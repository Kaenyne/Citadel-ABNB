"""Rebuild the independent technical checks; this does not issue a new human review."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import early_contract_checks
import uncertainty_independent_checks

ROOT = Path(__file__).resolve().parents[5]
ALLOWED = ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1/final_contract_review_v1'


def main(out):
    out=out.resolve()
    if not out.is_relative_to(ALLOWED.resolve()):
        raise ValueError('Use the exclusive final_contract_review_v1 directory')
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    early_contract_checks.OUT=out/'contract_checks'
    early_contract_checks.main()
    uncertainty_independent_checks.main(out/'uncertainty_checks')
    status=subprocess.check_output(['git','status','--porcelain','--',
        'data/processed/forecast_methods/registry',
        'analysis/src/forecast_methods/harness',
        'analysis/src/forecast_methods/harness_v1_1','model'],cwd=ROOT,text=True)
    if status.strip():
        raise AssertionError('Protected scorer/model/registry status changed: '+status)
    receipt=dict(status='PASS_REBUILT_TECHNICAL_CHECKS',new_human_claim_or_visual_signoff=False,
        protected_git_status_clean=True,own_economic_calculations_independently_reviewed_here=False,
        command=[sys.executable,'-B',str(Path(__file__).resolve()),'--out',str(out)],
        scope='Frozen identities, admissible information dates, accepted arithmetic and existing review bindings')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path)
    main(parser.parse_args().out)
