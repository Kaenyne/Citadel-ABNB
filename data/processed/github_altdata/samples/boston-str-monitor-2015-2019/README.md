# boston-str-monitor-2015-2019 -- sample

Source: https://github.com/js-fitz/STR-Monitor (js-fitz, 2020 capstone on Boston's 2018 Short-Term Rental Ordinance; no licence file; last push 2020-05-25).
What is here: every tabular file committed to the repo (~2.3 MB, 10 CSVs) plus the upstream README. The Airbnb tables are
tract- and neighbourhood-level aggregates of Inside Airbnb Boston scrapes, 35 scrape dates 2015-10-03 to 2020-02-13
(listing counts, accommodates, licensed share, median/avg nightly price, 30-day availability); the Padmapper tables are the
matching long-term-rental asking-rent panel (85 scrapes, 2013-02-18 to 2020-02-18); str/pro/props/census_groups_data are
Feb-2020 cross-sections of the city STR registry and BARI parcel data; duplicated_license_listings is 770 listing-level rows
sharing licence numbers in the 2020-02-13 scrape (contains host first names -- do not redistribute).
How pulled (2026-09-14): `gh api repos/js-fitz/STR-Monitor/git/trees/HEAD?recursive=1` then `curl -sL -o` from
raw.githubusercontent.com/js-fitz/STR-Monitor/HEAD/<path>; nothing cloned, no scraper run, no airbnb.com contact.
Caps: 25 MB cap not approached; files pulled whole (all under 1 MB each); GeoJSON, notebooks and images skipped.
Full dataset: the raw inputs (airbnb.csv 629 MB of 23 IA Boston listings dumps, STRE.csv 23 MB, SAMREF.csv 79 MB, BARI parcels
79 MB, padmapper.csv 48 MB, STR_apps.csv from Boston DoIT) were never committed; rebuild from Inside Airbnb archives (Boston
2015-2020 dumps are off the CDN), data.boston.gov, Harvard Dataverse doi:10.7910/DVN/UWTQ4E and jefftk.com/apartment_prices.
