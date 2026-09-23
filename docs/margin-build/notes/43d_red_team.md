# 43d. Red team of thesis point 3 (the S&M / cost leg): the strongest bull case, what it kills, what survives

Claude (Fable 5.1) as buy-side judge, 22 Sep 2026, branch `krish/cost-leg` (worktree `citadel-abnb-marginaudit`). Read-only over the
repo; nothing in `40_line_build`, `41_cost_leg`, `42_margin_reaction`, the dossiers or the official model was changed and no package
`run.py` was run. Three small replication tables (inline `py -3.13 -X utf8` on `02_panel_quarterly.csv`, commands in §7) are in
`data/processed/margin_build/43d_red_team/`. Sibling notes 43a-43c are other analysts' and were not read or touched.

Thesis 3 as drafted (unaudited): *"High costs associated with S&M that are dropping slower than the market is modeling."* Body: S&M
"elasticity 1.41 (95% CI 1.26-1.56)" to revenue vs 0.53 ops & support, 0.49 G&A, 0.86 cost of revenue, 0.87 product development
(Jessie's `analysis/r_stats/R/04_regressions.R`, log-log levels with quarter dummies, 1Q22-2Q26, n 18); "every 10% of revenue growth
has cost 14% more marketing, and this trend is accelerating. So marketing is paying for this quarter's nights, not the next."

## 1. Verdict

**Two of the twelve objections are fatal to the thesis as worded, none is fatal to the thesis as the repo actually supports it.** The
1.41 must go: it replicates exactly (1.41, HAC se 0.07) but it is the ratio of two trends, not a response coefficient (Durbin-Watson
0.93; with a linear trend in the regression the coefficient is 0.05 with se 0.43; it is 0.93 on 1Q22-4Q23 and 1.70 on 1Q24-2Q26). The
sentence "marketing is paying for this quarter's nights, not the next" is a causal reading of a contemporaneous correlation (r 0.66,
lead correlations 0.16-0.27 inside the 95% band) and must be rewritten. Everything else the bull can throw (22 of 22 EBITDA beats, the
floor never missed and raised twice this year, 1H26 margin +1.1pp, AI support savings, G&A flat, the Street already modelling S&M
deceleration, the 2023 cut precedent, peers at 26-30% marketing intensity, expansion-market payback, the stock forgiving margin-down
guides) is answerable from the repo, but every answer ends in the same conditional: **the cost leg is not a forecasting edge (evidence-only
costs are $31M *below* the Street for FY27; the FY27 excess is a persistence assumption carried from one 3Q26 reconciliation), it is a
description of a cost base that is a budget rather than a function of revenue, and it only bites if thesis 1 (nights decelerate) is
right.** Pitch it as the amplifier on thesis 1, with management's ability to cut named as the main risk, and it survives Q&A.

## 2. The objections, ranked

Severity: **fatal** = the sentence cannot be defended and must be removed; **serious** = defensible only with a specific reframing the
memo does not yet carry; **answerable** = the repo has the rebuttal, quote it. "Survives follow-up" = whether the rebuttal holds when
the judge asks the obvious next question.

| # | Bull objection (with the bull's numbers) | Severity | Best rebuttal (repo numbers) | Sources | Survives follow-up? |
|---|---|---|---|---|---|
| 1 | **The 1.41 "elasticity" is spurious on trending levels.** Both series trend up; log-levels with quarter dummies on n 18 is a trend ratio. DW 0.93. Add a trend: 0.05 (se 0.43). Window-dependent: 0.93 (1Q22-4Q23, n 8), 1.18 (to 4Q24), 1.61 (1Q23+), 1.70 (1Q24+), 1.07 with 2021 in. The growth-on-growth spec gives 0.41 (se 0.13). | **fatal** to the number and to "every 10% of revenue growth has cost 14% more marketing" | Drop the elasticity language and quote the arithmetic: S&M cash grew +21.1% / +20.1% / +29.9% in FY24 / FY25 / 1H26 against revenue +11.9% / +10.3% / +17.1% (ratios 1.77 / 1.96 / 1.75), from 16.5% of revenue (FY23) to 19.4% (FY25) and 23.9% (1H26). The *behavioural* result is worse for the bull than 1.41: y/y S&M growth moves only 0.41-0.42 with y/y revenue growth and carries a +14-17%/yr intercept (M6 `c_sm` 0.155), i.e. the budget grows regardless; and on the way down it does not slow at all (k_up +1.83, k_dn -0.12, p 0.003, n 16). | `43d_elasticity_specs.csv`; M6 §4 (`M6_cycle_flex_k_table.csv`); C4 dossier §3.7 | Yes, once reworded. The judge can still say n 16-18 and the asymmetry is "directional, not a coefficient" (M6's own words); agree and say so. |
| 2 | **22 of 22 EBITDA beats; the FY floor has never been missed; FY26 was raised twice (Feb "stable" → May "at least 35%" → Aug "at least 35.5%").** Why would a company with that record suddenly overrun? | **serious** (fatal to any "they will miss the guide" framing) | The record is of beating the company's *own* quarterly bar and the Street *in the quarter*; the thesis is about the *forward* bar. (i) Cushion over the February floor has shrunk: +140bp (FY24), +60bp (FY25); the line build's FY26 is 35.7% against a floor already at 35.5%, the thinnest ever. (ii) The beats have stopped coming from costs: costs were below consensus 16 of 18 prints to 2Q25 and above in 3 of the 4 since (+$4M, +$41M, +$28M, -$0.4M); 3Q26 P(EBITDA beat) is 0.78 on *revenue*. (iii) The Street's FY27 bar needs cost growth +10.0% after +15.0% in FY26E, the slowest year since the IPO, and a 43.7% incremental margin against 22.5% / 32.7% delivered in FY25 / FY24. (iv) The one margin-first drop (3Q24, -8.7%) came *on a beat*. | 41 §bottom lines 1-2; 05 §guide-language table; 42_event_reasons 3Q24; SYNTHESIS §9 | Yes. Follow-up "so 3Q26 beats too?" — answer yes (0.78) and say the memo does not pitch the beat (memo v3 risk 2). |
| 3 | **1H26 adjusted EBITDA margin was UP 1.1pp y/y (28.3% vs 27.2%) with S&M +30%. Costs are obviously under control.** | **serious** | Bridge the 1.1pp by line: S&M **-2.35pp**, offset by G&A +1.72pp (of which the $38M non-income-tax release is ~0.6pp and one-off), ops & support +1.08pp, product development +0.55pp, cost of revenue +0.25pp. Every line except S&M delivered leverage and S&M consumed more than ops, PD and COR gave together. Management then guided 3Q26 margin *down* y/y ("down slightly", 6 Aug) — the first down-guide of a year in which 1H was up — because 2H carries "some incremental investment" in S&M and a "material increase" in AI spend. | `43d_1h26_margin_bridge.csv`; 2Q26 10-Q MD&A (cached `abnb-20260630.htm`); 05 statements; 40 §reconciliation | Yes. |
| 4 | **AI is cutting customer-support cost per booking (-10% 1Q26, -16% 2Q26) and "nearly half" of tickets are automated; ops & support is a structural tailwind that funds the marketing.** | answerable | The ops & support *line* per booking fell 2.2% (1Q26) and 5.3% (2Q26), not 10-16%: the metric covers the third-party contact cost (~22% of the line; -$17M in 2Q26) while payroll +$27M, make-goods +$10M and host-liability insurance +$7M went the other way. The line build already models -10%/yr on the variable fifth and +8% on the rest (ops 10.1% of revenue FY25 → 8.7% FY27, +1.4pp of margin). The bull's tailwind is in our numbers; it is worth about 0.5-0.7pp a year, against S&M consuming 2.35pp in 1H26. | 40 §ops line; C2 dossier; 05 bottom line 1; 2Q26 10-Q MD&A | Yes. |
| 5 | **G&A is flat (-5.4% 1H26), product-development headcount growth is "lower than 2025", and Mertz calls the company "extremely disciplined".** | answerable | G&A's 1H26 decline is a $38M non-income-tax release against +$32M of payroll in 2Q26 alone (+7% underlying); we model +5%. PD grew +11% in 1H26, all payroll; we model +8% plus $30M AI tooling. Both lines are *in* the 35.7% FY27 line build; neither is where the disagreement with the Street sits. The "extremely disciplined" quote is Mertz on the 3Q24 call about total margin since 2020, not about G&A (C5 dossier corrected the attribution). | C3, C5 dossiers; 40 line table | Yes. |
| 6 | **The Street already models S&M deceleration and a mid-30s margin: FY27 36.45% (LSEG n 44) implies S&M +9.5% ($3,328M, 21.0% of revenue) after +28% in FY26. There is nothing to be short of; your 21.9% is inside consensus noise (sd $154M).** | **serious** | That *is* the disagreement, stated precisely: the Street needs the ramp to fall from +28% to +9.5% in one year, against a management record of **0 forward "slower than revenue" marketing statements in the last 10 prints and 0 of 5 Novembers** (1 of 18 since 1Q22), a stated policy to "reinvest top-line efficiencies... primarily in marketing", brand spend described as "a fixed amount for each market", and "major announcements next year" (Chesky, 8 Sep 2026). Our line build is +13.8% (21.9%); the calibrated run's allocation 23.5%; the gap is 0.8-2.5pp of FY27 margin ($132-393M). Concede the two honest limits: the Street's S&M is a residual on *our* other four lines, not a published line; and F04 puts P(FY27 S&M ≥ 21.9%) at only 0.55 (CI 0.40-0.68), so the cost leg *alone* is worth ~0.8pp, not the thesis. | C4 dossier §2, §7 conflict 3; B03 research log; 05 V023; F04 README | Yes, with the conditional clause ("on our own other four cost lines") kept in. |
| 7 | **Management has cut before and can again.** 2023: S&M growth +28.6% (2Q23) → +3.8% (3Q23), episode dummy -12.7pp (t -3.40). M6's cut engine reaches an FY27 35.0% floor inside historically observed caps in every scenario. They will simply hold the floor. | **serious** (the thesis's largest single risk) | Agree it is possible and price it. (i) The 2023 cut followed a *stated* policy in Feb 2023 ("flat as a percent of revenue"; Stephenson: "total marketing costs roughly the same as the prior year"); no such statement exists now — the standing policy is the opposite. (ii) The cut required to hold FY27 at 35% is $386-508M of programme; to hold FY26 at 35.5% in the short case, $177M off 4Q26 marketing (~35% of the quarter's marketing; $64M / 12.6% in the official case) — a visible decision, and one management signals in advance (B03, P 0.18 for 5 Nov). (iii) A cut is not free for the long: the marketing is what buys the expansion-market nights growth (thesis 1), so a cut confirms the fixed-cost mechanism and removes the growth the multiple pays for. (iv) The 4Q24 "floor defence" precedent is weakly sourced (Codex C-02); do not cite it. | C4 §9 Q2; M6 §5-6; 40 §short case; B03 README; `CODEX_THESIS_AUDIT_2026-09-22_C` C-02 | Partly. The judge will say "then your FY27 margin is a management choice, not a forecast" — the correct answer is yes, and the memo should say so before the judge does. |
| 8 | **Peers spend far more on marketing: BKNG 30.4% of revenue (FY25), EXPE 26.5% (S&M 49.9%). ABNB's 13.0% marketing / 21.1% S&M is under-spending, not excess.** | answerable | Level versus behaviour. BKNG's marketing is performance spend with an elasticity of 0.87-0.98 to revenue (t 9-16) — a variable cost that flexes down with a miss; ABNB's is brand plus field operations with total-opex k 0.14 (95% CI -0.44 to +0.72, imprecise not zero) and S&M k_dn -0.12: it does not flex. ABNB's multiple (16x FY27 EBITDA at the price) is paid for the 35% margin that its low-marketing, "nearly 90% direct or organic" model delivers; drifting toward peer marketing intensity is a de-rating story, not a comfort. The right peer comparison is ABNB 2026 vs ABNB 2023, not ABNB vs BKNG. Never say "Airbnb has no cost dial" (kill list). | `abnb_vs_bkng_annual.csv`; M6 §4 peers (`M6_cycle_flex_peer_k.csv`); SYNTHESIS §9; reverse DCF §1 | Yes. |
| 9 | **S&M is buying share in expansion markets (LatAm nights +16-20%, APAC +15-17%) with a long payback; Mertz: "some fixed cost upfront... over time we are able to scale into the marketing load." It is investment, not cost, and it is working: nights accelerated to +10% in 2Q26.** | **serious** | (i) The nights it buys are cheaper: geographic mix is -1.4 to -1.5pp a year on ADR (thesis 2), and S&M per night has grown +13-23% y/y for six straight quarters while revenue per night grew +1-8% — the spend per night is rising roughly 3x faster than what a night earns. (ii) "Scale into the marketing load" is logged *unverifiable* in the statement ledger; brand-line statements are 68% kept (n 41), multi-year claims 65% (n 46). (iii) Core-market brand spend is "a fixed amount per market" and the leverage it throws off is by policy re-spent on expansion, so company-level S&M leverage is zero by design — which is exactly why the Street's 43.7% incremental margin is inconsistent with management's own description. (iv) Whether the nights are bought or organic is thesis 1's question (bundle + World Cup); thesis 3 only needs the spend to recur. | panel `sm_cash_per_night_usd` vs `revenue_per_night_usd`; 05 reliability table; 05 statements 4Q24 Mertz; memo v3 thesis 2 | Yes, if the memo does not overclaim on payback (we cannot measure it). |
| 10 | **"Marketing pays for this quarter's nights, not the next" is unsupported and contradicts the brand story (brand is a multi-year asset; performance is a "surgical topper").** | **fatal** to the sentence as worded; answerable as a statistic | Jessie's own cross-correlation: S&M y/y vs nights y/y r 0.66 contemporaneous; S&M leading nights by 1-4 quarters r 0.16-0.27, every one inside the 95% band (0.46, n 18); M6: S&M has no lagged response to revenue (lag 1 k -0.06, lag 2 -0.11). But a contemporaneous correlation is equally consistent with the budget being set to the quarter's revenue (Mertz 1Q25: "every month we're looking at the relative efficiencies by channel... adjusting accordingly"). Reword: "there is no measurable lead from S&M growth to later nights growth (n 18); the two move together inside the quarter. Either way, the growth needs the spend to recur." No causal claim. | `analysis/r_stats/tables/09_sm_vs_nights_ccf.csv` (Jessie's branch); M6 §4 lags; 05 statements 2Q24 / 1Q25 Mertz | Yes once reworded. |
| 11 | **The stock does not care about margins when growth is strong: Feb 2025 (+14.4%) priced a $200-250M budget and a lower floor; Feb 2026 (+4.6%) priced a "stable" margin below the Street. Your own R2 fails — no separate margin effect is measurable.** | **serious** for the stock leg | Both forgiven guides came with revenue *acceleration* (FY25 EBITDA consensus +1.7%; FY26 revenue consensus +2.1%). The thesis pairs the cost base with a nights *deceleration* (thesis 1). When forward EBITDA estimates fall, the stock has moved 2.1-2.7x the NTM revision (R1/R3 pass both windows; an association, not a causal slope); the one margin-first drop (3Q24) was -8.7% on a beat with a named cost line in the letter; a 150bp FY27 reset is -3.7% at a constant multiple and -7.5% to -9.5% on the slope (range, not a CI; 50% haircut halves it). Concede R2: margin is not a standalone catalyst; thesis 3 is the amplifier that turns a revenue miss into an EBITDA miss because costs do not flex (0.35-0.6pp of FY27 margin per revenue point). | 42 §bottom lines 2-5; 42_event_reasons counter-examples; `CODEX_COST_LEG_CHECK` F2, F6 | Yes as amplifier; no as standalone. |
| 12 | **Your own line build says 3Q26 costs from the filings give 52.4%, ABOVE management's "down slightly"; the $97M is a plug; the FY27 excess over the Street ($131-165M) is that plug carried forward ($117M hosting + $78M marketing); without it costs are $31M BELOW the Street (Codex audits A, B, C). The cost thesis refutes itself.** | **serious** (this is the internal audit, and a judge who has read it wins) | Concede the audit in full and change the claim. We have no cost-forecasting edge: 41's registered tests are descriptive (T1 post hoc, T2 not independent, T3 fragile on two rounding prints), and the FY27 excess is a persistence assumption. What survives is the *mechanism*: management chose to spend ~$97M more in 3Q26 than the evidence required (marketing "some incremental investment", AI "material increase"), said the 2025 spend "will carry into next year as fixed headcount", and has a "relative floor" policy that re-spends efficiencies. Show the evidence-only case (3Q26 52.4%, FY27 +$195M) as the upside risk on the page, not in a footnote (C4 §8.1 recommendation (c)). The disagreement with the Street is then legible as one row: the ramp pauses (breaker, +9.4%) vs continues (+13.8%) vs the run's allocation (+21.8%). | 40 §bottom line 1; 41 framing paragraph; `CODEX_THESIS_AUDIT_2026-09-22_{A,B,C}`; C4 §8 | Yes, only with the caveat spoken first. |

Two objections considered and not carried: "cost of revenue overruns are merchant fees and amortisation, not AI" (Codex F7) — true, and 41 already says the COR residual cannot be pinned on hosting; keep the hosting line out of thesis 3. "Adjusted EBITDA excludes $1.8bn of SBC" — a valuation point already in the memo's thesis 3 tail, not a cost-leg objection; SBC's log-levels coefficient (1.37) has the same trend problem as S&M's and should not be quoted as an elasticity either.

## 3. What the replication shows about the 1.41 (`43d_elasticity_specs.csv`)

| spec (S&M cash on revenue, 1Q22-2Q26 unless stated) | n | coefficient | HAC se | reading |
|---|---|---|---|---|
| log-levels + quarter dummies (Jessie's spec, replicated) | 18 | **1.41** | 0.07 | DW 0.93; R² 0.95 — two trends |
| same, 1Q22-4Q23 / 1Q22-4Q24 / 1Q23-2Q26 / 1Q24-2Q26 | 8 / 12 / 14 / 10 | 0.93 / 1.18 / 1.61 / 1.70 | 0.17 / 0.10 / 0.13 / 0.06 | the "elasticity" is the ratio of growth rates in whatever window is chosen |
| same, 1Q21-2Q26 | 22 | 1.07 | 0.09 | the reopening year halves it |
| log-levels + quarter dummies + linear trend | 18 | **0.05** | 0.43 | trend 4.5%/quarter (se 1.5%): revenue and the trend are collinear; no elasticity is identified |
| y/y log growth on y/y log revenue growth (M6 form, equal weights) | 18 | **0.41** | 0.13 | intercept +14.0%/yr at zero revenue growth; M6 rw: 0.42, +17%/yr |
| q/q log first differences + quarter dummies | 17 | 0.67 | 0.45 | not distinguishable from 0 or 1 |

The other lines' coefficients also replicate (ops 0.53, G&A 0.58 ex-lodging vs Jessie's 0.49 incl., COR 0.86, PD 0.87, total 0.90) and
are the same kind of object. The honest summary of Jessie's table is "S&M is the only cash line whose share of revenue has risen since
2023"; her own margin-bridge figure says exactly that and should carry the point instead of the elasticity table.

`43d_sm_vs_revenue_growth.csv`: FY22 revenue +40.2% / S&M +29.1% (ratio 0.72); FY23 +18.1% / +16.5% (0.91); FY24 +11.9% / +21.1%
(1.77); FY25 +10.3% / +20.1% (1.96); 1H26 +17.1% / +29.9% (1.75). "This trend is accelerating" is true of the S&M growth rate (16.5 →
21.1 → 20.1 → 29.9) and not of the ratio (1.96 → 1.75 in 1H26, because revenue accelerated); say the first, not the second.

## 4. The version of thesis 3 that survives

*Airbnb's cost base is a budget, not a function of revenue. S&M has grown 1.8-2.0x revenue for two and a half years (+21%, +20%, +30%
against +12%, +10%, +17%), from 16.5% of revenue in FY23 to 23.9% in 1H26; management describes brand spend as a fixed amount per market
with the leverage re-spent on expansion markets and launches, has made no forward "slower than revenue" marketing statement in the last
10 prints, and historically S&M growth does not decelerate when revenue growth falls below trend (k_dn -0.12 vs k_up +1.83, p 0.003,
n 16). The Street's FY27 margin of 36.5% needs total cost growth to fall from +15% (FY26E) to +10%, a 43.7% incremental margin against
the 22.5% and 32.7% delivered in FY25 and FY24, and, on our other four cost lines, an S&M residual of +9.5%. We claim no cost-forecasting
edge: built from the filings alone our costs are within $31M of the Street, and our FY27 excess is the assumption that the 3Q26 step
persists. The claim is narrower and stronger: when nights decelerate (thesis 1) the cost base stays, so each point of FY27 revenue miss
costs 0.35-0.6pp of margin and the FY26 "at least 35.5%" floor breaks on a 0.6-0.9% 2H26 revenue shortfall unless management visibly
cuts the growth budget — a cut it has signalled in 0 of 5 Novembers, and one that would remove the growth the multiple is paying for.*

Caveats that go on the page, not in a footnote: (1) management *can* cut (2023 precedent; the M6 engine reaches 35% inside historical
caps); the required cut is $177M in 4Q26 / $386-508M in FY27 and is the thesis's main risk; (2) the evidence-only case (3Q26 52.4%,
FY27 margin ~36.9%) is the upside risk; (3) the 5 Nov tells are the 10-Q brand-and-performance growth (below ~+20% = the ramp is easing;
above +28% = the floor is being spent to) and any "2027 investment plans" or named cost line in the Q4 margin sentence.

## 5. Judge Q&A prep

**Q1. "Your 1.41 is two trending series regressed on each other. What is the actual elasticity?"**
A: You are right about the levels regression and we have taken the number out; with a trend in the equation it is 0.05 with a standard
error of 0.43. On year-over-year growth the elasticity is 0.4 with a +14-17% a year intercept, and on the way down it is zero
(k_dn -0.12, n 16). So the point is not that marketing scales 1.4x with revenue; it is that marketing grows 15-20% a year whatever
revenue does, which is what a budget looks like and what the Street's +9.5% FY27 S&M assumes away.

**Q2. "They have beaten EBITDA 22 quarters in a row and raised the FY26 floor twice this year. Why is this the year the cost base bites?"**
A: It does not bite in 3Q26 — we expect a beat (0.78) on our own revenue and we do not pitch the print's margin. It bites in FY27
against a Street bar that needs cost growth to halve from +15% to +10% and an incremental margin of 44% that Airbnb has never delivered
outside the 2021-23 reopening. Costs have already stopped beating consensus (above it in 3 of the last 4 prints after 16 of 18 below),
the cushion over the February floor has shrunk from 140bp to 60bp, and FY26 sits 20bp above a floor that was raised, not sandbagged.

**Q3. "If management cuts Q4 marketing to hold 35.5%, or guides FY27 flat in February, aren't you simply wrong?"**
A: On the margin number, yes, and we say so: FY27 margin is a management choice, and the required cut is visible ($177M off 4Q26
marketing in our short case, roughly a third of the quarter's marketing; 0 of 5 November letters has signalled one). On the stock,
a cut is the confirmation, not the refutation: it tells you the growth in expansion markets was bought, it removes the spend that
thesis 1 says is carrying nights, and the last time the letter named a cost line in a Q4 margin sentence (Nov 2024) the stock fell 8.7%
on a beat. The scenario where we are wrong is the one where nights re-accelerate on their own and the spend does not matter — that is
thesis 1's flip rule, not this one.

**Bonus Q. "Booking spends 30% of revenue on marketing and Expedia 26%. How is 21% too much?"**
A: Booking's marketing is performance spend with an elasticity of 0.9-1.0 to revenue: it is a variable cost that falls with a miss.
Airbnb's is brand and field operations whose measured response to a revenue fall is zero, on a company whose multiple is paid for a 35%
margin that a "nearly 90% direct or organic" model delivers. Drifting toward Booking's intensity without Booking's flexibility is a
de-rating, not a benchmark.

## 6. What the team must fix before 2 Oct (fatal items first)

1. **Remove "elasticity 1.41 (95% CI 1.26-1.56)" and "every 10% of revenue growth has cost 14% more marketing".** Replace with the
   growth-rate arithmetic (+21% / +20% / +30% vs +12% / +10% / +17%; 16.5% → 19.4% → 23.9% of revenue) and, if an elasticity is wanted,
   M6's y/y k 0.42 with the +17%/yr intercept and the k_dn -0.12 asymmetry, labelled n 18 / n 16 and directional. Do not quote SBC's 1.37
   as an elasticity for the same reason.
2. **Rewrite "marketing is paying for this quarter's nights, not the next"** as "S&M growth shows no measurable lead to later nights
   growth (cross-correlation 0.16-0.27 at 1-4 quarters, n 18, inside the 95% band); it moves with nights inside the quarter."
3. **Change "this trend is accelerating"** to "S&M growth is accelerating (+16.5% → +21% → +20% → +30%)"; the ratio to revenue growth
   did not rise in 1H26.
4. **Add the conditional clause** wherever the memo says the FY27 gap "is entirely S&M": "on our own other four cost lines, the Street's
   FY27 EBITDA implies S&M of $3,328M (+9.5%)"; the Street's S&M is a residual, not a published line (C4 §7 conflict 3; Codex B-05).
5. **Put the evidence-only case on the page** (3Q26 52.4%; FY27 +$195M of EBITDA) as the upside risk, and say plainly that the cost leg
   is a persistence scenario, not a forecast edge (41 framing paragraph; Codex A-06, B-01, C-05). Never quote 41's T1 as a passed test.
6. **Quote B03 as 0.18, not 0.21**; drop the 4Q24 "floor defence" precedent (Codex C-02); never say "Airbnb has no cost dial" (SYNTHESIS
   §9 kill list; the peer k is 0.14 with CI -0.44 to +0.72).
7. **Reframe the headline.** "Costs dropping slower than the market models" is defensible only as "the market models S&M growth falling
   from +28% to +9.5% in one year; management's words and record say it will not". Consider "(3) A cost base that is a budget, not a
   function of revenue" so the amplifier role is explicit.

## 7. What ran

Read-only. Replications with `py -3.13 -X utf8 -` from the worktree root, reading
`data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (post-IPO rows from 1Q21), statsmodels OLS with HAC (Newey-West,
2 lags) standard errors, quarter dummies as in `analysis/r_stats/R/04_regressions.R` (fetched from `origin/jessie/r-stats`, commit
188c3df1, not merged). Outputs: `data/processed/margin_build/43d_red_team/43d_elasticity_specs.csv` (15 specs),
`43d_sm_vs_revenue_growth.csv` (FY22-FY25 and 1H26), `43d_1h26_margin_bridge.csv` (five lines, pp of revenue). Peer marketing shares
from `data/processed/abnb_vs_bkng_annual.csv` (FY25: BKNG marketing 30.4% of revenue; EXPE marketing 26.5%, selling & marketing 49.9%;
ABNB marketing 13.0%, S&M 21.1%). The 2Q26 10-Q S&M split (brand and performance $1,091M vs $824M, +32%; field operations and policy
$535M vs $430M, +24%; S&M 26% of 1H26 revenue) read from the cached `docs/pitch-forecasts/questions/bonus-insider-selling/sources/tenq/
abnb-20260630.htm`. No web fetches; no scraping; no package `run.py` executed. Parameter count: zero new fitted objects carried
forward — the tables in §3 are diagnostics of an existing number, not a registered forecast.

## 8. What failed or could not be done

- The "long-term payback" of expansion-market S&M (objection 9) cannot be measured with what the repo holds: there is no cohort or
  market-level S&M disclosure, only the two-line 10-Q split. The rebuttal rests on S&M per night vs revenue per night and on management's
  own "fixed per market" description, not on a measured return.
- Whether the contemporaneous S&M-nights correlation is budget-follows-revenue or spend-drives-nights is not identifiable on n 18; the
  note recommends a non-causal sentence rather than a test.
- The Street's FY27 S&M is not observable (no LSEG line-item consensus below COGS); every "the gap is S&M" statement is conditional on
  our other four lines, and the memo must say so.

## RESUME

Done; nothing committed. The next agent should (1) hand §6 items 1-3 to whoever owns the memo text (the two fatal sentences are in
thesis 3's body in `deck/drafts/memo_v3_short_2026-09-17.md` ¶3 and in Jessie's `analysis/r_stats/README.md` headline, which is on an
unmerged branch — ask her to relabel the table "log-levels trend ratios" or to add the y/y and trend specs from
`43d_elasticity_specs.csv` before it is merged); (2) fold the surviving version in §4 and the three Q&A answers in §5 into the Q&A prep
sheet with the 43a-43c notes once those land; (3) on 5 Nov score the two tells named in §4 (10-Q brand-and-performance y/y; a named cost
line or "2027 investment plans" in the letter) before reading the margin number; (4) add a line to `WORKBOARD.md` for 43d when the
cost-leg notes are consolidated — this note did not edit the board, per the brief's no-edits rule.
