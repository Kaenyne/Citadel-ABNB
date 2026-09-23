"""Independent immutable commit/handoff review; no parent seal-helper imports."""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

from early_contract_checks import sha

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1'
DOCS=ROOT/'docs/revenue-forecast-strategy/quant_thesis_validation_v1'
COMMIT='965166c4572fe7c6300c7281e77afc5877411820'
L3='8821961853e4068febbfe2712f9a4e1036c9e629'
SCOPES=['analysis/src/forecast_methods/quant_thesis_validation_v1',
        'data/processed/forecast_methods/quant_thesis_validation_v1',
        'docs/revenue-forecast-strategy/quant_thesis_validation_v1',
        'docs/revenue-forecast-strategy/05_backtests/QUANT_THESIS_VALIDATION_v1.md']


def git(*args,data=None):
    return subprocess.check_output(['git',*args],cwd=ROOT,input=data)


def js(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main(out):
    if out.exists():raise FileExistsError(out)
    if not out.resolve().is_relative_to((BASE/'final_contract_review_v1').resolve()):raise ValueError('Exclusive reviewer output only')
    directory=DOCS/'handoff_v1';manifest_path=directory/'analytical_manifest.json'
    manifest=js(manifest_path);seal=js(directory/'seal_receipt.json')
    if manifest['analytical_commit']!=COMMIT or seal['analytical_commit']!=COMMIT:raise AssertionError('Wrong analytical commit')
    if sha(manifest_path)!=seal['manifest_sha256']:raise AssertionError('Manifest hash mismatch')
    subprocess.run(['git','merge-base','--is-ancestor',L3,COMMIT],cwd=ROOT,check=True)
    for line in git('diff','--name-status',L3,COMMIT).decode().splitlines():
        action,path=line.split('\t',1)
        if action!='A' or not any(path==s or path.startswith(s+'/') for s in SCOPES):
            raise AssertionError('Changed existing or unscoped file: '+line)
    tree={}
    for entry in git('ls-tree','-r','-z',COMMIT,'--',*SCOPES).split(b'\0'):
        if not entry:continue
        meta,p=entry.split(b'\t',1);mode,typ,obj=meta.decode().split()
        if typ!='blob':raise AssertionError('Nonblob analytical entry')
        tree[p.decode()]={'mode':mode,'git_blob':obj}
    records=manifest['files'];names=[r['path'] for r in records]
    if len(names)!=len(set(names)) or set(names)!=set(tree):raise AssertionError('Manifest/tree coverage mismatch')
    raw=git('cat-file','--batch',data=('\n'.join(tree[p]['git_blob'] for p in names)+'\n').encode())
    offset=0;checks=[]
    for r in records:
        end=raw.index(b'\n',offset);obj,typ,size=raw[offset:end].decode().split();size=int(size)
        payload=raw[end+1:end+1+size];offset=end+size+2
        expected=tree[r['path']]
        if obj!=expected['git_blob'] or typ!='blob':raise AssertionError('Wrong object in Git batch')
        digest=hashlib.sha256(payload).hexdigest();disk=sha(ROOT/r['path'])
        ok=(r['git_blob']==obj and r['mode']==expected['mode'] and r['bytes']==size and r['sha256']==digest==disk)
        checks.append(dict(path=r['path'],git_blob=obj,bytes=size,manifest_sha256=r['sha256'],git_sha256=digest,disk_sha256=disk,passes=ok))
    if len(checks)!=manifest['file_count'] or sum(c['bytes'] for c in checks)!=manifest['total_bytes'] or not all(c['passes'] for c in checks):
        raise AssertionError('Exact analytical byte check failed')
    analytical=js(BASE/'final_contract_review_v1/final_receipt_v1/receipt.json')
    by_path={r['path']:r for r in records}
    for p,h in analytical['bindings_sha256'].items():
        normalized=p.replace('\\','/')
        if normalized not in by_path or by_path[normalized]['sha256']!=h:raise AssertionError('Reviewed artifact missing or changed in commit')
    protection=js(BASE/'verification_postcommit_v1/receipt.json')
    if protection['status']!='PASS' or protection['failures'] or protection['registry_changed']:raise AssertionError('Protection receipt not passing')
    protected=js(BASE/'evidence_v3/protected_manifest.json');external=js(BASE/'evidence_v3/external_manifest.json')
    for r in protected:
        if sha(ROOT/r['path'])!=r['sha256']:raise AssertionError('Protected source changed')
    for r in external:
        if sha(ROOT/r['frozen_path'])!=r['sha256']:raise AssertionError('External evidence changed')
    handoff=(directory/'L4_HANDOFF.md').read_text(encoding='utf-8-sig')
    links=re.findall(r'\[[^\]]*\]\(([^)]+)\)',handoff)
    for link in links:
        target=(directory/link).resolve()
        if not target.is_relative_to(ROOT) or not target.is_file():raise AssertionError('Broken handoff link: '+link)
    hash_files=[manifest_path,DOCS/'delivery_v3/ABNB_decision_summary.pdf',DOCS/'FINAL_PROTOCOL_v1.md',
      ROOT/'data/processed/forecast_methods/l3_bundle_v1/SHA256SUMS.json',BASE/'verification_postcommit_v1/receipt.json',
      BASE/'independent_reproduction_v1/complete_run_v2/independent_completion_receipt.json',
      BASE/'adversarial_review_v1/results_v2/receipt.json',BASE/'adversarial_review_v1/final_prose_closure_v1/receipt.json',
      BASE/'final_contract_review_v1/final_receipt_v1/receipt.json',BASE/'reproductions/final_v1/run_receipt.json']
    expected_hashes={sha(p) for p in hash_files}
    if set(re.findall(r'\b[a-f0-9]{64}\b',handoff))!=expected_hashes:raise AssertionError('Written receipt/hash identities disagree')
    bindings={str(p.relative_to(ROOT)):sha(p) for p in [*hash_files,directory/'L4_HANDOFF.md',directory/'seal_receipt.json',Path(__file__).resolve()]}
    out.mkdir(parents=True)
    with (out/'analytical_identity_checks.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
    receipt=dict(reviewer='/root/test_designer',status='PASS_G8_RESEARCH_DELIVERY_IDENTITY',analytical_commit=COMMIT,
        analytical_files=len(checks),analytical_bytes=sum(r['bytes'] for r in checks),
        reviewed_artifact_bindings_present_unchanged=len(analytical['bindings_sha256']),
        only_new_authorized_scope_additions=True,protected_files=len(protected),external_files=len(external),
        handoff_links_resolve=len(links),written_sha256_identities_verified=len(expected_hashes),
        original_claim_limits_preserved=True,relocation_guarantee_claimed=False,
        new_calculations_fits_resamples=0,git_mutations=0,own_economic_numerical_signoff=False,
        forecast_promotion='FAIL',investment_adoption=False,
        parent_remaining_step='Bind this receipt in ACCEPTANCE_FINAL.json, make local handoff commit and verify clean state; no further analysis',
        bindings_sha256=bindings)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='bindings_sha256'},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);main(p.parse_args().out)
