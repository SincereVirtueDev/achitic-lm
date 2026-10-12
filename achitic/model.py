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

def rope(x, theta):
    d = x.shape[-1]
    assert d % 2 == 0
    t = torch.arange(x.shape[-2], device=x.device, dtype=torch.float32)
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
    def forward(self,x):
        b,t,_=x.shape
        def split(y,h): return y.view(b,t,h,self.d).transpose(1,2)
        q=rope(split(self.q(x),self.h),self.theta)
        k=rope(split(self.k(x),self.kv),self.theta)
        v=split(self.v(x),self.kv)
        k=k.repeat_interleave(self.h//self.kv,dim=1)
        v=v.repeat_interleave(self.h//self.kv,dim=1)
        y=F.scaled_dot_product_attention(q,k,v,is_causal=True)
        return self.o(y.transpose(1,2).contiguous().view(b,t,-1))

class Block(nn.Module):
    def __init__(self,c):
        super().__init__()
        self.an=RMSNorm(c.dim);self.attn=Attention(c)
        self.fn=RMSNorm(c.dim)
        self.gate=nn.Linear(c.dim,c.ffn_dim,bias=False)
        self.up=nn.Linear(c.dim,c.ffn_dim,bias=False)
        self.down=nn.Linear(c.ffn_dim,c.dim,bias=False)
    def forward(self,x):
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
    @torch.no_grad()
    def generate(self,ids,max_new_tokens=40,temperature=0.8,top_k=40,eos_id=None):
        self.eval()
        for _ in range(max_new_tokens):
            logits,_=self(ids[:,-self.config.context:]); scores=logits[:,-1,:].float()
            if temperature<=0: nxt=scores.argmax(-1,keepdim=True)
            else:
                scores=scores/temperature
                if top_k>0:
                    values,_=scores.topk(min(top_k,scores.size(-1)))
                    scores=scores.masked_fill(scores<values[:,-1,None],float('-inf'))
                nxt=torch.multinomial(F.softmax(scores,dim=-1),1)
            ids=torch.cat((ids,nxt),dim=1)
            if eos_id is not None and bool((nxt==eos_id).all()):break
        return ids
