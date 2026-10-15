import sys

import torch

from achitic import cli
from achitic.model import Config


class FakeSentencePiece:
    def piece_to_id(self,piece):
        return {'<|user|>':10,'<|assistant|>':11}[piece]


class FakeTokenizer:
    vocab_size=64
    bos_id=1
    eos_id=2
    unk_id=0
    sp=FakeSentencePiece()

    def __init__(self,path):
        self.path=path

    def encode(self,text,add_bos=False,add_eos=False):
        if text.startswith('<|user|>') and text.endswith('<|assistant|>'):
            ids=[10,20,11]
        else:
            ids=[20]
        return ([self.bos_id] if add_bos else [])+ids+([self.eos_id] if add_eos else [])

    def decode(self,ids):
        return 'decoded'


class FakeModel(torch.nn.Module):
    def __init__(self,cfg,captured):
        super().__init__()
        self.config=cfg
        self.captured=captured

    def load_state_dict(self,state):
        return None

    def generate(self,ids,max_new_tokens=40,temperature=0.8,top_k=40,eos_id=None,use_cache=True,stop_ids=None):
        self.captured['ids']=ids.detach().cpu().tolist()
        self.captured['eos_id']=eos_id
        self.captured['stop_ids']=list(stop_ids)
        return ids


def run_chat(monkeypatch,captured,argv,stage='sft'):
    cfg=Config(vocab_size=64,dim=16,layers=1,heads=2,kv_heads=1,ffn_dim=32,context=16)
    monkeypatch.setattr(cli,'load_weights',lambda *args,**kwargs:{'config':vars(cfg),'model':{},'stage':stage})
    monkeypatch.setattr(cli,'Tokenizer',FakeTokenizer)
    monkeypatch.setattr(cli,'AchiticLM',lambda cfg:FakeModel(cfg,captured))
    monkeypatch.setattr(sys,'argv',argv)
    cli.main()


def test_aligned_checkpoint_defaults_to_achitic_chat_template(monkeypatch,capsys):
    captured={}
    run_chat(monkeypatch,captured,[
        'cli','chat','--checkpoint','aligned.pt','--tokenizer','fake.model','--prompt','xin chao','--tokens','4'
    ],stage='sft')

    assert captured['ids']==[[1,10,20,11]]
    assert captured['eos_id']==2
    assert captured['stop_ids']==[2,10]
    assert capsys.readouterr().out.strip()=='decoded'


def test_chat_template_none_overrides_aligned_checkpoint_default(monkeypatch):
    captured={}
    run_chat(monkeypatch,captured,[
        'cli','chat','--checkpoint','aligned.pt','--tokenizer','fake.model','--prompt','xin chao',
        '--tokens','4','--chat-template','none'
    ],stage='dpo')

    assert captured['ids']==[[1,20]]
    assert captured['stop_ids']==[2]


def test_base_checkpoint_defaults_to_raw_prompt(monkeypatch):
    captured={}
    run_chat(monkeypatch,captured,[
        'cli','chat','--checkpoint','base.pt','--tokenizer','fake.model','--prompt','xin chao','--tokens','4'
    ],stage=None)

    assert captured['ids']==[[1,20]]
    assert captured['stop_ids']==[2]
