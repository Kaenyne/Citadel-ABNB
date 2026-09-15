"""WS20 step 6: parameter budget - free parameters per object against accuracy,
and the flag the prompt asks for: any object whose recency-weighted W2 win disappears in W1.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data" / "processed" / "margin_build" / "20_scoreboard"
ORACLE = "revknown|nightsknown|ebitda_known"
TARGETS = ["adj_ebitda_margin_pct", "adj_ebitda_musd"]


def truthy(s):
    return s.astype(str).str.lower().isin(["true", "yes", "1"])


def main():
    m = pd.read_csv(OUT / "20_scoreboard_master.csv")
    m = m[(m.target.isin(TARGETS)) & (m.horizon_q == 0)].copy()
    m["oracle"] = m.spec_id.str.contains(ORACLE, case=False, na=False)

    k = ["method", "object", "spec_id", "target"]
    piv = m.pivot_table(index=k, columns=["window", "weighting"],
                        values=["mae", "ratio_seasonal_naive", "ratio_street", "n"],
                        aggfunc="first")
    piv.columns = [f"{a}_{b}_{c}" for a, b, c in piv.columns]
    piv = piv.reset_index()

    meta = m.groupby(k).agg(n_params=("n_params", "max"), n_obs=("n_obs", "max"),
                            oracle=("oracle", "max")).reset_index()
    d = piv.merge(meta, on=k, how="left")

    surv = m.pivot_table(index=k, columns="weighting",
                         values="survives_both_windows", aggfunc="first").reset_index()
    surv = surv.rename(columns={"equal": "survives_both_equal", "recency": "survives_both_recency"})
    d = d.merge(surv, on=k, how="left")

    # the flag: a recency-weighted W2 win that does not repeat in W1
    d["rw_w2_beats_naive"] = d.get("ratio_seasonal_naive_W2_recency", np.nan) < 1.0
    d["rw_w1_beats_naive"] = d.get("ratio_seasonal_naive_W1_recency", np.nan) < 1.0
    d["eq_w2_beats_naive"] = d.get("ratio_seasonal_naive_W2_equal", np.nan) < 1.0
    d["eq_w1_beats_naive"] = d.get("ratio_seasonal_naive_W1_equal", np.nan) < 1.0
    d["FLAG_rw_W2_win_vanishes_in_W1"] = d["rw_w2_beats_naive"] & (~d["rw_w1_beats_naive"])
    d["FLAG_eq_W2_win_vanishes_in_W1"] = d["eq_w2_beats_naive"] & (~d["eq_w1_beats_naive"])

    # accuracy per parameter: how much of the seasonal-naive error each parameter buys
    d["naive_error_removed_pp_W2_equal"] = 1.0 - d.get("ratio_seasonal_naive_W2_equal", np.nan)
    d["error_removed_per_param"] = d["naive_error_removed_pp_W2_equal"] / d["n_params"].replace(0, np.nan)

    cols = k + ["n_params", "n_obs", "oracle",
                "n_W1_equal", "n_W2_equal",
                "mae_W1_equal", "mae_W1_recency", "mae_W2_equal", "mae_W2_recency",
                "ratio_seasonal_naive_W1_equal", "ratio_seasonal_naive_W2_equal",
                "ratio_seasonal_naive_W1_recency", "ratio_seasonal_naive_W2_recency",
                "ratio_street_W1_equal", "ratio_street_W2_equal",
                "survives_both_equal", "survives_both_recency",
                "FLAG_rw_W2_win_vanishes_in_W1", "FLAG_eq_W2_win_vanishes_in_W1",
                "naive_error_removed_pp_W2_equal", "error_removed_per_param"]
    d = d[[c for c in cols if c in d.columns]].sort_values(["target", "mae_W2_equal"])
    d.to_csv(OUT / "20_parameter_budget.csv", index=False)

    flagged = d[d.FLAG_rw_W2_win_vanishes_in_W1 & (~d.oracle)]
    print("rows", len(d), "flagged rw-W2-only winners", len(flagged))
    print(flagged[["method", "object", "spec_id", "target", "n_params",
                   "ratio_seasonal_naive_W1_recency", "ratio_seasonal_naive_W2_recency"]]
          .to_string(index=False))
    print()
    best = d[(d.target == "adj_ebitda_margin_pct") & (~d.oracle)].nsmallest(12, "mae_W2_equal")
    print(best[["method", "object", "spec_id", "n_params", "mae_W1_equal", "mae_W2_equal",
                "error_removed_per_param"]].to_string(index=False))


if __name__ == "__main__":
    main()
