# AchiticLM Nano Security Notes

Status: READY_FOR_GITHUB_PUBLICATION

## Trusted Loading

Nano checkpoints are PyTorch pickle artifacts. Only load `releases/nano/nano.pt` from trusted storage after verifying SHA256.

```bash
sha256sum -c releases/nano/SHA256SUMS
```

`torch.load(..., weights_only=False)` must be treated as unsafe for untrusted files.

## Privacy

The Nano smoke release was generated from `examples/corpus.txt`; no private data source, API key, credential, PII dataset or user conversation was intentionally included.

## Export

No GGUF or quantized artifact is included in this package. Export and quantization must not be called verified until llama.cpp load-and-generate passes on each artifact.
