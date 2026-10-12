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

The checkpoint `config` must instantiate `Config` and match the model config before state dict loading. A mismatch is a checkpoint contract failure.

## Resume Semantics

Current marker: `model_optimizer_rng_restored_data_order_not_exact`

Resume restores:

- model weights,
- optimizer state,
- global step,
- CPU torch RNG,
- NumPy RNG,
- Python RNG,
- CUDA RNG when available.

Resume is not bit-exact against an uninterrupted train run because the current format does not store a data cursor, DataLoader iterator position, RandomSampler order, DistributedSampler epoch/batch offset, or worker RNG state. On resume, the loader is rebuilt and training continues from the saved global step with restored model, optimizer and RNG state.

Exact data-order resume is future scale work. It requires storing and testing sampler/data cursor state before it can be claimed.
