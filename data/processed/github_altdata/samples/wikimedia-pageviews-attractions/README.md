# wikimedia-pageviews-attractions sample

Daily English-Wikipedia pageviews (all-access, user agent only) for four articles (Airbnb, Mexico_City, Lisbon, Kyoto),
2026-06-01 to 2026-09-13, pulled keyless from the public Wikimedia Analytics REST API on 2026-09-14.
The catalogued repo (https://github.com/Kenchch/nz-attraction-pageviews, MIT) is an ingest tool for 8 NZ attraction pages
and holds no data; only its venues.csv was copied for reference and its code was not run.
Files: pv_<Article>.json (raw API responses), pageviews_daily.csv (flattened, 420 rows), venues.csv, manifest.json.
Caps applied: 4 articles x 105 days, ~85 KB total (far under the 25 MB cap).
Full dataset: same endpoint with any article and dates from 20150701 onward, e.g.
https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/<Article>/daily/20150701/20260913
(rate limit ~100 req/s, set a descriptive User-Agent). Bulk hourly dumps: https://dumps.wikimedia.org/other/pageviews/
