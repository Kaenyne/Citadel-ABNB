# Workstream 10: regional and segment decomposition of nights, GBV and revenue

Krish Surapaneni / Citadel-ABNB, overnight run 6-7 Sep 2026. Last close used elsewhere: $181.94 (4 Sep 2026). Q3 2026 prints 5 Nov 2026.

Scripts: `analysis/src/overnight/10_fetch_fx.py`, `10_fetch_xbrl_geography.py`, `10_fetch_eurostat_latest.py`, `10_fetch_benchmarks.py`, `10_regional_panel.py`, `10_benchmarks.py`, `10_regional_forecast.py`. All run on `py -3.13` and rebuild every CSV below from raw inputs.

---

## Bottom line

1. **The growth engine has moved out of North America and is not coming back.** North America is ~29% of nights and 42.4% of revenue, down from 39.8% of nights in 1Q22 and 53.4% of revenue in 2021; US revenue is 39.3% of the total (2025 10-K) versus 50.0% in 2021. Latin America and Asia Pacific are 31.0% of nights but only 18.9% of revenue, so every incremental point of mix shift is dilutive to ADR and to revenue per night. In 2Q26 the four regions contributed 2.35 / 3.17 / 2.96 / 2.92 pp (NA / EMEA / LatAm / APAC) of an 11.40pp share-weighted total: **LatAm and APAC, at 31% of nights, delivered 5.88pp, or 52% of the growth.**

2. **North America's slowdown was mostly an inbound and Canada shock, and it has now reversed.** NA nights growth went mid-single (4Q24) → low-single (1Q25, 2Q25) → mid-single (3Q25, 4Q25) → high-single (1Q26, 2Q26, "the highest growth we've seen in almost three years"). The external series that moves with it is not US hotel RevPAR; it is inbound travel. BEA foreign travel in the US ran -5.7% / -9.9% / -9.4% real y/y in 2Q25-4Q25 and is back to **-0.6% in July 2026**. Canadians returning from the US collapsed to **-31% in mid-2025** and turned **positive in April 2026** (+1.8% Apr, +9.9% May, +5.0% Jun; StatCan 24-10-0053). NA revenue growth (XBRL, check-in basis) went from **+3.0% in 3Q25 to +15.8% in 2Q26**.

3. **EMEA is growing, but slower than the European platform market.** Eurostat platform nights for the EU27 have grown **5.5pp faster than ABNB's EMEA nights on average since 4Q24** (n=6; +6.4, +1.3, +12.7, +4.8, +2.9, +4.7 pp). That is a share-loss signal worth arguing about, with real caveats (different geography, nights spent vs nights booked, Easter timing, three other platforms in the Eurostat number). It is **not** a nowcast: Eurostat runs ~150 days late (data stops at March 2026 today) and its lead correlation with the next ABNB quarter is r = +0.19 (level) and -0.11 (acceleration), n=7.

4. **The regional panel reconciles.** Mapping the letters' qualitative buckets to midpoints and weighting by derived nights shares reproduces reported total nights growth within **1.1pp in every quarter since 4Q22**, with a mean residual of -0.41pp over the last four (`residual_vs_total_pp`). That is the evidence the share estimates are roughly right, and it is what makes a regional bottom-up usable.

5. **FX passes into reported ADR almost exactly one-for-one in EMEA and about 0.6:1 in LatAm.** Regressing the letters' reported-minus-ex-FX ADR gap on a currency basket for each region: EMEA slope 1.04, r 0.987, n=10; LatAm slope 0.62, r 0.996, n=7; APAC slope 0.86, r 0.972, n=5. **The 3Q26 FX picture has changed hard:** EUR is -1.6% and GBP -0.2% y/y quarter-to-date (to 28 Aug), against +11.1% and +6.9% in 1Q26. The EMEA reported-ADR tailwind is gone.

6. **The 3Q26 guide's "approximately three percentage point FX tailwind after factoring in our hedging program" is not a spot number.** The revenue-weighted spot basket is **+0.3% y/y** in 3Q26 QTD. The 3pp is hedges plus the check-in lag (revenue recognises stays booked in earlier, weaker-dollar quarters). **It rolls off in 4Q26 and FY27** — the single most under-appreciated line in the FY27 bridge.

7. **Bottom-up 3Q26 base: nights +10.3%, revenue +16.6% ($4,775m), just above the top of the $4,690-4,770m guide** — a ~1% beat versus the midpoint, exactly the size of the last two third-quarter beats (+0.9% in 3Q24 and 3Q25). **FY27 base: nights +9.2%, revenue +12.4%**, which lands on the driver model's FY27 base of +12%. Bear FY27 +4.9% (driver model bear +4%), bull +16.9% (bull +15%). The bottom-up brackets the top-down without being tuned to it.

---

## 1. What Airbnb actually discloses by region — and what it stopped disclosing

Every shareholder letter since 3Q22 carries a four-region paragraph (North America, EMEA, Latin America, Asia Pacific) with nights growth and ADR. The form changed twice:

| Period | Nights growth given as | ADR given as |
|---|---|---|
| 3Q22-3Q24 | numeric for LatAm and APAC only; NA and EMEA described qualitatively | NA and EMEA only, reported and ex-FX |
| 4Q24-2Q26 | qualitative bucket for all four ("mid-single digit", "low-20s", "approximately 20%") | all four regions, reported and ex-FX |

So there is **no quarter in which all four regions carry a hard nights number**. 4Q22-3Q24 NA and EMEA are derived here (method in §2); 4Q24 onward all four are bucket midpoints.

Series Airbnb **stopped disclosing** (each last appears in the quarter shown; all are in `10_regional_panel_quarterly.csv` up to that point):

| Series | Last disclosed | Last value |
|---|---|---|
| Cross-border share of nights | 1Q24 | 46% |
| Cross-border nights growth | 1Q24 | +10% |
| Urban share of nights | 4Q23 | 51% |
| Urban nights growth | 4Q23 | +11% |
| Long-term stay (28+ days) share | 1Q24 | 17% |

Since 1Q24 all three are qualitative only ("growth in short-term stays and entire homes… continued to outpace long-term stays and private rooms"). **Any pitch claim about cross-border or long-term-stay mix after 1Q24 is an assumption, not a disclosure.** This is a disclosure change worth flagging in the pitch's KPI section: management dropped exactly the three mix series that had been decelerating.

What replaced them: expansion-markets-versus-core language (every quarter since 1Q24, "roughly twice core" on an origin nights basis), country call-outs (Brazil, India, Japan, Mexico), first-time-booker growth (10% in 1Q26, 11% in 2Q26, "highest in four years"), and app-share of nights (64% in 2Q26 from 59%).

Every regional sentence in all 23 letters is extracted to `10_regional_quotes.csv` (766 sentences, tagged by category) so any claim here can be traced to a letter.

---

## 2. The regional panel and the reconciliation

`data/processed/overnight/10_regional_panel_quarterly.csv` — 23 quarters, 79 columns.

**Nights growth.** Numeric where the letter gives one; otherwise the bucket phrase mapped to a range (low-single 1-3, mid-single 4-6, high-single 7-9, low-double 10-12, mid-teens 14-16, high-teens 17-19, low-20s 20-23) with the midpoint used and the raw phrase kept in `*_phrase`. Basis is flagged per cell (`numeric` / `bucket` / `derived`).

**Derived NA and EMEA, 4Q22-3Q24.** Both are unknown in those quarters. They are solved so the share-weighted sum equals reported total nights growth, with the NA-minus-EMEA gap set by the XBRL regional revenue growth differential net of each region's letter ADR growth (clipped to ±12pp). Those rows carry `basis = derived (residual to total; NA-EMEA gap from XBRL revenue growth net of regional ADR)`. **Treat them as an interpolation, not a disclosure** — that is why the benchmark correlations are also run on a "disclosed only" subset that starts at 4Q24.

**Nights shares.** Estimated as trailing-four-quarter regional revenue (XBRL, check-in basis, so the four-quarter window strips the severe seasonality) divided by a regional ADR index, renormalised. The index (NA 1.42, EMEA 0.97, LatAm 0.68, APAC 0.59) is calibrated so North America averages 30% of nights in 2025 — which is exactly what the 1Q25, 2Q25 and 3Q25 letters disclose ("North America contributes approximately 30% of our Nights and Seats Booked"), and ordered as the letters describe. The derived 2025 average is **NA 31.1%**, against the disclosed ~30%.

### Regional nights growth and the reconciliation, last 8 quarters

| Quarter | Total (reported) | NA | EMEA | LatAm | APAC | NA share | EMEA share | LatAm share | APAC share | Weighted avg | Residual (pp) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3Q24 | 8.48 | 3.4* | 6.6* | 15 | 19 | 32.8 | 39.1 | 13.0 | 15.0 | 8.48 | 0.00 |
| 4Q24 | 12.35 | 5 | 11 | 21.5 | 21.5 | 32.4 | 39.1 | 13.1 | 15.4 | 12.05 | +0.30 |
| 1Q25 | 7.92 | 2 | 5 | 21.5 | 15 | 32.2 | 38.9 | 13.4 | 15.6 | 7.80 | +0.12 |
| 2Q25 | 7.43 | 2 | 5 | 18 | 15 | 31.5 | 39.2 | 13.5 | 15.8 | 7.39 | +0.04 |
| 3Q25 | 8.80 | 5 | 5 | 21.5 | 15 | 30.7 | 40.0 | 13.5 | 15.8 | 8.81 | -0.01 |
| 4Q25 | 9.82 | 5 | 8 | 18 | 15 | 30.0 | 40.0 | 14.0 | 16.1 | 9.62 | +0.20 |
| 1Q26 | 9.15 | 8 | 5 | 18 | 18 | 29.3 | 39.7 | 14.7 | 16.3 | 9.91 | -0.76 |
| 2Q26 | 10.34 | 8 | 8 | 20 | 18 | 29.3 | 39.6 | 14.8 | 16.2 | 11.40 | -1.06 |

\* derived. Shares are share of nights, %. Residual = reported total minus share-weighted regional. The residual runs -0.41pp on the last four quarters, so the bucket midpoints are mildly hot — that constant is carried explicitly into the forecast rather than hidden.

**Ex-North-America nights growth** (derived, in the panel as `ex_na_nights_yoy_est_pct`): 15.4% (4Q24), 10.6, 9.9, 10.5, 11.6, 10.7, **12.8% (2Q26)**. The one disclosed cross-check: the 1Q25 letter gives ex-NA nights growth of 11%; the panel derives 10.55%.

**Contribution to total nights growth (pp), 2Q26:** NA 2.35, EMEA 3.17, LatAm 2.96, APAC 2.92. Two years earlier (2Q24): NA 1.37, EMEA 2.22, LatAm 2.24, APAC 2.86.

---

## 3. Revenue by region and US versus international

`data/processed/overnight/10_regional_revenue_xbrl.csv` — built by parsing every 10-Q and 10-K XBRL instance from EDGAR for `RevenueFromContractWithCustomerExcludingAssessedTax` tagged on `srt:StatementGeographicalAxis` (`10_fetch_xbrl_geography.py`; raw in `10_xbrl_revenue_geography.csv`). Fourth quarters are derived as FY less 9M YTD and flagged.

### Annual revenue by region, USD m (10-K)

| Year | NA | EMEA | LatAm | APAC | NA share | US | Non-US | **US share** |
|---|---|---|---|---|---|---|---|---|
| 2021 | 3,201 | 1,931 | 431 | 429 | 53.4% | 2,996 | 2,995 | **50.0%** |
| 2022 | 4,210 | 2,924 | 643 | 622 | 50.1% | 3,890 | 4,509 | **46.3%** |
| 2023 | 4,638 | 3,615 | 824 | 840 | 46.8% | 4,290 | 5,627 | **43.3%** |
| 2024 | 5,006 | 4,135 | 969 | 992 | 45.1% | 4,640 | 6,462 | **41.8%** |
| 2025 | 5,196 | 4,729 | 1,160 | 1,156 | 42.4% | 4,814 | 7,427 | **39.3%** |

Revenue growth by region: FY25 NA **+3.8%**, EMEA +14.4%, LatAm +19.7%, APAC +16.5%. NA revenue has grown 10.2% → 7.9% → 3.8% over FY23-FY25.

Note the wedge between nights share and revenue share: LatAm and APAC are ~31% of nights but 9.5% and 9.4% of revenue respectively. That is the ADR gap doing the work, and it is the arithmetic reason total ADR ex-FX only grows 3-4% while regional ADR ex-FX grows 2-5% in every region — mix is a persistent ~1pp drag.

### Quarterly regional revenue growth (check-in basis), last 6 quarters

| Quarter | NA | EMEA | LatAm | APAC |
|---|---|---|---|---|
| 1Q25 | +3.8% | +5.3% | +11.7% | +9.9% |
| 2Q25 | +5.3% | +17.7% | +24.9% | +23.2% |
| 3Q25 | **+3.0%** | +14.1% | +18.1% | +15.7% |
| 4Q25 | +3.2% | +17.1% | +26.3% | +18.2% |
| 1Q26 | +8.0% | +25.1% | +31.5% | +23.0% |
| 2Q26 | **+15.8%** | +15.6% | +26.0% | +16.9% |

Two warnings on this table. Regional revenue is recognised at check-in and is violently seasonal (EMEA was 48.1% of regional revenue in 3Q25 and 26.3% in 1Q25), so only y/y comparisons are meaningful. And EMEA/LatAm revenue growth carries the FX translation that the nights numbers do not.

---

## 4. External benchmarks: what aligns, what does not, and when you can see it

`data/processed/overnight/10_regional_benchmarks.csv` (quarterly panel, 45 external series), `10_regional_benchmark_sources.csv` (source and publication lag per series), `10_regional_benchmark_correlations.csv` (**3,446 correlations run**: 5 targets x 45 series x 2 bases x 3 lags x 3 subsets, minus cells with n < 6).

### Publication lag is the first filter

Airbnb reports ~37 days after quarter end. A benchmark whose full quarter lands later than that cannot nowcast the quarter being reported.

| Benchmark | Full quarter public at | Usable before the print? |
|---|---|---|
| Google Trends "airbnb" | day 0 | yes |
| FX (FRED daily) | day 0 | yes |
| JNTO Japan arrivals | ~21 days | yes |
| Hilton RevPAR | ~24 days | yes |
| BEA monthly PCE travel | ~30 days | yes |
| Booking Holdings room nights | ~30 days | yes |
| Marriott RevPAR | ~33 days | yes |
| Expedia room nights | ~37 days | same day, usually |
| StatCan Canada/US travellers | ~40 days | two of three months only |
| **Eurostat platform nights** | **~150 days** | **no — a full quarter behind** |

### The correlations, honestly

On raw y/y-versus-y/y the whole panel correlates at r > 0.9 with everything, because every travel series was decaying from the same post-COVID normalisation. Those numbers are in the file, labelled `basis = level (y/y)`, and **they should not be used**. The same artefact is documented in `research/notes/2026-09-06_predictive-study.md`.

Two disciplines are applied: correlate **accelerations** (first differences of y/y), and restrict to the **post-4Q24 normalised window** (n=7). What survives:

| Target | Benchmark | Basis | Lag | n | r | Verdict |
|---|---|---|---|---|---|---|
| EMEA nights | BKNG room nights | acceleration | 0 | 7 | **+0.88** | usable, and BKNG prints ~8 days before ABNB |
| Total nights | BKNG room nights | acceleration | 0 | 7 | **+0.91** | usable, same timing |
| Total nights | EXPE room nights | acceleration | 0 | 7 | +0.78 | usable but EXPE often prints the same day |
| NA nights | US residents entering Canada | acceleration | 0 | 7 | +0.81 | plausible mechanism (cross-border North America) |
| NA nights | BEA air transportation, real | acceleration | 0 | 7 | +0.76 | monthly, published fast |
| NA nights | Canadians returning from the US | acceleration | 0 | 15 | +0.72 | the 2025-26 story in one series |
| EMEA nights | Eurostat EU27 platform nights | acceleration | +1 (lead) | 7 | **-0.11** | **no forecasting value** |
| APAC nights | JNTO Japan inbound arrivals | acceleration | 0 | 7 | -0.12 | **no relationship — see below** |
| LatAm nights | French Eurostat platform nights | acceleration | 0 | 7 | +0.95 | **spurious — no mechanism; this is the best LatAm r in the file** |

Three negatives that matter more than the positives:

- **Eurostat cannot nowcast EMEA.** It is 150 days late and its lead correlation is zero. Its value is as a share gauge (§5), not a forecast. Workstream 8's `08_eurostat_tests.csv` reaches the same conclusion from a different direction.
- **Japan inbound arrivals have decoupled from ABNB APAC.** JNTO arrivals ran +29.9% (4Q24) → +19.1% (2Q25) → +1.4% (1Q26) → **-5.3% (2Q26), +0.1% in July 2026**, driven by a collapse in Chinese arrivals (-60.7% Jan, -45.2% Feb, -55.9% Mar 2026). ABNB's APAC nights over the same span went +21.5% → +15% → +18%. **Airbnb's APAC growth is origin and domestic, not inbound-to-Japan** — India origin ~+50-60%, Japan origin high-teens, Japan domestic +27% in 3Q25. Anyone using Japan arrivals as an APAC proxy will be wrong in both directions.
- **Latin America has no external benchmark in this file, and the search demonstrates the multiple-testing hazard.** The strongest LatAm correlation across all 3,446 tests is r = +0.95 with *French* Eurostat platform nights on an acceleration basis, n = 7. There is no mechanism; it is what 3,446 tests produce. Brazil (Embratur), Mexico (DATATUR) and the STR regional RevPAR series were not obtainable programmatically in this session, and trade.gov blocks scripted access, so US NTTO monthly arrivals are absent too. LatAm forecasts here rest on the letters, FX, and the Brazil/Mexico country call-outs only. That is a real gap and it is the highest-value item to close next.

---

## 5. Drivers of the last eight quarters, by region

### North America: an inbound shock, not a demand shock

| Quarter | NA nights | NA ADR (rep.) | BEA inbound foreign travel in US, real | Canadians returning from the US | What the letter/call said |
|---|---|---|---|---|---|
| 3Q24 | ~3.4% (derived) | +3% | +9.8% | +3.9% | "continued growth" |
| 4Q24 | mid-single (5) | +3% | +5.6% | +3.0% | "an acceleration relative to Q3 2024" |
| 1Q25 | low-single (2) | +2% | -2.0% | **-14.7%** | "softness Canada to U.S. late in Q1" |
| 2Q25 | low-single (2) | +3% | **-5.7%** | **-29.2%** | "U.S. destination nights accelerated each month" |
| 3Q25 | mid-single (5) | +5% | **-9.9%** | **-31.0%** | sequential acceleration on Reserve Now Pay Later |
| 4Q25 | mid-single (5) | +5% | -9.4% | -25.0% | "domestic and longer lead times" |
| 1Q26 | high-single (8) | +7% | -6.9% | -13.6% | "modest acceleration vs Q4 2025" |
| 2Q26 | high-single (8) | +7% | **-7.1%** | **+5.6%** | "the highest growth in almost three years" |

The mechanism, and management confirms it in the 1Q26 letter: *"When tariff uncertainty resulted in fewer people traveling to the U.S. last year, they still came to Airbnb and found somewhere else to go."* Inbound-to-US demand fell (strong dollar, 2025 tariff and travel-policy headlines, and a Canadian consumer boycott that took land crossings down more than a third), and Airbnb substituted it with domestic US nights and with the same travellers booking elsewhere. That is why NA **nights** only fell to low-single digits while NA **revenue** growth fell to +3.0% — the lost nights were the high-ADR inbound ones.

The reversal is now mechanical: the Canada comparison base is -25% to -31%, so land crossings turning +5% to +10% in 2Q26 delivers a large y/y contribution with no change in underlying demand. **Monthly detail already public:** BEA inbound foreign travel real y/y Apr -13.0%, May -6.7%, Jun -1.4%, **Jul -0.6%**; BEA accommodations real Jun +1.5%, Jul +1.8%; StatCan Canadian returns Apr +1.8%, May +9.9%, Jun +5.0%.

The offset for 3Q26: management flagged on the 1Q26 call that they face **"tougher comps in the back half of this year against the rollout of Reserve Now, Pay Later"** — the product that drove the 3Q25 NA acceleration. RNPL was over 20% of total GBV in 2Q26.

### EMEA versus Eurostat

| Quarter | ABNB EMEA nights | Eurostat EU27 platform nights | Gap (pp) | EMEA ADR rep. / ex-FX |
|---|---|---|---|---|
| 4Q24 | 11 | +17.4% | +6.4 | +6% / +6% |
| 1Q25 | 5 | +6.3% | +1.3 | +2% / +4% |
| 2Q25 | 5 | +17.7% | +12.7 | +9% / +3% |
| 3Q25 | 5 | +9.8% | +4.8 | +10% / +4% |
| 4Q25 | 8 | +10.9% | +2.9 | +12% / +4% |
| 1Q26 | 5 | +9.7% | +4.7 | +15% / +4% |
| 2Q26 | 8 | n/a (Eurostat ends Mar 2026) | — | +7% / +5% |

Mean gap since 4Q24: **+5.5pp**. Caveats before anyone puts this on a slide: Eurostat `tour_ce_omr` covers Airbnb, Booking, Expedia and TripAdvisor in the EU27 only, while ABNB's EMEA includes the UK, Turkey, the Middle East and Africa; Eurostat counts nights *spent*, ABNB counts nights *booked*; and the 2Q25 gap of 12.7pp is inflated by Easter timing (Eurostat April 2025 was +34.1% against an Easter-shifted base). Even after haircutting those, the direction has been consistent for six quarters.

The two EMEA events that show up in the numbers: the **Paris 2024 Games** (3Q24 EMEA "slight acceleration, buoyed by the Paris Games", ~700k guests; the unfavourable comparison then dragged 3Q25 EMEA to mid-single), and the **Middle East conflict**, which cost approximately **100 basis points of total nights growth in 1Q26** (CFO Mertz, 1Q26 call: nights "grew 9% after accounting for an approximate 100-basis-point headwind from the conflict in the Middle East"), showed up as elevated cancellations in EMEA and APAC, and by 2Q26 was "less than we had anticipated" with "a steady recovery of demand trends within the region".

### Latin America and Asia Pacific: the engines

LatAm has printed high-teens to low-20s nights growth in **every quarter since 3Q22** — 14 consecutive quarters. Brazil origin net nights: +21% (4Q24), +27%, +18%, +21%, +21% (4Q25), +21% (1Q26), **+31% (2Q26)** — "over 20% for the third consecutive quarter" in 1Q26 and accelerating to over 30% in 2Q26, with Brazilian first-time bookers +40%. Mexico added interest-free installments in June 2026. LatAm ADR is the FX-noisiest line in the company: reported ADR was **-7%** in 1Q25 and **+10%** in 1Q26 on ex-FX moves of +2% and +3%.

APAC: mid-teens to high-teens since 4Q24, with India origin nights ~+50% (4Q25, 1Q26) and **+60% (2Q26)**, Japan domestic +21% (1Q25) and +27% (3Q25), Japan origin high-teens (2Q26). China outbound was a 2023-24 story (+100%, +90%, +80%, then +25% by 4Q24) and is now a headwind to the region's inbound-to-Japan flows.

Both regions are carried by the expansion-market playbook: origin nights in expansion markets have grown at roughly twice core markets for **ten consecutive quarters** (1Q24-2Q26). The 2Q26 twist is that core markets joined in — "net origin nights booked in the U.S., France, the U.K., and Australia all accelerated in the second quarter".

### The World Cup: a revenue event in 2Q/3Q26, a bookings event in 1Q/2Q26

This distinction decides how to read 3Q26. **Nights and Seats Booked is a bookings metric; revenue is recognised at check-in.** The 2026 World Cup ran 11 June to 19 July across 16 cities in the US, Canada and Mexico. On the 1Q26 call the CFO said that for past World Cups and Olympics "a lot of the booking activity happens close to the actual games", so the bulk of World Cup nights were **booked in 2Q26** (helping 2Q26's 10.3%) and **stayed in 2Q26 and July 2026** (helping 3Q26 revenue). 3Q26 nights booked therefore gets very little event lift and, in host markets, a modest air pocket.

Supply, by contrast, is durable: over **100,000 first-time listings** across the 16 host cities by 1Q26, **more than 150,000** by 2Q26, and management's Paris precedent is that "in excess of half" of event listings were retained six months later. The Milan-Cortina Winter Olympics (Feb 2026) delivered ~200,000 guests, host-market supply +30% and GBV "more than tripling" in host markets.

---

## 6. FX by region

`10_fx_basket.csv` (weights and currency y/y), `10_regional_adr_fx.csv` (reported vs ex-FX ADR and the basket by quarter), `10_regional_fx_passthrough.csv` (the fits).

### Basket weights (judgement, anchored on the 10-K country split and the letters' country call-outs)

| Region | Weights |
|---|---|
| NA | USD 0.90, CAD 0.08, MXN 0.02 |
| EMEA | EUR 0.62, GBP 0.25, other EUR-linked 0.08, USD 0.05 |
| LatAm | BRL 0.45, MXN 0.38, other LatAm (BRL proxy) 0.10, USD 0.07 |
| APAC | AUD 0.40, JPY 0.20, other APAC (AUD proxy) 0.15, KRW 0.10, USD 0.08, INR 0.07 |

### Pass-through into reported ADR

| Region | n | r | Slope (pp of ADR gap per pp of basket) | Basket range in sample |
|---|---|---|---|---|
| EMEA | 10 | 0.987 | **1.04** | 11.8pp |
| LatAm | 7 | 0.996 | **0.62** | 27.1pp |
| APAC | 5 | 0.972 | **0.86** | 9.0pp |
| NA | 5 | 0.849 | 3.21 — **not identified** | 1.0pp |
| Pooled | 27 | 0.953 | 0.71 | 27.1pp |

EMEA at 1.04 says the basket weights are right and translation is essentially complete. LatAm at 0.62 says roughly a third of LatAm GBV is effectively USD-linked (cross-border guests and USD-priced listings) — a useful structural fact, and it means a 10% BRL move only moves LatAm reported ADR ~6%. The NA slope is meaningless: the NA basket moves less than 1.5pp across the whole sample, so there is nothing to fit.

### Where the baskets stand now (3Q26 QTD, average to 28 Aug 2026 vs 3Q25 average)

| Region basket | 1Q26 | 2Q26 | **3Q26 QTD** |
|---|---|---|---|
| NA | +0.70% | +0.25% | **+0.02%** |
| EMEA | +9.51% | +1.93% | **-1.13%** |
| LatAm | +12.36% | +11.43% | **+6.39%** |
| APAC | +4.91% | +2.73% | **+1.47%** |
| Global, revenue-weighted | +5.60% | +2.19% | **+0.32%** |

Single currencies, 3Q26 QTD y/y: EUR -1.6%, GBP -0.2%, CAD -1.7%, BRL +6.2%, MXN +7.9%, AUD +7.5%, JPY -8.2%, KRW -4.1%, INR -8.7%.

**The gap between +0.32% spot and the guide's "approximately three percentage point FX tailwind after factoring in our hedging program" is the point.** Hedges struck in the weak-dollar first half plus check-in-basis recognition of earlier bookings are worth roughly 3pp of 3Q26 revenue growth. Neither survives into FY27 at current spot. Apply EMEA 1.04 and LatAm 0.62 pass-through to whatever FX view the model takes; do not apply a single global coefficient.

---

## 7. Forecast: 3Q26, 4Q26, FY27

`data/processed/overnight/10_regional_forecast.csv` (every cell carries its rationale and, for 3Q26, the benchmarks already public as of 6 Sep 2026). Figure: `analysis/figures/overnight/10_regional_forecast.png`.

Method: set regional nights growth in the same bucket-midpoint units the letters use; weight by nights shares extrapolated from the last four quarters' drift (NA -0.55pp/quarter, EMEA +0.10, LatAm +0.33, APAC +0.10, renormalised); add the **-0.41pp calibration** (mean 3Q25-2Q26 reconciliation residual) to get reported total nights; then nights x ADR ex-FX x FX = GBV, with take rate flat, to get revenue.

### Nights growth by region (%)

| Period | Scenario | NA | EMEA | LatAm | APAC | **Total nights** | ADR ex-FX | FX (pp on rev) | **Revenue** |
|---|---|---|---|---|---|---|---|---|---|
| 3Q26 | bear | 5 | 6 | 15 | 14 | **7.97** | 2.0 | +3.0 | **+13.1%** ($4,633m) |
| 3Q26 | **base** | **7** | **8** | **18** | **17** | **10.29** | 3.0 | +3.0 | **+16.6%** ($4,775m) |
| 3Q26 | bull | 9 | 10 | 21 | 19 | **12.44** | 4.0 | +3.5 | **+20.4%** ($4,932m) |
| 4Q26 | bear | 4 | 5 | 14 | 13 | **7.02** | 2.0 | +0.5 | **+9.7%** ($3,046m) |
| 4Q26 | **base** | **7** | **7** | **18** | **17** | **9.94** | 3.0 | +1.0 | **+14.2%** ($3,173m) |
| 4Q26 | bull | 9 | 9 | 21 | 19 | **12.09** | 4.0 | +1.5 | **+18.1%** ($3,280m) |
| FY27 | bear | 3 | 4 | 12 | 11 | **5.82** | 1.0 | -2.0 | **+4.9%** |
| FY27 | **base** | **6** | **7** | **16** | **15** | **9.15** | 3.0 | 0.0 | **+12.4%** |
| FY27 | bull | 8 | 9 | 19 | 18 | **11.48** | 4.0 | +1.0 | **+16.9%** |

### Checks

- **3Q26 guide** (2Q26 letter and call, 6 Aug 2026): revenue $4,690-4,770m, "15% to 17%" growth including ~3pp FX after hedging; GBV growth mid-teens; **low double-digit nights**; moderate ADR increase; no significant Middle East impact assumed. The base's 10.29% nights sits at the bottom of "low double-digit" and the base's $4,775m revenue sits $5m above the guide high, a **+0.95% beat versus the midpoint**. Airbnb has beaten the revenue guide midpoint by a mean 2.2% over the last 12 quarters, but by **+0.9% in each of the last two third quarters** (3Q24, 3Q25) — third quarters are guided tightest. The base is calibrated to that, not to the 12-quarter average.
- **FY26**: base implies $14,234m, **+16.3%**, meeting the raised "at least mid teens" guide.
- **FY27**: bottom-up base **+12.4%** revenue against the driver model's **+12%** base; bear +4.9% vs +4%; bull +16.9% vs +15%. Independent construction, same answer — which is a genuine cross-check, since the driver model works top-down from total nights and ADR while this works up from four regions.

### Benchmarks already public as of 6 Sep 2026 (in the CSV, per region)

- **NA**: BEA inbound foreign travel in the US real y/y Jun -1.4%, **Jul -0.6%** (3Q25 was -9.9%); BEA accommodations real Jun +1.5%, Jul +1.8%; BEA hotels and motels real Jul +2.4%; StatCan Canadian returns from the US Apr +1.8%, May +9.9%, Jun +5.0%; Google Trends "airbnb" US Jul -8.6%, Aug -4.5% y/y.
- **EMEA**: **nothing.** Eurostat ends March 2026 (1Q26 EU27 +9.7%, foreign +10.1%). The first external read on 3Q26 EMEA is Booking Holdings' late-October print, which correlates +0.88 with EMEA nights acceleration (n=7) and lands ~8 days before ABNB.
- **LatAm**: BRL +6.2% and MXN +7.9% y/y QTD against +12.3% and +12.2% in 2Q26 — the reported-ADR tailwind roughly halves. No nights benchmark exists.
- **APAC**: JNTO Japan inbound arrivals **Jul 2026 +0.1%** y/y (Jun -6.8%, May -3.6%) — a warning on inbound Japan, not on ABNB APAC (see §4). AUD +7.5%, JPY -8.2%, INR -8.7% QTD.

### The main risks to the base

- **3Q26 NA comp**: the RNPL anniversary and the World Cup bookings pull-forward could take NA back to mid-single. That is the bear's 5%.
- **3Q26 EMEA**: nothing public. A Middle East re-escalation, which cost 100bp of total nights in 1Q26, would be invisible until the print.
- **FY27 FX**: the base carries FX at zero. At current spot, the hedging and check-in tailwinds unwinding are worth roughly 3pp of revenue growth in 1H27 versus 1H26. If the dollar strengthens further, the bear's -2pp is not conservative.
- **LatAm decay**: base takes LatAm from ~20% to 16% by FY27. There is nothing in the external data to validate or refute that.

---

## Corrections to existing work

- `data/processed/overnight/05_regional_growth.csv` (workstream 5) records 2Q25 North America as "low-single digits". The 2Q25 letter says "low-single digit". Same meaning; no numeric impact.
- `data/processed/overnight/05_regional_growth.csv` records 1Q25 and 2Q25 LatAm as `22` and `18` while this panel uses `21.5` and `18` (low-20s midpoint 21.5 rather than 22). A 0.5pp convention difference, flagged so the two files reconcile.
- `data/processed/predictive/02_peer_prints.csv` carries **worldwide** Marriott and Hilton RevPAR, not regional. Any claim about regional hotel RevPAR in the pitch needs a new source; none was obtainable here.
- No error found in `10_regional_panel_quarterly.csv` as left by the earlier session; the letter quotes for 2Q26, 1Q26 and 4Q25 were re-verified line by line against `data/raw/letters/*.htm` and all matched.

## Caveats

- Bucket midpoints are the load-bearing assumption. The reconciliation residual (±1.1pp, mean -0.41pp over the last four quarters) is the honest error bar on the whole regional layer. Ranges (`*_nights_yoy_lo` / `_hi`) are in the panel; use them.
- Nights shares are estimated, not disclosed, except the ~30% North America anchor for 2025 that they are calibrated to.
- 4Q22-3Q24 NA and EMEA nights are derived from the total, so any correlation using them is partly circular. That is why `10_regional_benchmark_correlations.csv` carries a `subset` column and why every claim in §4 is quoted on the disclosed-only or post-4Q24 window.
- Fourth-quarter regional revenue is FY less 9M YTD; small rounding differences from the 10-K are possible.
- 3,446 correlations were run. Nothing in §4 is presented as a discovery; the exercise was to establish which benchmarks are usable and when, and the headline results are three negatives. The LatAm/France r = +0.95 is left in the note deliberately as the calibration for how much a single high r is worth here: nothing.

## What to build next

1. **US NTTO monthly arrivals** and **STR/CoStar regional RevPAR** — both blocked here (trade.gov blocks scripted access; STR is licensed). NTTO would sharpen the NA inbound picture by source country; STR Europe would give EMEA a fast benchmark to replace Eurostat's 150-day lag.
2. **Brazil (Embratur) and Mexico (DATATUR) arrivals**, plus a Brazilian domestic travel indicator. LatAm is 15% of nights, contributed 2.96pp of the 10.3% in 2Q26, and has zero external validation in this file.
3. **Marriott and Hilton regional RevPAR** from the quarterly press releases (US & Canada, EMEA, APAC, CALA), backfilled 2023-2026. That turns the peer file from one global number into four regional ones and would let §4 test NA and EMEA against a same-region hotel benchmark.
4. **Korea (KTO) and India (DGCA) outbound**, to test the India-origin claim that carries a third of APAC's growth.

---

## For the model

Parameters this workstream supplies to the driver model.

| Name | Value | Unit | Source |
|---|---|---|---|
| Nights share, North America (2Q26) | 29.3 | % of nights | `10_regional_panel_quarterly.csv`, calibrated to the disclosed ~30% in 1Q25-3Q25 letters |
| Nights share, EMEA (2Q26) | 39.6 | % | same |
| Nights share, LatAm (2Q26) | 14.8 | % | same |
| Nights share, APAC (2Q26) | 16.2 | % | same |
| Nights share drift | NA -0.55, EMEA +0.10, LatAm +0.33, APAC +0.10 | pp per quarter | last 4 quarters, `10_regional_forecast.py` |
| Revenue share, North America (FY25) | 42.4 | % of revenue | 2025 10-K XBRL, `10_regional_revenue_xbrl.csv` |
| Revenue share, EMEA / LatAm / APAC (FY25) | 38.6 / 9.5 / 9.4 | % | same |
| US revenue share (FY25) | 39.3 | % | same |
| Regional ADR index (NA / EMEA / LatAm / APAC) | 1.42 / 0.97 / 0.68 / 0.59 | relative ADR | `10_regional_panel.py` calibration |
| Bucket-to-total calibration | -0.41 | pp | mean reconciliation residual 3Q25-2Q26 |
| FX pass-through to reported ADR, EMEA | 1.04 (r 0.987, n 10) | pp per pp of basket | `10_regional_fx_passthrough.csv` |
| FX pass-through to reported ADR, LatAm | 0.62 (r 0.996, n 7) | pp per pp | same |
| FX pass-through to reported ADR, APAC | 0.86 (r 0.972, n 5) | pp per pp | same |
| FX pass-through to reported ADR, NA | not identified (basket range 1.0pp) | — | same |
| FX basket weights, EMEA | EUR 0.62, GBP 0.25, EUR-linked 0.08, USD 0.05 | weight | `10_fx_basket.csv` |
| FX basket weights, LatAm | BRL 0.45, MXN 0.38, BRL-proxy 0.10, USD 0.07 | weight | same |
| FX basket weights, APAC | AUD 0.40, JPY 0.20, AUD-proxy 0.15, KRW 0.10, USD 0.08, INR 0.07 | weight | same |
| FX basket weights, NA | USD 0.90, CAD 0.08, MXN 0.02 | weight | same |
| Global revenue-weighted FX basket, 3Q26 QTD | +0.32 | % y/y (USD per unit) | FRED to 28 Aug 2026 |
| Nights growth by region, 3Q26 base | NA 7, EMEA 8, LatAm 18, APAC 17 | % y/y | `10_regional_forecast.csv` |
| Nights growth by region, 4Q26 base | NA 7, EMEA 7, LatAm 18, APAC 17 | % y/y | same |
| Nights growth by region, FY27 base | NA 6, EMEA 7, LatAm 16, APAC 15 | % y/y | same |
| Total nights growth, 3Q26 / 4Q26 / FY27 base | 10.3 / 9.9 / 9.2 | % y/y | same |
| Revenue growth, 3Q26 / 4Q26 / FY27 base | 16.6 / 14.2 / 12.4 | % y/y | same |
| FY26 revenue, base | 14,234 | USD m (+16.3%) | same |

## For the 5 Nov card

1. **Guide**: revenue $4,690-4,770m (+15-17%, ~3pp FX after hedging), GBV mid-teens, nights **low double-digit**, ADR up moderately, EBITDA margin down slightly y/y, no Middle East impact assumed. FY26 revenue growth "at least mid teens", FY26 EBITDA margin "at least 35%".
2. **Our base**: nights **+10.3%**, revenue **$4,775m (+16.6%)** — a ~1% beat on the midpoint, in line with the last two third quarters (+0.9% each). Bear $4,633m (a miss below the guide low). Bull $4,932m.
3. **Regional call**: NA high-single (7%) — watch whether they say "high-single" again or slip back to mid-single on the RNPL comp; EMEA high-single (8%) with the Middle East fully recovered; LatAm high-teens to 20%; APAC high-teens.
4. **The number to look for on the call**: what happens to the **FX tailwind guidance for 4Q26**. Spot baskets say near zero. If management guides 4Q26 revenue with another 2-3pp of FX help, that is hedges and timing, and it is borrowed from FY27.
5. **Pre-print reads worth taking**: Booking Holdings prints ~28-29 Oct (room-nights acceleration correlates +0.88 with EMEA nights acceleration and +0.91 with total, n=7); Marriott ~3 Nov; BEA September PCE travel ~30 Oct; StatCan Canada travellers through August ~10 Oct. **Eurostat will tell you nothing** — it will not have 3Q26 until early 2027.
6. **The bear question to be ready for**: EU27 platform nights have outgrown ABNB EMEA by 5.5pp a quarter since 4Q24. Answer with the geography and nights-spent-vs-booked caveats, and with the 2Q26 evidence that core markets (US, France, UK, Australia) all accelerated.

---

## Files written

Data (`data/processed/overnight/`):

| File | What it is |
|---|---|
| `10_regional_panel_quarterly.csv` | 23 quarters x 79 columns: regional nights growth (numeric / bucket / derived, with lo-hi ranges and the raw phrase), regional ADR reported and ex-FX, regional revenue and shares, derived nights shares, contributions, weighted average and **reconciliation residual**, cross-border / urban / long-term-stay / expansion-market / country series, events |
| `10_regional_quotes.csv` | every regional sentence in all 23 letters, tagged by category, for audit |
| `10_regional_revenue_xbrl.csv` | quarterly (4Q derived as FY less 9M) and annual revenue by region and US vs non-US |
| `10_xbrl_revenue_geography.csv` | raw XBRL geographic revenue facts from EDGAR |
| `10_regional_benchmarks.csv` | 45 external benchmarks aligned to ABNB quarters |
| `10_regional_benchmark_sources.csv` | source and publication lag (days after quarter end) per benchmark |
| `10_regional_benchmark_correlations.csv` | 3,446 correlations: target x benchmark x level/acceleration x lag -1/0/+1 x subset, with n |
| `10_regional_forecast.csv` | 3Q26 / 4Q26 / FY27 x region x bear/base/bull, with rationale, aggregates, guide check and the public benchmarks as of 6 Sep 2026 |
| `10_regional_fx_passthrough.csv` | FX basket to reported-ADR pass-through by region (slope, r, n, basket range) |
| `10_fx_basket.csv` | regional currency weights and basket y/y for 1Q26, 2Q26, 3Q26 QTD |
| `10_regional_adr_fx.csv` | reported vs ex-FX regional ADR, FX gap and basket, by quarter |
| `10_fx_daily.csv`, `10_fx_quarterly.csv` | FRED daily FX (9 crosses, USD per unit) and quarterly averages with y/y |
| `10_eurostat_platform_monthly_latest.csv` | Eurostat platform nights, EU27 and 31 countries, monthly to Mar 2026 |
| `10_bench_japan_arrivals_monthly.csv` | JNTO Japan visitor arrivals monthly 2003-Jul 2026 |
| `10_bench_canada_travel_monthly.csv` | StatCan 24-10-0053, Canada/US travellers monthly to Jun 2026 |

Figures (`analysis/figures/overnight/`): `10_regional_nights_growth.png`, `10_regional_revenue_mix.png`, `10_regional_forecast.png`.
