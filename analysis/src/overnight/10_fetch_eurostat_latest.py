"""Workstream 10. Re-pulls Eurostat tour_ce_omr (platform short-stay nights, monthly, NGT_SP, NR) fresh from the API
(no cache) to extend the monthly EU27/country series past Mar 2026 (the cached data/raw/eurostat pull ends Mar 2026).
Writes data/processed/overnight/10_eurostat_platform_monthly_latest.csv (EU27 total/domestic/foreign + country totals, y/y).
Run: py -3.13 analysis/src/overnight/10_fetch_eurostat_latest.py
"""
import requests, json, os, numpy as np, pandas as pd
ROOT=os.path.dirname(os.path.abspath(__file__))+'/../../..'
UA={'User-Agent':'citadel-abnb research ksurapaneni@ufl.edu'}
URL='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_ce_omr'
r=requests.get(URL,params={'format':'JSON','lang':'EN','indic_to':'NGT_SP','unit':'NR','sinceTimePeriod':'2023-01'},headers=UA,timeout=300)
r.raise_for_status(); j=r.json()
def jsonstat_to_frame(j):
    dims,sizes=j['id'],j['size']
    cats={d:list(j['dimension'][d]['category']['index'].keys()) for d in dims}
    strides=[int(np.prod(sizes[i+1:])) if i+1<len(sizes) else 1 for i in range(len(sizes))]
    rows=[]
    for key,v in j['value'].items():
        k=int(key); idx=[]
        for s in strides: idx.append(k//s); k%=s
        rec={d:cats[d][ix] for d,ix in zip(dims,idx)}; rec['value']=v; rows.append(rec)
    return pd.DataFrame(rows)
d=jsonstat_to_frame(j)
print(d.columns.tolist(), d.time.max() if 'time' in d else None)
d=d[d.month!='TOTAL'].copy(); d['date']=pd.to_datetime(d.time+'-'+d.month.str[1:]+'-01')
tot=d[d.c_resid=='TOTAL'].pivot_table(index='date',columns='geo',values='value').sort_index()
resid=d[d.geo=='EU27_2020'].pivot_table(index='date',columns='c_resid',values='value').sort_index()
m=pd.DataFrame({'eu27_nights':tot['EU27_2020'],'eu27_domestic':resid.get('DOM'),'eu27_foreign':resid.get('FOR')})
for c in tot.columns:
    if c!='EU27_2020': m[f'{c}_nights']=tot[c]
for c in list(m.columns):
    m[c+'_yoy_pct']=((m[c]/m[c].shift(12)-1)*100).round(2)
m.index.name='month'
m.to_csv(f'{ROOT}/data/processed/overnight/10_eurostat_platform_monthly_latest.csv')
print('last month with EU27 total:', m.eu27_nights.dropna().index.max().date())
print(m[['eu27_nights','eu27_nights_yoy_pct','eu27_domestic_yoy_pct','eu27_foreign_yoy_pct']].tail(10).to_string())
