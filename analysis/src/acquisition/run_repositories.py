"""Discover + download Airbnb datasets from Zenodo, Figshare, Harvard Dataverse."""
import csv, datetime, json, os, sys, urllib.parse
from pathlib import Path
sys.path.insert(0, os.getcwd())
from processing.acquisition import fetch, integrity

BASE = Path('raw_expansion/v2_2026-09-05')
LOG  = Path('metadata/expansion/repositories_log.csv')
COLS = ['acquired_at_utc','repo','record_id','title','file_name','bytes','sha256',
        'local_path','http_status','classification','license','landing_url','license_tier']
MAX_FILE = 2_000_000_000      # 2 GB per file ceiling
QUERIES  = ['airbnb', 'short-term rental listings', 'inside airbnb']
OK_EXT   = ('.csv', '.csv.gz', '.zip', '.json', '.jsonl', '.tsv', '.parquet', '.xlsx', '.gz')

def jget(url, tmp, pace=1.5):
    r = fetch.get(url, tmp, pace=pace, timeout=120)
    if r.classification != 'ok': return None, r
    try: return json.loads(tmp.read_text(encoding='utf-8', errors='replace')), r
    except Exception: return None, r

def main():
    new = not LOG.exists()
    lf = open(LOG, 'a', newline=''); w = csv.DictWriter(lf, fieldnames=COLS); 
    if new: w.writeheader()
    tmp = Path('/tmp/_repo.json'); ok = 0

    def record(repo, rid, title, fname, res, dest, lic, land):
        nonlocal ok
        row = dict(acquired_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
                   repo=repo, record_id=str(rid), title=str(title)[:110], file_name=fname,
                   bytes=res.bytes, sha256='', local_path=str(dest), http_status=res.status,
                   classification=res.classification, license=str(lic)[:60], landing_url=land,
                   license_tier='open_repo')
        if res.classification == 'ok' and res.bytes > 512:
            v = integrity.validate(dest)
            if v.ok:
                row['sha256'] = integrity.sha256_file(dest); ok += 1
                print(f'  OK  {repo:<10} {res.bytes/1e6:>8.2f}MB  {fname[:38]:<38} {str(title)[:40]}', flush=True)
            else:
                dest.unlink(missing_ok=True); row['classification'] = 'rejected-' + v.detail[:34]
                print(f'  --  {repo:<10} rejected {fname[:38]}', flush=True)
        else:
            print(f'  {str(res.status):<4}{repo:<10} {fname[:38]}', flush=True)
        w.writerow(row); lf.flush()

    # ---------- ZENODO ----------
    for q in QUERIES:
        url = f'https://zenodo.org/api/records?q={urllib.parse.quote(q)}&size=25&type=dataset'
        d, r = jget(url, tmp)
        if not d: print(f'  zenodo query "{q}" -> {r.status}', flush=True); continue
        hits = d.get('hits', {}).get('hits', [])
        print(f'  zenodo "{q}" -> {len(hits)} records', flush=True)
        for rec in hits:
            title = rec.get('metadata', {}).get('title', '')
            if 'airbnb' not in (title + json.dumps(rec.get('metadata', {}).get('keywords', []))).lower():
                continue
            lic = rec.get('metadata', {}).get('license', {}).get('id', '')
            for fl in rec.get('files', [])[:4]:
                fn = fl.get('key', '')
                if not fn.lower().endswith(OK_EXT): continue
                if fl.get('size', 0) > MAX_FILE: 
                    print(f'  SKIP zenodo {fn} {fl["size"]/1e9:.1f}GB > ceiling', flush=True); continue
                link = fl.get('links', {}).get('self')
                if not link: continue
                dest = BASE / 'zenodo' / str(rec['id']) / fn
                record('zenodo', rec['id'], title, fn, fetch.get(link, dest, pace=2.0, timeout=600),
                       dest, lic, rec.get('links', {}).get('self_html', ''))

    # ---------- FIGSHARE ----------
    for q in QUERIES:
        url = f'https://api.figshare.com/v2/articles?search_for={urllib.parse.quote(q)}&page_size=25'
        d, r = jget(url, tmp)
        if not d: print(f'  figshare query "{q}" -> {r.status}', flush=True); continue
        print(f'  figshare "{q}" -> {len(d)} records', flush=True)
        for art in d[:12]:
            title = art.get('title', '')
            if 'airbnb' not in title.lower(): continue
            det, _ = jget(f"https://api.figshare.com/v2/articles/{art['id']}", tmp, pace=1.0)
            if not det: continue
            lic = det.get('license', {}).get('name', '')
            for fl in det.get('files', [])[:4]:
                fn = fl.get('name', '')
                if not fn.lower().endswith(OK_EXT): continue
                if fl.get('size', 0) > MAX_FILE: continue
                dest = BASE / 'figshare' / str(art['id']) / fn
                record('figshare', art['id'], title, fn,
                       fetch.get(fl['download_url'], dest, pace=2.0, timeout=600), dest, lic,
                       det.get('figshare_url', ''))

    # ---------- HARVARD DATAVERSE ----------
    tok = os.environ.get('DATAVERSE_API_TOKEN', '')
    for q in QUERIES:
        url = (f'https://dataverse.harvard.edu/api/search?q={urllib.parse.quote(q)}'
               f'&type=dataset&per_page=25')
        d, r = jget(url, tmp)
        if not d: print(f'  dataverse query "{q}" -> {r.status}', flush=True); continue
        items = d.get('data', {}).get('items', [])
        print(f'  dataverse "{q}" -> {len(items)} records', flush=True)
        for it in items[:10]:
            if 'airbnb' not in (it.get('name', '') + it.get('description', '')).lower(): continue
            gid = it.get('global_id', '')
            if not gid: continue
            durl = f'https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId={gid}'
            if tok: durl += f'&key={tok}'
            dd, _ = jget(durl, tmp, pace=1.5)
            if not dd: continue
            files = dd.get('data', {}).get('latestVersion', {}).get('files', [])
            lic = dd.get('data', {}).get('latestVersion', {}).get('license', {})
            lic = lic.get('name', '') if isinstance(lic, dict) else str(lic)
            for fmeta in files[:4]:
                df = fmeta.get('dataFile', {}); fn = df.get('filename', '')
                if not fn.lower().endswith(OK_EXT): continue
                if df.get('filesize', 0) > MAX_FILE:
                    print(f'  SKIP dataverse {fn} {df["filesize"]/1e9:.1f}GB > ceiling', flush=True); continue
                fu = f'https://dataverse.harvard.edu/api/access/datafile/{df.get("id")}'
                if tok: fu += f'?key={tok}'
                dest = BASE / 'harvard_dataverse' / gid.replace('/', '_').replace(':', '') / fn
                record('dataverse', gid, it.get('name', ''), fn,
                       fetch.get(fu, dest, pace=2.0, timeout=900), dest, lic, it.get('url', ''))

    lf.close(); print(f'\nDONE repository files acquired: {ok}', flush=True)

if __name__ == '__main__':
    main()
