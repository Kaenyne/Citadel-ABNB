"""Record reviewed team evidence without reacquiring existing hotel datasets."""
import concurrent.futures
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile
import argparse

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/processed/hotel_funnel_audit'
RAW = ROOT / 'data/raw/hotel_funnel_audit/team_review'
GH = Path.home() / 'AppData/Local/Programs/GitHub CLI/bin/gh.exe'
REPO = 'Kaenyne/Citadel-ABNB'

def api(path):
    return subprocess.check_output([str(GH), 'api', f'repos/{REPO}/{path}'])


def refresh_sources(urls):
    from urllib.parse import urlsplit
    def normalize(url):
        u=urlsplit(url)
        return (u.netloc.lower().removeprefix('www.'),u.path.rstrip('/').lower(),u.query)
    rows=[]
    for source in json.loads((ROOT/'research/sources/hotel_funnel_audit.json').read_text(encoding='utf-8')):
        hits=[r for r in urls if normalize(r['url'])==normalize(source['url'])]
        rows.append({**source,'exact_prior_url_matches':len(hits),
            'prior_locations':' | '.join(sorted({r['location'] for r in hits}))})
    with (OUT/'public_source_overlap.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'Compared {len(rows)} sources with {len(urls)} prior URL references')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources-only',action='store_true',help='Compare updated source ledger against the existing frozen team review')
    args=parser.parse_args()
    if args.sources_only:
        with (OUT/'team_review_urls.csv').open(encoding='utf-8',newline='') as f:
            refresh_sources(list(csv.DictReader(f)))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    tree = json.loads(api('git/trees/main?recursive=1'))
    rev = tree['sha']
    paths = [x['path'] for x in tree['tree'] if x['type'] == 'blob' and
             ((x['path'].startswith('research/notes/') and x['path'].endswith('.md')) or
              x['path'] == 'research/sources/README.md' or
              (x['path'].startswith('data/processed/') and x['path'].endswith('.csv') and
               any(t in x['path'] for t in ['hotel','market','city','sizing'])))]
    documents = []
    def fetch(path):
        payload = api(f'contents/{path}?ref={rev}')
        import base64
        obj = json.loads(payload)
        raw = base64.b64decode(obj['content'])
        target = RAW / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return ('github', f'https://github.com/{REPO}/blob/{rev}/{path}', raw)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        documents.extend(pool.map(fetch, paths))
    for zpath in sorted(ROOT.glob('*.zip')):
        with zipfile.ZipFile(zpath) as z:
            for entry in z.infolist():
                if entry.filename.endswith(('.md','.csv','.json','.txt')) and entry.file_size < 2_000_000:
                    documents.append(('local_zip', zpath.name+'::'+entry.filename, z.read(entry)))
    # Search existing local notes and imported source registries as well.
    for folder in ['research', 'citadel-abnb-files 2/research', 'theos-past-research/research']:
        for path in sorted((ROOT/folder).rglob('*')):
            if path.is_file() and path.suffix in ['.md','.csv'] and path.stat().st_size < 2_000_000:
                if 'hotel-funnel-audit' not in path.name:
                    documents.append(('local', path.relative_to(ROOT).as_posix(), path.read_bytes()))
    register=[]; urls=[]; matches=[]
    for origin, location, raw in documents:
        text=raw.decode('utf-8-sig',errors='replace')
        register.append(dict(origin=origin,location=location,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
        for url in sorted(set(re.findall(r'https?://[^\s<>"\]|]+',text))):
            urls.append(dict(origin=origin,location=location,url=url.rstrip(').,;')))
        if re.search(r'25[ -]markets?|twenty.five',text,re.I):
            matches.append(location)
    for name,rows in [('team_review_manifest',register),('team_review_urls',urls)]:
        with (OUT/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    hashes={r['sha256'] for r in register}
    metadata=dict(as_of='2026-09-07',main_commit=rev,github_files=len(paths),
        reviewed_documents=len(register),unique_content_hashes=len(hashes),
        duplicate_content_instances=len(register)-len(hashes),named_25_market_matches=matches,
        limit='Reviewed visible main notes/source ledger/selected processed tables and local research/ZIP drops. Does not certify unshared work or every open branch.')
    (OUT/'overlap_review_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    refresh_sources(urls)
    print(json.dumps(metadata,indent=2))

if __name__ == '__main__': main()
