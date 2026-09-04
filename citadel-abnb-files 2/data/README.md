# Data

| File | Source | Pulled by | Date | Notes |
|---|---|---|---|---|
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

`raw/` is gitignored except this log - put the actual files in the shared Drive if they're large or licensed, and record them here.
`processed/` files should be reproducible by running something in `analysis/src/`.
