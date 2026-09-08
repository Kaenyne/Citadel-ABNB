# ABNB catalyst calendar (as of 6 Sep 2026)

Last close $181.94 (4 Sep 2026) per the [ABNB Move Explorer](https://claude.ai/code/artifact/57e193ea-b799-47b2-a52a-bf42010fb318). Companion files: `data/processed/abnb_big_moves_7pct.csv` (all 41 moves ≥7% since IPO, transcribed from the Move Explorer), `data/processed/abnb_big_move_stats_by_driver.csv` and `analysis/src/big_move_reaction_stats.py`.

## 1. How big is each kind of catalyst historically?

All ≥7% close-to-close moves since the 10 Dec 2020 IPO, grouped by the Move Explorer's driver tag (n = 41). Computed by `analysis/src/big_move_reaction_stats.py`.

| Driver | n | Up / down | Mean abs move | Median | Range | Same-day QQQ (mean abs) | Excess vs QQQ | Excess vs BKNG | n since 2023 |
|---|---|---|---|---|---|---|---|---|---|
| Earnings | 11 | 6 / 5 | 12.1% | 13.3% | +17.4% / −13.4% | 1.1% | 11.3 pts | 9.8 pts | 7 |
| Macro / market | 20 | 9 / 11 | 8.6% | 8.1% | +14.8% / −12.1% | 3.6% | 5.1 pts | 4.2 pts | 2 |
| Company / other | 9 | 8 / 1 | 8.8% | 8.6% | +11.5% / −7.2% | 0.7% | 8.1 pts | 8.4 pts | 1 |
| Competitor / industry | 1 | 0 / 1 | 7.0% | — | −7.0% | 1.5% | 5.5 pts | 2.3 pts | 1 |
| All | 41 | 23 / 18 | 9.6% | 8.5% | | 2.3% | 7.4 pts | 6.6 pts | 11 |

Read-throughs:

- Regime shift. 2020–22: 18 of 30 big moves were macro. 2023 onward: 7 of 11 are earnings days; macro produced only the Liberation Day pair (3 Apr 2025 −7.2%, 9 Apr 2025 +14.8%). Source rows: Move Explorer.
- Earnings is the only catalyst that reliably clears ±10%. Mean 12.1% with QQQ ~flat — almost fully idiosyncratic.
- The earnings sign is set by the nights guide, not the beat. Drops on 2 Nov 2022 (−13.4%), 10 May 2023 (−10.9%), 7 Aug 2025 (−8.0%) were revenue beats with soft nights guidance; 14 Feb 2025 (+14.4%) was a nights beat with a below-consensus revenue guide that the market ignored. The 7 Aug 2024 (−13.4%) and 8 Nov 2024 (−8.7%) drops also had EPS misses. Source: Move Explorer KPI panels.
- Note the Move Explorer's side-panel claim of "six of eleven earnings moves were drops on revenue and EPS beats" does not match its own table: 5 drops total, 3 of them clean beat-and-drop.
- Company-specific non-earnings catalysts are almost all 2021 momentum/analyst days; the only one since 2023 is S&P 500 inclusion (5 Sep 2023, +7.2%).
- Competitor/industry has one entry: the 3 Feb 2026 AI-disintermediation day (ABNB −7.0% vs BKNG −9.3%, EXPE −15.3%). The market already prices ABNB as the least exposed OTA.

## 2. Dated calendar

| Date | Event | Direction risk | Historical analogue / expected size | Source |
|---|---|---|---|---|
| **9 Sep 2026** | European Commission presents draft Affordable Housing Act (VP Teresa Ribera): lets cities impose quantitative caps or grandfathering on STRs where price-to-income and supply metrics are breached; targets multi-property operators, exempts primary residences; then to Parliament and member states | Down headline risk; magnitude depends on professional-listing share in capped cities | No regulatory event has ever produced a ≥7% move (0 of 41). Expect low-single-digit unless a hard cap number appears | [Global Banking & Finance, 4 Sep 2026](https://www.globalbankingandfinance.com/proposed-eu-rules-curb-airbnb-short-term-rental-homes-draft/) |
| **15–16 Sep 2026** | FOMC (statement 2 pm ET on the 16th) | Two-way macro | Macro days average 8.6% when they do hit ≥7%, but only 2 macro days since 2023 have; ABNB's excess vs QQQ on macro days is ~5 pts | [Federal Reserve schedule](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm) |
| **2 Oct 2026** | Team prelim memo + model due | — | — | Team deadline |
| **22–24 Oct 2026** | Citadel finals, NYC | — | — | Team deadline |
| **Late Oct 2026** | Booking Holdings and Expedia Q3 prints | Read-across two-way | Peers' own prints have moved ABNB before (5 Nov 2021: EXPE +15.6%, ABNB +13.0% on its own print same day). Watch cross-border/inbound commentary — both flagged Middle East air-capacity pressure in Q2 | [MarketScale, 12 Aug 2026](https://www.marketscale.com/industries/hospitality/domestic-travel-carries-expedia-and-booking-holdings-past-q2-estimates-as-cross-border-headwinds-persist) |
| **27–28 Oct 2026** | FOMC | Two-way macro | As above | [Federal Reserve schedule](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm) |
| **~5 Nov 2026** (est.) | ABNB Q3'26 print. Guide: revenue $4.69–4.77B (+15–17% incl. ~3 pts FX), GBV mid-teens, nights low-double-digit, adj EBITDA margin down slightly YoY. Consensus EPS $2.53 | The catalyst. Sign set by the Q4 nights guide | Mean abs earnings move 12.1%; last six prints: −13.4, −8.7, +14.4, −8.0, (Q4'25 and Q1'26 <7%), +17.4 | [Airbnb Q2'26 release](https://news.airbnb.com/airbnb-q2-2026-financial-results/); [MarketBeat](https://www.marketbeat.com/stocks/NASDAQ/ABNB/earnings/) |
| **8–9 Dec 2026** | FOMC | Two-way macro | As above | [Federal Reserve schedule](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm) |

Competition-window implication: no ABNB print falls between 2 Oct and 24 Oct. The stock will trade on the EU act, AI-distribution headlines, macro and peer prints. The thesis has to be a view on the ~5 Nov Q4 nights guide.

## 3. Undated catalysts

### Up

| Catalyst | Evidence | Analogue |
|---|---|---|
| Nights re-acceleration holds | Q2'26 nights and seats +10% and accelerating; expansion markets ~2x core; LatAm ~20%, APAC high-teens; US, France, UK, Australia accelerating ([Yahoo call highlights](https://finance.yahoo.com/markets/stocks/articles/airbnb-q2-earnings-call-highlights-230346004.html)); FY26 revenue "at least mid-teens", margin ≥35.5% ([Airbnb](https://news.airbnb.com/airbnb-q2-2026-financial-results/)) | 14 Feb 2025 +14.4% (nights beat); 7 Aug 2026 +17.4% |
| Hotels scale / major-chain MSA | ~650M accounts, 90% of demand direct; hotel nights growing ~3x homes; 35% of first-time hotel guests later book a home; thousands of independents added across 20 destinations; no chain MSAs yet, execs say possible ([Hospitality Net](https://www.hospitalitynet.org/editorial/4134161/hilton-wires-into-google-chatgpt-and-claude-airbnb-brings-650-million-accounts-to-hotels-bad-records-keep-you-out-of-ai-answers.html)) | No precedent; treat as re-rating not one-day |
| Services / Experiences monetisation | Experiences supply +80% YoY; bookings accelerating but "small"; car rentals expected largest service category ([Yahoo call highlights](https://finance.yahoo.com/markets/stocks/articles/airbnb-q2-earnings-call-highlights-230346004.html)) | Disclosure of GBV contribution would be the trigger |
| AI margin story | ~45% of support issues resolved without a human; support cost per booking −16% YoY; features shipped +~80% ([Airbnb](https://news.airbnb.com/airbnb-q2-2026-financial-results/)) | Margin beats have not produced ≥7% days on their own — supports multiple rather than a spike |
| Capital return | $1.1B repurchased in Q2'26; described as core to capital allocation ([Yahoo call highlights](https://finance.yahoo.com/markets/stocks/articles/airbnb-q2-earnings-call-highlights-230346004.html)) | Floor on selloffs, not a spike |
| Favourable agentic-distribution deal | Hilton's Google AI Mode / ChatGPT / Claude integrations route bookings back to Hilton.com ([Hospitality Net](https://www.hospitalitynet.org/editorial/4134161/hilton-wires-into-google-chatgpt-and-claude-airbnb-brings-650-million-accounts-to-hotels-bad-records-keep-you-out-of-ai-answers.html)) — direct-heavy players negotiate from strength | Would unwind the 3 Feb 2026 discount |

### Down

| Catalyst | Evidence | Analogue |
|---|---|---|
| Valuation reset | ~30.9x forward vs BKNG 20x, EXPE 17x; Phillip Securities downgrade to Reduce, $158 PT, 11 Aug 2026; short interest 3.39% of float, 87 hedge-fund holders ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/airbnb-just-hit-four-high-110129364.html)) | Amplifier on any other catalyst |
| Soft Q4 nights guide | Q3 guide already "low double-digit" nights ([Airbnb](https://news.airbnb.com/airbnb-q2-2026-financial-results/)) — a reversion to high-single-digit is the bear trigger | 2 Nov 2022 −13.4%, 10 May 2023 −10.9%, 7 Aug 2025 −8.0% |
| Take rate stuck | Flat ~13.2% ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/airbnb-just-hit-four-high-110129364.html)); FY implied take rate "relatively flat" with Reserve Now Pay Later and incentives offsetting ([Yahoo call highlights](https://finance.yahoo.com/markets/stocks/articles/airbnb-q2-earnings-call-highlights-230346004.html)) | Revenue growth converges to nights + ADR + FX |
| Margin guide-down | Q3 margin guided down slightly on investment timing ([Airbnb](https://news.airbnb.com/airbnb-q2-2026-financial-results/)) | 7 Aug 2025 −8.0% ($200M new-business spend); 8 Nov 2024 −8.7% (expense growth) |
| Regulatory cascade | EU Affordable Housing Act (above) plus city-level actions | 0 of 41 big moves — would be first |
| Agentic commoditisation | Google AI Mode in-chat hotel booking live 27 Aug 2026 with Booking, Expedia, Hilton, Marriott, IHG, Wyndham, Priceline, Trip.com, Choice, Hotels.com — no Airbnb; Google shares only minimum booking data, keeps chat context ([Skift](https://skift.com/2026/08/27/googles-agentic-hotel-booking-tool-comes-to-ai-mode/)) | 3 Feb 2026 −7.0% (peers −9% / −15%) |
| Macro / consumer shock | 18 of 30 big moves in 2020–22 were macro; ABNB was the highest-beta travel name on rates (Move Explorer). Middle East conflict already pressuring air capacity and inbound ([MarketScale](https://www.marketscale.com/industries/hospitality/domestic-travel-carries-expedia-and-booking-holdings-past-q2-estimates-as-cross-border-headwinds-persist)) | 9 May 2022 −12.1%; 3 Apr 2025 −7.2% |

## 4. Caveats

- Move Explorer driver tags and "what happened" text are narrative attributions from same-day coverage, not verified causality. Rows 3, 10 and 25 explicitly say no catalyst was found.
- 23 earnings days exist but only 11 cleared 7%. For event-risk sizing, pull all 23 from price data (next step).
- Q3'26 date is MarketBeat's estimate from past schedules, not company-confirmed.
- All rows in the CSV were hand-transcribed from a rendered page on 6 Sep 2026; re-check any figure before it goes in the memo.
