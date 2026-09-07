# What Theo's alt-data cohort shows so far (first read, 2026-09-05)

**Author:** Jessie (with Claude). Reads the manifests, processed EDGAR files and the workbooks in `theos-past-research/`; nothing here required the bulk files on Theo's external volume. Charts in `analysis/figures/01–04`.

| Data | Status | What it says |
|---|---|---|
| **Thank-you reviews** (Inside Airbnb `reviews.csv.gz`, 91 markets, 50.1M reviews, all 34 US) | Downloaded, **not yet counted** | Nothing yet. One DuckDB query on Theo's drive gives reviews per market per quarter = the city-level demand proxy, US included. Ask Theo. |
| **House lists** (Inside Airbnb `listings.csv.gz`, 75 markets) | Row counts only | US: LA 43.8K, Hawaii 38.2K, NYC 30.2K (mostly unbookable shells post-LL18 — AirROI shows ~10K active), Las Vegas/Clark 20.2K, Broward 17.7K, San Diego 13.2K, Austin 11.3K, Nashville 10.2K. Globally London 92.6K, Sicily 56.9K, Puglia 48.7K, Rome 37.1K, Tokyo 34.4K, Mexico City 31.4K. |
| **City hall records** (25 municipal datasets) | Compiled in Theo's workbook (2 cities); 23 more acquired, unread | NYC enforcement 2025 vs 2024: complaints –14%, inspections +27%, summonses +31%, penalties imposed +71% ($5.6M→$9.6M), penalties paid only +22% (collection share fell to 6.6%). Vancouver STR licences: 3,248 (2018) → 6,240 (2019) → 3,887 (2021) → ~4,570 (2024) — halved by regulation, flat since. **Austin daily active-STR counts (527 dates)** acquired and unanalysed — the only true US supply time series we have. |
| **European government** (Eurostat platform nights, EU27) | Compiled monthly 2018-01 → 2026-03 | Nights booked via Airbnb/Booking/Expedia/Tripadvisor: 442M (2018) → 512M (2019) → 272M (2020) → 597M (2022) → 719M (2023, +20%) → 854M (2024, +19%) → **952M (2025, +11%)**; Jan–Mar 2026 running **+8–11%**. Growth is decelerating and now sits at roughly the pace Airbnb reports for EMEA nights (mid/high single digit) — so EMEA revenue growth of +15–25% is mostly price and FX, not volume. |
| **Money numbers** (SEC EDGAR XBRL: revenue, unearned fees) | Processed | **Unearned fees (customer prepayments for future stays) grew +0.4% YoY in Q1'26 and –0.9% in Q2'26 while GBV grew +19% / +16%.** Through 2024 the two moved together (+12–13%). The break starts Q3'25 — when Reserve Now, Pay Later launched in the US. Guests booking without paying up front means the prepaid balance no longer tracks bookings: the float that funds Airbnb's negative working capital and ~$12B cash pile is being drained relative to trend (≈$0.5B below where +16% growth would put it). Small in interest income (~$20M/yr at 4%), but it is the cleanest financial-statement fingerprint of the product change that drove the reacceleration — and the prepaid balance can no longer be used as a leading indicator of next-quarter revenue the way the earnings-call study assumed. |

## Two conclusions

1. The one European official series says Airbnb-type demand in Europe is growing ~10% and slowing, not accelerating. Airbnb's EMEA revenue acceleration is FX and price.
2. RNPL shows up in the balance sheet exactly where it should — and it means a common Airbnb tell (unearned fees as a revenue lead) is broken from Q3'25 onward. Worth a line in the model's working-capital assumptions and a question for the call: how much of the nights acceleration is RNPL pull-forward, and what happens when it laps in Q3'26?

## Sources
Eurostat `tour_ce_*` via Theo's `abnb_us_europe_guidance_comparison.xlsx`; SEC EDGAR XBRL companyfacts via `data/processed/abnb_edgar_quarterly_kpis.csv`; Inside Airbnb manifest `data/manifests/inside_airbnb_download_log.csv`; NYC OSE and Vancouver via `ABNB_edge_guidance_stock_reaction.xlsx`; Airbnb shareholder letters (GBV).
