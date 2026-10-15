import bz2
import importlib.util
import json
from pathlib import Path


SCRIPT=Path(__file__).parents[1]/'scripts'/'prepare_viwiki.py'
SPEC=importlib.util.spec_from_file_location('prepare_viwiki',SCRIPT)
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_dump(path):
    xml='''<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/">
<page><title>Học máy</title><ns>0</ns><revision><text>Học máy là một lĩnh vực nghiên cứu giúp máy tính học từ dữ liệu sạch. Dữ liệu sạch giúp mô hình hoạt động ổn định trong nhiều thử nghiệm khác nhau.</text></revision></page>
<page><title>Riêng tư</title><ns>0</ns><revision><text>Địa chỉ test@example.com không được giữ trong tập dữ liệu huấn luyện công khai.</text></revision></page>
<page><title>Lặp</title><ns>0</ns><revision><text>Dữ liệu sạch giúp mô hình hoạt động ổn định trong nhiều thử nghiệm khác nhau.</text></revision></page>
<page><title>Chuyển hướng</title><ns>0</ns><redirect title="Học máy"/><revision><text>#REDIRECT [[Học máy]]</text></revision></page>
<page><title>Thảo luận</title><ns>1</ns><revision><text>Đây là một câu tiếng Việt đủ dài nhưng không thuộc không gian bài viết chính.</text></revision></page>
<page><title>Đánh giá</title><ns>0</ns><revision><text>Dữ liệu sạch rất quan trọng khi huấn luyện mô hình ngôn ngữ trong thực tế.</text></revision></page>
</mediawiki>'''
    with bz2.open(path,'wb') as dest:dest.write(xml.encode('utf8'))


def test_build_corpus_filters_privacy_duplicates_namespaces_and_prompts(tmp_path):
    dump=tmp_path/'sample.xml.bz2';write_dump(dump)
    prompts=tmp_path/'prompts.jsonl'
    prompts.write_text(json.dumps({'id':'held-out','prompt':'Dữ liệu sạch rất quan trọng'},ensure_ascii=False)+'\n',encoding='utf8')
    args=type('Args',(),{
        'input':str(dump),'train_out':str(tmp_path/'train.txt'),'eval_out':str(tmp_path/'eval.txt'),
        'report':str(tmp_path/'report.json'),'source_url':'https://example.invalid/sample.xml.bz2',
        'snapshot_date':'2026-10-01','expected_md5':None,'prompts':str(prompts),'max_sentences':10,
        'eval_ratio':0.5,'seed':'test-seed','near_duplicate_hamming':0,
    })()

    report=MODULE.build_corpus(args)
    combined=(tmp_path/'train.txt').read_text(encoding='utf8')+(tmp_path/'eval.txt').read_text(encoding='utf8')

    assert 'test@example.com' not in combined
    assert combined.count('Dữ liệu sạch giúp mô hình hoạt động ổn định')==1
    assert 'Dữ liệu sạch rất quan trọng' not in combined
    assert report['counts']['privacy_email_rejected']==1
    assert report['counts']['exact_or_normalized_duplicate']==1
    assert report['counts']['fixed_prompt_contamination']==1
    assert report['counts']['redirect']==1
    assert report['counts']['non_main_namespace']==1
    assert report['contamination']['post_split_matches']==0


def test_expected_md5_is_enforced(tmp_path):
    dump=tmp_path/'sample.xml.bz2';write_dump(dump)
    args=type('Args',(),{
        'input':str(dump),'train_out':str(tmp_path/'train.txt'),'eval_out':str(tmp_path/'eval.txt'),
        'report':str(tmp_path/'report.json'),'source_url':'https://example.invalid/sample.xml.bz2',
        'snapshot_date':'2026-10-01','expected_md5':'0'*32,'prompts':None,'max_sentences':10,
        'eval_ratio':0.5,'seed':'test-seed','near_duplicate_hamming':0,
    })()

    try:
        MODULE.build_corpus(args)
    except ValueError as exc:
        assert 'source MD5 mismatch' in str(exc)
    else:
        raise AssertionError('expected checksum mismatch')
