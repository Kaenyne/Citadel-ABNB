"""Rebuild the bounded validation with frozen inputs and fresh, versioned outputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CODE = Path(__file__).resolve().parent
DATA = ROOT / 'data/processed/forecast_methods/quant_thesis_validation_v1'
DOCS = ROOT / 'docs/revenue-forecast-strategy/quant_thesis_validation_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True, help='Unused alphanumeric identifier, e.g. final_v1')
    parser.add_argument('--pdf-python', type=Path, required=True, help='Python executable with reportlab and pypdf')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,39}', args.run_id):
        parser.error('run-id must be 1-40 alphanumeric, underscore or hyphen characters')
    pdf_python = args.pdf_python.resolve(strict=True)
    tag = 'rebuild_' + args.run_id
    out = DATA / 'reproductions' / args.run_id
    paths = {
        'source': DATA / 'source_audit_v1' / tag,
        'uncertainty': DATA / 'uncertainty_audit_v1' / tag,
        'prospective': DATA / 'prospective_v1' / tag,
        'economics_calculation': DATA / 'economics_v1' / (tag + '_calculation'),
        'economics_publication': DATA / 'economics_v1' / (tag + '_publication'),
        'accounting_review': DATA / 'accounting_review_v1' / tag,
        'independent_reproduction': DATA / 'independent_reproduction_v1' / tag,
        'economic_review': DATA / 'adversarial_review_v1' / tag,
        'contract_review': DATA / 'final_contract_review_v1' / tag,
        'expectations': out / 'expectations', 'claims': out / 'claims',
        'verification': out / 'verification', 'forecast_figure': out / 'forecast_figure',
        'expectations_figure': out / 'expectations_figure',
    }
    for p in [out, *paths.values()]:
        if p.exists():
            raise FileExistsError(f'Choose an unused run-id; existing output: {p}')
        if not p.resolve().is_relative_to(DATA.resolve()):
            raise ValueError(f'Output outside this research package: {p}')
    # Fail dependency checks before creating the attempt directory.
    versions = {name: importlib.metadata.version(name) for name in ('numpy', 'pandas', 'matplotlib')}
    subprocess.run([str(pdf_python), '-B', '-c', 'import reportlab, pypdf'], check=True, cwd=ROOT)
    out.mkdir(parents=True)
    receipt = {
        'status': 'RUNNING', 'run_id': args.run_id,
        'observed_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'python': sys.executable, 'pdf_python': str(pdf_python), 'versions': versions,
        'runner_sha256': sha(Path(__file__)),
        'protocol_sha256': sha(DOCS / 'FINAL_PROTOCOL_v1.md'),
        'outputs': {k: str(p.relative_to(ROOT)) for k, p in paths.items()},
        'steps': [], 'research_hurdle': 'FAIL', 'forecast_promoted': False,
        'production_registration': False, 'new_weight_fits': 0, 'new_resamples': 0,
        'random_seed': None, 'seed_reason': 'No random procedure is run; accepted draws are immutable inputs.',
        'review_limit': 'Numerical checks are rerun. Narrative and visual signoff apply to the separately hash-bound canonical deliverables.'
    }

    def save():
        # This live receipt belongs only to this new attempt. Canonical receipts are never modified.
        (out / 'run_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')

    def execute(label, script=None, arguments=(), python=None, module=None):
        cmd = [str(python or sys.executable), '-B', '-X', 'utf8']
        cmd += ['-m', module] if module else [str(CODE / script)]
        cmd += [str(x) for x in arguments]
        step = {'label': label, 'command_argv': cmd, 'cwd': str(ROOT)}
        receipt['steps'].append(step)
        save()
        start = time.monotonic()
        with (out / (label + '.log')).open('x', encoding='utf-8') as log:
            result = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, text=True)
        step.update(exit_code=result.returncode, elapsed_seconds=round(time.monotonic()-start, 3))
        save()
        print(f'{label}: exit {result.returncode}', flush=True)
        if result.returncode:
            raise RuntimeError(f'{label} failed; retain {out / (label + ".log")}')

    try:
        execute('01_evidence', 'verify_evidence.py', ['--out', paths['verification']])
        for label, script, key in [
            ('02_source', 'source_audit_v1/run.py', 'source'),
            ('03_uncertainty', 'uncertainty_audit_v1/run_v2.py', 'uncertainty'),
            ('04_prospective', 'prospective_v1/run.py', 'prospective'),
            ('05_expectations', 'expectations_bridge_v2.py', 'expectations'),
            ('06_economics', 'economics_v1/run.py', 'economics_calculation'),
        ]:
            execute(label, script, ['--out', paths[key]])
        execute('07_economic_publication', 'economics_v1/publish_v2.py', [
            '--input', paths['economics_calculation'], '--out', paths['economics_publication']])
        for label, package, key, script in [
            ('08_accounting_review', 'accounting_review_v1', 'accounting_review', 'run_v2.py'),
            ('09_independent_reproduction', 'independent_reproduction_v1', 'independent_reproduction', 'run_v2.py'),
            ('10_economic_review', 'adversarial_review_v1', 'economic_review', 'run.py'),
            ('11_contract_review', 'final_contract_review_v1', 'contract_review', 'run.py'),
        ]:
            execute(label, package + '/' + script, ['--out', paths[key]])
        for label, package, pattern in [
            ('12_prospective_tests', 'prospective_v1', 'test_prospective.py'),
            ('13_economic_tests', 'economics_v1', 'test_economics.py'),
        ]:
            execute(label, module='unittest', arguments=['discover', '-s', CODE/package, '-p', pattern, '-v'])
        execute('14_claims', 'write_claims_v2.py', ['--out', paths['claims']])
        execute('15_forecast_figure', 'forecast_figure_v3.py', [
            '--source', paths['prospective']/'evaluation/scores.csv', '--out', paths['forecast_figure']])
        execute('16_expectations_figure', 'expectations_figure.py', ['--out', paths['expectations_figure']])
        execute('17_summary', 'render_summary.py', ['--source', DOCS/'DECISION_SUMMARY_v3.json',
            '--out', out/'ABNB_decision_summary.pdf'], python=pdf_python)
        pairs = [
            (DATA/'source_audit_v1/results_v3', paths['source'], '*'),
            (DATA/'uncertainty_audit_v1/results_v2', paths['uncertainty'], '*.csv'),
            (DATA/'prospective_v1/results_v1', paths['prospective'], '**/*'),
            (DATA/'expectations_v2', paths['expectations'], '*.csv'),
            (DATA/'economics_v1/results_v2', paths['economics_publication'], '*.csv'),
            (DATA/'claims_v2', paths['claims'], '*'),
        ]
        checks = []
        for canonical, fresh, pattern in pairs:
            for original in sorted(canonical.glob(pattern)):
                if not original.is_file():
                    continue
                target = fresh / original.relative_to(canonical)
                checks.append({'canonical': str(original.relative_to(ROOT)), 'fresh': str(target.relative_to(ROOT)),
                    'canonical_sha256': sha(original), 'fresh_sha256': sha(target),
                    'same_bytes': original.read_bytes() == target.read_bytes()})
        with (out/'canonical_comparison.csv').open('x', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(checks[0]))
            writer.writeheader(); writer.writerows(checks)
        if not all(c['same_bytes'] for c in checks):
            raise AssertionError('Canonical output byte mismatch; see canonical_comparison.csv')
        receipt.update(status='PASS_complete_bounded_rebuild', exact_output_comparisons=len(checks),
            source_notes='Reviewers also bind and independently reconstruct canonical source outputs. Figure 16 consumes canonical expectations after exact CSV equality is checked.',
            artifact_reproduction='CSV/JSON tables listed in comparison are exact. PDF/SVG creation metadata may differ; PDF enforces one page and canonical source text. No byte-reproducibility claim for generated media.')
    except Exception as exc:
        receipt.update(status='FAIL_attempt_preserved', error=repr(exc))
        save()
        raise
    save()
    print(json.dumps({'status': receipt['status'], 'research_hurdle': 'FAIL',
                      'receipt': str(out/'run_receipt.json')}, indent=2))


if __name__ == '__main__':
    main()
