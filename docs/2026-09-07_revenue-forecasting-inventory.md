# Revenue forecasting: what we hold for nights, ADR, GBV, take rate and FX (7 Sep 2026)

Compiled from origin/main at df833f5. Paths under `data/processed/overnight/` are written as `overnight/…`. Every number is quoted from a file in the tree.

## 0. The identity as the model already implements it

Revenue = Σ_region [prior-year nights × (1 + growth − regulatory drag)] × ADR ex-FX × (1 + ADR FX) = GBV; core revenue = GBV × take rate × (1 + FX timing wedge); revenue = core + new business outside GBV × take. Built quarterly 3Q26 to 4Q27 and annual FY26 to FY28 on the `Revenue` sheet of `model/ABNB_driver_model.xlsx` (rows 6-37 per case) and mirrored in `analysis/src/overnight/13_driver_model.py`. Outputs: `overnight/13_model_quarterly.csv`, `13_model_annual.csv`. Assumption table with sources: `model/assumptions.md`, section "Overnight run".

Two conventions matter. Take rate is carried on the quarterly basis (revenue / same-quarter GBV), which is strongly seasonal because revenue is recognised at check-in and GBV at booking: 2023-25 means are 9.2% (Q1), 13.1% (Q2), 18.3% (Q3), 14.0% (Q4); LTM to 2Q26 is 13.2%. Forecast quarters take the prior-year quarter plus a bps lever. Seasonality of nights is inherited by growing each quarter off its year-ago base (2023-25 shares of FY: 26.9 / 25.5 / 25.1 / 22.5%).

## 1. Historical data, by component

### Nights
- `overnight/02_kpi_panel_quarterly.csv`: 24 quarters 3Q20-2Q26, 119 columns. Total nights and y/y, regional nights y/y (NA, EMEA, LatAm, APAC, numeric where disclosed, bucket text otherwise, since 3Q22), cross-border share and growth (stopped 1Q24 at 46%), urban share (stopped 4Q23 at 51%), long-term-stay share (stopped 1Q24 at 17%), app share of nights, first-time booker growth, bedroom nights y/y (2Q26 only, +12%), active listings (stopped 4Q25), guest arrivals. `02_kpi_panel_long.csv` has the 1,050 source quotes; `02_metric_coverage.csv` says when each series starts and stops.
- `overnight/10_regional_panel_quarterly.csv`: 23 quarters, 79 columns. Regional nights low/high/mid bands, basis and phrase, nights-share estimates, contribution to total growth. Share-weighted sum reconciles to reported total within 1.1pp every quarter since 4Q22. `10_regional_quotes.csv` holds the 766 tagged letter sentences.
- `overnight/05_regional_growth.csv`: 3Q24-2Q26 regional buckets mapped to midpoints, alongside EU27 platform nights y/y.
- `overnight/05_crossborder_share.csv`: 2019 and 3Q21-1Q24 cross-border share.
- External benchmarks for nights: `10_regional_benchmarks.csv`, `10_regional_benchmark_correlations.csv` (3,446 pairs with availability lag), `10_bench_canada_travel_monthly.csv`, `10_bench_japan_arrivals_monthly.csv`, Eurostat platform nights (`eurostat_platform_nights_monthly.csv` 99 months, `_quarterly.csv` against EMEA revenue), Jessie's `eurostat_platform_vs_hotel_*` and air-traffic series (TSA, BTS, IATA, NTTO), BEA PCE travel, `abnb_kpi_vs_category_quarterly.csv`.
- Supply-side: `overnight/08_ia_dump_metrics.csv` (168 Inside Airbnb dumps, 13 cities: listings, reviews LTM and L30D, blocked share at 30/90 days), `08_ia_city_yoy.csv` on matched ids, Common Crawl survival, Theo's `booking_curves_by_market.csv` (120 markets, blocked-night rate by horizon, 25 snapshot dates but a single June 2026 vintage) and `booking_curve_daily.csv` (44,379 rows).
- Backlog: unearned fees and funds held for clients quarterly since 4Q20 (in the KPI panel and `abnb_backlog_indicators.csv`).

### ADR and FX
- KPI panel: ADR, reported y/y, ex-FX y/y (from 2Q22), `fx_pts_adr`, regional ADR reported and ex-FX (NA and EMEA from 2Q23, LatAm and APAC from 1Q25, with gaps).
- `overnight/10_fx_daily.csv` (19,467 rows, FRED bilateral rates), `10_fx_quarterly.csv`, `10_fx_basket.csv` (regional currency baskets with judgement weights and the revenue-weighted global basket), `10_regional_adr_fx.csv` (reported minus ex-FX ADR gap by region and quarter), `10_regional_fx_passthrough.csv` (pass-through of basket moves into reported ADR: EMEA 1.04, LatAm 0.62, APAC 0.86, NA not identified).
- `overnight/05_fx_fits.csv`: 26 fits of ADR FX and revenue FX on EUR/USD and broad USD at lags 0-2. ADR FX is contemporaneous (r 0.97-0.99). Revenue FX fits best on the mean of EUR/USD y/y at t-1 and t-2 (r 0.80).
- Price context for ADR ex-FX: `overnight/06_price_gap_series.csv` (CPI lodging, BEA hotel price index, STR ADR, MAR and HLT RevPAR, BKNG room nights, Inside Airbnb median prices, quarterly), `06_price_gap_monthly.csv`, `06_price_per_unit_panel.csv` (price per bedroom and per person by city and dump), `06_wtp_hedonic_coefs.csv` (extra bedroom +15.1%, capacity elasticity +0.49, rating 4.9+ premium +9.5%), `06_elasticities.csv` (25 sourced sensitivities). Jessie's party-size, stay-length and kitchen tables (in the stay-length v6 zip) give the unit-size side of ADR.

### GBV
- KPI panel: GBV, reported and ex-FX y/y from 2Q21. `abnb_revenue_decomposition.csv` splits revenue y/y 1Q22-2Q26 into nights, ADR ex-FX, FX and take-rate points (residual under 0.5pp).
- Company-stated uplifts: RNPL plus cancellation redesign plus single fee added about 3pp of nights and 4pp of GBV in 1Q26 (Mertz, in `06_elasticities.csv`); RNPL share of GBV above 20%; `overnight/08_backlog_tests.csv` shows the funds-held-to-GBV growth gap widening on RNPL (3.8pp at 2Q25, 5.2pp at 2Q26).

### Take rate
- KPI panel `take_rate_pct` quarterly; `abnb_quarterly_kpis_from_study.csv` and Jessie's `airbnb_adr_takerate_quarterly.csv` are the same series on the same basis.
- `overnight/06_fee_timeline.csv`: 19 dated fee events 2019-2026, including the single 15.5% host fee (PMS hosts from Oct 2025, over a quarter of listings by 1Q26, about half by 2Q26, most remaining hosts during 2026; Jessie's channel-fee table dates the general deadline 15 Sep 2026, EEA 13 Oct 2026).
- `overnight/06_elasticities.csv`: single-fee migration +40 to +50bps gross on a fully migrated book; the 2024 FX service fee +20bps y/y in 2025; Booking.com net take-rate ceiling about 14.5%; European managed-rental commission 15-16%.
- `overnight/06_quote_line_items.csv` and `06_quote_discount_panel.csv`: 1.71M fee-inclusive quotes Mar-Aug 2026 by city, with service-fee share of the quote and discount penetration (10.9% to 31.4% of quotes).
- Jessie: `fee_split_elasticity_scenarios.csv` (host and guest price changes, nights and revenue response, take-rate delta by elasticity), `str_channel_fee_comparison.csv`, `direct_link_leakage_sensitivity.csv` (link fee, GBV share, cannibalisation grid), `abnb_take_rate_baseline.csv`, `us_pro_managed_str_channel_mix.csv`.
- `overnight/11_new_business_scenarios.csv`: hotels, Experiences, Services, sponsored listings FY25-FY28 bear/base/bull; `11_ai_exposure_scenarios.csv` for the AI referral cost.

### Revenue, guidance and consensus
- Revenue and reported / ex-FX y/y with `fx_pts_revenue` in the KPI panel, cross-checked to XBRL (`revenue_musd_xbrl`).
- Regional revenue: `overnight/10_regional_revenue_xbrl.csv` and `10_xbrl_revenue_geography.csv` (258 rows), Jessie's `airbnb_regional_revenue_quarterly.csv` (15 quarters on a 10-Q basis). NA 42.4% of revenue and about 29% of nights; LatAm plus APAC 31% of nights and 18.9% of revenue.
- Guidance: `overnight/02_guidance_ledger.csv` (194 statements, 159 scoreable), `02_guidance_cushion_series.csv`, `02_guidance_accuracy.csv`, `02_guidance_tells.csv`, `02_fy_guide_revisions.csv`, `02_q3_2026_guide_card.csv`, `abnb_revenue_guidance_vs_actual.csv`. Quarterly revenue guide is a floor: 15 of 19 above the top of the range, none below; trailing-8 median cushion +1.79% over the midpoint. Theo's `guidance_items.csv` (100) and `quarterly_actuals.csv` (23) are the earlier schema.
- Consensus: `overnight/04_consensus_at_print.csv` and `16_consensus_at_print_merged.csv` (23 prints; revenue 23/23, next-quarter revenue 18/23, nights 18/23, GBV 12/23, ADR 5/23, from 145 sourced press quotes in `04_consensus_sources.csv`), `04_current_consensus.csv` (3-4 Sep: Q3 revenue $4,740M, Q4 $3,200M, FY26 $14.10-14.16bn, FY27 $15.73-15.76bn). Theo's `consensus_snapshots.csv` is 23 rows of "missing". The Bloomberg export on OneDrive is a revision history, not point-in-time.

### What has been tested against these series
`overnight/08_feature_tests_all.csv` (598), `05_macro_tests_all.csv` (1,408), `08_backlog_tests.csv`, `08_eurostat_tests.csv`, `08_ia_tests.csv`, `20_prediction_ledger.csv` (391), `08_test_scoreboard.csv`. Survivors on walk-forward: broad USD to ADR y/y, the fitted FX contribution to ADR FX, funds-held growth to revenue growth (slope 0.60, r 0.89, but RNPL distorts it). For nights nothing beats a naive or AR(1) baseline on both windows. Macro sensitivity of nights growth is zero at any confidence level.

## 2. Forward inputs already built

- `overnight/10_regional_forecast.csv`: nights growth by region for 3Q26, 4Q26 and FY27 in three cases, with rationale, ADR ex-FX and FX pp on revenue. Base 3Q26 NA/EMEA/LatAm/APAC 7/8/18/17, FY27 6/7/16/15.
- `overnight/05_fx_schedule.csv`: EUR/USD and broad-USD paths to 4Q27 on consensus, strong-USD and weak-USD tracks, with fitted ADR FX and revenue FX per quarter and the share of the revenue-FX driver already realised. Base revenue FX 3Q26 +3.0 (guided), 4Q26 −0.4, FY27 −0.6pp; strong USD FY27 −2.6pp.
- `overnight/05_macro_scenarios.csv` and `05_macro_sensitivities.csv`: ADR ex-FX sensitivities to airline-fare CPI (+0.067pp per 1%), Gulf jet fuel, initial claims; the 2027 airfare-lap drag on ADR ex-FX of −1.3 to −1.7pp.
- `overnight/08_q3_2026_nowcast.csv` and `08_q3_2026_guide_reconciliation.csv`: 3Q26 nights, ADR, GBV and revenue by feature, and a grid of revenue-minus-GBV gap cases against the $4,690-4,770M guide.
- `overnight/20_frozen_q3_2026.csv`: the pre-registered 5 November card (nights +10.2%, ADR +3.8%, GBV $26,185M, revenue $4,801M).
- `overnight/13_model_quarterly.csv`: base 3Q26 revenue $4,801M (+17.2%), 4Q26 $3,145M (+13.2%) against Street $3,200M, FY26 $14,233M, FY27 $15,842M, FY28 $17,947M.
- Jessie's choice-probability nights driver (stay-length v6 zip: `choice_nights_driver.py`, `docs/nights_choice_driver.xlsx`, three CSVs): US nights by party size as own-category plus hotel-contestable × P(Airbnb), calibrated on 2025 (Airbnb 10.9% of US lodging party-nights), projecting US nights +2.4 to +3.4% a year with a β sensitivity to the Airbnb-versus-hotel ADR gap. Not wired to the regional build.

## 3. Gaps and what to build

1. No quarter has hard nights numbers for all four regions; the bands are midpoints. Cross-border, urban and long-term-stay mix are assumptions after 1Q24.
2. The 3Q26 "3pp FX tailwind after hedging" is hedges plus the check-in lag against a spot basket of +0.3%. We have no hedge-book data; the 10-Q derivative disclosures have not been extracted.
3. Take rate is a bps lever. A bridge by mechanism (single-fee migration share × uplift, FX service fee, insurance, RNPL, direct-link cap, hotel and Services mix) would replace it, and every input for it is in the files above.
4. ADR ex-FX exists only from 2Q22, regional ADR ex-FX only patchily; the unit-size half of ADR growth (bedroom nights +12% vs nights +10%) has one data point.
5. Booking curves are one vintage, so no y/y; Inside Airbnb is 13 cities. The monthly capture has to start now.
6. Consensus for nights, GBV and ADR is thin; pull Zacks key metrics 2-3 days before each print.
7. FY28 has no regional or FX build; new businesses are a revenue line, not a segment.
