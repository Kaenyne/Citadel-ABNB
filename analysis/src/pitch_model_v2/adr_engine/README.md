# adr_engine — the ADR line v1 (line 2 of the official model)

Reported ADR y/y = **ex-FX mechanism** (core + product bundle lapping on filed dates + geo mix from the nights line +
unit size + LOS + seats + interaction) + **FX translation identity** (10-K GBV mix × frozen destination-currency
baskets × year-on-year of the booking-quarter average rate, ex ante with unobserved days held at spot).

Pre-registration (fixed before any fit): `docs/pitch-model-v2/lines/adr_fx_prereg.md`. Design: `adr_v1_design.md`.
Rationale: `final_adr.md`. Outputs: `data/processed/pitch_model_v2/adr_engine/`. Figures:
`docs/pitch-model-v2/lines/figures/adr_*.png|svg`. Workbook: `model/ABNB_official_model.xlsx` sheet `ADR_Engine`
and `Income_Statement` rows 8–11.

```bash
cd ~/Citadel-ABNB
PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run              # ≈ 3 min incl. the PyMC posterior; exit 0
PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run --no-posterior --no-workbook   # ≈ 20 s
PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/adr_engine/tests -q        # 10 tests
PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/adr_engine/fetch_fx.py               # FRED refresh (writes a new dated file; point config.FX_DAILY at it)
```

| module | what |
|---|---|
| `config.py` | paths, frozen baskets κ, priors, windows, pass line, decision dates, Street, nights line |
| `fetch_fx.py` | FRED H.10 refresh into this engine's own folder (never touches fx_lag / overnight files) |
| `fx_data.py` | daily FX → point-in-time quarterly averages (H.10 lag, spot held) → baskets → design rows; 10-K GBV shares with `knowable_from` |
| `exposure.py` | V0 translation (0 parameters); V1 pass-through (MAP / PyMC, interval likelihood); OLS comparators |
| `walkforward.py` | three origins × 14 targets × 6 variants; W1/W2 scores; block-bootstrap ratio intervals; the promotion rule |
| `forecast.py` | ex-ante forecast at the four decision dates; moving-block bootstrap band; ±5% USD device; currency contributions |
| `posterior.py` | full posterior of the regional pass-through (descriptive) |
| `exfx.py` | the ex-FX mechanism: history split into core / bundle, lap calendar, geo-mix arithmetic on the nights line, alternatives, envelope |
| `assemble.py` | reported ADR path, band, Street z / tail probability, GBV cross-check, scenario table |
| `figures.py` | seven figures (dataviz palette) incl. `adr_full_logic.png` |
| `workbook.py` | the `ADR_Engine` sheet + `Income_Statement` rows 8–11; runs the frozen nights builder unchanged and captures its workbook |

Nothing under `analysis/src/forecast_methods/`, `data/processed/forecast_methods/` or `data/processed/overnight/` is written.
