# task_nano_vnext.md - Nano v0.1.1 Patch Release Task

Model slot: `nano`

Current published release: `nano-v0.1.0`

Next planned release: `nano-v0.1.1`

Release type: patch documentation and packaging refresh

Baseline date: 2026-10-13

Business purpose: chốt một version Nano mới trước khi mở backlog tối ưu Tiny. Nano v0.1.1 phải làm rõ release package, bổ sung tài liệu ISO-aligned hiện đã có trong repo, kiểm lại checksum/smoke, và không thay đổi checkpoint/tokenizer/model nếu không có quyết định nâng minor version.

## Version Decision

Status: PLANNED

Default target: `nano-v0.1.1`

Use `nano-v0.1.1` only when all statements are true:

- `configs/nano.json` unchanged.
- `releases/nano/nano.pt` unchanged or intentionally reused with the same checksum.
- `releases/nano/tokenizer.model` and `releases/nano/tokenizer.vocab` unchanged or intentionally reused with the same checksum.
- AchiticLM Core behavior unchanged.
- The release only adds or corrects docs, checksums, release notes, usage instructions, manifests or governance/spec files.

Escalate to `nano-v0.2.0` if any statement below becomes true:

- Nano checkpoint is retrained.
- Tokenizer artifact changes.
- Nano config changes.
- Checkpoint format changes.
- Any runtime behavior changes beyond documentation/packaging.

## Readiness Verdict

Current status: PUBLISHED

Kết luận:

- Nano v0.1.0 is published and usable as the baseline.
- Repo docs now include `docs/releases/nano/ISO_TECHNICAL_SPEC.md`, but the public `nano-v0.1.0` release assets do not include this file.
- `nano-v0.1.1` is published as the Nano patch release before Tiny optimization.
- Tiny upgrade work is unblocked for planning/optimization after this closeout. Real Tiny training still waits for Data/Tokenizer PASS.

## Baseline Evidence

| Area | Current evidence | Result |
| --- | --- | --- |
| Published Nano release | `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.0` | PASS |
| Release status | GitHub API reports `prerelease: true`, tag `nano-v0.1.0`, target commit `e32a726b3832080f30556af1729581b5e7288dac` | PASS |
| Existing release assets | `COMMAND_LOG.md`, `INSTALL_USAGE.md`, `LICENSE`, `nano.json`, `nano.pt`, `NOTICE`, `README.md`, `SHA256SUMS`, `tokenizer.model`, `tokenizer.vocab`, `USAGE_TERMS.md` | PASS |
| Missing desired asset | `ISO_TECHNICAL_SPEC.md` was absent from `nano-v0.1.0` assets and is included in `nano-v0.1.1` | PASS |
| Nano pipeline | `docs/pipeline/task_nano.md` and `docs/pipeline/nano/07_NANO_CLOSEOUT.md` show Nano PASS | PASS |

## Progress Dashboard

Overall progress: `[xxxxxxxxxx] 100%`

Backlog progress: `10 / 10`

Current allowed rows:

- none; Nano vNext is closed.

Rows remaining before closeout:

- none.

```text
TODO        [ ] not claimed
CLAIMED     [>] owner set, no implementation edits yet
IN_PROGRESS [~] implementation edits in progress, file locks active
BLOCKED     [!] blocked with reason and next action
REVIEW      [?] implementation done, waiting for full gate/evidence
PASS        [x] evidence recorded and gate passed
```

## Progress Update Rule

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
- To claim, edit only this file first: set the row `Mark` to `[>]`, fill `Owner`, `Started`, and `Lock expires`.
- When implementation starts, change row `Mark` to `[~]`.
- Do not edit files outside the row's allowed write set.
- Do not edit a file locked by another `[~] IN_PROGRESS` row.
- Do not touch `achitic/model.py`, `achitic/train.py`, `configs/nano.json`, tokenizer artifacts or `nano.pt` for a patch release unless the row is changed to BLOCKED and a minor-version decision is recorded.
- Do not publish any release asset containing `github_token.txt`, `.venv`, `runs/`, private data, credentials, or non-audited datasets.
- Do not mark `[x] PASS` without command output summary and artifact/evidence refs.

## File Lock Matrix

| File or area | Owning row | Rule |
| --- | --- | --- |
| `docs/pipeline/task_nano_vnext.md`, `docs/pipeline/BACKLOG.md` | `NANO-VNEXT-SCOPE-001`, `NANO-VNEXT-CLOSE-001` | Release planning and closeout only |
| `docs/releases/nano/README.md`, `docs/releases/nano/V0_1_1_RELEASE_PLAN.md`, `docs/releases/nano/ISO_TECHNICAL_SPEC.md` | `NANO-VNEXT-DOC-001` | Release docs alignment only |
| `releases/nano/README.md`, `releases/nano/COMMAND_LOG.md`, `releases/nano/SHA256SUMS`, `releases/nano/INSTALL_USAGE.md`, optional copied docs | `NANO-VNEXT-PKG-001` | Package manifest/checksum refresh only |
| `docs/releases/nano/ARTIFACT_MANIFEST.md`, `docs/releases/nano/EVAL_REPORT.md`, `docs/releases/nano/RELEASE_CHECKLIST.md`, `docs/releases/nano/SECURITY.md` | `NANO-VNEXT-VERIFY-001` | Evidence refresh only |
| Git tag/release notes and GitHub release assets | `NANO-VNEXT-PUBLISH-001` | Publish only after verification PASS |
| `docs/pipeline/task_upgrade_tiny.md`, `docs/pipeline/tiny/*.md`, `docs/pipeline/03_PRETRAIN_SCALE.md` | `NANO-VNEXT-CLOSE-001` | Unblock Tiny only after v0.1.1 release decision |

## Backlog Checklist

| Mark | Backlog ID | Owner | Started | Lock expires | Done when |
| --- | --- | --- | --- | --- | --- |
| [x] | `NANO-VNEXT-BASE-001` | Codex | 2026-10-13 | released | Current release state and desired patch scope recorded |
| [x] | `NANO-VNEXT-SCOPE-001` | Codex | 2026-10-13 | released | Version number, release type and no-change contract confirmed |
| [x] | `NANO-VNEXT-DOC-001` | Codex | 2026-10-13 | released | ISO spec and release docs are aligned for v0.1.1 |
| [x] | `NANO-VNEXT-PKG-001` | Codex | 2026-10-13 | released | Local release package includes v0.1.1 docs/assets and checksums |
| [x] | `NANO-VNEXT-SMOKE-001` | Codex | 2026-10-13 | released | Pytest, Nano smoke train and release smoke pass |
| [x] | `NANO-VNEXT-SEC-001` | Codex | 2026-10-13 | released | Secret/private-data scan and checkpoint safety note pass |
| [x] | `NANO-VNEXT-RELNOTE-001` | Codex | 2026-10-13 | released | Release notes and asset delta are complete |
| [x] | `NANO-VNEXT-PUBLISH-001` | Codex | 2026-10-13 | released | GitHub tag/release `nano-v0.1.1` is created or explicitly deferred |
| [x] | `NANO-VNEXT-CLOSE-001` | Codex | 2026-10-13 | released | Nano vNext status is closed and Tiny upgrade is unblocked or blocked with reason |
| [x] | `NANO-VNEXT-AUDIT-001` | Codex | 2026-10-13 | released | Final audit confirms no model-quality overclaim |

## Stage Board

| Mark | Row | Depends on | Allowed write set | Required validation |
| --- | --- | --- | --- | --- |
| [x] | `NANO-VNEXT-BASE-001` | Nano v0.1.0 published | `docs/pipeline/task_nano_vnext.md` | Release API state and asset gap recorded |
| [x] | `NANO-VNEXT-SCOPE-001` | `NANO-VNEXT-BASE-001` PASS | `docs/pipeline/task_nano_vnext.md`, `docs/pipeline/BACKLOG.md` | Version decision is documented |
| [x] | `NANO-VNEXT-DOC-001` | `NANO-VNEXT-SCOPE-001` PASS | `docs/releases/nano/*` docs only | ISO/readme/release plan consistent |
| [x] | `NANO-VNEXT-PKG-001` | `NANO-VNEXT-DOC-001` PASS | `releases/nano/*` docs/checksums only | SHA256SUMS regenerated and verifies |
| [x] | `NANO-VNEXT-SMOKE-001` | `NANO-VNEXT-PKG-001` PASS | evidence docs only | `pytest -q`, Nano smoke train and release smoke pass |
| [x] | `NANO-VNEXT-SEC-001` | `NANO-VNEXT-PKG-001` PASS | security/checklist docs only | no secrets/private data in assets |
| [x] | `NANO-VNEXT-RELNOTE-001` | smoke and security PASS | release notes docs/assets | release notes describe patch scope |
| [x] | `NANO-VNEXT-PUBLISH-001` | all previous rows except close/audit PASS | GitHub tag/release assets | release exists or is explicitly deferred |
| [x] | `NANO-VNEXT-AUDIT-001` | local candidate ready | audit evidence docs only | no quality/export overclaim |
| [x] | `NANO-VNEXT-CLOSE-001` | all previous rows PASS or publish deferred with reason | closeout docs, Tiny blocker notes | Tiny upgrade dependency updated |

## Task Details

### NANO-VNEXT-SCOPE-001 - Version Scope

Business objective: giữ Nano v0.1.1 là patch release sạch, không vô tình biến thành model release mới.

Checklist:

- [x] Confirm chosen tag: `nano-v0.1.1`.
- [x] Confirm no model architecture change.
- [x] Confirm no Nano config change.
- [x] Confirm no tokenizer change.
- [x] Confirm no checkpoint retrain.
- [x] If any artifact changes beyond docs/package metadata, reclassify as `nano-v0.2.0`.

PASS criteria:

- Version type and no-change contract are recorded.

Evidence:

- Planned tag: `nano-v0.1.1`.
- Scope: documentation/package patch only.
- Escalation rule to `nano-v0.2.0` documented if checkpoint, tokenizer, config, format or runtime behavior changes.

### NANO-VNEXT-DOC-001 - Release Docs Alignment

Business objective: local release docs and public release asset plan must match.

Checklist:

- [x] Add a v0.1.1 release plan file under `docs/releases/nano/`.
- [x] Include `ISO_TECHNICAL_SPEC.md` in the planned release asset list.
- [x] Keep the ISO disclaimer: ISO-aligned, not ISO-certified.
- [x] Update `docs/releases/nano/README.md` with the planned v0.1.1 doc.
- [x] Record that v0.1.0 remains the last actually published release until publish task PASS.

PASS criteria:

- Another model can prepare the v0.1.1 assets without guessing scope.

Evidence:

- Added `docs/releases/nano/V0_1_1_RELEASE_PLAN.md`.
- Updated `docs/releases/nano/README.md`.
- Planned asset set includes `ISO_TECHNICAL_SPEC.md` and `RELEASE_NOTES.md`.

### NANO-VNEXT-PKG-001 - Local Package Refresh

Business objective: prepare the local release package that would be uploaded as `nano-v0.1.1`.

Expected v0.1.1 assets:

- `COMMAND_LOG.md`
- `INSTALL_USAGE.md`
- `ISO_TECHNICAL_SPEC.md`
- `LICENSE`
- `nano.json`
- `nano.pt`
- `NOTICE`
- `README.md`
- `RELEASE_NOTES.md`
- `SHA256SUMS`
- `tokenizer.model`
- `tokenizer.vocab`
- `USAGE_TERMS.md`

Checklist:

- [x] Copy or generate `ISO_TECHNICAL_SPEC.md` into the release package.
- [x] Add `RELEASE_NOTES.md` for v0.1.1.
- [x] Regenerate `SHA256SUMS`.
- [x] Verify `nano.pt`, tokenizer and config checksums against the v0.1.0 baseline if reused.
- [x] Do not add generated run scratch files.

Required validation:

```bash
sha256sum -c releases/nano/SHA256SUMS
```

Evidence:

- Added `releases/nano/ISO_TECHNICAL_SPEC.md`.
- Added `releases/nano/RELEASE_NOTES.md`.
- Updated `releases/nano/README.md`.
- Regenerated `releases/nano/SHA256SUMS`.
- `sha256sum -c releases/nano/SHA256SUMS` passed for 12 assets.

### NANO-VNEXT-SMOKE-001 - Test And Smoke Verification

Business objective: the new Nano patch release must still prove the same pipeline.

Required commands:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-v011-clean.txt
.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-v011-clean.txt --prefix /tmp/achitic-v011-sp --vocab 8000
.venv/bin/python -m achitic.cli encode --input /tmp/achitic-v011-clean.txt --tokenizer /tmp/achitic-v011-sp.model --out /tmp/achitic-v011.bin
.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-v011.bin --steps 3 --batch 1 --accum 1 --out runs/nano-v0.1.1-smoke.pt
.venv/bin/python -m achitic.cli chat --checkpoint runs/nano-v0.1.1-smoke.pt --tokenizer /tmp/achitic-v011-sp.model --prompt "Xin chao" --tokens 16
```

PASS criteria:

- Tests pass.
- Smoke train produces a checkpoint at step 3.
- Chat smoke runs without tokenizer/config mismatch.

Evidence:

- `.venv/bin/python -m pytest -q`: `25 passed`.
- Prepare smoke: `documents: 6`.
- Encode smoke: `tokens: 131`.
- Train smoke: `runs/nano-v0.1.1-smoke.pt`.
- Checkpoint smoke: `step 3`, `vocab 8000`, `checkpoint_format 1`.
- Chat smoke ran with the v0.1.1 smoke checkpoint and tokenizer.

### NANO-VNEXT-SEC-001 - Secret And Privacy Audit

Business objective: no private data, token or credential goes into the patch release.

Checklist:

- [x] Confirm `github_token.txt` is ignored and not in release assets.
- [x] Confirm `.venv`, `.pytest_cache`, `runs/` scratch files and local temp artifacts are not in release assets.
- [x] Confirm release data is still only the self-authored example corpus.
- [x] Confirm checkpoint security note still warns about trusted `.pt` loading.

Suggested checks:

```bash
rg -n "ghp_|github_pat_|BEGIN .*PRIVATE|api[_-]?key|token" releases/nano docs/releases/nano
```

Evidence:

- Secret scan used the stricter pattern `ghp_|github_pat_|BEGIN .*PRIVATE|api[_-]?key`.
- Result: no matches.

### NANO-VNEXT-RELNOTE-001 - Release Notes

Business objective: public users must understand v0.1.1 is a package/docs patch, not a new model-quality claim.

Checklist:

- [x] Create release notes with changed/unchanged sections.
- [x] Mention added `ISO_TECHNICAL_SPEC.md`.
- [x] State checkpoint/config/tokenizer are unchanged if reused.
- [x] State no GGUF/quantization verification is claimed.
- [x] State no production/chat quality claim is made.

Evidence:

- Added `releases/nano/RELEASE_NOTES.md`.

### NANO-VNEXT-PUBLISH-001 - GitHub Release

Business objective: publish `nano-v0.1.1` or explicitly defer publication with a reason.

Checklist:

- [x] Commit release docs/package refresh.
- [x] Create tag `nano-v0.1.1` from the committed source state.
- [x] Create GitHub release as prerelease unless owner explicitly asks for stable.
- [x] Upload all expected assets.
- [x] Verify asset list through GitHub API.
- [x] Verify release body includes limitations and checksum instructions.

Evidence:

- Commit: `1eb3c96174a28852a80f701f9ca7995eef55a59b`.
- Release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.1`.
- Asset count: `13`.
- Asset names: `COMMAND_LOG.md`, `INSTALL_USAGE.md`, `ISO_TECHNICAL_SPEC.md`, `LICENSE`, `NOTICE`, `README.md`, `RELEASE_NOTES.md`, `SHA256SUMS`, `USAGE_TERMS.md`, `nano.json`, `nano.pt`, `tokenizer.model`, `tokenizer.vocab`.

Blockers:

- Missing Git metadata.
- Missing/invalid GitHub token.
- Failed tests or checksum verification.

### NANO-VNEXT-AUDIT-001 - Final Claim Audit

Business objective: ensure the new release does not overclaim.

Checklist:

- [x] No text says Nano is chat-capable.
- [x] No text says Nano has verified factual quality.
- [x] No text says GGUF/quantization is verified without llama.cpp generation.
- [x] No text says ISO certified/compliant; only ISO-aligned documentation.
- [x] No pretrained model or third-party private data is implied.

Evidence:

- Claim-audit search found only limitation/disclaimer lines and checklist text for chat, factual quality, ISO certification, GGUF/quantization and pretrained weights.

### NANO-VNEXT-CLOSE-001 - Closeout And Tiny Unlock

Business objective: close Nano vNext before reopening Tiny upgrade work.

Checklist:

- [x] Record final release status: `PUBLISHED`, `DEFERRED`, or `NO_GO`.
- [x] If published, record GitHub release URL and tag commit.
- [x] If deferred, record exact blocker and next action.
- [x] Update `docs/pipeline/task_upgrade_tiny.md`: Tiny may start only after vNext is closed.
- [x] Update `docs/pipeline/BACKLOG.md`.

PASS criteria:

- Nano vNext is closed with evidence.
- Tiny optimization no longer has an unresolved Nano release drift blocker.

Evidence:

- Final status: `PUBLISHED`.
- GitHub release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.1`.
- Tiny optimization is unblocked for planning/config/data/memory tasks; Tiny train/release still requires Data/Tokenizer PASS.

## Handoff Template

```text
Task ID:
Mark before:
Mark after:
Owner:
Files changed:
Commands run:
Results:
Assets changed:
Known risks:
Next allowed task:
```
