"""Independent, read-only A2 power audit; run from the repository root."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/forecast_methods/refute_a2_power_v1"
INPUTS = {
    "cells": "data/processed/forecast_methods/alpha_a2/cells.csv",
    "registry": "data/processed/forecast_methods/registry/alpha-a2__guide_mid_next_q.csv",
    "returns": "data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv",
    "statistics": "data/processed/forecast_methods/alpha_a2/statistics.csv",
    "conditional_returns": "data/processed/forecast_methods/alpha_a2/conditional_returns.csv",
    "controls": "data/processed/forecast_methods/alpha_a2/controls.csv",
    "ridge": "data/processed/forecast_methods/alpha_a2/ridge_expanding.csv",
    "code": "analysis/src/forecast_methods/alpha_a2/run.py",
}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return math.nan, math.nan
    z = stats.norm.ppf(0.975)
    p = k / n
    center = (p + z*z/(2*n))/(1+z*z/n)
    radius = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return center-radius, center+radius


def exact_label_p(signal: np.ndarray, actual: np.ndarray) -> float:
    n = len(signal)
    observed = int(np.sum(signal == actual))
    positives = int(np.sum(actual == 1))
    exceed = 0
    total = 0
    for indexes in itertools.combinations(range(n), positives):
        labels = np.full(n, -1)
        labels[list(indexes)] = 1
        total += 1
        exceed += int(np.sum(labels == signal) >= observed)
    return exceed / total


def binomial_design(n: int) -> dict:
    critical = next((k for k in range(n+1) if stats.binom.sf(k-1, n, .5) <= .05), None)
    assert critical is not None
    mde_p = optimize.brentq(lambda p: stats.binom.sf(critical-1, n, p)-.8, .5, 1.)
    return {
        "null_hit_rate": .5, "alpha": .05, "target_power": .8,
        "critical_hits": critical, "actual_null_size": float(stats.binom.sf(critical-1, n, .5)),
        "power_at_true_hit_rate_70pct": float(stats.binom.sf(critical-1, n, .7)),
        "minimum_detectable_true_hit_rate": mde_p,
        "minimum_detectable_improvement_pp": (mde_p-.5)*100,
        "p_vs_70pct_even_if_all_hit": .7**n,
    }


def return_design(values: np.ndarray) -> dict:
    n = len(values)
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    se = sd / math.sqrt(n)
    critical = stats.t.ppf(.95, n-1)
    standardized_mde = optimize.brentq(
        lambda d: stats.nct.sf(critical, n-1, d*math.sqrt(n))-.8, 0., 20.)
    loomeans = [(float(np.sum(values))-float(v))/(n-1) for v in values]
    return {
        "n": n, "signed_mean_pp": mean, "sample_sd_pp": sd, "sample_se_pp": se,
        "iid_student_t_90_ci": [mean-critical*se, mean+critical*se],
        "iid_one_sided_positive_mean_p": float(stats.t.sf(mean/se, n-1)),
        "alpha": .05, "target_power": .8, "iid_normal_mde_pp": standardized_mde*sd,
        "iid_normal_mde_in_sample_sd": standardized_mde,
        "iid_normal_power_at_positive_2pp_mean": float(stats.nct.sf(critical, n-1, 2./se)),
        "leave_one_out_mean_range_pp": [min(loomeans), max(loomeans)],
        "leave_one_out_positive_count": sum(x>0 for x in loomeans),
    }


def main() -> None:
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    tables = {key: pd.read_csv(ROOT/path) for key, path in INPUTS.items() if path.endswith(".csv")}
    cells = tables["cells"]
    registered = tables["registry"]
    primary = registered[(registered.prior_basis == "PIT") & (registered.window == "W1")]
    assert not primary.quarter.duplicated().any()
    event = cells.merge(primary[["quarter", "point", "vintage_date"]], on="quarter", how="inner", validate="one_to_one")
    assert (event.guide_date == event.vintage_date).all()
    event["recomputed_signal_pct"] = (event.point/event.consensus_musd-1)*100
    event["recomputed_gap_lo"] = ((event.guide_mid_musd-.5)/event.consensus_musd-1)*100
    event["recomputed_gap_hi"] = ((event.guide_mid_musd+.5)/event.consensus_musd-1)*100
    event["recomputed_actual_sign"] = np.select([event.recomputed_gap_lo > 0, event.recomputed_gap_hi < 0], [1, -1], 0)
    eligible = event.dropna(subset=["recomputed_signal_pct", "actual_gap_pct"])
    assert np.allclose(eligible.recomputed_signal_pct, eligible.default_signal_pct, atol=1e-11, rtol=0)
    event = event.merge(tables["returns"][["event_date", "excess_open_20d_pct"]].rename(columns={"excess_open_20d_pct": "raw_return20_pp"}), left_on="guide_date", right_on="event_date", how="left", validate="one_to_one")
    assert np.allclose(event.raw_return20_pp, event.excess_open_20d_pct)
    windows = {}
    primary_sets = {}
    for window, start in (("W1", "2023Q1"), ("W2", "2024Q1")):
        high = event[event.quarter.between(start, "2026Q2") & (event.recomputed_signal_pct.abs()>1) & (event.recomputed_actual_sign.abs()==1)].copy()
        high["signal_sign"] = np.sign(high.recomputed_signal_pct)
        high["hit"] = high.signal_sign == high.recomputed_actual_sign
        high["signed_return20_pp"] = high.signal_sign * high.raw_return20_pp
        n, k = len(high), int(high.hit.sum())
        row = tables["statistics"][(tables["statistics"].variant=="default") & (tables["statistics"].window==window)].iloc[0]
        assert (n, k) == (row.n_scored, row.hits)
        assert np.allclose(wilson(k,n), [row.wilson95_lo, row.wilson95_hi])
        assert np.isclose(high.signed_return20_pp.mean(), row.signed_return20_mean)
        primary_sets[window] = set(high.quarter)
        windows[window] = {
            "n": n, "hits": k, "hit_rate": k/n, "wilson95": wilson(k,n),
            "exact_fixed_label_permutation_p": exact_label_p(high.signal_sign.to_numpy(), high.recomputed_actual_sign.to_numpy()),
            "iid_binomial_p_vs_half": float(stats.binom.sf(k-1,n,.5)),
            "signal_positive_n": int((high.signal_sign>0).sum()),
            "actual_positive_n": int((high.recomputed_actual_sign>0).sum()),
            "binomial_power_reference": binomial_design(n),
            "returns": return_design(high.signed_return20_pp.to_numpy()),
        }
        high.to_csv(OUT/f"primary_events_{window}.csv", index=False)

    sensitivity = []
    for variant in ("default", "ex_covid", "full_sample"):
        for window, start in (("W1", "2023Q1"), ("W2", "2024Q1")):
            base = cells[cells.quarter.between(start,"2026Q2")].dropna(subset=[variant+"_signal_pct", "actual_gap_pct"])
            for threshold in (.5,1.,1.5):
                sel = base[(base[variant+"_signal_pct"].abs()>threshold) & (base.actual_sign.abs()==1)]
                n = len(sel)
                sign = np.sign(sel[variant+"_signal_pct"])
                k = int((sign==sel.actual_sign).sum())
                low, high = wilson(k,n)
                for horizon in (1,5,20,60):
                    ret = (sign*sel[f"excess_open_{horizon}d_pct"]).dropna()
                    sensitivity.append({"variant":variant,"window":window,"threshold_pp":threshold,"horizon":horizon,"n_sign":n,"hits":k,"hit_rate":k/n if n else None,"wilson95_lo":low,"wilson95_hi":high,"n_return":len(ret),"signed_return_mean_pp":ret.mean(),"origin":"refuter_new_stress" if threshold!=1. else "recomputed_original_cutoff"})
    pd.DataFrame(sensitivity).to_csv(OUT/"threshold_sensitivity.csv", index=False)

    original = tables["conditional_returns"]
    family = {"reported_return_cells":len(original), "nonempty_return_cells":int((original.n>0).sum()), "return_cell_dimensions":{col:sorted(original[col].unique().tolist()) for col in ("variant","window","strategy","subset","side","horizon")}, "primary_window_kernel_pooled_return_cells":int(((original.window.isin(["W1","W2"]))&(original.strategy=="kernel")&(original.side=="direction_adjusted")).sum()), "primary_window_kernel_pooled_high_signal_cells":int(((original.window.isin(["W1","W2"]))&(original.strategy=="kernel")&(original.side=="direction_adjusted")&(original.subset=="abs_signal_gt1")).sum()), "sign_and_gap_summary_rows":len(tables["statistics"]), "control_rows":len(tables["controls"]),"ridge_prediction_rows":len(tables["ridge"]),"new_threshold_stress_return_cells":len(sensitivity),"default_ex_covid_signals_identical":bool(np.allclose(cells.default_signal_pct,cells.ex_covid_signal_pct,equal_nan=True))}
    result = {"windows":windows,"nesting":{"W2_subset_W1":primary_sets["W2"].issubset(primary_sets["W1"]),"unique_high_signal_events":len(primary_sets["W1"]|primary_sets["W2"]),"W1_only_high_signal_events":sorted(primary_sets["W1"]-primary_sets["W2"])},"specification_inventory":family,"inputs_sha256":{path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in INPUTS.values()},"runtime_seconds":time.perf_counter()-started}
    (OUT/"audit.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="inputs_sha256"},indent=2,allow_nan=False))


if __name__ == "__main__":
    main()
