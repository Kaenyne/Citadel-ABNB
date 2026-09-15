# montera34/airbnb.barcelona - Inside Airbnb Barcelona snapshots 2015-2019 (sample)

What: five of the 34 dated Inside Airbnb Barcelona `listings_summary` snapshots (150430, 160103, 170104, 180117, 190308) plus the cumulative `reviews_summary` file from the last snapshot (2010-08 to 2019-03, 576,579 rows), as committed in https://github.com/montera34/airbnb.barcelona under data/original/airbnb/<YYMMDD>/.
Why: fills gap #1 (Inside Airbnb dumps older than the CDN's ~1-year window) for Barcelona, one of the 13 panel cities.
How pulled (2026-09-14): `gh api` to list the snapshot folders, then one `curl -sL` per raw.githubusercontent.com file; see manifest.json for exact URLs and the pandas description.
Caps: 6 data files, 24.4 MB total (cap 25 MB); no cloning, nothing under scraping/ was run, airbnb.com not touched.
Full dataset: all 34 dates are in snapshot_dates_all34.txt; pull the rest with the same curl pattern (~80-90 MB CSV) or `git clone --depth 1 --filter=blob:none --sparse https://github.com/montera34/airbnb.barcelona && git sparse-checkout set data/original/airbnb`.
Licence: repo has no LICENSE; upstream Inside Airbnb is CC BY 4.0. Human decision before redistribution.
