# Nano task - Alignment CPU tests

Task ID: `NANO-ALN-001`

Status: PASS
Owner: Codex
Started: 2026-10-12
Finished: 2026-10-12

## Goal

Keep SFT/DPO reference code safe enough for Nano by testing prompt masking and response-only log probability before larger alignment work.

## Dependencies

- `NANO-ENV-001` must be `PASS`.
- `NANO-MODEL-001` must be `PASS`.

## Allowed write set

- `tests/test_alignment.py`
- `achitic/alignment.py` only if a failing test proves a bug.
- `docs/pipeline/nano/05_ALIGNMENT_CPU.md`

## Do not touch

- `achitic/model.py`
- `achitic/train.py`
- `achitic/tokenizer.py`
- `scripts/export_gguf.py`

## Checklist

- [x] Add test for `sequence_logprob()` shape and finite output.
- [x] Add response-only scoring test: prompt-only positions must not be included in returned sum.
- [x] Add invalid sequence length test for empty prompt or context overflow.
- [x] Add SFT masking regression test showing prompt tokens are set to `-100`.
- [x] Keep alignment tests CPU-only and small.
- [x] Document that this is not a production alignment pipeline.

## Required validation

```bash
python -m pytest -q tests/test_alignment.py
python -m pytest -q
```

## Conflict rules

- If a change appears to require model semantics, stop and hand off to `NANO-MODEL-001`.
- Do not add new data formats here; phase 5 owns production alignment schemas.

## Completion evidence

```text
Status: PASS
Owner: Codex
Files changed: tests/test_alignment.py; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_alignment.py
- .venv/bin/python -m pytest -q
Results:
- SFT mask and DPO response-only tests passed.
- Full test suite passed during Nano closeout: 25 passed in 2.82s.
Known risks: alignment code remains a CPU reference loop, not a production alignment pipeline.
Next allowed tasks: NANO-EXP-001, NANO-PUBLISH-001 and NANO-CLOSE-001 are now PASS.
```
