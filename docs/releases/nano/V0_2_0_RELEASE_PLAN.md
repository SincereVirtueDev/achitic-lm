# AchiticLM Nano v0.2.0 Release Plan

Status: PUBLISHED_PRERELEASE

Release tag target: `nano-v0.2.0`

Package directory: `releases/nano-v0.2.0/`

## Purpose

Nano v0.2.0 is a scratch-trained engineering baseline with a controlled Vietnamese
meaning-smoke behavior. It closes the audited data/tokenizer/train/alignment/package
path needed before larger roadmap models reuse the same implementation.

It is not a broad language-quality, factuality, safety or production release.

## Included

- Full `nano.pt` SFT checkpoint and FP16 weights-only safetensors.
- Exact `8000`-token tokenizer and Nano config.
- Sanitized training manifest, model card, evaluation/meaning reports, usage,
  security, notice, ISO-aligned spec and checksums.
- Attribution for the Vietnamese Wikipedia source.

## Excluded

- Raw and cleaned training/eval text.
- GGUF and quantized artifacts.
- Credentials, private data and local machine paths.
- General quality, factuality, safety or benchmark claims.

## Gate Summary

| Row | Status | Evidence |
| --- | --- | --- |
| `NANO-X-EXPORT-001` through `NANO-X-PKG-001` | PASS | Original audited engineering baseline |
| Merged audit implementation addendum | PASS | Prepare, stream, config, alignment and quant guards |
| `NANO-MEAN-001` | PASS | Real-corpus provenance plus `10/10` controlled review |
| `NANO-X-RETRAIN-001` | PASS | Refreshed coherent tokenizer/config/checkpoint/package |
| `NANO-X-PUBLISH-001` | PASS | Public prerelease has 19 digest-verified assets |

## Publication Rule

The exact package passed `SHA256SUMS`, secret/private-path scan, full pytest, full
and weights-only sample reports, and checkpoint/tokenizer/config consistency
checks before publication.

Published release:

`https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.2.0`

See `V0_2_0_PUBLICATION.md` for immutable commit, tag, asset and digest evidence.
