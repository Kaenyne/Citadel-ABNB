# Pre-registration for 41_cost_leg and 42_margin_reaction

Written 22 Sep 2026 by Krish with Claude (Opus 5.5), before any test below was run. It is committed before the scripts that run the tests.
What was already seen before writing: the 22 Sep audit decomposition (costs vs Street at the last 16 prints, which prompted T1),
the existing guidance-reaction results (`data/processed/abnb_guidance_reaction_results.csv`: margin guidance features do not
predict day-1 moves) and the FY2025 revision at the 3Q24 print (one row). Nothing else in 42 has been computed.

Windows follow CLAUDE.md: W1 = prints of 1Q23 to 2Q26 (n 14), W2 = 1Q24 to 2Q26 (n 10). A result is quoted only if it passes in both.
All consensus values are LSEG means with the vendor and lookup date in `03_consensus_at_dates.csv` / `03_surprise_history.csv`.

## 41 — the cost leg

Definitions. Street cash costs at print = consensus revenue - consensus adjusted EBITDA (morning of print, `03_surprise_history.csv`).
Actual cash costs = actual revenue - actual adjusted EBITDA. Cost surprise % = (actual - Street) / Street x 100 (+ = costs above consensus).
Ex-variable version: subtract (actual COR / actual revenue) x revenue surprise, so a revenue beat's own variable cost is not counted.
COR surprise = actual cost of revenue - LSEG COGS consensus at print (`printed_q_at_print` rows).

- **T1 regime (flagged data-snooped).** Mean cost surprise % in 3Q25-2Q26 minus the mean over the earlier prints in the window.
  One-sided exact permutation p over all C(n,4) splits. Pass: p <= 0.10 in both W1 and W2, on the raw version. The 3Q25 split was
  chosen after seeing the data, so a pass is descriptive support, not a test; the note must say so.
- **T2 persistence (not looked at).** OLS of cost surprise %[t] on cost surprise %[t-1] within the window. Pass: slope > 0, one-sided
  p <= 0.10 (HC1), both windows.
- **T3 cost of revenue (not looked at).** Mean COR surprise % and count above zero, by window; one-sided sign test that COR comes in
  above the LSEG COGS consensus more often than not. Pass: p <= 0.10 in both windows.
- **Live, scored 5 Nov 2026.** 3Q26 actual cash costs (revenue - adjusted EBITDA) above the Street's $2,382.8M (LSEG 11 Sep:
  $4,744.3M - $2,361.5M). The line build (base) says $2,384.4M; the sign is the call.
- **Descriptive, no pass line:** Street-implied annual cost growth FY26-FY28 against FY22-FY25 actuals and our builds; COR vs the
  LSEG COGS consensus for 3Q26, 4Q26, FY26, FY27; FY27 cost-growth scenarios (Street 10.0%, line build 11.0%, FY24-25 average,
  FY26E, Street plus the recent surprise).

## 42 — does margin news move the stock

Returns: close-to-close from the pre-print close, ABNB minus QQQ, day 1 and 5 sessions (`abnb_earnings_reactions.csv`, re-verified
against Yahoo closes). Revisions: LSEG FY consensus before the print and 5 trading days after (`fy_*_pre_guide` / `fy_*_post_guide_5td`).
NTM blend: weight on the current fiscal year = days left in it at the print date / 365; the rest on the next fiscal year.

- **R1.** 5-session excess return on the NTM adjusted-EBITDA revision %. Pass: slope > 0, one-sided p <= 0.10 (HC1), both windows.
- **R2.** 5-session excess return on the NTM revenue revision % and the NTM implied-margin revision (pts) together. "Margin news is
  priced beyond revenue" passes if the margin coefficient > 0 with one-sided p <= 0.10 in both windows.
- **R3.** R1 on day-1 excess return. Secondary.
- Known limitation: analysts revise after seeing the stock, so the slope mixes news and reaction. Five sessions is short enough that
  most revisions are the guidance itself.
- **Scenario, specified now:** management guides FY27 adjusted EBITDA margin 100 / 150 / 200bp below the Street's 36.45% with FY27
  revenue 0 / -2 / -4% below $15,819M, at the 5 Nov print (NTM weight on FY27 ~0.85) and at the Feb 2027 print (~0.88 FY27, rest FY28
  held at consensus). Mapped with the R1 slope only if R1 passes; always also at a constant EV/EBITDA multiple.
