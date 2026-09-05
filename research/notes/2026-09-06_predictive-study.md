# Predictive study: what in our ABNB data actually forecasts anything

- **Sources:** the five component notes in `research/notes/predictive/` (01 forecasting framework and base rates, 02 peer read-through, 03 macro and alt-data nowcasts, 04 margin and reaction function, 05 pitch scorecard), each with its script in `analysis/src/predictive/` and outputs in `data/processed/predictive/`. Inputs are the margin-branch datasets plus copies of the other branches' panels in `data/external/` (see data/README.md for provenance). Peer prints from EDGAR 8-K exhibits (S37), sixteen FRED series (S38).
- **Date:** 2026-09-06
- **Author:** Krishang Surapaneni (compiled with Claude Code; five parallel analyses).
- **Sample:** 23 Airbnb prints (Q4 2020 to Q2 2026), 19 with a numeric revenue guide, 14 in the post-2022 regime that matters. Smallest detectable correlation at n = 23 is about 0.41; roughly 1,500 tests were run across the five workstreams, so about 75 spurious 5% hits were expected. Everything below has been filtered for out-of-sample value against a naive baseline and for point-in-time availability; results that fail are listed as negatives, not omitted.

---

## 1. Bottom line

1. **There is no print-day alpha in public data.** Nothing we hold predicts the revenue beat versus guide (Airbnb beat the midpoint 19 of 19 times, so the beat is a constant, not a variable) or the day-1 excess return (best adjusted q-value 0.33, signs flip across windows). Theo's earlier 0.03 to 0.08 guidance-to-return result reproduces. Booking's and Expedia's prints do not read through, and half the time they arrive after Airbnb's anyway.
2. **The edge is in the second derivative, and it is only knowable at the print.** When nights growth accelerated versus the prior quarter, the day-1 excess return was positive 17 of 21 times by sign (binomial p = 0.007; mean +3.2% on acceleration, -2.7% on deceleration). Cross it with the margin guide: margin met and nights accelerating averaged +5.0% (7 prints, 86% positive); margin met and nights decelerating averaged -2.1% (11 prints, 18% positive). This is a reaction-function fact for the prediction card, not a pre-print trade.
3. **One mechanism is genuinely forecastable and nobody uses it: the FX contribution to ADR.** The trade-weighted dollar's y/y change explains the reported-minus-ex-FX ADR gap with r = -0.95 (n = 14, permutation p 0.001) and cuts the leave-one-out error to 0.8 points from 2.1. It is daily and available before every print. For Q3 2026 it implies the FX lift to ADR falls to about +0.8 points from +1.3 in Q2 and +5.0 in Q1, so reported ADR growth converges on the 3% to 4% ex-FX run rate on 5 November. That is a specific, falsifiable card item.
4. **Hotel RevPAR is the only peer signal, and only as a sanity check.** Hilton and Marriott system-wide RevPAR y/y correlate 0.88 and 0.91 with Airbnb nights y/y over 2023 to 2026 and beat a naive nowcast leave-one-out (error 1.2 points versus 1.9). But since 2024 Airbnb's own recent growth beats every peer model, and adding a peer to an AR(1) made it worse in 10 of 11 cases. Hilton (about 21 October) and Marriott (about 3 November) arrive before the print; Booking's and Expedia's usually do not.
5. **Margins are more forecastable than the stock.** A model of same-quarter-prior-year margin plus ADR ex-FX and S&M deleverage has a leave-one-out error of 2.0 points against 2.8 for the guide bound and 2.9 for prior-year margin; all the gain is the S&M term and it needs the print's S&M growth, so it is a nowcast, not a forecast. With lagged inputs only, error equals the guide's. Floors were beaten 4 of 4 by 1.3 to 6.3 points; ceilings undershot 8 of 9 by 0.5 to 2.5 points. Q3 2026 nowcast 49.1% to 49.8% against a 50.1% ceiling.
6. **One pre-print hypothesis survives, with a health warning.** Prior-quarter S&M cash deleverage predicts the next print's day-1 excess return with r = +0.59 (n = 17, permutation p 0.014, leave-one-out R-squared 0.24, stable from 2023). Heavier marketing ahead of a print was followed by a better reaction, consistent with "investment front-runs revenue". It is one hit in about 60 tests and the sign was not pre-specified; treat it as a hypothesis to pre-register for 5 November (the Q2 2026 reading implies a mild positive tilt) and score, not to trade.
7. **The macro and alt-data nowcasts are dead ends as held.** Every nights-level correlation with BEA or CPI series is a 2023 normalization trend (BEA hotels spending r = 0.88 over 2023 to 2026 but 0.28 from 2024; all-items CPI "predicts" nights equally well). Inside Airbnb like-for-like prices show r = 0.07 against ADR and the source stopped publishing prices in late 2025. Common Crawl review velocity is a supply-quality series, not demand. Booking-curve snapshots are a one-date seasonality ranking until monthly captures exist.
8. **Where the crowd has been wrong is where the pitch should live.** Of 26 scoreable prior calls, longs were right on direction 17 of 18 times but beat QQQ only 11 of 18; all 7 holds were wrong; calls built on nights acceleration and product catalysts beat QQQ by 25 points on average and produced the only targets hit in-year; calls built on take-rate expansion were wrong on the KPI and unpunished. Thirteen metrics our data now carries were used by nobody: cash S&M per night, the ex-SBC stack, the guidance cushion, FCF-to-EBITDA conversion, net cash return after SBC, hotel price versus ADR, RNPL-adjusted unearned fees, the second derivative of nights versus guide, post-print fade, brand versus field-ops S&M, interest income inside FCF, ADR ex-FX as a margin driver, and peer read-through.

---

## 2. What was tested and what happened

| Workstream | Question | Verdict | Where |
|---|---|---|---|
| 01 Base rates | How often does ABNB beat, and what happens to the stock | Beat 19/19; top of range 15/19; 1-day excess > 0 only 11/23, 20-day mean -4.7% | `01_print_base_rates*.csv` |
| 02 Peer read-through | Do BKNG, EXPE, MAR, HLT prints predict ABNB's | Hotel RevPAR tracks nights (r 0.88 to 0.91) but does not beat ABNB's own trend since 2024; OTAs no; calendar blocks half the pairs | `02_peer_*.csv` |
| 03 Macro and alt data | Do 25 macro series or our alt-data panels nowcast KPIs | Only FX to ADR survives; nights-level hits are the 2023 trend; alt data has no demand signal | `03_nowcast_results.csv` (900 pairs) |
| 04 Reaction and margins | What explains day-1 moves; are margin surprises predictable | Nights acceleration sign 17/21; nothing pre-print except the S&M hypothesis; margin nowcast beats the guide only with print-day inputs | `04_reaction_results.csv`, `04_margin_predictability.csv` |
| 05 Pitch scorecard | What did prior pitches lean on and how did they do | Nights-catalyst framings won; holds and take-rate bulls lost; 13 unused metrics | `05_pitch_scorecard.csv`, `05_metric_usage.csv` |

Multiple comparisons, study-wide: 03 alone ran 890 pairs and 5 pass Bonferroni (3 FX mechanism, 2 nights trend); 04 ran 63 reaction tests per sample and none passes; 02 reports 255 cells and only the hotel-RevPAR pairs survive Benjamini-Hochberg in the post-2022 window. Full-sample correlations across all workstreams are dominated by 2021 base effects (nights +197% in Q2 2021) and are not quoted here.

---

## 3. What this means for the pitch

**Stop looking for a print trade.** The evidence says the revenue guide plus the trailing cushion (mean absolute error 1.1%) is the best revenue forecast available, the margin guide bound is within 2.8 points, and the stock's reaction is set by the second derivative of nights and the margin guide read together, neither of which is knowable early. The 20-day post-print excess return averages -4.7%, so even a right call on the print has faded.

**Build the variant perception on the metrics nobody prices.**

- The equity story is per-share, not margin: FCF up 36% and FCF per share up 48% over 2022 to 2025, with SBC at 13% of revenue absorbing a third of FCF. Nobody in the pitch set modelled net cash return after SBC.
- Cash S&M per night is up 29% in two years against revenue per night up 11%, and management says the reinvestment is deliberate. The bull case is what happens when it stops; the bear case is that it does not.
- Take rate is flat and guided flat, the take-rate-expansion bulls have been wrong for three years without penalty, and the 2027 view should not lean on it.
- The FX tailwind that lifted 2026 ADR is fading on a knowable schedule; the ex-FX ADR run rate (3% to 4%) and hotel price re-acceleration (CPI lodging +2.8% in July after +4.4% to +5.0% in April to June) decide whether revenue per night keeps funding margin.

**Use the card, not a forecast model, for 5 November.** The framework note's eight-question template carries base-rate priors; the items with real information are: ADR FX contribution near +0.8 points (mechanical), Q3 margin 49.1% to 49.8% versus the 50.1% ceiling (nowcast), Hilton and Marriott RevPAR as the nights sanity check, nights acceleration versus Q2's 10% as the reaction driver, and the S&M-deleverage hypothesis scored as a pre-registered test.

---

## 4. Pre-print checklist for 5 November 2026

| When | Item | Source | What it tells us |
|---|---|---|---|
| Daily | Trade-weighted dollar y/y, EUR/USD y/y | FRED DTWEXBGS, DEXUSEU | FX contribution to ADR (fitted: 0.5 - 0.72 x USD y/y) |
| Mid-month | CPI lodging away from home y/y | FRED CUSR0000SEHB | Whether hotel pricing keeps running ahead of ABNB ADR |
| About 21 Oct | Hilton system-wide RevPAR y/y | HLT 8-K Ex. 99.1 | Directional check on Q3 nights (r 0.88) |
| About 28 Oct | Booking room nights, Q4 room-nights guide | BKNG 8-K | Context only; no read-through to ABNB nights |
| About 3 Nov | Marriott worldwide RevPAR y/y and acceleration | MAR 8-K | Second directional check (r 0.91; acceleration r 0.77) |
| 5 Nov | Nights y/y versus 10% (acceleration sign), margin versus 50.1%, S&M cash growth versus +30% 1H, FY floor action | ABNB letter | Reaction function: accel plus margin met has averaged +5.0% |

---

## 5. Build forward, because the tests that matter do not exist yet

- Monthly same-market captures of the Inside Airbnb booking curves (forward blocked rates), so a series exists by the pitch; the June to August 2026 snapshots are a seasonality ranking only.
- A fixed 13-city Inside Airbnb panel for review-count growth against nights; the current panel's city mix changes every quarter.
- Point-in-time consensus at each call (Bloomberg terminal, plan-of-attack branch 3). Without it, "beat versus consensus" cannot be tested and the reaction function stays under-specified.
- Options-implied move captured the week of each print (crossover options ledger), to test whether realized moves systematically exceed implied.
- Score the 5 November card and the S&M-deleverage hypothesis, then re-run 04 with n = 23.

---

## 6. Caveats that apply to everything above

- n is 14 to 23 depending on the test; no reaction result meets a Bonferroni threshold; the study reports what survives leave-one-out against naive baselines, which is a weaker standard than a held-out period.
- Full-year margin guides are keyed to Q4 in Theo's schema; ceiling guides equal prior-year margins, so "versus bound" and "y/y" surprises coincide for those quarters.
- 2020 KPIs and Q4 2020 EBITDA in the base-rate table are hand-entered from the letters; annual FX impacts were applied to quarters in the margin model.
- Peer releases were parsed from 8-K exhibits with every extracted sentence logged in `02_peer_sources.csv`; Expedia's 2021 "room nights" are stayed-night growth as then disclosed.
- Pitch scoring: 26 scoreable calls, 6 finished horizons, 22 of 37 rows dated 2026 in a stock up 44%; directions inferred for a handful of sell-side ratings.
