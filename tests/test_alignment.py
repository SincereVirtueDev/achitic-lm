import json
import sys

import pytest
import torch

from achitic import alignment
from achitic.alignment import sequence_logprob
from achitic.model import AchiticLM,Config


class ResponseOnlyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.weight=torch.nn.Parameter(torch.zeros(()))
        self.config=Config(vocab_size=8,dim=8,layers=1,heads=1,kv_heads=1,ffn_dim=16,context=8)

    def forward(self,ids,targets=None):
        logits=torch.zeros(ids.shape[0],ids.shape[1],self.config.vocab_size,device=ids.device)
        logits[:,0,0]=100.0
        logits[:,0,2]=-100.0
        logits[:,1,3]=100.0
        logits[:,2,4]=100.0
        return logits,None


def test_sequence_logprob_returns_finite_response_score():
    cfg=Config(vocab_size=32,dim=16,layers=1,heads=2,kv_heads=1,ffn_dim=32,context=8)
    model=AchiticLM(cfg).eval()
    with torch.no_grad():
        score=sequence_logprob(model,[1,2],[3,4])
    assert score.shape==(1,)
    assert torch.isfinite(score).all()


def test_sequence_logprob_excludes_prompt_only_positions():
    model=ResponseOnlyModel()
    with torch.no_grad():
        score=sequence_logprob(model,[1,2],[3,4])
    assert score.item()>-1e-4


def test_sequence_logprob_rejects_empty_prompt():
    model=ResponseOnlyModel()
    with pytest.raises(ValueError,match='invalid sequence length'):
        sequence_logprob(model,[],[3])


def test_sequence_logprob_rejects_context_overflow():
    model=ResponseOnlyModel()
    with pytest.raises(ValueError,match='invalid sequence length'):
        sequence_logprob(model,[1,2,3,4],[5,6,7,1,2])


def test_sft_main_masks_prompt_targets(monkeypatch,tmp_path):
    captured={}

    class FakeTokenizer:
        def __init__(self,path):
            pass

        def encode(self,text,add_bos=False,add_eos=False):
            values={'prompt':[10,11,12],'response':[20,21]}[text]
            return ([1] if add_bos else [])+values+([2] if add_eos else [])

    class FakeModel(torch.nn.Module):
        def __init__(self,cfg):
            super().__init__()
            self.config=cfg
            self.weight=torch.nn.Parameter(torch.zeros(()))

        def load_state_dict(self,state):
            return None

        def forward(self,x,targets=None):
            captured['x']=x.detach().cpu()
            captured['targets']=targets.detach().cpu()
            return torch.zeros(x.shape[0],x.shape[1],self.config.vocab_size,device=x.device),self.weight.square()

    ckpt=tmp_path/'base.pt'
    data=tmp_path/'sft.jsonl'
    out=tmp_path/'sft.pt'
    cfg=Config(vocab_size=64,dim=16,layers=1,heads=2,kv_heads=1,ffn_dim=32,context=16)
    torch.save({'model':{},'config':vars(cfg)},ckpt)
    data.write_text(json.dumps({'prompt':'prompt','response':'response'})+'\n',encoding='utf8')

    monkeypatch.setattr(alignment,'Tokenizer',FakeTokenizer)
    monkeypatch.setattr(alignment,'AchiticLM',FakeModel)
    monkeypatch.setattr(sys,'argv',[
        'alignment','--mode','sft','--checkpoint',str(ckpt),'--tokenizer','fake.model',
        '--data',str(data),'--out',str(out),'--steps','1'
    ])

    alignment.main()

    assert captured['x'].tolist()==[[1,10,11,12,20,21]]
    assert captured['targets'].tolist()==[[-100,-100,-100,20,21,2]]
    assert out.exists()
