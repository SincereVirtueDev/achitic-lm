# Nano task - Checkpoint and resume

Task ID: `NANO-CKPT-001`

Status: PASS
Owner: Codex
Started: 2026-10-12
Finished: 2026-10-12

## Goal

Prove Nano checkpoints can be saved, loaded and resumed without breaking config, model state, optimizer state or RNG metadata.

## Dependencies

- `NANO-ENV-001` must be `PASS`.

## Allowed write set

- `tests/test_checkpoint.py`
- `achitic/train.py`
- Optional: `docs/CHECKPOINTS.md`
- `docs/pipeline/nano/03_CHECKPOINT_RESUME.md`

## Do not touch

- `achitic/model.py` unless checkpoint test proves model state incompatibility and the model-task owner agrees.
- `achitic/tokenizer.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py`

## Checklist

- [x] Add test that `save()` writes model, optimizer, step, config, torch RNG, numpy RNG and python RNG.
- [x] Add test that checkpoint config can instantiate `Config` and load model state.
- [x] Add test that optimizer state loads after at least one optimizer step.
- [x] Define resume semantics for Nano: exact resume or non-exact data order.
- [x] If exact resume is not implemented, document the limitation clearly.
- [x] If exact resume is implemented, store data cursor/sampler state and test it.

## Required validation

```bash
python -m pytest -q tests/test_checkpoint.py
python -m pytest -q
```

## Conflict rules

- `achitic/train.py` is exclusive to this task while `Status: IN_PROGRESS`.
- If `NANO-DATA-001` needs a train CLI change, coordinate before editing `achitic/train.py`.

## Completion evidence

```text
Status: PASS
Owner: Codex
Files changed: tests/test_checkpoint.py; achitic/train.py; docs/CHECKPOINTS.md; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_checkpoint.py
- .venv/bin/python -m pytest -q
Results:
- Checkpoint save/load contract tests passed.
- Full test suite passed during Nano closeout: 25 passed in 2.82s.
Resume semantics: model, optimizer and RNG are restored; exact data order is not claimed because data cursor/sampler state is not stored.
Known risks: exact data-order resume remains future scale work.
Next allowed tasks: dependent Nano rows are already PASS.
```
