# Critique of M4 — MOSAIC (interval-censored 120-market panel for nights and home ADR)

Adversarial review, 11 Sep 2026. Reviewer role: Citadel IC + econometrics.
Target: `docs/revenue-forecast-strategy/02_proposals/M4_bottom_up_market_panel.md` (422 lines).
Ground truth read in full: `docs/revenue-forecast-strategy/01_ground-truth/02_model_audit.md` (647 lines).

**Every number below marked [reviewer-computed] was produced by me in this session from repo files; the
code is inline or reproducible from the cited path. Where I confirm the proposal, I say so.**

---

## 0. Verdict up front

**adopt_with_fixes, with a scope cut of roughly 70% and one hard kill-switch.**

Three of MOSAIC's four blocks are either unbuildable from repo data, not identified, or empirically
dead. One block — the dual-price-basis fee-migration exhibit — is a genuine, dated, falsifiable edge
that no Street model has, and it needs **none** of the state-space, the survivorship curve, the
gravity model or the Case–Shiller index to deliver. The reconciliation layer is the right idea but it
is `02_model_audit.md` recommendation 2 restated, it belongs to M1, and MOSAIC's own contribution to
it (the bottom-up measurement M1) is the part I can show adds no information.

The proposal is unusually honest — it states its own binding constraints, refuses to claim it can beat
AR(1), and schedules the null-model comparison that would kill it. I am grading it hard **because** it
is good enough to be taken seriously and therefore good enough to waste three weeks.

---

## 1. IDENTIFICATION — score 4/10

### 1.1 The headline claim is empirically false, and I tested it

MOSAIC's load-bearing measurement equation is

```
(M1)  Δln N̂^cov_{r,q} = Δln n_{r,q} − δ_{r,q} + η,   η ~ N(0, σ_η²),  σ_η ~ HalfNormal(0.02)
```

i.e. the survivorship-corrected covered-panel review flow is a ±2pp measurement of latent regional
nights growth. I built the covered panel — it already exists at the exact target grain, 22,455
market-month rows in `data/processed/abnb_party_size_reviews_v2_market_month_shard{0..5}.csv`
**[verified: 22,455 rows, columns `market, m, reviews, …`]** — mapped the 120 markets to the four
reporting regions by country, aggregated to quarters, and compared to the disclosed regional nights
growth in `data/processed/overnight/02_kpi_panel_quarterly.csv`.

**Result, uncorrected covered review-flow y/y minus disclosed nights y/y, pp [reviewer-computed]:**

| quarter | total | NA | EMEA | LatAm | APAC |
|---|---|---|---|---|---|
| 2023Q1 | **+33.1** | — | — | — | +13.7 |
| 2023Q3 | +14.6 | — | — | +37.3 | +16.6 |
| 2024Q3 | +14.3 | — | — | +37.4 | +12.6 |
| 2025Q3 | +13.1 | +14.2 | +14.6 | +23.8 | +10.2 |
| 2026Q1 | **+20.9** | +20.1 | +20.0 | **+35.9** | +12.8 |
| 2026Q2 | +0.4 | +4.1 | −1.2 | +7.4 | −2.9 |

The wedge the survivorship curve must remove is **not ±2pp; it is +14 to +36pp, region-specific, and
non-monotone in time** (it collapses in the terminal quarter because reviews posted after the scrape
date are missing — a second, opposite-signed truncation the proposal never mentions). `σ_η ~ HN(0.02)`
is mis-scaled by an order of magnitude, and `σ_δ ~ HN(0.01)` on a Gaussian random walk gives a
terminal-quarter prior sd of only 0.01·√24 = **4.9pp** against a wedge that moves 30pp. The filter
will not absorb this in δ; it will distort `g`.

### 1.2 The survivorship correction cannot rescue it, and that is provable, not arguable

`f(age)` is a function of `age = v − t`. In the 120-market store each market has exactly **one**
vintage `v_m`, all inside 14 Jun – 10 Aug 2026 **[verified: `inside_airbnb_current_manifest.csv`,
315 rows, dump dates 2026-06-14 to 2026-08-10]**. So for a given market `age` is a deterministic
affine function of calendar time, and the correction to y/y growth is
`c(a) = s(a) − s(a+12)`, a **common time profile** across markets up to an 8-week spread in `v_m` and
up to market heterogeneity in `f` — which the proposal itself says is *shrunk toward the pooled curve*
for the 107 markets with no deep history (and there is exactly one LatAm and one APAC deep-history
city, mexico-city and sydney, in the 13 **[verified: `08_ia_dump_metrics.csv`, 13 cities]**).

Therefore: **any measure that is differenced against the covered total is invariant to the
survivorship correction.** I ran the strongest version of MOSAIC's claim — relative regional flow
(region minus covered total) against relative disclosed growth (region minus disclosed total), on the
7 quarters 4Q24–2Q26 where regional buckets exist:

| region | corr(level) | corr(Δ) | cov sd (pp) | disclosed sd (pp) |
|---|---|---|---|---|
| NA | 0.691 | 0.176 | 2.15 | 2.14 |
| EMEA | 0.320 | 0.315 | 0.82 | 1.01 |
| LatAm | 0.407 | **0.010** | 8.93 | 2.22 |
| APAC | 0.213 | **−0.067** | 2.70 | 1.51 |

And the raw (undifferenced-from-total) version, which is what (M1) actually uses:
**NA 0.144, EMEA −0.070, LatAm −0.362, APAC 0.222**; in first differences NA 0.37, EMEA −0.19,
**LatAm −0.71**, APAC 0.35 **[all reviewer-computed, n = 7 quarters per region]**.

Pooled across all 32 region-quarters including 2022Q3, the relative measure gives r = 0.725, slope
0.312, **residual sd 6.57pp** against a disclosed sd of 9.4pp **[reviewer-computed]**. A 6.6pp
residual per region-quarter is **two to three times the width of the disclosed bucket itself**
(median band width: NA 3.0pp, EMEA 2.0pp, LatAm 0.0pp, APAC 0.0pp **[reviewer-computed from
`10_regional_panel_quarterly.csv`]**). **(M1) is a strictly less informative observation than (M2).**
Adding it to the filter widens nothing and sharpens nothing; at best it is ignored, at worst the
mis-scaled σ_η forces it to move the posterior in the wrong direction.

The cross-sectional r = 0.725 is real but it is one fact repeated seven times: *LatAm grows fastest*.
The bands already say that.

### 1.3 The concrete double count the proposal says is structurally impossible

The proposal's §2.6 asserts: "(M3) and (M4) are equality constraints, so … no residual exists to
calibrate," and separately that FX "never enters the nights weights … structurally impossible here."

Open `data/processed/overnight/10_regional_panel_quarterly.csv` and read the `*_basis` column
**[reviewer-verified, printed in full]**:

| quarters | NA / EMEA basis | count |
|---|---|---|
| 4Q22–1Q23 | `derived (residual to total)` | 2 |
| 2Q23–3Q24 | `derived (residual to total; NA-EMEA gap from XBRL revenue growth net of regional ADR)` | 6 |
| 4Q24–2Q26 | `bucket` (genuine verbal disclosure) | 7 |
| 3Q22 + LatAm/APAC 3Q22–3Q24 | `numeric` (point values, width 0.0pp) | 9 per region |

**Fourteen of the NA/EMEA "interval observations" were themselves manufactured by imposing
Σ_r n_r = N_total and splitting the NA–EMEA gap with XBRL regional revenue growth deflated by regional
ADR.** Feed those into (M2) as interval likelihoods *while also* imposing (M3) as an exact constraint
and you have counted the same disclosed total twice — and you have imported precisely the
FX-contaminated USD-revenue-divided-by-ADR construction that `02_model_audit.md` §3.2 prices at
+0.09pp of nights growth and calls "the worst possible correlation structure." MOSAIC's central
marketing claim ("FX never touches nights weights: weights are unit counts") is **true of the panel
and false of the likelihood**, because the likelihood eats a pre-cooked XBRL split. This is exactly
the failure mode the proposal says it was designed to prevent, sitting in its own (M2).

**Concrete case where two terms move together and are counted twice:** LatAm FX runs +11.4% y/y
(2Q26, `10_regional_forecast.py:156`). In the derived quarters that inflates LatAm USD revenue →
inflates its implied nights share → the NA/EMEA residual band shifts *down* by construction. MOSAIC
now (a) fits δ_LatAm to a covered panel whose LatAm review flow is genuinely strong, and (b)
simultaneously conditions on a band whose position was set by the same FX move. Two channels, one
shock, both loaded into the posterior for Δln n. Nothing in the reparameterisation detects it,
because the constraint is satisfied exactly — it is satisfied exactly *twice*.

### 1.4 ρ and δ are the same parameter, and the annual anchor does not separate them

The proposal: "ρ and δ are separately identified ONLY because the 10-K annual regional totals bind."
Count the arithmetic. ρ_{m,q} (reviews per stay) and δ_{r,q} (coverage wedge) both enter (M1) as
multiplicative time-varying wedges between covered review flow and regional nights; in logs they are
additively indistinguishable. The anchor is `data/processed/adr/01_regional_annual.csv`
**[verified: 2020–2025, 4 regions, NA 158 / EMEA 215 / LatAm 90 / APAC 70 for 2025 — the proposal's
numbers check]**: **24 annual constraints** against **96 δ states + 96 latent g + a market-level ρ
field**. Under (M3)+(M4) the reparameterisation leaves 3×24 = 72 free regional growths plus 96 δ
against ~124 informative observations, of which 28 are the only genuine intervals. The system is
prior-dominated. The posterior for Δln n is `AR(1) prior × disclosed bands × exact totals`.

That is defensible as a *model*. It is not defensible as a *reason to spend three weeks on 9.2 GB of
scrapes*, because you get the same posterior from the proposal's own Thursday-17-Sep null (bands +
total constraint, no panel). The proposal deserves credit for scheduling that comparison; my
prediction is that it will show posterior widths within a few basis points and the correct decision
will be to stop.

### 1.5 The 10-K anchor is not exact — it is rounded to 1m nights

`01_regional_annual.csv` carries `nights_precision_m = 1.0` for 2022–2025 **[verified]**. NA 158m ±0.5m
is ±0.32% on the level, ≈ **±0.45pp on an annual growth rate**. Imposing (M4) as an equality injects
spurious precision that the quarterly path must then absorb exactly. (M3) is fine (total nights
disclosed to 0.1m, ±0.04%). **Must-fix: (M4) is an interval constraint at the disclosed rounding, not
an equality.**

### 1.6 The hidden plugs

- **`L_{m,q}` (nights per stay) has no estimator anywhere in the proposal.** §2.1 defines the identity
  `ln N = ln A + ln s + ln L`; §2.2 estimates `s`, §2.3 estimates `A`, §2.4 estimates price. `L` is
  mentioned only as "min-nights for LOS floor." 2026 calendars carry **no realised bookings and no
  price** — I confirm the 5-column schema claim. Annual regional ALOS *is* disclosed (3.3–4.1 nights,
  `01_regional_annual.csv` `alos_nights` **[verified]**), so `L` is pinned annually at region grain and
  free at market-quarter grain. Partial credit: this is a smaller plug than I first scored it, but it
  is a plug, and it is the term that absorbs RNPL and long-stay mix — the live 2026–27 story.
- **`A_{m,q}` historically is not independently observed.** One vintage means listing counts exist at
  one date. The proposal's observable (iii), "review-implied active set," is derived from the *same*
  review table as `s`. So two of the three terms in the "identity in logs that cannot double count"
  are measured from one source. The identity is true; it is not informative.
- **Shrinkage target is wrong.** `cc_listing_survival_by_age.csv` has **four age buckets**
  (2–12m 0.921, 1–2y 0.872, 2–3y 0.856, 3y+ 0.838 **[verified]**) — a URL-liveness check implying
  ~13%/yr attrition. The repo's own matched-id retention says **68.0% over 250–400 days = ~32%/yr**
  (`inside_airbnb_like_for_like.csv`, 91 year-ago pairs **[reviewer-computed]**). The two priors
  disagree by 2.5x. Shrinking `f(age)` toward Common Crawl mis-scales the correction in the direction
  that *understates* the bias.

---

## 2. POINT-IN-TIME SAFETY AND BACKTEST VALIDITY — score 3/10

### 2.1 FATAL: the vintage stack that identifies `f(age)` has never existed and cannot be rebuilt in three weeks

The proposal's build plan, Mon 14 Sep: "B: assemble the 13-city × vintage review stack from
`08_ia_dump_metrics.csv` dump dates." That file is **169 rows of two scalars per dump**
(`reviews_ltm`, `reviews_l30d`) **[verified: columns `city, dump_date, listings, reviews_ltm,
reviews_l30d, n_avail, blocked_30, blocked_90, entire_share, partial_scope`]**. It contains no dated
reviews. To estimate `ln R^v_{m,t} = μ_{m,t} + f(v−t) + u` you need review counts **by review month
t** as seen in vintage v — i.e. 168 historical `reviews.csv.gz`.

Those were never downloaded and are not on disk:

- `analysis/src/inside_airbnb_supply_panel.py:51`: `CDN = "https://data.insideairbnb.com/{path}/{date}/data/listings.csv.gz"` — **listings only** **[verified]**.
- `analysis/src/overnight/08_inside_airbnb_demand.py` reads `data/raw/inside_airbnb/*_listings.parquet` **[verified]**.
- `data/raw/` contains `bea, fred, regulatory` — **there is no `inside_airbnb` directory in the repo at all** **[verified: `ls data/raw/`]**.
- A repo-wide search for historical `reviews.csv.gz` outside the 2026 captures returns nothing; the only other Airbnb store, `Theo Data/processed/airbnb_quant_panel_v1.duckdb`, has `review_events` covering **3 markets, 2009–2019** and `listing_snapshots` whose "43 snapshot dates" are all Jun–Jul 2026 scrape days, not vintages **[reviewer-verified via duckdb]**.

To build the stack you must download 168 historical `reviews.csv.gz` (Paris 2026 alone is ~125 MB
compressed — the 120-market reviews total 7.9 GB for one vintage each **[reviewer-computed from the
manifest]**), and the repo's own CDN probe says **22/72 = 31% return 403 and a further 6 error —
39% unavailable, concentrated in 2021–2022** (`Theo Data/raw_expansion/v2_2026-09-05/inside_airbnb_catalog/availability_probe.csv`,
73 rows: 2021 → 6×403/5×200, 2022 → 6×403/5×200, 2025–26 → 21×200 **[reviewer-computed]**). The dead
vintages are exactly the old-`age` cells that identify the long end of `f`.

**This is the single "NEVER CUT" item in the build plan, and it rests on a dataset the team does not
have and can only partially obtain.** Everything downstream of `R̂*` inherits it.

### 2.2 The "both windows" claim materially misstates the repo's own record

The proposal, twice, in the summary and in §4.4: the flow feature `ia_reviews_l30d_matched_yoy →
nights_yoy` "beat naive at **0.813× in BOTH windows**." From `data/processed/overnight/08_ia_tests.csv`
**[reviewer-verified, rows 4 and 22]**:

| window | n | r | perm p | wf_n | ratio vs naive | **ratio vs AR(1)** |
|---|---|---|---|---|---|---|
| 2022Q1.., WF from 2023Q1 | 11 | 0.291 | 0.376 | 7 | 0.813 | 0.828 |
| 2023Q1.., WF from 2024Q1 | 11 | 0.291 | 0.376 | 7 | 0.813 | **1.041** |

The two "windows" share **the same 7 walk-forward points and the same correlation statistics** — they
are not independent evidence, they differ only in the AR(1) benchmark. And in window 2 the feature
**loses to AR(1)**. `08_test_scoreboard.csv` records this directly: `inside_airbnb`, window 2,
`n_beat_naive_and_ar1 = 0` **[verified]**. The repo's own survival rule is beat-naive-**and**-AR(1),
and the proposal's sole surviving empirical foundation fails it. The same feature is **1.27× naive**
against `gbv_yoy` in both windows — a feature that helps on nights and hurts on GBV, on 7 points, with
r = 0.29 and permutation p = 0.38, is noise.

### 2.3 "Zero flags means the feature was broken" is a statistical error, and it is the proposal's central rhetorical plank

`inside_airbnb` scored `n_flagged_r05_perm05 = 0` in both windows, against 18 tests per window
**[verified: `08_test_scoreboard.csv`, `n_tests = 18`, not 36 unique]**. The proposal: "a
real-but-underpowered signal still throws spurious r>0.5 hits; zero flags in 36 tests means the
FEATURE was broken."

Under the null, flags require r > 0.5 **and** permutation p < 0.05. Expected flags ≈ 18 × 0.05 = 0.9
per window if tests were independent; P(0 of 18) = 0.95^18 = **0.397**. The 18 tests are 9 features ×
2 targets on overlapping data, so the effective count is nearer 9 and P(0) ≈ 0.63. **Observing zero
flags is the modal outcome under pure noise.** It is evidence of nothing. The proposal's inference
runs backwards: it treats absence of false positives as proof of a real signal being masked, which is
not a valid test in either direction.

### 2.4 The backtest as designed cannot fail

Three scoring routes are offered. (i) Market grain "where the power is" — those are estimates of DiD,
gravity and repeat-sales parameters, not *out-of-sample forecasts of the quantity being pitched*; a
tight standard error on θ^R says nothing about regional nights in 4Q26. (ii) Band-sharpening at
"n = 46 region-quarters" against a **uniform-on-the-bucket null**. The true count of genuine buckets is
**7 quarters × 4 regions = 28** (§1.3), and an AR(1) prior truncated to the bucket beats uniform-on-
bucket trivially, with or without 9.2 GB of scrapes. The test measures the prior, not the panel.
(iii) Split conformal on the 13-city nowcast — calibrating coverage for a market-level object that is
not the deliverable. **There is no test in the protocol whose failure would stop the project**, except
the 17 Sep null-model width comparison, which is buried in the schedule and not named as a kill-switch.

### 2.5 What *is* PIT-clean

Credit where due, and it is not nothing: ordinance effective dates are public and dated
(`research/regulatory/factors.json`, **32 records verified**, REG-01 NYC 2023-09-05, REG-02 Spain
2025-05-19, REG-17 EU 2026-05-20 **[verified]**); the disclosed bands and 10-K annuals are filings;
the `_pit` scope columns in `inside_airbnb_like_for_like.csv` are the right convention
(`scope_vs_peer_a_pit` present **[verified]**); and the `open_*` return convention is correctly
cited. The proposal is straight about the one-vintage limitation and states the June-2027 constraint
plainly. That honesty is why this gets 3 and not 1.

---

## 3. STATISTICAL POWER AND OVERFITTING — score 3/10

**Free-parameter count, as specified:** `f(age)` age bins ~60 + 13 market deviations ≈ 73;
repeat-sales μ_{m,τ} up to 120 × periods + hedonic β ≈ 10; DiD event study 19 coefficients × 2
outcomes = 38 + market FE 120 + country×month FE ≈ 34 × 130; gravity λ_{ℓ,m} ≈ 1,200 + γ_{m,t} ≈
15,600; state-space 96 g + 96 δ + 4 hyperparameters. Total **> 17,000 estimated quantities** feeding a
forecast whose out-of-sample evaluation set is **7 quarters × 4 regions**.

The proposal pre-empts this with "the estimation happens at market grain where n is 10³–10⁴." That is
true and it is the right instinct (`02_model_audit.md` rec. 8). But it answers the wrong question.
Market-grain power buys you precise estimates of *market-grain parameters*; the quantity that reaches
the pitch is a **4-vector per quarter**, and the aggregation step has n = 7. The proposal's own power
statement (power ≈ 0.35 at n = 15 for true incremental R² = 0.25) is correct and is then used as a
licence to not run the test, rather than as a reason to choose a different deliverable.

**Detectable effect size.** For MOSAIC to change the Q4-26 nights bucket it must shift the posterior
mean of a region's growth by ≳1pp with enough confidence to move probability mass across a bucket
boundary 2–3pp wide. My §1.1 measurement puts the covered panel's residual sd at **6.57pp per
region-quarter after the best-case attenuation fit**. The signal-to-noise required is roughly 6x
better than what the data delivers.

**Does it repeat a failed design?** Partly. It correctly avoids Trends, macro, tone, peer read-across
and NNLS composites, and it correctly reframes Eurostat as a smoothing measurement rather than a lead
predictor. But it repeats the Inside Airbnb design's *actual* failure — which was not the trailing-12m
statistic, it was that 13 dense tourist markets are not a sample of a 220-country platform. The
120-market store covers **1.61m listings and 15.77m LTM reviews** (`market_summary_2026.csv`
**[reviewer-computed]**), ≈ **22% of implied global stays at a 50% review rate**, and the composition
is worse than the count: Italy alone is 12.4% of covered reviews against ~4% of nights; the US is
18.7% of covered reviews against NA ≈ 30% of nights; APAC has essentially only Japan (463k) plus one
Hong Kong market. **The two regions whose growth drives the entire geo-mix ADR drag — LatAm and APAC —
are the thinnest and, in my test, the two with zero or negative time-series correlation.** Going from
13 to 120 markets changes the coverage problem's magnitude, not its kind.

**Uncertainty representation.** The three-layer construction (posterior → posterior-probability
scenario tree → split conformal) is genuinely better than a Monte Carlo of judgemental inputs and is
the right answer to the brief's "no plain Monte Carlo" rule. But an honest posterior built on
σ_η = 0.02 when the measurement error is 6.6pp is not honest; it is a precisely-quantified wrong
number. Conformal coverage on the market-level nowcast does not transfer to the regional aggregate.

---

## 4. TRADEABILITY OVER 3–12 MONTHS — score 4/10

### 4.1 The target is right; the deliverable is not

Choosing the **level of the growth vector** over surprise-vs-Street is correct and follows
`02_model_audit.md` §4.2b and rec. 7. Naming the Q4-26 nights guide as the sign-setting variable is
correct. But the deliverable — `P(nights bucket)` — collides with the disclosure record.

From `data/processed/overnight/02_guidance_ledger.csv`, metric `nights_yoy_pct`, **17 statements
[verified]**: **14 are `directional`** ("moderate relative to Q3", "relatively stable"), and only
**3 are `bucket`** (3Q25→4Q25 "mid-single-digit" 4–6%; 4Q25→1Q26 "high-single-digit" 7–9%;
2Q26→3Q26 "low double-digit" 10–12%). So:

1. The mapping from latent nights growth to a guided bucket has a training sample of **three**.
2. Of those three, **two printed above the top of the range** (4Q25 guided 4–6%, actual 9.82%;
   1Q26 guided 7–9%, actual 9.15%) **[verified, `outcome = above_range`]**. Management's nights
   conservatism is on the order of **4pp** — larger than the entire signal MOSAIC is trying to
   extract, and larger than a bucket.
3. Airbnb may not give a nights bucket at all on 5 Nov; 14 of 17 precedents are directional.

**Even a perfect forecast of true 4Q26 nights growth does not pin the guided bucket**, because the
guidance policy function's conservatism dominates. That function is M3's deliverable, estimated on
19 guided quarters with a trailing-8 median cushion of +1.79%. MOSAIC's marginal contribution to the
tradeable output is the *residual* after M3's cushion — i.e. small.

### 4.2 The one genuinely tradeable idea does not need MOSAIC

The fee-migration listed-price artefact is the best thing in this document. It is dated (15 Sep
ex-EEA, 13 Oct EEA+CH, both inside 3Q26/4Q26), mechanical (payout-neutral reprice lifts *listed*
nightly price ~+14.8% with ~zero effect on the all-in guest price, hence ~zero on GBV/ADR),
falsifiable, and **measurable in one file**: I confirm the 2026 schema carries both bases —
`price` (47), `price_quote_checkin_date` (48), `price_quote_checkout_date` (49),
`price_quote_total_price` (50), `price_quote_price_per_night` (51), `price_quote_raw` (52), 90 columns
total **[reviewer-verified on `Theo Data/raw/inside_airbnb/france/ile-de-france/paris/2026-06-16/listings.csv.gz`]**.
`2026-09-07_adr-decomposition.md` §7 flags it as unmodelled. That exhibit needs a before/after capture
and a two-column median. It needs no state-space, no gravity model and no survivorship curve.

The bedroom-elasticity point (0.23 measured vs the Street's implicit ~1:1 read of the +12% vs +10%
Bedroom-Nights wedge → +0.46pp not +2pp) is also a real, memo-sized edge already owned by
`adr/13_party_size_adr.py` — MOSAIC re-estimates it but does not create it.

### 4.3 The PM question it does not answer

"You are telling me your model lands FY27 at $15.5–15.7bn against Street $15.73–15.76bn — that is
*inside* the Street range. Where is the trade?" The proposal answers "the guide path and the Q4 nights
bucket," but §4.1 shows it cannot resolve the bucket to better than management's own 4pp
conservatism. The executable rule the repo actually owns — guide-below-Street → 20-day drift 9/9
negative, −4.21% on next-open entry — is triggered by the **revenue** guide, and the revenue guide's
dominant 4Q26 driver is the FX step-down that is already ~84% determined (`29_q4-fy27-bridge.md`).
**That trade is available without MOSAIC and is being fought for by M6.**

---

## 5. BUILDABILITY IN THREE WEEKS — score 3/10

### 5.1 What is genuinely on disk (I checked)

| Claim | Verdict |
|---|---|
| `raw_expansion/v2_2026-09-05/inside_airbnb_current/`, 9.2 GB, 315 files, 120 markets | **TRUE** — `du` 9.2G; manifest 315 rows, 120 markets, 35 countries (proposal says 34), all `verified = yes` |
| dumps 14 Jun – 10 Aug 2026 | **TRUE** |
| `calendar.csv.gz` 5 columns, no price | **TRUE** (proposal's own verification; consistent with `booking_curves_by_market.csv` carrying `blocked_rate`, not occupancy) |
| dual price basis at cols 47/48/50/51 | **TRUE**, 90-column schema |
| `08_ia_dump_metrics.csv` 168 dumps, 13 cities, rome 21 / paris 17 / austin 15 / nashville 15 | **TRUE** (169 lines incl. header) |
| `10_regional_panel_quarterly.csv` 23 quarters with lo/hi bands | **PARTIALLY** — 23 quarters, but only **7 carry genuine verbal buckets**; 14 NA/EMEA cells are derived-from-total; 18 LatAm/APAC cells are zero-width points |
| `research/regulatory/factors.json` 32 dated factors | **TRUE** |
| `abnb_party_size_reviews_v2_market_month_shard{0..5}` 22,455 market-month rows | **TRUE** — and this is the best news in the proposal: **the flow panel already exists**, so build-plan day A/Mon-14 is already done |
| `06_quote_line_items.csv` "1.71M fee-inclusive quotes" | **MISLEADING** — the file is **76 rows** of city × dump aggregates whose `quotes` column sums to 1,707,390. There is **no quote-grain table** to splice listing-level price bases against |
| `market_summary_2026.csv` 120 markets | **TRUE**; note `listings` sums to 1.609m, not the 982k quoted elsewhere in the brief |

### 5.2 The 45-market listings hole the plan would walk into

The manifest has **120 `calendar.csv.gz`, 120 `reviews.csv.gz`, and only 75 `listings.csv.gz`**
**[reviewer-computed]**. The missing 45 are alphabetically contiguous by country — argentina through
ireland — i.e. **all of Australia (11 markets), Canada (8), France (4, including Paris), Greece (4),
Belgium (3), Germany (2, incl. Berlin), Brazil (2), plus Vienna, Prague, Budapest, Dublin, Copenhagen,
Hong Kong, Santiago, Bogotá, Buenos Aires, Toronto, Montreal, Vancouver, Melbourne, Sydney**. The
build plan's first deliverable is "a DuckDB catalogue over `raw_expansion/…/inside_airbnb_current/**`"
— which would silently produce a hedonic, a supply panel, a licence-based DiD and a fee-basis exhibit
covering **75 markets with no France, Germany, Australia, Canada or Brazil**.

Those 45 listings files **do exist**, in a different folder: `Theo Data/raw/inside_airbnb/<country>/…/listings.csv.gz`,
45 files, 336 MB, same 90-column schema **[reviewer-verified]**. **Must-fix, one line: catalogue both
roots.** Not fatal, but it is a data-map error in a document whose opening sentence is "Every repo
path below was opened before it was cited."

### 5.3 The repeat-listing index is not deliverable by 24 Sep, and probably not at all at annual horizon

`inside_airbnb_like_for_like.csv`, 258 pairs, 13 cities **[verified]**. Broken out by gap
**[reviewer-computed]**:

| gap (days) | n pairs | retention | `price_comparable` share |
|---|---|---|---|
| ≤120 (sequential) | 155 | 0.897 | **0.632** |
| 250–400 (year-ago) | 91 | 0.680 | **0.165** |
| 400–800 | 12 | 0.584 | **0.000** |

Overall `price_comparable` = 43.8%. **At the year-ago horizon — the horizon at which the +3.6pp
residual is defined — only 16.5% of pairs are price-comparable, and beyond 400 days, none.** The
Case–Shiller index can only be built by chaining sequential links at ~90% retention and 63%
comparability each, three links per year, across a documented basis change, on **ask** prices in
**local currency**. That is not "the first identified split of the +3.6pp residual"; it is a chained
selection-biased sequential ask index that then has to be reconciled to disclosed levels anyway. Milestone
M3 (Thu 24 Sep) will not produce what it promises.

### 5.4 The DiD has a treatment-correlated survivorship confound and a national-treatment problem

I read all 32 factors **[reviewer-verified, printed]**. Two structural issues:

1. **National treatments cannot be identified with country × month FE**, which is MOSAIC's stated
   specification. REG-02/03 (Spain national), REG-07 (Portugal national), REG-17/25 (EU),
   REG-19/27 (UK), REG-20 (Greece national), REG-24 (Ireland) are absorbed entirely. The usable
   sub-national staggered set is roughly NYC, Paris, Amsterdam, Athens, Thessaloniki, Lisbon, Madrid,
   Malaga, Florence, Budapest-VI, Canary Islands, Balearics, Montreal, BC — of which several
   (Barcelona 2028, Maui 2029, Ireland Dec 2026) have **no post-period inside the sample**.
2. **The outcome is survivorship-truncated by the treatment itself.** `ln R̂*_{m,t}` for a treated
   market is read from a 2026 vintage from which every delisted listing — i.e. exactly the listings
   the ordinance removed — has been erased **along with its entire pre-treatment review history**. So
   the pre-period is depressed in treated markets in proportion to the treatment's bite, biasing θ^R
   toward zero or positive. `f(age)` cannot fix this: it is a function of age only, and the confound
   is market × treatment. This is not an anticipation or spillover problem (both of which the
   proposal handles competently); it is a mechanical inversion of the estimand. **A DiD on
   `ln A_{m,t}` has the same problem and worse — with one vintage there is no time variation in A at
   all.**

The usable version is a DiD on markets where a *second* capture gives a genuine post-period, which is
a 2027 deliverable, not an October one.

### 5.5 Skills and compute

DuckDB over 9.2 GB is fine on a laptop. `pyfixest` HDFE with ~16,800 gravity fixed effects is fine.
PyMC NUTS on 192 latent states with a censored likelihood and an exact reparameterisation is **not**
a three-undergraduate-days task; interval-censored + nonlinear equality reparameterisation is where
divergences live, and the plan allows one day (Thu 17 Sep) for v1 and one (Fri 25 Sep) for the full
model. The Callaway–Sant'Anna stack in Python is immature; the plan's R fallback means a second
language in week 2.

### 5.6 Minimum viable version that still carries an edge

1. **Fee-basis exhibit** (2 days, 1 person): median `price` vs `price_quote_price_per_night` by
   country cohort, before/after 15 Sep, on the second capture. Delivers the differentiated call.
2. **Start the daily capture on 13–14 Sep** — I agree completely that this is the one irreversible
   action, and it is cheap. Do it even if everything else is cut. Catalogue **both** roots (§5.2).
3. **Survivorship-corrected flow using the existing retention curve**, not a review-age spline:
   `f` from the 91 year-ago matched pairs (retention 0.680) plus the 155 sequential pairs. Buildable
   today, no downloads.
4. **Hand the reconciliation layer to M1** and run only the null (bands + exact total + 10-K interval).

That MVP is ~4 person-days and keeps the only edge that survives cross-examination.

---

## 6. DEFENSIBILITY IN A 2-PAGE MEMO AND HOSTILE Q&A — score 5/10

**One-sentence version (theirs, compressed):** "A 120-market Airbnb scrape, corrected for the listings
that have since vanished, tells us which way regional nights are running inside the ranges management
gives in words — and separately shows that the September fee migration will make listed prices jump
~15% with no effect on ADR, so the Street is about to misread Q4."

**The number a judge attacks first.** Not FY27 and not the $15.5–15.7bn. It is this: *"Show me the
correlation between your panel and the four regional nights growth rates Airbnb actually disclosed."*
The answer, on the seven quarters that have regional buckets, is **NA 0.14, EMEA −0.07, LatAm −0.36,
APAC 0.22** [§1.1]. **The proposal does not compute this number and does not give the answer.** It is a
twenty-minute calculation on a file already in the repo. A proposal that spends 422 lines on estimator
design without running the one scatter plot that validates its central measurement equation will not
survive ten minutes with a Citadel PM.

**Second attack:** "Your survivorship correction is a function of scrape-date-minus-review-date. Every
market has one scrape date. So your correction is a function of calendar time. How is that different
from your δ?" The proposal has no answer; §1.2 shows there isn't one.

**Third attack:** "You said your team's Inside Airbnb tests returned zero hits and that proves the
feature was broken. Walk me through the null distribution." §2.3.

**What *does* survive Q&A**, and should go in the memo regardless of the verdict:
the fee-basis artefact with the dual-column evidence; the bedroom-elasticity 0.23 vs the Street's 1:1;
geo mix as an identity rather than a row (so every bullish nights case pays its own ADR tax); the
interval-censored treatment of the verbal buckets; and the honest "no 120-market y/y exists before
June 2027" statement, which is the kind of line that buys credibility for everything around it.

The writing is disciplined, separates measured from assumed, cites lines, and pre-empts eight hostile
questions. That craft is worth 2 of the 5 points.

---

## 7. FATAL FLAWS

1. **The vintage review stack that identifies `f(age)` does not exist and is 39% unrecoverable.**
   Historical Inside Airbnb downloads were `listings.csv.gz` only (`inside_airbnb_supply_panel.py:51`);
   `data/raw/inside_airbnb/` is absent from the repo; the CDN probe shows 28/73 dead, concentrated in
   2021–22. The one item the plan says can never be cut is the one it cannot build.
2. **The covered panel carries no measurable within-region time-series information about regional
   nights growth.** Raw correlations over the 7 disclosed quarters: NA 0.14, EMEA −0.07, LatAm −0.36,
   APAC 0.22; relative-to-total residual sd 6.57pp against bucket widths of 0–3pp. And because a
   shrunk `f(age)` is common across markets, it cancels in the relative measure — so the survivorship
   defence cannot rescue this.
3. **(M2) double counts (M3) and re-imports the FX contamination the design claims is structurally
   impossible.** Fourteen NA/EMEA "interval observations" are `derived (residual to total; NA-EMEA gap
   from XBRL revenue growth net of regional ADR)`.
4. **ρ and δ are the same parameter in logs; 24 rounded annual constraints do not separate them from
   96 quarterly states.** The aggregate posterior is the AR(1) prior plus the disclosures — which is
   the proposal's own stated null model.

## 8. MUST-FIX

1. Run the §1.1 validation **before** anything else: covered flow vs the four disclosed regional
   growths, 4Q24–2Q26, levels and differences. If it looks like my table, stop the nights block.
2. Make the 17 Sep null-model comparison an explicit **kill-switch with a numeric threshold**
   (e.g. "MOSAIC must cut the mean 80% posterior width by ≥25% vs bands+total, or the panel is cut").
3. Reclassify (M2): only the **7 bucket quarters** are interval observations. Drop the 14
   `derived (residual to total)` cells entirely — they are a restatement of (M3). Treat the 18
   zero-width LatAm/APAC `numeric` cells as ±rounding intervals, not point equalities.
4. Make (M4) an interval at the 10-K's own precision (`nights_precision_m = 1.0` ⇒ ±0.5m ⇒ ±0.45pp of
   annual growth), not an equality.
5. Re-elicit σ_η and σ_δ from the measured wedge (14–36pp, region-specific) rather than 2pp/1pp.
   Better: give δ a region-specific **drift** term, not a driftless RW.
6. Estimate the survivorship correction from the **matched-id retention curve already on disk**
   (`inside_airbnb_like_for_like.csv`: 0.897 at ≤120d, 0.680 at 250–400d, 0.584 at 400–800d), not
   from a review-age spline that needs 168 downloads; shrink toward that, not toward Common Crawl
   (0.872 at 1–2y), which disagrees by 2.5x.
7. Catalogue **both** stores. 45 of 120 markets have no `listings.csv.gz` under `raw_expansion/`;
   they are in `Theo Data/raw/inside_airbnb/`. Without this the hedonic and the fee exhibit lose
   France, Germany, Australia, Canada and Brazil.
8. Drop the DiD on `ln R̂*` as a causal estimand, or restrict it to post-second-capture windows:
   the treatment removes listings and therefore removes their pre-treatment reviews from the vintage,
   inverting the estimand. Keep `11_regulatory_overlay.csv` as a stated prior band.
9. Correct the record in §4.4: the flow feature loses to AR(1) in window 2 and the two windows share
   the same 7 points. Delete the "zero flags proves the feature was broken" argument — it is
   statistically invalid (P(0 of 18 under the null) ≈ 0.40).
10. Re-target the deliverable. `P(nights bucket)` has three bucket precedents, two of which printed
    above the range; hand the bucket mapping to M3 and deliver a **posterior over nights growth** plus
    the fee-artefact exhibit instead.
11. Give `L_{m,q}` an estimator or declare it a plug. Annual regional ALOS is disclosed
    (`adr/01_regional_annual.csv`); market-quarter LOS is not.
12. State plainly that `06_quote_line_items.csv` is 76 aggregate rows, not a 1.71M-row quote table,
    and re-plan the price-basis splice accordingly.

## 9. WHAT TO KEEP EVEN IF THE WHOLE IS REJECTED

1. **The daily Inside Airbnb capture, started 13–14 Sep.** Irreversible, near-zero cost, and it is the
   only way the fee-migration exhibit exists. Do this today.
2. **The fee-migration dual-basis exhibit.** `price` (47) vs `price_quote_price_per_night` (51) on
   migrating-country cohorts across 15 Sep and 13 Oct. Dated, mechanical, falsifiable, unowned by the
   Street, and independent of every other block.
3. **Interval-censored likelihood for the verbal buckets + exact total-nights constraint by
   reparameterisation.** This is `02_model_audit.md` rec. 2 done properly and it kills the +0.19pp
   index-number bias and the 0.41pp CALIB gap. Give it to M1.
4. **Geographic mix as an output** (`ADR_blended = Σ_r ω_r ADR_r` with ω from the nights build).
   Closes the 1.13pp / ~$175M loop; cheap; correct.
5. **One joint hedonic for all listing-derived ADR terms, shift-shared on fitted coefficients.**
   The only construction under which unit size, party size and LOS composition cannot double count.
6. **The refusal to re-fight surprise-vs-Street**, and the AR(1)-as-prior discipline.
7. **The "what is estimable at each date" table** and the "no 120-market y/y before June 2027"
   statement — this is the standard the rest of the tree should meet.
8. **The bedroom-elasticity correction** (0.23 ⇒ +0.46pp, not the Street's ~+2pp).
9. **The honest statement that the team's own evidence puts FY27 at or below Street**, and that the
   pitch must rest on the guide path rather than a higher revenue number.
10. **Eurostat reframed as a smoothing measurement rather than a lead predictor** — correct use of a
    150-day-lagged series.

---

## 10. Refutation attempts

| # | Claim | Attack | Outcome |
|---|---|---|---|
| 1 | "The survivorship-corrected covered panel is a ±2pp measurement of latent regional nights growth (M1)." | Built the panel from the 22,455-row market-month shards, aggregated to regions, compared to disclosed regional growth. Wedge is +14 to +36pp, region-specific, non-monotone. Within-region correlations over the 7 disclosed quarters: NA 0.14, EMEA −0.07, LatAm −0.36, APAC 0.22; in differences LatAm −0.71. Relative-to-total residual sd 6.57pp vs bucket widths 0–3pp. | **refuted** |
| 2 | "Survivorship `f(age)` is identified off within-cell across-vintage variation on the 13-city stack." | The 13-city historical downloads were `listings.csv.gz` only (`inside_airbnb_supply_panel.py:51`); `data/raw/inside_airbnb/` does not exist in the repo; the only other store has review events for 3 markets, 2009–2019. Rebuilding needs 168 `reviews.csv.gz` of which 39% return 403/ERR, concentrated in the old vintages that identify long ages. | **refuted** |
| 3 | "Survivorship correction fixes the single-vintage y/y bias." | With one vintage per market, `age = v−t` is affine in calendar time, so a pooled/shrunk `f` is a common time profile and **cancels identically** in any region-minus-total measure. The relative series — post-correction by construction — still gives corr(Δ) of 0.18 / 0.32 / 0.01 / −0.07. | **refuted** |
| 4 | "Exact + interval constraints make double counting structurally impossible; FX never touches the nights weights." | 14 of the NA/EMEA band cells carry basis `derived (residual to total; NA-EMEA gap from XBRL revenue growth net of regional ADR)`. Using them as (M2) alongside exact (M3) counts the disclosed total twice and re-imports the FX-contaminated XBRL split that `02_model_audit.md` §3.2 condemns. | **refuted** |
| 5 | "Zero flags in the IA family proves the feature was broken, not weak." | 18 tests per window, flag = r>0.5 **and** perm p<0.05. P(0 of 18 | null) = 0.95^18 ≈ 0.40, ≈0.63 at the effective count of ~9 independent tests. Zero flags is the modal null outcome. | **refuted** |
| 6 | "The flow feature `ia_reviews_l30d_matched_yoy` beat naive at 0.813× in both windows." | Literally true for naive; the two windows share the same 7 walk-forward points and the same r = 0.291 (perm p 0.376), and the feature **loses to AR(1) in window 2** (1.041) — `08_test_scoreboard.csv` records `n_beat_naive_and_ar1 = 0`. Same feature is 1.27× naive on GBV. | **partially** (claim is technically accurate, materially misleading) |
| 7 | "MOSAIC emits P(nights bucket) for the Q4-26 guide — the sign-setting variable." | The guidance ledger has 17 nights statements: 14 directional, 3 bucket; 2 of the 3 buckets printed **above** the range (4Q25 guided 4–6% → 9.82%; 1Q26 guided 7–9% → 9.15%). Management conservatism ≈ 4pp, wider than a bucket. The mapping is M3's job and it dominates. | **refuted** |
| 8 | "`ln N = ln A + ln s + ln L` makes double counting mechanically impossible." | The identity is true but two of three terms (`A` via review-implied active set, `s` via `R*/ρ`) come from the same review table, and `L` has no estimator at market-quarter grain — annual regional ALOS is disclosed (`adr/01_regional_annual.csv`), market-quarter LOS is not. An identity with a free term is not a constraint. | **partially** |
| 9 | "Repeat-listing Case–Shiller index splits the +3.6pp residual by 24 Sep." | Only 16.5% of the 91 year-ago pairs are `price_comparable`; 0% beyond 400 days; 43.8% overall. The annual like-for-like index must be chained from sequential links at 90% retention and 63% comparability across a documented basis change, on ask prices. | **refuted** for the annual horizon |
| 10 | "DiD on 32 dated ordinances identifies regulation off within-country cross-market timing." | ~10 of 32 factors are national and absorbed by country×month FE; several have no in-sample post-period (Barcelona 2028, Maui 2029, Ireland Dec 2026). More seriously, delisted listings are erased from the 2026 vintage **with their pre-treatment reviews**, so the treatment depresses its own pre-period and biases θ^R toward zero/positive — a confound `f(age)` cannot address. | **refuted** |
| 11 | "9.2 GB, 315 files, 120 markets — every path opened before it was cited." | True for the store, but only **75 of 120** markets have `listings.csv.gz` under `raw_expansion/`; the other 45 (all of France, Germany, Australia, Canada, Brazil, Greece, plus Vienna/Prague/Budapest/Dublin/HK/Toronto/Sydney) sit in `Theo Data/raw/inside_airbnb/`. Also `06_quote_line_items.csv` is 76 aggregate rows, not a 1.71M-row quote table. | **partially** (data present, inventory wrong) |
| 12 | "(M3)/(M4) are exact constraints so no residual exists to calibrate." | (M3) is fine (total nights to 0.1m). (M4) is not: `nights_precision_m = 1.0` for 2022–25, so NA 158m is ±0.5m ≈ ±0.45pp of annual growth. Imposed as equality it injects false precision that the quarterly path must absorb. | **refuted** as stated; fixable as an interval |
| 13 | "120 markets is 9× the coverage — the failure was coverage, not concept." | Covered panel is ~22% of implied global stays with severe skew: Italy 12.4% of covered reviews vs ~4% of nights; US 18.7% vs NA ~30%; APAC is essentially Japan. LatAm and APAC — the regions that drive the geo-mix drag — are thinnest and show zero/negative time-series correlation. Magnitude changed, kind did not. | **refuted** |
| 14 | "The fee-migration listed-price artefact is a dated, measurable, unowned edge." | Verified the dual basis exists (cols 47/48/50/51, 90-col schema) on a real file; `adr-decomposition.md` §7 flags it unmodelled; the deadlines fall inside 3Q26/4Q26. I could not break this. | **survived** |
| 15 | "Interval-censored bands + exact total is the right treatment of the disclosure." | Correct, and it is `02_model_audit.md` rec. 2. My only attack is ownership (it belongs to M1) and constraint hygiene (§1.3, §1.5), not validity. | **survived** |

---

## 11. Interlock

MOSAIC should not be a lens; it should be **two deliverables and a data feed**. Give the
interval-censored reconciliation layer to **M1**, which already owns the structural mix state-space —
MOSAIC's (M2)/(M3)/(M4) plus the geo-mix identity `ADR_blended = Σ_r ω_r ADR_r` are M1's
specification, and running them twice in two lenses is itself a double count. Give the fee-migration
dual-basis exhibit and the bedroom-elasticity correction to the **ADR workstream**, where they
adjudicate the +3.6pp residual's near-term path without pretending to identify it; the exhibit lands
on the 4Q26 ADR line that **M6** translates. Give the daily capture and the survivorship-corrected
market-month flow to **M2** as a *tracker*, explicitly labelled a coincident monitoring series with no
backtested forecasting claim — which is the only role my §1.1 numbers support. Give the nights-bucket
mapping entirely to **M3**: the guidance ledger shows 14 of 17 nights statements are directional and
management's conservatism is ~4pp, so the bucket is a property of the policy function, not of the
underlying growth rate. What is left of MOSAIC proper — the 120-market bottom-up measurement of
regional nights — should be run once, on 17 Sep, against the bands-plus-total null, with a
pre-registered width threshold, and cut if it does not clear it. That single gated experiment costs
two days, is itself a defensible exhibit ("we tested our own alt-data panel against the disclosure-only
model and it added nothing"), and it protects the team from spending week two on an estimator whose
central measurement equation is, on the repo's own data, uncorrelated with the thing it measures.
