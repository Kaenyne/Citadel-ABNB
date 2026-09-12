"""Reproduce PR40 audit findings from frozen source/CSV files; no network calls."""
from pathlib import Path
import ast
import importlib.util
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
SNAP = ROOT / 'snapshot'
path = SNAP / 'analysis/src/overnight2/D1_rnpl_cohort_scenarios.py'
spec = importlib.util.spec_from_file_location('audit_d1', path)
d1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d1)

cross = d1.bundle_crosscheck()
gaps = d1.exna_4q26_gap()
bound_rows = []
for x, gap in zip([x for x in cross if x['quarter'] == '4Q25'], gaps):
    bound_rows.append({'bundle_4q25_pp': x['pr32_total_pts'],
                      'passes_disclosed_lower_bound': x['pr32_total_pts'] > 2.0,
                      'code_consistency_flag': gap['consistent_with_4q25_disclosure'],
                      'selected_q4_growth_pct': gap['adjusted_4q26_pct']})
assert all(x['passes_disclosed_lower_bound'] for x in bound_rows)
assert len([x for x in bound_rows if x['code_consistency_flag'].startswith('no')]) == 2
min_share = (2.0 - (2.40 + 2.29) * .288) / 1.75

# Unit-accounting counterexample to D1's proposed GBV-minus-nights signal.
n0, gbv0, lost_nights, cancelled_adr = 100.0, 10000.0, 10.0, 125.0
n1, gbv1 = n0-lost_nights, gbv0-lost_nights*cancelled_adr
night_growth = 100*(n1/n0-1)
gbv_growth = 100*(gbv1/gbv0-1)
assert gbv_growth < night_growth

# Use the exact qkey function from B3, without executing its IO or regressions.
b3 = SNAP / 'analysis/src/overnight2/B3_mix_tests.py'
tree = ast.parse(b3.read_text(encoding='utf-8'))
qfn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'qkey')
ns = {}
exec(compile(ast.Module(body=[qfn], type_ignores=[]), str(b3), 'exec'), ns)
old_key = ns['qkey']
good_key = lambda q: (2000+int(q[2:]))*4+int(q[0])-1
assert old_key('4Q19') > old_key('1Q20')
assert good_key('4Q19') < good_key('1Q20')
panel = pd.read_csv(SNAP / 'data/processed/overnight2/B/regional_target_panel.csv')
cbs = panel[(panel.metric == 'cross_border_share_of_gross_nights_pct') & (panel.region == 'total')].copy()
cbs['k'] = cbs.quarter.map(old_key)
cbs = cbs.drop_duplicates('k').sort_values('k')
cbs['prior_quarter_used'] = cbs.quarter.shift(4)
cbs['yoy_change_pp'] = cbs.value - cbs.value.shift(4)
bad_2019 = cbs[cbs.quarter.str.endswith('19')][['quarter','prior_quarter_used','yoy_change_pp']]
assert all(bad_2019.prior_quarter_used.str.endswith(('23','24')))
bad_2019.to_csv(ROOT/'pr40_crossborder_wrong_years.csv',index=False)

# Sanity check the reference cohort engine exactly reconciles all supplied targets.
errors = []
for lead in d1.LEAD_TIME_MONTHS.values():
    weights = d1.lead_time_weights(lead)
    gross = d1.solve_reference_gross(weights)
    calc = d1.run_scenario(gross, {}, 0.0, weights, weights, 0.0)
    errors += [abs(calc[q]-v) for q,v in d1.TARGETS.items()]
assert max(errors) < 1e-10

payload = {
    'scope': 'PR40 head 0324cace7172db757280988888f64f0d27c877f7',
    'lower_bound_error': {'minimum_share_implied':min_share, 'rows':bound_rows},
    'cancellation_signal_counterexample': {
        'lost_nights':lost_nights, 'cancelled_adr':cancelled_adr,
        'starting_blended_adr':gbv0/n0, 'ending_blended_adr':gbv1/n1,
        'nights_growth_pct':night_growth, 'gbv_growth_pct':gbv_growth,
        'gbv_minus_nights_growth_pp':gbv_growth-night_growth},
    'quarter_parser': {'4Q19_bad_key':old_key('4Q19'), '1Q20_bad_key':old_key('1Q20'),
                       'wrong_comparisons':bad_2019.to_dict(orient='records')},
    'reference_engine_max_reconciliation_error_mm':max(errors)
}
(ROOT/'root_reproduction_results.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload,indent=2))
