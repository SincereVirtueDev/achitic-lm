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

| Config | Ladder role | Approx params | Note |
| --- | --- | ---: | --- |
| `configs/nano.json` | Nano | 4,999,424 | Smoke/pipeline target, xấp xỉ 5M |
| `configs/tiny.json` | Tiny | 23,058,944 | CPU 20-30M target |
| `configs/50m.json` | Legacy 50M label | 30,745,088 | Cần calibrate trước khi dùng làm Mini |
| `configs/150m.json` | Legacy 150M label | 92,769,024 | Cần calibrate trước khi dùng làm Small |
| `configs/350m.json` | 350M-class candidate | 258,253,824 | Cần calibrate |
| `configs/1b.json` | 1B-class candidate | 668,345,856 | Cần calibrate hoặc đổi label |

## Gate order

1. Nano PASS: tests, tokenizer smoke, train smoke, checkpoint, alignment CPU guard, export claim guard.
2. Data/tokenizer PASS: provenance, license, privacy, dedup, contamination, frozen tokenizer.
3. Tiny PASS: 20-30M CPU config, train/eval/sample report, artifact manifest.
4. Mini/Small PASS: scale experiments with metrics and stability evidence.
5. 350M/1B PASS: GPU/sharding infrastructure, scheduled eval, recovery drill, budget.

Không được dùng kết quả Nano để claim chất lượng Tiny. Nano chỉ chứng minh pipeline và contract hoạt động.
