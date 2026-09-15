"""
WP-K reviews index 2023 vintage, step 6 (run only if T1 fails, per the pre-registration): a copy of the E5
walk-forward for the single quoted feature (GLOBAL all-reviews, review-weighted quarterly y/y, lag 0, level,
window 2023Q1+, target disclosed nights y/y) with the 2023-vintage values substituted for the quarters the
2023 vintage can supply (4Q22 and 1Q23; 1Q23 only for markets whose dump is late enough for all three months
to be complete, otherwise the quarter is left at its v1 value and the substitution is partial).

Reads  data/processed/q3nowcast/E/index_quarterly.csv        (v1, tracked)
       data/processed/q3nowcast_v2/E/market_vintage_monthly.csv
       MAIN/data/processed/abnb_driver_history_quarterly.csv
Writes data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv
Run: python analysis/src/q3nowcast_v2/E/V6_backtest_substituted.py
"""
import calendar
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[4]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
V1 = WT / "data/processed/q3nowcast/E"
OUT = WT / "data/processed/q3nowcast_v2/E"


def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0:
        return np.nan, np.nanmean(y)
    b = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    return b, y.mean() - b * x.mean()


def walkforward(x, y, start):
    e_f, e_n, ts = [], [], []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < 4 or not np.isfinite(x[t]) or not np.isfinite(y[t]) or not np.isfinite(y[t - 1]):
            continue
        b, a = ols(xs[ok], ys[ok])
        e_f.append(a + b * x[t] - y[t]); e_n.append(y[t - 1] - y[t]); ts.append(t)
    r = lambda e: float(np.sqrt(np.mean(np.asarray(e) ** 2)))
    return dict(wf_n=len(e_f), wf_rmse=r(e_f), wf_rmse_naive=r(e_n), wf_ratio_vs_naive=r(e_f) / r(e_n))


def complete(ymi, dump_date):
    y, m = ymi // 12, ymi % 12 + 1
    return pd.Timestamp(y, m, calendar.monthrange(y, m)[1]) + pd.Timedelta(days=14) <= pd.Timestamp(dump_date)


if __name__ == "__main__":
    kpi = pd.read_csv(MAIN / "data/processed/abnb_driver_history_quarterly.csv")
    kpi["qi"] = kpi.year * 4 + kpi.q - 1
    y = kpi.set_index("qi").nights_m_yoy_pct
    qq = pd.read_csv(V1 / "index_quarterly.csv")
    qq["qi"] = qq.year * 4 + qq.q - 1
    f = qq[(qq.region == "GLOBAL") & (qq.measure == "yoy_all")].set_index("qi").w_reviews.sort_index() * 100
    # 2023-vintage quarterly y/y, review-weighted, markets with all three months complete on both sides
    mv = pd.read_csv(OUT / "market_vintage_monthly.csv")
    v23 = mv[mv.dump_date < "2024"].copy()
    rows = []
    for mkt, g in v23.groupby("market_key"):
        dd = g.dump_date.iloc[0]
        s = g.set_index("ymi").n_reviews
        for q in [2022 * 4 + 3, 2023 * 4 + 0]:
            ms = [(q // 4) * 12 + (q % 4) * 3 + i for i in range(3)]
            if all(complete(m, dd) and m in s.index and (m - 12) in s.index for m in ms):
                rows.append(dict(market_key=mkt, qi=q, num=sum(s[m] for m in ms), den=sum(s[m - 12] for m in ms)))
    r = pd.DataFrame(rows)
    sub = r.groupby("qi").agg(n_markets=("market_key", "nunique"), num=("num", "sum"), den=("den", "sum"))
    sub["yoy_2023_vintage"] = (sub.num / sub.den - 1) * 100
    f2 = f.copy()
    for q, row in sub.iterrows():
        f2[q] = row.yoy_2023_vintage
    # variant b: 1Q23 read as Jan-Feb 2023 only (the two months complete in every dump dated >= 15 Mar 2023),
    # so the market set is the full 114 rather than the 7 late (May) dumps of the literal three-month rule
    rows_b = []
    for mkt, g in v23.groupby("market_key"):
        dd = g.dump_date.iloc[0]
        s = g.set_index("ymi").n_reviews
        ms = [2023 * 12 + 0, 2023 * 12 + 1]
        if all(complete(m, dd) and m in s.index and (m - 12) in s.index for m in ms):
            rows_b.append(dict(market_key=mkt, num=sum(s[m] for m in ms), den=sum(s[m - 12] for m in ms)))
    rb = pd.DataFrame(rows_b)
    f3 = f.copy()
    f3[2023 * 4] = (rb.num.sum() / rb.den.sum() - 1) * 100
    if (2022 * 4 + 3) in sub.index:
        f3[2022 * 4 + 3] = sub.loc[2022 * 4 + 3, "yoy_2023_vintage"]
    # variant c: v1 1Q23 value rescaled by the pooled T1 wedge factor (1 + g_2023v) / (1 + g_2025v), an estimate
    t1 = pd.read_csv(OUT / "t1_wedge_constancy.csv").set_index("scope").loc["GLOBAL"]
    fac = (1 + t1.yoy_2023_vintage_pct / 100) / (1 + t1.yoy_2025_vintage_pct / 100)
    f4 = f.copy()
    f4[2023 * 4] = ((1 + f[2023 * 4] / 100) * fac - 1) * 100
    out = []
    for name, ser in [("v1 (single 2025/2026 vintage)", f),
                      ("a: literal, 2023-vintage 4Q22 (114 mkts) and 1Q23 (3 complete months: 7 late-dump mkts)", f2),
                      ("b: 2023-vintage 4Q22 (114 mkts) and 1Q23 as Jan-Feb 2023 (%d mkts)" % rb.market_key.nunique(), f3),
                      ("c: v1 1Q23 rescaled by the pooled T1 wedge factor %.3f (estimate)" % fac, f4)]:
        df = pd.DataFrame({"x": ser}).join(y.rename("y"), how="inner").dropna()
        df = df[df.index >= 2023 * 4].sort_index()
        full = pd.DataFrame(index=range(df.index.min(), df.index.max() + 1)).join(df)
        start = max(4, int(np.searchsorted(full.index.to_numpy(), 2024 * 4)))
        wf = walkforward(full.x.to_numpy(float), full.y.to_numpy(float), start)
        out.append(dict(variant=name, n=len(df), v_4Q22=ser.get(2022 * 4 + 3, np.nan), v_1Q23=ser.get(2023 * 4, np.nan), **wf))
    t = pd.DataFrame(out)
    t["n_markets_4Q22"] = sub.n_markets.get(2022 * 4 + 3, 0)
    t["n_markets_1Q23"] = sub.n_markets.get(2023 * 4, 0)
    t.to_csv(OUT / "t1_fail_e5_rerun.csv", index=False, encoding="utf-8")
    print(t.round(3).to_string(index=False))
