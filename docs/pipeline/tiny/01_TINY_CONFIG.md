# Tiny task - 20-30M config calibration

Task ID: `TINY-CONFIG-001`

Status: PASS
Owner: Codex
Started: 2026-10-13
Finished: 2026-10-13

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

- [x] Confirm `configs/tiny.json` targets 20-30M parameters.
- [x] Confirm `dim % heads == 0` and `heads % kv_heads == 0`.
- [x] Confirm tokenizer vocab size required by Tiny is documented.
- [x] Record actual parameter count from code when dependencies are available.
- [x] Confirm ladder docs do not need a target-range change and add Tiny tokenizer strategy note.

## Required validation

```bash
python -c "import json; from pathlib import Path; from achitic.model import AchiticLM, Config; c=Config(**json.loads(Path('configs/tiny.json').read_text())); print(sum(p.numel() for p in AchiticLM(c).parameters()))"
python -m pytest -q
```

If `torch` is unavailable, record the formula estimate and mark the task `BLOCKED`, not `PASS`.

## Completion evidence

```text
Status: PASS
Owner: Codex
Files changed:
- docs/pipeline/task_upgrade_tiny.md
- docs/pipeline/tiny/01_TINY_CONFIG.md
- docs/pipeline/00_MODEL_LADDER.md

Commands run:
- .venv/bin/python -c "import json; from pathlib import Path; from achitic.model import AchiticLM, Config; cfg=Config(**json.loads(Path('configs/tiny.json').read_text())); model=AchiticLM(cfg); params=sum(p.numel() for p in model.parameters()); print('params', params); print('vocab_size', cfg.vocab_size); print('dim_mod_heads', cfg.dim % cfg.heads); print('heads_mod_kv_heads', cfg.heads % cfg.kv_heads); print('head_dim', cfg.dim // cfg.heads); print('layers', cfg.layers); print('ffn_dim', cfg.ffn_dim); print('context', cfg.context)"
  Result: params 23058944; vocab_size 12000; dim_mod_heads 0; heads_mod_kv_heads 0; head_dim 64; layers 6; ffn_dim 1408; context 512.
- .venv/bin/python -m pytest -q tests/test_model.py
  Result: 8 passed.
- .venv/bin/python -m pytest -q
  Result: 25 passed.

Parameter count: 23,058,944

Tokenizer strategy:
- Keep configs/tiny.json at vocab_size=12000.
- Do not reuse Nano release tokenizer with vocab_size=8000.
- Train and freeze a new audited Tiny tokenizer in the Data/Tokenizer gate.
- Required special IDs: unk=0, bos=1, eos=2, pad=3.

Known risks:
- Tiny checkpoint training/release is still blocked until Data/Tokenizer PASS.
- The Tiny tokenizer artifact does not exist yet; it must be created from audited phase-2 data before training.

Next allowed tasks:
- UPG-DAT-001
- UPG-MEM-001
```
