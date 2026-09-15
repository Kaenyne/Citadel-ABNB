# texas-comptroller-hotel-occupancy-tax — sample

Source repo: https://github.com/natnaelsolomon0101-sketch/tx-hotel-heatmap (pushed 22 Jul 2026, no licence file).
What it is: property-grain Texas hotel taxable room revenue from Texas Comptroller hotel occupancy tax filings, 5,141 hotels,
periods 2023 (annual), 2024Q2-2026Q1 (quarterly), 2026Q2 partial (Apr+May 2026); RevPAR per night = revenue / rooms / days.
Plus a 767-row STR/CoStar-style property list (brand, chain scale, class, submarket) merged onto part of the panel.
How pulled: file tree via `gh api .../git/trees/HEAD?recursive=1`; raw files via curl from raw.githubusercontent.com (see manifest.json
source_urls); pandas flattened hotel-history.json -> hotel_history_long.csv / hotel_history_t12.csv, hotels.geojson -> hotels_properties.csv,
TSV -> texas_hospitality_str_properties.csv. The job card's paths (data/hotels.csv, data/periods/) are gitignored upstream and do not exist.
Caps: 3.3 MB written (cap 25 MB); this IS the full committed data. Owner name/phone/contact columns were dropped (PII / possible CoStar terms).
Full dataset: the raw per-period Comptroller CSVs are not in the repo; get them from the Texas Comptroller Hotel Occupancy Tax public data
quarterly download (comptroller.texas.gov, form-driven query, history back to the 2000s) and run `node scripts/build-history.mjs`.
data.texas.gov Socrata sets (er34-v24h etc.) are city-level local-HOT reporting, a different, coarser series.
