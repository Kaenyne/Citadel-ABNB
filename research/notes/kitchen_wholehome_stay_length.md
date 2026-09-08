# Kitchen & whole-home effect on stay length

Follow-up to `stay_length_airbnb_vs_hotels.md` (Airbnb 3.7 nights/booking global, 4.1 N. America, vs U.S. hotels ~2.1). Question: how much of that gap is the *product* (kitchen, whole home) vs the *trip*?

## Headline

| Segment (Airbnb, 8 U.S. cities) | Nights per booked run | vs bare room |
|---|---|---|
| Private room, **no kitchen** (closest to a hotel room) | **3.7** | — |
| Private room **+ kitchen** | **5.2** | **+1.4 (+38%)** |
| Entire home, no kitchen | 5.1 | +1.4 |
| Entire home **+ kitchen** (84% of runs) | **4.9** | **+1.2 (+32%)** |

- **Kitchen ≈ +1.2–1.5 nights per booking (+32–38%).** Within private rooms, adding a kitchen lifts the mean run 3.7 → 5.2; within-city effect +1.5 nights (runs-weighted), median city +1.2. Entire homes without a kitchen are a tiny, odd sample (3% of runs; aparthotel-style) so the within-entire effect is noisy (+0.3 weighted, +0.1 median city).
- **Whole home + kitchen vs bare room: +1.2 pooled, +1.5 median city (range +1.2 Austin to +3.0 SF).**
- **This explains ~60–75% of the Airbnb-vs-hotel gap.** N. America 4.1 vs hotel 2.1 = 2.0-night gap; the product effect (+1.2–1.5) covers 0.6–0.75 of it. The remainder is trip mix (leisure/groups/remote-work stays vs 1–2 night business).
- **Bigger ≠ longer.** Larger entire homes book *shorter* stays: studio 5.3 → 1-bed 5.4 → 2-bed 5.1 → 3-bed 4.8 → 4+ bed 4.2 (−1.2 nights, −22%). By party size: sleeps 1–2 = 5.6, 3–4 = 5.4, 5–6 = 5.0, 7+ = 4.3. Big houses are weekend/event/group trips; small units are solo/couple, work-adjacent, longer.
- Share of runs ≥7 nights: bare room 12% → room+kitchen 21% → entire+kitchen 19%; 4+ bed only 12.5% vs 1-bed 24%.

## Method (transactions × nights, listing-level)

- Data: Inside Airbnb June-2026 scrapes — `listings.csv.gz` (room_type, amenities, bedrooms, accommodates) + `calendar.csv.gz` (365 days of availability) for Austin, Chicago, Denver, Nashville, New Orleans, San Francisco, Seattle, Washington DC. 37k active listings (≥1 review in last 12 months), 273,522 booked runs.
- Stay proxy: a **booked run** = contiguous block of nights marked unavailable, capped at 30 nights (drops host blocks/long-term). Mean run = nights ÷ runs = same construct as Airbnb's nights-per-booking.
- Kitchen = amenities string contains "kitchen" (incl. kitchenette). 92% of booked runs are in listings that have one (Austin: 95% of active listings).
- Caveats: (1) host blocks inflate levels (pooled 4.9 vs 10-K N. America 4.1) — trust the *differences*; (2) forward calendar mixes booked and blocked nights; (3) LA calendar (16M rows) didn't load in-browser — rerun locally with `--raw`; (4) NYC excluded (Local Law 18 forces ≥30-night minimums, breaks the proxy).
- Minimum-nights (host floor) tells the same story on kitchen but is dominated by the 30-night regulatory mode (Austin: 28% of room+kitchen listings set ≥28 nights vs 5% of rooms w/o kitchen).

## Hotel-side check (kitchen = extended-stay segment)

- Extended-stay hotels (kitchen in every room): long-stay guests average **24 nights** vs **13 nights** for the same guest type in traditional hotels (Kalibri Labs / The Highland Group 2025 ALOS report, 2024 national) — the kitchen product roughly doubles stay length even inside the hotel industry.
- Extended-stay ADR $121 vs U.S. all-hotel ADR (~$160, STR — verify against the 2024 print): guests trade rate for a kitchen and stay ~10x the 2.1-night all-hotel average (Highland Group March-2025 bulletin; Kalibri ALOS).
- Monthly furnished rentals (full kitchen, whole unit) average ~96 days (Furnished Finder) — the long tail of the same curve.
- Kalibri: every +0.1 night of ALOS ≈ 80k fewer daily check-ins industry-wide → hotels' cost incentive to chase kitchen/extended-stay product (HotelBusiness).

## Pitch angles

- **Bull:** the kitchen/whole-home product is worth +1.2–1.5 nights per booking *before* any trip-mix effect; hotels can only replicate it by building extended-stay supply (37% of U.S. pipeline per Kalibri) at $121 ADR, well below Airbnb N. America GBV/night of $255.
- **Bear:** Airbnb's growth is skewing to large homes (4+ bed = 21% of runs but shortest stays) and to APAC/LatAm (3.3–3.6 nights) — both pull nights-per-booking down, which is exactly the 4.1 → 3.7 drift in the 10-K. More transactions needed per night of growth → higher CAC/take-rate pressure.
- **Next:** run `--raw` on Theo's full Inside Airbnb store (add LA, Miami, Orlando, NYC-ex-LL18) and a regression of run length on kitchen × bedrooms × city FE; layer party size (accommodates) into the Airbnb-vs-hotel choice model.

## Files

- `data/processed/insideairbnb_booked_run_length_by_segment.csv` — per-city × segment aggregates
- `data/processed/kitchen_wholehome_pooled.csv` — pooled (runs-weighted)
- `analysis/src/kitchen_wholehome_stay_length.py` — recompute from raw gz or from aggregates + chart
- `docs/figures/kitchen_wholehome_stay_length.png`

## Sources

- Inside Airbnb, Get the Data (June-2026 U.S. city scrapes): https://insideairbnb.com/get-the-data/
- Inside Airbnb data assumptions (3-night default, SF 5.5): https://insideairbnb.com/data-assumptions/
- Airbnb FY2025 10-K (nights per booking by region): https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm
- Kalibri Labs / The Highland Group 2025 ALOS report (24 vs 13 nights): https://www.esla.org/wp-content/uploads/sites/2/2025/04/KL-THG-Report-Marketing-2025.pdf
- Highland Group March-2025 Extended-Stay Bulletin (ADR $121, occ 74%): https://www.esla.org/wp-content/uploads/sites/2/2025/04/March-2025-Extended-Stay-Bulletin.pdf
- Kalibri Labs extended-stay development (37% of pipeline): https://www.kalibrilabs.com/extended-stay-development/
- Kalibri via HotelBusiness (ALOS 1.9→2.1, 80k check-ins per 0.1 night): https://hotelbusiness.com/industry-data-trackers-see-positives-for-lodging/
- Furnished Finder (monthly rentals ~96 days): https://www.furnishedfinder.com/blog/monthly-renters-are-not-short-term-guests-and-that-changes-everything
- Hotel Interactive / Highland Group May-2026 bulletin (extended-stay drawing 4–7 night stays): https://www.hotelinteractive.com/extended-stay-hotel-demand-accelerates-as-u-s-lodging-performance-improves/
