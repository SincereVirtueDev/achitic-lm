# AchiticLM Nano v0.2.0 Install, Configure And Use

## Install From Source

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pytest -q
```

Validated result for this candidate: `91 passed, 1 skipped`.

## Verify The Package

```bash
sha256sum -c releases/nano-v0.2.0/SHA256SUMS
```

## Generate With Weights-Only Artifact

```bash
python -m achitic.cli chat \
  --checkpoint releases/nano-v0.2.0/nano-fp16.safetensors \
  --tokenizer releases/nano-v0.2.0/tokenizer.model \
  --prompt "Tóm tắt mục đích của Nano." \
  --tokens 32
```

## Generate With Full Checkpoint

```bash
python -m achitic.cli chat \
  --checkpoint releases/nano-v0.2.0/nano.pt \
  --tokenizer releases/nano-v0.2.0/tokenizer.model \
  --prompt "Viết một câu ngắn về học máy." \
  --tokens 32
```

The CLI detects stage `sft` and applies the Achitic chat template automatically.
Use `--chat-template none` only when deliberately testing raw continuation.

## Reproduce The Fixed-Prompt Report

```bash
python -m achitic.cli sample-report \
  --checkpoint releases/nano-v0.2.0/nano.pt \
  --tokenizer releases/nano-v0.2.0/tokenizer.model \
  --prompts docs/eval/nano_meaning_prompts.jsonl \
  --tokens 32 --device cpu --chat-template auto \
  --out /tmp/achitic-nano-meaning-samples.jsonl
```

## Contract Rules

- Keep config and tokenizer vocabulary at exactly `8000` for these weights.
- Context length is `128`; longer input is unsupported.
- Prefer safetensors for inference. Treat `nano.pt` as trusted-only input.
- Do not use this tokenizer for Tiny, whose config requires `12000` tokens.
- Do not describe an exported GGUF/quantized file as verified without an exact
  llama.cpp load-and-generate test.
