# I. The three mix terms of ex-FX ADR, measured for 3Q26 to date

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Question:** can the geographic-mix, unit-size (party-size) and length-of-stay terms of ex-FX ADR be measured for the quarter in progress from the same reviews and calendar data that gave the nights read, rather than carried from trailing averages, and do the measured versions have any validated history?
- **Scripts:** `analysis/src/adrq3/I0_protocol.py` (note-08 walk-forward, copied from E5), `I1_party_size_daily.py` (review-text classifier per market x dump x review date, 245 dump files, 8 background shards), `I1b_party_size_windows.py`, `I2a_los_runs_dated.py` (blocked runs with start dates, 189 calendars, 3 workers), `I2b_los_windows.py`, `I3_geo_mix.py`, `I4_backtests.py`, `I5_summary.py`. All `py -3.13`, no network.
- **Outputs:** `data/processed/adrq3/I/` (listed in section 6). Summary for workstream J: `I_mix_terms_3q26.csv`.
- **Inputs, read-only:** main-tree reviews dumps (123 markets, Aug 2026 vintage plus each market's own Aug/Sep 2025 vintage where the CDN still had one, 120 of 123), main-tree calendars (34 markets, 2024-2026 vintages), `04_regional_quarterly_wide.csv`, E_aug regional stays split, H's `adr_history_components.csv`, WS-C `C5_regional_split_forecast.csv`, 13/14a/14b/14c outputs, the pipeline's own classifier `analysis/src/abnb_party_size_reviews.py` (imported, not copied).
- **Does not redo:** the decomposition, the 14a discount ratios, the 0.59 elasticity, the E nights index, the FX estimators or the pricing residual (workstream J).

---

## 1. Bottom line

1. **Unit size (party size): +0.80 pp of ADR for 3Q26 to date, band +0.53 to +1.00, measured.** Booked capacity per reviewed stay is +1.35% y/y (log points) on the vintage-matched, day-matched window 1 Jul to 16 Aug 2026 (2026 dumps) against the same window 364 days earlier in each market's own 2025 dump, 119 markets, 2.05mm reviews, fixed-2019 weights; times the 0.592 elasticity. **It did not move:** 2Q26 on the identical construction is +1.46% / +0.87 pp, 3Q25 to date is +1.36% / +0.81 pp. NA +2.5% (+1.47 pp), EMEA +0.7%, APAC +1.6%, LatAm -0.1%, the same ordering as every quarter since 2024. Within-vintage and vintage-matched reads differ by 0.03 pp, so review survivorship does not touch this term.
2. **Length of stay: +0.06 pp, band -0.08 to +0.29, measured on blocked runs, not validated.** On the cleanest construction (stays starting 7 to 97 days after the vintage, occupancy-weighted, 24 to 30 markets ex NYC/LA) the 28+ share of blocked-run nights fell 1.7 pp y/y at the June vintages and 0.5 pp at the August vintages, giving +0.26 and +0.03 pp; on the calendar windows (1 Jul to 30 Sep, 1 to 30 Sep) it is flat, giving -0.08 pp. The H card carried +0.30 (assumed). **Versus 2Q26 there is no comparable read** (14b stops at 4Q25); against 14c's own five snapshots (occupancy-weighted 28+ share 17.4% Sep-25, 16.7, 16.8, 16.9, 15.5% Aug-26) the direction is the same and the size is smaller.
3. **Geographic mix: -1.43 pp, band -1.57 to -0.94, measured split, unvalidated mapping.** E's vintage-matched regional stays (NA +6.9, EMEA +0.9, LatAm +27.5, APAC +10.0, review-weighted) applied to the 3Q25 nights shares and anchored regional ADR levels through the 07/H arithmetic gives -1.43 pp (-1.57 with 2Q26 regional ex-FX ADR carried); the equal-weighted split gives -0.94. H carried -1.19 and WS-C -1.24; the 2025 actual was -1.58. The difference from H is one thing: E has EMEA near flat and LatAm near +28, WS-C has EMEA +6 and LatAm +20.
4. **The three terms together are +0.57 pp lower than the H card's +0.74, -1.19, +0.30 = -0.15: measured they sum to -0.57 (band -1.12 to +0.34).** Fed into J's card v2 (3 term rows read), 3Q26 ex-FX ADR moves from +3.88% to **+3.46%** (central band 2.13 to 4.78, was 2.48 to 5.28); reported at the midpoint FX estimator from +3.45% to **+3.03%**, $177.20 to **$176.47** (central $174.20 to $178.75; EUR fit +2.34% / $175.29, baskets +3.72% / $177.66). 4Q26 carries the same terms: +3.61% reported, $173.55. The walk-forward ratio is **unchanged at 0.994 (v2 persistence RMSE 0.903 vs naive 0.908, PASS)** because the backtest uses the realised quarter-t terms of history; the 3Q26 terms cannot move it, and nothing here claims it should.
5. **Evidence status, term by term.** Unit size: measured and reproducible (the refreshed Aug-2026 dumps reproduce 13's series on 12 overlapping quarters with r 0.97, RMSE 0.06 pp) but it is a level term with no timing information (r -0.17 against ex-FX ADR at lead 0, walk-forward ratio 4.2 vs naive: an OLS on a flat feature). Length of stay: measured but unvalidated (no quarterly history of the same construction; 14b's disclosure-based term has r -0.13 against ex-FX ADR, ratio 0.88 vs naive on 8 quarters, which is the term being small and smooth, not informative). Geographic mix: measured split, but the E-projected shares reproduce H's disclosed-share term only loosely (RMSE 0.41 to 0.69 pp, r 0.41 to 0.44, permutation p 0.21 to 0.25, n 10), and the term itself correlates with ex-FX ADR (r 0.68 to 0.78, p 0.005 to 0.04) without beating naive on the walk-forward (ratios 1.10 to 1.34, n 6). The correlation is the 2025 to 2026 co-movement of NA nights and NA pricing, which is one episode.
6. **What moved and what did not.** Nothing in the mix moved between 2Q26 and 3Q26 to date: party size is flat, long stays are still losing share at about the same pace, and the geographic drag is a little heavier than the card assumed because EMEA stays are flat while LatAm runs at +28. If the 5 Nov print's ex-FX ADR differs from 2Q26's +4%, it will be the pricing residual, not the mix.

---

## 2. Tables

### 2.1 The summary file (`I_mix_terms_3q26.csv`, measured rows)

| Term | 3Q26 to date value | Unit | ADR pp | lo | hi | Status |
|---|---|---|---|---|---|---|
| unit_size | +1.35 | booked capacity y/y, log %, fixed-2019 weights, 119 markets | **+0.80** | +0.53 | +1.00 | measured, level term |
| los_mix | -0.22 | d(28+ share of blocked-run nights), pp, median of 8 constructions | **+0.06** | -0.08 | +0.29 | measured on blocks, unvalidated |
| geo_mix | NA +6.9 / EMEA +0.9 / LatAm +27.5 / APAC +10.0 | regional stays y/y, E vintage-matched | **-1.43** | -1.57 | -0.94 | measured split, unvalidated mapping |
| sum | | | **-0.57** | -1.12 | +0.34 | H card: -0.15 (0.74 - 1.19 + 0.30) |

Bands: unit size = min/max over {vintage-matched, within-vintage} x {fixed-2019, equal, review weights} x {3Q26 to date, July only}, widened to the market bootstrap 5-95 and the listed-basis elasticity 0.577. LOS = min/max over {June pairs, August pairs} x {lead-matched, calendar window} x {occupancy-weighted, unweighted}. Geo = {review-weighted, equal-weighted split} x {regional ex-FX ADR zero, 2Q26 carried}.

### 2.2 Party size on the identical construction (global, fixed-2019 weights, elasticity 0.592)

| Window | Construction | Markets | Reviews | Capacity cur | Capacity prior | Capacity y/y % | bootstrap 5-95 | Composition index y/y % | Head-count y/y % | Size term pp |
|---|---|---|---|---|---|---|---|---|---|---|
| 3Q26 to date (1 Jul-16 Aug) | vintage-matched | 119 | 2,051,515 | 4.141 | 4.086 | +1.35 | 0.90 to 1.69 | +0.13 | +0.19 | **+0.80** |
| 3Q26 to date | within-vintage | 123 | 2,219,885 | 4.125 | 4.072 | +1.27 | 0.86 to 1.62 | +0.16 | +0.12 | +0.75 |
| July 2026 | vintage-matched | 119 | 1,694,431 | 4.135 | 4.077 | +1.40 | 0.92 to 1.74 | +0.10 | +0.30 | +0.83 |
| 2Q26 | vintage-matched | 119 | 4,612,105 | 4.020 | 3.961 | +1.46 | 1.00 to 1.89 | +0.53 | +0.30 | **+0.87** |
| 3Q25 to date (1 Jul-31 Aug 2025, 2025 dumps) | own vintage | 119 | 2,088,009 | 4.082 | 4.027 | +1.36 | 0.98 to 1.71 | +0.69 | +0.94 | **+0.81** |
| 3Q25 full | within-vintage | 123 | 4,413,818 | 3.991 | 3.938 | +1.33 | 0.96 to 1.68 | +0.57 | +0.73 | +0.79 |

By region, 3Q26 to date vintage-matched: NA +2.48% (+1.47 pp), EMEA +0.73% (+0.43), LatAm -0.07% (-0.04), APAC +1.58% (+0.93). 2Q26: NA +2.83, EMEA +0.74, LatAm +0.21, APAC +1.57.

The 13 note's stated fact that the composition index moves against capacity holds here too: the composition index is +0.1 in 3Q26 against +0.5 to +0.7 a year ago, while capacity is unchanged. Do not read the composition index as party size.

### 2.3 Length of stay: 28+ share of blocked-run nights, same stay window, same lead, global 10-K weights

| Vintage pair | Window | Weighting | Markets | 28+ share prior | 28+ share current | d 28+ pp | LOS mix pp |
|---|---|---|---|---|---|---|---|
| Jun-26 vs Jun/Jul-25 | lead-matched (7-97 d ahead) | occupancy | 24 | 11.8% | 10.2% | -1.7 | **+0.26** |
| Jun-26 vs Jun/Jul-25 | lead-matched | unweighted | 24 | 23.4% | 21.4% | -2.0 | +0.29 |
| Jun-26 vs Jun/Jul-25 | calendar 1 Jul-30 Sep | occupancy | 24 | 10.0% | 10.1% | +0.1 | -0.08 |
| Jun-26 vs Jun/Jul-25 | calendar 1 Jul-30 Sep | unweighted | 24 | 22.8% | 21.5% | -1.2 | +0.12 |
| Aug-26 vs Aug/Sep-25 | lead-matched | occupancy | 30 | 10.0% | 9.5% | -0.5 | **+0.03** |
| Aug-26 vs Aug/Sep-25 | lead-matched | unweighted | 30 | 21.7% | 20.9% | -0.8 | +0.08 |
| Aug-26 vs Aug/Sep-25 | calendar 1-30 Sep | occupancy | 30 | 7.0% | 7.4% | +0.4 | -0.07 |
| Aug-26 vs Aug/Sep-25 | calendar 1-30 Sep | unweighted | 30 | 23.0% | 22.6% | -0.4 | +0.03 |

Median of the eight: **+0.06 pp**; range -0.08 to +0.29. By region on the June lead-matched occupancy-weighted read: NA -1.8 pp of 28+ share (+0.23 pp), EMEA -1.8 (+0.35, Paris and Rome only), LatAm -1.4 (+0.14), APAC -1.4 (+0.20). The August calendar-September window is at 0 to 30 days' lead where near-term host blocks dominate and market-level 28+ shares swing by 5 to 10 pp (Buenos Aires, Singapore, Sunshine Coast, Mexico City up; London down 7.5 pp); it is in the band and not in the point. 2025 against 2024 exists for Austin, Nashville, Paris and Rome only, unweighted (2024 listings dumps carry no occupancy field): 28+ share -1.2 pp EMEA, -0.4 NA on the lead-matched window, consistent with 14b's -2 pp a year global drift once the block inflation is allowed for.

### 2.4 Geographic mix for 3Q26 by regional growth source (3Q25 shares NA 31.4, EMEA 36.8, LatAm 17.0, APAC 14.9; anchored ADR $249, $162, $97, $116)

| Growth source | NA | EMEA | LatAm | APAC | Geo mix pp, g = 0 | g = 2Q26 regional ex-FX | Label |
|---|---|---|---|---|---|---|---|
| E vintage-matched, review-weighted | +6.9 | +0.9 | +27.5 | +10.0 | **-1.43** | -1.57 | measured |
| E vintage-matched, equal-weighted | +5.7 | +0.2 | +21.7 | +4.3 | -0.94 | -1.02 | measured |
| E within-vintage, review-weighted | +29.4 | +20.2 | +52.3 | +29.1 | -1.14 | -1.25 | measured, survivor-biased levels, relative growth only |
| WS-C index model | +6.7 | +5.9 | +19.5 | +17.1 | -1.30 | -1.45 | modelled |
| WS-C persistence | +6.6 | +6.6 | +18.6 | +16.6 | -1.24 | -1.39 | modelled |
| WS10 base cells | +7.0 | +8.0 | +18.0 | +17.0 | -1.19 | -1.33 | modelled |
| 2Q26 letter buckets carried | +8.0 | +8.0 | +20.0 | +18.0 | -1.22 | -1.37 | assumed |

H card -1.19 (band -1.64 to -1.04); WS-C C5 -1.24; 2025 actual -1.58.

### 2.5 Backtests (note-08 protocol, `I4_backtest_scoreboard.csv`)

| Term | Feature | Target | n | r | perm p | WF n | RMSE | vs naive | vs prior yr | vs AR(1) | Knowable before print |
|---|---|---|---|---|---|---|---|---|---|---|---|
| unit size | 13 global size term, lead 0 | ex-FX ADR y/y | 20 | -0.17 | 0.45 | 10 | 3.79 | 4.17 | 2.17 | 4.02 | yes |
| unit size | same, lead 1 | ex-FX ADR y/y | 19 | 0.17 | 0.51 | 9 | 5.24 | 5.47 | 3.39 | 5.28 | no |
| unit size | 13 size term | H residual pricing | 14 | 0.46 | 0.14 | 6 | 1.23 | 1.84 | 0.74 | 1.14 | yes |
| LOS | H/14b los_mix_pp | ex-FX ADR y/y | 12 | -0.13 | 0.69 | 8 | 0.84 | 0.88 | 0.67 | 0.92 | no |
| geo | E vmatch review-wtd projected shares | H geo_mix (disclosed shares) | 10 | 0.43 | 0.21 | 6 | 0.36 | 1.59 | 0.63 | 1.57 | yes (RMSE vs H 0.69 pp, bias -0.40) |
| geo | E vmatch equal-wtd projected shares | H geo_mix | 10 | 0.41 | 0.25 | 6 | 0.36 | 1.59 | 0.63 | 1.56 | yes (RMSE vs H 0.42, bias +0.09) |
| geo | letter regional buckets | H geo_mix | 7 | 0.99 | 0.002 | 3 | 0.06 | 0.22 | 0.11 | 0.23 | yes; this is what 04's shares are built from, so it is a tautology |
| geo | E vmatch review-wtd term | ex-FX ADR y/y | 10 | 0.68 | 0.04 | 6 | 1.09 | 1.34 | 0.55 | 1.06 | yes |
| geo | E vmatch equal-wtd term | ex-FX ADR y/y | 10 | 0.77 | 0.01 | 6 | 0.90 | 1.10 | 0.45 | 0.87 | yes |
| geo | H geo_mix (disclosed) | ex-FX ADR y/y | 10 | 0.73 | 0.02 | 6 | 0.98 | 1.20 | 0.49 | 0.95 | no |
| all three | H geo + size + LOS | ex-FX ADR y/y | 14 | 0.52 | 0.05 | 6 | 1.13 | 1.38 | 0.56 | 1.03 | partial |

Series checks (`I4_party_size_series_check.csv`): H's unit_size_pp is 13's series exactly (max diff 0.000 pp); the refreshed Aug-2026 dumps reproduce it on 3Q23 to 2Q26 with mean difference -0.002 pp, RMSE 0.062 pp, r 0.97.

### 2.6 Card v2 before and after the measured terms (J3, midpoint FX; `data/processed/adrq3/J/adr_card_v2.csv`)

| | Geo | Size | LOS | Mix sum | Residual | ex-FX y/y | ex-FX band | Reported y/y | ADR $ | ADR $ band | GBV $bn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| before (H terms) | -1.19 | +0.74 | +0.30 | -0.15 | 4.61 | +3.88 | 2.48 to 5.28 | +3.45 | 177.20 | 174.81 to 179.60 | 26.01 |
| after (I terms) | -1.43 | +0.80 | +0.06 | -0.57 | 4.61 | **+3.46** | 2.13 to 4.78 | **+3.03** | **176.47** | 174.20 to 178.75 | 25.91 |

Reported by FX estimator, after: EUR fit +2.34% ($175.29), baskets +3.72% ($177.66). 4Q26 after: +3.61% midpoint, $173.55. Walk-forward, before and after: v2 persistence RMSE 0.903 vs naive 0.908, ratio 0.994, PASS; identical because the history uses realised quarter-t terms.

---

## 3. Method

**Party size (I1, I1b).** Every reviews dump was re-read with the pipeline's regexes and head-count parser imported from `abnb_party_size_reviews.py`, aggregated to sums per market x dump x review date (245 files: 123 Aug-2026 dumps, 120 Aug/Sep-2025 dumps; about two hours wall-clock across eight shards, checkpointed per file, `I1_inventory.csv`). Booked capacity is the `accommodates` of the reviewed listing from the market's 2026 listings dump, joined to both dumps; a review of a listing delisted by mid-2026 has no capacity on either side (survivor basis, second order for a mean). Windows follow E6: current side 1 Jul 2026 to min(late dump - 14 d, old dump - 14 d + 364 d), prior side the same dates 364 days earlier read from the market's own 2025 dump (vintage-matched) or from the 2026 dump (within-vintage). Market means are aggregated with each market's 2019 share of reviews (fixed-2019), plus equal and review weights. Elasticity 0.592 = 0.399 (log capacity, quote-basis hedonic, 1.38mm listings) + 0.140 (bedrooms) x 1.374 (bedrooms per unit log capacity, 29-market panel), reproduced from `13_party_size_adr.elasticities()`; the 13 docstring's 1.27 is stale, the note's 1.37 and 0.59 are what the code returns. Listed basis 0.577.

**Length of stay (I2a, I2b).** Runs are 14c's definition (contiguous `available == 'f'` nights per listing; a date gap also ends a run) with the start date kept, for every calendar dated May-Jul 2024, May-Sep 2025 and Jun-Sep 2026 (189 files, 18.6mm runs). Pairs: each 2026 June and August vintage against the 2025 vintage nearest 364 days earlier within 45 days, preferring one dated before the window. Runs over 90 nights are dropped; runs are assigned to a window by start date; active listings only; occupancy weighting as 14c (each listing contributes `estimated_occupancy_l365d` split across buckets in proportion to its in-window runs), from the 14c per-listing parquet where the vintage is one of its five and from the nearest listings dump within 60 days otherwise. Term = sum over buckets of d(share) x (ratio - 1) with the 14a ratios; regions ex NYC and LA; global on the 10-K FY25 nights weights.

**Geographic mix (I3).** H1's quarterly cell: within = sum(s0 A0 (1+g)) / sum(s0 A0) - 1, total the same on s1, geo mix = total - within, with s1 = s0 (1+n) renormalised. History 1Q24 to 2Q26 rebuilt with s1 projected from E's regional quarterly index (vintage-matched and within-vintage, review and equal weights) against H's disclosed-share term.

**Backtests (I0, I4).** E5's functions copied: expanding walk-forward OLS refit strictly before each scored quarter, scored against naive last quarter, prior year and AR(1); 1,000-shuffle permutation p; knowable-before-print flag. Nothing was tuned on the results.

---

## 4. What this can and cannot identify

- **A blocked run is not a booking.** It is a block of nights the host shows as unavailable: bookings plus owner use, maintenance, seasonal pauses and (NYC, LA) regulatory minimums. Host blocks are long, so the 28+ share of blocked nights (10 to 23% here depending on weighting and lead) is above Airbnb's disclosed 13 to 17% of nights, and by a factor that differs by market (14c: 1.2x NA to 1.8x APAC on mean run length). Comparing the same stay window at the same lead across vintages cancels the part of that inflation that is stable within a market. It does not cancel a change in host blocking behaviour: if hosts blocked more of September 2026 than of September 2025 for their own reasons, that reads here as a rise in long stays. The near-term window (0 to 30 days ahead) is where that risk is largest, which is why it sits in the band and not in the point. Runs that started before the window are excluded on both sides, which under-counts long stays symmetrically.
- **The LOS term has no validated history on this construction.** Two vintage pairs in 2026 and one four-market pair in 2025 are all that the CDN's one-year retention allows. The disclosure-based 14b series is a different object (bucket shares solved from ALOS) and stops at 4Q25.
- **Party size is a level term.** It has held at +0.7 to +1.0 pp of ADR every quarter since 2024, and it is at the low end of that range now. It carries no information about the quarter-to-quarter change in ex-FX ADR (r -0.17), which is what the H card's failure was about. Its value is that the +0.80 is measured on 2mm reviews of the quarter itself rather than carried from a trailing mean, so one of the four mix cells is no longer an assumption.
- **The geographic term inherits E's regional split, including its weakness in EMEA and LatAm.** EMEA at +0.9 on 56 markets is the review-weighted read and +0.2 equal-weighted; LatAm at +27.5 is five markets. The E-projected shares reproduce H's disclosed-share term with RMSE 0.4 to 0.7 pp on ten quarters, which is the same size as the term's own quarter-to-quarter movement, so the 3Q26 cell is measured but its mapping to the print is not validated. H's own term is not knowable before the print (it needs the letter's regional nights buckets).
- **None of this measures price.** The pricing residual is 4.6 pp of a 3.5 pp number and is workstream J's.
- **The Ireland country-level dump was matched by a prefix bug in the first run** (`ireland_*` picked up Dublin's files); fixed and re-run, one market of 123.

---

## 5. Next evidence

1. **The 5 Nov letter's regional nights buckets and regional ex-FX ADR lines** settle the geographic term (replace s1 with disclosed shares) and give the eleventh quarter for the E-to-H mapping test.
2. **A 2026 stay-length or ALOS disclosure** would let 14b extend past 4Q25 and give the LOS calendar read one anchor; none is expected.
3. **Re-run I1b after the September dumps land** (mid-October): the 3Q26 window extends from 16 Aug to about 15 Sep and the party-size read becomes three-quarters of the quarter. Cost is one shard hour; the scripts are checkpointed.
4. **Do not build a longer LOS history from calendars.** The CDN keeps one year; the Wayback vintages that exist for four markets carry no occupancy field, and the four-market 2025 read agrees with the direction 14b already has.

---

## 6. Files

| File | Contents |
|---|---|
| `analysis/src/adrq3/I0_protocol.py` | note-08 walk-forward and permutation helpers (copied from E5) |
| `analysis/src/adrq3/I1_party_size_daily.py` | classifier per market x dump x date, checkpointed to `data/processed/adrq3/I/cache/` (not committed, 13 MB) |
| `analysis/src/adrq3/I1b_party_size_windows.py` | windows, constructions, weightings, size term, within-vintage quarterly series |
| `analysis/src/adrq3/I2a_los_runs_dated.py` | blocked runs with start dates to `data/processed/adrq3/I/los_runs/` (not committed, 86 MB) |
| `analysis/src/adrq3/I2b_los_windows.py` | vintage pairs, windows, bucket shares, LOS term |
| `analysis/src/adrq3/I3_geo_mix.py` | 3Q26 geo mix by growth source, 1Q24-2Q26 history, backtest |
| `analysis/src/adrq3/I4_backtests.py` | scoreboard and series checks |
| `analysis/src/adrq3/I5_summary.py` | the summary file |
| `data/processed/adrq3/I/I_mix_terms_3q26.csv` | one row per measured term for J (quarter "3Q26"), plus comparison rows (2Q26, 3Q25, H card, WS-C) |
| `data/processed/adrq3/I/I1_inventory.csv`, `I1_market_windows.csv`, `I1_party_size_windows.csv`, `I1_party_size_quarterly.csv` | party size: dump inventory, market x window sums, aggregates, quarterly series |
| `data/processed/adrq3/I/I2_los_pairs.csv`, `I2_los_market_windows.csv`, `I2_los_term.csv` | LOS: pairs, market x window shares, regional and global term |
| `data/processed/adrq3/I/I3_geo_mix_3q26.csv`, `I3_geo_mix_history.csv`, `I3_geo_mix_backtest.csv` | geographic mix |
| `data/processed/adrq3/I/I4_backtest_scoreboard.csv`, `I4_party_size_series_check.csv` | backtests |
| `data/processed/adrq3/J/adr_card_v2.csv`, `J3_card_v2_terms.csv` | J3 re-run with the measured terms (mix source "workstream I I_mix_terms_3q26.csv (3 term rows read)") |
