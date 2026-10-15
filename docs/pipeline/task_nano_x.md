# task_nano_x.md - Nano v0.2.0 Audit Fix And Next-Model Baseline

Model slot: `nano`

Current published release: `nano-v0.2.0` (public prerelease)

Next planned release: not selected; complete Nano-X closeout first

Release type: engineering baseline refresh after Nano audit

Baseline date: 2026-10-13

Audit source: `docs/pipeline/ACHITIC_NANO_AUDIT.md`

Business purpose: tạo một version Nano mới để sửa các thiếu sót đã audit, làm nền kỹ thuật sạch cho Tiny, Mini, Small, 350M và 1B. Nano v0.2.0 vẫn là scratch pipeline model, không phải model chất lượng cao. Mục tiêu chính là làm đúng exporter, tokenizer, checkpoint loading, train loop, dữ liệu smoke, tài liệu và release contract trước khi các model lớn hơn kế thừa cùng code path.

## Version Decision

Status: CLOSED_PUBLISHED

Default target: `nano-v0.2.0`

Use `nano-v0.2.0` because this backlog may change runtime behavior, export behavior, tokenizer training behavior, safe checkpoint loading, generation cache, release assets and training loop semantics.

Use `nano-v0.1.2` only if the actual implementation is reduced to documentation/package cleanup with no code/runtime/artifact behavior change.

Escalate to `nano-v0.3.0` if any statement below becomes true, unless an explicit owner override keeps the work inside the unpublished `nano-v0.2.0` release candidate:

- AchiticLM Core architecture changes incompatibly.
- Checkpoint format changes in a way that old checkpoints cannot be loaded.
- Token IDs or special-token IDs are changed for an already published artifact.
- A new Nano checkpoint is trained on a materially different dataset and replaces `nano.pt`.

Owner override on 2026-10-14: include the real Vietnamese meaning-smoke corpus/tokenizer/checkpoint refresh in `nano-v0.2.0` as a supplement before public tag/publication. The refreshed artifact set was rebuilt, checked and documented on 2026-10-15.

## Readiness Verdict

Current status: CLOSED_PUBLISHED_PRERELEASE

Kết luận ngắn:

- Nano v0.2.0 is published as a prerelease with the merged audit fixes and controlled Vietnamese meaning-smoke evidence.
- Tiny and later models may inherit the verified implementation paths, but not Nano tokenizer, checkpoint or data artifacts.
- Tiny training remains blocked by Phase 2 Data/Tokenizer, but Tiny tooling should inherit the fixes from this Nano-X backlog.
- Do not publish GGUF or quantized assets unless the specific artifact has pinned llama.cpp load-and-generate evidence.
- Do not claim broad Nano language quality. The audited run proves only the controlled near-domain meaning smoke recorded by `NANO-MEAN-001`.

## Audit Findings To Close

| Audit ID | Priority | Summary | Owning row |
| --- | --- | --- | --- |
| `P0-1` | P0 | GGUF Q/K RoPE permutation is wrong for Achitic adjacent-pair RoPE | `NANO-X-EXPORT-001` |
| `P0-2` | P0 | GGUF writer calls missing token-ID methods | `NANO-X-EXPORT-001` |
| `P0-3` | P0 | GGUF writes 1-D norm tensors as FP16, causing llama.cpp abort | `NANO-X-EXPORT-001` |
| `P0-4a` | P0 | Need CPU regression tests for exporter tensor mapping and metadata | `NANO-X-EXPORT-001` |
| `P0-4b` | P0 | Need optional pinned llama.cpp parity/load-and-generate script | `NANO-X-LLAMA-001` |
| `P0-5` | P1 | GGUF token types for user-defined symbols are wrong | `NANO-X-EXPORT-001` |
| `P1-1` | P1 | Train loop lacks LR schedule, decay groups, validation, best checkpoint, throughput | `NANO-X-TRAIN-001` |
| `P1-2` | P1 | Tokenizer silently pads most vocab with reserved tokens | `NANO-X-TOK-001` |
| `P1-3` | P1 | Release should provide safer weights-only loading/export path | `NANO-X-CKPTSAFE-001` |
| `P2-1` | P2 | `generate()` lacks KV cache | `NANO-X-KVCACHE-001` |
| `P2-2` | P2 | Tiny smoke corpus reuse is not warned clearly | `NANO-X-DATAWARN-001` |
| `P2-3` | P2 | Docs contain local paths and missing measured model details | `NANO-X-DOC-001` |
| `P2-3 addendum` | P2 | Config names and measured parameter targets can mislead downstream agents | `NANO-X-CONFIGLABEL-001` |
| `P1-4` | P1 | `prepare` crashes on valid JSON lines that are not JSON objects | `NANO-X-PREP-001` |
| `P1-5` | P1 | Encode/tokenizer training are not large-corpus safe | `NANO-X-STREAM-001` |
| `P1-6` | P1 | Alignment checkpoints cannot resume and chat ignores template | `NANO-X-ALIGN-001` |
| `P2-4` | P2 | Quantization can silently fallback and lacks verification gate | `NANO-X-QUANT-001` |
| `R-1` | P1 | Retrain and publish a Nano artifact that reflects all audit fixes | `NANO-X-RETRAIN-001` |
| `OUT` | out of code scope | Real data is required for meaningful output; no agent may fetch unapproved datasets | `NANO-MEAN-001`, Phase 2 Data/Tokenizer |

Audit merge note:

- `docs/pipeline/ACHITIC_NANO_AUDIT.md` was updated from the former duplicate audit variant on 2026-10-14.
- The original `13` Nano-X rows below are the first Nano v0.2.0 engineering baseline scope and already have package evidence through `NANO-X-PKG-001`.
- The newly surfaced audit rows are tracked in the addendum board later in this file. They must pass, or be explicitly excluded with a next-version target, before this file can claim full audit closure.
- Use `nano-v0.2.1` for tooling/documentation-only addendum releases. Use `nano-v0.3.0` if tokenizer artifacts, Nano config, checkpoint format, `ffn_dim`, or trained weights change after `nano-v0.2.0` is public. Owner override: before `nano-v0.2.0` is public, `NANO-MEAN-001` may refresh the `nano-v0.2.0` tokenizer/config/checkpoint as one replacement candidate package.

## Progress Dashboard

Overall progress: `[xxxxxxxxxxxxxx] 100%`

Backlog progress: `14 / 14`

Current allowed rows:

- None in Nano-X. The next actionable gate is Phase 2 Data/Tokenizer for Tiny.

Rows that must stay locked until dependencies pass:

- None. Nano-X is closed; next-model locks are owned by their own task files.

```text
TODO        [ ] not claimed
CLAIMED     [>] owner set, no implementation edits yet
IN_PROGRESS [~] implementation edits in progress, file locks active
BLOCKED     [!] blocked with reason and next action
REVIEW      [?] implementation done, waiting for full gate/evidence
PASS        [x] evidence recorded and gate passed
```

## Progress Update Rule

Update `Overall progress`, `Backlog progress`, `Current allowed row` and the task table whenever a row becomes `PASS`.

| Passed rows | Overall progress |
| ---: | --- |
| 0 | `[--------------] 0%` |
| 1 | `[x-------------] 7%` |
| 2 | `[xx------------] 14%` |
| 3 | `[xxx-----------] 21%` |
| 4 | `[xxxx----------] 29%` |
| 5 | `[xxxxx---------] 36%` |
| 6 | `[xxxxxx--------] 43%` |
| 7 | `[xxxxxxx-------] 50%` |
| 8 | `[xxxxxxxx------] 57%` |
| 9 | `[xxxxxxxxx-----] 64%` |
| 10 | `[xxxxxxxxxx----] 71%` |
| 11 | `[xxxxxxxxxxx---] 79%` |
| 12 | `[xxxxxxxxxxxx--] 86%` |
| 13 | `[xxxxxxxxxxxxx-] 93%` |
| 14 | `[xxxxxxxxxxxxxx] 100%` |

## Claim And Lock Rules

- Claim exactly one row before editing files for that row.
- To claim, edit only this file first: set `Mark` to `[>]`, fill `Owner`, `Started`, and `Lock expires`.
- When implementation starts, change `Mark` to `[~]`.
- Do not edit files outside the row's allowed write set.
- Do not edit a file locked by another `[~] IN_PROGRESS` row.
- If a needed file is outside the write set, mark the row `[!] BLOCKED`, record `Coordination needed`, and stop.
- Do not mark `[x] PASS` without command output summary and artifact/evidence refs.
- Do not replace scratch Nano weights with pretrained weights.
- Do not publish `github_token.txt`, `.venv`, `runs/`, private data, credentials, local machine paths or non-audited datasets.
- Do not report GGUF or quantized artifacts as release-ready without llama.cpp load-and-generate evidence for that exact artifact.
- Keep tokenizer ID, vocabulary size and checkpoint config consistent.
- Run `.venv/bin/python -m pytest -q` and a Nano smoke train before any closeout. Run Tiny smoke where a train/export/shared-path row changes behavior used by Tiny.

## File Lock Matrix

| File or area | Owning row | Rule |
| --- | --- | --- |
| `docs/pipeline/task_nano_x.md`, `docs/pipeline/BACKLOG.md` | `NANO-X-BASE-001`, `NANO-X-CLOSE-001` | Planning and closeout only |
| `scripts/export_gguf.py`, `tests/test_export_gguf.py`, `pyproject.toml` export extra | `NANO-X-EXPORT-001` | GGUF mapping, token metadata and CPU exporter tests only |
| `scripts/verify_gguf.py`, optional llama.cpp integration test | `NANO-X-LLAMA-001` | Pinned llama.cpp evidence only |
| `achitic/checkpoint.py`, `scripts/export_weights.py`, safe-load integration sites, `pyproject.toml` release extra | `NANO-X-CKPTSAFE-001` | Safe load and weights-only artifact path only |
| `achitic/train.py`, `tests/test_train_metrics.py`, `docs/CHECKPOINTS.md`, `docs/RUN_MANIFEST.md` | `NANO-X-TRAIN-001` | LR schedule, decay groups, validation, best checkpoint, dtype and throughput only |
| `achitic/tokenizer.py`, `achitic/cli.py`, tokenizer tests and smoke docs | `NANO-X-TOK-001` | Reserved-token guard and tokenizer statistics only |
| `achitic/data.py`, `achitic/train.py`, `scripts/split_val.py`, data tests/docs | `NANO-X-DATAWARN-001` | Dataset window warnings, stride, split tooling only |
| `achitic/model.py`, model tests, generation docs | `NANO-X-KVCACHE-001` | KV cache inference path only; no train-forward regression |
| `docs/releases/nano/*`, `releases/nano/*`, `docs/pipeline/task_nano.md` path cleanup | `NANO-X-DOC-001` | Documentation cleanup and measured evidence only |
| `achitic/data.py`, prepare CLI/tests/docs | `NANO-X-PREP-001` | Robust `prepare` format detection only |
| `achitic/data.py`, `achitic/tokenizer.py`, encode/tokenizer CLI/tests/docs | `NANO-X-STREAM-001` | Streaming encode and large-corpus tokenizer controls only |
| `achitic/alignment.py`, `achitic/cli.py`, checkpoint/chat-template tests/docs | `NANO-X-ALIGN-001` | Alignment checkpoint contract and chat template only |
| `scripts/quantize.sh`, `scripts/verify_gguf.py`, quant tests/docs | `NANO-X-QUANT-001` | Quant fallback detection and llama.cpp verification only |
| `configs/*.json`, `docs/pipeline/00_MODEL_LADDER.md`, `docs/ARCHITECTURE.md`, config-param tests | `NANO-X-CONFIGLABEL-001` | Config label/parameter policy only |
| refreshed `releases/nano-v0.2.0/*`, or later `releases/nano-v0.2.1/*`/`releases/nano-v0.3.0/*`, release docs | `NANO-X-RETRAIN-001` | Fresh release candidate after addendum rows pass |
| `docs/data/NANO_MEANING_DATASET_CARD.md`, approved local corpus metadata, meaning-smoke eval docs | `NANO-MEAN-001` | Real Vietnamese corpus supplement for v0.2.0 only |
| `releases/nano-v0.2.0/*`, `docs/releases/nano/V0_2_0_RELEASE_PLAN.md`, checksums | `NANO-X-PKG-001` | Candidate package only |
| Git tag/release notes and release assets | `NANO-X-PUBLISH-001` | Publish only after package/smoke PASS |
| `docs/pipeline/01_FOUNDATION_SMOKE.md`, `docs/pipeline/task_upgrade_tiny.md`, closeout docs | `NANO-X-CLOSE-001` | Next-model unlock notes only |

## Backlog Checklist

| Mark | Backlog ID | Owner | Started | Lock expires | Done when |
| --- | --- | --- | --- | --- | --- |
| [x] | `NANO-X-BASE-001` | Codex | 2026-10-13 | released | Audit intake, version target and task ownership rules recorded |
| [x] | `NANO-X-EXPORT-001` | Codex | 2026-10-13 | released | GGUF exporter fixes and CPU regression tests pass |
| [x] | `NANO-X-LLAMA-001` | Codex | 2026-10-13 | released | Pinned llama.cpp load-and-generate parity script/evidence exists, or release scope explicitly excludes GGUF |
| [x] | `NANO-X-CKPTSAFE-001` | Codex | 2026-10-13 | released | Safe checkpoint/weights-only loading and release weight export path pass |
| [x] | `NANO-X-TRAIN-001` | Codex | 2026-10-13 | released | Train loop has schedule, decay groups, validation, best checkpoint, dtype and throughput evidence |
| [x] | `NANO-X-TOK-001` | Codex | 2026-10-13 | released | Tokenizer reserved padding is explicit, measured and guarded |
| [x] | `NANO-X-DATAWARN-001` | Codex | 2026-10-14 | released | Dataset window/stride warnings and validation split tooling pass |
| [x] | `NANO-X-KVCACHE-001` | Codex | 2026-10-14 | released | Cached generation matches uncached greedy output and logits |
| [x] | `NANO-X-DOC-001` | Codex | 2026-10-14 | released | Docs remove local paths and include measured Nano limitations/details |
| [x] | `NANO-X-SMOKE-001` | Codex | 2026-10-14 | released | Full pytest, Nano smoke, Tiny smoke and release-candidate smoke pass |
| [x] | `NANO-X-PKG-001` | Codex | 2026-10-14 | released | Local `nano-v0.2.0` package has manifest, checksums, safe weights and release notes |
| [x] | `NANO-MEAN-001` | Codex | 2026-10-15 | released | Real Vietnamese meaning-smoke corpus gates pass and refreshed v0.2.0 artifacts are ready |
| [x] | `NANO-X-PUBLISH-001` | Codex | 2026-10-15 | released | GitHub release is created or explicitly deferred with reason |
| [x] | `NANO-X-CLOSE-001` | Codex | 2026-10-15 | released | Nano-X closeout records go/no-go and updates next-model gates |

## Stage Board

| Mark | Row | Depends on | Allowed write set | Required validation |
| --- | --- | --- | --- | --- |
| [x] | `NANO-X-BASE-001` | Nano audit exists | `docs/pipeline/task_nano_x.md`, `docs/pipeline/BACKLOG.md` | Audit findings mapped to tasks |
| [x] | `NANO-X-EXPORT-001` | `NANO-X-BASE-001` PASS | `scripts/export_gguf.py`, `tests/test_export_gguf.py`, export dependency metadata | Export writes correct tensors/token metadata; CPU tests pass |
| [x] | `NANO-X-LLAMA-001` | `NANO-X-EXPORT-001` PASS | `scripts/verify_gguf.py`, optional integration test docs | Pinned llama.cpp load-and-generate evidence recorded or GGUF excluded from release |
| [x] | `NANO-X-CKPTSAFE-001` | `NANO-X-EXPORT-001` PASS | checkpoint module, `scripts/export_weights.py`, safe-load call sites, release dependency metadata | Weights-only/safetensors load path passes and unsafe fallback requires explicit trust flag |
| [x] | `NANO-X-TRAIN-001` | `NANO-X-BASE-001` PASS, coordinate with `NANO-X-DATAWARN-001` | `achitic/train.py`, train tests/docs | LR/decay/eval/best/dtype/throughput tests pass |
| [x] | `NANO-X-TOK-001` | `NANO-X-BASE-001` PASS | `achitic/tokenizer.py`, `achitic/cli.py`, tokenizer tests/docs | Reserved-ratio guard and stats tests pass |
| [x] | `NANO-X-DATAWARN-001` | `NANO-X-TRAIN-001` not `[~]` unless same owner | `achitic/data.py`, `achitic/train.py`, `scripts/split_val.py`, data tests/docs | Stride/window warning tests pass; split tool is deterministic |
| [x] | `NANO-X-KVCACHE-001` | model CPU tests PASS | `achitic/model.py`, model tests | Cached and uncached generation parity pass |
| [x] | `NANO-X-DOC-001` | implementation rows it documents are PASS or BLOCKED with reason | release docs/packages and selected pipeline docs | No local paths; model card/eval report include measured facts and limitations |
| [x] | `NANO-X-SMOKE-001` | all implementation rows PASS or explicitly excluded | evidence docs only | `pytest -q`, Nano smoke, Tiny smoke and package smoke pass |
| [x] | `NANO-X-PKG-001` | `NANO-X-SMOKE-001` PASS | `releases/nano-v0.2.0/*`, release docs | `sha256sum -c` passes; no secret/private data |
| [x] | `NANO-MEAN-001` | owner override, approved dataset card | dataset card, approved local corpus metadata, meaning-smoke eval docs, refreshed v0.2.0 package evidence | Real corpus provenance/license/privacy/contamination gates pass; refreshed tokenizer/config/checkpoint are consistent |
| [x] | `NANO-X-PUBLISH-001` | `NANO-MEAN-001` PASS and refreshed package evidence PASS | release notes/tag/assets | Public release exists or publication is deferred with reason |
| [x] | `NANO-X-CLOSE-001` | all previous rows PASS or allowed deferral | closeout docs only | Next-model gates updated with supported evidence |

## Task Details

### NANO-X-BASE-001 - Audit Intake And Version Scope

Business objective: biến `ACHITIC_NANO_AUDIT.md` thành backlog thực thi được, không để Tiny/Mini agent phải đọc lại toàn bộ audit và đoán thứ tự.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Read `docs/pipeline/ACHITIC_NANO_AUDIT.md`.
- [x] Map every P0/P1/P2 finding to an owning row.
- [x] Choose version target.
- [x] Add claim/lock rules.
- [x] Keep current Tiny training blocker intact.

Evidence:

- New backlog file: `docs/pipeline/task_nano_x.md`.
- Version target: `nano-v0.2.0`.
- Initial next allowed task was `NANO-X-EXPORT-001`; current allowed rows are tracked in the dashboard.

### NANO-X-EXPORT-001 - GGUF Exporter Fixes And CPU Regression Tests

Business objective: exporter phải đúng với Achitic RoPE, token metadata và tensor dtype trước khi bất kỳ model lớn hơn nào dùng exporter.

Audit coverage: `P0-1`, `P0-2`, `P0-3`, `P0-4a`, `P0-5`.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Remove Q/K permutation from `scripts/export_gguf.py`.
- [x] Replace missing GGUF writer calls with the correct unk/pad token ID APIs.
- [x] Keep every 1-D norm tensor in F32 and write 2-D tensors in FP16.
- [x] Read SentencePiece token types from `ModelProto`, including `USER_DEFINED`.
- [x] Add `tests/test_export_gguf.py` with a tiny tokenizer/model fixture.
- [x] Test that Q/K tensors are not permuted when read back from GGUF.
- [x] Test metadata: heads, kv heads, context, block count, RoPE theta, bos/eos/unk/pad IDs.
- [x] Test token types for user-defined, byte, control and unknown tokens.
- [x] Test `achitic.model.rope` against an independent adjacent-pair NumPy reference.
- [x] Raise the `gguf` optional dependency lower bound to `gguf>=0.19` and add `protobuf>=4` for SentencePiece proto parsing.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_export_gguf.py tests/test_export_guard.py tests/test_model.py
.venv/bin/python scripts/export_gguf.py --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --out /tmp/achitic-nano-x.gguf
```

PASS criteria:

- Export command completes with installed `gguf`.
- CPU tests prove tensor mapping, dtype and token metadata.
- No release doc claims GGUF readiness without `NANO-X-LLAMA-001`.

Completion evidence:

- Files changed: `scripts/export_gguf.py`, `tests/test_export_gguf.py`, `pyproject.toml`, `docs/pipeline/task_nano_x.md`.
- Exporter changes:
  - Removed Q/K permutation because Achitic RoPE rotates adjacent pairs and matches llama.cpp normal RoPE layout.
  - Replaced token-ID writer calls with `add_unk_token_id` and `add_pad_token_id`.
  - Writes 1-D tensors as F32 and 2-D tensors as FP16.
  - Reads SentencePiece token types from `ModelProto`, preserving `USER_DEFINED` and `BYTE`.
- Optional export dependencies installed in local venv for validation: `gguf 0.19.0`, `protobuf 7.36.2`.
- Commands run:
  - `.venv/bin/pip install -e '.[export]'` -> installed export dependencies.
  - `.venv/bin/python -m pytest -q tests/test_export_gguf.py tests/test_export_guard.py tests/test_model.py` -> `17 passed`.
  - `.venv/bin/python scripts/export_gguf.py --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --out /tmp/achitic-nano-x.gguf` -> exported FP16 GGUF successfully.
  - `.venv/bin/python -m pytest -q` -> `40 passed`.
  - Nano smoke: prepare -> `documents: 6`; tokenizer -> passed; encode -> `tokens: 131`; train -> checkpoint at `/tmp/achitic-nano-x-smoke.pt`; chat -> generated text successfully.
- Artifacts:
  - `/tmp/achitic-nano-x.gguf`, size approximately `10.3 MB`.
  - `/tmp/achitic-nano-x-smoke.pt`.
- Known risks:
  - GGUF export is CPU-regression-tested and `NANO-X-LLAMA-001` records llama.cpp evidence for `/tmp/achitic-nano-x.gguf`; release packaging must reuse that exact artifact/checksum or rerun verification against the final GGUF.
- Next allowed tasks at that time: `NANO-X-CKPTSAFE-001`, `NANO-X-TRAIN-001`, `NANO-X-TOK-001`, `NANO-X-DATAWARN-001` with train-file coordination, or `NANO-X-KVCACHE-001`. Current allowed rows are tracked in the dashboard.

### NANO-X-LLAMA-001 - Pinned llama.cpp Evidence

Business objective: nếu Nano v0.2.0 phát hành GGUF thì phải có bằng chứng load-and-generate/parity bằng llama.cpp đã pin; nếu không có, release phải loại GGUF khỏi asset list.

Audit coverage: `P0-4b`.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Add `scripts/verify_gguf.py`.
- [x] Accept `--checkpoint`, `--tokenizer`, `--gguf`, `--llama-cpp-dir`.
- [x] Build or invoke a pinned llama.cpp logits/generation checker.
- [x] Compare PyTorch logits after rounding 2-D tensors through FP16.
- [x] Include a stress case with Q/K scale to catch RoPE mapping regressions.
- [x] Add optional pytest guarded by `LLAMA_CPP_DIR`.
- [x] Record llama.cpp commit, command, thresholds and output.
- [x] If llama.cpp is unavailable, the script/test fail or skip clearly; this run used a local pinned checkout and is not blocked.

Required validation:

```bash
LLAMA_CPP_DIR=<path-to-pinned-llama.cpp> .venv/bin/python -m pytest -q tests/test_export_gguf.py
.venv/bin/python scripts/verify_gguf.py --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --gguf /tmp/achitic-nano-x.gguf --llama-cpp-dir <path-to-pinned-llama.cpp>
```

PASS criteria:

- Normal Nano parity meets the recorded threshold.
- Stress Nano parity catches the old RoPE bug and passes with the fixed exporter.
- Release notes describe exact evidence, not a generic exporter claim.

Completion evidence:

- Files changed: `scripts/verify_gguf.py`, `tests/test_verify_gguf.py`, `docs/pipeline/task_nano_x.md`.
- Local pinned llama.cpp checkout:
  - Path: `/tmp/llama.cpp`
  - Commit: `4413a192410fad1f054e9216114087a3e01527a0`
  - Configure: `cmake -S /tmp/llama.cpp -B /tmp/llama.cpp/build -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=OFF -DGGML_CUDA=OFF`
  - Build: `cmake --build /tmp/llama.cpp/build --target llama-cli -j2`
- Verification command:
  - `.venv/bin/python scripts/verify_gguf.py --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --gguf /tmp/achitic-nano-x.gguf --llama-cpp-dir /tmp/llama.cpp --generate-tokens 4 --max-input-tokens 16 --out /tmp/achitic-nano-x-llama-verify.json`
- Verification result:
  - Status: `PASS`
  - Normal max abs delta: `0.0007039159536361694`, threshold `< 0.001`
  - Normal top-1 match: `1.0`, threshold `>= 1.0`
  - Stress Q/K scale: `12.0`
  - Stress max abs delta: `0.010657072067260742`, threshold `< 0.1`
  - Stress top-1 match: `1.0`, threshold `>= 0.95`
  - Greedy llama.cpp-generated token IDs: `[7538, 7538, 7538, 7538]`
  - Greedy text: `Xin chao là là là là`
- Commands run:
  - `git ls-remote https://github.com/ggml-org/llama.cpp.git HEAD` -> reachable.
  - `git clone --depth 1 https://github.com/ggml-org/llama.cpp.git /tmp/llama.cpp` -> passed.
  - `git -C /tmp/llama.cpp rev-parse HEAD` -> `4413a192410fad1f054e9216114087a3e01527a0`.
  - `cmake -S /tmp/llama.cpp -B /tmp/llama.cpp/build -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=OFF -DGGML_CUDA=OFF` -> passed.
  - `cmake --build /tmp/llama.cpp/build --target llama-cli -j2` -> passed.
  - `LLAMA_CPP_DIR=/tmp/llama.cpp .venv/bin/python -m pytest -q tests/test_verify_gguf.py` -> `3 passed`.
  - `.venv/bin/python -m pytest -q tests/test_verify_gguf.py tests/test_export_gguf.py tests/test_export_guard.py` -> `11 passed, 1 skipped`.
  - `.venv/bin/python -m pytest -q` -> `42 passed, 1 skipped`.
- Notes:
  - `llama-cli` itself aborts in this environment with `failed to get a free port`, so `scripts/verify_gguf.py` uses a compiled libllama logits helper for both parity and greedy load-and-generate. This avoids the CLI UI/server path while still loading the GGUF through llama.cpp.
  - Evidence applies to `/tmp/achitic-nano-x.gguf`. Any release GGUF asset must either reuse this exact file/checksum or rerun `scripts/verify_gguf.py` against the final packaged artifact.
- Next allowed tasks at that time: `NANO-X-CKPTSAFE-001`, `NANO-X-TRAIN-001`, `NANO-X-TOK-001`, `NANO-X-DATAWARN-001` with train-file coordination, or `NANO-X-KVCACHE-001`. Current allowed rows are tracked in the dashboard.

### NANO-X-CKPTSAFE-001 - Safe Weights And Checkpoint Loading

Business objective: release inference paths should not require unsafe pickle loading by default.

Audit coverage: `P1-3`.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Add shared checkpoint/weight loading module: `achitic/checkpoint.py`.
- [x] Implement `load_weights(path)` for `.safetensors` and safe `.pt` loading.
- [x] Add safe globals needed for existing checkpoint state when using `weights_only=True`.
- [x] Require explicit `--trust-checkpoint` before any unsafe `weights_only=False` fallback.
- [x] Add `scripts/export_weights.py` with `--dtype fp16|fp32`.
- [x] Prefer `safetensors` as optional release dependency.
- [x] Do not duplicate tied `head.weight` when exporting weights-only artifacts.
- [x] Update `cli.py chat/benchmark`, `eval.py`, `alignment.py`, `scripts/export_gguf.py` and `scripts/verify_gguf.py` to use the safe path where applicable.
- [x] Keep `train.py --resume` capable of loading optimizer/RNG state, but try safe load first.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_checkpoint.py tests/test_data_tokenizer_cli.py
.venv/bin/python scripts/export_weights.py --checkpoint releases/nano/nano.pt --out /tmp/achitic-nano-x-fp16.safetensors --dtype fp16
.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-nano-x-fp16.safetensors --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16
```

PASS criteria:

- Existing `.pt` checkpoint can be loaded without unsafe fallback.
- FP16 weights-only artifact is materially smaller than full training checkpoint.
- Forward logits from exported FP16 weights match the FP16-rounded reference within the recorded tolerance.

Completion evidence:

- Files changed:
  - `achitic/checkpoint.py`
  - `scripts/export_weights.py`
  - `achitic/cli.py`
  - `achitic/eval.py`
  - `achitic/alignment.py`
  - `achitic/train.py`
  - `scripts/export_gguf.py`
  - `scripts/verify_gguf.py`
  - `tests/test_checkpoint.py`
  - `pyproject.toml`
  - `docs/pipeline/task_nano_x.md`
- Safe-load behavior:
  - `.pt` checkpoints load through `torch.load(..., weights_only=True)` with a narrow NumPy safe-global allowlist.
  - Unsafe `weights_only=False` is isolated in `achitic.checkpoint.trusted_torch_load()` and requires `--trust-checkpoint`.
  - `.safetensors` weights-only files store config JSON in metadata and reattach tied `head.weight` during load.
  - `scripts/export_weights.py` omits duplicated tied `head.weight`.
- Dependency:
  - Added optional release extra: `release = ["safetensors>=0.4"]`.
  - Local validation used `safetensors 0.8.0`.
- Commands run:
  - `.venv/bin/pip install safetensors>=0.4` -> installed `safetensors 0.8.0`.
  - `.venv/bin/python -m pytest -q tests/test_checkpoint.py` -> `7 passed`.
  - `.venv/bin/python -m pytest -q tests/test_eval.py tests/test_alignment.py tests/test_export_gguf.py tests/test_verify_gguf.py` -> `15 passed, 1 skipped`.
  - `.venv/bin/python scripts/export_weights.py --checkpoint releases/nano/nano.pt --out /tmp/achitic-nano-x-fp16.safetensors --dtype fp16` -> wrote FP16 safetensors with `38` tensors.
  - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-nano-x-fp16.safetensors --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16` -> generated text successfully.
  - `.venv/bin/python scripts/export_gguf.py --checkpoint /tmp/achitic-nano-x-fp16.safetensors --tokenizer releases/nano/tokenizer.model --out /tmp/achitic-nano-x-from-safe.gguf` -> exported successfully.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x.bin --steps 1 --batch 1 --accum 1 --out /tmp/achitic-ckptsafe-resume-a.pt` -> checkpoint saved.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x.bin --resume /tmp/achitic-ckptsafe-resume-a.pt --steps 2 --batch 1 --accum 1 --out /tmp/achitic-ckptsafe-resume-b.pt` -> safe resume succeeded.
  - `.venv/bin/python -m pytest -q tests/test_checkpoint.py tests/test_train_metrics.py tests/test_data_tokenizer_cli.py` -> `15 passed`.
  - `.venv/bin/python -m pytest -q` -> `45 passed, 1 skipped`.
- Artifact size evidence:
  - Full release checkpoint `releases/nano/nano.pt`: `58M`.
  - FP16 weights-only `/tmp/achitic-nano-x-fp16.safetensors`: `9.6M`.
  - GGUF exported from safetensors `/tmp/achitic-nano-x-from-safe.gguf`: `9.8M`.
- Known risks:
  - `.pt` remains a pickle container and must still be treated as trusted input even when loaded through `weights_only=True`; untrusted `.pt` fallback is explicitly gated by `--trust-checkpoint`.
  - Any safetensors asset added to a release must be included in `SHA256SUMS` and the artifact manifest.
- Next allowed tasks: `NANO-X-TRAIN-001`, `NANO-X-TOK-001`, `NANO-X-DATAWARN-001` with train-file coordination, or `NANO-X-KVCACHE-001`.

### NANO-X-TRAIN-001 - Training Loop For Scale

Business objective: Nano smoke train should exercise the same schedule/eval/logging path used by Tiny and larger models.

Audit coverage: `P1-1`.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Add `--warmup-steps`.
- [x] Add `--min-lr-ratio`.
- [x] Add `--schedule constant|cosine`, default `constant`.
- [x] Add `--weight-decay`, default `0.1`.
- [x] Group parameters so 1-D tensors and tied embedding avoid weight decay.
- [x] Add `--val-data`, `--eval-every`, `--eval-iters`.
- [x] Save `<out>.best.pt` when validation improves.
- [x] Store `best_val_loss` as an additive checkpoint key.
- [x] Add `--dtype fp32|bf16`, default `fp32`, with CPU-safe behavior.
- [x] Log `lr` and `tok/s`.
- [x] Ensure resume uses absolute step for LR schedule.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_train_metrics.py tests/test_checkpoint.py
.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-nano-x-train.pt --schedule cosine --warmup-steps 1 --min-lr-ratio 0.1
```

PASS criteria:

- LR schedule unit tests match formula at selected steps.
- Decay group test has no duplicate parameters and covers all trainable parameters.
- Resume test preserves LR sequence.
- Smoke command from existing docs remains backward-compatible.

Completion evidence:

- Files changed:
  - `achitic/train.py`
  - `tests/test_train_metrics.py`
  - `docs/CHECKPOINTS.md`
  - `docs/RUN_MANIFEST.md`
  - `docs/pipeline/task_nano_x.md`
- Train-loop changes:
  - Added `--warmup-steps`, `--min-lr-ratio`, `--schedule constant|cosine`, `--weight-decay`, `--val-data`, `--eval-every`, `--eval-iters` and `--dtype fp32|bf16`.
  - Added linear warmup plus optional cosine decay; resume uses the absolute global step when calculating LR.
  - Added AdamW decay/no-decay groups with no duplicated tied `embed.weight`/`head.weight`; 1-D tensors and `embed.weight` use `weight_decay=0`.
  - Added compatibility migration for older single-param-group optimizer checkpoints when resuming into the new decay/no-decay optimizer.
  - Added validation loss/perplexity, `<out>.best.pt`, additive `best_val_loss` checkpoint key, manifest fields and JSONL metrics fields.
  - Added bf16 autocast path when supported while keeping model checkpoint dtype unchanged.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_train_metrics.py tests/test_checkpoint.py` -> `13 passed`.
  - `.venv/bin/python -m pytest -q` -> `50 passed, 1 skipped`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x.bin --val-data /tmp/achitic-nano-x.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-nano-x-train.pt --schedule cosine --warmup-steps 1 --min-lr-ratio 0.1 --eval-every 1 --eval-iters 1 --metrics /tmp/achitic-nano-x-train-metrics.jsonl --run-manifest /tmp/achitic-nano-x-train-manifest.json --tokenizer /tmp/achitic-nano-x-sp.model` -> checkpoint and best checkpoint written.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-nano-x-train-required.pt --schedule cosine --warmup-steps 1 --min-lr-ratio 0.1` -> required minimal smoke command passed.
  - `.venv/bin/python -m achitic.train --config configs/tiny.json --data /tmp/achitic-tiny-train-smoke.bin --steps 1 --batch 1 --accum 1 --out /tmp/achitic-tiny-train-smoke.pt --schedule cosine --warmup-steps 0 --min-lr-ratio 1.0` -> Tiny shared-path smoke passed with synthetic token IDs only.
- Artifact evidence:
  - `/tmp/achitic-nano-x-train.pt`
  - `/tmp/achitic-nano-x-train.pt.best.pt`
  - `/tmp/achitic-nano-x-train-metrics.jsonl`
  - `/tmp/achitic-nano-x-train-manifest.json`
  - Manifest final step: `3`; best validation loss: `8.426473617553711`; final LR: `2.9999999999999997e-05`; tokens seen: `384`.
- Known risks:
  - Resume remains non-exact for data order, matching `model_optimizer_rng_restored_data_order_not_exact`.
  - Tiny smoke used synthetic token IDs to test code-path compatibility only; it is not an approved Tiny train/eval corpus.
- Next allowed tasks: `NANO-X-TOK-001`, `NANO-X-DATAWARN-001`, or `NANO-X-KVCACHE-001`.

### NANO-X-TOK-001 - Tokenizer Reserved Padding Guard

Business objective: tokenizer training must fail loudly when a corpus is too small for a requested vocab, unless the caller explicitly allows smoke padding.

Audit coverage: `P1-2`.

Status: PASS

Owner: Codex

Started: 2026-10-13

Finished: 2026-10-13

Checklist:

- [x] Add reserved-ratio accounting after tokenizer training.
- [x] Default `max_reserved_ratio` to `0.05`.
- [x] Raise a clear error if the ratio is exceeded.
- [x] Add CLI flag `--allow-reserved-padding` to keep Nano smoke possible.
- [x] Print tokenizer statistics: normal, user-defined, reserved, byte, control and unknown counts.
- [x] Update smoke commands to include the explicit flag where the example corpus intentionally pads vocab.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py
.venv/bin/python -m achitic.cli tokenizer --input examples/corpus.txt --prefix /tmp/achitic-nano-x-sp --vocab 8000 --allow-reserved-padding
```

PASS criteria:

- Training tokenizer on `examples/corpus.txt` with vocab `8000` fails without explicit reserved padding.
- The same command passes with `--allow-reserved-padding`.
- Token-type statistics sum to `vocab_size`.

Completion evidence:

- Files changed:
  - `achitic/tokenizer.py`
  - `achitic/cli.py`
  - `tests/test_data_tokenizer_cli.py`
  - `README.md`
  - `docs/DEVELOPMENT.md`
  - `docs/pipeline/00_PIPELINE_CONTRACT.md`
  - `docs/pipeline/nano/04_DATA_TOKENIZER_CLI.md`
  - `docs/pipeline/nano/07_NANO_CLOSEOUT.md`
  - `docs/releases/nano/MODEL_CARD.md`
  - `docs/pipeline/task_nano_x.md`
- Tokenizer behavior:
  - `train()` now returns tokenizer stats and validates `reserved_ratio`.
  - Default `max_reserved_ratio` is `0.05`.
  - `--allow-reserved-padding` is required for intentionally padded smoke tokenizers.
  - CLI tokenizer command prints JSON stats with `normal`, `user_defined`, `reserved`, `byte`, `control`, `unknown`, `reserved_ratio` and `vocab_size`.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py` -> `10 passed`.
  - `.venv/bin/python -m achitic.cli tokenizer --input examples/corpus.txt --prefix /tmp/achitic-nano-x-sp-no-allow --vocab 8000` -> failed as expected with `reserved tokens 7225/8000 (90.31%) exceed max_reserved_ratio 5.00%`.
  - `.venv/bin/python -m achitic.cli tokenizer --input examples/corpus.txt --prefix /tmp/achitic-nano-x-sp --vocab 8000 --allow-reserved-padding` -> passed and printed stats.
  - `.venv/bin/python -m pytest -q` -> `53 passed, 1 skipped`.
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-nano-x-tok-clean.txt` -> `documents: 6`.
  - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-nano-x-tok-clean.txt --prefix /tmp/achitic-nano-x-tok-sp --vocab 8000 --allow-reserved-padding` -> passed.
  - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-nano-x-tok-clean.txt --tokenizer /tmp/achitic-nano-x-tok-sp.model --out /tmp/achitic-nano-x-tok.bin` -> `tokens: 131`.
- Stats for the Nano smoke corpus:
  - `vocab_size`: `8000`
  - `reserved`: `7225`
  - `reserved_ratio`: `0.903125`
  - `normal`: `510`
  - `user_defined`: `5`
  - `byte`: `256`
  - `control`: `3`
  - `unknown`: `1`
  - Count sum: `8000`
- Known risks:
  - `--allow-reserved-padding` is a smoke-only escape hatch. It must not be treated as approval for real Tiny/Mini training tokenizers.
  - Tiny still requires its own audited 12k tokenizer from approved data.
- Next allowed tasks: `NANO-X-DATAWARN-001` or `NANO-X-KVCACHE-001`.

### NANO-X-DATAWARN-001 - Dataset Window Warnings And Validation Split Tool

Business objective: tiny corpora must be visibly marked as smoke-only, and future datasets need deterministic split tooling.

Audit coverage: `P2-2`, `OUT`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Checklist:

- [x] Add `--stride` for token windows, default equal to `context`.
- [x] Log train windows, tokens and tokens per step at train startup.
- [x] Warn if `len(dataset) < batch * accum`.
- [x] Warn if train token budget exceeds available unique tokens and data will repeat.
- [x] Add tests for stride/window counts.
- [x] Add tests for warnings on the example corpus.
- [x] Add `scripts/split_val.py` with deterministic hash-based line split.
- [x] Document that agents must not fetch internet datasets or invent data provenance.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py tests/test_train_metrics.py
.venv/bin/python scripts/split_val.py --input examples/corpus.txt --train-out /tmp/achitic-nano-x-train.txt --val-out /tmp/achitic-nano-x-val.txt --val-ratio 0.2 --seed achitic-nano-x
```

PASS criteria:

- Warnings appear for the 131-token smoke corpus.
- Split output is deterministic for the same seed and input.
- No dataset source is added without provenance/license/privacy/contamination fields.

Completion evidence:

- Files changed:
  - `achitic/data.py`
  - `achitic/train.py`
  - `scripts/split_val.py`
  - `tests/test_data_tokenizer_cli.py`
  - `tests/test_train_metrics.py`
  - `docs/data/TOKEN_PACKING.md`
  - `docs/data/TINY_DATA_GATE.md`
  - `docs/pipeline/task_nano_x.md`
- Data/window behavior:
  - `TokenDataset(path, context, stride=None)` now supports deterministic strided/sliding windows.
  - Default `stride=None` resolves to `context`, preserving the previous contiguous chunk behavior.
  - `token_packing_report()` now records `stride`, `tokens_per_epoch`, `overlap_tokens_per_window` and the packing strategy.
  - `achitic.train` adds `--stride`, prints `train windows=<n> tokens=<n> tokens/step=<n> stride=<n>`, records `train_data` in the run manifest and warns when tiny data repeats.
  - `scripts/split_val.py` performs deterministic hash-based line splitting by `--seed`.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py tests/test_train_metrics.py` -> `20 passed`.
  - `.venv/bin/python scripts/split_val.py --input examples/corpus.txt --train-out /tmp/achitic-nano-x-train.txt --val-out /tmp/achitic-nano-x-val.txt --val-ratio 0.2 --seed achitic-nano-x` -> `total_lines=6`, `train_lines=2`, `val_lines=4`.
  - `.venv/bin/python -m pytest -q` -> `57 passed, 1 skipped`.
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-nano-x-clean.txt` -> `documents: 6`.
  - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-nano-x-clean.txt --prefix /tmp/achitic-nano-x-sp --vocab 8000 --allow-reserved-padding` -> tokenizer stats printed.
  - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-nano-x-clean.txt --tokenizer /tmp/achitic-nano-x-sp.model --out /tmp/achitic-nano-x.bin` -> `tokens: 131`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-nano-x-datawarn.pt --metrics /tmp/achitic-nano-x-datawarn-metrics.jsonl --run-manifest /tmp/achitic-nano-x-datawarn-manifest.json --tokenizer /tmp/achitic-nano-x-sp.model` -> smoke train passed with startup report and repeat warning.
- Nano smoke data evidence:
  - Startup report: `train windows=1 tokens=131 tokens/step=128 stride=128`.
  - Warning: `train token budget 384 exceeds unique target tokens 128; data will repeat during training`.
  - Manifest `train_data`: `windows=1`, `total_tokens=131`, `used_target_tokens=128`, `tokens_per_epoch=128`, `wasted_target_tokens=2`, `waste_ratio=0.015384615384615385`.
- Known risks:
  - Stride overlap increases token presentations, not real data diversity.
  - Tiny/Mini training remains blocked until approved data, provenance, privacy, license and contamination evidence exist.
- Next allowed task: `NANO-X-KVCACHE-001`.

### NANO-X-KVCACHE-001 - Cached Generation

Business objective: inference should have a tested KV-cache path before edge and larger-model generation work depends on it.

Audit coverage: `P2-1`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Checklist:

- [x] Add a cache-aware inference path without changing training `forward` semantics.
- [x] RoPE accepts position offset for cached decoding.
- [x] GQA behavior remains equivalent with cache.
- [x] Add tests comparing cached and uncached greedy generation.
- [x] Add tests comparing per-step logits within tolerance.
- [x] Test a prompt close to `context` length.
- [x] Keep causality and existing model tests passing.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_model.py
.venv/bin/python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16
```

PASS criteria:

- Greedy cached and uncached generation produce identical token IDs.
- Logits differ by less than the recorded tolerance.
- Existing train forward and loss behavior are unchanged.

Completion evidence:

- Files changed:
  - `achitic/model.py`
  - `tests/test_model.py`
  - `docs/pipeline/task_nano_x.md`
- Runtime behavior:
  - Training `forward(ids, targets=None)` semantics remain unchanged for existing call sites.
  - `rope()` now accepts a position `offset` for cached decoding.
  - `Attention` stores cache before GQA repeat as `(k, v)` with shape `[batch, kv_heads, seq, head_dim]`.
  - `forward_cached(ids, cache=None, start_pos=0)` returns logits and the updated per-layer cache.
  - `forward_cached()` rejects cache length and `start_pos` mismatches instead of silently using inconsistent positions.
  - `generate(..., use_cache=True)` uses the cache path by default, while `use_cache=False` preserves the old uncached loop.
  - When the context window is full, cached generation rebuilds the window cache to preserve the previous sliding-window semantics exactly.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_model.py` -> `15 passed`.
  - `.venv/bin/python -m pytest -q` -> `64 passed, 1 skipped`.
  - `.venv/bin/python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16` -> passed.
- Parity evidence:
  - Cached prefill logits match uncached logits with `torch.allclose(..., atol=1e-5)`.
  - Cached per-step logits match uncached prefix logits with `torch.allclose(..., atol=1e-5)`.
  - Cached and uncached greedy generation produce identical token IDs.
  - Near-context-window cached generation matches uncached greedy generation.
  - Cache length and `start_pos` mismatch raises `ValueError`.
- Known risks:
  - Cache parity is verified on CPU tests.
  - The exact old sliding-window behavior is preserved by rebuilding the cache when the window is full; future speed optimization beyond the context limit must document any positional-semantics change.
- Next allowed task: `NANO-X-DOC-001`.

### NANO-X-DOC-001 - Documentation And Measurement Cleanup

Business objective: release docs must describe the actual Nano artifact, remove private machine paths and avoid unsupported claims.

Audit coverage: `P2-3`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Checklist:

- [x] Remove `<local-media-path>` and `<local-home-path>` from release docs/packages and selected pipeline evidence.
- [x] Replace local paths with repo-relative paths or `<local checkout>`.
- [x] Add measured smoke losses to `docs/releases/nano/EVAL_REPORT.md`.
- [x] Add actual `nano.pt` size split: weights vs optimizer/RNG state.
- [x] Add parameter allocation table to `MODEL_CARD.md`.
- [x] Make clear that Nano output quality is not validated.
- [x] Make clear that GGUF/quantized artifacts need their own llama.cpp load-and-generate evidence.
- [x] Sync docs into the current local release package only after checksums are regenerated.

Required validation:

```bash
rg -n "<local-media-path>|<local-home-path>" docs/releases/nano releases/nano docs/pipeline/task_nano.md
.venv/bin/python -m pytest -q tests/test_export_guard.py
```

PASS criteria:

- No private local paths remain in release-facing docs.
- Docs include actual measured Nano limitations and artifact facts.
- Export wording remains guarded.

Completion evidence:

- Files changed:
  - `docs/releases/nano/MODEL_CARD.md`
  - `docs/releases/nano/EVAL_REPORT.md`
  - `docs/releases/nano/ARTIFACT_MANIFEST.md`
  - `docs/releases/nano/ISO_TECHNICAL_SPEC.md`
  - `releases/nano/COMMAND_LOG.md`
  - `releases/nano/INSTALL_USAGE.md`
  - `releases/nano/ISO_TECHNICAL_SPEC.md`
  - `releases/nano/SHA256SUMS`
  - `docs/pipeline/task_nano.md`
  - `docs/pipeline/task_nano_x.md`
- Documentation updates:
  - Removed private local paths from release-facing docs and selected Nano pipeline evidence.
  - Added Nano parameter allocation table: embedding/tied head `2,048,000`, attention `786,432`, SwiGLU FFN `2,162,688`, RMSNorm `2,304`, total `4,999,424`.
  - Added checkpoint size split for `releases/nano/nano.pt`: full file `60,043,760` bytes, model unique tensor storage `19,997,696`, optimizer tensor storage `39,995,544`, RNG tensor storage `5,056`, serialization overhead `45,464`.
  - Added measured doc smoke train losses: step 1 `9.042657852172852`, step 2 `8.647053718566895`, step 3 `8.375679969787598`.
  - Updated current validation facts to `64 passed, 1 skipped` and kept original v0.1.1 publication counts clearly labeled where retained as historical command-log data.
  - Kept Nano quality limitations explicit and preserved the GGUF/quantization llama.cpp evidence guard.
  - Regenerated local release package checksums after package doc edits.
- Commands run:
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-nano-x-doc-clean.txt` -> `documents: 6`.
  - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-nano-x-doc-clean.txt --prefix /tmp/achitic-nano-x-doc-sp --vocab 8000 --allow-reserved-padding` -> tokenizer stats printed with `reserved_ratio=0.903125`.
  - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-nano-x-doc-clean.txt --tokenizer /tmp/achitic-nano-x-doc-sp.model --out /tmp/achitic-nano-x-doc.bin` -> `tokens: 131`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x-doc.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-nano-x-doc-smoke.pt --metrics /tmp/achitic-nano-x-doc-metrics.jsonl --run-manifest /tmp/achitic-nano-x-doc-manifest.json --tokenizer /tmp/achitic-nano-x-doc-sp.model` -> passed.
  - Private local path scan across release-facing docs and packages -> no matches.
  - `sha256sum -c releases/nano/SHA256SUMS` -> all 12 package assets OK.
  - `.venv/bin/python -m pytest -q tests/test_export_guard.py` -> `4 passed`.
  - `.venv/bin/python -m pytest -q` -> `64 passed, 1 skipped`.
- Known risks:
  - Nano remains a 3-step scratch smoke artifact, not a quality model.
  - The local release package docs were refreshed and checksums regenerated, but public publication still belongs to later publish/package rows.
- Next allowed task: `NANO-X-SMOKE-001`.

### NANO-X-SMOKE-001 - Integrated Regression And Smoke Gate

Business objective: prove the fixed Nano pipeline still runs end to end before packaging.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Checklist:

- [x] Run full test suite.
- [x] Run prepare/tokenizer/encode/train/chat Nano smoke with explicit reserved-padding flag.
- [x] Run Tiny smoke or dry-run path affected by shared train/eval/tokenizer changes.
- [x] Run release checkpoint chat from `releases/nano/nano.pt`.
- [x] Run weights-only chat if `NANO-X-CKPTSAFE-001` produced a safe artifact.
- [x] Run exporter CPU tests and optional llama.cpp evidence if GGUF is in scope.
- [x] Save command output summary in this file or a v0.2.0 release plan.

Required validation:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-nano-x-clean.txt
.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-nano-x-clean.txt --prefix /tmp/achitic-nano-x-sp --vocab 8000 --allow-reserved-padding
.venv/bin/python -m achitic.cli encode --input /tmp/achitic-nano-x-clean.txt --tokenizer /tmp/achitic-nano-x-sp.model --out /tmp/achitic-nano-x.bin
.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-nano-x.pt
.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-nano-x.pt --tokenizer /tmp/achitic-nano-x-sp.model --prompt "Xin chao" --tokens 16
```

PASS criteria:

- Full tests pass.
- Nano smoke train writes a checkpoint.
- Chat runs without tokenizer/config mismatch.
- Any changed shared path has a Tiny-compatible smoke or documented blocker.

Completion evidence:

- Files changed:
  - `docs/pipeline/task_nano_x.md`
- Full regression:
  - `.venv/bin/python -m pytest -q` -> `64 passed, 1 skipped`.
- Nano smoke:
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-nano-x-smoke-clean.txt` -> `documents: 6`.
  - `.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-nano-x-smoke-clean.txt --prefix /tmp/achitic-nano-x-smoke-sp --vocab 8000 --allow-reserved-padding` -> `reserved_ratio=0.903125`, `vocab_size=8000`.
  - `.venv/bin/python -m achitic.cli encode --input /tmp/achitic-nano-x-smoke-clean.txt --tokenizer /tmp/achitic-nano-x-smoke-sp.model --out /tmp/achitic-nano-x-smoke.bin` -> `tokens: 131`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x-smoke.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-nano-x-smoke.pt --metrics /tmp/achitic-nano-x-smoke-metrics.jsonl --run-manifest /tmp/achitic-nano-x-smoke-manifest.json --tokenizer /tmp/achitic-nano-x-smoke-sp.model` -> passed.
  - Nano train report: `train windows=1 tokens=131 tokens/step=128 stride=128`; final step `3`; losses `9.042657852172852`, `8.647053718566895`, `8.375679969787598`; `tokens_seen=384`.
  - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-nano-x-smoke.pt --tokenizer /tmp/achitic-nano-x-smoke-sp.model --prompt "Xin chao" --tokens 16` -> passed.
- Release/package smoke:
  - `.venv/bin/python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16` -> passed.
  - `sha256sum -c releases/nano/SHA256SUMS` -> all 12 package assets OK.
- Weights-only safe-load smoke:
  - `.venv/bin/python scripts/export_weights.py --checkpoint releases/nano/nano.pt --out /tmp/achitic-nano-x-smoke-fp16.safetensors --dtype fp16` -> passed, `tensor_count=38`, `dtype=fp16`.
  - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-nano-x-smoke-fp16.safetensors --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16` -> passed.
- Exporter/GGUF guard smoke:
  - `.venv/bin/python -m pytest -q tests/test_export_gguf.py tests/test_verify_gguf.py tests/test_export_guard.py` -> `11 passed, 1 skipped`.
  - The skipped test is the optional pinned llama.cpp integration because `LLAMA_CPP_DIR` is not set.
  - GGUF remains excluded from the release package; no GGUF or quantized artifact is claimed verified.
- Tiny-compatible dry-run:
  - Created `/tmp/achitic-nano-x-tiny-dryrun.bin` with `1025` synthetic int32 token IDs, max ID `1024`, within Tiny `vocab_size=12000`.
  - `.venv/bin/python -m achitic.train --config configs/tiny.json --data /tmp/achitic-nano-x-tiny-dryrun.bin --steps 1 --batch 1 --accum 1 --out /tmp/achitic-nano-x-tiny-dryrun.pt --metrics /tmp/achitic-nano-x-tiny-dryrun-metrics.jsonl --run-manifest /tmp/achitic-nano-x-tiny-dryrun-manifest.json` -> passed.
  - Tiny dry-run report: `train windows=2 tokens=1025 tokens/step=512 stride=512`; final step `1`; train loss `9.50780963897705`; config `vocab_size=12000`, `context=512`.
- Known risks:
  - Tiny dry-run uses synthetic token IDs only. It does not unblock Tiny training, dataset approval, tokenizer approval or Tiny publication.
  - Nano remains a smoke/pipeline artifact, not a language-quality model.
  - No llama.cpp integration was run in this row because GGUF is out of the release package scope and `LLAMA_CPP_DIR` is unset.
- Next allowed task: `NANO-X-PKG-001`.

### NANO-X-PKG-001 - Nano v0.2.0 Candidate Package

Business objective: create a local package ready for human review and public release, without secrets or unsupported artifacts.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Expected candidate asset set:

- `README.md`
- `INSTALL_USAGE.md`
- `MODEL_CARD.md`
- `ARTIFACT_MANIFEST.md`
- `EVAL_REPORT.md`
- `SECURITY.md`
- `USAGE_TERMS.md`
- `ISO_TECHNICAL_SPEC.md`
- `RELEASE_NOTES.md`
- `SHA256SUMS`
- `LICENSE`
- `NOTICE`
- `nano.json`
- `tokenizer.model`
- `tokenizer.vocab`
- `nano.pt` or an explicitly versioned replacement checkpoint
- optional `nano-fp16.safetensors` if `NANO-X-CKPTSAFE-001` PASS
- optional GGUF only if `NANO-X-LLAMA-001` PASS for that exact artifact

Checklist:

- [x] Create `docs/releases/nano/V0_2_0_RELEASE_PLAN.md`.
- [x] Create or refresh local package directory, for example `releases/nano-v0.2.0/`.
- [x] Include only approved artifacts.
- [x] Regenerate `SHA256SUMS`.
- [x] Verify checksums.
- [x] Confirm no `github_token.txt`, `.venv`, `runs/`, local private paths or private data are included.

Required validation:

```bash
sha256sum -c releases/nano-v0.2.0/SHA256SUMS
rg -n "github_token|<local-media-path>|<local-home-path>|BEGIN .*PRIVATE|api[_-]?key|token" releases/nano-v0.2.0 docs/releases/nano
```

PASS criteria:

- Candidate package has complete docs, checksums and explicit artifact scope.
- Assets align with the evidence rows above.

Completion evidence:

- Files changed:
  - `docs/releases/nano/V0_2_0_RELEASE_PLAN.md`
  - `docs/releases/nano/PUBLISH_INPUTS.md`
  - `docs/releases/nano/ISO_TECHNICAL_SPEC.md`
  - `releases/nano-v0.2.0/README.md`
  - `releases/nano-v0.2.0/INSTALL_USAGE.md`
  - `releases/nano-v0.2.0/MODEL_CARD.md`
  - `releases/nano-v0.2.0/ARTIFACT_MANIFEST.md`
  - `releases/nano-v0.2.0/EVAL_REPORT.md`
  - `releases/nano-v0.2.0/SECURITY.md`
  - `releases/nano-v0.2.0/USAGE_TERMS.md`
  - `releases/nano-v0.2.0/ISO_TECHNICAL_SPEC.md`
  - `releases/nano-v0.2.0/RELEASE_NOTES.md`
  - `releases/nano-v0.2.0/SHA256SUMS`
  - `releases/nano-v0.2.0/LICENSE`
  - `releases/nano-v0.2.0/NOTICE`
  - `releases/nano-v0.2.0/nano.json`
  - `releases/nano-v0.2.0/tokenizer.model`
  - `releases/nano-v0.2.0/tokenizer.vocab`
  - `releases/nano-v0.2.0/nano.pt`
  - `releases/nano-v0.2.0/nano-fp16.safetensors`
  - `docs/pipeline/task_nano_x.md`
- Candidate package:
  - Directory: `releases/nano-v0.2.0/`.
  - Asset count in `SHA256SUMS`: `16`.
  - Full checkpoint: `nano.pt`, `60,043,760` bytes, SHA256 `f067c5f9dad26cd78d2d89b9a3347444039d0dda53e8230b351c0a28958e761b`.
  - Weights-only safe artifact: `nano-fp16.safetensors`, `10,002,480` bytes, SHA256 `7912525f3036e07176f373cd339f5e08347aba788846f9f319dd1493b6bdaa5c`.
  - Tokenizer artifacts: `tokenizer.model`, `tokenizer.vocab`.
  - Config artifact: `nano.json`.
  - Docs: README, install/usage, model card, eval report, security, usage terms, ISO-aligned spec, release notes and artifact manifest.
  - Explicitly excluded: GGUF and quantized artifacts.
- Commands run:
  - `mkdir -p releases/nano-v0.2.0` -> package directory created.
  - Copied approved Nano artifacts from `releases/nano/`: `nano.pt`, `tokenizer.model`, `tokenizer.vocab`, config as `nano.json`, `LICENSE`, `NOTICE`.
  - `.venv/bin/python scripts/export_weights.py --checkpoint releases/nano/nano.pt --out releases/nano-v0.2.0/nano-fp16.safetensors --dtype fp16` -> passed, `tensor_count=38`, metadata `format=achitic_weights_only`.
  - `sha256sum -c releases/nano-v0.2.0/SHA256SUMS` -> all 16 candidate assets OK.
  - `.venv/bin/python -m achitic.cli chat --checkpoint releases/nano-v0.2.0/nano.pt --tokenizer releases/nano-v0.2.0/tokenizer.model --prompt "Xin chao" --tokens 16` -> passed.
  - `.venv/bin/python -m achitic.cli chat --checkpoint releases/nano-v0.2.0/nano-fp16.safetensors --tokenizer releases/nano-v0.2.0/tokenizer.model --prompt "Xin chao" --tokens 16` -> passed.
  - Secret and private local path scan across candidate assets and release docs -> no matches.
  - Broad task scan with `|token` was also inspected; remaining hits are expected tokenizer/token wording and `tokenizer.vocab` content, not credentials.
- Package hashes:
  - `releases/nano-v0.2.0/SHA256SUMS` SHA256: `db917edf91abdfba4a558faffc5d14913b9e3c7c1abc97053b067adcf1a7f841`.
  - `docs/releases/nano/V0_2_0_RELEASE_PLAN.md` SHA256: `50b6da10456f16c815e6666b59ed4603ac4814d17c44ba90b58e560ab413d243`.
- Known risks:
  - Package is local-only until `NANO-X-PUBLISH-001` confirms owner/tag/artifact scope and publishes or defers.
  - Nano remains a smoke artifact; no language-quality, production, GGUF or quantization claim is made.
- Historical note: this row packaged the pre-supplement candidate; `NANO-MEAN-001` and `NANO-X-RETRAIN-001` subsequently replaced it with the refreshed candidate.
- Next allowed task: `NANO-MEAN-001` planning/data approval gates, or remaining addendum implementation rows without file-lock overlap.

### NANO-X-PUBLISH-001 - Publish Or Defer Nano v0.2.0

Business objective: publish the new Nano version only after package evidence is complete, or record a clean deferral.

Status: PASS

Owner: Codex

Started: 2026-10-15

Finished: 2026-10-15

Checklist:

- [x] Confirm repo owner/org and release tag.
- [x] Confirm code and artifact license.
- [x] Confirm no private data/tokens are included.
- [x] Confirm whether this release includes GGUF; if yes, cite `NANO-X-LLAMA-001` evidence.
- [x] Confirm whether merged audit addendum rows are excluded from this tag or publication is deferred until they pass.
- [x] Confirm `NANO-MEAN-001` is included in the refreshed v0.2.0 candidate and cite dataset/license/privacy/contamination evidence.
- [x] Create tag `nano-v0.2.0` from the intended source state, or record deferral.
- [x] Upload release assets, or record why publish is blocked.
- [x] Record release URL or deferral reason.

PASS criteria:

- Release exists with expected assets and checksums, or publish is explicitly deferred.
- No model-quality claim is added.

Completion evidence:

- Repository: `https://github.com/SincereVirtueDev/achitic-lm` (public, Apache-2.0).
- Source commit: `66ddcf328f73eb55805de5c96f1164812714c5c2` on `main`.
- Annotated tag: `nano-v0.2.0`; peeled tag commit matches the source commit.
- Release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.2.0`.
- GitHub release ID: `413374113`; published at `2026-10-15T03:09:24Z` as a prerelease.
- Assets: `19` uploaded and public; all names, sizes and GitHub SHA256 digests match the local package.
- Public `SHA256SUMS` download matches local byte-for-byte; SHA256 `3ec914f84f7a8739173d8d94bedb9e0fc2faa35b4941788918c692e6f3979432`.
- Core assets: `nano.pt` SHA256 `91159067702c945c08fbd245f82ff1834a31e8aff77cc27920f11572315270b9`; `nano-fp16.safetensors` SHA256 `b945ecc7a608a85d5dda4b15cd7c7f7ce0dfc4f3b9508fda524c9b0ff6f88afd`.
- Source Git history excludes checkpoints, tokenizer binaries, safetensors, encoded corpora, local environments and `github_token.txt`.
- Release includes the complete merged audit addendum and `NANO-MEAN-001` evidence. No GGUF or quantized asset is included.
- Full tests on the committed tree: `91 passed, 1 skipped`; packaged `.pt` and safetensors inference output matched.
- Publication record: `docs/releases/nano/V0_2_0_PUBLICATION.md`.
- Next allowed row: `NANO-X-CLOSE-001`.

### NANO-X-CLOSE-001 - Closeout And Next-Model Unlock

Business objective: chốt Nano-X để Tiny/Mini/Small/350M/1B agents biết code path nào được phép kế thừa.

Status: PASS

Owner: Codex

Started: 2026-10-15

Finished: 2026-10-15

Checklist:

- [x] Confirm every previous row is `PASS`, or explicitly accepted as excluded from this release.
- [x] Record that the merged audit addendum and `NANO-MEAN-001` are included in the refreshed `nano-v0.2.0` candidate, or explicitly document any remaining exclusion.
- [x] Confirm `pytest -q` and Nano smoke pass.
- [x] Confirm Tiny shared-path smoke pass or documented blocker.
- [x] Update `docs/pipeline/01_FOUNDATION_SMOKE.md` with Nano-X status.
- [x] Update `docs/pipeline/task_upgrade_tiny.md` with any new prerequisite that genuinely applies to Tiny training/release.
- [x] Record whether Tiny can continue with current blockers unchanged.
- [x] Record whether Mini/Small/350M/1B may inherit exporter, safe-load, train-loop and tokenizer behavior.

PASS criteria:

- Nano v0.2.0 status is closed as `PUBLISHED`, `DEFERRED`, or `NO_GO`.
- Full audit closure is not claimed unless the addendum rows are `PASS` or explicitly excluded with next-version ownership.
- Next-model prerequisites are explicit and do not contradict Phase 2 Data/Tokenizer gates.

Completion evidence:

- Final decision: `PUBLISHED`; all `14 / 14` Nano-X rows and all `6 / 6` merged-audit addendum rows are `PASS`.
- Public prerelease: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.2.0`; immutable tagged source commit `66ddcf328f73eb55805de5c96f1164812714c5c2`.
- The release includes the refreshed tokenizer/config/checkpoint, approved Vietnamese meaning-smoke evidence and merged audit fixes. It excludes GGUF and quantized artifacts, so no unsupported llama.cpp or quantization claim is made.
- `.venv/bin/python -m pytest -q` -> `91 passed, 1 skipped in 67.59s`.
- Packaged Nano `.pt` and safetensors inference smokes passed and produced matching output on fixed prompts; the controlled meaning gate remains `10 / 10`.
- `sha256sum -c releases/nano-v0.2.0/SHA256SUMS` -> all `18 / 18` listed files passed.
- Tiny shared-path smoke with `configs/tiny.json` completed one CPU step: `loss=9.4865`, `lr=0.0003`, `tok/s=596.43`; measured Tiny parameter count is `23,058,944`.
- Tiny may inherit the exporter, safe checkpoint loading, train-loop, streaming data preparation, validation split, metrics, resume, KV-cache and tokenizer guard implementations.
- Tiny must not inherit Nano's `8k` tokenizer, token IDs as an artifact contract, checkpoint, corpus split or language-quality conclusions. Tiny training remains blocked by Phase 2 until an approved train/eval corpus and frozen `12k` tokenizer (`unk=0`, `bos=1`, `eos=2`, `pad=3`) pass provenance, license, privacy, deduplication and contamination gates.
- Mini, Small, 350M and 1B may inherit the same verified tooling paths only. This closeout does not unlock their training or publication gates.
- Closeout records were updated in `docs/pipeline/01_FOUNDATION_SMOKE.md`, `docs/pipeline/BACKLOG.md` and `docs/pipeline/task_upgrade_tiny.md`.

## Merged Audit Addendum Board

This board tracks audit rows added when `ACHITIC_NANO_AUDIT.md` was merged with the duplicate audit variant. These rows are part of the full audit contract, but they do not retroactively change the evidence already recorded for the original `13` Nano-X rows.

Addendum progress: `[xxxxxx] 100%`

Addendum backlog progress: `6 / 6`

Current addendum allowed rows:

- None. All addendum rows are complete.

Locked addendum rows:

- None.

```text
TODO        [ ] not claimed
CLAIMED     [>] owner set, no implementation edits yet
IN_PROGRESS [~] implementation edits in progress, file locks active
BLOCKED     [!] blocked with reason and next action
REVIEW      [?] implementation done, waiting for full gate/evidence
PASS        [x] evidence recorded and gate passed
```

### Addendum Checklist

| Mark | Backlog ID | Audit coverage | Owner | Started | Lock expires | Done when |
| --- | --- | --- | --- | --- | --- | --- |
| [x] | `NANO-X-PREP-001` | `P1-4` | Codex | 2026-10-14 | released | `prepare` handles text/JSONL safely and reports skip reasons |
| [x] | `NANO-X-STREAM-001` | `P1-5` | Codex | 2026-10-14 | released | Encode streams to disk and tokenizer training exposes large-corpus controls |
| [x] | `NANO-X-CONFIGLABEL-001` | `P2-3 addendum`, `P2-4` | Codex | 2026-10-14 | released | Config labels/parameter targets and divisibility policy are explicit |
| [x] | `NANO-X-ALIGN-001` | `P1-6` | Codex | 2026-10-14 | released | Alignment checkpoints resume and chat template behavior is tested |
| [x] | `NANO-X-QUANT-001` | `P2-4` | Codex | 2026-10-14 | released | Quantization fails or warns on fallback and has exact llama.cpp verification evidence |
| [x] | `NANO-X-RETRAIN-001` | `R-1` | Codex | 2026-10-14 | released | A fresh Nano candidate reflects the chosen addendum scope, or retrain is explicitly deferred |

### Addendum Stage Board

| Mark | Row | Depends on | Allowed write set | Required validation |
| --- | --- | --- | --- | --- |
| [x] | `NANO-X-PREP-001` | merged audit exists | `achitic/data.py`, CLI prepare path, prepare tests/docs | Mixed text/JSONL prepare tests pass and no valid JSON scalar line crashes |
| [x] | `NANO-X-STREAM-001` | `NANO-X-PREP-001` not `[~]` unless same owner | `achitic/data.py`, `achitic/tokenizer.py`, encode/tokenizer CLI/tests/docs | Streaming encode byte-equality test and tokenizer option tests pass |
| [x] | `NANO-X-CONFIGLABEL-001` | merged audit exists | `configs/*.json`, `docs/pipeline/00_MODEL_LADDER.md`, `docs/ARCHITECTURE.md`, config-param tests | Config parameter counts and old/new label policy are documented and tested |
| [x] | `NANO-X-ALIGN-001` | `NANO-X-CKPTSAFE-001` PASS | `achitic/alignment.py`, `achitic/cli.py`, checkpoint/chat-template tests/docs | Train -> SFT -> resume works; chat template tokenization and stop conditions pass |
| [x] | `NANO-X-QUANT-001` | `NANO-X-LLAMA-001` PASS, `NANO-X-CONFIGLABEL-001` decision recorded | `scripts/quantize.sh`, `scripts/verify_gguf.py`, quant tests/docs | Quant fallback is detected; exact artifact has llama.cpp load-and-generate/parity evidence |
| [x] | `NANO-X-RETRAIN-001` | all addendum implementation rows PASS or explicitly deferred | new release candidate dir, release docs, configs only if version escalates | Refreshed candidate contract, docs, checksums and validation pass |

### NANO-X-PREP-001 - Robust Prepare Format Handling

Business objective: `prepare` must survive real-world text files where some lines are valid JSON scalars, arrays or booleans, without losing plain text or crashing.

Audit coverage: `P1-4`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Depends on:

- No other row is editing `achitic/data.py` unless it is the same owner coordinating both rows.

Checklist:

- [x] Treat a line as JSONL only when `json.loads(line)` returns a dict with `text` as `str`.
- [x] For `auto` mode, keep valid JSON scalars/arrays/booleans as plain text instead of crashing.
- [x] Add `--format {auto,text,jsonl}` to the prepare CLI if the current CLI lacks it.
- [x] Report skip counters by reason: too short, duplicate, JSONL missing text, invalid type.
- [x] Add tests for mixed text, JSON scalar, JSON string and proper JSONL.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py
.venv/bin/python -m achitic.cli prepare --inputs <mixed-text-jsonl-fixture> --out /tmp/achitic-prepare-mixed.txt --format auto
```

PASS criteria:

- No `AttributeError` or equivalent crash on valid JSON scalar lines.
- `--format text` preserves a JSONL-looking line as raw text.
- `--format jsonl` handles missing or non-string `text` fields with a clear skip reason.

Completion evidence:

- Files changed:
  - `achitic/data.py`
  - `achitic/cli.py`
  - `tests/test_data_tokenizer_cli.py`
  - `docs/pipeline/task_nano_x.md`
- Behavior added:
  - `prepare(..., input_format="auto|text|jsonl", return_stats=True)`.
  - `auto` mode treats only JSON objects with string `text` as JSONL; JSON scalars, arrays and non-text objects stay as raw text.
  - `jsonl` mode skips invalid JSON, missing `text`, non-string `text` and non-object rows with explicit counters.
  - CLI `prepare` exposes `--format` and `--min-chars`, keeps the existing `documents: N` line, and prints `prepare_stats` JSON.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py` -> `17 passed`.
  - `.venv/bin/python -m achitic.cli prepare --help` -> shows `--format {auto,text,jsonl}` and `--min-chars`.
  - `.venv/bin/python -m pytest -q` -> `68 passed, 1 skipped`.
  - `.venv/bin/python -m achitic.cli prepare --inputs /tmp/achitic-prepare-mixed.txt --out /tmp/achitic-prepare-clean.txt --format auto --min-chars 10` -> `documents: 4`, `skipped_short: 1`, no JSON scalar crash.
  - `.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-nano-x-prep-clean.txt --format auto` -> `documents: 6`, all skip counters `0`.
  - `.venv/bin/python -m achitic.train --config configs/tiny.json --data /tmp/achitic-nano-x-prep-tiny.bin --steps 1 --batch 1 --accum 1 --out /tmp/achitic-nano-x-prep-tiny.pt --metrics /tmp/achitic-nano-x-prep-tiny-metrics.jsonl --run-manifest /tmp/achitic-nano-x-prep-tiny-manifest.json` -> passed, loss `9.5078`.
- Known risks:
  - `auto` mode intentionally preserves JSON objects without string `text` as raw text; use `--format jsonl` for strict JSONL ingestion.
  - Large-corpus memory behavior is owned by `NANO-X-STREAM-001`, not this row.
- Current addendum state after `NANO-X-QUANT-001` PASS:
  - Historical handoff waited for `NANO-MEAN-001`; both meaning and retrain rows are now `PASS`.

### NANO-X-STREAM-001 - Streaming Encode And Large-Corpus Tokenizer Controls

Business objective: data tooling must be usable for real Vietnamese corpus work without loading all token IDs or all tokenizer input sentences into memory.

Audit coverage: `P1-5`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Depends on:

- `NANO-X-PREP-001` not `[~]`, unless one owner is coordinating the same data module edits.

Checklist:

- [x] Change encode to write `int32` token IDs in bounded chunks instead of collecting the full corpus in a Python list.
- [x] Add or document `--workers` only if output order is deterministic.
- [x] Fail clearly when tokenizer vocab or token IDs cannot fit in `int32`.
- [x] Expose tokenizer training controls: `input_sentence_size`, `shuffle_input_sentence`, `num_threads`.
- [x] Log progress: lines processed, tokens processed and output bytes written.
- [x] Add byte-equality tests against the old small-corpus output.
- [x] Add a large synthetic corpus test with bounded memory, marked slow if needed.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py
.venv/bin/python -m achitic.cli encode --input examples/corpus.txt --tokenizer releases/nano/tokenizer.model --out /tmp/achitic-stream-encode.bin
```

PASS criteria:

- Small-corpus encoded `.bin` is byte-identical to the reference path.
- Large synthetic encode does not grow memory unbounded.
- Tokenizer training command records corpus sampling/thread parameters.

Completion evidence:

- Files changed:
  - `achitic/data.py`
  - `achitic/tokenizer.py`
  - `achitic/cli.py`
  - `tests/test_data_tokenizer_cli.py`
  - `docs/pipeline/task_nano_x.md`
- Behavior added:
  - `encode_corpus(..., chunk_tokens=..., return_stats=True)` streams `int32` token IDs in bounded chunks and keeps the old integer return by default.
  - Encode rejects invalid `chunk_tokens`, tokenizer vocab sizes `>= 2**31`, and token IDs outside int32 range.
  - CLI `encode` exposes `--chunk-tokens` and prints `encode_stats` with `lines`, `tokens`, `chunks`, `chunk_tokens` and `bytes_written`.
  - Tokenizer training exposes `input_sentence_size`, `shuffle_input_sentence` and `num_threads`; CLI adds `--input-sentence-size`, `--num-threads`, and `--no-shuffle-input-sentence`.
  - No `--workers` flag was added because deterministic parallel output ordering is not implemented yet; this row keeps the encode path serial and deterministic.
- Tests added:
  - Streaming encode byte-equality against a reference list-based encoding.
  - Large synthetic encode with many chunks and bounded `tracemalloc` peak.
  - CLI encode stats output.
  - Tokenizer training metadata and CLI controls.
  - int32 range guards for vocab and token IDs.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py` -> `21 passed`.
  - `.venv/bin/python -m achitic.cli encode --input examples/corpus.txt --tokenizer releases/nano/tokenizer.model --out /tmp/achitic-stream-encode.bin --chunk-tokens 17` -> `tokens: 131`, `chunks: 6`, `bytes_written: 524`.
  - `.venv/bin/python -m achitic.cli tokenizer --input examples/corpus.txt --prefix /tmp/achitic-nano-x-stream-sp --vocab 8000 --allow-reserved-padding --input-sentence-size 1000 --num-threads 1 --no-shuffle-input-sentence` -> passed with `input_sentence_size: 1000`, `num_threads: 1`, `shuffle_input_sentence: false`.
  - `.venv/bin/python -m achitic.cli tokenizer --help` -> shows the new tokenizer large-corpus controls.
  - `.venv/bin/python -m pytest -q` -> `72 passed, 1 skipped`.
  - `.venv/bin/python -m achitic.train --config configs/tiny.json --data /tmp/achitic-nano-x-stream-tiny.bin --steps 1 --batch 1 --accum 1 --out /tmp/achitic-nano-x-stream-tiny.pt --metrics /tmp/achitic-nano-x-stream-tiny-metrics.jsonl --run-manifest /tmp/achitic-nano-x-stream-tiny-manifest.json` -> passed, loss `9.5078`.
- Known risks:
  - Streaming still encodes one source line at a time, so a single extremely long line can allocate that line's token list before chunking.
  - Deterministic multi-worker encode remains unimplemented by design; add it only with ordering tests.
- Current addendum state after `NANO-X-QUANT-001` PASS:
  - Historical handoff waited for `NANO-MEAN-001`; both meaning and retrain rows are now `PASS`.

### NANO-X-CONFIGLABEL-001 - Config Label And Quant-Friendly Shape Policy

Business objective: config filenames, model ladder docs and quantization-shape constraints must not mislead downstream agents about parameter targets or release compatibility.

Audit coverage: `P2-3 addendum`, `P2-4`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Depends on:

- No release artifact should be renamed in place.
- Published configs/checkpoints must remain loadable under their recorded names.

Checklist:

- [x] Add a parameter-count test for every `configs/*.json`.
- [x] Compare measured params with `docs/pipeline/00_MODEL_LADDER.md` target ranges.
- [x] Document whether legacy names like `50m.json`, `150m.json`, `1b.json` are aliases or will be superseded.
- [x] Document the rule: new quant-friendly configs should choose `dim`/`ffn_dim` values that satisfy the intended quantizer block constraints.
- [x] Do not mutate config files that already have released checkpoints without a version escalation note.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_config*.py tests/test_model.py
rg -n "30.7M|92.8M|668.3M|ffn_dim|quant" docs/pipeline/00_MODEL_LADDER.md docs/ARCHITECTURE.md
```

PASS criteria:

- Every config has a recorded measured parameter count.
- Legacy label mismatches are documented as aliases, deprecated names or future config changes.
- Quant-friendly shape requirements are written in architecture docs before any new quantized release is claimed.

Completion evidence:

- Files changed:
  - `tests/test_config_policy.py`
  - `docs/pipeline/00_MODEL_LADDER.md`
  - `docs/ARCHITECTURE.md`
  - `docs/pipeline/task_nano_x.md`
- Behavior/policy added:
  - Every `configs/*.json` has an exact measured parameter count locked by test and recorded in the model ladder.
  - `configs/nano.json` and `configs/tiny.json` are documented as active CPU target configs.
  - `configs/50m.json`, `configs/150m.json`, `configs/350m.json` and `configs/1b.json` are documented as legacy/candidate aliases with `WARN` label status, not verified size claims.
  - Quant-friendly config policy is documented: new quant-intended configs should prefer `dim`, `ffn_dim` and GQA KV projection widths that satisfy block constraints; incompatible quant fallback must not be marked verified.
  - No config file or released artifact was renamed or mutated.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_config*.py tests/test_model.py` -> `18 passed`.
  - `rg -n "30.7M|92.8M|668.3M|ffn_dim|quant" docs/pipeline/00_MODEL_LADDER.md docs/ARCHITECTURE.md` -> found measured rounded counts and quant/`ffn_dim` policy.
  - `.venv/bin/python -m pytest -q` -> `75 passed, 1 skipped`.
  - `.venv/bin/python -m achitic.train --config configs/tiny.json --data /tmp/achitic-configlabel-tiny.bin --steps 1 --batch 1 --accum 1 --out /tmp/achitic-configlabel-tiny.pt --metrics /tmp/achitic-configlabel-tiny-metrics.jsonl --run-manifest /tmp/achitic-configlabel-tiny-manifest.json` -> passed, loss `9.5088`.
- Known risks:
  - Legacy config filenames remain for compatibility. Future releases must either relabel them or introduce successor config filenames before making size claims.
  - Quant-friendly dimensions reduce fallback risk but do not verify any quantized artifact; exact llama.cpp load-and-generate evidence remains mandatory.
- Current addendum state after `NANO-X-QUANT-001` PASS:
  - Historical handoff waited for `NANO-MEAN-001`; both meaning and retrain rows are now `PASS`.

### NANO-X-ALIGN-001 - Alignment Checkpoint Resume And Chat Template

Business objective: SFT/DPO checkpoints must be resumable or explicitly weights-only, and chat must use the same conversation template as aligned training data.

Audit coverage: `P1-6`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Depends on:

- `NANO-X-CKPTSAFE-001` PASS.
- No other row is editing `achitic/cli.py` or checkpoint loading semantics.

Checklist:

- [x] Save alignment checkpoints with `checkpoint_format`, `step`, `optimizer`, RNG state and `stage`.
- [x] Let normal checkpoint loading understand aligned checkpoints.
- [x] Provide an explicit `--weights-only-resume` path for old aligned checkpoints that lack optimizer state.
- [x] Add `--chat-template {none,achitic}`.
- [x] Use the Achitic template by default when checkpoint metadata says `stage` is `sft` or `dpo`.
- [x] Add `--interactive` only if context truncation and history formatting are deterministic. Decision: do not add `--interactive` in this row because deterministic multi-turn history truncation is not implemented yet.
- [x] Stop generation on EOS or generated `<|user|>`.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_alignment*.py tests/test_checkpoint*.py tests/test_cli*.py
.venv/bin/python -m achitic.alignment --mode sft --help
.venv/bin/python -m achitic.cli chat --help
```

PASS criteria:

- Train -> SFT -> `train --resume` continues with increasing `step`.
- Chat template token sequence starts with BOS and `<|user|>` and ends the prompt context with `<|assistant|>`.
- Generation stops on EOS or `<|user|>` without leaking a new user turn.

Completion evidence:

- Files changed:
  - `achitic/alignment.py`
  - `achitic/train.py`
  - `achitic/cli.py`
  - `achitic/model.py`
  - `tests/test_alignment.py`
  - `tests/test_checkpoint.py`
  - `tests/test_cli.py`
  - `tests/test_model.py`
  - `docs/pipeline/task_nano_x.md`
- Behavior added:
  - SFT/DPO alignment checkpoints now save `checkpoint_format`, `resume_semantics`, `optimizer`, `step`, config, RNG state and `stage`.
  - `achitic.train --resume` can load new aligned checkpoints normally and can load old weights-only aligned checkpoints only when `--weights-only-resume` is explicit.
  - `chat` and `benchmark` expose `--chat-template {none,achitic}`. If omitted, checkpoints with `stage` `sft` or `dpo` default to the Achitic chat template; other checkpoints default to raw prompt mode.
  - Achitic chat template encodes `<|user|>{prompt}<|assistant|>` with BOS, and generation stop IDs include EOS plus `<|user|>` in template mode.
  - `generate()` accepts `stop_ids` and stops cached and uncached generation on custom stop tokens.
  - `--interactive` was intentionally not added because deterministic multi-turn truncation/history formatting is not yet implemented.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_alignment*.py tests/test_checkpoint*.py tests/test_cli*.py` -> `17 passed`.
  - `.venv/bin/python -m achitic.alignment --mode sft --help` -> shows alignment CLI help.
  - `.venv/bin/python -m achitic.cli chat --help` -> shows `--chat-template {none,achitic}`.
  - `.venv/bin/python -m achitic.train --help` -> shows `--weights-only-resume`.
  - `.venv/bin/python -m pytest -q tests/test_model.py` -> `16 passed`.
  - `.venv/bin/python -m pytest -q` -> `81 passed, 1 skipped`.
  - `.venv/bin/python -m achitic.alignment --mode sft --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --data examples/sft.jsonl --out /tmp/achitic-align-sft.pt --steps 1` -> passed, loss `8.833394050598145`.
  - `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-align-resume.bin --resume /tmp/achitic-align-sft.pt --steps 2 --batch 1 --accum 1 --out /tmp/achitic-align-resumed.pt --metrics /tmp/achitic-align-resumed-metrics.jsonl --run-manifest /tmp/achitic-align-resumed-manifest.json` -> resumed from SFT checkpoint and completed step `2`, loss `9.0467`.
  - `.venv/bin/python -m achitic.cli chat --checkpoint /tmp/achitic-align-sft.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 4` -> used aligned checkpoint default template and generated text.
  - `.venv/bin/python -m achitic.train --config configs/tiny.json --data /tmp/achitic-align-tiny.bin --steps 1 --batch 1 --accum 1 --out /tmp/achitic-align-tiny.pt --metrics /tmp/achitic-align-tiny-metrics.jsonl --run-manifest /tmp/achitic-align-tiny-manifest.json` -> Tiny dry-run passed, loss `9.5088`.
- Known risks:
  - Old aligned checkpoints without optimizer/RNG state are not exact resumes; `--weights-only-resume` restarts optimizer/RNG and emits warnings.
  - `chat` still prints the full decoded prompt plus generation. A later UX task may split prompt/output display, but this row only fixes template parity and stop conditions.
- Current addendum state after `NANO-X-QUANT-001` PASS:
  - Historical handoff waited for `NANO-MEAN-001`; both meaning and retrain rows are now `PASS`.

### NANO-X-QUANT-001 - Quantization Verification And Fallback Guard

Business objective: quantized artifacts must never be reported as verified when the exact artifact has not passed llama.cpp load-and-generate/parity checks, and quant fallback must be visible.

Audit coverage: `P2-4`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-14

Depends on:

- `NANO-X-LLAMA-001` PASS.
- `NANO-X-CONFIGLABEL-001` has recorded the shape policy.

Checklist:

- [x] Update `scripts/quantize.sh` to run exact-artifact verification after quantization.
- [x] Detect and print tensors that fallback because shape is not compatible with the requested quant type.
- [x] Fail when the configured top-1 match/logit-delta threshold is not met.
- [x] Do not include Q4/Q6/Q8 assets in a release unless each asset has its own verification record.
- [x] Add tests for log parsing/fallback detection where possible without requiring llama.cpp in default CPU CI.

Required validation:

```bash
.venv/bin/python -m pytest -q tests/test_verify_gguf.py tests/test_export_guard.py
LLAMA_CPP_DIR=<pinned-llama.cpp> scripts/quantize.sh <f16.gguf> <quant.gguf> Q4_K_M
```

PASS criteria:

- Quant script exits nonzero when fallback or parity violates policy unless the caller explicitly allows it for experimental output.
- Release docs cite exact quant artifact checksum and exact llama.cpp evidence before any quantized asset is marked verified.

Completion evidence:

- Files changed:
  - `scripts/quantize.sh`
  - `scripts/quantize_policy.py`
  - `tests/test_verify_gguf.py`
  - `docs/pipeline/06_EXPORT_EDGE.md`
  - `docs/pipeline/task_nano_x.md`
- Behavior added:
  - `scripts/quantize.sh` now wraps pinned `llama-quantize`, records `<artifact>.quantize.log`, writes `<artifact>.fallbacks.json`, and runs `scripts/verify_gguf.py` against the exact quantized output.
  - `scripts/quantize_policy.py` parses quantization logs for fallback/fall-back lines, summarizes affected tensor-like names, and enforces `normal.max_abs_delta`, `normal.top1_match`, and report status.
  - Quantization fails by default on fallback or parity failure. `--allow-experimental` keeps the local artifact but prints that it is not publishable verified evidence.
  - Thresholds, prompt, context, generated-token count, checkpoint and tokenizer paths are configurable for per-artifact verification.
  - No Q4/Q6/Q8 release asset was added or marked verified by this row.
- Commands run:
  - `.venv/bin/python -m pytest -q tests/test_verify_gguf.py tests/test_export_guard.py` -> `10 passed, 1 skipped`.
  - `scripts/quantize.sh --help` -> usage and policy options printed.
  - `.venv/bin/python scripts/quantize_policy.py --help` -> `check-fallback` and `check-report` commands printed.
  - `.venv/bin/python -m pytest -q` -> `85 passed, 1 skipped`.
  - `ls -la /tmp/llama.cpp /tmp/achitic-nano-x.gguf /tmp/llama.cpp/build/bin/llama-quantize /tmp/llama.cpp/build/bin/llama-cli` -> all missing, so no real quantized release artifact was verified in this row.
- Known risks:
  - Exact llama.cpp quantization verification still must be run on each future quantized asset before that asset can be published.
  - Nano/Tiny configs with non-quant-friendly tensor shapes may trigger fallback; that is now visible and fails the release policy unless explicitly experimental.
  - `--allow-experimental` artifacts must stay local and must not be listed as verified release assets.
- Next allowed addendum task:
  - Historical handoff was `NANO-X-RETRAIN-001`; that row is now `PASS`.

### NANO-X-RETRAIN-001 - Fresh Nano Candidate After Addendum

Business objective: create a new Nano release candidate only after the merged audit scope and version boundary are clear.

Audit coverage: `R-1`.

Status: PASS

Owner: Codex

Started: 2026-10-14

Finished: 2026-10-15

Scope note: the unpublished local `nano-v0.2.0` package was rebuilt as one consistent real-corpus tokenizer/checkpoint/release contract.

Depends on:

- `NANO-X-PREP-001`, `NANO-X-STREAM-001`, `NANO-X-CONFIGLABEL-001`, `NANO-X-ALIGN-001` and `NANO-X-QUANT-001` are `PASS`, or explicitly deferred.
- Owner chooses one version target:
  - `nano-v0.2.0` refresh if the existing v0.2.0 package has not been publicly tagged/published and the owner accepts replacing the local candidate artifact set.
  - `nano-v0.2.1` for tooling/doc/package refresh that reuses existing config/tokenizer/checkpoint.
  - `nano-v0.3.0` if tokenizer, config, `ffn_dim`, checkpoint format or trained weights change after v0.2.0 is public, or if the owner override is revoked.
- Dataset/tokenizer decision is recorded. Real corpus work must use an approved dataset card and contamination/privacy/license gates.

Checklist:

- [x] Choose release tag and explain why it is patch/minor.
- [x] Do not retrain on `examples/corpus.txt` for the meaning supplement; the existing package remains smoke-only evidence.
- [x] If retraining on real corpus, cite the approved dataset card and split/contamination reports.
- [x] Train tokenizer only if the release version allows tokenizer contract changes.
- [x] Train Nano from scratch or resume only from an explicitly allowed AchiticLM scratch checkpoint.
- [x] Produce full checkpoint and optional weights-only artifact.
- [x] Include GGUF/quantized assets only when exact llama.cpp verification exists.
- [x] Regenerate release docs, manifest and checksums.

Required validation:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m achitic.train --config <nano-config> --data <train-bin> --steps <n> --out <candidate-ckpt> --metrics <metrics.jsonl> --run-manifest <manifest.json>
.venv/bin/python -m achitic.cli chat --checkpoint <candidate-ckpt> --tokenizer <candidate-tokenizer> --prompt "Xin chao" --tokens 16
sha256sum -c <candidate-release-dir>/SHA256SUMS
```

PASS criteria:

- Candidate artifacts have a consistent config/tokenizer/checkpoint contract.
- Release docs state whether the checkpoint is smoke, memorization, meaning-smoke or real-data trained.
- No unsupported language-quality, factuality, safety, GGUF or quantization claim is added.

Planning decision:

- Version target remains `nano-v0.2.0` refresh because the package is a local unpublished candidate and the owner explicitly folded the real Vietnamese meaning-smoke supplement into v0.2.0 before publication.
- `nano-v0.2.1` is not used because the intended supplement changes tokenizer/checkpoint artifacts, not documentation only.
- `nano-v0.3.0` is not used unless `nano-v0.2.0` has already been publicly tagged/published or the owner revokes the v0.2.0 override.
- The refreshed `releases/nano-v0.2.0/` package replaces the stale pre-supplement local candidate and is ready for the publish task.
- The approved data card records the source shard, checksums, split, privacy heuristics, dedup and zero fixed-prompt contamination.

Decision evidence:

- Files changed:
  - `docs/data/NANO_MEANING_DATASET_CARD.md`
  - `docs/data/nano_meaning_corpus_manifest.json`
  - `docs/data/nano_meaning_sft_manifest.json`
  - `docs/eval/NANO_MEANING_SMOKE_REPORT.md`
  - `docs/releases/nano/V0_2_0_RETRAIN_DECISION.md`
  - `docs/releases/nano/V0_2_0_RELEASE_PLAN.md`
  - `releases/nano-v0.2.0/*`
  - `docs/pipeline/task_nano_x.md`
- Refreshed candidate:
  - Scratch pretraining: `5000` CPU FP32 steps on `3,502,198` train token IDs.
  - Alignment: `800` SFT steps on `80` project-authored rows.
  - Core artifact SHA256: `nano.pt` `91159067702c945c08fbd245f82ff1834a31e8aff77cc27920f11572315270b9`; `nano-fp16.safetensors` `b945ecc7a608a85d5dda4b15cd7c7f7ce0dfc4f3b9508fda524c9b0ff6f88afd`.
  - Package checksum manifest SHA256: `3ec914f84f7a8739173d8d94bedb9e0fc2faa35b4941788918c692e6f3979432`.
  - Full and weights-only artifacts preserve `stage=sft`, `step=800`, vocab `8000`, and produce identical deterministic outputs for all 10 fixed prompts.
- Commands run:
  - `.venv/bin/python -m pytest -q` -> `91 passed, 1 skipped`.
  - Tiny shared-path smoke train -> PASS for one CPU step.
  - Full and safetensors sample reports -> `10/10` automatic PASS each with identical output.
  - `sha256sum -c releases/nano-v0.2.0/SHA256SUMS` -> all 18 package files `OK`.
  - Secret/private-path scan -> no matches.
- Known risks:
  - Post-SFT held-out Wikipedia loss/perplexity (`4.5470` / `94.35`) is worse than pre-SFT (`3.9901` / `54.06`).
  - The 10 prompts are near the SFT intent domain, so no broad quality/generalization claim is supported.
  - GGUF and quantized artifacts remain excluded.
- Next allowed row:
  - `NANO-X-PUBLISH-001`.

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

## Nano v0.2.0 Publication Gate

Nano v0.2.0 may be published only when all statements below are true:

- No pretrained weights are introduced.
- Tokenizer ID, vocabulary size and checkpoint config match for every released checkpoint/weights artifact.
- `pytest -q` passes.
- Nano smoke train and chat pass.
- Tiny shared-path smoke or dry-run evidence is recorded for changed train/tokenizer/eval code.
- Safe loading behavior is documented for `.pt` and weights-only artifacts.
- Release docs include model card, artifact manifest, eval report, security note, usage terms, checksums and install/use instructions.
- No local private paths, credentials or non-audited data are included.
- GGUF or quantized assets are either excluded, or have exact pinned llama.cpp load-and-generate evidence.
- Docs continue to say Nano is a smoke/pipeline artifact, not a production or factual-quality model.
- The merged audit addendum is either completed or explicitly documented as next-version scope; do not claim full audit closure while addendum rows remain open.
- Owner override is honored: the real Vietnamese meaning-smoke supplement is included in `nano-v0.2.0`, so `NANO-MEAN-001` and its dataset gates must pass before the refreshed v0.2.0 package can be published.

## Nano v0.2.0 Meaning Supplement

Owner decision on 2026-10-14: this task is no longer deferred to a later release. Include it directly in the unpublished `nano-v0.2.0` candidate as a supplement, then rebuild the v0.2.0 package evidence from the refreshed tokenizer/config/checkpoint.

### NANO-MEAN-001 - Controlled Meaningful Sentence Smoke

Business objective: tạo checkpoint Nano v0.2.0 bổ sung có thể sinh câu ngắn có nghĩa trong phạm vi prompt kiểm soát, làm bước đệm trước Tiny quality/eval work. Đây không phải benchmark chất lượng tổng quát.

Release target: refreshed `nano-v0.2.0` candidate package.

Status: PASS

Owner: Codex

Started: 2026-10-15

Finished: 2026-10-15

Depends on:

- Explicit owner approval to include this supplement in `nano-v0.2.0` before closeout. Recorded on 2026-10-14.
- Approved dataset card for the meaning-smoke corpus.
- No pretrained weights.
- No third-party/proprietary/private data unless provenance, license, privacy and contamination checks are recorded.
- The existing local `releases/nano-v0.2.0/*` artifact evidence is treated as stale after this task starts and must be regenerated before publication.

Recommended real Vietnamese source:

- Primary: Vietnamese Wikipedia article dump, `https://dumps.wikimedia.org/viwiki/latest/viwiki-latest-pages-articles.xml.bz2`; observed latest snapshot on 2026-10-14 was dated 2026-10-01 and sized `1,158,035,363` bytes.
- Secondary: Vietnamese Wikisource dump, `https://dumps.wikimedia.org/viwikisource/latest/viwikisource-latest-pages-articles.xml.bz2`, only after page-level license/provenance filtering. Do not use it as the first meaning-smoke corpus.
- Dataset card: `docs/data/NANO_MEANING_DATASET_CARD.md`.
- Do not use Common Crawl, OSCAR, news, blog, forum or social data for this first meaning-smoke gate until rights, privacy and redistribution risk are reviewed.
- Use a refreshed tokenizer/checkpoint pair for this real-corpus meaning work and keep it inside the `nano-v0.2.0` artifact contract. The current Nano tokenizer has too little real-vocabulary coverage and must not be silently reused for a meaning-quality claim.

Allowed write set:

- `docs/data/NANO_MEANING_DATASET_CARD.md`
- optional approved corpus file such as `examples/nano_meaning_corpus.txt`
- optional split files under `docs/data/` or `/tmp` during smoke work
- `configs/nano*.json` and `releases/nano-v0.2.0/*` only when rebuilding the complete unpublished v0.2.0 candidate package
- train/eval/sample-report docs and tests needed for the meaning smoke gate
- refreshed `releases/nano-v0.2.0/` package only after validation passes

Checklist:

- [x] Define the target behavior as controlled sentence smoke, not general language quality.
- [x] Record allowed real Vietnamese source candidates in the dataset card.
- [x] Select Vietnamese Wikipedia as the first real Vietnamese source candidate for vocabulary expansion.
- [x] Decide by owner override that the real-corpus meaning-smoke path is folded into the refreshed `nano-v0.2.0` candidate before publication.
- [x] Download the selected dump only after owner approval and record URL, dump date, checksum and command.
- [x] Create or approve a small cleaned Vietnamese meaning-smoke corpus with provenance/license/privacy/contamination fields.
- [x] Train and audit a refreshed v0.2.0 tokenizer/checkpoint pair; if tokenizer changes, regenerate every dependent config, checkpoint, weights-only artifact, manifest and checksum together.
- [x] Train from scratch or resume only from an explicitly allowed AchiticLM scratch checkpoint; never import pretrained external weights.
- [x] Add fixed prompts for deterministic evaluation, for example:
  - `Giới thiệu AchiticLM Nano trong một câu.`
  - `Viết một câu ngắn về học máy.`
  - `Nói một câu về dữ liệu huấn luyện.`
  - `Tóm tắt mục đích của Nano.`
  - `Viết một câu an toàn về thử nghiệm phần mềm.`
- [x] Add automatic checks for generated output:
  - no `<|reserved_...|>` tokens,
  - at least one sentence terminator or clear sentence boundary,
  - length within a configured min/max token range,
  - reject mostly repeated substrings,
  - tokenizer/config/checkpoint vocab IDs match.
- [x] Add a manual review table for the fixed prompts, because "có nghĩa" cannot be fully proven by regex.
- [x] Run full tests, Nano smoke, meaning-smoke generation and release checkpoint chat before packaging.
- [x] Document all failures and limitations; do not claim factuality, safety, benchmark score or production readiness.

Required validation:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m achitic.cli sample-report --checkpoint <meaning-checkpoint> --tokenizer <meaning-tokenizer> --prompts <fixed-prompts.txt> --tokens 32 --out <meaning-report.jsonl>
rg -n "<\\|reserved_|quality benchmark|production-ready|factual QA" <meaning-release-docs>
```

PASS criteria:

- At least `8/10` fixed prompts produce a short complete sentence judged meaningful by the manual review table.
- `0/10` fixed prompt outputs contain reserved-token strings.
- No output is used as evidence of factuality or broad language quality.
- Dataset card records source, license, privacy check and contamination check.
- The refreshed v0.2.0 checkpoint/tokenizer/config contract is internally consistent and does not overwrite Nano v0.1.x artifacts.
- Existing local `nano-v0.2.0` package evidence is replaced with new evidence generated after the real-corpus supplement.

Known risks:

- Nano may still be too small or undertrained for robust meaningful output.
- A small synthetic corpus can teach fixed patterns but not broad language ability.
- If `nano-v0.2.0` has already been publicly tagged or published outside this local package, do not silently mutate that public artifact; record a corrected release action before publishing replacement assets.

Completion evidence:

- Source shard: Vietnamese Wikipedia `2026-10-01`, first article shard, official MD5 `8ccdb33e3b24dcd44c81e2cbd91fd626`, SHA256 `7cdf607f7db4e3f2d95c1732e2288f9d0ed02ebeaa1488cf75d923f5fb89f49d`.
- Corpus: `97,978` train and `2,022` eval sentences; `576` normalized and `12` near duplicates rejected; fixed-prompt contamination `0`.
- Tokenizer: vocab `8000`, IDs `unk=0`, `bos=1`, `eos=2`, `pad=3`, reserved ratio `0.0`, SHA256 `26c8b92336b85b26f8bdc3020496ce7c328e42c61ac322a03c85c9955a1ee50d`.
- Training: `5000` scratch CPU FP32 pretraining steps, then `800` SFT steps on `80` project-authored rows; no external pretrained weights.
- Meaning gate: `10/10` automatic PASS, `10/10` manual PASS, `0/10` reserved-token strings. Full and weights-only artifacts produce identical deterministic outputs.
- Held-out trade-off: pre-SFT loss/perplexity `3.9901` / `54.06`; post-SFT `4.5470` / `94.35`.
- Validation: full pytest `91 passed, 1 skipped`; Tiny shared-path one-step CPU smoke PASS; package secret/private-path scan returned no matches.
- Package: `18` files pass `sha256sum -c`; manifest SHA256 `3ec914f84f7a8739173d8d94bedb9e0fc2faa35b4941788918c692e6f3979432`.
- Evidence files: `docs/data/NANO_MEANING_DATASET_CARD.md`, `docs/data/nano_meaning_corpus_manifest.json`, `docs/data/nano_meaning_sft_manifest.json`, `docs/eval/NANO_MEANING_SMOKE_REPORT.md`, `releases/nano-v0.2.0/TRAINING_RUN_MANIFEST.json`.
- Claim boundary: this is a controlled near-domain meaning smoke, not broad fluency, factuality, safety, benchmark or production evidence.
- Next allowed row: `NANO-X-PUBLISH-001`.
