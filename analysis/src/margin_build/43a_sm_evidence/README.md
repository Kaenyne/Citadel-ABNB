# 43a_sm_evidence — the statistics behind Thesis 3 (sales & marketing)

Pre-registered in `docs/margin-build/notes/43a_prereg.md`; write-up in `docs/margin-build/notes/43a_sm_evidence.md`.

Run from the repo root (exit code 0, ~5 s):

```
py -3.13 -X utf8 analysis/src/margin_build/43a_sm_evidence/run.py
```

Inputs (read-only): `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv`; the cached 10-Qs under
`docs/pitch-forecasts/questions/bonus-insider-selling/sources/tenq/` and the 10-Ks under `C:/Users/krish/citadel-abnb/data/raw/filings/`
(main tree; used only to verify the hard-coded S&M split table, skipped if absent); `data/processed/adr/04_regional_quarterly_wide.csv`
(modelled regional ADR, flagged as modelled).

Outputs in `data/processed/margin_build/43a_sm_evidence/`:

| file | content |
|---|---|
| `43a_h1_levels_elasticity.csv` | Jessie's log-log levels regressions reproduced (all five cash lines, 1Q22+), S&M on W1/W2, and the same with a linear trend; DW, residual AR(1), Breusch-Godfrey, Engle-Granger ADF |
| `43a_h1b_trend_ratio.csv` | trend growth of log S&M and log revenue (quarter dummies) and their ratio against the levels "elasticity" |
| `43a_h2a_growth_elasticity.csv` | y/y log-growth regression `g_sm ~ c + k g_rev` (HAC 3) on 1Q22+, W1, W2 |
| `43a_h2b_growth_gap.csv` | the pre-registered test: mean of `g_sm - g_rev`, HAC one-sided p, quarters positive, sign test |
| `43a_h2c_cagr_ratio.csv`, `43a_h2c_cagr_all_lines.csv` | CAGR of cash S&M vs revenue by span; the same for every cash cost line |
| `43a_h3_acceleration.csv`, `43a_h3_by_year.csv`, `43a_series_quarterly.csv` | trailing-4Q share, incremental S&M per revenue dollar, growth gap, and revenue / nights per incremental S&M dollar, with trend-on-time tests in W1/W2; the by-year table |
| `43a_h4_components_annual.csv`, `_halfyear.csv`, `_quarterly.csv`, `43a_h4_filing_verification.csv` | brand & performance marketing vs field operations & policy from the 10-K/10-Q tables (GAAP), growth, contributions, efficiency; the verification of every printed value against the cached filing |
| `43a_h5a_ccf.csv`, `43a_h5b_partial.csv` | lead/lag correlations of S&M (and marketing-only) y/y growth with nights y/y growth; the partial regression |
| `43a_h5d_regional_mix.csv` | share of incremental revenue from LatAm + APAC by year; modelled regional ADR |
| `43a_tests.csv` | every pre-registered pass line with its result and verdict |
