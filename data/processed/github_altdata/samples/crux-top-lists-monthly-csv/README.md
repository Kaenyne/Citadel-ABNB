# crux-top-lists sample (zakird/crux-top-lists)

Monthly Chrome UX Report (CrUX) top-1M origin lists cached as `origin,rank` CSV.gz from Google BigQuery. Rank is a magnitude bucket (1k/5k/10k/50k/100k/500k/1M; only 1k/10k/100k/1M before 2023), random order inside a bucket. Global files run 2021-02 to 2026-08 (67 months); per-country files (238 countries) start 2025-01.

Pulled 2026-09-14 with `curl -sL` from raw.githubusercontent.com: eight global months (202102, 202201, 202301, 202401, 202501, 202601, 202608, current) and `country/us/202608`. Each raw file is ~9 MB gz / 1,000,000 rows, so the raw files were kept in the scratchpad only (25 MB cap). Stored here:

- `travel_origins_filtered.csv` (2,474 rows): every origin in those 9 files whose domain is airbnb, vrbo, booking, expedia, vacasa, hotels, agoda, tripadvisor, kayak, hostelworld, marriott, hilton, sonder, homeaway, trivago, priceline, hopper, evolve or plumguide, with scope/month/brand columns.
- `global_202608_head2000.csv`, `us_202608_head2000.csv`: first 2,000 rows of one global and one US file.

Finding: airbnb.com is in the global 5k bucket (10k pre-2023) and the US 1k bucket in every sampled month, so the bucketed rank does not move at quarterly frequency; regional origins (airbnb.fr, airbnb.co.uk, ...) and peer bucket transitions are the only variation.

Full dataset: `git clone --depth 1 --filter=blob:none --sparse https://github.com/zakird/crux-top-lists && git sparse-checkout set data/global` (~600 MB gz), or fetch single months from `https://raw.githubusercontent.com/zakird/crux-top-lists/main/data/global/YYYYMM.csv.gz` and `data/country/<cc>/YYYYMM.csv.gz`. Licence: none in repo; underlying CrUX BigQuery data is under Google's terms (CC BY 4.0 per Google docs) - confirm before publishing.
