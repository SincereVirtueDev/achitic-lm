# AchiticLM pipeline contract

Mục tiêu của bộ file này là chia roadmap thành các giai đoạn có thể giao cho nhiều model khác nhau. Mỗi model chỉ được nhận việc khi phase trước đã có closeout `PASS`, có bằng chứng test, và không phá vỡ các ràng buộc nền của repo.

## Cách dùng bắt buộc

Trước khi làm một task, model nhận việc phải đọc:

- `AGENTS.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- file phase hiện tại trong `docs/pipeline/`
- file phase ngay trước đó và mục `Phase Closeout` của file đó

Không được chuyển sang phase sau nếu phase trước chưa có `Status: PASS`. Nếu cần làm song song, chỉ tách các task không thay đổi cùng một contract, không dùng cùng output artifact, và đều giữ nguyên gate của phase hiện tại.

## Ràng buộc không được vi phạm

- Không thay scratch-initialized weights bằng pretrained model.
- Tokenizer ID, vocabulary size và checkpoint config phải luôn khớp.
- Mọi thay đổi kiến trúc phải có test CPU, đặc biệt cho causality, RoPE, GQA và checkpoint loading.
- Không báo export hoặc quantization là đã verify nếu chưa chạy llama.cpp load-and-generate.
- Dataset phải có provenance, license, privacy check và contamination check train/eval.
- Trước khi merge hoặc chốt phase code: chạy `pytest -q` và Nano smoke train.
- Ưu tiên thay đổi nhỏ, tăng dần. Mọi thay đổi format checkpoint breaking phải được document rõ.

## Repo map hiện tại

- `achitic/model.py`: decoder-only Transformer, tied embedding/output, pre-RMSNorm, causal SDPA, GQA, interleaved RoPE, SwiGLU.
- `achitic/tokenizer.py`: SentencePiece BPE tự train, byte fallback, special IDs cố định.
- `achitic/data.py`: clean text, exact dedup theo SHA-256, encode token int32, `TokenDataset`.
- `achitic/train.py`: pretraining loop, DDP replicate model, AdamW, checkpoint có RNG.
- `achitic/alignment.py`: SFT và DPO baseline single-device.
- `achitic/cli.py`: prepare, tokenizer, encode, chat, benchmark.
- `scripts/export_gguf.py`: GGUF FP16 LLaMA-style exporter experimental.
- `scripts/quantize.sh`: wrapper llama-quantize Q4_K_M.
- `tests/test_model.py`: smoke forward/backward/generation và causal test.

## Config reality check

Các nhãn config hiện tại là nominal. Số dưới đây là baseline đã ghi trong docs; trước khi chốt run phải xác nhận lại bằng `sum(p.numel() for p in model.parameters())` trong môi trường hiện tại.

| Config | Ladder role | Approx params |
| --- | --- | ---: |
| `configs/nano.json` | Nano | 4,999,424 |
| `configs/tiny.json` | Tiny | 23,058,944 |
| `configs/50m.json` | Legacy 50M label | 30,745,088 |
| `configs/150m.json` | Legacy 150M label | 92,769,024 |
| `configs/350m.json` | 350M-class candidate | 258,253,824 |
| `configs/1b.json` | 1B-class candidate | 668,345,856 |

Gate bắt buộc trước các run tốn tiền: tính lại `sum(p.numel() for p in model.parameters())`, cập nhật config hoặc đổi label để không lập kế hoạch sai ngân sách.

## Phase chain

| Phase | File | Mục tiêu chốt |
| --- | --- | --- |
| Ladder | `00_MODEL_LADDER.md` | Nano -> Tiny -> Mini -> Small -> 350M -> 1B, một core architecture |
| 1 | `01_FOUNDATION_SMOKE.md` | Baseline đáng tin, test CPU, Nano smoke, checkpoint resume |
| 2 | `02_DATA_TOKENIZER.md` | Corpus/tokenizer/eval split có provenance và license sạch |
| Tiny | `tiny/00_TINY_BOARD.md` | Tiny 20-30M CPU sau Nano và Data PASS |
| 3 | `03_PRETRAIN_SCALE.md` | Tiny, Mini/50M, Small/150M, 350M theo số liệu eval và stability |
| 4 | `04_1B_INFRA.md` | Hạ tầng sharding/streaming đủ an toàn cho 1B-class |
| 5 | `05_ALIGNMENT_SAFETY.md` | SFT/DPO và safety chỉ sau base quality gate |
| 6 | `06_EXPORT_EDGE.md` | GGUF/quantization verify bằng llama.cpp và edge benchmark |
| Backlog | `BACKLOG.md` | Danh sách task chia được cho nhiều model |

## Test ladder chuẩn

Minimum local gate:

```bash
pytest -q
```

Nano smoke train chuẩn:

```bash
python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-clean.txt
python -m achitic.cli tokenizer --input /tmp/achitic-clean.txt --prefix /tmp/achitic-sp --vocab 8000
python -m achitic.cli encode --input /tmp/achitic-clean.txt --tokenizer /tmp/achitic-sp.model --out /tmp/achitic.bin
python -m achitic.train --config configs/nano.json --data /tmp/achitic.bin --steps 3 --batch 1 --accum 1 --out runs/nano.pt
python -m achitic.cli chat --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --prompt 'Xin chao' --tokens 16
```

Benchmark gate khi có GPU:

```bash
python -m achitic.cli benchmark --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model
```

Export gate chỉ được dùng khi đã có llama.cpp:

```bash
python scripts/export_gguf.py --checkpoint runs/nano.pt --tokenizer /tmp/achitic-sp.model --out runs/nano-f16.gguf
bash scripts/quantize.sh /path/to/llama-quantize runs/nano-f16.gguf runs/nano-q4.gguf
/path/to/llama-cli -m runs/nano-q4.gguf -p "Xin chao" -n 16
```

## Handoff format cho từng model

Mỗi task được chốt bằng một đoạn ngắn trong file phase hoặc PR description:

```text
Task ID:
Scope:
Files changed:
Tests run:
Artifacts produced:
Known risks:
Next task allowed:
```

## Phase Closeout template

Mỗi phase file có một mục `Phase Closeout`. Chỉ đổi sang `PASS` khi tất cả exit gates đã có evidence.

```text
Status: NOT_STARTED | BLOCKED | FAIL | PASS
Closed by:
Date:
Commit or artifact ref:
Evidence:
- pytest:
- smoke train:
- extra phase gate:
Notes:
```
