# Web pass, batch A10 (R04, R05, R07), 2026-09-17 ~03:30-03:45 UTC

WebSearch budget: 5 calls for the batch (two neutral queries shared by the three questions, one specific query per
question); each question therefore used at most 3 of its 5. Snippets are not sources; nothing below is load-bearing.
Market APIs (Kalshi, Polymarket) do not count against the budget; JSON saved in each question's `sources/`.

1. WebSearch "Airbnb news" (neutral pass, shared). Results: news.airbnb.com (2026 Summer Release; boutique/independent
   hotels), cbsnews.com/tag/airbnb, phocuswire.com/Airbnb, finance.yahoo.com/quote/ABNB/news, bloomberg.com/latest/airbnb-shakeup,
   investors.airbnb.com/press-releases. Snippets: ~60,000 fake listings removed; $250M Housing Accelerator (Austin $6.4M);
   "anticipated earnings of $2.88 per share this quarter, +30.3% y/y" (Zacks-style preview line). Nothing on take rate,
   Q3 margin or ADR.
2. WebSearch "Airbnb single service fee 15.5% take rate analyst revenue impact 2027" (R04). Results: smoobu.com (July 2026
   update), truvi.com, hello.pricelabs.co, rovetravel.com, airbnb.com/resources/hosting-homes/a/simplifying-service-fees-on-airbnb-771,
   airhostd.com, rield-rm.com, booktexoma.com, benzinga.com (2023). All host-facing explainers: migration waves from
   27 Oct 2025, mandatory for all hosts by end-2026, 15.5% of subtotal, hosts need +14-18% list-price increases to stay
   whole. No sell-side commentary on the 2027 revenue or take-rate effect found.
3. WebSearch "Airbnb Q3 2026 earnings preview adjusted EBITDA margin analyst expectations" (R05). Results: finance.yahoo.com
   (2Q26 beat and raise), fool.com 2Q26 transcript, gurufocus.com 2Q26 highlights, sec.gov 4Q25 8-K, investing.com 2Q26
   transcript, gurufocus "FY26 EBITDA margin of 35%" (May), news.airbnb.com 1Q26, 247wallst.com. Only restates the 6 Aug
   guide ("Adjusted EBITDA to increase year-over-year and Adjusted EBITDA Margin to be down slightly compared to Q3 2025 due
   to the timing of investments"; FY26 "at least 35.5%"). No sell-side 3Q26 margin preview found.
4. WebSearch "STR CoStar US hotel ADR week ending September 12 2026" (R07). Results: costar.com press releases (week ending
   1 Aug), asianhospitality.com, hotel-online.com ("21 weeks" Labor Day shift piece), costar.com Q2 2026 forecast assumptions,
   hoteldive.com. Latest data in results: week ending 5 Sep 2026 (published 14 Sep): occupancy 63.0% (+9.4%), ADR $159.19
   (+6.1%), RevPAR $100.31 (+16.1%), flattered by the Labor Day calendar shift. Week ending 12 Sep not yet in results. This
   matches the repo's `data/processed/q3nowcast/G/str_weekly_us_3q26.csv` last row; no new information.
5. WebSearch "Airbnb ABNB this week" (final 72-hour neutral recency check, shared, 2026-09-17). Results: investing.com quote
   ($170.65 on 15 Sep per snippet; the repo's yfinance capture has 15 Sep 168.32 and 16 Sep 167.51), cnbc.com, cnn.com,
   247wallst.com (52-week-high cards from July), simplywall.st ("down 7.44% over the past week"), stockanalysis.com,
   finance.yahoo.com. Analyst mean target $182.98 (26 buy / 3 sell). $250M Housing Accelerator. No pre-announcement,
   no guidance change, no management remark on take rate, Q3 spend or ADR. Nothing changes any of the three numbers.

Market APIs, fetched 2026-09-17T03:34:27Z (saved under each question's `sources/`):
- Kalshi KXABNB (Q3 2026 nights & experiences booked, close 2027-03-05), yes bid/ask/last: >138m 0.94/0.97/0.88, >140m 0.89/0.96/0.90,
  >142m 0.84/0.92/0.84, >144m 0.76/0.83/0.83, >146m 0.63/0.66/0.60, >148m 0.50/0.55/0.53, >150m 0.32/0.36/0.30; volume field None.
  No Kalshi market on take rate, Q3 margin/EBITDA or ADR.
- Polymarket public-search "airbnb", "Airbnb Q3", "Airbnb margin", "Airbnb ADR": only the closed Q2 GBV ladder (resolved 6 Aug),
  weekly/monthly price-hit ladders (e.g. "hit $180 in September" 0.08 on the week-of-14-Sep ladder) and a daily up/down market.
  No market on any of the three questions' objects.
