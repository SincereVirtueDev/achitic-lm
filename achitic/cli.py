import argparse,json,time
from pathlib import Path
import torch
from dataclasses import asdict
from .model import AchiticLM,Config
from .tokenizer import DEFAULT_INPUT_SENTENCE_SIZE,DEFAULT_MAX_RESERVED_RATIO,Tokenizer,train
from .data import prepare,encode_corpus
from .eval import evaluate_checkpoint,sample_checkpoint,write_json,write_jsonl
from .checkpoint import load_weights

def ensure_tokenizer_matches_config(tok,cfg):
    if tok.vocab_size!=cfg.vocab_size:
        raise ValueError(f'tokenizer vocab size {tok.vocab_size} does not match checkpoint config vocab_size {cfg.vocab_size}')

def resolve_chat_template(ck,requested=None):
    if requested in {'none','achitic'}:return requested
    return 'achitic' if ck.get('stage') in {'sft','dpo'} else 'none'

def chat_prompt_ids(tok,prompt,template):
    if template=='achitic':
        return tok.encode(f'<|user|>{prompt}<|assistant|>',add_bos=True)
    return tok.encode(prompt,add_bos=True)

def piece_id(tok,piece):
    idx=tok.sp.piece_to_id(piece)
    if idx<0 or (hasattr(tok,'unk_id') and idx==tok.unk_id and piece!='<unk>'):
        raise ValueError(f'tokenizer does not contain {piece}')
    return int(idx)

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('prepare');a.add_argument('--inputs',nargs='+',required=True);a.add_argument('--out',required=True)
    a.add_argument('--format',dest='input_format',choices=['auto','text','jsonl'],default='auto')
    a.add_argument('--min-chars',type=int,default=30)
    a=sub.add_parser('tokenizer');a.add_argument('--input',required=True);a.add_argument('--prefix',required=True);a.add_argument('--vocab',type=int,default=8000)
    a.add_argument('--max-reserved-ratio',type=float,default=DEFAULT_MAX_RESERVED_RATIO)
    a.add_argument('--allow-reserved-padding',action='store_true')
    a.add_argument('--input-sentence-size',type=int,default=DEFAULT_INPUT_SENTENCE_SIZE)
    a.add_argument('--num-threads',type=int)
    a.add_argument('--no-shuffle-input-sentence',dest='shuffle_input_sentence',action='store_false',default=True)
    a=sub.add_parser('encode');a.add_argument('--input',required=True);a.add_argument('--tokenizer',required=True);a.add_argument('--out',required=True)
    a.add_argument('--chunk-tokens',type=int,default=1_000_000)
    a=sub.add_parser('eval');a.add_argument('--checkpoint',required=True);a.add_argument('--tokenizer',required=True);a.add_argument('--data',required=True)
    a.add_argument('--batch',type=int,default=1);a.add_argument('--max-batches',type=int);a.add_argument('--device',default='cpu');a.add_argument('--out');a.add_argument('--trust-checkpoint',action='store_true')
    a=sub.add_parser('sample-report');a.add_argument('--checkpoint',required=True);a.add_argument('--tokenizer',required=True);a.add_argument('--prompts',required=True)
    a.add_argument('--tokens',type=int,default=32);a.add_argument('--min-generated-tokens',type=int,default=4)
    a.add_argument('--max-repeat-ratio',type=float,default=0.5)
    a.add_argument('--chat-template',choices=['auto','none','achitic'],default='auto')
    a.add_argument('--device',default='cpu');a.add_argument('--out');a.add_argument('--trust-checkpoint',action='store_true')
    for name in ['chat','benchmark']:
        a=sub.add_parser(name);a.add_argument('--checkpoint',required=True);a.add_argument('--tokenizer',required=True)
        a.add_argument('--prompt',default='Xin chào');a.add_argument('--tokens',type=int,default=32);a.add_argument('--trust-checkpoint',action='store_true')
        a.add_argument('--chat-template',choices=['none','achitic'])
    args=p.parse_args()
    if args.cmd=='prepare':
        stats=prepare(args.inputs,args.out,min_chars=args.min_chars,input_format=args.input_format,return_stats=True)
        print('documents:',stats['documents'])
        print('prepare_stats:',json.dumps(stats,ensure_ascii=False,sort_keys=True))
        return
    if args.cmd=='tokenizer':
        stats=train(args.input,args.prefix,args.vocab,max_reserved_ratio=args.max_reserved_ratio,
          allow_reserved_padding=args.allow_reserved_padding,input_sentence_size=args.input_sentence_size,
          shuffle_input_sentence=args.shuffle_input_sentence,num_threads=args.num_threads)
        print(json.dumps(stats,ensure_ascii=False,sort_keys=True))
        return
    if args.cmd=='encode':
        stats=encode_corpus(Tokenizer(args.tokenizer),args.input,args.out,
          chunk_tokens=args.chunk_tokens,return_stats=True)
        print('tokens:',stats['tokens'])
        print('encode_stats:',json.dumps(stats,ensure_ascii=False,sort_keys=True))
        return
    if args.cmd=='eval':
        result=asdict(evaluate_checkpoint(args.checkpoint,args.tokenizer,args.data,batch=args.batch,
          max_batches=args.max_batches,device=args.device,trust_checkpoint=args.trust_checkpoint))
        if args.out:write_json(args.out,result)
        print(json.dumps(result,ensure_ascii=False,indent=2));return
    if args.cmd=='sample-report':
        rows=[asdict(row) for row in sample_checkpoint(args.checkpoint,args.tokenizer,args.prompts,
          max_new_tokens=args.tokens,device=args.device,trust_checkpoint=args.trust_checkpoint,
          min_generated_tokens=args.min_generated_tokens,max_repeat_ratio=args.max_repeat_ratio,
          chat_template=args.chat_template)]
        if args.out:write_jsonl(args.out,rows)
        for row in rows:print(json.dumps(row,ensure_ascii=False))
        return
    ck=load_weights(args.checkpoint,map_location='cpu',trust_checkpoint=args.trust_checkpoint);c=Config(**ck['config'])
    tok=Tokenizer(args.tokenizer)
    ensure_tokenizer_matches_config(tok,c)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    model=AchiticLM(c).to(device);model.load_state_dict(ck['model']);model.eval()
    template=resolve_chat_template(ck,args.chat_template)
    prompt_ids=chat_prompt_ids(tok,args.prompt,template)
    ids=torch.tensor([prompt_ids],device=device)
    stop_ids=[tok.eos_id]
    if template=='achitic':stop_ids.append(piece_id(tok,'<|user|>'))
    if device=='cuda':torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize()
    t=time.perf_counter()
    output=model.generate(ids,args.tokens,eos_id=tok.eos_id,stop_ids=stop_ids)
    if device=='cuda':torch.cuda.synchronize()
    dt=time.perf_counter()-t;generated=output.shape[1]-ids.shape[1]
    print(tok.decode(output[0].tolist()))
    if args.cmd=='benchmark':
        print(json.dumps({'generated_tokens':generated,'seconds':dt,'tokens_per_second':generated/max(dt,1e-9),
          'peak_cuda_memory_bytes':torch.cuda.max_memory_allocated() if device=='cuda' else None},indent=2))
if __name__=='__main__':main()
