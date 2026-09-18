"""
Q3 2026 nowcast, workstream E, steps 3b and 4: build the stays-based demand index from the monthly
review counts, handling survivorship explicitly, then aggregate to region and global.

Reads  data/processed/q3nowcast/E/market_vintage_monthly.csv (from E3)
       data/processed/q3nowcast/E/market_vintage_daily.csv   (from E3)

Writes data/processed/q3nowcast/E/
  market_geo.csv                market -> country, Airbnb region
  survivorship_wedge.csv        same month measured in two vintages: attrition of review history
  posting_lag_curve.csv         same month measured in two vintages: how much of a month is posted yet
  market_monthly_yoy.csv        per market and vintage: monthly y/y, three constructions
  region_monthly_index.csv      region monthly y/y under three weightings
  global_monthly_index.csv      global monthly y/y under three weightings
  index_quarterly.csv           calendar-quarter y/y, region and global, three weightings
  coverage_monthly.csv          markets and review share behind each month

Three y/y constructions, all within a single dump vintage unless stated:
  yoy_all      n_reviews[m] / n_reviews[m-12] - 1            (primary, upward biased by survivorship)
  yoy_mature   n_mature12[m] / n_mature12[m-12] - 1          (both sides 12m+ old listings)
  yoy_cohort   n_mature24[m] / n_mature12[m-12] - 1          (identical listing set on both sides:
                                                              first review on or before m-24)
  yoy_vmatch   n[m] in the 2026 vintage / n[m-12] in a vintage ~12 months earlier
                                                             (vintage-matched, removes the wedge)

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC-BY 4.0.
Regional nights weights (region code NAM, not NA, because pandas reads "NA" as missing): Airbnb FY25 regional nights shares NAM 28.3, EMEA 41.6, LatAm 17.9, APAC 12.3
(main tree ADR decomposition note).
Run: py -3.13 analysis/src/q3nowcast/E4_build_index.py
"""
import time
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
OUT = WT / "data/processed/q3nowcast/E"

REGION_OF_COUNTRY = {
    "united-states": "NAM", "canada": "NAM",
    "argentina": "LatAm", "belize": "LatAm", "brazil": "LatAm", "chile": "LatAm",
    "colombia": "LatAm", "mexico": "LatAm",
    "australia": "APAC", "china": "APAC", "japan": "APAC", "new-zealand": "APAC",
    "singapore": "APAC", "taiwan": "APAC", "thailand": "APAC",
}
FY25_NIGHTS_SHARE = {"NAM": 28.3, "EMEA": 41.6, "LatAm": 17.9, "APAC": 12.3}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def ymi_to_ym(i):
    return f"{i // 12}-{i % 12 + 1:02d}"


def load():
    mv = pd.read_csv(OUT / "market_vintage_monthly.csv")
    mv["country"] = mv.market_key.str.split("_").str[0]
    mv["region"] = mv.country.map(REGION_OF_COUNTRY).fillna("EMEA")
    return mv


# ------------------------------------------------------------------ survivorship and posting lag
def wedges(mv):
    """Same market, same review month, two vintages. Early vs late dump."""
    rows = []
    for mkt, g in mv.groupby("market_key"):
        vs = sorted(g.dump_date.unique())
        if len(vs) < 2:
            continue
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                a, b = g[g.dump_date == vs[i]], g[g.dump_date == vs[j]]
                m = a.merge(b, on="ymi", suffixes=("_early", "_late"))
                if m.empty:
                    continue
                gap_d = (pd.Timestamp(vs[j]) - pd.Timestamp(vs[i])).days
                m = m.assign(market_key=mkt, vintage_early=vs[i], vintage_late=vs[j], gap_days=gap_d)
                # months from the END of the review month to the EARLY dump date
                end_early = pd.Timestamp(vs[i])
                m["months_before_early_dump"] = ((end_early.year * 12 + end_early.month - 1) - m.ymi)
                m["ratio_late_over_early"] = m.n_reviews_late / m.n_reviews_early.replace(0, np.nan)
                rows.append(m[["market_key", "vintage_early", "vintage_late", "gap_days", "ymi",
                               "months_before_early_dump", "n_reviews_early", "n_reviews_late",
                               "ratio_late_over_early"]])
    if not rows:
        log("no market has two vintages: survivorship wedge not measurable yet")
        cols = ["market_key", "vintage_early", "vintage_late", "gap_days", "ymi",
                "months_before_early_dump", "n_reviews_early", "n_reviews_late",
                "ratio_late_over_early", "ym"]
        w = pd.DataFrame(columns=cols)
        w.to_csv(OUT / "survivorship_wedge.csv", index=False, encoding="utf-8")
        pd.DataFrame().to_csv(OUT / "posting_lag_curve.csv", index=False, encoding="utf-8")
        return w
    w = pd.concat(rows, ignore_index=True)
    w["ym"] = w.ymi.map(ymi_to_ym)
    w.to_csv(OUT / "survivorship_wedge.csv", index=False, encoding="utf-8")
    log(f"survivorship_wedge.csv {len(w)} rows, {w.market_key.nunique()} markets")

    # posting-lag / truncation curve: months that were recent at the early dump, ratio > 1 means the
    # early dump had not yet seen the reviews. Attrition pushes the ratio the other way, so the two
    # are only separable by looking at the shape against months_before_early_dump.
    cur = w[w.months_before_early_dump.between(-1, 8)]
    lag = (cur.groupby(["gap_days", "months_before_early_dump"])
              .agg(n_pairs=("market_key", "size"),
                   median_ratio=("ratio_late_over_early", "median"),
                   mean_ratio=("ratio_late_over_early", "mean"),
                   pooled_ratio=("n_reviews_late", "sum"))
              .reset_index())
    den = (cur.groupby(["gap_days", "months_before_early_dump"]).n_reviews_early.sum()
              .reset_index(name="den"))
    lag = lag.merge(den, on=["gap_days", "months_before_early_dump"])
    lag["pooled_ratio"] = lag.pooled_ratio / lag.den
    lag.to_csv(OUT / "posting_lag_curve.csv", index=False, encoding="utf-8")
    log(f"posting_lag_curve.csv {len(lag)} rows")
    return w


# ------------------------------------------------------------------ market y/y
def market_yoy(mv, w):
    parts = []
    for (mkt, v), g in mv.groupby(["market_key", "dump_date"]):
        g = g.set_index("ymi").sort_index()
        idx = range(g.index.min(), g.index.max() + 1)
        g = g.reindex(idx)
        d = pd.DataFrame(index=g.index)
        d["n_reviews"] = g.n_reviews
        d["n_mature12"] = g.n_reviews_mature12
        d["n_mature24"] = g.n_reviews_mature24
        d["n_lag12"] = g.n_reviews.shift(12)
        d["n_mature12_lag12"] = g.n_reviews_mature12.shift(12)
        d["yoy_all"] = d.n_reviews / d.n_lag12 - 1
        d["yoy_mature"] = d.n_mature12 / d.n_mature12_lag12 - 1
        d["yoy_cohort"] = d.n_mature24 / d.n_mature12_lag12 - 1
        d = d.reset_index(names="ymi")
        d.insert(0, "dump_date", v)
        d.insert(0, "market_key", mkt)
        parts.append(d)
    my = pd.concat(parts, ignore_index=True)
    my["country"] = my.market_key.str.split("_").str[0]
    my["region"] = my.country.map(REGION_OF_COUNTRY).fillna("EMEA")
    my["ym"] = my.ymi.map(ymi_to_ym)
    # vintage-matched y/y: month m from the latest vintage over month m-12 from a vintage that is
    # 300 to 430 days older, so both measurements sit the same distance from their own dump
    lat = mv.sort_values("dump_date").groupby("market_key").dump_date.last()
    vm = []
    for mkt, g in mv.groupby("market_key"):
        vs = sorted(g.dump_date.unique())
        late = lat[mkt]
        olds = [v for v in vs if 300 <= (pd.Timestamp(late) - pd.Timestamp(v)).days <= 430]
        if not olds:
            continue
        old = olds[-1]
        a = g[g.dump_date == late].set_index("ymi").n_reviews
        b = g[g.dump_date == old].set_index("ymi").n_reviews
        for m in a.index:
            if (m - 12) in b.index and b[m - 12] > 0:
                vm.append(dict(market_key=mkt, ymi=m, vintage_late=late, vintage_old=old,
                               n_vm_cur=int(a[m]), n_vm_prior=int(b[m - 12]),
                               yoy_vmatch=a[m] / b[m - 12] - 1))
    vmd = pd.DataFrame(vm)
    if len(vmd):
        my = my.merge(vmd, on=["market_key", "ymi"], how="left",
                      suffixes=("", "_vm"))
    else:
        my["yoy_vmatch"] = np.nan
    my.to_csv(OUT / "market_monthly_yoy.csv", index=False, encoding="utf-8")
    log(f"market_monthly_yoy.csv {len(my)} rows; vintage-matched markets "
        f"{vmd.market_key.nunique() if len(vmd) else 0}")
    geo = my[["market_key", "country", "region"]].drop_duplicates().sort_values("market_key")
    geo.to_csv(OUT / "market_geo.csv", index=False, encoding="utf-8")
    return my


# ------------------------------------------------------------------ aggregation
def aggregate(my, mv):
    """Latest vintage per market only. Month m enters only if the market has n[m] and n[m-12]."""
    lat = mv.sort_values("dump_date").groupby("market_key").dump_date.last().rename("latest")
    d = my.join(lat, on="market_key")
    d = d[d.dump_date == d.latest].copy()
    # drop the dump month and anything after it: truncated by the scrape date
    dv = pd.to_datetime(d.dump_date)
    d["dump_ymi"] = dv.dt.year * 12 + dv.dt.month - 1
    d = d[d.ymi < d.dump_ymi]                 # the dump month is truncated by the scrape date
    d = d[d.n_reviews.notna() & d.n_lag12.notna() & (d.n_lag12 > 0)]

    NUMDEN = {"yoy_all": ("n_reviews", "n_lag12"),
              "yoy_mature": ("n_mature12", "n_mature12_lag12"),
              "yoy_cohort": ("n_mature24", "n_mature12_lag12"),
              "yoy_vmatch": ("n_vm_cur", "n_vm_prior")}

    def agg(g, col):
        num, den = NUMDEN[col]
        if num not in g.columns or den not in g.columns:
            return pd.Series({"n_markets": 0})
        ok = g[g[col].notna() & np.isfinite(g[col]) & g[num].notna() & g[den].notna() & (g[den] > 0)]
        if ok.empty:
            return pd.Series({"n_markets": 0})
        return pd.Series({
            "n_markets": len(ok),
            "w_equal": ok[col].mean(),
            "w_reviews": ok[num].sum() / ok[den].sum() - 1,
            "w_median": ok[col].median(),
            "reviews": ok[num].sum(),
            "reviews_lag12": ok[den].sum(),
        })

    rows = []
    for col in ["yoy_all", "yoy_mature", "yoy_cohort", "yoy_vmatch"]:
        for (ymi, reg), g in d.groupby(["ymi", "region"]):
            s = agg(g, col)
            if s.get("n_markets", 0) == 0:
                continue
            rows.append(dict(ymi=ymi, region=reg, measure=col, **s.to_dict()))
    reg = pd.DataFrame(rows)
    reg["ym"] = reg.ymi.map(ymi_to_ym)
    reg["is_dump_month"] = False
    reg.to_csv(OUT / "region_monthly_index.csv", index=False, encoding="utf-8")
    log(f"region_monthly_index.csv {len(reg)} rows")

    grows = []
    for col in ["yoy_all", "yoy_mature", "yoy_cohort", "yoy_vmatch"]:
        for ymi, g in d.groupby("ymi"):
            s = agg(g, col)
            if s.get("n_markets", 0) == 0:
                continue
            r = reg[(reg.ymi == ymi) & (reg.measure == col)]
            wsum = sum(FY25_NIGHTS_SHARE[x] for x in r.region)
            nw = (np.average(r["w_equal"], weights=[FY25_NIGHTS_SHARE[x] for x in r.region])
                  if len(r) and wsum > 0 else np.nan)
            grows.append(dict(ymi=ymi, measure=col, n_markets=int(s.n_markets), n_regions=len(r),
                              w_equal=s.w_equal, w_reviews=s.w_reviews, w_median=s.w_median, w_nights=nw,
                              regions_weight_covered=wsum,
                              reviews=s.reviews, reviews_lag12=s.reviews_lag12))
    gl = pd.DataFrame(grows)
    gl["ym"] = gl.ymi.map(ymi_to_ym)
    gl.to_csv(OUT / "global_monthly_index.csv", index=False, encoding="utf-8")
    log(f"global_monthly_index.csv {len(gl)} rows")

    # coverage
    cov = d.groupby("ymi").agg(
        n_markets=("market_key", "nunique"), reviews=("n_reviews", "sum")).reset_index()
    cov["ym"] = cov.ymi.map(ymi_to_ym)
    cov.to_csv(OUT / "coverage_monthly.csv", index=False, encoding="utf-8")

    # quarterly: sum counts in the calendar quarter, within vintage
    d["year"] = d.ymi // 12
    d["q"] = (d.ymi % 12) // 3 + 1
    qrows = []
    for col, num, den in [("yoy_all", "n_reviews", "n_lag12"),
                          ("yoy_mature", "n_mature12", "n_mature12_lag12"),
                          ("yoy_cohort", "n_mature24", "n_mature12_lag12"),
                          ("yoy_vmatch", "n_vm_cur", "n_vm_prior")]:
        if num not in d.columns:
            continue
        sub = d[d[num].notna() & d[den].notna() & (d[den] > 0)]
        # a market-quarter enters only with all three months present on both sides
        cnt = sub.groupby(["market_key", "year", "q"]).ymi.size().rename("nm")
        s = sub.groupby(["market_key", "region", "year", "q"])[[num, den]].sum().join(cnt)
        s = s[s.nm == 3].reset_index()
        for (y, q), g in s.groupby(["year", "q"]):
            for reg_name, gg in list(g.groupby("region")) + [("GLOBAL", g)]:
                yoy_m = (gg[num] / gg[den] - 1)
                qrows.append(dict(year=y, q=q, quarter=f"{q}Q{str(y)[2:]}", region=reg_name,
                                  measure=col, n_markets=len(gg), w_equal=yoy_m.mean(),
                                  w_reviews=gg[num].sum() / gg[den].sum() - 1, w_median=yoy_m.median(),
                                  reviews=gg[num].sum(), reviews_lag12=gg[den].sum()))
    qq = pd.DataFrame(qrows)
    # nights-weighted global
    piv = qq[qq.region != "GLOBAL"].pivot_table(index=["year", "q", "quarter", "measure"],
                                                columns="region", values="w_equal")
    nw = []
    for k, row in piv.iterrows():
        ws = {r: FY25_NIGHTS_SHARE[r] for r in row.index if pd.notna(row[r])}
        if not ws:
            continue
        nw.append(dict(year=k[0], q=k[1], quarter=k[2], measure=k[3], region="GLOBAL_NW",
                       n_markets=np.nan,
                       w_equal=np.average([row[r] for r in ws], weights=list(ws.values())),
                       w_reviews=np.nan, w_median=np.nan, reviews=np.nan, reviews_lag12=np.nan,
                       regions_weight_covered=sum(ws.values())))
    qq = pd.concat([qq, pd.DataFrame(nw)], ignore_index=True)
    qq.to_csv(OUT / "index_quarterly.csv", index=False, encoding="utf-8")
    log(f"index_quarterly.csv {len(qq)} rows")
    return reg, gl, qq


if __name__ == "__main__":
    mv = load()
    log(f"loaded {len(mv)} market-vintage-months, {mv.market_key.nunique()} markets, "
        f"{mv.groupby(['market_key', 'dump_date']).ngroups} vintages")
    w = wedges(mv)
    my = market_yoy(mv, w)
    aggregate(my, mv)

