# London capacity extension — 7 September 2026

The verified reference is **174,384 serviced rooms across Greater London in Q1 2025**, versus **160,115 in Q1 2019**: an increase of **14,269 rooms, or 8.9%**. The GLA report was published in July 2026; it does **not** supply a 2026 capacity observation. Its geographic coverage is 32 London boroughs plus the City of London. The City of London alone has 8,598 rooms. [GLA report, printed pp. 5, 13–14 and 28–29](https://www.london.gov.uk/sites/default/files/2026-07/Visitor%20Accommodation%20in%20London%20-%202026%20report.pdf)

The extract contains 33 geographic rows at two periods, plus one London total row. Both borough sums reconcile exactly to the published totals. Definitions include hotels, B&Bs, guest houses, apart-hotels and hostels. There is no chain-affiliation filter, so this is a broad capacity reference, not independent/boutique TAM. Named property records, Airbnb allocations and observed Airbnb bookings obtained here: **zero**.

This refines the existing `HOTEL-LON` ~174,000-room anchor, using the same GLA/CoStar Q1 2025 lineage. It is neither independent corroboration nor a new growth period. The earlier source was already in the team's audit and must not be counted again. [Existing GLA source](https://data.london.gov.uk/blog/a-snapshot-of-tourist-accommodation-in-london/)

The report's separate forecasting table uses 174,471 as its 2025 baseline; that inconsistent baseline is excluded. The historical series is consistent across the main text and annex. The 66 borough-period figures are correlated capacity observations, not hotel-demand observations or evidence of statistically significant Airbnb uplift.

London is included in the user-confirmed original 13-market listing panel. The active scope is `analysis/config/hotel_markets_13.csv`; this file covers London only.

Artifacts: `data/raw/hotel_13_market_extension/london/` contains the primary PDF, text, two rendered table pages, `london_serviced_capacity_observations.csv`, metadata, source-row lineage and `extract_london_capacity.py`. Run the script from the repository root with `.venv/Scripts/python.exe`. Source ledger: `research/sources/hotel_13_london_sources.json`.

The publication landing page returned HTTP 403, but the official PDF downloaded normally with HTTP 200. A secondary page was used only to discover the official PDF URL. No secondary numerical claims were used.
