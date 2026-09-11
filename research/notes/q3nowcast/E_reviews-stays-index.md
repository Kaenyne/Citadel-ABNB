# E. Review-date stays index: 123 Inside Airbnb markets, 363 dump vintages, July and August 2026 read

**Date:** 2026-09-11 (the 12 Sep 2026 Q3 nowcast run; all dumps downloaded and counted 2026-09-11).
Author: Krishang Surapaneni (compiled with Claude Code), workstream E.

**Question.** Can review dates in the Inside Airbnb reviews dumps, counted per market per dump vintage, give a stays index that (a) tracks disclosed Nights and Seats Booked y/y out of sample and (b) reads July and August 2026 now, so that 3Q26 nights growth can be stated with a band before the 5 Nov print?

**Scripts.** `analysis/src/q3nowcast/E1_inventory_and_discover.py` (local inventory, CDN HEAD probe, download plan), `E2_download_reviews.py` (240 dumps, 15.9 GB, into the main-tree raw store with a sha256 manifest), `E3_review_counts.py` (listing x month counts per file, checkpointed per file in `cache/`), `E4_build_index.py` (survivorship wedge, four y/y constructions, region and global aggregates, quarterly), `E4b_stable_listing.py` (same-listing variant across the 2025 and 2026 vintages), `E5_backtest.py` (note-08 walk-forward against ABNB KPIs and Eurostat), `E6_nowcast.py` (day-matched July and August windows, vintage-matched read, partial-to-full quarter, implied nights), `E7_report.py` (prints every table below). Run order E3, E4, E4b, E5, E6, E7, all with `py -3.13`.

**Read first.** `research/notes/overnight/08_altdata-index-and-backtests.md` section 2 for the protocol and for the earlier negative (13-city panel, n = 0 usable year-ago quarters because of composition). This note replaces that panel with 123 markets and, for 119 of them, a second dump vintage about 12 months older, which is what makes survivorship measurable rather than assumed.

---

## 1. Bottom line

1. **The index beats naive, modestly, and only as a coincident level.** The global all-reviews, review-count-weighted quarterly y/y (within one dump vintage) has an expanding-window walk-forward RMSE of 1.48 pp against disclosed nights y/y over 2024Q1 to 2026Q2 (10 scored quarters), versus 2.16 pp for naive last-quarter, 3.67 pp for prior-year and 2.11 pp for AR(1): ratios 0.68, 0.40 and 0.70. Jackknife over the 10 scored quarters keeps the ratio between 0.63 and 0.86, so no single quarter carries it. r = 0.86 (permutation p = 0.001), but r restricted to 2024Q1 onward is 0.42: most of the correlation is the 2023 normalisation, and inside the flat 2024 to 2026 stretch the signal is weaker. Every first-difference feature loses to naive (ratios 1.45 to 1.53 at lag 0). Lag-1 levels, the only fully knowable-before-print variant, sit at 0.87 to 0.91 vs naive: marginal. The July-August windows used here are lag 0 with the quarter 60 to 65 percent complete, so "partial" availability is the honest flag. (descriptive, computed)

2. **Survivorship is large, stable and measured, not assumed.** The same review month counted in a dump one year later holds 15 to 16 percent fewer reviews for months 1 to 12 before the early dump, decaying to 11 to 12 percent for months 30 to 40 back (129 vintage pairs pooled). Because both sides of a within-vintage y/y are attrited but the year-ago side has had one more year to attrite, the within-vintage y/y runs about 20 pp above the truth: 3Q26-to-date within-vintage +25.9 percent (review-weighted) against +5.2 percent vintage-matched (2026 dump over the 2025 dump), a 20.7 pp wedge, versus 20.4 pp in 2Q26 and 18.6 pp in 3Q25 on the same construction. The backtest works because the wedge is roughly constant in time, not because the level is right. Per-market wedges range 7 to 52 pp; the ten largest (Brussels, Dallas, Montreal, Toronto, Vienna, Stockholm, London, Barcelona, Vaud, Broward) are the markets where the within-vintage read is least trustworthy on its own. (sourced, computed)

3. **July and August 2026 read.** Day-matched (same calendar window, 364 days earlier, ending 14 days before each dump because 14 days is where posting completeness passes 98.5 percent):
   - Within-vintage, review-weighted: July +26.2 percent global (NAM +28.1, EMEA +20.7, LatAm +52.4, APAC +24.0); August-to-date +24.7 percent (NAM +27.5, EMEA +16.3, LatAm +63.9, APAC +27.0). These carry the 20 pp wedge.
   - Vintage-matched (the survivorship-clean number), review-weighted: July +3.8 percent (NAM +4.3, EMEA +1.1, LatAm +20.6, APAC +3.8); August-to-date +8.2 percent (NAM +7.6, EMEA +0.3, LatAm +44.2, APAC +7.4); 3Q26-to-date +5.2 percent (NAM +6.9, EMEA +0.9, LatAm +27.5, APAC +7.4). Nights-share weighted 3Q26-to-date +6.0 percent. 2Q26 on the same construction was +4.3 percent (nights-weighted +5.6), so the quarter-to-date is running about 0.5 to 1 pp faster than 2Q26 on the review-weighted series and flat on the nights-weighted one. The median market is +2.2 percent; 77 of 119 markets are positive; the interquartile range is -2.2 to +8.1 percent. (descriptive)
   - Coverage: 122 of 123 markets have an August 2026 dump (Tokyo's latest is 30 Jun). 111 markets deliver a full July and an August-to-date window, 88.4 percent of the 3Q25 review base; the 12 without (Brisbane, Tasmania, Montreal, Venice, Tokyo, New Zealand, Vaud, Los Angeles, San Francisco, Albany, New York City, Portland) have 10 to 13 Aug dumps, so after the 14-day trim their window ends before 1 Aug. The August-to-date window is 1 to 17 days long, median 15; 66 markets have 14 or more days. August is therefore a half-month read with 40 percent of the quarter's days still unseen. (descriptive)

4. **3Q26 stays growth and implied nights.** Lifting the quarter-to-date index to a whole quarter with the partial-to-full gap measured on 2023 to 2025 (+0.1 pp review-weighted, -0.6 pp equal-weighted, sd 0.2 pp) and mapping through the OLS of nights y/y on the index (2023Q1 to 2026Q2, 14 quarters, slope 0.32 nights-pp per index-pp): **+10.0 percent nights y/y, band 8.6 to 11.5** (all-reviews, review-weighted, band = walk-forward RMSE combined with the gap sd). The equal-weighted, median and nights-share weighted variants give 9.2 to 9.3; the vintage-matched variants give 8.6 to 9.2. Anchoring on the 2Q26 print instead (10.34 plus slope times the index change since 2Q26) gives 9.8 to 10.8. Taking the seven rows together: **3Q26 nights +9.5 percent, band 8.5 to 11.0**. Naive last quarter is 10.3, prior year 8.8, the team baseline 9.9 (comparison columns, not inputs). The index says a low-double-digit print is plausible but not that 3Q26 accelerates materially from 2Q26; at 146.8mm nights the team's 9.9 is inside the band and so is 9.0. (computed; the OLS mapping and the partial-to-full gap are assumed to hold in 2026)

5. **Same-listing demand is falling.** The stable-listing variant (listings with reviews in both the 2025 and 2026 dumps, so identical sets on both sides) is -3.3 percent y/y in 2Q26 (NAM -1.0, EMEA -3.3, LatAm -2.0, APAC -9.3) and -7.4 percent in July 2026; the within-vintage 24-month cohort measure agrees (-7.1 percent 2Q26). All of the platform's growth in these mature markets is coming from listings less than a year old. This is a composition fact about supply, not a demand signal, and it is why the all-reviews series (which includes new listings) is the one that tracks nights. (descriptive)

6. **Eurostat monthly check passes.** The EU27 aggregate of our EU markets' review counts against Eurostat platform nights y/y (2023M1 onward, 22 walk-forward months): RMSE ratio 0.59 vs naive, 0.45 vs prior-year, 0.74 vs AR(1), r 0.68. 36 of 37 country and EU27 tests beat naive. Monthly platform nights are noisy and naive last-month is a weak benchmark for a y/y series, so the pass is necessary, not sufficient. (computed)

## 2. Tables

### 2.1 Data held and added (sourced)

| Vintage month | Reviews dumps | Note |
|---|---|---|
| Aug-Sep 2025 | 119 | downloaded this run, year-ago vintages for survivorship (5 are Sep 2025) |
| Jun 2026 | 107 | held before the run |
| Jul 2026 | 15 | held before the run |
| Aug 2026 | 122 | 121 downloaded this run plus 1 held |
| Total | 363 files, 123 markets, 24 GB on disk | 0 download failures, sha256 in `download_manifest.csv` |

Region split of the 123 markets: NAM 42, EMEA 57 (includes 1 Africa, 3 Middle East), LatAm 7, APAC 17. Inside Airbnb covers regulated cities and tourist regions, not Airbnb's footprint: the panel is heavy in mature urban Europe and North America and thin in LatAm and APAC, where Airbnb reports its fastest nights growth.

### 2.2 Survivorship wedge: same month, two vintages ~12 months apart, 129 pairs pooled (computed)

| Months before the early dump | 1 | 3 | 6 | 12 | 18 | 24 | 36 |
|---|---|---|---|---|---|---|---|
| Reviews in late dump / early dump | 0.849 | 0.840 | 0.847 | 0.854 | 0.867 | 0.871 | 0.883 |
| Annual attrition of review history, % | 15.1 | 16.0 | 15.3 | 14.6 | 13.3 | 12.9 | 11.7 |

The month-0 ratio (1.82) is truncation, not attrition: the early dump had not yet seen most of its own dump month.

### 2.3 Posting completeness k days after a review date (computed, 122 market pairs)

| k days | 0 | 3 | 7 | 10 | 12 | 13 | 14 | 21 | 30 |
|---|---|---|---|---|---|---|---|---|---|
| Share of the date's reviews already posted | 0.29 | 0.55 | 0.68 | 0.74 | 0.81 | 0.89 | 1.01 | 1.03 | 1.03 |

The window is complete by day 14 (Airbnb's review window is 14 days from check-out). The 1.03 plateau is the mirror of attrition: the later dump has lost some listings, so the earlier dump looks 3 percent "over-complete". k = 14 is used everywhere below.

### 2.4 Global quarterly index vs disclosed KPIs, review-count weighted, percent (computed)

| Quarter | Within-vintage all reviews | 24m cohort | Vintage-matched | Stable listing | Nights y/y | GBV y/y | Revenue y/y |
|---|---|---|---|---|---|---|---|
| 1Q24 | 27.7 | -7.9 | 11.0 | (mechanical) | 9.5 | 12.3 | 17.8 |
| 2Q24 | 23.1 | -9.9 | 6.7 | | 8.7 | 11.0 | 10.6 |
| 3Q24 | 22.5 | -9.8 | 5.6 | | 8.5 | 9.8 | 9.9 |
| 4Q24 | 25.1 | -9.1 | 6.7 | | 12.3 | 13.5 | 11.8 |
| 1Q25 | 22.1 | -11.2 | 3.6 | | 7.9 | 7.0 | 6.1 |
| 2Q25 | 23.0 | -9.0 | 4.2 | | 7.4 | 10.8 | 12.7 |
| 3Q25 | 21.6 | -9.8 | 3.0 | | 8.8 | 13.9 | 9.7 |
| 4Q25 | 27.1 | -7.5 | 6.2 | | 9.8 | 15.9 | 12.0 |
| 1Q26 | 29.3 | -6.9 | 7.3 | 5.4 | 9.2 | 19.2 | 17.9 |
| 2Q26 | 25.0 | -7.1 | 4.3 | -3.3 | 10.3 | 15.7 | 16.5 |
| 3Q26 to date | 26.3 | n/a | 5.2 | n/a | ? | ? | ? |

The stable-listing column is only meaningful in the 12 months before the 2025 dump (its fixed listing set mechanically inflates earlier years), so it is shown for 1Q26 and 2Q26 only and is excluded from the backtest.

### 2.5 Regional quarterly index, vintage-matched, review-count weighted, percent (computed)

| Quarter | NAM | EMEA | LatAm | APAC | Global | Global nights-weighted |
|---|---|---|---|---|---|---|
| 1Q25 | -2.6 | 4.3 | 27.2 | -0.8 | 3.6 | 5.1 |
| 2Q25 | -0.9 | 3.0 | 34.0 | 4.7 | 4.2 | 6.1 |
| 3Q25 | -0.4 | 2.2 | 18.4 | 4.9 | 3.0 | 4.3 |
| 4Q25 | 0.1 | 5.5 | 24.8 | 6.2 | 6.2 | 7.6 |
| 1Q26 | 5.4 | 4.7 | 18.2 | 8.9 | 7.3 | 6.4 |
| 2Q26 | 6.9 | 1.5 | 20.4 | 2.3 | 4.3 | 5.6 |
| 3Q26 to date | 6.9 | 0.9 | 27.5 | 7.4 | 5.2 | 6.0 |

North America turned positive in 1Q26 after four quarters at or below zero and holds at +7 in the quarter to date; EMEA has faded to about +1; LatAm (7 markets, Mexico City +37, Rio +29, Santiago +17 in the quarter to date) is where the acceleration sits.

### 2.6 Backtest scoreboard, note-08 protocol (computed)

| Family | Tests | Flagged (abs r > 0.5, p < 0.05) | Beat naive | Beat naive and AR(1) | Beat naive by 20 pct | Best ratio |
|---|---|---|---|---|---|---|
| ABNB quarterly (nights, GBV, revenue, BKNG and EXPE room nights; 5 regions x 4 measures x 3 weights x lags 0,1 x level, d1 x 2 windows) | 2560 | 1186 | 463 | 372 | 70 | 0.60 |
| Eurostat monthly (18 countries and EU27, two builds, two windows) | 74 | 63 | 71 | 71 | 68 | 0.40 |

2560 tests is a multiplicity problem by construction; the honest reading is the feature family, not the best cell. Nights target, 2023Q1 window, level features, lag 0, expanding walk-forward from 2024Q1 (10 scored quarters):

| Feature | r | r 2024Q1+ | perm p | RMSE pp | vs naive | vs prior yr | vs AR(1) | Jackknife min-max | Sign acc | Knowable before print |
|---|---|---|---|---|---|---|---|---|---|---|
| GLOBAL all reviews, review-wtd | 0.86 | 0.42 | 0.001 | 1.48 | 0.68 | 0.40 | 0.70 | 0.63-0.86 | 0.7 | partial |
| GLOBAL all reviews, equal-wtd | 0.85 | 0.34 | 0.001 | 1.48 | 0.69 | 0.40 | 0.70 | 0.34-0.90 | 0.8 | partial |
| GLOBAL nights-share wtd | 0.84 | 0.34 | 0.002 | 1.57 | 0.73 | 0.43 | 0.74 | 0.39-0.95 | 0.7 | partial |
| GLOBAL vintage-matched, review-wtd | 0.86 | 0.32 | 0.003 | 1.47 | 0.68 | 0.40 | 0.70 | 0.59-0.88 | 0.7 | partial |
| GLOBAL 24m cohort, equal-wtd (best cell) | 0.86 | 0.50 | 0.002 | 1.30 | 0.60 | 0.35 | 0.62 | 0.37-0.78 | 0.8 | partial |
| NAM vintage-matched, review-wtd, lag 1 | 0.77 | 0.52 | 0.003 | 1.53 | 0.71 | 0.42 | 0.73 | 0.66-0.78 | 0.7 | yes |
| GLOBAL all reviews, review-wtd, lag 1 | 0.69 | | 0.016 | 1.97 | 0.91 | 0.54 | 0.94 | | 0.5 | yes |
| GLOBAL all reviews, review-wtd, first difference, lag 0 | -0.03 | | 0.89 | 3.17 | 1.47 | 0.87 | 1.51 | | 0.5 | partial |

Naive RMSE 2.16 pp, prior-year 3.67, AR(1) 2.11 on the same 10 quarters. Other targets: GBV best 0.69 (NAM mature, d1), revenue best 0.81, BKNG room nights best 0.86 (lag 1), EXPE room nights 0.61 (EMEA d1 lag 1, negative r, which is mean reversion, not a signal). The 2022Q1 window (14 scored quarters from 2023Q1) gives 0.71 to 0.84 vs naive for the same global level features; its prior-year ratio of 0.17 is the Covid base effect and should be ignored.

### 2.7 July and August 2026 by region, day-matched, review-count weighted, percent (computed)

| Window | Construction | NAM | EMEA | LatAm | APAC | Global | Global nights-wtd (equal-wtd regions) | Markets |
|---|---|---|---|---|---|---|---|---|
| June 2026 | within-vintage | 31.2 | 16.5 | 39.8 | 19.4 | 22.4 | 24.7 | 122 |
| July 2026 | within-vintage | 28.1 | 20.7 | 52.4 | 24.0 | 26.2 | 27.5 | 111 |
| Aug 1 to dump-14 | within-vintage | 27.5 | 16.3 | 63.9 | 27.0 | 24.7 | 29.2 | 111 |
| July 2026 | vintage-matched | 4.3 | 1.1 | 20.6 | 3.8 | 3.8 | 4.5 | 97 |
| Aug 1 to dump-14 | vintage-matched | 7.6 | 0.3 | 44.2 | 7.4 | 8.2 | 9.7 | 93 |
| Jul 1 to dump-14 (3Q26 to date) | vintage-matched | 6.9 | 0.9 | 27.5 | 7.4 | 5.2 | 6.0 | 119 |
| Wedge, 3Q26 to date, pp | within minus vintage-matched | 21.7 | 20.8 | 23.4 | 19.7 | 21.1 | 21.4 | 119 |

The vintage-matched July and August rows need the 2025 dump to reach the same calendar date, which drops markets whose 2025 dump was earlier in August than the 2026 one; the 3Q26-to-date row trims to the shorter of the two windows and keeps all 119.

### 2.8 Partial quarter to whole quarter, global, review-count weighted (computed)

| Year | Jul 1 to same day-of-year as 2026 cut, y/y % | Whole quarter y/y % | Gap pp |
|---|---|---|---|
| 2023 | 26.9 | 26.9 | +0.1 |
| 2024 | 21.2 | 21.5 | +0.3 |
| 2025 | 21.8 | 21.6 | -0.1 |
| 2026 | 26.3 | ? | mean +0.1, sd 0.2 |

Equal-weighted: -0.35, -0.70, -0.78 (mean -0.6). The first 45 to 50 days of the quarter have been a near-unbiased read of the whole in each of the last three years; the risk is September, which is where the 2023 to 2025 gaps were measured and cannot rule out a 2026 September that breaks the pattern.

### 2.9 3Q26 implied nights (computed; OLS 2023Q1 to 2026Q2, 14 quarters)

| Measure | Weighting | Slope | Index 3Q26 full, % | Index 2Q26, % | Implied nights y/y | Anchored on 2Q26 print | Band pp | Low | High |
|---|---|---|---|---|---|---|---|---|---|
| all reviews, within-vintage | review-count | 0.32 | 26.4 | 25.0 | 10.0 | 10.8 | 1.5 | 8.6 | 11.5 |
| all reviews, within-vintage | equal | 0.26 | 24.3 | 24.6 | 9.2 | 10.2 | 1.5 | 7.7 | 10.7 |
| all reviews, within-vintage | median | 0.40 | 21.3 | 22.5 | 9.2 | 9.8 | 1.5 | 7.7 | 10.7 |
| all reviews, within-vintage | nights share | 0.26 | 27.4 | 26.6 | 9.3 | 10.6 | 1.6 | 7.8 | 10.9 |
| vintage-matched | review-count | 0.32 | 5.3 | 4.3 | 9.2 | 10.7 | 1.5 | 7.7 | 10.7 |
| vintage-matched | equal | 0.26 | 2.9 | 3.8 | 8.6 | 10.1 | 1.6 | 7.0 | 10.2 |
| vintage-matched | nights share | 0.25 | 5.4 | 5.6 | 8.7 | 10.3 | 1.7 | 6.9 | 10.4 |

Comparison columns: naive last quarter 10.3, prior year 8.8, team baseline 9.9 (146.8mm nights, band 8.5 to 10.3), guide "low double digits". The band is the walk-forward RMSE (out of sample) combined with the partial-to-full gap sd; it does not include model risk in the slope, which the 2024Q1+ r of 0.3 to 0.5 says is real.

## 3. Method

1. **Counting (E3).** Each reviews.csv.gz is read with pyarrow (listing_id, date only), grouped to listing x month, cached as parquet per file (363 files, 186 MB, not committed), and summarised to market x vintage x month: all reviews, reviews by listings whose first review in that dump is 12+ and 24+ months before the month, and daily counts from 2021 for the day-matched windows. Review date is the only date in the schema; it is check-out plus 0 to 14 days (table 2.3 confirms the 14-day window empirically).
2. **Four y/y constructions (E4, E4b).** Within-vintage all reviews n[m]/n[m-12] (primary, carries the wedge); 12-month-mature both sides; 24-month cohort (identical set both sides, excludes anything born in the last two years); vintage-matched n_2026[m]/n_2025[m-12] (symmetric survivorship and posting lag, needs a year-ago dump: 119 markets); stable-listing (intersection of listing ids across the two dumps). The dump month itself is dropped as truncated. A market-quarter enters the quarterly index only with all three months on both sides.
3. **Aggregation.** Equal-weighted mean of market y/y, review-count weighted (sum of counts), median, and FY25 nights-share weights on the equal-weighted regional means (NAM 28.3, EMEA 41.6, LatAm 17.9, APAC 12.3; region code NAM because pandas reads "NA" as missing, a bug that had silently dropped North America from the previous run's downstream tables).
4. **Backtest (E5).** Expanding-window OLS y ~ x refit at each quarter on data strictly before it, scored from 2024Q1 (2023Q1 window) and from 2023Q1 (2022Q1 window); baselines naive y[t-1], prior year y[t-4], AR(1) refit the same way; 1,000-shuffle permutation p on Pearson r; jackknife of the ratio over scored quarters; lags 0 and 1; level and first difference; targets nights, GBV, revenue, BKNG and EXPE room nights. Eurostat: country review counts summed, y/y against Eurostat platform nights y/y monthly, same walk-forward with prior-year at 12 months.
5. **Nowcast (E6).** Windows end 14 days before each market's latest dump and are compared with the same window 364 days earlier (52 weeks, same day-of-week mix). The vintage-matched version reads the prior-year window from the market's 2025 dump. The partial-to-full gap is the difference between the Jul-1-to-cut and the Jul-1-to-Sep-30 y/y in each of 2023, 2024, 2025 inside the 2026 dump. Implied nights is the OLS mapping of table 2.9 plus a 2Q26-anchored variant.

## 4. What this can and cannot identify

- **Can:** the direction and rough size of stays growth in mature urban markets, coincident with the quarter, about 30 percent better than naive out of sample over 10 quarters; the size of survivorship bias (15 percent a year, roughly constant); that same-listing volume is shrinking while total volume grows; a survivorship-clean quarter-to-date number (+5.2 percent) and its regional split.
- **Cannot:** Airbnb's actual nights. The panel is 123 regulated cities and regions; Airbnb's growth is in expansion markets the panel does not hold, which is why the vintage-matched level (+4 to +7) sits far below reported nights (+9 to +10) and why the mapping needs a fitted intercept. Reviews per stay is unobserved and can drift (guest mix, review prompts, long stays); a 1 pp change in review propensity is indistinguishable from 1 pp of demand. Seats per booking and ADR are invisible to this data.
- **Cannot separate** a real August acceleration (+8.2 vintage-matched vs +3.8 July) from the mechanics of a 1 to 17 day window: 12 large markets (New York, Los Angeles, San Francisco, Montreal, Tokyo among them) are absent from the August row, and LatAm's +44 is five markets.
- **Composition and basis:** the 2026 dumps for Dec 2025 to May 2026 are partial-scope monthly releases per the Inside Airbnb regime memory; this run uses only the Jun to Aug 2026 full dumps and the Aug to Sep 2025 full dumps, so the partial-scope regime does not enter. The 13-city panel's Dec 2022 to Aug 2026 listings dumps were not needed. Ten markets carry per-market wedges above 34 pp (table in `E7_report.py` section 13b), consistent with scope or ID changes between dumps; they are inside the vintage-matched aggregate, and dropping them moves the 3Q26-to-date global from +5.2 to +5.0 percent review-weighted and from +3.5 to +3.2 equal-weighted (computed from `vintage_matched_nowcast_market.csv`).
- **Statistical:** 10 scored quarters; 2560 cells; the reported ratios are the family's typical value (0.65 to 0.75), not the best cell (0.60). A 2024Q1+ correlation of 0.3 to 0.5 means the OLS slope is set mostly by the 2023 normalisation.

## 5. Next evidence

1. **September 2026 dumps** (Inside Airbnb publishes most markets around the 10th to the 30th of each month) would close the August half-month and give the first September days; re-run E1 with the probe, E2, then E3 to E7. Everything is checkpointed; a rerun after new files land takes about ten minutes.
2. **Re-run on 5 Nov** with the print: add 3Q26 to the walk-forward and see whether the 0.68 survives an eleventh quarter. If the print is inside 8.6 to 11.5 the index did its job; if the ratio moves above 0.8 the signal is what note 08 found for every other composite.
3. **Reviews per stay** could be bounded from the 13-city listings dumps (number_of_reviews_ltm vs availability or estimated nights) to test whether propensity drifted in 2025 to 2026; not done here.
4. **Do not** widen the panel with agent-scraped listings; the quote index test (8 Sep) showed scraped quantities reproduce the dump's composition.

## 6. Files

Scripts: `analysis/src/q3nowcast/E1_inventory_and_discover.py`, `E2_download_reviews.py`, `E3_review_counts.py`, `E4_build_index.py`, `E4b_stable_listing.py`, `E5_backtest.py`, `E6_nowcast.py`, `E7_report.py`.

Outputs in `data/processed/q3nowcast/E/` (cache/ with 363 parquet and daily files, 186 MB, is not committed and is rebuilt by E3):
- `inventory.csv` (832 rows: 363 reviews files, 334 13-city listings dumps, Theo artifacts), `cdn_probe_reviews.csv`, `download_plan.csv`, `download_manifest.csv` (240 files, url, bytes, sha256), `download_gaps.csv` (empty).
- `market_vintage_monthly.csv` (49,243 rows), `market_vintage_daily.csv` (697,888 rows, 37 MB), `market_geo.csv`.
- `survivorship_wedge.csv` (47,105 pairs), `posting_lag_curve.csv`, `posting_completeness_curve.csv`.
- `market_monthly_yoy.csv`, `region_monthly_index.csv`, `global_monthly_index.csv`, `index_quarterly.csv` (five measures, six region rows), `coverage_monthly.csv`, `stable_listing_yoy_market.csv`, `stable_listing_index.csv`.
- `backtest_abnb_quarterly.csv` (2,560 tests), `backtest_wf_paths.csv`, `backtest_survivor_robustness.csv`, `backtest_eurostat_monthly.csv` (74 tests), `backtest_scoreboard.csv`.
- `partial_window_yoy_market.csv`, `partial_window_yoy_index.csv`, `monthly_nowcast_2026_market.csv`, `monthly_nowcast_2026.csv`, `vintage_matched_nowcast_market.csv`, `vintage_matched_nowcast.csv`, `partial_vs_full_quarter_market.csv`, `partial_vs_full_quarter.csv`, `q3_2026_nowcast.csv`, `q3_2026_coverage.csv`.

Raw (main tree, gitignored): `C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_reviews\`, 363 `<country>_<region>_<market>_<date>_reviews.csv.gz`, 24 GB. Source: Inside Airbnb, https://insideairbnb.com/get-the-data/, CC-BY 4.0. Logs: `logs/E3_full.log`, `E5_full.log`, `E6_full.log`, `E7_full.log`.
