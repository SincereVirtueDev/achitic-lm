# AchiticLM Nano v0.2.0 - Install, Configure And Use

Nano v0.2.0 is a controlled meaning-smoke release. It can produce short
meaningful sentences for the audited near-domain prompts, but it is not validated
for general chat, factual QA, safety-critical use or production deployment.

## 1. Install From Source Zip

```bash
unzip achitic-lm-nano-v0.2.0.zip
cd achitic-lm-nano-v0.2.0

python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pytest -q
```

Validated release result: `91 passed, 1 skipped`. The skipped test is the optional
llama.cpp integration test. No GGUF or quantized artifact is included.

## 2. Download Release Assets

Release URL:

`https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.2.0`

Required for inference:

- `nano-fp16.safetensors` or trusted `nano.pt`
- `tokenizer.model`
- `nano.json`
- `SHA256SUMS`

Recommended documentation:

- `MODEL_CARD.md`
- `EVAL_REPORT.md`
- `MEANING_SMOKE_REPORT.md`
- `TRAINING_RUN_MANIFEST.json`
- `USAGE_TERMS.md`, `LICENSE`, `NOTICE`

Place downloaded files under `releases/nano-v0.2.0/`, then verify them:

```bash
sha256sum -c releases/nano-v0.2.0/SHA256SUMS
```

The checksum file contains paths relative to the repository root. If assets are
downloaded into another directory, either preserve that layout or run
`sha256sum` against each listed artifact manually.

## 3. Run Weights-Only Inference

```bash
python -m achitic.cli chat \
  --checkpoint releases/nano-v0.2.0/nano-fp16.safetensors \
  --tokenizer releases/nano-v0.2.0/tokenizer.model \
  --prompt "Viết một câu ngắn về học máy." \
  --tokens 32
```

## 4. Run Full Checkpoint Inference

```bash
python -m achitic.cli chat \
  --checkpoint releases/nano-v0.2.0/nano.pt \
  --tokenizer releases/nano-v0.2.0/tokenizer.model \
  --prompt "Tóm tắt mục đích của Nano." \
  --tokens 32
```

The checkpoint stage is `sft`; the CLI automatically applies the Achitic chat
template. Use `--chat-template none` only for deliberate raw-continuation tests.

## 5. Configuration Contract

- Parameters: `4,999,424`.
- `vocab_size`: `8000`, exactly matching the packaged tokenizer.
- Special IDs: unknown `0`, BOS `1`, EOS `2`, padding `3`.
- Context: `128`.
- Dimensions: hidden `256`, layers `4`, heads `4`, KV heads `2`, FFN `704`.
- Never combine these weights with another tokenizer or changed config.
- Tiny uses a separate `12000`-token contract; do not reuse the Nano tokenizer.

## 6. Reproduce The Controlled Report

```bash
python -m achitic.cli sample-report \
  --checkpoint releases/nano-v0.2.0/nano.pt \
  --tokenizer releases/nano-v0.2.0/tokenizer.model \
  --prompts docs/eval/nano_meaning_prompts.jsonl \
  --tokens 32 --device cpu --chat-template auto \
  --out /tmp/achitic-nano-v0.2.0-samples.jsonl
```

The recorded result is `10/10` automatic and manual PASS. The SFT set contains
close intent paraphrases, so this is a near-domain smoke and not a broad benchmark.

## 7. Security And Limitations

- Prefer safetensors for inference.
- Load `nano.pt` only from trusted storage after checksum verification.
- The model can hallucinate, repeat, misunderstand requests or produce unsafe text.
- Post-SFT held-out loss is worse than the pre-SFT checkpoint; see `EVAL_REPORT.md`.
- Do not claim GGUF or quantization verification for this release.
- Do not commit credentials, private data, checkpoints or tokenizer binaries.
