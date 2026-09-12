"""
WS-S step 2: rescore every J3 model variant and the benchmarks through the S1 harness on the two
pre-registered v3 targets, and apply the pre-registered v3 criterion to the last_q rule.

Outputs (data/processed/adrv3/S/):
  reproduction_check_vs_J3.csv   S1 in J3 mode against data/processed/adrq3/J/card_v2_backtest.csv
  rescore_v2.csv                 every model and benchmark, both targets, both windows, three FX estimators
  rescore_v2_summary.csv         one row per model x target x window x fx: ratio and jackknife
  harness_change_isolation.csv   the same rule under J3's target, target 1 and target 2, so the
                                 scoring fix can be separated from the rule change
  v3_preregistered_result.csv    the last_q rule under preregistered_pass(): PASS or FAIL with numbers
  walk_forward_paths.csv         per quarter actual, naive, prior year, AR(1) and every model, in
                                 scored units, under each target and FX estimator
  error_attribution_v3.csv       per-quarter error of the last_q model split into residual-rule
                                 error, new-business-and-interaction fill error, rounding (t1) and
                                 FX-estimator error plus the disclosed identity gap (t2)

Run: py -3.13 analysis/src/adrv3/S2_rescore_v2.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import S1_scoring as S  # noqa: E402

ROOT = S.ROOT
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "S")
os.makedirs(OUT, exist_ok=True)
pd.set_option("display.width", 250)

# 1. reproduction check against the v2 record (stop if it fails)
cmp, ok = S.reproduce_j3()
cmp.to_csv(os.path.join(OUT, "reproduction_check_vs_J3.csv"), index=False)
print(f"reproduction check vs J3 card_v2_backtest.csv: {len(cmp)} rows, max abs diff {cmp.max_abs_diff.max():.6f} -> {'OK' if ok else 'MISMATCH'}")
if not ok:
    raise SystemExit("S1 does not reproduce J3 to 0.001; investigate before rescoring")

# 2. rescore on the v3 targets
paths = S.v2_model_paths()
models = {m: paths[m] for m in S.V2_MODELS}
if "h_route_a" in paths:
    models["h_route_a"] = paths["h_route_a"]
parts = [S.score_benchmarks()]
for m, s in models.items():
    parts.append(S.score(s, m, S.knowable_flag_v2(m)))
res = pd.concat(parts, ignore_index=True)
res["residual_rule"] = res.model.map(lambda m: m.split("_", 2)[2] if m.startswith("v2_") else "")
res["mix_variant"] = res.model.map(lambda m: "measured (realised quarter-t terms, upper bound on I)" if m.startswith("v2_measured")
                                   else "trailing 4q (H rule)" if m.startswith("v2_trailing4q") else "")
res["v3_pre_registered_rule"] = res.model == S.V3_RULE_MODEL
res["v2_pre_registered_rule"] = res.model == S.V2_RULE_MODEL
res.to_csv(os.path.join(OUT, "rescore_v2.csv"), index=False)

summ_cols = ["model", "residual_rule", "mix_variant", "target", "window", "fx_estimator", "n", "rmse_pp", "rmse_naive_pp",
             "ratio_vs_naive", "ratio_vs_prior_year", "ratio_vs_ar1", "jackknife_ratio_min", "jackknife_ratio_max",
             "jackknife_below_1", "jackknife_n", "sign_accuracy_vs_naive", "bias_pp", "knowable_before_print"]
summ = res[summ_cols].copy()
summ["ratio_and_jackknife_below_1"] = (summ.ratio_vs_naive < 1) & (summ.jackknife_ratio_max < 1)
summ.to_csv(os.path.join(OUT, "rescore_v2_summary.csv"), index=False)

# 3. harness change in isolation: same rule, three scorings
j3 = pd.read_csv(os.path.join(ROOT, "data", "processed", "adrq3", "J", "card_v2_backtest.csv"))
iso = []
for m in ["v2_measured_last_q", "v2_measured_persistence", "v2_measured_trailing_4q", "v2_measured_blend", "v2_measured_ar1_residual", "ar1_expanding"]:
    for w in S.WINDOWS:
        r0 = j3[(j3.model == m) & (j3.window == w)].iloc[0]
        iso.append({"model": m, "window": w, "scoring": "J3 record (unrounded model vs integer ex-FX)", "fx_estimator": "none",
                    "ratio_vs_naive": r0.ratio_vs_naive, "jackknife_ratio_min": r0.jackknife_ratio_min,
                    "jackknife_ratio_max": r0.jackknife_ratio_max, "jackknife_below_1": r0.jackknife_quarters_ratio_below_1})
        for tgt, ests in (("t1_exfx_integer_fair", ["none"]), ("t2_reported_usd_yoy", ["eur", "baskets", "midpoint"])):
            for est in ests:
                r1 = res[(res.model == m) & (res.window == w) & (res.target == tgt) & (res.fx_estimator == est)].iloc[0]
                iso.append({"model": m, "window": w, "scoring": tgt, "fx_estimator": est, "ratio_vs_naive": r1.ratio_vs_naive,
                            "jackknife_ratio_min": r1.jackknife_ratio_min, "jackknife_ratio_max": r1.jackknife_ratio_max,
                            "jackknife_below_1": r1.jackknife_below_1})
iso = pd.DataFrame(iso)
iso["strict_criterion_met"] = (iso.ratio_vs_naive < 1) & (iso.jackknife_ratio_max < 1)
iso.to_csv(os.path.join(OUT, "harness_change_isolation.csv"), index=False)

# 4. the pre-registered v3 result
verdict = S.preregistered_pass(res, S.V3_RULE_MODEL)
vt = S.pass_table(verdict)
vt["criterion"] = verdict["criterion"]
vt.to_csv(os.path.join(OUT, "v3_preregistered_result.csv"), index=False)
verdict_v2rule = S.preregistered_pass(res, S.V2_RULE_MODEL)   # comparison only, not the pre-registered rule

# 5. walk-forward paths in scored units
wf = S.paths(models)
wf.to_csv(os.path.join(OUT, "walk_forward_paths.csv"), index=False)

# 6. error attribution for the v3 rule (measured mix, last_q residual)
c = S.v2_components()
d = S.load_inputs()
attr = []
model_exfx = paths[S.V3_RULE_MODEL]
for q in c.index:
    base = {"quarter": q,
            "err_from_residual_rule_pp": float(c.loc[q, "residual_last_q_pp"] - c.loc[q, "actual_residual_pp"]),
            "err_from_new_business_and_interaction_pp": float((c.loc[q, "new_business_prior_year_pp"] + c.loc[q, "interaction_prior_year_pp"])
                                                              - (c.loc[q, "new_business_actual_pp"] + c.loc[q, "interaction_actual_pp"])),
            "model_exfx_unrounded_pp": float(model_exfx[q]), "actual_exfx_disclosed_pp": float(c.loc[q, "actual_exfx_pp"])}
    # target 1
    tf1 = S.target_frame("t1_exfx_integer_fair")
    pred1 = float(S.round_half_away(model_exfx[q]))
    e1 = pred1 - float(tf1.loc[q, "actual"])
    r = dict(base, target="t1_exfx_integer_fair", fx_estimator="none", model_scored_pp=pred1, actual_pp=float(tf1.loc[q, "actual"]),
             err_total_pp=e1, err_naive_pp=float(tf1.loc[q, "naive"] - tf1.loc[q, "actual"]),
             err_from_rounding_pp=pred1 - float(model_exfx[q]), err_from_fx_estimator_pp=np.nan, err_from_disclosed_identity_gap_pp=np.nan)
    r["check_sum_pp"] = r["err_from_residual_rule_pp"] + r["err_from_new_business_and_interaction_pp"] + r["err_from_rounding_pp"] - e1
    attr.append(r)
    # target 2, each estimator
    for est in S.FX_ESTIMATORS:
        tf2 = S.target_frame("t2_reported_usd_yoy", est)
        fx = float(tf2.loc[q, "fx_est_pp"])
        pred2 = float(model_exfx[q] + fx)
        e2 = pred2 - float(tf2.loc[q, "actual"])
        fx_err = fx - float(d["fx_disclosed"][q])
        ident = -float(d["identity_gap"][q])     # reported - (exfx_int + fx_disclosed), sign so that terms add to the total
        r = dict(base, target="t2_reported_usd_yoy", fx_estimator=est, model_scored_pp=pred2, actual_pp=float(tf2.loc[q, "actual"]),
                 err_total_pp=e2, err_naive_pp=float(tf2.loc[q, "naive"] - tf2.loc[q, "actual"]),
                 err_from_rounding_pp=0.0, err_from_fx_estimator_pp=fx_err, err_from_disclosed_identity_gap_pp=ident)
        r["check_sum_pp"] = (r["err_from_residual_rule_pp"] + r["err_from_new_business_and_interaction_pp"] + fx_err + ident) - e2
        attr.append(r)
attr = pd.DataFrame(attr)
assert attr.check_sum_pp.abs().max() < 1e-9, "attribution does not add up"
attr.to_csv(os.path.join(OUT, "error_attribution_v3.csv"), index=False)

# 7. print
print("\nrescored, measured-mix rules and benchmarks (ratio vs naive; jackknife min-max; below 1):")
show = summ[summ.model.isin(S.BENCHMARKS + [f"v2_measured_{r}" for r in S.RULES])]
piv = show.assign(cell=show.apply(lambda r: f"{r.ratio_vs_naive:.3f} [{r.jackknife_ratio_min:.2f}-{r.jackknife_ratio_max:.2f}] {int(r.jackknife_below_1)}/{int(r.jackknife_n)}", axis=1))
piv = piv.pivot_table(index="model", columns=["target", "fx_estimator", "window"], values="cell", aggfunc="first")
print(piv.to_string())
print("\nharness change in isolation:\n", iso.round(3).to_string())
print("\nerror attribution, v3 rule, target 2 midpoint FX:\n",
      attr[(attr.target == "t2_reported_usd_yoy") & (attr.fx_estimator == "midpoint")][["quarter", "err_total_pp", "err_naive_pp", "err_from_residual_rule_pp",
                                                                                        "err_from_new_business_and_interaction_pp", "err_from_fx_estimator_pp", "err_from_disclosed_identity_gap_pp"]].round(2).to_string())
print("\nv2 rule (persistence) under the v3 criterion, for comparison:", verdict_v2rule["verdict"], f"({verdict_v2rule['n_checks_met']} of {verdict_v2rule['n_checks']})")
print("\nV3 PRE-REGISTERED RESULT:", verdict["model"], "->", verdict["verdict"], f"({verdict['n_checks_met']} of {verdict['n_checks']} checks met)")
for ck in verdict["checks"]:
    print(f"  t2 {ck['fx_estimator']:8s} {ck['window']}: RMSE {ck['rmse_pp']:.3f} vs naive {ck['rmse_naive_pp']:.3f}, ratio {ck['ratio_vs_naive']:.3f}, jackknife {ck['jackknife_ratio_min']:.3f} to {ck['jackknife_ratio_max']:.3f} ({ck['jackknife_below_1']} below 1) -> {'met' if ck['criterion_met'] else 'NOT met'}")
for ck in verdict["alongside"]:
    print(f"  alongside {ck['target']} {ck['fx_estimator']:8s} {ck['window']}: ratio {ck['ratio_vs_naive']:.3f}, jackknife {ck['jackknife_ratio_min']:.3f} to {ck['jackknife_ratio_max']:.3f}")
