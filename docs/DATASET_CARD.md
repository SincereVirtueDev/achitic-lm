# AchiticLM Tiny Dataset Card

Status: BLOCKED_NO_APPROVED_TINY_CORPUS

Owner: SincereVirtueDev

Last updated: 2026-10-13

Applies to: `configs/tiny.json`, `docs/pipeline/02_DATA_TOKENIZER.md`, `docs/pipeline/task_upgrade_tiny.md`

## Purpose

This card defines the data and tokenizer gate for AchiticLM Tiny. Tiny must not train or publish a checkpoint until every training/evaluation source has provenance, license, privacy, deduplication and contamination evidence.

Nano release data remains smoke-only evidence. It proves the local pipeline runs; it is not an approved Tiny pretraining corpus.

## Current Source Inventory

| Source ID | Path or URL | Language | Size | Snapshot date | License | Owner | Allowed use | Tiny train/eval status |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| `achitic-example-corpus-v0` | `examples/corpus.txt` | Vietnamese | 6 lines, 110 words, 655 bytes | 2026-10-13 repo snapshot | Apache-2.0 compatible, self-authored synthetic/example corpus | SincereVirtueDev | Nano/pipeline smoke only | NOT_APPROVED_FOR_TINY |

Approved Tiny train sources: none yet.

Approved Tiny eval sources: none yet.

## Required Source Fields

Every candidate source must be added to `docs/data/tiny_dataset_manifest.json` before it can be used:

- `source_id`
- `path_or_url`
- `provenance`
- `license`
- `license_url_or_file`
- `rights_owner`
- `language`
- `snapshot_date`
- `raw_sha256`
- `normalized_sha256`
- `line_count`
- `byte_count`
- `allowed_use`
- `privacy_scan_status`
- `dedup_status`
- `contamination_status`
- `split_policy`

Sources with missing license, unclear provenance, private data, credentials, non-consented conversations, or unresolved PII are rejected.

## Privacy Policy

Drop or quarantine any document containing:

- Email addresses.
- Phone numbers.
- API keys, bearer tokens, private keys, passwords or credential-like strings.
- Personal street addresses.
- Private chat logs, support tickets, DM exports, emails or documents not explicitly cleared for model training.
- Copyrighted or proprietary text without a compatible training/evaluation grant.

No quarantined data may be committed to the repository or included in release artifacts.

## Deduplication Policy

Normalization before hashing must match the repo cleaner where possible: NFC Unicode normalization, NUL removal, whitespace collapse and trim.

Required checks:

- Exact document dedup by SHA-256 of normalized text.
- Duplicate report by source and split.
- Near-dedup plan for larger corpora using deterministic shingles or MinHash before long Tiny training.

## Split And Contamination Policy

Train/eval split must be deterministic and reproducible from normalized document hashes. Eval data must never leak into train.

Minimum checks:

- Exact overlap between train and eval normalized document hashes must be zero.
- N-gram or shingle overlap report must be produced before claiming held-out perplexity.
- Fixed sample prompts must be stored outside the training split or explicitly tagged as prompts only.

## Tiny Tokenizer Contract

Tiny uses a new tokenizer trained from the cleaned, approved Tiny train corpus:

- Tokenizer type: SentencePiece BPE.
- Target vocab size: `12000`.
- Required special IDs: `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Byte fallback: required.
- Nano tokenizer vocab `8000` must not be reused for Tiny.

Changing the Tiny tokenizer after checkpoint training is a breaking checkpoint-contract change.

## Gate Status

`UPG-DAT-001` may pass when the audit plan, manifest and blockers are explicit. The full Phase 2 data/tokenizer closeout remains blocked until approved Tiny train/eval sources exist and a 12k tokenizer is trained/audited from them.
