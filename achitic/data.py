import json,re,unicodedata,hashlib
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset

def clean(s):
    s=unicodedata.normalize('NFC',s).replace('\x00','')
    return re.sub(r'[ \t]+',' ',s).strip()

def prepare(inputs,out,min_chars=30):
    seen=set();n=0
    with open(out,'w',encoding='utf8') as dest:
        for name in inputs:
            with open(name,encoding='utf8') as src:
                for line in src:
                    try:
                        obj=json.loads(line);raw=obj.get('text','')
                    except json.JSONDecodeError:raw=line
                    s=clean(raw)
                    if len(s)<min_chars:continue
                    h=hashlib.sha256(s.encode()).digest()
                    if h in seen:continue
                    seen.add(h);dest.write(s.replace('\n',' ')+'\n');n+=1
    return n

def encode_corpus(tokenizer,source,out):
    ids=[]
    with open(source,encoding='utf8') as f:
        for line in f:
            ids.extend(tokenizer.encode(line,add_bos=True,add_eos=True))
    np.asarray(ids,dtype=np.int32).tofile(out)
    return len(ids)

class TokenDataset(Dataset):
    def __init__(self,path,context):
        self.ids=np.memmap(path,dtype=np.int32,mode='r');self.context=context
        if len(self.ids)<context+1:raise ValueError('not enough tokens')
    def __len__(self):return (len(self.ids)-1)//self.context
    def __getitem__(self,i):
        a=np.asarray(self.ids[i*self.context:i*self.context+self.context+1]).astype('int64')
        return torch.from_numpy(a[:-1].copy()),torch.from_numpy(a[1:].copy())
