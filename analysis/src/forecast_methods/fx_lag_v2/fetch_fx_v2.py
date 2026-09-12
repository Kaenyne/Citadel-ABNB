"""fx_lag_v2 / fetch_fx_v2.py  --  COPY of analysis/src/overnight/10_fetch_fx.py.

CHANGES vs the original (and nothing else):
  1. OUTPUT PATH.  The original overwrites data/processed/overnight/10_fx_daily.csv
     and 10_fx_quarterly.csv.  This copy writes ONLY to
         data/processed/forecast_methods/fx_lag_v2/fx_daily_2026-09-11.csv
         data/processed/forecast_methods/fx_lag_v2/fx_quarterly_2026-09-11.csv
     The overnight files are NEVER touched.
  2. BROAD USD.  DTWEXBGS (the broad trade-weighted dollar index) is fetched
     alongside the nine bilaterals, as B4 asks.  It is an INDEX LEVEL, not a
     price of a foreign unit, so it carries ccy='USD_BROAD' and
     unit='index_level_usd_strength'; the nine bilaterals carry
     unit='usd_per_foreign_unit'.  A positive y/y on USD_BROAD is a STRONGER
     dollar (a revenue headwind); a positive y/y on a bilateral is a WEAKER
     dollar (a tailwind).  Downstream code filters on `unit`.
  3. A `fetched_at` stamp and a per-series last-observation table are written so
     the note can state exactly how far the refresh reaches.

Run:
  /Users/theomachado/.venvs/citadel-abnb/bin/python \
      analysis/src/forecast_methods/fx_lag_v2/fetch_fx_v2.py
"""
import datetime as dt
import io
import os

import pandas as pd
import requests

ROOT = os.path.dirname(os.path.abspath(__file__)) + '/../../../..'  # v2 lives one level deeper than the original
OUT = f'{ROOT}/data/processed/forecast_methods/fx_lag_v2'
os.makedirs(OUT, exist_ok=True)
STAMP = '2026-09-11'

S = {'DEXUSEU': ('EUR', False), 'DEXUSUK': ('GBP', False), 'DEXBZUS': ('BRL', True),
     'DEXMXUS': ('MXN', True), 'DEXJPUS': ('JPY', True), 'DEXUSAL': ('AUD', False),
     'DEXKOUS': ('KRW', True), 'DEXCAUS': ('CAD', True), 'DEXINUS': ('INR', True)}
BROAD = 'DTWEXBGS'

frames, meta = [], []
for sid, (ccy, invert) in S.items():
    r = requests.get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}', timeout=60)
    d = pd.read_csv(io.StringIO(r.text)); d.columns = ['date', 'v']
    d['v'] = pd.to_numeric(d['v'], errors='coerce'); d = d.dropna()
    d['date'] = pd.to_datetime(d['date'])
    d['usd_per_unit'] = 1 / d['v'] if invert else d['v']
    d['ccy'] = ccy; d['fred_id'] = sid; d['unit'] = 'usd_per_foreign_unit'
    frames.append(d[['date', 'ccy', 'fred_id', 'usd_per_unit', 'unit']])
    meta.append({'fred_id': sid, 'ccy': ccy, 'unit': 'usd_per_foreign_unit',
                 'last_obs': d['date'].max().date().isoformat(),
                 'last_value': round(float(d['usd_per_unit'].iloc[-1]), 6),
                 'n_obs_since_2018': int((d['date'] >= '2018-01-01').sum())})
    print(sid, ccy, d['date'].max().date(), round(d['usd_per_unit'].iloc[-1], 5))

r = requests.get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={BROAD}', timeout=60)
b = pd.read_csv(io.StringIO(r.text)); b.columns = ['date', 'v']
b['v'] = pd.to_numeric(b['v'], errors='coerce'); b = b.dropna()
b['date'] = pd.to_datetime(b['date'])
b['usd_per_unit'] = b['v']          # index level, NOT a price; see `unit`
b['ccy'] = 'USD_BROAD'; b['fred_id'] = BROAD; b['unit'] = 'index_level_usd_strength'
frames.append(b[['date', 'ccy', 'fred_id', 'usd_per_unit', 'unit']])
meta.append({'fred_id': BROAD, 'ccy': 'USD_BROAD', 'unit': 'index_level_usd_strength',
             'last_obs': b['date'].max().date().isoformat(),
             'last_value': round(float(b['usd_per_unit'].iloc[-1]), 4),
             'n_obs_since_2018': int((b['date'] >= '2018-01-01').sum())})
print(BROAD, 'USD_BROAD', b['date'].max().date(), round(b['usd_per_unit'].iloc[-1], 4))

fx = pd.concat(frames)
fx = fx[fx.date >= '2018-01-01']
fx.to_csv(f'{OUT}/fx_daily_{STAMP}.csv', index=False)

bil = fx[fx['unit'] == 'usd_per_foreign_unit'].copy()
bil['quarter'] = bil.date.dt.to_period('Q')
q = bil.groupby(['ccy', 'quarter'])['usd_per_unit'].mean().unstack(0)
nd = bil.groupby(['ccy', 'quarter'])['usd_per_unit'].size().unstack(0)
brd = fx[fx['unit'] != 'usd_per_foreign_unit'].copy()
brd['quarter'] = brd.date.dt.to_period('Q')
q['USD_BROAD'] = brd.groupby('quarter')['usd_per_unit'].mean()
nd['USD_BROAD'] = brd.groupby('quarter')['usd_per_unit'].size()
yoy = (q / q.shift(4) - 1) * 100
q.index = [f'{p.quarter}Q{str(p.year)[2:]}' for p in q.index]
yoy.index = q.index; nd.index = q.index
out = pd.concat({'avg': q, 'yoy_pct': yoy.round(3), 'n_days': nd}, axis=1)
out.to_csv(f'{OUT}/fx_quarterly_{STAMP}.csv')

m = pd.DataFrame(meta)
m['fetched_at'] = dt.datetime.now().isoformat(timespec='seconds')
m['stamp'] = STAMP
m.to_csv(f'{OUT}/fx_fetch_manifest_{STAMP}.csv', index=False)
print(yoy.tail(8).round(2).to_string())
print('\nlast observation per series:')
print(m[['fred_id', 'ccy', 'last_obs']].to_string(index=False))
