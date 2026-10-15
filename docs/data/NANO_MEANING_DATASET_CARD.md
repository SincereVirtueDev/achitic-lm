# Nano Meaning Smoke Dataset Card

Status: APPROVED_LOCAL_CORPUS_USED_FOR_V0_2_0_CANDIDATE

Owning task: `NANO-MEAN-001`

Purpose: provide a bounded real-Vietnamese corpus for Nano vocabulary coverage and
scratch pretraining, followed by a small project-authored SFT supplement for the
controlled sentence smoke. This dataset does not support broad language-quality,
factuality, safety or production claims.

## Source And License

| Field | Value |
| --- | --- |
| Source | Vietnamese Wikipedia article dump, first `pages-articles` shard |
| Snapshot | `2026-10-01` |
| File | `viwiki-20261001-pages-articles1.xml-p1p832082.bz2` |
| URL | `https://dumps.wikimedia.org/viwiki/20261001/viwiki-20261001-pages-articles1.xml-p1p832082.bz2` |
| Size | `319,249,889` bytes |
| MD5 | `8ccdb33e3b24dcd44c81e2cbd91fd626` (matched the official dump manifest) |
| SHA256 | `7cdf607f7db4e3f2d95c1732e2288f9d0ed02ebeaa1488cf75d923f5fb89f49d` |
| Attribution | Vietnamese Wikipedia contributors |
| Source license | Generally CC BY-SA 4.0 and GFDL; page-level exceptions may apply |
| Terms | `https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use` |

The raw dump and cleaned corpus are not redistributed in Git or in the model
package. The release `NOTICE` preserves source attribution. Reusers remain
responsible for reviewing Wikimedia terms and any page-level exception relevant
to their use.

## Processing

Processor: `scripts/prepare_viwiki.py`.

The processor verifies the official MD5, streams the compressed XML, accepts only
main-namespace non-redirect pages, removes common wikitext/table/reference markup,
strips URLs, rejects email and phone-like strings, applies Vietnamese/length
filters, and performs normalized exact and SimHash near-duplicate removal.

Reproduction command:

```bash
python scripts/prepare_viwiki.py \
  --input /tmp/viwiki-20261001-pages-articles1.xml-p1p832082.bz2 \
  --train-out /tmp/achitic-nano-meaning-train.txt \
  --eval-out /tmp/achitic-nano-meaning-eval.txt \
  --report docs/data/nano_meaning_corpus_manifest.json \
  --source-url https://dumps.wikimedia.org/viwiki/20261001/viwiki-20261001-pages-articles1.xml-p1p832082.bz2 \
  --snapshot-date 2026-10-01 \
  --expected-md5 8ccdb33e3b24dcd44c81e2cbd91fd626 \
  --prompts docs/eval/nano_meaning_prompts.jsonl \
  --max-sentences 100000 --eval-ratio 0.02
```

## Corpus Results

| Measure | Result |
| --- | ---: |
| Pages seen | `3,577` |
| Articles seen | `1,284` |
| Accepted train sentences | `97,978` |
| Held-out eval sentences | `2,022` |
| Normalized duplicates rejected | `576` |
| Near duplicates rejected | `12` |
| Phone-like candidates rejected | `288` |
| URLs stripped | `80` |
| Fixed-prompt contamination matches | `0` |

| Output | SHA256 |
| --- | --- |
| Clean train text | `7473ac89a976b59f9909d339b52d61685b20f9d4dae72ed550fe9fcfa1a5de22` |
| Clean eval text | `39e898e350d03be50bbbf16205fa6348733930f67df8af092485f4bc7cc51907` |
| Encoded train tokens | `1d887de48dd3668bf676c80eab87158954cc6ee726f6345ef50bb6283cffd900` |
| Encoded eval tokens | `f10a8955d539da691b4f3bdca5f1a6d23a0e4f94ba9d97000b3f0dc10cf7620b` |

The train stream contains `3,502,198` token IDs. The eval stream contains
`73,688` token IDs. Splitting is deterministic under seed
`achitic-nano-meaning-v0.2.0`.

## SFT Supplement

`examples/nano_meaning_sft.jsonl` contains `80` project-authored synthetic
prompt/response pairs. It is licensed with the project under Apache-2.0 and does
not contain third-party or private data. Its SHA256 is
`137b16d28261f2f8c8ac29791f307e14e999f442ebd5b1bb378b2a8230a5b6cc`.

The SFT set includes close paraphrases of the evaluation intents but no exact
normalized copy of a fixed prompt. Therefore the 10-prompt result measures
controlled in-domain instruction behavior and must not be generalized.

## Gate Checklist

- [x] Owner approved the bounded Vietnamese Wikipedia source for this task.
- [x] Dump date, URL, official MD5 and local SHA256 are recorded.
- [x] Main-namespace article text was extracted; redirects and markup-heavy text were excluded.
- [x] URL/email/phone-like privacy heuristics ran before acceptance.
- [x] Exact and near-duplicate filtering ran.
- [x] A deterministic held-out eval split was created.
- [x] Sentence and token statistics are recorded.
- [x] Raw and cleaned data remain outside Git and the release package.
- [x] Fixed-prompt contamination scan returned `0` matches after final prompt selection.
- [x] Wikimedia attribution is included in the release notice.

## Limitations

Privacy filtering is heuristic and cannot prove that all personal information is
absent. The source shard is only part of Vietnamese Wikipedia, and Wikipedia text
does not represent all Vietnamese domains or styles. The controlled SFT supplement
is small and intentionally close to the smoke prompts.
