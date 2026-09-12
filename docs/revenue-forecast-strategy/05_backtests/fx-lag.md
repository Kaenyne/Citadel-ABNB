# fx-lag — the FX proxy: how far ahead does today's FX hit revenue, and how much of 4Q26 / FY27 FX is already determined

Package: `analysis/src/forecast_methods/fx_lag/`
Data: `data/processed/forecast_methods/fx_lag/`
Registry: `fx-lag__fx_rev_next_q_h2`, `fx-lag__fx_rev_next_q_h3`, `fx-lag__live_fx_schedule`
Run date 2026-09-11. Harness format v1.0 (frozen) obeyed; no harness or L0 file touched.

## Exact commands

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fx_lag/run.py
# exit code 0, ~25 s, 28 data files (27 CSV + 00_summary.json) + 3 registry files
```

---

## 0. The one-paragraph answer

**Theo's "two quarters ahead" and the architect's "booking-date FX is already inside the lagged GBV base" are the same statement about the same convolution, but the data will not support a lag as long as two quarters, and it rejects the Phi kernel as a *reduced-form* description of the disclosed revenue-FX series.** On the 14 letter-rounded observations the 95% confidence set for the effective lag of the revenue-FX contribution is about **0.0 to 0.9 quarters** (gross-of-hedge) or **0.0 to 1.2 quarters** (stated), point estimate **0.4 quarters**. H0 — weights equal 0.56 x (0, 2/3, 1/3), i.e. the architect's Phi kernel at the disclosed non-USD revenue share — is **rejected**: LR 16.8, df 3, p 0.0008 on gross; LR 10.2, p 0.017 on stated. Theo's pure lag-2 at 0.56 is rejected harder (p < 0.0005 on both). *But* — and this is the reconciliation — when you condition on the information set that actually exists at a guide date, where only about 39% of the guided quarter's FX has been observed, the Phi-implied lagged specification is the **best point-in-time forecaster on both windows** (RMSE 0.99pp, bias +0.1pp, versus 1.49-1.77pp for the contemporaneous and free-weight specifications). So: FX hits *revenue* with a short lag, but it hits *the number management can see when it guides* with the long one. Both men are right about different conditioning sets, and the sentence that survives cross-examination names which.

---

## 1. Stage (a) — the booking-date basket X^B. PASSED.

Built from `10_fx_daily.csv` (9 FRED bilaterals, USD per unit, 2018-01-02 to **2026-08-28** — note the daily file ends 28 Aug, not 11 Sep; every "as of today" number below is really as of 28 Aug and is labelled so), currency weights from `10_fx_basket.csv` (**judgement weights**, vintage = the overnight build, reproduced verbatim in `01b_basket_weights_used.csv`, not fitted), regional weights = **trailing-4-quarter filed regional revenue** from the L0 spine `L0_exact_regional_revenue.csv` (PIT-legal: every cell carries a `knowable_from`).

Reconciliation against the published `10_fx_basket.csv` headline values (`03_basket_reconciliation.csv`, n = 15 cells):

| series | 1Q26 pub / rebuilt | 2Q26 pub / rebuilt | 3Q26 pub / rebuilt | max abs diff |
|---|---|---|---|---|
| na | 0.70 / 0.70 | 0.25 / 0.25 | 0.02 / 0.02 | 0.004 pp |
| emea | 9.51 / 9.51 | 1.93 / 1.93 | -1.13 / -1.13 | 0.004 pp |
| latam | 12.36 / 12.36 | 11.43 / 11.44 | 6.39 / 6.39 | 0.007 pp |
| apac | 4.91 / 4.91 | 2.73 / 2.73 | 1.47 / 1.47 | 0.004 pp |
| **global revenue-weighted** | 5.60 / **5.67** | 2.19 / **2.27** | 0.32 / **0.36** | 0.08 pp |

All nine currency y/y series reproduce the published file to the printed precision. The four regional baskets reproduce to <0.01pp. The global basket differs by up to 0.08pp because the overnight build's regional revenue weights are not published; mine are the L0 trailing-4 filed shares (1Q26: na 0.42 / emea 0.39 / latam 0.10 / apac 0.10). **Acceptance test A: PASSED**, with the 0.08pp global difference stated.

Side check, unrequested but free: the panel reproduces the architect's conversion table exactly — 1Q23 12.803, 2Q23 13.724, 3Q23 17.391, 4Q23 11.946, 1Q24 13.034, 2Q24 13.449, 3Q24 17.145, 4Q24 12.117, 1Q25 12.325, 2Q25 13.946, 3Q25 17.182, 4Q25 12.026, 1Q26 12.612, 2Q26 13.736. Every published value matches to the third decimal.

Target-series check: `gross_fx_ex_hedge_pp` has **n = 14** (1Q23-2Q26), **population sd 2.3373 pp** (the spec's 2.337), and the *stated* series has **six exact zeros** (1Q24, 2Q24, 3Q24, 4Q24, 2Q25, 3Q25). **PASSED.**

---

## 2. Stage (b) — ADR FX contemporaneously, and the `05_fx_fits.csv` reproduction

`05_stage_b_adr_contemporaneous_fits.csv`. Scored with the interval likelihood on the letter-rounded one-decimal ADR points (+/-0.05); OLS reported alongside because that is what the prior art used.

| target | driver | window | n | my slope | pub slope | my r | pub r | my LOO | pub LOO | reproduces |
|---|---|---|---|---|---|---|---|---|---|---|
| adr_fx | eurusd | post22 | 14 | 0.4602 | 0.4602 | 0.9721 | 0.9721 | 0.5722 | 0.5722 | **YES** |
| adr_fx | usd_broad | post22 | 14 | -0.5925 | -0.5925 | -0.9508 | -0.9508 | 0.7650 | 0.7649 | **YES** |
| adr_fx | eurusd | ex21 | 17 | 0.4512 | 0.4512 | 0.9901 | 0.9901 | 0.5071 | 0.5072 | **YES** |
| adr_fx | usd_broad | ex21 | 17 | -0.7154 | -0.7154 | -0.9641 | -0.9641 | 0.9906 | 0.9905 | **YES** |
| rev_fx | usd_broad | post22 | **14** | -0.5023 | -0.5348 | -0.7801 | -0.7959 | 1.6037 | 1.6342 | **NO** |
| rev_fx | eurusd | post22 | **14** | 0.3466 | 0.3593 | 0.7084 | 0.7141 | 1.7856 | 1.8468 | **NO** |
| adr_fx | basket_global | post22 | 14 | 0.8717 | — | 0.9617 | — | 0.6674 | — | new |
| rev_fx | basket_global | post22 | 14 | 0.7467 | — | 0.7971 | — | 1.5610 | — | new |

**What failed:** the four ADR rows reproduce to the fourth decimal; `post22` is confirmed to mean **1Q23-2Q26**. The two `rev_fx` rows do **not** — the repo reports n = 13 where the same window gives 14 non-null revenue-FX points, and no contiguous 13-quarter window reproduces slope -0.5348. One observation is dropped somewhere that the file does not record. The difference is immaterial to the conclusions (r 0.78 vs 0.80) but it is a real, unreproduced number and I am not quoting the repo's rev_fx fit anywhere.

The interval likelihood recovers the OLS coefficients almost exactly on the ADR target (calibration slope 1.000 on all four rows) because the ADR rounding half-width of 0.05pp is small against a residual sd near 0.5pp. It matters a great deal on the revenue target, where the half-width is 0.5pp against a residual sd near 1.0pp: the in-sample interval RMSE is 0.56pp against a point RMSE of 0.93pp, i.e. **40% of the apparent error is rounding, not model error.** Anyone scoring this series with a Gaussian point likelihood is fitting the rounding.

---

## 3. OBJECT A — the lag confidence set and the H0 test. **The headline deliverable.**

Specification: `mu_q = a0 b_q + a1 b_{q-1} + a2 b_{q-2}`, `a >= 0`, scored on `[x-0.5, x+0.5]`; scale `s = a0+a1+a2`, weights `w = a/s`, effective lag `= w1 + 2 w2`. Four free parameters (a0, a1, a2, sigma). Confidence set = the grid points with `2(LLmax - LLprofile) <= chi2(0.95, 3) = 7.815`, sigma profiled out, over a 37^3 = 50,653-point grid at 0.025 spacing.

`06_object_a_summary.csv`, n = 14 (1Q23-2Q26) on both targets:

| | gross-ex-hedge | stated |
|---|---|---|
| a0 / a1 / a2 (point) | 0.54 / 0.41 / 0.00 | 0.45 / 0.36 / 0.03 |
| scale (point) | **0.95** | **0.84** |
| weights w0 / w1 / w2 | 0.57 / 0.43 / 0.00 | 0.53 / 0.43 / 0.04 |
| **effective lag, quarters** | **0.43** | **0.50** |
| 95% CS, effective lag | **[0.03, 0.92]** | **[0.00, 1.19]** |
| 95% CS, scale | [0.63, 1.33] | [0.45, 1.30] |
| 95% CS, w0 | [0.15, 0.97] | [0.00, 1.00] |
| 95% CS, w2 | [0.00, 0.41] | [0.00, 0.55] |
| is 0.56 inside the scale CS? | **NO** | yes |
| sigma | 0.88 pp | 1.03 pp |
| interval RMSE (in-sample) | 0.56 pp | 0.69 pp |
| CS size | 6,437 / 50,653 grid points | 10,007 / 50,653 |
| free parameters | 4 | 4 |

Block bootstrap (moving block of 3, 400 reps, `06c`): effective lag 2.5-97.5 percentile **[0.00, 0.66]** gross, **[0.00, 0.90]** stated; scale [0.56, 1.25] gross. The bootstrap is tighter than the likelihood CS and points the same way.

### 3.1 The H0 test — the deliverable the addendum asked for

`06b_object_a_hypothesis_tests.csv`, LR against the free fit, sigma profiled, df 3 (df 2 for the free-scale variant):

| hypothesis | a = | LR (gross) | p (gross) | LR (stated) | p (stated) | in 95% CS? |
|---|---|---|---|---|---|---|
| **H0 architect Phi x 0.56** | (0, 0.373, 0.187) | **16.8** | **0.0008** | **10.2** | **0.017** | **NO / NO** |
| H0b Theo pure lag-2 x 0.56 | (0, 0, 0.56) | 24.7 | 0.0000 | 18.0 | 0.0004 | NO / NO |
| H0c contemporaneous x 0.56 | (0.56, 0, 0) | 12.3 | 0.0065 | 7.5 | **0.058** | NO / **YES** |
| H0d pure lag-1 x 0.56 | (0, 0.56, 0) | 12.9 | 0.0048 | 7.1 | **0.069** | NO / **YES** |
| H0e Phi weights, free scale | (0, 2/3, 1/3) x s | 15.9 | 0.0004 | 9.9 | 0.0072 | NO / NO |

**The answer, stated plainly: the data DO reject H0, on both targets, at 5%.** The architect's Phi kernel is not the reduced-form lag structure of the disclosed revenue-FX series. Freeing the scale does not save it (H0e, p 0.0004 / 0.007), so the rejection is about the *shape*, not the level. Theo's pure two-quarter lead is rejected more strongly still. What the data *cannot* separate is contemporaneous from one-quarter-lagged: on the stated series both H0c and H0d sit inside the confidence set (p 0.058 and 0.069), and their LR difference is 0.4 — one quarter of lag is simply not identified at n = 14.

### 3.2 The over-identification on 0.56 — read this before reading the lag

The fitted scale on the gross series is **0.95, and 0.56 is outside its confidence set [0.63, 1.33]**. Per the addendum's own rule, a fitted scale materially away from the disclosed non-USD revenue share of 0.56 means **the judgemental basket weights are wrong, not that the lag is wrong.** The basket has to move 0.95pp to explain 1pp of disclosed revenue FX, i.e. it understates the true currency exposure by about 70%. Two visible causes: the NA basket carries a 0.90 USD weight and EMEA a 0.05 USD weight, both judgement, which suppress the cross-border legs; and the regional revenue weights are billing-geography shares, not booking-currency shares. On the stated (after-hedge) series the scale is 0.84 and 0.56 *is* inside the CS, which is consistent with hedges removing roughly a fifth of the gross move. **Conclusion: the scale result is a finding about the basket weights and should be carried as a caveat on every basket-derived pp in the programme. It does not rescue or damage H0, because the free-scale variant H0e is rejected too.**

### 3.3 The PIT hazard — stated

The gross-of-hedge target is built as `stated + hedge_effect_on_revenue_growth_pp`, and the hedge reclassification is a **10-Q number filed after the letter and well after the guide**. So the Object-A fit on `gross_fx_ex_hedge_pp` is **explicitly labelled NON-PIT STRUCTURAL**: it is a description of the mechanism, not a forecast, and it is not registered. Everything registered, and every number in section 5, uses the **stated** series, which is disclosed in the letter of the quarter it describes and is therefore unknown at the guide date being forecast — PIT-clean. Both are reported side by side throughout so the reader can see what the hedge adjustment does (it moves the effective lag from 0.50 to 0.43 and the scale from 0.84 to 0.95).

---

## 4. OBJECT B — the wedge IS the recognition lag (directionally; not significant)

`07_object_b_wedge.csv`. Wedge = revenue-FX minus ADR-FX; interval half-width 0.55pp (0.5 revenue integer + 0.05 ADR one-decimal). ADR FX is contemporaneous-at-booking by construction, so if the revenue leg needs a lag and the ADR leg does not, the wedge should load on lags 1-2 and not on lag 0.

| wedge of | n | mean | sd | c_lag0 | c_lag1 | c_lag2 | uni lag0 t / r | uni lag1 t / r | uni lag2 t / r |
|---|---|---|---|---|---|---|---|---|---|
| stated | 14 | -0.24 | 1.57 | **-0.48** | **+0.50** | -0.07 | -0.69 / -0.19 | 1.09 / 0.30 | 1.25 / 0.34 |
| gross-ex-hedge | 14 | 0.00 | 1.43 | **-0.43** | **+0.59** | -0.13 | -0.17 / -0.05 | **1.82** / 0.46 | 1.57 / 0.41 |

**The sign pattern is exactly Theo's**: essentially zero contemporaneous loading (univariate r -0.05 on gross), positive loading on lag 1 (t 1.82) and lag 2 (t 1.57). The wedge is where the recognition lag lives. **But no t exceeds 2 at n = 14**, so this is a *direction*, not a measurement, and it must be quoted as such. The mean wedge on the gross series is 0.00pp with sd 1.43pp: over 14 quarters the revenue and ADR FX points agree on average and differ by about 1.4pp in any given quarter, and the timing of that difference is what the whole argument is about.

---

## 5. OBJECT C — the architect's falsification: PARTIALLY reproduced, conclusion confirmed

Target to reproduce: slope 0.158, se 0.275, t 0.57, n 12, on season-demeaned conversion against the booking-to-check-in remeasurement wedge. `08_object_c_falsification.csv`, 20 rows across 2 samples x 2 wedge definitions x 5 demeaning conventions.

n = 12 (3Q23-2Q26, three season-year cells per season):

| wedge | convention | n | slope | se | t | p |
|---|---|---|---|---|---|---|
| basket | y demeaned ~ x demeaned (**headline**) | 12 | 0.030 | 0.028 | 1.06 | 0.31 |
| basket | y demeaned ~ x raw | 12 | 0.024 | 0.025 | 0.94 | 0.37 |
| basket | y raw ~ x demeaned | 12 | 0.030 | 0.316 | 0.09 | 0.93 |
| basket | y raw ~ x raw | 12 | 0.338 | 0.263 | 1.28 | 0.23 |
| **ADR-FX** | **y raw ~ x raw** | 12 | **0.389** | **0.277** | **1.40** | 0.19 |
| ADR-FX | y demeaned ~ x demeaned | 12 | 0.030 | 0.030 | 1.00 | 0.34 |

**Verdict: PARTIAL.** The sample size reproduces exactly (n = 12). The standard error reproduces to 0.002 on one specific convention — the **undemeaned ADR-wedge** regression gives se **0.277** against the architect's 0.275, which pins down that his regressor variance is the undemeaned ADR-FX wedge. The slope does not reproduce on any of the eight variants tried (0.389 at the matching se, against his 0.158). The architect's exact construction is not recoverable from the documents on disk, and I am not going to guess at it in prose.

**The conclusion reproduces on every single variant.** `|t|` ranges from 0.09 to 1.40 across all 20 rows and **never approaches 2**; p ranges 0.19 to 0.93. The booking-to-check-in remeasurement inside lambda is indistinguishable from zero, exactly as the architect ruled. Extending to n = 14 (1Q23-2Q26) with the interval likelihood on the lambda ratio (half-width about 0.034pp, propagated from the $0.1bn GBV rounding) changes nothing: slope 0.027, t 1.23. **Pre-registered test recorded: |t| must stay under 2 when the 4Q26 cell is added at the 2027-02 print.** At the season-mean lambda of 12.03 the 4Q26 cell sits on the fitted line and moves t by less than 0.1; the test only bites if 4Q26 lambda misses its season mean by more than about 0.5pp.

Regional pass-through weights (1.043 EMEA, 0.623 LatAm, 0.86 APAC, NA not identified because its basket moves less than 1.5pp across the sample) are carried in `08b_regional_passthrough_used.csv` and used only to document the extension; the NA slope of 3.205 is excluded as noise, as its own source file says.

---

## 6. The horse-race — and the reconciliation of the two views

### 6.1 Full-sample LOO (`09_hypothesis_horse_race_loo.csv`, n = 14 each)

Benchmark to beat: the repo's best one-parameter LOO on the post22 window is **1.2868** (rev_fx on `usd_broad_avg01`). **Never 2.3038** — that is the ex21 `eurusd_avg12` row and is not a comparable benchmark.

| spec | params | target = stated | LOO RMSE | target = gross | LOO RMSE |
|---|---|---|---|---|---|
| H0 contemporaneous only | 2 | | 1.47 | | 1.36 |
| H1 repo mean of EUR t-1, t-2 | 3 | | 1.73 | | 1.76 |
| H2 Phi-implied on ADR-FX | 2 | | 1.74 | | 1.84 |
| H2b Phi-implied on basket | 2 | | 1.59 | | 1.71 |
| **H3 free weights lags 0-2** | 4 | | **1.36** | | **1.16** |
| H3b free weights lags 1-3 | 4 | | 1.42 | | 1.43 |
| H4 free weights on ADR-FX lags 0-2 (NON-PIT) | 4 | | 1.52 | | 1.37 |
| BASE naive (last quarter's FX pp) | 0 | | 2.11 | | 2.11 |
| BASE zero | 0 | | 2.27 | | 2.47 |

**You must not read a winner off this table.** At n = 14 the standard error of an RMSE estimate is about RMSE/sqrt(2n) = **0.22 to 0.35pp** (published per row in the file). So 1.16, 1.36, 1.47 and the repo's 1.2868 are **statistically indistinguishable**, exactly as the addendum warned; 1.08, 1.40 and 1.94 would be too. The only separations that clear a standard error are against the baselines: every specification beats naive (2.11) and beats zero (2.27) by 2-4 standard errors. **FX is forecastable; the choice of lag structure is not resolvable at this sample size by LOO.**

### 6.2 Point-in-time expanding window (`09b`, `09c`) — this is the one that matters

Refit at each guide date on filings strictly before it; the guided quarter's own basket is **QTD actual + spot held constant** through the day before the guide (about 39% of the quarter elapsed at a typical guide date); L0 revenue shares filtered on `knowable_from <= vintage`.

| spec | W1 n | W1 RMSE | W1 bias | W1 interval RMSE | W2 n | W2 RMSE | W2 bias | W2 interval RMSE | params |
|---|---|---|---|---|---|---|---|---|---|
| H0 contemporaneous | 14 | 1.77 | +0.46 | 1.32 | 10 | 1.82 | +0.30 | 1.39 | 2 |
| H1 repo EUR mean t-1, t-2 | 14 | 2.46 | -1.25 | 2.12 | 10 | 1.09 | -0.14 | 0.69 | 3 |
| **H2 Phi-implied on ADR-FX** | **10*** | **0.99** | **+0.10** | **0.58** | **10** | **0.99** | **+0.10** | **0.58** | 2 |
| H2b Phi-implied on basket | 14 | 1.80 | -0.43 | 1.46 | 10 | 1.32 | +0.28 | 0.99 | 2 |
| H3 free weights (Object A) | 14 | 1.49 | +0.43 | 1.12 | 10 | 1.70 | +0.45 | 1.31 | 4 |
| H3b free weights lags 1-3 | 14 | 1.67 | -0.11 | 1.29 | 10 | 1.48 | +0.37 | 1.11 | 4 |

\* **H2 does not cover the full W1 window.** Its driver is the disclosed ADR-FX point, which does not exist before 2Q22, so the first four W1 guide dates have fewer than five usable training rows and are dropped. H2 covers **10 of 14** W1 quarters — the same 10 as W2. Under the "must survive both windows to be quoted" rule, **H2 cannot be quoted as a W1 winner.** It is quoted as: best on W2 (10/10), and best on the 10 W1 quarters where it can be evaluated, with the coverage shortfall named.

**What this table says, and it is the reconciliation.** In-sample and by LOO, the free-weight fit loads on lag 0 and lag 1 and the Phi kernel is rejected. Point-in-time at a guide date, the ranking flips: the specification with **no lag-0 loading at all** (H2) has the lowest RMSE, the smallest bias (+0.1pp against +0.43 for the free fit) and the lowest interval RMSE (0.58 against 1.12), on both windows in which it can be scored. The reason is mechanical and is the whole of Theo's point: **a lag-0 loading is only useful if you can observe the quarter, and at the guide date you have observed about 39% of it.** The free fit is the better description of the world; the lagged fit is the better forecast from the chair management sits in. Both are right. The sentence that survives cross-examination is: *"FX reaches revenue with an effective lag of under one quarter, so by the time Airbnb guides, roughly two-thirds of the FX in the guided quarter is already fixed — and the part that is still moving is the part management least wants to guess, which is why the lagged proxy out-forecasts the contemporaneous one at the guide date."*

RMSE standard errors at n = 10-14 are 0.3-0.4pp, so 0.99 vs 1.09 vs 1.49 is at most a 1.5-standard-error separation. **Say "best, within noise", not "wins".**

### 6.3 PIT-prior vs full-sample-prior replay (`09d`, `09e`, `09f`) — REBUILT IN ROUND 2

Round 1 shipped a broken full-sample-prior replay: it refit the full-sample coefficients and then discarded them, overwriting only sigma, so the two replays carried byte-identical point forecasts. The verifier caught it. It is fixed: `stages.full_sample_coefficients()` fits each spec once on the whole 1Q23-2Q26 sample and `stages.pit_forecasts(d, coef_override=...)` re-applies those weights at every guide date while keeping the **drivers** point-in-time (QTD basket + spot held) and keeping the >= 5-training-row gate, so the two replays stay row-matched (96 rows each) and differ only in the weights. A hard assertion in `run.py` now fails the run if the two replays ever coincide again.

| spec | rows matched | mean abs point delta (pp) | max abs delta | W1 RMSE PIT | W1 RMSE full-sample | W2 RMSE PIT | W2 RMSE full-sample |
|---|---|---|---|---|---|---|---|
| H0 contemporaneous | 17 | 1.22 | 3.09 | 1.77 | 1.30 | 1.82 | 0.99 |
| H1 repo EUR mean t-1, t-2 | 17 | 1.82 | 6.57 | 2.46 | 1.53 | 1.09 | 1.15 |
| **H2 Phi-implied on ADR-FX** | 11 | **0.22** | **0.50** | **0.99** | **0.99** | **0.99** | **0.99** |
| H2b Phi-implied on basket | 17 | 0.77 | 2.49 | 1.80 | 1.52 | 1.32 | 1.01 |
| H3 free weights (Object A) | 17 | 1.20 | 3.13 | 1.49 | 1.00 | 1.70 | 0.82 |
| H3b free weights lags 1-3 | 17 | 0.93 | 2.68 | 1.67 | 1.34 | 1.48 | 0.97 |

Zero of 96 rows now have identical points. Three things this says, none of which were visible before the fix:

1. **The hindsight premium is large, and it is the honest size of the estimation penalty.** Knowing the full-sample weights at every guide date takes W2 RMSE from 1.70 to 0.82 on the free-weight spec — it roughly halves the error. Across the six specs the W2 improvement runs **+0.88, +0.83, +0.51, +0.31, 0.00 and -0.06pp** (H1 is the one that gets slightly *worse*, which is what a two-parameter EUR-only fit with an intercept does when you stop letting it chase the recent window). So a backtest of this family quoted without a PIT replay is typically **0.3 to 0.9pp too good**, with one exception. That range is larger than every spec-vs-spec difference in §6.2, which is the point: the gap between "I estimated the weights as I went" and "I knew them" dominates the gap between the hypotheses.
2. **H2 is the one spec whose weights are essentially learned by the first fit.** Mean absolute point delta 0.22pp, max 0.50pp, and W1/W2 RMSE identical to two decimals between the replays (0.9936 PIT vs 0.9898 full-sample). It has one free scale on a fixed 2/3-1/3 shape, so there is almost nothing left to learn. This is a genuine argument for the Phi spec that §6.2 could not make: **it is not just the best PIT forecaster here, it is the one whose PIT and hindsight performance coincide**, so its backtest is not borrowing from the future.
3. **The free-weight specs pay the whole estimation penalty.** H3's PIT W2 RMSE is *worse* than its W1 (1.70 vs 1.49) while its full-sample replay is better (0.82 vs 1.00) — the signature of four parameters being re-estimated on 7-20 rows. Do not read a free-weight LOO number as a forecast accuracy.

The §6.2 PIT table is **unchanged** by this fix (it never used the broken full-sample rows): H2 W1 RMSE 0.9936, bias +0.0975, interval RMSE 0.5782, n = 10, reproduced after the rebuild.

### 6.4 PIT caveat on the training features (named after the round-1 verification)

The target quarter's own lag-0 basket is properly vintage-stamped: `pit_fx.basket_yoy_asof` uses FRED through the day before the guide and `pit_fx.regional_shares_asof` filters L0 rows on `knowable_from <= vintage`. **The historical training features do not get the same treatment.** `b_lag1/2/3`, `eur_lag1/2` and `adrfx_lag1/2` come from `02_basket_quarterly.csv`, built once by `baskets.regional_revenue_weights()`, which reads the current vintage of `L0_exact_regional_revenue.csv` with no `knowable_from` filter. So a PIT fit at an early guide date uses today's regional revenue split to weight a 2022 basket.

How much this can matter: FRED bilateral spot rates never revise, and `L0_exact_regional_revenue.csv` carries `basis` in {`filed`, `back_out`} with **zero restated or derived rows** (asserted and written out in `00_pit_caveats.csv`), so the shares a contemporaneous forecaster would have seen are the same numbers we use. The asymmetry is real and undocumented before now; the measured exposure to it is nil on this file. It is documented rather than fixed, because fixing it means rebuilding the entire basket history per vintage for a correction that the data says is exactly zero — and saying that plainly is better than a rebuild that produces the same numbers and implies a precision we did not add.

---

## 7. The already-determined share — the triple, never one number

`10_determined_share.csv`. Formula, stated: **FX-determined share = (1 - w0) + w0 x (days elapsed in the target quarter before the date / days in the quarter)**, where w0 is the contemporaneous loading. Published as a band across the Object-A confidence set.

| date | what | target | w0 = 0.15 (CS lo) | w0 = 0.57 (point) | w0 = 0.97 (CS hi) | w0 = 0.75 (M6 lambda) | w0 = 0 (architect) | **volume-determined** |
|---|---|---|---|---|---|---|---|---|
| 2026-08-06 | 3Q26 guide date | 3Q26 | 0.91 | **0.66** | 0.41 | 0.54 | 1.00 | 1.00 |
| 2026-09-11 | today (28 Aug FX) | 3Q26 | 0.97 | **0.88** | 0.79 | 0.84 | 1.00 | 1.00 |
| 2026-10-02 | memo due | 4Q26 | 0.85 | **0.44** | 0.04 | 0.26 | 1.00 | **0.33** |
| 2026-10-23 | finals | 4Q26 | 0.89 | **0.57** | 0.26 | 0.43 | 1.00 | **0.33** |
| 2026-11-05 | 4Q26 guide date | 4Q26 | 0.91 | **0.65** | 0.40 | 0.54 | 1.00 | **1.00** |
| 2027-02-11 | 1Q27 / FY27 guide | 1Q27 | 0.92 | **0.69** | 0.47 | 0.59 | 1.00 | 1.00 |

The three numbers to say together, for 4Q26:

1. **FX-determined share at the 5 Nov guide date: 0.65 central, band 0.40 to 0.91.** The M6 lambda of 0.75 gives 0.54, which is inside the band — the chief of staff's 0.54 figure is reproduced exactly and is the *pessimistic* end, not the estimate.
2. **Volume-determined share at the 5 Nov guide date: 1.00.** 3Q26 GBV prints that morning, so the kernel base 2/3 GBV(3Q26) + 1/3 GBV(2Q26) is fully known.
3. **Volume-determined share at the 2-24 Oct pitch date: 0.333.** Only 2Q26 GBV is printed; 3Q26 GBV, which carries two-thirds of the weight, is not. **This asymmetry must be stated in the pitch, not glossed.** The 82% figure and the 85-90% on-the-ledger claim are not used anywhere in this package.

---

## 8. Booking-date FX carried through the kernel, and the ex-FX acceleration

`12_kernel_carried_fx.csv`. Three readings, one decimal, all recomputed from the basket files:

| reading | 3Q26 | 4Q26 | step |
|---|---|---|---|
| A: disclosed ADR-FX points through Phi (2/3 q-1 + 1/3 q-2) | **+2.5** | **+0.6** | **-1.9** |
| B: global basket x 0.56 through Phi | +1.9 | +0.6 | -1.3 |
| C: Object-A weights on the basket | +1.1 | +0.7 | -0.5 |

Reading A is the architect's construction recomputed from data rather than from rounded letter figures, and it lands at **+2.5 / +0.6 / -1.9** against his stated **+2.3 / +0.3 / -2.0**. The 0.2-0.3pp differences come from using 2Q26 ADR-FX of +1.3 rather than the rounded +1.0, and from a fitted 3Q26 ADR-FX of +0.2 (contemporaneous basket fit, slope 0.87) rather than 0.0. **Reading A is reproduced within 0.3pp; the architect's arithmetic is sound.**

Ex-FX acceleration (`12b_exfx_acceleration.csv`), at the architect's central 3Q26 GBV of $26,300M:

| | 3Q26 | 4Q26 | step |
|---|---|---|---|
| kernel base (2/3 GBV q-1 + 1/3 GBV q-2), $m | 27,867 | 26,600 | |
| kernel base y/y | +16.9% | +15.2% | **-1.8pp** |
| FX step, reading A | | | **-1.9pp** |
| **ex-FX acceleration** | | | **+0.1pp** |

At the frozen card's $26,185M the base step is -2.1pp and ex-FX **decelerates 0.2pp**. **The brief's expected "+0.4pp acceleration" is not reproduced; the honest answer is that ex-FX growth is FLAT into 4Q26, somewhere between -0.2 and +0.1pp, and the sign flips on a $115M move in the 3Q26 GBV estimate.** That is a weaker claim than the one I was asked to confirm and it is the one the arithmetic supports. Under readings B and C, ex-FX decelerates by 0.5 to 1.6pp. Do not put "ex-FX accelerates" in the memo without naming the reading and the GBV.

---

## 9. The four-way (five-row) FX reconciliation — `13_four_way_reconciliation.csv`

**This table is the only place the rejected constructions appear. This package emits no additive FX pp to revenue.**

| construction | 4Q26 FX pp | status | named cause of the difference |
|---|---|---|---|
| repo `05_fx_schedule.csv` `revenue_fx_fit_pp` | **-0.4** | rejected as input | a reduced-form level fit of stated revenue FX on a lagged EURUSD/broad-USD blend; it forecasts the disclosed pp rather than running the kernel arithmetic, and it re-applies a lag that is already inside the lagged GBV base |
| repo `29_q4_fy27_bridge.py` FX step | **-3.4** | rejected as input | subtracts the FX step a **second** time on top of a GBV base that already carries booking-date FX — the double-subtraction the architect ruled out |
| M6 memo forward schedule | **+0.4** | rejected as input | rests on an FX fit that misses a nearly observed quarter by about 2pp, and the memo carries +1.04pp in its schedule against +0.73pp in its own 3Q26 build |
| guide-anchored (hold management's stated Q3 assumption) | **+2.6** | rejected as input | holds the 3Q26 tailwind flat into 4Q26; the basket itself rolls over, so flat imports a tailwind the spot path has already removed |
| **kernel-implied (this package)** | **+0.6 to +0.7** | **adopted, as an OUTPUT** | booking-date FX is already inside the lagged USD GBV base; the pp shown is what the arithmetic produces, never an adjustment applied to it |

Spread: -3.4 to +2.6 = **6.0pp**, which on 4Q25 revenue of $2,778M is **$167M** of 4Q26 revenue. Excluding the bridge's double-subtraction, the spread is -0.4 to +2.6 = 3.0pp = **$84M**, the "about $90M" the addendum anticipated. **The internal disagreement about FX alone is larger than the gap between our 4Q26 number and the Street's, and saying so first is a point in our favour.**

---

## 10. The forward schedule — `11_forward_schedule.csv`

Spot held constant from **2026-08-28** (the last FRED observation; there is no FX data between 28 Aug and today, and every "as of 11 Sep" label in the repo is really as of 28 Aug). Object-A gross weights applied to the basket. 80% bands from the fitted sigma of 0.88pp. FX pp quoted to one decimal.

| quarter | spot held | weak USD (+5%) | strong USD (-5%) | 80% band, spot held |
|---|---|---|---|---|
| 3Q26 | **+1.2** | +1.2 | +1.2 | 0.0 to +2.3 |
| 4Q26 | **+0.7** | +2.2 | -0.8 | -0.4 to +1.8 |
| 1Q27 | **+0.5** | +3.1 | -2.2 | -0.7 to +1.6 |
| 2Q27 | **+0.1** | +2.8 | -2.7 | -1.1 to +1.2 |
| 3Q27 | **+0.2** | +2.3 | -2.1 | -1.0 to +1.3 |
| 4Q27 | **+0.1** | +0.9 | -0.7 | -1.0 to +1.2 |

**FY27 under spot held: about +0.2pp on revenue growth, i.e. FX is a non-event for FY27 unless the dollar moves.**

**The arithmetic, shown (added round 2, `11b_fy27_annualisation.csv`).** A fiscal-year y/y FX contribution is the revenue-weighted **average** of its four quarterly y/y contributions, **not their sum** — do not add the column above and quote +0.9pp. Spot held: 1Q27 +0.5, 2Q27 +0.1, 3Q27 +0.2, 4Q27 +0.1; simple mean 0.9/4 = +0.22; revenue-weighted (2025 actual quarterly revenue shares 0.186 / 0.253 / 0.335 / 0.227) = +0.22. The two agree to under 0.05pp because the schedule is nearly flat, so **+0.2pp** either way. Under the same averaging: weak USD +2.3pp, strong USD -2.0pp (simple mean -1.9). The 2025 shares are used rather than an FY27 revenue forecast to keep this from depending on the number the programme is forecasting; the choice moves the answer by less than 0.05pp.

A +/-5% parallel shift in the held spot (about 1 sd of a two-quarter dollar move) swings FY27 FX by roughly +2.5 / -2.4pp, which is the dominant FY27 FX risk and is worth more than any of the decomposition lines.

**Forward curve: NOT DERIVABLE.** The FRED cache contains spot bilaterals and DTWEXBGS only — no forward points, no FX futures, no interest-rate differentials for the non-USD legs. The forward-curve path requested in (e) is therefore reported as unavailable rather than fabricated, and the scenario set is spot-held plus a parallel shift.

Against the repo's own `05_fx_schedule.csv` consensus path: it shows 2026Q3 `revenue_fx_fit_pp` +2.19 and 2026Q4 -0.43, against my +1.2 and +0.7. The repo path has FX turning negative in 4Q26; mine has it fading to roughly nothing. The difference is the lag structure — the repo fit loads on lagged EURUSD only, which rolled over hard (EURUSD y/y +11.1 in 1Q26 to -1.6 in 3Q26), while the revenue-weighted basket is held up by LatAm (+6.4 in 3Q26) and APAC (+1.5). **EURUSD is not the basket, and the 1.5-2pp of this disagreement is entirely the EMEA-only approximation.**

---

## 11. Hedges — `14_hedge_gross_vs_after.csv`

The identity `gross_ex_hedge + hedge_effect = stated` holds on all 14 quarters to 1e-6. Hedges did nothing to revenue growth from 1Q23 through 2Q25 (reclassifications were zero); from 3Q25 they subtract **-1.13, -0.93, -0.66, -0.61 pp** in 3Q25, 4Q25, 1Q26, 2Q26 as designated notional grew from $2.6bn to $3.4bn (45-47% of LTM non-USD revenue).

**Hedge-once rule, stated for the record: the letter-stated revenue-FX points are ALREADY AFTER hedges.** `28_fx_hedge_forward.csv` (the -0.21/-0.21/-0.18/-0.18 pp schedule derived from the ~$26M expected 12-month reclassification) is **never** added on top of a letter-stated FX point. This package does not add it anywhere. The one legitimate use of the forward file is to adjust a *gross* forward projection, and the forward schedule in section 10 is estimated on the **gross** series, so if it is converted to an after-hedge basis the forward file's -0.2pp would be applied **once** — and it is not applied in the table above, which is therefore on a gross-of-hedge basis. That is stated in the file.

---

## 12. Registry objects and parameter counts

| registry file | rows | target | windows | prior bases | free params |
|---|---|---|---|---|---|
| `fx-lag__fx_rev_next_q_h2.csv` | 40 | `fx_pts_revenue` | W1 (10/14 — driver unavailable pre-2Q22), W2 (10/10) | PIT + full_sample | **2** (scale, sigma) |
| `fx-lag__fx_rev_next_q_h3.csv` | 48 | `fx_pts_revenue` | W1 (14/14), W2 (10/10) | PIT + full_sample | **4** (a0, a1, a2, sigma) |
| `fx-lag__live_fx_schedule.csv` | 2 | `fx_pts_revenue` | LIVE 2026Q3 | PIT + full_sample | 4 |

Quantile ladder q05/q10/q25/q50/q75/q90/q95 from the fitted sigma, Gaussian. `knowable_from` = the day before the vintage date (FRED FX through d-1). No consensus number is consumed, so `street_vendor` / `street_as_of` are correctly absent.

Full parameter inventory for this package: Object A 4; Object B 5; Object C 3; stage-(b) ADR fit 3; H0/H1/H2 2-3 each. Against 14 interval-censored revenue-FX observations and 17 ADR-FX observations. The 4-parameter Object A on 14 observations is the loosest object here (3.5 observations per parameter) and its confidence set is correspondingly wide — which is the finding, not a defect.

---

## 13. What failed, and what I will not claim

1. **The `rev_fx` rows of `05_fx_fits.csv` do not reproduce** (n 13 vs 14; slope -0.5348 vs -0.5023). Not used anywhere.
2. **Object C reproduces its se (0.277 vs 0.275) and its n (12) and its conclusion, but not its slope** (0.389 vs 0.158). The architect's construction is not recoverable from the documents.
3. **H2 cannot be scored on the full W1 window** — its driver does not exist before 2Q22. It is 10/14. Under the survives-both-windows rule it is not quotable as a W1 result.
4. **"Ex-FX accelerates +0.4pp into 4Q26" is not reproduced.** The arithmetic gives -0.2 to +0.1pp and the sign turns on the 3Q26 GBV estimate. Say flat.
5. **The forward curve is not derivable from FRED** and is not fabricated.
6. **The daily FX file ends 2026-08-28**, so nothing in this package is genuinely "as of 11 September"; every spot-held number is as of 28 August. The 5 Nov determined-share rows use calendar day-counts (correct) with 28 Aug FX (the best available).
7. **The fitted scale of 0.95 against a disclosed 0.56 is a red flag on the basket weights**, which are judgement. Anyone using this basket for a level (rather than a change) should rebuild the weights from booking-currency data first.
8. **No FX pp is added to revenue anywhere.** No forward hedge file is added on top of stated after-hedge FX. No FX pp is quoted to two decimals.
9. **R engine cross-check: SKIPPED.** `Citadel-ABNB-fx-engine/analysis/src/fx_engine` was not exercised — the overnight budget went to the interval-likelihood confidence set and the PIT replay, and an unvalidated R cross-check would have added a number without adding evidence. Stated as skipped rather than silently omitted.

## Harness change request

**The registry cannot hold a LIVE forecast for any quarter after 2026Q3.** `windows.csv` maps only 2026Q3 to LIVE, and `validate_registry_frame(strict_windows=True)` rejects `window=LIVE, quarter=2026Q4` with "that quarter belongs to []". The whole point of this package's forward schedule is 4Q26 through 4Q27. Requested: admit `LIVE` for any quarter >= 2026Q3, or add a `FORWARD` window. Worked around locally by writing the un-registrable rows to `data/processed/forecast_methods/fx_lag/15_live_objects_not_registrable.csv` in registry column order.

**Second request: there is no annual target.** `targets.csv` is quarterly, so an FY27 object cannot be registered as a single row. FY27 FX is reported in this note and in `11_forward_schedule.csv` / `11b_fy27_annualisation.csv` as the revenue-weighted **average** of four quarterly objects (+0.2pp under spot held), not their sum.

---

## Fixes after verification (round 2, 2026-09-11)

Against `VERIFY_fx-lag_r1.md` (verdict PARTIAL; 13 of 13 recomputed numbers matched, one confirmed implementation bug, two documentation items). Re-run end to end, **exit code 0**, ~24 s, 28 data files + 3 registry files.

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fx_lag/run.py
```

### 1. PRIORITY 1 — the full-sample-prior replay. FIXED.

**The bug, stated plainly.** `run.py` fitted `full_coef` for each spec and then never used it: the loop appended only `f["sigma"]` and assigned `pf_full["sigma"] = rows`, leaving `point` (and therefore `q50` and the whole registered ladder's centre) a byte-for-byte copy of the PIT replay. All 96 rows of `09d` and every `prior_basis=full_sample` row of `fx-lag__fx_rev_next_q_h2.csv` and `fx-lag__fx_rev_next_q_h3.csv` carried a PIT point wearing a full-sample band. The harness's `check_replays()` only asserts that both `prior_basis` labels are present, so registration passed silently. The verifier is right that this defeats the substance of the two-replay rule, and right that a reader scoring the `prior_basis` split off the registry would have concluded "PIT and full-sample priors give identical point accuracy" — an artefact, not a finding.

**What changed.**

- New `stages.full_sample_coefficients(d, target)` — fits every PIT spec once on the whole 1Q23-2Q26 sample and returns `{spec: (coef, sigma, n)}`.
- `stages.pit_forecasts()` gained a `coef_override` argument. When passed, the expanding-window fit is still *run* (so the >= 5-training-row gate and therefore the row set are identical, keeping the replays row-matched at 96 vs 96), but the override coefficients are what get applied: `point = Xo @ coef`. **The drivers stay point-in-time** — the target quarter's lag-0 basket is still QTD actual + spot held through the day before the guide. Only the weights are the illegitimate ones. That is the correct contrast: it isolates "what did knowing the weights buy you" from "what did knowing the quarter buy you".
- Each forecast row now carries `prior_basis`, `coef` (the applied weight vector), `n_train` (the fit's own n: expanding for PIT, 14 for full-sample) and `n_train_pit` (the expanding-window count, kept on both so the rows stay comparable). `n_train` in the registry is now correct per basis rather than always the PIT count.
- New outputs: `09e_pit_window_scores_full_sample_prior.csv` (the full-sample replay scored on W1/W2 exactly as `09c` scores the PIT replay) and `09f_replay_delta_pit_vs_full.csv` (per spec: rows matched, mean and max absolute point delta, count of identical rows, both windows' RMSE side by side).
- **Regression guard.** `run.py` now asserts `max_abs_point_delta > 1e-6` and fails the run if the two replays ever coincide again. Console line on this run: `replay check: max |point delta| = 6.5733pp, 0 of 96 rows identical`.

**Result.** Zero of 96 rows identical. Registry: `fx_rev_next_q_h2` max PIT-vs-full point delta 0.5013pp over 20 matched triples; `fx_rev_next_q_h3` 2.6195pp over 24. The substantive reading is written up as **§6.3**, and it earns its place — the hindsight premium (0.3 to 0.9pp of W2 RMSE) turns out to be larger than any spec-vs-spec difference in §6.2, and H2 is the one spec whose PIT and full-sample replays coincide, which is a better argument for the Phi spec than anything §6.2 could make.

**Nothing else moved.** The PIT replay itself was never touched: `09c` reproduces exactly (H2 W1 RMSE 0.9936, bias +0.0975, interval RMSE 0.5782, n = 10), as do Object A (gross scale 0.9515, effective lag 0.4346, CS [0.029, 0.923]; H0 LR 16.762 p 0.0008), Object B, Object C, the determined-share triple, the four-way reconciliation and the forward schedule. Every headline number in the memo-facing narrative is unchanged.

### 2. PRIORITY 1b — the overstated acceptance test. DOWNGRADED, as the verifier asked.

The round-1 line *"Point-in-time expanding window ... both prior replays: PASSED"* was correct on row counts and false on substance. In this round's acceptance table it is split into two rows: the PIT expanding-window replay (**PASSED**, unchanged) and the two-replay distinctness test (**FAILED in round 1, PASSES now**, with the delta table as the evidence rather than the row count). It is reported as a round-1 failure that was fixed, not quietly re-passed.

### 3. PRIORITY 2 — non-vintage-stamped training features. DOCUMENTED (not fixed), as recommended.

Written up as **§6.4**, with a docstring on `baskets.regional_revenue_weights()` naming the asymmetry at the source, and a machine-readable `00_pit_caveats.csv` that re-derives the evidence on every run: the distinct `basis` values in `L0_exact_regional_revenue.csv` and a count of restated/derived rows (**0**). Not fixed, and the reason is stated: FRED spot never revises and the L0 file carries no restated rows, so a per-vintage rebuild of the basket history would produce the same numbers while implying a precision we did not add. If a restated row ever lands in L0, the caveat file's count stops being 0 and the decision should be revisited.

### 4. PRIORITY 3 (cosmetic) — the FY27 averaging arithmetic. SHOWN.

New `11b_fy27_annualisation.csv` and a paragraph in **§10**. A fiscal-year y/y FX contribution is the revenue-weighted **average** of four quarterly y/y contributions, never their sum; the note now shows 0.5 + 0.1 + 0.2 + 0.1 = 0.9, / 4 = **+0.22pp**, and the revenue-weighted version on 2025 actual quarterly revenue shares (0.186 / 0.253 / 0.335 / 0.227), which also gives +0.22. The file carries the sum in a column named `sum_of_four_quarters_pp_DO_NOT_QUOTE` so nobody picks it up by accident. 2025 shares are used deliberately rather than an FY27 revenue forecast, to keep the FX annualisation from depending on the number the programme is forecasting; the choice is worth under 0.05pp.

### What I did NOT fix, and why

1. **`05_fx_fits.csv` `rev_fx` rows still do not reproduce** (n 13 vs 14, slope -0.5348 vs -0.5023). The repo file does not record which observation it drops and I will not guess one to force a match. Not used anywhere in this package.
2. **Object C's slope still does not reproduce** (0.389 vs the architect's 0.158) on any of eight conventions. n (12), se (0.277 vs 0.275) and the conclusion (|t| < 2 on all 20 rows) do reproduce. The construction is not recoverable from the documents on disk.
3. **H2 still covers only 10 of 14 W1 quarters.** Its driver, the disclosed ADR-FX point, starts in 2Q22, so both lags are jointly non-null only from 4Q22 and five training rows do not accumulate until the 2024-02-13 guide date (the verifier's mechanism is more precise than round 1's and is adopted here). Under the survives-both-windows rule H2 is **not quotable as a W1 winner**; that is a property of the data, not a bug, and no amount of code fixes it.
4. **The LIVE-window and annual-target harness limits** are unchanged — both change requests stand, both workarounds unchanged (`15_live_objects_not_registrable.csv`; FY27 as a quarterly average in the note).
5. **The FRED daily file still ends 2026-08-28.** Nothing here is genuinely as of 11 September. Now also recorded in `00_pit_caveats.csv` rather than only in prose.
6. **The R engine cross-check remains skipped**, for the same reason as round 1.
7. **Still no additive FX pp to revenue anywhere**, no forward-hedge file added on top of stated after-hedge FX, and no FX pp quoted to two decimals.

### Round-2 acceptance tests

| test | result | evidence |
|---|---|---|
| Entry point re-runs end to end | **PASS** | exit code 0, ~24 s |
| Full-sample-prior replay is a distinct forecast | **PASS** (round-1 FAIL) | 0 of 96 rows identical; max delta 6.5733pp; `09f` |
| PIT replay numbers unchanged by the fix | **PASS** | `09c` H2 W1 0.9936 / +0.0975 / 0.5782, n 10 |
| Registry re-registered by the harness's own `register()` | **PASS** | 40 / 48 / 2 rows; the two genuine H2 W1 coverage warnings still surfaced, not suppressed |
| Registry `full_sample` points now differ from `PIT` | **PASS** | h2 max delta 0.5013 over 20 triples; h3 2.6195 over 24 |
| Registry `n_train` correct per prior basis | **PASS** | PIT 5-14 (h2) / 7-20 (h3); full_sample 14 |
| Regression guard fires if the bug returns | **PASS** | assertion in `run.py`, console line printed each run |
| Object A / B / C, determined share, reconciliation, forward schedule unchanged | **PASS** | scale 0.9515, eff. lag 0.4346, CS [0.029, 0.923], H0 LR 16.762 p 0.0008 |
| PIT caveats emitted as data, not only prose | **PASS** | `00_pit_caveats.csv`, 3 rows, L0 restated-row count 0 |
| FY27 averaging shown | **PASS** | `11b_fy27_annualisation.csv` + §10 |
| `05_fx_fits.csv` `rev_fx` reproduction | **FAIL** (unchanged) | n 13 vs 14; not used downstream |
| Object C slope reproduction | **PARTIAL** (unchanged) | n and se reproduce, slope does not, conclusion does |
| H2 covers both windows | **FAIL** (unchanged) | 10 of 14 W1; driver starts 2Q22 |
| LIVE registration for 4Q26+ | **BLOCKED** (unchanged) | harness `windows.csv`; change request stands |
