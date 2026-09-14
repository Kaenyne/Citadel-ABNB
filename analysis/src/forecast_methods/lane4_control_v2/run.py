"""Preserve the completed L4 baseline while verifying local L3 integration."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'data/processed/forecast_methods/lane4_control_v2'
BASE = '29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70'
L3 = '8821961853e4068febbfe2712f9a4e1036c9e629'
RESEARCH = '7fb6fe0f248d5492b899672b9b70545da62d63ee'
MANIFEST = 'data/processed/forecast_methods/l3_bundle_v1/SHA256SUMS.json'
EXPECTED = '9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def registry():
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / 'data/processed/forecast_methods/registry').glob('*.csv'))}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['init', 'verify'])
    p.add_argument('--snapshot', required=True)
    p.add_argument('--score', action='store_true')
    a = p.parse_args()
    if not a.snapshot.replace('_', '').replace('-', '').isalnum():
        raise ValueError('Use a simple new snapshot name')
    dest = OUT / a.snapshot
    dest.mkdir(parents=True, exist_ok=False)
    receipt = dict(started_utc=dt.datetime.now(dt.timezone.utc).isoformat(), command=subprocess.list2cmdline(sys.argv),
                   baseline_commit=BASE, l3_bundle_commit=L3, l3_research_commit=RESEARCH)
    try:
        if hashlib.sha256(git('show', f'{L3}:{MANIFEST}')).hexdigest() != EXPECTED:
            raise AssertionError('Accepted L3 Git manifest changed or is absent')
        subprocess.run(['git', 'merge-base', '--is-ancestor', RESEARCH, L3], cwd=ROOT, check=True)
        receipt['accepted_manifest_hash'] = EXPECTED
        if a.stage == 'init':
            if git('rev-parse', 'HEAD').decode().strip() != BASE:
                raise AssertionError('Unexpected integration starting commit')
            names = git('ls-files', '-z').decode().strip('\0').split('\0')
            hashes = {n: sha(ROOT / n) for n in names}
            save(dest / 'tracked_hashes.json', hashes)
            save(dest / 'registry_hashes.json', registry())
            receipt['pre_existing_files'] = len(hashes)
            receipt['registry_files'] = len(registry())
        else:
            baseline = OUT / 'baseline'
            hashes = json.loads((baseline / 'tracked_hashes.json').read_text(encoding='utf-8'))
            changed = [n for n, h in hashes.items() if not (ROOT / n).is_file() or sha(ROOT / n) != h]
            if changed:
                raise AssertionError(f'Pre-existing files changed: {changed[:10]}')
            old_reg = json.loads((baseline / 'registry_hashes.json').read_text(encoding='utf-8'))
            new_reg = registry()
            receipt['pre_existing_files'] = len(hashes)
            receipt['all_pre_existing_bytes_unchanged'] = True
            receipt['registry_unchanged'] = old_reg == new_reg
            if old_reg != new_reg and not a.score:
                raise AssertionError('Registry changed; required scorer verification was not requested')
            ext = json.loads((ROOT / 'data/processed/forecast_methods/lane4_control_v1/baseline/external_fx_hashes.json').read_text())
            ext_changed = [n for n, h in ext['files'].items() if not (Path(ext['root']) / n).is_file() or sha(Path(ext['root']) / n) != h]
            if ext_changed:
                raise AssertionError(f'External read-only FX bundle changed: {ext_changed[:10]}')
            receipt['external_fx_files_unchanged'] = len(ext['files'])
            if a.score:
                sys.path.insert(0, str(ROOT / 'analysis/src/forecast_methods'))
                from lane2_validation_v1.run import scorer, compare_frames
                import pandas as pd
                old_scores = pd.read_csv(ROOT / 'data/processed/forecast_methods/lane4_control_v1/close/format_1_0/scoreboard.csv')
                v10 = scorer('harness', dest / 'format_1_0')
                v11 = scorer('harness_v1_1', dest / 'format_1_1')
                receipt['historical_scores'] = compare_frames(old_scores, v10, allow_extra=True)
                receipt['both_scorers'] = compare_frames(v10, v11)
            else:
                receipt['scoring'] = 'Not repeated: registry and all historical score files are byte-identical; no new forecast registration'
        receipt['verdict'] = 'PASS'
    except Exception as exc:
        receipt['verdict'] = 'FAIL'
        receipt['error'] = repr(exc)
        raise
    finally:
        receipt['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        save(dest / 'receipt.json', receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
