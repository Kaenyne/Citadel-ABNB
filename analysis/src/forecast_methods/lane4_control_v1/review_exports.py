"""Independent read-only audit of exported XLSX cached formulas and model CSVs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = '{http://schemas.openxmlformats.org/package/2006/relationships}'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def workbook_cells(path):
    with ZipFile(path) as z:
        if any(n.startswith('xl/externalLinks/') for n in z.namelist()):
            raise AssertionError('Workbook contains external links')
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        relationships = {n.attrib['Id']: n.attrib['Target']
                         for n in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets = ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets', NS)
        results, formula_count, error_cells = {}, 0, []
        for item in sheets:
            target = relationships[item.attrib['{' + NS['r'] + '}id']]
            member = target.lstrip('/') if target.startswith('/') else str(PurePosixPath('xl') / target)
            cells = {}
            for c in ET.fromstring(z.read(member)).findall('.//s:c', NS):
                v, f = c.find('s:v', NS), c.find('s:f', NS)
                kind = c.attrib.get('t')
                value = v.text if v is not None else None
                if kind == 's' and value is not None:
                    value = strings[int(value)]
                elif kind == 'inlineStr':
                    value = ''.join(c.find('s:is', NS).itertext())
                elif kind not in ['str', 'e'] and value is not None:
                    value = float(value)
                if kind == 'e':
                    error_cells.append(f"{item.attrib['name']}!{c.attrib['r']}={value}")
                if f is not None:
                    formula_count += 1
                cells[c.attrib['r']] = {'value': value, 'formula': None if f is None else f.text}
            results[item.attrib['name']] = cells
    if error_cells:
        raise AssertionError(f'Exported formula errors: {error_cells[:20]}')
    return results, formula_count


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--workbook', type=Path, required=True)
    p.add_argument('--model-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    cells, count = workbook_cells(a.workbook)
    rows = list(csv.DictReader((a.model_dir / 'scenario_summary.csv').open(encoding='utf-8-sig')))
    if len(rows) != 7:
        raise AssertionError('Expected seven explicitly labelled model cases')
    metrics = ['q4_guide_musd', 'fy26_revenue_musd', 'fy27_revenue_musd', 'fy27_ebitda_musd',
               'fy27_net_income_musd', 'fy27_fcf_musd', 'fy27_net_cash_musd', 'fy27_shares_m',
               'enterprise_value_musd', 'equity_value_musd', 'value_per_share', 'six_lens_mean']
    checks = []

    def check(sheet, cell, expected, require_formula=False):
        c = cells[sheet][cell]
        actual = c['value']
        if not isinstance(actual, (int, float)) or not math.isfinite(actual):
            raise AssertionError(f'Missing numeric exported cache {sheet}!{cell}: {actual}')
        if require_formula and not c['formula']:
            raise AssertionError(f'Expected live formula {sheet}!{cell}')
        delta = actual - expected
        if abs(delta) > .001:
            raise AssertionError(f'Cached export mismatch {sheet}!{cell}: {delta}')
        checks.append({'sheet': sheet, 'cell': cell, 'expected': expected, 'exported_cached_value': actual,
                       'delta': delta, 'formula': c['formula']})

    for i, row in enumerate(rows):
        col = chr(ord('E') + i)
        for j, metric in enumerate(metrics):
            check('Case comparison', col + str(8 + j), float(row[metric]))
    ref = next(r for r in rows if r['scenario'] == 'review_with_k')
    for sheet, cell, metric in [('Summary', 'E20', 'q4_guide_musd'), ('Valuation', 'E14', 'value_per_share'),
                                ('Valuation', 'E10', 'enterprise_value_musd'), ('Valuation', 'E12', 'equity_value_musd'),
                                ('Valuation', 'E13', 'fy27_shares_m')]:
        check(sheet, cell, float(ref[metric]), True)
    check('Valuation', 'E38', 180.876286, True)
    check('Valuation', 'E45', 156.786845, True)
    if count < 100:
        raise AssertionError('Expected substantial linked model formulas')
    if cells['Case comparison']['E22']['value'] != 'Captured inputs unchanged':
        raise AssertionError('Exported comparison is stale')
    result = {'verdict': 'PASS', 'exported_formula_count': count, 'formula_errors': 0, 'external_links': 0,
              'independent_cached_value_checks': len(checks), 'max_abs_difference': max(abs(c['delta']) for c in checks),
              'workbook_sha256': sha(a.workbook), 'scenario_csv_sha256': sha(a.model_dir / 'scenario_summary.csv'),
              'checks': checks, 'scope': 'Read-only OOXML export audit; separate from in-memory artifact recalculation'}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'checks'}, indent=2))


if __name__ == '__main__':
    main()
