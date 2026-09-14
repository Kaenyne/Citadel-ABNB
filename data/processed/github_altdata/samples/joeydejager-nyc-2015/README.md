# joeydejager-nyc-2015 — Inside Airbnb NYC snapshot, 1 Jan 2015 (CC0-1.0)

Source: https://github.com/JoeyDeJager/inside-airbnb-data (3 commits, last push 2015-01-20). One city, one date:
`new-york-city/2015-01-01/` with `data/listings.csv` (raw, 84 MB, ~27k listings x 54 cols) and `visualizations/`
(summary listings 27,361 rows, neighbourhood lookup 181 rows, review log ~280k rows of listing_id+date back to 2008).

Pulled 2026-09-14 with `curl` from raw.githubusercontent.com (tree listed via `gh api .../git/trees/HEAD?recursive=1`).
Caps applied: summary listings, neighbourhoods, LICENSE and README taken whole; raw listings.csv limited to its first
2.5 MB (`curl -r 0-2499999`) and reviews to 1.5 MB (`curl -r 0-1499999`), trailing partial record dropped. 6.4 MB total.

Caveat: raw listings.csv is ragged (many rows have 55-56 fields vs a 54-column header); `listings_head.csv` keeps only the
468 well-formed rows of the first 846. Parse the full file with `pd.read_csv(..., engine="python", on_bad_lines="skip")`.

Full dataset: `git clone --depth 1 https://github.com/JoeyDeJager/inside-airbnb-data` (~22 MB packed, ~93 MB unpacked) or
`curl -L -o listings.csv https://raw.githubusercontent.com/JoeyDeJager/inside-airbnb-data/master/new-york-city/2015-01-01/data/listings.csv`.
