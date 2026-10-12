# Nano task - Checkpoint and resume

Task ID: `NANO-CKPT-001`

Status: TODO
Owner:
Started:
Finished:

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

- [ ] Add test that `save()` writes model, optimizer, step, config, torch RNG, numpy RNG and python RNG.
- [ ] Add test that checkpoint config can instantiate `Config` and load model state.
- [ ] Add test that optimizer state loads after at least one optimizer step.
- [ ] Define resume semantics for Nano: exact resume or non-exact data order.
- [ ] If exact resume is not implemented, document the limitation clearly.
- [ ] If exact resume is implemented, store data cursor/sampler state and test it.

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
Status:
Owner:
Files changed:
Commands run:
Results:
Resume semantics:
Known risks:
Next allowed tasks:
```
