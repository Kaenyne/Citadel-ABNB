# neshitov-la-inside-airbnb-2018 — sample (NOT obtained)

Source: https://github.com/neshitov/airbnb — a Dec-2018 price-regression notebook on the Inside Airbnb Los Angeles
listings.csv of 2018-12-06 (44,504 rows, 96 columns) plus neighbourhoods.geojson.
The job card said the CSV was committed; it is not. Checked the contents API, the recursive tree and all 11 commit
trees: only the notebook, README and three 4 MB gmplot HTML maps exist. sampled=false.
What is saved here: `repo_README.md` (names the exact source URL) and `notebook_listings_info_output.txt`
(the printed `listings.info()` = full 96-column schema and non-null counts of that vintage).
Pulled with `gh api` and `curl` from raw.githubusercontent.com on 2026-09-14; no scraper, no login; < 10 KB written.
Full dataset: http://data.insideairbnb.com/united-states/ca/los-angeles/2018-12-06/data/listings.csv.gz (now 403 on the
live CDN). Try the Wayback Machine for that URL (our lookups hit HTTP 429) or request it from Inside Airbnb.
