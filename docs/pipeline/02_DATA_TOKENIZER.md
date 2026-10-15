# Phase 2 - Data and tokenizer

Status: BLOCKED_NO_APPROVED_TINY_CORPUS

Last updated: 2026-10-13

Dependency: `01_FOUNDATION_SMOKE.md` must have `Status: PASS`.

Không train scale model nếu phase này chưa PASS. Dataset và tokenizer là contract dài hạn của checkpoint, nên mọi thay đổi phải có manifest và lý do rõ.

## Mục tiêu

Xây dựng corpus Vietnamese/English hợp pháp, sạch PII, có held-out eval tách biệt, có dedup và contamination check. Tokenizer được train từ corpus đã audit và vocab size phải khớp config của run.

## Scope được phép

- Dataset manifest, data card, cleaning pipeline, dedup, split train/eval.
- Tokenizer training và tokenizer audit.
- Eval corpus cố định cho perplexity và sample review.
- Không dùng dữ liệu không rõ license. Không đưa dữ liệu private/PII vào repo.

## Task checklist

- `DAT-001`: Tạo `docs/DATASET_CARD.md` với source, license, ngôn ngữ, khối lượng, ngày snapshot, privacy policy, và owner.
- `DAT-002`: Tạo manifest máy đọc được cho từng source, gồm URL/path nội bộ, license, checksum, split policy, loại dữ liệu, và allowed use.
- `DAT-003`: Bổ sung PII/privacy scan. Ghi rõ rule loại bỏ email, phone, token/API key, private conversation, personal address nếu có.
- `DAT-004`: Bổ sung exact dedup report và kế hoạch near-dedup nếu corpus lớn.
- `DAT-005`: Thiết lập train/eval split bằng checksum hoặc deterministic hash. Eval split không được leak vào train.
- `DAT-006`: Thêm contamination check giữa train và eval, ít nhất exact overlap và n-gram/document hash overlap.
- `DAT-007`: Train tokenizer từ cleaned train corpus. Ghi lại vocab size, special IDs, byte fallback, command, checksum `.model`.
- `DAT-008`: Tokenizer audit: roundtrip samples Vietnamese dấu, English, code, số, ký tự lạ, byte fallback.
- `DAT-009`: Token count report theo source và theo split. Cảnh báo nếu token count không đủ cho config context.
- `DAT-010`: Freeze tokenizer cho phase train. Sau khi freeze, đổi tokenizer là breaking checkpoint contract.

## UPG-DAT-001 Gate Snapshot

Status: PASS_FOR_AUDIT_PLAN, PHASE_NOT_PASS

Owner: Codex

Date: 2026-10-13

Evidence package:

- Dataset card: `docs/DATASET_CARD.md`
- Machine-readable manifest: `docs/data/tiny_dataset_manifest.json`
- Gate procedure: `docs/data/TINY_DATA_GATE.md`
- Reference smoke source checksum: `examples/corpus.txt` -> `7c1eaf73846dd770ed4d2137f3ca379100bb71e8b753ac99150070293825bac8`
- Manifest checksum: `60f9d31e5a70da2f488fbd3b9faad7fff0013816eeebf9bae6cf329e0df2c90c`
- Validation: manifest JSON parsed successfully, `pytest -q` passed, and Nano smoke prepare/tokenizer/encode/train/chat plus checkpoint/tokenizer vocab check passed from `/tmp` artifacts.

Current gate status:

| Item | Status | Notes |
| --- | --- | --- |
| `DAT-001` dataset card | DONE | `docs/DATASET_CARD.md` created |
| `DAT-002` manifest | DONE | `docs/data/tiny_dataset_manifest.json` validates as JSON |
| `DAT-003` privacy scan rules | DONE | Email, phone, token/API key, address and private conversation rules recorded |
| `DAT-004` dedup plan | DONE | Exact normalized SHA-256 dedup required; near-dedup required before long Tiny runs |
| `DAT-005` split policy | DONE | Deterministic hash buckets recorded |
| `DAT-006` contamination plan | DONE | Exact document hash and n-gram/shingle overlap checks required |
| `DAT-007` tokenizer train | BLOCKED | No approved Tiny train corpus yet |
| `DAT-008` tokenizer audit | BLOCKED | Waits for tokenizer train |
| `DAT-009` token count report | BLOCKED | Waits for approved train/eval sources |
| `DAT-010` freeze tokenizer | BLOCKED | Waits for 12k tokenizer audit |

Tiny-specific tokenizer decision:

- `configs/tiny.json` requires `vocab_size=12000`.
- Required special IDs remain `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Nano release tokenizer (`8000`) is smoke-only and must not be reused for Tiny.

Blocking items before Phase 2 can become `PASS`:

- Add at least one approved Tiny train source with provenance, license, rights owner, snapshot date, checksum and allowed use.
- Add a held-out Tiny eval source or deterministic eval split that remains disjoint from train.
- Run privacy/dedup/contamination checks and record reports.
- Train and audit a 12k tokenizer from the cleaned approved train split.
- Record tokenizer checksum and token counts by source/split.

## Exit gates

Phase này chỉ PASS khi có evidence:

- Dataset card và manifest đầy đủ.
- Mọi source có provenance và license hợp lệ cho mục đích train/eval.
- Privacy scan hoàn tất, không có PII/blocker chưa xử lý.
- Train/eval split có checksum và contamination report.
- Tokenizer vocab size khớp config dự kiến.
- Tokenizer special IDs: `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Smoke encode chạy được và `TokenDataset` không lỗi `not enough tokens`.

## Suggested split cho nhiều model

- Model A: dataset card và manifest schema.
- Model B: privacy/dedup/contamination checks.
- Model C: tokenizer train và audit.
- Model D: token statistics và eval split validation.

Người chốt phase phải verify lại các checksum và không dựa vào log rời rạc.

## Phase Closeout

```text
Status: BLOCKED_NO_APPROVED_TINY_CORPUS
Closed by: not closed
Date: 2026-10-13
Commit or artifact ref:
Evidence:
- dataset card: docs/DATASET_CARD.md
- manifest checksum: 60f9d31e5a70da2f488fbd3b9faad7fff0013816eeebf9bae6cf329e0df2c90c
- privacy/dedup/contamination: docs/data/TINY_DATA_GATE.md and docs/data/tiny_dataset_manifest.json
- tokenizer checksum: BLOCKED, no Tiny tokenizer trained yet
- encode smoke: Nano smoke passed from `/tmp` artifacts; Tiny encode smoke remains BLOCKED until approved corpus and tokenizer exist
Notes: UPG-DAT-001 completed the audit plan and blockers. Full Phase 2 remains blocked until real Tiny train/eval data and a 12k tokenizer are produced.
```
