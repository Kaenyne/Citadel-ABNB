"""ADR v3, workstream M, step 5: score the new-listing composition term on the S harness.

Baseline: the pre-registered v3 model, measured mix + prior-year fills + last-quarter residual
(S.v2_model_paths()["v2_measured_last_q"]).
With the term: the residual net of the term follows the last-quarter rule and the measured term enters
for quarter t:
    ex-FX(t) = mix_measured(t) + fills + [residual(t-1) - term(t-1)] + term(t)
which is S.exfx_from_residual(last_q on residual - term, "measured", extra_pp=term). Algebraically this
is the baseline plus the term's first difference, so the term only helps if its quarter-to-quarter change
tracks the residual's. A lagged-term variant (term(t-1) instead of term(t)) collapses to the baseline
and is not a separate model. Sensitivity: a walk-forward coefficient on the term change (expanding OLS
of the residual change on the term change strictly before t, minimum four pairs).

Criterion (BRIEF M): at least eight quarters of term history, and adding the term lowers the S-harness
RMSE on both windows; read on target 2 under both FX estimators (the v3 criterion), target 1 alongside.

Run: py -3.13 analysis/src/adrv3/M5_score_harness.py
Outputs: data/processed/adrv3/M/M5_scores.csv (every S.score row for baseline and each variant, with the
         baseline RMSE, delta and ratio vs the baseline), M5_paths.csv (per-quarter ex-FX paths),
         M5_criterion.csv (the pass table per variant)
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "M")
sys.path.insert(0, HERE)
import S1_scoring as S  # noqa: E402

KNOWABLE = ("no: prior-quarter residual known only at that print; the term's share is quarter-to-date "
            "(reviews) and its premium is the in-quarter dump")


def last_q_rule(series: pd.Series, quarters: list[str]) -> pd.Series:
    out = {}
    for t in quarters:
        prior = [q for q in series.index if S.QI[q] < S.QI[t]]
        out[t] = float(series[prior[-1]]) if prior else np.nan
    return pd.Series(out)


def walkforward_beta(res: pd.Series, term: pd.Series, quarters: list[str], min_pairs: int = 4) -> pd.Series:
    """expanding OLS of d(residual) on d(term) strictly before t; beta = 0 until min_pairs pairs exist."""
    dres, dterm = res.diff(), term.reindex(res.index).diff()
    out = {}
    for t in quarters:
        prior = [q for q in res.index if S.QI[q] < S.QI[t]]
        x, y = dterm[prior].values, dres[prior].values
        m = np.isfinite(x) & np.isfinite(y)
        if m.sum() >= min_pairs and np.std(x[m]) > 0:
            b = np.cov(x[m], y[m], ddof=1)[0, 1] / np.var(x[m], ddof=1)
        else:
            b = 0.0
        out[t] = b
    return pd.Series(out)


def main():
    d = S.load_inputs()
    res = d["residual"]  # H residual, 1Q23..2Q26
    comps = S.v2_components()
    quarters = list(comps.index)  # 1Q24..2Q26
    T = pd.read_csv(os.path.join(OUT, "M4_term_quarterly.csv"), keep_default_na=False, na_values=[""])
    G = T[T.region == "GLOBAL_NW"]
    base_path = S.v2_model_paths()["v2_measured_last_q"]
    base = S.score(base_path, "v2_measured_last_q", S.KNOWABLE_V2)
    base["variant"] = "baseline_last_q"
    base["term_history_quarters"] = 0
    frames, paths, crit = [base], {"baseline_last_q": base_path}, []
    key = ["target", "window", "fx_estimator"]
    for v in G.variant.unique():
        term = G[G.variant == v].set_index("quarter").term_pp.astype(float)
        term = term[[q for q in term.index if q in S.QI]]
        hist = [q for q in term.index if q in res.index]
        n_hist = len(hist)
        net = (res - term.reindex(res.index)).dropna()
        pred_net = last_q_rule(net, quarters)
        path = S.exfx_from_residual(pred_net, "measured", extra_pp=term)
        name = f"last_q_plus_term__{v}"
        sc = S.score(path, name, KNOWABLE)
        sc["variant"] = v
        sc["term_history_quarters"] = n_hist
        frames.append(sc)
        paths[name] = path
        # walk-forward coefficient sensitivity
        beta = walkforward_beta(res, term, quarters)
        dterm = term.diff().reindex(quarters)
        path_b = base_path + (beta * dterm).reindex(base_path.index).fillna(0.0)
        name_b = f"last_q_plus_beta_x_dterm__{v}"
        scb = S.score(path_b, name_b, KNOWABLE)
        scb["variant"] = v + " (walk-forward beta)"
        scb["term_history_quarters"] = n_hist
        frames.append(scb)
        paths[name_b] = path_b
        # criterion table
        pr = S.preregistered_pass(sc, model=name)
        both = sc.merge(base[key + ["rmse_pp", "ratio_vs_naive", "jackknife_ratio_max"]], on=key, suffixes=("", "_base"))
        t2 = both[(both.target == "t2_reported_usd_yoy") & (both.fx_estimator.isin(["eur", "baskets"]))]
        t1 = both[both.target == "t1_exfx_integer_fair"]
        crit.append(dict(variant=v, model=name, term_history_quarters=n_hist, history_ok=n_hist >= 8,
                         t2_rmse_lower_on_all_4=bool((t2.rmse_pp < t2.rmse_pp_base).all()),
                         t2_rmse_lower_count=int((t2.rmse_pp < t2.rmse_pp_base).sum()),
                         t2_eur_1Q24=float(t2[(t2.fx_estimator == "eur") & (t2.window == "1Q24-2Q26")].rmse_pp.iloc[0]),
                         t2_eur_1Q24_base=float(t2[(t2.fx_estimator == "eur") & (t2.window == "1Q24-2Q26")].rmse_pp_base.iloc[0]),
                         t2_eur_2Q24=float(t2[(t2.fx_estimator == "eur") & (t2.window == "2Q24-2Q26")].rmse_pp.iloc[0]),
                         t2_eur_2Q24_base=float(t2[(t2.fx_estimator == "eur") & (t2.window == "2Q24-2Q26")].rmse_pp_base.iloc[0]),
                         t2_baskets_1Q24=float(t2[(t2.fx_estimator == "baskets") & (t2.window == "1Q24-2Q26")].rmse_pp.iloc[0]),
                         t2_baskets_1Q24_base=float(t2[(t2.fx_estimator == "baskets") & (t2.window == "1Q24-2Q26")].rmse_pp_base.iloc[0]),
                         t2_baskets_2Q24=float(t2[(t2.fx_estimator == "baskets") & (t2.window == "2Q24-2Q26")].rmse_pp.iloc[0]),
                         t2_baskets_2Q24_base=float(t2[(t2.fx_estimator == "baskets") & (t2.window == "2Q24-2Q26")].rmse_pp_base.iloc[0]),
                         t1_rmse_lower_on_both=bool((t1.rmse_pp < t1.rmse_pp_base).all()),
                         t1_1Q24=float(t1[t1.window == "1Q24-2Q26"].rmse_pp.iloc[0]), t1_1Q24_base=float(t1[t1.window == "1Q24-2Q26"].rmse_pp_base.iloc[0]),
                         t1_2Q24=float(t1[t1.window == "2Q24-2Q26"].rmse_pp.iloc[0]), t1_2Q24_base=float(t1[t1.window == "2Q24-2Q26"].rmse_pp_base.iloc[0]),
                         v3_strict_pass_with_term=pr["pass"], v3_checks_met=pr["n_checks_met"],
                         M_criterion_met=bool(n_hist >= 8 and (t2.rmse_pp < t2.rmse_pp_base).all())))
    allsc = pd.concat(frames, ignore_index=True)
    b = base[key + ["rmse_pp", "ratio_vs_naive", "jackknife_ratio_max"]].rename(
        columns={"rmse_pp": "rmse_baseline_pp", "ratio_vs_naive": "ratio_vs_naive_baseline", "jackknife_ratio_max": "jackknife_max_baseline"})
    allsc = allsc.merge(b, on=key, how="left")
    allsc["delta_rmse_vs_baseline_pp"] = allsc.rmse_pp - allsc.rmse_baseline_pp
    allsc["ratio_vs_baseline"] = allsc.rmse_pp / allsc.rmse_baseline_pp
    allsc.to_csv(os.path.join(OUT, "M5_scores.csv"), index=False, encoding="utf-8")
    C = pd.DataFrame(crit)
    C.to_csv(os.path.join(OUT, "M5_criterion.csv"), index=False, encoding="utf-8")
    P = pd.DataFrame(paths)
    P.index.name = "quarter"
    P["actual_exfx_pp"] = comps.actual_exfx_pp
    P["actual_residual_pp"] = comps.actual_residual_pp
    P.to_csv(os.path.join(OUT, "M5_paths.csv"), encoding="utf-8")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_colwidth", 60)
    print("criterion table:")
    print(C[["variant", "term_history_quarters", "t2_rmse_lower_count", "t2_eur_1Q24", "t2_eur_1Q24_base", "t2_eur_2Q24", "t2_eur_2Q24_base",
             "t2_baskets_1Q24", "t2_baskets_1Q24_base", "t2_baskets_2Q24", "t2_baskets_2Q24_base", "t1_1Q24", "t1_1Q24_base", "t1_2Q24", "t1_2Q24_base",
             "v3_strict_pass_with_term", "M_criterion_met"]].round(3).to_string(index=False))
    print("\nratios vs naive (target 2, both estimators, both windows) and jackknife max:")
    sub = allsc[(allsc.target == "t2_reported_usd_yoy") & (allsc.fx_estimator.isin(["eur", "baskets"]))]
    print(sub.pivot_table(index="variant", columns=["fx_estimator", "window"], values=["ratio_vs_naive", "jackknife_ratio_max"]).round(3).to_string())
    print("\npaths (pp):")
    print(P.round(2).to_string())


if __name__ == "__main__":
    main()
