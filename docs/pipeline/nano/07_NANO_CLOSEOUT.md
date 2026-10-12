# Nano closeout

Task ID: `NANO-CLOSE-001`

Status: PASS
Owner: Codex
Started: 2026-10-12
Finished: 2026-10-12

## Goal

Chốt Nano/Foundation thành `PASS`, sau đó mới mở khóa Tiny tasks và phase 2 Data/Tokenizer.

## Dependencies

All Nano task files must be `Status: PASS`:

- `NANO-ENV-001`
- `NANO-MODEL-001`
- `NANO-CKPT-001`
- `NANO-DATA-001`
- `NANO-ALN-001`
- `NANO-EXP-001`
- `NANO-PUBLISH-001`

## Allowed write set

- `docs/pipeline/nano/00_NANO_BOARD.md`
- `docs/pipeline/nano/02_MODEL_ROPE_GQA.md`
- `docs/pipeline/nano/03_CHECKPOINT_RESUME.md`
- `docs/pipeline/nano/04_DATA_TOKENIZER_CLI.md`
- `docs/pipeline/nano/05_ALIGNMENT_CPU.md`
- `docs/pipeline/nano/06_EXPORT_GUARD.md`
- `docs/pipeline/nano/07_NANO_CLOSEOUT.md`
- `docs/pipeline/01_FOUNDATION_SMOKE.md`
- Optional: `docs/pipeline/BACKLOG.md` only to mark Nano row summaries.

## Do not touch

- Source code.
- Tests.
- Configs.
- Generated checkpoints.

## Closeout checklist

- [x] Confirm every Nano task file is `Status: PASS`.
- [x] Run full test suite.
- [x] Run Nano smoke train from prepare to chat.
- [x] Run release artifact inference smoke.
- [x] Confirm release package checksum verification.
- [x] Confirm checkpoint load/resume evidence exists.
- [x] Confirm tokenizer/config mismatch guard evidence exists.
- [x] Confirm RoPE/GQA/causality evidence exists and passes.
- [x] Confirm SFT/DPO CPU evidence exists and passes.
- [x] Confirm export docs do not overclaim verification.
- [x] Confirm public GitHub repo and Nano release assets exist.
- [x] Update `docs/pipeline/01_FOUNDATION_SMOKE.md` `Phase Closeout` to `PASS` with evidence.

## Required validation

```bash
python -m pytest -q
python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt "Xin chao" --tokens 16
```

## PASS evidence template

```text
Status: PASS
Owner: Codex
Date: 2026-10-12
Commit or artifact ref: https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.0
pytest: .venv/bin/python -m pytest -q -> 25 passed in 2.82s
nano prepare: examples/corpus.txt -> /tmp/achitic-closeout-clean.txt; documents: 6
nano tokenizer: /tmp/achitic-closeout-sp.model; vocab 8000
nano encode: /tmp/achitic-closeout.bin; tokens: 131
nano train: configs/nano.json -> runs/nano.pt; checkpoint step 3, vocab 8000
nano chat: runs/nano.pt + /tmp/achitic-closeout-sp.model -> passed
release chat: releases/nano/nano.pt + releases/nano/tokenizer.model -> passed
release checksum: sha256sum -c releases/nano/SHA256SUMS -> all OK
checkpoint/resume: tests/test_checkpoint.py and docs/CHECKPOINTS.md define load/resume contract; exact data-order resume is not claimed
RoPE/GQA/causality: tests/test_model.py covers forward/backward/generation, tied weights, causality, RoPE dtype/shape and valid/invalid GQA
SFT/DPO: tests/test_alignment.py covers finite response score, response-only scoring, invalid length and SFT prompt mask
export claim guard: tests/test_export_guard.py and docs keep GGUF/quantization experimental until llama.cpp load-and-generate evidence exists
release package: public repo and GitHub Release nano-v0.1.0 are published with 10 verified assets
Next phase unlocked: Tiny CPU gate may start; Data/Tokenizer phase may start for real training data, but Tiny real training still depends on audited data/tokenizer work
```
