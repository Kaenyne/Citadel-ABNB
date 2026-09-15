import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

spec=importlib.util.spec_from_file_location('l3_bundle',Path(__file__).with_name('bundle.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

def row():
    return dict(package='cohort_fx',quarter='2026Q3',metric='replacement',scenario='u20',value=1.,lower=np.nan,upper=np.nan,
                units='USD',information_date='2026-09-13',evidence_status='scenario_only',source_reference='weights.csv',
                treatment='incremental_replacement',baseline_being_replaced='K0 reported booking baseline',
                embedded_fx='booking_fx',adoption_status='pending_L4_compatibility_review')

def test_valid_sensitivity_and_missing_estimate():
    b.validate(pd.DataFrame([row()]))
    r=row();r['value']=np.nan;r['evidence_status']='unavailable';r['treatment']='descriptive'
    b.validate(pd.DataFrame([r]))

@pytest.mark.parametrize('field,value',[('value',np.inf),('information_date','2026-09-14'),('quarter','2026Q5'),
                         ('source_reference',''),('adoption_status','adopted'),('baseline_being_replaced','none'),('embedded_fx','not_applicable')])
def test_invalid_input_rejected(field,value):
    r=row();r[field]=value
    with pytest.raises(ValueError):b.validate(pd.DataFrame([r]))

def test_duplicate_and_bounds_rejected():
    with pytest.raises(ValueError):b.validate(pd.DataFrame([row(),row()]))
    r=row();r.update(lower=2,upper=1)
    with pytest.raises(ValueError):b.validate(pd.DataFrame([r]))

def test_existing_bundle_never_overwritten(tmp_path):
    with pytest.raises(FileExistsError):b.build(tmp_path,{})

def test_normalize_preserves_nclh_metadata_without_duplicate_columns(tmp_path,monkeypatch):
    monkeypatch.setattr(b,'ROOT',tmp_path)
    r=row();r.update(quarter='2023Q1-2026Q2',information_date='2026-07-30T10:30:00Z',
                    treatment='No ABNB forecast adjustment',replacement_vs_incremental='neither; diagnostic')
    r['lower_bound']=.5;r['upper_bound']=2.;r.pop('lower');r.pop('upper')
    p=tmp_path/'inputs.csv';pd.DataFrame([r]).to_csv(p,index=False)
    normalized=b.normalize(p,'nclh')
    assert normalized.columns.is_unique
    assert normalized.iloc[0].quarter=='historical'
    assert normalized.iloc[0].source_period=='2023Q1-2026Q2'
    assert normalized.iloc[0].information_date=='2026-09-13'
    assert normalized.iloc[0].source_information_date=='2026-07-30T10:30:00Z'
    assert normalized.iloc[0].lower==.5
    b.validate(normalized)

def test_unexpected_nested_checksum_file_rejected(tmp_path):
    import json,hashlib
    pd.DataFrame([row()]).to_csv(tmp_path/'l4_inputs.csv',index=False)
    manifest={'l4_inputs.csv':hashlib.sha256((tmp_path/'l4_inputs.csv').read_bytes()).hexdigest()}
    (tmp_path/'SHA256SUMS.json').write_text(json.dumps(manifest))
    b.verify(tmp_path)
    nested=tmp_path/'payload'/'nested';nested.mkdir(parents=True)
    (nested/'SHA256SUMS.json').write_text('{}')
    with pytest.raises(AssertionError,match='checksum'):b.verify(tmp_path)

def test_uncommitted_research_source_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(b.subprocess,'check_output',lambda *args,**kwargs:'?? new_source.py\n')
    with pytest.raises(ValueError,match='Commit'):
        b.build(tmp_path/'new_bundle',{})

def test_ignored_source_is_not_a_committed_blob(tmp_path,monkeypatch):
    import subprocess
    monkeypatch.setattr(b,'ROOT',tmp_path)
    p=tmp_path/'ignored.csv';p.write_text('x\n1\n')
    def missing(*args,**kwargs):raise subprocess.CalledProcessError(128,args[0])
    monkeypatch.setattr(b.subprocess,'check_output',missing)
    with pytest.raises(ValueError,match='not committed'):b.committed_bytes(p)

def test_changed_source_not_hidden_by_clean_status(tmp_path,monkeypatch):
    monkeypatch.setattr(b,'ROOT',tmp_path)
    p=tmp_path/'input.csv';p.write_bytes(b'x\n2\n')
    monkeypatch.setattr(b.subprocess,'check_output',lambda *args,**kwargs:b'x\n1\n')
    with pytest.raises(ValueError,match='differ'):b.committed_bytes(p)
