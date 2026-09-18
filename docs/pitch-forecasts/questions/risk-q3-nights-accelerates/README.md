# R02 — risk-q3-nights-accelerates

**Question.** Will 3Q26 nights growth print ≥ +10.6% y/y (≥147.8m), an acceleration against 2Q26's +10.34% under the positioning card's 0.25pt dead band? Binary. Resolution 5 Nov 2026. Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A09 with R01 and R03).** **P = 0.32**, credible interval 0.20–0.42.

**Why.** The same three views as R01, evaluated at 147.8m: the team's error-measured nowcast puts 0.17–0.27 above 10.6 (alt-data view 0.22); the outside view (a quarter-to-quarter acceleration of ≥ +0.26pt happened in 6 of 16 transitions since 3Q22, 3 of 4 Q2→Q3; management's guide midpoint is 11.0 and the floor-plus-cushion construction gives 0.50) lands at 0.44; the stale Kalshi ladder reads 0.54. Blend 0.60/0.30/0.10 = 0.32. An accelerating print is the memo's "thesis breaker" state and the one the historical reaction function pays +6% for; every measured outside series says the opposite through August, which is why the number sits well below the market's and the Street's (28 of 28 estimates at or above 10.0, mean 11.5).

**Impact if it happens.** 3Q26 nights +1.8pt (E[nights | ≥10.6] = 11.7 vs team 9.9), 4Q26 +1.1pt, FY27 +0.9pt; 4Q26 revenue +$65M, FY27 +$140M; FY26 margin +0.6pp, FY27 +0.6pp; FY27 EPS +$0.13; stock +$23/share vs the base-case day-1 (+$13 vs the unconditional). EV 0.32 × $23 ≈ **$7/share: material.**

**Files.**
- `research-log.md` — full schema plus `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/a09_nights_error_distribution.py` (identical copy of the batch script, seed 20260917; writes the same ten output files here) and its outputs.
- `sources/` — Kalshi ladder JSON (2026-09-17T03:21:58Z) and the Octagon mirror note.

**Not submitted anywhere.** Next: Astra audit (`docs/pitch-forecasts/audits/A09-research-audit.md`), then revision 2.
