# Phase 6 - Export and edge inference

Dependency: `01_FOUNDATION_SMOKE.md` must PASS for exporter smoke. The Nano smoke checkpoint `runs/nano.pt` is the first allowed exporter smoke input. Real model export also requires the relevant train/alignment phase PASS.

Không bao giờ báo export hoặc quantization là verified nếu chưa chạy llama.cpp load-and-generate trên file GGUF/quantized cụ thể.

## Mục tiêu

Đưa checkpoint AchiticLM sang GGUF, verify tokenizer parity, verify generation bằng pinned llama.cpp load-and-generate, tạo Q8/Q6/Q4 variants, và đo edge inference target như 4GB VRAM, tokens/sec, chất lượng sample.

## Task checklist

- `EXP-001`: Pin llama.cpp version/commit và ghi command build.
- `EXP-002`: Thêm exporter smoke test với checkpoint Nano.
- `EXP-003`: Verify tensor mapping LLaMA-style, nhất là Q/K RoPE interleaved-to-split permutation.
- `EXP-004`: Verify tokenizer parity: BOS/EOS/UNK/PAD IDs, SentencePiece pieces, byte fallback, encode/decode sample.
- `EXP-005`: Chạy llama.cpp load-and-generate cho FP16 GGUF.
- `EXP-006`: Tạo quantization matrix Q8, Q6, Q4 nếu tooling hỗ trợ.
- `EXP-007`: Chạy llama.cpp load-and-generate cho từng quantized file.
- `EXP-008`: Benchmark edge: model size, peak RAM/VRAM, tokens/sec, prompt, output sample, hardware.
- `EXP-009`: So sánh PyTorch generate vs llama.cpp output ở temperature 0 nếu parity khả thi.
- `EXP-010`: Document known incompatibilities theo llama.cpp commit.

## Exit gates

Phase này chỉ PASS khi có evidence:

- `pytest -q` pass nếu exporter code đổi.
- Nano smoke checkpoint `runs/nano.pt` export được.
- llama.cpp FP16 load-and-generate pass.
- Mỗi quantized artifact được test load-and-generate riêng.
- Tokenizer parity report pass hoặc limitation được ghi rõ.
- Edge benchmark có hardware cụ thể và command tái lập.
- Không có claim "4GB works" nếu chưa có peak memory evidence trên target.

## Verification command template

```bash
python scripts/export_gguf.py --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --out runs/nano-f16.gguf
/path/to/llama-cli -m runs/nano-f16.gguf -p "Xin chao" -n 16 --temp 0
LLAMA_CPP_DIR=/path/to/pinned-llama.cpp scripts/quantize.sh runs/nano-f16.gguf runs/nano-q4.gguf Q4_K_M --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model
/path/to/llama-cli -m runs/nano-q4.gguf -p "Xin chao" -n 16 --temp 0
```

## Quantization policy

`scripts/quantize.sh` is the required wrapper for Q8/Q6/Q4 release candidates. It must:

- invoke the pinned `llama-quantize`,
- record the quantization log,
- detect fallback lines such as tensors downgraded from K-quant because a shape is incompatible,
- run `scripts/verify_gguf.py` against the exact quantized artifact,
- fail when fallback or parity thresholds fail, unless `--allow-experimental` is explicitly used.

Artifacts produced with `--allow-experimental` are local experiments only. A release manifest may list a quantized artifact as supported only when it includes the exact file checksum, quantization log, fallback summary, `verify_gguf.py` report, llama.cpp commit and load-and-generate output for that same file.

## Suggested split cho nhiều model

- Model A: exporter tests và tensor mapping audit.
- Model B: tokenizer parity harness.
- Model C: llama.cpp integration commands và pinned version docs.
- Model D: quantization matrix và benchmark report.

Người chốt phase phải xem output generation thật. File tồn tại trên disk không đủ để PASS.

## Phase Closeout

```text
Status: NOT_STARTED
Closed by:
Date:
Commit or artifact ref:
Evidence:
- pytest:
- FP16 GGUF load-and-generate:
- Q8/Q6/Q4 load-and-generate:
- tokenizer parity:
- edge benchmark:
Notes:
```
