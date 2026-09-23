# 43. Thesis 3 (costs): what to write, how it supports the short, how it enters the valuation

Krish with Claude (Opus 5.5), 22-23 Sep 2026, branch `krish/cost-leg`. Synthesis of four parallel workstreams run on 22 Sep:
`43a_sm_evidence.md` (the S&M statistics rebuilt, pre-registered), `43b_valuation_link.md` (how costs enter the target, corrected
Monte Carlo), `43c_catalyst_path.md` (5 Nov / 11 Feb decision tree, does cutting marketing cost nights, pre-registered),
`43d_red_team.md` (the bull case against thesis 3), on top of `40_line_build.md`, `41_cost_leg.md`, `42_margin_reaction.md`,
`42_event_reasons.md` and the Codex audits in `docs/margin-build/audit/`. Every number below traces to those files. Where the draft
memo's numbers conflict with these, these win (the draft's were unaudited).

## 0. In one paragraph

Thesis 3 as drafted rests on two sentences that do not survive: the S&M "elasticity of 1.41" is a regression of one trending series on
another (with a time trend in the equation it is 0.05, se 0.43), and "marketing is paying for this quarter's nights" failed its
pre-registered test (the contemporaneous correlation is 0.04 on 2023+ data; Jessie's 0.66 comes from the 2022 reopening quarters). What
survives is stronger and simpler: **Airbnb's cost base is a budget, not a function of revenue.** S&M has grown faster than revenue for
ten straight quarters, grows 12-17% a year even at zero revenue growth, and has not slowed when revenue slowed; the Street's FY27
margin needs total cost growth to fall from ~15% to 10%, the slowest year since the IPO. Thesis 3 is not a claim to out-forecast
consensus on costs (built from the filings alone, our FY27 costs are within $31M of the Street); it is the amplifier that turns the
nights slowdown of theses 1-2 into an EBITDA miss and a lower multiple. **In the valuation it is worth about $6 of the $23 per share
between today's price and the $143 target (25%), $10-15 on historical or FY26-like cost growth.** It does not work on its own: if nights
hold, the cost leg mostly disappears.

## 1. Replacement text for the memo

**In the Investment Thesis list (replaces point 3):**
> (3) Airbnb's cost base is a budget, not a function of revenue: sales and marketing has grown faster than revenue for ten straight
> quarters, and the Street's FY27 margin needs cost growth to fall from 15% to 10%, so the slowdown in (1) and (2) falls through to
> EBITDA.

**Optional line for Market/Variant View:**
> The Street's FY27 adjusted EBITDA margin of 36.5% needs total cost growth to slow from about 15% in FY26 to 10% in FY27, which would be
> the slowest year since the IPO, and a 44% incremental margin against 23% and 33% delivered in FY25 and FY24.

**Thesis Point 3: Costs (replaces the current paragraph):**
> Sales and marketing has outgrown revenue for three years. Cash S&M grew 21%, 20% and 30% in FY24, FY25 and 1H26 against revenue
> growth of 12%, 10% and 17%, rising from 16.5% of revenue in FY23 to 19.4% in FY25 (23.9% in 1H26 against 21.6% a year earlier), and it
> has grown faster than revenue in each of the last ten quarters. It behaves like a budget, not a variable cost: in growth terms S&M
> rises 12-17% a year even at zero revenue growth, and when revenue growth slowed in 2024-25 S&M growth did not. Management calls brand
> spend "effectively a fixed amount of spend for each market", said the 2025 launch spend "will carry into next year as fixed
> headcount", and describes the 1H26 step as "paid growth marketing initiatives in emerging markets and partnerships"; each incremental
> S&M dollar has bought less revenue every year ($6.6 in FY23, $3.4 in FY24, $2.9 in FY25, $2.7 in 1H26). The Street has been late to
> the ramp: costs came in above consensus in three of the last four prints after coming in below in 16 of the previous 18. We do not
> claim to out-forecast consensus on costs; built from filings alone, our FY27 costs are within $31M of the Street. The claim is that
> the cost base will not come down when nights slow, so the revenue shortfall in (1) and (2) falls through to EBITDA: our FY27 adjusted
> EBITDA is $5.24bn (34.0% margin) against the Street's $5.77bn (36.5%).

**Valuation (replaces the Monte Carlo sentence; keep the ADR paragraph above it):**
> We value ABNB on EV/FY27 adjusted EBITDA, which the market prices at 15.6x on the Street's numbers today. Our FY27 is revenue of
> $15.4bn (2.5% below the Street) and adjusted EBITDA of $5.24bn (34.0% margin against 36.5%). Lower growth also compresses the
> multiple: it has moved about half a turn per point of growth (0.49, 95% CI 0.32-0.65, 35 overlapping monthly changes), which takes
> 15.6x to 14.5x for our 2.2-point lower FY27 growth. $5.24bn at 14.5x gives $143.6 ($140-147 across that interval). Of the $23 between
> $167 and $143, $8 is revenue below the Street with costs flexing at their measured elasticity, $9.5 is the lower multiple, and $6, a
> quarter, is thesis 3: $2.4 because costs do not come down when revenue slows and $3.4 because our costs grow 11.1% against the Street's
> 10.0%. If FY27 costs grow at the FY24-25 average of 12.6% the target is $140; a repeat of FY26's 15% gives $135. A 20,000-draw
> simulation in which margin is the output of cost growth and the multiple moves with growth gives a median of $145 (5th-95th
> percentile $126-168), conditional on our revenue view.

**Catalysts (cost lines to add):**
> - **Nov 5, 2026 (Q3 print).** The Q4 margin sentence: when the November 2024 letter said Q4 margin would "decline ... due to higher
>   marketing and product development expenses", the Street cut Q4 EBITDA 9.6% and the stock fell 8.7% on a beat (our probability of a
>   Q4 "down y/y" sentence: 22%). The 10-Q segment table's Marketing line ($506M and $600M in 1Q and 2Q26, +32% and +28%): +25% or more in Q3 means the paid step
>   persists into a Q4 we expect to be guided below the Street (72%). Any "2027 investment plans" language.
> - **Feb 11, 2027 (Q4 print).** The FY27 margin framework: 49% probability that management guides FY27 margin below FY26 or calls it
>   an investment year. Each 100bp below the Street's 36.5% is $158M of FY27 EBITDA (2.7%).

**Risks & Mitigants (cost lines to add):**
> - **Risk: management trims Q4 marketing to hold its "at least 35.5%" floor** (a $64-177M cut; the 10-K's non-cancelable commitments
>   that include brand marketing total only $66M within a year) and nights do not suffer (the 2023 cut did not slow nights more than at Booking or Expedia). *Mitigant:* a trim caps
>   FY26 at the floor but leaves FY27 unchanged, our target does not rely on a cut hurting growth, and management has signalled such a
>   cut in none of the last five Novembers.
> - **Risk: costs fall on their own** (AI cut support cost per booking 16% in 2Q26; G&A flat) and the Q4 margin sentence reads "up
>   y/y". *Mitigant:* that sentence mostly follows revenue: in the team's audited forecasts an "up" sentence is 78% likely if the Q4
>   revenue guide is at or above the Street, while a "down" sentence is 30% likely if the guide is below. If nights hold, that is thesis 1's flip rule, not this one; the support
>   saving applies to about a fifth of a $1.3bn line.
> - **Risk: the Q3 margin was sandbagged** (22%, about +$3.5 a share on the day). *Mitigant:* the quarterly sentence has been missed
>   more often than beaten (above it in 4 of 10 quarters), and a step that slips out of Q3 lands in Q4.

## 2. How exactly thesis 3 supports the short

1. **It is an amplifier, not a standalone call.** The short's revenue case (theses 1-2) puts FY27 revenue 2.5% below the Street. What
   that does to EBITDA depends on whether costs follow revenue down. At Airbnb they have not: S&M growth carries a +12-17% a year
   intercept and its measured response to a revenue slowdown is zero (k_down −0.12 vs k_up +1.83, n 16, directional). So the revenue
   miss falls through to EBITDA, and EBITDA misses by more than revenue (official model: revenue −2.5%, EBITDA −9.1% vs the Street).
2. **The Street is modelling the opposite.** Its FY27 needs costs to grow 10.0% after ~15% in FY26 and an incremental margin of 43.7%.
   That is the specific assumption thesis 3 disputes; it is not a claim that management will overspend its own guidance.
3. **The catalyst is the forward bar, not the reported quarter.** Airbnb has beaten EBITDA consensus in dollars on 22 of 22 reported
   quarters. Its margin-driven sell-offs came from forward estimate cuts: every 1% cut to next-twelve-month EBITDA estimates has come
   with a 2.1-2.7% relative fall over five sessions (2023+; an association). The cleanest precedent is Nov 2024: a Q4 margin sentence
   naming marketing and product development, Q4 EBITDA consensus −9.6%, stock −8.7% on a beat.
4. **Its expected value at 5 Nov is small; its value is the tail and February.** Weighted over the team's audited probabilities for the
   Q4 and FY26 margin sentences, the cost leg adds about −1% to the 5 Nov relative move (the "Q4 down y/y" branch, 22%, is worth −5% to
   −6%; the "Q4 up y/y" branch, 25%, is worth +2% to +3% against us). February is where it bites: B12 puts a FY27 down-guide or
   "investment year" at 49%.
5. **What it does not claim.** Do not print "heads we win, tails we win". A Q4 marketing trim to hold the floor is most likely cheap
   in nights (2023 precedent; "nearly 90% of our traffic is direct or organic"), so it neutralises the FY26 part of the cost leg rather
   than confirming the short. The FY27 part survives a trim because the trim is a one-quarter decision.

## 3. How it supports the valuation

The $143 in memo v3 came from the reverse-DCF joint solve at ~7.1% NTM growth, which holds margin fixed and so contains no cost view
(43b §1). The official model reaches the same number by a route that does contain the cost leg, and the memo should cite that route:

| Step (EV / FY27 adj. EBITDA, spot-anchored) | FY27 EBITDA | Multiple | $/share | Change |
|---|---|---|---|---|
| Street FY27 at today's multiple | $5,766M (36.5%) | 15.6x | $166.84 | |
| (a) Revenue 2.5% below the Street, costs flexing at the measured 0.36 | $5,463M | 15.6x | $158.91 | −$7.93 (34%) |
| (b) Costs do not flex with revenue (thesis 3) | $5,371M | 15.6x | $156.52 | −$2.39 (10%) |
| (c) Costs grow 11.1% (line build) vs the Street's 10.0% (thesis 3) | $5,240M (34.0%) | 15.6x | $153.09 | −$3.43 (15%) |
| (d) Multiple at 0.49 turns per point of lower growth | $5,240M | 14.5x | $143.59 | −$9.50 (41%) |

Thesis 3 = (b) + (c) = **$5.8 of $23.3 (25%)**. Sensitivity: on FY24-25 cost growth (12.6%) the target is $140.1 and thesis 3 is 36%;
on a repeat of FY26 (15.0%) $134.8 and 48%; with the Street's cost growth (thesis 3 reduced to non-flex only) $145.9 and 16%. Each point
of FY27 cost growth is ~$92M of EBITDA, ~$2.4 a share; each point of revenue growth is ~$1.5 through EBITDA and ~$4.3 through the multiple,
which is why the target is mostly a growth call and thesis 3 is its multiplier.

**The Monte Carlo in the draft should be replaced.** It is Jessie's simulation on the superseded 7 Sep driver model (growth centred on
+11.3%, about the Street; multiple independent of growth; spot $181.94). Re-scored at today's $166.84 it gives a $176 median and a 68%
chance of upside, an argument for a long. The corrected version (43b: growth from the official model's range, cost growth 8.7-15% with
the measured 0.36 flex, margin as an output, multiple tied to growth) gives a median of $145, 5th-95th $126-168, P(below spot) 0.94,
P(below $143) 0.44. Two honest limits: it is the official model with uncertainty, not new evidence, and it charges every growth
shortfall twice (EBITDA and multiple), so do not quote 0.94 as the probability the short works. The reverse DCF cannot distinguish the
cost paths (SBC treatment and WACC swamp them); the target is a multiple-lens number and the memo should say so.

## 4. Corrections to the current draft

| Draft text | Problem | Replace with |
|---|---|---|
| "S&M elasticity of 1.41 (95% CI 1.26 to 1.56)" and the 0.53 / 0.49 / 0.86 / 0.87 comparisons | Log-levels regressions of trending series (Durbin-Watson 0.93); with a trend term S&M is 0.05 (se 0.43); the number moves from 0.93 to 1.70 with the window (43a H1, 43d §3) | Growth arithmetic: S&M +21% / +20% / +30% vs revenue +12% / +10% / +17%; FY22-25 CAGR 19.2% vs 13.4%; faster than revenue ten quarters running |
| "every 10% of revenue growth has cost 14% more marketing" | Implies a response coefficient; the growth-on-growth k is 0.41 and insignificant in both windows; the growth is an intercept | "S&M grows 12-17% a year even at zero revenue growth" |
| "the one cost line that does not scale with revenue" | Product development also outgrew revenue on an FY23 base (14.0% vs 11.1% CAGR) | "the line that has outgrown revenue by the most" |
| "this trend is accelerating" | True of S&M growth (16.5% → 21% → 20% → 30%), not of its ratio to revenue growth (1.96 → 1.75 in 1H26) | "S&M growth has accelerated" with the numbers |
| "So marketing is paying for this quarter's nights, not the next" | Pre-registered test failed: contemporaneous correlation 0.04 on 2023+ data (n 14); no lead at 1-4 quarters | Falling efficiency: incremental revenue per incremental S&M dollar $6.6 → $3.4 → $2.9 → $2.7 |
| Headline "dropping slower than the market is modeling" | S&M is not dropping anywhere; the Street's S&M is a residual, not a published line | "the Street's FY27 needs cost growth to fall from 15% to 10%" |
| Monte Carlo "median value of $176 with only a 37% probability of any upside" | Old driver model; measured against a $181.94 spot; at $166.84 it implies 68% upside | The corrected simulation (median $145) or drop it |
| $143 "at ~7.5% NTM growth" | Joint solve holds margin fixed; no cost view inside | Official model: $5.24bn × 14.5x = $143.6 |
| Any "FY27 gap is entirely S&M" | Conditional on our other four cost lines; LSEG's COGS field puts our FY27 excess in cost of revenue (+$101M), not opex (+$30M) | Add "on our own other four cost lines" or drop |
| "Heads we win, tails we win" on a marketing cut | E-2023 test failed (43c) | Risk and mitigant above |
| Memo v3 "3Q26 is a revenue and EBITDA beat on our own numbers" | The official model now has 3Q26 EBITDA $2,307M, below the Street's $2,362M | Pick one before 2 Oct |

Also never quote: "Airbnb has no cost dial" (kill list; the peer k is 0.14 with CI −0.44 to +0.72); 41's T1 as a passed test; B03 as
0.21 (it is 0.18); the 4Q24 "floor defence" precedent (weakly sourced, Codex C-02).

## 5. Judge Q&A

**"Your 1.41 is two trending series regressed on each other."** Agreed, and we took it out: with a trend in the equation it is 0.05. On
year-over-year growth the elasticity is about 0.4 with a 12-17% a year intercept, and on the way down it is zero. The point is not that
marketing scales 1.4x with revenue; it is that marketing grows 15-20% a year whatever revenue does, which is what the Street's FY27
assumes away.

**"22 of 22 EBITDA beats and the floor raised twice this year. Why now?"** Not in 3Q26: we expect a beat and do not pitch the quarter's
margin. In FY27, against a bar that needs cost growth to fall from 15% to 10% and a 44% incremental margin Airbnb has not delivered since
the reopening. Costs have already stopped beating consensus (above it in three of the last four prints) and the cushion over the
February floor has shrunk from 140bp (FY24) to 60bp (FY25).

**"If they cut Q4 marketing to hold 35.5%, aren't you wrong?"** On the FY26 margin, yes, and we say so: the required cut is $64-177M, and
history says it would not cost many nights. It does not change FY27, where the spend is headcount, launches and hosting commitments,
and it does not rescue the revenue miss. We are wrong on thesis 3 if nights hold and costs grow 10% or less in FY27; then the stock is
worth $167-172 on these numbers.

**Bonus, "Booking spends 30% of revenue on marketing":** Booking's is performance spend that flexes with revenue (elasticity 0.9-1.0);
Airbnb's is brand and field operations whose measured response to a slowdown is zero, on a multiple paid for a 35% margin that a
"nearly 90% direct or organic" model delivers. Drifting toward Booking's intensity without its flexibility is a de-rating, not a
benchmark.

## 6. Decisions for the team before 2 Oct

1. Base cost path for FY27: line build 11.1% (target $143.6) or FY24-25 history 12.6% ($140.1). The line build is the committed model
   (DEC-0022); history is the stronger thesis-3 claim.
2. Multiple anchor: spot-anchored 15.6x (primary here, because $143 was solved from the price) or DEC-0014's literal line (gives
   $148). Every row moves $4-5.
3. Whether to print the simulation at all; if yes, the corrected one only.
4. Put the evidence-only case (3Q26 margin 52.4%; FY27 +$195M EBITDA) on the page as the upside risk (red team item 12).
5. Ask Jessie to relabel her `05_cost_elasticities` table ("log-levels trend ratios") before `jessie/r-stats` is merged.

## RESUME

Text in §1 is ready to paste once the team settles §6. Re-run `43b_valuation_link/run.py` after the spot refresh (DEC-0015) and after the
September Inside Airbnb dumps move the official revenue line. On 5 Nov score, in this order: the Q4 margin sentence, the 10-Q marketing
line (≥+25% confirms, ≤+15% refutes), cost of revenue against $641M, then 41's live cost call and the 43c kill criteria K1-K4.
