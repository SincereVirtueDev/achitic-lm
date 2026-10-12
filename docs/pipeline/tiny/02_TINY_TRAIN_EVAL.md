# Tiny task - Train and eval

Task ID: `TINY-TRAIN-001`

Status: TODO
Owner:
Started:
Finished:

## Goal

Run the 20-30M Tiny model on the audited dataset/tokenizer and produce minimal train/eval/sample evidence.

## Dependencies

- `TINY-CONFIG-001` must be `PASS`.
- `docs/pipeline/02_DATA_TOKENIZER.md` must have `Status: PASS`.

## Allowed write set

- Train/eval scripts if needed.
- Metrics or artifact manifest docs.
- `docs/pipeline/tiny/02_TINY_TRAIN_EVAL.md`
- Generated Tiny run artifacts outside source-controlled docs/code.

## Do not touch

- `achitic/model.py`
- `configs/nano.json`
- Frozen tokenizer files except by creating new versioned artifacts with explicit breaking-contract docs.
- Phase 2 dataset manifests except to reference checksums.

## Checklist

- [ ] Verify tokenizer vocab size equals `configs/tiny.json`.
- [ ] Run a short overfit/loss-decrease check.
- [ ] Run held-out eval perplexity if phase 2 eval split exists.
- [ ] Save sample outputs for fixed Vietnamese/English prompts.
- [ ] Save artifact manifest: config, tokenizer checksum, data checksum, command, hardware, metrics.
- [ ] Confirm Nano smoke still passes after any train/eval code changes.

## Required validation

```bash
python -m pytest -q
python -m achitic.train --config configs/tiny.json --data <phase2-train.bin> --steps <tiny-steps> --batch <batch> --accum <accum> --out runs/tiny.pt
python -m achitic.cli benchmark --checkpoint runs/tiny.pt --tokenizer <phase2-tokenizer.model>
```

Use real paths from the phase 2 closeout. Do not substitute Nano example data for Tiny PASS.

## Completion evidence

```text
Status:
Owner:
Files changed:
Commands run:
Metrics:
Artifact manifest:
Sample report:
Known risks:
Next allowed tasks:
```
