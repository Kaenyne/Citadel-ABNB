"""
02_peer_readthrough_tests.py - do peer prints (BKNG, EXPE, MAR, HLT) that land before Airbnb's print predict
Airbnb's KPIs, its revenue beat, or its day-1 stock reaction?

Inputs
  data/processed/predictive/02_peer_prints.csv          built by 02_peer_prints_build.py (peer KPIs, dates, reactions)
  data/processed/abnb_quarterly_kpis_from_study.csv      ABNB nights, GBV 1Q21-2Q26 (shareholder letters)
  data/raw/letters/4Q21_d251410dex991.htm                ABNB 2019-2020 quarterly nights and GBV from the Q4 2021 letter's
                                                         history table (parsed if present, else the hardcoded copy below)
  data/processed/abnb_revenue_guidance_vs_actual.csv     revenue actual vs guide midpoint (%), 2021Q4 on
  data/external/abnb_earnings_reactions.csv              ABNB 1-day % and excess vs QQQ per print

Point-in-time rule: a peer signal counts for quarter q only if the peer's 8-K was filed before Airbnb's release for q
(strictly earlier date, or the same date when the peer filed pre-market, i.e. acceptance before 16:00 UTC, since Airbnb
reports after the close). Pairs that fail the rule are dropped, and n is reported for every cell.

Tests (per peer signal x ABNB target, for three samples: all quarters 2021Q1-2026Q2, 2023Q1-2026Q2, and 2024Q1-2026Q2 as a
  robustness check on the 2023Q1 leverage point)
  Pearson r and p, Spearman rho and p, permutation p (1,000 shuffles of the target, two-sided on |r|, seed 0),
  sign concordance (share of quarters where signal and target have the same sign) and change concordance (share of
  consecutive quarters where the signal and the target moved the same way). Benjamini-Hochberg q-values are added
  per sample block because there are many cells.
  Leave-one-out OLS forecast of ABNB nights y/y from each peer signal, scored on the same quarters as the naive
  forecast (prior-quarter ABNB nights y/y), the seasonal naive (nights y/y four quarters earlier), an AR(1) fit
  in LOO, and AR(1) plus the peer signal in LOO.

Outputs
  data/processed/predictive/02_peer_readthrough_results.csv   correlation block
  data/processed/predictive/02_peer_readthrough_loo.csv       forecast comparison block
  data/processed/predictive/02_peer_readthrough_panel.csv     the merged quarter panel the tests run on

Run: python analysis/src/predictive/02_peer_readthrough_tests.py
"""
import html
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
PRED = ROOT / "data" / "processed" / "predictive"
N_PERM = 1000
SEED = 0

# ABNB 2019-2020 quarterly history (nights in millions, GBV in $B) from the Q4 2021 shareholder letter's quarterly
# table (data/raw/letters/4Q21_d251410dex991.htm, "Nights and Experiences Booked" and "Gross Booking Value" rows).
# Re-parsed from the letter when the file is present; this copy is the fallback and is checked against the parse.
ABNB_HIST = {
    "2019Q1": (81.3, 10.0), "2019Q2": (83.9, 9.8), "2019Q3": (85.9, 9.7), "2019Q4": (75.8, 8.5),
    "2020Q1": (57.1, 6.8), "2020Q2": (28.0, 3.2), "2020Q3": (61.8, 8.0), "2020Q4": (46.3, 5.9),
}


def abnb_history_from_letter():
    f = ROOT / "data" / "raw" / "letters" / "4Q21_d251410dex991.htm"
    if not f.exists():
        return None
    s = f.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"</t[dh]>", " | ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", html.unescape(s).replace("\xa0", " "))
    out = {}
    for lab, key in [("Nights and Experiences Booked", 0), ("Gross Booking Value", 1)]:
        for m in re.finditer(lab, s):
            vals = re.findall(r"\$?\s?([\d,]+\.\d)\s?[MB]?", s[m.end(): m.end() + 700])
            if len(vals) >= 12:
                out[key] = [float(v.replace(",", "")) for v in vals[:8]]
                break
    if 0 in out and 1 in out:
        qs = ["2019Q1", "2019Q2", "2019Q3", "2019Q4", "2020Q1", "2020Q2", "2020Q3", "2020Q4"]
        return {q: (out[0][i], out[1][i]) for i, q in enumerate(qs)}
    return None


def qkey(s):
    """'1Q21' -> '2021Q1'"""
    m = re.fullmatch(r"(\d)Q(\d\d)", s)
    return f"20{m.group(2)}Q{m.group(1)}" if m else s


def prev_q(q, k=1):
    y, n = int(q[:4]), int(q[5])
    idx = y * 4 + (n - 1) - k
    return f"{idx // 4}Q{idx % 4 + 1}"


def build_panel():
    peers = pd.read_csv(PRED / "02_peer_prints.csv", dtype={"quarter": str})
    kpi = pd.read_csv(ROOT / "data" / "processed" / "abnb_quarterly_kpis_from_study.csv")
    kpi["quarter"] = kpi["quarter"].map(qkey)
    hist = abnb_history_from_letter()
    if hist:
        for q, v in hist.items():
            assert abs(v[0] - ABNB_HIST[q][0]) < 0.05 and abs(v[1] - ABNB_HIST[q][1]) < 0.05, (q, v, ABNB_HIST[q])
        hist_src = "parsed from data/raw/letters/4Q21_d251410dex991.htm"
    else:
        hist, hist_src = ABNB_HIST, "hardcoded copy of the Q4 2021 letter table (letter file not present)"
    extra = pd.DataFrame([{"quarter": q, "nights_m": v[0], "gbv_b": v[1]} for q, v in hist.items()])
    k = pd.concat([extra, kpi[["quarter", "nights_m", "gbv_b", "revenue_musd"]]], ignore_index=True).sort_values("quarter")
    k = k.set_index("quarter")
    k["abnb_nights_yoy"] = (k["nights_m"] / k["nights_m"].shift(4) - 1) * 100
    k["abnb_gbv_yoy"] = (k["gbv_b"] / k["gbv_b"].shift(4) - 1) * 100
    k["abnb_nights_accel_pp"] = k["abnb_nights_yoy"].diff()
    k["abnb_nights_yoy_prev"] = k["abnb_nights_yoy"].shift(1)
    k["abnb_nights_yoy_prev4"] = k["abnb_nights_yoy"].shift(4)
    k = k.round(2).reset_index()

    guide = pd.read_csv(ROOT / "data" / "processed" / "abnb_revenue_guidance_vs_actual.csv", dtype={"guided_quarter": str})
    guide = guide.rename(columns={"guided_quarter": "quarter", "actual_vs_mid_pct": "abnb_rev_beat_pct"})[["quarter", "abnb_rev_beat_pct"]]
    rx = pd.read_csv(ROOT / "data" / "external" / "abnb_earnings_reactions.csv", dtype={"quarter": str})
    rx = rx.rename(columns={"abnb_1d_pct": "abnb_1d_pct", "excess_1d_pct": "abnb_excess_1d_pct"})[["quarter", "abnb_1d_pct", "abnb_excess_1d_pct"]]

    p = peers.merge(k, on="quarter", how="left").merge(guide, on="quarter", how="left").merge(rx, on="quarter", how="left")

    # point-in-time availability flags
    for tk in ["bkng", "expe", "mar", "hlt"]:
        rd, ac = p[f"{tk}_report_date"], p[f"{tk}_acceptance_utc"].astype(str)
        same_day_premarket = (rd == p["abnb_release_date"]) & (ac.str[:2].astype(float) < 16)
        p[f"{tk}_available"] = (rd < p["abnb_release_date"]) | same_day_premarket
    # composite: mean of BKNG and EXPE room nights y/y when both are available
    both = p["bkng_available"] & p["expe_available"]
    p["ota_room_nights_yoy"] = np.where(both, (p["bkng_room_nights_yoy"] + p["expe_room_nights_yoy"]) / 2, np.nan)
    p["ota_room_nights_accel_pp"] = np.where(both, (p["bkng_room_nights_accel_pp"] + p["expe_room_nights_accel_pp"]) / 2, np.nan)
    p["ota_available"] = both
    return p, hist_src


SIGNALS = [  # (column, availability flag, label)
    ("bkng_room_nights_yoy", "bkng_available", "BKNG room nights y/y"),
    ("bkng_room_nights_accel_pp", "bkng_available", "BKNG room nights accel (pp q/q)"),
    ("bkng_gb_yoy", "bkng_available", "BKNG gross bookings y/y (reported)"),
    ("bkng_gb_yoy_cc", "bkng_available", "BKNG gross bookings y/y (constant currency)"),
    ("bkng_excess_1d_pct", "bkng_available", "BKNG day-1 excess return"),
    ("expe_room_nights_yoy", "expe_available", "EXPE room nights y/y"),
    ("expe_room_nights_accel_pp", "expe_available", "EXPE room nights accel (pp q/q)"),
    ("expe_gb_yoy", "expe_available", "EXPE gross bookings y/y"),
    ("expe_excess_1d_pct", "expe_available", "EXPE day-1 excess return"),
    ("ota_room_nights_yoy", "ota_available", "BKNG+EXPE mean room nights y/y"),
    ("ota_room_nights_accel_pp", "ota_available", "BKNG+EXPE mean room nights accel (pp)"),
    ("mar_revpar_yoy", "mar_available", "MAR worldwide RevPAR y/y"),
    ("mar_revpar_accel_pp", "mar_available", "MAR RevPAR accel (pp q/q)"),
    ("mar_excess_1d_pct", "mar_available", "MAR day-1 excess return"),
    ("hlt_revpar_yoy", "hlt_available", "HLT system-wide RevPAR y/y"),
    ("hlt_revpar_accel_pp", "hlt_available", "HLT RevPAR accel (pp q/q)"),
    ("hlt_excess_1d_pct", "hlt_available", "HLT day-1 excess return"),
]
TARGETS = [
    ("abnb_nights_yoy", "ABNB nights y/y"),
    ("abnb_nights_accel_pp", "ABNB nights accel (pp q/q)"),
    ("abnb_gbv_yoy", "ABNB GBV y/y"),
    ("abnb_rev_beat_pct", "ABNB revenue beat vs guide midpoint (%)"),
    ("abnb_excess_1d_pct", "ABNB day-1 excess return"),
]
SAMPLES = {"2021Q1-2026Q2": "2021Q1", "2023Q1-2026Q2": "2023Q1", "2024Q1-2026Q2": "2024Q1"}


def perm_p(x, y, rng):
    r_obs = np.corrcoef(x, y)[0, 1]
    cnt = 0
    for _ in range(N_PERM):
        r = np.corrcoef(x, rng.permutation(y))[0, 1]
        if abs(r) >= abs(r_obs) - 1e-12:
            cnt += 1
    return (cnt + 1) / (N_PERM + 1)


def bh_q(pvals):
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n)
    running = 1.0
    for rank, i in enumerate(order[::-1], start=0):
        k = n - rank
        running = min(running, p[i] * n / k)
        q[i] = running
    return q


def correlations(panel):
    rows = []
    for sname, start in SAMPLES.items():
        sub = panel[panel["quarter"] >= start]
        rng = np.random.default_rng(SEED)
        for sig, avail, slab in SIGNALS:
            for tgt, tlab in TARGETS:
                d = sub[sub[avail]][["quarter", sig, tgt]].dropna()
                n = len(d)
                row = dict(sample=sname, signal=sig, signal_label=slab, target=tgt, target_label=tlab, n=n,
                           quarters_used=" ".join(d["quarter"]))
                if n >= 5:
                    x, y = d[sig].to_numpy(float), d[tgt].to_numpy(float)
                    pr = stats.pearsonr(x, y)
                    sr = stats.spearmanr(x, y)
                    row.update(pearson_r=round(pr[0], 3), pearson_p=round(pr[1], 4), spearman_rho=round(sr[0], 3),
                               spearman_p=round(sr[1], 4), perm_p=round(perm_p(x, y, rng), 4))
                    nz = (np.sign(x) != 0) & (np.sign(y) != 0)
                    row.update(sign_concord=round(float(np.mean(np.sign(x[nz]) == np.sign(y[nz]))), 2) if nz.sum() else np.nan,
                               sign_n=int(nz.sum()))
                    # change concordance on consecutive quarters actually present
                    qs = d["quarter"].tolist()
                    dx, dy = [], []
                    for i in range(1, n):
                        if prev_q(qs[i]) == qs[i - 1]:
                            dx.append(x[i] - x[i - 1]); dy.append(y[i] - y[i - 1])
                    dx, dy = np.array(dx), np.array(dy)
                    ok = (dx != 0) & (dy != 0)
                    row.update(change_concord=round(float(np.mean(np.sign(dx[ok]) == np.sign(dy[ok]))), 2) if ok.sum() else np.nan,
                               change_n=int(ok.sum()))
                rows.append(row)
    out = pd.DataFrame(rows)
    for sname in SAMPLES:
        m = (out["sample"] == sname) & out["pearson_p"].notna()
        out.loc[m, "pearson_q_bh"] = bh_q(out.loc[m, "pearson_p"]).round(3)
    return out


def loo_ols(X, y):
    """Leave-one-out OLS predictions. X: (n, k) without intercept."""
    n = len(y)
    X1 = np.column_stack([np.ones(n), X])
    pred = np.empty(n)
    for i in range(n):
        m = np.arange(n) != i
        beta, *_ = np.linalg.lstsq(X1[m], y[m], rcond=None)
        pred[i] = X1[i] @ beta
    return pred


def loo_block(panel):
    rows = []
    tgt = "abnb_nights_yoy"
    for sname, start in SAMPLES.items():
        sub = panel[panel["quarter"] >= start]
        for sig, avail, slab in SIGNALS:
            d = sub[sub[avail]][["quarter", sig, tgt, "abnb_nights_yoy_prev", "abnb_nights_yoy_prev4"]].dropna()
            n = len(d)
            row = dict(sample=sname, signal=sig, signal_label=slab, target=tgt, n=n, quarters_used=" ".join(d["quarter"]))
            if n >= 6:
                x, y = d[sig].to_numpy(float), d[tgt].to_numpy(float)
                yp, yp4 = d["abnb_nights_yoy_prev"].to_numpy(float), d["abnb_nights_yoy_prev4"].to_numpy(float)
                preds = {
                    "peer_ols": loo_ols(x[:, None], y),
                    "naive_prior_q": yp,
                    "seasonal_naive": yp4,
                    "ar1": loo_ols(yp[:, None], y),
                    "ar1_plus_peer": loo_ols(np.column_stack([yp, x]), y),
                    "mean_only": np.array([np.delete(y, i).mean() for i in range(n)]),
                }
                for k, p in preds.items():
                    e = p - y
                    row[f"mae_{k}"] = round(float(np.mean(np.abs(e))), 2)
                    row[f"rmse_{k}"] = round(float(np.sqrt(np.mean(e ** 2))), 2)
                row["mae_ratio_peer_vs_naive"] = round(row["mae_peer_ols"] / row["mae_naive_prior_q"], 2)
                row["mae_ratio_ar1peer_vs_ar1"] = round(row["mae_ar1_plus_peer"] / row["mae_ar1"], 2)
                # does adding the peer beat AR(1) on more quarters than not?
                better = np.abs(preds["ar1_plus_peer"] - y) < np.abs(preds["ar1"] - y)
                row["ar1peer_beats_ar1_share"] = round(float(better.mean()), 2)
            rows.append(row)
    return pd.DataFrame(rows)


def main():
    panel, hist_src = build_panel()
    keep = ["quarter", "abnb_release_date", "abnb_reaction_date", "abnb_nights_yoy", "abnb_nights_accel_pp", "abnb_gbv_yoy",
            "abnb_rev_beat_pct", "abnb_1d_pct", "abnb_excess_1d_pct", "abnb_nights_yoy_prev", "abnb_nights_yoy_prev4"]
    for tk in ["bkng", "expe", "mar", "hlt"]:
        keep += [c for c in panel.columns if c.startswith(tk + "_") and c.split("_", 1)[1] in
                 ("report_date", "lead_days", "available", "room_nights_yoy", "room_nights_accel_pp", "gb_yoy", "gb_yoy_cc",
                  "revpar_yoy", "revpar_accel_pp", "excess_1d_pct", "next_q_direction")]
    keep += ["ota_room_nights_yoy", "ota_room_nights_accel_pp", "ota_available"]
    panel[keep].to_csv(PRED / "02_peer_readthrough_panel.csv", index=False)

    corr = correlations(panel)
    corr.to_csv(PRED / "02_peer_readthrough_results.csv", index=False)
    loo = loo_block(panel)
    loo.to_csv(PRED / "02_peer_readthrough_loo.csv", index=False)

    pd.set_option("display.width", 250)
    print("ABNB 2019-2020 history:", hist_src)
    print("\nAvailability (peer print strictly before ABNB's):")
    print(panel[["quarter", "abnb_release_date", "bkng_lead_days", "bkng_available", "expe_lead_days", "expe_available",
                 "mar_lead_days", "mar_available", "hlt_lead_days", "hlt_available"]].to_string(index=False))
    print("\nABNB targets:")
    print(panel[["quarter", "abnb_nights_yoy", "abnb_nights_accel_pp", "abnb_gbv_yoy", "abnb_rev_beat_pct", "abnb_excess_1d_pct"]].to_string(index=False))
    show = ["sample", "signal", "target", "n", "pearson_r", "pearson_p", "pearson_q_bh", "spearman_rho", "spearman_p", "perm_p",
            "sign_concord", "sign_n", "change_concord", "change_n"]
    print("\nCorrelations, sorted by |r| (n >= 5):")
    c = corr.dropna(subset=["pearson_r"]).copy()
    c["abs_r"] = c["pearson_r"].abs()
    print(c.sort_values("abs_r", ascending=False)[show].head(25).to_string(index=False))
    print("\nWeakest:")
    print(c.sort_values("abs_r")[show].head(8).to_string(index=False))
    print("\nLOO forecast of ABNB nights y/y (MAE, pp):")
    print(loo.dropna(subset=["mae_peer_ols"])[["sample", "signal", "n", "mae_peer_ols", "mae_naive_prior_q", "mae_seasonal_naive",
                                                 "mae_ar1", "mae_ar1_plus_peer", "mae_mean_only", "mae_ratio_peer_vs_naive",
                                                 "mae_ratio_ar1peer_vs_ar1", "ar1peer_beats_ar1_share"]].to_string(index=False))


if __name__ == "__main__":
    main()
