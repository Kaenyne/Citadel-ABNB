"""WS21 check 06: (a) re-score every LINE-level claim on adj_ebitda_margin_pct (M4's cross-method warning),
and (b) interval calibration of every registered object.

(a) For every (method, object, spec) that has a line target and a margin target at h=0, PIT, report the
    line MAE ratio to seasonal naive and the MARGIN MAE ratio side by side, in both windows. A spec that
    improves lines and worsens the margin is the failure mode M4 found (M1's line errors cancel in the sum).
(b) cov80 / cov90 against the nominal 0.80 / 0.90 for every object at h=0, with the binomial 90%
    interval attainable at n=14 / n=10, so 'under-covers' is claimed only where n can support it.

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_06_lines_vs_margin_and_coverage.py [processed_dir]
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
SB = pd.read_csv(PROC / "10_harness_margin" / "scoreboard_margin.csv")
LINES = ["cor_cash_musd", "ops_cash_musd", "pd_cash_musd", "sm_cash_musd", "ga_cash_ex_reserves_musd"]


def main() -> int:
    d = SB[(SB["prior_basis"] == "PIT") & (SB["horizon_q"] == 0)]
    print("=== (a) line improvement vs margin improvement, same method/spec, h=0, PIT ===")
    rows = []
    for meth in sorted(set(d["method"]) - {"baselines-margin"}):
        m = d[d["method"] == meth]
        for spec in sorted(set(m["spec_id"].dropna())):
            s = m[m["spec_id"] == spec]
            for win in ("W1", "W2"):
                w = s[s["window"] == win]
                ln = w[w["target"].isin(LINES)]["mae_ratio_seasonal_naive"]
                mg = w[w["target"] == "adj_ebitda_margin_pct"]["mae_ratio_seasonal_naive"]
                if len(ln) == 0 or len(mg) == 0:
                    continue
                rows.append(dict(method=meth, spec=spec, window=win, n_lines=len(ln),
                                 lines_mean_ratio=float(ln.mean()),
                                 lines_beating_naive=int((ln < 1).sum()),
                                 margin_ratio=float(mg.iloc[0]),
                                 lines_better_margin_worse=bool(ln.mean() < 1 and mg.iloc[0] > 1)))
    o = pd.DataFrame(rows)
    with pd.option_context("display.width", 220, "display.max_rows", 200):
        print(o.round(3).to_string(index=False))
    bad = o[o["lines_better_margin_worse"]]
    print(f"\nspec/window cells where the LINES beat naive on average but the MARGIN does not: {len(bad)} of {len(o)}")
    if len(bad):
        print(bad[["method", "spec", "window", "lines_mean_ratio", "margin_ratio"]].round(3).to_string(index=False))
    print("\ncorrelation across cells between mean line ratio and margin ratio: "
          f"{o['lines_mean_ratio'].corr(o['margin_ratio']):.3f}  (a low or negative value means line-level "
          "tuning does not transmit to the margin)")

    print("\n=== (b) interval calibration at h=0, PIT, adj_ebitda_margin_pct ===")
    c = d[(d["target"] == "adj_ebitda_margin_pct")][
        ["method", "object", "spec_id", "window", "n", "cov80", "cov90", "pit_mean", "n_params"]]
    c = c.dropna(subset=["cov80"])
    def band(n, p):
        lo, hi = stats.binom.ppf([0.05, 0.95], n, p) / n
        return lo, hi
    out = []
    for r in c.itertuples():
        lo80, hi80 = band(int(r.n), 0.80)
        out.append(dict(method=r.method, object=r.object, spec=r.spec_id, window=r.window, n=int(r.n),
                        cov80=r.cov80, band80=f"[{lo80:.2f},{hi80:.2f}]",
                        verdict=("under" if r.cov80 < lo80 else "over" if r.cov80 > hi80 else "ok"),
                        cov90=r.cov90, pit_mean=r.pit_mean, n_params=r.n_params))
    oo = pd.DataFrame(out)
    print(oo["verdict"].value_counts().to_string())
    print("\nunder-covering cells (the ones that matter for a 5 Nov band):")
    print(oo[oo["verdict"] == "under"].round(3).to_string(index=False) or "  none")
    print("\nover-covering cells (intervals too wide to be a trade):", int((oo["verdict"] == "over").sum()))

    print("\n=== (c) every target's coverage, all objects, h=0 PIT, W1 ===")
    all0 = SB[(SB["prior_basis"] == "PIT") & (SB["horizon_q"] == 0) & (SB["window"] == "W1")].dropna(subset=["cov80"])
    g = all0.groupby("target").agg(n_cells=("cov80", "size"), mean_cov80=("cov80", "mean"),
                                   min_cov80=("cov80", "min"), mean_cov90=("cov90", "mean"))
    print(g.round(3).sort_values("mean_cov80").to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
