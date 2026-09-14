# 20_scoreboard — WS20, the scoreboard and comparison of every margin method

Overseer package for the margin build run (13-14 Sep 2026). It compares; it does not refit anything.
Inputs: `data/processed/margin_build/10_harness_margin/` (scoreboard, by-quarter errors, targets,
revenue leg) and `data/processed/margin_build/registry/*.csv` (all 32 registered objects), plus
WS03 consensus, WS30 walk and WS31b profiles for the LIVE table.

## Run

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/10_harness_margin/score.py    # only if the registry changed
py -3.13 analysis/src/margin_build/20_scoreboard/run.py          # ~60 s, exit 0
```

Interpreter: `py -3.13` (pandas 2.3, numpy). `run.py` runs the eight build steps in order and
writes only into `data/processed/margin_build/20_scoreboard/`.

## Steps and outputs

| step | writes |
|---|---|
| `build_master.py` | `20_scoreboard_master.csv` — one row per (method, object, spec, target, window, horizon, weighting): n, MAE, RMSE, bias, CRPS, coverage, ratios to all seven baselines, n_params, survival flags, PIT-vs-full_sample hindsight gap |
| `build_rankings.py` | `20_rankings_headline.csv`, `20_rankings_lines.csv`, `20_rankings_below_ebitda.csv`, `20_excluded_oracle_and_thin.csv`, `20_rank_disagreement.csv` |
| `build_live.py` | `20_live_comparison.csv`, `20_live_spread.csv`, `20_live_fy_margin_denominator.csv` |
| `build_correlations.py` | `20_errors_by_quarter_surviving.csv`, `20_error_correlations.csv`, `20_error_diversification.csv`, `20_shock_vs_calm.csv`, `20_hard_quarters.csv` |
| `build_combination.py` | `20_combination_backtest.csv`, `20_combination_scores.csv`, `20_combination_live.csv`, `20_combination_live_long.csv`, `20_combination_weights_live.csv` |
| `build_parameter_budget.py` | `20_parameter_budget.csv` |
| `build_line_vs_margin.py` | `20_line_vs_margin.csv` |
| `build_digest.py` | `20_rankings_digest.md` |

`20_runpy_status.csv` (exit codes and runtimes of every method `run.py`) is written by hand from the
run logs, not by `run.py`.

## Ranking rules (pre-registered in the note before the tables were read)

1. PIT replay only.
2. Oracle specs — `spec_id` containing `revknown`, `nightsknown` or `ebitda_known` — substitute a
   realised driver and are diagnostics, not forecasts. Excluded from every ranking; listed in
   `20_excluded_oracle_and_thin.csv`.
3. Minimum n: 8 in W1, 6 in W2. Thinner cells are never ranked (`margin-ts|q_sentence_direction`
   has n=1 at h=1 and h=2).
4. Rank on MAE, ties to the smaller `n_params`.
5. Objects that consume Street as an input (`street-bias`, the `street` baseline) are flagged
   `consensus_anchored` and also ranked separately (`rank_independent`).

Note: `docs/margin-build/notes/20_scoreboard.md`.
