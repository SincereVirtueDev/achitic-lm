# Coding-agent contract (Codex / Claude)
- Do not replace scratch-initialized weights with pretrained models.
- Keep tokenizer ID, vocabulary size and checkpoint config consistent.
- Add CPU tests for every architectural change, especially causality, RoPE, GQA, and checkpoint loading.
- Never report an export or quantization as verified without a llama.cpp load-and-generate test.
- Dataset sources require provenance, licensing, privacy checks and train/eval contamination checks.
- Run `pytest -q` and the tiny smoke train before merging.
- Prefer minimal incremental changes and document breaking checkpoint format changes.
