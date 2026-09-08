"""Transparent hotel TAM, mix, room productivity and credit sensitivities.

This is an operating audit, not an estimate of undisclosed Airbnb hotel earnings.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
from research_integrity import finite_number, atomic_write_csv

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT/'analysis/config/hotel_funnel_audit.json'
OUT = ROOT/'data/processed/hotel_funnel_audit'

def fraction(x):
    return finite_number(x, 'Fraction', minimum=0, maximum=1)

def growth(x):
    return finite_number(x, 'Growth', minimum=-1)

def mix_after(s, gc, gh):
    fraction(s); growth(gc); growth(gh)
    total=(1-s)*(1+gc)+s*(1+gh)
    return s*(1+gh)/total if total > 0 else None

def nights_per_signed_property(rooms, activation, live_fraction, occupancy, channel_share):
    finite_number(rooms, 'Rooms', minimum=0)
    return rooms*365*math.prod(fraction(v) for v in [activation,live_fraction,occupancy,channel_share])

def required_properties(nights, productivity):
    finite_number(nights, 'Target nights', minimum=0)
    finite_number(productivity, 'Property productivity', minimum=0)
    return nights/productivity if productivity else (0 if nights == 0 else None)

def contribution_share(take, variable_cost, eligible, award, redemption, funding):
    for v in [take,variable_cost,eligible,award,redemption,funding]: fraction(v)
    return take-variable_cost-eligible*award*redemption*funding


def validate_market_scope(anchors, selection):
    names = [m['market'] for m in anchors]
    selected = [m['market'] for m in selection]
    if len(names) != 25 or len(set(names)) != 25 or len(selected) != 25 or set(names) != set(selected):
        raise ValueError('Capacity anchors must match exactly 25 unique selected markets')


def available_daily_rooms(room_nights, days):
    finite_number(room_nights, 'Available room nights', minimum=0)
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 31:
        raise ValueError('Nonnegative room nights and a valid month length required')
    return room_nights / days

def write(name, rows):
    atomic_write_csv(OUT/(name+'.csv'), rows)


def validate_config(c):
    """Validate the full scenario before any output is replaced."""
    a = c['assumptions']
    growth(a['home_growth'])
    finite_number(a['hotel_growth_multiple'], 'Hotel growth multiple', minimum=0)
    growth(a['home_growth'] * a['hotel_growth_multiple'])
    for key in ('rooms_per_property', 'adr_usd', 'required_revenue_usd'):
        finite_number(a[key], key, minimum=0)
    if a['adr_usd'] == 0 or a['hotel_take_rate'] == 0:
        raise ValueError('A positive ADR and take rate are required for the revenue hurdle')
    for key in ('activation_rate', 'average_fraction_of_year_live', 'physical_hotel_occupancy',
                'airbnb_share_of_occupied_room_nights', 'hotel_take_rate', 'credit_award_rate',
                'credit_eligible_gbv_share', 'airbnb_credit_funding_share', 'variable_cost_share_gbv'):
        fraction(a[key])
    for key in ('starting_hotel_shares', 'credit_redemption_scenarios'):
        if not a[key]:
            raise ValueError(f'Empty scenario grid: {key}')
        for value in a[key]:
            fraction(value)
    finite_number(c['global']['rooms'], 'Global room stock', minimum=0)
    fraction(c['global']['branded_room_share'])
    for m in c['market_anchors']:
        for key in ('hotel_rooms', 'independent_rooms'):
            if m[key] is not None:
                finite_number(m[key], key, minimum=0)
        if m['independent_room_share'] is not None:
            fraction(m['independent_room_share'])
        if m['boutique_available_room_nights'] is not None:
            available_daily_rooms(m['boutique_available_room_nights'], m['available_period_days'])


def break_even_redemption(a):
    exposure = a['credit_eligible_gbv_share'] * a['credit_award_rate'] * a['airbnb_credit_funding_share']
    return (a['hotel_take_rate'] - a['variable_cost_share_gbv']) / exposure if exposure else None

def main():
    c=json.loads(CONFIG.read_text(encoding='utf-8')); a=c['assumptions']
    validate_config(c)
    with (ROOT/'analysis/config/hotel_markets_25.csv').open(encoding='utf-8', newline='') as f:
        selection = list(csv.DictReader(f))
    validate_market_scope(c['market_anchors'], selection)
    for relative in ('archive25/hotel_listing_panel.csv', 'reused_capture_manifest.csv',
                     'archive25/reused_capture_manifest.csv'):
        if not (OUT/relative).is_file():
            raise ValueError(f'Required prior hotel audit is missing: {relative}')
    OUT.mkdir(parents=True,exist_ok=True)
    gc=a['home_growth']; gh=gc*a['hotel_growth_multiple']
    write('hotel_mix_scenarios',[dict(starting_hotel_share=s,home_growth=gc,hotel_growth=gh,
        ending_hotel_share=mix_after(s,gc,gh),combined_growth=(1-s)*gc+s*gh,
        growth_uplift_vs_all_nights_at_home_rate=s*(gh-gc),status='analyst_scenario')
        for s in a['starting_hotel_shares']])
    rows=[]
    for channel in [.02,.05,.10,.20]:
        p=nights_per_signed_property(a['rooms_per_property'],a['activation_rate'],
            a['average_fraction_of_year_live'],a['physical_hotel_occupancy'],channel)
        rev_per_night=a['adr_usd']*a['hotel_take_rate']
        rows.append(dict(airbnb_channel_share=channel,nights_per_signed_property_first_year=p,
            properties_for_1m_nights=required_properties(1e6,p),
            nights_for_target_revenue=a['required_revenue_usd']/rev_per_night,
            properties_for_target_revenue=required_properties(a['required_revenue_usd']/rev_per_night,p),
            gross_revenue_per_signed_property=p*rev_per_night,status='analyst_scenario'))
    write('hotel_supply_requirements',rows)
    write('hotel_credit_sensitivity',[dict(redemption_rate=r,
        credit_cost_share_hotel_gbv=a['credit_eligible_gbv_share']*a['credit_award_rate']*r*a['airbnb_credit_funding_share'],
        contribution_share_gbv_before_fixed_costs=contribution_share(a['hotel_take_rate'],a['variable_cost_share_gbv'],
            a['credit_eligible_gbv_share'],a['credit_award_rate'],r,a['airbnb_credit_funding_share']),
        status='analyst_scenario_not_accounting_forecast') for r in a['credit_redemption_scenarios']])
    tam=[]
    for m in c['market_anchors']:
        keys=m['independent_rooms']
        derived=False
        if keys is None and m['hotel_rooms'] is not None and m['independent_room_share'] is not None:
            keys=m['hotel_rooms']*fraction(m['independent_room_share']); derived=True
        tam.append({**m,'independent_rooms_derived_or_reported':keys,
            'independent_rooms_calculated':derived,
            'annual_physical_independent_roomnight_capacity':keys*365 if keys is not None else None,
            'boutique_eligible_rooms':None,
            'boutique_average_daily_available_rooms':available_daily_rooms(m['boutique_available_room_nights'],m['available_period_days'])
                if m['boutique_available_room_nights'] is not None else None})
    write('hotel_market_capacity_anchors',tam)
    global_keys=c['global']['rooms']*(1-fraction(c['global']['branded_room_share']))
    write('global_hotel_tam_sensitivity',[dict(global_unbranded_rooms=global_keys,occupancy=o,
        annual_all_channel_occupied_room_nights=global_keys*365*o,
        one_percent_airbnb_share_before_eligibility_filters=global_keys*365*o*.01,
        status='room_stock_derived_from_source_occupancy_and_channel_share_assumed') for o in [.60,.70,.75]])
    report=dict(as_of=c['as_of'],scope_status=c['scope_status'],
        config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        global_unbranded_rooms=global_keys,
        global_physical_roomnight_capacity=global_keys*365,
        starting_share_reaching_10pct_after_year=.1*(1+gc)/(.9*(1+gh)+.1*(1+gc)),
        credit_redemption_break_even=break_even_redemption(a),
        known_historical_independent_room_subtotal=sum(m['independent_rooms_derived_or_reported'] or 0 for m in tam),
        city_anchors=len(tam),city_independent_anchors=sum(m['independent_rooms_derived_or_reported'] is not None for m in tam),
        limitations=['New judgment-selected 25-market sample, not a recovered team list or representative world sample','No verified boutique-eligible room census',
            'No global extrapolation from selected cities','City vintages and geography differ; subtotal is historical, not current floor',
            'Capacity is not demand, bookings, incremental revenue or contribution'])
    (OUT/'hotel_model_summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # One reviewable market table; do not pool the overlapping historical panels.
    with (OUT/'archive25/hotel_listing_panel.csv').open(encoding='utf-8',newline='') as f:
        panel={r['market']:r for r in csv.DictReader(f) if r['scope']=='strict'}
    if set(panel) != {r['market'] for r in selection}:
        raise ValueError('Listing panel does not match capacity scope')
    choices={r['market']:r for r in selection}
    sources={r['source_id']:r for r in json.loads((ROOT/'research/sources/hotel_funnel_audit.json').read_text(encoding='utf-8'))}
    combined=[]
    for anchor in tam:
        market=anchor['market']
        source=sources[anchor['source_id']]
        combined.append({**choices[market],**anchor,'source_url':source['url'],'source_access':source['access'],
            **{'listing_panel_'+k:v for k,v in panel[market].items() if k not in ['market','scope']}})
    write('hotel_25_market_audit',combined)
    captures=[]
    for label,path in [('historical13',OUT/'reused_capture_manifest.csv'),('archive25',OUT/'archive25/reused_capture_manifest.csv')]:
        with path.open(encoding='utf-8',newline='') as f:
            captures.extend({'panel':label,**r} for r in csv.DictReader(f))
    by_hash={}
    for r in captures:
        by_hash.setdefault(r['sha256'],[]).append(r)
    dedup=[dict(sha256=h,market=rs[0]['market'],snapshot_start=rs[0]['snapshot_start'],
        panels=' | '.join(sorted({r['panel'] for r in rs})),references=len(rs),
        local_paths=' | '.join(sorted({r['local_path'] for r in rs}))) for h,rs in sorted(by_hash.items())]
    write('unique_reused_captures',dedup)
    overlap=dict(capture_references=len(captures),unique_hashes=len(by_hash),
        shared_between_panels=sum(len({r['panel'] for r in rs})>1 for rs in by_hash.values()),
        rule='Panels are overlapping sensitivity views and are never added or treated as independent corroboration.')
    (OUT/'panel_capture_overlap.json').write_text(json.dumps(overlap,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
