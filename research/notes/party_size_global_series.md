# Party size over time, globally: Airbnb vs hotels vs other lodging

Built 7–8 Sep 2026. Goal: a time series of average party size for Airbnb and for competing lodging (STR, hotels, other) to see the trend, what drives it, and whether it extrapolates. Figure: `docs/figures/party_size_global_series.png`. Predecessors: `party_size_distribution.md` (the fitted Airbnb level), `hawaii_party_size_series.md` (the only observed by-accommodation series).

## The dataset

| Series | File | Coverage | Basis |
|---|---|---|---|
| **Airbnb party composition, global + 4 regions, quarterly** | `data/processed/abnb_party_size_reviews_quarterly.csv` | 2011Q1–2026Q2, 123 Inside Airbnb markets, 35 countries, 74m reviews | Review text: who the guest says they travelled with (solo / couple / family with kids / friends-group), explicit head-counts, and the reviewed listing's capacity. Raw and fixed-2019-market-weight versions |
| Airbnb by listing-capacity bucket × room type, year | `abnb_party_size_reviews_v2_by_bucket_year.csv`, `_decomposition.csv` | 2011–2025 | Same flags; splits mix shift toward big homes from change within a home size |
| Airbnb global monthly + seasonal index | `abnb_party_size_reviews_v2_global_month.csv`, `_seasonal_index.csv` | 2013-01–2026-06 | |
| Airbnb by review language | `abnb_party_size_reviews_v2_by_language_year.csv` | | Mention-rate bias check |
| Per-market detail | `abnb_party_size_reviews_market_quarter_shard*.csv`, `_v2_bucket_quarter_shard*.csv`, `_v2_market_month_shard*.csv` | | |
| **Airbnb disclosures ledger** | `abnb_party_size_disclosures.csv` (28 dated points), `abnb_newsroom_party_mentions.csv` (989 numeric sentences, 296 posts, 2017–2026) | 2017–2026 | Letters, calls, 10-K, newsroom |
| **Hawaii DBEDT by accommodation** (rental house / hotel / condo / timeshare / B&B), annual; all visitors monthly | `hawaii_party_size_annual*.csv`, `hawaii_party_size_monthly.csv` | 1999–2024; 2013-01–2026-07 | Survey, observed party size |
| **Booking.com hotels, Europe, monthly** | `booking_515k_guest_type_monthly.csv` | 2015-08–2017-08, 515k reviews, 1,493 hotels | Reviewer-declared traveller type |
| **Booking.com by accommodation type × month, 2023** | `booking_rectour24_guest_type_by_type_month.csv`, `_by_country_type.csv` | 2023, 1.63m stays | Declared guest_type: hotel vs apartment vs holiday home etc. **CC BY-SA 4.0 non-commercial licence** |
| Portugal hotel ledger quarterly | `hotel_party_size_portugal_quarterly.csv` | 2015Q3–2017Q3 | Adults+children per booking, city vs resort |
| All comparators, one long table | `party_size_benchmarks.csv` | | + Las Vegas guests per room (2.2, 2024–25), NTTO inbound-US composition (60% alone, 2024–25) |

Scripts: `analysis/src/abnb_party_size_reviews.py` (+`_v2`, `_aggregate`, `_v2_aggregate`), `booking_party_composition.py`, `abnb_newsroom_party_mentions.py`, `party_size_benchmarks.py`, `party_size_validate_hawaii.py`, `party_size_global_figures.py`; orchestration `overnight_party_size.sh`. Raw inputs are gitignored (`data/raw/inside_airbnb_reviews/` 7.6 GB, `data/raw/booking/`, `data/raw/abnb_newsroom/`).

## How the Airbnb series is built and why it can be trusted

Airbnb never discloses guests per booking. Inside Airbnb publishes every review a listing has ever received, so one current snapshot per market gives the full 2009→2026 history. A review "states composition" when it says who travelled ("my wife and I", "family of five", "the six of us", "éramos 4", "zu viert", …; patterns in en/es/fr/it/de/pt). 6–13% of reviews do (13% in 2013, ~6% since 2018 as reviews got shorter); ~2% give an explicit head-count. Everything reported is the composition *among reviews that state it*, plus the head-count mean and the capacity of the listing reviewed.

- **Implied party size** = solo 1 · couple 2 · family 3.9 · group 4.7 (family/group weights from the stated head-counts). It is an index of composition, not a calibrated level.
- **Validation (`party_size_validation_hawaii.csv`)**: for Inside Airbnb's Hawaii market, the text-derived series tracks DBEDT's observed rental-house party size 2013–2024 (ex-2020/21) at **r = 0.96** (implied size), **0.98** (family share and head-count mean) and **0.99** (capacity of reviewed listing). Direction and timing are right; the level is not (Airbnb text implies ~3.5 in Hawaii vs 2.5 observed, because couples under-state and families/groups over-state who they were with).
- **Fixed-market weights**: the `fixed_2019` version holds every market at its 2019 share of reviews, so Inside Airbnb adding cities or one city booming cannot masquerade as a trend. Raw and fixed versions move together.
- **Language check**: English carries 80% of stated compositions (7.8% mention rate vs 1–4% in other languages). The English-only series shows the same trend (family 29% → 46%, implied 3.24 → 3.66, 2011 → 2025), so it is not a language-mix artefact.

## What the data say

**1. Airbnb parties have been getting bigger since 2012, and the shift is families replacing couples — not more friend-groups.** Global, fixed weights, share of reviews stating composition:

| | 2012 | 2015 | 2019 | 2021 | 2023 | 2025 | 1H26 |
|---|---|---|---|---|---|---|---|
| Couple | 50% | 40% | 34% | 38% | 28% | 25% | 19% |
| Family with kids | 31% | 34% | 38% | 37% | 43% | 46% | 50% |
| Friends / group | 25% | 30% | 29% | 25% | 28% | 28% | 30% |
| Solo | 4% | 3% | 5% | 6% | 6% | 6% | 6% |
| Implied party size | 3.12 | 3.34 | 3.37 | 3.25 | 3.44 | 3.50 | 3.63 |
| Stated head-count, mean | 4.3 | 4.7 | 5.0 | 4.8 | 4.9 | 5.0 | 4.9 |
| Capacity of listing reviewed | 3.3 | 3.5 | 3.7 | 3.8 | 3.8 | 3.9 | 3.9 |
| Share of reviews on listings sleeping 5+ | 17% | 20% | 24% | 24% | 26% | 27% | 25% |

(1H26 is Q1–Q2 only; family share is seasonally low in Q1 and high in Q2–Q3, so treat it as ≈ 2025.) Two regimes: 2012–2016 the couple share fell ~2.5 pts a year while families and groups both rose; 2017–2019 flat; 2020–21 a couples spike (COVID); 2022–2025 the couple share fell another ~4 pts a year, all of it into families. Solo is small and flat — solo travellers rarely say so in a review, which is also why the solo share here is a fifth of Airbnb's disclosed 24–26% of *nights*.

**2. Regions move together; Latin America is a level lower.** North America 3.2 → 3.5 (2014 → 2025), EMEA 3.3 → 3.5, APAC 3.2 → 3.5, LatAm 3.0 → 3.25. NA lagged Europe until 2019 and has caught up since 2022 — consistent with Airbnb's letters calling out North American groups of 5+ growing fastest (+15–16% y/y in 1H24).

**3. Drivers: the size rise is a capacity-mix story; the family rise is within-home-size.** Decomposing the bucket-weighted implied party size 2014–16 → 2023–25 (`_v2_decomposition.csv`):

| | 2014–16 | 2023–25 |
|---|---|---|
| Share of stated compositions on entire homes sleeping 5–6 / 7+ | 19% / 13% | 25% / 24% |
| … sleeping 1–2 (entire) / private rooms | 23% / 12% | 15% / 6% |
| Implied party size within "sleeps 3–4" | 3.63 | 3.57 |
| Family share within "sleeps 3–4" / "sleeps 5–6" / "7+" | 40% / 51% / 40% | 49% / 64% / 51% |

Total change +0.08 = **mix +0.23** (demand migrating to bigger homes, private rooms halving) **and within-bucket −0.15** (within any given home size the party got *smaller*: friend-groups and couples replaced by families, and a family of 3–4 is smaller than a friend-group of 5). So "Airbnb parties are bigger" is true because guests book bigger homes, not because the same homes host bigger groups; and "Airbnb is more of a family product" is true within every home size (family share +9 to +13 pts in each bucket). Both are what the supply data show too: entire homes' share of reviews 67% (2011) → 83% (2020+), 4+ bedroom homes Airbnb's fastest-growing category, bedroom-nights growing 2 pts faster than nights.

**4. Seasonality is a family-calendar effect, ±3% on implied size, ±20% on family share.** Monthly global index (month ÷ annual mean, normal years): family share Jul 1.19, Dec 1.18, Aug 1.15, Sep 0.84; solo Sep–Nov 1.17–1.24, Jul–Aug 0.82; couples Feb 1.14 (Valentine's), Jul–Aug 0.86–0.87; friend-groups May 1.09, Dec 0.85. Implied party size only Jul–Aug +2.7%, Feb/Sep −2.5%: composition swings offset (families up when groups and couples are down). Hawaii's observed all-visitor party size swings ±10% for the same reason — families are also *larger* in summer — which the composition-only proxy cannot see.

**5. Comparators: hotels are ~1 person smaller and not trending.** People per party / implied:

| | 2013 | 2015 | 2017 | 2019 | 2022 | 2024 |
|---|---|---|---|---|---|---|
| Airbnb reviews, global (implied) | 3.23 | 3.34 | 3.35 | 3.37 | 3.37 | 3.47 |
| Hawaii rental house (observed) | 2.28 | 2.30 | 2.35 | 2.41 | 2.42 | 2.49 |
| Hawaii hotel (observed) | 2.22 | 2.25 | 2.27 | 2.29 | 2.26 | 2.30 |
| Booking.com hotels Europe (implied from declared type) | | 2.5 (2015Q4) | 2.8 (2017Q3) | | | |
| Portugal 2-hotel ledger (adults+children/booking) | | 1.8 | 2.0 (2017Q2) | | | |

- Booking.com 2023 (1.63m stays, declared guest type): hotels 2.66 implied (solo 18%, couple 43%, family 28%, group 12%), apartments 3.03 (family 33%, group 19%), **holiday homes 3.17** (solo 7%, family 36%, group 20%), resorts 2.98, hostels 1.86. The same platform sells to the same travellers, so this is the cleanest cross-section: whole-home rentals carry ~0.4–0.5 more people per party than hotels and half the solo share — the same gap DBEDT observes in Hawaii (rental house 2.49 vs hotel 2.30) and the same ordering the Airbnb text series implies.
- Booking.com Europe hotels 2015–17: composition drifted the *other* way from Airbnb over the same two years (couples 60% → 49%, families 14% → 22%, groups 12% → 18% — hotel parties also grew), so 2015–17 was a market-wide move toward families, not an Airbnb share gain; Airbnb's divergence from hotels is post-2021.
- Hawaii hotels: 2.13 → 2.30 over 25 years, most of it 2019–24; rental-house parties +0.21 since 2013 vs hotels +0.09; 3+ share 34% vs 29%.
- Airbnb's own numbers are consistent with all of this: family = 27% of nights summer 2019 → 33% summer 2021 → "~1 in 5 nights" 2024 on a stricter definition, multigenerational +35–72% y/y in the years disclosed, 81% of trips 2+ guests, groups of 5+ the fastest-growing segment in NA and EMEA. One inconsistency to carry: Chesky's "the average number of guests is two" (Q1'24 call) vs ~3.0 from cumulative guest arrivals ÷ bookings; the former reads as a loose remark about the *median*, but it is on the record.

## Can it be extrapolated?

- The series is trend-stationary in composition, not size: family share has risen ~1.5 pts a year for a decade (2.5–4 pts a year outside 2017–19), and the implied party size follows at ~+0.03/yr. Mechanically that is another ~+0.1 people per party by 2028 if the couple → family substitution continues; the ceiling is the friend-group share, which has not moved in 12 years.
- For ABNB modelling the operative variables are the ones in the decomposition: the capacity mix of booked listings (drives ADR per night and bedroom-nights growth) and the within-size family share (drives LOS — families stay longer — and seasonality). Both are observable quarterly here at market level, one quarter ahead of Airbnb's letters.
- What would break the extrapolation: a hotel-style shift back to couples/solo (the 2020–21 pattern), which showed up in this series within one quarter; or Airbnb's supply mix stopping its drift to large homes (the `accommodates_ge5` share flattened in 2025–26 at 25–27% after rising every year to 2024 — worth watching).

## Caveats

- Proxy, not measurement: composition is conditional on the guest mentioning it; mention rates halved 2013→2019 and differ by traveller type. The Hawaii validation says the *trend* survives this; the level does not.
- "Family" = mentions of kids/children/parents; a childless family gathering is coded as group or couple. "Group" catches friends, colleagues, stag/hen parties.
- Capacity is the listing's *current* `accommodates`; listings delisted before the snapshot have none (they are missing from the bucket series, not mis-bucketed), and a listing's capacity can have changed.
- Review dates lag stays by days to weeks; quarters are review quarters.
- Booking.com RecTour24 is licensed non-commercial; use for internal comparison only unless cleared.

## Sources

- Inside Airbnb, https://insideairbnb.com/get-the-data/ (CC BY 4.0), 123 `reviews.csv.gz` + `listings.csv.gz`, snapshots Jun–Jul 2026; manifest `data/raw/inside_airbnb_reviews/reviews_manifest.csv`
- Airbnb shareholder letters and earnings-call transcripts in `data/raw/letters`, `data/raw/regulatory/transcripts`; Airbnb Newsroom sitemap crawl (`data/raw/abnb_newsroom/`)
- Hawaii DBEDT Annual Visitor Research Reports and monthly Visitor Highlights (see `hawaii_party_size_series.md`)
- Booking.com 515K Hotel Reviews in Europe (Kaggle jiashenliu; HF mirror Dricz/515k-Hotel-Reviews-In-Europe); Booking.com RecTour 2024 accommodation-reviews (HF Booking-com/accommodation-reviews, `rectour24/train_users.csv`)
- Antonio, de Almeida & Nunes (2019) hotel booking demand datasets; LVCVA 2025 Las Vegas Visitor Profile Study; NTTO Survey of International Air Travelers 2024 and 2025 results
