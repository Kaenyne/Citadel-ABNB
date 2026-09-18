# F04 — fy27-sm-share-above-219

Will Airbnb's FY27 sales and marketing expense ex-SBC be ≥ 21.9% of FY27 revenue in the FY27 10-K (~Feb 2028)? Binary.

- Forecast (revision 1, 2026-09-17): **P = 0.55**, credible interval 0.40–0.68. Conditional on the Feb 2027 FY27 margin guide (F03): (a) 0.25 / (b) 0.40 / (c) 0.52 / (d) 0.70 / (e) 0.55. Anchor 0.30 (Street-implied FY27 S&M ≈ 20.5%); |final − anchor| 25 points.
- Reference points: FY25 19.4%, 1H26 23.9%, FY26 line build 21.3%, FY27 line build 21.86% (just under the bar), the run's allocation 23.5%.
- Files: `research-log.md`, `forecasts/2026-09-17-forecast.json`, `datasets/f04_model.py` (numpy, seed 20260917), `datasets/f04_summary.csv`, `f04_sensitivity.csv`, `sm_share_history_annual.csv`, `sm_share_history_quarterly.csv`, `sources/` (market JSON, web query log).
- Batch A08 with F01, F02, F03.
