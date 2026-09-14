"""
Q3 2026 nowcast, workstream E, step 6: July and August 2026 review-date y/y by market, region and
global, then 3Q26 stays growth with a band and what it implies for reported Nights and Seats Booked.

Three problems have to be handled before a partial quarter can be read:
  1. truncation   the August dumps stop on their scrape date, so August is a part month
  2. posting lag  a review is written after check-out, so the last days before a dump are incomplete
  3. survivorship a dump holds only listings alive at dump time, so the year-ago side of a within-
                  vintage y/y is missing the reviews of listings that have since gone

1 and 2 are handled by a day-matched window that ends k days before the dump date and is compared with
the SAME calendar window 364 days earlier (52 weeks, so the day-of-week mix matches). k is chosen from
the posting-completeness curve measured on markets that have both a June 2026 and an August 2026 dump.
3 is handled by also reporting the vintage-matched version wherever a year-ago dump was obtainable.

Writes data/processed/q3nowcast/E/
  posting_completeness_curve.csv   share of a review date that is already posted k days later
  partial_window_yoy_market.csv    per market: quarter-to-date y/y for 3Q26 and the same window in
                                   every prior year, day-matched
  partial_window_yoy_index.csv     region and global aggregates of the above, three weightings
  monthly_nowcast_2026.csv         July 2026 and August-to-date 2026 y/y, market/region/global
  q3_2026_nowcast.csv              the 3Q26 reading, the implied nights y/y and its band
  q3_2026_coverage.csv             markets and review share behind the August reading

Run: py -3.13 analysis/src/q3nowcast/E6_nowcast.py
"""
import time
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
OUT = WT / "data/processed/q3nowcast/E"
FY25_NIGHTS_SHARE = {"NAM": 28.3, "EMEA": 41.6, "LatAm": 17.9, "APAC": 12.3}
WEEK_SHIFT = 364  # 52 weeks, keeps the day-of-week mix identical across years


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def load_daily():
    d = pd.read_csv(OUT / "market_vintage_daily.csv", parse_dates=["review_date", "dump_date"])
    geo = pd.read_csv(OUT / "market_geo.csv")
    return d.merge(geo, on="market_key", how="left")


# ------------------------------------------------------------------ 1. posting completeness
def completeness(d):
    """Pairs of vintages of the same market: how much of review date x was visible k days later."""
    rows = []
    for mkt, g in d.groupby("market_key"):
        vs = sorted(g.dump_date.unique())
        if len(vs) < 2:
            continue
        early, late = vs[-2], vs[-1]
        a = g[g.dump_date == early].set_index("review_date").n_reviews
        b = g[g.dump_date == late].set_index("review_date").n_reviews
        idx = a.index.intersection(b.index)
        idx = idx[idx <= early]
        if not len(idx):
            continue
        k = (pd.Timestamp(early) - idx).days
        rows.append(pd.DataFrame({"market_key": mkt, "vintage_early": early, "vintage_late": late,
                                  "review_date": idx, "k_days": k,
                                  "n_early": a.loc[idx].to_numpy(), "n_late": b.loc[idx].to_numpy()}))
    if not rows:
        log("no vintage pair: completeness curve not measurable")
        return pd.DataFrame()
    c = pd.concat(rows, ignore_index=True)
    c = c[c.k_days.between(0, 120)]
    cur = (c.groupby("k_days").agg(n_pairs=("market_key", "size"), n_early=("n_early", "sum"),
                                   n_late=("n_late", "sum")).reset_index())
    cur["completeness"] = cur.n_early / cur.n_late
    cur.to_csv(OUT / "posting_completeness_curve.csv", index=False, encoding="utf-8")
    log(f"posting_completeness_curve.csv {len(cur)} rows")
    return cur


def pick_k(cur, thresh=0.985):
    if cur.empty:
        return 21
    ok = cur[(cur.k_days >= 3) & (cur.completeness >= thresh)]
    return int(ok.k_days.min()) if len(ok) else 21


# ------------------------------------------------------------------ 2. day-matched windows
def window_yoy(d, k, start_md=(7, 1)):
    """Per market, on its latest vintage: reviews in [quarter start, dump - k] this year vs the same
    calendar window 364 days earlier, and the same pair of windows in every earlier year."""
    rows = []
    for mkt, g in d.groupby("market_key"):
        v = g.dump_date.max()
        s = g[g.dump_date == v].set_index("review_date").n_reviews.sort_index()
        end = pd.Timestamp(v) - pd.Timedelta(days=k)
        yr = end.year
        start = pd.Timestamp(year=yr, month=start_md[0], day=start_md[1])
        if end < start:
            continue
        for back in range(0, 5):
            a0, a1 = start - pd.Timedelta(days=WEEK_SHIFT * back), end - pd.Timedelta(days=WEEK_SHIFT * back)
            b0, b1 = a0 - pd.Timedelta(days=WEEK_SHIFT), a1 - pd.Timedelta(days=WEEK_SHIFT)
            na = s[(s.index >= a0) & (s.index <= a1)].sum()
            nb = s[(s.index >= b0) & (s.index <= b1)].sum()
            if nb <= 0 or b0 < s.index.min():
                continue
            rows.append(dict(market_key=mkt, region=g.region.iloc[0], vintage=str(v)[:10],
                             years_back=back, win_start=str(a0.date()), win_end=str(a1.date()),
                             n_cur=int(na), n_prior=int(nb), yoy=na / nb - 1))
    w = pd.DataFrame(rows)
    w.to_csv(OUT / "partial_window_yoy_market.csv", index=False, encoding="utf-8")
    log(f"partial_window_yoy_market.csv {len(w)} rows, {w.market_key.nunique()} markets")
    return w


def aggregate_windows(w):
    rows = []
    for (back, reg), g in list(w.groupby(["years_back", "region"])) + \
                          [((b, "GLOBAL"), gg) for b, gg in w.groupby("years_back")]:
        rows.append(dict(years_back=back, region=reg, n_markets=len(g), w_equal=g.yoy.mean(),
                         w_reviews=g.n_cur.sum() / g.n_prior.sum() - 1, w_median=g.yoy.median(),
                         n_cur=g.n_cur.sum(), n_prior=g.n_prior.sum()))
    a = pd.DataFrame(rows)
    nw = []
    for back, g in a[a.region.isin(FY25_NIGHTS_SHARE)].groupby("years_back"):
        ws = [FY25_NIGHTS_SHARE[r] for r in g.region]
        nw.append(dict(years_back=back, region="GLOBAL_NW", n_markets=int(g.n_markets.sum()),
                       w_equal=np.average(g.w_equal, weights=ws), w_reviews=np.nan,
                       w_median=np.nan, n_cur=np.nan, n_prior=np.nan,
                       regions_weight_covered=sum(ws)))
    a = pd.concat([a, pd.DataFrame(nw)], ignore_index=True)
    a.to_csv(OUT / "partial_window_yoy_index.csv", index=False, encoding="utf-8")
    log(f"partial_window_yoy_index.csv {len(a)} rows")
    return a


# ------------------------------------------------------------------ 3. July / August monthly
def monthly_2026(d, k):
    rows = []
    for mkt, g in d.groupby("market_key"):
        v = pd.Timestamp(g.dump_date.max())
        s = g[g.dump_date == g.dump_date.max()].set_index("review_date").n_reviews.sort_index()
        for label, a0, a1 in [
            ("2026-07", pd.Timestamp("2026-07-01"), pd.Timestamp("2026-07-31")),
            ("2026-08_to_date", pd.Timestamp("2026-08-01"), v - pd.Timedelta(days=k)),
            ("2026-06", pd.Timestamp("2026-06-01"), pd.Timestamp("2026-06-30")),
        ]:
            if a1 < a0 or a1 > v - pd.Timedelta(days=k):
                continue
            b0, b1 = a0 - pd.Timedelta(days=WEEK_SHIFT), a1 - pd.Timedelta(days=WEEK_SHIFT)
            na = s[(s.index >= a0) & (s.index <= a1)].sum()
            nb = s[(s.index >= b0) & (s.index <= b1)].sum()
            if nb <= 0:
                continue
            rows.append(dict(market_key=mkt, region=g.region.iloc[0], period=label,
                             vintage=str(v.date()), win_start=str(a0.date()), win_end=str(a1.date()),
                             n_cur=int(na), n_prior=int(nb), yoy=na / nb - 1))
    m = pd.DataFrame(rows)
    agg = []
    for (per, reg), g in list(m.groupby(["period", "region"])) + \
                         [((p, "GLOBAL"), gg) for p, gg in m.groupby("period")]:
        agg.append(dict(period=per, region=reg, n_markets=len(g), w_equal=g.yoy.mean(),
                        w_reviews=g.n_cur.sum() / g.n_prior.sum() - 1, w_median=g.yoy.median(),
                        n_cur=g.n_cur.sum(), n_prior=g.n_prior.sum()))
    a = pd.DataFrame(agg)
    nw = []
    for per, g in a[a.region.isin(FY25_NIGHTS_SHARE)].groupby("period"):
        ws = [FY25_NIGHTS_SHARE[r] for r in g.region]
        nw.append(dict(period=per, region="GLOBAL_NW", n_markets=int(g.n_markets.sum()),
                       w_equal=np.average(g.w_equal, weights=ws), w_reviews=np.nan, w_median=np.nan,
                       n_cur=np.nan, n_prior=np.nan, regions_weight_covered=sum(ws)))
    a = pd.concat([a, pd.DataFrame(nw)], ignore_index=True)
    m.to_csv(OUT / "monthly_nowcast_2026_market.csv", index=False, encoding="utf-8")
    a.to_csv(OUT / "monthly_nowcast_2026.csv", index=False, encoding="utf-8")
    log(f"monthly_nowcast_2026.csv {len(a)} rows, market file {len(m)} rows")
    return m, a


# ----------------------------------------------------- 3b. vintage-matched version of the same windows
def vintage_matched(d, k):
    """The same July and August-to-date windows, but with the prior-year side read from the market's
    own ~August 2025 dump instead of from the 2026 dump. Both sides then sit the same number of days
    after their own scrape, so the survivorship wedge and the posting lag cancel instead of biasing
    the level. Only markets where a year-ago dump was still on the CDN can do this."""
    rows = []
    for mkt, g in d.groupby("market_key"):
        vs = sorted(pd.to_datetime(g.dump_date.unique()))
        late = vs[-1]
        olds = [v for v in vs if 300 <= (late - v).days <= 430]
        if not olds:
            continue
        old = olds[-1]
        sl = g[g.dump_date == late].set_index("review_date").n_reviews.sort_index()
        so = g[g.dump_date == old].set_index("review_date").n_reviews.sort_index()
        cur_end = min(late - pd.Timedelta(days=k),
                      old - pd.Timedelta(days=k) + pd.Timedelta(days=WEEK_SHIFT))
        for label, a0, a1 in [
            ("2026-07", pd.Timestamp("2026-07-01"), pd.Timestamp("2026-07-31")),
            ("2026-08_to_date", pd.Timestamp("2026-08-01"), cur_end),
            ("3q26_to_date", pd.Timestamp("2026-07-01"), cur_end),
        ]:
            if a1 < a0 or a1 > cur_end:
                continue
            b0, b1 = a0 - pd.Timedelta(days=WEEK_SHIFT), a1 - pd.Timedelta(days=WEEK_SHIFT)
            na = int(sl[(sl.index >= a0) & (sl.index <= a1)].sum())
            nb = int(so[(so.index >= b0) & (so.index <= b1)].sum())
            nb_same = int(sl[(sl.index >= b0) & (sl.index <= b1)].sum())
            if nb <= 0 or nb_same <= 0:
                continue
            rows.append(dict(market_key=mkt, region=g.region.iloc[0], period=label,
                             vintage_late=str(late.date()), vintage_old=str(old.date()),
                             win_start=str(a0.date()), win_end=str(a1.date()),
                             n_cur=na, n_prior_oldvintage=nb, n_prior_samevintage=nb_same,
                             yoy_vmatch=na / nb - 1, yoy_within=na / nb_same - 1,
                             wedge_pp=(na / nb_same - na / nb) * 100))
    m = pd.DataFrame(rows)
    agg = []
    for (per, reg), g in list(m.groupby(["period", "region"])) +                          [((p_, "GLOBAL"), gg) for p_, gg in m.groupby("period")]:
        agg.append(dict(period=per, region=reg, n_markets=len(g),
                        vmatch_eq=g.yoy_vmatch.mean(),
                        vmatch_cw=g.n_cur.sum() / g.n_prior_oldvintage.sum() - 1,
                        within_eq=g.yoy_within.mean(),
                        within_cw=g.n_cur.sum() / g.n_prior_samevintage.sum() - 1,
                        wedge_eq_pp=g.wedge_pp.mean()))
    a = pd.DataFrame(agg)
    nwl = []
    for per, g in a[a.region.isin(FY25_NIGHTS_SHARE)].groupby("period"):
        ws = [FY25_NIGHTS_SHARE[r] for r in g.region]
        nwl.append(dict(period=per, region="GLOBAL_NW", n_markets=int(g.n_markets.sum()),
                        vmatch_eq=np.average(g.vmatch_eq, weights=ws), vmatch_cw=np.nan,
                        within_eq=np.average(g.within_eq, weights=ws), within_cw=np.nan,
                        wedge_eq_pp=np.average(g.wedge_eq_pp, weights=ws),
                        regions_weight_covered=sum(ws)))
    a = pd.concat([a, pd.DataFrame(nwl)], ignore_index=True)
    m.to_csv(OUT / "vintage_matched_nowcast_market.csv", index=False, encoding="utf-8")
    a.to_csv(OUT / "vintage_matched_nowcast.csv", index=False, encoding="utf-8")
    log(f"vintage_matched_nowcast.csv {len(a)} rows, markets {m.market_key.nunique() if len(m) else 0}")
    return m, a


# ------------------------------------------------------------------ 4. partial to full quarter
def partial_to_full(d, k):
    """For each market and each of the years we can see whole, the day-matched Jul-1-to-Aug-D y/y and
    the whole-quarter Jul-1-to-Sep-30 y/y, both from the same dump. The gap between them is what the
    missing half of August plus September adds, and it is what the 3Q26 partial reading has to carry."""
    rows = []
    for mkt, g in d.groupby("market_key"):
        v = pd.Timestamp(g.dump_date.max())
        s = g[g.dump_date == g.dump_date.max()].set_index("review_date").n_reviews.sort_index()
        end26 = v - pd.Timedelta(days=k)
        for back in range(0, 5):
            off = pd.Timedelta(days=WEEK_SHIFT * back)
            pa0, pa1 = pd.Timestamp("2026-07-01") - off, end26 - off
            pb0, pb1 = pa0 - pd.Timedelta(days=WEEK_SHIFT), pa1 - pd.Timedelta(days=WEEK_SHIFT)
            fa0, fa1 = pd.Timestamp("2026-07-01") - off, pd.Timestamp("2026-09-30") - off
            fb0, fb1 = fa0 - pd.Timedelta(days=WEEK_SHIFT), fa1 - pd.Timedelta(days=WEEK_SHIFT)
            if pb0 < s.index.min():
                continue
            w = lambda a, b: int(s[(s.index >= a) & (s.index <= b)].sum())
            pc, pp = w(pa0, pa1), w(pb0, pb1)
            fc, fp = (w(fa0, fa1), w(fb0, fb1)) if fa1 <= end26 else (np.nan, np.nan)
            if pp <= 0:
                continue
            rows.append(dict(market_key=mkt, region=g.region.iloc[0], year=2026 - back,
                             n_partial_cur=pc, n_partial_prior=pp,
                             partial_yoy=pc / pp - 1,
                             n_full_cur=fc, n_full_prior=fp,
                             full_yoy=(fc / fp - 1) if (fp and fp > 0) else np.nan))
    m = pd.DataFrame(rows)
    agg = []
    for (yr, reg), g in list(m.groupby(["year", "region"])) +                         [((y, "GLOBAL"), gg) for y, gg in m.groupby("year")]:
        ff = g.dropna(subset=["n_full_cur", "n_full_prior"])
        agg.append(dict(year=yr, region=reg, n_markets=len(g),
                        partial_eq=g.partial_yoy.mean(),
                        partial_cw=g.n_partial_cur.sum() / g.n_partial_prior.sum() - 1,
                        full_eq=ff.full_yoy.mean() if len(ff) else np.nan,
                        full_cw=(ff.n_full_cur.sum() / ff.n_full_prior.sum() - 1) if len(ff) else np.nan))
    a = pd.DataFrame(agg)
    a["gap_eq_pp"] = (a.full_eq - a.partial_eq) * 100
    a["gap_cw_pp"] = (a.full_cw - a.partial_cw) * 100
    m.to_csv(OUT / "partial_vs_full_quarter_market.csv", index=False, encoding="utf-8")
    a.to_csv(OUT / "partial_vs_full_quarter.csv", index=False, encoding="utf-8")
    log(f"partial_vs_full_quarter.csv {len(a)} rows")
    return a


# ------------------------------------------------------------------ 5. map the index to nights
def implied_nights(ptf, wi, vm_a):
    """Three steps. (1) Take the 3Q26 quarter-to-date index (Jul 1 to dump minus k, day-matched) for a
    measure and weighting whose partial window is built from the same counts: yoy_all (all reviews,
    within the 2026 dump) and yoy_vmatch (2026 dump over the 2025 dump). (2) Lift it to a whole-quarter
    index with the partial-to-full gap measured on 2023-2025 (measured on all reviews within vintage;
    applied to the vintage-matched rows as an assumption). (3) Put it through the OLS of disclosed
    nights y/y on the whole-quarter index fitted on 2023Q1-2026Q2, the same fit the E5 walk-forward
    scores, and carry the walk-forward RMSE (out of sample) as the band, not the in-sample residual.
    A second mapping anchors on the last print: nights_2Q26 + slope x (index_3Q26 - index_2Q26)."""
    kpi = pd.read_csv(MAIN / "data/processed/abnb_driver_history_quarterly.csv")
    kpi["qi"] = kpi.year * 4 + kpi.q - 1
    qq = pd.read_csv(OUT / "index_quarterly.csv")
    qq["qi"] = qq.year * 4 + qq.q - 1
    bt = pd.read_csv(OUT / "backtest_abnb_quarterly.csv") if (OUT / "backtest_abnb_quarterly.csv").exists() else pd.DataFrame()
    g = ptf[ptf.region == "GLOBAL"].set_index("year")
    wi0 = wi[wi.years_back == 0].set_index("region")
    vm0 = vm_a[vm_a.period == "3q26_to_date"].set_index("region")
    # (measure, weighting column in index_quarterly, region row in index_quarterly, partial reading, gap column)
    specs = [
        ("yoy_all", "w_reviews", "GLOBAL", float(wi0.loc["GLOBAL", "w_reviews"]), "gap_cw_pp", "measured"),
        ("yoy_all", "w_equal", "GLOBAL", float(wi0.loc["GLOBAL", "w_equal"]), "gap_eq_pp", "measured"),
        ("yoy_all", "w_median", "GLOBAL", float(wi0.loc["GLOBAL", "w_median"]), "gap_eq_pp", "measured"),
        ("yoy_all", "w_equal", "GLOBAL_NW", float(wi0.loc["GLOBAL_NW", "w_equal"]), "gap_eq_pp", "assumed_global_gap"),
        ("yoy_vmatch", "w_reviews", "GLOBAL", float(vm0.loc["GLOBAL", "vmatch_cw"]), "gap_cw_pp", "assumed_from_yoy_all"),
        ("yoy_vmatch", "w_equal", "GLOBAL", float(vm0.loc["GLOBAL", "vmatch_eq"]), "gap_eq_pp", "assumed_from_yoy_all"),
        ("yoy_vmatch", "w_equal", "GLOBAL_NW", float(vm0.loc["GLOBAL_NW", "vmatch_eq"]), "gap_eq_pp", "assumed_from_yoy_all"),
    ]
    rows = []
    for meas, wcol, reg, part, gcol, gap_src in specs:
        f = qq[(qq.region == reg) & (qq.measure == meas)][["qi", wcol]].dropna()
        df = f.merge(kpi[["qi", "nights_m_yoy_pct"]], on="qi", how="inner")
        df = df[df.qi >= 2023 * 4].dropna().sort_values("qi")
        if len(df) < 8:
            continue
        x, y = df[wcol].to_numpy() * 100, df.nights_m_yoy_pct.to_numpy()
        b = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
        a = y.mean() - b * x.mean()
        resid_sd = float(np.std(y - (a + b * x), ddof=1))
        part26 = part * 100
        gaps = g.loc[[y_ for y_ in [2023, 2024, 2025] if y_ in g.index], gcol].dropna()
        gap_mean = float(gaps.mean())
        gap_sd = float(gaps.std(ddof=1)) if len(gaps) > 1 else np.nan
        idx26 = part26 + gap_mean
        pt = a + b * idx26
        idx_2q26 = float(x[df.qi.to_numpy() == 2026 * 4 + 1][0]) if (df.qi == 2026 * 4 + 1).any() else np.nan
        n2q26 = float(kpi[(kpi.year == 2026) & (kpi.q == 2)].nights_m_yoy_pct.iloc[0])
        pt_anchor = n2q26 + b * (idx26 - idx_2q26) if np.isfinite(idx_2q26) else np.nan
        wf_rmse, wf_ratio = np.nan, np.nan
        if len(bt):
            k = bt[(bt.feature == f"{reg}|{meas}|{wcol}") & (bt.lag == 0) & (bt["transform"] == "level")
                   & (bt.target == "nights_yoy") & (bt.window == "2023Q1+")]
            if len(k):
                wf_rmse, wf_ratio = float(k.wf_rmse.iloc[0]), float(k.wf_ratio_vs_naive.iloc[0])
        base_sd = wf_rmse if np.isfinite(wf_rmse) else resid_sd
        band = float(np.sqrt(base_sd ** 2 + (b * gap_sd) ** 2)) if np.isfinite(gap_sd) else base_sd
        rows.append(dict(measure=meas, weighting=wcol, region=reg, n_fit=len(df), slope=b, intercept=a,
                         r=float(np.corrcoef(x, y)[0, 1]), resid_sd_pp=resid_sd, wf_rmse_pp=wf_rmse,
                         wf_ratio_vs_naive=wf_ratio,
                         partial_index_3q26_pct=part26, gap_source=gap_src, gap_mean_pp=gap_mean,
                         gap_sd_pp=gap_sd, full_index_3q26_pct=idx26, index_2q26_pct=idx_2q26,
                         implied_nights_yoy=pt, implied_nights_yoy_anchored_2q26=pt_anchor,
                         band_pp=band, lo=pt - band, hi=pt + band,
                         naive_2q26=n2q26,
                         prior_year_3q25=float(kpi[(kpi.year == 2025) & (kpi.q == 3)].nights_m_yoy_pct.iloc[0]),
                         team_baseline_3q26=9.9))
    r = pd.DataFrame(rows)
    r.to_csv(OUT / "q3_2026_nowcast.csv", index=False, encoding="utf-8")
    log(f"q3_2026_nowcast.csv {len(r)} rows")
    return r


if __name__ == "__main__":
    d = load_daily()
    log(f"daily rows {len(d)}, markets {d.market_key.nunique()}, vintages "
        f"{d.groupby(['market_key', 'dump_date']).ngroups}")
    cur = completeness(d)
    k = pick_k(cur)
    log(f"posting-lag trim k = {k} days")
    w = window_yoy(d, k)
    wi = aggregate_windows(w)
    m, ma = monthly_2026(d, k)
    vm_m, vm_a = vintage_matched(d, k)
    ptf = partial_to_full(d, k)
    r = implied_nights(ptf, wi, vm_a)
    # coverage
    lat = d.groupby("market_key").dump_date.max().rename("vintage").reset_index()
    lat["aug_covered_to"] = lat.vintage - pd.Timedelta(days=k)
    lat = lat.merge(m[m.period == "2026-08_to_date"][["market_key", "n_cur", "region"]], on="market_key", how="left")
    lat.to_csv(OUT / "q3_2026_coverage.csv", index=False, encoding="utf-8")
    print(vm_a.to_string(index=False))
    print(ptf.to_string(index=False))
    print(wi.to_string(index=False))
    print(ma.to_string(index=False))
    print(r.to_string(index=False))
