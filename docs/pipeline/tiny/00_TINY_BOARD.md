# Tiny CPU board

Tiny là nấc sau Nano trong ladder CPU. Tiny không đổi cấu trúc model; chỉ dùng config 20-30M, dữ liệu đã audit, tokenizer đã freeze và cùng checkpoint/inference contract.

## Dependencies

- `docs/pipeline/01_FOUNDATION_SMOKE.md` must have `Status: PASS` from Nano.
- `docs/pipeline/02_DATA_TOKENIZER.md` must have `Status: PASS` before real Tiny training.

## Luật tránh dẫm đạp

- Chỉ nhận một task Tiny tại một thời điểm.
- Không sửa `achitic/model.py` trong Tiny trừ khi quay lại Nano model task và có test chứng minh bug.
- Không đổi tokenizer đã freeze trong phase 2.
- Không sửa task file khác đang `IN_PROGRESS`.
- Tiny PASS không mở khóa 1B trực tiếp; nó chỉ mở khóa Mini/Small scale experiments.

## Tiny task order

| Mark | Task file | Depends on | Primary write set |
| --- | --- | --- | --- |
| [ ] | `01_TINY_CONFIG.md` | Nano PASS | `configs/tiny.json`, docs ladder, estimator docs/tests |
| [ ] | `02_TINY_TRAIN_EVAL.md` | Data PASS, `01_TINY_CONFIG` PASS | train/eval scripts, metrics docs, Tiny task file |
| [ ] | `03_TINY_CLOSEOUT.md` | all Tiny tasks PASS | closeout docs only |

## Tiny PASS definition

- `configs/tiny.json` is calibrated in the 20-30M target range.
- Tokenizer vocab size matches `configs/tiny.json`.
- Train/eval run uses audited data from phase 2.
- Artifact manifest records config, tokenizer checksum, data manifest checksum, command, hardware and metrics.
- Sample report exists for fixed Vietnamese/English prompts.
- `pytest -q` and Nano smoke still pass after Tiny changes.
