"""Assemble the user-selected 13-market hotel evidence panel without pooling units.

Requires all three extension workstreams. Original captures remain in place;
scoped views and explicit missing-data fields are written to a separate folder.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from research_integrity import atomic_write_csv, finite_number, verify_frozen_report

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/processed/hotel_13_market_panel'
RAW = ROOT / 'data/raw/hotel_13_market_extension'
SUPPLY = ROOT / 'data/processed/hotel_rollout_economics'


def csv_rows(path: Path) -> list[dict]:
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_csv(name: str, rows: list[dict], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f'Explicit columns required for empty output {name}')
        fields = list(rows[0])
    atomic_write_csv(OUT/name, rows, fields)


def validate_results(rows: list[dict], expected: set[str]) -> None:
    counts = Counter(row['market'] for row in rows)
    if set(counts) != expected or any(n != 1 for n in counts.values()):
        raise ValueError(f'Require one record for every selected market. Got {dict(counts)}')
    for row in rows:
        for key in ['source_id', 'source_url', 'observation_period', 'geography', 'metric', 'unit', 'status']:
            if not row.get(key):
                raise ValueError(f'Missing provenance/definition {key} in {row["market"]}')
        if row['status'] not in {'observed', 'calculated', 'estimated'}:
            raise ValueError(f'Unknown observation status: {row["status"]}')
        value = row.get('value')
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
            raise ValueError(f'Invalid primary numeric observation in {row["market"]}: {value}')
        for key in ('property_records_obtained', 'independent_rooms'):
            if row.get(key) is not None:
                finite_number(row[key], key, minimum=0)
                if key == 'property_records_obtained' and int(row[key]) != row[key]:
                    raise ValueError('Property records must be a whole number')


def root_results() -> list[dict]:
    austin = read_json(RAW / 'austin/summary.json')
    london = read_json(RAW / 'london/london_capacity_metadata.json')
    nyc = csv_rows(SUPPLY / 'nyc_hotel_license_frame.csv')
    current = [row for row in nyc if row['current_status_candidate'] == 'True']
    paris = csv_rows(SUPPLY / 'paris_classified_hotels.csv')
    return [
        dict(market='austin', source_id='H13-AUS-REG', source_url=austin['source_url'],
             observation_period=austin['rows_updated_utc'], geography=austin['geographic_scope'],
             metric='Recorded capacity of active hotel/motel/B&B licenses', value=austin['active_recorded_units_rooms'],
             unit='licensed rooms/units', status='calculated', property_records_obtained=austin['active_license_records'],
             property_record_definition='active operating-license rows, not deduplicated physical hotels', independent_rooms=None,
             limitations='Includes motel/B&B/hostel/HOA categories; all-hotel city/metro completeness and independence unverified.',
             overlap_status='New hotel-license frame; separate from Jessie STR licenses; earlier Visit Austin headline not added.',
             raw_path='data/raw/hotel_13_market_extension/austin/licenses.csv',
             observations=[{'metric':'Active Hotel-classified license capacity','value':25424,'unit':'licensed rooms/units','records':168}]),
        dict(market='london', source_id=london['source_id'], source_url=london['source_url'],
             observation_period='Q1 2025', geography=london['geography'],
             metric='Serviced accommodation inventory', value=london['reconciliation']['q1_2025']['published_london_total'],
             unit='serviced rooms', status='observed', property_records_obtained=0,
             property_record_definition='33 borough aggregates at two periods; no named-property records', independent_rooms=None,
             limitations='Includes B&Bs, guest houses, apart-hotels and hostels; July 2026 publication is not a 2026 observation.',
             overlap_status=london['overlap'], raw_path='data/raw/hotel_13_market_extension/london/gla_2026_report.pdf',
             observations=[{'metric':'Serviced accommodation Q1 2019','value':160115,'unit':'serviced rooms'}]),
        dict(market='new-york-city', source_id='HRE-NYC-LICENSE',
             source_url='https://data.cityofnewyork.us/Business/Issued-Licenses/w7w3-xahh',
             observation_period='Source updated 2026-08-20; status filter 2026-09-07',
             geography='NYC hotel operating-license records; five boroughs', metric='Active/Ready-for-Renewal candidate licenses',
             value=len(current), unit='license records', status='calculated', property_records_obtained=len(current),
             property_record_definition='785 candidate licenses / 761 address clusters; not 785 proven physical hotels',
             independent_rooms=None, limitations='No room-count field; active/renewal status is not evidence of Airbnb operation or booking production.',
             overlap_status='Reused earlier hotel rollout registry; historical CoStar independence anchor kept separately.',
             raw_path='data/raw/hotel_rollout_economics/nyc_query_1.json',
             observations=[{'metric':'Candidate address clusters','value':len({r['address_cluster'] for r in current}),'unit':'address clusters'}]),
        dict(market='paris', source_id='HRE-FR-CLASSIFIED',
             source_url='https://www.data.gouv.fr/datasets/hebergements-touristiques-classes-en-france',
             observation_period='Classification export retrieved 2026-09-07',
             geography='Paris municipality, postcodes 75001–75020 and 75116',
             metric='Classified-hotel registered capacity', value=sum(int(r['rooms']) for r in paris),
             unit='rooms', status='calculated', property_records_obtained=len(paris),
             property_record_definition='classified-hotel name/address identities', independent_rooms=None,
             limitations='Classified hotels only; chain affiliation and operating/Airbnb status unverified; unclassified stock excluded.',
             overlap_status='Reused Paris subset of France; France national total excluded from selected market panel.',
             raw_path='data/raw/hotel_rollout_economics/france_classified_accommodation.csv',
             observations=[{'metric':'Classified hotels with fewer than 50 rooms','value':1172,'unit':'properties','rooms':37301,'independence_verified':False}]),
    ]


def normalized_url(url: str) -> str:
    p = urlsplit(url.strip())
    return urlunsplit(('https', p.netloc.lower().removeprefix('www.'), p.path.rstrip('/'), p.query, ''))


def render_report(table: list[dict], summary: dict) -> None:
    def cell(value):
        return str(value).replace('|','/').replace('\n',' ')
    capacity_lines = []
    frame_lines = []
    notes = []
    for r in table:
        number = 'Missing' if r['capacity_value'] is None else f"{r['capacity_value']:,.0f}"
        capacity_lines.append(f"| [{r['market_label']}]({r['source_url']}) | {number} {cell(r['capacity_unit'])} | {cell(r['observation_period'])} | {cell(r['source_geography'])} |")
        frame_lines.append(f"| {r['market_label']} | {r['property_records_obtained']:,} | {cell(r['property_record_definition'])} |")
        notes.append(f"- **{r['market_label']}:** {r['limitations'].replace(' | ', ' ')}")
    market_names=', '.join(r['market_label'] for r in table)
    report=f'''# Airbnb hotels: the original 13-market evidence panel

As of September 7, 2026. **The user explicitly selected the original listing panel. All 13 markets are included:** {market_names}. The [active configuration](../../analysis/config/hotel_markets_13.csv) matches the original listing-panel IDs exactly, including Austin. Jessica's separate accommodation-choice study is existing team context, not this panel's market definition.

**All 13 now have a sourced capacity or licensing reference and a row in the requested production-data coverage table. This is a supply-evidence panel, not a measured Airbnb hotel bookings panel.** Absolute Airbnb hotel nights, Airbnb hotel revenue and current verified independent-room totals remain missing. Missing values are retained, not set to zero. Source geographies, accommodation types and dates differ, so no combined boutique/independent TAM total is asserted.

## Capacity and licensing references

Each market name links to its primary source. A license, registered room, directory room, and serviced-accommodation room are different units. The [full coverage table](../../data/processed/hotel_13_market_panel/market_coverage.csv) retains the exact metric, qualification, geography, limitations and provenance.

| Market / source | Recorded reference | Observation / publication basis | Source boundary |
|---|---:|---|---|
{chr(10).join(capacity_lines)}

These references need not cover every hotel in a selected listing-market polygon. No capacity is divided by an Inside Airbnb listing count, and country, county, city, downtown and district measures are not substituted for one another. Detailed alternate observations, including broader/narrower populations, are preserved in [market evidence](../../data/processed/hotel_13_market_panel/market_evidence.json).

## Property-level records available for the acquisition funnel

These counts describe the type of record actually obtained. They are not additive as a sample of unique hotels. Zero here means no usable property-level frame obtained in this workstream, not zero hotels in the market.

| Market | Records in usable candidate frame | Record definition |
|---|---:|---|
{chr(10).join(frame_lines)}

Rome's property candidates are from a separate June 2025 registry, while its primary city capacity reference is year-end 2024; the difference is not proved supply growth. Los Angeles's TMD directory is a municipal subset that excludes properties below 50 rooms, so it systematically misses part of the small-hotel opportunity. Sydney's development applications are preserved as pipeline evidence rather than counted as operating hotel properties. New Orleans licensing sources have different definitions and vintages; their count changes are not a hotel-closure series.

## What the Airbnb observations cover

Filtering the previously collected hotel pages to the approved 13 yields **{summary['existing_page_captures_in_scope']} page captures and {summary['existing_property_clusters_in_scope']} property-name/address clusters**, across New York City, Paris, London and Rome. These are the existing captures reused, not additional bookings or a representative 13-market hotel census. The other nine markets remain in the table with zero *captured pages in this particular collection*; that is not evidence Airbnb has no hotels there.

The accepted registry links within scope are **{summary['accepted_registered_room_matches_in_scope']} Paris properties / {summary['registered_rooms_in_accepted_matches']:,} registered rooms**. Room allocation to Airbnb, availability for requested dates, first booking dates, completed nights, fees and hotel-level revenue remain unobserved. Multiple listing IDs are clustered by property identity. Existing captures outside the approved scope remain in their original files but are excluded from this scoped view. [Scoped page observations](../../data/processed/hotel_13_market_panel/airbnb_page_observations_scoped.csv), [property clusters](../../data/processed/hotel_13_market_panel/airbnb_property_clusters_scoped.csv), [registry matches](../../data/processed/hotel_13_market_panel/airbnb_registry_crosswalk_scoped.csv)

The statistically meaningful next dataset is actual channel production or matched receipts with stable hotel IDs, hotel/home classification, cancellations, stay dates, room quantities and provider coverage. Supply registries cannot establish demand uplift or statistical significance. More regions do not fix that missing outcome.

## Independent/boutique capacity and the next-year financial test

The prior two historical independent-room anchors remain in a [separate context table](../../data/processed/hotel_13_market_panel/historical_independent_room_context.csv): CoStar's roughly 38,000 NYC independent rooms in September 2024, and HVS's approximately 51,040 Paris rooms calculated from 92,800 rooms × 55% at year-end 2023. Both are reused, dated source populations. Their shares are not applied to the new registries, and independence does not by itself establish boutique positioning or Airbnb eligibility. [CoStar public abstract](https://www.costar.com/article/1020852869/new-york-citys-existing-supply-and-pipeline-is-flooded-with-independent-hotels), [HVS Paris](https://hvs.com/Print/Paris-Market-Pulse-2024-Going-for-Gold?id=9930)

For each selected market, the required revenue bridge remains: eligible hotels → actual activation → Airbnb-allocated room nights → completed hotel nights → recognized platform revenue, with promotion costs, own-home/HotelTonight displacement and what is already in broker forecasts handled separately. A hotel booking shifted from another OTA can add Airbnb revenue even if the hotel's total occupancy does not rise. No hotel stock total is a substitute for these conversion and economic inputs.

The [Bloomberg/Refinitiv request](../../data/requests/hotel_channel_and_consensus_request.md) and [production schema](../../data/requests/hotel_channel_panel_schema.json) now explicitly use these 13 destinations. The [13-row provider coverage request](../../data/processed/hotel_13_market_panel/provider_coverage_request_13.csv) keeps every market, including absent provider coverage. Consolidated company estimates remain company estimates, not artificially constructed city-level consensus. The prior [financial materiality work](2026-09-07_hotel-expanded-research-results.md) remains the reference for the earnings and expectation test.

## Market-specific limitations

{chr(10).join(notes)}

## Reuse, reproducibility and checks

This panel reuses earlier Austin, London, NYC and Paris evidence and the explicitly labeled original city capacity anchors. It adds the separately documented registry/directory/report extractions for the remaining markets. Historical team sources, new versions of the same source and new property records are distinguished in [the overlap table](../../data/processed/hotel_13_market_panel/source_overlap.csv); a different URL alone is not independent evidence. The bounded review covers the frozen visible GitHub/local team inventory and the [latest repository delta](hotel-13-team-overlap-update.md) through commit `{summary['team_overlap_review_head']}`, not unshared personal work. The delta adds no hotel source URLs or hotel claims; the previous overlap dispositions therefore remain unchanged.

Source and extraction detail: [Austin](hotel-13-austin-extension.md), [London](hotel-13-london-extension.md), [Chicago / Los Angeles / San Diego](hotel-13-us-west-chicago-extension.md), [Nashville / New Orleans / Mexico City](hotel-13-south-mexico-extension.md), [Barcelona / Rome / Sydney](hotel-13-europe-sydney-extension.md), [NYC / Paris original registries](2026-09-07_hotel-rollout-economics-expansion.md).

Rebuild with `.venv/Scripts/python.exe analysis/src/assemble_hotel_13_market_panel.py`. The assembler requires exactly one result per approved market, checks the selected list against the original 13, rejects invalid quantities or missing provenance, and writes scoped views without deleting original datasets. Tests cover missing/duplicate/extra markets, invalid numeric values, and retaining missing measures. The [summary](../../data/processed/hotel_13_market_panel/summary.json) records the scope hash and exact capture counts. No hotel booking data, paid subscription, outreach or terminal export was obtained as part of this scope extension.
'''
    (ROOT/'research/notes/2026-09-07_hotel-original-13-market-coverage.md').write_text(report,encoding='utf-8')


def main() -> None:
    verify_frozen_report(ROOT, 'assemble_hotel_13_market_panel.py')
    scope = csv_rows(ROOT / 'analysis/config/hotel_markets_13.csv')
    expected = {row['market'] for row in scope}
    original = {row['market'] for row in csv_rows(ROOT / 'data/processed/listing_churn_panel/market_coverage.csv')}
    if len(scope) != 13 or expected != original:
        raise ValueError('Active hotel scope must equal all 13 original listing-panel market IDs.')
    selection = read_json(ROOT / 'analysis/config/hotel_13_market_scope_candidates.json')
    if selection['selected_universe'] != 'original_listing_panel':
        raise ValueError('User market selection does not match the original listing panel.')

    results = root_results()
    for group in ['us_west_chicago', 'south_mexico', 'europe_sydney']:
        extension = read_json(RAW / group / 'market_results.json')
        if isinstance(extension, dict):
            extension = extension.get('markets', extension.get('results'))
        if not isinstance(extension, list):
            raise ValueError(f'Expected a market result list for {group}')
        results.extend(extension)
    validate_results(results, expected)
    by_market = {row['market']:row for row in results}
    # This dated assembler includes fixed source interpretations in its report.
    # A changed evidence bundle must be reviewed before any scoped output is replaced.
    frozen = read_json(ROOT/'data/processed/hotel_13_market_panel/market_evidence.json')
    if [by_market[r['market']] for r in scope] != frozen:
        raise ValueError('Dated market evidence changed; audit the source extraction and narrative before publication')
    OUT.mkdir(parents=True, exist_ok=True)

    city_to_market = {r['market_label']:r['market'] for r in scope}
    pages_all = csv_rows(SUPPLY / 'airbnb_hotel_page_observations.csv')
    ids_all = csv_rows(SUPPLY / 'airbnb_property_identity_clusters.csv')
    pages = [dict(market=city_to_market[r['city']], **r) for r in pages_all if r['city'] in city_to_market]
    identities = [dict(market=city_to_market[r['city']], **r) for r in ids_all if r['city'] in city_to_market]
    write_csv('airbnb_page_observations_scoped.csv', pages)
    write_csv('airbnb_property_clusters_scoped.csv', identities)
    cross = [dict(market=city_to_market[r['airbnb_city']], **r) for r in csv_rows(SUPPLY / 'airbnb_registry_crosswalk.csv') if r['airbnb_city'] in city_to_market]
    write_csv('airbnb_registry_crosswalk_scoped.csv', cross)
    identity_counts = Counter(r['market'] for r in identities)
    page_counts = Counter(r['market'] for r in pages)

    table = []
    for item in scope:
        r = by_market[item['market']]
        def as_text(value):
            return ' | '.join(str(x) for x in value) if isinstance(value, list) else str(value or '')
        table.append({
            'market': item['market'], 'market_label': item['market_label'], 'country':item['country'],
            'capacity_metric':r['metric'], 'capacity_value':r.get('value'), 'capacity_unit':r['unit'],
            'capacity_qualifier':r.get('qualifier',r.get('value_qualifier','See source scope and limitations; not necessarily a census')),
            'observation_period':r['observation_period'], 'source_geography':r['geography'],
            'status':r['status'], 'source_id':r['source_id'], 'source_url':r['source_url'],
            'property_records_obtained':r.get('property_records_obtained',0),
            'property_record_definition':r.get('property_record_definition',r.get('property_records_basis',
                'No named operating-property frame obtained; see alternate aggregate or pipeline evidence.' if not r.get('property_records_obtained') else
                'See market source memo; these are not necessarily distinct physical hotels')),
            'current_verified_independent_rooms':r.get('independent_rooms'),
            'airbnb_pages_observed_in_existing_capture':page_counts[item['market']],
            'airbnb_property_clusters_observed_in_existing_capture':identity_counts[item['market']],
            'actual_airbnb_hotel_nights':None, 'actual_airbnb_hotel_revenue_usd':None,
            'booking_data_status':'not obtained; missing rather than zero',
            'geography_match_to_listing_polygon':'not certified; keep source boundaries explicit',
            'limitations':as_text(r.get('limitations')),
            'overlap_status':as_text(r.get('overlap_status')), 'raw_path':r.get('raw_path',''),
        })
    write_csv('market_coverage.csv', table)
    (OUT / 'market_evidence.json').write_text(json.dumps([by_market[r['market']] for r in scope], indent=2, ensure_ascii=False)+'\n',encoding='utf-8')

    # Historical independence evidence retains its own year/geography. Never apply
    # a 2023/2024 share to a 2026 registry with different population coverage.
    anchors = csv_rows(ROOT / 'data/processed/hotel_funnel_audit/hotel_market_capacity_anchors.csv')
    old_sources = {r['source_id']:r for r in read_json(ROOT / 'research/sources/hotel_funnel_audit.json')}
    historical = []
    for row in anchors:
        if row['market'] not in expected or not row.get('independent_rooms_derived_or_reported'):
            continue
        historical.append({
            'market':row['market'], 'rooms':row['independent_rooms_derived_or_reported'],
            'room_share':row['independent_room_share'], 'period':row['vintage'],
            'geography':row['geography'], 'source_id':row['source_id'], 'source_url':old_sources[row['source_id']]['url'],
            'calculated_from_rounded_inputs':row['independent_rooms_calculated'],
            'status':'reused historical context; not current eligible boutique room TAM',
            'limitation':row['limitation'],
        })
    write_csv('historical_independent_room_context.csv',historical)

    requested = []
    for r in scope:
        requested.append({'market':r['market'],'market_label':r['market_label'],'country':r['country'],
            'requested_period':'2024-01 through latest complete month; forward bookings separately',
            'required_metrics':'hotel/home/unknown reservations; room nights; room value; unique hotels; active panel consumers; cancellations; HotelTonight split',
            'coverage_status':'no entitled production export obtained',
            'missing_policy':'retain this market with explicit missing status; do not impute zero business',
            'geography_rule':r['geography_rule']})
    write_csv('provider_coverage_request_13.csv',requested)

    team_urls = {normalized_url(r['url']) for r in csv_rows(ROOT/'data/processed/hotel_expanded_research/team_source_urls.csv')}
    team_update=read_json(RAW/'team_update_3de6ec7/update_summary.json')
    if team_update['errors']:
        raise ValueError('Latest team overlap review has unresolved fetch/validation errors.')
    team_urls.update(normalized_url(r['url']) for r in csv_rows(RAW/'team_update_3de6ec7/changed_source_urls.csv'))
    ledger_names = ['hotel_13_austin_sources','hotel_13_london_sources','hotel_13_us_west_chicago_sources',
                    'hotel_13_south_mexico_sources','hotel_13_europe_sydney_sources']
    provenance = []
    for name in ledger_names:
        ledger = read_json(ROOT/f'research/sources/{name}.json')
        sources = ledger if isinstance(ledger,list) else ledger['sources']
        for source in sources:
            url=source.get('url',source.get('source_url',''))
            if not url:
                continue
            provenance.append({'ledger':name,'source_id':source.get('source_id',source.get('id','')),
                'source_url':url,'exact_match_to_frozen_team_urls':normalized_url(url) in team_urls,
                'declared_overlap_status':str(source.get('overlap_status',source.get('overlap',source.get('disposition','See source ledger')))),
                'interpretation':'Exact URL match only; a new URL does not establish independent evidence or claim novelty.'})
    write_csv('source_overlap.csv',provenance)

    accepted=[r for r in cross if r['accepted_roomcount_link']=='True']
    summary={'as_of':'2026-09-07','scope_status':'explicitly selected by user','selected_universe':'original_listing_panel',
        'selected_markets':[r['market'] for r in scope], 'market_rows':len(table),
        'existing_page_captures_in_scope':len(pages),'existing_property_clusters_in_scope':len(identities),
        'markets_with_existing_page_captures':len(identity_counts),
        'existing_page_captures_outside_scope_retained_in_original_files':len(pages_all)-len(pages),
        'existing_property_clusters_outside_scope_retained_in_original_files':len(ids_all)-len(identities),
        'accepted_registered_room_matches_in_scope':len(accepted),
        'registered_rooms_in_accepted_matches':sum(int(r['registered_physical_rooms']) for r in accepted),
        'new_raw_airbnb_hotel_booking_observations':0,'absolute_hotel_nights_obtained':False,'absolute_hotel_revenue_obtained':False,
        'capacity_sum':None,'capacity_sum_reason':'Mixed units, years, boundaries and registry coverage; no defensible common-date independent/boutique total.',
        'extension_source_records_with_urls':len(provenance),
        'extension_source_url_records_with_exact_team_matches':sum(r['exact_match_to_frozen_team_urls'] for r in provenance),
        'team_overlap_review_base':team_update['base_commit'],
        'team_overlap_review_head':team_update['head_commit'],
        'incremental_team_source_urls':team_update['changed_source_url_count'],
        'scope_sha256':hashlib.sha256((ROOT/'analysis/config/hotel_markets_13.csv').read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
        'scope_hash_convention':'SHA-256 after CRLF-to-LF normalization',
        'limitations':['Every selected market retained, including missing production data.',
                      'Property/license/development and geographic-aggregate records are not pooled as independent hotels.',
                      'Existing Airbnb page samples are reused, not new booking evidence or a complete hotel census.',
                      'Statistical significance of demand remains unmeasured without actual hotel production outcomes.']}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    render_report(table,summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
