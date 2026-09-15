"""Bounded source precision audit. Offline, no fitted model or forecast writes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
INPUTS = ROOT / 'data/processed/forecast_methods/l3_source_contract_v1/precision/inputs_v1'
METRICS = ('gbv_musd', 'revenue_musd', 'nights_m', 'adr_usd')
QUARTERS = tuple(f'{y}Q{q}' for y in range(2020, 2027) for q in range(1, 5)
                 if '2020Q3' <= f'{y}Q{q}' <= '2026Q2')
UNIT = {'gbv_musd': 'USD_million', 'revenue_musd': 'USD_million',
        'nights_m': 'million_aggregate_booked_units', 'adr_usd': 'USD_per_aggregate_booking'}
FACTORS = {'gbv_musd': {'USD_million': 1, 'USD_billion': 1000},
           'revenue_musd': {'USD_million': 1, 'USD_thousand': .001},
           'nights_m': {'million_bookings': 1},
           'adr_usd': {'USD_per_aggregate_booking': 1}}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def normalize(metric, value, unit):
    if unit not in FACTORS[metric]:
        raise ValueError(f'Incompatible units: {metric} / {unit}')
    if isinstance(value, bool):
        raise ValueError('Boolean is not a metric observation')
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError('Metric observations must be finite and nonnegative')
    result = value * FACTORS[metric][unit]
    if not math.isfinite(result):
        raise ValueError('Unit conversion produced nonfinite value')
    return result


def canonical_quarter(q):
    return f'20{q[2:]}Q{q[0]}' if len(q) == 4 and q[1] == 'Q' else q


def close(a, b):
    return abs(a-b) <= 1e-8


def load(inputs=INPUTS):
    inputs = Path(inputs)
    manifest = json.loads((inputs/'input_manifest.json').read_text(encoding='utf-8'))
    for name, item in manifest['files'].items():
        if sha(inputs/name) != item['sha256']:
            raise ValueError(f'Frozen input checksum mismatch: {name}')
    facts = json.loads((inputs/'audit_facts.json').read_text(encoding='utf-8'))
    return facts, read_csv(inputs/'frozen_panel.csv'), read_csv(inputs/'lambda_basis.csv'), read_csv(inputs/'calendar.csv'), manifest


def validate(data, panel, lambdas, calendar):
    expected = {(q, m) for q in QUARTERS for m in METRICS}
    keys = [(x['quarter'], x['metric']) for x in data['facts']]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError('Need exactly 96 distinct quarter/metric cells')
    if tuple(data['quarters']) != QUARTERS or set(data['scope']) != set(METRICS):
        raise ValueError('Scope/quarter contract changed')
    pkeys = [canonical_quarter(r['quarter']) for r in panel]
    if len(pkeys) != 24 or set(pkeys) != set(QUARTERS):
        raise ValueError('Frozen panel must have exactly 24 distinct quarters')
    for row in panel:
        for metric in METRICS:
            # Frozen fields have normalized units; source count-unit lexeme is retained separately.
            normalize(metric, row[metric], 'million_bookings' if metric == 'nights_m' else UNIT[metric])
    sources = {s['id']: s for s in data['sources']}
    if len(sources) != len(data['sources']):
        raise ValueError('Duplicate source')
    for s in sources.values():
        if not s['url'].startswith('https://www.sec.gov/Archives/edgar/data/1559720/'):
            raise ValueError('Source outside permitted primary SEC issuer scope')
        if date.fromisoformat(s['publication_date']) > date.fromisoformat(data['as_of']):
            raise ValueError('Future source')
    def check(m, o):
        if o is None:
            return
        normalize(m, o['value'], o['unit'])
        if o['precision_step'] <= 0 or not o['section']:
            raise ValueError('Observation lacks precision/section')
        source = sources[o['source_id']]
        if source['access_status'] != 'checked_primary_text':
            raise ValueError('Observation source text was not checked')
        known = date.fromisoformat(o['first_known_date'])
        if known < date.fromisoformat(source['publication_date']):
            raise ValueError('Observation illegally backdated before its source')
        if known > date.fromisoformat(data['as_of']):
            raise ValueError('Observation from future information set')
        if 'derivation' in o:
            d = o['derivation']
            if d['operation'] != 'subtract' or len(d['terms']) != 2:
                raise ValueError('Only explicit two-source aggregate subtraction supported')
            a, b = d['terms']
            for term in (a, b):
                if sources[term['source_id']]['access_status'] != 'checked_primary_text':
                    raise ValueError('Derived observation parent source text was not checked')
                if known < date.fromisoformat(sources[term['source_id']]['publication_date']):
                    raise ValueError('Derived value precedes a required source')
                normalize(m, term['value'], term['unit'])
            if not close(normalize(m, o['value'], o['unit']), normalize(m, a['value'], a['unit'])-normalize(m, b['value'], b['unit'])):
                raise ValueError('Derived arithmetic mismatch')
            total_step = sum(normalize(m, t['precision_step'], t['unit']) for t in (a, b))
            if not close(normalize(m, o['precision_step'], o['unit']), total_step):
                raise ValueError('Derived precision must propagate both rounding intervals')
    for x in data['facts']:
        if x['original_source_id'] not in sources:
            raise ValueError('Missing original source')
        for k in ('original', 'fine'):
            check(x['metric'], x[k])
        if x['original'] and x['fine']:
            op = normalize(x['metric'], x['original']['precision_step'], x['original']['unit'])
            fp = normalize(x['metric'], x['fine']['precision_step'], x['fine']['unit'])
            if fp >= op:
                raise ValueError('Finer candidate is not more precise than original')
    for x in data['supplements']:
        check(x['metric'], x['observation'])
    if len(lambdas) != 2 or {r['booking_quarter'] for r in lambdas} != {'2026Q1', '2026Q2'}:
        raise ValueError('Expected two inherited current Q3 coefficient rows')
    if {r['quarter'] for r in lambdas} != {'2026Q3'} or len({r['lambda_pct'] for r in lambdas}) != 1:
        raise ValueError('Incompatible held-fixed lambda')
    pmap = {canonical_quarter(r['quarter']): r for r in panel}
    for r in lambdas:
        weight = 2/3 if r['booking_quarter'] == '2026Q2' else 1/3
        if not math.isclose(float(r['kernel_coefficient']), weight, abs_tol=1e-11):
            raise ValueError('Operational fixed weight changed')
        if not close(float(r['gbv_reported_usd'])/1e6, float(pmap[r['booking_quarter']]['gbv_musd'])):
            raise ValueError('Inherited GBV units/baseline mismatch')
        if not (0 < float(r['lambda_pct']) < 100):
            raise ValueError('Lambda must be percentage coefficient, converted exactly once')
        known = date.fromisoformat(r['lambda_knowable_from'])
        origin = date.fromisoformat(r['kernel_origin'])
        information = date.fromisoformat(r['information_date'])
        if not known <= origin <= information <= date.fromisoformat(data['as_of']):
            raise ValueError('Inherited lambda dates violate known/origin/information/audit chronology')
    return sources, pmap


def definition(q, m):
    if m in ('nights_m', 'adr_usd'):
        name = 'Nights and Experiences Booked' if q < '2025Q2' else 'Nights and Seats Booked'
        detail = 'stay nights plus experience participant seats' if q < '2025Q2' else 'stay nights plus experience and service participant seats'
        return name, detail + ('; ADR is direct GBV per aggregate booked unit, except explicitly calculated frozen 2020 ADR' if m == 'adr_usd' else '; not pure hotel room nights')
    return ('Gross Booking Value' if m == 'gbv_musd' else 'GAAP revenue'), ('Booking-event gross value, includes host earnings, service/cleaning fees and taxes, net cancellations/alterations; not recognized revenue' if m == 'gbv_musd' else 'Recognized revenue; not cash bookings or GBV')


def flatten_observation(prefix, o, sources, metric):
    if o is None:
        return {prefix+'_value': None, prefix+'_unit': None, prefix+'_normalized_value': None,
                prefix+'_source_id': None, prefix+'_source_url': None, prefix+'_document': None,
                prefix+'_section': None, prefix+'_first_known_date': None,
                prefix+'_precision_step_normalized': None, prefix+'_calculated': None}
    s = sources[o['source_id']]
    return {prefix+'_value': o['value'], prefix+'_unit': o['unit'],
            prefix+'_normalized_value': normalize(metric, o['value'], o['unit']),
            prefix+'_source_id': s['id'], prefix+'_source_url': s['url'], prefix+'_document': s['document'],
            prefix+'_section': o['section'], prefix+'_first_known_date': o['first_known_date'],
            prefix+'_precision_step_normalized': normalize(metric, o['precision_step'], o['unit']),
            prefix+'_calculated': 'derivation' in o}


def build(data, panel, lambdas, calendar):
    sources, pmap = validate(data, panel, lambdas, calendar)
    ledger = []
    for x in data['facts']:
        q, m = x['quarter'], x['metric']
        frozen = float(pmap[q][m])
        original, fine = x['original'], x['fine']
        s = sources[x['original_source_id']]
        chosen = fine or original
        value = normalize(m, chosen['value'], chosen['unit']) if chosen else None
        delta = value-frozen if chosen else None
        step = .1 if q in ('2020Q3', '2020Q4') and m in ('gbv_musd', 'revenue_musd') else {'gbv_musd': 100, 'revenue_musd': 1, 'nights_m': .1, 'adr_usd': .01}[m]
        compatible = abs(delta) <= step/2 + 1e-8 if delta is not None else None
        later = bool(fine and fine['first_known_date'] > s['publication_date'])
        if m == 'adr_usd' and q in ('2020Q3', '2020Q4'):
            classification = 'definition_difference'
        elif original is None:
            classification = 'unresolved'
        elif delta is not None and close(delta, 0):
            classification = 'exact'
        elif not compatible:
            classification = 'unresolved'
        elif later:
            classification = 'later_precision'
        else:
            classification = 'rounding'
        ov = normalize(m, original['value'], original['unit']) if original else None
        ostep = normalize(m, original['precision_step'], original['unit']) if original else None
        oc = None if original is None else abs(ov-frozen) <= ostep/2 + 1e-8
        name, detail = definition(q, m)
        ledger.append({'quarter': q, 'metric': m, 'frozen_value': frozen, 'normalized_unit': UNIT[m],
                       'frozen_display_step': step, 'original_checked_status': 'checked' if original else 'unavailable',
                       'original_publication_date': s['publication_date'], 'original_publication_basis': s['publication_date_basis'],
                       'original_time_value': s['time_value'], 'original_time_basis': s['time_basis'],
                       'original_source_attempt_url': s['url'],
                       **flatten_observation('original', original, sources, m),
                       **flatten_observation('finer_or_later_corroboration', fine, sources, m),
                       'best_checked_value': value, 'best_minus_frozen': delta,
                       'original_headline_rounding_compatible': oc,
                       'best_vs_frozen_rounding_compatible': compatible,
                       'discrepancy_classification': classification,
                       'precision_timing': 'later_document' if later else 'same_document_or_same_date' if fine else 'no_finer_value_confirmed',
                       'filed_metric_name': name, 'definition': detail, 'notes': x['notes'],
                       'treatment': 'descriptive_source_audit_no_replacement', 'as_of': data['as_of']})
    coverage = []
    for q in QUARTERS:
        rows = [r for r in ledger if r['quarter'] == q]
        coverage.append({'quarter': q, 'scope': '|'.join(METRICS), 'cells_audited_or_unavailable': len(rows),
                         'original_cells_checked': sum(r['original_checked_status'] == 'checked' for r in rows),
                         'original_cells_unavailable': sum(r['original_checked_status'] == 'unavailable' for r in rows),
                         'finer_or_later_corroboration_cells': sum(r['finer_or_later_corroboration_value'] is not None for r in rows),
                         'unresolved_cells': sum(r['discrepancy_classification'] == 'unresolved' for r in rows),
                         'definition_difference_cells': sum(r['discrepancy_classification'] == 'definition_difference' for r in rows),
                         'unrelated_wide_panel_columns': 'out_of_scope'})
    sensitivities = []
    for r in ledger:
        if r['metric'] != 'gbv_musd':
            continue
        known = r['finer_or_later_corroboration_first_known_date']
        delta = r['best_minus_frozen'] if known else None
        for lag, weight in ((1, 2/3), (2, 1/3)):
            sensitivities.append({'booking_quarter': r['quarter'], 'target_quarter': None, 'scenario': 'normalized_single_GBV_precision_difference',
                                  'lag': lag, 'weight': weight, 'delta_gbv_musd': delta,
                                  'dR_dGBV_div_lambda': weight, 'delta_revenue_div_lambda_musd': weight*delta if delta is not None else None,
                                  'lambda_decimal': None, 'dR_dGBV': None, 'delta_revenue_musd': None,
                                  'first_known_date': known, 'evidence_status': r['discrepancy_classification'] if known else 'finer_value_unavailable',
                                  'lambda_basis': 'No compatible seasonal coefficient attached; normalized derivative only',
                                  'treatment': 'descriptive_sensitivity_no_refit_or_forecast_replacement'})
    coefficient = float(lambdas[0]['lambda_pct'])/100
    contribution = []
    for k in lambdas:
        r = next(r for r in ledger if r['quarter'] == k['booking_quarter'] and r['metric'] == 'gbv_musd')
        weight = 2/3 if k['booking_quarter'] == '2026Q2' else 1/3
        delta = r['best_minus_frozen']
        contribution.append(weight*delta)
        sensitivities.append({'booking_quarter': r['quarter'], 'target_quarter': '2026Q3', 'scenario': 'inherited_current_Q3_lambda_held_fixed',
                              'lag': 1 if weight > .5 else 2, 'weight': weight, 'delta_gbv_musd': delta,
                              'dR_dGBV_div_lambda': weight, 'delta_revenue_div_lambda_musd': weight*delta,
                              'lambda_decimal': coefficient, 'dR_dGBV': coefficient*weight, 'delta_revenue_musd': coefficient*weight*delta,
                              'first_known_date': r['finer_or_later_corroboration_first_known_date'],
                              'evidence_status': 'single_current_origin_arithmetic_illustration_not_validation',
                              'lambda_basis': 'cohort_fx_v2/results_v2/kernel_inputs.csv; inherited ewm, n=5; information_date='+k['information_date'],
                              'treatment': 'descriptive_sensitivity_no_refit_or_forecast_replacement'})
    sensitivities.append({'booking_quarter': '2026Q1|2026Q2', 'target_quarter': '2026Q3', 'scenario': 'combined_current_Q3_held_fixed',
                          'delta_revenue_div_lambda_musd': sum(contribution), 'lambda_decimal': coefficient,
                          'delta_revenue_musd': coefficient*sum(contribution), 'first_known_date': '2026-08-06',
                          'evidence_status': 'n1_arithmetic_illustration_not_historical_validation',
                          'lambda_basis': 'Same inherited current Q3 ewm lambda; all other inputs held fixed',
                          'treatment': 'descriptive_sensitivity_no_refit_or_forecast_replacement'})
    for row in sensitivities:
        # first_known_date concerns the observed source value, never the later complete analysis.
        row['source_value_first_known_date'] = row.pop('first_known_date')
        row['analysis_information_date'] = data['as_of']
        row['lambda_information_date'] = max(k['information_date'] for k in lambdas) if row.get('lambda_decimal') is not None else None
        row['information_date_basis'] = 'Audit analysis assembled on analysis_information_date; source and inherited coefficient dates remain separate'
    supplements = [{**{k: v for k, v in x.items() if k != 'observation'},
                    **flatten_observation('observation', x['observation'], sources, x['metric']),
                    'derivation_json': json.dumps(x['observation'].get('derivation'), sort_keys=True)} for x in data['supplements']]
    derived = [{ 'quarter': x['quarter'], 'metric': x['metric'],
                 'derivation_json': json.dumps(x['fine']['derivation'], sort_keys=True),
                 'first_known_date': x['fine']['first_known_date']} for x in data['facts'] if x['fine'] and 'derivation' in x['fine']]
    earliest_origin = min(r['guide_date'] for r in calendar if r['fiscal_quarter'] >= '2022Q4' and r['guide_date'])
    summary = {'as_of': data['as_of'], 'quarters': len(coverage), 'metric_cells': len(ledger),
               'primary_scope': list(METRICS), 'other_wide_panel_columns': 'out_of_scope',
               'original_checked_cells': sum(r['original_checked_status'] == 'checked' for r in ledger),
               'original_unavailable_cells': sum(r['original_checked_status'] == 'unavailable' for r in ledger),
               'classification_counts': dict(sorted(Counter(r['discrepancy_classification'] for r in ledger).items())),
               'sources': len(sources), 'primary_source_texts_checked': sum(s['access_status'] == 'checked_primary_text' for s in sources.values()),
               'unavailable_source_texts': [s['id'] for s in sources.values() if s['access_status'] != 'checked_primary_text'],
               'gbv_quarters_with_finer_or_later_corroboration': sum(r['metric'] == 'gbv_musd' and r['finer_or_later_corroboration_value'] is not None for r in ledger),
               'current_Q3_held_fixed_lambda_decimal': coefficient,
               'current_Q3_weighted_input_delta_musd': sum(contribution),
               'current_Q3_arithmetic_delta_revenue_musd': coefficient*sum(contribution),
               'current_illustration_n': 1, 'fitted_parameters': 0, 'revised_forecasts': 0,
               'operational_policy': 'Retain inherited fixed 2/3-1/3 seasonal estimation policy; free-w promotion FAIL unchanged',
               'IPO_calendar_gap': {'frozen_approximate_date': '2020-11-15', 'verified_index_filed_date': sources['2020Q3_filing']['publication_date'],
                                    'same_day_availability_validated': False, 'earliest_W1_guide_origin': earliest_origin,
                                    'both_dates_before_all_W1_origins': max('2020-11-15', sources['2020Q3_filing']['publication_date']) < earliest_origin,
                                    'effect': 'No refit performed; one-day date correction alone precedes all W1 origins; original value availability remains unverified'},
               'limitations': data['limitations']+['Revenue precision can affect historical outcomes or fitted coefficients; such refit effects are deliberately not quantified by the held-lambda GBV derivative.',
                                                 '2025Q2 GBV primary presentation conflict and 2022Q2 later rounded history discrepancy remain unresolved.',
                                                 'No exact SEC acceptance time recovered for Q2 2026. Date-only filing basis is inherited; no intraday claim.']}
    return {'discrepancy_ledger.csv': ledger, 'quarter_coverage.csv': coverage, 'kernel_sensitivity.csv': sensitivities,
            'source_manifest.csv': list(sources.values()), 'supplemental_observations.csv': supplements,
            'derived_values.csv': derived}, summary


def run(out, inputs=INPUTS):
    out = Path(out)
    if out.exists():
        raise FileExistsError(f'Immutable outputs: destination already exists: {out}')
    data, panel, lambdas, calendar, manifest = load(inputs)
    tables, summary = build(data, panel, lambdas, calendar)
    out.mkdir(parents=True, exist_ok=False)
    for name, rows in tables.items():
        write_csv(out/name, rows)
    (out/'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    (out/'input_manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    (out/'output_manifest.json').write_text(json.dumps({p.name: sha(p) for p in sorted(out.iterdir())}, indent=2)+'\n', encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path, help='New directory, must not already exist')
    parser.add_argument('--inputs', default=INPUTS, type=Path, help='Frozen compact source-facts directory')
    args = parser.parse_args()
    print(json.dumps(run(args.out, args.inputs), indent=2, sort_keys=True))
