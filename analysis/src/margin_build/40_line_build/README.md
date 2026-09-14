# 40_line_build: bottom-up margin build by cost item

```
py -3.13 analysis/src/margin_build/40_line_build/run.py
```

Exit 0 in about 40 seconds. Writes `data/processed/margin_build/40_line_build/` (params, quarterly lines, annual, backcast, sensitivities,
sentence-implied table, comparison with the run's allocated lines) and `model/ABNB_margin_line_build.xlsx` (a frozen report of the CSVs).

Built directly by the orchestrator on 15 Sep 2026 without subagents, after the 13-15 Sep run produced a calibrated top-down forecast but no
line-by-line view. The note is `docs/margin-build/notes/40_line_build.md`.

Inputs: `02_financial_panel/02_panel_quarterly.csv` (actuals 1Q23-2Q26), `06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv` and the
annual file (revenue path, base/bear/bull), `M7_below_ebitda/M7_parameter_sheet.csv` (below-EBITDA rules), and the 10-K / 10-Q facts quoted
in the parameter table (S&M split, payment processing, hosting commitments, MD&A component deltas for 1H26).

Every line is a formula on named parameters; every parameter has a source in `40_params.csv`. Cash lines are GAAP less SBC and still contain
D&A; adjusted EBITDA = revenue - sum(cash lines) + D&A + lodging-tax reserves, the WS02 identity, asserted at the end of the script.

Scenarios: `base` (reconciled to management's 3Q26 sentence), `evidence_only` (the same build without the reconciliation), `rev_bear` /
`rev_bull` (revenue path at base costs), `cost_bear` / `cost_bull` (base revenue at the adverse / favourable cost parameters), `both_*`.
