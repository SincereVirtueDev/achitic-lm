"""Export compatible LLaMA-layout AchiticLM weights as FP16 GGUF.
Requires `pip install -e '.[export]'`. Validate with your pinned llama.cpp version.
"""
import argparse,json
from pathlib import Path
import numpy as np
import torch
import gguf
from achitic.model import Config

def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',required=True);p.add_argument('--tokenizer',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();from achitic.tokenizer import Tokenizer
    ck=torch.load(a.checkpoint,map_location='cpu',weights_only=False);c=Config(**ck['config']);tok=Tokenizer(a.tokenizer)
    assert tok.vocab_size==c.vocab_size
    w=gguf.GGUFWriter(a.out,'llama')
    w.add_name('AchiticLM');w.add_context_length(c.context);w.add_embedding_length(c.dim)
    w.add_block_count(c.layers);w.add_feed_forward_length(c.ffn_dim)
    w.add_head_count(c.heads);w.add_head_count_kv(c.kv_heads)
    w.add_rope_freq_base(c.rope_theta);w.add_layer_norm_rms_eps(1e-6)
    # SentencePiece tokens and scores, with tokenizer-specific token types.
    sp=tok.sp
    tokens=[sp.id_to_piece(i).encode('utf8') for i in range(sp.vocab_size())]
    scores=[float(sp.get_score(i)) for i in range(sp.vocab_size())]
    types=[int(sp.is_unknown(i))*2+int(sp.is_control(i))*3+int(sp.is_unused(i))*5+int(sp.is_byte(i))*6 or 1 for i in range(sp.vocab_size())]
    w.add_tokenizer_model('llama');w.add_token_list(tokens);w.add_token_scores(scores);w.add_token_types(types)
    w.add_bos_token_id(sp.bos_id());w.add_eos_token_id(sp.eos_id());w.add_unknown_token_id(sp.unk_id());w.add_padding_token_id(sp.pad_id())
    sd=ck['model'];mapping={'embed.weight':'token_embd.weight','norm.weight':'output_norm.weight'}
    for i in range(c.layers):
        pre=f'blocks.{i}.';dst=f'blk.{i}.'
        for src,target in {'an.weight':'attn_norm.weight','fn.weight':'ffn_norm.weight','attn.q.weight':'attn_q.weight','attn.k.weight':'attn_k.weight','attn.v.weight':'attn_v.weight','attn.o.weight':'attn_output.weight','gate.weight':'ffn_gate.weight','up.weight':'ffn_up.weight','down.weight':'ffn_down.weight'}.items():mapping[pre+src]=dst+target
    # llama.cpp uses split-half RoPE on Q/K; interleaved Achitic pairs require permutation.
    for src,dst in mapping.items():
        tensor=sd[src].detach().float()
        if src.endswith(('attn.q.weight','attn.k.weight')):
            heads=c.heads if 'attn.q.' in src else c.kv_heads
            tensor=tensor.reshape(heads,c.dim//c.heads//2,2,c.dim).transpose(1,2).reshape(-1,c.dim)
        w.add_tensor(dst,tensor.half().numpy())
    w.write_header_to_file();w.write_kv_data_to_file();w.write_tensors_to_file();w.close()
    print('Exported FP16 GGUF:',a.out)
if __name__=='__main__':main()
