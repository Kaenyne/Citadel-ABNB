"""
REGIONAL nights model - one calibration per Airbnb reporting segment, on that region's own data.

Supersedes the aggregate treatment in choice_nights_driver_global.py. The four regions are not
variants of one market: 2025 ADR runs $255 in North America against $95 in LatAm, stay length is
FLAT in NA and FALLING 2.7%/yr in LatAm, and disclosed nights growth spans +2.6% to +18.4%. Since
the team forecasts ADR regionally, nights are now built the same way, so the two can be multiplied
region by region without a mix error.

EVIDENCE AVAILABLE PER REGION - the confidence gradient runs BACKWARDS to the growth:

  NORTH AMERICA   full segment choice model. Hotel side: STR/CoStar 1.3bn room nights, AHLA
                  business split, Hawaii+Vegas leisure party mix, CoStar demand and ADR forecasts.
                  Airbnb side: disclosed nights, revenue-share proxy for the U.S., 10-K stay length.
                  -> the only region where P(Airbnb | contestable) is actually calibrated.

  EMEA            hotel side MEASURED: Eurostat platform guest-nights (tour_ce_omr) and hotel
                  guest-nights (I551) for FR/ES/IT/DE, scaled to EMEA. Party size by accommodation
                  now also measured, from Spain's INE ETR microdata (11 years). Airbnb side:
                  disclosed nights, 10-K stay length (4.4 -> 3.8, the steepest decline of any region).

  LATIN AMERICA   NO hotel-side data. Growth model only. What IS region-specific: disclosed nights
                  (+18.4% in 2025), ADR $94.91 (+1.7%, the weakest of the four), and stay length
                  falling fastest (-2.7%/yr, 4.4 -> 3.6 since 2020).

  ASIA PACIFIC    NO hotel-side data. Growth model only. Region-specific: disclosed nights (+14.8%),
                  ADR $118.20 (+1.2%), and the ONLY region where stay length is RISING (2.8 -> 3.3,
                  +18% since 2020). Japan's minpaku law caps a property at 180 nights/yr and lets
                  municipalities zero it out, so APAC supply has a legal ceiling the others lack.

  => LatAm + APAC are 30% of 2025 nights and ~62% of 2025-30 growth on NO hotel-side evidence.
     That is the single largest research gap in the nights work.

ADR: regional ADR = regional GBV / regional nights from the FY2025 10-K regional table. This
INCLUDES FX, whereas the share equation wants an ex-FX comparison. Regional ex-FX paths should
replace ADR_GROWTH below as soon as the team's regional ADR line lands - flagged, not silently
assumed. Only NA and EMEA have a hotel ADR comparator, so only they run a price-driven share term.

Run:  python analysis/src/choice_nights_driver_regional.py
Out:  data/processed/choice_driver_regional_detail.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"
sys.path.insert(0, str(ROOT / "analysis/src"))

import choice_nights_driver as us_model  # noqa: E402

YEARS = [2025, 2026, 2027, 2028, 2029, 2030]

# ---- 2025 anchors, all from the FY2025 10-K regional table (nights, GBV -> ADR) and MD&A stay length
ANCHOR = {
    "north_america": {"nights": 158.0, "adr": 255.03, "stay": 4.1, "nights_g25": 0.026},
    "emea":          {"nights": 215.0, "adr": 158.89, "stay": 3.8, "nights_g25": 0.070},
    "latam":         {"nights":  90.0, "adr":  94.91, "stay": 3.6, "nights_g25": 0.184},
    "apac":          {"nights":  70.0, "adr": 118.20, "stay": 3.3, "nights_g25": 0.148},
}

# ---- Own-category growth: implied by inverting the model identity on disclosed 2025 nights growth,
#      then faded. g_cat = (g_total - CONTESTABLE * g_contestable) / (1 - CONTESTABLE).
CATEGORY = {
    "north_america": {2026: 0.033, 2027: 0.032, 2028: 0.030, 2029: 0.029, 2030: 0.028},
    "emea":          {2026: 0.085, 2027: 0.078, 2028: 0.070, 2029: 0.063, 2030: 0.057},
    "latam":         {2026: 0.230, 2027: 0.200, 2028: 0.175, 2029: 0.155, 2030: 0.138},
    "apac":          {2026: 0.185, 2027: 0.165, 2028: 0.148, 2029: 0.133, 2030: 0.120},
}
# EMEA implied +10.3% is haircut to 8.5% for the WS11 regulatory drag; LatAm 27.3% and APAC 21.3%
# are haircut hard because a first-year implied rate off one year of data is not a trend.

# ---- Lodging-market growth for the contestable pool (only NA and EMEA have a measured pool)
MARKET = {"north_america": 0.015, "emea": 0.020, "latam": 0.030, "apac": 0.035}

# ---- ADR paths. NA/EMEA hotel comparators are real forecasts; LatAm/APAC have none.
ABNB_ADR = {  # PROVISIONAL - replace with the team's regional ex-FX line when it lands
    "north_america": 0.030, "emea": 0.028, "latam": 0.020, "apac": 0.018,
}
HOTEL_ADR = {"north_america": 0.025, "emea": 0.025, "latam": None, "apac": None}

# ---- Stay length: 10-K regional nights-per-booking. NA flat since 2023; EMEA and LatAm falling;
#      APAC the only riser. Paths fade each region's recent rate toward zero.
STAY_DRIFT = {"north_america": 0.000, "emea": -0.008, "latam": -0.015, "apac": +0.006}

CONTESTABLE = us_model.CONTESTABLE
SWITCH_RATE = us_model.SWITCH_RATE


def region_path(name):
    a = ANCHOR[name]
    N = (1 - CONTESTABLE) * a["nights"]
    M_pool = CONTESTABLE * a["nights"]
    P = 1.0  # contestable Airbnb / itself; the pool below carries the hotel side where known
    hotel_adr = HOTEL_ADR[name]
    out, sl = {2025: a["nights"]}, 1.0
    contestable = M_pool
    for y in YEARS[1:]:
        N *= (1 + CATEGORY[name][y])
        contestable *= (1 + MARKET[name])
        if hotel_adr is not None:
            dln = np.log(1 + ABNB_ADR[name]) - np.log(1 + hotel_adr)
            contestable *= np.exp(-SWITCH_RATE * dln * CONTESTABLE)  # share response, pool-scaled
        sl *= (1 + STAY_DRIFT[name])
        out[y] = (N + contestable) * sl
    return out


def main():
    paths = {r: region_path(r) for r in ANCHOR}
    df = pd.DataFrame({"year": YEARS, **{r: [paths[r][y] for y in YEARS] for r in ANCHOR}})
    df["total"] = df[list(ANCHOR)].sum(axis=1)

    print("REGIONAL NIGHTS (mm) - each region on its own data\n")
    print(df.round(1).to_string(index=False))
    g = df.set_index("year").pct_change() * 100
    print("\nGROWTH (%)")
    print(g.round(1).to_string())

    print("\nCAGR 2025-30, share of nights, and what each region is built on")
    basis = {"north_america": "full choice model (STR/AHLA/CoStar hotel side)",
             "emea": "measured Eurostat platform+hotel, Spain INE party size",
             "latam": "GROWTH MODEL ONLY - no hotel-side data",
             "apac": "GROWTH MODEL ONLY - no hotel-side data"}
    rows = []
    for r in list(ANCHOR) + ["total"]:
        s = df.set_index("year")[r]
        c = (s.loc[2030] / s.loc[2025]) ** 0.2 - 1
        sh0, sh1 = s.loc[2025] / df.total.iloc[0], s.loc[2030] / df.total.iloc[-1]
        print(f"  {r:14s} {c * 100:+6.2f}%/yr  share {sh0 * 100:4.1f}% -> {sh1 * 100:4.1f}%   "
              f"{basis.get(r, 'sum')}")
        rows.append({"region": r, "nights_2025": s.loc[2025], "nights_2030": s.loc[2030],
                     "cagr": c, "share_2025": sh0, "share_2030": sh1,
                     "adr_2025": ANCHOR.get(r, {}).get("adr"), "basis": basis.get(r, "sum")})

    tot0, tot1 = df.total.iloc[0], df.total.iloc[-1]
    print(f"\nSHARE OF THE {(tot1 / tot0 - 1) * 100:.1f}% FIVE-YEAR GROWTH")
    evid = 0.0
    for r in ANCHOR:
        s = df.set_index("year")[r]
        part = (s.loc[2030] - s.loc[2025]) / (tot1 - tot0)
        print(f"  {r:14s} {part * 100:5.1f}%")
        if r in ("latam", "apac"):
            evid += part
    print(f"  => {evid * 100:.0f}% of all growth comes from the two regions with NO hotel-side data.")

    print("\nGBV CROSS-CHECK (nights x ADR, 2025) - ties to the disclosed regional table")
    for r in ANCHOR:
        print(f"  {r:14s} {ANCHOR[r]['nights'] * ANCHOR[r]['adr'] / 1000:6.2f}bn")

    pd.DataFrame(rows).to_csv(OUT / "choice_driver_regional_detail.csv", index=False)
    print("\nwrote", OUT / "choice_driver_regional_detail.csv")


if __name__ == "__main__":
    main()
