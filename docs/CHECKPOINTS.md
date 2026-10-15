# Checkpoint Contract

Status: Nano baseline contract

AchiticLM checkpoints are scratch-trained PyTorch artifacts. They must be loaded only from trusted local sources because `torch.load(..., weights_only=False)` can execute unsafe pickle payloads.

## Format

Current format version: `1`

Required keys:

- `checkpoint_format`: integer format marker.
- `resume_semantics`: resume behavior marker.
- `model`: `AchiticLM.state_dict()`.
- `optimizer`: optimizer `state_dict()`.
- `step`: next global train step to run.
- `config`: serialized `achitic.model.Config` fields.
- `rng`: CPU torch RNG state.
- `cuda_rng`: CUDA RNG states if CUDA is available, otherwise `None`.
- `numpy_rng`: NumPy RNG state.
- `python_rng`: Python `random` RNG state.

Optional additive keys:

- `best_val_loss`: best validation loss observed so far when validation is enabled.

The checkpoint `config` must instantiate `Config` and match the model config before state dict loading. A mismatch is a checkpoint contract failure.

## Resume Semantics

Current marker: `model_optimizer_rng_restored_data_order_not_exact`

Exact data-order resume: `False`

Resume restores:

- model weights,
- optimizer state,
- global step,
- CPU torch RNG,
- NumPy RNG,
- Python RNG,
- CUDA RNG when available.

When `best_val_loss` is present, resume carries it forward so later validation can continue writing `<out>.best.pt` only when the resumed run improves on the previous best value.

Current training uses separate AdamW decay/no-decay parameter groups. Older checkpoints saved with a single optimizer parameter group are migrated on load by matching optimizer state to the current model parameter objects; this is a compatibility bridge, not a new exact data-order resume claim.

Resume is not bit-exact against an uninterrupted train run because the current format does not store a data cursor, DataLoader iterator position, RandomSampler order, DistributedSampler epoch/batch offset, or worker RNG state. On resume, the loader is rebuilt and training continues from the saved global step with restored model, optimizer and RNG state.

Missing state for exact data-order resume:

- data cursor,
- DataLoader iterator position,
- RandomSampler order,
- DistributedSampler epoch and batch offset,
- DataLoader worker RNG state.

## Scale Gate Decision

Tiny may use current resume only for short smoke and recovery checks where exact sample order is not claimed. Long Tiny/Mini/Small runs must either:

- accept and document non-exact data order after resume, or
- implement a new checkpoint contract that stores sampler/data cursor state and proves bit-exact continuation in tests.

No release note, model card or pipeline task may claim exact resume until such a test exists.
