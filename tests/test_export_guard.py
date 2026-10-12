from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]


def _read(path):
    return (ROOT/path).read_text(encoding='utf8')


def test_readme_marks_export_experimental_until_llamacpp_generation():
    text=_read('README.md')
    assert 'GGUF export / quantization (experimental)' in text
    assert 'load-and-generate' in text
    assert 'have not been verified' in text
    assert 'not a guarantee of GGUF compatibility' in text


def test_architecture_requires_tokenizer_parity_and_llamacpp_load_generate():
    text=_read('docs/ARCHITECTURE.md')
    assert 'load-and-generate' in text
    assert 'tokenizer parity must test BOS/EOS/UNK/PAD IDs' in text
    assert 'generated text before publishing' in text


def test_roadmap_and_phase6_require_load_and_generate_gate():
    roadmap=_read('docs/ROADMAP.md')
    phase6=_read('docs/pipeline/06_EXPORT_EDGE.md')
    assert 'pinned llama.cpp load-and-generate for each artifact' in roadmap
    assert 'runs/nano.pt' in phase6
    assert 'llama.cpp FP16 load-and-generate pass' in phase6
    assert 'Mỗi quantized artifact được test load-and-generate riêng' in phase6


def test_no_export_or_quant_verified_claim_without_guard_language():
    paths=[
        'README.md',
        'docs/ARCHITECTURE.md',
        'docs/ROADMAP.md',
        'docs/pipeline/06_EXPORT_EDGE.md',
        'scripts/export_gguf.py',
        'scripts/quantize.sh',
    ]
    unsafe_phrases=[
        'export is verified',
        'export verified',
        'gguf is verified',
        'gguf verified',
        'quantization is verified',
        'quantization verified',
        'quantized artifact is verified',
        'quantized artifacts are verified',
    ]
    for path in paths:
        text=_read(path).lower()
        for phrase in unsafe_phrases:
            assert phrase not in text, f'{path} contains unsafe export claim: {phrase}'
