# Airbnb vs. Air Traffic — does flight volume predict ABNB?

Alt-data study for the Citadel Intercollegiate Stock Pitch Competition (ABNB pitch).
Question: is US / global / regional / destination-level air passenger traffic correlated with Airbnb's business (nights booked, gross booking value, revenue) or its stock?

**Short answer: no, not since 2024.** The apparent correlation in a longer window is an artifact of the 2023 post-COVID normalization. Airbnb has decoupled from travel volumes — it grows on share and mix, not on more people flying.

## Repo layout

```
data/processed/                       the series as CSV (every row carries its source URL)
analysis/src/                         python scripts that compute the correlations
analysis/figures/abnb_vs_air_traffic.html   chart + tables page
analysis/air_traffic_study/results.md full numeric output of the three scripts, 2026-09-04
research/notes/abnb_research_notes.md consolidated ABNB research
docs/terminal_guide.md                Bloomberg functions for the data we could not get for free
```
Run the scripts from the repo root.

Run: `python analysis/src/aggregate_correlation.py`, `python analysis/src/regional_correlation.py`, `python analysis/src/destination_snapshot.py` (needs numpy only).

## Data

| File | Series | Period | Source |
|---|---|---|---|
| `tsa_checkpoint_monthly.csv` | US TSA checkpoint travelers, monthly total (daily rows summed) | 2022-01 → 2026-06 | tsa.gov/travel/passenger-volumes (+ /2022…/2025). Sums verified vs TSA annual totals (904M 2024, 906.7M 2025) |
| `bts_us_airline_passengers_monthly.csv` | US airline systemwide passengers (millions) + reported YoY | 2022-01 → 2026-05 | bts.gov monthly "U.S. Airline Traffic Data" releases. 2022 is seasonally adjusted; 2023+ is not — level series has a break |
| `iata_rpk_yoy_monthly.csv` | Global RPK YoY %, total / international / domestic | 2023-01 → 2026-07 | IATA Air Passenger Market Analysis (monthly) |
| `iata_rpk_yoy_by_region_monthly.csv` | RPK YoY % by region of airline registration | 2024-01 → 2026-07 | IATA (same). May-24 and Nov-24 regional rows are international-only |
| `ntto_us_inbound_monthly.csv` | US international inbound arrivals YoY | 2025-01 → 2026-07 | NTTO (trade.gov); basis switches between air-only and total-volume by month — see column |
| `airbnb_quarterly_kpis.csv` | Nights & seats booked, GBV, revenue + YoY (as reported) | 2022Q1 → 2026Q2 | Airbnb shareholder letters |
| `airbnb_regional_revenue_quarterly.csv` | Revenue by listing region (NA, EMEA, LatAm, APAC), $M | 2022Q4 → 2026Q2 | Airbnb 10-Q/10-K "revenue by geographic region" (SEC R-pages). Q4s derived as FY minus 9M |
| `abnb_monthly_close.csv` | ABNB month-end close | 2021-12 → 2026-08 | Yahoo Finance |
| `destination_air_vs_str_snapshot.csv` | Latest air-arrivals YoY vs latest short-term-rental demand YoY, 9 vacation destinations | mid-2026 | DBEDT, GOAA, Harry Reid/LVCVA, ASUR, MIA, AENA, ANA, Athens Intl, JNTO; AirDNA/AirROI free pages; DBEDT vacation-rental report |

## Method

All tests use **year-over-year growth rates**, not levels, because the series are seasonally offset (TSA peaks in Q3 when people fly; Airbnb nights *booked* peak in Q1 when people book). Monthly series are averaged (YoY %) or summed (TSA counts) to quarters and matched to Airbnb's fiscal quarters. Pearson correlation, two windows: 2023Q1–2026Q2 (14 quarters) and post-normalization 2024Q1–2026Q2 (10 quarters). Stock test uses quarter-end close-to-close returns.

## Results

**1. Aggregate (US and global air traffic vs Airbnb)**

| Air series | vs nights YoY, 2023–26 | vs nights YoY, 2024–26 | vs GBV, 2024–26 | vs revenue, 2024–26 | vs stock return, 2024–26 |
|---|---|---|---|---|---|
| TSA screenings (US) | +0.84 | +0.16 | −0.17 | +0.20 | +0.03 |
| BTS US enplanements | +0.67 | +0.16 | −0.20 | +0.23 | −0.00 |
| IATA total RPK | +0.83 | +0.04 | −0.37 | +0.05 | +0.16 |
| IATA international RPK | +0.86 | +0.05 | −0.43 | −0.01 | +0.16 |

Lagging air traffic one quarter ahead of nights: r ≈ +0.5 on the full window, entirely from 2023. Levels: r = −0.09.

Interpretation: in 2023 every travel series decelerated together from the reopening spike, which manufactures a high r. From 2024 on, US screenings were flat-to-negative for six quarters, global international air demand turned negative in Q2 2026, US inbound fell most months of 2025–26 — and Airbnb nights grew 7–10% with GBV accelerating to +16–19%.

**2. Regional (Airbnb revenue by listing region vs IATA RPK by airline region, 2024Q1–2026Q2)**

| Region | quarterly r | avg air RPK YoY | avg Airbnb revenue YoY |
|---|---|---|---|
| North America | +0.20 | +2.3% | +7.1% |
| Europe / EMEA | +0.25 | +6.5% | +15.9% |
| Latin America | +0.08 | +7.8% | +20.6% |
| Asia Pacific | +0.28 | +11.5% | +17.8% |

Quarter-to-quarter, no region correlates. But the *ranking* matches: regions where air travel grows faster are regions where Airbnb grows faster (cross-sectional r = +0.81 across the four regions). Air traffic tells you *where* Airbnb's growth is, not *when* it changes. Caveat: Airbnb counts by listing location; IATA counts by airline domicile — not the same activity.

**3. Destinations (latest air-arrivals YoY vs latest STR demand YoY)**

| Destination | Air arrivals YoY | STR demand YoY (metric) |
|---|---|---|
| Hawaii | +1.2% (Jul-26) | +5.5% (official DBEDT vacation-rental unit-nights, Feb-26) |
| Orlando | −4.8% (Jun-26) | +19.3% (AirDNA occupancy, TTM) |
| Las Vegas | −9.3% (Jun-26) | −17.1% (AirDNA RevPAR, TTM) |
| Cancún | −11.5% (Jun-26) | −7.3% (AirROI STR revenue, TTM) |
| Miami | +0.5% (May-26) | +14.1% (AirDNA RevPAR, TTM) |
| Athens | +1.7% (Jun-26) | −4.6% (AirROI STR revenue, TTM) |
| Barcelona / Lisbon / Japan | +6.0% / +1.3% / −6.8% | no free STR YoY series |

Cross-sectional r = +0.49 across six destinations, same sign in 4 of 6 — but the STR metrics are not comparable (occupancy vs RevPAR vs revenue; monthly vs trailing-twelve-month) so this is suggestive at best. Where both drop (Las Vegas, Cancún) they drop together; where air is flat, STR demand can still surge (Orlando, Miami — drive-to markets).

## Caveats

- n = 10–14 quarters. These are descriptive statistics, not proof.
- Airbnb GBV and revenue YoY are as reported (FX helped 2025–26); Airbnb's ex-FX figures are in the shareholder letters if you want the cleaner series.
- BTS 2023Q1 YoY uses March only (Jan/Feb were reported vs 2020, not YoY).
- The Middle East war (from March 2026) is a large exogenous shock to IATA regional series; NTTO's inbound basis changes month to month.
- Destination STR data comes from AirDNA/AirROI free pages (trailing-twelve-month snapshots) except Hawaii, which has an official monthly government series.

## Suggested next steps

Better leading indicators for Airbnb are inside its own funnel: web/app traffic (Similarweb), listing supply growth and review velocity (Inside Airbnb), and hotel/experience listing counts by city. Flight data is best used in the pitch to show *decoupling*, not as a demand signal.

## Airbnb's biggest markets by city (added 2026-09-04)

`data/processed/top_airbnb_cities_listings_airports.csv` — AirROI active listings (Aug 2026), STR occupancy/ADR, and each city's latest airport-traffic YoY. Airbnb's largest markets are big international cities, not US vacation spots: Paris (40K active), São Paulo (34K), Rio (32K), London (31K), Rome (29K), Buenos Aires (23K), Mexico City (21K), Dubai (20K). New York has collapsed to ~10K active listings (Local Law 18), down from ~41K in 2023.

Limitation: AirROI's free city pages give levels but not YoY for most cities, so a same-metric city-level correlation could not be computed from this pull. `analysis/src/inside_airbnb_review_velocity.py` builds the consistent demand proxy (quarterly review counts per city from Inside Airbnb) — run it locally, since Inside Airbnb downloads were blocked in the environment this repo was assembled in — then join to the airport YoY column.
