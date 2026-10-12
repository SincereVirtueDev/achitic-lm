# Phase 5 - Alignment and safety

Dependency: `03_PRETRAIN_SCALE.md` must have base quality gate PASS. For 1B-class alignment, `04_1B_INFRA.md` should also PASS.

Không chạy DPO trước khi base model và SFT có chất lượng tối thiểu. SFT/DPO hiện là reference single-device loop, chưa phải production alignment pipeline.

## Mục tiêu

Xây dựng pipeline instruct bằng dữ liệu SFT và preference có provenance, sau đó đánh giá behavior, safety, hallucination và prompt-injection resilience bằng prompt set cố định.

## Task checklist

- `ALN-001`: Tạo schema và data card cho SFT: prompt, response, language, source, license, quality label, privacy status.
- `ALN-002`: Tạo schema và data card cho preference/DPO: prompt, chosen, rejected, source, license, annotator/process note.
- `ALN-003`: Thêm validation script cho JSONL SFT/DPO, bao gồm length/context truncation report.
- `ALN-004`: Thêm CPU tests cho SFT prompt masking để prompt token không tính loss.
- `ALN-005`: Thêm CPU tests cho `sequence_logprob` response-only scoring.
- `ALN-006`: Cải thiện alignment checkpoint metadata: base checkpoint ref, tokenizer checksum, data manifest checksum, alignment stage.
- `ALN-007`: Thiết lập fixed eval prompt set: Vietnamese QA, English QA, code, refusal/safety, hallucination probes, prompt injection.
- `ALN-008`: Thêm side-by-side sample report base vs SFT vs DPO.
- `ALN-009`: Định nghĩa DPO gate: chỉ chạy nếu SFT cải thiện eval hoặc có lý do rõ.
- `ALN-010`: Document limitation. Không claim assistant production-ready nếu chưa có human eval và safety review.

## Exit gates

Phase này chỉ PASS khi có evidence:

- SFT/DPO data có provenance, license và privacy check.
- JSONL validation pass.
- CPU tests cho SFT masking và DPO logprob pass.
- SFT run có eval/sample report.
- DPO chỉ chạy sau SFT gate, có before/after comparison.
- Safety/prompt injection eval report có lưu artifact.
- Không có pretrained weights hoặc external chat model bị trộn vào checkpoint.

## Suggested split cho nhiều model

- Model A: SFT/DPO schema và validation.
- Model B: tests masking/logprob.
- Model C: alignment metadata và checkpoint contract.
- Model D: eval prompt set và sample report.
- Model E: safety report và DPO go/no-go.

Người chốt phase phải kiểm tra data license giống phase 2, không chỉ kiểm tra training loss.

## Phase Closeout

```text
Status: NOT_STARTED
Closed by:
Date:
Commit or artifact ref:
Evidence:
- pytest:
- Nano smoke train:
- SFT validation:
- DPO validation:
- safety eval:
- sample report:
Notes:
```
