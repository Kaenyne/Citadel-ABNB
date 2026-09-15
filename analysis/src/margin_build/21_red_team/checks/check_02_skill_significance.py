"""WS21 check 02: is any margin 'survives_both_windows' win distinguishable from zero?

For every scoreboard cell that carries BOTH survive flags on adj_ebitda_margin_pct, take the
paired loss differential against the seasonal-naive baseline on the SAME quarters
  d_q = |e_method_q| - |e_seasonal_naive_q|
and report mean(d), its Newey-West(1) standard error, the t statistic and a two-sided p-value
(normal), plus a sign test and a 10,000-draw stationary-block bootstrap of mean(d).
n is 14 (W1) or 10 (W2): the point of the check is how little that n can resolve.

Also reports the multiple-comparison denominator: how many margin cells were scored in total.

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_02_skill_significance.py [processed_dir]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PROC = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data/processed/margin_build"
SB = PROC / "10_harness_margin" / "scoreboard_margin.csv"
BQ = PROC / "10_harness_margin" / "scoreboard_by_quarter.csv"
TARGET = "adj_ebitda_margin_pct"
RNG = np.random.default_rng(20260914)


def nw_se(d: np.ndarray, lag: int = 1) -> float:
    n = len(d)
    x = d - d.mean()
    g0 = float(x @ x) / n
    var = g0
    for l in range(1, lag + 1):
        if l >= n:
            break
        gl = float(x[l:] @ x[:-l]) / n
        var += 2.0 * (1.0 - l / (lag + 1.0)) * gl
    var = max(var, 1e-12)
    return float(np.sqrt(var / n))


def block_boot(d: np.ndarray, n_draw: int = 10000, block: int = 2) -> tuple:
    n = len(d)
    means = np.empty(n_draw)
    n_blocks = int(np.ceil(n / block))
    for i in range(n_draw):
        starts = RNG.integers(0, n, size=n_blocks)
        idx = np.concatenate([np.arange(s, s + block) % n for s in starts])[:n]
        means[i] = d[idx].mean()
    return float(np.quantile(means, 0.05)), float(np.quantile(means, 0.95)), float((means >= 0).mean())


def main() -> int:
    sb = pd.read_csv(SB)
    bq = pd.read_csv(BQ)
    marg = sb[(sb["target"] == TARGET) & (sb["prior_basis"] == "PIT") & (sb["method"] != "baselines-margin")]
    n_cells = marg.groupby(["method", "object", "spec_id", "horizon_q"]).ngroups
    print(f"margin PIT cells scored (method,object,spec,h): {n_cells}")
    sur = marg[(marg["window"] == "W1") & marg["survives_both_windows"] & marg["rw_survives_both_windows"]]
    print(f"cells with both survive flags: {len(sur)}  ({100*len(sur)/max(n_cells,1):.1f}% of cells)\n")
    rows = []
    for r in sur.itertuples():
        for win in ("W1", "W2"):
            g = bq[(bq["method"] == r.method) & (bq["object"] == r.object) & (bq["target"] == TARGET)
                   & (bq["spec_id"].astype(str) == str(r.spec_id)) & (bq["horizon_q"] == r.horizon_q)
                   & (bq["prior_basis"] == "PIT") & (bq["window"] == win)].sort_values("quarter")
            g = g.dropna(subset=["abs_err", "seasonal_naive_abs_err"])
            if len(g) < 3:
                continue
            d = (g["abs_err"] - g["seasonal_naive_abs_err"]).to_numpy(dtype=float)
            se = nw_se(d)
            t = d.mean() / se if se > 0 else np.nan
            p = 2 * (1 - stats.norm.cdf(abs(t))) if np.isfinite(t) else np.nan
            n_better = int((d < 0).sum())
            p_sign = float(stats.binomtest(n_better, len(d), 0.5, alternative="greater").pvalue)
            lo, hi, p_boot_ge0 = block_boot(d)
            rows.append(dict(method=r.method, object=r.object, spec=r.spec_id, h=int(r.horizon_q), window=win,
                             n=len(d), mean_d_pp=d.mean(), nw_se=se, t=t, p_two_sided=p,
                             quarters_better=f"{n_better}/{len(d)}", p_sign_test=p_sign,
                             boot_q05=lo, boot_q95=hi, p_boot_no_gain=p_boot_ge0))
    out = pd.DataFrame(rows)
    with pd.option_context("display.width", 250, "display.max_columns", 30, "display.max_rows", 100):
        print(out.round(4).to_string(index=False))
    if len(out):
        print(f"\ncells whose paired gain is significant at p<0.05 (two-sided, NW1): "
              f"{int((out['p_two_sided'] < 0.05).sum())} of {len(out)}")
        print(f"cells whose gain is significant at p<0.10: {int((out['p_two_sided'] < 0.10).sum())} of {len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
