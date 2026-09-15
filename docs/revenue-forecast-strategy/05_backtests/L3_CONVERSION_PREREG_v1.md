# L3 conversion validation v1 — preregistration

2026-09-13 · `adr_hotel` · `codex/lane3-full`; claimed in `WORKBOARD_L3_v2.md`. Saved before fitting or evaluating new models. The user explicitly requests all 22 lag-complete quarters, 2021Q1–2026Q2, four seasonal conversion rates and one shared lag weight.

## Model and estimation, locked

`R_t = lambda_season(t) × [w GBV_(t−1) + (1−w) GBV_(t−2)]`, with one scalar `w ∈ [0,1]`, four positive through-origin seasonal coefficients and no intercept. Both R and GBV are USD millions. The coefficient is a reduced-form seasonal conversion ratio, not a fee take rate or probability. No current-quarter GBV enters this model. No RNPL, FX or fee overlay is fitted here.

Primary loss is USD-level sum of squared revenue errors. At each w, `lambda_s = Σ(x_t R_t)/Σ(x_t²)` within season s. Search a 201-point profile grid on [0,1], refine each interior local minimum with bounded scalar minimization (x tolerance 1e-10), and include both boundaries; choose minimum loss with deterministic tie-breaking by ascending w. Compare to w=2/3 with the **identical** analytical seasonal fit. Full22 estimates are descriptive calibration. Four lambda values plus the one common w are five estimated parameters; the matched fixed-weight fit has four estimated parameters.

Sensitivity loss is squared relative error `(predicted/actual−1)²`, using its analytic profile coefficients `Σ(x/R)/Σ((x/R)²)`. It is reported separately, never substituted after examining which loss wins. Also show ex-2021 (2022Q1+, n=18) and 2023Q1+ (n=14), with both losses and both fixed/free rules; these are estimation-regime sensitivities, not replacements for the user-requested full22 primary.

## Chronological validation, locked

Use the frozen KPI panel/calendar and L2 guide-date convention: at the close of the same-day letter, the just-printed prior quarter's revenue/GBV is known; the target quarter's outcome is not. Rebuild training rows after truncating source observations by print date, use targets from 2023Q1–2026Q2 (W1 n=14) and 2024Q1–2026Q2 (W2 n=10), and require at least eight lag-complete training observations and two per season. Explicitly refuse undated, future or duplicate supplied observations and unavailable lag inputs. No full-sample coefficient enters historical predictions. Record every training quarter, source dates, w and all four lambda values for every origin.

Primary promotion hurdle: free-w USD-level RMSE must be lower than identically fitted fixed-w RMSE on **both** matched windows. Report absolute and relative improvements, paired squared/absolute-error changes and per-date errors. A strict numerical pass with tiny or unstable improvement is qualified; no automatically adopted production specification follows. If it fails, retain the existing fixed operational benchmark, not a newly fitted all22 fixed-OLS substitute. The audited full22 fit can remain an accepted descriptive calibration regardless of prospective promotion outcome.

Compare frozen operational fixed kernel registry methods (published season-mean and last3 excluding 2021), plus the completed K0 v2 dynamically selected fixed-weight engine using its documented `as_of=guide_date+1 day` wrapper; record that wrapper and same-day maximum input date. Compare frozen harness naive, AR(1), and guide+cushion rows only on identical target/vintage/window/PIT cells. Guide+cushion uses management's already-issued target guide; it is an explicitly advantaged post-guide revenue benchmark, not a test of anticipating that guide. Legacy parameter counts or loss conventions are not silently reinterpreted.

## Uncertainty and robustness, locked

- Full-sample parameter sensitivity: 1,000 seeded (`20260913`) resamples of the six observed calendar-year blocks, sampled with replacement preserving each year's quarterly rows, re-fit the model, and reject draws with fewer than two observations in any season. Report attempted/accepted draws, n, percentile 2.5/50/97.5 for w and each lambda, and endpoint frequency. Six blocks, including a partial 2026 block, do not justify precise asymptotic confidence or structural identification claims.
- Leave each of the six years out, re-estimate full-sample fixed/free USD loss, and report w/lambdas/error on held-out year. This is sensitivity, not chronology-preserving validation. Report the original/exclusion profiles and the descriptive w range within 5% of minimum RMSE as a flatness diagnostic, not a confidence interval.
- For the paired chronological errors, draw 2,000 calendar-year-block resamples of the matched target-year blocks separately per W1/W2 with seed 20260913. Report percentile intervals for the free/fixed RMSE ratio and MSE delta. W1 has four target-year blocks; W2 has three. These overlapping windows and few blocks are not independent confirmations or reliable precise p-values.
- Chronological interval diagnostic: after at least six previously observed out-of-sample errors, use the last at most eight absolute relative errors, conservative order statistic `ceil((m+1)*0.8)`, and symmetric relative bands around the current point. Publish eligible n, empirical coverage and width. No exchangeability/80% guarantee is asserted; before six errors, bounds remain missing. This tests practical calibration without using future residuals.

## Integrity, presentation and delivery

Reconcile exactly 22 unique rows to the KPI panel/targets/calendar and both GBV lags. Require positive finite observations and explicit units, fixed-boundary/constant-coefficient arithmetic tests, duplicate/season-coverage guards, GBV and future-outcome leakage tests, deterministic numerical output and preservation of all frozen source hashes. Immutable `--out` only; existing outputs are refused.

Deliver profile/parameter tables, full-sample fitted values, chronological predictions/scores/intervals, sensitivity draws and leave-year-out rows, PNG and SVG presentation charts, a claim ledger with allowed/forbidden wording, and a versioned JSON specification plus L4 rows. The JSON separates accepted validation protocol, descriptive parameters, prospective evidence, production benchmark retention and pending L4 adoption. In-sample R², w as measured booking probability/share, and “all revenue already booked” are forbidden claims. No model/card/registry, workbook, memo, valuation or investment-direction edit occurs.

## RESUME

Implement and run the new `conversion_validation_v1` package, publish all failures, and ask the lead to independently audit chronology, coefficient/profile arithmetic, plots and schema. Do not overwrite prior L3 research; the bundle may add this specification only from its reviewed commit.
