# Nano task - Export claim guard

Task ID: `NANO-EXP-001`

Status: PASS
Owner: Codex
Started: 2026-10-12
Finished: 2026-10-12

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

- [x] Confirm README says GGUF export is experimental until llama.cpp generation passes.
- [x] Confirm architecture docs mention tokenizer parity and llama.cpp compatibility must be tested.
- [x] Confirm roadmap export gate requires load-and-generate.
- [x] Add a doc/test guard if wording drifts toward verified claims.
- [x] Do not mark any export artifact verified in Nano unless llama.cpp was actually run.

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
Status: PASS
Owner: Codex
Files changed: README.md; docs/ARCHITECTURE.md; docs/ROADMAP.md; docs/pipeline/06_EXPORT_EDGE.md; tests/test_export_guard.py; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_export_guard.py
- .venv/bin/python -m pytest -q
- rg "verified|load-and-generate|llama.cpp|experimental|not been verified" README.md docs scripts
Results:
- Export claim guard tests passed.
- Full test suite passed during Nano closeout: 25 passed in 2.82s.
Known risks: GGUF export, tokenizer parity and quantized artifacts are not verified until pinned llama.cpp load-and-generate evidence exists.
Next allowed tasks: NANO-PUBLISH-001 and NANO-CLOSE-001 are now PASS.
```
