# Nano Release Command Log

Status: READY_FOR_GITHUB_PUBLICATION

Date: 2026-10-12

Source snapshot: repository checkout at publication time; GitHub publication target is `SincereVirtueDev/achitic-lm`.

## Environment

- Python: 3.14.4
- Platform: Linux-7.0.0-38-generic-x86_64-with-glibc2.43
- torch: 2.14.1+cu130
- sentencepiece: 0.2.2
- pytest: 9.1.1

## Commands

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000 --allow-reserved-padding
.venv/bin/python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
.venv/bin/python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt "Xin chao" --tokens 16
cp runs/nano.pt releases/nano/nano.pt
cp /tmp/achitic-sp.model releases/nano/tokenizer.model
cp /tmp/achitic-sp.vocab releases/nano/tokenizer.vocab
cp configs/nano.json releases/nano/configs/nano.json
sha256sum releases/nano/nano.pt releases/nano/tokenizer.model releases/nano/tokenizer.vocab releases/nano/configs/nano.json
```

## Results

- Full pytest at original Nano publication: `25 passed in 2.82s`.
- Current Nano-X repository validation: `64 passed, 1 skipped`.
- Prepare: `6` documents from `examples/corpus.txt`.
- Encode: `131` tokens.
- Train smoke: `runs/nano.pt`, step `3`.
- Checkpoint/tokenizer vocab: `8000 / 8000`.
- Release checksum verification passed from `releases/nano/SHA256SUMS`.
- Release package chat smoke passed from `releases/nano/nano.pt` and `releases/nano/tokenizer.model`.

Release chat smoke output:

```text
Xin chao<|reserved_2387|><|reserved_1849|><|reserved_3267|><|reserved_4988|><|reserved_3253|> là là<|reserved_6562|><|reserved_2081|><|reserved_3617|> trình<|reserved_6940|><|reserved_5230|> đô<|reserved_833|><|reserved_2274|>
```
