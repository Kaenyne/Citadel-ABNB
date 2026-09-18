"""Verify and bind the exact manually reviewed final analytical artifact set."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

from early_contract_checks import sha

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1'
DOCS=ROOT/'docs/revenue-forecast-strategy/quant_thesis_validation_v1'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main(spec,out):
    if out.exists():raise FileExistsError(out)
    if not out.resolve().is_relative_to((BASE/'final_contract_review_v1').resolve()):
        raise ValueError('Write only in exclusive reviewer directory')
    spec=spec.resolve();config=read_json(spec)
    checks=[]
    def verify(kind,path,expected):
        path=Path(path)
        if not path.is_absolute():path=ROOT/path
        path=path.resolve()
        if not path.is_relative_to(ROOT):raise ValueError('Binding escaped worktree')
        actual=sha(path)
        checks.append(dict(kind=kind,path=str(path.relative_to(ROOT)),expected=expected,actual=actual,passes=actual==expected))
    for r in read_json(BASE/'evidence_v3/protected_manifest.json'):
        verify('protected',r['path'],r['sha256'])
    for r in read_json(BASE/'evidence_v3/external_manifest.json'):
        verify('external',r['frozen_path'],r['sha256'])
    receipts=[
      ('accounting_review_v1/results_v1/independent_receipt.json','bound_inputs_code_and_outputs_sha256',''),
      ('independent_reproduction_v1/complete_run_v2/independent_completion_receipt.json','bindings',''),
      ('independent_reproduction_v1/complete_run_v2/source_review/source_independent_receipt.json','bound_author_files_sha256',''),
      ('independent_reproduction_v1/complete_run_v2/prospective_review/prospective_independent_receipt.json','bindings',''),
      ('adversarial_review_v1/results_v2/receipt.json','reviewed_author_file_hashes',str(BASE/'economics_v1/results_v2')),
      ('adversarial_review_v1/final_prose_closure_v1/receipt.json','bindings_sha256',''),
      ('final_contract_review_v1/uncertainty_checks_v1/receipt.json','bound_inputs_and_reviewed_outputs_sha256','')]
    for p,key,prefix in receipts:
        for path,h in read_json(BASE/p)[key].items():verify('independent_review',Path(prefix)/path if prefix else path,h)
    run=read_json(BASE/'reproductions/final_v1/run_receipt.json')
    if run['status']!='PASS_complete_bounded_rebuild' or len(run['steps'])!=17 or any(r['exit_code'] for r in run['steps']):
        raise AssertionError('Full canonical runner has not completed17successful stages')
    verify('executed_runner','analysis/src/forecast_methods/quant_thesis_validation_v1/run.py',run['runner_sha256'])
    with (BASE/'reproductions/final_v1/canonical_comparison.csv').open(encoding='utf-8-sig',newline='') as f:
        comparisons=list(csv.DictReader(f))
    for r in comparisons:
        verify('canonical_rebuild_original',r['canonical'],r['canonical_sha256'])
        verify('canonical_rebuild_fresh',r['fresh'],r['fresh_sha256'])
        if r['same_bytes']!='True' or r['canonical_sha256']!=r['fresh_sha256']:
            raise AssertionError('A canonical comparison did not pass')
    with (BASE/'claims_v2/claim_ledger.csv').open(encoding='utf-8-sig',newline='') as f:claims=list(csv.DictReader(f))
    if len(claims)!=18 or claims!=read_json(BASE/'claims_v2/claim_ledger.json'):
        raise AssertionError('Claim CSV/JSON do not agree')
    if any(not v for r in claims for v in r.values()):raise AssertionError('Required claim field is empty')
    text=(DOCS/'PRESENTATION_DEFENSE_v2.md').read_text(encoding='utf-8-sig')
    links=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text)
    if len(links)!=2:raise AssertionError('Expected two essential figure links')
    for link in links:
        p=(DOCS/link).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file():raise AssertionError('Broken figure link: '+link)
    artifact_paths=list(config['artifact_paths'])+[str(spec.relative_to(ROOT))]
    bindings={}
    for p in artifact_paths:
        file=(ROOT/p).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file():raise ValueError('Invalid artifact path: '+p)
        bindings[str(file.relative_to(ROOT))]=sha(file)
    failures=[r for r in checks if not r['passes']]
    if failures:raise AssertionError(f'Final binding mismatch: {failures}')
    out.mkdir(parents=True)
    with (out/'identity_checks.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
    receipt=dict(reviewer='/root/test_designer',status='PASS_FINAL_ANALYTICAL_ARTIFACT_CONTRACT',
        manually_reviewed_gate_dispositions=config['gate_dispositions'],
        own_economics_numerical_signoff=False,economic_independence='Worker A567checkreceipt, independently rebound here',
        prospective_independence='Worker C793checks and33exact files, independently rebound here',
        accepted_uncertainty_independently_recomputed_checks=246,
        protected_checks=sum(r['kind']=='protected' for r in checks),external_checks=sum(r['kind']=='external' for r in checks),
        independent_review_bindings=sum(r['kind']=='independent_review' for r in checks),
        full_runner_successful_stages=len(run['steps']),canonical_file_pairs=len(comparisons),
        claims_csv_json_equal=True,claims_n=18,essential_figure_links_valid=2,
        canonical_pdf_pages_visually_inspected=1,canonical_figure_pngs_visually_inspected=2,
        forecast_promotion='FAIL',investment_direction_target_probability_adopted=False,
        transfer_commit_binding='Separate handoff receipt required after analytical commit; this binds analytical bytes only',
        bindings_sha256=bindings,identity_failures=0,
        scope_limit='This is an independent contract/claim/visual review, not independent approval of reviewer-authored economics.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('bindings_sha256','manually_reviewed_gate_dispositions')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();main(a.spec,a.out)
