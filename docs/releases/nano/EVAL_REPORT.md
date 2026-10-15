# AchiticLM Nano Eval Report

Status: PUBLISHED

Nano evaluation is limited to smoke tests. It does not measure language quality.

## Test Results

```text
.venv/bin/python -m pytest -q
64 passed, 1 skipped
```

## Pipeline Smoke

- Prepare: `6` documents from `examples/corpus.txt`.
- Tokenizer: `8000` vocab, `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Tokenizer stats on the smoke corpus: `normal=510`, `user_defined=5`, `byte=256`, `control=3`, `unknown=1`, `reserved=7225`, `reserved_ratio=0.903125`.
- Encode: `131` tokens.
- Train: `3` steps with `configs/nano.json`.
- Checkpoint: `releases/nano/nano.pt`, step `3`.
- Data packing: `1` train window, `128` target tokens per epoch, `128` tokens per step.

## Current Nano-X Doc Smoke Losses

Command:

```bash
.venv/bin/python -m achitic.train --config configs/nano.json --data /tmp/achitic-nano-x-doc.bin --steps 3 --batch 1 --accum 1 --out /tmp/achitic-nano-x-doc-smoke.pt --metrics /tmp/achitic-nano-x-doc-metrics.jsonl --run-manifest /tmp/achitic-nano-x-doc-manifest.json --tokenizer /tmp/achitic-nano-x-doc-sp.model
```

Measured CPU train losses:

| Step | Train loss | Tokens seen |
| ---: | ---: | ---: |
| 1 | `9.042657852172852` | `128` |
| 2 | `8.647053718566895` | `256` |
| 3 | `8.375679969787598` | `384` |

The train token budget was `384`, which exceeds the `128` unique target tokens in the smoke corpus. This is expected for the smoke-only corpus and is not evidence of model quality.

## Inference Smoke

Release inference smoke command:

```bash
.venv/bin/python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16
```

Result: passed.

Sample output from one local smoke run:

```text
Xin chao đô<|reserved_4988|><|reserved_2081|><|reserved_4625|><|reserved_5995|> Nam<|reserved_2274|><|reserved_4860|><|reserved_833|><|reserved_6710|>� một<|reserved_5602|><|reserved_1541|><|reserved_2347|> chuỗi
```

## Quality Claims

No quality, safety, factuality, alignment or benchmark claim is made. The output above is a load/generate smoke result only and includes reserved tokenizer symbols.

## Nano v0.1.1 Candidate Smoke

Status: PASS

Commands/results:

```text
.venv/bin/python -m pytest -q
64 passed, 1 skipped

.venv/bin/python -m achitic.cli prepare --inputs examples/corpus.txt --out /tmp/achitic-v011-clean.txt
documents: 6

.venv/bin/python -m achitic.cli encode --input /tmp/achitic-v011-clean.txt --tokenizer /tmp/achitic-v011-sp.model --out /tmp/achitic-v011.bin
tokens: 131
```

Checkpoint smoke:

```text
checkpoint: runs/nano-v0.1.1-smoke.pt
step: 3
vocab_size: 8000
checkpoint_format: 1
```

This v0.1.1 candidate smoke is still a pipeline check only. It does not change the model-quality claims above. The current Nano-X code path adds KV-cache and train-loop tests, which is why the current test count is higher than the original v0.1.1 publication count.
