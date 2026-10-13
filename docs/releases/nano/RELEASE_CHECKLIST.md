# AchiticLM Nano Release Checklist

Status: PUBLISHED

- [x] Final Nano checkpoint copied to `releases/nano/nano.pt`.
- [x] Tokenizer model copied to `releases/nano/tokenizer.model`.
- [x] Tokenizer vocab copied to `releases/nano/tokenizer.vocab`.
- [x] Exact config copied to `releases/nano/configs/nano.json`.
- [x] SHA256 checksums recorded for checkpoint, tokenizer and config.
- [x] Command log recorded in `releases/nano/COMMAND_LOG.md`.
- [x] Environment note recorded.
- [x] Dataset/provenance note recorded.
- [x] Privacy note recorded.
- [x] Security note recorded.
- [x] Known limitations recorded.
- [x] No GGUF/quantized artifact included.
- [x] License and usage terms are explicit.
- [x] Git commit or immutable source snapshot is available.
- [x] Owner publish input checklist recorded in `docs/releases/nano/PUBLISH_INPUTS.md`.
- [x] Usage terms recorded in `docs/releases/nano/USAGE_TERMS.md`.
- [x] Release inference smoke has been rerun from `releases/nano/`.
- [x] Public GitHub repository exists: `https://github.com/SincereVirtueDev/achitic-lm`.
- [x] `main` branch pushed.
- [x] GitHub Release `nano-v0.1.0` created.
- [x] Nano package artifacts uploaded as GitHub Release assets.
- [x] `INSTALL_USAGE.md` added to source zip and release assets.
- [x] Release asset checksum manifest updated after adding `INSTALL_USAGE.md`.

## Publication

Published repo: `https://github.com/SincereVirtueDev/achitic-lm`

Published Nano release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.0`

Owner decisions are recorded in `docs/releases/nano/PUBLISH_INPUTS.md`.

## Nano v0.1.1 Patch Release

Status: PUBLISHED

- [x] Planned tag recorded as `nano-v0.1.1`.
- [x] Patch scope recorded: docs/package refresh only.
- [x] `ISO_TECHNICAL_SPEC.md` copied into `releases/nano/`.
- [x] `RELEASE_NOTES.md` added to `releases/nano/`.
- [x] `releases/nano/README.md` updated for v0.1.1.
- [x] `releases/nano/SHA256SUMS` regenerated for 12 assets.
- [x] `sha256sum -c releases/nano/SHA256SUMS` passed.
- [x] `pytest -q` passed.
- [x] Nano v0.1.1 smoke train and chat passed.
- [x] Secret pattern scan found no GitHub token, API key or private key in release docs/assets.
- [x] Git commit for v0.1.1 source state exists: `1eb3c96174a28852a80f701f9ca7995eef55a59b`.
- [x] GitHub Release `nano-v0.1.1` created.
- [x] v0.1.1 assets uploaded and verified through GitHub API.

Published Nano v0.1.1 release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.1`
