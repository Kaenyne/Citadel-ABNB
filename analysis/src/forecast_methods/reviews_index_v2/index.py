"""The three y/y constructions per market-month, and their aggregation by ratio of sums (review-share weighting
within a group) and by FY25 nights shares across regions. yoy_vmatch is the primary (WPK-A §4)."""
import numpy as np, pandas as pd
import config as C

MEASURES = {"yoy_all": ("n_reviews", "n_lag12"),
            "yoy_mature": ("n_reviews_mature12", "n_mature12_lag12"),
            "yoy_vmatch": ("n_vm_cur", "n_vm_prior")}


def market_monthly(latest, prior):
    parts = []
    for mkt, g in latest.groupby("market_key"):
        d = g.set_index("ymi")[["n_reviews", "n_reviews_mature12"]].sort_index()
        full = d.reindex(range(int(d.index.min()), int(d.index.max()) + 1))
        out = pd.DataFrame({"n_reviews": full.n_reviews, "n_lag12": full.n_reviews.shift(12),
                            "n_reviews_mature12": full.n_reviews_mature12,
                            "n_mature12_lag12": full.n_reviews_mature12.shift(12)})
        p = prior[prior.market_key == mkt].set_index("ymi").n_reviews
        out["n_vm_cur"] = full.n_reviews
        out["n_vm_prior"] = [p.get(m - 12, np.nan) for m in full.index]
        out = out.dropna(subset=["n_reviews"]); out.index.name = "ymi"
        out = out.reset_index(); out.insert(0, "market_key", mkt); parts.append(out)
    my = pd.concat(parts, ignore_index=True)
    geo = latest[["market_key", "country", "region"]].drop_duplicates()
    return my.merge(geo, on="market_key", how="left")


def ratio_of_sums(df, by, measure):
    num, den = MEASURES[measure]
    g = df.dropna(subset=[num, den]).groupby(by)[[num, den]].sum()
    g = g[g[den] > 0]
    return (g[num] / g[den] - 1).rename(measure), g


def country_monthly(my, measure):
    s, _ = ratio_of_sums(my, ["country", "ymi"], measure)
    return s.reset_index()


def global_quarterly(my, measure, min_weight=0.5):
    """Quarter = ratio of the 3 monthly sums (markets must have all 3 months); region by review share; global
    by FY25 nights shares over the regions present (at least min_weight of the nights weight)."""
    d = my.copy(); d["qi"] = d.ymi // 3
    cnt = d.groupby(["market_key", "qi"]).ymi.transform("count"); d = d[cnt == 3]
    reg, _ = ratio_of_sums(d, ["region", "qi"], measure)
    reg = reg.reset_index().pivot(index="qi", columns="region", values=measure)
    w = pd.Series(C.FY25_NIGHTS_SHARE).reindex(reg.columns).fillna(0)
    ok = reg.notna()
    wsum = (ok * w).sum(axis=1)
    glob = (reg.fillna(0) * w).sum(axis=1) / wsum
    glob[wsum < min_weight * w.sum()] = np.nan
    return glob.rename(measure), reg
