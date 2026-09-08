# Party size over time: the Hawaii DBEDT series (2000–2026)

Built 7 Sep 2026. Answers "does a party-size time series exist" — Airbnb discloses none (see `party_size_distribution.md` for the fitted global distribution and the guest-arrival-milestone windows). Hawaii's visitor survey is the only public source that reports travel-party size **by accommodation type**, every year, and **monthly** for all visitors. Figure: `docs/figures/hawaii_party_size_series.png`.

## What was built

| File | Coverage | What |
|---|---|---|
| `data/processed/hawaii_party_size_annual.csv` (+ `_wide`, `_raw_vintages`) | 1999–2024, annual | Avg party size, visitors in parties of 1 / 2 / 3+, derived party shares, 3+ party size, statewide LOS — hotel-only, condo-only, timeshare-only (2004+), **rental-house-only (2013+)**, B&B-only, family, first-time / repeat, all air visitors and each MMA (to 2015) |
| `data/processed/hawaii_party_size_monthly.csv` (+ `_raw`, `_final_raw`) | Jan 2013–Jul 2026, monthly | Avg party size for all air visitors / domestic / international, visitor counts, accommodation counts (rental house from Dec 2015) |
| `analysis/src/hawaii_party_size_series.py` | | Parser: 24 annual Excel table workbooks + 19 current monthly xlsx + 165 Wayback-recovered legacy monthly/annual-highlights files (all gitignored under `data/raw/hawaii_dbedt/`) |

Party = self-reported immediate travel party of visitors arriving by air (DBEDT Visitor Characteristics survey). Reported counts are *people* in parties of 1 / 2 / 3+; parties are backed out as visitors ÷ avg party size, and the 3+ party size is solved from the mean.

## Annual: rental-house parties are growing, hotel parties are not

Avg party size (people), latest vintage:

| | 2013 | 2015 | 2017 | 2019 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| Hotel only | 2.22 | 2.25 | 2.27 | 2.29 | 2.25 | 2.26 | 2.29 | 2.30 |
| Condo only | 2.34 | 2.39 | 2.42 | 2.45 | 2.34 | 2.42 | 2.44 | 2.44 |
| Timeshare only | 2.32 | 2.38 | 2.39 | 2.41 | 2.37 | 2.38 | 2.42 | 2.42 |
| **Rental house only** | **2.28** | **2.30** | **2.35** | **2.41** | **2.30** | **2.42** | **2.46** | **2.49** |
| Rental house − hotel | +0.06 | +0.05 | +0.08 | +0.12 | +0.05 | +0.16 | +0.17 | +0.18 |
| 3+ share of parties, rental house | 27.8% | 27.8% | 29.4% | 30.8% | 28.7% | 31.9% | 32.4% | 33.5% |
| 3+ share of parties, hotel | 22.7% | 23.9% | 24.7% | 26.7% | 27.5% | 27.1% | 27.9% | 28.6% |

- In 2013 rental-house parties were the same size as hotel parties (2.28 vs 2.22) and *smaller* than condo parties. By 2024 they are the largest segment (2.49): +0.21 people in 11 years, vs +0.09 for hotels and +0.10 for condos. The gap to hotels tripled (0.06 → 0.18) and most of the widening came after 2021.
- The whole 3+ bucket drives it: 3+ parties went from 28% to 34% of rental-house parties, while solo parties fell from 33% to 29%. Hotel 3+ rose too (23% → 29%), so *all* Hawaii travel got groupier post-COVID, but rentals gained ~2 pts more.
- Hotel party size is flat over 25 years (2.13 in 1999, 2.16 in 2000, 2.30 in 2024 — most of the rise is 2019–24). The whole-market number (all air visitors) was 2.06–2.19 for 1999–2015 and 2.25–2.31 for 2024–26 (monthly-series annual means), so the market-wide lift is ~+0.1 people per party, half of the rental-house lift.
- Stay length moves the other way: rental-house LOS fell from 11.5 to 9.5 days (2013 → 2024) as the segment tripled (348k → 758k visitors), i.e. the incremental rental guest is a bigger, shorter-stay party — the same shape Airbnb's own "family travel" disclosures describe.
- Caveat: Hawaii is a couples market with a ~10-day LOS; levels do not transfer to Airbnb's global 2.97 (`party_size_distribution.md`), but *changes* in the rental-vs-hotel gap are the cleanest observed evidence there is of the group mix shifting toward rentals.

## Monthly: strong, stable seasonality; no evidence of a seasonal rental effect on party size

Seasonal index (month ÷ annual mean, 11 normal years 2013–19 & 2022–25):

| J | F | M | A | M | J | J | A | S | O | N | D |
|---|---|---|---|---|---|---|---|---|---|---|---|
| −6% | −5% | +2% | −1% | −5% | +9% | +11% | +8% | −6% | −6% | −4% | +3% |

- Summer school holidays (Jun–Aug) run 8–11% above the annual mean, Sep–Feb 4–6% below, with a March (spring break) and December bump. Domestic visitors swing more (Jul +16%, Jan −9%) than international (Aug +17%, otherwise ±4%) — the U.S. family calendar is the driver.
- Level: 2.14–2.23 for 2013–19, 1.66 in 2020, 2.15 in 2021, 2.20–2.25 in 2022–24, 2.31 in 2025 and 2.33 YTD 2026 — a step up since 2024 that the annual by-accommodation tables also show.
- Rental-house share of visitors (monthly, from Dec 2015): 7.4% (2016) → 10.0% (2019) → 12.1% (2021 peak) → 10.5–10.8% (2023–26). Monthly correlation with party size is 0.38 raw and 0.30 after removing month-of-year effects — positive but weak; the mix shift explains only a small part of month-to-month party-size variation, most of which is the holiday calendar.
- The monthly file is **not** by accommodation, so a "rental party size by month" series does not exist anywhere public; the annual tables are the only cross-tab.

## Method and data quality

- Annual tables: DBEDT Annual Visitor Research Report Excel companions 2000–2024 (2003 missing). Each report prints the year and the prior year; the prior-year column is a revision and is preferred (`_raw_vintages` keeps both; revisions are ≤0.02 people). From the 2016 report the summary and MMA tables dropped the party-size block, so the all-visitor and by-market annual series end in 2015; the monthly series carries all-visitor party size forward.
- Monthly: DBEDT Visitor Highlights xlsx. dbedt.hawaii.gov only serves Jan 2025 onward; Jan 2014–Jan 2025 monthly files and the 2013–2023 `YYYY-highlights` annual-by-month files were recovered from the Wayback Machine (`data/raw/hawaii_dbedt/monthly_legacy/download_plan.csv` records timestamp + URL). Priority: final annual-by-month value > preliminary monthly print > prior-year column of the next year's print (used for 2021, 2024–2026). Preliminary-to-final revisions average −0.01 (sd 0.06; the large ones are 2020). Party size first appears in the monthly release in Jan 2014; the 2013 values come from the 2013 annual-highlights file. Mar and Apr 2026 releases omit the characteristics table.
- Site access: Cloudflare blocks scripted downloads; the annual and 2025+ monthly files were pulled through the browser. Everything raw is gitignored; the parser rebuilds all outputs from `data/raw/hawaii_dbedt/`.

## How it plugs into the ABNB work

- Supports the bull-side line in `party_size_distribution.md` (group demand compounding toward rentals) with an observed 11-year series rather than Airbnb's marketing stats: rental parties +9% in size since 2013 vs +4% for hotels, 3+ share 34% vs 29%.
- Gives a seasonal party-size profile (±10%) for any nights-per-booking or guest-nights seasonality work — party size peaks exactly when Airbnb's Q3 nights peak, which is one reason Q3 ADR per night looks high.
- Not a proxy for Airbnb's *level* (Hawaii rental parties 2.5 vs Airbnb global ~3.0) or for regional mix outside Hawaii.

## Sources

- DBEDT annual reports index: https://dbedt.hawaii.gov/economic/tourism/annual-reports/ ; archive 2000–2023: https://dbedt.hawaii.gov/economic/tourism/tourism-archive/ (files at `files.hawaii.gov/dbedt/economic/archive/tourism/annual-reports/YYYY-annual-visitor.xls`)
- DBEDT monthly visitor statistics: https://dbedt.hawaii.gov/economic/tourism/monthly-statistics/ (`files.hawaii.gov/dbedt/economic/tourism/monthly-highlights/Mon YYYY.xlsx`)
- Legacy monthly highlights via Wayback: `files.hawaii.gov/dbedt/visitor/tourism/YYYY/MonYY.xls` (2011–2021), `.../YYYY/Mon YYYY.xlsx` (2022–Jan 2025), `.../YYYY-highlights.xls(x)` (2007–2023)
