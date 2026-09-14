# sec-cik-mapper — CIK/ticker crosswalk sample

Source: https://github.com/jadchaar/sec-cik-mapper (MIT, archived Apr 2025, last push 28 Feb 2025).
Files: mappings_stocks.csv (9,713 rows: CIK, Ticker, Name, Exchange), ticker_to_cik.json (9,713 keys), README_upstream.md (package docs).
Pulled 2026-09-14 with curl from raw.githubusercontent.com at HEAD (7883b83); no cloning, no API keys.
Caps: three files, 672 KB total, well under the 25 MB cap; nothing truncated.
Use: resolve ABNB (0001559720), BKNG, EXPE, MAR, HLT, TRIP, SOND, VCSA to CIKs for EDGAR XBRL frames / full-text search / financial-statement datasets.
Full dataset: `git clone --depth 1 https://github.com/jadchaar/sec-cik-mapper` and read mappings/stocks/ and mappings/mutual_funds/ (~1.5 MB total);
for a current snapshot use the live SEC endpoint https://www.sec.gov/files/company_tickers.json (User-Agent header required) or `pip install sec-cik-mapper`.
Caveat: frozen at Feb 2025; tickers listed/delisted since are stale.
