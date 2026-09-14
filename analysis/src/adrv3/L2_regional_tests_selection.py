"""
WS-L step 2: note-08 tests of every candidate per region, and the walk-forward selection.

For each region, every candidate (own-history rules; each covering proxy in level and first
difference at lags 0 and 1; MAR and HLT RevPAR for NA as test-only) is asked for a strictly
out-of-sample prediction at every quarter 1Q23-2Q26 (L0.predict). The tests table scores each
candidate on the usable quarters of 1Q24-2Q26 against the region's own naive (last quarter),
prior year and expanding AR(1), with J2's correlation statistics for the proxies (Pearson r and p,
Spearman, 1,000-shuffle permutation p, Bonferroni within region). The selection table records, for
every scored quarter 1Q24-2Q26 and for 3Q26 and 4Q26, the candidate with the lowest out-of-sample
RMSE on usable quarters strictly before t among candidates with at least four such quarters
(default last_q).

Writes to data/processed/adrv3/L/: L2_proxy_tests.csv, L2_candidate_oos_paths.csv,
L2_regional_selection.csv, L2_selection_tables.csv.

py -3.13 analysis/src/adrv3/L2_regional_tests_selection.py    (offline, about a minute: permutation tests)
"""
import os

import numpy as np
import pandas as pd

import L0_common as L
from L0_common import S, REGIONS, QI

panel, wide = L.load_regional()
proxies, readings = L.load_proxies()

scored = S.quarters_between(L.FIRST_SCORED, L.LAST_SCORED)
tests, oos_long, sel_rows, sel_tables = [], [], [], []
OOS = {}

for region in REGIONS:
    rd = L.RegionData(region, panel, proxies)
    pool = L.candidates_for(region, pool_only=True)
    allc = L.candidates_for(region, pool_only=False)
    oos = L.oos_table(rd, allc)
    OOS[region] = oos
    # benchmark columns on the region's own series
    oos["naive"] = oos["last_q"]
    oos["prior_year"] = [rd.y.get(L.qprev(q, 4), np.nan) if rd.usable.get(L.qprev(q, 4), False) else np.nan for q in oos.index]
    oos["ar1_bench"] = oos["ar1"]
    for q in oos.index:
        for c in allc:
            oos_long.append({"region": region, "quarter": q, "candidate": c, "pred_pp": oos.at[q, c],
                             "actual_pp": oos.at[q, "actual"], "usable": bool(oos.at[q, "usable"]),
                             "in_selection_pool": c in pool})
    # --- tests on the scored window, usable quarters only ---
    win = [q for q in scored if q in oos.index and bool(oos.at[q, "usable"])]
    for c in allc:
        w = oos.loc[win]
        m = w[c].notna()
        if m.sum() == 0:
            continue
        ww = w[m]
        e = ww[c] - ww.actual
        r_n, r_p, r_a = L.rmse(ww.naive - ww.actual), L.rmse(ww.prior_year - ww.actual), L.rmse(ww.ar1_bench - ww.actual)
        d_act, d_pred = ww.actual - ww.naive, ww[c] - ww.naive
        nz = d_act != 0
        row = {"region": region, "candidate": c, "kind": "own_rule" if c in L.OWN_RULES else "proxy_ols",
               "in_selection_pool": c in pool, "wf_n": int(m.sum()), "wf_first_q": ww.index[0], "wf_last_q": ww.index[-1],
               "wf_rmse_model": L.rmse(e), "wf_rmse_naive": r_n, "wf_rmse_prior_year": r_p, "wf_rmse_ar1": r_a,
               "wf_ratio_vs_naive": L.rmse(e) / r_n if r_n else np.nan,
               "wf_ratio_vs_prior_year": L.rmse(e) / r_p if r_p else np.nan,
               "wf_ratio_vs_ar1": L.rmse(e) / r_a if r_a else np.nan,
               "wf_sign_accuracy": float((np.sign(d_pred[nz]) == np.sign(d_act[nz])).mean()) if nz.any() else np.nan,
               "wf_bias": float(e.mean())}
        # jackknife on the ratio vs naive
        ratios = []
        for drop in ww.index:
            keep = [q for q in ww.index if q != drop]
            if len(keep) >= 2:
                den = L.rmse(ww.loc[keep, "naive"] - ww.loc[keep, "actual"])
                if den and np.isfinite(den):
                    ratios.append(L.rmse(ww.loc[keep, c] - ww.loc[keep, "actual"]) / den)
        row["jackknife_ratio_min"] = min(ratios) if ratios else np.nan
        row["jackknife_ratio_max"] = max(ratios) if ratios else np.nan
        row["jackknife_below_1"] = int(sum(r < 1 for r in ratios))
        if c not in L.OWN_RULES:
            proxy, transform, lag = c.split("|")
            row.update({"proxy": proxy, "transform": transform, "lag": int(lag[3:]), "knowable_before_print": L.PROXY_KNOWABLE[proxy]})
            x = rd.proxy_x(proxy, transform, int(lag[3:]))
            y = rd.y[rd.usable[rd.usable].index]
            row.update(L.corr_stats(x.reindex(y.index), y))
        else:
            row.update({"proxy": "", "transform": "", "lag": np.nan,
                        "knowable_before_print": "regional ex-FX through t-1 (prior print)" + ("; size term from I1 in-quarter" if c == "last_q_ex_size" else "")})
        tests.append(row)
    # --- walk-forward selection ---
    for t in scored + L.NOWCAST_QUARTERS:
        s = L.select(oos, pool, t)
        tab = s.pop("table")
        ranked = sorted([(c, v[0], v[1]) for c, v in tab.items() if v[0] >= L.MIN_SELECT], key=lambda z: z[2])
        runner = ranked[1] if len(ranked) > 1 else (None, 0, np.nan)
        pred = oos.at[t, s["pick"]] if t in oos.index else np.nan
        sel_rows.append({"region": region, "quarter": t, "pick": s["pick"], "pick_kind": "own_rule" if s["pick"] in L.OWN_RULES else "proxy_ols",
                         "pick_rmse_prior_oos": s["pick_rmse_prior"], "n_oos_prior": s["n_oos_prior"], "n_eligible": s["n_eligible"],
                         "runner_up": runner[0], "runner_up_rmse_prior_oos": runner[2],
                         "last_q_rmse_prior_oos": tab["last_q"][1], "last_q_n_prior_oos": tab["last_q"][0],
                         "selection_basis": s["selection_basis"],
                         "pred_pp": pred, "pred_last_q_pp": oos.at[t, "last_q"] if t in oos.index else np.nan,
                         "actual_pp": oos.at[t, "actual"] if t in oos.index else np.nan,
                         "actual_usable": bool(oos.at[t, "usable"]) if t in oos.index else False})
        for c, (n, r) in tab.items():
            sel_tables.append({"region": region, "quarter": t, "candidate": c, "n_oos_prior": n, "rmse_prior_oos": r,
                               "eligible": n >= L.MIN_SELECT, "picked": c == s["pick"]})

tests = pd.DataFrame(tests)
for reg, gg in tests[tests.kind == "proxy_ols"].groupby("region"):
    tests.loc[gg.index, "n_tests_on_region"] = len(gg)
    tests.loc[gg.index, "p_bonferroni"] = np.minimum(1.0, gg.p * len(gg))
tests["flagged_r"] = (tests.pearson_r.abs() > 0.5) & (tests.perm_p < 0.05)
tests["beats_naive"] = tests.wf_ratio_vs_naive < 1
tests["beats_naive_and_ar1"] = (tests.wf_ratio_vs_naive < 1) & (tests.wf_ratio_vs_ar1 < 1)
tests["survivor"] = tests.flagged_r.fillna(False) & tests.beats_naive_and_ar1 & (tests.wf_n >= 6)
tests = tests.sort_values(["region", "wf_ratio_vs_naive"])
tests.to_csv(os.path.join(L.OUT, "L2_proxy_tests.csv"), index=False)
pd.DataFrame(oos_long).to_csv(os.path.join(L.OUT, "L2_candidate_oos_paths.csv"), index=False)
sel = pd.DataFrame(sel_rows)
sel.to_csv(os.path.join(L.OUT, "L2_regional_selection.csv"), index=False)
pd.DataFrame(sel_tables).to_csv(os.path.join(L.OUT, "L2_selection_tables.csv"), index=False)

pd.set_option("display.width", 250)
cols = ["region", "candidate", "wf_n", "wf_rmse_model", "wf_rmse_naive", "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "wf_sign_accuracy",
        "jackknife_ratio_min", "jackknife_ratio_max", "pearson_r", "perm_p", "p_bonferroni", "survivor"]
for region in REGIONS:
    print(f"\n=== {region}: tests on usable quarters of 1Q24-2Q26 ===")
    print(tests[tests.region == region][cols].round(3).to_string(index=False))
print("\n=== walk-forward picks ===")
print(sel[["region", "quarter", "pick", "n_oos_prior", "n_eligible", "pick_rmse_prior_oos", "last_q_rmse_prior_oos", "runner_up",
           "pred_pp", "pred_last_q_pp", "actual_pp", "actual_usable"]].round(3).to_string(index=False))
