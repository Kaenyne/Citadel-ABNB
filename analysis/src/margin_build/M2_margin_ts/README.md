# M2_margin_ts — time-series and ratio methods for the margin and the lines (method `margin-ts`)

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M2_margin_ts/run.py              # rebuild everything, rescore, figures; exit 0
py -3.13 analysis/src/margin_build/M2_margin_ts/run.py --no-sarima  # same without object 5 (faster)
py -3.13 analysis/src/margin_build/10_harness_margin/score.py       # rescore only
```

Interpreter: `py -3.13` (pandas 2.3, numpy, statsmodels for SARIMAX, matplotlib for the two figures).

Inputs: the margin harness (`analysis/src/margin_build/10_harness_margin/`: targets, PIT slice, revenue leg, guides, registry),
WS06 `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_wide.csv` (revenue and nights by quarter and scenario;
`06_revenue_path_3q26_4q27_v2b.csv` overrides it when present), WS06 `06_consensus_quarterly_2027.csv` (LSEG comparison column).

Outputs: `data/processed/margin_build/M2_margin_ts/` (grid at every vintage, params by vintage, LIVE quarterly forecasts base/bear/bull,
annual FY26-28, scoreboard extract, run log); registry files `data/processed/margin_build/registry/margin-ts__<object>.csv`;
figures `analysis/figures/margin_build/M2_margin_ts_*.png`; note `docs/margin-build/notes/M2_margin_ts.md`.

Objects, specs, parameter counts and the pre-registered pass lines are in the note.
