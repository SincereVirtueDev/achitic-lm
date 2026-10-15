# AchiticLM Nano v0.2.0 Release Notes

Status: RELEASE_ARTIFACT

Nano v0.2.0 refreshes the engineering baseline and adds a controlled Vietnamese
meaning-smoke candidate before the Tiny roadmap stage.

## Added

- Scratch pretraining on a bounded, cleaned Vietnamese Wikipedia shard.
- New `8000`-token tokenizer with `0` reserved-padding ratio.
- Project-authored 80-row SFT supplement and automatic Achitic chat template.
- Deterministic 10-prompt report with `10/10` automatic and manual PASS.
- Sanitized training manifest, data provenance, privacy/dedup/contamination notes.
- Refreshed full checkpoint, FP16 safetensors artifact and package checksums.

## Validation

- Full tests: `91 passed, 1 skipped`.
- Tiny shared train path: PASS for one CPU step.
- Packaged full and weights-only inference: PASS.
- Post-SFT held-out loss/perplexity: `4.5470` / `94.35`.

## Limits

The 10 prompts are close to SFT intents, and post-SFT held-out loss is worse than
the pre-SFT checkpoint. This release proves a controlled pipeline behavior only.
No broad quality, factuality, safety, production, GGUF or quantization claim is
made.
