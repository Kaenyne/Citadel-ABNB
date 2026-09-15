# Booking.com accommodation reviews (RecTour 2024) - sample

What: Booking.com's own public review dataset on Hugging Face (`Booking-com/accommodation-reviews`, ungated). ~1.6M English reviews published in 2023 from ~40k properties; each row carries guest_type, room_nights, check-in month, anonymised guest country, property country/type/star rating and beach/ski/city flags. `rectour24/` re-cuts it into users / reviews / matches for the review-ranking challenge (CEUR-WS Vol-3886, arXiv 2407.00787).
How pulled (14 Sep 2026): keyless `curl -sL -r <byte range>` heads from `https://huggingface.co/datasets/Booking-com/accommodation-reviews/resolve/main/<file>` (train 5 MB, val 2 MB, rectour24 train_users 2 MB, train_reviews 2 MB, train_matches 1 MB) plus the README; each head was parsed with pandas and the trailing truncated record dropped. Exact commands in manifest.json.
Caps applied: 12.4 MB total written, 6 files, no clone, no login, nothing beyond the first bytes of each file.
Row counts: train head 14,203; val head 5,861; rectour24 users head 19,330; reviews head 5,896; matches head 11,768. Dates: month 1-12 (2023, no year column).
Licence: README text says non-commercial but links CC BY-SA 4.0; card tag 'cc'. Treat as research-only until a human decides.
Full dataset: 1.71 GB across 11 files; pull with `huggingface-cli download Booking-com/accommodation-reviews --repo-type dataset` or `curl -L` on the resolve URLs above (train.csv 584 MB, rectour24/train_reviews.csv 554 MB are the big ones).
