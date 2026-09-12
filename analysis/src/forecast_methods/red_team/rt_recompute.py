"""Red-team independent recomputation of scoreboard cells from registry CSVs.
No harness imports. Pure pandas."""
import pandas as pd, numpy as np, glob, os, json
from pathlib import Path
REPO = Path("/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB")
REG = REPO/"data/processed/forecast_methods/registry"
H = REPO/"data/processed/forecast_methods/harness"
tg = pd.read_csv(H/"targets.csv")
# build actuals long
skip = {"quarter","print_date","guide_date","guide_issued_on","street_pre_guide_vendor",
        "street_pre_guide_as_of","cons_at_print_vendor","has_actual"}
rows=[]
for c in tg.columns:
    if c in skip: continue
    v=pd.to_numeric(tg[c],errors="coerce")
    for q,x,pdte in zip(tg["quarter"],v,tg["print_date"]):
        if pd.notna(x) and pd.notna(pdte):
            rows.append({"quarter":q,"target":c,"actual":float(x)})
act=pd.DataFrame(rows)

frames=[]
for f in sorted(glob.glob(str(REG/"*.csv"))):
    d=pd.read_csv(f); d["__file"]=os.path.basename(f); frames.append(d)
reg=pd.concat(frames,ignore_index=True)
print("registry rows:",len(reg),"files:",reg['__file'].nunique())
d=reg.merge(act,on=["quarter","target"],how="left")
d=d[d["window"].astype(str).str.upper()!="LIVE"].dropna(subset=["actual"]).copy()
nai=d[(d.method=="baselines")&(d.object=="naive")]
nmap={(r.target,r.window,r.prior_basis,r.quarter):float(r.point) for r in nai.itertuples()}

out=[]
for keys,g in d.groupby(["method","object","target","window","prior_basis"],sort=True):
    g=g.sort_values("quarter")
    y=g["actual"].to_numpy(float); p=pd.to_numeric(g["point"],errors="coerce").to_numpy(float)
    e=p-y; n=len(y)
    nd=np.array([nmap.get((keys[2],keys[3],keys[4],q),np.nan) for q in g["quarter"]],float)
    ok=np.isfinite(nd)
    rn=float(np.sqrt(np.mean((nd[ok]-y[ok])**2))) if ok.sum()>=2 else np.nan
    rmse=float(np.sqrt(np.mean(e**2)))
    out.append(dict(method=keys[0],object=keys[1],target=keys[2],window=keys[3],prior_basis=keys[4],
                    n=n,first=g["quarter"].iloc[0],last=g["quarter"].iloc[-1],
                    mae=float(np.mean(np.abs(e))),rmse=rmse,bias=float(np.mean(e)),
                    rmse_naive=rn,ratio=(rmse/rn if np.isfinite(rn) and rn>0 else np.nan)))
rt=pd.DataFrame(out)
rt.to_csv("/private/tmp/claude-501/-Users-theomachado-Library-CloudStorage-OneDrive-UniversityofFlorida-Young--Willem-K--s-files---Citadel---ABNB/81b082fa-72a6-4700-a5b1-850588b2868b/scratchpad/rt_scoreboard.csv",index=False)

sb=pd.read_csv(H/"scoreboard.csv")
m=sb.merge(rt,on=["method","object","target","window","prior_basis"],suffixes=("_sb","_rt"),how="outer",indicator=True)
print("merge status:",m["_merge"].value_counts().to_dict())
m["d_rmse"]=(m["rmse_sb"]-m["rmse_rt"]).abs()
m["d_ratio"]=(m["rmse_ratio_to_naive"]-m["ratio"]).abs()
m["d_n"]=(m["n_sb"]-m["n_rt"]).abs()
bad=m[(m["d_rmse"]>1e-6)|(m["d_ratio"]>1e-6)|(m["d_n"]>0)]
print("MISMATCHES:",len(bad))
pd.set_option('display.width',250)
if len(bad): print(bad[["method","object","target","window","prior_basis","n_sb","n_rt","rmse_sb","rmse_rt","rmse_ratio_to_naive","ratio"]].to_string())
