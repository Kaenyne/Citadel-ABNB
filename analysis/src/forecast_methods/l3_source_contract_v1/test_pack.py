import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('source_contract_pack',Path(__file__).with_name('pack.py'))
p=importlib.util.module_from_spec(s);s.loader.exec_module(p)

def test_existing_output_refused_before_any_source_access(tmp_path):
    with pytest.raises(FileExistsError):p.build(tmp_path/'missing',tmp_path)

def test_nested_manifest_is_not_exempt_from_integrity(tmp_path):
    (tmp_path/'fact.csv').write_bytes(b'x\n1\n')
    (tmp_path/'SHA256SUMS.json').write_text(json.dumps({'fact.csv':hashlib.sha256(b'x\n1\n').hexdigest()}))
    p.verify(tmp_path)
    nested=tmp_path/'payload';nested.mkdir();(nested/'SHA256SUMS.json').write_text('{}')
    with pytest.raises(ValueError,match='checksum'):p.verify(tmp_path)

def test_source_blobs_cannot_ignore_changed_working_bytes(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'ROOT',tmp_path)
    source=tmp_path/'fact.csv';source.write_bytes(b'x\n2\n')
    monkeypatch.setattr(p.preserve,'blobs',lambda ref,paths:{'fact.csv':b'x\n1\n'})
    with pytest.raises(ValueError,match='changed source'):p.committed([source],'committed-ref')

def acceptance_fixture(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'ROOT',tmp_path)
    names=['precision.md','accounting.md','consumption.md','facts.json']
    for name in names:(tmp_path/name).write_bytes(b'reviewed\n')
    monkeypatch.setattr(p.preserve,'blobs',lambda ref,paths:{Path(x).as_posix():b'reviewed\n' for x in paths})
    return {'status':'ACCEPTED_AFTER_INDEPENDENT_REVIEW',
            'reviews':[dict(package=k,author=a,reviewer=r,status='PASS',note=k+'.md')
                       for k,a,r in [('precision','adr_hotel','nclh'),('accounting','cohort_fx','adr_hotel'),
                                     ('consumption','nclh','cohort_fx')]],
            'bound_files':{x:hashlib.sha256(b'reviewed\n').hexdigest() for x in names}}

def test_closed_review_binds_required_facts(tmp_path,monkeypatch):
    a=acceptance_fixture(tmp_path,monkeypatch)
    assert p.validate_acceptance(a,'commit',[tmp_path/'facts.json'])==4
    a['bound_files'].pop('facts.json')
    with pytest.raises(ValueError,match='Required evidence'):p.validate_acceptance(a,'commit',[tmp_path/'facts.json'])

def test_self_approval_rejected(tmp_path,monkeypatch):
    a=acceptance_fixture(tmp_path,monkeypatch);a['reviews'][0]['reviewer']='adr_hotel'
    with pytest.raises(ValueError,match='self approval'):p.validate_acceptance(a,'commit',[])

def test_changed_review_binding_rejected(tmp_path,monkeypatch):
    a=acceptance_fixture(tmp_path,monkeypatch);a['bound_files']['facts.json']='0'*64
    with pytest.raises(ValueError,match='digest differs'):p.validate_acceptance(a,'commit',[])

def test_external_acceptance_path_rejected(tmp_path,monkeypatch):
    a=acceptance_fixture(tmp_path,monkeypatch);a['bound_files']['../outside.json']='0'*64
    with pytest.raises(ValueError,match='outside repository'):p.validate_acceptance(a,'commit',[])

def test_runtime_snapshots_are_required_outside_code_tree(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'ROOT',tmp_path)
    base=tmp_path/'data/processed/forecast_methods/l3_source_contract_v1'
    for directory,name in [('precision/inputs_v1','input_manifest.json'),('consumption/inputs_v2','manifest.json')]:
        target=base/directory;target.mkdir(parents=True);(target/name).write_text('{"files":{}}')
    inventory=base/'consumption/supplemental_path_inventory_v1.json';inventory.write_text('{}')
    assert len(p.runtime_inputs())==3
    inventory.unlink()
    with pytest.raises(FileNotFoundError,match='runtime input'):p.runtime_inputs()
