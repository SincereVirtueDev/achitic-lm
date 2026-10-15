#!/usr/bin/env python3
"""Build a bounded, audited Vietnamese sentence corpus from a Wikimedia XML dump."""

from __future__ import annotations

import argparse
import bz2
import hashlib
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path


URL_RE=re.compile(r'https?://\S+|www\.\S+',re.IGNORECASE)
EMAIL_RE=re.compile(r'(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])')
PHONE_RE=re.compile(r'(?<!\d)(?:\+?84|0)(?:[ .-]?\d){8,10}(?!\d)')
COMMENT_RE=re.compile(r'<!--.*?-->',re.DOTALL)
REF_RE=re.compile(r'<ref\b[^>]*>.*?</ref\s*>|<ref\b[^>]*/\s*>',re.IGNORECASE|re.DOTALL)
TAG_BLOCK_RE=re.compile(r'<(?:gallery|math|code|syntaxhighlight|timeline)\b[^>]*>.*?</[^>]+>',re.IGNORECASE|re.DOTALL)
TAG_RE=re.compile(r'<[^>]+>')
TABLE_RE=re.compile(r'{\|.*?\|}',re.DOTALL)
EXTERNAL_LINK_RE=re.compile(r'\[(?:https?://\S+)(?:\s+([^\]]+))?\]',re.IGNORECASE)
INTERNAL_LINK_RE=re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
HEADING_RE=re.compile(r'^=+\s*(.*?)\s*=+$',re.MULTILINE)
SPACE_RE=re.compile(r'\s+')
SENTENCE_SPLIT_RE=re.compile(r'(?<=[.!?…])\s+|[\r\n]+')
WORD_RE=re.compile(r"[0-9A-Za-zÀ-ỹĐđ]+",re.UNICODE)
TERMINATOR_RE=re.compile(r'[.!?…][\"”’\')\]]*$')
VIETNAMESE_CHARS=set('ăâđêôơưĂÂĐÊÔƠƯàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ')
VIETNAMESE_WORDS={
    'của','và','là','có','được','trong','một','những','các','với','cho','từ','đến','này','đã','theo','khi','tại','về','trên',
}
SKIP_PREFIXES=('thể loại:','tập tin:','file:','category:','bản mẫu:','template:')


def file_hashes(path: Path) -> dict[str,str]:
    md5=hashlib.md5(usedforsecurity=False);sha256=hashlib.sha256()
    with open(path,'rb') as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):
            md5.update(chunk);sha256.update(chunk)
    return {'md5':md5.hexdigest(),'sha256':sha256.hexdigest()}


def normalized_text(text: str) -> str:
    return ' '.join(word.lower() for word in WORD_RE.findall(text))


def prompt_contaminated(text: str,prompts: list[str]) -> bool:
    normalized=normalized_text(text)
    return any(prompt and (prompt in normalized or normalized in prompt) for prompt in prompts)


def strip_templates(text: str) -> str:
    previous=None
    while previous!=text:
        previous=text
        text=re.sub(r'{{[^{}]*}}',' ',text)
    return text


def strip_wikitext(text: str) -> str:
    text=COMMENT_RE.sub(' ',text)
    text=REF_RE.sub(' ',text)
    text=TAG_BLOCK_RE.sub(' ',text)
    text=TABLE_RE.sub(' ',text)
    text=strip_templates(text)
    text=EXTERNAL_LINK_RE.sub(lambda match:match.group(1) or ' ',text)
    def internal(match):
        target=(match.group(1) or '').strip()
        label=(match.group(2) or target).strip()
        if target.lower().startswith(SKIP_PREFIXES):return ' '
        return label
    text=INTERNAL_LINK_RE.sub(internal,text)
    text=HEADING_RE.sub(r'\1.',text)
    text=TAG_RE.sub(' ',text)
    text=text.replace("'''",'').replace("''",'')
    return html.unescape(text)


def clean_sentence(raw: str,counters: Counter) -> str | None:
    text=SPACE_RE.sub(' ',raw).strip(' \t-*#;:')
    if not text:return None
    if EMAIL_RE.search(text):
        counters['privacy_email_rejected']+=1;return None
    if PHONE_RE.search(text):
        counters['privacy_phone_rejected']+=1;return None
    if URL_RE.search(text):
        counters['privacy_url_stripped']+=1
        text=SPACE_RE.sub(' ',URL_RE.sub(' ',text)).strip()
    if len(text)<40:
        counters['too_short']+=1;return None
    if len(text)>320:
        counters['too_long']+=1;return None
    if not TERMINATOR_RE.search(text):
        counters['no_sentence_terminator']+=1;return None
    words=WORD_RE.findall(text)
    if len(words)<7:
        counters['too_few_words']+=1;return None
    letters=sum(char.isalpha() for char in text)
    if letters/max(len(text),1)<0.55:
        counters['low_letter_ratio']+=1;return None
    lower_words={word.lower() for word in words}
    accents=sum(char in VIETNAMESE_CHARS for char in text)
    if accents<2 and len(lower_words&VIETNAMESE_WORDS)<2:
        counters['language_filter']+=1;return None
    if '{{' in text or '}}' in text or '[[' in text or ']]' in text:
        counters['markup_residue']+=1;return None
    return text


def simhash(text: str) -> int:
    words=normalized_text(text).split()
    features=[' '.join(words[index:index+3]) for index in range(max(1,len(words)-2))]
    weights=[0]*64
    for feature in features:
        value=int.from_bytes(hashlib.blake2b(feature.encode('utf8'),digest_size=8).digest(),'big')
        for bit in range(64):weights[bit]+=1 if value&(1<<bit) else -1
    result=0
    for bit,weight in enumerate(weights):
        if weight>=0:result|=1<<bit
    return result


class NearDuplicateIndex:
    def __init__(self,max_hamming=3):
        self.max_hamming=max_hamming
        self.buckets=defaultdict(list)

    @staticmethod
    def keys(value):
        return [(part,(value>>(part*16))&0xffff) for part in range(4)]

    def add_if_new(self,text: str) -> bool:
        value=simhash(text);candidates=set()
        for key in self.keys(value):candidates.update(self.buckets[key])
        if any((value^candidate).bit_count()<=self.max_hamming for candidate in candidates):return False
        for key in self.keys(value):self.buckets[key].append(value)
        return True


def open_dump(path: Path):
    return bz2.open(path,'rb') if path.suffix=='.bz2' else open(path,'rb')


def child_text(element,name):
    for child in element.iter():
        if child.tag.rsplit('}',1)[-1]==name:return child.text or ''
    return ''


def stream_main_articles(path: Path,counters: Counter):
    with open_dump(path) as source:
        for _,element in ET.iterparse(source,events=('end',)):
            if element.tag.rsplit('}',1)[-1]!='page':continue
            counters['pages_seen']+=1
            namespace=child_text(element,'ns')
            title=child_text(element,'title')
            is_redirect=any(child.tag.rsplit('}',1)[-1]=='redirect' for child in element)
            if namespace!='0':counters['non_main_namespace']+=1
            elif is_redirect:counters['redirect']+=1
            else:
                text=child_text(element,'text')
                if text:
                    counters['articles_seen']+=1
                    yield title,text
                else:counters['empty_article']+=1
            element.clear()


def load_prompt_norms(path: Path | None) -> list[str]:
    if path is None:return []
    prompts=[]
    with open(path,encoding='utf8') as source:
        for line in source:
            if not line.strip() or line.lstrip().startswith('#'):continue
            prompts.append(normalized_text(json.loads(line)['prompt']))
    return prompts


def split_is_eval(text: str,seed: str,ratio: float) -> bool:
    digest=hashlib.sha256((seed+'\0'+text).encode('utf8')).digest()
    return int.from_bytes(digest,'big')/(1<<256)<ratio


def build_corpus(args) -> dict:
    source=Path(args.input);hashes=file_hashes(source)
    if args.expected_md5 and hashes['md5'].lower()!=args.expected_md5.lower():
        raise ValueError(f"source MD5 mismatch: expected {args.expected_md5}, got {hashes['md5']}")
    prompts=load_prompt_norms(Path(args.prompts) if args.prompts else None)
    counters=Counter();seen=set();near=NearDuplicateIndex(args.near_duplicate_hamming)
    train_path=Path(args.train_out);eval_path=Path(args.eval_out)
    train_path.parent.mkdir(parents=True,exist_ok=True);eval_path.parent.mkdir(parents=True,exist_ok=True)
    train_tmp=train_path.with_suffix(train_path.suffix+'.tmp');eval_tmp=eval_path.with_suffix(eval_path.suffix+'.tmp')
    accepted=0
    with open(train_tmp,'w',encoding='utf8') as train,open(eval_tmp,'w',encoding='utf8') as evaluate:
        for _,wikitext in stream_main_articles(source,counters):
            plain=strip_wikitext(wikitext)
            for raw in SENTENCE_SPLIT_RE.split(plain):
                counters['sentence_candidates']+=1
                sentence=clean_sentence(raw,counters)
                if sentence is None:continue
                normalized=normalized_text(sentence)
                digest=hashlib.sha256(normalized.encode('utf8')).digest()
                if digest in seen:
                    counters['exact_or_normalized_duplicate']+=1;continue
                if not near.add_if_new(sentence):
                    counters['near_duplicate']+=1;continue
                if prompt_contaminated(sentence,prompts):
                    counters['fixed_prompt_contamination']+=1;continue
                seen.add(digest)
                destination=evaluate if split_is_eval(sentence,args.seed,args.eval_ratio) else train
                destination.write(sentence+'\n')
                counters['eval_sentences' if destination is evaluate else 'train_sentences']+=1
                accepted+=1
                if accepted>=args.max_sentences:break
            if accepted>=args.max_sentences:break
    os.replace(train_tmp,train_path);os.replace(eval_tmp,eval_path)
    if not counters['train_sentences'] or not counters['eval_sentences']:
        raise ValueError('deterministic split produced an empty train or eval set')
    post_contamination=0
    for path in (train_path,eval_path):
        with open(path,encoding='utf8') as source_file:
            post_contamination+=sum(prompt_contaminated(line,prompts) for line in source_file)
    report={
        'schema_version':'1.0',
        'status':'LOCAL_CORPUS_PREPARED',
        'source':{
            'name':'Vietnamese Wikipedia article dump',
            'url':args.source_url,
            'snapshot_date':args.snapshot_date,
            'filename':source.name,
            'size_bytes':source.stat().st_size,
            **hashes,
            'license':'CC BY-SA 4.0 and GFDL; page-level exceptions may apply',
            'terms_url':'https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use',
            'attribution':'Vietnamese Wikipedia contributors',
        },
        'processing':{
            'max_sentences':args.max_sentences,
            'eval_ratio':args.eval_ratio,
            'seed':args.seed,
            'near_duplicate_hamming':args.near_duplicate_hamming,
            'fixed_prompts_file':Path(args.prompts).name if args.prompts else None,
            'raw_and_cleaned_data_committed':False,
        },
        'counts':dict(sorted(counters.items())),
        'privacy':{
            'method':'regex reject emails/phone-like strings and strip URLs before acceptance',
            'limitations':'Heuristic scan; it cannot prove that all personal data is absent.',
        },
        'contamination':{
            'method':'normalized prompt substring exclusion before split, followed by post-write scan',
            'post_split_matches':post_contamination,
        },
        'outputs':{
            'train_filename':train_path.name,
            'eval_filename':eval_path.name,
            'train_sha256':file_hashes(train_path)['sha256'],
            'eval_sha256':file_hashes(eval_path)['sha256'],
        },
    }
    report_path=Path(args.report);report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report


def parse_args():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True)
    parser.add_argument('--train-out',required=True)
    parser.add_argument('--eval-out',required=True)
    parser.add_argument('--report',required=True)
    parser.add_argument('--source-url',required=True)
    parser.add_argument('--snapshot-date',required=True)
    parser.add_argument('--expected-md5')
    parser.add_argument('--prompts')
    parser.add_argument('--max-sentences',type=int,default=100_000)
    parser.add_argument('--eval-ratio',type=float,default=0.02)
    parser.add_argument('--seed',default='achitic-nano-meaning-v0.2.0')
    parser.add_argument('--near-duplicate-hamming',type=int,default=3)
    args=parser.parse_args()
    if args.max_sentences<2:parser.error('--max-sentences must be >= 2')
    if not 0<args.eval_ratio<1:parser.error('--eval-ratio must be between 0 and 1')
    if not 0<=args.near_duplicate_hamming<=64:parser.error('--near-duplicate-hamming must be between 0 and 64')
    return args


def main():
    report=build_corpus(parse_args())
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))


if __name__=='__main__':main()
