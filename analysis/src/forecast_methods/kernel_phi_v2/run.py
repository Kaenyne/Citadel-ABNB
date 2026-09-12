"""kernel_phi_v2 — entry point.  Run from the repo root:

    /Users/theomachado/.venvs/citadel-abnb/bin/python \
        analysis/src/forecast_methods/kernel_phi_v2/run.py

Writes every table to data/processed/forecast_methods/kernel_phi_v2/.
No registry writes, no harness/score.py, no git.
"""
from __future__ import annotations

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import (build_panel, ex_covid_mask, OUT, SEASON_NAME,
                    GBV_2Q26, GBV_1Q26, GUIDE_3Q26_MID)          # noqa: E402
from phi_fit import fit_phi, phi_of                              # noqa: E402
import stage_a, stage_b, stage_c, stage_d as sd                  # noqa: E402

KMAX = 4
N_BOOT = 400
W_PUB = 2.0 / 3.0
Z = {"q10": -1.2816, "q25": -0.6745, "q50": 0.0, "q75": 0.6745, "q90": 1.2816}


def headline_fit(panel):
    exm = ex_covid_mask(panel)
    return fit_phi(panel[exm | panel["gbv_l4"].isna()], kmax=KMAX, mode="pooled")


# ---------------------------------------------------------------- A7 split profile
def split_profile(panel, fit):
    """Hold phi_0 and the tail at the fitted values, sweep the phi_1:phi_2 split."""
    phi = fit["phi"][0]
    s12 = phi[1] + phi[2]
    exm = ex_covid_mask(panel)
    frame = panel[exm | panel["gbv_l4"].isna()]
    rows = []
    for w in np.round(np.arange(0.0, 1.001, 0.05), 2):
        p = np.array([phi[0], s12 * w, s12 * (1 - w), phi[3], phi[4]])
        f = fit_phi(frame, kmax=KMAX, fixed_phi=p)
        from phi_fit import loo_rmse
        lr, _, _, ln, _ = loo_rmse(frame, kmax=KMAX, fixed_phi=p)
        rows.append(dict(split_w=float(w), phi_1=p[1], phi_2=p[2],
                         insample_rel_rmse_pct=f["rmse_pct"],
                         loo_rel_rmse_pct=lr, loo_n=ln))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- D runner
def run_d(panel, fit):
    rows_sweep = []
    for w in np.round(np.arange(0.0, 1.001, 0.05), 3):
        d = sd.build(panel, fit, kmax=KMAX, w=float(w))
        for tw in ("all", "ex_covid", "last3_ex_covid"):
            rep = sd.pit_replay(d, None, train_window=tw)
            a, b = sd.score(rep, "2023Q1"), sd.score(rep, "2024Q1")
            rows_sweep.append(dict(carried_w=float(w), train_window=tw,
                                   W1_n=a["n"], W1_rmse_pct=a["rmse_pct"],
                                   W1_mae_pct=a["mae_pct"], W1_bias_pct=a["bias_pct"],
                                   W2_n=b["n"], W2_rmse_pct=b["rmse_pct"],
                                   W2_bias_pct=b["bias_pct"]))
    sweep = pd.DataFrame(rows_sweep)
    sweep.to_csv(os.path.join(OUT, "D3_carried_weight_pit_sweep.csv"), index=False)

    # headline carried definition: the estimated split, and the PIT-optimal 2/3
    phi = fit["phi"][0]
    w_est = float(phi[1] / (phi[1] + phi[2]))
    d_est = sd.build(panel, fit, kmax=KMAX, w=w_est)
    d_pub = sd.build(panel, fit, kmax=KMAX, w=W_PUB)

    desc = pd.concat([sd.describe_R(d_est).assign(carried_def=f"estimated split w={w_est:.3f}"),
                      sd.describe_R(d_pub).assign(carried_def="published split w=2/3")])
    desc.to_csv(os.path.join(OUT, "D1_residual_R_by_season.csv"), index=False)

    expl = pd.concat([sd.explain_R(d_est).assign(carried_def=f"estimated split w={w_est:.3f}"),
                      sd.explain_R(d_pub).assign(carried_def="published split w=2/3")])
    expl.to_csv(os.path.join(OUT, "D2_residual_R_explainers.csv"), index=False)

    panel_out = d_pub[["label", "q", "season_name", "revenue_musd", "carried_musd",
                       "R_musd", "R_share_of_revenue", "k", "R_yoy_pct",
                       "phi0_inquarter_share", "x_gbv_yoy_l1", "x_nights_yoy_l1",
                       "x_paid_backlog_yoy_l1", "x_fp_yoy_l1", "x_uf_yoy_l1"]].copy()
    panel_out.to_csv(os.path.join(OUT, "D0_carried_and_residual_panel.csv"), index=False)

    # feature horse race at the PIT-optimal carried definition
    feats = [None, "x_gbv_yoy_l1", "x_gbv_accel_l1", "x_paid_backlog_yoy_l1",
             "x_fp_yoy_l1", "x_uf_yoy_l1", "x_nights_yoy_l1"]
    rows, reps = [], {}
    for tw in ("all", "ex_covid", "last3_ex_covid"):
        for col in feats:
            rep = sd.pit_replay(d_pub, col, train_window=tw)
            reps[(tw, col)] = rep
            a, b = sd.score(rep, "2023Q1"), sd.score(rep, "2024Q1")
            rows.append(dict(train_window=tw, feature=col or "season_mean_only",
                             W1_n=a["n"], W1_rmse_pct=a["rmse_pct"],
                             W1_mae_pct=a["mae_pct"], W1_bias_pct=a["bias_pct"],
                             W2_n=b["n"], W2_rmse_pct=b["rmse_pct"],
                             W2_mae_pct=b["mae_pct"], W2_bias_pct=b["bias_pct"]))
    race = pd.DataFrame(rows)
    b0 = race[(race.feature == "season_mean_only")].set_index("train_window")
    race["W1_ratio_vs_season_mean"] = race.apply(
        lambda r: r["W1_rmse_pct"] / b0.loc[r["train_window"], "W1_rmse_pct"], axis=1)
    race["W2_ratio_vs_season_mean"] = race.apply(
        lambda r: r["W2_rmse_pct"] / b0.loc[r["train_window"], "W2_rmse_pct"], axis=1)
    race.to_csv(os.path.join(OUT, "D4_R_model_pit_race.csv"), index=False)

    # PIT calibration of the chosen object
    chosen_tw, chosen_col = "ex_covid", "x_gbv_yoy_l1"
    rep = reps[(chosen_tw, chosen_col)]
    rep.to_csv(os.path.join(OUT, "D5_R_model_pit_replay.csv"), index=False)
    e = rep[rep["q"] >= "2023Q1"]["err_pct"].values
    mu_e, sd_e = float(e.mean()), float(e.std(ddof=1))

    # ------------------------------------------------ conditional 3Q26 revenue
    sm, b, xm = sd._fit_k(sd._train_filter(d_pub, chosen_tw), chosen_col)
    x_now = float(d_pub[d_pub["q"] == "2026Q2"]["gbv_yoy_pct"].iloc[0])
    k3 = sm[3] + (b * (x_now - xm) if np.isfinite(xm) else 0.0)
    scale = float(phi[1] + phi[2])
    carried_3q26 = fit["c"][3] / 100.0 * scale * (W_PUB * GBV_2Q26 + (1 - W_PUB) * GBV_1Q26)
    pred_3q26 = carried_3q26 * (1 + k3)
    rows = []
    for lab, spec in [("season_mean_only", (sm[3], None)), ("gbv_yoy_momentum", (k3, None))]:
        kk = spec[0]
        pr = carried_3q26 * (1 + kk)
        cen = pr / (1 + mu_e / 100.0)
        qs = {q: pr / (1 + (mu_e + z * sd_e) / 100.0) for q, z in Z.items()}
        rows.append(dict(spec=lab, carried_musd=carried_3q26, k=kk, raw_point_musd=pr,
                         bias_corrected_point_musd=cen,
                         q10=qs["q90"], q25=qs["q75"], q50=qs["q50"],
                         q75=qs["q25"], q90=qs["q10"],
                         pit_bias_pct=mu_e, pit_sd_pct=sd_e, pit_n=len(e)))
    live3 = pd.DataFrame(rows)
    live3["guide_mid_musd"] = GUIDE_3Q26_MID
    live3.to_csv(os.path.join(OUT, "D6_live_3q26_conditional.csv"), index=False)

    # ------------------------------------------------ 4Q26 on a GBV_3Q26 grid
    grid = []
    for g3 in range(25_500, 28_001, 100):
        carried4 = fit["c"][4] / 100.0 * scale * (W_PUB * g3 + (1 - W_PUB) * GBV_2Q26)
        # momentum feature for 4Q26 is 3Q26 GBV y/y, implied by the grid point
        x4 = 100.0 * (g3 / 22_900.0 - 1.0)
        k4 = sm[4] + (b * (x4 - xm) if np.isfinite(xm) else 0.0)
        pr = carried4 * (1 + k4)
        cen = pr / (1 + mu_e / 100.0)
        qs = {q: pr / (1 + (mu_e + z * sd_e) / 100.0) for q, z in Z.items()}
        grid.append(dict(gbv_3q26_musd=g3, gbv_3q26_yoy_pct=x4, carried_musd=carried4,
                         k=k4, raw_point_musd=pr, bias_corrected_point_musd=cen,
                         q10=qs["q90"], q25=qs["q75"], q50=qs["q50"],
                         q75=qs["q25"], q90=qs["q10"]))
    pd.DataFrame(grid).to_csv(os.path.join(OUT, "D7_live_4q26_grid.csv"), index=False)

    # ------------------------------------------------ GBV forecast
    gf = sd.gbv_frame(panel)
    feats_g = ["x_gbv_yoy_l1", "x_nights_yoy_l1", "x_fp_yoy_l1",
               "x_paid_backlog_yoy_l1", "x_uf_yoy_l1",
               "x_uf_yoy_corr_k0.5", "x_uf_yoy_corr_k1.0"]
    grows, greps = [], {}
    for start, wname in [("2023Q1", "W1"), ("2024Q1", "W2")]:
        nv = sd.gbv_naive(gf, start)
        en = nv["err_pct"].values
        rmse_n = float(np.sqrt((en ** 2).mean()))
        grows.append(dict(window=wname, feature="naive_yoy_persistence", n=len(en),
                          rmse_pct=rmse_n, mae_pct=float(np.abs(en).mean()),
                          bias_pct=float(en.mean()), ratio_vs_naive=1.0))
        for col in feats_g:
            rp = sd.gbv_replay(gf, col, start)
            greps[(wname, col)] = rp
            if len(rp) == 0:
                continue
            ee = rp["err_pct"].values
            grows.append(dict(window=wname, feature=col, n=len(ee),
                              rmse_pct=float(np.sqrt((ee ** 2).mean())),
                              mae_pct=float(np.abs(ee).mean()),
                              bias_pct=float(ee.mean()),
                              ratio_vs_naive=float(np.sqrt((ee ** 2).mean())) / rmse_n))
    gsc = pd.DataFrame(grows)
    gsc.to_csv(os.path.join(OUT, "D8_gbv_forecast_pit_race.csv"), index=False)

    # live GBV_3Q26 from each feature, plus the naive
    live_rows = []
    last = gf[gf["q"] == "2026Q2"].iloc[0]
    gbv_3q25 = 22_900.0
    for col in ["naive_yoy_persistence"] + feats_g:
        if col == "naive_yoy_persistence":
            yhat = float(last["gbv_yoy_pct"])
        else:
            tr = gf[gf["q"] <= "2026Q2"].dropna(subset=["y_gbv_yoy", col])
            if len(tr) < 6 or not np.isfinite(last[col]):
                continue
            bb = np.polyfit(tr[col].values.astype(float),
                            tr["y_gbv_yoy"].values.astype(float), 1)
            yhat = float(np.polyval(bb, float(last[col])))
        pt = gbv_3q25 * (1 + yhat / 100.0)
        r = gsc[(gsc.window == "W2") & (gsc.feature == col)]
        rm = float(r["rmse_pct"].iloc[0]) if len(r) else np.nan
        bi = float(r["bias_pct"].iloc[0]) if len(r) else np.nan
        live_rows.append(dict(feature=col, implied_gbv_yoy_pct=yhat,
                              gbv_3q26_musd=pt,
                              bias_corrected_musd=pt / (1 + bi / 100.0)
                              if np.isfinite(bi) else np.nan,
                              W2_rmse_pct=rm,
                              q10=pt / (1 + (bi + 1.2816 * rm) / 100.0) if np.isfinite(rm) else np.nan,
                              q90=pt / (1 + (bi - 1.2816 * rm) / 100.0) if np.isfinite(rm) else np.nan))
    pd.DataFrame(live_rows).to_csv(os.path.join(OUT, "D9_live_gbv_3q26.csv"), index=False)
    return sweep, race, live3, pd.DataFrame(grid), gsc, pd.DataFrame(live_rows), (mu_e, sd_e)


# ---------------------------------------------------------------- figure
def _point_phi(panel, sname):
    import stage_a as _sa
    frame = _sa.samples(panel)[sname]
    return fit_phi(frame, kmax=4, mode="pooled")["phi"][0]


def figure(panel, fit, boot_store):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    samples = ["full_2021Q3+", "ex_covid_nightsyoy_25", "post2023_2023Q1+"]
    colours = ["#4C72B0", "#DD8452", "#55A868"]
    ks = np.arange(0, 5)
    for j, sname in enumerate(samples):
        key = (sname, "pooled")
        if key not in boot_store:
            continue
        ph, cc, grp = boot_store[key]
        pt = _point_phi(panel, sname)
        lo = np.percentile(ph, 2.5, axis=0)
        hi = np.percentile(ph, 97.5, axis=0)
        off = (j - 1) * 0.18
        ax[0].errorbar(ks + off, pt,
                       yerr=[np.maximum(pt - lo, 0), np.maximum(hi - pt, 0)], fmt="o",
                       color=colours[j], capsize=3, label=sname, lw=1.4, ms=5)
    ax[0].plot(ks, [0, 2 / 3, 1 / 3, 0, 0], "k--", lw=1.2, marker="s", ms=4,
               label="published kernel (0, 2/3, 1/3, 0, 0)")
    ax[0].set_xticks(ks)
    ax[0].set_xticklabels([f"$\\phi_{k}$" for k in ks])
    ax[0].set_ylabel("weight on GBV$_{q-k}$")
    ax[0].set_title("Pooled lag weights, 95% block-bootstrap CI")
    ax[0].axhline(0, color="0.7", lw=0.8)
    ax[0].legend(fontsize=7, loc="upper right")

    # season-specific phi from the ex-COVID season fit
    exm = ex_covid_mask(panel)
    frame_ex = panel[exm | panel["gbv_l4"].isna()]
    fs = fit_phi(frame_ex, kmax=4, mode="season")
    from common import usable as _usable
    nn = _usable(frame_ex, kmax=4)["season"].value_counts().to_dict()
    for s, col in zip((1, 2, 3, 4), ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]):
        ax[1].plot(ks + (s - 2.5) * 0.08, fs["phi"][s], "o-", color=col, ms=5,
                   lw=1.2, label=f"{SEASON_NAME[s]} (n={nn.get(s, 0)})")
    ax[1].plot(ks, fit["phi"][0], "k-", lw=2.0, label="pooled ex-COVID")
    ax[1].set_xticks(ks)
    ax[1].set_xticklabels([f"$\\phi_{k}$" for k in ks])
    ax[1].set_title("Season-specific $\\phi_{s,k}$ (ex-COVID, n=16, 20 params)\n"
                    "— saturated, LOO 2.10% vs pooled 1.61%", fontsize=9)
    ax[1].axhline(0, color="0.7", lw=0.8)
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    p = os.path.join(OUT, "F1_phi_by_season.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def main():
    os.makedirs(OUT, exist_ok=True)
    panel = build_panel(kmax=KMAX)
    fit = headline_fit(panel)
    print("headline pooled ex-COVID phi:", np.round(fit["phi"][0], 4),
          "c:", {k: round(v, 3) for k, v in fit["c"].items()}, "n:", fit["n"])

    print("\n[A] weights ...")
    a1, ident, dm, fits, boot_store = stage_a.run(panel, n_boot=N_BOOT)
    sp = split_profile(panel, fit)
    sp.to_csv(os.path.join(OUT, "A7_phi1_phi2_split_profile.csv"), index=False)

    print("[B] paid backlog ...")
    bpanel, norms, devs, live_b = stage_b.run(panel, fit, kmax=KMAX)

    print("[C] RNPL leakage ...")
    lam, cst, c3, c4, c5, c6, sig = stage_c.run(panel)

    print("[D] residual and conditional range ...")
    sweep, race, live3, grid4, gsc, liveg, (mu_e, sd_e) = run_d(panel, fit)

    print("[F] figure ...")
    fp = figure(panel, fit, boot_store)

    files = sorted(f for f in os.listdir(OUT) if f.endswith((".csv", ".png")))
    pd.DataFrame({"file": files}).to_csv(os.path.join(OUT, "00_manifest.csv"), index=False)
    print(f"\nwrote {len(files)} files to {OUT}")
    print(f"figure: {fp}")
    print(f"\n3Q26 conditional (gbv_yoy_momentum): "
          f"{live3.loc[1,'bias_corrected_point_musd']:.0f} "
          f"[q10 {live3.loc[1,'q10']:.0f}, q90 {live3.loc[1,'q90']:.0f}]")
    print(f"PIT bias {mu_e:+.3f}%, sd {sd_e:.3f}%")


if __name__ == "__main__":
    main()
