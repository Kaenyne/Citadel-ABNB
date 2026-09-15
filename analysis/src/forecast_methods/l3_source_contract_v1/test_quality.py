import copy
import importlib.util
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('source_contract_quality',Path(__file__).with_name('quality.py'))
q=importlib.util.module_from_spec(s);s.loader.exec_module(q)

def fixture():
    old={'package':'fx','quarter':'2026Q3','metric':'retiming','scenario':'u20','value':'-2.434000',
         'lower':'','upper':'','units':'USD_millions','evidence_status':'scenario_only_unidentified',
         'information_date':'2026-09-13','source_reference':'frozen.csv','embedded_fx':'booking_rate'}
    new={**old,'consumption_status':'usable_as_conditional_scenario'}
    return old,new

def test_condition_with_exact_original_value_and_metadata():
    a,b=fixture();assert q.consumption([a],[b])['all_original_fields_exact']

@pytest.mark.parametrize('field,value',[('value','-2.434'),('information_date','2026-09-14'),
                                        ('embedded_fx','none'),('units','USD')])
def test_no_silent_value_unit_vintage_or_fx_rewrite(field,value):
    a,b=fixture();b[field]=value
    with pytest.raises(ValueError,match='lexeme'):q.consumption([a],[b])

def test_no_observation_status_for_assumed_exposure():
    a,b=fixture();b['consumption_status']='usable_as_observed_input'
    with pytest.raises(ValueError,match='promoted'):q.consumption([a],[b])

def test_missing_estimate_cannot_become_conditional_numeric_input():
    a,b=fixture();a['value']=b['value']=''
    with pytest.raises(ValueError,match='Unavailable'):q.consumption([a],[b])
    b['consumption_status']='unavailable';q.consumption([a],[b])

def test_missing_or_duplicate_rows_rejected():
    a,b=fixture()
    with pytest.raises(ValueError,match='coverage'):q.consumption([a],[])
    with pytest.raises(ValueError,match='Duplicate'):q.consumption([a],[b,copy.copy(b)])

