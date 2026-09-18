"""Run unchanged scorers to new directories and verify pre-existing file hashes."""
from pathlib import Path
import argparse
import importlib
import importlib.util
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[5]
os.environ['CITADEL_ABNB_RUN_DATE'] = '2026-09-15'
sys.path.insert(0, str(ROOT / 'analysis/src/forecast_methods'))
HELPER = ROOT / 'analysis/src/forecast_methods/gbv_event_v1/registry_scoring/run.py'
spec = importlib.util.spec_from_file_location('prior_preservation_helpers', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--before', type=Path)
    args = p.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError('Output directory must be new')
    protected = {str(path.relative_to(ROOT)).replace('\\', '/'): helper.sha(path)
                 for path in helper.protected_paths()}
    if args.before:
        original = json.loads((args.before / 'protected.json').read_text())
        failures = [rel for rel, sha in original.items() if protected.get(rel) != sha]
        if failures:
            raise ValueError(f'Pre-existing protected files changed: {failures}')
    out.mkdir(parents=True)
    (out / 'protected.json').write_text(json.dumps(protected, indent=2), encoding='utf-8')
    tables = {}
    for name, module_name in [('format_1_0', 'harness.score'), ('format_1_1', 'harness_v1_1.score')]:
        tables[name] = helper.score_to(importlib.import_module(module_name), out / name)
    cross = helper.comparison(tables['format_1_0'], tables['format_1_1'], 'format_equality')
    if cross:
        raise ValueError(f'Scorer disagreement: {cross[:5]}')
    receipt = {'scorer_exit_codes': [0, 0], 'formats_equal': True,
               'score_rows': len(tables['format_1_0']), 'protected_files': len(protected),
               'helper_sha256': helper.sha(HELPER), 'wrapper_sha256': helper.sha(Path(__file__))}
    if args.before:
        import pandas as pd
        old = pd.read_csv(args.before / 'format_1_0/scoreboard.csv')
        new_existing = tables['format_1_0'].loc[tables['format_1_0'].method.isin(old.method.unique())]
        delta = helper.comparison(old, new_existing, 'existing_scores_unchanged')
        if delta:
            raise ValueError(f'Existing method scores changed: {delta[:5]}')
        receipt['existing_score_rows_unchanged'] = len(old)
        receipt['original_protected_files_unchanged'] = len(original)
    after = {rel: helper.sha(ROOT / rel) for rel in protected}
    if after != protected:
        raise ValueError('Scoring changed an existing protected file')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
