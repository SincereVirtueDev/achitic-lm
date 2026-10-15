import argparse
import json
import math
import re
import time
from dataclasses import asdict,dataclass
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from .data import TokenDataset
from .model import AchiticLM,Config
from .tokenizer import Tokenizer
from .checkpoint import load_weights


@dataclass
class EvalResult:
    loss: float
    perplexity: float
    batches: int
    tokens: int
    seconds: float
    tokens_per_second: float
    device: str
    checkpoint_step: int | None = None


@dataclass
class SampleResult:
    id: str
    language: str
    prompt: str
    chat_template: str
    output: str
    generated_text: str
    generated_tokens: int
    checks: dict


def ensure_tokenizer_matches_config(tok,cfg):
    if tok.vocab_size!=cfg.vocab_size:
        raise ValueError(f'tokenizer vocab size {tok.vocab_size} does not match checkpoint config vocab_size {cfg.vocab_size}')


def _device(name=None):
    if name:
        return torch.device(name)
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def _safe_ppl(loss):
    return math.exp(min(float(loss),50.0))


def evaluate_model(model,data,context,batch=1,max_batches=None,device=None):
    device=_device(device)
    model=model.to(device)
    was_training=model.training
    model.eval()
    ds=TokenDataset(data,context)
    loader=DataLoader(ds,batch_size=batch,shuffle=False,drop_last=False)
    total_loss=0.0;total_tokens=0;batches=0
    start=time.perf_counter()
    try:
        with torch.no_grad():
            for i,(x,y) in enumerate(loader):
                if max_batches is not None and i>=max_batches:break
                x,y=x.to(device),y.to(device)
                _,loss=model(x,y)
                n=y.numel()
                total_loss+=float(loss.item())*n
                total_tokens+=n;batches+=1
    finally:
        if was_training:model.train()
    seconds=time.perf_counter()-start
    if total_tokens==0:
        raise ValueError('no eval tokens processed')
    loss=total_loss/total_tokens
    return EvalResult(loss=loss,perplexity=_safe_ppl(loss),batches=batches,tokens=total_tokens,
      seconds=seconds,tokens_per_second=total_tokens/max(seconds,1e-9),device=str(device))


def load_checkpoint_model(checkpoint,tokenizer,device=None,trust_checkpoint=False):
    device=_device(device)
    ck=load_weights(checkpoint,map_location=device,trust_checkpoint=trust_checkpoint)
    cfg=Config(**ck['config'])
    tok=Tokenizer(tokenizer)
    ensure_tokenizer_matches_config(tok,cfg)
    model=AchiticLM(cfg).to(device)
    model.load_state_dict(ck['model'])
    return model,tok,cfg,ck


def evaluate_checkpoint(checkpoint,tokenizer,data,batch=1,max_batches=None,device=None,trust_checkpoint=False):
    model,_,cfg,ck=load_checkpoint_model(checkpoint,tokenizer,device=device,trust_checkpoint=trust_checkpoint)
    result=evaluate_model(model,data,cfg.context,batch=batch,max_batches=max_batches,device=device)
    result.checkpoint_step=ck.get('step')
    return result


def load_fixed_prompts(path):
    prompts=[]
    with open(path,encoding='utf8') as f:
        for line_no,line in enumerate(f,1):
            line=line.strip()
            if not line or line.startswith('#'):continue
            obj=json.loads(line)
            if 'id' not in obj or 'prompt' not in obj:
                raise ValueError(f'prompt line {line_no} must include id and prompt')
            prompts.append({'id':obj['id'],'language':obj.get('language','und'),'prompt':obj['prompt']})
    if not prompts:
        raise ValueError('no fixed prompts found')
    return prompts


def generated_sample_checks(text,token_ids,min_tokens=4,max_tokens=32,max_repeat_ratio=0.5):
    reserved=bool(re.search(r'<\|reserved_[^|]+\|>',text))
    sentence_boundary=bool(re.search(r'[.!?…](?:["”’\')\]]*)',text))
    length_ok=min_tokens<=len(token_ids)<=max_tokens
    if len(token_ids)<3:
        repeat_ratio=0.0
    else:
        trigrams=[tuple(token_ids[index:index+3]) for index in range(len(token_ids)-2)]
        repeat_ratio=1.0-len(set(trigrams))/len(trigrams)
    checks={
        'contains_reserved_token':reserved,
        'has_sentence_boundary':sentence_boundary,
        'length_ok':length_ok,
        'repeat_ratio':repeat_ratio,
        'repeat_ok':repeat_ratio<=max_repeat_ratio,
    }
    checks['automatic_pass']=not reserved and sentence_boundary and length_ok and checks['repeat_ok']
    return checks


def sample_prompt_ids(tok,prompt,chat_template):
    if chat_template=='achitic':
        return tok.encode(f'<|user|>{prompt}<|assistant|>',add_bos=True)
    if chat_template=='none':return tok.encode(prompt,add_bos=True)
    raise ValueError('chat_template must be none or achitic')


def sample_model(model,tok,prompts,max_new_tokens=32,device=None,min_generated_tokens=4,max_repeat_ratio=0.5,
  chat_template='none'):
    device=_device(device)
    model=model.to(device)
    was_training=model.training
    model.eval()
    rows=[]
    try:
        with torch.no_grad():
            for prompt in prompts:
                prompt_ids=sample_prompt_ids(tok,prompt['prompt'],chat_template)
                ids=torch.tensor([prompt_ids],device=device)
                out=model.generate(ids,max_new_tokens,temperature=0,eos_id=tok.eos_id)
                generated_ids=out[0,len(prompt_ids):].tolist()
                generated_text=tok.decode(generated_ids)
                rows.append(SampleResult(id=prompt['id'],language=prompt.get('language','und'),
                  prompt=prompt['prompt'],chat_template=chat_template,
                  output=tok.decode(out[0].tolist()),generated_text=generated_text,
                  generated_tokens=len(generated_ids),checks=generated_sample_checks(generated_text,generated_ids,
                    min_tokens=min_generated_tokens,max_tokens=max_new_tokens,max_repeat_ratio=max_repeat_ratio)))
    finally:
        if was_training:model.train()
    return rows


def sample_checkpoint(checkpoint,tokenizer,prompts_path,max_new_tokens=32,device=None,trust_checkpoint=False,
  min_generated_tokens=4,max_repeat_ratio=0.5,chat_template='auto'):
    model,tok,_,ck=load_checkpoint_model(checkpoint,tokenizer,device=device,trust_checkpoint=trust_checkpoint)
    if chat_template=='auto':chat_template='achitic' if ck.get('stage') in {'sft','dpo'} else 'none'
    return sample_model(model,tok,load_fixed_prompts(prompts_path),max_new_tokens=max_new_tokens,device=device,
      min_generated_tokens=min_generated_tokens,max_repeat_ratio=max_repeat_ratio,chat_template=chat_template)


def write_json(path,payload):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def write_jsonl(path,rows):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,'w',encoding='utf8') as f:
        for row in rows:
            f.write(json.dumps(row,ensure_ascii=False)+'\n')


def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('loss')
    a.add_argument('--checkpoint',required=True);a.add_argument('--tokenizer',required=True);a.add_argument('--data',required=True)
    a.add_argument('--batch',type=int,default=1);a.add_argument('--max-batches',type=int);a.add_argument('--device',default='cpu');a.add_argument('--out');a.add_argument('--trust-checkpoint',action='store_true')
    a=sub.add_parser('samples')
    a.add_argument('--checkpoint',required=True);a.add_argument('--tokenizer',required=True);a.add_argument('--prompts',required=True)
    a.add_argument('--tokens',type=int,default=32);a.add_argument('--min-generated-tokens',type=int,default=4)
    a.add_argument('--max-repeat-ratio',type=float,default=0.5)
    a.add_argument('--chat-template',choices=['auto','none','achitic'],default='auto')
    a.add_argument('--device',default='cpu');a.add_argument('--out');a.add_argument('--trust-checkpoint',action='store_true')
    args=p.parse_args()
    if args.cmd=='loss':
        result=asdict(evaluate_checkpoint(args.checkpoint,args.tokenizer,args.data,batch=args.batch,
          max_batches=args.max_batches,device=args.device,trust_checkpoint=args.trust_checkpoint))
        text=json.dumps(result,ensure_ascii=False,indent=2)
        if args.out:write_json(args.out,result)
        print(text);return
    rows=[asdict(row) for row in sample_checkpoint(args.checkpoint,args.tokenizer,args.prompts,
      max_new_tokens=args.tokens,device=args.device,trust_checkpoint=args.trust_checkpoint,
      min_generated_tokens=args.min_generated_tokens,max_repeat_ratio=args.max_repeat_ratio,
      chat_template=args.chat_template)]
    if args.out:write_jsonl(args.out,rows)
    for row in rows:print(json.dumps(row,ensure_ascii=False))


if __name__=='__main__':main()
