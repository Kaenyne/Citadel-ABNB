"""
Workstream C: reaction-function tests on the 23-print panel.

Pre-stated design (written before the numbers were run):
  PRIMARY target   : ret_1d_cc_excess_pct (close before the print to close of the reaction session, minus QQQ).
                     This is the market's revaluation of the print; the executable open-entry return is reported
                     alongside because a trader cannot capture the gap.
  PRIMARY sample   : ex_reopening = 3Q22-2Q26 (16 prints). The 2021-1H22 prints carry +/-30 to +/-180pt base
                     effects in nights acceleration and 2019-basis guides, so they are excluded from the primary
                     sample and shown as robustness.
  PRIMARY features : (1) nights_accel_sign, (2) nights_yoy_accel_pts, (3) guide_dir_code, (4) guide_dir_pts,
                     (5) momentum_score, (6) revenue_surprise_pct, (7) rev_beat_vs_guide_top_pct,
                     (8) eps_surprise_bps_px, (9) fy_raised, (10) nights_surprise_pct, (11) guide_vs_street_pct,
                     (12) pre_runup_20d_pct.                                           -> 12 primary univariate tests
  PRIMARY multivariate: M1 accel_sign + guide_dir_code; M2 = M1 + revenue_surprise; M3 accel_pts + guide_dir_pts;
                     M4 = M3 + revenue_surprise; M5 = M2 + eps_surprise_bps_px + fy_raised.   -> 5 primary tests
  Everything else (other targets, other samples) is SECONDARY robustness and is labelled so in the output.
  Selection rule: a feature "survives" if, on the primary target and sample, LOO R2 > 0 AND the coefficient sign
  is the same in every leave-one-out fit AND the permutation p for R2 is < 0.10. Report everything either way.

Outputs (data/processed/reverse_dcf/C/):
  C_univariate_tests.csv, C_multivariate_tests.csv, C_sorted_portfolios.csv, C_feature_ranking.csv,
  C_case_study_2q26.csv, C_test_count.csv, C_deadband_sensitivity.csv, C_multiplicity_holm.csv, C_fragility.csv
Audit (audit_C.md, 12 Sep) fixes applied: Fisher between-bucket tests and raw-return counts (1), Holm table (2), dead-band
sensitivity (3), 2Q26-stable recode and guide-vs-Street drop-print fragility (4, 6), gap/intraday split (7), clipped 4Q21
guide-vs-Street in the all sample (9), full-precision target (10).
Run: py -3.13 analysis/src/reverse_dcf/C_02_reaction_tests.py
"""
from pathlib import Path
import itertools
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/reverse_dcf/C"
rng = np.random.default_rng(20260912)
N_PERM = 2000

TARGETS = {
    "ret_1d_cc_excess_pct": "day-1 close-to-close excess vs QQQ (primary)",
    "ret_1d_cc_raw_pct": "day-1 close-to-close raw",
    "ret_1d_open_excess_pct": "day-1 executable next-open to close, excess",
    "ev_ntm_rev_multiple_change_pct": "EV/NTM revenue multiple change on the print (WS12)",
    "ret_5d_cc_excess_pct": "5-session close-to-close excess",
    "ret_20d_cc_excess_pct": "20-session close-to-close excess",
    "ret_20d_open_excess_pct": "20-session executable open-entry excess",
}
SAMPLES = {"ex_reopening": "sample_ex_reopening", "all": "sample_all", "post2022": "sample_post2022"}
FEATURES = ["nights_accel_sign", "nights_yoy_accel_pts", "guide_dir_code", "guide_dir_pts", "momentum_score",
            "revenue_surprise_pct", "rev_beat_vs_guide_top_pct", "eps_surprise_bps_px", "fy_raised",
            "nights_surprise_pct", "guide_vs_street_pct", "pre_runup_20d_pct"]
MULTI = {
    "M1_accel_sign+guide_dir_code": ["nights_accel_sign", "guide_dir_code"],
    "M2_M1+revenue_surprise": ["nights_accel_sign", "guide_dir_code", "revenue_surprise_pct"],
    "M3_accel_pts+guide_dir_pts": ["nights_yoy_accel_pts", "guide_dir_pts"],
    "M4_M3+revenue_surprise": ["nights_yoy_accel_pts", "guide_dir_pts", "revenue_surprise_pct"],
    "M5_M2+eps+fy_raised": ["nights_accel_sign", "guide_dir_code", "revenue_surprise_pct", "eps_surprise_bps_px", "fy_raised"],
    # POST-HOC (added after the univariate results were seen; combines the two strongest univariate features)
    "M6_posthoc_accel_sign+guide_vs_street": ["nights_accel_sign", "guide_vs_street_pct"],
    "M7_posthoc_M6+guide_dir_code": ["nights_accel_sign", "guide_vs_street_pct", "guide_dir_code"],
    "M8_posthoc_M6+revenue_surprise": ["nights_accel_sign", "guide_vs_street_pct", "revenue_surprise_pct"],
}
POST_HOC = {"M6_posthoc_accel_sign+guide_vs_street", "M7_posthoc_M6+guide_dir_code", "M8_posthoc_M6+revenue_surprise"}
PRIMARY_TARGET = "ret_1d_cc_excess_pct"
PRIMARY_SAMPLE = "ex_reopening"


def ols(X, y):
    """OLS with HC1 standard errors. X includes a constant column."""
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    hc1 = XtX_inv @ (X.T * (e ** 2)) @ X @ XtX_inv * n / max(n - k, 1)
    se = np.sqrt(np.diag(hc1))
    t = b / np.where(se > 0, se, np.nan)
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (e ** 2).sum() / ss_tot if ss_tot > 0 else np.nan
    adj = 1 - (1 - r2) * (n - 1) / max(n - k, 1)
    return b, se, t, r2, adj, e


def loo(X, y):
    n = len(y)
    pred = np.empty(n)
    pred_mean = np.empty(n)
    coefs = []
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        b = np.linalg.pinv(X[m].T @ X[m]) @ X[m].T @ y[m]
        pred[i] = X[i] @ b
        pred_mean[i] = y[m].mean()
        coefs.append(b)
    sse = ((y - pred) ** 2).sum()
    sse_mean = ((y - pred_mean) ** 2).sum()
    return 1 - sse / sse_mean, np.sqrt(sse / n), np.sqrt(sse_mean / n), np.array(coefs)


def perm_p(X, y, r2_obs):
    cnt = 0
    for _ in range(N_PERM):
        yp = rng.permutation(y)
        _, _, _, r2, _, _ = ols(X, yp)
        cnt += r2 >= r2_obs
    return (cnt + 1) / (N_PERM + 1)


def fit_spec(df, feats, target, sample_name, spec_name, primary):
    d = df.loc[df[SAMPLES[sample_name]], feats + [target]].dropna()
    n = len(d)
    if n < len(feats) + 4:
        return None
    X = np.column_stack([np.ones(n)] + [d[f].values.astype(float) for f in feats])
    y = d[target].values.astype(float)
    b, se, t, r2, adj, e = ols(X, y)
    loo_r2, loo_rmse, naive_rmse, coefs = loo(X, y)
    p = perm_p(X, y, r2)
    row = {"spec": spec_name, "features": "+".join(feats), "target": target, "sample": sample_name, "n": n,
           "primary": primary, "r2": round(r2, 4), "adj_r2": round(adj, 4), "loo_r2": round(loo_r2, 4),
           "loo_rmse": round(loo_rmse, 3), "naive_rmse": round(naive_rmse, 3), "perm_p_r2": round(p, 4),
           "const": round(b[0], 3), "resid_sd": round(e.std(ddof=len(feats) + 1), 3)}
    for j, f in enumerate(feats, start=1):
        row[f"b_{f}"] = round(b[j], 4)
        row[f"t_{f}"] = round(t[j], 2)
        row[f"loo_sign_stability_{f}"] = round(float((np.sign(coefs[:, j]) == np.sign(b[j])).mean()), 2)
        row[f"loo_b_min_{f}"] = round(coefs[:, j].min(), 4)
        row[f"loo_b_max_{f}"] = round(coefs[:, j].max(), 4)
    if len(feats) == 1:
        row["b"] = row[f"b_{feats[0]}"]
        row["t_hc1"] = row[f"t_{feats[0]}"]
        row["loo_sign_stability"] = row[f"loo_sign_stability_{feats[0]}"]
        row["spearman"] = round(stats.spearmanr(d[feats[0]], d[target]).statistic, 3)
        row["pearson"] = round(stats.pearsonr(d[feats[0]], d[target]).statistic, 3)
        row["survives_rule"] = bool(loo_r2 > 0 and row["loo_sign_stability"] == 1.0 and p < 0.10)
    else:
        row["survives_rule"] = bool(loo_r2 > 0 and p < 0.10)
    return row


def sorted_portfolios(df):
    rows = []
    targets = ["ret_1d_cc_excess_pct", "ret_1d_cc_raw_pct", "ret_1d_open_excess_pct", "gap_excess_pct", "intraday_excess_pct",
               "ev_ntm_rev_multiple_change_pct", "ret_5d_cc_excess_pct", "ret_20d_cc_excess_pct", "ret_20d_open_excess_pct"]
    sorts = {
        "guide_dir": ("guide_dir", {"accelerating": "accelerating", "stable": "stable", "decelerating": "decelerating"}),
        "nights_accel_sign": ("nights_accel_sign", {1.0: "accelerating", 0.0: "flat", -1.0: "decelerating"}),
        "momentum_score": ("momentum_score", {2.0: "+2 both accel", 1.0: "+1", 0.0: "0", -1.0: "-1", -2.0: "-2 both decel"}),
        "guide_dir_x_q4print": None,
        "accel_sign_x_guide_dir": None,
    }
    df = df.copy()
    df["is_q4_print"] = df["label"].str.startswith("4Q")
    df["guide_x_q4"] = df["guide_dir"].astype(str) + np.where(df["is_q4_print"], " | Q4 print", " | non-Q4 print")
    df["accel_x_guide"] = ("printed " + df["nights_accel_sign"].map({1.0: "accel", 0.0: "flat", -1.0: "decel"}).astype(str)
                           + " | guide " + df["guide_dir"].astype(str))
    sorts["guide_dir_x_q4print"] = ("guide_x_q4", None)
    sorts["accel_sign_x_guide_dir"] = ("accel_x_guide", None)
    for sample_name, col in SAMPLES.items():
        d0 = df[df[col]]
        for sort_name, (scol, labels) in sorts.items():
            for target in targets:
                base_pos = (d0[target].dropna() > 0).mean()
                groups = d0.dropna(subset=[scol, target]).groupby(scol)
                for key, g in groups:
                    if isinstance(key, float) and key != key:
                        continue
                    lab = labels.get(key, str(key)) if labels else str(key)
                    v = g[target].values
                    n = len(v)
                    npos = int((v > 0).sum())
                    rows.append({"sample": sample_name, "sort": sort_name, "bucket": lab, "target": target, "n": n,
                                 "mean": round(v.mean(), 2), "median": round(np.median(v), 2), "min": round(v.min(), 2),
                                 "max": round(v.max(), 2), "n_positive": npos, "hit_rate_positive": round(npos / n, 2),
                                 "sample_base_rate_positive": round(base_pos, 2),
                                 "binom_p_vs_half": round(stats.binomtest(npos, n, 0.5).pvalue, 3) if n > 0 else np.nan,
                                 "binom_p_vs_base_rate_1sided": round(min(stats.binomtest(npos, n, base_pos, alternative="less").pvalue,
                                                                          stats.binomtest(npos, n, base_pos, alternative="greater").pvalue), 3) if n > 0 else np.nan,
                                 "prints": " ".join(g["label"])})
                # two-bucket comparison accel vs decel where defined
                if labels:
                    ga = d0[(d0[scol] == list(labels.keys())[0])][target].dropna()
                    gd = d0[(d0[scol] == list(labels.keys())[-1])][target].dropna()
                    if len(ga) >= 2 and len(gd) >= 2:
                        mw = stats.mannwhitneyu(ga, gd, alternative="two-sided").pvalue
                        tt = stats.ttest_ind(ga, gd, equal_var=False).pvalue
                        # audit fix 1: the between-bucket test on the share positive is the test the sign claim needs
                        fisher = stats.fisher_exact([[int((ga > 0).sum()), int((ga <= 0).sum())],
                                                     [int((gd > 0).sum()), int((gd <= 0).sum())]]).pvalue
                        rows.append({"sample": sample_name, "sort": sort_name, "bucket": "TOP minus BOTTOM", "target": target,
                                     "n": len(ga) + len(gd), "mean": round(ga.mean() - gd.mean(), 2),
                                     "median": round(np.median(ga) - np.median(gd), 2), "min": np.nan, "max": np.nan,
                                     "n_positive": np.nan, "hit_rate_positive": np.nan, "sample_base_rate_positive": np.nan,
                                     "binom_p_vs_half": np.nan, "mann_whitney_p": round(mw, 3), "welch_p": round(tt, 3),
                                     "fisher_p_share_positive": round(fisher, 3),
                                     "prints": "top " + str(int((ga > 0).sum())) + "/" + str(len(ga)) + " positive vs bottom " + str(int((gd > 0).sum())) + "/" + str(len(gd))})
    return pd.DataFrame(rows)


def deadband_sensitivity(df):
    """Audit fix 3: the sign result under alternative dead bands, both samples, primary target."""
    rows = []
    for band in [0.0, 0.25, 0.5, 1.0, 1.5]:
        d0 = df.copy()
        d0["sign_b"] = np.where(d0["nights_yoy_accel_pts"] > band, 1.0, np.where(d0["nights_yoy_accel_pts"] < -band, -1.0, 0.0))
        d0.loc[d0["nights_yoy_accel_pts"].isna(), "sign_b"] = np.nan
        for sname, col in [("ex_reopening", "sample_ex_reopening"), ("post2022", "sample_post2022")]:
            d = d0[d0[col]].dropna(subset=["sign_b", PRIMARY_TARGET])
            a = d[d["sign_b"] == 1][PRIMARY_TARGET]; de = d[d["sign_b"] == -1][PRIMARY_TARGET]; fl = d[d["sign_b"] == 0]
            X = np.column_stack([np.ones(len(d)), d["sign_b"].values]); y = d[PRIMARY_TARGET].values
            b, se, t, r2, adj, e = ols(X, y); loo_r2, _, _, _ = loo(X, y)
            fisher = stats.fisher_exact([[int((a > 0).sum()), int((a <= 0).sum())], [int((de > 0).sum()), int((de <= 0).sum())]]).pvalue if len(a) and len(de) else np.nan
            rows.append({"dead_band_pts": band, "sample": sname, "accel_n": len(a), "accel_positive": int((a > 0).sum()), "accel_mean": round(a.mean(), 2) if len(a) else np.nan,
                         "decel_n": len(de), "decel_positive": int((de > 0).sum()), "decel_mean": round(de.mean(), 2) if len(de) else np.nan,
                         "flat_prints": " ".join(fl["label"]), "b_sign": round(b[1], 2), "t_hc1": round(t[1], 2), "r2": round(r2, 3), "loo_r2": round(loo_r2, 3),
                         "fisher_p": round(fisher, 3) if fisher == fisher else np.nan})
    return pd.DataFrame(rows)


def holm_table(uni, multi):
    """Audit fix 2: Holm step-down over the 17 pre-stated specs, and the 36-test primary-target univariate family."""
    pre = pd.concat([uni[uni["primary"]][["spec", "perm_p_r2"]], multi[multi["primary"]][["spec", "perm_p_r2"]]]).sort_values("perm_p_r2").reset_index(drop=True)
    pre["family"] = "17 pre-stated specs (primary target, primary sample)"
    pre["rank"] = range(1, len(pre) + 1)
    pre["holm_threshold"] = 0.05 / (len(pre) - pre["rank"] + 1)
    pre["clears_holm"] = pre["perm_p_r2"] < pre["holm_threshold"]
    pre["bonferroni_p"] = (pre["perm_p_r2"] * len(pre)).clip(upper=1)
    fam = uni[(uni["target"] == PRIMARY_TARGET)][["spec", "sample", "perm_p_r2"]].sort_values("perm_p_r2").reset_index(drop=True)
    fam["spec"] = fam["spec"] + " [" + fam["sample"] + "]"
    fam = fam.drop(columns=["sample"])
    fam["family"] = "36 primary-target univariate tests across three samples"
    fam["rank"] = range(1, len(fam) + 1)
    fam["holm_threshold"] = 0.05 / (len(fam) - fam["rank"] + 1)
    fam["clears_holm"] = fam["perm_p_r2"] < fam["holm_threshold"]
    fam["bonferroni_p"] = (fam["perm_p_r2"] * len(fam)).clip(upper=1)
    return pd.concat([pre, fam], ignore_index=True)


def fragility(df):
    """Audit fixes 4 and 6: guide-vs-Street with influential prints dropped; guide direction with 2Q26 recoded stable."""
    rows = []
    base = df[df["sample_ex_reopening"]]
    for drop in [[], ["2Q24"], ["4Q22"], ["2Q26"], ["2Q24", "2Q26"], ["2Q24", "4Q22"]]:
        d = base[~base["label"].isin(drop)][["label", "guide_vs_street_pct", "nights_accel_sign", PRIMARY_TARGET]].dropna()
        X = np.column_stack([np.ones(len(d)), d["guide_vs_street_pct"].values]); y = d[PRIMARY_TARGET].values
        b, se, t, r2, adj, e = ols(X, y); loo_r2, _, _, _ = loo(X, y)
        X2 = np.column_stack([np.ones(len(d)), d["nights_accel_sign"].values, d["guide_vs_street_pct"].values])
        b2, se2, t2, r22, adj2, e2 = ols(X2, y); loo2, _, _, _ = loo(X2, y)
        rows.append({"test": "guide_vs_street univariate, ex_reopening", "dropped": " ".join(drop) or "none", "n": len(d), "b": round(b[1], 2), "t_hc1": round(t[1], 2),
                     "r2": round(r2, 3), "loo_r2": round(loo_r2, 3),
                     "M6_b_sign": round(b2[1], 2), "M6_t_sign": round(t2[1], 2), "M6_b_gvs": round(b2[2], 2), "M6_t_gvs": round(t2[2], 2), "M6_r2": round(r22, 3), "M6_loo_r2": round(loo2, 3), "note": ""})
    d = base.copy(); d.loc[d["label"] == "2Q26", "guide_dir_code"] = 0.0; d.loc[d["label"] == "2Q26", "guide_dir"] = "stable"
    for lab, g in d.groupby("guide_dir"):
        v = g[PRIMARY_TARGET]
        rows.append({"test": "guide_dir buckets with 2Q26 recoded stable, ex_reopening", "dropped": lab, "n": len(v), "b": round(v.mean(), 2), "t_hc1": np.nan,
                     "r2": np.nan, "loo_r2": np.nan, "M6_b_sign": np.nan, "M6_t_sign": np.nan, "M6_b_gvs": np.nan, "M6_t_gvs": np.nan, "M6_r2": np.nan, "M6_loo_r2": np.nan,
                     "note": "mean; " + str(int((v > 0).sum())) + "/" + str(len(v)) + " positive; prints " + " ".join(g["label"])})
    dd = d[["guide_dir_code", "nights_accel_sign", PRIMARY_TARGET]].dropna()
    X = np.column_stack([np.ones(len(dd)), dd["nights_accel_sign"].values, dd["guide_dir_code"].values]); y = dd[PRIMARY_TARGET].values
    b, se, t, r2, adj, e = ols(X, y); loo_r2, _, _, _ = loo(X, y)
    rows.append({"test": "M1 sign + guide_dir with 2Q26 recoded stable, ex_reopening", "dropped": "none", "n": len(dd), "b": round(b[2], 2), "t_hc1": round(t[2], 2),
                 "r2": round(r2, 3), "loo_r2": round(loo_r2, 3), "M6_b_sign": round(b[1], 2), "M6_t_sign": round(t[1], 2), "M6_b_gvs": np.nan, "M6_t_gvs": np.nan, "M6_r2": np.nan, "M6_loo_r2": np.nan,
                 "note": "b and t here are the guide_dir_code coefficient; M6_b_sign / M6_t_sign are the sign coefficient in the same fit"})
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(OUT / "C_print_panel.csv")
    # winsorise the pts features for the 'all' sample only (2021-22 base effects); primary sample is untouched
    df["nights_yoy_accel_pts_w"] = df["nights_yoy_accel_pts"].clip(-10, 10)

    uni = []
    for sample_name in SAMPLES:
        for target in TARGETS:
            for f in FEATURES:
                feat = f
                if sample_name == "all" and f == "nights_yoy_accel_pts":
                    feat = "nights_yoy_accel_pts_w"
                if sample_name == "all" and f == "guide_vs_street_pct":
                    feat = "guide_vs_street_pct_clipped"   # audit fix 9
                primary = (sample_name == PRIMARY_SAMPLE and target == PRIMARY_TARGET)
                r = fit_spec(df, [feat], target, sample_name, f"U_{f}", primary)
                if r:
                    uni.append(r)
    uni = pd.DataFrame(uni)
    uni.to_csv(OUT / "C_univariate_tests.csv", index=False)

    multi = []
    for sample_name in SAMPLES:
        for target in TARGETS:
            for name, feats in MULTI.items():
                feats2 = [("nights_yoy_accel_pts_w" if (sample_name == "all" and f == "nights_yoy_accel_pts") else
                           ("guide_vs_street_pct_clipped" if (sample_name == "all" and f == "guide_vs_street_pct") else f)) for f in feats]
                primary = (sample_name == PRIMARY_SAMPLE and target == PRIMARY_TARGET)
                r = fit_spec(df, feats2, target, sample_name, name, primary and name not in POST_HOC)
                if r:
                    r["post_hoc"] = name in POST_HOC
                    multi.append(r)
    multi = pd.DataFrame(multi)
    multi.to_csv(OUT / "C_multivariate_tests.csv", index=False)

    # ranking on the primary target: by LOO R2 across the three samples
    rank_rows = []
    for f in FEATURES:
        r = {"feature": f}
        for s in SAMPLES:
            fname = "nights_yoy_accel_pts_w" if (s == "all" and f == "nights_yoy_accel_pts") else ("guide_vs_street_pct_clipped" if (s == "all" and f == "guide_vs_street_pct") else f)
            u = uni[(uni["target"] == PRIMARY_TARGET) & (uni["sample"] == s) & (uni["features"] == fname)]
            if len(u):
                u = u.iloc[0]
                r[f"{s}_n"] = u["n"]; r[f"{s}_b"] = u["b"]; r[f"{s}_t"] = u["t_hc1"]; r[f"{s}_r2"] = u["r2"]
                r[f"{s}_loo_r2"] = u["loo_r2"]; r[f"{s}_perm_p"] = u["perm_p_r2"]; r[f"{s}_sign_stab"] = u["loo_sign_stability"]
        m = uni[(uni["target"] == "ev_ntm_rev_multiple_change_pct") & (uni["sample"] == PRIMARY_SAMPLE) & (uni["features"] == f)]
        if len(m):
            m = m.iloc[0]
            r["multiple_b"] = m["b"]; r["multiple_t"] = m["t_hc1"]; r["multiple_loo_r2"] = m["loo_r2"]; r["multiple_n"] = m["n"]
        o = uni[(uni["target"] == "ret_1d_open_excess_pct") & (uni["sample"] == PRIMARY_SAMPLE) & (uni["features"] == f)]
        if len(o):
            o = o.iloc[0]
            r["open_b"] = o["b"]; r["open_t"] = o["t_hc1"]; r["open_loo_r2"] = o["loo_r2"]
        rank_rows.append(r)
    rank = pd.DataFrame(rank_rows).sort_values("ex_reopening_loo_r2", ascending=False)
    rank.to_csv(OUT / "C_feature_ranking.csv", index=False)

    sp = sorted_portfolios(df)
    sp.to_csv(OUT / "C_sorted_portfolios.csv", index=False)

    # 2Q26 case study: fitted values from the primary multivariate specs
    cs = []
    row = df[df["label"] == "2Q26"].iloc[0]
    for name, feats in MULTI.items():
        m = multi[(multi["spec"] == name) & (multi["target"] == PRIMARY_TARGET) & (multi["sample"] == PRIMARY_SAMPLE)]
        if not len(m):
            continue
        m = m.iloc[0]
        fitted = m["const"] + sum(m[f"b_{f}"] * row[f] for f in feats)
        cs.append({"spec": name, "sample": PRIMARY_SAMPLE, "actual_ret_1d_cc_excess_pct": row[PRIMARY_TARGET],
                   "fitted_pct": round(fitted, 2), "residual_pct": round(row[PRIMARY_TARGET] - fitted, 2),
                   "inputs": "; ".join(f"{f}={row[f]:.2f}" for f in feats)})
    # the same fit without 2Q26 in the training sample (is it an outlier relative to the function estimated on the others?)
    for name, feats in MULTI.items():
        d = df[df["sample_ex_reopening"] & (df["label"] != "2Q26")][feats + [PRIMARY_TARGET]].dropna()
        X = np.column_stack([np.ones(len(d))] + [d[f].values for f in feats])
        b = np.linalg.pinv(X.T @ X) @ X.T @ d[PRIMARY_TARGET].values
        fitted = b[0] + sum(b[j + 1] * row[f] for j, f in enumerate(feats))
        cs.append({"spec": name + " (fit excludes 2Q26)", "sample": PRIMARY_SAMPLE,
                   "actual_ret_1d_cc_excess_pct": row[PRIMARY_TARGET], "fitted_pct": round(fitted, 2),
                   "residual_pct": round(row[PRIMARY_TARGET] - fitted, 2),
                   "inputs": "; ".join(f"b_{f}={b[j + 1]:.2f}" for j, f in enumerate(feats)) + f"; const={b[0]:.2f}"})
    cs.append({"spec": "decomposition (WS12)", "sample": "", "actual_ret_1d_cc_excess_pct": row[PRIMARY_TARGET],
               "fitted_pct": np.nan, "residual_pct": np.nan,
               "inputs": f"raw +{row['ret_1d_cc_raw_pct']:.1f}%; gap {row['gap_pct']:.1f}%; open-to-close excess {row['ret_1d_open_excess_pct']:.1f}%; "
                         f"NTM revenue estimate change {row['ntm_rev_estimate_change_pct']:.1f}%; EV/NTM revenue multiple change {row['ev_ntm_rev_multiple_change_pct']:.1f}%; "
                         f"nights +{row['nights_yoy_pct']:.1f}% (accel {row['nights_yoy_accel_pts']:+.1f}pts, surprise {row['nights_surprise_pct']:+.1f}%); "
                         f"revenue surprise {row['revenue_surprise_pct']:+.1f}%; EPS surprise {row['eps_surprise_pct_comparable']:+.1f}%; "
                         f"guide {row['guide_dir']} ({row['guide_dir_pts']:+.1f}pts); guide vs Street {row['guide_vs_street_pct']:+.1f}%; FY raised {int(row['fy_raised'])}"})
    pd.DataFrame(cs).to_csv(OUT / "C_case_study_2q26.csv", index=False)

    deadband_sensitivity(df).to_csv(OUT / "C_deadband_sensitivity.csv", index=False)
    holm_table(uni, multi).to_csv(OUT / "C_multiplicity_holm.csv", index=False)
    fragility(df).to_csv(OUT / "C_fragility.csv", index=False)

    # test count
    tc = pd.DataFrame([
        {"family": "univariate regressions", "n_tests": len(uni), "n_primary": int(uni["primary"].sum())},
        {"family": "multivariate regressions", "n_tests": len(multi), "n_primary": int(multi["primary"].sum())},
        {"family": "sorted-portfolio cells (descriptive, incl. top-minus-bottom rows)", "n_tests": len(sp), "n_primary": 0},
        {"family": "prior team tests (04: 97; predictive 04: 189 contemporaneous + 180 pre-print; WS20: 195)", "n_tests": 97 + 189 + 180 + 195, "n_primary": 0},
    ])
    tc.to_csv(OUT / "C_test_count.csv", index=False)

    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print("=== primary univariate (ret_1d_cc_excess, ex_reopening) ===")
    print(uni[uni["primary"]][["features", "n", "b", "t_hc1", "pearson", "spearman", "r2", "loo_r2", "perm_p_r2",
                               "loo_sign_stability", "survives_rule"]].to_string())
    print("=== primary multivariate ===")
    cols = [c for c in multi.columns if c.startswith(("b_", "t_"))]
    print(multi[multi["primary"]][["spec", "n", "r2", "adj_r2", "loo_r2", "perm_p_r2", "const", "survives_rule"] + cols].to_string())
    print("=== ranking ===")
    print(rank.to_string())
    print("=== sorted: guide_dir and accel sign, primary target, ex_reopening ===")
    print(sp[(sp["sample"] == "ex_reopening") & (sp["target"] == PRIMARY_TARGET) & (sp["sort"].isin(["guide_dir", "nights_accel_sign", "momentum_score", "guide_dir_x_q4print", "accel_sign_x_guide_dir"]))]
          [["sort", "bucket", "n", "mean", "median", "n_positive", "hit_rate_positive", "binom_p_vs_half", "prints"]].to_string())
    print(pd.DataFrame(cs).to_string())


if __name__ == "__main__":
    main()
