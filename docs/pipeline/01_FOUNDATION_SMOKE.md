# Phase 1 - Nano foundation and smoke

Dependency: `00_PIPELINE_CONTRACT.md`.

Không phase nào phía sau được nhận việc nếu file này chưa có `Phase Closeout` là `Status: PASS`.

## Nano task files

Phase này được tách nhỏ trong `docs/pipeline/nano/`. Đây là nguồn task cụ thể để nhiều model nhận việc mà không dẫm lên nhau:

- `docs/pipeline/nano/00_NANO_BOARD.md`: luật claim task, parallel group và Nano PASS definition.
- `docs/pipeline/nano/01_ENV_BASELINE.md`: môi trường dev và lệnh verify tối thiểu.
- `docs/pipeline/nano/02_MODEL_ROPE_GQA.md`: CPU tests cho model, causality, RoPE, GQA.
- `docs/pipeline/nano/03_CHECKPOINT_RESUME.md`: checkpoint save/load/resume semantics.
- `docs/pipeline/nano/04_DATA_TOKENIZER_CLI.md`: prepare/tokenizer/encode/train/chat smoke.
- `docs/pipeline/nano/05_ALIGNMENT_CPU.md`: SFT mask và DPO response-only tests.
- `docs/pipeline/nano/06_EXPORT_GUARD.md`: guard chống claim export/quantization khi chưa có llama.cpp.
- `docs/pipeline/nano/07_NANO_CLOSEOUT.md`: chốt Nano và mở khóa Tiny/phase 2.

Các task trong thư mục Nano có `Allowed write set` riêng. Nếu một task cần sửa ngoài vùng đó, task phải dừng ở `BLOCKED` hoặc phối hợp với owner liên quan trước khi sửa.

## Mục tiêu

Biến repo hiện tại thành baseline đáng tin: test CPU đủ phủ kiến trúc lõi, Nano smoke train chạy lặp lại được, checkpoint resume có bằng chứng, và không có claim vượt quá mức code đã verify.

## Scope được phép

- Test, script smoke, tài liệu dev workflow.
- Sửa lỗi nhỏ trong model/train/data/cli nếu test chứng minh bug.
- Thêm metadata checkpoint nếu giữ backward loading hoặc document breaking change rõ ràng.
- Không thay kiến trúc lớn, không đổi tokenizer IDs, không thêm pretrained artifact.

## Task checklist

- `FND-001`: Chuẩn hóa môi trường dev tối thiểu. Ghi rõ Python version, dependencies, optional export dependencies và command cài đặt.
- `FND-002`: Thêm CPU tests cho RoPE. Kiểm tra shape, dtype, tính causal không nhìn token tương lai, và behavior ổn định khi đổi suffix.
- `FND-003`: Thêm CPU tests cho GQA. Kiểm tra `heads % kv_heads == 0`, shape Q/K/V, lỗi config invalid.
- `FND-004`: Thêm checkpoint tests. Lưu, load, assert config khớp, state dict load được, optimizer/RNG có mặt.
- `FND-005`: Thêm resume smoke. Một run liên tục và một run resume phải có behavior được định nghĩa, ít nhất chứng minh checkpoint load không vỡ. Nếu muốn exact resume thì phải lưu data cursor/sampler state.
- `FND-006`: Thêm tokenizer/config mismatch test cho CLI hoặc loader. Vocab mismatch phải fail rõ.
- `FND-007`: Thêm Nano smoke script hoặc document command dùng config nhỏ đủ chạy trên CPU. Dataset phải có token count >= context + 1.
- `FND-008`: Thêm regression test cho SFT mask và DPO `sequence_logprob` nếu alignment tiếp tục nằm trong repo core.
- `FND-009`: Cập nhật docs để không ai claim GGUF/export/quant đã verify nếu chưa có llama.cpp generation.

## Exit gates

Phase này chỉ PASS khi có evidence:

- `pytest -q` pass.
- Nano prepare/tokenizer/encode/train/chat pass.
- Có test CPU cho causality, RoPE, GQA và checkpoint loading.
- Checkpoint format hiện tại được document. Nếu thay format, có migration note hoặc backward-compatible loader.
- Không có pretrained weight hoặc external model artifact được đưa vào repo.

## Suggested split cho nhiều model

- Model A: tests kiến trúc `model.py`.
- Model B: checkpoint/resume và train smoke.
- Model C: tokenizer/data/CLI smoke.
- Model D: docs và test command consolidation.

Các model này có thể chạy song song nếu không sửa cùng file. Người chốt phase phải gom lại và chạy toàn bộ exit gates.

## Phase Closeout

```text
Status: PASS
Closed by: Codex
Date: 2026-10-12
Commit or artifact ref: https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.0
Evidence:
- pytest: .venv/bin/python -m pytest -q -> 25 passed in 2.82s
- Nano smoke train: prepare 6 docs, tokenizer vocab 8000, encode 131 tokens, train runs/nano.pt step 3, chat smoke passed
- Release package: sha256sum -c releases/nano/SHA256SUMS passed; release chat smoke passed; GitHub Release nano-v0.1.0 published with 11 assets including INSTALL_USAGE.md
- RoPE/GQA/checkpoint tests: tests/test_model.py and tests/test_checkpoint.py pass; checkpoint resume semantics documented in docs/CHECKPOINTS.md
- Data/tokenizer guard: tests/test_data_tokenizer_cli.py pass; tokenizer/config mismatch fails clearly
- Alignment guard: tests/test_alignment.py pass for SFT mask and DPO response-only scoring
- Export guard: tests/test_export_guard.py pass; GGUF/quantization remains experimental until pinned llama.cpp load-and-generate
Notes: Nano is closed as a publishable 3-step scratch pipeline artifact, not as a quality language model. Tiny CPU tasks may start; real Tiny training still depends on audited Data/Tokenizer phase work.
```
