# M. New-listing price premium as a composition term for ex-FX ADR

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code). Workstream M of the ADR v3 run (`docs/adrv3/BRIEF.md`).
- **Question:** Workstream E found that same-listing review volume in mature markets is falling 3 to 7 percent y/y and that all growth comes from listings under a year old; J found hosts do not reprice existing dates. If realised ADR growth comes from composition, a term the current mix set lacks is the price of new listings relative to incumbents times the change in the share of stays they take. Does such a term exist with eight or more quarters of history, and does adding it to the measured mix lower the S-harness RMSE on both windows?
- **Scripts (`analysis/src/adrv3/`, `py -3.13`, run in order):** `M1_dump_census.py` (334 dumps, 2 minutes, writes a 204 MB cache), `M2_new_listing_premium.py` (2 minutes), `M3_new_listing_share.py`, `M4_term_quarterly.py`, `M5_score_harness.py`, `M6_term_3q26.py` (seconds each).
- **Outputs (`data/processed/adrv3/M/`):** `M1_dump_census.csv`, `M2_new_listing_premium.csv`, `M2_new_listing_premium_region.csv`, `M2_premium_summary_by_period.csv`, `M3_new_listing_share.csv`, `M3_new_listing_share_region.csv`, `M3_attrition_wedge.csv`, `M3_listings_dump_share.csv`, `M4_term_quarterly.csv`, `M4_premium_by_region_quarter.csv`, `M4_feature_tests.csv`, `M5_scores.csv`, `M5_criterion.csv`, `M5_paths.csv`, `M6_term_3q26.csv`.
- **Does not redo:** the residual rules, the other mix terms, the FX estimators, the S harness, E's index or J's calendar panel. Nothing under `adrq3/`, `q3nowcast/` or `adrv3/S*` was touched. No same-listing price panel was built and nothing was scraped.

---

## 1. Bottom line

1. **Verdict: FAIL on the pre-registered criterion.** The term exists with 14 quarters of history (1Q23 to 2Q26, plus 3Q26 to date), so the history condition is met, but adding it to the measured mix at the mechanical elasticity does not lower the S-harness RMSE on both windows. On the primary specification, fixed before any score was seen (all-rooms unweighted hedonic premium pooled by region with market fixed effects, review-weighted regional change in the new-listing share, FY25 nights weights), target-2 RMSE is lower on 2 of the 4 checks: eur 1Q24-2Q26 1.116 against the last_q baseline's 1.099 (worse), eur 2Q24-2Q26 0.928 against 0.935 (better), baskets 1Q24-2Q26 0.836 against 0.831 (worse), baskets 2Q24-2Q26 0.766 against 0.783 (better). Target 1 is unchanged to three decimals (0.894 / 0.882). One sensitivity, the stay-weighted (l30d-review-weighted) premium, is lower on all four checks by 0.003 to 0.009 pp of RMSE; that is under one percent of the RMSE, smaller than the change from any other specification detail, and it is not the pre-declared specification, so it is reported as noise, not as a pass. The term is a memo line for P, not a point input. (descriptive, walk-forward 1Q24-2Q26 n 10 and 2Q24-2Q26 n 9)

2. **The premium has the wrong sign for the story and is small.** Listings under a year old (by `first_review`) are priced below incumbents of the same room type, capacity and bedroom count in the same market. On the 2025 listed-rate basis (1Q25-3Q25, 28 markets, 261k new and 625k older priced listings) the pooled hedonic premium is -5.6 log points globally: EMEA -8.8 (3 markets), NA -6.4 (6), LatAm -3.1 (5), APAC -2.3 (14). On the 2026 stay-quote basis (1Q26-3Q26, 33 markets, 606k new and 1.65m older) it is -1.9 globally: EMEA -5.4, LatAm -2.8, APAC -0.7 and NA +3.6. The quote-basis number is a different object from the listed-basis number (a quoted stay on selected dates versus a host's default nightly rate; the 8 September test found a 20 to 70 pp market-specific wedge between the two) and the two are never differenced here. Weighting by last-30-day reviews, which is closer to what enters ADR, pulls the premium toward zero (global -4.0 listed, -1.4 quote): the new listings that actually get booked are priced nearer incumbents than the average new listing. Rome is the one long series and it moved: +9 to +13 log points through mid-2023, -1 by December 2023, -8 in 2024, -12 in 2025, then -1 to -5 on the 2026 quote basis. (descriptive)

3. **The new-listing share of stays rose through mid-2024 and has fallen since.** Reviews from listings under 12 months old were 31 to 32 percent of all reviews in 2023 and 1H24 across E's 123 markets, 29 percent in 2025 and 2026. The y/y change was +0.5 to +4.2 pp through 2Q24 (within-vintage, deep lag, biased upward by the attrition wedge), -0.2 to -1.0 pp in 3Q24-2Q25 (mixed lag), and -2.3, -1.7, -0.9, -1.5 pp in 3Q25-2Q26 on the vintage-matched construction, with 3Q26 to date (July) at -1.8 pp: EMEA -3.8, APAC -2.0, NA -0.7, LatAm +0.6. The attrition wedge on the share is -1.8 to -2.3 pp per year of dump lag (same market-quarter seen a year later in a later dump), so the 2023 to 1H24 rise is overstated by one to two points and the direction since mid-2024 is robust. The lag-zero cross-check from the listings dumps' `number_of_reviews_l30d` agrees in direction market by market (Paris 52 to 28 percent, Rome 36 to 21, Austin 36 to 29, Tokyo 45 to 39, London 43 to 40; Sydney 37 to 41 and Mexico City 30 to 36 up). (descriptive)

4. **The term is an order of magnitude below the other mix terms.** Premium times share change gives a global contribution between -0.02 and +0.20 pp of ex-FX ADR y/y in every quarter (mean absolute value 0.08 pp; mean absolute quarterly change 0.05 pp against 0.82 pp for the residual). H's geographic mix runs -0.9 to -1.9 pp, unit size +0.3 to +1.0, LOS +0.1 to +0.5, new business -0.2 to -0.5, the residual +0.8 to +4.9. The largest term values, +0.20 in 4Q23 and +0.16 in 3Q25, are a tenth of the residual's move in the same quarters. Because new listings are cheaper, the fall in their share since mid-2024 is a small positive for ADR, +0.03 to +0.16 pp a quarter; it is not where the 2 to 5 pp residual comes from. (descriptive; the elasticity of one is assumed)

5. **What this says about where realised ADR growth comes from.** Composition through listing age is not it. E's finding that volume growth in mature markets comes from new listings is a volume fact; those new listings are priced 2 to 9 log points below incumbents, so their growth carried a mild price drag in 2023 to 1H24 (-0.1 to -0.3 pp in NA, where the premium was most negative) and a mild lift since, as their share fell. Realised ex-FX ADR accelerated from +1 in 1H25 to +4 in 1H26 while the new-listing share was falling by 1 to 2 pp and the term was adding 0.03 to 0.07 pp. Whatever moved the residual in 1H26 (K's fee-migration reprice, like-for-like pricing on incumbents, sub-regional mix, or expansion markets the Inside Airbnb panel does not hold) is not the new-listing mix. One correlation deserves a sentence: the share change is negatively related to the residual (primary term r -0.33, perm p 0.27; wedge-corrected variant r -0.68, p 0.009, walk-forward 0.66 to 0.89 vs naive), and the expanding walk-forward coefficient on the term is -9 to -15, the wrong sign for a composition mechanism and ten times its mechanical size. That is a correlation of falling new supply with rising incumbent pricing (fewer entrants, firmer prices), consistent with a supply-tightening reading of E's same-listing decline, and it is not this term. It is not promoted: the wedge-corrected series carries a construction step at 3Q24 where the correction switches on, the coefficient is fitted on ten points, and the S-harness variant using it at elasticity one is worse than the baseline on all four checks (0.874 to 1.142 against 0.783 to 1.099). (descriptive; the supply reading is a hypothesis)

6. **3Q26 to date: +0.05 pp, band +0.02 to +0.07; 4Q26 carried at the same value.** Quote-basis premiums from the July and August 2026 dumps (EMEA -4.7, NA +3.8, LatAm -2.0, APAC +0.3 log points, standard errors 0.2 to 0.3) times the July 2026 share change against July 2025 on the vintage-matched construction (120 markets). EMEA supplies all of it (+0.18); NA, LatAm and APAC are -0.03 to -0.01. The 2Q26 value on the same specification is +0.07. The band is the range across the eight specification variants plus one standard error on the premiums, and the share is one month of the quarter. (descriptive point; assumed band)

---

## 2. Tables

### 2.1 Dump census: what carries a price and on which basis (`M1_dump_census.csv`, sourced)

334 listings dumps, 34 markets (the 13-city parquet panel plus 21 csv-only markets held for the quote-index test), December 2022 to August 2026.

| basis | dumps | markets | vintages | how the basis was set |
|---|---|---|---|---|
| listed nightly rate (`price`) | 109 | 31 | Dec 2022 to Oct 2025 | `price_basis` column in the 13-city parquet; for csv-only markets, `price` populated and dump before Nov 2025 |
| none | 70 | 32 | Sep 2025 (Paris, Sydney, Melbourne), Nov 2025 to Feb 2026 all markets, Mar 2026 (Chicago, Nashville, San Diego) | `price` empty |
| stay quote per night (`price_quote_price_per_night`, also written to `price`) | 155 | 34 | Mar 2026 to Aug 2026 | quote columns populated |

`first_review` is populated for 49 to 96 percent of listings per dump (the rest have never been reviewed and have not traded); `host_since` for 98 to 100 percent. `number_of_reviews_l30d` and `_ltm` are present in every dump. Scope: the Dec 2025 to May 2026 monthly releases are partial-scope (memory) and 40 of the 114 in that window carry under 80 percent of the market's full-scope count; they are flagged and the full-scope-only premium is a sensitivity (it changes the pooled premium by under 1 log point). 257 dumps meet the premium sample floor (100 priced new and 300 priced older listings).

### 2.2 New-listing price premium by region and basis (`M2_premium_summary_by_period.csv`, descriptive)

Pooled hedonic coefficient on new (< 12 months by `first_review`) in log price with market fixed effects, room-type dummies, log accommodates and bedrooms, prices trimmed to the 1st to 99th percentile per dump; mean over the period's quarters; n is the sum over quarters of priced listings in the regression. Regional premiums on the quote basis in 3Q26 carry standard errors of 0.2 to 0.3 log points; the spread across variants, not the standard error, is the uncertainty.

| period, basis | region | markets | hedonic, log pts (min to max over quarters) | l30d-review weighted | entire home only | raw median premium, % | n new | n older |
|---|---|---|---|---|---|---|---|---|
| 2023, listed (Rome only) | EMEA | 1 to 2 | +8.6 (+5.9 to +12.9) | +0.2 | +9.0 | +6.8 | 46,569 | 115,614 |
| 2024, listed | NA (Austin, Nashville) | 2 | -11.9 (-15.4 to -9.5) | -4.8 | -12.6 | -7.3 | 13,175 | 32,797 |
| 2024, listed | EMEA (Paris, Rome) | 2 | -7.1 (-8.6 to -6.0) | -7.6 | -6.4 | -6.1 | 103,010 | 174,518 |
| 2024, listed (Dec only) | APAC | 6 | +0.9 | -0.5 | +1.0 | n/a (mixed currencies) | 17,473 | 33,888 |
| 1Q25-3Q25, listed | NA | 6 | -6.4 (-6.5 to -6.0) | -1.5 | -6.3 | +1.3 | 46,808 | 134,532 |
| 1Q25-3Q25, listed | EMEA | 3 | -8.8 (-8.8 to -8.7) | -9.2 | -8.8 | -7.0 | 70,954 | 152,583 |
| 1Q25-3Q25, listed | LatAm | 5 | -3.1 (-5.5 to +0.2) | -4.5 | -3.9 | -3.4 | 64,839 | 152,590 |
| 1Q25-3Q25, listed | APAC | 14 | -2.3 (-3.1 to -1.8) | -0.5 | -1.7 | n/a | 78,879 | 185,595 |
| 1Q25-3Q25, listed | global, market FE | 28 | -5.6 (-5.8 to -5.3) | -4.0 | -5.5 | n/a | 261,480 | 625,300 |
| 1Q26-3Q26, quote | NA | 7 | +3.6 (+3.0 to +4.2) | +0.9 | +3.5 | +19.8 | 96,883 | 351,897 |
| 1Q26-3Q26, quote | EMEA | 4 | -5.4 (-6.7 to -4.7) | -3.1 | -6.4 | -3.4 | 177,663 | 525,328 |
| 1Q26-3Q26, quote | LatAm | 7 | -2.8 (-4.0 to -2.0) | -2.8 | -2.8 | n/a | 183,902 | 402,723 |
| 1Q26-3Q26, quote | APAC | 15 | -0.7 (-1.5 to +0.3) | +0.7 | -0.1 | n/a | 147,361 | 370,548 |
| 1Q26-3Q26, quote | global, market FE | 33 | -1.9 (-2.9 to -1.1) | -1.4 | -2.2 | n/a | 605,809 | 1,650,496 |

The raw median premium pools local currencies within a region and is only readable where the region is one currency (NA, EMEA euro and sterling markets are mixed but close). The NA quote-basis premium is positive because of Los Angeles (+4.6) and New York (+7.6, where the October 2025 listed-basis reading was already +1.9 against Austin's -15); Austin (-5.9) and Chicago (-2.3) stay negative. Using `host_since` instead of `first_review` gives -3.9 (APAC) to -9.0 (EMEA) on the 2025 listed basis, the same picture with more noise, because a multi-listing host's new listing is not new by `host_since`.

### 2.3 New-listing share of stays and its y/y change (`M3_new_listing_share_region.csv`, descriptive)

Share of reviews in the quarter from listings whose first review in the same dump is under 12 months earlier, review-weighted across E's markets (NA 42, EMEA 56 to 57, LatAm 5 to 7, APAC 17), global on FY25 nights weights. Construction: vintage-matched (both the quarter and its year-ago quarter within 13 months of a dump, symmetric attrition), mixed lag, or within-vintage deep (both from the 2025 dump, more than 13 months back).

| quarter | share, % global | NA | EMEA | LatAm | APAC | y/y change, pp global | NA | EMEA | LatAm | APAC | construction |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1Q23 | 30.9 | 32.8 | 27.6 | 38.6 | 26.8 | +4.2 | +2.4 | +3.3 | +8.5 | +5.4 | within-vintage deep |
| 2Q23 | 31.1 | 31.1 | 27.6 | 41.0 | 28.6 | +3.4 | +0.6 | +2.0 | +8.3 | +7.0 | within-vintage deep |
| 3Q23 | 31.4 | 30.2 | 27.4 | 42.5 | 31.1 | +2.5 | -1.1 | +1.2 | +7.0 | +8.1 | within-vintage deep |
| 4Q23 | 31.8 | 29.9 | 28.9 | 41.8 | 31.3 | +1.7 | -2.7 | +2.2 | +4.8 | +6.6 | within-vintage deep |
| 1Q24 | 32.0 | 29.6 | 30.2 | 41.0 | 31.5 | +1.1 | -3.2 | +2.6 | +2.4 | +4.7 | within-vintage deep |
| 2Q24 | 31.7 | 28.9 | 29.3 | 41.2 | 32.5 | +0.5 | -2.2 | +1.7 | +0.2 | +3.9 | within-vintage deep |
| 3Q24 | 31.2 | 28.7 | 28.4 | 40.4 | 32.8 | -0.2 | -1.6 | +1.1 | -2.1 | +1.7 | mixed lag |
| 4Q24 | 31.4 | 29.0 | 30.0 | 38.9 | 31.4 | -0.4 | -0.9 | +1.1 | -2.9 | +0.1 | mixed lag |
| 1Q25 | 31.2 | 29.1 | 30.4 | 37.3 | 30.5 | -0.8 | -0.5 | +0.3 | -3.7 | -1.0 | mixed lag |
| 2Q25 | 30.7 | 28.4 | 28.5 | 38.6 | 32.0 | -1.0 | -0.5 | -0.9 | -2.6 | -0.5 | mixed lag |
| 3Q25 | 28.8 | 26.2 | 25.6 | 38.7 | 31.0 | -2.3 | -2.4 | -2.8 | -1.7 | -1.8 | vintage-matched (mixed lag for 3 markets) |
| 4Q25 | 29.7 | 27.2 | 27.6 | 38.4 | 30.1 | -1.7 | -1.8 | -2.4 | -0.6 | -1.4 | vintage-matched |
| 1Q26 | 30.3 | 28.2 | 28.3 | 39.3 | 29.5 | -0.9 | -0.8 | -2.2 | +2.0 | -0.9 | vintage-matched |
| 2Q26 | 29.2 | 28.0 | 24.5 | 39.8 | 31.0 | -1.5 | -0.4 | -4.0 | +1.2 | -1.0 | vintage-matched |
| 3Q26 to date (July) | 29.1 | 28.7 | 24.7 | 37.6 | 31.1 | -1.8 | -0.7 | -3.8 | +0.6 | -2.0 | vintage-matched, 120 markets |

Attrition wedge (`M3_attrition_wedge.csv`): the same market-quarter read from a dump a year later shows a new-listing share lower by 2.0 pp (NA, 320 pairs), 2.3 (EMEA, 444), 1.7 (LatAm, 40) and 1.8 (APAC, 136), review-weighted. Applying it to the deep-lag side of the mixed-lag quarters moves 3Q24 to 2Q25 from -0.2 / -1.0 to -2.4 / -3.5 pp (`d_share_wedge_corrected_rw_pp`); the truth for those four quarters is between the two because attrition slows with depth (E table 2.2).

### 2.4 The term by quarter (`M4_term_quarterly.csv`, pp of ex-FX ADR y/y, descriptive under an assumed elasticity of one)

| quarter | primary, global | NA | EMEA | LatAm | APAC | range across 7 variants | premium source |
|---|---|---|---|---|---|---|---|
| 1Q23 | +0.14 | -0.22 | +0.27 | +0.62 | +0.05 | -0.01 to +0.35 | EMEA measured; NA, LatAm, APAC carried back from their first listed dump |
| 2Q23 | +0.19 | -0.06 | +0.26 | +0.61 | +0.06 | +0.03 to +0.44 | same |
| 3Q23 | +0.16 | +0.10 | +0.08 | +0.51 | +0.07 | -0.02 to +0.16 | same |
| 4Q23 | +0.20 | +0.26 | +0.13 | +0.35 | +0.06 | -0.06 to +0.20 | same |
| 1Q24 | +0.08 | +0.31 | -0.16 | +0.18 | +0.04 | -0.07 to +0.11 | same |
| 2Q24 | +0.03 | +0.21 | -0.11 | +0.01 | +0.04 | -0.05 to +0.06 | NA measured from here |
| 3Q24 | -0.01 | +0.17 | -0.09 | -0.16 | +0.02 | -0.02 to +0.14 | |
| 4Q24 | -0.02 | +0.14 | -0.08 | -0.21 | +0.00 | -0.02 to +0.17 | all measured |
| 1Q25 | +0.00 | +0.03 | -0.02 | -0.01 | +0.02 | +0.00 to +0.15 | all measured |
| 2Q25 | +0.06 | +0.03 | +0.08 | +0.11 | +0.01 | +0.04 to +0.21 | all measured |
| 3Q25 | +0.16 | +0.16 | +0.25 | +0.09 | +0.06 | +0.13 to +0.19 | all measured, last listed-basis quarter |
| 4Q25 | +0.07 | -0.03 | +0.21 | +0.03 | +0.00 | +0.04 to +0.09 | premium carried from 3Q25 (no price in any dump) |
| 1Q26 | +0.03 | -0.04 | +0.15 | -0.08 | +0.01 | +0.01 to +0.05 | quote basis, measured |
| 2Q26 | +0.07 | -0.01 | +0.20 | -0.03 | +0.01 | +0.03 to +0.07 | quote basis, measured |
| 3Q26 to date | +0.05 | -0.03 | +0.18 | -0.01 | -0.01 | +0.02 to +0.07 | quote basis, measured; share July only |

Note-08 feature tests (`M4_feature_tests.csv`, walk-forward from 1Q24, n 10): primary term level against the residual r -0.33 (perm p 0.27), ratio vs naive 1.59; first difference r -0.28, ratio 0.94; against ex-FX ADR 1.49 and 1.07. The stay-weighted premium variant: 1.42 and 0.88. The wedge-corrected share variant is the only one under 1 on levels: r -0.68 (p 0.009), 1.18 vs the residual and 0.89 vs ex-FX; first differences 0.66 and 0.75. Its sign is negative and it carries the 3Q24 construction step, see bottom line 5.

### 2.5 S-harness scores (`M5_scores.csv`, `M5_criterion.csv`, descriptive, walk-forward)

Baseline is the pre-registered v3 model (measured mix, prior-year fills, last-quarter residual). With the term: residual net of the term follows the last-quarter rule and the measured quarter-t term is added, which equals the baseline plus the term's first difference. RMSE in pp; ratio is vs naive; jackknife is the drop-one maximum of that ratio.

| model | t2 eur 1Q24- RMSE / ratio / jk max | t2 eur 2Q24- | t2 baskets 1Q24- | t2 baskets 2Q24- | t1 1Q24- / 2Q24- RMSE | RMSE lower than baseline on the 4 t2 checks | M criterion |
|---|---|---|---|---|---|---|---|
| baseline last_q | 1.099 / 0.916 / 0.969 | 0.935 / 0.905 / 0.989 | 0.831 / 0.876 / 0.918 | 0.783 / 0.871 / 0.924 | 0.894 / 0.882 | | |
| **+ term, primary** | 1.116 / 0.931 / 0.982 | 0.928 / 0.898 / 0.974 | 0.836 / 0.881 / 0.923 | 0.766 / 0.853 / 0.901 | 0.894 / 0.882 | 2 of 4 | **not met** |
| + term, l30d-weighted premium | 1.096 / 0.914 / 0.965 | 0.930 / 0.900 / 0.979 | 0.825 / 0.870 / 0.910 | 0.774 / 0.861 / 0.911 | 0.894 / 0.882 | 4 of 4, by 0.003 to 0.009 pp | sensitivity only |
| + term, entire-home premium | 1.113 / 0.929 / 0.978 | 0.927 / 0.897 / 0.972 | 0.833 / 0.879 / 0.922 | 0.766 / 0.852 / 0.899 | 0.894 / 0.882 | 2 of 4 | not met |
| + term, equal-weighted share | 1.108 / 0.924 / 0.974 | 0.926 / 0.897 / 0.973 | 0.830 / 0.875 / 0.915 | 0.767 / 0.854 / 0.902 | 0.894 / 0.882 | 3 of 4 | not met |
| + term, full-scope premium | 1.120 / 0.934 / 0.983 | 0.933 / 0.903 / 0.976 | 0.838 / 0.883 / 0.924 | 0.769 / 0.856 / 0.902 | 0.894 / 0.882 | 2 of 4 | not met |
| + term, global pooled premium | 1.134 / 0.946 / 1.000 | 0.940 / 0.910 / 0.990 | 0.856 / 0.903 / 0.947 | 0.783 / 0.872 / 0.922 | 1.049 / 0.882 | 0 of 4 | not met |
| + term, wedge-corrected share | 1.142 / 0.953 / 1.007 | 0.967 / 0.936 / 1.021 | 0.874 / 0.922 / 0.964 | 0.816 / 0.908 / 0.961 | 0.894 / 0.882 | 0 of 4 | not met |
| + term, vintage-matched-only share | history 4 quarters, ineligible | | | | | | not met |

The walk-forward-coefficient sensitivity (baseline plus beta times the term change, beta fitted on prior quarters) is worse than the baseline for the primary term (ratios 1.05 to 1.22; beta -9 to -12) and better for the wedge-corrected term (0.70 to 0.81; beta -10 to -15). A coefficient of -10 on a term whose mechanical coefficient is +1 is not the composition mechanism and is not promoted.

The strict v3 criterion (ratio under 1 and jackknife maximum under 1 on the four target-2 checks) is met with the term added for the primary and most variants, because the baseline already meets it and the term barely moves the paths; that is not evidence for the term.

### 2.6 3Q26 to date (`M6_term_3q26.csv`)

| region | premium, log pts (SE) | basis | share change, pp (July 2026 vs July 2025) | term, pp |
|---|---|---|---|---|
| NA | +3.8 (0.3) | quote | -0.7 | -0.03 |
| EMEA | -4.7 (0.2) | quote | -3.8 | +0.18 |
| LatAm | -2.0 (0.2) | quote | +0.6 | -0.01 |
| APAC | +0.3 (0.2) | quote | -2.0 | -0.01 |
| **global, FY25 weights** | | | -1.8 | **+0.05, band +0.02 to +0.07** |
| memo: 2Q26, same specification | | | -1.5 | +0.07 |
| 4Q26 | carried | | | +0.05, same band (assumed) |

---

## 3. Method

1. **Census and cache (M1).** Every `*_listings.parquet` (13 cities) or `*_listings.csv.gz` (21 further markets) in the main-tree raw store is read once with the columns needed (id, host_since, first_review, room_type, accommodates, bedrooms, price, price_quote_*, review counts), the price string parsed, the basis set from the parquet `price_basis` column or the BRIEF rule for csv-only markets, and a slim parquet written per dump to `data/processed/adrv3/M/cache/` (334 files, 204 MB, not committed; M1 rebuilds it in two minutes). Region for the 21 csv-only markets is assigned in the script (APAC 16, LatAm 7, EMEA 4, NA 7 overall).
2. **Listing age.** `first_review` (dump date minus first review, new if under 365 days) because it dates the listing's first stay, which is when it starts contributing nights and a price to ADR. `host_since` dates the host account, so a second listing from a five-year host is old by that field and new by trading; it is run as a sensitivity. Never-reviewed listings (4 to 51 percent of a dump, the high end in partial-scope releases) are excluded from the premium: they have no realised price and no nights.
3. **Premium (M2).** Per market x vintage and pooled per region x quarter x basis (market fixed effects): OLS of log price on the new dummy, room-type dummies, log accommodates and bedrooms, HC0 standard errors, prices trimmed to the 1st to 99th percentile per dump. Variants: weighted by `number_of_reviews_l30d` (listings with no review in the last 30 days drop out; the weight is a stay proxy), entire home only, full-scope dumps only. Bases are fitted separately and never differenced across the Dec 2025 to Feb 2026 gap. The regional premium used in the term is the quarter's own pooled coefficient where a dump exists; 4Q25 carries 3Q25 (the two or three October 2025 listed-basis dumps per region are a different panel and are not used); quarters before a region's first priced dump carry its earliest coefficient backward (NA before 2Q24, LatAm and APAC before 4Q24; flagged in `M4_premium_by_region_quarter.csv`).
4. **Share (M3).** From E's `market_vintage_monthly.csv` (listing x month counts already summarised as all reviews and reviews by listings 12+ months old in the same dump): new = all minus mature12, summed to quarters, the dump month dropped. For each market-quarter the dump with the smallest lag whose months all precede the dump month is used, and the y/y change pairs the quarter with its year-ago quarter under the same rule; the construction flag records whether both sides are within 13 months of a dump. The attrition wedge is measured on the 940 market-quarters seen in two dumps about 12 months apart. Regional aggregation is review-weighted (and equal-weighted, and median), global on the FY25 nights weights given in the brief (NA 31.4, EMEA 36.8, LatAm 17.0, APAC 14.9; E's own weights are 28.3 / 41.6 / 17.9 / 12.3 and the choice does not change any conclusion). The listings-dump cross-check (`M3_listings_dump_share.csv`) is the share of `number_of_reviews_l30d` from listings under 365 days by `first_review` at each dump, lag zero by construction, with the scope flag.
5. **Term (M4).** term_r(t) = premium_r(t) / 100 x d_share_r(t), global = weighted sum. With ADR = s P_new + (1 - s) P_old, the derivative of log ADR with respect to s is (P_new - P_old) / ADR, the premium in log points to first order, so a 1 pp share change at a -5 log point premium is -0.05 pp of ADR y/y. This assumes the listed or quoted price gap between age groups equals the realised gap (assumed; new-listing promotions and first-booking discounts are not in the listed price, which would make the realised premium more negative and the term slightly larger). Correlations and note-08 walk-forward via `I0_protocol.score`, unchanged.
6. **Scoring (M5).** `S.exfx_from_residual(last_q on residual minus term, "measured", extra_pp=term)` scored with `S.score` on both targets, both windows, three FX estimators, jackknife; baseline `S.v2_model_paths()["v2_measured_last_q"]`; criterion read on target 2 under eur and baskets. A lagged-term variant equals the baseline algebraically and is not scored separately. The walk-forward-beta sensitivity fits an expanding OLS of the residual change on the term change strictly before each scored quarter (minimum four pairs).
7. **3Q26 (M6).** Primary point from M4; band = min and max across the eight M4 variants and plus or minus one standard error on each regional premium.

---

## 4. What this can and cannot identify

- **Can:** that new listings in 34 mature markets are priced at or below incumbents on both bases after room-type, capacity and bedroom controls; that the share of stays they take in 123 mature markets peaked around mid-2024 and has fallen 1 to 2 pp a year since, with survivorship measured rather than assumed; that the product of the two is 0.0 to 0.2 pp of ADR y/y and does not move the S harness. The null is well-measured: 261k to 606k new listings per basis, standard errors of 0.2 to 0.6 log points per region-quarter.
- **Cannot: the realised premium.** Both bases are asking prices (J: unchanged y/y on 72 to 77 percent of calendar dates; the 8 September test: quotes do not track disclosed ADR). A new listing that lists at -6 percent and then discounts its first bookings a further 20 percent realises a larger discount than measured; a new listing that lists high and gets no bookings contributes no nights. The stay-weighted premium (nearer zero) is the better guide to what enters ADR, and the term built on it is the one variant that clears the RMSE bar, by an amount that is noise.
- **Cannot: the 2023 to 1H24 share change without bias.** Only one dump vintage (2025) sees those quarters, at 13 to 42 months of lag; the wedge is measured only between lags of 1 to 13 and 13 to 25 months. The raw and wedge-corrected series bracket the truth and the term's sign does not depend on which is used.
- **The panel is the wrong footprint for a global mix term.** Inside Airbnb holds regulated cities and tourist regions in NA, Europe and Australia; Airbnb's growth and its fastest ADR moves are in expansion markets. The new-listing share in those markets is unobserved and could be rising while it falls here. The regional weights spread a mature-market measurement over the whole company.
- **The negative share-residual correlation is not identified.** It is consistent with fewer entrants allowing incumbents to price up (a supply story), with regulation removing cheap new supply in Paris, Barcelona and New York while their ADR rose, or with chance on 14 points. The wedge-corrected variant that carries it has a construction step in 3Q24, and its fitted coefficient has the wrong sign and ten times the size for the composition mechanism. It is a lead for a supply-growth term, not evidence for this one.
- **Carried premiums.** Eight of the 15 term quarters use a carried-back or carried-forward regional premium for at least one region; the term's values in 2023 depend on Rome's positive 2023 premium spread over EMEA and on carried NA, LatAm and APAC premiums. None of that matters for the scored window (1Q24 onward), where NA is measured from 2Q24, EMEA throughout, LatAm and APAC from 4Q24, and 4Q25 is the only carried quarter.

---

## 5. Next evidence

1. **P should carry the term as a memo line, +0.05 pp in 3Q26 and 4Q26 with a +0.02 to +0.07 band, not in the point.** It does not meet the M criterion and its size is inside the rounding of the ex-FX print.
2. **A supply-growth term is the lead this note leaves.** The share change (or E's same-listing decline, or the listing count itself) moving opposite to the residual with a coefficient near -10 is a different mechanism from composition and would need its own pre-registered test on the S harness with a stated sign and size before fitting. K (fee migration) and L (regional residual) are nearer the 1H26 step than this is.
3. **September 2026 dumps (T) add August to the 3Q26 share and a fourth quote-basis quarter to the premium.** Re-run M1 (cache only rebuilds new files), M2, M3, M4, M6; M5 does not change until the 5 November print adds a scored quarter.
4. **The realised premium needs a realised-rate source**, the same conclusion as the quote-index test and J section 5; nothing in Inside Airbnb after May 2025 carries a transaction price.

---

## 6. Files

| File | Contents |
|---|---|
| `analysis/src/adrv3/M1_dump_census.py` | census of 334 dumps, basis rule, scope flag, slim per-dump cache |
| `analysis/src/adrv3/M2_new_listing_premium.py` | per-dump and pooled hedonic premiums, three variants, two age fields |
| `analysis/src/adrv3/M3_new_listing_share.py` | share of stays from listings under 12 months, three constructions, wedge, regional and global aggregates, listings-dump cross-check |
| `analysis/src/adrv3/M4_term_quarterly.py` | premium path per region with source flags, the term by variant, correlations and note-08 tests |
| `analysis/src/adrv3/M5_score_harness.py` | S-harness scoring of baseline and every variant, criterion table, paths |
| `analysis/src/adrv3/M6_term_3q26.py` | 3Q26 to date point and band, 4Q26 carried |
| `data/processed/adrv3/M/M1_dump_census.csv` | 334 rows: market, region, date, quarter, format, n, basis, price and age-field coverage, new-listing counts and l30d shares, scope flag, usable flag |
| `data/processed/adrv3/M/M2_new_listing_premium.csv` | 637 market x vintage cells (all rooms, entire home, host_since) with medians, means, hedonic premium and SE, weighted variant, n |
| `data/processed/adrv3/M/M2_new_listing_premium_region.csv` | region and global x quarter x basis x variant x scope, pooled with market FE, n and markets |
| `data/processed/adrv3/M/M2_premium_summary_by_period.csv` | table 2.2 |
| `data/processed/adrv3/M/M3_new_listing_share.csv` | 1,842 market x quarter rows, 123 markets, 1Q23 to 3Q26, both sides' dump, lag, counts, share, y/y change raw and wedge-corrected, construction flag |
| `data/processed/adrv3/M/M3_new_listing_share_region.csv` | regional and global aggregates, all-markets and vintage-matched-only subsets |
| `data/processed/adrv3/M/M3_attrition_wedge.csv` | the wedge by region and by region x quarter, 940 pairs |
| `data/processed/adrv3/M/M3_listings_dump_share.csv` | lag-zero l30d and ltm shares per dump, 334 rows |
| `data/processed/adrv3/M/M4_term_quarterly.csv` | term by variant x region x quarter with premium, share change, sources |
| `data/processed/adrv3/M/M4_premium_by_region_quarter.csv` | the premium path used per variant with measured / carried flags |
| `data/processed/adrv3/M/M4_feature_tests.csv` | note-08 tests, 32 rows |
| `data/processed/adrv3/M/M5_scores.csv` | 136 S.score rows (baseline, 8 variants x 2 forms) with baseline RMSE, delta and ratio |
| `data/processed/adrv3/M/M5_criterion.csv` | the pass table per variant |
| `data/processed/adrv3/M/M5_paths.csv` | per-quarter ex-FX paths, actuals |
| `data/processed/adrv3/M/M6_term_3q26.csv` | table 2.6 |
| `data/processed/adrv3/M/cache/` (not committed, 204 MB) | 334 slim per-dump parquets; rebuilt by M1 |

Raw inputs (main tree, read-only, gitignored): `C:\Users\krish\citadel-abnb\data\raw\inside_airbnb\` (listings dumps). E's counts from the worktree copy of `data/processed/q3nowcast/E_aug/market_vintage_monthly.csv` and `market_geo.csv`. H components, seats dilution and the 07 interaction through `S1_scoring.load_inputs`.
