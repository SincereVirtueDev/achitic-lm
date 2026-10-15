import os
import subprocess
import sys

import pytest


def write_executable(path,body):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(body,encoding='utf8')
    path.chmod(0o755)


def test_verify_gguf_help_lists_required_inputs():
    result=subprocess.run(
        [sys.executable,'scripts/verify_gguf.py','--help'],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    assert '--checkpoint' in result.stdout
    assert '--tokenizer' in result.stdout
    assert '--gguf' in result.stdout
    assert '--llama-cpp-dir' in result.stdout


def test_verify_gguf_missing_llama_cpp_dir_fails_clearly(tmp_path):
    gguf=tmp_path/'fake.gguf'
    gguf.write_bytes(b'GGUF')
    result=subprocess.run(
        [
            sys.executable,'scripts/verify_gguf.py',
            '--checkpoint','missing.pt',
            '--tokenizer','missing.model',
            '--gguf',str(gguf),
            '--llama-cpp-dir',str(tmp_path/'missing-llama.cpp'),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode!=0
    assert 'llama.cpp directory not found' in (result.stdout+result.stderr)


def test_quantize_policy_detects_fallback_log(tmp_path):
    log=tmp_path/'quant.log'
    summary=tmp_path/'fallbacks.json'
    log.write_text(
        'llama_model_quantize_internal: blk.0.ffn_down.weight cannot use Q4_K_M; fallback to Q8_0\n',
        encoding='utf8',
    )
    result=subprocess.run(
        [
            sys.executable,'scripts/quantize_policy.py','check-fallback',
            '--log',str(log),
            '--summary',str(summary),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode!=0
    assert 'fallback' in result.stdout
    assert 'blk.0.ffn_down.weight' in summary.read_text(encoding='utf8')


def test_quantize_policy_rejects_failed_report(tmp_path):
    report=tmp_path/'verify.json'
    report.write_text(
        '{"status":"FAIL","normal":{"max_abs_delta":0.5,"top1_match":0.5}}\n',
        encoding='utf8',
    )
    result=subprocess.run(
        [
            sys.executable,'scripts/quantize_policy.py','check-report',
            '--report',str(report),
            '--max-delta','0.25',
            '--top1-min','0.90',
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode!=0
    assert '"passed": false' in result.stdout


def test_quantize_wrapper_runs_verifier_for_exact_quant_artifact(tmp_path):
    in_gguf=tmp_path/'model-f16.gguf'
    out_gguf=tmp_path/'model-q4.gguf'
    checkpoint=tmp_path/'nano.pt'
    tokenizer=tmp_path/'tokenizer.model'
    llama_dir=tmp_path/'llama.cpp'
    verifier=tmp_path/'fake_verify.py'
    in_gguf.write_bytes(b'GGUF')
    checkpoint.write_bytes(b'checkpoint')
    tokenizer.write_bytes(b'tokenizer')
    write_executable(
        llama_dir/'build'/'bin'/'llama-quantize',
        '#!/usr/bin/env bash\ncp "$1" "$2"\necho "quantized $3"\n',
    )
    write_executable(
        verifier,
        '''#!/usr/bin/env python3
import argparse,json
p=argparse.ArgumentParser()
p.add_argument('--checkpoint');p.add_argument('--tokenizer');p.add_argument('--gguf')
p.add_argument('--llama-cpp-dir');p.add_argument('--prompt');p.add_argument('--context')
p.add_argument('--generate-tokens');p.add_argument('--normal-max-delta')
p.add_argument('--normal-top1-min');p.add_argument('--skip-stress',action='store_true')
p.add_argument('--out',required=True)
a=p.parse_args()
payload={'status':'PASS','gguf':a.gguf,'normal':{'max_abs_delta':0.1,'top1_match':0.95},'generation':{'generated_token_ids':[1]}}
open(a.out,'w',encoding='utf8').write(json.dumps(payload)+'\\n')
print(json.dumps(payload))
''',
    )

    env={**os.environ,'LLAMA_CPP_DIR':str(llama_dir),'ACHITIC_VERIFY_GGUF':str(verifier),'PYTHON':sys.executable}
    result=subprocess.run(
        [
            'scripts/quantize.sh',str(in_gguf),str(out_gguf),'Q4_K_M',
            '--checkpoint',str(checkpoint),
            '--tokenizer',str(tokenizer),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    assert result.returncode==0,result.stdout+result.stderr
    assert out_gguf.read_bytes()==b'GGUF'
    assert (tmp_path/'model-q4.gguf.verify.json').exists()
    assert 'exact-artifact llama.cpp verification policy' in result.stdout


def test_quantize_wrapper_fails_on_fallback_unless_experimental(tmp_path):
    in_gguf=tmp_path/'model-f16.gguf'
    out_gguf=tmp_path/'model-q4.gguf'
    checkpoint=tmp_path/'nano.pt'
    tokenizer=tmp_path/'tokenizer.model'
    llama_dir=tmp_path/'llama.cpp'
    verifier=tmp_path/'fake_verify.py'
    in_gguf.write_bytes(b'GGUF')
    checkpoint.write_bytes(b'checkpoint')
    tokenizer.write_bytes(b'tokenizer')
    write_executable(
        llama_dir/'build'/'bin'/'llama-quantize',
        '#!/usr/bin/env bash\ncp "$1" "$2"\necho "blk.0.ffn_down.weight fallback to Q8_0"\n',
    )
    write_executable(
        verifier,
        '''#!/usr/bin/env python3
import argparse,json
p=argparse.ArgumentParser()
p.add_argument('--checkpoint');p.add_argument('--tokenizer');p.add_argument('--gguf')
p.add_argument('--llama-cpp-dir');p.add_argument('--prompt');p.add_argument('--context')
p.add_argument('--generate-tokens');p.add_argument('--normal-max-delta')
p.add_argument('--normal-top1-min');p.add_argument('--skip-stress',action='store_true')
p.add_argument('--out',required=True)
a=p.parse_args()
payload={'status':'PASS','normal':{'max_abs_delta':0.1,'top1_match':0.95},'generation':{'generated_token_ids':[1]}}
open(a.out,'w',encoding='utf8').write(json.dumps(payload)+'\\n')
print(json.dumps(payload))
''',
    )
    env={**os.environ,'LLAMA_CPP_DIR':str(llama_dir),'ACHITIC_VERIFY_GGUF':str(verifier),'PYTHON':sys.executable}

    result=subprocess.run(
        [
            'scripts/quantize.sh',str(in_gguf),str(out_gguf),'Q4_K_M',
            '--checkpoint',str(checkpoint),
            '--tokenizer',str(tokenizer),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    assert result.returncode!=0
    assert 'ffn_down.weight' in result.stdout
    assert 'failed policy' in result.stderr

    allowed=subprocess.run(
        [
            'scripts/quantize.sh',str(in_gguf),str(out_gguf),'Q4_K_M',
            '--checkpoint',str(checkpoint),
            '--tokenizer',str(tokenizer),
            '--allow-experimental',
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    assert allowed.returncode==0
    assert 'experimental only' in allowed.stderr


@pytest.mark.skipif(not os.environ.get('LLAMA_CPP_DIR'),reason='LLAMA_CPP_DIR not set')
def test_verify_gguf_integration_with_pinned_llama_cpp():
    pytest.importorskip('gguf')
    result=subprocess.run(
        [
            sys.executable,'scripts/verify_gguf.py',
            '--checkpoint','releases/nano/nano.pt',
            '--tokenizer','releases/nano/tokenizer.model',
            '--gguf','/tmp/achitic-nano-x.gguf',
            '--llama-cpp-dir',os.environ['LLAMA_CPP_DIR'],
            '--generate-tokens','4',
            '--max-input-tokens','16',
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode==0,result.stdout+result.stderr
