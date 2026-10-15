import torch
import pytest
from achitic.model import AchiticLM,Config,rope

def test_forward_backward_and_generation():
    c=Config(vocab_size=128,dim=64,layers=2,heads=4,kv_heads=2,ffn_dim=160,context=32)
    m=AchiticLM(c)
    assert m.head.weight is m.embed.weight
    x=torch.randint(0,128,(2,12));logits,loss=m(x,x)
    assert logits.shape==(2,12,128)
    loss.backward()
    assert m.embed.weight.grad is not None
    assert m.generate(x[:1,:3],3).shape==(1,6)
    assert m.generate(x[:1,:3],3,use_cache=False).shape==(1,6)

def test_causal():
    c=Config(vocab_size=128,dim=64,layers=2,heads=4,kv_heads=2,ffn_dim=160,context=32)
    m=AchiticLM(c).eval();x=torch.randint(0,128,(1,10));y=x.clone();y[0,-1]=(y[0,-1]+1)%128
    with torch.no_grad():a,_=m(x);b,_=m(y)
    assert torch.allclose(a[:,:-1],b[:,:-1],atol=1e-5)

def test_rope_preserves_shape_dtype_and_pair_norm():
    x=torch.randn(2,3,5,8)
    y=rope(x,10000.0)
    assert y.shape==x.shape
    assert y.dtype==x.dtype
    assert torch.allclose(y[:,:,0,:],x[:,:,0,:],atol=1e-6)
    x_pairs=x.float().reshape(*x.shape[:-1],-1,2)
    y_pairs=y.float().reshape(*y.shape[:-1],-1,2)
    assert torch.allclose(x_pairs.norm(dim=-1),y_pairs.norm(dim=-1),atol=1e-5)

def test_rope_offset_matches_full_sequence_slice():
    x=torch.randn(1,2,3,8)
    prefix=torch.randn(1,2,5,8)
    expected=rope(torch.cat((prefix,x),dim=-2),10000.0)[:,:,5:]
    actual=rope(x,10000.0,offset=5)
    assert torch.allclose(actual,expected,atol=1e-6)

def test_rope_preserves_low_precision_dtype_on_cpu():
    x=torch.randn(1,2,4,8).to(torch.bfloat16)
    y=rope(x,10000.0)
    assert y.shape==x.shape
    assert y.dtype==torch.bfloat16

def test_rope_rejects_odd_head_dim():
    with pytest.raises(AssertionError):
        rope(torch.zeros(1,1,2,3),10000.0)

def test_causal_prefix_is_invariant_to_future_suffix():
    c=Config(vocab_size=128,dim=64,layers=2,heads=4,kv_heads=2,ffn_dim=160,context=32)
    m=AchiticLM(c).eval()
    prefix=torch.randint(0,128,(1,6))
    suffix=torch.randint(0,128,(1,4))
    x=torch.cat((prefix,suffix),dim=1)
    y=torch.cat((prefix,(suffix+1)%128),dim=1)
    with torch.no_grad():a,_=m(x);b,_=m(y)
    assert torch.allclose(a[:,:prefix.shape[1]],b[:,:prefix.shape[1]],atol=1e-5)

def test_gqa_valid_config_uses_smaller_kv_projection_and_runs_forward():
    c=Config(vocab_size=96,dim=48,layers=1,heads=6,kv_heads=2,ffn_dim=96,context=16)
    m=AchiticLM(c)
    attn=m.blocks[0].attn
    assert attn.h==6
    assert attn.kv==2
    assert attn.d==8
    assert attn.q.out_features==48
    assert attn.k.out_features==16
    assert attn.v.out_features==16
    x=torch.randint(0,96,(2,7))
    with torch.no_grad():logits,_=m(x)
    assert logits.shape==(2,7,96)

def test_cached_prefill_logits_match_uncached_gqa_forward():
    c=Config(vocab_size=96,dim=48,layers=2,heads=6,kv_heads=2,ffn_dim=96,context=16)
    m=AchiticLM(c).eval()
    x=torch.randint(0,96,(2,9))
    with torch.no_grad():
        uncached,_=m(x)
        cached,cache=m.forward_cached(x)
    assert len(cache)==c.layers
    assert cache[0][0].shape==(2,c.kv_heads,9,c.dim//c.heads)
    assert torch.allclose(cached,uncached,atol=1e-5)


def test_cached_step_logits_match_uncached_prefix_logits():
    c=Config(vocab_size=96,dim=48,layers=2,heads=6,kv_heads=2,ffn_dim=96,context=16)
    m=AchiticLM(c).eval()
    x=torch.randint(0,96,(1,10))
    cache=None
    with torch.no_grad():
        for pos in range(x.shape[1]):
            cached,cache=m.forward_cached(x[:,pos:pos+1],cache=cache,start_pos=pos)
            uncached,_=m(x[:,:pos+1])
            assert torch.allclose(cached[:,-1],uncached[:,-1],atol=1e-5)


def test_cached_and_uncached_greedy_generation_match():
    c=Config(vocab_size=96,dim=48,layers=2,heads=6,kv_heads=2,ffn_dim=96,context=16)
    m=AchiticLM(c).eval()
    x=torch.randint(0,96,(1,6))
    with torch.no_grad():
        cached=m.generate(x,max_new_tokens=8,temperature=0,use_cache=True)
        uncached=m.generate(x,max_new_tokens=8,temperature=0,use_cache=False)
    assert torch.equal(cached,uncached)


def test_cached_generation_matches_uncached_near_context_window():
    c=Config(vocab_size=96,dim=48,layers=2,heads=6,kv_heads=2,ffn_dim=96,context=8)
    m=AchiticLM(c).eval()
    x=torch.randint(0,96,(1,7))
    with torch.no_grad():
        cached=m.generate(x,max_new_tokens=4,temperature=0,use_cache=True)
        uncached=m.generate(x,max_new_tokens=4,temperature=0,use_cache=False)
    assert torch.equal(cached,uncached)


def test_generation_stops_on_custom_stop_id():
    c=Config(vocab_size=96,dim=48,layers=1,heads=6,kv_heads=2,ffn_dim=96,context=16)
    m=AchiticLM(c).eval()
    x=torch.randint(0,96,(1,4))

    def sample_stop(scores,temperature,top_k):
        return torch.full((scores.shape[0],1),7,dtype=torch.long,device=scores.device)

    m._sample_next=sample_stop
    with torch.no_grad():
        cached=m.generate(x,max_new_tokens=5,stop_ids=[7],use_cache=True)
        uncached=m.generate(x,max_new_tokens=5,stop_ids=[7],use_cache=False)

    assert cached.shape[1]==x.shape[1]+1
    assert uncached.shape[1]==x.shape[1]+1
    assert int(cached[0,-1])==7
    assert int(uncached[0,-1])==7


def test_forward_cached_rejects_context_exceeded():
    c=Config(vocab_size=96,dim=48,layers=1,heads=6,kv_heads=2,ffn_dim=96,context=8)
    m=AchiticLM(c).eval()
    with pytest.raises(ValueError,match='context exceeded'):
        m.forward_cached(torch.randint(0,96,(1,2)),start_pos=7)


def test_forward_cached_rejects_start_pos_cache_mismatch():
    c=Config(vocab_size=96,dim=48,layers=1,heads=6,kv_heads=2,ffn_dim=96,context=8)
    m=AchiticLM(c).eval()
    x=torch.randint(0,96,(1,3))
    with torch.no_grad():
        _,cache=m.forward_cached(x)
        with pytest.raises(ValueError,match='cache length/start_pos mismatch'):
            m.forward_cached(torch.randint(0,96,(1,1)),cache=cache,start_pos=1)

def test_gqa_invalid_kv_heads_raise():
    with pytest.raises(AssertionError):
        AchiticLM(Config(vocab_size=96,dim=48,layers=1,heads=6,kv_heads=4,ffn_dim=96,context=16))
