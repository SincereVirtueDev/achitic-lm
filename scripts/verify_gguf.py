#!/usr/bin/env python3
"""Verify an Achitic GGUF with pinned llama.cpp.

This script intentionally requires a local llama.cpp checkout. It does not make a
GGUF artifact release-ready by itself; the command output must be recorded for
the exact artifact being published.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from achitic.model import AchiticLM,Config
from achitic.tokenizer import Tokenizer
from achitic.checkpoint import load_weights


HELPER_C=r'''
#include "llama.h"
#include <stdio.h>
#include <stdlib.h>
static void quiet(enum ggml_log_level level, const char * text, void * user_data) {
    (void) level; (void) text; (void) user_data;
}
int main(int argc, char ** argv) {
    if (argc < 4) {
        fprintf(stderr, "usage: dump_logits model.gguf out.bin ctx id0 id1 ...\n");
        return 2;
    }
    llama_log_set(quiet, NULL);
    llama_backend_init();
    struct llama_model_params mp = llama_model_default_params();
    struct llama_model * model = llama_model_load_from_file(argv[1], mp);
    if (!model) {
        fprintf(stderr, "load fail\n");
        return 1;
    }
    struct llama_context_params cp = llama_context_default_params();
    cp.n_ctx = atoi(argv[3]);
    cp.n_batch = cp.n_ctx;
    cp.n_threads = 1;
    struct llama_context * ctx = llama_init_from_model(model, cp);
    if (!ctx) {
        fprintf(stderr, "ctx fail\n");
        return 1;
    }
    int n = argc - 4;
    int nv = llama_vocab_n_tokens(llama_model_get_vocab(model));
    struct llama_batch batch = llama_batch_init(n, 0, 1);
    for (int i = 0; i < n; i++) {
        batch.token[i] = atoi(argv[i + 4]);
        batch.pos[i] = i;
        batch.n_seq_id[i] = 1;
        batch.seq_id[i][0] = 0;
        batch.logits[i] = 1;
    }
    batch.n_tokens = n;
    if (llama_decode(ctx, batch)) {
        fprintf(stderr, "decode fail\n");
        return 1;
    }
    FILE * f = fopen(argv[2], "wb");
    if (!f) {
        fprintf(stderr, "open output fail\n");
        return 1;
    }
    for (int i = 0; i < n; i++) {
        fwrite(llama_get_logits_ith(ctx, i), sizeof(float), nv, f);
    }
    fclose(f);
    printf("ok n=%d vocab=%d\n", n, nv);
    return 0;
}
'''


def run(cmd,cwd=None):
    return subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)


def llama_commit(llama_cpp_dir):
    try:
        return run(['git','-C',str(llama_cpp_dir),'rev-parse','HEAD']).stdout.strip()
    except Exception:
        return None


def library_dirs(llama_cpp_dir):
    roots=[
        llama_cpp_dir/'build'/'bin',
        llama_cpp_dir/'build'/'src',
        llama_cpp_dir/'build'/'ggml'/'src',
        llama_cpp_dir/'build'/'ggml'/'src'/'ggml-cpu',
        llama_cpp_dir/'build',
    ]
    return [path for path in roots if path.exists()]


def build_helper(llama_cpp_dir,workdir):
    source=workdir/'dump_logits.c'
    binary=workdir/'dump_logits'
    source.write_text(HELPER_C,encoding='utf8')
    include_flags=[
        '-I'+str(llama_cpp_dir/'include'),
        '-I'+str(llama_cpp_dir/'src'),
        '-I'+str(llama_cpp_dir/'ggml'/'include'),
    ]
    lib_dirs=library_dirs(llama_cpp_dir)
    if not lib_dirs:
        raise RuntimeError(f'no built llama.cpp library dirs found under {llama_cpp_dir}; run cmake build first')
    lib_flags=[]
    rpath_flags=[]
    for path in lib_dirs:
        lib_flags.append('-L'+str(path))
        rpath_flags.append('-Wl,-rpath,'+str(path))
    cmd=['c++','-O2','-std=c++17','-o',str(binary),str(source),*include_flags,*lib_flags,
      '-lllama','-lggml','-lggml-base','-pthread','-ldl','-lm',*rpath_flags]
    run(cmd)
    return binary


def export_stress_gguf(checkpoint,tokenizer,out,scale,trust_checkpoint=False):
    from export_gguf import export_checkpoint

    ck=load_weights(checkpoint,map_location='cpu',trust_checkpoint=trust_checkpoint)
    state={k:v.detach().clone() for k,v in ck['model'].items()}
    for name,tensor in state.items():
        if name.endswith(('attn.q.weight','attn.k.weight')):
            tensor.mul_(scale)
    stress=out.with_suffix('.pt')
    torch.save({'config':ck['config'],'model':state},stress)
    export_checkpoint(stress,tokenizer,out,trust_checkpoint=trust_checkpoint)
    return stress,out


def pytorch_logits(checkpoint,ids,stress_scale=1.0,trust_checkpoint=False):
    ck=load_weights(checkpoint,map_location='cpu',trust_checkpoint=trust_checkpoint)
    cfg=Config(**ck['config'])
    state={k:v.detach().clone() for k,v in ck['model'].items()}
    for name,tensor in state.items():
        if stress_scale!=1.0 and name.endswith(('attn.q.weight','attn.k.weight')):
            tensor.mul_(stress_scale)
        if tensor.ndim==2:
            state[name]=tensor.half().float()
    model=AchiticLM(cfg).eval()
    model.load_state_dict(state)
    with torch.no_grad():
        logits,_=model(torch.tensor([ids],dtype=torch.long))
    return logits[0].float().numpy()


def llama_logits(helper,gguf_path,ids,workdir,context):
    out=workdir/'llama_logits.bin'
    run([str(helper),str(gguf_path),str(out),str(context),*(str(i) for i in ids)])
    data=np.fromfile(out,dtype=np.float32)
    if data.size % len(ids)!=0:
        raise RuntimeError(f'llama logits size {data.size} is not divisible by token count {len(ids)}')
    return data.reshape(len(ids),data.size//len(ids))


def compare_logits(torch_logits,llama_logits,max_delta,top1_min):
    if torch_logits.shape!=llama_logits.shape:
        raise RuntimeError(f'logit shape mismatch: torch {torch_logits.shape}, llama.cpp {llama_logits.shape}')
    delta=np.abs(torch_logits-llama_logits)
    top1_match=float((torch_logits.argmax(axis=1)==llama_logits.argmax(axis=1)).mean())
    return {
        'max_abs_delta':float(delta.max()),
        'mean_abs_delta':float(delta.mean()),
        'top1_match':top1_match,
        'passed':bool(delta.max()<max_delta and top1_match>=top1_min),
        'max_delta_threshold':max_delta,
        'top1_threshold':top1_min,
    }


def run_generate(helper,gguf,tokenizer,prompt,tokens,context,workdir):
    if tokens<=0:
        return {'skipped':True,'reason':'tokens <= 0'}
    ids=tokenizer.encode(prompt,add_bos=True)
    generated=[]
    for _ in range(tokens):
        logits=llama_logits(helper,gguf,ids,workdir,context)
        nxt=int(logits[-1].argmax())
        ids.append(nxt)
        generated.append(nxt)
        if nxt==tokenizer.eos_id:
            break
    return {
        'backend':'libllama_dump_logits_greedy',
        'generated_token_ids':generated,
        'text':tokenizer.decode(ids),
    }


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',required=True)
    p.add_argument('--tokenizer',required=True)
    p.add_argument('--gguf',required=True)
    p.add_argument('--llama-cpp-dir',required=True)
    p.add_argument('--prompt',default='Xin chao')
    p.add_argument('--context',type=int,default=128)
    p.add_argument('--threads',type=int,default=1)
    p.add_argument('--generate-tokens',type=int,default=8)
    p.add_argument('--max-input-tokens',type=int,default=64)
    p.add_argument('--normal-max-delta',type=float,default=1e-3)
    p.add_argument('--normal-top1-min',type=float,default=1.0)
    p.add_argument('--stress-scale',type=float,default=12.0)
    p.add_argument('--stress-max-delta',type=float,default=0.1)
    p.add_argument('--stress-top1-min',type=float,default=0.95)
    p.add_argument('--skip-stress',action='store_true')
    p.add_argument('--trust-checkpoint',action='store_true')
    p.add_argument('--out')
    return p.parse_args()


def main():
    args=parse_args()
    llama_cpp_dir=Path(args.llama_cpp_dir)
    if not llama_cpp_dir.exists():
        raise SystemExit(f'llama.cpp directory not found: {llama_cpp_dir}')
    if not Path(args.gguf).exists():
        raise SystemExit(f'GGUF file not found: {args.gguf}')

    tok=Tokenizer(args.tokenizer)
    ids=tok.encode(args.prompt,add_bos=True)[:args.max_input_tokens]
    if len(ids)<2:
        raise SystemExit('prompt must encode to at least two tokens')

    with tempfile.TemporaryDirectory(prefix='achitic-verify-gguf-') as td:
        workdir=Path(td)
        helper=build_helper(llama_cpp_dir,workdir)
        normal=compare_logits(
            pytorch_logits(args.checkpoint,ids,trust_checkpoint=args.trust_checkpoint),
            llama_logits(helper,Path(args.gguf),ids,workdir,args.context),
            args.normal_max_delta,
            args.normal_top1_min,
        )
        stress=None
        if not args.skip_stress:
            _,stress_gguf=export_stress_gguf(args.checkpoint,args.tokenizer,workdir/'stress.gguf',args.stress_scale,trust_checkpoint=args.trust_checkpoint)
            stress=compare_logits(
                pytorch_logits(args.checkpoint,ids,stress_scale=args.stress_scale,trust_checkpoint=args.trust_checkpoint),
                llama_logits(helper,stress_gguf,ids,workdir,args.context),
                args.stress_max_delta,
                args.stress_top1_min,
            )
        generation=run_generate(helper,Path(args.gguf),tok,args.prompt,args.generate_tokens,args.context,workdir)

    payload={
        'status':'PASS' if normal['passed'] and (stress is None or stress['passed']) else 'FAIL',
        'llama_cpp_dir':str(llama_cpp_dir),
        'llama_cpp_commit':llama_commit(llama_cpp_dir),
        'checkpoint':args.checkpoint,
        'tokenizer':args.tokenizer,
        'gguf':args.gguf,
        'prompt':args.prompt,
        'token_ids':ids,
        'normal':normal,
        'stress':stress,
        'generation':generation,
    }
    text=json.dumps(payload,ensure_ascii=False,indent=2)
    if args.out:
        Path(args.out).write_text(text+'\n',encoding='utf8')
    print(text)
    if payload['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
