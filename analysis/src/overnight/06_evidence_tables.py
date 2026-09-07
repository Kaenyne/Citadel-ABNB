"""Workstream 06: the curated evidence tables behind the note.

These are hand-entered from primary sources (shareholder letters, earnings-call transcripts, the five
Third Bridge expert PDFs, published surveys and academic papers) and emitted as CSV so every number in
the note is machine-readable and carries its citation. The script is the source of truth; edit here.

Writes: data/processed/overnight/06_company_evidence.csv     Airbnb's own disclosures on price, mix, fees, take rate
        data/processed/overnight/06_expert_call_evidence.csv the five Third Bridge calls
        data/processed/overnight/06_choice_drivers.csv       third-party survey and market evidence on choice
        data/processed/overnight/06_elasticities.csv         elasticity / sensitivity table with confidence
        data/processed/overnight/06_fee_timeline.csv         dated fee and total-price-display history
Run: py -3.13 analysis/src/overnight/06_evidence_tables.py
"""
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
OUT = os.path.join(ROOT, "data", "processed", "overnight")

# --------------------------------------------------------------------------------------------
# 1. Airbnb's own disclosures. `evidence` = a fact the company published; `opinion` = management view.
#    Quotes are <=25 words; longer statements are paraphrased.
# --------------------------------------------------------------------------------------------
COMPANY = [
    # --- price vs hotels -------------------------------------------------------------------
    ("3Q23 letter", "price_vs_hotel", "evidence", "Average nightly price of a one-bedroom Airbnb listing in September 2023 vs hotel ADR; prices include all fees, exclude taxes; sources CoStar and Airbnb", "ABNB 1BR $120 (+1% y/y); hotel $153 (+10% y/y)"),
    ("4Q23 letter", "price_vs_hotel", "evidence", "Same comparison for December 2023", "ABNB 1BR $114 (-2% y/y); hotel $149 (+7% y/y)"),
    ("2Q24 call (reported by Skift 22-May-2024)", "price_vs_hotel", "evidence", "March 2024 comparison reported by Skift from Airbnb and CoStar", "ABNB 1BR $114 (-2% y/y); hotel ADR $140.16 (+1.6% y/y); economy hotels $64.70, midscale $73.70"),
    ("1Q23 letter", "price_vs_hotel", "evidence", "Airbnb Rooms (private rooms) average price at the 2023 Summer Release", "$67 per night; over 80% under $100 per night"),
    ("2Q26 call", "price_vs_hotel", "opinion", "Chesky: Airbnb is building a new AI pricing model for hosts that ingests hotel prices, Airbnb prices, events and lead-time patterns", "n/a"),

    # --- ADR: price vs mix -----------------------------------------------------------------
    ("3Q22 letter", "adr_driver", "evidence", "ADR $156, +5% y/y (+12% ex-FX); increase entirely price appreciation, partly offset by negative urban mix", "ADR $156; +5% reported / +12% ex-FX"),
    ("4Q22 letter", "adr_driver", "evidence", "ADR $153, -1% y/y (+5% ex-FX); decline driven by FX and urban mix shift", "ADR $153; -1% / +5% ex-FX"),
    ("1Q23 letter", "adr_driver", "evidence", "ADR $168, flat y/y (+3% ex-FX); price appreciation offset by FX", "ADR $168; 0% / +3% ex-FX"),
    ("2Q23 letter", "adr_driver", "evidence", "ADR $166, +1% y/y (+2% ex-FX); host list-price increases offset by guest mix", "ADR $166; +1% / +2% ex-FX"),
    ("3Q23 letter", "adr_driver", "evidence", "ADR $161, +3% y/y (+<1% ex-FX), partly mix shift; ex-FX ADR down in North America", "ADR $161; +3% / <+1% ex-FX"),
    ("4Q23 letter", "adr_driver", "evidence", "ADR $157, +3% y/y (+<1% ex-FX), partly mix shift; ex-FX flat in North America", "ADR $157; +3% / <+1% ex-FX"),
    ("1Q24 letter", "adr_driver", "evidence", "ADR $173, +3% y/y (+2% ex-FX), largely price appreciation", "ADR $173; +3% / +2% ex-FX"),
    ("2Q24 letter", "adr_driver", "evidence", "ADR $170, +2% y/y (+3% ex-FX), price appreciation and mix shift", "ADR $170; +2% / +3% ex-FX"),
    ("3Q24 letter", "adr_driver", "evidence", "ADR $164, +1% y/y (+2% ex-FX), price appreciation and mix shift", "ADR $164; +1% / +2% ex-FX"),
    ("4Q24 letter", "adr_driver", "evidence", "ADR +6% reported and FX-neutral, price appreciation and mix shift", "ADR $158; +6% / +6% ex-FX"),
    ("1Q25 letter", "adr_driver", "evidence", "ADR $171, -1% y/y (+1% ex-FX), largely price appreciation; FX headwind", "ADR $171; -1% / +1% ex-FX"),
    ("2Q25 letter", "adr_driver", "evidence", "ADR $174, +3% y/y (+1% ex-FX), largely price appreciation", "ADR $174; +3% / +1% ex-FX"),
    ("3Q25 letter", "adr_driver", "evidence", "ADR $171, +5% y/y (+2% ex-FX), largely price appreciation", "ADR $171; +5% / +2% ex-FX"),
    ("4Q25 letter", "adr_driver", "evidence", "ADR $168, +6% y/y (+3% ex-FX), largely price appreciation", "ADR $168; +6% / +3% ex-FX"),
    ("1Q26 letter", "adr_driver", "evidence", "ADR $187, +9% y/y (+4% ex-FX); FX tailwind plus strong North America ADR", "ADR $187; +9% / +4% ex-FX"),
    ("2Q26 letter", "adr_driver", "evidence", "ADR $184, +5% y/y (+4% ex-FX), price appreciation AND mix: entire homes, especially 4+ bedroom listings, grew fastest", "ADR $184; +5% / +4% ex-FX"),
    ("2Q26 letter", "adr_driver", "evidence", "Bedroom Nights Booked (nights x bedroom count) grew over 12% vs Nights and Seats Booked +10%; more than 1 billion bedroom nights over the trailing twelve months, a record", "bedroom nights +12% vs nights +10%; >1.0bn LTM"),
    ("2Q26 call", "adr_driver", "opinion", "Mertz: the bedroom-nights component of ADR growth is durable and reflects incremental value delivered, not just rising prices", "n/a"),

    # --- mix and guest behaviour -----------------------------------------------------------
    ("1Q21 letter", "mix", "evidence", "Share of nights from stays of at least seven nights", "50% (1Q21)"),
    ("3Q22 letter", "mix", "evidence", "Share of gross nights from stays of at least seven nights", "~45% (3Q22)"),
    ("4Q22 letter", "mix", "evidence", "Share of gross nights from stays of at least seven nights", "~46% (4Q22)"),
    ("2Q23 letter", "mix", "evidence", "Share of gross nights from stays of at least seven nights", "~45% (2Q23)"),
    ("3Q21-1Q24 letters", "mix", "evidence", "Long-term stays (28+ days) as share of gross nights booked: 20% (3Q21), 22% (4Q21), 20% (3Q22), 21% (4Q22), 18% (1Q23), 18% (2Q23), 18% (3Q23), 19% (4Q23), 17% (1Q24)", "20-22% in 2021-22 falling to 17% by 1Q24"),
    ("2Q24 onward", "mix", "evidence", "The letters stop giving a Trip Length section with the 28-day share; no long-term-stay percentage is disclosed after 1Q24. Disclosure change, not a trend", "not disclosed after 1Q24"),
    ("4Q22 letter", "mix", "evidence", "High-density urban share of gross nights booked", "51% (4Q22); 48-49% through 2023"),
    ("4Q25 letter", "mix", "evidence", "App share of nights booked, and app nights growth", "64% of nights (4Q25) vs 60% (4Q24); app nights +20% y/y"),
    ("1Q26 letter", "mix", "evidence", "App share of nights booked", "63% (1Q26) vs 58% (1Q25); app nights +22% y/y"),
    ("2Q26 letter", "mix", "evidence", "App share of nights booked", "64% (2Q26) vs 59% (2Q25); app nights +23% y/y"),
    ("4Q25-2Q26 letters", "new_guests", "evidence", "First-time booker growth y/y", "+8% (4Q25), +10% (1Q26, highest since early 2022), +11% (2Q26, highest in four years)"),
    ("1Q26 letter", "hotel_funnel", "evidence", "Share of guests who book a hotel on Airbnb who return to book a home", "~55%"),
    ("2Q26 call", "hotel_funnel", "evidence", "Chesky: about 35% of people who book a hotel on Airbnb for the first time come back and book a home", "~35%"),
    ("2Q26 call", "substitution", "opinion", "Chesky's segmentation of demand: some people only stay in homes, some only in hotels, and most are willing to stay in both", "three segments, unquantified"),

    # --- fees, total price, cancellation ----------------------------------------------------
    ("4Q22 letter", "fees", "evidence", "December 2022: optional total-price display rolled out; guests who opt in see the total before taxes in search, map, price filter and listing page", "opt-in toggle"),
    ("1Q23 letter", "fees", "evidence", "2023 Summer Release: 50+ features including new host pricing and discount tools, checkout-instruction transparency, removal of listings with unreasonable checkout tasks, and reduced guest service fee after three months on long stays", "50+ features"),
    ("2Q23 letter", "fees", "evidence", "Since the Summer Release more hosts adopted discounting tools and lowered prices; more offering weekly and monthly discounts", "qualitative"),
    ("3Q23 letter", "fees", "evidence", "Airbnb frames lower prices and lower cleaning fees as the top two host-facing asks from guests", "qualitative"),
    ("4Q25 letter", "fees", "evidence", "From October 2025 Airbnb began simplifying its fee structure, migrating property-management-software hosts from the split fee (3% host + separate guest service fee) to a single 15.5% host fee", "single fee 15.5%"),
    ("1Q26 letter", "fees", "evidence", "Over a quarter of active listings subject to the single service fee; hosts can adjust prices to keep the same net earnings; guests continue to see the full price upfront", ">25% of active listings"),
    ("1Q26 call", "fees", "evidence", "Mertz: Reserve Now Pay Later, redesigned cancellation policies and the single-fee migration together delivered about 3 points of nights growth and about 4 points of GBV growth in Q1 2026", "+3pp nights, +4pp GBV"),
    ("2Q26 letter", "fees", "evidence", "Approximately half of active listings on the single fee; in July Airbnb announced migration of most remaining hosts, to complete in 2026", "~50% of active listings"),
    ("2Q26 letter", "cancellation", "evidence", "Eligible listings migrated from Strict to Firm cancellation policies to help hosts attract more bookings", "qualitative"),
    ("2Q26 call", "fees", "opinion", "Chesky on total price display: it began as a toggle, was positive for those who used it, and the same staged approach is being used for AI search", "qualitative"),

    # --- take rate --------------------------------------------------------------------------
    ("2Q23 call", "take_rate", "opinion", "Chesky: cutting the take rate after the third month of a long stay drove incremental conversion; he does not expect the take rate to change materially", "stable"),
    ("3Q23 call", "take_rate", "opinion", "Stephenson: the take rate has been very stable; no recent change to the absolute take rate; further monetisation comes from added services, e.g. guest travel insurance", "stable"),
    ("4Q23 call", "take_rate", "opinion", "Stephenson: no real reason take rates should rise on a timing-adjusted basis; pricing as a percentage of GBV has not materially changed", "stable"),
    ("4Q24 call", "take_rate", "evidence", "Mertz: an FX service fee introduced mid-2024, about 100bps applied to 20% of GBV, gives a full 20bps year-over-year take-rate benefit in 2025", "+20bps"),
    ("1Q25 call", "take_rate", "opinion", "Chesky: almost everything built for hosts in the last five years was given away with no incremental take rate; several host-side monetisation options are being looked at", "qualitative"),
    ("1Q26 call", "take_rate", "opinion", "Mertz: expect modest upside to the take rate from the single-fee migration and the insurance programmes; the Delta revenue share is not a take-rate negative", "modest upside"),
    ("1Q26 letter", "take_rate", "evidence", "Implied take rate 9.2% in Q1 2026 vs 9.3% in Q1 2025; affected by FX and by Reserve Now Pay Later pushing bookings further ahead of stays", "9.2% vs 9.3%"),
    ("4Q25 letter", "take_rate", "evidence", "Implied take rate 13.6% in Q4 2025 vs 14.1% in Q4 2024, mainly FX and book-vs-stay timing", "13.6% vs 14.1%"),
    ("2Q26 letter", "take_rate", "evidence", "Implied take rate 13.2% in Q2 2026, in line with Q2 2025; FX and Reserve Now Pay Later timing", "13.2% flat"),
    ("2Q26 call", "take_rate", "evidence", "Mertz: full-year 2026 implied take rate relatively flat vs 2025 on RNPL timing and higher customer incentives for new businesses; absent those it would have been slightly higher", "flat, would be higher"),
    ("4Q25-2Q26 letters", "take_rate", "evidence", "Guest travel insurance revenue growth, available in 12 of the largest countries", "+~40% FY25, +45% 1Q26, +>60% 2Q26"),
    ("1Q26/2Q26 letters", "take_rate", "evidence", "Reserve Now Pay Later share of GBV", "~20% (1Q26), over 20% (2Q26)"),
    ("2Q25 call", "take_rate", "opinion", "Chesky on hotels: Airbnb's take rate is very competitive and independent and boutique hotels want an additional channel bringing incremental travellers", "qualitative"),
    ("2Q26 call", "take_rate", "opinion", "Chesky on why hotels join: Airbnb has heavy traffic, a young and disproportionately American audience, and an extremely favourable take rate", "qualitative"),

    # --- quality and trust -------------------------------------------------------------------
    ("1Q24 letter", "quality", "evidence", "Guest Favorites launched November 2023; over 100 million nights booked at Guest Favorite listings since launch", ">100m nights"),
    ("4Q23 letter", "quality", "evidence", "Host cancellations fell 36% in Q4 2023 vs the prior-year period", "-36%"),
]

# --------------------------------------------------------------------------------------------
# 2. Third Bridge expert calls. Licensed research: everything paraphrased, quotes <=25 words.
# --------------------------------------------------------------------------------------------
EXPERT = [
    ("US VRM (MD, US full-service short-term rental manager)", "2-Jun-2026", "guest_choice", "observed",
     "Vacation rentals sit on the value side of leisure and have been fairly resilient in downturns; a group of six to eight splits the cost and cooks in, which makes the stay affordable", "group of 6-8"),
    ("US VRM", "2-Jun-2026", "demand_2026", "opinion",
     "Most of the industry is doing extremely well in 2026 because air and international travel have got more expensive and people still want a vacation, just an affordable one", "n/a"),
    ("US VRM", "2-Jun-2026", "host_economics", "observed",
     "A property manager takes 20-25% of rental income; the homeowner keeps 75-80%. The manager keeps 100% of the fees (housekeeping, damage waiver, booking fee)", "20-25% commission"),
    ("US VRM", "2-Jun-2026", "host_economics", "observed",
     "Management commission rates have been broadly stable, down slightly since 2018 when Vacasa and TurnKey competed on fees; the decline is gradual and unquantified", "slight decline"),
    ("US VRM", "2-Jun-2026", "take_rate", "observed",
     "Of a $100 nightly rate, roughly $15 goes to Airbnb. Typical manager take rate about 30%; typical platform about 40% (on the manager's own definition of the revenue base)", "$15 per $100; 30% / 40%"),
    ("US VRM", "2-Jun-2026", "take_rate", "opinion",
     "Airbnb could not push fees to 20% without consequence: it competes with Booking.com and Vrbo for supply and must stay supplier-friendly; managers would reallocate inventory", "n/a"),
    ("US VRM", "2-Jun-2026", "channel_mix", "observed",
     "Airbnb has lost the supply exclusivity it once had; platforms now compete for large suppliers with revenue-target rebates and paid placement, Vrbo most aggressively", "n/a"),
    ("US VRM", "2-Jun-2026", "channel_mix", "opinion",
     "In this market the property managers hold the power because the OTAs need the supply; on Airbnb specifically the expert says it has its back against the wall on supply", "n/a"),
    ("US VRM", "2-Jun-2026", "cycle", "observed",
     "In 2009-10 the industry saw some ADR decline but made it up on occupancy; managers also picked up failed competitors", "n/a"),

    ("UK/Europe VR (former C-level, Awaze Vacation Rentals)", "26-May-2026", "pricing_power", "observed",
     "Campaigns and discounts come out of the manager's own margin once the price falls below the corridor agreed with the homeowner", "n/a"),
    ("UK/Europe VR", "26-May-2026", "take_rate", "observed",
     "Airbnb and the other big platforms charge 15-16% in Europe, which leaves a managed-rental business with very little after its own costs", "15-16%"),
    ("UK/Europe VR", "26-May-2026", "take_rate", "opinion",
     "The risk of commission cuts is low because Airbnb and the rest have set a plateau; managed rentals will always carry a higher take rate because of the added services", "plateau"),
    ("UK/Europe VR", "26-May-2026", "demand", "observed",
     "European vacation rental has grown at only very low single digits since 2023; utility, fuel and inflation pressure on household budgets is the constraint", "very low single digit"),
    ("UK/Europe VR", "26-May-2026", "supply", "observed",
     "Roughly 18 million second homes in Europe, of which about 15 million are never let out; only about 3 million are in the rental pool", "18m / 15m / ~3m"),
    ("UK/Europe VR", "26-May-2026", "supply", "opinion",
     "Buy-to-let and second-home letting is becoming less attractive in the UK on tax; owners are trying to exit", "n/a"),

    ("India alt-accom (senior exec, revenue management, MakeMyTrip)", "19-Aug-2026", "market_size", "observed",
     "Indian domestic hotel market roughly INR 400 crore per day of bookings; alternative accommodation about INR 30 crore per day, roughly 8%, about USD 1.2bn a year. Educated estimate, not published data", "~8% of hotel"),
    ("India alt-accom", "19-Aug-2026", "occupancy", "observed",
     "Hotels run 60-65% occupancy; non-hotel alternative accommodation typically 40%, because the use case is weekend leisure", "60-65% vs 40%"),
    ("India alt-accom", "19-Aug-2026", "price_vs_hotel", "observed",
     "A villa is about three rooms; branded operators charge a premium, but unbranded villas typically price at the same level as a hotel on a per-room basis", "per-room parity"),
    ("India alt-accom", "19-Aug-2026", "price_vs_hotel", "observed",
     "Branded villa operators price at a large multiple of the market average: StayVista about 3x, Elivaas about 2 to 2.5x", "3x / 2-2.5x"),
    ("India alt-accom", "19-Aug-2026", "fees", "observed",
     "Airbnb used to charge standalone hosts (no channel manager) a low commission plus a guest service fee, and channel-manager-connected hosts a higher one. That gap is being removed, taking away the reason standalone hosts stayed unbranded and helping the aggregators", "n/a"),
    ("India alt-accom", "19-Aug-2026", "growth", "opinion",
     "The category will keep growing faster than hotels but will not become a major share; Indian hotels growing around 12-13% in 2026", "hotels +12-13%"),

    ("Booking Holdings (former Director, Commercial Excellence Americas)", "30-Jul-2026", "loyalty", "observed",
     "Booking.com direct traffic is high-50s to mid-60s percent; Genius level 2 and 3 members drive high-50s to low-60s percent of room nights, up about 5 points year over year", "~60% of room nights"),
    ("Booking Holdings", "30-Jul-2026", "take_rate", "observed",
     "Booking's net take rate was around 14.5% in 2025, slightly up on 2024; it was 15-16% before the pandemic", "14.5% (2025)"),
    ("Booking Holdings", "30-Jul-2026", "take_rate", "opinion",
     "The expert expects a small improvement over 12-24 months against a sell-side view of a 30bp fall to about 13.6%; he sees nothing that pushes OTA take rates materially above the low teens", "13-14% ceiling"),
    ("Booking Holdings", "30-Jul-2026", "consumer", "opinion",
     "Leisure travel carries a large emotional and financial investment, so travellers keep shopping several options before booking; that is also why AI will not replace the OTA booking engine soon", "n/a"),

    ("OTA AI disruption (principal PM, ML and AI, Booking Holdings)", "14-Aug-2026", "ai_channel", "opinion",
     "Only about 3% of accommodation bookings are likely to shift to AI-native transactions in the next 12-24 months; the barrier is trust, since a trip is typically over USD 1,000", "~3%"),
    ("OTA AI disruption", "14-Aug-2026", "ai_channel", "opinion",
     "OTAs took about 30 years from 1996 to reach roughly 50% share, so AI challengers taking 50% within two years is implausible", "n/a"),
]

# --------------------------------------------------------------------------------------------
# 3. Third-party market and survey evidence on how travellers choose.
# --------------------------------------------------------------------------------------------
CHOICE = [
    ("AirDNA U.S. Review, July 2026", "2026-07", "us_str_market", "US short-term-rental market: ADR $317.55 (+6.9% y/y), RevPAR $217.17 (+7.2%), occupancy 68.4% (+0.3%), demand nights +2.0%, available supply +2.6%", "https://www.airdna.co/blog/u.s.-review-july-2026"),
    ("AirDNA U.S. Review, June 2026", "2026-06", "us_str_market", "ADR $310.64 (+4.6%), RevPAR $200.19 (+4.5%), occupancy 64.4% (-0.1%), demand +1.9%, supply +1.7%", "https://www.airdna.co/blog/u.s.-review-june-2026"),
    ("AirDNA U.S. Review, December 2025", "2025-12", "us_str_market", "December ADR $248.57 (+3.3%), RevPAR $126.97 (+1.8%), occupancy 51.0%; FY2025 occupancy 56.9% (+0.2pp), ADR +1.8%", "https://www.airdna.co/blog/us-review-december-2025"),
    ("AirDNA U.S. Review, December 2024", "2024-12", "us_str_market", "FY2024 demand +6.8%, supply +3.3%, occupancy 56.7% (+0.3pp), RevPAR +3.7%", "https://www.airdna.co/blog/us-review-december-2024"),
    ("AirDNA European Review, July 2026", "2026-07", "eu_str_market", "Europe ADR EUR 159.2 (+8.2% y/y), RevPAR EUR 110.1 (+7.7%), occupancy 69.2% (-0.3pp), demand +0.8%, listings +1.9%", "https://www.airdna.co/blog/european-review-july-2026"),
    ("AirDNA European Review, 2025", "2025-12", "eu_str_market", "Europe FY2025 ADR EUR 130 (-1.1%), RevPAR EUR 76 (-0.4%), occupancy 58.7-59% (+0.7pp), demand nights 470m (+4.4%), listings +3.5%", "https://www.airdna.co/blog/european-review-december-2025"),
    ("CoStar / Business Travel News, 26-Aug-2026", "2026-07", "us_hotel", "US hotels July 2026: ADR $171.74 (+5.7%), RevPAR $119.77 (+8.2%), occupancy 69.7% (+2.3%); sixth consecutive month of gains; 22 of the top 25 markets grew RevPAR", "https://www.businesstravelnews.com/Lodging/CoStar-US-Hotels-Grow-Occupancy-Rate-in-July"),
    ("CoStar / Business Travel News, 20-Jan-2026", "2025-12", "us_hotel", "US hotels full-year 2025: occupancy 62.3% (-1.2pp), ADR $160.54 (+0.9%), RevPAR $100.02 (-0.3%); first annual occupancy and RevPAR decline since 2020", "https://www.businesstravelnews.com/Lodging/CoStar-25-U.S.-Hotel-Occupancy-RevPAR-Decline"),
    ("CoStar / Tourism Economics forecast, 7-Aug-2026", "2026-08", "us_hotel_forecast", "2026 US hotel forecast raised to RevPAR +4.4%, ADR +3.1%, occupancy 63.1%; 2027 RevPAR +2.1%, ADR +1.6%, occupancy 63.4%", "https://www.asianhospitality.com/us-hotel-forecast-2026-costar-tourism-economics/"),
    ("Barclays brand RevPAR tracker via Asian Hospitality, 24-Aug-2026", "2026-07", "us_hotel_segment", "July 2026 RevPAR by brand: Marriott +9.5%, Hilton +7.9%, Hyatt +10.9%, Choice +5.8%, Wyndham +5.2%. By segment: luxury RevPAR +17.7% and ADR +14.5%; economy RevPAR +3.6%; group +14%, transient +11%", "https://www.asianhospitality.com/us-hotel-revpar-up-8-2-percent-july-report/"),
    ("Hilton Q2 2026 release (SEC), 28-Jul-2026", "2026-06", "us_hotel", "Hilton US Q2 2026: occupancy 77.3% (+1.6pp), ADR $180.16 (+3.2%), RevPAR $139.28 (+5.4%); FY26 system RevPAR guidance raised to +3.0-3.5%", "https://stories.hilton.com/releases/hilton-reports-2026-second-quarter-results"),
    ("Marriott Q2 2026 release (SEC), 3-Aug-2026", "2026-06", "us_hotel", "Marriott Q2 2026: worldwide ADR $228.23 (+3.7%), comparable constant-currency RevPAR +3.4%, US and Canada +5.0%, international -0.5%; FY26 RevPAR guidance raised to +3.0-3.5%", "https://www.sec.gov/Archives/edgar/data/1048286/000104828626000033/mar-2026q2xex99earningsrel.htm"),
    ("Key Data via Short Term Rentalz, 22-Jan-2026", "2026-01", "channel_mix", "US vacation-rental managers Q4 2025 distribution: Airbnb 54% of reservations and 45% of revenue; direct bookings 21% of reservations. Early 2026 paid-occupancy pacing -6%/-5%/-3% for Jan/Feb/Mar with ADR pacing +2% to +4%; booking windows and length of stay both shortening", "https://shorttermrentalz.com/news/key-data-report-us-booking-windows/"),
    ("PriceLabs via RentalScaleUp, 19-Dec-2025", "2025-12", "booking_window", "US booking windows shortened from about 19 to 15 days in January and 34 to 29 days in July between 2022 and 2025; bookings made 0-7 days out rose from 21% to 27% of all bookings. Large managers (100+ listings) run lower occupancy but higher ADR and RevPAR", "https://www.rentalscaleup.com/short-term-rental-planning-2026/"),
    ("Lighthouse via VisitBritain, June 2026", "2026-06", "party_size", "UK short-term rentals: share of bookings by property guest capacity moved from 1-2 guests 43% and 6+ guests 21% in June 2019 to 1-2 guests 29% and 6+ guests 30% in June 2026; 3-5 guests 35% to 41%. June 2026 ADR GBP 343 (+4%), occupancy 47% (flat), average stay 6.7 nights", "https://www.visitbritain.org/media/6087/download?attachment"),
    ("AirROI, 2026 study of 28 US markets", "2026", "fees", "Reports a 55.9% median markup between the advertised nightly rate and the checkout total across 28 US markets, and finds hotels cheaper in 27 of 28 single-room scenarios while Airbnb is competitive for families and groups in 19 of 28. Third-party methodology, not verified against the underlying data", "https://www.airroi.com/blog/airbnb-vs-hotel-all-in-pricing-2026"),
    ("Airbnb newsroom, 18-May-2021", "2021-05", "fees", "45% of active listings globally charged no cleaning fee; where charged, the average cleaning fee was under 10% of the total reservation cost", "https://news.airbnb.com/fee-transparency-on-airbnb/"),
    ("Airbnb newsroom, support for federal price-display legislation (stats through Sep 2024)", "2024-09", "fees", "More than 300,000 listings lowered or removed cleaning fees since the December 2022 toggle; about 40% of active listings charge no cleaning fee; more than 15 million guests had used the toggle", "https://news.airbnb.com/support-for-federal-price-display-legislation/"),
    ("Airbnb newsroom, 21-Apr-2025", "2025-04", "fees", "Total price display became the global default. About 17 million guests had used the optional toggle over the prior two years; over 80% of hosts used at least one pricing tool in the past year; 2 million hosts used the similar-listings comparison tool", "https://news.airbnb.com/total-price-display-is-now-standard-globally/"),
    ("Skift, 29-Aug-2026", "2026-08", "fees", "AirDNA told Skift that Airbnb's lower-fee 'bring your own cleaner' offer is a pilot, not a full rollout; the standard host fee remains 15.5%", "https://skift.com/2026/08/29/"),
    ("Skift, 28-Apr-2026 (AirDNA data)", "2026-01", "demand", "Inbound US short-term-rental demand fell 4.7% y/y in January 2026 against a 3.5% fall in overall inbound visitation, so STRs were hit harder than the wider inbound market", "https://skift.com/2026/04/28/us-tourism-slump-short-term-rentals/"),
    ("Rabbu analysis of ABNB Q2 2026, 6-Aug-2026", "2026-08", "mix", "Reads Q2 2026 as volume-led rather than price-led; over 150,000 homes newly listed across World Cup host cities; hotel nights on Airbnb grew roughly three times faster than home nights; Experiences supply +80% y/y", "https://rabbu.com/blog/airbnb-q2-2026-earnings-what-str-investors-need-to-know"),
    # --- consumer surveys -------------------------------------------------------------------
    ("Deloitte 2026 Summer Travel Survey ('Flight or Fold'), fielded 2-9 Apr 2026, n=4,003", "2026-04", "survey", "45% of Americans planning a paid-lodging summer vacation, a six-year low; 81% of those plan at least one hotel stay (80% in 2025) and 29% plan a private-rental stay, up slightly y/y; households on $100k+ are 55% of the travelling public, up from 50% in 2025; cost is the deterrent cited by roughly a third of non-travellers", "https://www.deloitte.com/us/en/insights/industry/transportation/2026-summer-travel-trends-survey.html"),
    ("Deloitte 2024 Summer Travel Survey, fielded 20-Mar to 2-Apr 2024, n=4,022", "2024-04", "survey", "48% planning a paid-lodging vacation, down from 50% in 2023; demand described as up for non-hotel lodging including private rentals, with no percentage given; high-income travellers 44% of the travelling public vs 35% in 2023", "https://www.deloitte.com/us/en/insights/industry/transportation/2024-summer-leisure-travel-trends.html"),
    ("Morning Consult brand tracking via Business Insider, Feb 2023, n=5,000 US adults", "2023-02", "survey", "Airbnb favourability 42% in February 2023 vs 38% in January 2022 and 23% in 2018; booking intent among short-term travellers 51% vs 50% a year earlier. No measurable dent from the autumn-2022 cleaning-fee and chore-list backlash", "https://www.businessinsider.com/airbnb-brand-morning-consult-market-research-cleaning-fees-chore-lists-2023-2"),
    ("YouGov US Hotel Rankings 2026 (consideration Jul 2025-Jun 2026, n>10,960)", "2026-06", "survey", "Airbnb and Vrbo are explicitly excluded from YouGov's hotel-brand rankings, which is itself a signal about how the category is framed for consumers. Marriott consideration 45.3%, Hilton 44.9%, Courtyard 37.8%", "https://yougov.com/en-us/articles/55288-us-hotel-rankings-report-2026"),
    ("Airbnb newsroom archive and IR, searched 6-Sep-2026", "2026-09", "business_travel", "No Airbnb-disclosed business-travel share of nights exists for 2023-2026. The only dated figures found were about 8% of bookings from corporate travel in 2014 and a 2018 note that nearly 60% of Airbnb for Work trips had more than one guest. Treat business mix as unquantified", "https://news.airbnb.com/"),
    ("Searched but not found", "n/a", "loyalty_gap", "No sourced statistic on the share of hotel bookings driven by loyalty points could be located. The nearest quantified anchor is the Third Bridge Booking.com expert: Genius level 2 and 3 members drive high-50s to low-60s percent of Booking's room nights", "n/a"),
    # --- academic ---------------------------------------------------------------------------
    ("Zervas, Proserpio and Byers (2017), Journal of Marketing Research, DOI 10.1509/jmr.15.0204", "2017", "academic_substitution", "A 10% rise in Airbnb listings is associated with roughly a 0.5% fall in quarterly Texas hotel revenue, concentrated in lower-priced, non-business-oriented hotels. Difference-in-differences on the staggered market-by-market rollout", "https://people.bu.edu/zg/publications/airbnb.pdf"),
    ("Farronato and Fradkin (2022), American Economic Review 112(6) 1782-1817", "2022", "academic_welfare", "Consumer surplus of about $41 per transaction; the welfare gain is concentrated where and when hotels are capacity-constrained, because peer supply expands elastically into demand spikes and moderates hotel price increases", "https://www.aeaweb.org/articles?id=10.1257/aer.20180260"),
    ("Guttentag and Smith (2017), International Journal of Hospitality Management vol. 57", "2017", "academic_substitution", "In a survey of over 800 Airbnb users, nearly two-thirds had used Airbnb as a substitute for a hotel. Airbnb is expected to outperform budget hotels and motels, underperform upscale hotels and be mixed against mid-range", "n/a (Google Scholar; full text paywalled)"),
    ("Li and Srinivasan (2019), Marketing Science, DOI 10.1287/mksc.2018.1143", "2019", "academic_substitution", "Airbnb mildly cannibalises hotel sales, with the effect concentrated in low-end hotels. Magnitude not retrievable; publisher blocked access", "https://pubsonline.informs.org/doi/abs/10.1287/mksc.2018.1143"),
    ("Gunter, Onder and Zekan (2020), Tourism Management (New York City)", "2020", "academic_elasticity", "Own-price demand for Airbnb in New York found price-inelastic; spatial Durbin model on 1,461 listings, Sep 2014 to Jun 2016. Coefficient not retrieved", "n/a (paywalled)"),
    ("Gunter and Onder (2018), Tourism Economics (Vienna)", "2018", "academic_elasticity", "Airbnb demand elasticity estimated between 0 and 1 in modulus, i.e. inelastic", "n/a (paywalled)"),
    ("Casamatta et al. (2022), Tourism Management (Barcelona and Madrid)", "2022", "academic_elasticity", "Airbnb demand found price-elastic in Barcelona and Madrid, the opposite sign of the New York and Vienna results. The literature does not agree on a single own-price elasticity", "n/a (paywalled)"),
    ("Barron, Kung and Proserpio (2021), Marketing Science 40(1)", "2021", "academic_supply", "Airbnb listing growth raises house prices and rents, more strongly where owner-occupancy is lower. Magnitude not retrievable; publisher blocked access", "https://www.marshall.usc.edu/personnel/davide-proserpio"),
    ("Superhost willingness-to-pay literature (Gibbs et al. 2018 JTR; Chen and Xie 2017 IJCHM; Lorde et al. 2019)", "2017-2019", "academic_wtp", "All find a positive Superhost price premium; none of the retrievable abstracts gives a magnitude. Our own hedonic on 3.0m listing-dumps puts the badge premium near zero once size, room type, rating and host scale are controlled", "n/a (paywalled)"),
]

# --------------------------------------------------------------------------------------------
# 4. Fee and total-price-display timeline.
# --------------------------------------------------------------------------------------------
FEE_TIMELINE = [
    ("2019-05", "Host-only ('simplified pricing') fee offered as a voluntary option to larger and professional hosts", "trade press (RentalScaleUp)", "medium"),
    ("2020-11", "Host-only fee made mandatory for software-connected hosts in Australia", "trade press (RentalScaleUp, STAAH)", "medium"),
    ("2020-12", "Host-only fee mandatory for software-connected hosts in most countries, excluding hosts whose listings are mostly in the US, Canada, Mexico, Bahamas, Argentina, Taiwan and Uruguay", "trade press (RentalScaleUp, STAAH); the original Airbnb newsroom post was not located", "medium"),
    ("2021-05", "Airbnb fee-transparency post: 45% of listings charge no cleaning fee, average fee under 10% of the reservation", "news.airbnb.com", "high"),
    ("2022-11", "Airbnb announces the optional total-price toggle for December 2022 and new checkout-task rules banning unreasonable chores", "news.airbnb.com", "high"),
    ("2022-12", "Total-price toggle live; search ranking begins weighting total price (per the 4Q22 shareholder letter)", "ABNB 4Q22 letter; news.airbnb.com", "high"),
    ("2023-05", "2023 Summer Release: host pricing and discount tools, similar-listings comparison, checkout-instruction preview, lower guest service fee after three months on long stays, Airbnb Rooms at $67 average", "ABNB 1Q23/2Q23 letters; news.airbnb.com", "high"),
    ("2023-09", "Airbnb reports more than 260,000 listings had cut or removed cleaning fees since the toggle", "Thrillist, headline verified only", "low"),
    ("2024-02", "About 300,000 listings had cut or removed cleaning fees; roughly 40% of active listings charge none", "TechCrunch 13-Feb-2024; news.airbnb.com", "high"),
    ("2024-07", "California SB 478 honest-pricing law takes effect, covering hotels and short-term rentals", "oag.ca.gov", "high"),
    ("2024-12", "FTC finalises the Rule on Unfair or Deceptive Fees covering short-term lodging", "ftc.gov", "high"),
    ("2025-04", "Total price display becomes the global default, not a toggle", "news.airbnb.com 21-Apr-2025", "high"),
    ("2025-05", "FTC junk-fees rule effective 12-May-2025", "ftc.gov", "high"),
    ("2025-10", "Airbnb begins migrating property-management-software hosts from the split fee to a single 15.5% host fee", "ABNB 4Q25 and 1Q26 letters", "high"),
    ("2026-03", "Over a quarter of active listings on the single fee (as at Q1 2026)", "ABNB 1Q26 letter", "high"),
    ("2026-05", "2026 Summer Release: services, boutique and independent hotels, and a price-match guarantee on the new hotel category (15% Airbnb credit)", "news.airbnb.com 20-May-2026", "medium-high"),
    ("2026-07", "Airbnb announces migration of most remaining hosts to the single 15.5% fee, to complete during 2026", "ABNB 2Q26 letter", "high"),
    ("2026-06", "About half of active listings on the single fee (as at Q2 2026)", "ABNB 2Q26 letter", "high"),
    ("2026-08", "'Bring your own cleaner' lower-fee offer confirmed by AirDNA as a pilot, not a rollout", "Skift 29-Aug-2026", "medium"),
]

# --------------------------------------------------------------------------------------------
# 5. Elasticities and sensitivities. `basis` says whether it is estimated here, published, or asserted.
# --------------------------------------------------------------------------------------------
ELASTICITY = [
    ("Entire home vs private room, all-in price", "+120% median / +30% hedonic-adjusted", "Inside Airbnb 2026 quote basis, 1.66m listing-dumps, 13 cities", "estimated here", "high",
     "data/processed/overnight/06_wtp_evidence.csv"),
    ("Guest capacity (accommodates), elasticity of nightly price", "+0.49% per 1% more capacity (2026 quote basis); +0.39% on the 2024-25 listed basis", "Inside Airbnb hedonic, city-dump fixed effects", "estimated here", "high",
     "data/processed/overnight/06_wtp_hedonic_coefs.csv"),
    ("Extra bedroom, holding capacity and everything else fixed", "+15.1% per bedroom (2026 quote basis); +19.5% (2024-25 listed basis)", "Inside Airbnb hedonic", "estimated here", "high",
     "data/processed/overnight/06_wtp_hedonic_coefs.csv"),
    ("Rating 4.9+ vs 4.7-4.8 (Guest Favorite proxy)", "+9.5% (2026 quote basis); +13.5% (2024-25)", "Inside Airbnb hedonic", "estimated here", "medium (rating is a proxy for the Guest Favorite badge, not the badge itself)",
     "data/processed/overnight/06_wtp_hedonic_coefs.csv"),
    ("Superhost badge", "+1.0% (2026 quote basis), +11.0% unadjusted median; -1.2% (2024-25 hedonic)", "Inside Airbnb hedonic and median cut", "estimated here", "low (the raw premium is composition, not the badge)",
     "data/processed/overnight/06_wtp_evidence.csv"),
    ("Instant Book", "+8.9% (2024-25 listed basis); not identified on the 2026 quote basis", "Inside Airbnb hedonic", "estimated here", "low",
     "data/processed/overnight/06_wtp_evidence.csv"),
    ("Professional host (>20 listings) vs single-listing host", "+8.1% (2026 quote basis); +9.5% (2024-25)", "Inside Airbnb hedonic", "estimated here", "medium",
     "data/processed/overnight/06_wtp_hedonic_coefs.csv"),
    ("Minimum stay 7+ nights vs 1-2 nights", "-37.8% median (2026 quote basis); -19.7% (2024-25)", "Inside Airbnb median cut", "estimated here", "medium (length-of-stay discounts plus a different property mix)",
     "data/processed/overnight/06_wtp_evidence.csv"),
    ("Airbnb take rate from full single-fee migration", "+40 to +50bps on a fully migrated book, arithmetic from published rates (split 14.1% guest + 3% host on a fee-inclusive GBV base gives about 15.0%; single fee gives 15.5%)", "Airbnb help-centre fee rates; letters", "arithmetic here", "medium (guest fee varies 14.1-16.5% and the taxes in GBV dilute both sides)",
     "note section 6"),
    ("Take rate from the mid-2024 FX service fee", "+20bps y/y in 2025", "Mertz, 4Q24 call", "published", "high", "4Q24 call"),
    ("Nights and GBV uplift from RNPL + cancellation redesign + single fee", "about +3pp nights and +4pp GBV in Q1 2026, so about +1pp of ADR", "Mertz, 1Q26 call", "published", "high (company-stated, no counterfactual)", "1Q26 call"),
    ("ABNB ADR y/y sensitivity to FX", "reported minus ex-FX ADR ran +5pp (1Q26), +1pp (2Q26), +3pp (4Q25), +2pp (3Q25)", "shareholder letters", "published", "high", "data/processed/overnight/06_price_gap_series.csv"),
    ("Airbnb price premium over hotels per room", "Airbnb 1-bedroom all-in $114-120 vs hotel ADR $140-153 in Sep-23, Dec-23 and Mar-24, i.e. Airbnb 19-25% cheaper per room", "ABNB 3Q23/4Q23 letters and Skift, sourced to CoStar", "published", "high (but on Airbnb's own chosen comparator)", "data/processed/overnight/06_price_gap_monthly.csv"),
    ("Airbnb price per person vs a hotel room", "Median all-in Airbnb entire-home price per guest capacity was about $59 a night across seven large US cities in Q2-Q3 2026, against a US hotel ADR of $171.74 in July 2026 for a room holding roughly 1.4-1.8 people", "Inside Airbnb; CoStar", "estimated here", "medium (capacity is not realised party size; the seven cities are high-ADR urban markets)",
     "data/processed/overnight/06_price_per_unit_panel.csv"),
    ("Discount penetration in Airbnb's own near-term quotes", "share of available quotes carrying a discount rose from 10.9% (Mar 2026) to 31.4% (Aug 2026), higher in all 13 cities; median discount about 15% of the nightly subtotal, 9.6% in August", "Inside Airbnb price_quote_raw", "estimated here", "medium (no year-ago comparison exists; seasonality is not controlled)",
     "data/processed/overnight/06_quote_discount_panel.csv"),
    ("Booking.com net take rate ceiling", "about 14.5% in 2025, 15-16% pre-pandemic; expert and sell-side both see the low teens as the range", "Third Bridge, 30-Jul-2026", "expert opinion", "medium", "06_expert_call_evidence.csv"),
    ("Airbnb commission charged to European managed rentals", "15-16%", "Third Bridge, 26-May-2026", "expert observed", "medium", "06_expert_call_evidence.csv"),
    ("Alt-accom vs hotel occupancy gap (India)", "hotels 60-65%, non-hotel alternative accommodation about 40%", "Third Bridge, 19-Aug-2026", "expert observed", "medium", "06_expert_call_evidence.csv"),
    ("AI-native booking share shift", "about 3% of accommodation bookings over the next 12-24 months", "Third Bridge, 14-Aug-2026", "expert opinion", "low", "06_expert_call_evidence.csv"),
    ("Hotel revenue displaced by Airbnb supply", "a 10% rise in Airbnb listings is associated with about a 0.5% fall in quarterly hotel revenue, concentrated in lower-priced non-business hotels", "Zervas, Proserpio and Byers (2017), JMR", "published, causal design", "high for Texas 2008-2014, dated for 2026", "06_choice_drivers.csv"),
    ("Consumer surplus per Airbnb transaction", "about $41, concentrated where hotels are capacity-constrained", "Farronato and Fradkin (2022), AER", "published, structural", "high for the sample period", "06_choice_drivers.csv"),
    ("Share of Airbnb guests who would otherwise have used a hotel", "nearly two-thirds of surveyed users had used Airbnb as a hotel substitute (n>800)", "Guttentag and Smith (2017), IJHM", "published, survey", "medium (2017 survey, self-report)", "06_choice_drivers.csv"),
    ("Own-price elasticity of Airbnb demand", "no consensus: inelastic (0 to 1 in modulus) in New York and Vienna, elastic in Barcelona and Madrid", "Gunter/Onder/Zekan 2020; Gunter and Onder 2018; Casamatta et al. 2022", "published", "low (city-specific, pre-2020 data, conflicting signs)", "06_choice_drivers.csv"),
    ("US private-rental trip intent", "29% of paid-lodging summer travellers plan a private-rental stay in 2026 against 81% planning at least one hotel stay; the two overlap", "Deloitte 2026 summer survey, n=4,003, fielded 2-9 Apr 2026", "published, survey", "medium-high", "06_choice_drivers.csv"),
    ("Sensitivity of Airbnb nights to a hotel-price move", "not estimable from what we hold. The predictive study already found hotel RevPAR tracks ABNB nights but adds no incremental forecast value", "research/notes/2026-09-06_predictive-study.md", "prior team work", "n/a", "predictive study"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    pd.DataFrame(COMPANY, columns=["source", "topic", "type", "statement", "numbers"]).to_csv(
        os.path.join(OUT, "06_company_evidence.csv"), index=False)
    pd.DataFrame(EXPERT, columns=["call", "call_date", "topic", "evidence_type", "point_paraphrased",
                                  "numbers"]).to_csv(
        os.path.join(OUT, "06_expert_call_evidence.csv"), index=False)
    pd.DataFrame(CHOICE, columns=["source", "period", "topic", "finding", "url"]).to_csv(
        os.path.join(OUT, "06_choice_drivers.csv"), index=False)
    pd.DataFrame(FEE_TIMELINE, columns=["month", "event", "source", "confidence"]).to_csv(
        os.path.join(OUT, "06_fee_timeline.csv"), index=False)
    pd.DataFrame(ELASTICITY, columns=["sensitivity", "estimate", "source", "basis", "confidence",
                                      "file_or_reference"]).to_csv(
        os.path.join(OUT, "06_elasticities.csv"), index=False)
    print("wrote", len(COMPANY), "company rows,", len(EXPERT), "expert rows,", len(CHOICE),
          "choice rows,", len(FEE_TIMELINE), "fee rows,", len(ELASTICITY), "elasticity rows")


if __name__ == "__main__":
    main()
