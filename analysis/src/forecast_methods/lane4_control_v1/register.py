"""Parent-owned, current conditional revenue/guide registration (FORMAT 1.1)."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'analysis/src/forecast_methods'))
from harness_v1_1 import registry as R, RUN_DATE

SCENARIOS = ['review_with_k', 'review_without_k', 'nights_case_a', 'adr_mean_reversion']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--revenue-dir', type=Path, required=True)
    p.add_argument('--snapshot', required=True)
    p.add_argument('--register', action='store_true')
    a = p.parse_args()
    if RUN_DATE != dt.date.today():
        raise ValueError('Do not override the real registration run date')
    source = a.revenue_dir / 'forecast.csv'
    df = pd.read_csv(source)
    if df.duplicated(['scenario', 'quarter']).any():
        raise ValueError('Duplicate forecast scenario-quarter')
    targets = pd.read_csv(ROOT / 'data/processed/forecast_methods/harness/targets.csv')
    if not {'revenue_musd', 'guide_mid'} <= set(targets.columns):
        raise ValueError('Target metric absent from frozen harness')
    today = RUN_DATE.isoformat()
    if set(df.as_of) != {today}:
        raise ValueError('Rebuild the forecast at the real run date before registering it')
    if not a.snapshot.replace('_', '').replace('-', '').isalnum():
        raise ValueError('Simple new snapshot name required')
    dest = ROOT / 'data/processed/forecast_methods/lane4_control_v1' / a.snapshot
    dest.mkdir(parents=True, exist_ok=False)
    pending, inventory = [], []
    for scenario in SCENARIOS:
        rows = []
        quarters = ['2027Q1'] if scenario == 'nights_case_a' else ['2026Q4', '2027Q1']
        for q in quarters:
            matches = df[(df.scenario == scenario) & (df.quarter == q)]
            if len(matches) != 1:
                raise ValueError(f'Missing unique forecast {scenario}/{q}')
            f = matches.iloc[0]
            if f.fx_integration_status != 'pending_explicit_L3_bundle' or pd.notna(f.incremental_fx_musd):
                raise ValueError('This registration is only for reviewed baseline objects; L3 requires a new review')
            if f.conversion_status != 'fixed_K0_2over3_benchmark_provisional_pending_L3_conversion_validation':
                raise ValueError('Conversion replacement requires an explicit accepted L3 review')
            for column, target in [('revenue_musd', 'revenue_musd'), ('guide_musd', 'guide_mid')]:
                value = float(f[column])
                notes = (f'LIVE conditional review, not adopted; {scenario}; no W1/W2 observations; '
                         'deterministic point copied to q50, no calibrated distribution; L3 conversion and FX/RNPL pending; '
                         'USD GBV embeds booking FX, historical lambda embeds reported accounting/hedges; '
                         '5 inherited parameters: four seasonal lambdas and cushion, zero new fit; '
                         f'seasonal lambda n={int(f.lambda_n_train)}, cushion n={int(f.cushion_n_train)}')
                rows.append(dict(method='l4-review-v1', object=scenario.replace('_', '-'), target=target,
                                 quarter=q, vintage_date=today,
                                 horizon_q=(int(q[:4]) - RUN_DATE.year) * 4 + int(q[-1]) - ((RUN_DATE.month - 1) // 3 + 1),
                                 point=value, q50=value, window='LIVE', prior_basis='PIT',
                                 n_params=5, n_train=int(f.lambda_n_train), knowable_from=today,
                                 spec_id='lane4_revenue_v1_baseline', notes=notes))
        frame = pd.DataFrame(rows)
        validated = R.validate_registry_frame(frame)
        path = R.registry_path('l4-review-v1', scenario.replace('_', '-'))
        if path.exists():
            raise FileExistsError(f'Registration would overwrite existing file: {path}')
        validated.to_csv(dest / path.name, index=False)
        pending.append(frame)
        inventory.extend(rows)
    # Validate every file before the first shared-registry write.
    published = []
    if a.register:
        for frame in pending:
            published.append(str(R.register(frame).relative_to(ROOT)))
    pd.DataFrame(inventory).to_csv(dest / 'inventory.csv', index=False)
    receipt = dict(run_date=today, rows=len(inventory), objects=len(pending), registered=a.register,
                   paths=published, source=str(source.resolve()), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   omitted='Unchanged Q3 K0 result, K0 conditional comparison, duplicate nights-case-A Q4, all unsupported FX estimates',
                   historical_claim='None; LIVE only; PIT means current information set, not historical validation')
    (dest / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
