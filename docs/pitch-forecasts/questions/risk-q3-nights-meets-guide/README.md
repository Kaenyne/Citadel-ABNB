# R01 — risk-q3-nights-meets-guide

**Question.** Will 3Q26 Nights and Seats Booked growth print ≥ +10.0% y/y (≥147.0m on 133.6m), the floor of management's "low double digits"? Binary. Resolution 5 Nov 2026. Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A09 with R02 and R03).** **P = 0.42**, credible interval 0.30–0.55.

**Why.** The team's reviews-index nowcast, read honestly, is centred at 9.4–9.7 (the seven level rows bias-corrected by their own walk-forward errors) with an error sd of 1.5–1.9pp after the vintage caveat, which puts the ≥10.0 mass at 0.27–0.40 (alt-data view 0.33). Management has never missed a nights guide to the downside by more than 0.6pt in 16 tries, set this bucket on 6 Aug with July bookings in hand, and Q3 has not decelerated against Q2 in any of the last four years; that outside view gives 0.44–0.67 (used 0.55). The Kalshi ladder (P(>147.0m) ≈ 0.59) is quoted but has not repriced since 29 July. The blend 0.60/0.30/0.10 lands at 0.42. The asymmetry that keeps the number below 0.5 is the direction of the outside reads: hotels, TSA, CPI lodging, the external stack (+9.2) and EMEA stays all decelerate through August, and the index's two upside misses were product-driven accelerations that management had already flagged, which is not the case this quarter beyond an unquantified July eligibility expansion.

**Impact if it happens (memo base case).** 3Q26 nights +1.3pt (E[nights | ≥10] = 11.2 vs team 9.9), 4Q26 +0.8pt, FY27 +0.5pt; 4Q26 revenue +$50M, FY27 +$85M; FY26 margin +0.4pp, FY27 +0.35pp; FY27 EPS +$0.08; stock +$19/share vs the base-case day-1 (+$9 vs the unconditional). EV 0.42 × $19 ≈ **$8/share: material.**

**Files.**
- `research-log.md` — claims ledger, query log, three estimates, reconciliation, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json` — the number, estimates, impact block, sensitivity, monitoring (brief schema).
- `datasets/a09_nights_error_distribution.py` — seeded (20260917) script; rebuilds every table below for R01, R02 and R03 from the repo's E/E_aug/q3nowcast_v2 files. Outputs: `a09_rows_and_errors.csv` (seven rows, per-quarter walk-forward errors), `a09_alt_data_estimates.csv` (32 constructions), `a09_sd_sensitivity.csv`, `a09_base_rates.csv`, `a09_mgmt_delivery_view.csv`, `a09_three_views.csv`, `a09_weight_sensitivity.csv`, `a09_r03_joint.csv`, `a09_impact.csv`, `a09_final.json`.
- `sources/` — Kalshi KXABNB ladder (2026-09-17T03:21:58Z), Polymarket search, Octagon mirror note (29 Jul prices).

**Not submitted anywhere.** Next: Astra audit (`docs/pitch-forecasts/audits/A09-research-audit.md`), then a revision-2 response.
