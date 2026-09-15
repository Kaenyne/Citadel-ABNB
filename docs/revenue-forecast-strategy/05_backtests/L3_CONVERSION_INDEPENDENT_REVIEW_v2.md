# L3 conversion validation — independent publication closure v2

Reviewer: cohort_fx, independent of author adr_hotel. Review date: 2026-09-13. Branch: codex/lane3-full. This closes the two publication items in `L3_CONVERSION_INDEPENDENT_REVIEW_v1.md`; the detailed independent numerical audit remains in that preserved note.

## Acceptance decision

**The five-parameter descriptive specification and chronological validation protocol are accepted after independent audit. Free-weight forecast promotion is rejected by the preregistered hurdle. Production adoption remains pending L4/team review, with the existing operational fixed 2/3 kernel retained.**

The requested 22-quarter model jointly estimates four seasonal conversion rates and one common bounded lag coefficient, with no intercept. The full-sample USD fit is w=0.786478481 and Q1/Q2/Q3/Q4 rates of 12.931911/13.224232/17.302744/12.111558 percent. This is a descriptive reduced-form calibration. The identically fitted fixed-weight benchmark beats the free-weight model chronologically: free/fixed RMSE ratios are **1.165407390 in W1 (n=14)** and **1.015512948 in W2 (n=10)**. The validation acceptance does not turn w into a measured booking probability, lambda into take rate, or an in-sample fit into evidence of a prospective edge.

## Repairs verified

1. **Matched chart comparison closed.** Independently viewed the final `results_v2/03_chronological_validation.png`. Both panels now show the free and fixed matched OLS models, the existing last3-excluding-2021 fixed comparator, harness naive, and the explicitly advantaged guide-plus-cushion benchmark. Independently checked all ten chart cells against `chronological_scores.csv`: each W1 bar uses 14 quarters; each W2 bar uses 10. The operational comparator RMSEs are $52.207377M and $51.188606M. The code asserts equal coverage among plotted bars. K0's n=12 W1 abstention results remain available in the numerical tables and notes, outside this full-coverage absolute-error chart. The image is legible with no clipped labels or overlaps; its post-guide information advantage and imprecise paired-year ranges remain explicit.
2. **Shared-weight title closed.** Independently viewed final `results_v2/01_seasonal_conversion.png`. It says “One shared weight. Four seasonal conversion rates.” The chart correctly identifies the full-sample 22-quarter fit and the coefficient's reduced-form meaning. The points, seasonal lines, coefficient values and year-block sensitivity ranges remain unchanged.
3. **Generic-import collision closed.** Inspected the conversion test loader and runner. Tests load the local runner under `_conversion_validation_v1_runner_test`; the runner loads its local model/charts through `_conversion_validation_v1_...` module names, so another suite's cached `run` cannot supply its API. Lead independently reran the exact six-suite command that failed previously: **132 passed, 3 subtests passed in 19.00 seconds, exit 0**. The previous five import failures are preserved in the joint-test failure note/receipt. The conversion suite had already passed all 21 analytical tests independently; this joint receipt closes the actual integration failure rather than changing research results.
4. **Adapter and wording checked.** The four seasonal adapter rows now use `percent_of_weighted_lagged_GBV_coefficient_level` for coefficient levels; values and bounds are unchanged. The claim ledger adds the numerical full22 fit, estimation-window sensitivities, and W1/W2 negative result. Prohibited structural and forecasting interpretations remain explicit. No probability, precision interval, or operational adoption was added.

## Numerical preservation

Independently compared all 24 files shared by `results_v1` and `results_v2`: **18 are byte-identical**, including all estimates, observations, fitted values, chronological paths/scores, profile tables, parameter and paired bootstrap draws, uncertainty tables, leave-year-out fits, source manifest, summary, and both identification-chart formats. The six changed files are the PNG/SVG pairs for figures 01 and 03, the claim ledger, and L4 adapter units. The analytical `model.py` hash is unchanged.

The earlier independent checks remain applicable: direct five-parameter fits across six specifications; reconstruction of all 14 historical origins without calling package fit/predict; future-observation perturbations; registry date/coverage matching; all 56 interval cells; selected parameter-bootstrap refits and all parameter percentiles; all 12 leave-year-out fits; all 4,000 paired-year resamples; and continuous profile-flatness bounds. These support numerical acceptance, while the limited year counts and unstable fitted weight support the qualified interpretation.

## Reviewed source and artifact hashes

All SHA-256 values below were computed directly from the final chart/units output snapshot `data/processed/forecast_methods/conversion_validation_v1/results_v2/` and the source that generated it. If a later immutable output only binds this completed review into acceptance metadata, these numerical and chart hashes remain the identity checks; its separate receipt should identify the final acceptance JSON.

| Artifact | SHA-256 |
|---|---|
| `model.py` | `a9046663fb0e9c705337eb537282f17e54e9f2499c019d33793677007c8d94ae` |
| `run.py`, reviewed packaging snapshot | `bb3e9f930d7a1acf050908c0e4ad53b8fa0b71018ef4425e0ef54d52aaff1e85` |
| `charts.py` | `90ba262e041970c26a7ce9c747722edfc4c56357fbcc9a2963d5a8f3254e192f` |
| `test_conversion.py` | `292a637d2d1bf53bdce949e30b2b4aeff7e1b442f5244dcbe88eea1af85119d1` |
| `parameters.csv` | `baa328ac3b8d3e6523e5de6486e8307a6510de2cec4414a4c6b78145859fc17b` |
| `chronological_scores.csv` | `3ac919a1c3f88bc5a9653c8776b015c8d3690acb186cb73676d3e4ce4d0f87a7` |
| `l4_conversion_inputs.csv` | `5b5eb57ca73ece267e8d8a8ae03050f2503e7a2cbb3fadee121896ffab9f0c82` |
| `01_seasonal_conversion.png` | `52ffcb5cef1e965127370afca0d233d0de57efeed8dd369e98e662823a7642ac` |
| `03_chronological_validation.png` | `89b39cb8527bdd531caba51b7c50e9939254b43c6bbb25e537217f74acd72248` |
| `claim_ledger.csv` | `be783ed3cb65cbe85c3ee9040dc674d970a6c2f0e40b22871ee6964b02288921` |

Lead's exact joint closure command, from the isolated repository root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 -m pytest analysis/src/forecast_methods/cohort_fx_v2/tests analysis/src/forecast_methods/fee_panel_v1/test_fee_panel.py analysis/src/forecast_methods/l3_adr_hotel_v1/test_audit.py analysis/src/forecast_methods/nclh_transfer_v1/test_nclh.py analysis/src/forecast_methods/l3_integration_v1/test_bundle.py analysis/src/forecast_methods/conversion_validation_v1 -q
```

No registration, scorer write, forecast combination, model/workbook edit, commit, push, or adoption was performed by this reviewer. Only new independent review notes were written.

## RESUME

Independent analytical and publication review is closed. Author may bind this note into an immutable final acceptance receipt and report a reproducible new-output comparison. Lead may package the accepted descriptive specification, the rejected free-weight promotion result, all limitations, and the retained fixed operational benchmark for L4. Future adoption is a separate decision; changes to the estimator, information sets or numerical outputs require new review rather than inheriting this acceptance automatically.
