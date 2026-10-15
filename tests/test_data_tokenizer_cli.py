import json
import subprocess
import sys
import tracemalloc
from pathlib import Path

import numpy as np
import pytest
import torch

from achitic.cli import ensure_tokenizer_matches_config
from achitic.data import TokenDataset,clean,encode_corpus,prepare,token_packing_report
from achitic.model import Config
from achitic.tokenizer import Tokenizer,tokenizer_stats,train


COUNT_KEYS=['normal','user_defined','reserved','byte','control','unknown','vocab_size','reserved_ratio']


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


def test_prepare_auto_keeps_json_scalars_and_non_text_objects(tmp_path):
    source=tmp_path/'mixed.txt'
    out=tmp_path/'clean.txt'
    raw='Một dòng văn bản thường đủ dài để giữ lại trong corpus.'
    json_string='Một chuỗi JSON hợp lệ nhưng vẫn phải giữ như văn bản thô.'
    json_array='Một mảng JSON hợp lệ nhưng không phải JSONL object.'
    jsonl='Dòng JSONL đúng định dạng có trường text để bóc ra.'
    missing='Đối tượng JSON thiếu text cũng được giữ nguyên ở chế độ auto.'
    source.write_text('\n'.join([
        raw,
        '2026',
        json.dumps(json_string,ensure_ascii=False),
        json.dumps([json_array],ensure_ascii=False),
        json.dumps({'text':jsonl},ensure_ascii=False),
        json.dumps({'body':missing},ensure_ascii=False),
    ]),encoding='utf8')

    stats=prepare([source],out,min_chars=20,input_format='auto',return_stats=True)

    assert stats['documents']==5
    assert stats['input_lines']==6
    assert stats['skipped_short']==1
    assert stats['skipped_jsonl_invalid_type']==0
    assert out.read_text(encoding='utf8').splitlines()==[
        raw,
        json.dumps(json_string,ensure_ascii=False),
        json.dumps([json_array],ensure_ascii=False),
        jsonl,
        json.dumps({'body':missing},ensure_ascii=False),
    ]


def test_prepare_text_format_preserves_jsonl_looking_lines(tmp_path):
    source=tmp_path/'text.txt'
    out=tmp_path/'clean.txt'
    line=json.dumps({'text':'Dòng này nhìn giống JSONL nhưng phải giữ raw ở format text.'},ensure_ascii=False)
    source.write_text(line+'\n',encoding='utf8')

    stats=prepare([source],out,min_chars=5,input_format='text',return_stats=True)

    assert stats['documents']==1
    assert out.read_text(encoding='utf8').strip()==line


def test_prepare_jsonl_format_reports_invalid_rows(tmp_path):
    source=tmp_path/'bad.jsonl'
    out=tmp_path/'clean.txt'
    kept='Dòng JSONL hợp lệ đủ dài để giữ lại.'
    source.write_text('\n'.join([
        json.dumps({'body':'thiếu trường text'},ensure_ascii=False),
        json.dumps({'text':123},ensure_ascii=False),
        json.dumps(['không phải object'],ensure_ascii=False),
        '{bad json',
        json.dumps({'text':'ngắn'},ensure_ascii=False),
        json.dumps({'text':kept},ensure_ascii=False),
    ]),encoding='utf8')

    stats=prepare([source],out,min_chars=10,input_format='jsonl',return_stats=True)

    assert stats['documents']==1
    assert stats['skipped_jsonl_missing_text']==1
    assert stats['skipped_jsonl_invalid_text']==1
    assert stats['skipped_jsonl_invalid_type']==1
    assert stats['skipped_json_decode_error']==1
    assert stats['skipped_short']==1
    assert out.read_text(encoding='utf8').splitlines()==[kept]


def test_cli_prepare_supports_format_and_reports_stats(tmp_path):
    source=tmp_path/'cli.jsonl'
    out=tmp_path/'clean.txt'
    kept='Dòng JSONL hợp lệ cho CLI prepare.'
    source.write_text('\n'.join([
        json.dumps({'body':'thiếu text'},ensure_ascii=False),
        json.dumps({'text':kept},ensure_ascii=False),
    ]),encoding='utf8')

    passed=subprocess.run([
        sys.executable,'-m','achitic.cli','prepare',
        '--inputs',str(source),
        '--out',str(out),
        '--format','jsonl',
        '--min-chars','10',
    ],check=True,cwd='.',text=True,capture_output=True)

    lines=passed.stdout.strip().splitlines()
    assert lines[0]=='documents: 1'
    assert lines[1].startswith('prepare_stats: ')
    stats=json.loads(lines[1].split(': ',1)[1])
    assert stats['documents']==1
    assert stats['skipped_jsonl_missing_text']==1
    assert out.read_text(encoding='utf8').splitlines()==[kept]


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


def test_token_dataset_stride_creates_overlapping_windows(tmp_path):
    data=tmp_path/'tokens.bin'
    np.arange(11,dtype=np.int32).tofile(data)
    ds=TokenDataset(data,context=4,stride=2)

    assert len(ds)==4
    x,y=ds[1]
    assert x.tolist()==[2,3,4,5]
    assert y.tolist()==[3,4,5,6]

    with pytest.raises(ValueError,match='stride must be >= 1'):
        TokenDataset(data,context=4,stride=0)


def test_token_packing_report_matches_token_dataset_chunking(tmp_path):
    data=tmp_path/'tokens.bin'
    np.arange(14,dtype=np.int32).tofile(data)

    report=token_packing_report(data,context=4)
    ds=TokenDataset(data,context=4)

    assert report['total_tokens']==14
    assert report['target_tokens']==13
    assert report['stride']==4
    assert report['windows']==len(ds)==3
    assert report['used_target_tokens']==12
    assert report['tokens_per_epoch']==12
    assert report['wasted_target_tokens']==1
    assert report['waste_ratio']==pytest.approx(1/13)
    assert report['max_possible_waste_tokens']==3
    assert report['overlap_tokens_per_window']==0
    assert report['packing_strategy']=='contiguous_fixed_context_chunks'


def test_token_packing_report_stride_counts_overlapping_windows(tmp_path):
    data=tmp_path/'tokens.bin'
    np.arange(14,dtype=np.int32).tofile(data)

    report=token_packing_report(data,context=4,stride=2)

    assert report['target_tokens']==13
    assert report['stride']==2
    assert report['windows']==5
    assert report['used_target_tokens']==12
    assert report['tokens_per_epoch']==20
    assert report['wasted_target_tokens']==1
    assert report['overlap_tokens_per_window']==2
    assert report['packing_strategy']=='strided_fixed_context_windows'


def test_token_packing_report_rejects_invalid_or_short_inputs(tmp_path):
    data=tmp_path/'short.bin'
    np.arange(4,dtype=np.int32).tofile(data)

    with pytest.raises(ValueError,match='context must be >= 1'):
        token_packing_report(data,context=0)
    with pytest.raises(ValueError,match='stride must be >= 1'):
        token_packing_report(data,context=4,stride=0)
    with pytest.raises(ValueError,match='not enough tokens'):
        token_packing_report(data,context=4)


def test_tokenizer_train_load_special_ids_and_encode_decode(tmp_path):
    corpus=tmp_path/'corpus.txt'
    corpus.write_text(('Xin chào mô hình Nano. Đây là corpus kiểm thử tokenizer.\n')*80,encoding='utf8')
    prefix=tmp_path/'sp'/'nano'

    stats=train(corpus,prefix,vocab_size=320,input_sentence_size=1000,
      shuffle_input_sentence=False,num_threads=1)
    tok=Tokenizer(str(prefix)+'.model')

    assert sum(stats[key] for key in ['normal','user_defined','reserved','byte','control','unknown'])==stats['vocab_size']
    assert stats['reserved_ratio']<=0.05
    assert stats['input_sentence_size']==1000
    assert stats['shuffle_input_sentence'] is False
    assert stats['num_threads']==1
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


def test_encode_corpus_streaming_matches_reference_bytes(tmp_path):
    corpus=tmp_path/'corpus.txt'
    corpus.write_text('\n'.join(f'Dòng kiểm thử encode streaming số {i}.' for i in range(40)),encoding='utf8')
    prefix=tmp_path/'sp'/'nano'
    train(corpus,prefix,vocab_size=320,input_sentence_size=1000,num_threads=1)
    tok=Tokenizer(str(prefix)+'.model')

    reference_ids=[]
    for line in corpus.read_text(encoding='utf8').splitlines(True):
        reference_ids.extend(tok.encode(line,add_bos=True,add_eos=True))
    reference=tmp_path/'reference.bin'
    np.asarray(reference_ids,dtype=np.int32).tofile(reference)

    streamed=tmp_path/'streamed.bin'
    stats=encode_corpus(tok,corpus,streamed,chunk_tokens=17,return_stats=True)

    assert stats['tokens']==len(reference_ids)
    assert stats['lines']==40
    assert stats['chunks']>1
    assert stats['bytes_written']==len(reference_ids)*4
    assert streamed.read_bytes()==reference.read_bytes()


def test_encode_corpus_rejects_invalid_chunk_and_int32_vocab(tmp_path):
    corpus=tmp_path/'corpus.txt'
    corpus.write_text('Một dòng đủ dài cho kiểm thử encode.\n',encoding='utf8')

    class FakeTokenizer:
        vocab_size=2**31
        def encode(self,*args,**kwargs):
            return [1,2,3]

    with pytest.raises(ValueError,match='chunk_tokens must be >= 1'):
        encode_corpus(FakeTokenizer(),corpus,tmp_path/'bad.bin',chunk_tokens=0)
    with pytest.raises(ValueError,match='vocab size must be < 2\\*\\*31'):
        encode_corpus(FakeTokenizer(),corpus,tmp_path/'bad.bin')


def test_encode_corpus_large_synthetic_uses_bounded_memory(tmp_path):
    corpus=tmp_path/'large.txt'
    corpus.write_text(''.join(f'dòng tổng hợp {i}\n' for i in range(20_000)),encoding='utf8')

    class FakeTokenizer:
        vocab_size=128
        def encode(self,line,add_bos=False,add_eos=False):
            return ([1] if add_bos else [])+[4,5,6]+([2] if add_eos else [])

    out=tmp_path/'large.bin'
    tracemalloc.start()
    try:
        stats=encode_corpus(FakeTokenizer(),corpus,out,chunk_tokens=128,return_stats=True)
        _,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    assert stats['lines']==20_000
    assert stats['tokens']==100_000
    assert stats['chunks']>100
    assert out.stat().st_size==stats['bytes_written']==400_000
    assert peak<5_000_000


def test_cli_encode_reports_streaming_stats(tmp_path):
    corpus=tmp_path/'corpus.txt'
    corpus.write_text(('Xin chào mô hình Nano. Đây là corpus kiểm thử tokenizer.\n')*40,encoding='utf8')
    prefix=tmp_path/'sp'/'nano'
    train(corpus,prefix,vocab_size=320,input_sentence_size=1000,num_threads=1)
    out=tmp_path/'encoded.bin'

    passed=subprocess.run([
        sys.executable,'-m','achitic.cli','encode',
        '--input',str(corpus),
        '--tokenizer',str(prefix)+'.model',
        '--out',str(out),
        '--chunk-tokens','23',
    ],check=True,cwd='.',text=True,capture_output=True)

    lines=passed.stdout.strip().splitlines()
    assert lines[0].startswith('tokens: ')
    assert lines[1].startswith('encode_stats: ')
    stats=json.loads(lines[1].split(': ',1)[1])
    assert stats['tokens']==int(lines[0].split(': ',1)[1])
    assert stats['lines']==40
    assert stats['chunks']>1
    assert out.stat().st_size==stats['bytes_written']


def test_tokenizer_rejects_excess_reserved_padding_by_default(tmp_path):
    prefix=tmp_path/'sp'/'nano'
    corpus=Path('examples/corpus.txt')

    with pytest.raises(ValueError,match='corpus too small for requested tokenizer vocab'):
        train(corpus,prefix,vocab_size=8000)
    with pytest.raises(ValueError,match='vocab_size must be < 2\\*\\*31'):
        train(corpus,prefix,vocab_size=2**31)


def test_tokenizer_allows_explicit_reserved_padding_and_reports_stats(tmp_path):
    prefix=tmp_path/'sp'/'nano'
    stats=train(Path('examples/corpus.txt'),prefix,vocab_size=8000,allow_reserved_padding=True,
      input_sentence_size=1000,shuffle_input_sentence=False,num_threads=1)
    reread=tokenizer_stats(str(prefix)+'.model')

    assert {key:stats[key] for key in COUNT_KEYS}==reread
    assert stats['vocab_size']==8000
    assert stats['reserved_ratio']>0.05
    assert stats['reserved']>0
    assert stats['byte']==256
    assert stats['input_sentence_size']==1000
    assert stats['shuffle_input_sentence'] is False
    assert stats['num_threads']==1
    assert sum(stats[key] for key in ['normal','user_defined','reserved','byte','control','unknown'])==8000


def test_cli_tokenizer_requires_explicit_reserved_padding_for_smoke_corpus(tmp_path):
    fail_prefix=tmp_path/'fail'/'sp'
    ok_prefix=tmp_path/'ok'/'sp'

    failed=subprocess.run([
        sys.executable,'-m','achitic.cli','tokenizer',
        '--input','examples/corpus.txt',
        '--prefix',str(fail_prefix),
        '--vocab','8000',
    ],cwd='.',text=True,capture_output=True)
    assert failed.returncode!=0
    assert 'corpus too small for requested tokenizer vocab' in failed.stderr

    passed=subprocess.run([
        sys.executable,'-m','achitic.cli','tokenizer',
        '--input','examples/corpus.txt',
        '--prefix',str(ok_prefix),
        '--vocab','8000',
        '--allow-reserved-padding',
        '--input-sentence-size','1000',
        '--num-threads','1',
        '--no-shuffle-input-sentence',
    ],check=True,cwd='.',text=True,capture_output=True)
    stats=json.loads(passed.stdout)
    assert stats['vocab_size']==8000
    assert stats['reserved_ratio']>0.05
    assert stats['input_sentence_size']==1000
    assert stats['shuffle_input_sentence'] is False
    assert stats['num_threads']==1
    assert sum(stats[key] for key in ['normal','user_defined','reserved','byte','control','unknown'])==8000


def test_split_val_script_is_deterministic(tmp_path):
    source=tmp_path/'source.txt'
    source.write_text(''.join(f'dòng {i}\n' for i in range(50)),encoding='utf8')
    train_a=tmp_path/'a'/'train.txt'
    val_a=tmp_path/'a'/'val.txt'
    train_b=tmp_path/'b'/'train.txt'
    val_b=tmp_path/'b'/'val.txt'

    first=subprocess.run([
        sys.executable,'scripts/split_val.py',
        '--input',str(source),
        '--train-out',str(train_a),
        '--val-out',str(val_a),
        '--val-ratio','0.2',
        '--seed','achitic-nano-x',
    ],check=True,cwd='.',text=True,capture_output=True)
    second=subprocess.run([
        sys.executable,'scripts/split_val.py',
        '--input',str(source),
        '--train-out',str(train_b),
        '--val-out',str(val_b),
        '--val-ratio','0.2',
        '--seed','achitic-nano-x',
    ],check=True,cwd='.',text=True,capture_output=True)

    first_stats=json.loads(first.stdout)
    second_stats=json.loads(second.stdout)
    assert first_stats['total_lines']==50
    assert first_stats['train_lines']+first_stats['val_lines']==50
    assert second_stats['train_lines']==first_stats['train_lines']
    assert second_stats['val_lines']==first_stats['val_lines']
    assert train_a.read_text(encoding='utf8')==train_b.read_text(encoding='utf8')
    assert val_a.read_text(encoding='utf8')==val_b.read_text(encoding='utf8')


def test_cli_tokenizer_config_mismatch_fails_clearly():
    class FakeTokenizer:
        vocab_size=320

    cfg=Config(vocab_size=8000)
    with pytest.raises(ValueError,match='tokenizer vocab size 320 does not match checkpoint config vocab_size 8000'):
        ensure_tokenizer_matches_config(FakeTokenizer(),cfg)
