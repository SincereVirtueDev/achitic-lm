# Nano completion board

Nano là nấc đầu tiên trước Tiny. Mục tiêu là test pipeline trên CPU với cùng kiến trúc AchiticLM Core, không đổi `model.py` trừ khi test chứng minh bug.

Model-level task board: `docs/pipeline/task_nano.md`. Dùng file này để claim task, theo dõi progress bar và lock file trước khi sửa code/docs.

## Luật tránh dẫm đạp

- Một model chỉ nhận một task file tại một thời điểm.
- Khi nhận task, chỉ sửa task file của mình để đổi `Status: TODO` thành `Status: IN_PROGRESS` và điền `Owner`.
- Không sửa `00_NANO_BOARD.md` trừ khi bạn là người chốt Nano hoặc cập nhật link task.
- Không sửa file ngoài `Allowed write set` của task. Nếu cần, ghi `Coordination needed` và dừng.
- Không sửa cùng một test/code file với task khác đang `IN_PROGRESS`.
- Task chỉ được đổi `Status: PASS` khi đã ghi command test và kết quả.
- Chỉ người chốt Nano được đổi `docs/pipeline/01_FOUNDATION_SMOKE.md` closeout sang `PASS`.

## Nano task order

| Mark | Task file | Depends on | Parallel group | Primary write set |
| --- | --- | --- | --- | --- |
| [x] | `01_ENV_BASELINE.md` | none | A | setup docs, this task file |
| [ ] | `02_MODEL_ROPE_GQA.md` | `01_ENV_BASELINE` | B | model tests, `achitic/model.py` only if bug proven |
| [ ] | `03_CHECKPOINT_RESUME.md` | `01_ENV_BASELINE` | C | checkpoint tests, `achitic/train.py` |
| [ ] | `04_DATA_TOKENIZER_CLI.md` | `01_ENV_BASELINE` | D | data/tokenizer/CLI tests, Nano smoke |
| [ ] | `05_ALIGNMENT_CPU.md` | `02_MODEL_ROPE_GQA` | E | alignment tests |
| [ ] | `06_EXPORT_GUARD.md` | `01_ENV_BASELINE` | F | docs/export claim guard |
| [ ] | `../task_nano.md#NANO-PUBLISH-001` | pipeline rows PASS | R | `docs/releases/nano/*`, optional release script |
| [ ] | `07_NANO_CLOSEOUT.md` | all above and publish PASS | Z | closeout docs only |

Groups B, C, D and F may run in parallel after `01_ENV_BASELINE` PASS because their write sets are separate. Group E waits for model tests. Group R waits for checkpoint/data/export evidence. Group Z is exclusive.

## Nano global PASS definition

- All Nano task files are `Status: PASS`.
- `pytest -q` passes.
- Nano prepare/tokenizer/encode/train/chat smoke passes with `configs/nano.json`.
- CPU tests cover causality, RoPE, GQA, checkpoint loading, SFT mask and DPO response-only scoring.
- Tokenizer ID/vocab/checkpoint config mismatch failures are explicit.
- Docs do not claim GGUF or quantization verification without llama.cpp load-and-generate evidence.
- `docs/releases/nano/` has a publishable release package: model card, artifact manifest, checksums, eval report, security note and release checklist.

After Nano PASS, the next allowed model-size target is Tiny, but real Tiny training still depends on the Data/Tokenizer phase.
