"""
Q3 2026 nowcast, workstream E, step 4b: stable-listing (same-store) y/y where a market has two dump
vintages about 12 months apart.

For each market with a latest dump L (Jun-Aug 2026) and an older dump O 300 to 430 days earlier
(Aug-Sep 2025), S = listings with at least one review in BOTH dumps. Then
  yoy_stable[m] = sum_{S} n_L[m] / sum_{S} n_O[m-12] - 1
Both sides are the identical listing set, each read from a dump the same distance from the month,
so neither survivorship nor posting lag can bias the ratio. The price is that listings born after
O are excluded (the series is biased DOWN relative to total demand by new-supply growth) and that
the set S is itself a survivor set for months long before O.

Reads  data/processed/q3nowcast/E/cache/<market>_<vintage>_listing_month.parquet (from E3)
       data/processed/q3nowcast/E/market_geo.csv (from E4)
Writes data/processed/q3nowcast/E/
  stable_listing_yoy_market.csv   market x month: stable counts, yoy_stable, coverage of the late dump
  stable_listing_index.csv        region and global monthly, three weightings
  index_quarterly.csv             APPENDS measure = yoy_stable rows (run after E4, before E5)

Run: py -3.13 analysis/src/q3nowcast/E4b_stable_listing.py
"""
import time
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
OUT = WT / "data/processed/q3nowcast/E"
CACHE = OUT / "cache"
FY25_NIGHTS_SHARE = {"NAM": 28.3, "EMEA": 41.6, "LatAm": 17.9, "APAC": 12.3}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def ymi_to_ym(i):
    return f"{i // 12}-{i % 12 + 1:02d}"


def pairs():
    mv = pd.read_csv(OUT / "market_vintage_monthly.csv")[["market_key", "dump_date"]].drop_duplicates()
    out = []
    for mkt, g in mv.groupby("market_key"):
        vs = sorted(g.dump_date.unique())
        late = vs[-1]
        olds = [v for v in vs if 300 <= (pd.Timestamp(late) - pd.Timestamp(v)).days <= 430]
        if olds:
            out.append((mkt, olds[-1], late))
    return out


def one(mkt, old, late):
    po = CACHE / f"{mkt}_{old}_listing_month.parquet"
    pl = CACHE / f"{mkt}_{late}_listing_month.parquet"
    if not (po.exists() and pl.exists()):
        return None
    o, l = pd.read_parquet(po), pd.read_parquet(pl)
    S = np.intersect1d(o.listing_id.unique(), l.listing_id.unique())
    os_, ls_ = o[o.listing_id.isin(S)], l[l.listing_id.isin(S)]
    no = os_.groupby("ymi").n.sum()
    nl = ls_.groupby("ymi").n.sum()
    nl_all = l.groupby("ymi").n.sum()
    od, ld = pd.Timestamp(old), pd.Timestamp(late)
    o_ymi, l_ymi = od.year * 12 + od.month - 1, ld.year * 12 + ld.month - 1
    rows = []
    for m in nl.index:
        if m >= l_ymi or (m - 12) >= o_ymi or (m - 12) not in no.index or no[m - 12] <= 0:
            continue
        rows.append(dict(market_key=mkt, vintage_old=old, vintage_late=late, ymi=int(m),
                         n_stable_cur=int(nl[m]), n_stable_prior=int(no[m - 12]),
                         yoy_stable=nl[m] / no[m - 12] - 1,
                         stable_share_of_late_reviews=nl[m] / nl_all[m] if nl_all.get(m, 0) else np.nan,
                         n_stable_listings=int(len(S))))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    prs = pairs()
    log(f"{len(prs)} markets with a year-ago vintage")
    parts = [x for x in (one(*p) for p in prs) if x is not None and len(x)]
    m = pd.concat(parts, ignore_index=True)
    geo = pd.read_csv(OUT / "market_geo.csv")
    m = m.merge(geo[["market_key", "region"]], on="market_key", how="left")
    m["ym"] = m.ymi.map(ymi_to_ym)
    m.to_csv(OUT / "stable_listing_yoy_market.csv", index=False, encoding="utf-8")
    log(f"stable_listing_yoy_market.csv {len(m)} rows, {m.market_key.nunique()} markets, "
        f"months {m.ym.min()}..{m.ym.max()}")

    # monthly aggregates
    rows = []
    for (ymi, reg), g in list(m.groupby(["ymi", "region"])) + [((y, "GLOBAL"), gg) for y, gg in m.groupby("ymi")]:
        rows.append(dict(ymi=ymi, ym=ymi_to_ym(ymi), region=reg, measure="yoy_stable", n_markets=len(g),
                         w_equal=g.yoy_stable.mean(),
                         w_reviews=g.n_stable_cur.sum() / g.n_stable_prior.sum() - 1,
                         w_median=g.yoy_stable.median(),
                         reviews=g.n_stable_cur.sum(), reviews_lag12=g.n_stable_prior.sum()))
    a = pd.DataFrame(rows)
    nw = []
    for ymi, g in a[a.region.isin(FY25_NIGHTS_SHARE)].groupby("ymi"):
        ws = [FY25_NIGHTS_SHARE[r] for r in g.region]
        nw.append(dict(ymi=ymi, ym=ymi_to_ym(ymi), region="GLOBAL_NW", measure="yoy_stable",
                       n_markets=int(g.n_markets.sum()), w_equal=np.average(g.w_equal, weights=ws),
                       regions_weight_covered=sum(ws)))
    a = pd.concat([a, pd.DataFrame(nw)], ignore_index=True)
    a.to_csv(OUT / "stable_listing_index.csv", index=False, encoding="utf-8")
    log(f"stable_listing_index.csv {len(a)} rows")

    # quarterly, appended to index_quarterly.csv as measure yoy_stable (only full 3-month quarters)
    m["year"], m["q"] = m.ymi // 12, (m.ymi % 12) // 3 + 1
    cnt = m.groupby(["market_key", "year", "q"]).ymi.size().rename("nm")
    s = m.groupby(["market_key", "region", "year", "q"])[["n_stable_cur", "n_stable_prior"]].sum().join(cnt)
    s = s[s.nm == 3].reset_index()
    qrows = []
    for (y, q), g in s.groupby(["year", "q"]):
        for reg_name, gg in list(g.groupby("region")) + [("GLOBAL", g)]:
            yy = gg.n_stable_cur / gg.n_stable_prior - 1
            qrows.append(dict(year=y, q=q, quarter=f"{q}Q{str(y)[2:]}", region=reg_name, measure="yoy_stable",
                              n_markets=len(gg), w_equal=yy.mean(),
                              w_reviews=gg.n_stable_cur.sum() / gg.n_stable_prior.sum() - 1,
                              w_median=yy.median(), reviews=gg.n_stable_cur.sum(),
                              reviews_lag12=gg.n_stable_prior.sum()))
    qq = pd.DataFrame(qrows)
    nwq = []
    for (y, q), g in qq[qq.region.isin(FY25_NIGHTS_SHARE)].groupby(["year", "q"]):
        ws = [FY25_NIGHTS_SHARE[r] for r in g.region]
        nwq.append(dict(year=y, q=q, quarter=f"{q}Q{str(y)[2:]}", region="GLOBAL_NW", measure="yoy_stable",
                        n_markets=np.nan, w_equal=np.average(g.w_equal, weights=ws),
                        regions_weight_covered=sum(ws)))
    qq = pd.concat([qq, pd.DataFrame(nwq)], ignore_index=True)
    iq = pd.read_csv(OUT / "index_quarterly.csv")
    iq = pd.concat([iq[iq.measure != "yoy_stable"], qq], ignore_index=True)
    iq.to_csv(OUT / "index_quarterly.csv", index=False, encoding="utf-8")
    log(f"index_quarterly.csv now {len(iq)} rows incl {len(qq)} yoy_stable rows")
    g = qq[qq.region == "GLOBAL"].sort_values(["year", "q"]).tail(14)
    print(g[["quarter", "n_markets", "w_equal", "w_reviews", "w_median"]].to_string(index=False))

