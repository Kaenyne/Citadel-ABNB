"""G2: note-08 walk-forward backtest of every external series with quarterly history
against disclosed ABNB nights / GBV / revenue / ADR y/y, then a 3Q26 nowcast from
whatever survives.

Workstream G, Q3 2026 nowcast run. Krishang Surapaneni (compiled with Claude Code).

Protocol (identical to research/notes/overnight/08_altdata-index-and-backtests.md):
  - quarterly y/y target from data/processed/abnb_driver_history_quarterly.csv
  - two windows: 2022Q1-2026Q2 (walk-forward from 2023Q1) and 2023Q1-2026Q2 (WF from 2024Q1)
  - expanding-window walk-forward, OLS refit each quarter on data strictly before t
  - three baselines refit the same way: naive y[t-1], prior year y[t-4], AR(1)
  - 1,000-shuffle permutation p, leave-one-out RMSE
  - every feature labelled with whether it is knowable before the 5 Nov print

Two feature vintages per series:
  *_full  = the whole calendar quarter. Knowable before the 5 Nov print for TSA
            (daily), BLS CPI (Sep print ~13 Oct), NTTO (Sep prelim ~mid Oct),
            INE (Sep release ~3 Nov, tight). Flagged per series.
  *_qtd   = only the part of the quarter observable on day 74 (11 Sep 2026):
            TSA = days 1-74, monthly series = month 1 of the quarter (NTTO, INE)
            or months 1-2 (BLS, which publishes Aug on 11 Sep). This is the
            genuinely actionable-today vintage.
"""
from __future__ import annotations

import os
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MAIN = r"C:\Users\krish\citadel-abnb"
OUT = os.path.join(ROOT, "data", "processed", "q3nowcast", "G")
RAW = os.path.join(OUT, "raw")

WIN1 = pd.Period("2026Q2", "Q")
NOWQ = pd.Period("2026Q3", "Q")
WINDOWS = [(pd.Period("2022Q1", "Q"), pd.Period("2023Q1", "Q")),
           (pd.Period("2023Q1", "Q"), pd.Period("2024Q1", "Q"))]


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------- ABNB targets
def targets():
    d = pd.read_csv(os.path.join(MAIN, "data", "processed", "abnb_driver_history_quarterly.csv"))
    d["q"] = pd.PeriodIndex(d["year"].astype(int).astype(str) + "Q" + d["q"].astype(int).astype(str), freq="Q")
    d = d.set_index("q").sort_index()
    cols = ["nights_m_yoy_pct", "gbv_musd_yoy_pct", "revenue_musd_yoy_pct", "adr_yoy_pct"]
    return d[cols]


# --------------------------------------------------------------- feature builds
def q_of(ts):
    return pd.PeriodIndex(ts, freq="Q")


def yoy(s, k=4):
    return (s / s.shift(k) - 1) * 100


def tsa_features():
    d = pd.read_csv(os.path.join(RAW, "tsa_checkpoint_daily.csv"), parse_dates=["date"])
    d["q"] = q_of(d["date"])
    d["doq"] = d.groupby("q").cumcount() + 1
    # QTD window = 72 days, Jul 1 to Sep 10, exactly what is observable on 11 Sep 2026
    QTD_D = 72
    full = d.groupby("q")["pax"].mean()
    ndays = d.groupby("q").size()
    qlen = pd.Series({q: q.end_time.dayofyear - q.start_time.dayofyear + 1 for q in ndays.index})
    full = full.where(ndays >= qlen)  # drop incomplete calendar quarters
    qtd = d[d.doq <= QTD_D].groupby("q")["pax"].sum()
    nq = d[d.doq <= QTD_D].groupby("q").size()
    qtd = qtd.where(nq == QTD_D)
    out = pd.DataFrame({"tsa_full": yoy(full), "tsa_qtd72": yoy(qtd)})
    out["tsa_full_lag1"] = out["tsa_full"].shift(1)
    return out


def bls_features():
    d = pd.read_csv(os.path.join(RAW, "bls_cpi_travel_monthly.csv"))
    d["per"] = pd.PeriodIndex(d["month"], freq="M")
    d["q"] = pd.PeriodIndex(d["per"]).asfreq("Q")
    d["moq"] = ((pd.PeriodIndex(d["per"]).month - 1) % 3) + 1
    out = pd.DataFrame()
    for sid, tag in [("CUUR0000SEHB", "cpi_lodging_nsa"), ("CUSR0000SEHB", "cpi_lodging_sa"),
                     ("CUSR0000SETG01", "cpi_airfare")]:
        s = d[d.series_id == sid]
        full = s.groupby("q")["value"].mean()
        nf = s.groupby("q").size()
        full = full.where(nf == 3)   # 3Q26 has only Jul and Aug; do not average 2 of 3
        m12 = s[s.moq <= 2].groupby("q")["value"].mean()
        nm = s[s.moq <= 2].groupby("q").size()
        m12 = m12.where(nm == 2)
        out[tag + "_full"] = yoy(full)
        out[tag + "_qtd"] = yoy(m12)
    return out


def ntto_features():
    """Prefer the flattened CSV that G1 writes; the vendor xlsx is not committed."""
    csvp = os.path.join(RAW, "ntto_arrivals_monthly.csv")
    if os.path.exists(csvp):
        d = pd.read_csv(csvp)
        d["per"] = pd.PeriodIndex(d["month"].astype(str), freq="M")
        out = pd.DataFrame()
        for key, tag in [("OVERSEAS", "ntto_overseas"), ("WESTERN EUROPE", "ntto_weurope"),
                         ("TOTAL ALL COUNTRIES", "ntto_total")]:
            s = d[d.region == key].set_index("per")["arrivals"].sort_index()
            s = s[~s.index.duplicated()]
            q = s.groupby(s.index.asfreq("Q")).sum()
            nq = s.groupby(s.index.asfreq("Q")).size()
            q = q.where(nq == 3)
            moq = pd.Series(((s.index.month - 1) % 3) + 1, index=s.index)
            m1 = s[moq == 1]
            m1.index = m1.index.asfreq("Q")
            out[tag + "_full"] = yoy(q)
            out[tag + "_qtd1m"] = yoy(m1)
        return out
    f = os.path.join(RAW, "ntto_monthly_arrivals_2000_present_COR.xlsx")
    d = pd.read_excel(f, sheet_name="Monthly", header=None)
    hdr = d.iloc[0]
    cols = {}
    for i, v in hdr.items():
        if isinstance(v, (pd.Timestamp,)) or hasattr(v, "year"):
            try:
                cols[i] = pd.Period(year=v.year, month=v.month, freq="M")
            except Exception:  # noqa: BLE001
                pass
        elif isinstance(v, str):
            t = v.strip().split("\n")[0]
            if len(t) == 7 and t[4] == "-":
                try:
                    cols[i] = pd.Period(t, freq="M")
                except Exception:  # noqa: BLE001
                    pass
    lab = d.iloc[:, 1].astype(str).str.strip()
    out = pd.DataFrame()
    for key, tag in [("OVERSEAS", "ntto_overseas"), ("WESTERN EUROPE", "ntto_weurope"),
                     ("TOTAL ALL COUNTRIES", "ntto_total")]:
        idx = lab[lab == key].index
        if not len(idx):
            continue
        row = d.loc[idx[0]]
        s = pd.Series({p: pd.to_numeric(row[i], errors="coerce") for i, p in cols.items()}).dropna().sort_index()
        s.index = pd.PeriodIndex(s.index, freq="M")
        q = s.groupby(s.index.asfreq("Q")).sum()
        nq = s.groupby(s.index.asfreq("Q")).size()
        q = q.where(nq == 3)
        moq = pd.Series(((s.index.month - 1) % 3) + 1, index=s.index)
        m1 = s[moq == 1]
        m1.index = m1.index.asfreq("Q")
        out[tag + "_full"] = yoy(q)
        out[tag + "_qtd1m"] = yoy(m1)
    return out


def _ine_q(df, name_contains, tag, qtd_months=1):
    s = df[df["name"].str.strip() == name_contains]
    if s.empty:
        return pd.DataFrame()
    s = s.copy()
    s["per"] = pd.PeriodIndex(s["period"].astype(str), freq="M")
    s = s.dropna(subset=["value"]).set_index("per")["value"].sort_index()
    s = s[~s.index.duplicated()]
    q = s.groupby(s.index.asfreq("Q")).sum()
    nq = s.groupby(s.index.asfreq("Q")).size()
    q = q.where(nq == 3)
    moq = pd.Series(((s.index.month - 1) % 3) + 1, index=s.index)
    p = s[moq <= qtd_months]
    pq = p.groupby(p.index.asfreq("Q")).sum()
    npq = p.groupby(p.index.asfreq("Q")).size()
    pq = pq.where(npq == qtd_months)
    return pd.DataFrame({tag + "_full": yoy(q), tag + "_qtd1m": yoy(pq)})


def spain_features():
    out = pd.DataFrame()
    f = os.path.join(RAW, "ine_frontur_visitors_monthly.csv")
    if os.path.exists(f):
        d = pd.read_csv(f)
        for nm, tag in [("Tourist. National Total. Base data.", "es_frontur_tourists"),
                        ("Total. National Total. Base data.", "es_frontur_visitors")]:
            out = out.join(_ine_q(d, nm, tag), how="outer") if len(out) else _ine_q(d, nm, tag)
    f = os.path.join(RAW, "ine_hotel_overnight_monthly.csv")
    if os.path.exists(f):
        d = pd.read_csv(f)
        for nm, tag in [("National. National. Hotel establishments. Overnight stays. Total.", "es_hotel_nights"),
                        ("National. National. Hotel establishments. Overnight stays. Residents abroad.", "es_hotel_nights_foreign"),
                        ("National. National. Hotel establishments. Travellers. Total.", "es_hotel_travellers")]:
            part = _ine_q(d, nm, tag)
            out = out.join(part, how="outer") if len(out) else part
    return out


def eurostat_features():
    f = os.path.join(RAW, "eurostat_tour_ce_omr_eu27.csv")
    if not os.path.exists(f):
        return pd.DataFrame()
    d = pd.read_csv(f)
    d = d[(d["month"] != "TOTAL") & (d["c_resid"] == "TOTAL") if "c_resid" in d else (d["month"] != "TOTAL")]
    if "indic_to" in d:
        pref = [v for v in ["NGT_SP", "NGTS", "NGT"] if v in set(d["indic_to"])]
        if pref:
            d = d[d["indic_to"] == pref[0]]
    d["per"] = pd.PeriodIndex(d["time"].astype(str) + "-" + d["month"].str.replace("M", "", regex=False), freq="M")
    s = d.groupby("per")["value"].sum().sort_index()
    q = s.groupby(s.index.asfreq("Q")).sum()
    nq = s.groupby(s.index.asfreq("Q")).size()
    q = q.where(nq == 3)
    y = yoy(q)
    return pd.DataFrame({"eu_platform_nights_full": y,
                         "eu_platform_nights_lag1": y.shift(1),
                         "eu_platform_nights_lag2": y.shift(2)})


def peer_features():
    f = os.path.join(MAIN, "data", "processed", "predictive", "02_peer_prints.csv")
    if not os.path.exists(f):
        return pd.DataFrame()
    d = pd.read_csv(f)
    d["q"] = pd.PeriodIndex(d["quarter"], freq="Q")
    d = d.set_index("q").sort_index()
    keep = {"mar_revpar_yoy": "mar_revpar_full", "hlt_revpar_yoy": "hlt_revpar_full",
            "bkng_room_nights_yoy": "bkng_nights_full", "expe_room_nights_yoy": "expe_nights_full"}
    out = d[[c for c in keep if c in d]].rename(columns=keep)
    for c in list(out.columns):
        out[c.replace("_full", "_lag1")] = out[c].shift(1)
    return out


# ------------------------------------------------------- note-08 test machinery
def rmse(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = ~(np.isnan(a) | np.isnan(b))
    return float(np.sqrt(np.mean((a[m] - b[m]) ** 2))) if m.sum() else np.nan


def ols_fit(x, y):
    X = np.column_stack([np.ones(len(x)), x])
    return np.linalg.lstsq(X, y, rcond=None)[0]


def loo_rmse(x, y):
    pr = []
    for i in range(len(x)):
        xi, yi = np.delete(x, i), np.delete(y, i)
        b = ols_fit(xi, yi)
        pr.append(b[0] + b[1] * x[i])
    return rmse(pr, y)


def walk_forward(df, xcol, ycol, start, min_train=4):
    rows = []
    for t in df.index:
        if t < start or pd.isna(df.at[t, ycol]) or pd.isna(df.at[t, xcol]):
            continue
        tr = df[df.index < t].dropna(subset=[xcol, ycol])
        if len(tr) < min_train:
            continue
        b = ols_fit(tr[xcol].values, tr[ycol].values)
        pred = b[0] + b[1] * df.at[t, xcol]
        yh = df[ycol][df.index < t].dropna()
        naive = yh.iloc[-1] if len(yh) else np.nan
        prior = df[ycol].get(t - 4, np.nan)
        if len(yh) >= 4:
            ba = ols_fit(yh.shift(1).dropna().values, yh.iloc[1:].values)
            ar1 = ba[0] + ba[1] * yh.iloc[-1]
        else:
            ar1 = naive
        rows.append(dict(q=t, actual=df.at[t, ycol], pred=pred, naive=naive,
                         prior_year=prior, ar1=ar1, n_train=len(tr)))
    return pd.DataFrame(rows)


KNOWABLE = {  # before the 5 Nov 2026 print
    "tsa": "yes (daily, zero lag)",
    "cpi": "yes (Sep CPI 13 Oct 2026)",
    "ntto": "yes (Sep prelim mid-Oct 2026)",
    "es_": "tight (INE Sep release ~3 Nov 2026)",
    "eu_platform_nights_full": "no (Eurostat runs ~5 months behind)",
    "eu_platform_nights_lag1": "no (2026Q2 EU data not out by 5 Nov)",
    "eu_platform_nights_lag2": "yes (2026Q1 EU published)",
    "mar_revpar_full": "yes (MAR reports ~4 Nov 2026)",
    "hlt_revpar_full": "yes (HLT reports late Oct 2026)",
    "bkng_nights_full": "yes (BKNG reports ~28 Oct 2026)",
    "expe_nights_full": "yes (EXPE reports ~6 Nov, AFTER the print in some years)",
}


def knowable(feat):
    for k, v in KNOWABLE.items():
        if feat.startswith(k):
            return v
    if feat.endswith("_lag1"):
        return "yes (prior quarter already printed)"
    if feat.endswith("_qtd72") or feat.endswith("_qtd") or feat.endswith("_qtd1m"):
        return "yes (observable on 11 Sep 2026)"
    return "unknown"


def test_pair(panel, xcol, ycol, win0, wf0):
    d = panel.loc[win0:WIN1, [xcol, ycol]].dropna()
    r = dict(feature=xcol, target=ycol, window=f"{win0}..{WIN1}", wf_from=str(wf0),
             knowable_before_print=knowable(xcol), n=len(d))
    if len(d) < 6:
        r["note"] = "n<6"
        return r
    x, y = d[xcol].values, d[ycol].values
    pr, pp = stats.pearsonr(x, y)
    sr, _ = stats.spearmanr(x, y)
    rng = np.random.default_rng(0)
    xz = (x - x.mean()) / (x.std() or 1.0)
    hits = 0
    for _ in range(1000):
        yp = rng.permutation(y)
        yz = (yp - yp.mean()) / (yp.std() or 1.0)
        if abs(float(np.dot(xz, yz) / len(x))) >= abs(pr):
            hits += 1
    perm = hits / 1000.0
    r.update(pearson_r=pr, pearson_p=pp, spearman=sr, perm_p=perm,
             loo_rmse=loo_rmse(x, y),
             loo_mean_rmse=rmse(y, [np.mean(np.delete(y, i)) for i in range(len(y))]))
    wf = walk_forward(panel.loc[win0:WIN1], xcol, ycol, start=wf0)
    if len(wf) >= 4:
        r.update(wf_n=len(wf), wf_first=str(wf.q.min()), wf_last=str(wf.q.max()),
                 wf_rmse=rmse(wf.pred, wf.actual), wf_rmse_naive=rmse(wf.naive, wf.actual),
                 wf_rmse_prior_year=rmse(wf.prior_year, wf.actual),
                 wf_rmse_ar1=rmse(wf.ar1, wf.actual))
        r["wf_ratio_vs_naive"] = r["wf_rmse"] / r["wf_rmse_naive"] if r["wf_rmse_naive"] else np.nan
        r["wf_ratio_vs_ar1"] = r["wf_rmse"] / r["wf_rmse_ar1"] if r["wf_rmse_ar1"] else np.nan
        r["wf_ratio_vs_prior_year"] = (r["wf_rmse"] / r["wf_rmse_prior_year"]
                                       if r["wf_rmse_prior_year"] else np.nan)
        ca = np.sign(wf.actual - wf.naive)
        cp = np.sign(wf.pred - wf.naive)
        m = ca != 0
        r["wf_sign_acc"] = float((ca[m] == cp[m]).mean()) if m.any() else np.nan
        r["wf_sign_n"] = int(m.sum())
    return r


def main():
    tg = targets()
    feats = pd.concat([tsa_features(), bls_features(), ntto_features(),
                       spain_features(), eurostat_features(), peer_features()], axis=1)
    feats = feats.loc[:, ~feats.columns.duplicated()]
    panel = feats.join(tg, how="outer").sort_index()
    panel = panel.loc[pd.Period("2018Q1", "Q"):]
    panel.to_csv(os.path.join(OUT, "G_quarterly_panel.csv"))
    log(f"panel {panel.shape}, features {len([c for c in panel.columns if c not in tg.columns])}")

    rows = []
    fcols = [c for c in panel.columns if c not in tg.columns]
    for win0, wf0 in WINDOWS:
        for x in fcols:
            for y in tg.columns:
                rows.append(test_pair(panel, x, y, win0, wf0))
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUT, "G_backtests_all.csv"), index=False)
    log(f"{len(res)} tests written")

    ev = res[res.get("wf_n", pd.Series(dtype=float)).notna() & (res.get("wf_n", 0) >= 6)].copy()
    beat = ev[ev.wf_ratio_vs_naive < 1].sort_values("wf_ratio_vs_naive")
    log(f"\nevaluable (wf_n>=6): {len(ev)}; beat naive: {len(beat)}; beat by >=20%: {(ev.wf_ratio_vs_naive<0.8).sum()}")
    cols = ["feature", "target", "window", "n", "wf_n", "pearson_r", "perm_p",
            "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "wf_sign_acc", "knowable_before_print"]
    log("\n--- beat naive ---")
    log(beat[cols].to_string(index=False))
    beat[cols].to_csv(os.path.join(OUT, "G_backtest_survivors.csv"), index=False)

    # scoreboard by family
    def fam(f):
        for k, v in [("tsa", "TSA air throughput"), ("cpi", "BLS CPI price"),
                     ("ntto", "NTTO US inbound"), ("es_", "Spain INE"),
                     ("eu_", "Eurostat platform"), ("mar_", "Hotel RevPAR"),
                     ("hlt_", "Hotel RevPAR"), ("bkng_", "OTA room nights"),
                     ("expe_", "OTA room nights")]:
            if f.startswith(k):
                return v
        return "other"

    ev["family"] = ev.feature.map(fam)
    res["family"] = res.feature.map(fam)
    sb = (res.groupby(["family", "window"])
            .agg(tests=("feature", "size"),
                 flagged=("perm_p", lambda s: int(((res.loc[s.index, "perm_p"] < 0.05) &
                                                   (res.loc[s.index, "pearson_r"].abs() > 0.5)).sum())))
            .reset_index())
    ebf = (ev.groupby(["family", "window"])
             .agg(evaluable_wf=("wf_n", "size"),
                  beat_naive=("wf_ratio_vs_naive", lambda s: int((s < 1).sum())),
                  beat_20pct=("wf_ratio_vs_naive", lambda s: int((s < 0.8).sum())),
                  best_ratio=("wf_ratio_vs_naive", "min")).reset_index())
    sb = sb.merge(ebf, on=["family", "window"], how="left")
    sb.to_csv(os.path.join(OUT, "G_backtest_scoreboard.csv"), index=False)
    log("\n--- scoreboard ---")
    log(sb.to_string(index=False))

    # ---------------------------------------------------- 3Q26 nowcast attempt
    nc = []
    latest = panel.loc[NOWQ] if NOWQ in panel.index else None
    for _, r in beat.iterrows():
        x, y, w = r.feature, r.target, r.window
        win0 = pd.Period(w.split("..")[0], "Q")
        xv = panel.at[NOWQ, x] if (NOWQ in panel.index and x in panel) else np.nan
        tr = panel.loc[win0:WIN1, [x, y]].dropna()
        if pd.isna(xv) or len(tr) < 6:
            nc.append(dict(feature=x, target=y, window=w, x_3q26=xv, pred_3q26=np.nan,
                           naive_3q26=panel[y].dropna().iloc[-1],
                           note="feature not observable for 2026Q3" if pd.isna(xv) else "short train"))
            continue
        b = ols_fit(tr[x].values, tr[y].values)
        pred = b[0] + b[1] * xv
        resid = tr[y].values - (b[0] + b[1] * tr[x].values)
        nc.append(dict(feature=x, target=y, window=w, x_3q26=xv, pred_3q26=pred,
                       naive_3q26=panel[y].dropna().iloc[-1],
                       insample_resid_sd=float(np.std(resid, ddof=2)),
                       wf_ratio_vs_naive=r.wf_ratio_vs_naive, wf_n=r.wf_n,
                       knowable=r.knowable_before_print, note="in-sample fit on full window"))
    ncd = pd.DataFrame(nc)
    ncd.to_csv(os.path.join(OUT, "G_nowcast_3q26.csv"), index=False)
    log("\n--- 3Q26 nowcast from survivors ---")
    if len(ncd):
        log(ncd.to_string(index=False))

    # what the features themselves say about 3Q26 (descriptive, no model)
    desc = []
    for c in fcols:
        v = panel.at[NOWQ, c] if NOWQ in panel.index else np.nan
        v2 = panel.at[WIN1, c] if WIN1 in panel.index else np.nan
        desc.append(dict(feature=c, knowable=knowable(c), value_2026Q2=v2, value_2026Q3=v,
                         delta_pp=(v - v2) if pd.notna(v) and pd.notna(v2) else np.nan))
    dd = pd.DataFrame(desc)
    dd.to_csv(os.path.join(OUT, "G_feature_readings_3q26.csv"), index=False)
    # observable-today nowcast: survivors that actually have a 2026Q3 value
    live = ncd[ncd.pred_3q26.notna()].sort_values("wf_ratio_vs_naive")
    live.to_csv(os.path.join(OUT, "G_nowcast_3q26_observable.csv"), index=False)
    if len(live):
        log("\n--- observable-today 3Q26 nowcast (survivors with a 2026Q3 reading) ---")
        log(live.to_string(index=False))
        for tgt in live.target.unique():
            sub = live[live.target == tgt]
            log(f"  {tgt}: n={len(sub)} median {sub.pred_3q26.median():.2f}, "
                f"range {sub.pred_3q26.min():.2f} to {sub.pred_3q26.max():.2f}, "
                f"naive {sub.naive_3q26.iloc[0]:.2f}")
    log("\n--- feature readings, 2026Q2 vs 2026Q3 (y/y %) ---")
    log(dd.dropna(subset=["value_2026Q3"]).to_string(index=False))


if __name__ == "__main__":
    main()

