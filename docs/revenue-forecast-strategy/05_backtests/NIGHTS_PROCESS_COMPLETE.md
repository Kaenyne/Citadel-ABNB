# The nights engine — complete process record, and the statistical review register

Version 2.1, state of 22 September 2026. This is the single granular document: every step from raw file to final number,
every parameter with its source, every result with its uncertainty, and — in Part 6 — the explicit register of what a
statistician must review, ranked, with what would settle each item.

Companion files: `REVIEWS_INDEX_v2.md` (spec + frozen pre-registration + results), `REVIEWS_INDEX_v2_RATIONALE.md` (why each
number stands), `NIGHTS_ENGINE.md` (how to run it), `NIGHTS_ENGINE_EXPLAINED.md` (three audiences),
`NIGHTS_ENGINE_REVIEW_RESPONSE.md` (external review, A–I). Engine: `analysis/src/forecast_methods/reviews_index_v2/`.
Outputs: `data/processed/forecast_methods/reviews_index_v2/`. Workbook: `model/ABNB_official_model.xlsx`.

**Reproduce everything:** `cd analysis/src/forecast_methods/reviews_index_v2 && python3 -m pytest tests -q && python3 run.py --stage all && python3 workbook.py` (≈20 s).

---

## Part 0 — What the engine is, in one page

| | |
|---|---|
| **Object measured** | year-over-year growth of completed stays in 123 Inside Airbnb city markets |
| **Object forecast** | Airbnb's reported *Nights and Seats Booked* growth (booking-dated, net of in-period cancellations) |
| **Raw material** | 75.1 M reviews in the latest vintage (49.1 M since 2023); 697,888 market × dump × day count rows |
| **Validation target** | Eurostat `tour_ce_omr` observed platform guest-nights, 18 EU countries × 39 months = 702 country-months |
| **Headline scores** | walk-forward RMSE ratio vs naive **0.723 / 0.723** (W1 n 14, W2 n 10); panel β **0.494** (0.313 with month FE), wild-cluster p 0.001 |
| **Current read** | 3Q26 stays **+8.92% ± 1.85 → 145.5m [143.0, 148.0]**, produced 18 Sep 2026 on data through ~17 Aug 2026 |
| **Status of that read** | the only genuinely point-in-time observation; scored 5 Nov 2026 |
| **What it is not** | not a calibrated realised-stay estimator, not a real-time backtest, not a causal estimate of RNPL |

---

## Part 1 — Inputs, with provenance and availability

### 1.1 Review counts (the alt-data)

| item | value |
|---|---|
| source | Inside Airbnb published dumps (third-party, CC-licensed, public); **downloaded, not scraped by us** |
| download record | `data/processed/q3nowcast/E/download_manifest.csv` — 240 files, URL + sha256 + UTC timestamp (11 Sep 2026) |
| file inventory | `q3nowcast/E/inventory.csv` — 832 entries, 123 markets |
| vintages held | 2025-08, 2025-09, 2026-06, 2026-07, 2026-08 (+ 2023-03..05 for 114 markets in `q3nowcast_v2/E`) |
| publication lag | dump date → CDN last-modified **median 18 days** (`cdn_probe_reviews.csv`, n 641 probes with HTTP 200) |
| counted layer | `q3nowcast/E/market_vintage_{daily,monthly}.csv` — produced by E1–E3 (**not re-run** on this machine; a counting error inside E3 would survive) |
| grain | market × dump_date × review_date × n_reviews; monthly adds `n_reviews_mature12/24`, `n_listings`, `n_new_listing_cohort` |
| what a review is | one row per review; a review is written after check-out → **one completed reservation**, not one night, not one guest |

### 1.2 Targets and weights

| input | file | availability at a 2023–25 forecast cutoff |
|---|---|---|
| printed nights (levels 1Q21–2Q26) | `abnb_driver_history_quarterly.csv` | yes (prior quarters only, enforced by the expanding window) |
| Eurostat platform nights | `eurostat_platform_nights_monthly.csv` (`tour_ce_omr`, 31 countries, 2018-01→2026-03) | validation only, not in the forecast path |
| regional revenue by quarter | `overnight/10_regional_panel_quarterly.csv` (10-Q) | **no — same-quarter revenue publishes ~5 weeks after the cutoff (look-ahead in the backtest)** |
| regional ADR index 1.42 / 0.97 / 0.68 / 0.59 | `research/notes/overnight/10_regional-and-segment-decomposition.md` | no — a Sep 2026 calibration |
| share-drift rule −0.55 / +0.10 / +0.33 / +0.10 pp/qtr | same note | no |
| K2 lead-time kernel | `kernel_leadtime_v2/K2_M_matrix.csv` | no — full-history estimate (used only outside the primary read) |
| unearned fees, GBV | `overnight/02_kpi_panel_quarterly.csv` (10-Q) | evidence layer only |
| Street nights 149.0 / 134.0 | Bloomberg MODL 12 Sep 2026 (DEC-0005); `final_nights.md` §4.6 | comparison only |
| nights guidance buckets | `overnight/02_guidance_ledger.csv` | comparison only |

### 1.3 RNPL disclosures used (verified quotes)

| id | date | source class | content |
|---|---|---|---|
| — | 2026-08-06 | **10-Q, official** | "RNPL bookings, which require no payment at the time of booking, have experienced **higher cancellation rates** than historic bookings…" |
| — | 2026-08-06 | **10-Q, official** | KPI = "…net of cancellations and alterations **that occurred in that period**"; GBV "reflected in the quarter it occurs regardless of when payment is collected" |
| D018 | 2026-02-12 | call, **mirror transcript** | "an average of maybe **16% cancellation rate historically going to 17%** … not hugely material relative to the broader cancellations" |
| D033 | 2026-05-07 | call, mirror | "expanded RNPL to more markets… driving **longer booking lead times** … meaningful lift to all booking metrics, **net of cancellation**" |
| D025 | 2026-02-17 | Newsroom, official | RNPL "**now available to guests globally** for domestic and international trips" |
| D044 | 2026-08-06 | call, mirror | "in July, we **expanded the types of bookings eligible**" |
| D042 | 2026-05-07 | letter, official | "~1 growth point" = **Middle East conflict**, *not* RNPL (earlier drafts misattributed this) |

---

## Part 2 — Construction, step by step

### 2.1 Vintage selection — `data.select_vintages`
Per market: latest dump L; prior dump P with **300 ≤ age(L) − age(P) ≤ 430 days** (E4's rule). Both trimmed: months
`ymi ≤ dump_ymi − 2` (posting lag + truncation). Result: 119 of 123 markets have a usable pair; 16,963 market-months.

### 2.2 Same-age counts — `index.market_monthly`
`n_vm_cur(m,t)` = reviews for month t in L; `n_vm_prior(m,t)` = reviews for t−12 in P. Both read the same distance from
their own dump, so attrition of delisted listings is common to both sides.
*Worked example (Paris, June):* 65,997 (Aug-26 file) ÷ 74,784 (Aug-25 file) − 1 = **−11.7%**. Within one file:
65,997 ÷ 59,070 − 1 = **+11.7%** — 5,680 of 26,826 June-2025 listings (21%) had vanished from the later file.
*Assumption that remains:* the attrition **hazard** is stationary across vintages. Two vintages cannot test it.
Also built and kept as sensitivities: `yoy_all` (one file both sides), `yoy_mature` (listings ≥ 12 months on both sides).

### 2.3 Regional growth — `index.global_quarterly`
Ratio of sums within region and quarter, markets requiring all three months:
`g_r,q = Σ n_vm_cur / Σ n_vm_prior − 1`.
*2Q26:* NAM 1,062,749/994,190 = **+6.90**; EMEA 2,640,604/2,602,033 = **+1.48**; LatAm 418,408/347,527 = **+20.40**;
APAC 500,145/488,886 = **+2.30** (%).

### 2.4 Stay-quarter mix weights — `mix.seasonal_weights` (v2.1)
`w_r,q = (Rev_r,q / A_r) / Σ_r(Rev_r,q / A_r)`; Rev = disclosed regional revenue (check-in basis → a stay mix), A = the ADR index.
Forward quarters: same quarter of the prior year + the drift rule, renormalised.
Seasonality is large: EMEA ≈ **51.5%** of stays in a Q3 and **27–28%** in a Q1; LatAm ≈ 10% in Q3, 24–26% in Q1.

### 2.5 The index
`x_q = Σ_r w_r,q · g_r,q`.
*2Q26:* 0.318×6.90 + 0.417×1.48 + 0.121×20.40 + 0.143×2.30 = **5.62%**.
Full series (v2.1, %): 1Q23 32.7 · 2Q23 16.9 · 3Q23 11.5 · 4Q23 14.5 · 1Q24 12.2 · 2Q24 6.0 · 3Q24 5.8 · 4Q24 7.0 ·
1Q25 6.0 · 2Q25 5.5 · 3Q25 3.2 · 4Q25 7.6 · 1Q26 9.0 · 2Q26 5.6.

### 2.6 Mapping — `stages.frozen_mapping`
`y_q = a + b·x_q`, OLS on **1Q23–2Q25 (n 10)**, frozen: **a = 6.825, b = 0.350**.
Interpretation of each parameter, and its risk: *b* = pp of Airbnb nights growth per index point (sample→platform
elasticity; the Eurostat panel's 0.49/0.31 is the review→nights elasticity at country level and is **not transferable** —
tested: imported as b it scores 4.47× naive); *a* = growth when the sampled cities are flat — expansion markets we do not
sample. **The intercept supplies 6.83 of the 8.92 read (77%).**
Leave-one-quarter-out slope (1Q23–2Q26): 0.332 full; range **0.258–0.350**; without 1Q23 → **0.258**.

### 2.7 Residual after the freeze
`gap_q = y_q − (a + b·x_q)` for q ≥ 3Q25. This is the post-launch residual; it equals the option term I only under stable
lead time, LOS, review propensity, sample-to-platform composition and model form.

### 2.8 The current-quarter read — `stages.stage_c3_3q26` + E6
Partial window 1 July → **dump − k, k = 14 days** (`E6_nowcast.pick_k`, first day with ≥ 98.5% posting completeness),
day-matched against the same window **364 days** earlier, same-age across vintages, per region:
NAM 6.85 · EMEA 0.86 · LatAm 27.53 · APAC 7.35 (%). 3Q26 weights: NAM .265 · EMEA .515 · LatAm .100 · APAC .120.
Composite **5.899** + partial-to-full gap **+0.087** = **5.987** → through the frozen mapping → **8.918%** →
133.6m × 1.08918 = **145.5m**, band ±1.852 → **[143.0, 148.0]**.
*Caveat on the +0.087:* estimated on the single-file construction 2023–25 and applied to the same-age one
(`q3_2026_nowcast.csv` labels it `assumed_from_yoy_all`).

---

## Part 3 — Evidence

### 3.1 Stage A — does the count measure stays? (`panel.py`)
Panel: 18 EU countries × 2023-01..2026-03. `Y = log(N_t/N_{t−12})` Eurostat; `X = log(1+g)` review growth.

| test | statistic | value | note |
|---|---|---|---|
| A1 country FE | β (cluster se; t; wild-cluster p) | **0.4936** (0.0696; 7.09; **0.001**) | n 702, 18 clusters, within-R² 0.358 |
| **AUDIT** country **+ month** FE | β (se; t; p) | **0.3127** (0.0692; 4.52; **0.001**) | 37% of A1 was common EU time variation |
| A2 first differences | β_Δ (se; t; p) | **0.7034** (0.1030; 6.83; **0.001**) | n 684 |
| A3 leave-one-country-out | β range | 0.471–0.547 | all same sign |
| A4 era split | β 23–24 vs 25–26 | 0.456 (0.081) vs 0.431 (0.124), \|z\| 0.17 | non-rejection, not proof of stability |
| A5 per-country walk-forward | median ratio vs naive | **0.590** | 486 scored months; 17/18 ≤ 0.75 (CZ 0.42 … MT 0.76) |

### 3.2 Stage B — does the index forecast the KPI? (`scoring.py`, E5's function verbatim)
Protocol: at each scored quarter, refit a,b on prior quarters in the window; predict; compare to naive `y_{t−1}`.

| window | n | RMSE idx/naive | **ratio** | 90% block bootstrap | DM | p | vs prior-yr | vs AR(1) | mean err | sign acc |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| W1 1Q23–2Q26 | 14 | 2.080/2.877 | **0.723** | [0.614, 1.081] | −1.29 | 0.218 | 0.169 | 0.521 | +1.198 | 0.571 |
| W2 1Q24–2Q26 | 10 | 1.561/2.159 | **0.723** | [0.577, 0.966] | −1.20 | 0.261 | 0.425 | 0.741 | +0.101 | 0.600 |
| W2 pre-RNPL 1Q24–2Q25 | 6 | 1.850/2.641 | 0.700 | [0.489, 0.846] | −1.12 | 0.312 | 0.417 | 0.666 | +0.442 | 0.667 |
| W1 acceleration | 13 | 7.133/4.572 | **1.560** | — | — | — | 0.901 | 2.193 | −6.121 | 0.462 |
| W2 acceleration | 10 | 2.309/3.393 | 0.680 | — | — | — | 0.680 | 0.807 | −0.185 | 0.600 |

Construction comparison (full/level): `yoy_vmatch_mix` **0.723/0.723** · `yoy_vmatch` 0.682/0.720 · `yoy_all` 0.749/0.684 ·
`yoy_all_mix` 0.823/0.749 (fails W1) · `yoy_mature` **0.972/0.908** (fails both).
**AUDIT:** W2 ⊂ W1, **10 shared quarters**. W1 scored from 3Q23 (dropping 1Q23–2Q23) = **0.838**. The two biggest naive
misses are 2Q23 (−7.62) and 1Q25 (+4.43); the index's own worst are 2Q23 (+4.58) and 1Q24 (+3.23).
**AUDIT weights sensitivity** (`audit/weights_sensitivity.csv`), reported in full, none selected:

| scheme | W1 | W2 | a | b | band | 3Q26 read |
|---|---:|---:|---:|---:|---:|---:|
| contemporaneous stay-mix (as run) | 0.723 | 0.723 | 6.825 | 0.350 | 1.850 | 8.92 |
| **lagged stay-mix (real-time policy)** | 0.723 | 0.723 | 6.675 | 0.363 | 1.841 | **8.85** |
| FY25 annual (v2) | 0.682 | 0.720 | 6.517 | 0.345 | 1.881 | 9.35 |
| equal | 0.760 | 0.770 | 6.342 | 0.314 | 2.041 | 9.72 |

### 3.3 Stage C — the post-launch residual

| quarter | index | mapped | printed | **gap** | in bands |
|---|---:|---:|---:|---:|---:|
| 3Q25 | 3.18 | 7.94 | 8.80 | **+0.86** | 0.46 |
| 4Q25 | 7.60 | 9.48 | 9.82 | **+0.34** | 0.18 |
| 1Q26 | 8.96 | 9.96 | 9.15 | **−0.80** | −0.43 |
| 2Q26 | 5.62 | 8.79 | 10.34 | **+1.55** | 0.84 |
| **mean** | | | | **+0.486** | **0.26** |

Pre-registered line (mean > 1 band **and** ≥ 3 of 4 > ½ band): **not met** → pre-written reading "no measurable RNPL
signature in stays". **AUDIT power:** 6% / 16% / 32% / 53% / 86% against true effects of 0.5 / 1.0 / 1.5 / 2.0 / 3.0 pp.
Cohort-consistent variant (kernel deconvolution): mean −0.47 against a ±3.11 band — uninformative.
C2 bound: gap ÷ disclosed bundle lift = 0.24 ± 0.93 (β_B 2 pts) or 0.16 ± 0.62 (3 pts) — covers 0 and 1.

### 3.4 Stage D — why no causal DiD
US minus never-treated controls, y/y log stays, 2024-01..2025-07: **−3.95 pp** (parallel trends fail before treatment).
MDE at α .05 / power .8: **7.17 pp** (permutation) / **3.98 pp** (placebo dates) against a sought effect ≤ 3 pp.
Reported as a power analysis; the event study is labelled EXPLORATORY. **Note (19 Sep):** RNPL went global in Feb 2026,
so EU markets are *not* valid never-treated controls after 1Q26 — the post-Feb-2026 months of that figure are contaminated.

### 3.5 Stage E — the balance sheet
Spread = unearned fees y/y − GBV y/y. Pre-RNPL 1Q23–2Q25: **+2.696 ± 2.947 pp (n 10)**; lag-1 autocorrelation **−0.14**.
Post: −4.09 / −8.05 / −18.81 / −16.65 → z −2.30 / −3.65 / −7.30 / −6.56. Welch t **−4.04, p 0.021**; ex-FX **−3.50, p 0.028**.
**AUDIT** block-position permutation: the post block is the most extreme of 11 positions, **p = 0.091 (the floor, 1/11)**.
Both known confounds bias toward the null (single-fee migration raises unearned fees; ex-FX is the FX-clean comparator).
**What this establishes:** payment deferral and RNPL exposure. **What it does not:** conversion deterioration.

### 3.6 Stage F — the forward model
`print = stays + I`. Level channel: each writing wave's exercise lands at stay dates through the kernel. Y/y channel:
`I_yoy,t = I_t − I_{t−4}`.

| quarter | stays y/y | base print y/y | I (pp) | **I y/y (pp)** | level |
|---|---:|---:|---:|---:|---:|
| 3Q26 | 8.92 | 9.89 | +0.97 | **+0.11** | 146.8 |
| 4Q26 | 8.12 | 8.12 | 0 | **−0.34** | 131.8 |
| 1Q27 | 8.21 | 8.21 | 0 | **+0.80** | 169.0 |
| 2Q27 | 5.93 | 5.93 | 0 | **−1.55** | 157.1 |
| 3Q27 / 4Q27 | 6.23 / 6.05 | same | 0 | — | 156.0 / 139.8 |

Filed laps carried in the base (independent of the above): 4Q26 −0.78 · 1Q27 −1.11 (+1.0 event) · 2Q27–4Q27 −1.65.

---

## Part 4 — The three interpretive layers, kept apart

| layer | status | what it rests on |
|---|---|---|
| **Measured** | reviews measure stays; the index tracks reported growth; the post-launch residual is bounded at ±1.85/quarter; unearned fees diverged from GBV (p 0.02) | the engine's own outputs |
| **Disclosed** | RNPL bookings "have experienced higher cancellation rates"; 16% → 17%; RNPL "driving longer booking lead times"; "net impact positive"; >20% of GBV; global since 17 Feb 2026; eligibility expanded July 2026 | Airbnb filings, letters, calls |
| **Assumed (team)** | the *size* of the conversion shortfall; the adoption ceiling in 1Q27; the exercise schedule; that the base carries laps and not the drag (DEC-0020) | judgement, anchored on the disclosures |

The pitch language must preserve these boundaries. The engine does not prove RNPL damages conversion; Airbnb says
cancellation rates are higher; the team sizes and times the consequence.

---

## Part 5 — Known errors already corrected, and errors still live

**Corrected, dated in the documents:** "~1 growth point" misattributed to RNPL (it is the Middle East conflict, D042);
a plain-English sentence implying cancelled bookings stay in the KPI (they are netted in the period they occur);
"700,000 review records" (that is the daily row count; the corpus is 75.1 M reviews); "Europe is not in the rollout
list" / "a European launch would defer the hit" (RNPL is global since 17 Feb 2026).

**Live, not yet fixed:**
1. `final_model_paths.csv` **phase labels are stale** — they read "flat: laps the −0.07" for 1Q27 and "THE HIT … 2Q26 wave"
   while v2.1's gaps are −0.80 (1Q26) and +1.55 (2Q26). The y/y numbers updated; the words did not.
2. **1Q27's option term flipped sign** under v2.1: **+0.80 pp** (lapping a negative 1Q26 residual), i.e. a y/y *tailwind*,
   not "flat". Any narrative that says 1Q27 is neutral is now inconsistent with the engine's own table.
3. `final_model_landing.csv` feeds **net** gaps into the kernel as if they were **gross** cohorts — double counts.
4. The **ceiling** argument must be restated: access is global; the remaining fuel is adoption inside a fixed pool.
5. Backtest weights are contemporaneous (look-ahead). The lagged run exists and matches; it is not yet the primary.

---

## Part 6 — Statistical review register

Ranked. **S = severity for the claim; F = feasibility of resolution before 2 Oct.**

### 6.1 Blocking — the claim is wrong or unverifiable without these

| # | issue | current state | what a reviewer must check | what would settle it | S | F |
|---|---|---|---|---|---|---|
| R1 | **Predictor is not point-in-time.** Every historical index value is reconstructed from the 2025/26 files; regional weights use same-quarter 10-Q revenue | `audit/availability_table.csv`; verdict "retrospective reconstruction" | that no claim of real-time forecast skill is made anywhere | the Mar 2023–Jul 2025 Inside Airbnb vintages (archive request), or the 5 Nov print as the first honest observation | high | low |
| R2 | **Selection / no untouched sample.** 256-cell grid (11 Sep) → v2 declared 18 Sep knowing neighbours → v2.1 after seeing v2; all scored on the same 14 quarters | `REVIEWS_INDEX_v2.md` §2.3, chronology in the review response §F | that "pre-registered" is not read as "out-of-sample" | one future quarter, scored | high | low |
| R3 | **Stage C is a bound, not a test** (power 16% at 1 pp) | `audit/f_h_checks.json` | that no document calls the C1 result a test of RNPL | either accept it as a bound, or pool quarters/sharpen the band | high | done |
| R4 | **Band uncertainty.** 1.85 is an RMSE of 6 errors; bootstrap [1.11, 2.46]; no coverage known; parameter and partial-quarter uncertainty excluded | `audit/f_h_checks.json`; `q3_2026_nowcast.csv` `gap_sd_pp` | whether ±1.85 is used as an interval anywhere | a predictive interval that adds parameter variance (delta method or bootstrap of a,b) and the partial-quarter term | high | high |
| R5 | **Residual is not identified as RNPL.** Longer lead times (disclosed, D033), LOS drift, propensity drift, mix drift all produce a positive residual | Part 4 | that every mention says "consistent with, under stated assumptions" | a lead-time control from the K2 kernel refit per year; an LOS series | high | med |

### 6.2 Important — change the numbers or the interval, not the direction

| # | issue | current state | what would settle it | S | F |
|---|---|---|---|---|---|
| R6 | W1 pass depends on 1Q23–2Q23 (0.723 → **0.838** without them) | audit | report both; lead with W2 | med | done |
| R7 | W1 and W2 share 10 of 14 quarters — not two independent tests | audit | state the nesting wherever "both windows" appears | med | done |
| R8 | Intercept is 77% of the 3Q26 read; *b* is small (0.35) so the index moves the answer 0.35 pp per point | Part 2.6 | a sensitivity: read vs index ±2 pp; and an economic account of the intercept | med | high |
| R9 | 1Q23 leverage: slope 0.332 → **0.258** without it | `stage_b_loco_slopes.csv` | re-read 1Q23 from the 2023 vintage (114 markets exist) | med | high |
| R10 | LatAm is 5 markets and carries ~2.5–4.9 index points in most quarters | Part 2.3/2.8 | a jackknife of the index by region; more LatAm markets | med | high |
| R11 | Mixed vintage ages inside the "same-age" construction (dumps span 2026-06..08 across markets) | `select_vintages` | per-market age distribution and a sensitivity dropping markets whose pair ages differ by > 30 days | med | high |
| R12 | Partial-to-full gap (+0.087) estimated on a different construction than it is applied to | `q3_2026_nowcast.csv` | re-estimate the gap on the vmatch series across 2023–25 | med | high |
| R13 | Stage E: n 4 post vs 10 pre; Welch on possibly seasonal spreads; permutation floor 0.091 | `audit/e_uf_gbv_checks.json` | quarter fixed effects on the spread, or a longer pre-window (2019–22) | med | high |
| R14 | Panel β halves with month FE (0.494 → 0.313) — the headline number is the weaker specification | `audit/g_twoway_fe.json` | quote 0.31 as the conservative figure | med | done |
| R15 | Eurostat pools four platforms; Airbnb share drift is an unmeasured bias in β | Part 1.2 | Airbnb's EU share trend, or a country subset where Airbnb dominates | med | low |

### 6.3 Worth reviewing — methodology hygiene

| # | issue | what would settle it |
|---|---|---|
| R16 | DM test uses HLN correction with h = 1; overlapping windows are not accounted for across W1/W2 | one DM per window only (already the case); do not pool |
| R17 | Block bootstrap block length = 2 chosen, not tuned | report ratio interval for block ∈ {1,2,3} |
| R18 | Wild-cluster bootstrap 999 draws → p floor 0.001; "p = 0.001" is a floor, not a point estimate | say "p ≤ 0.001" |
| R19 | A3/A4/A5 are described as tests in one place; they are robustness/out-of-sample checks | corrected in the explainer; verify no other file repeats it |
| R20 | The C1 pre-registration mixed a mean condition and a count condition (correlated) | state the joint null explicitly if reused |
| R21 | Multiple constructions scored on one sample without a family-wise correction | report the whole table (already done) and avoid any "significance" language for B |
| R22 | The cohort variant's deconvolution amplifies noise (band ±3.11) — it should not be quoted as corroboration | keep it as reported-only |

### 6.4 What a statistician should be given
`REVIEWS_INDEX_v2.md` (§1 frozen pre-registration, sha256 `a531e9b0…`), this file, `stage_a_tests.csv`,
`stage_b_walkforward.csv` + `stage_b_paths.csv`, `stage_c_gap.csv`, `audit/*`, `panel_country_month.csv` (the raw panel),
and `run.py --stage all` to reproduce. The two questions to put to them first: **(1) Is any statement of forecast skill
defensible given R1 and R2? (2) What is the right predictive interval for the 3Q26 read given R4?**

---

## Part 7 — The defensible claim set, as of today

**Can say.** Review counts co-move with observed platform nights across 18 countries and 702 country-months (β 0.31–0.49,
p ≤ 0.001, out of sample in 17 of 18). On 1Q23–2Q26 the index tracks reported nights growth with ~28% lower walk-forward
error than naive on both windows, with intervals that include 1.0, on a sample used to develop the method and with a
retrospectively reconstructed predictor. The 3Q26 stays read is 8.92% ± 1.85 (145.5m), produced 18 Sep on data through
~17 Aug — the first point-in-time observation. Unearned fees diverged from GBV by 2–7 sd after the RNPL launch (p 0.02).

**Cannot say.** That the engine estimates realised Airbnb stays independently. That it beats consensus (no historical
nights consensus exists). That it forecasts turning points (acceleration fails W1). That RNPL has measurably reduced
conversion — Airbnb discloses higher cancellation rates; our residual cannot detect an effect below ~2 pp.

**Next real evidence.** 5 Nov 2026: the 3Q26 print against 8.92 ± 1.85, scored and published whatever the outcome.
