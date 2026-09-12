"""FX live-quarter falsification: does the fitted lag structure reproduce management's stated 3Q26 FX?"""
import pandas as pd, numpy as np
from pathlib import Path
from scipy import stats, optimize
REPO=Path("/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB")
O=REPO/"data/processed/overnight"
d=pd.read_csv(O/"10_fx_daily.csv",parse_dates=["date"]); d["q"]=d["date"].dt.to_period("Q")
qa=d.groupby(["q","ccy"])["usd_per_unit"].mean().unstack(); yoy=(qa/qa.shift(4)-1)*100
bk=pd.read_csv(O/"10_fx_basket.csv"); bk=bk[bk.currency!="BASKET"]
m=d.drop_duplicates("fred_id")[["fred_id","ccy"]].set_index("fred_id")["ccy"].to_dict()
RB={}
for r,g in bk.groupby("region"):
    s=0.0; w=0.0
    for _,row in g.iterrows():
        ww=float(row["weight"]); c=(pd.Series(0.0,index=yoy.index) if pd.isna(row["fred_id"]) else yoy[m[row["fred_id"]]])
        s=s+c*ww; w+=ww
    RB[r]=s/w
RB=pd.DataFrame(RB)
L0=pd.read_csv(REPO/"data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv"); L0=L0[L0.basis=="filed"]
qp=lambda s: pd.Period(f"20{int(s[2:]):02d}Q{s[0]}",freq="Q")
L0["qp"]=L0["quarter"].map(qp)
piv=L0.pivot_table(index="qp",columns="region",values="revenue_musd",aggfunc="sum").sort_index()
sh=(piv.rolling(4).sum().div(piv.rolling(4).sum().sum(axis=1),axis=0)).dropna(how="any")
G={}
for q in RB.index:
    pv=[x for x in sh.index if x<q]; w=sh.loc[pv[-1]] if pv else sh.iloc[0]
    cols=[c for c in w.index if c in RB.columns]
    v=sum(RB.loc[q,c]*w[c] for c in cols)/sum(w[c] for c in cols)
    if pd.notna(v): G[q]=float(v)
G=pd.Series(G).sort_index()
k=pd.read_csv(O/"02_kpi_panel_quarterly.csv"); k["qp"]=k["quarter"].map(qp)
tgt=k.set_index("qp")["fx_pts_revenue"].dropna()
idx=list(pd.period_range("2023Q1","2026Q2",freq="Q"))
y=np.array([tgt[q] for q in idx]); X=np.column_stack([[G[q] for q in idx],[G[q-1] for q in idx],[G[q-2] for q in idx]])
def nll(t):
    a=t[:3]; s=np.exp(t[3])
    if np.any(a<0): return 1e9
    mu=X@a; p=np.clip(stats.norm.cdf((y+.5-mu)/s)-stats.norm.cdf((y-.5-mu)/s),1e-300,None)
    return -np.sum(np.log(p))
best=min([optimize.minimize(nll,st,method="Nelder-Mead",options=dict(maxiter=20000,xatol=1e-9,fatol=1e-11))
          for st in [[.3,.3,.3,0],[.6,0,0,0],[0,.6,0,0],[0,0,.6,0],[.5,.4,0,0]]],key=lambda r:r.fun)
a=np.clip(best.x[:3],0,None)
Q3=pd.Period("2026Q3",freq="Q"); Q4=pd.Period("2026Q4",freq="Q")
b3=np.array([G[Q3],G[Q3-1],G[Q3-2]]); b4=np.array([np.nan,G[Q4-1],G[Q4-2]])
print("basket lag vector 3Q26 (l0 QTD-28Aug, l1, l2):",np.round(b3,3))
MGMT=3.0
print("\nMANAGEMENT 2026-08-06 letter: 3Q26 revenue growth 15-17pct 'inclusive of an approximate THREE percentage point FX tailwind AFTER factoring in our hedging program'")
print("fx-lag registered LIVE 3Q26 point = +1.2pp, q10-q90 = [0.074, 2.326]  -> management's 3.0 is OUTSIDE the 80pct interval\n")
rows=[]
def pred(w,b): return float(np.nansum(np.array(w)*b))
specs={
 "free fit (package Object A, stated)":a,
 "Theo pure lag-2 x0.56":[0,0,0.56],
 "architect Phi x0.56":[0,2/3*0.56,1/3*0.56],
 "architect Phi x fitted stated scale 0.851":[0,2/3*0.851,1/3*0.851],
 "contemporaneous x0.56":[0.56,0,0],
}
print(f"{'spec':45s} {'3Q26 pred':>10s} {'vs mgmt 3.0':>12s} | backtest 1Q26 (act 3.0) 2Q26 (act 4.0)")
for nm,w in specs.items():
    p3=pred(w,b3)
    p1=pred(w,[G[pd.Period('2026Q1',freq='Q')-i] for i in range(3)])
    p2=pred(w,[G[pd.Period('2026Q2',freq='Q')-i] for i in range(3)])
    print(f"{nm:45s} {p3:10.2f} {p3-MGMT:12.2f} |  {p1:6.2f} ({p1-3:+.2f})   {p2:6.2f} ({p2-4:+.2f})")
print("\n4Q26 (only lags 1,2 knowable today; lag0 = 4Q26 spot, unknown):")
for nm,w in specs.items():
    print(f"  {nm:45s} lag1/lag2 part = {np.nansum(np.array(w)[1:]*b4[1:]):.2f}pp")
# scale needed on Phi weights to hit 3.0
need=MGMT/(2/3*b3[1]+1/3*b3[2]); print(f"\nPhi-weight scale required to match mgmt 3.0pp on 3Q26 = {need:.3f}  (fitted stated scale 0.851, disclosed non-USD share 0.56)")
# full-model scale needed
print(f"Free-weight model would need basket scale x{MGMT/ (a@b3):.2f} to match mgmt")
