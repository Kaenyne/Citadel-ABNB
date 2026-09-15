"""Bind additive integration/event repairs and the rendered memo; no statistical refit."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
D=ROOT/'data/processed/forecast_methods/gbv_event_v1'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

old=D/'events_v1/run_v2';new=D/'events_v1/run_v3'
same_names=['associations.csv','current_print_control.csv','cushion_training.csv','guide_tieout.csv',
            'influence.csv','sign_groups.csv','vendor_sensitivity.csv','pre_event_forecast_join.csv','return_tieout.csv']
checks=[{'file':n,'same_bytes':sha(old/n)==sha(new/n),'sha256':sha(new/n)} for n in same_names]
assert all(r['same_bytes'] for r in checks)
a,b=rows(old/'event_panel.csv'),rows(new/'event_panel.csv')
assert len(a)==len(b)==23
fields=set(a[0])&set(b[0])-{'primary_eligibility','current_consensus_status'}
unchanged_cells=sum(x[k]==y[k] for x,y in zip(a,b) for k in fields)
assert unchanged_cells==len(a)*len(fields)
modelpath=D/'integration_v2/model.json';model=json.loads(modelpath.read_text())
assert all(r['source_role'] in ('current','pit_history') for r in model['comparisons'])
assert all('break_even_conversion_given_our_gbv' in r for r in model['comparisons'])
assert all('implied_street_conversion' not in r for r in model['comparisons'])
for filename,digest in model['source_hashes'].items():assert sha(ROOT/filename)==digest
assert model['gbv_inputs'][0]['information_date']=='2026-05-07'
raw=(ROOT/'data/processed/forecast_methods/returns_v1/ohlc_daily.csv').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='a94c35e2c70f5bc9ce4b5bd85343fed199ac1e941b94d287bb3ee7780b799286'
assert hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()=='5b03005c30b1793e2d146e6a76fc352ecee56b7fbaf0e9f737bd479652b7a253'
bound=[modelpath,new/'receipt.json',new/'event_panel.csv',D/'events_v1/canonical_v1.json',
       ROOT/'analysis/src/forecast_methods/gbv_event_v1/events/run.py',
       ROOT/'analysis/src/forecast_methods/gbv_event_v1/events/test_events.py',D/'sources_v1/review_v2/receipt.json']
receipt={'verdict':'PASS bounded repairs and unchanged arithmetic; source readiness remains PARTIAL',
         'unchanged_csvs':checks,'unchanged_event_cells':unchanged_cells,
         'event_metadata_changes':'two raw source timestamp columns and eligibility basis labels',
         'manual_timestamp_code_review':'Raw timestamp preserved. Date-only same-day exception isolated; aware timestamps strictly before 16:00 America/New_York; naive/exact-close/post-close rejected. Existing date-only inputs numerically unchanged. Owning-agent tests report 12 passed.',
         'independent_arithmetic':json.loads((D/'sources_v1/review_v2/receipt.json').read_text()),
         'model_repairs':'current/pit_history role filter; conditional break-even conversion name; true Q1 publication date; all nine transitive source hashes checked',
         'source_precision':'CRLF working hash and retained LF hash reconcile without data change',
         'remaining_limits':['No held real intraday event panel','No directly observed guide-expectations panel','No historical forecast promotion','Current EWM scenario differs from ex-COVID historical audit variant','No calibrated current probability or demonstrated executable trade'],
         'bindings':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in bound}}
dest=D/'sources_v1/closure_v3.json'
with dest.open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
print(json.dumps({'verdict':receipt['verdict'],'unchanged_csvs':len(checks),'unchanged_event_cells':unchanged_cells,'receipt':str(dest)}))
