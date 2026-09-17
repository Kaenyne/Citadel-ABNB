# Web calls for R12 (risk-sellside-upgrades), 17 Sep 2026

WebSearch budget: 1 of 5 used for R12 (the batch's final 72-hour neutral recency check, "Airbnb news past 3 days", is logged under R14 and shared).

## WebSearch 1 — "Airbnb ABNB analyst rating upgrade downgrade this week" (2026-09-17, ~08:00 UTC)
Result snippets (not fetched unless listed below): Benzinga ABNB analyst-ratings page; Investing.com "Phillip Securities downgrades Airbnb stock rating on valuation"; thecerbatgem.com "Weekly Analysts' Ratings Changes for Airbnb (ABNB)" (16 Sep, already captured by S04 in `../../sellside-mean-target-cut-by-15dec/sources/web_analyst_actions_capture_20260917.md`); dailypolitical.com weekly ratings (31 Aug); Seeking Alpha "SA analyst upgrades/downgrades: EMR, DIS, ABNB, PAYC" (undated snippet). Search-engine summary: Weiss Ratings upgraded ABNB from "hold (c+)" to "buy (b-)" on 21 Aug 2026; Phillip Securities downgraded from "hold" to "moderate sell" on 11 Aug 2026; Bernstein reaffirmed Outperform $168 (10 Aug), BMO raised to $165 Market Perform, Evercore reaffirmed Outperform $190. No rating change reported for 14–17 Sep other than the Morgan Stanley re-initiation at Equal-weight $170 (16 Sep, S04 capture).
Feed relevance: neither Weiss Ratings nor Phillip Securities (one 2024 row) is carried by the yfinance/Benzinga feed used for resolution (`datasets/feed check`, 0 and 1 rows in 469), so the Weiss upgrade would not count and the Phillip downgrade is outside the feed.

## WebFetch 1 — https://finance.yahoo.com/markets/stocks/articles/airbnb-just-hit-four-high-110129364.html (published 2026-08-22, fetched 2026-09-17)
Verbatim extracts (WebFetch summary): Phillip Securities (analyst Paul Chew) "Downgraded to Reduce", price target $158; reason: "With such a great quarter, an already expensive stock is made more expensive", AI benefits "becoming assumptions baked into the price"; "Short interest sits at just 3.39% of float as of mid-August." No Buy/Hold/Sell counts on the page.

## Market cross-reference (no WebSearch cost)
- Kalshi `markets?series_ticker=KXABNB&status=open` at 2026-09-17T03:56:27Z (`kalshi_KXABNB_20260917T035627Z.json`): seven Q3-2026 nights strikes (>138m … >150m), no market on ratings, targets or the December price.
- Polymarket `public-search?q=airbnb` at 2026-09-17T03:56:27Z (`polymarket_search_airbnb_20260917T035627Z.json`): weekly / September price-hit ladders only; nothing on analyst actions or December.
