# adr_engine — the ADR line v1 (line 2 of the official model)

Reported ADR y/y = **ex-FX mechanism** (core + product bundle lapping on filed dates + geo mix from the nights line +
unit size + LOS + seats + interaction) + **FX translation identity** (10-K GBV mix × frozen destination-currency
baskets × year-on-year of the booking-quarter average rate, ex ante with unobserved days held at spot).

A second, sub-regional (country-level) geo-mix layer sits beside the four disclosed regional buckets:
pre-registration `adr_v2_geomix_prereg.md`, scoring `adr_v2_upgrade6_sustainability_and_score.md`.

Pre-registration (fixed before any fit): `docs/pitch-model-v2/lines/adr_fx_prereg.md`. Design: `adr_v1_design.md`.
Rationale: `final_adr.md`. Outputs: `data/processed/pitch_model_v2/adr_engine/`. Figures:
`docs/pitch-model-v2/lines/figures/adr_*.png|svg`. Workbook: `model/ABNB_official_model.xlsx` sheet `ADR_Engine`
and `Income_Statement` rows 8–11.

```bash
cd ~/Citadel-ABNB
PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run              # ≈ 3 min incl. the PyMC posterior; exit 0
PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run --no-posterior --no-workbook   # ≈ 20 s
PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run --no-refresh-prices             # geomix stage reuses the saved inputs
PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.refresh_prices                      # ≈ 14 s; rebuilds the geo-mix inputs only
PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/adr_engine/tests -q        # 27 tests
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
| `geomix.py` | the sub-regional term: within-region country mix `build_term`, GBV-weighted `subregional_term` |
| `refresh_prices.py` | rebuilds the sub-regional term's three inputs from the raw stores (see below) |
| `assemble.py` | reported ADR path, band, Street z / tail probability, GBV cross-check, scenario table |
| `figures.py` | seven figures (dataviz palette) incl. `adr_full_logic.png` |
| `workbook.py` | the `ADR_Engine` sheet + `Income_Statement` rows 8–11; runs the frozen nights builder unchanged and captures its workbook |

## The `geomix` stage (`run.geomix_stage`, after the ex-FX stage)

`run.py` calls `refresh_prices.main()` (skip with `--no-refresh-prices`), then builds the term, the H3 forward, the
four-region tilt table and the H2 scores, **verifies each against the file already on disk before overwriting it**
and prints the check. It writes `geomix_within_region[_forward].csv`, `geomix_country_contributions.csv`,
`geomix_subregional_term[_forward].csv`, `geo_mix_tilt_sensitivity.csv`, `geomix_h2_scores.csv`, and adds
`subgeo_4q26_pp`, `geo_mix_tiltB_4q26_pp` and a `geomix` block to `00_summary.json`. `exfx.alternatives()` runs
after it, because its composition scenarios read the two forward files. Three commented hook lines mark where
`geomix_eurostat` (upgrade 1), `od_layer` (upgrade 2) and `reconcile` (upgrade 3) will attach.

`refresh_prices.py` rebuilds, deterministically and in about 14 s:

| output | from |
|---|---|
| `market_currency_map.csv` | the E panel's 123 markets × the frozen `COUNTRY_CCY` map (Hong Kong = HKD); `fx_available` flags the FRED H.10 bilaterals |
| `stays_yoy_by_country_vmatch.csv` | `q3nowcast/E/market_monthly_yoy.csv`: `n_vm_cur` / `n_vm_prior` summed to country-quarter, a market counting only when all three of its months are present |
| `market_price_levels_capture_2026.csv` | the latest `listings.csv.gz` per market under `~/abnb_ia_capture/<country>/<state>/<market>/<dump>/`: entire-home, `number_of_reviews_ltm > 0`, median and review-weighted mean nightly price, converted at the 2026 calendar-year-average rate (FRED + ECB reference + Belize peg) |
| `country_price_levels_usd.csv` | `n_listed`-weighted mean of its markets' median USD price; markets below `MIN_USD_LEVEL = $5/night` dropped (the three Swiss dumps carry 0.16–0.18 CHF) |

It prints a coverage table (markets found / priced, countries priced, the unpriced lists) and the reproduction
check on `country_price_levels_usd.csv` — currently `max |diff| = 2.842e-14 USD on 30 countries -> OK to 3
decimals`. The three judgement constants (`COUNTRY_CCY`, `FX_YEAR`, `MIN_USD_LEVEL`) are frozen at the top of the
file. Scoring on 5 Nov 2026 and 11 Feb 2027 is pre-registered in
`docs/pitch-model-v2/lines/adr_v2_upgrade6_sustainability_and_score.md`.

`tests/test_geomix.py` (17 of the 27 tests) covers the mix arithmetic (sign, the zero when every country grows
equally, invariance to the price unit, contributions summing to the region mix), the three-month aggregation rule,
the currency map (every market mapped, HKD for Hong Kong, `fx_available` = the FRED set) and reproduction of the
filed term, forward and tilt table to 1e-6.

Nothing under `analysis/src/forecast_methods/`, `data/processed/forecast_methods/` or `data/processed/overnight/` is written.
