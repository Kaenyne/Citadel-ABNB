# Batch A14 web log (shared by B01, B02, B03), 2026-09-17

Budget: at most 5 WebSearch calls per question; batch used 6 WebSearch calls in total (three shared), 3 WebFetch, 2 curl.

| # | Tool | Query / URL (verbatim) | Charged to | Result |
|---|---|---|---|---|
| 1 | WebSearch | Airbnb news | shared (neutral pass) | Summer Release, Housing Accelerator, fake-listing removals; nothing on demand language, ADR or spending plans |
| 2 | WebSearch | Airbnb Q3 2026 earnings preview analysts expectations November | shared | 5 Nov 2026 date, EPS $2.85 projection; the Yahoo "Q3 preview" pages are the 2025 print (stale, zero weight) |
| 3 | WebSearch | STR CoStar US hotel ADR RevPAR week ending September 12 2026 | B02 | latest published week is w/e 5 Sep (ADR +6.1%, already in the repo); 12 Sep week not yet out |
| 4 | WebSearch | US travel demand consumer September 2026 hotels airlines bookings softening | B01 | NerdWallet tracker (fetched), U.S. Travel dashboard snippet ("fourth quarter room nights 1.2% behind"), "hotel prices dip this fall" (snippet); snippets zero weight |
| 5 | WebSearch | Airbnb ABNB this week | shared (final 72-hour recency check) | ABNB $170.65 on 15 Sep, -7.4% w/w; Housing Accelerator; EU STR plans; ratings; nothing that changes any number |
| 6 | WebSearch | Airbnb sales and marketing expense 2027 leverage analysts Chesky Mertz marketing spend next year launches | B03 | Marketing Week brand-vs-performance coverage; nothing on 2027 plans |
| 7 | WebFetch | https://www.costar.com/article/1169409150/adr-led-growth-extends-us-hotel-revpar-streak-as-weekday-demand-strengthens | B02 | HTTP 403 |
| 8 | WebFetch | https://www.ustravel.org/research/travel-recovery-insights-dashboard | B01 | HTTP 403; curl -A Mozilla returned a 1.1MB JS dashboard shell with no text (unusable) |
| 9 | WebFetch | https://www.nerdwallet.com/travel/learn/travel-price-tracker | B01/B02 | 11 Sep 2026, August CPI: travel costs +9% y/y, airfares +23.4%, hotel and motel rates +2.9% |
| 10 | curl | https://gamma-api.polymarket.com/public-search?q=Airbnb ; https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=100&series_ticker=KXABNB | all (2026-09-17T08:03:45Z) | saved as JSON in each question's sources/; no market on language, ADR or cost guidance; KXABNB Q3 nights ladder unchanged since 6 Aug |
