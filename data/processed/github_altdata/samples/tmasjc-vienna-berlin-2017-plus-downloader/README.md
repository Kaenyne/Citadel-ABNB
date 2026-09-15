# tmasjc/airbnb-market-data — 2017 Vienna + Berlin Inside Airbnb listings.csv, plus an R downloader

Source: https://github.com/tmasjc/airbnb-market-data (last push 2019-10-14, no licence file). A Shiny demo app that ships two
Inside Airbnb *summary* `listings.csv` files (16 columns: id, host, neighbourhood, lat/lon, room_type, price, minimum_nights,
number_of_reviews, last_review, reviews_per_month, calculated_host_listings_count, availability_365).
- `vienna_listings.csv`: 9,201 rows, vintage 2017-09-15 (per upstream README; last_review max 2017-09-14).
- `berlin_listings.csv`: 20,576 rows, vintage ~2017-05-08 (last_review max 2017-05-08).
- `download_csv.R`: CLI that scrapes insideairbnb.com/get-the-data.html for the city list and date index, then fetches
  `data.insideairbnb.com/<country>/<region>/<city>/<date>/visualisations/listings.csv`. NOT run here (rvest scrape of a third-party page;
  the 2017-era page layout it parses no longer exists, so it is reference-only). `README_upstream.md` is the repo README.
Pulled 2026-09-14 with `curl -sL -o` from raw.githubusercontent.com/tmasjc/airbnb-market-data/master/{Data/berlin.csv,Data/vienna.csv,download_csv.R,README.md}.
This is the ENTIRE data content of the repo (~4.9 MB); no rows were truncated. Caps: <=5 MB target met.
Full dataset = same files; the demo.gif (7 MB) and Cache/webpage.xml (the 2017 get-the-data page snapshot, 0.97 MB, useful as a
2017 city/date inventory) were skipped. Data are Inside Airbnb (CC0-style "public data" claim by Inside Airbnb; repo itself unlicensed).
