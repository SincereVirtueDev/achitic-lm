# AchiticLM Nano v0.2.0 Publication Record

Status: PUBLISHED_PRERELEASE

Published at: `2026-10-15T03:09:24Z`

Owning task: `NANO-X-PUBLISH-001`

## Public References

- Repository: `https://github.com/SincereVirtueDev/achitic-lm`
- Release: `https://github.com/SincereVirtueDev/achitic-lm/releases/tag/nano-v0.2.0`
- Tag: `nano-v0.2.0`
- Source commit: `66ddcf328f73eb55805de5c96f1164812714c5c2`
- GitHub release ID: `413374113`
- Release mode: public prerelease

The annotated tag peels to the source commit above, and `main` pointed to the same
commit when the release was published.

## Artifact Verification

- Public asset count: `19`.
- Every uploaded asset reported state `uploaded`.
- Every remote asset name, byte size and GitHub SHA256 digest matched the local
  package before publication.
- The public `SHA256SUMS` asset was downloaded anonymously and matched the local
  file byte-for-byte.
- `SHA256SUMS` SHA256:
  `3ec914f84f7a8739173d8d94bedb9e0fc2faa35b4941788918c692e6f3979432`.
- `nano.pt` SHA256:
  `91159067702c945c08fbd245f82ff1834a31e8aff77cc27920f11572315270b9`.
- `nano-fp16.safetensors` SHA256:
  `b945ecc7a608a85d5dda4b15cd7c7f7ce0dfc4f3b9508fda524c9b0ff6f88afd`.

## Scope

Included: full and weights-only Nano artifacts, exact tokenizer/config, checksums,
training manifest, model/eval/meaning reports, install/security/usage documents,
Apache-2.0 license and Vietnamese Wikipedia attribution notice.

Excluded: GGUF, quantized artifacts, raw/cleaned corpus, private data, credentials,
local environments and encoded datasets.

## Validation

- Committed source tree: `91 passed, 1 skipped`.
- Full checkpoint and safetensors inference produced identical controlled output.
- `NANO-MEAN-001`: `10/10` automatic and manual PASS, with the near-domain scope
  and held-out loss regression disclosed.
- Merged Nano audit addendum: complete.

This publication does not claim broad Vietnamese quality, factuality, safety,
benchmark performance or production readiness.
