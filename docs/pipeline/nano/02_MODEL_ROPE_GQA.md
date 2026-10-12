# Nano task - Model, RoPE and GQA CPU tests

Task ID: `NANO-MODEL-001`

Status: TODO
Owner:
Started:
Finished:

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

- [ ] Add/keep forward, backward and generation smoke on CPU.
- [ ] Add deterministic causality test: changing future token must not affect earlier logits.
- [ ] Add RoPE test for shape and dtype preservation.
- [ ] Add GQA valid config test: `heads % kv_heads == 0`.
- [ ] Add GQA invalid config test: invalid `heads`/`kv_heads` raises.
- [ ] Add tied embedding/output assertion.
- [ ] Keep tests small enough for CPU.

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
Status:
Owner:
Files changed:
Commands run:
Results:
Known risks:
Next allowed tasks:
```
