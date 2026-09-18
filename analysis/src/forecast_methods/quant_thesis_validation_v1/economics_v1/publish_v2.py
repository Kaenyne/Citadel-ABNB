"""Additive publication metadata repair; all existing numeric cells remain exact strings."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
ALLOWED=(ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1/economics_v1').resolve()


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def publish(source,out):
    source,out=Path(source).resolve(),Path(out).resolve()
    if ALLOWED not in source.parents or ALLOWED not in out.parents:
        raise ValueError('Both directories must be in the exclusive economic data package')
    if out.exists():raise FileExistsError('Refuse existing publication destination')
    receipt=json.loads((source/'receipt.json').read_text())
    for name,expected in receipt['output_hashes'].items():
        if sha(source/name)!=expected:raise ValueError(f'Numerical source changed: {name}')
    out.mkdir(parents=True)
    numeric_checks=0
    for name in receipt['output_hashes']:
        with (source/name).open(newline='',encoding='utf-8') as handle:
            reader=csv.DictReader(handle);fields=list(reader.fieldnames);rows=list(reader)
        rename={'actual_endpoint_balance_value':'conditional_endpoint_balance_value'} if name=='horizon_convention.csv' else {}
        corrected=[]
        for row in rows:
            target={rename.get(k,k):v for k,v in row.items()}
            for k,v in row.items():
                if target[rename.get(k,k)]!=v:raise AssertionError('Unexpected numeric or label change')
                try:float(v);numeric_checks+=1
                except ValueError:pass
            target['empirical_validation_n']='0'
            if name in ('cash_share_horizons.csv','horizon_convention.csv','horizon_operating_contrast.csv',
                        'multiple_cash_share_sensitivity.csv','repurchase_price_sensitivity.csv'):
                target['evidence_status']='conditional_cash_share_roll; FY27 EBITDA held constant; no current-price adoption'
            elif name=='equation_checks.csv':
                target['evidence_status']='Deterministic equation reconciliation; not empirical validation'
            else:
                target['evidence_status']='Conditional accounting scenario; no fitted probability or investment adoption'
            corrected.append(target)
        newfields=[rename.get(k,k) for k in fields]
        for k in ('empirical_validation_n','evidence_status'):
            if k not in newfields:newfields.append(k)
        with (out/name).open('x',newline='',encoding='utf-8') as handle:
            writer=csv.DictWriter(handle,fieldnames=newfields);writer.writeheader();writer.writerows(corrected)
    for old,new in [('receipt.json','numerical_receipt_v1.json'),('source_hashes.json','source_hashes.json')]:
        with (out/new).open('xb') as handle:handle.write((source/old).read_bytes())
    summary=dict(status='Publication-label repair only; numerical cells unchanged',
                 source_receipt_sha256=sha(source/'receipt.json'),source_directory=str(source.relative_to(ROOT)),
                 numerical_cell_string_checks=numeric_checks,source_code_sha256=sha(Path(__file__)),
                 changed_column='actual_endpoint_balance_value -> conditional_endpoint_balance_value',
                 conditional_definition='Uniform modeled cash/share roll with unchanged FY27 EBITDA and multiple; not actual future balances or an underwritten target',
                 empirical_validation_n=0,
                 output_hashes={p.name:sha(p) for p in sorted(out.iterdir())})
    with (out/'receipt.json').open('x',encoding='utf-8') as handle:json.dump(summary,handle,indent=2,sort_keys=True);handle.write('\n')
    print(json.dumps({'output':str(out),'numeric_cells_unchanged':numeric_checks},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();publish(args.input,args.out)
