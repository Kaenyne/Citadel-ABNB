"""Focused repeat audit of the exact committed L4 package before publication."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
TARGET='3da2903e2c78f6beea358819e7c561b07a5f49a3'
BUNDLED=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
RESEARCH=Path('C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe')
OUT=ROOT/'data/processed/forecast_methods/lane4_publish_audit_v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--check',required=True,choices=['sources','revenue','model','review','numeric','preservation'])
    ap.add_argument('--run-id',required=True)
    a=ap.parse_args()
    if not re.fullmatch('[A-Za-z0-9_-]+',a.run_id):
        raise ValueError('Use a simple new audit ID')
    dest=OUT/a.run_id
    dest.mkdir(parents=True,exist_ok=True)
    receipt=dest/(a.check+'.json')
    log=dest/(a.check+'.log')
    if receipt.exists() or log.exists():
        raise FileExistsError('This check ID already exists; preserve prior results')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',TARGET,head],cwd=ROOT,check=True)
    changed_since_target=subprocess.check_output(['git','diff','--name-only','--diff-filter=MDR',TARGET,head],cwd=ROOT,text=True).splitlines()
    if changed_since_target:
        raise AssertionError('Audited committed files changed: '+repr(changed_since_target[:5]))
    start=time.monotonic()
    result=dict(commit=head,audited_artifact_commit=TARGET,check=a.check,started_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    commands=[]
    if a.check=='sources':
        commands=[[str(BUNDLED),'-B','-m','unittest','discover','-s','analysis/src/forecast_methods/lane4_sources_v2','-p','test_*.py','-v']]
    elif a.check=='revenue':
        commands=[[str(RESEARCH),'-B','-m','pytest','-q','-p','no:cacheprovider','analysis/src/forecast_methods/lane4_revenue_v2/tests']]
    elif a.check=='model':
        commands=[[str(BUNDLED),'-B','-m','unittest','discover','-s','analysis/src/forecast_methods/lane4_model_v2','-p','test_model.py','-v']]
    elif a.check=='review':
        commands=[[str(BUNDLED),'-B','-m','unittest','discover','-s','analysis/src/forecast_methods/lane4_review_v2/tests','-v']]
    elif a.check=='numeric':
        commands=[
          [str(RESEARCH),'-B','analysis/src/forecast_methods/lane4_control_v2/review_revenue.py','--revenue-dir','data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1','--output',str(dest/'revenue_arithmetic.json')],
          [str(RESEARCH),'-B','analysis/src/forecast_methods/lane4_control_v2/review_exports.py','--workbook','model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx','--model-dir','data/processed/forecast_methods/lane4_model_v2/snapshot_v2','--revenue-dir','data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1','--output',str(dest/'export_arithmetic.json')]]
    try:
        if a.check=='preservation':
            old=json.loads((ROOT/'data/processed/forecast_methods/lane4_control_v2/baseline/tracked_hashes.json').read_text())
            changed=[n for n,h in old.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
            if changed:
                raise AssertionError('Pre-existing bytes changed: '+repr(changed[:5]))
            regs=json.loads((ROOT/'data/processed/forecast_methods/lane4_control_v2/baseline/registry_hashes.json').read_text())
            if any(sha(ROOT/n)!=h for n,h in regs.items()):
                raise AssertionError('Registry changed')
            ext=json.loads((ROOT/'data/processed/forecast_methods/lane4_control_v1/baseline/external_fx_hashes.json').read_text())
            if any(sha(Path(ext['root'])/n)!=h for n,h in ext['files'].items()):
                raise AssertionError('Original FX dependency changed')
            bundle=ROOT/'data/processed/forecast_methods/lane4_sources_v2/snapshot_v1/bundle'
            manifest=json.loads((bundle/'SHA256SUMS.json').read_text())
            if len(manifest)!=108 or any(sha(bundle/n)!=h for n,h in manifest.items()):
                raise AssertionError('Accepted source bytes changed')
            if subprocess.run(['git','diff','--quiet',head],cwd=ROOT).returncode:
                raise AssertionError('A committed file changed during audit')
            result.update(pre_existing_files=len(old),registry_files=len(regs),external_fx_files=len(ext['files']),accepted_bundle_files=len(manifest),source_bytes_unchanged=True)
        else:
            logs=[]
            result['commands']=commands
            exits=[]
            for command in commands:
                proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
                logs.append(proc.stdout+proc.stderr)
                exits.append(proc.returncode)
                if proc.returncode:
                    break
            text='\n'.join(logs)
            log.write_text(text,encoding='utf-8')
            result['exit_codes']=exits
            counts=re.findall(r'Ran (\d+) tests',text) or re.findall(r'(\d+) passed',text)
            if counts:
                result['tests_passed']=sum(map(int,counts)) if not any(exits) else None
            if any(exits):
                raise AssertionError('Audit command failed; see preserved log')
        result['verdict']='PASS'
    except Exception as exc:
        result['verdict']='FAIL'
        result['error']=str(exc)
    result['elapsed_seconds']=time.monotonic()-start
    receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0 if result['verdict']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
