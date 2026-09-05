"""FRED macro series + TSA throughput acquisition."""
import csv, datetime, os, sys
from pathlib import Path
sys.path.insert(0, os.getcwd())
from processing.acquisition import fetch, integrity

OUT = Path('raw_expansion/v2_2026-09-05/macro')
LOG = Path('metadata/expansion/macro_download_log.csv')
COLS = ['acquired_at_utc','source','series_id','title','obs','bytes','sha256',
        'local_path','http_status','classification','license_tier']

FRED = [
    ('CUSR0000SEHB','CPI: Lodging away from home (ADR proxy)'),
    ('CUUR0000SEHB','CPI: Lodging away from home, NSA'),
    ('USLAH','All employees: Leisure and hospitality'),
    ('UMCSENT','Consumer sentiment'),
    ('PCEC96','Real personal consumption expenditures'),
    ('DSPIC96','Real disposable personal income'),
    ('CUSR0000SETA01','CPI: New vehicles (discretionary control)'),
    ('AIRRPMTSID11','Air revenue passenger miles'),
    ('TRFVOLUSM227NFWA','Vehicle miles travelled'),
    ('DTWEXBGS','Trade-weighted USD index (FX exposure)'),
]

def main():
    key = os.environ.get('FRED_API_KEY')
    if not key:
        print('FATAL: FRED_API_KEY not set; source .secrets/env.sh', flush=True); return
    new = not LOG.exists()
    f = open(LOG,'a',newline=''); w = csv.DictWriter(f, fieldnames=COLS)
    if new: w.writeheader()
    ok = 0
    for sid, title in FRED:
        dest = OUT / 'fred' / f'{sid}.json'
        url = (f'https://api.stlouisfed.org/fred/series/observations?series_id={sid}'
               f'&api_key={key}&file_type=json')
        r = fetch.get(url, dest, pace=1.0, timeout=120)
        row = dict(acquired_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
                   source='FRED', series_id=sid, title=title, obs='', bytes=r.bytes, sha256='',
                   local_path=str(dest), http_status=r.status, classification=r.classification,
                   license_tier='public_domain')
        if r.classification == 'ok' and integrity.validate(dest).ok:
            import json
            try:
                n = len(json.loads(dest.read_text()).get('observations', []))
            except Exception:
                n = ''
            row['obs'] = n; row['sha256'] = integrity.sha256_file(dest); ok += 1
            print(f'  OK  {sid:<18} {n:>6} obs  {title[:46]}', flush=True)
        else:
            print(f'  {r.status}  {sid}  {r.classification}', flush=True)
        w.writerow(row); f.flush()

    # TSA passenger throughput page
    dest = OUT / 'tsa' / 'passenger_volumes.html'
    r = fetch.get('https://www.tsa.gov/travel/passenger-volumes', dest, pace=2.0, timeout=120)
    row = dict(acquired_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
               source='TSA', series_id='passenger_volumes', title='TSA checkpoint throughput',
               obs='', bytes=r.bytes, sha256=integrity.sha256_file(dest) if r.classification=='ok' else '',
               local_path=str(dest), http_status=r.status, classification=r.classification,
               license_tier='public_domain')
    w.writerow(row); f.flush(); f.close()
    print(f'  TSA -> {r.status} {r.bytes/1024:.0f}KB', flush=True)
    print(f'DONE macro series acquired: {ok} FRED + TSA', flush=True)

if __name__ == '__main__':
    main()
