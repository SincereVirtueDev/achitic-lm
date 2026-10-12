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
