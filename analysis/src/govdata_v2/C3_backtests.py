"""C3: walk-forward backtests of the EUROCONTROL daio features against EMEA nights y/y (primary)
and total nights y/y (secondary), through analysis/src/adrq3/I0_protocol.py, on the two govdata
windows. Copy of analysis/src/govdata/V2_backtests.py narrowed to this source; the protocol
(expanding OLS refit strictly before each scored quarter, min_fit=4, RMSE ratio vs naive last
quarter / prior year / AR(1), 1,000-shuffle permutation p, jackknife) is unchanged.

Build C of the GitHub alt-data integration plan, 14 Sep 2026 (compiled with Claude Code).
Pre-registration: docs/revenue-forecast-strategy/05_backtests/C2_eurocontrol-daio.md.

Features: eu40_flt_da_{full,lag1,qtd75,qtd75pit}, eu_core_flt_da_{full,lag1,qtd75,qtd75pit};
sensitivities on W1 only: *_full_s2019 (2022 rows replaced by growth vs 2019), *_full_sdrop
(2022 rows dropped).
Outputs: data/processed/govdata_v2/C_feature_panel.csv, C_backtests.csv, C_readings_3q26.csv,
C_t0_duplicate_check.csv.
Run: python analysis/src/govdata_v2/C3_backtests.py
"""
from __future__ import annotations

import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "analysis", "src", "adrq3"))
import I0_protocol as I0  # noqa: E402

OUT = os.path.join(ROOT, "data", "processed", "govdata_v2")
LAST_Q = "2Q26"
NOW_Q = "3Q26"
WINDOWS = {"2022Q1+": ("1Q22", "1Q23"), "2023Q1+": ("1Q23", "1Q24")}
KNOWABLE = "yes (daily, about 1-day lag; 3Q26 complete by 1 Oct)"
QTD_DAYS = 75


def log(*a):
    print(*a, flush=True)


def qlab(p):  # pandas Period Q -> '3Q26'
    return f"{p.quarter}Q{p.year % 100:02d}"


# ------------------------------------------------------------------ targets (same files as V2)
def targets():
    d = pd.read_csv(os.path.join(ROOT, "data", "processed", "abnb_driver_history_quarterly.csv"))
    t = d.set_index("quarter")["nights_m_yoy_pct"].rename("total_nights_yoy")
    r = pd.read_csv(os.path.join(ROOT, "data", "processed", "overnight", "10_regional_panel_quarterly.csv")).set_index("quarter")
    out = pd.concat([t, r[["emea_nights_yoy_mid"]]], axis=1)
    return out.loc[[q for q in I0.QORDER if q in out.index]]


# ------------------------------------------------------------------ features
def build_features():
    agg = pd.read_csv(os.path.join(OUT, "daio_daily_aggregates.csv"), parse_dates=["entry_date"]).set_index("entry_date").sort_index()
    feats, meta = {}, {}
    pit = pd.read_csv(os.path.join(OUT, "qtd75_pit.csv")) if os.path.exists(os.path.join(OUT, "qtd75_pit.csv")) else None
    for tag, col in [("eu40", "eu40_flt_da"), ("eu_core", "eu_core_flt_da")]:
        s = agg[col]
        q = s.index.to_period("Q")
        full = s.groupby(q).sum()
        ndays = s.groupby(q).size()
        expected = pd.Series([p.end_time.dayofyear - p.start_time.dayofyear + 1 for p in full.index], index=full.index)
        full = full.where(ndays == expected)  # complete quarters only
        yoy = (full / full.shift(4) - 1) * 100
        vs2019 = pd.Series({p: (full[p] / full[pd.Period(f"2019Q{p.quarter}", freq="Q")] - 1) * 100 for p in full.index if p.year >= 2020 and pd.notna(full.get(p))})
        yoy.index = [qlab(p) for p in yoy.index]
        vs2019.index = [qlab(p) for p in vs2019.index]
        name = f"{tag}_flt_da"
        feats[name + "_full"] = yoy
        feats[name + "_lag1"] = yoy.shift(1)
        feats[name + "_vs2019"] = vs2019
        # sensitivity A: 2022 rows replaced by vs-2019 growth; sensitivity B: 2022 rows dropped
        sA = yoy.copy()
        for qq in [k for k in yoy.index if k.endswith("Q22")]:
            sA[qq] = vs2019.get(qq, np.nan)
        feats[name + "_full_s2019"] = sA
        sB = yoy.copy()
        sB[[k for k in yoy.index if k.endswith("Q22")]] = np.nan
        feats[name + "_full_sdrop"] = sB
        # qtd75, current vintage: days 1..75 of each quarter vs the same 75 calendar days a year earlier
        qtd = {}
        for p in full.index:
            q0 = p.start_time.normalize()
            cur = s.reindex(pd.date_range(q0, periods=QTD_DAYS))
            prev = s.reindex(pd.date_range(q0 - pd.DateOffset(years=1), periods=QTD_DAYS))
            if cur.notna().all() and prev.notna().all():
                qtd[qlab(p)] = (cur.sum() / prev.sum() - 1) * 100
        # the live quarter (3Q26) has no complete-quarter row in `full`; add it from the daily data
        for q0 in [pd.Timestamp("2026-07-01")]:
            cur = s.reindex(pd.date_range(q0, periods=QTD_DAYS))
            prev = s.reindex(pd.date_range(q0 - pd.DateOffset(years=1), periods=QTD_DAYS))
            if cur.notna().all() and prev.notna().all():
                qtd[qlab(q0.to_period("Q"))] = (cur.sum() / prev.sum() - 1) * 100
        feats[name + "_qtd75"] = pd.Series(qtd)
        if pit is not None:
            pp = pit.set_index("quarter")[f"{col}_yoy"]
            feats[name + "_qtd75pit"] = pp
        meta[name] = dict(source="eurocontrol_daio", region="EMEA", asset="flights to or from the state (departures plus arrivals), " + ("40 EUROCONTROL states" if tag == "eu40" else "EU27 plus UK, CH, NO"),
                          knowable=KNOWABLE, last=str(agg.index.max().date()))
    panel = pd.DataFrame(feats)
    panel = panel.loc[[q for q in I0.QORDER if q in panel.index]]
    return panel, meta


# ------------------------------------------------------------------ jackknife (copied from V2)
def wf_errors(x, y, start, min_fit=4):
    x = np.asarray(x, float); y = np.asarray(y, float)
    out = []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < min_fit or not np.isfinite(x[t]) or not np.isfinite(y[t]) or not np.isfinite(y[t - 1]):
            continue
        b, a = I0.ols(xs[ok], ys[ok])
        pred = a + b * x[t]
        if not np.isfinite(pred):
            continue
        out.append((t, pred - y[t], y[t - 1] - y[t], b))
    return out


def jackknife(x, y, start):
    e = wf_errors(x, y, start)
    if len(e) < 4:
        return dict(jk_ratio_min=np.nan, jk_ratio_max=np.nan, jk_n_below_1=np.nan)
    ratios = []
    for i in range(len(e)):
        keep = [r for j, r in enumerate(e) if j != i]
        ef = np.array([r[1] for r in keep]); en = np.array([r[2] for r in keep])
        ratios.append(np.sqrt(np.mean(ef ** 2)) / np.sqrt(np.mean(en ** 2)))
    return dict(jk_ratio_min=float(min(ratios)), jk_ratio_max=float(max(ratios)), jk_n_below_1=int(sum(r < 1 for r in ratios)),
                wf_slope_min=float(min(r[3] for r in e)), wf_slope_max=float(max(r[3] for r in e)), wf_first_scored=e[0][0], wf_last_scored=e[-1][0])


def full_slope(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3:
        return np.nan
    return I0.ols(x[m], y[m])[0]


# ------------------------------------------------------------------ T0 duplicate check
def t0_duplicate(panel):
    v = pd.read_csv(os.path.join(ROOT, "data", "processed", "govdata", "V", "V_feature_panel.csv")).set_index("quarter")
    rows = []
    for feat in ["eu_core_flt_da_full", "eu40_flt_da_full"]:
        for held in ["avia_eu27_full", "avia_es_full", "avia_it_full"]:
            if held not in v.columns:
                continue
            for label, lo in [("1Q23 to 4Q25", "1Q23"), ("1Q20 to 4Q25", "1Q20")]:
                labels = [q for q in I0.QORDER if I0.qkey(lo) <= I0.qkey(q) <= I0.qkey("4Q25")]
                d = pd.concat([panel.reindex(labels)[feat], v.reindex(labels)[held]], axis=1).dropna()
                r = np.corrcoef(d.iloc[:, 0], d.iloc[:, 1])[0, 1] if len(d) >= 3 else np.nan
                rows.append(dict(feature=feat, held_series=held, overlap=label, n=len(d), r=r,
                                 duplicate_at_0_97=bool(r > 0.97) if pd.notna(r) else None, duplicate_at_0_90=bool(r > 0.90) if pd.notna(r) else None))
    t0 = pd.DataFrame(rows)
    t0.to_csv(os.path.join(OUT, "C_t0_duplicate_check.csv"), index=False)
    log("\nT0 duplicate check:\n" + t0.to_string(index=False))
    return t0


def main():
    tg = targets()
    panel, meta = build_features()
    both = panel.join(tg, how="outer")
    both = both.loc[[q for q in I0.QORDER if q in both.index]]
    both.to_csv(os.path.join(OUT, "C_feature_panel.csv"), index_label="quarter")
    log(f"panel {both.shape}; features {panel.shape[1]}")
    log(both[[c for c in both.columns if c.endswith(("_full", "_qtd75", "_qtd75pit")) or c.endswith("_yoy") or c.endswith("_mid")]].loc["1Q22":].round(2).to_string())

    t0_duplicate(panel)

    rows = []
    for feat in panel.columns:
        base = feat.split("_flt_da")[0] + "_flt_da"
        m = meta[base]
        vint = feat.replace(base + "_", "")
        know = m["knowable"]
        if vint == "lag1":
            know = "yes (prior quarter already published)"
        elif vint.startswith("qtd75"):
            know = "yes (days 1 to 75 of the quarter, observable about day 76; 3Q26 value = 1 Jul to 13 Sep 2026)"
        for tcol in ["emea_nights_yoy_mid", "total_nights_yoy"]:
            for wname, (w0, wf0) in WINDOWS.items():
                labels = [q for q in I0.QORDER if I0.qkey(w0) <= I0.qkey(q) <= I0.qkey(LAST_Q)]
                x = both.reindex(labels)[feat].values
                y = both.reindex(labels)[tcol].values
                r = I0.score(feat, x, y, labels, wf0, know)
                r.update(target=tcol, window=wname, source=m["source"], region=m["region"], asset=m["asset"], vintage=vint, last_period=m["last"],
                         ols_slope_window=full_slope(x, y), role="primary" if vint in ("full",) else ("sensitivity" if vint.startswith("full_s") or vint == "vs2019" else "reported"))
                if r.get("wf_n"):
                    r.update(jackknife(x, y, labels.index(wf0)))
                    r["wf_first_scored_q"] = labels[r["wf_first_scored"]]
                    r["wf_last_scored_q"] = labels[r["wf_last_scored"]]
                rows.append(r)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUT, "C_backtests.csv"), index=False)
    cols = ["feature", "target", "window", "n", "wf_n", "wf_first_scored_q", "r", "perm_p", "ols_slope_window", "wf_ratio_vs_naive", "wf_ratio_vs_prior", "wf_ratio_vs_ar1", "sign_acc", "jk_ratio_min", "jk_ratio_max", "jk_n_below_1"]
    log("\n" + res[cols].round(3).to_string(index=False))

    # ---------------------------------------------------------------- 3Q26 readings
    rd = []
    for feat in panel.columns:
        if NOW_Q not in panel.index or pd.isna(panel.at[NOW_Q, feat]):
            continue
        v = panel.at[NOW_Q, feat]
        v2 = panel.at[LAST_Q, feat] if LAST_Q in panel.index else np.nan
        for tcol in ["emea_nights_yoy_mid", "total_nights_yoy"]:
            labels = [q for q in I0.QORDER if I0.qkey("1Q23") <= I0.qkey(q) <= I0.qkey(LAST_Q)]
            d = both.reindex(labels)[[feat, tcol]].dropna()
            pred = np.nan
            if len(d) >= 6:
                b, a = I0.ols(d[feat].values, d[tcol].values)
                pred = a + b * v
            bt = res[(res.feature == feat) & (res.target == tcol) & (res.window == "2023Q1+")]
            rd.append(dict(feature=feat, target=tcol, value_2q26=v2, value_3q26=v, delta_pp=v - v2 if pd.notna(v2) else np.nan,
                           naive_3q26=both[tcol].dropna().iloc[-1], insample_pred_3q26=pred,
                           wf_ratio_vs_naive_2023=bt.wf_ratio_vs_naive.iloc[0] if len(bt) else np.nan, wf_n=bt.wf_n.iloc[0] if len(bt) else np.nan,
                           note="in-sample OLS on 1Q23 to 2Q26"))
    rdd = pd.DataFrame(rd)
    rdd.to_csv(os.path.join(OUT, "C_readings_3q26.csv"), index=False)
    log("\n3Q26 readings:\n" + rdd.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
