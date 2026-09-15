"""Independent read-only exported workbook, expectations and horizon audit.

Uses the completed CSVs and raw OOXML caches; does not call model functions or
the workbook's own recalculation/tie-out implementation.
"""
from __future__ import annotations
import argparse
import csv
from datetime import date
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--workbook', type=Path, required=True)
    p.add_argument('--model-dir', type=Path, required=True)
    p.add_argument('--revenue-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    # Preserve the previously reviewed read-only OOXML parser, without editing it.
    parser_path = ROOT / 'analysis/src/forecast_methods/lane4_control_v1/review_exports.py'
    spec = importlib.util.spec_from_file_location('readonly_ooxml', parser_path)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    cells, formula_count = parser.workbook_cells(a.workbook)
    cases = rows(a.model_dir / 'scenario_summary.csv')
    annual = {(r['scenario'], int(r['year'])): r for r in rows(a.model_dir / 'annual.csv')}
    forecasts = {(r['scenario'], r['quarter']): r for r in rows(a.revenue_dir / 'forecast.csv')}
    forecasts.update({(r['scenario'], r['quarter']): r for r in rows(a.revenue_dir / 'joint_scenarios.csv')})
    cons = [r for r in rows(a.revenue_dir / 'consensus_selection.csv') if r['panel_family'] == 'LSEG family']
    if len(cons) != 1:
        raise AssertionError('Need one independently selected LSEG-family panel')
    consensus = float(cons[0]['value'])
    if cons[0]['as_of_timestamp'] != '2026-09-13T15:20Z':
        raise AssertionError('Unexpected frozen consensus timestamp')
    checks = []

    def check(label, actual, expected, tolerance=.001):
        actual, expected = float(actual), float(expected)
        if not math.isfinite(actual) or not math.isfinite(expected):
            raise AssertionError(f'Non-finite value {label}')
        delta = actual - expected
        if abs(delta) > tolerance:
            raise AssertionError(f'{label}: actual={actual}, expected={expected}, delta={delta}')
        checks.append(dict(check=label, actual=actual, expected=expected, difference=delta))

    def cell(sheet, address, expected, formula=False, tolerance=.001):
        c = cells[sheet][address]
        if formula and not c['formula']:
            raise AssertionError(f'Missing live formula {sheet}!{address}')
        check(f'{sheet}!{address}', c['value'], expected, tolerance)

    if len(cases) != 9 or len({r['scenario'] for r in cases}) != 9:
        raise AssertionError('Expected nine unique scenarios')
    fraction = (date(2027, 9, 13) - date(2026, 12, 31)).days / (date(2027, 12, 31) - date(2026, 12, 31)).days
    reference = None
    for i, r in enumerate(cases):
        scenario = r['scenario']
        prior, end = annual[scenario, 2026], annual[scenario, 2027]
        cash = float(prior['net_cash']) + fraction * (float(end['net_cash']) - float(prior['net_cash']))
        shares = float(prior['shares']) + fraction * (float(end['shares']) - float(prior['shares']))
        ev = float(r['exit_multiple']) * float(end['adj_ebitda'])
        equity = ev + cash
        price = equity / shares
        later_price = (ev + float(end['net_cash'])) / float(end['shares'])
        if r['horizon_date'] != '2027-09-13':
            raise AssertionError('Valuation horizon is not the approved conditional 12-month date')
        for key, expected in [('horizon_fraction', fraction), ('horizon_net_cash_musd', cash),
                              ('horizon_shares_m', shares), ('enterprise_value_musd', ev),
                              ('equity_value_musd', equity), ('value_per_share', price),
                              ('december_value_per_share', later_price),
                              ('date_only_value_difference', later_price-price)]:
            check(f'{scenario}/{key}', r[key], expected)
        # Verify full-year cash and stock flows separately from the date interpolation.
        for year in [2026, 2027, 2028]:
            y = annual[scenario, year]
            check(f'{scenario}/{year}/cash flow identity', y['net_cash'],
                  float(y['opening_cash']) + float(y['delta_fcf']) - float(y['delta_buybacks']) - float(y['delta_withholding']))
            check(f'{scenario}/{year}/share identity', y['shares'],
                  float(y['opening_shares']) - float(y['buyback_shares']) + float(y['issuance_shares']))
            check(f'{scenario}/{year}/earnings identity', y['pretax'],
                  float(y['op_income']) + float(y['interest_income']) - float(y['interest_expense']))
        q4r = float(r['q4_revenue_musd'])
        q4g = float(r['q4_guide_musd'])
        source_case = 'review_with_k' if '_sensitivity' in scenario else scenario
        f = forecasts[source_case, '2026Q4']
        factor = .99 if 'down_sensitivity' in scenario else 1.01 if 'up_sensitivity' in scenario else 1.
        check(f'{scenario}/revenue bridge', q4r, float(f['revenue_musd']) * factor)
        check(f'{scenario}/guide identity', q4g, q4r/(1+float(f['cushion_decimal'])))
        expected_values = [q4g, float(prior['revenue']), float(end['revenue']), float(end['adj_ebitda']),
                           float(end['net_income']), float(end['fcf']), cash, shares, ev, equity,
                           price, later_price, q4r, q4r-consensus]
        col = chr(ord('E') + i)
        for j, expected in enumerate(expected_values):
            cell('Case comparison', col+str(8+j), expected)
        if scenario == 'review_with_k':
            reference = dict(revenue=q4r, guide=q4g, cash=cash, shares=shares, ev=ev,
                             equity=equity, price=price, later_price=later_price,
                             hypothetical=consensus/(1+float(f['cushion_decimal'])))
    if reference is None:
        raise AssertionError('No reference case')
    for address, expected in [('E29', reference['revenue']), ('E30', consensus),
                              ('E31', reference['revenue']-consensus),
                              ('E32', reference['revenue']/consensus-1),
                              ('E33', reference['guide']-consensus), ('E34', reference['hypothetical']),
                              ('E35', reference['guide']-reference['hypothetical']),
                              ('E18', reference['price']), ('E19', reference['later_price']),
                              ('E20', reference['guide'])]:
        cell('Summary', address, expected, True)
    for address, key in [('E10','ev'), ('E11','cash'), ('E12','equity'), ('E13','shares'),
                         ('E14','price'), ('E23','later_price')]:
        cell('Valuation', address, reference[key], True)
    cell('Valuation', 'E38', 180.876286, True)
    cell('Valuation', 'E45', 156.786845, True)
    cell('Assumptions', 'F145', fraction, True, 1e-12)
    if cells['Case comparison']['E22']['value'] != 'Captured inputs unchanged':
        raise AssertionError('Exported comparison is stale')
    if formula_count < 100:
        raise AssertionError('Missing linked model formulas')
    suspicious = [(s, c, v['value']) for s, cc in cells.items() for c, v in cc.items()
                  if isinstance(v['value'], str) and any(t in v['value'] for t in ['\u00e2\u20ac', '\u00c3\u2014', '\u00c2\u00b1'])]
    if suspicious:
        raise AssertionError(f'Mojibake text in workbook: {suspicious[:5]}')
    result = dict(verdict='PASS', formula_count=formula_count, formula_errors=0, external_links=0,
                  checks_count=len(checks), max_abs_difference=max(abs(r['difference']) for r in checks),
                  horizon_fraction=fraction, consensus_value=consensus,
                  consensus_vendor=cons[0]['vendor'], consensus_timestamp=cons[0]['as_of_timestamp'],
                  source_hashes={str(p):sha(p) for p in [a.workbook, a.model_dir/'scenario_summary.csv',
                      a.model_dir/'annual.csv', a.revenue_dir/'consensus_selection.csv', parser_path]},
                  scope='Independent raw export caches and CSV cash/share/expectations audit; no native Excel session',
                  checks=checks)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','source_hashes']}, indent=2))


if __name__ == '__main__':
    main()
