"""Priority-ordered Inside Airbnb acquisition to external SSD."""
import csv, datetime, os, shutil, sys
from pathlib import Path
sys.path.insert(0, os.getcwd())
from processing.acquisition import fetch, integrity
from processing.acquisition.sources import inside_airbnb as ia

SSD = Path('/Volumes/PortableSSD/ABNB_DATA_EXPANSION/raw_expansion/v2_2026-09-05/inside_airbnb_current')
INV = Path('metadata/expansion/inside_airbnb_download_log.csv')
COLS = ['acquired_at_utc','country','region','city','snapshot_date','kind','http_status',
        'classification','bytes','row_count','sha256','local_path','url','license_tier']
MIN_FREE_GB = 5

def free_gb(p):
    s = shutil.disk_usage(p)
    return s.free / 1e9

def priority(s, held_cities):
    if s.country == 'united-states' and s.kind == 'listings': return 0
    if s.country == 'united-states': return 1
    if (s.country, s.region, s.city) in held_cities and s.kind == 'calendar': return 2
    if (s.country, s.region, s.city) in held_cities and s.kind == 'reviews': return 3
    if s.kind == 'listings': return 4
    return 5

def main():
    html = Path('raw_expansion/v2_2026-09-05/inside_airbnb_catalog/get_the_data_current.html')\
        .read_text(encoding='utf-8', errors='replace')
    snaps = ia.parse_index(html)
    held, held_cities = set(), set()
    for root, _, fs in os.walk('raw/inside_airbnb'):
        if 'listings.csv.gz' in fs:
            q = root.split(os.sep)
            held.add((q[2], q[3], q[4], q[5], 'listings')); held_cities.add((q[2], q[3], q[4]))
    todo = sorted(ia.plan_downloads(snaps, held), key=lambda s: (priority(s, held_cities), s.country, s.city, s.kind))
    print(f'queued {len(todo)} files; free {free_gb(SSD.parent):.1f} GB', flush=True)

    done = set()
    if INV.exists():
        for r in csv.DictReader(open(INV)):
            done.add((r['country'], r['region'], r['city'], r['snapshot_date'], r['kind']))
    new = not INV.exists()
    f = open(INV, 'a', newline=''); w = csv.DictWriter(f, fieldnames=COLS)
    if new: w.writeheader()

    ok = skipped = restricted = failed = 0
    for i, s in enumerate(todo, 1):
        key = (s.country, s.region, s.city, s.date, s.kind)
        if key in done:
            skipped += 1; continue
        if free_gb(SSD.parent) < MIN_FREE_GB:
            print(f'ABORT: free space {free_gb(SSD.parent):.1f} GB < {MIN_FREE_GB}', flush=True); break
        dest = SSD / s.country / s.region / s.city / s.date / f'{s.kind}.csv.gz'
        r = fetch.get(s.url, dest, pace=5.0)
        row = dict(acquired_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
                   country=s.country, region=s.region, city=s.city, snapshot_date=s.date, kind=s.kind,
                   http_status=r.status, classification=r.classification, bytes=r.bytes,
                   row_count='', sha256='', local_path=str(dest), url=s.url, license_tier='cc_by_4_0')
        if r.classification == 'ok':
            v = integrity.validate(dest)
            if not v.ok:
                dest.unlink(missing_ok=True)
                row['classification'] = 'rejected-' + v.detail[:40]; failed += 1
            else:
                row['row_count'] = v.row_count or ''
                row['sha256'] = integrity.sha256_file(dest); ok += 1
        elif r.classification == 'source-restriction':
            restricted += 1
        else:
            failed += 1
        w.writerow(row); f.flush()
        if i % 5 == 0 or r.classification != 'ok':
            print(f'[{i}/{len(todo)}] {s.country}/{s.city}/{s.kind} -> {r.status} '
                  f'{r.bytes/1e6:.1f}MB | ok={ok} restr={restricted} fail={failed} '
                  f'free={free_gb(SSD.parent):.0f}GB', flush=True)
    f.close()
    print(f'DONE ok={ok} skipped={skipped} restricted={restricted} failed={failed}', flush=True)

if __name__ == '__main__':
    main()
