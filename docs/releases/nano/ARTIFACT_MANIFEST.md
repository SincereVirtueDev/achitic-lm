# AchiticLM Nano Artifact Manifest

Status: PUBLISHED

## Source Reference

- Local source snapshot: `/run/media/thanhnd/DATA_LINUX/AchiticLM/achitic-lm`
- Date: 2026-10-12
- GitHub repo: `https://github.com/SincereVirtueDev/achitic-lm`
- GitHub release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.0`
- Release target commit: `c4fef1582cb951306048425c50084a32c4126ee6`

## Artifacts

| Path | Size bytes | SHA256 |
| --- | ---: | --- |
| `releases/nano/nano.pt` | `60043760` | `f067c5f9dad26cd78d2d89b9a3347444039d0dda53e8230b351c0a28958e761b` |
| `releases/nano/tokenizer.model` | `596172` | `b1dc236a8e22c68a7201fe50dcf6ff150e494b9bea49f5f971400b1a830b0bc6` |
| `releases/nano/tokenizer.vocab` | `151055` | `d893d94f665232759a71adcceb4616b3426b97cc952f9d45e5e26c5d35f3588f` |
| `releases/nano/configs/nano.json` | `121` | `802a2968e0b2c70ab1c2531c80cec2f9d46bd79a8e669b491ae74f4b7136be72` |
| `releases/nano/COMMAND_LOG.md` | `2011` | `01e1b41b5d061aab270a31bf7c3d3b5caf71873512f3a30e5098fb456941b33f` |
| `releases/nano/README.md` | `756` | `f73518c87db131b6031f023509bf4d90d3cd4e6f56e3c67a46375605d3a247ec` |

## Environment

- Python: `3.14.4`
- Platform: `Linux-7.0.0-38-generic-x86_64-with-glibc2.43`
- torch: `2.14.1+cu130`
- sentencepiece: `0.2.2`
- pytest: `9.1.1`

## Dataset and Provenance

Input data: `examples/corpus.txt`.

This corpus is a tiny repository example corpus. It is used only for smoke testing and is not a curated pretraining dataset.

## License and Usage

- Code license: Apache-2.0
- Checkpoint/model weights license: Apache-2.0
- Tokenizer code and artifacts license: Apache-2.0
- Example corpus: self-authored synthetic/example corpus created for AchiticLM and allowed for public release

See `LICENSE`, `NOTICE` and `docs/releases/nano/USAGE_TERMS.md`.

## Privacy

The release artifacts were generated from `examples/corpus.txt` and local code/config files. No private data source, API token, credential, PII dataset or user conversation was intentionally included.

## Export and Quantization

No GGUF or quantized artifact is included. Do not claim export or quantization verified until llama.cpp load-and-generate evidence exists for each artifact.
