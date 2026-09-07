"""Workstream 10. Fetches FRED daily FX series (DEXUSEU, DEXUSUK, DEXBZUS, DEXMXUS, DEXJPUS, DEXUSAL, DEXKOUS, DEXCAUS, DEXINUS)
via the keyless fredgraph.csv endpoint. Writes data/processed/overnight/10_fx_daily.csv (USD per foreign unit, inverted where FRED quotes foreign per USD)
and data/processed/overnight/10_fx_quarterly.csv (quarterly average and y/y % change, quarters 1Q19..3Q26 QTD).
Run: py -3.13 analysis/src/overnight/10_fetch_fx.py
"""
import requests, pandas as pd, io, os
ROOT=os.path.dirname(os.path.abspath(__file__))+'/../../..'
S={'DEXUSEU':('EUR',False),'DEXUSUK':('GBP',False),'DEXBZUS':('BRL',True),'DEXMXUS':('MXN',True),'DEXJPUS':('JPY',True),'DEXUSAL':('AUD',False),'DEXKOUS':('KRW',True),'DEXCAUS':('CAD',True),'DEXINUS':('INR',True)}
frames=[]
for sid,(ccy,invert) in S.items():
    r=requests.get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}',timeout=60)
    d=pd.read_csv(io.StringIO(r.text)); d.columns=['date','v']
    d['v']=pd.to_numeric(d['v'],errors='coerce'); d=d.dropna(); d['date']=pd.to_datetime(d['date'])
    d['usd_per_unit']=1/d['v'] if invert else d['v']
    d['ccy']=ccy; d['fred_id']=sid
    frames.append(d[['date','ccy','fred_id','usd_per_unit']])
    print(sid,ccy,d['date'].max().date(),round(d['usd_per_unit'].iloc[-1],5))
fx=pd.concat(frames); fx=fx[fx.date>='2018-01-01']
fx.to_csv(f'{ROOT}/data/processed/overnight/10_fx_daily.csv',index=False)
fx['quarter']=fx.date.dt.to_period('Q')
q=fx.groupby(['ccy','quarter'])['usd_per_unit'].mean().unstack(0)
yoy=(q/q.shift(4)-1)*100
q.index=[f'{p.quarter}Q{str(p.year)[2:]}' for p in q.index]; yoy.index=q.index
out=pd.concat({'avg':q,'yoy_pct':yoy.round(2)},axis=1)
out.to_csv(f'{ROOT}/data/processed/overnight/10_fx_quarterly.csv')
print(yoy.tail(8).round(1).to_string())
