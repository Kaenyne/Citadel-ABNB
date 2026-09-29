# Thesis 3 (margins): memo text and sources, 24 Sep 2026

Krish with Claude (Opus 5.5). Replaces the team draft's Thesis 3 (S&M elasticity 1.41). Built from the margin work on
`krish/cost-leg` (worktree `../citadel-abnb-marginaudit`, not pushed): notes 43 (thesis-3 integration, Codex-checked), 45 (AI
and the FY27 margin) and 46 (margin bridge Street → ours). Official revenue = pitch model v2 income statement (DEC-0042).

## Memo text (~230 words)

**Thesis 3 – AI Driven Margin Expansion is Overstated and Revenue Declines Compound Compressing Margins:** The Street lifts
FY27 margin to 36.4% from 35.6% by slowing cost growth from about 15% to 10%, the slowest since the IPO, and the bull case says
AI delivers it. The filings say the savings are small and already spent. The 2Q26 10-Q credits AI with $17M of lower support
costs in a quarter when S&M rose $184M and ops and product payroll $89M. Management plans to "reinvest most of these
efficiencies into marketing, product and technology", and its 2026 guide absorbs "a material increase" in AI spend. In our FY27
bridge, hosting and AI compute take 59bp of margin while AI support savings return 20bp; even a generous AI case leaves FY27 at
35.8%. Meanwhile costs behave like a budget. S&M has outgrown revenue for nine straight quarters (16.5% of revenue in FY23, 23.9%
in 1H26); when revenue growth slowed from 18% to 10%, S&M growth rose from 16.5% to 20%, and each extra S&M dollar now buys $2.7
of revenue, down from $6.6. So our 2.5% lower FY27 revenue falls through: even if costs follow the Street's own plan and fall
with revenue at the historical rate, FY27 margin is 35.4% and FY26 35.4%, below the "at least 35.5%" floor. On our costs FY27 is
34.0% ($5.24bn EBITDA vs $5.77bn); holding consensus needs 7.3% cost growth.

## Where each number comes from

| Claim | Number | Source (branch `krish/cost-leg`) |
|---|---|---|
| Street FY27 / FY26 margin | 36.45% (LSEG 11 Sep, n 44; 23 Sep re-pull same within $3M) / 35.6% | `45_ai_margin.md`; memo v3 estimates table |
| Street cost growth | ~15% FY26 → 10.0% FY27; FY21–25 actual 21.2 / 25.0 / 14.0 / 12.7 / 12.5% | `43_thesis3_integration.md` §1 (variant line); `45_breakeven.csv` |
| Filed AI saving | $17M lower third-party support costs, 2Q26 ($15M in 1H26); same quarter S&M +$184M, ops payroll +$27M, PD payroll +$62M | 2Q26 10-Q MD&A via `45_ai_margin.md` §2 |
| Management quotes | "reinvest most of these efficiencies into marketing, product and technology" (Mertz, 12 Feb 2026); guide "does assume a material increase in terms of the AI spend" (6 Aug 2026) | `45_ai_margin.md` §2 (call transcripts; check against the official IR transcript) |
| FY27 bridge | hosting & AI compute −59bp (−$91M); AI support automation +20bp (+$30M) | `data/processed/margin_build/46_margin_bridge/46_bridge.csv`. These are against the Street's total cost plan spread evenly across lines, because no vendor publishes Street cost lines |
| Generous AI case | FY27 35.8% (−62bp), EBITDA −$240M on official revenue | `45_fy27_grid.csv`, case C |
| S&M | faster than revenue 9 straight quarters (11 of 14 since 1Q23); 16.5% of revenue FY23, 19.4% FY25, 23.9% 1H26; growth 16.5% → 21% → 20% → 30% (1H26) while revenue 18% → 12% → 10% → 17% | `43a_sm_evidence.md`; `43_thesis3_integration.md` §1 |
| Incremental revenue per incremental S&M $ | $6.6 (FY23), $3.4, $2.9, $2.7 (1H26) | `43a_h3_by_year.csv`. A ratio, not a return: 90% of traffic is direct or organic |
| Revenue gap | FY27 −2.5% vs Street ($15.42bn vs $15.82bn) | `46_bridge_meta.csv` |
| Street cost plan, flexed | FY27 35.4% (−103bp, −$303M); FY26 35.4% | `45_fy27_grid.csv` case E, k 0.364; `45_ai_margin.md` §5 |
| Our FY27 | $5.24bn, 34.0% vs $5.77bn, 36.45% | `46_bridge_meta.csv`; line build via official IS v2 |
| Break-even | 7.3% FY27 cost growth holds 36.45% on official revenue ($251M below the Street's plan) | `45_breakeven.csv` |

## What changed from the team draft, and why

| Draft | Problem | Replacement |
|---|---|---|
| "S&M elasticity of 1.41 (95% CI 1.26 to 1.56)" and 0.53 / 0.49 / 0.86 / 0.87 | Log-levels regression of two trending series (Durbin-Watson 0.93). With a time trend in the equation S&M is 0.05 (se 0.43), and the estimate moves from 0.93 to 1.70 with the window. A judge who knows econometrics will take it apart. | Growth arithmetic: nine straight quarters faster than revenue; S&M growth up while revenue growth fell |
| "this trend is accelerating" [JY7.1] | True of S&M growth (16.5% → 21% → 20% → 30%), not of its ratio to revenue growth | Stated as S&M growth rising while revenue growth fell |
| "marketing is paying for this quarter's nights, not the next" | Pre-registered test failed: contemporaneous correlation 0.04 on 2023+ (n 14), no lead at 1–4 quarters | Incremental revenue per S&M dollar, $6.6 → $2.7, given as a ratio |

## For Q&A (cut from the text)

- **Cost-surprise record:** costs came in above consensus in 3 of the last 4 prints, after coming in below in 16 of the previous 18.
- **Management on fixed spend:** brand spend is "effectively a fixed amount of spend for each market"; 2025 investments "will carry
  into next year as fixed headcount".
- **Our model already credits AI:** ops, product and G&A fall from 29.2% of revenue (FY25) to 26.2% (FY27).
- **The only case that reaches the Street's margin:** every AI lever plus S&M slowing. It gives 36.7%, but EBITDA is still $108M
  below the Street, and the stock is worth $154 because growth, and so the multiple, is lower.
- **November 2024 precedent:** a Q4 guide of margin "decline … due to higher marketing and product development expenses" cut Q4
  EBITDA consensus 9.6% and the stock 8.7% on a beat.
- **Main risk:** a Q4 marketing trim to hold 35.5% (about $64M). It caps the FY26 miss but not FY27, which needs $251M of cuts beyond
  the Street's plan.
