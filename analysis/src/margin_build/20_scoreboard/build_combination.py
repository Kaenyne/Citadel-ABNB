"""WS20 step 5: leave-future-out test of candidate weighting schemes for WS23.

Every scheme is fitted ONLY on quarters that printed before the quarter being forecast
(expanding window, minimum 6 prior quarters), so the comparison is leave-future-out and
not a hindsight blend. Objects are the ten that survive both windows at h=0 on
adj_ebitda_margin_pct (one spec each, chosen by W1 MAE) from build_correlations.py.

Outputs
  20_combination_backtest.csv     per-quarter combined point and error for each scheme
  20_combination_scores.csv       MAE / RMSE / bias per scheme, W1 and W2, equal and recency
  20_combination_live.csv         the same schemes applied to the LIVE 3Q26-4Q27 points
"""
from pathlib import Path
import glob
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data" / "processed" / "margin_build" / "20_scoreboard"
REG = ROOT / "data" / "processed" / "margin_build" / "registry"
TODAY = "2026-09-11"
MIN_PRIOR = 4
HL = 4.0
W2_START = "2024Q1"
M5 = "street-bias|dispersion_conditioned|rw_hl4_med"
M3 = "guide-policy-margin|actual_given_guide|rw_hl4_pin"


def rw_weights(n, hl=HL):
    """Exponential recency weights, half-life hl, newest last."""
    age = np.arange(n - 1, -1, -1)
    return 0.5 ** (age / hl)


def schemes(prior, labels, div_order):
    """prior: DataFrame quarter x label of absolute errors, oldest first. Returns dict
    scheme -> weight Series over labels."""
    out = {}
    mae = prior.mean()
    w_rw = rw_weights(len(prior))
    mae_rw = (prior.mul(w_rw, axis=0).sum() / w_rw.sum())
    out["ew_all"] = pd.Series(1.0, index=labels)
    top3 = mae.nsmallest(3).index
    out["ew_top3_prior_mae"] = pd.Series([1.0 if l in top3 else 0.0 for l in labels], index=labels)
    out["invmae_all"] = 1.0 / mae.reindex(labels).replace(0, np.nan)
    out["invmae_recency"] = 1.0 / mae_rw.reindex(labels).replace(0, np.nan)
    best = mae.idxmin()
    out["best_single_prior_mae"] = pd.Series([1.0 if l == best else 0.0 for l in labels], index=labels)
    out["m5_dispersion_only"] = pd.Series([1.0 if l == M5 else 0.0 for l in labels], index=labels)
    out["m5_m3_5050"] = pd.Series([1.0 if l in (M5, M3) else 0.0 for l in labels], index=labels)
    # 60/40 consensus-anchored / independent, the scheme recommended to WS23
    ind = [l for l in labels if not l.startswith("street-bias") and not l.startswith("baselines-margin")]
    ind_mae = mae.reindex(ind)
    ind_best = ind_mae.nsmallest(2).index
    w = pd.Series(0.0, index=labels)
    w[M5] = 0.6
    for l in ind_best:
        w[l] = 0.2
    out["m5_60_plus_two_independent_40"] = w
    # three least-correlated objects, equal weights
    trio = [l for l in div_order[:3] if l in labels]
    out["ew_three_least_correlated"] = pd.Series([1.0 if l in trio else 0.0 for l in labels], index=labels)
    # family weights: the correlation matrix says there are only ~3 independent views -
    # A the driver / cost-line family (M1, M4, M6, M2-sarima; pairwise r 0.93-1.00),
    # B the Street-anchored family (M5 objects and the Street baseline; r 0.85-0.92),
    # C the guidance-policy view (M3; r 0.02-0.20 against everything).
    famA = [l for l in labels if l.startswith(("driver-lines", "alt-augmented", "cycle-flex"))
            or l.startswith("margin-ts|sarima")]
    famB = [l for l in labels if l.startswith("street-bias")]
    famC = [l for l in labels if l.startswith("guide-policy-margin")]
    for name, (wa, wb, wc) in (("family_equal_thirds", (1 / 3, 1 / 3, 1 / 3)),
                               ("family_B50_A30_C20", (0.30, 0.50, 0.20))):
        w = pd.Series(0.0, index=labels)
        for fam, wt in ((famA, wa), (famB, wb), (famC, wc)):
            if fam:
                for l in fam:
                    w[l] += wt / len(fam)
        if w.sum() > 0:
            out[name] = w
    # the scheme WS20 recommends to WS23 at h=0: 60 pct the Street-anchored view (M5
    # dispersion_conditioned), 20 pct the guidance-policy view (M3, the only object whose
    # errors are uncorrelated with the rest), 20 pct the driver / cost-line family averaged
    # (M1, M6, M4, M2-sarima, which are near-identical to one another).
    w = pd.Series(0.0, index=labels)
    if M5 in labels:
        w[M5] = 0.60
    if M3 in labels:
        w[M3] = 0.20
    if famA:
        for l in famA:
            w[l] += 0.20 / len(famA)
    if w.sum() > 0:
        out["recommended_ws23_60_20_20"] = w
    out["median_all"] = None  # handled separately
    return out


def main():
    q = pd.read_csv(OUT / "20_errors_by_quarter_surviving.csv")
    div = pd.read_csv(OUT / "20_error_diversification.csv")
    div_order = list(div.label)

    pts = q.pivot_table(index="quarter", columns="label", values="point")
    errs = q.pivot_table(index="quarter", columns="label", values="abs_err")
    act = q.groupby("quarter")["actual"].first()
    qs = sorted(pts.index)
    labels = list(pts.columns)

    rows = []
    for i, tq in enumerate(qs):
        if i < MIN_PRIOR:
            continue
        prior = errs.loc[qs[:i]]
        prior = prior.dropna(axis=1, how="any")
        lab = [l for l in labels if l in prior.columns and not np.isnan(pts.loc[tq, l])]
        prior = prior[lab]
        sc = schemes(prior, lab, div_order)
        p = pts.loc[tq, lab]
        for name, w in sc.items():
            if name == "median_all":
                point = float(p.median())
            else:
                w = w.reindex(lab).fillna(0.0)
                if w.sum() == 0:
                    continue
                w = w / w.sum()
                point = float((p * w).sum())
            rows.append(dict(quarter=tq, scheme=name, point=point, actual=float(act[tq]),
                             err=point - float(act[tq]), abs_err=abs(point - float(act[tq])),
                             n_objects=len(lab)))
        # benchmarks
        rows.append(dict(quarter=tq, scheme="_street_baseline",
                         point=float(pts.loc[tq, "baselines-margin|street|street|adj_ebitda_margin_pct|h0|PIT"])
                         if "baselines-margin|street|street|adj_ebitda_margin_pct|h0|PIT" in lab else np.nan,
                         actual=float(act[tq]), err=np.nan, abs_err=np.nan, n_objects=len(lab)))
    bt = pd.DataFrame(rows)
    bench = bt[bt.scheme == "_street_baseline"].copy()
    bench["err"] = bench["point"] - bench["actual"]
    bench["abs_err"] = bench["err"].abs()
    bt = pd.concat([bt[bt.scheme != "_street_baseline"], bench], ignore_index=True)
    bt.to_csv(OUT / "20_combination_backtest.csv", index=False)

    scores = []
    for name, g in bt.groupby("scheme"):
        g = g.sort_values("quarter")
        halves = sorted(set(g.quarter))
        mid = halves[len(halves) // 2]
        for win, sub in (("full_2024Q1_2026Q2", g),
                         ("first_half", g[g.quarter < mid]),
                         ("second_half", g[g.quarter >= mid])):
            if sub.empty:
                continue
            w = rw_weights(len(sub))
            scores.append(dict(scheme=name, eval_window=win, n=len(sub),
                               first_quarter=sub.quarter.iloc[0], last_quarter=sub.quarter.iloc[-1],
                               mae=sub.abs_err.mean(),
                               rw_mae=float((sub.abs_err * w).sum() / w.sum()),
                               rmse=float(np.sqrt((sub.err ** 2).mean())),
                               bias=sub.err.mean()))
    sc = pd.DataFrame(scores).sort_values(["eval_window", "mae"])
    st = sc[sc.scheme == "_street_baseline"].set_index("eval_window")["mae"]
    sc["ratio_to_street"] = sc.apply(lambda r: r["mae"] / st.get(r["eval_window"], np.nan), axis=1)
    sc.to_csv(OUT / "20_combination_scores.csv", index=False)

    # ---- apply the schemes to LIVE -------------------------------------------
    live_rows = []
    for f in glob.glob(str(REG / "*.csv")):
        d = pd.read_csv(f)
        d = d[(d.window == "LIVE") & (d.vintage_date == TODAY)
              & (d.target == "adj_ebitda_margin_pct") & (d.prior_basis == "PIT")]
        if len(d):
            d["spec_id"] = d["spec_id"].fillna("(none)")
            d["label"] = d.method + "|" + d.object + "|" + d.spec_id
            live_rows.append(d[["label", "quarter", "point", "sd"]])
    lv = pd.concat(live_rows, ignore_index=True)
    lv = lv[lv.label.isin(labels)]
    prior_all = errs.dropna(axis=1, how="any")
    sc_live = schemes(prior_all, list(prior_all.columns), div_order)
    out = []
    for qq, g in lv.groupby("quarter"):
        p = g.set_index("label")["point"]
        lab = [l for l in prior_all.columns if l in p.index]
        if not lab:
            continue
        for name, w in sc_live.items():
            if name == "median_all":
                val = float(p[lab].median())
            else:
                w2 = w.reindex(lab).fillna(0.0)
                if w2.sum() == 0:
                    continue
                w2 = w2 / w2.sum()
                val = float((p[lab] * w2).sum())
            out.append(dict(quarter=qq, scheme=name, n_objects=len(lab),
                            adj_ebitda_margin_pct=val))
    od = pd.DataFrame(out)
    od.to_csv(OUT / "20_combination_live_long.csv", index=False)
    lc = od[od.n_objects >= 5].pivot_table(index="scheme", columns="quarter",
                                           values="adj_ebitda_margin_pct")
    lc.to_csv(OUT / "20_combination_live.csv")

    wts = pd.DataFrame({k: (v / v.sum() if v is not None else np.nan)
                        for k, v in sc_live.items() if v is not None})
    wts.to_csv(OUT / "20_combination_weights_live.csv")

    print(sc.to_string(index=False))
    print()
    print(lc.to_string())


if __name__ == "__main__":
    main()
