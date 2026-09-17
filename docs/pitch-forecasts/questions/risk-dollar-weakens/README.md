# R10 — risk-dollar-weakens

**Question.** Will FRED DTWEXBGS on 11 Feb 2027 be ≤ 0.96 × its 16 Sep 2026 value (a ≥4% broad-dollar decline over 105 trading days)? Binary. Resolution 11 Feb 2027. Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A12 with R11, R15, R16).** **P = 0.09**, credible interval 0.05–0.15.

**Why.** A −4.08% log move in 105 observations is a 1.5-sigma draw at the trailing realised vol (4.1% annualised, the calmest quintile of 2006–2026) and 1.3-sigma at a judgement implied vol. The empirical 105-day distribution gives 0.12 unconditionally, 0.11 in the calm-vol quintile, 0.07 in a ±1pp band around today's vol; the parametric legs at realised vol give 0.05–0.08 with the Reuters-poll drift (−0.4% over the window); the implied construction gives 0.09–0.12. The Fed hiked on 16 Sep with three more priced, which argues for zero drift rather than the poll's mild dollar decline. Episodes of ≥4% declines cluster (2007, 2009, 2010, 2020, 2025) and none is on the calendar; the tail is a policy-shock tail, priced through the fat-tailed legs rather than a named branch.

**Impact if it happens.** E[move | Yes] = −5.6%: FY27 revenue FX +2.5pp (+$400M), FY27 margin +1.6pp, FY27 EPS +$0.37, 4Q26 revenue +$17M, ADR +4pt from 1Q27; stock +$5 (FX discounted) to +$10 (joint solve). EV 0.09 × $5 ≈ **$0.5/share: immaterial/borderline.** Keep FX as bridge arithmetic, not a risk line.

**Files.**
- `research-log.md` — claims ledger, query log, three estimates, sensitivity, pre-mortem, hazard table, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json` — the number, estimates, impact block, sensitivity, monitoring.
- `datasets/r10_model.py` — deterministic script (`py -3.13`); outputs `r10_summary.csv`, `r10_by_year.csv`, `r10_regime.csv`, `r10_tail.csv`, `r10_sensitivity.csv`, `r10_dtwexbgs_105d_windows.csv`.
- `sources/` — FRED DTWEXBGS/DEXUSEU/DTWEXAFEGS pulls (2026-09-17T07:54:53Z), yfinance DXY, EUR/USD and FX-ETF option chains, Polymarket and Kalshi searches. Earlier pulls from the killed first attempt (03:46Z/04:00Z) are kept for provenance and were not used.

**Open item.** The 16 Sep DTWEXBGS value posts on 21 Sep; the log uses 119.02 (DXY-beta estimate). Fix the threshold then.

**Not submitted anywhere.** Next: Astra audit, then a revision-2 response.
