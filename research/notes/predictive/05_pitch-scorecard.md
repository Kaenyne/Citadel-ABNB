# ABNB pitch scorecard: what earlier pitches predicted, which metrics they leaned on, and how the calls did

- **Sources:** `research/notes/2026-09-04_abnb-pitch-landscape.md` and `2026-09-04_abnb-pitch-catalogue.md` (the 30-plus pitches, their KPIs, methods and links); `research/sources/README.md` S5 to S13; `research/airbnb_earnings_call_study.md` sections 3.1, 5 and 8 and `research/notes/2026-09-05_margin-drivers.md` (the outcome record: nights, ADR, take rate, margin, buyback, guidance); `research/notes/2026-09-05_abnb-major-moves.md` (41 attributed moves and the 23 print reactions); Theo's IC brief (`theos-past-research/docs/forecasting/abnb_ic_brief/brief.tex`, `generated/metrics.tex`); prices from `data/raw/prices/ABNB_daily.csv` and `QQQ_daily.csv` (yfinance adjusted closes to 2026-09-04; stooq was behind a JavaScript challenge and could not be used).
- **Files:** `data/processed/predictive/05_pitch_scorecard.csv` (37 rows) and `05_metric_usage.csv` (44 metrics, 13 of them unused), both from `analysis/src/predictive/05_pitch_scorecard.py`.
- **Date:** 2026-09-06
- **Author:** Krishang Surapaneni (compiled with Claude Code)

**How to read the scores.** Price at date is the close on or before the pitch date. Returns are close-to-close ABNB and QQQ over 3, 6 and 12 months and to 2026-09-04; excess is ABNB minus QQQ. A call is judged over its own horizon if that horizon has finished (six rows), otherwise to date and flagged provisional. Long is right if ABNB rose, short if it fell, hold if the move stayed inside plus or minus 10%. Target reached means the stock traded through the PT in the right direction inside the horizon. Call quality: 2 = direction right and target reached, 1 = direction right, 0 = wrong. Rows younger than 60 days (everything from Morgan Stanley's 30 Jul 2026 Underweight onward, 11 rows) are marked "too early" and excluded from win rates. Theo's brief is not a stock call and is not scored.

**Sample warning, up front.** 37 rows, 26 scoreable, 6 with a finished horizon. Twenty-two rows are dated 2026 and the stock is up 44% in twelve months, so "direction right" for a long is a low bar; the excess-return column is the more honest one. Directions were inferred for two rows (Morningstar fair value 26% above price; the BofA/UBS/BMO/JPM cluster from PTs below the price), three dates are approximate (post-Q2 target raises, Finn), four pieces are paywalled with no visible target, and Bernstein's 2023 bear thread and the Scribd "Sell $97.72" report have no usable date. Two fetch attempts for original pages returned 403s, so nothing beyond the two notes was read.

---

## 1. Bottom line

1. **Longs 17 of 18 right on direction, but only 11 of 18 beat QQQ; holds 0 of 7; shorts 1 of 1 (Wolf of Harcourt Street's June 2025 exit, minus 5.5% over twelve months against QQQ plus 34%).** Every long written after August 2025 (11) beat QQQ by a mean 27.6 points; every long written before August 2025 (7) lagged QQQ, by a mean 14.8 points, even though all seven are up in dollars. Entry timing around the Q1 to Q2 2025 slowdown, not the thesis, decided the excess return.
2. **The consensus was wrong on demand in mid-2025 and it cost 45 to 59 points.** The "slowing demand" case (Wolf exit at $139, Sanjiv "overvalued" at $128, the minus 8% reaction to the Q2'25 print on "H2 nights to moderate") preceded nights going 7% to 9% to 10% to 9% to 10%. From the 16 Aug 2025 close ($125) the stock is plus 45% against QQQ plus 25%; from the 23 Nov 2025 low ($114), plus 59% against plus 22%.
3. **The "valuation is full" hold cluster of January to March 2026 was the second-largest miss.** Barclays EW/$120, Truist Hold/$129, LongYield $132, Phaetrix "mid-$140s", Finance Corner $145: entry prices $128 to $139, stock now $182, excess plus 13 to plus 24 points. Barclays had the single best KPI call in the sample (2026 nights plus 9% against consensus 7.5%) and still rated Equal Weight; the right KPI with the wrong multiple discipline scored zero.
4. **Framing that leaned on product catalysts and nights acceleration did best: 6 of 7 right, mean excess plus 25.3 points, mean call quality 1.29, and the only three targets reached within a year (Morningstar $154, Wells Fargo $178, Oppenheimer $180).** Optionality pitches (Experiences, Services, "a new $1B business a year") were 7 of 8 right on direction but minus 3.4 points against QQQ, and the KPI they leaned on has not happened (management: three to five years).
5. **The take-rate bulls are wrong on the KPI and have not been punished; the take-rate skeptics are right on the KPI and have not been paid.** Eremos (14% by 2029) and Bernstein (toward 15.5%) against a take rate of 13.2% flat, LTM down 31 bps, guided flat for 2026 and a 6 to 10% host-fee test. Phaetrix and MBI called it, and Phaetrix's "watch, not buy" missed plus 36%. The stock trades on nights, not take rate: consistent with the major-moves note (all eleven 7%-plus earnings moves keyed off forward nights) and with Theo's result that guidance level carries no return information (r = 0.08, n = 16).
6. **The three most-used metrics are nights growth (16 pitches, 73% hit rate, 5 of 11 beat QQQ), Experiences/Services optionality (12, 90% direction hit rate but 3 of 10 beat QQQ and the KPI did not move) and take rate (12, 56%).** The metrics with the best record are the ones the fewest people used: hotels and RNPL (8 and 7 users, 4 of 5 right and 4 of 5 beat QQQ each, mean excess plus 26 points), GBV growth and first-time bookers.
7. **Thirteen framings that our own data supports were used by nobody**: cash S&M per night (plus 29% in two years against revenue per night plus 11%), the ex-SBC cost stack, the revenue guidance cushion (19 of 19 quarters above the midpoint, mean plus 2.6%), FCF-to-EBITDA conversion (117% to 107%), net cash return after SBC (60% of FCF against Booking's 94%), hotel prices relative to ADR (gap closed in Q2'26), RNPL-adjusted unearned fees, the second derivative of nights against the guide, the post-print fade base rate, the brand-versus-field-ops S&M split, interest income inside FCF, ADR ex-FX as the margin driver, and peer read-through.

---

## 2. Scorecard (condensed)

Returns are to 2026-09-04 unless the row's own horizon finished (marked "12m"). Excess is against QQQ over the same window. Full columns (3/6/12-month returns, KPIs, method, outcome note) are in the CSV.

| # | Date | Author / house | Call | Price | PT | Return | Excess | Target | KPI happened | CQ |
|---|---|---|---|---|---|---|---|---|---|---|
| P01 | 2024-09-17 | Disruptive Analytics | Long | 122 | 120 | +0.9% (12m) | -24.4 | PT below price, no credit | partly | 1 |
| P02 | 2024-11-17 | Wolf of Harcourt St (bull) | Long | 133 | - | -11.2% (12m) | -33.5 | - | partly | 0 |
| P03 | 2024-11-20 | Henry Fund (U. Iowa) | Hold | 135 | 140 | -17.5% (12m) | -34.6 | touched | partly | 0 |
| P04 | 2025-01-02 | Speedwell Research (paid) | Long | 131 | - | +38.4% | -3.6 | - | partly | 1 |
| P05 | 2025-01-21 | Summit Stocks | Long | 133 | - | +36.7% | -1.3 | - | partly | 1 |
| P06 | 2025-02-19 | Byte Alchemist | Long | 158 | 239 (10y) | +15.2% | -19.1 | not yet | partly | 1 |
| P07 | 2025-02-26 | Eremos Notes | Long | 144 | 350 (5y) | +26.3% | -14.4 | not yet | partly | 1 |
| P08 | 2025-05-14 | Emerging Moats | Long | 137 | - | +32.4% | -7.1 | - | no | 1 |
| P09 | 2025-06-09 | Wolf of Harcourt St (exit) | Short | 139 | - | -5.5% (12m) | -39.5 | - | no | 1 |
| P10 | 2025-08-16 | Compounding Your Wealth | Long | 125 | - | +47.1% (12m) | +19.9 | - | yes | 1 |
| P11 | 2025-08-25 | Sanjiv | Hold (bear) | 128 | 117 | +48.7% (12m) | +23.4 | touched | no | 0 |
| P12 | 2025-11-11 | Morningstar | Long | 123 | 154 | +48.5% | +32.4 | yes | yes | 2 |
| P13 | 2025-11-23 | Rebound Capital (paid) | Long | 114 | - | +59.2% | +36.9 | - | partly | 1 |
| P14 | 2025-12-14 | The Finance Corner | Hold | 128 | 145 | +41.7% | +24.1 | touched | yes | 0 |
| P15 | 2025-12-27 | Motley Fool | Long | 137 | - | +33.0% | +17.5 | - | yes | 1 |
| P16 | 2026-01-09 | Barclays | Hold (EW) | 139 | 120 | +30.6% | +15.6 | touched | yes | 0 |
| P17 | 2026-02-14 | Speedwell Memos (paid) | Long | 121 | - | +49.9% | +30.2 | - | yes | 1 |
| P18 | 2026-02-25 | LongYield (bear) | Hold (bear) | 132 | 132 | +37.8% | +21.0 | touched | partly | 0 |
| P19 | 2026-03-09 | Phaetrix | Hold (bear) | 134 | 145 | +35.7% | +17.2 | touched | yes | 0 |
| P20 | 2026-03-26 | Truist | Hold | 131 | 129 | +38.8% | +13.4 | touched | partly | 0 |
| P21 | 2026-04-22 | Wells Fargo | Long | 144 | 178 | +26.2% | +16.3 | yes | yes | 2 |
| P22 | 2026-05-07 | Oppenheimer | Long | 140 | 180 | +29.5% | +26.0 | yes | yes | 2 |
| P23 | 2026-05-07 | TIKR (3 posts) | Long | 140 | 314 (2030) | +29.5% | +26.0 | not yet | partly | 1 |
| P24 | 2026-05-21 | Trefis | Long | 134 | 220 (3y) | +35.5% | +34.8 | not yet | partly | 1 |
| P25 | 2026-05-27 | Summit Stocks (ecosystem) | Long | 132 | - | +37.7% | +39.1 | - | yes | 1 |
| P26 | 2026-06-24 | High Tech Investing | Long | 144 | - | +26.0% | +24.8 | - | yes | 1 |
| P27 | 2026-07-30 | Morgan Stanley | Short (UW) | 152 | 125 | +19.6% | +14.5 | not yet | no | too early |
| P28 | 2026-08-07 | Wedbush | Long | 178 | 200 | +2.2% | +2.7 | not yet | open | too early |
| P29 | 2026-08-07 | MBI Deep Dives (paid) | Long | 178 | - | +2.2% | +2.7 | - | open | too early |
| P30 | 2026-08-07* | Susquehanna, Evercore | Long | 178 | 200 | +2.2% | +2.7 | not yet | open | too early |
| P31 | 2026-08-07* | BofA / UBS / BMO / JPM | Hold (inferred) | 178 | 160 | +2.2% | +2.7 | not yet | open | too early |
| P32 | 2026-08-08 | LongYield (constructive) | Long | 178 | - | +2.2% | +2.7 | - | open | too early |
| P33 | 2026-08-11 | Phillip Securities | Short (Reduce) | 185 | 158 | -1.6% | -1.7 | not yet | open | too early |
| P34 | 2026-08-14* | Finn scorecard | Hold | 184 | - | -1.2% | +0.5 | - | open | too early |
| P35 | 2026-08-24 | Bernstein | Long | 190 | 217 | -4.3% | -6.1 | not yet | open | too early |
| P36 | 2026-09-01 | Rosenblatt | Long | 183 | 220 | -0.3% | -1.9 | not yet | open | too early |
| P37 | 2026-09-03 | Theo IC brief | No call | 185 | - | - | - | - | n/a | not scored |

\* date approximate. "Touched" on a hold row means the price passed through the fair value at some point, which is not a win; every hold row scored 0 because the stock moved more than 10% in its window.

**Twelve-month view for the eight longs whose 12-month window has finished (Sep 2024 to Aug 2025 pitches):** mean ABNB return +1.3%, mean excess -21.8 points. The stock did nothing for twelve months after each of them and then re-rated after they had been judged. The early bulls were right and early, which in this sample was the same as being wrong against the index.

---

## 3. Metric usage

`n_used` counts all 37 rows; hit rate and beat-QQQ use the 26 scoreable rows. "Moved as assumed" is judged against the earnings-call study and the margin note. Full table with the pitch IDs per metric in `05_metric_usage.csv`.

| Metric | Used | Right / scoreable | Beat QQQ | Mean excess | What actually happened (2Q25 to 2Q26) | Moved as assumed? |
|---|---|---|---|---|---|---|
| Nights & seats growth | 16 | 8 / 11 (73%) | 5 | +5.3 | 7% -> 9% -> 10% -> 9% -> 10%; Q3'26 guide low double digits | yes for bulls, no for bears |
| Experiences / Services optionality | 12 | 9 / 10 (90%) | 3 | -0.7 | supply +80% but "not material"; 3 to 5 years out | no (not yet) |
| Take rate | 12 | 5 / 9 (56%) | 2 | +8.0 | 13.2% flat YoY; LTM -31 bps; guided flat; 6-10% host-fee test | no for bulls, yes for skeptics |
| Adj. EBITDA margin | 10 | 4 / 7 (57%) | 3 | +9.3 | FY25 35%; FY26 floor 35.5%; Q3'26 guided down slightly | neither: a flat floor |
| FCF / FCF margin | 10 | 5 / 9 (56%) | 2 | +7.0 | $4.8B TTM, 36.7% (from 44% peak); FCF/EBITDA 105% | partly |
| Hotels | 8 | 4 / 5 (80%) | 4 | +25.9 | single-digit % of nights, growing ~3x homes; conversion restated 55% -> 35% | yes on growth, unproven on economics |
| Forward P/E | 8 | 3 / 6 (50%) | 3 | +11.2 | expanded to ~31x forward; the "full" calls lost 30-40% | no |
| RNPL | 7 | 4 / 5 (80%) | 4 | +25.9 | >20% of GBV, ~70% adoption, +1 pt cancellations, laps Q3'26 | yes (level shift) |
| Buybacks / share count | 5 | 3 / 4 (75%) | 1 | -5.5 | $1.1B/qtr; diluted shares -3.4% (2025), -9% since 2022 | yes, but users were early |
| GBV growth | 5 | 3 / 4 (75%) | 3 | +26.0 | +11% -> +16% -> +19% -> +16%, ~3 pts FX | yes |
| Revenue growth | 5 | 3 / 5 (60%) | 2 | +18.9 | +13% -> +18% -> +17% | no for the bear (Sanjiv) |
| AI as cost lever | 4 | 2 / 3 (67%) | 2 | +22.0 | support cost/booking -16%; ~45% self-resolved | yes |
| EV/EBITDA | 4 | 1 / 3 (33%) | 1 | +20.1 | definitions differ by ten turns (guest float); re-rated anyway | mixed |
| Relative multiple (BKNG/EXPE or MAR/HLT) | 4 | 2 / 2 | 2 | +30.4 | vs hotels: re-rating happened; vs OTAs: premium widened | framing decides the answer |
| App share of nights | 3 | 2 / 2 | 2 | +27.7 | 59% -> 64% | yes |
| EPS growth | 3 | 1 / 2 | 1 | +19.7 | 2026 EPS raised twice | yes so far |
| First-time bookers | 2 | 1 / 1 | 1 | +17.5 | +10%, +11%, best in four years | yes |
| SBC-adjusted FCF | 2 | 1 / 2 | 1 | +30.0 | SBC 13% of revenue, unchanged; stock ignored it | yes on KPI, no on price |
| Listings growth / occupancy | 2 | 1 / 2 | 1 | +15.3 | supply disclosure dropped 2024; nights accelerated anyway | no |
| Regulation | 2 | 1 / 2 | 0 | +8.7 | spreading, no city >2% of revenue, no KPI impact | event yes, impact no |
| S&M intensity | 2 | 1 / 1 | 0 | -14.4 | S&M +27% vs revenue +17%; field ops & policy +43% in 2025 | yes |
| ADR | 2 | 1 / 1 | 1 | -5.4 | -1% (1Q25) -> +9% (1Q26) -> +5%; ex-FX +4% | no for the bear |
| Operating income | 2 | 2 / 2 | 2 | +23.8 | on track (+15% 2026) | yes |
| Regional mix | 2 | 0 / 1 | 0 | +15.3 | expansion 2x core; core moved to HSD in 2Q26 | yes for bulls, no for bears |
| Gross margin | 2 | too early | - | - | 82.5%, flat | flat |
| AI disintermediation | 1 | 1 / 1 | 1 | +30.2 | 3 Feb 2026 -7% (BKNG -9%, EXPE -15%); faded | not so far |
| Product-dev spend / ROI | 1 | 0 / 1 | 0 | +24.1 | cash product dev flat at 10-11% of revenue; the creep is SBC | partly |
| Unpaid traffic share | 1 | 1 / 1 | 0 | -3.6 | still ~90% | yes |
| Support cost per booking | 1 | too early | - | - | -16% | yes |
| Raw guidance change (Theo) | 1 | not a call | - | - | r = 0.08 with excess return, n = 16; direction aligned 7 of 19 | no signal |
| Macro / travel-activity composite (Theo) | 1 | not a call | - | - | r = 0.78 with guidance level, -0.63 with acceleration; 0 strict-PIT rows | level yes, change no |
| **Cash S&M per night (ex-SBC)** | **0** | | | | $4.21 (2Q24) -> $4.75 -> $5.45 (2Q26): +29% vs revenue/night +11% | unused |
| **Ex-SBC cash cost stack** | **0** | | | | 2022-25 revenue/night added 5.1 margin pts, S&M took back 4.2; product dev flat | unused |
| **Revenue guidance cushion** | **0** | | | | 19 of 19 quarters above midpoint, mean +2.6%; range width 6% -> 1.6% | unused |
| **FCF-to-EBITDA conversion** | **0** | | | | 117% (FY22) -> 107% (FY25) -> 105% TTM; float off, full tax, interest falling | unused |
| **Net cash return after SBC** | **0** | | | | ABNB 60% of FCF (2023-25) vs BKNG 94%; $1.4B buyback per 1% share cut | unused |
| **Hotel price vs ADR** | **0** | | | | ADR +9.0% vs hotels -2.2% (1Q26); +5.3% vs +4.9% (2Q26): gap closed | unused |
| **Unearned fees adjusted for RNPL** | **0** | | | | flat at $2.83B with GBV +16%; next-quarter coverage 88% -> 76% | unused |
| **Second derivative of nights vs guide** | **0** | | | | all eleven 7%+ print moves keyed off forward nights; six were on beats | unused (Barclays closest) |
| **Post-print fade base rate** | **0** | | | | every 7%+ up day before Q2'26 was given back in 20 sessions; Q2'26 first exception | unused |
| **Brand vs field-ops S&M split** | **0** | | | | brand +10% vs field ops & policy +43% ($993M) in 2025 | unused |
| **Interest income inside FCF** | **0** | | | | 5.2% of revenue TTM (7.4% peak), falling with rates | unused (Summit mentioned it) |
| **ADR ex-FX as margin driver** | **0** | | | | +1 pt ADR ex-FX ~ +0.5 pt margin; tailwind was Airbnb-specific | unused (MBI tracks NA only) |
| **Peer read-through** | **0** | | | | one peer-driven 7% day in six years (3 Feb 2026) | unused |

---

## 4. Where the consensus narrative was wrong

**4.1 The 2024 to mid-2025 "slowing demand" bear (largest price consequence).** The Q2'24 print (-13.4%, "shorter lead times, slowing US demand"), Q3'24 (-8.7% on spend), the Q1'25 trough (nights +8%, ADR -1%) and the Q2'25 print (-8.0% on "H2 nights to moderate") built a consensus that Airbnb was an ex-growth OTA. Wolf of Harcourt Street sold at $139 in June 2025 on exactly those KPIs; Sanjiv called it "slightly overvalued" at $128 in August 2025 because growth (12.7%) was below the five-year CAGR; the Street mean PT was still $149 to $157 in May 2026. Nights then accelerated for five straight quarters and first-time bookers hit an eleven-year high. From 16 Aug 2025 the stock is +45% (QQQ +25%); from the Nov 2025 low, +59% (QQQ +22%). The bear KPIs were real for two quarters and wrong for the next five. The Q4'24 print (+14.4% on 111M nights against 108.7M) had already signalled the pattern a year earlier, and the same reacceleration-after-a-trough happened in Q3'24; the crowd extrapolated the trough both times.

**4.2 The "valuation is full" hold cluster, January to March 2026 (second-largest).** Barclays (EW, $120, 20x FY27 EPS), Truist (Hold, $129, 20x 2027 EBITDA), LongYield ($132 base, 26x trailing EBITDA), Phaetrix (mid-$140s, tripwire $110), Finance Corner ($145 DCF). Entry $128 to $139; stock $182; excess +13 to +24 points. Common structure: a correct or nearly correct operating view (Barclays had nights +9%; LongYield had SBC and FCF conversion right; Phaetrix had the take rate right) capped by a multiple anchored to Booking or to Airbnb's own two-year P/E band. The multiple went to ~31x forward instead. Lesson for our deck: when the KPI call is differentiated, do not let a peer multiple neutralise it; the $125 to $220 PT dispersion is a multiple debate on a consensual growth path, and the multiple has followed nights every time.

**4.3 The AI-disintermediation bear (3 Feb 2026).** Hotel chains signing Google/Anthropic/ChatGPT booking deals took ABNB -7%, BKNG -9%, EXPE -15%. Speedwell flagged agentic-web bypass of cross-listed PMS inventory as the main risk eleven days later. From the 14 Feb close ($121) the stock is +50% (QQQ +20%). ABNB fell half as much as the OTAs and the Third Bridge calls put AI-native booking share at ~3% with no EBITDA impact. The scare was a one-day repricing, not a trend; it produced the best entry point of 2026.

**4.4 The take-rate-expansion bull (no price consequence yet, but the KPI is wrong).** Eremos modelled 14% by 2029 and Bernstein still models a lift toward 15.5% from the single fee. The actual path: 13.5% LTM (2Q25) to 13.2% (2Q26), guidance moved from "modest upside" (May) to "flat" (Aug), and a 6 to 10% host-fee pilot appeared on 29 Aug. The bulls have not been punished because the stock trades on nights and GBV (section 8.4 of the earnings-call study, and every 7%+ print move in the moves note). This is the consensus error that has not been priced, which makes it the one worth building a differentiated 2027 view around.

**4.5 The Experiences/Services optionality bull.** Twelve pitches leaned on it; nine were right on direction because the stock rose; three beat QQQ. The KPI has not moved (management: "3 to 5 years to materiality"), and the conversion story that did work was hotels-to-homes, which almost none of the 2024 to early-2025 optionality pitches named. Being right for the wrong reason is not a repeatable edge.

**4.6 The supply and regulation bear.** Morgan Stanley's listings deceleration (12% to ~7%) and LongYield's host-occupancy decline (57% to 50%) were both followed by a nights acceleration. Airbnb stopped disclosing supply in 2024, so the thesis is unfalsifiable from public data; the regulation events (NYC LL18, Barcelona 2028, Paris, Amsterdam, Spain's 86k delistings) all happened and none is visible in the KPI table. Morgan Stanley's 30 Jul 2026 Underweight is too young to score but is +19.6% against.

---

## 5. What framings were predictive

| Framing | Scoreable | Right | Mean excess | Mean CQ | Read |
|---|---|---|---|---|---|
| Nights acceleration / product catalysts (RNPL, hotels, first-timers, GBV) | 7 | 6 | +25.3 | 1.29 | Best. Three of the four targets reached in-sample (Morningstar, Wells, Oppenheimer). Barclays is the one miss and it was a rating problem, not a KPI problem. |
| Buyback / capital return | 1 | 1 | +19.9 | 1.00 | Compounding Your Wealth bought the Q2'25 drop citing the $6B authorisation. Buyback users overall (5) were -5.5 excess because three of them were 2024 to early-2025 entries; buyback math did not time anything. |
| Valuation multiple / fair value | 5 | 2 | +12.7 | 0.40 | The two rights were longs using a relative-to-hotels multiple (Trefis, TIKR). All holds anchored to Booking or history were wrong. |
| Optionality / new businesses | 8 | 7 | -3.4 | 0.88 | Direction right, index lagged, KPI absent. |
| Take-rate expansion bull | 1 | 1 | -14.4 | 1.00 | Eremos: right on "market too conservative", wrong on the take-rate and margin path, lagged QQQ. |
| Take-rate skeptic | 1 | 0 | +17.2 | 0 | Phaetrix: right KPI, wrong stock. MBI (Aug 2026) too early. |
| Quality of cash / SBC / margin | 1 | 0 | +21.0 | 0 | LongYield: SBC 13% and FCF conversion were right; demand overwhelmed it. |
| Slowing-demand bear | 2 | 1 | -8.1 | 0.50 | Wolf's exit scored over 12 months (-5.5%) but the stock was +31% from his exit price two months after the window closed. |

Three specific observations:

- **Did pitches that focused on nights acceleration do better?** Yes, and it is the only framing whose KPI both happened and was rewarded. The mechanism is in the moves note: the stock reprices on forward nights against the guide, so the pitches that forecast the second derivative (Barclays' 9% versus 7.5%, Motley Fool's first-time bookers, Wells' hotels/RNPL inflection) had the causal variable. Nobody in the sample built the framing as a formal "nights versus guide versus consensus" surprise, which Theo's brief argues is the correct object and which no pitch used.
- **Did margin floors help?** Nobody used the floor as a bull argument. The skeptics who read margin (Wolf: op margin 5% to 2%; Finn: OCF flat) were wrong on the stock because the FY floor has been beaten by 60 to 180 bps every year and raised twice in 2026. The floor-plus-revenue-cushion framing (19 of 19 quarters above the guided midpoint) would have predicted every 2025 to 2026 guide raise and no one used it.
- **Did buyback math help?** Not on its own. The share count fell 9% since 2022 through every regime, so it explains none of the timing. It matters for the model (EPS CAGR ~20% needs the buyback) but not for the call.
- **Did KPI accuracy translate to call accuracy?** Rows whose named KPI happened: 8 of 11 right, mean excess +23.9. KPI partly: 8 of 12, +0.1. KPI did not happen: 2 of 3 right (both by luck: Wolf's exit window, Emerging Moats' stock rising on unrelated drivers), -7.7. Getting the KPI right roughly doubled the excess return, but a right KPI paired with a valuation-capped rating (Barclays, Phaetrix, LongYield) scored zero. The KPI is necessary, not sufficient.

---

## 6. Framings nobody used that our data supports

1. **Cash S&M per night, ex-SBC.** $4.21 (2Q24) to $5.45 (2Q26), +29% while revenue per night rose 11%. Every S&M debate in the pitches was "S&M +27% versus revenue +17%"; none put it on a per-night basis, which is what shows the reacceleration is partly bought. (`data/processed/abnb_quarterly_cost_stack_exsbc.csv`.)
2. **Brand versus field-ops S&M.** Brand and performance marketing grew 10% in 2025; field operations and policy (supply acquisition for hotels, services, experiences, expansion markets) grew 43% to $993M. The "90% unpaid traffic" line that every bull repeats is intact because the money is going into supply, not ads. No pitch made that distinction.
3. **The revenue guidance cushion.** 19 of 19 guided quarters beat the midpoint, mean +2.6%, 15 of 19 above the top of the range; the cushion narrowed from 2.7% (2022) to 1.8% (2026) as the range narrowed to 1.6%. Applied to Q3'26 it puts revenue near $4.82B, +18%. A print below the midpoint would be the first ever. This is a forecastable catalyst variable and nobody used it.
4. **FCF-to-Adjusted-EBITDA conversion.** 117% (FY22) to 107% (FY25) to 105% TTM: the float stopped growing under RNPL, the tax provision went from 1% to 5% of revenue, interest income (5.2% of revenue) is falling. Ten pitches used FCF margin; two adjusted for SBC; none decomposed why the FCF margin fell 7.5 points while EBITDA margin moved half a point.
5. **Net cash return after SBC.** Buybacks minus SBC were 60% of FCF cumulatively 2023 to 2025 versus Booking's 94%; it takes $1.4B of buyback to cut the count 1%. Five pitches cited buybacks; none netted the SBC they fund.
6. **Hotel price inflation relative to ADR.** ABNB's ADR ran 5 to 6 points above US hotel prices from Q2'25 to Q1'26 (an Airbnb-specific pricing tailwind that funded the margin raises); in Q2'26 hotels priced +4.9% against ADR +5.3% and the gap closed. Two analysts asked about it on the Q2 call; no pitch modelled it. It is the cleanest leading indicator for whether Q3'26 revenue growth rests on nights alone.
7. **Unearned fees adjusted for RNPL.** Flat YoY at $2.83B with GBV +16%; coverage of next-quarter revenue fell from 88% to 76%. The reported backlog understates booked business, which is bullish for near-term revenue and bearish for the "FCF is clean" story at the same time. Finn's scorecard was the only piece to mention RNPL cash timing.
8. **Second derivative of nights against the guide, and the post-print fade base rate.** All eleven 7%+ earnings moves since 2021 keyed off forward nights, six of them on revenue and EPS beats; mean 20-session excess after a print is -4.7% and every 7%+ up day before Q2'26 was given back within a month. No pitch framed its catalyst calendar this way; Theo's brief describes the object (a joint actual/guide surprise vector) but has zero point-in-time rows to test it.
9. **ADR ex-FX as the margin driver.** +1 point of ADR ex-FX is worth ~0.5 point of margin, and the 2025 to 2026 ADR tailwind (~3 points FX) is the least controllable input. MBI tracks North America ADR ex-FX; no one used it as the margin swing.
10. **Peer read-through.** One peer-driven 7% day in six years (3 Feb 2026); Booking's prints never moved ABNB 7%. The bear pitches that lean on Booking's multiple are borrowing a comparison the market does not trade.

**What this means for our pitch.** The framings with a record are nights acceleration read against the guide and product catalysts (hotels, RNPL, first-timers). The framings with unused evidence are the cost stack per night, the guidance cushion, the FCF bridge and the hotel-price gap. A long should be built on the first set with the second set as the falsifiers; a short should not repeat the valuation-only or supply structures that have scored zero, and should instead be built on the KPI the bulls have wrong (take rate) plus the one they have not looked at (cash S&M per night), with the RNPL lap (US from Q3'26) as the timing.

---

## 7. Caveats, repeated

- 26 scoreable calls, 6 finished horizons, 11 too early. Nothing here is statistically significant; it is a record, not a backtest.
- Direction hit rates are inflated by a stock up 44% in twelve months. Read the excess-return column first.
- "Hold right" uses a plus or minus 10% band; a wider band would flip some 2024 holds but none of the 2026 ones.
- Target reached on hold rows means touched, not achieved as an outcome.
- KPI tags were assigned from the two catalogue notes, not from re-reading originals; four pieces are paywalled and their targets are unknown; Morningstar's direction and the BofA/UBS/BMO/JPM cluster's direction are inferred from fair value against price.
- The QQQ benchmark is a growth index, not a travel index; against BKNG or a travel basket the excess returns of 2026 longs would be smaller. `data/raw/prices/` also holds BKNG, EXPE, MAR and HLT closes if the team wants that comparison.
