#!/usr/bin/env python3
import argparse
import json

from achitic.checkpoint import save_safetensors_weights


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--dtype',choices=['fp16','fp32'],default='fp16')
    p.add_argument('--trust-checkpoint',action='store_true')
    args=p.parse_args()
    result=save_safetensors_weights(args.checkpoint,args.out,dtype=args.dtype,trust_checkpoint=args.trust_checkpoint)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
