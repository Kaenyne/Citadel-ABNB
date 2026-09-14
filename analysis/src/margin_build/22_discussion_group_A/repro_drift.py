"""Group A: paired-loss tests against seasonal_naive_drift (the honest baseline for a growing dollar line)."""
import numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
REPO = Path(r"C:\Users\krish\citadel-abnb-margins")
REG = REPO/"data/processed/margin_build/registry"
bq = pd.read_csv(REPO/"data/processed/margin_build/10_harness_margin/scoreboard_by_quarter.csv")
dr = pd.read_csv(REG/"baselines-margin__seasonal_naive_drift.csv")
dr = dr[dr.prior_basis == "PIT"]
key = dr.set_index(["target", "quarter", "vintage_date", "horizon_q"])["point"].to_dict()
tg = pd.read_csv(REPO/"data/processed/margin_build/10_harness_margin/targets.csv")
act = {}
for t in tg.columns:
    pass

def nw_t(d, lag=1):
    n=len(d); m=d.mean(); e=d-m; g0=(e*e).sum()/n; v=g0
    for L in range(1,lag+1):
        if n>L: v += 2*(1-L/(lag+1))*(e[L:]*e[:-L]).sum()/n
    se=np.sqrt(v/n); return (m/se if se>0 else np.nan)

MINE={"driver-lines":"M1","alt-augmented":"M4","cycle-flex":"M6"}
MAIN={"driver-lines":["b_elastic_rw","b_elastic_eq"],"alt-augmented":["none_rw","best1_rw","ridge_all_eq"],"cycle-flex":["l0_rw","l0_eq"]}
TARGETS=["adj_ebitda_margin_pct","cor_cash_musd","ops_cash_musd","pd_cash_musd","sm_cash_musd",
         "ga_cash_ex_reserves_musd","total_cash_costs_musd","adj_ebitda_musd"]
rows=[]
sub=bq[(bq.prior_basis=="PIT")&(bq.horizon_q==0)&(bq.method.isin(MINE))&(bq.target.isin(TARGETS))]
for (meth,spec,win,t),g in sub.groupby(["method","spec_id","window","target"]):
    if spec not in MAIN[meth]: continue
    g=g.sort_values("quarter").copy()
    g["drift"]=[key.get((t,q,v,0),np.nan) for q,v in zip(g.quarter,g.vintage_date)]
    g=g[g.drift.notna()]
    if len(g)<5: continue
    ae=g.abs_err.to_numpy(float); ad=np.abs(g.drift.to_numpy(float)-g.actual.to_numpy(float))
    d=ae-ad; n=len(d); tt=nw_t(d); better=int((d<0).sum())
    w=g.weight_rw.to_numpy(float); w=w/w.sum()
    rows.append(dict(method=MINE[meth],spec=spec,window=win,target=t,n=n,mae=ae.mean(),mae_drift=ad.mean(),
                     ratio=ae.mean()/ad.mean(), rw_ratio=float((w*ae).sum()/(w*ad).sum()),
                     mean_d=d.mean(), nw_t=tt, p=2*(1-stats.norm.cdf(abs(tt))),
                     better=f"{better}/{n}", p_sign=stats.binomtest(better,n,0.5).pvalue))
r=pd.DataFrame(rows).sort_values(["target","method","spec","window"])
pd.set_option("display.width",260); pd.set_option("display.max_rows",300)
print(r.round(3).to_string(index=False))
r.to_csv(REPO/"data/processed/margin_build/22_discussion_group_A/groupA_paired_vs_drift.csv",index=False)
