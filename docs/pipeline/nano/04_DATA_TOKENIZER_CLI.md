# Nano task - Data, tokenizer and CLI smoke

Task ID: `NANO-DATA-001`

Status: TODO
Owner:
Started:
Finished:

## Goal

Make the Nano data path runnable end to end: prepare text, train tokenizer, encode corpus, create `TokenDataset`, run Nano train and chat.

## Dependencies

- `NANO-ENV-001` must be `PASS`.

## Allowed write set

- `tests/test_data_tokenizer_cli.py`
- `achitic/data.py`
- `achitic/tokenizer.py`
- `achitic/cli.py`
- `configs/nano.json`
- Optional: `scripts/nano_smoke.sh`
- `docs/pipeline/nano/04_DATA_TOKENIZER_CLI.md`

## Do not touch

- `achitic/model.py`
- `achitic/train.py` unless the checkpoint task owner agrees.
- `achitic/alignment.py`
- `scripts/export_gguf.py`
- Large real dataset files.

## Checklist

- [ ] Add test for `clean()` NFC normalization and NUL removal.
- [ ] Add test for `prepare()` min length and exact dedup behavior.
- [ ] Add test for `TokenDataset` length and `not enough tokens` error.
- [ ] Add tokenizer train/load smoke with a very small temporary corpus.
- [ ] Add tokenizer special ID assertion: `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- [ ] Add CLI mismatch guard test or a small loader helper test for tokenizer vocab vs config vocab.
- [ ] Provide a Nano smoke command that is realistic for `examples/corpus.txt`.
- [ ] Keep `configs/nano.json` in the 5-10M target range unless model ladder is updated.

## Required validation

```bash
python -m pytest -q tests/test_data_tokenizer_cli.py
python -m pytest -q
python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt "Xin chao" --tokens 16
```

## Conflict rules

- Do not edit `achitic/train.py` from this task unless the checkpoint owner explicitly hands it off.
- Do not change tokenizer special IDs without updating every checkpoint/export/alignment task.

## Completion evidence

```text
Status:
Owner:
Files changed:
Commands run:
Results:
Tokenizer IDs:
Nano smoke artifact paths:
Known risks:
Next allowed tasks:
```
