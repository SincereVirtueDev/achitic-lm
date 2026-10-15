# AchiticLM Nano v0.2.0 Eval Report

Status: RELEASE_ARTIFACT

## Validation Summary

| Check | Result |
| --- | --- |
| Full pytest | `91 passed, 1 skipped` |
| Packaged full-checkpoint sample report | `10/10` automatic PASS |
| Manual meaningful-sentence review | `10/10` PASS |
| Reserved-token output | `0/10` |
| Tiny shared-path smoke train | PASS, `1` CPU step |
| Full checkpoint chat | PASS |
| FP16 safetensors chat | PASS |
| Checksum verification | PASS |

The one skipped test is the optional llama.cpp integration test. This package does
not include a GGUF or quantized artifact and makes no verification claim for one.

## Held-Out Language Modeling

| Candidate | Loss | Perplexity | Tokens |
| --- | ---: | ---: | ---: |
| Scratch pretraining checkpoint before SFT | `3.9901` | `54.06` | `73,600` |
| Packaged checkpoint after SFT | `4.5470` | `94.35` | `73,600` |

The SFT phase improved the controlled prompt behavior but degraded held-out
Wikipedia loss. This trade-off limits the candidate to meaning-smoke use.

## Meaning Smoke

The deterministic report uses 10 fixed Vietnamese prompts, greedy decoding, the
Achitic chat template and at most 32 new tokens. Every output passed the automatic
length, boundary, repetition and reserved-token checks and manual relevance review.

See `MEANING_SMOKE_REPORT.md` for every prompt and generated sentence.

## Claim Boundary

This report does not establish broad Vietnamese fluency, factuality, safety,
alignment generalization, benchmark quality or production readiness. The SFT data
contains close intent paraphrases of the fixed prompts.
