# AchiticLM development environment

This file is the reproducible setup contract for Nano pipeline work. Nano is the first CPU smoke target and uses `configs/nano.json`.

## Python target

- Python: 3.10 or newer.
- Platform: Linux is the primary development target.
- GPU: not required for Nano. CPU is enough for the Nano tests and smoke commands.

## Install

Create an isolated environment and install development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

The normal development install must provide:

- `torch` from project dependencies.
- `numpy` from project dependencies.
- `sentencepiece` from project dependencies.
- `pyyaml` from project dependencies.
- `pytest` from the `dev` extra.

Export tooling is optional and intentionally separate:

```bash
pip install -e '.[export]'
```

Do not use export tooling to claim GGUF or quantization verification unless llama.cpp load-and-generate has actually passed.

## Required Nano Validation

Dependency import check:

```bash
python -c "import torch, sentencepiece, pytest; print('nano deps ok')"
```

Unit tests:

```bash
python -m pytest -q
```

Nano smoke:

```bash
python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt "Xin chao" --tokens 16
```

## Local Environment Status

As of 2026-10-12, the Nano development dependencies are installed in `.venv`.

Validated versions:

- `torch 2.14.1+cu130`
- `sentencepiece 0.2.2`
- `pytest 9.1.1`
