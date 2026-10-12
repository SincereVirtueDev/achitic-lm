# Tiny task - 20-30M config calibration

Task ID: `TINY-CONFIG-001`

Status: TODO
Owner:
Started:
Finished:

## Goal

Calibrate Tiny as the first real CPU language-learning target after Nano, without changing AchiticLM architecture.

## Dependencies

- Nano closeout must be `PASS`.

## Allowed write set

- `configs/tiny.json`
- `docs/pipeline/00_MODEL_LADDER.md`
- `docs/pipeline/tiny/01_TINY_CONFIG.md`
- Optional: param-count utility docs/tests if created by the owner.

## Do not touch

- `achitic/model.py`
- `achitic/train.py`
- `achitic/tokenizer.py`
- Data manifests or tokenizer artifacts.

## Checklist

- [ ] Confirm `configs/tiny.json` targets 20-30M parameters.
- [ ] Confirm `dim % heads == 0` and `heads % kv_heads == 0`.
- [ ] Confirm tokenizer vocab size required by Tiny is documented.
- [ ] Record actual parameter count from code when dependencies are available.
- [ ] Update ladder docs if the target range changes.

## Required validation

```bash
python -c "import json; from pathlib import Path; from achitic.model import AchiticLM, Config; c=Config(**json.loads(Path('configs/tiny.json').read_text())); print(sum(p.numel() for p in AchiticLM(c).parameters()))"
python -m pytest -q
```

If `torch` is unavailable, record the formula estimate and mark the task `BLOCKED`, not `PASS`.

## Completion evidence

```text
Status:
Owner:
Files changed:
Commands run:
Parameter count:
Known risks:
Next allowed tasks:
```
