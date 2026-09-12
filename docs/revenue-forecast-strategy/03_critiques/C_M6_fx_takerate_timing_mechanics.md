# C-M6 — Adversarial review of `M6_fx_takerate_timing_mechanics.md`

**Reviewer role:** Citadel IC seat + econometrics. **Posture:** refute first; the proposal survives only where I failed to break it.
**Date:** 11 Sep 2026. **Verdict: ADOPT WITH FIXES** — the *architecture* is right and is already the repo's own recommendation; almost every *number* the memo would print is wrong, weakly identified, or circular.

Everything below was checked by opening the file. Where I recomputed something I say so and give the arithmetic.

---

## 0. Executive summary — what I broke

| # | The proposal's load-bearing claim | Status after attack |
|---|---|---|
| 1 | Restated unearned fees are a **hard accounting pin** on `Φ` (identification pin #1, "the day that decides") | **Circular.** `restated ≡ coverage_norm × next-quarter revenue`, by the definition of `d_q`. For 2Q26 it is literally `0.697 × the 3Q26 guide midpoint`. Using it to forecast next-quarter revenue is forecasting the guide from the guide. **FATAL as specified.** |
| 2 | Fee migration is worth **+4.05% of revenue on the migrated cohort** — "measured (arithmetic on published rates)" | **Assumption.** It requires constant host payout. The repo's own `12_reprice_summary.csv` does not support that, and does not support the quoted θ either. Honest range is **+1.1% to +1.8%**, with GBV **falling** 1.6-2.3% on the migrated cohort, not rising 0.60%. That cut alone removes ~60-75% of the claimed edge vs Street. |
| 3 | Two-index FX **halves** the incumbent's LOO error (1.08 vs 2.30pp) | **Apples to oranges, twice.** 1.08 is *in-sample, two free parameters*; 2.30 is *LOO* from the **wrong window** (`ex21`, n=17). The matching-window (`post22`, n=14) incumbent LOO is **1.2868** on one parameter. At n=14 on an integer-rounded target the SE of an RMSE estimate is ~0.26pp. There is no measured improvement. |
| 4 | `Φ` is over-identified; the conversion's stability proves the kernel | **Refuted by grid search.** Pooled within-quarter-of-year relative sd is 0.0099 at w₁=0.33, 0.0099 at 0.38, 0.0102 at 0.50, 0.0109 at 0.62, 0.0114 at 0.667. Flat. The file cited as "independent confirmation" (`h2_bridge_gbv_lag_conversion.csv`) uses **w₁=0.667**, the near-opposite kernel, and is equally tight. Stability is a property of smoothly-growing GBV, not of `Φ`. |
| 5 | 11 free parameters against 79 observations | **Mis-counted.** The Stan sketch in §6 declares `vector[T] H` as a *parameter*. 23 GBV observations are consumed by 23 free `H`. `p_q` and refunds enter as a free measurement-error term. |
| 6 | Overlap "arithmetically impossible" | **A contract, not a construction.** It holds only if lens 1 hands over payout-per-night already purged of the migration gross-up — using the same `m_q × θ` that `g(·)` then multiplies back in. Concrete double-count case in §1.3. |
| 7 | "All three killers are observable on 5 Nov 2026, **before the finals reconvene**" | **False.** Finals are 22-24 Oct 2026. 5 Nov is after. |

**What survives and is worth keeping:** the object (revenue as a convolution of *already-printed* GBV), the single-numéraire fee algebra, the hedge-in-dollars-once rule, the interval likelihood on letter-rounded FX and guide buckets, and the four-way FX reconciliation as a memo exhibit. Those are real and they are the best-argued pages in the six proposals.

---

## 1. Axis 1 — Identification. **Score 3/10**

### 1.1 The hidden plug is the restatement, and it is circular

`03_insider_mechanics.md` §1.5 (lines 174-205) defines the distortion series as the gap between reported unearned fees and *what the historical seasonal coverage norm implies they should have been*:

| quarter | reported | coverage norm | implied | gap | `d_q` |
|---|---|---|---|---|---|
| 3Q25 | $1,820m | 0.661 | $1,836m | $16m | 0.9% |
| 4Q25 | $1,743m | 0.676 | $1,810m | $67m | 3.8% |
| 1Q26 | $2,733m | 0.880 | $3,175m | $442m | 16.2% |
| 2Q26 | $2,831m | 0.697 | **$3,297m (at the $4,730m guide mid)** | $466m | 16.5% |

Check the arithmetic: 3175 = 0.880 × 3608 (2Q26 *actual* revenue); 3297 = 0.697 × 4730 (the 3Q26 **guide midpoint**). And `d_q = gap / reported`, so

```
restated_q  =  reported_q × (1 + d_q)  =  reported_q + gap_q  =  coverage_norm_Q × Revenue_{q+1}
```

**identically.** The restated series is not a restated balance sheet. It is `norm × next-quarter revenue` with the balance sheet deleted. Regressing next-quarter revenue on it returns R² = 1 by construction; "beating naive" on day 2A is guaranteed and means nothing. For 2Q26 the value is a function of the 3Q26 *guide*, so it cannot appear in any guide-forecasting feature set at all.

This is the proposal's **hardest** claimed pin ("hard", pin #1 of four). Remove it and `Φ` rests on the column-sum restriction (which is one equation per quarter against a kernel that the next section shows is flat) plus a **single-vintage** Jul-Aug 2026 booking-curve prior. The proposal says exactly this in §4 as its own falsification test — but it expects the test to pass, and it will pass for the wrong reason. **This is the single most important thing to fix before the team spends day 2 on it.**

Second-order but telling: the memo states the formula as `reported/(1 − d_q)`, while the numbers it quotes (+16.6% for 1Q26, +15.4% for 2Q26) come from `reported × (1 + d_q)`. I reproduced both: 2733 × 1.162 / 2723 = **+16.6%** ✓; 2733 / (1 − 0.162) / 2723 = **+19.8%** ✗. Same for 2Q26 (2831 × 1.165 / 2857 = +15.4% ✓ vs /0.835 = +18.7% ✗). A 3pp discrepancy in the memo's own restatement, formula versus number.

### 1.2 `Φ` is weakly identified — I ran the grid

Using `data/processed/overnight/02_kpi_panel_quarterly.csv` (`gbv_musd`, `revenue_musd`), conversion = Rev_q / (w₁·GBV_{q−1} + (1−w₁)·GBV_{q−2}), scored on 1Q23-2Q26 as within-quarter-of-year relative sd, pooled over the four seasons:

| w₁ (weight on GBV_{q−1}) | Q1 | Q2 | Q3 | Q4 | pooled |
|---|---|---|---|---|---|
| 0.00 | 1.433% | 1.796% | 1.110% | 0.732% | 0.0127 |
| 0.20 | 1.540 | 1.185 | 0.892 | 0.600 | 0.0105 |
| 0.33 | 1.647 | 0.998 | 0.771 | 0.546 | **0.0099** |
| **0.38 (proposal)** | 1.696 | 0.980 | 0.731 | 0.535 | **0.0099** |
| 0.50 | 1.829 | 1.043 | 0.658 | 0.531 | 0.0102 |
| 0.62 | 1.983 | 1.209 | 0.626 | 0.561 | 0.0109 |
| 0.667 (`h2_bridge`, audit §3.1) | 2.048 | 1.289 | 0.627 | 0.581 | 0.0114 |
| 1.00 | 2.589 | 1.915 | 0.834 | 0.823 | 0.0154 |

Three findings.

1. **The objective is flat.** Anything in w₁ ∈ [0.2, 0.62] is within 10% of the optimum. The data cannot distinguish "⅓ of revenue comes from one quarter back" from "⅔ does". That is a 2× range on the quantity that drives the entire recognition-timing story, the "share already determined at the guide date", and the FX lag.
2. **The "independent confirmation" is not independent and not the same kernel.** The proposal cites `h2_bridge_gbv_lag_conversion.csv` (Q3 17.39/17.15/17.18, Q4 11.95/12.12/12.03) as proof the kernel is stable. I reproduced those figures exactly at **w₁ = 0.667** — the audit's kernel, not the proposal's. At the proposal's w₁ = 0.38 the same quarters are 17.06/16.77/16.98 and 11.80/11.93/11.94. **Two nearly opposite kernels are both "remarkably stable"**, which proves the stability is a property of GBV's smooth seasonal path, not evidence about `Φ`.
3. **The seasonal claim runs the wrong way in the data.** Q1's dispersion is *minimised at w₁ = 0* and rises monotonically; Q3's is minimised at w₁ ≈ 0.62. The proposal's mechanism story ("Q1 cohorts book long, Q4 cohorts book short") is asserted from the direction of a within-3-to-4-observation optimum. Q3 and Q4 have **three** observations each in the 2023+ window. A 4×4 seasonal transition matrix will be fitted on 3-4 points per row.

### 1.3 The double count is not closed by construction — here is the concrete case

The proposal's §2.3(a) claim is that denominating in host payout makes the fee double count "arithmetically impossible". It is impossible *inside* `schedule()`. It is not impossible *at the interface*, and §9 admits as much ("if they hand me reported ADR … the double count returns"). That is a request, not a construction.

Concretely, with two terms moving together and counted twice:

- Lens 1 builds regional ADR from reported ADR ex-FX. The audit's ADR decomposition leaves an **unidentified +3.6pp pricing / sub-regional residual** (context; audit §3.4-3.5). Roughly half of listings were on the single 15.5% fee by 2Q26 (`06_fee_timeline.csv`, 2026-06 row), and a migrating host must gross up ~11.5-14.8pp of list price. GBV-weighted, that is plausibly **+2 to +5pp of reported ADR in 1H26** — i.e. a large slice of the unidentified residual *is* the migration.
- M6 asks for `H` = host payout per night. To produce it, lens 1 must divide reported ADR by `(1 + migrated_share × θ × 14.79%)`.
- M6 then multiplies it back: `g(H, m_q)` grosses the same payout up by the same factor.
- If lens 1 does **not** purge (or purges with a different `m_q` or a different θ), the migration is in both the ADR residual and `g(·)`. At 50% migrated and θ = 0.83 that is ~+6.1% on GBV counted twice, i.e. ~$1.7bn of FY27 GBV and ~$260m of FY27 revenue.
- Worse: `m_q` is **fitted**. The Stan block includes `gbv_obs ~ normal(gbv_hat, σ_g)`. If `H` arrives un-purged, the fit will attribute the un-purged gross-up to `m_q`, raise the migrated share, and *also* raise revenue through `τ(m_q)`. The estimator has a positive-feedback path from "unexplained ADR strength" straight into "the fee edge", which is precisely the number the pitch rests on.

The fix is not a handshake. It is: **make `m_q` exogenous and dated** (from `06_fee_timeline.csv` disclosures: 0 / ~15 / ~25 / ~50 / deadline-forced ~100), **never** estimated from GBV, and have M6 — not lens 1 — own the single de-gross-up step so only one file applies it.

### 1.4 Two undisclosed plugs inside the headline numbers

- **The 3Q26 conversion.** §5 builds `4,830 = 16.645% × [0.38·GBV_2Q26 + 0.62·GBV_1Q26] × 1.015 × 1.0052`. I verified the arithmetic (28,440 × 0.16645 × 1.015 × 1.0052 = 4,829.8). But 16.645% is **below every historical Q3 value** at that kernel (17.065 / 16.770 / 16.978, mean 16.938). No derivation is given. At the three-year mean the same build gives **$4,915m**, 3.0% above the top of the guide range. The "two methods with no shared parameter agreeing to 60bp" with the frozen card ($4,801m) is manufactured by a silent 1.8% haircut to the conversion — and the two methods share the entire GBV history anyway.
- **FX in the headline differs from FX in the table.** §5's 3Q26 build uses "+FX 0.73% − hedge 0.21%"; §2.5's forward schedule says 3Q26 gross **+1.04**, after hedge **+0.83**. Both cannot be right, and the difference is $15m.

### 1.5 Parameter count

§4 claims 11 free parameters against ~79 observations. The Stan sketch declares `vector[T] H` among `parameters`. With T ≈ 23 that is 23 more free parameters, and they exactly absorb the 23 GBV observations the count relies on. Add `σ_r, σ_g, σ_u`, the free `p_q`/refund measurement-error term, `τ_eff` (called deterministic but see §1.4), and the count is closer to **35-40 against ~56 non-trivial observations**, several of which are interval-censored and therefore worth a fraction of a data point each.

**Justification for 3/10.** The estimand is the right one and two of the priors (`s_R` from the disclosed 56% non-USD revenue share, `s_G` from the nights mix) are genuine accounting anchors — that is real and it is why this is not a 1. But the hardest pin is circular, the kernel is flat over a 2× range, the overlap fix is contractual, the headline conversion carries an undocumented 1.8% haircut, and the parameter count omits a T-vector.

---

## 2. Axis 2 — Point-in-time safety and backtest validity. **Score 4/10**

The protocol is the best-specified of the six proposals: refit at **guide dates** rather than quarter-ends, information set = letters and 10-Qs filed strictly before, FRED through the prior day, `spec_id` frozen in `20_experiment_spec.json`, and an explicit warning about the LSEG-vs-Zacks vintage trap. Credit where due; `20_vintage_register.csv` and `20_frozen_q3_2026.csv` both exist and are the right artefacts. Then five leaks:

1. **The restated backlog contains the forward guide.** §1.1 above. The 2Q26 restated value is `0.697 × $4,730m`. Any replay that uses the restated series at the 6 Aug 2026 guide date is conditioning on the thing being forecast.
2. **`d_q`'s coverage norms are full-sample.** "2023-25 seasonal coverage norms" applied inside an expanding-window replay whose origin is 4Q22 means every pre-2026 replay uses a statistic computed from its own future.
3. **10-Q hedge data post-dates the guide.** `28_fx_hedge_disclosures.csv` is hand-extracted from 10-Qs. The guide is issued with the shareholder letter; the 10-Q follows days later. So `designated_notional`, `aoci_cash_flow_hedges_musd`, `reclassified_to_revenue_musd` and `expected_reclass_next_12m_musd` for the just-closed quarter are **not** in the guide-date information set. `gross_fx_ex_hedge_pp` — the proposal's FX *target* — is constructed from `reclassified_to_revenue_musd`, so the target itself is not PIT-available at the date the feature is formed. The proposal's own PIT rule forbids what §2.5 does.
4. **The booking-curve prior is one 2026 vintage.** `booking_curves_by_market.csv` (600 rows, 120 markets) is a single Jul-Aug 2026 snapshot; the insider note flags it **"unusable for y/y — single vintage, host blocks included, calendars carry no price"**. Using it as the Dirichlet centre at a 2023 replay origin is look-ahead. It is soft (a prior worth ~4 quarters of data, by the proposal's own tuning — which is a *lot* against 23 observations), but it is look-ahead.
5. **The reprice panel is Mar-Aug 2026.** `12_reprice_summary.csv` windows are all 2026. Any replay before 2026 that uses θ is using 2026 information; and see §3.2 for whether it measures θ at all.

Two things the proposal gets *right* that the incumbent does not: forecasting the **guide** (an event with a known date) rather than the surprise, and entering qualitative guide buckets as interval likelihoods rather than midpoints. Keep both.

**Justification for 4/10.** Protocol design 8/10; execution against its own protocol 2/10. The FX target and the backlog pin both violate the rule the same document writes down.

---

## 3. Axis 3 — Statistical power and overfitting. **Score 4/10**

### 3.1 The FX comparison is not a comparison

§2.5's table sets "Two-index fit, λ and scale free: **1.08pp**" against "Incumbent: LOO RMSE **2.30pp**". Two separate errors:

- **In-sample versus out-of-sample.** 1.08 is the fit of a two-parameter model to the same 14 points. 2.30 is a leave-one-out statistic. A two-parameter in-sample RMSE at n=14 should be compared to the incumbent's *in-sample* RMSE, or the proposal's own LOO should be reported. It is not.
- **Wrong window.** 2.3038 is `rev_fx ~ eurusd_avg12` in the **`ex21`** window, n=17 (`05_fx_fits.csv`). The proposal scores its own model on **1Q23-2Q26, n=14** — that is the `post22` window, where the same driver's LOO is **1.8133**, and where better single-driver fits already exist: `usd_broad_avg01` LOO **1.2868**, `eurusd_avg01` **1.3411**, `eurusd` lag 1 **1.4704**, `usd_broad` lag 1 **1.5503**. The honest sentence is: *a two-parameter in-sample fit at 1.08 does not beat an existing one-parameter LOO fit at 1.29.*

### 3.2 The target is integers, and nobody has the power to tell 1.40 from 1.08

`stated_revenue_fx_pp` in `28_fx_hedge_disclosures.csv` is **−4, −1, 4, 3, 0, 0, 0, 0, −2, 0, 0, 1, 3, 4** — every value an integer, six of fourteen exactly zero. `gross_fx_ex_hedge_pp` adds a sub-point hedge correction to that. I computed the series' sd: **2.337pp**, so a constant-mean predictor scores RMSE 2.337.

Consequences the proposal should have stated:
- The incumbent baseline it nominates (2.30) is **no better than predicting the mean.** Halving it is not an achievement.
- The SE of an RMSE estimate at n=14 is roughly RMSE/√(2n) ≈ **0.26pp**. So 1.40 (H1) versus 1.08 (two-index) versus 1.94 (H2) sit inside roughly one standard error of each other. **The proposal's central empirical result — that check-in translation beats booking-lock — is not statistically distinguishable on this target.** The memo asserts a mechanism from it anyway (`λ = 0.75`, a Beta(3,1) prior, and a forward FX schedule to two decimals).
- The proposal's own fix (score on an interval likelihood, `[x−0.5, x+0.5]`) is correct and should be applied *before* any of the comparisons in §2.5 are quoted, not after.

### 3.3 The kernel is fitted to the statistic used as its evidence

`Φ = (0, 0.38, 0.62, 0)` is described as "the weights that minimise pooled within-quarter dispersion". The dispersion is then reported as the evidence the kernel is right, and "removes 60.0% of the printed take rate's variance" is an in-sample R²-equivalent on two free parameters against 14 points. Report leave-one-quarter-out, or nothing.

### 3.4 The crude version ties the incumbent and loses to a one-line rule

The proposal's own honest paragraph: crude kernel PIT one-step revenue error **mean +0.17%, sd 2.33%, MAE 1.82%** (n=10) against the incumbent's **+0.40% / 2.48% / 1.83%**. That is a tie on MAE.

What it does not do is compare to **its own nominated baseline #2**: guide midpoint × (1 + trailing-8 median cushion), stated at **1.1% mean error, 19/19**. I verified 19/19 and 15/19 in `02_guidance_cushion_series.csv` (`beat_vs_mid_pct` positive in all 19 rows; `beat_vs_high_pct` negative in 4). For 3Q26 that rule gives 4,730 × 1.0179 = **$4,815m**; the mechanical build gives **$4,830m** — **0.3% apart**, against a cushion whose last-eight realisations span 0.86% to 3.27% (±1.2%). So on the one quarter the memo will be judged on, a Bayesian state-space model with 4 seasonal simplexes, a dated fee schedule and a two-index FX basket produces a number 0.3% away from multiplying the guide by 1.0179.

### 3.5 Does it repeat a failed design?

Mostly **no**, and the proposal's defence is fair: it uses no exogenous demand predictor, so the Trends / macro / peer / tone negatives (audit §4.2) genuinely do not bind, and it accepts the AR(1)-beats-everything-for-nights result. The two negatives that *do* bind are handled badly: the backlog negative (WF 1.17× naive, `08_backlog_tests.csv`) is "fixed" by the circular restatement (§1.1), and the letter-rounding contamination (audit §4.2c, `predictive/03_nowcast_tests.py:48-51`) is acknowledged and then ignored in every number quoted.

**Justification for 4/10.** The strategic argument — *replace free parameters with accounting restrictions rather than hunt for features* — is exactly right for n≈23 and is the best paragraph in the six proposals. The tactical execution reports an in-sample two-parameter fit against an out-of-sample one-parameter baseline from a different window, on a target that is integer-rounded, and never benchmarks its headline quarter against the one-line rule it itself calls "the bar".

---

## 4. Axis 4 — Tradeability over 3-12 months. **Score 5/10**

**What is right.** The output object is correct: a distribution over the *printed guide range* on 5 Nov, which is the only ABNB event between the finals and year-end, and which plugs directly into the repo's one executable survivor ("guide below Street → 9/9 negative 20-day drift, mean −4.21%"). The FX-to-margin translation (0.47 EBITDA margin points per point of revenue FX) and the multiple link (+0.48 turns per point of forward revenue growth) give a complete path from a take-rate basis point to a price. No other lens closes that loop.

**What breaks it.**

1. **The edge is smaller than the admitted uncertainty.** Claimed 4Q26 = $3,284m vs Street $3,200m = **+2.6%**, of which +2.52% *is* the fee uplift. The memo simultaneously admits a **3pp / $90M** spread across three defensible FX constructions. The error bar is larger than the signal, by the author's own accounting.
2. **The edge is smaller than the consensus dispersion.** `04_current_consensus.csv`: 4Q26 Zacks $3,200m from **10 estimates spanning $3,050-3,700m**. And the quarterly consensus does not tie to the annual: 2,678 + 3,608 + 4,740 + 3,200 = **$14,226m** against an FY26 consensus of **$14,100m**. An $84m disagreement with a number that disagrees with itself by $126m is not a trade.
3. **The sign of the tradeable signal flips on the θ correction.** Guide midpoint implied by the model = posterior ÷ (1 + cushion). At $3,284m: 3,284 / 1.0179 = **$3,226m, above Street** — the 9/9 drift rule does not fire, so the model's central case says *no trade*. Apply the θ correction of §5 below (uplift +1.1% instead of +2.52%): revenue $3,239m → implied guide **$3,182m, below Street $3,200m** — the rule fires, *bearish*. **The direction of the only executable signal in the repo is determined by the one parameter the proposal mis-specified.**
4. **The mechanism-of-disagreement argument is circular.** "`3,284 / 1.0252 = $3,203m`, therefore the Street's Q4 is exactly our model with the fee set to zero" is presented as proof of edge. Read the other way it says: *every non-fee component of this model reproduces consensus*, i.e. the model contributes exactly one assumed parameter and nothing else. That is a one-variable pitch, and the variable is contested (§5).
5. **Calendar error.** "All three are observable on 5 Nov 2026, **before the finals reconvene**." Finals are **22-24 Oct**. The thesis is unfalsifiable within the competition. For a real PM on a 3-12 month horizon this is fine — for the memo it is a sentence a judge will delete for you.
6. **It inverts the team's existing Q4 call**, which the proposal flags honestly. Good. But the reconciliation it promises ("four days") is precisely the FX question it could not resolve for 3Q26, where it misses management's own guided number by 2.2pp.

**Justification for 5/10.** Right object, right event, right translation to price; but the claimed alpha is smaller than the FX spread, smaller than the consensus dispersion, and its sign is hostage to one misread parameter.

---

## 5. Axis 5 — Buildability in three weeks by 3-4 undergraduates. **Score 5/10**

### 5.1 The data map is mostly honest. I spot-checked 31 paths.

Every cited path **exists** and every row/column count I checked was accurate: `02_kpi_panel_quarterly.csv` (24 rows, `gbv_musd`/`take_rate_pct`/`fx_pts_revenue`/`fx_pts_adr` present), `abnb_backlog_indicators.csv` (23 data rows 4Q20-2Q26), `28_fx_hedge_disclosures.csv` (14 rows, `non_usd_revenue_share` 0.54→0.56, `designated_notional_pct_of_ltm_non_usd_revenue` 10.5→46.1), `28_fx_hedge_forward.csv` (4 rows, −0.21/−0.21/−0.18/−0.18pp), `28_fx_hedge_tests.csv` (gross-ex-hedge lag-0 r 0.763, **lag-1 r 0.861**, lag-2 0.582 — verified), `10_fx_quarterly.csv` (37 rows), `10_fx_daily.csv` (19,467 rows), `10_fx_basket.csv` (23 rows with the judgemental weights as described), `06_fee_timeline.csv` (19 dated events; the 15 Sep / 13 Oct deadlines are **not** in this file — the 2026-07 row says only "to complete during 2026"), `fee_split_elasticity_scenarios.csv` (60 rows), `booking_curve_daily.csv` (44,379), `booking_curves_by_market.csv` (600), `h2_bridge_gbv_lag_conversion.csv` (6 rows, values verified), `29_*` bridge files, `05_fx_fits.csv` (26 rows), `08_backlog_tests.csv`, `02_guidance_ledger.csv` (194 statements), `04_current_consensus.csv` (verified line by line), `13_driver_model.py` (the `take = b["take"] + take_bps/10000` and `wedge = (1+rev_fx)/(1+adr_fx) − 1` construction is exactly as described; `take_bps` base = 0.0 for 2026 and 2027). Two mis-rootings: `Citadel-ABNB-fx-engine/` and `FX_ENGINE_MENTAL_MAP.md` are **siblings of** `Citadel-ABNB/`, not inside it.

**Two files do not contain what is claimed, and both are on the "cannot be cut" list.**

### 5.2 `06_quote_line_items.csv` cannot measure the tax/cleaning de-rate

The proposal's day-3C task: "Measure the tax+cleaning share of GBV from `06_quote_line_items.csv` (`li_taxes + li_cleaning_fee` over `li_nightly_subtotal`), city-weighted." I opened it. The `li_*` columns are **counts of quotes in which that line item appears**, not dollar amounts:

```
austin, 2026-03-25, quotes 7968, li_nightly_subtotal 7926, li_taxes 18.0, li_cleaning_fee 0.0
```

Across all 76 rows: `li_nightly_subtotal` = 1,394,998, `li_taxes` = 40,723, `li_cleaning_fee` = **88**. A cleaning fee is present in 88 of 1.71M quotes. The prescribed ratio evaluates to **2.93% — a ratio of counts**, meaningless as a share of GBV. The 11% de-rate hard-coded in the §6 skeleton is therefore an **assumption**, classified in the memo's own table as "measurable, not yet measured".

Separately, the de-rate **does nothing to the headline anyway**: `rev *= (1 − tax_clean_sh)` multiplies the split-fee and single-fee legs identically, so it cancels out of the +4.05% ratio. The table row claims it "de-rates the above"; the code says otherwise. Delete the row or re-derive it.

### 5.3 `12_reprice_summary.csv` does not measure θ

The memo calls θ "the only hard number on host behaviour", quotes **0.833-0.845**, and classifies it *measured*. I opened all 420 rows:

- `mean_jump_pp` takes only **half-integer values** — 11.5 (65 rows), 12.5 (13), 14.5 (7), 13.5 (4), 17.5 (4). These are **histogram bin midpoints**, not estimates.
- `theta` = `mean_jump_pp / 13.8` exactly, and ranges **0.833 to 1.407** across the 402 non-blank rows and 34 markets — not 0.833-0.845, which is the Austin sub-sample the memo happened to read.
- `excess_share_12_20` — the excess mass of listings repricing into the payout-neutral band relative to baseline — has **median 0.0029 and 90% of rows below 0.01**. The identified excess is ~0.3pp of listings. It is indistinguishable from zero.
- `share_lt_m10` ≈ 0.255 versus `share_gt_10` ≈ 0.178: **more** listings cut price by >10% than raised it by >10% in the migration window.

**Conclusion: host re-pricing pass-through is unidentified in this dataset.** The proposal's own §8 answer to "Inside Airbnb failed 36 tests" is that it uses the panel only for "the *measured* pass-through θ" and "the *cross-sectional* tax/cleaning share". Neither exists in these files.

### 5.4 The θ correction, done properly — this is the number that decides the pitch

Constant host payout (the memo's arithmetic, which I verified): per $97 of host net, split → GBV 114.10, revenue 17.10, take 14.99%; single → list 97/0.845 = 114.79, GBV 114.79, revenue 17.79, take 15.50%. **GBV +0.60%, revenue +4.03%, take +51bp.** Correct — *conditional on the host raising list price by the full +14.79%.*

Now let the host pass through only θ of that:

| θ | list jump | new GBV vs split | new revenue vs split | host net vs before |
|---|---|---|---|---|
| 1.00 (memo) | +14.79% | **+0.60%** | **+4.03%** | 0.0% |
| 0.833 (memo's own citation, vs 14.79) | +12.32% | **−1.56%** | **+1.81%** | −2.2% |
| 11.5pp actual modal jump | +11.50% | **−2.28%** | **+1.07%** | −2.9% |

So the migrated-cohort revenue uplift is **+1.1% to +1.8%**, not +4.05%, and **GBV falls** on the migrated cohort rather than rising. Note also that the memo's table calls θ a GBV-channel-only effect. That is arithmetically false: under the single fee, revenue **is** 15.5% of GBV, so anything that moves GBV moves revenue one-for-one. And the `schedule()` function in §6 takes no θ argument at all — θ appears in the prose and the data map and nowhere in the specification.

Rippling through: FY27 "+2.3% take rate vs Street" becomes **+0.6% to +1.0%**; 4Q26 "+2.52%" becomes **+0.7% to +1.1%**; 4Q26 revenue $3,284m becomes **~$3,232m**, versus Street $3,200m. Combined with the FX spread the memo already admits, the central case is indistinguishable from consensus.

### 5.5 Schedule realism

Three weeks, 3-4 undergraduates, for: a Stan state-space model with four seasonal simplexes, an ordering constraint, a random-walk retention state, two interval-censored likelihood families, an expanding-window replay at 19 guide dates with strict vintages, split conformal calibration, a scenario tree with base-rate branch probabilities, *and* an R-engine cross-validation to 0.1%. That is a term-long project. The proposal's cut list is honest and correctly ordered, and the **minimum viable version — constrained least squares on the kernel + the dated fee schedule + one FX basket + the four-way reconciliation — is genuinely a week's work and carries most of the value**, precisely because (per §3.4) the Stan machinery buys 0.3% over multiplying the guide by 1.0179.

**Justification for 5/10.** Almost everything is on disk and the fallback is real. But two of the four items declared un-cuttable are impossible with these files, and the full build is 3× the available labour.

---

## 6. Axis 6 — Defensibility in two pages and ten minutes of hostile Q&A. **Score 5/10**

**One-sentence version (the memo's, cleaned up):** *Airbnb recognises revenue at check-in but books GBV at reservation, so most of any quarter's revenue is already on the ledger before the quarter starts; price that ledger with one dated fee schedule and one FX basket and you get the guide before management prints it.* That is a good sentence and it is memo-ready.

**The number a judge attacks first: +4.05%.** It is the headline, it is 100% of the disagreement with the Street, and it is labelled "measured (arithmetic on published rates)". The attack is one line — *"that's true only if hosts raised list prices by the full 14.8%; your own Austin panel says they raised by 11.5%, so your uplift is 1.8% and your GBV falls"* — and **the proposal has no answer.** §8 pre-empts five questions and this is not one of them. Worse, the memo *cites* the θ file as supporting evidence, so the judge will have it open.

**Second attack, and it is in the memo already:** *"your FX model misses the quarter management has already guided by 2.2pp; why should I believe your Q4 FX?"* The answer offered — "believe the reconciliation, not the point estimate" — is not a number, and a Citadel panel will read it as "my model does not work yet".

**Third attack:** *"you are using a balance sheet you restated using next quarter's revenue."* Fatal in public if anyone opens `03_insider_mechanics.md` §1.5.

**What is defensible:** the Mertz quotes (2Q22 "any of the variation in take rate is just a timing difference between revenue stays versus timing of bookings"; 2Q26 "accounting for the timing of bookings versus check-in with Reserve Now, Pay Later") genuinely support building the model management describes. The two-sided take-rate framing — single-fee uplift *versus* the 29 Aug 2026 direct-link pilot at 6-10%, worth −80bp at 10% of nights — is the most sophisticated point in any of the six proposals and is the right way to present a policy variable. The hedge warning ("anyone who adds it separately understates revenue by ~0.2pp a quarter") is correct and worth a footnote in the memo.

**Justification for 5/10.** Excellent framing and quote ledger; the first two questions a judge asks have no answer in the document.

---

## 7. The FX-lag hypothesis, tested directly

**Theo's working hypothesis:** today's FX move hits reported revenue roughly two quarters ahead, because the USD value is largely struck at booking and revenue lands at check-in.

### 7.1 Does the proposal derive the lag weights from data? **No.**

It does not use the booking lead-time distribution to build the lag. It does two things:
- fits a **single scalar λ** (share remeasured at check-in versus locked at booking) on **14 letter-rounded integer observations**, landing at λ = 0.75;
- convolves with the **same `Φ` kernel** that §1.2 shows is flat over w₁ ∈ [0.2, 0.62].

So the lag weights are `(1−λ) × Φ`, i.e. the product of an under-powered scalar and a weakly identified kernel. The booking-curve file — the only object that could give a lead-time density — is explicitly labelled by the insider note as *"unusable for y/y — single vintage, host blocks included, calendars carry no price"*, and the proposal uses it only as a Dirichlet centre worth ~4 quarters of data.

### 7.2 The proposal's own result contradicts Theo — and the repo contradicts the proposal

λ = 0.75 means **75% of FX is struck at check-in**, i.e. essentially contemporaneous. Effective lag ≈ 0.25 × E[k] ≈ 0.4 quarters, not 2. And H2 (full booking lock, the two-quarter story) scores **worst** of the three specs (1.94 vs 1.40). Read literally, the memo **refutes** the working hypothesis — and never says so.

But the repo's strongest single piece of FX evidence points the other way, and the proposal walks past it. From `10_fx_basket.csv`, the global revenue-weighted basket y/y is **1Q26 +5.60%, 2Q26 +2.19%, 3Q26 +0.32%** (QTD to 28 Aug). With the disclosed non-USD revenue share of 0.56:

| specification for 3Q26 gross revenue FX | computed | vs management's guided ~+3.2pp gross |
|---|---|---|
| contemporaneous (λ = 1): 0.56 × 0.32 | **+0.18pp** | −3.0pp |
| proposal's two-index (λ = 0.75) | **+1.04pp** | −2.2pp |
| **two-quarter lag (λ ≈ 0): 0.56 × 5.60 (1Q26 basket)** | **+3.14pp** | **−0.06pp** |

The two-quarter-lagged basket reproduces the guided number to within 0.1pp. The same pattern holds at 2Q26: stated gross FX **+4.61pp** against a contemporaneous basket of only +2.19% (which would give +1.23pp) — the contemporaneous specification cannot generate the observed magnitude at all, while a one-to-two-quarter lag can. This is consistent with `28_fx_hedge_tests.csv`'s lag-1 r **0.861** > lag-0 **0.763** > lag-2 **0.582**, and with the insider note §2.4's own headline ("Revenue FX lags spot by one to two quarters").

**The 2.2pp miss the proposal flags as "the item to put in front of a PM" is not a basket-frequency problem. It is the lag.** The memo lists three candidate explanations — daily baskets, GBV-weighting at booking date, cross-currency fee contamination — and omits the obvious fourth: **λ is near 0, H2 is right, and the RMSE test that rejected it lacked the power to detect anything** (§3.2: differences of 0.3-0.9pp against an SE of ~0.26pp on an integer-rounded target).

### 7.3 Is the "already-determined share at the guide date" computed correctly? **No.**

The memo says 4Q26 will be "~100% determined on volume and ~80% determined on FX (the 4Q26 check-in basket is one quarter forward of a spot that is 82% observed by early November)". The 82% is `q4_driver_realised_share` from `29_fx_step_down.csv`, whose own note reads: *"Q4 fit −0.43pp on EUR y/y of +0.50% averaged over 2Q26-3Q26; 82% of that driver is already observed."* That is the realised share of a **two-quarter-lagged driver** — a number that only exists in the lagged model the proposal rejects.

Under the proposal's own λ = 0.75, the relevant object is the **4Q26 average basket**, of which at 5 Nov 2026 roughly **35 of 92 days (38%)** have elapsed. The correct determined share is

```
0.25 × 1.00  +  0.75 × 0.38  ≈  0.54
```

not 0.80-0.84. The memo has imported the lagged model's comfort while running the contemporaneous model's arithmetic. Under the lagged model (λ ≈ 0) the share genuinely *is* ~100%, and the 4Q26 gross FX would be 0.56 × (a blend of 2Q26 +2.19% and 3Q26 +0.32%) ≈ **+0.6 to +1.2pp**, not the +0.62pp gross / +0.41pp after hedge in the forward table — close by accident, for the wrong reason.

### 7.4 What would falsify the lag hypothesis

Pre-register these, all runnable this week with files on disk:
1. **Joint regression, interval likelihood.** Regress `gross_fx_ex_hedge_pp` on the contemporaneous and one- and two-quarter-lagged revenue-weighted baskets, **jointly**, with the letter-rounding scored as `[x−0.5, x+0.5]` rather than a point. Falsification: if the contemporaneous coefficient dominates and the lagged coefficients are not jointly different from zero, λ ≈ 1 and Theo is wrong. Report the confidence set, not the point — at n=14 it will be wide, and say so.
2. **Over-identification on the disclosed share.** Under λ ≈ 0, the fitted scale on the lagged basket must equal the disclosed non-USD revenue share (0.56). Falsification: a fitted scale materially away from 0.56 means the basket weights (judgemental, `10_fx_basket.csv`) are wrong, not the lag.
3. **The ADR leg as a control.** ADR FX *must* be contemporaneous-at-booking. The memo's own `s_G = 0.66` result on the ADR leg (RMSE 0.76pp) is the clean case. If the revenue leg needs a lag that the ADR leg does not, the wedge **is** the recognition lag and it is measurable as `revenue_FX − ADR_FX`. Run that difference against basket lags directly: it is a two-line test and it is the sharpest form of the hypothesis.
4. **The 5 Nov 10-Q.** If management's "FX" sentence bundles the cross-currency service fee with translation, the derivatives note and the revenue disaggregation will show it. That is the memo's best disclosure-finding candidate and costs nothing.

### 7.5 Verdict on the hypothesis

Theo is **probably right, and the proposal has not established it**. The single strongest piece of arithmetic in the repo — 0.56 × the 1Q26 basket of +5.6% = +3.14pp against a guided ~+3.2pp for 3Q26 — supports a two-quarter lead, and the contemporaneous specification cannot reproduce either 2Q26 or 3Q26 stated FX. The proposal's λ = 0.75 is fitted on fourteen integers with no power to separate the hypotheses, and it then imports the *lagged* model's "82% determined" comfort into a *contemporaneous* model. Fix the target (interval likelihood), fix the estimand (joint lag regression on the revenue-minus-ADR wedge), and state the λ confidence set honestly. Until then, no FX pp in this memo should be quoted to two decimals.

---

## 8. Scores

| Axis | Score | One-line justification |
|---|---|---|
| 1. Identification | **3/10** | Hardest pin is circular (`restated ≡ norm × next-quarter revenue`); kernel flat over a 2× range; overlap fix is a contract with lens 1, not a construction; headline conversion carries an undocumented 1.8% haircut; parameter count omits a free T-vector `H`. |
| 2. PIT safety / backtest validity | **4/10** | Best protocol of the six (guide-date refits, vintage register, interval-censored buckets) — violated by its own inputs: the restated backlog embeds the forward guide, the FX target is built from 10-Q data filed after the guide, `d_q` norms are full-sample, the booking-curve prior is a single 2026 vintage. |
| 3. Power / overfitting | **4/10** | Right strategy (constraints, not features), wrong execution: in-sample two-parameter 1.08 vs a LOO 2.30 from the wrong window (the matching-window LOO is 1.29); differences of 0.3pp against an SE of 0.26pp on an integer target; kernel fitted to the statistic used as its evidence; never benchmarked against the guide+cushion rule it nominates. |
| 4. Tradeability (3-12m) | **5/10** | Right object (a distribution over the 5 Nov guide) and a complete path to price; but claimed alpha (+2.6% on Q4) is smaller than the admitted 3pp FX spread and the consensus dispersion ($3,050-3,700m), and the sign of the executable signal flips on the θ correction. |
| 5. Buildability in 3 weeks | **5/10** | 31 of 31 cited paths exist and counts check out; but two "cannot be cut" measurements are impossible with those files, and the full Stan + R-engine + conformal build is 3× the available labour. The MVP (constrained LS + fee schedule + one basket + the reconciliation) is real and is a week. |
| 6. Defensibility | **5/10** | Memo-ready sentence, strong quote ledger, genuinely sophisticated two-sided take-rate framing; but the first and second questions a judge asks (+4.05% under θ<1; the 2.2pp 3Q26 FX miss) have no answer in the document. |

---

## 9. FATAL flaws

**F1. The restated-backlog identification pin is circular.** `d_q` is defined as the gap between reported unearned fees and `coverage_norm × next-quarter revenue`, so `reported × (1 + d_q) ≡ coverage_norm × next-quarter revenue`. The 2Q26 value is `0.697 × the 3Q26 guide midpoint`. Pin #1 of four cannot be used as specified, and the day-2A test that the proposal calls decisive will pass trivially and mean nothing.

**F2. The headline fee uplift assumes away the one thing the repo tried to measure.** +4.05% requires θ = 1. At the memo's own cited θ the uplift is +1.8% and migrated-cohort GBV *falls* 1.6%; at the modal 11.5pp jump it is +1.07% and GBV falls 2.3%. And θ is not actually measured: `12_reprice_summary.csv` carries bin-midpoint jumps, θ ∈ [0.833, 1.407] across 402 rows, and an excess repricing mass of ~0.3pp of listings. The number that carries 100% of the disagreement with the Street is an assumption dressed as arithmetic, and it is contradicted by the file cited in its support.

**F3. The FX block's central comparison has no statistical content.** In-sample two-parameter RMSE against an out-of-sample one-parameter baseline from a different window, on a target that is integer-rounded and whose sd is 2.34pp at n=14. λ = 0.75 is not identified; the three spec RMSEs (1.08 / 1.40 / 1.94) sit inside ~one SE of each other. Every FX pp quoted to two decimals in §2.5 is over-stated precision, and the forward schedule built from them is the input to the 4Q26 call.

---

## 10. MUST-FIX (ordered; 1-4 are pre-conditions for using any of this in the memo)

1. **Delete the `1/(1−d_q)` restatement as an identification pin.** Either identify `Φ` from the column-sum restriction plus an exogenous prior alone, or build a *genuine* balance-sheet restatement that does not reference next-quarter revenue (e.g. model prepaid share `p_q` and RNPL GBV share explicitly and let unearned fees be a residual you *predict*, not one you back-solve). If the team keeps the restated series, it must be excluded from every feature set and every PIT replay.
2. **Re-derive the fee uplift with θ as an explicit, uncertain parameter, and put it in `schedule()`.** Report the uplift as a **range (+1.0% to +4.0%)**, with the central case at θ ≈ 0.83-0.9 (+1.8% to +2.5%), and state that θ is *unidentified* in Inside Airbnb, not measured. Carry the GBV sign correctly: at θ < 1, migration **reduces** GBV on the migrated cohort. Re-run the Street bridge with the range, and show the pitch's direction under both ends.
3. **Re-score the FX block on the interval likelihood *before* quoting any comparison**, and re-benchmark against `05_fx_fits.csv` **`post22`** (best one-parameter LOO 1.2868), not `ex21` (2.3038). Report your own LOO, not your in-sample fit. Report a confidence set for λ.
4. **Run the lag test in §7.4 and let it set λ.** Specifically: regress the `revenue_FX − ADR_FX` wedge on contemporaneous and lagged baskets. If the lag wins, rebuild the forward schedule and recompute the determined-share (§7.3) as `(1−λ) + λ × (days elapsed / days in quarter)` — at λ = 0.75 and 5 Nov that is **~54%, not 82%**.
5. **Fix the parameter count and the Stan block.** Either `H` is data from lens 1 (then say so, and drop the 23 GBV observations from the count) or it is estimated (then say 34+ parameters). Do not claim 11 against 79.
6. **Make `m_q` exogenous and dated**, never fitted against GBV, and own the ADR de-gross-up step inside M6 so the migration is removed in exactly one place. Write the interface as an equation, not a request to lens 1.
7. **Document the 16.645% 3Q26 conversion** or replace it with the three-year Q3 mean (16.94%), which gives $4,915m. Do not present a haircut that manufactures agreement with the frozen card as independent validation.
8. **Drop the tax/cleaning de-rate row**, or re-source it. `06_quote_line_items.csv` holds field-presence *counts* (cleaning fee: 88 of 1.71M quotes). And note that as coded the de-rate cancels out of the migration ratio entirely.
9. **Benchmark every headline number against guide-midpoint × 1.0179** in the same table. For 3Q26 that is $4,815m vs the model's $4,830m. If the model cannot beat it, say so and sell the *mechanism* (which quarters are pre-determined, and why the cushion is shrinking) rather than the point estimate.
10. **Fix the calendar sentence.** Finals are 22-24 Oct; the 5 Nov print is after. Reframe as a post-competition catalyst for the PM, which is what it is.
11. **Reconcile the 3Q26 FX figure** (+1.04 in the table vs +0.73 in the build) and the λ-vs-lag-structure tension (λ = 0.75 says check-in-dominant; lag-1 r 0.861 > lag-0 0.763 says otherwise).
12. **Re-report the kernel evidence leave-one-quarter-out**, and show the flat grid from §1.2 in the appendix. It is more honest and it is a better argument: *"the kernel is not identified to better than ±0.2 in w₁, and here is what that costs the forecast"* is a Citadel answer; *"the conversion is stable to 0.14pp"* on n=3 is not.

---

## 11. WHAT TO KEEP even if the whole is rejected

1. **The object.** Forecast revenue as a convolution of *already-printed* GBV rather than as a forecast take rate on forecast GBV. This removes the GBV forecast error from the Q4 problem entirely, and it is the audit's own §3.1 recommendation — M6 is the most complete write-up of it. Keep it.
2. **The single-numéraire fee algebra.** The host-payout → (GBV, revenue) mapping, evaluated once, is the correct way to stop the ADR reprice row and the take-rate row from double counting. Keep the function; fix θ inside it.
3. **The hedge rule.** Hedges enter once, in dollars, additively, after pre-hedge revenue; the after-hedge stated FX already contains them. The warning that `28_fx-hedge-disclosures.md`'s "For the model" section reads like an instruction to double-subtract is correct and worth 0.2pp a quarter. Put it in the model README.
4. **Interval likelihoods everywhere.** Guide buckets as `lo ≤ x ≤ hi`, letter-rounded FX as `[x−0.5, x+0.5]`. This is the single cheapest power gain in the repo and it applies to lenses 1 and 3 as well.
5. **The four-way FX reconciliation as a memo exhibit** (repo lagged fit −0.43 / two-index +0.41 / guide-anchored +2.6 / R-engine adapter), with the honest statement that the spread is $90M on 4Q26. A reconciliation with a named cause per term is a better exhibit than a point estimate, and no other lens has one.
6. **The two-sided take-rate framing.** Single-fee uplift versus the 29 Aug 2026 direct-link pilot at 6-10% (−80bp at 10% of nights) versus the hotel credit expiring 31 Dec 2026. "Take rate is now a policy variable with a positive and a negative lever pulling simultaneously" is the best sentence in the six proposals.
7. **`Φ` as a communication device** — "what share of quarter q's revenue is already on the ledger at date t" — even at low precision. It converts "19/19 beats" from a base rate into a mechanism and it is what lens 3 needs.
8. **The RNPL reclassification.** RNPL is a `Φ`/`ρ` effect, not a take-rate lever, and management says so. Correct, cheap, and it removes a plug from the incumbent.
9. **The negative-test triage.** The argument that Trends/macro/peer/tone negatives do not bind on a design with no exogenous demand predictor is correct and should be reused verbatim by the other lenses.

---

## 12. Refutation log

| # | Claim | Attack | Outcome |
|---|---|---|---|
| 1 | Restated unearned fees are a hard accounting pin on `Φ` | `d_q` ≡ gap/reported where gap = `coverage_norm × next-quarter revenue − reported`; so restated ≡ `norm × next-quarter revenue`. 2Q26 = `0.697 × the 3Q26 guide midpoint`. Verified against `03_insider_mechanics.md` lines 182-185 and `abnb_backlog_indicators.csv` | **Refuted** |
| 2 | +4.05% revenue on the migrated cohort, "measured" | Requires θ=1. At θ=0.833 → +1.81% and GBV −1.56%; at the modal 11.5pp jump → +1.07% and GBV −2.28%. `12_reprice_summary.csv` carries bin-midpoint jumps, θ ∈ [0.833, 1.407] over 402 rows, excess repricing mass median 0.0029. θ absent from `schedule()` | **Refuted** |
| 3 | Two-index FX halves the incumbent's error (1.08 vs 2.30pp) | 1.08 is in-sample/2-param; 2.30 is LOO from `ex21` (n=17) while the model is scored on `post22` (n=14), where the incumbent LOO is 1.2868. Target is integer-valued, sd 2.337pp; SE of RMSE ≈ 0.26pp | **Refuted** |
| 4 | `Φ` is over-identified; conversion stability proves the kernel | Grid over w₁: pooled within-Q relative sd 0.0099 (0.33), 0.0099 (0.38), 0.0102 (0.50), 0.0109 (0.62), 0.0114 (0.667). The cited "independent confirmation" file uses w₁=0.667 — a different kernel, equally tight | **Refuted** |
| 5 | Double counting is arithmetically impossible by construction | It is a contract with lens 1, not a construction. The de-gross-up needs `m_q × θ`, the same parameter `g(·)` multiplies back; and `m_q` is fitted against `gbv_obs`, creating a feedback path from unexplained ADR strength into the fee edge | **Refuted** |
| 6 | 11 free parameters against 79 observations | §6 Stan block declares `vector[T] H` as a parameter; 23 GBV observations are absorbed by 23 free `H`; `p_q`/refunds enter as a free measurement-error term | **Refuted** |
| 7 | The Street's Q4 is exactly this model with the fee set to zero — so the edge is one dated schedule change | Read the other way: every non-fee component reproduces consensus, so the model contributes one contested parameter. And Q4 consensus is 10 estimates spanning 3,050-3,700 that do not tie to the FY26 consensus (sum 14,226 vs 14,100) | **Refuted** |
| 8 | The crude kernel already matches the incumbent and needs no GBV forecast | It ties on MAE (1.82 vs 1.83) and is not compared to its own nominated baseline: guide × 1.0179 gives $4,815m vs the model's $4,830m for 3Q26 (0.3% apart, cushion dispersion ±1.2%). **But** the structural claim is true and valuable: at `Φ₀ ≈ 0` the 4Q26 guide needs no same-quarter GBV forecast, which no other lens delivers | **Partially** |
| 9 | "All three killers are observable on 5 Nov 2026, before the finals reconvene" | Finals are 22-24 Oct 2026 | **Refuted** |
| 10 | The tax/cleaning de-rate is measurable from `06_quote_line_items.csv` | `li_*` are counts of quotes containing the field (cleaning fee: 88 of 1.71M quotes); the prescribed ratio is a ratio of counts. And as coded the de-rate multiplies both fee regimes identically, so it cancels out of the +4.05% ratio | **Refuted** |
| 11 | The 4Q26 guide is ~80% determined on FX | The 82% is the realised share of a **two-quarter-lagged** driver (`29_fx_step_down.csv`), imported into a λ=0.75 check-in-dominant model whose 4Q26 basket is ~38% elapsed at 5 Nov. Correct figure ≈ 54% | **Refuted** |
| 12 | H1 (check-in translation) beats H2 (booking lock), so revenue FX is roughly contemporaneous | 0.56 × the 1Q26 basket (+5.60%) = **+3.14pp** against management's guided ~+3.2pp gross for 3Q26, while the contemporaneous basket (+0.32%) gives +0.18pp; 2Q26 stated +4.61pp cannot be generated contemporaneously (+1.23pp) either; lag-1 r 0.861 > lag-0 0.763. The RMSE test that rejected H2 has no power | **Refuted** — and the proposal's own 2.2pp miss is the symptom |

---

## 13. Verdict

**ADOPT WITH FIXES.**

Rejecting this would be a mistake, because the *object* it forecasts is the right one and because it is the only proposal that closes the loop from a basis point of take rate to a share price. But it must not be adopted as written: its headline 4Q26 and FY27 numbers rest on a fee uplift that is roughly 2-4× too large, an FX schedule quoted to two decimals from a fourteen-point integer target, and an identification pin that is algebraically the guide itself. Adopt the architecture; rebuild the numbers under must-fixes 1-4 before anything reaches the memo. If must-fix 1 and 2 are honoured, the honest FY27 position is roughly **+0.5% to +1.5% versus the Street with a −1% to +3% band** — a smaller, defensible edge, which is a better pitch than a large indefensible one.

---

## 14. Interlock with the other five lenses

M6 is a **translation layer, not a forecaster**, and should be positioned that way: it consumes volume and price and emits the guide. From **lens 1 (structural mix state-space)** it needs host payout per night in `usd_constant` by region — and lens 1 must **not** be asked to de-gross-up the fee migration; M6 should own that step with an exogenous dated `m_q`, otherwise the two lenses share the free parameter that carries the entire edge and the double count returns through the estimator rather than through the spreadsheet. In exchange M6 hands lens 1 `s_G` and the FX-neutral deflators that fix the procyclical FX contamination in the nights weights (audit §3.2), which is a clean, one-directional trade. From **lens 2 (nowcast tracker)** it needs nothing for 4Q26 — `Φ₀ ≈ 0` is exactly why — but it needs a 3Q26 GBV nowcast for the *pitch date*, since at 2 Oct / 22-24 Oct the 3Q26 GBV print does not exist and 38% of the Q4 base depends on it; the memo's "100% determined" claim holds only at the 5 Nov guide date, and that asymmetry should be stated explicitly rather than glossed. To **lens 3 (guidance game)** M6 hands the single most valuable thing in this document: `Φ` converts "19/19 beats, cushion shrinking 3.04%→1.86%, range width 4.9%→1.9%" from a base rate into a mechanism (management sees most of the quarter on guide day), and lens 3 hands back the cushion and range-width distributions that turn M6's revenue posterior into a guide distribution — but lens 3 must own the trade, because M6's own central case (implied guide $3,226m vs Street $3,200m) does *not* fire the 9/9 drift rule while the θ-corrected case does, and that decision belongs in one place. From **lens 4 (bottom-up markets)** M6 needs a post-deadline repricing capture to identify θ on the *mandatory* cohort — given §5.3, this is now the highest-value single piece of new work in the whole programme, because θ, not FX, is what the pitch turns on. And with **M5 (ML/LLM extraction)** the division is clean and non-overlapping: M5 extracts the fee, hedge and incentive sentences from the 3Q26 10-Q within hours of the print (designated notional, expected next-12-month reclass, migrated-listing share), M6 consumes them as dated parameters, and neither touches the other's identification. The one rule the synthesis must enforce across all six: **the fee migration, the FX translation and the hedge each appear in exactly one file, and every other lens references that file rather than re-deriving it.** M6 is the right home for all three — it just has to get them right first.
