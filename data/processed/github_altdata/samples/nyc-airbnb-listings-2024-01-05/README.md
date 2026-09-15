# nyc-airbnb-listings-2024-01-05

NYC Airbnb listings snapshot dated 5 Jan 2024 (Inside Airbnb summary-listings format re-hosted on Kaggle by vrindakallu, committed to GitHub by Tracey-Sneed). One row per listing: borough, neighbourhood, room type, price, minimum nights, review counts, availability_365, host listing count, NYC OSE licence string, plus curator-added rating/bedrooms/beds/baths. 20,758 rows x 22 columns; last_review spans 2011-12-10 to 2024-01-05.

Pulled 2026-09-14 with `curl -sL -o` from raw.githubusercontent.com (main branch): the CSV (4.4 MB, complete, no head taken), schema.sql, and the repo README (saved as SOURCE_README.md). The 17 MB SQLite db, 6.4 MB .pbix and PDFs were skipped per the sample plan. Total written: 4.47 MB, under the 25 MB cap.

Caveats: the repo carries no licence file (underlying data is Inside Airbnb, CC BY 4.0, via Kaggle); the Kaggle curator dropped zero-review and null rows, so the 20,758 count is a reviewed-listings subset of the ~39k raw Inside Airbnb NYC dump of the same date.

Full dataset: `git clone --depth 1 https://github.com/Tracey-Sneed/New-York-Airbnb-Listings-2024` (about 29 MB) or the Kaggle page https://www.kaggle.com/datasets/vrindakallu/new-york-dataset (login required, not used here).
