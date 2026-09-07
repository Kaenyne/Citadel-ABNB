# Average length of stay: Airbnb vs. hotels

**Method (nights ÷ transactions):** avg stay = reported nights ÷ number of bookings (consumer transactions).
Airbnb discloses both pieces in the 10-K; hotels need STR room nights ÷ Kalibri check-in-based ALOS.

## Headline

| | Avg nights per stay | Source |
|---|---|---|
| Airbnb, global, 2025 | **3.7** (2024: 3.8) | Airbnb FY2025 10-K, MD&A "Geographic Mix" |
| Airbnb, North America, 2025 | **4.1** | Airbnb FY2025 10-K |
| U.S. hotels, all, post-2020 | **~2.1** (pre-2020: ~1.9) | Kalibri Labs via HotelBusiness / HotelsMag |
| U.S. hotels, 2019 | 1.8 | Kalibri Labs via HotelTechReport |

- Airbnb stays run **~1.8x** U.S. hotel stays (3.7 vs 2.1); **~2.0x** if you use North America (4.1 vs 2.1).
- Airbnb's avg is **drifting down** (4.1 → 3.7 over 2022–25) as post-COVID long stays normalize and mix shifts to APAC/LatAm; hotels **stepped up** once (1.9 → 2.1) and stuck.
- Gap is narrowing: 2022 ratio ≈ 1.95x → 2025 ≈ 1.76x.

## Airbnb — 10-K series ("average nights per booking, excluding experiences")

| Year | Global | N. America | EMEA | LatAm | APAC | Nights booked (mm) | Implied bookings (mm) |
|---|---|---|---|---|---|---|---|
| 2020 | 4.1 | 4.4 | 4.4 | 4.4 | 2.8 | 193.2 | 47 |
| 2021 | 4.1 | 4.3 | 4.4 | 4.3 | 2.7 | 300.6 | 73 |
| 2022 | 4.1 | 4.2 | 4.2 | 4.2 | 3.2 | 394 | 96 |
| 2023 | 3.9 | 4.1 | 3.9 | 3.9 | 3.3 | 448 | 115 |
| 2024 | 3.8 | 4.1 | 3.8 | 3.7 | 3.3 | 491.5 | 129 |
| 2025 | 3.7 | 4.1 | 3.8 | 3.6 | 3.3 | 533.0 | 144 |

Sources: Airbnb 10-Ks FY2020–FY2025 (each year's MD&A "Geographic Mix" paragraph; FY2025 filed 2026-02-12, accession 0001559720-26-000004). Nights 2024/2025 from FY2025 10-K regional table; 2020–2023 from Airbnb IR annual figures (via Backlinko compilation).

- Implied bookings = nights ÷ nights-per-booking. Slight overstatement: nights include experiences/seats, per-booking metric excludes them.
- 2019 not disclosed in S-1/10-K. Proxy: U.S. panel of all Airbnb reservations 2019–24 (arXiv 2507.21298) → 2019 mean **3.7**, median **2**; post-2021 mean 4.1–4.4, median 3. Month-plus (28+) bookings ~1.5% pre-COVID → 2.2% after.
- Long-term stays (28+ nights) were ~17–18% of *nights* (Q1 2024, Airbnb IR / Reuters via Awning). FY2025 10-K: short-term stay growth "continued to outpace long-term stays."
- 2025 regional GBV/nights → ADR: NA $255, EMEA $159, LatAm $95, APAC $118 (FY2025 10-K table).

## Hotels

| Period | Scope | ALOS (nights) | Source |
|---|---|---|---|
| 2015–2019 | U.S. all hotels | ~1.9 | Kalibri Labs (Lomanno) via HotelBusiness |
| 2019 | U.S. all hotels | 1.8 | Kalibri via HotelTechReport |
| 2020–2022 | U.S. all hotels | ~2.1 | Kalibri via HotelsMag; "has stayed in the range consistently" |
| 2024 | Extended-stay hotels, long-stay guests | 24 | Kalibri / Highland Group 2025 ALOS report (ESLA) |
| 2024 | Traditional hotels, long-stay guests | 13 | same — applies to 7+ night guests only, not all guests |

- Transaction proxy: U.S. hotels sold **1.3B room nights in 2024** (STR/CoStar via HospitalityNet) ÷ 2.1 ≈ **620mm stays** vs Airbnb's ~129mm bookings globally (2024).
- Kalibri: each 0.1-night change in ALOS ≈ 80k fewer daily check-ins industry-wide (HotelBusiness) — hotels' cost lever from longer stays.
- No 2023–2025 all-hotel ALOS print found; 2.1 carried forward per Kalibri's "won't revert to 1.9" view. Gap: STR/Kalibri subscription would give exact annual ALOS.

## Pitch angles

- **Bull:** 3.7 vs 2.1 = structurally different trip (leisure/groups/remote work), not a hotel substitute at the margin → less exposed to business-travel cycles, higher GBV per transaction (2025: $91.3B ÷ 144mm ≈ **$633/booking** vs hotel ≈ 2.1 × U.S. ADR (~$160 — verify vs STR 2024 print) ≈ $340).
- **Bear:** Airbnb's stay length is falling every year since 2022 while hotels held their step-up → the COVID "longer stays" tailwind is unwinding; fewer nights per booking means more bookings needed for the same nights growth (bookings +11% in 2025 for +8% nights).
- **Next:** swap `implied_bookings_mm` for a card-panel transaction count (Consumer Edge / Second Measure) to get a true transaction-based LOS and check the 10-K series; city-level cut via Inside Airbnb (default assumes 3 nights/booking; SF reported 5.5).

## Files

- `data/processed/airbnb_nights_per_booking.csv` — 10-K series by year/region + implied bookings
- `data/processed/hotel_avg_length_of_stay.csv` — hotel ALOS points + implied stays
- `analysis/src/stay_length_airbnb_vs_hotels.py` — recompute + chart
- `docs/figures/stay_length_airbnb_vs_hotels.png`

## Source links

- Airbnb FY2025 10-K: https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm
- Airbnb FY2024 10-K: https://www.sec.gov/Archives/edgar/data/1559720/000155972025000010/abnb-20241231.htm
- Airbnb FY2023 10-K: https://www.sec.gov/Archives/edgar/data/1559720/000155972024000006/abnb-20231231.htm
- Airbnb FY2022 10-K: https://www.sec.gov/Archives/edgar/data/1559720/000155972023000003/abnb-20221231.htm
- Airbnb FY2021 10-K: https://www.sec.gov/Archives/edgar/data/1559720/000155972022000006/abnb-20211231.htm
- Airbnb FY2020 10-K: https://www.sec.gov/Archives/edgar/data/1559720/000155972021000010/airbnb-10k.htm
- Airbnb Q4-2025 shareholder letter: https://s26.q4cdn.com/656283129/files/doc_financials/2025/q4/Airbnb_Q4-2025-Shareholder-Letter.pdf
- arXiv 2507.21298 (U.S. Airbnb reservations 2019–24): https://arxiv.org/pdf/2507.21298v1
- Backlinko Airbnb stats (nights by year, IR-sourced): https://backlinko.com/airbnb-stats
- Awning Airbnb stats (long-term stays share): https://awning.com/post/airbnb-statistics
- Inside Airbnb data assumptions: https://insideairbnb.com/data-assumptions/
- Kalibri via HotelBusiness: https://hotelbusiness.com/industry-data-trackers-see-positives-for-lodging/
- Kalibri via HotelsMag: https://hotelsmag.com/news/kalibri-labs-says-longer-length-of-stays-reducing-operational-costs/
- Kalibri via HotelTechReport: https://hoteltechreport.com/news/hospitality-statistics
- Kalibri / Highland Group ALOS report: https://www.esla.org/wp-content/uploads/sites/2/2025/04/KL-THG-Report-Marketing-2025.pdf
- STR room nights via HospitalityNet: https://www.hospitalitynet.org/news/4127015.html
- Prostay ALOS benchmarks: https://www.prostay.com/blog/hotel-average-length-of-stay/
