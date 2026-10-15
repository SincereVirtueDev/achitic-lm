# AchiticLM Nano v0.2.0 Model Card

Status: RELEASE_ARTIFACT

## Model Summary

AchiticLM Nano is a small scratch-initialized decoder-only Transformer intended to
validate the AchiticLM data, tokenizer, training, alignment, checkpoint and
inference pipeline.

| Field | Value |
| --- | --- |
| Parameters | `4,999,424` |
| Vocabulary | `8000` |
| Context | `128` |
| Architecture | GQA, RoPE, RMSNorm, SwiGLU, tied embedding/output |
| Pretraining | `5000` CPU FP32 steps, about `10.24M` target tokens |
| Alignment | `800` SFT steps over `80` project-authored rows |
| Checkpoint stage/step | `sft` / `800` |
| Initialization | Scratch; no external pretrained weights |

## Training Data

Pretraining used `97,978` cleaned train sentences from the first Vietnamese
Wikipedia `2026-10-01` article-dump shard. A deterministic held-out split contains
`2,022` sentences. The raw and cleaned text are not included in the package.

The SFT supplement is self-authored for AchiticLM and contains close paraphrases of
the fixed evaluation intents. This makes the meaning test a controlled in-domain
smoke, not an independent benchmark. See `NOTICE`, `TRAINING_RUN_MANIFEST.json`
and the repository dataset card for provenance and filtering details.

## Measured Evidence

- Full tests: `91 passed, 1 skipped`.
- Fixed prompt automatic checks: `10/10` PASS.
- Fixed prompt manual meaningful-sentence review: `10/10` PASS.
- Reserved-token strings in reviewed outputs: `0/10`.
- Pre-SFT held-out Wikipedia loss/perplexity: `3.9901` / `54.06`.
- Post-SFT held-out Wikipedia loss/perplexity: `4.5470` / `94.35`.

The post-SFT loss regression is material: controlled instruction behavior improved
while broader held-out text modeling degraded.

## Intended Use

- Research, education and pipeline development.
- Controlled AchiticLM Nano evaluation.
- CPU checkpoint, tokenizer and inference smoke testing.
- Baseline engineering work before larger AchiticLM model slots.

## Unsupported Use

- Production chat, factual QA or broad Vietnamese generation claims.
- Safety-critical or high-stakes decisions.
- Deployment without independent quality, safety and domain validation.
- Treating the 10-prompt score as evidence of generalization.

## Limitations

The model is very small, has a `128`-token context, sees only part of Vietnamese
Wikipedia and is narrowly SFT-tuned. It may hallucinate, repeat, fail on reworded or
unseen requests, and produce unsafe or incorrect content. Privacy filtering is
heuristic. No factuality, safety, bias, benchmark or production evaluation exists.
