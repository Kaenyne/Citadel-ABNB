# Airbnb party size: how many people stay per booking

Readable version: artifact "Airbnb Party Size" (claude.ai/code/artifact/ebd4b51a-eb74-4c32-916f-0ffe4882dc02). Rendered page source: `docs/party_size_distribution.html`.

## Headline

| People per stay | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8+ |
|---|---|---|---|---|---|---|---|---|
| Share of Airbnb bookings (central) | 16% | 36% | 21% | 12% | 7% | 4% | 2% | 3% |
| Low / high band | 13–19 | 36–39 | 20–21 | 11–12 | 5–7 | 3–4 | 1–3 | 2–4 |

- **Mean ≈ 2.97 people per booking** (range 2.8–3.05 across every long window since 2018). **84% of bookings are groups; 48% are 3+; 28% are 4+; 16% are 5+.**
- Airbnb does not disclose guests per booking; this is a maximum-entropy fit to three independent anchors (below). Mean and solo share are firm; the 3/4/5+ split is the soft part.

## Anchor 1 — mean = cumulative guest arrivals ÷ bookings

Guest arrivals = every person checking in (Airbnb definition; "3.5M guest arrivals in one night" = in-house guests). Bookings = nights booked ÷ nights per booking (10-K).

| Window | Arrivals added (mm) | Bookings (mm) | People/booking |
|---|---|---|---|
| Aug 2018 (400M) → Oct 2021 (1B) | 600 | 213 | 2.81 |
| Mar 2019 (500M) → Oct 2021 (1B) | 500 | 171 | 2.93 |
| Sep 2020 (825M) → Oct 2024 (2B) | 1,175 | 397 | 2.96 |
| Oct 2021 (1B) → Oct 2024 (2B) | 1,000 | 328 | 3.05 |
| Oct 2021 (1B) → Dec 2025 (2.5B) | 1,500 | 499 | 3.01 |
| Aug 2018 (400M) → Dec 2025 (2.5B) | 2,100 | 712 | 2.95 |

- Milestones: 400M Aug 26 2018 and 500M Mar 27 2019 (Airbnb Newsroom); 825M as of Sep 30 2020 (S-1); 1B Oct 2021 and 2B Oct 2024 (Newsroom, 2-billionth guest); "over 2.5B" (FY2025 10-K). Nights: S-1 (2017 185.8M, 2018 250.3M, 2019 326.9M) and 10-Ks; nights per booking 3.7–4.1 (10-Ks), 3.8 assumed 2017–19.
- Sub-2-year windows swing 2.3–3.2 because arrivals lag bookings by the lead time — ignore them. Full table: `data/processed/airbnb_guests_per_booking_windows.csv`.
- Cross-check: Bedroom Nights Booked >1B TTM to Q2 2026 vs ~560M nights → ~1.8 bedrooms per stay; at ~1.6 people per bedroom ≈ 2.9 people.

## Anchor 2 — solo share

- "More than 80% of bookings on Airbnb are group trips" (Airbnb 2024 Summer Release) → solo ≤ 20% of bookings; fit uses 16%. Fewer than 10% of group trips add a co-traveller to the reservation.
- "Almost a quarter of nights booked worldwide in 2022 were by guests traveling on their own"; ~half of those nights were 28+ stays (Airbnb Newsroom, solo-travel safety release). Solo stays ≈ 1.5× average length → 16% of bookings = 24% of nights. Consistent.
- Solo travellers and millennials most likely to book a private room; >80% of private-room stays under $100/night, avg $67 (2023 Summer Release).

## Anchor 3 — shape (Hawaii DBEDT 2024, only public party-size-by-accommodation data)

| Accommodation (air visitors, 2024) | 1 | 2 | 3+ | Avg party | Avg 3+ party | LOS (days) |
|---|---|---|---|---|---|---|
| Rental house only | 29% | 37% | 33% | 2.49 | 4.3 | 9.46 |
| Hotel only | 29% | 43% | 29% | 2.30 | 4.0 | 7.31 |
| Condo only | 23% | 46% | 32% | 2.44 | 4.1 | 10.23 |
| Timeshare / B&B | — | — | — | 2.42 / 2.12 | — | 9.36 / 8.53 |

- Parties = visitors ÷ party size (3+ average solved from reported mean). Rental-house parties 8% bigger than hotel parties, 3+ share 33% vs 29%, stay 2.2 days longer. Hawaii is a couples market → its 3+ share is a floor for Airbnb globally.
- Family travel ≈ 1 in 5 nights on Airbnb (H1 2024), +15% y/y, multigenerational +35%; 20% of Thanksgiving family bookings 10+ guests; ~40% of US listings 3+ bedrooms (Airbnb Newsroom Oct 2024).


## Hotels: the same distribution

| People per stay | 1 | 2 | 3 | 4 | 5+ | Mean | 3+ |
|---|---|---|---|---|---|---|---|
| **U.S. hotel, per travel party (est.)** | 45% | 39% | 7% | 6% | 4% | 1.87 | 17% |
| **U.S. hotel, per room-booking (est.)** | 42% | 48% | 7% | 2% | 0% | 1.69 | 9% |
| Portugal city + resort hotel, all completed bookings 2015–17 (n = 75,011) | 21% | 66% | 10% | 3% | 0% | 1.94 | 13% |
| — corporate segment | 80% | 19% | 2% | 0% | 0% | 1.22 | 2% |
| — leisure segments (OTA / direct / offline TA) | 16% | 70% | 11% | 4% | 0% | 2.04 | 15% |
| Hawaii hotel-only visitors 2024 (parties) | 29% | 43% | 29% (3+) | | | 2.30 | 29% |
| Las Vegas visitors 2024 (parties, n = 5,418) | 12% | 64% | 11% | 9% | 6% | 2.42 | 26% |
| Airbnb, per booking (fitted) | 16% | 36% | 21% | 12% | 16% | 2.97 | 48% |

- Two constructs: *per room-booking* (transactions lens; a family of 5 = 2 bookings) and *per travel party* (choice lens). Airbnb's number is both, since one listing holds the party.
- U.S. estimates = business share of room nights (42%: 439M business vs 605M leisure in 2023, AHLA 2024 SOTI) × the corporate booking shape + leisure share × (per-room: Portuguese leisure bookings; per-party: mean of Hawaii hotel-only and Las Vegas 2024).
- **Solo ≈ 45% of U.S. hotel stays vs 16% on Airbnb** (corporate bookings are 80% single-occupancy). **3+ ≈ 17% vs 48%.** Hotels host 4+ in one room in 3% of bookings and 5+ in 0.1%; big parties split rooms.
- Even leisure-only hotel markets are pair markets: Hawaii 43%, Vegas 64%, Portuguese leisure 70% pairs; Airbnb's 36% pairs is the lowest because both tails (solo long-stays, groups) are fatter.
- Portuguese nights by party: 1 → 2.5, 2 → 3.6, 3 → 3.7, 4 → 3.5 — bigger party, not longer, same as Airbnb past two people.
- Script: `analysis/src/hotel_party_size.py` (downloads the TidyTuesday mirror into gitignored `data/raw/`); output `data/processed/hotel_party_size_distribution.csv`.

## Capacity ≠ party size

- Inside Airbnb (8 cities, Jun 2026, 273k booked stays): room 13%, sleeps 1–2 12%, 3–4 23%, 5–6 20%, **7+ 33%**. Fitted parties 5+ = 16% → guests fill about half of listed capacity. `accommodates` is an upper bound, never an estimate.

## Method

- Max-entropy: P(1) fixed; sizes 2..8+ shifted-geometric with q chosen so mean = anchor. Central: P(1)=0.16, mean 2.97. Band: (0.19, 2.7) to (0.13, 3.1). Script: `analysis/src/party_size_distribution.py`.
- Caveats: fit, not a disclosed histogram; regional mix (NA 4.1 nights and biggest homes vs APAC 3.3) means a NA-only distribution sits right of global; Hawaii parties are self-reported immediate parties of air visitors.

## Pitch angles

- **Bull:** half of stays are 3+ — past the cost cross-over where an entire home beats two hotel rooms; group/family demand compounding faster than the platform (family +15%, bedroom nights +12% vs nights +10%, 4+ bedroom homes fastest-growing).
- **Bear:** Airbnb only knows the booker (<10% of groups add co-travellers) — thin data for loyalty; the 52% of bookings that are solo/couple are the contestable segment and couples pay ~20% more than a hotel room.
- **Next:** get a guest-count field (card panel won't have it; Airbnb guest survey or AirDNA "guests" field would); rerun Hawaii tables for 2019–2023 to see whether rental parties are growing vs hotel parties.

## Files

- `data/processed/airbnb_party_size_distribution.csv` — fitted distribution + band
- `data/processed/airbnb_party_size_evidence.csv` — every data point with source URL
- `data/processed/airbnb_guests_per_booking_windows.csv` — anchor-1 windows
- `data/processed/hawaii_party_size_by_accommodation_2024.csv`
- `data/processed/hotel_party_size_distribution.csv` · `analysis/src/hotel_party_size.py`
- `analysis/src/party_size_distribution.py` · `docs/figures/party_size_distribution.png` · `docs/party_size_distribution.html`

## Sources

- Airbnb 400M guest arrivals (Aug 2018): https://news.airbnb.com/airbnb-surpasses-400-million-guest-arrival-milestone/
- Airbnb 500M guest arrivals (Mar 2019): https://news.airbnb.com/airbnb-celebrates-half-a-billion-guest-arrivals/
- Airbnb S-1 (825M arrivals; 2017–19 nights): https://www.sec.gov/Archives/edgar/data/1559720/000119312520294801/d81668ds1.htm
- Airbnb 2-billionth guest arrival (1B Oct 2021, 2B Oct 2024): https://news.airbnb.com/the-power-of-2-meet-the-couple-marking-our-2-billionth-guest-arrival/
- Airbnb FY2025 10-K (2.5B arrivals; nights per booking): https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm
- Airbnb 2024 Summer Release (>80% group trips): https://news.airbnb.com/airbnb-2024-summer-release-highlights/
- Airbnb solo travel (24% of nights, 2022): https://news.airbnb.com/airbnb-expands-safety-product-to-help-solo-travelers-as-solo-travel-surges
- Airbnb 2023 Summer Release (private rooms): https://news.airbnb.com/airbnb-2023-summer-release-highlights/
- Airbnb family travel (Oct 2024): https://news.airbnb.com/how-and-where-families-are-traveling-this-thanksgiving/
- Airbnb Q2 2026 bedroom nights (Pulse2): https://pulse2.com/airbnb-guests-book-more-than-1-billion-bedroom-nights-in-one-year-as-group-travel-drives-growth/ ; call transcript: https://www.fool.com/earnings/call-transcripts/2026/08/13/airbnb-abnb-q2-2026-earnings-call-transcript/
- Hawaii DBEDT 2024 Annual Visitor Research Report (Tables 43–47): https://files.hawaii.gov/dbedt/economic/tourism/annual-reports/2024-annual-visitor.pdf
- Inside Airbnb: https://insideairbnb.com/get-the-data/
- Hotel Booking Demand datasets (Antonio, de Almeida & Nunes 2019, Data in Brief): https://www.sciencedirect.com/science/article/pii/S2352340918315191 ; mirror: https://github.com/rfordatascience/tidytuesday/tree/master/data/2020/2020-02-11
- AHLA 2024 State of the Industry (2023 room nights business 439M / leisure 605M): https://www.ahla.com/sites/default/files/SOTI.2024.Final_.Draft_.v4.pdf
- AHLA business share of room revenue via BTN: https://www.businesstravelnews.com/Lodging/AHLA-Business-Travel-Share-of-US-Hotel-Revenue-Down-Sharply-from-19
- Las Vegas Visitor Profile 2024 party size via Statista: https://www.statista.com/statistics/411714/party-size-of-las-vegas-visitors-us/
