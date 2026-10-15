# AchiticLM Nano Publish Inputs

Status: PUBLISHED

This file lists the human-owned decisions required before `NANO-PUBLISH-001`
can move from `BLOCKED` to `PASS`.

## Required Owner Inputs

- [x] GitHub publication credential availability was confirmed by the owner outside release artifacts.
- [x] GitHub owner or organization: `SincereVirtueDev`
- [x] New GitHub repository name: `achitic-lm`
- [x] Repository visibility: `public`
- [x] Code license: Apache-2.0
- [x] Checkpoint/model weights license: Apache-2.0
- [x] Tokenizer license: Apache-2.0 for self-developed tokenizer code, vocabulary and original/compatible training data
- [x] Example corpus license/source confirmation: self-authored synthetic/example corpus created for AchiticLM; public release allowed
- [x] Release tag name, for example `nano-v0.1.0`: `nano-v0.1.0`
- [x] Release title: `AchiticLM Nano v0.1.0`
- [x] Intended usage note: research, education, development, pipeline smoke testing, experimentation and early-stage Nano evaluation; not validated for production
- [x] Prohibited usage note: safety-critical applications, unsupported factual claims, high-stakes decisions or production deployment without appropriate validation
- [x] Whether to include `releases/nano/nano.pt` in Git history, Git LFS, or GitHub Release asset: GitHub Release asset
- [x] Confirm that no credential, private dataset or private file should be published: yes

## Recommended Defaults

These are only defaults for review. Do not apply them until the owner confirms.

- Repository visibility: `public`
- Release tag: `nano-v0.1.0`
- Release title: `AchiticLM Nano v0.1.0`
- Artifact strategy: GitHub Release assets for Nano package artifacts; source/docs in Git
- Code license: Apache-2.0
- Checkpoint license: Apache-2.0

## Credential Handling

Do not commit local publication credentials.

Publication should run with an authenticated GitHub CLI session or another approved local credential flow.
Never paste credentials into release notes, command logs, issues, commits or docs.

## Publish Gate

`NANO-PUBLISH-001` may pass only after:

- a repository license file exists,
- model/checkpoint usage terms are explicit,
- tokenizer usage terms are explicit,
- example corpus provenance and license are explicit,
- source is committed to an immutable Git commit,
- release artifact checksums are verified after packaging,
- release smoke inference has been run from the packaged artifact paths.
