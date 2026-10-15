# AchiticLM model ladder

Mục tiêu của ladder này là thêm Nano trước Tiny mà không đổi kiến trúc. Tất cả kích cỡ dùng cùng `AchiticLM Core`: Transformer decoder-only, GQA, RoPE, RMSNorm, SwiGLU, tied embedding/output. Khác biệt nằm ở config, backend thực thi, dữ liệu và gate.

## Core and backends

```text
AchiticLM Core
Transformer - GQA - RoPE - RMSNorm - SwiGLU
        |
        v
CPU Backend                         GPU Backend
Nano / Tiny / Mini / Small          Mini / Small / 350M / 1B
FP32, BF16 neu ho tro, CPU threads  CUDA, DDP, AMP, sharding khi can
        |
        v
Unified Checkpoint & Inference
Mot kien truc, nhieu cau hinh va thiet bi thuc thi
```

## CPU model targets

| Version | Target params | Config | Estimated RAM train | Mục đích |
| --- | ---: | --- | ---: | --- |
| Nano | 5-10M | `configs/nano.json` | 1-2GB | Test pipeline |
| Tiny | 20-30M | `configs/tiny.json` | 2-4GB | Học ngôn ngữ cơ bản |
| Mini | ~50M | pending calibrated config | 4-8GB | Pretraining thực nghiệm |
| Small | ~150M | pending calibrated config | 8-16GB+ | Huấn luyện CPU dài hạn hoặc GPU nhỏ |

RAM thực tế phụ thuộc batch size, context, dtype, optimizer và worker. Các mức này là dự toán, không phải benchmark đã đo.

## Current config estimates

Các số dưới đây tính theo công thức tham số trong `achitic/model.py`; trước run lớn phải xác nhận lại bằng `sum(p.numel() for p in model.parameters())`.

| Config | Ladder role | Measured params | Rounded | Label status | Note |
| --- | --- | ---: | ---: | --- | --- |
| `configs/nano.json` | Nano | 4,999,424 | 5.0M | OK | Smoke/pipeline target, xấp xỉ 5M |
| `configs/tiny.json` | Tiny | 23,058,944 | 23.1M | OK | CPU 20-30M target |
| `configs/50m.json` | Legacy 50M alias | 30,745,088 | 30.7M | WARN | Deprecated label for Mini experiments; supersede before claiming 50M |
| `configs/150m.json` | Legacy 150M alias | 92,769,024 | 92.8M | WARN | Deprecated label for Small experiments; supersede before claiming 150M |
| `configs/350m.json` | 350M-class candidate alias | 258,253,824 | 258.3M | WARN | Candidate only; supersede or relabel before a 350M release |
| `configs/1b.json` | 1B-class candidate alias | 668,345,856 | 668.3M | WARN | Candidate only; supersede or relabel before a 1B release |

## Legacy alias policy

- `configs/nano.json` and `configs/tiny.json` are active CPU target configs. Nano is accepted as an approximate 5M smoke target because it is within 1,000 parameters of 5M; Tiny is inside the 20-30M CPU target band.
- `configs/50m.json`, `configs/150m.json`, `configs/350m.json` and `configs/1b.json` are legacy or candidate aliases, not verified size claims. Their filenames are kept so old docs, scripts and checkpoints can still resolve them.
- Do not rename or mutate a config that has released checkpoint evidence in place. Add a new calibrated config filename, document the migration and regenerate tokenizer/config/checkpoint/manifest/checksum evidence together.
- A future Mini/Small/350M/1B release must use measured parameter counts in its model card. If the rounded target in the release name differs materially from the measured count, treat the old filename as deprecated and record the successor config.

Tokenizer strategy for Tiny: keep `configs/tiny.json` at `vocab_size=12000` and train/freeze a new audited Tiny tokenizer from the Data/Tokenizer gate. Do not reuse the Nano release tokenizer (`8000`) for Tiny unless Tiny is intentionally recalibrated and every config/checkpoint/tokenizer document is updated together.

## Gate order

1. Nano PASS: tests, tokenizer smoke, train smoke, checkpoint, alignment CPU guard, export claim guard.
2. Data/tokenizer PASS: provenance, license, privacy, dedup, contamination, frozen tokenizer.
3. Tiny PASS: 20-30M CPU config, train/eval/sample report, artifact manifest.
4. Mini/Small PASS: scale experiments with metrics and stability evidence.
5. 350M/1B PASS: GPU/sharding infrastructure, scheduled eval, recovery drill, budget.

Không được dùng kết quả Nano để claim chất lượng Tiny. Nano chỉ chứng minh pipeline và contract hoạt động.
