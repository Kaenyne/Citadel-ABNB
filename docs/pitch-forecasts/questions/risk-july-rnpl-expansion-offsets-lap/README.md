# R03 — risk-july-rnpl-expansion-offsets-lap

**Question.** Will the 5 Nov print show both an RNPL GBV share ≥25% (C06 option a) and 3Q26 nights growth ≥ +10.0% (R01 Yes)? Binary. Resolution 5 Nov 2026. Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A09 with R01 and R02).** **P = 0.07**, credible interval 0.04–0.12.

**Why.** The joint is computed, not multiplied: C06's share model (2Q26 true share U(21,23), ex-US ramp, July expansion Exp(mean 1.4) capped at 6, Q3 lead-time drag) and R01's nights distribution share the July eligibility expansion as a common cause (RNPL module: +0.2pt of nights at the C06 mean expansion), and disclosure is more likely when nights are strong (C06: P(disclosed) 0.70 → 0.80 on an accelerating print). That gives P(nights ≥10 | share ≥25 disclosed) = 0.51 against the marginal 0.42, a joint of 0.074 versus 0.061 for the product of marginals. The cap is C06's P(a) = 0.15, and the number is bound by disclosure: the true share is ≥25 with probability 0.21, but management gives a 3Q26 GBV share only 0.70 of the time and rounds "over 20%" for anything in the low twenties.

**Impact if it happens.** R01's deltas plus the RNPL-drag rebuttal: 3Q26 nights +1.3pt, 4Q26 +1.2pt, FY27 +1.3pt, ADR +0.3pt (larger-home mix); 4Q26 revenue +$62M, FY27 +$211M; FY26 margin +0.5pp, FY27 +0.9pp; FY27 EPS +$0.20; stock +$22/share vs the base case. EV 0.07 × $22 ≈ **$1.6/share: material, marginally** (and a subset of R01's EV, not additive).

**Files.**
- `research-log.md` — full schema, joint model, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/a09_nights_error_distribution.py` (batch script, seed 20260917; `a09_r03_joint.csv` holds the joint and its eight variants) and its outputs.
- `sources/` — Kalshi ladder JSON, Polymarket search, Octagon mirror note, Finimize/B. Riley fragment on the expansion.

**Not submitted anywhere.** Next: Astra audit (`docs/pitch-forecasts/audits/A09-research-audit.md`), then revision 2.
