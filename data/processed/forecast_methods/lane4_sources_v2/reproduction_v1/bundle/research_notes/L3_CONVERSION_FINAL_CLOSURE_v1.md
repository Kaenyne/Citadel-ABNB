# L3 conversion validation — final accepted specification and reproduction

2026-09-13 · `adr_hotel` · `codex/lane3-full`. Implementation, independent analytical review, publication repairs and immutable reproduction are complete.

The accepted descriptive calibration uses all22 quarters, four seasonal through-origin coefficients and one common bounded weight: w=0.7864784808, with Q1/Q2/Q3/Q4 conversion coefficients 12.93191114/13.22423248/17.30274407/12.11155832 percent. The preregistered chronological promotion hurdle **fails both windows**, with free/fixed USD RMSE ratios 1.165407390 (W1, n14) and 1.015512948 (W2, n10). The existing fixed 2/3 operational kernel is retained; neither new free-weight parameters nor new all22 fixed-OLS coefficients are adopted.

## Accepted artifacts

Canonical directory: `data/processed/forecast_methods/conversion_validation_v1/results_v2/`.

- `accepted_validation_spec.json` contains the complete five-parameter descriptive specification, failed prospective test and pending production adoption.
- `final_review_acceptance.json` supersedes **only** that specification's initial pending-independent-review status. Its acceptance follows the actual closed reviews in `L3_CONVERSION_INDEPENDENT_REVIEW_v1.md` and `L3_CONVERSION_INDEPENDENT_REVIEW_v2.md`. It binds both reviews, the specification, all24 mathematical/presentation outputs and five source files by SHA-256.
- `l4_conversion_inputs.csv` supplies seven research-only rows: five joint calibration parameters and two chronological RMSE ratios. Treatment, baseline candidate, embedded reported-USD FX, evidence and limitations are explicit. The receipt does not change their pending L4/team adoption status.
- PNG/SVG figures are final and independently inspected. Figure03 uses only equal-coverage methods within each window; K0's two W1 abstentions remain in the numerical evidence.

Specification SHA-256: `f7cec04de2cdacfaad0fd7bb774992d933130e76918cca788bce151d482ddb40`.

Acceptance-receipt SHA-256: `bf91d81a78e79368b8815ac33f626f0c12509158f4fe24161f34fd97d09bd973`.

Initial `results_v1` is preserved. Eighteen of its24 files are byte-identical to final v2; the six differences are the two corrected chart PNG/SVG pairs, added quantitative claim-ledger wording and clarified seasonal coefficient units. All numerical estimates, paths, scoring, profile/uncertainty/LOYO/bootstrap tables and source hashes are unchanged. The independent publication note records the final reviewed code/chart hashes.

## Final checks

The focused conversion suite passes **21 tests**, including units, scalar boundaries, exact22-row reconstruction, seasonal coverage, future-outcome/GBV rejection, deterministic fit, interval algebra and refusal of an existing output destination. The previously failing combined package process now passes **132 tests plus3 subtests**, exit0 in19.00s, closing the actual generic-import collision.

Lead independently ran all six package test suites and all five package runners. The conversion runner rebuilt into the NEW directory `data/processed/forecast_methods/l3_integration_v1/reproduction_v1/conversion/`, exited0 in30.998s, and its24 files are **24/24 byte-identical** to the canonical research outputs. Its independently rerun focused tests passed21 in3.14s. The ten frozen source hashes remained unchanged. Overall integration comparison is saved in `data/processed/forecast_methods/l3_integration_v1/reproduction_comparison_v1.json`.

Author then independently verified every acceptance binding: specification, two closed review notes, five final source files, all24 canonical outputs and all24 newly rebuilt outputs match the acceptance receipt hashes. The separately issued review receipt is the25th canonical file and is deliberately not fabricated by an automatic numerical rerun. The overall integration reproduction also matched all69 analytical output files across the five L3 packages; that broader result is lead-owned evidence.

Exact final numerical reproduction command, from the worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/conversion_validation_v1/run.py --out data/processed/forecast_methods/l3_integration_v1/reproduction_v1/conversion
```

That destination now exists and must not be reused. Choose a new directory for another reproduction. Full method/results are in `L3_CONVERSION_RESULTS_v1.md`; the retained development/audit failure record is `L3_CONVERSION_AUDIT_REPAIR_v1.md`. No forecast registration, scorer mutation, model/workbook, memo, valuation, commit or push was performed by this package author.

## RESUME

Package this final canonical directory, source, result/repair notes and both closed independent reviews for L4. Verify the receipt before presenting the accepted descriptive fit, and state the failed forecasting hurdle with the fitted-weight and small-year-sample limitations. Keep operational adoption separate. Future numerical or information-set changes require a new version and review; a new mathematical reproduction does not itself create a new acceptance decision.
