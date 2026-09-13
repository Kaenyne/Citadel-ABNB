# Lane 2 LIVE score sheet

Recorded 13 September 2026 through FORMAT 1.1. Eighteen registry rows represent nine scenarios, each with PIT and full_sample replay labels. Dollar values are USD millions. LIVE entries are prospective scenarios and have no historical performance score.

| Method / object | Scenario | Target | Quarter | Vintage | Point, $M | Replays |
|---|---|---|---|---|---:|---|
| alpha-a2 / guide_mid_next_q | conditional_RNPL_ledger_scenario | guide_mid | 2026Q4 | 2026-09-13 | 3,158.227962 | PIT, full_sample |
| alpha-b2 / revenue_q_plus_2 | w_2over3_unseasonal_gbv_growth | revenue_musd | 2026Q4 | 2026-09-13 | 3,628.501834 | PIT, full_sample |
| alpha-b2 / revenue_q_plus_2 | w_2over3_unseasonal_gbv_growth | revenue_musd | 2027Q1 | 2026-09-13 | 4,456.648132 | PIT, full_sample |
| rnpl-v2 / revenue_next_q | exna | revenue_musd | 2026Q3 | 2026-09-13 | 4,766.049428 | PIT, full_sample |
| rnpl-v2 / revenue_next_q | exna | revenue_musd | 2026Q4 | 2026-09-13 | 3,185.195735 | PIT, full_sample |
| rnpl-v2 / revenue_next_q | team | revenue_musd | 2026Q3 | 2026-09-13 | 4,766.049428 | PIT, full_sample |
| rnpl-v2 / revenue_next_q | team | revenue_musd | 2026Q4 | 2026-09-13 | 3,185.195735 | PIT, full_sample |
| rnpl-v2 / revenue_next_q | theo | revenue_musd | 2026Q3 | 2026-09-13 | 4,766.049428 | PIT, full_sample |
| rnpl-v2 / revenue_next_q | theo | revenue_musd | 2026Q4 | 2026-09-13 | 3,203.184582 | PIT, full_sample |

Full row inventory: `data/processed/forecast_methods/lane2_validation_v1/after_repairs/live_format_1_1_rows.csv`; authoritative rows remain in the three named files under `data/processed/forecast_methods/registry/`.

A2 targets the November Q4 guide midpoint and uses the existing conditional Q3 GBV ledger scenario. Its kernel point remains $3,158.227962M; the fresh Yahoo/LSEG comparison is $3,161.02149M, captured 2026-09-13 15:20 UTC (n=36), giving S=-0.088374%. S&P $3,160M (2026-09-10) and Zacks $3,200M (2026-09-11) retain their older stamps.

B2 targets revenue before the guide cushion. Its extrapolation compounds the latest quarter by trailing year-over-year growth without a seasonal anchor; the resulting large levels are arithmetic sensitivities. Registry horizon_q uses the FORMAT calendar-quarter definition, while the package preserves horizon_from_print separately.

F exposes three conditional nights paths. Q3 revenue does not use contemporaneous nights in the inherited two-lag kernel. The Theo Q4 scenario withholds extra D1 leakage because its Q3 nights input already includes a cancellation adjustment; team and ex-NA rows include the gross stress. These different conditional constructions are explicit and should not be ranked as three estimates of the same incremental loss.

At scoring, retain method, object, scenario ID and replay separately; the frozen scorer currently excludes LIVE rows and does not group by scenario ID. Do not pool the F scenarios into one forecast. The November guide is an A2 target; Q4 actual revenue arrives later. No team decision or trade instruction is adopted by this sheet.
