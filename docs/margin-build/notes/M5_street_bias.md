# M5 — `street-bias`: the Street's EBITDA consensus plus its systematic bias

Slug `M5_street_bias`. Method name `street-bias`. Written 13-14 Sep 2026. Interpreter `py -3.13`.
Rebuild: `py -3.13 analysis/src/margin_build/M5_street_bias/run.py` (exit 0), then
`py -3.13 analysis/src/margin_build/10_harness_margin/score.py`.

## Bottom line

1. **The pre-registered pass line FAILED for all three objects and all six specs.** It required beating
   the raw `baselines-margin__street` object on adjusted-EBITDA $ **and** margin at **h = 0 and h = 1**, in
   W1 and W2, on both weightings — 8 cells. The best objects pass 4 of 8. **Every failure is at h = 1.**
2. **At h = 0 the Street is beatable, and by a lot.** `dispersion_conditioned` (spec `rw_hl4`) cuts the
   margin MAE from 1.59 to **1.33 pt in W1** (n 14) and from 1.31 to **0.74 pt in W2** (n 10); recency-weighted
   0.66x and 0.56x. `street_plus_flowthrough` (`rw_hl4`) cuts the $ MAE from $65.3M to **$43.1M** in W1 and
   from $58.1M to **$33.8M** in W2 (rw 0.55x and 0.52x). Four (object, spec) pairs beat Street in all four
   h = 0 cells on both weightings: `dispersion_conditioned` x {`rw_hl4`, `rw_hl4_med`, `rw_hl4_usd`} and
   `street_plus_flowthrough` x `rw_hl4_med`. All of them also clear `seasonal_naive` (ratios 0.35-0.78) and
   carry `survives_both_windows = True` on the harness scoreboard.
3. **At h = 1 there is no bias to harvest, only noise.** The pre-guide next-quarter Street error has mean
   +0.21 pt (W2, n 10) with sd 1.94 and flips sign: the guide that arrives days later moves it -9.6% to +4.5%.
   Every bias correction at h = 1 makes MAE worse (ratios 1.05-4.10). This is the honest reason the pass line fails.
4. **A supplementary (non-registrable) test rescues 4Q26.** The 4Q26 consensus we hold *today* is not a
   pre-guide h = 1 number: it is five weeks **after** the 6 Aug guide. The post-guide (D+5td) h = 1 Street
   under-calls the margin by **+1.11 pt** on average in W2 (n 10, sd 1.61, 9/10 beats; last 8: +0.88, sd 0.73,
   8/8). Correcting it beats the raw post-guide Street on $ (MAE ratio 0.85 W1 / 0.85 W2; rw 0.66 / 0.64) but
   **not** on margin points (1.30 / 1.12). It cannot be registered — the value is stamped after the vintage
   date and fails the harness PIT rule — so it is a labelled side table, not a scored object.
5. **LIVE (11 Sep 2026 vintage).** Composite of the four h = 0-validated specs: **3Q26 adjusted EBITDA
   $2,412M (range $2,384-2,436M), margin 50.19% (50.03-50.30%)** against the Street's $2,361.5M / 49.78%.
   That is a beat of **+$51M / +0.41 pt**, and **P(EBITDA beat) = 0.64** (margin beat 0.62) on the team's
   base revenue path. This is a *small* beat by ABNB's history, and deliberately so: analyst dispersion on
   3Q26 is at a record low (sd/mean 0.0085 vs a recency-weighted reference of 0.0497), and dispersion is the
   one conditioning variable that works (slope +28 pt of surprise per unit of sd/mean, p 0.005, n 19).

## Pre-registration (written before any fit)

`data/processed/margin_build/M5_street_bias/M5_prereg.json`, timestamped on disk before `build.py` ran.

* **Objects** `street_plus_bias`, `street_plus_flowthrough`, `dispersion_conditioned`; **targets**
  `adj_ebitda_musd`, `adj_ebitda_margin_pct`.
* **Pass line.** Beat `baselines-margin__street` on MAE for both targets, at h = 0 **and** h = 1, in W1
  **and** W2, on both weightings (`mae` and `rw_mae`), PIT replay, matched quarters. Any failing cell fails
  the object; a failure is written up, not deleted.
* **Constants fixed before fitting:** half-life 4 q; bias shrinkage `kappa_b` = 2.0 effective observations at
  zero; flow-through prior `m0` = 0.45 with `kappa_m` = 4.0; dispersion-ratio cap [0.5, 2.0]; residual pool
  last 12 PIT errors, min 3, else the harness fallback (10% relative / 3.0 pp).
* **Estimation pool starts 2022Q1**, declared in advance: 2021 is the COVID re-opening regime (the Street
  carried a -50.7% margin estimate for 1Q21 and the realised surprise was +44.0 pt — WS03's table), and
  averaging that into a 2024 bias is not a judgement about the same object. `rw_hl4_from21` is the registered
  sensitivity that keeps 2021. **It is materially worse everywhere** (margin ratios 1.22-1.90 at h = 0),
  so the pre-registered choice is validated, not assumed.
* **Declared specs** (all registered, both replays): `rw_hl4` (primary), `ew`, `rw_hl4_usd`, `ew_usd`,
  `rw_hl4_med` (recency-weighted median, declared in advance as the robust variant), `rw_hl4_from21`.
* **Declared limitation.** Street quarterly consensus exists at h = 0 and h = 1 only (WS03 roles
  `guided_q_pre_guide` / `next_q_pre_guide`), so there is no h = 2 backtest row. LIVE 1Q27-4Q27 uses a Street
  quarterly path allocated from the FY27 consensus with the harness PIT seasonal shares (spec suffix
  `_fyalloc`); those rows never enter a scored backtest cell.

## Method

Let `S(v, q)` be the LSEG mean for quarter `q` stamped at vintage `v` (WS03 / `street_margin_pit.csv`,
`street_as_of` = the LSEG calc date, always <= `v`), `h` the horizon, and `P(v, h)` the set of past
(vintage, quarter) pairs at the **same horizon** whose target quarter printed on or before `v` and whose
quarter is >= 2022Q1. Weights `w_i = 0.5^((t_last - t_i)/4)` (spec `ew`: `w_i = 1`), `n_eff = sum w_i`.

**1. `street_plus_bias`** — `E(q) = S_E(v,q) * (1 + b_pct)` (or `+ b_usd` for the `_usd` specs) and
`M(q) = S_M(v,q) + b_pt`, where for each unit
`b = sum(w_i s_i) / (n_eff + 2)` (shrunk toward zero; `rw_hl4_med` uses the weighted median in the numerator).
Percentage surprises are computed only where the Street EBITDA is positive. Free parameters: the bias and the
shrinkage constant = **2** (+1 residual sd).

**2. `street_plus_flowthrough`** — weighted OLS `s_usd_i = a + m * r_usd_i` on `P(v,h)` (`r` = the realised
$ revenue surprise), then `m* = (n_eff * m_hat + 4 * 0.45) / (n_eff + 4)` and `a* = shrunk residual mean`.
`E(q) = S_E(v,q) + a* + m* * (Rev_team(v,q) - S_R(v,q))`, `M(q) = 100 * E(q) / Rev_team(v,q)`.
`Rev_team` is the harness PIT revenue leg (`revenue_forecast_pit`: guide cushion, else naive) at backtest
vintages and the WS06 v2b path (bridge v3 for 3Q26/4Q26) at LIVE, with base / bear / bull columns.
Free parameters: `a`, `m`, `m0`, `kappa_m`, `kappa_b` = **5** (+1).

**3. `dispersion_conditioned`** — object 1 with `b` and the residual sd multiplied by
`clip(disp(v,h) / disp_ref(v,h), 0.5, 2.0)`, `disp = EBITDA sd / mean` at the vintage (WS03
`03_consensus_at_dates.csv`) and `disp_ref` the recency-weighted mean of `disp` at past vintages at the same
horizon. Free parameters: bias, shrinkage, and the two cap bounds = **4** (+1).

Quantiles q05-q95 are Gaussian on the object's own walk-forward residual pool (same object / target /
horizon / spec): PIT = the last 12 errors whose target quarter printed before the vintage; full_sample = all
realised errors. Relative errors for `adj_ebitda_musd`, additive for the margin — the harness convention.
Both replays are registered for every row.

## Backtest — `data/processed/margin_build/M5_street_bias/M5_backtest_vs_street.csv`

MAE relative to the raw Street baseline (PIT replay, matched quarters; < 1 is better). **h = 0:**

| object | spec | margin W1 (n 14) | margin W2 (n 10) | $ W1 | $ W2 | rw margin W1 / W2 | rw $ W1 / W2 |
|---|---|---|---|---|---|---|---|
| street (raw) | - | 1.592 pt | 1.311 pt | $65.3M | $58.1M | 1.250 / 1.116 | $62.3M / $59.3M |
| `dispersion_conditioned` | `rw_hl4` | **0.835** | **0.567** | **0.810** | **0.865** | 0.656 / 0.557 | 0.717 / 0.720 |
| `dispersion_conditioned` | `rw_hl4_med` | **0.768** | **0.600** | **0.781** | **0.839** | 0.688 / 0.629 | 0.691 / 0.695 |
| `dispersion_conditioned` | `rw_hl4_usd` | **0.835** | **0.567** | **0.848** | **0.748** | 0.656 / 0.557 | 0.750 / 0.718 |
| `street_plus_flowthrough` | `rw_hl4` | 1.043 | **0.753** | **0.660** | **0.581** | 0.907 / 0.830 | 0.545 / 0.524 |
| `street_plus_flowthrough` | `rw_hl4_med` | **0.973** | **0.779** | **0.656** | **0.600** | 0.906 / 0.878 | 0.548 / 0.535 |
| `street_plus_bias` | `rw_hl4` | 1.005 | **0.906** | **0.940** | 1.174 | 0.814 / 0.785 | 0.771 / 0.819 |
| `street_plus_bias` | `rw_hl4_usd` | 1.005 | **0.906** | **0.743** | **0.632** | 0.814 / 0.785 | 0.545 / 0.501 |
| `street_plus_bias` | `ew` | 1.566 | 1.642 | 1.261 | 1.598 | 1.705 / 1.832 | 1.139 / 1.229 |
| `dispersion_conditioned` | `rw_hl4_from21` | 1.417 | 1.218 | 0.813 | 0.896 | 1.056 / 0.990 | 0.717 / 0.733 |

**h = 1 (all fail):** margin ratios 1.05-2.30 (W1) and 1.12-4.10 (W2); $ ratios 1.10-1.88 (W1) and
1.76-4.05 (W2). The best h = 1 object is `dispersion_conditioned rw_hl4_med` at 1.11 / 1.75 on margin.

Verdict file `M5_passline_verdict.csv`: **0 of 18 (object, spec) pairs pass all 8 cells; 4 of 18 pass all
four h = 0 cells.** 144 cells tested in total.

Harness scoreboard rows (`scoreboard_margin.csv`, method `street-bias`, PIT replay, spec `rw_hl4`), for the record:

| object | target | window | h | n | mae | rw_mae | mae_ratio_street | mae_ratio_seasonal_naive | survives_both_windows | n_params |
|---|---|---|---|---|---|---|---|---|---|---|
| dispersion_conditioned | margin_pct | W1 | 0 | 14 | 1.330 | 0.820 | 0.835 | 0.594 | True | 5 |
| dispersion_conditioned | margin_pct | W2 | 0 | 10 | 0.743 | 0.622 | 0.567 | 0.380 | True | 5 |
| street_plus_flowthrough | ebitda_musd | W1 | 0 | 14 | 43.06 | 33.99 | 0.660 | 0.349 | True | 6 |
| street_plus_flowthrough | ebitda_musd | W2 | 0 | 10 | 33.76 | 31.08 | 0.581 | 0.345 | True | 6 |
| street_plus_bias | margin_pct | W2 | 1 | 9 | 2.158 | 1.579 | 2.174 | 1.368 | False | 3 |

(`n_params` on the scoreboard is the declared count + 1 for the fitted residual sd.)

**Which weighting goes in the pitch: recency-weighted, decisively.** `ew` is worse than the raw Street on
margin in every h = 0 cell (1.12-1.64); `rw_hl4` is better in three of four. The beat has been shrinking
monotonically (2021 +17.2 pt, 2022 +5.2, 2023 +2.1, 2024 +2.8, 2025 +1.1, 1H26 +0.7 — WS03), so an
equal-weighted average of the surprise is a forecast of 2022, not of 2026.

## What failed, and why

* **h = 1, every object, every spec.** The object of a bias correction is a stable mean. At h = 1 the
  pre-guide Street has a W2 mean error of +0.21 pt against a sd of 1.94 — a signal-to-noise ratio of 0.11,
  versus +1.13 / 1.41 at h = 0 (0.80). Worse, the h = 1 error changes sign by era (W1 bias -0.66 pt, W2
  +0.28 pt on the harness scoreboard) because the guide that lands days later can cut the number by up to
  9.6% (2024) or lift it 4.5% (2026). A recency-weighted estimator chases that sign. **This is a real
  negative result and it kills the naive "just add the beat to next quarter" trade.**
* **`ew` and `rw_hl4_from21` fail the level test on margin** even at h = 0 — the 2021-22 beats are a
  different animal and any estimator that keeps their weight over-forecasts 2025-26 by 1-2 pt.
* **`street_plus_bias` fails on $ in W2 at h = 0** (1.17) with the percentage parameterisation, because a
  percentage beat estimated across Q1s (EBITDA $400-500M) and Q3s ($2.0B+) is not one parameter. The
  `_usd` parameterisation fixes it (0.632) but then over-corrects the margin. Only the dispersion scaling
  makes the two units agree.
* **Calibration, all objects.** `cov80 = cov90 = 1.00` in every scored cell: the intervals are far too wide,
  because the PIT residual pool still contains the 2022-23 errors. The points are usable; **the quantiles
  are not, and should be replaced by the LIVE sd quoted below or by M2/M4's** if a distribution is needed.
  CRPS for the `$` objects ($73-103M) is worse than the raw Street's ($48-50M) for the same reason.

## Secondary tests (pre-registered) — `M5_secondary_tests.json`

| test | result | reading |
|---|---|---|
| Ljung-Box on the h = 0 margin surprise | n 22: Q(1) 6.18 **p 0.013**, Q(4) 9.22 p 0.056; from 2022Q1 (n 18): Q(1) 4.70 p 0.030, Q(4) 5.31 p 0.257 | The series is *not* white noise, but the structure is a monotone **downward trend in the size of the beat**, not an AR process: within W1 alone (n 14) the lag-1 autocorrelation is 0.14. Power at n <= 22 is low; nothing here is tradeable as an AR(1). |
| Quarter-of-year seasonality of the surprise (one-way ANOVA) | from 2022Q1: F 0.43, **p 0.73** (n 18); W2 era: F 1.06, **p 0.43** (n 10) | **Fails** the pre-registered p < 0.10 gate, as expected. The pooled bias is used; no quarter-of-year term is fitted. Q3 means are +2.11 pt (from 2022) and +0.30 pt (W2 era). |
| FY-floor anchoring | 19 guide dates 2022-2026; over the 15 dates from 2023 the consensus FY margin sits **+0.37 pt** above the floor in force, within 0.5 pt on 12/15 and within 1 pt on 13/15. Over the 10 dates with a numeric level guide: +0.49 pt, 8/10 within 0.5 pt | **Confirms and extends WS03.** The Street reads the floor as the point. FY24 actual beat its floor by 1.4 pt, FY25 by 0.6. |
| Dispersion regression (margin surprise on EBITDA sd/mean at the vintage, h = 0) | signed: slope **+28.3** pt per unit, se 8.8, **p 0.005**, R2 0.38, n 19; |surprise|: +26.6, p 0.006, R2 0.37; from 2022Q1: +17.1, se 8.1, p 0.052, R2 0.23, n 17 | **The one conditioning variable that works.** It is why `dispersion_conditioned` is the best margin object, and why the 3Q26 call is a small beat: today's sd/mean of 0.0085 is the lowest in the sample. |

## Supplementary test, declared after the h = 1 failure — `M5_h1_basis_summary.csv`, `M5_h1_postguide_scoreboard.csv`

The Street value the team actually holds for 4Q26 on 11 Sep 2026 is a *post-guide* number. Comparing the two
bases for the same 21 quarters:

| basis | window | n | mean margin surprise | sd | MAE pt | mean $ | share beats |
|---|---|---|---|---|---|---|---|
| pre-guide (h = 1, registrable) | W1 | 14 | +0.77 | 2.11 | 1.67 | +$34.8M | 50% |
| pre-guide | W2 | 10 | +0.21 | 1.94 | 1.35 | +$11.2M | 40% |
| pre-guide | last 8 | 8 | -0.02 | 1.05 | 0.83 | +$9.5M | 38% |
| **post-guide D+5td** | W1 | 14 | **+1.18** | 1.74 | 1.54 | +$51.5M | 86% |
| **post-guide D+5td** | W2 | 10 | **+1.11** | 1.61 | 1.29 | +$42.6M | 90% |
| **post-guide D+5td** | last 8 | 8 | **+0.88** | 0.73 | 0.88 | +$40.3M | **100%** |

A PIT-shrunk bias applied to the post-guide number beats it on $ (MAE ratio 0.86 W1 / 0.85 W2; rw 0.66 / 0.64,
n 14 / 10) and loses on margin points (1.30 / 1.06 rw W1; 1.12 / 1.01 rw W2) — the bias and the noise are the
same size once the estimator has to be built PIT. **Use the direction, not the point.**

## LIVE forecasts (vintage 2026-09-11) — `M5_live_forecasts.csv`, `M5_card_composite.csv`

Parameters at the LIVE vintage (spec `rw_hl4`, `M5_parameters_by_vintage.csv`): h = 0 pool n 18, n_eff 6.01,
raw bias +1.41 pt / +8.41%, shrunk **b_pt +1.057 pt, b_pct +6.29%, b_usd +$44.7M**; flow-through
`m_hat` 0.473 -> shrunk **m 0.464**, **a +$15.9M**; dispersion 0.0085 vs reference 0.0497 -> ratio 0.083,
**clipped to the 0.50 floor** (the cap binds; uncapped the 3Q26 margin call would be 49.9%, i.e. essentially
the Street). h = 1: b_pt +0.592, m 0.525, a -$1.65M, disp ratio 0.645.

Composite of the four h = 0-validated (object, spec) pairs — `dispersion_conditioned` x {`rw_hl4`,
`rw_hl4_med`, `rw_hl4_usd`} and `street_plus_flowthrough` x `rw_hl4_med`:

| period | metric | M5 point | spec range | Street (LSEG 11 Sep) | surprise | P(beat) | validated? |
|---|---|---|---|---|---|---|---|
| 3Q26 | adj EBITDA | **$2,412M** | 2,384 - 2,436 | $2,361.5M (n 36, sd 20.0) | **+$51M** | **0.64** | yes, h = 0 |
| 3Q26 | adj EBITDA margin | **50.19%** | 50.03 - 50.30 | 49.78% | **+0.41 pt** | **0.62** | yes, h = 0 |
| 4Q26 | adj EBITDA | $932M | 915 - 942 | $913.7M (n 36, sd 26.5) | +$18M | 0.58 | **no** (h = 1 fails) |
| 4Q26 | adj EBITDA margin | 29.16% | 28.79 - 29.29 | 28.90% | +0.26 pt | 0.55 | **no** (h = 1 fails) |

Per-object LIVE points (spec `rw_hl4`, base revenue): 3Q26 `street_plus_bias` $2,510M / 50.83%,
`dispersion_conditioned` $2,436M / 50.30%, `street_plus_flowthrough` $2,405M / 50.07%; 4Q26 $957M / 29.49%,
$942M / 29.28%, $921M / 28.97%. The `street_plus_bias` number is the one to discard: it is the object that
fails W2 on $ and it is applying the pre-2025 beat unconditionally.

Scenario spread on `street_plus_flowthrough` (`rw_hl4`), driven entirely by the WS06 v2b revenue path
(3Q26 base $4,804M / bear $4,755M / bull $4,878M vs Street revenue $4,744.3M):
3Q26 EBITDA $2,382M (bear) / $2,405M (base) / $2,439M (bull), P(beat) 0.57 / 0.64 / 0.73; margins 50.10 /
50.07 / 50.01 — note the margin barely moves, because the incremental margin on the revenue surprise (0.46)
is **below** the level margin (0.50), so upside revenue is very slightly margin-dilutive in this method.

**The two LIVE vintages, and a stamp caveat that matters.** Every backtested h = 0 Street value is a
*pre-guide* number (stamped the day before the guide, ~3 months before that quarter prints). The 11 Sep row
is not: it is five weeks **after** the 6 Aug guide, so the post-guide revision has already happened
(3Q26 consensus EBITDA $2,323.8M -> $2,361.5M, +1.6%; margin 50.41% -> 49.78% as revenue was marked up from
$4,610M to $4,744M). Running the same four validated specs on the backtest-consistent **6 Aug pre-guide**
vintage gives 3Q26 adjusted EBITDA **$2,390M** (range 2,346-2,428) and a margin of 50.79% on the then-Street
revenue. **The dollar answers agree within $22M** ($2,390M vs $2,412M) — that is the robustness check that
matters, and on the team's revenue base of $4,804M they are 49.75% and 50.21%. I quote the 11 Sep vintage
because it uses the freshest consensus and because applying a bias estimated on pre-guide values to a
pre-guide value that is now five weeks stale would double-count part of a revision we have already observed.
The 6 Aug read is the aggressive bookend.

Quarterly LIVE rows for 1Q27-4Q27 are registered under spec suffix `_fyalloc` (Street allocated from the
FY27 consensus with PIT seasonal shares — `M5_street_fy27_allocation.csv`, EBITDA shares 9.1 / 22.9 / 48.8 /
19.1%). **They are not backtested and the h >= 2 bias borrows the failed h = 1 estimate. Do not quote them.**

Annuals — `M5_street_bias_annual_forecasts.csv`:

| FY | basis | M5 EBITDA | M5 margin | Street | note |
|---|---|---|---|---|---|
| FY26 | 1H26 actual $1,780M + 3Q26 (validated) + 4Q26 (not) | **$5,125M** | **35.92%** on revenue $14,268M | $5,053.7M / 35.62% | vs management's ">= 35.5%" floor: +0.4 pt. FY24 beat its floor by 1.4 pt, FY25 by 0.6 |
| FY27 | 4 x `_fyalloc` quarters | $5,764M (flowthrough) to $6,042M (bias) | 36.42% - 38.17% | $5,766.1M / 36.45% | **not validated**; the spread is the method breaking down at h >= 2 |
| FY28 | — | not produced | | $6,602.7M / 37.65% | M5 has no object at this horizon; see M1/M3 |

## Corrections to existing work

* **WS03 §4** reports the lag-1 autocorrelation of the h = 0 margin surprise as 0.26 (n 22). Recomputed on
  the same 22 quarters, demeaned, it is **0.496** (Ljung-Box Q(1) 6.18, p 0.013); lag-4 is 0.191, not 0.15.
  The *conclusion* in WS03 is unchanged and I endorse it — there is no exploitable AR structure — but the
  reason is different: the apparent autocorrelation is the downward trend in the size of the beat, and
  within W1 alone the lag-1 coefficient is 0.14. Source: `M5_surprise_panel.csv`, `M5_secondary_tests.json`.
* WS03's FY-floor tally (8/10 within 0.5 pt) is confirmed on the same 10 numeric-level guides (+0.49 pt mean)
  and extends to 12/15 within 0.5 pt when the 2023 y/y-anchored guides are included.
* No file outside `docs/margin-build/`, `analysis/src/margin_build/M5_street_bias/`,
  `data/processed/margin_build/{M5_street_bias,registry}/` and `analysis/figures/margin_build/` was touched.
  No LSEG raw file was read: this package consumes WS03's derived, date-stamped tables only.

## Tests counted

1 pre-registered pass line (144 cells: 18 object-spec pairs x 2 targets x 2 horizons x 2 windows x 2
weightings — **0 pass, 4 pairs pass the four h = 0 cells**), 4 pre-registered secondary tests (Ljung-Box,
seasonality ANOVA, FY-floor anchoring, dispersion regression x 3 specifications), 1 supplementary test
declared after the h = 1 failure (post-guide h = 1 basis, 4 scored cells). Free parameters: 2 / 5 / 4 (+1
residual sd each); `param_obs_ratio` 0.21-0.67 on the scoreboard.

## For the model

| name | value | unit | source |
|---|---|---|---|
| `m5_3q26_ebitda` | **2,412** (range 2,384-2,436; sd 145) | $M | `M5_card_composite.csv`, 4 validated specs, vintage 2026-09-11 |
| `m5_3q26_margin` | **50.19** (range 50.03-50.30; sd 1.33) | % | same |
| `m5_3q26_surprise_vs_street` | +51 / +0.41 | $M / pt | vs LSEG $2,361.5M / 49.776% |
| `m5_p_beat_3q26_ebitda` | **0.64** (margin 0.62); bear 0.57, bull 0.73 | prob | `M5_prob_beat.csv` |
| `m5_4q26_ebitda / margin` | 932 / 29.16 — **unvalidated (h = 1 fails)** | $M / % | `M5_card_composite.csv` |
| `m5_fy26_ebitda / margin` | 5,125 / 35.92 on revenue 14,268 | $M / % | `M5_street_bias_annual_forecasts.csv` |
| `street_bias_h0_pt` (LIVE, shrunk) | +1.057 | pt | `M5_parameters_by_vintage.csv`, spec rw_hl4 |
| `street_bias_h0_pct` (LIVE, shrunk) | +6.29 | % | same |
| `dispersion_ratio_3q26` | 0.50 (cap; raw 0.171 = 0.0085 / 0.0497) | ratio | same |
| `flowthrough_m` (LIVE, shrunk) | **0.464**; intercept `a` +$15.9M | ratio, $M | same; prior m0 0.45, `m_hat` 0.473 |
| `street_surprise_h0_W2_mean / sd` | **+1.126 / 1.403** (W1 +1.219 / 1.641; rw +1.03 / +1.10) | pt | `M5_surprise_panel.csv`. **This is the *pre-guide* consensus for the quarter being guided** (stamped at the guide date, ~3 months before that quarter prints), not WS03's at-print consensus (+1.70 W2, stamped one day before the print). Both are correct; they are different objects and M5 is built on the first because that is what the harness `street` baseline registers. |
| `street_surprise_h1_postguide_W2_mean / sd` | +1.11 / 1.61 (last 8: +0.88 / 0.73) | pt | `M5_h1_basis_summary.csv` |
| `dispersion_slope` | +28.3 pt of surprise per unit EBITDA sd/mean (se 8.8, p 0.005, n 19) | pt | `M5_secondary_tests.json` |
| `fy_floor_gap` | +0.37 pt mean, 12/15 within 0.5 pt | pt | same |
| free parameters | 2 (`street_plus_bias`), 5 (`street_plus_flowthrough`), 4 (`dispersion_conditioned`), +1 residual sd each | | |

**Do not use M5's quantiles** (cov80 = 1.00 everywhere). Use the point and the LIVE sd above, or another
method's distribution.

## For the 5 Nov card

* **The Street is at $2,361M / 49.8% for 3Q26 (n 36, sd $20M, high-low $2,323-2,420M).** M5 says the print
  lands at **$2,412M / 50.2%** — a beat of **+$51M / +0.4 pt** — with **P(beat) 0.64**. A print above
  ~$2,420M clears every published estimate; that is roughly our 65th percentile, not our base case.
  Re-run from the 6 Aug pre-guide vintage (the stamp the backtest actually validates) the answer is
  $2,390M, so the dollar call is $2,390-2,412M either way.
* **"What is the Street missing" is smaller than it has been, and that is the point.** The Street has
  under-called the margin at 21 of 22 prints, but the beat has decayed from +17 pt (2021) to +0.43 pt over
  the last four prints, and 3Q dispersion is at a record low (sd/mean 0.0085). The pitch line is
  *"the Street is still 0.3-0.5 pt light on 3Q margin, not 1.5-2 pt"* — a bias-correction model that keeps
  the old beat (`street_plus_bias`: 50.8% / $2,510M) is the thing the backtest rejects.
* **Do not claim an edge on the 4Q26 guide from this method.** At h = 1 the bias correction is worse than
  doing nothing in every backtest cell. What M5 does support: the post-guide 4Q26 consensus has under-called
  the margin in 9 of the last 10 quarters by +1.1 pt on average (last 8: +0.9 pt, 8/8), so the direction on
  4Q26 is up from 28.9%, with a sd of the same size as the bias. Quote a tilt, not a number.
* **FY26 is the number management will be judged on.** Street 35.62% sits 0.11 pt above the ">= 35.5%" floor;
  M5 gets to **35.9%**. The FY-floor test (12/15 within 0.5 pt over 2023-26) says the Street will not move off
  the floor until the guide moves, and management has cleared its floor by 1.4 pt (FY24) and 0.6 pt (FY25).
  A 5 Nov FY26 statement of "at least 35.5%" reiterated is the base case and is not a negative surprise.
* **Direction of the revenue link:** in this method a revenue beat is *margin-neutral to very slightly
  dilutive* (incremental margin on surprises 0.46 vs a level margin of 0.50). Do not pair "revenue beats" with
  "margin beats" as if they were the same trade — the beat is cost-side (intercept +$16M PIT, +$36-39M in
  WS03's W1/W2 regressions).

## Files written

Scripts: `analysis/src/margin_build/M5_street_bias/{build.py, analyse.py, figures.py, run.py, README.md}`.
Processed (`data/processed/margin_build/M5_street_bias/`): `M5_prereg.json`, `M5_grid_all_vintages.csv`,
`M5_parameters_by_vintage.csv`, `M5_surprise_panel.csv`, `M5_backtest_vs_street.csv`,
`M5_passline_verdict.csv`, `M5_h1_preguide_vs_postguide.csv`, `M5_h1_basis_summary.csv`,
`M5_h1_postguide_backtest.csv`, `M5_h1_postguide_scoreboard.csv`, `M5_live_forecasts.csv`,
`M5_live_all_specs.csv`, `M5_prob_beat.csv`, `M5_card_composite.csv`,
`M5_street_bias_annual_forecasts.csv`, `M5_street_current.json`, `M5_secondary_tests.json`,
`M5_street_fy27_allocation.csv`.
Registry: `data/processed/margin_build/registry/street-bias__{street_plus_bias, street_plus_flowthrough,
dispersion_conditioned}.csv` (1,296 rows each; 6 specs x 2 replays, plus the `_fyalloc` LIVE specs).
Figures: `analysis/figures/margin_build/M5_street_bias_{surprise_and_bias, mae_ratio, dispersion}.png`.
Note: this file.

## RESUME

M5 is complete and rebuildable (`py -3.13 analysis/src/margin_build/M5_street_bias/run.py`, exit 0;
rescore with `.../10_harness_margin/score.py`). The next agent should (a) treat only the **h = 0** objects as
usable — quote 3Q26 $2,412M / 50.19% and the +0.4 pt / +$51M surprise with P(beat) 0.64, and delete
`street_plus_bias` from any card; (b) **replace M5's quantiles** with M2's or M4's before any distribution is
shown — cov80 is 1.00 in every cell, so the intervals are useless even though the points are the best on the
board at h = 0; (c) for the 4Q26 guide line, use the post-guide h = 1 direction (+0.9 to +1.1 pt, 9/10 beats)
as a tilt only, and consider building a proper post-guide vintage in the harness (a `guide_date + 5td`
vintage) if the team wants that number registered — it needs a frozen-harness change request, logged here as
request 3 alongside the two in the margin harness README; (d) re-run M5 if WS03 refreshes the LSEG pull after
12 Sep (nothing else in this package depends on a raw pull), and re-run after any change to
`06_revenue_path_3q26_4q27_v2b.csv`, which is the only external input to `street_plus_flowthrough` at LIVE;
(e) at synthesis, note that M5's dispersion finding (+28 pt of surprise per unit of sd/mean, p 0.005) is the
cleanest cross-check on M1's 51.6% and M2's 48.1% for 3Q26 — M5's 50.2% sits between them and is the only one
of the three anchored to a number the market has actually published.
