# AchiticLM Nano v0.2.0 Artifact Manifest

Status: RELEASE_ARTIFACT

Package directory: `releases/nano-v0.2.0/`

## Core Artifacts

| Artifact | Size | SHA256 |
| --- | ---: | --- |
| `nano.pt` | `60,055,064` | `91159067702c945c08fbd245f82ff1834a31e8aff77cc27920f11572315270b9` |
| `nano-fp16.safetensors` | `10,002,496` | `b945ecc7a608a85d5dda4b15cd7c7f7ce0dfc4f3b9508fda524c9b0ff6f88afd` |
| `tokenizer.model` | `363,595` | `26c8b92336b85b26f8bdc3020496ce7c328e42c61ac322a03c85c9955a1ee50d` |
| `tokenizer.vocab` | `104,686` | `a4c31a288dcf595662b5b2954990d59362e69f4299822e23d17c5462431e1905` |
| `nano.json` | `121` | `802a2968e0b2c70ab1c2531c80cec2f9d46bd79a8e669b491ae74f4b7136be72` |

The full checkpoint records stage `sft`, step `800`, checkpoint format `1` and the
same `8000` vocabulary/config contract as the packaged tokenizer. The weights-only
artifact contains `38` FP16 tensors.

## Included Documentation

README, model card, evaluation report, controlled meaning report, training run
manifest, install guide, security note, usage terms, ISO-aligned technical spec,
release notes, license, notice and checksums.

## Excluded

- Raw or cleaned training/evaluation text.
- Credentials, tokens, private datasets and local machine paths.
- GGUF and quantized artifacts.

All package-file checksums are listed in `SHA256SUMS`.
