# Handoff message — 11 Sep 2026, for Krish and Jessie

*Under 400 words, paste-ready. Word count of the message body (Subject through signature): 399.*

Subject: ABNB overnight programme — read before Monday

Krish, Jessie —

Overnight: 7 forecast method families, a shared backtest harness, a red-team audit, then today's 4 fixes
(B1-B4). Writeup: `07_MORNING_REPORT.md`. Artifact link in `00_OVERNIGHT_RUNBOOK.md` (private until
shared). Backtest detail: `05_backtests/B1_TAKE_RATE_RECONCILIATION.md`-`B4_FX_EXHIBIT.md`. Pre-reg card:
`PREREG_ABNB-INT-v1.md`. Memo draft: `deck/drafts/memo_v0_2026-09-11.md`.

**The pitch, three sentences:** Once Airbnb has guided a quarter, guide midpoint x (1 + trailing-8
cushion) IS the forecast and nothing beats it (RMSE ratio to naive 0.377 W1 / 0.319 W2) — no level edge
on a guided quarter. Your two-quarter FX lead is rejected as a description of the series (effective lag
~0.5 quarters, p = 0.0005) but vindicated at the guide date, where the lag-loaded spec forecasts best.
The asymmetry is the 3Q26 take rate against 18.10% — reconciled today to 18.14%, P(clear) 0.53, a coin
flip.

**Eleven decisions need a call this weekend** (defaults + reasoning: `PREREG_ABNB-INT-v1.md` §5):
- **D-01** 3Q26 revenue: guide+cushion $4,816M vs kernel $4,804M.
- **D-02** 3Q26 nights baseline: reviews index +9.5% vs team +9.9%.
- **D-03** quote the ADR card despite its own tie/fail, or use naive +4.0%.
- **D-04** which block anchors the card: backtest-winner vs registered vs hybrid (reject hybrid).
- **D-05** FX spec for stated 3Q26: lag-loaded Phi -> +3 vs free fit -> +1 vs WS05 -> +2.
- **D-06** retire the unsourced $4.80bn 3Q26 revenue figure in `SYNTHESIS.md`.
- **D-07** fee step for 4Q26: no-step $3,161M vs half-step $3,179M.
- **D-08** 4Q26 nights baseline: team +8.9% vs ex-NA lap +8.0-8.2% vs Theo's +7.6%.
- **D-09** FY26 guide-raise base rate: 0.67 (n=7) vs 0.75 (n=2).
- **D-10** funds-payable refutation condition: one-sided vs two-sided (recommend two-sided).
- **D-11** chain Theo's 4Q26 ex-NA lap with PR#32's 1Q27 lap, or zero one (chaining double-counts).

**Clocks already running:** Inside Airbnb daily capture at 06:00 local; fee-panel captures 09:00 local
on 14/16/18 Sep; consensus vintage stamps (re-pull 3-4 Nov, again if Zacks updates).

**Two asks only a human can do:**
1. Self-register for LSEG/Refinitiv Workspace (free, UF email) at
   `businesslibrary.uflib.ufl.edu/refinitivworkspace` — unblocks point-in-time consensus history past a
   personal-login wall I can't cross.
2. Decide on the private GraphQL quote route for listing-level pricing. Works technically, but
   impersonates Airbnb's web client against a private API — weigh against Airbnb's ToS yourself, not me.

**Checkpoints:** Mon 14 Sep 09:00 (post first fee-panel capture); Wed 16 Sep 18:00 (post second capture,
a stability read).

— Theo (via Claude)
