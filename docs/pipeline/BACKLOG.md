# AchiticLM staged backlog

Backlog này là danh sách task có thể chia cho nhiều model. Mỗi task phải tuân thủ `00_PIPELINE_CONTRACT.md` và phase tương ứng. Không nhận task ở phase sau nếu dependency phase chưa `PASS`.

## P0 - Nano foundation gate

Task cụ thể cho mức Nano nằm trong `docs/pipeline/nano/`. Hoàn tất Nano trước, rồi mới mở Tiny và Data/Tokenizer.

Status: PASS on 2026-10-12. Evidence is recorded in `docs/pipeline/task_nano.md`, `docs/pipeline/nano/07_NANO_CLOSEOUT.md`, `docs/pipeline/01_FOUNDATION_SMOKE.md` and the public Nano release `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.0`.

| ID | Phase | Task | Done when |
| --- | --- | --- | --- |
| `FND-001` | 1 | Chuẩn hóa dev environment docs | Có command setup và dependency notes chạy được |
| `FND-002` | 1 | CPU tests cho RoPE | Test shape/dtype/causality/suffix pass |
| `FND-003` | 1 | CPU tests cho GQA | Valid/invalid config và Q/K/V shape pass |
| `FND-004` | 1 | Checkpoint load tests | Save/load config, model, optimizer, RNG pass |
| `FND-005` | 1 | Resume smoke semantics | Document exact hoặc non-exact resume, test pass |
| `FND-006` | 1 | Tokenizer/config mismatch guard | Vocab mismatch fail rõ |
| `FND-007` | 1 | Nano smoke train command/script | Prepare/tokenizer/encode/train/chat pass |
| `FND-008` | 1 | Alignment CPU tests | SFT mask và DPO logprob pass |
| `FND-009` | 1 | Export claim guard docs | Docs cấm claim nếu thiếu llama.cpp generation |
| `NANO-PUB-001` | 1 | Publishable Nano release package | Model card, artifact manifest, checksums, eval report, security note and release smoke pass |

## P0.5 - Tiny CPU gate

Task cụ thể cho mức Tiny nằm trong `docs/pipeline/tiny/`. Tiny chỉ chạy sau Nano PASS và Data/Tokenizer PASS.

| ID | Phase | Task | Done when |
| --- | --- | --- | --- |
| `TINY-CONFIG-001` | Tiny | Calibrate Tiny 20-30M | Param count trong target, không đổi architecture |
| `TINY-TRAIN-001` | Tiny | Train/eval Tiny CPU | Dùng data/tokenizer đã audit, có metrics/sample/manifest |
| `TINY-CLOSE-001` | Tiny | Tiny closeout | Tiny PASS và mở khóa Mini/Small scale experiments |

## P1 - Data/tokenizer gate

| ID | Phase | Task | Done when |
| --- | --- | --- | --- |
| `DAT-001` | 2 | Dataset card | Source/license/privacy/use case đầy đủ |
| `DAT-002` | 2 | Machine-readable manifest | Checksum và split policy có thể audit |
| `DAT-003` | 2 | Privacy scan | PII/blocker report rõ ràng |
| `DAT-004` | 2 | Dedup report | Exact dedup pass, near-dedup plan nếu cần |
| `DAT-005` | 2 | Deterministic split | Train/eval checksum ổn định |
| `DAT-006` | 2 | Contamination check | Train/eval overlap report pass |
| `DAT-007` | 2 | Tokenizer training record | Vocab/special IDs/checksum/command lưu lại |
| `DAT-008` | 2 | Tokenizer audit | Vietnamese/English/code/byte fallback samples pass |
| `DAT-009` | 2 | Token statistics | Token count theo source/split/context có report |
| `DAT-010` | 2 | Tokenizer freeze | Contract breaking nếu đổi tokenizer được document |

## P1 - Pretrain scale gate

| ID | Phase | Task | Done when |
| --- | --- | --- | --- |
| `TRN-001` | 3 | Param/memory estimator | Params thật và memory estimate in ra từ config |
| `TRN-002` | 3 | Eval perplexity loop | Held-out eval chạy theo checkpoint/config |
| `TRN-003` | 3 | Metrics logging | Loss/lr/tokens/throughput/grad/memory được lưu |
| `TRN-004` | 3 | Resume cursor | Resume semantics đủ rõ, exact nếu cần scale |
| `TRN-005` | 3 | LR schedule config | Warmup/schedule không hard-code |
| `TRN-006` | 3 | AMP policy | CUDA AMP có scaler, CPU vẫn chạy |
| `TRN-007` | 3 | Efficient sampling/packing | Wasted tokens giảm hoặc được đo |
| `TRN-008` | 3 | DDP sanity | Local multi-process smoke hoặc doc limitation |
| `TRN-009` | 3 | Fixed sample prompts | Vietnamese/English/code sample report |
| `TRN-010` | 3 | Artifact manifest | Checkpoint có config/tokenizer/data/command/metrics ref |

## P2 - 1B infrastructure

| ID | Phase | Task | Done when |
| --- | --- | --- | --- |
| `INF-001` | 4 | Recalibrate 1B config | Param target thật được tính và document |
| `INF-002` | 4 | FSDP2/sharding | Dry run pass, không chỉ DDP replicate |
| `INF-003` | 4 | Sharded checkpoint | State đầy đủ và resume được |
| `INF-004` | 4 | Streaming shards | Data không phụ thuộc memmap đơn quá lớn |
| `INF-005` | 4 | Scheduled eval | Eval chạy định kỳ và lưu metrics |
| `INF-006` | 4 | Fault recovery drill | Kill/restart từ checkpoint pass |
| `INF-007` | 4 | Budget plan | GPU hours/storage/tokens/batch/context rõ |
| `INF-008` | 4 | Nano sharding test | CPU/GPU nhỏ pass |
| `INF-009` | 4 | Checkpoint security note | `torch.load` trust boundary rõ |
| `INF-010` | 4 | 1B release checklist | Artifact/eval/repro checklist đầy đủ |

## P2 - Alignment and safety

| ID | Phase | Task | Done when |
| --- | --- | --- | --- |
| `ALN-001` | 5 | SFT schema/data card | Provenance/license/privacy đủ |
| `ALN-002` | 5 | Preference schema/data card | Chosen/rejected source và process rõ |
| `ALN-003` | 5 | JSONL validator | Length/context/schema report pass |
| `ALN-004` | 5 | SFT mask tests | Prompt tokens không tính loss |
| `ALN-005` | 5 | DPO logprob tests | Response-only scoring đúng |
| `ALN-006` | 5 | Alignment metadata | Base/tokenizer/data/stage refs lưu trong checkpoint |
| `ALN-007` | 5 | Safety eval prompts | QA/code/hallucination/injection set cố định |
| `ALN-008` | 5 | Sample comparison | Base vs SFT vs DPO report |
| `ALN-009` | 5 | DPO go/no-go gate | Không chạy DPO nếu SFT chưa đạt |
| `ALN-010` | 5 | Limitation docs | Không claim production assistant thiếu review |

## P2 - Export and edge

| ID | Phase | Task | Done when |
| --- | --- | --- | --- |
| `EXP-001` | 6 | Pin llama.cpp | Commit/build command được ghi |
| `EXP-002` | 6 | Exporter Nano smoke | Nano FP16 GGUF tạo được |
| `EXP-003` | 6 | Tensor mapping audit | Q/K RoPE permutation verified |
| `EXP-004` | 6 | Tokenizer parity | IDs/pieces/byte fallback samples pass |
| `EXP-005` | 6 | FP16 load-and-generate | llama.cpp generation pass |
| `EXP-006` | 6 | Quant matrix | Q8/Q6/Q4 artifacts nếu tool hỗ trợ |
| `EXP-007` | 6 | Quant load-and-generate | Mỗi quant file generation pass |
| `EXP-008` | 6 | Edge benchmark | RAM/VRAM/tokens/sec/hardware recorded |
| `EXP-009` | 6 | PyTorch vs llama.cpp parity | Temp 0 comparison có report |
| `EXP-010` | 6 | Known incompatibilities | Limitation theo llama.cpp commit rõ |

## Chốt task

Mỗi task khi xong phải cập nhật evidence vào phase file tương ứng hoặc PR description:

```text
Task ID:
Files changed:
Tests run:
Artifact refs:
Risk left:
```

Task thiếu evidence không được tính là done, kể cả code đã chạy một lần trên máy cá nhân.
