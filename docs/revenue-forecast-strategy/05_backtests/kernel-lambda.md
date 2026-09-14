# kernel-lambda — the recognition kernel on lagged printed GBV

Run 2026-09-11 overnight. Package `analysis/src/forecast_methods/kernel_lambda/`.

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/kernel_lambda/run.py   # exit 0
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py        # exit 0
```

---

## Headline, in four sentences

1. **The acceptance table reproduces exactly.** All 12 architect cells to 2 decimals, Q4 within-season range 0.171pp. The kernel package is implementing the kernel the programme thinks it is.
2. **The lag weight is not identified, and the direction of the miss flips with the estimation window.** The leave-one-quarter-out minimiser is w = 0.76 on n=22, 0.68 on n=18, 0.32 on n=14 and 0.13 on the 12 acceptance cells; the 95% block-bootstrap interval on the argmin spans essentially [0, 0.9] in every window. The critic's "minimum near 0.33, 2/3 materially worse" is a property of the **2023Q1+ subsample only**; on the post-COVID n=18 window 2/3 is the minimiser to three decimals. Neither side is wrong; the objective is flat and the data cannot separate them.
3. **The cost of that non-identification on the number that matters is 6M dollars.** 4Q26 at GBV_3Q26 = 26,300: w=2/3 gives 26,600 x 12.030% = **3,200M**; w=0.38 gives 26,858 x 11.890% = **3,193M**. Gap +6M, 0.20%. The whole w in [0.33, 2/3] band spans 3,192-3,200M.
4. **The pre-registered same-quarter test FAILS in the direction that weakens the memo's first sentence.** A non-negative simplex lag polynomial over lags 0-3 puts **phi_0 = 0.23 to 0.41** on the *current* quarter's GBV in all three estimation windows, with 95% block-bootstrap intervals excluding 0.02 in all three, and it beats the phi_0 = 0 restriction **out of sample** (leave-one-quarter-out) in all three. The implied mean lag is 0.95-1.18 quarters, not the 1.33 that a 2/3-1/3 kernel implies. This is reported in full below, with the identification caveats, because it is the single finding tonight that changes what the memo may claim.

---

## (a) Acceptance test — **PASS**

`lambda_q = Revenue_q / [2/3 GBV_{q-1} + 1/3 GBV_{q-2}]`, from `02_kpi_panel_quarterly.csv` alone.
Output: `data/processed/forecast_methods/kernel_lambda/01_acceptance_test.csv`, `01_lambda_table.csv`.

| season | cell 1 | cell 2 | cell 3 | architect | match |
|---|---|---|---|---|---|
| Q1 | 1Q24 **13.034** | 1Q25 **12.325** | 1Q26 **12.612** | 13.034 / 12.325 / 12.612 | 3/3 |
| Q2 | 2Q24 **13.449** | 2Q25 **13.946** | 2Q26 **13.736** | 13.449 / 13.946 / 13.736 | 3/3 |
| Q3 | 3Q23 **17.391** | 3Q24 **17.145** | 3Q25 **17.182** | 17.391 / 17.145 / 17.182 | 3/3 |
| Q4 | 4Q23 **11.946** | 4Q24 **12.117** | 4Q25 **12.026** | 11.946 / 12.117 / 12.026 | 3/3 |

n = 12 cells, all matched to 2 d.p.; max absolute difference 0.0005pp. Q4 within-season range **0.171pp** as stated.

**Extra usable cells the architect table omits:** 1Q23 = **12.803**, 2Q23 = **13.724** (n=2). The table's three-per-season labelling is *not* 2023-2026 uniformly: Q1 and Q2 run 2024-2026 and Q3 and Q4 run 2023-2025, which is why Q1/Q2 have a fourth observation and Q3/Q4 do not. This resolves the documentation inconsistency the chief of staff flagged.

**Subset used downstream.** The season means that drive every live object use the **2023Q1+ window (n=14)**, i.e. the 12 acceptance cells *plus* 1Q23 and 2Q23. Estimation-window variants are registered separately and scored.

The full lambda series is available from **2021Q1** (n=22 quarters with both GBV lags). 2021 is COVID-distorted — 2Q21 lambda is 15.110 against a 2Q23-2Q26 range of 13.72-13.95 — and it is the single largest driver of the PIT backtest's positive bias (below).

---

## (b) The weight grid

**Pooling convention, one line:** relative deviations of `lambda_t(w)` from the mean of its own quarter-of-year, pooled across all four seasons on one fixed quarter set, RMS with denominator `(N - S)`, reported in percent. The LOO criterion is the same arithmetic with the season mean recomputed without the held-out quarter, which is the criterion that should be quoted: in-sample dispersion is not evidence about its own minimiser.

Output: `02_weight_grid.csv` (101-point grid x 4 samples), `03_weight_summary.csv`.

| sample | n | argmin w (LOO) | LOO at argmin | LOO at w=2/3 | LOO at w=0.38 | +5% flat band | block-boot 95% CI on argmin |
|---|---|---|---|---|---|---|---|
| 2021Q1+ | 22 | **0.76** | 3.141% | 3.273% | 4.944% | [0.67, 0.86] | [0.26, 0.90] |
| 2022Q1+ (ex-COVID) | 18 | **0.68** | 1.891% | 1.891% | 2.210% | [0.53, 0.84] | [0.08, 0.88] |
| 2023Q1+ | 14 | **0.32** | 1.534% | 1.834% | 1.544% | [0.17, 0.48] | [0.00, 0.86] |
| 12 acceptance cells | 12 | **0.13** | 1.548% | 2.154% | 1.705% | [0.00, 0.30] | [0.00, 0.86] |

400 moving-block bootstrap draws, block length 4 (one seasonal cycle), draws rejected unless all four seasons appear at least twice.

**Interpretation, honestly.** I was told to expect the shape "minimum near 0.33, flat across 0.20-0.50, 2/3 materially worse" and not to worry if levels differed. That shape **reproduces on the 2023Q1+ and 12-cell samples and only there.** Add the 2022 quarters and the minimiser jumps to 0.68; add 2021 and it goes to 0.76. The correct statement is therefore stronger and less convenient than either camp's: *the lag weight is not identified at all by 22 quarters of data.* The bootstrap CI covers nearly the whole unit interval in every window. Saying "2/3 is not the minimiser" is true on one subsample and false on another; saying "the conversion is stable to 0.14pp" is a statement about smoothly growing GBV, not about the weight. Both should be dropped in favour of the CI and the cost below.

### Cost of the flatness (`05_flatness_cost_4q26.csv`)

Season-Q4 lambda re-estimated at each w on the 2023Q1+ window, applied to GBV_3Q26 = 26,300:

| w | lambda_Q4 | base (M) | 4Q26 print (M) |
|---|---|---|---|
| 0.20 | 11.804 | 27,020 | 3,189.6 |
| 0.33 | 11.866 | 26,903 | 3,192.4 |
| 0.38 | 11.890 | 26,858 | 3,193.5 |
| 0.50 | 11.948 | 26,750 | 3,196.2 |
| **2/3** | **12.030** | **26,600** | **3,199.9** |
| 0.76 | 12.076 | 26,516 | 3,202.1 |
| 0.80 | 12.096 | 26,480 | 3,203.0 |

n = 3 Q4 cells per estimate. **The entire 0.20-0.80 range of the weight moves the 4Q26 print by 13M, or 0.42%; the 2/3-versus-0.38 fight is worth 6M, or 0.20%.** This is the sentence that answers the hardest attack on the kernel: the weight is unidentified and it does not matter, because re-estimating lambda at each w absorbs almost all of the change in the base.

---

## (c) Point-in-time backtest at guide dates

Refit at each guide date on the harness spine (`history_as_of`, `print_date <= vintage_date`, i.e. the same-day letter is in the information set — the harness deviation, inherited, not re-litigated here). At horizon 0 **both GBV lags are already printed**, so the object needs no GBV forecast: the just-printed quarter's GBV arrives in the same letter that carries the guide.

Baselines are the harness's own five; the scorer joins them. Percent-scale errors computed against `targets.csv` actuals. **W1 n = 14 guide dates (targets 2023Q1-2026Q2), W2 n = 10 (2024Q1-2026Q2).** The 2026-08-06 guide is LIVE and enters nothing.

### PIT-prior replay, revenue level

| object / baseline | W1 n | MAE % | RMSE % | bias % | RMSE ratio to naive (W1) | W2 n | MAE % | RMSE ratio (W2) | survives both |
|---|---|---|---|---|---|---|---|---|---|
| baselines guide_cushion | 14 | 1.086 | 1.204 | +0.265 | **0.377** | 10 | 1.043 | 0.319 | yes |
| **kernel last3_ex_covid** | 14 | **1.489** | **2.050** | **+0.187** | **0.555** | 10 | **1.398** | **0.472** | **yes** |
| kernel ex_covid | 14 | 1.532 | 2.084 | +0.257 | 0.565 | 10 | 1.458 | 0.484 | yes |
| kernel last3 | 14 | 2.053 | 2.859 | +1.546 | 0.766 | 10 | 1.790 | 0.647 | yes |
| **kernel published spec (w=2/3)** | 14 | **2.313** | **3.066** | **+2.230** | **0.831** | 10 | **2.154** | **0.727** | **yes** |
| baselines naive | 14 | 2.743 | 3.405 | +0.510 | 1.000 | 10 | 3.207 | 1.000 | no |
| baselines street (pre-guide, vintage-stamped) | 14 | 3.216 | 3.746 | -2.627 | 1.073 | 10 | 2.849 | 0.871 | no |
| baselines ar1 | 14 | 3.358 | 3.801 | -1.870 | 1.101 | 10 | 3.374 | 1.009 | no |
| kernel h1 (two quarters ahead, naive GBV) | 14 | 3.373 | 4.397 | +2.761 | 1.169 | 10 | 2.546 | 0.886 | no |
| kernel w=0.38 | 14 | 3.691 | 4.461 | +3.264 | 1.433 | 10 | 3.452 | 1.196 | no |
| kernel w=0.33 | 14 | 4.011 | 4.850 | +3.488 | 1.583 | 10 | 3.728 | 1.311 | no |
| baselines trailing4 | 14 | 5.319 | 7.441 | +3.316 | 1.806 | 10 | 3.412 | 1.101 | no |

### Full-sample-prior replay (published side by side, as required)

| object | W1 n | MAE % | RMSE % | bias % | W2 n | MAE % | RMSE % | bias % |
|---|---|---|---|---|---|---|---|---|
| kernel last3 / last3_ex_covid | 14 | 1.015 | 1.360 | -0.071 | 10 | 1.140 | 1.528 | +0.042 |
| kernel ex_covid | 14 | 1.017 | 1.448 | +0.061 | 10 | 1.232 | 1.654 | +0.203 |
| kernel published spec (w=2/3) | 14 | 1.418 | 1.904 | +1.142 | 10 | 1.626 | 2.154 | +1.296 |
| kernel w=0.38 | 14 | 2.053 | 2.467 | +1.695 | 10 | 2.418 | 2.781 | +1.917 |
| kernel w=0.33 | 14 | 2.198 | 2.657 | +1.815 | 10 | 2.588 | 2.980 | +2.051 |

### Revenue y/y growth target

| object | window | basis | n | MAE (pp) | RMSE (pp) | bias (pp) | RMSE ratio to naive |
|---|---|---|---|---|---|---|---|
| kernel revenue_yoy_next_q | W1 | PIT | 14 | 2.626 | 3.454 | +2.533 | 0.903 |
| kernel revenue_yoy_next_q | W2 | PIT | 10 | 2.389 | 3.242 | +2.258 | 0.756 |
| kernel revenue_yoy_next_q | W1 | full_sample | 14 | 1.597 | 2.107 | +1.275 | 0.551 |
| baselines naive | W1 | PIT | 14 | 3.100 | 3.825 | +0.544 | 1.000 |
| baselines ar1 | W1 | PIT | 14 | 3.839 | 4.351 | -2.221 | 1.138 |

### Calibration

CRPS, PIT and conformal come from the harness scorer (`scoreboard.csv`). For the best PIT object (`last3_ex_covid`, W1): CRPS 30.9, PIT KS p = 0.63, empirical coverage of the nominal-80% [q10, q90] band 0.643, rolling split-conformal coverage 0.875 at n_cal = 6, alpha = 0.2. The published spec at w=2/3 has PIT KS p = **0.0027** — its predictive distribution is rejected, which is the bias showing up in the calibration diagnostic rather than only in the mean. **Exchangeability is violated**: these residuals are a time-ordered non-exchangeable sequence and the conformal number is descriptive, not a guarantee; the attainable band at n_cal = 6 is [85.7%, 100%] and there is no 80% guarantee available at this sample size.

### On the "honest figures to match"

I was given MAE 1.74%, RMSE 2.44, bias +0.99 from origin 1Q23. **I could not reproduce those as a strict point-in-time replay of the published spec.** The strict PIT numbers for w=2/3 season-mean-over-all-history are 2.313 / 3.066 / +2.230. The quoted triple sits between my full-sample-prior w=2/3 replay (1.418 / 1.904 / +1.142) and my full-sample-prior w=0.38 replay (2.053 / 2.467 / +1.695). My reading is that the quoted figures are a **full-sample-prior** construction, not a PIT one, and the memo should not describe them as walk-forward. The defensible PIT claim is the `last3_ex_covid` object at **MAE 1.49%, RMSE 2.05%, bias +0.19%, RMSE ratio 0.555, surviving both windows.**

### What the kernel does and does not beat

Beats on both windows: naive, AR(1), trailing-4, the vintage-stamped pre-guide Street. **Loses to guide-midpoint-plus-cushion by a wide margin** (0.555 vs 0.377 RMSE ratio). That is the right result and must be said first: once management has guided, the guide plus the trailing-8 cushion is the best revenue forecast available and the kernel does not improve on it. The kernel's job is the case where **no guide exists yet** — at the 2-24 October pitch date there is no 4Q26 guide, so the cushion baseline is undefined and the kernel is the constructive object. The kernel is also the only object that produces the *guide* rather than the *print*.

---

## (d) Is the booking-to-check-in FX remeasurement inside lambda distinguishable from zero? — **No**

Construction: wedge_q = stated revenue FX points minus the ADR FX points already carried into the lagged GBV base through the same kernel, `fx_pts_revenue_q - [2/3 fx_pts_adr_{q-1} + 1/3 fx_pts_adr_{q-2}]`; regressand is the relative deviation of lambda from its season mean, in percent. Output `07_fx_wedge_regression.csv`, cells in `07_fx_wedge_cells.csv`.

| sample | n | slope | se | t | p | interval-likelihood slope set | distinguishable from 0 |
|---|---|---|---|---|---|---|---|
| the 12 acceptance cells (architect's n) | 12 | **+0.233** | 0.252 | +0.93 | 0.35 | [+0.087, +0.373] | no |
| all four seasons, 2023Q1+ | 14 | +0.184 | 0.216 | +0.85 | 0.39 | [+0.051, +0.304] | no |
| all available | 15 | +0.193 | 0.207 | +0.94 | 0.35 | [+0.055, +0.322] | no |

The **interval likelihood** is the set-identified reading demanded by the letter-rounding rule: every FX point is a letter-rounded integer, so the wedge is only known inside a box of +/- 0.5 on each of three integers. I draw the latent values uniformly inside their intervals 2,000 times and report the full attainable range of the slope. The slope set never crosses zero, but it is small and the t-statistic never approaches 2 at any latent draw.

**Verdict: the architect's falsification survives.** My slope on his n=12 is +0.233 against his +0.158 with a nearly identical standard error (0.252 vs 0.275) and the same conclusion. I could not reproduce +0.158 to the digit — the exact regressand and wedge construction are not written down anywhere I could find, so this is a re-derivation of the test rather than a replication of his arithmetic, and I flag that rather than claim a match. **Extending to all four seasons with the interval likelihood does not change the answer:** the check-in remeasurement inside lambda is not distinguishable from zero at n = 12-15, and the FX step-down must not be subtracted a second time.

---

## (e) The pre-registered same-quarter test — **phi_0 is NOT zero**

Model: `Revenue_q = lambda_{s(q)} * sum_{k=0..3} phi_k GBV_{q-k}`, phi on the simplex, phi >= 0 (softmax parameterisation), fitted on **relative** errors. 4 seasonal lambdas + 3 free weights = 7 parameters. Output `06_lag_polynomial.csv`.

| sample | n | phi_0 | phi_1 | phi_2 | phi_3 | mean lag (q) | in-sample rel-RMSE | phi_0 95% block-boot CI | P(phi_0 > 0.02) |
|---|---|---|---|---|---|---|---|---|---|
| 2021Q2+ | 21 | **0.225** | 0.604 | 0.172 | 0.000 | 0.95 | 1.26% | [0.162, 0.517] | 0.99 |
| 2022Q1+ | 18 | **0.405** | 0.179 | 0.360 | 0.056 | 1.07 | 0.88% | [0.096, 0.633] | 0.98 |
| 2023Q1+ | 14 | **0.390** | 0.041 | 0.569 | 0.000 | 1.18 | 0.75% | [0.032, 0.920] | 0.97 |

Restricting phi_0 = 0 (6 parameters) and comparing **out of sample**, leave-one-quarter-out:

| sample | n | LOO rel-RMSE, phi_0 free | LOO rel-RMSE, phi_0 = 0 | restricted phi (0, phi_1, phi_2, phi_3) | restricted mean lag |
|---|---|---|---|---|---|
| 2021Q2+ | 21 | **2.95%** | 3.30% | (0, 0.866, 0.134, 0.000) | 1.13 |
| 2022Q1+ | 18 | **1.45%** | 2.30% | (0, 0.658, 0.231, 0.111) | 1.45 |
| 2023Q1+ | 14 | **1.28%** | 1.74% | (0, 0.313, 0.687, 0.000) | 1.69 |

**Reading it honestly.** The free fit wins out of sample in all three windows, so this is not just the extra parameter buying in-sample fit. But the phi vector itself is badly identified — the three windows give wildly different shapes (0.23/0.60/0.17/0.00 versus 0.41/0.18/0.36/0.06 versus 0.39/0.04/0.57/0.00) because consecutive GBV quarters are highly collinear. What **is** stable across windows is (i) phi_0 is materially positive, and (ii) the implied mean lag is **0.95 to 1.18 quarters, shorter than the 1.33 that a 2/3-1/3 kernel implies**. Conditional on phi_0 = 0, the restricted fits recover mean lags of 1.13 to 1.69, straddling 1.33 — so the published kernel is a good description of the data *given the assumption that same-quarter bookings do not reach revenue*, and a worse one without it.

**What this does to the memo's first sentence.** The premise "management can already see essentially all of the quarter it is about to guide" was pre-registered as falsifiable and it is weakened. At the 5 November guide date for 4Q26, the 2/3-1/3 kernel says 100% of the revenue driver is printed. The lag polynomial says roughly **0.23-0.41 of it is not**, because it is same-quarter GBV that will be booked between 5 November and 31 December. Recommended wording: *"the two lagged GBV quarters that drive the great majority of 4Q26 revenue are already printed when management guides on 5 November; a lag-polynomial fit puts 23-41% of weight on within-quarter bookings, with a wide and window-dependent confidence set, so the claim is 'most', not 'all'."* Do not write "100% determined". Do not write "82%" either — that number was already struck.

**Caveats I will not hide:** n = 14-21 with 7 parameters and collinear regressors; the softmax parameterisation cannot return exactly zero, so phi_3 = 0.000 means "driven to the boundary"; the bootstrap blocks are length 4 on a series of 14-21, so the intervals are optimistic if anything.

**Do not claim independent confirmation from the h2 bridge conversion file.** It is the same six ratios from the same two columns of the same panel at w = 0.667. Nothing in this package is corroborated by it.

---

## (f) Live objects

### 3Q26 print — no GBV forecast required (`08_live_3q26.csv`)

GBV_2Q26 = 27,200 and GBV_1Q26 = 29,200 are both printed. Base = 2/3 x 27,200 + 1/3 x 29,200 = **27,867M**. Season-Q3 lambda (mean of 17.391, 17.145, 17.182) = **17.239%**.

**27,867 x 17.239% = 4,804M**, q10-q90 4,707-4,903, sd 77M (PIT prior, n_train = 14).
Full-sample prior: 4,832M, q10-q90 4,648-5,024.
Weight sensitivity w in [0.33, 2/3]: 4,804-4,819M.

Against guide-plus-cushion 4,730 x 1.0186 = 4,818M, these are **two constructions 0.3% apart, not three.** Against the Q3 guide range 4,690-4,770 the kernel print sits 0.7% above the top of the range, which is what a +1.86% cushion means.

### 4Q26 print on a GBV_3Q26 grid (`09_live_4q26_grid.csv`), w = 2/3, lambda_Q4 = 12.030%

| GBV_3Q26 (M) | base (M) | print (M) | guide mid (M) at cushion +1.86% |
|---|---|---|---|
| 25,900 | 26,333 | 3,168 | 3,110 |
| 26,000 | 26,400 | 3,176 | 3,118 |
| 26,100 | 26,467 | 3,184 | 3,126 |
| 26,200 | 26,533 | 3,192 | 3,134 |
| **26,300** | **26,600** | **3,200** | **3,141** |
| 26,400 | 26,667 | 3,208 | 3,149 |
| 26,500 | 26,733 | 3,216 | 3,157 |
| 26,600 | 26,800 | 3,224 | 3,165 |
| 26,700 | 26,867 | 3,232 | 3,173 |
| 26,800 | 26,933 | 3,240 | 3,181 |
| 26,900 | 27,000 | 3,248 | 3,189 |
| 27,000 | 27,067 | 3,256 | 3,197 |

No fee step and no FX added — this package owns neither, and **the FX step is an output of this arithmetic and must never be subtracted again.** The architect's central figures (print 3,200M, guide 3,141M at 26,300) reproduce exactly. Registered predictive sd is 51M (1.6%, PIT) — narrower than the 2.6pp the decision document carries, because this object conditions on a *given* GBV_3Q26 and therefore excludes GBV uncertainty; whoever assembles the 4Q26 distribution must convolve this with the GBV_3Q26 distribution rather than quote 1.6%.

### Share of quarter-q revenue whose GBV driver is already printed (`10_ledger_share.csv`)

| as-of | target | GBV printed through | share at w=2/3 | share at w=0.38 |
|---|---|---|---|---|
| pitch date 2026-10-02 | 4Q26 | 2Q26 | **0.333** | 0.620 |
| guide date 2026-11-05 | 4Q26 | 3Q26 | **1.000** | 1.000 |
| guide date 2027-02 | 1Q27 | 4Q26 | 1.000 | 1.000 |
| guide date 2027-05 | 2Q27 | 1Q27 | 1.000 | 1.000 |

This is the volume-determined share the chief of staff asked for, and it makes the pitch-date/guide-date asymmetry impossible to gloss: **at the pitch we know one third of the driver of the quarter we are forecasting; management, three weeks later, knows all of it** — subject to the phi_0 finding above, which says "all of it" should read "most of it". Note the sensitivity is large here and points the other way from everywhere else: at w = 0.38 the pitch-date share is 0.62, not 0.33. That is the one place where the unidentified weight materially changes a claim, and it should be quoted as a range.

---

## Parameter count and pre-registration

`11_parameter_count.csv`, `12_prereg_card.csv`.

| object | free parameters | against |
|---|---|---|
| kernel, published | **5** = 4 seasonal conversions + 1 lag weight (asserted at 2/3, counted anyway) | 23 printed revenue identities (22 usable with both lags) |
| lag polynomial, diagnostic only | 7 = 4 seasonal conversions + 3 free simplex weights | 21 identities |

Pre-registration entries written tonight:

| id | statement | resolves | status |
|---|---|---|---|
| KL-1 | 3Q26 printed revenue lands in [4,707, 4,903] M (q10-q90, PIT) | 2026-11-05 | open |
| KL-2 | 4Q26 guide midpoint < 3,200 (Zacks, as of 2026-09-04) | 2026-11-05 | open |
| KL-3 | phi_0 is not distinguishable from 0 | tested tonight | **FAILED** — phi_0 = 0.23-0.41, CI excludes 0.02 in all three windows, wins LOO |
| KL-4 | the kernel weight is not identified better than +/- 0.2 | tested tonight | **CONFIRMED, and worse than stated** — argmin ranges 0.13-0.76 across windows; bootstrap CI ~ [0, 0.9] |

---

## What failed, and what I did not do

* **The strict-PIT reproduction of the quoted 1.74 / 2.44 / +0.99 walk-forward figures failed.** See above; they are a full-sample-prior construction.
* **`phi_0 = 0` failed**, as a pre-registered test should be allowed to.
* **The +0.158 slope could not be replicated to the digit** because the regressand and wedge construction are not written down; I re-derived the test and reached the same conclusion with slope +0.233, se 0.252.
* **The published w = 2/3 spec's predictive distribution is rejected by the PIT KS test** (p = 0.0027, W1). The fix was not a wider variance — it was dropping the COVID lambda cells from the estimation window, which removes the bias and fixes the calibration (p = 0.63). The memo should use the ex-COVID estimation window and say so.
* Not built, per the kill list: no Monte-Carlo-only or SARIMAX-only work, no state space, no second FX subtraction, no fee step inside this package, no ADR de-gross-up (that is `fee-takerate`'s, exclusively), no use of the September vendor as a pre-guide Street.
* The `live_4q26_print` object was registered with `strict_windows=False`; see the change request.

---

## Harness change request

**The frozen format cannot express a 2026Q4 forecast object.** README section 2.5 says "`LIVE` requires 2026Q3 or later", but `windows.window_of_target('2026Q4')` returns `[]`, so `validate_registry_frame` rejects `window='LIVE'` with `quarter='2026Q4'`. Since the entire pitch turns on the 4Q26 guide, this is not a corner case. Requested change: map every quarter from 2026Q3 forward to `LIVE` in `window_of_target`, so the validator's behaviour matches its own README.

Local workaround used tonight, recorded here so it is not mistaken for a format invention: `register(sub, strict_windows=False)` for the 4Q26 object only — every other validation (columns, PIT rule, quantile monotonicity, vintage membership) still ran and passed — plus an identical copy at `data/processed/forecast_methods/kernel_lambda/13_local_live_4q26_print_registry_format.csv` in the frozen column set, in case the scorer should not see the registered file.

**Second, smaller:** `baseline_guide_cushion` uses the **median** trailing-8 cushion while the decision document's guide-midpoint arithmetic uses the **mean** (+1.86%). The live objects in this note use the mean, so the 4Q26 guide-midpoint column here and the harness's `guide_cushion` baseline are not the same estimator. Not a bug, but it should be stated once somewhere central rather than in each package's note.
