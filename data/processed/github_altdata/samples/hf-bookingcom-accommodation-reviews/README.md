# hf-bookingcom-accommodation-reviews (sample)

Official Booking.com review dataset on HuggingFace (https://huggingface.co/datasets/Booking-com/accommodation-reviews): ~1.6M English guest reviews published in 2023 over ~40k accommodations, with guest_type, room_nights, check-in month, accommodation type/country/star rating and beach/ski/city-centre tags; rectour24/ holds the RecTour 2024 challenge split of the same panel.
Pulled 2026-09-14 with HTTP Range reads only (no login, no API key): first 3 MB of train.csv (8,395 clean rows) and first 2 MB of rectour24/train_users.csv (19,329 rows), trailing partial record dropped; plus the HF API file listing, the dataset card, and HEAD Content-Length per file.
Caps applied: 5.0 MB written, heads only; the 584 MB / 554 MB files were not downloaded.
Full dataset (10 CSVs, 1.71 GB): `huggingface-cli download --repo-type dataset Booking-com/accommodation-reviews` or curl each `resolve/main/<file>` URL.
Licence: card text says non-commercial but links CC-BY-SA-4.0; treat as research-only until a human decides.
Date grain: check-in month 1-12 only, no year or day; not a time series.
