# M4_alt_augmented — does any external signal add to M1's driver-line model?

Method name in the margin registry: **`alt-augmented`**. Objects: `lines_aug`, `margin_aug`.

## Run

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M4_alt_augmented/run.py     # rebuilds everything, ~8 min, exit 0
```

Interpreter: **`py -3.13`** (pandas 2.3, numpy, matplotlib). The repo venv `python` also works for the
arithmetic but not for the figures; use `py -3.13`.

The script re-runs `analysis/src/margin_build/10_harness_margin/score.py` itself at the end and copies the
`alt-augmented` scoreboard rows into the package folder. No other package's files are touched.

## What it does

For each of the five cash lines it takes M1's `b_elastic_rw` line model **by import** (`M1_driver_lines/run.py`
is loaded as a module, never copied) and adds ONE external signal at a time:

```
d4 log L_q = g_L + b_L * d4 log D_q + c * x_{q-lead} + e_q
```

D = GBV (cor), nights (ops), revenue (sm), none (pd, ga); weights exponential, half-life 4 quarters.
`x` is a WS04 signal in y/y change form. **Strict knowability**: an observation enters the fit, and the signal
term enters a forecast, only if WS04's `knowable_from` for that quarter is `<= vintage_date`; otherwise the
quarter reverts exactly to M1 and the row is flagged. One extra series is built here (`trends_qtd4_share_{us,ww}`):
Airbnb's share of P1_peers category search over the weeks starting in the first 21 days of the quarter,
y/y, knowable ~day 28 of the quarter — the honest "Google Trends is a nowcast" construction.

Then: 50 pre-registered one-signal tests, 47 leakage placebos (lead 0 and +4-quarter future shift, run with the
knowability gate switched OFF so the placebo is informative), 1,000 random-series placebos, a `best1` composite,
an L2-penalised `ridge_all` composite, and a `none` spec that is bit-for-bit M1 so the delta is visible.

## Inputs

| what | path |
|---|---|
| M1 line model (imported) | `analysis/src/margin_build/M1_driver_lines/run.py` |
| M1 LIVE / annual comparison columns | `data/processed/margin_build/M1_driver_lines/M1_driver_lines_{live_quarterly,annual_forecasts}.csv` |
| WS04 signal panel + knowable_from | `data/processed/margin_build/04_alt_signals/04_signal_{panel_quarterly,knowable_from}.csv` |
| Google Trends weekly (for the QTD build) | `data/processed/overnight/08_trends_weekly.csv` |
| targets, calendar, windows, registry, revenue leg | `analysis/src/margin_build/10_harness_margin/` |
| revenue path for LIVE | via M1: bridge v3 (3Q26/4Q26) + WS06 `06_revenue_path_3q26_4q27_v2b.csv` |

## Outputs (`data/processed/margin_build/M4_alt_augmented/`)

| file | what |
|---|---|
| `..._signal_tests.csv` | one row per spec: line, signal, lead, kind (test / placebo_lead0 / placebo_future), c, t, n, IV at h=0 and h=1 in W1/W2 equal- and recency-weighted, `iv_pass`, `survives` |
| `..._iv_grid.csv` | the long IV table (every spec x window x horizon, line IV and margin IV) |
| `..._placebo_random.csv`, `..._placebo_summary.csv` | 200 random series per line; false-positive rate of the pass line, single and best-of-5 |
| `..._best1_selection.csv` | which signal was selected per line and its selection score |
| `..._coefs_by_vintage.csv` | every fitted g, b, c with se and t, per vintage and per spec |
| `..._forecasts_wide.csv` | every forecast row (backtest + LIVE, all specs, both replays) |
| `..._registry_long.csv` | the rows handed to `register()`, with quantiles |
| `..._live_quarterly.csv`, `..._live_margin_by_spec.csv` | LIVE 3Q26-4Q27 by spec and scenario, with consensus / WS31b / WS30 comparison columns |
| `..._annual_forecasts.csv` | FY26 / FY27 / FY28 by spec and scenario (annuals are not scored by the harness) |
| `..._trends_qtd_{us,ww}.csv` | the quarter-to-date Trends share series built here |
| `..._scoreboard_rows.csv` | the `alt-augmented` rows of `scoreboard_margin.csv` after rescoring |
| `..._build.json` | run stamp, row counts, test counts, survivors |

Figures: `analysis/figures/margin_build/M4_alt_augmented_iv_grid.png`, `..._placebo.png`.
Note: `docs/margin-build/notes/M4_alt_augmented.md`.

## Bottom line

One of 50 signals clears the pre-registered pass line (`ga` ~ private computer-systems-design employment,
2-quarter lead). The random-series placebo puts the false-positive rate for a single G&A test at 5.5% and for
best-of-5 selection at 22.5%, so that one survivor is inside the noise, and it improves the **margin** MAE by
0.6% (W1) / 0.1% (W2). **The LIVE margin table is M1's.** See the note for the full grid and the reasoning.

## WS22 discussion round (14 Sep 2026)

One change only: `MARGIN_SKIP_SCORE=1` now skips the `score.py` call at the end (three discussion agents
re-ran their packages concurrently; the orchestrator re-scores once), and a missing `scoreboard_margin.csv`
no longer raises. **Every M4 output is byte-identical after the re-run**, including both registry files -
confirmation that M1's R04 step gate does not touch the `b_elastic` base M4 builds on. M4 registers no
oracle spec, so R03 costs it nothing.

```bash
MARGIN_SKIP_SCORE=1 py -3.13 analysis/src/margin_build/M4_alt_augmented/run.py   # ~130 s, exit 0
```
