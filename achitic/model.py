from dataclasses import dataclass
import math
import torch
from torch import nn
from torch.nn import functional as F

@dataclass
class Config:
    vocab_size: int = 8000
    dim: int = 512
    layers: int = 8
    heads: int = 8
    kv_heads: int = 2
    ffn_dim: int = 1408
    context: int = 512
    rope_theta: float = 10000.0

class RMSNorm(nn.Module):
    def __init__(self, d):
        super().__init__(); self.weight = nn.Parameter(torch.ones(d))
    def forward(self, x):
        return F.rms_norm(x, (x.shape[-1],), self.weight, eps=1e-6)

def rope(x, theta, offset=0):
    d = x.shape[-1]
    assert d % 2 == 0
    t = torch.arange(offset,offset+x.shape[-2], device=x.device, dtype=torch.float32)
    inv = 1.0 / (theta ** (torch.arange(0,d,2,device=x.device,dtype=torch.float32)/d))
    phase = torch.outer(t,inv)
    c,s = phase.cos()[None,None], phase.sin()[None,None]
    a,b = x.float()[...,::2],x.float()[...,1::2]
    return torch.stack((a*c-b*s,a*s+b*c),dim=-1).flatten(-2).to(x.dtype)

class Attention(nn.Module):
    def __init__(self,c):
        super().__init__()
        assert c.dim%c.heads==0 and c.heads%c.kv_heads==0
        self.h,self.kv,self.d,self.theta=c.heads,c.kv_heads,c.dim//c.heads,c.rope_theta
        self.q=nn.Linear(c.dim,c.heads*self.d,bias=False)
        self.k=nn.Linear(c.dim,c.kv_heads*self.d,bias=False)
        self.v=nn.Linear(c.dim,c.kv_heads*self.d,bias=False)
        self.o=nn.Linear(c.dim,c.dim,bias=False)
    def forward(self,x,cache=None,start_pos=0,use_cache=False):
        b,t,_=x.shape
        def split(y,h): return y.view(b,t,h,self.d).transpose(1,2)
        q=rope(split(self.q(x),self.h),self.theta,offset=start_pos)
        k=rope(split(self.k(x),self.kv),self.theta,offset=start_pos)
        v=split(self.v(x),self.kv)
        if cache is not None:
            ck,cv=cache
            k=torch.cat((ck,k),dim=2)
            v=torch.cat((cv,v),dim=2)
        new_cache=(k,v) if use_cache else None
        kk=k.repeat_interleave(self.h//self.kv,dim=1)
        vv=v.repeat_interleave(self.h//self.kv,dim=1)
        if cache is None:
            y=F.scaled_dot_product_attention(q,kk,vv,is_causal=True)
        else:
            key_pos=torch.arange(k.shape[-2],device=x.device)[None,:]
            query_pos=torch.arange(start_pos,start_pos+t,device=x.device)[:,None]
            mask=torch.zeros((t,k.shape[-2]),device=x.device,dtype=q.dtype)
            mask=mask.masked_fill(key_pos>query_pos,float('-inf'))
            y=F.scaled_dot_product_attention(q,kk,vv,attn_mask=mask[None,None],is_causal=False)
        out=self.o(y.transpose(1,2).contiguous().view(b,t,-1))
        return (out,new_cache) if use_cache else out

class Block(nn.Module):
    def __init__(self,c):
        super().__init__()
        self.an=RMSNorm(c.dim);self.attn=Attention(c)
        self.fn=RMSNorm(c.dim)
        self.gate=nn.Linear(c.dim,c.ffn_dim,bias=False)
        self.up=nn.Linear(c.dim,c.ffn_dim,bias=False)
        self.down=nn.Linear(c.ffn_dim,c.dim,bias=False)
    def forward(self,x,cache=None,start_pos=0,use_cache=False):
        if use_cache:
            attn,cache=self.attn(self.an(x),cache=cache,start_pos=start_pos,use_cache=True)
            x=x+attn
            z=self.fn(x)
            return x+self.down(F.silu(self.gate(z))*self.up(z)),cache
        x=x+self.attn(self.an(x)); z=self.fn(x)
        return x+self.down(F.silu(self.gate(z))*self.up(z))

class AchiticLM(nn.Module):
    def __init__(self,c):
        super().__init__();self.config=c
        self.embed=nn.Embedding(c.vocab_size,c.dim)
        self.blocks=nn.ModuleList(Block(c) for _ in range(c.layers))
        self.norm=RMSNorm(c.dim)
        self.head=nn.Linear(c.dim,c.vocab_size,bias=False)
        self.head.weight=self.embed.weight
        self.apply(self._init)
    @staticmethod
    def _init(m):
        if isinstance(m,(nn.Linear,nn.Embedding)): nn.init.normal_(m.weight,mean=0,std=0.02)
    def forward(self,ids,targets=None,mask=None):
        if ids.shape[1]>self.config.context: raise ValueError('context exceeded')
        x=self.embed(ids)
        for block in self.blocks:x=block(x)
        logits=self.head(self.norm(x))
        loss=None
        if targets is not None:
            loss=F.cross_entropy(logits.float().reshape(-1,logits.size(-1)),targets.reshape(-1),ignore_index=-100)
        return logits,loss
    def forward_cached(self,ids,cache=None,start_pos=0):
        if ids.shape[1]<1: raise ValueError('empty ids')
        if start_pos+ids.shape[1]>self.config.context: raise ValueError('context exceeded')
        if cache is not None:
            if len(cache)!=len(self.blocks): raise ValueError('cache layer count mismatch')
            if any(layer_cache[0].shape[2]!=start_pos for layer_cache in cache):
                raise ValueError('cache length/start_pos mismatch')
        x=self.embed(ids);new_cache=[]
        for i,block in enumerate(self.blocks):
            layer_cache=None if cache is None else cache[i]
            x,layer_cache=block(x,cache=layer_cache,start_pos=start_pos,use_cache=True)
            new_cache.append(layer_cache)
        return self.head(self.norm(x)),new_cache
    def _sample_next(self,scores,temperature,top_k):
        if temperature<=0:return scores.argmax(-1,keepdim=True)
        scores=scores/temperature
        if top_k>0:
            values,_=scores.topk(min(top_k,scores.size(-1)))
            scores=scores.masked_fill(scores<values[:,-1,None],float('-inf'))
        return torch.multinomial(F.softmax(scores,dim=-1),1)
    @torch.no_grad()
    def generate(self,ids,max_new_tokens=40,temperature=0.8,top_k=40,eos_id=None,use_cache=True,stop_ids=None):
        self.eval()
        stops=[]
        if eos_id is not None:stops.append(int(eos_id))
        if stop_ids is not None:
            if isinstance(stop_ids,int):stop_ids=[stop_ids]
            stops.extend(int(idx) for idx in stop_ids if idx is not None)
        stops=tuple(dict.fromkeys(stops))
        def should_stop(nxt):
            if not stops:return False
            stop_tensor=torch.tensor(stops,device=nxt.device,dtype=nxt.dtype)
            return bool((nxt[...,None]==stop_tensor).any(-1).all())
        if not use_cache:
            for _ in range(max_new_tokens):
                logits,_=self(ids[:,-self.config.context:]); scores=logits[:,-1,:].float()
                nxt=self._sample_next(scores,temperature,top_k)
                ids=torch.cat((ids,nxt),dim=1)
                if should_stop(nxt):break
            return ids
        window=ids[:,-self.config.context:]
        logits,cache=self.forward_cached(window)
        for _ in range(max_new_tokens):
            scores=logits[:,-1,:].float()
            nxt=self._sample_next(scores,temperature,top_k)
            ids=torch.cat((ids,nxt),dim=1)
            if should_stop(nxt):break
            if window.shape[1]>=self.config.context:
                window=ids[:,-self.config.context:]
                logits,cache=self.forward_cached(window)
            else:
                start_pos=window.shape[1]
                window=torch.cat((window,nxt),dim=1)
                logits,cache=self.forward_cached(nxt,cache=cache,start_pos=start_pos)
        return ids
