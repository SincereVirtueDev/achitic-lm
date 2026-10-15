# Token Packing And Waste Report

Status: ACTIVE_MEASURED

Owner: SincereVirtueDev

Last updated: 2026-10-13

## Current Strategy

`TokenDataset` reads one contiguous int32 token stream and returns deterministic fixed-context windows.

For a token stream with `N` tokens, context `C` and stride `S`:

- target tokens available: `N - 1`
- default stride: `S = C`
- training windows: `1 + ((N - 1 - C) // S)`
- used target tokens: `(windows - 1) * S + C`
- tokens presented per epoch: `windows * C`
- wasted target tokens: `(N - 1) - used_target_tokens`
- maximum possible waste: `C - 1`

With default `S = C`, this is the original contiguous chunk behavior. With `S < C`, windows overlap; this can increase training token presentations for smoke or small-data experiments, but it does not create new unique data.

## Report API

Use `achitic.data.token_packing_report(path, context, stride=None)` to produce:

- `total_tokens`
- `target_tokens`
- `stride`
- `windows`
- `used_target_tokens`
- `tokens_per_epoch`
- `wasted_target_tokens`
- `waste_ratio`
- `max_possible_waste_tokens`
- `overlap_tokens_per_window`
- `packing_strategy`

The train CLI prints the same startup facts as:

```text
train windows=<n> tokens=<n> tokens/step=<n> stride=<n>
```

It warns when a corpus has fewer windows than `batch * accum`, or when the planned train token budget exceeds the unique target tokens covered by the windows.

## Tiny Decision

No new packing implementation is required before Tiny release-candidate training if the approved Tiny train split is encoded into one or more sufficiently long contiguous `.bin` files and the measured waste ratio is negligible.

Packing must be revisited if:

- the corpus is stored as many short files and each file is trained separately,
- waste ratio is material for the approved Tiny train split,
- document-boundary masking becomes a requirement,
- exact data-order resume is implemented and changes the sampler/data cursor contract.

## Interaction With Resume

This task does not change dataset order or sampler behavior. It remains compatible with the current non-exact resume contract documented in `docs/CHECKPOINTS.md`.
