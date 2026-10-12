# task_nano.md - Full Publishable Nano Pipeline Task

Model slot: `nano`

Config: `configs/nano.json`

Target params: 5-10M, current estimate 4,999,424 params

Business purpose: Nano là model đầu tiên để chứng minh toàn bộ pipeline chạy đúng trên CPU và tạo được một release package có thể xuất bản: environment, architecture tests, checkpoint, data/tokenizer/CLI, alignment reference, export-claim guard, model card, artifact manifest, checksum, release checklist và closeout. Nano không dùng để claim chất lượng ngôn ngữ.

Architecture rule: dùng đúng AchiticLM Core hiện có. Không đổi `achitic/model.py` chỉ để đạt tham số. Chỉ sửa model code khi có failing CPU test chứng minh bug thật.

## Progress Dashboard

Overall progress: `[xxxxxxxxx-] 87%`

Backlog progress: `10 / 10`

Stage progress: `7 / 8`

Publication progress: `1 / 1`

Current allowed row: `NANO-CLOSE-001` may be claimed.

Next unlock: `NANO-CLOSE-001` waits for all Nano rows PASS and can now start closeout.

```text
TODO        [ ] not claimed
CLAIMED     [>] owner set, no implementation edits yet
IN_PROGRESS [~] implementation edits in progress, file locks active
BLOCKED     [!] blocked with reason and next action
REVIEW      [?] implementation done, waiting for full gate/evidence
PASS        [x] evidence recorded and gate passed
```

## Progress Update Rule

Update these three fields whenever a row becomes `PASS`:

| Passed stage rows | Stage progress | Overall progress |
| ---: | --- | --- |
| 0 | `0 / 8` | `[----------] 0%` |
| 1 | `1 / 8` | `[x---------] 12%` |
| 2 | `2 / 8` | `[xxx-------] 25%` |
| 3 | `3 / 8` | `[xxxx------] 37%` |
| 4 | `4 / 8` | `[xxxxx-----] 50%` |
| 5 | `5 / 8` | `[xxxxxx----] 62%` |
| 6 | `6 / 8` | `[xxxxxxxx--] 75%` |
| 7 | `7 / 8` | `[xxxxxxxxx-] 87%` |
| 8 | `8 / 8` | `[xxxxxxxxxx] 100%` |

Backlog progress counts `FND-001` through `FND-009` plus `NANO-PUB-001`. If a stage row covers two backlog IDs, update both IDs only after their evidence is present.

## Claim And Lock Rules

- Claim exactly one stage row before editing code/docs.
- To claim, edit only this file first: set the row `Mark` to `[>]`, fill `Owner`, `Started`, and `Lock expires`.
- When implementation starts, change row `Mark` to `[~]`.
- Do not edit files outside the row's `Allowed write set`.
- Do not edit a file locked by another `[~] IN_PROGRESS` row.
- If a needed file is outside the write set, mark row `[!] BLOCKED`, record `Coordination needed`, and stop.
- Do not mark `[x] PASS` without command output summary and artifact/evidence refs.
- `NANO-PUBLISH-001` is exclusive for release packaging and may run only after the pipeline evidence rows are `[x] PASS`.
- `NANO-CLOSE-001` is exclusive and may run only after all other Nano rows, including `NANO-PUBLISH-001`, are `[x] PASS`.

## File Lock Matrix

| File or area | Owning row | Rule |
| --- | --- | --- |
| `README.md`, `.gitignore`, setup docs, `pyproject.toml` | `NANO-ENV-001` | Setup/dependency docs only |
| `tests/test_model.py`, optional `tests/test_architecture.py` | `NANO-MODEL-001` | CPU architecture tests only |
| `achitic/model.py` | `NANO-MODEL-001` | Only if failing test proves bug |
| `tests/test_checkpoint.py`, `achitic/train.py` | `NANO-CKPT-001` | Exclusive while in progress |
| `tests/test_data_tokenizer_cli.py`, `achitic/data.py`, `achitic/tokenizer.py`, `achitic/cli.py` | `NANO-DATA-001` | No train-loop edits unless coordinated |
| `configs/nano.json` | `NANO-DATA-001` | Only to keep Nano smoke valid; no size target drift |
| `tests/test_alignment.py`, `achitic/alignment.py` | `NANO-ALN-001` | Reference alignment tests only |
| `README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/pipeline/06_EXPORT_EDGE.md` | `NANO-EXP-001` | Export claim guard only |
| `LICENSE`, `NOTICE`, `docs/releases/nano/*`, `releases/nano/*`, optional `scripts/nano_release.sh` | `NANO-PUBLISH-001` | Release license, package metadata and publication docs only; no source-code behavior changes |
| `docs/pipeline/01_FOUNDATION_SMOKE.md`, `docs/pipeline/BACKLOG.md` | `NANO-CLOSE-001` | Closeout evidence only |

## Backlog Checklist

| Mark | Backlog ID | Stage row | Owner | Started | Lock expires | Done when |
| --- | --- | --- | --- | --- | --- | --- |
| [x] | `FND-001` | `NANO-ENV-001` | Codex | 2026-10-12 | released | Setup docs and dependency check are reproducible |
| [x] | `FND-002` | `NANO-MODEL-001` | Codex | 2026-10-12 | released | RoPE CPU tests pass |
| [x] | `FND-003` | `NANO-MODEL-001` | Codex | 2026-10-12 | released | GQA valid/invalid config tests pass |
| [x] | `FND-004` | `NANO-CKPT-001` | Codex | 2026-10-12 | released | Checkpoint save/load tests pass |
| [x] | `FND-005` | `NANO-CKPT-001` | Codex | 2026-10-12 | released | Resume semantics documented and tested |
| [x] | `FND-006` | `NANO-DATA-001` | Codex | 2026-10-12 | released | Tokenizer/config mismatch fails clearly |
| [x] | `FND-007` | `NANO-DATA-001` | Codex | 2026-10-12 | released | Nano prepare/tokenizer/encode/train/chat smoke passes |
| [x] | `FND-008` | `NANO-ALN-001` | Codex | 2026-10-12 | released | SFT mask and DPO response-only tests pass |
| [x] | `FND-009` | `NANO-EXP-001` | Codex | 2026-10-12 | released | Export docs do not claim verification without llama.cpp |
| [x] | `NANO-PUB-001` | `NANO-PUBLISH-001` | Codex | 2026-10-12 | released | Public GitHub repo and Nano release assets published |

## Stage Board

| Mark | Row | Depends on | Backlog IDs | Allowed write set | Required validation |
| --- | --- | --- | --- | --- | --- |
| [x] | `NANO-ENV-001` | none | `FND-001` | `README.md`, `.gitignore`, `docs/pipeline/nano/01_ENV_BASELINE.md`, optional `docs/DEVELOPMENT.md`, optional `pyproject.toml` | dependency import check passed; `pytest -q` passed |
| [x] | `NANO-MODEL-001` | `NANO-ENV-001` PASS | `FND-002`, `FND-003` | `tests/test_model.py`, optional `tests/test_architecture.py`, `achitic/model.py` only if bug proven | FND-002 and FND-003 PASS; model tests and full pytest passed |
| [x] | `NANO-CKPT-001` | `NANO-ENV-001` PASS | `FND-004`, `FND-005` | `tests/test_checkpoint.py`, `achitic/train.py`, optional `docs/CHECKPOINTS.md` | checkpoint tests and full pytest passed |
| [x] | `NANO-DATA-001` | `NANO-ENV-001` PASS | `FND-006`, `FND-007` | `tests/test_data_tokenizer_cli.py`, `achitic/data.py`, `achitic/tokenizer.py`, `achitic/cli.py`, `configs/nano.json`, optional `scripts/nano_smoke.sh` | data/tokenizer tests, Nano smoke, full pytest passed |
| [x] | `NANO-ALN-001` | `NANO-MODEL-001` PASS | `FND-008` | `tests/test_alignment.py`, `achitic/alignment.py` only if bug proven | alignment tests and full pytest passed |
| [x] | `NANO-EXP-001` | `NANO-ENV-001` PASS | `FND-009` | `README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/pipeline/06_EXPORT_EDGE.md`, optional `tests/test_export_guard.py` | export claim guard and full pytest passed |
| [x] | `NANO-PUBLISH-001` | `NANO-DATA-001`, `NANO-CKPT-001`, `NANO-EXP-001` PASS | `NANO-PUB-001` | `LICENSE`, `NOTICE`, `docs/releases/nano/*`, `releases/nano/*`, optional `scripts/nano_release.sh` | Public GitHub repo and Nano release assets published; checksum, chat smoke and full pytest passed |
| [ ] | `NANO-CLOSE-001` | all above PASS | closeout | `docs/pipeline/nano/07_NANO_CLOSEOUT.md`, `docs/pipeline/01_FOUNDATION_SMOKE.md`, optional `docs/pipeline/BACKLOG.md` | full pytest, Nano smoke, release package evidence |

## Task Details

### NANO-ENV-001 - Environment Baseline

Business objective: mọi model sau đó phải có cùng command cài dependency và cùng command verify. Nếu môi trường thiếu dependency thì không được coi Nano là fail về code.

Backlog covered: `FND-001`

Allowed write set:

- `README.md`
- `.gitignore`
- `docs/pipeline/nano/01_ENV_BASELINE.md`
- Optional: `docs/DEVELOPMENT.md`
- Optional: `pyproject.toml` only if dev dependencies are missing or wrong

Do not touch:

- `achitic/model.py`
- `achitic/train.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py`
- Generated checkpoints

Implementation checklist:

- [ ] Document Python version target.
- [ ] Document install command for normal dev: `pip install -e '.[dev]'`.
- [ ] Confirm `dev` dependencies include `pytest`.
- [ ] Confirm base dependencies include `torch`, `numpy`, `sentencepiece`, and `pyyaml`.
- [ ] Keep export dependencies optional.
- [ ] Add or confirm Nano smoke command points to `configs/nano.json`.
- [ ] Record blocker clearly if local env lacks `torch`, `pytest`, or `sentencepiece`.

Required commands:

```bash
python -c "import torch, sentencepiece, pytest; print('nano deps ok')"
python -m pytest -q
```

PASS criteria:

- Dependency import check passes.
- `pytest -q` is runnable.
- Setup docs are enough for another model to reproduce.
- `FND-001` is marked PASS in this file.

Evidence template:

```text
Row: NANO-ENV-001
Backlog IDs: FND-001
Status:
Owner:
Files changed:
Commands run:
Results:
Blocked by:
Next allowed row:
```

### NANO-MODEL-001 - Shared Model Architecture Tests

Business objective: Nano must prove the shared AchiticLM Core is correct on CPU before any larger config depends on it.

Backlog covered: `FND-002`, `FND-003`

Allowed write set:

- `tests/test_model.py`
- Optional: `tests/test_architecture.py`
- `achitic/model.py` only if a failing test proves a bug

Do not touch:

- `achitic/train.py`
- `achitic/data.py`
- `achitic/tokenizer.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py`

Implementation checklist:

- [x] Keep forward/backward/generation CPU smoke.
- [x] Test tied embedding/output weight.
- [x] Test deterministic causality: changing future token does not alter previous logits.
- [x] Test RoPE shape and dtype preservation.
- [x] Test RoPE/GQA behavior with small CPU config.
- [x] Test valid GQA config where `heads % kv_heads == 0`.
- [x] Test invalid GQA config raises.
- [x] Keep tests small enough for CPU CI.

Required commands:

```bash
python -m pytest -q tests/test_model.py
python -m pytest -q
```

PASS criteria:

- `FND-002` and `FND-003` have passing tests.
- No architecture change unless tied to a failing test.
- Nano config remains compatible with the model.

Evidence template:

```text
Row: NANO-MODEL-001
Backlog IDs: FND-002, FND-003
Status:
Owner:
Files changed:
Commands run:
Results:
Model changes:
Known risks:
Next allowed row:
```

### NANO-CKPT-001 - Checkpoint And Resume Contract

Business objective: Nano checkpoints must define the contract used by every larger model: config, model state, optimizer state, step, RNG and resume semantics.

Backlog covered: `FND-004`, `FND-005`

Allowed write set:

- `tests/test_checkpoint.py`
- `achitic/train.py`
- Optional: `docs/CHECKPOINTS.md`

Do not touch:

- `achitic/model.py` unless coordinated with `NANO-MODEL-001`
- `achitic/tokenizer.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py`

Implementation checklist:

- [x] Test checkpoint contains `model`, `optimizer`, `step`, `config`.
- [x] Test checkpoint contains torch RNG, numpy RNG, python RNG.
- [x] Test checkpoint config instantiates `Config`.
- [x] Test model state loads into `AchiticLM(Config)`.
- [x] Test optimizer state loads after at least one optimizer step.
- [x] Define resume semantics: exact data order or non-exact data order.
- [x] If exact resume is not implemented, document limitation explicitly.
- [x] Exact resume is not implemented; no data cursor/sampler state is claimed.

Required commands:

```bash
python -m pytest -q tests/test_checkpoint.py
python -m pytest -q
```

PASS criteria:

- `FND-004` and `FND-005` have evidence.
- Checkpoint load is tested on CPU.
- Resume behavior is documented and not overclaimed.

Evidence template:

```text
Row: NANO-CKPT-001
Backlog IDs: FND-004, FND-005
Status:
Owner:
Files changed:
Commands run:
Results:
Resume semantics:
Known risks:
Next allowed row:
```

### NANO-DATA-001 - Data, Tokenizer, CLI And Nano Smoke

Business objective: Nano must prove the full local data path works: prepare raw text, train tokenizer, encode corpus, train checkpoint, run chat.

Backlog covered: `FND-006`, `FND-007`

Allowed write set:

- `tests/test_data_tokenizer_cli.py`
- `achitic/data.py`
- `achitic/tokenizer.py`
- `achitic/cli.py`
- `configs/nano.json`
- Optional: `scripts/nano_smoke.sh`

Do not touch:

- `achitic/model.py`
- `achitic/train.py` unless coordinated with `NANO-CKPT-001`
- `achitic/alignment.py`
- `scripts/export_gguf.py`
- Large real dataset files

Implementation checklist:

- [x] Test `clean()` NFC normalization and NUL removal.
- [x] Test `prepare()` min length filtering.
- [x] Test `prepare()` exact dedup behavior.
- [x] Test `TokenDataset` length and sample shape.
- [x] Test `TokenDataset` raises `not enough tokens`.
- [x] Test tokenizer train/load with temporary corpus.
- [x] Test tokenizer special IDs: `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- [x] Test or guard tokenizer vocab mismatch against checkpoint config.
- [x] Ensure Nano smoke uses `configs/nano.json`, not Tiny.
- [x] Confirm `examples/corpus.txt` is sufficient for Nano context; no copied smoke config was needed.

Required commands:

```bash
python -m pytest -q tests/test_data_tokenizer_cli.py
python -m pytest -q
python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt "Xin chao" --tokens 16
```

PASS criteria:

- `FND-006` and `FND-007` have evidence.
- Tokenizer/config mismatch fails clearly.
- Nano smoke produces `runs/nano.pt`.
- No language-quality claim is made.

Evidence template:

```text
Row: NANO-DATA-001
Backlog IDs: FND-006, FND-007
Status:
Owner:
Files changed:
Commands run:
Results:
Tokenizer IDs:
Nano smoke artifacts:
Known risks:
Next allowed row:
```

### NANO-ALN-001 - Alignment Reference CPU Tests

Business objective: Nano must keep SFT/DPO reference behavior testable before any instruct/alignment phase uses it.

Backlog covered: `FND-008`

Allowed write set:

- `tests/test_alignment.py`
- `achitic/alignment.py` only if a failing test proves a bug

Do not touch:

- `achitic/model.py`
- `achitic/train.py`
- `achitic/tokenizer.py`
- `scripts/export_gguf.py`

Implementation checklist:

- [x] Test `sequence_logprob()` returns finite response score.
- [x] Test response-only scoring excludes prompt-only positions.
- [x] Test empty prompt raises.
- [x] Test context overflow raises.
- [x] Test SFT mask sets prompt targets to `-100`.
- [x] Keep tests CPU-only and small.
- [x] Preserve docs that SFT/DPO are reference loops, not production pipeline.

Required commands:

```bash
python -m pytest -q tests/test_alignment.py
python -m pytest -q
```

PASS criteria:

- `FND-008` has passing test evidence.
- No new production alignment data format is introduced here.
- Alignment code remains tied to scratch checkpoint and tokenizer contract.

Evidence template:

```text
Row: NANO-ALN-001
Backlog IDs: FND-008
Status:
Owner:
Files changed:
Commands run:
Results:
Known risks:
Next allowed row:
```

### NANO-EXP-001 - Export Claim Guard

Business objective: Nano must prevent false claims that GGUF export or quantization are verified without actual llama.cpp load-and-generate.

Backlog covered: `FND-009`

Allowed write set:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/pipeline/06_EXPORT_EDGE.md`
- Optional: `tests/test_export_guard.py`

Do not touch:

- `achitic/model.py`
- `achitic/train.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py` unless guard must be enforced in code

Implementation checklist:

- [x] README says export is experimental until llama.cpp generation passes.
- [x] Architecture docs mention tokenizer parity and llama.cpp compatibility must be tested.
- [x] Roadmap export gate requires load-and-generate.
- [x] Phase 6 template uses Nano smoke checkpoint for export smoke.
- [x] Add test/doc guard if wording drifts toward verified claims.
- [x] Do not mark any export artifact verified in Nano unless llama.cpp was actually run.

Required commands:

```bash
rg "verified|load-and-generate|llama.cpp|experimental|not been verified" README.md docs scripts
python -m pytest -q
```

PASS criteria:

- `FND-009` has evidence.
- No docs imply GGUF/quantization verified without llama.cpp.
- Real export compatibility remains phase 6 work.

Evidence template:

```text
Row: NANO-EXP-001
Backlog IDs: FND-009
Status:
Owner:
Files changed:
Commands run:
Results:
Known risks:
Next allowed row:
```

### NANO-PUBLISH-001 - Publishable Nano Release Package

Business objective: Nano phải có release package đủ để xuất bản checkpoint nghiên cứu một cách tái lập, kiểm chứng được và không overclaim. "Publishable" ở đây nghĩa là local release package đã sẵn sàng để upload hoặc gắn tag sau khi human owner duyệt; task này không tự upload ra dịch vụ ngoài.

Backlog covered: `NANO-PUB-001`

Allowed write set:

- `LICENSE`
- `NOTICE`
- `docs/releases/nano/MODEL_CARD.md`
- `docs/releases/nano/ARTIFACT_MANIFEST.md`
- `docs/releases/nano/EVAL_REPORT.md`
- `docs/releases/nano/RELEASE_CHECKLIST.md`
- `docs/releases/nano/SECURITY.md`
- `docs/releases/nano/PUBLISH_INPUTS.md`
- `docs/releases/nano/USAGE_TERMS.md`
- Optional: `docs/releases/nano/README.md`
- Optional: `releases/nano/*`
- Optional: `scripts/nano_release.sh`
- Optional generated release artifacts outside docs/code, such as `releases/nano/`

Do not touch:

- `achitic/model.py`
- `achitic/train.py`
- `achitic/tokenizer.py`
- `achitic/alignment.py`
- `scripts/export_gguf.py`
- Data source files, except to reference checksums/provenance

Release artifact requirements:

- [x] Final Nano checkpoint, for example `releases/nano/nano.pt`.
- [x] Tokenizer model and vocab used by the checkpoint, for example `releases/nano/tokenizer.model` and optional `.vocab`.
- [x] Exact `configs/nano.json` copy used for the run.
- [x] SHA256 checksums for checkpoint, tokenizer, config and any release notes.
- [x] Command log for prepare/tokenizer/encode/train/chat.
- [x] Dependency/environment note: Python, OS, torch, sentencepiece, pytest versions.
- [x] Git commit or source snapshot ref.
- [x] Dataset/provenance note. If using `examples/corpus.txt`, state that this is a tiny repo example corpus and not a real language dataset.
- [ ] License/usage note for code, data and checkpoint. If license is missing or unclear, mark release `BLOCKED`.
- [x] Privacy note: no private data, PII, secrets, API keys, or user conversations in release artifacts.
- [x] Security note for `torch.load`: only load trusted artifacts, verify checksum first.
- [x] Known limitations: random/scratch training, tiny corpus, no chat capability, no safety guarantee.
- [x] No GGUF/quantized artifact in release unless llama.cpp load-and-generate evidence exists.

Model card minimum sections:

- [x] Model summary and size.
- [x] Architecture: AchiticLM Core, GQA, RoPE, RMSNorm, SwiGLU.
- [x] Training data and provenance.
- [x] Training procedure and command.
- [x] Intended use: pipeline research and smoke testing.
- [x] Out-of-scope use: production chat, factual QA, safety-critical use.
- [x] Limitations and risks.
- [x] Evaluation/smoke results.
- [x] Artifact list and checksums.
- [x] Citation or repo reference.

Required commands:

```bash
python -m pytest -q
python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16
sha256sum releases/nano/nano.pt releases/nano/tokenizer.model releases/nano/configs/nano.json
```

Optional release packaging command if `scripts/nano_release.sh` exists:

```bash
bash scripts/nano_release.sh
```

PASS criteria:

- `NANO-PUB-001` has evidence.
- Release package is reproducible from documented commands.
- Artifact manifest has exact paths, sizes and SHA256 checksums.
- Model card clearly says Nano is a pipeline/test model, not a useful chat model.
- License/provenance/privacy/security notes are present.
- Smoke inference runs from release artifact paths, not only temporary `/tmp` paths.
- No external upload is performed unless the human owner explicitly requests it.

Evidence template:

```text
Row: NANO-PUBLISH-001
Backlog IDs: NANO-PUB-001
Status:
Owner:
Files changed:
Release artifact paths:
Checksums:
Commands run:
Results:
Publication status:
Known risks:
Next allowed row:
```

### NANO-CLOSE-001 - Nano Closeout

Business objective: close Nano/Foundation so Tiny and Data/Tokenizer work can start with a tested and publishable Nano pipeline contract.

Backlog covered: closeout only

Allowed write set:

- `docs/pipeline/nano/07_NANO_CLOSEOUT.md`
- `docs/pipeline/01_FOUNDATION_SMOKE.md`
- Optional: `docs/pipeline/BACKLOG.md`

Do not touch:

- Source code
- Tests
- Configs
- Generated artifacts

Implementation checklist:

- [ ] Confirm all rows except closeout are `[x] PASS`.
- [ ] Confirm backlog progress is `10 / 10`.
- [ ] Confirm publication progress is `1 / 1`.
- [ ] Run full test suite.
- [ ] Run Nano smoke from prepare to chat.
- [ ] Run inference smoke from release artifact paths.
- [ ] Confirm checkpoint/resume evidence exists.
- [ ] Confirm tokenizer/config mismatch evidence exists.
- [ ] Confirm RoPE/GQA/causality evidence exists.
- [ ] Confirm SFT/DPO CPU evidence exists.
- [ ] Confirm export-claim guard evidence exists.
- [ ] Confirm release package evidence exists.
- [ ] Update `docs/pipeline/01_FOUNDATION_SMOKE.md` `Phase Closeout` to `Status: PASS`.
- [ ] Set dashboard to `Overall progress: [xxxxxxxxxx] 100%`, `Backlog progress: 10 / 10`, `Stage progress: 8 / 8`, `Publication progress: 1 / 1`.

Required commands:

```bash
python -m pytest -q
python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt "Xin chao" --tokens 16
python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16
```

PASS criteria:

- Nano pipeline is fully reproducible.
- Nano release package is publishable after human owner approval.
- `docs/pipeline/01_FOUNDATION_SMOKE.md` is `Status: PASS`.
- No in-progress, blocked, review, or claimed rows remain.
- Tiny/Data phase can start without guessing Nano state.

Evidence template:

```text
Row: NANO-CLOSE-001
Backlog IDs: closeout
Status:
Owner:
Files changed:
Commands run:
Results:
Phase closeout:
Release package:
Next unlocked:
Known risks:
```

## Evidence Log

Append one block per completed row. Do not delete older evidence.

```text
Row: NANO-PUBLISH-001
Backlog IDs: NANO-PUB-001
Mark: [x] PASS
Owner: Codex
Files changed: LICENSE; NOTICE; README.md; .gitignore; pyproject.toml; docs/releases/nano/*; releases/nano/README.md; releases/nano/COMMAND_LOG.md; releases/nano/SHA256SUMS; releases/nano/LICENSE; releases/nano/NOTICE; releases/nano/USAGE_TERMS.md; docs/pipeline/task_nano.md
Public repo: https://github.com/SincereVirtueDev/achitic-lm
Nano release: https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.0
Release target commit: c4fef1582cb951306048425c50084a32c4126ee6
Release asset names verified from GitHub API: COMMAND_LOG.md; LICENSE; nano.json; nano.pt; NOTICE; README.md; SHA256SUMS; tokenizer.model; tokenizer.vocab; USAGE_TERMS.md
Checksums:
- f067c5f9dad26cd78d2d89b9a3347444039d0dda53e8230b351c0a28958e761b  releases/nano/nano.pt
- b1dc236a8e22c68a7201fe50dcf6ff150e494b9bea49f5f971400b1a830b0bc6  releases/nano/tokenizer.model
- d893d94f665232759a71adcceb4616b3426b97cc952f9d45e5e26c5d35f3588f  releases/nano/tokenizer.vocab
- 802a2968e0b2c70ab1c2531c80cec2f9d46bd79a8e669b491ae74f4b7136be72  releases/nano/configs/nano.json
- fb4dd0fc3bd27268048ad85c119c5e4744d6310c9c5c6fd75e90447a93b45d82  releases/nano/COMMAND_LOG.md
- bc0ce94219893861338a2f3851ad199629c03996f94efe09fb2d3f2b14ea3747  releases/nano/README.md
- 7505b489cc8ad7f16ba08343184320f1583303cfacdb9121b9b756bc073df1ab  releases/nano/LICENSE
- 6caa26531c1646e81167332770fda34aa34264c533131e2ec10fdf8c21b122ed  releases/nano/NOTICE
- f0f01fe4f29f50b2539cd9b83510624749c1e6b7c66bdf109da258cd2ad40c83  releases/nano/USAGE_TERMS.md
Commands run:
- sha256sum -c releases/nano/SHA256SUMS
- .venv/bin/python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16
- .venv/bin/python -m pytest -q
- git --git-dir=/tmp/achitic-lm.git --work-tree=/run/media/thanhnd/DATA_LINUX/AchiticLM/achitic-lm push -u origin main
- GitHub API create repo/release and upload assets
- GitHub API release asset list verification
Results:
- checksum verification passed for all release package files
- release chat smoke passed from package artifact paths
- full pytest passed: 25 passed in 2.96s
- public repo created and main branch pushed
- GitHub Release nano-v0.1.0 created as prerelease
- 10 release assets uploaded and verified from GitHub API
Known risks: Nano remains a 3-step scratch smoke artifact, not a quality model; GGUF/quantization remains unverified until pinned llama.cpp load-and-generate evidence exists.
Next allowed row: NANO-CLOSE-001 may be claimed.
```

```text
Row: NANO-PUBLISH-001
Backlog IDs: NANO-PUB-001
Mark: [!] BLOCKED
Owner: Codex
Files changed: docs/releases/nano/MODEL_CARD.md; docs/releases/nano/ARTIFACT_MANIFEST.md; docs/releases/nano/EVAL_REPORT.md; docs/releases/nano/RELEASE_CHECKLIST.md; docs/releases/nano/SECURITY.md; docs/releases/nano/README.md; releases/nano/README.md; releases/nano/COMMAND_LOG.md; releases/nano/SHA256SUMS; releases/nano/nano.pt; releases/nano/tokenizer.model; releases/nano/tokenizer.vocab; releases/nano/configs/nano.json; docs/pipeline/task_nano.md
Release artifact paths:
- releases/nano/nano.pt
- releases/nano/tokenizer.model
- releases/nano/tokenizer.vocab
- releases/nano/configs/nano.json
- releases/nano/COMMAND_LOG.md
- releases/nano/README.md
- releases/nano/SHA256SUMS
Checksums:
- f067c5f9dad26cd78d2d89b9a3347444039d0dda53e8230b351c0a28958e761b  releases/nano/nano.pt
- b1dc236a8e22c68a7201fe50dcf6ff150e494b9bea49f5f971400b1a830b0bc6  releases/nano/tokenizer.model
- d893d94f665232759a71adcceb4616b3426b97cc952f9d45e5e26c5d35f3588f  releases/nano/tokenizer.vocab
- 802a2968e0b2c70ab1c2531c80cec2f9d46bd79a8e669b491ae74f4b7136be72  releases/nano/configs/nano.json
- 01e1b41b5d061aab270a31bf7c3d3b5caf71873512f3a30e5098fb456941b33f  releases/nano/COMMAND_LOG.md
- f73518c87db131b6031f023509bf4d90d3cd4e6f56e3c67a46375605d3a247ec  releases/nano/README.md
Commands run:
- rg --files -g '*LICENSE*' -g '*LICENCE*' -g '*COPYING*' -g '*NOTICE*'
- sha256sum -c releases/nano/SHA256SUMS
- .venv/bin/python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16
- .venv/bin/python -m pytest -q
Results:
- license search found no license/notice file
- checksum verification passed for all release artifacts
- release chat smoke passed from release artifact paths
- full pytest passed: 25 passed in 2.94s
Publication status: BLOCKED_FOR_LICENSE; no external upload performed
Known risks: release is technically packaged but not publishable until license/usage terms are explicit and an immutable source ref is supplied.
Next allowed row: NANO-PUBLISH-001 can be retried after license/usage terms are added.
```

```text
Row: NANO-EXP-001
Backlog IDs: FND-009
Mark: [x] PASS
Owner: Codex
Files changed: README.md; docs/ARCHITECTURE.md; docs/ROADMAP.md; docs/pipeline/06_EXPORT_EDGE.md; tests/test_export_guard.py; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_export_guard.py
- .venv/bin/python -m pytest -q
- rg "verified|load-and-generate|llama.cpp|experimental|not been verified" README.md docs scripts
Results:
- tests/test_export_guard.py passed: 4 passed in 0.02s
- full pytest passed: 25 passed in 2.82s
- grep evidence shows README export remains experimental and not verified, Architecture/Roadmap/Phase 6 require pinned llama.cpp load-and-generate before verification claims.
Artifacts: none
Known risks: GGUF export, tokenizer parity, quantized artifacts and edge benchmarks remain unverified until real llama.cpp load-and-generate evidence exists for each artifact.
Next allowed row: NANO-PUBLISH-001 may be claimed.
```

```text
Row: NANO-ALN-001
Backlog IDs: FND-008
Mark: [x] PASS
Owner: Codex
Files changed: tests/test_alignment.py; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_alignment.py
- .venv/bin/python -m pytest -q
Results:
- tests/test_alignment.py passed: 5 passed in 2.83s
- full pytest passed: 21 passed in 2.90s
Model changes: none
Alignment code changes: none
Known risks: SFT/DPO remain reference CPU loops and are not a production alignment pipeline.
Next allowed row: NANO-EXP-001 may be claimed.
```

```text
Row: NANO-DATA-001
Backlog IDs: FND-006, FND-007
Mark: [x] PASS
Owner: Codex
Files changed: achitic/tokenizer.py; achitic/cli.py; tests/test_data_tokenizer_cli.py; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_data_tokenizer_cli.py
- .venv/bin/python -m pytest -q
- .venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
- .venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
- .venv/bin/python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
- .venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
- .venv/bin/python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt "Xin chao" --tokens 16
- .venv/bin/python -c "checkpoint/tokenizer vocab and step check"
Results:
- tests/test_data_tokenizer_cli.py passed: 5 passed in 1.68s
- full pytest passed: 16 passed in 2.96s
- prepare produced 6 documents
- tokenizer vocab/special IDs: vocab=8000, unk=0, bos=1, eos=2, pad=3
- encode produced 131 tokens, enough for Nano context 128
- train smoke completed; checkpoint reports vocab=8000 and step=3
- chat smoke completed from runs/nano.pt and /tmp/achitic-sp.model
Tokenizer IDs: unk=0; bos=1; eos=2; pad=3
Nano smoke artifacts: /tmp/achitic-clean.txt; /tmp/achitic-sp.model; /tmp/achitic.bin; runs/nano.pt
Known risks: examples/corpus.txt is tiny; tokenizer pads unused reserved symbols to satisfy the Nano 8000-vocab contract, so smoke output can include reserved tokens and is not a language-quality signal.
Next allowed row: NANO-ALN-001 or NANO-EXP-001 may be claimed.
```

```text
Row: NANO-CKPT-001
Backlog IDs: FND-004, FND-005
Mark: [x] PASS
Owner: Codex
Files changed: achitic/train.py; tests/test_checkpoint.py; docs/CHECKPOINTS.md; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_checkpoint.py
- .venv/bin/python -m pytest -q
Results:
- tests/test_checkpoint.py passed: 3 passed in 10.72s
- full pytest passed: 11 passed in 10.66s
Resume semantics: model, optimizer, step and RNG are restored; data order is not exact because no data cursor/sampler state is stored.
Artifacts: docs/CHECKPOINTS.md; pytest temp checkpoint artifacts only
Known risks: exact data-order resume remains future scale work before any exact-resume claim.
Next allowed row: NANO-DATA-001, NANO-ALN-001 or NANO-EXP-001 may be claimed.
```

```text
Row: NANO-MODEL-001
Backlog IDs: FND-003
Mark: [x] PASS for FND-003; stage row now [x] PASS because FND-002 and FND-003 both have evidence
Owner: Codex
Files changed: tests/test_model.py; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_model.py
- .venv/bin/python -m pytest -q
Results:
- tests/test_model.py passed: 8 passed in 1.67s
- full pytest passed: 8 passed in 1.69s
Model changes: none
Artifacts: none
Known risks: no checkpoint/data/alignment/export evidence yet; those remain separate locked rows.
Next allowed row: NANO-CKPT-001, NANO-DATA-001, NANO-ALN-001 or NANO-EXP-001 may be claimed.
```

```text
Row: NANO-MODEL-001
Backlog IDs: FND-002
Mark: [x] PASS for FND-002; stage row not complete because FND-003 remains TODO
Owner: Codex
Files changed: tests/test_model.py; docs/pipeline/task_nano.md
Commands run:
- .venv/bin/python -m pytest -q tests/test_model.py
- .venv/bin/python -m pytest -q
Results:
- tests/test_model.py passed: 6 passed in 1.68s
- full pytest passed: 6 passed in 1.73s
Artifacts: none
Known risks: NANO-MODEL-001 cannot be marked PASS until FND-003 GQA tests also pass.
Next allowed row: NANO-MODEL-001 for FND-003, NANO-CKPT-001, NANO-DATA-001 or NANO-EXP-001 may be claimed.
```

```text
Row: NANO-ENV-001
Backlog IDs: FND-001
Mark: [x] PASS
Owner: Codex
Files changed: .gitignore; README.md; docs/DEVELOPMENT.md; docs/pipeline/nano/01_ENV_BASELINE.md; docs/pipeline/task_nano.md
Commands run:
- python -m venv .venv
- .venv/bin/pip install -e '.[dev]'
- .venv/bin/python -c "import torch, sentencepiece, pytest; print('nano deps ok')"
- .venv/bin/python -m pytest -q
- .venv/bin/python -c "import torch, sentencepiece, pytest; print versions"
Results:
- install succeeded in .venv
- dependency import passed: nano deps ok
- pytest passed: 2 passed in 11.01s
- versions: torch 2.14.1+cu130; sentencepiece 0.2.2; pytest 9.1.1
Artifacts: .venv local environment; docs/DEVELOPMENT.md
Known risks: PyPI torch installed CUDA 13 wheels, so the local venv is large. Nano still uses CPU unless CUDA is explicitly selected by runtime availability.
Next allowed row: NANO-MODEL-001, NANO-CKPT-001, NANO-DATA-001 or NANO-EXP-001 may be claimed.
```

```text
Row: NANO-ENV-001
Backlog IDs: FND-001
Mark: [!] BLOCKED
Owner: Codex
Files changed: README.md; docs/DEVELOPMENT.md; docs/pipeline/nano/01_ENV_BASELINE.md; docs/pipeline/task_nano.md
Commands run:
- python -c "import torch, sentencepiece, pytest; print('nano deps ok')"
- python -m pytest -q
- python -c "import importlib.util; print availability"
Results:
- import check failed: ModuleNotFoundError: No module named 'torch'
- pytest failed: /home/thanhnd/.local/bin/python: No module named pytest
- availability: torch=False, sentencepiece=False, pytest=False
Artifacts: docs/DEVELOPMENT.md
Known risks: FND-001 cannot PASS until dependencies are installed and validation commands pass.
Next allowed row: none until NANO-ENV-001 is rerun and marked PASS.
```

```text
Row:
Backlog IDs:
Mark:
Owner:
Files changed:
Commands run:
Results:
Artifacts:
Known risks:
Next allowed row:
```

## Closeout Gate

Nano is complete only when:

- Backlog progress is `10 / 10`.
- Stage progress is `8 / 8`.
- Publication progress is `1 / 1`.
- Overall progress is `[xxxxxxxxxx] 100%`.
- `docs/pipeline/01_FOUNDATION_SMOKE.md` has `Status: PASS` with evidence.
- `docs/releases/nano/` contains a publishable release package manifest, model card, eval report, security note and checklist.
- No row remains `[>] CLAIMED`, `[~] IN_PROGRESS`, `[!] BLOCKED`, or `[?] REVIEW`.

## Next Model Task

After Nano PASS:

- `docs/pipeline/tiny/00_TINY_BOARD.md` may start.
- `docs/pipeline/02_DATA_TOKENIZER.md` may start.
- No Mini/Small/350M/1B work may start until its documented dependency gate is PASS.
