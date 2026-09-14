# fx_lag_v2 — the B4 FX exhibit

A COPY of `fx_lag/`, re-pointed at a fresh FRED pull and extended with the B4
exhibit. **Nothing under `analysis/src/fx_lag/`, `analysis/src/overnight/`,
`data/processed/overnight/`, `data/processed/forecast_methods/fx_lag/` or `docs/`
is read for output or written to.** Outputs go to
`data/processed/forecast_methods/fx_lag_v2/` and to two NEW registry files,
`fx-lag-v2__*.csv`.

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
python analysis/src/forecast_methods/fx_lag_v2/fetch_fx_v2.py
python analysis/src/forecast_methods/fx_lag_v2/run.py
```

`harness/score.py` is NOT run by this package.

| file | copied from | what changed |
|---|---|---|
| `fetch_fx_v2.py` | `analysis/src/overnight/10_fetch_fx.py` | output path -> `fx_daily_2026-09-11.csv`; DTWEXBGS broad USD added (`unit='index_level_usd_strength'`); fetch manifest |
| `common.py` | `fx_lag/common.py` | `OUT` -> `fx_lag_v2/`; `METHOD='fx-lag-v2'`; `FX_DAILY`, `FX_QUARTERLY`, `FX_LAST_OBS=2026-09-04` |
| `baskets.py` | `fx_lag/baskets.py` | reads the refresh, filters `unit`; broad USD from the refresh instead of the stale FRED cache; 3Q26 reconciliation row labelled as a refresh difference |
| `pit_fx.py` | `fx_lag/pit_fx.py` | reads the refresh; **`_q_avg_spot_held` fixed**: a business day with no FRED print takes the last rate observed on or before it, not the current spot |
| `fits.py` | `fx_lag/fits.py` | `object_a` also returns the 95% confidence-set grid in its `pack` |
| `stages.py` | `fx_lag/stages.py` | `forward_schedule` as-of defaults to `FX_LAST_OBS` |
| `panel.py` | `fx_lag/panel.py` | unchanged (reads `OUT`, which now points at v2) |
| `registry_out.py` | `fx_lag/registry_out.py` | new LIVE 4Q26 object; harness validator called strictly first, then with `strict_windows=False` only for the LIVE-window limit, which is printed |
| `exhibit.py` | — | NEW: the B4 tables 19-27 |
| `run.py` | `fx_lag/run.py` | new entry point for the above |

Note: `docs/revenue-forecast-strategy/05_backtests/B4_FX_EXHIBIT.md`
