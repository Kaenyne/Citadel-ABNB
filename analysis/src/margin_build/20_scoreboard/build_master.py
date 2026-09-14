"""WS20 step 1: master scoreboard.

Reads the margin harness scoreboard and registry, and writes
data/processed/margin_build/20_scoreboard/20_scoreboard_master.csv
with one row per (method, object, spec_id, target, window, horizon_q, weighting).
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HARN = ROOT / "data" / "processed" / "margin_build" / "10_harness_margin"
OUT = ROOT / "data" / "processed" / "margin_build" / "20_scoreboard"
OUT.mkdir(parents=True, exist_ok=True)

BASE = ["seasonal_naive", "seasonal_naive_drift", "trailing4", "pct_rev_last4",
        "guide_implied", "q_guide_implied", "street"]


def main():
    s = pd.read_csv(HARN / "scoreboard_margin.csv")
    s["spec_id"] = s["spec_id"].fillna("(none)")

    key = ["method", "object", "spec_id", "target", "window", "horizon_q"]

    # --- hindsight: PIT vs full_sample MAE on the same key -------------------
    pit = s[s.prior_basis == "PIT"].set_index(key)
    full = s[s.prior_basis == "full_sample"].set_index(key)
    hind = pd.DataFrame(index=pit.index)
    hind["mae_full_sample"] = full["mae"].reindex(pit.index)
    hind["rw_mae_full_sample"] = full["rw_mae"].reindex(pit.index)
    hind["hindsight_gap_mae"] = pit["mae"] - hind["mae_full_sample"]
    hind["hindsight_share"] = hind["hindsight_gap_mae"] / pit["mae"].replace(0, np.nan)
    hind["rw_hindsight_gap_mae"] = pit["rw_mae"] - hind["rw_mae_full_sample"]
    hind["rw_hindsight_share"] = hind["rw_hindsight_gap_mae"] / pit["rw_mae"].replace(0, np.nan)

    p = pit.join(hind).reset_index()

    rows = []
    for w, pre in (("equal", ""), ("recency", "rw_")):
        d = pd.DataFrame({
            "method": p["method"], "object": p["object"], "spec_id": p["spec_id"],
            "target": p["target"], "window": p["window"], "horizon_q": p["horizon_q"],
            "weighting": w, "n": p["n"],
            "first_quarter": p["first_quarter"], "last_quarter": p["last_quarter"],
            "mae": p[pre + "mae"], "rmse": p[pre + "rmse"], "bias": p[pre + "bias"],
            "crps": p[pre + "crps"], "pinball_mean": p[pre + "pinball_mean"],
            "cov80": p[pre + "cov80"], "cov90": p[pre + "cov90"], "pit_mean": p[pre + "pit_mean"],
        })
        for b in BASE:
            d["ratio_" + b] = p[pre + "mae_ratio_" + b]
            d["n_match_" + b] = p["n_match_" + b]
        d["beats_seasonal_naive"] = p[pre + "beats_seasonal_naive"]
        d["survives_both_windows"] = p[pre + "survives_both_windows"]
        d["mae_full_sample"] = p[pre + "mae_full_sample"]
        d["hindsight_gap_mae"] = p[pre + "hindsight_gap_mae"]
        d["hindsight_share"] = p[pre + "hindsight_share"]
        d["n_params"] = p["n_params"]
        d["n_obs"] = p["n_obs"]
        d["param_obs_ratio"] = p["param_obs_ratio"]
        d["conformal_cov_empirical"] = p["conformal_cov_empirical"]
        d["replays_present"] = p["replays_present"]
        rows.append(d)
    out = pd.concat(rows, ignore_index=True)

    # both-window survival flag combining equal AND recency, per weighting-free key
    k2 = ["method", "object", "spec_id", "target", "horizon_q"]
    surv = (out.assign(f=out["survives_both_windows"].astype(str).str.lower().isin(["true", "yes", "1"]))
              .groupby(k2 + ["weighting"])["f"].max().unstack("weighting"))
    surv["survives_both_windows_eq_and_rw"] = surv.get("equal", False) & surv.get("recency", False)
    out = out.merge(surv[["survives_both_windows_eq_and_rw"]].reset_index(), on=k2, how="left")

    out = out.sort_values(["target", "horizon_q", "window", "weighting", "mae"])
    out.to_csv(OUT / "20_scoreboard_master.csv", index=False)
    print("wrote", OUT / "20_scoreboard_master.csv", out.shape)
    return out


if __name__ == "__main__":
    main()
