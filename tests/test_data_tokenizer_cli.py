import json

import numpy as np
import pytest
import torch

from achitic.cli import ensure_tokenizer_matches_config
from achitic.data import TokenDataset,clean,encode_corpus,prepare
from achitic.model import Config
from achitic.tokenizer import Tokenizer,train


def test_clean_normalizes_nfc_removes_nul_and_collapses_spaces():
    assert clean('Cafe\u0301\x00\t  ngon  ')=='Café ngon'


def test_prepare_filters_short_rows_and_exact_deduplicates(tmp_path):
    source=tmp_path/'raw.jsonl'
    out=tmp_path/'clean.txt'
    kept='Đây là một dòng đủ dài để giữ lại trong tập dữ liệu thử nghiệm.'
    other='Một dòng văn bản khác cũng đủ dài để kiểm tra đường raw text.'
    source.write_text('\n'.join([
        json.dumps({'text':'ngắn'},ensure_ascii=False),
        json.dumps({'text':kept},ensure_ascii=False),
        json.dumps({'text':kept},ensure_ascii=False),
        other,
        other,
    ]),encoding='utf8')

    assert prepare([source],out,min_chars=20)==2
    assert out.read_text(encoding='utf8').splitlines()==[kept,other]


def test_token_dataset_shapes_and_not_enough_tokens(tmp_path):
    data=tmp_path/'tokens.bin'
    np.arange(11,dtype=np.int32).tofile(data)
    ds=TokenDataset(data,context=4)
    assert len(ds)==2
    x,y=ds[1]
    assert x.shape==(4,)
    assert y.shape==(4,)
    assert x.dtype==torch.int64
    assert y.dtype==torch.int64
    assert x.tolist()==[4,5,6,7]
    assert y.tolist()==[5,6,7,8]

    short=tmp_path/'short.bin'
    np.arange(4,dtype=np.int32).tofile(short)
    with pytest.raises(ValueError,match='not enough tokens'):
        TokenDataset(short,context=4)


def test_tokenizer_train_load_special_ids_and_encode_decode(tmp_path):
    corpus=tmp_path/'corpus.txt'
    corpus.write_text(('Xin chào mô hình Nano. Đây là corpus kiểm thử tokenizer.\n')*80,encoding='utf8')
    prefix=tmp_path/'sp'/'nano'

    train(corpus,prefix,vocab_size=320)
    tok=Tokenizer(str(prefix)+'.model')

    assert tok.unk_id==0
    assert tok.bos_id==1
    assert tok.eos_id==2
    assert tok.pad_id==3
    assert tok.vocab_size==320
    ids=tok.encode('Xin chào Nano',add_bos=True,add_eos=True)
    assert ids[0]==1
    assert ids[-1]==2
    assert 'Nano' in tok.decode(ids)

    encoded=tmp_path/'encoded.bin'
    assert encode_corpus(tok,corpus,encoded)>0
    assert np.memmap(encoded,dtype=np.int32,mode='r').shape[0]>0


def test_cli_tokenizer_config_mismatch_fails_clearly():
    class FakeTokenizer:
        vocab_size=320

    cfg=Config(vocab_size=8000)
    with pytest.raises(ValueError,match='tokenizer vocab size 320 does not match checkpoint config vocab_size 8000'):
        ensure_tokenizer_matches_config(FakeTokenizer(),cfg)
