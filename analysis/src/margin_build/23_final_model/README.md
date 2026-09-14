# 23_final_model — WS23 triangulation: the final margin model

The combination of every surviving margin object in the run, its line decomposition, the full
3Q26-4Q27 / FY26-28 forecast set, the cyclicality analysis, the 5 Nov card and the workbook.

## Run

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/23_final_model/run.py       # ~4 min, exit 0
MARGIN_SKIP_SCORE=1 py -3.13 analysis/src/margin_build/23_final_model/run.py   # without the scorer
```

**Interpreter: `py -3.13`** (pandas 2.3, numpy, scipy, openpyxl). The repo venv `python` has no
scipy and no openpyxl and will not run this package.

**Never run this concurrently with another method package.** `run.py` ends by calling the margin
harness `score.py`, and so do M1-M7; two concurrent scorers produced the exit-127 collision in
WS20 section 10.

## Files

| file | what it does |
|---|---|
| `prereg.json` | the pre-registration: member pool, weight rule, clip rule, specs, pass line, n_params. Written before any result. |
| `combine.py` | leave-future-out inverse-MAE weights with shrinkage to equal weights, plus the zero-parameter management-sentence clip; PIT and full_sample replays; conformal quantiles from the combination's own PIT errors; registers `final-margin__combined`. |
| `diagnostics.py` | leave-one-member-out, the no-clip variant, the Street-independent variant, shock vs calm. |
| `forecast.py` | line decomposition reconciled to the adopted EBITDA, the full P&L / bridge / FCF, annuals, scenarios, cyclicality, the 5 Nov card, the budget identity. |
| `workbook.py` | writes `model/ABNB_margin_model.xlsx` (README, Inputs, Lines, Bridge, Scenarios, Consensus, Seasonality, Weights, Card). |
| `run.py` | all of the above in order, then `score.py` once. |

## Outputs

`data/processed/margin_build/23_final_model/`:
`23_combination_by_quarter.csv`, `23_combination_weights.csv`, `23_combination_scores.csv`,
`23_combination_live.csv`, `23_conformal.csv`, `23_path_rule.csv`, `23_bands.csv`,
`23_lines_quarterly.csv`, `23_forecast_quarterly.csv`, `23_forecast_annual.csv`,
`23_vs_consensus.csv`, `23_scenarios.csv`, `23_seasonality.csv`, `23_macro_sensitivity.csv`,
`23_fy26_floor_breakeven.csv`, `23_card_5nov.csv`, `23_card_budget_identity.csv`,
`23_diag_leave_one_out.csv`, `23_diag_member_scores.csv`, `23_diag_shock_vs_calm.csv`,
`23_diag_street_independent_live.csv`.

Registry: `data/processed/margin_build/registry/final-margin__combined.csv` (1,152 rows,
four specs, PIT and full_sample replays, W1 / W2 / LIVE).

Workbook: `model/ABNB_margin_model.xlsx`. Note: `docs/margin-build/SYNTHESIS.md`,
`docs/margin-build/notes/23_triangulate.md`.

## Inputs (all read-only)

- `data/processed/margin_build/10_harness_margin/{scoreboard_by_quarter,scoreboard_margin,targets,guides_margin}.csv`
- every `data/processed/margin_build/registry/*.csv` (LIVE rows, vintage 2026-09-11)
- `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv`, `06_annual_fy26_fy28_v2b.csv`, `06_consensus_quarterly_2027.csv`
- `data/processed/margin_build/M1_driver_lines/M1_driver_lines_live_quarterly.csv`
- `data/processed/margin_build/M7_below_ebitda/M7_live_waterfall_quarterly.csv`, `M7_below_ebitda_annual_forecasts.csv`
- `data/processed/margin_build/03_consensus_pit/03_current_consensus.csv`
- M6 constants (`k` elasticities) are hard-coded in `forecast.py` with their source in the comment and
  reproduced on the workbook Inputs sheet; they come from
  `data/processed/margin_build/M6_cycle_flex/M6_cycle_flex_k_table.csv` (sample 1Q22+, weighting rw, spec lag0).

No licensed data is read or written by this package.
