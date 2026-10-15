# AchiticLM Nano v0.2.0 Security Notes

Status: RELEASE_ARTIFACT

## Trusted Loading

Verify `SHA256SUMS` before use. Prefer `nano-fp16.safetensors` for inference.
`nano.pt` is a PyTorch training checkpoint and must be loaded only from trusted
storage; never enable trusted fallback for an untrusted checkpoint.

## Data And Privacy

The pretraining corpus came from a public Vietnamese Wikipedia dump. Processing
stripped URLs and rejected email/phone-like patterns, but this heuristic does not
prove that all personal data was removed. Raw and cleaned corpus text is not in the
package. The SFT supplement is project-authored and contains no intentionally
included private data.

No API key, credential, private dataset or user conversation is intentionally
included in this release candidate.

## Output Safety

The model has no validated safety behavior and can produce incorrect, unsafe or
unexpected text. Do not use it for safety-critical, high-stakes or production
decisions.

## Export And Quantization

No GGUF or quantized artifact is included. Each future exported artifact requires
its own pinned llama.cpp load-and-generate verification.
