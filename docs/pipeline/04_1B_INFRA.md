# Phase 4 - 1B-class infrastructure

Dependency: `03_PRETRAIN_SCALE.md` must have `Status: PASS` through the 350M-class gate.

Không launch 1B-class training nếu chưa có sharding, streaming data, optimizer-state plan, budget và failure recovery. DDP hiện tại chỉ replicate full model, không đủ để gọi là 1B training system.

## Mục tiêu

Chuẩn bị hạ tầng để train model xấp xỉ 1B tham số một cách có thể resume, audit, và tái lập. Phase này ưu tiên correctness và recoverability trước tốc độ.

## Task checklist

- `INF-001`: Recalibrate `configs/1b.json` để đạt target thật hoặc đổi label nếu giữ khoảng 668M params.
- `INF-002`: Chọn và implement sharding strategy: FSDP2 hoặc equivalent sharded optimizer/model state.
- `INF-003`: Thiết kế checkpoint sharded: model, optimizer, scheduler, scaler, RNG, data cursor, tokenizer/config checksums.
- `INF-004`: Thêm dataset streaming/shards thay vì memmap đơn nếu corpus vượt local RAM/storage workflow.
- `INF-005`: Thêm scheduled eval không phá train loop và lưu metrics theo step/token.
- `INF-006`: Thêm fault recovery drill: kill/restart từ checkpoint gần nhất, verify metrics tiếp tục hợp lý.
- `INF-007`: Lập budget compute/storage/network. Ghi rõ GPU type, hours, batch, context, tokens target.
- `INF-008`: Thêm dry-run Nano FSDP/sharding test trên CPU hoặc GPU nhỏ.
- `INF-009`: Thêm security note cho checkpoint loading vì `torch.load(..., weights_only=False)` chỉ nên dùng với artifact tin cậy.
- `INF-010`: Tạo release checklist cho 1B-class checkpoint, gồm artifact manifest và eval report.

## Exit gates

Phase này chỉ PASS khi có evidence:

- Param count của 1B-class config được tính bằng code.
- Sharded training dry run pass.
- Checkpoint resume pass sau fault recovery drill.
- Scheduled eval chạy và metrics được lưu.
- Budget được duyệt trước full run.
- Security note cho checkpoint loading được document.
- Không gọi 4GB VRAM là train target. 4GB chỉ là quantized inference target.

## Suggested split cho nhiều model

- Model A: config/param/memory planning.
- Model B: FSDP2/sharding implementation.
- Model C: streaming dataset và cursor resume.
- Model D: checkpoint/fault recovery.
- Model E: eval scheduling, budget, security docs.

Người chốt phase phải tự chạy hoặc xác nhận evidence từ hạ tầng thật. Log khởi động thành công không đủ để PASS.

## Phase Closeout

```text
Status: NOT_STARTED
Closed by:
Date:
Commit or artifact ref:
Evidence:
- pytest:
- Nano smoke train:
- sharded dry run:
- fault recovery:
- scheduled eval:
- budget:
Notes:
```
