# Tiny closeout

Task ID: `TINY-CLOSE-001`

Status: TODO
Owner:
Started:
Finished:

## Goal

Chốt Tiny CPU model trước khi chuyển sang Mini/Small scale experiments.

## Dependencies

- `TINY-CONFIG-001` must be `PASS`.
- `TINY-TRAIN-001` must be `PASS`.

## Allowed write set

- `docs/pipeline/tiny/03_TINY_CLOSEOUT.md`
- Optional: `docs/pipeline/03_PRETRAIN_SCALE.md`
- Optional: `docs/pipeline/BACKLOG.md`

## Do not touch

- Source code.
- Configs.
- Data/tokenizer artifacts.

## Closeout checklist

- [ ] Confirm Tiny parameter count is 20-30M.
- [ ] Confirm data/tokenizer phase is PASS and checksums are referenced.
- [ ] Confirm `pytest -q` pass.
- [ ] Confirm Nano smoke still pass.
- [ ] Confirm Tiny train/eval/sample evidence exists.
- [ ] Confirm artifact manifest exists.
- [ ] Mark Tiny gate PASS in `docs/pipeline/03_PRETRAIN_SCALE.md` if that file tracks scale gates.

## PASS evidence template

```text
Status:
Owner:
Date:
Commit or artifact ref:
pytest:
nano smoke:
tiny param count:
tiny train:
tiny eval:
tiny samples:
artifact manifest:
Next phase unlocked:
```
