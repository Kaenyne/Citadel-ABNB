# H1/H2 bridge v2 — FX lines swapped to the programme's adopted estimators

Built 12 Sep 2026 by `analysis/src/h1_to_h2_bridge_v2.py` (a copy of the 10 Sep v1 script; v1 and
`data/processed/h2_bridge/` are untouched). Rebuild with:

```
python analysis/src/h1_to_h2_bridge_v2.py data/raw/fred
```

What changed against v1, and nothing else:

- `fx_pts_adr` for 3Q26 / 4Q26: ADR v3 midpoint estimator (mean of the EUR fit and the regional
  baskets, `data/processed/adrv3/N/N1_fx_choice_card.csv`) instead of the broad-USD single-factor fit.
- `fx_pts_revenue` for 4Q26: the fx_lag_v2 kernel output (Φ (0, ⅔, ⅓) × 0.851 on the revenue-weighted
  basket, spot held; `data/processed/forecast_methods/fx_lag_v2/23_forecast_4q26_v2.csv`) instead of
  the assumed 2.0. 3Q26 stays at management's stated ~3 after hedging.
- Every replaced value and every rejected construction is kept as a comparison column in
  `h2_bridge_v2_fx_line.csv`; `h2_bridge_v2_vs_v1_delta.csv` shows what moved.

All FX inputs are on FRED data through **2026-09-04** (H.10 publishes with about a week's lag).

The v1 interpretation notice still applies to everything that is not the FX line: the nights overlays
(RNPL lap, World Cup) are assumptions, not fitted effects, and were not re-based here. Read
`docs/RNPL_HANDOFF.md` and the note
`docs/revenue-forecast-strategy/05_backtests/FXSWAP_h2_bridge_kernel_fx.md` before quoting anything.
