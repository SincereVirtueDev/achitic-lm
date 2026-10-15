# Phase 3 - Pretrain scale

Status: BLOCKED_WAITING_FOR_DATA_TOKENIZER

Last updated: 2026-10-13

Dependency: `02_DATA_TOKENIZER.md` must have `Status: PASS`.

Không chạy Tiny/Mini/Small/350M nếu tokenizer, data manifest và eval split chưa freeze. Không publish checkpoint nếu test/eval evidence thiếu.

## Mục tiêu

Scale từ Nano baseline sang Tiny, Mini/50M, Small/150M và 350M bằng dữ liệu đã audit. Mỗi cấp phải có số liệu loss, held-out perplexity, sample review, throughput, memory, checkpoint resume và artifact manifest.

## Config calibration

Trước khi launch run đắt tiền, phải tính lại tham số thật bằng model hiện tại. Các config hiện nay cần được kiểm tra trước khi dùng làm mốc:

- `configs/nano.json`: khoảng 5.0M params, chỉ dùng làm pipeline smoke.
- `configs/tiny.json`: khoảng 23.1M params, Tiny CPU target.
- `configs/50m.json`: khoảng 30.7M params, legacy label cần calibrate nếu dùng làm Mini.
- `configs/150m.json`: khoảng 92.8M params, legacy label cần calibrate nếu dùng làm Small.
- `configs/350m.json`: khoảng 258.3M params.
- `configs/1b.json`: khoảng 668.3M params.

Task scale đầu tiên phải quyết định: sửa config để gần label, hoặc đổi tên/label để phản ánh số thật. Không sửa `achitic/model.py` chỉ để đạt mốc tham số.

## UPG-MEM-001 Param And Memory Snapshot

Status: PASS_FOR_ESTIMATOR, PHASE_NOT_PASS

Owner: Codex

Date: 2026-10-13

Estimator command:

```bash
.venv/bin/python scripts/model_report.py --configs configs/nano.json configs/tiny.json configs/50m.json configs/150m.json configs/350m.json configs/1b.json --verify-threshold 50000000
```

Memory model: params + gradients + AdamW first/second moments + activation estimate + 20% overhead. This is a planning estimate, not a measured peak RSS benchmark.

| Config | Role | Params | Verified | Status | Context | Estimated train RAM | Recommended start |
| --- | --- | ---: | --- | --- | ---: | ---: | --- |
| `configs/nano.json` | Nano | 4,999,424 | yes | OK | 128 | 0.10 GiB | `batch=1, accum=16` |
| `configs/tiny.json` | Tiny | 23,058,944 | yes | OK | 512 | 0.50 GiB | `batch=1, accum=4` |
| `configs/50m.json` | 50M | 30,745,088 | yes | WARN | 1024 | 0.77 GiB | `batch=1, accum=2` |
| `configs/150m.json` | 150M | 92,769,024 | skipped | WARN | 2048 | 2.67 GiB | `batch=1, accum=4` |
| `configs/350m.json` | 350M | 258,253,824 | skipped | WARN | 4096 | 9.12 GiB | `batch=1, accum>=8; reduce context/model or add memory before long runs` |
| `configs/1b.json` | 1B | 668,345,856 | skipped | WARN | 4096 | 20.05 GiB | `batch=1, accum>=8; reduce context/model or add memory before long runs` |

Warnings:

- `configs/50m.json` label target is 50,000,000; actual params are 30,745,088 (-38.5%).
- `configs/150m.json` label target is 150,000,000; actual params are 92,769,024 (-38.2%).
- `configs/350m.json` label target is 350,000,000; actual params are 258,253,824 (-26.2%).
- `configs/1b.json` label target is 1,000,000,000; actual params are 668,345,856 (-33.2%).

Tiny CPU note:

- Tiny fits the 20-30M target and the initial CPU memory plan at batch 1, accumulation 4.
- This does not unlock Tiny training; Phase 2 still needs approved data, held-out eval and a 12k tokenizer.
- Large config verification was skipped intentionally to avoid allocating hundreds of millions of parameters during a reporting command.

## Task checklist

- `TRN-001`: DONE_BY_UPG_MEM_001. `scripts/model_report.py` reports params and estimates memory by dtype, optimizer state, batch, context.
- `TRN-002`: Bổ sung eval loop held-out perplexity vào train hoặc CLI eval riêng.
- `TRN-003`: Bổ sung logging ổn định: train loss, eval loss, lr, tokens seen, tokens/sec, grad norm, peak memory.
- `TRN-004`: Làm rõ resume semantics. Nếu cần exact resume, lưu data cursor/sampler epoch và batch offset.
- `TRN-005`: Thêm learning-rate schedule, warmup, weight decay policy và config hóa thay vì hard-code.
- `TRN-006`: Thêm AMP/grad scaler policy cho CUDA, giữ CPU fallback.
- `TRN-007`: Cải thiện packing hoặc sampling để giảm waste khi corpus lớn.
- `TRN-008`: DDP sanity test trên CPU/Gloo hoặc documented local two-process smoke nếu khả thi.
- `TRN-009`: Thiết lập sample review fixed prompts Vietnamese/English/code.
- `TRN-010`: Tạo artifact manifest cho mỗi checkpoint: config, tokenizer checksum, dataset manifest checksum, git/ref, command, hardware, metrics.

## Stage gates

### Tiny CPU gate

- Nano closeout PASS.
- Data/tokenizer phase PASS.
- `configs/tiny.json` trong target 20-30M và vocab size khớp tokenizer.
- Train/eval/sample report có artifact manifest.
- Nano smoke vẫn pass sau mọi thay đổi train/eval.

### 50M-class gate

- Tiny CPU gate PASS.
- Param count và label đã khớp hoặc đã document mismatch.
- Train chạy qua smoke dài hơn Nano, có eval perplexity.
- Loss giảm trên overfit corpus và không NaN.
- Resume checkpoint load được.
- Sample fixed prompts được lưu, không claim chất lượng chat.

### 150M-class gate

- 50M-class gate PASS.
- Throughput và memory đủ dự báo cho 150M.
- Eval loss/perplexity tốt hơn baseline hoặc có phân tích nguyên nhân.
- Dataset language balance report được cập nhật.
- Checkpoint artifact manifest đầy đủ.

### 350M-class gate

- 150M-class gate PASS.
- Có stability report: NaN/grad spike/restart/resume.
- Có eval Vietnamese QA, English, code tối thiểu bằng prompt set cố định.
- Có risk note về hallucination và safety. Không claim production.
- Có kế hoạch compute/storage trước khi chuyển 1B infra.

## Suggested split cho nhiều model

- Model A: param/memory estimator và config calibration.
- Model B: eval loop và metrics logging.
- Model C: resume/data cursor semantics.
- Model D: DDP/AMP/schedule.
- Model E: artifact manifest và sample review harness.

Người chốt phase phải chạy lại test ladder và kiểm tra artifact manifest của từng checkpoint.

## Phase Closeout

```text
Status: BLOCKED_WAITING_FOR_DATA_TOKENIZER
Closed by: not closed
Date: 2026-10-13
Commit or artifact ref:
Evidence:
- pytest: UPG-MEM-001 full suite passed, 28 tests
- Nano smoke train: prepare/tokenizer/encode/train/chat passed from /tmp artifacts
- Tiny CPU gate: config and memory estimator pass; train/eval still blocked by Phase 2 data/tokenizer
- 50M gate: label mismatch warning exists, actual params 30,745,088
- 150M gate: label mismatch warning exists, actual params 92,769,024
- 350M gate: label mismatch warning exists, actual params 258,253,824
- artifact manifest: pending train/eval tasks
Notes: TRN-001 is complete through UPG-MEM-001. Full phase remains blocked until data/tokenizer, eval, logging, resume and train artifact tasks pass.
```
