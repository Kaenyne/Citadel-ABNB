"""Create a local immutable supplement from reviewed, committed L3 source blobs."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import preserve

def digest(data):return hashlib.sha256(data).hexdigest()

def runtime_inputs():
    data=ROOT/'data/processed/forecast_methods/l3_source_contract_v1'
    inputs=[]
    for relative,manifest_name in [('precision/inputs_v1','input_manifest.json'),
                                   ('consumption/inputs_v2','manifest.json')]:
        directory=data/relative
        manifest=directory/manifest_name
        inputs.append(manifest)
        for name in json.loads(manifest.read_text(encoding='utf-8'))['files']:
            if Path(name).name!=name:raise ValueError('Compact runtime input must be a local file name')
            inputs.append(directory/name)
        inputs.extend(p for p in directory.iterdir() if p.is_file())
    inputs.append(data/'consumption/supplemental_path_inventory_v1.json')
    if any(not p.is_file() for p in inputs):raise FileNotFoundError('Required compact runtime input missing')
    return list(dict.fromkeys(inputs))

def committed(paths,commit):
    relative=[Path(p).resolve().relative_to(ROOT).as_posix() for p in paths]
    values=preserve.blobs(commit,relative)
    for p,v in values.items():
        if (ROOT/p).read_bytes()!=v:raise ValueError('Uncommitted or changed source: '+p)
    return values

def validate_acceptance(acceptance,commit,required):
    """Bind distinct independent reviewers and the exact local committed evidence."""
    if acceptance.get('status')!='ACCEPTED_AFTER_INDEPENDENT_REVIEW':
        raise ValueError('Closed independent acceptance is required')
    expected={'precision':('adr_hotel','nclh'),'accounting':('cohort_fx','adr_hotel'),
              'consumption':('nclh','cohort_fx')}
    reviews=acceptance.get('reviews',[])
    if len(reviews)!=3 or {r.get('package') for r in reviews}!=set(expected):
        raise ValueError('Exactly three independently reviewed packages required')
    bound=acceptance.get('bound_files',{})
    for review in reviews:
        if (review.get('author'),review.get('reviewer'))!=expected[review['package']]:
            raise ValueError('Independent review rotation differs or self approval attempted')
        if review.get('status')!='PASS' or review.get('note') not in bound:
            raise ValueError('Accepted review note missing from bound evidence')
    required={Path(p).resolve().relative_to(ROOT).as_posix() for p in required}
    if not required.issubset(bound):raise ValueError('Required evidence missing from acceptance binding')
    for relative in bound:
        path=(ROOT/relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(ROOT):
            raise ValueError('Acceptance path outside repository')
    values=committed([ROOT/p for p in bound],commit)
    if any(digest(values[p])!=sha for p,sha in bound.items()):
        raise ValueError('Acceptance digest differs from reviewed committed evidence')
    return len(bound)

def verify(out):
    out=Path(out)
    expected=json.loads((out/'SHA256SUMS.json').read_text())
    actual={p.relative_to(out).as_posix():digest(p.read_bytes()) for p in out.rglob('*')
            if p.is_file() and p.relative_to(out).as_posix()!='SHA256SUMS.json'}
    if expected!=actual:raise ValueError('Supplement file/checksum mismatch')
    print(json.dumps({'status':'PASS','exact_files_verified':len(actual),
                      'manifest_sha256':digest((out/'SHA256SUMS.json').read_bytes())}))

def build(results,out):
    results=Path(results).resolve();out=Path(out).resolve()
    if out.exists():raise FileExistsError('Use a NEW immutable supplement directory')
    preserved=preserve.verify()
    commit=preserve.git('rev-parse','HEAD').decode().strip()
    start_path=ROOT/'data/processed/forecast_methods/l3_source_contract_v1/preservation_start.json'
    start=committed([start_path],commit)[start_path.relative_to(ROOT).as_posix()]
    if json.loads(start)!=preserved:raise ValueError('Protected bytes differ from committed start receipt')
    code=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
          and '.pytest_cache' not in p.parts]
    committed(code,commit)
    result_paths=[p for p in results.rglob('*') if p.is_file()]
    notes=sorted((ROOT/'docs/revenue-forecast-strategy/05_backtests').glob('L3_SC_*.md'))
    note_blobs=committed(notes,commit);result_blobs=committed(result_paths,commit)
    acceptance_path=ROOT/'data/processed/forecast_methods/l3_source_contract_v1/review_acceptance_v1.json'
    acceptance=committed([acceptance_path],commit)[acceptance_path.relative_to(ROOT).as_posix()]
    bound_count=validate_acceptance(json.loads(acceptance),commit,code+runtime_inputs()+[start_path]+result_paths+notes)
    out.mkdir(parents=True)
    (out/'.gitattributes').write_text('* -text\n',encoding='utf-8',newline='\n')
    for p in result_paths:
        relative=p.relative_to(results);target=out/'payload'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(result_blobs[p.relative_to(ROOT).as_posix()])
    (out/'notes').mkdir()
    for p in notes:(out/'notes'/p.name).write_bytes(note_blobs[p.relative_to(ROOT).as_posix()])
    (out/'review_acceptance.json').write_bytes(acceptance)
    metadata={'version':out.name,'research_source_commit':commit,'original_bundle_commit':preserve.BASE,
              'original_bundle_manifest_sha256':preserve.MANIFEST_SHA,'publication':'local_only; public push not authorized',
              'scope':'source precision, accounting denominators, consumption permissions; no forecast or trade adoption',
              'prior_policy':'fixed 2/3-1/3 operational estimator retained; free-weight promotion FAIL',
              'results':results.relative_to(ROOT).as_posix(),'result_files':len(result_paths),'review_notes':len(notes),
              'reviewed_committed_files_verified':bound_count}
    (out/'supplement.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
    (out/'README.md').write_text('''# L3 source-contract supplement

Start with `notes/L3_SC_LEAD_HANDOFF_v1.md` and `review_acceptance.json`. The original L3 bundle is unchanged. This supplement adds source-precision/availability evidence, accounting and denominator rules, and a classification of its original 1,187 rows. All statuses and unavailability reasons remain part of the inputs.

Read `payload/precision/discrepancy_ledger.csv`, `quarter_coverage.csv` and `kernel_sensitivity.csv`; `payload/accounting/accounting_contract.csv` and `timing_contract.csv`; then `payload/consumption/consumption_matrix.csv` and `information_gaps.csv`. Package source manifests and independent review notes accompany them. Sensitivities hold named inherited parameters fixed and do not replace historical inputs or forecasts. Cohort flow, timing and future hedge assumptions remain unidentified where stated.

The fixed 2/3-1/3 operational seasonal policy remains in place. Full22 free-w calibration stays descriptive and its matched W1/W2 promotion result stays FAIL. L4 owns forecast/workbook/valuation/memo/registration integration; the quant task owns new preannouncement and investment validation. No investment direction is adopted.

`supplement.json` identifies the actual committed research source. Code and compact primary facts are in that local commit. `SHA256SUMS.json` covers every file except itself. Reproduce into new directories only. This local supplement is not authorization to publish any branch history or artifacts to a public repository.
''',encoding='utf-8',newline='\n')
    hashes={p.relative_to(out).as_posix():digest(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
    (out/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8',newline='\n')
    verify(out)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--results',type=Path)
    a.add_argument('--verify',action='store_true');x=a.parse_args()
    if x.verify:verify(x.out)
    elif x.results is None:a.error('--results is required to build')
    else:build(x.results,x.out)
