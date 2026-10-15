# Nano v0.2.0 Controlled Meaning Smoke

Status: PASS

Date: 2026-10-15

Owning task: `NANO-MEAN-001`

## Contract

- Checkpoint: refreshed scratch-pretrained and project-SFT Nano candidate.
- Decoding: deterministic greedy decoding, maximum `32` new tokens.
- Template: Achitic `<|user|>...<|assistant|>` template selected from checkpoint stage `sft`.
- Automatic gates: 4-32 generated tokens, sentence boundary, no reserved-token text,
  trigram repeat ratio at most `0.5`.
- Manual gate: short, complete and responsive sentence for at least `8/10` prompts.

## Review Table

| ID | Generated text | Auto | Manual | Reason |
| --- | --- | --- | --- | --- |
| `vi-meaning-001` | AchiticLM Nano phục vụ nghiên cứu, thử nghiệm pipeline và đánh giá sớm trên phạm vi nhỏ. | PASS | PASS | Complete and directly introduces Nano. |
| `vi-meaning-002` | Máy học tìm quy luật trong dữ liệu để thực hiện một nhiệm vụ đã xác định. | PASS | PASS | Complete sentence about machine learning. |
| `vi-meaning-003` | Dữ liệu huấn luyện cần đủ sạch, có nguồn rõ ràng và phù hợp với mục tiêu của mô hình. | PASS | PASS | Relevant and coherent. |
| `vi-meaning-004` | Nano được xây dựng để kiểm tra pipeline mô hình, không phải để dùng trong sản xuất. | PASS | PASS | Correctly states the controlled scope. |
| `vi-meaning-005` | Kiểm thử phần mềm giúp phát hiện lỗi trước khi lỗi đó ảnh hưởng đến người sử dụng. | PASS | PASS | Complete safety-oriented testing statement. |
| `vi-meaning-006` | Tokenizer mã hóa văn bản thành token và giải mã token trở lại thành văn bản. | PASS | PASS | Concise, responsive explanation. |
| `vi-meaning-007` | Tách riêng dữ liệu đánh giá giúp đo khả năng khái quát thay vì khả năng ghi nhớ. | PASS | PASS | Gives one relevant reason. |
| `vi-meaning-008` | Thông tin riêng tư cần được loại bỏ hoặc bảo vệ trước khi dữ liệu được sử dụng. | PASS | PASS | Complete privacy statement. |
| `vi-meaning-009` | Mô hình thử nghiệm có thể tạo câu sai, lặp hoặc không bám sát yêu cầu. | PASS | PASS | States a concrete limitation. |
| `vi-meaning-010` | Kiểm tra checksum giúp phát hiện artifact bị thay đổi hoặc hỏng sau khi được tạo. | PASS | PASS | Correctly addresses checksum purpose. |

## Result

- Automatic checks: `10/10` PASS.
- Manual meaningful-sentence review: `10/10` PASS.
- Reserved-token strings: `0/10`.
- Fixed prompts found in pretraining train/eval or exact SFT prompts: `0`.

This passes the controlled gate of at least `8/10`. It is not evidence of broad
Vietnamese fluency, factual accuracy, safety, instruction generalization or
production readiness. The SFT set contains close intent paraphrases, so this is a
near-domain smoke test rather than an independent benchmark.

## Reproduction

```bash
python -m achitic.cli sample-report \
  --checkpoint releases/nano-v0.2.0/nano.pt \
  --tokenizer releases/nano-v0.2.0/tokenizer.model \
  --prompts docs/eval/nano_meaning_prompts.jsonl \
  --tokens 32 --min-generated-tokens 4 --max-repeat-ratio 0.5 \
  --device cpu --chat-template auto \
  --out /tmp/achitic-nano-v0.2.0-meaning-samples.jsonl
```
