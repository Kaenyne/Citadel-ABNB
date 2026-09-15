# Reviews pipeline audit — PR41, PR42, PR43

All findings below were reproduced against exact GitHub sources or committed output CSVs. No production source was changed. Run `reproduce_reviews_findings.py`; results are in `reproduction_results.json`.

## P2 — preserve transform in the walk-forward path and robustness key (PR41; inherited PR43)

Location: `analysis/src/q3nowcast/E5_backtest.py:162-164` and `:275-281`.

Paths drop the level/d1 transform key even though both are tested. If both beat naive, robustness pools their errors and removes one row rather than one scored quarter. The committed results contain 63 such collided groups, 31 for nights. Recovering each original model path reproduces all 463 source RMSE ratios within 3.33e-16. There are 63 individual variants, 31 for nights, whose true jackknife max exceeds 1 while the pooled max is at most 1. Example: EMEA|yoy_all|w_equal, lag1, nights,2023Q1+: pooled max0.9493 over20 rows; actual level max1.1167 and d1 max1.0190 over10 quarters each. The headline lag0 all-reviews result is unaffected. Include transform when writing and grouping paths and assert unique qi per model.

## P2 — correct the amount of Q3 actually observed (PR42)

Location: `docs/2026-09-11_q3-nowcast-explainer.md:33`.

The claim that windows cover60–65% of the quarter exceeds even the longest available window. The PR41 vintage-matched Q3 rows span19–47 days of92, median40 days(43.5%), prior-review-weighted38.24 days(41.6%). At PR43 the median is41 days(44.6%), with maximum still47 days(51.1%). The latest within-vintage cut could only reachAug17,48 days(52.2%). This understates the unobserved part of Q3. Replace the percentage with the actual window distribution and distinguish market-base coverage88–90% from temporal coverage.

## P2 — cap August windows at August31 before September refreshes (PR41; inherited PR43)

Location: `analysis/src/q3nowcast/E6_nowcast.py:145` and `:199`.

Both monthly constructors use dump-minus-lag as the end of the August row without a month-end cap. PR43 explicitly instructs users to rerun this pipeline when September dumps arrive. A2026-09-30 snapshot yields an August-labeled window Aug1–Sep16. Executing the unmodified function on a synthetic series where August is flat and September counts double produces a false August+34.04% instead of0%. Clamp the August row independently from the quarter-to-date row.

## P2 — estimate the median variant's own partial-to-full gap (PR41; inherited PR43)

Location: `analysis/src/q3nowcast/E6_nowcast.py:309`.

The median row receives the equal-weighted mean gap but is labeled measured. The committed per-market table gives median gaps for2023/24/25 of+0.854/−0.939/+1.605pp, mean+0.507 and sd1.307, instead of the used mean−0.610 and sd0.226. Changing only this gap input moves the median nights variant from9.203% to9.653% and its band from1.519pp to1.605pp. Effect on the seven-row mean is only+0.064pp, so this does not overturn the headline. Compute and carry separate median-gap columns or label the approximation explicitly.

## Disclosed analytical limitation, not counted as an undisclosed E5 bug

E5 marks every ABNB test `point_in_time=False` at line154. Full-quarter predictors are reconstructed from2025/2026 vintages, while the live Q3 inputs are partial-window data. The0.68 ratio verifies sequential coefficient fitting on retrospective completed-quarter predictors; it does not establish point-in-time live nowcast performance. PR42 line31 says “using only data before each quarter” and line49 encourages an out-of-sample pitch claim without this qualification. If included in the root audit, target those documentation claims and distinguish chronological fit from historical data availability.
