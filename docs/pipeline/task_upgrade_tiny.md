# task_upgrade_tiny.md - Nano to Tiny Optimization Backlog

Model slot: `tiny`

Current next level: Tiny CPU, 20-30M parameters

Candidate config: `configs/tiny.json`

Current measured Tiny params: `23,058,944`

Baseline date: 2026-10-13

Business purpose: dùng Nano release đã xuất bản để mở backlog tối ưu/nâng cấp lên level Tiny mà không đổi AchiticLM Core, không dùng pretrained weights, không claim chất lượng khi chưa có data/eval, và không phá các contract của Nano. Backlog này được mở sau khi Nano vNext trong `docs/pipeline/task_nano_vnext.md` đã close.

## Readiness Verdict

Status: READY_FOR_OPTIMIZATION, NOT_READY_FOR_TINY_PUBLICATION

Kết luận ngắn:

- Có thể bắt đầu tối ưu Tiny vì Nano đã closeout PASS, `nano-v0.1.1` đã published và `configs/tiny.json` nằm trong target 20-30M.
- `UPG-CFG-001`, `UPG-DAT-001`, `UPG-MEM-001`, `UPG-EVAL-001`, `UPG-LOG-001`, `UPG-RESUME-001` và `UPG-PACK-001` đã PASS.
- Chưa được publish Tiny checkpoint vì phase Data/Tokenizer đang `BLOCKED_NO_APPROVED_TINY_CORPUS`, Tiny hiện dùng `vocab_size=12000` trong khi Nano release tokenizer là `8000`, và release infrastructure chưa có Tiny artifact manifest đầy đủ.
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
| Nano vNext | `nano-v0.1.1` published at `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.1` | PASS |
| Data phase | `docs/pipeline/02_DATA_TOKENIZER.md` closeout is `BLOCKED_NO_APPROVED_TINY_CORPUS`; audit plan and manifest exist | BLOCKER before Tiny train/release |
| Pretrain scale phase | `scripts/model_report.py` exists; `docs/pipeline/03_PRETRAIN_SCALE.md` remains `BLOCKED_WAITING_FOR_DATA_TOKENIZER` | BLOCKER before Mini/Small/350M |

Release drift note: closed by `nano-v0.1.1`, which includes `ISO_TECHNICAL_SPEC.md`.

## Progress Dashboard

Overall progress: `[xxxxxxxx--] 80%`

Backlog progress: `8 / 10`

Current allowed rows:

- none until Phase 2 Data/Tokenizer closeout is `PASS`

Rows that must stay locked until dependencies pass:

- `UPG-TRAIN-001` waits for `UPG-CFG-001`, `UPG-DAT-001`, `UPG-EVAL-001`, `UPG-LOG-001`, `UPG-RESUME-001`, `UPG-PACK-001` and Phase 2 data/tokenizer closeout `PASS`.
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
| [x] | `UPG-CFG-001` | Codex | 2026-10-13 | released | Tiny config/tokenizer strategy is calibrated and documented |
| [x] | `UPG-DAT-001` | Codex | 2026-10-13 | released | Data/tokenizer audit plan is executable and blocks are explicit |
| [x] | `UPG-MEM-001` | Codex | 2026-10-13 | released | Param/memory estimator exists and reports Tiny CPU budget |
| [x] | `UPG-EVAL-001` | Codex | 2026-10-13 | released | Held-out perplexity and fixed sample harness exist |
| [x] | `UPG-LOG-001` | Codex | 2026-10-13 | released | Training writes metrics/run manifest without breaking Nano |
| [x] | `UPG-RESUME-001` | Codex | 2026-10-13 | released | Resume semantics are exact or explicitly blocked for scale |
| [x] | `UPG-PACK-001` | Codex | 2026-10-13 | released | Data packing/sampling waste is measured or reduced |
| [!] | `UPG-TRAIN-001` | Codex | 2026-10-13 | blocked | Tiny release candidate train/eval package exists |
| [ ] | `UPG-CLOSE-001` |  |  |  | Go/no-go for Tiny publication and Mini unlock is recorded |

## Stage Board

| Mark | Row | Depends on | Allowed write set | Required validation |
| --- | --- | --- | --- | --- |
| [x] | `UPG-BASE-001` | Nano closeout PASS | `docs/pipeline/task_upgrade_tiny.md`, `docs/pipeline/BACKLOG.md` | Release/API asset audit and Tiny param command recorded |
| [x] | `UPG-CFG-001` | `UPG-BASE-001` PASS | `configs/tiny.json`, `docs/pipeline/tiny/01_TINY_CONFIG.md`, `docs/pipeline/00_MODEL_LADDER.md` | Tiny param count 20-30M; tokenizer strategy selected |
| [x] | `UPG-DAT-001` | Nano closeout PASS | `docs/pipeline/02_DATA_TOKENIZER.md`, optional `docs/DATASET_CARD.md`, optional `docs/data/*` | Dataset/tokenizer gate can reach PASS without private/unclear data |
| [x] | `UPG-MEM-001` | `UPG-BASE-001` PASS | `scripts/model_report.py`, optional `achitic/cli.py`, optional tests, `docs/pipeline/03_PRETRAIN_SCALE.md` | Param/memory report for Nano and Tiny is reproducible |
| [x] | `UPG-EVAL-001` | `UPG-DAT-001` REVIEW or PASS | `achitic/eval.py`, `achitic/cli.py`, tests, fixed prompt docs | Held-out loss/perplexity command and sample command pass on CPU |
| [x] | `UPG-LOG-001` | `UPG-MEM-001` PASS | `achitic/train.py`, train metrics tests, run-manifest docs | Train writes loss/lr/tokens/throughput/grad/memory evidence |
| [x] | `UPG-RESUME-001` | `UPG-LOG-001` PASS | `achitic/train.py`, `tests/test_checkpoint.py`, `docs/CHECKPOINTS.md` | Resume contract is tested; exact cursor if claimed |
| [x] | `UPG-PACK-001` | `UPG-DAT-001` REVIEW or PASS | `achitic/data.py`, data tests, data docs | Packing/sampling report measures wasted tokens |
| [!] | `UPG-TRAIN-001` | `UPG-CFG-001`, `UPG-DAT-001`, `UPG-EVAL-001`, `UPG-LOG-001`, `UPG-RESUME-001`, `UPG-PACK-001` PASS and Phase 2 closeout PASS | `docs/releases/tiny/*`, optional `releases/tiny/*`, `docs/pipeline/tiny/02_TINY_TRAIN_EVAL.md` | BLOCKED: Phase 2 closeout is not PASS; no approved Tiny train/eval data or 12k tokenizer |
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

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Allowed choices:

1. Keep `configs/tiny.json` at `vocab_size=12000` and require a new audited Tiny tokenizer with vocab 12000.
2. Change Tiny config to use `vocab_size=8000` only if the team intentionally reuses Nano tokenizer and remeasures parameter count.

Preferred choice: option 1, because Tiny should be trained from audited phase-2 corpus, not from Nano smoke corpus.

Checklist:

- [x] Confirm actual params from instantiated model.
- [x] Confirm `dim % heads == 0` and `heads % kv_heads == 0`.
- [x] Record chosen tokenizer strategy.
- [x] Vocab size unchanged; ladder docs updated with tokenizer strategy.
- [x] Do not modify `achitic/model.py`.

Required validation:

```bash
.venv/bin/python -c "import json; from pathlib import Path; from achitic.model import AchiticLM, Config; c=Config(**json.loads(Path('configs/tiny.json').read_text())); print(sum(p.numel() for p in AchiticLM(c).parameters()))"
.venv/bin/python -m pytest -q tests/test_model.py
```

PASS criteria:

- Parameter count is within 20-30M.
- Tokenizer vocab decision is documented and compatible with the planned checkpoint.

Completion evidence:

- `configs/tiny.json` kept at `vocab_size=12000`, `dim=512`, `layers=6`, `heads=8`, `kv_heads=2`, `ffn_dim=1408`, `context=512`.
- Instantiated Tiny model parameter count: `23,058,944`, inside the 20-30M target band.
- Shape constraints: `dim % heads == 0`, `heads % kv_heads == 0`, `head_dim=64`.
- Tokenizer strategy: do not reuse Nano release tokenizer (`8000`) for Tiny. Tiny requires a new audited tokenizer with `vocab_size=12000` and frozen special IDs `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Files changed: `docs/pipeline/task_upgrade_tiny.md`, `docs/pipeline/tiny/01_TINY_CONFIG.md`, `docs/pipeline/00_MODEL_LADDER.md`.
- Commands run:
  - `.venv/bin/python -c "import json; from pathlib import Path; from achitic.model import AchiticLM, Config; cfg=Config(**json.loads(Path('configs/tiny.json').read_text())); model=AchiticLM(cfg); params=sum(p.numel() for p in model.parameters()); print('params', params); print('vocab_size', cfg.vocab_size); print('dim_mod_heads', cfg.dim % cfg.heads); print('heads_mod_kv_heads', cfg.heads % cfg.kv_heads); print('head_dim', cfg.dim // cfg.heads); print('layers', cfg.layers); print('ffn_dim', cfg.ffn_dim); print('context', cfg.context)"` -> `params 23058944`, `vocab_size 12000`, `dim_mod_heads 0`, `heads_mod_kv_heads 0`, `head_dim 64`.
  - `.venv/bin/python -m pytest -q tests/test_model.py` -> `8 passed`.
  - `.venv/bin/python -m pytest -q` -> `25 passed`.
- Known risks: Tiny training/release remains blocked until Data/Tokenizer, eval and logging rows pass.
- Next allowed tasks at close time: `UPG-DAT-001`, `UPG-MEM-001`.

### UPG-DAT-001 - Data And Tokenizer Gate Plan

Business objective: chuyển từ Nano smoke corpus sang corpus hợp pháp có thể dùng cho Tiny.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Create or update dataset card with source, license, language, size, snapshot date and owner.
- [x] Create machine-readable manifest with checksums and allowed use.
- [x] Add privacy scan rules for email, phone, API tokens, personal address and private conversation.
- [x] Define exact dedup and train/eval contamination checks.
- [x] Freeze tokenizer special IDs: `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- [x] Decide Tiny tokenizer vocab size from `UPG-CFG-001`.

PASS criteria for this row:

- `docs/pipeline/02_DATA_TOKENIZER.md` has explicit evidence fields and blockers so it can be closed as PASS only after real Tiny corpus/tokenizer artifacts exist.
- No private/proprietary/unclear-license data enters the repo or release.

Completion evidence:

- Dataset card created: `docs/DATASET_CARD.md`.
- Machine-readable manifest created: `docs/data/tiny_dataset_manifest.json`.
- Gate procedure created: `docs/data/TINY_DATA_GATE.md`.
- Manifest status: `BLOCKED_NO_APPROVED_TINY_CORPUS`; this is intentional and prevents Tiny training/release overclaim.
- Reference smoke source recorded: `examples/corpus.txt`, SHA-256 `7c1eaf73846dd770ed4d2137f3ca379100bb71e8b753ac99150070293825bac8`, allowed only for pipeline/tokenizer CLI smoke and not approved for Tiny pretraining or held-out quality evaluation.
- Privacy rules recorded for email, phone, API keys/tokens/passwords/private keys, personal address and private conversations.
- Dedup and contamination policy recorded: exact normalized SHA-256 dedup, deterministic hash split, train/eval exact hash intersection, and n-gram/shingle overlap report before quality claims.
- Tiny tokenizer contract recorded: SentencePiece BPE, vocab size `12000`, byte fallback, special IDs `unk=0`, `bos=1`, `eos=2`, `pad=3`; Nano 8k tokenizer reuse is disallowed.
- Commands run:
  - `sha256sum examples/corpus.txt` -> `7c1eaf73846dd770ed4d2137f3ca379100bb71e8b753ac99150070293825bac8`.
  - `wc -l -w -c examples/corpus.txt` -> `6 110 655`.
  - `.venv/bin/python -m json.tool docs/data/tiny_dataset_manifest.json` -> JSON parsed successfully.
  - `sha256sum docs/DATASET_CARD.md docs/data/TINY_DATA_GATE.md docs/data/tiny_dataset_manifest.json examples/corpus.txt` -> manifest checksum `60f9d31e5a70da2f488fbd3b9faad7fff0013816eeebf9bae6cf329e0df2c90c`.
  - `.venv/bin/python -m pytest -q` -> `25 passed`.
  - Nano smoke from `/tmp` artifacts:
    - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-upg-dat-clean.txt` -> `documents: 6`.
    - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-upg-dat-clean.txt --prefix /tmp/achitic-upg-dat-sp --vocab 8000` -> passed.
    - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-upg-dat-clean.txt --tokenizer /tmp/achitic-upg-dat-sp.model --out /tmp/achitic-upg-dat.bin` -> `tokens: 131`.
    - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-upg-dat.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-upg-dat-nano.pt` -> `step=1 loss=9.0427`, checkpoint saved at step 3.
    - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-upg-dat-nano.pt --tokenizer /tmp/achitic-upg-dat-sp.model --prompt "Xin chao" --tokens 16` -> generated text successfully.
    - `.venv/bin/python -c "checkpoint/tokenizer vocab and step check"` -> `checkpoint_step 3`, `checkpoint_vocab 8000`, `tokenizer_vocab 8000`, `special_ids 0 1 2 3`.
- Phase 2 status after this row: `BLOCKED_NO_APPROVED_TINY_CORPUS`, not `PASS`.
- Known risks: no real Tiny train/eval corpus is approved yet; no Tiny 12k tokenizer exists yet; token counts and encode smoke for Tiny remain blocked.
- Next allowed tasks at close time: `UPG-MEM-001`, `UPG-EVAL-001`, `UPG-PACK-001`.

### UPG-MEM-001 - Param And Memory Estimator

Business objective: biết Tiny có chạy thực tế trên CPU/RAM hiện có hay không trước khi train.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Add a reusable param-count report for every config.
- [x] Estimate training memory by parameters, gradients, AdamW states, activations, batch, context and dtype.
- [x] Print warnings when config label and actual params diverge.
- [x] Keep estimator independent from release artifacts.

Suggested command:

```bash
.venv/bin/python scripts/model_report.py --configs configs/nano.json configs/tiny.json configs/50m.json
```

PASS criteria:

- Report records Tiny params, estimated RAM and recommended batch/accum start point.
- Full `pytest -q` still passes.

Completion evidence:

- Added `scripts/model_report.py` with exact AchiticLM parameter formula and optional instantiated-model verification for configs below a safe threshold.
- Added `tests/test_model_report.py` covering formula parity, label mismatch warnings and activation-memory batch scaling.
- Updated `docs/pipeline/03_PRETRAIN_SCALE.md` with the current ladder report and Tiny CPU budget.
- Tiny report: `23,058,944` params, verified by instantiated model, estimated train RAM `0.50 GiB` for FP32 batch 1/accum 4 planning model, recommended start `batch=1, accum=4`.
- Config label warnings are emitted for `configs/50m.json`, `configs/150m.json`, `configs/350m.json` and `configs/1b.json`.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_model_report.py` -> `3 passed`.
  - `.venv/bin/python scripts/model_report.py --configs configs/nano.json configs/tiny.json configs/50m.json` -> Nano/Tiny/50M report passed; 50M label warning emitted.
  - `.venv/bin/python scripts/model_report.py --configs configs/nano.json configs/tiny.json configs/50m.json --json` -> JSON report passed.
  - `.venv/bin/python scripts/model_report.py --configs configs/nano.json configs/tiny.json configs/50m.json configs/150m.json configs/350m.json configs/1b.json --verify-threshold 50000000` -> full ladder report passed.
  - `.venv/bin/python -m pytest -q` -> `28 passed`.
  - Nano smoke from `/tmp` artifacts:
    - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-upg-mem-clean.txt` -> `documents: 6`.
    - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-upg-mem-clean.txt --prefix /tmp/achitic-upg-mem-sp --vocab 8000` -> passed.
    - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-upg-mem-clean.txt --tokenizer /tmp/achitic-upg-mem-sp.model --out /tmp/achitic-upg-mem.bin` -> `tokens: 131`.
    - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-upg-mem.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-upg-mem-nano.pt` -> `step=1 loss=9.0427`, checkpoint saved at step 3.
    - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-upg-mem-nano.pt --tokenizer /tmp/achitic-upg-mem-sp.model --prompt "Xin chao" --tokens 16` -> generated text successfully.
    - `.venv/bin/python -c "checkpoint/tokenizer vocab and step check"` -> `checkpoint_step 3`, `checkpoint_vocab 8000`, `tokenizer_vocab 8000`, `special_ids 0 1 2 3`.
- Known risks: RAM values are estimates, not measured peak RSS; Tiny training remains blocked by Phase 2 data/tokenizer closeout.
- Next allowed tasks: `UPG-EVAL-001`, `UPG-LOG-001`, `UPG-PACK-001`.

### UPG-EVAL-001 - Held-Out Eval And Fixed Samples

Business objective: Tiny must have measurable held-out loss/perplexity and fixed prompt samples before anyone discusses quality.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Add eval command for a held-out `.bin` split.
- [x] Compute loss and perplexity without updating weights.
- [x] Add fixed Vietnamese, English and code prompts.
- [x] Store outputs in a report, with no production-quality claim.

PASS criteria:

- Eval command runs on CPU for a tiny smoke split.
- The command accepts real phase-2 eval data when available.
- Tests cover no-grad eval behavior.

Completion evidence:

- Added `achitic/eval.py` with `evaluate_model`, `evaluate_checkpoint`, fixed-prompt loading and sample report helpers.
- Added CLI subcommands:
  - `.venv/bin/python -m achitic.cli eval --checkpoint <ckpt> --tokenizer <tokenizer.model> --data <eval.bin> --device cpu --out <report.json>`
  - `.venv/bin/python -m achitic.cli sample-report --checkpoint <ckpt> --tokenizer <tokenizer.model> --prompts docs/eval/fixed_prompts.jsonl --device cpu --out <samples.jsonl>`
- Added `tests/test_eval.py` covering no-grad eval behavior, train-mode restore, fixed-prompt validation and no-grad sample generation.
- Added fixed prompt docs:
  - `docs/eval/fixed_prompts.jsonl`
  - `docs/eval/FIXED_PROMPTS.md`
- Smoke eval result from Nano `/tmp` artifacts: loss `8.159513473510742`, perplexity `3496.4850572735186`, batches `1`, tokens `128`, checkpoint step `3`, device `cpu`.
- Fixed sample report generated 3 rows: Vietnamese, English and code prompts, 8 generated tokens each.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_eval.py` -> `3 passed`.
  - `.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py` -> `5 passed`.
  - `.venv/bin/python -m achitic.eval --help` -> listed `loss` and `samples`.
  - `.venv/bin/python -m achitic.cli --help` -> listed `eval` and `sample-report`.
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-upg-eval-clean.txt` -> `documents: 6`.
  - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-upg-eval-clean.txt --prefix /tmp/achitic-upg-eval-sp --vocab 8000` -> passed.
  - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-upg-eval-clean.txt --tokenizer /tmp/achitic-upg-eval-sp.model --out /tmp/achitic-upg-eval.bin` -> `tokens: 131`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-upg-eval.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-upg-eval-nano.pt` -> `step=1 loss=9.0427`, checkpoint saved at step 3.
  - `.venv/bin/python -m achitic.cli eval --checkpoint /tmp/achitic-upg-eval-nano.pt --tokenizer /tmp/achitic-upg-eval-sp.model --data /tmp/achitic-upg-eval.bin --batch 1 --device cpu --out /tmp/achitic-upg-eval-report.json` -> JSON report written and printed.
  - `.venv/bin/python -m achitic.eval loss --checkpoint /tmp/achitic-upg-eval-nano.pt --tokenizer /tmp/achitic-upg-eval-sp.model --data /tmp/achitic-upg-eval.bin --batch 1 --device cpu` -> JSON report printed.
  - `.venv/bin/python -m achitic.cli sample-report --checkpoint /tmp/achitic-upg-eval-nano.pt --tokenizer /tmp/achitic-upg-eval-sp.model --prompts docs/eval/fixed_prompts.jsonl --tokens 8 --device cpu --out /tmp/achitic-upg-eval-samples.jsonl` -> 3 sample rows written and printed.
  - `.venv/bin/python -m pytest -q` -> `31 passed`.
- Known risks: smoke eval uses Nano example data and is not a held-out Tiny quality result. Real Tiny perplexity waits for Phase 2 approved eval split and 12k tokenizer.
- Next allowed tasks: `UPG-LOG-001`, `UPG-PACK-001`.

### UPG-LOG-001 - Train Metrics And Run Manifest

Business objective: mỗi run Tiny tạo evidence đủ để debug và tái lập.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Log step, train loss, LR, tokens seen, tokens/sec and grad norm.
- [x] Record device, dtype, config checksum, data checksum and tokenizer checksum.
- [x] Add optional JSONL/CSV metrics output.
- [x] Keep Nano smoke command backward-compatible.
- [x] Configize LR schedule/warmup if implemented; no schedule is implemented in this row, and current LR is logged from the optimizer.

PASS criteria:

- A Nano smoke train writes metrics without breaking existing tests.
- `pytest -q` passes.

Completion evidence:

- Updated `achitic/train.py` with optional `--metrics`, `--run-manifest` and `--tokenizer` arguments.
- Metrics JSONL is written on rank 0 with step, train loss, LR, tokens this step, tokens seen, tokens/sec, elapsed seconds, grad norm, epoch, batch, accum, device, dtype, peak CUDA memory and max RSS.
- Run manifest JSON records command, config/data/tokenizer paths and SHA-256 checksums, checkpoint format, resume semantics, device, dtype, world size, start/final step, batch, accum, LR, save cadence, tokens seen and final timing.
- Added schema docs: `docs/RUN_MANIFEST.md`.
- Added tests: `tests/test_train_metrics.py`.
- Legacy train command remains valid without metrics/manifest flags.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_train_metrics.py` -> `1 passed`.
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-upg-log-clean.txt` -> `documents: 6`.
  - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-upg-log-clean.txt --prefix /tmp/achitic-upg-log-sp --vocab 8000` -> passed.
  - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-upg-log-clean.txt --tokenizer /tmp/achitic-upg-log-sp.model --out /tmp/achitic-upg-log.bin` -> `tokens: 131`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-upg-log.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-upg-log-nano.pt --metrics /tmp/achitic-upg-log-metrics.jsonl --run-manifest /tmp/achitic-upg-log-manifest.json --tokenizer /tmp/achitic-upg-log-sp.model` -> `step=1 loss=9.0427`, checkpoint saved at step 3.
  - `.venv/bin/python -c "metrics and manifest summary"` -> `metrics_rows 3`, `manifest_status completed`, `manifest_final_step 3`, `manifest_tokens_seen 384`, `checkpoint_step 3`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-upg-log.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-upg-log-nano-legacy.pt` -> legacy command passed.
  - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-upg-log-nano.pt --tokenizer /tmp/achitic-upg-log-sp.model --prompt "Xin chao" --tokens 16` -> generated text successfully.
  - `.venv/bin/python -m pytest -q` -> `32 passed`.
- Known risks: metrics/manifest are run evidence only and do not make resume exact. `UPG-RESUME-001` remains required before long scale claims.
- Next allowed tasks: `UPG-RESUME-001`, `UPG-PACK-001`.

### UPG-RESUME-001 - Resume Semantics Upgrade

Business objective: trước các run dài hơn Nano, resume phải rõ là exact hay non-exact.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Decide whether Tiny requires exact data-order resume.
- [x] Exact resume is not claimed; sampler epoch, data cursor and consumed microbatch offset remain absent from checkpoint format v1.
- [x] Because exact resume is not implemented, keep the checkpoint semantics explicit and block long scale exact-resume claims.
- [x] Update `docs/CHECKPOINTS.md`.

PASS criteria:

- Resume behavior is tested.
- No exact-resume claim exists without a test that proves it.

Decision:

- Current resume is non-exact by design: model, optimizer, global step and RNG states are restored, but data order is not bit-exact.
- Tiny smoke/recovery checks may use this contract.
- Long Tiny/Mini/Small runs must not claim exact resume unless a future checkpoint contract stores and tests sampler/data cursor state.

Completion evidence:

- Added `EXACT_DATA_ORDER_RESUME=False`, `MISSING_EXACT_RESUME_STATE` and `resume_contract()` to `achitic/train.py`.
- Updated `tests/test_checkpoint.py` to prove the saved checkpoint carries `model_optimizer_rng_restored_data_order_not_exact` and does not contain exact data-order cursor/sampler state.
- Updated `docs/CHECKPOINTS.md` with exact data-order resume status, missing state list and scale gate decision.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_checkpoint.py` -> `4 passed`.
  - `.venv/bin/python -m pytest -q tests/test_train_metrics.py` -> `1 passed`.
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-upg-resume-clean.txt` -> `documents: 6`.
  - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-upg-resume-clean.txt --prefix /tmp/achitic-upg-resume-sp --vocab 8000` -> passed.
  - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-upg-resume-clean.txt --tokenizer /tmp/achitic-upg-resume-sp.model --out /tmp/achitic-upg-resume.bin` -> `tokens: 131`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-upg-resume.bin --steps 2 --batch 1 --accum 1 --out /tmp/achitic-upg-resume-nano.pt --metrics /tmp/achitic-upg-resume-metrics-a.jsonl --run-manifest /tmp/achitic-upg-resume-manifest-a.json --tokenizer /tmp/achitic-upg-resume-sp.model` -> `step=1 loss=9.0427`, checkpoint saved at step 2.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-upg-resume.bin --resume /tmp/achitic-upg-resume-nano.pt --steps 4 --batch 1 --accum 1 --out /tmp/achitic-upg-resume-nano-resumed.pt --metrics /tmp/achitic-upg-resume-metrics-b.jsonl --run-manifest /tmp/achitic-upg-resume-manifest-b.json --tokenizer /tmp/achitic-upg-resume-sp.model` -> `step=3 loss=8.3757`, resumed checkpoint saved at step 4.
  - `.venv/bin/python -c "resume smoke summary"` -> `initial_manifest completed 0 2 256`, `resume_manifest completed 2 4 256`, `metrics_rows 2 2`, `checkpoint_step 4`, `exact_data_order_resume False`, `missing_state_count 5`.
  - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-upg-resume-nano-resumed.pt --tokenizer /tmp/achitic-upg-resume-sp.model --prompt "Xin chao" --tokens 16` -> generated text successfully.
  - `.venv/bin/python -m pytest -q` -> `33 passed`.
- Known risks: current resume is not bit-exact for data order. This is documented and blocks exact-resume claims.
- Next allowed task: `UPG-PACK-001`.

### UPG-PACK-001 - Data Packing And Sampling Efficiency

Business objective: tránh lãng phí token khi chuyển từ smoke corpus sang corpus lớn.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Measure wasted tokens for current `TokenDataset` path.
- [x] Decide whether packing is needed for Tiny.
- [x] Add tests for deterministic chunking/packing if implemented.
- [x] Preserve tokenizer/config consistency checks.

PASS criteria:

- A waste report exists, or packing is implemented and tested.
- No dataset-order claim conflicts with `UPG-RESUME-001`.

Decision:

- Current `TokenDataset` uses deterministic contiguous fixed-context chunks over a single encoded int32 token stream.
- No new packing implementation is required before Tiny release-candidate training if approved Tiny train data is encoded into sufficiently long contiguous `.bin` streams and measured waste is negligible.
- The current path wastes only the final tail: `(total_tokens - 1) % context` target tokens.
- This task does not change dataset order, sampler behavior or resume semantics.

Completion evidence:

- Added `token_packing_report(path, context)` to `achitic/data.py`.
- Added tests in `tests/test_data_tokenizer_cli.py` for deterministic chunking alignment, waste math, invalid context and short input handling.
- Added data doc: `docs/data/TOKEN_PACKING.md`.
- Smoke packing report for `/tmp/achitic-upg-pack.bin`, context `128`: total tokens `131`, target tokens `130`, windows `1`, used target tokens `128`, wasted target tokens `2`, waste ratio `0.015384615384615385`.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py` -> `7 passed`.
  - `.venv/bin/python -c "import json; from achitic.data import token_packing_report; print(json.dumps(token_packing_report('/tmp/achitic-upg-pack.bin',128), indent=2))"` -> packing report printed.
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-upg-pack-clean.txt` -> `documents: 6`.
  - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-upg-pack-clean.txt --prefix /tmp/achitic-upg-pack-sp --vocab 8000` -> passed.
  - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-upg-pack-clean.txt --tokenizer /tmp/achitic-upg-pack-sp.model --out /tmp/achitic-upg-pack.bin` -> `tokens: 131`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-upg-pack.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-upg-pack-nano.pt --metrics /tmp/achitic-upg-pack-metrics.jsonl --run-manifest /tmp/achitic-upg-pack-manifest.json --tokenizer /tmp/achitic-upg-pack-sp.model` -> `step=1 loss=9.0427`, checkpoint saved at step 3.
  - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-upg-pack-nano.pt --tokenizer /tmp/achitic-upg-pack-sp.model --prompt "Xin chao" --tokens 16` -> generated text successfully.
  - `.venv/bin/python -m pytest -q` -> `35 passed`.
- Known risks: Tiny waste must be remeasured on approved Phase 2 train/eval `.bin` files. Current smoke corpus is too small to infer real Tiny efficiency.
- Next allowed task: none until Phase 2 Data/Tokenizer closeout is `PASS`; then `UPG-TRAIN-001`.

### UPG-TRAIN-001 - Tiny Release Candidate Run

Business objective: tạo release-candidate Tiny package, không nhất thiết publish ngay.

Status: BLOCKED

Owner: Codex

Started: 2026-10-13

Blocked date: 2026-10-13

Blocking reason:

- `docs/pipeline/02_DATA_TOKENIZER.md` is `Status: BLOCKED_NO_APPROVED_TINY_CORPUS`, not `PASS`.
- `docs/data/tiny_dataset_manifest.json` has `approved_tiny_train_sources: []`.
- `docs/data/tiny_dataset_manifest.json` has `approved_tiny_eval_sources: []`.
- Tiny tokenizer `vocab_size=12000` has not been trained/audited.
- Nano release tokenizer has vocab `8000` and is smoke-only, so it cannot be reused for Tiny.

Required unblock inputs:

- Approved Tiny train source with provenance, license, rights owner, snapshot date, raw/normalized checksums and allowed use.
- Approved held-out Tiny eval split/source with contamination checks against train.
- Privacy scan, exact dedup and train/eval contamination reports.
- Frozen Tiny tokenizer `12000` with special IDs `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Encoded train/eval `.bin` files whose tokenizer vocab matches `configs/tiny.json`.
- Phase 2 closeout updated to `Status: PASS`.

Dependencies:

- `UPG-CFG-001` PASS
- `UPG-DAT-001` PASS
- `docs/pipeline/02_DATA_TOKENIZER.md` closeout PASS
- `UPG-EVAL-001` PASS
- `UPG-LOG-001` PASS
- `UPG-RESUME-001` PASS
- `UPG-PACK-001` PASS

Checklist:

- [ ] Train Tiny from scratch with audited train split. BLOCKED.
- [ ] Run held-out eval. BLOCKED.
- [ ] Generate fixed sample report. BLOCKED.
- [ ] Create `docs/releases/tiny/ARTIFACT_MANIFEST.md`. BLOCKED.
- [ ] Record config, tokenizer checksum, dataset manifest checksum, command, hardware and metrics. BLOCKED.
- [ ] Run `pytest -q` and Nano smoke after train/eval code changes. BLOCKED until train/eval inputs exist.

PASS criteria:

- Tiny release candidate has enough evidence for review.
- It is still not published until `UPG-CLOSE-001` gives go/no-go.

Blocked evidence:

- Dependency check command:
  - `.venv/bin/python -c "import json; m=json.load(open('docs/data/tiny_dataset_manifest.json')); print('manifest_status', m.get('status')); print('approved_train_sources', len(m.get('approved_tiny_train_sources', []))); print('approved_eval_sources', len(m.get('approved_tiny_eval_sources', []))); print('tokenizer_vocab', m.get('tokenizer_contract', {}).get('vocab_size')); print('blockers', [b.get('id') for b in m.get('blockers', [])])"`
- Result:
  - `manifest_status BLOCKED_NO_APPROVED_TINY_CORPUS`
  - `approved_train_sources 0`
  - `approved_eval_sources 0`
  - `tokenizer_vocab 12000`
  - `blockers ['TINY_DATA_001', 'TINY_DATA_002', 'TINY_TOKENIZER_001']`
- Files updated: `docs/pipeline/task_upgrade_tiny.md`, `docs/pipeline/tiny/02_TINY_TRAIN_EVAL.md`.
- No Tiny training command was run.
- No Tiny checkpoint, release candidate or artifact manifest was created.
- Next action: complete Phase 2 Data/Tokenizer closeout, then retry `UPG-TRAIN-001`.

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
