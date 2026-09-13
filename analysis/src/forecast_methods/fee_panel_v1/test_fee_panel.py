import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

spec=importlib.util.spec_from_file_location('fee_panel_consumer',Path(__file__).with_name('run.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def panel(theta=.7, wave='sep'):
    rows=[]
    for i in range(40):
        country='MX' if i%3==0 else 'US'
        region='non_eea' if i<20 else 'eea_ch'
        treated=region==('non_eea' if wave=='sep' else 'eea_ch')
        for window in ['W1','W2']:
            for j,date in enumerate(m.WAVES[wave]):
                shift=(theta*m.neutral_log(.16 if country=='MX' else .155)*treated+.01) if j else 0
                rows.append(dict(listing_id=str(i),checkin='2026-11-13' if window=='W1' else '2026-12-11',
                   checkout='2026-11-16' if window=='W1' else '2026-12-14',nights=3,city='test',
                   country_iso2=country,host_region_guess=region,room_type='entire',bedroom_bucket='2',
                   host_class='individual',stay_window=window,capture_date=date,currency='USD',
                   nightly_price=(100+i)*np.exp(shift)))
    return pd.DataFrame(rows)

@pytest.mark.parametrize('wave',['sep','oct'])
def test_exact_log_theta(wave):
    result,table=m.estimate(panel(wave=wave),m.WAVES[wave],wave)
    assert result['theta']==pytest.approx(.7,abs=1e-10)
    assert result['status']=='association_precision_pass'
    assert result['causal_identified'] is False
    assert table.retention.min()==1

def test_mexico_denominator():
    assert m.neutral_log(.16)==pytest.approx(np.log(.97/.84))
    assert m.neutral_log(.16)>m.neutral_log(.155)
    assert m.neutral_log(.155)!=pytest.approx(.97/.845-1)

def test_overlap_failure_not_pooled_away():
    d=panel();d.loc[d.listing_id.eq('0'),'city']='small_stratum'
    d=d[~(d.listing_id.eq('0') & d.capture_date.ne('2026-09-14'))]
    result,_=m.estimate(d,m.WAVES['sep'],'sep')
    assert result['status']=='blocked_overlap'

def test_unknown_residence_excluded():
    d=panel(); d.loc[d.listing_id.eq('0'),'host_region_guess']='unknown'
    result,_=m.estimate(d,m.WAVES['sep'],'sep')
    assert result['clusters']==39
    assert result['theta']==pytest.approx(.7)

def test_one_arm_refused():
    d=panel(); d=d[d.host_region_guess.eq('non_eea')]
    result,_=m.estimate(d,m.WAVES['sep'],'sep')
    assert result['status']=='blocked_arm_support'

def test_missing_wave_not_zero():
    d=panel();d=d[d.capture_date.ne('2026-09-18')]
    result,_=m.estimate(d,m.WAVES['sep'],'sep')
    assert result['status'].startswith('blocked')
    assert 'theta' not in result

def captures(tmp_path,change=None):
    d=panel().iloc[:3].copy()
    d['captured_at']=d.capture_date+'T13:00:00Z';d['parse_status']='ok'
    metadata=d.drop_duplicates(m.KEY).copy();metadata['dump_date']='2026-08-25'
    if change:
        change(d)
    path=tmp_path/'capture.csv';d.to_csv(path,index=False)
    return path,metadata[m.KEY+m.META+['dump_date']]

def test_future_capture_rejected(tmp_path):
    p,meta=captures(tmp_path)
    with pytest.raises(ValueError,match='future'):
        m.load_captures([p],meta,'2026-09-15')

def test_duplicate_capture_rejected(tmp_path):
    p,meta=captures(tmp_path)
    with pytest.raises(ValueError,match='duplicate capture'):
        m.load_captures([p,p],meta,'2026-09-19')

def test_currency_change_rejected(tmp_path):
    p,meta=captures(tmp_path,lambda d:d.loc.__setitem__((d.index[1],'currency'),'EUR'))
    with pytest.raises(ValueError,match='currency changes'):
        m.load_captures([p],meta,'2026-09-19')

def test_missing_currency_rejected(tmp_path):
    p,meta=captures(tmp_path,lambda d:d.loc.__setitem__((d.index[1],'currency'),''))
    with pytest.raises(ValueError,match='currency'):
        m.load_captures([p],meta,'2026-09-19')

def test_invalid_price_excluded(tmp_path):
    p,meta=captures(tmp_path,lambda d:d.loc.__setitem__((d.index[1],'nightly_price'),-1))
    assert len(m.load_captures([p],meta,'2026-09-19'))==2

def test_output_immutable(tmp_path):
    with pytest.raises(FileExistsError):
        m.run([],Path('unused'),'2026-09-13',tmp_path)

def test_unknown_room_stratum_still_gates_known_residence():
    d=panel();affected=d.listing_id.astype(int).lt(8)
    d.loc[affected,'room_type']='unknown'
    d=d[~(affected & d.capture_date.ne('2026-09-14'))]
    result,table=m.estimate(d,m.WAVES['sep'],'sep')
    assert result['status']=='blocked_overlap'
    bad=table[table.population.eq('known_residence_primary') & table.stratum.eq('room_type') & table.value.eq('unknown')]
    assert bad.primary_gate.all()
    assert bad.retention.eq(0).all()

def test_unknown_residence_descriptive_overlap_retained():
    d=panel();d.loc[d.listing_id.eq('0'),'host_region_guess']='unknown'
    result,table=m.estimate(d,m.WAVES['sep'],'sep')
    unknown=table[table.stratum.eq('host_region_guess') & table.value.eq('unknown')]
    assert len(unknown)==3
    assert unknown.population.eq('all_descriptive').all()
    assert not unknown.primary_gate.any()

def test_missing_listing_country_is_not_standard_fee():
    d=panel();d.loc[d.country_iso2.eq('MX'),'country_iso2']=''
    with pytest.raises(ValueError,match='fee regime'):
        m.estimate(d,m.WAVES['sep'],'sep')

def test_metadata_after_pre_capture_rejected(tmp_path):
    p,meta=captures(tmp_path);meta['dump_date']='2026-09-18'
    with pytest.raises(ValueError,match='metadata unavailable'):
        m.load_captures([p],meta,'2026-09-19')

def test_missing_metadata_date_rejected(tmp_path):
    p,meta=captures(tmp_path);meta['dump_date']=''
    path=tmp_path/'metadata.csv';meta.to_csv(path,index=False)
    with pytest.raises(ValueError,match='metadata'):
        m.load_metadata(path,'2026-09-19')

def test_new_valid_wave_metadata_does_not_redate_historical_dryrun(tmp_path):
    import json
    _,meta=captures(tmp_path);meta['dump_date']='2026-09-13'
    path=tmp_path/'new_metadata.csv';meta.to_csv(path,index=False)
    out=tmp_path/'new_output'
    m.run([],path,'2026-09-19',out)
    summary=json.loads((out/'summary.json').read_text())
    assert summary['dry_run']['residence_known_rows']==6
    manifest=pd.read_csv(out/'source_manifest.csv')
    assert manifest.path.str.contains('sample_ids.csv').any()
