# R14 — risk-feb-print-up-day

**Question.** Will ABNB's close-to-close return on the first session after the 4Q26 print (expected 11 Feb 2027 after the close, so the 12 Feb session) be ≥ +5%? Binary. Resolution ~12 Feb 2027. Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A13 with R12 and R13).** **P = 0.30**, credible interval 0.20–0.42.

**The record, corrected.** Q4-print day-1 raw returns: 4Q20 +13.3, 4Q21 +3.6, 4Q22 +13.4, 4Q23 −1.7, 4Q24 +14.4, 4Q25 +4.6. That is **5 of 6 positive** (not the memo's "6 of 6", which is the calendar-February excess return), **3 of 6 at or above +5%** (not 4 of 6: 4Q25's +4.6 misses the bar), 5 of 6 ≥ +3.5%, mean +7.9, median +9.0. All prints: 6 of 23 ≥ +5% (0.26); post-2022: 3 of 14 (0.21).

**Why 0.30.** Three estimates: base rate 0.38 (the Q4 class 0.50 on n 6 blended with the all-print 0.26), decomposition 0.26 (the reaction panel's cells on the 4Q26 print sign and the 1Q27 guide vs Street, a Q4-print uplift carried at +3 points, a t5 residual at the options-implied Feb event sd 8.5–9.5%), anchor 0.27 (the risk-neutral symmetric distribution at that sd). The pull-down: both the team (8.1 vs 9.55) and the Street (9.9 vs 11.1) expect the 4Q26 nights print to decelerate against 3Q26, decelerating prints have closed ≥ +5% raw 2 of 9 times since 3Q22, and F02 puts the 1Q27 revenue guide median (+9.4%) below the gap-adjusted Street (+11.0%; P(guide ≥ Street) 0.33). The pull-up: Q4 prints have beaten the pre-stated sign rule by +10 points on average (n 4, t 2.4, post-hoc; carried at +3), which is the annual-guide reset and the January "bid into the February guide" seasonal. S03 carried this event at P(≥ +5%) 0.39 with a +2.6% mean; this log lands lower and says why (§4, §6).

**Impact if it happens.** E[day-1 | ≥ +5%] ≈ +10.8%; against the model's unconditional mean (−0.1%) that is +$18/share on a ~$163 pre-print price (+$13 against S03's +2.6% mean). EV 0.30 × $18 ≈ **$5/share: material** — the largest two-way risk after 5 Nov itself. Operating deltas are indirect and small (the up-day is mostly a better-than-feared 1Q27 guide, P(guide ≥ Street | up) 0.52 vs 0.33; E[4Q26 nights | up] 7.9 vs 7.8).

**Files.**
- `research-log.md` — schema log with claims ledger, query log, three estimates, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/r14_model.py` → `r14_base_rates.json` (Q4 counts, S1 residuals by print, Feb event sd from the Jan/Mar expiries), `r14_summary.json`, `r14_sensitivity.csv` (seeded 20260917 mixture, 400,000 draws).
- `sources/web_search_log.md` (1 WebSearch; S03's date query and the options term structure reused).

**Not submitted anywhere.** Next: Astra audit (`docs/pitch-forecasts/audits/A13-research-audit.md`), then a revision-2 response.
