"""
WP-K reviews index 2023 vintage, step 4: the pre-registered tests T1 (wedge constancy) and T2 (attrition
curve extension), exactly as written in section 0 of
docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md before this ran.

Reads  data/processed/q3nowcast_v2/E/market_vintage_monthly.csv   (V2: held vintages + 2023 vintages)
       data/processed/q3nowcast/E/market_geo.csv                   (v1, tracked; region map)
Writes data/processed/q3nowcast_v2/E/
  t1_wedge_constancy.csv          global + region pooled within-vintage y/y in both vintages, difference, pass flag
  t1_wedge_constancy_monthly.csv  the same by review month (descriptive)
  t1_market_pairs.csv             every market x month pair that entered T1
  t2_attrition_extension.csv      pooled 2025/2023 ratio by dump age (26-40 months) and the pass flag
  t2_attrition_by_age.csv         the table 2.2 extension: ratio by months-before-early-dump, 2023->2025 and 2023->2026

Run: python analysis/src/q3nowcast_v2/E/V4_tests_T1_T2.py
"""
import calendar, time
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[4]
OUT = WT / "data/processed/q3nowcast_v2/E"
GEO = WT / "data/processed/q3nowcast/E/market_geo.csv"
T1_MONTHS = list(range(2022 * 12 + 2, 2023 * 12 + 2))       # Mar 2022 .. Feb 2023 (ymi)
T1_GLOBAL_PP, T1_REGION_PP = 2.0, 3.0
T2_AGE = (26, 40)
T2_BAND = (0.75, 0.90)
POST_DAYS = 14


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def ymi_to_ym(i):
    return f"{i // 12}-{i % 12 + 1:02d}"


def month_end(ymi):
    y, m = ymi // 12, ymi % 12 + 1
    return pd.Timestamp(y, m, calendar.monthrange(y, m)[1])


def complete(ymi, dump_date):
    return month_end(ymi) + pd.Timedelta(days=POST_DAYS) <= pd.Timestamp(dump_date)


def load():
    mv = pd.read_csv(OUT / "market_vintage_monthly.csv")
    geo = pd.read_csv(GEO)
    mv = mv.merge(geo[["market_key", "region"]], on="market_key", how="left")
    mv["region"] = mv.region.fillna("EMEA")
    v23 = mv[mv.dump_date < "2024"]
    held = mv[mv.dump_date >= "2025"]
    first25 = held[held.dump_date < "2026"].groupby("market_key").dump_date.min()
    first26 = held[held.dump_date >= "2026"].groupby("market_key").dump_date.min()
    v25 = held[held.dump_date == held.market_key.map(first25)]
    v26 = held[held.dump_date == held.market_key.map(first26)]
    mk = sorted(set(v23.market_key) & set(v25.market_key))
    log(f"2023 vintage markets {v23.market_key.nunique()}, held 2025 vintage markets {len(first25)}, both {len(mk)}")
    return mv, v23[v23.market_key.isin(mk)], v25[v25.market_key.isin(mk)], v26[v26.market_key.isin(mk)]


def pooled(df, num, den):
    return df[num].sum() / df[den].sum() - 1


def t1(v23, v25):
    a = v23.set_index(["market_key", "ymi"])
    b = v25.set_index(["market_key", "ymi"])
    rows = []
    for mkt, g in v23.groupby("market_key"):
        dd = g.dump_date.iloc[0]
        reg = g.region.iloc[0]
        for m in T1_MONTHS:
            if not complete(m, dd):
                continue
            k, kl = (mkt, m), (mkt, m - 12)
            if k in a.index and kl in a.index and k in b.index and kl in b.index:
                rows.append(dict(market_key=mkt, region=reg, dump_2023=dd, dump_2025=v25[v25.market_key == mkt].dump_date.iloc[0],
                                 ymi=m, ym=ymi_to_ym(m),
                                 n23=int(a.loc[k, "n_reviews"]), n23_lag=int(a.loc[kl, "n_reviews"]),
                                 n25=int(b.loc[k, "n_reviews"]), n25_lag=int(b.loc[kl, "n_reviews"])))
    p = pd.DataFrame(rows)
    p = p[(p.n23_lag > 0) & (p.n25_lag > 0)]
    p["yoy23"] = p.n23 / p.n23_lag - 1
    p["yoy25"] = p.n25 / p.n25_lag - 1
    p.to_csv(OUT / "t1_market_pairs.csv", index=False, encoding="utf-8")

    def block(g, name):
        return dict(scope=name, n_markets=g.market_key.nunique(), n_pairs=len(g),
                    reviews_2023v=int(g.n23.sum()), reviews_2025v=int(g.n25.sum()),
                    yoy_2023_vintage_pct=100 * pooled(g, "n23", "n23_lag"),
                    yoy_2025_vintage_pct=100 * pooled(g, "n25", "n25_lag"),
                    equal_wt_yoy_2023_pct=100 * g.yoy23.mean(), equal_wt_yoy_2025_pct=100 * g.yoy25.mean())
    out = [block(p, "GLOBAL")] + [block(g, r) for r, g in p.groupby("region")]
    t = pd.DataFrame(out)
    t["diff_pp"] = t.yoy_2025_vintage_pct - t.yoy_2023_vintage_pct
    t["equal_wt_diff_pp"] = t.equal_wt_yoy_2025_pct - t.equal_wt_yoy_2023_pct
    t["line_pp"] = np.where(t.scope == "GLOBAL", T1_GLOBAL_PP, T1_REGION_PP)
    t["pass"] = t.diff_pp.abs() <= t.line_pp
    t["overall_pass"] = bool(t["pass"].all())
    t.to_csv(OUT / "t1_wedge_constancy.csv", index=False, encoding="utf-8")
    mrows = []
    for (m, r), g in list(p.groupby(["ymi", "region"])) + [((m, "GLOBAL"), g) for m, g in p.groupby("ymi")]:
        mrows.append(dict(ym=ymi_to_ym(m), region=r, n_markets=g.market_key.nunique(),
                          yoy_2023_vintage_pct=100 * pooled(g, "n23", "n23_lag"),
                          yoy_2025_vintage_pct=100 * pooled(g, "n25", "n25_lag")))
    mm = pd.DataFrame(mrows)
    mm["diff_pp"] = mm.yoy_2025_vintage_pct - mm.yoy_2023_vintage_pct
    mm.sort_values(["region", "ym"]).to_csv(OUT / "t1_wedge_constancy_monthly.csv", index=False, encoding="utf-8")
    print("T1 wedge constancy (pooled review-weighted within-vintage y/y, Mar 2022 to Feb 2023)")
    print(t[["scope", "n_markets", "n_pairs", "yoy_2023_vintage_pct", "yoy_2025_vintage_pct", "diff_pp",
             "equal_wt_diff_pp", "line_pp", "pass"]].round(2).to_string(index=False))
    return t, p


def t2(v23, v25, v26):
    a = v23.set_index(["market_key", "ymi"]).n_reviews
    rows = []
    for late, tag in [(v25, "2025"), (v26, "2026")]:
        b = late.set_index(["market_key", "ymi"]).n_reviews
        dumps = late.groupby("market_key").dump_date.first()
        for mkt, g in v23.groupby("market_key"):
            if mkt not in dumps.index:
                continue
            dd23, ddl = g.dump_date.iloc[0], dumps[mkt]
            e = pd.Timestamp(dd23); l = pd.Timestamp(ddl)
            e_ymi, l_ymi = e.year * 12 + e.month - 1, l.year * 12 + l.month - 1
            for m in g.ymi:
                if m < 2015 * 12 or not complete(m, dd23) or (mkt, m) not in b.index:
                    continue
                rows.append(dict(late_vintage=tag, market_key=mkt, region=g.region.iloc[0], ymi=m, ym=ymi_to_ym(m),
                                 dump_2023=dd23, dump_late=ddl, gap_months=l_ymi - e_ymi,
                                 months_before_early_dump=e_ymi - m, age_at_late_dump=l_ymi - m,
                                 n_early=int(a[(mkt, m)]), n_late=int(b[(mkt, m)])))
    w = pd.DataFrame(rows)
    w = w[w.n_early > 0]
    w["ratio"] = w.n_late / w.n_early
    # primary: 2025 vintage, age at late dump 26-40 months
    s = w[(w.late_vintage == "2025") & w.age_at_late_dump.between(*T2_AGE)]
    prim = dict(scope="GLOBAL", late_vintage="2025", age_lo=T2_AGE[0], age_hi=T2_AGE[1], n_markets=s.market_key.nunique(),
                n_pairs=len(s), n_early=int(s.n_early.sum()), n_late=int(s.n_late.sum()),
                pooled_ratio=s.n_late.sum() / s.n_early.sum(), median_ratio=s.ratio.median(),
                mean_gap_months=s.gap_months.mean())
    regs = []
    for r, g in s.groupby("region"):
        regs.append(dict(scope=r, late_vintage="2025", age_lo=T2_AGE[0], age_hi=T2_AGE[1], n_markets=g.market_key.nunique(),
                         n_pairs=len(g), n_early=int(g.n_early.sum()), n_late=int(g.n_late.sum()),
                         pooled_ratio=g.n_late.sum() / g.n_early.sum(), median_ratio=g.ratio.median(),
                         mean_gap_months=g.gap_months.mean()))
    t = pd.DataFrame([prim] + regs)
    t["band_lo"], t["band_hi"] = T2_BAND
    t["pass"] = t.pooled_ratio.between(*T2_BAND)
    t["overall_pass"] = bool(t.loc[t.scope == "GLOBAL", "pass"].iloc[0])
    t["annualised_retention"] = t.pooled_ratio ** (12 / t.mean_gap_months)
    t.to_csv(OUT / "t2_attrition_extension.csv", index=False, encoding="utf-8")
    print("T2 attrition extension (pooled n_late / n_2023, review months aged 26-40 months at the 2025 dump)")
    print(t.round(3).to_string(index=False))
    # table 2.2 extension by months before the early dump
    by = (w.groupby(["late_vintage", "months_before_early_dump"])
            .agg(n_pairs=("market_key", "size"), n_early=("n_early", "sum"), n_late=("n_late", "sum"),
                 median_ratio=("ratio", "median"), mean_gap_months=("gap_months", "mean")).reset_index())
    by["pooled_ratio"] = by.n_late / by.n_early
    by["annualised_retention"] = by.pooled_ratio ** (12 / by.mean_gap_months)
    by.to_csv(OUT / "t2_attrition_by_age.csv", index=False, encoding="utf-8")
    w.to_csv(OUT / "t2_pairs.csv", index=False, encoding="utf-8")
    sel = by[(by.late_vintage == "2025") & by.months_before_early_dump.isin([1, 3, 6, 12, 18, 24, 36, 48, 60])]
    print("table 2.2 extension, 2023 -> 2025 vintage (gap about 29 months):")
    print(sel[["months_before_early_dump", "n_pairs", "pooled_ratio", "median_ratio", "annualised_retention"]].round(3).to_string(index=False))
    return t, by


if __name__ == "__main__":
    mv, v23, v25, v26 = load()
    t1(v23, v25)
    t2(v23, v25, v26)
