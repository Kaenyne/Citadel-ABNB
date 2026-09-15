# WP-K (build A): Reviews stays index: the Mar-May 2023 Inside Airbnb vintage as a second era, plus the NYC Local Law 18 bracket

Agent: Claude (Fable 5.1) subagent · 14 Sep 2026 · branch `krish/github-altdata-catalog` (worktree `citadel-abnb-ghcat`) · packages touched (all new): `analysis/src/q3nowcast_v2/E/`, `data/processed/q3nowcast_v2/E/`, `data/processed/regulatory_v2/` · raw store (gitignored, outside the repo): `C:/Users/krish/abnb_ia_capture/ia_reviews_vintage2023/` (4.88 GB, 114 files) · time spent: about 35 minutes wall (13:40 to 14:12 local), of which 13 minutes download and 2 minutes counting.

Attribution: Inside Airbnb, CC BY 4.0, dump dates as listed in `data/processed/q3nowcast_v2/E/raw_manifest_vintage2023.csv` (mirror: Hugging Face `alujjdnd/Airbnb-Mar-2022-2023`, folder `raw_dl/`; the MIT tag on the HF card is the uploader's, not the origin's). Nothing here touched airbnb.com.

## Verdict

One pass, two fails, all three written up. T3 (NYC Local Law 18) PASSES: the attrition-corrected NYC review flow Sep 2023 to Aug 2024 is -65.8 percent against Sep 2022 to Aug 2023 (sensitivity -66.2, uncorrected -32.3), inside the pre-registered -40 to -70 band and 10 pp below the CRA -56.1 percent guest-nights benchmark, so REG-01 now has a non-company corroboration measured on Inside Airbnb data. T1 (wedge constancy) FAILS: the within-vintage y/y for Mar 2022 to Feb 2023 is +90.4 percent read inside the fresh 2023 dumps and +80.5 percent read inside the same markets' Aug/Sep 2025 dumps, a difference of -10.0 pp globally (line 2.0) and -6.6 to -15.4 pp in every region (line 3.0), n = 114 markets, 1,357 market-months. The survivorship wedge is not constant in the age of the review month: the months just before a dump lose more of their reviews over the following years (2025/2023 ratio 0.63 at 1 to 3 months of age, 0.71 at 36 months, 0.74 at 60), so a within-vintage y/y read years after the fact is lower than the same y/y read fresh, and the gap grows with the y/y itself. The pre-registered consequence was applied. The E5 result the team quotes (window 2023Q1+, 0.68 vs naive) is scored on exactly the harness W2 target set (10 quarters 1Q24 to 2Q26) with 1Q23 to 4Q23 as training quarters, and those training quarters are read from a stale vintage; the W1-scored analogue (window 2022Q1+, 14 scored quarters) sits at 0.837 in the v1 backtest and was never a survivor. Re-reading 1Q23 from the fresh 2023 vintage moves the W2-scored ratio to 0.757 on the honest 103-market variant and 0.841 on the literal rule, both above the pre-registered 0.75 line. So after the re-run no separately measured statistic keeps the stays index at survivor grade on either window, and its short-window-survivor label now carries a revintaging caveat attached to the 1Q23 to 4Q23 training quarters (the lane spec's wording for this consequence, a downgrade to the W2 window, meant that caveat, not that a W2 walk-forward passed). The substitution touches no scored quarter (1Q24 to 2Q26 are read at 0 to 20 months of age inside the 2025/2026 dumps and the 2023 vintage cannot reach them), yet the scored statistic still moves because the walk-forward trains on the substituted quarter. T2 (attrition extension) FAILS its band: the pooled 2025/2023 ratio at 26 to 40 months of age is 0.660 (n = 114 markets, 1,246 pairs, band 0.75 to 0.90), but the band was mis-extrapolated when it was written: the E table 2.2 hazard of about 15 percent a year compounds to 0.68 over the actual 28.9-month gap, and the measured 0.660 (annualised retention 0.842, i.e. 15.8 percent a year) is consistent with that table. The disagreement is with the band, not with the curve; the constant-hazard reading of table 2.2 survives, its age-flatness does not (T1). Nothing was registered through the harness; the harness change request is in section 5.

## 0. Pre-registration (written 14 Sep 2026 13:55 local, before any test ran; pass lines, consequences and numbers unchanged; the W1/W2 window labels were corrected on 14 Sep after independent verification, because the quoted 0.68 is scored on the harness W2 target set, see the Verdict)

Context. The reviews stays index (`research/notes/q3nowcast/E_reviews-stays-index.md`) rests on two held vintages of the Inside Airbnb review log per market (Aug/Sep 2025 and Jun-Aug 2026). Its 1Q23 to 4Q24 quarters (1Q23 to 4Q23 are training-only quarters and 1Q24 to 4Q24 scored quarters in the run quoted below) are read inside a single 2025 or 2026 dump, so their y/y carries a survivorship wedge that the E note assumes is constant in time (table 2.2: the same review month measured in two dumps 12 months apart is 0.85 to 0.88 of its earlier count, flat from 1 to 36 months of age). The E5 walk-forward result the team quotes is the global all-reviews review-weighted quarterly y/y at lag 0, level, window 2023Q1+, 10 scored quarters 1Q24 to 2Q26 (the harness W2 target set; 1Q23 to 4Q23 are training quarters): RMSE ratio 0.68 vs naive (`backtest_abnb_quarterly.csv`, feature `GLOBAL|yoy_all|w_reviews`). The 116-market Mar-May 2023 mirror is a genuine second vintage that lets the wedge be measured 2.5 years earlier and lets the 2022 to early-2023 months be read without any attrition.

Definitions used in every test.

- Within-vintage y/y for review month m in dump V: `n_V[m] / n_V[m-12] - 1`, review counts from E3 logic (pyarrow read of listing_id and date, group listing x month, sum), the dump month dropped as truncated.
- Complete month: a review month m enters a test only if the month end plus 14 days is on or before the dump date (E table 2.3: a review date is complete 14 days later). This is stricter than the E4 rule (drop the dump month only) and is stated here because most 2023 dumps are dated 6 to 31 March 2023 and February 2023 is otherwise only partly posted for the earliest ones.
- Held 2025 vintage: the earliest held dump per market (Aug or Sep 2025, `market_vintage_monthly.csv`, v1, tracked).
- Regions: `market_geo.csv` (v1, tracked); the 2023-vintage market_key is the raw_dl stem minus the date, mapped to the geo key for `japan_kantō_tokyo -> japan_kanto_tokyo` and the three mangled country-level names (ireland, malta, new-zealand); the two 75-byte china files are skipped. Markets enter a test only if they have both a 2023 vintage and a held 2025 vintage.
- Review-weighted aggregate: pooled `sum(num) / sum(den) - 1` over markets and months, exactly E4's `w_reviews` construction.

T1, wedge constancy (corroboration of the assumption behind the quoted 0.68, whose 2023 training quarters are read from a stale vintage). For the 12 review months Mar 2022 to Feb 2023 (all complete in every 2023 dump dated on or after 15 Mar 2023; markets whose 2023 dump is earlier lose Feb 2023 under the completeness rule), compute the within-vintage y/y inside the 2023 vintage and inside the held 2025 vintage, pooled review-weighted over the 12 months. Pass line: global |difference| <= 2.0 pp AND every region (NAM, EMEA, LatAm, APAC) |difference| <= 3.0 pp. PASS = the constant-wedge assumption survives a second era and the quoted stays-index result stands as written. FAIL = the quoted result gets a revintaging caveat attached to its 1Q23 to 4Q23 training quarters (the lane spec's wording for this consequence, a downgrade to the W2 window, means this caveat and not a separately passed W2 walk-forward, since the quoted run is already W2-scored), unless the E5 walk-forward re-run on the 2023Q1+ window with the 2023-vintage values substituted for 4Q22 and 1Q23 (the only quarters the 2023 vintage can supply) keeps the ratio vs naive <= 0.75, in which case it stays a short-window survivor with the caveat. Per-month differences are reported as descriptive.

T2, attrition curve extension. Pooled same-month ratio `n_2025[m] / n_2023[m]` over the markets in T1, for review months whose age at the 2025 dump is 26 to 40 months (dump age = months from the review month to the later dump), restricted to months complete in the 2023 vintage. Pass line: the pooled ratio lies in 0.75 to 0.90 (the extrapolation of E table 2.2, which stops at a 12-month gap and 36 months of age). The ratio is also reported by months-before-early-dump bucket as a direct extension of table 2.2. Outside the band = written up as a disagreement with the 15 percent per year extrapolation; the E note's wedge table gets a caveat that attrition is not a constant hazard.

T3, NYC Local Law 18 bracket. From the 2023-03-06 NYC mirror file (un-attrited pre-LL18 log) and the held NYC 2025-09-01 dump: attrition-corrected review flow Sep 2023 to Aug 2024 versus Sep 2022 to Aug 2023. Construction: A (pre) = 2023-vintage counts for Sep 2022 to Feb 2023 (Feb 2023 is not complete at a 6 Mar dump: it is taken from the 2025 dump and corrected like Mar to Aug 2023) plus 2025-vintage counts for Feb to Aug 2023 divided by r_pre, where r_pre = pooled `n_2025[m]/n_2023[m]` over NYC's complete months Sep 2022 to Jan 2023; B (post) = 2025-vintage counts for Sep 2023 to Aug 2024 divided by r_post, where r_post = 0.86 (E table 2.2 pooled 12 to 24 month ratio, the ordinary attrition of 12 to 24 month old history). Sensitivity: r_post from NYC's own held pair (n_2026-08[m]/n_2025-09[m] on Sep 2023 to Aug 2024). Cross-check: the Jan 2024 Kaggle listing file's `number_of_reviews_ltm` sum (225,268, Jan 2023 to Jan 2024, un-attrited as of 5 Jan 2024) against the 2025 dump's count of the same window. Pass line: T3 = B/A - 1 falls in -40 percent to -70 percent, corroborating the CRA -56.1 percent guest-nights benchmark (`research/regulatory/phase2/nyc_activity_benchmark.json`) with a non-company source. Outside the band = written up as a disagreement; the benchmark keeps its CRA label. Bracket file: `data/processed/regulatory_v2/nyc_ll18_bracket.csv` with a row per cross-section (2023-03-06 mirror, 2024-01-05 Kaggle file, 2025-09-01 and 2026-08-10 held dumps), listings on the reviewed-in-trailing-12-months basis only, never raw counts.

Nothing is registered through the harness in this build (T1 to T3 are corroboration tests of an existing survivor and a regulatory exhibit); any change to a registered stays-index row is a harness change request (section 5).

## 1. What ran

All from the worktree root `C:/Users/krish/citadel-abnb-ghcat`, interpreter `py -3.13` (pandas 2.3.3, pyarrow 24; the repo venv `python` has no pyarrow on this machine, as the v1 E scripts also note). Every step exit 0.

| Step | Command | Exit | Wall |
|---|---|---|---|
| Download + verify + manifest | `py -3.13 -X utf8 analysis/src/q3nowcast_v2/E/V1_download_vintage2023.py` (background; log `_download.log` in the raw store) | 0 | 13:47:58 to 14:00:51, 114/114 files, 0 retries, 0 gzip failures |
| Count (E3 logic, two folders, v1 caches copied) | `py -3.13 -X utf8 analysis/src/q3nowcast_v2/E/V2_review_counts_two_folders.py --workers 3` | 0 | 98 s (364 cached, 115 counted afresh) |
| E4 copy on the v2 folder | `py -3.13 -X utf8 analysis/src/q3nowcast_v2/E/V3_build_index.py` | 0 | 17 s |
| T1, T2 | `py -3.13 -X utf8 analysis/src/q3nowcast_v2/E/V4_tests_T1_T2.py` | 0 | 28 s |
| T3 + bracket | `py -3.13 -X utf8 analysis/src/q3nowcast_v2/E/V5_nyc_ll18_bracket.py` | 0 | 11 s |
| E5 substitution re-run (T1 fail branch) | `py -3.13 -X utf8 analysis/src/q3nowcast_v2/E/V6_backtest_substituted.py` | 0 | 2 s |
| End-to-end confirmation | `py -3.13 -X utf8 analysis/src/q3nowcast_v2/E/run.py --skip-download` (log `data/processed/q3nowcast_v2/E/_run_log.txt`) | 0 | see log |

Data pulled: 114 of the 116 `raw_dl/` files (the two 75-byte china files skipped), 4,883,718,264 bytes, 42,600,893 lines, every file size-matched to the HF index and read end to end through gzip; sha256 and `pulled_at` (UTC) per file in `data/processed/q3nowcast_v2/E/raw_manifest_vintage2023.csv`. Files renamed to `<market_key>_<dump_date>_reviews.csv.gz`; 110 keys match `market_geo.csv` as-is, 4 by the stated map, so all 114 join the index. Dump dates 2023-03-06 (NYC) to 2023-05-18 (Dallas); 107 of 114 dated in March 2023. The held store `MAIN/data/raw/inside_airbnb_reviews` was not written to.

Consistency: the 49,243 held market-vintage-months recomputed here from the copied v1 caches are identical to the tracked v1 `market_vintage_monthly.csv` on every count column (0 value mismatches; `v1_consistency_check.csv`). The v2 table carries two held Tokyo vintages the v1 table lacks (`japan_kanto_tokyo` 2025-08-30 and 2026-08-31, files present in the held store but never counted by v1: 269 rows, of which `v1_consistency_mismatches.csv` lists the first 50, all `japan_kanto_tokyo` 2025-08-30, right_only); they do not enter any of T1 to T3 beyond Tokyo's 2025 vintage in T1/T2, which is exactly the vintage the tests need. The v2 table: 60,811 rows, 123 markets, 479 market-vintages (365 held + 114 new). The 2023 vintages hold 41.9 M reviews dated 2015 onward.

## 2. Results

All figures computed from the files named; PIT status: the 2023 vintages are genuine point-in-time objects (public at the time; the CDN no longer serves them); the held 2025/2026 vintages are as in v1. No consensus number appears in this note.

### 2.1 T1: within-vintage y/y for Mar 2022 to Feb 2023, fresh (2023 dump) vs stale (2025 dump), pooled review-weighted, percent (`t1_wedge_constancy.csv`)

| Scope | n markets | n market-months | Reviews (2023 v) | y/y in 2023 vintage | y/y in 2025 vintage | Diff, pp | Equal-wt diff, pp | Line, pp | Pass |
|---|---|---|---|---|---|---|---|---|---|
| GLOBAL | 114 | 1,357 | 12,442,784 | 90.41 | 80.45 | -9.96 | -10.28 | 2.0 | FAIL |
| NAM | 39 | 463 | 3,555,537 | 55.77 | 44.29 | -11.48 | -10.47 | 3.0 | FAIL |
| EMEA | 55 | 657 | 6,435,017 | 115.27 | 103.73 | -11.54 | -8.43 | 3.0 | FAIL |
| LatAm | 5 | 60 | 821,310 | 129.41 | 113.98 | -15.42 | -12.34 | 3.0 | FAIL |
| APAC | 15 | 177 | 1,630,920 | 80.22 | 73.64 | -6.58 | -15.92 | 3.0 | FAIL |

Market level (114 markets): median difference -8.3 pp, interquartile -17.5 to -3.2 pp, 90 percent of markets negative. The sign is uniform: the stale read is lower.

By review month, global (`t1_wedge_constancy_monthly.csv`, n = 114 markets each month, 103 for Feb 2023):

| Month | 2022-03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 2023-01 | 02 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| y/y, 2023 vintage | 155.6 | 178.7 | 152.2 | 125.2 | 87.2 | 62.5 | 89.4 | 80.9 | 61.4 | 51.7 | 71.3 | 72.5 |
| y/y, 2025 vintage | 152.0 | 176.6 | 146.7 | 117.6 | 78.7 | 54.2 | 77.9 | 67.6 | 49.6 | 39.6 | 57.3 | 57.8 |
| Diff, pp | -3.6 | -2.1 | -5.5 | -7.6 | -8.5 | -8.3 | -11.5 | -13.2 | -11.9 | -12.1 | -14.0 | -14.7 |

The gap widens toward the dump date: the months nearest a dump are the ones that later lose the most reviews (section 2.2), so a y/y whose numerator month is young is biased down when re-read years later. Multiplicatively the stale read is (1 + 0.8045) / (1 + 0.9041) = 0.947 of the fresh read on the growth factor; the pp gap scales with the level of growth (large here because Mar 2022 to Feb 2023 is the post-Omicron recovery year).

### 2.2 T2: attrition of review history between the 2023 dumps and the held 2025 / 2026 dumps (`t2_attrition_extension.csv`, `t2_attrition_by_age.csv`)

Primary (pre-registered): pooled n_2025 / n_2023, review months aged 26 to 40 months at the 2025 dump, complete in the 2023 vintage.

| Scope | n markets | n pairs | Reviews (2023 v) | Pooled ratio | Median market ratio | Mean gap, months | Annualised retention | Band | Pass |
|---|---|---|---|---|---|---|---|---|---|
| GLOBAL | 114 | 1,246 | 11,728,878 | 0.660 | 0.666 | 28.9 | 0.842 | 0.75-0.90 | FAIL |
| NAM | 39 | 425 | 3,262,847 | 0.607 | 0.636 | 28.9 | 0.813 | 0.75-0.90 | FAIL |
| EMEA | 55 | 602 | 6,074,674 | 0.685 | 0.697 | 29.0 | 0.855 | 0.75-0.90 | FAIL |
| LatAm | 5 | 55 | 767,178 | 0.635 | 0.658 | 29.0 | 0.828 | 0.75-0.90 | FAIL |
| APAC | 15 | 164 | 1,624,179 | 0.686 | 0.683 | 28.7 | 0.854 | 0.75-0.90 | FAIL |

Extension of E table 2.2 by months before the early (2023) dump, pooled, 114 markets per row (97 at month 1 because the earliest March dumps fail the 14-day completeness rule for February):

| Months before the 2023 dump | 1 | 3 | 6 | 12 | 18 | 24 | 36 | 48 | 60 |
|---|---|---|---|---|---|---|---|---|---|
| 2025 dump / 2023 dump (gap 28.9 months) | 0.626 | 0.629 | 0.665 | 0.682 | 0.708 | 0.692 | 0.709 | 0.729 | 0.739 |
| annualised retention | 0.824 | 0.825 | 0.844 | 0.853 | 0.866 | 0.858 | 0.867 | 0.877 | 0.882 |
| 2026 dump / 2023 dump (gap 39.0 months) | 0.558 | 0.563 | 0.598 | 0.615 | 0.640 | 0.624 | 0.641 | 0.660 | 0.670 |
| annualised retention | 0.836 | 0.838 | 0.853 | 0.861 | 0.872 | 0.865 | 0.872 | 0.880 | 0.884 |
| n pairs (2025 row) | 97 | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 114 |

Reading: the annualised hazard is 12 to 18 percent a year, the same order as table 2.2 (11.7 to 16.0), and it compounds: 0.85 a year over 28.9 months is 0.676, over 39 months 0.59, against measured 0.660 and 0.598 at 6 months of age. The band 0.75 to 0.90 written in the lane spec would have required a hazard of 4 to 11 percent a year and was not the extrapolation of table 2.2 it claimed to be; the fail is recorded as pre-registered and the band error is stated here. What the curve does show, and what T1 turns on, is that retention rises with the age of the month at the early dump: 0.63 for months 1 to 3 old, 0.71 at 36 months, 0.74 at 60 (the 2026 row shows the same slope). Recent months carry more reviews from young listings, and young listings churn.

### 2.3 T1 fail branch: E5 walk-forward re-run with 2023-vintage values substituted (`t1_fail_e5_rerun.csv`)

Feature `GLOBAL|yoy_all|w_reviews`, lag 0, level, window 2023Q1+, target disclosed nights y/y, 10 scored quarters 1Q24 to 2Q26 (the harness W2 target set; 1Q23 to 4Q23 are training quarters, so every ratio in this table is W2-scored), naive RMSE 2.159 pp in every row. 4Q22 lies outside the 2023Q1+ window, so only the 1Q23 substitution moves the ratio.

| Variant | 4Q22 value, % | 1Q23 value, % | wf n | RMSE feature, pp | Ratio vs naive | <= 0.75 |
|---|---|---|---|---|---|---|
| v1 (single 2025/2026 vintage; reproduces the note's 0.68) | 51.8 | 51.6 | 10 | 1.475 | 0.683 | yes |
| a: literal rule, 2023-vintage 4Q22 (114 mkts) and 1Q23 (three complete months: only the 7 May-dump markets) | 65.5 | 109.1 | 10 | 1.816 | 0.841 | no |
| b: 2023-vintage 4Q22 (114 mkts) and 1Q23 read as Jan-Feb 2023 (103 mkts, the months complete in every dump dated >= 15 Mar) | 65.5 | 71.8 | 10 | 1.634 | 0.757 | no |
| c: v1 1Q23 rescaled by the pooled T1 factor 1.055 (estimate, not a measurement) | 51.8 | 60.0 | 10 | 1.538 | 0.713 | yes |

Variant a is the pre-registered rule taken literally, but its 1Q23 value is a 7-market composition artefact (Montreal, Quebec City, Dallas, Bozeman, Vaud, New Zealand, Mid-North Coast) and is not the index. Variant b is the honest measured substitution and also fails the 0.75 line (0.757). Variant c is an estimate and cannot rescue a pre-registered line. Decision: the quoted 0.68 is a W2-scored statistic (10 quarters 1Q24 to 2Q26) trained on 2023 quarters read from a stale vintage; with 1Q23 re-read fresh it sits at 0.757 (honest) or 0.841 (literal), above the 0.75 line, so no measured statistic keeps the index at survivor grade on either window (the W1-scored 2022Q1+ row was already 0.837), and the short-window-survivor label carries the revintaging caveat below, attached to the 1Q23 to 4Q23 training quarters.

### 2.4 T3: NYC Local Law 18 (`data/processed/regulatory_v2/nyc_ll18_t3.csv`, `nyc_monthly_reviews_by_vintage.csv`)

NYC files: 2023-03-06 mirror 1,110,024 reviews on 32,627 listings (dates to 2023-03-06); held 2025-09-01 980,152 reviews on 25,009 listings; held 2026-08-10 994,127 on 21,925.

| Item | Value | n |
|---|---|---|
| r_pre: pooled 2025 / 2023 ratio on Sep 2022 to Jan 2023 (NYC pre-LL18 history surviving in the Sep 2025 dump) | 0.434 | 5 months, 158,747 reviews in the 2023 vintage vs 68,871 |
| monthly r_pre, Jun 2022 to Jan 2023 (flatness check) | 0.447, 0.447, 0.451, 0.443, 0.439, 0.436, 0.426, 0.420 | 8 months |
| A: pre-LL18 flow Sep 2022 to Aug 2023, attrition-corrected | 409,982 | 158,747 measured + 108,996 / 0.434 |
| A uncorrected (as it sits in the 2025 dump) | 177,867 | 12 months |
| B raw: Sep 2023 to Aug 2024 in the 2025 dump | 120,504 | 12 months |
| r_post (E table 2.2, 12 to 24 month history) / NYC-specific sensitivity (2026-08 over 2025-09, same months) | 0.86 / 0.870 | 12 months |
| B corrected | 140,121 (sens. 138,474) | 12 months |
| T3 = B / A - 1 | -65.8 percent (sens. -66.2; uncorrected -32.3) | band -70 to -40: PASS |
| CRA benchmark, guest-nights Sep 2023 to Aug 2024 vs prior year (6.56 M to 2.88 M) | -56.1 percent | two annual guest-night figures; Airbnb-commissioned, Dec 2024 |
| Cross-check: Jan 2024 Kaggle file `number_of_reviews_ltm` sum, Jan 2023 to Jan 2024, as of 5 Jan 2024 | 225,268 | 20,758 listings |
| same window counted in the 2025-09-01 dump | 161,016 (ratio 0.715) | 161,016 reviews in the Jan 2023 to Jan 2024 window |

The cross-check is consistent with the construction: the Jan 2023 to Jan 2024 window mixes 8 pre-LL18 months (surviving at 0.43) with 4 post months (surviving at about 0.87), and 0.715 sits between. The NYC pre-LL18 history is 57 percent gone from the current dumps because the listings LL18 removed took their review logs with them; an uncorrected NYC y/y read in any 2025 or 2026 dump understates the LL18 hit by half.

Bracket (`data/processed/regulatory_v2/nyc_ll18_bracket.csv`; listings on the reviewed-in-trailing-365-days basis only):

| Date | Basis | Listings reviewed LTM | Min-nights >= 30 share | Entire-home share | OSE-STRREG licences | Reviews LTM | Review flow 12m (corrected where stated) | Source |
|---|---|---|---|---|---|---|---|---|
| 2023-03-06 | reviews dump | 21,456 | n/a | n/a | n/a | 331,374 | 331,374 | Inside Airbnb via HF mirror |
| 2023-08-31 | T3 window A (Sep 2022 to Aug 2023), corrected | n/a | n/a | n/a | n/a | 177,867 raw | 409,982 | this note |
| 2024-01-05 | listings file, curated Kaggle subset, reviews_ltm > 0 | 16,148 | 0.851 | 0.556 | 1,054 | 225,268 | 225,268 | Tracey-Sneed re-upload of the Inside Airbnb 2024-01-05 dump |
| 2024-08-31 | T3 window B (Sep 2023 to Aug 2024), corrected by 0.86 | n/a | n/a | n/a | n/a | 120,504 raw | 140,121 | this note |
| 2025-09-01 | reviews dump | 10,918 | n/a | n/a | n/a | 145,073 | 145,073 | held |
| 2026-08-10 | reviews dump; shares from the same-date listings dump (30,234 listings) | 10,720 | 0.808 | 0.552 | 2,284 | 144,476 | 144,476 | held |

Reviewed-active listings fell from 21,456 (Mar 2023) to 16,148 (Jan 2024, curated file) to 10,918 (Sep 2025): -49 percent over the bracket, with the trailing-12-month review count at 145 k in both 2025 and 2026 against 331 k in the year to Mar 2023 (-56 percent, a number that is un-attrited on both ends because each is read at its own dump).

## 3. What failed or could not be done, and why

- T1 and T2 failed their pre-registered lines (sections 2.1, 2.2). Neither result is deleted; the T2 band is additionally recorded as mis-set at the time of writing.
- The literal T1 fail-branch rule ("substitute 4Q22 and 1Q23") cannot be executed cleanly: 4Q22 is outside the 2023Q1+ window and 1Q23 has three complete months in only 7 of 114 markets. Variant b (Jan-Feb 2023, 103 markets) is reported as the honest reading and both fail the 0.75 line.
- The 2023 vintage supplies no quarter inside the scored range (1Q24 onward), so it cannot add a scored quarter to either window; its value is the wedge measurement, as the lane spec said.
- The Feb 2023 month is dropped for the 11 markets whose dump is dated before 14 Mar 2023 (NYC, SF, LA, Venice, Amsterdam, Toronto, New Orleans, Tasmania, Sydney, Melbourne, Paris) under the 14-day completeness rule (Feb 28 + 14 days = 14 Mar, so the 14 Mar dumps of London, Barcelona and Vancouver keep it). n is stated per row.
- The 2026-08-10 NYC listings dump's licence column is free text; the licence count uses a case-insensitive `OSE-STRREG` prefix (2,284) and is not comparable one-for-one with the Kaggle file's cleaned column (1,054).
- `python` (the repo venv) lacks pyarrow on this machine; every step ran under `py -3.13`, as the v1 E scripts document. `run.py` passes its own interpreter down.
- Not done: the party-size cohort check on the 2023-vintage comments (lane spec, optional), the Barcelona and ChicagoBooth ladders (separate lane rows).

## 4. Interpretation

1. The stays index's key assumption, a survivorship wedge constant in the age of the review month, does not hold across eras. The wedge is a hazard of about 15 percent a year (T2, consistent with E table 2.2), but the hazard is higher for the months just before a dump (those months are richer in young listings, which churn), so a within-vintage y/y whose numerator month is 0 to 3 months old at the dump is measured on a different wedge from one whose numerator is 30 months old. In the v1 index the 1Q23 to 4Q24 quarters are read at 8 to 32 months of age inside the 2025 dumps and the 2025 to 2026 quarters at 0 to 14 months; the fresh-read T1 gap of -10 pp at +90 percent growth scales to roughly -1.5 to -2 pp at the +25 percent growth of the 1Q23 to 4Q24 quarters read inside the 2025 dumps (multiplicative factor 0.947). That is the size of the naive RMSE (2.16 pp), so it matters for a walk-forward whose training set is those quarters.
2. Applied consequence: the E note's line "beats naive on 2023Q1+ (0.68)" becomes "0.68 is a W2-scored statistic (10 quarters 1Q24 to 2Q26) whose 1Q23 to 4Q23 training quarters are read from a stale vintage; with 1Q23 re-read from the fresh 2023 vintage it is 0.757 (honest) or 0.841 (literal), above the 0.75 line; short-window survivor with a revintaging caveat on those training quarters, and no separately measured statistic keeps it at survivor grade on either window (the W1-scored 2022Q1+ row is 0.837)". The 3Q26 nowcast band (nights +9.5 to +10.0 percent, `docs/q3nowcast/SYNTHESIS.md`) is not changed by this: it rests on the vintage-matched construction (2026 dump over 2025 dump at the same age) which T1 does not test and which is symmetric in age by construction.
3. Vintage-matched is the right primary. The fix is not a bigger correction table but reading every quarter at the same age from its own dump, which the team can do from Aug 2025 onward (two vintages) and, with this mirror, for 4Q22 and Jan-Feb 2023 as well. Anything in between (Mar 2023 to Jul 2025) needs the missing dumps (Inside Airbnb data request form; already recommended in `research/notes/2026-09-05_inside-airbnb-supply-panel.md`).
4. NYC: -65.8 percent on Inside Airbnb review flow is an independent corroboration of the CRA -56.1 percent guest-nights figure and lands on the harsher side of it (reviews per stay may themselves have fallen among the surviving, mostly 30-night-plus listings: 81 to 85 percent of NYC listings now carry a 30-night minimum, so a review counts a longer stay). The regulatory note can cite the bracket with its bases; it still forecasts nothing.
5. Parameter count: zero fitted parameters in T1 to T3 (ratios of counts); the E5 re-run uses the one-slope OLS of E5 unchanged.

## 5. Harness change requests

1. The stays-index quotation ("0.68 vs naive, 2023Q1+, 10 quarters") should carry, wherever it is quoted (E note section 1 item 1, `docs/q3nowcast/SYNTHESIS.md`, the scoreboard narrative), the caveat: "W2-scored (10 quarters 1Q24 to 2Q26, 1Q23 to 4Q23 training); the within-vintage 1Q23 to 4Q24 values (2023 training quarters and 2024 scored quarters) are read at 8 to 32 months of age; a fresh-vintage re-read of the 2022-23 year is 5 percent higher on the growth factor (WPK note T1), and re-reading 1Q23 fresh moves the ratio to 0.757 honest / 0.841 literal, above the 0.75 line; short-window survivor with a revintaging caveat on the 2023 training quarters, no separately measured statistic at survivor grade on either window". No registry row exists for the stays index in `data/processed/forecast_methods/registry/`, so no registry file changes; if one is ever registered, register the vintage-matched construction under a new method name (e.g. `stays-index-v2__nights_yoy_vmatch`), FORMAT 1.0, and re-run `harness/score.py`.
2. The harness README could add a "vintage age" field to the point-in-time declaration for any feature built from cumulative logs (reviews, listings): the age of each training observation at its read date, so that an age-dependent wedge is visible at registration.
3. E table 2.2 should be cited as a hazard of about 15 percent a year that compounds (0.66 at 29 months, 0.60 at 39 months), not as a flat 0.85 wedge; and the note that the hazard is higher for the most recent months (0.63 vs 0.71) belongs beside it.

## RESUME

Next agent: (1) the E note owner (Krish) decides the wording of the revintaging caveat (section 5 item 1) and applies it in a dated correction line in the E note and `WORKBOARD.md` "Corrections" (do not edit the E note body); (2) if the team wants the stays index back at survivor grade on either window (a fresh 2023 training set for the W2-scored run, or 2022 training quarters for a W1-scored run), build the vintage-matched index for 4Q22 and Jan-Feb 2023 from these files (V3 already writes the wedge pairs; `market_monthly_yoy.csv` in the v2 folder carries the 2023-vintage rows) and file the Inside Airbnb data request for the Mar 2023 to Jul 2025 dumps; (3) the regulatory package owner cites `data/processed/regulatory_v2/nyc_ll18_bracket.csv` (row bases as stated) beside the CRA benchmark in REG-01; (4) optional, from the lane spec: run the party-size regex flags on the 2023-vintage comments by region x quarter as the pre-attrition cohort check, and add the Barcelona (montera34) and ChicagoBooth 2015 ladders to `t2_attrition_by_age.csv` to pin the hazard at 4 to 10 years. Raw store: `C:/Users/krish/abnb_ia_capture/ia_reviews_vintage2023/` (4.88 GB, manifest with sha256 in the v2 folder); rebuild with `py -3.13 analysis/src/q3nowcast_v2/E/run.py --skip-download`.
