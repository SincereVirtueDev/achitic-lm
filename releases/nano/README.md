# AchiticLM Nano Release Package

Status: LOCAL_RELEASE_CANDIDATE

This directory contains local Nano release artifacts for pipeline smoke testing.
It is prepared as a `nano-v0.1.1` patch release candidate before Tiny upgrade work.

- `nano.pt`: scratch checkpoint trained for 3 smoke steps.
- `tokenizer.model`: SentencePiece tokenizer used by the checkpoint.
- `tokenizer.vocab`: tokenizer vocabulary.
- `configs/nano.json`: exact Nano config copy.
- `COMMAND_LOG.md`: reproducibility command log.
- `INSTALL_USAGE.md`: install, configuration and usage guide for source zip and release assets.
- `ISO_TECHNICAL_SPEC.md`: ISO-aligned technical specification and risk/evidence matrix. This is not ISO certification.
- `RELEASE_NOTES.md`: v0.1.1 patch release notes.
- `SHA256SUMS`: checksums for release artifacts.
- `LICENSE`: Apache-2.0 license text.
- `NOTICE`: project notice.
- `USAGE_TERMS.md`: Nano usage terms.

Nano is not a useful chat model. It is a CPU pipeline artifact for environment, model, checkpoint, tokenizer, alignment and export-claim guard verification.

The release package is licensed under Apache-2.0. The planned patch tag is `nano-v0.1.1`.

The v0.1.1 patch scope does not change `nano.pt`, `tokenizer.model`, `tokenizer.vocab` or `configs/nano.json` unless the release task is reclassified as `nano-v0.2.0`.
