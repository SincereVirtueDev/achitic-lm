# AchiticLM Nano v0.2.0 Retrain Decision

Date: 2026-10-15

Owning task: `NANO-X-RETRAIN-001`

Status: `PASS_LOCAL_CANDIDATE_REFRESHED`

## Decision

The local, unpublished `nano-v0.2.0` candidate has been replaced as one complete
artifact contract. `nano-v0.2.1` and `nano-v0.3.0` are not needed because no public
v0.2.0 tag or release was mutated.

The refreshed candidate uses a new `8000`-token tokenizer, a scratch-pretrained
Nano checkpoint and an `800`-step project-authored SFT stage. Nano v0.1.x artifacts
remain untouched.

## Data Decision

- Pretraining source: first Vietnamese Wikipedia `2026-10-01` article-dump shard.
- Clean split: `97,978` train and `2,022` held-out sentences.
- Fixed-prompt contamination: `0` normalized matches.
- SFT: `80` project-authored rows, with close intent paraphrases disclosed.
- Raw and cleaned Wikipedia text: local only, absent from Git and release assets.

Provenance, source checksum, license, privacy heuristics, dedup and split evidence
are in `docs/data/NANO_MEANING_DATASET_CARD.md` and
`docs/data/nano_meaning_corpus_manifest.json`.

## Candidate Result

- Parameters/config: `4,999,424`, vocabulary `8000`, context `128`.
- Scratch pretraining: `5000` CPU FP32 steps.
- Alignment: `800` SFT steps; checkpoint stage `sft`.
- Controlled meaning smoke: `10/10` automatic and manual PASS.
- Reserved-token output: `0/10`.
- Post-SFT held-out loss/perplexity: `4.5470` / `94.35`, worse than pre-SFT.
- GGUF/quantized assets: excluded.

The held-out regression and near-domain SFT/eval relationship prevent any broad
quality claim. The candidate is suitable only for controlled pipeline evaluation.

## Next Action

`NANO-X-PUBLISH-001` may inspect and publish this exact checksum-verified candidate,
or explicitly defer publication. Any further weight/tokenizer/config change requires
new checksums and full gate execution.
