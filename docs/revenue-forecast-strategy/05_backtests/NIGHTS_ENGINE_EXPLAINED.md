# The nights engine, explained three ways

Part 1 is for anyone. Part 2 is for the person who wants to rebuild it. Part 3 is for the statistician who wants to break it.
This document is about the **method** and its evidence; the current-quarter readings, the forward path and the Street
comparison live in `REVIEWS_INDEX_v2.md` (§3–5) and `REVIEWS_INDEX_v2_RATIONALE.md`. Every number here is read from
`data/processed/forecast_methods/reviews_index_v2/` (engine v2.1, 18 Sep 2026).

---

## Part 1 — In plain English

**The problem.** Airbnb tells the world how many nights were booked once every three months. We want to know what is
happening before they say it — and, more importantly, whether the number they report is made of trips that actually
happen.

**The idea.** Every stay on Airbnb leaves a trace: after check-out the guest can write a review, and most do. Inside
Airbnb, a public project, publishes the complete review logs for about 120 cities. Count the reviews and you are
counting trips that were taken. Not searches, not clicks, not intentions — trips.

**Three traps, and how we step around them.**

1. *Listings disappear.* Each published file only contains listings that are still live. Read last year's reviews in
   this year's file and every listing that has since been removed has taken its reviews with it — in Paris, a fifth of
   them in one year. So last June looks smaller than it was and this June looks like growth that never happened. We fix
   it by reading each month at the same age in its own file: this June from this year's file, last June from last year's.
2. *Our cities are not Airbnb's map.* Europe is over half of our cities but less than half of Airbnb's nights, and the
   mix changes with the season — Europe is half of all stays in the summer quarter and a quarter of them in winter. So we
   weight the four regions by Airbnb's own mix for that quarter of the year, taken from what the company discloses.
3. *A review is not a night.* Reviews grow faster than nights (new listings get reviewed more, people review more over
   time). We don't assume the conversion; we measure it where real nights are published — Eurostat, the EU's statistics
   office, publishes nights spent in platform rentals by country every month. Across 18 countries and three years, when
   our review count moves, real nights move with it, by a steady proportion. That is what makes the count an instrument.

**Turning the count into Airbnb's number.** Our count is a growth rate for the sampled cities; Airbnb's number is growth
for the whole platform. A straight line with two numbers — a slope and a level — translates one into the other. We fit
the line only on the quarters before August 2025, then freeze it, so nothing that happened after can leak into it.

**How we know it works.** We pretend, quarter by quarter since the start of 2023, that we don't know that quarter's
result, forecast it from the count, and record the miss. Our misses are about 28% smaller than the simplest possible
forecast ("the same growth as last quarter") — on both of the test windows the team uses, which no earlier construction
had managed. We also say honestly that with only 10–14 quarters to test on, the advantage is clear in size but not yet
proven beyond statistical doubt.

**Why "reported" and "real" can differ.** Airbnb counts a night when it is *booked*. A review counts a night when it is
*stayed*. A booking that is later cancelled is in the first number and never in the second. Since August 2025 Airbnb lets
guests reserve with nothing down and pay later; a guest who never pays never stays. So the gap between the reported
number and our stays measure is where that option shows up — and the balance sheet confirms it: the fees Airbnb collects
in advance stopped growing while bookings kept growing.

**What we can and cannot say.** We can say how fast real stays are growing, with an error bar we measured. We can say
the reported number has run above real stays since the pay-later option launched, in the direction expected, but by
less than our error bar — "consistent with", not "proven". We cannot say, from cities alone, *how much* of the gap is
the option, because the test that would prove that needs data we don't have; we say that too.

---

## Part 2 — Technical and granular

### 2.1 Data

| object | source | grain | span |
|---|---|---|---|
| review counts | Inside Airbnb dumps, mirrored; `q3nowcast/E/market_vintage_monthly.csv` | market × review-month × dump vintage | 123 markets; vintages Aug 2025, Aug 2026 (+ Mar–May 2023 for 114 markets) |
| printed nights | 10-Q/10-K; `abnb_driver_history_quarterly.csv` | quarter | 1Q21–2Q26 (levels) |
| observed platform nights | Eurostat experimental statistics; `eurostat_platform_nights_monthly.csv` | country × month | 31 countries, 2018-01 → 2026-03 |
| regional revenue, ADR index | 10-Q; `overnight/10_regional_panel_quarterly.csv` | region × quarter | 1Q22–2Q26 |
| unearned fees, GBV | 10-Q balance sheet; `overnight/02_kpi_panel_quarterly.csv` | quarter | 1Q23–2Q26 |

### 2.2 Construction

**Vintage selection.** For market m, the latest dump L and the prior dump P with 300 ≤ age(L) − age(P) ≤ 430 days. Months
in the two calendar months up to and including each dump's month are dropped (posting lag, truncation).

**Same-age counts.** For review-month t: `n_cur(m,t) = reviews for t in L`; `n_prior(m,t) = reviews for t−12 in P`.
Both are read the same number of months after their own dump; attrition of delisted listings is common to both sides and
cancels to first order (the residual assumption is a stationary attrition hazard across vintages — WPK-A T2 measured it at
~15.8%/yr, age-dependent, hence same-age rather than a constant wedge).

**Regional growth.** `g_r,q = Σ_{m∈r} Σ_{t∈q} n_cur(m,t) / Σ_{m∈r} Σ_{t∈q} n_prior(m,t) − 1`, markets included only if all three
months of q are present (review-share weighting within region).

**Stay-quarter mix weights.** `w_r,q = (Rev_r,q / A_r) / Σ_r (Rev_r,q / A_r)`, with Rev the disclosed regional revenue
(check-in basis, hence a stay-quarter mix) and A the regional ADR index (NA 1.42, EMEA 0.97, LatAm 0.68, APAC 0.59).
Forward quarters: same quarter of the prior year plus the drift rule (NA −0.55 pp/qtr, EMEA +0.10, LatAm +0.33, APAC
+0.10), renormalised.

**Index.** `x_q = Σ_r w_r,q · g_r,q` (percent).

**Mapping.** `y_q = a + b · x_q + ε_q`, y = printed nights y/y (%). Fitted by OLS on 1Q23–2Q25 (n = 10) and frozen:
`a = 6.825`, `b = 0.350`. Leave-one-quarter-out slope on 1Q23–2Q26: 0.332, range 0.258–0.350.

**Stays-implied y/y and the gap.** `ŷ_q = a + b · x_q`; `gap_q = y_q − ŷ_q` for q after the freeze. The gap is the option
term I in `print = stays + I`.

### 2.3 Scoring (the record's protocol, E5 verbatim)

Expanding-window walk-forward. For each scored quarter q: fit a_q, b_q by OLS on all quarters in the window before q
(≥ 4 required); predict `a_q + b_q · x_q`; error `e_q = pred − y_q`; naive error `n_q = y_{q−1} − y_q`; prior-year
`y_{q−4} − y_q`; AR(1) refit likewise. Ratio = RMSE(e) / RMSE(n). W1: window 1Q22+, scored 1Q23–2Q26 (n 14). W2: window
1Q23+, scored 1Q24–2Q26 (n 10). Band = RMSE(e) on W2 scored 1Q24–2Q25 (n 6, pre-RNPL). Interval: moving-block bootstrap
(block 2) of the ratio, 2,000 draws, 5th–95th percentile. Test: Diebold–Mariano on squared loss, h = 1, HLN small-sample
factor. The scorer reproduces E5's 0.683209 on the v1 cell before any v2 number is written (`tests/test_scoring.py`).

### 2.4 Validation of the instrument (Stage A)

Panel: 18 EU countries (50 markets summed to country), months 2023-01 → 2026-03. `Y_ct = log(N_ct / N_c,t−12)` (Eurostat
nights), `X_ct = log(1 + g_ct)` (review growth, same-age). Model `Y_ct = α_c + β X_ct + u_ct` by within-country OLS.
Standard errors clustered by country; with 18 clusters the p-value is a Rademacher wild-cluster bootstrap of the t
statistic (999 draws, restricted residuals). Robustness: the same model in first differences (`ΔY_ct = β_Δ ΔX_ct`);
leave-one-country-out; 2023–24 vs 2025–26 split; per-country expanding walk-forward from 2024-01 with naive `Y_c,t−1`.

### 2.5 The identity and the option term

`N_q = G_q − C_q`: printed nights = gross bookings in q less cancellations occurring in q (any cohort). Stays from cohort q
= `G_q (1 − x)`; stays landing in q = `Σ_k m_k(q) G_{q−k}` with m the K2 lead-time kernel (≈ 50 / 35 / 10 / 5 % over
lags 0..3). Hence `N_q − (eventual stays of cohort q) = x·G_q − C_q`, positive while the option flow grows, zero at a
plateau, negative if exercise exceeds refill; the gap defined in 2.2 estimates it up to the mapping's error.

### 2.6 What was tried and rejected (each with its number, in `REVIEWS_INDEX_v2.md`)

Single-file counts (`yoy_all`): clears both windows only under v2's aggregation (0.749/0.684; 0.823/0.749 with seasonal
weights). Same-store (`yoy_mature`): 0.972/0.908, fails. Importing the panel β as the slope: walk-forward 4.47× naive.
Cohort-consistent deconvolution: band ±3.1, uninformative. A staggered DiD on stays: not identified (Part 3.5).

### 2.7 Parameters and what pins them

| parameter | value | pinned by |
|---|---|---|
| attrition treatment | same-age two vintages | WPK-A T1/T2 |
| posting-lag trim | 2 months | E6 completeness curve |
| ADR index (weights) | 1.42 / 0.97 / 0.68 / 0.59 | `10_regional-and-segment-decomposition.md` |
| drift rule | −0.55 / +0.10 / +0.33 / +0.10 pp per quarter | same |
| a, b | 6.825, 0.350 | OLS 1Q23–2Q25, frozen |
| band | 1.85 pp | W2 pre-RNPL walk-forward RMSE |
| kernel m_k | K2 matrix | `kernel_leadtime_v2` |

---

## Part 3 — Statistical significance

Three claims, each with its null hypothesis, its test, and its verdict. The pass lines were frozen (sha256 in the note)
before anything ran; nothing below was chosen after seeing a result.

### 3.1 Claim: review counts measure stays

*Null:* review growth carries no information about observed nights growth (β = 0), or the association is a shared
trend.

| test | statistic | value | inference |
|---|---|---|---|
| A1 elasticity, country FE | β; cluster se; t | **0.494; 0.070; t 7.09** | wild-cluster bootstrap **p = 0.001** (the floor of 999 draws); within-R² 0.36; n 702, 18 clusters |
| A2 first differences | β_Δ; se; t | **0.703; 0.103; t 6.83** | **p = 0.001**; a shared trend cannot produce co-movement in month-to-month *changes* |
| A3 leave-one-country-out | range of β | 0.471–0.547 | all 18 fits same sign; no single country drives it |
| A4 era split | β(2023–24) vs β(2025–26) | 0.456 (se 0.081) vs 0.431 (se 0.124) | |z| = 0.17 — no break across the RNPL era |
| A5 out of sample by country | median walk-forward RMSE ratio vs naive | **0.59** | 486 scored months; 17 of 18 countries ≤ 0.75 |

Why these tests: months within a country are serially dependent → cluster by country; 18 clusters is too few for
asymptotic cluster-robust inference → wild-cluster bootstrap (Cameron–Gelbach–Miller); post-COVID normalisation could
make two declining series co-move → first differences; a panel β can be one country's story → leave-one-out;
the instrument could have changed nature when RNPL launched → era split. **Verdict: rejected at any conventional level,
on all five.** This is the claim the model stands on, and it does not depend on Airbnb's 14 quarters.

### 3.2 Claim: the index forecasts printed nights better than naive

*Null:* the walk-forward RMSE of the index equals that of "same as last quarter."

| window | n | RMSE index / naive | **ratio** | 90% block-bootstrap interval | DM stat | DM p | vs prior-year | vs AR(1) |
|---|---:|---|---:|---|---:|---:|---:|---:|
| W1 (scored 1Q23–2Q26) | 14 | 2.08 / 2.88 | **0.723** | [0.61, 1.08] | −1.29 | 0.22 | 0.17 | 0.52 |
| W2 (scored 1Q24–2Q26) | 10 | 1.56 / 2.16 | **0.723** | [0.58, 0.97] | −1.20 | 0.26 | 0.43 | 0.74 |
| W2 pre-RNPL (1Q24–2Q25) | 6 | 1.85 / 2.64 | 0.700 | [0.49, 0.85] | −1.12 | 0.31 | | |

Reading it straight: the point estimate is a 28% reduction in error on both windows, and the pre-registered survivor
line (≤ 0.75 on both) is cleared — the first construction in the team's record to do so, out of 256 cells tried before
it. The bootstrap interval on W1 reaches 1.08 and the Diebold–Mariano test does not reject equal accuracy at 5% on
either window. That is what n = 10–14 can deliver: the effect is large and the sample is short. The honest sentence is
*"beats naive by 28% on both windows; the interval at this n does not exclude naive."* Two supporting facts: the index
beats the prior-year baseline by a wide margin (0.17 / 0.43) and the AR(1) (0.52 / 0.74); and the acceleration target
(Δ of y/y) is not forecast on W1 (1.56) — the level is forecast, the shape is not, and we say so.

**Multiple comparisons.** The v1 grid tried 256 nights cells and exactly one cleared both windows (1/256 ≈ chance). v2 was
one construction, declared before the run, with the neighbouring v1 cells named as the prior (0.754/0.682 and
0.708/0.809 — each clears one window). v2.1 (seasonal weights) was a single declared change with its reason, reported
beside v2. No cell was re-picked.

### 3.3 Claim: printed nights have run above stays since the option launched

*Null:* post-launch residuals of the frozen mapping are drawn from the pre-launch error distribution (mean 0, sd = band).

| quarter | printed | stays-implied | gap (pp) | in bands |
|---|---:|---:|---:|---:|
| 3Q25 | 8.80 | 7.94 | +0.86 | 0.46 |
| 4Q25 | 9.82 | 9.48 | +0.34 | 0.18 |
| 1Q26 | 9.15 | 9.96 | −0.80 | −0.43 |
| 2Q26 | 10.34 | 8.79 | +1.55 | 0.84 |
| mean | | | **+0.49** | **0.26** |

Pre-registered pass line: mean > 1.0 band and ≥ 3 of 4 quarters > 0.5 band. **Not met.** Three of four have the predicted
sign; the mean is a quarter of a band; a one-sample t on four residuals against 0 gives t ≈ 1.0. Verdict as written before
the run: *no measurable signature in stays.* "Consistent with" is licensed; "shows" is not.

### 3.4 Claim: the option is being written at scale (balance sheet)

*Null:* the unearned-fees-minus-GBV spread after 3Q25 is drawn from its 1Q23–2Q25 distribution.

Pre-launch spread: mean **+2.70 pp, sd 2.95, n 10**. Post-launch: **−4.1, −8.1, −18.8, −16.7 pp** → z = −2.3, −3.7,
−7.3, −6.6. Welch t (post vs pre, unequal variances, n 4 vs 10) **= −4.04, p = 0.021**; on ex-FX GBV **t = −3.50,
p = 0.028**. Both known confounds bias toward the null (the single-fee migration raises unearned fees; the ex-FX row is the
FX-clean comparison). **Verdict: rejected at 5% on both comparators.** This is the significant RNPL result; 3.3 is the
consistent one.

### 3.5 What the sample cannot test — and why we say so instead of testing anyway

A staggered difference-in-differences on stays (US Aug 2025; UK/AU/CA Feb–Mar 2026; EU never) fails its own validity
gate before the treatment test: US stays growth ran **−3.95 pp** below never-treated controls over 2024-01..2025-07,
before launch (parallel trends violated), and the minimum detectable effect at α .05 / power .8 is **4.0–7.2 pp** against a
sought effect ≤ 3 pp. Reporting a coefficient from it would be an underpowered test with a violated pre-trend presented
as causation. It is reported as a power analysis.

### 3.6 Summary

| claim | test | statistic | verdict |
|---|---|---|---|
| reviews measure stays | FE panel, wild-cluster bootstrap; first differences; OOS by country | β 0.49, p .001; β_Δ 0.70, p .001; median 0.59 | **significant** |
| index beats naive | walk-forward W1/W2; block bootstrap; DM | 0.723 / 0.723; [0.61, 1.08] / [0.58, 0.97]; p .22 / .26 | **clears the line; not separated from naive at this n** |
| print above stays post-launch | residuals vs pre-launch band | mean +0.49 pp, 0.26 bands | **consistent, not significant** |
| option written at scale | Welch t on UF − GBV spread | −4.04, p .021 (ex-FX p .028) | **significant** |
| causal effect at market level | DiD | MDE 4–7 pp vs ≤ 3; pre-trend −3.95 | **not testable here** |

The discipline that makes these numbers citable: one pre-registered construction, pass lines hashed before the run, every
fail printed with its pre-written reading, and the intervals beside every point estimate.
