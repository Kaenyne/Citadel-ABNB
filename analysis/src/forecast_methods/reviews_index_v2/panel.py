"""Stage A: do review counts measure stays? Country x month, review y/y (log) against observed Eurostat
platform-nights y/y (log). Country fixed effects; wild-cluster bootstrap over countries; first differences;
leave-one-country-out; era split; per-country expanding walk-forward vs naive."""
import numpy as np, pandas as pd
import config as C, data as D, index as I, scoring as S


def build_panel(my):
    eu = D.load_eurostat_yoy()
    p = eu[["code", "ymi", "nights", "y_yoy"]].copy()
    sub = my[my.country.isin(C.EU_CODE)]
    for meas in ["yoy_vmatch", "yoy_all", "yoy_mature"]:
        s = I.country_monthly(sub, meas); s["code"] = s.country.map(C.EU_CODE)
        s[f"x_{meas}"] = np.log1p(s[meas])
        p = p.merge(s[["code", "ymi", f"x_{meas}"]], on=["code", "ymi"], how="left")
    return p[p.code.isin(set(C.EU_CODE.values()))]


def fe_ols(df, y, x, group):
    d = df[[y, x, group]].dropna().copy()
    yd = d[y] - d.groupby(group)[y].transform("mean")
    xd = d[x] - d.groupby(group)[x].transform("mean")
    beta = float((xd * yd).sum() / (xd ** 2).sum())
    resid = yd - beta * xd
    se = cluster_se(xd, resid, d[group])
    return beta, se, d, xd, yd, resid


def cluster_se(xd, e, cl):
    s = pd.Series(xd.to_numpy() * e.to_numpy()).groupby(np.asarray(cl)).sum()
    return float(np.sqrt((s ** 2).sum()) / (xd ** 2).sum())


def wild_cluster_p(d, xd, yd, group, B=999, seed=1):
    """Rademacher wild cluster bootstrap of the t statistic under H0 beta = 0 (restricted residuals = yd)."""
    rng = np.random.default_rng(seed)
    beta = float((xd * yd).sum() / (xd ** 2).sum()); t0 = beta / cluster_se(xd, yd - beta * xd, d[group])
    cl = d[group].to_numpy(); ucl = np.unique(cl); pos = pd.Series(range(len(ucl)), index=ucl).reindex(cl).to_numpy()
    xd_np, yd_np = xd.to_numpy(), yd.to_numpy(); sxx = (xd_np ** 2).sum(); ts = []
    for _ in range(B):
        w = rng.choice([-1.0, 1.0], size=len(ucl))[pos]
        ystar = yd_np * w; b = (xd_np * ystar).sum() / sxx; e = ystar - b * xd_np
        s = np.bincount(pos, weights=xd_np * e); se = np.sqrt((s ** 2).sum()) / sxx
        ts.append(b / se if se > 0 else 0.0)
    ts = np.abs(np.array(ts))
    return float((np.sum(ts >= abs(t0)) + 1) / (B + 1)), float(t0)


def first_differences(p, x):
    d = p.sort_values(["code", "ymi"]).copy()
    for c in ["y_yoy", x]:
        d[f"d_{c}"] = d.groupby("code")[c].diff()
        d.loc[d.groupby("code").ymi.diff() != 1, f"d_{c}"] = np.nan
    return d


def per_country_walkforward(p, x):
    rows = []
    for code, g in p.groupby("code"):
        r = S.score_window(g.set_index("ymi")[x], g.set_index("ymi").y_yoy, C.PANEL_START, C.PANEL_SCORE_START,
                           season_lag=12, score_end=C.PANEL_END)
        if r:
            rows.append(dict(code=code, n_scored=r["wf_n"], ratio_vs_naive=r["wf_ratio_vs_naive"],
                             ratio_vs_prior=r["wf_ratio_vs_prior"], rmse=r["wf_rmse"]))
    return pd.DataFrame(rows)


def run_stage_a(my, measure="yoy_vmatch"):
    x = f"x_{measure}"
    p = build_panel(my)
    w = p[(p.ymi >= C.PANEL_START) & (p.ymi <= C.PANEL_END)].dropna(subset=["y_yoy", x])
    rows = []
    beta, se, d, xd, yd, resid = fe_ols(w, "y_yoy", x, "code")
    pA1, t = wild_cluster_p(d, xd, yd, "code")
    n_obs, n_c = len(d), d.code.nunique()
    r2w = 1 - (resid ** 2).sum() / (yd ** 2).sum()
    rows.append(dict(test="A1_elasticity", statistic="beta (country FE)", value=beta, se_cluster=se, t=t, p=pA1,
                     n=n_obs, clusters=n_c, extra=f"within-R2 {r2w:.3f}", pass_line="p<0.01",
                     passed=bool(pA1 < C.PREREG["A1_beta_p_max"])))
    fd = first_differences(w, x)
    bD, seD, dD, xdD, ydD, _ = fe_ols(fd, "d_y_yoy", f"d_{x}", "code")
    pA2, tD = wild_cluster_p(dD, xdD, ydD, "code")
    rows.append(dict(test="A2_first_differences", statistic="beta on d(y/y)", value=bD, se_cluster=seD, t=tD, p=pA2,
                     n=len(dD), clusters=dD.code.nunique(), extra="", pass_line="beta>0, p<0.05",
                     passed=bool(bD > 0 and pA2 < C.PREREG["A2_diff_p_max"])))
    loco = {c: fe_ols(w[w.code != c], "y_yoy", x, "code")[0] for c in sorted(w.code.unique())}
    rows.append(dict(test="A3_leave_one_country_out", statistic="beta range", value=min(loco.values()),
                     se_cluster=np.nan, t=np.nan, p=np.nan, n=len(loco), clusters=n_c,
                     extra=f"max {max(loco.values()):.3f}; all same sign {all(np.sign(v) == np.sign(beta) for v in loco.values())}",
                     pass_line="reported", passed=bool(all(np.sign(v) == np.sign(beta) for v in loco.values()))))
    early = w[w.ymi < C.ymi(2025, 1)]; late = w[w.ymi >= C.ymi(2025, 1)]
    b1, s1 = fe_ols(early, "y_yoy", x, "code")[:2]; b2, s2 = fe_ols(late, "y_yoy", x, "code")[:2]
    z = (b2 - b1) / np.sqrt(s1 ** 2 + s2 ** 2)
    rows.append(dict(test="A4_era_split", statistic="beta 2023-24 vs 2025-26", value=b1, se_cluster=s1, t=z, p=np.nan,
                     n=len(early) + len(late), clusters=n_c, extra=f"beta late {b2:.3f} se {s2:.3f}; |z| {abs(z):.2f}",
                     pass_line="reported (|z|<2)", passed=bool(abs(z) < 2)))
    pc = per_country_walkforward(p, x)
    med = float(pc.ratio_vs_naive.median())
    rows.append(dict(test="A5_out_of_sample_by_country", statistic="median walk-forward RMSE ratio vs naive", value=med,
                     se_cluster=np.nan, t=np.nan, p=np.nan, n=int(pc.n_scored.sum()), clusters=len(pc),
                     extra=f"countries<=0.75: {int((pc.ratio_vs_naive <= 0.75).sum())}/{len(pc)}",
                     pass_line="median<=0.75", passed=bool(med <= C.PREREG["A5_median_ratio_max"])))
    t = pd.DataFrame(rows); t.insert(0, "measure", measure)
    return t, p, pc
