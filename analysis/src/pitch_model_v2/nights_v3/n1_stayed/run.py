"""N1 - stayed nights from alt data: same-listing vs new-listing decomposition.

Judge's question: how much of Airbnb's reported nights growth is new supply versus demand on
existing listings, and does that split predict reported nights on both point-in-time windows?

Pre-registration that governs this script: docs/pitch-model-v2/lines/nights_v3_prereg.md (DEC-0033).
Nothing here chooses a specification by its 3Q26 output; every spec listed in the brief is reported.

Definitions (all from E4_build_index.py, unchanged):
  c  = yoy_cohort  = n_mature24[m] / n_mature12[m-12] - 1   same listing set both sides (born <= m-24)
  v  = yoy_vmatch  = n[m] in the latest dump / n[m-12] in a dump ~12 months older - 1
                     (both sides sit the same distance from their own scrape: late - m ~ old - (m-12))
  nl = v - c       new-listing contribution, in points of stays y/y
  a  = yoy_all     = n[m] / n[m-12] - 1 within one dump (survivorship-inflated; the published index)
  new_share = n_new_listing_cohort / n_listings, latest dump per market (count-based alternative)

Reported nights y/y g_N is computed from unrounded nights_m levels, never from nights_m_yoy_pct.

Walk-forward protocol is E5_backtest.walkforward(): expanding window, OLS refit on data strictly
before the scored quarter, naive = previous quarter's y/y, W1 data from 1Q22 scored 1Q23-2Q26,
W2 data from 1Q23 scored 1Q24-2Q26. One deviation, stated in the dossier: E5's minimum training
count of 4 is raised to n_params + 2, so a two-regressor spec is never fitted on 4 points. Every
ratio is therefore also reported against a naive and a single-index comparator recomputed on the
*same* scored set.

Run: python3 analysis/src/pitch_model_v2/nights_v3/n1_stayed/run.py
Out: data/processed/pitch_model_v2/nights_v3/N1/
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[5]
E = ROOT / "data/processed/q3nowcast/E"
OUT = ROOT / "data/processed/pitch_model_v2/nights_v3/N1"

REGIONS = ["GLOBAL", "NAM", "EMEA", "APAC", "LatAm"]
Q_FIRST, Q_LAST = 2023 * 4, 2026 * 4 + 1          # 1Q23 .. 2Q26
W = {"W1": 2023 * 4, "W2": 2024 * 4}               # first scored / first fitted quarter
WF_DATA_START = {"W1": 2022 * 4, "W2": 2023 * 4}   # E5's data window for the walk-forward
K_SETTLED = 14      # posting-lag trim, days; E5/E6 pick_k on posting_completeness_curve.csv
JUL = 6             # month index of July inside a year (0-based)
PUBLISHED_SINGLE_INDEX = {"W1": 0.837125, "W2": 0.683209}  # yoy_all RMSE ratio, backtest_abnb_quarterly.csv


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def qlabel(qi: int) -> str:
    return f"{qi % 4 + 1}Q{str(qi // 4)[2:]}"


# --------------------------------------------------------------------------- 1. quarterly series
def quarterly_series() -> pd.DataFrame:
    q = pd.read_csv(E / "index_quarterly.csv")
    q["qi"] = q.year * 4 + q.q - 1
    q = q[q.measure.isin(["yoy_all", "yoy_cohort", "yoy_vmatch"]) & q.region.isin(REGIONS)]
    rows = []
    for (qi, reg), g in q.groupby(["qi", "region"]):
        g = g.set_index("measure")
        d = {"qi": qi, "quarter": qlabel(qi), "region": reg}
        for meas, short in [("yoy_cohort", "c"), ("yoy_vmatch", "v"), ("yoy_all", "a")]:
            if meas in g.index:
                d[f"{short}_pct"] = float(g.loc[meas, "w_reviews"]) * 100
                d[f"{short}_eq_pct"] = float(g.loc[meas, "w_equal"]) * 100
                d[f"{short}_n_markets"] = float(g.loc[meas, "n_markets"])
        rows.append(d)
    s = pd.DataFrame(rows)
    s["nl_pct"] = s.v_pct - s.c_pct
    s["nl_eq_pct"] = s.v_eq_pct - s.c_eq_pct
    return s


def new_listing_share() -> pd.DataFrame:
    """Count-based alternative: new listings (first review in the month) over listings reviewed,
    latest dump per market, summed to region and quarter, plus its y/y change in points."""
    mv = pd.read_csv(E / "market_vintage_monthly.csv")
    geo = pd.read_csv(E / "market_geo.csv")
    mv = mv.merge(geo, on="market_key", how="left")
    mv["dump_ts"] = pd.to_datetime(mv.dump_date)
    lat = mv.groupby("market_key").dump_ts.max().rename("latest")
    d = mv.join(lat, on="market_key")
    d = d[d.dump_ts == d.latest].copy()
    d["dump_ymi"] = d.latest.dt.year * 12 + d.latest.dt.month - 1
    d = d[d.ymi < d.dump_ymi]                       # the dump month is truncated by the scrape date
    d["qi"] = (d.ymi // 12) * 4 + (d.ymi % 12) // 3
    agg = d.groupby(["qi", "region"])[["n_new_listing_cohort", "n_listings"]].sum().reset_index()
    glob = d.groupby("qi")[["n_new_listing_cohort", "n_listings"]].sum().reset_index()
    glob["region"] = "GLOBAL"
    agg = pd.concat([agg, glob], ignore_index=True)
    agg["new_share_pct"] = agg.n_new_listing_cohort / agg.n_listings * 100
    agg = agg.sort_values(["region", "qi"])
    agg["new_share_yoy_pp"] = agg.groupby("region").new_share_pct.diff(4)
    return agg[["qi", "region", "new_share_pct", "new_share_yoy_pp"]]


# --------------------------------------------------------------------------- 2. partial 3Q26
def partial_3q26() -> tuple[pd.DataFrame, dict]:
    """July 2026 is a complete review month in every dump taken on or after 14 Aug 2026 (the
    posting-completeness curve is flat from k = 14 days). August 2026 is truncated at the scrape
    date, so the cohort split - which needs monthly maturity counts, not daily counts - can only be
    read for July. The vintage-matched total is also read on the package's own day-matched
    Jul-1-to-(dump - 14 days) window (E6) as a second basis, where no cohort split is possible.

    Both bases are then lifted to a whole quarter with a gap measured on the same market set:
    full-3Q y/y minus July-only y/y in 2023, 2024 and 2025 (July basis), and E6's
    partial_vs_full_quarter gap (day-matched basis).
    """
    mv = pd.read_csv(E / "market_vintage_monthly.csv")
    geo = pd.read_csv(E / "market_geo.csv")
    mv = mv.merge(geo, on="market_key", how="left")
    mv["dump_ts"] = pd.to_datetime(mv.dump_date)
    lat = mv.groupby("market_key").dump_ts.max().rename("latest")
    mv = mv.join(lat, on="market_key")
    cutoff = pd.Timestamp("2026-07-31") + pd.Timedelta(days=K_SETTLED)

    # market set: latest dump settles July 2026, and a ~12-month-older dump exists for the
    # vintage-matched leg. One set for c, v and nl so that nl = v - c is internally consistent.
    pairs = {}
    for mkt, g in mv.groupby("market_key"):
        late = g.latest.iloc[0]
        if late < cutoff:
            continue
        olds = sorted(v for v in g.dump_ts.unique() if 300 <= (late - v).days <= 430)
        if not olds:
            continue
        pairs[mkt] = (late, olds[-1], g.region.iloc[0])
    mset = sorted(pairs)
    log(f"partial 3Q26 market set: {len(mset)} markets with a settled July 2026 and a year-ago dump")

    late_rows, old_rows = [], []
    for mkt in mset:
        late, old, reg = pairs[mkt]
        g = mv[mv.market_key == mkt]
        a = g[g.dump_ts == late].assign(region=reg)
        b = g[g.dump_ts == old].assign(region=reg)
        late_rows.append(a)
        old_rows.append(b)
    L = pd.concat(late_rows, ignore_index=True)
    O = pd.concat(old_rows, ignore_index=True)

    def months(year, win):
        base = year * 12 + JUL
        return [base] if win == "jul" else [base, base + 1, base + 2]

    def read(year, win, region):
        m = months(year, win)
        Lr = L if region == "GLOBAL" else L[L.region == region]
        Or = O if region == "GLOBAL" else O[O.region == region]
        cur = Lr[Lr.ymi.isin(m)]
        pri_same = Lr[Lr.ymi.isin([x - 12 for x in m])]        # within-vintage prior year
        pri_old = Or[Or.ymi.isin([x - 12 for x in m])]         # vintage-matched prior year
        out = {}
        if pri_same.n_reviews_mature12.sum() > 0:
            out["c"] = (cur.n_reviews_mature24.sum() / pri_same.n_reviews_mature12.sum() - 1) * 100
        if pri_same.n_reviews.sum() > 0:
            out["a"] = (cur.n_reviews.sum() / pri_same.n_reviews.sum() - 1) * 100
        if pri_old.n_reviews.sum() > 0:
            out["v"] = (cur.n_reviews.sum() / pri_old.n_reviews.sum() - 1) * 100
        if "v" in out and "c" in out:
            out["nl"] = out["v"] - out["c"]
        out["n_markets"] = cur.market_key.nunique()
        out["reviews_cur"] = int(cur.n_reviews.sum())
        return out

    rows = []
    # gaps, measured on 2023-2025 on the same market set
    gaps = {}
    for meas in ["c", "v", "a", "nl"]:
        gs = []
        for yr in (2023, 2024, 2025):
            j = read(yr, "jul", "GLOBAL")
            f = read(yr, "q3", "GLOBAL")
            if meas in j and meas in f:
                gs.append(f[meas] - j[meas])
        gaps[meas] = (float(np.mean(gs)), float(np.std(gs, ddof=1)), len(gs))

    for region in REGIONS:
        j26 = read(2026, "jul", region)
        for meas in ["c", "v", "nl", "a"]:
            if meas not in j26:
                continue
            gm, gs, gn = gaps[meas]
            rows.append(dict(basis="jul_only_monthly", region=region, measure=meas,
                             observed_months="2026-07", observed_pct=j26[meas],
                             gap_mean_pp=gm, gap_sd_pp=gs, gap_n_years=gn,
                             corrected_pct=j26[meas] + gm, n_markets=j26["n_markets"],
                             reviews_cur=j26["reviews_cur"],
                             note="within-vintage prior year for c and a; year-ago dump for v"))

    # second basis: E6's day-matched Jul 1 -> dump - 14 days window, vintage-matched and within
    vm = pd.read_csv(E / "vintage_matched_nowcast.csv")
    vm = vm[vm.period == "3q26_to_date"]
    ptf = pd.read_csv(E / "partial_vs_full_quarter.csv")
    for region in REGIONS:
        r = vm[vm.region == region]
        if r.empty:
            continue
        g = ptf[(ptf.region == region) & (ptf.year.isin([2023, 2024, 2025]))]
        gm = float(g.gap_cw_pp.mean()) if len(g) else np.nan
        gs = float(g.gap_cw_pp.std(ddof=1)) if len(g) > 1 else np.nan
        for meas, col in [("v", "vmatch_cw"), ("a", "within_cw")]:
            val = float(r[col].iloc[0]) * 100
            if not np.isfinite(val):
                continue
            rows.append(dict(basis="jul_aug_daymatched_E6", region=region, measure=meas,
                             observed_months="2026-07 + 2026-08 to dump-14d",
                             observed_pct=val, gap_mean_pp=gm, gap_sd_pp=gs, gap_n_years=len(g),
                             corrected_pct=val + gm, n_markets=int(r.n_markets.iloc[0]),
                             reviews_cur=np.nan,
                             note="E6 day-matched window; no cohort split possible on daily counts"))
    p = pd.DataFrame(rows)

    cov = pd.read_csv(E / "q3_2026_coverage.csv")
    cov["aug_covered_to"] = pd.to_datetime(cov.aug_covered_to)
    coverage = dict(markets_total=int(cov.market_key.nunique()),
                    markets_partial_set=len(mset),
                    aug_covered_to_median=str(cov.aug_covered_to.median().date()),
                    aug_covered_to_min=str(cov.aug_covered_to.min().date()),
                    aug_covered_to_max=str(cov.aug_covered_to.max().date()),
                    september_observed=False, k_settled_days=K_SETTLED)
    return p, coverage


# --------------------------------------------------------------------------- 3. regressions
def hac_fit(y, X, names):
    Xc = sm.add_constant(np.asarray(X, float), has_constant="add")
    m = sm.OLS(np.asarray(y, float), Xc).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    return m


def loo_slopes(y, X):
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    n = len(y)
    out = []
    for i in range(n):
        k = np.ones(n, bool)
        k[i] = False
        Xc = sm.add_constant(X[k], has_constant="add")
        out.append(sm.OLS(y[k], Xc).fit().params[1:])
    return np.asarray(out)


def regressions(panel: pd.DataFrame, spec_defs: dict) -> pd.DataFrame:
    rows = []
    for spec, (cols, target_shift, label) in spec_defs.items():
        for wname, q0 in W.items():
            d = panel[(panel.qi >= q0) & (panel.qi <= Q_LAST)][["qi", "gN"] + cols].dropna()
            if len(d) < 4:
                continue
            m = hac_fit(d.gN.values, d[cols].values, cols)
            lo = loo_slopes(d.gN.values, d[cols].values)
            names = ["const"] + cols
            for i, nm in enumerate(names):
                rows.append(dict(spec=spec, spec_label=label, window=wname, n=len(d),
                                 first_q=qlabel(int(d.qi.min())), last_q=qlabel(int(d.qi.max())),
                                 term=nm, coef=float(m.params[i]), se_hac3=float(m.bse[i]),
                                 t_hac3=float(m.tvalues[i]), p_hac3=float(m.pvalues[i]),
                                 r2=float(m.rsquared), r2_adj=float(m.rsquared_adj),
                                 loo_slope_min=(np.nan if i == 0 else float(lo[:, i - 1].min())),
                                 loo_slope_max=(np.nan if i == 0 else float(lo[:, i - 1].max()))))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- 4. walk-forward
def walkforward(panel: pd.DataFrame, cols: list[str], wname: str) -> dict | None:
    """E5_backtest.walkforward, generalised to k regressors. Scored quarters are W[wname] .. 2Q26;
    training data starts at WF_DATA_START[wname] and is strictly before the scored quarter."""
    d = panel.set_index("qi").sort_index()
    idx = list(range(WF_DATA_START[wname], Q_LAST + 1))
    d = d.reindex(idx)
    y = d.gN.to_numpy(float)
    X = d[cols].to_numpy(float)
    min_train = len(cols) + 3          # E5 uses 4 with one regressor; k + 1 params + 2 dof
    start = idx.index(W[wname])
    ef, en, ts = [], [], []
    for t in range(start, len(idx)):
        ok = np.isfinite(y[:t]) & np.isfinite(X[:t]).all(axis=1)
        if ok.sum() < min_train or not np.isfinite(X[t]).all() or not np.isfinite(y[t]):
            continue
        if not np.isfinite(y[t - 1]):
            continue
        Xc = sm.add_constant(X[:t][ok], has_constant="add")
        try:
            b = sm.OLS(y[:t][ok], Xc).fit().params
        except Exception:
            continue
        pred = float(b[0] + X[t] @ b[1:])
        if not np.isfinite(pred):
            continue
        ef.append(pred - y[t])
        en.append(y[t - 1] - y[t])
        ts.append(idx[t])
    if len(ef) < 4:
        return None
    ef, en = np.asarray(ef), np.asarray(en)
    return dict(wf_n=len(ef), scored_first=qlabel(ts[0]), scored_last=qlabel(ts[-1]),
                mae=float(np.mean(np.abs(ef))), mae_naive=float(np.mean(np.abs(en))),
                mae_ratio=float(np.mean(np.abs(ef)) / np.mean(np.abs(en))),
                rmse=float(np.sqrt(np.mean(ef ** 2))), rmse_naive=float(np.sqrt(np.mean(en ** 2))),
                rmse_ratio=float(np.sqrt(np.mean(ef ** 2)) / np.sqrt(np.mean(en ** 2))),
                bias_pp=float(np.mean(ef)), scored=ts, err=ef)


def walkforward_table(panel: pd.DataFrame, spec_defs: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, paths = [], []
    gseries = panel.set_index("qi").sort_index().gN
    for spec, (cols, _, label) in spec_defs.items():
        for wname in W:
            r = walkforward(panel, cols, wname)
            if r is None:
                rows.append(dict(spec=spec, spec_label=label, window=wname, wf_n=0,
                                 note="not evaluable: fewer than 4 scored quarters"))
                continue
            scored, err = r.pop("scored"), r.pop("err")
            en_full = np.asarray([gseries.get(t - 1, np.nan) - gseries.get(t, np.nan)
                                  for t in scored], float)
            for t, e_, n_ in zip(scored, err, en_full):
                paths.append(dict(spec=spec, window=wname, quarter=qlabel(t),
                                  err_spec_pp=float(e_), err_naive_pp=float(n_)))
            # jackknife the ratio one scored quarter at a time (E5 robustness)
            jk_mae, jk_rmse = [], []
            for i in range(len(err)):
                k = np.ones(len(err), bool)
                k[i] = False
                jk_mae.append(np.mean(np.abs(err[k])) / np.mean(np.abs(en_full[k])))
                jk_rmse.append(np.sqrt(np.mean(err[k] ** 2)) / np.sqrt(np.mean(en_full[k] ** 2)))
            # single-index comparator recomputed on the identical scored set
            ref = walkforward(panel, ["a_pct"], wname)
            ref_m = ref_r = np.nan
            if ref is not None:
                rs, re_ = ref.pop("scored"), ref.pop("err")
                keep = [i for i, t in enumerate(rs) if t in scored]
                if keep:
                    e2 = re_[keep]
                    ref_r = float(np.sqrt(np.mean(e2 ** 2)) / np.sqrt(np.mean(en_full ** 2)))
                    ref_m = float(np.mean(np.abs(e2)) / np.mean(np.abs(en_full)))
            rows.append(dict(spec=spec, spec_label=label, window=wname, **r,
                             jk_mae_ratio_min=float(min(jk_mae)), jk_mae_ratio_max=float(max(jk_mae)),
                             jk_rmse_ratio_min=float(min(jk_rmse)), jk_rmse_ratio_max=float(max(jk_rmse)),
                             single_index_mae_ratio_same_set=ref_m,
                             single_index_rmse_ratio_same_set=ref_r,
                             published_single_index_rmse_ratio=PUBLISHED_SINGLE_INDEX[wname],
                             note=""))
    return pd.DataFrame(rows), pd.DataFrame(paths)


# --------------------------------------------------------------------------- 5. regional
def regional(series: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rev = pd.read_csv(ROOT / "data/processed/airbnb_regional_revenue_quarterly.csv")
    rev["qi"] = rev.quarter.str[:4].astype(int) * 4 + rev.quarter.str[-1].astype(int) - 1
    rev = rev.sort_values("qi").set_index("qi")
    cmap = {"NAM": "north_america_usd_m", "EMEA": "emea_usd_m",
            "LatAm": "latam_usd_m", "APAC": "apac_usd_m"}
    rows = []
    for reg, col in cmap.items():
        yoy = (rev[col] / rev[col].shift(4) - 1) * 100
        s = series[series.region == reg].set_index("qi")[["c_pct", "v_pct", "nl_pct"]]
        d = s.join(yoy.rename("rev_yoy")).dropna()
        for wname, q0 in W.items():
            dd = d[d.index >= q0]
            if len(dd) < 5:
                continue
            for spec, cols in [("R-a: v", ["v_pct"]), ("R-b: c+nl", ["c_pct", "nl_pct"])]:
                m = hac_fit(dd.rev_yoy.values, dd[cols].values, cols)
                for i, nm in enumerate(["const"] + cols):
                    rows.append(dict(region=reg, spec=spec, window=wname, n=len(dd),
                                     first_q=qlabel(int(dd.index.min())),
                                     last_q=qlabel(int(dd.index.max())), term=nm,
                                     coef=float(m.params[i]), se_hac3=float(m.bse[i]),
                                     t_hac3=float(m.tvalues[i]), p_hac3=float(m.pvalues[i]),
                                     r2=float(m.rsquared),
                                     contamination="USD revenue: ADR and FX contaminated, not nights"))
    reg_tbl = pd.DataFrame(rows)

    ws = pd.read_csv(ROOT / "data/processed/overnight/10_regional_forecast.csv")
    ws = ws[(ws.period == "3Q26") & (ws.region != "TOTAL")]
    rmap = {"na": "NAM", "emea": "EMEA", "latam": "LatAm", "apac": "APAC"}
    ws["region_code"] = ws.region.map(rmap)
    piv = ws.pivot_table(index="region_code", columns="scenario", values="nights_yoy_pct")
    return reg_tbl, piv


# --------------------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    series = quarterly_series()
    ns = new_listing_share()
    series = series.merge(ns, on=["qi", "region"], how="left")
    series = series.sort_values(["region", "qi"])
    out_series = series[(series.qi >= Q_FIRST) & (series.qi <= Q_LAST)].copy()
    cols = ["quarter", "qi", "region", "c_pct", "v_pct", "nl_pct", "a_pct",
            "new_share_pct", "new_share_yoy_pp", "c_eq_pct", "v_eq_pct", "nl_eq_pct", "a_eq_pct",
            "c_n_markets", "v_n_markets", "a_n_markets"]
    out_series[cols].to_csv(OUT / "series_quarterly.csv", index=False, encoding="utf-8")
    log(f"series_quarterly.csv {len(out_series)} rows")

    part, coverage = partial_3q26()
    part.to_csv(OUT / "partial_3q26.csv", index=False, encoding="utf-8")
    pd.DataFrame([coverage]).to_csv(OUT / "partial_3q26_coverage.csv", index=False, encoding="utf-8")
    log(f"partial_3q26.csv {len(part)} rows; coverage {coverage}")

    # global panel with reported nights y/y from unrounded levels
    kpi = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
    kpi["qi"] = kpi.year * 4 + kpi.q - 1
    kpi = kpi.sort_values("qi").set_index("qi")
    gN = (kpi.nights_m / kpi.nights_m.shift(4) - 1) * 100
    g = series[series.region == "GLOBAL"].set_index("qi")
    panel = pd.DataFrame(index=range(2022 * 4, Q_LAST + 1))
    for col in ["c_pct", "v_pct", "nl_pct", "a_pct"]:
        panel[col] = g[col]
    panel["gN"] = gN
    # one-quarter-ahead stays: X at t+1 lines up with g_N at t. The t+1 quarter for 2Q26 is the
    # partial 3Q26 reading (July basis, gap-corrected); both variants are carried.
    p26 = part[(part.basis == "jul_only_monthly") & (part.region == "GLOBAL")].set_index("measure")
    for col, meas in [("c_pct", "c"), ("v_pct", "v"), ("nl_pct", "nl"), ("a_pct", "a")]:
        lead = panel[col].shift(-1)
        panel[f"{col}_t1_drop"] = lead
        lead_inc = lead.copy()
        lead_inc.loc[Q_LAST] = float(p26.loc[meas, "corrected_pct"])
        panel[f"{col}_t1_incl"] = lead_inc
    panel = panel.reset_index(names="qi")

    spec_defs = {
        "a": (["v_pct"], 0, "g_N(t) on v(t)"),
        "b": (["c_pct", "nl_pct"], 0, "g_N(t) on c(t) and nl(t)"),
        "c_incl": (["c_pct_t1_incl", "nl_pct_t1_incl"], 1,
                   "g_N(t) on c(t+1) and nl(t+1) - partial 3Q26 included as t+1 for 2Q26"),
        "c_drop": (["c_pct_t1_drop", "nl_pct_t1_drop"], 1,
                   "g_N(t) on c(t+1) and nl(t+1) - 2Q26 dropped"),
        "ref_single_index": (["a_pct"], 0, "g_N(t) on yoy_all(t) - the published single index"),
    }
    reg = regressions(panel, spec_defs)
    reg.to_csv(OUT / "regressions.csv", index=False, encoding="utf-8")
    log(f"regressions.csv {len(reg)} rows")

    wf, wfp = walkforward_table(panel, spec_defs)
    wf.to_csv(OUT / "walkforward.csv", index=False, encoding="utf-8")
    wfp.to_csv(OUT / "walkforward_paths.csv", index=False, encoding="utf-8")
    log(f"walkforward.csv {len(wf)} rows; walkforward_paths.csv {len(wfp)} rows")

    # 3Q26 fitted reads
    reads = []
    for spec, (cols, shift, label) in spec_defs.items():
        for wname, q0 in W.items():
            d = panel[(panel.qi >= q0) & (panel.qi <= Q_LAST)][["qi", "gN"] + cols].dropna()
            if len(d) < 4:
                continue
            m = hac_fit(d.gN.values, d[cols].values, cols)
            if shift == 1:
                reads.append(dict(spec=spec, spec_label=label, window=wname, n=len(d),
                                  fitted_gN_3q26_pct=np.nan,
                                  basis="not obtainable: g_N(3Q26) needs stays at 4Q26",
                                  x_used=""))
                continue
            xs, desc = [], []
            for col in cols:
                meas = {"c_pct": "c", "v_pct": "v", "nl_pct": "nl", "a_pct": "a"}[col]
                xs.append(float(p26.loc[meas, "corrected_pct"]))
                desc.append(f"{meas}={xs[-1]:.3f}")
            pred = float(m.params[0] + np.dot(m.params[1:], xs))
            reads.append(dict(spec=spec, spec_label=label, window=wname, n=len(d),
                              fitted_gN_3q26_pct=pred,
                              basis="July-2026 partial corrected to full quarter",
                              x_used="; ".join(desc)))
            # second basis for spec a: E6 day-matched window
            if cols == ["v_pct"]:
                p26b = part[(part.basis == "jul_aug_daymatched_E6") & (part.region == "GLOBAL")].set_index("measure")
                if "v" in p26b.index:
                    xv = float(p26b.loc["v", "corrected_pct"])
                    reads.append(dict(spec=spec, spec_label=label + " [E6 day-matched basis]",
                                      window=wname, n=len(d),
                                      fitted_gN_3q26_pct=float(m.params[0] + m.params[1] * xv),
                                      basis="E6 Jul+Aug-to-date day-matched, corrected to full quarter",
                                      x_used=f"v={xv:.3f}"))
    pd.DataFrame(reads).to_csv(OUT / "reads_3q26.csv", index=False, encoding="utf-8")
    log(f"reads_3q26.csv {len(reads)} rows")

    reg_tbl, ws_piv = regional(series)
    reg_tbl.to_csv(OUT / "regional_revenue_regressions.csv", index=False, encoding="utf-8")
    comp = []
    for region in ["NAM", "EMEA", "APAC", "LatAm"]:
        s2 = series[(series.region == region) & (series.qi == Q_LAST)]
        pj = part[(part.basis == "jul_only_monthly") & (part.region == region)].set_index("measure")
        row = dict(region=region,
                   c_2q26_pct=float(s2.c_pct.iloc[0]), v_2q26_pct=float(s2.v_pct.iloc[0]),
                   nl_2q26_pct=float(s2.nl_pct.iloc[0]),
                   c_jul26_pct=float(pj.loc["c", "observed_pct"]) if "c" in pj.index else np.nan,
                   v_jul26_pct=float(pj.loc["v", "observed_pct"]) if "v" in pj.index else np.nan,
                   nl_jul26_pct=float(pj.loc["nl", "observed_pct"]) if "nl" in pj.index else np.nan)
        for sc in ["bear", "base", "bull"]:
            row[f"ws10_3q26_nights_{sc}_pct"] = float(ws_piv.loc[region, sc])
        comp.append(row)
    pd.DataFrame(comp).to_csv(OUT / "regional_vs_ws10.csv", index=False, encoding="utf-8")
    log(f"regional_revenue_regressions.csv {len(reg_tbl)} rows; regional_vs_ws10.csv {len(comp)} rows")

    print("\n=== GLOBAL series 1Q23-2Q26 ===")
    print(out_series[out_series.region == "GLOBAL"][
        ["quarter", "c_pct", "nl_pct", "v_pct", "a_pct", "new_share_pct"]].round(3).to_string(index=False))
    print("\n=== partial 3Q26, GLOBAL ===")
    print(part[part.region == "GLOBAL"].round(3).to_string(index=False))
    print("\n=== regressions ===")
    print(reg.round(4).to_string(index=False))
    print("\n=== walk-forward ===")
    print(wf.round(4).to_string(index=False))
    print("\n=== 3Q26 reads ===")
    print(pd.DataFrame(reads).round(3).to_string(index=False))
    print("\n=== regional vs WS10 ===")
    print(pd.DataFrame(comp).round(2).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
