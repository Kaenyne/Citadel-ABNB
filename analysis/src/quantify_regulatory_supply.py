"""Download public Inside Airbnb snapshots and aggregate listing-level exposure proxies.

Raw data are retained locally; counts are platform listings, not unique dwellings.
Run with --index to inspect discovered source URLs before downloads.
"""
import argparse, concurrent.futures, hashlib, io, json, re
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/regulatory/quantification'
OUT = ROOT / 'research/regulatory/quantification'
MARKETS = ['amsterdam','athens','barcelona','lisbon','madrid','malaga','paris','montreal',
           'new-york-city','florence','budapest','thessaloniki','hawaii','ireland',
           'mallorca','menorca','crete','vancouver','victoria','edinburgh','london',
           'porto','tenerife','gran-canaria']

def urls():
    html = (RAW/'insideairbnb_index.html').read_text(encoding='utf-8')
    return list(dict.fromkeys(re.findall(r'https?[^\s\"<>]+listings\.csv(?:\.gz)?', html)))

def download(url):
    parts = url.split('/')
    market, date = parts[-4], parts[-3]
    p = RAW / f'{market}_{date}_listings.csv'
    if not p.exists():
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        p.write_bytes(r.content)
    df = pd.read_csv(p)
    minimum = pd.to_numeric(df.minimum_nights, errors='coerce')
    reviews = pd.to_numeric(df.number_of_reviews_ltm, errors='coerce') if 'number_of_reviews_ltm' in df else None
    availability = pd.to_numeric(df.availability_365, errors='coerce')
    short = minimum.lt(30)
    home = df.room_type.eq('Entire home/apt')
    row = dict(market=market,snapshot_date=date,source_url=url,total_listings=len(df),
               unique_listing_ids=df.id.nunique(),short_minimum_listings=int(short.sum()),
               entire_home_listings=int(home.sum()),short_entire_home_listings=int((home&short).sum()),
               short_available_listings=int((short&availability.gt(0)).sum()),
               reviewed_ltm_listings=int(reviews.gt(0).sum()) if reviews is not None else None,
               short_reviewed_ltm_listings=int((short&reviews.gt(0)).sum()) if reviews is not None else None,
               sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    groups=[]
    for col in ['neighbourhood_group','neighbourhood']:
        if col not in df: continue
        for name, group in df.groupby(col,dropna=True):
            ix=group.index
            groups.append(dict(market=market,snapshot_date=date,geography_field=col,geography=str(name),
                               total_listings=len(group),short_minimum_listings=int(short.loc[ix].sum()),
                               short_entire_home_listings=int((home.loc[ix]&short.loc[ix]).sum()),source_url=url))
    print(f'{market} {date}: {len(df):,} listings; {int(short.sum()):,} minimum <30 nights',flush=True)
    return row,groups

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--index',action='store_true'); args=ap.parse_args()
    allurls=urls()
    if args.index:
        print('\n'.join(u for u in allurls if any('/'+m+'/' in u for m in MARKETS)))
        return
    OUT.mkdir(parents=True,exist_ok=True)
    selected=[]
    for market in MARKETS:
        available=sorted([u for u in allurls if u.split('/')[-4]==market and u.endswith('/visualisations/listings.csv')],reverse=True)
        if available: selected.append(available[0])
    rows=[]; groups=[]; errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures={ex.submit(download,u):u for u in selected}
        for f in concurrent.futures.as_completed(futures):
            try:
                row,grp=f.result(); rows.append(row); groups.extend(grp)
            except Exception as e:
                errors.append(dict(url=futures[f],error_type=type(e).__name__))
                print('Download failed',futures[f],type(e).__name__,flush=True)
    (OUT/'listing_snapshots.json').write_text(json.dumps(sorted(rows,key=lambda x:x['market']),indent=2),encoding='utf-8')
    (OUT/'neighbourhood_counts.json').write_text(json.dumps(groups,indent=2,ensure_ascii=False),encoding='utf-8')
    (OUT/'download_errors.json').write_text(json.dumps(errors,indent=2),encoding='utf-8')

if __name__=='__main__': main()
