"""Immutable Lane 4 provenance and actual-scorer snapshots."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'analysis/src/forecast_methods'
OUT = ROOT / 'data/processed/forecast_methods/lane4_control_v1'
sys.path.insert(0, str(SRC))
from lane2_validation_v1.run import compare_frames, scorer, tests


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def tracked():
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    return {p: digest(ROOT / p) for p in names if p}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    import pandas as pd
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['init', 'verify'])
    p.add_argument('--snapshot', required=True)
    p.add_argument('--fx-dependency', type=Path)
    p.add_argument('--tests', action='store_true')
    a = p.parse_args()
    if not a.snapshot.replace('_', '').replace('-', '').isalnum():
        raise ValueError('snapshot must be a simple name')
    dest = OUT / a.snapshot
    dest.mkdir(parents=True, exist_ok=False)
    receipt = {'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'command': subprocess.list2cmdline(sys.argv), 'stage': a.stage,
               'starting_commit': '1c87628cedbc94ab8a0e8552743c94485ef353b8'}
    try:
        if a.stage == 'init':
            before = tracked()
            save(dest / 'tracked_hashes.json', before)
            if not a.fx_dependency or not a.fx_dependency.is_dir():
                raise ValueError('explicit read-only FX dependency directory required')
            fx = {str(f.relative_to(a.fx_dependency)): digest(f)
                  for f in sorted(a.fx_dependency.rglob('*')) if f.is_file()}
            save(dest / 'external_fx_hashes.json', {'root': str(a.fx_dependency.resolve()), 'files': fx})
            receipt['tracked_files'] = len(before)
            receipt['external_fx_files'] = len(fx)
            receipt['head'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            if receipt['head'] != receipt['starting_commit']:
                raise AssertionError('unexpected start commit')
        else:
            baseline = OUT / 'baseline'
            before = json.loads((baseline / 'tracked_hashes.json').read_text())
            changed = [name for name, sha in before.items()
                       if not (ROOT / name).is_file() or digest(ROOT / name) != sha]
            if changed:
                raise AssertionError(f'pre-existing tracked files changed: {changed}')
            ext = json.loads((baseline / 'external_fx_hashes.json').read_text())
            fx_changed = [name for name, sha in ext['files'].items()
                          if not (Path(ext['root']) / name).is_file() or digest(Path(ext['root']) / name) != sha]
            if fx_changed:
                raise AssertionError(f'external FX dependency changed: {fx_changed}')
            receipt['all_pre_existing_hashes_unchanged'] = True
            receipt['tracked_files'] = len(before)
            receipt['external_fx_files'] = len(ext['files'])
            if a.tests:
                receipt['tests'] = tests(dest)
            v10 = scorer('harness', dest / 'format_1_0')
            v11 = scorer('harness_v1_1', dest / 'format_1_1')
            old = pd.read_csv(ROOT / 'data/processed/forecast_methods/lane2_validation_v1/close/format_1_0/scoreboard.csv')
            receipt['all_lane2_rows'] = compare_frames(old, v10, allow_extra=True)
            receipt['both_scorers'] = compare_frames(v10, v11)
            after_changed = [name for name, sha in before.items() if digest(ROOT / name) != sha]
            if after_changed:
                raise AssertionError(f'verification changed existing files: {after_changed}')
        receipt['verdict'] = 'PASS'
    except Exception as exc:
        receipt['verdict'] = 'FAIL'
        receipt['error'] = repr(exc)
        raise
    finally:
        receipt['finished_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        save(dest / 'receipt.json', receipt)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
