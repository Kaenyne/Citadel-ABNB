# 29. The Q4 2026 and FY27 revenue-growth bridge

Krish with Claude Code, 7 Sep 2026. Script `analysis/src/overnight/29_q4_fy27_bridge.py` (`py -3.13`; re-pulls FRED on every run, so re-run it weekly and in the week of the print). Outputs `data/processed/overnight/29_bridge_assumptions.csv`, `29_fx_refresh.csv`, `29_fx_step_down.csv`, `29_residual_history.csv`, `29_q4_2026_bridge.csv`, `29_fy27_bridge.csv`, `29_fy27_quarterly_path.csv`; figure `analysis/figures/overnight/29_q4_fy27_bridge.png`. Nothing here is newly sourced: it stacks workstreams 05 (FX), 10 (regional nights and ADR), 28 (hedge) and 02 (actuals) into one walk, with the Street from workstream 04 as a comparison column only.

## Bottom line

1. **The Q4 2026 revenue guide steps down about three and a half points from the Q3 guide on FX alone, and 82% of that FX term is already observed.** Q3 was guided with "an approximate three percentage point foreign exchange tailwind after factoring in our hedging program". The revenue-FX fit (EUR/USD y/y averaged over the two prior quarters, workstream 05) gives **−0.4pp for 4Q26**, because the driver for Q4 is the 2Q26 and 3Q26 euro, and both are known (3Q26 is 64% complete at 28 Aug). Guide-anchored the step is **−3.4pp**; fit-to-fit it is **−2.6pp**; the fit's leave-one-out error is ±2.3pp, so the honest range on the Q4 FX term itself is −2.7 to +1.9pp. The sign of the step-down does not depend on the FX path: consensus, strong-dollar and weak-dollar paths all give the same 4Q26 number.
2. **Base-case 4Q26 reported growth is +12.0%, $3,111m, against a Street at $3,200m (+15.2%).** The walk from the Q3 guide midpoint (+15.5%): FX −3.4, nights −1.1 (the regional build's 9.9% against the guide's "low double-digit", which is the RNPL US lap against a +9.8% 4Q25 comp), ADR ex-FX 0.0, take-rate and timing residual +1.0 (the guide-implied residual is −1.5pp, the trailing-four mean −0.5pp). Bear +6.6% ($2,961m), bull +16.7% ($3,241m). **Only the bull clears the Street.** The Street range for Q4 is $3,050-3,700m, a 21% spread; the base sits below its bottom.
3. **FY27 base is +11.6%, which is where the Street already is (+11.3 to +11.5%). The disagreement is not the year, it is the shape.** The FY27 walk from FY26 base (+15.7%): FX −3.4 (FY26 carried +2.7pp of stated FX, FY27 carries −0.6pp on the consensus euro path), nights −0.8, ADR ex-FX −0.5, residual +0.5. The quarterly phasing puts 1Q27 at **+9.9%** against 1Q26's +17.9% and 2Q27 at **+10.7%** against +16.5%, then +11.9% and +13.4%. If the Street's FY27 is phased like FY26, its first-half numbers are too high and its second half too low. The bear is +3.2% (strong dollar −2.6pp, nights 5.8%, ADR 1%); the bull +17.0%.
4. **The FX term is the only one that is arithmetic. The other three are judgement, and the note says which.** The nights step is the regional bottom-up (workstream 10), labelled with management's own attribution of ~2pt (4Q25) and ~3pt (1Q26) of nights growth to three product features, but not subtracted twice. The residual is the least certain term: it swung from −4.2pp (revenue minus GBV growth, 3Q25) to +0.8pp (2Q26) as Reserve Now Pay Later moved guest payments toward check-in, and the Q3 guide assumes it stays near the favourable end.
5. **For 5 November the question is not whether Q4 is guided at +12% but whether management says why.** The 4Q25 letter quantified Q1's FX ("an approximate three point foreign exchange tailwind"); the 1Q26 letter quantified Q2's ADR FX ("significantly lower in Q2 2026 than in Q1"); the 2Q26 letter quantified Q3's. If the Q4 guide arrives at +11-13% *with* an FX sentence, the market has the bridge. If it arrives without one, all nine prior guide-below-Street prints had a negative 20-day excess return (mean −4.2% on an executable entry, base-rate p 0.038, workstream 20).

## The Q4 2026 bridge

Reported revenue growth, % y/y. Start is the 2Q26 letter's Q3 guide midpoint ($4,730m on 3Q25's $4,095m). Each step is the change in one term between what the guide implies for Q3 and what we assume for Q4.

| Term | Bear | Base | Bull | What sets it |
|---|---|---|---|---|
| 3Q26 guide midpoint | 15.5 | 15.5 | 15.5 | 2Q26 letter |
| FX after hedging | −3.4 | −3.4 | −3.4 | +3.0 guided in Q3 to −0.4 fitted for Q4; driver 82% observed; identical on all three euro paths |
| Nights | −4.0 | −1.1 | +1.1 | guide "low double-digit" (11) to 4Q26 regional build 7.0 / 9.9 / 12.1; RNPL US lap plus +9.8% comp |
| ADR ex-FX | −1.0 | 0.0 | +1.0 | 3.0 to 2.0 / 3.0 / 4.0 |
| Take-rate / timing residual | −0.5 | +1.0 | +2.5 | guide-implied −1.5 to −2.0 / −0.5 / +1.0 |
| **4Q26 reported growth** | **6.6** | **12.0** | **16.7** | |
| 4Q26 revenue, $m | 2,961 | 3,111 | 3,241 | on 4Q25 $2,778m |
| vs Street $3,200m | −7.5% | −2.8% | +1.3% | Zacks, 10 estimates, 4 Sep 2026; range 3,050-3,700 |

Where the guide's implied Q3 terms come from: midpoint growth 15.5 less stated FX 3.0 is ex-FX growth 12.5; nights at the bucket midpoint 11 and ADR ex-FX 3 (letters have run +3 / +4 / +4%) leave a residual of −1.5pp. That residual is the guide's implicit assumption about booking-versus-stay timing and take rate; the realised series is in `29_residual_history.csv` (3Q24 to 2Q26: −0.5, −2.4, −0.9, +4.6, −0.8, −1.8, +1.9, −1.3; trailing-four mean −0.5).

The hedge sits inside the FX bar and is a memo, not a separate step: the 2Q26 10-Q expects ~$26M of deferred losses to reach revenue over the next twelve months, about −0.2pp a quarter (workstream 28).

## The FY27 bridge

| Term | Bear | Base | Bull | What sets it |
|---|---|---|---|---|
| FY26 reported growth | 13.4 | 15.7 | 18.1 | 1H26 actual $6,286m + 3Q26 (10 note: $4,633 / 4,775 / 4,932m) + 4Q26 above; Street $14,100-14,160m |
| FX after hedging | −5.4 | −3.4 | −1.8 | FY26 stated 0 / +3 / +4 / +3 (Q4 fitted) = +2.7pp; FY27 strong −2.6 / consensus −0.6 / weak +1.1pp |
| Nights | −3.7 | −0.8 | +1.2 | FY26 9.5 / 10.0 / 10.3 to FY27 regional 5.8 / 9.2 / 11.5, phased heavier in 1H27 |
| ADR ex-FX | −2.0 | −0.5 | 0.0 | 3.0 / 3.5 / 4.0 to 1.0 / 3.0 / 4.0 |
| Take-rate / timing residual | +0.9 | +0.5 | −0.6 | FY26 implied plug to −1.0 / 0.0 / +0.5; take rate flat |
| **FY27 reported growth** | **3.2** | **11.6** | **17.0** | |
| FY27 revenue, $m | 14,318 | 15,804 | 16,910 | Street $15,730-15,760m |

Cross-check: the regional note's FY27 base is +12.4% with FX at zero; this note's +11.6% is the same nights and ADR with FX at −0.6pp from the consensus euro path. The driver model's FY27 base is +12%. Three constructions, one answer within a point.

### FY27 quarterly phasing, base case

| Quarter | Nights | ADR ex-FX | Residual | FX | **Reported growth** | Revenue $m | Prior-year growth | Lap |
|---|---|---|---|---|---|---|---|---|
| 1Q27 | 8.0 | 3.0 | 0.0 | −1.0 | **+9.9** | 2,944 | +17.9 | global three-feature lap (1Q26 +3pt, management), Middle East base |
| 2Q27 | 8.5 | 3.0 | 0.0 | −0.8 | **+10.7** | 3,992 | +16.5 | World Cup bookings (2Q26), RNPL eligibility expansion (Jul 2026) |
| 3Q27 | 9.6 | 3.0 | 0.0 | −0.6 | **+11.9** | 5,341 | +16.6 (base) | clean comp; hotels and AI pricing are the swing |
| 4Q27 | 10.5 | 3.0 | 0.0 | −0.1 | **+13.4** | 3,527 | +12.0 (base) | clean comp |

The nights phasing (FY27 total 9.2, spread −1.2 / −0.7 / +0.4 / +1.3 around it) is a judgement about where the laps land, not a disclosure. Bear and bull rows are in `29_fy27_quarterly_path.csv`.

## FX refresh, consensus path (FRED to 28 Aug 2026)

| Quarter | EUR/USD y/y | Driver (two-prior-quarter mean) | Fitted revenue FX, pp | Stated, pp | Share of driver observed |
|---|---|---|---|---|---|
| 3Q25 | +6.4 | +1.2 | −0.2 | 0 | 100% |
| 4Q25 | +9.1 | +5.9 | +1.8 | +1 | 100% |
| 1Q26 | +11.1 | +7.7 | +2.6 | +3 | 100% |
| 2Q26 | +2.6 | +10.1 | +3.6 | +4 | 100% |
| 3Q26 | −1.6 (QTD) | +6.8 | +2.2 | guided ~+3 | 100% |
| **4Q26** | −0.4 | **+0.5** | **−0.4** | | **82%** |
| 1Q27 | −0.4 | −1.0 | −1.0 | | 32% |
| 2Q27 | +0.6 | −0.4 | −0.8 | | 0% |
| 3Q27 | +2.1 | +0.1 | −0.6 | | 0% |
| 4Q27 | +1.7 | +1.4 | −0.1 | | 0% |

The fit under-predicted the stated number by 0.4 to 0.8pp in each of the last three quarters, which is why the guide-anchored step (−3.4) and the fit-to-fit step (−2.6) are both shown. Strong-dollar and weak-dollar paths differ only from 1Q27 (`29_fx_refresh.csv`).

## What this bridge is for

- **Before 5 November:** the deck's Q4 slide is this table. State the FX term as arithmetic with its observed share, the nights term as the regional build labelled with management's own product attribution, and the residual as the assumption it is. Put the Street's $3,200m beside the base, not inside it.
- **On 5 November:** score the guide against the three rows. A Q4 midpoint of +11-13% with the FX quantified is the base case and the market should be able to read it. A midpoint of +11-13% *without* an FX sentence is the "guide below Street, misread as demand" setup. A midpoint above +14% means either the residual is running at the favourable end again (check the implied take rate against 13.6%) or nights are above 11% in Q4, which would be a genuine demand fact.
- **For FY27:** do not argue with the Street's annual number, argue with its shape. First-half 2027 reported growth near +10% on a business whose nights are still growing 8-9% is the thing a growth-set multiple (+0.48 turns per point of forward revenue growth, workstream 12) has to digest.
- **For the margin case:** every point of FX on revenue is worth about 0.47 points of Adjusted EBITDA margin at Airbnb's dollar cost base (margin-drivers note §14), so the −3.4pp FX step in Q4 is roughly −1.6 margin points against a Q3-style tailwind, before any marketing decision. Workstream 07's FY26 attribution already shows the whole year's margin gain as ADR-plus-FX (+3.6) less marketing (−2.2); FY27 starts without the FX half.

## Caveats

- The FX fit has n 17 and a leave-one-out error of 2.3pp; it is right about the sign and the timing of the step-down, not about the second decimal. The 4Q26 number is the same on all three euro paths because its driver is already observed, which is the point; from 1Q27 the path matters and the three paths span −2.6 to +1.1pp on FY27.
- Nights and ADR ex-FX are the regional bottom-up's bucket-midpoint construction (±1.1pp reconciliation error, workstream 10). The 3Q26 revenue used inside FY26 is a base-case assumption ($4,775m, +1% on the midpoint), not a print.
- The residual conflates take rate, booking-versus-stay timing and the RNPL cash-timing effect. It cannot be separated with public data; the history table is there so the reader can pick a different number.
- Management's product attribution is quoted, not modelled: the nights step-down is the regional build's, and the attribution explains it rather than adding to it (audit CONF-12).
- The Street numbers are Zacks (7-13 estimates) and S&P Global as of 3-4 Sep 2026; the Q4 range is wide and the vendor column should stay attached.
