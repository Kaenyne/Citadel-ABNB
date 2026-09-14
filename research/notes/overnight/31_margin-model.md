# 31. The margin model: cost lines derived from the revenue drivers, tested against history and against what management says

Krish with Claude Code, 8 Sep 2026. Two parts, read them in this order: **31a** `31a_mgmt-margin-statements.md` (194 verified management statements on margin structure, all 23 prints, and the operating profile they imply by cost line) and **31b** `31b_operating-profile.md` (how each cash cost line has actually scaled with nights, GBV, ADR and mix since 2021; the annual decomposition of every margin move since 2019; a forward model FY26-FY28 under three cost profiles). Scripts `analysis/src/overnight/31a_mgmt_margin_statements.py`, `31b_operating_profile.py` (`py -3.13`; 31b reads the 29 bridge and reconciles to the 30 walk). Both need the gitignored raw inputs in the main tree (`data/raw/letters`, `data/raw/transcripts`, `data/raw/xbrl`).

## Bottom line

1. **Only one cost line is a volume function. The other five are decisions.** Cost of revenue scales one-for-one with GBV dollars (elasticity +1.01, t 3.3, stable leave-one-year-out) and is the only line where a driver-based forecast is an estimate rather than a judgement. Operations and support falls per night at about 2.5% a year as a *trend*, not as scale leverage (elasticity unstable, 0.4 to 1.7). Product development, brand marketing, field operations and G&A have no stable relationship to revenue or nights on 14 quarters; they are what management chooses to spend. So "margin derived from revenue" is honest for roughly 17% of revenue (cost of revenue) and for the leverage every other line gets from revenue per night; the rest of the forward margin is a spending policy, and 31a shows management describes it that way ("find incremental efficiencies every year... invest some of that", the "relative floor").

2. **What built the margin: three parts ADR windfall to one part cost reset.** FY2019 to FY2022, +39.8 points: revenue per night +30.0 (ADR +26.2, take rate +3.8) against a cost side worth only +9.8, of which brand marketing +5.9 and field ops +3.4. Operations and support contributed nothing. Since then, FY2022 to FY2025, +0.5 points net: revenue per night +5.1 (size mix and like-for-like price +5.4, **regional mix −2.5**, FX +1.1, length of stay +0.5, take rate +0.7), scale leverage +3.5, ADR passing into cost of revenue −1.2, and per-unit spending decisions −7.2 (marketing −4.2, G&A −2.2, product development −1.5). 1H26 repeats the shape: revenue per night +4.9 (FX +2.4), support +0.4, G&A +1.0, brand marketing −3.2.

3. **AI has moved exactly one line so far.** Support cost per night −3.8% (1H26 vs 1H25), worth about +0.4 margin points a year, consistent with management's −10% and −16% per booking. Cost of revenue per $100 GBV −1.6%. Product development per night **+2.1%** with no filed evidence of the engineering-productivity claim (the "+30% output" language has run since 1Q23 while the line deleveraged every year). Chesky's "AI will not affect the P&L" (4Q25) was reversed by Mertz ("a material increase in AI spend", 2Q26) and never sized, while contracted hosting obligations went $719m to $1,749m.

4. **Three forward profiles, base revenue path (workstream 29):**

| Adj. EBITDA margin | FY2025A | FY2026E | FY2027E | FY2028E |
|---|---|---|---|---|
| Historical: elasticities and per-unit trends only, no overlays | 35.1 | 35.8 | 35.4 | **34.6** |
| Management: what the statements imply | 35.1 | 35.8 | 36.5 | **37.4** |
| Base: our judgement | 35.1 | 35.3 | 35.9 | **36.9** |
| Workstream 07 lever model (base) | 35.1 | 36.1 | 36.6 | 37.5 |
| Workstream 30 quarterly walk (base) | 35.1 | 36.2 | 36.4 | |

   Pure history loses about half a point a year because the discretionary lines keep growing at their 2023-26 trends (brand +16.5%, field +24%, product +11%) against a revenue path decelerating to 11-12%. **The 2.8-point gap between history and management is field operations (+$322m) and G&A (+$200m) by FY28, not brand marketing.** Bear and bull revenue scenarios move each profile by −5 to +5 points at FY28 (`31b_forward_margin_by_profile.csv`).

5. **Management's profile past FY2026 is mostly silence.** Of 30 cost-line-years in 31a, 12 are `mgmt_silent`; the only quantified statement beyond FY2026 on any line is the tax rate. So the "management" profile above is FY26 as guided, then the reinvestment algorithm. Total-margin statements are 91% kept (n 43) and the floors were beaten by 140bp and 60bp; take-rate guides are 59% kept (FY25 +20bp guided, −16bp printed); the FY24 marketing "largely the same" guide missed by 157bp. Reliability by line is the thing to carry into any forecast: trust the total, discount the take rate and the marketing sentence, expect nothing on FY27 until February.

6. **Sensitivities (FY2028E, base profile, margin points):** support −10% per night +0.84; brand marketing growth +5pt −0.66; take rate +10bp +0.47; ADR ex-FX +1pt +0.42 (FX the same); nights +1pt +0.34; one point of nights share moving from NA to LatAm/APAC −0.33. Estimation risk rivals business risk: the support elasticity at its leave-one-out bounds moves FY28 by +1.1 / −1.5 points.

## Conflicts this workstream opens, and where they stand

- **FY2026: 31b base 35.3% (below the 35.5% floor) against 30 at 36.2% and 07 at 36.1%.** 31b lets the discretionary lines run at their per-unit trends through 2H26; 30 phases H2 brand marketing down to +10% in Q4. Management has never missed a floor. Treat 35.3% as the "no deceleration in spend" case and 36.2% as the "H2 deceleration" case; the 10-Q S&M split on 5 November decides it.
- **Regional mix is a real margin drag that two earlier notes folded into "ADR ex-FX".** The margin-drivers bridge's +3.7 of ADR ex-FX (FY22-25) is +5.4 of size mix and pricing net of −2.5 of regional mix. Worth 0.5-0.7 points a year and negative every year; it belongs as its own line in any bridge.
- **"Product development flat at 10-11% of revenue in cash" is an ADR artefact.** Per night it is $2.42 to $2.51 to $2.46. **"Operations and support is the quiet source of leverage"** is a trend, not leverage.
- The "fixed brand spend per market" framing is unidentifiable: no expansion-market count has ever been disclosed. It is in the overlay table as a parameter with no source.
- Small corrections listed in both notes: the floor-beat range is 60-140bp not 60-180bp; FY2023 was never a floor guide; FY2024 margin is 36.40% not 35.8%; the letter-sourced guidance ledger misses the two most consequential FY guides (FY24 marketing, FY25 take rate) because they were spoken on calls.

## How to use it

- **For forecasting**, use `31b_overlay_parameters.csv` as the single place assumptions live: each overlay (AI support per-night decline, headcount productivity, marketing per market, hosting step, new-business incentives, take rate, FX flow-through) has a historical value, a management value with the 31a statement IDs and confidence, and a base value. Change a parameter, re-run 31b, and the quarterly and annual margins, the FY25-FY28 bridges and the sensitivities regenerate.
- **For the management-language forecast**, 31a's table (e) has every FY margin sentence verbatim; the pattern is floor in February, verbatim in May and August, point in November, and the floor has never been missed.
- **For the pitch**, the defensible statements are: margin is a policy variable held in a 35-37% band; the ADR windfall built it and ADR ex-FX still funds it; the only structural cost lever that has shown up is support; regional mix is a persistent drag nobody quotes; and the FY28 answer sits between 34.6% (spend keeps growing at trend) and 37.4% (management's algorithm), with the difference living in field ops and G&A.

## Caveats

Fourteen quarters of y/y data, so every elasticity except cost of revenue is reported as unusable and imposed rather than estimated. The forward model inherits the 29 bridge's revenue path and its residual term. Management statements from the eight pre-2023 calls come from stockanalysis.com transcripts (audio-aligned, not corrector-reviewed; rows tagged `-sa`). Nothing here is a stock view.
