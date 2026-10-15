# AchiticLM Nano v0.2.0 Release Candidate

Status: RELEASE_ARTIFACT

AchiticLM Nano is a `4,999,424`-parameter decoder-only Transformer trained from
scratch on a bounded Vietnamese Wikipedia corpus and aligned with `80`
project-authored SFT pairs. It passes a controlled 10-prompt sentence smoke; it is
not a general Vietnamese language model or a production chat model.

## Contents

- `nano.pt`: full SFT checkpoint with optimizer and RNG state.
- `nano-fp16.safetensors`: FP16 weights-only artifact for safer inference loading.
- `tokenizer.model`, `tokenizer.vocab`: exact `8000`-token SentencePiece contract.
- `nano.json`: exact architecture config.
- `TRAINING_RUN_MANIFEST.json`: sanitized scratch-training and SFT facts.
- `MEANING_SMOKE_REPORT.md`: fixed-prompt manual and automatic review.
- Model, evaluation, install, security, usage and technical documentation.

The raw Wikipedia dump and cleaned corpus are not included.

## Quick Check

```bash
sha256sum -c releases/nano-v0.2.0/SHA256SUMS
python -m achitic.cli chat \
  --checkpoint releases/nano-v0.2.0/nano-fp16.safetensors \
  --tokenizer releases/nano-v0.2.0/tokenizer.model \
  --prompt "Viết một câu ngắn về học máy." --tokens 32
```

The checkpoint stage is `sft`, so the CLI automatically uses the Achitic chat
template. No GGUF or quantized artifact is included.
