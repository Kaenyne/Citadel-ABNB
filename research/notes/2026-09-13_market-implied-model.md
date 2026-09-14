# The market-implied model: what the price, the options market and the sell-side tape are pricing for Airbnb

Krish with Claude Code, 13 Sep 2026. Branch `krish/reverse-dcf`. Workbook `model/ABNB_market_implied.xlsx` (formula-driven, recalculated in Excel, reconciled to a Python mirror: max difference 0.0014). Builder `analysis/src/reverse_dcf/market_implied_model.py`, which reads the four workstream outputs under `data/processed/reverse_dcf/A-D/` so that a repair there flows through on a rebuild. Workstream notes under `research/notes/reverse_dcf/` (A joint solve, B options, C reaction function, D sell-side), each with an independent audit (`audit_A` to `audit_D`; all four pass with fixes applied, no blockers). Companion to `2026-09-12_management-implied-model.md`, which this note assumes.

Price used: $170.19, the 11 Sep 2026 close. Every number below is one of ANCHOR (brief), MEASURED (computed from data by a workstream) or JUDGEMENT (a modelling choice, named).

## 1. Bottom line

1. **At $170.19 the market is paying for the Street and the team's base case, not for management's guide.** The joint solve (the multiple endogenous to growth, workstream A) identifies next-twelve-month revenue growth of **12.9%** (fitted-line band about 11.5 to 14.3; MEASURED, in the guide-proxy units the regression was fitted on, which run about a point above realised growth). Mapped to FY27 that is **revenue $15.7 to 15.9bn, +10.4 to +11.5%** (JUDGEMENT on the mapping), **adj. EBITDA $5.7bn at a 36.2% margin, EV/FY27 EBITDA 16.0 to 16.2x**, and **nights growth of +8 to +9%** at ADR ex-FX +3%, FX -0.6pp and a flat take rate. Management's delivered case is $16.0bn, +12.6%, nights +10%; the Street is $15.75bn; the team's base is $15.8bn. In realised units (about a point lower) the price sits between management's literal case and the Street, with the delivered case about $5 above it.

2. **The tape and the options market bracket the same answer.** The mean sell-side target ($179.5 to 182) is management's delivered case on the joint solve ($175) or 16.1 to 17.1x on that case's EBITDA (workstream D). The options market's 12-month risk-neutral median is $164 (lognormal; interquartile $126 to $214), i.e. the price itself within noise, and puts a risk-neutral 0.41 (lognormal; 0.43 skew-adjusted) on the stock being above the mean target in a year. Nothing in the price, the tape or the options surface is ahead of management; the disagreement is about the multiple, not the operating numbers.

3. **The range.** Each price point implies a different FY27 operating case. At $150 (bear tape) the joint solve needs FY27 revenue growth of about 7% and nights under 5%. At $165 (p25 target, and roughly the options median) it needs the Street. At $185 (median target) it needs management's delivered case plus two points. At $197.5 (p75 target) it needs management's ambition case (nights +14%). At $220 (top target) it needs nights growth of about 18% or a 19.5x multiple on the ambition numbers. The tails are mapping-dependent (JUDGEMENT): at $150 the FY27 growth reads 1.4 / 7.2 / 10.2% across the three mappings, at $220 16 / 21 / 31%.

4. **The 5 Nov print is priced for a 9.5% standard-deviation move (about a 7.6% expected absolute move), and the market expects an accelerating print.** The term structure of implied volatility around the 20 Nov expiry gives an event standard deviation of 8.5 to 10.5% (central 9.5%, JUDGEMENT inside the measured range; about half a point above ABNB's realised print root-mean-square of 8.9% on raw returns). Skew is ordinary for ABNB (25-delta risk reversal -3.5 vol points; a 10% out-of-the-money put costs 1.18x what a flat smile would imply relative to the call). The Street's 3Q26 nights bar is 148.9m (+11.45% on the letter's 133.6m), above 2Q26's +10.3%, so consensus already assumes acceleration. The team's own nowcast is +9.5 to 10.0%, a deceleration.

5. **Nights acceleration is the one print variable with a measurable reaction, and it is a sign rule, not a slope.** Workstream C re-tested the team's predictive-study result on the same prints: post-2022, prints with accelerating nights growth returned +6.0% on the day (QQQ-excess, close to close) and decelerating prints -5.6% (0 of 8 positive on excess returns, 2 of 8 on raw; Fisher p 0.007 between buckets). The size of the acceleration carries no coefficient, guide direction against the printed rate is not detectable (most guides are coded decelerating by construction), and none of the 17 pre-stated specifications clears a Holm multiplicity threshold, so this is a base rate with a sample of 14, not a model. Applied to the team's base case (3Q26 nights +9.9%, a deceleration) the conditional expected day-1 move is **-4% (n 16) to -6% (n 14)** on the sign rule, with the two-variable function at -8.5%; unconditionally, with the nowcast band putting 13 to 21% of the mass above the acceleration threshold, about -2 to -3.5%. Decelerating prints gap about -5% and recover about +1.7% intraday, so the move is close-to-close and is captured only by holding a position through the print.

6. **What the price does not contain.** Nothing for the new businesses (the joint solve at the price is inside the homes-only cases), nothing for a take-rate lift (the Street's 4Q26 revenue needs one, +20bp, which management has withdrawn), and no cancellation or RNPL term that anyone can observe. The reverse DCF says the price needs FY28 FCF growth of 4.6% fading to 3% on reported FCF, 16% on SBC-adjusted FCF: the SBC debate is the only place the market is demanding something management has not promised.

## 2. Method in one paragraph

The share price is taken as the market's fair value (Krish's decision). Workstream A re-estimated WS12's relationship between ABNB's EV/NTM EBITDA multiple and its forward revenue growth on 45 monthly observations 2023-26: multiple = 12.53 + 0.40 x growth (Newey-West t 3.1, R2 0.23, Durbin-Watson 0.53, about 16 independent observations). Because the multiple rises with growth, EV = M(g) x EBITDA(g) is a quadratic in g with one admissible root; solving it at each price gives the growth the market is paying for, jointly with the multiple it is paying. NTM growth is then mapped to FY27 two ways (subtracting the 1.4pp NTM-to-FY27 spread of the delivered case; or chaining through the Street's 2H26 revenue to an implied 1H27) and quoted as the range. Nights are backed out of revenue growth log-additively at ADR ex-FX +3.0% (management's "mix and price appreciation", the team's H note), FX -0.6pp (WS29 consensus EUR path) and a flat take rate (management's guide), so one point of ADR or take rate moves implied nights one for one. The fixed-multiple hold (16.5x on FY27 EBITDA at 36.2%) is carried as the fallback: at the price it agrees with the joint solve (FY27 +8.2% vs +10.4 to 11.5%), in the tails it does not (-6% at $150, +43% at $220), which is why the joint solve is primary (audit A concurs). Workstream B priced the 5 Nov event from the 16 Oct / 20 Nov implied-volatility pair (event variance = T_post x (sigma_post^2 - sigma_pre^2), assuming a flat background; the brief's original formula was wrong and was corrected) and built the 12-month distribution from the Jun 27 / Dec 27 expiries. Workstream C built a 23-print panel and tested the reaction of the day-1 QQQ-excess return to printed nights acceleration, guide direction, guide vs Street, and the revenue, EPS and EBITDA surprises. Workstream D translated the 32 live targets and the Zacks estimate range into implied multiples and operating cases.

## 3. The range: what each price point implies

Joint solve, spec A, FY27 on the management-delivered FY26 base ($14,231m) at a 36.2% margin. NTM growth MEASURED (guide-proxy units); FY27 and nights JUDGEMENT (mapping and decomposition). P(above) is the options market's risk-neutral probability of the stock being above that level in 12 months (lognormal on the 12-month ATM implied volatility; not a real-world probability).

| Price | What it is | Implied NTM growth | FY27 revenue growth, proportional / chained | FY27 EBITDA ($bn) | FY27 nights growth | Implied EV / FY27 EBITDA | Nearest case | Options P(above) |
|---|---|---|---|---|---|---|---|---|
| $125.5 | options 12M p25 | 3.0% | 1.6% / -10% | 5.2 | -1% | 12.5x | team bear ($14.3bn) | 0.75 |
| $150 | bear tape | 8.6% | 7.2% / 1.4% | 5.5 | 4.7% | 14.5x | below management literal | 0.59 |
| $163.8 | options 12M p50 | 11.6% | 10.2% / 7.6% | 5.7 | 7.6% | 15.5x | Street | 0.50 |
| $165 | p25 target | 11.8% | 10.4% / 8.1% | 5.7 | 7.9% | 15.6x | Street ($15.75bn) | 0.49 |
| **$170.19** | **price, 11 Sep** | **12.9%** | **11.5% / 10.4%** | **5.7** | **8.9% / 7.8%** | **16.0x** | **team base to Street** | **0.46** |
| $179.5 | mean target (brief) | 14.8% | 13.4% / 14.4% | 5.8 | 10.8% | 16.7x | management delivered (+12.6%) | 0.41 |
| $185 | median target | 15.9% | 14.5% / 16.7% | 5.9 | 11.9% | 17.1x | delivered +2pp | 0.38 |
| $197.5 | p75 target | 18.4% | 17.0% / 21.9% | 6.0 | 14.3% | 18.0x | management ambition (+18.0%) | 0.32 |
| $213.9 | options 12M p75 | 21.5% | 20.1% / 28.4% | 6.2 | 17.3% | 19.1x | above ambition | 0.25 |
| $220 | top target | 22.7% | 21.2% / 30.8% | 6.2 | 18.4% | 19.5x | above ambition | 0.23 |

The same solve run backwards prices the cases: management literal $162, Street $166, team base $168, management delivered $175, management ambition $203, team bull $207, team bear $121. At a fixed 16.5x on each case's own EBITDA: literal $169, delivered $176, ambition $188, Street $174, team base $175, team bear $137, team bull $209. One point of FY27 nights is worth about $4.90 a share (2.9%; $4.80 per point of revenue) on the joint solve and about $1.50 on a fixed multiple, because on the joint solve the multiple moves with the growth.

Reverse DCF at each price (10-year fade to 3%, WACC 10%, on the delivered case's FY27 FCF of $5.94bn; sensitivities in `A_reverse_dcf.csv`): the FY28 starting growth required is 0.6% at $150, 3.6% at $165, 4.6% at $170.19, 6.3% at $179.5, 9.3% at $197.5, 12.6% at $220; on SBC-adjusted FCF ($4.0bn) 12%, 15%, 16%, 18%, 21%, 24%.

## 4. The options market

| Item | Value | Label |
|---|---|---|
| First post-print expiry | 20 Nov 2026 (no 6 Nov weekly listed; 15 post-print sessions inside) | MEASURED |
| 20 Nov $170 straddle | 13.5% of spot (mid on a 12.0 to 15.0 market); a 70-day total move, an upper bound on the print | MEASURED |
| ATM implied volatility | 16 Oct 31.1%, 20 Nov 38.4%, 18 Dec 37.1%, 15 Jan 36.5%, 12-month 39.5% (own Black-76 from mids on a parity-checked forward) | MEASURED |
| Event standard deviation, 5 Nov | 9.9% (16 Oct / 20 Nov pair), 9.2% (least squares on five expiries), 9.7% (11 expiries, sloped background), 8.3% (two post-print expiries); +/-1 vol point on either leg moves it 8.4 to 11.2% | MEASURED |
| Central reading | 9.5% sd, 7.6% expected absolute move (range 8.5 to 10.5 / 6.8 to 8.4) | JUDGEMENT |
| Same method on the 4 Sep Bloomberg chain at $181.94 | 9.8 to 10.0%: the 8-10 Sep fall did not re-price the print, it added 1-2 vol points across the curve | MEASURED |
| Realised print history, 23 prints | raw close-to-close rms 8.9%, mean absolute 7.1%, median 6.9%, 48% of prints 7%+, 13 up / 10 down; QQQ-excess rms 8.5%, 11 up / 12 down | MEASURED |
| Implied vs realised historically | Bloomberg 30-day IV crush implied 10.5% sd per print vs 8.9% realised raw (ratio 0.85); the 30/60-day kink 45 days before past prints averaged 8.5%, so today's 9.2 to 9.9% is about half a point above where past prints were priced at this distance | MEASURED |
| Skew | 20 Nov 25-delta risk reversal -3.5 vol points (puts richer); 90/110 skew 3.3 points vs a 2021-26 30-day median of 4.4 (cross-method, approximate); a 10% OTM put is 1.18x richer than a flat smile implies relative to the call; risk-neutral P(above spot at 20 Nov) 0.49 | MEASURED |
| 12-month distribution (lognormal, forward $177.1) | p10 $99, p25 $126, p50 $164, p75 $214, p90 $272; P(above $179.5) 0.41, above $185 0.38, above $197.5 0.32, above $220 0.23; P(below $150) 0.41, below $125 0.25 | MEASURED (risk-neutral) |
| Skew-adjusted sensitivity | p25 $124, p50 $167, p75 $217; tails extrapolated, do not quote | MEASURED |

Reading: the options market prices the print at its own history plus half a point, with the usual ABNB downside premium and no crowded hedge; the 12-month distribution is centred on the price. Risk-neutral probabilities carry no equity or variance risk premium and are not forecasts; the below-spot median is mechanical (the forward is above spot, the lognormal median is below the forward).

## 5. The 5 Nov print: what is priced and what the team's case implies

Workstream C's panel (23 prints 4Q20-2Q26, QQQ-excess close-to-close day-1 return) and the audit's corrections.

| Finding | Result | Status |
|---|---|---|
| Printed nights acceleration, sign | post-2022 (n 14): accelerating +6.0% (4 of 5 positive on excess; one flat), decelerating -5.6% (0 of 8 positive on excess, 2 of 8 on raw); Fisher p 0.007 between buckets; coefficient +5.7% per unit sign, HC1 t 2.7, leave-one-out R2 +0.28, permutation p 0.017. On the pre-stated n 16 sample (3Q22 on): +3.4 vs -3.6, t 1.4, LOO -0.02, perm 0.16 | MEASURED; a re-test of the predictive study on the same prints, not multiplicity-robust (Holm threshold 0.0029 across 17 pre-stated specs, best p 0.040) |
| Acceleration in points | no coefficient (Spearman 0.38, p 0.19 at n 14); a threshold, not a slope | MEASURED |
| Next-quarter guide direction vs the printed rate | not detectable: 3 accelerating guides in 16, 11 decelerating by construction | MEASURED (power) |
| Next-quarter revenue guide vs Street | +1.9% return per 1% above Street (t 2.2, LOO R2 +0.15) on n 16 and +1.4% (t 2.4, LOO +0.15) on n 19 with the low-confidence 4Q21 point clipped; fails on n 14; drop 2Q24 and it vanishes | MEASURED, fragile |
| Revenue, EPS, EBITDA surprise; FY guide raise; nights beat vs consensus; pre-print run-up | nothing survives out of sample | MEASURED (clean negatives) |
| Tradeable? | decelerating prints gap -5.3% at the open and recover +1.7% intraday (9 of 9); the executable next-open return shows nothing; the expected move is the gap | MEASURED |

Expected day-1 excess return by scenario (S1 sign rule, conditional on the print's acceleration sign; S2 two-variable function illustrative):

| Scenario | 3Q26 nights | 4Q26 revenue guide | S1 sign rule | S2 (illustrative) |
|---|---|---|---|---|
| Team base (WS29/30): 3Q26 +9.9%, 4Q26 $3,111m | decelerating | -1.4% vs Street | **-6.1%** (n 14) / -4.0% (n 16) | -8.5% (Zacks comparator: -11.5%) |
| Team base with the ex-NA lap (4Q26 8.1%, $3,102m at the team's 0.38%/pt elasticity) | decelerating | -1.7% | -6.1% | -9.2% |
| Q3 nowcast central (+9.75%, 4Q26 $3,121m) | decelerating | -1.0% | -6.1% | -7.9% |
| Street (Bloomberg FA): +11.1%, $3,154m | accelerating | 0.0% | +5.2% | +2.0% (Zacks comparator: -1.0%) |
| Management delivered: +11.5%, $3,130m | accelerating | -0.8% | +5.2% | +0.4% (Zacks: -2.5%) |
| Flat print: 3Q26 = 2Q26 rate, guide at Street | flat | 0.0% | -0.5% | -1.9% |
| 2Q26 replay: accelerating print, guide +2.6% vs Street | accelerating | +2.6% | +5.2% | +7.4% |

Unconditionally, with the team's nowcast band (8.5 to 11.0) placing 13 to 21% of its mass above the 10.6% acceleration threshold, the S1 expectation for the team's case is -1.9% (n 16) to -3.5% (n 14). The realised-move range around the conditional expectation (plus or minus 1.28 residual standard deviations) is about -15% to +7%. The options market's 9.5% event sd is the dispersion around any of these expectations, not a substitute for them. The residual standard deviation of the reaction function is 6.9 to 8.8 points (S1) and 7.3 (S2), so the sign is the claim, not the size.

What is "priced": an accelerating 3Q26 (nights above about 10.6%) with a 4Q26 revenue guide at or just below the Street's $3,154 to 3,200m. That is also the Street's own forecast and management's delivered case. The team's base case is a decelerating print with a guide 1 to 3% below the Street, for which the post-2022 base rate is 0 of 8 positive days on excess returns (2 of 8 on raw) and 1 of 9 since 3Q22 (3 of 9 raw).

## 6. The sell-side tape

32 live targets (12 Sep 2026 pull; Goldman corrected from the feed's Sell $155 to Neutral $165; mean $182.1, median $182.5, p25 $165, p75 $200, range $125 Morgan Stanley to $220 Rosenblatt and DA Davidson; 34% of targets below the price). Three moves during the 8-10 Sep fall, all up: Baird $175 to $200, Raymond James upgrade to Outperform $200, Truist $134 to $161. Nobody cut.

| Tape level | Target | Implied EV / FY27 delivered EBITDA (spot / FY27-end basis) | At 16.5x: FY27 revenue, growth | FY27 nights at 16.5x | Joint-solve FY27 growth |
|---|---|---|---|---|---|
| min | $125 | 11.2x / 10.5x | $10.9bn, -23% | -25% | about +1.5% |
| p25 | $165 | 15.3x / 14.4x | $14.9bn, +4.6% | +2.2% | +10.4% |
| price | $170.19 | 15.9x / 14.9x | $15.4bn, +8.2% | +5.7% | +11.5% |
| mean | $181.8 | 17.1x / 16.1x | $16.6bn, +16.4% | +13.7% | +13.9% |
| p75 | $200 | 18.9x / 17.8x | $18.4bn, +29% | +26% | +17.5% |
| max | $220 | 21.0x / 19.8x | $20.4bn, +43% | +40% | +21.2% |

Reading (D, as corrected by its audit): the tape is a multiple call on management's delivered numbers, partly by construction; held at a single multiple the p25-p75 range would require FY27 growth of +5 to +29%, which no analyst forecasts. The real operating dispersion is in the estimates: the Zacks FY27 revenue range $14.99 to 16.29bn maps to nights +2.9 to +11.8% on the delivered base (consensus $15.73bn to +8.0%, one to two points below management; the only direct nights consensus, Bloomberg's 3Q26/4Q26 bars, is 0.4 points below management). Bulls with published arithmetic run a consensus-like operating case on a higher multiple, with one exception: Bernstein's $217 at "25.5x core earnings" is a P/E implying $8.51 of FY27 earnings, 40% above management's delivered EPS. Targets follow the price in both directions with a one-to-two-month lag (six down prints of 5%+ drew -3.8% in the mean target at +20 sessions, six up prints +6.3%; block-regression betas sum to 0.26 to 0.36), so a $5 to 7 cut in the mean target over the next two to three months is the base case after the 8-10 Sep fall. Positioning: short interest 2.2% (bottom decile), put/call open interest 1.1, Buy share 59%, Hold-or-worse 31 to 46% depending on the feed; none of it has detectable predictive content in-sample.

## 7. Management vs market vs team: the one table

FY27E on the delivered FY26 base; nights at ADR +3%, FX -0.6pp, take rate flat (JUDGEMENT).

| Who | Price / target | FY27 revenue growth | FY27 revenue | FY27 adj. EBITDA | FY27 nights growth | EV / FY27 EBITDA | Options P(above) | Expected 5 Nov day-1 move (S1, conditional) |
|---|---|---|---|---|---|---|---|---|
| Market, current price (joint solve) | $170.19 | 10.4 to 11.5% | $15.7 to 15.9bn | $5.7bn | 8 to 9% | 16.0x | 0.46 | priced for an accelerating print |
| Market, current price (fixed 16.5x) | $170.19 | 8.2% | $15.4bn | $5.6bn | 5.7% | 16.5x | 0.46 | |
| Options 12M median | $164 | 10.2% | $15.7bn | $5.7bn | 7.6% | 15.5x | 0.50 | |
| Sell-side mean target (brief $179.5; 12 Sep tape $181.8 reads 13.9%, 16.9x) | $179.5 | 13.4% | $16.1bn | $5.8bn | 10.8% | 16.7x | 0.41 | |
| Management literal | $162 (joint) / $169 (16.5x) | 9.8% | $15.6bn | $5.5bn | 7.3% | 15.7x | 0.50 | |
| Management delivered | $175 / $176 | 12.6% | $16.0bn | $5.8bn | 10.0% | 16.4x | 0.43 | +5.2% |
| Management ambition | $203 / $188 | 18.0% | $16.8bn | $6.2bn | 15.2% | 17.9x | 0.30 | |
| Street | $166 / $174 | 10.6% | $15.75bn | $5.7bn | 8.1% | 15.7x | 0.48 | +5.2% |
| Team base (WS29/30) | $168 / $175 | 11.0% | $15.8bn | $5.8bn | 8.5% | 15.8x | 0.47 | **-6.1%** |
| Team bear (WS29) | $121 / $137 | 0.6% | $14.3bn | $4.4bn | -1.7% | 14.4x | 0.76 | |
| Team bull (WS29) | $207 / $209 | 18.8% | $16.9bn | $7.0bn | 16.1% | 16.3x | 0.28 | |

The table says three things. The price, the Street, the team's base and the options median all sit within about a point of each other on FY27 revenue growth (10 to 11.5%) and within $6 of each other on value; management's delivered case is 1 to 2 points above them and is the sell-side mean, $5 to 12 above the price. The team's disagreement with the market is not about FY27 revenue (it is the same number); it is about the 3Q26 print (decelerating vs the accelerating print the Street and the options market assume) and the 4Q26 guide (below the Street), which is where the trade pivot note already put it.

## 10. Is the market positioned for an accelerating 3Q26? The positioning card

Krish's question after the run: the reverse DCF is meant to show that the market is positioned for the opposite of the team's 3Q26 and 4Q26. Workstream E (`analysis/src/reverse_dcf/E_positioning_card.py`, outputs `data/processed/reverse_dcf/E/`, audited in `audit_E.md`: pass with fixes, applied) answers it in three tables. The honest answer is split: **on nights the Street's bar is positioned for acceleration and the price carries most of it; on revenue and valuation the price is within 1 to 3% of the team's own path.** And the bar is not an independent market view: it is management's guide.

**1. The Street's nights bar has implied acceleration only three times in 16 scored prints, and 5 Nov is the fourth.** At every print with a nights consensus, compare the growth the Street's bar implies (bar over the year-ago quarter) with the just-printed rate, 0.25pt dead band (MEASURED, `E_street_sign_history.csv`; the bar series is spliced across StreetAccount, LSEG, Zacks and Bloomberg):

| Street's bar positioned for | Prints | Printed acceleration | Printed deceleration | Mean day-1 excess return |
|---|---|---|---|---|
| acceleration (4Q21, 3Q23, 4Q24) | 3 | 3 | 0 | +4.2% |
| flat (3Q25) | 1 | 1 | 0 | +0.6% |
| deceleration | 12 | 2 (4Q25 +4.4%, 2Q26 +16.3%) | 8 | +0.4% |
| **3Q26E: 148.9m = +11.45% vs 2Q26 +10.34%** | **acceleration, +1.1pt** | | | |

The big up days came when a decelerating bar met an accelerating print (2Q26, 4Q25, 4Q24). This time the bar itself is an acceleration, the first since 4Q24 (and 4Q21 is a reopening comp; post-3Q22 the count is 2 of 13). No print in the sample pairs an accelerating bar with a decelerating print, so that reaction is unobserved; the sign rule (section 5) is the closest evidence.

**The bar is the guide.** In the 13 scored prints where management gave a next-quarter nights guide, the Street's bar carried the same sign as the guide in 12 (`E_guide_vs_street_sign.csv`). Both accelerating guides (3Q23, 4Q24) were met, and there is one soft downside miss in 13 (1Q25: guided "stable", printed 0.4pt lower). The 3Q26 bar sits in the upper half of management's "low double-digit" bucket (midpoint 11.0, itself +0.7pt on 2Q26). So the team's call is not a bet against Street positioning; it is a bet on the first downside miss of a management nights guide in the sample. That is what a sceptical judge will say first, and the slide should say it before the judge does.

**2. What nights rate the price carries.** Shift the team's own bridge by a uniform nights uplift until NTM revenue matches the price-implied NTM, using the bridge's additive convention (revenue y/y = nights + ADR ex-FX + FX + residual, as in WS30's file) on both team baselines (`E_price_implied_2h26_path.csv`; MEASURED on the solve, JUDGEMENT on the bridge and the uplift shape):

| Team bridge | Price-implied NTM (units) | Gap vs team NTM | Uplift (pts of nights) | Implied 3Q26 nights | Sign vs 2Q26 +10.34% | Gap to Street bar 11.45% | Implied 4Q26 revenue |
|---|---|---|---|---|---|---|---|
| WS30 pnl (3Q26 10.3 / 4Q26 9.9) | 12.9% (guide-proxy) | +$42m | +0.3 (uniform) / +0.6 (2H26 only) | 10.6% / 10.9% | marginal acceleration | -0.8 / -0.6 | $3,120m / $3,128m |
| 10 Sep pivot (3Q26 9.9 / 4Q26 8.9) | 12.9% (guide-proxy) | +$87m | +0.7 / +1.3 | 10.6% / 11.2% | flat / acceleration | -0.9 / -0.3 | $3,101m / $3,118m |
| either | 11.6% (realised units, bias removed; unstable) | -$93 to -138m | -0.7 to -2.0 | 8.3 to 9.2% | deceleration | -2.2 to -3.2 | $3,045 to 3,082m |
| Street path (Bloomberg 2H26 + 1H27 at Street FY27) | 13.0 to 13.4% | +$57 to 152m | +0.4 to +2.2 | 10.7 to 12.1% | acceleration | -0.8 to +0.7 | $3,104 to 3,155m |
| management delivered | 14.0% | +$186 to 231m | +1.4 to +3.4 | 11.7 to 13.3% | acceleration | +0.2 to +1.8 | $3,131 to 3,187m |

Read plainly: in the units the regression was fitted on, the price carries a 3Q26 nights rate of about 10.6 to 11.2%, between the team's path and the Street's bar and closer to the bar (0.3 to 0.9pt below it); in realised units it carries 8.3 to 9.2%, below the team. On every proxy-unit convention the price-implied 4Q26 revenue ($3,100 to 3,134m) sits below the Bloomberg $3,154m and Zacks $3,200m consensus. The first finding (the price is within 1 to 3% of the team's revenue path) is robust; the sign the price carries for 3Q26 is not identified, because it straddles the dead band across defensible conventions.

**3. The repricing ladder for 5 Nov** (`E_repricing_ladder.csv`). The fundamental column is the joint-solve repricing if the market re-anchors NTM growth to the printed path (same units as it prices today; the realised-units alternative is $6 to 7 higher in every row and is shown in the CSV). The sign-rule column (S1, post-2022 n 14 and n 16) is a total day-1 excess return that already contains whatever estimate effect there was, so the two columns are alternatives, not addends.

| Outcome on 5 Nov | NTM growth | Joint-solve price | Fundamental repricing | Sign rule (history of the day) |
|---|---|---|---|---|
| Street path prints (3Q26 +11.45%, 4Q26 $3,177m) | 13.0 to 13.4% | $170.7 to 172.6 | +0.3 to +1.4% | +2.7 to +5.2% |
| Management delivered prints (3Q26 +11.5%, 4Q26 $3,130m) | 14.0% | $175.5 | +3.1% | +2.7 to +5.2% |
| Team pnl bridge prints (3Q26 +10.3%, 4Q26 +9.9%) | 12.6% | $168.7 | -0.9% | -4.0 to -6.1% |
| Team pivot baseline prints (3Q26 +9.9%, 4Q26 +8.9%) | 12.3% | $167.0 | -1.9% | -4.0 to -6.1% |
| Pivot baseline with the ex-NA lap (4Q26 +8.1%, 1H27 unchanged) | 12.1% | $166.2 | -2.3% | -4.0 to -6.1% |
| Same, with the lap also taking 0.8pt off 1H27 | 11.7% | $164.4 | -3.4% | -4.0 to -6.1% |

The fundamental level is uncertain by about $7 to 15 (the units choice; A found the proxy bias unstable), but the differences between rows are robust: the team's path is worth 1 to 5% less than the Street's on the multiple-growth line, and the Street's path is worth about what the stock trades at.

**4. The whole Street distribution, not just the mean (Bloomberg MODL, 12 Sep 2026, from Krish's terminal; `E_street_distribution_vs_team.csv`).** Growth on the letter bases (3Q25 nights 133.6m, GBV $22,892m; 4Q25 nights 121.9m, GBV $20,400m).

| 3Q26 | Estimates | Low | Mean | High | Team | Team's position |
|---|---|---|---|---|---|---|
| Nights | 28 | 147m, +10.0% | 149m, +11.5% | 151m, +13.0% | 146.8m, +9.9% | below the lowest estimate |
| GBV | 28 | $25,992m, +13.5% | $26,375m, +15.2% | $26,723m, +16.7% | about $25.9bn, +13.1% | at or below the lowest |
| ADR | 26 | $173.71, +1.4% | $177.06, +3.4% | $179.12, +4.6% | $176.9, +3.3% | inside, near the mean |
| Take rate | 28 | 17.82% | 18.00% | 18.44% | about 18.4% | inside, near the top |

| 4Q26 | Estimates | Low | Mean | High | Team | Team's position |
|---|---|---|---|---|---|---|
| Nights | 28 | 130m, +6.6% | 134m, +9.9% | 136m, +11.6% | 132.7m, +8.9% (131.8m, +8.1% with the ex-NA lap) | inside, lower half |
| GBV | 28 | $22,177m, +8.7% | $23,003m, +12.8% | $23,565m, +15.5% | about $23.1bn, +13.2% | inside, near the mean |
| ADR | 25 | $167.79, +0.2% | $171.33, +2.3% | $174.21, +4.0% | $174.1, +3.9% | inside, at the top |
| Revenue | 37 | $3,052m, +9.9% | $3,157m, +13.6% | $3,223m, +16.0% | $3,111m, +12.0% | inside, lower third |
| EPS | 29 | $0.67 | $0.87 | $1.36 | $0.81 | inside, lower third |

This is the cleanest positioning fact in the card. For 3Q26, not one of 28 analysts models a deceleration: the lowest nights estimate is 2Q26's rate, and the team's 146.8m sits below the entire range while the team's ADR sits on the consensus, so the whole disagreement is nights, not price. For 4Q26 the range is wide enough that the team's base sits inside it, in the lower half, so the 4Q26 argument is a guide-below-consensus argument, not a below-the-range argument. The Bloomberg Earnings Estimates Graph (`E_street_nights_estimate_path.csv`, read off the image) shows the mechanism: the 3Q26 bar went from about 145.4m before the 6 Aug print to about 148.5m after it, a 2.1% lift that matches the 2Q26 beat (148.3m printed against a 145.44m bar), and has drifted to 148.96m since; the 4Q26 bar rose 1.1% on the print. The Street carried the beat forward one for one, which is what workstream D found for targets and what the 12-of-13 guide match in table 1 implies.

**What the card supports for the pitch.** The Street's nights bar is positioned for acceleration (only the fourth such bar in 16 prints), every one of the 28 estimates behind it is at or above 2Q26's rate and the team's 3Q26 nights sit below the lowest of them, the price carries most of that bar in the units it is priced in, short interest is in its bottom decile, three houses raised targets into the 8-10 Sep fall, and the options market carries no extra event premium. The team's case is a flat-to-decelerating print, and the historical reaction to that sign is -4 to -6% on the day (conditional; -2 to -3.5% unconditional under the nowcast band). What the card does not support is a valuation gap: the price is within 1 to 3% of the team's own revenue path, so the trade is the print reaction and the multiple, not an estimate revision; and because the bar is the guide, the pitch is a call that management misses a nights guide to the downside for the first time in the sample, and it should be framed as exactly that.

## 8. What this can and cannot say

**Can.** The growth the market pays for at any price, given the fitted multiple-growth relationship; the range across the tape and the options quartiles; the options market's implied print move and skew; the historical base rate of the print reaction conditional on nights acceleration; what each analyst target requires; how the Street's numbers relate to management's.

**Cannot.** Separate "12.9% growth at 17.7x" from "17.8% guide-proxy growth at 16.9x, not believed": the regression's residual scatter is +/-3 turns and the slope is weakly identified (t 3.1 in levels on about 16 independent observations, near zero in 12-month changes and in 2024-26 alone; the 24-month rolling slope runs -0.18 to +0.94). The tails of the price range are mapping-dependent by 6 to 15 points of growth. Nights are a residual of revenue at an assumed ADR, FX and take rate, not a priced variable in their own right; the only direct nights consensus is Bloomberg's 3Q26 and 4Q26 bars. The reaction function is 14 to 16 observations, a re-test rather than a discovery, and the magnitude (residual sd 7.3 points) is not usable; its content is the sign. Risk-neutral probabilities are not forecasts. Cancellation rate and RNPL timing are unobservable to the market and to us; they live in the -0.6 to -1.1pp revenue timing residual. The sell-side feed covers 32 of 40 to 46 analysts with 96 chain breaks, so raise/cut counts are lower bounds.

**What would change the reading.** A 6 Nov weekly expiry listing (cleaner event variance; re-pull the last week of September). The September Inside Airbnb dumps (the nowcast band narrows, and with it the conditional vs unconditional gap in section 5). Any management appearance that updates the 3Q26 nights rate. A re-estimate of the multiple-growth slope after the 5 Nov print adds a 17th independent observation.

## 9. Files

- `model/ABNB_market_implied.xlsx`: Cover, Inputs, Market_Implied, Cases, Print_5Nov, SellSide, Options, Comparison, Recon.
- `analysis/src/reverse_dcf/market_implied_model.py` (builder); workstreams `A_*.py`, `B_*.py`, `C_*.py`, `D_*.py`, `E_positioning_card.py`.
- `data/processed/reverse_dcf/market/`: `market_implied_by_price.csv`, `market_implied_cases.csv`, `market_implied_print_scenarios.csv`, `market_implied_comparison.csv`, `market_implied_recon.csv`, `market_implied_params.json`.
- `data/processed/reverse_dcf/A/` (23 files), `B/` (31), `C/` (19), `D/` (20), `E/` (7: Street sign history and summary, guide-vs-bar sign, price-implied 2H26 path, repricing ladder, Bloomberg MODL distribution vs team, EEG nights-estimate path), `audit/` (6 findings CSVs).
- Notes: `research/notes/reverse_dcf/A_joint-solve.md`, `B_options-implied.md`, `C_reaction-function.md`, `D_sell-side-dispersion.md`, `audit_A.md` to `audit_D.md`; run brief and state under `docs/reverse_dcf/`.
