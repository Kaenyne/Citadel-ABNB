"""Top-down: which macro conditions move Airbnb's operating metrics and its stock?
Quarterly panel 2022Q1-2026Q2 (18 quarters). Run from repo root: python analysis/src/macro_topdown.py
Inputs (data/processed/): macro_us_monthly.csv, us_real_gdp_growth_quarterly.csv, sp500_monthly_close.csv,
  airbnb_quarterly_kpis.csv, airbnb_adr_takerate_quarterly.csv, airbnb_regional_revenue_quarterly.csv, abnb_monthly_close.csv
"""
import csv, numpy as np
from collections import defaultdict
P='data/processed/'
def qtr(m): y,mm=m.split('-')[:2]; return f"{y}Q{(int(mm)-1)//3+1}"
def prevq(q): return f"{int(q[:4])-1}{q[4:]}"
labs=[f"{y}Q{i}" for y in range(2021,2027) for i in range(1,5)]
macro=defaultdict(lambda: defaultdict(list))
for r in csv.DictReader(open(P+'macro_us_monthly.csv')):
    q=qtr(r['month'])
    for k,v in r.items():
        if k in('month','source') or v=='': continue
        macro[q][k].append(float(v))
Q={q:{k:np.mean(v) for k,v in d.items()} for q,d in macro.items()}
def lvl(q,k): return Q[q][k] if q in Q and k in Q[q] else None
def yoy(q,k):
    a,b=lvl(q,k),lvl(prevq(q),k); return (a/b-1)*100 if a and b else None
def chg(q,k):
    a,b=lvl(q,k),lvl(prevq(q),k); return a-b if a is not None and b is not None else None
X={}
for q in labs:
    if q not in Q: continue
    X[q]={'sentiment_lvl':lvl(q,'umcsent'),'sentiment_yoy_pts':chg(q,'umcsent'),'unemp_lvl':lvl(q,'unrate'),'unemp_chg_pts':chg(q,'unrate'),
          'cpi_yoy':yoy(q,'cpi'),'real_dpi_yoy':yoy(q,'real_dpi'),'real_pce_yoy':yoy(q,'real_pce'),'saving_rate':lvl(q,'saving_rate'),
          'fedfunds':lvl(q,'fedfunds'),'gs10':lvl(q,'gs10'),'usd_yoy':yoy(q,'usd_broad'),'eurusd_yoy':yoy(q,'eurusd'),'wti_yoy':yoy(q,'wti'),'wti_lvl':lvl(q,'wti')}
for r in csv.DictReader(open(P+'us_real_gdp_growth_quarterly.csv')):
    X.setdefault(r['quarter'],{})['gdp_saar']=float(r['real_gdp_growth_saar_pct'])
Y=defaultdict(dict)
for r in csv.DictReader(open(P+'airbnb_quarterly_kpis.csv')):
    q=r['quarter']; Y[q]['nights_yoy']=float(r['nights_yoy_pct']); Y[q]['gbv_yoy']=float(r['gbv_yoy_pct_as_reported']); Y[q]['rev_yoy']=float(r['revenue_yoy_pct_as_reported'])
adr={r['quarter']:(float(r['adr_usd']),float(r['take_rate_pct'])) for r in csv.DictReader(open(P+'airbnb_adr_takerate_quarterly.csv'))}
for q,(a,t) in adr.items():
    if prevq(q) in adr: Y[q]['adr_yoy']=(a/adr[prevq(q)][0]-1)*100; Y[q]['take_rate_chg_pts']=t-adr[prevq(q)][1]
reg={r['quarter']:r for r in csv.DictReader(open(P+'airbnb_regional_revenue_quarterly.csv'))}
for q in reg:
    if prevq(q) in reg:
        Y[q]['emea_rev_yoy']=(float(reg[q]['emea_usd_m'])/float(reg[prevq(q)]['emea_usd_m'])-1)*100
        Y[q]['na_rev_yoy']=(float(reg[q]['north_america_usd_m'])/float(reg[prevq(q)]['north_america_usd_m'])-1)*100
px={};sp={}
for r in csv.DictReader(open(P+'abnb_monthly_close.csv')):
    if r['month'][5:] in('03','06','09','12'): px[qtr(r['month'])]=float(r['close_usd'])
for r in csv.DictReader(open(P+'sp500_monthly_close.csv')):
    if r['month'][5:] in('03','06','09','12'): sp[qtr(r['month'])]=float(r['close'])
for a,b in zip(labs[:-1],labs[1:]):
    if a in px and b in px: Y[b]['abnb_ret']=(px[b]/px[a]-1)*100
    if a in sp and b in sp: Y[b]['spx_ret']=(sp[b]/sp[a]-1)*100
for q in list(Y):
    if 'abnb_ret' in Y[q] and 'spx_ret' in Y[q]: Y[q]['abnb_excess_ret']=Y[q]['abnb_ret']-Y[q]['spx_ret']
def corr(fx,fy,keys):
    ks=[k for k in keys if k in X and k in Y and X[k].get(fx) is not None and fy in Y[k]]
    if len(ks)<5: return None,len(ks)
    a=np.array([X[k][fx] for k in ks]); b=np.array([Y[k][fy] for k in ks]); return np.corrcoef(a,b)[0,1],len(ks)
full=[q for q in labs if "2022Q1"<=q<="2026Q2"]; post=[q for q in labs if "2024Q1"<=q<="2026Q2"]
feats=['gdp_saar','real_pce_yoy','real_dpi_yoy','sentiment_lvl','sentiment_yoy_pts','unemp_lvl','unemp_chg_pts','saving_rate','cpi_yoy','fedfunds','gs10','usd_yoy','eurusd_yoy','wti_yoy']
targs=['nights_yoy','gbv_yoy','adr_yoy','rev_yoy','emea_rev_yoy','na_rev_yoy','take_rate_chg_pts','abnb_ret','abnb_excess_ret']
def table(keys,title):
    print(title); print(f"{'feature':18s}"+"".join(f"{t:>14s}" for t in targs))
    for fx in feats:
        row=f"{fx:18s}"
        for fy in targs:
            r,n=corr(fx,fy,keys); row+=f"{('%+.2f'%r) if r is not None else 'n/a':>14s}"
        print(row)
table(full,"Pearson r, same quarter, 2022Q1-2026Q2 (n<=18)"); print(); table(post,"Pearson r, same quarter, 2024Q1-2026Q2 (n<=10)")
def ols(fxs,fy,keys):
    ks=[k for k in keys if k in X and k in Y and all(X[k].get(f) is not None for f in fxs) and fy in Y[k]]
    A=np.column_stack([np.ones(len(ks))]+[[X[k][f] for k in ks] for f in fxs]); b=np.array([Y[k][fy] for k in ks])
    beta=np.linalg.lstsq(A,b,rcond=None)[0]; pred=A@beta; r2=1-((b-pred)**2).sum()/((b-b.mean())**2).sum(); return beta,r2,len(ks)
print()
for fy in ['nights_yoy','gbv_yoy','abnb_excess_ret']:
    beta,r2,n=ols(['real_pce_yoy','sentiment_yoy_pts','usd_yoy'],fy,full)
    print(f"OLS {fy} ~ real_pce_yoy + sentiment_yoy_pts + usd_yoy (n={n}): coefs={np.round(beta,2)} R2={r2:.2f}")
beta,r2,n=ols(['eurusd_yoy'],'emea_rev_yoy',full); print(f"OLS emea_rev_yoy ~ eurusd_yoy (n={n}): intercept={beta[0]:.1f}, slope={beta[1]:.2f} pts per 1% EUR move, R2={r2:.2f}")
beta,r2,n=ols(['usd_yoy'],'gbv_yoy',full); print(f"OLS gbv_yoy ~ usd_yoy (n={n}): intercept={beta[0]:.1f}, slope={beta[1]:.2f}, R2={r2:.2f}")
beta,r2,n=ols(['cpi_yoy'],'adr_yoy',full); print(f"OLS adr_yoy ~ cpi_yoy (n={n}): intercept={beta[0]:.1f}, slope={beta[1]:.2f}, R2={r2:.2f}")
ks=[k for k in full if 'abnb_ret' in Y[k] and 'spx_ret' in Y[k]]
a=np.array([Y[k]['spx_ret'] for k in ks]); b=np.array([Y[k]['abnb_ret'] for k in ks]); bb=np.polyfit(a,b,1)
print(f"ABNB quarterly beta to S&P 500 (n={len(ks)}): beta={bb[0]:.2f}, r={np.corrcoef(a,b)[0,1]:+.2f}")
print("\nPanel: Q | gdp pce_yoy sent unemp cpi_yoy ff usd_yoy eur_yoy wti_yoy | nights gbv adr rev emea tr_chg | abnb_ret spx_ret")
g=lambda v: f"{v:+.1f}" if isinstance(v,(int,float)) else "  -  "
for q in full:
    x=X.get(q,{}); y=Y.get(q,{})
    print(q,'|',g(x.get('gdp_saar')),g(x.get('real_pce_yoy')),g(x.get('sentiment_lvl')),g(x.get('unemp_lvl')),g(x.get('cpi_yoy')),g(x.get('fedfunds')),g(x.get('usd_yoy')),g(x.get('eurusd_yoy')),g(x.get('wti_yoy')),'|',g(y.get('nights_yoy')),g(y.get('gbv_yoy')),g(y.get('adr_yoy')),g(y.get('rev_yoy')),g(y.get('emea_rev_yoy')),g(y.get('take_rate_chg_pts')),'|',g(y.get('abnb_ret')),g(y.get('spx_ret')))
