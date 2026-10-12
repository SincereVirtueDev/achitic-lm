# AchiticLM Nano - Install, Configure and Use

This guide is for the `nano-v0.1.0` source zip and release assets.

Nano is a 3-step scratch-trained pipeline artifact. It proves that the local
CPU pipeline works, but it is not a useful chat model and must not be used for
production, safety-critical decisions or factual claims.

## 1. Install From Source Zip

```bash
unzip achitic-lm-nano-v0.1.0.zip
cd achitic-lm-nano-v0.1.0

python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

python -m pytest -q
```

Expected test result for the Nano release line:

```text
25 passed
```

The source zip contains code, configs, examples and docs. It does not contain
the large generated checkpoint/tokenizer binary assets unless you download them
from the GitHub Release.

## 2. Nano Config

Use `configs/nano.json` for the published Nano pipeline.

Important fields:

- `vocab_size`: must match the tokenizer vocabulary size. Nano uses `8000`.
- `context`: maximum sequence length used by training/inference. Nano uses `128`.
- `dim`, `layers`, `heads`, `kv_heads`, `ffn_dim`: model size and attention layout.
- `rope_theta`: RoPE frequency base.

Rules:

- Do not change `vocab_size` unless you also retrain the tokenizer and use a
  matching checkpoint.
- `heads % kv_heads` must be `0`.
- The encoded corpus must contain at least `context + 1` tokens.
- Bigger configs such as Tiny/50M/1B are not Nano release claims.

## 3. Reproduce Nano Smoke From Source

```bash
python -m achitic.cli prepare \
  --inputs examples/corpus.txt \
  --out /tmp/achitic-clean.txt

python -m achitic.cli tokenizer \
  --input /tmp/achitic-clean.txt \
  --prefix /tmp/achitic-sp \
  --vocab 8000

python -m achitic.cli encode \
  --input /tmp/achitic-clean.txt \
  --tokenizer /tmp/achitic-sp.model \
  --out /tmp/achitic.bin

python -m achitic.train \
  --config configs/nano.json \
  --data /tmp/achitic.bin \
  --steps 3 \
  --batch 1 \
  --accum 1 \
  --out runs/nano.pt

python -m achitic.cli chat \
  --checkpoint runs/nano.pt \
  --tokenizer /tmp/achitic-sp.model \
  --prompt "Xin chao" \
  --tokens 16
```

The generated text may include reserved tokens. That is expected for Nano.

## 4. Use Published Nano Checkpoint

Download these release assets from:

`https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.0`

Required for inference:

- `nano.pt`
- `tokenizer.model`
- `SHA256SUMS`

Recommended:

- `tokenizer.vocab`
- `nano.json`
- `USAGE_TERMS.md`
- `LICENSE`
- `NOTICE`

Place the assets under `releases/nano/`:

```bash
mkdir -p releases/nano
```

After downloading, verify checksums from the repository root:

```bash
sha256sum -c releases/nano/SHA256SUMS
```

Run inference smoke:

```bash
python -m achitic.cli chat \
  --checkpoint releases/nano/nano.pt \
  --tokenizer releases/nano/tokenizer.model \
  --prompt "Xin chao" \
  --tokens 16
```

## 5. Optional Benchmark

```bash
python -m achitic.cli benchmark \
  --checkpoint releases/nano/nano.pt \
  --tokenizer releases/nano/tokenizer.model
```

Treat this as a local smoke benchmark only. It is not a model quality benchmark.

## 6. Security Notes

- `nano.pt` is a PyTorch checkpoint. Only load it from trusted storage after
  checksum verification.
- Do not commit `github_token.txt`, `.venv`, `runs/`, `*.pt`, `*.model`,
  `*.vocab` or `*.gguf`.
- GGUF export and quantization are not verified for Nano until a pinned
  llama.cpp load-and-generate test passes for each artifact.

## 7. Common Errors

Tokenizer/config mismatch:

```text
tokenizer vocab size ... does not match checkpoint config vocab_size ...
```

Use the tokenizer that belongs to the checkpoint, or retrain both together.

Not enough tokens:

```text
not enough tokens
```

Use a longer corpus or reduce `context` in a copied config.

Missing dependency:

```bash
pip install -e '.[dev]'
```

Run from an activated virtual environment.
