"""adr_engine / fetch_fx.py -- FRED H.10 refresh for the ADR engine. A COPY of
analysis/src/forecast_methods/fx_lag_v2/fetch_fx_v2.py with ONLY the output path changed
(writes to data/processed/pitch_model_v2/adr_engine/, never to any fx_lag or overnight file)
and the stamp taken from the run date. Nine bilaterals as USD per foreign unit plus the broad
dollar index (an index level, unit='index_level_usd_strength'). No API key is needed.

Run:  python3 analysis/src/pitch_model_v2/adr_engine/fetch_fx.py
"""
import datetime as dt
import io
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/pitch_model_v2/adr_engine"
OUT.mkdir(parents=True, exist_ok=True)
STAMP = dt.date.today().isoformat()

S = {'DEXUSEU': ('EUR', False), 'DEXUSUK': ('GBP', False), 'DEXBZUS': ('BRL', True),
     'DEXMXUS': ('MXN', True), 'DEXJPUS': ('JPY', True), 'DEXUSAL': ('AUD', False),
     'DEXKOUS': ('KRW', True), 'DEXCAUS': ('CAD', True), 'DEXINUS': ('INR', True)}
BROAD = 'DTWEXBGS'


def main():
    frames, meta = [], []
    for sid, (ccy, invert) in S.items():
        r = requests.get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}', timeout=60)
        r.raise_for_status()
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
    r.raise_for_status()
    b = pd.read_csv(io.StringIO(r.text)); b.columns = ['date', 'v']
    b['v'] = pd.to_numeric(b['v'], errors='coerce'); b = b.dropna()
    b['date'] = pd.to_datetime(b['date'])
    b['usd_per_unit'] = b['v']
    b['ccy'] = 'USD_BROAD'; b['fred_id'] = BROAD; b['unit'] = 'index_level_usd_strength'
    frames.append(b[['date', 'ccy', 'fred_id', 'usd_per_unit', 'unit']])
    meta.append({'fred_id': BROAD, 'ccy': 'USD_BROAD', 'unit': 'index_level_usd_strength',
                 'last_obs': b['date'].max().date().isoformat(),
                 'last_value': round(float(b['usd_per_unit'].iloc[-1]), 4),
                 'n_obs_since_2018': int((b['date'] >= '2018-01-01').sum())})
    fx = pd.concat(frames); fx = fx[fx.date >= '2015-01-01']
    fx.to_csv(OUT / f'fx_daily_{STAMP}.csv', index=False)
    m = pd.DataFrame(meta); m['fetched_at'] = dt.datetime.now().isoformat(timespec='seconds')
    m.to_csv(OUT / f'fx_fetch_manifest_{STAMP}.csv', index=False)
    print(m.to_string(index=False))
    print('wrote', OUT / f'fx_daily_{STAMP}.csv')


if __name__ == '__main__':
    main()
