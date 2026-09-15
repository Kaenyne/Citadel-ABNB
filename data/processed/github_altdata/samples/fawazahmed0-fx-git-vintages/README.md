# fawazahmed0 exchange-api — dated FX snapshot sample

What: CC0 daily exchange rates (~200 fiat + crypto/metal codes) from https://github.com/fawazahmed0/exchange-api, published as one immutable npm version per day (`@fawazahmed0/currency-api@<YYYY-MM-DD>`) and served keyless via jsDelivr. Each file is `{date, <base>: {code: rate}}`, rate = units of quote per 1 base.

Sample here: six USD-base snapshots (2024-03-03, 2024-03-06, 2025-01-02, 2025-07-01, 2026-01-02, 2026-09-12), the currency-name list, and `usd_vintages_long.csv` (2,756 rows: snapshot_date, base, quote, rate_per_usd).

How pulled: `curl -sL -o usd_<date>.json https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@<date>/v1/currencies/usd.json`, then pandas to melt. Total 157 KB, well under the 25 MB cap; no scraper, no key, no login.

Caveats: earliest dated snapshot the CDN serves is 2024-03-02 (not 2023 as the job card said); daily files are npm versions, not git commits, so "git vintages" is a misnomer. Rates are the maintainer's blend of public feeds, not central-bank fixings.

Full dataset: loop over dates from 2024-03-02 to yesterday and the base currency you need (USD or EUR base is enough: ~925 files, ~7 MB). Mirror: `https://<date>.currency-api.pages.dev/v1/currencies/<base>.json`. Full every-base pull is ~2.3 GB and should be throttled.
