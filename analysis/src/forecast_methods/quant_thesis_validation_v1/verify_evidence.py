"""Verify frozen local/Git evidence and protected inputs without writing to them."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess

ROOT=Path(__file__).resolve().parents[4]
PKG=ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1'

def read_bytes(path):
    p=Path(path).resolve()
    if os.name=='nt':
        p=Path(chr(92)*2+'?'+chr(92)+str(p))
    return p.read_bytes()

def sha(path): return hashlib.sha256(read_bytes(path)).hexdigest()

def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)

def verify(out):
    out=Path(out).resolve()
    if out.exists(): raise FileExistsError(out)
    if not out.is_relative_to(ROOT): raise ValueError('Output must be inside task worktree')
    frozen=PKG/'evidence_v3'
    failures=[]
    protected=json.loads((frozen/'protected_manifest.json').read_text())
    for r in protected:
        try:
            if sha(ROOT/r['path']) != r['sha256']: failures.append('protected: '+r['path'])
        except OSError as exc:
            failures.append(f"protected unreadable: {r['path']}: {exc}")
    external=json.loads((frozen/'external_manifest.json').read_text())
    for r in external:
        if sha(ROOT/r['frozen_path']) != r['sha256']: failures.append('frozen: '+r['frozen_path'])
        if r['commit']:
            content=git('show',r['commit']+':'+r['source_path'])
            if hashlib.sha256(content).hexdigest()!=r['sha256']: failures.append('Git external: '+r['source_path'])
    docs=ROOT/'docs/revenue-forecast-strategy/quant_thesis_validation_v1'
    protocol=json.loads((docs/'PROTOCOL_FREEZE_v1.json').read_text())
    for name,digest in protocol['files'].items():
        if sha(docs/name)!=digest: failures.append('protocol changed: '+name)
    ancestors=[('7fb6fe0f248d5492b899672b9b70545da62d63ee','8821961853e4068febbfe2712f9a4e1036c9e629'),
               ('1039252935e9c3cf0cf62bdc9f07b5407d0a11ad','29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70')]
    for ancestor,descendant in ancestors:
        subprocess.run(['git','merge-base','--is-ancestor',ancestor,descendant],cwd=ROOT,check=True)
    changed=git('diff','--name-status','8821961853e4068febbfe2712f9a4e1036c9e629','HEAD').decode().splitlines()
    for entry in changed:
        if not entry.startswith('A\t'): failures.append('existing tracked change: '+entry)
    bundle=ROOT/'data/processed/forecast_methods/l3_bundle_v1/SHA256SUMS.json'
    if sha(bundle)!='9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970':
        failures.append('L3 bundle manifest')
    out.mkdir(parents=True)
    receipt=dict(status='PASS' if not failures else 'FAIL',protected_files=len(protected),external_files=len(external),
                 committed_external_files=sum(bool(r['commit']) for r in external),protocol_files=len(protocol['files']),
                 baseline_commit='8821961853e4068febbfe2712f9a4e1036c9e629',
                 ancestry_checks=ancestors,failures=failures,registry_changed=False,
                 registry_basis='All starting registry/scorer bytes included in protected file check; no new registration authorized')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    if failures: raise AssertionError(f'{len(failures)} evidence checks failed')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=PKG/'verification_v1')
    verify(p.parse_args().out)
