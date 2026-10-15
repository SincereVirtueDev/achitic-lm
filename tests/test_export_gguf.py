import numpy as np
import pytest
import torch

gguf=pytest.importorskip('gguf')
pytest.importorskip('google.protobuf')

from achitic.model import AchiticLM,Config,rope
from achitic.tokenizer import Tokenizer,train
from scripts.export_gguf import export_checkpoint,sentencepiece_token_types


def _field_value(reader,key):
    field=reader.fields[key]
    if hasattr(field,'contents'):
        value=field.contents()
    elif hasattr(field,'data') and hasattr(field,'parts'):
        data=field.data
        if len(data)==1:
            value=field.parts[data[0]]
        else:
            value=[field.parts[i] for i in data]
    elif hasattr(field,'data'):
        value=field.data
    else:
        value=field
    if isinstance(value,np.ndarray):
        return value.item() if value.size==1 else value.tolist()
    if isinstance(value,(list,tuple)) and len(value)==1:
        item=value[0]
        return item.item() if isinstance(item,np.ndarray) and item.size==1 else item
    return value


def _tensor_by_name(reader):
    return {tensor.name:tensor for tensor in reader.tensors}


def _tensor_array(tensor,shape):
    array=np.asarray(tensor.data)
    if array.shape==shape:
        return array
    if array.T.shape==shape:
        return array.T
    if array.size==int(np.prod(shape)):
        return array.reshape(shape)
    raise AssertionError(f'{tensor.name} has shape {array.shape}, expected {shape}')


def _tensor_type_name(tensor):
    return getattr(tensor.tensor_type,'name',str(tensor.tensor_type)).upper()


@pytest.fixture()
def exported_tiny_gguf(tmp_path):
    corpus=tmp_path/'corpus.txt'
    corpus.write_text(('Xin chao Nano export test. This corpus trains a tiny tokenizer.\n')*96,encoding='utf8')
    prefix=tmp_path/'sp'/'tok'
    train(corpus,prefix,vocab_size=320)
    tokenizer_path=str(prefix)+'.model'
    tok=Tokenizer(tokenizer_path)
    cfg=Config(vocab_size=tok.vocab_size,dim=64,layers=2,heads=4,kv_heads=2,ffn_dim=128,context=32)
    torch.manual_seed(1234)
    model=AchiticLM(cfg)
    state={name:value.detach().clone() for name,value in model.state_dict().items()}
    ckpt=tmp_path/'model.pt'
    torch.save({'config':cfg.__dict__,'model':state},ckpt)
    out=tmp_path/'model.gguf'
    export_checkpoint(ckpt,tokenizer_path,out)
    return cfg,tok,tokenizer_path,state,gguf.GGUFReader(str(out))


def test_export_preserves_adjacent_pair_qk_weights_without_permutation(exported_tiny_gguf):
    _,_,_,state,reader=exported_tiny_gguf
    tensors=_tensor_by_name(reader)
    checks={
        'blocks.0.attn.q.weight':'blk.0.attn_q.weight',
        'blocks.0.attn.k.weight':'blk.0.attn_k.weight',
        'blocks.1.attn.q.weight':'blk.1.attn_q.weight',
        'blocks.1.attn.k.weight':'blk.1.attn_k.weight',
    }
    for src,dst in checks.items():
        expected=state[src].numpy().astype(np.float16)
        actual=_tensor_array(tensors[dst],expected.shape)
        np.testing.assert_array_equal(actual,expected)


def test_export_writes_1d_tensors_f32_and_2d_tensors_f16(exported_tiny_gguf):
    _,_,_,_,reader=exported_tiny_gguf
    for tensor in reader.tensors:
        array=np.asarray(tensor.data)
        type_name=_tensor_type_name(tensor)
        if array.ndim==1:
            assert 'F32' in type_name,tensor.name
            assert array.dtype==np.float32
        elif array.ndim==2:
            assert 'F16' in type_name,tensor.name
            assert array.dtype==np.float16
        else:
            raise AssertionError(f'unexpected tensor rank for {tensor.name}: {array.shape}')


def test_export_metadata_matches_config_and_tokenizer(exported_tiny_gguf):
    cfg,tok,_,_,reader=exported_tiny_gguf
    assert _field_value(reader,'llama.attention.head_count')==cfg.heads
    assert _field_value(reader,'llama.attention.head_count_kv')==cfg.kv_heads
    assert _field_value(reader,'llama.rope.freq_base')==pytest.approx(cfg.rope_theta)
    assert _field_value(reader,'llama.context_length')==cfg.context
    assert _field_value(reader,'llama.block_count')==cfg.layers
    assert _field_value(reader,'tokenizer.ggml.bos_token_id')==tok.bos_id
    assert _field_value(reader,'tokenizer.ggml.eos_token_id')==tok.eos_id
    assert _field_value(reader,'tokenizer.ggml.unknown_token_id')==tok.unk_id
    assert _field_value(reader,'tokenizer.ggml.padding_token_id')==tok.pad_id


def test_sentencepiece_token_types_keep_user_defined_and_byte_tokens(exported_tiny_gguf):
    _,tok,tokenizer_path,_,_=exported_tiny_gguf
    types=sentencepiece_token_types(tokenizer_path)
    assert types[tok.sp.piece_to_id('<|user|>')]==int(gguf.TokenType.USER_DEFINED)
    assert types[tok.sp.piece_to_id('<0x41>')]==int(gguf.TokenType.BYTE)
    assert types[tok.bos_id]==int(gguf.TokenType.CONTROL)
    assert types[tok.eos_id]==int(gguf.TokenType.CONTROL)
    assert types[tok.unk_id]==int(gguf.TokenType.UNKNOWN)


def test_rope_matches_independent_adjacent_pair_reference():
    rng=np.random.default_rng(123)
    x_np=rng.normal(size=(2,3,5,8)).astype(np.float32)
    theta=10000.0
    positions=np.arange(x_np.shape[-2],dtype=np.float32)
    inv=1.0/(theta**(np.arange(0,x_np.shape[-1],2,dtype=np.float32)/x_np.shape[-1]))
    phase=np.outer(positions,inv)
    cos=np.cos(phase)[None,None]
    sin=np.sin(phase)[None,None]
    even=x_np[...,::2]
    odd=x_np[...,1::2]
    expected=np.stack((even*cos-odd*sin,even*sin+odd*cos),axis=-1).reshape(x_np.shape)
    actual=rope(torch.from_numpy(x_np),theta).numpy()
    np.testing.assert_allclose(actual,expected,rtol=0,atol=1e-6)
