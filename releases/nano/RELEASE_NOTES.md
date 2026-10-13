# AchiticLM Nano v0.1.1 Release Notes

Status: PUBLISHED

Release type: patch documentation and package refresh

## Changed

- Added `ISO_TECHNICAL_SPEC.md` to the local release package.
- Added this `RELEASE_NOTES.md` file to make asset changes explicit.
- Refreshed package README wording for the planned `nano-v0.1.1` release.
- Regenerated `SHA256SUMS` for the expanded asset set.

## Unchanged

- No pretrained weights are introduced.
- `nano.pt` is unchanged from the Nano v0.1.0 baseline if its checksum remains `f067c5f9dad26cd78d2d89b9a3347444039d0dda53e8230b351c0a28958e761b`.
- `tokenizer.model` is unchanged if its checksum remains `b1dc236a8e22c68a7201fe50dcf6ff150e494b9bea49f5f971400b1a830b0bc6`.
- `tokenizer.vocab` is unchanged if its checksum remains `d893d94f665232759a71adcceb4616b3426b97cc952f9d45e5e26c5d35f3588f`.
- `configs/nano.json` is unchanged if its checksum remains `802a2968e0b2c70ab1c2531c80cec2f9d46bd79a8e669b491ae74f4b7136be72`.
- No GGUF or quantized artifact is included or verified.
- No production, chat-quality, factual-QA or safety-critical claim is made.

## Validation Required Before GitHub Publication

```bash
.venv/bin/python -m pytest -q
sha256sum -c releases/nano/SHA256SUMS
```

Nano smoke train and release smoke must also pass before publishing `nano-v0.1.1`.
