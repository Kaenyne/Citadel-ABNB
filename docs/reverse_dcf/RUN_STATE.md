# Reverse-DCF overnight run: state

Started 12 Sep 2026 (late evening) after the management-implied model (PR #49). Krish asleep; instructions: be thorough, try several approaches, build multiple models and compare, have subagents audit each idea and the final result.

## Plan

1. Four parallel workstreams (Fable subagents, four at a time): A joint solve, B options, C reaction function, D sell-side dispersion. Brief: `docs/reverse_dcf/BRIEF.md`.
2. One auditor per workstream (independent agents; they read the note + outputs, re-run the scripts, check the maths and the claims, write `research/notes/reverse_dcf/audit_X.md` and a findings CSV under `data/processed/reverse_dcf/audit/`).
3. Repairs: send each audit back to its author agent (or a fresh one) to fix what the audit found.
4. Synthesis: `model/ABNB_market_implied.xlsx` (formula-driven, COM-recalculated, reconciled), `research/notes/2026-09-13_market-implied-model.md`, `docs/reverse_dcf/SYNTHESIS.md`, comparison of management-implied vs market-implied vs team.
5. Audit of the synthesis; repairs; commit; push; update PR #49 (or open PR #50 for the market half).

## Status

| Step | State | Notes |
|---|---|---|
| A joint solve | DONE | joint solve at $170.19: FY27 rev +11.5%, EBITDA $5.75bn, nights +8.9%, 16.0x (= team base / Street, $5 below Delivered); case prices Literal $162 / Street $166 / Team $168 / Delivered $175 / Ambition $203; $150 = nights <5%, $220 = nights 18%; slope +0.40 weakly identified (t 3.1 levels, ~0 in changes and 2024-26); fixed-multiple hold gives absurd tails; reverse DCF reproduces 4.61% / 15.95%
| B options | DONE | 5 Nov event sd 9.5% (7.6% expected abs move), 20 Nov straddle 13.5% (70d upper bound); RR -3.5 vol pts, downside ~18% richer than symmetric; 12m RN p25/p50/p75 $124/$167/$217; P(>$179.5) 0.43; base rate 23 prints rms 8.5%, nights accel 6 up/2 down, decel 1 up/10 down; brief formula for event variance was wrong (agent corrected)
| C reaction function | DONE | printed nights-accel SIGN rule survives (post-2022 +6.0 vs -5.6%, 0/8 decel positive, t 2.7, LOO R2 +0.28); no slope; guide direction vs printed rate: nothing; guide vs Street revenue +1.9%/1% (one sample only); breakeven = accelerating 3Q26 (>~10.6%) with 4Q26 guide ~1% below Street; team base case implies -4 to -8.5% day-1; Street nights bar 148.9m already assumes acceleration
| D sell-side | DONE | tape = multiple call on mgmt delivered (mean target 17.1x); Zacks FY27 range -> nights +2.9 to +11.8%; 3 upward moves 8-10 Sep (Baird, Raymond James, Truist); Goldman feed label wrong (Neutral, not Sell)
| audits A-D | DONE, all four PASS WITH FIXES, no blockers | A: drop direct FY27 mapping, delta-method band, quote FY27 10.4-11.5% at price, units caveat. B: return series was QQQ-excess (raw decel split 3/8 not 1/10), lognormal quartiles $126/$164/$214 headline, drop a Bloomberg-reconstructible column. C: sign rule is a re-test not multiplicity-robust, S1 headline, team-base -4 to -8.5% is conditional on deceleration (unconditional -2 to -2.5%), gap/intraday split. D: "chase up not down" wrong (symmetric), Bernstein 25.5x is P/E, feed coverage gaps, relabel decomposition JUDGEMENT |
| repairs A-D | DONE (all four authors applied their audits; synthesis rebuilt on the repaired CSVs) | |
| synthesis | DONE: workbook + research/notes/2026-09-13_market-implied-model.md + docs/reverse_dcf/SYNTHESIS.md | at $170.19: FY27 growth 9.5-11.5% (direct / proportional), nights 7-9%, EBITDA $5.6-5.7bn, 16x; mean target = Delivered; options 12M p25/p50/p75 $124/$167/$217; team base case implies -6 to -9% on 5 Nov
| synthesis audit | DONE: pass with fixes, no blockers; 6 material fixes applied (event-sd input parsing, lognormal P(above), retired guide numbers, drifted figures) | |
| commit / PR | DONE: 2a07337 (workstreams + audits + repairs), ed7d6dd (synthesis-audit fixes); pushed; PR #49 retitled and described for both halves | |
