"""
WS-L step 3: aggregate the regional forecasts into blended ex-FX and score on the S harness.

Variants (all forecast within-region ex-FX, aggregate on year-ago dollar weights, add H's measured
geo term; primary is L_wf, stated before any result):
  L_wf            walk-forward pick per region per quarter (L2, absolute OOS RMSE, min four quarters)
  L_wf_gap_lastq  L_wf minus last quarter's reconstruction gap (gap = reconstructed - disclosed)
  L_fixed_hicp    EMEA on euro-area HICP accommodation, level lag 0 OLS (J2's survivor); others last_q
  L_reg_lastq     every region on its own last quarter (the regional analogue of naive)
  L_reg_persist   every region on the mean of its last two quarters
  L_wf_rel        sensitivity: pick by RMSE ratio to last_q on the SAME prior quarters (min four)
  L_wf_own        sensitivity: walk-forward pick restricted to own-history rules (no proxies)
  v2_measured_last_q  the pre-registered v3 rule, rebuilt by S (the comparison the L criterion is against)

L criterion (BRIEF): the regional aggregate beats last_q on the S harness on both windows. Applied
here as: on target 2, under both the eur and baskets FX estimators, on both windows, the variant's
ratio vs naive is below last_q's ratio (four checks). Jackknife max and the strict v3 criterion
are reported alongside.

Writes to data/processed/adrv3/L/: L3_scores.csv, L3_pass.csv, L3_walk_forward_paths.csv,
L3_regional_paths.csv, L3_regional_scores.csv, L3_error_attribution.csv.

py -3.13 analysis/src/adrv3/L3_aggregate_score.py    (offline, seconds)
"""
import os

import numpy as np
import pandas as pd

import L0_common as L
from L0_common import S, REGIONS, QI

panel, wide = L.load_regional()
H = S.load_inputs()["H"]
sel = pd.read_csv(os.path.join(L.OUT, "L2_regional_selection.csv"))
oosl = pd.read_csv(os.path.join(L.OUT, "L2_candidate_oos_paths.csv"))
scored = S.quarters_between(L.FIRST_SCORED, L.LAST_SCORED)

# OOS tables per region (quarter x candidate), usable flags, actuals
OOS = {}
for r in REGIONS:
    d = oosl[oosl.region == r]
    tab = d.pivot(index="quarter", columns="candidate", values="pred_pp")
    tab = tab.loc[sorted(tab.index, key=lambda q: QI[q])]
    tab["actual"] = d.groupby("quarter").actual_pp.first().reindex(tab.index)
    tab["usable"] = d.groupby("quarter").usable.first().reindex(tab.index).astype(bool)
    OOS[r] = tab
POOL = {r: L.candidates_for(r, pool_only=True) for r in REGIONS}


def select_rel(oos, cands, t, min_select=L.MIN_SELECT):
    """Sensitivity selection: lowest RMSE ratio to last_q over the candidate's own prior usable quarters."""
    prior = [q for q in oos.index if QI[q] < QI[t] and bool(oos.at[q, "usable"])]
    best, best_v = "last_q", 1.0
    for c in cands:
        e = (oos.loc[prior, c] - oos.loc[prior, "actual"]).dropna()
        if len(e) < min_select:
            continue
        en = (oos.loc[e.index, "last_q"] - oos.loc[e.index, "actual"])
        den = L.rmse(en)
        v = L.rmse(e) / den if den else np.inf
        if v < best_v - 1e-12:
            best, best_v = c, v
    return best


# ---- regional forecast paths per variant ---------------------------------------
reg_paths = []   # long: variant, region, quarter, candidate, pred
def add_path(variant, region, q, cand, pred):
    reg_paths.append({"variant": variant, "region": region, "quarter": q, "candidate": cand, "pred_pp": pred,
                      "actual_pp": OOS[region].at[q, "actual"], "actual_usable": bool(OOS[region].at[q, "usable"])})

for r in REGIONS:
    oos = OOS[r]
    for q in scored:
        s = sel[(sel.region == r) & (sel.quarter == q)].iloc[0]
        add_path("L_wf", r, q, s.pick, float(s.pred_pp))
        add_path("L_wf_gap_lastq", r, q, s.pick, float(s.pred_pp))
        fixed = "hicp_ea_accommodation|level|lag0" if r == "emea" else "last_q"
        add_path("L_fixed_hicp", r, q, fixed, float(oos.at[q, fixed]))
        add_path("L_reg_lastq", r, q, "last_q", float(oos.at[q, "last_q"]))
        pers = float(oos.at[q, "persistence"]) if pd.notna(oos.at[q, "persistence"]) else float(oos.at[q, "last_q"])
        add_path("L_reg_persist", r, q, "persistence" if pd.notna(oos.at[q, "persistence"]) else "last_q (persistence unavailable)", pers)
        c_rel = select_rel(oos, POOL[r], q)
        add_path("L_wf_rel", r, q, c_rel, float(oos.at[q, c_rel]))
        own = L.select(oos, [c for c in POOL[r] if c in L.OWN_RULES], q)["pick"]
        v = oos.at[q, own]
        add_path("L_wf_own", r, q, own if pd.notna(v) else "last_q", float(v) if pd.notna(v) else float(oos.at[q, "last_q"]))
reg_paths = pd.DataFrame(reg_paths)
reg_paths.to_csv(os.path.join(L.OUT, "L3_regional_paths.csv"), index=False)
VARIANTS = ["L_wf", "L_wf_gap_lastq", "L_fixed_hicp", "L_reg_lastq", "L_reg_persist", "L_wf_rel", "L_wf_own"]

# ---- aggregate to blended ex-FX --------------------------------------------------
gap = H["geo_recon_gap_pp"].astype(float)
geo = H["geo_mix_pp"].astype(float)
agg_rows, exfx_paths = [], {}
for v in VARIANTS:
    path = pd.Series(index=scored, dtype=float)
    for q in scored:
        g = {r: float(reg_paths[(reg_paths.variant == v) & (reg_paths.region == r) & (reg_paths.quarter == q)].pred_pp.iloc[0]) for r in REGIONS}
        s0, s1, a0 = L.weights_for(wide, q)
        within = L.aggregate_within(g, s0, a0)
        gap_term = float(gap[L.qprev(q)]) if v == "L_wf_gap_lastq" else 0.0
        model = within + float(geo[q]) - gap_term
        path[q] = model
        agg_rows.append({"variant": v, "quarter": q, "within_forecast_pp": within, "geo_measured_pp": float(geo[q]), "gap_term_pp": gap_term,
                         "model_exfx_pp": model, "within_actual_pp": float(H.at[q, "within_region_exfx_pp"]),
                         "gap_actual_pp": float(gap[q]), "disclosed_exfx_pp": float(H.at[q, "adr_exfx_yoy_pp"]),
                         **{f"g_{r}": g[r] for r in REGIONS}, **{f"w_{r}": L.dollar_weights(wide, q)[r] for r in REGIONS}})
    exfx_paths[v] = path
agg = pd.DataFrame(agg_rows)
v2 = S.v2_model_paths()
exfx_paths["v2_measured_last_q"] = v2["v2_measured_last_q"]
exfx_paths["v2_measured_persistence"] = v2["v2_measured_persistence"]

# ---- score on the S harness ------------------------------------------------------
KNOW = {v: L.KNOWABLE_L for v in VARIANTS}
KNOW["L_wf_gap_lastq"] += "; gap uses the prior print"
parts = [S.score_benchmarks()]
for name, path in exfx_paths.items():
    parts.append(S.score(path, name, KNOW.get(name, S.KNOWABLE_V2)))
scores = pd.concat(parts, ignore_index=True)
scores.to_csv(os.path.join(L.OUT, "L3_scores.csv"), index=False)

ref = scores[scores.model == "v2_measured_last_q"]
def ref_row(target, est, w):
    return ref[(ref.target == target) & (ref.fx_estimator == est) & (ref.window == w)].iloc[0]

pass_rows = []
for v in VARIANTS:
    res = S.preregistered_pass(scores, v)
    checks = []
    for c in res["checks"]:
        rr = ref_row(c["target"], c["fx_estimator"], c["window"])
        c = dict(c, last_q_ratio_vs_naive=float(rr.ratio_vs_naive), last_q_jackknife_max=float(rr.jackknife_ratio_max),
                 beats_last_q_ratio=bool(c["ratio_vs_naive"] < rr.ratio_vs_naive),
                 beats_last_q_jackknife_max=bool(c["jackknife_ratio_max"] < rr.jackknife_ratio_max))
        checks.append(c)
    along = []
    for c in res["alongside"]:
        rr = ref_row(c["target"], c["fx_estimator"], c["window"])
        along.append(dict(c, last_q_ratio_vs_naive=float(rr.ratio_vs_naive), last_q_jackknife_max=float(rr.jackknife_ratio_max),
                          beats_last_q_ratio=bool(c["ratio_vs_naive"] < rr.ratio_vs_naive),
                          beats_last_q_jackknife_max=bool(c["jackknife_ratio_max"] < rr.jackknife_ratio_max)))
    l_pass = all(c["beats_last_q_ratio"] for c in checks)
    for c in checks + along:
        pass_rows.append(dict(c, L_criterion="target 2, eur and baskets, both windows: ratio vs naive below the last_q rule's",
                              L_verdict="PASS" if l_pass else "FAIL", L_checks_met=int(sum(x["beats_last_q_ratio"] for x in checks)),
                              v3_strict_verdict=res["verdict"], v3_strict_checks_met=res["n_checks_met"]))
passdf = pd.DataFrame(pass_rows)
passdf.to_csv(os.path.join(L.OUT, "L3_pass.csv"), index=False)

# ---- walk-forward paths in scored units -------------------------------------------
wf = S.paths(exfx_paths)
wf.to_csv(os.path.join(L.OUT, "L3_walk_forward_paths.csv"), index=False)

# ---- per-region scores vs the region's own naive (usable quarters of the window) -------
rs = []
for v in VARIANTS:
    for r in REGIONS:
        d = reg_paths[(reg_paths.variant == v) & (reg_paths.region == r) & reg_paths.actual_usable].set_index("quarter")
        naive = OOS[r].loc[d.index, "last_q"]
        e, en = d.pred_pp - d.actual_pp, naive - d.actual_pp
        ratios = []
        for drop in d.index:
            keep = [q for q in d.index if q != drop]
            den = L.rmse(en[keep])
            if den:
                ratios.append(L.rmse(e[keep]) / den)
        rs.append({"variant": v, "region": r, "n": len(d), "first_q": d.index[0], "last_q": d.index[-1],
                   "rmse_pp": L.rmse(e), "rmse_regional_naive_pp": L.rmse(en), "ratio_vs_regional_naive": L.rmse(e) / L.rmse(en) if L.rmse(en) else np.nan,
                   "bias_pp": float(e.mean()), "jackknife_min": min(ratios) if ratios else np.nan, "jackknife_max": max(ratios) if ratios else np.nan,
                   "picks": ";".join(f"{q}:{c}" for q, c in d.candidate.items())})
rscores = pd.DataFrame(rs)
rscores.to_csv(os.path.join(L.OUT, "L3_regional_scores.csv"), index=False)

# ---- error attribution: L_wf vs last_q, per quarter, by region --------------------------
att = []
for v in ["L_wf", "L_fixed_hicp", "L_reg_lastq", "L_wf_own"]:
    a = agg[agg.variant == v].set_index("quarter")
    for q in scored:
        row = {"variant": v, "quarter": q, "model_exfx_error_pp": a.at[q, "model_exfx_pp"] - a.at[q, "disclosed_exfx_pp"],
               "last_q_rule_error_pp": float(v2.at[q, "v2_measured_last_q"] - a.at[q, "disclosed_exfx_pp"]),
               "naive_error_pp": float(S.load_inputs()["exfx"][L.qprev(q)] - a.at[q, "disclosed_exfx_pp"]),
               "within_error_pp": a.at[q, "within_forecast_pp"] - a.at[q, "within_actual_pp"],
               "gap_pp": a.at[q, "gap_actual_pp"], "gap_term_used_pp": a.at[q, "gap_term_pp"]}
        for r in REGIONS:
            act = OOS[r].at[q, "actual"]
            row[f"contrib_{r}_pp"] = a.at[q, f"w_{r}"] * (a.at[q, f"g_{r}"] - act) * (1.0)  # linearised: weight x regional error
            row[f"actual_usable_{r}"] = bool(OOS[r].at[q, "usable"])
        att.append(row)
att = pd.DataFrame(att)
att.to_csv(os.path.join(L.OUT, "L3_error_attribution.csv"), index=False)

# ---- paired jackknife: variant vs last_q on the SAME drop-one subsample ---------------------
pj = []
for target in S.TARGETS:
    for est in (["none"] if target == "t1_exfx_integer_fair" else list(S.FX_ESTIMATORS)):
        blk = wf[(wf.target == target) & (wf.fx_estimator == est)].set_index("quarter")
        for wname, (w0, w1) in S.WINDOWS.items():
            idx = [q for q in blk.index if QI[w0] <= QI[q] <= QI[w1]]
            b = blk.loc[idx]
            for v in VARIANTS:
                full_v = L.rmse(b[v] - b.actual) / L.rmse(b.naive - b.actual)
                full_l = L.rmse(b["v2_measured_last_q"] - b.actual) / L.rmse(b.naive - b.actual)
                wins, worst_gap, best_gap, drop_worst, drop_best = 0, -np.inf, np.inf, None, None
                for drop in idx:
                    keep = [q for q in idx if q != drop]
                    k = b.loc[keep]
                    rv = L.rmse(k[v] - k.actual) / L.rmse(k.naive - k.actual)
                    rl = L.rmse(k["v2_measured_last_q"] - k.actual) / L.rmse(k.naive - k.actual)
                    wins += int(rv < rl)
                    if rv - rl > worst_gap:
                        worst_gap, drop_worst = rv - rl, drop
                    if rv - rl < best_gap:
                        best_gap, drop_best = rv - rl, drop
                pj.append({"model": v, "target": target, "fx_estimator": est, "window": wname, "n": len(idx),
                           "ratio_vs_naive": full_v, "last_q_ratio_vs_naive": full_l, "gap_full": full_v - full_l,
                           "paired_drops_beating_last_q": wins, "paired_gap_min": best_gap, "drop_giving_min_gap": drop_best,
                           "paired_gap_max": worst_gap, "drop_giving_max_gap": drop_worst})
pj = pd.DataFrame(pj)
pj.to_csv(os.path.join(L.OUT, "L3_paired_jackknife.csv"), index=False)

pd.set_option("display.width", 250)
print("\npaired jackknife vs last_q, target 2 (gap = variant ratio minus last_q ratio on the same quarters):")
print(pj[(pj.target == "t2_reported_usd_yoy") & pj.fx_estimator.isin(["eur", "baskets"])][
    ["model", "fx_estimator", "window", "ratio_vs_naive", "last_q_ratio_vs_naive", "paired_drops_beating_last_q", "n", "paired_gap_min", "drop_giving_min_gap", "paired_gap_max", "drop_giving_max_gap"]].round(3).to_string(index=False))
cols = ["model", "target", "window", "fx_estimator", "n", "rmse_pp", "rmse_naive_pp", "ratio_vs_naive", "jackknife_ratio_min", "jackknife_ratio_max", "jackknife_below_1", "sign_accuracy_vs_naive"]
show = scores[scores.model.isin(["v2_measured_last_q"] + VARIANTS) & ((scores.target == "t2_reported_usd_yoy") | (scores.target == "t1_exfx_integer_fair"))]
print(show[cols].round(3).sort_values(["target", "fx_estimator", "window", "model"]).to_string(index=False))
print("\nL verdicts (beats last_q's ratio vs naive on target 2, eur and baskets, both windows):")
print(passdf[passdf.in_pass_criterion][["model", "fx_estimator", "window", "ratio_vs_naive", "last_q_ratio_vs_naive", "jackknife_ratio_max", "last_q_jackknife_max", "beats_last_q_ratio", "L_verdict", "v3_strict_verdict"]].round(3).to_string(index=False))
print("\nper-region scores vs regional naive:")
print(rscores[["variant", "region", "n", "rmse_pp", "rmse_regional_naive_pp", "ratio_vs_regional_naive", "jackknife_min", "jackknife_max"]].round(3).to_string(index=False))
print("\nerror attribution, L_wf (pp):")
print(att[att.variant == "L_wf"][["quarter", "model_exfx_error_pp", "last_q_rule_error_pp", "naive_error_pp", "within_error_pp", "gap_pp"] + [f"contrib_{r}_pp" for r in REGIONS]].round(2).to_string(index=False))
print("\naggregate paths:")
print(agg[agg.variant == "L_wf"][["quarter", "within_forecast_pp", "within_actual_pp", "geo_measured_pp", "model_exfx_pp", "disclosed_exfx_pp", "g_na", "g_emea", "g_latam", "g_apac"]].round(2).to_string(index=False))
