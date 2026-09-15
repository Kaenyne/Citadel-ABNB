# WS06v: independent check of the FY27 revenue path v2

Re-derives 1Q27-4Q27 (nights, ADR ex-FX, FX points, GBV, take rate, revenue; base / bear / bull / FX variants /
one sensitivity) from the same inputs WS06 was given, without reading WS06's script or note first, then diffs
WS06's `06_revenue_path_3q26_4q27.csv` line by line and writes the `_v2b` correction.

Run from the worktree root (repo venv, no openpyxl or scipy needed):

```
python analysis/src/margin_build/06v_fy27_path_check/run.py
```

Exit code 0, about 5 s. Reads only existing CSVs: bridge v3, KPI panel, PR #32, WS10, WS-D, ADR v3 card terms,
seats dilution, the WS-B daily FX file (for the ADR-FX estimators on held spot), fx_lag_v2 (23b for the revenue-FX
line), WS29, l1-reconciliation-v2, WS03 consensus (comparison only), and WS06's outputs (for the diff and v2b).

Outputs, `data/processed/margin_build/06v_fy27_path_check/`:

| file | what |
|---|---|
| `06v_independent_path.csv` | the independent path, long format (quarter, scenario, line, value, unit, source), 3Q26-4Q27 + FY26/FY27/FY28 |
| `06v_independent_path_wide.csv` | same, one row per quarter x scenario, with the nights decomposition parts |
| `06v_diff.csv` | quarter, scenario, line, ws06, mine, diff, tolerance, is_finding, explanation |
| `06v_4q26_exit_rederivation.csv` | the 4Q26 exit on the v2 decomposition (8.111 / 8.145 vs 8.12 adopted) |
| `06v_fx_adr_estimators.csv` | EUR fit, regional baskets and midpoint ADR-FX for 3Q26-4Q27 on held spot, +/-5% variants |
| `06v_fx_revenue_reconciliation.csv` | my basket reconstruction vs the kernel's (does not reproduce; the 23b table is read instead) |
| `06v_assumptions.csv`, `06v_pass_line.csv`, `06v_seasonal_check.csv` | assumptions (name, value, unit, source, is_judgement), pre-registered checks, seasonal shares |
| `06v_comparison_quarterly.csv`, `06v_comparison_annual.csv` | vs PR #32, WS29, B3, consensus (columns, never inputs) |
| `06_revenue_path_3q26_4q27_v2b.csv`, `06_annual_fy26_fy28_v2b.csv`, `06_v2b_changes.csv` | WS06's path with the one correction (3Q26 bear/bull revenue = INT-01 80% band); copies also placed in `06_fy27_path_v2/` as new files |

Note: `docs/margin-build/notes/06v_fy27_path_check.md`.
