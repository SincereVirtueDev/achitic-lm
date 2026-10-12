# Roadmap / exit gates
1. Nano smoke: tokenizer train, loss decrease on overfit corpus, deterministic causal test, checkpoint resume. Nano is the first CPU pipeline gate and uses the same architecture as every larger model.
2. Tiny CPU: 20-30M config, audited tokenizer/data, held-out perplexity, sample quality, artifact manifest and checkpoint resume evidence.
3. Mini / ~50M: clean licensed Vietnamese/English corpus; establish controlled scaling, throughput and language-balance metrics.
4. Small / ~150M: longer CPU or small-GPU run; compare tokens-per-parameter, data mix, training stability and sample quality.
5. ~350M: evaluate Vietnamese QA, code, hallucinations, prompt injection resilience and safety; improve dataset quality.
6. ~1B: budget accelerator hours and storage, introduce FSDP2, streaming shards, scheduled evaluation, optimizer state sharding, reproducible artifacts.
7. Instruct: curated SFT and human preference data; DPO only after base/SFT quality gates.
8. Edge: GGUF FP16 export, Q8/Q6/Q4 variants, pinned llama.cpp load-and-generate for each artifact, tokenizer parity, output parity, 4GB peak VRAM and tokens/sec on P1000.

Parameter labels are nominal: calculate exact count using `sum(p.numel() for p in model.parameters())` before sizing runs. Current configs are starting points, not calibrated parameter counts.

See `docs/pipeline/00_MODEL_LADDER.md` for the Nano -> Tiny -> Mini -> Small -> 350M -> 1B target ladder.

Production gaps: distributed exact data cursor resume, FSDP2, gradient scaler/AMP policy, efficient packed samples, dataset streaming and provenance, evaluation suite, secure checkpoint formats, GGUF parity integration, CI GPU matrix.
