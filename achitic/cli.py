import argparse,json,time
from pathlib import Path
import torch
from .model import AchiticLM,Config
from .tokenizer import Tokenizer,train
from .data import prepare,encode_corpus

def ensure_tokenizer_matches_config(tok,cfg):
    if tok.vocab_size!=cfg.vocab_size:
        raise ValueError(f'tokenizer vocab size {tok.vocab_size} does not match checkpoint config vocab_size {cfg.vocab_size}')

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('prepare');a.add_argument('--inputs',nargs='+',required=True);a.add_argument('--out',required=True)
    a=sub.add_parser('tokenizer');a.add_argument('--input',required=True);a.add_argument('--prefix',required=True);a.add_argument('--vocab',type=int,default=8000)
    a=sub.add_parser('encode');a.add_argument('--input',required=True);a.add_argument('--tokenizer',required=True);a.add_argument('--out',required=True)
    for name in ['chat','benchmark']:
        a=sub.add_parser(name);a.add_argument('--checkpoint',required=True);a.add_argument('--tokenizer',required=True)
        a.add_argument('--prompt',default='Xin chào');a.add_argument('--tokens',type=int,default=32)
    args=p.parse_args()
    if args.cmd=='prepare':print('documents:',prepare(args.inputs,args.out));return
    if args.cmd=='tokenizer':train(args.input,args.prefix,args.vocab);return
    if args.cmd=='encode':print('tokens:',encode_corpus(Tokenizer(args.tokenizer),args.input,args.out));return
    ck=torch.load(args.checkpoint,map_location='cpu',weights_only=False);c=Config(**ck['config'])
    tok=Tokenizer(args.tokenizer)
    ensure_tokenizer_matches_config(tok,c)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    model=AchiticLM(c).to(device);model.load_state_dict(ck['model']);model.eval()
    ids=torch.tensor([tok.encode(args.prompt,add_bos=True)],device=device)
    if device=='cuda':torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize()
    t=time.perf_counter()
    output=model.generate(ids,args.tokens,eos_id=tok.eos_id)
    if device=='cuda':torch.cuda.synchronize()
    dt=time.perf_counter()-t;generated=output.shape[1]-ids.shape[1]
    print(tok.decode(output[0].tolist()))
    if args.cmd=='benchmark':
        print(json.dumps({'generated_tokens':generated,'seconds':dt,'tokens_per_second':generated/max(dt,1e-9),
          'peak_cuda_memory_bytes':torch.cuda.max_memory_allocated() if device=='cuda' else None},indent=2))
if __name__=='__main__':main()
