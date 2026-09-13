"""Independent table arithmetic and frozen-input review of L4 revenue outputs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'analysis/src/forecast_methods'))
from kernel_engine_v2 import engine as K0


def close(actual, expected, name, tol=1e-8):
    if abs(float(actual) - float(expected)) > tol:
        raise AssertionError(f'{name}: {actual} != {expected}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--revenue-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    df = pd.read_csv(a.revenue_dir / 'forecast.csv')
    op = pd.read_csv(a.revenue_dir / 'operating_inputs.csv')
    weights = pd.read_csv(a.revenue_dir / 'cohort_weights.csv')
    sources = pd.read_csv(a.revenue_dir / 'source_ledger.csv')
    for s in sources.itertuples():
        if hashlib.sha256((ROOT / s.path).read_bytes()).hexdigest() != s.sha256:
            raise AssertionError(f'Source changed: {s.path}')
    if df.duplicated(['scenario', 'quarter']).any() or len(df) != 15:
        raise AssertionError('Expected 15 unique scenario-quarter rows')
    as_of = df.as_of.unique().tolist()
    if len(as_of) != 1:
        raise AssertionError('Mixed forecast vintages')
    cushion = K0.kernel_guide('2026Q3', as_of[0])['cushion']
    kpi = pd.read_csv(ROOT / 'data/processed/overnight/02_kpi_panel_quarterly.csv')
    kpi['canonical'] = kpi.quarter.map(lambda q: f'20{q[-2:]}Q{q[0]}')
    lookup = kpi.set_index('canonical').gbv_musd.to_dict()
    lambdas = {s: K0.pit_lambda(s, as_of[0])['lambda_pct'] for s in [1, 3, 4]}
    checks = []
    for f in df.itertuples():
        parts = weights[(weights.scenario == f.scenario) & (weights.target_quarter == f.quarter)]
        if len(parts) != 2:
            raise AssertionError('Each forecast requires exactly two cohort rows')
        expected_base = 0
        for part in parts.itertuples():
            expected_q = str(pd.Period(f.quarter, freq='Q') - int(part.lag))
            if part.booking_quarter != expected_q:
                raise AssertionError('Quarter timing mismatch')
            coeff = {1: 2/3, 2: 1/3}[int(part.lag)]
            close(part.kernel_coefficient, coeff, 'fixed benchmark weight')
            if part.gbv_kind == 'reported':
                expected_gbv = lookup[part.booking_quarter]
            else:
                row = op[(op.scenario == f.scenario) & (op.quarter == part.booking_quarter)]
                if len(row) != 1:
                    raise AssertionError('Missing unique forecast GBV')
                expected_gbv = float(row.iloc[0].gbv_musd)
            close(part.gbv_musd, expected_gbv, 'GBV source')
            expected_base += coeff * expected_gbv
        close(f.kernel_base_musd, expected_base, 'kernel base')
        close(f.lambda_pct, lambdas[int(f.quarter[-1])], 'K0 lambda')
        expected_revenue = expected_base * lambdas[int(f.quarter[-1])] / 100
        close(f.revenue_musd, expected_revenue, 'revenue')
        close(f.guide_musd, expected_revenue / (1 + cushion), 'guide')
        close(parts.usd_baseline_contribution_weight.sum(), 1, 'cohort conservation')
        if pd.notna(f.incremental_fx_musd) or f.fx_integration_status != 'pending_explicit_L3_bundle':
            raise AssertionError('Unsupported FX estimate or application')
        checks.append({'scenario': f.scenario, 'quarter': f.quarter, 'independent_revenue_musd': expected_revenue,
                       'absolute_revenue_difference': abs(expected_revenue - f.revenue_musd)})
    for r in op[op.scenario != 'k0_conditional'].itertuples():
        close(r.gbv_musd, r.nights_m * r.adr_usd, 'operating identity')
    if df[df.quarter == '2026Q3'].revenue_musd.nunique() != 1:
        raise AssertionError('Contemporaneous operating inputs changed Q3 revenue')
    ref = df.set_index(['scenario', 'quarter'])
    close(ref.loc[('nights_case_a', '2026Q4'), 'revenue_musd'], ref.loc[('review_with_k', '2026Q4'), 'revenue_musd'], 'Q4 nights cannot change Q4 revenue')
    if not ref.loc[('nights_case_a', '2027Q1'), 'revenue_musd'] > ref.loc[('review_with_k', '2027Q1'), 'revenue_musd']:
        raise AssertionError('Q4 nights must enter Q1 revenue')
    bridge = pd.read_csv(a.revenue_dir / 'guide_reconciliation.csv')
    close(bridge.delta_musd.sum(), bridge.guide_musd.iloc[-1] - bridge.guide_musd.iloc[0], 'attribution reconciliation')
    result = {'verdict': 'PASS', 'source_hashes_verified': len(sources), 'forecast_rows_recomputed': len(checks),
              'maximum_revenue_difference': max(c['absolute_revenue_difference'] for c in checks),
              'checks': checks, 'limits': 'Arithmetic review of fixed benchmark only; no new conversion validation or accepted L3 inputs'}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'checks'}, indent=2))


if __name__ == '__main__':
    main()
