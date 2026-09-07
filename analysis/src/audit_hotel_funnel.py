"""Audit hotel-tagged Airbnb listings using existing verified team captures.

No new acquisition and no claim that listings are properties or reviews are nights.
Run from repo root: .venv/Scripts/python.exe analysis/src/audit_hotel_funnel.py
"""
from __future__ import annotations
import csv
import argparse
from collections import defaultdict, Counter
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
from research_integrity import atomic_write_csv, observed_count

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/processed/hotel_funnel_audit'
REVIEW_FIELDS = ('number_of_reviews_ltm', 'number_of_reviews_l30d')
REVIEW_GROUPS = ('baseline', 'endpoint', 'retained_baseline', 'retained', 'new_to_panel')

def ratio(n, d):
    return n / d if n is not None and d is not None and d != 0 else None


def growth_rate(endpoint, baseline):
    relative = ratio(endpoint, baseline)
    return relative - 1 if relative is not None else None


def complete_sum(values):
    """An empty population totals zero; an unobserved member makes its total unknown."""
    values = list(values)
    return sum(values) if all(v is not None for v in values) else None

def count(r, key):
    return observed_count(r.get(key, ''), key)

def is_hotel(r, scope='strict'):
    p = r.get('property_type', '').lower()
    if scope == 'boutique':
        return p == 'boutique hotel' or p.endswith(' in boutique hotel')
    tagged = p == 'hotel' or p == 'boutique hotel' or p.endswith(' in hotel') or p.endswith(' in boutique hotel')
    if scope == 'strict':
        return tagged
    if scope == 'broad':
        return tagged or r.get('room_type') == 'Hotel room'
    raise ValueError(scope)

def read_capture(meta):
    path = ROOT / meta['local_path']
    with path.open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != meta['sha256']:
            raise ValueError(f'Hash mismatch: {path}')
    result = {}
    keep = ['id', 'host_id', 'property_type', 'room_type', 'number_of_reviews',
            'number_of_reviews_ltm', 'number_of_reviews_l30d', 'first_review',
            'minimum_nights', 'availability_30', 'last_scraped']
    with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not set(keep).issubset(reader.fieldnames):
            raise ValueError(f'Missing fields: {path}')
        for r in reader:
            if r['id'] in result:
                raise ValueError('Duplicate ID')
            result[r['id']] = {k:r[k] for k in keep}
    if len(result) != int(meta['expected_rows']):
        raise ValueError('Row count differs from team manifest')
    return result

def aggregate(rows):
    rows = list(rows)
    out = dict(listings=len(rows), unique_host_ids=len({r['host_id'] for r in rows}),
               boutique_tagged=sum('boutique hotel' in r['property_type'].lower() for r in rows),
               min_nights_le2=sum((count(r,'minimum_nights') or 999) <= 2 for r in rows))
    for field in REVIEW_FIELDS:
        vals = [count(r,field) for r in rows]
        out[field] = complete_sum(vals)
        out[field+'_observed_sum'] = sum(v for v in vals if v is not None)
        out[field+'_missing'] = sum(v is None for v in vals)
        out[field+'_positive'] = sum(v is not None and v > 0 for v in vals)
    return out

def compare(a, b, start, scope):
    ah = {k:r for k,r in a.items() if is_hotel(r,scope)}
    bh = {k:r for k,r in b.items() if is_hotel(r,scope)}
    retained = set(ah)&set(bh)
    added_ids = set(bh)-set(a)
    recat_in = (set(bh)&set(a))-set(ah)
    lost_ids = set(ah)-set(b)
    recat_out = (set(ah)&set(b))-set(bh)
    if len(bh) != len(ah)+len(added_ids)+len(recat_in)-len(lost_ids)-len(recat_out):
        raise ValueError('Hotel listing stock-flow identity failed')
    aa, bb = aggregate(ah.values()), aggregate(bh.values())
    result = {f'baseline_{k}':v for k,v in aa.items()}
    result.update({f'endpoint_{k}':v for k,v in bb.items()})
    result.update(retained_hotel_ids=len(retained), new_to_panel_hotel_ids=len(added_ids),
                  recategorized_into_hotel=len(recat_in), absent_baseline_hotel_ids=len(lost_ids),
                  recategorized_out_of_hotel=len(recat_out))
    for k,v in aggregate(ah[k] for k in retained).items():
        result['retained_baseline_'+k]=v
    for label, ids in [('retained',retained),('new_to_panel',added_ids)]:
        g=aggregate(bh[k] for k in ids)
        for k,v in g.items():
            result[f'{label}_{k}']=v
    first_after = [bh[k] for k in added_ids if bh[k]['first_review'] and bh[k]['first_review'][:10] >= start]
    result['new_ids_first_review_after_baseline'] = len(first_after)
    result['new_ids_first_review_before_baseline'] = sum(bool(bh[k]['first_review']) and bh[k]['first_review'][:10] < start for k in added_ids)
    deltas = [count(bh[k],'number_of_reviews')-count(ah[k],'number_of_reviews') for k in retained
              if count(bh[k],'number_of_reviews') is not None and count(ah[k],'number_of_reviews') is not None]
    result['retained_missing_lifetime_review_delta_ids'] = len(retained)-len(deltas)
    result['retained_lifetime_review_delta_nonnegative'] = sum(v for v in deltas if v >= 0)
    result['retained_negative_review_delta_ids'] = sum(v < 0 for v in deltas)
    for key in ['listings','number_of_reviews_ltm','number_of_reviews_l30d']:
        result[f'{key}_growth'] = growth_rate(bb[key],aa[key])
    result['ltm_reviews_per_listing_baseline'] = ratio(aa['number_of_reviews_ltm'],aa['listings'])
    result['ltm_reviews_per_listing_endpoint'] = ratio(bb['number_of_reviews_ltm'],bb['listings'])
    result['l30d_reviews_per_listing_baseline'] = ratio(aa['number_of_reviews_l30d'],aa['listings'])
    result['l30d_reviews_per_listing_endpoint'] = ratio(bb['number_of_reviews_l30d'],bb['listings'])
    return result

def pool_results(results, scope):
    selected = [r for r in results if r['scope'] == scope and r['pair_eligible']]
    if not selected:
        raise ValueError(f'No eligible markets for hotel scope: {scope}')
    # Keep nullable total columns even when the first city's count is unknown.
    review_totals = {f'{group}_{field}' for group in REVIEW_GROUPS for field in REVIEW_FIELDS}
    keys = [k for k, v in selected[0].items()
            if k in review_totals or (isinstance(v, int) and not isinstance(v, bool) and k != 'interval_days')]
    p = {k: complete_sum(r[k] for r in selected) for k in keys}
    p.update(scope=scope, markets=len(selected))
    for key in ('listings', *REVIEW_FIELDS):
        p[key+'_growth'] = growth_rate(p['endpoint_'+key], p['baseline_'+key])
    for label, field in zip(('ltm', 'l30d'), REVIEW_FIELDS):
        p[label+'_reviews_per_listing_growth'] = growth_rate(
            ratio(p['endpoint_'+field], p['endpoint_listings']),
            ratio(p['baseline_'+field], p['baseline_listings']))
        p['retained_'+label+'_reviews_growth'] = growth_rate(
            p['retained_'+field], p['retained_baseline_'+field])
    return p


def write_csv(path, rows):
    atomic_write_csv(path, rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--panel',choices=['historical13','archive25'],default='historical13')
    args=parser.parse_args()
    archive=args.panel=='archive25'
    out=OUT/'archive25' if archive else OUT
    manifest=ROOT/('data/raw/listing_churn_archive/download_manifest.csv' if archive else 'data/raw/listing_churn_panel/download_manifest.csv')
    with manifest.open(encoding='utf-8-sig',newline='') as f:
        metas=list(csv.DictReader(f))
    selected_markets=None
    exclusions={}
    selection_file=ROOT/'analysis/config/hotel_markets_25.csv'
    if archive:
        with selection_file.open(encoding='utf-8',newline='') as f:
            selection=list(csv.DictReader(f))
        selected_markets={r['market'] for r in selection}
        if len(selection)!=25 or len(selected_markets)!=25:
            raise ValueError('Expected 25 unique configured markets')
        with (ROOT/'data/processed/listing_churn_archive/market_coverage.csv').open(encoding='utf-8-sig',newline='') as f:
            coverage={r['market']:r for r in csv.DictReader(f)}
        for market in selected_markets:
            if market not in coverage: raise ValueError(f'Missing inherited coverage: {market}')
            if coverage[market]['status']!='pair_eligible': exclusions[market]=coverage[market]['reason']
    grouped=defaultdict(list)
    for m in metas:
        if selected_markets is not None and m['market'] not in selected_markets: continue
        if m['status'] != 'ok':
            raise ValueError('Acquisition failed in existing manifest')
        if archive: m['expected_rows']=m['rows']
        grouped[m['market']].append(m)
    if len(grouped) != (25 if archive else 13):
        raise ValueError('Market coverage does not match requested panel')
    out.mkdir(parents=True,exist_ok=True)
    results=[]; captures=[]; taxonomy=[]
    seen_baseline=set(); seen_endpoint=set()
    for market, ms in sorted(grouped.items()):
        ms.sort(key=lambda m:m['snapshot_start'])
        ma,mb=ms[0],ms[-1]
        if archive and (not ma['snapshot_start'].startswith('2025-09') or not mb['snapshot_start'].startswith('2026-06')):
            raise ValueError('Archive pair must be September 2025 to June 2026')
        a,b=read_capture(ma),read_capture(mb)
        eligible=market not in exclusions and all(m['source_partial_scope'].lower() != 'true' for m in [ma,mb])
        if eligible:
            ah={k for k,r in a.items() if is_hotel(r,'broad')}
            bh={k for k,r in b.items() if is_hotel(r,'broad')}
            if seen_baseline & ah or seen_endpoint & bh:
                raise ValueError('Cross-market duplicate hotel IDs require explicit reconciliation before pooling')
            seen_baseline.update(ah); seen_endpoint.update(bh)
        captures.extend([ma,mb])
        for scope in ['strict','broad','boutique']:
            results.append(dict(market=market,scope=scope,baseline_date=ma['snapshot_complete'],
                endpoint_date=mb['snapshot_complete'], interval_days=(date.fromisoformat(mb['snapshot_complete'])-date.fromisoformat(ma['snapshot_complete'])).days,
                pair_eligible=eligible,exclusion='' if eligible else exclusions.get(market,'team partial-scope endpoint flag'),
                **compare(a,b,ma['snapshot_complete'],scope)))
        for p,n in Counter(r['property_type'] for r in b.values() if is_hotel(r,'broad')).items():
            taxonomy.append(dict(market=market,endpoint_date=mb['snapshot_complete'],property_type=p,listings=n))
        print(f'{market}: {results[-3]["baseline_listings"]} -> {results[-3]["endpoint_listings"]} strict hotel-tagged listings; eligible={eligible}',flush=True)
    write_csv(out/'hotel_listing_panel.csv',results)
    write_csv(out/'reused_capture_manifest.csv',captures)
    write_csv(out/'hotel_taxonomy.csv',taxonomy)
    pooled=[pool_results(results, scope) for scope in ['strict','broad','boutique']]
    write_csv(out/'hotel_panel_pooled.csv',pooled)
    (out/'methodology.json').write_text(json.dumps(dict(
        as_of='2026-09-07',source='Inside Airbnb CC BY 4.0, existing team captures',
        panel=args.panel,selection='New analytical 25-market sample; not a recovered prior team list' if archive else 'Original historical 13-market sample',
        selection_sha256=hashlib.sha256(selection_file.read_bytes()).hexdigest() if archive else None,
        cross_market_duplicate_hotel_ids=0,
        snapshot_files_read=len(captures),new_raw_downloads=0,
        manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        strict_definition='property_type Hotel, Boutique hotel, or room in either',
        broad_definition='strict OR room_type Hotel room; includes B&B/serviced apartments',
        limits=['No verified independence, property deduplication, room inventory, booked nights, causal incrementality or 2026 new hotel product coverage',
                'First and last observed snapshots; unequal dates and no annualization or seasonal adjustment',
                'Austin excluded from pooled changes under existing team partial-scope flags',
                'Endpoint-new IDs may be re-listings, not newly recruited hotels',
                'Review counts are unconverted proxies; incomplete totals and their growth/means stay unknown (blank CSV cells)',
                'Observed review subtotals and missing-listing counts are separate; missingness propagates into pooled and retained-ID results',
                'Pooled unique_host_ids is sum of city counts, not globally deduplicated hosts']
        ),indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__':
    main()
