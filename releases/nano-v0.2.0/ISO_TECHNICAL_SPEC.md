# AchiticLM Nano v0.2.0 ISO-Aligned Technical Specification

Document ID: `ACH-NANO-V020-ISO-TECH-002`

Status: RELEASE_ARTIFACT

This is an ISO-aligned technical record, not ISO certification, a conformity
assessment or a claim of certified compliance.

## Identification And Configuration

| Field | Value |
| --- | --- |
| System/model | AchiticLM Nano v0.2.0 |
| Model family | AchiticLM Core |
| Architecture | Decoder-only Transformer; GQA, RoPE, RMSNorm, SwiGLU |
| Parameters | `4,999,424` |
| Vocabulary / context | `8000` / `128` |
| Dimensions | dim `256`; layers `4`; heads `4`; KV heads `2`; FFN `704` |
| RoPE theta | `10000.0` |
| Initialization | Scratch, no external pretrained weights |
| Full / safe artifacts | `nano.pt` / `nano-fp16.safetensors` |

## Lifecycle Evidence

| Area | Evidence |
| --- | --- |
| Data provenance | Vietnamese Wikipedia shard URL/date/checksums and attribution recorded |
| Data controls | Namespace filtering, markup cleanup, privacy heuristics, dedup and deterministic split |
| Contamination | `0` normalized fixed-prompt matches |
| Training | `5000` scratch steps plus `800` project-authored SFT steps |
| Evaluation | Held-out loss plus `10/10` controlled prompt review |
| Verification | `91 passed, 1 skipped`; Tiny shared-path smoke PASS |
| Integrity | Package `SHA256SUMS` |

## Risk Register

| Risk | Control | Residual risk |
| --- | --- | --- |
| Controlled score mistaken for broad quality | Explicit near-domain scope in all release docs | Users may ignore documentation |
| SFT degrades broad modeling | Pre/post held-out loss is disclosed | Candidate remains narrow |
| Incorrect or unsafe generation | Unsupported-use policy and no safety claim | Output can still be harmful or wrong |
| Training-data privacy | URL/email/phone heuristics and no corpus redistribution | Heuristics cannot prove absence of PII |
| Unsafe checkpoint deserialization | Checksums and safetensors alternative | Full `.pt` remains trusted-only |
| Export overclaim | GGUF/quant assets excluded | Future artifacts need exact llama.cpp evidence |

## Change Control

Any change to weights, tokenizer, special IDs, config or SFT data requires a new
candidate checksum set and rerun of the fixed-prompt, held-out, full-test and shared
Tiny-path gates.
