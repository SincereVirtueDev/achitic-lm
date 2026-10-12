import os
from pathlib import Path

import sentencepiece as spm

USER_SYMBOLS=['<|system|>','<|user|>','<|assistant|>','<|tool|>','<|tool_result|>']

class Tokenizer:
    def __init__(self,path):
        self.sp=spm.SentencePieceProcessor(model_file=str(path))
    @property
    def vocab_size(self):return self.sp.vocab_size()
    @property
    def unk_id(self):return self.sp.unk_id()
    @property
    def bos_id(self):return self.sp.bos_id()
    @property
    def eos_id(self):return self.sp.eos_id()
    @property
    def pad_id(self):return self.sp.pad_id()
    def encode(self,text,add_bos=False,add_eos=False):
        ids=self.sp.encode(text)
        return ([self.bos_id] if add_bos else [])+ids+([self.eos_id] if add_eos else [])
    def decode(self,ids):return self.sp.decode(ids)

def _train_once(source,prefix,vocab_size,user_symbols):
    with open(os.devnull,'w') as log:
        spm.SentencePieceTrainer.train(input=str(source),model_prefix=str(prefix),vocab_size=vocab_size,
        model_type='bpe',character_coverage=0.9995,byte_fallback=True,
        bos_id=1,eos_id=2,unk_id=0,pad_id=3,
        user_defined_symbols=user_symbols,hard_vocab_limit=False,logstream=log)

def train(source,prefix,vocab_size=8000):
    prefix=Path(prefix);prefix.parent.mkdir(parents=True,exist_ok=True)
    reserved=[]
    for _ in range(3):
        _train_once(source,prefix,vocab_size,USER_SYMBOLS+reserved)
        actual=Tokenizer(str(prefix)+'.model').vocab_size
        if actual==vocab_size:return
        if actual>vocab_size:break
        start=len(reserved)
        reserved.extend(f'<|reserved_{i}|>' for i in range(start,start+vocab_size-actual))
    raise ValueError(f'tokenizer vocab size {actual} does not match requested vocab size {vocab_size}')
