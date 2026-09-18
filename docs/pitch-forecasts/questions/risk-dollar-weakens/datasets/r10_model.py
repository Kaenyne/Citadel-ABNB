"""R10: P(DTWEXBGS on 2027-02-11 <= 0.96 x DTWEXBGS on 2026-09-16).
py -3.13, numpy/pandas/scipy. Reads sources/fred_DTWEXBGS_*.csv (latest) and sources/yfinance_dxy_daily_*.csv.
Writes r10_summary.csv, r10_by_year.csv, r10_regime.csv, r10_sensitivity.csv, r10_tail.csv.
"""
import pandas as pd, numpy as np, glob, csv, os
from scipy.stats import norm, t as student_t
os.chdir(os.path.dirname(os.path.abspath(__file__)))
b=pd.read_csv(sorted(glob.glob('../sources/fred_DTWEXBGS_2026*.csv'))[-1]); b.columns=['date','v']
b.v=pd.to_numeric(b.v,errors='coerce'); b=b.dropna().reset_index(drop=True); b.date=pd.to_datetime(b.date)
x=pd.read_csv(sorted(glob.glob('../sources/yfinance_dxy_daily_2026*.csv'))[-1]); x.columns=['date','dxy']; x.date=pd.to_datetime(x.date)
lv=np.log(b.v.values); dl=np.diff(lv)
H=105; THR=np.log(0.96)          # 106 business days 16 Sep -> 11 Feb, 105 FRED observations net of holidays
# --- spot on 16 Sep (FRED publishes the 14-18 Sep week on 21 Sep): DXY-beta estimate
m=b.merge(x,on='date'); m=m[m.date>='2024-01-01']
lb=np.log(m.v).diff().dropna(); lx=np.log(m.dxy).diff().dropna()
beta=np.cov(lb,lx)[0,1]/lx.var()
dxy11=float(x[x.date=='2026-09-11'].dxy.iloc[0]); dxy16=float(x[x.date=='2026-09-16'].dxy.iloc[0])
s11=float(b.v.iloc[-1]); s16=s11*np.exp(beta*np.log(dxy16/dxy11)); thr_level=0.96*s16
# --- empirical 105-day log changes
r=lv[H:]-lv[:-H]; start=b.date.values[:-H]
df=pd.DataFrame({'start':pd.to_datetime(start),'r':r}); df['yr']=df.start.dt.year
p_all=(r<=THR).mean()
by=df.groupby('yr').r.agg(mean='mean',sd='std',p=lambda s:(s<=THR).mean(),n='count').round(4); by.to_csv('r10_by_year.csv')
p_post2010=(df[df.yr>=2010].r<=THR).mean(); p_post2015=(df[df.yr>=2015].r<=THR).mean()
# --- regime: trailing 252-day realised vol at window start
rv=pd.Series(dl).rolling(252).std().values*np.sqrt(252)
df['rv']=np.r_[np.nan,rv][:len(r)]
cur={'rv63':dl[-63:].std()*np.sqrt(252),'rv126':dl[-126:].std()*np.sqrt(252),'rv252':dl[-252:].std()*np.sqrt(252),'rv_full':dl.std()*np.sqrt(252)}
q=df.dropna().copy(); q['rvq']=pd.qcut(q.rv,5,labels=False)
reg=q.groupby('rvq').agg(rv_lo=('rv','min'),rv_hi=('rv','max'),mean=('r','mean'),sd=('r','std'),p=('r',lambda s:(s<=THR).mean()),n=('r','count')).round(4)
band=q[(q.rv>cur['rv252']-0.01)&(q.rv<cur['rv252']+0.01)]
reg.loc['band_cur_pm1pp']=[band.rv.min(),band.rv.max(),band.r.mean(),band.r.std(),(band.r<=THR).mean(),len(band)]
reg.to_csv('r10_regime.csv')
p_q1=float(reg.loc[0,'p']); p_band=(band.r<=THR).mean()
# momentum band (trailing 12m change near current)
df['mom12']=np.r_[np.full(252,np.nan),lv[252:]-lv[:-252]][:len(r)]
cm=lv[-1]-lv[-253]; mm=df.dropna(subset=['mom12']); sub=mm[(mm.mom12>cm-0.02)&(mm.mom12<cm+0.02)]; p_mom=(sub.r<=THR).mean()
# --- parametric: normal and student-t(4) at current vols, drift 0 and consensus drift
def p_norm(vol,drift=0.0): sd=vol*np.sqrt(H/252); return norm.cdf((THR-drift)/sd)
def p_t(vol,drift=0.0,nu=4): sd=vol*np.sqrt(H/252); scale=sd/np.sqrt(nu/(nu-2)); return student_t.cdf((THR-drift)/scale,nu)
# consensus drift: Reuters poll 2 Sep 2026 EUR/USD 1.16 -> 1.18 at 12m (+1.7%); broad-USD beta to EUR/USD y/y about -0.6 (fx fits) -> broad -1.0%/12m -> -0.42% over 105 days
drift_cons=-0.0042
implied_vol=0.048   # judgement: EUR/USD 6m implied ~7% (training knowledge, no live quote obtainable) x broad/EUR beta ~0.6 + non-EUR legs ~ 4.5-5.0%
rows=[('empirical_all_2006_2026',p_all),('empirical_2010plus',p_post2010),('empirical_2015plus',p_post2015),
      ('regime_vol_quintile1',p_q1),('regime_vol_band_pm1pp',p_band),('momentum_band_12m',p_mom),
      ('normal_rv252_zero_drift',p_norm(cur['rv252'])),('normal_rv252_cons_drift',p_norm(cur['rv252'],drift_cons)),
      ('normal_rv63_zero_drift',p_norm(cur['rv63'])),('normal_fullsample_vol',p_norm(cur['rv_full'])),
      ('t4_rv252_zero_drift',p_t(cur['rv252'])),('t4_rv252_cons_drift',p_t(cur['rv252'],drift_cons)),
      ('normal_implied_4.8_zero_drift',p_norm(implied_vol)),('normal_implied_4.8_cons_drift',p_norm(implied_vol,drift_cons)),
      ('t4_implied_4.8_cons_drift',p_t(implied_vol,drift_cons))]
# tail moments: E[move | <= -4.08%]
tail=r[r<=THR]; e_tail=tail.mean(); 
with open('r10_tail.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['item','value'])
    w.writerow(['E_logchange_given_yes_empirical',round(e_tail,4)]); w.writerow(['median_given_yes',round(np.median(tail),4)])
    w.writerow(['p10_given_yes',round(np.percentile(tail,10),4)]); w.writerow(['n_tail_windows',len(tail)])
    w.writerow(['kurtosis_105d_changes',round(pd.Series(r).kurt(),3)]); w.writerow(['skew',round(pd.Series(r).skew(),3)])
with open('r10_summary.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['item','value'])
    for k,v in [('spot_11sep',s11),('beta_broad_on_dxy',beta),('dxy_11sep',dxy11),('dxy_16sep',dxy16),('spot_16sep_est',s16),('threshold_level',thr_level),
                ('threshold_log',THR),('horizon_obs',H),('n_windows',len(r)),('mean_105d',r.mean()),('sd_105d',r.std()),
                ('rv63',cur['rv63']),('rv126',cur['rv126']),('rv252',cur['rv252']),('rv_full',cur['rv_full']),('mom12_log',cm),('drift_cons_105d',drift_cons)]:
        w.writerow([k,round(float(v),5)])
    for k,v in rows: w.writerow(['P_'+k,round(float(v),4)])
# sensitivity grid
with open('r10_sensitivity.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['vol_ann','drift_105d','dist','p'])
    for vol in [0.035,0.040,0.042,0.045,0.048,0.054,0.060]:
        for dr in [-0.015,-0.008,-0.0042,0.0,0.005,0.01]:
            w.writerow([vol,dr,'normal',round(p_norm(vol,dr),4)]); w.writerow([vol,dr,'t4',round(p_t(vol,dr),4)])
    # spot uncertainty: if the true 16 Sep value is +/-0.4% from the estimate the threshold moves but the spot at forecast time is the same point -> no change to P except via realised path; report the level
    for s in [s16*0.996,s16,s16*1.004]: w.writerow(['spot16',round(s,2),'threshold',round(0.96*s,2)])
print(open('r10_summary.csv').read())
