"""Verify collected units and compare sources against the frozen team inventory.

URL matches identify reuse, not claim independence. Registry rows and document
counts are coverage measures; they are never added to booking observations.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from research_integrity import atomic_write_csv

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/processed/hotel_expanded_research'
SUPPLY = ROOT / 'data/processed/hotel_rollout_economics'


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix('www.')
    # Preserve path case and query, which can identify different resources.
    return urlunsplit(('https', host, parts.path.rstrip('/'), parts.query, ''))


def main() -> None:
    team_urls: dict[str, set[str]] = defaultdict(set)
    for row in read_csv(OUT / 'team_source_urls.csv'):
        team_urls[canonical_url(row['url'])].add(row['location'])

    ledgers = ['hotel_absolute_disclosure_search', 'hotel_channel_data_expansion',
               'hotel_rollout_economics_expansion']
    source_rows = []
    source_artifact_hashes_verified = 0
    for ledger in ledgers:
        content = json.loads((ROOT / f'research/sources/{ledger}.json').read_text(encoding='utf-8'))
        sources = content if isinstance(content, list) else content['sources']
        for source in sources:
            artifact_path = source.get('local_path', source.get('path'))
            digest = source.get('sha256')
            if artifact_path and digest:
                artifact = ROOT / artifact_path
                if not artifact.exists() or hashlib.sha256(artifact.read_bytes()).hexdigest() != digest:
                    raise AssertionError(f'Source artifact path/hash mismatch: {artifact}')
                source_artifact_hashes_verified += 1
            url = source.get('url', '')
            if not url:
                continue
            canonical = canonical_url(url)
            matches = sorted(team_urls.get(canonical, set()))
            source_rows.append({
                'workstream': ledger,
                'source_id': source.get('source_id', source.get('id', '')),
                'title': source.get('title', ''), 'url': url,
                'canonical_url': canonical,
                'exact_team_url_match': bool(matches),
                'team_document_matches': len(matches),
                'team_locations': ' | '.join(matches),
                'novelty_note': 'Reused URL; do not call independent corroboration' if matches else
                'No exact URL match; claim/source-family novelty still requires semantic review',
            })
    coverage = json.loads((SUPPLY / 'coverage_summary.json').read_text(encoding='utf-8'))
    cross = json.loads((SUPPLY / 'crosswalk_summary.json').read_text(encoding='utf-8'))
    nyc = read_csv(SUPPLY / 'nyc_hotel_license_frame.csv')
    france = read_csv(SUPPLY / 'france_classified_hotels_deduplicated.csv')
    paris = read_csv(SUPPLY / 'paris_classified_hotels.csv')
    singapore = read_csv(SUPPLY / 'singapore_hotel_frame.csv')
    pages = read_csv(SUPPLY / 'airbnb_hotel_page_observations.csv')
    identities = read_csv(SUPPLY / 'airbnb_property_identity_clusters.csv')
    links = read_csv(SUPPLY / 'airbnb_registry_crosswalk.csv')
    accepted = [row for row in links if row['accepted_roomcount_link'] == 'True']
    checks = {}
    checks['nyc_license_unique_ids'] = len(nyc) == len({row['license_nbr'] for row in nyc}) == 826
    candidates = [row for row in nyc if row['current_status_candidate'] == 'True']
    checks['nyc_candidate_status_and_address_counts'] = len(candidates) == 785 and len({row['address_cluster'] for row in candidates}) == 761
    checks['france_unique_identities'] = len(france) == len({row['name_address_key'] for row in france}) == 13302
    checks['france_room_sum'] = sum(int(row['rooms']) for row in france) == coverage['france']['hotel_rooms_deduplicated'] == 606429
    checks['paris_subset_not_additional_population'] = {row['name_address_key'] for row in paris}.issubset({row['name_address_key'] for row in france})
    checks['paris_counts_and_rooms'] = len(paris) == 1589 and sum(int(row['rooms']) for row in paris) == 85815
    checks['singapore_counts_and_rooms'] = len(singapore) == len({row['object_id'] for row in singapore}) == 468 and sum(int(row['rooms']) for row in singapore) == 74597
    checks['airbnb_pages_and_clusters'] = len(pages) == 143 and len(identities) == 141
    checks['roomcount_links_unique'] = len(accepted) == len({row['airbnb_property_key'] for row in accepted}) == len({(row['registry_source_id'], row['registry_id']) for row in accepted}) == 41
    checks['roomcount_link_sum'] = sum(int(row['registered_physical_rooms']) for row in accepted) == cross['accepted_physical_rooms'] == 3499
    checks['no_booking_or_price_observations'] = coverage['airbnb_pages']['actual_booking_observations'] == coverage['airbnb_pages']['price_quotes_collected'] == 0
    for name, passed in checks.items():
        if not passed:
            raise AssertionError(f'Coverage check failed: {name}')

    overlap = {
        'source_records_with_urls': len(source_rows),
        'distinct_canonical_urls': len({r['canonical_url'] for r in source_rows}),
        'records_with_exact_team_url_matches': sum(r['exact_team_url_match'] for r in source_rows),
        'by_workstream': {ledger: {
            'records': sum(r['workstream'] == ledger for r in source_rows),
            'records_with_exact_team_url_matches': sum(r['workstream'] == ledger and r['exact_team_url_match'] for r in source_rows),
        } for ledger in ledgers},
        'limitation': 'Exact normalized URLs only. Translations, syndications, new dates and new URLs for old claims are not independent observations. No claim about unshared work.'
    }
    result = {'as_of': '2026-09-07', 'checks': checks, 'all_checks_passed': all(checks.values()), 'source_overlap': overlap,
              'source_artifact_path_hash_pairs_verified': source_artifact_hashes_verified,
              'raw_registry_rows': coverage['nyc']['license_rows'] + coverage['france']['hotel_rows'] + coverage['singapore']['hotel_rows'],
              'actual_airbnb_hotel_transactions_obtained': 0,
              'absolute_current_airbnb_hotel_nights_obtained': False,
              'absolute_current_airbnb_hotel_revenue_obtained': False,
              'causal_hotel_uplift_estimate_obtained': False}
    atomic_write_csv(OUT / 'expanded_source_overlap.csv', source_rows)
    (OUT / 'expanded_output_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
