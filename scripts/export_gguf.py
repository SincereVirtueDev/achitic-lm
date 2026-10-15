"""Export compatible LLaMA-layout AchiticLM weights as FP16 GGUF.
Requires `pip install -e '.[export]'`. Validate with your pinned llama.cpp version.
"""
import argparse
from pathlib import Path

import torch
import gguf
from achitic.checkpoint import load_weights
from achitic.model import Config


def sentencepiece_token_types(tokenizer_path):
    from sentencepiece import sentencepiece_model_pb2

    proto=sentencepiece_model_pb2.ModelProto()
    proto.ParseFromString(Path(tokenizer_path).read_bytes())
    sp_type=sentencepiece_model_pb2.ModelProto.SentencePiece
    return [
        {
            sp_type.NORMAL:int(gguf.TokenType.NORMAL),
            sp_type.UNKNOWN:int(gguf.TokenType.UNKNOWN),
            sp_type.CONTROL:int(gguf.TokenType.CONTROL),
            sp_type.USER_DEFINED:int(gguf.TokenType.USER_DEFINED),
            sp_type.UNUSED:int(gguf.TokenType.UNUSED),
            sp_type.BYTE:int(gguf.TokenType.BYTE),
        }[piece.type]
        for piece in proto.pieces
    ]


def tensor_mapping(c):
    mapping={'embed.weight':'token_embd.weight','norm.weight':'output_norm.weight'}
    block_map={
        'an.weight':'attn_norm.weight',
        'fn.weight':'ffn_norm.weight',
        'attn.q.weight':'attn_q.weight',
        'attn.k.weight':'attn_k.weight',
        'attn.v.weight':'attn_v.weight',
        'attn.o.weight':'attn_output.weight',
        'gate.weight':'ffn_gate.weight',
        'up.weight':'ffn_up.weight',
        'down.weight':'ffn_down.weight',
    }
    for i in range(c.layers):
        pre=f'blocks.{i}.';dst=f'blk.{i}.'
        for src,target in block_map.items():
            mapping[pre+src]=dst+target
    return mapping


def export_checkpoint(checkpoint,tokenizer,out,trust_checkpoint=False):
    from achitic.tokenizer import Tokenizer

    ck=load_weights(checkpoint,map_location='cpu',trust_checkpoint=trust_checkpoint)
    c=Config(**ck['config'])
    tok=Tokenizer(tokenizer)
    if tok.vocab_size!=c.vocab_size:
        raise ValueError(f'tokenizer vocab size {tok.vocab_size} does not match checkpoint config vocab_size {c.vocab_size}')

    w=gguf.GGUFWriter(out,'llama')
    w.add_name('AchiticLM')
    w.add_context_length(c.context)
    w.add_embedding_length(c.dim)
    w.add_block_count(c.layers)
    w.add_feed_forward_length(c.ffn_dim)
    w.add_head_count(c.heads)
    w.add_head_count_kv(c.kv_heads)
    w.add_rope_freq_base(c.rope_theta)
    w.add_layer_norm_rms_eps(1e-6)

    sp=tok.sp
    tokens=[sp.id_to_piece(i).encode('utf8') for i in range(sp.vocab_size())]
    scores=[float(sp.get_score(i)) for i in range(sp.vocab_size())]
    types=sentencepiece_token_types(tokenizer)
    if len(types)!=sp.vocab_size():
        raise ValueError(f'tokenizer proto has {len(types)} pieces, processor has {sp.vocab_size()}')
    w.add_tokenizer_model('llama')
    w.add_token_list(tokens)
    w.add_token_scores(scores)
    w.add_token_types(types)
    w.add_bos_token_id(sp.bos_id())
    w.add_eos_token_id(sp.eos_id())
    w.add_unk_token_id(sp.unk_id())
    w.add_pad_token_id(sp.pad_id())

    for src,dst in tensor_mapping(c).items():
        tensor=ck['model'][src].detach().float().cpu()
        # No Q/K permutation: Achitic RoPE rotates adjacent pairs, matching llama.cpp LLAMA_ROPE_TYPE_NORM.
        array=(tensor if tensor.ndim==1 else tensor.half()).contiguous().numpy()
        w.add_tensor(dst,array)
    w.write_header_to_file()
    w.write_kv_data_to_file()
    w.write_tensors_to_file()
    w.close()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',required=True)
    p.add_argument('--tokenizer',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--trust-checkpoint',action='store_true')
    a=p.parse_args()
    export_checkpoint(a.checkpoint,a.tokenizer,a.out,trust_checkpoint=a.trust_checkpoint)
    print('Exported FP16 GGUF:',a.out)


if __name__=='__main__':main()
