# AchiticLM Nano Artifact Manifest

Status: PUBLISHED

Published release: `nano-v0.1.0`

Latest patch release: `nano-v0.1.1`

Nano v0.1.1 is a published patch release. It adds release docs and keeps the Nano checkpoint, tokenizer and config unchanged.

## Source Reference

- Source snapshot: `<local checkout>`
- Date: 2026-10-12
- GitHub repo: `https://github.com/SincereVirtueDev/achitic-lm`
- GitHub release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.1`
- Release tag: `nano-v0.1.1`
- Source zip includes root `INSTALL_USAGE.md` for installation, configuration and usage.

## Artifacts

| Path | Size bytes | SHA256 |
| --- | ---: | --- |
| `releases/nano/nano.pt` | `60043760` | `f067c5f9dad26cd78d2d89b9a3347444039d0dda53e8230b351c0a28958e761b` |
| `releases/nano/tokenizer.model` | `596172` | `b1dc236a8e22c68a7201fe50dcf6ff150e494b9bea49f5f971400b1a830b0bc6` |
| `releases/nano/tokenizer.vocab` | `151055` | `d893d94f665232759a71adcceb4616b3426b97cc952f9d45e5e26c5d35f3588f` |
| `releases/nano/configs/nano.json` | `121` | `802a2968e0b2c70ab1c2531c80cec2f9d46bd79a8e669b491ae74f4b7136be72` |
| `releases/nano/COMMAND_LOG.md` | `2112` | `7a7f521ea2bee4f775f83636e80a75cbbf553da16740ace293e589e2c28f1322` |
| `releases/nano/README.md` | `1317` | `e4c964b825a52fecdd78b495b3c5f4d4bd2bdafb991e892cc803b9e2594d1665` |
| `releases/nano/INSTALL_USAGE.md` | `3985` | `cfdfb1e7fb8872e760e565949abfac82f056b2203254c9ef4fa68ea5cbf7a875` |
| `releases/nano/LICENSE` | `10254` | `7505b489cc8ad7f16ba08343184320f1583303cfacdb9121b9b756bc073df1ab` |
| `releases/nano/NOTICE` | `355` | `6caa26531c1646e81167332770fda34aa34264c533131e2ec10fdf8c21b122ed` |
| `releases/nano/USAGE_TERMS.md` | `1854` | `f0f01fe4f29f50b2539cd9b83510624749c1e6b7c66bdf109da258cd2ad40c83` |

Checksum manifest: `releases/nano/SHA256SUMS`, `1129` bytes.

## Checkpoint Content And Size Split

Measured from `releases/nano/nano.pt`:

| Component | Tensor count | Logical tensor bytes | Unique storage bytes | Notes |
| --- | ---: | ---: | ---: | --- |
| Model state dict | `39` | `28,189,696` | `19,997,696` | `head.weight` and `embed.weight` are tied and share storage |
| Optimizer state | `114` | `39,995,544` | `39,995,544` | AdamW resume state |
| Torch RNG state | `1` | `5,056` | `5,056` | CPU RNG state |
| Serialization metadata and non-tensor state | n/a | n/a | `45,464` | Config, Python/NumPy RNG metadata and PyTorch container overhead |
| Full checkpoint file | n/a | n/a | `60,043,760` | Full training checkpoint, not weights-only |

Trainable unique model parameters: `4,999,424`.

Checkpoint config:

```json
{
  "vocab_size": 8000,
  "dim": 256,
  "layers": 4,
  "heads": 4,
  "kv_heads": 2,
  "ffn_dim": 704,
  "context": 128,
  "rope_theta": 10000.0
}
```

## Nano v0.1.1 Patch Release Addendum

The local `releases/nano/` package has been refreshed as the v0.1.1 patch release package.

Unchanged core artifacts:

| Path | SHA256 |
| --- | --- |
| `releases/nano/nano.pt` | `f067c5f9dad26cd78d2d89b9a3347444039d0dda53e8230b351c0a28958e761b` |
| `releases/nano/tokenizer.model` | `b1dc236a8e22c68a7201fe50dcf6ff150e494b9bea49f5f971400b1a830b0bc6` |
| `releases/nano/tokenizer.vocab` | `d893d94f665232759a71adcceb4616b3426b97cc952f9d45e5e26c5d35f3588f` |
| `releases/nano/configs/nano.json` | `802a2968e0b2c70ab1c2531c80cec2f9d46bd79a8e669b491ae74f4b7136be72` |

New or refreshed package docs:

| Path | SHA256 |
| --- | --- |
| `releases/nano/README.md` | `e4c964b825a52fecdd78b495b3c5f4d4bd2bdafb991e892cc803b9e2594d1665` |
| `releases/nano/COMMAND_LOG.md` | `7a7f521ea2bee4f775f83636e80a75cbbf553da16740ace293e589e2c28f1322` |
| `releases/nano/INSTALL_USAGE.md` | `cfdfb1e7fb8872e760e565949abfac82f056b2203254c9ef4fa68ea5cbf7a875` |
| `releases/nano/ISO_TECHNICAL_SPEC.md` | `d6858f74ef977dcbb1d6d314e364036cba778b142fe1f1b3cad332b260d3af06` |
| `releases/nano/RELEASE_NOTES.md` | `7945875cbd47315f1bb1180584af38133034acddb915d91e16b2c430ad0a19b5` |
| `releases/nano/SHA256SUMS` | `36903457d8a1d62fdb5125e75ad5200aeabb044c8d80268912614acdef524fea` |

Validation:

```text
sha256sum -c releases/nano/SHA256SUMS
Result: 12 assets OK
```

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
