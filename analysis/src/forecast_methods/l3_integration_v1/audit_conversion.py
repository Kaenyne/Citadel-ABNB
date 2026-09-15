"""Independent direct five-parameter nonlinear LS check of profiled conversion fit."""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[4]

def direct_fit(d):
    y=d.revenue_musd.to_numpy();g1=d.gbv_l1.to_numpy();g2=d.gbv_l2.to_numpy();s=d.season.to_numpy()-1
    def residual(p):return (p[1:][s]*(p[0]*g1+(1-p[0])*g2)-y)
    fits=[least_squares(residual,[w,.13,.14,.17,.12],bounds=([0,0,0,0,0],[1,1,1,1,1]),
                        ftol=1e-13,xtol=1e-13,gtol=1e-10,max_nfev=2000,x_scale='jac') for w in [.05,.25,.5,.75,.95]]
    best=min(fits,key=lambda f:np.square(f.fun).sum())
    return {'n':len(d),'w':best.x[0],**{'lambda_Q'+str(i):best.x[i] for i in range(1,5)},
            'sse':np.square(best.fun).sum(),'optimizer_starts':5,
            'max_start_sse_gap':max(np.square(f.fun).sum() for f in fits)-np.square(best.fun).sum()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    d=pd.read_csv(ROOT/'data/processed/overnight/02_kpi_panel_quarterly.csv')
    d['quarter']=d.quarter.map(lambda q:'20'+q[2:]+'Q'+q[0])
    d=d.sort_values('quarter');d['gbv_l1']=d.gbv_musd.shift(1);d['gbv_l2']=d.gbv_musd.shift(2)
    d['season']=d.quarter.str[-1].astype(int);d=d.dropna(subset=['gbv_l1','gbv_l2','revenue_musd'])
    assert len(d)==22 and d.quarter.iloc[0]=='2021Q1' and d.quarter.iloc[-1]=='2026Q2'
    result={'method':'Independent direct five-parameter least_squares, five starts; author uses scalar profile.',
            'full22':direct_fit(d),'exclude2021':direct_fit(d[d.quarter.ge('2022Q1')]),
            'since2023':direct_fit(d[d.quarter.ge('2023Q1')])}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
