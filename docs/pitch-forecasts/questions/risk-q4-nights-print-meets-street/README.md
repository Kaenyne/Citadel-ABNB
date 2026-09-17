# R16 — risk-q4-nights-print-meets-street

**Question.** Will 4Q26 Nights and Seats Booked print ≥ 134.0m (≥ +9.93% y/y on 121.9m), the Bloomberg bar of 12 Sep 2026? Binary. Resolution ~11 Feb 2027. Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A12 with R10, R11, R15).** **P = 0.27**, credible interval 0.15–0.42.

**Why.** Three views disagree by 38 points and the number is a weighted reconciliation. The team's decomposition (4Q26 centre 8.1 after the global October-2025 lap, conditioned on R01's 3Q26 distribution, 12% short tail) gives 0.12: the bar needs a Q4 at the top of every repo model's band. The management-guide route (C02's 5 Nov bucket vector × Airbnb's record of printing at or above its nights bucket, 4 of 4 Q4 guides met, 4Q25 printed 9.8 after a "mid-single" guide) gives 0.37–0.47. The Street's own bar is 0.5 by construction, but it is the 2Q26 beat carried forward and will be reset on 5 Nov. Blend 0.5/0.3/0.2 = 0.27. Conditional reads: 3Q26 ≥10.6 → ~0.50; "low double digits" for Q4 on 5 Nov → ~0.85; "high single digits" → ~0.25.

**Impact if it happens.** E[Q4 | Yes] ≈ 10.7 vs the team's 8.1: 4Q26 nights +2.6pt (+$80M revenue), 3Q26 +0.6pt in the joint draw, FY27 revenue +$250M, FY26 margin +0.35pp, FY27 +1.05pp, FY27 EPS +$0.23; stock +$8–12 (joint solve plus the February reaction to a bar met). EV 0.27 × $10 ≈ **$2.7/share: material** — the second-largest risk line after R01.

**Coherence.** F01's tree (decomposition only) implies ~0.12 for this threshold; R16 adds the guide route and the anchor. X01 should adopt one 4Q26 distribution.

**Files.**
- `research-log.md` — claims ledger, query log, three estimates, conditionals, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json` — the number, estimates, conditioning, impact block, sensitivity, monitoring.
- `datasets/r16_model.py` — seeded (20260917) numpy script; outputs `r16_summary.csv`, `r16_views.csv`, `r16_conditional.csv`, `r16_sensitivity.csv`; `r16_revenue_consensus_5m_vs_actual.csv` (DoltHub five-month-ahead revenue consensus vs actual, from the L0 register).
- `sources/` — Kalshi KXABNBA / KXABNB ladders (2026-09-17T07:55:03Z; the 03:46Z files are the killed first attempt's pulls, kept for provenance).

**Not submitted anywhere.** Next: Astra audit, then a revision-2 response.
