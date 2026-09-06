"""08_altdata_backtests.py -- alt-data / high-frequency demand features, composite indexes and walk-forward backtests
against ABNB quarterly KPIs (nights, GBV, ADR, revenue), plus a Q3 2026 nowcast.

Reads (all relative to repo root):
  data/processed/abnb_driver_history_quarterly.csv          KPIs and y/y (letters)
  data/processed/predictive/03_quarterly_panel.csv          ADR ex-FX and FX effect (letters, hardcoded in 03), BEA hotel series
  data/processed/abnb_backlog_indicators.csv                unearned fees, funds held (XBRL)
  data/processed/eurostat_platform_nights_monthly.csv       Eurostat tour_ce_omr EU27 nights, monthly to Mar 2026
  data/processed/predictive/02_peer_prints.csv              MAR / HLT RevPAR y/y, BKNG room nights
  data/processed/overnight/08_trends_weekly.csv             Google Trends (08_trends_pull.py), if present
  data/processed/overnight/08_ia_city_yoy.csv, 08_ia_dump_metrics.csv   Inside Airbnb fixed-city panel (08_inside_airbnb_demand.py)
  data/processed/inside_airbnb_like_for_like.csv            same-listing price change (supply-panel branch)
  data/processed/cc_listing_survival.csv                    Common Crawl survival per crawl
  data/processed/hotel_price_monitor_monthly.csv            CPI lodging y/y, BEA hotel price y/y (monthly to Jul 2026)
  data/raw/bea/bea_pce_travel_monthly_2015_2026.csv         BEA hotels nominal spend
  scratch/08/fred_*.csv                                     fresh FRED keyless pulls (DTWEXBGS, DEXUSEU, AIRRPMTSID11, ICSA, CUSR0000SEHB)
Writes data/processed/overnight/08_*.csv: 08_panel_quarterly (aligned quarterly panel), 08_trends_quarterly_features,
  08_feature_tests_all + per-family 08_{trends,backlog,eurostat,ia}_tests, 08_test_scoreboard (tests run / flagged /
  beat-naive by family), 08_{demand,demand_index_p22,supply,price}_index_quarterly, 08_index_backtests,
  08_survivor_robustness + 08_survivor_wf_path (per-quarter walk-forward path and jackknife for the pairs that
  survive), 08_q3_2026_nowcast, 08_q3_2026_components, 08_q3_2026_guide_reconciliation.
  Figure: analysis/figures/overnight/08_indexes_vs_kpis.png.

Test design (same for every feature): window 2022Q1..2026Q2 (post-normalisation, n <= 18). Leave-one-out OLS
RMSE and a walk-forward from 2023Q1 with an expanding window (first fit on 2022Q1..2022Q4, n_train >= 4),
each against naive last-quarter (y[t-1]), prior-year (y[t-4]) and an AR(1) refit on the same expanding window.
Sign accuracy = share of walk-forward quarters where the predicted change from y[t-1] has the actual sign.
"""
from pathlib import Path
import warnings, itertools
import numpy as np, pandas as pd
from scipy import stats
from scipy.optimize import nnls

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data/processed"; OUT = PROC / "overnight"; FIG = ROOT / "analysis/figures/overnight"
SCR = Path(r"C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb\fe93ae72-a37b-4547-991f-690c32a0f6a0\scratchpad\08")
OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
WIN0, WIN1, WF0 = pd.Period("2022Q1"), pd.Period("2026Q2"), pd.Period("2023Q1")
TARGETS = ["nights_yoy", "gbv_yoy", "adr_yoy", "rev_yoy", "na_nights_band", "emea_nights_band"]

def qp(s):  # '1Q21' -> Period 2021Q1
    s = str(s); return pd.Period(f"20{s[-2:]}Q{s[0]}")

def yoy(s, k=4): return (s / s.shift(k) - 1) * 100

# ----------------------------------------------------------------------------- targets
def targets():
    k = pd.read_csv(PROC / "abnb_driver_history_quarterly.csv")
    k["q"] = k["quarter"].map(qp); k = k.set_index("q").sort_index()
    t = pd.DataFrame(index=k.index)
    t["nights_yoy"] = k["nights_m_yoy_pct"]; t["gbv_yoy"] = k["gbv_musd_yoy_pct"]
    t["adr_yoy"] = k["adr_yoy_pct"]; t["rev_yoy"] = k["revenue_musd_yoy_pct"]
    p3 = pd.read_csv(PROC / "predictive/03_quarterly_panel.csv"); p3["q"] = pd.PeriodIndex(p3["quarter"], freq="Q")
    p3 = p3.set_index("q")
    t["adr_exfx_yoy"] = p3["adr_exfx_yoy"]; t["adr_fx_effect"] = p3["adr_fx_effect"]
    # regional nights growth as stated in the letters (bands coded to midpoints: low-single 2, mid-single 5,
    # high-single 8, low-double 11, mid-teens 15, high-teens 18); source: data/raw/letters/<q>_*.htm regional highlights
    na = {"2024Q4": 5, "2025Q1": 2, "2025Q2": 2, "2025Q3": 5, "2025Q4": 5, "2026Q1": 8, "2026Q2": 8}
    emea = {"2022Q3": 20, "2022Q4": 25, "2023Q1": 21, "2024Q4": 11, "2025Q1": 5, "2025Q2": 5, "2025Q3": 5,
            "2025Q4": 8, "2026Q1": 5, "2026Q2": 8}
    t["na_nights_band"] = pd.Series({pd.Period(k_): v for k_, v in na.items()})
    t["emea_nights_band"] = pd.Series({pd.Period(k_): v for k_, v in emea.items()})
    return t

# ----------------------------------------------------------------------------- features
def qavg_yoy_from_monthly(s, name):
    """s: monthly Series indexed by Timestamp. Quarter average level -> y/y %. Partial last quarter kept."""
    q = s.groupby(s.index.to_period("Q")).mean()
    return yoy(q).rename(name)

def trends_features():
    f = OUT / "08_trends_weekly.csv"
    if not f.exists(): return pd.DataFrame(), pd.DataFrame()
    w = pd.read_csv(f, parse_dates=["date"]).drop_duplicates(["geo", "payload", "term", "date"])
    w["q"] = w["date"].dt.to_period("Q")
    feats, levels = {}, []
    for geo in ["US", "WW"]:
        g = w[w.geo == geo]
        p1 = g[g.payload == "P1_peers"].pivot_table(index="q", columns="term", values="value_stitched", aggfunc="mean")
        if p1.empty: continue
        p2 = g[g.payload == "P2_category"].pivot_table(index="q", columns="term", values="value_stitched", aggfunc="mean")
        singles = {p: g[g.payload == p].groupby("q")["value_stitched"].mean() for p in
                   ["S_airbnb_near_me", "S_hotels_near_me", "S_vacation_rental"] if (g.payload == p).any()}
        peers = p1[["vrbo", "booking.com", "hotels.com", "expedia"]].sum(axis=1)
        share = p1["airbnb"] / (p1["airbnb"] + peers)
        pre = f"tr_{geo.lower()}_"
        feats[pre + "airbnb_yoy"] = yoy(p1["airbnb"])
        feats[pre + "vrbo_yoy"] = yoy(p1["vrbo"]); feats[pre + "expedia_yoy"] = yoy(p1["expedia"])
        feats[pre + "booking_yoy"] = yoy(p1["booking.com"]); feats[pre + "peers4_yoy"] = yoy(peers)
        feats[pre + "share_airbnb_vs_peers"] = share * 100
        feats[pre + "share_yoy_pts"] = (share - share.shift(4)) * 100
        feats[pre + "airbnb_minus_peers_yoy"] = yoy(p1["airbnb"]) - yoy(peers)
        if not p2.empty and "hotel" in p2:
            feats[pre + "hotel_yoy"] = yoy(p2["hotel"])
            feats[pre + "airbnb_minus_hotel_yoy"] = yoy(p2["airbnb"]) - yoy(p2["hotel"])
        for p, s in singles.items():
            feats[pre + p[2:] + "_yoy"] = yoy(s)
        if "S_airbnb_near_me" in singles and "S_hotels_near_me" in singles:
            feats[pre + "near_me_ratio_yoy"] = yoy(singles["S_airbnb_near_me"] / singles["S_hotels_near_me"])
        lv = p1.add_prefix(pre + "level_"); lv[pre + "level_share"] = share * 100; levels.append(lv)
    F = pd.DataFrame(feats)
    for c in list(F.columns):
        if c.endswith("_yoy") or c.endswith("_yoy_pts"): F[c + "_d1"] = F[c].diff()
    L = pd.concat(levels, axis=1) if levels else pd.DataFrame()
    return F, L

def backlog_features():
    b = pd.read_csv(PROC / "abnb_backlog_indicators.csv"); b["q"] = b["quarter"].map(qp); b = b.set_index("q").sort_index()
    b = b.reindex(pd.period_range(b.index.min(), b.index.max() + 1, freq="Q"))
    F = pd.DataFrame(index=b.index)
    # value at quarter-end t, used as a feature for t+1 (shift 1 = "known at the prior print")
    F["bl_unearned_yoy_lag1"] = b["unearned_fees_musd_yoy_pct"].shift(1)
    F["bl_funds_yoy_lag1"] = b["funds_held_musd_yoy_pct"].shift(1)
    F["bl_unearned_to_next_rev_lag1"] = b["unearned_to_next_q_revenue"].shift(1)
    # seasonally adjusted: ratio of unearned fees to the *same quarter last year* is already the y/y; add the
    # ratio to trailing-4Q revenue (level-free) and its y/y
    rev = b["revenue_musd"]; F["bl_unearned_to_ttm_rev_yoy_lag1"] = yoy(b["unearned_fees_musd"] / rev.rolling(4).sum()).shift(1)
    F["bl_funds_to_ttm_rev_yoy_lag1"] = yoy(b["funds_held_musd"] / rev.rolling(4).sum()).shift(1)
    F["bl_unearned_yoy_lag1_d1"] = F["bl_unearned_yoy_lag1"].diff(); F["bl_funds_yoy_lag1_d1"] = F["bl_funds_yoy_lag1"].diff()
    return F

def eurostat_features():
    # use whichever pull runs further: the cached branch file or workstream 10's fresh API pull
    cand = [PROC / "eurostat_platform_nights_monthly.csv", OUT / "10_eurostat_platform_monthly_latest.csv"]
    best, bmax = None, None
    for f in cand:
        if not f.exists(): continue
        d = pd.read_csv(f, parse_dates=["month"]).set_index("month")
        if bmax is None or d.index.max() > bmax: best, bmax = d, d.index.max()
    m = best
    def qsum(col):
        s = m[col].groupby(m.index.to_period("Q")).sum(); c = m[col].groupby(m.index.to_period("Q")).size()
        s = s[c == 3]                                    # complete quarters only
        return s.reindex(pd.period_range(s.index.min(), pd.Period("2026Q3"), freq="Q"))  # contiguous, so shift(1)/(4) align
    q = qsum("eu27_nights")
    F = pd.DataFrame({"eu_platform_yoy_lag0": yoy(q)})
    F["eu_platform_yoy_lag1"] = F["eu_platform_yoy_lag0"].shift(1)  # what is published before the print
    F["eu_platform_yoy_lag1_d1"] = F["eu_platform_yoy_lag1"].diff()
    # first month of the quarter alone (if Eurostat ever moves to monthly release; not currently knowable)
    m1 = m["eu27_nights"][m.index.month.isin([1, 4, 7, 10])]
    F["eu_platform_m1_yoy_lag0"] = yoy(m1.groupby(m1.index.to_period("Q")).sum()).reindex(F.index)
    for c in ["ES", "FR", "IT", "DE"]:
        F[f"eu_{c}_yoy_lag1"] = yoy(qsum(f"{c}_nights")).shift(1)
    F.attrs["last_month_published"] = str(bmax.date())
    return F

def peer_features():
    p = pd.read_csv(PROC / "predictive/02_peer_prints.csv"); p["q"] = pd.PeriodIndex(p["quarter"], freq="Q"); p = p.set_index("q")
    F = pd.DataFrame(index=p.index)
    for c in ["mar_revpar_yoy", "hlt_revpar_yoy", "bkng_room_nights_yoy", "expe_room_nights_yoy"]:
        F["pr_" + c] = pd.to_numeric(p[c], errors="coerce")
    F["pr_hotel_revpar_yoy"] = F[["pr_mar_revpar_yoy", "pr_hlt_revpar_yoy"]].mean(axis=1)
    F["pr_hotel_revpar_yoy_d1"] = F["pr_hotel_revpar_yoy"].diff()
    return F

def macro_features():
    def fred(sid):
        f = SCR / f"fred_{sid}.csv"
        if not f.exists(): return None
        d = pd.read_csv(f, na_values="."); d.columns = ["date", "v"]; d["date"] = pd.to_datetime(d["date"])
        return d.set_index("date")["v"].astype(float)
    F = {}
    usd, eur, rpm, icsa, cpi = (fred(s) for s in ["DTWEXBGS", "DEXUSEU", "AIRRPMTSID11", "ICSA", "CUSR0000SEHB"])
    if usd is not None: F["mx_usd_yoy"] = qavg_yoy_from_monthly(usd.dropna(), "usd")
    if eur is not None: F["mx_eurusd_yoy"] = qavg_yoy_from_monthly(eur.dropna(), "eur")
    if rpm is not None:
        a = qavg_yoy_from_monthly(rpm, "rpm"); F["mx_air_rpm_yoy_lag0"] = a; F["mx_air_rpm_yoy_lag1"] = a.shift(1)
    if icsa is not None: F["mx_claims_yoy"] = qavg_yoy_from_monthly(icsa, "claims")
    if cpi is not None: F["mx_cpi_lodging_yoy"] = qavg_yoy_from_monthly(cpi, "cpi")
    bea = pd.read_csv(ROOT / "data/raw/bea/bea_pce_travel_monthly_2015_2026.csv")
    bea["date"] = pd.to_datetime(bea["date"])
    def bea_series(sub, meas):
        s = bea[(bea["series"].str.contains(sub, case=False)) & (bea["measure"].str.lower().str.startswith(meas))]
        return s.groupby("date")["value"].mean()
    hot_n = bea_series("hotel", "nominal"); hot_p = bea_series("hotel", "price")
    if len(hot_n): F["mx_bea_hotels_nominal_yoy"] = qavg_yoy_from_monthly(hot_n, "bea")
    if len(hot_p): F["mx_bea_hotels_price_yoy"] = qavg_yoy_from_monthly(hot_p, "beap")
    F = pd.DataFrame(F)
    for c in ["mx_usd_yoy", "mx_bea_hotels_nominal_yoy", "mx_air_rpm_yoy_lag1"]:
        if c in F: F[c + "_d1"] = F[c].diff()
    return F

def ia_features():
    y = pd.read_csv(OUT / "08_ia_city_yoy.csv", parse_dates=["dump_date", "yearago_date"])
    y = y[(~y.partial_scope) & (y.days_apart.between(300, 430))].copy()
    y["q"] = y["dump_date"].dt.to_period("Q")
    # one observation per city per quarter (latest dump in the quarter), then cross-city median (chained panel)
    y = y.sort_values("dump_date").groupby(["city", "q"]).tail(1)
    g = y.groupby("q")
    F = pd.DataFrame({
        "ia_reviews_ltm_matched_yoy": g["reviews_ltm_matched_yoy"].median() * 100,
        "ia_reviews_ltm_all_yoy": g["reviews_ltm_all_yoy"].median() * 100,
        "ia_reviews_l30d_matched_yoy": g["reviews_l30d_matched_yoy"].median() * 100,
        "ia_blocked30_matched_yoy_pts": g["blocked_30_matched_yoy_pts"].median() * 100,
        "ia_listings_yoy": g["listings_yoy"].median() * 100,
        "ia_n_cities": g["city"].nunique(),
        "ia_city_list": g["city"].agg(lambda s: "|".join(sorted(s))),
    })
    # fixed 13-city version: only quarters where all 13 are present
    full = F[F.ia_n_cities >= 12]
    F["ia_reviews_ltm_matched_yoy_fixed13"] = full["ia_reviews_ltm_matched_yoy"]
    # regional (US cities vs NA band, EMEA cities vs EMEA band)
    us = y[y.city.isin(["austin", "nashville", "chicago", "los-angeles", "new-orleans", "san-diego", "new-york-city"])]
    em = y[y.city.isin(["paris", "london", "barcelona", "rome"])]
    F["ia_us_reviews_ltm_matched_yoy"] = us.groupby("q")["reviews_ltm_matched_yoy"].median() * 100
    F["ia_us_n"] = us.groupby("q")["city"].nunique()
    F["ia_emea_reviews_ltm_matched_yoy"] = em.groupby("q")["reviews_ltm_matched_yoy"].median() * 100
    F["ia_emea_n"] = em.groupby("q")["city"].nunique()
    # like-for-like price (supply-panel branch), year-ago pairs on one price basis
    l = pd.read_csv(PROC / "inside_airbnb_like_for_like.csv", parse_dates=["date_a", "date_b"])
    l = l[(l.pair_type == "year_ago") & (l.price_comparable == True)] if "year_ago" in set(l.pair_type) else l[(l.price_comparable == True) & (l.days_apart.between(300, 430))]
    l["q"] = l["date_b"].dt.to_period("Q")
    F["ia_lfl_price_yoy"] = l.groupby("q")["lfl_price_chg_median"].median() * 100
    F["ia_lfl_price_n"] = l.groupby("q")["city"].nunique()
    F["ia_reviews_ltm_matched_yoy_d1"] = F["ia_reviews_ltm_matched_yoy"].diff()
    return F

def cc_features():
    c = pd.read_csv(PROC / "cc_listing_survival.csv", parse_dates=["crawl_date"])
    c = c[c.status_informative == True]
    q = c.groupby(c["crawl_date"].dt.to_period("Q"))["survival_share"].mean() * 100
    F = pd.DataFrame({"cc_survival_pct": q}); F["cc_survival_yoy_pts"] = F["cc_survival_pct"] - F["cc_survival_pct"].shift(4)
    return F

# ----------------------------------------------------------------------------- tests
def rmse(a, b): a, b = np.asarray(a, float), np.asarray(b, float); m = ~(np.isnan(a) | np.isnan(b)); return float(np.sqrt(np.mean((a[m] - b[m]) ** 2))) if m.sum() else np.nan

def ols_fit(x, y):
    X = np.column_stack([np.ones(len(x)), x]); beta, *_ = np.linalg.lstsq(X, y, rcond=None); return beta

def loo_rmse(x, y):
    n = len(x); pred = np.full(n, np.nan)
    for i in range(n):
        m = np.arange(n) != i; b = ols_fit(x[m], y[m]); pred[i] = b[0] + b[1] * x[i]
    return rmse(pred, y), pred

def walk_forward(df, xcol, ycol, start=WF0, min_train=4):
    """df indexed by Period with columns xcol, ycol (target) plus full target history for baselines."""
    rows = []
    for t in df.index:
        if t < start or pd.isna(df.at[t, ycol]) or pd.isna(df.at[t, xcol]): continue
        tr = df[(df.index < t)].dropna(subset=[xcol, ycol])
        if len(tr) < min_train: continue
        b = ols_fit(tr[xcol].values, tr[ycol].values); pred = b[0] + b[1] * df.at[t, xcol]
        # baselines: naive last, prior-year, AR(1) expanding on the target history
        y_hist = df[ycol][df.index < t].dropna()
        naive = y_hist.iloc[-1] if len(y_hist) else np.nan
        prior = df[ycol].get(t - 4, np.nan)
        yh = df[ycol][(df.index < t)].dropna()
        if len(yh) >= 4:
            ba = ols_fit(yh.shift(1).dropna().values, yh.iloc[1:].values); ar1 = ba[0] + ba[1] * yh.iloc[-1]
        else: ar1 = naive
        rows.append(dict(q=t, actual=df.at[t, ycol], pred=pred, naive=naive, prior_year=prior, ar1=ar1, n_train=len(tr)))
    return pd.DataFrame(rows)

def test_pair(panel, xcol, ycol, family, available, note="", win0=WIN0, wf0=WF0):
    d = panel.loc[win0:WIN1, [xcol, ycol]].dropna()
    r = dict(family=family, feature=xcol, target=ycol, available_before_print=available, window=f"{win0}..{WIN1}, WF from {wf0}", n=len(d),
             first_q=str(d.index.min()) if len(d) else "", last_q=str(d.index.max()) if len(d) else "")
    if len(d) < 6: r.update(note="n<6"); return r
    x, y = d[xcol].values, d[ycol].values
    pr, pp = stats.pearsonr(x, y); sr, sp = stats.spearmanr(x, y)
    rng = np.random.default_rng(0); perm = np.mean([abs(stats.pearsonr(x, rng.permutation(y))[0]) >= abs(pr) for _ in range(1000)])
    loo, _ = loo_rmse(x, y)
    naive_full = rmse(d[ycol].values[1:], panel[ycol].reindex(d.index).shift(1).values[1:])
    r.update(pearson_r=pr, pearson_p=pp, spearman=sr, perm_p=perm, loo_rmse=loo,
             loo_mean_rmse=rmse(y, [np.mean(np.delete(y, i)) for i in range(len(y))]))
    wf = walk_forward(panel.loc[win0:WIN1], xcol, ycol, start=wf0)
    if len(wf) >= 4:
        r.update(wf_n=len(wf), wf_first=str(wf.q.min()), wf_last=str(wf.q.max()),
                 wf_rmse=rmse(wf.pred, wf.actual), wf_rmse_naive=rmse(wf.naive, wf.actual),
                 wf_rmse_prior_year=rmse(wf.prior_year, wf.actual), wf_rmse_ar1=rmse(wf.ar1, wf.actual))
        r["wf_ratio_vs_naive"] = r["wf_rmse"] / r["wf_rmse_naive"]; r["wf_ratio_vs_ar1"] = r["wf_rmse"] / r["wf_rmse_ar1"]
        r["wf_ratio_vs_prior_year"] = r["wf_rmse"] / r["wf_rmse_prior_year"] if r["wf_rmse_prior_year"] else np.nan
        ch_a = np.sign(wf.actual - wf.naive); ch_p = np.sign(wf.pred - wf.naive); m = (ch_a != 0)
        r["wf_sign_acc"] = float((ch_a[m] == ch_p[m]).mean()) if m.any() else np.nan; r["wf_sign_n"] = int(m.sum())
        r["wf_sign_acc_ar1"] = float((ch_a[m] == np.sign(wf.ar1 - wf.naive)[m]).mean()) if m.any() else np.nan
    r["note"] = note
    return r

# ----------------------------------------------------------------------------- composites
def expanding_z(s, min_n=4):
    out = pd.Series(np.nan, index=s.index)
    for i, t in enumerate(s.index):
        h = s.loc[:t].dropna()
        if len(h) >= min_n and h.std() > 0: out[t] = (s[t] - h.mean()) / h.std()
    return out

def build_index(panel, comps, name, z_start=None):
    """comps: dict col -> sign. Equal-weight mean of point-in-time z-scores of available components.
    z_start: first quarter of the z baseline (default WIN0-4 = 2021Q1). Setting it to 2023Q1 removes the
    2021-22 reopening levels from the expanding mean, which otherwise pins every z at a saturated negative."""
    s0 = (WIN0 - 4) if z_start is None else z_start
    Z = pd.DataFrame({c: expanding_z(panel[c].loc[s0:]) * sgn for c, sgn in comps.items() if c in panel})
    idx = pd.DataFrame(index=Z.index)
    idx[name + "_eq"] = Z.mean(axis=1); idx[name + "_n_components"] = Z.notna().sum(axis=1)
    for c in Z: idx["z_" + c] = Z[c]
    return idx, Z

def nnls_walk_forward(Z, y, start=WF0, min_train=6):
    rows = []
    for t in Z.index:
        if t < start or pd.isna(y.get(t, np.nan)): continue
        tr = pd.concat([Z, y.rename("y")], axis=1).loc[:t - 1].dropna(subset=["y"])
        tr = tr[tr.index >= WIN0]
        keep = [c for c in Z.columns if tr[c].notna().sum() >= min_train]   # components with enough history
        tr = tr.dropna(subset=keep) if keep else tr.iloc[0:0]; Ztr = tr[keep]
        if len(tr) < min_train or not keep: continue
        if Z.loc[t, keep].isna().all(): continue
        ym = tr["y"].mean(); w, _ = nnls(Ztr.values, (tr["y"] - ym).values)
        pred = ym + float(Z.loc[t, keep].fillna(0.0).values @ w)
        rows.append(dict(q=t, actual=y[t], pred=pred, weights="|".join(f"{c}:{v:.2f}" for c, v in zip(Ztr.columns, w) if v > 0)))
    return pd.DataFrame(rows)

def evaluate_index(panel, idx_col, ycol, label, extra=None):
    r = test_pair(panel, idx_col, ycol, "index", "see components", "")
    r.update(index=label, target=ycol); return r

# ----------------------------------------------------------------------------- main
def main():
    T = targets()
    TR, TRL = trends_features()
    EU = eurostat_features()
    parts = [T, backlog_features(), EU, peer_features(), macro_features(), ia_features(), cc_features()]
    if len(TR): parts.append(TR)
    panel = pd.concat(parts, axis=1).sort_index()
    panel = panel.loc[pd.Period("2019Q1"):pd.Period("2026Q3")]
    # FX contribution model (03 note: FX effect on ADR = a + b * USD y/y); refit here on 2022Q2..2026Q2
    d = panel.loc[pd.Period("2022Q2"):WIN1, ["mx_usd_yoy", "adr_fx_effect"]].dropna()
    bfx = ols_fit(d["mx_usd_yoy"].values, d["adr_fx_effect"].values) if len(d) else np.array([0.5, -0.72]); n_fx = len(d)
    panel["px_fx_contribution_fitted"] = bfx[0] + bfx[1] * panel["mx_usd_yoy"]
    panel.index.name = "quarter"
    panel.to_csv(OUT / "08_panel_quarterly.csv")
    if len(TR):
        tq = pd.concat([TR, TRL], axis=1); tq.index.name = "quarter"; tq.to_csv(OUT / "08_trends_quarterly_features.csv")

    tests = []
    # 1. Trends
    if len(TR):
        for c in TR.columns:
            for y in ["nights_yoy", "gbv_yoy", "rev_yoy", "na_nights_band"]:
                tests.append(test_pair(panel, c, y, "trends", "yes: real time (but Google rescales history on each pull)"))
    # 2. Backlog
    for c in [c for c in panel if c.startswith("bl_")]:
        for y in ["rev_yoy", "gbv_yoy", "nights_yoy"]:
            tests.append(test_pair(panel, c, y, "backlog", "yes: prior-quarter balance sheet (10-Q/10-K, same day as the prior print)"))
    # 3. Eurostat
    for c in [c for c in panel if c.startswith("eu_")]:
        av = "no: lag-0 quarter is published ~3 months after quarter end (after the print)" if "lag0" in c else "yes: prior quarter published ~3 months after its end, i.e. before the next print"
        for y in ["emea_nights_band", "nights_yoy", "gbv_yoy", "rev_yoy"]:
            tests.append(test_pair(panel, c, y, "eurostat", av))
    # 4. Inside Airbnb
    for c in [c for c in panel if c.startswith("ia_") and panel[c].dtype != object and not c.endswith("_n") and "n_cities" not in c and "_n" != c[-2:]]:
        ys = ["na_nights_band"] if c.startswith("ia_us") else ["emea_nights_band"] if c.startswith("ia_emea") else ["adr_yoy", "adr_exfx_yoy"] if "price" in c else ["nights_yoy", "gbv_yoy"]
        for y in ys: tests.append(test_pair(panel, c, y, "inside_airbnb", "yes: dump dates precede the print by 1-8 weeks; chained city set (see note)"))
    # 5. macro / peers used in composites (coverage check only; 03 and 02 already tested these)
    for c in ["pr_hotel_revpar_yoy", "mx_bea_hotels_nominal_yoy", "mx_air_rpm_yoy_lag1", "mx_usd_yoy", "mx_cpi_lodging_yoy", "cc_survival_yoy_pts"]:
        if c in panel:
            for y in ["nights_yoy", "adr_yoy"]: tests.append(test_pair(panel, c, y, "component", "see 03 note"))
    # post-2022 window for every pair (2023Q1..2026Q2, n<=14, walk-forward from 2024Q1 trained on 2023)
    post = []
    for r in tests:
        post.append(test_pair(panel, r["feature"], r["target"], r["family"], r["available_before_print"], r.get("note", ""), win0=pd.Period("2023Q1"), wf0=pd.Period("2024Q1")))
    tests = pd.DataFrame(tests + post)
    tests.to_csv(OUT / "08_feature_tests_all.csv", index=False)
    tests[tests.family == "trends"].to_csv(OUT / "08_trends_tests.csv", index=False)
    tests[tests.family == "backlog"].to_csv(OUT / "08_backlog_tests.csv", index=False)
    tests[tests.family == "eurostat"].to_csv(OUT / "08_eurostat_tests.csv", index=False)
    tests[tests.family == "inside_airbnb"].to_csv(OUT / "08_ia_tests.csv", index=False)

    # composites -------------------------------------------------------------
    dem = {"eu_platform_yoy_lag1": 1, "pr_hotel_revpar_yoy": 1, "mx_air_rpm_yoy_lag1": 1, "mx_bea_hotels_nominal_yoy": 1,
           "ia_reviews_ltm_matched_yoy": 1}
    if "tr_us_share_yoy_pts" in panel: dem["tr_us_share_yoy_pts"] = 1
    if "tr_ww_airbnb_yoy" in panel: dem["tr_ww_airbnb_yoy"] = 1
    sup = {"ia_listings_yoy": 1, "cc_survival_yoy_pts": 1}
    prc = {"ia_lfl_price_yoy": 1, "mx_cpi_lodging_yoy": 1, "mx_bea_hotels_price_yoy": 1, "px_fx_contribution_fitted": 1}
    D, ZD = build_index(panel, dem, "demand"); S, ZS = build_index(panel, sup, "supply"); P, ZP = build_index(panel, prc, "price")
    for X, name in [(D, "demand"), (S, "supply"), (P, "price")]:
        X.index.name = "quarter"; X.round(3).to_csv(OUT / f"08_{name}_index_quarterly.csv")
    panel = pd.concat([panel, D[["demand_eq"]], S[["supply_eq"]], P[["price_eq"]]], axis=1)
    # demand index without the not-knowable-at-print components (BEA month 3 arrives ~1 week before; keep) and a
    # variant that drops Inside Airbnb (chained composition)
    D2, _ = build_index(panel, {k: v for k, v in dem.items() if k != "ia_reviews_ltm_matched_yoy"}, "demand_noia")
    panel["demand_noia_eq"] = D2["demand_noia_eq"]
    # z baseline started at 2023Q1: the 2021-22 reopening levels otherwise dominate the expanding mean and
    # pin every component z at a saturated negative, which is what kills the equal-weight index (see note).
    D3, ZD3 = build_index(panel, dem, "demand_p22", z_start=pd.Period("2023Q1"))
    panel["demand_p22_eq"] = D3["demand_p22_eq"]
    D3.index.name = "quarter"; D3.round(3).to_csv(OUT / "08_demand_index_p22_quarterly.csv")
    panel.index.name = "quarter"; panel.to_csv(OUT / "08_panel_quarterly.csv")   # re-write with index columns
    bt = []
    for idx_col, Z, label, ys in [("demand_eq", ZD, "Demand index (equal-weight z)", ["nights_yoy", "gbv_yoy", "rev_yoy"]),
                                  ("demand_p22_eq", ZD3, "Demand index, z baseline from 2023Q1", ["nights_yoy", "gbv_yoy", "rev_yoy"]),
                                  ("demand_noia_eq", None, "Demand index ex Inside Airbnb", ["nights_yoy", "gbv_yoy", "rev_yoy"]),
                                  ("supply_eq", ZS, "Supply index (equal-weight z)", ["nights_yoy", "adr_yoy"]),
                                  ("price_eq", ZP, "Price index (equal-weight z)", ["adr_yoy", "adr_exfx_yoy"]),
                                  ("px_fx_contribution_fitted", None, "FX contribution alone", ["adr_yoy", "adr_fx_effect"]),
                                  ("bl_funds_yoy_lag1", None, "Funds held y/y (lag 1) alone", ["rev_yoy", "gbv_yoy"])]:
        for y in ys:
            r = evaluate_index(panel, idx_col, y, label); r["method"] = "equal-weight z / single"; bt.append(r)
            r = test_pair(panel, idx_col, y, "index", "see components", "", win0=pd.Period("2023Q1"), wf0=pd.Period("2024Q1")); r.update(index=label, method="equal-weight z / single"); bt.append(r)
            if Z is not None:
                nn = nnls_walk_forward(Z, panel[y])
                if len(nn) >= 4:
                    wf = walk_forward(panel.loc[:WIN1], idx_col, y)
                    r2 = dict(index=label, target=y, method="NNLS weights, expanding", wf_n=len(nn), wf_first=str(nn.q.min()), wf_last=str(nn.q.max()),
                              wf_rmse=rmse(nn.pred, nn.actual))
                    mm = wf.set_index("q").reindex(nn.q)
                    r2.update(wf_rmse_naive=rmse(mm.naive, nn.actual.values), wf_rmse_ar1=rmse(mm.ar1, nn.actual.values), wf_rmse_prior_year=rmse(mm.prior_year, nn.actual.values))
                    r2["wf_ratio_vs_naive"] = r2["wf_rmse"] / r2["wf_rmse_naive"]; r2["wf_ratio_vs_ar1"] = r2["wf_rmse"] / r2["wf_rmse_ar1"]
                    ch_a = np.sign(nn.actual.values - mm.naive.values); ch_p = np.sign(nn.pred.values - mm.naive.values); m = ch_a != 0
                    r2["wf_sign_acc"] = float((ch_a[m] == ch_p[m]).mean()) if m.any() else np.nan; r2["wf_sign_n"] = int(m.sum())
                    r2["last_weights"] = nn.weights.iloc[-1]; bt.append(r2)
    bt = pd.DataFrame(bt)
    cols = ["index", "target", "method", "window", "n", "pearson_r", "perm_p", "loo_rmse", "loo_mean_rmse", "wf_n", "wf_first", "wf_last", "wf_rmse", "wf_rmse_naive",
            "wf_rmse_ar1", "wf_rmse_prior_year", "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "wf_ratio_vs_prior_year", "wf_sign_acc", "wf_sign_acc_ar1", "wf_sign_n", "last_weights"]
    bt = bt.reindex(columns=[c for c in cols if c in bt.columns]); bt.to_csv(OUT / "08_index_backtests.csv", index=False)

    # scoreboard: how many tests per family/window, how many flagged, how many actually beat naive walk-forward
    sb = []
    for (fam, win), g in tests.groupby(["family", "window"]):
        ev = g[g.wf_n >= 6]
        sb.append(dict(family=fam, window=win, n_tests=len(g),
                       n_flagged_r05_perm05=int(((g.pearson_r.abs() > 0.5) & (g.perm_p < 0.05)).sum()),
                       n_evaluable_wf=len(ev), n_beat_naive=int((ev.wf_ratio_vs_naive < 1).sum()),
                       n_beat_naive_and_ar1=int(((ev.wf_ratio_vs_naive < 1) & (ev.wf_ratio_vs_ar1 < 1)).sum()),
                       n_beat_naive_by_20pct=int((ev.wf_ratio_vs_naive < 0.8).sum()),
                       best_ratio=float(ev.wf_ratio_vs_naive.min()) if len(ev) else np.nan,
                       best_feature=ev.loc[ev.wf_ratio_vs_naive.idxmin(), "feature"] + " -> " + ev.loc[ev.wf_ratio_vs_naive.idxmin(), "target"] if len(ev) and ev.wf_ratio_vs_naive.notna().any() else ""))
    pd.DataFrame(sb).to_csv(OUT / "08_test_scoreboard.csv", index=False)

    # robustness on the pairs that survived: per-quarter walk-forward path and later-subsample correlation
    rob, path = [], []
    survivors = [("bl_funds_yoy_lag1", "rev_yoy"), ("bl_funds_yoy_lag1", "gbv_yoy"), ("px_fx_contribution_fitted", "adr_fx_effect"),
                 ("mx_usd_yoy", "adr_yoy"), ("pr_hotel_revpar_yoy", "nights_yoy"), ("mx_bea_hotels_nominal_yoy", "nights_yoy"),
                 ("demand_p22_eq", "nights_yoy"), ("ia_reviews_l30d_matched_yoy", "nights_yoy")]
    for x, y in survivors:
        if x not in panel: continue
        wf = walk_forward(panel.loc[pd.Period("2023Q1"):WIN1], x, y, start=pd.Period("2024Q1"))
        for _, r in wf.iterrows():
            path.append(dict(feature=x, target=y, q=str(r.q), actual=r.actual, pred=r.pred, naive=r.naive, ar1=r.ar1,
                             err=r.pred - r.actual, err_naive=r.naive - r.actual, n_train=r.n_train))
        row = dict(feature=x, target=y)
        for lab, w0 in [("2022Q1+", WIN0), ("2023Q1+", pd.Period("2023Q1")), ("2024Q1+", pd.Period("2024Q1")), ("2025Q1+", pd.Period("2025Q1"))]:
            d = panel.loc[w0:WIN1, [x, y]].dropna()
            row[f"r_{lab}"] = stats.pearsonr(d[x], d[y])[0] if len(d) >= 5 else np.nan
            row[f"n_{lab}"] = len(d)
        # jackknife the walk-forward: worst and best RMSE ratio when one WF quarter is dropped
        if len(wf) >= 5:
            ratios = [rmse(wf.pred.drop(i), wf.actual.drop(i)) / rmse(wf.naive.drop(i), wf.actual.drop(i)) for i in wf.index]
            row.update(wf_ratio=rmse(wf.pred, wf.actual) / rmse(wf.naive, wf.actual), wf_ratio_jk_min=min(ratios), wf_ratio_jk_max=max(ratios), wf_n=len(wf))
        rob.append(row)
    pd.DataFrame(rob).to_csv(OUT / "08_survivor_robustness.csv", index=False)
    pd.DataFrame(path).to_csv(OUT / "08_survivor_wf_path.csv", index=False)

    # Q3 2026 nowcast --------------------------------------------------------
    q3 = pd.Period("2026Q3"); now = []
    def fit_pred(xcol, ycol):
        d = panel.loc[pd.Period("2023Q1"):WIN1, [xcol, ycol]].dropna()   # post-normalisation fit
        if len(d) < 6 or pd.isna(panel.at[q3, xcol]): return np.nan, np.nan, len(d)
        b = ols_fit(d[xcol].values, d[ycol].values); resid = d[ycol].values - (b[0] + b[1] * d[xcol].values)
        return b[0] + b[1] * panel.at[q3, xcol], float(np.std(resid, ddof=2)), len(d)
    for xcol, ycol in [("demand_eq", "nights_yoy"), ("demand_noia_eq", "nights_yoy"), ("demand_p22_eq", "nights_yoy"), ("demand_eq", "gbv_yoy"), ("demand_eq", "rev_yoy"),
                       ("eu_platform_yoy_lag1", "emea_nights_band"), ("eu_platform_yoy_lag1", "nights_yoy"),
                       ("bl_funds_yoy_lag1", "rev_yoy"), ("bl_funds_yoy_lag1", "gbv_yoy"), ("px_fx_contribution_fitted", "adr_fx_effect"),
                       ("mx_usd_yoy", "adr_yoy"), ("mx_claims_yoy", "adr_exfx_yoy"), ("price_eq", "adr_yoy")] + \
                      ([("tr_us_share_yoy_pts", "nights_yoy"), ("tr_ww_airbnb_yoy", "nights_yoy"), ("tr_us_airbnb_yoy", "na_nights_band")] if len(TR) else []):
        if xcol not in panel: continue
        p, s, n = fit_pred(xcol, ycol)
        now.append(dict(target=ycol, feature=xcol, feature_q3_value=panel.at[q3, xcol] if xcol in panel else np.nan, point=p, resid_sd=s, n_fit=n,
                        low=p - s, high=p + s, naive_last=panel.at[WIN1, ycol], prior_year=panel.at[pd.Period("2025Q3"), ycol]))
    now = pd.DataFrame(now)
    # mechanical assembly: ADR = ex-FX run-rate + fitted FX contribution; GBV = (1+nights)(1+ADR)-1;
    # revenue = GBV y/y + trailing-4Q mean of (revenue y/y - GBV y/y) (stay-vs-booking timing and hedging)
    fx = float(panel.at[q3, "px_fx_contribution_fitted"]); exfx = float(panel.loc[pd.Period("2025Q3"):WIN1, "adr_exfx_yoy"].mean())
    adr = exfx + fx; gap = float((panel["rev_yoy"] - panel["gbv_yoy"]).loc[pd.Period("2025Q3"):WIN1].mean())
    for nights_pt, lab in [(float(panel.at[WIN1, "nights_yoy"]), "nights = naive last (2Q26)"),
                           (float(now.loc[(now.target == "nights_yoy") & (now.feature == "demand_noia_eq"), "point"].iloc[0]) if (now.target == "nights_yoy").any() else np.nan, "nights = demand index ex-IA (post-22 fit)"),
                           (11.0, "nights = guide (low double digit, 11)")]:
        gbv = ((1 + nights_pt / 100) * (1 + adr / 100) - 1) * 100
        now = pd.concat([now, pd.DataFrame([dict(target="assembly", feature=lab, point=nights_pt, resid_sd=np.nan, n_fit=np.nan,
                          low=np.nan, high=np.nan, adr_exfx_runrate=exfx, fx_contribution=fx, adr_yoy=adr, gbv_yoy=gbv, rev_yoy=gbv + gap, rev_minus_gbv_gap_ttm=gap)])], ignore_index=True)
    # reconcile to the company's own 3Q26 revenue guide ($4,690-4,770m vs 3Q25 actual $4,095m; data/processed/
    # abnb_revenue_guidance_vs_actual.csv). The swing factor is the revenue-minus-GBV gap, which ran -4.2 pp in
    # 3Q25 and +0.8 pp in 2Q26, so the assembly is shown across the observed range of that gap.
    gd = pd.read_csv(PROC / "abnb_revenue_guidance_vs_actual.csv")
    g26 = gd[gd.guided_quarter == "2026Q3"].iloc[0]; a25 = float(gd[gd.guided_quarter == "2025Q3"].actual_musd.iloc[0])
    rec = []
    for nights_pt in [10.34, 11.0, 12.0]:
        gbv = ((1 + nights_pt / 100) * (1 + adr / 100) - 1) * 100
        for gp, glab in [(gap, "trailing-4Q mean (%.2f pp)" % gap), (0.0, "0 pp (as in 2Q26)"), (-4.2, "-4.2 pp (as in 3Q25)")]:
            rec.append(dict(nights_yoy=nights_pt, adr_yoy=adr, gbv_yoy=gbv, rev_minus_gbv_gap=gp, gap_case=glab,
                            rev_yoy=gbv + gp, rev_musd=a25 * (1 + (gbv + gp) / 100),
                            guide_low=g26.guide_low_musd, guide_mid=g26.guide_mid_musd, guide_high=g26.guide_high_musd,
                            guide_mid_implied_rev_yoy=(g26.guide_mid_musd / a25 - 1) * 100,
                            vs_guide_mid_pct=(a25 * (1 + (gbv + gp) / 100) / g26.guide_mid_musd - 1) * 100))
    pd.DataFrame(rec).round(2).to_csv(OUT / "08_q3_2026_guide_reconciliation.csv", index=False)
    now.to_csv(OUT / "08_q3_2026_nowcast.csv", index=False)
    comp = panel.loc[q3, [c for c in panel.columns if c in list(dem) + list(sup) + list(prc) + ["mx_usd_yoy", "mx_eurusd_yoy", "mx_claims_yoy", "bl_funds_yoy_lag1", "bl_unearned_yoy_lag1"]]]
    comp.rename("value_2026Q3_to_date").to_csv(OUT / "08_q3_2026_components.csv")

    # figure ----------------------------------------------------------------
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    w = panel.loc[pd.Period("2022Q1"):q3]; xs = [str(q) for q in w.index]
    def two(ax, a, b, la, lb, title):
        ax.plot(xs, w[a], color="#1f4e79", lw=2, label=la); ax.set_ylabel(la, color="#1f4e79")
        ax2 = ax.twinx(); ax2.plot(xs, w[b], color="#c55a11", lw=1.8, ls="--", label=lb); ax2.set_ylabel(lb, color="#c55a11")
        ax.set_title(title, fontsize=10); ax.tick_params(axis="x", rotation=90, labelsize=7); ax.axhline(0, color="grey", lw=0.5)
    two(axes[0, 0], "nights_yoy", "demand_eq", "ABNB nights y/y, %", "Demand index (z)", "Demand index vs nights y/y")
    two(axes[0, 1], "rev_yoy", "bl_funds_yoy_lag1", "ABNB revenue y/y, %", "Funds held y/y, prior quarter-end, %", "Backlog: funds held (lag 1) vs revenue y/y")
    two(axes[1, 0], "adr_yoy", "price_eq", "ABNB ADR y/y, %", "Price index (z)", "Price index vs ADR y/y")
    if "tr_us_share_yoy_pts" in w: two(axes[1, 1], "nights_yoy", "tr_us_share_yoy_pts", "ABNB nights y/y, %", "US Trends: airbnb share of search, y/y pts", "Google Trends share-of-search vs nights y/y")
    fig.text(0.01, 0.005, "Sources: ABNB shareholder letters; SEC XBRL; Eurostat tour_ce_omr; MAR/HLT 8-Ks; BEA; FRED; Inside Airbnb (CC-BY 4.0); Google Trends. 2026Q3 = quarter to date (6 Sep 2026).", fontsize=7, color="grey")
    fig.tight_layout(); fig.savefig(FIG / "08_indexes_vs_kpis.png", dpi=150); plt.close(fig)

    print("tests run:", len(tests), "| by family:", tests.family.value_counts().to_dict())
    print(bt.round(2).to_string())
    print(now.round(2).to_string())
    print("FX fit: fx_effect = %.2f + %.2f * USD y/y (n=%d)" % (bfx[0], bfx[1], n_fx))
    print("Eurostat last published month:", EU.attrs.get("last_month_published"))
    print(pd.read_csv(OUT / "08_test_scoreboard.csv").to_string())
    print(pd.read_csv(OUT / "08_survivor_robustness.csv").round(2).to_string())

if __name__ == "__main__":
    main()
