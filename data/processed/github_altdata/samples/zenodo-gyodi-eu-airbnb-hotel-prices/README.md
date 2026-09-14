# zenodo-gyodi-eu-airbnb-hotel-prices — sample

What: Gyodi & Nawaro replication data (Tourism Management 2021, CC-BY-4.0). Zenodo record 4446043 = listing-level Airbnb quote prices (EUR, 2 guests x 2 nights) for 10 European cities, summer 2019, weekday vs weekend; record 6976622 = hotel-level median 2-person prices for the same cities (no Rome), same season, with stars, hotel/hostel segment and ratings. Record 5233198 = the authors' "Airbnb and hotels during COVID-19" PDF (CC-BY-NC-4.0) with 2018-2020 nine-city tables.

Sample here: 4 Airbnb cities (Barcelona, Paris, London, Rome; weekdays + weekends, 28,541 rows), 3 hotel cities (Barcelona, Paris, London; 4,678 rows), the authors' spatial-model script, the COVID PDF, and the two Zenodo API record JSONs. 9.8 MB total, under the 25 MB cap; ~10 files of data pulled.

How pulled (14 Sep 2026): keyless `curl -sL` against `https://zenodo.org/records/<id>/files/<file>?download=1`, one file at a time with a 1 s pause (Zenodo rate-limits bots). Exact URLs in manifest.json. No scraper run; nothing on airbnb.com touched.

Full dataset: the remaining 6 Airbnb cities (amsterdam, athens, berlin, budapest, lisbon, vienna) and 6 hotel cities from the same two records, ~15 MB total; record 8135170 holds a 14.5 MB ESDA supplement PDF (not pulled).

Caveats: single cross-section, no date column in the Airbnb files (hotel `datecontrol` gives 16-21 Jul 2019 and 6-11 Aug 2019 stay dates); quote prices, not realised ADR.
