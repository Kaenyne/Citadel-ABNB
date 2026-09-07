"""
First DIRECT estimate of beta - cross-city Airbnb utilisation vs relative price.

Motivation: beta (the logit share sensitivity to ln(Airbnb/hotel price) in
choice_nights_driver.py) has so far been anchored on Farronato & Fradkin Table E9 (implies 10.3)
and judgment-discounted to 5.0. No one - including the published literature - has estimated it on
Airbnb's own data. This is a first, deliberately crude, attempt using the repo's Inside Airbnb
8-city extract (Jun-2026 calendars) plus web-sourced city hotel ADRs.

Design (what could be measured, not what would be ideal):
    ln( booked_nights_c / active_listings_c ) = a - eps * ln( P_abnb,c / ADR_hotel,c )
  - LHS: Airbnb demand per active listing (utilisation), from the repo calendar extract -
    booked runs x mean run length, per active listing. Same snapshot window for all cities.
  - RHS: 4-person entire home median price x 1.14 service fee vs the city hotel ADR.
  - eps maps to beta via the model's structure: only the contestable 38% of Airbnb demand responds
    to the relative price, so d ln(total nights)/d ln(relprice) = -CONTESTABLE * beta * (1-P),
    i.e. beta = eps / 0.363. If instead ALL Airbnb demand responded, beta = eps / 0.955 (bound).

Known weaknesses (all flagged, none hidden):
  - n = 5-6 cities. Cross-sectional: city amenities, STR regulation (SF permit caps!) and market
    composition load onto the price coefficient. Denver & New Orleans excluded (no defensible ADR:
    Denver sources are qualitative; New Orleans figures are event-comp distorted). DC's ADR is a
    Dec-2025 weekly print, likely below its annual level - reported with and without.
  - Hotel ADRs are mixed vintages (FY2024-FY2025-Q1'25); Airbnb prices are Jun-2026 forward.
  - A proper estimate needs the same regression in a PANEL (city x quarter, city FE) - Inside
    Airbnb archives quarterly snapshots; that is the follow-up this script is scaffolding for.

RESULT (7 Sep 2026): eps = -0.3, se 0.5, R2 0.1 - a NULL. The point estimate has the wrong sign
(more-expensive-relative-to-hotels cities show HIGHER utilisation) and is statistically zero. This is
the expected cross-sectional failure: desirable cities are simultaneously pricier and busier, and the
regression has no instrument. Conclusion recorded so nobody re-runs this design expecting better:
beta CANNOT be estimated from a single cross-section; the F&F Table E9 anchor (10.3 ceiling, 5.0
central) stands. The fix is the PANEL version - Inside Airbnb archives ~quarterly snapshots per city;
city fixed effects difference out the amenity confound, leaving within-city relative-price variation.

Run:  python analysis/src/beta_city_estimate.py
Out:  data/processed/beta_city_estimate.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

FEE = 1.14          # Airbnb service fee on top of nightly price (as in party_size_cost_crossover)
CONTESTABLE = 0.38
P_POOL = 0.045      # aggregate P from choice_driver_calibration_2025.csv

# City hotel ADRs - each with source + vintage + quality flag. DO NOT silently update:
# a change here changes beta.
HOTEL_ADR = {
    # city: (ADR, quality, source)
    "austin":       (173.83, "B",  "metro ADR, Matthews/CoStar via mmcginvest, ~FY2024-25"),
    "chicago":      (171.00, "A-", "CBD TTM mid-2025, +6.3% y/y (Chicago Hospitality/CoStar)"),
    "nashville":    (201.83, "A-", "FY2024 CoStar (ADR -2.0% y/y)"),
    "sanfrancisco": (225.82, "A",  "FY2025 CoStar top-25 release (+6.0% y/y)"),
    "seattle":      (182.00, "B+", "Q1-2025, Kidder Mathews/CBRE"),
    "washingtondc": (172.40, "C",  "week of Dec 7-13 2025, -12.9% y/y - likely BELOW annual level"),
    # excluded - no defensible annual figure found:
    #   denver:     HVS/CoStar 2025 pieces are qualitative only ("ADR trending ~2% lower")
    #   neworleans: available prints are event-comp distorted (weekly -18% to -35% y/y)
}


def ols(x, y):
    x = np.asarray(x); y = np.asarray(y)
    X = np.column_stack([np.ones_like(x), x])
    b, res, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ b
    dof = len(x) - 2
    s2 = ((y - yhat) ** 2).sum() / dof if dof > 0 else np.nan
    se = np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1]) if dof > 0 else np.nan
    r2 = 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b[1], se, r2


def main():
    price = pd.read_csv(OUT / "insideairbnb_price_by_accommodates.csv")
    runs = pd.read_csv(OUT / "insideairbnb_booked_run_length_by_segment.csv")
    e4 = price[price.segment == "E4"].set_index("city")["med"]
    allseg = runs[runs.segment == "ALL"].set_index("city")

    rows = []
    for city, (adr, q, src) in HOTEL_ADR.items():
        booked_nights = allseg.loc[city, "runs"] * allseg.loc[city, "mean"]
        util = booked_nights / allseg.loc[city, "listings_active"]
        rel = e4[city] * FEE / adr
        rows.append({"city": city, "abnb_e4_price": e4[city], "hotel_adr": adr, "adr_quality": q,
                     "rel_price": rel, "booked_nights": booked_nights,
                     "active_listings": allseg.loc[city, "listings_active"],
                     "nights_per_listing": util, "adr_source": src})
    df = pd.DataFrame(rows)

    for label, sample in [("incl. DC (n=6)", df), ("excl. DC (n=5)", df[df.city != "washingtondc"])]:
        eps, se, r2 = ols(np.log(sample.rel_price), np.log(sample.nights_per_listing))
        eps = -eps  # report as a positive elasticity of demand w.r.t. relative price
        beta_model = eps / (CONTESTABLE * (1 - P_POOL))   # only contestable demand responds
        beta_bound = eps / (1 - P_POOL)                   # if ALL demand responded (lower bound)
        print(f"{label}: eps = {eps:.2f} (se {se:.2f}, R2 {r2:.2f})  ->  "
              f"beta = {beta_model:.1f} (model mapping) | {beta_bound:.1f} (all-demand bound)")

    print("\n", df.drop(columns=["adr_source"]).round(2).to_string(index=False))
    df.to_csv(OUT / "beta_city_estimate.csv", index=False)
    print("\nwrote", OUT / "beta_city_estimate.csv")


if __name__ == "__main__":
    main()
