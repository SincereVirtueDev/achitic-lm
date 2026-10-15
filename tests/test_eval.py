import json

import numpy as np
import pytest
import torch
from torch.nn import functional as F

from achitic.eval import evaluate_model,generated_sample_checks,load_fixed_prompts,sample_model
from achitic.model import Config


class GradProbeModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.config=Config(vocab_size=16,dim=8,layers=1,heads=1,kv_heads=1,ffn_dim=16,context=4)
        self.grad_enabled=[]

    def forward(self,x,targets=None):
        self.grad_enabled.append(torch.is_grad_enabled())
        logits=torch.zeros(x.shape[0],x.shape[1],self.config.vocab_size,device=x.device)
        loss=F.cross_entropy(logits.reshape(-1,logits.size(-1)),targets.reshape(-1))
        return logits,loss


class ToyTokenizer:
    eos_id=2

    def encode(self,text,add_bos=False,add_eos=False):
        ids=[4+len(text)%3]
        if add_bos:ids=[1]+ids
        if add_eos:ids=ids+[2]
        return ids

    def decode(self,ids):
        return 'decoded:'+' '.join(str(i) for i in ids)


class ToyGenerator(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.grad_enabled=[]

    def generate(self,ids,max_new_tokens=40,temperature=0.8,top_k=40,eos_id=None):
        self.grad_enabled.append(torch.is_grad_enabled())
        extra=torch.full((ids.shape[0],max_new_tokens),5,device=ids.device,dtype=ids.dtype)
        return torch.cat((ids,extra),dim=1)


def test_evaluate_model_uses_no_grad_and_restores_training_mode(tmp_path):
    data=tmp_path/'eval.bin'
    (np.arange(13,dtype=np.int32)%16).tofile(data)
    model=GradProbeModel()
    model.train()

    result=evaluate_model(model,data,context=4,batch=2,device='cpu')

    assert result.batches==2
    assert result.tokens==12
    assert result.loss==pytest.approx(float(torch.log(torch.tensor(16.0))))
    assert model.training is True
    assert model.grad_enabled==[False,False]


def test_load_fixed_prompts_requires_id_and_prompt(tmp_path):
    prompts=tmp_path/'prompts.jsonl'
    prompts.write_text(json.dumps({'id':'vi-basic','language':'vi','prompt':'Xin chào'},ensure_ascii=False)+'\n',encoding='utf8')

    assert load_fixed_prompts(prompts)==[{'id':'vi-basic','language':'vi','prompt':'Xin chào'}]

    bad=tmp_path/'bad.jsonl'
    bad.write_text(json.dumps({'id':'missing-prompt'})+'\n',encoding='utf8')
    with pytest.raises(ValueError,match='must include id and prompt'):
        load_fixed_prompts(bad)


def test_sample_model_uses_no_grad_and_reports_generated_tokens():
    model=ToyGenerator()
    model.train()
    prompts=[{'id':'en-basic','language':'en','prompt':'Hello'}]

    rows=sample_model(model,ToyTokenizer(),prompts,max_new_tokens=3,device='cpu')

    assert len(rows)==1
    assert rows[0].id=='en-basic'
    assert rows[0].chat_template=='none'
    assert rows[0].generated_tokens==3
    assert rows[0].generated_text=='decoded:5 5 5'
    assert rows[0].output.startswith('decoded:')
    assert rows[0].checks['contains_reserved_token'] is False
    assert model.training is True
    assert model.grad_enabled==[False]


def test_generated_sample_checks_reject_reserved_and_repeated_output():
    checks=generated_sample_checks('<|reserved_7|> lặp lặp lặp',[7,7,7,7,7,7],min_tokens=4,max_tokens=8,max_repeat_ratio=0.25)

    assert checks['contains_reserved_token'] is True
    assert checks['has_sentence_boundary'] is False
    assert checks['repeat_ok'] is False
    assert checks['automatic_pass'] is False


def test_generated_sample_checks_accepts_short_complete_sentence():
    checks=generated_sample_checks('Dữ liệu giúp mô hình học tốt.',[10,11,12,13,14,15],min_tokens=4,max_tokens=8)

    assert checks['automatic_pass'] is True


def test_sample_model_applies_achitic_chat_template():
    model=ToyGenerator()
    tok=ToyTokenizer()
    captured=[]
    original=tok.encode
    def encode(text,add_bos=False,add_eos=False):
        captured.append(text)
        return original(text,add_bos=add_bos,add_eos=add_eos)
    tok.encode=encode

    rows=sample_model(model,tok,[{'id':'vi','language':'vi','prompt':'Xin chào'}],max_new_tokens=3,
      device='cpu',chat_template='achitic')

    assert captured==['<|user|>Xin chào<|assistant|>']
    assert rows[0].chat_template=='achitic'
