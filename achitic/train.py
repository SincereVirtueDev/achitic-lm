import os,random,argparse,json,time,sys,hashlib,resource,math,warnings
from contextlib import nullcontext
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader,DistributedSampler
from .model import AchiticLM,Config
from .data import TokenDataset,token_packing_report
from .checkpoint import load_checkpoint_dict

CHECKPOINT_FORMAT_VERSION=1
RESUME_SEMANTICS='model_optimizer_rng_restored_data_order_not_exact'
EXACT_DATA_ORDER_RESUME=False
MISSING_EXACT_RESUME_STATE=(
    'data_cursor',
    'dataloader_iterator_position',
    'random_sampler_order',
    'distributed_sampler_epoch_batch_offset',
    'worker_rng_state',
)

def resume_contract():
    return {'checkpoint_format':CHECKPOINT_FORMAT_VERSION,'resume_semantics':RESUME_SEMANTICS,
      'exact_data_order_resume':EXACT_DATA_ORDER_RESUME,
      'missing_exact_resume_state':MISSING_EXACT_RESUME_STATE}

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def max_rss_bytes():
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(rss*1024)

def dtype_name(model):
    return str(next(model.parameters()).dtype).replace('torch.','')

def write_json(path,payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    os.replace(temp,path)

def append_jsonl(path,payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with open(path,'a',encoding='utf8') as f:f.write(json.dumps(payload,ensure_ascii=False)+'\n')

def build_manifest(args,cfg,device,world,start_step,model_dtype):
    tokenizer_path=getattr(args,'tokenizer',None)
    val_path=getattr(args,'val_data',None)
    return {'schema_version':'0.1','status':'running','started_at':utc_now(),
      'completed_at':None,'command':' '.join(sys.argv),'config_path':args.config,
      'config_sha256':sha256_file(args.config),'data_path':args.data,
      'data_sha256':sha256_file(args.data),'val_data_path':val_path,
      'val_data_sha256':sha256_file(val_path) if val_path else None,'tokenizer_path':tokenizer_path,
      'tokenizer_sha256':sha256_file(tokenizer_path) if tokenizer_path else None,
      'out':args.out,'resume':args.resume,'metrics_path':args.metrics,
      'weights_only_resume':bool(getattr(args,'weights_only_resume',False)),
      'checkpoint_format':CHECKPOINT_FORMAT_VERSION,'resume_semantics':RESUME_SEMANTICS,
      'device':str(device),'dtype':model_dtype,'compute_dtype':args.compute_dtype,
      'requested_dtype':args.dtype,'world_size':world,'start_step':start_step,
      'target_steps':args.steps,'final_step':start_step,'batch':args.batch,'accum':args.accum,
      'stride':args.stride,
      'lr':args.lr,'schedule':args.schedule,'warmup_steps':args.warmup_steps,
      'min_lr_ratio':args.min_lr_ratio,'weight_decay':args.weight_decay,
      'save_every':args.save_every,'eval_every':args.eval_every,'eval_iters':args.eval_iters,
      'best_checkpoint_path':str(best_checkpoint_path(args.out)) if val_path else None,
      'best_val_loss':None,'config':vars(cfg)}

def learning_rate_for_step(base_lr,step,total_steps,warmup_steps=0,min_lr_ratio=1.0,schedule='constant'):
    if total_steps<1:raise ValueError('total_steps must be >= 1')
    if step<0:raise ValueError('step must be >= 0')
    if warmup_steps<0:raise ValueError('warmup_steps must be >= 0')
    if not 0<=min_lr_ratio<=1:raise ValueError('min_lr_ratio must be between 0 and 1')
    if schedule not in {'constant','cosine'}:raise ValueError('schedule must be constant or cosine')
    step=min(step,total_steps)
    if warmup_steps>0 and step<=warmup_steps:
        return base_lr*step/warmup_steps
    if schedule=='constant':return base_lr
    decay_steps=max(1,total_steps-warmup_steps)
    progress=min(max((step-warmup_steps)/decay_steps,0.0),1.0)
    cosine=0.5*(1.0+math.cos(math.pi*progress))
    return base_lr*(min_lr_ratio+(1.0-min_lr_ratio)*cosine)

def build_optimizer(model,lr,weight_decay):
    decay=[];no_decay=[];seen=set()
    for name,param in model.named_parameters():
        if not param.requires_grad or id(param) in seen:continue
        seen.add(id(param))
        if param.ndim<2 or name=='embed.weight':no_decay.append(param)
        else:decay.append(param)
    groups=[]
    if decay:groups.append({'params':decay,'weight_decay':float(weight_decay)})
    if no_decay:groups.append({'params':no_decay,'weight_decay':0.0})
    return torch.optim.AdamW(groups,lr=lr)

def load_optimizer_state(opt,state,model):
    error=None
    try:
        opt.load_state_dict(state);return 'exact'
    except ValueError as exc:
        error=exc
    old_groups=state.get('param_groups',[])
    if len(old_groups)!=1:raise error
    old_order=[param for param in model.parameters() if param.requires_grad]
    current=opt.state_dict()
    current_indices=[idx for group in current['param_groups'] for idx in group['params']]
    current_order=[param for group in opt.param_groups for param in group['params']]
    if len(old_order)!=len(current_order):raise error
    old_index_by_id={id(param):idx for idx,param in enumerate(old_order)}
    if set(old_index_by_id)!={id(param) for param in current_order}:raise error
    migrated={'state':{},'param_groups':current['param_groups']}
    old_state=state.get('state',{})
    for current_idx,param in zip(current_indices,current_order):
        old_idx=old_index_by_id[id(param)]
        if old_idx in old_state:migrated['state'][current_idx]=old_state[old_idx]
    opt.load_state_dict(migrated)
    return 'migrated_single_param_group'

def set_optimizer_lr(opt,lr):
    for group in opt.param_groups:group['lr']=lr

def best_checkpoint_path(path):
    return Path(str(path)+'.best.pt')

def supports_bf16(device):
    if device.type=='cpu':return True
    if device.type=='cuda':return torch.cuda.is_bf16_supported()
    return False

def autocast_context(device,compute_dtype):
    if compute_dtype=='bf16':
        return torch.autocast(device_type=device.type,dtype=torch.bfloat16)
    return nullcontext()

def perplexity(loss):
    return float(math.exp(min(float(loss),100.0)))

def evaluate_loss(model,loader,device,compute_dtype,max_iters):
    was_training=model.training
    model.eval();losses=[]
    with torch.no_grad():
        for idx,(x,y) in enumerate(loader):
            if max_iters is not None and idx>=max_iters:break
            x,y=x.to(device),y.to(device)
            with autocast_context(device,compute_dtype):
                _,loss=model(x,y)
            losses.append(float(loss.item()))
    if was_training:model.train()
    if not losses:raise ValueError('validation loader produced no batches')
    return sum(losses)/len(losses)

def train_data_startup_report(path,context,stride,batch,accum,steps):
    report=token_packing_report(path,context,stride=stride)
    tokens_per_step=batch*accum*context
    train_token_budget=steps*tokens_per_step
    report['tokens_per_step']=int(tokens_per_step)
    report['train_token_budget']=int(train_token_budget)
    report['batch_accum_windows']=int(batch*accum)
    return report

def warn_train_data_if_needed(report):
    if report['windows']<report['batch_accum_windows']:
        warnings.warn(
            f"dataset windows {report['windows']} < batch*accum {report['batch_accum_windows']}; "
            'the same tiny corpus can repeat within an optimizer step',
            RuntimeWarning,
            stacklevel=2,
        )
    if report['train_token_budget']>report['used_target_tokens']:
        warnings.warn(
            f"train token budget {report['train_token_budget']} exceeds unique target tokens "
            f"{report['used_target_tokens']}; data will repeat during training",
            RuntimeWarning,
            stacklevel=2,
        )

def setup():
    rank=int(os.getenv('RANK','0'));world=int(os.getenv('WORLD_SIZE','1'))
    if world>1:dist.init_process_group('nccl' if torch.cuda.is_available() else 'gloo')
    local=int(os.getenv('LOCAL_RANK','0'))
    device=torch.device(f'cuda:{local}' if torch.cuda.is_available() else 'cpu')
    if device.type=='cuda':torch.cuda.set_device(device)
    return rank,world,device

def save(path,model,opt,step,cfg,best_val_loss=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp')
    payload={'checkpoint_format':CHECKPOINT_FORMAT_VERSION,'resume_semantics':RESUME_SEMANTICS,
      'model':model.state_dict(),'optimizer':opt.state_dict(),'step':step,'config':vars(cfg),
      'rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
      'numpy_rng':np.random.get_state(),'python_rng':random.getstate()}
    if best_val_loss is not None:payload['best_val_loss']=float(best_val_loss)
    torch.save(payload,temp)
    os.replace(temp,path)

def load_checkpoint(path,model,opt=None,map_location='cpu',restore_rng=True,trust_checkpoint=False,
  weights_only_resume=False):
    ck=load_checkpoint_dict(path,map_location=map_location,trust_checkpoint=trust_checkpoint)
    cfg=Config(**ck['config'])
    if hasattr(model,'config') and vars(model.config)!=vars(cfg):
        raise ValueError('checkpoint config does not match model config')
    model.load_state_dict(ck['model'])
    if opt is not None:
        if 'optimizer' in ck:load_optimizer_state(opt,ck['optimizer'],model)
        elif weights_only_resume:
            warnings.warn(
                'resume checkpoint has no optimizer state; restarting optimizer because --weights-only-resume was set',
                RuntimeWarning,
                stacklevel=2,
            )
        else:
            raise ValueError('checkpoint has no optimizer state; pass --weights-only-resume to restart optimizer')
    if restore_rng:
        rng_keys={'rng','numpy_rng','python_rng'}
        if rng_keys<=set(ck):
            torch.set_rng_state(ck['rng']);np.random.set_state(ck['numpy_rng']);random.setstate(ck['python_rng'])
            if torch.cuda.is_available() and ck.get('cuda_rng') is not None:torch.cuda.set_rng_state_all(ck['cuda_rng'])
        elif weights_only_resume:
            warnings.warn(
                'resume checkpoint has no RNG state; continuing with current RNG because --weights-only-resume was set',
                RuntimeWarning,
                stacklevel=2,
            )
        else:
            raise ValueError('checkpoint has no RNG state; pass --weights-only-resume to continue without restoring RNG')
    if 'step' not in ck:
        if weights_only_resume:
            step=0
        else:
            raise ValueError('checkpoint has no step; pass --weights-only-resume to restart from step 0')
    else:
        step=ck['step']
    return step,cfg,ck

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',required=True);p.add_argument('--data',required=True)
    p.add_argument('--out',default='runs/model.pt');p.add_argument('--resume')
    p.add_argument('--steps',type=int,default=100);p.add_argument('--batch',type=int,default=2)
    p.add_argument('--accum',type=int,default=4);p.add_argument('--lr',type=float,default=3e-4)
    p.add_argument('--stride',type=int)
    p.add_argument('--warmup-steps',type=int,default=0)
    p.add_argument('--min-lr-ratio',type=float,default=1.0)
    p.add_argument('--schedule',choices=['constant','cosine'],default='constant')
    p.add_argument('--weight-decay',type=float,default=0.1)
    p.add_argument('--save-every',type=int,default=100)
    p.add_argument('--val-data');p.add_argument('--eval-every',type=int,default=0)
    p.add_argument('--eval-iters',type=int,default=10)
    p.add_argument('--dtype',choices=['fp32','bf16'],default='fp32')
    p.add_argument('--metrics');p.add_argument('--run-manifest');p.add_argument('--tokenizer')
    p.add_argument('--trust-checkpoint',action='store_true')
    p.add_argument('--weights-only-resume',action='store_true')
    a=p.parse_args();rank,world,device=setup()
    if a.weights_only_resume and not a.resume:p.error('--weights-only-resume requires --resume')
    if a.steps<1:p.error('--steps must be >= 1')
    if a.batch<1:p.error('--batch must be >= 1')
    if a.accum<1:p.error('--accum must be >= 1')
    if a.stride is not None and a.stride<1:p.error('--stride must be >= 1')
    if a.save_every<1:p.error('--save-every must be >= 1')
    if a.warmup_steps<0:p.error('--warmup-steps must be >= 0')
    if a.warmup_steps>a.steps:p.error('--warmup-steps must be <= --steps')
    if not 0<=a.min_lr_ratio<=1:p.error('--min-lr-ratio must be between 0 and 1')
    if a.weight_decay<0:p.error('--weight-decay must be >= 0')
    if a.eval_every<0:p.error('--eval-every must be >= 0')
    if a.eval_iters<1:p.error('--eval-iters must be >= 1')
    a.compute_dtype='bf16' if a.dtype=='bf16' and supports_bf16(device) else 'fp32'
    if rank==0 and a.dtype=='bf16' and a.compute_dtype!='bf16':
        print('warning: bf16 autocast is not supported on this device; using fp32',flush=True)
    torch.manual_seed(42+rank)
    cfg=Config(**json.loads(Path(a.config).read_text()))
    if a.stride is None:a.stride=cfg.context
    model=AchiticLM(cfg).to(device)
    if device.type=='cuda':torch.cuda.reset_peak_memory_stats(device)
    opt=build_optimizer(model,a.lr,a.weight_decay)
    start=0;best_val_loss=None
    if a.resume:
        start,_,ck=load_checkpoint(a.resume,model,opt,trust_checkpoint=a.trust_checkpoint,
          weights_only_resume=a.weights_only_resume)
        best_val_loss=ck.get('best_val_loss')
    if rank==0 and a.metrics:
        Path(a.metrics).parent.mkdir(parents=True,exist_ok=True);Path(a.metrics).write_text('',encoding='utf8')
    manifest=build_manifest(a,cfg,device,world,start,dtype_name(model)) if rank==0 and a.run_manifest else None
    if manifest:manifest['best_val_loss']=best_val_loss
    if manifest:write_json(a.run_manifest,manifest)
    raw=model
    if world>1:model=DDP(model,device_ids=[device.index] if device.type=='cuda' else None)
    model.train()
    ds=TokenDataset(a.data,cfg.context,stride=a.stride)
    train_report=train_data_startup_report(a.data,cfg.context,a.stride,a.batch,a.accum,a.steps)
    if rank==0:
        print(
            f"train windows={train_report['windows']} tokens={train_report['total_tokens']} "
            f"tokens/step={train_report['tokens_per_step']} stride={train_report['stride']}",
            flush=True,
        )
        warn_train_data_if_needed(train_report)
    if manifest:
        manifest['train_data']=train_report
        write_json(a.run_manifest,manifest)
    sampler=DistributedSampler(ds,num_replicas=world,rank=rank,shuffle=True) if world>1 else None
    loader=DataLoader(ds,batch_size=a.batch,sampler=sampler,shuffle=sampler is None,drop_last=False)
    val_loader=DataLoader(TokenDataset(a.val_data,cfg.context,stride=a.stride),batch_size=a.batch,shuffle=False,drop_last=False) if a.val_data and rank==0 else None
    it=iter(loader);epoch=0
    tokens_seen=0
    train_started=time.perf_counter()
    for step in range(start,a.steps):
        step_lr=learning_rate_for_step(a.lr,step+1,a.steps,a.warmup_steps,a.min_lr_ratio,a.schedule)
        set_optimizer_lr(opt,step_lr)
        step_started=time.perf_counter();tokens_this_step=0
        opt.zero_grad(set_to_none=True)
        for micro in range(a.accum):
            try:x,y=next(it)
            except StopIteration:
                epoch+=1
                if sampler:sampler.set_epoch(epoch)
                it=iter(loader);x,y=next(it)
            x,y=x.to(device),y.to(device)
            tokens_this_step+=int(y.numel())
            sync=model.no_sync() if world>1 and micro<a.accum-1 else None
            with sync if sync is not None else nullcontext():
                with autocast_context(device,a.compute_dtype):
                    _,loss=model(x,y)
                (loss/a.accum).backward()
        grad_norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step()
        tokens_seen+=tokens_this_step
        elapsed=time.perf_counter()-step_started
        total_elapsed=time.perf_counter()-train_started
        tok_per_sec=tokens_this_step/max(elapsed,1e-9)
        val_loss=None;val_ppl=None
        if rank==0 and val_loader is not None and ((a.eval_every>0 and (step+1)%a.eval_every==0) or step+1==a.steps):
            val_loss=evaluate_loss(raw,val_loader,device,a.compute_dtype,a.eval_iters)
            val_ppl=perplexity(val_loss)
            print(f'step={step+1} val_loss={val_loss:.4f} val_ppl={val_ppl:.4f}',flush=True)
            if best_val_loss is None or val_loss<best_val_loss:
                best_val_loss=val_loss
                save(best_checkpoint_path(a.out),raw,opt,step+1,cfg,best_val_loss=best_val_loss)
        if rank==0 and ((step+1)%10==0 or step==start):
            print(f'step={step+1} loss={loss.item():.4f} lr={step_lr:.6g} tok/s={tok_per_sec:.2f}',flush=True)
        if rank==0 and a.metrics:
            append_jsonl(a.metrics,{'step':step+1,'train_loss':float(loss.item()),
              'lr':float(opt.param_groups[0]['lr']),'tokens_this_step':tokens_this_step,
              'tokens_seen':tokens_seen,'tokens_per_second':tok_per_sec,
              'elapsed_seconds':total_elapsed,'grad_norm':float(grad_norm.item()),
              'epoch':epoch,'batch':a.batch,'accum':a.accum,'device':str(device),
              'dtype':dtype_name(raw),'compute_dtype':a.compute_dtype,
              'val_loss':val_loss,'val_ppl':val_ppl,'best_val_loss':best_val_loss,
              'peak_cuda_memory_bytes':torch.cuda.max_memory_allocated(device) if device.type=='cuda' else None,
              'max_rss_bytes':max_rss_bytes()})
        if rank==0 and ((step+1)%a.save_every==0 or step+1==a.steps):save(a.out,raw,opt,step+1,cfg,best_val_loss=best_val_loss)
        if manifest:
            manifest.update({'final_step':step+1,'tokens_seen':tokens_seen,
              'last_train_loss':float(loss.item()),'last_lr':float(opt.param_groups[0]['lr']),
              'last_val_loss':val_loss,'last_val_ppl':val_ppl,'best_val_loss':best_val_loss,
              'last_grad_norm':float(grad_norm.item()),'peak_cuda_memory_bytes':torch.cuda.max_memory_allocated(device) if device.type=='cuda' else None,
              'max_rss_bytes':max_rss_bytes()})
            write_json(a.run_manifest,manifest)
    if manifest:
        manifest.update({'status':'completed','completed_at':utc_now(),
          'total_seconds':time.perf_counter()-train_started})
        write_json(a.run_manifest,manifest)
    if world>1:dist.destroy_process_group()
if __name__=='__main__':main()
