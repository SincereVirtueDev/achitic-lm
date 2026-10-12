# AchiticLM Nano Usage Terms

Status: READY_FOR_SOURCE_COMMIT

## License Summary

AchiticLM Nano is released under the Apache License, Version 2.0.

- Code license: Apache-2.0
- Checkpoint/model weights license: Apache-2.0
- Tokenizer code license: Apache-2.0
- Tokenizer model/vocabulary license: Apache-2.0
- Example corpus license/source: self-authored synthetic/example corpus created for AchiticLM and allowed for public release

The full license text is in the repository `LICENSE` file. Attribution and
release notices are in `NOTICE`.

## Intended Usage

AchiticLM Nano may be used for research, education, development, pipeline smoke
testing, experimentation and early-stage AchiticLM Nano evaluation.

Nano is not validated for production use.

## Prohibited or Unsupported Usage

Do not use AchiticLM Nano for:

- safety-critical applications,
- unsupported factual claims,
- high-stakes decisions,
- production deployment without appropriate validation.

## Data Rights Statement

The Nano smoke checkpoint and tokenizer were generated from `examples/corpus.txt`.
The corpus is self-authored synthetic/example text created specifically for
AchiticLM. No third-party proprietary dataset, private dataset, credential,
authentication token, personal data or user conversation was intentionally used.

## Artifact Strategy

Source code, model architecture, tokenizer implementation, configurations and
documentation are intended to live in the Git repository.

Release artifacts such as `nano.pt`, `tokenizer.model`, `tokenizer.vocab` and
checksums are intended to be published as GitHub Release assets for the Nano tag.

## No Quality Claim

Nano is a scratch-initialized pipeline artifact trained for only 3 smoke steps.
It does not establish language quality, factuality, safety, alignment or
benchmark performance.
