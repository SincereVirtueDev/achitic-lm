# Fixed Evaluation Prompts

Status: ACTIVE_SMOKE_SET

Owner: SincereVirtueDev

Last updated: 2026-10-13

## Purpose

These prompts provide a stable sample harness for Nano/Tiny smoke reports. They are not a benchmark, not a safety eval and not evidence of production quality.

## Prompt File

Use `docs/eval/fixed_prompts.jsonl`.

Each row is JSON Lines with:

- `id`
- `language`
- `prompt`

Current coverage:

- Vietnamese general explanation.
- English tokenizer explanation.
- Small Python code generation prompt.

## Usage

```bash
.venv/bin/python -m achitic.cli sample-report \
  --checkpoint <checkpoint.pt> \
  --tokenizer <tokenizer.model> \
  --prompts docs/eval/fixed_prompts.jsonl \
  --tokens 32 \
  --device cpu \
  --out <samples.jsonl>
```

Rules:

- Keep this file out of training data.
- Do not use these samples to claim model quality.
- Store outputs with checkpoint, tokenizer and dataset manifest references.
