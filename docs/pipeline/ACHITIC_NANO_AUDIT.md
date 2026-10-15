# AchiticLM Nano v0.1.1: báo cáo kiểm tra và danh sách việc cần sửa

Tài liệu này dành cho coding agent (Codex) thực hiện. Mỗi task có bằng chứng, file cần sửa, yêu cầu thay đổi và tiêu chí chấp nhận có thể kiểm chứng.

- **Repo:** `SincereVirtueDev/achitic-lm`, commit `626e0b4` (sau tag `nano-v0.1.1`)
- **Artifact đã kiểm tra:** `nano.pt` (SHA256 `f067c5f9…958e761b`, khớp release), `tokenizer.model` (`b1dc236a…a830b0bc6`)
- **Môi trường kiểm tra:** Python 3.13, torch 2.14.1, sentencepiece 0.2.x, gguf 0.19.0, llama.cpp `8f574b0` (2026-10-13), CPU
- **Hiện trạng test:** `pytest -q` → 25 passed trên commit `626e0b4`

## Phạm vi của tài liệu

Làm hết các task dưới đây thì phần **code, tooling và quy trình phát hành** của Nano sẽ đúng và sẵn sàng cho dữ liệu thật. Riêng việc **mô hình nói ra câu có nghĩa** thì tài liệu này không giải quyết được: việc đó cần corpus thật (mục OUT), và corpus phải do người duy trì chọn. Sau khi hoàn tất, Nano sẽ:
- export được sang GGUF, có test chứng minh khớp với llama.cpp;
- train đúng chuẩn: có LR schedule, validation và lưu checkpoint tốt nhất;
- dùng tokenizer không còn token reserved vô nghĩa;
- phát hành file trọng số an toàn, nhẹ;
- được phát hành lại thành v0.2 (task R-1).

## Ràng buộc bắt buộc (từ `AGENTS.md`)

- Không thay trọng số scratch bằng mô hình pretrained.
- Giữ nhất quán token ID, vocab size và config trong checkpoint.
- Mọi thay đổi kiến trúc hoặc export phải có test CPU, đặc biệt cho RoPE, GQA, causality và việc load checkpoint.
- **Không ghi "verified" cho GGUF/quantization** nếu chưa có test load-and-generate bằng llama.cpp. `tests/test_export_guard.py` sẽ fail nếu `scripts/export_gguf.py`, README hoặc docs chứa các cụm như `export verified` hay `gguf verified`.
- Chạy `pytest -q` và tiny smoke train trước khi merge.
- Ưu tiên thay đổi nhỏ, từng bước. Nếu đổi định dạng checkpoint theo kiểu không tương thích ngược, phải ghi vào tài liệu.

## Tổng quan

| ID | Ưu tiên | Hạng mục | File chính |
|---|---|---|---|
| P0-1 | P0 | Export GGUF permute RoPE sai chiều | `scripts/export_gguf.py` |
| P0-2 | P0 | Export GGUF gọi hàm không tồn tại trong thư viện `gguf` | `scripts/export_gguf.py` |
| P0-3 | P0 | Export GGUF ghi tensor norm ở FP16, llama.cpp abort | `scripts/export_gguf.py` |
| P0-4 | P0 | Thêm test chống tái phát cho export | `tests/test_export_gguf.py` (mới), `scripts/verify_gguf.py` (mới) |
| P0-5 | P1 | Token type của user-defined symbol sai trong GGUF | `scripts/export_gguf.py` |
| P1-1 | P1 | Vòng lặp train: LR schedule, nhóm weight decay, validation, best checkpoint | `achitic/train.py` |
| P1-2 | P1 | Tokenizer âm thầm lấp 90% vocab bằng token reserved | `achitic/tokenizer.py`, `achitic/cli.py` |
| P1-3 | P1 | Phát hành trọng số riêng, load an toàn | `scripts/export_weights.py` (mới), `achitic/cli.py`, `achitic/train.py` |
| P2-1 | P2 | `generate()` thiếu KV cache | `achitic/model.py` |
| P2-2 | P2 | Dataset quá nhỏ mà không có cảnh báo | `achitic/data.py`, `achitic/train.py` |
| P2-3 | P2 | Tài liệu: lộ đường dẫn cá nhân, thiếu số đo thật, nhãn config sai | `docs/releases/nano/*`, `releases/nano/*`, `docs/pipeline/00_MODEL_LADDER.md` |
| P1-4 | P1 | `prepare` crash khi một dòng văn bản là JSON hợp lệ nhưng không phải object | `achitic/data.py` |
| P1-5 | P1 | Encode và train tokenizer không chịu được corpus lớn | `achitic/data.py`, `achitic/tokenizer.py` |
| P1-6 | P1 | Alignment: checkpoint sau SFT/DPO không resume được; CLI chat không dùng chat template | `achitic/alignment.py`, `achitic/cli.py` |
| P2-4 | P2 | Quantize: `ffn_dim=704` không chia hết 256, k-quant bị fallback; script không có bước kiểm tra | `scripts/quantize.sh`, `configs/*.json` |
| R-1 | P1 | Train lại và phát hành Nano v0.2 sau khi sửa xong | `releases/nano/*`, `docs/releases/nano/*` |
| OUT | — | Dữ liệu huấn luyện thật (ngoài phạm vi code) | — |

---

## P0-1. Export GGUF: permute RoPE sai chiều

### Vấn đề

`achitic/model.py::rope` xoay các **cặp chiều kề nhau** `(x[2i], x[2i+1])`. Đây cũng là quy ước của kiến trúc `llama` trong llama.cpp (`LLAMA_ROPE_TYPE_NORM`). Bước permute trong converter chính thức của llama.cpp tồn tại để chuyển trọng số từ quy ước split-half (`rotate_half`) của HF sang kiểu kề nhau. Achitic đã ở sẵn kiểu kề nhau, nên **không được permute**.

`scripts/export_gguf.py` hiện có đoạn sau, kèm chú thích sai rằng "llama.cpp uses split-half RoPE":

```python
if src.endswith(('attn.q.weight','attn.k.weight')):
    heads=c.heads if 'attn.q.' in src else c.kv_heads
    tensor=tensor.reshape(heads,c.dim//c.heads//2,2,c.dim).transpose(1,2).reshape(-1,c.dim)
```

Đoạn này chuyển kiểu kề nhau sang split-half, làm hỏng Q/K trong file GGUF.

### Bằng chứng

So logits PyTorch với llama.cpp trên 64 token đầu của `examples/corpus.txt`. "stress" là `nano.pt` với Q/K nhân ×12 để attention sắc nét, nhằm làm lộ lỗi vị trí. Trọng số gần như ngẫu nhiên của `nano.pt` khiến attention gần như đều, nên che mất lỗi.

| Model | Export | max \|Δlogit\| | top-1 khớp | Δ ở vị trí 0 / 1 / 63 |
|---|---|---:|---:|---|
| nano.pt | gốc | 0.034 | 96.9% | 0.0003 / 0.0057 / 0.023 |
| nano.pt | đã sửa | 0.00026 | 100% | 0.0003 / 0.0002 / 0.0001 |
| stress | gốc | **1.85** | **18.8%** | 0.0003 / 0.135 / **1.70** |
| stress | đã sửa | 0.032 | 98.4% | 0.0003 / 0.0003 / 0.005 |

Dấu hiệu đặc trưng của lỗi RoPE: ở vị trí 0 cả hai bản đều khớp (RoPE tại vị trí 0 là phép đồng nhất), từ vị trí 1 trở đi bản gốc lệch dần và càng xa càng lệch nhiều.

### Yêu cầu

- Xoá đoạn permute Q/K và xoá chú thích sai.
- Thay bằng chú thích đúng, ví dụ: `# No Q/K permutation: Achitic RoPE rotates adjacent pairs, matching llama.cpp LLAMA_ROPE_TYPE_NORM.`

### Tiêu chí chấp nhận

- Thoả các test của P0-4.

---

## P0-2. Export GGUF: gọi hàm không tồn tại

### Vấn đề

`w.add_unknown_token_id(...)` và `w.add_padding_token_id(...)` không tồn tại trong `gguf.GGUFWriter`. Với gguf 0.19.0, script bị `AttributeError` trước khi ghi được file. Tên đúng là `add_unk_token_id` và `add_pad_token_id`.

### Yêu cầu

- Đổi sang `add_unk_token_id` và `add_pad_token_id`.
- Kiểm tra lại cận dưới `export = ["gguf>=0.10"]` trong `pyproject.toml`: đặt cận dưới là phiên bản thấp nhất có đủ các hàm đang dùng và có trong CI.

### Tiêu chí chấp nhận

- `python scripts/export_gguf.py --checkpoint <ckpt> --tokenizer <tok> --out x.gguf` chạy hết, không lỗi, với gguf 0.19.0.

---

## P0-3. Export GGUF: tensor norm ghi ở FP16

### Vấn đề

Mọi tensor, kể cả trọng số RMSNorm 1-D, đều được ghi bằng `tensor.half()`. Khi decode, llama.cpp abort với lỗi:

```
ggml-cpu/binary-ops.cpp:135: binary_op: unsupported types: dst: f32, src0: f32, src1: f16
```

Converter chính thức của llama.cpp luôn giữ tensor 1-D ở F32.

### Yêu cầu

```python
w.add_tensor(dst, (tensor if tensor.ndim == 1 else tensor.half()).numpy())
```

### Tiêu chí chấp nhận

- Trong file GGUF xuất ra, mọi tensor 1-D (`*_norm.weight`, `output_norm.weight`) có type F32, mọi tensor 2-D có type F16.
- llama.cpp load và decode được file mà không abort.

### Diff gộp cho P0-1, P0-2 và P0-3

Diff đã kiểm tra bằng `git apply --check` trên commit `626e0b4`:

```diff
diff --git a/scripts/export_gguf.py b/scripts/export_gguf.py
index e6c089f..ed065db 100644
--- a/scripts/export_gguf.py
+++ b/scripts/export_gguf.py
@@ -24,18 +24,15 @@ def main():
     scores=[float(sp.get_score(i)) for i in range(sp.vocab_size())]
     types=[int(sp.is_unknown(i))*2+int(sp.is_control(i))*3+int(sp.is_unused(i))*5+int(sp.is_byte(i))*6 or 1 for i in range(sp.vocab_size())]
     w.add_tokenizer_model('llama');w.add_token_list(tokens);w.add_token_scores(scores);w.add_token_types(types)
-    w.add_bos_token_id(sp.bos_id());w.add_eos_token_id(sp.eos_id());w.add_unknown_token_id(sp.unk_id());w.add_padding_token_id(sp.pad_id())
+    w.add_bos_token_id(sp.bos_id());w.add_eos_token_id(sp.eos_id());w.add_unk_token_id(sp.unk_id());w.add_pad_token_id(sp.pad_id())
     sd=ck['model'];mapping={'embed.weight':'token_embd.weight','norm.weight':'output_norm.weight'}
     for i in range(c.layers):
         pre=f'blocks.{i}.';dst=f'blk.{i}.'
         for src,target in {'an.weight':'attn_norm.weight','fn.weight':'ffn_norm.weight','attn.q.weight':'attn_q.weight','attn.k.weight':'attn_k.weight','attn.v.weight':'attn_v.weight','attn.o.weight':'attn_output.weight','gate.weight':'ffn_gate.weight','up.weight':'ffn_up.weight','down.weight':'ffn_down.weight'}.items():mapping[pre+src]=dst+target
-    # llama.cpp uses split-half RoPE on Q/K; interleaved Achitic pairs require permutation.
     for src,dst in mapping.items():
         tensor=sd[src].detach().float()
-        if src.endswith(('attn.q.weight','attn.k.weight')):
-            heads=c.heads if 'attn.q.' in src else c.kv_heads
-            tensor=tensor.reshape(heads,c.dim//c.heads//2,2,c.dim).transpose(1,2).reshape(-1,c.dim)
-        w.add_tensor(dst,tensor.half().numpy())
+        # no permutation: Achitic interleaved RoPE == llama.cpp LLAMA_ROPE_TYPE_NORM
+        w.add_tensor(dst,(tensor if tensor.ndim==1 else tensor.half()).numpy())
     w.write_header_to_file();w.write_kv_data_to_file();w.write_tensors_to_file();w.close()
     print('Exported FP16 GGUF:',a.out)
 if __name__=='__main__':main()
```

---

## P0-4. Test chống tái phát cho export

Bản Nano hiện tại có trọng số gần như ngẫu nhiên, nên attention gần như đều và lỗi RoPE gần như vô hình. Test bắt buộc phải dùng trọng số có Q/K được nhân lớn.

### 4a. Test CPU, không cần llama.cpp: `tests/test_export_gguf.py`

Dùng `pytest.importorskip('gguf')`. Với một model nhỏ tạo trong test (ví dụ `vocab_size=` bằng vocab của một tokenizer SentencePiece nhỏ train ngay trong test, `dim=64, layers=2, heads=4, kv_heads=2, ffn_dim=128, context=32`):

1. Lưu checkpoint, chạy `export_gguf.main()` qua `sys.argv` hoặc subprocess.
2. Đọc lại bằng `gguf.GGUFReader` và kiểm tra:
   - `blk.*.attn_q.weight` và `blk.*.attn_k.weight` **bằng đúng** trọng số gốc (FP16, không permute). Chú ý thứ tự shape của reader.
   - Mọi tensor 1-D có type F32, mọi tensor 2-D có type F16.
   - Metadata đúng: `llama.attention.head_count`, `head_count_kv`, `rope.freq_base`, `context_length`, `block_count`, bos/eos/unk/pad ID.
3. Test quy ước RoPE: so `achitic.model.rope` với một tham chiếu NumPy độc lập của kiểu xoay cặp kề nhau `(x[2i], x[2i+1])`. Mục đích là để nếu ai đổi quy ước RoPE trong model, test sẽ báo rằng export cũng phải đổi theo.

### 4b. Kiểm tra parity với llama.cpp: `scripts/verify_gguf.py` và test tuỳ chọn

- Script nhận `--checkpoint --tokenizer --gguf --llama-cpp-dir`. Script build một chương trình C nhỏ (mã ở Phụ lục A) dựa trên `libllama`, lấy logits cho một chuỗi token ID cố định (ví dụ 64 token đầu corpus), rồi so với PyTorch. Trọng số 2-D phía PyTorch phải được làm tròn qua FP16 trước khi so.
- **Ngưỡng đạt:**
  - Model thường: `max |Δlogit| < 1e-3`.
  - Model stress (Q/K ×12): `max |Δlogit| < 0.1` và top-1 khớp ≥ 95%.
  - Bản export gốc chưa sửa phải **fail** ngưỡng stress, để chứng minh test có khả năng bắt lỗi.
- Thêm test pytest đánh dấu `@pytest.mark.skipif(not os.environ.get('LLAMA_CPP_DIR'), ...)`.
- Chỉ khi test này pass trong CI với llama.cpp được pin phiên bản thì mới được cập nhật tài liệu về trạng thái export, và vẫn phải tuân thủ `test_export_guard.py`.

---

## P0-5. Token type của user-defined symbol

### Vấn đề

Công thức hiện tại

```python
int(sp.is_unknown(i))*2+int(sp.is_control(i))*3+int(sp.is_unused(i))*5+int(sp.is_byte(i))*6 or 1
```

gán type 1 (normal) cho `<|system|>`, `<|user|>`, `<|assistant|>`, `<|tool|>`, `<|tool_result|>` và 7225 token `<|reserved_N|>`. Đúng ra các token này phải có type 4 (USER_DEFINED).

### Yêu cầu

Đọc type trực tiếp từ `ModelProto` của SentencePiece qua `sentencepiece_model_pb2`, map 1:1 sang `gguf.TokenType`:

| SentencePiece | gguf.TokenType |
|---|---|
| NORMAL=1 | NORMAL |
| UNKNOWN=2 | UNKNOWN |
| CONTROL=3 | CONTROL |
| USER_DEFINED=4 | USER_DEFINED |
| UNUSED=5 | UNUSED |
| BYTE=6 | BYTE |

### Tiêu chí chấp nhận

- Test 4a kiểm tra type của `<|user|>` là USER_DEFINED, `<0x41>` là BYTE, BOS/EOS là CONTROL.

---

## P1-1. Vòng lặp train (`achitic/train.py`)

### Vấn đề

| # | Hiện trạng | Hệ quả |
|---|---|---|
| 1 | LR cố định 3e-4, không warmup, không decay | Train dài kém ổn định, hội tụ kém |
| 2 | `AdamW(model.parameters(), weight_decay=0.1)` cho mọi tham số | Weight decay áp cả lên RMSNorm và embedding dùng chung |
| 3 | Chỉ in loss train, không có tập validation | Không biết model tốt lên hay overfit |
| 4 | Chỉ lưu checkpoint cuối | Không giữ lại được checkpoint tốt nhất |
| 5 | Không đo throughput | Khó ước lượng chi phí train Tiny |

### Yêu cầu

Thêm các tham số mới; mặc định phải giữ hành vi gần như cũ để không phá smoke test:
- `--warmup-steps` (mặc định 0)
- `--min-lr-ratio` (mặc định 1.0, tức không decay)
- `--schedule {constant,cosine}` (mặc định `constant`)

Các thay đổi:
1. **LR:** warmup tuyến tính rồi cosine decay về `lr * min_lr_ratio`. Tính theo step tuyệt đối, để resume tiếp tục đúng schedule.
2. **Nhóm weight decay:**
   - Tham số có `ndim < 2` (các norm) → `weight_decay=0`.
   - `embed.weight` (dùng chung với `head.weight`) → `weight_decay=0`.
   - Các ma trận còn lại → `weight_decay=args.weight_decay` (tham số mới, mặc định 0.1).
   - Không được đưa trùng tham số dùng chung vào hai nhóm.
3. **Validation:** thêm `--val-data`, `--eval-every`, `--eval-iters`. Hàm `evaluate()` chạy với `torch.no_grad()` và `model.eval()`, trả về loss trung bình, và in `step=… val_loss=… val_ppl=…`.
4. **Best checkpoint:** khi `val_loss` giảm, lưu thêm `<out>.best.pt`. Lưu `best_val_loss` trong checkpoint dưới dạng **khoá bổ sung**, để checkpoint format 1 cũ vẫn load được. Ghi vào `docs/CHECKPOINTS.md`.
5. **Log:** thêm `lr=…` và `tok/s=…` vào dòng log.
6. Tuỳ chọn `--dtype {fp32,bf16}`, dùng autocast khi hỗ trợ. Mặc định `fp32`.

### Tiêu chí chấp nhận

- **Test LR:** với warmup=10, tổng 100 bước, cosine, min_lr_ratio=0.1, thì LR tại step 0, 10, 55, 100 khớp công thức (sai số 1e-9).
- **Test nhóm tham số:** mọi tensor 1-D và `embed.weight` nằm trong nhóm `weight_decay=0`; tổng số tham số của các nhóm bằng `sum(p.numel() for p in model.parameters())`, không trùng.
- **Test resume:** train 6 bước liền so với train 3 bước, resume, train thêm 3 bước, thì LR tại mỗi bước như nhau.
- **Test overfit:** model `configs/nano.json` train 300 bước trên `examples/corpus.txt` với cosine và warmup 20 phải đạt loss train < 1.0 (đánh dấu `slow` nếu cần). Hiện loss sau 3 bước là 8.16.
- Smoke command trong model card vẫn chạy được.

---

## P1-2. Tokenizer âm thầm lấp vocab bằng token reserved

### Vấn đề

`achitic/tokenizer.py::train` tự thêm `<|reserved_N|>` cho đến khi đủ `vocab_size`. Với corpus mẫu, **7225 trên 8000 token là reserved**; chỉ có 510 token BPE thật và 256 token byte. Hậu quả:
- 41% tham số của model nằm ở bảng embedding, phần lớn dành cho các token vô nghĩa này.
- Khi sinh văn bản, mô hình chọn token reserved 7–21 lần trên 24 token.

### Yêu cầu

- Sau khi train tokenizer, tính tỉ lệ token reserved trên tổng vocab.
  - Nếu vượt `max_reserved_ratio` (mặc định 0.05) thì **raise lỗi** với thông báo rõ ràng: corpus quá nhỏ cho vocab đã chọn, hãy giảm `--vocab` hoặc dùng corpus lớn hơn.
  - Thêm cờ `--allow-reserved-padding` cho CLI `tokenizer` để giữ được hành vi cũ khi smoke test.
- In ra thống kê: số token normal, user-defined, reserved, byte, control.
- Cập nhật lệnh smoke trong tài liệu nếu cần thêm cờ.

### Tiêu chí chấp nhận

- Test train tokenizer trên corpus mẫu với vocab 8000: không có cờ thì raise lỗi, có cờ thì pass.
- Test thống kê: tổng các loại token bằng `vocab_size`.

---

## P1-3. Phát hành trọng số riêng, load an toàn

### Vấn đề

- `nano.pt` nặng 60 MB, gồm 20 MB trọng số và 40 MB trạng thái AdamW, cộng trạng thái RNG.
- Mọi chỗ load đều dùng `torch.load(..., weights_only=False)`, tức pickle có thể chạy code tùy ý: `train.py::load_checkpoint`, `cli.py`, `alignment.py`, `export_gguf.py`.
- Đã thử: checkpoint load được với `weights_only=True` nếu thêm `numpy.ndarray`, `numpy.dtype`, `numpy._core.multiarray._reconstruct` và dtype class vào `torch.serialization.add_safe_globals`.

### Yêu cầu

1. **Script mới `scripts/export_weights.py`:** đọc checkpoint đầy đủ và ghi file chỉ có trọng số.
   - Ưu tiên `safetensors` (thêm optional dependency `release = ["safetensors>=0.4"]`), kèm `config` trong metadata dạng JSON.
   - Tuỳ chọn `--dtype fp16|fp32`.
   - Bỏ `head.weight` vì nó dùng chung với `embed.weight`.
2. **Hàm `load_weights(path)`** trong một module dùng chung (ví dụ `achitic/checkpoint.py`):
   - Nhận `.safetensors`, hoặc `.pt` load bằng `weights_only=True` cùng các safe globals ở trên.
   - Chỉ fallback sang `weights_only=False` khi có cờ rõ ràng `--trust-checkpoint`, và in cảnh báo.
3. Cho `cli.py chat/benchmark`, `alignment.py` và `export_gguf.py` dùng `load_weights`.
4. `train.py --resume` vẫn cần optimizer và RNG: thử `weights_only=True` với safe globals trước, chỉ fallback khi có cờ.

### Tiêu chí chấp nhận

- Export `nano.pt` ra FP16 thì file khoảng 10 MB. Load lại và chạy forward cho logits khớp checkpoint gốc (trọng số đã làm tròn FP16) với sai số dưới 1e-5.
- Test: `load_weights` trên `.pt` do `save()` tạo ra thành công mà không cần `weights_only=False`.
- Thêm file trọng số vào `SHA256SUMS` và `ARTIFACT_MANIFEST.md` ở release sau.

---

## P2-1. `generate()` thiếu KV cache

### Vấn đề

`AchiticLM.generate` gọi lại forward trên toàn bộ chuỗi ở mỗi bước, độ phức tạp O(n²).

### Yêu cầu

Thêm KV cache:
- `forward(ids, cache=None, start_pos=0)` trả về `(logits, loss, cache)`, hoặc dùng một API riêng `forward_step`.
- RoPE phải nhận offset vị trí.
- GQA giữ `repeat_interleave` hoặc dùng broadcast tương đương.
- Không được làm thay đổi kết quả của `forward` khi train.

### Tiêu chí chấp nhận

- Greedy (`temperature=0`) 32 token **có** và **không có** cache cho chuỗi token giống hệt nhau.
- Logits ở mọi bước lệch dưới 1e-5.
- Test cả trường hợp prompt dài gần chạm `context`.

Tham khảo: engine JS dùng cho demo trên trình duyệt đã có KV cache và khớp PyTorch, xem Phụ lục B.

---

## P2-2. Dataset quá nhỏ mà không có cảnh báo

### Vấn đề

Với 131 token và `context=128`, `TokenDataset.__len__` trả về 1. Cả 3 bước train dùng đi dùng lại một cửa sổ duy nhất, nhưng không có thông báo nào.

### Yêu cầu

- `train.py` in ra `train windows=…, tokens=…, tokens/step=…` lúc khởi động.
- Cảnh báo nếu `len(ds) < batch * accum`, hoặc nếu tổng số token train ít hơn `steps * batch * accum * context` (tức sẽ lặp dữ liệu).
- Tuỳ chọn `--stride` cho cửa sổ chồng lấn. Mặc định bằng `context` để giữ hành vi cũ.

### Tiêu chí chấp nhận

- Có test cho số cửa sổ khi đổi stride.
- Cảnh báo xuất hiện khi chạy trên corpus mẫu, kiểm bằng `capsys`.

---

## P2-3. Tài liệu

1. **Xoá đường dẫn cá nhân** `<local-media-path>` và `<local-home-path>` khỏi:
   - `docs/releases/nano/MODEL_CARD.md`
   - `docs/releases/nano/ARTIFACT_MANIFEST.md`
   - `releases/nano/COMMAND_LOG.md`
   - `docs/pipeline/task_nano.md`

   Thay bằng đường dẫn tương đối trong repo, hoặc `<local checkout>`.
2. **Bổ sung số đo thật vào `EVAL_REPORT.md`.** Ghi rõ đây vẫn chỉ là smoke test, không phải tuyên bố về chất lượng:
   - Loss trên cửa sổ train: 8.16 (mô hình mới khởi tạo: 9.04; phân phối đều ln 8000: 8.99).
   - Loss trên câu chưa thấy: 8.71.
   - Độ lệch chuẩn trọng số sau 3 bước: 0.0200, bằng giá trị lúc khởi tạo.
3. **`MODEL_CARD.md`:** ghi kích thước thực của `nano.pt` gồm 20 MB trọng số và 40 MB optimizer, kèm phân bổ tham số:

   | Thành phần | Tham số | Tỉ lệ |
   |---|---:|---:|
   | Embedding (dùng chung) | 2,048,000 | 41.0% |
   | FFN | 2,162,688 | 43.3% |
   | Attention Q/O | 524,288 | 10.5% |
   | Attention K/V | 262,144 | 5.2% |
   | Norm | 2,304 | 0.05% |

4. Không thêm bất kỳ câu nào nói export hay GGUF "đã verified" khi P0-4b chưa pass trong CI.
5. **Nhãn config không khớp số tham số thật.** `configs/50m.json` thực tế là 30.7M, `150m.json` là 92.8M, `1b.json` là 668.3M. `00_MODEL_LADDER.md` đã ghi nhận điều này nhưng tên file vẫn gây hiểu nhầm. Hoặc đổi tên file theo số tham số thật (giữ alias cũ một phiên bản, kèm cảnh báo), hoặc sửa config cho đúng nhãn. Thêm test tính số tham số của mọi file trong `configs/*.json` và so với bảng trong `00_MODEL_LADDER.md`.

---

## P1-4. `prepare` crash với dòng là JSON hợp lệ nhưng không phải object

### Vấn đề

`achitic/data.py::prepare` gọi `json.loads(line)` rồi `obj.get('text','')`, và chỉ bắt `JSONDecodeError`. Nếu một dòng văn bản thường tình cờ là JSON hợp lệ (một con số như `2026`, một chuỗi trong ngoặc kép, `true`, `null`, hay một mảng), `obj` không phải dict nên `.get` raise `AttributeError` và toàn bộ bước prepare dừng.

### Bằng chứng

Tệp 4 dòng gồm một dòng văn bản thường, `2026`, một chuỗi JSON trong ngoặc kép, và một dòng JSONL đúng định dạng:

```text
CRASH: AttributeError 'int' object has no attribute 'get'
```

Với corpus thật cỡ hàng triệu dòng, gần như chắc chắn sẽ gặp dòng kiểu này.

### Yêu cầu

- Chỉ coi một dòng là JSONL khi `json.loads` trả về `dict` có khoá `text` kiểu `str`. Mọi trường hợp khác thì dùng nguyên dòng gốc làm văn bản.
- Tuỳ chọn `--format {auto,text,jsonl}` (mặc định `auto`) để tắt việc đoán định dạng.
- Đếm và in số dòng bị bỏ theo từng lý do: quá ngắn, trùng lặp, JSONL thiếu `text`.

### Tiêu chí chấp nhận

- Test với tệp hỗn hợp ở trên: không crash, giữ đúng 3 dòng đủ dài (dòng `2026` bị bỏ vì ngắn hơn 30 ký tự).
- Test `--format text`: một dòng JSONL được giữ nguyên chuỗi gốc, không bị bóc trường `text`.

---

## P1-5. Encode và train tokenizer không chịu được corpus lớn

### Vấn đề

Phát hiện khi đọc code; chưa chạy với corpus lớn.

- `encode_corpus` gom **toàn bộ** token ID vào một `list` của Python rồi mới ghi file. Mỗi phần tử list tốn khoảng 36 byte (con trỏ cộng đối tượng int), nên 100M token cần khoảng 3.6 GB RAM, và Tiny (500M token) cần khoảng 18 GB.
- `_train_once` gọi `SentencePieceTrainer.train` mà không đặt `input_sentence_size`, `shuffle_input_sentence` hay `num_threads`. Với corpus lớn, SentencePiece sẽ nạp toàn bộ câu vào RAM.
- Cả hai bước đều không có thanh tiến trình hay log.

### Yêu cầu

- `encode_corpus` ghi theo từng khối (ví dụ 1M token mỗi lần) bằng `np.asarray(chunk, dtype=np.int32).tofile(f)` với file mở ở chế độ append. Tuỳ chọn `--workers` để encode song song theo khối dòng, nhưng thứ tự đầu ra phải giữ nguyên.
- Kiểm tra `vocab_size < 2**31`, nếu không thì báo lỗi (hiện dùng `int32`).
- Tokenizer: thêm `input_sentence_size` (mặc định 5,000,000), `shuffle_input_sentence=True`, `num_threads=os.cpu_count()`. Đưa ra CLI dưới dạng tham số.
- In tiến trình: số dòng và token đã xử lý.

### Tiêu chí chấp nhận

- Test: file `.bin` encode theo khối giống hệt từng byte với cách cũ trên `examples/corpus.txt`, và trên một corpus tổng hợp lớn hơn kích thước một khối.
- Test: bộ nhớ đỉnh khi encode một corpus tổng hợp 5M token tăng dưới 200 MB so với lúc bắt đầu (đo bằng `tracemalloc` hoặc `resource.getrusage`, đánh dấu `slow`).

---

## P1-6. Alignment: không resume được; CLI chat không dùng chat template

### Vấn đề

- SFT và DPO chạy được trên `nano.pt` (đã thử 5 bước SFT, 3 bước DPO). Tuy vậy, `alignment.py` lưu checkpoint chỉ gồm `{'model','config','stage'}`, không có `checkpoint_format`, `optimizer` hay `step`. Kết quả là `achitic.train --resume dpo.pt` báo `KeyError: 'optimizer'`.
- Dữ liệu SFT/DPO trong repo dùng template `<|user|>…<|assistant|>`, nhưng `cli chat` đưa prompt thô vào model. Một model đã SFT sẽ bị hỏi sai định dạng so với lúc train, nên chất lượng trả lời sẽ thấp hơn mức thật của nó.
- Không có cách nào chạy hội thoại nhiều lượt.

### Bằng chứng

```text
$ python -m achitic.alignment --mode sft ... --steps 5    → chạy xong
$ python -m achitic.alignment --mode dpo ... --steps 3    → chạy xong
aligned ck keys: ['config', 'model', 'stage']
$ python -m achitic.train --resume dpo.pt ...             → KeyError: 'optimizer'
```

### Yêu cầu

- `alignment.py` lưu theo cùng contract với `train.save()`: `checkpoint_format`, `step`, `optimizer`, RNG, cộng thêm `stage`. `load_checkpoint` phải load được checkpoint aligned. Với checkpoint cũ thiếu optimizer, cho phép `--resume` với cờ `--weights-only-resume`: chỉ khởi tạo lại optimizer, và in cảnh báo.
- `cli chat`:
  - Thêm `--chat-template {none,achitic}`.
  - `achitic` bọc prompt thành `<|user|>{prompt}<|assistant|>`.
  - Mặc định là `achitic` nếu checkpoint có `stage` thuộc `sft` hoặc `dpo`, ngược lại là `none`.
- Tuỳ chọn `--interactive` để chat nhiều lượt: nối các lượt trước vào context, cắt bớt từ đầu khi vượt `context`.
- Dừng sinh khi gặp EOS hoặc `<|user|>`.

### Tiêu chí chấp nhận

- Test: train → SFT → `train --resume` chạy được, và `step` tiếp tục tăng.
- Test: với `--chat-template achitic`, chuỗi token đưa vào model bắt đầu bằng `[BOS, id(<|user|>)]` và kết thúc bằng `id(<|assistant|>)`.
- Test: sinh văn bản dừng khi model sinh ra `<|user|>`.

---

## P2-4. Quantize: k-quant bị fallback, không có bước kiểm tra

### Vấn đề

- k-quant (Q4_K, Q6_K…) yêu cầu số cột của tensor chia hết cho 256. `ffn_dim=704` không chia hết, nên mọi `ffn_down.weight` bị llama.cpp tự hạ xuống Q5_0 hoặc Q8_0. Lỗi tương tự xảy ra với `tiny.json` và `50m.json` (`ffn_dim=1408`). Các config `150m`, `350m` và `1b` thì không bị (2048, 2816 và 4096 đều chia hết cho 256).
- `scripts/quantize.sh` chỉ gọi `llama-quantize`, không có kiểm tra nào sau đó.

### Bằng chứng

Chạy `llama-quantize` trên bản GGUF đã sửa:

```text
blk.0.ffn_down.weight - ncols 704 not divisible by 256 (required for type q4_K) -> falling back to q5_0
blk.2.ffn_down.weight - ncols 704 not divisible by 256 (required for type q6_K) -> falling back to q8_0
```

Kết quả: file Q4_K_M 3.8 MB; so với F16 trên 64 token thì max |Δlogit| = 0.141, top-1 khớp 92.2%. Model gần như ngẫu nhiên nên con số này chỉ mang tính tham khảo.

### Yêu cầu

- `quantize.sh`: sau khi quantize, chạy `scripts/verify_gguf.py` (P0-4b) để so file đã quantize với bản F16. In max |Δlogit| và tỉ lệ top-1 khớp. Fail nếu top-1 khớp thấp hơn một ngưỡng (đưa ra thành tham số, ví dụ 0.9 cho Q4_K_M), và in cảnh báo nếu có tensor bị fallback.
- **Không** sửa `ffn_dim` của các config đã có checkpoint. Với config **mới** hoặc lần train lại tiếp theo (R-1), chọn `ffn_dim` chia hết cho 256. Ví dụ: Nano dùng 768 thay vì 704 (+196,608 tham số, tức +3.9%), Tiny dùng 1536 thay vì 1408. Ghi quy tắc này vào `docs/ARCHITECTURE.md`.
- Thêm test kiểm tra mọi `configs/*.json` có `dim` và `ffn_dim` chia hết cho 256, đánh dấu `xfail` cho các config cũ kèm lý do.

### Tiêu chí chấp nhận

- `quantize.sh` trả mã lỗi khác 0 khi file đã quantize không đạt ngưỡng.
- Log in ra danh sách các tensor bị fallback.

---

## R-1. Train lại và phát hành Nano v0.2

Không có task này thì sẽ không có artifact nào phản ánh các bản sửa. Ngoài ra, `nano.pt` và `tokenizer.model` hiện tại sẽ **không còn tạo lại được** bằng lệnh mặc định sau P1-2 (phải thêm `--allow-reserved-padding`).

### Yêu cầu

Thực hiện sau khi xong P0, P1-1 đến P1-6 và P2-4:

1. Train lại tokenizer. Với `examples/corpus.txt`, chọn `--vocab` đủ nhỏ để không cần token reserved, hoặc dùng corpus thật nếu đã có (mục OUT). Ghi rõ lựa chọn vào model card.
2. Train lại Nano với `ffn_dim` chia hết cho 256, có cosine schedule và validation. Nếu vẫn dùng corpus mẫu, chạy đủ số bước để model **thuộc lòng** corpus (loss train < 1.0, xem test overfit của P1-1). Mục đích là chứng minh pipeline học được, không phải tuyên bố chất lượng.
3. Tạo đủ artifact:
   - checkpoint đầy đủ (để resume);
   - `nano.safetensors` FP16 chỉ chứa trọng số (P1-3);
   - GGUF F16 đã pass `verify_gguf.py` (P0-4b);
   - tuỳ chọn Q8_0 và Q4_K_M đã pass `quantize.sh` (P2-4).
4. Cập nhật `SHA256SUMS`, `ARTIFACT_MANIFEST.md`, `MODEL_CARD.md`, `EVAL_REPORT.md` với số đo thật: loss train/val, perplexity, Δlogit của GGUF, mẫu sinh từ 3 prompt cố định với seed cố định.
5. Tag `nano-v0.2.0`. Release notes liệt kê các thay đổi không tương thích ngược: tokenizer mới, `ffn_dim` mới, định dạng checkpoint của alignment.

### Tiêu chí chấp nhận

- `sha256sum -c SHA256SUMS` pass cho mọi artifact.
- Theo `AGENTS.md`, chỉ được ghi GGUF là đã kiểm tra khi có log load-and-generate từ llama.cpp đi kèm trong release.
- Với 3 prompt lấy từ corpus mẫu, greedy sinh lại đúng phần tiếp theo trong corpus. Đây là bằng chứng thuộc lòng, không phải chất lượng ngôn ngữ, và phải ghi đúng như vậy trong `EVAL_REPORT.md`.

---

## OUT. Ngoài phạm vi code: dữ liệu

Nguyên nhân gốc khiến đầu ra vô nghĩa **không phải lỗi code** mà là dữ liệu: 6 câu, 131 token, 3 bước train. Đây là việc của người duy trì, agent không tự làm:
- Model 5M tham số cần cỡ 100M token. Bản Tiny (23M) cần cỡ 500M token.
- Mọi nguồn dữ liệu phải có ghi chép nguồn gốc, giấy phép, kiểm tra quyền riêng tư và kiểm tra nhiễm chéo train/eval, đúng theo `AGENTS.md`.
- Agent **không** tự tải dataset từ internet. Chỉ chuẩn bị công cụ: P1-1, P1-2, P2-2, cùng một script `scripts/split_val.py` để tách tập validation theo hash của từng dòng, tránh rò rỉ dữ liệu.

---

## Thứ tự thực hiện đề xuất

1. P0-1, P0-2, P0-3, P0-5 trong một PR, kèm P0-4a.
2. P0-4b (verify với llama.cpp), PR riêng, có pin phiên bản llama.cpp. Sau đó là P2-4 (quantize dùng `verify_gguf.py`).
3. P1-3 (load an toàn và trọng số riêng).
4. P1-4 và P1-5 (dữ liệu: prepare, encode, tokenizer chịu được corpus lớn).
5. P1-1 (vòng lặp train), rồi P1-2 (tokenizer), rồi P2-2.
6. P1-6 (alignment và chat template).
7. P2-1 (KV cache).
8. R-1 (train lại và phát hành v0.2).
9. P2-3 (tài liệu), cập nhật theo kết quả thật của các PR trên.

Mỗi PR phải pass `pytest -q` và chạy được tiny smoke train.

---

## Phụ lục A. Chương trình C lấy logits từ llama.cpp

Đã chạy với llama.cpp `8f574b0`.

```c
// usage: dump_logits model.gguf out.bin id0 id1 ... ; writes n_tokens*n_vocab float32
#include "llama.h"
#include <stdio.h>
#include <stdlib.h>
static void quiet(enum ggml_log_level l,const char*t,void*u){(void)l;(void)t;(void)u;}
int main(int argc,char**argv){
  llama_log_set(quiet,NULL); llama_backend_init();
  struct llama_model_params mp=llama_model_default_params();
  struct llama_model*m=llama_model_load_from_file(argv[1],mp); if(!m){fprintf(stderr,"load fail\n");return 1;}
  struct llama_context_params cp=llama_context_default_params(); cp.n_ctx=128; cp.n_batch=128; cp.n_threads=1;
  struct llama_context*c=llama_init_from_model(m,cp); if(!c){fprintf(stderr,"ctx fail\n");return 1;}
  int n=argc-3; int nv=llama_vocab_n_tokens(llama_model_get_vocab(m));
  struct llama_batch b=llama_batch_init(n,0,1);
  for(int i=0;i<n;i++){b.token[i]=atoi(argv[i+3]);b.pos[i]=i;b.n_seq_id[i]=1;b.seq_id[i][0]=0;b.logits[i]=1;}
  b.n_tokens=n;
  if(llama_decode(c,b)){fprintf(stderr,"decode fail\n");return 1;}
  FILE*f=fopen(argv[2],"wb"); for(int i=0;i<n;i++) fwrite(llama_get_logits_ith(c,i),sizeof(float),nv,f); fclose(f);
  printf("ok n=%d vocab=%d\n",n,nv); return 0;
}
```

Build:

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=OFF && cmake --build build -j --target llama-simple
gcc -O2 -o dump_logits dump_logits.c -I$LLAMA/include -I$LLAMA/ggml/include \
    -L$LLAMA/build/bin -lllama -lggml -lggml-base -Wl,-rpath,$LLAMA/build/bin
```

Phía PyTorch: load trọng số, làm tròn tensor 2-D qua `.half().float()` để khớp FP16 trong GGUF, chạy forward trên cùng chuỗi ID, rồi so `max |Δ|`, top-1 khớp và KL theo từng vị trí.

## Phụ lục B. Số đo tham khảo (đã kiểm chứng)

| Mục | Giá trị |
|---|---|
| Tham số | 4,999,424 (không tính embedding: 2,951,424; mỗi block 737,792) |
| FLOPs/token (forward) | ≈ 10.0M, cộng ~0.5M cho attention ở context 128 |
| KV cache | 4 KB/token (FP32); 512 KB với context 128 |
| Tokenizer | 510 token normal, 5 token hội thoại, 7225 reserved, 256 byte, 3 control, 1 unk |
| Engine JS (tokenizer + Transformer + KV cache) so với PyTorch/SentencePiece | Tokenizer khớp 11/11 câu thử (có dấu tiếng Việt, emoji, full-width, user symbol); logits lệch < 1e-6; greedy 24 token giống hệt; ~13 ms/token trên CPU |
