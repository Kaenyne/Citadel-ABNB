# WS06: FY27 quarterly revenue path v2

Audits the PR #32 three-feature lap on real quarters, re-bases 1Q27-4Q27 on the adopted 3Q26/4Q26 exit
(H2 bridge v3), and writes one path file for the margin model: quarter x scenario x line, 3Q26-4Q27,
plus FY26/FY27 annuals (bear/base/bull) and a flagged FY28 base-only continuation.

Run from the worktree root (repo venv; the figure step shells out to `py -3.13` for matplotlib and is optional):

```
python analysis/src/margin_build/06_fy27_path_v2/run.py
```

Exit code 0, about 3 s. Reads only existing CSVs (bridge v3, PR #32, WS10, WS-D, ADR v3 card/K4, seats, fx_lag_v2,
WS29, l1-reconciliation-v2, WS03 consensus, and the LSEG quarterly pull cached under `data/raw/margin_build/06_fy27_path_v2/`,
manifest at `data/manifests/margin_build/06_fy27_path_v2.csv`). Consensus is a comparison column only.

Outputs, `data/processed/margin_build/06_fy27_path_v2/`:

| file | what |
|---|---|
| `06_revenue_path_3q26_4q27.csv` | the object: long format (quarter, scenario, line, value, source), 3Q26-4Q28 |
| `06_revenue_path_wide.csv` | same, one row per quarter x scenario |
| `06_annual_fy26_fy28.csv` | FY25-FY28 sums by scenario (FY28 base only, flagged) |
| `06_nights_build.csv`, `06_adr_build.csv` | the growth-space decomposition behind every 2027 quarter |
| `06_assumptions.csv` | every parameter: name, value, unit, source, is_judgement |
| `06_pr32_rederivation.csv` | PR #32's numbers re-derived from its stated features, and the FY27 sums it never produced |
| `06_comparison_quarterly.csv`, `06_comparison_annual.csv`, `06_comparison_fy28.csv` | v2 vs PR #32, WS29, B3/l1-v2, reverse DCF, consensus (columns, never inputs) |
| `06_consensus_quarterly_2027.csv` | derived LSEG quarterly means (vendor, n, obs date, pull timestamp) |
| `06_seasonal_check.csv`, `06_pass_line.csv`, `06_kernel_lambda_history.csv` | checks |

Figure: `analysis/figures/margin_build/06_fy27_path_v2_quarterly.png` (`fig.py`). Note: `docs/margin-build/notes/06_fy27_path_v2.md`.
