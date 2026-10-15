import hashlib
import json
import subprocess
import sys

import numpy as np
import torch

from achitic.model import AchiticLM,Config
from achitic.train import build_optimizer,learning_rate_for_step,load_checkpoint,save


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_train_writes_metrics_and_run_manifest(tmp_path):
    config=tmp_path/'config.json'
    data=tmp_path/'train.bin'
    tokenizer=tmp_path/'tokenizer.model'
    checkpoint=tmp_path/'model.pt'
    metrics=tmp_path/'metrics.jsonl'
    manifest=tmp_path/'manifest.json'

    config.write_text(json.dumps({
        'vocab_size':64,
        'dim':32,
        'layers':1,
        'heads':4,
        'kv_heads':2,
        'ffn_dim':64,
        'context':8,
    }),encoding='utf8')
    (np.arange(65,dtype=np.int32)%64).tofile(data)
    tokenizer.write_bytes(b'fake tokenizer bytes for checksum only')

    subprocess.run([
        sys.executable,'-m','achitic.train',
        '--config',str(config),
        '--data',str(data),
        '--out',str(checkpoint),
        '--steps','2',
        '--batch','1',
        '--accum','1',
        '--lr','0.001',
        '--metrics',str(metrics),
        '--run-manifest',str(manifest),
        '--tokenizer',str(tokenizer),
    ],check=True,cwd='.')

    rows=[json.loads(line) for line in metrics.read_text(encoding='utf8').splitlines()]
    assert len(rows)==2
    assert rows[0]['step']==1
    assert rows[1]['step']==2
    for row in rows:
        assert row['train_loss']>0
        assert row['lr']==0.001
        assert row['tokens_this_step']==8
        assert row['tokens_per_second']>0
        assert row['grad_norm']>=0
        assert row['device']=='cpu'
        assert row['dtype']=='float32'
        assert row['compute_dtype']=='fp32'
        assert row['val_loss'] is None
        assert row['best_val_loss'] is None
        assert row['max_rss_bytes']>0

    run=json.loads(manifest.read_text(encoding='utf8'))
    assert run['status']=='completed'
    assert run['config_sha256']==sha256(config)
    assert run['data_sha256']==sha256(data)
    assert run['tokenizer_sha256']==sha256(tokenizer)
    assert run['device']=='cpu'
    assert run['dtype']=='float32'
    assert run['compute_dtype']=='fp32'
    assert run['requested_dtype']=='fp32'
    assert run['final_step']==2
    assert run['tokens_seen']==16
    assert run['checkpoint_format']==1
    assert run['resume_semantics']=='model_optimizer_rng_restored_data_order_not_exact'
    assert run['schedule']=='constant'
    assert run['warmup_steps']==0
    assert run['min_lr_ratio']==1.0
    assert run['weight_decay']==0.1
    assert run['val_data_path'] is None
    assert run['best_checkpoint_path'] is None

    ck=torch.load(checkpoint,map_location='cpu',weights_only=False)
    assert ck['step']==2
    assert ck['config']['vocab_size']==64


def test_learning_rate_schedule_matches_formula():
    assert learning_rate_for_step(1.0,0,100,warmup_steps=10,min_lr_ratio=0.1,schedule='cosine')==0.0
    assert learning_rate_for_step(1.0,10,100,warmup_steps=10,min_lr_ratio=0.1,schedule='cosine')==1.0
    assert abs(learning_rate_for_step(1.0,55,100,warmup_steps=10,min_lr_ratio=0.1,schedule='cosine')-0.55)<1e-12
    assert abs(learning_rate_for_step(1.0,100,100,warmup_steps=10,min_lr_ratio=0.1,schedule='cosine')-0.1)<1e-12
    assert learning_rate_for_step(0.001,5,20,schedule='constant')==0.001


def test_optimizer_weight_decay_groups_cover_unique_trainable_params():
    cfg=Config(vocab_size=64,dim=32,layers=1,heads=4,kv_heads=2,ffn_dim=64,context=8)
    model=AchiticLM(cfg)
    opt=build_optimizer(model,lr=0.001,weight_decay=0.25)

    params=[param for group in opt.param_groups for param in group['params']]
    assert len(params)==len({id(param) for param in params})
    expected={id(param) for param in model.parameters() if param.requires_grad}
    assert {id(param) for param in params}==expected

    groups_by_id={}
    for group in opt.param_groups:
        for param in group['params']:
            groups_by_id[id(param)]=group['weight_decay']

    assert groups_by_id[id(model.embed.weight)]==0.0
    for name,param in model.named_parameters():
        if not param.requires_grad:continue
        if param.ndim<2 or name=='embed.weight':
            assert groups_by_id[id(param)]==0.0
        else:
            assert groups_by_id[id(param)]==0.25


def test_load_checkpoint_migrates_legacy_single_optimizer_group(tmp_path):
    cfg=Config(vocab_size=64,dim=32,layers=1,heads=4,kv_heads=2,ffn_dim=64,context=8)
    model=AchiticLM(cfg)
    legacy_opt=torch.optim.AdamW(model.parameters(),lr=0.001,weight_decay=0.1)
    x=torch.randint(0,cfg.vocab_size,(1,8))
    _,loss=model(x,x)
    loss.backward();legacy_opt.step();legacy_opt.zero_grad(set_to_none=True)
    checkpoint=tmp_path/'legacy.pt'
    save(checkpoint,model,legacy_opt,step=2,cfg=cfg)

    loaded=AchiticLM(cfg)
    grouped_opt=build_optimizer(loaded,lr=0.001,weight_decay=0.1)
    step,_,_=load_checkpoint(checkpoint,loaded,grouped_opt)

    assert step==2
    assert len(grouped_opt.param_groups)==2
    assert len(grouped_opt.state)>0


def _write_train_fixture(tmp_path):
    config=tmp_path/'config.json'
    train=tmp_path/'train.bin'
    val=tmp_path/'val.bin'
    tokenizer=tmp_path/'tokenizer.model'
    config.write_text(json.dumps({
        'vocab_size':64,
        'dim':32,
        'layers':1,
        'heads':4,
        'kv_heads':2,
        'ffn_dim':64,
        'context':8,
    }),encoding='utf8')
    (np.arange(129,dtype=np.int32)%64).tofile(train)
    ((np.arange(65,dtype=np.int32)+7)%64).tofile(val)
    tokenizer.write_bytes(b'fake tokenizer bytes for checksum only')
    return config,train,val,tokenizer


def test_train_eval_writes_best_checkpoint_and_manifest(tmp_path):
    config,train,val,tokenizer=_write_train_fixture(tmp_path)
    checkpoint=tmp_path/'model.pt'
    metrics=tmp_path/'metrics.jsonl'
    manifest=tmp_path/'manifest.json'
    best=tmp_path/'model.pt.best.pt'

    subprocess.run([
        sys.executable,'-m','achitic.train',
        '--config',str(config),
        '--data',str(train),
        '--val-data',str(val),
        '--out',str(checkpoint),
        '--steps','2',
        '--batch','1',
        '--accum','1',
        '--lr','0.001',
        '--schedule','cosine',
        '--warmup-steps','1',
        '--min-lr-ratio','0.1',
        '--weight-decay','0.05',
        '--eval-every','1',
        '--eval-iters','2',
        '--metrics',str(metrics),
        '--run-manifest',str(manifest),
        '--tokenizer',str(tokenizer),
    ],check=True,cwd='.')

    assert checkpoint.exists()
    assert best.exists()
    rows=[json.loads(line) for line in metrics.read_text(encoding='utf8').splitlines()]
    assert len(rows)==2
    assert [row['lr'] for row in rows]==[
        learning_rate_for_step(0.001,1,2,warmup_steps=1,min_lr_ratio=0.1,schedule='cosine'),
        learning_rate_for_step(0.001,2,2,warmup_steps=1,min_lr_ratio=0.1,schedule='cosine'),
    ]
    assert all(row['val_loss'] is not None for row in rows)
    assert all(row['val_ppl'] is not None for row in rows)
    assert rows[-1]['best_val_loss'] is not None

    run=json.loads(manifest.read_text(encoding='utf8'))
    assert run['status']=='completed'
    assert run['val_data_sha256']==sha256(val)
    assert run['schedule']=='cosine'
    assert run['warmup_steps']==1
    assert run['min_lr_ratio']==0.1
    assert run['weight_decay']==0.05
    assert run['eval_every']==1
    assert run['eval_iters']==2
    assert run['best_checkpoint_path']==str(best)
    assert run['best_val_loss'] is not None

    ck=torch.load(checkpoint,map_location='cpu',weights_only=False)
    best_ck=torch.load(best,map_location='cpu',weights_only=False)
    assert ck['best_val_loss']==run['best_val_loss']
    assert best_ck['best_val_loss']==run['best_val_loss']


def test_resume_uses_absolute_step_for_lr_schedule(tmp_path):
    config,train,_,_=_write_train_fixture(tmp_path)
    second=tmp_path/'second.pt'
    second_metrics=tmp_path/'second_metrics.jsonl'
    cfg=Config(**json.loads(config.read_text(encoding='utf8')))
    model=AchiticLM(cfg)
    opt=build_optimizer(model,lr=0.001,weight_decay=0.1)
    save(tmp_path/'resume.pt',model,opt,step=2,cfg=cfg)
    args=[
        '--config',str(config),
        '--data',str(train),
        '--batch','1',
        '--accum','1',
        '--lr','0.001',
        '--schedule','cosine',
        '--warmup-steps','1',
        '--min-lr-ratio','0.1',
    ]

    subprocess.run([
        sys.executable,'-m','achitic.train',
        *args,
        '--resume',str(tmp_path/'resume.pt'),
        '--out',str(second),
        '--steps','4',
        '--metrics',str(second_metrics),
    ],check=True,cwd='.')

    rows=[json.loads(line) for line in second_metrics.read_text(encoding='utf8').splitlines()]
    assert [row['step'] for row in rows]==[3,4]
    expected=[
        learning_rate_for_step(0.001,step,4,warmup_steps=1,min_lr_ratio=0.1,schedule='cosine')
        for step in range(3,5)
    ]
    assert [row['lr'] for row in rows]==expected


def test_train_logs_dataset_warnings_for_tiny_corpus(tmp_path):
    config=tmp_path/'config.json'
    data=tmp_path/'train.bin'
    checkpoint=tmp_path/'model.pt'
    config.write_text(json.dumps({
        'vocab_size':64,
        'dim':32,
        'layers':1,
        'heads':4,
        'kv_heads':2,
        'ffn_dim':64,
        'context':8,
    }),encoding='utf8')
    (np.arange(17,dtype=np.int32)%64).tofile(data)

    result=subprocess.run([
        sys.executable,'-m','achitic.train',
        '--config',str(config),
        '--data',str(data),
        '--out',str(checkpoint),
        '--steps','1',
        '--batch','2',
        '--accum','2',
    ],check=True,cwd='.',text=True,capture_output=True)

    assert 'train windows=2 tokens=17 tokens/step=32 stride=8' in result.stdout
    assert 'dataset windows 2 < batch*accum 4' in result.stderr
    assert 'train token budget 32 exceeds unique target tokens 16' in result.stderr
