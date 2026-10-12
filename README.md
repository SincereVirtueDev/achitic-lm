# AchiticLM — from-scratch language-model research repo

**Status:** runnable research foundation; not a pretrained/chat-capable model, and not a production 1B training system. All model weights initialize randomly. PyTorch and SentencePiece are implementation libraries, not sources of pretrained weights.

## Quick start (Linux / Python 3.10+)
For the full Nano development environment contract, see `docs/DEVELOPMENT.md`.
For source-zip installation, configuration and release-asset usage, see `INSTALL_USAGE.md`.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt 'Xin chào' --tokens 16
python -m achitic.cli benchmark --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model
```
Nano example data is intentionally tiny and **will not produce meaningful language**. For realistic training use a large legally usable and curated corpus, with a separate held-out evaluation set. Ensure token count >= context+1. For an extremely short corpus, reduce `context` in a copied config.

## Model ladder
AchiticLM keeps one core architecture across sizes. The intended ladder is Nano (5-10M, pipeline test), Tiny (20-30M, basic CPU language learning), Mini (~50M), Small (~150M), 350M-class and 1B-class. See `docs/pipeline/00_MODEL_LADDER.md`.

## License and Nano usage
AchiticLM source code, documentation, example corpus, tokenizer artifacts and scratch-trained Nano checkpoint are released under Apache-2.0 unless stated otherwise. See `LICENSE`, `NOTICE` and `docs/releases/nano/USAGE_TERMS.md`.

Nano is intended for research, education, development, pipeline smoke testing and early experimentation. Do not use it for safety-critical applications, unsupported factual claims, high-stakes decisions or production deployment without appropriate validation.

## SFT and DPO
```bash
python -m achitic.alignment --mode sft --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --data examples/sft.jsonl --out runs/sft.pt --steps 10
python -m achitic.alignment --mode dpo --checkpoint runs/sft.pt --tokenizer /tmp/achitic-sp.model --data examples/dpo.jsonl --out runs/dpo.pt --steps 10
```
SFT/DPO are reference single-device loops, with JSONL prompt/response and prompt/chosen/rejected formats respectively. Not production alignment pipelines.

## Distributed data parallel (one model replica per GPU)
```bash
torchrun --standalone --nproc_per_node=2 -m achitic.train --config configs/50m.json --data /data/train.bin --steps 1000 --out runs/50m.pt
```
This is DDP, **not** parameter sharding. 1B training requires larger accelerators or FSDP2 extension.

## GGUF export / quantization (experimental)
```bash
pip install -e '.[export]'
python scripts/export_gguf.py --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --out runs/nano-f16.gguf
bash scripts/quantize.sh /path/to/llama-quantize runs/nano-f16.gguf runs/nano-q4.gguf
```
The exporter is experimental until a pinned llama.cpp build can load-and-generate from the exact GGUF artifact. **Conversion, tokenizer parity and actual llama.cpp inference have not been verified** for Nano or quantized variants. Treat this as an integration starting point, not a guarantee of GGUF compatibility.

## Scope
`achitic/model.py` architecture; `tokenizer.py` scratch tokenizer; `data.py` normalization/exact dedup/token storage; `train.py` pretraining+DDP+checkpoint; `alignment.py` SFT/DPO; `cli.py` inference/benchmark; `scripts/` GGUF and quantize; `docs/` design and roadmap; `AGENTS.md` collaboration instructions.

4GB VRAM is a **quantized inference target**, not a feasible full 1B pretraining budget. Benchmarks and VRAM acceptance require real hardware.
