# brightdata-booking-listings-sample-1001

Bright Data's free promotional sample of Booking.com search results (repo: https://github.com/luminati-io/Booking-dataset-sample).
One CSV, 1,000 property quotes, 26 columns, for a single fixed search: 1 adult, 1 room, check-in 2025-01-01, check-out 2025-01-10,
USD final/original price for the 9-night stay, review score/count, bedroom/bed/kitchen counts, free_cancellation and no_prepayment
flags, geo JSON. Cities: Melbourne area, Vienna, Orlando/Kissimmee. Captured ~Dec 2024 (last push 2024-12-16).

Pulled 2026-09-14 with `curl -sL` from raw.githubusercontent.com (file renamed to `brightdata_booking_1001.csv`); 814,588 bytes,
well under the 25 MB cap, so this is the complete free file, not a head. The 627 KB marketing PNG was skipped.

Full dataset: this sample is everything that is public. Bright Data advertises a ~30.4K-record paid product; obtaining it requires a
Bright Data account and purchase. No LICENSE file: usage/redistribution rights unstated (scraped Booking.com data) -- human decision needed.
