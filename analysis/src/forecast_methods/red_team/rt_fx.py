"""Independent rebuild of the FX-lag central regression. No package imports."""
import pandas as pd, numpy as np
from pathlib import Path
from scipy import stats, optimize
REPO=Path("/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB")
O=REPO/"data/processed/overnight"

d=pd.read_csv(O/"10_fx_daily.csv", parse_dates=["date"])
d["q"]=d["date"].dt.to_period("Q")
qa=d.groupby(["q","ccy"])["usd_per_unit"].mean().unstack()
yoy=(qa/qa.shift(4)-1.0)*100.0

bk=pd.read_csv(O/"10_fx_basket.csv")
bk=bk[bk.currency!="BASKET"].copy()
print("basket rows:",len(bk)); print(bk[["region","currency","proxy_series","weight","fred_id"]].to_string())

# map fred_id -> ccy label in daily file
m=d.drop_duplicates("fred_id")[["fred_id","ccy"]].set_index("fred_id")["ccy"].to_dict()
print("fred map:",m)

reg_b={}
for r,g in bk.groupby("region"):
    s=None; wsum=0.0
    for _,row in g.iterrows():
        w=float(row["weight"])
        if pd.isna(row["fred_id"]):      # USD leg, 0 y/y
            contrib=pd.Series(0.0,index=yoy.index)
        else:
            c=m.get(row["fred_id"])
            if c is None: raise SystemExit(f"missing {row['fred_id']}")
            contrib=yoy[c]
        s = contrib*w if s is None else s+contrib*w
        wsum+=w
    reg_b[r]=s/wsum
RB=pd.DataFrame(reg_b)

# regional revenue weights: trailing-4 filed regional revenue from L0
L0=pd.read_csv(REPO/"data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv")
L0=L0[L0.basis=="filed"]
def qp(s):
    n,y=s[0],int(s[2:]); return pd.Period(f"20{y:02d}Q{n}",freq="Q")
L0["qp"]=L0["quarter"].map(qp)
piv=L0.pivot_table(index="qp",columns="region",values="revenue_musd",aggfunc="sum").sort_index()
t4=piv.rolling(4).sum()
shares=t4.div(t4.sum(axis=1),axis=0)
# global basket at quarter q uses shares as of q-1 (trailing-4 ending q-1) => PIT-ish
sh=shares.dropna(how='any')
gl={}
for q in RB.index:
    prev=[x for x in sh.index if x < q]
    w=sh.loc[prev[-1]] if prev else sh.iloc[0]   # bfill the earliest share vector for pre-2023 lags
    cols=[c for c in w.index if c in RB.columns]
    v=sum(RB.loc[q,c]*w[c] for c in cols)/sum(w[c] for c in cols)
    if pd.notna(v): gl[q]=float(v)
G=pd.Series(gl).sort_index()
print('shares first row:',sh.index[0],sh.iloc[0].round(3).to_dict())
print("\nglobal basket y/y pct (last 14):"); print(G.tail(16).round(3).to_string())

# target
k=pd.read_csv(O/"02_kpi_panel_quarterly.csv")
k["qp"]=k["quarter"].map(qp)
tgt=k.set_index("qp")["fx_pts_revenue"].dropna()
tadr=k.set_index("qp")["fx_pts_adr"].dropna()

idx=[q for q in pd.period_range("2023Q1","2026Q2",freq="Q")]
y=np.array([tgt[q] for q in idx]); 
X=np.column_stack([[G[q] for q in idx],[G[q-1] for q in idx],[G[q-2] for q in idx]])
print("\nn =",len(y))
for j,lab in enumerate(["lag0","lag1","lag2"]):
    r=np.corrcoef(X[:,j],y)[0,1]
    sl,ic,rr,p,se=stats.linregress(X[:,j],y)
    print(f"  {lab}: r={r:.3f}  slope={sl:.4f} se={se:.4f} t={sl/se:.2f} p={p:.4f}")

# interval likelihood: y observed as rounded integer -> [y-0.5,y+0.5]
def nll(theta):
    a=theta[:3]; s=np.exp(theta[3])
    if np.any(a<0): return 1e9
    mu=X@a
    lo=(y-0.5-mu)/s; hi=(y+0.5-mu)/s
    p=stats.norm.cdf(hi)-stats.norm.cdf(lo)
    p=np.clip(p,1e-300,None)
    return -np.sum(np.log(p))
best=None
for st in [[0.3,0.3,0.3,np.log(1.0)],[0.6,0.0,0.0,0.0],[0.0,0.6,0.0,0.0],[0.0,0.0,0.6,0.0],[0.5,0.4,0.0,0.0]]:
    r=optimize.minimize(nll,st,method="Nelder-Mead",options=dict(maxiter=20000,xatol=1e-8,fatol=1e-10))
    if best is None or r.fun<best.fun: best=r
a=np.clip(best.x[:3],0,None); sig=np.exp(best.x[3]); LLmax=-best.fun
s=a.sum(); w=a/s
print(f"\nFREE FIT (interval lik): a0={a[0]:.4f} a1={a[1]:.4f} a2={a[2]:.4f} scale={s:.4f}")
print(f"  weights w0={w[0]:.4f} w1={w[1]:.4f} w2={w[2]:.4f}  effective lag={w[1]+2*w[2]:.4f} q  sigma={sig:.4f}  LL={LLmax:.4f}")

def restricted_ll(avec):
    f=lambda ls: nll(np.r_[avec,ls[0]])
    r=optimize.minimize(f,[0.0],method="Nelder-Mead",options=dict(maxiter=5000,xatol=1e-9,fatol=1e-11))
    return -r.fun
tests={
 "H0 architect Phi x0.56 (0,.373,.187)":[0.0,2/3*0.56,1/3*0.56],
 "H0b Theo pure lag2 x0.56":[0.0,0.0,0.56],
 "H0c contemporaneous x0.56":[0.56,0.0,0.0],
 "H0d pure lag1 x0.56":[0.0,0.56,0.0],
}
print("\nLR tests vs free fit (df=3):")
for nm,av in tests.items():
    ll=restricted_ll(np.array(av)); lr=2*(LLmax-ll); p=stats.chi2.sf(lr,3)
    print(f"  {nm:42s} LL={ll:9.4f} LR={lr:7.3f} p={p:.4f}")
# free-scale Phi
def phi_scale_ll():
    def f(z):
        sc=z[0]
        if sc<0: return 1e9
        return nll(np.r_[0.0,2/3*sc,1/3*sc,z[1]])
    r=optimize.minimize(f,[0.56,0.0],method="Nelder-Mead",options=dict(maxiter=20000,xatol=1e-9,fatol=1e-11))
    return -r.fun, r.x[0]
ll,sc=phi_scale_ll(); lr=2*(LLmax-ll); print(f"  H0e Phi weights free scale (s={sc:.3f})        LL={ll:9.4f} LR={lr:7.3f} p={stats.chi2.sf(lr,2):.4f}")

# LOO RMSE horse race on point (OLS/NNLS) specs
def loo_rmse(build):
    e=[]
    for i in range(len(y)):
        tr=[j for j in range(len(y)) if j!=i]
        pred=build(tr,i)
        e.append(pred-y[i])
    return float(np.sqrt(np.mean(np.array(e)**2)))
def mk(cols):
    def b(tr,i):
        A=np.column_stack([np.ones(len(tr))]+[X[tr,c] for c in cols])
        beta,*_=np.linalg.lstsq(A,y[tr],rcond=None)
        xv=np.r_[1.0,[X[i,c] for c in cols]]
        return float(xv@beta)
    return b
print("\nLOO RMSE (point, OLS with intercept):")
print(f"  lag0 only          {loo_rmse(mk([0])):.4f}")
print(f"  lag1 only          {loo_rmse(mk([1])):.4f}")
print(f"  lag2 only          {loo_rmse(mk([2])):.4f}")
print(f"  free lags 0,1,2    {loo_rmse(mk([0,1,2])):.4f}")
def phi_b(tr,i):
    z=np.array([2/3*X[j,1]+1/3*X[j,2] for j in tr]); A=np.column_stack([np.ones(len(tr)),z])
    beta,*_=np.linalg.lstsq(A,y[tr],rcond=None)
    return float(beta[0]+beta[1]*(2/3*X[i,1]+1/3*X[i,2]))
print(f"  Phi kernel on basket {loo_rmse(phi_b):.4f}")
print(f"  BASE zero          {float(np.sqrt(np.mean(y**2))):.4f}")
lastv=np.array([tgt[q-1] for q in idx])
print(f"  BASE last value    {float(np.sqrt(np.mean((lastv-y)**2))):.4f}")

# Theo's specific claim: 0.56 * lag-2 basket vs guided ~+3.2pp for 3Q26
print("\nTHEO PROXY CHECK (0.56 x basket, various lags), target quarters:")
for q in [pd.Period('2026Q3',freq='Q'),pd.Period('2026Q4',freq='Q')]:
    print(f"  {q}: 0.56*lag0={0.56*G.get(q,np.nan):.2f}  0.56*lag1={0.56*G[q-1]:.2f}  0.56*lag2={0.56*G[q-2]:.2f}  Phi(2/3 l1+1/3 l2)*0.56={0.56*(2/3*G[q-1]+1/3*G[q-2]):.2f}")
print("\nbasket values: 1Q26=%.3f 2Q26=%.3f 3Q26(QTD to 28Aug)=%.3f"%(G[pd.Period('2026Q1',freq='Q')],G[pd.Period('2026Q2',freq='Q')],G.get(pd.Period('2026Q3',freq='Q'),np.nan)))
