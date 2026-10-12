# AchiticLM architecture
Scratch-initialized decoder-only Transformer: tied embedding/output, pre-RMSNorm, causal scaled-dot-product attention, grouped-query attention, interleaved RoPE, SwiGLU MLP. This repository does not import pretrained weights.

Nano, Tiny, Mini, Small, 350M-class and 1B-class targets share this same core architecture. Size changes should happen through config calibration and backend/infrastructure work, not by forking the model structure.

Training loss is next-token cross-entropy. SFT masks prompt tokens; DPO compares response-only sequence log probabilities against a frozen reference snapshot. DPO here is a pedagogical single-device baseline, not an optimized trainer.

DDP replicates the complete model per rank; it is not model sharding. For 1B use FSDP2 / sharded optimizer or large-memory accelerators; 4GB target is quantized inference only.

GGUF exporter maps to LLaMA-style tensor naming and attempts the interleaved-to-split RoPE permutation. Compatibility with the target llama.cpp version must be proven by a pinned load-and-generate test before any artifact is called verified. The exported tokenizer uses SentencePiece and byte fallback; tokenizer parity must test BOS/EOS/UNK/PAD IDs, byte fallback, encode/decode samples and generated text before publishing.
