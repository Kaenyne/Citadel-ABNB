"""Build a versioned research handoff, never an automatically adopted ABNB model."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
DATE='2026-09-13'
REQUIRED=['package','quarter','metric','scenario','value','lower','upper','units','information_date',
          'evidence_status','source_reference','treatment','baseline_being_replaced','embedded_fx','adoption_status']
PAYLOAD_SUFFIXES={'.csv','.json','.md','.png','.svg','.txt'}

def committed_bytes(path):
    """Reject ignored/untracked/changed files; return the immutable HEAD blob."""
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('Research source must be inside repository')
    rel=path.relative_to(ROOT).as_posix()
    try:
        blob=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        raise ValueError('Research source not committed in HEAD: '+rel) from exc
    if blob!=path.read_bytes():raise ValueError('Research source bytes differ from HEAD: '+rel)
    return blob

def validate(d):
    if set(REQUIRED)-set(d):
        raise ValueError('missing bundle fields '+str(set(REQUIRED)-set(d)))
    for c in REQUIRED:
        if c not in ['value','lower','upper'] and (d[c].isna().any() or d[c].astype(str).str.strip().eq('').any()):
            raise ValueError('missing '+c)
    for c in ['value','lower','upper']:
        values=pd.to_numeric(d[c],errors='raise')
        if (~np.isfinite(values[values.notna()])).any():
            raise ValueError('nonfinite '+c)
    bounds=d.lower.notna() & d.upper.notna()
    if (d.loc[bounds,'lower']>d.loc[bounds,'upper']).any():
        raise ValueError('reversed bounds')
    dates=pd.to_datetime(d.information_date,errors='coerce',utc=True)
    if dates.isna().any() or (dates>=pd.Timestamp(DATE,tz='UTC')+pd.Timedelta(days=1)).any():
        raise ValueError('missing or future information date')
    if not d.quarter.astype(str).str.fullmatch(r'\d{4}Q[1-4]|historical|not_applicable').all():
        raise ValueError('quarter must be explicit fiscal quarter or labeled historical/not_applicable')
    if d.duplicated(['package','quarter','metric','scenario']).any():
        raise ValueError('duplicate semantic key')
    if not d.adoption_status.str.contains('pending|not_applicable',case=False,regex=True).all():
        raise ValueError('L3 cannot adopt a forecast')
    replacements=d.treatment.str.contains('replacement|multiply',case=False,regex=True)
    missing_baseline=d.baseline_being_replaced.str.lower().str.startswith('none')
    if (replacements & missing_baseline).any():
        raise ValueError('replacement requires a named matching baseline')
    if (replacements & d.embedded_fx.str.lower().isin(['not_applicable','unknown','none'])).any():
        raise ValueError('replacement requires explicit embedded FX treatment')
    return d

def normalize(path,package):
    d=pd.read_csv(path)
    aliases={'source_ref':'source_reference','baseline_replaced':'baseline_being_replaced',
             'replacement_vs_incremental':'treatment','lower_bound':'lower','upper_bound':'upper'}
    for old,new in aliases.items():
        if new not in d and old in d:d[new]=d[old]
    d['package']=package
    d['source_period']=d.quarter
    period_range=d.quarter.astype(str).str.fullmatch(r'\d{4}Q[1-4]-\d{4}Q[1-4]')
    d.loc[period_range,'quarter']='historical'
    # L3's analysis is not backdated to its latest underlying quarterly release.
    d['source_information_date']=d.information_date
    source_dates=pd.to_datetime(d.information_date,errors='coerce',utc=True)
    if source_dates.isna().any() or (source_dates>=pd.Timestamp(DATE,tz='UTC')+pd.Timedelta(days=1)).any():
        raise ValueError('source information date invalid or after L3 audit')
    d['information_date']=DATE
    for c in ['lower','upper']:
        if c not in d:d[c]=np.nan
    for c,default in [('baseline_being_replaced','none; descriptive evidence only'),
                      ('embedded_fx','not_applicable'),('adoption_status','pending_L4_and_team_review')]:
        if c not in d:d[c]=default
        else:d[c]=d[c].fillna(default)
    # Preserve original period/source date and add a path into the immutable payload.
    d['package_input_file']=path.relative_to(ROOT).as_posix()
    d['bundle_payload_reference']='payload/'+package+'/'+path.name
    return d

def build(out,inputs):
    out=Path(out).resolve()
    if out.exists():raise FileExistsError(out)
    source_paths=[str(Path(p).resolve().parent) for p in inputs.values()]
    code_paths=[str(ROOT/'analysis/src/forecast_methods'/p) for p in
                ['cohort_fx_v1','cohort_fx_v2','fee_panel_v1','l3_adr_hotel_v1',
                 'nclh_transfer_v1','conversion_validation_v1','l3_integration_v1']]
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*source_paths,*code_paths],cwd=ROOT,text=True)
    if status.strip():raise ValueError('Commit the selected research inputs and package sources before bundling')
    for directory in code_paths:
        for f in Path(directory).rglob('*'):
            if f.is_file() and (f.suffix in {'.py','.md'} or f.name=='.gitattributes'):
                committed_bytes(f)
    payloads={}
    for package,p in inputs.items():
        for f in sorted(Path(p).resolve().parent.iterdir()):
            if f.is_file() and f.suffix.lower() in PAYLOAD_SUFFIXES:
                if f.stat().st_size>20_000_000:raise ValueError('Unexpected large payload '+str(f))
                payloads[(package,f)]=committed_bytes(f)
    # Accounting limits and independent audit findings travel with the payload.
    notes={f:committed_bytes(f) for f in sorted((ROOT/'docs/revenue-forecast-strategy/05_backtests').glob('L3_*.md'))}
    frames=[normalize(Path(p).resolve(),package) for package,p in inputs.items()]
    # Normalization read the same bytes whose immutable Git blobs we captured.
    for package,p in inputs.items():
        f=Path(p).resolve()
        if payloads[(package,f)]!=f.read_bytes():raise ValueError('Source changed during bundle preparation')
    d=validate(pd.concat(frames,ignore_index=True))
    out.mkdir(parents=True)
    (out/'.gitattributes').write_text('* -text\n',encoding='utf-8',newline='\n')
    d.to_csv(out/'l4_inputs.csv',index=False,float_format='%.12g',lineterminator='\n')
    copied=[]
    notes_dir=out/'research_notes';notes_dir.mkdir()
    for f,blob in notes.items():(notes_dir/f.name).write_bytes(blob)
    for package,p in inputs.items():
        source=Path(p).resolve().parent
        dest=out/'payload'/package;dest.mkdir(parents=True)
        for (source_package,f),blob in payloads.items():
            if source_package==package:
                (dest/f.name).write_bytes(blob)
                copied.append(f.relative_to(ROOT).as_posix())
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    metadata={'bundle_version':out.name,'information_date':DATE,'research_source_commit':commit,
              'verified_L1_L2_base':'1c87628cedbc94ab8a0e8552743c94485ef353b8','rows':len(d),
              'packages':d.groupby('package').size().to_dict(),'source_outputs':copied,
              'research_notes':[f.relative_to(ROOT).as_posix() for f in notes],
              'source_reference_prefixes':{'cohort_fx_v2/':'payload/cohort_fx/',
                  'conversion_validation_v1/':'payload/conversion/',
                  'fee_panel_v1/':'payload/fee_panel/','l3_adr_hotel_v1/':'payload/adr_hotel/',
                  'nclh_transfer_v1/':'payload/nclh/','L3_*.md':'research_notes/ (same filename)'},
              'investment_adoption':'pending; L4 owns combined forecast and registrations',
              'checksums':'SHA256SUMS.json covers exact payload bytes; bundle-local .gitattributes disables newline conversion'}
    (out/'bundle.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
    (out/'README.md').write_text('''# L3 research handoff

Read `l4_inputs.csv` with the evidence and treatment fields intact. Values are conditional inputs or descriptive evidence; none is an adopted forecast. Nulls mean unidentified/unavailable, never zero. The combined model, guide forecast and registrations remain L4's responsibility.

Start with `payload/conversion/final_review_acceptance.json`, the hash-bound `accepted_validation_spec.json`, and the conversion claim ledger and charts. The separately issued receipt closes the specification's initial pending-review status. The 22-quarter fit estimates four seasonal conversion coefficients and one shared lag weight. Full-sample parameters are descriptive; prospective promotion depends on the matched chronological comparison. Retain the existing fixed 2/3-1/3 operational benchmark when that promotion hurdle fails. Conversion coefficients are not fee take rates, and the weight is not an identified booking or payment share.

Use exactly one compatible replacement route. ADR totals already contain their named FX estimator and fee mechanics; component rows are explanatory and must not be added again. Cohort FX can replace only the matching inherited booking-FX baseline after currency, cohort and hedge compatibility review. Its full reference FX factor must never multiply reported USD kernel revenue. No RNPL demand or cancellation overlay is supplied. Fee theta remains unavailable until matched residence-known wave data clear the gates. NCLH and hotel rows are research evidence, not ABNB adjustments.

`bundle.json` records the committed research source. The commit containing this immutable bundle is supplied in the lead handoff. `SHA256SUMS.json` verifies all files except itself. Rebuild into a NEW output directory and never edit this one. Code and underlying compact source inputs are in the same Git branch; external R examples are not required to execute the new Python adapter.

Useful order: package results/accounting/independent-review notes in `research_notes/`; then evidence rows; then corresponding payload detail/weights/scores. Every scenario retains original source references plus a bundle payload reference. `bundle.json` maps logical package prefixes to payload directories; referenced L3 note filenames are in `research_notes/`. Source-manifest hashes refer to the source worktree bytes; immutable payload checksums refer to this bundle's exact bytes.
''',encoding='utf-8',newline='\n')
    manifest={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(out.rglob('*')) if p.is_file()}
    (out/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(metadata,indent=2))

def verify(out):
    out=Path(out)
    expected=json.loads((out/'SHA256SUMS.json').read_text())
    actual={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in out.rglob('*') if p.is_file() and p.relative_to(out).as_posix()!='SHA256SUMS.json'}
    if expected!=actual:raise AssertionError('bundle payload checksum mismatch')
    validate(pd.read_csv(out/'l4_inputs.csv'))
    print(json.dumps({'checksums_verified':len(actual),'schema':'PASS'}))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--verify',action='store_true')
    ap.add_argument('--input',action='append',help='PACKAGE=CANONICAL_L4_CSV')
    a=ap.parse_args()
    if a.verify:verify(a.out)
    else:
        inputs=dict(x.split('=',1) for x in (a.input or []))
        if set(inputs)!={'cohort_fx','fee_panel','adr_hotel','nclh','conversion'}:raise ValueError('all five L3 packages required')
        build(a.out,inputs)

if __name__=='__main__':main()
