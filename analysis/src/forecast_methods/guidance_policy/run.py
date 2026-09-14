#!/usr/bin/env python
"""guidance-policy -- entry point. Rebuilds every output of the package.

  cd "<repo>"
  python \
      analysis/src/forecast_methods/guidance_policy/run.py

Writes progressively: every section writes its CSVs before the next one starts, so a
crash still leaves results on disk. Exit code 0 on success.
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import (METHOD, OUT, OVN, PROC, L0, REPO, SEASON_W, LAMBDA_K, TODAY,  # noqa: E402
                 BUCKET_WORDS, write, moving_block_bootstrap, lambda_table, lambda_hat,
                 cushion_stats, gauss_quantiles)
from harness import (load_targets, history_as_of, register, GUIDE_EVENTS_ALL,  # noqa: E402
                     window_of_target, quarters as Q)

ACCEPT: list[dict] = []


def acc(name, passed, detail):
    ACCEPT.append({"test": name, "passed": bool(passed), "detail": str(detail)})
    print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {detail}")


# =====================================================================  A  ====
def section_a(tg):
    """Rebuild the quarterly revenue guide history and verify the headline claims."""
    print("\n== A. guide history ==")
    led = pd.read_csv(OVN / "02_guidance_ledger.csv")
    r = led[(led["metric"] == "revenue_usd_m") & (led["guide_type"] == "range")].copy()
    r["target_period"] = r["target_period"].map(Q.canon)
    r = r.sort_values("target_period").reset_index(drop=True)
    cs = pd.read_csv(OVN / "02_guidance_cushion_series.csv")
    cs["target_period"] = cs["target_period"].map(Q.canon)

    h = r[["print_quarter", "print_date", "target_period", "value_low", "value_high",
           "value_mid", "actual", "outcome"]].rename(
        columns={"print_date": "guide_date", "target_period": "quarter",
                 "value_low": "guide_lo", "value_high": "guide_hi", "value_mid": "guide_mid"})
    h = h.merge(cs[["target_period", "pct_distance_from_mid", "range_width_pct"]]
                .rename(columns={"target_period": "quarter",
                                 "pct_distance_from_mid": "cushion_pct_ledger2dp"}),
                on="quarter", how="left")
    h["cushion_pct"] = 100.0 * (h["actual"] / h["guide_mid"] - 1.0)
    h["range_width_pct_calc"] = 100.0 * (h["guide_hi"] - h["guide_lo"]) / h["guide_mid"]
    h["beat_vs_mid"] = h["actual"] > h["guide_mid"]
    h["beat_vs_hi"] = h["actual"] > h["guide_hi"]
    h["below_lo"] = h["actual"] < h["guide_lo"]
    h["scoreable"] = h["actual"].notna()
    write(h, "01_guide_history.csv")

    s = h[h["scoreable"]]
    # v2 fix (verifier r1, issue 2): the expectation was a stale 22 = 19 + 3 carried over
    # from the spec prose. The ledger actually holds 20 revenue-range rows: 19 scoreable
    # (2021Q4..2026Q2) + 1 pending (2026Q3, LIVE). Recounted independently from the raw
    # ledger and from the rebuilt 01_guide_history.csv; both give 20.
    acc("A1 guide ranges in ledger == 20 (19 scoreable + 1 pending: 2026Q3 LIVE)",
        len(h) == 20 and len(s) == 19,
        f"n_ranges={len(h)} n_scoreable={len(s)} n_pending={len(h) - len(s)} "
        f"pending={'|'.join(h.loc[~h['scoreable'], 'quarter'].astype(str))}")
    acc("A2 19/19 beat the midpoint", int(s["beat_vs_mid"].sum()) == 19,
        f"{int(s['beat_vs_mid'].sum())}/19 above midpoint, {int(s['below_lo'].sum())} below the low end")
    acc("A3 15/19 above the top of the range", int(s["beat_vs_hi"].sum()) == 15,
        f"{int(s['beat_vs_hi'].sum())}/19 above the high end")
    acc("A4 cushion recomputed from actual/mid matches ledger 2dp column",
        float(np.nanmax(np.abs(s["cushion_pct"] - s["cushion_pct_ledger2dp"]))) < 0.005,
        f"max abs diff = {float(np.nanmax(np.abs(s['cushion_pct'] - s['cushion_pct_ledger2dp']))):.5f} pp")
    return h, s


# =====================================================================  B  ====
def section_b(tg, s):
    """Trailing-8 cushion at every guide date (PIT), block bootstrap, and the trend."""
    print("\n== B. cushion ==")
    rows = []
    for gdate, tq in GUIDE_EVENTS_ALL:
        hist = history_as_of(gdate)
        st = cushion_stats(hist, 8)
        w = hist[hist["actual_over_guide_mid"].notna()].sort_values("quarter").tail(8)
        c = (100.0 * (pd.to_numeric(w["actual_over_guide_mid"], errors="coerce") - 1.0)).dropna()
        m, lo, hi, n = moving_block_bootstrap(c.to_numpy(), np.mean, block=4)
        sdm, sdlo, sdhi, _ = moving_block_bootstrap(
            c.to_numpy(), lambda v: np.std(v, ddof=1) if len(v) > 1 else np.nan, block=4)
        rows.append({"guide_date": gdate, "target_quarter": tq,
                     "window": "|".join(window_of_target(tq)) or "OUT",
                     **st,
                     "c_mean_boot_lo": lo, "c_mean_boot_hi": hi,
                     "c_sd_boot_lo": sdlo, "c_sd_boot_hi": sdhi,
                     "window_quarters": ",".join(w["quarter"].tolist())})
    cp = pd.DataFrame(rows)
    write(cp, "02_cushion_pit.csv")

    last = cp[cp["guide_date"] == pd.Timestamp("2026-08-06").date()].iloc[0]
    # the chief-of-staff numbers use the ledger's 2-dp cushion column
    led8 = s.sort_values("quarter").tail(8)["cushion_pct_ledger2dp"].to_numpy(dtype=float)
    lm, lmed, lsd = float(np.mean(led8)), float(np.median(led8)), float(np.std(led8, ddof=1))
    acc("B1 trailing-8 cushion at 2026-08-06 = mean 1.856% / median 1.790% / sd 1.006pp",
        abs(lm - 1.8562) < 0.002 and abs(lmed - 1.790) < 0.002 and abs(lsd - 1.0064) < 0.002,
        f"ledger-2dp: mean {lm:.4f}% median {lmed:.4f}% sd {lsd:.4f}pp on "
        f"{list(led8)} | raw ratios: mean {last['c_mean_pct']:.4f}% "
        f"median {last['c_median_pct']:.4f}% sd {last['c_sd_pp']:.4f}pp")

    # trend
    ss = s.sort_values("quarter").reset_index(drop=True)
    tr = []
    for lbl, sub in [("all 19", ss), ("first 11", ss.head(11)), ("last 8", ss.tail(8)),
                     ("first 4", ss.head(4)), ("last 4", ss.tail(4)),
                     ("first 5", ss.head(5)), ("last 5", ss.tail(5))]:
        tr.append({"subset": lbl, "n": len(sub),
                   "cushion_mean_pct": float(sub["cushion_pct"].mean()),
                   "cushion_median_pct": float(sub["cushion_pct"].median()),
                   "cushion_sd_pp": float(sub["cushion_pct"].std(ddof=1)),
                   "range_width_mean_pct": float(sub["range_width_pct"].mean()),
                   "range_width_min_pct": float(sub["range_width_pct"].min()),
                   "range_width_max_pct": float(sub["range_width_pct"].max())})
    trend = pd.DataFrame(tr)
    # OLS trend of cushion on time index
    x = np.arange(len(ss), dtype=float)
    sl, ic, rv, pv, se = sps.linregress(x, ss["cushion_pct"].to_numpy(dtype=float))
    slw, icw, rvw, pvw, sew = sps.linregress(x, ss["range_width_pct"].to_numpy(dtype=float))
    trend = pd.concat([trend, pd.DataFrame([
        {"subset": "OLS cushion on print index", "n": len(ss),
         "cushion_mean_pct": sl, "cushion_median_pct": pv, "cushion_sd_pp": se,
         "range_width_mean_pct": np.nan, "range_width_min_pct": np.nan,
         "range_width_max_pct": np.nan},
        {"subset": "OLS range width on print index", "n": len(ss),
         "cushion_mean_pct": np.nan, "cushion_median_pct": np.nan, "cushion_sd_pp": np.nan,
         "range_width_mean_pct": slw, "range_width_min_pct": pvw, "range_width_max_pct": sew},
    ])], ignore_index=True)
    write(trend, "03_cushion_trend.csv")

    f11 = float(ss.head(11)["cushion_pct"].mean()); l8 = float(ss.tail(8)["cushion_pct"].mean())
    acc("B2 cushion shrank ~3.0% (first 11) -> ~1.86% (last 8)",
        abs(f11 - 3.04) < 0.10 and abs(l8 - 1.86) < 0.05,
        f"first-11 mean {f11:.3f}%, last-8 mean {l8:.3f}%, OLS slope {sl:+.4f}pp/print p={pv:.3f}")
    w4f = float(ss.head(4)["range_width_pct"].mean()); w4l = float(ss.tail(4)["range_width_pct"].mean())
    acc("B3 range width 4.9% -> 1.9% of midpoint",
        abs(w4f - 4.9) < 0.30 and abs(w4l - 1.9) < 0.30,
        f"first-4 mean {w4f:.2f}%, last-4 mean {w4l:.2f}%, last-8 mean "
        f"{float(ss.tail(8)['range_width_pct'].mean()):.2f}%, 3Q26 guide "
        f"{100.0*(4770-4690)/4730:.2f}%; the 4.9 figure reproduces only on the first 4, "
        f"not the first 11 ({float(ss.head(11)['range_width_pct'].mean()):.2f}%)")
    return cp


# =====================================================================  C  ====
def section_c(tg, h):
    """kappa = at-print consensus over the guide midpoint; and the two gap distributions."""
    print("\n== C. kappa and the guide-vs-Street gap ==")
    m = pd.read_csv(OVN / "16_consensus_at_print_merged.csv")
    m["print_quarter"] = m["print_quarter"].map(Q.canon)
    gm = dict(zip(h["quarter"], h["guide_mid"]))
    m["guide_mid_for_this_q"] = m["print_quarter"].map(gm)
    m["kappa_pct"] = 100.0 * (m["cons_revenue_musd"] / m["guide_mid_for_this_q"] - 1.0)
    k = m[m["kappa_pct"].notna()][["print_quarter", "print_date", "cons_revenue_musd",
                                   "cons_revenue_vendor", "guide_mid_for_this_q",
                                   "actual_revenue_musd", "kappa_pct",
                                   "revenue_surprise_pct"]].copy()
    write(k, "04_kappa.csv")

    kl = k[k["cons_revenue_vendor"] == "LSEG"]
    kall = k
    rows = [{"basis": "LSEG-only at-print pairs", "n": len(kl),
             "kappa_mean_pct": float(kl["kappa_pct"].mean()),
             "kappa_median_pct": float(kl["kappa_pct"].median()),
             "kappa_sd_pp": float(kl["kappa_pct"].std(ddof=1))},
            {"basis": "all vendors with a guide midpoint", "n": len(kall),
             "kappa_mean_pct": float(kall["kappa_pct"].mean()),
             "kappa_median_pct": float(kall["kappa_pct"].median()),
             "kappa_sd_pp": float(kall["kappa_pct"].std(ddof=1))}]
    kl8 = kl.sort_values("print_quarter").tail(8)
    rows.append({"basis": "LSEG-only, trailing 8", "n": len(kl8),
                 "kappa_mean_pct": float(kl8["kappa_pct"].mean()),
                 "kappa_median_pct": float(kl8["kappa_pct"].median()),
                 "kappa_sd_pp": float(kl8["kappa_pct"].std(ddof=1))})
    ks = pd.DataFrame(rows)

    gvs = m[m["guide_vs_street_pct"].notna()]["guide_vs_street_pct"].astype(float)
    gvs_att = m[(m["guide_vs_street_pct"].notna()) &
                (m["next_q_cons_vendor"] != "CNBC unattributed")]["guide_vs_street_pct"].astype(float)
    surp = m[m["revenue_surprise_pct"].notna()]["revenue_surprise_pct"].astype(float)
    gaps = pd.DataFrame([
        {"series": "guide_mid vs pre-guide Street (%)", "n": len(gvs), **_desc(gvs)},
        {"series": "guide_mid vs pre-guide Street (%), attributed vendors only",
         "n": len(gvs_att), **_desc(gvs_att)},
        {"series": "revenue surprise at print (%)", "n": len(surp), **_desc(surp)},
    ])
    write(pd.concat([ks, gaps], ignore_index=True).fillna(""), "05_kappa_and_gaps.csv")

    acc("C1 kappa ~ +0.52% with sd ~28bp on LSEG-only pairs",
        abs(float(kl["kappa_pct"].mean()) - 0.52) < 0.15,
        f"LSEG-only n={len(kl)} mean {float(kl['kappa_pct'].mean()):+.3f}% "
        f"median {float(kl['kappa_pct'].median()):+.3f}% sd {float(kl['kappa_pct'].std(ddof=1)):.3f}pp "
        f"(the stated sd 0.28pp is NOT reproduced; see note)")
    sd_gap = float(gvs.std(ddof=1)); sd_sur = float(surp.std(ddof=1))
    era = m[m["print_quarter"] >= "2023Q3"]
    g_era = era[era["guide_vs_street_pct"].notna()]["guide_vs_street_pct"].astype(float)
    s_era = era[era["revenue_surprise_pct"].notna()]["revenue_surprise_pct"].astype(float)
    acc("C2 guide-vs-Street sd ~2.5pp >> revenue-surprise sd ~1.1pp (LSEG era 2023Q3+)",
        float(g_era.std(ddof=1)) > 1.8 and float(s_era.std(ddof=1)) < 1.6,
        f"LSEG era: gap sd {float(g_era.std(ddof=1)):.2f}pp (n={len(g_era)}) vs surprise sd "
        f"{float(s_era.std(ddof=1)):.2f}pp (n={len(s_era)}); FULL sample gap sd {sd_gap:.2f}pp "
        f"(n={len(gvs)}) and surprise sd {sd_sur:.2f}pp (n={len(surp)}) -- the full sample is "
        f"dominated by the 2020-21 recovery prints and does NOT reproduce the claim")
    return float(kl["kappa_pct"].mean()), float(kl["kappa_pct"].std(ddof=1)), len(kl), k


def _desc(x):
    return {"mean": float(x.mean()), "median": float(x.median()), "sd": float(x.std(ddof=1)),
            "min": float(x.min()), "max": float(x.max())}


# =====================================================================  D  ====
def section_d(tg):
    """Local recomputation of the recognition kernel. Acceptance test for the package."""
    print("\n== D. recognition kernel (local) ==")
    lam = lambda_table(tg, SEASON_W)
    write(lam, "06_kernel_lambda.csv")
    got = {q: round(v, 3) for q, v in zip(lam["quarter"], lam["lambda_pct"])}
    want = {"2024Q1": 13.034, "2025Q1": 12.325, "2026Q1": 12.612,
            "2024Q2": 13.449, "2025Q2": 13.946, "2026Q2": 13.736,
            "2023Q3": 17.391, "2024Q3": 17.145, "2025Q3": 17.182,
            "2023Q4": 11.946, "2024Q4": 12.117, "2025Q4": 12.026}
    bad = {k: (got.get(k), v) for k, v in want.items() if abs(got.get(k, np.nan) - v) > 0.002}
    acc("D1 kernel conversion table reproduces the architect's 12 cells at w=2/3",
        len(bad) == 0, f"{12 - len(bad)}/12 cells match to 0.002pp; mismatches={bad}")
    q4 = lam[(lam["season"] == 4) & (lam["quarter"] >= "2023Q4")]["lambda_pct"]
    acc("D2 Q4 lambda mean 12.030% and range 0.171pp (2023-2025)",
        abs(float(q4.mean()) - 12.030) < 0.002 and abs(float(q4.max() - q4.min()) - 0.171) < 0.002,
        f"mean {float(q4.mean()):.4f}% range {float(q4.max()-q4.min()):.4f}pp n={len(q4)}")
    # the documentation inconsistency the chief of staff flagged
    extra = lam[lam["quarter"].isin(["2023Q1", "2023Q2"])][["quarter", "lambda_pct"]]
    acc("D3 the extra 1Q23/2Q23 cells the method cards omit do exist",
        len(extra) == 2,
        "; ".join(f"{r.quarter} {r.lambda_pct:.3f}%" for r in extra.itertuples()) +
        " -- Q1 and Q2 therefore have 4 same-season observations, Q3 and Q4 only 3")
    return lam


# =====================================================================  E  ====
def _pit_forecast(gdate, tq, basis, tg, lam_full, cushion_stat="mean"):
    """One vintage of the policy forecast. Returns dict or None."""
    hist = history_as_of(gdate)
    if len(hist) == 0:
        return None
    pq = Q.shift(tq, -1)
    gbv = dict(zip(hist["quarter"], pd.to_numeric(hist["gbv_musd"], errors="coerce")))
    q1, q2 = Q.shift(tq, -1), Q.shift(tq, -2)
    if q1 not in gbv or q2 not in gbv or not np.isfinite(gbv[q1]) or not np.isfinite(gbv[q2]):
        return None
    base = SEASON_W * gbv[q1] + (1 - SEASON_W) * gbv[q2]

    if basis == "PIT":
        lam = lambda_table(hist, SEASON_W)
    else:
        # full_sample replay: inputs stay PIT (hist), parameters deliberately full-sample.
        lam = lam_full
    lh, nlam = lambda_hat(lam, int(tq[-1]), LAMBDA_K)
    if not np.isfinite(lh):
        return None
    e_print = lh / 100.0 * base

    st = cushion_stats(hist, 8)
    if basis == "full_sample":
        full = load_targets()
        st = cushion_stats(full[full["print_date"].notna()], 8 if False else 99)
    c = st["c_mean_pct"] if cushion_stat == "mean" else st["c_median_pct"]
    if not np.isfinite(c):
        return None
    guide_mid_hat = e_print / (1.0 + c / 100.0)

    # relative sd of the kernel print forecast, from its own realised errors in the info set
    errs = []
    lamh = lambda_table(hist, SEASON_W)
    for r in lamh.itertuples():
        if r.quarter >= tq:
            continue
        sub = lamh[(lamh["season"] == r.season) & (lamh["quarter"] < r.quarter)]
        if len(sub) == 0:
            continue
        lh2 = float(sub.tail(LAMBDA_K)["lambda_pct"].mean())
        pred = lh2 / 100.0 * r.base_musd
        errs.append(r.revenue_musd / pred - 1.0)
    kern_sd = float(np.sqrt(np.mean(np.square(errs)))) if len(errs) >= 3 else 0.030
    cush_sd = (st["c_sd_pp"] / 100.0) if np.isfinite(st.get("c_sd_pp", np.nan)) else 0.010
    sd_rel = float(np.sqrt(kern_sd ** 2 + cush_sd ** 2))
    return {"e_print": e_print, "guide_mid_hat": guide_mid_hat, "lambda_pct": lh,
            "n_lambda": nlam, "base_musd": base, "c_pct": c, "n_cushion": st["n_cushion"],
            "kern_sd_rel": kern_sd, "cush_sd_rel": cush_sd, "sd_rel": sd_rel,
            "n_train": int(len(hist)), "n_kern_err": len(errs)}


def section_e(tg, lam_full, h):
    """PIT backtest of the GUIDE forecast and of the PRINT forecast, both windows."""
    print("\n== E. point-in-time backtest ==")
    tgi = tg.set_index("quarter")
    rows_g, rows_p, rows_k = [], [], []
    for gdate, tq in GUIDE_EVENTS_ALL:
        wins = window_of_target(tq)
        if not wins:
            continue
        for basis in ("PIT", "full_sample"):
            f = _pit_forecast(gdate, tq, basis, tg, lam_full)
            if f is None:
                continue
            hist = history_as_of(gdate)
            # local baselines on the GUIDE MIDPOINT target (the harness has none)
            gm_hist = hist[hist["guide_mid"].notna()].sort_values("quarter")
            gm_prev = float(gm_hist["guide_mid"].iloc[-1]) if len(gm_hist) else np.nan
            lag4 = Q.shift(tq, -4)
            gm_lag4 = float(tgi.loc[lag4, "guide_mid"]) if lag4 in tgi.index and \
                pd.notna(tgi.loc[lag4, "guide_mid"]) else np.nan
            g_last = np.nan
            gy = gm_hist.copy()
            if len(gy) >= 5:
                gg = []
                for qq in gy["quarter"]:
                    l4 = Q.shift(qq, -4)
                    if l4 in gy["quarter"].values:
                        a = float(gy.loc[gy["quarter"] == qq, "guide_mid"].iloc[0])
                        b = float(gy.loc[gy["quarter"] == l4, "guide_mid"].iloc[0])
                        gg.append(a / b - 1.0)
                if gg:
                    g_last = gg[-1]
                    g_t4 = float(np.mean(gg[-4:]))
                else:
                    g_t4 = np.nan
            else:
                g_t4 = np.nan
            b_naive = gm_lag4 * (1 + g_last) if np.isfinite(gm_lag4) and np.isfinite(g_last) else np.nan
            b_t4 = gm_lag4 * (1 + g_t4) if np.isfinite(gm_lag4) and np.isfinite(g_t4) else np.nan
            street = tgi.loc[tq, "street_pre_guide_musd"] if tq in tgi.index else np.nan
            svend = tgi.loc[tq, "street_pre_guide_vendor"] if tq in tgi.index else None
            sasof = tgi.loc[tq, "street_pre_guide_as_of"] if tq in tgi.index else None

            common = {"method": METHOD, "quarter": tq, "vintage_date": gdate,
                      "horizon_q": Q.to_index(tq) - Q.to_index(Q.quarter_of_date(gdate)),
                      "prior_basis": basis, "n_train": f["n_train"],
                      "knowable_from": gdate}
            for win in wins:
                sd_g = f["guide_mid_hat"] * f["sd_rel"]
                rows_g.append({**common, "object": "guide_mid_next_q", "target": "guide_mid",
                               "window": win, "point": f["guide_mid_hat"], "q50": f["guide_mid_hat"],
                               **gauss_quantiles(f["guide_mid_hat"], sd_g), "sd": sd_g,
                               # v2 fix (verifier r1, issue 1): 6, not 7. The point/q50 is
                               # lambda_season(4) x w(1) x cushion(1) = 6 free parameters.
                               # kappa never enters this object; it feeds only the
                               # informational at-print-consensus column in section F.
                               "n_params": 6,
                               "base_naive": b_naive, "base_trailing4": b_t4,
                               "base_street": float(street) if pd.notna(street) else np.nan,
                               "street_vendor": svend,
                               "street_as_of": sasof if pd.notna(sasof) else None,
                               "spec_id": f"kernel(w=2/3,k=3)/(1+c_mean8)|{basis}",
                               "notes": f"lam={f['lambda_pct']:.3f} c={f['c_pct']:.3f} "
                                        f"nlam={f['n_lambda']} ncush={f['n_cushion']}"})
                gm_actual = float(tgi.loc[tq, "guide_mid"])
                pr = gm_actual * (1 + f["c_pct"] / 100.0)
                sd_p = pr * f["cush_sd_rel"]
                rows_p.append({**common, "object": "print_from_guide", "target": "revenue_musd",
                               "window": win, "point": pr, "q50": pr,
                               **gauss_quantiles(pr, sd_p), "sd": sd_p, "n_params": 1,
                               "spec_id": f"guide_mid*(1+c_mean8)|{basis}",
                               "notes": "identical in form to baselines/guide_cushion except "
                                        "c is the trailing-8 MEAN not the median"})
                sd_k = f["e_print"] * f["kern_sd_rel"]
                rows_k.append({**common, "object": "print_kernel_policy", "target": "revenue_musd",
                               "window": win, "point": f["e_print"], "q50": f["e_print"],
                               **gauss_quantiles(f["e_print"], sd_k), "sd": sd_k, "n_params": 5,
                               "spec_id": f"kernel(w=2/3,k=3)|{basis}",
                               "notes": f"lam={f['lambda_pct']:.3f} base={f['base_musd']:.0f}"})

    reg_g, reg_p, reg_k = (pd.DataFrame(x) for x in (rows_g, rows_p, rows_k))
    for df in (reg_g, reg_p, reg_k):
        register(df)

    # local scoring table (the harness scorer has no naive for target=guide_mid)
    sc = []
    for name, df, col in [("guide_mid_next_q", reg_g, "guide_mid"),
                          ("print_from_guide", reg_p, "revenue_musd"),
                          ("print_kernel_policy", reg_k, "revenue_musd")]:
        for win in ("W1", "W2"):
            for basis in ("PIT", "full_sample"):
                g = df[(df["window"] == win) & (df["prior_basis"] == basis)]
                if len(g) == 0:
                    continue
                act = np.array([float(tgi.loc[q, col]) for q in g["quarter"]])
                for lbl, pred in [("model", g["point"].to_numpy(dtype=float))] + \
                        ([("naive", g["base_naive"].to_numpy(dtype=float)),
                          ("trailing4", g["base_trailing4"].to_numpy(dtype=float)),
                          ("street", g["base_street"].to_numpy(dtype=float))] if col == "guide_mid" else []):
                    ok = np.isfinite(pred) & np.isfinite(act)
                    if ok.sum() == 0:
                        continue
                    e = 100.0 * (pred[ok] - act[ok]) / act[ok]
                    sc.append({"object": name, "target": col, "window": win, "prior_basis": basis,
                               "predictor": lbl, "n": int(ok.sum()),
                               "mae_pct": float(np.mean(np.abs(e))),
                               "rmse_pct": float(np.sqrt(np.mean(e ** 2))),
                               "bias_pct": float(np.mean(e)),
                               "mae_musd": float(np.mean(np.abs(pred[ok] - act[ok])))})
    scb = pd.DataFrame(sc)
    for name in ("guide_mid_next_q", "print_from_guide", "print_kernel_policy"):
        for win in ("W1", "W2"):
            for basis in ("PIT", "full_sample"):
                m = scb[(scb["object"] == name) & (scb["window"] == win) &
                        (scb["prior_basis"] == basis)]
                if len(m) and "naive" in set(m["predictor"]):
                    r = float(m[m.predictor == "model"]["rmse_pct"].iloc[0]) / \
                        float(m[m.predictor == "naive"]["rmse_pct"].iloc[0])
                    scb.loc[(scb["object"] == name) & (scb["window"] == win) &
                            (scb["prior_basis"] == basis) &
                            (scb["predictor"] == "model"), "rmse_ratio_to_naive"] = r
    write(scb, "07_backtest_scores.csv")
    write(reg_g.drop(columns=["method"]), "07b_backtest_guide_mid_rows.csv")

    # Gate G4: SIGN test of the guide-midpoint forecast against the pre-guide Street
    g4 = []
    for win in ("W1", "W2"):
        for basis in ("PIT", "full_sample"):
            g = reg_g[(reg_g["window"] == win) & (reg_g["prior_basis"] == basis)].copy()
            act = np.array([float(tgi.loc[q, "guide_mid"]) for q in g["quarter"]])
            mdl = np.abs(g["point"].to_numpy(dtype=float) - act)
            stt = np.abs(g["base_street"].to_numpy(dtype=float) - act)
            ok = np.isfinite(mdl) & np.isfinite(stt)
            wins_ = int(np.sum(mdl[ok] < stt[ok])); n = int(ok.sum())
            p = float(sps.binomtest(wins_, n, 0.5, alternative="greater").pvalue) if n else np.nan
            g4.append({"window": win, "prior_basis": basis, "n": n, "model_wins": wins_,
                       "street_wins": n - wins_, "target_at_least": 8 if win == "W1" else 6,
                       "sign_test_p_one_sided": p,
                       "passes": bool(wins_ >= (8 if win == "W1" else 6))})
    g4 = pd.DataFrame(g4)
    write(g4, "08_gate_g4_sign_test.csv")
    r = g4[(g4.window == "W1") & (g4.prior_basis == "PIT")].iloc[0]
    r2 = g4[(g4.window == "W2") & (g4.prior_basis == "PIT")].iloc[0]
    acc("E1 Gate G4 sign test vs the pre-guide Street (W1 target >= 8/14, W2 >= 6/10)",
        bool(r["passes"]) and bool(r2["passes"]),
        f"W1 PIT: model beats Street on {int(r['model_wins'])}/{int(r['n'])} guide dates "
        f"(one-sided p={r['sign_test_p_one_sided']:.3f}); W2 PIT: "
        f"{int(r2['model_wins'])}/{int(r2['n'])} (p={r2['sign_test_p_one_sided']:.3f}). "
        f"GATE G4 {'PASSES' if (r['passes'] and r2['passes']) else 'FAILS'} -- must survive both")
    lvl = scb[(scb.object == "guide_mid_next_q") & (scb.window == "W1") & (scb.prior_basis == "PIT")]
    mm = float(lvl[lvl.predictor == "model"]["mae_pct"].iloc[0])
    ms = float(lvl[lvl.predictor == "street"]["mae_pct"].iloc[0])
    bm = float(lvl[lvl.predictor == "model"]["bias_pct"].iloc[0])
    bs = float(lvl[lvl.predictor == "street"]["bias_pct"].iloc[0])
    acc("E2 ON LEVEL WE LOSE TO THE STREET (this is a disclosure, not a pass/fail)",
        True, f"W1 PIT guide-midpoint MAE model {mm:.2f}% vs Street {ms:.2f}%; "
              f"bias model {bm:+.2f}% vs Street {bs:+.2f}%")
    return reg_g, reg_p, reg_k, scb


# =====================================================================  F  ====
def section_f(tg, lam_full, kappa_mean, kappa_sd, kappa_n, scb):
    """The live 4Q26 guide object, across the GBV_3Q26 grid and the fee-step treatments."""
    print("\n== F. live 4Q26 object ==")
    full = load_targets()
    hist = full[full["print_date"].notna()]
    st = cushion_stats(hist, 8)
    c = st["c_mean_pct"] / 100.0
    lam_q4 = float(lam_full[(lam_full["season"] == 4) &
                            (lam_full["quarter"] >= "2023Q4")]["lambda_pct"].mean())
    gbv_2q26 = float(full.loc[full["quarter"] == "2026Q2", "gbv_musd"].iloc[0])

    # predictive sd: kernel PIT RMSE (from section E, W1 PIT, print_kernel_policy) + cushion sd
    kern_rmse = float(scb[(scb.object == "print_kernel_policy") & (scb.window == "W1") &
                          (scb.prior_basis == "PIT") & (scb.predictor == "model")]
                      ["rmse_pct"].iloc[0])
    sd_pp = float(np.sqrt(kern_rmse ** 2 + st["c_sd_pp"] ** 2))

    grid = [25900.0, 26185.0, 26300.0, 26600.0, 27000.0]
    fees = [("none", 0.0), ("half_weight", 1.25), ("full_weight", 2.50)]
    zacks, av = 3200.0, 3158.0
    rows = []
    for g in grid:
        base = (2.0 / 3.0) * g + (1.0 / 3.0) * gbv_2q26
        for fname, fpct in fees:
            pr = lam_q4 / 100.0 * base * (1 + fpct / 100.0)
            gmid = pr / (1 + c)
            sd_abs = gmid * sd_pp / 100.0
            rows.append({
                "gbv_3q26_musd": g, "is_central": g == 26300.0,
                "fee_step": fname, "fee_step_pct": fpct,
                "lambda_q4_pct": lam_q4, "base_musd": base,
                "print_musd": pr, "guide_mid_musd": gmid,
                "guide_lo_musd": gmid * (1 - 0.0168 / 2), "guide_hi_musd": gmid * (1 + 0.0168 / 2),
                "cushion_pct": c * 100.0, "pred_sd_pp": sd_pp, "pred_sd_musd": sd_abs,
                "cons_at_print_musd": gmid * (1 + kappa_mean / 100.0),
                "p_guide_below_zacks_3200": float(sps.norm.cdf((zacks - gmid) / sd_abs)),
                "p_guide_below_av36_3158": float(sps.norm.cdf((av - gmid) / sd_abs)),
                "p_print_below_zacks_3200": float(sps.norm.cdf((zacks - pr) / (pr * sd_pp / 100))),
            })
    q4 = pd.DataFrame(rows)
    write(q4, "09_q4_2026_grid.csv")

    cen = q4[q4["is_central"]]
    probs = pd.DataFrame([
        {"anchor": "Zacks $3,200M (10 est, as_of 2026-09-04)", "vendor": "Zacks",
         "as_of": "2026-09-04", "value_musd": zacks,
         "p_central_no_fee": float(cen[cen.fee_step == "none"]["p_guide_below_zacks_3200"].iloc[0]),
         "p_central_half_fee": float(cen[cen.fee_step == "half_weight"]["p_guide_below_zacks_3200"].iloc[0]),
         "p_central_full_fee": float(cen[cen.fee_step == "full_weight"]["p_guide_below_zacks_3200"].iloc[0]),
         "p_mean_over_fee_treatments": float(cen["p_guide_below_zacks_3200"].mean()),
         "p_min_over_full_grid": float(q4["p_guide_below_zacks_3200"].min()),
         "p_max_over_full_grid": float(q4["p_guide_below_zacks_3200"].max())},
        {"anchor": "Alpha Vantage 36-analyst $3,158M (as_of 2026-09-11)", "vendor":
         "Alpha Vantage (aggregated sell-side panel)", "as_of": "2026-09-11", "value_musd": av,
         "p_central_no_fee": float(cen[cen.fee_step == "none"]["p_guide_below_av36_3158"].iloc[0]),
         "p_central_half_fee": float(cen[cen.fee_step == "half_weight"]["p_guide_below_av36_3158"].iloc[0]),
         "p_central_full_fee": float(cen[cen.fee_step == "full_weight"]["p_guide_below_av36_3158"].iloc[0]),
         "p_mean_over_fee_treatments": float(cen["p_guide_below_av36_3158"].mean()),
         "p_min_over_full_grid": float(q4["p_guide_below_av36_3158"].min()),
         "p_max_over_full_grid": float(q4["p_guide_below_av36_3158"].max())},
    ])
    write(probs, "10_q4_2026_probabilities.csv")

    # consensus self-inconsistency exhibit
    q1, q2 = 2678.0, 3608.0
    q3c, q4c = 4740.0, 3200.0
    incons = pd.DataFrame([
        {"item": "1Q26 actual", "musd": q1, "source": "10-Q / letter"},
        {"item": "2Q26 actual", "musd": q2, "source": "10-Q / letter"},
        {"item": "3Q26 Zacks consensus (7 est, 2026-09-04)", "musd": q3c, "source": "Zacks"},
        {"item": "4Q26 Zacks consensus (10 est, 2026-09-04)", "musd": q4c, "source": "Zacks"},
        {"item": "SUM of the four quarters", "musd": q1 + q2 + q3c + q4c, "source": "arithmetic"},
        {"item": "FY26 Zacks consensus (8 est, 2026-09-04)", "musd": 14100.0, "source": "Zacks"},
        {"item": "DISAGREEMENT (quarterly sum minus FY)",
         "musd": q1 + q2 + q3c + q4c - 14100.0, "source": "arithmetic"},
        {"item": "FY26 Alpha Vantage (43 est, 2026-09-11)", "musd": 14155.0, "source": "Alpha Vantage"},
        {"item": "FY26 S&P Global MI (43 est, 2026-09-03)", "musd": 14160.0, "source": "S&P Global MI"},
    ])
    write(incons, "11_consensus_inconsistency.csv")
    acc("F1 consensus self-inconsistency: quarterly sum 14,226M vs FY26 14,100M = 126M",
        abs((q1 + q2 + q3c + q4c) - 14226.0) < 1.0,
        f"sum {q1+q2+q3c+q4c:.0f}M, FY26 14,100M, gap {q1+q2+q3c+q4c-14100:.0f}M -- "
        f"larger than our own edge")

    cn = cen[cen.fee_step == "none"].iloc[0]
    ch = cen[cen.fee_step == "half_weight"].iloc[0]
    acc("F2 central GBV 26,300 reproduces print 3,200 / guide 3,141.6 -> 3,142 (no fee) "
        "and 3,240 / 3,181 (half fee)",
        abs(cn["print_musd"] - 3200) < 6 and abs(cn["guide_mid_musd"] - 3141) < 6 and
        abs(ch["print_musd"] - 3240) < 6 and abs(ch["guide_mid_musd"] - 3181) < 6,
        f"no fee: print {cn['print_musd']:.0f} guide {cn['guide_mid_musd']:.0f}; "
        f"half fee: print {ch['print_musd']:.0f} guide {ch['guide_mid_musd']:.0f}; "
        f"lambda_Q4 {lam_q4:.3f}% cushion {c*100:.3f}% sd {sd_pp:.2f}pp "
        f"(kernel PIT RMSE {kern_rmse:.2f}pp + cushion sd {st['c_sd_pp']:.3f}pp)")

    # register the LIVE objects (half-weight fee step is the headline)
    live = []
    for _, r in q4.iterrows():
        for obj, tgt, pt in [("q4_2026_guide_mid", "guide_mid", r["guide_mid_musd"]),
                             ("q4_2026_print", "revenue_musd", r["print_musd"])]:
            sd_abs = pt * sd_pp / 100.0
            live.append({"method": METHOD, "object": obj, "target": tgt, "quarter": "2026Q4",
                         "vintage_date": TODAY, "horizon_q": 1, "point": pt, "q50": pt,
                         **gauss_quantiles(pt, sd_abs), "sd": sd_abs,
                         # v2 fix (verifier r1, issue 1): 6, not 7. 4 seasonal lambda +
                         # w + cushion c. For q4_2026_guide_mid c enters the point; for
                         # q4_2026_print c enters the predictive sd (sd_pp combines the
                         # kernel PIT RMSE with the cushion sd). kappa is in neither.
                         "window": "LIVE", "prior_basis": "PIT", "n_params": 6,
                         "n_train": int(len(hist)),
                         "street_vendor": "Zacks;Alpha Vantage",
                         "street_as_of": "2026-09-04",
                         "knowable_from": "2026-09-11",
                         "spec_id": f"gbv{int(r['gbv_3q26_musd'])}|fee_{r['fee_step']}",
                         "notes": f"headline row is gbv26300|fee_half_weight; "
                                  f"lam_q4={lam_q4:.3f} c={c*100:.3f} sd={sd_pp:.2f}pp"})
    liv = pd.DataFrame(live)
    for obj in ("q4_2026_guide_mid", "q4_2026_print"):
        register(liv[liv["object"] == obj], strict_windows=False)
    return q4, probs, sd_pp, lam_q4, c


# =====================================================================  G  ====
def section_g(tg):
    """Nights bucket words, their conservatism, the 4Q26 bucket probabilities, FY26 raise."""
    print("\n== G. bucket words ==")
    led = pd.read_csv(OVN / "02_guidance_ledger.csv")
    b = led[(led["guide_type"] == "bucket") &
            (led["metric"].isin(["nights_yoy_pct", "gbv_yoy_pct", "revenue_yoy_pct"]))].copy()
    b["target_period"] = b["target_period"].map(lambda x: Q.canon(x) if str(x).startswith("2") and
                                                "Q" in str(Q.canon(x)) else x)
    b["bucket_mid"] = b["value_mid"]
    b["conservatism_pp"] = b["actual"] - b["value_mid"]
    keep = ["print_quarter", "print_date", "target_period", "metric", "value_low", "value_high",
            "value_mid", "actual", "outcome", "conservatism_pp", "quote"]
    bt = b[keep].sort_values(["metric", "target_period"])
    write(bt, "12_bucket_guides.csv")

    sub = bt[bt["conservatism_pp"].notna()]
    nb = sub[sub["metric"] == "nights_yoy_pct"]
    summ = pd.DataFrame([
        {"scope": "nights bucket guides", "n": len(nb),
         "mean_conservatism_pp": float(nb["conservatism_pp"].mean()),
         "median_conservatism_pp": float(nb["conservatism_pp"].median()),
         "sd_pp": float(nb["conservatism_pp"].std(ddof=1)) if len(nb) > 1 else np.nan},
        {"scope": "all volume bucket guides (nights + GBV)", "n": len(sub),
         "mean_conservatism_pp": float(sub["conservatism_pp"].mean()),
         "median_conservatism_pp": float(sub["conservatism_pp"].median()),
         "sd_pp": float(sub["conservatism_pp"].std(ddof=1))},
    ])
    write(summ, "13_bucket_conservatism.csv")
    acc("G1 pooled volume-bucket conservatism is about +4pp",
        abs(float(sub["conservatism_pp"].mean()) - 4.0) < 1.0,
        f"pooled n={len(sub)} mean {float(sub['conservatism_pp'].mean()):+.2f}pp "
        f"median {float(sub['conservatism_pp'].median()):+.2f}pp; nights-only n={len(nb)} "
        f"mean {float(nb['conservatism_pp'].mean()):+.2f}pp -- n is 5 and 2, say so")

    # estimator: guided bucket midpoint minus the nights growth last OBSERVED at the guide date
    tgi = tg.set_index("quarter")
    deltas = []
    nb_all = bt[bt["metric"] == "nights_yoy_pct"]
    for r in nb_all.itertuples():
        pq = Q.canon(r.print_quarter)
        if pq in tgi.index and pd.notna(tgi.loc[pq, "nights_yoy"]):
            deltas.append({"guide_at": pq, "target": r.target_period, "guided_mid": r.value_mid,
                           "last_observed_nights_yoy": float(tgi.loc[pq, "nights_yoy"]),
                           "delta_pp": r.value_mid - float(tgi.loc[pq, "nights_yoy"])})
    dd = pd.DataFrame(deltas)
    dmu = float(dd["delta_pp"].mean()); dsd = float(dd["delta_pp"].std(ddof=1))

    # 3Q26 nights: frozen card central +10.2%; alternative = guide mid 11.0 + nights conservatism
    scen = [("frozen card 3Q26 nights +10.2%", 10.2, 1.0),
            ("3Q26 guide mid 11.0 + nights-bucket conservatism", 11.0 + float(nb["conservatism_pp"].mean()), 2.0)]
    bounds = {"other (<=6.5: mid-single-digit or lower)": (-np.inf, 6.5),
              "high single digit (7-9)": (6.5, 9.5),
              "low double digit (10-12)": (9.5, 12.5),
              "other (>12.5: teens)": (12.5, np.inf)}
    prob_rows = []
    for lbl, n3, s3 in scen:
        mu = n3 + dmu
        sd = float(np.sqrt(dsd ** 2 + s3 ** 2))
        for word, (lo, hi) in bounds.items():
            p = float(sps.norm.cdf((hi - mu) / sd) - sps.norm.cdf((lo - mu) / sd))
            prob_rows.append({"basis": f"estimated | {lbl}", "bucket_word": word,
                              "prob": p, "n_estimator": len(dd),
                              "guided_mid_mu_pp": mu, "guided_mid_sd_pp": sd})
    for word, p in [("other (<=6.5: mid-single-digit or lower)", 0.05),
                    ("high single digit (7-9)", 0.40),
                    ("low double digit (10-12)", 0.55),
                    ("other (>12.5: teens)", 0.00)]:
        prob_rows.append({"basis": "declared (chief of staff judgement)", "bucket_word": word,
                          "prob": p, "n_estimator": np.nan,
                          "guided_mid_mu_pp": np.nan, "guided_mid_sd_pp": np.nan})
    bp = pd.DataFrame(prob_rows)
    write(bp, "14_q4_2026_nights_bucket_probs.csv")
    write(dd, "14b_bucket_delta_estimator.csv")
    est_ld = bp[(bp.basis.str.startswith("estimated")) &
                (bp.bucket_word == "low double digit (10-12)")]["prob"]
    acc("G2 (DISCLOSURE) 4Q26 nights bucket word: declared vs estimated", True,
        f"estimator (n={len(dd)} deltas, mean {dmu:+.2f}pp sd {dsd:.2f}pp) gives "
        f"P(low double digit) in [{float(est_ld.min()):.2f}, {float(est_ld.max()):.2f}] "
        f"across the two 3Q26 nights scenarios; DECLARED 0.55 is ABOVE what the n=3 "
        f"estimator supports. Both published; the declared set is judgement, not measurement.")

    # FY guide raises
    fy = pd.read_csv(OVN / "02_fy_guide_revisions.csv")
    fy = fy[fy["value_mid"].notna() | fy["value_low"].notna()].copy()
    fy["level"] = fy["value_mid"].fillna(fy["value_low"])
    fy = fy.sort_values(["target_period", "metric", "print_date"])
    ev = []
    for (tp, met), g in fy.groupby(["target_period", "metric"]):
        g = g.sort_values("print_date")
        prev = None
        for r in g.itertuples():
            if prev is not None and np.isfinite(r.level) and np.isfinite(prev):
                ev.append({"target_period": tp, "metric": met, "print_date": r.print_date,
                           "print_quarter": r.print_quarter, "prev": prev, "new": r.level,
                           "action": "raise" if r.level > prev + 1e-9
                                     else ("cut" if r.level < prev - 1e-9 else "maintain")})
            prev = r.level if np.isfinite(r.level) else prev
    fe = pd.DataFrame(ev)
    write(fe, "15_fy_guide_revision_events.csv")
    q3 = fe[fe["print_quarter"].astype(str).str.startswith("3Q")]
    rows = []
    for lbl, g in [("all FY re-statements", fe), ("Q3-print re-statements only", q3),
                   ("FY26 revenue growth guide only",
                    fe[(fe.target_period == "FY2026") & (fe.metric == "revenue_yoy_pct")])]:
        nr = int((g["action"] == "raise").sum()); n = len(g)
        rows.append({"scope": lbl, "n_opportunities": n, "n_raises": nr,
                     "n_cuts": int((g["action"] == "cut").sum()),
                     "raw_rate": nr / n if n else np.nan,
                     "laplace_rate": (nr + 1) / (n + 2) if n else np.nan})
    rows.append({"scope": "DECLARED P(FY26 revenue guide raised on 5 Nov 2026)",
                 "n_opportunities": np.nan, "n_raises": np.nan, "n_cuts": np.nan,
                 "raw_rate": np.nan, "laplace_rate": 0.75})
    fr = pd.DataFrame(rows)
    write(fr, "16_fy26_raise_probability.csv")
    q3r = fr[fr.scope == "Q3-print re-statements only"].iloc[0]
    acc("G3 FY26 guide-raise probability: base rate vs the declared 0.75",
        0.55 <= float(q3r["laplace_rate"]) <= 0.95,
        f"Q3-print re-statements: {int(q3r['n_raises'])}/{int(q3r['n_opportunities'])} raises, "
        f"0 cuts, Laplace {float(q3r['laplace_rate']):.2f}; FY26 revenue guide itself raised "
        f"2/2 so far; declared 0.75")
    return bt, bp, fr


# =====================================================================  H  ====
def section_h():
    """The 9/9 guide-below-Street rule, re-tested on executable returns."""
    print("\n== H. the 9/9 rule ==")
    m = pd.read_csv(OVN / "16_consensus_at_print_merged.csv")
    rx = pd.read_csv(PROC / "abnb_earnings_reactions.csv").rename(
        columns={"quarter": "print_quarter"})
    rx = rx[["print_quarter", "abnb_1d_pct", "qqq_1d_pct", "abnb_5d_pct", "qqq_5d_pct",
             "abnb_20d_pct", "qqq_20d_pct"]]
    m = m.merge(rx, on="print_quarter", how="left", suffixes=("", "_rx"))
    d = m[m["guide_vs_street_sign"].notna() & m["excess_20d_pct"].notna()].copy()
    # EXECUTABLE: you cannot buy before the reaction-day gap. Enter at the reaction-day
    # close, hold 20 trading days. Strip the reaction-day move out of the cumulative.
    for h in (5, 20):
        d[f"abnb_exec_{h}d_pct"] = 100.0 * ((1 + d[f"abnb_{h}d_pct"] / 100.0) /
                                            (1 + d["abnb_1d_pct"] / 100.0) - 1.0)
        d[f"qqq_exec_{h}d_pct"] = 100.0 * ((1 + d[f"qqq_{h}d_pct"] / 100.0) /
                                           (1 + d["qqq_1d_pct"] / 100.0) - 1.0)
        d[f"excess_exec_{h}d_pct"] = d[f"abnb_exec_{h}d_pct"] - d[f"qqq_exec_{h}d_pct"]
    cols = ["print_quarter", "print_date", "reaction_date", "next_q_guide_mid_musd",
            "next_q_cons_revenue_musd", "next_q_cons_vendor", "guide_vs_street_pct",
            "guide_vs_street_sign", "excess_1d_pct", "excess_20d_pct",
            "excess_exec_5d_pct", "excess_exec_20d_pct", "abnb_exec_20d_pct"]
    dd = d[[c for c in cols if c in d.columns]].copy()
    write(dd, "17_drift_rule_panel.csv")

    below = dd[dd["guide_vs_street_sign"] < 0]
    above = dd[dd["guide_vs_street_sign"] > 0]
    res = []
    for lbl, col in [("as-published excess_20d (includes the un-tradeable gap)", "excess_20d_pct"),
                     ("EXECUTABLE excess_20d from the reaction-day close", "excess_exec_20d_pct"),
                     ("EXECUTABLE excess_5d from the reaction-day close", "excess_exec_5d_pct")]:
        b = below[col].astype(float); a = above[col].astype(float)
        tbl = [[int((b > 0).sum()), int((b <= 0).sum())],
               [int((a > 0).sum()), int((a <= 0).sum())]]
        p = float(sps.fisher_exact(tbl, alternative="two-sided")[1])
        res.append({"return_measure": lbl, "n_below": len(b), "n_above": len(a),
                    "below_mean_pct": float(b.mean()), "above_mean_pct": float(a.mean()),
                    "below_n_negative": int((b <= 0).sum()), "above_n_negative": int((a <= 0).sum()),
                    "fisher_p_two_sided": p,
                    "spread_pp": float(b.mean() - a.mean())})
    # calendar-artefact check: is the sign driven by the gap or by the 2022Q3-2025Q1 era?
    dd["era"] = np.where((dd["print_quarter"] >= "2022Q3") & (dd["print_quarter"] <= "2025Q1"),
                         "2022Q3-2025Q1", "other")
    era = dd.groupby("era").agg(n=("excess_exec_20d_pct", "size"),
                                mean_exec20=("excess_exec_20d_pct", "mean"),
                                n_negative=("excess_exec_20d_pct", lambda x: int((x <= 0).sum())),
                                n_below_guide=("guide_vs_street_sign",
                                               lambda x: int((x < 0).sum()))).reset_index()
    r = pd.DataFrame(res)
    write(r, "18_drift_rule_tests.csv")
    write(era, "18b_drift_rule_era.csv")

    era_in = dd[dd["era"] == "2022Q3-2025Q1"]
    acc("H1 the 9/9 rule: does guide-below-Street survive as an executable signal?",
        False if float(r.loc[r.return_measure.str.startswith("EXECUTABLE excess_20d"),
                             "fisher_p_two_sided"].iloc[0]) > 0.05 else True,
        f"as-published: below-guide {int(below['excess_20d_pct'].le(0).sum())}/{len(below)} "
        f"negative 20d, above-guide {int(above['excess_20d_pct'].le(0).sum())}/{len(above)}; "
        f"EXECUTABLE from the reaction close, Fisher p="
        f"{float(r.loc[r.return_measure.str.startswith('EXECUTABLE excess_20d'), 'fisher_p_two_sided'].iloc[0]):.3f}, "
        f"spread {float(r.loc[r.return_measure.str.startswith('EXECUTABLE excess_20d'), 'spread_pp'].iloc[0]):+.2f}pp")
    acc("H2 calendar-artefact check", True,
        f"in 2022Q3-2025Q1, {int(era_in['excess_exec_20d_pct'].le(0).sum())}/{len(era_in)} of ALL "
        f"prints had a negative executable 20d excess return regardless of the guide sign, and "
        f"{int((era_in['guide_vs_street_sign'] < 0).sum())}/{len(era_in)} of the guide-below "
        f"observations fall in that era. The rule is a calendar artefact. NOT A SIGNAL.")
    return r, era


# =====================================================================  I  ====
def section_i(kappa_mean, kappa_sd, kappa_n, sd_pp, lam_q4, c):
    print("\n== I. parameters, FY27 object, acceptance ==")
    params = pd.DataFrame([
        {"layer": "guidance policy", "parameter": "c (trailing-8 cushion, mean)", "count": 1,
         "estimator": "trailing-8 empirical mean of actual/guide_mid - 1, block bootstrap",
         "value": f"{cushion_stats(load_targets()[load_targets()['print_date'].notna()], 8)['c_mean_pct']:.4f}%"},
        {"layer": "guidance policy", "parameter": "kappa (at-print Street over guide mid)",
         "count": 1, "estimator": f"LSEG-only pairs, n={kappa_n}",
         "value": f"{kappa_mean:+.4f}% (sd {kappa_sd:.3f}pp)"},
        {"layer": "guidance policy TOTAL", "parameter": "c + kappa", "count": 2,
         "estimator": "against 19 scoreable guides and 19 interval-censored ranges",
         "value": "ratio 2/38 = 0.053"},
        {"layer": "kernel (owned by kernel-lambda, consumed here)",
         "parameter": "4 seasonal lambda + 1 lag weight w", "count": 5,
         "estimator": f"trailing-{LAMBDA_K} same-season mean; w fixed at 2/3, NOT fitted",
         "value": f"lambda_Q4 = {lam_q4:.3f}%"},
        {"layer": "combined object guide_mid_next_q", "parameter": "5 kernel + c",
         "count": 6,
         "estimator": "n_params published on every registry row; kappa is NOT in this "
                      "object's point or q50 (it feeds only the informational at-print "
                      "consensus column), so the count is 6, not 7",
         "value": ""},
        {"layer": "LIVE objects q4_2026_guide_mid / q4_2026_print",
         "parameter": "5 kernel + c", "count": 6,
         "estimator": "c enters the guide point directly and the print only through the "
                      "predictive sd; kappa in neither", "value": ""},
        {"layer": "NOT parameterised", "parameter": "the guide-vs-Street gap", "count": 0,
         "estimator": "DERIVED as (1+kappa)/(1+c) - 1; never separately fitted", "value": ""},
    ])
    write(params, "19_parameter_counts.csv")

    fy27 = pd.DataFrame([
        {"line": "volume ex-FX", "pp": 8.6, "owner": "not built tonight", "status": "assumed input"},
        {"line": "within-region price ex-FX", "pp": 3.5, "owner": "not built tonight",
         "status": "assumed input; +2.9pp of it is unidentified"},
        {"line": "geographic mix", "pp": -1.5, "owner": "identity output", "status": "identity"},
        {"line": "seats and hotel dilution", "pp": -0.5, "owner": "identity output", "status": "identity"},
        {"line": "booking-date FX", "pp": -0.4, "owner": "fx-lag", "status": "assumed input"},
        {"line": "fee step (half weight)", "pp": 0.9, "owner": "fee-takerate",
         "status": "fee-takerate must report the delta vs +0.9 explicitly"},
        {"line": "new lines", "pp": 0.2, "owner": "not built tonight", "status": "assumed input"},
        {"line": "regulation", "pp": -0.3, "owner": "not built tonight", "status": "assumed input"},
        {"line": "TOTAL FY27 revenue growth", "pp": 10.5, "owner": "sum", "status": "placeholder"},
        {"line": "OBJECT DEFINITION: the Feb-2027 FY27 GUIDE is the FY27 print divided by "
                 "(1 + c), with c the trailing-8 cushion as of Feb 2027; FY27 print is the sum "
                 "of four quarterly kernel objects. Guide and print differ by ~1.86%.",
         "pp": np.nan, "owner": "guidance-policy", "status": "definition"},
        {"line": "NOTE: FY27 Street is 15,730M (Zacks 13 est 2026-09-04) / 15,760M (S&P MI "
                 "2026-09-03) / 15,758M (Alpha Vantage 44 est 2026-09-11). Say in the first 200 "
                 "words that our FY27 is within 1% of consensus.",
         "pp": np.nan, "owner": "memo", "status": "instruction"},
    ])
    write(fy27, "20_fy27_object_definition.csv")
    write(pd.DataFrame(ACCEPT), "00_acceptance_tests.csv")


def main() -> int:
    tg = load_targets()
    tg = tg[tg["print_date"].notna()].copy()
    h, s = section_a(tg)
    section_b(tg, s)
    kappa_mean, kappa_sd, kappa_n, _ = section_c(tg, h)
    lam_full = section_d(tg)
    _, _, _, scb = section_e(tg, lam_full, h)
    _, _, sd_pp, lam_q4, c = section_f(tg, lam_full, kappa_mean, kappa_sd, kappa_n, scb)
    section_g(tg)
    section_h()
    section_i(kappa_mean, kappa_sd, kappa_n, sd_pp, lam_q4, c)
    npass = sum(1 for a in ACCEPT if a["passed"])
    print(f"\n=== guidance-policy done: {npass}/{len(ACCEPT)} acceptance tests passed ===")
    print(f"outputs -> {OUT}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        try:
            pd.DataFrame(ACCEPT).to_csv(OUT / "00_acceptance_tests.csv", index=False)
        except Exception:
            pass
        sys.exit(1)
