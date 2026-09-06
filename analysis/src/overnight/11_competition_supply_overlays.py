"""Workstream 11: competitive position, supply economics, AI and regulatory overlays as model inputs.

Reads
  data/processed/abnb_quarterly_kpis_from_study.csv          Airbnb nights, GBV, ADR, revenue by quarter (1Q21-2Q26)
  data/processed/inside_airbnb_like_for_like.csv             Inside Airbnb matched-listing pairs (retention, churn)
  data/processed/cc_listing_survival.csv                     Common Crawl re-fetch survival by crawl
  data/processed/abnb_regulatory_profile.csv                 regulatory Monte Carlo percentiles (2027, 2030)
  data/processed/abnb_regulatory_contributions.csv           per-event expected loss and probability
  data/processed/predictive/02_peer_prints.csv               BKNG / EXPE room-night growth by quarter
  Hand-entered disclosures (Booking Holdings 8-K/10-K/calls, Airbnb letters and calls, Skift Research,
  Phocuswright, AirDNA, Key Data, Third Bridge paraphrases) with a source column on every row.

Writes
  data/processed/overnight/11_alt_accom_share.csv            Airbnb vs Booking alt-accom nights, shares, market sizing
  data/processed/overnight/11_supply_economics.csv           dated supply disclosures, nights per listing, churn, US STR stats
  data/processed/overnight/11_competitor_events.csv          dated competitive and AI events
  data/processed/overnight/11_regulatory_overlay.csv         probability-weighted nights drag by year and region
  data/processed/overnight/11_new_business_scenarios.csv     bear/base/bull revenue by new business FY26-FY28
  data/processed/overnight/11_ai_exposure_scenarios.csv      AI-referral cost scenarios
  analysis/figures/overnight/11_alt_accom_growth.png

Run: py -3.13 analysis/src/overnight/11_competition_supply_overlays.py  (from the repo root)
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)  # noqa: E731
OUT = P("data", "processed", "overnight")
FIG = P("analysis", "figures", "overnight")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

L = "data/raw/letters/{q}_*.htm (shareholder letter)"
T = "data/raw/regulatory/transcripts/{q}.pdf (IR call transcript)"

# --------------------------------------------------------------------------------------
# 1. Alternative-accommodation share
# --------------------------------------------------------------------------------------
kpi = pd.read_csv(P("data", "processed", "abnb_quarterly_kpis_from_study.csv"))
kpi["year"] = 2000 + kpi["quarter"].str[-2:].astype(int)
kpi["q"] = kpi["quarter"].str[0].astype(int)
abnb_annual = kpi.groupby("year")["nights_m"].sum()
abnb_h1 = kpi[kpi["q"] <= 2].groupby("year")["nights_m"].sum()

# Booking Holdings: total room nights (annual, from 10-K / Q4 releases) and Booking.com alt-accom disclosures.
bkng_total = {  # millions; 2019, 2022, 2023 from BKNG 10-Ks; 2024 and 2025 from Q4 releases (+9%, +8%; "1.1bn", "over 1.2bn")
    2019: 845, 2022: 896, 2023: 1049, 2024: 1143, 2025: 1235,
}
bkng_total_src = {
    2019: "BKNG 10-K FY2019 (845m room nights)",
    2022: "BKNG 10-K FY2022 (896m)",
    2023: "BKNG 10-K FY2023 (1,049m)",
    2024: "BKNG Q4'24 release: room nights +9% y/y ('1.1 billion'); level derived from 2023 x 1.09",
    2025: "BKNG Q4'25 release: 'over 1.2 billion', +8% y/y (https://www.phocuswire.com/booking-holdings-q4-full-year-2025-earnings); level derived",
}
bkng_alt_mix = {  # share of Booking.com room nights that are alternative accommodation
    2022: (0.30, "BKNG calls: 32% in Q2'22, ~29% in Q4'22 (https://www.rentalscaleup.com/booking-com-32-of-room-nights-from-non-hotels-new-features-to-attract-short-term-rental-hosts/); FY approx 30%"),
    2023: (0.33, "BKNG Q3'23 call: 34% (https://www.phocuswire.com/booking-holdings-q2-2024 context); FY approx 33%"),
    2024: (0.35, "BKNG 10-K FY2025: 'approximately 36%' in 2025 'up versus approximately 35%' in 2024 (https://www.sec.gov/Archives/edgar/data/1075531/000107553126000009/bkng-20251231.htm)"),
    2025: (0.36, "BKNG 10-K FY2025, same sentence"),
}
bkng_alt_q = [  # quarter, mix, alt-accom room-night growth, listings (m), source
    ("2Q22", 0.32, None, None, "Booking.com Q2'22 (rentalscaleup 32% article)"),
    ("4Q22", 0.29, None, None, "BKNG Q4'22 call (via Stockopine summary, https://www.stockopine.com/p/booking-holdings-riding-the-travel-momentum)"),
    ("3Q23", 0.34, None, None, "BKNG Q3'23 call (via PhocusWire)"),
    ("2Q24", 0.36, None, None, "BKNG Q2'25 slides: 37% vs ~36% in Q2'24 (https://www.investing.com/news/company-news/booking-holdings-q2-2025-slides-revenue-jumps-16-adjusted-ebitda-up-28-93CH-4158985)"),
    ("3Q24", None, 0.14, None, "BKNG Q3'24 call: alt-accom room nights +14% (https://www.rentalscaleup.com/booking-coms-alternative-accommodations-keep-growing-and-so-does-its-grip-on-host-payments/)"),
    ("4Q24", 0.33, 0.19, 7.9, "BKNG Q4'24 call: +19%, 33% of room nights, 7.9m listings +8% (same rentalscaleup article, 28 Feb 2025)"),
    ("1Q25", 0.37, None, None, "BKNG Q1'25 slides (https://www.investing.com/news/company-news/booking-holdings-q1-2025-slides-alternative-accommodations-drive-8-revenue-growth-93CH-4012009)"),
    ("2Q25", 0.37, 0.10, 8.4, "BKNG Q2'25 slides/call: +10%, 37%, 8.4m listings (+8%)"),
    ("3Q25", 0.36, 0.10, 8.6, "BKNG Q3'25 call: ~+10%, 36%, 8.6m listings (+10%) (https://www.rentalscaleup.com/booking-com-alternative-accommodations-q3-2025/)"),
    ("1Q26", 0.38, 0.055, 8.8, "BKNG Q1'26 call: +5.5%, 38% vs 37%, 8.8m listings (+9%) (https://www.rentalscaleup.com/booking-com-q1-2026-results/)"),
    ("2Q26", 0.37, 0.04, 9.1, "BKNG Q2'26 8-K and call: +4%, ~37% flat, 9.1m listings (+8%) (https://www.sec.gov/Archives/edgar/data/0001075531/000107553126000036/q2-26bkngearningsrelease.htm; https://www.rentalscaleup.com/booking-com-q2-2026-earnings/)"),
]

rows = []
for y in [2019, 2022, 2023, 2024, 2025]:
    a = abnb_annual.get(y, np.nan)
    if y == 2019:
        a = 326.9  # Airbnb S-1 / 4Q20 letter
    b_tot = bkng_total[y]
    mix = bkng_alt_mix.get(y, (np.nan, ""))
    b_alt = b_tot * mix[0] if not np.isnan(mix[0]) else np.nan
    rows.append(dict(
        period=str(y), airbnb_nights_m=round(a, 1), airbnb_nights_yoy_pct=round(100 * (a / abnb_annual.get(y - 1) - 1), 1) if (y - 1) in abnb_annual.index else np.nan,
        bkng_total_room_nights_m=b_tot, bkng_alt_accom_mix=mix[0], bkng_alt_accom_nights_m=round(b_alt, 0) if not np.isnan(b_alt) else np.nan,
        airbnb_share_of_two_player_alt_nights=round(a / (a + b_alt), 3) if not np.isnan(b_alt) else np.nan,
        source=f"Airbnb nights: {L.format(q='4Q'+str(y)[2:])} via abnb_quarterly_kpis_from_study.csv; BKNG total: {bkng_total_src[y]}; mix: {mix[1]}",
    ))
# H1 2026 comparison using quarterly growth
a_h1_26, a_h1_25 = abnb_h1[2026], abnb_h1[2025]
rows.append(dict(
    period="1H26", airbnb_nights_m=round(a_h1_26, 1), airbnb_nights_yoy_pct=round(100 * (a_h1_26 / a_h1_25 - 1), 1),
    bkng_total_room_nights_m=np.nan, bkng_alt_accom_mix=0.375, bkng_alt_accom_nights_m=np.nan,
    airbnb_share_of_two_player_alt_nights=np.nan,
    source="Airbnb 1Q26+2Q26 nights vs 1Q25+2Q25; Booking.com alt-accom room nights +5.5% (Q1) and +4% (Q2) per calls; mix 38%/37%",
))
alt = pd.DataFrame(rows)
altq = pd.DataFrame(bkng_alt_q, columns=["quarter", "bkng_alt_accom_mix", "bkng_alt_accom_nights_yoy", "bkng_alt_accom_listings_m", "source"])
# Airbnb quarterly nights growth alongside
kpi["nights_yoy"] = kpi["nights_m"] / kpi["nights_m"].shift(4) - 1
altq = altq.merge(kpi[["quarter", "nights_yoy"]].rename(columns={"nights_yoy": "airbnb_nights_yoy"}), on="quarter", how="left")
peer = pd.read_csv(P("data", "processed", "predictive", "02_peer_prints.csv"))
# 02_peer_prints uses "2024Q3"; this file uses Airbnb-letter style "3Q24".
peer["quarter"] = peer["quarter"].str[-1] + "Q" + peer["quarter"].str[2:4]
altq = altq.merge(peer[["quarter", "bkng_room_nights_yoy", "expe_room_nights_yoy"]], on="quarter", how="left")
altq["bkng_room_nights_yoy"] = altq["bkng_room_nights_yoy"] / 100
altq["expe_room_nights_yoy"] = altq["expe_room_nights_yoy"] / 100

market = pd.DataFrame([
    dict(period="2019", source_name="Skift Research", metric="Airbnb share of global STR revenue", value=0.28, unit="share", source="https://skift.com/2025/03/14/short-term-rentals-airbnbs-dominance-and-bookings-gains-in-1-chart/"),
    dict(period="2019", source_name="Skift Research", metric="Booking.com share of global STR revenue", value=0.14, unit="share", source="same"),
    dict(period="2019", source_name="Skift Research", metric="Vrbo share of global STR revenue", value=0.11, unit="share", source="same"),
    dict(period="2024", source_name="Skift Research", metric="Airbnb share of global STR revenue", value=0.44, unit="share", source="same"),
    dict(period="2024", source_name="Skift Research", metric="Booking.com share of global STR revenue", value=0.18, unit="share", source="same"),
    dict(period="2024", source_name="Skift Research", metric="Vrbo share of global STR revenue", value=0.09, unit="share", source="same"),
    dict(period="2024", source_name="Skift Research", metric="Big-3 OTA share of global STR revenue", value=0.71, unit="share", source="same"),
    dict(period="2024", source_name="Skift Research", metric="Global STR revenue", value=183, unit="USD bn", source="same"),
    dict(period="2025", source_name="Phocuswright (Aug 2026)", metric="Global STR gross bookings", value=219.9, unit="USD bn", source="https://www.phocuswright.com/Travel-Research/Research-Updates/2026/shortterm-rentals-enter-a-new-phase-of-scrutiny-and-structural-growth"),
    dict(period="2029", source_name="Phocuswright (Aug 2026)", metric="Global STR gross bookings forecast (5.3% CAGR 2025-29)", value=270.6, unit="USD bn", source="same"),
    dict(period="2025", source_name="Phocuswright (Aug 2026)", metric="North America STR gross bookings (+4% y/y)", value=78.0, unit="USD bn", source="same, via search summary; 2026 forecast $81.8bn (+5%)"),
    dict(period="2025", source_name="Airbnb", metric="Airbnb GBV (all categories incl. hotels, experiences, services)", value=91.3, unit="USD bn", source="4Q25 letter; abnb_vs_bkng_annual.csv"),
    dict(period="2025", source_name="Eurostat", metric="EU-27 platform STR nights (Airbnb, Booking, Expedia, Tripadvisor)", value=951.6, unit="m nights (+11.4% y/y)", source="data/processed/eurostat_platform_nights_quarterly.csv; https://logos-pres.md/en/news/new-rental-record-airbnb-effect-could-not-be-stopped/"),
    dict(period="1Q26", source_name="Eurostat", metric="EU-27 platform STR nights y/y", value=0.097, unit="growth", source="data/processed/eurostat_platform_nights_quarterly.csv (144.3m nights)"),
    dict(period="2026", source_name="AirDNA (Jul 2026 midyear)", metric="US STR demand growth forecast", value=0.027, unit="growth", source="https://www.prnewswire.com/news-releases/steady-demand-and-slower-new-supply-define-us-short-term-rentals-in-2026-airdna-finds-302820776.html"),
    dict(period="2026", source_name="Vrbo", metric="Vrbo bookable listings", value=2.0, unit="m (company claim 'over 2 million')", source="https://www.businessofapps.com/data/vrbo-statistics/"),
    dict(period="2025", source_name="Marriott", metric="Homes & Villas by Marriott Bonvoy homes", value=0.18, unit="m (180,000+, Aug 2025)", source="https://www.businesswire.com/news/home/20250814071977/en"),
])

# Share-cap arithmetic: what Airbnb's GBV path implies for its share of the global STR pool.
# Market: Phocuswright Aug 2026, $219.9bn 2025 gross bookings growing 5.3% CAGR to $270.6bn in 2029.
# Airbnb GBV: FY25 $91.3bn (4Q25 letter), grown at nights growth (model/assumptions.md) x ADR growth
# implied by the driver-model revenue scenarios at the scenario take rate.
mkt25, mkt_cagr = 219.9, 0.053
abnb_gbv25 = 91.3
gbv_paths = {  # scenario: (nights growth, ADR growth) FY26, FY27, FY28, FY29 (FY29 = FY28 repeated)
    "bear": ([0.095, 0.06, 0.05, 0.04], [0.05, -0.01, -0.01, -0.01]),
    "base": ([0.10, 0.09, 0.08, 0.07], [0.055, 0.03, 0.03, 0.03]),
    "bull": ([0.105, 0.10, 0.09, 0.08], [0.06, 0.04, 0.04, 0.04]),
}
cap_rows = []
for case, (ng, ag) in gbv_paths.items():
    g = abnb_gbv25
    for i, y in enumerate([2026, 2027, 2028, 2029]):
        g *= (1 + ng[i]) * (1 + ag[i])
        m = mkt25 * (1 + mkt_cagr) ** (y - 2025)
        cap_rows.append(dict(period=str(y), source_name=f"derived ({case})", metric="Airbnb implied share of global STR gross bookings",
                             value=round(g / m, 3), unit="share",
                             source=f"Airbnb GBV ${g:.0f}bn (FY25 $91.3bn x nights {ng[i]:+.1%} x ADR {ag[i]:+.1%} path, model/assumptions.md) / Phocuswright market ${m:.0f}bn (5.3% CAGR from $219.9bn 2025). 2025 actual share {abnb_gbv25/mkt25:.3f}"))
cap = pd.DataFrame(cap_rows)
market = pd.concat([market, cap], ignore_index=True)

alt.to_csv(os.path.join(OUT, "11_alt_accom_share.csv"), index=False)
altq.to_csv(os.path.join(OUT, "11_alt_accom_share_quarterly.csv"), index=False)
market.to_csv(os.path.join(OUT, "11_alt_accom_market_sizing.csv"), index=False)

# --------------------------------------------------------------------------------------
# 2. Supply economics
# --------------------------------------------------------------------------------------
supply_disc = [
    # date, metric, value, unit, note, source
    ("2020-12-31", "active_listings", 5.6, "m", "Reported in S-1/10-K: '5.6 million active listings' end 2020", "ABNB 10-K FY2020"),
    ("2021-12-31", "active_listings", 6.0, "m", "'6 million active listings at the end of 2021'", L.format(q="4Q21")),
    ("2022-12-31", "active_listings", 6.6, "m", "'increase of over 900,000 active listings, or 16% compared to 2021, excluding ... China' -> ~6.6m ex-China", L.format(q="4Q22")),
    ("2023-06-30", "active_listings", 7.0, "m", "'exceed 7 million total active listings'; record net adds", L.format(q="2Q23")),
    ("2023-12-31", "active_listings", 7.7, "m", "'Active listings exceeded 7.7 million', +18% y/y", L.format(q="4Q23")),
    ("2024-06-30", "active_listings", 8.0, "m", "'surpassed 8 million active listings'", T.format(q="2024-Q2")),
    ("2024-12-31", "active_listings", 8.0, "m", "'over 8 million active listings' (no growth rate disclosed; Q1'24 +17% ex-removals was the last rate)", L.format(q="4Q24")),
    ("2025-12-31", "active_listings", 9.0, "m", "'over 9 million active listings'; Q4'25 'grew relatively in-line with' nights (+10%)", L.format(q="4Q25")),
    ("2026-03-31", "active_listings_growth", "in line with nights (+9%)", "text", "'active listings grew relatively in-line with the year-over-year increase of Nights and Seats Booked'", L.format(q="1Q26")),
    ("2023-03-31", "active_listings_yoy", 0.18, "growth", "ex-China; Q4'22 was +16%", L.format(q="1Q23")),
    ("2023-06-30", "active_listings_yoy", 0.19, "growth", "", L.format(q="2Q23")),
    ("2023-09-30", "active_listings_yoy", 0.19, "growth", "'nearly 1 million active listings this year'", L.format(q="3Q23")),
    ("2023-12-31", "active_listings_yoy", 0.18, "growth", "", L.format(q="4Q23")),
    ("2024-03-31", "active_listings_yoy", 0.15, "growth", "17% excluding the removal of low-quality listings", L.format(q="1Q24") + "; " + T.format(q="2024-Q1")),
    ("2025-09-30", "active_listings_yoy", "approx. in line with nights (+9%)", "text", "", L.format(q="3Q25")),
    ("2025-06-30", "listings_removed_since_2023", 0.5, "m", "'removed over 500,000 listings' since the 2023 hosting quality system", L.format(q="2Q25")),
    ("2021-03-31", "hosts", 4.0, "m", "'4 million Hosts'", L.format(q="1Q21")),
    ("2023-12-31", "hosts", 5.0, "m", "'Host community surpassed 5 million Hosts'", L.format(q="4Q23")),
    ("2026-05-20", "hosts", 5.5, "m", "'over 5.5 million hosts'", "https://news.airbnb.com/airbnb-2026-summer-release"),
    ("2023-12-31", "host_earnings_annual", 57, "USD bn", "'in 2023 alone, Hosts earned more than $57 billion' (GBV 73.3bn -> 78% of GBV)", L.format(q="4Q23") + "; " + T.format(q="2023-Q4")),
    ("2023-09-30", "host_earnings_quarter", 19, "USD bn", "Q3'23", T.format(q="2023-Q3")),
    ("2025-12-31", "host_earnings_annual_est", 71, "USD bn", "Not disclosed for 2024-25; 78% of GBV ($91.3bn) = ~$71bn (estimate)", "derived"),
    ("2026-05-20", "cumulative_host_earnings", 380, "USD bn", "'hosts have earned over $380 billion' (third-party stats pages citing Airbnb)", "https://www.ipropertymanagement.com/research/airbnb-statistics (secondary)"),
    ("2023-03-31", "individual_hosts_share", 0.90, "share", "'Approximately 90% of our Hosts are individual Hosts', majority of listings and nights", L.format(q="1Q23")),
    ("2024-10-16", "co_host_network", 10000, "co-hosts", "Launched with 10,000 co-hosts in 10 countries; 20,000 applicants in 3 weeks", L.format(q="3Q24") + "; " + T.format(q="2024-Q3")),
    ("2025-02-13", "co_host_network_listings", 100000, "listings", "'almost 100,000 listings' in four months; 15,000 co-hosts; co-hosted new listings earn ~2x comparable", L.format(q="4Q24") + "; " + T.format(q="2024-Q4")),
    ("2025-08-06", "co_host_network_listings", 100000, "listings", "'over 100,000 listings, which have had over 10 million nights booked'; no incremental take rate on co-host listings (Q1'25 call)", L.format(q="2Q25") + "; " + T.format(q="2025-Q1")),
    ("2025-03-31", "superhost_nights_yoy", 0.15, "growth", "nights at Superhost listings +15% (Q1'25), +12% (Q2'25)", L.format(q="1Q25")),
    ("2024-06-30", "superhost_listings_yoy", 0.26, "growth", "active listings managed by Superhosts +26%", T.format(q="2024-Q2")),
    ("2025-11-06", "guest_favorite_nights_cum", 500, "m", "nearly 500m nights at Guest Favorite listings since Nov 2023 (2m listings)", L.format(q="3Q25")),
    ("2026-05-07", "event_supply", 100000, "listings", "16 World Cup host cities: +100,000 incremental listings; Paris 2024: >50% of Games listings retained 6 months on", T.format(q="2026-Q1")),
    ("2026-08-06", "event_supply", 150000, "listings", "'over 150,000 listings by first time hosts' for the World Cup", L.format(q="2Q26")),
    ("2026-08-06", "single_fee_share_of_listings", 0.50, "share", "'Approximately half of our active listings are now subject to the single service fee'; whole base by year-end 2026", T.format(q="2026-Q2")),
    ("2023-11-01", "occupancy_statement", "stable globally", "text", "'occupancy ... pretty stable ... on a global basis'; lowest-price listings have highest occupancy (US)", T.format(q="2023-Q3")),
    ("2024-05-08", "occupancy_statement", "far below hotels", "text", "'global occupancy on Airbnb is so much lower than hotels'; 'not even close to high occupancy'", T.format(q="2024-Q1")),
    ("2025-08-06", "supply_strategy", "supply-constrained top markets", "text", "'focusing on our most supply-constrained markets'; hotels as gap-fill", T.format(q="2025-Q2")),
    ("2026-05-07", "supply_strategy", "targeted, not volume", "text", "'concentrating our acquisition efforts on the markets and geographies where underlying demand exists ... encouraging existing hosts to open up more of their calendar'", L.format(q="1Q26")),
    ("2026-08-06", "supply_strategy", "both constrained and unconstrained markets", "text", "'seeing strength in both supply-constrained markets and in non-supply-constrained markets'", T.format(q="2026-Q2")),
    # US STR industry stats
    ("2025-12-16", "airdna_us_available_listings_2025", 1.69, "m", "2025 available listings (AirDNA via stayfi); 2026 forecast 1.77m", "https://stayfi.com/vrm-insider/2026/04/20/vacation-rental-statistics/; https://www.prnewswire.com/news-releases/2026-will-be-the-best-year-to-invest-in-short-term-rentals-since-2021-new-airdna-report-finds-302643393.html"),
    ("2025-12-16", "airdna_us_2026_outlook_dec", "listings +4.6%, ADR +1.5%, occupancy -1%", "text", "December 2025 outlook: STR premium highest since 2022", "same PRNewswire release"),
    ("2026-07-08", "airdna_us_2026_outlook_jul", "demand +2.7%, listings +2.7%, occupancy 57.4%, RevPAR +2.9%, ADR ~+3%", "text", "Midyear update: new-listing growth cut to 2.7% (mortgage rates >6%); international inbound STR demand -12% vs spring 2025; Canada -32%", "https://www.prnewswire.com/news-releases/steady-demand-and-slower-new-supply-define-us-short-term-rentals-in-2026-airdna-finds-302820776.html"),
    ("2024-12-31", "airdna_us_new_listing_growth", "2022 +22.1%, 2023 +14.4%, 2024 +6.8%", "text", "US new-listing growth decelerating three years running", "https://skift.com/2025/01/30/where-to-invest-in-short-term-rentals-in-2025-airdnas-top-u-s-markets/"),
    ("2025-04-20", "us_host_occupancy", "57% (2024) -> 50% (spring 2025)", "text", "Cited in bear pitch (LongYield) from AirDNA; US listings 1.76m", "research/notes/2026-09-04_abnb-pitch-catalogue.md (LongYield)"),
    ("2026-06-04", "keydata_july4_2026", "occupancy +6.5%, ADR +5.5%, RevPAR +12.4% y/y", "text", "Professionally managed US STRs, 25 markets, 22 positive; booking window 134 days", "https://www.keydata.co/blog/july-4th-2026-short-term-rental-performance-report-occupancy-adr-and-revpar-trends"),
    ("2026-07-31", "keydata_q2_2026", "RevPAR +2.1% to $119.27; occupancy -1.5% to 48.4%", "text", "'rate, not demand, is driving growth' (VRM Intel headline; page 403 on fetch)", "https://vrmintel.com/as-short-term-rental-market-stabilizes-rate-not-demand-is-driving-growth/key-data-dashboard-us-q2-2026-revpar-growth/"),
    # Third Bridge paraphrases
    ("2026-06-02", "tb_us_vrm_supply", "~2m professionally managed US rentals, ~20,000 firms, PE roll-ups ~10% share", "text", "Paraphrase; managers allocate inventory across Airbnb, Vrbo, Booking; owner retention 80-85%/yr", "data/raw/licensed/third-bridge/ (T5, 2 Jun 2026)"),
    ("2026-05-26", "tb_europe_supply", "~18m second homes, ~3m let, ~1m urban; manager portfolios flat; owner churn ~15%/yr", "text", "Paraphrase; non-exclusive listings double-counted across platforms", "data/raw/licensed/third-bridge/ (T4, 26 May 2026)"),
]
sup = pd.DataFrame(supply_disc, columns=["date", "metric", "value", "unit", "note", "source"])

# nights per listing (annual)
npl = []
listings_year_end = {2020: 5.6, 2021: 6.0, 2022: 6.6, 2023: 7.7, 2024: 8.0, 2025: 9.0}
for y in [2021, 2022, 2023, 2024, 2025]:
    avg_l = (listings_year_end[y] + listings_year_end[y - 1]) / 2
    n = abnb_annual[y]
    npl.append(dict(date=f"{y}-12-31", metric="nights_per_avg_active_listing", value=round(n / avg_l, 1), unit="nights/listing/yr",
                    note=f"nights {n:.1f}m / average listings {avg_l:.2f}m; listings growth {100*(listings_year_end[y]/listings_year_end[y-1]-1):.0f}% vs nights growth {100*(n/abnb_annual.get(y-1, np.nan)-1):.0f}%" if (y-1) in abnb_annual.index else f"nights {n:.1f}m / avg listings {avg_l:.2f}m",
                    source="derived from letters (listing levels rounded as disclosed; 'over X million' treated as X)"))
sup = pd.concat([sup, pd.DataFrame(npl)], ignore_index=True)

# Inside Airbnb retention: year-ago pairs, by city and end year.
# Exclude any pair where either dump is partial-scope (Inside Airbnb changed the geographic scope of
# several 2026 monthlies; a partial dump looks like mass churn). Flag from inside_airbnb_city_snapshots.csv.
lfl = pd.read_csv(P("data", "processed", "inside_airbnb_like_for_like.csv"))
snaps = pd.read_csv(P("data", "processed", "inside_airbnb_city_snapshots.csv"))
scope = snaps.set_index(["city", "dump_date"])["partial_scope"].astype(bool).to_dict()
ya = lfl[lfl["pair_type"] == "year_ago"].copy()
ya["partial_a"] = [bool(scope.get((c, d), False)) for c, d in zip(ya["city"], ya["date_a"])]
ya["partial_b"] = [bool(scope.get((c, d), False)) for c, d in zip(ya["city"], ya["date_b"])]
n_pairs_all = len(ya)
ya_partial = ya[ya["partial_a"] | ya["partial_b"]]
ya = ya[~(ya["partial_a"] | ya["partial_b"])].copy()
print(f"Inside Airbnb year-ago pairs: {n_pairs_all} total, {len(ya_partial)} dropped as partial-scope, {len(ya)} kept")
if len(ya_partial):
    print("  dropped mean retention %.3f vs kept %.3f" % (ya_partial["retention"].mean(), ya["retention"].mean()))
ya["end_year"] = ya["date_b"].str[:4].astype(int)
ret = ya.groupby(["city", "end_year"]).agg(retention=("retention", "mean"), new_share=("new_share_b", "mean"), exits_reviewed=("exit_reviewed_ltm_share", "mean"),
                                           matched_reviews_chg=("matched_reviews_ltm_chg", "mean"), n=("retention", "size")).reset_index()
ret_wide = ret.pivot(index="city", columns="end_year", values="retention")
for _, r in ret.iterrows():
    sup.loc[len(sup)] = [f"{r.end_year}-12-31", f"inside_airbnb_year_ago_retention_{r.city}", round(r.retention, 3), "share",
                         f"new-listing share {r.new_share:.2f}; exits with review LTM {r.exits_reviewed:.2f}; matched-listing reviews LTM chg {r.matched_reviews_chg:+.2f}; n pairs {int(r.n)}",
                         "data/processed/inside_airbnb_like_for_like.csv (pair_type=year_ago, mean over pairs ending in year, partial-scope dumps excluded via inside_airbnb_city_snapshots.csv)"]
# CC survival by year (informative crawls)
cc = pd.read_csv(P("data", "processed", "cc_listing_survival.csv"))
cci = cc[cc["status_informative"]]
ccy = cci.groupby("year")[["refetched", "live", "removed"]].sum().reset_index()
ccy["survival"] = ccy["live"] / ccy["refetched"]
for _, r in ccy.iterrows():
    sup.loc[len(sup)] = [f"{int(r.year)}-12-31", "cc_listing_survival", round(r.survival, 3), "share", f"re-fetched {int(r.refetched)}, removed {int(r.removed)} (informative crawls only)", "data/processed/cc_listing_survival.csv"]
sup.to_csv(os.path.join(OUT, "11_supply_economics.csv"), index=False)

# --------------------------------------------------------------------------------------
# 3. Competitor and AI events
# --------------------------------------------------------------------------------------
events = [
    ("2019-03-07", "Airbnb", "hotels", "Airbnb acquires HotelTonight (referenced on 2023-2025 calls as the hotel foothold)", T.format(q="2023-Q3")),
    ("2023-05-09", "Airbnb", "AI", "Chesky: Airbnb was 'supposed to be one of the launch partners for the plugins on OpenAI for ChatGPT'; declined to prioritise; 90% of traffic direct or unpaid", T.format(q="2023-Q1")),
    ("2023-06-28", "Booking.com", "AI", "Booking.com launches AI Trip Planner (ChatGPT-based) in the app", "https://news.booking.com/bookingcom-launches-new-ai-trip-planner-to-enhance-travel-planning-experience/"),
    ("2023-11-01", "Google", "distribution", "Google Vacation Rentals update lets property managers show prices; Airbnb: 'not going to respond directly'; Airbnb chose not to integrate Google Hotel Finder (Q3'25 call)", T.format(q="2023-Q3") + "; " + T.format(q="2025-Q3")),
    ("2024-08-06", "Airbnb", "share", "Airbnb says it gains share of 'total nights stayed over the universe of hotel and other travel accommodations' every quarter; alternative accommodation called 'a catch-all' (Q3'24)", T.format(q="2024-Q2") + "; " + T.format(q="2024-Q3")),
    ("2024-10-16", "Airbnb", "supply", "Co-Host Network launched: 10,000 co-hosts, 10 countries", L.format(q="3Q24")),
    ("2025-01-23", "OpenAI", "AI", "Operator agent debuts with Booking.com, Priceline, Tripadvisor, Uber as early contributors; deprecated into ChatGPT agent, shut 31 Aug 2025", "https://www.phocuswire.com/openai-operator-web-agent; https://en.wikipedia.org/wiki/OpenAI_Operator"),
    ("2025-02-13", "Airbnb", "new business", "FY25 plan: $200-250m to launch and scale new businesses; 'easily $1 billion revenue opportunity'; Vrbo's Q4'24 strength attributed to soft comp", T.format(q="2024-Q4")),
    ("2025-03-27", "Perplexity", "AI", "Perplexity adds in-app hotel booking via Selfbook and Tripadvisor (140,000 hotels)", "https://skift.com/2025/03/27/perplexity-now-handles-hotel-bookings-what-our-tests-show/"),
    ("2025-05-13", "Airbnb", "new business", "Summer Release: Airbnb Services (10 categories, 260 cities, 8 countries, 15% host fee) and reimagined Experiences (20% fee); 60,000 host applications by Aug", L.format(q="2Q25") + "; https://techcrunch.com/2025/05/13/airbnb-lauches-services-and-experinces-as-it-thinks-about-connecting-travelers"),
    ("2025-05-22", "Expedia/Vrbo", "loyalty", "One Key earn on Vrbo cut: Blue members earn nothing on Vrbo, Silver 1%, Gold/Platinum 2%", "https://shorttermrentalz.com/news/vrbo-to-revise-one-key-earn-rates-from-may/"),
    ("2025-07-29", "Booking.com", "share", "Q2'25: alt-accom room nights +10% (vs Airbnb nights +7%), 37% of room nights, 8.4m listings", "https://www.investing.com/news/company-news/booking-holdings-q2-2025-slides-revenue-jumps-16-adjusted-ebitda-up-28-93CH-4158985"),
    ("2025-08-06", "Airbnb", "AI", "Chesky: 'open to' integrating with AI agents; chatbots are 'not the new Google, yet'; AI support agent cut human contacts 15%", T.format(q="2025-Q2")),
    ("2025-08-15", "Airbnb", "payments", "Reserve Now, Pay Later launched in the US ($0 upfront); ~70% adoption among eligible; ~20% of global GBV by Q1'26; +3 pts nights growth Q1'26", L.format(q="3Q25") + "; " + L.format(q="1Q26")),
    ("2025-09-15", "Airbnb", "take rate", "Single service fee (15.5% host-only) rolled to API-connected hosts (property managers); ~25% of listings by Q1'26, ~50% by Q2'26, all by end-2026", T.format(q="2026-Q1") + "; " + T.format(q="2026-Q2")),
    ("2025-10-06", "OpenAI", "AI", "Apps in ChatGPT launched with Expedia and Booking.com among first partners; Airbnb absent", "https://www.phocuswire.com/openai-chatgpt-apps-expedia-booking-tripadvisor"),
    ("2025-10-21", "Airbnb", "AI", "Chesky: ChatGPT apps 'not quite robust enough' for Airbnb; will monitor; Airbnb uses Alibaba Qwen among models", "https://www.cnbc.com/2025/10/22/airbnb-chatgpt-ai-chesky.html"),
    ("2025-11-06", "Airbnb", "AI", "Chesky: ChatGPT traffic converts higher than Google traffic when sent to Airbnb; 'close to the people at OpenAI'; hotels custom product built; chose not to join Google Hotel Finder", T.format(q="2025-Q3")),
    ("2025-12-01", "Hilton", "entry", "Apartment Collection by Hilton announced: furnished apartments bookable on Hilton channels H1 2026 (NYC, DC, Atlanta)", "https://stories.hilton.com/releases/hilton-introduces-apartment-collection-by-hilton"),
    ("2026-02-12", "Airbnb", "hotels", "Q4'25: direct partnerships with boutique hotels in NYC, LA, Madrid, SF; >100 NYC hotels / 20,000 rooms; hotels single-digit % of nights growing ~2x platform; AI companies 'top-of-funnel traffic generators ... just like Google was'; chatbot traffic converts above Google", L.format(q="4Q25") + "; " + T.format(q="2025-Q4")),
    ("2026-02-18", "Booking.com", "connected trip", "FY25: connected-trip verticals flights +37%, attractions +80%; travellers booking multiple components +20%", "https://www.sec.gov/Archives/edgar/data/1075531/000107553126000009/bkng-20251231.htm; https://www.phocuswire.com/booking-holdings-q4-full-year-2025-earnings"),
    ("2026-04-28", "Booking.com", "share", "Q1'26: alt-accom room nights +5.5% (in line with total, Middle East hit), 38% mix, 8.8m listings (+9%)", "https://www.rentalscaleup.com/booking-com-q1-2026-results/"),
    ("2026-05-07", "Airbnb", "hotels", "Q1'26: hotels growing >2x platform; ~55% of hotel bookers return to book a home; hotels 'could be a multibillion-dollar revenue business'", T.format(q="2026-Q1") + "; " + L.format(q="1Q26")),
    ("2026-05-20", "Airbnb", "new business", "2026 Summer Release: grocery (Instacart, 25+ US cities), airport pickups (160+ cities), luggage storage (15,000 locations, 175 cities), car rentals; 3,000+ landmark and 2,500+ food experiences; hotels in 20 destinations; 5.5m hosts", "https://news.airbnb.com/airbnb-2026-summer-release"),
    ("2026-05-26", "Airbnb", "hotels", "Andrea D'Amico (ex-Booking.com hotels EMEA) VP Hotels; Airbnb leads $58m WeRoad round for ~10%", "research/notes/2026-09-04_management-timeline.md"),
    ("2026-06-04", "Airbnb", "AI", "Chesky to found an independent AI lab while remaining CEO", "https://techcrunch.com/2026/06/04/airbnbs-brian-chesky-plans-to-launch-a-new-ai-lab/"),
    ("2026-07-30", "Booking.com (expert)", "AI/loyalty", "Third Bridge T1 (paraphrase): Genius L2/L3 drive high-50s to low-60s % of room nights; US direct high-50s to mid-60s; connected trip low double digits of transactions, ~50% is '10 years best case'; Europe STR supply lead over Airbnb; 'not concerned about losing share'", "data/raw/licensed/third-bridge/ (T1)"),
    ("2026-08-04", "Booking.com", "share", "Q2'26: alt-accom room nights +4% vs total +5%; 37% mix flat; 9.1m listings (+8%); AI tools <1% of room nights; B2C direct mid-60s%; connected-trip transactions +low double digits; Q3 room nights guide +3-5%; Fogel wants US alt-accom share 'a lot higher'", "https://www.sec.gov/Archives/edgar/data/0001075531/000107553126000036/q2-26bkngearningsrelease.htm; https://www.rentalscaleup.com/booking-com-q2-2026-earnings/; https://www.phocuswire.com/news/finance/booking-holdings-q2-2026-earnings"),
    ("2026-08-04", "Airbnb", "hotels", "Lark Hotels partnership (75+ boutique hotels)", "research/notes/2026-09-04_management-timeline.md"),
    ("2026-08-05", "Expedia/Vrbo", "share", "Q2'26: room nights +6% (US mid-single, EMEA low-single, RoW low-double); B2C bookings +8%, fastest US growth in 15 quarters; Vrbo supplier-funded promotions >40% of bookings, May sale >$1bn; 'answer engine optimisation' fastest-growing channel; testing ChatGPT and Claude channels; Vrbo agentic voice for partner inquiries", "https://www.sec.gov/Archives/edgar/data/1324424/000132442426000051/earningsrelease-q22026.htm; https://www.rentalscaleup.com/vrbo-q2-2026-earnings/; https://www.gurufocus.com/news/9009782/"),
    ("2026-08-06", "Airbnb", "hotels/AI", "Q2'26: hotel nights ~3x homes growth, thousands of hotels in 20+ destinations, 15% credit to 31 Dec 2026, price-match; 35% of first-time hotel guests book a home within a year; app 64% of nights; AI assistant resolves ~45% of issues; support cost/booking -16%", L.format(q="2Q26") + "; " + T.format(q="2026-Q2")),
    ("2026-08-07", "Google", "AI", "Google confirms agentic hotel booking test in Search AI Mode (US)", "https://skift.com/2026/08/07/google-confirms-hotel-agentic-booking-is-now-in-testing/"),
    ("2026-08-10", "Airbnb", "AI", "Chesky interview: AI-native search within a year; rental cars/hotels 1-2 years from super-app scope", "research/notes/2026-09-04_management-timeline.md"),
    ("2026-08-14", "OTA AI (expert)", "AI", "Third Bridge T2 (paraphrase): ~3% of accommodation bookings could move to AI-native transactions in 12-24 months, no EBITDA impact; Airbnb's direct traffic is the exposure if users start at ChatGPT/Perplexity; long-tail inventory benefits after 24 months", "data/raw/licensed/third-bridge/ (T2)"),
    ("2026-08-27", "Google", "AI", "Agentic hotel booking rolls into AI Mode; launch partners Booking.com, Expedia, Hotels.com, Priceline, Trip.com, Marriott, Hilton, IHG, Wyndham, Choice; hotel/OTA stays merchant of record; Airbnb not a partner", "https://skift.com/2026/08/27/googles-agentic-hotel-booking-tool-comes-to-ai-mode/"),
    ("2026-08-29", "Airbnb", "take rate", "Pilot: 6-10% host fee (vs 15.5%) on bookings arriving via the host's own link; response to direct-booking leakage", "https://skift.com/2026/08/29/airbnb-is-testing-lower-fees-for-hosts-who-bring-their-own-guests/; https://www.bloomberg.com/news/articles/2026-08-31/airbnb-rolls-out-pilot-program-in-us-to-lower-fees-paid-by-hosts-to-6-or-10"),
    ("2026-09-02", "Expedia/Vrbo", "pricing", "Vrbo auto-enrols hosts in 'Members Only Deals' (automatic discounts to One Key members) unless they opt out by 10 Sep 2026; extends the supplier-funded-promotion model that was >40% of Vrbo bookings in Q2'26", "https://www.rentalscaleup.com/ (RSU by PriceLabs, 2 Sep 2026, via Google News)"),
    ("2026-09-04", "EU Commission", "regulatory", "Draft Affordable Housing Act leaked: enabling framework letting authorities restrict STRs in housing-stress areas; primary residences exempt; formal presentation 9 Sep 2026", "Reuters 4 Sep 2026 'Proposed EU rules would curb Airbnb, short-term rental homes, draft shows'; https://skift.com/2026/09/04/european-commission-short-term-rental-crackdown/; euractiv.com 4 Sep 2026"),
    ("2026-09-01", "Airbnb", "hotels", "Pepijn Rijvers (13 yrs Booking.com, ran hotels; Viator president) named Chief Business Officer over Homes, Hotels, Global Markets", "https://skift.com/2026/09/01/airbnb-names-ex-booking-com-hotel-boss-and-viator-president-as-chief-business-officer/"),
]
ev = pd.DataFrame(events, columns=["date", "actor", "category", "event", "source"]).sort_values("date")
ev.to_csv(os.path.join(OUT, "11_competitor_events.csv"), index=False)

# --------------------------------------------------------------------------------------
# 4. Regulatory overlay: probability-weighted drag by year and region
# --------------------------------------------------------------------------------------
prof = pd.read_csv(P("data", "processed", "abnb_regulatory_profile.csv"))
con = pd.read_csv(P("data", "processed", "abnb_regulatory_contributions.csv"))
eu_ids = {"EU-AHA", "EU-TAIL", "ES-REMOVE", "ES-REGIONS", "BCN-2028", "BCN-PARTIAL", "PARIS-PRO", "PARIS-COPRO", "GR-FREEZE", "IE-REG", "UK-ENG", "IT-NAT", "PT-RETIGHT", "NL-AMS"}
us_ids = {"US-CITY", "NYC-LOOSEN", "CHI-SUIT", "MAUI"}
def region_split(h):
    d = con[con.horizon == h]
    eu = d[d.id.isin(eu_ids)].expected_loss_pct.sum()
    us = d[d.id.isin(us_ids)].expected_loss_pct.sum()
    return eu, us
eu27, us27 = region_split(2027)
eu30, us30 = region_split(2030)
med27 = prof[(prof.horizon == 2027) & (prof.percentile == "50")].revenue_loss_pct.iloc[0]
mean27 = prof[(prof.horizon == 2027) & (prof.percentile == "mean")].revenue_loss_pct.iloc[0]
med30 = prof[(prof.horizon == 2030) & (prof.percentile == "50")].revenue_loss_pct.iloc[0]
mean30 = prof[(prof.horizon == 2030) & (prof.percentile == "mean")].revenue_loss_pct.iloc[0]
p95_27 = prof[(prof.horizon == 2027) & (prof.percentile == "95")].revenue_loss_pct.iloc[0]
p95_30 = prof[(prof.horizon == 2030) & (prof.percentile == "95")].revenue_loss_pct.iloc[0]
# Timing: profile gives end-2027 and end-2030 run-rates. Interpolate: 2026 = events already in force (Paris copro, Greece freeze, Spain regions partial)
# ~ one third of the 2027 run-rate; 2028 = linear between 2027 and 2030 (one third of the way).
def interp(v27, v30, year):
    if year == 2026:
        return v27 / 3
    if year == 2027:
        return v27
    return v27 + (v30 - v27) * (year - 2027) / 3
share_emea_rev = 0.39  # EMEA share of revenue (pitch landscape: NA 42, EMEA 39, LatAm 9, APAC 9)
share_na_rev = 0.42
eu_frac27 = eu27 / (eu27 + us27)
eu_frac30 = eu30 / (eu30 + us30)
reg_rows = []
for y in [2026, 2027, 2028]:
    med = interp(med27, med30, y); mean = interp(mean27, mean30, y); p95 = interp(p95_27, p95_30, y)
    eu_frac = eu_frac27 if y <= 2027 else eu_frac27 + (eu_frac30 - eu_frac27) * (y - 2027) / 3
    reg_rows.append(dict(year=y, revenue_drag_pct_median=round(med, 3), revenue_drag_pct_mean=round(mean, 3), revenue_drag_pct_p95=round(p95, 3),
                         europe_share_of_drag=round(eu_frac, 2),
                         emea_nights_drag_pct_median=round(med * eu_frac / share_emea_rev, 2),
                         na_nights_drag_pct_median=round(med * (1 - eu_frac) / share_na_rev, 2),
                         global_nights_drag_pct_median=round(med, 2),
                         note="run-rate loss vs Q2'26 baseline, net of recapture; 2026 = one third of end-2027 (already-in-force items), 2028 = linear toward end-2030; nights drag assumes loss is volume not price",
                         source="data/processed/abnb_regulatory_profile.csv; abnb_regulatory_contributions.csv; research/notes/2026-09-05_regulatory-forecast-profile.md"))
reg = pd.DataFrame(reg_rows)
pending = pd.DataFrame([
    dict(date="2026-09-09", item="EU Affordable Housing Act proposal presented (Ribera)", region="EMEA", what_it_does="Enabling framework: authorities may restrict STRs in housing-stress areas (price-to-income test), quantitative limits or grandfathering, primary residences exempt; must pass Council and Parliament (EU median ~18 months)", model_link="EU-AHA p(2030)=45%; move to 60% if binding caps or primary residences included", status_6sep="Draft leaked 4-5 Sep matches the 'proportionate enabling' reading; no change to probabilities yet", source="https://ca.investing.com/news/stock-market-news/eu-proposes-to-curb-airbnb-and-shortterm-rentals-amid-housing-shortage-4829353; https://skift.com/2026/09/04/european-commission-short-term-rental-crackdown/"),
    dict(date="2026-09 to 2026-10", item="NYC OSE FY26 registration report and Oct renewals; Int 879-2026 (owner-occupied 1-2 family loosening) has no hearing scheduled", region="NA", what_it_does="Upside only: 20% chance of loosening by 2027", model_link="NYC-LOOSEN -0.14% if enacted", status_6sep="No hearing as of 31 Aug 2026", source="https://www.bookwithhaven.com/blog/nyc-short-term-rental-law"),
    dict(date="2026 H2 (undated)", item="Spain replacement for the annulled national registry (Supreme Court 19 May 2026 voided RD 1312/2024; regional registers and platform data-sharing survive)", region="EMEA", what_it_does="A replacement law with platform verification would re-enable mass removals (ES-REMOVE 35% by 2027)", model_link="ES-REMOVE 0.25% loss if in force", status_6sep="No replacement text found as of 6 Sep", source="https://skift.com/2026/05/22/spains-top-court-voids-national-short-term-rental-registry/"),
    dict(date="2026-12-01", item="Ireland STR register launch", region="EMEA", what_it_does="Planning-compliance enforcement could remove >20% of Irish listings within a year (p 35%)", model_link="IE-REG 0.09%", status_6sep="Launch date already slipped once", source="research/notes/2026-09-05_regulatory-forecast-profile.md"),
    dict(date="2026-12-31", item="Greek ministerial decision on extending Athens/Thessaloniki registration freezes into 2027", region="EMEA", what_it_does="p 70% extended; attrition through the transfer rule", model_link="GR-FREEZE 0.06%", status_6sep="Undecided", source="same"),
    dict(date="2027-05", item="Barcelona municipal election ahead of the Nov 2028 licence lapse (10,101 licences)", region="EMEA", what_it_does="p 45% that 70%+ of licences lapse and are enforced", model_link="BCN-2028 0.24% (2030 only)", status_6sep="No change", source="same"),
    dict(date="2026-09-06", item="NEWS SCAN 5-6 Sep 2026 (post regulatory-forecast cut-off)", region="global", what_it_does="Google News sweep of 'Airbnb regulation' for the trailing week returned: EU draft (Reuters/Euractiv/Skift, 4 Sep, already modelled as EU-AHA); Hillsborough County FL STR ordinance into law (2-3 Sep); Richardson TX distance/fee rules effective 4 Sep; Pennsylvania caps and Italy tax enforcement (RentalScaleUp, early Sep); Ventura CA permit cap and fee hike", model_link="All US items sit inside US-CITY (p=30% by 2027, 0.22% loss if occurs); none is individually material", status_6sep="No probability changes made", source="https://news.google.com/rss/search?q=Airbnb+regulation+when:7d (retrieved 6 Sep 2026); https://www.rentalscaleup.com/"),
    dict(date="2029-01-01", item="Maui Bill 9 West Maui phase-out (lawsuits filed Jan 2026, no injunction; Planning Commission rejected the softening bill Feb 2026)", region="NA", what_it_does="p 40% proceeds with <50% exempt", model_link="MAUI 0.08% (2030 only)", status_6sep="No change", source="https://www.civilbeat.org/2026/02/maui-planning-commission-rejects-bill-to-save-thousands-of-vacation-rentals/"),
])
reg.to_csv(os.path.join(OUT, "11_regulatory_overlay.csv"), index=False)
pending.to_csv(os.path.join(OUT, "11_regulatory_pending_items.csv"), index=False)

# --------------------------------------------------------------------------------------
# 5. New-business scenarios FY26-FY28 (revenue, USD m)
# --------------------------------------------------------------------------------------
fy25_rev = 12241.0
fy25_nights = float(abnb_annual[2025])
platform_growth = {"bear": [0.095, 0.06, 0.06], "base": [0.10, 0.09, 0.09], "bull": [0.105, 0.10, 0.10]}  # nights growth FY26-28 (model/assumptions.md)
scen = {
    # business: (FY25 revenue estimate, growth by scenario FY26, FY27, FY28), assumptions text
    "hotels": dict(fy25=290.0, growth={"bear": [0.20, 0.15, 0.12], "base": [0.35, 0.30, 0.25], "bull": [0.60, 0.50, 0.40]},
                   assumptions="FY25: hotels 'single-digit % of nights' (Q4'25 call) -> assume 3.5% of 533m nights = 18.7m nights x ~$140 hotel ADR x ~11% commission (undisclosed; 'best-in-class' per Q3'25 call) = ~$290m. Growth: Q2'26 hotel nights ~3x homes (~30%); base fades 35/30/25%; bull holds 3-5x; bear reverts to 2x platform after the 15% credit expires 31 Dec 2026. Jefferies: hotels ~$1bn by 2030 (https://finance.yahoo.com/markets/stocks/articles/airbnb-hotels-experiences-push-could-add-153900298.html)"),
    "experiences": dict(fy25=90.0, growth={"bear": [0.25, 0.20, 0.15], "base": [0.50, 0.45, 0.40], "bull": [0.80, 0.70, 0.60]},
                        assumptions="FY25: ~40,000 experiences, GBV assumed ~$450m x 20% take (Airbnb help centre: 20% on experiences) = ~$90m. Q2'26: supply +80% y/y, bookings accelerating on a small base; 'thousands of markets ... not this year' (Q2'26 call). Almost half of bookings not attached to a stay (3Q25/4Q25 letters)"),
    "services": dict(fy25=12.0, growth={"bear": [1.0, 0.6, 0.4], "base": [2.5, 1.2, 0.8], "bull": [4.0, 2.0, 1.2]},
                     assumptions="FY25: 10 categories in 260 cities from May 2025 at a 15% host fee ($6 minimum); assume ~$80m GBV = ~$12m revenue. 2026 partner services (car rental, airport pickup, luggage, grocery) are referral economics, 'do not think they'll incur a lot of costs' (Q2'26 call). Management: 3-5 years to materiality"),
    "sponsored_listings_ads": dict(fy25=0.0, growth=None, levels={"bear": [0, 0, 60], "base": [0, 120, 350], "bull": [0, 250, 700]},
                                   assumptions="Not launched; Wedbush (Aug 2026) expects sponsored listings in 2027 (pitch catalogue); Skift 2023 sized an ad platform at $1.2bn by 2026 (did not happen). Vrbo and Booking already sell placement; T5: paid placement and rebates already exist on the host side. Base: 2027 launch, 0.3% of GBV by FY28"),
    "co_host_network": dict(fy25=0.0, growth=None, levels={"bear": [0, 0, 0], "base": [0, 0, 0], "bull": [0, 0, 0]},
                            assumptions="No incremental take rate on co-host listings (Q1'25 call); value is supply quality (co-hosted new listings earn ~2x). Zero direct revenue in all cases"),
    "long_term_stays": dict(fy25=None, growth=None, levels=None,
                            assumptions="17-18% of nights (2023-24 disclosures); inside core nights, not incremental; lower take rate after month three. Not modelled separately"),
    "rnpl_payments": dict(fy25=None, growth=None, levels=None,
                          assumptions="Reserve Now, Pay Later: ~20% of GBV (Q1'26), +3 pts nights (Q1'26), +1 pt cancellation rate; no fee revenue; working-capital drag (unearned fees). Laps from Q3'26 US. Growth lever inside core nights, not a revenue line"),
    "airbnb_for_work": dict(fy25=None, growth=None, levels=None,
                            assumptions="Last disclosure: ~700,000 companies (2019, https://news.airbnb.com/airbnb-for-work-700000/); no nights share disclosed since. Not modelled"),
}
nb_rows = []
for name, s in scen.items():
    for case in ["bear", "base", "bull"]:
        if s.get("fy25") is None:
            nb_rows.append(dict(business=name, case=case, fy25_rev_musd=np.nan, fy26_rev_musd=np.nan, fy27_rev_musd=np.nan, fy28_rev_musd=np.nan, fy28_incremental_vs_platform_growth_musd=np.nan, assumptions=s["assumptions"]))
            continue
        if s.get("growth"):
            g = s["growth"][case]
            lv = [s["fy25"] * (1 + g[0])]
            lv.append(lv[-1] * (1 + g[1])); lv.append(lv[-1] * (1 + g[2]))
        else:
            lv = s["levels"][case]
        pg = platform_growth[case]
        base_path = s["fy25"] * (1 + pg[0]) * (1 + pg[1]) * (1 + pg[2])  # what the FY25 base would be if it merely grew with the platform (already inside the driver model's nights)
        nb_rows.append(dict(business=name, case=case, fy25_rev_musd=round(s["fy25"], 0), fy26_rev_musd=round(lv[0], 0), fy27_rev_musd=round(lv[1], 0), fy28_rev_musd=round(lv[2], 0),
                            fy28_incremental_vs_platform_growth_musd=round(lv[2] - base_path, 0), assumptions=s["assumptions"]))
nb = pd.DataFrame(nb_rows)
tot = nb.dropna(subset=["fy25_rev_musd"]).groupby("case")[["fy25_rev_musd", "fy26_rev_musd", "fy27_rev_musd", "fy28_rev_musd", "fy28_incremental_vs_platform_growth_musd"]].sum().reset_index()
tot["business"] = "TOTAL (hotels+experiences+services+ads)"
tot["assumptions"] = "Sum; incremental column = FY28 revenue minus the FY25 base compounded at the scenario's platform nights growth (i.e. what is not already inside the driver model's nights path). Base FY28 revenue (driver model) ~ $17bn"
nb = pd.concat([nb, tot[nb.columns]], ignore_index=True)
nb.to_csv(os.path.join(OUT, "11_new_business_scenarios.csv"), index=False)

# --------------------------------------------------------------------------------------
# 6. AI disintermediation exposure scenarios
# --------------------------------------------------------------------------------------
gbv26 = 91.3 * 1.15  # FY26 GBV ~ $105bn, USD bn (H1'26 GBV +17%)
rev26 = fy25_rev * 1.14  # USD m (fy25_rev is USD m)
ai_rows = []
for year, s_list in [(2026, [0.005, 0.01, 0.02]), (2027, [0.01, 0.03, 0.06]), (2028, [0.02, 0.05, 0.10])]:
    gbv = gbv26 * (1.12 ** (year - 2026))          # USD bn
    rev = rev26 * (1.11 ** (year - 2026))          # USD m
    for case, s in zip(["low", "mid", "high"], s_list):
        for fee in [0.03, 0.05, 0.08]:
            cost = s * fee * gbv * 1000  # USD m (bn -> m)
            ai_rows.append(dict(year=year, case=case, ai_referred_share_of_gbv=s, referral_fee_pct_of_gbv=fee,
                                revenue_musd=round(rev, 0), cost_musd=round(cost, 0),
                                cost_pct_revenue=round(100 * cost / rev, 2),
                                cost_pct_adj_ebitda=round(100 * cost / (rev * 0.36), 2),
                                note="Cost if that share of GBV arrives via a paid AI referral instead of direct/app. Anchors: Booking <1% of room nights from AI tools (Q2'26); T2 ~3% of bookings AI-native in 12-24 months; Airbnb 90% direct/unpaid, app 64% of nights (Q2'26); metasearch CPC economics 3-8% of booking value (analyst assumption)"))
ai = pd.DataFrame(ai_rows)
ai.to_csv(os.path.join(OUT, "11_ai_exposure_scenarios.csv"), index=False)

# --------------------------------------------------------------------------------------
# Figure: Airbnb nights growth vs Booking.com alt-accom room-night growth (quarters with a disclosure)
# --------------------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

f = altq.dropna(subset=["bkng_alt_accom_nights_yoy"]).copy()
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
x = np.arange(len(f))
w = 0.38
ax.bar(x - w / 2, 100 * f["airbnb_nights_yoy"], w, color="#2a78d6", label="Airbnb nights & seats y/y")
ax.bar(x + w / 2, 100 * f["bkng_alt_accom_nights_yoy"], w, color="#eb6834", label="Booking.com alt-accom room nights y/y")
for i, (a, b) in enumerate(zip(f["airbnb_nights_yoy"], f["bkng_alt_accom_nights_yoy"])):
    ax.text(i - w / 2, 100 * a + 0.4, f"{100*a:.0f}", ha="center", va="bottom", fontsize=8, color="#52514e")
    ax.text(i + w / 2, 100 * b + 0.4, f"{100*b:.0f}", ha="center", va="bottom", fontsize=8, color="#52514e")
ax.set_xticks(x); ax.set_xticklabels(f["quarter"])
ax.set_ylabel("% y/y"); ax.set_ylim(0, 22)
ax.set_title("Booking.com's alt-accom out-grew Airbnb in 2024-25; the gap flipped in 1H26", fontsize=10, loc="left")
ax.spines[["top", "right"]].set_visible(False); ax.grid(axis="y", color="#e6e5e1", lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=8, loc="upper right")
fig.text(0.01, 0.01, "Sources: Airbnb letters (abnb_quarterly_kpis_from_study.csv); Booking Holdings calls/8-Ks (see 11_alt_accom_share_quarterly.csv). Quarters where Booking disclosed alt-accom growth.", fontsize=6.5, color="#52514e")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(os.path.join(FIG, "11_alt_accom_growth.png"))

# --------------------------------------------------------------------------------------
# Console summary
# --------------------------------------------------------------------------------------
pd.set_option("display.width", 200)
print("== alt accom annual"); print(alt.drop(columns="source").to_string(index=False))
print("== alt accom quarterly"); print(altq.drop(columns="source").to_string(index=False))
print("== nights per listing"); print(pd.DataFrame(npl)[["date", "value", "note"]].to_string(index=False))
print("== Inside Airbnb year-ago retention by end year"); print(ret_wide.round(3).to_string())
print("== Inside Airbnb matched-listing reviews LTM change by end year"); print(ret.pivot(index="city", columns="end_year", values="matched_reviews_chg").round(3).to_string())
print("== CC survival"); print(ccy.to_string(index=False))
print("== implied share of global STR gross bookings"); print(cap.pivot(index="period", columns="source_name", values="value").to_string())
print("== regulatory overlay"); print(reg.drop(columns=["note", "source"]).to_string(index=False))
print(f"EU share of expected loss 2027 {eu_frac27:.2f}, 2030 {eu_frac30:.2f}")
print("== new business"); print(nb.drop(columns="assumptions").to_string(index=False))
print("== AI exposure (mid case, 5% fee)"); print(ai[(ai.case == "mid") & (ai.referral_fee_pct_of_gbv == 0.05)].drop(columns="note").to_string(index=False))
