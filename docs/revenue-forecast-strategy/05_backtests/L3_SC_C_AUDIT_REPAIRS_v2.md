# SC-C independent-review repairs and final version

2026-09-14. Canonical consumption output is now `data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v2/`; prior `results_v1`, input snapshots and verification receipts remain intact. This note supplements L3_SC_C_RESULTS_v1.md.

Reviewer B independently verified all 33,236 original cells, all nine committed L4 blobs and IDs, and all 16 inventory hashes/content comparisons. B then reproduced three callable-classifier acceptance holes: a future information date, malformed source date and wrong metric units. The canonical runner's pinned input hash already rejected changed source files, so original results were unaffected. Direct classifier validation now also requires compatible metric-specific units, valid ISO dates or timezone-bearing timestamps, source date no later than row date, and no information beyond the frozen September 13 bundle cutoff. Five new date/unit counterexamples reject; no source vintage was refreshed.

The ADR ex-FX YoY definition now explicitly says a total growth rate in percent. The original `percentage_points` units string is retained exactly, with the distinction explained in the appended definition. The FX hedge dependency now explicitly requires reconstructing a compatible **operating-only** T/B after reconciling hedge effects in the baseline, lambda and cohort construction. Supplying h alone does not certify the unresolved original aggregate T/B for `(R-h)*T/B+h` application. All model application remains blocked.

Focused verification passes **24 tests**, including all prior 18 plus metadata counterexamples and the clarified accounting definitions. All eight files reproduce byte-identically to `results_verify_v2`. All 1,187 statuses and every original value/metadata cell match v1. The status counts remain 576 conditional scenario exhibits, 603 descriptive, four comparators, four unavailable and zero observed/rejected. No new forecast or empirical result changed. The code, commands and hashes are recorded in `verification_v2/receipt.json`.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/consumption/test_consumption.py -q
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B analysis/src/forecast_methods/l3_source_contract_v1/consumption/run.py --out data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v2
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B analysis/src/forecast_methods/l3_source_contract_v1/consumption/run.py --out data/processed/forecast_methods/l3_source_contract_v1/consumption/results_verify_v2
```

These exact commands completed with exit 0; use fresh output names for future runs. No frozen tests, collector, registration, L4 file or publication action was invoked.

## RESUME

Reviewer B should close the three reproduced metadata defects and the two wording/accounting qualifications against results_v2. Parent should consume v2 for the supplement while retaining original bundle rows and dates unchanged. Required model inputs, compatible operating-only FX treatment and same-basis guide expectations remain explicit unresolved gates.
