import os
from pathlib import Path

import sentencepiece as spm

USER_SYMBOLS=['<|system|>','<|user|>','<|assistant|>','<|tool|>','<|tool_result|>']
DEFAULT_MAX_RESERVED_RATIO=0.05
DEFAULT_INPUT_SENTENCE_SIZE=5_000_000

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

def _train_once(source,prefix,vocab_size,user_symbols,input_sentence_size=DEFAULT_INPUT_SENTENCE_SIZE,
  shuffle_input_sentence=True,num_threads=None):
    if input_sentence_size is None:input_sentence_size=0
    if input_sentence_size is not None and input_sentence_size<0:
        raise ValueError('input_sentence_size must be >= 0')
    if num_threads is None:num_threads=os.cpu_count() or 1
    if num_threads<1:raise ValueError('num_threads must be >= 1')
    kwargs={
        'input':str(source),
        'model_prefix':str(prefix),
        'vocab_size':vocab_size,
        'model_type':'bpe',
        'character_coverage':0.9995,
        'byte_fallback':True,
        'bos_id':1,
        'eos_id':2,
        'unk_id':0,
        'pad_id':3,
        'user_defined_symbols':user_symbols,
        'hard_vocab_limit':False,
        'input_sentence_size':input_sentence_size,
        'shuffle_input_sentence':shuffle_input_sentence,
        'num_threads':num_threads,
    }
    with open(os.devnull,'w') as log:
        spm.SentencePieceTrainer.train(logstream=log,**kwargs)

def _is_reserved_piece(piece):
    return piece.startswith('<|reserved_') and piece.endswith('|>')

def tokenizer_stats(path):
    sp=spm.SentencePieceProcessor(model_file=str(path))
    stats={'vocab_size':sp.vocab_size(),'normal':0,'user_defined':0,'reserved':0,'byte':0,'control':0,'unknown':0}
    for idx in range(sp.vocab_size()):
        piece=sp.id_to_piece(idx)
        if sp.is_unknown(idx):stats['unknown']+=1
        elif sp.is_control(idx):stats['control']+=1
        elif sp.is_byte(idx):stats['byte']+=1
        elif _is_reserved_piece(piece):stats['reserved']+=1
        elif piece in USER_SYMBOLS:stats['user_defined']+=1
        else:stats['normal']+=1
    stats['reserved_ratio']=stats['reserved']/stats['vocab_size'] if stats['vocab_size'] else 0.0
    return stats

def validate_reserved_padding(stats,max_reserved_ratio=DEFAULT_MAX_RESERVED_RATIO,allow_reserved_padding=False):
    if not 0<=max_reserved_ratio<=1:
        raise ValueError('max_reserved_ratio must be between 0 and 1')
    if allow_reserved_padding:return
    if stats['reserved_ratio']>max_reserved_ratio:
        raise ValueError(
            'corpus too small for requested tokenizer vocab: '
            f"reserved tokens {stats['reserved']}/{stats['vocab_size']} "
            f"({stats['reserved_ratio']:.2%}) exceed max_reserved_ratio {max_reserved_ratio:.2%}. "
            'Reduce --vocab, use a larger corpus, or pass --allow-reserved-padding for smoke tests.'
        )

def train(source,prefix,vocab_size=8000,max_reserved_ratio=DEFAULT_MAX_RESERVED_RATIO,allow_reserved_padding=False,
  input_sentence_size=DEFAULT_INPUT_SENTENCE_SIZE,shuffle_input_sentence=True,num_threads=None):
    if vocab_size>=2**31:
        raise ValueError('vocab_size must be < 2**31 for int32 encoded corpora')
    if input_sentence_size is None:input_sentence_size=0
    if num_threads is None:num_threads=os.cpu_count() or 1
    prefix=Path(prefix);prefix.parent.mkdir(parents=True,exist_ok=True)
    reserved=[]
    for _ in range(3):
        _train_once(source,prefix,vocab_size,USER_SYMBOLS+reserved,
          input_sentence_size=input_sentence_size,shuffle_input_sentence=shuffle_input_sentence,
          num_threads=num_threads)
        actual=Tokenizer(str(prefix)+'.model').vocab_size
        if actual==vocab_size:
            stats=tokenizer_stats(str(prefix)+'.model')
            validate_reserved_padding(stats,max_reserved_ratio=max_reserved_ratio,
              allow_reserved_padding=allow_reserved_padding)
            stats['input_sentence_size']=input_sentence_size
            stats['shuffle_input_sentence']=bool(shuffle_input_sentence)
            stats['num_threads']=int(num_threads)
            return stats
        if actual>vocab_size:break
        start=len(reserved)
        reserved.extend(f'<|reserved_{i}|>' for i in range(start,start+vocab_size-actual))
    raise ValueError(f'tokenizer vocab size {actual} does not match requested vocab size {vocab_size}')
