# E (August-batch refresh). Re-probe of the Inside Airbnb August 2026 batch: the store was already complete except Tokyo; the 3Q26 read does not move

**Date:** 2026-09-11 (probe, download and full E re-run on 2026-09-11, 15:20 to 15:35 local).
Author: Krishang Surapaneni (compiled with Claude Code), workstream E, August-batch refresh on branch `krish/aug-batch-refresh`.

**Question.** Workstream G reported an unlisted August 2026 batch on `data.insideairbnb.com` (86 of 122 markets, scrapes 10 to 31 Aug) of which the team's reviews store held only about 49, with Los Angeles, San Francisco, Chicago, Boston, London, Paris, Barcelona, Singapore, Sydney and Toronto missing. Does fetching the rest improve the reviews-based stays index (coverage, band, regional balance), and does the 3Q26 read move?

**Scripts.** `analysis/src/q3nowcast/E_aug1_probe.py` (HEAD probe, all 123 markets, every date 1 Aug to 11 Sep 2026, reviews then listings and calendar on live dates, back-off on CDN errors), `E_aug2_download.py` (downloads into the main-tree raw stores with sha256 manifest), `E_aug_run.py` (runs the committed E1, E3, E4, E4b, E5, E6, E7 unchanged with every output path redirected to `data/processed/q3nowcast/E_aug/`), `E_aug3_compare.py` (before/after table and the big-market table). Read `research/notes/q3nowcast/E_reviews-stays-index.md` first; this note only reports what changed.

---

## 1. Bottom line

1. **The premise was stale. The store already held the August batch.** The probe (5,655 HEAD requests, 374 live, zero errors, 75 seconds) finds exactly one August 2026 reviews dump for every one of the 123 markets and no September dump for any. 122 of the 123 were already in `C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_reviews` from the 12 Sep E2 run (the "49 of 86" count that motivated this task does not match the store; the ten named markets all had their August file). The 34 calendar-panel markets already had their August calendar and listings. The only hole was **Tokyo**: E1 probed `japan/kanto/tokyo` while the CDN path is `japan/kantō/tokyo` (macron), so every Tokyo probe returned 403 and Tokyo sat on a 30 Jun dump with no year-ago vintage. Fixed here: Tokyo 2026-08-31 (178 MB, 1.39 mm reviews, 31,305 listings) and Tokyo 2025-08-30 (124 MB) downloaded; sha256 in the manifest. Three other markets without a year-ago vintage (São Paulo, Bogotá, Nairobi) have no June 2025 dump on the CDN either, so they stay within-vintage only. (sourced)

2. **Coverage improved by one market, but a large one.** Markets with a full July and an August-to-date window: 111 to 112, 88.4 to 90.4 percent of the 3Q25 review base. Vintage-matched 3Q26-to-date panel: 119 to 120 markets, 94.1 to 96.1 percent of the base. All of the gain is APAC, where the July-plus-August panel goes from 50.5 to 67.7 percent of the region's 3Q25 base (Tokyo's 56,281 reviews in the quarter-to-date window are four times Sydney's). North America (36 of 42 markets in the August row, 78.3 percent of the NAM base) and EMEA (55 of 57, 97.8 percent) are unchanged because they were already complete; the six NAM and two EMEA markets outside the August row (New York, Los Angeles, San Francisco, Montreal, Portland, Albany, Venice, Vaud) have 10 to 13 Aug dumps whose 14-day trim ends before 1 Aug, and the re-probe confirms no later August dump exists for them. Only a September dump can close that. (descriptive)

3. **The APAC read moved, the global read barely.** Vintage-matched, review-weighted, 3Q26 to date: APAC +7.3 to +10.0 percent (equal-weighted +3.4 to +4.3); global +5.2 to +5.5 (equal-weighted +3.5 to +3.6, nights-share weighted +6.0 to +6.1). July: global +3.8 to +4.2; August to date: +8.2 to +8.5. Within-vintage global review-weighted 3Q26 to date +26.3 to +26.4. The within-vintage history also shifts a little because Tokyo's 2Q26 now enters the quarterly index (the 30 Jun dump could not close June): global all-reviews 2Q26 25.0 to 25.3, vintage-matched 2Q26 4.3 to 4.7, and the APAC vintage-matched history rises 1 to 5 pp in every quarter from 3Q25. Tokyo itself reads +18.9 percent vintage-matched for the quarter to date (July +20.3, August to 15 Aug +16.0), within-vintage +32.1, a 13 pp wedge that is below the panel median of 19. Tokyo is the strongest large APAC market in the panel by a wide margin (Sydney +3.7, Singapore +3.3). (descriptive)

4. **The backtest is unchanged, as it should be with the same history.** Global all-reviews review-weighted, nights, 2023Q1 window, lag 0: walk-forward RMSE ratio vs naive 0.683 to 0.681, r 0.86 both, wf RMSE 1.475 to 1.471 pp. Vintage-matched review-weighted 0.682 to 0.674. Scoreboard 2,560 tests, beat naive 463 to 465, best cell 0.600 to 0.601. Eurostat rows identical (Japan is not in Eurostat). The one visible change is APAC vintage-matched, 0.78 to 0.71 vs naive, which is the Tokyo history entering. (computed)

5. **3Q26 implied nights: no change to the call.** All-reviews review-weighted: +10.04 to +10.05, band 8.6 to 11.5 both runs. Equal 9.18 to 9.20, median 9.20 to 9.23, nights-share 9.34 to 9.35. Vintage-matched review-weighted 9.19 to 9.06 (the index rose 0.3 pp but the fitted slope fell from 0.322 to 0.312 because the whole vintage-matched history rose with Tokyo in it), equal 8.58 to 8.57, nights-share 8.69 to 8.68. Mean of the seven rows 9.17 to 9.16; anchored on the 2Q26 print 10.36 to 10.34; band width 1.56 to 1.55 pp. **3Q26 nights +9.5 percent, band 8.5 to 11.0, stands.** Comparison columns unchanged: naive 10.3, prior year 8.8, team baseline 9.9. (computed)

6. **What the batch did and did not buy.** It bought APAC coverage and a cleaner Tokyo series, and it settled that the reviews store is complete for August. It did not narrow the band (the band is the out-of-sample RMSE over 10 quarters, which Tokyo does not change), did not add any North American or EMEA market, and did not extend the August window for the twelve early-August markets. The read of the quarter is the same as on 12 Sep.

## 2. Tables

### 2.1 Probe and download (sourced)

| Item | Result |
|---|---|
| Markets probed | 123 (every market in `E/inventory.csv`), 1 Aug to 11 Sep 2026, reviews.csv.gz |
| Requests | 5,655 (5,409 reviews incl. 243 year-ago dates for Tokyo, São Paulo, Bogotá, Nairobi; 246 listings and calendar on live dates); 5,281 x 403, 374 x 200, 0 errors, 16 workers, 75 s |
| August 2026 reviews dumps live | 123 markets, one each, dates 10 to 31 Aug; 122 already held |
| September 2026 dumps live | 0 |
| Listings and calendar on the August dates | 123 each, live; the 34 panel markets' files already held (`14c_calendar_manifest.csv` 3Q26 rows) |
| Year-ago extension | Tokyo: 27 Jun, 29 Jul, 30 Aug, 29 Sep, 30 Oct 2025 all live; São Paulo, Bogotá, Nairobi: no June 2025 dump |
| Downloaded | `japan_kanto_tokyo_2026-08-31_reviews.csv.gz` 177,651,422 B sha256 755804ea…; `japan_kanto_tokyo_2025-08-30_reviews.csv.gz` 123,715,623 B sha256 a949918b…; 0 failures |
| Store after | 365 reviews files, 123 markets, 24.7 GB; 119 markets with three vintages, 4 with two |

The 2025-08-30 Tokyo vintage was chosen over the four others so that Tokyo's vintage-matched pair (366 days apart) matches the Aug 2025 to Aug 2026 construction used for the other 119 markets; the other four are recorded in `cdn_probe_aug2026.csv` and not downloaded.

### 2.2 Coverage before and after (descriptive; `before_after.csv`, block coverage)

| Metric | Before (12 Sep E run) | After | Change |
|---|---|---|---|
| Markets with an Aug 2026 dump | 122 | 123 | +1 (Tokyo) |
| Markets with July and Aug-to-date windows | 111 | 112 | +1 |
| Share of 3Q25 review base, those markets | 88.4% | 90.4% | +2.0 pp |
| Vintage-matched 3Q26-to-date markets | 119 | 120 | +1 |
| Share of 3Q25 base, vintage-matched | 94.1% | 96.1% | +2.0 pp |
| NAM in the Aug row (share of NAM base) | 36 (78.3%) | 36 (78.3%) | none |
| EMEA in the Aug row (share of EMEA base) | 55 (97.8%) | 55 (97.8%) | none |
| LatAm in the Aug row | 7 (100%) | 7 (100%) | none |
| APAC in the Aug row (share of APAC base) | 13 (50.5%) | 14 (67.7%) | +1, +17.2 pp |
| August window length, median / min days | 15 / 1 | 15 / 1 | none |

### 2.3 July, August-to-date and 3Q26-to-date y/y, before and after, percent (descriptive; `before_after.csv`, blocks vintage_matched_daymatched and within_vintage_daymatched)

Vintage-matched (2026 dump over the market's 2025 dump), review-count weighted, with equal-weighted in brackets:

| Window | NAM | EMEA | LatAm | APAC | Global | Global nights-wtd |
|---|---|---|---|---|---|---|
| July, before | 4.3 (4.5) | 1.1 (0.1) | 20.6 (16.8) | 3.8 (1.8) | 3.8 (2.5) | 4.5 |
| July, after | 4.3 (4.5) | 1.1 (0.1) | 20.6 (16.8) | 9.5 (3.5) | 4.2 (2.7) | 4.7 |
| Aug to date, before | 7.6 (9.2) | 0.3 (1.2) | 44.2 (33.1) | 7.3 (5.3) | 8.2 (6.1) | 9.7 |
| Aug to date, after | 7.6 (9.2) | 0.3 (1.2) | 44.2 (33.1) | 10.7 (6.3) | 8.5 (6.2) | 9.8 |
| 3Q26 to date, before | 6.9 (5.7) | 0.9 (0.2) | 27.5 (21.7) | 7.3 (3.4) | 5.2 (3.5) | 6.0 |
| 3Q26 to date, after | 6.9 (5.7) | 0.9 (0.2) | 27.5 (21.7) | 10.0 (4.3) | 5.5 (3.6) | 6.1 |
| Wedge 3Q26 to date, after, pp | 21.7 | 20.8 | 23.4 | 19.3 | 21.0 | 21.3 |

Within-vintage, day-matched, review-count weighted: July global 26.2 to 26.4 (APAC 24.0 to 26.4), August to date global 24.7 to 24.8 (APAC 27.0 to 26.6), 3Q26 to date global 26.3 to 26.4 (APAC 27.5 to 28.3). Equal-weighted and median rows move 0.0 to 0.3 pp. NAM, EMEA and LatAm rows are identical to three decimals in every construction.

### 2.4 Backtest, nights target, 2023Q1 window, level, lag 0 (computed; `before_after.csv`, block backtest_nights_2023Q1plus_level)

| Feature | wf ratio vs naive, before | after | wf RMSE pp, before | after | r 2024Q1+, before | after |
|---|---|---|---|---|---|---|
| GLOBAL all reviews, review-wtd | 0.683 | 0.681 | 1.475 | 1.471 | 0.42 | 0.42 |
| GLOBAL all reviews, equal-wtd | 0.686 | 0.684 | 1.480 | 1.478 | 0.34 | 0.34 |
| GLOBAL nights-share wtd | 0.725 | 0.724 | 1.565 | 1.562 | 0.20 | 0.21 |
| GLOBAL vintage-matched, review-wtd | 0.682 | 0.674 | 1.473 | 1.455 | 0.32 | 0.33 |
| GLOBAL 24m cohort, equal-wtd | 0.600 | 0.601 | 1.296 | 1.297 | 0.50 | 0.50 |
| APAC vintage-matched, review-wtd | 0.781 | 0.710 | 1.685 | 1.532 | 0.31 | 0.30 |
| Scoreboard: beat naive / of 2,560 | 463 | 465 | | | | |
| Eurostat EU27 2023M1+, vs naive | 0.591 | 0.591 | | | | |

### 2.5 3Q26 implied nights, before and after (computed; `q3_2026_nowcast.csv` in E and E_aug)

| Measure, weighting | Index 3Q26 full, before / after | Implied nights, before / after | Anchored on 2Q26, before / after | Band, before / after |
|---|---|---|---|---|
| all reviews, review-count | 26.4 / 26.5 | 10.0 / 10.0 | 10.8 / 10.7 | 8.6-11.5 / 8.6-11.5 |
| all reviews, equal | 24.3 / 24.3 | 9.2 / 9.2 | 10.2 / 10.2 | 7.7-10.7 / 7.7-10.7 |
| all reviews, median | 21.3 / 21.3 | 9.2 / 9.2 | 9.8 / 9.8 | 7.7-10.7 / 7.7-10.7 |
| all reviews, nights share | 27.4 / 27.5 | 9.3 / 9.4 | 10.6 / 10.6 | 7.8-10.9 / 7.8-10.9 |
| vintage-matched, review-count | 5.3 / 5.6 | 9.2 / 9.1 | 10.7 / 10.6 | 7.7-10.7 / 7.6-10.5 |
| vintage-matched, equal | 2.9 / 3.0 | 8.6 / 8.6 | 10.1 / 10.1 | 7.0-10.2 / 7.0-10.2 |
| vintage-matched, nights share | 5.4 / 5.5 | 8.7 / 8.7 | 10.3 / 10.3 | 6.9-10.4 / 6.9-10.4 |
| Seven rows together | | 9.17 / 9.16 | 10.36 / 10.34 | 6.9-11.5 / 6.9-11.5 |

Partial-to-full gap (2023 to 2025 mean): review-weighted +0.09 to +0.02 pp, equal -0.61 to -0.59 pp. Posting completeness at k = 14 days 1.007 to 1.008; k stays 14.

### 2.6 The named large markets, after run (descriptive; `big_markets_aug2026.csv`)

Vintage-matched y/y is the survivorship-clean number; within-vintage carries the wedge. "3Q26 to date" ends 14 days before the shorter of the two dumps. None of the rows below changed between runs except Tokyo, which is new.

| Market | Aug 2026 dump | 2025 dump | 3Q26-to-date window ends | Reviews in window | Vintage-matched y/y % | Within-vintage y/y % | Wedge pp | In the August row? |
|---|---|---|---|---|---|---|---|---|
| Los Angeles | 10 Aug | 1 Sep | 27 Jul | 38,439 | +12.4 | +41.9 | 29.5 | no (dump too early) |
| San Francisco | 10 Aug | 1 Sep | 27 Jul | 6,089 | +7.0 | +18.6 | 11.5 | no |
| New York City | 10 Aug | 1 Sep | 27 Jul | 13,741 | +22.8 | +42.7 | 19.9 | no |
| Montreal | 10 Aug | 16 Aug | 27 Jul | 17,038 | +19.3 | +66.7 | 47.4 | no |
| Chicago | 27 Aug | 19 Aug | 4 Aug | 19,435 | +12.5 | +36.3 | 23.7 | yes (to 13 Aug within-vintage) |
| Boston | 27 Aug | 23 Aug | 8 Aug | 8,393 | +22.9 | +46.1 | 23.3 | yes |
| Toronto | 15 Aug | 5 Aug | 21 Jul | 15,348 | +6.8 | +47.2 | 40.3 | yes (1 day) |
| London | 18 Aug | 14 Sep | 4 Aug | 87,896 | +9.7 | +45.3 | 35.6 | yes |
| Paris | 15 Aug | 8 Aug | 24 Jul | 46,781 | -3.0 | +24.8 | 27.8 | yes (1 day) |
| Barcelona | 23 Aug | 10 Aug | 26 Jul | 19,224 | +1.1 | +36.0 | 34.9 | yes |
| Sydney | 15 Aug | 5 Aug | 21 Jul | 13,145 | +3.7 | +32.7 | 29.0 | yes (1 day) |
| Singapore | 31 Aug | 30 Aug | 15 Aug | 1,236 | +3.3 | +15.3 | 12.0 | yes |
| Tokyo (new) | 31 Aug | 30 Aug | 15 Aug | 56,281 | +18.9 | +32.1 | 13.2 | yes |

Reading the column: the US big cities are strong on the clean measure (Boston +23, New York +23, Chicago +12, Los Angeles +12, San Francisco +7), the European capitals are flat to negative (Paris -3, Barcelona +1, London +10 with a 36 pp wedge that puts it on the scope-change screen), and Tokyo at +19 is the APAC outlier. Montreal, Toronto, London and Barcelona remain on the ten-largest-wedge list from the E note, so their within-vintage numbers should not be quoted on their own. Tokyo's July-to-August-to-date deceleration (+20.3 to +16.0) is inside the noise of a 15-day window.

## 3. Method

1. **Probe (E_aug1).** Market list and CDN paths from `E/inventory.csv`, with Tokyo's path corrected to the macron form. For each market, HEAD on `https://data.insideairbnb.com/<path>/<date>/data/reviews.csv.gz` for every date 1 Aug to 11 Sep 2026 (5,166 requests), plus Jun to Oct 2025 for Tokyo and June 2025 for the three other markets without a 2025 vintage. Then HEAD on listings and calendar for every date where reviews was live. 16 threads; 200/403/404 are answers, anything else is an error with a 30 s pause after 5 in a minute and a stop after 20; none occurred. `already_held` is checked against the three main-tree stores under their own naming (`<market_key>_<date>_reviews.csv.gz`; `<short>_<date>_calendar.csv.gz`; `<short>_<date>_listings.csv.gz`). Paths are percent-encoded with `urllib.parse.quote`, which is what makes the diacritic markets resolve (E1 passed raw paths, which `requests` also encodes; the Tokyo failure was the missing macron, not the encoding).
2. **Download (E_aug2).** Streaming GET, `.part` then rename, size check against Content-Length, sha256, manifest appended and deduplicated on file name. Only the two Tokyo reviews files were needed; calendar and listings for the 34-market panel were already held.
3. **Re-run (E_aug_run).** The committed E scripts are executed byte-for-byte except that the string `"data/processed/q3nowcast/E"` is replaced by `"data/processed/q3nowcast/E_aug"` at load time (and, for E7 only, the three download bookkeeping file names get the `_aug2026` suffix). E3 ran over all 365 files single-process against a copy of the q3nowcast worktree's per-file cache (363 files, 183 MB, copied with robocopy) plus the two new Tokyo files; it rebuilt `market_vintage_monthly.csv` (49,512 rows) and `market_vintage_daily.csv` (701,663 rows) from scratch in 2.6 minutes. E4 about a minute, E4b 20 s, E5 60 s, E6 6 s. The cache directory is not committed (`*.parquet` is gitignored; the daily CSVs in it are excluded by adding files explicitly).
4. **Compare (E_aug3).** Every metric the E note quotes, read from both directories, written as block / key / metric / before / after / delta. The "share of the 3Q25 review base" is the sum of July to September 2025 reviews in each market's latest dump, for the markets in the window, over the same sum for all 123 markets.

## 4. What this can and cannot identify

- **Can:** that the reviews store is complete for the August 2026 batch and that the only missing large market was a path bug; that adding Tokyo lifts APAC coverage from half to two thirds of the region's review base and lifts the APAC vintage-matched read by about 3 pp review-weighted (1 pp equal-weighted); that none of this moves the global 3Q26 implied nights by more than 0.15 pp on any row or the band at all.
- **Cannot:** narrow the band. The band is the walk-forward RMSE over 10 scored quarters of the same history, and one extra market in a 123-market panel does not change that history enough to matter (ratios move in the third decimal). Nor can it bring New York, Los Angeles, San Francisco or Montreal into the August row: their August dumps are dated 10 Aug and the probe confirms there is no later one. Nor can it say anything about September 2026, for which no dump exists yet.
- **Caveats carried from the E note, unchanged:** survivorship wedge about 21 pp, applied as a constant; reviews per stay unobserved; the panel is regulated cities, not Airbnb's footprint; the OLS slope is set mostly by the 2023 normalisation; 2,560 cells is a multiplicity problem; the August-to-date window is 1 to 17 days.
- **Specific to Tokyo:** the 2025-08-30 vintage was chosen to match the other markets' construction; the four other 2025 vintages would give slightly different vintage-matched levels (more attrition in the later ones). Tokyo's review counts date back to 2021 in the daily file, so it enters the partial-to-full gap measurement, which moved the review-weighted gap mean from +0.09 to +0.02 pp; this is inside the gap sd (0.2 pp).
- **The "49 of 86" premise:** this note cannot say where that count came from. The reviews store held 123 files dated 2026-08 for 122 markets before this run; the most likely explanation is a count taken from a different directory or before the 12 Sep E2 download completed.

## 5. Next evidence

1. **September 2026 dumps.** Inside Airbnb posts most markets between the 10th and the 30th; a re-probe on or after 15 Sep with `E_aug1_probe.py` (change `TODAY`) would close the August half-month for all 123 markets and bring the twelve early-August markets into the August row. Then `E_aug2_download.py`, then `E_aug_run.py --steps E1,E3,E4,E4b,E5,E6,E7` (about 5 minutes with the cache). That is the only thing that will materially change the 3Q26 read before the 5 Nov print.
2. **Fix the Tokyo path in E1** (`CITY13` is fine; the reviews store key `japan_kanto_tokyo` maps to `japan/kanto/tokyo` in `parse_name`). A one-line `PATH_FIX` as in `E_aug1_probe.py` would let future E1 runs see Tokyo. Not done here because E1 is a committed E file outside this workstream's paths.
3. **Do not** re-download the 2025 Tokyo vintages at other dates unless a Tokyo-specific survivorship study is wanted; the 366-day pair is the right one for the index.

## 6. Files

Scripts: `analysis/src/q3nowcast/E_aug1_probe.py`, `E_aug2_download.py`, `E_aug_run.py`, `E_aug3_compare.py`.

Outputs in `data/processed/q3nowcast/E_aug/` (the committed E outputs in `E/` are untouched):
- `cdn_probe_aug2026.csv` (5,655 rows: market, path, kind, date, why, url, status, bytes, last_modified, already_held), `download_plan_aug2026.csv` (6 rows, all Tokyo), `download_manifest_aug2026.csv` (2 files, url, bytes, sha256), `download_gaps_aug2026.csv` (empty).
- `before_after.csv` (717 rows, blocks: coverage, within_vintage_daymatched, vintage_matched_daymatched, q3_to_date_window, quarterly_index, backtest_scoreboard, backtest_nights_2023Q1plus_level, backtest_eurostat, q3_2026_nowcast, posting_completeness, partial_to_full_gap), `big_markets_aug2026.csv` (13 markets, both runs).
- The full E output set rebuilt on 365 files: `inventory.csv` (834 rows), `market_vintage_monthly.csv` (49,512), `market_vintage_daily.csv` (701,663, 37 MB), `market_geo.csv`, `survivorship_wedge.csv`, `posting_lag_curve.csv`, `posting_completeness_curve.csv`, `market_monthly_yoy.csv`, `region_monthly_index.csv`, `global_monthly_index.csv`, `index_quarterly.csv`, `coverage_monthly.csv`, `stable_listing_yoy_market.csv`, `stable_listing_index.csv`, `backtest_abnb_quarterly.csv`, `backtest_wf_paths.csv`, `backtest_survivor_robustness.csv`, `backtest_eurostat_monthly.csv`, `backtest_scoreboard.csv`, `partial_window_yoy_market.csv`, `partial_window_yoy_index.csv`, `monthly_nowcast_2026_market.csv`, `monthly_nowcast_2026.csv`, `vintage_matched_nowcast_market.csv`, `vintage_matched_nowcast.csv`, `partial_vs_full_quarter_market.csv`, `partial_vs_full_quarter.csv`, `q3_2026_nowcast.csv`, `q3_2026_coverage.csv`.
- `cache/` (365 parquet and 365 daily files, 188 MB) is not committed.

Raw (main tree, gitignored): `C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_reviews\japan_kanto_tokyo_2026-08-31_reviews.csv.gz` and `japan_kanto_tokyo_2025-08-30_reviews.csv.gz`, from `https://data.insideairbnb.com/japan/kant%C5%8D/tokyo/<date>/data/reviews.csv.gz`. Source: Inside Airbnb, https://insideairbnb.com/get-the-data/, CC-BY 4.0. Logs (not committed): `logs/E_aug1_probe.log`, `E_aug2_download.log`, `E_aug_run.log`, `E_aug_E7_report.log`, `E_aug3_compare.log`.
