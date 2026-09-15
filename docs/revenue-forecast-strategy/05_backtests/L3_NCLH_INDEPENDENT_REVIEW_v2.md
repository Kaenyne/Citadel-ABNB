# L3 NCLH — independent review closure v2

Reviewer cohort_fx, independent of NCLH author · 2026-09-13 · codex/lane3-full.
Preserves `L3_NCLH_INDEPENDENT_REVIEW_v1.md`; reviews repaired code and `results_v4`.

## Verdict

**Implementation accepted for the reviewed scope; research FAIL remains unchanged.** All five malformed-input attacks in v1 now raise explicit ValueErrors. Eighteen author tests pass, and nine numerical/figure/verdict files are byte-identical between results_v3 and repaired results_v4. The primary-source checks, original-column checks, known-deposit-lag checks and independent RMSE reproduction recorded in v1 stand. No ABNB adoption follows.

## Repair verification

| Finding | n attacks | Repaired result |
|---|---:|---|
| N-01: exact next-day midnight | 1 | Rejected: Future source publication |
| N-02: one missing per-metric timestamp | 1 | Rejected: Missing or invalid per-row publication timestamp |
| N-03: infinite passenger and total revenues | 1 | Rejected: Nonfinite or nonnumeric observation value |
| N-04: nonhexadecimal source hash | 1 | Rejected: Missing provenance |
| N-05: whitespace source reference | 1 | Rejected: Missing provenance |
| Full package unit suite | 18 | PASS, 0.811 seconds |
| Valid-input financial outputs preserved | 9 files | Byte-identical v3/v4 |

The nine unchanged files are panel, predictions, coefficients, exclusions, scores, lambda_values, stability, verdict.json and lambda_comparison.png. L4 source paths and run manifests appropriately change to the repaired version. The reviewer re-executed the same temporary-copy attack scripts described in v1; all five were rejected. The combined independent attack/comparison and unit-test command returned exit 0 in 5.36 tool-wall seconds.

Exact package test command from the isolated repository root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -m unittest discover -s analysis/src/forecast_methods/nclh_transfer_v1 -p test_nclh.py -v
```

The byte check reads each named file in `data/processed/forecast_methods/nclh_transfer_v1/results_v3/` and `results_v4/` and asserts their bytes equal. No real input, output or code file was modified during review. The author additionally reports an identical `results_verify_v2` rebuild; this reviewer independently checked the nine economically relevant files against v3 rather than treating the author's receipt as a substitute.

Reviewed source SHA-256 values:

| File | SHA-256 |
|---|---|
| run.py | `0f8f10a2085473eae74baae31e78247fcf2248c64b28689a693f445e5df09e13` |
| test_nclh.py | `a756b3eb82a29720d8adf0af6bcebbb4d523a183462410dc3b1b1697e5e91ba8` |
| fetch.py | `b55027f8507572449983b66c5545fef340ed96e87a92669a68a877106fd6878c` |

Hash syntax and source nonblankness now fail loudly; the canonical manifest/raw-body correspondence was independently checked 47/47 in v1. This is not an assertion that arbitrary substituted valid-length hashes are automatically authenticated against a new network retrieval.

## Substantive conclusion and limits

Passenger-revenue RMSE ratios remain 1.376459 (W1 n=14) and 3.840746 (W2 n=10), and every three-observation seasonal range remains above the 0.5pp limit. Total revenue also fails. Deposit stocks overlap future voyages; these predictive weights are not measured recognition probabilities. Current ATS excludes longer-term deposit liabilities. Guidance remains unscored at n=0 because no metric-matched GAAP revenue guide/consensus dataset is assembled. Original-period issuer pages were recovered in 2026 rather than archived at each historical vintage. Those limits remain visible and do not invalidate the qualified negative result.

## RESUME

Lead may include results_v4 evidence-only rows and the two independent-review notes in the L4 bundle. Keep the original negative verdict and exact scope; do not describe NCLH as validation of the Airbnb mechanism or expand to BKNG/EXPE on these findings. Any future source refresh must preserve timestamp, metric, finite-number and source checks and rebuild under a new immutable version.
