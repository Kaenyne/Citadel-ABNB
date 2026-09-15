# L3 conversion validation — 22-quarter calibration and chronological test

2026-09-13 · `adr_hotel` · `codex/lane3-full`. Preregistered in `L3_CONVERSION_PREREG_v1.md` before fitting. Canonical presentation output is `data/processed/forecast_methods/conversion_validation_v1/results_v2`; initial `results_v1` is preserved. Source is `analysis/src/forecast_methods/conversion_validation_v1/`. The independent acceptance receipt, when closed, binds the final specification and review by SHA-256; analytical acceptance does not authorize investment or operational adoption.

## Decision

The requested full-history model is an auditable descriptive calibration: **four seasonal conversion rates and one shared first-lag coefficient, estimated jointly on all 22 quarters from 2021Q1 through 2026Q2**. Its extra lag parameter **fails** the preregistered forecasting hurdle in both chronological windows. Retain the existing fixed 2/3 operational benchmark. Do not substitute the newly estimated all22 fixed-OLS seasonal coefficients into production either.

| Primary USD-level comparison | W1: 2023Q1–2026Q2, n=14 | W2: 2024Q1–2026Q2, n=10 |
|---|---:|---:|
| Free shared w RMSE, USD million | 63.1971 | 57.3924 |
| Identically fitted fixed 2/3 RMSE, USD million | 54.2275 | 56.5157 |
| Free / fixed RMSE | **1.1654** | **1.0155** |
| Free w MAE, USD million | 48.3807 | 41.4143 |
| Fixed 2/3 MAE, USD million | 41.7834 | 42.2487 |
| Free w signed bias, USD million | +12.5342 | +17.0884 |
| Fixed 2/3 signed bias, USD million | +28.0367 | +26.2252 |
| Free w relative RMSE, % of actual | 2.3947 | 2.2969 |
| Fixed 2/3 relative RMSE, % of actual | 2.2229 | 2.2357 |
| Strict preregistered promotion result | FAIL | FAIL |

The modest W2 MAE improvement is retained in the table; it does not replace the preregistered USD-level RMSE criterion. W2 is a subset of W1, not an independent replication.

## Specification and descriptive calibration

`R_t = lambda_season(t) × [w × GBV_(t−1) + (1−w) × GBV_(t−2)]`.

Revenue and GBV are USD millions. There is no intercept, current-quarter GBV, fitted FX term, fee overlay or RNPL term. For each candidate w, the seasonal through-origin OLS coefficient is `Σ(xR)/Σ(x²)`. A 201-point profile on [0,1] is refined at all interior local minima, with both endpoints retained. The fixed model uses exactly the same seasonal estimation rule at w=2/3. Free/fixed models estimate five/four parameters respectively. Optimization details are deterministic and independently testable; low in-sample error is not evidence of prospective edge.

| All22 primary USD OLS parameter | Estimate | Year-block 2.5–97.5% sensitivity |
|---|---:|---:|
| Shared first-lag coefficient w | **0.78647848** | 0.30791–0.85733 |
| Q1 conversion coefficient, percent | **12.931911%** | 12.012842–13.339723% |
| Q2 conversion coefficient, percent | **13.224232%** | 12.879306–15.629557% |
| Q3 conversion coefficient, percent | **17.302744%** | 16.835001–17.470947% |
| Q4 conversion coefficient, percent | **12.111558%** | 11.872228–12.311378% |

The fullsample free/fixed RMSE is $44.7208m/$48.5646m; relative RMSE is 2.7273%/2.8261%. These are fit statistics over the same observations used to estimate the coefficients. The extra degree of freedom must improve training SSE, so the chronological comparison carries the decision weight. Seasonal coefficients are ratios to weighted lagged GBV, not Airbnb commission take rates; w is neither a measured booking-to-stay probability nor a measured revenue contribution share. In particular, the contemporaneous accounting identity GBV × take rate is a different object.

The underlying frozen KPI panel has 24 rows beginning 2020Q3; exactly 22 have both lagged GBVs. `dataset_22.csv` reconciles every lag to the same panel and every revenue/current GBV to the frozen targets. Publication dates and any approximate historical date basis are carried from the existing calendar rather than silently promoted to exact timestamps.

## Information set and comparators

Every guide-date prediction rebuilds its training lags after truncating observations to print dates no later than that origin. The L2 convention admits the same-day prior-quarter letter at its close. The target outcome and target GBV are excluded; training n grows from 8 to 21 with at least two observations in every season. `chronological_paths.csv` stores all training quarters, source dates, lag values, fitted w and all four rates per origin. Poisoning unavailable future revenue or GBV cannot affect the forecast. This is historical information-set reconstruction using frozen public values, not a claim to have recovered original unrevised vendor vintages.

Frozen registry comparisons require target `revenue_musd`, PIT basis, identical quarter and guide date. Native W2 rows independently reconcile to the W1 subset. The table reports USD-million revenue RMSE. Only the last3 fixed comparator, with full14/10 coverage, appears beside the matched models in the presentation chart.

| Comparator | W1 n | W1 RMSE | W2 n | W2 RMSE |
|---|---:|---:|---:|---:|
| Existing fixed season-mean registry method | 14 | 78.1269 | 10 | 78.8214 |
| Existing fixed last3 excluding 2021 registry method | 14 | 52.2074 | 10 | 51.1886 |
| Harness naive | 14 | 94.0308 | 10 | 108.4278 |
| Harness AR(1) | 14 | 103.5419 | 10 | 109.4438 |
| Guide + cushion, explicitly advantaged post-guide | 14 | 35.4565 | 10 | 34.5963 |
| K0 v2 fixed operational policy, available cells only | **12** | **48.6641** | 10 | 52.6901 |

K0's default policy abstains in 2023Q1 and 2023Q2 because its eligible historical same-season training rule is not satisfied. Both abstentions remain in the path table; no fallback is inserted. Its W1 RMSE must not be visually ranked against full14-cell scores. On the K0's own 12 available W1 cells, its RMSE ratios to the matched fixed OLS and naive are 0.86677 and 0.48533; on W2's 10 cells they are 0.93231 and 0.48595. The existing K0 API is called with its documented guide-date+1-day wrapper, and its actual maximum input date is checked to remain no later than the guide date. The wrapper does not admit a future input.

Guide + cushion already knows management's target-quarter guide. It is an advantaged post-guide revenue benchmark, not evidence that this kernel anticipates the guide or produces guide-surprise alpha. Legacy methods keep their original seasonal estimation rules and parameter counts rather than being mislabeled as matched OLS.

## Sensitivity and identification limits

All 22 observations remain the requested primary fit, including 2021. The two predeclared exclusion regimes demonstrate that the shared lag is sensitive to the estimation period.

| Sample / loss | n | Fitted w | Free USD RMSE | Fixed USD RMSE | w grid range within 5% of optimum loss-RMSE |
|---|---:|---:|---:|---:|---:|
| All22 / USD | 22 | 0.78648 | 44.7208 | 48.5646 | 0.700–0.875 |
| Exclude 2021 / USD | 18 | 0.53873 | 33.6996 | 34.8728 | 0.390–0.690 |
| 2023 onward / USD | 14 | 0.35696 | 28.1489 | 33.5078 | 0.220–0.505 |
| All22 / relative error | 22 | 0.76163 | 48.3772 | 52.4684 | 0.660–0.865 |
| Exclude 2021 / relative error | 18 | 0.68487 | 35.7959 | 35.4685 | 0.525–0.845 |
| 2023 onward / relative error | 14 | 0.31264 | 28.3648 | 33.6888 | 0.165–0.475 |

The relative loss uses `Σ(predicted/actual−1)²` and analytical seasonal coefficients `Σ(x/R)/Σ((x/R)²)`. Its chronological free/fixed USD RMSE is 71.4509/73.1890 (W1) and 69.9714/74.0202 (W2): a different loss can make the free/fixed comparison look better, while both models are worse in USD RMSE than the primary USD fits. This predeclared sensitivity is reported without switching the primary loss or promoting an alternative after seeing its result. Profile ranges use the .005 grid and are descriptive flatness diagnostics, not confidence intervals.

The parameter resampling accepted all 1,000 of 1,000 seeded draws, with no season-coverage rejections and 0.1% endpoint estimates. It resamples six calendar-year blocks, one of them partial 2026. The weight's 2.5/50/97.5 percentiles are 0.30791/0.78921/0.85733. These are finite-sample block sensitivity ranges, not precise structural confidence intervals; the number of independent regimes is small.

| Held-out year, descriptive LOYO | Training n / test n | Refit free w | Free held-year RMSE | Fixed held-year RMSE |
|---|---:|---:|---:|---:|
| 2021 | 18 / 4 | 0.53873 | 123.5551 | 89.1762 |
| 2022 | 18 / 4 | 0.78191 | 44.4583 | 47.1149 |
| 2023 | 18 / 4 | 0.80551 | 34.9243 | 22.4838 |
| 2024 | 18 / 4 | 0.80278 | 59.2634 | 55.7006 |
| 2025 | 18 / 4 | 0.80198 | 59.3978 | 54.2775 |
| 2026, partial | 20 / 2 | 0.78961 | 30.6324 | 27.0002 |

Only the 2022 held-out comparison favors free w. Leave-year-out fits use years after the held-out year and therefore are sensitivity checks, not point-in-time predictions.

The paired chronological error bootstrap uses 2,000 year-block draws for each window. W1 has four target-year blocks and a free/fixed RMSE ratio sensitivity range of 0.84834–1.52512; W2 has three and a range of 0.80688–1.13594. Their mean-squared-error delta ranges are −634.71 to +2,877.98 and −1,057.90 to +1,201.73 USD-million squared. Both spans include no difference. The strict point-estimate hurdle fails, while the small block count prevents strong claims that the structural lag is precisely identified or that one model dominates in all regimes.

Sequential nominal80% bands use only previously printed out-of-sample errors, with six required and at most eight retained. The calibration error denominator is the forecast, matching symmetric bands `point × (1±width)`. Both primary models cover 7/8 eligible outcomes; mean full width is 9.7381% of forecast for free w and 9.1055% for fixed. The same eight eligible quarters appear in both overlapping windows. Coverage is descriptive; eight cases and a dependent time series provide no 80% coverage guarantee. Missing early bounds remain missing.

## Delivery, reproduction and failures retained

Source command from the worktree root, using the repository virtual environment:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/conversion_validation_v1/test_conversion.py -q -p no:cacheprovider
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/conversion_validation_v1/run.py --out data/processed/forecast_methods/conversion_validation_v1/results_NEW_VERSION
```

Every destination must be new. Do not rerun against results_v1 or results_v2. The completed initial run exited0 in29.038s; the repaired package's 21 focused tests pass. The final closure note records the rebuilt file-by-file comparison, source preservation and independent review receipt. No frozen source, registry or workbook is written.

The runner emits 24 files: reconciled22-row data, parameter/fitted/profile/flatness tables, 1,000 parameter draws, 12 LOYO rows, 140 chronological model-origin rows including two K0 abstentions, 20 model-window scores, paired errors/4,000 paired bootstrap rows, uncertainty summaries, ten-source hash manifest, summary/spec JSON, claim ledger, seven L4 rows, and three figures in PNG/SVG. Final acceptance evidence is a separately added immutable receipt. L4 rows separate coefficient levels from PIT validation ratios, state reported-USD embedded FX, state the candidate joint baseline replacement, and prohibit applying descriptive parameters as production replacements. Null bounds mean unavailable.

Figure01 shows the 22-quarter seasonal fit and conversion levels; figure02 shows weight sensitivity and leave-year-out estimates; figure03 compares only matched-coverage methods. All images are 3200×1800 PNG plus editable SVG and were visually inspected. The claim ledger permits quantitative descriptive/validation statements and forbids probability/take-rate, in-sample R² edge, all-future-revenue-booked and automatic adoption claims.

`L3_CONVERSION_AUDIT_REPAIR_v1.md` preserves the initial K0-abstention exception, interval normalization defect caught before completed outputs, module-import collision under joint tests, and unequal-coverage chart presentation finding. None changes the primary point forecasts or the failed promotion conclusion. Independent analytical review is performed separately from this implementation note.

## RESUME

Use the final `results_v2` directory plus its acceptance receipt and independently closed review note when assembling L4. Verify the receipt's specification/review hashes, preserve the exact five-parameter descriptive fit and failed W1/W2 promotion decision, and keep the existing operational fixed benchmark. Apply no joint parameter replacement or FX/fee addition without a separately reviewed L4/team decision. Source scripts reproduce into a new directory only; the final closure note contains the reproduction and audit evidence.
