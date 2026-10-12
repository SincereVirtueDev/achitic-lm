import random

import numpy as np
import pytest
import torch

from achitic.model import AchiticLM,Config
from achitic.train import RESUME_SEMANTICS,load_checkpoint,save


def _small_config():
    return Config(vocab_size=64,dim=32,layers=1,heads=4,kv_heads=2,ffn_dim=64,context=16)


def _trained_model_and_optimizer():
    torch.manual_seed(7)
    cfg=_small_config()
    model=AchiticLM(cfg)
    opt=torch.optim.AdamW(model.parameters(),lr=0.01)
    x=torch.randint(0,cfg.vocab_size,(2,8))
    _,loss=model(x,x)
    loss.backward()
    opt.step()
    opt.zero_grad(set_to_none=True)
    return cfg,model,opt


def test_save_checkpoint_contains_loadable_contract(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    path=tmp_path/'nano.pt'
    save(path,model,opt,step=3,cfg=cfg)

    ck=torch.load(path,map_location='cpu',weights_only=False)
    assert {'model','optimizer','step','config','rng','numpy_rng','python_rng'} <= set(ck)
    assert ck['checkpoint_format']==1
    assert ck['resume_semantics']==RESUME_SEMANTICS
    assert ck['step']==3
    assert ck['config']==vars(cfg)
    assert isinstance(ck['rng'],torch.Tensor)
    assert ck['cuda_rng'] is None or isinstance(ck['cuda_rng'],list)
    assert isinstance(ck['numpy_rng'],tuple)
    assert isinstance(ck['python_rng'],tuple)

    loaded_cfg=Config(**ck['config'])
    loaded_model=AchiticLM(loaded_cfg)
    result=loaded_model.load_state_dict(ck['model'])
    assert result.missing_keys==[]
    assert result.unexpected_keys==[]

    loaded_opt=torch.optim.AdamW(loaded_model.parameters(),lr=0.01)
    loaded_opt.load_state_dict(ck['optimizer'])
    assert len(loaded_opt.state)>0

    probe=torch.randint(0,cfg.vocab_size,(1,5))
    with torch.no_grad():
        expected,_=model(probe)
        actual,_=loaded_model(probe)
    assert torch.allclose(actual,expected)


def test_load_checkpoint_restores_step_config_optimizer_and_rng(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    path=tmp_path/'resume.pt'

    torch.manual_seed(1234);np.random.seed(1234);random.seed(1234)
    expected_torch=torch.rand(4)
    expected_numpy=np.random.random(4)
    expected_python=[random.random() for _ in range(4)]

    torch.manual_seed(1234);np.random.seed(1234);random.seed(1234)
    save(path,model,opt,step=11,cfg=cfg)
    torch.rand(8);np.random.random(8);[random.random() for _ in range(8)]

    loaded_model=AchiticLM(cfg)
    loaded_opt=torch.optim.AdamW(loaded_model.parameters(),lr=0.01)
    step,loaded_cfg,ck=load_checkpoint(path,loaded_model,loaded_opt)

    assert step==11
    assert loaded_cfg==cfg
    assert ck['resume_semantics']==RESUME_SEMANTICS
    assert len(loaded_opt.state)>0
    assert torch.allclose(torch.rand(4),expected_torch)
    assert np.allclose(np.random.random(4),expected_numpy)
    assert [random.random() for _ in range(4)]==expected_python


def test_load_checkpoint_rejects_config_mismatch(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    path=tmp_path/'mismatch.pt'
    save(path,model,opt,step=1,cfg=cfg)

    mismatched=Config(vocab_size=64,dim=32,layers=1,heads=4,kv_heads=2,ffn_dim=64,context=8)
    mismatched_model=AchiticLM(mismatched)
    mismatched_opt=torch.optim.AdamW(mismatched_model.parameters())
    with pytest.raises(ValueError,match='checkpoint config does not match model config'):
        load_checkpoint(path,mismatched_model,mismatched_opt)
