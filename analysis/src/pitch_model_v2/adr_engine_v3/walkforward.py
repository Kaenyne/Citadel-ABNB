"""adr_engine / walkforward.py — point-in-time walk-forward of the FX-on-ADR variants at three origins
(O1 quarter start, O2 day 60, O3 pre-print) against the 17 disclosed ADR-FX points; scoring on W1 / W2 per the
pre-registration §4–§5."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C
from . import fx_data as F
from . import exposure as E


def build_full_design(daily, shares, targets: pd.DataFrame) -> pd.DataFrame:
    """Completed-quarter design rows (all prints observed, latest 10-K knowable at the print date)."""
    rows = []
    for q, t in targets.iterrows():
        x = F.design_row(daily, shares, q, t.print_date)
        x.update({"quarter": q, "y": float(t.fx_pts_adr), "h": float(t.half_width), "print_date": t.print_date})
        rows.append(x)
    return pd.DataFrame(rows).set_index("quarter")


def run(daily=None, shares=None, targets=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = F.load_daily() if daily is None else daily
    shares = F.gbv_shares() if shares is None else shares
    targets = F.disclosed_targets() if targets is None else targets
    pdts = F.print_dates()
    full = build_full_design(daily, shares, targets)
    recs = []
    for q in C.WINDOWS["W1"]:
        odates = F.origin_dates(q, pdts)
        for o, d in odates.items():
            if d is None:
                continue
            # training set: disclosed points printed on or before the origin
            tr = full[full.print_date <= d]
            if len(tr) < 3:
                continue
            Xtr = tr[C.REGIONS].values; ytr = tr.y.values; htr = tr.h.values
            # target design at the origin (PIT rates, PIT shares)
            xt = F.design_row(daily, shares, q, d)
            Xt = np.array([xt[r] for r in C.REGIONS])
            m1 = E.fit_v1_map(Xtr, ytr, htr)
            a2, b2 = E.fit_ols(tr.eur_yoy.values, ytr)
            a3, b3 = E.fit_ols(tr.usd_broad_yoy.values, ytr)
            naive = float(tr.y.iloc[-1])
            preds = {"V0_translation": E.predict_v0(Xt), "V1_passthrough": E.predict_v1(Xt, m1["beta"]),
                     "V2_eur_ols": a2 + b2 * xt["eur_yoy"], "V3_usd_broad_ols": a3 + b3 * xt["usd_broad_yoy"],
                     "naive_last_disclosed": naive, "zero": 0.0}
            # audit fix (j): the card's method, the average of the identity and the euro-only fit, scored point in time
            preds["M_card_midpoint"] = 0.5 * (preds["V0_translation"] + preds["V2_eur_ols"])
            y, h = float(full.loc[q, "y"]), float(full.loc[q, "h"])
            for v, p in preds.items():
                err = p - y
                ierr = 0.0 if abs(err) <= h else (abs(err) - h) * np.sign(err)
                recs.append({"quarter": q, "origin": o, "origin_date": d.date().isoformat(), "variant": v, "pred_pp": p,
                             "disclosed_pp": y, "half_width": h, "err_pp": err, "interval_err_pp": ierr,
                             "obs_frac": xt["obs_frac"], "n_train": len(tr), "naive_pp": naive,
                             "beta_na": m1["beta"][0], "beta_emea": m1["beta"][1], "beta_latam": m1["beta"][2],
                             "beta_apac": m1["beta"][3], "sigma_map": m1["sigma"], "shares_fy": xt["shares_fy"]})
    wf = pd.DataFrame(recs)
    return wf, full


def _rmse(x):
    x = np.asarray(x, float); return float(np.sqrt(np.mean(x ** 2)))


def block_bootstrap_ratio(e_model, e_naive, block=4, n=2000, seed=21):
    rng = np.random.default_rng(seed); m = len(e_model); out = []
    for _ in range(n):
        idx = []
        while len(idx) < m:
            s = rng.integers(0, m); idx += [(s + j) % m for j in range(block)]
        idx = idx[:m]
        out.append(_rmse(e_model[idx]) / _rmse(e_naive[idx]))
    return float(np.percentile(out, 5)), float(np.percentile(out, 95))


def score(wf: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for w, qs in C.WINDOWS.items():
        for o in C.ORIGINS:
            sub = wf[(wf.origin == o) & (wf.quarter.isin(qs))]
            if sub.empty:
                continue
            nv = sub[sub.variant == "naive_last_disclosed"].set_index("quarter")
            for v, g in sub.groupby("variant"):
                g = g.set_index("quarter")
                g = g.loc[[q for q in qs if q in g.index]]
                e = g.err_pp.values; en = nv.loc[g.index, "err_pp"].values
                ie = g.interval_err_pp.values; ien = nv.loc[g.index, "interval_err_pp"].values
                lo, hi = block_bootstrap_ratio(e, en) if v != "naive_last_disclosed" else (1.0, 1.0)
                rows.append({"window": w, "origin": o, "variant": v, "n": len(g), "rmse_pp": _rmse(e),
                             "rmse_naive_pp": _rmse(en), "ratio_vs_naive": _rmse(e) / _rmse(en),
                             "ratio_boot90_lo": lo, "ratio_boot90_hi": hi,
                             "interval_rmse_pp": _rmse(ie), "interval_rmse_naive_pp": _rmse(ien),
                             "interval_ratio": (_rmse(ie) / _rmse(ien)) if _rmse(ien) > 0 else np.nan,
                             "bias_pp": float(np.mean(e)), "mean_obs_frac": float(g.obs_frac.mean()),
                             "pass_line_0.75": bool(_rmse(e) / _rmse(en) <= C.PASS_RATIO)})
    return pd.DataFrame(rows)


def promotion(scores: pd.DataFrame) -> dict:
    """Apply the pre-registered promotion rule (§5)."""
    def ok(v):
        s = scores[(scores.variant == v) & (scores.origin.isin(["O2", "O3"]))]
        return bool(len(s) == 4 and s["pass_line_0.75"].all())
    v0, v1 = ok("V0_translation"), ok("V1_passthrough")
    leg = None
    if v0 and v1:
        s0 = scores[(scores.variant == "V0_translation") & (scores.origin.isin(["O2", "O3"]))].set_index(["window", "origin"]).rmse_pp
        s1 = scores[(scores.variant == "V1_passthrough") & (scores.origin.isin(["O2", "O3"]))].set_index(["window", "origin"]).rmse_pp
        leg = "V1_passthrough" if bool((s1 < s0.loc[s1.index]).all()) else "V0_translation"
    elif v1:
        leg = "V1_passthrough"
    elif v0:
        leg = "V0_translation"
    return {"V0_passes": v0, "V1_passes": v1, "promoted_leg": leg or "none (card midpoint DEC-0027 stays)"}
