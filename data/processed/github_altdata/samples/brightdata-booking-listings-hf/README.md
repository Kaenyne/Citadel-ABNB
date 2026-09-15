# brightdata-booking-listings-hf — sample

Head of `booking-listings.csv` from https://huggingface.co/datasets/BrightData/Booking.com-Listings (Bright Data, last modified 2025-05-12, licence tag "other" = Bright Data Master Service Agreement). Booking.com search-result rows: quoted final vs original price (USD), free-cancellation / no-prepayment flags, cancellation deadline, bedrooms/beds/kitchens, review score, for six check-in dates 27 Dec 2024 – 27 Feb 2025 across ~50 countries. One-off cross-section, not a time series.

Pulled 2026-09-14 with a keyless HTTP range request for bytes 0–5,000,000 of the 62,784,719-byte file (`curl -r 0-5000000` on the `/resolve/main/` URL, HTTP 206), parsed with pandas and the final truncated record dropped: 5,896 rows, 35 columns, 4.9 MB (`brightdata_booking_listings_head.csv`). `head_summary.json` holds country mix (from the `/hotel/<cc>/` path in `url`, since `searched_country`/`listing_country` are null in the head), flag shares, price quantiles and bedroom counts.

Caps applied: 5 MB head only, one file fetched, no scraper run, no login or token. Eight columns are all-null in the head; `free_cancellation` is 100% True, so the capture looks filtered on that flag.

Full dataset: the same URL without the range header (~63 MB, ~75k rows) — do not fetch or redistribute until a human has decided whether the Bright Data MSA permits it.
