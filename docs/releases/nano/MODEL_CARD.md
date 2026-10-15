# AchiticLM Nano Model Card

Status: PUBLISHED

## Model Summary

AchiticLM Nano is a scratch-initialized decoder-only Transformer checkpoint for pipeline smoke testing. It is not pretrained, not instruction-tuned, and not suitable for real chat, factual QA or production use.

- Parameters: `4,999,424`
- Vocabulary size: `8000`
- Context length: `128`
- Training steps: `3`
- Release checkpoint: `releases/nano/nano.pt`
- Checkpoint file size: `60,043,760` bytes
- Checkpoint format: full PyTorch training checkpoint with model, optimizer and RNG state

## Architecture

AchiticLM Core:

- Decoder-only Transformer
- GQA
- RoPE
- RMSNorm
- SwiGLU
- Tied embedding/output weight

The same architecture is used for Nano, Tiny and larger ladder targets; size changes are config changes, not model forks.

## Parameter Allocation

Trainable unique parameters:

| Component | Parameters |
| --- | ---: |
| Token embedding and tied output head | `2,048,000` |
| Attention projections across 4 layers | `786,432` |
| SwiGLU FFN projections across 4 layers | `2,162,688` |
| RMSNorm weights | `2,304` |
| Total | `4,999,424` |

The tied output head reuses `embed.weight`. The checkpoint state dict lists both `embed.weight` and `head.weight`, but they share storage when loaded.

## Training Data

Training data source: `examples/corpus.txt`.

This is a tiny repo example corpus used only for smoke testing. It is not a real language dataset and is not sufficient for quality claims.

## Training Procedure

```bash
.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000 --allow-reserved-padding
.venv/bin/python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt --metrics runs/nano-metrics.jsonl
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
- Current KV-cache parity is verified by CPU tests only.
- GGUF export and quantization are not verified without llama.cpp load-and-generate.

## Evaluation and Smoke Results

- `.venv/bin/python -m pytest -q`: `64 passed, 1 skipped`
- Prepare: `6` documents
- Encode: `131` tokens
- Current Nano-X doc smoke train losses:
  - step 1: `9.042657852172852`
  - step 2: `8.647053718566895`
  - step 3: `8.375679969787598`
- Train smoke: checkpoint step `3`
- Release inference smoke: passed from `releases/nano/nano.pt` and `releases/nano/tokenizer.model`

## Checkpoint Size Notes

Measured from `releases/nano/nano.pt`:

| Component | Tensor bytes |
| --- | ---: |
| Model unique tensor storage | `19,997,696` |
| Optimizer tensor storage | `39,995,544` |
| Torch RNG tensor storage | `5,056` |
| Serialization metadata and overhead | `45,464` |
| Full checkpoint file | `60,043,760` |

The full checkpoint is larger than a weights-only artifact because it stores AdamW optimizer state and RNG state for resume smoke tests.

## Artifacts

See `docs/releases/nano/ARTIFACT_MANIFEST.md` and `releases/nano/SHA256SUMS`.

## Citation or Repo Reference

Source snapshot: `<local checkout>`

Source repository: `https://github.com/SincereVirtueDev/achitic-lm`

Latest published Nano release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.1`
