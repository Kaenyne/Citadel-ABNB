"""Workstream 06: the Airbnb-vs-hotel price gap, quarterly and monthly, with sourced externals.

Reads : data/processed/abnb_driver_history_quarterly.csv     ABNB nights, GBV, ADR, take rate (letters)
        data/raw/fred/CUSR0000SEHB.csv (refreshed from FRED)  CPI lodging away from home, SA
        data/raw/bea/bea_pce_travel_monthly_2015_2026.csv     BEA PCE hotels-and-motels price index
        data/processed/predictive/02_peer_prints.csv          HLT and MAR system-wide RevPAR y/y
        EXTERNALS below                                       STR/CoStar US hotel ADR and RevPAR,
                                                              and Airbnb's own 1-bedroom-vs-hotel claims
Writes: data/processed/overnight/06_price_gap_series.csv      quarterly, 1Q21-2Q26 + monthly hotel block
        data/processed/overnight/06_price_gap_monthly.csv     monthly CPI/BEA/STR through latest print

Extends research/notes/2026-09-05_margin-drivers.md section 3.4 and analysis/src/hotel_price_monitor.py:
this file adds (a) STR/CoStar dollar ADR levels, not just index y/y, (b) HLT/MAR RevPAR alongside,
(c) the per-unit normalisation (ABNB ADR per listing-night vs hotel ADR per room-night, and ABNB ADR
divided by average bedrooms from the Inside Airbnb cross-section), and (d) Airbnb's own published
like-for-like 1-bedroom comparison.
Run: py -3.13 analysis/src/overnight/06_price_gap.py
"""
import io
import os
import urllib.request

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
OUT = os.path.join(ROOT, "data", "processed", "overnight")

# ---------------------------------------------------------------------------------------------
# EXTERNALS. Every row is a published figure; `source` carries the citation. Nothing is interpolated.
# ---------------------------------------------------------------------------------------------

# US hotel ADR, full-year averages, STR/CoStar as reported in the trade press. USD.
STR_ANNUAL_ADR = {}     # filled from EXTERNAL_SERIES below; kept for readability
# Airbnb's own comparison: average nightly price of a one-bedroom Airbnb listing vs hotel ADR.
# "Prices include all fees but exclude taxes. Sources: CoStar, Airbnb" (3Q23 and 4Q23 letters).
ABNB_1BR_VS_HOTEL = [
    {"month": "2023-09", "abnb_1br_usd": 120, "abnb_1br_yoy_pct": 1, "hotel_adr_usd": 153,
     "hotel_adr_yoy_pct": 10, "source": "ABNB 3Q23 shareholder letter, footnote 4 (CoStar, Airbnb)"},
    {"month": "2023-12", "abnb_1br_usd": 114, "abnb_1br_yoy_pct": -2, "hotel_adr_usd": 149,
     "hotel_adr_yoy_pct": 7, "source": "ABNB 4Q23 shareholder letter, footnote 3 (CoStar, Airbnb)"},
    {"month": "2024-03", "abnb_1br_usd": 114, "abnb_1br_yoy_pct": -2, "hotel_adr_usd": 140.16,
     "hotel_adr_yoy_pct": 1.6,
     "source": "Skift 22-May-2024 'Are Airbnbs Cheaper Than Hotels?' citing Airbnb and CoStar"},
]

# ADR y/y as stated in the letters, reported and ex-FX, plus the stated ADR driver.
ADR_STATED = {
    "4Q24": (2, None), "1Q25": (-1, 1), "2Q25": (3, 2), "3Q25": (5, 3),
    "4Q25": (6, 3), "1Q26": (9, 4), "2Q26": (5, 4),
}


def fred(series):
    u = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    try:
        raw = urllib.request.urlopen(u, timeout=60).read().decode()
        d = pd.read_csv(io.StringIO(raw))
    except Exception as e:
        print("FRED fetch failed, using cached file:", e)
        d = pd.read_csv(os.path.join(ROOT, "data/raw/fred", series + ".csv"))
    d.columns = ["date", "value"]
    d = d[d["value"] != "."].copy()
    d["value"] = d["value"].astype(float)
    d["month"] = d["date"].astype(str).str[:7]
    return d.set_index("month")["value"]


def yoy(s):
    prev = s.copy()
    prev.index = [f"{int(m[:4]) + 1}{m[4:]}" for m in s.index]
    return (100 * (s / prev.reindex(s.index) - 1)).round(2)


def main():
    os.makedirs(OUT, exist_ok=True)

    # ---- monthly hotel price block -----------------------------------------------------------
    cpi = fred("CUSR0000SEHB")
    bea_raw = pd.read_csv(os.path.join(ROOT, "data/raw/bea/bea_pce_travel_monthly_2015_2026.csv"))
    bea = bea_raw[(bea_raw["series"] == "hotels_motels") &
                  (bea_raw["measure"] == "price_index_2017eq100")].copy()
    bea["month"] = bea["date"].astype(str).str[:7]
    bea_s = bea.set_index("month")["value"]
    m = pd.DataFrame({"cpi_lodging_index": cpi, "cpi_lodging_yoy_pct": yoy(cpi),
                      "bea_hotels_price_index": bea_s, "bea_hotels_price_yoy_pct": yoy(bea_s)})
    m = m[m.index >= "2019-01"].reset_index().rename(columns={"index": "month"})
    ext = pd.DataFrame(EXTERNAL_MONTHLY)
    m = m.merge(ext, on="month", how="left")
    onebr = pd.DataFrame(ABNB_1BR_VS_HOTEL)
    m = m.merge(onebr, on="month", how="left")
    m.to_csv(os.path.join(OUT, "06_price_gap_monthly.csv"), index=False)

    # ---- quarterly gap series ----------------------------------------------------------------
    d = pd.read_csv(os.path.join(ROOT, "data/processed/abnb_driver_history_quarterly.csv"))
    d["yq"] = d["year"].astype(int).astype(str) + "Q" + d["q"].astype(int).astype(str)
    q = d[["quarter", "yq", "nights_m", "gbv_musd", "adr", "adr_yoy_pct", "nights_m_yoy_pct",
           "take_rate_calc_pct", "revenue_musd_yoy_pct", "fx_pts", "nights_m_ltm",
           "gbv_musd_ltm"]].copy()
    q["abnb_adr_yoy_letter_pct"] = q["quarter"].map(lambda x: ADR_STATED.get(x, (None, None))[0])
    q["abnb_adr_exfx_yoy_letter_pct"] = q["quarter"].map(lambda x: ADR_STATED.get(x, (None, None))[1])

    # quarterly averages of the monthly hotel indices
    mm = m.copy()
    mm["yq"] = pd.PeriodIndex(pd.to_datetime(mm["month"] + "-01"), freq="Q").astype(str)
    hq = mm.groupby("yq").agg(cpi_lodging_index=("cpi_lodging_index", "mean"),
                              bea_hotels_price_index=("bea_hotels_price_index", "mean"),
                              str_us_hotel_adr_usd=("str_us_hotel_adr_usd", "mean"),
                              str_us_hotel_revpar_usd=("str_us_hotel_revpar_usd", "mean"),
                              str_us_hotel_occ_pct=("str_us_hotel_occ_pct", "mean"),
                              months_with_str=("str_us_hotel_adr_usd", "count")).reset_index()
    for c in ("cpi_lodging_index", "bea_hotels_price_index"):
        hq[c.replace("_index", "") + "_yoy_pct"] = (100 * (hq[c] / hq[c].shift(4) - 1)).round(2)
    # a quarterly STR average is only meaningful with all three months present
    part = hq["months_with_str"] < 3
    hq.loc[part, ["str_us_hotel_adr_usd", "str_us_hotel_revpar_usd", "str_us_hotel_occ_pct"]] = None
    hq["str_us_hotel_adr_yoy_pct"] = float("nan")
    for c in ("str_us_hotel_adr_usd", "str_us_hotel_revpar_usd", "str_us_hotel_occ_pct"):
        hq[c] = pd.to_numeric(hq[c], errors="coerce")
    q = q.merge(hq, on="yq", how="left")

    peers = pd.read_csv(os.path.join(ROOT, "data/processed/predictive/02_peer_prints.csv"))
    peers["yq"] = peers["quarter"].str.replace("Q", "Q", regex=False)
    q = q.merge(peers[["yq", "mar_revpar_yoy", "hlt_revpar_yoy", "bkng_room_nights_yoy",
                       "bkng_gb_yoy_cc"]], on="yq", how="left")

    # per-unit normalisation from the Inside Airbnb cross-section (all-in quote basis in 2026)
    try:
        pu = pd.read_csv(os.path.join(OUT, "06_price_per_unit_panel.csv"))
        pu["yq"] = pd.PeriodIndex(pd.to_datetime(pu["dump_date"]), freq="Q").astype(str)
        us = ["austin", "chicago", "los-angeles", "nashville", "new-orleans", "new-york-city", "san-diego"]
        g = (pu[pu["city"].isin(us)].groupby("yq")
             .agg(ia_us_median_entire_price=("median_price_entire", "median"),
                  ia_us_median_price_per_bedroom=("median_price_per_bedroom_entire", "median"),
                  ia_us_median_price_per_person=("median_price_per_person_entire", "median"),
                  ia_us_median_1br_price=("median_price_1br_entire", "median"),
                  ia_us_mean_bedrooms_entire=("mean_bedrooms_entire", "mean"),
                  ia_us_mean_accommodates_entire=("mean_accommodates_entire", "mean"),
                  ia_us_price_basis=("price_basis", "first"),
                  ia_us_cities=("city", "nunique")).reset_index())
        q = q.merge(g, on="yq", how="left")
    except FileNotFoundError:
        print("run 06_wtp_hedonics.py first for the per-unit block")

    # ABNB ADR per bedroom-night. The 2Q26 letter discloses "more than 1 billion bedroom nights" over
    # the trailing twelve months (nights x bedroom count), the only bedroom-count datapoint Airbnb has
    # ever published. Divided by LTM nights it gives bedrooms per booked night; 1.0bn is a floor, so
    # the implied bedrooms-per-night is a floor and ADR per bedroom-night is a ceiling.
    q["abnb_bedroom_nights_ltm_m"] = q["quarter"].map({"2Q26": 1000.0})
    q["abnb_bedrooms_per_night_ltm"] = (q["abnb_bedroom_nights_ltm_m"] / q["nights_m_ltm"]).round(3)
    q["abnb_adr_per_bedroom_night_disclosed"] = (q["adr"] / q["abnb_bedrooms_per_night_ltm"]).round(2)
    q["abnb_adr_per_bedroom_proxy"] = (q["adr"] / q["ia_us_mean_bedrooms_entire"]).round(2)
    q["gap_abnb_adr_vs_str_adr_pct"] = (100 * (q["adr"] / q["str_us_hotel_adr_usd"] - 1)).round(1)
    q["gap_abnb_perbed_vs_str_adr_pct"] = (
        100 * (q["abnb_adr_per_bedroom_proxy"] / q["str_us_hotel_adr_usd"] - 1)).round(1)
    q["abnb_adr_yoy_less_cpi_lodging_pp"] = (q["adr_yoy_pct"] - q["cpi_lodging_yoy_pct"]).round(1)
    q["abnb_adr_yoy_less_str_adr_pp"] = (q["adr_yoy_pct"] - q["str_us_hotel_adr_yoy_pct"]).round(1)
    q["abnb_adr_exfx_less_str_adr_pp"] = (
        q["abnb_adr_exfx_yoy_letter_pct"] - q["str_us_hotel_adr_yoy_pct"]).round(1)
    q.round(3).to_csv(os.path.join(OUT, "06_price_gap_series.csv"), index=False)
    print("wrote 06_price_gap_series.csv", q.shape, "and 06_price_gap_monthly.csv", m.shape)
    cols = ["quarter", "adr", "adr_yoy_pct", "abnb_adr_exfx_yoy_letter_pct", "cpi_lodging_yoy_pct",
            "str_us_hotel_adr_usd", "str_us_hotel_adr_yoy_pct", "hlt_revpar_yoy", "mar_revpar_yoy",
            "gap_abnb_adr_vs_str_adr_pct", "gap_abnb_perbed_vs_str_adr_pct"]
    print(q[cols].tail(14).to_string(index=False))


# ---------------------------------------------------------------------------------------------
# STR / CoStar US hotel figures, hand-entered from the sourced pull of 6-Sep-2026. Monthly dollar
# levels for the US total are only published in press releases, so coverage is partial: the months
# below are the ones with a citable full-month figure. `str_confidence` records how it was sourced.
# Annual figures are placed on the December row so the annual comparison is not lost.
# ---------------------------------------------------------------------------------------------
EXTERNAL_MONTHLY = [
    {"month": "2022-12", "str_us_hotel_adr_annual_usd": 148.83, "str_us_hotel_revpar_annual_usd": 93.27,
     "str_us_hotel_occ_annual_pct": 62.7, "str_confidence": "medium-high",
     "str_source": "CoStar 20-Jan-2023 'US hotel ADR and RevPAR reached record highs' (full-year 2022)"},
    {"month": "2023-12", "str_us_hotel_adr_annual_usd": 155.62, "str_us_hotel_revpar_annual_usd": 97.97,
     "str_us_hotel_occ_annual_pct": 63.0, "str_confidence": "medium-high",
     "str_source": "CoStar Data Insights 30-Jan-2024 / Hotel Investment Today 18-Jan-2024 (full-year 2023)"},
    {"month": "2025-12", "str_us_hotel_adr_annual_usd": 160.54, "str_us_hotel_revpar_annual_usd": 100.02,
     "str_us_hotel_occ_annual_pct": 62.3, "str_confidence": "high",
     "str_source": "Business Travel News 20-Jan-2026 citing CoStar (full-year 2025; occ -1.2pp, ADR +0.9%, RevPAR -0.3%)"},
    {"month": "2026-03", "str_us_hotel_adr_usd": 168.06, "str_us_hotel_revpar_usd": 108.99,
     "str_us_hotel_occ_pct": 64.9, "str_us_hotel_adr_yoy_reported_pct": 3.8,
     "str_us_hotel_revpar_yoy_reported_pct": 5.9, "str_confidence": "medium-high",
     "str_source": "Business Travel News, Apr-2026, 'CoStar: March U.S. Hotel Rate, Occupancy Rise'"},
    {"month": "2026-07", "str_us_hotel_adr_usd": 171.74, "str_us_hotel_revpar_usd": 119.77,
     "str_us_hotel_occ_pct": 69.7, "str_us_hotel_adr_yoy_reported_pct": 5.7,
     "str_us_hotel_revpar_yoy_reported_pct": 8.2, "str_confidence": "high (fetched 6-Sep-2026)",
     "str_source": "Business Travel News 26-Aug-2026, 'CoStar: U.S. Hotels Grow Occupancy, Rate in July'"},
    # AirDNA US short-term-rental market (the whole STR category, of which Airbnb is the largest part).
    # Levels are far above ABNB's global ADR because the US STR universe skews to large whole homes.
    {"month": "2024-12", "airdna_us_str_adr_usd": 310.84, "airdna_us_str_adr_yoy_pct": 3.1,
     "airdna_us_str_revpar_usd": 151.26, "airdna_us_str_occ_pct": 48.7, "airdna_us_str_demand_yoy_pct": 3.0,
     "airdna_us_str_supply_yoy_pct": 4.7, "airdna_source": "AirDNA U.S. Review December 2024"},
    {"month": "2025-12", "airdna_us_str_adr_usd": 248.57, "airdna_us_str_adr_yoy_pct": 3.3,
     "airdna_us_str_revpar_usd": 126.97, "airdna_us_str_occ_pct": 51.0, "airdna_us_str_demand_yoy_pct": 1.9,
     "airdna_us_str_supply_yoy_pct": 3.4, "airdna_source": "AirDNA U.S. Review December 2025"},
    {"month": "2026-06", "airdna_us_str_adr_usd": 310.64, "airdna_us_str_adr_yoy_pct": 4.6,
     "airdna_us_str_revpar_usd": 200.19, "airdna_us_str_occ_pct": 64.4, "airdna_us_str_demand_yoy_pct": 1.9,
     "airdna_us_str_supply_yoy_pct": 1.7, "airdna_source": "AirDNA U.S. Review June 2026"},
    {"month": "2026-07", "airdna_us_str_adr_usd": 317.55, "airdna_us_str_adr_yoy_pct": 6.9,
     "airdna_us_str_revpar_usd": 217.17, "airdna_us_str_occ_pct": 68.4, "airdna_us_str_demand_yoy_pct": 2.0,
     "airdna_us_str_supply_yoy_pct": 2.6, "airdna_source": "AirDNA U.S. Review July 2026"},
]

if __name__ == "__main__":
    main()
