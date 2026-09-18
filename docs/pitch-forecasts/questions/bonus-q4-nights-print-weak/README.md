# B13 — bonus-q4-nights-print-weak

Will 4Q26 Nights and Seats Booked print ≤ 131.0m (≤ +7.5% y/y on 121.9m)? Binary; resolves at the ~11 Feb 2027 print.

Revision 1 (17 Sep 2026, Fable, batch A17): **P = 0.26, CI 0.14–0.40**. This is the lower tail of R16's 4Q26 distribution (`../risk-q4-nights-print-meets-street/`), computed with R16's parameters unchanged so that X01 has one 4Q26 object (P(≤131.0m) 0.26 / P(≥134.0m) 0.27, mean ≈ 8.3). Impact if Yes: −2.0pt of 4Q26 nights, −$60M 4Q26 revenue, −$220M FY27 revenue, −0.9pp FY27 margin, −$0.20 FY27 EPS, ≈ −$10/share; EV ≈ −$2.6/share, material.

- `research-log.md` — the log (schema per the forecast skill), with the `## 9. Impact` table.
- `forecasts/2026-09-17-forecast.json` — the forecast in the brief's schema.
- `datasets/b13_model.py` — reproduction (numpy, seed 20260917, ~5 s; run from anywhere: `py -3.13 docs/pitch-forecasts/questions/bonus-q4-nights-print-weak/datasets/b13_model.py`), writing `b13_summary.csv`, `b13_views.csv`, `b13_conditional.csv`, `b13_sensitivity.csv`.
- `sources/` — Kalshi snapshots (2026-09-17T08:27:05Z) and the web-search log.
