# Airbnb vs hotel: the choice data, and what's in Theo's SharePoint folder

**Author:** Jessie (with Claude). **Date:** 2026-09-06. **Status:** research notes.
**Code:** `analysis/src/listing_size_demand.py` (size-vs-demand model), `analysis/src/crowding_hotel_vs_airbnb.py` (Europe + Hawaii crowding tests), `analysis/src/eurostat_annual_platform_vs_hotel.py`, `analysis/src/hawaii_accommodation_choice.py`, `analysis/src/download_us_listings.sh`.
**Data (data/processed):** `hawaii_dbedt_2024_accommodation_by_market.csv`, `hawaii_dbedt_2024_accommodation_by_island.csv`, `hawaii_dbedt_2024_characteristics_by_accommodation.csv`, `hawaii_dbedt_2024_crowding_by_island.csv`, `eurostat_platform_vs_hotel_by_country_2019_2024.csv`, `eurostat_platform_vs_hotel_monthly_2024.csv`, `eurostat_crowding_tests_by_country_2024.csv`, `abnb_size_demand_pooled.csv`, `abnb_size_demand_pooled_us_only.csv`, `abnb_size_demand_by_market.csv`, `abnb_size_demand_5plus_by_market.csv`, `abnb_size_regression.csv`. Raw inputs (listings.csv.gz, DBEDT xlsx, Eurostat JSON) stay in gitignored `data/raw/`.

---

## 1. The honest framing first

No public dataset records an individual choosing Airbnb *instead of* a hotel. Inside Airbnb only sees the Airbnb side. So the question splits into two measurable pieces:

1. **Within Airbnb** — which listing sizes capture demand? If groups/families are the segment that leaves hotels for rentals, large listings (5+ guests, 3+ bedrooms) should take a bigger share of stays than of supply, in every market. Inside Airbnb `accommodates` and `bedrooms` answer this (section 3).
2. **Across the whole lodging market** — which visitor types stay in rentals vs hotels? Only official visitor surveys record that. Hawaii DBEDT publishes it by source market and island; NTTO's SIAT publishes it for overseas visitors to the US (section 2).

Gender: no source anywhere records lodging choice by gender. Drop it.

## 2. Survey layer — who stays in rentals (official data)

**Hawaii DBEDT, 2024 Annual Visitor Research Report** (files.hawaii.gov/dbedt/visitor/visitor-research/2024-annual-visitor.pdf; companion Excel `2024-annual-visitor.xlsx` pulled 2026-09-06; tables 43–49 give characteristics by accommodation type — see §3b). Transcribed from the narrative pages, 11 source markets and 4 islands.

| Market | Hotel % | Condo % | Rental home % | Timeshare % | Avg stay (days) | First-time % | Honeymoon % |
|---|---|---|---|---|---|---|---|
| US West | 53.2 | 15.3 | 11.8 | 9.9 | 8.40 | 18.1 | 2.0 |
| US East | 59.7 | 11.9 | 11.6 | 8.2 | 9.65 | 39.6 | 3.2 |
| Canada | 54.8 | 22.5 | 10.5 | 9.5 | 10.96 | 35.2 | 1.8 |
| Germany | 62.9 | 8.9 | 15.9 | 1.1 | 14.22 | 70.0 | 6.6 |
| Latin America | 62.0 | 8.1 | 13.5 | 1.1 | 10.57 | 68.5 | n/a |
| United Kingdom | 71.7 | 9.7 | 10.0 | 2.8 | 9.96 | 64.1 | 4.9 |
| New Zealand | 75.5 | 9.9 | 5.6 | 4.9 | 9.20 | 44.0 | 1.6 |
| Japan | 76.3 | 14.7 | n/r | 10.0 | 6.19 | 27.5 | 11.3 |
| China | 85.8 | 10.0 | 5.4 | 1.1 | 8.08 | 72.3 | 5.5 |
| Korea | 86.2 | 7.8 | 8.8 | n/r | 8.34 | 68.3 | 23.4 |
| Australia | 88.7 | 5.9 | 3.5 | 2.4 | 8.67 | 45.0 | 2.5 |

Islands (table 57–63): rental-home share Oahu 7.5% (hotel 70.2%), Maui 10.3% (50.9%), Kauai 18.2% (49.1%), Hawaii Island 18.8% (50.8%). Rentals win where hotels are scarce and trips are long/repeat (Kauai, Big Island: 74% / 70% repeat visitors); Oahu (Waikiki hotel stock, most first-timers) is hotel territory.

What moves the share, across the 11 markets (Spearman, n=11 — directional, not proof):
- **Length of stay → rentals.** Self-catering (condo + rental home) share vs avg stay: ρ = +0.65, p = 0.03. Germans (14 days) and Canadians (11 days) rent; Japanese (6 days) don't.
- **Honeymoon / first-time → hotel.** Hotel share vs honeymoon share ρ = +0.44; vs first-time share ρ = +0.43 (p ≈ 0.2). Korea (23% honeymoon) and Japan are the extreme hotel markets.
- **Repeat visitors → rentals.** US West (82% repeat) has the lowest hotel share of any market; that is the "know the destination, book a condo" behaviour Airbnb monetises.
- VFR correlates with non-hotel mechanically (they stay with friends) — ignore.

**NTTO Survey of International Air Travelers, CY2024** (overseas visitors to the US, 35.2M arrivals): hotel/motel 71.6% top accommodation; purpose vacation 56.5%, VFR 22.9%, business 16%; 59.9% travelled alone, 20.8% with spouse/partner, 17.7% with family; avg 17.5 nights. The country profiles (trade.gov Country Profile Monitor) carry the "private home / rented home or apartment" rows and party size by market — free but form-gated, pull via browser.

Read-across to ABNB: the rental-choosing traveller is **long-stay, repeat, self-organised, in a market where hotel stock is thin**. That is exactly the profile of Airbnb's strongest cohorts (28+ night stays 17–21% of nights; 4+ bedroom mix rising; drive-to and secondary markets growing fastest). The hotel-choosing traveller is **short-stay, first-time, honeymoon/MCI, urban** — the segment Airbnb is chasing with hotels-on-platform and Guest Favorites.

## 3. Inside Airbnb — size vs demand (13 markets: Austin, Twin Cities, Bozeman, London, Manchester, Bristol, Edinburgh, Milan, Bergamo, Puglia, Sicily, Menorca, Stockholm)

`analysis/src/listing_size_demand.py` over 270k listings → 147k active entire homes (snapshots Jun–Aug 2026; the 3 US files are the ones available today — Austin from Inside Airbnb, Twin Cities and Bozeman from Theo's OneDrive store; the other 31 US files still need `analysis/src/download_us_listings.sh`).

**Result — measured three ways (figure 08):**

| Guests | share of listings | share of bookings (reviews) | share of guest-stays (reviews × capacity) | share of est. revenue | revenue index |
|---|---|---|---|---|---|
| 1–2 | 21.9% | 25.7% | 11.7% | 16.7% | 0.76 |
| 3–4 | 41.7% | 41.9% | 36.3% | 34.8% | 0.83 |
| 5–6 | 23.3% | 21.0% | 27.1% | 26.9% | 1.15 |
| 7+ | 13.1% | 11.5% | 24.8% | 21.7% | 1.66 |

- Big homes get *fewer bookings per listing* (9 reviews/yr vs 12 for studios) but carry far more guests and money: 7+ guest homes are 13% of supply and ~22–25% of guest-stays and revenue. Median price per guest falls from $67 (1–2) to $39–42 (5+) — the group economics that beat two hotel rooms.
- US-only (3 markets): 7+ guest homes are 31% of supply, 55% of guest-stays, 50% of estimated revenue (revenue index 1.64). Austin's mean listing sleeps 5.9.
- Revenue index for 5+ guest homes is > 1 in **13 of 13 markets** (figure 09): Milan 1.75, London 1.51, Austin 1.36 … Menorca 1.07.
- Regression (log 1+reviews on accommodates, bedrooms, log price, min nights, multi-host, market FE; n=128,676): accommodates +0.008 per guest slot (p=0.001) after price; price elasticity of bookings −0.21; each doubling of minimum nights costs −0.66 log bookings. Bedrooms add nothing once capacity is controlled.


**Actual bookings, not listings (added later on 2026-09-06):**
- Forward calendar pickup (`analysis/src/calendar_forward_bookings_by_size.py`; 7 markets with calendar files: London, Manchester, Bristol, Edinburgh, Bergamo, Stockholm, Bozeman; 47k active entire homes). Pickup = share of the next 30 nights unavailable minus the share of nights 181–365 unavailable (host-block baseline). Per listing: 1–2 guests 24.2%, 3–4 27.8%, 5–6 30.7%, 7+ 29.4% — bigger homes book *more* nights per listing going forward, not fewer (reviews undercount them because their stays are longer). Share of forward-booked guest-nights: 5+ guest homes 49–68% in every market vs 29–48% of listings (guest-nights index 1.4× for 5–6, 2.1× for 7+). Figure 14; `data/processed/abnb_forward_bookings_*.csv`.
- Company confirmation on booked nights: "Bedroom nights booked grew 12% year over year, outpacing total nights booked" (+10%) — Chesky, Q2 2026 call, Aug 6 2026; Mertz: ADR is being driven by "the continued disproportionate popularity of larger homes" (fool.com transcript, 2026-08-13). AirDNA's Jul 8 2026 midyear outlook also notes preferences shifting toward larger homes (no size breakdown published).
- Caveat: calendar "unavailable" includes host blocks; the baseline subtraction removes most but not all. Krishang's `krish/inside-airbnb-supply` panel (168 dumps) can turn this into a time series.

What this says for the pitch: the household-sized home is the unit of Airbnb's revenue, and it is the product hotels cannot copy. Caveats: reviews ≈ 0.5 × stays and count bookings not nights; `estimated_revenue_l365d` is Inside Airbnb's model (occupancy from reviews × asking price), not observed; single vintage, so no growth claim here — Krishang's supply panel (`krish/inside-airbnb-supply`, 13 cities × 168 dumps) is where the time dimension lives.

## 3b. Crowding — does a full hotel market push people to Airbnb? (`analysis/src/crowding_hotel_vs_airbnb.py`)

**Europe, 29 countries × 12 months of 2024 (Eurostat: platform nights `tour_ce_omr`, hotel nights `tour_occ_nim`, hotel bed places `tour_cap_nat`):**
- Seasonally, yes: platform share of nights is higher in each country's three most crowded hotel months than in its three emptiest in **23 of 29 countries** (18 significant). EU27: platform share 26% in Jan → 38% in Aug while hotel bed occupancy goes 24% → 63% (figure 11). Croatia +30 pts, Slovenia +21, Lithuania +18, Denmark +15, France +13.
- The exceptions are the resort-package countries — Cyprus (−18 pts), Bulgaria, Greece, Romania, Spain — where peak season is hotel season.
- But crowding and leisure season are the same thing at this grain: with country FE, +10 pts hotel occupancy ↔ +1.4 pts platform share (p=0.13); add month FE and the effect disappears. So we cannot separate "hotels are full" from "it's summer and families travel". Say that plainly.
- Structurally, the share gain is *not* overflow: EU27 platform share rose 21.6% (2019) → 31.0% (2024) while hotel bed occupancy was flat (41.2% → 40.3%); platform nights +67%, hotel nights +2%. Cross-country, hotel occupancy barely predicts platform share (ρ +0.23, n.s.) — Croatia, France, Portugal lead because of second-home supply, not full hotels.

**Hawaii, 4 islands (DBEDT tables 8, 57–63, 105–108, 110):**

| Island | visitors/day | lodging units | visitors per unit | hotel share of units | hotel share of visitors | rental-home share | hotel occ | ADR |
|---|---|---|---|---|---|---|---|---|
| Oahu | 111,613 | 40,269 | 2.8 | 69% | 70.2% | 7.5% | 79.8% | $285 |
| Maui | 51,100 | 21,437 | 2.4 | 34% | 50.9% | 10.3% | 61.6% | $547 |
| Kauai | 28,353 | 9,142 | 3.1 | 32% | 49.1% | 18.2% | 73.2% | $415 |
| Hawaii Island | 36,740 | 11,551 | 3.2 | 50% | 50.8% | 18.8% | 67.0% | $428 |

- Where hotels are a small share of the plant (Kauai, Maui: ~1/3 of units), half of visitors still squeeze into them and the rest spill into condos and rental homes; where hotel supply is abundant (Oahu, 27.7k hotel units) rentals are 7.5%. Rental-home share is highest on the two most crowded islands (3.1–3.2 visitors per unit). n=4 — descriptive.
- DBEDT counts 17.5k "vacation rental units" statewide vs ~38k Inside Airbnb Hawaii listings: official inventory undercounts the rental stock by >2×, which is itself a data point on how much of Airbnb supply sits outside regulators' view.

**Who actually stays in a rental house vs a hotel (DBEDT tables 43–46, figure 13):** rental-house-only visitors are 58% parties of 3+ (hotel 50%), 94% independent travellers (hotel 73%, a quarter on packages), stay 9.5 days (hotel 7.3), are 1.9% honeymooners (hotel 5.1%), 1.5% meetings/conventions (hotel 6.8%), 29% first-timers (hotel 34%), average age 42.9 (hotel 44.3). Family visitors (parties with children, 2.4M): hotel 62%, rental house 12%, condo 15%.

## 4. What's in the SharePoint folder (Young, Willem K. › Citadel – ABNB)

Theo's whole data project, mirrored to Willem's UF OneDrive on 2026-09-05/06. Read through the browser; data files can't be pulled from the cloud session, only listed.

- `AIRBNB DATA/A_LEVEL_AIRBNB_DATA_EXPANSION_HANDOFF.md` — v1 baseline: 53 raw files (517 MiB), `processed/airbnb_quant_panel_v1/` (749k listing snapshots, 5.8M calendar rows, 685k review events) + DuckDB; rules (raw/ frozen, never overwrite, versioned siblings); ready-to-paste Codex prompt for an "A-level expansion agent".
- `AIRBNB DATA/CODEX_HANDOFF_V3.md` (2 hours old) — the phase-3 plan: **guidance nowcast** (predict next-quarter revenue and Nights & Seats Booked vs Street). Adds the E-series: E1 Google Trends (blocked — no browser), E2 TSA daily (2,803 rows, open), E3 lodging-tax receipts (292 rows/14 markets, the "denominator"), E3b Eurostat `tour_occ_nim` monthly hotel vs short-stay nights (40,610 rows, 53 markets), E4 hotel dashboards (via Eurostat, 7,173 rows), E5 regulatory events (206 events/31 markets), E6 App Store reviews (5,794), E7 Wikipedia pageviews (486k rows), E8 Eurostat air passengers (5,269), E9 corporate events (1,254). Corrections: the US Inside Airbnb *historical* 403 was wrong — 17/17 US markets returned 2025 snapshots, so a real US YoY panel is viable. Key trap for us: deferred revenue is contaminated by RNPL (same conclusion we reached).
- `processed/airbnb_quant_panel_v3/` — manifest lists 22 artifacts (3.4 GB DuckDB, 1.4 GB listing_snapshots, 909 MB review_events parquet, market_hotel_performance.csv 8.9 MB, market_lodging_demand.csv 43 MB, regulatory_events.csv, corporate_events.csv, geo_crosswalk.csv 116 markets) but only 4 small files had synced when read (cohort_status, demand_search_interest, market_lodging_tax, output_manifest). **`market_lodging_demand.csv` (Eurostat hotel vs short-stay nights by country-month) and `market_hotel_performance.csv` are the hotel-vs-Airbnb denominators we want — ask Theo to finish the sync or commit them.**
- `raw_expansion/v2_2026-09-05/` — eurostat, harvard_dataverse, macro, municipal (Cambridge, Colorado, Missouri, Norfolk portals), sec_edgar, zenodo. The 9.2 GB Inside Airbnb store is *not* here (SSD only).
- `raw_expansion_licensed/` — Bloomberg/FactSet exports; never commit. `ABNB_Options_Bloomberg_Pull (1).xlsx` (1.3 MB) at root — licensed, same rule.
- Folder owner is Willem (team: Jessie, Krishang, Willem, Theo); Theo uploaded everything. The OneDrive zip Jessie pulled (3.3 GB) holds only a partial Inside Airbnb store: 47 listings files, 5 countries, 2 US (Twin Cities, Bozeman).

## Sources

- Hawaii DBEDT, 2024 Annual Visitor Research Report (PDF; companion Excel). Tables 15, 17, 22, 24, 27, 28, 30, 31, 33, 34, 35, 57, 59, 62, 63.
- NTTO, Survey of International Air Travelers CY2024 inbound results (via hotel-online.com release, 2025); trade.gov/country-profile-monitor.
- Inside Airbnb, detailed listings files, 34 US markets, snapshots 2026-06-14 → 2026-08-10 (CC BY 4.0).
- Theo Brito Machado, AIRBNB DATA project handoffs (UF OneDrive, 2026-09-05/06).

- Eurostat `tour_ce_oam`, `tour_ce_omr`, `tour_occ_ninat`, `tour_occ_nim`, `tour_cap_nat` (API, fetched 2026-09-06).
- Krishang, `research/notes/2026-09-05_eu-platform-and-backlog.md` and `2026-09-05_inside-airbnb-supply-panel.md` (branches `krish/eu-platform-backlog`, `krish/inside-airbnb-supply`) — overlapping platform-nights series; this note adds the hotel side only.
