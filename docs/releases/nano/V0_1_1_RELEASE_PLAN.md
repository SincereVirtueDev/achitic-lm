# AchiticLM Nano v0.1.1 Release Plan

Status: PLANNED

Planned tag: `nano-v0.1.1`

Release type: patch release

## Purpose

Nano v0.1.1 is planned as a documentation and release-package patch before Tiny upgrade work starts. It should align the public Nano release package with the current repo docs, especially the ISO-aligned technical specification.

This is not a new model-quality release.

## Version Scope

`nano-v0.1.1` may reuse the Nano v0.1.0 checkpoint, tokenizer and config if their checksums remain unchanged.

Use `nano-v0.2.0` instead if any of these change:

- Nano checkpoint weights.
- Tokenizer model or vocabulary.
- `configs/nano.json`.
- Checkpoint format.
- Runtime/model behavior.

## Planned Asset Set

| Asset | Status | Note |
| --- | --- | --- |
| `COMMAND_LOG.md` | carry forward or refresh | Must include v0.1.1 validation commands |
| `INSTALL_USAGE.md` | carry forward or refresh | Source zip and release asset usage |
| `ISO_TECHNICAL_SPEC.md` | add | ISO-aligned, not ISO-certified |
| `LICENSE` | carry forward | Apache-2.0 |
| `nano.json` | carry forward | Must match checkpoint config |
| `nano.pt` | carry forward unless v0.2.0 | Must keep checksum if reused |
| `NOTICE` | carry forward | Project notice |
| `README.md` | refresh | Mention v0.1.1 patch scope |
| `RELEASE_NOTES.md` | add | Must state changed/unchanged assets |
| `SHA256SUMS` | regenerate | Must verify all uploaded assets |
| `tokenizer.model` | carry forward unless v0.2.0 | Must keep checksum if reused |
| `tokenizer.vocab` | carry forward unless v0.2.0 | Must keep checksum if reused |
| `USAGE_TERMS.md` | carry forward | Intended and unsupported use |

## Required Validation

```bash
.venv/bin/python -m pytest -q
sha256sum -c releases/nano/SHA256SUMS
```

Nano smoke train must also pass before publication:

```bash
.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-v011-clean.txt
.venv/bin/python -m achitic.cli tokenizer --input /tmp/achitic-v011-clean.txt --prefix /tmp/achitic-v011-sp --vocab 8000
.venv/bin/python -m achitic.cli encode --input /tmp/achitic-v011-clean.txt --tokenizer /tmp/achitic-v011-sp.model --out /tmp/achitic-v011.bin
.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-v011.bin --steps 3 --batch 1 --accum 1 --out runs/nano-v0.1.1-smoke.pt
.venv/bin/python -m achitic.cli chat --checkpoint runs/nano-v0.1.1-smoke.pt --tokenizer /tmp/achitic-v011-sp.model --prompt "Xin chao" --tokens 16
```

## Release Notes Draft

Changed:

- Add `ISO_TECHNICAL_SPEC.md` to the release asset plan.
- Refresh release docs to make the Nano limitations and evidence easier to audit.
- Keep source zip installation and release asset usage documented.

Unchanged:

- No pretrained weights.
- No model architecture change.
- No Nano config change.
- No tokenizer change.
- No production/chat quality claim.
- No verified GGUF or quantized artifact.

## Publication Gate

Publish only after `docs/pipeline/task_nano_vnext.md` reaches `NANO-VNEXT-CLOSE-001` with `PUBLISHED` or an explicit owner-approved publication step.

Tiny optimization work should wait until this plan is either published or explicitly deferred with a blocker.
