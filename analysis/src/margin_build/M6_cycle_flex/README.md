# M6_cycle_flex — cycle and cost-flex model (`cycle-flex`)

How each cash cost line responds to revenue growth, and the scenario engine that maps bear/base/bull
revenue paths into cost paths and margins. Part of the margin build, 13-14 Sep 2026.

## Run

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M6_cycle_flex/run.py     # ~155 s, exit 0; calls the margin scorer at the end
```

`run.py` rebuilds everything: the seasonal decomposition, the pooled cyclicality regressions (`k` per line),
the peer `k` comparison, the point-in-time backtests at the 14 W1 / 10 W2 guide dates, the LIVE 3Q26-4Q27 path,
the bear/base/bull scenario engine, the FY26 floor break-even, and both registry files; then it runs
`analysis/src/margin_build/10_harness_margin/score.py`. It overwrites only its own outputs under
`data/processed/margin_build/M6_cycle_flex/`, the two `cycle-flex__*.csv` registry files, and the three
`analysis/figures/margin_build/M6_cycle_flex_*.png`. Verified byte-identical on a second run (13 Sep 14:44).

**Interpreter: `py -3.13`** (pandas 2.3, numpy, matplotlib). The repo venv `python` lacks matplotlib.

## Inputs

| what | path |
|---|---|
| targets, PIT slice, revenue leg, registry, scorer | `analysis/src/margin_build/10_harness_margin/` |
| revenue path 3Q26-4Q27 and FY26-28 (bear/base/bull) | `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv`, `06_annual_fy26_fy28_v2b.csv`, `06_consensus_quarterly_2027.csv` |
| Street consensus at TODAY | `data/processed/margin_build/03_consensus_pit/03_current_consensus.csv` |
| base cost path for the scenario engine | `data/processed/margin_build/M1_driver_lines/M1_driver_lines_live_quarterly.csv` (spec `b_elastic_rw`) |
| peer opex / S&M (LSEG, licensed, raw stays out of `data/processed`) | `data/raw/margin_build/04_alt_signals/misc/lseg_peer_opex_quarterly.csv`, `lseg_peer_sm_quarterly.csv` |

## Outputs (`data/processed/margin_build/M6_cycle_flex/`)

`M6_cycle_flex_k_table.csv` (121 regressions), `_params_by_vintage.csv` (k at every vintage),
`_peer_k.csv` (ABNB vs BKNG/EXPE/TRIP), `_seasonal.csv` + `_seasonal_stability_2022_25.csv`,
`_forecasts_wide.csv` (808 quarter-rows), `_registry_long.csv`, `_backtest_grid.csv`,
`_scoreboard_rows.csv`, `_scenarios_quarterly.csv`, `_annual_forecasts.csv` (FY26-28 x scenario x variant),
`_cut_solutions.csv`, `_fy26_floor_breakeven.csv`, `_test_2H22_reproduction.csv`, `_test_T3_rows.csv`,
`_build.json`. Registry: `data/processed/margin_build/registry/cycle-flex__flex_margin.csv` (1,872 rows)
and `cycle-flex__flex_lines.csv` (3,120 rows).

Note: `docs/margin-build/notes/M6_cycle_flex.md`.
