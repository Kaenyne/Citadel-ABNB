# Rationale — nights: the stays measurement, the print, the Street, and the RNPL timing

> **Correction, 19 Sep 2026.** (1) RNPL has been available **globally** since 17 Feb 2026 (Airbnb Newsroom, ledger D025; 4Q25 letter D023
> "even more guests globally in 2026"). Statements that Europe is not in the rollout list, that "a European launch would defer the hit",
> or that EU markets are never-treated controls are wrong: the geographic ceiling was reached in Feb–Mar 2026; the last eligibility
> expansion was July 2026; the remaining growth in the option flow is adoption within a fixed pool (and any further eligibility change).
> The exploratory event study's post-Feb-2026 months use contaminated controls. (2) Management states RNPL is "driving longer booking
> lead times" (1Q26 call, D033, mirror): a lead-time extension lifts printed nights above review-implied nights without any
> cancellation — an additional, disclosed explanation for a positive post-launch residual. (3) The review data comprise **75.1 million
> reviews** across 123 cities in the latest vintage (49 M since 2023); "700,000" in earlier drafts counted daily aggregate rows.
> **Corrections, 18 Sep 2026 (audit, see `NIGHTS_ENGINE_REVIEW_RESPONSE.md`).** (1) Wherever this file attributes "~1 growth point"
> of nights cost to RNPL: that figure is the Middle East conflict cancellation effect in the 1Q26 letter (ledger D042), not RNPL —
> withdrawn. The RNPL cancellation disclosures are the 2Q26 10-Q ("higher cancellation rates than historic bookings") and the
> 4Q25 call's 16% → 17% (mirror transcript). (2) Any sentence implying a cancelled booking stays in the reported KPI: the KPI is
> "net of cancellations and alterations that occurred in that period" (2Q26 10-Q) — a cancellation is subtracted in the quarter it
> occurs. (3) "Stays-implied" means review-implied *reported*-night growth under the pre-launch relation; the post-launch residual
> is a bound (16% power against 1 pp), not a test; the walk-forward predictor is reconstructed from 2025/26 files, not point-in-time.
> The size of any RNPL conversion effect is a team assumption anchored on disclosures, not a measurement of this engine.
Session OLS.V2 with Theo, 18 September 2026. Companion to `REVIEWS_INDEX_v2.md` (spec, pre-registration, results) and to the
main session's `docs/pitch-model-v2/lines/final_nights.md` (the mechanism base and the filed laps). Written in the form
DEC-0026 asks for: every number with the reason it stands, the data and code behind it, every alternative considered with
its own number, and how each thesis catalyst enters. The final picture is `figures/reviews_index_v2/fig8_final_model.png`.


> **v2.1 (18 Sep evening).** After this rationale was written, Theo pointed at the regional-mix data already in the record and the
> weights were corrected from Airbnb's FY25 annual nights shares to the **stay-quarter mix** (quarterly regional revenue ÷ the
> regional ADR index; EMEA ~51% of stays in Q3, LatAm ~9%). Same frozen pass lines: walk-forward 0.723 / 0.723 (still clears
> both), gap mean +0.49 inside the band (same reading), **3Q26 stays read 8.92% ± 1.85 → 145.5m
> [143.0, 148.0]**, Street 149.0 at 1.41 bands (P ≈ 8%). Every 9.35 / 146.1 / 12% below is the v2 number; v2.1 is the primary
> in the engine and the note's §5 carries both side by side. The logic of every section is unchanged; §2.3's weights are the
> one construction choice that changed, and §7's timing is unaffected.

---

## 0. The claim, in one sentence, and the numbers

**Airbnb's reported nights are running ahead of the stays that actually happen, because a fifth of bookings now carry a
free cancellation option; the option is being written faster than it is exercised, the balance sheet shows it, and the
print will give it back in 4Q26 and 2Q27 — the Street is pricing the top of the writing wave.**

| object | number | where it comes from |
|---|---:|---|
| 3Q26 stays (the business) | **+9.35% ± 1.88 → 146.1m [143.6, 148.6]** | v2 index through the frozen mapping (§4) |
| 3Q26 print (what Airbnb reports) | 9.35–10.94% → 146.1–148.2m; base 9.89% (146.8m) | stays + the option term (§5); DEC-0029 |
| 3Q26 Street | 149.0m (+11.53%; 147.0–151.0, n 28) | Bloomberg MODL 12 Sep (DEC-0005) |
| probability the print is at or above the Street, on the stays read | **12%** (36% for the Street's low) | §6 |
| 4Q26 base / Street | 131.8m (+8.12%) / 134.0m (+9.93%) | DEC-0019 / record |
| 2027 base | 169.0 / 157.1 / 156.0 / 139.8m; FY27 621.8m, +6.64% | DEC-0025 |
| where the RNPL hit lands | **4Q26 (−0.4 pp level) and 2Q27 (−1.6 pp y/y)**; 1Q27 neither | §7 |

---

## 1. What we measure, and why it is a measurement rather than a proxy

A review on Airbnb can only be written after check-out. So a review is a **completed stay**, dated at the stay. The count of
reviews in a set of markets is a census of stays in those markets — not a sentiment, not an intention, not a search.
Everything else the team tested in the 3,500-test record (Google Trends, macro, tone, peer prints) measures something
adjacent to nights; this measures nights' own realised half.

**The data.** Inside Airbnb's published review logs for 123 city markets, per listing, per review date, held in two annual
vintages (August 2025, August 2026) plus a Mar–May 2023 vintage for 114 markets. On this machine: `data/processed/q3nowcast/E/
market_vintage_daily.csv` (697,889 market × dump × day rows) and `market_vintage_monthly.csv`. Not scraped by us; mirrored from
the published files.

**Why we can say it measures stays — the Eurostat panel (Stage A).** Eurostat publishes, monthly and per EU country, the
nights actually spent in platform-booked short-stay rentals. That is observed ground truth for exactly what a review count
should track. Summing our cities to 18 countries and regressing observed-nights growth on review growth with a fixed
effect per country, on 702 country-months (2023-01 to 2026-03):

- β = **0.494**, cluster se 0.070 (18 clusters), t 7.1, wild-cluster bootstrap p **0.001**; within-R² 0.36.
- in first differences β = **0.703**, p 0.001 — month-to-month *changes* co-move, so this is not two series drifting down together after COVID.
- leave-one-country-out: 0.471–0.547, all the same sign; no single country carries it.
- 2023–24 vs 2025–26: 0.456 vs 0.431, |z| 0.17 — no break across the RNPL era.
- out of sample, per country, expanding walk-forward from 2024-01: median RMSE **0.59 of naive**, 17 of 18 countries at or below 0.75 (CZ 0.42 … NO 0.68; MT 0.76).

Why β is 0.5 and not 1: reviews grow faster than nights — new listings get reviewed more, propensity drifts up. The point is
not the level of β but its **stability**: the same proportionality in 18 countries and across three years. A scaled
measure, consistently scaled.

**What this does and does not establish.** It establishes that the instrument reads stays. It does not supply the slope to
Airbnb's KPI (§3): we tested importing β = 0.494 as the Airbnb slope and it fails on the record's yardstick (walk-forward
4.47× naive), because the elasticity of our *urban sample* to *Airbnb's global booked nights* is a different, smaller number
(0.345) that must be estimated on Airbnb's own history. The panel is validation; the mapping is fitted. Two claims, kept apart.

---

## 2. Why the index is built the way it is — every construction choice against its alternative

**2.1 Same-age vintages (`yoy_vmatch`), not one file.** A dump holds only listings alive on the dump date. Read last year's
month in this year's file and the reviews of every listing delisted since are gone. Paris, June 2025: **74,784** reviews from
26,826 listings when read fresh (Aug 2025 file); **59,070** from 21,146 listings when read a year later (Aug 2026 file) — 21% of
the listings gone, and their reviews with them. Within one file Paris June 2026 reads **+11.7%** (65,997 / 59,070); at the
same age in two files it reads **−11.7%** (65,997 / 74,784). The v1 index used the one-file version for every market and
absorbed the wedge in a 20-point intercept, assuming it constant; WPK-A's re-vintaging (14 Sep) found it is not — retention
is 0.63 at 1–3 months of age, 0.71 at 36, 0.74 at 60 — largest and least stable on the youngest months, exactly the nowcast
edge. v2 does not estimate the wedge; it cancels by construction. *Alternative kept as sensitivity:* `yoy_all` under v2's
aggregation still clears both windows (0.749 / 0.684), so weighting and trimming matter as much as vintage-matching.
*Alternative rejected:* same-store (`yoy_mature`, listings ≥ 12 months old on both sides) fails the yardstick (0.972 / 0.908) —
the nights signal is carried by stays on new listings; a same-store construction measures the wrong thing.

**2.2 Posting-lag trim.** Reviews are written after check-out and keep arriving for weeks; the last two months before each
dump are incomplete and are dropped (June 2026 is the last month used from the August 2026 files). *Alternative:* E6's
day-matched partial window with a measured completeness curve — used for the 3Q26 quarter-to-date read (§4), not for the
history.

**2.3 Review-share within region, FY25 nights shares across regions.** Cities are summed within each of NAM / EMEA / LatAm /
APAC (numerators over denominators, so a city counts by its size), then the four regional growth rates are weighted by
Airbnb's disclosed FY25 share of nights: 28.3 / 41.6 / 17.9 / 12.3. Reason: the sample's mix is Inside Airbnb's coverage, not
Airbnb's footprint — EMEA is 56 of 123 cities and ~57% of reviews but 41.6% of Airbnb's nights; LatAm is 5 cities and 9% of
reviews but 17.9% of nights. *Alternative:* E5's equal-weighted `GLOBAL_NW` (0.708 / 0.809) and review-weighted `GLOBAL`
(0.754 / 0.682) each clear one window, never both. *Fragility stated:* five LatAm cities at +20.4% contribute 3.65 of 2Q26's
6.50 points and 4.9 of 3Q26's 8.12.

**2Q26, the worked example.** NAM 42 cities 1,062,749 / 994,190 = +6.90%; EMEA 56 cities 2,640,604 / 2,602,033 = +1.48%; LatAm 5
cities 418,408 / 347,527 = +20.40%; APAC 16 cities 500,145 / 488,886 = +2.30%. Weighted: 1.95 + 0.62 + 3.65 + 0.28 = **6.50%**.
119 of 123 markets have both vintages; 16,963 market-months in the panel. v2 reproduces E4's published `yoy_all` index to the
decimal on every quarter before it changes anything (`tests/`), so the difference is the construction, not the counting.

---

## 3. The mapping to Airbnb's KPI — why two parameters, why frozen, what each one is

`nights y/y = 6.517 + 0.345 × index`, fitted by OLS on the ten quarters 1Q23–2Q25 and **frozen there**.

**Why a mapping at all.** Our sample is urban cores; Airbnb's growth is in non-urban and expansion markets we do not hold;
reviews grow faster than nights (§1). A stays growth rate in the sample is therefore a scaled, shifted read of Airbnb's global
nights growth. **The slope 0.345**: one point of sample stays growth is worth a third of a point of Airbnb nights growth — part
propensity (the panel's 0.49 says reviews outrun nights everywhere), part composition (urban vs global). **The intercept 6.5**:
if the sampled cities were flat, Airbnb would still grow ~6.5% — the growth happening where we do not look. It is the
parameter carrying the most weight on the least data, and it is why the read is quoted only with its out-of-sample band.

**Why frozen at 2Q25.** The US RNPL launch was August 2025. A mapping refit through 2026 would absorb into its coefficients the
very thing §5 measures. Freezing makes every post-launch residual a measurement, not a fit.

**The evidence (Stage B) — the record's yardstick, not a p-value.** Stand at each quarter-end since 1Q23, refit on the past
only, predict, record the miss. Fourteen misses on W1 (window 2022Q1+, scored 1Q23–2Q26), ten on W2 (2023Q1+, scored
1Q24–2Q26). Baseline: "next quarter's y/y equals this quarter's" — genuinely hard to beat on a smooth series, and unbeaten by
3,500 tests.

| | RMSE index | RMSE naive | **ratio** | 90% block bootstrap | DM p | vs prior-year | vs AR(1) | mean error |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| W1, n 14 | 1.96 | 2.88 | **0.682** | [0.57, 1.02] | 0.21 | 0.16 | 0.49 | +0.93 |
| W2, n 10 | 1.55 | 2.16 | **0.720** | [0.53, 1.00] | 0.29 | 0.42 | 0.74 | −0.11 |
| W1 pre-RNPL, n 10 | 2.29 | 3.33 | 0.687 | [0.56, 0.93] | 0.25 | | | +1.24 |
| W2 pre-RNPL, n 6 | **1.88** | 2.64 | 0.712 | [0.51, 0.95] | 0.37 | | | +0.24 |

The pre-registered survivor line was 0.75 on both; v2 clears with 0.682 / 0.720 — the first construction in the record to
do so. The band on every read is the W2 pre-RNPL RMSE, **±1.88 pp**: the typical out-of-sample miss of this exact procedure,
not the in-sample residual. And the honest half, printed by pre-commitment: at n 10–14 the bootstrap interval reaches 1.0 and
the Diebold–Mariano test does not reject equal accuracy. The memo says both halves: *clears the survivor line on both windows;
the interval at this n does not exclude naive.* The scorer reproduces E5's 0.683209 on the v1 cell before any v2 number is
written; the acceleration target (Δ of y/y) is 1.20 on W1 (fails) and 0.68 on W2 — the thesis is a shape, and the shape is
harder to forecast than the level.

**Alternatives and their numbers.** v1 (`yoy_all`, review-weighted, no trim): 0.837 / 0.683; re-vintaged W2 0.757. v1 plus
W2 bias correction: 9.52% for 3Q26 — a patch that worked because the inflation was roughly stable in-sample; v2 reaches 9.35%
by construction with no correction term. Imported panel β (slope 0.494, intercept only fitted): read 8.65%, walk-forward
4.47× naive — rejected (§1). Slope fixed at 1 (structural identity): impossible; the sample and population differ (§2.3).
Leave-one-quarter-out slope on 1Q23–2Q26: 0.327 full, range 0.248–0.355, **0.248 without 1Q23 — 1Q23 is still the leverage
point**; the walk-forward is immune (refits every quarter), the frozen mapping is not, so §4 reports the read both ways.
Cohort-consistent index (stays deconvolved with the K2 kernel into booking cohorts): band ±3.1 — the deconvolution amplifies
noise and it says nothing either way; kept as a reported variant.

---

## 4. The 3Q26 number, word by word

Quarter-to-date, 1 July to the dump date minus *k* days (from the posting-completeness curve), day-matched against the same
window 364 days earlier so the weekday mix is identical, same-age in two files, per region (E6's
`vintage_matched_nowcast.csv`, review-weighted): **NAM +6.85%, EMEA +0.86%, LatAm +27.53%, APAC +7.35%**. FY25-weighted:
1.94 + 0.36 + 4.93 + 0.90 = **8.12%**. Plus the measured partial-to-full-quarter gap, +0.09 → **8.21%**. Through the frozen
mapping: 6.517 + 0.345 × 8.21 = **9.35%**. On the printed 3Q25 base of 133.6m: **146.1m**, band ±1.88 pp → **[143.6, 148.6]**.

Sensitivities, all reported: E6's own review-weighted global cell (5.30%, a different aggregation) gives 8.34%; the mapping
without 1Q23 gives 9.45%; the mean post-launch gap with 1Q23 excluded is +0.51 pp at 0.23 bands (same conclusion as §5).
Fragility: LatAm's five cities carry 4.9 of the 8.12. Beside the record: v1 raw 10.04, v1 bias-corrected 9.52 (DEC-0004),
mechanism base 9.886 (DEC-0029), external stack 9.23, team baseline 9.9.

---

## 5. The print is not the business — the option term

Airbnb's *Nights and Seats Booked* counts a night **when it is booked**, net of cancellations **in the quarter the
cancellation occurs**. A review counts a night **when it is stayed**. Before RNPL the two agree through the mapping
(pre-launch residuals ±1.9 with a mean near zero). After RNPL they can differ by construction: a $0-down booking that later
cancels is in the print the quarter it is made, subtracted the quarter it cancels, and never a stay. So

> **print_t = stays_t + I_t**, with I_t = options written this quarter that will later cancel, less cancellations landing
> this quarter from earlier cohorts.

I_t is positive while RNPL access is expanding (more written than exercised), zero when the flow plateaus, negative if the
stock is exercised faster than it is refilled.

**What the four post-launch quarters show (Stage C, mapping frozen at 2Q25):**

| | 3Q25 | 4Q25 | 1Q26 | 2Q26 | mean |
|---|---:|---:|---:|---:|---:|
| index (%) | 4.70 | 7.52 | 7.84 | 6.50 | |
| stays-implied y/y | 8.14 | 9.11 | 9.22 | 8.76 | |
| printed y/y | 8.80 | 9.82 | 9.15 | 10.34 | |
| **gap = print − stays (pp)** | **+0.66** | **+0.71** | −0.07 | **+1.59** | **+0.72** |

The sign is the one the identity predicts for the writing phase, in three of four quarters, and it follows the rollout
calendar (US launch → 3Q25; the international wave, 18 Feb–4 Mar 2026, → 2Q26; 1Q26 flat because almost nothing was
written inside it and the launch cohorts' cancellations were landing). The size is inside the band: +0.72 against ±1.88 fails
the pre-registered pass line (mean > 1 band, ≥ 3 of 4 quarters > ½ band), and the pre-written reading applies — *no measurable
RNPL signature in stays*. Robust to dropping 1Q23 (+0.51). The wording the memo may use is fixed: **"consistent with"**, never
"shows". The 2Q26 gap of +1.59 is the largest and only 48% of that cohort's stays had landed at the June cut; the September
dumps settle it.

**The 3Q26 print, therefore, is stays + I:** 9.35% if exercise keeps pace with the July eligibility expansion; 10.07% at the
mean post-launch gap; 10.94% for a 2Q26-sized wave → **146.1 / 147.1 / 148.2m**. The mechanism base built independently from
the 10-K regional growth (DEC-0029, 9.886%) sits +0.54 above the stays read — two constructions agreeing once a modest
writing term is allowed.

---

## 6. The Street, and where the alpha is

**149.0m = +11.53%** on 133.6m; range 147.0–151.0, n 28 (Bloomberg MODL, 12 Sep; DEC-0005). On the stays read N(9.35, 1.88):
the Street is **1.16 bands above**; **P(print ≥ 149.0) = 12%**; P(≥ 147.0) = 36%; P(≥ 146.8, our base) = 39%. 4Q26: Street
134.0m (+9.93%) vs base 131.8m (+8.12%), 1.8 pp / one band.

**Why the Street's low is where it is.** The naive way to use Inside Airbnb — one file, this year over last, through a
regression fitted on the same inflated series — reads the 3Q26 quarter-to-date at +26.3% and gives, through v1's own
coefficients, **10.04% = 147.0m to the decimal**: the bottom of the Street range. Three layers sit between that and the stays
read: (i) the rest of the Street, to 151.0, is momentum plus the ~3 points of bundle lift management quoted plus the July
expansion; (ii) the naive read is itself inflated by survivorship — 15–21% of last year's reviews are missing from this
year's file, most on the youngest months — worth ~0.7 pp; (iii) the anchor every momentum model starts from, the 2Q26 print
at +10.34%, is 1.6 pp above what realised stays support.

**The honest size of the call.** 2.2 pp of nights growth, 2.9m nights, a 12% tail — not a certainty. And the way we are wrong:
if the July eligibility expansion is bigger than the 0.1–0.3 points carried in the module ("the largest unquantified offset in
the model", D2), the print lands inside our band and the Street was right to stand at the top of it. That is also why the
position is not the 5 Nov print (§7).

---

## 7. The RNPL catalyst — written, exercised, and when it lands

**7.1 Written: the balance sheet (statistical).** Unearned fees are recorded when cash is collected; an RNPL booking collects
nothing until its payment deadline. So the one line an option cannot touch is unearned fees, and the fingerprint of the option
being written at scale is unearned fees stalling while GBV grows. Spread = unearned fees y/y − GBV y/y
(`overnight/02_kpi_panel_quarterly.csv`):

| | 1Q23–2Q25 (10 quarters) | 3Q25 | 4Q25 | 1Q26 | 2Q26 |
|---|---|---:|---:|---:|---:|
| spread, GBV reported | **+2.7 ± 3.0 pp** | −4.1 | −8.1 | **−18.8** | **−16.7** |
| z vs pre-RNPL | | −2.3 | −3.7 | −7.3 | −6.6 |
| spread, GBV ex-FX | +2.8 ± 3.2 | −2.2 | −5.1 | −12.6 | −15.9 |

Welch t −4.04, **p 0.021** (reported GBV); −3.5, p 0.028 (ex-FX). Both audit corrections make it conservative: the single-fee
migration moves unearned fees *up* 3–4% (FY25 10-K Note 2), so the divergence is understated; unearned fees is the FX-clean line,
so the ex-FX row is the fair comparison and it still reads −13 to −16. The audit's stock estimate: 17–28M unpaid nights at 30
June (cited, not re-estimated). Airbnb lends nothing — this is an **option**, not credit: the guest holds a free right to cancel,
Airbnb and the host wrote it, and the unpaid stock is the open interest.

**7.2 Exercised: the company's own numbers.** Cancellation rate 16% → 17% (4Q25); "~1 growth point" of nights cost (1Q26 call);
take-up ~70% of guests offered; RNPL "over 20%" of GBV (2Q26); 2Q26 10-Q MD&A: RNPL bookings "have experienced higher
cancellation rates than historic bookings". Macro and sentiment do **not** enter as coefficients: 1,408 macro pairs in the
record, nights sensitivity zero. What macro can move is the exercise rate on a stock of unpaid bookings that did not exist
before August 2025 — a scenario dial on x, bounded, not fitted.

**7.3 When it lands — two channels, each with its quarter.**

*Exercise happens at the stay date.* The payment is due shortly before the free-cancellation window closes (ledger D002:
flexible 24 hours, moderate 5 days before check-in). So the cancellation flow follows Airbnb's **stay** calendar, and the K2
lead-time kernel times it: a cohort's stays — and its exercise decisions — land ~50% in the booking quarter, ~35% the next,
~10% two out, 3–6% three out.

*Level channel — where each writing wave's cancellations land* (cohort size = the observed gap, pp of nights, at the historical
exercise rate; `final_model_landing.csv`):

| written | 2Q26 | 3Q26 | 4Q26 | 1Q27 | 2Q27 |
|---|---:|---:|---:|---:|---:|
| 3Q25 launch + 4Q25 (+0.66, +0.71) | 0.10 | 0.04 | — | — | — |
| 2Q26 international wave (+1.59) | 0.77 *(inside the 2Q26 gap)* | **0.60** | 0.18 | 0.04 | — |
| 3Q26 July expansion (+0.54 base) | — | 0.26 | **0.20** | 0.06 | 0.03 |
| **landing, pp** | 0.87 | **0.89** | **0.38** | **0.10** | 0.03 |

The expansion cohorts' cancellations pile up in **3Q26 (0.89, netted by the July writing — "RNPL does not show in Q3") and
4Q26 (0.38, the first hit)**. By 1Q27 they are ~90% resolved; 1Q27's own writing — the largest booking quarter of the year at
the ceiling — nets the 0.10 left, which is what 1Q26 showed (−0.07).

*Y/y channel — the print laps its own inflated year-ago.* The KPI is reported year over year, so this quarter's net writing minus
what was written a year earlier is what bites: 3Q26 **−0.12** (July writing laps the launch: nets), 4Q26 **−0.71**, 1Q27 **+0.07**,
2Q27 **−1.59** (the international wave laps with nothing to net it). This matches, quarter by quarter, the laps the main session
filed from the disclosures and carries in the base path: −0.78 (4Q26), −1.11 + 1.0 event (1Q27), −1.65 (2Q27). Two independent
constructions, one timing.

**So: 4Q26 is the first hit (level), 2Q27 the second and larger (y/y), 1Q27 sits between them with neither.** Cumulative over
4Q26–2Q27: −2.2 pp; the split across quarters is only as good as each quarter's gap, and 1Q27's share is the least certain.

**7.4 The assumptions that carry the timing, and how each is wrong.**
- **The ceiling** — no further access growth after the July 2026 eligibility expansion (UK/AU/CA done Feb–Mar 2026; BRL/INR/TRY
  excluded). **Europe is not in the rollout list.** A European launch in 1H27 writes a new wave that nets the 2Q26 cohort and
  defers the hit two to three quarters. This is the load-bearing assumption and the first thing to watch.
- **The exercise rate** — 16–17% historical. If the stock cancels harder (consumer stress), the drag is a level effect, untimed
  by cohorts: the short case (4Q26 7.61%, DEC-0020 deferred).
- **Long-lead bookings** — 3–6% of any cohort by the kernel; only these could push the expansion cohorts' cancellations into 1Q27.

---

## 8. The forward path, and how each catalyst enters numerically

Base (main session, DEC-0019 / DEC-0025); every term sourced; the base carries the laps and **not** the cancellation drag
(adding a drag on top double-counts, `final_nights.md` §4.4):

| quarter | underlying | fee / cancellation lap | ex-NA RNPL lap | events | **y/y** | level | Street |
|---|---|---:|---:|---:|---:|---:|---:|
| 3Q26 | 0.288 × NA +5.60 + 0.712 × ex-NA +11.62 | (US lap inside M1) | | | **+9.89** | 146.8m | 149.0m |
| 4Q26 | reference +8.90 | −0.78 | in the −0.78 | — | **+8.12** | 131.8m | 134.0m |
| 1Q27 | 0.291 × +2.31 + 0.709 × +10.773 = +8.31 | −0.742 | −0.363 (40%) | +1.0 | **+8.21** | 169.0m | — |
| 2Q27 | 0.291 × +2.31 + 0.709 × +10.452 = +8.08 | −0.742 | −0.907 (full) | −0.5 World Cup lap | **+5.93** | 157.1m | — |
| 3Q27 | +7.86 | −0.742 | −0.907 | — | **+6.23** | 156.0m | — |
| 4Q27 | +7.63 | −0.742 | −0.907 | — | **+6.05** | 139.8m | — |
| FY27 | | | | | **+6.64** | 621.8m | |

The stays path is the same path from 4Q26 (I = 0 at the ceiling) with 3Q26 replaced by the stays read 9.35. The deceleration
from ~8 to ~6 is the arithmetic of laps already filed; the option term tells you *which* of those laps is the RNPL cohort
giving itself back, and when.

---

## 9. What settles it

**5 November (3Q26 print).** From `final_nights.md` §6.1 / `D1_prereg_thresholds.csv`, plus this note's additions:
a quantified bundle contribution ≤ 1.5 pts supports (≥ 2.5 weakens); RNPL share of GBV flat or down while nights decelerate
supports (≥ 25% with nights ≥ 10% weakens); **(3Q26 unearned fees y/y − GBV y/y) ≤ −18 pp supports**, −12 to −18 in line with
1H26, wider than −8 weakens; the print against the stays read — inside [143.6, 148.6] is the read; at or above 149.0 with
unearned fees stalling again is the thesis confirmed *on written options*, not refuted.
**September dumps.** Re-run `run.py --stage all`: the 2Q26 gap (+1.59 at 48% realised) tightens; 3Q26's I becomes a
measurement instead of a scenario.

---

## 10. Everything else that was considered, with its number

| alternative | result | why not |
|---|---|---|
| a staggered difference-in-differences on stays (US Aug 2025; UK/AU/CA Feb–Mar 2026; EU never) | US pre-trend **−3.9 pp** before launch; MDE **4–7 pp** vs a ≤ 3 pp effect; Canada +5 to +15 pp in 2026 (its own boom) | not identified; reported as a power analysis; the exploratory event study swings ±8 before launch and its June 2026 spike is the World Cup |
| macro / sentiment as regressors | 1,408 pairs, nights sensitivity zero | enters only as the exercise-rate dial |
| ML ensemble over all alt-data | not run | would fit 14–22 points and lose to naive walk-forward, as 3,500 tests did |
| stock-flow state-space with unearned fees as a measurement equation | designed, then split | the unearned-fees equation as first written was wrong in the RNPL direction (fees exclude the unpaid stock); the identity model is the main session's nights v3 (DEC-0033); this lane keeps nights only |
| within-US intensity by eligibility (domestic share, flexible/moderate policy share) | the one causal design that would work | needs per-listing data not on this machine |
| party-size text, Google Trends | — | ADR line / failed in the record |

---

## 11. Limits carried forward

Not point-in-time: every historical quarter is read from the 2025 / 2026 files; only two vintages exist (the fully honest
"each quarter read fresh from its own dump" needs the Mar 2023–Jul 2025 dumps, requested). The K2 kernel is a full-history
estimate. Eurostat pools four platforms and is national while our sample is cities. The disclosed 16 → 17% was not used
numerically (its basis is unpinned). Six calibration quarters set the band and 4Q24 dominates it. n on the Airbnb step is 14
and nothing changes that; it is printed, not hidden.

---

## 12. The sentences the memo may use

- "Review counts measure stays: elasticity 0.49 on 702 country-months against observed nights, survives first differences,
  forecasts out of sample in 17 of 18 countries."
- "The stays index clears the survivor line on both windows (0.68 / 0.72); at n 10–14 the interval does not exclude naive, and we say so."
- "3Q26: the business is +9.3% ± 1.9 (146.1m); the print is stays plus written options, 146–148m; the Street's 149.0 is a 12% tail
  on the stays read and reachable only on options that will not all convert."
- "RNPL is an option written at scale: unearned fees stalled at 0% while GBV grew 16–19% — a 2–7 sd divergence from ten pre-launch
  quarters, p 0.02 — and the company reports the option being exercised (16 → 17%, ~1 growth point)."
- "The stays data are consistent with, and do not yet prove, that RNPL bookings failed to become stays."
- "The hit lands when access stops growing: 4Q26 as the expansion cohorts cancel at their stay dates, 2Q27 as the print laps the
  2Q26 wave — the laps already filed. A European launch would defer it."

---

## 13. Provenance

| file | provides | decision / note |
|---|---|---|
| `data/processed/q3nowcast/E/market_vintage_{daily,monthly}.csv` | review counts by market × dump × date | E note; WPK-A |
| `data/processed/q3nowcast_v2/E/*` | 2023 vintage, attrition-by-age curve | WPK-A T1/T2 |
| `data/processed/eurostat_platform_nights_monthly.csv` | observed platform nights, 31 countries, 2018–2026-03 | Stage A |
| `data/processed/abnb_driver_history_quarterly.csv` | nights levels 1Q21–2Q26 | DEC-0003 |
| `data/processed/forecast_methods/kernel_leadtime_v2/K2_M_matrix.csv` | booking → stay quarter weights | kernel lane |
| `data/processed/q3nowcast/E/{vintage_matched_nowcast,q3_2026_nowcast}.csv` | 3Q26 quarter-to-date, partial-to-full gap | E6 |
| `data/processed/overnight/02_kpi_panel_quarterly.csv` | unearned fees, GBV reported / ex-FX | RNPL audit |
| `data/processed/overnight2/D/rnpl_statement_ledger.csv` | 60 verified RNPL statements (D001–D060) | overnight2 D |
| `docs/pitch-model-v2/lines/final_nights.md`, `DECISIONS.md` | base path, laps, Street bar, tells | DEC-0005/0019/0020/0025/0028/0029 |
| `analysis/src/forecast_methods/reviews_index_v2/` | this lane's engine; `run.py --stage all` | commit 07f8cb4 + this note |
