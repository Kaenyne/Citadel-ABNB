# L3 bundle independent review v1

Reviewer `adr_hotel` · 2026-09-13 · `codex/lane3-full`; author of ADR package, independent of integration/fee implementation. Reviewed `l3_integration_v1/bundle.py`, tests and four canonical package adapters. Production bundle not built by this reviewer because committed research sources are required first.

## Verdict and positive verification

The actual four-package normalization preserves economic values and the source metadata needed to interpret them. **1,180 rows** validate: cohort FX 1,080, fee 2, ADR/hotel 86, NCLH 12. NCLH's historical period ranges become `quarter=historical` with the original range in `source_period`; its underlying public filing timestamp stays in `source_information_date`, while the new analysis is dated to the L3 audit. Original `replacement_vs_incremental` text remains alongside the existing source treatment column without duplicate column names. NCLH `lower_bound`/`upper_bound` are copied to canonical bound fields. Noncanonical extra columns and limits remain present. This correctly avoids backdating research to a filing date and preserves cross-issuer/non-adoption restrictions.

Independent execution:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/l3_integration_v1/test_bundle.py -q -p no:cacheprovider
```

Exit 0; **10 tests passed in 1.61 seconds** at first review. A separate import-only check normalized each actual adapter and applied `validate` to the concatenation without writing a bundle. Cohort FX, fee and ADR source-column equality was exact; the NCLH field transformations above were inspected and accounted for. These are package/row counts, not independent statistical observations.

The bundle requires unique package/quarter/metric/scenario keys, rejects future/invalid information dates, nonfinite numbers, reversed bounds, missing strings and unadopted-replacement baselines. Existing destinations are refused. The bundle-local `.gitattributes` disables text conversion, and the manifest hashes actual bytes. A synthetic LF-to-CRLF mutation was independently injected after hashing and was correctly rejected by `verify`; line-ending changes are not silently normalized away.

## Findings sent to the lead

1. **P2 checksum coverage bug.** `verify` excluded any recursive file whose basename is `SHA256SUMS.json`, while the documented exception is the bundle-root manifest only. In a temporary valid one-row bundle, an unmanifested `payload/nested/SHA256SUMS.json` file was added. `verify` still returned schema PASS and one verified checksum. Fix the exclusion to the exact root-relative path `SHA256SUMS.json`, and test nested unexpected files. This does not imply an existing production payload was corrupted; none had been built.

2. **Provenance enforcement gap (delivery condition).** `build` records `git rev-parse HEAD` as the committed research source but, at initial review, did not itself require the source code/payloads to be tracked and clean at that commit. The lead's planned research-first commit can satisfy this operationally; a source-commit guard would make the “committed research source” claim independently enforceable for future reruns. Do not publish a source commit that does not contain the actual copied research outputs.

3. **Missing FX metadata hardening.** `normalize` defaulted missing `embedded_fx` to `not_applicable`, including replacement/multiply routes. The current canonical replacement rows supply the field, so this is not a current-data misstatement. A future source adapter missing this economically critical field should fail, rather than silently relabel an unknown as inapplicable. An explicit descriptive NCLH/default can be supported separately; the matching-baseline guard already follows the fail-closed principle.

The checksum counterexample used a temporary directory containing a schema-valid one-row `l4_inputs.csv`, a root hash manifest over that exact file, and then the additional nested file. It used no production output or source writes. No integration code was changed by this reviewer.

## RESUME

The lead should close the checksum bug with a regression, resolve or explicitly verify the source-commit condition before building the production bundle, and reject missing embedded-FX metadata on replacement routes. Then build from committed canonical outputs into a new immutable directory, verify hashes locally and from committed Git bytes/clean checkout, and publish the bundle commit. A new closeout note should preserve this original review. None of these integrity checks adopts a forecast or relaxes any package's research limitations.
