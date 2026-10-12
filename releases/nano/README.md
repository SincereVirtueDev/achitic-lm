# AchiticLM Nano Release Package

Status: READY_FOR_GITHUB_PUBLICATION

This directory contains local Nano release artifacts for pipeline smoke testing:

- `nano.pt`: scratch checkpoint trained for 3 smoke steps.
- `tokenizer.model`: SentencePiece tokenizer used by the checkpoint.
- `tokenizer.vocab`: tokenizer vocabulary.
- `configs/nano.json`: exact Nano config copy.
- `COMMAND_LOG.md`: reproducibility command log.
- `SHA256SUMS`: checksums for release artifacts.
- `LICENSE`: Apache-2.0 license text.
- `NOTICE`: project notice.
- `USAGE_TERMS.md`: Nano usage terms.

Nano is not a useful chat model. It is a CPU pipeline artifact for environment, model, checkpoint, tokenizer, alignment and export-claim guard verification.

The release package is licensed under Apache-2.0 and is ready to be published as GitHub Release assets for tag `nano-v0.1.0`.
