# AchiticLM Nano Model Card

Status: READY_FOR_GITHUB_PUBLICATION

## Model Summary

AchiticLM Nano is a scratch-initialized decoder-only Transformer checkpoint for pipeline smoke testing. It is not pretrained, not instruction-tuned, and not suitable for real chat, factual QA or production use.

- Parameters: `4,999,424`
- Vocabulary size: `8000`
- Context length: `128`
- Training steps: `3`

## Architecture

AchiticLM Core:

- Decoder-only Transformer
- GQA
- RoPE
- RMSNorm
- SwiGLU
- Tied embedding/output weight

The same architecture is used for Nano, Tiny and larger ladder targets; size changes are config changes, not model forks.

## Training Data

Training data source: `examples/corpus.txt`.

This is a tiny repo example corpus used only for smoke testing. It is not a real language dataset and is not sufficient for quality claims.

## Training Procedure

```bash
.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
.venv/bin/python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
```

## Intended Use

- Research, education and development
- CPU pipeline smoke testing
- Checkpoint/tokenizer contract validation
- Early-stage AchiticLM Nano evaluation

## Out-of-Scope Use

- Production chat
- Factual QA
- Safety-critical use
- Benchmark claims
- Any claim of language quality
- Unsupported factual claims
- High-stakes decisions
- Production deployment without appropriate validation

## License

AchiticLM Nano code, checkpoint/model weights, tokenizer artifacts and example
corpus are released under Apache-2.0. See `LICENSE`, `NOTICE` and
`docs/releases/nano/USAGE_TERMS.md`.

## Limitations and Risks

- Random scratch model trained for only 3 steps.
- Example corpus is tiny.
- Tokenizer pads unused reserved symbols to satisfy the Nano `8000` vocab contract.
- Generated output can include reserved tokens.
- No safety behavior is established.
- GGUF export and quantization are not verified without llama.cpp load-and-generate.

## Evaluation and Smoke Results

- `pytest -q`: `25 passed in 2.82s`
- Prepare: `6` documents
- Encode: `131` tokens
- Train smoke: checkpoint step `3`
- Release inference smoke: passed from `releases/nano/nano.pt` and `releases/nano/tokenizer.model`

## Artifacts

See `docs/releases/nano/ARTIFACT_MANIFEST.md` and `releases/nano/SHA256SUMS`.

## Citation or Repo Reference

Local source snapshot: `/run/media/thanhnd/DATA_LINUX/AchiticLM/achitic-lm`

Source snapshot is available in the local Git repository and is intended to be
published to `https://github.com/SincereVirtueDev/achitic-lm`.
