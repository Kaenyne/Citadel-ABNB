# Workstream 02: definitive quarterly KPI panel and full guidance ledger

- **Date:** 2026-09-06. **Author:** Krishang Surapaneni (compiled with Claude Code), overnight run workstream 02.
- **Sources:** 23 shareholder letters `data/raw/letters/*.htm` (8-K Ex. 99.1, 4Q20-2Q26), XBRL `data/raw/xbrl/ABNB_companyfacts.json`, IR transcripts `data/raw/regulatory/transcripts/`, existing processed CSVs, Theo's `theos-past-research/research/guidance/`.
- **Scripts (rebuild everything):** `analysis/src/overnight/02_kpi_panel.py`, `02_guidance_ledger.py`, `02_guidance_analysis.py` (`py -3.13`).

## Bottom line

1. **Airbnb's quarterly revenue range is a floor dressed as a forecast.** 15 of 19 prints finished *above the top* of the range; none finished below the bottom. Mean beat vs midpoint +2.54%, median +2.52%. Over the last eight prints the cushion is +1.86% mean / +1.79% median, and the range itself has tightened from 4.9% of the midpoint (2021-22) to 1.9% (2024-26). **The company sandbags less than it used to, but it still sandbags.**
2. **How far out management guides has changed twice.** 4Q20-2Q21 was pure prose (zero numeric guides). 3Q21 introduced the revenue $ range and the horizon collapsed to one quarter. 4Q22 added the take-rate guide and the ex-FX revenue range. 4Q23 turned the full-year margin statement into a hard floor ("at least 35%") reiterated every quarter. 4Q25 added the **first ever full-year revenue growth guide**. Numeric guides per print went 0-1 (2020-21) → 8-10 (2024-26).
3. **The full-year guide has only ever been raised, never cut.** FY24 margin 35% floor → 35.5% point (3Q24). FY25 34.5% floor → ~35% (3Q25). FY26 revenue growth "at least low double digits" (4Q25) → "low to mid teens" (1Q26) → "at least mid teens" (2Q26); FY26 margin "stable" → "at least 35%" → "at least 35.5%".
4. **None of it explains the stock.** Across 17 regressions, neither the revenue beat, the raw next-quarter guide, the cushion-aware guide surprise, the FY guide action, nor the margin-guide direction produces a positive leave-one-out R² against day-1 excess return. The best in-sample fit (day-20 vs cushion-aware guide surprise, R² 0.166, t 1.61) still has LOO R² -0.135. This **confirms and extends** the predictive study's "no print-day alpha from beat-vs-guide" and adds that the *guide* has no more information than the beat.
5. **For 5 Nov:** the 3Q26 guide midpoint is $4,730m. Applying the trailing-8-print cushion gives a cushion-adjusted expectation of **$4.82bn (+17.6% y/y)**, and the full-history cushion gives $4.85bn (+18.4%) — against a guided 15-17%. Nights guided "low double digit" (10-12%); bucketed nights guides have been beaten by 2-5 points every time. A guide that *doesn't* look like this is the signal.

## Part A. The KPI panel

`data/processed/overnight/02_kpi_panel_quarterly.csv` — 24 rows (3Q20-2Q26) × 119 columns.
`data/processed/overnight/02_kpi_panel_long.csv` — 1,050 rows, one per (quarter, metric), each with a verbatim source quote or a `file:column` citation. Of these, 342 carry a verbatim letter quote and **all 342 re-verify against the letter HTML at run time** (`source_verified` column; 0 failures); the rest cite a processed CSV column or XBRL concept.
`data/processed/overnight/02_crosscheck.csv` — empty: driver history, the older KPI study, Theo's `quarterly_actuals.csv` and XBRL agree on revenue, nights, GBV, ADR, adj. EBITDA, CFO and diluted shares to within tolerance in every quarter. No restatements found in the reported series.

Coverage of what the brief asked for:

| group | columns | span |
|---|---|---|
| Headline | nights, GBV, ADR, revenue, revenue y/y reported + ex-FX, GBV y/y reported + ex-FX, ADR ex-FX, take rate | 3Q20-2Q26 |
| P&L / cash | net income + margin, adj. EBITDA + margin, FCF + margin, SBC + % revenue, tax, operating income, restructuring, CFO, capex | 4Q20-2Q26 |
| Cost lines | cost of revenue, ops & support, product dev, S&M, G&A — GAAP $, % of revenue, and the ex-SBC cash stack ($, % rev, per night) | 1Q20-2Q26 |
| Balance sheet | cash, ST investments, restricted cash, cash+ST, unearned fees, funds held for clients, LT debt, buybacks, diluted and basic WA shares, RSU tax withholding | 4Q20-2Q26 |
| Narrative KPIs | regional nights growth (exact % or bucket midpoint), regional ADR, cross-border share and growth, urban/non-urban share and growth, long-term-stay share, active listings level/growth, app share and app nights growth, first-time bookers, guest arrivals, buyback authorisations, removed listings, bedroom nights, single fee rate, cross-currency share of GBV, marketing commentary | as disclosed |

Growth buckets ("mid-single digit") are stored as the bucket midpoint with `unit = "pct (bucket midpoint)"` and the bucket named in `note` — do not treat them as measured numbers.

### Disclosure starts, stops and redefinitions

`data/processed/overnight/02_disclosure_changes.csv` (23 items). The ones that matter for a model:

| item | when | what happened |
|---|---|---|
| Nights and Experiences Booked → **Nights and Seats Booked** | 2Q25 | rename with the Services/Experiences relaunch; series continuous, no restatement |
| **Cross-border share and growth** | last given 1Q24 | ran 1Q21-1Q24 (20%→46% of gross nights); dropped from 2Q24 |
| **High-density urban share** | last given 4Q23 | ran 1Q21-4Q23; 1Q24 gave non-urban growth only; dropped after |
| **Long-term stays (28+) share** | last given 1Q24 | ran 1Q21-1Q24 (24%→17%); replaced by "short-term outpaced long-term" prose |
| **Active listings growth %** | last given 1Q24 | exact % 3Q22-1Q24 (15-19%); then only "over 8 million"; from 1Q25 only "in line with nights" |
| **Regional nights growth, exact %** | last given 3Q24 | from 4Q24 replaced by buckets ("mid-single digit") for all four regions |
| Regional ADR y/y | started 2Q23 | NA/EMEA from 2Q23; all four regions with ex-FX from 1Q25 |
| App share of nights / app nights growth | started 3Q23 / 1Q24 | 48%→64% of nights; app nights +17-23% every quarter |
| First-time booker growth (global %) | started 4Q25 | 8%, 10%, 11% |
| **Bedroom Nights Booked** | started 2Q26 | new metric, nights × bedroom count, +12% vs nights +10% |
| China domestic listings removed | 3Q22 | supply growth quoted ex-China from 4Q22 |
| Take-rate guide | started 4Q22 | "implied take rate" guided every quarter since |
| FY margin floor / FY revenue growth guide | started 4Q23 / 4Q25 | see Part B |

The disclosure trend is one-way: **the company has stopped giving the mix metrics (cross-border, urban, long-term stays, listings growth) exactly as they turned less flattering, and replaced exact regional growth with buckets.** Any model that needs those series has 2024 as its last hard data point.

## Part B. The guidance ledger

`data/processed/overnight/02_guidance_ledger.csv` — **194 guidance statements** across 23 prints (Theo's file had 100). Companion files: `02_guidance_coverage.csv` (guides per print × metric, max horizon), `02_fy_guide_revisions.csv` (the path of each full-year guide through its year).

Every row carries: print quarter and date, target period, horizon in quarters, metric, guide type, value low/high/mid, unit, comparator, **actual**, outcome, distance from midpoint (absolute and %), cushion, whether a later print revised it, a ≤150-char verbatim quote, the source file, and `verified` (all 194 quotes re-verify against the letter or transcript text).

Guide types: 46 ranges, 39 floors ("at least X"), 26 points ("approximately X"), 15 ceilings ("down slightly vs last year's X"), 10 buckets ("mid-single digit"), 48 directional, 10 qualitative. 159 are scoreable; 16 are pending (3Q26 and FY26); 13 are not scoreable because the company never reports the metric (the $200-250m new-business investment, FY21 capex) or the guide is prose.

Metrics covered: revenue $, revenue growth reported and ex-FX, nights level and growth, GBV level and growth, ADR level and growth, take rate (y/y and sequential), adj. EBITDA $ and margin (quarter and FY), S&M as % of revenue and S&M growth vs revenue growth, FCF margin vs EBITDA margin, SBC growth, effective tax rate, capex, new-business investment $, plus the FX commentary embedded in each revenue guide.

## Part C. What the ledger says

### 1. How far out management guides, and how that changed

| era | prints | numeric guides/print | longest horizon | character |
|---|---|---|---|---|
| 4Q20-2Q21 | 3 | 0 | 4q (FY21 prose) | "we are not providing an outlook"; nights/GBV comps called "volatile and unreliable" |
| 3Q21-3Q22 | 5 | 1-5 | 1-4q | revenue $ range appears (3Q21); FY22 margin only as "directionally in-line" |
| 4Q22-3Q23 | 4 | 6-8 | 1-4q | take rate, ex-FX revenue range, S&M bps, FY margin as a soft point |
| 4Q23-3Q25 | 8 | 7-9 | 2-5q | **FY margin becomes a hard floor** reiterated all year; FCF margin, SBC, tax added |
| 4Q25-2Q26 | 3 | 8-10 | 3-4q | **first FY revenue-growth guide**; GBV and nights guided as buckets every quarter |

Two-quarter-ahead guides exist but are rare and unreliable: 1Q24 promised 3Q24 revenue growth would accelerate vs 2Q24 (it did not: +10.6% → +9.9%); 3Q24 warned 1Q25 growth would decelerate (it did); 2Q25 pre-guided a 4Q25 margin decline (it happened).

### 2. Accuracy by guide type

n = 159 scored guides. Full table in `02_guidance_accuracy.csv`.

| guide type | n | hit / met | beat | miss | mean distance from midpoint |
|---|---|---|---|---|---|
| range | 39 | 11 within | 28 above | 0 below | +11.7% of midpoint |
| bucket | 5 | 0 in bucket | 5 above | 0 | +4.4 pts |
| floor ("at least") | 36 | 35 met | — | 1 | +4.4 pts of cushion |
| ceiling ("down slightly") | 14 | 12 met | — | 2 | −0.95 pts |
| point ("approximately") | 22 | 3 at point | 14 beat | 5 miss | +12.1% |
| directional | 43 | 35 met | — | 7 | — |

**Revenue $ range, the cleanest series (n = 19, 4Q21-2Q26 targets):**

| year of print | n | within | above | mean beat vs midpoint |
|---|---|---|---|---|
| 2021 | 2 | 0 | 2 | +5.60% |
| 2022 | 4 | 2 | 2 | +2.07% |
| 2023 | 4 | 1 | 3 | +3.14% |
| 2024 | 4 | 0 | 4 | +1.48% |
| 2025 | 4 | 1 | 3 | +2.32% |
| 2026 | 1 | 0 | 1 | +1.06% |

Smallest beat +0.86% (3Q24 target), largest +6.76% (4Q21 target). Actual exceeded the *top* of the range 15/19 times, by a mean of +1.06%. **Cushion trend:** +3.04% mean over the first 11 prints, +1.86% over the last 8. The range width fell from 4.9% to 1.9% of the midpoint over the same span, so the guide is genuinely tighter *and* less padded — but the sign has never flipped.

**Nights:** 14 directional guides, 13 met. The 2 bucketed nights guides were both beaten — 3Q25 guided "mid-single digit" for 4Q25 and delivered +9.8% (a ~5 point beat), 4Q25 guided "high-single digit" for 1Q26 and delivered +9.2%.

**ADR:** 8 "up" floors, 8 met. 2 misses, both in 2023, both the same error — "slightly lower ADR" guided, +0.2% and +1.4% delivered. ADR guides go wrong when FX moves after the guide is set, which is the mechanism the predictive study already documents (FX→ADR r −0.95).

**Margin:** every full-year floor cleared — FY24 35.0% floor → 36.4% actual (+140bps), FY25 34.5% floor → 35.1% (+60bps), and the 3Q25 "approximately 35%" landed at 35.1%. 10 next-quarter margin *ceilings* ("margin down y/y"), 9 met; the exception is 1Q25, which guided 2Q25 margin "flat to down slightly" and delivered +1.2 points.

**Directional guides that were wrong (7):**

| print | target | guide | outcome |
|---|---|---|---|
| 2Q22 | 3Q22 | margin "at or slightly below last year's 49%" | 50.5% — beaten upward |
| 4Q22 | 1Q23 | "slightly lower ADR" | +0.2% y/y |
| 1Q23 | 2Q23 | "slightly lower ADR" | +1.4% y/y |
| 1Q24 | 3Q24 | revenue growth "to accelerate vs Q2" | decelerated 10.6% → 9.9% |
| 1Q25 | 2Q25 | margin "flat to down slightly" | +1.2 pts |
| 4Q25 | 1Q26 | take rate "up slightly y/y" | −0.10 pts |
| 1Q26 | 2Q26 | nights growth "to slightly decelerate" | accelerated 9.1% → 10.3% |

Five of the seven are wrong in the *company's favour*. The two that aren't (the take-rate guide and the 3Q24 acceleration promise) are the only cases in six years where a guide over-promised.

**Point guides that miss are all expense lines:** FY24 SBC guided "+20%" (1Q24) then "+25%" (3Q24), delivered +30.8%; FY24 tax guided "mid-to-high teens" then "approximately 20%", delivered 20.5%; 1Q23 S&M guided "+150bps as a % of revenue", delivered +190bps.

### 3. Full-year guide revisions through the year

`02_fy_guide_revisions.csv`. Every FY guide path, in order:

- **FY22 margin:** 4Q21 "directionally in-line with 2021" → 1Q22 "modest expansion" → 2Q22 "expansion" → actual +8.0 pts (26.6% → 34.6%). Massively conservative.
- **FY23 margin:** 4Q22 "maintain 2022" → 1Q23 "broadly in-line" → 2Q23 "modestly higher" → 3Q23 "approximately 150 bps higher" → actual +2.3 pts. Ratcheted up three times.
- **FY24 margin:** 4Q23 / 1Q24 / 2Q24 "at least 35%" → 3Q24 "approximately 35.5%" → actual 36.4%. One raise, at the Q3 print.
- **FY25 margin:** 4Q24 / 1Q25 / 2Q25 "at least 34.5%" → 3Q25 "approximately 35%" → actual 35.1%. Same pattern, same quarter.
- **FY26 margin:** 4Q25 "stable y/y" → 1Q26 "at least 35%" → 2Q26 "at least 35.5%". Two raises already, both earlier in the year than the 2024/2025 pattern.
- **FY26 revenue growth:** 4Q25 "at least low double digits" → 1Q26 "low to mid teens" → 2Q26 "at least mid teens". 1H26 actual is +17.1%.
- **FY24 SBC:** 1Q24 "+20%" → 3Q24 "+25%" → actual +30.8%. The one guide raised *against* the company twice and still missed.

Pattern: **the FY margin guide is set as a floor in February, reiterated verbatim in May and August, and raised to a point estimate in November.** It has never been lowered.

### 4. Does the guide move the stock? No.

`02_guidance_reaction_tests.csv`, joined to `data/processed/abnb_earnings_reactions.csv`. Definitions, all point-in-time:

- `beat_pct` = reported revenue ÷ the guide midpoint set one print earlier − 1.
- `guide_vs_naive_pct` = next-quarter guide midpoint ÷ a seasonal-naive expectation (last year's same quarter grown at the y/y rate just printed) − 1.
- `cushion_aware_guide_surprise_pct` = the same, after grossing the guide up by the **walk-forward median cushion** estimated only from prints strictly before this one (≥4 prior observations required, so the series starts at the 3Q22 print, n = 15).

**17 tests run.** Every one has a negative leave-one-out R²; none beats predicting the sample mean.

| test | n | R² | LOO R² | LOO RMSE vs mean RMSE | t on the feature |
|---|---|---|---|---|---|
| day-1 ~ beat | 19 | 0.052 | −0.129 | 8.80 vs 8.28 | 0.97 |
| day-1 ~ raw guide vs naive | 20 | 0.020 | −0.121 | 9.12 vs 8.61 | 0.61 |
| day-1 ~ cushion-aware guide surprise | 15 | 0.011 | −0.293 | 8.87 vs 7.80 | 0.39 |
| day-1 ~ beat + cushion-aware guide | 15 | 0.156 | −0.272 | 8.80 vs 7.80 | 1.43 / 0.82 |
| day-1 ~ nights acceleration (benchmark) | 19 | 0.029 | −0.096 | 8.67 vs 8.28 | 0.72 |
| day-1 ~ FY guide raise/cut | 23 | 0.007 | −0.210 | 9.31 vs 8.47 | 0.38 |
| day-1 ~ next-Q margin guide direction | 17 | 0.000 | −0.225 | 9.87 vs 8.92 | 0.07 |
| day-1 ~ change in margin guide direction | 14 | 0.018 | −0.566 | 10.43 vs 8.34 | −0.47 |
| day-20 ~ FY guide raise/cut | 22 | 0.000 | −0.132 | 7.82 vs 7.36 | 0.06 |
| day-20 ~ change in margin guide direction | 13 | 0.071 | −0.288 | 8.67 vs 7.64 | 0.92 |
| day-20 ~ cushion-aware guide surprise | 15 | **0.166** | −0.135 | 7.88 vs 7.40 | 1.61 |

**The cushion-aware guide is not better than the raw guide, and neither is better than the beat.** The only thing in this whole exercise with a respectable sign hit rate is the nights-acceleration variable already owned by the predictive study:

| feature | dep | n | same sign | hit rate |
|---|---|---|---|---|
| nights acceleration | day-1 excess | 19 | 15 | **0.79** |
| cushion-aware guide surprise | day-1 excess | 15 | 8 | 0.53 |
| FY guide raise/cut | day-1 excess | 6 | 3 | 0.50 |
| next-Q margin guide direction | day-1 excess | 15 | 7 | 0.47 |
| revenue beat vs guide | day-1 excess | 19 | 7 | **0.37** |

The revenue beat's sign hit rate is *below* a coin flip: a bigger beat is, if anything, associated with a worse day-1 move. Consistent with the predictive study, and with the mechanism — everyone knows the guide is a floor, so beating it is priced in and the reaction is set by the volume trajectory.

Caveats: n is 13-23 everywhere; the FY-guide-action variable only has 6 non-zero observations; day-20 is missing for 2Q26. Nothing here would survive a multiple-testing correction, which is the point — it is a negative result.

Figure: `analysis/figures/overnight/02_guidance_cushion.png` (cushion history + the day-1 scatter).

### 5. Ranked guidance tells

`02_guidance_tells.csv`.

| # | tell | strength | how to use |
|---|---|---|---|
| 1 | The quarterly revenue range is a floor, not a forecast (15/19 above the top, 0 below the bottom) | very strong | model next-quarter revenue at midpoint × (1 + cushion) |
| 2 | The cushion has halved (3.0% → 1.9%) and the range has tightened (4.9% → 1.9% of midpoint) | moderate | use the trailing-8 cushion (~1.8%), not the full history |
| 3 | Bucketed nights and GBV guides are the most beatable line in the letter (5/5 above bucket) | strong | treat "mid-single digit nights" as a floor; 4Q25 beat it by ~5 pts |
| 4 | Every full-year margin floor has been cleared, by 60-140bps | strong | add 60-140bps to the FY margin floor in the base case |
| 5 | The guides that miss are the expense/monetisation lines: SBC (+20%/+25% guided, +30.8% actual), tax, take rate | moderate | haircut SBC and tax guides; treat take-rate guides as directional only |
| 6 | The FY guide is only ever raised, and (2024, 2025) the raise lands at the Q3 print | strong | assume an FY26 raise on 5 Nov unless the quarter itself misses |
| 7 | ADR direction calls go wrong when FX moves after the guide is set (2 of 17) | moderate | model ADR from the FX basket, not from the guide's ADR sentence |
| 8 | Nothing about the guide predicts the stock reaction | very strong (negative) | do not build a trade around the guide; nights acceleration is the reaction variable |

## Corrections to existing work

- No numeric errors found. `02_crosscheck.csv` is empty: the driver history, the KPI study, Theo's `quarterly_actuals.csv` and XBRL agree on every cell tested.
- Theo's `guidance_items.csv` (100 rows) is correct as far as it goes, but it covers only revenue $, adj. EBITDA margin, and directional nights/ADR/GBV/take-rate. It has **no** revenue-growth ranges, no ex-FX ranges, no numeric take-rate or S&M items, no bucketed nights/GBV guides, and no SBC / tax / FCF / capex / investment-spend guides. This ledger supersedes it for coverage; it does not contradict it.
- Two of Theo's `absolute_floor` rows (2021Q1 and 2021Q4 next-quarter margin, `value_low = 0.0`) encode "positive Adjusted EBITDA", not a 0% margin floor. Worth a comment in his schema.
- The FY2024 tax row here is scored against the 4Q23 sentence "we expect our effective tax rate to approximate the mid-to-high teens **in the near-term**", which is not strictly an FY24 guide. It is flagged in the row's `note`; treat it as indicative.
- 2Q26 letter HTML contains OCR-style artefacts in the filed text ("ee ff ctive", "die ff rence"). Quotes in the ledger reproduce the filed text verbatim so they verify; do not "fix" them.

## For the model

| parameter | value | unit | source |
|---|---|---|---|
| Revenue guide cushion, trailing 8 prints (median) | +1.79 | % above guide midpoint | `02_guidance_cushion_series.csv` |
| Revenue guide cushion, full history (median) | +2.52 | % above guide midpoint | same, n = 19 |
| Revenue guide cushion, 25th-75th pct (last 8) | +0.95 to +2.63 | % | same |
| Probability actual lands above the top of the range | 15/19 = 0.79 | — | `02_guidance_ledger.csv` |
| FY adj. EBITDA margin cushion over the stated floor | +60 to +140 | bps | FY24 +140, FY25 +60 |
| Nights bucket-guide beat | +3 to +5 | pts above the bucket midpoint | 4Q25 +4.8, 1Q26 +1.2 |
| FY26 effective tax rate | 17-19 (guide), 20.0 actual FY25 | % | 1Q26 and 2Q26 letters; panel |
| FCF margin premium over adj. EBITDA margin | +4.0 (FY24), +2.6 (FY25) | pts | panel; guided "several points" |
| SBC growth guide reliability | guide understates by 6-11 pts | pts | FY24 +20%/+25% guided vs +30.8% actual |
| Take rate, quarterly seasonal path | 9.2 / 13.2 / 17.9 / 13.6 (2025) | % of GBV | panel `take_rate_pct` |
| 1H26 revenue growth | +17.1 | % y/y | panel |
| 1H26 adj. EBITDA margin | 28.32 (vs 27.20 in 1H25, +1.12 pts) | % | panel |

## For the 5 Nov card

The 2Q26 letter guides 3Q26 and FY26. What it says, and what history says it means:

| item | guide | cushion-adjusted expectation |
|---|---|---|
| 3Q26 revenue | $4.69-4.77bn, +15-17% y/y, ~3pt FX tailwind after hedging | **$4.82bn (+17.6%)** on the trailing-8 cushion; $4.85bn (+18.4%) on the full-history cushion; 25th-75th band $4.78-4.85bn (`02_q3_2026_guide_card.csv`) |
| 3Q26 nights | "low double-digit" (10-12%) | 12-15%, i.e. 150-154m nights (3Q25 base 133.6m) |
| 3Q26 GBV | "mid teens" (14-16%) | 16-19%, i.e. $26.6-27.2bn |
| 3Q26 take rate | "relatively in-line y/y" | 17.9% ± 0.2pt; the one guide type that has actually missed |
| 3Q26 adj. EBITDA margin | "down slightly vs Q3 2025" (50.1%) | 48.7-50.0%; 9 of 10 such ceilings were met, by a mean of 1.4 pts |
| FY26 revenue growth | "at least mid teens" (14-16%) | 1H26 already +17.1%; expect a raise to "high teens" or a point estimate at the Q3 print |
| FY26 adj. EBITDA margin | "at least 35.5%" | 36.1-36.9% on the FY24/FY25 cushion (+60 to +140bps) |
| FY26 tax rate | "high teens" (17-19%) | tax guides have run 50bps hot; use 19-20% |

**What a good Q4 guide looks like:** 4Q26 revenue range whose midpoint implies ≥+14% y/y (4Q25 base $2,778m → ≥$3.17bn), nights guided "low double digit" again, and the FY26 revenue-growth guide moved up a notch (to "high teens" or a point). Consistent with the pattern, the FY26 margin floor would be replaced by "approximately X%" with X ≥ 36%.

**What a bad Q4 guide looks like:** a 4Q26 revenue midpoint implying <+12% y/y, nights dropped back to "high-single digit", the FY26 revenue guide merely reiterated rather than raised (the first non-raise since the FY guide existed), or — the real red flag — a *take-rate down* guide alongside a margin ceiling, which would say monetisation and cost are moving the wrong way together.

**And the trading caveat:** none of this predicts the print-day move. On the evidence here (17 tests, all with negative LOO R²), the guide is for the model, not for the trade. If a print-day view is needed, use nights acceleration (0.79 sign hit rate, n = 19), not the beat (0.37).

## What to build next

1. Extend the ledger backwards is impossible (the 4Q20 letter is the first), but the **call transcripts add CFO guides the letters omit** — only two were found in a targeted grep (FY26 tax). A full pass over all 23 transcripts for "we expect / we anticipate" sentences with a number would likely add 20-40 rows.
2. There is no consensus series in this repo (`consensus_snapshots.csv` is empty). The single most valuable missing input is **sell-side consensus at the moment of each guide** — it would let us test guide-vs-consensus rather than guide-vs-naive, which is the version of the test the market actually trades.
3. The bucket→range map (`BUCKET` in `02_guidance_ledger.py`) is a judgement call. If someone has a source for how the sell side reads "low-20s" vs "high teens", swap it in; the nights and GBV outcomes are sensitive to it.
