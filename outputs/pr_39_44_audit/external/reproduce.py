"""Read-only reproductions against PR40/41 source and committed input CSVs.

Run with Python, pandas, numpy and scipy. All generated files stay beside this script.
"""
from pathlib import Path
import importlib.util
import json
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'source'))


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / 'source' / f'{name}.py')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


g2 = module('G2_external_backtests')
g2.RAW = str(HERE / 'data')
original = g2.ntto_features()
panel = pd.read_csv(HERE / 'data/G_quarterly_panel.csv', index_col=0)
panel.index = pd.PeriodIndex(panel.index, freq='Q')
pd.testing.assert_frame_equal(original.reindex(panel.index), panel[original.columns],
                              check_names=False, check_exact=False, atol=1e-10, rtol=1e-10)

raw = pd.read_csv(HERE / 'data/ntto_arrivals_monthly.csv')
corrected = pd.DataFrame(index=panel.index)
for region, tag in [('OVERSEAS', 'ntto_overseas'), ('WESTERN EUROPE', 'ntto_weurope'),
                    ('TOTAL ALL COUNTRIES', 'ntto_total')]:
    s = raw[raw.region == region].copy()
    s.index = pd.PeriodIndex(s.month, freq='M')
    s = s.arrivals.sort_index()
    s = s[~s.index.duplicated()]
    q = s.groupby(s.index.asfreq('Q')).sum()
    nq = s.groupby(s.index.asfreq('Q')).size()
    q = q.where(nq == 3)
    m1 = s[(s.index.month - 1) % 3 == 0]
    m1.index = m1.index.asfreq('Q')
    for suffix, levels in [('full', q), ('qtd1m', m1)]:
        # The only correction: make shift(4) mean four calendar quarters.
        levels = levels.reindex(pd.period_range(levels.index.min(), levels.index.max(), freq='Q'))
        corrected[tag + '_' + suffix] = g2.yoy(levels).reindex(panel.index)

rows = []
for column in corrected:
    for quarter in panel.loc['2022Q1':'2026Q3'].index:
        old, new = panel.at[quarter, column], corrected.at[quarter, column]
        if not (pd.isna(old) and pd.isna(new)) and not np.isclose(old, new, equal_nan=True):
            rows.append({'feature': column, 'quarter': str(quarter), 'original_yoy_pct': old,
                         'corrected_yoy_pct': new})
pd.DataFrame(rows).to_csv(HERE / 'ntto_wrong_year_comparisons.csv', index=False)

fixed = panel.copy()
fixed[corrected.columns] = corrected
results = []
target = 'nights_m_yoy_pct'
for start, wfstart in g2.WINDOWS:
    for feature in corrected:
        for label, data in [('original', panel), ('calendar_aligned', fixed)]:
            result = g2.test_pair(data, feature, target, start, wfstart)
            tr = data.loc[start:g2.WIN1, [feature, target]].dropna()
            coef = g2.ols_fit(tr[feature].values, tr[target].values)
            result['prediction_2026Q3'] = coef[0] + coef[1] * data.at[g2.NOWQ, feature]
            result['version'] = label
            results.append(result)
results = pd.DataFrame(results)
results.to_csv(HERE / 'ntto_backtest_comparison.csv', index=False)

original_live = pd.read_csv(HERE / 'data/G_nowcast_3q26_observable.csv')
original_live = original_live[original_live.target == target]
other = original_live[~original_live.feature.str.startswith('ntto')].pred_3q26
ntto_live = results[(results.version == 'calendar_aligned') & (results.wf_n >= 6)
                    & (results.wf_ratio_vs_naive < 1) & results.prediction_2026Q3.notna()]
new_live = pd.concat([other, ntto_live.prediction_2026Q3])
feature = 'ntto_overseas_qtd1m'
old_wf = g2.walk_forward(panel.loc['2023Q1':'2026Q2'], feature, target, pd.Period('2024Q1'))
new_wf = g2.walk_forward(fixed.loc['2023Q1':'2026Q2'], feature, target, pd.Period('2024Q1'))
old_wf = old_wf[old_wf.q.isin(new_wf.q)]
common_quarters = {'quarters': old_wf.q.astype(str).tolist(),
                   'original_ratio': g2.rmse(old_wf.pred, old_wf.actual) / g2.rmse(old_wf.naive, old_wf.actual),
                   'corrected_ratio': g2.rmse(new_wf.pred, new_wf.actual) / g2.rmse(new_wf.naive, new_wf.actual)}

g3 = module('G3_rank_sources')
coverage = [{'coverage_end': end, 'frequency': freq,
             'actual_score': g3.coverage_score(end, freq), 'expected_from_docstring': expect}
            for end, freq, expect in [('2026-07', 'monthly', 1),
                                       ('2026-07-31', 'monthly', 1),
                                       ('2026Q2 (released 9 Sep 2026)', 'quarterly', 0)]]
provenance = pd.read_csv(HERE / 'data/F1_provenance.csv')
calendar = []
for market, group in provenance.groupby('market'):
    dates = sorted(group.snapshot)
    calendar.append({'market': market, 'n_vintages_in_PR41': len(dates),
                     'first_four_pairs_if_A1_rerun': list(zip(dates[:4], dates[1:5]))})

a1 = module('A1_calendar_reopening_all_markets')
a1.self_test()
f1 = module('F1_calendar_pace')
f1.self_test()

summary = {'original_ensemble_nights_n': len(original_live),
           'original_ensemble_nights_median': original_live.pred_3q26.median(),
           'calendar_aligned_ensemble_nights_n': len(new_live),
           'calendar_aligned_ensemble_nights_median': new_live.median(),
           'overseas_qtd_identical_evaluation_quarters': common_quarters,
           'coverage_score_reproduction': coverage,
           'calendar_vintages': calendar}
(HERE / 'reproduction_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(results[['feature', 'window', 'version', 'n', 'wf_n', 'wf_ratio_vs_naive',
               'prediction_2026Q3']].to_string(index=False))
print(json.dumps({k: v for k, v in summary.items() if k != 'calendar_vintages'}, indent=2))
