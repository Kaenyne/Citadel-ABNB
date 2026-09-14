"""Independent B2 power audit. Reads frozen inputs; creates timestamped outputs."""
from __future__ import annotations

import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "data/processed/forecast_methods/alpha_b2/run_20260913T171654_499731Z"
RETURN_PATH = ROOT / "data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv"
THRESHOLDS = (0.5, 1.0, 1.5)
HORIZONS = (1, 5, 20, 60)


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    z = stats.norm.ppf(0.975)
    denominator = n + z * z
    center = (k + z * z / 2) / denominator
    radius = z * math.sqrt(k * (n - k) / n + z * z / 4) / denominator
    return center - radius, center + radius


def detection(n: int) -> dict:
    if n < 1:
        return {}
    candidates = [k for k in range(n + 1) if stats.binom.sf(k - 1, n, .5) <= .05]
    if not candidates:
        return {"critical_hits": None, "p80": None}
    critical = min(candidates)
    p80 = optimize.brentq(lambda p: stats.binom.sf(critical - 1, n, p) - .8, .5, 1)
    return {
        "critical_hits": critical,
        "p80": p80,
        "mde_above_50_pp": 100 * (p80 - .5),
        "power_at_70_pct": 100 * stats.binom.sf(critical - 1, n, .7),
        "empirical_gate_hits": math.ceil(.7 * n),
        "probability_meet_empirical_gate_at_true_70_pct": 100 * stats.binom.sf(math.ceil(.7 * n) - 1, n, .7),
    }


def return_summary(values: np.ndarray) -> dict:
    n = len(values)
    mean = float(np.mean(values)) if n else float("nan")
    if n < 2:
        return {"n": n, "mean_pp": mean}
    sd = float(np.std(values, ddof=1))
    se = sd / math.sqrt(n)
    critical = stats.t.ppf(.95, n - 1)
    standardized = optimize.brentq(
        lambda effect: stats.nct.sf(critical, n - 1, effect * math.sqrt(n)) - .8, 0, 10
    )
    radius = stats.t.ppf(.975, n - 1) * se
    leave_one = (values.sum() - values) / (n - 1)
    return {
        "n": n, "mean_pp": mean, "sd_pp": sd,
        "iid_t95_lo_pp": mean - radius, "iid_t95_hi_pp": mean + radius,
        "iid_mde80_standardized": standardized, "iid_mde80_pp": standardized * sd,
        "leave_one_out_positive": int(np.sum(leave_one > 0)),
        "leave_one_out_negative": int(np.sum(leave_one < 0)),
        "leave_one_out_min_pp": float(np.min(leave_one)),
        "leave_one_out_max_pp": float(np.max(leave_one)),
    }


def main() -> None:
    start = time.perf_counter()
    cells = pd.read_csv(SOURCE / "cells.csv")
    returns = pd.read_csv(RETURN_PATH)
    assert not returns.event_date.duplicated().any(), "Return events must be unique"
    rebuilt_signal = 100 * (cells.k_q1_musd / cells.c_pre_value - 1)
    rebuilt_revision = 100 * (cells.c_next_value / cells.c_pre_value - 1)
    np.testing.assert_allclose(cells.s1_pct, rebuilt_signal, atol=1e-10, rtol=0, equal_nan=True)
    np.testing.assert_allclose(cells.revision_pct, rebuilt_revision, atol=1e-10, rtol=0, equal_nan=True)
    for h in (20, 60):
        matched = cells.merge(returns[["event_date", f"excess_open_{h}d_pct"]], on="event_date", validate="many_to_one", suffixes=("", "_source"))
        np.testing.assert_allclose(matched[f"excess_open_{h}d_pct"], matched[f"excess_open_{h}d_pct_source"], atol=1e-10, rtol=0, equal_nan=True)
    # Replace copied return columns with source observations before every audit.
    cells = cells.drop(columns=[f"excess_open_{h}d_pct" for h in (20, 60)])
    cells = cells.merge(returns[["event_date"] + [f"excess_open_{h}d_pct" for h in HORIZONS]], on="event_date", validate="many_to_one")
    cells["s1_pct"] = rebuilt_signal
    cells["revision_pct"] = rebuilt_revision
    sign_rows, return_rows, detail, headline, headline_returns = [], [], [], [], []
    strong_sets = {}
    for basis in ("PIT", "full_sample"):
        for weight in sorted(cells.weight.unique()):
            for window, first in (("W1", "2023Q1"), ("W2", "2024Q1")):
                subset = cells[(cells.prior_basis == basis) & np.isclose(cells.weight, weight) & cells.guided_quarter.ge(first)]
                paired = subset.dropna(subset=["s1_pct", "revision_pct"])
                for threshold in THRESHOLDS:
                    strong = paired[paired.s1_pct.abs().gt(threshold)]
                    n = len(strong)
                    hits = int((np.sign(strong.s1_pct) == np.sign(strong.revision_pct)).sum())
                    lo, hi = wilson(hits, n)
                    key = {"prior_basis": basis, "weight": weight, "window": window, "threshold_pp": threshold}
                    row = {**key, "n_pairs": len(paired), "n_strong": n, "hits": hits, "hit_rate": hits / n if n else None,
                           "wilson_lo": lo, "wilson_hi": hi,
                           "corr": paired.s1_pct.corr(paired.revision_pct) if len(paired) > 2 else None,
                           "sign_gate_pass": n >= 6 and hits / n >= .7}
                    row["full_gate_pass"] = row["sign_gate_pass"] and row["corr"] > .4
                    sign_rows.append(row)
                    is_headline = basis == "PIT" and np.isclose(weight, 2 / 3) and threshold == .5
                    if is_headline:
                        headline.append({**row, **detection(n), "iid_p_lower_tail_against_70": stats.binom.cdf(hits, n, .7)})
                        strong_sets[window] = set(strong.event_date)
                        for event in strong.to_dict("records"):
                            detail.append({"window": window, **event, "hit": int(np.sign(event["s1_pct"]) == np.sign(event["revision_pct"]))})
                    for h in HORIZONS:
                        rpaired = subset.dropna(subset=["s1_pct", f"excess_open_{h}d_pct"])
                        rstrong = rpaired[rpaired.s1_pct.abs().gt(threshold)]
                        values = (np.sign(rstrong.s1_pct) * rstrong[f"excess_open_{h}d_pct"]).to_numpy()
                        result = {**key, "horizon": h, **return_summary(values)}
                        return_rows.append(result)
                        if is_headline:
                            headline_returns.append(result)
    expected = {"W1": (9, 5), "W2": (7, 4)}
    for row in headline:
        assert (row["n_strong"], row["hits"]) == expected[row["window"]]
    assert strong_sets["W2"] <= strong_sets["W1"]
    assert len(sign_rows) == 36 and len(return_rows) == 144
    assert all(row["mean_pp"] < 0 for row in headline_returns if row["horizon"] in (20, 60))
    source_stats = pd.read_csv(SOURCE / "statistics.csv")
    source_returns = pd.read_csv(SOURCE / "return_statistics.csv")
    source_baselines = pd.read_csv(SOURCE / "revision_baselines.csv")
    n80 = next(n for n in range(1, 301) if detection(n).get("power_at_70_pct", 0) >= 80)
    output = ROOT / "data/processed/forecast_methods/refute_b2_power_v1" / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    for name, rows in (("headline_sign.csv", headline), ("headline_returns.csv", headline_returns), ("strong_events.csv", detail),
                       ("posthoc_sign_grid.csv", sign_rows), ("posthoc_return_grid.csv", return_rows)):
        pd.DataFrame(rows).to_csv(output / name, index=False)
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
              [SOURCE / "cells.csv", SOURCE / "statistics.csv", SOURCE / "return_statistics.csv", SOURCE / "revision_baselines.csv", RETURN_PATH, Path(__file__)]}
    summary = {
        "verdict": "SURVIVED", "headline_sign": headline, "headline_returns": headline_returns,
        "overlap": {"W1_strong": len(strong_sets["W1"]), "W2_strong": len(strong_sets["W2"]),
                    "intersection": len(strong_sets["W1"] & strong_sets["W2"]), "union": len(strong_sets["W1"] | strong_sets["W2"]),
                    "W1_only": sorted(strong_sets["W1"] - strong_sets["W2"])},
        "original_inventory": {"thresholds": [.5], "return_horizons": [20, 60], "computed_weights": [.33, .5, 2 / 3],
                               "summarized_weights": [2 / 3], "replays": ["PIT", "full_sample"], "windows": ["W1", "W2"],
                               "event_scenario_rows": len(cells), "sign_correlation_rows": len(source_stats),
                               "return_rows": len(source_returns), "baseline_rows": len(source_baselines),
                               "original_primary_gating_rows": 2},
        "new_posthoc_inventory": {"thresholds": THRESHOLDS, "horizons": HORIZONS, "sign_rows": len(sign_rows), "return_rows": len(return_rows)},
        "iid_exact_binomial_min_n_for_80pct_power_at_true_70": n80,
        "hashes": hashes, "elapsed_seconds": time.perf_counter() - start,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "headline_sign": headline, "headline_returns": headline_returns,
                      "overlap": summary["overlap"], "inventory": summary["original_inventory"], "n80": n80,
                      "elapsed_seconds": summary["elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
