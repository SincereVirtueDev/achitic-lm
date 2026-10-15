# Training Run Manifest

Status: ACTIVE

Owner: SincereVirtueDev

Last updated: 2026-10-13

## Purpose

`achitic.train` can write reproducible run evidence without changing checkpoint format.

Use:

```bash
.venv/bin/python -m achitic.train \
  --config configs/nano.json \
  --data /tmp/train.bin \
  --out /tmp/model.pt \
  --steps 3 \
  --batch 1 \
  --accum 1 \
  --schedule cosine \
  --warmup-steps 1 \
  --min-lr-ratio 0.1 \
  --val-data /tmp/val.bin \
  --eval-every 1 \
  --eval-iters 4 \
  --metrics /tmp/metrics.jsonl \
  --run-manifest /tmp/run_manifest.json \
  --tokenizer /tmp/tokenizer.model
```

The legacy train command still works without these optional flags.

## Metrics JSONL

One JSON row is written per optimizer step on rank 0.

Fields:

- `step`
- `train_loss`
- `lr`
- `tokens_this_step`
- `tokens_seen`
- `tokens_per_second`
- `elapsed_seconds`
- `grad_norm`
- `epoch`
- `batch`
- `accum`
- `device`
- `dtype`
- `compute_dtype`
- `peak_cuda_memory_bytes`
- `max_rss_bytes`
- `val_loss`
- `val_ppl`
- `best_val_loss`

## Run Manifest JSON

The manifest is written at start, updated during training, and finalized at completion.

Fields include:

- `schema_version`
- `status`
- `started_at`
- `completed_at`
- `command`
- `config_path`
- `config_sha256`
- `data_path`
- `data_sha256`
- `val_data_path`
- `val_data_sha256`
- `tokenizer_path`
- `tokenizer_sha256`
- `out`
- `resume`
- `metrics_path`
- `checkpoint_format`
- `resume_semantics`
- `device`
- `dtype`
- `compute_dtype`
- `requested_dtype`
- `world_size`
- `start_step`
- `target_steps`
- `final_step`
- `batch`
- `accum`
- `lr`
- `schedule`
- `warmup_steps`
- `min_lr_ratio`
- `weight_decay`
- `save_every`
- `eval_every`
- `eval_iters`
- `best_checkpoint_path`
- `tokens_seen`
- `last_train_loss`
- `last_lr`
- `last_val_loss`
- `last_val_ppl`
- `best_val_loss`
- `last_grad_norm`
- `peak_cuda_memory_bytes`
- `max_rss_bytes`
- `total_seconds`
- `config`

## Contract

- These files are evidence artifacts, not checkpoint state.
- Adding metrics or a manifest does not make resume exact.
- `tokenizer_sha256` is recorded only when `--tokenizer` is supplied.
- LR is recorded from the optimizer each step after applying the selected schedule.
- `--schedule constant` is the default and preserves legacy fixed-LR behavior after warmup.
- `--schedule cosine` uses linear warmup followed by cosine decay to `lr * min_lr_ratio`.
- Validation runs only when `--val-data` is supplied. `--eval-every 0` disables periodic validation, but the final step is still evaluated when validation data exists.
- `<out>.best.pt` is written only after validation improves and stores `best_val_loss` as an additive checkpoint key.
- `--dtype bf16` uses autocast when the device supports it; model weights remain stored in the configured checkpoint dtype.
