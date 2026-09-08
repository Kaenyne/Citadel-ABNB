"""
Is party size diverging across cities? 122 markets, 36 countries, 2015-2025.

The model applies ONE global mix-drift vector (MIX_DRIFT_ABNB, implying +0.62%/yr) everywhere.
Krish's review-text panel has per-market quarterly composition for 123 Inside Airbnb markets, so
that assumption can be tested city by city rather than argued about. No new data pull needed.

Method: per market, weighted-average implied party size per year (solo 1 / couple 2 / family 3.9 /
group 4.7, the same weights as the global series), markets with >=400 stated compositions a year
and >=8 usable years, then a log-linear trend per market with its own t-stat.

RESULT - the trend is real in North America and absent everywhere else:

    region          n    mean    median   % significant (t>2)   % positive
    north_america  42   +0.66%   +0.71%          52%               81%
    emea           57   -0.01%   +0.02%          12%               51%
    latam           7   +0.26%   +0.17%          14%               57%
    apac           16   -0.19%   -0.10%          19%               38%
    ALL           122   +0.21%   +0.12%          27%               60%

Two things follow, and they pull in opposite directions for the model:

1. THE U.S. MODEL IS FINE. MIX_DRIFT_ABNB implies +0.62%/yr; North America's 42 markets average
   +0.66%/yr with 52% individually significant and 81% positive. That is close agreement from an
   independent cut of the data, and it means the global "+0.62%" was really a North America number.

2. APPLYING IT OUTSIDE NORTH AMERICA IS WRONG. EMEA is flat (-0.01%, only 12% of markets
   significant), which independently CORROBORATES the Spain INE microdata finding that the
   rental/hotel ratio there is flat over 11 years - two different instruments, same answer. APAC is
   flat to slightly negative. So the regional model should NOT carry a North American mix drift
   into EMEA or APAC, and does not: its regional CATEGORY paths are fitted per region.

Dispersion is the other headline: sd 0.73%/yr across markets, from Salem OR at +3.8%/yr to
Singapore at -2.8%/yr. "Party sizes are rising" is not a global fact; it is a North American one
with wide within-region variation. Anglo markets lead (US +0.67, Canada +0.60, UK +0.52) while
continental Europe is flat to negative (Italy -0.08, France -0.05, Switzerland -0.27).

CAVEATS: the review-text proxy measures composition among reviews that STATE composition (~6% of
reviews), so it inherits that selection; it is validated for DIRECTION against Hawaii DBEDT at
r 0.96-0.99 but its LEVEL is biased high. Market coverage is Inside Airbnb's, which skews to large
Western cities - hence only 7 LatAm and 16 APAC markets against 57 EMEA.

Run:  python analysis/src/party_size_divergence_by_city.py
Out:  data/processed/party_size_trend_by_market.csv
"""
import glob
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

W = {"cond_solo": 1.0, "cond_couple": 2.0, "cond_family": 3.9, "cond_group": 4.7}
MIN_REVIEWS, MIN_YEARS = 400, 8
NA = {"united-states", "canada"}
LATAM = {"mexico", "brazil", "argentina", "chile", "colombia", "peru", "uruguay", "belize",
         "costa-rica", "panama", "ecuador"}
APAC = {"australia", "japan", "china", "hong-kong", "singapore", "thailand", "new-zealand",
        "taiwan", "south-korea", "malaysia", "indonesia", "india", "vietnam"}


def region_of(c):
    if c in NA:
        return "north_america"
    if c in LATAM:
        return "latam"
    if c in APAC:
        return "apac"
    return "emea"


def main():
    files = sorted(glob.glob(str(OUT / "abnb_party_size_reviews_market_quarter_shard*.csv")))
    if not files:
        raise SystemExit("per-market shards not found - see Krish's party-size series (PR #33)")
    d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    d["year"] = d.q.str[:4].astype(int)
    d["implied"] = sum(d[k] * W[k] for k in W)
    d["country"] = d.market.str.split("_").str[0]
    d["region"] = d.country.map(region_of)

    a = (d[(d.year >= 2015) & (d.year <= 2025)]
         .groupby(["market", "region", "country", "year"])
         .apply(lambda x: pd.Series({"implied": np.average(x.implied, weights=x.reviews),
                                     "reviews": x.reviews.sum()}), include_groups=False)
         .reset_index())
    a = a[a.reviews >= MIN_REVIEWS]

    rows = []
    for m, g in a.groupby("market"):
        if len(g) < MIN_YEARS:
            continue
        x = g.year.values.astype(float)
        y = np.log(g.implied.values)
        b = np.polyfit(x, y, 1)
        resid = y - np.polyval(b, x)
        se = np.sqrt((resid ** 2).sum() / (len(x) - 2) / ((x - x.mean()) ** 2).sum())
        rows.append({"market": m, "region": g.region.iloc[0], "country": g.country.iloc[0],
                     "trend_pct_yr": b[0] * 100, "t": b[0] / se if se > 0 else np.nan,
                     "years": len(g)})
    r = pd.DataFrame(rows)

    print(f"PARTY-SIZE TREND BY MARKET, {len(r)} markets / {r.country.nunique()} countries, 2015-2025\n")
    print(f"{'region':14s} {'n':>4s} {'mean':>7s} {'median':>7s} {'sig(t>2)':>9s} {'positive':>9s}")
    for reg, g in r.groupby("region"):
        print(f"{reg:14s} {len(g):4d} {g.trend_pct_yr.mean():+6.2f}% {g.trend_pct_yr.median():+6.2f}% "
              f"{(g.t > 2).mean() * 100:8.0f}% {(g.trend_pct_yr > 0).mean() * 100:8.0f}%")
    print(f"{'ALL':14s} {len(r):4d} {r.trend_pct_yr.mean():+6.2f}% {r.trend_pct_yr.median():+6.2f}% "
          f"{(r.t > 2).mean() * 100:8.0f}% {(r.trend_pct_yr > 0).mean() * 100:8.0f}%")
    print(f"\ndispersion: sd {r.trend_pct_yr.std():.2f}%/yr, "
          f"range {r.trend_pct_yr.min():+.2f}% to {r.trend_pct_yr.max():+.2f}%")

    print("\nfastest RISING / FALLING:")
    for lbl, sub in [("rising", r.nlargest(4, "trend_pct_yr")), ("falling", r.nsmallest(4, "trend_pct_yr"))]:
        for _, x in sub.iterrows():
            print(f"  {lbl:8s} {x.market.split('_')[-2][:28]:30s} {x.trend_pct_yr:+6.2f}%/yr  t={x.t:+.1f}")

    print("\nVERDICT: the model's global +0.62%/yr matches NORTH AMERICA (+0.66%) and only")
    print("North America. EMEA is flat, which independently corroborates Spain's INE microdata.")
    r.round(4).to_csv(OUT / "party_size_trend_by_market.csv", index=False)
    print("\nwrote", OUT / "party_size_trend_by_market.csv")


if __name__ == "__main__":
    main()
