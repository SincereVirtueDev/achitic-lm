import random
import subprocess
import sys

import numpy as np
import pytest
import torch

from achitic.checkpoint import load_model,load_weights,save_safetensors_weights
from achitic.alignment import save_alignment_checkpoint
from achitic.model import AchiticLM,Config
from achitic.train import (
    EXACT_DATA_ORDER_RESUME,
    MISSING_EXACT_RESUME_STATE,
    RESUME_SEMANTICS,
    load_checkpoint,
    resume_contract,
    save,
)


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


def test_train_resume_loads_alignment_checkpoint_with_optimizer(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    path=tmp_path/'sft.pt'
    save_alignment_checkpoint(path,model,opt,step=4,cfg=cfg,stage='sft')

    loaded_model=AchiticLM(cfg)
    loaded_opt=torch.optim.AdamW(loaded_model.parameters(),lr=0.01)
    step,loaded_cfg,ck=load_checkpoint(path,loaded_model,loaded_opt)

    assert step==4
    assert loaded_cfg==cfg
    assert ck['stage']=='sft'
    assert len(loaded_opt.state)>0


def test_weights_only_resume_requires_explicit_flag_for_old_alignment_checkpoint(tmp_path):
    cfg,model,_=_trained_model_and_optimizer()
    path=tmp_path/'old-sft.pt'
    torch.save({'model':model.state_dict(),'config':vars(cfg),'stage':'sft'},path)

    loaded_model=AchiticLM(cfg)
    loaded_opt=torch.optim.AdamW(loaded_model.parameters(),lr=0.01)
    with pytest.raises(ValueError,match='optimizer state'):
        load_checkpoint(path,loaded_model,loaded_opt)

    with pytest.warns(RuntimeWarning) as warnings:
        step,loaded_cfg,ck=load_checkpoint(path,loaded_model,loaded_opt,weights_only_resume=True)
    messages=[str(item.message) for item in warnings]
    assert any('no optimizer state' in message for message in messages)
    assert any('no RNG state' in message for message in messages)
    assert step==0
    assert loaded_cfg==cfg
    assert ck['stage']=='sft'


def test_resume_contract_explicitly_blocks_exact_data_order_claim(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    path=tmp_path/'non_exact.pt'
    save(path,model,opt,step=5,cfg=cfg)

    ck=torch.load(path,map_location='cpu',weights_only=False)
    contract=resume_contract()

    assert EXACT_DATA_ORDER_RESUME is False
    assert contract['exact_data_order_resume'] is False
    assert contract['resume_semantics']==RESUME_SEMANTICS
    assert ck['resume_semantics']=='model_optimizer_rng_restored_data_order_not_exact'
    for key in MISSING_EXACT_RESUME_STATE:
        assert key not in ck


def test_safe_load_weights_reads_pt_without_unsafe_fallback(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    path=tmp_path/'safe.pt'
    save(path,model,opt,step=9,cfg=cfg)

    ck=load_weights(path)

    assert ck['step']==9
    assert ck['config']==vars(cfg)
    assert 'model' in ck
    assert 'head.weight' in ck['model']


def test_export_safetensors_weights_omits_tied_head_and_roundtrips_logits(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    checkpoint=tmp_path/'full.pt'
    out=tmp_path/'weights.safetensors'
    save(checkpoint,model,opt,step=3,cfg=cfg)

    result=save_safetensors_weights(checkpoint,out,dtype='fp16')
    ck=load_weights(out)
    loaded,loaded_cfg,_=load_model(out)

    assert result['tensor_count']>0
    assert ck['checkpoint_format']=='weights-only-safetensors'
    assert ck['config']==vars(cfg)
    assert 'head.weight' in ck['model']
    assert loaded_cfg==cfg
    assert out.stat().st_size<checkpoint.stat().st_size

    probe=torch.randint(0,cfg.vocab_size,(1,5))
    fp16_model=AchiticLM(cfg)
    fp16_state={name:value.detach().clone() for name,value in model.state_dict().items()}
    for name,value in fp16_state.items():
        if value.is_floating_point():
            fp16_state[name]=value.half().float()
    fp16_model.load_state_dict(fp16_state)
    with torch.no_grad():
        expected,_=fp16_model(probe)
        actual,_=loaded(probe)
    assert torch.allclose(actual,expected,atol=1e-5)


def test_export_weights_script_writes_safetensors(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    checkpoint=tmp_path/'full.pt'
    out=tmp_path/'weights.safetensors'
    save(checkpoint,model,opt,step=3,cfg=cfg)

    subprocess.run([
        sys.executable,'scripts/export_weights.py',
        '--checkpoint',str(checkpoint),
        '--out',str(out),
        '--dtype','fp16',
    ],check=True,cwd='.')

    assert out.exists()
    ck=load_weights(out)
    assert ck['config']==vars(cfg)


def test_safetensors_preserves_alignment_stage_and_step(tmp_path):
    cfg,model,opt=_trained_model_and_optimizer()
    checkpoint=tmp_path/'sft.pt'
    out=tmp_path/'sft.safetensors'
    save_alignment_checkpoint(checkpoint,model,opt,step=17,cfg=cfg,stage='sft')

    save_safetensors_weights(checkpoint,out,dtype='fp16')
    ck=load_weights(out)

    assert ck['stage']=='sft'
    assert ck['step']==17
