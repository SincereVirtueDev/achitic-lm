# Phase 2 - Data and tokenizer

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
Status: NOT_STARTED
Closed by:
Date:
Commit or artifact ref:
Evidence:
- dataset card:
- manifest checksum:
- privacy/dedup/contamination:
- tokenizer checksum:
- encode smoke:
Notes:
```
