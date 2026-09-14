# M3 — guidance-policy model for the adjusted-EBITDA margin (`guide-policy-margin`)

Forecasts (1) the actual margin **given** the guide in force, (2) the **next guide sentence**
(5 Nov 2026 and the February FY27 floor), and (3) the **Q4 margin implied** by a November FY sentence.

## Run

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M3_guide_policy_margin/run.py       # ~40 s, exit 0, registers 2 objects
py -3.13 analysis/src/margin_build/10_harness_margin/score.py          # rescore (~4 min)
py -3.13 analysis/src/margin_build/M3_guide_policy_margin/make_figures.py   # also called by run.py
```

Interpreter: **`py -3.13`** (pandas 2.3, numpy, matplotlib). The repo venv `python` has no matplotlib.

## Inputs

`10_harness_margin` (targets, PIT slice, `fy_guide_in_force` / `q_guide_in_force`, `guides_margin.csv`,
`revenue_forecast_pit`, seasonal EBITDA shares, WS03 Street, the FORMAT 1.0 registry) and, for the LIVE
rows only, the WS06 v2b revenue path
`data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv` (base / bear / bull).
WS05's language pattern is used as a cross-check in the note, not as an input to any fit.

## Outputs — `data/processed/margin_build/M3_guide_policy_margin/`

| file | what |
|---|---|
| `M3_cushion_history.csv` | every realised (FY actual margin − guide level in force), by FY and guide bucket |
| `M3_february_haircut_history.csv` | every realised (February FY guide level − prior-FY actual) |
| `M3_grid_all_vintages.csv` | every point at every vintage / spec / replay, with quantiles and errors |
| `M3_guide_policy_margin_annual_forecasts.csv` | FY margin forecasts (backtest and FY26-28 LIVE) |
| `M3_live_forecasts.csv` | 3Q26-4Q27 by spec and revenue scenario |
| `M3_guide_forecast_november_backtest.csv` / `..._february_backtest.csv` | object 2 |
| `M3_q4_implied_backtest.csv` / `M3_q4_implied_live_5nov.csv` | object 3 |
| `M3_slightly_magnitude.csv` | the "slightly" adverb test M2 asked for |

Registry: `data/processed/margin_build/registry/guide-policy-margin__actual_given_guide.csv` (2,808 rows,
9 spec_ids × 2 replays, W1 / W2 / LIVE) and `guide-policy-margin__q4_implied.csv` (20 rows, W1 / W2).
Figures: `analysis/figures/margin_build/M3_guide_policy_margin_*.png`.
Note: `docs/margin-build/notes/M3_guide_policy_margin.md`.
