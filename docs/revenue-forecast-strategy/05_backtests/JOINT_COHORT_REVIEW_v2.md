# GE-JOINT-REVIEW — final independent acceptance and pitch eligibility

15 September 2026. Reviewer: chart_auditor; independent of the joint-model author. Additive final version; `JOINT_COHORT_REVIEW_v1.md` preserves the interim review. Base commit `2dfe0c2a1852181a246f4b6b9072e05e844d52d5`, branch `codex/submission-readiness-v1`. Review code/data: `gbv_joint_cohort_v1/review_v1/`.

**PASS for implementation, arithmetic and the bounded research audit. FAIL for forecast promotion and headline cohort-share precision under the preregistered rules. Current direct corporate cohort measurement is UNAVAILABLE.** The candidate's early-guide RMSE improves in both primary samples, but the advantage reverses after deleting 2024 and its paired uncertainty intervals include no improvement. This is a useful research result, not a new promoted forecast or a reason to describe unobserved physical cohorts as measured.

## Exact accepted versions

- Core: `data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1/`; manifest SHA256 `9867d8c9822132f4f07a057083fd053f1fc3ff96c7cd6fd8cd6b7a4e9cdc44fb`.
- Diagnostics: `data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/diagnostics_v1/`; manifest SHA256 `ff09fd82faed0a3052cb6b0a448e9146fd4d4c010f9d99736eb2126c7f7a8b1d`.
- Core `run.py` SHA256 `6f395b2956762f179701e78f4c6743ba523da55e45cb7c9f742a2151aa2495af`; `diagnostics.py` SHA256 `39c3514848d78453e01424d194d42232b11d1395f079265afca42bfc9d1436e8`.
- Prepared registry accepted for research retention: `control_v1/prepare_v1/prepared_registry/`, 42 rows; preparation receipt SHA256 `022a7e16ab22305f05eedb230b1efe7d0145b4ebcb00b5627e8a453b11df4830`.

These hashes bind the reviewed implementation and outputs. Revisions require another bounded comparison. The quant author's independent full rebuild reproduces all 21 core output files byte-for-byte with six input hashes unchanged; that reproduction receipt is `quant_v1/validation_v1/core_rebuild_receipt.json`.

## Economic meaning and repairs

The model constructs one dollar matrix and reads it in two directions. Its backward share divides a cell by the allocated recognition-quarter total. Its actual-revenue attribution divides the same cell by corporate revenue; the residual is exposed separately. Its forward effective rate divides the cell by that booking quarter's reported GBV. Independent calculations verified all three quantities, their different denominators and their reconciliation. Normalized regression coefficients are not substituted for backward shares.

Reported GBV is a net reporting-period measure containing cancellation/alteration effects from older bookings. It is not the original gross value of a mature reservation cohort. Therefore these are **conditional accounting allocations**, not observed fee cohorts, booking completion probabilities, cancellation rates or RNPL causality. The implementation adds no second generic cancellation haircut. Lags 3 and 4 retain separate original-quarter denominators. `effective_coefficient_sum` for the grouped tail is the sum of rates with different denominators, not a single tail cohort's conversion. Forward summaries identify missing supported lags and left/right censoring; the tail beyond the assumed support remains unobserved.

The original preregistration's same-release timing was corrected before execution in `JOINT_COHORT_QUANT_PREREG_ADDENDUM_v1.md`. Target t now uses the t−2 earnings release as origin and predicts the guide issued at the t−1 release. Both t−1 and t GBV are recursively forecast. After deliberately multiplying all unpublished company GBV/revenue and future guide midpoints, the complete earlier-origin candidate and baseline forecasts were unchanged while the oracle changed. Known GBV remains an effective input in the positive-control test. The oracle cannot qualify for promotion.

PR60 flight admission now uses the actual historical UTC commit timestamp, conservatively requiring it at or before date-only origin UTC midnight. Future same-day commits, incomplete day-count rows, stale rows and later company outcomes fail the adversarial admission tests. This does not certify full state coverage in the absent raw mirror. The source caveat remains explicit. Q3 2026's already-issued guide is labelled an implied-guide diagnostic, not a forecast of an unknown guide.

The guide bridge uses the arithmetic mean of the last eight completed actual/first-guide cushions known at the origin. Candidate and baseline share it. Earlier GE work used a median; the present comparison is internally consistent but should not be represented as the identical earlier protocol.

## Forecast usefulness: favorable points, failed robustness

All figures below use matching actual pre-guide origins. W2 is nested. W1 contains 11 eligible targets, 2023Q4–2026Q2; W2 contains 10, 2024Q1–2026Q2. Three early W1 primary origins lack the minimum complete training history and remain in the skipped-origin file. Monetary errors are USD millions.

| Primary metric | W1, n=11 | W2, n=10 |
|---|---:|---:|
| Candidate guide RMSE | 64.287 | 63.831 |
| Fixed-kernel guide RMSE | 74.592 | 77.012 |
| Guide RMSE ratio | 0.86185 | 0.82884 |
| Candidate / baseline guide MAE | 46.257 / 59.477 | 44.014 / 61.071 |
| Candidate / baseline guide bias | -27.193 / +11.694 | -23.044 / +17.217 |
| Revenue RMSE ratio | 0.73423 | 0.69464 |
| Guide RMSE ratio after deleting 2024 | **1.06375**, n=7 | **1.02984**, n=6 |
| Paired year-bootstrap 90% ratio interval | [0.54269, 1.57425] | [0.60377, 1.12539] |

The roughly 14% / 17% guide RMSE improvement clears the prespecified 10% point threshold and n≥8 rule. It fails the requirement to retain an advantage under every evaluable year/quarter deletion. Deleting 2024Q2 also reverses W1's ratio to 1.02171. All evaluation omissions were retained and independently recomputed; no deletion was selected to optimize the method. The 2,000 paired year-cluster resamples preserve candidate/baseline losses from the same quarter. With only four / three evaluation years, these intervals are conditional and imprecise; neither excludes a ratio of one.

The single PR60 flight ablation has eight eligible targets in each displayed window, **the same eight observations in both**. Guide RMSE is 73.504 with flights, 69.610 for the no-flight candidate on those rows and 67.581 for the original fixed-kernel baseline. The flight version worsens this matched comparison. Stored flight vintages supply a demand feature, not a cohort observation. No additional feature or profitable threshold was searched.

## Cohort precision and variance

The primary pooled shape has seven fitted degrees of freedom: three free exposure weights and four seasonal conversion scales. The guide adds one cushion parameter. The flexible diagnostic has 36 coefficients; its nine coefficients per season face only two to four quarterly observations. It fits multiple materially different matrices, and its fitted bounds are conditional on positivity, fit tolerance and finite lag support. Such a saturated diagnostic alone would not reject the smaller forecasting model; the smaller model has its own precision and forecast tests.

| Precision diagnostic | W1, n=14 retrospective quarters | W2, n=10 retrospective quarters |
|---|---:|---:|
| Retained near-fit shapes | 219 | 103 |
| Maximum near-fit share width | 60.840 pp | 52.254 pp |
| Maximum 90% parameter-bootstrap share width | 75.926 pp | 97.186 pp |
| Maximum year-deletion share shift | 26.578 pp | 50.327 pp |
| Preregistered allowed width / shift | 10 pp / 5 pp | 10 pp / 5 pp |

These fail the precision/stability rule. The maximum within-season standard deviation of the assumed retrospective backward shares is much smaller, 0.789 / 1.077 percentage points. That small time variation is conditional on an imposed shape; it does not resolve the wide range of plausible shapes. Bootstrap fits preserve year clusters, but they are not observations of physical booking survival. K2's older Melbourne accommodation shares remain a separately labelled assumption stress, with local-month and northern-season analogies distinguished and failed truncation recovery retained.

Uncertain composition does not automatically imply equally uncertain total revenue. Across W1 near-fit shapes, the Q4 2026 same-quarter share spans approximately 8.83%–61.72%, while the conditional implied-guide range is $3,147.40M–$3,190.76M. Component changes offset one another. The review independently verified both the within-season dollar covariance and the near-fit-grid contribution covariance, including every off-diagonal term. This guide range holds GBV forecasts and cushion assumptions fixed; it is **model sensitivity, not a predictive interval or an assigned probability distribution**. Missing input, cushion and structural uncertainty must not disappear from a pitch because this conditional range looks narrow.

## Source availability and pitch-use decision

PR60 merge `dd3aa1440b152b46fdee8c094875d178b802d74a` is included in this checkout. Independent source checks corroborate the 23-source audit: no current directly observed booking-date by corporate fee-recognition-dollar ledger with compatible original cohort value and cancellations is available locally. Reviews lack original booking dates; calendar availability transitions mix bookings and blocks; competitor samples are missing or unsuitable; dated flights measure demand. K2 is old reconstructed accommodation value, not current consolidated Airbnb fees. Its adjusted mean lead times, approximately 40.61–43.64 days, failed to recover the 52.31-day reference in its truncation diagnostic.

| Proposed pitch statement | Decision |
|---|---|
| Reported revenue divided by the explicitly defined lagged-GBV denominator, with dates/season/sample | Eligible as an observed aggregate ratio |
| The joint model illustrates one consistent accounting allocation and its sensitivity | Eligible as a clearly conditional research illustration |
| The candidate reduced guide RMSE by about 14% / 17% in the matched historical samples, but failed deletion robustness | Eligible only with the complete qualification and n |
| Current corporate booking-cohort shares or survival/cancellation rates were measured | **UNAVAILABLE**; exclude as an evidentiary claim |
| A precise estimated corporate cohort percentage is stable enough to headline | **FAIL** under the specified precision rule |
| The candidate or PR60 ablation establishes a new promoted forecast or trading edge | **FAIL** for promotion; no stock-return test follows from this package |

Do not suppress the favorable point result, infer that physical cohorts have been empirically disproven, or infer that the forecast is useless solely because its decomposition is unidentified. The evidence supports continued research while leaving the existing adopted model in place.

## Verification suites and exact commands

Counts below are **separate suite counts**, not a grand total. Numerical v2 includes numerical v1; earlier versions are retained and must not be added together. Source/hash checks overlap across suites. Engineering checks are not extra economic observations.

- **24 independent-review tests PASS:** 13 economic-contract examples plus 11 attacks on the actual core/diagnostic functions. Receipt: `review_v1/adversarial_v3.xml`. The author's separate 11 tests are not added to this count.
- **143 source checks PASS:** local hashes, field/schema and date arithmetic; `review_v1/source_v1/receipt.json`.
- **2,128 saved-output checks PASS:** independent financial-source/matrix arithmetic, covariance, near-fit bounds, LP witnesses, per-origin forecast levels/timing, matching actuals, all score/deletion rows and supplementary matrix/censoring identities; `review_v1/numerical_v2/receipt.json`.
- **317 additional diagnostic checks PASS:** parameter intervals, paired bootstrap arithmetic, UTC flight training/feature selection/slopes/scores, and conditional future inputs; `review_v1/diagnostics_v1/receipt.json`.
- **260 prepared-registry checks PASS:** 42 rows, source hashes, dates, horizon, seven revenue/eight guide parameters, training counts, matching points, q50 placeholders and absent predictive bands; `review_v1/stage_v1/receipt.json`.

Saved-output/source replays import no candidate calculation functions. Actual-code adversarial tests necessarily call the candidate. Initial reviewer test v1 failed because it required exact equality of 2.0000000000000004 and 2.0; the failure is preserved in `review_v1/ATTEMPT_v1.json`. Replacing that assertion with a tight floating-point comparison required no model change. All final commands exited zero:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/test_economic_contract.py analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/test_quant_adversarial.py -q -p no:cacheprovider --junitxml=data/processed/forecast_methods/gbv_joint_cohort_v1/review_v1/adversarial_v3.xml
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/source_checks.py --out data/processed/forecast_methods/gbv_joint_cohort_v1/review_v1/source_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/audit_outputs.py --core data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1 --diagnostics data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/diagnostics_v1 --out data/processed/forecast_methods/gbv_joint_cohort_v1/review_v1/numerical_v2
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/diagnostic_checks.py --core data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1 --diagnostics data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/diagnostics_v1 --out data/processed/forecast_methods/gbv_joint_cohort_v1/review_v1/diagnostics_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/stage_checks.py --stage data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/prepare_v1 --out data/processed/forecast_methods/gbv_joint_cohort_v1/review_v1/stage_v1
```

Use fresh output names for another replay; existing output directories are refused. The final audit code and exact accepted objects are also bound by `review_v1/closure_v1.json`.

## Registry/scorer boundary

The reviewer accepted the parent's 42 prepared rows for retention of this research candidate; q50 equals the point only to satisfy format and is explicitly a placeholder, with no calibrated intervals. Parent owns registration and scorer execution. The frozen scorer keys its baseline map without vintage/horizon, so its baseline ratio is not the matching-origin promotion test. Use the independent local race above for that decision. No frozen scorer was changed. Parent reports both unchanged scorer versions agree on 292 post-registration rows, with all 288 pre-existing scores and 122 protected original files unchanged; its authoritative receipt is `control_v1/after_v1/receipt.json`.

## RESUME

GE-JOINT-REVIEW is complete. The parent can deliver the joint-model visual explanation, quantified variance and forecast comparison with these separate verdicts. Retain the favorable point result and failed robustness side by side, keep conditional composition distinct from physical measurement, and limit future examples to Q3 2026–Q2 2027. No extra method search is required for this delivery. A later cohort headline needs compatible direct data or a new preregistered identification result; a later forecast promotion needs fresh, robust common-origin evidence. The present review found no remaining implementation defect in the accepted versions.
