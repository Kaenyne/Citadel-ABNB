# reviews_index_v2 — the stays measurement and the final nights model

Session OLS.V2, 18 Sep 2026. Spec, pre-registration and results: `docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md`.

Run from this directory: `python3 run.py --stage freeze|A|B|C|D|E|F|figures|all` (all ≈ 15 s). Tests: `python3 -m pytest tests -q`
(the first test reproduces E5's 0.683209 on the v1 cell; nothing runs before it passes). Reads only committed inputs
(`q3nowcast/E`, `q3nowcast_v2/E`, `kernel_leadtime_v2`, Eurostat, KPI history, `overnight/02_kpi_panel_quarterly.csv`);
writes only to `data/processed/forecast_methods/reviews_index_v2/`.

| stage | module | question | output |
|---|---|---|---|
| A | `panel.py` | do review counts measure stays? (18 EU countries vs Eurostat observed nights) | `stage_a_tests.csv`, `panel_*.csv` |
| B | `stages.py` | does the vintage-matched, FY25-weighted index beat naive on the record's windows? | `stage_b_*.csv`, `index_quarterly_v2.csv` |
| C | `stages.py` | post-RNPL gap (print minus stays-implied) vs the pre-RNPL band; 3Q26 read | `stage_c_*.csv`, `stage_c3_3q26.json` |
| D | `did_power.py` | why no causal DiD (pre-trend, MDE, exploratory event study) | `stage_d_*.csv` |
| E | `view.py` | our numbers vs the Street; unearned fees vs GBV (the option written) | `stage_e_*.csv` |
| F | `final_model.py` | print = stays + option term; two channels (kernel landing, y/y lap); ceiling | `final_model_*.csv/json` |

Verdicts 18 Sep: A PASS · B PASS (W1 0.682 / W2 0.720) · C FAIL by the pre-registered line (gap +0.72 inside ±1.88) · D, E, F reported.
3Q26: stays +9.35 ± 1.88 (146.1m); print 9.35–10.94 by the writing term; Street 149.0 (+11.5%) = 12% tail. The RNPL hit: 4Q26 (level) and 2Q27 (y/y).
Figures in `figures/` (fig0 overview, fig1–fig8), copied beside the note.
