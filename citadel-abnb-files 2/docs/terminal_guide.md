# Bloomberg terminal guide — ABNB pitch

Load the security first: type `ABNB US Equity` and press GO. Then run the functions below. Codes are from memory, not verified on a live terminal — if one errors, type the description into the command line (e.g., "alternative data") and let autocomplete find the current code.

## Fundamentals and consensus

| Function | What it gives you | Use in the pitch |
|---|---|---|
| `DES` | Company description, key stats | Sanity-check share count, market cap, EV |
| `FA` | Financial statements; segment / geography tabs | Regional revenue (compare to `data/airbnb_regional_revenue_quarterly.csv`) |
| `EE` | Consensus estimates by quarter and year | The 2026/2027 revenue, EBITDA, EPS your variant view is measured against |
| `EEB` | Estimate revisions over time | Are 2027 numbers rising or falling into the Nov print? |
| `ANR` | Analyst ratings, price targets, per-broker numbers | Where the Street sits; which brokers are at the extremes |
| `EEO` | Earnings history: beat/miss and stock reaction | Post-print behavior (Aug 7, 2026: +17%) |
| `SI` | Short interest, days to cover | Positioning (ABNB ~3% of float) |
| `OWN` / `HDS` | Holders and changes | Hedge-fund positioning shifts |
| `CF` | Company filings | 10-Q regional revenue tables, risk factors |
| `DOCV` / `CN` (filter Transcripts) | Earnings-call transcripts and news | Management language on take rate, hotels, services |

## Price and valuation

| Function | What it gives you |
|---|---|
| `GP` / `GIP` | Price chart / intraday |
| `HP` | Historical prices — export to Excel for return regressions |
| `RV` | Relative valuation vs. BKNG, EXPE (EV/EBITDA, P/E, FCF yield side by side) |
| `COMP` | Return comparison vs. peers and S&P 500 |

## Alternative data and industry (the pieces we could not get for free)

| Function | What to search | Why |
|---|---|---|
| `ALTD` | "Consumer Edge", "Earnest", "Second Measure", "Yipit" | Card-panel spend on Airbnb by income and age, and Airbnb vs. Booking/Expedia share — demographics and share-gain evidence. Availability depends on UF's entitlements. |
| `BI` | "online travel", "lodging", "short-term rental" | Bloomberg Intelligence dashboards: Airbnb nights, take rate, ADR, web traffic and listing data by market — the city-level series missing from the free sources |
| `ECO` / `ECST` | TSA throughput, consumer confidence, air passenger data | On-terminal versions of the series in `data/` |
| `SPLC` | — | Supplier/customer map (mainly useful for peers) |

## Practical notes

- Entitlements differ by school. If `ALTD` shows no card-panel datasets, ask the business-library staff which alt-data feeds UF's terminals are licensed for — this is not visible from the terminal itself.
- Export anything you use to Excel (`Actions → Export` on most screens) and drop the file into `data/` with the Bloomberg function and date in the filename, so the memo's numbers are reproducible.
- Peers to load alongside: `BKNG US Equity`, `EXPE US Equity`; for read-through timing, both report late Oct / early Nov 2026.
