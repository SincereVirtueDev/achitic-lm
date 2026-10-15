import json
import warnings
from pathlib import Path

import numpy as np
import torch

from .model import AchiticLM,Config


def _numpy_safe_globals():
    from numpy._core.multiarray import _reconstruct

    return [_reconstruct,np.ndarray,np.dtype,type(np.dtype('uint32'))]


def safe_torch_load(path,map_location='cpu'):
    with torch.serialization.safe_globals(_numpy_safe_globals()):
        return torch.load(path,map_location=map_location,weights_only=True)


def trusted_torch_load(path,map_location='cpu'):
    warnings.warn(
        'Loading checkpoint with weights_only=False. Only use --trust-checkpoint for trusted local artifacts.',
        RuntimeWarning,
        stacklevel=2,
    )
    return torch.load(path,map_location=map_location,weights_only=False)


def load_checkpoint_dict(path,map_location='cpu',trust_checkpoint=False):
    try:
        return safe_torch_load(path,map_location=map_location)
    except Exception as exc:
        if trust_checkpoint:
            return trusted_torch_load(path,map_location=map_location)
        raise RuntimeError(
            f'failed to safely load checkpoint {path}; pass --trust-checkpoint only for trusted local artifacts'
        ) from exc


def _config_from_metadata(metadata):
    if metadata is None or 'config' not in metadata:
        raise ValueError('weights metadata must include config')
    return Config(**json.loads(metadata['config']))


def _state_with_tied_head(state):
    if 'head.weight' not in state and 'embed.weight' in state:
        state=dict(state)
        state['head.weight']=state['embed.weight']
    return state


def load_weights(path,map_location='cpu',trust_checkpoint=False):
    path=Path(path)
    if path.suffix=='.safetensors':
        try:
            from safetensors.torch import load_file, safe_open
        except ImportError as exc:
            raise RuntimeError('safetensors is required to load .safetensors weights') from exc
        with safe_open(str(path),framework='pt',device='cpu') as f:
            metadata=f.metadata() or {}
            cfg=_config_from_metadata(metadata)
        state=load_file(str(path),device='cpu')
        state=_state_with_tied_head(state)
        if map_location not in (None,'cpu',torch.device('cpu')):
            device=torch.device(map_location)
            state={k:v.to(device) for k,v in state.items()}
        source_step=metadata.get('source_step','')
        return {
            'config':vars(cfg),
            'model':state,
            'checkpoint_format':'weights-only-safetensors',
            'step':int(source_step) if source_step else None,
            'stage':metadata.get('stage') or None,
        }

    ck=load_checkpoint_dict(path,map_location=map_location,trust_checkpoint=trust_checkpoint)
    if 'config' not in ck or 'model' not in ck:
        raise ValueError('checkpoint must contain config and model')
    ck=dict(ck)
    ck['model']=_state_with_tied_head(ck['model'])
    return ck


def load_model(path,map_location='cpu',trust_checkpoint=False):
    ck=load_weights(path,map_location=map_location,trust_checkpoint=trust_checkpoint)
    cfg=Config(**ck['config'])
    model=AchiticLM(cfg).to(map_location)
    model.load_state_dict(ck['model'])
    return model,cfg,ck


def save_safetensors_weights(checkpoint,out,dtype='fp16',trust_checkpoint=False):
    try:
        from safetensors.torch import save_file
    except ImportError as exc:
        raise RuntimeError('safetensors is required to export weights') from exc
    if dtype not in {'fp16','fp32'}:
        raise ValueError('dtype must be fp16 or fp32')
    ck=load_weights(checkpoint,map_location='cpu',trust_checkpoint=trust_checkpoint)
    state={}
    for name,tensor in ck['model'].items():
        if name=='head.weight':
            continue
        value=tensor.detach().cpu()
        if value.is_floating_point() and dtype=='fp16':
            value=value.half()
        elif value.is_floating_point() and dtype=='fp32':
            value=value.float()
        state[name]=value
    cfg=Config(**ck['config'])
    metadata={
        'format':'achitic_weights_only',
        'dtype':dtype,
        'config':json.dumps(vars(cfg),sort_keys=True),
        'source_checkpoint_format':str(ck.get('checkpoint_format')),
        'source_step':str(ck.get('step')) if ck.get('step') is not None else '',
        'stage':str(ck.get('stage') or ''),
    }
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    save_file(state,str(out),metadata=metadata)
    return {'out':str(out),'config':vars(cfg),'metadata':metadata,'tensor_count':len(state)}
