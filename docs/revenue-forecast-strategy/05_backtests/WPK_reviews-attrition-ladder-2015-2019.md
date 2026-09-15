# WPK: Reviews attrition ladder from the 2015-2019 Inside Airbnb archives (Build B of the GitHub alt-data catalogue)
Claude Fable 5.1 subagent (github-altdata Build B) · 2026-09-14 · branch `krish/github-altdata-catalog` (worktree `citadel-abnb-ghcat`) · packages touched (all new): `analysis/src/q3nowcast_v2/E_attrition/`, `data/processed/q3nowcast_v2/E_attrition/`, raw store `C:/Users/krish/abnb_ia_capture/{montera34_barcelona,chicagobooth_2015,joeydejager_nyc_2015}/` (outside git, 100 files, 946 MB) · time spent: about 75 minutes wall (pulls 15 min, code and runs 35 min, note 25 min).

Data: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC BY 4.0, redistributed on GitHub by montera34/airbnb.barcelona (no LICENSE file), ChicagoBoothML/DATA___InsideAirBnB (no LICENSE file) and JoeyDeJager/inside-airbnb-data (CC0). Attribution in every output: "Inside Airbnb, CC BY 4.0".

## 0. Pre-registration (written 2026-09-14 13:45 local, before any pull or computation)

The E note (`research/notes/q3nowcast/E_reviews-stays-index.md`, table 2.2) measures survivorship of review history at 1 to 36 months of dump age on 129 vintage pairs from 2025 and 2026 dumps: about 15 percent of a review month's count disappears per year, decaying to 11 to 12 percent at 30 to 40 months. The index's vintage-matched construction assumes this wedge is roughly constant. Three older archives (Inside Airbnb, CC BY 4.0, redistributed on GitHub by montera34, ChicagoBoothML and JoeyDeJager) let the wedge be measured in an independent era (2015-2019) and at a decade horizon (2015 vintage vs the held 2025/2026 vintage). Nothing here enters the harness: there is no ABNB target before 1Q19 and the test is a corroboration of a mechanism, not a forecast.

Pre-registered lines (fixed before running anything):

| Line | Source | Measurement | PASS if |
|---|---|---|---|
| L1 | montera34 Barcelona, 34 vintages 2015-04-30 to 2019-03-08 | 12-month attrition of review history on successive vintage pairs whose early dump is in 2017 to 2019 (late dump 11 to 13 months after the early one), review-weighted over review months 1 to 36 months before the early dump, expressed as an annual rate | the pooled annual rate lies in 10 to 20 percent per year (the E note's constant-wedge assumption gains an independent era). Also reported: the rate for the 2015-2016 and 2016-2017 pairs, which are outside the line |
| L2 | ChicagoBoothML, 30 cities, one 2015 vintage per city (Jun to Nov 2015) | pooled cumulative attrition of the 2014 review months (Jan to Dec 2014) between the 2015 vintage and the market's held latest 2025/2026 vintage, review-weighted over the cities that map to a held market_key | ratio equals (1 - 0.15)^10 = 0.20 within +/- 0.10, i.e. in [0.10, 0.30] |
| L3 | JoeyDeJager NYC, one vintage 2015-01-01 | NYC cumulative attrition of the 2014 review months between the 2015-01-01 vintage and the held NYC 2025/2026 vintage | the ratio is reported and lies within +/- 0.10 of the L2 pooled value |

Vocabulary: a PASS on L1 and L2 is a "corroboration" of the E note's survivorship mechanism (it cannot be a survivor, nothing is scored against ABNB). A FAIL is written up and the E note gets a caveat in the RESUME. L3 is exhibit-only: it reproduces the manifest row counts and reports the NYC point.

Held side: `data/processed/q3nowcast/E/market_vintage_monthly.csv` (market x dump_date x review month, n_reviews), using the latest dump_date per market. Age in months = (held dump month - archive dump month). Ratios are same market, same review month, held count over archive count. The dump month of the archive vintage is excluded as truncated (E note, table 2.2 footnote).

Known caveats registered up front: (a) the held side uses the E3 count (listing_id x month from the 2025/2026 reviews.csv.gz), the archive side uses the same grain from reviews_summary (montera34, joeydejager) or the full reviews.csv.gz (ChicagoBooth); both are one row per review, so the counts are comparable. (b) Inside Airbnb's scope for a city can change between 2015 and 2026 (Barcelona, NYC after LL18, Amsterdam); a scope change shows up as attrition and is reported per market, not removed. (c) A decade of attrition compounds many mechanisms (delisting, host removal, review deletion, ID re-issue); the line tests only whether the cumulative survival is consistent with the 15 percent per year measured recently.

One deviation from the plan after pre-registration, recorded here: the E3 summary `market_vintage_monthly.csv` turns out to start at review month 2015-01, so the held side for the 2014 months used by L2 and L3 does not exist in it. The held latest raw reviews file for each of the 30 mapped markets was therefore recounted at the same listing x month grain (main-tree raw store, files named in `data/processed/q3nowcast/E/inventory.csv`) and used as the held side for those markets. The recount matches E3 exactly for every 2015-01 onward month in all 30 markets (`held_recount_vs_E3_check.csv`, max absolute monthly difference 0), so the held side is the same object E used, extended backwards. The lines were not changed.

## Verdict

Partial: one fail, two passes. **L1 fails.** Barcelona's review history attrited at 31 percent a year on 40 twelve-month vintage pairs with early dumps in 2017-2019 (17.1 million archive reviews), not the 10 to 20 percent pre-registered; the 2015 and 2016 pairs give 36 and 31 percent, so the whole 2015-2019 era ran at double the E note's rate, and the E note's own Barcelona 2025-to-2026 wedge is 11.8 percent. The loss is entirely listings leaving the dump (45 to 48 percent of reviewed listings gone within a year); listings that stay keep 100 percent of their reviews. Two 8-to-9-month cross-source pairs show the same thing outside Barcelona and before the HUTB crackdown: NYC Jan 2015 to Sep 2015 lost 25 percent of its review history (35 percent annualised), Barcelona Apr 2015 to Jan 2016 lost 29 percent. Fast attrition was a property of the 2015-2019 platform, not of one regulated city. **L2 passes.** Pooled over 30 cities, 13.9 percent of the reviews dated 2014 that a 2015 dump held are still in the 2026 dump (1.02 million archive reviews; equal-weighted mean 0.151, median 0.155, range Brussels 0.078 to Venice 0.256), inside the pre-registered [0.10, 0.30]. Annualised over the 129 to 134 month gaps that is 16.6 to 17.4 percent a year, close to the E note's 15. **L3 passes**, narrowly: NYC Jan 2015 vintage to Aug 2026 is 0.065, 0.074 below the L2 pooled value against a 0.10 tolerance; NYC is the LL18 market and the second-worst decade survivor. The constant-wedge assumption therefore holds as a decade average and holds within 2025-2026 (E note), but the 2015-2019 archives show the wedge can run at 30 percent a year for years; the within-vintage y/y of the stays index is only as stable as the attrition regime, which is the caveat the E note should carry (RESUME).

## What ran

All from the worktree root `C:/Users/krish/citadel-abnb-ghcat`, Python 3.11 venv (`python`; no pyarrow or duckdb in this venv, so the count cache is csv.gz).

Pulls (raw stores outside git; every file's url, bytes, sha256 and pull time in `data/processed/q3nowcast_v2/E_attrition/raw_manifest.csv`, 100 rows, 946,058,488 bytes):

1. montera34: `git clone --depth 1 --filter=blob:none --sparse https://github.com/montera34/airbnb.barcelona` then `git sparse-checkout set data/original/airbnb` FAILED (exit 128, "unable to read sha1 file ... a1c061104e6d", the partial clone could not fetch promisor blobs; `git restore --source=HEAD :/` also failed). Fallback per the plan: one curl per file, `https://raw.githubusercontent.com/montera34/airbnb.barcelona/master/data/original/airbnb/<yymmdd>/{listings_summary,reviews_summary}_barcelona_insideairbnb.csv`, resumable loop that skips files already present at the Content-Length; exit 0, 368 MB, about 6 minutes. Folder `180619` holds DataHippo scrapes (barcelona_*_datahippo.csv), not Inside Airbnb files; its two raw URLs returned "404: Not Found" bodies, which were deleted. The archive therefore has **33** Inside Airbnb vintages, not 34.
2. ChicagoBooth: `curl -sL -o <slug>_reviews.csv.gz "https://raw.githubusercontent.com/ChicagoBoothML/DATA___InsideAirBnB/master/<City%20Name>/reviews.csv.gz"` for the 30 directories listed by the GitHub contents API, plus `listings.csv.gz` for New York City and Barcelona; resumable loop with Content-Length check; exit 0, 32 files, 526 MB, about 2 minutes; the raw endpoint served the files whole (no LFS fallback needed). Scrape dates per city from `commits?per_page=100` (all committed 2015-12-03; Washington, D.C. has no date in its message, max review date + 1 = 2015-10-03 used).
3. JoeyDeJager: `curl -sL -o nyc_reviews_20150101184336.csv` and `nyc_listings_20150101184336.csv` from `.../new-york-city/2015-01-01/visualizations/`; exit 0; 277,605 review rows and 27,361 listing rows, matching the plan's manifest (27,361 and about 280k).

Build: `python analysis/src/q3nowcast_v2/E_attrition/run.py` -> exit 0, wall 232.7 s on the first full run (held recount of 30 raw files 100 to 330 MB each), 60 s cached. Earlier attempts: exit 1 (pyarrow missing, cache switched to csv.gz), exit 1 (the 180619 404 body), exit 0 but with the 2014 held months absent and the 2014 rows dropped by a NaN groupby key (fixed: held recount, and held vintage taken per market rather than from the merge). Log: `data/processed/q3nowcast_v2/E_attrition/run.log`.

## Results

All computed 2026-09-14 from genuine dated vintages (archive dumps 2015-01-01 to 2019-03-08; held dumps 2026-08-10 to 2026-08-31). No consensus numbers anywhere in this note.

### R1. Archive inventory (n = 64 vintages, 0 unmatched cities)

| Source | Vintages | Markets | Dump dates | Reviews in the latest vintage | Listing x month grain |
|---|---|---|---|---|---|
| montera34 Barcelona | 33 | 1 | 2015-04-30 .. 2019-03-08 (annual to Jan 2016, monthly Nov 2016 on) | 576,579 (2019-03-08) | reviews_summary (listing_id, date) |
| ChicagoBooth | 30 | 30 (all map to E market_keys by last key segment; alias washington-d-c -> washington-dc) | 2015-06-22 .. 2015-11-07 | 5,634 (Trentino) to 417,476 (Paris); NYC 366,453 | reviews.csv.gz, listing_id + date used |
| JoeyDeJager NYC | 1 | 1 | 2015-01-01 | 277,605 | visualizations csv (listing_id, date) |

Cross-check: ChicagoBooth Barcelona (2015-10-02) and montera34 151002 hold identical counts in every window tested (235,609 reviews in months 1-36 before the dump, 75,053 in calendar 2014, 11,738 listings): the two GitHub mirrors carry the same Inside Airbnb file, so the Barcelona ladder is not source-dependent.

### R2. Pooled attrition by dump-age bucket, review months 1-36 before the early dump (`survivorship_pooled_by_age.csv`)

Ages 1-48 months come from montera34 intra-archive pairs (Barcelona only, 528 vintage pairs); ages 85-144 from archive vs held 2026 (Barcelona for 85-120; 30 cities for 121-144). Annual attrition = 1 - ratio^(12/mean age).

| Age bucket, months | Vintage pairs | Markets | Archive reviews | Held/late reviews | Ratio (review-weighted) | Median row ratio | Annual attrition, % |
|---|---|---|---|---|---|---|---|
| 1-12 | 259 | 1 | 108,543,949 | 90,079,163 | 0.830 | 0.845 | 31.5 |
| 13-24 | 172 | 1 | 59,041,433 | 34,690,921 | 0.588 | 0.605 | 29.9 |
| 25-36 | 65 | 1 | 14,782,436 | 6,358,014 | 0.430 | 0.423 | 28.8 |
| 37-48 | 32 | 1 | 6,032,439 | 2,027,204 | 0.336 | 0.335 | 27.7 |
| 85-96 | 8 | 1 | 3,871,849 | 1,039,680 | 0.269 | 0.284 | 15.7 |
| 97-108 | 11 | 1 | 5,061,137 | 1,082,752 | 0.214 | 0.233 | 16.5 |
| 109-120 | 9 | 1 | 3,469,703 | 608,944 | 0.176 | 0.198 | 16.9 |
| 121-132 | 26 | 24 | 3,471,276 | 435,172 | 0.125 | 0.136 | 17.4 |
| 133-144 | 9 | 8 | 842,310 | 106,454 | 0.126 | 0.166 | 16.9 |

Comparison row from the E note, table 2.2 (2025-2026 dumps, 129 pairs, age about 12 months): ratio 0.849 to 0.883, annual attrition 11.7 to 16.0 percent. The "archive reviews" column counts every review-month row in every pair, so a review is counted once per pair (the 528 Barcelona pairs overlap heavily); n_rows and n_vintage_pairs are in the csv.

Reading: the Barcelona ladder at 1 to 48 months (2015-2019) attrites at 28 to 32 percent a year, twice the recent rate, and the compounding is clean (0.83, 0.59, 0.43, 0.34 at 6, 18, 30, 40 months mean age). The decade rungs (85 to 144 months) annualise to 15.7 to 17.4 percent, which is what a 30 percent regime in 2015-2019 followed by a 10 to 12 percent regime since implies: 0.127 (Barcelona 2015-10 to 2026-08) = 0.69^3.4 x 0.90^7.4 within rounding.

### R3. L1: Barcelona 12-month pairs (`L1_by_early_year.csv`, `L1_montera34_12m_pairs.csv`, `L1_listing_exit_decomposition.csv`)

Pairs with gap 11-13 months, review months 1-36 before the early dump. Annual attrition = 1 - ratio^(12/gap).

| Early dump year | Pairs | Archive reviews | Ratio | Mean gap, months | Annual attrition, % | Listings with reviews gone within a year, % | Reviews kept by surviving listings |
|---|---|---|---|---|---|---|---|
| 2015 (outside L1) | 1 | 235,609 | 0.613 | 13.0 | 36.3 | 48.3 | 1.016 |
| 2016 (outside L1) | 9 | 2,858,679 | 0.688 | 12.0 | 31.2 | 43.6 | 1.003 |
| 2017 | 33 | 13,838,816 | 0.690 | 12.0 | 31.0 | 45.5 | 1.001 |
| 2018 | 7 | 3,215,277 | 0.680 | 11.8 | 32.3 | 47.9 | 1.011 |
| **L1 pooled, 2017-2019** | **40** | **17,054,093** | **0.690** | **12.0** | **31.2** | | |

Pre-registered line 10 to 20 percent: **FAIL** (31.2). The per-pair range over the 40 pairs is 27.9 to 36.3 percent (ratios 0.639 to 0.726, csv), so no pair passes. E note comparison: Barcelona 2025-08-10 to 2026-08-23, months 1-36, ratio 0.882, attrition 11.8 percent (from `survivorship_wedge.csv`). The decomposition says the mechanism is listing exit, not review deletion: 44 to 48 percent of the listings with a review in the prior 36 months are absent from the dump a year later, and listings present in both dumps hold 100.1 to 101.6 percent of their earlier reviews (the excess is late-posted reviews). Exiting listings carry fewer reviews than average (45 percent of listings, 31 percent of reviews).

### R4. Cross-source 8-to-9-month pairs (`cross_source_pairs.csv`)

| Pair | Window | Early reviews | Late reviews | Ratio | Annualised attrition, % | Listings gone, % |
|---|---|---|---|---|---|---|
| NYC 2015-01-01 (JoeyDeJager) -> 2015-09-01 (ChicagoBooth), 8 months | months 1-36 before | 263,272 | 197,098 | 0.749 | 35.2 | 43.4 |
| same | calendar 2014 | 168,319 | 121,774 | 0.723 | 38.5 | 42.9 |
| Barcelona 2015-04-30 -> 2016-01-03 (montera34), 9 months | months 1-36 before | 142,190 | 100,953 | 0.710 | 36.7 | 40.1 |
| same | calendar 2014 | 82,752 | 59,871 | 0.723 | 35.0 | 38.4 |

NYC in 2015 attrited as fast as Barcelona, before any enforcement in either city (Barcelona's HUTB crackdown began 2016, NYC's LL18 in 2023), so the 2015-2019 rate is an era effect (young supply, high listing churn), not a regulatory one.

### R5. L2: 2014 review months, 2015 vintage vs held 2026 vintage, 30 cities (`L2_chicagobooth_2014_by_city.csv`)

| Statistic | Value |
|---|---|
| Cities (all 30 mapped, all with held 2026 dumps) | 30 |
| Archive 2014 reviews | 1,016,010 |
| Held 2014 reviews | 141,408 |
| Pooled ratio (review-weighted) | **0.139** |
| Equal-weighted mean / median | 0.151 / 0.155 |
| Range | Brussels 0.078, Chicago 0.080, Berlin 0.085, Montreal 0.090, NYC 0.090 ... Nashville 0.200, Venice 0.256 |
| Gap | 129 to 134 months |
| Pre-registered [0.097, 0.297] | **PASS** |

Twenty-four of 30 cities are inside the band on their own; six (Brussels, Chicago, Berlin, Montreal, NYC and Antwerp, 0.078 to 0.093) sit just below the lower edge of 0.097, none above the upper edge. The line was pre-registered on the pooled ratio, which passes; the per-city spread is reported, not scored. Per-market table with region and the E note's own 12-month wedge: `per_market_decade_attrition.csv` (2012-2014 months). Spearman rank correlation between the decade-implied annual attrition and the E note's 2025-2026 12-month attrition across the 30 cities is 0.29 (n = 30): the markets that lost most over a decade are only weakly the ones losing most today. The E-note 12-month wedge ranges 5.1 (Amsterdam) to 20.0 percent (Brussels) across these 30; the decade-implied annual rate ranges 10.6 (Trentino) to 20.9 (Brussels).

### R6. L3: NYC 2015-01-01 vintage vs held 2026-08-10

| Window | Archive reviews | Held reviews | Ratio | Line | Verdict |
|---|---|---|---|---|---|
| Calendar 2014 (L3) | 168,319 | 10,987 | **0.065** | within 0.10 of 0.139, i.e. [0.039, 0.239] | **PASS** (margin 0.026) |
| Reference: NYC Sep 2015 vintage, calendar 2014 | 121,774 | 10,987 | 0.090 | | |
| Reference: 2012-2014 months, Jan 2015 vintage | 263,272 | 19,766 | 0.075 | implied 20.0 percent a year | |

Row counts reproduced: 277,605 reviews (manifest "about 280k"), 27,361 listing rows (manifest 27,361; `wc -l` shows 27,364 lines because three names contain quoted newlines). NYC is the market where the E note's index has to work through LL18 (Sep 2023); its decade survival is the second lowest in NAM and the implied annual rate (20.0 percent from the Jan 2015 vintage, 19.0 from the Sep 2015 one) is the highest of the 30 cities bar Brussels.

### R7. Barcelona supply exhibit, montera34 listings_summary per dump (`barcelona_supply_2015_2019.csv`, 33 rows; prices in EUR as quoted, no FX)

| Dump | Listings | Entire home, % | Multi-listing hosts' share, % | Median price, EUR | Min nights 30+, % | Cumulative reviews |
|---|---|---|---|---|---|---|
| 2015-04-30 | 12,033 | 59.1 | 59.5 | 65 | 0.0 | 157,355 |
| 2015-10-02 | 14,539 | 53.8 | 55.1 | 60 | 1.0 | 242,562 |
| 2016-01-03 | 14,855 | 53.0 | 53.7 | 59 | 0.8 | 232,100 |
| 2016-11-07 | 17,036 | 50.8 | 57.4 | 60 | 2.0 | 381,537 |
| 2017-01-04 | 17,412 | 50.2 | 57.9 | 60 | 2.1 | 390,575 |
| 2017-06-05 | 18,362 | 49.6 | 56.8 | 65 | 2.3 | 456,163 |
| 2017-09-12 | 18,284 | 45.5 | 56.1 | 60 | 2.3 | 480,416 |
| 2018-01-17 | 18,760 | 46.6 | 56.1 | 59 | 2.3 | 512,365 |
| 2018-05-14 | 18,919 | 46.3 | 56.1 | 60 | 2.0 | 547,588 |
| 2018-06-09 | 17,221 | 40.2 | 58.7 | 59 | 2.3 | 529,675 |
| 2018-08-18 | 19,261 | 42.4 | 61.9 | 55 | 12.8 | 561,090 |
| 2018-12-10 | 18,871 | 46.5 | 62.4 | 55 | 15.1 | 597,176 |
| 2019-03-08 | 17,807 | 49.2 | 64.6 | 60 | 16.5 | 576,579 |

Readings (descriptive): the listing count rose 12,033 to about 19,000 through 2015-2018 despite 45 percent annual exit, so gross adds ran near 55 percent of stock a year; the entire-home share fell from 59 to 40 percent by June 2018 (the enforcement period) and recovered to 49 percent by March 2019; the 30-plus minimum-nights share jumped from 2 to 13 percent between the June and August 2018 dumps (the response to the licence rule: unlicensed entire homes re-listed as 31-night stays), reaching 16.5 percent by March 2019; median quoted price stayed 55 to 65 EUR throughout. Full monthly table in the csv.

## What failed or could not be done, and why

- L1 failed against its pre-registered line (31.2 percent vs 10 to 20). Written up above; not re-specified.
- The sparse partial clone of montera34 failed twice on missing promisor blobs (git 2.x on Windows, `--filter=blob:none` with a 147 MB repo); the per-file curl route worked. The plan's first_command should be replaced by the curl loop (in `run.py` docstring and README).
- Folder 180619 is not an Inside Airbnb vintage (DataHippo files), so the ladder has 33 vintages, not the plan's 34.
- `market_vintage_monthly.csv` has no months before 2015-01; the held side for L2 and L3 had to be recounted from raw for 30 markets (validated exactly against E3 for 2015-01 onward). This is a deviation from the pre-registered mechanics, not from the lines.
- No pyarrow or duckdb in the venv: cache is csv.gz (43 MB, ignored by a `.gitignore` inside `cache/`).
- The Spearman between decade and 12-month per-market attrition (0.29) is reported but was not pre-registered; treat it as descriptive.
- The 13-city like-for-like panel extension (lane feed 2, listing-id retention pairs on `inside_airbnb_like_for_like.csv` schema) was not built: it is outside Build B's five steps. The listing-exit shares in R3 are the same quantity for the reviewed subset and could seed it.

## Interpretation

1. The E note's 15 percent a year is a 2025-2026 measurement and a decade average, not a constant of the platform. In 2015-2019 the same quantity ran at 28 to 36 percent a year in Barcelona and NYC alike, through listing exit alone. The within-vintage y/y that the stays index uses carries a wedge equal to roughly one year of attrition on the year-ago side; at 15 percent that wedge is the 20 pp the E note measures, at 30 percent it would be about 40 pp. The backtest's 0.68 ratio to naive rests on the wedge being roughly constant across 2023-2026, which the E note measured; these archives cannot test 2023-2026 but they show the assumption can break, and break for years, when the supply regime changes (the 2015-2019 era was one of young, churning supply). The vintage-matched construction (2026 dump over 2025 dump) is the one that does not depend on it and should stay the headline.
2. The decade survival passing at 0.139 pooled (16 to 17 percent a year annualised) is consistent with the E note's 15 percent only as a blend: fast early years, slow recent years. It is corroboration of the level over a long window, not of constancy.
3. NYC is the live case. Its decade survival (0.065 to 0.090 depending on the 2015 vintage) is among the lowest, its implied annual attrition (19 to 20 percent) the highest bar Brussels, and its 2025-2026 12-month wedge (12.8 percent) is now close to the panel median, so LL18's supply removal sits mostly in the 2023-2025 pairs that the E note's 2025-2026 wedge does not see. Any NYC within-vintage y/y spanning Sep 2023 is not comparable with other markets.
4. Per-market wedges are not a stable market trait: Spearman 0.29 between decade and current attrition over 30 cities. The E note's list of ten high-wedge markets should be read as "high now", not "always high".
5. Barcelona supply exhibit: the entire-home share fell 19 points and the 30-plus-night share rose 14 points across the 2016-2018 enforcement window while the listing count kept rising. Useful for the regulatory Barcelona factor (lane feed 3) and as the template for what an LL18-style shock looks like in Inside Airbnb dumps; not a nights measurement (kill-list item on the 120-market panel applies to any such count).
6. Nothing here bears on 3Q26 or the 5 Nov print directly. The one operational implication is for the E note's caveat list: add "the wedge is regime-dependent; 2015-2019 archives show 30 percent a year".

Parameter count: zero fitted parameters. Every number is a ratio of counts; the only choices are the 36-month review window, the 11-13 month gap band for L1, the 12-month age buckets, and the exclusion of the dump month.

## Harness change requests

None. Nothing registered; the scorer was not run (no registry file written, by design: no ABNB quarter is scored).

## RESUME

The next agent should (1) add one caveat sentence to the E v2 note (new file, do not edit E) citing R2 and R4: the survivorship wedge was 28 to 36 percent a year in 2015-2019 (Barcelona and NYC) against 15 percent in 2025-2026, so the within-vintage y/y is only comparable across periods with a stable attrition regime, and the vintage-matched series stays the headline; (2) when the September 2026 dumps land (WP-K), append them as a third held vintage and re-run `python analysis/src/q3nowcast_v2/E_attrition/run.py` (60 s cached; held recount cache is keyed by market and dump date, so new dumps recount automatically) to get a 2025-08 to 2026-09 rung and check the Barcelona 12-month wedge stays near 12 percent; (3) if the like-for-like panel extension is wanted, the montera34 listings_summary files (33 dates, ids) are on disk under `C:/Users/krish/abnb_ia_capture/montera34_barcelona/` and `L1_listing_exit_decomposition.csv` already gives reviewed-listing retention at 12 months; (4) do not re-pull; the manifest has sha256 for all 100 files and the loops skip files already present at the right size. Nothing enters the harness and no forecast changes.
