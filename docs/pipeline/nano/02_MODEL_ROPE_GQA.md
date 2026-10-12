# Nano task - Model, RoPE and GQA CPU tests

Task ID: `NANO-MODEL-001`

Status: PASS
Owner: Codex
Started: 2026-10-12
Finished: 2026-10-12

## Goal

Make the shared architecture baseline trustworthy on CPU before Tiny or larger training. Cover causality, RoPE, GQA, invalid configs and generation shape.

## Dependencies

- `NANO-ENV-001` must be `PASS`.

## Allowed write set

- `tests/test_model.py`
- Optional: `tests/test_architecture.py`
- `achitic/model.py` only if a failing test proves a bug.
- `docs/pipeline/nano/02_MODEL_ROPE_GQA.md`

## Do not touch

- `achitic/train.py`
- `achitic/data.py`
- `achitic/tokenizer.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py`

## Checklist

- [x] Add/keep forward, backward and generation smoke on CPU.
- [x] Add deterministic causality test: changing future token must not affect earlier logits.
- [x] Add RoPE test for shape and dtype preservation.
- [x] Add GQA valid config test: `heads % kv_heads == 0`.
- [x] Add GQA invalid config test: invalid `heads`/`kv_heads` raises.
- [x] Add tied embedding/output assertion.
- [x] Keep tests small enough for CPU.

## Required validation

```bash
python -m pytest -q tests/test_model.py
python -m pytest -q
```

## Conflict rules

- If another task needs to edit `achitic/model.py`, both owners must stop and create one combined model patch.
- Do not change architecture just to hit Nano/Tiny parameter targets. Size belongs in config files.

## Completion evidence

```text
Status: PASS
Owner: Codex
Files changed: tests/test_model.py; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_model.py
- .venv/bin/python -m pytest -q
Results:
- RoPE, causality, tied weight and GQA tests passed.
- Full test suite passed during Nano closeout: 25 passed in 2.82s.
Known risks: none for Nano CPU architecture gate.
Next allowed tasks: NANO-CKPT-001, NANO-DATA-001, NANO-ALN-001 and NANO-EXP-001 are already PASS.
```
