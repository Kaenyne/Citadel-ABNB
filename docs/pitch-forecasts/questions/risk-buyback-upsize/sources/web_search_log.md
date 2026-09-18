# R06 risk-buyback-upsize — web and API log (2026-09-17)

Budget: 5 WebSearch per question. Used: 2 (one shared recency query). Fetches (WebFetch/curl) do not count.

| # | Time (UTC) | Tool | Query / URL | Result |
|---|---|---|---|---|
| 1 | 2026-09-17T03:41:48Z | curl | https://gamma-api.polymarket.com/public-search?q=airbnb | saved `polymarket_search_airbnb_20260917T034148Z.json`. Only closed 2Q26 GBV ladders, weekly/monthly price-hit ladders (e.g. HIGH $172 week of 14 Sep 0.355, LOW $164 in September 0.76), an up/down day market. No market on buybacks, authorizations, disclosures. |
| 2 | 2026-09-17T03:41:48Z | curl | https://api.elections.kalshi.com/trade-api/v2/events?status=open&limit=200&series_ticker=KXABNB | saved `kalshi_events_KXABNB_20260917T034148Z.json`. One open event: KXABNB-26NOVNEB "Airbnb bookings in Q3". Nothing on capital return. |
| 3 | 2026-09-17T03:42:17Z | curl | https://efts.sec.gov/LatestSearch/index?q="repurchase program"&ciks=0001559720&forms=8-K | HTTP 403 (`{"message":"Forbidden"}`), saved as `edgar_fts_8k_repurchase_20260917T034217Z.json`. Full-text search blocked; fell back to the submissions index. |
| 4 | 2026-09-17T03:42:43Z | curl | https://data.sec.gov/submissions/CIK0001559720.json | saved `edgar_submissions_CIK0001559720_20260917T034243Z.json`. 8-K items since 2023: every 2.02/9.01 8-K is a print day; off-cycle 8-Ks are 5.07 (AGM), 5.02 (officers), 8.01 (2023-11-07, 2023-11-14, 2023-12-13) and 2026-03-16 (1.01/2.03: the $2.5bn notes). No off-cycle 8-K for a repurchase authorization. |
| 5 | 2026-09-17T03:44Z | WebFetch | https://news.airbnb.com/ | Newsroom to 14 Sep 2026: housing accelerator (14 Sep), Rijvers CBO (1 Sep), Q2 results (6 Aug). Nothing on repurchases or a Q3 results date. |
| 6 | 2026-09-17T03:45Z | WebSearch | `Airbnb share repurchase authorization` | Hits: Yahoo/CNBC 6 Aug 2025 ($6bn), news.airbnb.com Q2 2025 and Q1 2025 results, 10-K FY2022/FY2024/FY2025 (program has no expiration date, may be modified/suspended). Confirms the $6bn Aug 2025 program and the Feb 2024 $6bn program; nothing newer. |
| 7 | 2026-09-17T03:50Z | WebSearch (shared recency) | `Airbnb news this week` | Chesky CNBC at Goldman (AI, 80% more software, ~half of tickets by AI), Icons collection, $250M Housing Accelerator, Q2 results recap. No capital-return news in the last 72 hours. |
