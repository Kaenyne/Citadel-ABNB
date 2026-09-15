"""WS22 discussion round, group C: the checks M5 was asked to answer (R23, R24, R25, R27).

Additive only: reads the registry / scoreboard that `run.py` already wrote plus M5's own parameter
file, and writes NEW files. It changes nothing `run.py` produces, so M5 does not need a re-run.

  py -3.13 analysis/src/margin_build/M5_street_bias/discussion_checks.py

Writes (data/processed/margin_build/M5_street_bias/):
  M5_discussion_paired_tests.csv   - paired loss differential vs the RAW STREET baseline for every
                                     street-bias cell (NW(1) t, two-sided p, sign test, quarters better)
  M5_discussion_clip_audit.csv     - how often clip(disp/disp_ref, 0.5, 2.0) binds, by vintage/horizon
  M5_discussion_counterfactual.csv - R25's decisive test: is `dispersion_conditioned` better than a
                                     FIXED half-bias constant (mult == 0.5) with no dispersion input?
  M5_discussion_summary.json       - the headline numbers quoted in docs/margin-build/discussion/group_C.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PROC = REPO / "data/processed/margin_build"
OUT = PROC / "M5_street_bias"
BQ = PROC / "10_harness_margin/scoreboard_by_quarter.csv"


def nw_se(d: np.ndarray, lag: int = 1) -> float:
    """Newey-West(1) standard error of the mean of d (same convention as WS21 check 10)."""
    n = len(d)
    x = d - d.mean()
    v = float(x @ x) / n
    for l in range(1, lag + 1):
        if l < n:
            v += 2 * (1 - l / (lag + 1)) * float(x[l:] @ x[:-l]) / n
    return float(np.sqrt(max(v, 1e-12) / n))


def paired(own: np.ndarray, base: np.ndarray) -> dict:
    d = own - base
    n = len(d)
    se = nw_se(d)
    t = d.mean() / se if se > 0 else np.nan
    k = int((d < 0).sum())
    ties = int((d == 0).sum())
    m = n - ties
    return {
        "n": n, "mae_own": float(own.mean()), "mae_base": float(base.mean()),
        "ratio": float(own.mean() / base.mean()) if base.mean() else np.nan,
        "mean_d": float(d.mean()), "t_nw1": float(t),
        "p_nw1": float(2 * (1 - stats.norm.cdf(abs(t)))) if np.isfinite(t) else np.nan,
        "k_better": k, "n_cmp": m,
        "p_sign": float(stats.binomtest(k, m, 0.5, alternative="greater").pvalue) if m else np.nan,
    }


def main() -> int:
    bq = pd.read_csv(BQ)
    st = bq[(bq["method"] == "baselines-margin") & (bq["object"] == "street") & (bq["prior_basis"] == "PIT")]
    st_err = {(r.target, r.window, int(r.horizon_q), r.quarter): float(r.abs_err) for r in st.itertuples()}
    st_pt = {(r.target, r.window, int(r.horizon_q), r.quarter): float(r.point) for r in st.itertuples()}

    # ---- 1. paired tests vs the raw Street, every street-bias cell (R23)
    b = bq[(bq["method"] == "street-bias") & (bq["prior_basis"] == "PIT")]
    rows = []
    for (obj, tgt, spec, h, win), g in b.groupby(["object", "target", "spec_id", "horizon_q", "window"]):
        g = g.sort_values("quarter")
        base = np.array([st_err.get((tgt, win, int(h), q), np.nan) for q in g["quarter"]], dtype=float)
        own = g["abs_err"].to_numpy(dtype=float)
        m = np.isfinite(base) & np.isfinite(own)
        if m.sum() < 5:
            continue
        rows.append(dict(object=obj, target=tgt, spec_id=spec, horizon_q=int(h), window=win,
                         **paired(own[m], base[m])))
    pt = pd.DataFrame(rows).sort_values(["target", "horizon_q", "window", "ratio"])
    pt.to_csv(OUT / "M5_discussion_paired_tests.csv", index=False)

    # ---- 2. clip audit (R25)
    par = pd.read_csv(OUT / "M5_parameters_by_vintage.csv")
    cl = par[par["spec_id"] == "rw_hl4"][["vintage_date", "horizon_q", "disp", "disp_ref", "disp_ratio"]].copy()
    cl = cl.drop_duplicates().sort_values(["vintage_date", "horizon_q"])
    cl["raw_ratio"] = cl["disp"] / cl["disp_ref"]
    cl["binds_floor"] = np.isclose(cl["disp_ratio"], 0.5)
    cl["binds_cap"] = np.isclose(cl["disp_ratio"], 2.0)
    cl["has_dispersion"] = cl["disp"].notna()
    cl.to_csv(OUT / "M5_discussion_clip_audit.csv", index=False)
    live = cl[cl["vintage_date"].astype(str) == "2026-09-11"]
    hist = cl[(cl["vintage_date"].astype(str) < "2026-09-01") & cl["has_dispersion"]]
    h0 = hist[hist["horizon_q"] == 0]

    # ---- 3. R25's decisive counterfactual: a FIXED half-bias, no dispersion input at all.
    # dispersion_conditioned = street + b * clip(disp/disp_ref, .5, 2);  street_plus_bias = street + b.
    # So "street + 0.5 * b" = 0.5 * (street_plus_bias point + street point) -- reconstructable exactly.
    cf = []
    for tgt in ["adj_ebitda_margin_pct", "adj_ebitda_musd"]:
        for win in ["W1", "W2"]:
            for h in [0, 1]:
                spb = b[(b["object"] == "street_plus_bias") & (b["target"] == tgt) & (b["window"] == win)
                        & (b["horizon_q"] == h) & (b["spec_id"] == "rw_hl4")].sort_values("quarter")
                dcn = b[(b["object"] == "dispersion_conditioned") & (b["target"] == tgt) & (b["window"] == win)
                        & (b["horizon_q"] == h) & (b["spec_id"] == "rw_hl4")].sort_values("quarter")
                if len(spb) < 5 or len(dcn) < 5:
                    continue
                q = spb["quarter"].tolist()
                s = np.array([st_pt.get((tgt, win, h, x), np.nan) for x in q], dtype=float)
                y = spb["actual"].to_numpy(dtype=float)
                half = 0.5 * (spb["point"].to_numpy(dtype=float) + s)      # street + 0.5*b
                own_half = np.abs(half - y)
                own_disp = dcn.set_index("quarter").loc[q, "abs_err"].to_numpy(dtype=float)
                own_street = np.abs(s - y)
                m = np.isfinite(own_half) & np.isfinite(own_disp) & np.isfinite(own_street)
                cf.append(dict(target=tgt, window=win, horizon_q=h, n=int(m.sum()),
                               mae_street=float(own_street[m].mean()),
                               mae_half_bias_const=float(own_half[m].mean()),
                               mae_dispersion_conditioned=float(own_disp[m].mean()),
                               ratio_half_vs_street=float(own_half[m].mean() / own_street[m].mean()),
                               ratio_disp_vs_street=float(own_disp[m].mean() / own_street[m].mean()),
                               **{f"disp_vs_half_{k}": v for k, v in paired(own_disp[m], own_half[m]).items()}))
    cfd = pd.DataFrame(cf)
    cfd.to_csv(OUT / "M5_discussion_counterfactual.csv", index=False)

    # ---- 3b. WS20 question 1: the clip floor as a free parameter (0.0 / 0.3 / 0.5 / 0.7 / 1.0).
    # dispersion_conditioned = street + b_pt * clip(disp/disp_ref, floor, 2.0)  [margin]
    #                        = street * (1 + b_pct * clip(...))                 [dollars]
    # Rebuild it at every floor, check the rebuild reproduces the registered floor-0.5 points, then
    # re-score. Answers "how much of the LIVE beat is the clip rather than the fitted slope?"
    pv = par[["vintage_date", "horizon_q", "spec_id", "b_pt", "b_pct", "disp", "disp_ref"]].drop_duplicates()
    pv["raw"] = pv["disp"] / pv["disp_ref"]
    FLOORS = [0.0, 0.3, 0.5, 0.7, 1.0]
    sens, live_rows = [], []
    for spec in ["rw_hl4", "rw_hl4_med"]:
        pk = pv[pv["spec_id"] == spec].set_index(["vintage_date", "horizon_q"])
        for tgt, col in (("adj_ebitda_margin_pct", "b_pt"), ("adj_ebitda_musd", "b_pct")):
            for win in ["W1", "W2"]:
                g = b[(b["object"] == "dispersion_conditioned") & (b["target"] == tgt)
                      & (b["window"] == win) & (b["horizon_q"] == 0) & (b["spec_id"] == spec)].sort_values("quarter")
                if len(g) < 5:
                    continue
                s = np.array([st_pt.get((tgt, win, 0, q), np.nan) for q in g["quarter"]], dtype=float)
                yv = g["actual"].to_numpy(dtype=float)
                bb, raw = [], []
                for vd in g["vintage_date"].astype(str):
                    try:
                        r0 = pk.loc[(vd, 0)]
                        r0 = r0.iloc[0] if isinstance(r0, pd.DataFrame) else r0
                        bb.append(float(r0[col])); raw.append(float(r0["raw"]))
                    except KeyError:
                        bb.append(np.nan); raw.append(np.nan)
                bb, raw = np.array(bb), np.array(raw)
                for fl in FLOORS:
                    mult = np.where(np.isfinite(raw), np.clip(raw, fl, 2.0), 1.0)
                    pt_ = s + bb * mult if col == "b_pt" else s * (1 + bb * mult)
                    e = np.abs(pt_ - yv)
                    m2 = np.isfinite(e)
                    row = dict(spec_id=spec, target=tgt, window=win, floor=fl, n=int(m2.sum()),
                               mae=float(e[m2].mean()), mae_street=float(np.abs(s - yv)[m2].mean()),
                               k_better=int((e[m2] < np.abs(s - yv)[m2]).sum()))
                    if abs(fl - 0.5) < 1e-9:      # reconstruction check against the registered points
                        row["max_abs_diff_vs_registered"] = float(np.nanmax(np.abs(pt_ - g["point"].to_numpy(float))))
                    sens.append(row)
    # LIVE 3Q26 at each floor
    livep = pv[(pv["vintage_date"].astype(str) == "2026-09-11") & (pv["horizon_q"] == 0)]
    st_live = {"adj_ebitda_margin_pct": 49.775747, "adj_ebitda_musd": 2361.52179}   # M5_live_all_specs.csv
    for _, r in livep.iterrows():
        for fl in FLOORS:
            mult = np.clip(r["raw"], fl, 2.0)
            live_rows.append(dict(spec_id=r["spec_id"], floor=fl, raw_ratio=float(r["raw"]), mult=float(mult),
                                  margin_pct=st_live["adj_ebitda_margin_pct"] + r["b_pt"] * mult,
                                  beat_pt=r["b_pt"] * mult,
                                  ebitda_musd=st_live["adj_ebitda_musd"] * (1 + r["b_pct"] * mult),
                                  beat_musd=st_live["adj_ebitda_musd"] * r["b_pct"] * mult))
    sdf = pd.DataFrame(sens)
    ldf = pd.DataFrame(live_rows)
    sdf.to_csv(OUT / "M5_discussion_clip_sensitivity_backtest.csv", index=False)
    ldf.to_csv(OUT / "M5_discussion_clip_sensitivity_live.csv", index=False)

    # ---- 3c. WS20 question 2: which regime, quarter by quarter (street error vs M5's correction)
    reg_rows = []
    g = b[(b["object"] == "dispersion_conditioned") & (b["target"] == "adj_ebitda_margin_pct")
          & (b["window"] == "W1") & (b["horizon_q"] == 0) & (b["spec_id"] == "rw_hl4")].sort_values("quarter")
    pk = pv[pv["spec_id"] == "rw_hl4"].set_index(["vintage_date", "horizon_q"])
    for r in g.itertuples():
        se = st_pt.get(("adj_ebitda_margin_pct", "W1", 0, r.quarter), np.nan)
        try:
            pr = pk.loc[(str(r.vintage_date), 0)]
            pr = pr.iloc[0] if isinstance(pr, pd.DataFrame) else pr
            disp, ratio, bpt = float(pr["disp"]), float(pr["raw"]), float(pr["b_pt"])
        except KeyError:
            disp = ratio = bpt = np.nan
        reg_rows.append(dict(quarter=r.quarter, vintage_date=r.vintage_date, actual=r.actual,
                             street=se, street_err=se - r.actual, m5_point=r.point, m5_err=r.err,
                             d_abs=abs(r.err) - abs(se - r.actual), disp=disp, disp_raw_ratio=ratio, b_pt=bpt))
    rdf = pd.DataFrame(reg_rows)
    rdf.to_csv(OUT / "M5_discussion_regime_by_quarter.csv", index=False)

    # ---- 4. coverage (R27) straight off the by_quarter file
    cov = (b[b["horizon_q"] == 0].groupby(["object", "target", "window", "spec_id"])["in80"]
           .agg(["mean", "count"]).reset_index())

    sec = json.loads((OUT / "M5_secondary_tests.json").read_text(encoding="utf-8"))
    summary = {
        "R23_flowthrough_usd": pt[(pt.object == "street_plus_flowthrough") & (pt.target == "adj_ebitda_musd")
                                  & (pt.spec_id == "rw_hl4") & (pt.horizon_q == 0)]
                                 .set_index("window")[["n", "ratio", "t_nw1", "p_nw1", "k_better", "p_sign"]]
                                 .to_dict("index"),
        "R23_dispersion_margin": pt[(pt.object == "dispersion_conditioned") & (pt.target == "adj_ebitda_margin_pct")
                                    & (pt.spec_id == "rw_hl4") & (pt.horizon_q == 0)]
                                   .set_index("window")[["n", "ratio", "t_nw1", "p_nw1", "k_better", "p_sign"]]
                                   .to_dict("index"),
        "R23_cells_beating_street_p05": int(((pt["p_nw1"] < 0.05) & (pt["ratio"] < 1)).sum()),
        "R23_cells_tested": int(len(pt)),
        "R24_dispersion_slope_full": sec.get("dispersion_signed"),
        "R24_dispersion_slope_from22": sec.get("dispersion_signed_from22"),
        "R25_clip_binds_floor_all_rows": int(hist["binds_floor"].sum()),
        "R25_rows_with_dispersion": int(len(hist)),
        "R25_clip_binds_floor_h0": int(h0["binds_floor"].sum()),
        "R25_h0_rows_with_dispersion": int(len(h0)),
        "R25_h0_rows_from_2023_05": int((h0["vintage_date"].astype(str) >= "2023-05-01").sum()),
        "R25_h0_binds_from_2023_05": int(h0[h0["vintage_date"].astype(str) >= "2023-05-01"]["binds_floor"].sum()),
        "R25_live_raw_ratio_h0": float(live[live.horizon_q == 0]["raw_ratio"].iloc[0]),
        "R25_backtest_raw_ratio_min_h0": float(h0["raw_ratio"].min()),
        "R27_mean_cov80_h0": float(cov["mean"].mean()),
        "R27_min_cov80_h0": float(cov["mean"].min()),
    }
    (OUT / "M5_discussion_summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=float))
    print("\nclip sensitivity, LIVE 3Q26 (WS20 q1):")
    print(ldf.round(4).to_string(index=False))
    print("\nclip sensitivity, backtest h=0 MAE by floor (WS20 q1):")
    print(sdf.round(4).to_string(index=False))
    print("\nregime by quarter (WS20 q2):")
    print(rdf.round(3).to_string(index=False))
    print("\ncounterfactual (R25): dispersion_conditioned vs a fixed half-bias constant")
    print(cfd[["target", "window", "horizon_q", "n", "mae_street", "mae_half_bias_const",
               "mae_dispersion_conditioned", "disp_vs_half_mean_d", "disp_vs_half_t_nw1",
               "disp_vs_half_p_nw1", "disp_vs_half_k_better"]].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
