# ABNB-Crossover — what the SIG work already gives you for an Airbnb pitch

Built 2026-09-05 from a full read of `SIG/` (39 research reports, ~110 data files, 14 scripts, 50 transcripts, the data inventory and digest, deck skeleton and drafts) plus the cross-competition `context/` corpus. Purpose: stop you re-pulling, re-building, or re-learning anything for ABNB that the SIG project already paid for.

Everything here is one of three kinds:
- **Reuse as-is** — data or code that works for ABNB today (copied into `data/` and `tools/`).
- **Adapt** — a method, script, or template that transfers with a ticker/URL/KPI swap (pointers + what to change).
- **Idea** — an approach that worked (or failed instructively) on SIG and has a clear Airbnb analog you should consider, with the lesson attached.

Dollar signs are escaped (`\$`) so Obsidian renders the tables.

## Files in this folder

| File | What it is | Read when |
|---|---|---|
| `01_METHOD_TRANSFER_MAP.md` | Every SIG workstream → its ABNB analog, verdict (reuse / adapt / drop), effort, the SIG file to open | Planning the ABNB research sprint |
| `02_DATA_ALREADY_IN_HAND.md` | Data already on disk that is usable for ABNB, incl. the **new BEA travel-spend panel** extracted from the SIG workbook | Before pulling any macro/category series |
| `03_ACCESS_MAP.md` | Vendors, academic routes, free tiers, terminal functions — verified for SIG, with the ABNB-specific analogs (AirDNA, Inside Airbnb, STR, TSA, app trackers) | Before signing up for anything |
| `04_IDEAS_BACKLOG.md` | Ranked list of alt-data / exhibit ideas for ABNB derived from what worked on SIG, each with the SIG lesson that motivates it | Deciding what to build first |
| `05_PITCH_CRAFT_CARRYOVER.md` | The judge-tested rules from the deck-skeleton corpus and the SIG post-mortems that apply to any consumer pitch | Structuring the ABNB deck |
| `tools/TOOLS_README.md` | What each copied script does, what to change for ABNB, gotchas already hit | Before writing any scraper |
| `templates/TEMPLATES_README.md` | Schemas of the SIG CSVs worth cloning: KPI panel, bear scoreboard, print-day moves, notable-moves ledger, consensus-at-call | Setting up the ABNB data folder |
| `data/` | Copied FRED consumer-backdrop series, options-ledger baseline, SimilarWeb snapshot format, plus `bea_pce_travel_monthly_2015_2026.csv` (new) | — |
| `tools/` | 13 scripts copied verbatim from SIG (no edits; see TOOLS_README) | — |

## The ten highest-value carry-overs (in order)

1. **BEA PCE travel panel is already in hand.** The SIG workbook `bea_Section2All_underlying.xlsx` (Table 2.4.5U/2.4.6U/2.4.4U, monthly to Jul-2026) contains Accommodations, Hotels & motels, Air transportation, Package tours, Foreign travel by US residents, and inbound Foreign travel in the US. Extracted to `data/bea_pce_travel_monthly_2015_2026.csv` with nominal, real, price index, and y/y. This is the category denominator for ABNB's US business, the same role BEA jewelry played for SIG. See `02_DATA_ALREADY_IN_HAND.md`.
2. **Card-panel access map** (`SIG/research/credit_card_data.md`) — every URL verified 2026-08-29. Earnest Dash free tier, Consumer Edge academic trial, Bloomberg Second Measure via `ECAN <GO>` / `ALTD <GO>` at Hough Hall, Dewey, WRDS. ABNB is a **better** card-panel name than SIG (no in-house financing) but has its own timing caveat (card sees booking, revenue recognizes at stay). Second Measure has published ABNB-vs-VRBO pieces historically.
3. **Common Crawl scraping stack** (`tools/cc_pricing_scraper.py`, `cc_matched_sku.py`, `fetch_commoncrawl.py`) — the pattern is CDX index → range-fetch WARC → parse embedded state JSON. Airbnb listing and search pages embed JSON too. Analog: nightly rate, cleaning fee, service fee, total-price display, review count, Superhost, instant-book, by listing over time. This is the "free Evidence Lab clone" that was SIG's most differentiated exhibit.
4. **The "find the site's own search API" trick** (`tools/holiday_capture.py`) — when the site 403s scripts, the front end usually calls a public JSON search endpoint with keys embedded in the page. Airbnb's front end calls an internal GraphQL API; same idea, more fragile. Documented gotchas inside.
5. **Transcript analytics pipeline design** — analyst roster, topic frequency, congrats count, Q&A attendance as a contrarian flag, "questions management declined to answer." Method in `SIG/research/earnings_call_analyst_analysis.md` and `call_language_signal_study.md`. Transcripts came from a Bloomberg merged-PDF export at Hough Hall; ABNB has ~22 calls since the Dec-2020 IPO so it is a one-afternoon job. The parser was never saved (rebuild ~1h).
6. **Guidance-history / sandbag table** (`SIG/research/guidance_history.md`) — guided vs actual per print, raise/cut magnitudes, what the guide assumes. ABNB guides quarterly revenue, nights direction, ADR direction, adj-EBITDA margin. Same table, and the SIG finding that **the print-day move follows the guide, not the EPS surprise** is the rule to test first on ABNB.
7. **Options ledger + pre-earnings drift study** (`tools/options_ledger.py`; method in `00_MASTER_SYNTHESIS.md` §4b) — implied move, 25Δ skew vs peers, event-variance differencing; drift-vs-print correlation. Swap tickers to ABNB, BKNG, EXPE, TRIP, MAR, HLT, H, JETS.
8. **Pitch-mining method** (`SIG/research/pitch_mining_sig.md` §0 for channels; `pitch_mining_cannibals.md` for the XBRL discrimination study) — every prior writeup scored at its date's price. VIC/SumZero/Seeking Alpha RSS/Substack archive API/Google News RSS all work; AI-aggregator sites fabricate. ABNB will have far more VIC writeups than SIG did. The **buyback-vs-SBC** angle from the cannibal study is directly on point for ABNB.
9. **Google Trends and SimilarWeb, with the failure modes already learned** (`SIG/research/altdata_search_traffic.md`) — payload normalization, contamination events, the levels-vs-first-differences test that killed a 0.85 correlation, 3.4x cross-vendor disagreement on visits, free tier is 3-month aggregate not monthly. For ABNB: airbnb vs vrbo vs booking.com vs hotels.com share-of-search; and **app trackers become relevant** (they were a verified dead end for SIG, they are central for ABNB).
10. **The whole `context/` corpus and the deck skeleton Part A/B** — winning-deck exhibit frequencies, judge Q&A patterns, format norms, the "market hunts the disqualifier" rule, quantified-not-listed risks. Summarized in `05_PITCH_CRAFT_CARRYOVER.md`.

## What does NOT transfer (so you don't look for it)

- Every jewelry-specific series: LGD wholesale (Golan/IDEX/RAPI/StoneAlgo/GJEPC), gold ledger and hedge book, Tenoris and Edge POS panels, wedding studies, marriage rates, De Beers/Anglo, tariff/HTSUS work, Placer mall indices, promo-depth parsing rules. Only their *methods* carry.
- The SIG Screener row: ABNB is not in the Screener universe (grep of `C:\Users\krish\Screener\output` returns nothing, presumably the cap band), so the reverse-DCF "what's priced in" exhibit has to be computed fresh for ABNB. The method is in `context/PITCH_SIGNAL_BACKLOG.md` Tier 1 #1.
- `Bloomberg_Context.md` at the project root is a teammate's corn-futures memo, unrelated to either name.

## Where ABNB differs structurally from SIG (keep in mind while adapting)

| Dimension | SIG | ABNB | Consequence |
|---|---|---|---|
| Fiscal year | ends ~Feb 1; Q2 = May–Jul | calendar year; Q3 = Jul–Sep, print early Nov (verify date) | Re-map every quarter helper (`fq_of` in `forward_exhibits.py`) |
| Physical footprint | ~2,300 doors | none | Foot traffic, store walks, mall indices drop out; supply is *listings* (Inside Airbnb / AirDNA) |
| Revenue timing | at sale | at check-in; GBV at booking | Card panels and search lead revenue by weeks-to-months — a feature if you model it, a trap if you don't |
| Coverage | ~9 analysts, under-owned | ~40 analysts, mega-cap, heavily owned | "Neglect" leg unavailable; edge must be mechanism + measurement, not discovery |
| Bear corpus | 2 institutional shorts | Deep bear literature (take-rate, regulation, hotel re-acceleration, SBC) | Pitch-mining will be the longest workstream; the bear scoreboard template is the payoff |
| App | none (verified) | core distribution channel | App trackers (Sensor Tower free tier, Appfigures) move from "dead end" to "tier 1" |
| Regulatory | tariffs (Federal Register API) | city STR ordinances (NYC LL18, Barcelona, etc.) | Same discipline — primary legal text with dates — different sources |

## Suggested first week for ABNB, using only what is here

1. Copy `templates/kpi_panel_quarterly.csv` schema → build the ABNB KPI panel (nights, GBV, ADR, take rate, revenue, adj EBITDA, FCF, SBC, buybacks, share count) from the ~22 shareholder letters. Same day: guidance-history table.
2. Run `tools/options_ledger.py` with ABNB peers; run the print-day reaction and drift study on ABNB daily prices (yfinance, same CSV schema as `sig_prices_daily.csv`).
3. Pull Google Trends share-of-search (airbnb / vrbo / booking.com / hotels.com / expedia) with the `pytrends` patch from `altdata_search_traffic.md` §1.1; run the first-differences test before believing anything.
4. Sign up: Earnest Dash (free), Consumer Edge academic trial, Sensor Tower / Appfigures free tiers, Inside Airbnb download, AlphaSense trial timed to the sprint. Book Hough Hall terminal time for `ECAN`, `ALTD`, transcripts export, UBS Evidence Lab notes on ABNB.
5. Pitch-mine: VIC + Seeking Alpha RSS + Substack for every ABNB writeup since IPO; score each at its date's price; start the bear scoreboard.
6. Prototype the Common Crawl listing scrape on one city for one crawl to see what JSON Airbnb pages carry in the archive before committing.
