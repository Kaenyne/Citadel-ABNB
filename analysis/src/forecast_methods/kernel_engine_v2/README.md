# K0 kernel engine v1

**Gate 1 passed on 2026-09-12:** 12/12 identities; 63 module tests; 47 frozen harness/L0 tests; CLI exit 0 in 5.38 seconds. V1 remains a preserved failed checkpoint. Use this v2 module.

From the repository root, using its `.venv` interpreter:

```text
python -m pytest analysis/src/forecast_methods/kernel_engine_v2/tests -q
python analysis/src/forecast_methods/kernel_engine_v2/run.py --as-of 2026-09-12
```

New outputs only: `data/processed/forecast_methods/kernel_engine_v2/`. No registrations or frozen files are written.

## Public interface

Import `kernel_engine_v2.engine` with `analysis/src/forecast_methods` on `sys.path`. Currency outputs are **USD millions**; lambda is in **percent**.

- `pit_lambda(season, as_of, variant=None)` returns lambda, training quarters, sample size and publication cutoff.
- `kernel_forecast(q, as_of)` returns a revenue `point`, quantiles and provenance. Both lagged GBVs must have printed strictly before the origin.
- `kernel_guide(q, as_of, cushion='median')` divides by the median or mean of the last eight realised actual/guide-mid ratios. Adds cushion dispersion and reports chronological conformal-lite calibration counts.
- `term_structure(as_of)` reports three quarters after the last printed quarter. Missing GBV inputs are conditional scenarios. At 12 September these are Q3 2026, Q4 2026 and Q1 2027.
- `control_chart(as_of)` returns current seasonal limits, chronological historical alarms and the dated November monitoring rule.
- `lambda_table(as_of)` returns historical accounting identities, not forecasts.

All six accept `panel=`, `regional_gbv=` and `regional_lambdas=`. Supplied panel data must already be truncated and carry publication dates; contaminated or undated input is refused rather than silently filtered. Repository loading filters full histories before calling the same validators. Dates are normalised: an intraday timestamp cannot circumvent a date-only same-day refusal.

## Regional contract for X

`regional_gbv`: `quarter`, `region`, `gbv_usd_booking_dated` in **USD**, optional `print_date` (otherwise joined from the frozen calendar). `regional_lambdas`: `region`, integer `season` 1–4, `lambda_pct`, `print_date`, optional `lambda_sd_pct`. Coefficients must be dated before `as_of`. There is one coefficient per region-season; X chooses its admissible vintage and estimates it. Missing regions or coefficients are errors.

Revenue and guide **dollars** are summed across regions. Coefficients and control-chart limits are not additive; `pit_lambda` returns the regional parameters and no meaningless sum of percentages. Regional uncertainty is unavailable without dispersion inputs; when supplied, a perfectly positively correlated Gaussian sensitivity avoids an unsupported diversification assumption. X owns richer joint uncertainty. Regional future GBV forecasting remains X's responsibility; K0's term-structure interface labels unavailable regional horizons explicitly.

## Pre-registered default-selection policy

Weight fixed at 2/3 on the first GBV lag and 1/3 on the second. Candidate lambda variants: ex-COVID same-season mean (`|nights y/y|<=25`, missing growth excluded), last three same-season observations, exponential mean with a fixed half-life of two same-season observations. Live selection uses the lowest relative revenue LOO RMSE on common W1 cells; ties follow the listed order. Historical calls rerun selection strictly within their own information set, with an ex-COVID fallback below eight common LOO cells. No future-selected variant is inserted into a historical replay.

The full-W1 LOO table is a **retrospective specification diagnostic**, not an out-of-sample alpha claim. The frozen live default is **ewm** (half-life two same-season observations). The policy is frozen now.

```text
 variant window  n  rmse_pct                       basis
ex_covid     W1 14  1.829421 retrospective_LOO_selection
ex_covid     W2 10  2.067514 retrospective_LOO_selection
   last3     W1 14  1.829421 retrospective_LOO_selection
   last3     W2 10  2.067514 retrospective_LOO_selection
     ewm     W1 14  1.804318 retrospective_LOO_selection
     ewm     W2 10  2.020128 retrospective_LOO_selection
```

## Limits and interpretation

The prior quarter's GBV is published in the same letter as its successor quarter's guide. A strict pre-guide call therefore refuses the unavailable lag. Post-letter predictions can be formed on the next calendar day, and are labelled post-letter. They are not evidence of anticipating the guide.

The K1 RNPL correction is refitted from raw printed KPI data, using the explicit scenario ramp in the existing K1 source (available 11 September 2026). Those ramp values are **research assumptions, not disclosures**. Historical origins before that scenario's availability abstain on missing GBV. Live Q1 2027 requires a second missing GBV: its growth is persisted from the first ledger nowcast and its uncertainty widened. Both are conditional scenarios, not validated PIT forecast results. The script does not adopt a team direction, fee step, FX step, RNPL share or target-price decision.

Bootstrap blocks are two adjacent same-season years. Predictive residual and estimation uncertainty are combined, then guide-cushion dispersion is added. Samples are small. Conformal-lite uses at most six chronological post-letter residuals, reports `n_cal`, returns unavailable bounds when the finite-sample rank is unattainable, and makes no exchangeability or coverage guarantee. Sparse regional histories likewise do not justify precise intervals.

## Verified outputs and limits

Q3 revenue/guide: 4808.363/4723.784 USD millions. Conditional Q4: 3214.776/3158.228; conditional Q1 2027: 3121.423/3066.517. These are model outputs, not adopted investment targets. Historical control chart alarms: 1/6 eligible cells on both W1 and W2; these overlapping cells do not establish stability. Pre-guide printed-lag availability is 0/14 W1 and 0/10 W2. Regional conformal bounds require X residuals and are explicitly unavailable. Guidance intervals now include cushion dispersion; full historical calibration applies the requested mean or median at each origin. Two-decimal displays are calculated from full precision; published three-decimal references are compared to their rounding interval.
