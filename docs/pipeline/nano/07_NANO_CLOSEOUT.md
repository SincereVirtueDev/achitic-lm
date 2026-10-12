# Nano closeout

Task ID: `NANO-CLOSE-001`

Status: TODO
Owner:
Started:
Finished:

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

## Allowed write set

- `docs/pipeline/nano/07_NANO_CLOSEOUT.md`
- `docs/pipeline/01_FOUNDATION_SMOKE.md`
- Optional: `docs/pipeline/BACKLOG.md` only to mark Nano row summaries.

## Do not touch

- Source code.
- Tests.
- Configs.
- Generated checkpoints.

## Closeout checklist

- [ ] Confirm every Nano task file is `Status: PASS`.
- [ ] Run full test suite.
- [ ] Run Nano smoke train from prepare to chat.
- [ ] Confirm checkpoint load/resume evidence exists.
- [ ] Confirm tokenizer/config mismatch guard evidence exists.
- [ ] Confirm RoPE/GQA/causality tests exist and pass.
- [ ] Confirm SFT/DPO CPU tests exist and pass.
- [ ] Confirm export docs do not overclaim verification.
- [ ] Update `docs/pipeline/01_FOUNDATION_SMOKE.md` `Phase Closeout` to `PASS` with evidence.

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
Status:
Owner:
Date:
Commit or artifact ref:
pytest:
nano prepare:
nano tokenizer:
nano encode:
nano train:
nano chat:
checkpoint/resume:
RoPE/GQA/causality:
SFT/DPO:
export claim guard:
Next phase unlocked:
```
