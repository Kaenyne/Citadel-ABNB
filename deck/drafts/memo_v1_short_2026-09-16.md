# Airbnb (NASDAQ: ABNB) — SHORT: a product-bundle lap priced as demand

Draft v1, 16 Sep 2026. Krish with Claude (Fable 5.1). Format follows the team's one-pagers in the Community Repo (Murata, ASMPT, TXN) and Luca Cifolelli's CAKE short. Every number names its source note; nothing on the AGENT_BRIEF §6 / margin-build §9 kill lists is used. Price is the 16 Sep close.

**Price (16 Sep 2026): $167.51 | Mkt cap: ~$100bn (597m diluted) | Net cash ex-float: $9.6bn | EV/FY27E adj. EBITDA: 15.7x Street, 19.0x our short case | PT (12M, prob.-weighted): $158, base $155, short case $140 | SI: 3.4% of float, 2.6 days to cover, bottom decile of its own history | Horizon: 5 Nov 2026 print to Feb 2027 guide (3–6 months)**

**Recommendation:** SHORT ABNB, hedged against QQQ, sized 1–2% of notional and underwritten to a +17% day. The stock is priced for an accelerating 3Q26 nights print and a FY27 in which 2026's growth rate simply repeats. Our work says 2026's re-acceleration was a dated product bundle (Reserve Now Pay Later, the cancellation redesign, the single-fee migration) plus a 3-point FX tailwind and a World Cup booking pull-forward, all of which anniversary between 3Q26 and 2Q27, while the cost base management has budgeted for does not flex down. The first visible test is 5 Nov: a decelerating nights print against a Street bar that assumes acceleration, and a 4Q26 guide below the Street.

## What the market is underwriting, and where we differ

At $167.51 the price pays for FY27 revenue growth of +10.4% to +11.5% and nights growth of +8% to +9% at about 16x FY27 EBITDA (joint solve, `2026-09-13_market-implied-model.md` §3). That is the Street's number and, on revenue, close to our own base. The disagreement is not the FY27 level; it is (1) the 3Q26 nights print, (2) the shape of FY27, and (3) what happens to margins when revenue growth halves on a cost base built for it. **On 3Q26 nights the Street's bar is 148.9m (+11.45% vs 2Q26's +10.3%), all 28 Bloomberg estimates sit at or above the 2Q26 rate, and our nowcast is 146.8m (+9.9%, band 8.5–11.0), below the lowest estimate.** The bar is an acceleration for only the fourth time in 16 prints, and it is management's guide ("low double digits") carried forward one-for-one after the 2Q26 beat (positioning card, market note §10).

## Thesis

**1. The 2026 nights re-acceleration is a lap, not demand, and our alternative data says it has already stopped.** North America ran +2%/+2% in 1H25, stepped to +5% when RNPL launched (3Q25) and +8% with all three features live (1Q26); management itself attributed "over 200bp" (4Q25) then "approximately 3 points" (1Q26) of nights growth to the bundle, and gave no figure in 2Q26 (RNPL ledger D014/D032/D043). The legs anniversary on sourced dates: US RNPL from 3Q26, the global cancellation and fee legs from 4Q26, ex-NA RNPL from 1Q27 (partial) and 2Q27 (full). The World Cup adds a 2Q26 booking comp on top (`overnight/05` §4.6). The review-date stays index across 123 Inside Airbnb markets, the first team series to beat a naive nights forecast out of sample (walk-forward RMSE ratio 0.68), reads 3Q26 at +9.5% to +10.0%; the external stack (hotel RevPAR, NTTO inbound arrivals) reads +9.2%; same-listing review volume is −3% to −7% y/y with all growth from listings under a year old (`docs/q3nowcast/SYNTHESIS.md`). Nothing measured points to the +10.6% or more the Street needs to call it an acceleration.

**2. FY27 will look worse than FY27 demand, and the Street has not phased it.** The Street runs FY27 at a flat ~+11% every quarter. Our kernel puts 1Q27 at +9.4% to +11.6% against a +17.9% comp and 2Q27 at +10.7% against +16.5% (`03_insider_mechanics.md` §5.5; RNPL audit §3.6), the first sub-teens quarterly guide since 2023. Three arithmetic pieces sit inside that and are all knowable today: revenue FX runs +3.0pp in 3Q26 to about +1.0pp in 4Q26 and −0.6pp in FY27 (bridge v3, kernel path); the bundle lap is worth −1.1 to −3.2 points of FY27 nights against the Street on the RNPL module (FY27 nights +6.4% global lap / +8.2% NA-only, vs the +8–9% the price carries); and the 2Q26 World Cup bookings lap in 2Q27. The multiple pays +0.40 to +0.48 EV/EBITDA turns per point of forward growth, so two to three points off FY27 growth is roughly one turn, $9–13 a share, before any estimate cut.

**3. The cost base is budgeted for the growth that is lapping, and management cuts less readily than it spends.** Built from the 10-Q component disclosures alone, 3Q26 costs grow 11.5% and the quarter prints 52.4%; management's "margin down slightly vs Q3 2025" sentence means it has chosen to spend about $97M more, in brand marketing and AI hosting (`40_line_build.md`). S&M has gone from 19.4% of revenue (FY25) to 21.3% (FY26E) to 21.9–23.5% (FY27E) depending on build; the Street's FY27 margin of 36.5% implies a 43.7% incremental margin that requires the ramp to stop, against our 24.7–34.8%. Total cash-cost elasticity to revenue is 0.36 and asymmetric (k_down < k_up at p < 0.02), so a revenue miss costs 0.35–0.6pp of FY27 margin per point of revenue, and the FY26 "at least 35.5%" floor breaks on a 2H26 revenue shortfall of only 0.6–0.9% ($50–75M). Adjusted EBITDA also excludes $1.8bn of FY26 SBC (35% of EBITDA); on SBC-adjusted FCF the stock yields ~3% and the price requires 16% FCF growth on a reverse DCF (market note §3).

## Estimates vs consensus

| | Street (LSEG 11 Sep / BBG) | Team base (line build, bridge v3) | Short case (40_line_build §8b) | Short vs Street |
|---|---|---|---|---|
| 3Q26 nights | 148.9m, +11.5% | 146.8m, +9.9% | 145.0m, +8.5% | −2.6% |
| 3Q26 revenue | $4,744M | $4,804M | $4,681M | −1.3% |
| 3Q26 adj. EBITDA / margin | $2,362M / 49.8% | $2,420M / 50.4% | $2,290M / 48.9% | −$72M |
| 3Q26 EPS | $2.85 | $2.91 | $2.71 | −5% |
| 4Q26 revenue (guide mid implied) | $3,157–3,162M | $3,178M ($3,059M) | $2,966M | −6% |
| 4Q26 adj. EBITDA / margin | $914M / 28.9% | $899M / 28.3% | $700M / 23.6% (at budget); $876M / 29.6% with a $177M marketing cut | −$214M / −$38M |
| FY26 adj. EBITDA margin | 35.6% (floor 35.5%) | 35.7% | 34.2% at budget; 35.5% with the cut | floor at risk |
| FY27 revenue | $15.8bn, +11% | $15.8bn, +10.9% | $14.9bn, +4.5% | −6% |
| FY27 adj. EBITDA / margin | $5,766M / 36.5% | $5,644M / 35.7% | $4,761M / 31.9% | −$1.0bn |
| FY27 EPS | $6.23 | $5.93 | $4.58 | −26% |

The run's top-down margin combination (backtested, 0.47x the Street's h=0 dollar error, better in 14 of 14 quarters) gives 3Q26 $2,399M / 49.9% and FY27 $5,483M / 34.6%; the line build above is the composition view. Both agree on 2026 and disagree with the Street on 2027, entirely in S&M.

## Scenarios (12 months; joint-solve prices, fixed-multiple cross-check in brackets)

| | Thesis breaker (stock up) | Base | Short case ("bonus") |
|---|---|---|---|
| Probability | 25% | 45% | 30% |
| 3Q26 nights / 4Q26 guide | ≥10.6%, "low double digits" reiterated, bundle figure ≥2.5pt restated, FY sentence "approximately 36%" | 9.5–10.0%, "high single digit" or guide $3.05–3.10bn vs Street $3.16bn | ≤8.5%, guide implies ≤7.5%, no bundle figure |
| FY27 revenue growth / margin | +12.6% / 36.2% (management delivered) | +8–9.5% / 34.6–35.7% | +4.5% / 31.9% |
| 5 Nov day-1 precedent | accelerating print: +6.0% mean, n 5 (4Q24 +14.4%, 2Q26 +17.4%) | Q4 guide below Street **and** nights guided lower: −8.0% mean, −10.9% median, n 5 (3Q22 −13.4, 1Q23 −10.9, 2Q24 −13.4, 3Q23 −3.3, 1Q25 +1.0); 20-day excess after decelerating prints −8.0% | same, plus the FY26 floor at risk and no bundle figure |
| Price | $180–190 ($176 at 16.5x) | $145–155 (−8% to −13% on the day; joint solve $150 at ~8.6% NTM growth) | $125–140 ($140 interpolated, $148 at 16.5x; team bear $121–137) |
| Return from $167.51 | +7% to +13% | −8% to −13% | −16% to −25% |

Probability-weighted 12M price ≈ **$154 (−8%)**; at 60/25/15 on the deceleration cases it is $147 (−12%). The event is where the asymmetry is: since 2022, every print that paired a Q4-guide-below-Street with a downgraded nights direction fell on the day (median −10.9%), and the four 10%+ down days in ABNB's history were all nights-guide or lead-time events on revenue and EPS beats (`2026-09-05_abnb-major-moves.md`). The one exception in the pair, 1Q25 (+1.0%), was a "stable" nights guide missed by 0.4pt. The options market prices the print at a 9.5% sd, so the base case is a one-sigma day, not a tail.

## Catalyst path

- **13 Oct 2026** (15 Sep non-EEA): single-fee migration deadline for hosts. Migrating listings display ~15% higher on dateless search; unmodelled conversion risk in EMEA into 4Q26. Dates are from a host resource page, not a filing.
- **5 Nov 2026 (AMC): 3Q26 print.** Nights sign vs the 148.9m bar; 4Q26 nights bucket and revenue guide; FY26 margin sentence (35.5% held vs "approximately 36%"; 1pp of the FY sentence = 4.49pp of 4Q26 margin); the 10-Q S&M brand/performance split; whether the bundle-contribution figure returns; RNPL GBV share; 3Q26 stated FX integer.
- **~11 Feb 2027: 4Q26 print and 1Q27 guide.** The shape: 1Q27 guided against a +17.9% comp. Note the Q4 print has been positive on day 1 in 6 of 6 observations; size down into it.

## Risks (what moves the stock against the short) and mitigants

1. **Management delivers its nights guide, as it has in 12 of 13 guided prints.** Our call is the first downside miss of a nights guide in the sample. Mitigant: the guide was set 6 Aug with July in hand; the alt data through mid-August sits at or below 2Q26's rate; the pre-registered flip is nights ≥10.3% with a bundle figure ≥2.5pt, and we cover on it.
2. **3Q26 is a revenue and EBITDA beat on our own numbers** (revenue $60M above Street, P(EBITDA beat) 0.78; guide beaten 19 of 19 times). Mitigant: the reaction study finds no return to revenue/EPS/EBITDA surprise; the nights sign and the Q4 guide are what price. Do not pitch the beat.
3. **The July 2026 RNPL eligibility expansion is fresh treatment inside the quarter** and unquantified. Mitigant: it is the one unbounded offset; the tell is RNPL share ≥25% with nights ≥10%, and it is a cut signal, not a debate.
4. **FX and the take rate.** ±2.3 points of FY27 growth per one-sigma dollar move, larger than the whole bundle lap; the host-only fee could add 40–50bp of take rate if the replaced blended fee was 14.1%. Mitigant: revenue FX is 84% observed for 4Q26; the 3Q26 printed take rate vs 18.10% is scored as a paired flip rule.
5. **The margin sentence is conservative.** If "down slightly" is sandbagged, 3Q26 prints the evidence build (52.4%, $2,516M). Mitigant: the quarterly sentence has been missed slightly more often than beaten (above in 4 of 10 quarters); the FY floor has been beaten by 60–140bp every year, so the FY sentence, not the quarter, is the risk.
6. **No crowding, no borrow, a $3.4bn buyback and a +17.4% August print that did not fade.** Mitigant: size 1–2%, QQQ hedge (2026 beta 0.91), express through a Nov put spread if the fitted event sd prints below ~7% when the 6 Nov weekly lists (week of 26–30 Oct).

## Bonus (what would take the stock down more than the base)

- **RNPL cancellations show up in the KPI.** Cancellation drag is bounded at −0.15 to −0.93pt of 3Q26 nights on the cohort engine, but a live unpaid book above ~40m nights (IR's unbilled balance) or a propensity revision above +6pt would double it; 46–49% of any excess arrives from earlier cohorts. Tell: unearned fees y/y ≤ −3% with GBV on plan.
- **ADR pricing residual mean-reverts.** The like-for-like residual stepped from 2–3.5pp (2023–25) to 4.4–4.9pp in 1H26 and is 31% of the 3Q26 band variance; reversion puts reported ADR nearer +0.8% than +3%, worth $46M of revenue per point.
- **Fee-migration reprice in EMEA** (~15% listed-price step for the migrating cohort into the 13 Oct deadline) plus the EU short-term-rental act: both unmodelled, both 4Q26.
- **A visible 4Q26 marketing cut to hold 35.5%** ($177M, ~35% of Q4 marketing) confirms the fixed-cost mechanism rather than refuting it; Street FY27 margin needs the ramp to stop voluntarily, not under a revenue miss.

## Appendix: EPS bridge, Street FY27 $6.23 to short case $4.58

| Step | EPS | Source |
|---|---|---|
| Street FY27 | $6.23 | LSEG 11 Sep, n 44 |
| Costs at management's budget: S&M ramp continues (+15% FY27), AI hosting step, SBC/share count | −$0.30 | line build base $5.93 |
| Nights lap and deceleration: −3 pts of nights per quarter vs the team path, ADR ex-FX flat, revenue −$915M on a fixed cost base (cash costs move $32M) | −$1.27 | short case revenue path, `40_short_case_stress.csv` |
| RNPL overlays: ops & support +4% per booking, chargebacks +$0.15 per booking | −$0.08 | `40_params.csv` overlays |
| Funds held −10%: interest income −$10–19M a quarter (below EBITDA) | ≈ $0.00 net of the above rounding | M7 convention |
| **Short case FY27** | **$4.58** | `40_short_case_summary.csv` |

Appendix (page 2 of the submission): the 5 Nov pre-registered score sheet (nights ≤8.5 / ≥10.3; 4Q26 nights guide ≤7.5 / ≥9.5; bundle figure none-or-≤1.5 / ≥2.5; take rate vs 18.10% paired with GBV vs $26,608M; unearned fees y/y; stated 3Q26 FX 0/+1 vs +3), the S&M share table (19.4% → 21.3% → 21.9–23.5%), and the reviews-index survivorship correction.

---
---

## Reviewer notes for Krish (not part of the memo)

**Where the differentiation actually is.** Three things in the repo are genuinely not in a sell-side model: (a) the reviews-based stays index, the only alt series that beats naive out of sample and reads "no acceleration" for 3Q26 while every one of 28 Street estimates assumes one; (b) the phased FY27 shape (1Q27 vs +17.9%, 2Q27 vs +16.5%) with dated lap schedules for three product legs, FX and the World Cup, where the Street runs flat +11%; (c) the line-by-line cost build showing the FY27 Street margin needs the marketing ramp to stop. Everything else (the Q3 beat, the FY27 revenue level, valuation) is consensus and should not lead.

**What drives a move down on 5 Nov.** Only one print variable has a measurable reaction: the sign of nights acceleration (post-2022, n 14). The team's case is a decelerating print against an accelerating bar, which is unobserved in the sample (no print pairs an accelerating bar with a decelerating print). Revenue/EPS/EBITDA surprise has no measured reaction. So the 5 Nov leg is: nights below 10.6% (and ideally below 10.0%, outside "low double digits"), a 4Q26 nights bucket downgraded to "high single digits", and a Q4 revenue guide below the Street's $3.16bn. The FY margin sentence is a second leg only if it is held at 35.5% while the Street already needs a raise for its 4Q26 number; an unchanged floor is "absence of a raise", not a guide-down, and its price reaction is untested.

**Calibration problems you should fix before 2 Oct.**
1. The 12-month probability-weighted target is −8% at 25/45/30 and −12% at 15/25/60. The bear branch (management delivers, $180–190) is real and 12 of 13 guided prints say so, and it is what dilutes the PW number. The event math is stronger than the PW math: conditional on the thesis (decelerating print, Q4 guide below Street, nights bucket downgraded) the precedent is −8 to −13% on the day (n 5, median −10.9%) with a further −8% 20-day drift after decelerating prints. Two conditions matter for that precedent: the nights print or guide must decelerate, not just the revenue guide (4Q24 had a revenue guide below Street and rose +14.4% on a nights beat), and management will attribute ~2pp of the Q4 revenue step-down to FX, so the pitch must be argued on nights, not on the revenue guide alone.
2. The short case's FY27 nights (+2% to +5% per quarter) is a scenario, not a forecast. The RNPL-aware module supports +6.4% to +8.2% FY27. Consider re-basing the pitch's "base" to the module (FY27 revenue growth ~+8–9%) and keeping +4.5% as the bonus case. On the joint solve that base is $150–160, which is where I put it above.
3. The World Cup framing needs care: WS10 and the reconciliation note say World Cup stays were booked in 4Q25–2Q26, so 3Q26 booked nights get no lift and there is nothing to "hide" in 3Q26; the comp problem is 2Q27. Management never sized its benefit. Phrase it as a 2Q26 booking pull-forward that laps in 2Q27, not as a 1H26 disguise.
4. The team's own 3Q26 numbers are a beat on revenue and EBITDA. Judges will ask why you are short into a beat. The answer (nights sign and guide, not the level; 19 of 19 beats carry no reaction) must be on page one.
5. Two builds disagree on FY27 margin by a point (run 34.6% vs line build 35.7%, all S&M). Pick one for the memo; the line build is the composition view and the workbook default.
6. Price anchor: the market-implied note used $170.19 (11 Sep); spot is $167.51 (16 Sep). The 8–10 Sep fall took the stock from $182 to $170 without repricing the print (event sd unchanged), so part of the base case has already happened; the price-implied 4Q26 revenue is already below the Street.
7. Nothing regulatory or macro is in the thesis by design: 0 of 41 moves ≥7% have been regulatory; peer read-across is null. Keep it that way in Q&A.

**Sources read for this draft:** `docs/margin-build/MORNING_REPORT.md`, `SYNTHESIS.md`, `notes/40_line_build.md`; `docs/reverse_dcf/SYNTHESIS.md`, `research/notes/2026-09-13_market-implied-model.md`; `docs/q3nowcast/SYNTHESIS.md`; `docs/rnpl-short-audit/00_SYNTHESIS.md`, `03_short-thesis-viability.md`; `docs/overnight2/SYNTHESIS.md`; `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md`; `deck/drafts/memo_v0_2026-09-11.md`; `docs/2026-09-16_pitch-model-workbook.md`; `data/processed/margin_build/40_line_build/40_short_case_*.csv`; `data/processed/reverse_dcf/D/D_positioning_summary.csv`; yfinance close and short-interest fields, 16 Sep 2026.
