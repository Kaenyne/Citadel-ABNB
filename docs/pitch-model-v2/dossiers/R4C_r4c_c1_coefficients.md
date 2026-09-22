# R4C — C1 guide-conversion coefficients (seasonal intercepts, GBV beta, 0.4/0.4/0.2 weights)

## 1. Header
- Line: R4C · Judge's question: "You map bookings straight to the guide with a five-parameter log fit on nineteen observations. Why should I believe those coefficients, and what did they get wrong out of sample?"
- Digger: opus · Date: 2026-09-18 · Commit: `b098ac2` (main clone, `theo/pitch-model-v2`)

> **Two checkouts.** The R4C object does **not** live on `theo/pitch-model-v2`. The package
> `gbv_guidance_inference_v1`, its outputs, and every note cited below live in the worktree
> `/Users/theomachado/Citadel-ABNB-untracked` on branch `theo/local-untracked-2026-09-15`,
> commit `d984b14`. The reproduction receipt carries `d984b14`; the dossier and the receipt folder
> are written into the main clone at `b098ac2`. The GBV path used for the 4Q26 application comes
> from the **main clone** (`airbnb_quarterly_kpis.csv`, `h2_bridge_v3/`).

**One-paragraph answer.** You should believe the *arithmetic* completely and the *claim* narrowly.
The five coefficients reproduce to 1.4e−14 from a fresh refit and again from my own independent
statsmodels fit off the raw guide/GBV cells, so nothing here is a transcription. What they are is a
**conditional in-sample map**, not a forecast: C1 regresses the issued guide on a weighted GBV
driver that includes the *target quarter's own* actual GBV — a number Airbnb had not published when
that guide was issued. On 19 observations that fit is almost perfect (adj. R² 0.9988, HAC3 beta
1.0433 [1.0091, 1.0774], Holm-adjusted p 4.8e−18) and the elasticity is statistically
indistinguishable from a clean 1.0, which is the honest reading: **guidance scales one-for-one with
weighted bookings, and the four seasonal intercepts do the rest of the work.** Out of sample it
loses. When the identical equation is refit one day before each historical guide and fed a
feasible GBV projection, its next-guide RMSE is **$65.93M against $50.52M for the existing 50/50
blend and $63.51M for a one-line guide-growth baseline** on the same nine quarters — worse than
both, on RMSE and on MAE. And the W1/W2 requirement cannot even be exercised: adequate training
only begins in 2024, so C1's "W1" and "W2" rolling rows are **byte-identical** (the same 9/8/7
target quarters), i.e. one window printed twice. Quote C1 as the transparent operating-scenario
translator it is, never as a validated advance forecaster.

## 2. The number

Scenario **base** for every row; the coefficients do not vary by scenario or period, so their period
is **all**. `low`/`high` on coefficient rows are the **HAC3 nominal pointwise 95%** intervals
(the protocol's primary covariance); the OLS alternative is in the note under the table and is
Open Choice 1 in §8. `w0/w1/w2` are **fixed, not estimated** — they were inherited as a declared
predictive convention and carry no interval.

| item | scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|---|
| season_Q1 (log intercept) | base | all | **6.9473876951** | 6.9278640 | 6.9669114 | log | coefficients as of 2026-09-16; 19 guides 2021Q4–2026Q2; GBV through 2Q26 (printed 2026-08-06) |
| season_Q2 (log intercept) | base | all | **7.1507485411** | 7.1224813 | 7.1790158 | log | same |
| season_Q3 (log intercept) | base | all | **7.4320468510** | 7.4107985 | 7.4532952 | log | same |
| season_Q4 (log intercept) | base | all | **7.0898192281** | 7.0750944 | 7.1045440 | log | same |
| gbv_beta (GBV elasticity of the guide) | base | all | **1.0432632149** | 1.0091337 | 1.0773924 | elasticity | same |
| w0 — weight on GBV of the target quarter | base | all | **0.4** | — | — | weight | inherited convention, frozen before fitting |
| w1 — weight on GBV[q−1] | base | all | **0.4** | — | — | weight | same |
| w2 — weight on GBV[q−2] | base | all | **0.2** | — | — | weight | same |
| **C1 implied guide at bridge-v3 GBV** | base | 4Q26 | **3,126.51** | 3,056.72 | 3,197.90 | musd | GBV 2Q26 printed 2026-08-06; 3Q26/4Q26 bridge v3 base (built 2026-09-12, FRED through 2026-09-04); coefficients 2026-09-16 |

Notes that must travel with the table:

- **The intercepts are log dollars, not multipliers.** `exp(season)` is the usable form:
  **Q1 1,040.4283 · Q2 1,275.0600 · Q3 1,689.2617 · Q4 1,199.6909** ($M at X = $10,000M).
  Full equation, X and guide both in USD millions:
  `guide_q = exp(season_q) × (X_q / 10000) ^ 1.0432632149063203`, with
  `X_q = 0.4·GBV_q + 0.4·GBV_{q−1} + 0.2·GBV_{q−2}`.
- **OLS intervals are tighter than HAC3 on beta and on three of four intercepts.** OLS 95%:
  beta [1.0156968, 1.0708297]; Q1 [6.9276699, 6.9671055]; Q2 [7.1285560, 7.1729411];
  Q3 [7.4101969, 7.4538968]; Q4 [7.0725201, 7.1071184]. HAC3 is *wider* on beta (0.0682 vs 0.0551)
  and on Q2, and *narrower* on Q1, Q3 and Q4 — so "HAC is the conservative choice" is only true for
  the elasticity. See §8.1.
- **The 4Q26 low/high are coefficient uncertainty only.** They propagate the estimated
  coefficients' HAC3 covariance at that X and nothing else: no GBV uncertainty, no residual
  variance, no smearing correction. The package states in three places that **no calibrated
  predictive interval was frozen**, so this is not an 80/95% forecast band and must not be printed
  as one. On OLS covariance the same band is [3,080.66, 3,173.05].
- **Beta is not distinguishable from 1.** Both intervals straddle 1.0, W2's point estimate is
  0.9962, and the package's own README warns against the "elasticity exceeds one" claim. Say
  "roughly one-for-one", never "guidance is super-elastic to bookings".
- **Exponentiating a log fit gives a geometric centre** — a median only under symmetric log errors,
  not a conditional mean.

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| season_q1_log | base | all | 6.9473876951229796 | log | C1 canonical/full log intercept, Q1 |
| season_q2_log | base | all | 7.1507485411437006 | log | C1 canonical/full log intercept, Q2 |
| season_q3_log | base | all | 7.4320468510260342 | log | C1 canonical/full log intercept, Q3 |
| season_q4_log | base | all | 7.0898192281226526 | log | C1 canonical/full log intercept, Q4 |
| gbv_beta | base | all | 1.0432632149063203 | elasticity | GBV elasticity of the guide; indistinguishable from 1.0 |
| gbv_beta_hac_low | base | all | 1.0091344843257835 | elasticity | HAC3 nominal pointwise 95% lower bound |
| gbv_beta_hac_high | base | all | 1.0773919454868572 | elasticity | HAC3 nominal pointwise 95% upper bound |
| w0 | base | all | 0.4 | weight | weight on GBV of the target quarter; fixed convention, not fitted |
| w1 | base | all | 0.4 | weight | weight on GBV[q-1]; fixed convention, not fitted |
| w2 | base | all | 0.2 | weight | weight on GBV[q-2]; fixed convention, not fitted |
| c1_guide_musd | base | 4Q26 | 3126.51 | musd | at bridge-v3 GBV: 2Q26 27200 printed, 3Q26 26027.96, 4Q26 22987.26 |

### 2b. Inputs behind the 4Q26 row

| item | value | unit | source (main clone) |
|---|---|---|---|
| GBV 2Q26 (printed) | 27,200 | musd | `data/processed/airbnb_quarterly_kpis.csv`, row 2026Q2, `gbv_usd_b` = 27.2 |
| GBV 3Q26 (bridge v3, base) | 26,027.962983 | musd | `data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv`, row 4Q26, `gbv_3q26_assumed_busd` |
| GBV 4Q26 (bridge v3, base) | 22,987.263456 | musd | `data/processed/h2_bridge_v3/h2_bridge_v3_card_check.csv`, row 4Q26 "GBV, $bn", col `bridge` |
| driver X_4Q26 = 0.4·22,987.263456 + 0.4·26,027.962983 + 0.2·27,200 | 25,046.0905756 | musd | computed by `forecast.py` |
| C1 implied 4Q26 guide | 3,126.5119091765 | musd | `forecast.py --target-quarter 2026Q4` |

Both bridge GBV figures are the base ("adjusted") case: 3Q26 GBV y/y +13.659227% on a $22.9bn base,
4Q26 GBV y/y +12.682664% on a $20.4bn base (`h2_bridge_2026_projection.csv`, `gbv_yoy_reported_pct`,
columns `q3_adjusted` / `q4_adjusted`).

## 3. Derivation chain

1. Guides and GBV → `data/processed/forecast_methods/current_quarter_w2_v1/results_v1/source_panel.csv`
   and `data/processed/forecast_methods/harness/targets.csv` (19 numeric guide midpoints,
   2021Q4 g=1,435 issued 2021-11-04 … 2026Q2 g=3,570 issued 2026-05-07; the 2026Q3 guide of 4,730 is
   **excluded** because its own-quarter GBV is not yet published) →
2. `…/gbv_guidance_inference_v1/conditional/results_v1/prepared_mature_rows.csv`
   (`driver_musd` = 0.4/0.4/0.2 weighted GBV; `log_x` = ln(driver/10000); `log_guide` = ln(guide_mid)) →
3. `analysis/src/forecast_methods/gbv_guidance_inference_v1/conditional/run.py`
   (+ `model.py`; OLS on 4 season dummies + log_x, then
   `get_robustcov_results(cov_type="HAC", maxlags=3, kernel="bartlett", use_correction=True, use_t=True)`) →
4. `…/conditional/results_v1/coefficients.csv`, rows
   `input_variant=canonical, window=full, model=C1`, column `estimate` for terms
   `season_Q1…season_Q4, gbv_beta`; statistics in `model_statistics.csv` /`primary_claims.csv`;
   stability in `leave_one_year_out.csv`; diagnostics in `diagnostics.csv` →
5. `analysis/src/forecast_methods/gbv_guidance_inference_v1/forecast.py` reads those same rows
   (`covariance=HAC3`, which carries the identical point estimates) and applies them to a supplied
   GBV path → the 4Q26 row in §2.
6. Out-of-sample record: `analysis/src/forecast_methods/gbv_guidance_charts_v1/run.py` →
   `data/processed/forecast_methods/gbv_guidance_charts_v1/results_v1/c1_rolling_forecasts.csv`,
   `c1_matched_scores.csv`, `own_support_scores.csv`, `all_resolved_forecasts.csv`.

## 4. Governing sources

| date | note or package | claim | status |
|---|---|---|---|
| 2026-09-16 | `05_backtests/GBV_GUIDANCE_INFERENCE_PROTOCOL_v1.md` | Freezes the six specifications, the 0.4/0.4/0.2 driver ("no weight search … allowed after outcomes are inspected"), two-sided HAC3 lag-3 primary inference with Holm over six | **governs the pre-registration** |
| 2026-09-16 | `05_backtests/GBV_GUIDANCE_INFERENCE_RESULTS_v1.md` + `…/conditional/README.md` | C1 is the recommended conditional map; beta 1.043263, HAC3 [1.009134, 1.077392], Holm p 4.78e−18; AICc beats C2 | **governs the coefficients** |
| 2026-09-16 | `05_backtests/GBV_GUIDANCE_SEARCH_PROTOCOL_v1.md` / `…_SEARCH_RESULTS_v1.md` | Defines X = .4G[q]+.4G[q−1]+.2G[q−2] as the **frozen inherited driver** and calls it "a predictive convention"; sets the economic gate (≥10% below **both** baselines in **both** windows, n≥8, no MAE/bias deterioration, no year-deletion reversal) | **governs the driver definition and the forecast gate** |
| 2026-09-16 | `05_backtests/GBV_GUIDANCE_INPUT_CLARIFICATION_v1.md` | Terminology repair: `direct_gbv_growth` is *not* guidance-free; it anchors on the year-ago guide | governs labelling |
| 2026-09-16 | `05_backtests/GBV_GUIDANCE_BACKTEST_CHARTS_v1.md` | The **only** genuine rolling backtest of C1 itself: h1/h2/h3 RMSE 65.927/111.721/117.394 vs blend 50.524/98.245/122.694, n 9/8/7; "W1 and W2 contain exactly the same C1 forecasts" | **governs the out-of-sample record**; supersedes any use of P1 as "C1's backtest" |
| 2026-09-16 | `05_backtests/GBV_GUIDANCE_ALTERNATIVES_RESULTS_v1.md` | Seven further GBV→guide mappings; none promoted; a near-identical 5-parameter direct elasticity (beta 1.01663) exists as a live-formula alternative to C1 | governs the "is there a better 5-parameter map" question |
| 2026-09-16 | `05_backtests/C1_WORKBOOK_APPLICATION_v1.md` | C1 on the workbook **Base** path: 4Q26 $3,126.727M; also records C1's rolling loss to the blend | **superseded for the thesis** by the reconciliation below; still governs the workbook-identity arithmetic |
| 2026-09-16 | `05_backtests/C1_THESIS_RECONCILIATION_v1.md` | The Base case was the wrong case: the thesis lives in the **Short** path → 4Q26 $3,011.882M; also confirms two source-model errors in the Short build | **governs which GBV path the memo should quote** |
| 2026-09-15 | `05_backtests/GD_DECISION_REPORT_v2.md` (Willem's audit) | Fixed vs joint timing rules; joint weights 35.90/47.29/16.81/0.00; next-guide RMSE fixed 74.59/77.01, joint 64.29/63.83, **guide growth 59.06/61.31**; "retain the tool, change the pitch claim" | **strongest counter-evidence; governs the claim strength** |
| 2026-09-16 | `05_backtests/CONVERSION_SARIMA_PREREG_v1.md` §"fixed40" | Earliest statement of the 40/40/20 weights in the repo, as "a separately labeled predictive approximation", inherited challenger | governs the weights' provenance |
| — | `05_backtests/GBV_RECOGNITION_OPTIONS_v1.md` | Fees recognise at check-in; long stays recognise initially then monthly → no exact quarterly recognition schedule exists from booked or occupied nights alone | governs why any weight vector is a convention |

No web fetches were made for this line. Repo only.

## 5. Reproduction receipt

- Receipt: `data/processed/pitch_model_v2/receipts/R4C/receipt.json`
- Command: `PYTHONPATH=/Users/theomachado/Citadel-ABNB/analysis/src python3 /Users/theomachado/Citadel-ABNB/analysis/src/pitch_model_v2/repro.py --id R4C --watch data/processed/forecast_methods/gbv_guidance_inference_v1 --cmd "python3 -B analysis/src/forecast_methods/gbv_guidance_inference_v1/conditional/run.py --out …/conditional/results_v2 && MPLCONFIGDIR=… python3 -B analysis/src/forecast_methods/gbv_guidance_inference_v1/run.py --out-dir …/integrated_v2 && python3 -B <scratch>/compare_r4c.py"`
  · Exit: **0** · Wall: **10.2 s** · Interpreter: `python3` (3.13; pandas 3.0.0, statsmodels 0.14.6, numpy 2.4.2) · cwd: `/Users/theomachado/Citadel-ABNB-untracked` @ `d984b14`
- The package README's top-level command is `run.py --out-dir <fresh dir>`; it only **integrates**
  preserved results and re-verifies the scenario. The coefficients themselves are produced by
  `conditional/run.py --out <fresh dir>`, so both were run, in that order, inside one wrapper call.
  Both refuse to overwrite an existing directory, so a fresh `results_v2` / `integrated_v2` was used
  and the wrapper deleted them afterwards (`restored: true`, `changed: []`, 20 new files removed).
  The two empty directories were then removed by hand; `git -C /Users/theomachado/Citadel-ABNB-untracked status --short` is **empty**.
- Output: `…/conditional/results_v1/coefficients.csv`, rows `canonical / full / C1`, column `estimate`
  — `season_Q1` 6.9473876951229796 · `season_Q2` 7.1507485411437006 · `season_Q3` 7.4320468510260342 ·
  `season_Q4` 7.0898192281226526 · `gbv_beta` 1.0432632149063203.
  Committed values: identical. Tolerance: ±1e−9 on the estimate.
  **Match: yes** — fresh refit reproduces every one of the 30 C1 canonical coefficient rows
  (full/W1/W2 × OLS/HAC3 × 5 terms) with **max |estimate diff| 1.35e−14** and
  **max |SE diff| 1.33e−14**. File-level maxima across the whole results directory:
  `coefficients.csv` 2.46e−09 (a `t_statistic` cell), `model_statistics.csv` 4.64e−08
  (`joint_f_statistic`), `leave_one_year_out.csv` 1.73e−11, `diagnostics.csv` 2.87e−11,
  `primary_claims.csv` 9.20e−09, `conditional_scenarios.csv` 8.00e−11, `influence.csv` 1.01e−11,
  `vif.csv` 3.55e−15, `prepared_mature_rows.csv` **0.0**. All shapes identical.
- **Second, independent reproduction.** I refit C1 myself from
  `prepared_mature_rows.csv` with my own design matrix and statsmodels call, rebuilding the driver
  and both logs from the raw GBV and guide cells rather than reading the stored columns:
  my `0.4/0.4/0.2` driver matches `driver_musd` to **0.0**, `log_x` to 1.1e−16, `log_guide` to
  8.9e−16, and my coefficients match the committed file to **1.4e−14 (full)**, **3.6e−15 (W1)**,
  **7.4e−15 (W2)**, with HAC3 SEs to 1.3e−14 and beta p-values reproducing 4.04e−20 (OLS) /
  7.97e−19 (HAC3). Full transcript: `receipts/R4C/stdout.txt`.
- The 4Q26 application was run separately (it is a scenario, not a rebuild) and recorded at
  `receipts/R4C/forecast_4q26.json` and `receipts/R4C/forecast_4q26_cmd.txt`.
- `stderr.txt` contains one benign line: "Matplotlib is building the font cache".

## 6. Test record

**What was actually pre-registered.** Two different gates apply to this object and only one of them
is C1's own:

- **(P) Inference gate**, `GBV_GUIDANCE_INFERENCE_PROTOCOL_v1.md`, frozen before the fits:
  two-sided test of `beta_GBV = 0` under Bartlett HAC lag-3 with n/(n−k) correction and Student-t
  residual df, **Holm-adjusted across all six specifications**, positive sign required. The protocol
  states in advance that "W1/W2 subsets are descriptive robustness slices that overlap; they do not
  add independent replications."
- **(E) Economic/forecast gate**, inherited identically by `GBV_GUIDANCE_SEARCH_PROTOCOL_v1.md`,
  `GBV_GUIDANCE_ALTERNATIVES_PROTOCOL_v1.md` and `CONVERSION_SARIMA_PREREG_v1.md`: matched RMSE
  **≥10% below BOTH strong baselines in BOTH windows**, **n ≥ 8 per window**, no worse MAE or
  absolute bias, no target-year-deletion reversal, and a paired 90% dependence-aware RMSE-ratio
  upper bound below 1 against guide growth.

**(a) The in-sample association — gate (P).**

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| full (2021Q4–2026Q2) | 19 | HAC3 beta, 95% CI | **1.043263 [1.009134, 1.077392]** | — | — | — | positive, excludes 0, Holm p < .05 over six | **pass** (raw p 7.97e−19, **Holm p 4.78e−18**) |
| full | 19 | OLS beta p (sensitivity, not selectable) | 4.04e−20 | — | — | — | reported, never chosen for being smaller | pass (reported) |
| full | 19 | adj. R² / GBV partial R² / AICc | 0.998812 / 0.997880 / −107.056 | — | — | — | AICc vs trend model C2 on same rows | pass (C2 −103.806) |
| full | 19 | simulation-calibrated worst-null tail, Holm | **0.000300** | — | — | — | frozen addendum, 20,000 draws × 6 null processes | pass (0 exceedances; MC-resolution-limited) |
| W1 (2023Q1+) | 14 | HAC3 beta, p | 1.013953, 5.29e−12 | — | — | — | descriptive slice only | pass (not an independent replication) |
| W2 (2024Q1+) | 10 | HAC3 beta, p | 0.996204, 9.73e−07 | — | — | — | descriptive slice only | pass (not an independent replication) |

**(b) Stability of the coefficients.**

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| full, leave-one-target-year-out | 18/15/15/15/15/17 | beta range across the 6 deletions | **1.036676 – 1.057894**, every OLS p ≤ 4.6e−17 | — | — | — | sign and magnitude must not depend on one year | **pass** |
| full, delete 2025 (the influential year) | 15 | beta | 1.057894 (vs 1.043263) | — | — | — | — | pass |
| W2, leave-2024-out / leave-2025-out | 6 / 6 | beta, 95% CI (1 residual df) | 0.997 **[0.303, 1.691]** / 1.034 **[0.179, 1.889]** | — | — | — | — | **vacuous** — the window is too short to test anything |
| full | 19 | 2025Q4 Cook's D vs 4/n | **0.3354 vs 0.2105** | — | — | — | flag, do not delete | flagged, retained |
| full | 19 | GBV VIF / design condition number | 1.188 / 4.70 | — | — | — | — | pass (C2's VIF is 55.33 — that is why C2 is not the map) |
| full | 19 | BG4 / Ljung-Box4 / Koenker-BP / Jarque-Bera p | 0.597 / 0.755 / **0.0689** / 0.479 | — | — | — | none below 5% | pass, but BP is near the cutoff and F-form p is 0.0576 |
| full | 19 | ADF vs KPSS on levels | ADF rejects unit root; **KPSS rejects trend-stationarity** for log guide (p<0.01) and log X (p 0.0405) | — | — | — | descriptive, low power | **conflicting** — no stationarity claim is available |
| W2, BG4 | 10 | residual serial-correlation test | **unavailable** (frozen minimum auxiliary residual-df rule fails) | — | — | — | — | skipped, recorded, not counted as a pass |

**Window sensitivity of the answer itself:** feeding the same driver X = $25,046.09M through the W1
and W2 refits instead of the full fit gives **$3,109.41M (W1)** and **$3,092.73M (W2)** against
$3,126.51M (full) — a **$33.8M / 1.08% spread from the choice of training window alone**, before any
GBV uncertainty.

**(c) The out-of-sample record — gate (E).** The only genuine rolling test of C1 refits the exact
equation one day before each historical first-guide issuance, using only mature GBV and guide labels
published by that date, and projects the unknown target GBV with the inherited published-YoY carry
(`gbv_guidance_charts_v1/results_v1/c1_matched_scores.csv`; I recomputed every reference column
below from `all_resolved_forecasts.csv` and reproduced the note's numbers exactly).

| window | n | metric | this line (C1) | naive (guide_snaive) | guide+cushion (blend) | guide growth | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 = W2, h1 (next guide), 2024Q2–2026Q2 | 9 | guide-mid RMSE $M | **65.927** | 343.552 | **50.524** | **63.514** | ≥10% below both, both windows | **FAIL** (worse than both) |
| W1 = W2, h1 | 9 | MAE $M / bias $M | 53.575 / **+13.703** | 331.111 | 43.778 / −19.156 | 60.170 / −5.741 | MAE must not worsen | **FAIL** |
| W1 = W2, h2 | 8 | guide-mid RMSE $M | **111.721** | 347.518 | **98.245** | **103.099** | ≥10% below both | **FAIL** (worse than both) |
| W1 = W2, h3 | 7 | guide-mid RMSE $M | **117.394** | 347.162 | 122.694 | **116.363** | ≥10% below both, n ≥ 8 | **FAIL** (−4.3% vs blend only; loses to guide growth; n = 7 < 8) |
| W1 = W2, h3 | 7 | MAE $M | **99.039** | 331.429 | 87.279 | 91.438 | MAE must not worsen | **FAIL** (+13.5% vs blend) |
| W1 = W2, h1, incl. the disclosed 2026Q3 origin | 10 | guide-mid RMSE $M | **89.134** | — | — | — | — | the single 2026Q3 h1 error is **+$200.8M** |
| W1 (full own support) | 14 | h1 RMSE $M — C1 has **no** rows | — | — | 54.15 | 75.04 | n ≥ 8 per window | **cannot be evaluated** (training adequate only from 2024) |
| W2 (full own support) | 10 | h1 RMSE $M — C1 has **no** rows | — | — | 48.87 | 61.31 | n ≥ 8 per window | **cannot be evaluated** |

The other comparators on C1's own h1 sample (n = 9) for completeness: fixed40 bridge 66.632,
fixed-lag (⅔/⅓) bridge 73.024, `direct_gbv_growth` 55.078. At h3 (n = 7): fixed40 139.210,
fixed-lag 118.950, `direct_gbv_growth` 118.889.

**(d) The fixed kernel and the same baselines elsewhere in the repo**, for the judge who asks
"beaten by what, exactly":

| source | window | n | fixed kernel | joint | guide growth | blend | note |
|---|---|---|---|---|---|---|---|
| `GBV_GUIDANCE_SEARCH_RESULTS_v1.md`, next guide | W1 / W2 | 14 / 10 | fixed40 66.51 / 63.69 | — | 75.04 / 61.31 | **54.15 / 48.87** | the frozen 50/50 blend is the incumbent |
| `GD_DECISION_REPORT_v2.md` (Willem, 15 Sep), next guide | W1 / W2 | 11 / 10 | fixed-lag 74.59 / 77.01 | 64.29 / 63.83 | **59.06 / 61.31** | — | "retain the tool, change the pitch claim" |
| `GD_DECISION_REPORT_v2.md`, eligibility re-scope, third guide | W1 / W2 | 12 / 10 | 159.10 / 114.36 | — | 144.57 / 125.70 | — | the one favourable fixed result reverses on its own eligible history |

**Did any pre-registered gate pass?** Yes — exactly one, and it is not a forecasting gate. Gate (P),
the in-sample conditional association, passes on the full sample and is not reversed by any
leave-one-year deletion or by either window slice, and it survives the auditor's frozen small-sample
simulation (Holm-adjusted worst-null tail 0.000300). Gate (E), the forecast gate, **fails at every
horizon** and cannot even be run on W1/W2 as the harness defines them. Two further caveats on the
"survives both windows" language: (i) the C1 rolling W1 and W2 rows are **identical** — same 9/8/7
quarters, same RMSE to every decimal — so printing both is one window twice, not a replication; and
(ii) the frozen pre-registration the charts note cites for that rolling test,
`WORKBOARD_GBV_GUIDANCE_CHARTS_v1.md`, **does not exist in either checkout**, so that test's
pre-registration cannot be verified from the repo.

**Strongest known failure:** on the only guide the pitch trades — the next one — C1's own
prior-only backtest is worse than *both* of its pre-registered baselines, $65.93M RMSE against
$50.52M for the existing 50/50 blend and $63.51M for a one-line guide-growth rule on the same nine
quarters (and worse on MAE too), while the W1/W2 double-window requirement cannot be exercised at
all because C1 has only one window's worth of forecasts printed twice.

Three further failures that must travel with this line, in descending severity:

1. **The fit is not point-in-time and cannot be.** The driver contains the target quarter's own
   actual GBV, which Airbnb had not published when that guide was issued. CLAUDE.md rule 2
   ("point-in-time or it doesn't count") therefore bars the full-sample C1 numbers from being
   registered as a forecast — and the package never registered them. adj. R² 0.9988 is a
   description of 19 log-guide points, not 99.88% forecast accuracy.
2. **Five parameters on nineteen observations, fourteen residual df — and the seasons carry the
   fit.** The joint F is F(4,14) = 5,740.9, but that omnibus test includes the seasonal contrasts;
   the protocol says so explicitly. Guidance is already near-deterministic in season and scale, so a
   high R² here is nearly free. The W2 slice has 5 residual df, and its own leave-one-year-out
   refits drop to **1** residual df, producing beta intervals as wide as [0.18, 1.89].
3. **The GBV input, not the mapping, is where the error lives.** Applying the same origin-fitted
   coefficients to subsequently *realised* GBV cuts rolling RMSE to 49.2 / 52.0 / 54.7 $M at
   h1/h2/h3. That hindsight diagnostic is not a deployable forecast or a lower bound, but it says
   plainly that C1's precision is inherited from the ADR/nights path — which is R4C's dependency,
   not its achievement.

## 7. Kill list and consistency

- **Kill-list check: none.** Nothing in this line quotes the −3.4pp Q4 FX step (bridge v3 uses the
  fx_lag_v2 kernel +1.0pp for 4Q26 revenue FX), the "82% of Q4 FX already determined" claim, the
  "+4.05% fee uplift", the 9/9 guide-below-Street drift rule or any p-value for it, restated unearned
  fees, the 1.71M quote panel, M5's hierarchical cushion model, the 120-market panel or the Stan
  state space. C1 requires none of them: its only inputs are a GBV path and the quarter of the year.
  One phrase to police: the governing notes are careful to say the blend is "the historical leader
  among this bounded family", never "nothing beats guide × cushion" — keep that wording.
- **Conflict 1 — the driver contradicts our own kernel (R1).** The established kernel is
  `Revenue_q = λ_s × [⅔·GBV_{q−1} + ⅓·GBV_{q−2}]`: **zero weight on the target quarter's own GBV**.
  C1's driver puts **0.4 on the same quarter**. Willem's joint re-fit gives a third answer
  (0.3590 / 0.4729 / 0.1681 / 0.00), and R1's own dossier records the joint w₀ wandering 0.359→0.605
  across origins. Three timing rules, none measured from reservation cohorts; the SEARCH results call
  the weighted driver "a predictive convention" and `CONVERSION_SARIMA_PREREG_v1.md` introduced
  40/40/20 as "a separately labeled predictive approximation". **Do not present 0.4/0.4/0.2 as a
  booking-cohort share, and do not let a memo page assert both ⅔/⅓ and 0.4/0.4/0.2 as *the* timing
  of Airbnb's bookings.** The honest line is R1's: the weights are forecasting conventions, and the
  seasonal scale absorbs most of the difference.
- **Conflict 2 — the flagged window conflict.** C1's full fit trains on **19 guides spanning
  2021Q4–2026Q2**, i.e. on *every* quarter the harness reserves for scoring, because the harness
  windows are W1 = 1Q23+ (n≈14) and W2 = 1Q24+ (n≈10). Worse, the labels "W1"/"W2" inside
  `coefficients.csv` are **training-sample slices of an in-sample conditional fit**, not the
  harness's point-in-time scoring windows, and the inference protocol itself says they "do not add
  independent replications". Two consequences: (i) no number from the C1 full fit may be described as
  having "survived W1 and W2" in the harness sense; (ii) where C1 *does* have PIT forecasts, W1 and
  W2 contain the identical rows. If the memo prints a W1/W2 line for R4C it must say which of the
  two meanings it is using.
- **Conflict 3 — cushion double-count risk with R3.** C1 is trained on *issued guides*, so the
  management cushion is already inside `exp(season)`. The workbook's legacy path instead computes
  `revenue / (1 + cushion)` (`Revenue Model!B101`, 3.88%). **Never apply a cushion on top of a C1
  output**, and never compare a C1 guide with a cushion-derived guide as if they were the same
  object. Related unrepaired defect to hand to R3: the workbook's Q4 cushion is 3.88% in
  `'5 Nov & Street'!B39` while `C97` lists four Q4 cushions averaging 3.15%.
- **Conflict 4 — which GBV path.** `C1_WORKBOOK_APPLICATION_v1.md` applied C1 to the workbook's
  **Base** exhibit ($3,126.73M for 4Q26); `C1_THESIS_RECONCILIATION_v1.md` (same day, later)
  establishes that the thesis lives in the **Short** case ($3,011.88M) and that the Base exhibit is a
  fixed presentation row that the case selector does not drive. **The reconciliation governs.** My
  §2 row is neither: it is C1 on the team's current **bridge-v3 base** GBV path, $3,126.51M — which
  lands within $0.22M of the workbook Base because the workbook's Base GBV path is essentially the
  bridge-v3 path. If the memo quotes a bear case, it must quote the Short-path number and say so.
- **Conflict 5 — comparing guidance to revenue consensus.** Both C1 notes compare a C1 *guide* with
  LSEG/Bloomberg *revenue* means. Those are different objects, as both notes state; the −4.74% /
  −9.34% "gaps" in the reconciliation table are not observed guidance-expectation gaps. Do not let
  that number migrate into the memo as a Street disagreement.
- **Cross-check against the team's other 4Q26 objects** (context, not a conflict): C1 at bridge-v3
  base $3,126.5M sits below B2's guide midpoint $3,161M (80% $3,012–3,312), below Willem's joint
  $3,185.3M and fixed-lag $3,160.6M, just below guide growth $3,133.9M, and above the workbook's
  legacy cushion-derived $3,059.4M. All five are inside B2's 80% band, so R4C does not by itself
  create a new disagreement with Street.
- **Provenance gaps to disclose:** (i) the package and all its notes are on an unmerged local branch
  (`theo/local-untracked-2026-09-15`, `d984b14`), not on `theo/pitch-model-v2`; (ii) the frozen
  extension `WORKBOARD_GBV_GUIDANCE_CHARTS_v1.md` cited by the charts note is absent from both
  checkouts; (iii) the underlying guide/GBV panel is a reconstructed public history, not a certified
  vendor archive — the alternatives audit found a filing with 2Q26 GBV 27,247 and 2Q25 23,447 where
  the panel records 27,200 and 23,500, and the four-cell SEC precision sensitivity moves beta only
  from 1.043263 to 1.043657 (4Q26 guide effect < $1M), so the effect is immaterial but the
  certification is genuinely incomplete.

## 8. Open choices

1. **Quote C1's HAC3 interval or its OLS interval?** — options:
   (a) **HAC3** (the protocol's primary): beta [1.0091, 1.0774]; 4Q26 coefficient-only band
   [$3,056.7, $3,197.9]. (b) **OLS** (the protocol's declared sensitivity): beta [1.0157, 1.0708];
   4Q26 band [$3,080.7, $3,173.0]. — **recommendation: HAC3, and say so out loud.** — why: the
   protocol pre-registered HAC3 as primary and OLS as a sensitivity, with an explicit instruction
   never to choose the smaller p-value after the fact; HAC3 is also the wider (more conservative)
   interval on beta, which is the coefficient a judge will press. The catch a human must accept: on
   three of the four seasonal intercepts HAC3 is *narrower* than OLS, so "HAC is conservative" is not
   uniformly true, and with 19 observations and lag 3 neither interval is exact — the auditor's own
   simulation found nominal 5% HAC3 tests rejecting 8.1–31.1% under plausible short-sample nulls. If
   the memo has room for only one number, quote the point estimate with "≈1.0, indistinguishable from
   one-for-one" and put the interval in the appendix.
2. **How to word "five parameters on nineteen observations"?** — options:
   (a) **Lead with parsimony**: "four seasonal levels and one elasticity — five numbers, 14 residual
   degrees of freedom, lower AICc than the trend-augmented alternative, and every leave-one-year
   refit keeps beta in 1.037–1.058." (b) **Lead with the limitation**: "19 observations is a small
   sample and the seasonal terms carry most of the fit; the defensible claim is a conditional
   association, not a forecast." (c) **Both, in that order, in one sentence.** —
   **recommendation: (c), with the elasticity stated as ≈1.0.** — why: (a) alone invites exactly the
   question the judge asked and will be punished when the out-of-sample record comes out; (b) alone
   understates a coefficient that really is stable across every deletion. The wording that survives
   cross-examination is: *"Five parameters on nineteen guides: four seasonal levels and one
   elasticity that comes out at 1.04 — guidance scales one-for-one with weighted bookings. That is a
   conditional map, not a forecast: it uses the quarter's own booked GBV, and when we refit it before
   each historical guide it loses to a one-line guide-growth rule. We use it to translate our nights
   and ADR view into a guide, and we show the blend and guide-growth beside it."* A human must also
   decide whether to state the parameter count at all in a two-page memo, or only in the Q&A pack.
3. *(Secondary, only if the memo quotes R4C at all.)* **Does C1 replace the cushion bridge or sit
   beside it?** — options: (a) replace (C1 learns the cushion implicitly; one fewer assumption);
   (b) sit beside it, with the blend and guide-growth printed too, as `GD_DECISION_REPORT_v2.md` and
   the charts note both recommend. — **recommendation: (b)** — why: C1 loses the pre-registered
   forecast gate; showing it alone converts a transparent scenario translator into an implied
   accuracy claim we cannot defend. The cost of (b) is column space, not credibility.

## 9. Judge Q&A

1. Q: *"Five parameters on nineteen observations — isn't that overfit?"*
   A: In the usual sense, no: 14 residual degrees of freedom, GBV VIF 1.19, condition number 4.7,
   AICc better than the trend-augmented version, and every leave-one-target-year refit keeps the
   elasticity in 1.037–1.058 with p ≤ 4.6e−17. In the sense that matters, yes: four of the five
   parameters are seasonal levels, guidance is already nearly deterministic in season and scale, so
   the 0.9988 adjusted R² is close to free — and it is an *in-sample* number on a driver that
   includes the quarter's own booked GBV, which management did not have when it issued that guide.
   The parameter count is not the problem; the information set is.
2. Q: *"So what did it get wrong out of sample?"*
   A: The next guide, which is the only one we trade. Refit one day before each historical guide with
   a feasible GBV projection, C1's next-guide RMSE is $65.9M against $50.5M for our existing 50/50
   blend and $63.5M for a one-line rule that just extends the last guide's growth rate — worse than
   both on RMSE and on MAE, on the same nine quarters, with a +$13.7M bias. It is also worse at the
   second guide. At the third it edges the blend on RMSE by 4% but is worse on MAE and still loses to
   guide growth. And we cannot show you the two-window test our own protocol demands: C1 has enough
   training history only from 2024, so its W1 and W2 rows are the identical nine, eight and seven
   quarters. On the one origin outside the scored window, 2026Q3, it missed the guide by +$200.8M.
3. Q: *"Then why is it in the model at all?"*
   A: Because it is the cleanest way to turn *our* nights and ADR view into a guide without a second
   cushion assumption, and because the mapping itself is not where the error lives. Hand the same
   origin-fitted coefficients the GBV that actually happened and rolling RMSE drops from
   $65.9/$111.7/$117.4M to $49.2/$52.0/$54.7M. That says the uncertainty is in our operating path,
   which is exactly where we want to be arguing. We use C1 as a transparent translator, we print the
   blend and guide-growth next to it, and we claim a conditional association — one-for-one elasticity
   of guidance to weighted bookings — not a forecasting edge. Willem's 15 September audit reached the
   same conclusion: retain the tool, change the claim.

## 10. Grade
Grade: B — the five coefficients reproduce exactly (exit 0; fresh refit and my own independent
statsmodels fit both match `coefficients.csv` to 1.4e−14 across all 30 canonical C1 rows, with the
driver rebuilt from raw GBV cells to 0.0), but the object is **descriptive and single-window**: it is
a conditional in-sample map that conditions on GBV published after the guide was issued, its only
pre-registered win is the in-sample association gate, it fails the pre-registered forecast gate
against both baselines at h1 and h2, and its W1/W2 rolling rows are literally the same forecasts
printed twice — so the A condition ("survives both W1 and W2 against a pre-registered line") is not
merely unmet but unavailable.
