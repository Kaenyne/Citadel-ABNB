"""WS20 step 4: error correlations across surviving objects, and shock vs calm quarters.

Uses the harness long file scoreboard_by_quarter.csv (PIT replay, h=0, target
adj_ebitda_margin_pct unless overridden). One column per (method|object|spec) that
(a) survives both windows equal-weighted and (b) is not an oracle spec.

Shock quarters: the prompt names 2H22 and 1Q25-2Q25. 2H22 is OUTSIDE both backtest
windows (W1 targets start 2023Q1), so the shock set that can actually be measured is
2025Q1-2025Q2; 2023Q1-2023Q2 (the ADR windfall / first post-reset quarters) is reported
as a second, separate stress set.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HARN = ROOT / "data" / "processed" / "margin_build" / "10_harness_margin"
OUT = ROOT / "data" / "processed" / "margin_build" / "20_scoreboard"
ORACLE = "revknown|nightsknown|ebitda_known"
SHOCK = ["2025Q1", "2025Q2"]
STRESS2 = ["2023Q1", "2023Q2"]
TARGET = "adj_ebitda_margin_pct"


def main():
    master = pd.read_csv(OUT / "20_scoreboard_master.csv")
    m = master[(master.target == TARGET) & (master.horizon_q == 0)
               & (master.weighting == "equal") & (master.window == "W1")
               & (~master.spec_id.str.contains(ORACLE, case=False, na=False))].copy()
    m["surv"] = m["survives_both_windows"].astype(str).str.lower().isin(["true", "yes", "1"])
    keep = m[m.surv & (m.n >= 8)]
    # one spec per object: the best W1 MAE among survivors
    keep = keep.sort_values("mae").groupby(["method", "object"], as_index=False).first()
    keys = set(zip(keep.method, keep.object, keep.spec_id))

    cols = ["method", "object", "target", "window", "horizon_q", "prior_basis", "spec_id",
            "quarter", "vintage_date", "point", "actual", "err", "abs_err",
            "seasonal_naive_point", "seasonal_naive_abs_err"]
    chunks = []
    for ch in pd.read_csv(HARN / "scoreboard_by_quarter.csv", usecols=cols, chunksize=400_000):
        ch = ch[(ch.target == TARGET) & (ch.horizon_q == 0) & (ch.prior_basis == "PIT")
                & (ch.window == "W1")]
        ch["spec_id"] = ch["spec_id"].fillna("(none)")
        ch = ch[[(a, b, c) in keys for a, b, c in zip(ch.method, ch.object, ch.spec_id)]]
        if len(ch):
            chunks.append(ch)
    q = pd.concat(chunks, ignore_index=True)
    q["label"] = q.method + "|" + q.object + "|" + q.spec_id
    q.to_csv(OUT / "20_errors_by_quarter_surviving.csv", index=False)

    piv = q.pivot_table(index="quarter", columns="label", values="err")
    piv = piv.dropna(axis=1, thresh=8)
    corr = piv.corr()
    corr.to_csv(OUT / "20_error_correlations.csv")

    # mean pairwise correlation per object, as a diversification score
    c = corr.copy()
    np.fill_diagonal(c.values, np.nan)
    div = pd.DataFrame({"label": c.columns, "mean_pairwise_corr": c.mean(),
                        "min_pairwise_corr": c.min()}).reset_index(drop=True)
    div = div.sort_values("mean_pairwise_corr")
    div.to_csv(OUT / "20_error_diversification.csv", index=False)

    # shock vs calm
    rows = []
    for label, g in q.groupby("label"):
        g = g.set_index("quarter")
        sh = g.reindex(SHOCK)["abs_err"].dropna()
        s2 = g.reindex(STRESS2)["abs_err"].dropna()
        calm = g.drop(index=[x for x in SHOCK + STRESS2 if x in g.index])["abs_err"]
        rows.append(dict(label=label, n_all=len(g), mae_all=g["abs_err"].mean(),
                         n_shock_2025h1=len(sh), mae_shock_2025h1=sh.mean(),
                         n_stress_2023h1=len(s2), mae_stress_2023h1=s2.mean(),
                         n_calm=len(calm), mae_calm=calm.mean(),
                         shock_minus_calm=sh.mean() - calm.mean(),
                         bias_shock=g.reindex(SHOCK)["err"].mean(),
                         bias_calm=calm.index.size and g.drop(
                             index=[x for x in SHOCK + STRESS2 if x in g.index])["err"].mean()))
    sc = pd.DataFrame(rows).sort_values("mae_shock_2025h1")
    sc.to_csv(OUT / "20_shock_vs_calm.csv", index=False)

    # per-quarter MAE across all surviving objects, to show which quarters are hard
    hard = q.groupby("quarter").agg(n_objects=("label", "nunique"),
                                    mean_abs_err=("abs_err", "mean"),
                                    median_abs_err=("abs_err", "median"),
                                    mean_err=("err", "mean"),
                                    seasonal_naive_abs_err=("seasonal_naive_abs_err", "mean"))
    hard.to_csv(OUT / "20_hard_quarters.csv")

    print("objects", piv.shape[1], "quarters", piv.shape[0])
    print(div.head(8).to_string(index=False))
    print(sc[["label", "mae_all", "mae_shock_2025h1", "mae_calm", "shock_minus_calm"]].to_string(index=False))
    print(hard.to_string())


if __name__ == "__main__":
    main()
