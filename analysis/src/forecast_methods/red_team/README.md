# red_team — independent audit scripts

Recompute, from source only, the numbers the red-team note challenges.
These scripts import **no package code** on purpose.

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
python analysis/src/forecast_methods/red_team/run.py
```

* `rt_recompute.py` — rebuilds all 200 harness scoreboard cells from the 57 registry CSVs
  and `targets.csv`; prints the mismatch count (expected 0) and the 72 registry groups
  absent from `scoreboard.csv`.
* `rt_fx.py` — rebuilds the FX basket from `10_fx_daily.csv`, `10_fx_basket.csv` and
  `L0_exact_regional_revenue.csv`; fits lags 0/1/2 by interval likelihood on the
  letter-rounded integers; runs the LR tests and the LOO horse race.
* `rt_fx2.py` — falsifies the registered live 3Q26 FX point against the verified
  2026-08-06 letter and backtests the rival kernels on 1Q26 and 2Q26.

Findings: `docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md`.
Writes no data outputs and registers nothing.
