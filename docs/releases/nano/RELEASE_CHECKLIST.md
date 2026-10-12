# AchiticLM Nano Release Checklist

Status: READY_FOR_GITHUB_PUBLICATION

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

## Remaining Publication Step

Create or reuse the public GitHub repository `SincereVirtueDev/achitic-lm`, push
the `main` branch, then publish Nano package artifacts as GitHub Release assets
for tag `nano-v0.1.0`.

Owner decisions are recorded in `docs/releases/nano/PUBLISH_INPUTS.md`.
