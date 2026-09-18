"""Independent metadata/identity review; no import of the reviewed implementation."""
import csv
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1'
OUT=BASE/'final_contract_review_v1/early_checks_v1'


def sha(path):
    path=Path(path).resolve()
    p=str(path)
    if os.name=='nt' and len(p)>=240:p='\\\\?\\'+p
    with open(p,'rb') as h:return hashlib.sha256(h.read()).hexdigest()


def rows(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))


def main():
    if OUT.exists():raise FileExistsError('Immutable review output already exists')
    checks=[]
    def add(kind,path,expected):
        digest=sha(ROOT/path)
        checks.append(dict(kind=kind,path=path,expected=expected,actual=digest,passes=digest==expected))
    for x in json.loads((BASE/'evidence_v3/protected_manifest.json').read_text(encoding='utf-8-sig')):
        add('protected_input',x['path'],x['sha256'])
    for x in json.loads((BASE/'evidence_v3/external_manifest.json').read_text(encoding='utf-8-sig')):
        add('external_evidence',x['frozen_path'],x['sha256'])
    for path,key in [('independent_reproduction_v1/source_review_v1/source_independent_receipt.json','bound_author_files_sha256'),
                     ('accounting_review_v1/results_v1/independent_receipt.json','bound_inputs_code_and_outputs_sha256')]:
        receipt=json.loads((BASE/path).read_text(encoding='utf-8-sig'))
        for p,digest in receipt[key].items():add('independent_review_binding',p,digest)
    f=BASE/'prospective_v1/results_v1/forecast';e=BASE/'prospective_v1/results_v1/evaluation'
    prediction=rows(f/'predictions.csv')
    origin={r['quarter']:r['origin_date'] for r in prediction}
    temporal=[]
    for table,fields in [('panel_inputs',['available_date']),('guide_inputs',['available_date']),
                         ('cushion_inputs',['actual_available_date']),
                         ('lambda_training',['revenue_available_date','gbv1_available_date','gbv2_available_date'])]:
        for r in rows(f/(table+'.csv')):
            for col in fields:
                ok=r[col] < origin[r['quarter']]
                temporal.append(dict(table=table,quarter=r['quarter'],input_quarter=r.get('input_quarter',r.get('training_quarter')),
                                     field=col,available_date=r[col],origin=origin[r['quarter']],strictly_before=ok))
    for r in rows(e/'calibration_inputs.csv'):
        temporal.append(dict(table='calibration_inputs',quarter=r['quarter'],input_quarter=r['input_quarter'],
                             field='target_guide_available_date',available_date=r['target_guide_available_date'],
                             origin=r['origin_date'],strictly_before=r['target_guide_available_date']<r['origin_date']))
    target_checks=[r['origin_date']<r['guide_issuance_date'] for r in prediction]
    fair=rows(e/'errors.csv')
    rounding=[abs(float(r['target_mid_hi'])-float(r['target_mid_lo'])-1)<1e-8 for r in fair if r['target_mid_lo']]
    av2=BASE/'source_audit_v1/results_v2/observation_availability.csv'
    av3=BASE/'source_audit_v1/results_v3/observation_availability.csv'
    summary=dict(reviewer='/root/test_designer',role='Wave3 I contract reviewer',
                 independently_recomputed_economic_authorship=False,
                 status='EARLY_CONTRACT_CHECKS_PASS_PENDING_EXACT_FINAL_ARTIFACTS',
                 protected_count=sum(x['kind']=='protected_input' for x in checks),
                 external_count=sum(x['kind']=='external_evidence' for x in checks),
                 review_bindings=sum(x['kind']=='independent_review_binding' for x in checks),
                 hash_failures=[x for x in checks if not x['passes']],
                 temporal_fields_checked=len(temporal),temporal_failures=[x for x in temporal if not x['strictly_before']],
                 target_guide_after_origin_all=all(target_checks),target_method_rows=len(target_checks),
                 rounding_is_administrative_one_usdm_width_all=all(rounding),
                 source_v2_v3_availability_bytes_equal=sha(av2)==sha(av3),
                 preserved_result_verdict=json.loads((e/'verdict.json').read_text())['verdict'],
                 outstanding=['Exact final summary/PDF/claim ledger/interface not yet supplied',
                              'Independent reviewer A must sign E financial calculations; this reviewer authored E',
                              'Outcome loading wording must mean scoring join after freeze, not blind process loading'])
    OUT.mkdir(parents=True)
    for name,data in [('identity_checks.csv',checks),('information_date_checks.csv',temporal)]:
        with (OUT/name).open('x',encoding='utf-8',newline='') as h:
            w=csv.DictWriter(h,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    with (OUT/'receipt.json').open('x',encoding='utf-8') as h:json.dump(summary,h,indent=2);h.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='outstanding'},indent=2))
    if summary['hash_failures'] or summary['temporal_failures'] or not all(target_checks) or not all(rounding):
        raise AssertionError('Contract review found a blocking integrity failure')


if __name__=='__main__':main()
