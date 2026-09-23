# 43. Thesis 3 (costs): what to write, how it supports the short, how it enters the valuation

Krish with Claude (Opus 5.5), 22-23 Sep 2026, branch `krish/cost-leg`. Synthesis of four parallel workstreams run on 22 Sep:
`43a_sm_evidence.md` (the S&M statistics rebuilt, pre-registered), `43b_valuation_link.md` (how costs enter the target, updated
simulation), `43c_catalyst_path.md` (5 Nov / 11 Feb decision tree, does cutting marketing cost nights, pre-registered),
`43d_red_team.md` (the bull case against thesis 3), on top of `40_line_build.md`, `41_cost_leg.md`, `42_margin_reaction.md`,
`42_event_reasons.md` and `44_short_case_v2.md`. Revised after a Codex Astra check of this text (`audit/CODEX_THESIS3_TEXT_CHECK.md`,
11 findings, all applied; see §7). Every number below traces to those files. Where the draft memo's numbers conflict with these, these
win (the draft's were unaudited).

## 0. In one paragraph

Thesis 3 as drafted rests on two sentences that do not survive: the S&M "elasticity of 1.41" is a regression of one trending series on
another (with a time trend in the equation it is 0.05, se 0.43), and "marketing is paying for this quarter's nights" failed its
pre-registered test (the contemporaneous correlation is 0.04 on 2023+ data; Jessie's 0.66 comes from the 2022 reopening quarters). What
survives is narrower and more defensible: **Airbnb's cost base has behaved like a budget, not a function of revenue.** S&M has grown
faster than revenue for nine straight quarters and rose, then held near 20%, while revenue growth slowed in 2024-25; the Street's FY27 margin needs
total cost growth to fall from ~15% to 10%. Thesis 3 is a **scenario about spending persisting**, not a claim to out-forecast consensus
on costs: without the persistence assumption our FY27 EBITDA would be $5.44bn rather than $5.24bn, against the Street's $5.77bn. Its
job is to turn the nights slowdown of theses 1-2 into an EBITDA miss. **In the valuation it is worth $3.4-5.8 of the $23 per share
between today's price and the target (15-25% depending on the order of the steps, ~20% averaged), and more if costs grow at their
FY24-25 pace.** If nights hold, most of it disappears; management's ability to trim is its main risk.

## 1. Replacement text for the memo

**In the Investment Thesis list (replaces point 3):**
> (3) Airbnb's cost base behaves like a budget, not a function of revenue: sales and marketing has grown faster than revenue for nine
> straight quarters, and the Street's FY27 margin needs total cost growth to fall from 15% to 10%, so if nights slow as in (1) and (2),
> the miss falls through to EBITDA.

**Optional line for Market/Variant View:**
> The Street's FY27 adjusted EBITDA margin of 36.4% needs total cost growth to slow from about 15% in FY26 to 10% in FY27, the slowest
> year since the IPO, and a 43.7% incremental margin against 22.5% in FY25 and 32.7% in FY24. Over FY25-27 that still averages 12.5% a
> year, close to history; the disagreement is whether FY26's spending step repeats.

**Thesis Point 3: Costs (replaces the current paragraph):**
> Sales and marketing has grown faster than revenue in each of the last nine quarters (11 of 14 since 1Q23). Cash S&M grew 21% in FY24,
> 20% in FY25 and 30% in 1H26, against revenue growth of 12%, 10% and 17%, rising from 16.5% of revenue in FY23 to 19.4% in FY25 (23.9%
> in 1H26 against 21.6% a year earlier). When revenue growth slowed from 18% in FY23 to 12% and then 10%, S&M growth rose from 16.5% to 21% and held at 20%. Management
> calls brand spend "effectively a fixed amount of spend for each market", said some 2025 investments "will carry into next year as fixed
> headcount", and attributes the 1H26 increase to "higher paid growth marketing initiatives in emerging markets and partnerships"; the
> ratio of incremental revenue to incremental S&M has fallen from $6.6 in FY23 to $3.4 in FY24, $2.9 in FY25 and $2.7 in 1H26 (against
> 1H25). The Street has been late to the ramp: costs came in above consensus in three of the last four prints after coming in below in
> 16 of the previous 18. Our FY27 case assumes the spending step persists while revenue slows, producing adjusted EBITDA of $5.24bn (34.0%
> margin) against the Street's $5.77bn (36.4%); without that assumption it would be $5.44bn. This is a scenario about spending, not a
> claim to out-forecast consensus on costs, and management's ability to trim is its main risk.

**Valuation (replaces the Monte Carlo sentence; keep the ADR paragraph above it):**
> We value ABNB on EV/FY27 adjusted EBITDA, which the market prices at 15.6x on the Street's numbers at $166.84 (21 Sep). Our FY27 is
> revenue of $15.4bn (2.5% below the Street) and adjusted EBITDA of $5.24bn (34.0% margin against 36.4%). We also let the multiple fall
> with growth: the team's estimate is about half a turn per point of growth (0.49, 95% CI 0.32-0.65, from 35 overlapping monthly changes
> in the trailing multiple), which takes 15.6x to 14.5x for our 2.2-point lower FY27 growth. $5.24bn at 14.5x gives $143.6 ($140-147
> across that interval; the team's DEC-0014 line anchored at 16.5x gives $148). Of the $23 between $167 and $144, $8-10 is revenue below
> the Street, $9.5 is the lower multiple, and $3.4-5.8 (15-25%, depending on the order of the steps) is thesis 3: costs that do not come
> down with revenue and grow 11.1% against the Street's 10.0%. If FY27 costs grow at the FY24-25 average of 12.6% the value is $140; a
> repeat of FY26's 15% gives $135. A scenario simulation that treats margin as the output of cost growth and ties the multiple to growth
> has a median of $145 (5th-95th percentile $126-168) on our revenue view, and $158.5 with revenue centred on the Street.

**Catalysts (cost lines to add):**
> - **Nov 5, 2026 (Q3 print).** The Q4 margin sentence: when the November 2024 letter said Q4 margin would "decline ... due to higher
>   marketing and product development expenses", the Street cut Q4 EBITDA 9.6% and the stock fell 8.7% on a beat (team probability of
>   a Q4 "down y/y" sentence: 22%). The 10-Q segment table's Marketing line ($506M and $600M in 1Q and 2Q26, +32% and +28%): +25% or
>   more in Q3 means the paid step persists into a Q4 we expect to be guided below the Street (72%). Any "2027 investment plans" language.
> - **Feb 2027 (Q4 print, expected ~11 Feb).** The FY27 margin framework: 49% probability that management guides FY27 margin below FY26
>   or calls it an investment year. Each 100bp below the Street's 36.4% is $158M of FY27 EBITDA (2.7%).

**Risks & Mitigants (cost lines to add):**
> - **Risk: management trims Q4 marketing to hold its "at least 35.5%" floor** ($64M at our revenue, $177M in the short case; the 10-K's
>   non-cancelable commitments that include brand marketing were only $66M due within a year at December 2025) and nights do not suffer.
>   The one precedent, 2023's brand phasing, was not followed by a larger nights slowdown than at Booking or Expedia. *Mitigant:* if the
>   trim is temporary it caps FY26 at the floor without changing FY27; our target does not rely on a cut hurting growth; and management
>   has not signalled such a cut in any of the last five Novembers.
> - **Risk: costs fall on their own** (support cost per booking −16% in 2Q26, driven partly by AI; G&A flat) and the Q4 margin sentence
>   reads "up y/y". *Mitigant:* in the team's audited forecasts that sentence mostly follows revenue: "up" is 78% likely if the Q4
>   revenue guide is at or above the Street, while "down" is 30% likely if the guide is below. If nights hold, that is thesis 1's flip
>   rule, not this one; and the support saving applies to roughly a fifth of a $1.3bn line.
> - **Risk: the Q3 margin was sandbagged** (team probability 22%, about +$3.5 a share on the day). *Mitigant:* the quarterly margin
>   sentence has been missed more often than beaten (above it in 4 of 10 quarters), and a step that slips out of Q3 could land in Q4.

## 2. How exactly thesis 3 supports the short

1. **It is an amplifier, not a standalone call.** The revenue case (theses 1-2) puts FY27 revenue 2.5% below the Street. What that does
   to EBITDA depends on whether costs follow revenue down. At Airbnb they have not so far: S&M growth rose from 16.5% to 21% and held at 20% while revenue growth fell
   from 18% to 12% and 10% in FY24-25, and the repo's asymmetry estimate puts S&M's response to revenue slowdowns near zero (k_down −0.12 vs k_up +1.83, n 16,
   directional only). If that holds, the revenue miss falls through: official model revenue −2.5%, EBITDA −9.1% vs the Street.
2. **The Street is modelling the opposite.** Its FY27 needs costs to grow 10.0% after ~15% in FY26 and a 43.7% incremental margin.
   Over FY25-27 the Street's cost growth averages 12.5%, in line with history; the specific disagreement is whether FY26's step repeats.
   Management's words point to persistence (fixed per-market brand spend; launch headcount carried forward; "major announcements next
   year" at Goldman on 8 Sep 2026), but none of that is a FY27 number.
3. **The catalyst is the forward bar, not the reported quarter.** Airbnb has beaten EBITDA consensus in dollars on 22 of 22 reported
   quarters. Its margin-related sell-offs came with forward estimate cuts: each 1% cut to next-twelve-month EBITDA estimates has come with
   a 2.1-2.7% relative fall over five sessions (2023+; an association). The cleanest precedent is Nov 2024: a Q4 margin sentence naming
   marketing and product development, Q4 EBITDA consensus −9.6%, stock −8.7% on a beat.
4. **Its expected value at 5 Nov is small; its value is the tail and February.** Weighted over the team's audited probabilities, the
   cost leg adds about −1% to the 5 Nov relative move: the "Q4 down y/y" branch (22%) is worth −5% to −6%, the "Q4 up y/y" branch (25%)
   +2% to +3% against us. February is where it bites: B12 puts a FY27 down-guide or "investment year" at 49%.
5. **What it does not claim.** Do not print "heads we win, tails we win". The pre-registered 2023 test found no evidence that the
   marketing cut cost nights, so a Q4 trim to hold the floor would most likely neutralise the FY26 part of the cost leg rather than
   confirm the short. One brand-phasing episode cannot tell us what cutting 2026's paid growth spend would do, so the memo should make no
   claim either way.

## 3. How it supports the valuation

The $143 in memo v3 came from the reverse-DCF joint solve at ~7.1% NTM growth, which holds margin fixed and so contains no cost view
(43b §1). The official model reaches almost the same number by a route that contains the cost leg, and the memo should cite that route:

| Step (EV / FY27 adj. EBITDA, spot-anchored, revenue first) | FY27 EBITDA | Multiple | $/share | Change |
|---|---|---|---|---|
| Street FY27 at today's multiple | $5,766M (36.4%) | 15.6x | $166.84 | |
| (a) Revenue 2.5% below the Street, costs flexing at M6's 0.36 | $5,463M | 15.6x | $158.91 | −$7.93 |
| (b) Costs do not flex with revenue (thesis 3) | $5,371M | 15.6x | $156.52 | −$2.39 |
| (c) Costs grow 11.1% (line build) vs the Street's 10.0% (thesis 3) | $5,240M (34.0%) | 15.6x | $153.09 | −$3.43 |
| (d) Multiple at 0.49 turns per point of lower growth | $5,240M | 14.5x | $143.59 | −$9.50 |

The attribution depends on the order. Revenue first (above): thesis 3 = (b) + (c) = $5.82 (25%). Costs first: $166.84 → $163.41 (costs)
→ $153.09 (revenue, no flex) → $143.59, thesis 3 = $3.43 (15%). The order average is $4.62 (20%). Step (c) includes $37M from the line
build's higher FY26 cost base as well as $94M from faster FY27 growth. Sensitivity (revenue first): FY24-25 cost growth (12.6%) gives
$140.1; a repeat of FY26 (15.0%) $134.8. Each point of FY27 cost growth is ~$92M of EBITDA, ~$2.4 a share; each point of revenue growth
is ~$2.6 a share through EBITDA with costs flexing at 0.36 ($3.4 with fixed costs) and ~$4.3 through the multiple, which is why the target
is mostly a growth call and thesis 3 is its multiplier.

Two limits a judge can press: the 0.49 slope was estimated on changes in the **trailing** EV/EBITDA multiple and is applied here to a
forward multiple (an assumption); and the $140-147 range varies only the slope, so it is not a confidence interval on the target.

**The draft's Monte Carlo should be replaced or relabelled.** It is Jessie's simulation on the superseded 7 Sep driver model (growth
centred on +11.3%, about the Street; growth, margin and multiple joined by a generic 0.5 correlation rather than the cost mechanism;
upside measured against a $181.94 spot). Re-scored at today's $166.84 it gives a $176 median and 68% odds of upside, an argument for a
long. The updated scenario simulation (43b: growth from the official model's range, cost growth 8.7-15% with the 0.36 flex, margin as an
output, multiple tied to growth) gives a median of $145 (5th-95th $126-168; $145 with 1.5 turns of multiple noise, $116-177); with
revenue centred on the Street it gives $158.5, and on DEC-0014's literal anchor $149.6. It is the official model with uncertainty, not
new evidence, and it charges every growth shortfall twice (EBITDA and multiple): do not quote its 94% "below spot" as the probability the
short works. The reverse DCF cannot distinguish the cost paths (SBC treatment and WACC swamp them); the target is a multiple-lens number
and the memo should say so.

The short-case price also moves: fixing two construction errors in the 40 short case (`44_short_case_v2.md`) lowers FY27 EBITDA by
$280M to $4,481M (30.8%); the short case is $117 on memo v3's 13.5x (not $125) and $108 on the growth-linked multiple.

## 4. Corrections to the current draft

| Draft text | Problem | Replace with |
|---|---|---|
| "S&M elasticity of 1.41 (95% CI 1.26 to 1.56)" and the 0.53 / 0.49 / 0.86 / 0.87 comparisons | Log-levels regressions of trending series (Durbin-Watson 0.93); with a trend term S&M is 0.05 (se 0.43); the number moves from 0.93 to 1.70 with the window (43a H1, 43d §3) | Growth arithmetic: S&M +21% / +20% / +30% vs revenue +12% / +10% / +17%; FY22-25 CAGR 19.2% vs 13.4%; faster than revenue nine quarters running |
| "every 10% of revenue growth has cost 14% more marketing" | Implies a response coefficient; the growth-on-growth k is 0.41 and insignificant in both windows | "S&M growth rose and held near 20% while revenue growth slowed" |
| "the one cost line that does not scale with revenue" | Product development also outgrew revenue on an FY23 base (14.0% vs 11.1% CAGR) | "the line that has outgrown revenue by the most" |
| "this trend is accelerating" | True of S&M growth (16.5% → 21% → 20% → 30%), not of its ratio to revenue growth (1.96 → 1.75 in 1H26) | "S&M growth has accelerated" with the numbers |
| "So marketing is paying for this quarter's nights, not the next" | Pre-registered test failed: contemporaneous correlation 0.04 on 2023+ data (n 14); no lead at 1-4 quarters | The falling ratio of incremental revenue to incremental S&M ($6.6 → $2.7), described as a ratio, not a return |
| Headline "dropping slower than the market is modeling" | S&M is not dropping anywhere; the Street's S&M is a residual, not a published line | "the Street's FY27 needs total cost growth to fall from 15% to 10%" |
| Monte Carlo "median value of $176 with only a 37% probability of any upside" | Old driver model; measured against a $181.94 spot; at $166.84 it implies 68% upside | The updated simulation (median $145, $158.5 Street-centred) labelled as a scenario, or drop it |
| $143 "at ~7.5% NTM growth" | Joint solve holds margin fixed; no cost view inside | Official model: $5.24bn × 14.5x = $143.6 |
| Short case $125 | Two construction errors (44) | $117 at 13.5x, $108 growth-linked |
| Any "FY27 gap is entirely S&M" | Conditional on our other four cost lines; LSEG's COGS field puts our FY27 excess in cost of revenue (+$101M), not opex (+$30M) | Add "on our own other four cost lines" or drop |
| "Heads we win, tails we win" on a marketing cut | E-2023 test found no evidence the 2023 cut cost nights (43c) | The trim risk and mitigant in §1 |
| Memo v3 "3Q26 is a revenue and EBITDA beat on our own numbers" | The official model now has 3Q26 EBITDA $2,307M, below the Street's $2,362M | Pick one before 2 Oct |

Also never quote: "Airbnb has no cost dial" (kill list; the peer k is 0.14 with CI −0.44 to +0.72); 41's T1 as a passed test; B03 as
0.21 (it is 0.18); the 4Q24 "floor defence" precedent (weakly sourced, Codex C-02); "S&M grows 12-17% a year at zero revenue growth" (a
regression intercept extrapolated below any observed revenue growth; W2's interval runs from −3.5% to +29.7%).

## 5. Judge Q&A

**"Your 1.41 is two trending series regressed on each other."** Agreed, and we took it out: with a trend in the equation it is 0.05. What
we claim instead is simpler: S&M has grown faster than revenue for nine straight quarters, and when revenue growth slowed in 2024-25,
S&M growth rose and then held near 20%. The Street's FY27 assumes that reverses in one year.

**"22 of 22 EBITDA beats and the floor raised twice this year. Why now?"** Not in 3Q26: we do not pitch the quarter's margin. In FY27,
against a bar that needs cost growth to fall from 15% to 10% and a 44% incremental margin, well above the 22.5% and 32.7% of FY25 and
FY24. Costs have already stopped beating consensus (above it in three of the last four prints), and the cushion over the February floor
shrank from 140bp in FY24 to 60bp in FY25.

**"Why does historical S&M growth prove management cannot flex a budget when your revenue misses?"** It does not, and we do not claim it
does. Our FY27 is a scenario in which the step persists; without that assumption FY27 EBITDA is $5.44bn instead of $5.24bn. The case for
persistence is management's own description (fixed brand spend per market, launch headcount carried forward, new launches next year) and
the absence of any cut signal in five Novembers. If they trim, the FY26 floor holds and the cost leg shrinks; the revenue leg does not.

**Bonus, "Booking spends 30% of revenue on marketing":** Booking's is performance spend that has moved with revenue (elasticity 0.9-1.0).
Airbnb's is brand and field operations whose measured response to a slowdown is close to zero, on a multiple paid for a 35% margin that a
"nearly 90% direct or organic" model delivers. Drifting toward Booking's intensity without its flexibility is a de-rating, not a
benchmark.

## 6. Decisions for the team before 2 Oct

1. Base cost path for FY27: line build 11.1% (target $143.6) or FY24-25 history 12.6% ($140.1). The line build is the committed model
   (DEC-0022); history is the stronger thesis-3 claim.
2. Multiple anchor: spot-anchored 15.6x (primary here, because $143 was solved from the price) or DEC-0014's literal line ($148). Every
   row moves $4-5. Either way, say the slope was estimated on the trailing multiple.
3. Attribution convention for "how much is thesis 3": sequential revenue-first (25%), costs-first (15%) or the order average (20%).
4. Whether to print the simulation at all; if yes, the updated one, labelled as a scenario, with the Street-centred median beside it.
5. Put the no-persistence case on the page (FY27 EBITDA $5.44bn) as the upside risk.
6. Ask Jessie to relabel her `05_cost_elasticities` table ("log-levels trend ratios") before `jessie/r-stats` is merged.

## 7. Audit trail

The Codex Astra check of this note (`audit/CODEX_THESIS3_TEXT_CHECK.md`) found: the streak is nine quarters, not ten (F1); "12-17% at
zero revenue growth" is an extrapolated intercept (F2); the incremental ratio is not a marketing return (F3); the evidence-only
comparison mixed consensus bases ($31M vs quarterly sums, $64M vs the annual Street) (F4); the 0.49 slope comes from the trailing
multiple (F5); the attribution is order-dependent (F6); "$1.5 a share through EBITDA" was wrong, $2.6-3.4 (F7); Jessie's simulation does
correlate growth and multiple through its copula, and the updated median is $158.5 with Street-centred growth (F8); one 2023 episode
cannot establish that a 2026 trim is cheap in nights (F9); several risk sentences needed conditional wording (F10); rounding and dates
(F11). All applied above. It also noted that 43c's code labels the least-decelerating peer with `min` and that the stacked-growth
condition was computable (−31pp) though pandemic-confounded; the E-2023 verdict (FAIL) is unchanged.

## RESUME

Text in §1 is ready to paste once the team settles §6. Re-run `43b_valuation_link/run.py` after the spot refresh (DEC-0015) and after the
September Inside Airbnb dumps move the official revenue line. On 5 Nov score, in this order: the Q4 margin sentence, the 10-Q Marketing
line (≥+25% confirms, ≤+15% refutes), cost of revenue against $641M, then 41's live cost call and the 43c kill criteria K1-K4.
