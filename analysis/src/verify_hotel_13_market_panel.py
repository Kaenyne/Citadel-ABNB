"""Check final scoped artifacts and recorded source hashes without refetching."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re
import argparse

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/processed/hotel_13_market_panel'


def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main(raw_root=None):
    raw_root = Path(raw_root) if raw_root is not None else ROOT
    scope=rows(ROOT/'analysis/config/hotel_markets_13.csv')
    table=rows(OUT/'market_coverage.csv')
    request=rows(OUT/'provider_coverage_request_13.csv')
    require(len(scope)==len(table)==len(request)==13, 'Require exactly 13 rows in each scoped table')
    require(len({r['market'] for r in scope})==13, 'Market scope contains duplicates')
    require([r['market'] for r in scope]==[r['market'] for r in table]==[r['market'] for r in request], 'Scope/order mismatch')
    require(all(r['actual_airbnb_hotel_nights']==r['actual_airbnb_hotel_revenue_usd']=='' for r in table), 'Unobserved hotel production must remain missing')
    require(all(r['current_verified_independent_rooms']=='' for r in table), 'Unverified independent-room counts must remain missing')
    pages=rows(OUT/'airbnb_page_observations_scoped.csv')
    ids=rows(OUT/'airbnb_property_clusters_scoped.csv')
    require(len(pages)==len({r['listing_id'] for r in pages})==113, 'Page count/identity mismatch')
    require(len(ids)==len({r['physical_property_key'] for r in ids})==111, 'Property-cluster count/identity mismatch')
    accepted=[r for r in rows(OUT/'airbnb_registry_crosswalk_scoped.csv') if r['accepted_roomcount_link']=='True']
    require(len(accepted)==len({r['airbnb_property_key'] for r in accepted})==len({(r['registry_source_id'],r['registry_id']) for r in accepted})==26, 'Accepted links are not one-to-one or their count changed')
    require(sum(int(r['registered_physical_rooms']) for r in accepted)==1060, 'Registered room total changed')
    require({r['market'] for r in accepted}=={'paris'}, 'Accepted-link market changed')

    pairs=set()
    def visit(obj):
        if isinstance(obj,list):
            for item in obj:visit(item)
        elif isinstance(obj,dict):
            path=obj.get('raw_path',obj.get('local_path',obj.get('path')))
            digest=obj.get('raw_sha256',obj.get('sha256'))
            if isinstance(path,str) and isinstance(digest,str) and len(digest)==64:
                pairs.add((path,digest))
            for item in obj.values():
                if isinstance(item,(dict,list)):visit(item)
    for f in (ROOT/'research/sources').glob('hotel_13_*_sources.json'):
        visit(json.loads(f.read_text(encoding='utf-8-sig')))
    for folder in ['austin','london','us_west_chicago','south_mexico','europe_sydney']:
        for f in (raw_root/'data/raw/hotel_13_market_extension'/folder).glob('*manifest.json'):
            visit(json.loads(f.read_text(encoding='utf-8-sig')))
    for path,digest in pairs:
        artifact=(raw_root if path.replace('\\','/').startswith('data/raw/') else ROOT)/path
        require(artifact.exists(), f'Missing preserved source: {path}')
        require(hashlib.sha256(artifact.read_bytes()).hexdigest()==digest, f'Source checksum changed: {path}')

    link_count=0
    for path in ['research/notes/2026-09-07_hotel-original-13-market-coverage.md',
                 'data/requests/hotel_channel_and_consensus_request.md']:
        f=ROOT/path
        for target in re.findall(r'\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
            if target.startswith(('https://','http://','#')):continue
            require((f.parent/target).resolve().exists(), f'Broken local reference: {target}')
            link_count+=1
    result={'all_checks_passed':True,'market_scope_rows':13,'provider_request_rows':13,
            'page_captures':113,'property_clusters':111,'accepted_room_matches':26,'registered_rooms_matched':1060,
            'recorded_source_path_hash_pairs_verified':len(pairs),'local_links_verified':link_count,
            'missing_booking_revenue_and_current_independent_room_fields_preserved':True,
            'limitation':'Hash checks verify preserved artifacts, not source truth or statistical independence.'}
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-root',type=Path,default=ROOT,help='Checkout containing the preserved data/raw capture bundle')
    main(parser.parse_args().raw_root)
