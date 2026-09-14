"""ADR v3, workstream M, step 3: new-listing share of stays per quarter, by market, region and global.

Share = reviews written in the quarter by listings whose first review (in the same dump) is under 12
months before the review month, over all reviews in the quarter. Reviews stand in for stays (E method).

Source A (primary, 123 markets): workstream E's market x dump x month counts,
  data/processed/q3nowcast/E_aug/market_vintage_monthly.csv (n_reviews, n_reviews_mature12).
  Construction per quarter: the dump with the smallest lag whose months all precede the dump month.
    lag <= 13 months on both the quarter and its year-ago quarter  -> "vintage_matched"
    lag <= 13 on the quarter, deeper on the year-ago quarter       -> "mixed_lag"
    both deeper than 13 months (one dump, 2025-08/09)               -> "within_vintage_deep"
  The attrition wedge on the share is measured on the quarters seen at both lags (3Q24-2Q25 in the
  2025-08 and the 2026-08 dumps) and reported; a wedge-corrected variant of the deep series is written.
  3Q26 to date = July 2026 from the August 2026 dumps (the dump month is truncated), against July 2025
  from the August 2025 dumps.
Source B (cross-check, 34 markets): the listings dumps' number_of_reviews_l30d split by first_review
  age at the dump date (lag 0 by construction), from the M1 cache. Scope-flagged.

Regional aggregation: review-weighted and equal-weighted; global on FY25 10-K nights shares used in
I3 (NA 31.4, EMEA 36.8, LatAm 17.0, APAC 14.9), regional review-weighted shares. Region codes NAM,
EMEA, LatAm, APAC (NAM, not NA, because pandas reads the string NA as missing).

Run: py -3.13 analysis/src/adrv3/M3_new_listing_share.py
Outputs: data/processed/adrv3/M/M3_new_listing_share.csv (market rows), M3_new_listing_share_region.csv,
         M3_attrition_wedge.csv, M3_listings_dump_share.csv (source B)
"""
import glob
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
E_AUG = os.path.join(ROOT, "data", "processed", "q3nowcast", "E_aug")
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "M")
CACHE = os.path.join(OUT, "cache")
WEIGHTS = {"NAM": 31.4, "EMEA": 36.8, "LatAm": 17.0, "APAC": 14.9}  # FY25 10-K nights shares, as I3 (sourced)
MAX_LAG = 13  # months from the last month of the quarter to the dump month


def qlabel_from_ymi(ymi: int) -> str:
    y, m = ymi // 12, ymi % 12 + 1
    return f"{(m - 1) // 3 + 1}Q{str(y)[2:]}"


def qorder(q: str) -> int:
    return (2000 + int(q[-2:])) * 4 + int(q[0]) - 1


def q_shift(q: str, k: int) -> str:
    o = qorder(q) + k
    return f"{o % 4 + 1}Q{str(o // 4)[2:]}"


def source_a() -> tuple[pd.DataFrame, pd.DataFrame]:
    mv = pd.read_csv(os.path.join(E_AUG, "market_vintage_monthly.csv"), keep_default_na=False, na_values=[""])
    geo = pd.read_csv(os.path.join(E_AUG, "market_geo.csv"), keep_default_na=False, na_values=[""])
    reg = dict(zip(geo.market_key, geo.region))
    mv["dump_ymi"] = pd.to_datetime(mv.dump_date).dt.year * 12 + pd.to_datetime(mv.dump_date).dt.month - 1
    mv = mv[mv.ymi < mv.dump_ymi].copy()  # drop the truncated dump month
    mv["quarter"] = mv.ymi.map(qlabel_from_ymi)
    mv["n_new"] = mv.n_reviews - mv.n_reviews_mature12
    # quarter x dump: full quarters only, except 3Q26 to date (July 2026)
    g = mv.groupby(["market_key", "dump_date", "dump_ymi", "quarter"]).agg(
        n_reviews=("n_reviews", "sum"), n_new=("n_new", "sum"), months=("ymi", "count"), last_ymi=("ymi", "max")).reset_index()
    g["to_date"] = (g.quarter == "3Q26") & (g.months < 3)
    g = g[(g.months == 3) | g.to_date].copy()
    g["lag_months"] = g.dump_ymi - g.last_ymi
    g["share_new"] = g.n_new / g.n_reviews
    g["region"] = g.market_key.map(reg)
    # the 3Q26-to-date comparator is July 2025 from the 2025 dumps, one month only
    jul25 = mv[(mv.ymi == 2025 * 12 + 6) & (mv.dump_date < "2026-01-01")].groupby(["market_key", "dump_date", "dump_ymi"]).agg(
        n_reviews=("n_reviews", "sum"), n_new=("n_new", "sum")).reset_index()
    jul25["quarter"] = "3Q25_jul"
    jul25["lag_months"] = jul25.dump_ymi - (2025 * 12 + 6)
    jul25["share_new"] = jul25.n_new / jul25.n_reviews
    jul25["region"] = jul25.market_key.map(reg)
    jul25["months"] = 1
    jul25["to_date"] = True
    g = pd.concat([g, jul25], ignore_index=True)
    # attrition wedge: same market-quarter in two dumps ~12 months apart
    both = g[(g.quarter != "3Q25_jul") & (~g.to_date)].merge(
        g[(g.quarter != "3Q25_jul") & (~g.to_date)], on=["market_key", "quarter", "region"], suffixes=("_early", "_late"))
    both = both[(both.dump_ymi_late - both.dump_ymi_early).between(10, 14) & (both.lag_months_early <= MAX_LAG)]
    both["wedge_pp"] = 100 * (both.share_new_late - both.share_new_early)
    # nearest-lag pick per market-quarter
    g = g.sort_values(["market_key", "quarter", "lag_months"])
    pick = g.groupby(["market_key", "quarter"]).head(1).copy()
    pick = pick.set_index(["market_key", "quarter"])
    rows = []
    wedge_reg = both.groupby("region").apply(
        lambda d: 100 * (d.n_new_late.sum() / d.n_reviews_late.sum() - d.n_new_early.sum() / d.n_reviews_early.sum())).to_dict()
    for (mk, q), r in pick.iterrows():
        if q == "3Q25_jul":
            continue
        qa = "3Q25_jul" if q == "3Q26" else q_shift(q, -4)
        if (mk, qa) not in pick.index:
            continue
        ra = pick.loc[(mk, qa)]
        lag_c, lag_a = r.lag_months, ra.lag_months
        if lag_c <= MAX_LAG and lag_a <= MAX_LAG:
            flag = "vintage_matched"
        elif lag_c <= MAX_LAG:
            flag = "mixed_lag"
        else:
            flag = "within_vintage_deep"
        w = wedge_reg.get(r.region, 0.0)
        # wedge correction: a share observed at lag > 13 months is raised by the regional wedge (assumed constant in depth)
        cur_c = r.share_new * 100 - (w if lag_c > MAX_LAG else 0.0)
        prev_c = ra.share_new * 100 - (w if lag_a > MAX_LAG else 0.0)
        rows.append(dict(market_key=mk, region=r.region, quarter=q, construction=flag,
                         dump_cur=r.dump_date, lag_cur=int(lag_c), dump_prev=ra.dump_date, lag_prev=int(lag_a),
                         n_reviews_cur=int(r.n_reviews), n_new_cur=int(r.n_new), n_reviews_prev=int(ra.n_reviews), n_new_prev=int(ra.n_new),
                         share_new_cur_pct=round(100 * r.share_new, 3), share_new_prev_pct=round(100 * ra.share_new, 3),
                         d_share_pp=round(100 * (r.share_new - ra.share_new), 3),
                         d_share_wedge_corrected_pp=round(cur_c - prev_c, 3),
                         to_date=bool(r.to_date), months_cur=int(r.months)))
    m = pd.DataFrame(rows)
    return m, both


def source_b() -> pd.DataFrame:
    cen = pd.read_csv(os.path.join(OUT, "M1_dump_census.csv"), keep_default_na=False, na_values=[""])
    cen = cen[cen.source_format != "error"]
    rows = []
    for _, r in cen.iterrows():
        rows.append(dict(market=r.market, region=("NAM" if r.region == "NA" else r.region), dump_date=r.dump_date, quarter=r.quarter,
                         scope_flag=r.scope_flag, n_listings=r.n_listings,
                         share_l30d_reviews_from_new_pct=100 * float(r.share_l30d_reviews_from_new) if r.share_l30d_reviews_from_new != "" else np.nan,
                         share_ltm_reviews_from_new_pct=100 * float(r.share_ltm_reviews_from_new) if r.share_ltm_reviews_from_new != "" else np.nan,
                         share_listings_new_pct=100 * float(r.share_listings_new_by_first_review)))
    b = pd.DataFrame(rows).sort_values(["market", "dump_date"])
    # y/y change on full-scope vintages nearest to 12 months apart
    out = []
    for mk, d in b.groupby("market"):
        d = d.reset_index(drop=True)
        for i, r in d.iterrows():
            cand = d[(pd.to_datetime(d.dump_date) - pd.Timestamp(r.dump_date)).dt.days.between(-400, -330)]
            if cand.empty:
                out.append(dict(**r, d_share_l30d_pp=np.nan, prev_dump=""))
                continue
            p = cand.iloc[(pd.to_datetime(cand.dump_date) - (pd.Timestamp(r.dump_date) - pd.Timedelta(days=365))).abs().argsort().iloc[0]]
            out.append(dict(**r, d_share_l30d_pp=r.share_l30d_reviews_from_new_pct - p.share_l30d_reviews_from_new_pct, prev_dump=p.dump_date))
    return pd.DataFrame(out)


def aggregate(m: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (q, reg), d in m.groupby(["quarter", "region"]):
        for cons, dd in [("all", d), ("vintage_matched_only", d[d.construction == "vintage_matched"])]:
            if dd.empty:
                continue
            rows.append(dict(quarter=q, region=reg, subset=cons, n_markets=len(dd),
                             construction=";".join(sorted(dd.construction.unique())),
                             share_new_cur_rw_pct=100 * dd.n_new_cur.sum() / dd.n_reviews_cur.sum(),
                             share_new_prev_rw_pct=100 * dd.n_new_prev.sum() / dd.n_reviews_prev.sum(),
                             d_share_rw_pp=100 * (dd.n_new_cur.sum() / dd.n_reviews_cur.sum() - dd.n_new_prev.sum() / dd.n_reviews_prev.sum()),
                             d_share_eq_pp=dd.d_share_pp.mean(), d_share_median_pp=dd.d_share_pp.median(),
                             d_share_wedge_corrected_rw_pp=np.average(dd.d_share_wedge_corrected_pp, weights=dd.n_reviews_cur),
                             reviews_cur=int(dd.n_reviews_cur.sum()), to_date=bool(dd.to_date.any())))
    a = pd.DataFrame(rows)
    glob_rows = []
    for (q, sub), d in a.groupby(["quarter", "subset"]):
        d = d.set_index("region")
        regs = [r for r in WEIGHTS if r in d.index]
        w = np.array([WEIGHTS[r] for r in regs]); w = w / w.sum()
        glob_rows.append(dict(quarter=q, region="GLOBAL_NW", subset=sub, n_markets=int(d.n_markets.sum()),
                              construction=";".join(sorted(set(";".join(d.construction).split(";")))),
                              share_new_cur_rw_pct=float(np.dot(w, d.loc[regs, "share_new_cur_rw_pct"])),
                              share_new_prev_rw_pct=float(np.dot(w, d.loc[regs, "share_new_prev_rw_pct"])),
                              d_share_rw_pp=float(np.dot(w, d.loc[regs, "d_share_rw_pp"])),
                              d_share_eq_pp=float(np.dot(w, d.loc[regs, "d_share_eq_pp"])),
                              d_share_median_pp=float(np.dot(w, d.loc[regs, "d_share_median_pp"])),
                              d_share_wedge_corrected_rw_pp=float(np.dot(w, d.loc[regs, "d_share_wedge_corrected_rw_pp"])),
                              reviews_cur=int(d.reviews_cur.sum()), to_date=bool(d.to_date.any()), regions_covered=len(regs)))
    a = pd.concat([a, pd.DataFrame(glob_rows)], ignore_index=True)
    a["qo"] = a.quarter.map(qorder)
    a = a.sort_values(["subset", "region", "qo"]).drop(columns="qo")
    return a


def main():
    m, both = source_a()
    m["qo"] = m.quarter.map(qorder)
    m = m[m.qo >= qorder("1Q23")].sort_values(["market_key", "qo"]).drop(columns="qo")
    m.to_csv(os.path.join(OUT, "M3_new_listing_share.csv"), index=False, encoding="utf-8")
    wr = both.groupby("region").agg(n_pairs=("wedge_pp", "size"), wedge_eq_pp=("wedge_pp", "mean"), wedge_median_pp=("wedge_pp", "median"),
                                   n_new_early=("n_new_early", "sum"), n_reviews_early=("n_reviews_early", "sum"),
                                   n_new_late=("n_new_late", "sum"), n_reviews_late=("n_reviews_late", "sum")).reset_index()
    wr["wedge_rw_pp"] = 100 * (wr.n_new_late / wr.n_reviews_late - wr.n_new_early / wr.n_reviews_early)
    wq = both.groupby(["region", "quarter"]).agg(n_pairs=("wedge_pp", "size"), wedge_eq_pp=("wedge_pp", "mean")).reset_index()
    pd.concat([wr.assign(quarter="all"), wq], ignore_index=True).to_csv(os.path.join(OUT, "M3_attrition_wedge.csv"), index=False)
    a = aggregate(m)
    a.to_csv(os.path.join(OUT, "M3_new_listing_share_region.csv"), index=False, encoding="utf-8")
    b = source_b()
    b.to_csv(os.path.join(OUT, "M3_listings_dump_share.csv"), index=False, encoding="utf-8")
    pd.set_option("display.width", 250)
    print("attrition wedge on the new-listing share (late dump minus early dump, same quarter), pp:")
    print(wr.round(2).to_string(index=False))
    print("\nregional and global new-listing share, review-weighted, all constructions:")
    print(a[a.subset == "all"].pivot(index="quarter", columns="region", values="share_new_cur_rw_pct").round(1)
          .loc[sorted(a.quarter.unique(), key=qorder)].to_string())
    print("\ny/y change in share, pp:")
    print(a[a.subset == "all"].pivot(index="quarter", columns="region", values="d_share_rw_pp").round(2)
          .loc[sorted(a.quarter.unique(), key=qorder)].to_string())
    print("\nconstruction by quarter (global):")
    print(a[(a.subset == "all") & (a.region == "GLOBAL_NW")][["quarter", "n_markets", "construction", "share_new_cur_rw_pct", "d_share_rw_pp", "d_share_wedge_corrected_rw_pp"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
