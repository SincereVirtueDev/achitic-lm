# AchiticLM Nano Eval Report

Status: PUBLISHED

Nano evaluation is limited to smoke tests. It does not measure language quality.

## Test Results

```text
.venv/bin/python -m pytest -q
25 passed in 2.82s
```

## Pipeline Smoke

- Prepare: `6` documents from `examples/corpus.txt`.
- Tokenizer: `8000` vocab, `unk=0`, `bos=1`, `eos=2`, `pad=3`.
- Encode: `131` tokens.
- Train: `3` steps with `configs/nano.json`.
- Checkpoint: `releases/nano/nano.pt`, step `3`.

## Inference Smoke

Release inference smoke command:

```bash
.venv/bin/python -m achitic.cli chat --checkpoint releases/nano/nano.pt --tokenizer releases/nano/tokenizer.model --prompt "Xin chao" --tokens 16
```

Result: passed.

Output:

```text
Xin chao<|reserved_2387|><|reserved_1849|><|reserved_3267|><|reserved_4988|><|reserved_3253|> là là<|reserved_6562|><|reserved_2081|><|reserved_3617|> trình<|reserved_6940|><|reserved_5230|> đô<|reserved_833|><|reserved_2274|>
```

## Quality Claims

No quality, safety, factuality, alignment or benchmark claim is made. The output above is a load/generate smoke result only and includes reserved tokenizer symbols.

## Nano v0.1.1 Candidate Smoke

Status: PASS

Commands/results:

```text
.venv/bin/python -m pytest -q
25 passed

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

This v0.1.1 candidate smoke is still a pipeline check only. It does not change the model-quality claims above.
