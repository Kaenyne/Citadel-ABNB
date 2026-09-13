"""Run existing scorers without writing frozen outputs; reject material drift."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import importlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'analysis/src/forecast_methods'
OUT = ROOT / 'data/processed/forecast_methods/lane2_validation_v1'
sys.path.insert(0, str(SRC))
KEYS = ['method', 'object', 'target', 'window', 'prior_basis']
ATOL = 1e-9  # Existing FORMAT 1.1 frozen-score equivalence test; rtol is zero.


def compare_frames(expected, actual, keys=KEYS, allow_extra=False):
    """Require exact structure/discrete fields; float error strictly below ATOL."""
    if set(expected.columns) != set(actual.columns):
        raise AssertionError('column set changed')
    if expected.duplicated(keys).any() or actual.duplicated(keys).any():
        raise AssertionError('duplicate row key')
    a, b = expected.set_index(keys).sort_index(), actual.set_index(keys).sort_index()
    if not a.index.isin(b.index).all():
        raise AssertionError('missing expected row key')
    if not allow_extra and not a.index.equals(b.index):
        raise AssertionError('unexpected row key')
    b = b.reindex(a.index)[a.columns]
    deltas = {}
    for c in a.columns:
        x, y = a[c], b[c]
        if not x.isna().equals(y.isna()):
            raise AssertionError(f'{c}: missingness changed')
        mask = x.notna()
        if pd.api.types.is_float_dtype(x) and pd.api.types.is_numeric_dtype(y):
            xv, yv = x[mask].to_numpy(float), y[mask].to_numpy(float)
            if not np.isfinite(xv).all() or not np.isfinite(yv).all():
                raise AssertionError(f'{c}: nonfinite numeric value')
            delta = float(np.max(np.abs(xv-yv))) if len(xv) else 0.0
            deltas[c] = delta
            if delta >= ATOL:
                raise AssertionError(f'{c}: absolute drift {delta} >= {ATOL}')
        elif not x[mask].reset_index(drop=True).equals(y[mask].reset_index(drop=True)):
            raise AssertionError(f'{c}: exact value or type changed')
    return {'expected_rows': len(a), 'actual_rows': len(actual),
            'added_rows': len(actual)-len(a), 'max_abs_by_metric': deltas,
            'max_abs_difference': max(deltas.values(), default=0),
            'discrete_fields_exact': True, 'missingness_exact': True}


def frozen_hashes():
    roots = ['analysis/src/forecast_methods/harness',
             'analysis/src/forecast_methods/harness_v1_1',
             'analysis/src/forecast_methods/L0',
             'analysis/src/forecast_methods/kernel_engine_v2',
             'analysis/src/forecast_methods/returns_v1',
             'data/processed/forecast_methods/harness',
             'data/processed/forecast_methods/harness_v1_1',
             'data/processed/forecast_methods/kernel_engine_v2',
             'data/processed/forecast_methods/returns_v1',
             'data/processed/overnight/20_frozen_q3_2026.csv', 'research/thesis.md']
    files = subprocess.check_output(['git', 'ls-files', '-z', '--', *roots], cwd=ROOT).decode().split('\0')
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files if p}


def scorer(module, destination):
    mod = importlib.import_module(module + '.score')
    destination.mkdir(parents=True, exist_ok=True)
    fields = {'OUT_SCOREBOARD': destination/'scoreboard.csv',
              'OUT_SCOREBOARD_MD': destination/'scoreboard.md',
              'OUT_CONFORMAL_GRID': destination/'conformal_attainable_grid.csv'}
    stream = io.StringIO()
    with contextlib.ExitStack() as stack:
        for name, value in fields.items():
            stack.enter_context(patch.object(mod.P, name, value))
        stack.enter_context(contextlib.redirect_stdout(stream))
        rc = mod.main()
    (destination/'stdout.txt').write_text(stream.getvalue(), encoding='utf-8')
    if rc != 0:
        raise AssertionError(f'{module} scorer exit {rc}')
    print(module + ': ' + ' | '.join(stream.getvalue().splitlines()[:2]), flush=True)
    return pd.read_csv(fields['OUT_SCOREBOARD'])


def tests(destination):
    specs = [('frozen', 47, ['harness/tests', 'L0']),
             ('format_1_1', 37, ['harness_v1_1/tests']),
             ('returns', 8, ['returns_v1/tests']),
             ('kernel', 63, ['kernel_engine_v2/tests'])]
    result = {}
    for name, expected, folders in specs:
        cmd = [sys.executable, '-X', 'utf8', '-m', 'pytest',
               *[str(SRC/f) for f in folders], '-q']
        p = subprocess.run(cmd, cwd=ROOT, text=True, encoding='utf-8', capture_output=True)
        output = p.stdout+p.stderr
        (destination/f'tests_{name}.txt').write_text('COMMAND: '+subprocess.list2cmdline(cmd)+'\n'+output, encoding='utf-8')
        match = re.search(r'(\d+) passed', output)
        if p.returncode or not match or int(match[1]) != expected:
            raise AssertionError(f'{name}: exit {p.returncode}; expected {expected} tests: {output}')
        result[name] = int(match[1])
        print(f'{name}: {expected} passed', flush=True)
    return result


def loader_and_returns(destination):
    from harness_v1_1 import RUN_DATE, LIVE_VINTAGE_MIN, paths as P
    from returns_v1 import build_open_returns as B
    from returns_v1 import run as R
    ret = pd.read_csv(B.P.OPEN_RETURNS)
    original_manifest = json.loads(B.P.MANIFEST.read_text(encoding='utf-8'))
    capture = io.StringIO()
    with patch.object(B.P, 'OUT_DIR', destination), patch.object(B.P, 'OPEN_RETURNS', destination/'returns_rebuilt.csv'), contextlib.redirect_stdout(capture):
        rc = R.main([])
    (destination/'returns_stdout.txt').write_text(capture.getvalue(), encoding='utf-8')
    assert rc == 0
    rebuilt = pd.read_csv(destination/'returns_rebuilt.csv')
    comparison = compare_frames(ret, rebuilt, ['event_date'])
    assert len(ret) == 23
    assert (pd.to_datetime(ret.entry_date) > pd.to_datetime(ret.event_date)).all()
    for h in (1, 5, 20, 60):
        x = ret[f'excess_open_{h}d_pct']
        y = ret[f'open_{h}d_pct']-ret[f'qqq_open_{h}d_pct']
        np.testing.assert_allclose(x, y, rtol=0, atol=1e-9, equal_nan=True)
    legacy = pd.read_csv(B.P.LEGACY_REACTIONS)
    joined = legacy.merge(ret, left_on='quarter', right_on='print_quarter')
    med = float((joined.abnb_1d_pct-joined.cc_1d_pct).abs().median())
    lines = P.SRC_L0_VINTAGE_REGISTER.read_text(encoding='utf-8').splitlines()
    start = next(i for i, line in enumerate(lines) if line.count(',') >= 8)
    l0 = pd.read_csv(io.StringIO('\n'.join(lines[start:])))
    pg = l0[l0.register_id == 'PG-2026Q3-revenue']
    assert len(pg) == 1 and float(pg.iloc[0]['value']) == 4610
    assert str(pg.iloc[0].as_of_timestamp).startswith('2026-08-06') and bool(pg.iloc[0].pit_usable)
    cal, target = pd.read_csv(P.OUT_CALENDAR), pd.read_csv(P.OUT_TARGETS)
    assert len(cal) == len(target) == 25 and len(l0) >= 161
    assert RUN_DATE == dt.date.today()
    summary = {'calendar_rows': len(cal), 'target_rows': len(target), 'l0_rows': len(l0),
               'roles': l0.role.value_counts().to_dict(),
               'aug6_pre_guide': pg[['vendor','value','as_of_timestamp','pit_usable']].to_dict('records'),
               'return_events': len(ret), 'all_entries_strictly_after_letter': True,
               'excess_identity_atol': 1e-9, 'legacy_tieout_n': len(joined),
               'legacy_median_abs_diff_pp': med, 'returns_rebuild_comparison': comparison,
               'returns_manifest': original_manifest,
               'RUN_DATE': str(RUN_DATE), 'LIVE_VINTAGE_MIN': str(LIVE_VINTAGE_MIN), 'format': P.FORMAT_VERSION}
    print(f'returns: {len(ret)} events; every entry after letter; median legacy difference {med:.8f}pp (n={len(joined)})', flush=True)
    print(f'loader: calendar {len(cal)} / targets {len(target)} / L0 {len(l0)} / RUN_DATE {RUN_DATE}', flush=True)
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', required=True, help='New named snapshot, e.g. gate1, after_a2, close')
    p.add_argument('--tests', action='store_true')
    args = p.parse_args()
    if not re.fullmatch('[a-z0-9_]+', args.stage):
        raise ValueError('stage must be a simple lowercase slug')
    destination = OUT/args.stage
    destination.mkdir(parents=True, exist_ok=True)
    before = frozen_hashes()
    summary = {'stage': args.stage, 'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'source': 'unmodified existing scorer main functions; output destinations only redirected',
               'absolute_tolerance': ATOL, 'relative_tolerance': 0}
    try:
        if args.tests:
            summary['tests'] = tests(destination)
        sb10 = scorer('harness', destination/'format_1_0')
        sb11 = scorer('harness_v1_1', destination/'format_1_1')
        base = pd.read_csv(ROOT/'data/processed/forecast_methods/harness/scoreboard.csv')
        summary['frozen_rows_vs_1_0'] = compare_frames(base, sb10, allow_extra=True)
        summary['frozen_rows_vs_1_1'] = compare_frames(base, sb11, allow_extra=True)
        summary['both_scorers'] = compare_frames(sb10, sb11)
        summary['loader_returns'] = loader_and_returns(destination)
        summary['verdict'] = 'PASS'
    except Exception as exc:
        summary['verdict'] = 'FAIL'
        summary['error'] = repr(exc)
        raise
    finally:
        after = frozen_hashes()
        summary['frozen_hashes_unchanged'] = before == after
        summary['protected_file_count'] = len(before)
        (destination/'frozen_hashes_before.json').write_text(json.dumps(before,indent=2)+'\n', encoding='utf-8')
        (destination/'frozen_hashes_after.json').write_text(json.dumps(after,indent=2)+'\n', encoding='utf-8')
        if before != after:
            summary['verdict'] = 'FAIL'
            summary['error'] = 'frozen file hash changed'
        summary['finished_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        (destination/'summary.json').write_text(json.dumps(summary,indent=2)+'\n', encoding='utf-8')
    if summary['verdict'] != 'PASS':
        raise AssertionError(summary['error'])
    print(f'PASS: {len(base)} original scoreboard rows preserved; {len(before)} frozen file hashes unchanged', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
