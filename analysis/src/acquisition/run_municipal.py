"""Federated Socrata discovery + extraction of short-term-rental registry datasets.

Socrata's catalog API federates across all Socrata domains, so one search finds
STR datasets network-wide. Each result carries its OWN domain in metadata.domain,
which is the host that actually serves it.
"""
import csv, datetime, json, os, sys, time, urllib.parse
from pathlib import Path
sys.path.insert(0, os.getcwd())
from processing.acquisition import fetch, integrity

OUT = Path('raw_expansion/v2_2026-09-05/municipal')
LOG = Path('metadata/expansion/municipal_download_log.csv')
COLS = ['acquired_at_utc','domain','dataset_id','dataset_name','rows','bytes','sha256',
        'local_path','http_status','classification','license_tier']
QUERIES = ['short term rental','short-term rental','home sharing','vacation rental',
           'airbnb','transient accommodation','lodging license']
KEEP = ('short','rental','sharing','airbnb','transient','lodging','vacation')

def discover():
    found = {}
    for q in QUERIES:
        url = ('https://api.us.socrata.com/api/catalog/v1?q='
               + urllib.parse.quote(q) + '&only=dataset&limit=100')
        tmp = Path('/tmp/_cat.json')
        r = fetch.get(url, tmp, pace=1.5, timeout=90)
        if r.classification != 'ok':
            print(f'  discovery "{q}" -> {r.status}', flush=True); continue
        try:
            data = json.loads(tmp.read_text())
        except Exception:
            continue
        n = 0
        for res in data.get('results', []):
            rs = res.get('resource', {}); dom = res.get('metadata', {}).get('domain')
            name = rs.get('name') or ''
            if not dom or not rs.get('id'):
                continue
            if not any(k in name.lower() for k in KEEP):
                continue
            found[(dom, rs['id'])] = name; n += 1
        print(f'  "{q}" -> {n} matches (catalog total {len(data.get("results",[]))})', flush=True)
    return found

def main():
    found = discover()
    print(f'\ndiscovered {len(found)} candidate datasets across '
          f'{len({d for d,_ in found})} domains\n', flush=True)
    new = not LOG.exists()
    f = open(LOG, 'a', newline=''); w = csv.DictWriter(f, fieldnames=COLS)
    if new: w.writeheader()
    ok = 0
    for (dom, did), name in sorted(found.items()):
        dest = OUT / dom.replace('.', '_') / f'{did}.csv'
        url = f'https://{dom}/resource/{did}.csv?$limit=200000'
        r = fetch.get(url, dest, pace=2.0, timeout=240)
        row = dict(acquired_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
                   domain=dom, dataset_id=did, dataset_name=name[:90], rows='', bytes=r.bytes,
                   sha256='', local_path=str(dest), http_status=r.status,
                   classification=r.classification, license_tier='open_gov')
        if r.classification == 'ok' and r.bytes > 512:
            with open(dest, newline='', encoding='utf-8', errors='replace') as fh:
                row['rows'] = max(sum(1 for _ in fh) - 1, 0)
            row['sha256'] = integrity.sha256_file(dest); ok += 1
            print(f'  OK  {dom:<30} {str(row["rows"]):>8} rows  {r.bytes/1e6:>6.2f}MB  {name[:44]}', flush=True)
        else:
            dest.unlink(missing_ok=True)
            print(f'  {str(r.status):<4} {dom:<30} {name[:44]}', flush=True)
        w.writerow(row); f.flush()
    f.close()
    print(f'\nDONE municipal datasets acquired: {ok}/{len(found)}', flush=True)

if __name__ == '__main__':
    main()
