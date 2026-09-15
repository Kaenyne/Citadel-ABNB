# Independent SC-A review: repair closure

2026-09-14. Reviewer C (`nclh`). **The precision source-audit package is accepted within its stated scope.** All five findings in L3_SC_REVIEW_A_v1.md are closed. This accepts source-accounting infrastructure, not a new forecast, coefficient, guide, investment claim or statistical result. Canonical precision output is `data/processed/forecast_methods/l3_source_contract_v1/precision/results_v2/`; v1 remains preserved.

I reran the exact five original in-memory attacks against the repaired code. Future lambda availability, NaN frozen revenue, an unavailable observation parent, finite-input unit overflow and a boolean observation now all raise `ValueError` with relevant reasons. The added derivation-parent and lambda-origin checks also appear in the focused author suite. Independently, **31 tests pass**. The frozen canonical inputs remain unchanged.

I independently rebuilt into `data/processed/forecast_methods/l3_source_contract_v1/consumption/independent_A_review_v2/rebuild/`. All **nine files** match the author's canonical results_v2 byte-for-byte, and all eight payload hashes in its output manifest verify. Comparing the v1/v2 discrepancy ledgers, the only changed field is `normalized_unit`: Nights/Seats now says `million_aggregate_booked_units`. Source observation unit lexemes and all 96 values/differences/classifications remain unchanged. Sensitivity rows now distinguish source-value first-known dates, inherited lambda information date September 13, and analysis information date September 14.

Coverage remains 24 quarters × four metrics = 96 cells, with 92 original cells checked and all four original 2020Q3 observations unavailable. Later corroboration does not fill original availability. The 67 exact, 18 rounding, four later-precision, two definition-difference and five unresolved classifications are unchanged. The Q4 2020 revenue, Q2 2025 original presentation conflict, later Q2 2022 rounded-history discrepancy and aggregate-booking-denominator distinctions remain visible. Primary source spot checks and the limits of those checks are recorded in review v1.

The Q1 2026 29,187 USDm number is supported by the original May filing; the August H1 subtraction remains separately dated. The current-Q3 held-fixed illustration remains 27 USDm weighted GBV difference and **4.658820541731 USDm** revenue sensitivity at lambda 0.172548908953. This does not measure a revenue refit effect or create a point-in-time replacement series. The coefficient is the inherited operational EWM input, not the failed full22 free-weight calibration. Fixed 2/3–1/3 policy and the earlier empirical FAIL remain intact; W2 is nested in W1.

Publication dates, the earliest checked finer observation, exact intraday availability and historical archived bytes remain distinct. Current original SEC pages were inspected, but no contemporaneous byte archive is asserted. IPO original body and Q2 2026 exact acceptance clock remain unavailable. Date-only sources do not certify morning-of-release access. These qualifications are material to later use and are not defects hidden by acceptance.

Final reviewed SHA-256 bindings:

| Artifact | SHA-256 |
|---|---|
| precision/run.py | `f82b66018b7a3cdd337b1c479307460c712ff2f219d95e7d02024f031dcfb2a5` |
| precision/test_precision.py | `f5d574d7c6721313237dfe456f5c5234f7e777eb64cb5180e3a2a8637297cb53` |
| precision/inputs_v1/input_manifest.json | `af137faedf8df00513234e500b265b6809b1a595d6c4a87329f245614f4e5a80` |
| precision/results_v2/output_manifest.json | `c805076609dd5975061cfb0ab9a36b853e6b7426e3a7c2f997e3c5ef7c4323e5` |

Independent receipt: `data/processed/forecast_methods/l3_source_contract_v1/consumption/independent_A_review_v2/receipt.json`, timestamp **2026-09-14T04:49:32.806956+00:00**. It binds code/input/output hashes, attack results, test command/stdout and deterministic reproduction. Exact test command: `C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe -X utf8 -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/precision/test_precision.py -q`, from isolated L3 root; exit 0, 31 passed in 0.46 seconds. No authored precision file was changed by this reviewer.

## RESUME

Parent can integrate canonical precision results_v2 with accounting and consumption contracts. Preserve all source-availability flags and original-byte limitations, use the normalized aggregate unit label, and keep source-value dates separate from audit dates. No finding remains open within this review's bounded schema/accounting/source-sample scope. Later model changes, adoption or publication require their own authorized version and review.
