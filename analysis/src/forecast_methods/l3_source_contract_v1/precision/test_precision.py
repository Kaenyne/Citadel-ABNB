import copy
import importlib.util
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('sc_a_precision_run', Path(__file__).with_name('run.py'))
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)


def inputs():
    d, p, l, c, _ = r.load()
    return d, p, l, c


def cell(d, q, m='gbv_musd'):
    return next(x for x in d['facts'] if x['quarter'] == q and x['metric'] == m)


def test_exact_scope_and_negative_findings():
    tables, s = r.build(*inputs())
    assert s['quarters'] == 24 and s['metric_cells'] == 96
    assert s['original_checked_cells'] == 92 and s['original_unavailable_cells'] == 4
    rows = tables['discrepancy_ledger.csv']
    q4 = next(x for x in rows if x['quarter']=='2020Q4' and x['metric']=='revenue_musd')
    assert q4['discrepancy_classification'] == 'unresolved'
    assert q4['best_minus_frozen'] == pytest.approx(.164)
    gbv = next(x for x in rows if x['quarter']=='2025Q2' and x['metric']=='gbv_musd')
    assert gbv['best_minus_frozen'] == -53 and not gbv['best_vs_frozen_rounding_compatible']
    assert gbv['discrepancy_classification'] == 'unresolved'


@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'wrong_metric', 'panel_duplicate'])
def test_coverage_rejects(defect):
    d,p,l,c = inputs()
    if defect == 'missing': d['facts'].pop()
    if defect == 'duplicate': d['facts'][-1] = copy.deepcopy(d['facts'][0])
    if defect == 'wrong_metric': d['facts'][0]['metric'] = 'take_rate_pct'
    if defect == 'panel_duplicate': p[-1] = p[0]
    with pytest.raises(ValueError): r.validate(d,p,l,c)


@pytest.mark.parametrize('metric,value,unit,answer', [('gbv_musd',27.2,'USD_billion',27200),('revenue_musd',859264,'USD_thousand',859.264)])
def test_units(metric,value,unit,answer):
    assert r.normalize(metric,value,unit) == pytest.approx(answer)


@pytest.mark.parametrize('unit', ['USD','USD_per_night','USD_billion'])
def test_unit_mismatch_rejected(unit):
    with pytest.raises(ValueError): r.normalize('nights_m',148.3,unit)


def test_later_precision_cannot_be_backdated():
    d,p,l,c = inputs()
    cell(d,'2024Q1')['fine']['first_known_date'] = '2024-05-08'
    with pytest.raises(ValueError,match='backdated'): r.validate(d,p,l,c)


def test_later_derived_requires_both_sources():
    d,p,l,c = inputs()
    o = cell(d,'2024Q4')['fine']
    o['source_id'] = '2024Q4_filing'
    o['first_known_date'] = '2025-02-13'
    with pytest.raises(ValueError,match='precedes'): r.validate(d,p,l,c)


def test_derivation_rounding_bounds_and_arithmetic():
    d,p,l,c = inputs()
    cell(d,'2025Q4')['fine']['precision_step'] = 1
    with pytest.raises(ValueError,match='rounding'): r.validate(d,p,l,c)
    d,p,l,c = inputs()
    cell(d,'2025Q4')['fine']['value'] += 1
    with pytest.raises(ValueError,match='arithmetic'): r.validate(d,p,l,c)


def test_coarser_filing_nights_not_finer():
    d,p,l,c = inputs()
    x = cell(d,'2026Q2','nights_m')
    x['fine'] = copy.deepcopy(next(z['observation'] for z in d['supplements'] if z['quarter']=='2026Q2'))
    with pytest.raises(ValueError,match='not more precise'): r.validate(d,p,l,c)


def test_q1_original_precision_and_later_corroboration_dates_distinct():
    d,p,l,c = inputs()
    assert cell(d,'2026Q1')['fine']['first_known_date'] == '2026-05-07'
    later = next(x for x in d['supplements'] if x['quarter']=='2026Q1' and x['metric']=='gbv_musd')
    assert later['observation']['first_known_date'] == '2026-08-06'
    assert cell(d,'2026Q1')['fine']['value'] == later['observation']['value'] == 29187


def test_held_lambda_algebra_and_no_revenue_refit_effect():
    tables,s = r.build(*inputs())
    assert s['fitted_parameters'] == 0 and s['revised_forecasts'] == 0
    assert s['current_Q3_weighted_input_delta_musd'] == 27
    assert s['current_Q3_arithmetic_delta_revenue_musd'] == pytest.approx(27*.172548908953)
    rows=tables['kernel_sensitivity.csv']
    assert len(rows)==51
    assert sum(x['delta_revenue_musd'] for x in rows if x['scenario']=='inherited_current_Q3_lambda_held_fixed') == pytest.approx(4.658820541731)
    assert all(x['delta_revenue_musd'] is None for x in rows if x['scenario']=='normalized_single_GBV_precision_difference')


@pytest.mark.parametrize('defect', ['unit','weight','lambda'])
def test_inherited_basis_integrity(defect):
    d,p,l,c = inputs()
    if defect=='unit': l[0]['gbv_reported_usd']='27200'
    if defect=='weight': l[0]['kernel_coefficient']='.5'
    if defect=='lambda': l[1]['lambda_pct']='17.24'
    with pytest.raises(ValueError): r.validate(d,p,l,c)


def test_definition_and_IPO_gap_preserved():
    t,s = r.build(*inputs())
    assert s['IPO_calendar_gap']['both_dates_before_all_W1_origins']
    assert not s['IPO_calendar_gap']['same_day_availability_validated']
    assert 'Experiences' in r.definition('2025Q1','nights_m')[0]
    assert 'Seats' in r.definition('2025Q2','nights_m')[0]
    early=[x for x in t['discrepancy_ledger.csv'] if x['quarter']<'2021Q1' and x['metric']=='adr_usd']
    assert all(x['discrepancy_classification']=='definition_difference' for x in early)


def test_existing_output_guard_before_any_write(tmp_path):
    marker=tmp_path/'keep';marker.write_text('preserve')
    with pytest.raises(FileExistsError): r.run(tmp_path)
    assert marker.read_text()=='preserve' and len(list(tmp_path.iterdir()))==1


def test_deterministic_offline_and_hashes(tmp_path):
    a,b=tmp_path/'a',tmp_path/'b'
    r.run(a);r.run(b)
    assert {x.name:r.sha(x) for x in a.iterdir()}=={x.name:r.sha(x) for x in b.iterdir()}
    manifest=json.loads((a/'output_manifest.json').read_text())
    assert all(r.sha(a/k)==v for k,v in manifest.items())


def test_input_mutation_detected(tmp_path):
    for f in r.INPUTS.iterdir(): (tmp_path/f.name).write_bytes(f.read_bytes())
    with (tmp_path/'frozen_panel.csv').open('a') as f: f.write('tamper')
    with pytest.raises(ValueError,match='checksum'): r.load(tmp_path)


@pytest.mark.parametrize('attack', ['lambda_future','lambda_before_known','panel_nan','unavailable_source','unavailable_derivation_parent','overflow','bool'])
def test_independent_review_adversarial_integrity(attack):
    d,p,l,c=inputs()
    if attack=='lambda_future':
        for row in l:
            row['information_date']='2027-01-01';row['lambda_knowable_from']='2027-01-01'
    if attack=='lambda_before_known': l[0]['kernel_origin']='2024-01-01'
    if attack=='panel_nan': next(x for x in p if x['quarter']=='4Q20')['revenue_musd']='nan'
    if attack=='unavailable_source': next(x for x in d['sources'] if x['id']=='2020Q4_letter')['access_status']='unavailable_text_index_checked'
    if attack=='unavailable_derivation_parent': next(x for x in d['sources'] if x['id']=='2024Q4_filing')['access_status']='unavailable_text_index_checked'
    if attack=='overflow': cell(d,'2020Q4')['original']['value']=1e308
    if attack=='bool': cell(d,'2020Q4','nights_m')['original']['value']=True
    with pytest.raises(ValueError): r.validate(d,p,l,c)


def test_analysis_date_and_aggregate_unit_are_explicit():
    t,s=r.build(*inputs())
    assert all(x['normalized_unit']=='million_aggregate_booked_units' for x in t['discrepancy_ledger.csv'] if x['metric']=='nights_m')
    for row in t['kernel_sensitivity.csv']:
        assert row['analysis_information_date']=='2026-09-14'
        assert 'first_known_date' not in row
        if row.get('lambda_decimal') is not None:
            assert row['lambda_information_date']=='2026-09-13'
            assert row['source_value_first_known_date']<'2026-09-13'
