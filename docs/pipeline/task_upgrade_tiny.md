# task_upgrade_tiny.md - Nano to Tiny Optimization Backlog

Model slot: `tiny`

Current next level: Tiny CPU, 20-30M parameters

Candidate config: `configs/tiny.json`

Current measured Tiny params: `23,058,944`

Baseline date: 2026-10-13

Business purpose: dùng Nano release đã xuất bản để mở backlog tối ưu/nâng cấp lên level Tiny mà không đổi AchiticLM Core, không dùng pretrained weights, không claim chất lượng khi chưa có data/eval, và không phá các contract của Nano. Backlog này chỉ được claim sau khi Nano vNext trong `docs/pipeline/task_nano_vnext.md` được close.

## Readiness Verdict

Status: WAITING_FOR_NANO_VNEXT, NOT_READY_FOR_TINY_PUBLICATION

Kết luận ngắn:

- Có thể chuẩn bị kế hoạch tối ưu Tiny vì Nano đã closeout PASS và `configs/tiny.json` nằm trong target 20-30M.
- Chưa claim implementation rows trong file này cho tới khi `NANO-VNEXT-CLOSE-001` trong `docs/pipeline/task_nano_vnext.md` PASS hoặc bị defer rõ ràng.
- Chưa được publish Tiny checkpoint vì phase Data/Tokenizer đang `NOT_STARTED`, Tiny hiện dùng `vocab_size=12000` trong khi Nano release tokenizer là `8000`, và train/eval infrastructure chưa có held-out eval, metrics manifest, exact resume hoặc artifact manifest đầy đủ.
- Không cần sửa `achitic/model.py` cho bước này. Mọi tối ưu trước Tiny phải giữ nguyên Transformer - GQA - RoPE - RMSNorm - SwiGLU.

## Baseline Evidence

| Area | Current evidence | Result |
| --- | --- | --- |
| Nano closeout | `docs/pipeline/task_nano.md`, `docs/pipeline/nano/07_NANO_CLOSEOUT.md`, `docs/pipeline/01_FOUNDATION_SMOKE.md` | PASS |
| Public release | GitHub release `nano-v0.1.0`, prerelease, target commit `e32a726b3832080f30556af1729581b5e7288dac` | PASS |
| Release assets | `COMMAND_LOG.md`, `INSTALL_USAGE.md`, `LICENSE`, `nano.json`, `nano.pt`, `NOTICE`, `README.md`, `SHA256SUMS`, `tokenizer.model`, `tokenizer.vocab`, `USAGE_TERMS.md` | PASS |
| Nano local release docs | `docs/releases/nano/*` includes model card, eval report, manifest, security, usage terms and ISO-aligned spec | PASS |
| Tiny param count | `.venv/bin/python -c "... AchiticLM(Config(**configs/tiny.json)) ..."` returned `23058944` | PASS |
| Tiny tokenizer compatibility | `configs/tiny.json` uses `vocab_size=12000`; Nano release tokenizer uses `8000` | BLOCKER before Tiny train/release |
| Nano vNext | `docs/pipeline/task_nano_vnext.md` plans `nano-v0.1.1` patch release | BLOCKER before Tiny optimization |
| Data phase | `docs/pipeline/02_DATA_TOKENIZER.md` closeout is `NOT_STARTED` | BLOCKER before Tiny train/release |
| Pretrain scale phase | `docs/pipeline/03_PRETRAIN_SCALE.md` closeout is `NOT_STARTED` | BLOCKER before Mini/Small/350M |

Release drift note: the current GitHub release assets do not include `ISO_TECHNICAL_SPEC.md`. Nano vNext must close this drift before Tiny work starts.

## Progress Dashboard

Overall progress: `[x---------] 10%`

Backlog progress: `1 / 10`

Current allowed rows:

- None in this file until `docs/pipeline/task_nano_vnext.md` is closed.

Rows that must stay locked until dependencies pass:

- `UPG-TRAIN-001` waits for `UPG-CFG-001`, `UPG-DAT-001`, `UPG-EVAL-001` and `UPG-LOG-001`.
- `UPG-CLOSE-001` waits for every previous row.

```text
TODO        [ ] not claimed
CLAIMED     [>] owner set, no implementation edits yet
IN_PROGRESS [~] implementation edits in progress, file locks active
BLOCKED     [!] blocked with reason and next action
REVIEW      [?] implementation done, waiting for full gate/evidence
PASS        [x] evidence recorded and gate passed
```

## Progress Update Rule

Update these fields whenever a row becomes `PASS`:

| Passed rows | Overall progress |
| ---: | --- |
| 0 | `[----------] 0%` |
| 1 | `[x---------] 10%` |
| 2 | `[xx--------] 20%` |
| 3 | `[xxx-------] 30%` |
| 4 | `[xxxx------] 40%` |
| 5 | `[xxxxx-----] 50%` |
| 6 | `[xxxxxx----] 60%` |
| 7 | `[xxxxxxx---] 70%` |
| 8 | `[xxxxxxxx--] 80%` |
| 9 | `[xxxxxxxxx-] 90%` |
| 10 | `[xxxxxxxxxx] 100%` |

## Claim And Lock Rules

- Claim exactly one row before editing files for that row.
- To claim, edit only this file first: set `Mark` to `[>]`, fill `Owner`, `Started`, and `Lock expires`.
- When implementation starts, change `Mark` to `[~]`.
- Do not edit files outside the row's allowed write set.
- Do not edit a file locked by another `[~] IN_PROGRESS` row.
- If a needed file is outside the write set, mark the row `[!] BLOCKED`, record `Coordination needed`, and stop.
- Do not mark `[x] PASS` without command output summary and artifact/evidence refs.
- Do not train or publish Tiny with Nano release tokenizer unless `configs/tiny.json` is changed to match `8000` and the checkpoint contract is documented. The preferred path is a new audited Tiny tokenizer matching `12000`.
- Do not change `achitic/model.py` unless a failing CPU test proves a real architecture bug. That work belongs to a separate architecture task, not this upgrade backlog.

## File Lock Matrix

| File or area | Owning row | Rule |
| --- | --- | --- |
| `docs/pipeline/task_upgrade_tiny.md`, `docs/pipeline/BACKLOG.md` | `UPG-BASE-001`, `UPG-CLOSE-001` | Coordination and closeout docs only |
| `configs/tiny.json`, `docs/pipeline/tiny/01_TINY_CONFIG.md`, `docs/pipeline/00_MODEL_LADDER.md` | `UPG-CFG-001` | Tiny sizing and tokenizer-size decision only |
| `docs/pipeline/02_DATA_TOKENIZER.md`, optional `docs/DATASET_CARD.md`, optional `docs/data/*` | `UPG-DAT-001` | Data/tokenizer provenance, split and audit planning only |
| `scripts/model_report.py`, optional `achitic/cli.py`, `tests/test_model_report.py`, `docs/pipeline/03_PRETRAIN_SCALE.md` | `UPG-MEM-001` | Param/memory reporting only |
| `achitic/eval.py`, `achitic/cli.py`, `tests/test_eval.py`, fixed prompt docs | `UPG-EVAL-001` | Held-out eval and sample harness only |
| `achitic/train.py`, `tests/test_train_metrics.py`, run-manifest docs | `UPG-LOG-001` | Metrics logging, run manifest and LR/schedule config only |
| `achitic/train.py`, `tests/test_checkpoint.py`, `docs/CHECKPOINTS.md` | `UPG-RESUME-001` | Exact or explicitly non-exact resume contract; waits for `UPG-LOG-001` |
| `achitic/data.py`, `tests/test_data_tokenizer_cli.py`, data packing docs | `UPG-PACK-001` | Token packing/sampling efficiency only |
| `docs/releases/tiny/*`, optional `releases/tiny/*`, `docs/pipeline/tiny/02_TINY_TRAIN_EVAL.md` | `UPG-TRAIN-001` | Tiny run evidence and release-candidate package only |
| `docs/pipeline/tiny/03_TINY_CLOSEOUT.md`, `docs/pipeline/03_PRETRAIN_SCALE.md` | `UPG-CLOSE-001` | Go/no-go and unlock decision only |

## Backlog Checklist

| Mark | Backlog ID | Owner | Started | Lock expires | Done when |
| --- | --- | --- | --- | --- | --- |
| [x] | `UPG-BASE-001` | Codex | 2026-10-13 | released | Repo/release baseline captured and Tiny feasibility recorded |
| [ ] | `UPG-CFG-001` |  |  |  | Tiny config/tokenizer strategy is calibrated and documented |
| [ ] | `UPG-DAT-001` |  |  |  | Data/tokenizer audit plan is executable and blocks are explicit |
| [ ] | `UPG-MEM-001` |  |  |  | Param/memory estimator exists and reports Tiny CPU budget |
| [ ] | `UPG-EVAL-001` |  |  |  | Held-out perplexity and fixed sample harness exist |
| [ ] | `UPG-LOG-001` |  |  |  | Training writes metrics/run manifest without breaking Nano |
| [ ] | `UPG-RESUME-001` |  |  |  | Resume semantics are exact or explicitly blocked for scale |
| [ ] | `UPG-PACK-001` |  |  |  | Data packing/sampling waste is measured or reduced |
| [ ] | `UPG-TRAIN-001` |  |  |  | Tiny release candidate train/eval package exists |
| [ ] | `UPG-CLOSE-001` |  |  |  | Go/no-go for Tiny publication and Mini unlock is recorded |

## Stage Board

| Mark | Row | Depends on | Allowed write set | Required validation |
| --- | --- | --- | --- | --- |
| [x] | `UPG-BASE-001` | Nano closeout PASS | `docs/pipeline/task_upgrade_tiny.md`, `docs/pipeline/BACKLOG.md` | Release/API asset audit and Tiny param command recorded |
| [ ] | `UPG-CFG-001` | `UPG-BASE-001` PASS | `configs/tiny.json`, `docs/pipeline/tiny/01_TINY_CONFIG.md`, `docs/pipeline/00_MODEL_LADDER.md` | Tiny param count 20-30M; tokenizer strategy selected |
| [ ] | `UPG-DAT-001` | Nano closeout PASS | `docs/pipeline/02_DATA_TOKENIZER.md`, optional `docs/DATASET_CARD.md`, optional `docs/data/*` | Dataset/tokenizer gate can reach PASS without private/unclear data |
| [ ] | `UPG-MEM-001` | `UPG-BASE-001` PASS | `scripts/model_report.py`, optional `achitic/cli.py`, optional tests, `docs/pipeline/03_PRETRAIN_SCALE.md` | Param/memory report for Nano and Tiny is reproducible |
| [ ] | `UPG-EVAL-001` | `UPG-DAT-001` REVIEW or PASS | `achitic/eval.py`, `achitic/cli.py`, tests, fixed prompt docs | Held-out loss/perplexity command and sample command pass on CPU |
| [ ] | `UPG-LOG-001` | `UPG-MEM-001` PASS | `achitic/train.py`, train metrics tests, run-manifest docs | Train writes loss/lr/tokens/throughput/grad/memory evidence |
| [ ] | `UPG-RESUME-001` | `UPG-LOG-001` PASS | `achitic/train.py`, `tests/test_checkpoint.py`, `docs/CHECKPOINTS.md` | Resume contract is tested; exact cursor if claimed |
| [ ] | `UPG-PACK-001` | `UPG-DAT-001` REVIEW or PASS | `achitic/data.py`, data tests, data docs | Packing/sampling report measures wasted tokens |
| [ ] | `UPG-TRAIN-001` | `UPG-CFG-001`, `UPG-DAT-001`, `UPG-EVAL-001`, `UPG-LOG-001` PASS | `docs/releases/tiny/*`, optional `releases/tiny/*`, `docs/pipeline/tiny/02_TINY_TRAIN_EVAL.md` | Tiny train/eval/sample/manifest exists; no release overclaim |
| [ ] | `UPG-CLOSE-001` | all previous rows PASS | closeout docs only | Tiny publication go/no-go recorded; Mini unlock only if Tiny PASS |

## Task Details

### UPG-BASE-001 - Current Repo And Release Baseline

Business objective: đóng băng trạng thái xuất phát trước khi tối ưu, để các model sau không tranh luận lại Nano đã publish hay chưa.

Status: PASS

Evidence:

- Nano pipeline docs show PASS.
- Public release `nano-v0.1.0` verified through GitHub API on 2026-10-13.
- Release assets verified: `COMMAND_LOG.md`, `INSTALL_USAGE.md`, `LICENSE`, `nano.json`, `nano.pt`, `NOTICE`, `README.md`, `SHA256SUMS`, `tokenizer.model`, `tokenizer.vocab`, `USAGE_TERMS.md`.
- Tiny param command returned `23058944`.
- Tokenizer mismatch blocker identified: Tiny config `12000` vs Nano tokenizer `8000`.

### UPG-CFG-001 - Tiny Config And Tokenizer Strategy

Business objective: chốt Tiny là 20-30M và không tạo checkpoint/tokenizer mismatch.

Allowed choices:

1. Keep `configs/tiny.json` at `vocab_size=12000` and require a new audited Tiny tokenizer with vocab 12000.
2. Change Tiny config to use `vocab_size=8000` only if the team intentionally reuses Nano tokenizer and remeasures parameter count.

Preferred choice: option 1, because Tiny should be trained from audited phase-2 corpus, not from Nano smoke corpus.

Checklist:

- [ ] Confirm actual params from instantiated model.
- [ ] Confirm `dim % heads == 0` and `heads % kv_heads == 0`.
- [ ] Record chosen tokenizer strategy.
- [ ] If vocab size changes, recalculate params and update ladder docs.
- [ ] Do not modify `achitic/model.py`.

Required validation:

```bash
.venv/bin/python -c "import json; from pathlib import Path; from achitic.model import AchiticLM, Config; c=Config(**json.loads(Path('configs/tiny.json').read_text())); print(sum(p.numel() for p in AchiticLM(c).parameters()))"
.venv/bin/python -m pytest -q tests/test_model.py
```

PASS criteria:

- Parameter count is within 20-30M.
- Tokenizer vocab decision is documented and compatible with the planned checkpoint.

### UPG-DAT-001 - Data And Tokenizer Gate Plan

Business objective: chuyển từ Nano smoke corpus sang corpus hợp pháp có thể dùng cho Tiny.

Checklist:

- [ ] Create or update dataset card with source, license, language, size, snapshot date and owner.
- [ ] Create machine-readable manifest with checksums and allowed use.
- [ ] Add privacy scan rules for email, phone, API tokens, personal address and private conversation.
- [ ] Define exact dedup and train/eval contamination checks.
- [ ] Freeze tokenizer special IDs: `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- [ ] Decide Tiny tokenizer vocab size from `UPG-CFG-001`.

PASS criteria:

- `docs/pipeline/02_DATA_TOKENIZER.md` can be closed as PASS with evidence.
- No private/proprietary/unclear-license data enters the repo or release.

### UPG-MEM-001 - Param And Memory Estimator

Business objective: biết Tiny có chạy thực tế trên CPU/RAM hiện có hay không trước khi train.

Checklist:

- [ ] Add a reusable param-count report for every config.
- [ ] Estimate training memory by parameters, gradients, AdamW states, activations, batch, context and dtype.
- [ ] Print warnings when config label and actual params diverge.
- [ ] Keep estimator independent from release artifacts.

Suggested command:

```bash
.venv/bin/python scripts/model_report.py --configs configs/nano.json configs/tiny.json configs/50m.json
```

PASS criteria:

- Report records Tiny params, estimated RAM and recommended batch/accum start point.
- Full `pytest -q` still passes.

### UPG-EVAL-001 - Held-Out Eval And Fixed Samples

Business objective: Tiny must have measurable held-out loss/perplexity and fixed prompt samples before anyone discusses quality.

Checklist:

- [ ] Add eval command for a held-out `.bin` split.
- [ ] Compute loss and perplexity without updating weights.
- [ ] Add fixed Vietnamese, English and code prompts.
- [ ] Store outputs in a report, with no production-quality claim.

PASS criteria:

- Eval command runs on CPU for a tiny smoke split.
- The command accepts real phase-2 eval data when available.
- Tests cover no-grad eval behavior.

### UPG-LOG-001 - Train Metrics And Run Manifest

Business objective: mỗi run Tiny tạo evidence đủ để debug và tái lập.

Checklist:

- [ ] Log step, train loss, LR, tokens seen, tokens/sec and grad norm.
- [ ] Record device, dtype, config checksum, data checksum and tokenizer checksum.
- [ ] Add optional JSONL/CSV metrics output.
- [ ] Keep Nano smoke command backward-compatible.
- [ ] Configize LR schedule/warmup if implemented; do not hard-code scale policy.

PASS criteria:

- A Nano smoke train writes metrics without breaking existing tests.
- `pytest -q` passes.

### UPG-RESUME-001 - Resume Semantics Upgrade

Business objective: trước các run dài hơn Nano, resume phải rõ là exact hay non-exact.

Checklist:

- [ ] Decide whether Tiny requires exact data-order resume.
- [ ] If exact resume is claimed, save sampler epoch, data cursor and consumed microbatch offset.
- [ ] If exact resume is not implemented, keep the checkpoint semantics explicit and block long scale claims.
- [ ] Update `docs/CHECKPOINTS.md`.

PASS criteria:

- Resume behavior is tested.
- No exact-resume claim exists without a test that proves it.

### UPG-PACK-001 - Data Packing And Sampling Efficiency

Business objective: tránh lãng phí token khi chuyển từ smoke corpus sang corpus lớn.

Checklist:

- [ ] Measure wasted tokens for current `TokenDataset` path.
- [ ] Decide whether packing is needed for Tiny.
- [ ] Add tests for deterministic chunking/packing if implemented.
- [ ] Preserve tokenizer/config consistency checks.

PASS criteria:

- A waste report exists, or packing is implemented and tested.
- No dataset-order claim conflicts with `UPG-RESUME-001`.

### UPG-TRAIN-001 - Tiny Release Candidate Run

Business objective: tạo release-candidate Tiny package, không nhất thiết publish ngay.

Dependencies:

- `UPG-CFG-001` PASS
- `UPG-DAT-001` PASS
- `UPG-EVAL-001` PASS
- `UPG-LOG-001` PASS

Checklist:

- [ ] Train Tiny from scratch with audited train split.
- [ ] Run held-out eval.
- [ ] Generate fixed sample report.
- [ ] Create `docs/releases/tiny/ARTIFACT_MANIFEST.md`.
- [ ] Record config, tokenizer checksum, dataset manifest checksum, command, hardware and metrics.
- [ ] Run `pytest -q` and Nano smoke after train/eval code changes.

PASS criteria:

- Tiny release candidate has enough evidence for review.
- It is still not published until `UPG-CLOSE-001` gives go/no-go.

### UPG-CLOSE-001 - Tiny Go/No-Go And Next Level Unlock

Business objective: chốt Tiny có được publish và có mở Mini/Small experiments hay không.

Checklist:

- [ ] Confirm Tiny params are in 20-30M.
- [ ] Confirm tokenizer/config/checkpoint vocab match.
- [ ] Confirm data provenance/license/privacy/contamination evidence.
- [ ] Confirm eval/sample/metrics/artifact manifest.
- [ ] Confirm Nano smoke still passes.
- [ ] Decide publication status: `NO_GO`, `RELEASE_CANDIDATE`, or `PUBLISH`.
- [ ] Unlock Mini/Small only if Tiny PASS.

PASS criteria:

- Go/no-go is recorded in `docs/pipeline/tiny/03_TINY_CLOSEOUT.md`.
- `docs/pipeline/03_PRETRAIN_SCALE.md` is updated only with supported evidence.

## Handoff Template

```text
Task ID:
Mark before:
Mark after:
Owner:
Files changed:
Commands run:
Results:
Artifacts:
Known risks:
Next allowed task:
```

## Tiny Publication Gate

Tiny may be published only when all statements below are true:

- `docs/pipeline/02_DATA_TOKENIZER.md` is `Status: PASS`.
- Every row in this backlog is PASS.
- Tokenizer vocabulary size equals checkpoint/config `vocab_size`.
- Checkpoint is scratch-trained by this repo, not replaced with pretrained weights.
- Release docs include model card, artifact manifest, eval report, security note, usage terms, checksums and install/use instructions.
- No GGUF/quantized artifact is claimed verified unless llama.cpp load-and-generate evidence exists.
