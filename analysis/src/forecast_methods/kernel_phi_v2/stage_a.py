"""Stage A — the ACTUAL lag weights by season."""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

from common import (build_panel, usable, ex_covid_mask, OUT, SEASON_NAME,
                    GBV_2Q26, GBV_1Q26)
from phi_fit import (fit_phi, loo_rmse, block_bootstrap_phi, phi_of, ci)

KMAX = 4
PUBLISHED = np.array([0.0, 2 / 3, 1 / 3, 0.0, 0.0])


def samples(panel: pd.DataFrame):
    """The three estimation samples, each already a frame with lags attached."""
    exm = ex_covid_mask(panel)
    return {
        "full_2021Q3+": panel.copy(),
        "ex_covid_nightsyoy_25": panel[exm | panel["gbv_l4"].isna()].copy(),
        "post2023_2023Q1+": panel[panel["q"] >= "2023Q1"].copy(),
    }


def mean_lag(phi):
    return float(np.sum(np.arange(len(phi)) * phi))


def run(panel: pd.DataFrame, n_boot=400, verbose=True):
    os.makedirs(OUT, exist_ok=True)
    smp = samples(panel)
    rows = []
    fits = {}
    for sname, frame in smp.items():
        for mode, tag in [("pooled", "pooled (one phi, 4 c_s)"),
                          ("season", "season-specific phi_{s,k}"),
                          ("summer", "summer(Q3) vs rest")]:
            try:
                fit = fit_phi(frame, kmax=KMAX, mode=mode)
            except Exception as e:                                  # pragma: no cover
                if verbose:
                    print(f"  ! {sname}/{mode}: {e}")
                continue
            fits[(sname, mode)] = fit
            lr, lm, lb, ln, _ = loo_rmse(frame, kmax=KMAX, mode=mode)
            groups = sorted(fit["phi"].keys())
            for g in groups:
                phi = fit["phi"][g]
                if mode == "pooled":
                    gl = "all"
                elif mode == "season":
                    gl = SEASON_NAME[g]
                else:
                    gl = "Q3" if g == 1 else "Q1/Q2/Q4"
                rows.append(dict(
                    sample=sname, spec=mode, spec_label=tag, phi_group=gl,
                    n=fit["n"], n_params=fit["n_params"],
                    **{f"phi_{k}": float(phi[k]) for k in range(KMAX + 1)},
                    phi_1_plus_2=float(phi[1] + phi[2]),
                    mean_lag_q=mean_lag(phi),
                    c_Q1=fit["c"].get(1, np.nan), c_Q2=fit["c"].get(2, np.nan),
                    c_Q3=fit["c"].get(3, np.nan), c_Q4=fit["c"].get(4, np.nan),
                    insample_rel_rmse_pct=fit["rmse_pct"],
                    loo_rel_rmse_pct=lr, loo_mae_pct=lm, loo_bias_pct=lb, loo_n=ln))
        # baselines on the same sample
        for bname, kw in [("fixed_kernel_2/3-1/3", dict(fixed_phi=PUBLISHED)),
                          ("seasonal_lambda_only_phi1=1", dict(single_lag=True))]:
            fit = fit_phi(frame, kmax=KMAX, **kw)
            fits[(sname, bname)] = fit
            lr, lm, lb, ln, _ = loo_rmse(frame, kmax=KMAX, **kw)
            phi = fit["phi"][0]
            rows.append(dict(
                sample=sname, spec=bname, spec_label=bname, phi_group="all (fixed)",
                n=fit["n"], n_params=fit["n_params"],
                **{f"phi_{k}": float(phi[k]) for k in range(KMAX + 1)},
                phi_1_plus_2=float(phi[1] + phi[2]), mean_lag_q=mean_lag(phi),
                c_Q1=fit["c"].get(1, np.nan), c_Q2=fit["c"].get(2, np.nan),
                c_Q3=fit["c"].get(3, np.nan), c_Q4=fit["c"].get(4, np.nan),
                insample_rel_rmse_pct=fit["rmse_pct"],
                loo_rel_rmse_pct=lr, loo_mae_pct=lm, loo_bias_pct=lb, loo_n=ln))
    a1 = pd.DataFrame(rows)
    a1.to_csv(os.path.join(OUT, "A1_phi_estimates.csv"), index=False)

    # ---------------- bootstrap on the two identified specs ------------------
    boot_rows, ident_rows = [], []
    boot_store = {}
    for sname, frame in smp.items():
        for mode in ("pooled", "summer"):
            ph, cc, grp = block_bootstrap_phi(frame, kmax=KMAX, mode=mode,
                                              n_boot=n_boot, block=4)
            if len(ph) == 0:
                continue
            boot_store[(sname, mode)] = (ph, cc, grp)
            for k in range(KMAX + 1):
                lo, hi = ci(ph[:, k])
                boot_rows.append(dict(sample=sname, spec=mode, phi_group="Q3" if mode == "summer" else "all",
                                      k=k, point=float(fits[(sname, mode)] and
                                                       phi_of(fits[(sname, mode)], 3)[k]),
                                      boot_median=float(np.median(ph[:, k])),
                                      ci_lo=lo, ci_hi=hi, n_boot=len(ph)))
            s12 = ph[:, 1] + ph[:, 2]
            lo12, hi12 = ci(s12)
            corr12 = float(np.corrcoef(ph[:, 1], ph[:, 2])[0, 1])
            corr01 = float(np.corrcoef(ph[:, 0], ph[:, 1])[0, 1])
            corr02 = float(np.corrcoef(ph[:, 0], ph[:, 2])[0, 1])
            ident_rows.append(dict(
                sample=sname, spec=mode, n_boot=len(ph),
                phi1_point=float(phi_of(fits[(sname, mode)], 3)[1]),
                phi2_point=float(phi_of(fits[(sname, mode)], 3)[2]),
                phi1_ci_lo=ci(ph[:, 1])[0], phi1_ci_hi=ci(ph[:, 1])[1],
                phi2_ci_lo=ci(ph[:, 2])[0], phi2_ci_hi=ci(ph[:, 2])[1],
                sum12_point=float(phi_of(fits[(sname, mode)], 3)[1] +
                                  phi_of(fits[(sname, mode)], 3)[2]),
                sum12_ci_lo=lo12, sum12_ci_hi=hi12,
                corr_phi1_phi2=corr12, corr_phi0_phi1=corr01, corr_phi0_phi2=corr02,
                phi1_ci_width=ci(ph[:, 1])[1] - ci(ph[:, 1])[0],
                sum12_ci_width=hi12 - lo12))
    pd.DataFrame(boot_rows).to_csv(os.path.join(OUT, "A2_phi_bootstrap_ci.csv"), index=False)
    pd.DataFrame(ident_rows).to_csv(os.path.join(OUT, "A6_identification.csv"), index=False)

    # ---------------- LOO horse race ----------------------------------------
    a3 = a1[["sample", "spec", "n", "n_params", "insample_rel_rmse_pct",
             "loo_rel_rmse_pct", "loo_mae_pct", "loo_bias_pct", "loo_n"]].drop_duplicates()
    base = a3[a3["spec"] == "fixed_kernel_2/3-1/3"].set_index("sample")["loo_rel_rmse_pct"]
    lam = a3[a3["spec"] == "seasonal_lambda_only_phi1=1"].set_index("sample")["loo_rel_rmse_pct"]
    a3 = a3.assign(
        loo_ratio_vs_fixed_kernel=a3.apply(lambda r: r["loo_rel_rmse_pct"] / base[r["sample"]], axis=1),
        loo_ratio_vs_lambda_only=a3.apply(lambda r: r["loo_rel_rmse_pct"] / lam[r["sample"]], axis=1))
    a3.to_csv(os.path.join(OUT, "A3_loo_comparison.csv"), index=False)

    # ---------------- rolling / expanding windows ---------------------------
    u = usable(panel, kmax=KMAX)
    roll = []
    for end in range(11, len(u)):
        for wname, start in [("expanding", 0), ("rolling_12", max(0, end - 11))]:
            sub = u.iloc[start:end + 1]
            if sub["season"].nunique() < 4 or sub["season"].value_counts().min() < 2:
                continue
            try:
                fit = fit_phi(sub, kmax=KMAX, mode="pooled")
            except Exception:
                continue
            phi = fit["phi"][0]
            roll.append(dict(window=wname, end_quarter=u["label"].iloc[end],
                             start_quarter=sub["label"].iloc[0], n=len(sub),
                             **{f"phi_{k}": float(phi[k]) for k in range(KMAX + 1)},
                             phi_1_plus_2=float(phi[1] + phi[2]),
                             mean_lag_q=mean_lag(phi),
                             c_Q3=fit["c"].get(3, np.nan), c_Q4=fit["c"].get(4, np.nan),
                             insample_rel_rmse_pct=fit["rmse_pct"]))
    pd.DataFrame(roll).to_csv(os.path.join(OUT, "A4_rolling_windows.csv"), index=False)

    # ---------------- the dollar map for 2Q26 GBV ---------------------------
    # revenue contribution of GBV_b to quarter b+k  =  c_{s(b+k)} * phi_k * GBV_b
    dm = []
    targets = [(2, 0, "2Q26 (in-quarter)"), (3, 1, "3Q26"), (4, 2, "4Q26"),
               (1, 3, "1Q27"), (2, 4, "2Q27")]
    for sname in smp:
        for mode in ("pooled", "summer"):
            if (sname, mode) not in boot_store:
                continue
            fit = fits[(sname, mode)]
            ph, cc, grp = boot_store[(sname, mode)]
            for season, k, tgt in targets:
                phi_pt = phi_of(fit, season)[k]
                c_pt = fit["c"].get(season, np.nan)
                pt = c_pt / 100.0 * phi_pt * GBV_2Q26
                if mode == "pooled":
                    draws = cc[:, season - 1] / 100.0 * ph[:, k] * GBV_2Q26
                else:
                    gk = 1 if season == 3 else 0
                    pk = np.array([g[gk][k] for g in grp])
                    draws = cc[:, season - 1] / 100.0 * pk * GBV_2Q26
                lo, hi = ci(draws)
                lo80, hi80 = ci(draws, 10, 90)
                dm.append(dict(sample=sname, spec=mode, source_gbv_quarter="2Q26",
                               source_gbv_musd=GBV_2Q26, target_quarter=tgt, lag_k=k,
                               phi_k=phi_pt, c_s_pct=c_pt, revenue_musd=pt,
                               q10=lo80, q90=hi80, ci95_lo=lo, ci95_hi=hi,
                               n_boot=len(draws)))
    # the published kernel, for contrast, on the same dollar map
    for sname in smp:
        fitp = fits[(sname, "fixed_kernel_2/3-1/3")]
        for season, k, tgt in targets:
            dm.append(dict(sample=sname, spec="fixed_kernel_2/3-1/3",
                           source_gbv_quarter="2Q26", source_gbv_musd=GBV_2Q26,
                           target_quarter=tgt, lag_k=k, phi_k=PUBLISHED[k],
                           c_s_pct=fitp["c"].get(season, np.nan),
                           revenue_musd=fitp["c"].get(season, np.nan) / 100.0 *
                           PUBLISHED[k] * GBV_2Q26,
                           q10=np.nan, q90=np.nan, ci95_lo=np.nan, ci95_hi=np.nan,
                           n_boot=0))
    dmf = pd.DataFrame(dm)
    dmf.to_csv(os.path.join(OUT, "A5_dollar_map_2q26_gbv.csv"), index=False)

    # A5b: total lifetime revenue that 2Q26 GBV eventually produces, and the
    # implied effective take rate (a plausibility check against the 13.2% LTM rate)
    tot = (dmf.groupby(["sample", "spec"])["revenue_musd"].sum().reset_index()
           .rename(columns={"revenue_musd": "lifetime_revenue_from_2q26_gbv_musd"}))
    tot["implied_effective_take_rate_pct"] = (
        100.0 * tot["lifetime_revenue_from_2q26_gbv_musd"] / GBV_2Q26)
    tot["ltm_take_rate_2q26_pct"] = 13.2
    tot.to_csv(os.path.join(OUT, "A5b_lifetime_take_rate_check.csv"), index=False)
    return a1, pd.DataFrame(ident_rows), dmf, fits, boot_store
