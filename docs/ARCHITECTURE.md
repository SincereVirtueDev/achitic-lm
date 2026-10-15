# AchiticLM architecture
Scratch-initialized decoder-only Transformer: tied embedding/output, pre-RMSNorm, causal scaled-dot-product attention, grouped-query attention, interleaved RoPE, SwiGLU MLP. This repository does not import pretrained weights.

Nano, Tiny, Mini, Small, 350M-class and 1B-class targets share this same core architecture. Size changes should happen through config calibration and backend/infrastructure work, not by forking the model structure.

Training loss is next-token cross-entropy. SFT masks prompt tokens; DPO compares response-only sequence log probabilities against a frozen reference snapshot. DPO here is a pedagogical single-device baseline, not an optimized trainer.

DDP replicates the complete model per rank; it is not model sharding. For 1B use FSDP2 / sharded optimizer or large-memory accelerators; 4GB target is quantized inference only.

GGUF exporter maps to LLaMA-style tensor naming and attempts the interleaved-to-split RoPE permutation. Compatibility with the target llama.cpp version must be proven by a pinned load-and-generate test before any artifact is called verified. The exported tokenizer uses SentencePiece and byte fallback; tokenizer parity must test BOS/EOS/UNK/PAD IDs, byte fallback, encode/decode samples and generated text before publishing.

## Quant-friendly shape policy

Quantized release assets are not implied by any config name. Before publishing a new quantized artifact, the exact artifact must pass pinned llama.cpp load-and-generate verification and the release docs must cite that evidence.

For new configs intended to support llama.cpp block quantization, choose matrix dimensions that avoid silent fallback:

- `dim` must be divisible by `heads`; `heads` must be divisible by `kv_heads`; the resulting attention head dimension must be even for RoPE.
- Prefer `dim`, `ffn_dim`, query/output matrix widths and feed-forward matrix dimensions that are multiples of `32`; prefer multiples of `64` for large release targets when this does not distort the measured parameter target.
- The GQA key/value projection width, computed as `kv_heads * (dim / heads)`, should also be a multiple of `32` for quantization-friendly export.
- If a chosen quantizer reports tensor fallback because a shape is incompatible with its block size, that quantized artifact is experimental only and must not be marked verified.

Existing released or candidate configs must not be mutated in place solely to satisfy a quantizer. Add a successor config, regenerate all dependent artifacts, and document the measured parameter count and migration boundary.
