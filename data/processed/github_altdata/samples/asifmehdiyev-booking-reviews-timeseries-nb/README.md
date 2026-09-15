# asifmehdiyev-booking-reviews-timeseries-nb — sample

Repo: https://github.com/Asifmehdiyev/Booking_Time_Series_Modelling (1 notebook + README, no licence, last push 2023-06-19).
What it is: EDA + Prophet notebook over a Kaggle CSV (kaggle.com/datasets/asifmehdiyev/bookingnew, booking.csv) of 26,386
Booking.com guest reviews for 819 Belgian properties, review dates 2018-07-31 to 2021-07-19, crawled 2021-07-20.
Columns: review_title, reviewed_at, reviewed_by, images, crawled_at, url, hotel_name, hotel_url, avg_rating, nationality,
rating, review_text, raw_review_text, tags (trip type~party~room~Stayed N nights), meta.
How pulled (2026-09-14): curl of the raw notebook and README from raw.githubusercontent.com; Python stripped the 22 PNG
and HTML outputs (1.1 MB -> 78 KB) and dumped every cell source + text output to notebook_text_outputs.txt; the schema
and the one printed monthly table were transcribed to CSV. Total ~130 KB, well under the 25 MB cap.
Not pulled: the Kaggle CSV (login required; booking.com scrape, ToS question for a human). To get the full data,
log in to Kaggle and download booking.csv from the dataset page above, then re-run the notebook.
