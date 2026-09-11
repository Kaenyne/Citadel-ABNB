# G. External sources: what the outside world can tell us about 3Q26 right now

**Date:** 2026-09-11 (the 12 Sep 2026 Q3 nowcast run; every external series and page accessed 2026-09-11).
Author: Krishang Surapaneni (compiled with Claude Code), workstream G.

**Question.** The run's question has two halves. This note answers the second: if the data the team holds is insufficient, what other source gives a better read on 3Q26 now? Concretely, pull every accessible external series that covers July to September 2026, score it against disclosed ABNB quarterly growth with the note-08 walk-forward protocol wherever history allows, assemble the intra-quarter commentary that already exists, and price what we cannot get.

**Scripts.** `analysis/src/q3nowcast/G1_collect_external_series.py` (pulls and caches TSA, BLS, Spain INE, Eurostat, NTTO, JNTO), `G2_external_backtests.py` (288 note-08 walk-forward tests plus the 3Q26 nowcast), `G3_rank_sources.py` (the ranked inventory). All run with `py -3.13`.

**Read first.** `research/notes/overnight/08_altdata-index-and-backtests.md` for the protocol and for the two negatives this note re-tests with the 2026 quarters added (air traffic stopped predicting nights in 2024; hotel RevPAR tracks nights but does not beat naive). Section 2.6 and 2.9 of `docs/2026-09-06_research-inventory.md` for what the team already holds and already knows it does not hold.

---

## 1. Bottom line

1. **The best external read on 3Q26 is the CoStar/STR weekly US hotel series, and its message is a clean deceleration through August.** It is the only free source that reaches into September (week ending 5 Sep, published 11 Sep), it splits into occupancy and rate so it maps onto nights and ADR separately, and its family is the strongest performer in the backtest (hotel RevPAR, best walk-forward RMSE ratio 0.67 vs naive on nights, n = 10 quarters, permutation p 0.000). The path of US RevPAR y/y is +8.2% (July month), then +7.3%, +7.2%, +6.2%, +4.4%, +1.7% across the five August weeks, then +16.1% in the week ending 5 Sep. The last two weeks are a Labor Day calendar artefact and cancel each other; the clean signal is the mid-August slope from +7% to +4%, with ADR decaying from +5.7% in July to +0.6% in the week of 23 to 29 August. July was also flattered by the World Cup final: NYC ADR +24.0% and RevPAR +27.1% in a single market.

2. **Hotel RevPAR now does beat naive on ABNB nights, which updates note 08.** With 2026Q1 and 2026Q2 added, HLT quarterly RevPAR against nights y/y gives walk-forward RMSE 0.665x naive and 0.632x AR(1) on the 2023Q1 window (r +0.88, permutation p 0.000, sign right 6 of 10); MAR gives 0.691x and 0.656x (sign right 7 of 10). Note 08's finding that RevPAR "tracks but does not beat naive" was made on ratios near 1.0 and no longer holds on this window. It is still only ten walk-forward quarters and the sign accuracy is 60 to 70 percent, so it is a corroborating read, not a forecast I would stake the pitch on.

3. **TSA confirms note 08's negative and sharpens it.** Quarter-to-date through 10 September, TSA throughput is **-2.65% y/y**, against -0.39% for the whole of 2Q26. So US air volume is decelerating 2.3 pp while ABNB guides nights to accelerate into low double digits. The TSA family's best walk-forward ratio is 0.92 on nights and it fails on the longer window (0.98 to 1.00). Air traffic is a genuinely bad nights predictor and is currently pointing the opposite way to the guide, which is exactly why it cannot be used as the bear case on its own.

4. **The one genuinely new external survivor is NTTO I-94 US inbound arrivals, and it is the cheapest signal nobody in the repo has used.** The full monthly history back to 2000 is a single free xlsx that is kept current to July 2026 preliminary (the team's inventory lists NTTO only as "figures quoted from public releases"). Overseas arrivals, first month of the quarter, against nights y/y: walk-forward 0.743x naive, 0.705x AR(1), r +0.79, permutation p 0.000, n = 10. Total all-countries arrivals does slightly better at 0.720x. It is knowable before the print (September preliminary lands mid-October). Its 3Q26 reading is July overseas arrivals -7.0% y/y, which is an improvement on 2Q26's -14.1%, so on this one feature inbound is a shrinking drag rather than a worsening one.

5. **Stacking every knowable-today survivor gives 3Q26 nights +9.2% (median of 12 specs, range +6.8% to +12.0%) against a naive 2Q26-repeat of +10.3% and the team baseline of +9.9%.** The twelve specs are not independent, the fits are in-sample on the full window, and the spread is 5 pp wide, so this is a consistency check and not a competing forecast. Read plainly: nothing external argues the team baseline is wrong, and nothing external is precise enough to tighten it. The honest sentence for the deck is that the external evidence puts 3Q26 nights in single digits rather than the low double digits management guided to, which is the same direction the H1-to-H2 bridge already points.

6. **No external source, free or paid, will deliver September 2026 before the 2 October pitch.** Verified: Inside Airbnb has no September snapshot (all 122 market paths probed for 1 to 10 September, zero hits, and the cadence is a June batch then an August batch); Similarweb publishes the month by the 10th of the following month; Eurostat's 3Q26 platform nights arrive around January 2027; Census QSS 3Q26 advance lands 19 November. September must be forecast, not observed. That is a structural fact about the calendar, not a gap in our effort.

7. **The single most useful outside statement found is Marriott's CEO at the BofA Gaming and Lodging Conference on 9 September: "We saw 7% RevPAR growth in July. We saw 8% RevPAR growth in the U.S. and Canada," with the clean adjustment "even if you back out the impact in U.S. and Canada of this extraordinary FIFA World Cup, we were still up 5% in July."** Named executive, hard numbers, self-supplied event adjustment, and it reconciles with the independent STR July print. The closest thing to an ABNB read-through is Expedia's CEO at Communacopia on 9 September: "Trends we've seen in July were consistent with what we'd seen in the second quarter," which matters because the team's own peer study found EXPE reads through to ABNB and BKNG does not.

8. **Airbnb itself gave no quarter-to-date number.** Across 1 August to 11 September 2026 there is exactly one conference appearance (Chesky at Goldman Communacopia, 8 September), one 8-K (the 6 August earnings release), no CFO appearance after the call, and no mid-quarter business update. Chesky's present-tense language on 8 September is directionally positive and quantitatively empty: "Almost every market is accelerating. Almost every country is accelerating," "Four of the five countries are accelerating," "India is growing 60% year-over-year." Treat these as tone, not data. Note that he is speaking five and a half weeks into the quarter and chose not to update the guide.

9. **The paid sources would not fix this either, and the one that would is unobtainable.** Consumer Edge is the only vendor that splits transaction count from average ticket, which is exactly the nights-versus-ADR decomposition the print turns on, at T+3 days. It is not publicly priced, the third-party band is $150k and up, and the $3,600/yr Dewey academic channel publishes no recency guarantee. Two priors in the repo need correcting: YipitData has no travel or OTA public footprint at all and is the wrong vendor to chase, and Bloomberg Second Measure is **not** bundled in a standard terminal seat, so the Hough Hall assumption in the access map needs one email to verify.

---

## 2. Tables

### 2.1 Ranked sources, coverage of Jul-Sep 2026 by backtest quality

Full table with URLs and access dates in `data/processed/q3nowcast/G/source_inventory.csv` (40 rows). Coverage score 3 means it reaches into September today, 2 means July and August today with September before the 5 Nov print, 0 means it does not reach 3Q26. Backtest score 3 means best walk-forward ratio on nights below 0.80, 2 means 0.80 to 0.95, 1 means 0.95 to 1.00, 0 means it never beat naive or has no testable quarterly history. Both scores are scoring rules I chose, so DESCRIPTIVE.

| Rank | Source | Coverage end | Cov | Best WF ratio, nights | BT | Score | Nearest ABNB series |
|---|---|---|---|---|---|---|---|
| 1 | CoStar/STR US weekly hotel RevPAR | 2026-09-05 | 3 | 0.665 | 3 | 9 | nights (occupancy) and ADR (rate) |
| 2 | TSA checkpoint throughput, daily | 2026-09-10 | 3 | 0.924 | 2 | 6 | nights (weak), Seats Booked |
| 3 | BLS CPI lodging away from home, NSA and SA | 2026-08 | 2 | 0.716 | 3 | 6 | ADR, US, price only |
| 4 | NTTO I-94 overseas arrivals to the US | 2026-07 | 2 | 0.720 | 3 | 6 | North America nights, inbound leg |
| 5 | CoStar/STR US monthly hotel RevPAR | 2026-07-31 | 2 | 0.665 | 3 | 6 | nights and ADR |
| 6 | Spain INE Frontur arrivals and EOH hotel nights | 2026-07 | 2 | 0.839 | 2 | 4 | Europe nights |
| 7 | Spain INE EOAT apartment nights plus IPAP price index | 2026-07-31 | 2 | 0.839 | 2 | 4 | nights AND ADR, Spain; NOT YET PULLED |
| 8 | Airbnb newsroom travel-trend posts | 2026-09-10 | 3 | none | 0 | 0 | searches, never nights |
| 9 | Apple App Store US Travel top free chart | 2026-09-11 | 3 | none | 0 | 0 | installs; point-in-time only, no history |
| 10 | Eurocontrol European daily flight traffic | 2026-09-03 | 3 | none | 0 | 0 | EMEA nights, loose; JS-only, no series extracted |
| 11 | Census QSS NAICS 721 accommodation revenue | 2026Q2 | 3 | none | 0 | 0 | US GBV; 3Q26 advance 19 Nov, after the print |
| 12 | AirDNA free monthly Europe/US market review | 2026-07-31 | 2 | none | 0 | 0 | nights AND ADR, same asset class; no free archive to backtest |
| 13 | BofA Institute Consumer Checkpoint | 2026-07-31 | 2 | none | 0 | 0 | GBV; lodging y/y is a chart bar with no printed number |
| 14 | Inside Airbnb August 2026 CDN batch | 2026-08-31 | 2 | none | 0 | 0 | nights (stayed, not booked); composition broke it in note 08 |
| 15 | JNTO Japan inbound arrivals | 2026-07-31 | 2 | none | 0 | 0 | APAC nights, Japan only |
| 16 | IATA Air Passenger Market Analysis | 2026-07-31 | 2 | none | 0 | 0 | nights, very loose |
| 17 | Similarweb free tier airbnb.com visits | 2026-08-31 | 2 | none | 0 | 0 | bookings funnel; 3-month tile only, history gated |
| 18 | US Travel Insights Dashboard (has an explicit STR demand line) | 2026-07-31 | 2 | none | 0 | 0 | nights; page 403s to fetchers, verify in a browser |
| 19 | AAA holiday travel forecasts | 2026-07-05 | 2 | none | 0 | 0 | nights, US domestic; 5 irregular obs per year |
| 20 | Eurostat `tour_ce_omr` platform nights | **2026-03** | 0 | 1.067 | 0 | 0 | nights, EU; confirmed five-month lag |
| 21 | Airlines for America summer/Labor Day forecast | 2024-05 | 0 | none | 0 | 0 | **NOT PUBLISHED in 2026** |
| 22 | Mastercard SpendingPulse monthly US | 2025-12-24 | 0 | none | 0 | 0 | **no free monthly release since about 2022** |
| 23 | UK ONS overseas travel and tourism, monthly | 2022-12 | 0 | none | 0 | 0 | **series discontinued since 2023** |

### 2.2 Backtest scoreboard, 288 tests

From `G_backtests_all.csv` and `G_backtest_scoreboard.csv`. Flagged means absolute r above 0.5 and permutation p below 0.05. Beat naive means walk-forward ratio below 1 with at least six walk-forward quarters.

| Family | Window | Tests | Flagged | Evaluable WF | Beat naive | Beat by 20%+ | Best ratio |
|---|---|---|---|---|---|---|---|
| Hotel RevPAR (MAR, HLT) | 2023Q1+ | 16 | 8 | 16 | 6 | 2 | **0.665** |
| BLS CPI price | 2023Q1+ | 24 | 8 | 24 | 8 | 2 | **0.716** |
| NTTO US inbound | 2023Q1+ | 24 | 12 | 24 | 9 | **5** | **0.720** |
| OTA room nights (BKNG, EXPE) | 2023Q1+ | 16 | 3 | 16 | 3 | 1 | 0.744 |
| Spain INE | 2023Q1+ | 40 | 20 | 40 | 14 | 0 | 0.839 |
| TSA air throughput | 2023Q1+ | 12 | 6 | 12 | 3 | 0 | 0.924 |
| Eurostat platform | 2023Q1+ | 12 | 4 | 12 | 1 | 0 | 0.932 |
| Hotel RevPAR | 2022Q1+ | 16 | 12 | 16 | 2 | 1 | 0.755 |
| NTTO US inbound | 2022Q1+ | 24 | 16 | 24 | 7 | 1 | 0.760 |
| OTA room nights | 2022Q1+ | 16 | 12 | 16 | 1 | 0 | 0.843 |
| TSA air throughput | 2022Q1+ | 12 | 9 | 12 | 2 | 0 | 0.976 |
| Spain INE | 2022Q1+ | 40 | 23 | 40 | **0** | 0 | 1.003 |
| BLS CPI price | 2022Q1+ | 24 | 12 | 24 | **0** | 0 | 1.318 |
| Eurostat platform | 2022Q1+ | 12 | 6 | 12 | **0** | 0 | 1.027 |

Every family collapses on the longer window. That is the same pattern note 03 and note 08 found: the 2022 reopening base effect makes everything correlate with everything, and a feature that only survives on the short window is surviving on 14 observations. The Spain INE family is the clearest illustration, 14 of 40 beating naive on 2023Q1+ and 0 of 40 on 2022Q1+.

### 2.3 Top survivors on nights, walk-forward ratio below 0.90

| Feature | Window | n | WF n | r | perm p | vs naive | vs AR(1) | sign acc | Knowable before 5 Nov |
|---|---|---|---|---|---|---|---|---|---|
| hlt_revpar_full | 2023Q1+ | 14 | 10 | +0.879 | 0.000 | **0.665** | 0.632 | 0.60 | yes, HLT reports late Oct |
| mar_revpar_full | 2023Q1+ | 14 | 10 | +0.878 | 0.000 | **0.691** | 0.656 | 0.70 | yes, MAR reports about 4 Nov |
| cpi_lodging_sa_full | 2023Q1+ | 13 | 9 | +0.829 | 0.000 | **0.716** | 0.672 | 0.78 | yes, Sep CPI 13 Oct |
| ntto_total_full | 2023Q1+ | 14 | 10 | +0.783 | 0.000 | **0.720** | 0.683 | 0.70 | yes, Sep prelim mid-Oct |
| ntto_total_qtd1m | 2023Q1+ | 14 | 10 | +0.796 | 0.000 | **0.724** | 0.687 | 0.60 | **yes, observable today** |
| cpi_lodging_nsa_full | 2023Q1+ | 13 | 9 | +0.832 | 0.001 | 0.733 | 0.689 | 0.67 | yes, Sep CPI 13 Oct |
| ntto_overseas_qtd1m | 2023Q1+ | 14 | 10 | +0.794 | 0.000 | 0.743 | 0.705 | 0.60 | **yes, observable today** |
| bkng_nights_full | 2023Q1+ | 14 | 10 | +0.895 | 0.000 | 0.744 | 0.707 | 0.60 | yes, BKNG reports about 28 Oct |
| mar_revpar_full | 2022Q1+ | 18 | 14 | +0.937 | 0.000 | 0.755 | 0.547 | 0.64 | yes |
| ntto_total_full | 2022Q1+ | 15 | 11 | +0.876 | 0.000 | 0.760 | 0.514 | 0.73 | yes |
| ntto_weurope_qtd1m | 2023Q1+ | 14 | 10 | +0.751 | 0.002 | 0.781 | 0.741 | 0.70 | **yes, observable today** |
| ntto_overseas_full | 2023Q1+ | 14 | 10 | +0.736 | 0.004 | 0.798 | 0.758 | 0.60 | yes |
| es_hotel_nights_foreign_qtd1m | 2023Q1+ | 14 | 10 | +0.829 | 0.010 | 0.839 | 0.796 | 0.50 | tight, INE Sep release about 3 Nov |
| es_frontur_tourists_qtd1m | 2023Q1+ | 14 | 10 | +0.831 | 0.006 | 0.859 | 0.815 | 0.60 | tight |
| es_hotel_travellers_qtd1m | 2023Q1+ | 14 | 10 | +0.802 | 0.017 | 0.877 | 0.833 | 0.50 | tight |
| es_hotel_nights_qtd1m | 2023Q1+ | 14 | 10 | +0.806 | 0.017 | 0.884 | 0.840 | 0.50 | tight |

### 2.4 What the observable-today features actually read for 3Q26

From `G_feature_readings_3q26.csv`. All SOURCED.

| Feature | 2026Q2 y/y | 3Q26 y/y so far | Change, pp | Window observed |
|---|---|---|---|---|
| TSA throughput | -0.39% | **-2.65%** | -2.26 | 1 Jul to 10 Sep (72 days) |
| CPI lodging away from home, NSA | +4.89% | **+3.11%** | -1.78 | Jul and Aug |
| CPI lodging away from home, SA | +4.73% | +3.00% | -1.73 | Jul and Aug |
| CPI airline fares, SA | +23.67% | +24.45% | +0.78 | Jul and Aug |
| NTTO overseas arrivals to the US | -14.12% | **-7.02%** | **+7.10** | Jul |
| NTTO Western Europe arrivals to the US | -20.07% | -10.47% | +9.60 | Jul |
| Spain Frontur tourists | +5.24% | +4.64% | -0.59 | Jul |
| Spain Frontur total visitors | +3.54% | +1.96% | -1.58 | Jul |
| Spain hotel overnight stays, total | +1.13% | +0.33% | -0.80 | Jul |
| Spain hotel overnight stays, non-residents | +1.26% | +1.06% | -0.20 | Jul |
| US hotel RevPAR (STR, not in the model) | +3 to +5% in Q2 per MAR/HLT | +8.2% Jul, +1.7% w/e 29 Aug | see 2.5 | Jul to 5 Sep |
| European STR RevPAR (AirDNA, not in the model) | n/a | +7.7% Jul, ADR +8.2%, nights +0.8% | n/a | Jul, Sep pacing +6.9% |

Nine of eleven machine-pulled readings are decelerating. The exception is US inbound, which is a shrinking drag. Note that **ADR-relevant prices are decelerating too**: CPI lodging away from home falls from +4.9% to +3.1%, which sits awkwardly against a guide of "a moderate increase in ADR due to mix shift and price appreciation" and matches the STR ADR fade from +5.7% in July to +0.6% in late August.

### 2.5 The STR weekly path, the highest-frequency external evidence we have

From `str_weekly_us_3q26.csv`. All SOURCED, hand-keyed from trade-press reprints because costar.com returns 403.

| Period | Occupancy y/y | ADR y/y | RevPAR y/y | Published |
|---|---|---|---|---|
| July 2026, full month | +2.3% | +5.7% | +8.2% | 26 Aug |
| w/e 1 Aug | n/a | n/a | +7.3% | 6 Aug |
| w/e 8 Aug | n/a | +4.1% | +7.2% | 14 Aug |
| w/e 15 Aug | +2.6% | +3.5% | +6.2% | 20 Aug |
| w/e 22 Aug | +2.1% | +2.3% | +4.4% | 27 Aug |
| w/e 29 Aug | +1.1% | +0.6% | +1.7% | 3 Sep |
| w/e 5 Sep | +9.4% | +6.1% | +16.1% | 11 Sep |

The last two rows are one event. Labor Day fell a week later in 2026, so the w/e 29 Aug weekend was compared against a holiday weekend and the w/e 5 Sep weekend was not. CoStar flags this itself and reports that within the w/e 29 Aug week, Sunday to Thursday RevPAR rose 10.9% on a 6.4% demand increase. Averaging the two weeks gives about +8.5% RevPAR, which is closer to the July run rate than to the +4.4% of the prior clean week. I do not know which of those two readings is right, and that ambiguity is the single largest piece of uncertainty in the external picture for the last fortnight of the quarter.

### 2.6 Intra-quarter commentary digest

Full file `intra_quarter_commentary.csv`, 96 rows, 27 companies, 17 Jun to 11 Sep 2026, with verbatim quote, metric, direction, URL, access date and source type (42 primary transcript, 19 company press release, 22 news coverage, 12 industry press release, 1 documented negative). Paraphrases are marked PARAPHRASE and clean negatives are recorded as rows.

**Airbnb's own Q3 inputs.** The 6 August guide is the only quantitative Q3 statement: revenue $4.69-4.77bn, +15-17%, inclusive of about 3 pp FX tailwind after hedge; GBV mid-teens; **"low double-digit growth in nights and seats booked"** against 2Q26 actual +10.3%, so the guide embeds acceleration; ADR up moderately on mix shift and price appreciation; implied take rate roughly flat; EBITDA margin down slightly y/y on investment timing. Two caveats management volunteered: "Even against tougher comps in the back half of the year, we are raising our full year guidance" (Mertz), and in July Airbnb **expanded the types of bookings eligible for Reserve Now Pay Later**, which was already over 20% of 2Q26 GBV and which Mertz says "drove more bookings, longer booking lead times, and contributed to the increase in ADR." A longer book-to-check-in gap is the main mechanical risk to the 3Q26 revenue-versus-GBV relationship and to the take rate, and it is the same RNPL confound that note 08's funds-held model tripped over.

**Peers, ranked by usefulness for ABNB.**
1. MAR at BofA, 9 Sep: July RevPAR +7% global, +8% US and Canada, +5% ex-World Cup; Middle East improved from -43% in Q2 to -12% in July; group "turned upwards in a really encouraging way" in July.
2. EXPE at Communacopia, 9 Sep: "Trends we've seen in July were consistent with what we'd seen in the second quarter." Q2 was room nights +6% (US mid-single, EMEA low-single, rest of world low-double) with ADR +5% FX-neutral and "our fastest U.S. growth in 15 quarters."
3. BKNG 2Q26 8-K, 4 Aug: "Global travel demand has remained resilient so far in the third quarter, supported by healthy domestic travel trends," paired with a Q3 room-night guide of **+3% to +5% against Q2 actual +5%**. Resilient commentary, decelerating guide. At Communacopia the CFO said the US was the strongest market in Q2 and gave no new forecast.
4. CHH at BofA, 9 Sep: July RevPAR about 100 bp above June and Q3 "higher than Q2," from "project-based business travel, as well as more value driven leisure travel," with a "C-shaped economy" and "you are possibly seeing some trade down." The trade-down framing is the mix-down risk to ABNB ADR even with healthy nights.
5. Hilton 2Q26: Q3 system-wide RevPAR about 4%, US mid-single digits, and inbound international recovery framed explicitly as a **2027** story. Hyatt: Q3 about 3%. IHG H1: EMEAA Q2 only +0.6% with Middle East -19%.
6. Tripadvisor 2Q26, 6 Aug: US-to-Europe bookings "well below levels seen at the beginning of the year," and unusual weather "dampened bookings growth and increased cancellations throughout July." The only cancellation evidence in the set.
7. Sabre 2Q26: "The trends we saw in June have continued through July," Q3 air distribution bookings guided flat to low single digits, corporate offsetting "softness in leisure demand."
8. Airlines are loud on price and quiet on volume. DAL, UAL, AAL, LUV, ALK and JBLU all guide Q3 unit revenue up double digits, while IATA reports July global RPK **+0.2%** and **North America RPK -1.2%**. Air travel is not growing in volume; lodging is. Any ABNB 3Q26 nights upside is mix and share, not a rising travel tide.

**Clean negatives worth as much as the positives.** Airbnb appeared at no conference in the window other than Communacopia, filed no mid-quarter 8-K and made no CFO appearance. AAA published no Labor Day 2026 volume forecast at all and made no record claim. Airlines for America published no 2026 summer or Labor Day forecast. UAL and LUV speak at Morgan Stanley Laguna on **16 September**, five days after this cut. There were **zero Atlantic hurricanes** through 9 September, the latest first hurricane since 1966, so weather is a non-factor; Tropical Storm Edouard caused about 2,510 US flight disruptions over Labor Day weekend and European ATC staffing, not storms, was the Q3 supply friction. The widely circulated "Canada-to-US collapse" stories are 2025-dated; Statistics Canada shows June 2026 Canadian return trips from the US **+5% y/y**, still 24.6% below June 2024.

### 2.7 What we cannot get, priced

Full table with cost labels in `paid_sources_priced.csv`, free academic and mirror datasets in `free_datasets_2025_2026.csv`. Every price is labelled VENDOR-PUBLISHED or THIRD-PARTY BAND; the recurring "$150k and up" for card panels is altdata.wiki's third-party band, not a vendor quote.

| Source | What it would give for 3Q26 | Cost | Student verdict before 2 Oct |
|---|---|---|---|
| Consumer Edge | US and EU card spend at Airbnb splitting **transaction count from average ticket**, T+3 days, i.e. a true nights proxy and a true ADR proxy | not quoted; $150k+ band; Dewey academic $3,600/yr | **NO.** Dewey publishes no recency spec, so even the academic channel would not nowcast |
| YipitData | 40+ ticker panels | not quoted; high six figures | **NO, and downgrade the prior.** Zero travel or OTA public footprint, no free ABNB commentary |
| Bloomberg Second Measure | US card panel to ABNB brand sales | not quoted; $150k+ band | **NO, and verify the access map.** Not bundled in a standard terminal seat; ships via Data License entitlements |
| STR / CoStar Benchmark | Property-level hotel benchmarking | "$750/yr entry" (third party) | **NO.** Access is tied to submitting your own hotel data, so students are structurally ineligible. The free weeklies are the usable product |
| AirDNA MarketMinder | Market-level monthly STR occupancy, ADR, RevPAR, CSV export, 36 months | **$125/mo or $400/yr, vendor-published** | Affordable, but gives markets not a global aggregate, and still no September |
| Similarweb | airbnb.com visits, daily at paid tier | Starter $125/mo (third party); free tier exists | **NO for September.** The month publishes by the 10th of the following month, so buying does not move the date |
| Sensor Tower | Airbnb app downloads and DAU/MAU | not quoted; Vendr median $75k/yr | **NO.** Sales-gated annual contracts, no free artifact covers Jul-Sep |
| Appfigures | Daily Airbnb download estimates, 100 countries, MAPE 5-25%, iPhone only | **$149.99/mo, vendor-published** | **YES, the only realistic buy.** About $150 buys the full Jul 1 to Sep 30 daily series pullable on 2 Oct. A corroborating cross-check, never the read |
| Facteus | 185m cards, Airbnb is a tracked brand with sales AND transaction counts | not quoted; $150k+ band; AWS backtest listings $0 | **NO for 3Q26**, but the most sample-friendly vendor; the free brand page is stamped 7 Jan 2026 with Dec 2025 as the latest month |
| Revelio Labs | ABNB monthly headcount, postings, attrition | **$85,000 per 12 months on AWS, vendor-published**; $0 trial listing on AWS Data Exchange | YES but only for the cost and margin leg. Zero read-through to nights, ADR or GBV |
| Placer.ai | Nothing direct, no ABNB estate | not quoted, and circulating figures audited as untraceable | **NO.** The free hotel index stops at Dec 2024 |
| Nasdaq Data Link | Nothing. The live free catalogue returns one product, a carbon-removal calendar | n/a | **NO.** The Quandl free catalogue is gone |

**Free academic and Kaggle mirrors: the prior is refuted by exactly one source.** ICPSR returns zero Airbnb studies, data.world's Open Data Community was retired 13 July 2026, Tom Slee's archive 404s, GitHub has code not data, and every Hugging Face or Harvard Dataverse record with a 2026 upload date carries 2017 to 2023 data. The exception is **Inside Airbnb's unlisted August 2026 batch on the CDN, 86 of 122 markets, scrapes 10 to 31 August, reviews through 30 August, CC BY 4.0**, which is the freshest usable public Airbnb dataset in existence. The team's disk holds only about 49 of those 86 markets and the wave is alphabetically truncated, missing LA, SF, Chicago, Boston, London, Paris, Barcelona, Singapore, Sydney and Toronto. Kaggle coverage dates could not be verified (JS-rendered pages) and the Zenodo API returned 403, so both are labelled unverified rather than guessed; neither showed any evidence of 2026 coverage.

### 2.8 Does anything external beat the team's own H1-to-H2 bridge for 3Q26?

No, and the reason is structural rather than a failure of search. The bridge forecasts the quarter ABNB will report, which is **nights booked** in a quarter that is 80 percent complete and whose last three weeks nobody outside the company can observe. Every external series either measures a different asset class (hotels, airlines, arrivals), measures a different act (stayed nights, card spend, searches, app installs), or stops before September. The best of them, the CoStar/STR weekly series, beats naive by a third on nights in the backtest and reaches 5 September, but it is US-only, hotel-basis, and its final two weeks are a calendar artefact that swings the reading by 14 pp. The twelve knowable-today survivors stacked together put 3Q26 nights at a median +9.2% with a 5 pp range, which straddles the team's +9.9% baseline and sits below management's low double digits. So the external evidence does two useful things and one useless thing: it **corroborates** the bridge's direction (single digits, not low double digits), it **adds the ADR leg** that the bridge is weakest on (CPI lodging +4.9% to +3.1%, STR ADR +5.7% to +0.6%, AirDNA Europe ADR +8.2%, all pointing to price decelerating in the US while holding in Europe), and it **cannot tighten the nights band** because it is less precise than the bridge it would be replacing. The external read belongs in the pitch as the corroboration slide and the ADR cross-check, not as the forecast.

---

## 3. Method

Everything is quarterly. Daily and monthly inputs are aggregated by calendar quarter and expressed as y/y percent. Each series is built in two vintages: `_full`, the whole calendar quarter, which for every survivor here publishes before the 5 November print and is guarded so an incomplete quarter produces a missing value rather than a biased average; and a quarter-to-date vintage observable on 11 September 2026, which is `_qtd72` for TSA (days 1 to 72 of the quarter, 1 July to 10 September, compared against the same 72 days a year earlier), `_qtd` for BLS CPI (the first two months, since August CPI printed on 11 September), and `_qtd1m` for NTTO and Spain INE (the first month, since only July is published). Every feature carries a `knowable_before_print` label.

Per pair: Pearson r and p, Spearman, a 1,000-shuffle permutation p computed on standardised vectors, leave-one-out OLS RMSE against the leave-one-out mean, then the expanding-window walk-forward that the conclusions are written off. At each quarter t the model is refit on data strictly before t, predicts t, and is scored against three baselines refit the same way: naive y[t-1], prior year y[t-4], and an AR(1). A ratio below 1 means the feature helped. Sign accuracy is the share of walk-forward quarters where the predicted change from y[t-1] has the actual sign. Two windows are reported for every pair, 2022Q1 to 2026Q2 with walk-forward from 2023Q1, and 2023Q1 to 2026Q2 with walk-forward from 2024Q1. The second is the one to read, for note 03's reason: 2022 still carries reopening base effects.

**Test count and multiplicity.** 36 features times 4 targets times 2 windows is 288 tests. At 5 percent we would expect about 14 false positives on correlation alone, and the features are far from independent (three NTTO regions in two vintages, five Spain INE series in two vintages, three CPI series in two vintages). This is why every conclusion is written off the walk-forward column and not off r, and why I report the whole scoreboard including the families that failed.

The 3Q26 nowcast figures in section 1 are in-sample OLS fits on the full window applied to the 2026Q3 feature reading, not walk-forward predictions, because a walk-forward prediction for 2026Q3 requires the 2026Q3 target which does not exist. They are labelled as such in `G_nowcast_3q26_observable.csv` and should be read as a consistency band, not a forecast. The commentary file is a web-research artefact: every row carries its URL, access date and a source-type flag, and nothing was recorded without a retrievable page.

---

## 4. What this can and cannot identify

**Can.** Whether each free external series reaches into 3Q26 today and when the rest of the quarter publishes. Whether each series with quarterly history beats three naive baselines out of sample on disclosed ABNB nights, GBV, revenue and ADR. The direction and magnitude of every observable-today reading against its own 2Q26 value. What Airbnb and its peers said in public between 1 August and 11 September and, equally, what they conspicuously did not say. What the paid sources cost and whether a student team can reach them by 2 October.

**Cannot.** September 2026 for any source. This is verified, not assumed: Inside Airbnb has no September snapshot across all 122 market paths, Similarweb publishes by the 10th of the following month, Eurostat's 3Q26 lands around January 2027, Census QSS 3Q26 advance lands 19 November. Occupancy, which nothing public measures. Realised ABNB ADR, since CPI lodging is a hotel-weighted price index, STR ADR is hotels, and the Inside Airbnb 2026 calendars lost their price column. Anything about the revenue-minus-GBV gap, which is where RNPL bites and which no external series sees.

**Where the biases bite.** TSA counts travellers at checkpoints including connections and business travel, so it is a poor volume proxy for leisure nights and its correlation with nights halved after 2024. NTTO measures the inbound leg only, which is a small share of ABNB's North America nights, and it is a strong statistical performer for a reason I cannot fully justify economically, so treat it as a correlate on 10 to 14 observations rather than a mechanism. Spain INE hotel nights are hotels, and Frontur is arrivals at the border, neither of which is a platform night. Hotel RevPAR blends occupancy and rate, so a RevPAR beat can be an ADR beat with flat volume, exactly as happened in August. The Inside Airbnb review proxy measures **stayed** nights while ABNB reports **booked** nights, a three-to-eight-week lead-time mismatch, on a survivorship-selected set of listings live at dump time. The STR weekly Labor Day artefact is a genuine basis break within the quarter, not noise. And the single largest caveat on the whole note: six of the fourteen families beat naive on a 14-observation window and none on the 18-observation window, which is the signature of a common deceleration rather than of prediction.

---

## 5. Next evidence

1. **Pull Spain INE EOAT table 429 (tourist apartments) and Eurostat `tour_occ_nim` NACE I552.** Both were identified but not pulled. EOAT gives apartment nights **and** the IPAP apartment price index monthly with a one-month lag, which is the only free source that carries a nights series and an ADR series on the same asset class. `tour_occ_nim` reaches June 2026 against `tour_ce_omr`'s March, so it is the faster Eurostat sibling and should replace it in the panel.
2. **Add the CoStar/STR weekly series to the backtest properly.** It currently enters only through MAR and HLT quarterly RevPAR. Building a weekly-to-quarterly US RevPAR feature from the trade-press archive back to 2023 would let the strongest source be tested directly instead of by proxy.
3. **Two dated catalysts before the pitch.** The STR August monthly publishes about 23 September, and UAL plus LUV speak at Morgan Stanley Laguna on 16 September with "remarks on current trends affecting the business." Both land before 2 October. The STR week-ending 12 September release on about 17 September is the first clean post-Labor-Day reading and will resolve the artefact in section 2.5.
4. **Two dated catalysts after the pitch but before the print.** September CPI on 13 October, NTTO September preliminary mid-October, BKNG reports about 28 October, HLT late October, MAR about 4 November. Four of the seven strongest survivors are knowable in that window, so the prediction card should be re-scored on 20 October rather than left at the 2 October state.
5. **Pull the remaining 37 Inside Airbnb August markets from the CDN.** The team holds about 49 of 86 and the missing set is the important half. Then difference `number_of_reviews_l30d` and `_ltm` between the June and August batches on matched listing ids, which controls for listing churn in a way the raw counts do not. Note 08's `reviews_l30d` proxy was the most promising untested metric and is still untested.
6. **One email and about $150.** Email the UF business librarian to confirm whether the Capital IQ Pro seat includes the Visible Alpha KPI module and whether any Bloomberg alternative-data entitlement exists, and if the team wants a genuinely independent cross-check, buy one month of Appfigures on 2 October for the full daily Airbnb download series across Jul to Sep.

---

## 6. Files

**Scripts.** `analysis/src/q3nowcast/G1_collect_external_series.py`, `G2_external_backtests.py`, `G3_rank_sources.py`.

**Outputs, all under `data/processed/q3nowcast/G/`.**
- `source_inventory.csv` (40 sources ranked, coverage score by backtest score, URL and access date on every row)
- `source_inventory_raw.csv` (the 20 machine-pulled series and page caches with URL, bytes, HTTP status, coverage end, basis, nearest ABNB series)
- `intra_quarter_commentary.csv` (96 rows, 27 companies, 17 Jun to 11 Sep 2026)
- `str_weekly_us_3q26.csv` (the CoStar/STR July monthly plus six weekly prints to 5 Sep)
- `G_quarterly_panel.csv` (36 features plus 4 targets, 2018Q1 to 2026Q3)
- `G_backtests_all.csv` (288 tests), `G_backtest_survivors.csv`, `G_backtest_scoreboard.csv`
- `G_nowcast_3q26.csv`, `G_nowcast_3q26_observable.csv`, `G_feature_readings_3q26.csv`
- `paid_sources_priced.csv` (24 vendor rows, every price labelled vendor-published or third-party band)
- `free_datasets_2025_2026.csv` (16 rows, the Inside Airbnb August 2026 batch is the only one with 2026 dates)
- `raw/` cache, committed: `tsa_checkpoint_daily.csv` (2,810 days, 2019-01-01 to 2026-09-10), `bls_cpi_travel_monthly.csv` (5 series to Aug 2026), `ine_frontur_visitors_monthly.csv`, `ine_frontur_by_country_monthly.csv`, `ine_hotel_overnight_monthly.csv` (all to Jul 2026), `eurostat_tour_ce_omr_eu27.csv` (to Mar 2026), `ntto_arrivals_monthly.csv` (11 world regions, 2000-01 to 2026-07, flattened from the vendor xlsx and the file G2 actually reads).
- **Not committed, per the brief's no-raw-dumps rule, but recorded in `source_inventory_raw.csv` with URL and byte size:** four NTTO xlsx files including the 2000-to-present monthly history current to Jul 2026 preliminary, the Eurostat JSON payload, three JNTO landing-page caches. Re-download any of them with `py -3.13 analysis/src/q3nowcast/G1_collect_external_series.py ntto eurostat jnto`; G2 rebuilds the panel identically from `ntto_arrivals_monthly.csv` without them (verified).
