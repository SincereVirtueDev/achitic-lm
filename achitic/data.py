import json,re,unicodedata,hashlib
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset

def clean(s):
    s=unicodedata.normalize('NFC',s).replace('\x00','')
    return re.sub(r'[ \t]+',' ',s).strip()

def _prepare_text_from_line(line,input_format):
    if input_format=='text':
        return line,None
    if input_format not in {'auto','jsonl'}:
        raise ValueError("input_format must be one of: auto, text, jsonl")
    try:
        obj=json.loads(line)
    except json.JSONDecodeError:
        if input_format=='jsonl':return '', 'skipped_json_decode_error'
        return line,None
    if isinstance(obj,dict):
        if 'text' not in obj:return (line,None) if input_format=='auto' else ('','skipped_jsonl_missing_text')
        if not isinstance(obj['text'],str):return (line,None) if input_format=='auto' else ('','skipped_jsonl_invalid_text')
        return obj['text'],None
    if input_format=='jsonl':return '', 'skipped_jsonl_invalid_type'
    return line,None

def prepare(inputs,out,min_chars=30,input_format='auto',return_stats=False):
    if input_format not in {'auto','text','jsonl'}:
        raise ValueError("input_format must be one of: auto, text, jsonl")
    seen=set();n=0
    stats={
        'documents':0,
        'input_lines':0,
        'skipped_short':0,
        'skipped_duplicate':0,
        'skipped_json_decode_error':0,
        'skipped_jsonl_missing_text':0,
        'skipped_jsonl_invalid_text':0,
        'skipped_jsonl_invalid_type':0,
    }
    with open(out,'w',encoding='utf8') as dest:
        for name in inputs:
            with open(name,encoding='utf8') as src:
                for line in src:
                    stats['input_lines']+=1
                    raw,skip=_prepare_text_from_line(line,input_format)
                    if skip:
                        stats[skip]+=1
                        continue
                    s=clean(raw)
                    if len(s)<min_chars:
                        stats['skipped_short']+=1
                        continue
                    h=hashlib.sha256(s.encode()).digest()
                    if h in seen:
                        stats['skipped_duplicate']+=1
                        continue
                    seen.add(h);dest.write(s.replace('\n',' ')+'\n');n+=1
    stats['documents']=n
    if return_stats:return stats
    return n

def encode_corpus(tokenizer,source,out,chunk_tokens=1_000_000,return_stats=False):
    if chunk_tokens<1:
        raise ValueError('chunk_tokens must be >= 1')
    vocab_size=getattr(tokenizer,'vocab_size',None)
    if vocab_size is not None and vocab_size>=2**31:
        raise ValueError('tokenizer vocab size must be < 2**31 for int32 encoding')
    chunk=[];total=0;lines=0;chunks=0
    def flush(dest):
        nonlocal chunk,total,chunks
        if not chunk:return
        arr=np.asarray(chunk,dtype=np.int32)
        arr.tofile(dest)
        total+=int(arr.size);chunks+=1;chunk=[]
    with open(source,encoding='utf8') as f:
        with open(out,'wb') as dest:
            for line in f:
                ids=tokenizer.encode(line,add_bos=True,add_eos=True)
                if ids:
                    max_id=max(ids);min_id=min(ids)
                    if min_id<0 or max_id>=2**31:
                        raise ValueError('token id out of int32 range')
                chunk.extend(ids);lines+=1
                if len(chunk)>=chunk_tokens:flush(dest)
            flush(dest)
    stats={'tokens':total,'lines':lines,'chunks':chunks,'chunk_tokens':int(chunk_tokens),'bytes_written':total*4}
    if return_stats:return stats
    return total

def token_packing_report(path,context,stride=None):
    if context<1:raise ValueError('context must be >= 1')
    if stride is None:stride=context
    if stride<1:raise ValueError('stride must be >= 1')
    ids=np.memmap(path,dtype=np.int32,mode='r')
    total_tokens=int(len(ids))
    if total_tokens<context+1:raise ValueError('not enough tokens')
    target_tokens=total_tokens-1
    windows=1+(target_tokens-context)//stride
    used_target_tokens=(windows-1)*stride+context
    wasted_target_tokens=target_tokens-used_target_tokens
    tokens_per_epoch=windows*context
    return {
        'path':str(path),
        'context':int(context),
        'stride':int(stride),
        'total_tokens':total_tokens,
        'target_tokens':target_tokens,
        'windows':int(windows),
        'used_target_tokens':int(used_target_tokens),
        'tokens_per_epoch':int(tokens_per_epoch),
        'wasted_target_tokens':int(wasted_target_tokens),
        'waste_ratio':wasted_target_tokens/target_tokens,
        'max_possible_waste_tokens':context-1,
        'overlap_tokens_per_window':max(context-stride,0),
        'packing_strategy':'contiguous_fixed_context_chunks' if stride==context else 'strided_fixed_context_windows',
    }

class TokenDataset(Dataset):
    def __init__(self,path,context,stride=None):
        self.ids=np.memmap(path,dtype=np.int32,mode='r');self.context=context
        self.stride=context if stride is None else stride
        if self.context<1:raise ValueError('context must be >= 1')
        if self.stride<1:raise ValueError('stride must be >= 1')
        if len(self.ids)<context+1:raise ValueError('not enough tokens')
    def __len__(self):return 1+((len(self.ids)-1)-self.context)//self.stride
    def __getitem__(self,i):
        start=i*self.stride
        a=np.asarray(self.ids[start:start+self.context+1]).astype('int64')
        return torch.from_numpy(a[:-1].copy()),torch.from_numpy(a[1:].copy())
