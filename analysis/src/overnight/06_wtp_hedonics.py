"""Workstream 06: willingness-to-pay premia on Airbnb, from Inside Airbnb listing dumps.

Reads : data/raw/inside_airbnb/*_listings.parquet  (13 cities, 2022-12 to 2026-08)
Writes: data/processed/overnight/06_wtp_evidence.csv         one row per (basis-era, attribute) premium
        data/processed/overnight/06_price_per_unit_panel.csv per-city-dump price per night /
                                                             per bedroom-night / per person-night
        data/processed/overnight/06_wtp_hedonic_coefs.csv    full OLS coefficient table

Method. Within each price-basis era (`listed_nightly` through Sep 2025 = the host's nightly rate for
the next available night; `quote_per_night` from Mar 2026 = Airbnb's fee-inclusive total for a real
short stay divided by nights), pool dumps and fit
    log(price) ~ room_type + log(accommodates) + bedrooms + superhost + instant_bookable
                 + rating bands + licence disclosed + host-portfolio size + city x dump fixed effects
Price is winsorised at the 1st/99th percentile inside each city-dump and demeaned in logs within
city-dump, so currency (EUR, GBP, AUD, MXN) and level drop out. Reported premium = exp(beta) - 1.

CAVEATS (see research/notes/2026-09-05_inside-airbnb-supply-panel.md on price basis):
- The listed price is an ASKING price for one date, not a realised rate. It is not ADR.
- Cross-era level comparisons are invalid; the 2026 quote basis includes fees, the older basis does not.
- Attributes are not randomly assigned: these are hedonic associations, not causal WTP.
Run: py -3.13 analysis/src/overnight/06_wtp_hedonics.py
"""
import glob
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
OUT = os.path.join(ROOT, "data", "processed", "overnight")
COLS = ["city", "dump_date", "price_basis", "id", "room_type", "accommodates", "bedrooms", "price",
        "host_is_superhost", "instant_bookable", "review_scores_rating", "number_of_reviews",
        "number_of_reviews_ltm", "license", "calculated_host_listings_count", "minimum_nights",
        "estimated_occupancy_l365d", "estimated_revenue_l365d"]
ENTIRE = "Entire home/apt"


def load():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data/raw/inside_airbnb/*_listings.parquet"))):
        d = pd.read_parquet(f)
        d = d[[c for c in COLS if c in d.columns]].copy()
        if "price_basis" not in d.columns:
            d["price_basis"] = "listed_nightly"
        out.append(d)
    d = pd.concat(out, ignore_index=True)
    d["price"] = pd.to_numeric(d["price"].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")
    for c in ("accommodates", "bedrooms", "review_scores_rating", "number_of_reviews",
              "number_of_reviews_ltm", "calculated_host_listings_count", "minimum_nights",
              "estimated_occupancy_l365d", "estimated_revenue_l365d"):
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    for c in ("host_is_superhost", "instant_bookable"):
        d[c] = d[c].astype(str).str.lower().isin(["t", "true", "1"]).astype(int)
    lic = d["license"].astype(str).str.strip().str.lower()
    d["licensed"] = (~lic.isin(["", "nan", "none", "exempt"])).astype(int)
    d = d[d["price"].between(5, 20000) & d["accommodates"].between(1, 16)].copy()
    d["cell"] = d["city"] + "|" + d["dump_date"].astype(str)
    g = d.groupby("cell")["price"]
    lo, hi = g.transform(lambda s: s.quantile(0.01)), g.transform(lambda s: s.quantile(0.99))
    d = d[(d["price"] >= lo) & (d["price"] <= hi)].copy()
    d["lp"] = np.log(d["price"])
    d["bedrooms_f"] = d["bedrooms"].fillna((d["accommodates"].clip(upper=8) / 2).round()).clip(0.5, 8)
    d["price_per_bedroom"] = d["price"] / d["bedrooms_f"].clip(lower=1)
    d["price_per_person"] = d["price"] / d["accommodates"]
    d["rating_band"] = pd.cut(d["review_scores_rating"], [0, 4.5, 4.7, 4.8, 4.9, 5.01],
                              labels=["lt4.5", "4.5-4.7", "4.7-4.8", "4.8-4.9", "ge4.9"])
    d["host_band"] = pd.cut(d["calculated_host_listings_count"], [0, 1, 4, 20, 1e6],
                            labels=["single", "2to4", "5to20", "gt20"])
    d["entire"] = (d["room_type"] == ENTIRE).astype(int)
    d["reviewed_ltm"] = (d["number_of_reviews_ltm"].fillna(0) > 0).astype(int)
    return d


def hedonic(d, era):
    s = d[(d["price_basis"] == era) & d["rating_band"].notna() & d["host_band"].notna()].copy()
    if len(s) < 5000:
        return None
    s["lpd"] = s["lp"] - s.groupby("cell")["lp"].transform("mean")
    s["lacc"] = np.log(s["accommodates"])
    f = ('lpd ~ C(room_type, Treatment("Entire home/apt")) + lacc + bedrooms_f + host_is_superhost'
         ' + instant_bookable + C(rating_band, Treatment("4.7-4.8")) + licensed'
         ' + C(host_band, Treatment("single")) + reviewed_ltm')
    m = smf.ols(f, data=s).fit(cov_type="HC1")
    tab = pd.DataFrame({"term": m.params.index, "coef": m.params.values, "se": m.bse.values,
                        "p": m.pvalues.values})
    tab["premium_pct"] = 100 * (np.exp(tab["coef"]) - 1)
    tab["premium_lo_pct"] = 100 * (np.exp(tab["coef"] - 1.96 * tab["se"]) - 1)
    tab["premium_hi_pct"] = 100 * (np.exp(tab["coef"] + 1.96 * tab["se"]) - 1)
    tab.insert(0, "price_basis", era)
    tab["n"] = len(s)
    tab["r2"] = round(m.rsquared, 4)
    tab["dumps"] = s["cell"].nunique()
    return tab


def raw_cuts(d, era):
    s = d[d["price_basis"] == era].copy()
    if not len(s):
        return []
    s["rel"] = s["lp"] - s.groupby("cell")["lp"].transform("mean")
    rows = []

    def cut(label, ma, mb, na, nb):
        a, b = s[ma], s[mb]
        if len(a) < 500 or len(b) < 500:
            return
        rows.append({"attribute": label, "group_a": na, "group_b": nb, "n_a": len(a), "n_b": len(b),
                     "premium_pct": round(100 * (np.exp(a["rel"].median() - b["rel"].median()) - 1), 2),
                     "median_price_a": round(a["price"].median(), 2),
                     "median_price_b": round(b["price"].median(), 2)})

    cut("room_type", s["room_type"] == ENTIRE, s["room_type"] == "Private room", "entire_home", "private_room")
    cut("superhost", s["host_is_superhost"] == 1, s["host_is_superhost"] == 0, "superhost", "non_superhost")
    cut("instant_book", s["instant_bookable"] == 1, s["instant_bookable"] == 0, "instant_bookable", "not_instant")
    cut("rating", s["review_scores_rating"] >= 4.9, s["review_scores_rating"].between(4.0, 4.79),
        "rating_ge_4.9", "rating_4.0_4.79")
    cut("host_scale", s["calculated_host_listings_count"] > 20, s["calculated_host_listings_count"] <= 1,
        "host_gt20_listings", "single_listing_host")
    cut("licence", s["licensed"] == 1, s["licensed"] == 0, "licence_disclosed", "no_licence")
    cut("min_nights", s["minimum_nights"] >= 7, s["minimum_nights"] <= 2, "min_stay_7plus", "min_stay_1_2")
    return rows


def main():
    d = load()
    print("rows:", len(d), "city-dumps:", d["cell"].nunique(), "\n", d["price_basis"].value_counts().to_dict())
    coefs, ev = [], []
    for era in ("listed_nightly", "quote_per_night"):
        tab = hedonic(d, era)
        if tab is not None:
            coefs.append(tab)
            for _, r in tab.iterrows():
                if r["term"] == "Intercept":
                    continue
                ev.append({"price_basis": era, "kind": "hedonic_ols", "attribute": r["term"],
                           "premium_pct": round(r["premium_pct"], 2), "ci_lo_pct": round(r["premium_lo_pct"], 2),
                           "ci_hi_pct": round(r["premium_hi_pct"], 2), "p_value": round(r["p"], 8),
                           "n_listing_dumps": int(r["n"]), "n_city_dumps": int(r["dumps"]), "r2": r["r2"],
                           "median_price_a": None, "median_price_b": None})
        for r in raw_cuts(d, era):
            ev.append({"price_basis": era, "kind": "median_cut",
                       "attribute": f"{r['attribute']}: {r['group_a']} vs {r['group_b']}",
                       "premium_pct": r["premium_pct"], "ci_lo_pct": None, "ci_hi_pct": None, "p_value": None,
                       "n_listing_dumps": r["n_a"] + r["n_b"], "n_city_dumps": None, "r2": None,
                       "median_price_a": r["median_price_a"], "median_price_b": r["median_price_b"]})
    os.makedirs(OUT, exist_ok=True)
    pd.concat(coefs).to_csv(os.path.join(OUT, "06_wtp_hedonic_coefs.csv"), index=False)
    e = pd.DataFrame(ev)
    e.to_csv(os.path.join(OUT, "06_wtp_evidence.csv"), index=False)

    rows = []
    for (city, dump, basis), s in d.groupby(["city", "dump_date", "price_basis"]):
        eh = s[s["entire"] == 1]
        rows.append({
            "city": city, "dump_date": str(dump), "price_basis": basis, "listings_priced": len(s),
            "median_price": s["price"].median(),
            "median_price_entire": eh["price"].median() if len(eh) else np.nan,
            "median_price_per_bedroom_entire": eh["price_per_bedroom"].median() if len(eh) else np.nan,
            "median_price_per_person_entire": eh["price_per_person"].median() if len(eh) else np.nan,
            "median_price_1br_entire": eh.loc[eh["bedrooms_f"] == 1, "price"].median() if len(eh) else np.nan,
            "median_accommodates_entire": eh["accommodates"].median() if len(eh) else np.nan,
            "mean_accommodates_entire": eh["accommodates"].mean() if len(eh) else np.nan,
            "mean_bedrooms_entire": eh["bedrooms_f"].mean() if len(eh) else np.nan,
            "share_entire": s["entire"].mean(),
            "share_bedrooms_ge4_entire": (eh["bedrooms_f"] >= 4).mean() if len(eh) else np.nan,
            "share_accommodates_ge6": (s["accommodates"] >= 6).mean(),
            "share_superhost": s["host_is_superhost"].mean(),
            "share_instant_book": s["instant_bookable"].mean(),
            "median_min_nights": s["minimum_nights"].median(),
            # Inside Airbnb's estimated_occupancy_l365d is estimated NIGHTS BOOKED in the last 365
            # days (0-365), not a percentage.
            "mean_est_nights_booked_l365d": s["estimated_occupancy_l365d"].mean(),
        })
    pd.DataFrame(rows).round(3).sort_values(["city", "dump_date"]).to_csv(
        os.path.join(OUT, "06_price_per_unit_panel.csv"), index=False)
    print(e[["price_basis", "kind", "attribute", "premium_pct", "ci_lo_pct", "ci_hi_pct", "n_listing_dumps"]].to_string())


if __name__ == "__main__":
    main()
