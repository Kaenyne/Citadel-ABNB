# Independent audit: PR40 calendars and PR41 calendars/external sources

Reviewed PR40 head `0324cace7172db757280988888f64f0d27c877f7` and PR41 head `5a590cedb42928666c580e06974947c301e2bbab` through GitHub. Files under `source/` and `data/` are evidence copies; repository production code was not changed.

## P2 — Align NTTO year-over-year changes by calendar quarter

Location: [G2_external_backtests.py, lines 119–124](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/G2_external_backtests.py#L119), with root cause in the positional `shift(k)` at lines 64–65.

The committed NTTO monthly CSV has no January–September 2022 rows. Grouping by the observed quarterly index and then shifting four rows does not compare with the same quarter one year earlier. For example, the reported 2023Q1 Western Europe first-month growth of 1,561.9% compares January 2023 (634,269 arrivals) with April 2021 (38,165), rather than January 2022. Across the three regions and two feature constructions, all 2023Q1–Q3 features are invalid, as are 2022Q4 features. Overseas full-quarter 2022Q4 growth is 84.6%, not 596.3%.

The exact original G2 code reproduced the committed NTTO feature columns within 1e-10. Reindexing the level series to a complete quarterly calendar before calculating growth makes the 2023Q1–Q3 values missing until the absent 2022 data are recovered. Using the original walk-forward functions, the headline overseas first-month nights specification changes from 0.7429× naive RMSE over 10 scored quarters to 0.8949× over 7. On the same seven quarters, the original wrongly trained model scores 0.7291× versus corrected 0.8949×. Total-arrivals first-month short-window RMSE changes from 0.7239× to 0.9646×.

The current ensemble median moves only from 9.2324% (12 specifications) to 9.3122% (13 specifications after the existing survivor-selection rule is rerun). The immediate risk is invalid historical skill and early training data, rather than a large current forecast change. Recovering the missing raw months could yield different final metrics. Fix calendar alignment and repair the input history, then regenerate G backtests, source scores and narrative claims.

Evidence: `reproduce.py`, `ntto_wrong_year_comparisons.csv`, `ntto_backtest_comparison.csv`, `reproduction_summary.json`.

## P2 — Freeze the calendar research windows before consuming newly downloaded vintages

Location: [A2_cross_market_analysis.py, lines 104–114](https://github.com/Kaenyne/Citadel-ABNB/blob/0324cace7172db757280988888f64f0d27c877f7/analysis/src/overnight2/A2_cross_market_analysis.py#L104), with the statistic at lines 140–145 and all-file discovery in A1 lines 117–126 / 263.

PR40 A1 discovers every calendar vintage in the shared raw directory and emits consecutive pairs. A2 assigns the fixed September–December / December–March / March–June / June–August labels using ordinal pair positions 1–4, and calculates the pre/post statistic from those positions. PR41 downloads 164 additional historical/monthly calendar vintages into that same directory. Of the 32 markets that originally had five snapshots, 29 now have more than five. A rerun with A1 `--overwrite` silently changes both the stable-listing cohort and the research windows; A2 has no date validation.

Concrete example from committed PR41 `F1_provenance.csv`: Austin now has 20 snapshots. Its first five dates are 2024-05-19, 2024-06-17, 2024-07-21, 2024-08-14, and 2024-09-13. Rebuilding A1 makes A2 label these four 2024 intervals as the 2025/26 pre/post windows. Sydney's extra August 2025 capture similarly shifts its June–August 2026 comparison out of the first four pairs. This does not prove the committed PR40 aggregates are wrong; it makes their recommended rebuild unstable after PR41. Use an explicit frozen capture manifest or date-selected research intervals, and reject incompatible vintages. Regenerate listing-cluster caches from the identical selected captures.

The complete 6.3 GB calendar corpus was not redownloaded or recomputed. The trigger is established from the exact source and committed provenance chronology. `reproduction_summary.json` records each market's first four pairs under rediscovery.

## P2/P3 — Source coverage scores overstate the months actually observed

Location: [G3_rank_sources.py, lines 172–184](https://github.com/Kaenyne/Citadel-ABNB/blob/5a590cedb42928666c580e06974947c301e2bbab/analysis/src/q3nowcast/G3_rank_sources.py#L172).

The function returns score 2 for July-only monthly sources despite its definition requiring both July and August for score 2. It also compares non-ISO quarter text lexicographically: `2026Q2 (released 9 Sep 2026)` receives score 3, defined as covering July, August and part of September. The committed source table and research note consequently mark Q2 Census revenue as September coverage and double July-only sources' rank contributions. Parse coverage periods explicitly and keep observation-period coverage separate from release dates. This changes source prioritization, not the numerical nowcast.

## Shared reproducibility issue for consolidation

G2 `MAIN` is fixed to `C:\Users\krish\citadel-abnb` (line 36). Calling the original `targets()` on the user's checkout fails with `FileNotFoundError` at line 52, even though the KPI file exists in the current repository. F2 has the same issue for its KPI input. Consolidate with any wider absolute-path finding from the other audit workstreams.

## Checks and boundaries

- Original A1 and F1 synthetic self-tests pass.
- NTTO original feature reproduction and corrected walk-forward calculations use the actual committed CSVs and original G2 fitting functions.
- F code clearly labels availability as a mixed blocked-calendar measure and rejects it as a nights forecaster; these disclosed limitations were not reported as new bugs.
- G's explicitly disclosed in-sample current fit and non-independent ensemble are not separate findings.
- Two externally cited STR sources were spot-checked through browsing: July levels/growth and week ending August 29 match their cited articles. The latter article also confirms the Labor Day shift caveat. No data-source mismatch established in those checks.

External spot-check URLs: https://lodgingmagazine.com/costar-reports-positive-u-s-hotel-industry-performance-results-in-july/ and https://lodgingmagazine.com/costar-u-s-hotel-industry-reports-20th-consecutive-week-of-positive-year-over-year-comparisons/.
