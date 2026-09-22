# 42. Does margin news move ABNB, and what would a FY27 margin reset do to the stock?

Krish with Claude (Opus 5.5), 22 Sep 2026. Script `analysis/src/margin_build/42_margin_reaction/run.py` (`py -3.13`, exit 0), outputs
`data/processed/margin_build/42_margin_reaction/`. Pre-registered in `41_42_prereg.md` (commit f6d01166). The reasons behind each large
move, from the letters and call transcripts, are in `42_event_reasons.md` (a separate research pass). Returns are close-to-close from the
pre-print close, ABNB minus QQQ; the file was re-verified against Yahoo closes (max difference 0.05pp, `42_return_check.csv`). Revisions
are LSEG FY means the day before each print and 5 trading days after, blended to next-twelve-months (NTM) by the days left in the
current fiscal year.

## Bottom line

1. **Airbnb has never missed EBITDA consensus on a reported quarter** (22 of 22 beats since 2021Q1). Every margin-driven fall has come
   from the forward view, meaning guidance and commentary that cut next year's estimates, not from the quarter itself.
2. **The stock trades on forward EBITDA revisions at about 2-2.7x.** Each 1% cut to NTM adjusted-EBITDA consensus came with a 2.1%
   (W1, n 14, p 0.010, R² 0.30) to 2.7% (W2, n 10, p 0.008, R² 0.37) fall relative to QQQ over five sessions; day 1 gives 2.0% / 2.7%
   (p 0.002 / 0.001). **R1 and R3 PASS both windows.** At a constant EV/EBITDA multiple the move would be about 0.9% per 1%, so the
   multiple moves with the estimates. The average print, with no revision, was followed by a −3.5% (W1) / −1.6% (W2) relative move.
3. **The market does not price margin news separately from revenue news.** With the NTM revenue revision and the margin revision
   together, the margin coefficient is +1.4 (W1, p 0.33) and +5.1 (W2, p 0.13). **R2 FAILS.** Descriptively the direction is right:
   in W1 the nine prints where forward margin estimates fell averaged −5.5% over five sessions, against +1.7% for the five where they
   rose. Margin cuts with flat or falling revenue estimates averaged −8.2% (1Q23 −18.8, 4Q23 −0.4, 2Q24 −15.6, 3Q24 −7.7, 1Q25 +0.5,
   2Q25 −6.9); margin cuts alongside rising revenue estimates were forgiven (4Q25 +8.9, 3Q25 +1.1; 1Q24 −10.6 is the exception).
4. **The cleanest margin reset on record is 3Q24 (Nov 2024).** Revenue estimates went up (+0.4% NTM) while EBITDA estimates fell 1.7%
   (margin −0.77pt): −8.7% on day 1, −7.7% relative over five sessions. See `42_event_reasons.md` for what management said.
5. **The scenario.** If management resets FY27 so that consensus margin falls 150bp below the Street's 36.45% with revenue unchanged,
   FY27 EBITDA falls $237M (−4.1%), NTM EBITDA −3.6%, and the historical slope implies **−7.5% to −9.5%** relative to QQQ (constant
   multiple −3.7%). With revenue also 2% lower: **−11% to −14%**. The full range, 100bp with flat revenue to 200bp with −4%:
   **−5% to −21%**. A February reset gives almost the same numbers, because the NTM weight on FY27 is ~0.85-0.88 at both prints.

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

## Limits

n is 14 and 10. Analysts revise after seeing the stock, so the slope mixes news with reaction. The margin-only effect cannot be separated
from revenue at this n. Scenario rows are linear extrapolations and ignore what is already priced; the reverse DCF says the price sits on
the Street/team base. Parameter count: two per regression (three for R2).

## RESUME

Done. Next: after 5 Nov, append the 3Q26 print (5-session revision from LSEG or the L0 register) and re-fit R1 on n 15 / 11; if the memo
quotes the stock effect, use the W1-W2 slope range with the constant-multiple row beside it, never a single point.
