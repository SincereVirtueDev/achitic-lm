# AchiticLM Nano ISO-Aligned Technical Specification

Document ID: `ACH-NANO-ISO-TECH-001`

Status: PUBLISHED

Release tag: `nano-v0.1.1`

Repository: `https://github.com/SincereVirtueDev/achitic-lm`

Release package: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.1.1`

## 1. Scope

This document records technical specifications for AchiticLM Nano in an
ISO-aligned structure for AI/ML system description, governance, risk evidence
and release traceability.

This document is not an ISO certificate, conformity assessment, audit report or
claim of certified compliance.

## 2. ISO/IEC Alignment References

The structure is aligned with the intent of these ISO/IEC AI standards:

| Standard | Use in this document |
| --- | --- |
| ISO/IEC 22989:2022 | AI terminology, system roles and ML terminology alignment |
| ISO/IEC 23053:2022 | AI/ML system description: data, model, training, evaluation and deployment context |
| ISO/IEC 23894:2023 | AI risk identification, controls and residual-risk notes |
| ISO/IEC 42001:2023 | AI management-system style evidence: responsibilities, lifecycle, monitoring and change control |

## 3. System Identification

| Field | Value |
| --- | --- |
| System name | AchiticLM Nano |
| Model family | AchiticLM Core |
| Model slot | `nano` |
| Configuration file | `configs/nano.json` |
| Release status | Published smoke release |
| License | Apache-2.0 |
| Intended deployment | Local CPU pipeline smoke and research/development only |
| Out-of-scope deployment | Production chat, factual QA, high-stakes decisions, safety-critical use |
| Certification status | No ISO certification claimed |

## 4. AI/ML System Description

| Component | Description |
| --- | --- |
| AI system type | Language-model pipeline artifact using machine learning |
| Model type | Scratch-initialized decoder-only Transformer |
| Learning mode | Self-supervised next-token prediction during pretraining smoke |
| Adaptation/alignment status | Not instruction-tuned; SFT/DPO code has CPU reference tests only |
| Input modality | Text token IDs |
| Output modality | Text token IDs decoded through SentencePiece |
| Runtime framework | PyTorch |
| Tokenizer framework | SentencePiece BPE |
| Pretrained external weights | None |

## 5. Architecture Specification

| Item | Value |
| --- | --- |
| Layers | `4` |
| Hidden dimension | `256` |
| Attention heads | `4` |
| KV heads | `2` |
| GQA repeat/group ratio | `2` |
| Head dimension | `64` |
| FFN dimension | `704` |
| Context length | `128` tokens |
| Vocabulary size | `8000` |
| Positional method | RoPE |
| RoPE theta | `10000.0` |
| Normalization | RMSNorm |
| MLP activation | SwiGLU-style gated SiLU |
| Attention mode | Causal scaled dot-product attention |
| Weight tying | Embedding and output head tied |
| Trainable parameters | `4,999,424` |
| Total parameters | `4,999,424` |

## 6. Configuration Control

Nano config:

```json
{
  "vocab_size": 8000,
  "dim": 256,
  "layers": 4,
  "heads": 4,
  "kv_heads": 2,
  "ffn_dim": 704,
  "context": 128
}
```

Configuration constraints:

- `vocab_size` must match the tokenizer model vocabulary size.
- `heads % kv_heads` must be `0`.
- `dim % heads` must be `0`.
- Encoded training data must contain at least `context + 1` tokens.
- Checkpoints must be loaded only with a matching config.

## 7. Data Specification

| Field | Value |
| --- | --- |
| Smoke corpus | `examples/corpus.txt` |
| Corpus type | Self-authored synthetic/example corpus |
| Release data status | Public release allowed |
| Prepared documents | `6` |
| Encoded tokens | `131` |
| Privacy status | No private dataset, credential, PII dataset or user conversation intentionally included |
| Dataset limitation | Not a curated pretraining dataset |
| Contamination status | Not applicable to quality evaluation; corpus is only for pipeline smoke |

## 8. Tokenizer Specification

| Field | Value |
| --- | --- |
| Tokenizer type | SentencePiece BPE |
| Vocabulary size | `8000` |
| `unk_id` | `0` |
| `bos_id` | `1` |
| `eos_id` | `2` |
| `pad_id` | `3` |
| Release tokenizer asset | `releases/nano/tokenizer.model` |
| Vocabulary asset | `releases/nano/tokenizer.vocab` |
| Config compatibility rule | Tokenizer vocab size must equal checkpoint/config `vocab_size` |

## 9. Training Specification

| Field | Value |
| --- | --- |
| Initialization | Random scratch initialization |
| Training command | `.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt` |
| Training steps | `3` |
| Batch size | `1` |
| Gradient accumulation | `1` |
| Optimizer | AdamW |
| Learning rate | `3e-4` default unless overridden |
| Weight decay | `0.1` |
| Gradient clipping | `1.0` |
| Distributed mode | DDP supported by train code; Nano release smoke is single-process CPU/local |
| Checkpoint output | `runs/nano.pt` and `releases/nano/nano.pt` |

## 10. Checkpoint and Resume Specification

| Field | Value |
| --- | --- |
| Checkpoint format | PyTorch checkpoint |
| Format marker | `checkpoint_format = 1` |
| Stored model state | Yes |
| Stored optimizer state | Yes |
| Stored step | Yes |
| Stored config | Yes |
| Stored RNG state | Torch, CUDA when available, NumPy and Python RNG |
| Resume semantics | `model_optimizer_rng_restored_data_order_not_exact` |
| Exact data-order resume | Not claimed |
| Security boundary | Load only trusted checkpoints; PyTorch pickle artifacts are unsafe for untrusted files |

## 11. Evaluation and Verification Evidence

| Evidence area | Result |
| --- | --- |
| Full test suite | `64 passed, 1 skipped` |
| Environment baseline | Dependency import and pytest passed |
| Architecture tests | Forward/backward/generation, causality, RoPE, GQA, KV-cache parity and tied weights tested |
| Checkpoint tests | Save/load/config/optimizer/RNG and mismatch rejection tested |
| Data/tokenizer/CLI tests | Cleaning, prepare, TokenDataset, tokenizer special IDs and vocab mismatch tested |
| Alignment tests | SFT prompt mask and DPO response-only scoring tested |
| Export claim guard | Docs/tests prevent verified GGUF/quantization claims without llama.cpp evidence |
| Nano smoke | Prepare, tokenizer, encode, train and chat passed |
| Release smoke | Inference from `releases/nano/nano.pt` and `releases/nano/tokenizer.model` passed |
| Checksum verification | `sha256sum -c releases/nano/SHA256SUMS` passed |

## 12. Release Artifacts

| Artifact | Purpose |
| --- | --- |
| `nano.pt` | Scratch-trained Nano checkpoint |
| `tokenizer.model` | SentencePiece tokenizer model |
| `tokenizer.vocab` | Tokenizer vocabulary |
| `nano.json` | Exact Nano config copy |
| `SHA256SUMS` | Integrity verification manifest |
| `INSTALL_USAGE.md` | Installation, configuration and usage instructions |
| `README.md` | Release package overview |
| `COMMAND_LOG.md` | Reproducibility command log |
| `LICENSE` | Apache-2.0 license text |
| `NOTICE` | Project notice |
| `USAGE_TERMS.md` | Intended and unsupported usage terms |

## 13. Risk Register

| Risk ID | Risk | Control | Residual risk |
| --- | --- | --- | --- |
| R-001 | Users may assume Nano is a quality language model | Model card, usage terms and README state Nano is a smoke artifact | Misuse remains possible if docs are ignored |
| R-002 | Reserved tokens appear in generated output | Limitation documented; no language-quality claim made | Output remains unsuitable for end users |
| R-003 | Tokenizer/checkpoint vocab mismatch | CLI/config guard raises clear error; tests cover mismatch | Users can still manually bypass checks in custom code |
| R-004 | Unsafe checkpoint loading | Security docs require trusted storage and checksum verification | PyTorch pickle risk remains inherent to `.pt` checkpoints |
| R-005 | Export/quantization overclaim | Export guard docs/tests require llama.cpp load-and-generate evidence | Future exporter work must keep guard current |
| R-006 | Exact resume misunderstanding | Resume semantics documented as non-exact data order | Exact scale resume remains future work |
| R-007 | Training data rights ambiguity | Corpus declared self-authored synthetic/example and Apache-2.0 compatible | Future real datasets require separate provenance and license audit |

## 14. Operational Controls

| Control area | Current control |
| --- | --- |
| Access to source | Public GitHub repository |
| Release integrity | SHA256 checksums |
| Secret handling | Local publication credentials, `.venv`, `runs/`, `*.pt`, `*.model`, `*.vocab`, `*.gguf` ignored by Git |
| Dependency reproducibility | `pip install -e '.[dev]'`; dependencies recorded in `pyproject.toml` |
| Change control | Pipeline board and task evidence in `docs/pipeline/task_nano.md` |
| Lifecycle gate | Nano closed at 100%; Tiny/Data phases depend on closeout rules |
| Monitoring | No deployed service monitoring; local smoke/test evidence only |

## 15. Acceptance Criteria

Nano is acceptable only for:

- local installation verification,
- CPU pipeline smoke,
- checkpoint/tokenizer contract validation,
- research and education on the AchiticLM code path,
- release packaging rehearsal.

Nano is not acceptable for:

- production assistant behavior,
- factual or safety-critical answers,
- high-stakes decisions,
- benchmark or quality claims,
- verified edge/quantized deployment claims.

## 16. Traceability Matrix

| Requirement | Evidence |
| --- | --- |
| Same architecture ladder | `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `configs/nano.json` |
| No pretrained weights | `README.md`, `AGENTS.md`, scratch initialization in `achitic/model.py` |
| Tokenizer/config consistency | `tests/test_data_tokenizer_cli.py`, `achitic/cli.py` |
| CPU architecture coverage | `tests/test_model.py` |
| Checkpoint contract | `tests/test_checkpoint.py`, `docs/CHECKPOINTS.md` |
| Alignment reference guard | `tests/test_alignment.py` |
| Export overclaim guard | `tests/test_export_guard.py`, `docs/pipeline/06_EXPORT_EDGE.md` |
| Release package evidence | `docs/releases/nano/ARTIFACT_MANIFEST.md`, `docs/releases/nano/RELEASE_CHECKLIST.md` |
| Usage and limitation terms | `docs/releases/nano/USAGE_TERMS.md`, `INSTALL_USAGE.md` |

## 17. Open Items

- Real dataset card, licensing, privacy scan and contamination checks for non-smoke training.
- Exact data-order resume with sampler/cursor state.
- Evaluation suite for perplexity, fixed samples, safety and robustness.
- GGUF/quantization verification with pinned llama.cpp load-and-generate.
- Production-grade monitoring, incident response and model lifecycle records.
