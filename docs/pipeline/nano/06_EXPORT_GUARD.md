# Nano task - Export claim guard

Task ID: `NANO-EXP-001`

Status: TODO
Owner:
Started:
Finished:

## Goal

Prevent accidental claims that GGUF export or quantization are verified before a real llama.cpp load-and-generate test exists.

## Dependencies

- `NANO-ENV-001` must be `PASS`.

## Allowed write set

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/pipeline/06_EXPORT_EDGE.md`
- Optional: `tests/test_export_guard.py`
- `docs/pipeline/nano/06_EXPORT_GUARD.md`

## Do not touch

- `achitic/model.py`
- `achitic/train.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py` unless a guard must be enforced in code.

## Checklist

- [ ] Confirm README says GGUF export is experimental until llama.cpp generation passes.
- [ ] Confirm architecture docs mention tokenizer parity and llama.cpp compatibility must be tested.
- [ ] Confirm roadmap export gate requires load-and-generate.
- [ ] Add a doc/test guard if wording drifts toward verified claims.
- [ ] Do not mark any export artifact verified in Nano unless llama.cpp was actually run.

## Required validation

```bash
rg "verified|load-and-generate|llama.cpp|experimental|not been verified" README.md docs scripts
python -m pytest -q
```

## Conflict rules

- This task is documentation/guard only. It must not change exporter tensor mapping.
- Real exporter fixes belong to phase 6 after Nano and relevant train gates PASS.

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
