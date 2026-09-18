# Web calls for R13 (risk-short-interest-crowding), 17 Sep 2026

WebSearch budget: 1 of 5 used for R13.

## Nasdaq API (curl, no search cost) — https://api.nasdaq.com/api/quote/ABNB/short-interest?assetclass=stocks
Pulled 2026-09-17T03:52:13Z (`nasdaq_short_interest_20260917T035213Z.json`, earlier attempt) and again 2026-09-17T08:01:27Z (`nasdaq_short_interest_20260917T080127Z.json`, this run). Latest rows: 08/31/2026 interest 14,228,547, avg daily volume 4,747,241, days to cover 2.997; 08/14/2026 12,860,433 (1.97 days); 07/31/2026 12,914,119; 07/15/2026 13,994,933. The 15 Sep 2026 settlement is not yet published (expected ~24 Sep).

## yfinance `Ticker('ABNB').info` (earlier attempt, 2026-09-17T03:52:13Z; `yfinance_info_short_20260917T035213Z.json`)
sharesShort 14,228,547 (dateShortInterest 2026-08-31); sharesShortPriorMonth 12,914,119 (2026-07-31); shortRatio 2.56; shortPercentOfFloat 0.0344; sharesPercentSharesOut 0.0241; sharesOutstanding 419,529,556 (Class A only); impliedSharesOutstanding 598,785,682; floatShares 405,782,346; currentPrice 167.51.

## MarketBeat (earlier attempt, fetched 2026-09-17; `marketbeat_short_interest_20260917.html`, 240 KB)
Embedded dollar-value short-interest series, 99 settlements 30 Sep 2021 – 31 Aug 2026 ("Percentage of Float Shorted" chart also embedded; latest 0.0326 = 3.26% of float on MarketBeat's float). Converted to shares with the repo's daily closes and to % of basic shares outstanding in `datasets/marketbeat_history.py` → `si_history_2022_2026.csv`; calibration against the repo's 84 known settlements: ratio est/known median 1.00 (the embedded value is short shares × settlement-date price).

## WebSearch 1 — "Airbnb short interest September 2026" (2026-09-17, ~08:00 UTC)
Results: SEC 10-Qs (1Q26, 2Q26); Yahoo "Airbnb Just Hit a Four-Year High. The Downgrade Says That's the Problem." (22 Aug: "Short interest sits at just 3.39% of float as of mid-August"); SEC 424B2 FY2026 (fetched below); CapEdge, Finviz, Fintel, Nasdaq short-interest pages (not fetched; the Nasdaq API is the primary). Nothing on a September change in positioning.

## WebFetch 1 — https://www.sec.gov/Archives/edgar/data/1559720/000119312526106418/d107518d424b2.htm (prospectus supplement dated 2026-03-12, fetched 2026-09-17)
Verbatim (WebFetch summary): "$850,000,000 4.400% Senior Notes due 2029", "$850,000,000 4.650% Senior Notes due 2031", "$800,000,000 5.250% Senior Notes due 2036"; "We intend to use the net proceeds from this offering for general corporate purposes including to repay our outstanding 2026 Notes, of which $2.0 billion aggregate principal amount is outstanding." Straight senior notes, not convertible — no new convertible-arbitrage hedge short was created in 2026, and the 2026 converts (the prior hedge-short source) were repaid in March 2026.

## Market cross-reference (no search cost)
Kalshi KXABNB / KXABNBA and Polymarket "airbnb" scans of this batch (`../../risk-sellside-upgrades/sources/`, 2026-09-17T03:56:27Z) and S02's (03:10Z): no market on short interest or positioning.
