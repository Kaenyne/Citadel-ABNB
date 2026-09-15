"""Group A reproduction of R01/R02: paired-loss tests vs seasonal naive for M1/M4/M6 margin cells."""
import numpy as np, pandas as pd
from pathlib import Path
from scipy import stats

REPO = Path(r"C:\Users\krish\citadel-abnb-margins")
bq = pd.read_csv(REPO/"data/processed/margin_build/10_harness_margin/scoreboard_by_quarter.csv")

MINE = {"driver-lines": "M1", "alt-augmented": "M4", "cycle-flex": "M6"}

def nw_t(d, lag=1):
    n = len(d); m = d.mean(); e = d - m
    g0 = (e*e).sum()/n
    v = g0
    for L in range(1, lag+1):
        if n > L:
            gl = (e[L:]*e[:-L]).sum()/n
            v += 2*(1 - L/(lag+1))*gl
    se = np.sqrt(v/n)
    return (m/se if se > 0 else np.nan), se

rows = []
sub = bq[(bq.target == "adj_ebitda_margin_pct") & (bq.prior_basis == "PIT") & (bq.horizon_q == 0)
         & (bq.method.isin(MINE))]
for (meth, obj, spec, win), g in sub.groupby(["method", "object", "spec_id", "window"]):
    g = g.sort_values("quarter")
    d = (g["abs_err"] - g["seasonal_naive_abs_err"]).to_numpy(float)
    n = len(d)
    t, se = nw_t(d)
    better = int((d < 0).sum())
    p_t = 2*(1-stats.norm.cdf(abs(t))) if np.isfinite(t) else np.nan
    p_sign = stats.binomtest(better, n, 0.5).pvalue
    w = g["weight_rw"].to_numpy(float); w = w/w.sum()
    rows.append(dict(method=MINE[meth], obj=obj, spec=spec, window=win, n=n,
                     mae=g["abs_err"].mean(), mae_sn=g["seasonal_naive_abs_err"].mean(),
                     ratio=g["abs_err"].mean()/g["seasonal_naive_abs_err"].mean(),
                     rw_ratio=float((w*g["abs_err"]).sum()/(w*g["seasonal_naive_abs_err"]).sum()),
                     mean_d=d.mean(), nw_t=t, p_nw=p_t, better=better, p_sign=p_sign))
r = pd.DataFrame(rows).sort_values(["method", "obj", "spec", "window"])
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(r.round(3).to_string(index=False))
r.to_csv(REPO/"data/processed/margin_build/22_discussion_group_A/groupA_paired_tests.csv", index=False)
