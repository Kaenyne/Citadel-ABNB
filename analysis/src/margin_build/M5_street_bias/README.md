# M5_street_bias — method `street-bias`

The Street's adjusted-EBITDA consensus at the vintage date plus its systematic bias. This is the one
margin method allowed to use consensus as an input, because its object is the *surprise*.

## Run

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M5_street_bias/run.py           # build + analyse + figures, exit 0
py -3.13 analysis/src/margin_build/10_harness_margin/score.py      # rescore the registry
```

**Interpreter: `py -3.13`** (needs scipy, statsmodels, matplotlib; the repo venv `python` has none of them).
`run.py` re-runs `build.py` (registers the three objects), `analyse.py` (backtest, post-guide h=1
supplementary test, LIVE table, P(beat), annual roll-up) and `figures.py`.

## Objects (registered, method `street-bias`)

| object | rule | free params |
|---|---|---|
| `street_plus_bias` | `Street_q(vintage) + b(vintage, h)`; `b` = shrunk recency-weighted mean (or median) of the PIT-knowable surprises at the same horizon | 2 (+1 residual sd) |
| `street_plus_flowthrough` | `Street_q + a + m * (Rev_team_q - Rev_Street_q)`, `a`/`m` from a PIT weighted OLS of the $ EBITDA surprise on the $ revenue surprise, `m` shrunk to `m0 = 0.45`; margin = EBITDA / Rev_team | 5 (+1) |
| `dispersion_conditioned` | `street_plus_bias` with `b` and sigma scaled by `clip(disp / disp_ref, 0.5, 2.0)`, `disp = EBITDA sd / mean` at the vintage | 4 (+1) |

Targets `adj_ebitda_musd` and `adj_ebitda_margin_pct`; specs `rw_hl4` (primary), `ew`, `rw_hl4_usd`,
`ew_usd`, `rw_hl4_med`, `rw_hl4_from21`; replays PIT and full_sample. Street exists at **h = 0 and
h = 1 only** (WS03 roles `guided_q_pre_guide` / `next_q_pre_guide`), so there is no h = 2 backtest row.
LIVE 1Q27-4Q27 uses a Street quarterly path allocated from the FY27 consensus with the harness PIT
seasonal shares (spec suffix `_fyalloc`); those rows are never in a scored backtest cell.

## Outputs

`data/processed/margin_build/M5_street_bias/`: `M5_prereg.json`, `M5_grid_all_vintages.csv`,
`M5_parameters_by_vintage.csv`, `M5_surprise_panel.csv`, `M5_backtest_vs_street.csv`,
`M5_passline_verdict.csv`, `M5_h1_preguide_vs_postguide.csv`, `M5_h1_basis_summary.csv`,
`M5_h1_postguide_backtest.csv`, `M5_h1_postguide_scoreboard.csv`, `M5_live_forecasts.csv`,
`M5_live_all_specs.csv`, `M5_prob_beat.csv`, `M5_street_bias_annual_forecasts.csv`,
`M5_street_current.json`, `M5_secondary_tests.json`, `M5_street_fy27_allocation.csv`.
Registry: `data/processed/margin_build/registry/street-bias__{street_plus_bias,
street_plus_flowthrough,dispersion_conditioned}.csv`.
Figures: `analysis/figures/margin_build/M5_street_bias_{surprise_and_bias,mae_ratio,dispersion}.png`.
Note: `docs/margin-build/notes/M5_street_bias.md`.

No LSEG raw file is read by this package; it consumes WS03's derived, date-stamped tables only.
