# Booking.com multi-destination trip dataset (WSDM WebTour 2021) — sample

What: Booking.com's official challenge release of 1.55M anonymised real reservations (check-in 2016-01 to 2017-02) grouped into multi-city trips; columns user_id, checkin, checkout, city_id, device_class, affiliate_id, booker_country, hotel_country, utrip_id. Countries and cities are anonymised (fictional names / integer IDs); no price or accommodation-type fields. Hosted ungated on HuggingFace, licence CC-BY-NC-ND-4.0.

How pulled (2026-09-14): ranged `curl -r` heads from the HF resolve endpoint, no login: first 5 MB of train_set.csv (62,861 rows), first 2 MB of test_set.csv (25,880 rows), ground_truth.csv in full (1.84 MB, 70,662 rows), plus README.md. Partial last lines dropped. Total 8.8 MB, under the 25 MB cap.

Caveats: heads are sorted by user_id so booker_country coverage is truncated (5 of ~? values); README mentions a created_date column that the files do not carry; the challenge selects multi-city trips only, so LOS (~1.7 nights) and cross-border share (~90%) are not representative of all bookings.

Full dataset (~124 MB CSV, ~152 MB repo): `curl -L -O https://huggingface.co/datasets/Booking-com/multi-destination-trip-dataset/resolve/main/train_set.csv` (and test_set.csv, ground_truth.csv), or `huggingface-cli download Booking-com/multi-destination-trip-dataset --repo-type dataset`.
