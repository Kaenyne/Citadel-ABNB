# returns_v1 — executable next-open returns around every ABNB letter

**Why:** the Lane 1 guide-surprise (A) and term-structure (B′) tests could not report a return leg because the only reactions
file in the repo (`data/processed/abnb_earnings_reactions.csv`) is close-to-close and has no `open_*` columns. This package
gives every brief one executable convention and one file to cite.

**Source:** Yahoo Finance daily bars via `yfinance` (public, no login), raw / unadjusted Open and Close, ABNB and QQQ,
from 2020-12-01. `manifest.json` records the retrieval timestamp, version and SHA-256. ABNB has no dividends or splits;
QQQ's dividends make its raw 20-day return a few basis points below total return — immaterial here and stated.

**Convention** (also in the module docstring): event = letter date (after the close) · entry = first trading day after, at the
OPEN · `open_{1,5,20,60}d_pct` = close h bars later ÷ entry open − 1 · `excess_open_*` = ABNB − QQQ · `gap_pct` = overnight move
(reported for reconciliation, never executable) · `cc_1d_pct` = legacy close-to-close for tie-out.

```bash
python analysis/src/forecast_methods/returns_v1/run.py             # rebuild from the committed OHLC (offline, exit 0)
python analysis/src/forecast_methods/returns_v1/run.py --refresh   # re-fetch OHLC first (internet)
python -m pytest analysis/src/forecast_methods/returns_v1/tests -q
```

Outputs under `data/processed/forecast_methods/returns_v1/`: `ohlc_daily.csv`, `earnings_reactions_open_v1.csv` (23 events,
2020Q4 print → 2026Q2 print), `manifest.json`. Nothing existing was modified.
