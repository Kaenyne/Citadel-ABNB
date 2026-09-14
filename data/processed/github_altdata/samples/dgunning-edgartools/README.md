# dgunning/edgartools - sample (pulled 2026-09-14)

What: MIT Python client for SEC EDGAR (https://github.com/dgunning/edgartools, HEAD abe44344, 2026-09-11). No API key; SEC wants a contact string in User-Agent and <=10 req/s.
Sample here: repo README + examples/ (97 KB), one repo fixture (apple_gaap.csv, 258 facts) and an index of the 329 fixture files in data/ (320 MB, NOT copied),
plus four keyless proof pulls straight from data.sec.gov flattened to CSV: ABNB revenue facts (71 rows, periods 2019-12-31..2026-06-30, filed 2021-05..2026-08),
NCLH ContractWithCustomerLiabilityCurrent (66 rows, 2017-12-31..2026-06-30, the customer-deposit / book-ahead analogue), ABNB submissions index (1001 filings, 2023-05-01..2026-09-03),
and the list of 359 us-gaap tags in the first 5 MB of ABNB companyfacts.
How: git clone --depth 1 --filter=blob:none --sparse + sparse-checkout set examples data; curl -H 'User-Agent: citadel-abnb-research contact@example.com' on the URLs in manifest.json.
Caps: ~1.3 MB total written; companyfacts truncated with curl -r 0-4999999; nothing from data/ beyond one CSV.
Gotcha: job-card tags us-gaap:Revenues (ABNB) and DeferredRevenueCurrent (NCLH) 404 - use RevenueFromContractWithCustomerExcludingAssessedTax and ContractWithCustomerLiabilityCurrent.
Full data: pip install edgartools; Company('ABNB').get_facts() / get_filings(); or raw data.sec.gov companyfacts JSON per CIK, SEC Financial Statement Data Sets quarterly zips (2009+), full-index since 1993. Grain: entity x tag x period x accession with filed date (point-in-time).
