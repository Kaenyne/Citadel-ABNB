# Web search and API log — C04 fy26-margin-sentence (shared with C09; run 2026-09-17, 02:40–03:10 UTC)

WebSearch budget: 4 calls used, shared across C04 and C09 (cap 5 per question).

## WebSearch 1 — "Airbnb news" (neutral pass), 2026-09-17
Results: Airbnb Newsroom, CBS tag page, PhocusWire, Yahoo ABNB news, Bloomberg, IR press releases. Snippet content: World Cup 2026 services/experiences, hotels on Airbnb, ~60,000 fake listings removed, "anticipated earnings of $2.88 per share this quarter", NYC hosts suing the city. Nothing on margin guidance. No page fetched (nothing load-bearing).

## WebSearch 2 — "Airbnb third quarter 2026 results date November", 2026-09-17
Results: Yahoo "Airbnb Set to Report Q3 Earnings" (fetched: dated 2025-11-03, about 3Q25 — STALE, zero weight), IR "Airbnb to Announce Second Quarter 2026 Results", Investing.com earnings page (fetched, see below), TipRanks, Public, Seeking Alpha, MarketScreener (3Q25 announcement). Snippet: "expected to announce Q3 2026 earnings on 11/05/2026 ... EPS GAAP estimate $2.85, revenue $4.74B".

## WebFetch — https://www.investing.com/equities/airbnb-inc-earnings, retrieved 2026-09-17
"Next Scheduled Release: Date: Nov 04, 2026; EPS Forecast: 2.86; Revenue Forecast: 4.74B". Last four quarters: 06/2026 EPS 1.37 vs 1.26, revenue 3.61B vs 3.58B; 03/2026 0.260 vs 0.310, 2.68B vs 2.62B; 12/2025 0.560 vs 0.660, 2.78B vs 2.71B; 09/2025 2.21 vs 2.31, 4.10B vs 4.08B. The date is a vendor projection; the company had not announced the 3Q26 date as of retrieval (the 2Q26 date was announced by press release in July). QUESTIONS.md convention: "if the date moves, the same event on its actual date".

## WebFetch — https://finance.yahoo.com/news/airbnb-set-report-q3-earnings-181600069.html, retrieved 2026-09-17
Publication date 2025-11-03; about the 6 Nov 2025 (3Q25) print; consensus then $4.08B / $2.29. STALE — zero weight; recorded only so the audit can see it was checked and discarded.

## WebSearch 3 — "Airbnb 2026 adjusted EBITDA margin guidance analysts expect raise", 2026-09-17
Results: SEC 8-K exhibits for the 1Q26, 2Q26 and 4Q25 letters (d23351dex991.htm, d70413dex991.htm, d58192dex991.htm — the same documents as data/raw/letters/), Yahoo 2Q26 call summary, Investing.com 2Q26 transcript, Seeking Alpha "targets at least 35% ..." (1Q26), Quartz, Simply Wall St. Snippet: "now expects ... full-year 2026 adjusted EBITDA margin of at least 35.5% ... an increase from prior guidance of 35%". No analyst expectation of a November raise found in snippets; nothing new versus the repo letters.

## WebSearch 4 — "Airbnb ABNB this week" (final 72-hour recency check), 2026-09-17
Results: CNBC quote, CNN quote, 24/7 Wall St (52-week high $187.30, older), Simply Wall St "ABNB dropped", stockanalysis, Yahoo quote, TIKR "fell 7% this week ... $155 target". Snippet: close $167.51; down 7.44% over the past week; $250M Housing Accelerator (Austin $6.4M); Morgan Stanley assumed Equal Weight; Truist and BofA Hold. Nothing on the Q3 print, the margin guide or a pre-announcement. Result: nothing that changes either number.

## Polymarket API — https://gamma-api.polymarket.com/public-search?q=Airbnb and ?q=ABNB%20earnings, fetched 2026-09-17T02:52:53Z
Saved: polymarket_search_airbnb.json, polymarket_search_abnb_earnings.json. Live ABNB events: weekly price-hit ladder "What will Airbnb (ABNB) hit Week of September 14 2026?" (e.g. HIGH $174 yes 0.095, vol24 $259; $178 yes 0.06) and the September monthly ladder ($196 yes 0.055 ... $216 0.03); "Airbnb (ABNB) Up or Down on September 16?" closed. Quarterly "beat quarterly earnings?" markets exist only for past prints (closed: 2025-11-06, 2026-02-12, 2026-05-07, 2026-08-06); the Q2 GBV ladder is closed. NO market on the FY26 margin guide, the Q4 margin sentence, or the 3Q26 print. Zero weight as an anchor; recorded for completeness.

## Kalshi API — events?status=open (3,000 events over 15 pages) and markets?series_ticker=KXABNB / KXABNBA, fetched 2026-09-17T02:53:46Z
Saved: kalshi_scan_airbnb.json, kalshi_KXABNB_markets.json, kalshi_KXABNBA_markets.json. Two Airbnb series, both on NIGHTS, none on margin:
- KXABNB-26NOVNEB "Airbnb bookings in Q3" (3Q26 nights & experiences booked): >138m bid 0.94/ask 0.97; >140m 0.89/0.96; >142m 0.84/0.92; >144m 0.76/0.83; >146m 0.63/0.66 (last 0.60); >148m 0.50/0.55 (last 0.53); >150m 0.32/0.36 (last 0.30). Volume field null. Implied median ≈148m = +10.8% y/y on 133.6m (the guide is "low double digits" = 10–12%; the team band is 8.5–10.0).
- KXABNBA-27FEBNEB fiscal-2026 nights: >565m 0.79/0.88; >570m 0.63/0.71; >575m 0.37/0.41; >580m 0.19/0.28; >585m 0.10/0.15; >590m 0.08/0.12.
Adjacent only (a Q3 nights beat raises the internal FY26 margin through revenue); no direct anchor exists for either question.

## Revision 2 additions (audit response A03, 2026-09-17, 07:57–08:10 UTC)

### Polymarket API — pagination completed (A03-15)
https://gamma-api.polymarket.com/public-search?q=Airbnb&page=1..4&limit_per_type=50, fetched 2026-09-17T07:57:07Z–07:57:15Z. Saved: polymarket_search_airbnb_page1..4_20260917T0757*.json (page 4 has hasMore=false). 190 results, 187 unique event titles. Airbnb-related open events: "What will Airbnb, Inc. (ABNB) hit Week of September 14 2026?", "What will Airbnb, Inc. (ABNB) hit in September 2026?", "Airbnb (ABNB) Up or Down on September 17?". Everything else is closed: daily Up-or-Down markets, weekly/monthly price ladders, "Will Airbnb (ABNB) beat quarterly earnings?" (past prints), "Will Airbnb (ABNB) Q2 gross booking value be above __?", "Airbnb Nights and Seats Booked above ___ in Q1?", "What will Airbnb say during their next earnings call?" (closed; a past call). None found on the FY26 margin guide, the Q4 margin sentence or 3Q26 EBITDA.

### WebSearch 5 — "Airbnb fourth quarter 2026 marketing spend margin guidance news September 2026", 2026-09-17 (A03-16; 5th and last call of the shared C04/C09 budget)
Results: SEC 8-K exhibits d70413dex991.htm (2Q26 letter) and d58192dex991.htm (4Q25 letter); news.airbnb.com Q1 2026 and Q4 2025 results pages; Motley Fool call transcripts for 4Q25 (12 Feb 2026) and 1Q26 (7 May 2026); Quartr IR summary; TIKR "Airbnb Raised Its 2026 Guidance After Q1 Revenue Grew 18%" (May 2026); the Q1 2026 shareholder letter PDF. Snippets: "at least 35%" (May), "reinvestment ... efficient marketing spend, international expansion, and AI initiatives". Nothing published in September 2026 on Q4 spend, launches, the margin guide or a pre-announcement. Recorded as a limited search that found nothing new — not as confirmation of the spending outlook.
