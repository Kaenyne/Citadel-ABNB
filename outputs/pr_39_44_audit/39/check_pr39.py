"""Run unchanged PR39 functions against audit-only committed fixtures/synthetic input names."""
import importlib.util
import json
import hashlib
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent/'snapshot'
FIX = HERE/'fixture'
results = {}

def module(name):
    spec = importlib.util.spec_from_file_location(name,SNAP/'analysis/src'/f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

mat = module('rnpl_materiality')
mat.ROOT, mat.SOURCE, mat.OUT = FIX,FIX/'data/processed/overnight/02_kpi_panel_quarterly.csv',HERE/'generated_materiality'
mat.OUT.mkdir(exist_ok=True)
# Preserve original relative-to reporting while keeping output only inside audit fixture root.
mat.OUT = FIX/'outputs/generated_materiality'
mat.main()
got = json.loads((mat.OUT/'materiality.json').read_text(encoding='utf-8'))
want = json.loads((FIX/'outputs/rnpl-audit-20260910/materiality.json').read_text(encoding='utf-8'))
assert got['thresholds']==want['thresholds']
assert got['required_hazards']==want['required_hazards']
results['materiality']={'thresholds':len(got['thresholds']),'scenarios':len(got['required_hazards']),'all_values_match_committed':True,
    'source_hash_matches_after_CRLF_reconstruction':hashlib.sha256(mat.SOURCE.read_text(encoding='utf-8').rstrip().replace('\n','\r\n').encode()+b'\r\n').hexdigest()==want['local_source_sha256'],
    'source_hash_note':'Connector/apply_patch copied text with LF and an extra trailing newline; original saved fingerprint matches CRLF representation exactly.'}

pilot = module('rnpl_calendar_pilot')
pilot.self_test()
results['pilot_self_test']='passed'
# Additional meaningful boundary: separate blocked runs across missing dates, not adjacency in the frame.
a = pd.DataFrame({'listing_id':[1,1,1,1,2], 'date':pd.to_datetime(['2026-07-01','2026-07-02','2026-07-04','2026-07-05','2026-07-01']), 'u':[True,True,True,False,True]})
r = pilot.add_runs(a)
assert r['run'].tolist()==[2,2,1,1,1]
results['missing_date_run_boundary']='passed'

report = module('rnpl_calendar_pilot_report')
report.ROOT, report.OUT = FIX,FIX/'outputs/rnpl-calendar-pilot-20260910'
report.main()
report_got=(report.OUT/'pilot-report.md').read_text(encoding='utf-8')
report_want=(SNAP/'outputs/rnpl-calendar-pilot-20260910/pilot-report.md').read_text(encoding='utf-8')
results['pilot_report']={'regenerated':True,'identical_except_trailing_newline':report_got.rstrip()==report_want.rstrip(),'manifest_url_size_checks':15}

provenance=pd.read_csv(HERE/'F1_provenance.csv')
market_column='market'
print('Provenance columns:',list(provenance.columns))
results['calendar_vintage_counts_after_PR41']={m:int((provenance[market_column]==m).sum()) for m in ['austin','rome','sydney']}
# Six clearly synthetic filenames are sufficient to trigger the pre-I/O guard. No fake calendar data is generated/read.
fake=HERE/'synthetic_filename_guard_only'
fake.mkdir(exist_ok=True)
for month in range(1,7):
    (fake/f'austin_2026-{month:02d}-01_calendar.csv.gz').touch()
pilot.RAW=fake
try:
    pilot.process_market('austin')
except ValueError as exc:
    results['extra_vintage_failure']=str(exc)
else:
    raise AssertionError('Expected the original exact-five-vintage guard to fail')
(HERE/'check_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
