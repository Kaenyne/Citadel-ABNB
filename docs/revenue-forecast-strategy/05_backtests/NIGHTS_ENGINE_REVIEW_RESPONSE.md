# Response to the external review of the nights engine

> **Correction, 19 Sep 2026.** (1) RNPL has been available **globally** since 17 Feb 2026 (Airbnb Newsroom, ledger D025; 4Q25 letter D023
> "even more guests globally in 2026"). Statements that Europe is not in the rollout list, that "a European launch would defer the hit",
> or that EU markets are never-treated controls are wrong: the geographic ceiling was reached in Feb–Mar 2026; the last eligibility
> expansion was July 2026; the remaining growth in the option flow is adoption within a fixed pool (and any further eligibility change).
> The exploratory event study's post-Feb-2026 months use contaminated controls. (2) Management states RNPL is "driving longer booking
> lead times" (1Q26 call, D033, mirror): a lead-time extension lifts printed nights above review-implied nights without any
> cancellation — an additional, disclosed explanation for a positive post-launch residual. (3) The review data comprise **75.1 million
> reviews** across 123 cities in the latest vintage (49 M since 2023); "700,000" in earlier drafts counted daily aggregate rows.
18 September 2026, session OLS.V2. Scope: the concerns A–I in the reviewer's brief, checked against the code, the output
files and dated primary sources. New diagnostics run for this response are in
`data/processed/forecast_methods/reviews_index_v2/audit/` and are labelled AUDIT throughout; nothing in the original outputs,
the frozen pre-registration or the note was altered. Two factual errors in our own documents were found on the way and are
corrected at the top of each affected file with a dated line.

---

## Executive verdict

**What survives.** (1) The measurement claim: review counts, read at the same age in two file vintages, co-move with
*observed* platform nights across 18 EU countries — β 0.49 with country effects, **0.31 with country and month effects
(AUDIT)**, both at wild-cluster p 0.001; out of sample by country at 0.59 of naive. (2) The association between the
review index and Airbnb's reported nights growth over 1Q23–2Q26: a 28% lower walk-forward RMSE than "same as last
quarter", robust to four weighting schemes (0.68–0.77), the interval reaching 1.0. (3) The 3Q26 read as a genuine,
dated nowcast (data through mid-August, produced 18 Sep, print 5 Nov) — the first observation that will score the method
on data it was not developed on.

**What needs narrower language.** The fitted value is *review-implied reported-night growth*, not an independently
calibrated realised-stay estimate. The post-launch residual is a bound, not a test (16% power against 1 pp). The
walk-forward is a retrospective reconstruction of the predictor, not a point-in-time backtest. "Instrument" means
measurement proxy, not identification. "All five reject the null" becomes "two significance tests and three robustness
checks". The unearned-fees divergence establishes payment deferral and RNPL exposure, not conversion deterioration.

**What needs an implementation correction.** Regional weights in the backtest use the same quarter's 10-Q revenue
(look-ahead); the lagged policy gives the same ratio (0.723) but must be the one on the record. The kernel landing table
feeds a net gap in as a gross cohort and must be rebuilt or dropped. Two document errors: "~1 growth point" was the Middle
East conflict, not RNPL; "a cancelled booking … never in the second number" omits that the KPI subtracts it when cancelled.

**What remains unproven.** That RNPL has reduced booking-to-stay conversion by any measurable amount. Our data do not
show it; management's own words are "higher cancellation rates" (2Q26 10-Q, verified) and "net impact positive" (1Q26
call). The RNPL conversion effect in the pitch is a **team assumption anchored on those disclosures**, and the
documents must say so wherever it appears. A useful predictor survives this; the RNPL interpretation does not rest on
the predictor.

---

## Issue-by-issue response

### A. What the engine estimates, and what the residual means

**Verdict: valid.** The regression `nights y/y = a + b × index` (`stages.frozen_mapping`, `scoring.walkforward`) is fitted
on *reported, booking-dated* Nights and Seats Booked growth (`abnb_driver_history_quarterly.csv`). Its fitted value is
therefore **review-implied reported-night growth under the pre-August-2025 relation between stays and reported
bookings**. There is no independent calibration to realised Airbnb stays anywhere in the repo; the Eurostat panel
(`panel.run_stage_a`) validates that review growth co-moves with *observed platform guest-nights* in EU countries
(`tour_ce_omr`), which supports "the count reads stays" but does not calibrate the Airbnb mapping.

*Under what assumptions does the residual identify booking-vs-stay divergence?* Only if everything else in the
pre-launch relation is stable: lead-time distribution, length of stay, review propensity, the sample-to-platform
composition, and the model form. The residual cannot separate RNPL from any of those. The record's own §0.5/§2.7 list
them; the label did not.

*Levels vs growth.* The identity `N_t = G_t − C_t` is in levels. For the four scored post-launch quarters the year-ago
quarter is pre-launch, so the y/y residual approximates `I_t / N_{t−4}` in pp; from 3Q26 the year-ago term enters and the
lap channel (`final_model.py`, `I_yoy`) is the right object. Cancellations in the current quarter from earlier cohorts are
inside `C_t` in the identity and inside the residual empirically — not separately observed.

*Kernel.* Used in the primary read: **no**. It enters only the cohort-consistent variant (`stages.cohort_index`, reported,
band ±3.1) and the landing table (`final_model.landing_table`). The operational estimate is the same-quarter mapping.

**Consequence.** Rename: "stays-implied" → "review-implied reported-night growth"; "the option term I, observed" →
"post-launch residual of the frozen mapping". What remains useful: a predictor of reported growth with a measured error
scale, and a residual that bounds any post-launch shift at ±1.85 pp per quarter.

### B. Was the historical signal available before each forecast cutoff?

**Verdict: valid — and it is the most important correction.** Every historical predictor value is read from the August
2026 files (latest) over the August/September 2025 files (prior): `data.select_vintages` picks the latest dump per market
and the dump 300–430 days older; `index.market_monthly` builds `n_vm_cur/n_vm_prior` from those two vintages for every
month back to 2016 (`market_vintage_monthly.csv`; inventory in `q3nowcast/E/inventory.csv`, 832 files, 5 dump months:
2025-08/09, 2026-06/07/08). Publication ≈ dump date + 18 days (median of `cdn_probe_reviews.csv` last-modified);
downloads 11 Sep 2026 (`download_manifest.csv`). Regional weights for quarter t use the *same* quarter's 10-Q revenue
(`mix.seasonal_weights`), published ~5 weeks after the cutoff. The ADR index and drift rule come from a September 2026
note; the kernel is a full-history estimate.

**Availability table:** `audit/availability_table.csv` — every scored quarter 1Q23–2Q26 is **retrospective
reconstruction** of the predictor with expanding-window coefficient estimation; only the coefficient step is
pseudo-out-of-sample. **3Q26 is genuinely point-in-time**: review activity through dump − 14 days (1–17 Aug 2026,
`q3_2026_coverage.csv`), read produced 18 Sep, print 5 Nov.

*Could a real-time analyst have computed the same numbers?* Not the same numbers. WPK-A T1 (`WPK_reviews-index-2023-vintage.md`
§2.1) shows the same y/y read fresh vs stale differs by −10 pp within-vintage; the same-age construction removes the *bias*
only under a stationary attrition hazard across vintages, which two vintages cannot test. Vintages for a true real-time
series (Mar 2023–Jul 2025) are not on this machine.

*The current-quarter rule.* The two-month trim (`config.LAG_TRIM_MONTHS = 2`) applies to the **monthly index history** —
for the Aug 2026 files the last monthly value is June 2026. **3Q26 is not forecast from that series.** It uses E6's
daily partial window: 1 July to dump − k with k = 14 days from the posting-completeness curve (`E6_nowcast.pick_k`,
threshold 98.5%; `posting_completeness_curve.csv`), day-matched against the same window 364 days earlier, per region and
same-age across vintages (`vintage_matched_nowcast.csv`, period `3q26_to_date`); then the measured partial-to-full gap
(+0.09 pp, estimated on the single-file construction 2023–25, `q3_2026_nowcast.csv` `gap_source`); then the frozen mapping.
Observed: reviews for stays 1 Jul–~17 Aug. Forecast: the rest of the quarter via the +0.09 gap, and the mapping.

**Consequence.** Every walk-forward number carries "retrospective predictor". The 0.723 is evidence of *association on
the development sample*, not of real-time forecast skill. The engine's first real-time observation is 5 Nov.

### C. Units and populations

**Verdict: partly valid; mostly labelling, two time-varying biases.**

| object | what it is (verified) | mapping consequence |
|---|---|---|
| a review | one per completed reservation (Inside Airbnb `reviews.csv`: one row per review) — a **stay count**, not nights, not guests | reviews → nights needs length of stay; drift in LOS is a time-varying bias |
| Eurostat target | `tour_ce_omr`: **guest nights** at short-stay accommodation booked via Airbnb, Booking, Expedia, TripAdvisor, national, monthly (`data/manifests/expansion_source_manifest.csv`; `research/notes/2026-09-05_eu-platform-and-backlog.md`) | four platforms pooled (Airbnb share drift is a bias); guest-nights vs listing-nights (party size); national vs our city samples |
| Airbnb KPI | "sum of the total number of nights booked for stays and the total number of seats booked for experiences and services, net of cancellations and alterations that occurred in that period" (2Q26 10-Q, verified) | includes experience/service seats (small); booking-dated; listing-nights |

Party size and LOS: absorbed into the slope on average; a trend in either is a bias the mapping cannot see. Product mix
(experiences seats) is small. Review propensity: the Eurostat β < 1 partly reflects it; its drift is a bias.
"Instrument": in every document it means **measurement proxy**; no exclusion restriction is claimed or needed. Language
changed accordingly.

### D. Regional weights

**Verdict: partly valid.** Regional revenue is 10-Q revenue by geography (listing location) — revenue ≈ nights × ADR ×
take rate, so revenue ÷ ADR ∝ nights × take rate. Airbnb's fee structure is global, so cross-region take-rate differences
are second order (cross-currency fees are the known exception); the regional ADR index (NA 1.42 / EMEA 0.97 / LatAm 0.68 /
APAC 0.59) is the record's calibration in `research/notes/overnight/10_regional-and-segment-decomposition.md`, anchored to
the disclosed "NA ~30% of nights". These are **estimated proxies**, not disclosed night shares. Timing: the backtest
uses contemporaneous weights (look-ahead); the live 3Q26 read uses lagged + drift.

**AUDIT sensitivity (`audit/weights_sensitivity.csv`, pre-specified: report all four, choose none):**

| scheme | W1 | W2 | a | b | band | 3Q26 read |
|---|---:|---:|---:|---:|---:|---:|
| contemporaneous stay-mix (as run, v2.1) | 0.723 | 0.723 | 6.825 | 0.350 | 1.85 | 8.92 |
| **lagged stay-mix (live policy applied to history)** | 0.723 (n 10) | 0.723 | 6.675 | 0.363 | 1.84 | **8.85** |
| FY25 annual shares (v2) | 0.682 | 0.720 | 6.517 | 0.345 | 1.88 | 9.35 |
| equal weights | 0.760 | 0.770 | 6.342 | 0.314 | 2.04 | 9.72 |

The lagged policy — the only one available in real time — gives the same ratio and a read 0.07 lower. Equal weights fail
the line. The result is robust to the look-ahead; the record should nonetheless carry the lagged run as primary.

### E. What the balance-sheet evidence establishes

**Verdict: valid.** Separating the five claims:

1. *Payment timing changed* — **established.** GBV is "reflected in the quarter it occurs regardless of when payment is
   collected" (2Q26 10-Q, verified); unearned fees are recorded when cash is collected (FY25 10-K Note 2, as quoted in
   `final_nights.md` §6.1). The spread unearned-fees-minus-GBV y/y: +2.7 ± 2.95 pp over 1Q23–2Q25, then −4.1, −8.1, −18.8,
   −16.7 (`stage_e_rnpl_evidence.csv`; Welch t −4.04, p 0.021; ex-FX p 0.028). **AUDIT:** pre-period lag-1 autocorrelation
   −0.14 (little dependence); a block-position permutation places the post block as the most extreme of 11 positions
   (p = 1/11 = 0.09 — the permutation cannot go lower with 14 quarters). The parametric test is the best available and
   is indicative on n = 4.
2. *RNPL exposure* — **established by disclosure**: "over 20%" of GBV (2Q26), take-up ~70% (3Q25 call), international
   rollout Feb–Mar 2026 (ledger D001–D060).
3. *Pull-forward* — **not shown.** Nothing in our data separates pull-forward from new demand.
4. *Higher cancellations / weaker conversion* — **disclosed, not measured by us.** 2Q26 10-Q: "RNPL bookings … have
   experienced higher cancellation rates than historic bookings" (verified, official). 4Q25 call (mirror transcript,
   D018): "16% … going to 17% … within the cohorts that chooses that product … not hugely material". 1Q26 call (mirror,
   D035): "a very elevated level of cancellations … the net impact is positive." **Our stays residual does not detect it**
   (+0.49 mean, band 1.85, power 16% at 1 pp). **Correction:** the "~1 growth point of nights cost" attributed to RNPL in
   our documents is the Middle East conflict effect (1Q26 letter, D042). Removed.
5. *Consequences beyond expectations* — **assumed** (cohort engine grid, deferred short case, DEC-0020).

So the balance sheet corroborates a **payment-timing mechanism and exposure**, not a realised-demand shortfall. The
+0.49 vs 1.85 permits: "no detectable post-launch shift; any per-quarter divergence is inside ±1.85 pp (±2.5 at the
band's upper bound)". It does not permit "consistent with RNPL" as evidence — it is consistent with anything inside the
band, including zero. And the KPI subtracts a cancellation in the quarter it occurs; a cancelled booking is not
permanently in the metric.

### F. Forecasting evidence after selection

**Verdict: valid.** Facts (`stage_b_walkforward.csv`, `audit/f_h_checks.json`): W1 0.723 (n 14), W2 0.723 (n 10);
**W2 ⊂ W1, 10 shared quarters** — not two independent tests. Intervals [0.61, 1.08] / [0.58, 0.97]; DM p 0.22 / 0.26.
Prior-year 0.17 / 0.43; AR(1) 0.52 / 0.74. Acceleration: W1 1.56 (fails), W2 0.68. **W1 without 1Q23–2Q23: 0.838** —
the W1 pass depends on the 2023 deceleration where naive missed by 7.6. The evidence supports forecasting the **level**
of y/y growth on this sample, not changes or turning points, and nothing about guidance surprise.

*Chronology.* E5's 256-cell grid: 11 Sep 2026 (`docs/q3nowcast/SYNTHESIS.md`; commit "Q3 nowcast WS-E"), scored on
1Q23–2Q26. WPK-A re-vintaging: 14 Sep. v2 specified and frozen 18 Sep 15:57 with the neighbouring E5 cells' results
known and stated (0.754/0.682, 0.708/0.809); run 16:02 on the same 14 quarters. v2.1 (weights) specified after v2's
results, 18 Sep 18:34, same quarters. **No evaluation period is untouched.** "Declared before this run" is true;
"evaluated on data not used to develop the method" is false for every historical quarter. The "1/256 ≈ chance" line is
withdrawn — cells are correlated and it is not a false-discovery probability; the correct statement is that the grid
was exhausted and v2 is one declared construction scored on the same sample.

**Strongest honest claim today:** *on 1Q23–2Q26, a review-count index built without fitted survivorship corrections tracks
reported nights growth with ~28% lower walk-forward RMSE than naive, with an interval that includes 1.0; the quarters
were used to develop the method and the predictor is reconstructed from 2025–26 files.* **Smallest genuinely new
validation:** the 3Q26 print on 5 Nov against the dated 8.92 ± 1.85 read; then 4Q26 with the September/November dumps.

### G. Country-panel conclusions

**Verdict: partly valid.** First differences remove smooth shared trends, not common shocks. **AUDIT
(`audit/g_twoway_fe.json`):** adding month fixed effects (country + month) gives **β 0.313, se 0.069, t 4.5, wild-cluster
p 0.001** versus 0.494 with country effects only — 37% of the association was common EU-wide time variation; what remains
is cross-country co-movement within each month, still significant. The era split (|z| 0.17) is a non-rejection with two
periods of ~18 months, not proof of stability. Of the five exercises, A1 and A2 are significance tests of β = 0; A3, A4,
A5 are robustness and out-of-sample checks — "all five reject the null" is withdrawn. Transfer to global Airbnb realised
nights is **not** established by the panel (four platforms, national, guest-nights, EU only); the panel supports "review
counts read stays where stays are observed."

### H. Uncertainty

**Verdict: valid.** The 1.85 is the RMSE of six expanding-refit errors (W2, 1Q24–2Q25), while the post-launch residuals and
the 3Q26 read use the *frozen* mapping — related but not identical policies (`stages.run_stage_c`). It is an **error
scale**, not a prediction interval: no empirical coverage is known (n 6); bootstrap of the RMSE itself gives **[1.11,
2.46]** (`audit/f_h_checks.json`); parameter uncertainty (2 coefficients on 10 points) and the partial-quarter term
(`gap_sd_pp` in `q3_2026_nowcast.csv`) are not in it; pre-launch errors are mildly positive-biased (+0.44 mean). Safe to
pass into a probabilistic model: a point (8.92) with an error scale of ~2 pp treated as an *uncalibrated* sd, inflated for
parameter and partial-quarter uncertainty (≈ ×1.2), for a **one-quarter nowcast only**. Not for multi-quarter horizons,
and not as a calibrated distribution.

### I. Investment-relevant disagreement with the Street

**Verdict: partly valid.** The chain: review signal (implemented) → nights read (implemented, dated 18 Sep) → the
mechanism base 146.8m (main session, DEC-0029) and revenue (kernel / guide-plus-cushion lanes) → Street nights 149.0m
(Bloomberg MODL 12 Sep, DEC-0005) and 134.0m (4Q26) → consequences (memo). Dates match within a week (12 vs 18 Sep;
our data through 17 Aug). Units match (nights, quarter). **No dated historical nights consensus exists in the record**
(`03_current_consensus.csv` and the DoltHub history carry revenue/EBITDA/EPS), so beating naive cannot be turned into
"beats consensus" for any past quarter; guidance-surprise accuracy is untested (nights guidance is qualitative). Under a
benign RNPL scenario (deferral, no conversion change) the base path is unchanged — it carries the filed laps and no drag
— and the short case (DEC-0020, deferred) is what fails; the deceleration in the base is the laps' arithmetic, not a
conversion forecast. Double counting: the record's rule stands (`final_nights.md` §4.4: drag is not in the base); the
revenue and working-capital treatment of RNPL is the main session's and was not re-audited here.

---

## Reproduction and audit results

| check | run | result |
|---|---|---|
| engine re-run, `run.py --stage all` | yes, 18 Sep | verdicts A PASS / B PASS / C FAIL unchanged; 9 tests green |
| scorer reproduces E5's 0.683209 | yes (`tests/test_scoring.py`) | pass |
| lagged-weight backtest (live policy on history) | AUDIT | W1 0.723 (n 10), W2 0.723, read 8.85 |
| FY25 / equal weights | AUDIT | 0.682/0.720 read 9.35; 0.760/0.770 read 9.72 |
| W1 ∩ W2 overlap; W1 ex-2023 | AUDIT | 10 quarters; 0.838 |
| band bootstrap (n 6) | AUDIT | [1.11, 2.46] |
| C1 power | AUDIT | 6% / 16% / 32% / 53% at 0.5 / 1 / 1.5 / 2 pp |
| two-way FE panel | AUDIT | β 0.313, t 4.5, wild p 0.001 |
| UF−GBV dependence / permutation | AUDIT | lag-1 ρ −0.14; block permutation p 0.09 (floor 1/11) |
| 10-Q KPI definition, RNPL cancellation sentence, GBV timing | verified in `data/raw/regulatory/quantification/abnb_2026q2_10q.html` | quoted above |
| 16→17% and "net impact positive" | ledger D018, D035 — **mirror transcripts**, not official | quoted above |
| "~1 growth point" | ledger D042 — Middle East conflict, 1Q26 letter | misattribution, corrected |
| Eurostat variable | `tour_ce_omr`, guest nights, 4 platforms | verified in manifests |
| snapshot publication lag | `cdn_probe_reviews.csv` | median 18 days |
| 3Q26 window end | `q3_2026_coverage.csv`, `E6_nowcast.pick_k` | dump − 14 days, k at 98.5% completeness |
| unearned-fees accounting (FY25 10-K Note 2) | quoted in `final_nights.md` §6.1; not re-extracted here | not independently verified in this response |
| point-in-time backtest of the predictor | **cannot be constructed**: 2023–25 vintages absent | stated |

Availability table: `audit/availability_table.csv`.

---

## Revised pitch language (current → defensible)

**Part 1 — plain English**
- "Count the reviews and you are counting trips that were taken" → keep; add "in about 120 cities, which is not Airbnb's whole map."
- "A booking that is later cancelled is in the first number and never in the second" → "A booking counts when it is made; if it is cancelled, Airbnb subtracts it in the quarter it is cancelled. A review only exists if the stay happens."
- "Our misses are about 28% smaller … on both test windows" → "…on the 2023–26 quarters we used to build it, reading the review files as they exist today; the first forecast made before the fact is for the quarter Airbnb reports on 5 November."
- "the reported number has run above real stays since the pay-later option launched, in the direction expected, but by less than our error bar" → "since the option launched we cannot see a difference between reported and review-implied growth larger than our error bar; Airbnb itself reports higher cancellation rates on those bookings; how much that costs is our assumption, not our measurement."

**Part 2 — technical**
- "Stays-implied y/y" → "review-implied reported-night growth (pre-launch relation)".
- "the gap is the option term I, observed" → "the post-launch residual of the frozen mapping; interpretable as I only under stable lead time, LOS, propensity and mix."
- Add to 2.3: "Predictor values for all scored quarters are reconstructed from the Aug 2025 / Aug 2026 files; the backtest is retrospective in the predictor and expanding-window in the coefficients. Regional weights in the backtest are contemporaneous; the lagged policy gives 0.723 / 0.723 (audit)."
- Add to 2.4: "With month fixed effects β = 0.31 (audit)."
- "instrument" → "measurement proxy" throughout.

**Part 3 — significance**
- "Verdict: rejected at any conventional level, on all five" → "A1 and A2 reject β = 0 at p 0.001 (0.49 with country effects; 0.31 with country and month effects); A3–A5 are robustness and out-of-sample checks, all consistent."
- "the first construction in the team's record to do so, out of 256 cells" → keep the fact; delete "≈ chance"; add "W2 is nested in W1 (10 shared quarters); W1 without 1Q23–2Q23 is 0.838."
- 3.3 title "Claim: printed nights have run above stays since the option launched" → "Bound: post-launch residuals are inside ±1.85 pp; the pre-registered line had 16% power against a 1 pp effect."
- 3.4 → "the balance sheet establishes payment deferral and RNPL exposure (p 0.02 on n 4 vs 10; permutation floor 0.09); conversion deterioration is disclosed by management ('higher cancellation rates'), assumed in size by the team, and not measured by this engine."
- Every "±1.85" → "±1.85 (error scale; its own 90% range 1.1–2.5)".

---

## Prioritised next actions

**Blocking before the model is presented as a forecasting edge**
1. Put the lagged-weight run on the record as primary (`config`/`mix`: weights for t from t−4 + drift), re-freeze the
   note's §2 numbers with a dated line. Output: `stage_b_walkforward.csv` under the lagged policy; §5 table updated.
2. Relabel throughout (A, C, G language above); rebuild the landing table on gross cohorts (x × RNPL bookings with x =
   16–17% disclosed, B from the disclosed share) or remove it. Output: `final_model_landing.csv` v2 or its deletion noted.
3. Score 5 Nov: the 3Q26 print against 8.92 ± 1.85, written up as the first point-in-time observation. Output: one row in a
   new `live_scoring.csv` with the read's date, the print, the miss.

**Important, not invalidating the narrower use**
4. Re-read 2Q26 and 3Q26 from the September/November dumps; report the change in the residual. Output: updated
   `stage_c_gap.csv` with vintage stamps.
5. Real-time reconstruction for 1Q23 from the 2023 vintage (`q3nowcast_v2/E`, 114 markets) vs the retrospective value:
   one number on how much a fresh read differs. Output: `audit/realtime_1q23.csv`.
6. Uncertainty: report the band's interval and an inflated sd for the probabilistic model; no distribution engine.

**Optional**
7. Booking-side scoring of the Bloomberg/Similarweb QTD paths on the same yardstick (12 closed quarters), then the two
   sides of the identity on one chart — as corroboration with its own band.
8. Per-region mappings when the disclosed buckets give ≥ 12 quarters per region.

---

## Reply to the reviewer

Thank you for the review. We investigated each point against the code, the output files and the primary filings rather
than the methods note alone. Here is what we found, what we concede, and what changed.

**A — estimand.** Correct. The mapping is fitted on reported, booking-dated nights growth; its fitted value is
review-implied *reported*-night growth under the pre-launch relation, and there is no independent calibration to realised
Airbnb stays. The Eurostat panel shows review counts co-move with observed platform guest-nights; it does not calibrate
the Airbnb mapping. The residual identifies a booking-vs-stay divergence only if lead time, length of stay, review
propensity, mix and model form are stable, and cannot distinguish RNPL from those. The lead-time kernel is not in the
operational estimate. We have relabelled accordingly and retained the predictor as what it is: a review-based predictor
of reported growth with a measured error scale.

**B — availability.** Correct, and the most important point. Every historical predictor value is reconstructed from the
August 2025 and August 2026 files (published ~18 days after their dump dates, downloaded 11 Sep 2026); regional weights
in the backtest use the same quarter's 10-Q revenue; the ADR index and drift rule are from a 2026 note. The evaluation is
a retrospective reconstruction of the predictor with expanding-window coefficients, not a point-in-time backtest, and a
fully point-in-time version cannot be built from the vintages we hold. The current quarter is different: the two-month
trim applies to the monthly history; 3Q26 uses a daily window from 1 July to each dump minus 14 days (activity through
about 17 August), day-matched against the same window a year earlier, plus a measured partial-to-full adjustment. That
read (8.92% ± 1.85, produced 18 Sep) is the first genuinely point-in-time observation and is scored on 5 November. An
availability table by quarter is attached.

**C — units.** Reviews are per reservation; Eurostat `tour_ce_omr` is guest-nights across four platforms at national
level; Airbnb's KPI is booking-dated nights plus experience/service seats, net of cancellations in the period. Party
size, length of stay and propensity are absorbed on average and are time-varying biases if they trend. "Instrument" meant
measurement proxy; we now say so.

**D — weights.** Revenue ÷ ADR is nights × take rate; with a global fee structure the take-rate term is second order, and
the shares are estimated proxies, not disclosures. The backtest used contemporaneous weights — a look-ahead. Re-running
with the lagged policy that is available in real time gives the same walk-forward ratios (0.723 / 0.723) and a read 0.07
lower; equal weights fail the line (0.76 / 0.77); FY25 annual shares give 0.68 / 0.72. All four are reported; the lagged
run will become the primary.

**E — balance sheet.** Correct. The unearned-fees divergence (Welch p 0.02 on n 4 vs 10; a position permutation can only
reach 0.09) establishes payment deferral and RNPL exposure, not conversion deterioration. Management's own words are
"higher cancellation rates than historic bookings" (2Q26 10-Q) and "net impact is positive" (1Q26 call). Our residual
does not detect a shift (+0.49 pp against a 1.85 error scale; the pre-registered line had 16% power against 1 pp), so it
permits only a bound, not "consistent with RNPL." One error of ours: the "~1 growth point" of nights cost was the Middle
East conflict, not RNPL; removed. And the KPI subtracts a cancellation in the quarter it occurs — our plain-English
sentence implied otherwise and is corrected. The size of any RNPL conversion effect in our pitch is a team assumption
anchored on those disclosures, and it is now labelled as such.

**F — selection.** W2 is nested in W1 (10 shared quarters); W1 without 1Q23–2Q23 is 0.838; the acceleration target fails on
W1; no evaluation period was untouched — the 256-cell grid ran on 11 Sep, v2 was declared on 18 Sep knowing its
neighbours' results and scored on the same quarters, v2.1 after seeing v2. "1 in 256 ≈ chance" is withdrawn. The
defensible claim is association on the development sample with a 28% lower RMSE and an interval that includes 1.0; the
smallest new validation is the 5 November print.

**G — panel.** Partly correct. First differences do not remove common shocks; with month fixed effects added, β falls
from 0.49 to 0.31 and stays significant (wild-cluster p 0.001). The era split is a non-rejection, not stability. Only
two of the five exercises test β = 0; the others are robustness checks, and the summary line is corrected. Transfer to
global Airbnb realised nights is not established by the panel.

**H — uncertainty.** The 1.85 is an error scale from six expanding-refit errors, not a prediction interval; its own
bootstrap range is 1.1–2.5; parameter and partial-quarter uncertainty are not in it; it applies to a one-quarter nowcast
only. We pass it to the probabilistic model as an uncalibrated sd, inflated, and not for longer horizons.

**I — Street.** Our 3Q26 read (18 Sep, data through 17 Aug) and the Bloomberg consensus (12 Sep) are matched in date and
unit. No dated historical nights consensus exists in our record, so "beats naive" cannot be converted into "beats
consensus" for past quarters, and guidance-surprise accuracy is untested. Under a benign RNPL scenario the base path is
unchanged (it carries the filed laps and no cancellation drag); it is the deferred short case that would fail.

**What changed:** labels (review-implied reported growth; measurement proxy; bound not test), the availability
classification and table, the lagged-weight sensitivity, the two-way-FE result, the corrected "~1 growth point" and
cancellation sentences, and a clear separation in the pitch between what the engine measures and what the team assumes
about RNPL.
