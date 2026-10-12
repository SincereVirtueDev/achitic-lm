import os,random,argparse,json
from pathlib import Path
import numpy as np
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader,DistributedSampler
from .model import AchiticLM,Config
from .data import TokenDataset

CHECKPOINT_FORMAT_VERSION=1
RESUME_SEMANTICS='model_optimizer_rng_restored_data_order_not_exact'

def setup():
    rank=int(os.getenv('RANK','0'));world=int(os.getenv('WORLD_SIZE','1'))
    if world>1:dist.init_process_group('nccl' if torch.cuda.is_available() else 'gloo')
    local=int(os.getenv('LOCAL_RANK','0'))
    device=torch.device(f'cuda:{local}' if torch.cuda.is_available() else 'cpu')
    if device.type=='cuda':torch.cuda.set_device(device)
    return rank,world,device

def save(path,model,opt,step,cfg):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp')
    torch.save({'checkpoint_format':CHECKPOINT_FORMAT_VERSION,'resume_semantics':RESUME_SEMANTICS,
      'model':model.state_dict(),'optimizer':opt.state_dict(),'step':step,'config':vars(cfg),
      'rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
      'numpy_rng':np.random.get_state(),'python_rng':random.getstate()},temp)
    os.replace(temp,path)

def load_checkpoint(path,model,opt=None,map_location='cpu',restore_rng=True):
    ck=torch.load(path,map_location=map_location,weights_only=False)
    cfg=Config(**ck['config'])
    if hasattr(model,'config') and vars(model.config)!=vars(cfg):
        raise ValueError('checkpoint config does not match model config')
    model.load_state_dict(ck['model'])
    if opt is not None:opt.load_state_dict(ck['optimizer'])
    if restore_rng:
        torch.set_rng_state(ck['rng']);np.random.set_state(ck['numpy_rng']);random.setstate(ck['python_rng'])
        if torch.cuda.is_available() and ck.get('cuda_rng') is not None:torch.cuda.set_rng_state_all(ck['cuda_rng'])
    return ck['step'],cfg,ck

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',required=True);p.add_argument('--data',required=True)
    p.add_argument('--out',default='runs/model.pt');p.add_argument('--resume')
    p.add_argument('--steps',type=int,default=100);p.add_argument('--batch',type=int,default=2)
    p.add_argument('--accum',type=int,default=4);p.add_argument('--lr',type=float,default=3e-4)
    p.add_argument('--save-every',type=int,default=100)
    a=p.parse_args();rank,world,device=setup()
    torch.manual_seed(42+rank)
    cfg=Config(**json.loads(Path(a.config).read_text()))
    model=AchiticLM(cfg).to(device)
    opt=torch.optim.AdamW(model.parameters(),lr=a.lr,weight_decay=0.1)
    start=0
    if a.resume:
        start,_,_=load_checkpoint(a.resume,model,opt)
    raw=model
    if world>1:model=DDP(model,device_ids=[device.index] if device.type=='cuda' else None)
    ds=TokenDataset(a.data,cfg.context)
    sampler=DistributedSampler(ds,num_replicas=world,rank=rank,shuffle=True) if world>1 else None
    loader=DataLoader(ds,batch_size=a.batch,sampler=sampler,shuffle=sampler is None,drop_last=False)
    it=iter(loader);epoch=0
    for step in range(start,a.steps):
        opt.zero_grad(set_to_none=True)
        for micro in range(a.accum):
            try:x,y=next(it)
            except StopIteration:
                epoch+=1
                if sampler:sampler.set_epoch(epoch)
                it=iter(loader);x,y=next(it)
            x,y=x.to(device),y.to(device)
            sync=model.no_sync() if world>1 and micro<a.accum-1 else None
            from contextlib import nullcontext
            with sync if sync is not None else nullcontext():
                _,loss=model(x,y);(loss/a.accum).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step()
        if rank==0 and ((step+1)%10==0 or step==start):print(f'step={step+1} loss={loss.item():.4f}',flush=True)
        if rank==0 and ((step+1)%a.save_every==0 or step+1==a.steps):save(a.out,raw,opt,step+1,cfg)
    if world>1:dist.destroy_process_group()
if __name__=='__main__':main()
