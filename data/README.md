# Data

| File | Source | Pulled by | Date | Notes |
|---|---|---|---|---|
| processed/abnb_daily_close.csv | Yahoo Finance daily closes (ABNB), via yfinance | Krish (Claude Code) | 2026-09-05 | Date, Close, 10 Dec 2020 to 4 Sep 2026 (1,440 sessions). Input to the major-moves screen. |
| processed/abnb_major_moves_events.csv | Derived from abnb_daily_close.csv plus same-day QQQ, BKNG, EXPE moves; triggers from shareholder letters, call transcripts and same-day press | Krish (Claude Code) | 2026-09-05 | 41 close-to-close moves of 7% or more, each attributed macro/industry vs company-specific with headline and KPI detail. Attribution is hand-checked, not scripted. See research/notes/2026-09-05_abnb-major-moves.md. |
| processed/abnb_earnings_reactions.csv | Theo's guidance dataset (`theos-past-research/research/guidance/data/normalized/market_returns.csv`, Nasdaq closes vs QQQ) | Krish (Claude Code) | 2026-09-05 | 1/5/20-session ABNB, QQQ and excess returns for all 23 prints Q4 2020 to Q2 2026. Rebuild with `python analysis/src/abnb_from_theo_guidance.py`. Q2 2026 20-session window incomplete at Theo's 3 Sep cutoff. |
| processed/abnb_revenue_guidance_vs_actual.csv | Theo's guidance dataset (`guidance_items.csv`, `quarterly_actuals.csv`, from SEC-filed shareholder letters) | Krish (Claude Code) | 2026-09-05 | Next-quarter revenue guide range, midpoint, actual, beat vs midpoint and vs top, Q4 2021 to Q3 2026 (20 numeric guides). Same rebuild script. |
| processed/abnb_edgar_quarterly_kpis.csv | SEC EDGAR XBRL companyfacts, CIK 1559720 | Theo (Claude Code) | 2026-09-05 | 20 quarterly revenue + 23 deferred-revenue points, 2020Q1-2026Q2. Public domain. Rebuild: `python analysis/src/acquisition/run_edgar_filings.py`. |
| processed/abnb_filing_kpis.csv | ABNB 10-Q/10-K primary documents (SEC EDGAR) | Theo (Claude Code) | 2026-09-05 | 368 KPI sentences from 14 filings 2023Q1-2026Q2, tagged nights_booked/gbv/adr/rnpl, 50 carrying figures. Evidence-grade not series-grade: the clean KPI tables are HTML tables, not prose. Public domain. |
| manifests/*.csv | Acquisition provenance for every file pulled | Theo (Claude Code) | 2026-09-05 | Append-only logs: source, URL, HTTP status, byte count, SHA-256, licence tier. Bulk data itself lives on an external volume - see below. |
| processed/booking_curves_by_market.csv | Derived from 588M Inside Airbnb calendar rows | Theo (Claude Code) | 2026-09-05 | 600 rows: blocked-night rate by market x snapshot x horizon bucket (0-30/31-60/61-90/91-180/181-372 days ahead), 120 markets, 35 countries. Rebuild: `python analysis/src/build_booking_curves.py`. **blocked_rate is a bounded proxy - `available='f'` conflates booked, host-blocked and inactive. Never call it occupancy.** |
| processed/booking_curve_daily.csv | Same source, daily granularity | Theo (Claude Code) | 2026-09-05 | 44,379 rows: blocked rate by market x snapshot x days_ahead (0-372). Same caveat. |
| processed/market_summary_2026.csv | Inside Airbnb listings, 2026 vintage (incl. frozen v1, read-only) | Theo (Claude Code) | 2026-09-05 | 120 markets: listings, hosts, entire-home/multi-host/superhost/licence-disclosure shares, median asking price (native currency, no FX), availability, review flow, ratings. Rebuild: `python analysis/src/build_market_summary.py`. |
| processed/tsa_checkpoint_monthly.csv | TSA daily checkpoint counts, summed to months (tsa.gov/travel/passenger-volumes) | Jessie (via Claude) | 2026-09-04 | 2022-01→2026-06; sums verified vs TSA annual totals |
| processed/bts_us_airline_passengers_monthly.csv | BTS monthly U.S. Airline Traffic Data releases | Jessie (via Claude) | 2026-09-04 | 2022 SA, 2023+ NSA — level break |
| processed/iata_rpk_yoy_monthly.csv | IATA Air Passenger Market Analysis (global RPK YoY) | Jessie (via Claude) | 2026-09-04 | 2023-01→2026-07 |
| processed/iata_rpk_yoy_by_region_monthly.csv | IATA regional RPK YoY (by airline registration) | Jessie (via Claude) | 2026-09-04 | 2024-01→2026-07; May/Nov-24 international-only |
| processed/ntto_us_inbound_monthly.csv | NTTO US international inbound arrivals YoY | Jessie (via Claude) | 2026-09-04 | basis varies by month (air-only vs total) |
| processed/airbnb_quarterly_kpis.csv | Airbnb shareholder letters (nights, GBV, revenue) | Jessie (via Claude) | 2026-09-04 | 2022Q1→2026Q2, as reported |
| processed/airbnb_regional_revenue_quarterly.csv | Airbnb 10-Q/10-K revenue by geographic region (SEC R-pages) | Jessie (via Claude) | 2026-09-04 | Q4s derived as FY minus 9M |
| processed/abnb_monthly_close.csv | Yahoo Finance monthly closes | Jessie (via Claude) | 2026-09-04 | 2021-12→2026-08 |
| processed/destination_air_vs_str_snapshot.csv | Airport authorities + AirDNA/AirROI/DBEDT | Jessie (via Claude) | 2026-09-04 | mixed metrics/periods — see columns |
| processed/top_airbnb_cities_listings_airports.csv | AirROI active listings + airport traffic releases | Jessie (via Claude) | 2026-09-04 | STR YoY only for NYC/LA/Sydney |
| processed/macro_us_monthly.csv | FRED monthly: Michigan sentiment, unemployment, CPI, real DPI, saving rate, fed funds, 10y yield, broad dollar index, WTI, real PCE, EUR/USD | Jessie (via Claude) | 2026-09-05 | 2021-01→2026-08 where available |
| processed/us_real_gdp_growth_quarterly.csv | FRED A191RL1Q225SBEA real GDP growth (SAAR) | Jessie (via Claude) | 2026-09-05 | 2021Q1→2026Q2 |
| processed/sp500_monthly_close.csv | Yahoo Finance ^GSPC month-end close | Jessie (via Claude) | 2026-09-05 | 2021-12→2026-08 |
| processed/airbnb_adr_takerate_quarterly.csv | ADR and quarterly take rate, from research/airbnb_earnings_call_study.md (Krishang) | Jessie (via Claude) | 2026-09-05 | 2021Q1→2026Q2 |
| processed/nyc_ose_enforcement_2024_2025.csv | NYC Office of Special Enforcement annual reports (LL18) | Jessie (Claude) | 2026-09-05 | Complaints, inspections, summonses, penalties 2024 vs 2025. |
| processed/vancouver_str_business_licences.csv | City of Vancouver open data, STR business licences | Jessie (Claude) | 2026-09-05 | Annual licence counts. |
| processed/austin_active_str_daily.csv | City of Austin Development Services, Socrata `mydx-h5dy` (Active Short Term Rental Counts) | Jessie (Claude) | 2026-09-05 | Daily total active STR licences, 2025-02-28 + 2025-03-13..2026-09-05 (527 dates). SoQL in `analysis/src/austin_str_daily.py`. Licences, not listings. Open government data. |
| processed/austin_str_by_type_monthly_raw.csv | same | Jessie (Claude) | 2026-09-05 | Sum of daily counts per month x licence type; divide by dates-in-month (script does it) for a monthly average. |
| processed/austin_str_by_type_monthly_avg.csv | derived | Jessie (Claude) | 2026-09-05 | Monthly average active licences by type. Rebuild: `python analysis/src/austin_str_daily.py`. |
| processed/austin_str_by_district_type_snapshots.csv | same Socrata dataset | Jessie (Claude) | 2026-09-05 | 2025-03-13 vs 2026-09-05, council district x licence type. |
| processed/hawaii_dbedt_2024_accommodation_by_market.csv | Hawaii DBEDT 2024 Annual Visitor Research Report (tables 15-35) | Jessie (Claude) | 2026-09-06 | Hotel/condo/timeshare/rental-home share, stay length, first-time %, purpose by source market. Public. |
| processed/hawaii_dbedt_2024_accommodation_by_island.csv | same, tables 57/59/62/63 | Jessie (Claude) | 2026-09-06 | Accommodation and purpose shares by island. |
| processed/hawaii_dbedt_2024_characteristics_by_accommodation.csv | same, tables 42-49 (companion Excel) | Jessie (Claude) | 2026-09-06 | Party size, independent vs package, stay length, purpose, age for hotel-only / condo-only / timeshare-only / rental-house-only visitors. The direct "who picks a rental" table. |
| processed/hawaii_dbedt_2024_crowding_by_island.csv | same, tables 8, 105-108 (STR), 110 (Visitor Plant Inventory) | Jessie (Claude) | 2026-09-06 | Daily visitor census, lodging units by type, hotel occupancy/ADR, derived visitors-per-unit. |
| processed/eurostat_platform_vs_hotel_by_country_2019_2024.csv | Eurostat tour_ce_oam, tour_occ_ninat (I551), tour_cap_nat (I551 bed places) | Jessie (Claude) | 2026-09-06 | Platform vs hotel nights, hotel bed occupancy, platform share, 2019 and 2024, 32 countries. Rebuild: `python analysis/src/eurostat_annual_platform_vs_hotel.py`. |
| processed/eurostat_platform_vs_hotel_monthly_2024.csv | Eurostat tour_ce_omr, tour_occ_nim (I551), tour_cap_nat | Jessie (Claude) | 2026-09-06 | Country x month 2024: platform nights, hotel nights, platform share, hotel bed occupancy. Platform-nights column overlaps Krishang's `eurostat_platform_nights_monthly.csv` (krish/eu-platform-backlog); the hotel side is new. Rebuild: `python analysis/src/crowding_hotel_vs_airbnb.py`. |
| processed/eurostat_crowding_tests_by_country_2024.csv | derived | Jessie (Claude) | 2026-09-06 | Per country: Spearman(platform share, hotel occupancy) over 12 months; share in 3 busiest vs 3 quietest hotel months. |
| processed/abnb_size_demand_pooled.csv, _pooled_us_only.csv, _by_market.csv, _5plus_by_market.csv, abnb_size_regression.csv | Inside Airbnb detailed listings, 13 markets (snapshots 2026-06-14..07-16), CC BY 4.0 | Jessie (Claude) | 2026-09-06 | Listing size (accommodates / bedrooms) vs share of bookings, guest-stays and estimated revenue; OLS with market FE. Raw files are gitignored: fetch with `analysis/src/download_us_listings.sh`, then `python analysis/src/listing_size_demand.py`. |
| processed/abnb_forward_bookings_by_size.csv, abnb_forward_bookings_pooled.csv | Inside Airbnb calendar + listings, 7 markets (Jun–Jul 2026) | Jessie (Claude) | 2026-09-06 | Forward-booking pickup (next 30 nights net of host-block baseline) by guest-capacity bucket; nights and guest-nights share vs listing share. Rebuild: `python analysis/src/calendar_forward_bookings_by_size.py`. |

`raw/` is gitignored except this log - put the actual files in the shared Drive if they're large or licensed, and record them here.
`processed/` files should be reproducible by running something in `analysis/src/`.

## Alt-data cohort (2026-09-05, Theo)

Bulk files are **not** in the repo - too large for git, per CONTRIBUTING. They live on an
external volume and are fully described by `data/manifests/`, with a SHA-256 for every file.

| Cohort | Scope | Size | Licence |
|---|---|---|---|
| Inside Airbnb current | 120 markets incl. **all 34 US**, listings + calendar + reviews (calendars are 5-col: NO price) | ~10 GB | CC BY 4.0 |
| Municipal STR registries | 25 datasets, 17 portals, 109,343 rows. Austin daily active-STR counts (527 dates); California TOT, 482 cities x 8 fiscal years | 28 MB | Open government |
| Eurostat `tour_ce_*` | Platform-sourced guest nights/stays, 32 countries, 2018-2026 monthly, NUTS 1/2/3 + cities | 6.8 MB | Eurostat re-use |
| FRED | 10 macro series incl. CPI lodging-away-from-home (ADR proxy) and trade-weighted USD | 1.1 MB | Public domain |
| SEC EDGAR | XBRL companyfacts + 14 10-Q/10-K primary documents | 20 MB | Public domain |
| Zenodo / Figshare / Dataverse | Academic replication packages | small | Per-record |

**Not committed, by design:** FactSet transcripts and Bloomberg terminal exports are licensed
and live in the private shared Drive, per CONTRIBUTING. They appear in the manifests as
references with `license_tier=licensed_norestribute` so provenance stays complete, but no
licensed content is in this public repo.

**Known blockers (lawful, not worked around):**
- Harvard Dataverse AirDNA-derived sets (Venice, Reykjavik, Boston MSA daily) require a
  Guestbook form response - must be completed manually in a browser.
- Inside Airbnb retired snapshots: ~39% return HTTP 403. Country-consistent, verified with
  paced retries as a source decision, logged and respected.
- TSA passenger volumes returns 403 to non-browser clients; FRED air revenue passenger miles
  is used instead rather than spoofing a user agent.

### Correction 2026-09-05: current calendars carry no price

Inside Airbnb's **2026** `calendar.csv.gz` has 5 columns -
`listing_id, date, available, minimum_nights, maximum_nights`. **There is no price column.**
Verified across 8 markets on 3 continents. The 2019-20 legacy files had 7 columns and did
carry price; do not generalise from them.

Consequence: **realised ADR is not obtainable** from this data. `listings.price` is an
*asking* price for a single scrape date (~76% populated, format `$1,234.56`) and must never
be presented as ADR or reconciled to the company's reported ADR without stating the gap.

What calendars DO give is a **372-day forward booking curve** per listing - see
`processed/booking_curves_by_market.csv`.

## Jessie's alt-data drop - deliberately NOT included (already covered by a teammate)

- `abnb_unearned_fees_quarterly.csv` — same numbers as the `deferred_revenue` column in Theo's `data/processed/abnb_edgar_quarterly_kpis.csv`.
- `eurostat_eu27_platform_nights_monthly.csv` — Krishang's `eurostat_platform_nights_monthly.csv` (branch `krish/eu-platform-backlog`) has the same series for every country.
- `inside_airbnb_current_listing_counts.csv` — derivable from the `row_count` column of Theo's `data/manifests/inside_airbnb_download_log.csv`.
- Raw inputs (Inside Airbnb listings.csv.gz, DBEDT xlsx, Eurostat JSON, FRED txt) — gitignored under `data/raw/`; every processed file names the script that rebuilds it.
