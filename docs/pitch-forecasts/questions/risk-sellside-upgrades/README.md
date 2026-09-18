# R12 — risk-sellside-upgrades

**Question.** Between 17 Sep and 15 Dec 2026, will ABNB receive ≥3 rating upgrades (to Buy/Outperform-equivalent) from firms in the tracked feed (`data/processed/reverse_dcf/D/` convention, yfinance/Benzinga `upgrades_downgrades`), or will the mean live target rise to ≥$190? Binary. Resolution 15 Dec 2026. Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A13 with R13 and R14).** **P = 0.42**, credible interval 0.30–0.55. Legs: ≥3 upgrades-to-Buy 0.25; mean target ≥$190 at any feed pull 0.29 (0.25 on 15 Dec alone); both 0.10.

**Why.** The tape follows the price with a one-to-two-month lag and re-rates same-day on prints (D note §5). Replicating S04's tape-lag block over the S02 print branches, the feed mean (base $183.22 with Morgan Stanley's $170) reaches $190 on 15 Dec with P 0.25 and touches it at some point with P 0.29 (the D panel's running-max premium of 1.12–1.22). Upgrades to Buy run at 9 per year in the trailing twelve months (8 in 2026 so far) against 4–5 per year in 2023–25; with 0.7 expected pre-print and 0.35–2.0 post-print by branch (they cluster on up prints), P(≥3) is 0.25. Joint over branches: accelerating print 0.68, decel-guide-below 0.30. The 2024+ 90-day base rate for ≥3 to-Buy upgrades is only 0.13, but the 2026 regime doubles it and the Buy share (59.5% on the 24-month panel, a series high) limits the pool of upgraders to about 13 feed firms.

**Impact if it happens.** No operating delta. The event is a marker of the print branch: E[15 Dec close | Yes] $176 vs $161 unconditional (+$15/share), but that is the 5 Nov branch already counted in R01/R02/S02, not an incremental force — analyst actions outside prints move the stock by nothing detectable (09 note §6). Incremental EV ≈ 0.42 × ~$1.5 = **$0.6/share: immaterial as a standalone line**; fold into the thesis-breaker scenario.

**Files.**
- `research-log.md` — schema log with claims ledger, query log, three estimates, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json` — the number, estimates, impact block, sensitivity, monitoring.
- `datasets/upgrade_base_rates.py` → `upgrade_base_rates.json`, `feed_upgrades_all.csv` — every "up" action in the feed with a to-Buy flag; 90-day window counts 2021+/2023+/2024+; print-window counts; same-calendar counts.
- `datasets/r12_model.py` → `r12_summary.json`, `r12_sensitivity.csv` — seeded (20260917) joint simulation of the two legs over the S02 branches (S04 tape block replicated).
- `sources/` — Kalshi and Polymarket snapshots (03:56Z), `web_search_log.md` (1 WebSearch, 1 WebFetch). Feed pull reused from `../sellside-mean-target-cut-by-15dec/sources/yfinance_upgrades_downgrades_20260917T031221Z.csv`.

**Not submitted anywhere.** Next: Astra audit (`docs/pitch-forecasts/audits/A13-research-audit.md`), then a revision-2 response.
