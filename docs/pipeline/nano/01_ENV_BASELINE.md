# Nano task - Environment baseline

Task ID: `NANO-ENV-001`

Status: PASS
Owner: Codex
Started: 2026-10-12
Finished: 2026-10-12

## Goal

Make the Nano development path reproducible enough that other model agents can run the same tests and smoke commands.

## Dependencies

None. This is the first Nano task.

## Allowed write set

- `README.md`
- `.gitignore`
- `docs/pipeline/nano/01_ENV_BASELINE.md`
- Optional: `docs/DEVELOPMENT.md`
- Optional: `pyproject.toml` only for missing dev dependencies required by existing code/tests.

## Do not touch

- `achitic/model.py`
- `achitic/train.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py`
- Generated checkpoint artifacts.

## Checklist

- [x] Document Python version target and install command.
- [x] Confirm install command includes `torch`, `sentencepiece`, and `pytest`.
- [x] Separate optional export dependency from Nano dependencies.
- [x] Add exact Nano verification command list.
- [x] Verify `python -m pytest -q` command is documented.

## Required validation

```bash
python -c "import torch, sentencepiece, pytest; print('nano deps ok')"
python -m pytest -q
```

If dependencies are unavailable, mark `Status: BLOCKED` and record the missing packages. Do not mark PASS.

## Completion evidence

```text
Status: PASS
Owner: Codex
Files changed: README.md; docs/DEVELOPMENT.md; docs/pipeline/nano/01_ENV_BASELINE.md; docs/pipeline/task_nano.md
Commands run:
- python -m venv .venv
- .venv/bin/pip install -e '.[dev]'
- python -c "import torch, sentencepiece, pytest; print('nano deps ok')"
- python -m pytest -q
- .venv/bin/python -c "import torch, sentencepiece, pytest; print('nano deps ok')"
- .venv/bin/python -m pytest -q
- .venv/bin/python -c "import torch, sentencepiece, pytest; print versions"
Results:
- initial system Python check failed because torch, sentencepiece and pytest were missing
- venv install succeeded
- dependency import passed: nano deps ok
- pytest passed: 2 passed in 11.01s
- versions: torch 2.14.1+cu130; sentencepiece 0.2.2; pytest 9.1.1
Blocked by: none.
Next allowed tasks: NANO-MODEL-001, NANO-CKPT-001, NANO-DATA-001 and NANO-EXP-001 may be claimed according to file locks.
```
