# Tiny task - Train and eval

Task ID: `TINY-TRAIN-001`

Status: BLOCKED
Owner: Codex
Started: 2026-10-13
Blocked date: 2026-10-13
Finished:

## Goal

Run the 20-30M Tiny model on the audited dataset/tokenizer and produce minimal train/eval/sample evidence.

## Dependencies

- `TINY-CONFIG-001` must be `PASS`.
- `docs/pipeline/02_DATA_TOKENIZER.md` must have `Status: PASS`.

Current dependency state:

- `docs/pipeline/02_DATA_TOKENIZER.md` is `Status: BLOCKED_NO_APPROVED_TINY_CORPUS`, not `PASS`.
- `docs/data/tiny_dataset_manifest.json` has no approved Tiny train sources.
- `docs/data/tiny_dataset_manifest.json` has no approved Tiny eval sources.
- Tiny config requires tokenizer `vocab_size=12000`; the Nano release tokenizer is `8000` and smoke-only.
- Do not substitute Nano example data or Nano tokenizer for Tiny PASS.

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

- [ ] Verify tokenizer vocab size equals `configs/tiny.json`. BLOCKED until frozen Tiny tokenizer exists.
- [ ] Run a short overfit/loss-decrease check. BLOCKED until approved Tiny train `.bin` exists.
- [ ] Run held-out eval perplexity. BLOCKED until approved Tiny eval `.bin` exists.
- [ ] Save sample outputs for fixed Vietnamese/English prompts. BLOCKED until Tiny checkpoint exists.
- [ ] Save artifact manifest: config, tokenizer checksum, data checksum, command, hardware, metrics. BLOCKED until Tiny run artifacts exist.
- [ ] Confirm Nano smoke still passes after any train/eval code changes. BLOCKED until this task has implementation/run changes.

## Required validation

```bash
python -m pytest -q
python -m achitic.train --config configs/tiny.json --data <phase2-train.bin> --steps <tiny-steps> --batch <batch> --accum <accum> --out runs/tiny.pt
python -m achitic.cli benchmark --checkpoint runs/tiny.pt --tokenizer <phase2-tokenizer.model>
```

Use real paths from the phase 2 closeout. Do not substitute Nano example data for Tiny PASS.

## Required unblock inputs

- Approved Tiny train source with provenance, license, rights owner, snapshot date, raw checksum, normalized checksum and allowed use.
- Approved held-out Tiny eval source or split with documented separation from train.
- Privacy scan report.
- Exact dedup report.
- Train/eval contamination report.
- Frozen Tiny tokenizer `12000` with special IDs `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Encoded train/eval `.bin` files whose tokenizer vocabulary matches `configs/tiny.json`.
- Phase 2 closeout updated to `Status: PASS`.

## Completion evidence

```text
Status: BLOCKED
Owner: Codex
Files changed: docs/pipeline/task_upgrade_tiny.md, docs/pipeline/tiny/02_TINY_TRAIN_EVAL.md
Commands run:
- .venv/bin/python -c "import json; m=json.load(open('docs/data/tiny_dataset_manifest.json')); print('manifest_status', m.get('status')); print('approved_train_sources', len(m.get('approved_tiny_train_sources', []))); print('approved_eval_sources', len(m.get('approved_tiny_eval_sources', []))); print('tokenizer_vocab', m.get('tokenizer_contract', {}).get('vocab_size')); print('blockers', [b.get('id') for b in m.get('blockers', [])])"
Metrics: none; Tiny training was not run.
Artifact manifest: none; no Tiny checkpoint or release candidate was created.
Sample report: none; no Tiny checkpoint exists.
Known risks: Training Tiny before Phase 2 PASS would create an invalid checkpoint/tokenizer/data contract.
Next allowed tasks: complete Phase 2 Data/Tokenizer closeout, then retry UPG-TRAIN-001.
```
