"""Read-only audit checks of exact PR41 sources and committed outputs.

Source PR41: 5a590cedb42928666c580e06974947c301e2bbab
All synthetic outputs are confined to this audit directory.
"""
import csv
import importlib.util
import json
import math
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
DATA = SOURCE / 'data/processed/q3nowcast/E'


def read(name):
    with (DATA / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def key(row):
    return tuple(row[k] for k in ('feature', 'lag', 'target', 'window'))


def ratio(rows):
    return math.sqrt(sum(float(r['err_feature']) ** 2 for r in rows) /
                     sum(float(r['err_naive']) ** 2 for r in rows))


def robustness():
    tests = defaultdict(list)
    paths = defaultdict(list)
    pooled = {key(r): r for r in read('backtest_survivor_robustness.csv')}
    for r in read('backtest_abnb_quarterly.csv'):
        if r['wf_ratio_vs_naive'] and float(r['wf_ratio_vs_naive']) < 1:
            tests[key(r)].append(r)
    for r in read('backtest_wf_paths.csv'):
        paths[key(r)].append(r)
    collision_groups = 0
    false_robust = []
    max_ratio_error = 0
    # E5 traverses level before d1; each group's path contains complete runs
    # in the same order as backtest_abnb_quarterly.csv. Verify that recovery
    # against every original RMSE ratio, rather than assuming the split.
    for k, variants in tests.items():
        start = 0
        collision_groups += len(variants) > 1
        for r in variants:
            count = int(float(r['wf_n']))
            p = paths[k][start:start + count]
            start += count
            error = abs(ratio(p) - float(r['wf_ratio_vs_naive']))
            max_ratio_error = max(max_ratio_error, error)
            assert error < 1e-12
            assert len({v['qi'] for v in p}) == count
            if len(variants) < 2:
                continue
            true_max = max(ratio(p[:i] + p[i + 1:]) for i in range(count))
            pooled_max = float(pooled[k]['jk_max'])
            if true_max > 1 >= pooled_max:
                false_robust.append(dict(zip(('feature', 'lag', 'target', 'window'), k),
                    transform=r['transform'], true_jk_max=true_max,
                    pooled_jk_max=pooled_max, true_wf_n=count,
                    pooled_wf_n=int(float(pooled[k]['wf_n']))))
        assert start == len(paths[k])
    return {'collision_groups': collision_groups,
            'max_recovered_ratio_error': max_ratio_error,
            'false_robust_variants': len(false_robust),
            'false_robust_nights_variants': sum(r['target'] == 'nights_yoy' for r in false_robust),
            'examples': false_robust}


def coverage():
    rows = [r for r in read('vintage_matched_nowcast_market.csv')
            if r['period'] == '3q26_to_date']
    days = [(date.fromisoformat(r['win_end']) - date.fromisoformat(r['win_start'])).days + 1
            for r in rows]
    weights = [float(r['n_prior_oldvintage']) for r in rows]
    weighted_days = sum(d * w for d, w in zip(days, weights)) / sum(weights)
    return {'markets': len(rows), 'min_days': min(days), 'max_days': max(days),
            'median_days': statistics.median(days),
            'median_fraction_of_92day_quarter': statistics.median(days) / 92,
            'prior_review_weighted_days': weighted_days,
            'prior_review_weighted_fraction': weighted_days / 92}


def september_refresh():
    import pandas as pd
    mod_path = SOURCE / 'analysis/src/q3nowcast/E6_nowcast.py'
    spec = importlib.util.spec_from_file_location('audit_e6', mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUT = ROOT / 'synthetic_september_output'
    mod.OUT.mkdir(exist_ok=True)
    dates = pd.date_range('2025-06-01', '2026-09-30')
    d = pd.DataFrame({'market_key': 'example', 'region': 'NAM',
                      'dump_date': pd.Timestamp('2026-09-30'), 'review_date': dates,
                      'n_reviews': [20 if x.year == 2026 and x.month == 9 else 10 for x in dates]})
    market, _ = mod.monthly_2026(d, 14)
    aug = market[market.period == '2026-08_to_date'].iloc[0]
    assert aug.win_end == '2026-09-16'
    assert abs(aug.yoy - 160 / 470) < 1e-12
    return {'label': aug.period, 'actual_window_end': aug.win_end,
            'reported_august_growth_pct': aug.yoy * 100,
            'correct_august_growth_pct': 0.0,
            'mechanism': 'August label includes September 1-16 reviews after the September refresh'}


def median_gap():
    rows = read('partial_vs_full_quarter_market.csv')
    gaps = []
    for year in (2023, 2024, 2025):
        group = [r for r in rows if int(r['year']) == year]
        gaps.append(100 * (statistics.median(float(r['full_yoy']) for r in group) -
                           statistics.median(float(r['partial_yoy']) for r in group)))
    mean, sd = statistics.mean(gaps), statistics.stdev(gaps)
    row = next(r for r in read('q3_2026_nowcast.csv') if r['weighting'] == 'w_median')
    forecast = float(row['intercept']) + float(row['slope']) * (float(row['partial_index_3q26_pct']) + mean)
    band = math.sqrt(float(row['wf_rmse_pp']) ** 2 + (float(row['slope']) * sd) ** 2)
    return {'median_gaps_pp': gaps, 'correct_mean_gap_pp': mean, 'correct_sd_gap_pp': sd,
            'used_mean_gap_pp': float(row['gap_mean_pp']),
            'used_sd_gap_pp': float(row['gap_sd_pp']),
            'original_nights_forecast': float(row['implied_nights_yoy']),
            'corrected_median_variant_nights_forecast': forecast,
            'original_band_pp': float(row['band_pp']), 'corrected_band_pp': band}


if __name__ == '__main__':
    result = {'robustness': robustness(), 'coverage': coverage(),
              'september_refresh': september_refresh(), 'median_gap': median_gap()}
    (ROOT / 'reproduction_results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({**result,
        'robustness': {k: v for k, v in result['robustness'].items() if k != 'examples'}}, indent=2))
