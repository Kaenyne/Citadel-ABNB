"""Prepare or register a reviewed primary early-guide replay; never overwrite."""
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import os
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
METHOD = 'gbv-joint-cohort-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_rows(predictions):
    p = predictions.loc[predictions.spec == 'tail34'].copy()
    required = ['quarter', 'origin', 'knowable_from', 'guide_event_date', 'n_train', 'n_params',
                'n_cushion', 'candidate_guide_musd', 'candidate_revenue_musd']
    if p.empty or p[required].isna().any().any() or p.quarter.duplicated().any():
        raise ValueError('Primary prediction rows missing, duplicated or incomplete')
    records = []
    for r in p.itertuples():
        origin = pd.Timestamp(r.origin)
        if pd.Timestamp(r.knowable_from) > origin or origin >= pd.Timestamp(r.guide_event_date):
            raise ValueError('Pre-guide information timing violated')
        horizon = pd.Period(r.quarter, freq='Q').ordinal - origin.to_period('Q').ordinal
        if horizon < 0 or r.n_train < 8 or r.n_params != 7:
            raise ValueError('Unexpected horizon or model sample/parameter count')
        windows = ['W1'] + (['W2'] if r.quarter >= '2024Q1' else [])
        for window in windows:
            for object_name, target, point, extra in [
                ('primary-guide', 'guide_mid', r.candidate_guide_musd, 1),
                ('primary-revenue', 'revenue_musd', r.candidate_revenue_musd, 0),
            ]:
                if not np.isfinite(point) or point <= 0:
                    raise ValueError('Non-positive or non-finite prediction')
                records.append(dict(method=METHOD, object=object_name, target=target,
                    quarter=r.quarter, vintage_date=origin.date().isoformat(), horizon_q=horizon,
                    point=float(point), q50=float(point), window=window, prior_basis='PIT',
                    n_params=int(r.n_params)+extra, n_train=int(r.n_train),
                    knowable_from=str(r.knowable_from), spec_id='pooled_lag0_1_2_equal_tail3_4_early_guide_v1',
                    notes=f'Research candidate retained; prior release origin before guide; '
                          f'7 allocation parameters'+(f' plus 1 cushion parameter using {r.n_cushion} observations' if extra else '')+
                          '; point-only q50 format placeholder; no calibrated bands; effective allocation not physical cohorts; '
                          'frozen scorer ignores baseline vintage so use local paired same-origin race for promotion'))
    return pd.DataFrame(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--write', action='store_true')
    a = parser.parse_args()
    out = a.out.resolve()
    if out.exists():
        raise FileExistsError('Output directory must be new')
    data = build_rows(pd.read_csv(a.predictions))
    os.environ['CITADEL_ABNB_RUN_DATE'] = '2026-09-15'
    sys.path.insert(0, str(ROOT / 'analysis/src/forecast_methods'))
    registry = importlib.import_module('harness_v1_1.registry')
    original = registry.P.REGISTRY_DIR
    planned = [original / f'{METHOD}__{obj}.csv' for obj in data.object.unique()]
    if any(path.exists() for path in planned):
        raise FileExistsError('Registry objects already exist; do not overwrite')
    out.mkdir(parents=True)
    stage = out / 'prepared_registry'
    stage.mkdir()
    try:
        registry.P.REGISTRY_DIR = stage
        for _, frame in data.groupby('object'):
            registry.register(frame, allow_single_replay=True, quiet=True)
    finally:
        registry.P.REGISTRY_DIR = original
    if a.write:
        for path in planned:
            with path.open('xb') as f:
                f.write((stage / path.name).read_bytes())
    receipt = {'mode': 'registered' if a.write else 'prepared_only', 'method': METHOD,
               'source': str(a.predictions.resolve()), 'source_sha256': sha(a.predictions),
               'script_sha256': sha(Path(__file__)), 'rows': len(data),
               'rows_by_object_window': data.groupby(['object', 'window']).size().to_dict(),
               'staged_sha256': {path.name: sha(path) for path in stage.iterdir()},
               'forecast_promoted': False, 'predictive_intervals': False,
               'scorer_baseline_vintage_limitation': True}
    receipt['rows_by_object_window'] = {f'{key[0]}/{key[1]}': int(val) for key, val in receipt['rows_by_object_window'].items()}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
