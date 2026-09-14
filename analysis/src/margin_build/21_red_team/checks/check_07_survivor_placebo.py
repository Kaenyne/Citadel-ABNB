"""WS21 check 07: how many margin cells would 'survive both windows' by chance?

The scorer's headline flag is `survives_both_windows` AND `rw_survives_both_windows`: the object beats
seasonal naive on MAE in W1 (n 14) and W2 (n 10), equal- and recency-weighted. W2's quarters are a SUBSET
of W1's, so the two legs are not independent evidence, and the run scored 165 margin cells.

Null: each cell's per-quarter paired loss differential d_q = |e_method_q| - |e_naive_q| is exchangeable
with mean zero. Draw a sign vector s_q in {-1,+1} over the 14 W1 quarters (one vector per iteration,
applied to EVERY cell, so cross-cell correlation is preserved), set d_q -> s_q d_q, recompute the four
MAE comparisons, and count how many of the 165 cells survive. 2,000 iterations.

Reports the null distribution of the survivor count against the observed count, the per-cell null
survival probability, and the same statistic restricted to cells whose spec is NOT an oracle
(revenue-known) spec.

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_07_survivor_placebo.py [processed_dir]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))
from harness_margin import Q  # noqa: E402

PROC = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data/processed/margin_build"
TARGET = "adj_ebitda_margin_pct"
N_DRAW = 2000
HL = 4.0
RNG = np.random.default_rng(20260914)
ORACLE = ("revknown", "nightsknown", "_known")


def rw(quarters, anchor):
    w = np.array([0.5 ** ((Q.to_index(anchor) - Q.to_index(q)) / HL) for q in quarters], dtype=float)
    return w / w.sum()


def main() -> int:
    bq = pd.read_csv(PROC / "10_harness_margin" / "scoreboard_by_quarter.csv")
    b = bq[(bq["target"] == TARGET) & (bq["prior_basis"] == "PIT") & (bq["method"] != "baselines-margin")
           & (bq["horizon_q"] == 0)].copy()
    b["spec_id"] = b["spec_id"].fillna("").astype(str)
    b = b.dropna(subset=["abs_err", "seasonal_naive_abs_err"])
    cells = []
    for (meth, obj, spec), g in b.groupby(["method", "object", "spec_id"]):
        c = {}
        ok = True
        for win in ("W1", "W2"):
            gg = g[g["window"] == win].sort_values("quarter")
            if len(gg) < 5:
                ok = False
                break
            c[win] = (gg["quarter"].tolist(),
                      (gg["abs_err"] - gg["seasonal_naive_abs_err"]).to_numpy(dtype=float))
        if ok:
            cells.append(((meth, obj, spec), c))
    print(f"margin h=0 PIT cells with both windows: {len(cells)}")

    def survives(c, signs=None):
        for win in ("W1", "W2"):
            qs, d = c[win]
            dd = d if signs is None else d * np.array([signs[q] for q in qs])
            w = rw(qs, "2026Q2")
            if dd.mean() >= 0 or float(np.sum(w * dd)) >= 0:
                return False
        return True

    obs = [k for k, c in cells if survives(c)]
    print(f"observed survivors (both windows, both weightings): {len(obs)}")
    for k in obs:
        print("   ", "/".join(k))
    allq = sorted({q for _, c in cells for q in c["W1"][0]})
    counts = np.empty(N_DRAW, dtype=int)
    for i in range(N_DRAW):
        s = {q: (1 if RNG.random() < 0.5 else -1) for q in allq}
        counts[i] = sum(1 for _, c in cells if survives(c, s))
    print(f"\nnull distribution of the survivor count over {N_DRAW} sign-flip draws:")
    print(f"   mean {counts.mean():.1f}, median {np.median(counts):.0f}, "
          f"5-95 pct [{np.quantile(counts, 0.05):.0f}, {np.quantile(counts, 0.95):.0f}], max {counts.max()}")
    print(f"   P(null survivor count >= observed {len(obs)}) = {(counts >= len(obs)).mean():.3f}")
    print(f"   per-cell null survival probability = {counts.mean()/len(cells):.3f}  "
          f"(observed rate {len(obs)/len(cells):.3f})")
    nonor = [k for k in obs if not any(t in k[2] for t in ORACLE)]
    print(f"\nsurvivors that are NOT oracle (revenue/nights-known) specs: {len(nonor)} of {len(obs)}")
    for k in nonor:
        print("   ", "/".join(k))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
