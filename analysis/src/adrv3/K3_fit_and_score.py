"""WS-K, step 3 and 4: fit the pricing residual on the migrated-cohort share, test the alternatives
that produce the same step, then build cohort-share residual rules and score them on the S harness
(target 2, both FX estimators, both windows) against last_q and persistence.

Fits (n 14, 1Q23 to 2Q26): levels with and without a constant (baseline = 2023-25 mean), changes,
for each K1 variant (central, low_migrant, high_migrant) and basis (nights, listings).
Alternatives: AR(1), linear trend, 2026 dummy, 4Q25-onward dummy, geographic terms (geo_mix_pp,
geo_recon_gap_pp, NA nights-share y/y change), RNPL share y/y change (D's path), and share + AR(1).

Rules (walk-forward, residual history strictly before t, share for t from K1):
  last_q, persistence                     : S reference rules
  K_mech_central  : last_q + 0.007 * (d4share_t - d4share_{t-1})     PRIMARY, pre-stated in K2
  K_mech_high     : last_q + 0.038 * (d4share_t - d4share_{t-1})
  K_level_mech    : expanding mean of pre-migration residuals + 0.007 * d4share_t
  K_level_high    : same at 0.038
  K_fitted_wf     : last_q + b_hat * (d4share_t - d4share_{t-1}), b_hat fitted on prior quarters with
                    d4share > 0 (demeaned levels, no constant), fallback 0.007 when none exist
  K_level_fitted  : expanding pre-migration mean + b_hat * d4share_t, same b_hat
Outputs: K3_residual_fit.csv, K3_alternatives.csv, K3_residual_rule_scores.csv, K3_walk_forward_paths.csv,
K3_rule_residual_paths.csv, K3_pass_table.csv.

py -3.13 analysis/src/adrv3/K3_fit_and_score.py
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import S1_scoring as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "K")
os.makedirs(OUT, exist_ok=True)

H = pd.read_csv(os.path.join(ROOT, "data", "processed", "q3nowcast", "H", "adr_history_components.csv")).set_index("quarter")
Q = list(H.index)  # 1Q23 .. 2Q26
res = H["residual_pricing_pp"].astype(float)
share = pd.read_csv(os.path.join(OUT, "K1_migrated_cohort_share.csv"))
W = pd.read_csv(os.path.join(ROOT, "data", "processed", "adr", "04_regional_quarterly_wide.csv")).set_index("quarter")

PRE_Q = [q for q in Q if q not in ("4Q25", "1Q26", "2Q26")]  # 2023-25 baseline (3Q25 carries a 0.2 pp share; kept in the baseline)
MEAN_2325 = float(res[[q for q in Q if int(q[2:]) <= 25]].mean())
MECH_CENTRAL, MECH_HIGH = 0.007, 0.038  # K2, pre-stated


def d4share(variant, basis, region="blended"):
    s = share[(share.region == region) & (share.basis == basis) & (share.variant == variant)].set_index("quarter")
    return (s["migrated_share_yoy_change"] * 100).astype(float)  # pp


def ols(y, X, const=True):
    y = np.asarray(y, float); X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    if const:
        X = np.column_stack([np.ones(len(y)), X])
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ beta
    dof = max(n - k, 1)
    s2 = float(e @ e) / dof
    cov = s2 * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    tss = float(((y - y.mean()) ** 2).sum()) if const else float((y ** 2).sum())
    r2 = 1 - float(e @ e) / tss if tss > 0 else np.nan
    aic = n * np.log(float(e @ e) / n) + 2 * k
    return {"beta": beta, "se": se, "t": beta / np.where(se > 0, se, np.nan), "r2": r2, "rmse": float(np.sqrt(np.mean(e ** 2))), "aic": aic, "n": n, "k": k, "resid": e}


# ------------------------------------------------------------------------------------------
# 1. fits on the cohort share
# ------------------------------------------------------------------------------------------
fits = []
for variant in ("central", "low_migrant", "high_migrant"):
    for basis in ("nights", "listings"):
        x = d4share(variant, basis).reindex(Q).fillna(0.0)
        y = res.reindex(Q)
        specs = {
            "levels, with constant": (y.values, x.values, True, 1),
            "levels, no constant, baseline = 2023-25 mean": ((y - MEAN_2325).values, x.values, False, 0),
            "changes, with constant": (y.diff().dropna().values, x.diff().dropna().values, True, 1),
            "changes, no constant": (y.diff().dropna().values, x.diff().dropna().values, False, 0),
        }
        for spec, (yy, xx, const, bi) in specs.items():
            f = ols(yy, xx, const)
            b, se, t = float(f["beta"][bi]), float(f["se"][bi]), float(f["t"][bi])
            fits.append({"variant": variant, "basis": basis, "spec": spec, "n": f["n"],
                         "coef_pp_per_pp_share": b, "se": se, "t": t,
                         "const": float(f["beta"][0]) if const else MEAN_2325 if "levels" in spec else 0.0,
                         "r2": f["r2"], "rmse_pp": f["rmse"], "aic": f["aic"],
                         "expected_central": MECH_CENTRAL, "expected_range": "0.000 to 0.038",
                         "ratio_to_expected_central": b / MECH_CENTRAL, "ratio_to_expected_high": b / MECH_HIGH,
                         "within_mechanics": bool(-0.02 <= b <= 0.05),
                         "ci95_low": b - 2.2 * se, "ci95_high": b + 2.2 * se,
                         "share_obs_nonzero": int((x != 0).sum()),
                         "label": "descriptive (OLS on n 14, three to four informative quarters)"})
fits = pd.DataFrame(fits)
fits.to_csv(os.path.join(OUT, "K3_residual_fit.csv"), index=False)

# ------------------------------------------------------------------------------------------
# 2. alternatives that produce the same step
# ------------------------------------------------------------------------------------------
y = res.reindex(Q)
x_c = d4share("central", "nights").reindex(Q).fillna(0.0)
tidx = np.arange(len(Q), dtype=float)
d2026 = pd.Series([1.0 if q.endswith("26") else 0.0 for q in Q], index=Q)
d4q25 = pd.Series([1.0 if q in ("4Q25", "1Q26", "2Q26") else 0.0 for q in Q], index=Q)
geo = H["geo_mix_pp"].reindex(Q).astype(float)
geo_gap = H["geo_recon_gap_pp"].reindex(Q).astype(float)
na_share = W["nights_share_na_pct"].reindex(Q).astype(float)
na_share_yoy = pd.Series([na_share[q] - W.loc[f"{q[:2]}{int(q[2:]) - 1}", "nights_share_na_pct"] for q in Q], index=Q)
na_exfx = W["adr_yoy_exfx_na_pct"].reindex(Q).astype(float)
exna_exfx = pd.Series([(W.loc[q, "adr_yoy_exfx_emea_pct"] * W.loc[q, "nights_share_emea_pct"] + W.loc[q, "adr_yoy_exfx_latam_pct"] * W.loc[q, "nights_share_latam_pct"]
                        + W.loc[q, "adr_yoy_exfx_apac_pct"] * W.loc[q, "nights_share_apac_pct"]) / (100 - W.loc[q, "nights_share_na_pct"]) for q in Q], index=Q)
# RNPL GBV share path (D1_rnpl_parameters: 3Q25 4%, 4Q25 9% assumed; 1Q26 ~20%, 2Q26 21% sourced), converted to nights share at r = 1.25
rnpl_gbv = pd.Series(0.0, index=Q); rnpl_gbv.update(pd.Series({"3Q25": 0.04, "4Q25": 0.09, "1Q26": 0.20, "2Q26": 0.21}))
r_adr = 1.25
rnpl_nights = rnpl_gbv / (r_adr * (1 - rnpl_gbv) + rnpl_gbv) * 100
rnpl_d4 = rnpl_nights  # zero before 3Q25, so the y/y change equals the level
alts = []
def add(name, X, const=True, note="", coef_names=None):
    f = ols(y.values, X, const)
    names = coef_names or [f"x{i}" for i in range(np.asarray(X).ndim if np.asarray(X).ndim > 1 and np.asarray(X).shape[1] > 1 else 1)]
    row = {"model": name, "n": f["n"], "k": f["k"], "r2": f["r2"], "rmse_pp": f["rmse"], "aic": f["aic"], "note": note}
    off = 1 if const else 0
    for i, nm in enumerate(names):
        row[f"coef_{nm}"] = float(f["beta"][off + i]); row[f"t_{nm}"] = float(f["t"][off + i])
    alts.append(row)
    return f
add("constant only (2023-26 mean)", np.zeros((len(Q), 0)) if False else np.ones((len(Q), 1)), const=False, note="reference", coef_names=["const"])
add("cohort share d4 (central, nights)", x_c.values, note="the K model", coef_names=["share"])
add("2026 dummy", d2026.values, note="two quarters", coef_names=["d2026"])
add("4Q25-onward dummy", d4q25.values, note="three quarters, the migration window", coef_names=["d4q25"])
add("linear trend", tidx, note="residual has risen since 2023", coef_names=["trend"])
yl = y.shift(1)
m = yl.notna()
f = ols(y[m].values, yl[m].values, True); alts.append({"model": "AR(1) on the residual", "n": f["n"], "k": f["k"], "r2": f["r2"], "rmse_pp": f["rmse"], "aic": f["aic"], "coef_ar1": float(f["beta"][1]), "t_ar1": float(f["t"][1]), "note": "n 13; rho and its half-life"})
f = ols(y[m].values, np.column_stack([yl[m].values, x_c[m].values]), True); alts.append({"model": "AR(1) + cohort share d4", "n": f["n"], "k": f["k"], "r2": f["r2"], "rmse_pp": f["rmse"], "aic": f["aic"], "coef_ar1": float(f["beta"][1]), "t_ar1": float(f["t"][1]), "coef_share": float(f["beta"][2]), "t_share": float(f["t"][2]), "note": "does the share add to the residual's own persistence"})
f = ols(y[m].values, np.column_stack([yl[m].values, d2026[m].values]), True); alts.append({"model": "AR(1) + 2026 dummy", "n": f["n"], "k": f["k"], "r2": f["r2"], "rmse_pp": f["rmse"], "aic": f["aic"], "coef_ar1": float(f["beta"][1]), "t_ar1": float(f["t"][1]), "coef_d2026": float(f["beta"][2]), "t_d2026": float(f["t"][2]), "note": ""})
add("geographic mix term (geo_mix_pp)", geo.values, note="does the residual absorb the geo term", coef_names=["geo"])
add("geo reconciliation gap (geo_recon_gap_pp)", geo_gap.values, note="H's regional reconstruction gap", coef_names=["geo_gap"])
add("NA nights share y/y change, pp", na_share_yoy.values, note="sub-regional mix proxy", coef_names=["na_share_yoy"])
add("NA ex-FX ADR minus ex-NA ex-FX ADR, pp", (na_exfx - exna_exfx).values, note="regional signature: NA accelerated from 3Q25", coef_names=["na_minus_exna"])
add("RNPL nights share (D path, r 1.25), pp", rnpl_d4.values, note="the other dated 2H25-26 ramp; 3Q25 and 4Q25 assumed", coef_names=["rnpl"])
add("cohort share d4 + RNPL share", np.column_stack([x_c.values, rnpl_d4.values]), note="can the two ramps be separated", coef_names=["share", "rnpl"])
add("cohort share d4 + 2026 dummy", np.column_stack([x_c.values, d2026.values]), note="can the share be separated from a level shift", coef_names=["share", "d2026"])
alts = pd.DataFrame(alts)
alts["corr_share_vs_2026_dummy"] = float(np.corrcoef(x_c.values, d2026.values)[0, 1])
alts["corr_share_vs_rnpl"] = float(np.corrcoef(x_c.values, rnpl_d4.values)[0, 1])
alts["corr_share_vs_trend"] = float(np.corrcoef(x_c.values, tidx)[0, 1])
alts["label"] = "descriptive (n 14; none of these is a causal estimate)"
alts.to_csv(os.path.join(OUT, "K3_alternatives.csv"), index=False)

# ------------------------------------------------------------------------------------------
# 3. residual rules, walk-forward, and the S harness
# ------------------------------------------------------------------------------------------
def rule_paths(variant="central", basis="nights"):
    x = d4share(variant, basis)  # 1Q23..4Q26
    scored = S.quarters_between("1Q24", "2Q26")
    rows = []
    for t in scored:
        prior = [q for q in Q if S.QI[q] < S.QI[t]]
        r_prior = res[prior]
        lq = float(r_prior.iloc[-1])
        pers = float(r_prior.iloc[-2:].mean())
        pre_mean = float(r_prior[[q for q in prior if x.get(q, 0.0) == 0.0]].mean())  # expanding mean over pre-migration quarters
        ds = float(x[t] - x[prior[-1]])
        # walk-forward fitted b: prior quarters with nonzero share, demeaned levels, no constant
        pq = [q for q in prior if x.get(q, 0.0) >= 2.0]  # at least 2 pp of migrated share; 3Q25 (0.2 pp) would give a degenerate slope
        if len(pq) >= 1:
            xx = np.array([x[q] for q in pq]); yy = np.array([res[q] - pre_mean for q in pq])
            b_hat = float((xx @ yy) / (xx @ xx))
            b_src = f"fitted on {len(pq)} prior quarter(s) with share >= 2 pp"
        else:
            b_hat, b_src = MECH_CENTRAL, "no prior migrated quarter: mechanics central"
        rows.append({"quarter": t, "actual_residual_pp": float(res[t]), "d4share_pp": float(x[t]), "dd4share_pp": ds,
                     "pre_migration_mean_pp": pre_mean, "b_hat": b_hat, "b_hat_source": b_src,
                     "last_q": lq, "persistence": pers,
                     "mean_pre_migration": pre_mean, "mean_all_prior": float(r_prior.mean()),
                     "K_mech_central": lq + MECH_CENTRAL * ds,
                     "K_mech_high": lq + MECH_HIGH * ds,
                     "K_level_mech": pre_mean + MECH_CENTRAL * float(x[t]),
                     "K_level_high": pre_mean + MECH_HIGH * float(x[t]),
                     "K_fitted_wf": lq + b_hat * ds,
                     "K_level_fitted": pre_mean + b_hat * float(x[t])})
    return pd.DataFrame(rows).set_index("quarter")


RULES_K = ["last_q", "persistence", "mean_pre_migration", "mean_all_prior", "K_mech_central", "K_mech_high", "K_level_mech", "K_level_high", "K_fitted_wf", "K_level_fitted"]
KNOW = {"last_q": S.KNOWABLE_V2, "persistence": S.KNOWABLE_V2, "mean_pre_migration": S.KNOWABLE_V2, "mean_all_prior": S.KNOWABLE_V2}
for r in RULES_K[4:]:
    KNOW[r] = ("share term yes: the tranche dates (3Q25 and 4Q25 letters, host notices) precede each scored print; the level "
               "calibration to 'over a quarter' and 'about half' is disclosed at the 1Q26 and 2Q26 prints themselves. "
               "Base term as v2: " + S.KNOWABLE_V2)
scores, paths_all, respaths = [], [], []
for variant in ("central", "high_migrant", "low_migrant"):
    rp = rule_paths(variant, "nights")
    rp.insert(0, "variant", variant)
    respaths.append(rp.reset_index())
    for rule in RULES_K:
        if variant != "central" and rule in ("last_q", "persistence", "mean_pre_migration", "mean_all_prior"):
            continue
        name = f"{rule}" if not rule.startswith("K_") else f"{rule}__{variant}"
        exfx = S.exfx_from_residual(rp[rule], mix_variant="measured")
        sc = S.score(exfx, name, KNOW[rule])
        sc.insert(1, "rule", rule); sc.insert(2, "share_variant", variant if rule.startswith("K_") else "n/a")
        scores.append(sc)
        pth = S.paths({name: exfx})
        pth.insert(0, "model_name", name)
        paths_all.append(pth)
scores = pd.concat(scores, ignore_index=True)
# comparison with last_q on the same rows
lq = scores[scores.model == "last_q"].set_index(["target", "window", "fx_estimator"])
scores["last_q_ratio_vs_naive"] = [lq.loc[(t, w, e), "ratio_vs_naive"] for t, w, e in zip(scores.target, scores.window, scores.fx_estimator)]
scores["last_q_jackknife_max"] = [lq.loc[(t, w, e), "jackknife_ratio_max"] for t, w, e in zip(scores.target, scores.window, scores.fx_estimator)]
scores["beats_last_q_ratio"] = scores.ratio_vs_naive < scores.last_q_ratio_vs_naive - 1e-9
scores["beats_last_q_jackknife_max"] = scores.jackknife_ratio_max < scores.last_q_jackknife_max - 1e-9
scores["in_k_criterion"] = (scores.target == "t2_reported_usd_yoy") & scores.fx_estimator.isin(["eur", "baskets"])
scores.to_csv(os.path.join(OUT, "K3_residual_rule_scores.csv"), index=False)
pd.concat(paths_all, ignore_index=True).to_csv(os.path.join(OUT, "K3_walk_forward_paths.csv"), index=False)
pd.concat(respaths, ignore_index=True).to_csv(os.path.join(OUT, "K3_rule_residual_paths.csv"), index=False)

# per-quarter margin of the primary rule over last_q on target 2 (squared-error difference), with a sign test
allp = pd.concat(paths_all, ignore_index=True)
mrows = []
for est in ("eur", "baskets", "midpoint"):
    a = allp[(allp.model_name == "last_q") & (allp.target == "t2_reported_usd_yoy") & (allp.fx_estimator == est)].set_index("quarter")
    b = allp[(allp.model_name == "K_mech_central__central") & (allp.target == "t2_reported_usd_yoy") & (allp.fx_estimator == est)].set_index("quarter")
    for q in a.index:
        e_a = float(a.loc[q, "last_q"] - a.loc[q, "actual"]); e_b = float(b.loc[q, "K_mech_central__central"] - b.loc[q, "actual"])
        mrows.append({"fx_estimator": est, "quarter": q, "err_last_q_pp": e_a, "err_K_mech_central_pp": e_b, "nudge_pp": e_b - e_a,
                      "sq_err_change": e_b ** 2 - e_a ** 2})
margin = pd.DataFrame(mrows)
margin["label"] = "descriptive"
margin.to_csv(os.path.join(OUT, "K3_primary_rule_margin.csv"), index=False)
nz = margin[(margin.fx_estimator == "midpoint") & (margin.nudge_pp.abs() > 1e-6)]
n_help = int((nz.sq_err_change < 0).sum()); n_nz = len(nz)
sign_p = 0.5 ** n_nz if n_help == n_nz else float("nan")
print(f"\nPRIMARY RULE MARGIN: nudged quarters {n_nz}, helped {n_help}, one-sided sign-test p {sign_p:.3f}")

# pre-registered pass per rule and the K criterion (beats last_q on both windows, both estimators, target 2)
pt, kcrit = [], []
for name in scores.model.unique():
    r = S.preregistered_pass(scores, model=name)
    pt.append(S.pass_table(r))
    sub = scores[(scores.model == name) & scores.in_k_criterion]
    kcrit.append({"model": name, "v3_preregistered_pass": r["verdict"], "n_checks_met": r["n_checks_met"],
                  "beats_last_q_ratio_all_4": bool(sub.beats_last_q_ratio.all()), "beats_last_q_jackknife_all_4": bool(sub.beats_last_q_jackknife_max.all()),
                  "n_of_4_beating_last_q_ratio": int(sub.beats_last_q_ratio.sum()),
                  "K_criterion_met": bool(sub.beats_last_q_ratio.all()) and name != "last_q"})
pd.concat(pt, ignore_index=True).to_csv(os.path.join(OUT, "K3_pass_table.csv"), index=False)
kcrit = pd.DataFrame(kcrit)
kcrit["primary_rule_nudged_quarters"] = n_nz; kcrit["primary_rule_quarters_helped"] = n_help; kcrit["primary_rule_sign_test_p"] = sign_p
kcrit.to_csv(os.path.join(OUT, "K3_k_criterion.csv"), index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print("baseline mean 2023-25:", round(MEAN_2325, 3))
print("\nFITS (central, nights):"); print(fits[(fits.variant == "central") & (fits.basis == "nights")][["spec", "coef_pp_per_pp_share", "se", "t", "r2", "rmse_pp", "ratio_to_expected_central", "ratio_to_expected_high", "within_mechanics"]].round(4).to_string())
print("\nFITS all variants, levels no constant:"); print(fits[fits.spec.str.startswith("levels, no")][["variant", "basis", "coef_pp_per_pp_share", "se", "t", "r2", "ratio_to_expected_high"]].round(4).to_string())
print("\nALTERNATIVES:"); print(alts.drop(columns=["label"]).round(3).to_string())
print("\nRULE RESIDUAL PATHS (central):"); print(respaths[0].round(3).to_string())
sub = scores[scores.in_k_criterion][["model", "window", "fx_estimator", "rmse_pp", "rmse_naive_pp", "ratio_vs_naive", "jackknife_ratio_min", "jackknife_ratio_max", "jackknife_below_1", "last_q_ratio_vs_naive", "beats_last_q_ratio"]]
print("\nSCORES (target 2, eur and baskets):"); print(sub.round(3).to_string())
print("\nK CRITERION:"); print(kcrit.to_string())
