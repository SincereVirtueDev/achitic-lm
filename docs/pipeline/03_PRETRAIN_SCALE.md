# Phase 3 - Pretrain scale

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

## Task checklist

- `TRN-001`: Thêm script/report đếm params thật và estimate memory theo dtype, optimizer state, batch, context.
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
Status: NOT_STARTED
Closed by:
Date:
Commit or artifact ref:
Evidence:
- pytest:
- Nano smoke train:
- Tiny CPU gate:
- 50M gate:
- 150M gate:
- 350M gate:
- artifact manifest:
Notes:
```
