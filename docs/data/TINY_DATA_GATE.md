# Tiny Data And Tokenizer Gate

Status: BLOCKED_NO_APPROVED_TINY_CORPUS

Owner: SincereVirtueDev

Last updated: 2026-10-13

## Gate Objective

Make the Tiny data path auditable before any Tiny checkpoint is trained. This gate is about evidence, not model quality claims.

## Accepted Input States

| State | Meaning | Training allowed |
| --- | --- | --- |
| `CANDIDATE` | Source is proposed but not audited | No |
| `QUARANTINED` | Source failed privacy/license/provenance scan | No |
| `APPROVED_TRAIN` | Source passed provenance, license, privacy and dedup checks for training | Yes |
| `APPROVED_EVAL` | Source passed checks and is reserved for held-out eval | Eval only |
| `SMOKE_ONLY` | Source is allowed only for pipeline smoke | No Tiny train/eval claims |

## Required Procedure

1. Add candidate sources to `docs/data/tiny_dataset_manifest.json`.
2. Record raw SHA-256 and normalized SHA-256.
3. Run privacy scan rules.
4. Run exact dedup on normalized documents.
5. Create deterministic train/eval split.
6. Run contamination checks between train and eval.
7. Train SentencePiece BPE tokenizer with vocab size `12000`.
8. Audit tokenizer special IDs, roundtrip behavior and vocab/config match.
9. Record token counts by source and split.
10. Close `docs/pipeline/02_DATA_TOKENIZER.md` only after every evidence item is present.

Use `scripts/split_val.py` for smoke and candidate line-level split evidence:

```bash
.venv/bin/python scripts/split_val.py --input examples/corpus.txt --train-out /tmp/train.txt --val-out /tmp/val.txt --val-ratio 0.2 --seed achitic
```

Agents must not fetch internet datasets, invent data provenance, or silently promote `SMOKE_ONLY` data into Tiny training/eval approval. Every non-smoke source must enter the manifest before it can be used.

## Privacy Scan Rules

| Rule ID | Detection target | Required action |
| --- | --- | --- |
| `PII_EMAIL` | Email-like strings | Drop or quarantine document |
| `PII_PHONE` | Phone-like strings with separators or country code | Drop or quarantine document |
| `SECRET_API_KEY` | API keys, bearer tokens, private keys, password assignments | Drop document and review source |
| `PII_ADDRESS` | Street-address-like private location data | Quarantine for manual review |
| `PRIVATE_CONVERSATION` | Private chat, support, email or DM exports | Reject unless explicit compatible rights exist |

## Dedup Rules

- Normalize each document with NFC, NUL removal and whitespace collapse.
- Compute `sha256(normalized_text)`.
- Keep the first accepted document per hash.
- Record duplicate count by source.
- For corpora above smoke scale, add near-dedup shingle or MinHash report before long Tiny runs.

## Contamination Rules

- Train/eval exact document hash intersection must be empty.
- Eval n-grams or shingles must be checked against train before reporting held-out perplexity.
- Any fixed benchmark prompt must be stored as prompt metadata, not mixed into training text.

## Tokenizer Rules

- Train only on cleaned approved train split.
- Use SentencePiece BPE with byte fallback.
- Freeze IDs: `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Tiny target vocab: `12000`.
- Save tokenizer checksum before any Tiny checkpoint training.
- If tokenizer vocab differs from `configs/tiny.json`, training is blocked.

## Current Blockers

- No approved Tiny train corpus has been added.
- No approved Tiny eval split has been added.
- Tiny tokenizer `12000` has not been trained or audited.
