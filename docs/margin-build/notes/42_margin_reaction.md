# 42. Does margin news move ABNB, and what would a FY27 margin reset do to the stock?

Krish with Claude (Opus 5.5), 22 Sep 2026. Script `analysis/src/margin_build/42_margin_reaction/run.py` (`py -3.13`, exit 0), outputs
`data/processed/margin_build/42_margin_reaction/`. Pre-registered in `41_42_prereg.md` (commit f6d01166). The reasons behind each large
move, from the letters and call transcripts, are in `42_event_reasons.md` (a separate research pass). Returns are close-to-close from the
pre-print close, ABNB minus QQQ; the file was re-verified against Yahoo closes (max difference 0.05pp, `42_return_check.csv`). Revisions
are LSEG FY means the day before each print and 5 trading days after, blended to next-twelve-months (NTM) by the days left in the
current fiscal year.

## Bottom line (revised after the Codex check, `audit/CODEX_COST_LEG_CHECK.md`)

1. **Airbnb has beaten EBITDA consensus in dollars on every reported quarter** (22 of 22 since 2021Q1; 1Q23 beat in dollars but
   missed the Street margin by 0.07pt). The large margin-related falls came with cuts to forward estimates at the same print, through
   guidance and commentary; the quarter itself was never the problem.
2. **Forward EBITDA revisions and the stock move together at about 2-2.7x.** Each 1% cut to NTM adjusted-EBITDA consensus came with a
   2.1% (W1, n 14, p 0.010, R² 0.30) to 2.7% (W2, n 10, p 0.008, R² 0.37) relative fall over five sessions; day 1 gives 2.0% / 2.7%.
   **R1 and R3 PASS both windows as registered.** It is an association, not a measured price response: analysts revise after seeing
   the stock, the day-1 slope already explains the five-session slope, dropping 2Q24 makes W2 fail (p 0.13), and adding 2022 kills it
   (slope 0.44, p 0.28). A constant EV/EBITDA multiple would give about 1x.
3. **A separate margin effect cannot be measured.** With the NTM revenue revision in the regression, the margin coefficient is +1.4
   (W1, p 0.33) and +5.1 (W2, p 0.13): **R2 FAILS**, which means insufficient evidence, not proof of no effect. Descriptively, in W1 the
   nine prints where forward margin estimates fell averaged −5.5% relative over five sessions, against +1.7% for the five where they rose.
   Margin cuts with revenue estimates also falling: 1Q23 −18.8, 2Q24 −15.6, 1Q25 +0.5 (mean −11.3%). Margin cuts with revenue estimates
   rising: 4Q23 −0.4, 1Q24 −10.6, 3Q24 −7.7, 2Q25 −6.9, 3Q25 +1.1, 4Q25 +8.9 (mean −2.6%).
4. **One drop is margin-first: 3Q24 (8 Nov 2024).** The letter said Q4 margin would "decline ... due to higher marketing and product
   development expenses" and promised "2025 growth and investment plans early next year". Q4 EBITDA consensus fell 9.6% with Q4 revenue
   unchanged; FY25 EBITDA −2.1% on revenue +0.5%. −8.7% on day 1, −7.7% relative over five sessions. In 2Q24 (Aug 2024, −13.4%) the
   headline was demand, but about 60% of the forward EBITDA cut came through margin. `42_event_reasons.md` has every print.
5. **The scenario.** If management resets FY27 so that consensus margin falls 150bp below the Street's 36.45% with revenue unchanged,
   FY27 EBITDA falls $237M (−4.1%) and NTM EBITDA −3.6%: **−3.7% at a constant multiple, −7.5% to −9.5% on the historical slope**, and
   roughly −0.5% to −14% across the slope's own uncertainty. With revenue also 2% lower: −5.4% constant multiple, −11% to −14% on the
   slope. The full grid runs from −2.5% / −5% (100bp, flat revenue) to −8.4% / −21% (200bp, −4%); rows past the largest observed cut
   (−5.5% NTM, 2Q24) are extrapolations. A February reset gives almost the same numbers (NTM weight on FY27 0.85 in November, 0.88 in
   February). Slope-only moves are relative to a fitted baseline that is itself negative (average print −3.5% W1 / −1.6% W2).

## The regressions (`42_regressions.csv`, HC1 standard errors, one-sided p for a positive coefficient)

| Test | Window | n | Coefficient | p | R² | Verdict |
|---|---|---|---|---|---|---|
| R1: 5-session excess on NTM EBITDA revision % | W1 | 14 | 2.10 | 0.010 | 0.30 | PASS |
| | W2 | 10 | 2.66 | 0.008 | 0.37 | |
| R3: day-1 excess on NTM EBITDA revision % | W1 | 14 | 2.02 | 0.002 | 0.37 | PASS |
| | W2 | 10 | 2.73 | 0.001 | 0.47 | |
| R2: margin revision (pts), with revenue revision % | W1 | 14 | 1.38 | 0.33 | 0.37 | FAIL |
| | W2 | 10 | 5.10 | 0.13 | 0.38 | |
| R2 day-1 variant, margin revision | W1 / W2 | 14 / 10 | 3.97 / 9.96 | 0.14 / 0.027 | | FAIL |
| R1 on 2022Q1+ (descriptive) | | 18 | 0.44 | 0.28 | 0.03 | |

The 2022 prints break R1: estimates rose 6-15% at the 4Q21 and 1Q22 prints while the stock fell 9-14% relative over five sessions (the
2022 de-rating). The slope is a 2023+ relationship.

## Largest forward EBITDA cuts (`42_panel.csv`)

| Print | Day 1 | 5-session excess | NTM EBITDA rev. | NTM revenue rev. | NTM margin rev. |
|---|---|---|---|---|---|
| 2Q24 (7 Aug 2024) | −13.4% | −15.6% | −5.5% | −2.1% | −1.27pt |
| 1Q23 (10 May 2023) | −10.9% | −18.8% | −3.0% | −1.6% | −0.50pt |
| 3Q24 (8 Nov 2024) | −8.7% | −7.7% | −1.7% | +0.4% | −0.77pt |
| 1Q25 (2 May 2025) | +1.0% | +0.5% | −1.1% | −1.0% | −0.05pt |
| 4Q23 (14 Feb 2024) | −1.7% | −0.4% | −0.4% | +0.3% | −0.24pt |

## Scenario table (`42_scenarios.csv`; price $167.51 on 16 Sep, DEC-0015; 21 Sep close $166.84; EV/FY27 EBITDA 15.7x)

| FY27 margin vs Street | FY27 revenue vs Street | FY27 EBITDA change | NTM revision | Implied move vs QQQ (W1-W2 slope) | Constant multiple |
|---|---|---|---|---|---|
| −100bp | 0% | −$158M | −2.4% | −5.0% to −6.3% | −2.5% |
| −100bp | −2% | −$270M | −4.1% | −8.5% to −10.8% | −4.2% |
| −150bp | 0% | −$237M | −3.6% | −7.5% to −9.5% | −3.7% |
| −150bp | −2% | −$348M | −5.2% | −11.0% to −13.9% | −5.4% |
| −200bp | 0% | −$316M | −4.7% | −10.0% to −12.6% | −5.0% |
| −200bp | −4% | −$534M | −8.0% | −16.8% to −21.3% | −8.4% |

Rows at or beyond −5.5% NTM are extrapolations past the largest cut in the sample (2Q24).

## How it would reach the market (read with `42_event_reasons.md`)

The FY margin framework is given in February, with the 4Q letter. The November print carries the 4Q26 revenue guide, a 4Q26 margin
sentence and an update to the FY26 floor, so on 5 Nov a FY27 reset would come through the Q4 guide and qualitative 2027 language, with
analysts cutting FY27 themselves. The team's audited probabilities (`docs/pitch-forecasts/`): 4Q26 revenue guide below the Street 0.72
(C01); FY26 sentence held at "at least 35.5%" 0.33, "approximately 36%" 0.30, lowered or softened 0.27 (C04); FY27 guided down y/y or
framed as an investment year in February 0.49 (B12); a numeric FY27 guide below 35.5% 0.36 and no number 0.48 (F03, strict reading).

Management has never given a next-year margin number in November (`42_event_reasons.md`, five November prints). It signals a
lower-margin year one quarter early in three ways: a named cost line growing faster than revenue in the guided quarter ("Q4 2024 Adjusted
EBITDA Margin is expected to decline ... due to higher marketing and product development expenses", 3Q24 letter); "investment plans"
attached to next year ("We're excited to share more about our 2025 growth and investment plans early next year", same letter); and a CFO
answer that spend "will carry into next year as fixed headcount" (2Q25 call). The Nov 2024 to Feb 2025 sequence shows where the stock
reacts: −8.7% when the November letter flagged the costs and the Street cut FY25, then +14.4% in February when the $200-250M budget and
the 34.5% floor landed on a Street already at 34.46%. **For the pitch, 5 Nov is the event: the tells are a Q4 margin sentence that
names marketing, product development or AI, and any "2027 investment plans" line.** A formal FY27 number would wait for February.

## Limits

n is 14 and 10. Analysts revise after seeing the stock, so the slope mixes news with reaction; a 50% haircut to the slope (an
illustration, not an estimate) halves the scenario moves. The W1-W2 range is not a confidence interval. The margin-only effect cannot be separated
from revenue at this n. Scenario rows are linear extrapolations and ignore what is already priced; the reverse DCF says the price sits on
the Street/team base. Parameter count: two per regression (three for R2).

## RESUME

Done. Next: after 5 Nov, append the 3Q26 print (5-session revision from LSEG or the L0 register) and re-fit R1 on n 15 / 11; if the memo
quotes the stock effect, use the W1-W2 slope range with the constant-multiple row beside it, never a single point.
