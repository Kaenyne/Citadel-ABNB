"""
Q3 2026 nowcast, workstream E, step 5: backtest the review-count stays index against the disclosed
quarterly KPIs (nights, GBV, revenue) with the note-08 protocol, and against Eurostat platform
nights monthly as a second reality check with a proper monthly target.

Protocol (research/notes/overnight/08_altdata-index-and-backtests.md section 2)
  expanding-window walk-forward: at each period t the OLS y~x is refit on data strictly before t and
  scored against three baselines refit the same way (naive y[t-1], prior year y[t-4] / y[m-12],
  AR(1)); RMSE ratios below 1 mean the feature helped; 1,000-shuffle permutation p on Pearson r;
  every feature carries a knowable-before-print flag.

Writes data/processed/q3nowcast/E/
  backtest_abnb_quarterly.csv   every feature x target x lag x window test against ABNB KPIs
  backtest_wf_paths.csv         the walk-forward path of the best features
  backtest_eurostat_monthly.csv country-level and EU27 tests against Eurostat platform nights
  backtest_scoreboard.csv       tests run / flagged / beat naive by family

Run: py -3.13 analysis/src/q3nowcast/E5_backtest.py
"""
import itertools, time
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
OUT = WT / "data/processed/q3nowcast/E"
RNG = np.random.default_rng(20260912)

EU_CODE = {"austria": "AT", "belgium": "BE", "czech-republic": "CZ", "denmark": "DK", "france": "FR",
           "germany": "DE", "greece": "EL", "hungary": "HU", "ireland": "IE", "italy": "IT",
           "latvia": "LV", "malta": "MT", "portugal": "PT", "spain": "ES", "sweden": "SE",
           "the-netherlands": "NL", "switzerland": "CH", "norway": "NO"}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0:
        return np.nan, np.nanmean(y)
    b = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    return b, y.mean() - b * x.mean()


def perm_p(x, y, n=1000):
    """1,000-shuffle permutation p on |Pearson r|, vectorised."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 4 or np.std(x) == 0 or np.std(y) == 0:
        return np.nan, np.nan
    r0 = np.corrcoef(x, y)[0, 1]
    idx = RNG.random((n, len(x))).argsort(axis=1)
    xp = x[idx]
    xm = xp - xp.mean(axis=1, keepdims=True)
    ym = y - y.mean()
    denom = np.sqrt((xm ** 2).sum(axis=1) * (ym ** 2).sum())
    r = (xm @ ym) / np.where(denom == 0, np.nan, denom)
    cnt = int(np.nansum(np.abs(r) >= abs(r0)))
    return r0, (cnt + 1) / (n + 1)


def walkforward(x, y, start, season_lag):
    """x, y aligned arrays indexed 0..n-1 in time order. start = first index scored."""
    e_f, e_n, e_p, e_a, sg, ts = [], [], [], [], [], []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < 4 or not np.isfinite(x[t]) or not np.isfinite(y[t]):
            continue
        b, a = ols(xs[ok], ys[ok])
        pred = a + b * x[t]
        if not np.isfinite(pred):
            continue
        if not np.isfinite(y[t - 1]):
            continue
        e_f.append(pred - y[t]); e_n.append(y[t - 1] - y[t])
        e_p.append((y[t - season_lag] - y[t]) if t >= season_lag and np.isfinite(y[t - season_lag]) else np.nan)
        yl, yy = ys[:-1], ys[1:]
        m = np.isfinite(yl) & np.isfinite(yy)
        if m.sum() >= 4:
            b2, a2 = ols(yl[m], yy[m])
            e_a.append(a2 + b2 * y[t - 1] - y[t])
        else:
            e_a.append(np.nan)
        sg.append(np.sign(pred - y[t - 1]) == np.sign(y[t] - y[t - 1]))
        ts.append(t)
    if len(e_f) < 4:
        return None
    r = lambda e: float(np.sqrt(np.nanmean(np.asarray(e, float) ** 2))) if np.isfinite(np.asarray(e, float)).sum() else np.nan
    return dict(wf_n=len(e_f), wf_rmse=r(e_f), wf_rmse_naive=r(e_n), wf_rmse_prior=r(e_p),
                wf_rmse_ar1=r(e_a), wf_ratio_vs_naive=r(e_f) / r(e_n) if r(e_n) else np.nan,
                wf_ratio_vs_prior=r(e_f) / r(e_p) if r(e_p) else np.nan,
                wf_ratio_vs_ar1=r(e_f) / r(e_a) if r(e_a) else np.nan,
                sign_acc=float(np.mean(sg)), wf_first_t=ts[0], wf_last_t=ts[-1],
                _path=(ts, e_f, e_n))


# ---------------------------------------------------------------- ABNB quarterly
def abnb_tests():
    kpi = pd.read_csv(MAIN / "data/processed/abnb_driver_history_quarterly.csv")
    kpi["qi"] = kpi.year * 4 + kpi.q - 1
    targets = {"nights_yoy": "nights_m_yoy_pct", "gbv_yoy": "gbv_musd_yoy_pct",
               "revenue_yoy": "revenue_musd_yoy_pct"}
    # peer booked room nights are an independently measured nights series on the same quarterly grid
    pr = pd.read_csv(MAIN / "data/processed/predictive/02_peer_prints.csv")
    pr["qi"] = pr.quarter.str[:4].astype(int) * 4 + pr.quarter.str[-1].astype(int) - 1
    kpi = kpi.merge(pr[["qi", "bkng_room_nights_yoy", "expe_room_nights_yoy"]], on="qi", how="left")
    targets["bkng_room_nights_yoy"] = "bkng_room_nights_yoy"
    targets["expe_room_nights_yoy"] = "expe_room_nights_yoy"
    qq = pd.read_csv(OUT / "index_quarterly.csv")
    qq["qi"] = qq.year * 4 + qq.q - 1
    feats = {}
    for (reg, meas), g in qq.groupby(["region", "measure"]):
        if meas == "yoy_stable":
            # the stable-listing set is fixed at the 2025 and 2026 dumps, so its history carries a
            # mechanical birth trend (see E4b); it is a one-period read, not a series to backtest
            continue
        for w in ["w_equal", "w_reviews", "w_median"]:
            if g[w].notna().sum() < 8:
                continue
            s = g.set_index("qi")[w].sort_index() * 100.0
            feats[f"{reg}|{meas}|{w}"] = s
    log(f"{len(feats)} quarterly index features")
    rows, paths = [], []
    for fname, s in feats.items():
        for lag in [0, 1]:
            for diff in [False, True]:
                x = s.diff() if diff else s
                x = x.shift(lag)
                for tname, tcol in targets.items():
                    for wname, q0, qwf in [("2022Q1+", 2022 * 4, 2023 * 4),
                                           ("2023Q1+", 2023 * 4, 2024 * 4)]:
                        df = pd.DataFrame({"x": x}).join(kpi.set_index("qi")[tcol].rename("y"), how="inner")
                        df = df[df.index >= q0].dropna().sort_index()
                        if len(df) < 7:
                            continue
                        # require a contiguous index for the lag baselines
                        full = pd.DataFrame(index=range(df.index.min(), df.index.max() + 1)).join(df)
                        xa, ya = full.x.to_numpy(float), full.y.to_numpy(float)
                        r, p = perm_p(df.x.to_numpy(), df.y.to_numpy())
                        sp = pd.Series(df.x.to_numpy()).corr(pd.Series(df.y.to_numpy()), method="spearman")
                        # note 08 protocol: walk forward from 2023Q1 on the wide window and from
                        # 2024Q1 on the post-2022 window
                        start = max(4, int(np.searchsorted(full.index.to_numpy(), qwf)))
                        wf = walkforward(xa, ya, start, 4)
                        d24 = df[df.index >= 2024 * 4]
                        r24 = (np.corrcoef(d24.x, d24.y)[0, 1] if len(d24) >= 4 and
                               d24.x.std() > 0 else np.nan)
                        rec = dict(family="abnb_quarterly", feature=fname, lag=lag,
                                   transform="d1" if diff else "level", target=tname, window=wname,
                                   n=len(df), r=r, perm_p=p, spearman=sp, r_2024q1plus=r24,
                                   first_q=int(df.index.min()), last_q=int(df.index.max()),
                                   point_in_time=False,
                                   available_before_print=("partial" if lag == 0 else "yes"))
                        if wf:
                            pth = wf.pop("_path")
                            rec.update(wf)
                            if wf["wf_ratio_vs_naive"] < 1.0:
                                ts, ef, en = pth
                                for t, a_, b_ in zip(ts, ef, en):
                                    paths.append(dict(feature=fname, lag=lag, target=tname,
                                                      window=wname, qi=int(full.index[t]),
                                                      err_feature=a_, err_naive=b_))
                        rows.append(rec)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "backtest_abnb_quarterly.csv", index=False, encoding="utf-8")
    pd.DataFrame(paths).to_csv(OUT / "backtest_wf_paths.csv", index=False, encoding="utf-8")
    log(f"backtest_abnb_quarterly.csv {len(t)} tests")
    return t


# ---------------------------------------------------------------- Eurostat monthly
def eurostat_tests():
    eu = pd.read_csv(MAIN / "data/processed/eurostat_platform_nights_monthly.csv")
    eu["d"] = pd.to_datetime(eu.month)
    eu["ymi"] = eu.d.dt.year * 12 + eu.d.dt.month - 1
    my = pd.read_csv(OUT / "market_monthly_yoy.csv")
    mv = pd.read_csv(OUT / "market_vintage_monthly.csv")
    lat = mv.sort_values("dump_date").groupby("market_key").dump_date.last().rename("latest")
    my = my.join(lat, on="market_key")
    my = my[my.dump_date == my.latest]
    my = my[my.country.isin(EU_CODE)]
    rows = []
    # country level: our market review counts summed by country. Two constructions: within-vintage
    # (n[m]/n[m-12] inside one dump) and vintage-matched (m from the 2026 dump over m-12 from the
    # 2025 dump, so both sides sit the same distance from their own scrape).
    builds = [("within_vintage", "n_reviews", "n_lag12")]
    if "n_vm_cur" in my.columns:
        builds.append(("vintage_matched", "n_vm_cur", "n_vm_prior"))
    ccs = {}
    for bname, num, den in builds:
        c = my.groupby(["country", "ymi"])[[num, den]].sum().reset_index()
        c = c[c[den] > 0]
        c["rev_yoy"] = (c[num] / c[den] - 1) * 100
        ccs[bname] = c
    for bname, cc in ccs.items():
      for ctry, g in cc.groupby("country"):
          code = EU_CODE[ctry]
          col = f"{code}_nights"
          if col not in eu.columns:
              continue
          e = eu[["ymi", col]].copy()
          e["tgt"] = (e[col] / e[col].shift(12) - 1) * 100
          base = g[["ymi", "rev_yoy"]].merge(e[["ymi", "tgt"]], on="ymi").dropna().sort_values("ymi")
          for wname, m0 in [("2022M1+", 2022 * 12), ("2023M1+", 2023 * 12)]:
              df = base[base.ymi >= m0]
              if len(df) < 12:
                  continue
              full = pd.DataFrame(index=range(df.ymi.min(), df.ymi.max() + 1)).join(df.set_index("ymi"))
              r, p = perm_p(df.rev_yoy.to_numpy(), df.tgt.to_numpy())
              wf = walkforward(full.rev_yoy.to_numpy(float), full.tgt.to_numpy(float),
                               max(8, int(len(full) * 0.45)), 12)
              rec = dict(family="eurostat_country", build=bname, geo=ctry, window=wname, n=len(df), r=r, perm_p=p,
                         first_ym=int(df.ymi.min()), last_ym=int(df.ymi.max()),
                         n_markets=my[my.country == ctry].market_key.nunique())
              if wf:
                  wf.pop("_path")
                  rec.update(wf)
              rows.append(rec)
    # EU27 aggregate from the markets that sit in EU27 member states
    eu27 = {k: v for k, v in EU_CODE.items() if v not in ("CH", "NO")}
    a = my[my.country.isin(eu27)].groupby("ymi")[["n_reviews", "n_lag12"]].sum().reset_index()
    a = a[a.n_lag12 > 0]
    a["rev_yoy"] = (a.n_reviews / a.n_lag12 - 1) * 100
    df = a.merge(eu[["ymi", "eu27_yoy_pct"]].rename(columns={"eu27_yoy_pct": "tgt"}), on="ymi")
    base = df.dropna(subset=["rev_yoy", "tgt"]).sort_values("ymi")
    for wname, m0 in [("2022M1+", 2022 * 12), ("2023M1+", 2023 * 12)]:
        df = base[base.ymi >= m0]
        if len(df) < 12:
            continue
        full = pd.DataFrame(index=range(df.ymi.min(), df.ymi.max() + 1)).join(df.set_index("ymi"))
        r, p = perm_p(df.rev_yoy.to_numpy(), df.tgt.to_numpy())
        wf = walkforward(full.rev_yoy.to_numpy(float), full.tgt.to_numpy(float),
                         max(8, int(len(full) * 0.45)), 12)
        rec = dict(family="eurostat_eu27", geo="EU27", window=wname, n=len(df), r=r, perm_p=p,
                   first_ym=int(df.ymi.min()), last_ym=int(df.ymi.max()),
                   n_markets=my[my.country.isin(eu27)].market_key.nunique())
        if wf:
            wf.pop("_path")
            rec.update(wf)
        rows.append(rec)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "backtest_eurostat_monthly.csv", index=False, encoding="utf-8")
    log(f"backtest_eurostat_monthly.csv {len(t)} tests")
    return t


def scoreboard(a, e):
    rows = []
    for name, t in [("abnb_quarterly", a), ("eurostat_monthly", e)]:
        if t.empty:
            continue
        ev = t[t.get("wf_ratio_vs_naive").notna()] if "wf_ratio_vs_naive" in t else t.iloc[0:0]
        fl = t[(t.r.abs() > 0.5) & (t.perm_p < 0.05)] if "r" in t else t.iloc[0:0]
        beat = ev[ev.wf_ratio_vs_naive < 1]
        rows.append(dict(family=name, tests=len(t), flagged=len(fl), evaluable_wf=len(ev),
                         beat_naive=len(beat),
                         beat_naive_and_ar1=len(beat[beat.wf_ratio_vs_ar1 < 1]) if len(beat) else 0,
                         beat_by_20pct=len(ev[ev.wf_ratio_vs_naive < 0.8]),
                         best_ratio=float(ev.wf_ratio_vs_naive.min()) if len(ev) else np.nan))
    s = pd.DataFrame(rows)
    s.to_csv(OUT / "backtest_scoreboard.csv", index=False, encoding="utf-8")
    print(s.to_string(index=False))
    return s


def robustness():
    """Jackknife the walk-forward ratio one scored quarter at a time, for every feature that beat
    naive on nights. A ratio that only survives because of one quarter is not a result."""
    pth = pd.read_csv(OUT / "backtest_wf_paths.csv")
    if pth.empty:
        return pd.DataFrame()
    rows = []
    for k, g in pth.groupby(["feature", "lag", "target", "window"]):
        ef, en = g.err_feature.to_numpy(), g.err_naive.to_numpy()
        full = np.sqrt((ef ** 2).mean()) / np.sqrt((en ** 2).mean())
        jk = []
        for i in range(len(ef)):
            m = np.ones(len(ef), bool); m[i] = False
            jk.append(np.sqrt((ef[m] ** 2).mean()) / np.sqrt((en[m] ** 2).mean()))
        rows.append(dict(feature=k[0], lag=k[1], target=k[2], window=k[3], wf_n=len(ef),
                         wf_ratio_vs_naive=full, jk_min=min(jk), jk_max=max(jk),
                         jk_max_above_1=bool(max(jk) > 1.0)))
    r = pd.DataFrame(rows).sort_values("wf_ratio_vs_naive")
    r.to_csv(OUT / "backtest_survivor_robustness.csv", index=False, encoding="utf-8")
    log(f"backtest_survivor_robustness.csv {len(r)} rows")
    return r


if __name__ == "__main__":
    a = abnb_tests()
    robustness()
    e = eurostat_tests()
    scoreboard(a, e)
    if not a.empty and "wf_ratio_vs_naive" in a:
        best = a.dropna(subset=["wf_ratio_vs_naive"]).sort_values("wf_ratio_vs_naive").head(15)
        print(best[["feature", "lag", "transform", "target", "window", "n", "r", "perm_p",
                    "wf_n", "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "sign_acc"]].to_string(index=False))
