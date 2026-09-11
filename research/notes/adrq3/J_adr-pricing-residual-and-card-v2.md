# J. The like-for-like pricing residual: listed prices, proxies, and ADR card v2

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Question:** the H card's component build failed walk-forward because its largest term, the like-for-like pricing residual (3 to 5 pp of a 4 pp number), is unobserved. Would a listed-price panel have tracked it? Does any proxy with July to September 2026 coverage track it? What is the 3Q26 and 4Q26 residual, what does the rebuilt card say, and does the rebuilt card pass the pre-registered test against naive?
- **Scripts:** `analysis/src/adrq3/J1_calendar_price_yoy.py`, `J1b_calendar_tests.py`, `J2_proxy_tests.py`, `J3_residual_nowcast_card_v2.py` (`py -3.13`; J2 reads two new raw pulls, everything else is offline).
- **Outputs (`data/processed/adrq3/J/`):** `calendar_price_yoy.csv`, `calendar_price_tests.csv`, `proxy_tests.csv`, `residual_nowcast.csv`, `adr_card_v2.csv`, `card_v2_backtest.csv`, plus the intermediate files in section 6.
- **New raw (main tree, `data/raw/external_prices/`, with `MANIFEST.csv`):** Eurostat `prc_hicp_minr` euro-area accommodation services (ECOICOP v2, monthly to July 2026) and INE Spanish hotel price index table 12157 (monthly to July 2026).
- **Does not redo:** party size, length of stay and geographic mix (workstream I; its `I_mix_terms_3q26.csv` is an input to the card), the FX estimators (WS-B, carried through H), the H reconstruction of the residual itself.

---

## 1. Bottom line

1. **No. A listed-price panel would not have told us about the residual, and the reason is structural, not statistical.** The Inside Airbnb calendar price is a stale host default: on the six year-apart vintage pairs that carry prices on both ends (Austin, Nashville, Paris, Rome; March and May 2025 against the same month of 2024; 68 million matched listing-dates on 191,000 listings, 66 to 77 percent of each 2025 dump), **72 to 77 percent of same-listing same-stay-date prices are identical a year later**, and the matched median y/y is exactly 0.0 in every market, every lead bucket and every stay quarter. Within a year, 3 to 5 percent of listing-dates are cut and 3 to 5 percent raised per month at every lead, median revision zero: hosts do not reprice into the stay date either. The statistics that do move are composition: the matched-panel arithmetic-mean ratio (global +0.9 to +2.5) and the unmatched all-listings median (global +0.8 to +5.1). Against the residual on six stay quarters (1Q25 to 2Q26) those series have r of -0.61 to -0.85: they decelerated from +5 to +1 while the residual rose from 2.2 to 4.9 pp. Sign agreement is 100 percent only because both are positive; direction agreement on quarter-to-quarter changes is 20 to 40 percent. Had we held 2026 calendar prices, the matched index would have printed 0.0 and the composition index would have pointed the wrong way. A second finding closes the route for good: **Inside Airbnb stopped populating calendar prices with the June 2025 dumps** (98 of 227 pre-2026 vintages carry prices, none dated after 28 May 2025; 89 have an empty column and 40 no column), so the BRIEF's "2024 and 2025 vintages carry price" holds only to May 2025 and the panel cannot be extended even if it were useful.

2. **No proxy with 3Q26 coverage tracks the residual, which confirms the decomposition note's null.** 164 note-08 tests over nine candidates (three CPI lodging series, the BEA hotels price index, euro-area HICP accommodation, the Spanish hotel price index, Marriott and Hilton RevPAR, and management's own ADR outlook wording coded on an ordinal scale), each in level and first difference at lags 0 and 1. Against the residual: 36 tests, zero beat naive walk-forward, best ratio 1.03 (BEA hotels price, first difference), and the only four flagged correlations (r 0.53 to 0.63 on first differences, permutation p 0.01 to 0.06) all die under Bonferroni (p 0.55 to 1.00). Against blended ex-FX ADR: 72 tests, zero beat naive. The three tests that do beat naive are on secondary targets and are marginal: euro-area HICP accommodation against EMEA ex-FX ADR (ratio 0.91, r 0.74, n 14) and management's wording against reported ADR (ratio 0.97 with sign accuracy 0.40, which is the wording carrying FX). US hotel prices ran negative y/y for seven straight quarters (2Q24 to 4Q25) while the residual rose from 2.1 to 3.7 pp; the two series are not measuring the same thing.

3. **The 3Q26 residual is set by rule, not by data: 4.61 pp (persistence, the 1H26 mean), band 2.4 to 4.85 pp.** The persistence case is 4.4 to 4.9 pp (1Q26 and 2Q26 values); the mean-reversion case is 2.4 pp (2023-25 mean, interquartile 2.0 to 2.9, full range 0.8 to 3.7); the unconditional 2023-26 distribution has a mean of 2.7 pp with a 10th to 90th percentile of 1.3 to 4.2 pp. The rule was written down before the walk-forward was run (J3 docstring) and is the same rule the backtest scores. Nothing external moves it: the proxies with a 3Q26 reading (CPI lodging +3.5 y/y for July-August, BEA hotels +3.6 for July, STR US hotel ADR +5.7 in July fading to +0.6 in the last full week of August, euro-area HICP accommodation +4.6 for July, Spanish hotel prices +5.9 for July, management "moderate increase") are recorded as readings and not used, because none of them passed.

4. **Card v2, on workstream I's measured 3Q26-to-date mix terms: 3Q26 reported ADR +3.0%, $176.5, central band $174.2 to $178.8 (+1.7% to +4.4%); 4Q26 +3.6%, $173.6, band $171.3 to $175.8 (+2.3% to +4.9%).** Ex-FX +3.46% in both quarters (central band +2.1 to +4.8, arithmetic extremes +0.4 to +4.9): residual 4.61 + geographic mix -1.43 (I: measured regional stays split, band -1.57 to -0.94) + unit size +0.80 (I: booked capacity +1.35% y/y on reviews dated 1 July to 16 August, band 0.53 to 1.00) + LOS +0.06 (I: 28-plus share of blocked runs -0.2 pp y/y, band -0.08 to 0.29) + new business -0.48 + interaction -0.10. 4Q26 carries I's 3Q26 terms because I measures only the quarter in progress. FX at the midpoint of the two H estimators (-0.43 pp in 3Q26, +0.15 in 4Q26); the estimator choice alone spans +2.3% to +3.7% in 3Q26 and +2.8% to +4.4% in 4Q26. Against the H card (+3.2% and +3.9%) v2 is 0.2 pp lower in 3Q26 and 0.3 pp lower in 4Q26: the residual moved up 0.67 pp (trailing four quarters 3.94 to persistence 4.61) and I's measured mix moved down 0.42 pp against H's inputs (geographic mix -0.24, LOS -0.24, unit size +0.06), with H's fee-migration increment (+0.16, +0.26) carried as a memo rather than added. At the team nights baseline this is GBV $25.9bn (+13.2%) in 3Q26 and $23.0bn (+12.8%) in 4Q26, still at the low end of management's "mid teens". The card on H's inputs, for reference, was +3.4% / $177.2 and +4.0% / $174.3 (`adr_card_v2.csv` carries `mix_source` in every row; re-running J3 regenerates it from whichever inputs exist).

5. **The pre-registered test is a coin flip, not a pass.** v2 with the persistence residual and perfectly measured mix terms has walk-forward RMSE 0.903 pp against naive 0.908 on 1Q24 to 2Q26 (ratio 0.994, n 10), which meets the letter of the criterion, and 0.851 against 0.816 on 2Q24 to 2Q26 (ratio 1.042, n 9, the H window), which does not. The jackknife range is 0.87 to 1.05 with the ratio below 1 in five of ten drop-one samples. Against AR(1) it is 0.79 and against H's route a 0.70, so v2 is a clear improvement on the component build (H: 1.42 on this window) but not on doing nothing. The term that causes the failure is the residual rule: with measured mix the error is the residual-rule error to within 0.06 to 0.30 pp (the prior-year new-business fill), and that error is -1.3 to -1.7 pp in 1Q24 to 2Q24 and -0.8 to -1.3 pp in 4Q25 to 1Q26, the two accelerations. A trailing rule of any length is late into a turn. The last-quarter rule (ratio 0.89, jackknife 0.84 to 0.94, below 1 in all ten) would pass, but it was not pre-registered and is reported as a sensitivity, not promoted. With H's trailing mix instead of measured mix every rule fails (1.12 to 1.36), which locates the H card's 1.58 in both places: about a third from the mix lag, two thirds from the residual lag.

---

## 2. Tables

### 2.1 Calendar listed-price panel: what exists and what it says

Coverage census (`J1_price_coverage.csv`): 227 calendar vintages dated before 2026, 98 with a populated `price` column, last priced snapshot 28 May 2025 (Singapore); every vintage from June 2025 is unpriced (89 empty, 40 without the column). Year-apart pairs with prices on both ends:

| market | region | 2024 vintage | 2025 vintage | matched listing-dates | matched listings | share of 2025 dump | share of prices unchanged y/y | up | down |
|---|---|---|---|---|---|---|---|---|---|
| austin | NA | 2024-05-19 | 2025-05-11 | 4.06m | 11,310 | 74% | 77% | 10% | 13% |
| nashville | NA | 2024-05-26 | 2025-05-17 | 2.45m | 6,859 | 71% | 73% | 13% | 14% |
| paris | EMEA | 2024-03-16 | 2025-03-03 | 21.37m | 60,774 | 71% | 75% | 12% | 13% |
| paris | EMEA | 2024-05-11 | 2025-05-03 | 23.39m | 65,448 | 77% | 75% | 11% | 13% |
| rome | EMEA | 2024-03-22 | 2025-03-05 | 8.02m | 22,942 | 66% | 72% | 20% | 8% |
| rome | EMEA | 2024-05-17 | 2025-05-09 | 8.66m | 24,136 | 67% | 73% | 18% | 10% |

"Unchanged" = same-listing same-stay-date (364 days apart, same weekday) price within 0.5 percent, stay dates 0 to 90 days ahead; the 0 to 365 day window gives the same shares.

Listed-price y/y by stay quarter, percent, global (NA 0.423 / EMEA 0.577, FY25 shares renormalised), all matched dates:

| statistic | 1Q25 | 2Q25 | 3Q25 | 4Q25 | 1Q26 | 2Q26 |
|---|---|---|---|---|---|---|
| matched median | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| matched 10% trimmed mean | 0.7 | 0.4 | 0.4 | 0.4 | 0.4 | 0.1 |
| matched arithmetic-mean ratio | 2.5 | 1.8 | 1.7 | 1.7 | 1.7 | 0.9 |
| unmatched all-listings median | 5.1 | 2.8 | 2.7 | 2.7 | 2.9 | 0.8 |
| unmatched open-dates median | 10.4 | 8.1 | 3.8 | 4.8 | 4.0 | 1.3 |
| **residual pricing, disclosed-based** | **2.2** | **1.9** | **2.8** | **3.7** | **4.4** | **4.9** |
| **ex-FX ADR, disclosed** | **1.0** | **1.0** | **2.0** | **3.0** | **4.0** | **4.0** |

1Q25 is Paris and Rome only (the May pairs start in 2Q25). By region, the NA matched-mean ratio is -1.2 in every quarter (Nashville -3.0, Austin +0.6) against NA disclosed ex-FX of +3.3 to +6.8; EMEA is +2.5 (Rome +7.4 to +7.9, Paris -2.2 to -3.0) against EMEA +3.0 to +5.0.

### 2.2 Calendar panel against the residual

| series (global, stay-quarter alignment) | n | r | sign agreement | direction agreement on changes | mean gap, pp |
|---|---|---|---|---|---|
| matched median | 6 | undefined (constant 0) | 0% | 0% | -3.3 |
| matched trimmed mean | 6 | -0.70 | 100% | 40% | -2.9 |
| matched mean ratio | 6 | -0.73 | 100% | 40% | -1.6 |
| matched mean ratio, open at both snapshots | 6 | -0.61 | 100% | 40% | -0.1 |
| unmatched all-listings median | 6 | -0.67 | 100% | 40% | -0.5 |
| unmatched open-dates median | 6 | -0.84 | 100% | 40% | +2.1 |

The same rows against blended ex-FX ADR give r -0.67 to -0.85 and direction agreement 20 percent; against regional ex-FX, NA r -0.8 (n 5) and EMEA r -0.4 to -0.8 (n 6). At the snapshot alignment (0 to 90 day window at the March and May 2025 snapshots against the same and next quarter's residual) there are two points, so only the levels are reported: matched mean ratio 1.75 against residuals of 2.07 (same quarter) and 2.36 (next). Lead revision within a year (`J1_lead_revision.csv`, 50 consecutive-vintage pairs): median revision 0.0 at every lead, 2 to 11 percent of listing-dates cut and 2 to 10 percent raised per month, no gradient toward the stay date.

### 2.3 Proxy history and the 3Q26 readings

Quarterly means of monthly y/y, percent. The residual and ex-FX columns are the targets.

| | residual | ex-FX | CPI lodging SA | BEA hotels | HICP EA accom. | INE hotel price | MAR RevPAR | HLT RevPAR | mgmt wording |
|---|---|---|---|---|---|---|---|---|---|
| 1Q23 | 3.5 | 3.0 | 7.1 | 7.9 | 9.3 | 10.8 | 34.3 | 30.0 | -1 |
| 2Q23 | 2.5 | 2.0 | 3.8 | 4.0 | 9.8 | 8.9 | 13.5 | 12.1 | -1 |
| 3Q23 | 1.0 | 0.5 | 5.6 | 6.0 | 7.8 | 7.0 | 8.8 | 6.8 | 1 |
| 4Q23 | 0.8 | 0.5 | 0.6 | 0.2 | 6.8 | 9.0 | 7.2 | 5.7 | 0.5 |
| 1Q24 | 2.3 | 2.0 | -0.6 | -0.9 | 5.3 | 8.5 | 4.2 | 2.0 | 0.5 |
| 2Q24 | 3.2 | 3.0 | -1.2 | -1.7 | 5.5 | 6.7 | 4.9 | 3.5 | 1 |
| 3Q24 | 2.1 | 2.0 | -0.9 | -1.4 | 5.0 | 6.9 | 3.0 | 1.4 | 1 |
| 4Q24 | 2.8 | 2.0 | 1.8 | 1.8 | 5.1 | 6.2 | 5.0 | 3.5 | 1 |
| 1Q25 | 2.2 | 1.0 | 0.5 | 0.0 | 4.5 | 4.6 | 4.1 | 2.5 | -1 |
| 2Q25 | 1.9 | 1.0 | -1.6 | -2.6 | 4.0 | 5.7 | 1.5 | -0.5 | 0 |
| 3Q25 | 2.8 | 2.0 | -1.9 | -3.1 | 2.8 | 5.4 | 0.5 | -1.1 | 1 |
| 4Q25 | 3.7 | 3.0 | -1.9 | -3.2 | 3.3 | 4.3 | 1.9 | 0.5 | 1 |
| 1Q26 | 4.4 | 4.0 | -0.9 | -2.2 | 3.9 | 4.2 | 4.2 | 3.6 | 2 |
| 2Q26 | 4.8 | 4.0 | 4.2 | 5.0 | 4.3 | 4.9 | 3.4 | 3.9 | 2 |
| **3Q26 reading** | ? | ? | 3.5 (Jul-Aug) | 3.6 (Jul) | 4.6 (Jul) | 5.9 (Jul) | n/a | n/a | 2 |

Other 3Q26 readings, not testable: STR US hotel ADR +5.7% for July (NYC +24% on the World Cup final), then +4.1, +3.5, +2.3, +0.6 across the August weeks (mean +2.6); Inside Airbnb 13-city stay quote per night, matched listings, June to August 2026: mean of market medians -0.9% (entire homes -1.7%), against the June to September 2025 listed-rate analogue of -2.9% on nine markets. Two sequential points on two bases; recorded, not used.

### 2.4 Proxy tests, note-08 protocol (2023Q1+, walk-forward 1Q24 to 2Q26, n 10)

| target | tests | flagged (abs r > 0.5, perm p < 0.05) | beat naive | beat naive and AR(1) | best ratio vs naive |
|---|---|---|---|---|---|
| residual pricing | 36 | 4 | 0 | 0 | 1.03 |
| ex-FX ADR (blended) | 72 | 26 | 0 | 0 | 1.03 |
| ex-FX ADR, NA (US proxies) | 32 | 5 | 0 | 0 | 1.18 |
| ex-FX ADR, EMEA (EA and ES proxies) | 16 | 9 | 2 | 2 | 0.91 |
| reported ADR (mgmt wording only) | 8 | 3 | 1 | 1 | 0.97 |

Best three against the residual, all first differences at lag 0: BEA hotels price r 0.63 (perm p 0.008, Bonferroni 0.55, walk-forward 1.03 vs naive, 0.77 vs AR(1), sign 6 of 10); CPI lodging SA r 0.62 (perm p 0.014, Bonferroni 0.65, 1.05); CPI lodging NSA r 0.60 (1.10). A first-difference correlation of 0.6 on 14 points that cannot beat "same as last quarter" is the note-03 pattern: the series co-move on the 2Q26 jump (CPI lodging went from -0.9 to +4.2 in one quarter, the residual from 4.4 to 4.8) and nowhere else.

### 2.5 The residual nowcast

| case | 3Q26 pp | band | 4Q26 pp | band | basis |
|---|---|---|---|---|---|
| **persistence (pre-registered point)** | **4.61** | 3.68 to 5.54 | **4.61** | 3.29 to 5.94 | mean of 1Q26 and 2Q26; band +/- 1 sd (3Q) and 1.41 sd (4Q) of quarterly residual changes, 0.93 pp |
| persistence case, 1H26 level | 4.61 | 4.38 to 4.85 | same | same | 1Q26 and 2Q26 values |
| mean reversion, 2023-25 level | 2.40 | 2.04 to 2.93 | same | same | 2023-25 mean and interquartile range; full range 0.83 to 3.70 |
| historical distribution | 2.71 | 1.28 to 4.18 | same | same | 1Q23 to 2Q26 mean, 10th to 90th percentile |
| last quarter | 4.85 | 3.92 to 5.78 | 4.85 | 3.53 to 6.17 | 2Q26 value |
| trailing 4 quarters (H's rule) | 3.94 | 3.01 to 4.87 | 3.94 | 2.62 to 5.26 | |
| AR(1) on the residual | 4.37 | 3.44 to 5.30 | 4.37 | 3.05 to 5.70 | fitted on 1Q23 to 2Q26 |
| proxy based | none | | none | | no survivor in 2.4 |

The 4Q26 residual is the same number as 3Q26 because no 3Q26 residual exists to update it; only the band widens. The card carries the pre-registered point with a band from the mean-reversion case (2.40) to the 2Q26 value (4.85), which is the honest spread of the two stories in the H card rather than a statistical interval.

### 2.6 Card v2

Mix inputs: workstream I `I_mix_terms_3q26.csv`, measured 3Q26-to-date rows (`mix_source` in every output row). Re-run `py -3.13 analysis/src/adrq3/J3_residual_nowcast_card_v2.py` to refresh.

| term, pp | 3Q26 lo / point / hi | 4Q26 lo / point / hi | source | label |
|---|---|---|---|---|
| Like-for-like pricing residual | 2.40 / 4.61 / 4.85 | same | J3 persistence rule; band mean-reversion to 2Q26 | assumed, anchored on measured residuals |
| Geographic mix | -1.57 / -1.43 / -0.94 | same (carried) | I: E_aug vintage-matched regional stays (NA +6.9, EMEA +0.9, LatAm +27.5, APAC +10.0) on 3Q25 shares and anchored regional ADR; band review- vs equal-weighted | measured |
| Unit size (party size) | 0.53 / 0.80 / 1.00 | same (carried) | I: booked capacity +1.35% y/y, reviews 1 Jul to 16 Aug 2026, 123 markets, elasticity 0.59 | measured |
| Length-of-stay mix | -0.08 / 0.06 / 0.29 | same (carried) | I: 28-plus share of blocked-run nights -0.2 pp y/y, Jun/Aug 2026 calendars, blocked runs not bookings | measured |
| New business (seats, hotels) | -0.75 / -0.48 / -0.23 | same | H (15_seats quarterly) | assumed |
| Interaction | -0.15 / -0.10 / -0.05 | same | H (07) | descriptive |
| **Ex-FX ADR** | **2.13 / 3.46 / 4.78** | **2.13 / 3.46 / 4.78** | root-sum-square half range 1.32; arithmetic extremes 0.38 to 4.92 | |
| memo: fee-migration increment (H) | -0.30 / +0.16 / +0.85 | -0.50 / +0.26 / +1.42 | not in the point | assumed |
| memo: H card mix inputs | geo -1.19, size 0.74, LOS 0.30 | same | H table 2.3 | for comparison |

| | 3Q26 | 4Q26 |
|---|---|---|
| Base | 3Q25 $171.29 | 4Q25 $167.51 |
| FX, EUR fit / baskets / midpoint | -1.12 / +0.26 / -0.43 | -0.66 / +0.97 / +0.15 |
| **Reported ADR y/y, point (midpoint FX)** | **+3.03%** | **+3.61%** |
| Reported y/y, EUR fit / baskets | +2.34% / +3.72% | +2.80% / +4.43% |
| Reported y/y, central band | +1.70 to +4.35 | +2.28 to +4.93 |
| Reported y/y, wide band (arithmetic extremes plus FX spread) | -0.74 to +5.18 | -0.28 to +5.89 |
| **ADR, $ point** | **$176.47** | **$173.55** |
| ADR, $ central band | $174.20 to $178.75 | $171.33 to $175.78 |
| GBV at 146.8mm / 132.7mm nights | $25.91bn, +13.2% | $23.03bn, +12.8% |
| Revenue at H's same-quarter take rate (17.88% / 13.62%) | $4,632mm, +13.1% | $3,137mm, +12.9% |
| H card, same FX | +3.19%, $176.76 | +3.91%, $174.06 |
| v2 on H's mix inputs (earlier run) | +3.45%, $177.20 | +4.03%, $174.26 |

The revenue line is H's convention and not recognition mechanics (revenue recognises at check-in); it is there so a 1 pp ADR move can be sized, $46mm in 3Q26 and $31mm in 4Q26.

### 2.7 Pre-registered walk-forward, ex-FX ADR, RMSE in pp

| model | 1Q24-2Q26, n 10: RMSE | ratio vs naive | jackknife range | vs AR(1) | sign acc. | 2Q24-2Q26, n 9: ratio vs naive |
|---|---|---|---|---|---|---|
| naive last disclosed ex-FX | 0.908 | 1.000 | | 0.79 | | 1.000 |
| prior year | 1.746 | 1.92 | | | | 2.22 |
| AR(1), expanding | 1.144 | 1.26 | 1.15 to 1.34 | 1.00 | 0.43 | 1.30 |
| H route a (component build) | 1.292 (n 9) | 1.42 | 1.24 to 1.58 | 1.13 | 0.29 | 1.58 |
| **v2, measured mix, persistence residual (pre-registered)** | **0.903** | **0.994** | **0.87 to 1.05 (5 of 10 below 1)** | **0.79** | **0.71** | **1.042** |
| v2, measured mix, last-quarter residual | 0.807 | 0.89 | 0.84 to 0.94 (10 of 10) | 0.71 | 0.86 | 0.88 |
| v2, measured mix, trailing 4q residual | 0.949 | 1.05 | 0.93 to 1.22 | 0.83 | 0.57 | 1.22 |
| v2, measured mix, AR(1) residual (n 8) | 0.831 | 0.92 | | 0.73 | 0.43 | 1.02 |
| v2, trailing-4q mix, persistence residual | 1.171 | 1.29 | | 1.02 | 0.29 | 1.38 |
| v2, trailing-4q mix, trailing 4q residual (= H) | 1.236 | 1.36 | | 1.08 | 0.43 | 1.58 |

**Verdict: FAIL on the intended reading.** The criterion was written as "ratio below 1"; 0.994 on one window and 1.042 on the other, with a jackknife straddling 1, is not evidence that v2 beats naive. Error attribution for the pre-registered model (`J3_card_v2_error_attribution.csv`): 1Q24 -1.28 (residual rule -1.34), 2Q24 -1.63 (-1.69), 3Q24 +0.72, 4Q24 -0.04, 1Q25 +0.37, 2Q25 +0.77, 3Q25 -0.58, 4Q25 -1.16 (-1.33), 1Q26 -0.82 (-1.12), 2Q26 -0.51 (-0.81). The model is biased low by 0.4 pp on average and by 0.8 to 1.7 pp in every acceleration quarter, exactly H's diagnosis one rule later. The measured-mix variant is an upper bound on workstream I: any error in I's real-time geographic, size and LOS terms adds to these numbers.

---

## 3. Method

**Calendar panel (J1, J1b).** Coverage census: every pre-2026 calendar vintage in the main-tree raw store is read for its header and the first 500,000 rows; a vintage is "priced" if more than half of those rows carry a non-empty `price`. Pairs: same market, snapshots 340 to 380 days apart, both priced. Load: pyarrow, columns `listing_id`, `date`, `available`, `price`; price parsed from "$1,234.00" to float, rows kept if 1 to 10,000 in listing currency (USD or EUR at both ends, so the y/y is constant-currency). Match: 2024 stay dates shifted +364 days (same weekday) and joined to 2025 on (listing, stay date) with a sorted-key search; leads 0 to 365 days from the 2025 snapshot. Per matched listing-date the log ratio; aggregated by lead bucket (0-30, 31-90, 91-180, 181-365, 0-90) and by stay quarter, in two regimes (all matched dates; open at both snapshots). Statistics: median, 10 percent trimmed mean, ratio of arithmetic means over the matched panel (composition within the panel), plus the unmatched all-listings and open-dates medians (composition of the whole dump). Region = mean of markets, global = NA 0.423 and EMEA 0.577 (FY25 10-K shares 29.6 and 40.3 renormalised); LatAm and APAC have no price-bearing 2024 vintage. Lead revision: 50 consecutive priced vintage pairs in the four markets (Paris on a deterministic 20 percent listing sample, others 50 percent), same listing and stay date, median log change by lead bucket at the later snapshot. Tests: stay-quarter alignment (asking prices for stays in quarter q against the residual and ex-FX of q, snapshots averaged where both cover q) and snapshot alignment (0-90 day window at the snapshot quarter against the same and next quarter); with n 6 and n 2 no walk-forward or permutation test is possible and the note reports r, sign agreement, direction agreement on changes and the gap.

**Proxies (J2).** Monthly series are averaged by calendar quarter into y/y percent; the 3Q26 reading is the mean of the months in hand. BLS CPI from the G raw cache (three series, to August 2026); BEA hotels-and-motels PCE price index from `data/raw/bea` (to July 2026); Eurostat euro-area HICP accommodation services from the ECOICOP v2 dataset `prc_hicp_minr` (the pre-2026 dataset `prc_hicp_midx` is frozen at December 2025, so the new dataset was pulled; to July 2026); INE hotel price index national total, table 12157 (to July 2026); Marriott and Hilton worldwide comparable constant-currency RevPAR from `06_measured_price_quarterly.csv` (to 2Q26); management's ADR outlook sentence for the quarter, taken from the prior quarter's shareholder letter and coded -1 (lower, pressure), 0 (flat), 0.5 (flat to slightly up), 1 (slightly higher, modestly up), 2 (moderate increase), with the verbatim wording in `J2_mgmt_adr_guide_coded.csv`. Each feature is tested in level and first difference at lags 0 and 1 against the residual (1Q23 to 2Q26), blended ex-FX ADR (windows 2023Q1+ and 2022Q1+), and the regional ex-FX ADR the proxy geographically covers. Per test: Pearson r and p, Spearman, 1,000-shuffle permutation p, an expanding-window OLS walk-forward from 1Q24 (fit strictly before t, at least four training quarters) scored by RMSE against naive last quarter, prior year and an AR(1) refit the same way, sign accuracy of the predicted change from last quarter, Bonferroni p over the tests on that target, and the knowable-before-print flag. Survivor = flagged, beats naive and AR(1), at least six walk-forward quarters. The Inside Airbnb sequential quote drift is computed from the 13-city listings parquet store (matched listings, median log change, `price_quote_price_per_night` in 2026 and listed `price` in 2025) and is not tested because it has no y/y and no history.

**Residual rules and card v2 (J3).** Every rule uses residual history strictly before the target quarter. The pre-registered point rule is persistence (mean of the last two residuals), chosen because H's diagnosis was that a trailing four-quarter residual lags accelerations by about 1.5 pp; it was fixed in the script docstring before the walk-forward ran and was not changed afterwards. Card v2 ex-FX = geographic mix + unit size + LOS mix (workstream I's measured 3Q26-to-date rows from `I_mix_terms_3q26.csv`, columns `adr_contribution_pp`, `lo`, `hi`; H's inputs are the fallback if the file is absent, flagged in `mix_source`; 4Q26 carries the 3Q26 terms) + new-business dilution (H's 15_seats quarterly base, bull and bear) + interaction (H) + residual. Reported = ex-FX + FX, with the H card's EUR-fit and four-basket estimators and their midpoint. The central band is the root-sum-square of the term half-ranges (terms independently sourced); the wide band is the arithmetic sum of extremes plus the FX estimator spread. Dollar ADR on 3Q25 $171.29 and 4Q25 $167.51; GBV and revenue at the team nights baseline of 146.8mm and 132.7mm nights with H's same-quarter implied take rates (17.88%, 13.62%), a comparison column only. The H card's incremental fee-migration term is a memo line and not in the point, because the residual already embeds the reprice on the cohort migrated by 1H26 and the increment is an assumption on an assumption (H section 4).

**Pre-registered walk-forward (J3).** For each quarter 1Q24 to 2Q26 (n 10; 2Q24 to 2Q26 also shown to match H), ex-FX_v2 = mix + new business (prior calendar year) + interaction (prior calendar year) + residual rule. Two mix variants: measured (the realised quarter-t geographic, size and LOS terms from the H reconstruction, i.e. what a perfect in-quarter measurement by workstream I would deliver, an upper bound on I) and trailing four quarters (H's rule). Benchmarks refit the same way: naive last disclosed ex-FX, prior year, AR(1) with an expanding fit on ex-FX strictly before t, and H's route a from `adr_exfx_backtest.csv`. Pass criterion: RMSE ratio vs naive below 1 for the pre-registered rule with measured mix. A jackknife drops one walk-forward quarter at a time and reports the range of the ratio.

---

## 4. What this can and cannot identify

- **The calendar price is not a transaction price and, for three quarters of listing-dates, not even a decision.** It is the host's default nightly rate, unchanged a year later on 72 to 77 percent of matched dates and revised on 6 to 10 percent per month. Airbnb's realised ADR moved 2 to 5 pp a year over the same period. A panel that does not move cannot track a residual that does, and the composition statistics that do move measure who lists, not what guests pay. This is the same conclusion as the quote-index test (8 September) reached from listings-dump prices, now reached from the per-date calendar, which was the last untested price field in the Inside Airbnb data.
- **Four markets, two regions, two snapshots.** Rome's matched-mean ratio (+7 to +11) and Paris's (-2 to -3) sit on either side of EMEA disclosed ex-FX; Nashville's -3 and Austin's +1 on either side of NA. Market dispersion is larger than the regional signal being sought, as in the quote-index test.
- **The panel cannot be extended.** Prices end at the May 2025 vintages. The 2026 calendars carry only availability. There is no 2026 listed-price y/y to build.

- **The proxy null is a confirmation, not a discovery.** The decomposition note found every external price benchmark at Bonferroni p 1.00 against ex-FX ADR after 2023; this note adds two European series, management's wording and the residual itself as a target, with a walk-forward, and finds the same thing. The four flagged first-difference correlations are one event (the 2Q26 jump) seen through four correlated US hotel series, not four votes.
- **Euro-area HICP accommodation against EMEA ex-FX is the one marginal survivor, and it is not usable here.** Ratio 0.91 on 10 walk-forward quarters, jackknife not run; it is a regional comparator for one region's ADR, not a residual proxy, and the residual is a blended global term. It is worth carrying into the regional read for the 5 November letter, nothing more.
- **Management's wording tracks reported ADR because it carries FX.** Sign accuracy 0.40 says it does not tell you the direction of change; it tells you the level bucket. "Moderate increase" preceded +9.0% and +5.3% reported; the 3Q26 "moderate" is consistent with anything from +2.5% to +5%.
- **The residual is still unidentified and this note does not change that.** It absorbs like-for-like pricing, sub-regional mix inside regions, measurement error in the other four terms and the fee-migration reprice on the migrated cohort. A rule on its own history is the only thing that survived, and a rule on its own history cannot see a turn.
- **The measured-mix variant of the backtest is an upper bound on workstream I.** It uses the realised quarter-t mix terms. Workstream I's own scoreboard (`I4_backtest_scoreboard.csv`) has the review-based unit-size term at a walk-forward ratio above 4 against ex-FX ADR, so I's real-time terms will carry error the upper bound does not.
- **The naive benchmark is hard to beat by construction.** Disclosed ex-FX ADR is rounded to whole percentage points (1, 2, 3, 4), so "same as last quarter" has an RMSE of 0.82 to 0.91 pp on a series whose quarterly changes are mostly 0 or 1. Any model that carries the unrounded components inherits rounding noise the naive does not.

---

## 5. Next evidence

1. **The 5 November ex-FX ADR sentence resolves the residual.** Ex-FX +4% or better says persistence held (residual near 4.6); +3% or below says mean reversion (residual near 2.4 to 3). This is the same one-line resolution H named; card v2 has not moved it.
2. **AirDNA or Transparent realised-rate data, not more listed prices.** Section 1 and 2.1 close the listed-price route on the only price-bearing calendar panel that exists. A same-asset-class realised ADR series is the only thing that could measure the residual directly.
3. **Do not re-run the calendar price panel unless Inside Airbnb restores prices.** Every vintage from June 2025 is unpriced; there is nothing more to extract.
4. **Score the pre-registered rule on 5 November.** The v2 persistence residual implies ex-FX of 3.5 pp with I's mix (3.9 with H's), naive says 4.0; a print of 3 or 4 does not separate them, so the test that matters is the residual's own level backed out of the letter's components, not the ex-FX total.
5. **Carry euro-area HICP accommodation into the EMEA line of the regional read**, with the September flash (1 October) and the final (mid-October) both before the print.

---

## 6. Files

| File | Contents |
|---|---|
| `analysis/src/adrq3/J1_calendar_price_yoy.py` | coverage census, six year-apart calendar pairs, matched same-listing same-date same-lead price y/y, aggregation, lead-revision diagnostic |
| `analysis/src/adrq3/J1b_calendar_tests.py` | the calendar series against the residual, ex-FX and regional ex-FX at both alignments |
| `analysis/src/adrq3/J2_proxy_tests.py` | proxy panel, 3Q26 readings, 164 note-08 tests, management wording code, Inside Airbnb sequential quote drift |
| `analysis/src/adrq3/J3_residual_nowcast_card_v2.py` | residual rules, nowcast, card v2, pre-registered walk-forward with jackknife and error attribution |
| `data/processed/adrq3/J/calendar_price_yoy.csv` | region and global listed-price y/y by snapshot quarter, lead bucket, stay quarter, regime and statistic |
| `data/processed/adrq3/J/calendar_price_tests.csv` | n, r, sign agreement, gaps at stay-quarter and snapshot alignments |
| `data/processed/adrq3/J/J1_calendar_pairs.csv`, `J1_provenance.csv`, `J1_price_coverage.csv`, `J1_lead_revision.csv`, `J1b_calendar_vs_targets_side_by_side.csv` | per-pair results, file provenance, the price coverage census of every pre-2026 vintage, lead-revision diagnostic, side-by-side series |
| `data/processed/adrq3/J/proxy_tests.csv` | all 164 tests with walk-forward ratios, permutation and Bonferroni p, knowable flag, survivor flag |
| `data/processed/adrq3/J/J2_proxy_monthly.csv`, `J2_proxy_quarterly_panel.csv`, `J2_proxy_readings_3q26.csv`, `J2_mgmt_adr_guide_coded.csv`, `J2_ia_quote_sequential.csv`, `J2_walk_forward_paths.csv` | proxy histories, the 3Q26 readings, the coded wording with verbatim quotes, the sequential quote drift, walk-forward paths |
| `data/processed/adrq3/J/residual_nowcast.csv` | every residual rule and case for 3Q26 and 4Q26 with bands |
| `data/processed/adrq3/J/adr_card_v2.csv`, `J3_card_v2_terms.csv` | card v2 by quarter and FX estimator; the term table with sources and labels |
| `data/processed/adrq3/J/card_v2_backtest.csv`, `J3_card_v2_walk_forward_paths.csv`, `J3_card_v2_error_attribution.csv` | walk-forward scores for every rule and mix variant with jackknife; per-quarter paths; error attribution |
| `C:\Users\krish\citadel-abnb\data\raw\external_prices\` | Eurostat HICP accommodation (ECOICOP v2) and INE hotel price index raw JSON with `MANIFEST.csv` |
