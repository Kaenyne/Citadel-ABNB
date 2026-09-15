# Workboard completion — improvement_0915_theo joint cohorts

15 September 2026 · `codex/submission-readiness-v1` · additive completion of `WORKBOARD_improvement_0915_theo_joint_v1.md`

## Status

| Package | Owner | Completion |
|---|---|---|
| GE-JOINT-DATA | joint_cohort_data_0915 | COMPLETE: inspected actual repo and merged PR 60 sources; direct current corporate cohort ledger unavailable; flight-vintage lineage and raw-access limits documented |
| GE-JOINT-QUANT | joint_cohort_quant_0915 | COMPLETE: coherent backward/forward matrix, same-quarter/lagged/finite-tail model, preregistered identification and variance tests, early-origin guide race, PR 60 flight ablation and full rebuilds |
| GE-JOINT-REVIEW | chart_auditor | COMPLETE: engineering PASS; cohort precision FAIL; forecast promotion FAIL; physical measurement UNAVAILABLE |
| GE-JOINT-DELIVERY | parent | COMPLETE: consolidated interpretation, two reviewed charts, additive research registration and both unchanged scorers with preservation checks |

The requested research audit is complete. Obtaining a new matched reservation/value/fee panel is the next proposed work package, not work silently claimed as completed. Existing live forecasts and pitch artifacts remain unchanged. No commit or push was performed for this new research package.

## Read these results together

- [Consolidated pitch-use decision and next steps](05_backtests/improvement_0915_theo_joint_results_v1.md)
- [Quant results and parameter counts](05_backtests/JOINT_COHORT_QUANT_RESULTS_v1.md)
- [Full deterministic rebuild validation](05_backtests/JOINT_COHORT_QUANT_VALIDATION_v1.md)
- [Final independent review](05_backtests/JOINT_COHORT_REVIEW_v2.md)
- [Data audit](05_backtests/JOINT_COHORT_DATA_v1.md)
- [Pinned-fetch supplement](05_backtests/JOINT_COHORT_DATA_PINNED_FETCH_v2.md)
- [Frozen-scorer origin/horizon limitation](05_backtests/JOINT_COHORT_HARNESS_CHANGE_REQUEST_v1.md)

Canonical visuals are `outputs/gbv-joint-cohort-20260915-v2/01_joint_uncertainty.png` and `02_guide_forecast_test.png`, with SVGs and a source-hash manifest. Both final PNGs were visually inspected. Version 1 is retained but superseded.

## Verification closure

The complete deterministic core rebuild reproduces 21 outputs byte-for-byte and preserves six input hashes. The supplemental rebuild reproduces 11 outputs byte-for-byte. Both core and supplemental manifests match their first accepted runs. The author's 11 tests pass. The independent review has 24 tests passing; its separate source, saved-output, supplemental-diagnostic and prepared-registry suites also pass. These partly overlapping suite counts are not extra economic observations and are not added together.

Forty-two historical replay rows were registered under a new method, with W1 n=11 and W2 n=10 per guide/revenue target. No live, oracle or conditional sensitivity rows were registered. Both frozen scorer versions returned zero, agreed on all 292 resulting score rows, preserved all 288 preexisting score rows and preserved 122 original protected files. The two added registry files raise the protected inventory to 124. Baseline-relative frozen-scorer flags are not used for promotion because their lookup omits origin/horizon; the same-origin local race is authoritative.

Primary historical guide RMSE improves from $74.59m to $64.29m in W1 and from $77.01m to $63.83m in W2. However, removing 2024 reverses the advantage and paired uncertainty includes no improvement. Adding the one preregistered PR 60 flight feature worsens the candidate from $69.61m to $73.50m on eight matched origins. Cohort share ranges and year-deletion instability fail their prespecified limits. No live model promotion follows.

## RESUME

The user can now review the joint-cohort visual explanation and the pitch-use verdict. The next useful input is a matched original-booking-date/value × recognition-date/fee matrix with cancellations, modifications, coverage and historical vintages. Treat fitted shares as conditional assumptions until that evidence exists. Preserve the current benchmark and all failed tests; do not turn low conditional time-series variance into a claim that the underlying booking weights or physical conversion rates have been measured.
