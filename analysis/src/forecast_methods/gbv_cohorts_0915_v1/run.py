"""Descriptive figures only. Read frozen inputs; write to a new output directory."""
from pathlib import Path
import argparse
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
SOURCES = {
    'kpi': ROOT / 'data/processed/overnight/02_kpi_panel_quarterly.csv',
    'lambda_history': ROOT / 'data/processed/forecast_methods/gbv_event_v1/integration_v2/lambda_history.csv',
    'k2_prior': ROOT / 'data/processed/forecast_methods/kernel_leadtime_v2/K2_recommended_prior.csv',
}
COLORS = ['#167d9a', '#4456a6', '#dba347', '#abb3bf']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(ax):
    ax.set_facecolor('#ffffff')
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    for side in ['bottom', 'left']:
        ax.spines[side].set_color('#cad2db')
    ax.tick_params(colors='#425166', labelsize=10)
    ax.set_axisbelow(True)


def save(fig, out, stem):
    fig.savefig(out / f'{stem}.png', dpi=160, facecolor=fig.get_facecolor())
    fig.savefig(out / f'{stem}.svg', facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'outputs/gbv-cohorts-20260915-v1')
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(f'Choose a NEW output directory: {out}')
    before = {key: digest(path) for key, path in SOURCES.items()}
    kpi = pd.read_csv(SOURCES['kpi'])
    kpi['q'] = kpi.quarter.map(lambda x: f'20{x[2:]}Q{x[0]}')
    if kpi.q.duplicated().any():
        raise ValueError('Duplicate KPI quarters')
    lookup = kpi.set_index('q').gbv_musd
    hist = pd.read_csv(SOURCES['lambda_history'])
    rows = hist.loc[hist.quarter.between('2023Q1', '2026Q2')].copy()
    if len(rows) != 14 or rows.quarter.duplicated().any():
        raise ValueError('Expected 14 distinct W1 quarters')
    for r in rows.itertuples():
        q = pd.Period(r.quarter, freq='Q')
        g1, g2 = lookup[str(q - 1)], lookup[str(q - 2)]
        revenue = float(kpi.set_index('q').loc[r.quarter, 'revenue_musd'])
        base = 2 / 3 * g1 + 1 / 3 * g2
        if not np.allclose([r.gbv_l1, r.gbv_l2, r.revenue_musd, r.base_musd, r.lambda_pct],
                           [g1, g2, revenue, base, 100 * revenue / base], rtol=0, atol=1e-8):
            raise ValueError(f'Frozen inputs disagree: {r.quarter}')
    rows['year'] = rows.quarter.str[:4].astype(int)
    summaries = []
    for window, start in [('W1', '2023Q1'), ('W2', '2024Q1')]:
        for season, group in rows.loc[rows.quarter >= start].groupby('season'):
            x = group.lambda_pct
            summaries.append(dict(window=window, season=int(season), n=len(x),
                                  mean_pct=x.mean(), sd_pp=x.std(ddof=1),
                                  variance_pp2=x.var(ddof=1), min_pct=x.min(), max_pct=x.max(),
                                  range_pp=x.max()-x.min(), basis='retrospective descriptive; not forecast error'))
    stats = pd.DataFrame(summaries)
    prior = pd.read_csv(SOURCES['k2_prior'])
    prior = prior.loc[prior.weighting == 'value'].copy()
    order = {'1-2-3': 0, '4-5-6': 1, '7-8-9': 2, '10-11-12': 3}
    prior['month_order'] = prior.melbourne_months.map(order)
    prior = prior.sort_values('month_order')
    values = prior[[f'phi{k}' for k in range(4)]].to_numpy() * 100
    if len(prior) != 4 or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError('Invalid K2 proxy shares')
    if not np.allclose(values.sum(axis=1), 100, atol=1e-8):
        raise ValueError('Cohorts do not sum to 100% including 3+ tail')
    if prior.n_reservations.sum() != 268110:
        raise ValueError('K2 sample count mismatch')

    out.mkdir(parents=True)
    rows.to_csv(out / 'aggregate_conversion_history.csv', index=False)
    stats.to_csv(out / 'aggregate_conversion_variance.csv', index=False)
    prior['basis'] = 'K2 reconstructed accommodation-value proxy; not ABNB fee revenue'
    prior.to_csv(out / 'melbourne_proxy_cohorts.csv', index=False)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': '#172b45'})

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw={'width_ratios': [1.35, 1]})
    fig.set_facecolor('#f5f7fa')
    fig.subplots_adjust(left=.07, right=.97, top=.72, bottom=.22, wspace=.27)
    fig.text(.055, .925, 'What we can calculate: aggregate conversion', fontsize=21, weight='bold')
    fig.text(.055, .855, 'Quarter revenue / [(2/3 × prior-quarter GBV) + (1/3 × GBV two quarters earlier)]', fontsize=12)
    fig.text(.055, .805, 'Historical ratio from frozen model inputs. It does not identify booking cohorts or cancellation rates.', fontsize=11, color='#526279')
    ax = axes[0]
    clean(ax)
    for season, g in rows.groupby('season'):
        ax.plot(g.year, g.lambda_pct, marker='o', linewidth=2, markersize=7,
                color=COLORS[int(season)-1], label=f'Q{season}')
    ax.set_xticks([2023, 2024, 2025, 2026])
    ax.set_xlim(2022.88, 2026.13)
    ax.set_ylim(11.5, 18.0)
    ax.set_ylabel('Aggregate conversion ratio (%)')
    ax.grid(axis='y', color='#e4e9ef')
    ax.legend(ncol=4, frameon=False, loc='upper left', fontsize=9)
    ax.set_title('Compare each quarter with the same season', fontsize=12, loc='left', pad=14)
    ax = axes[1]
    clean(ax)
    s = stats.loc[stats.window == 'W1']
    bars = ax.barh(np.arange(4), s.sd_pp, color=COLORS, height=.55)
    ax.set_yticks(np.arange(4), [f'Q{int(r.season)}  (n={int(r.n)})' for r in s.itertuples()])
    ax.invert_yaxis()
    ax.set_xlim(0, max(.48, s.sd_pp.max()*1.45))
    for bar, r in zip(bars, s.itertuples()):
        ax.text(r.sd_pp+.012, bar.get_y()+bar.get_height()/2, f'{r.sd_pp:.3f} pp', va='center', fontsize=10)
    ax.set_xlabel('Within-season sample standard deviation (pp)')
    ax.set_title('How much the historical ratio varied', fontsize=12, loc='left', pad=14)
    ax.grid(axis='x', color='#e4e9ef')
    fig.text(.055, .11, '2023Q1–2026Q2: 14 observations. Each season has only 3–4 observations; 2026 Q3/Q4 are absent.', fontsize=10)
    fig.text(.055, .065, 'SD describes this sample, not a forecast interval. CSV includes variance (pp²), range and the shorter W2 window.', fontsize=10, color='#526279')
    save(fig, out, '01_aggregate_conversion')

    fig, ax = plt.subplots(figsize=(13, 6.5))
    fig.set_facecolor('#f5f7fa')
    fig.subplots_adjust(left=.18, right=.97, top=.68, bottom=.27)
    clean(ax)
    fig.text(.055, .925, 'Booking-quarter split: an old proxy, not company revenue', fontsize=20, weight='bold')
    fig.text(.055, .862, 'Melbourne accommodation-value shares reconstructed by the existing K2 study | March 2016–February 2017', fontsize=11)
    fig.text(.055, .805, 'No corporate dollar allocation. No evidence here of the current global split or its year-to-year variance.', fontsize=11, color='#526279')
    labels = ['Booked in same quarter', 'Booked 1 quarter earlier', 'Booked 2 quarters earlier', 'Booked 3+ quarters earlier']
    left = np.zeros(4)
    for k in range(4):
        ax.barh(np.arange(4), values[:, k], left=left, height=.56, color=COLORS[k], label=labels[k])
        for i, v in enumerate(values[:, k]):
            ax.text(left[i]+v/2, i, f'{v:.1f}%', ha='center', va='center', fontsize=10,
                    color='white' if k < 2 else '#172b45', weight='bold')
        left += values[:, k]
    ax.set_yticks(np.arange(4), [f'{label}\nn = {int(n):,}' for label, n in zip(
        ['Jan–Mar months*', 'Apr–Jun 2016', 'Jul–Sep 2016', 'Oct–Dec 2016'], prior.n_reservations)])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(PercentFormatter(100))
    ax.set_xlabel('Share of estimated accommodation value, grouped by check-in month')
    ax.legend(ncol=2, frameon=False, loc='upper center', bbox_to_anchor=(.43, 1.28), fontsize=10)
    fig.text(.055, .175, '*Jan–Mar combines March 2016 with January–February 2017. Southern-hemisphere month labels are retained.', fontsize=10)
    fig.text(.055, .125, '268,110 reservations. Value uses cleaned nightly price × nights; currency/units were not independently verified.', fontsize=10)
    fig.text(.055, .075, 'Tail and truncation assumptions affect the estimates. Source raw files are absent locally; this plots saved K2 outputs.', fontsize=10, color='#526279')
    fig.text(.055, .032, 'The earlier truncation test did not recover the reference mean. These shares are exploratory inputs, not validated cohort measurements.', fontsize=9, color='#526279')
    save(fig, out, '02_melbourne_cohort_proxy')

    after = {key: digest(path) for key, path in SOURCES.items()}
    if before != after:
        raise RuntimeError('An input changed during chart generation')
    manifest = {'as_of': '2026-09-15', 'purpose': 'descriptive cohort feasibility; no fitted model or forecasts',
                'source_sha256': before, 'input_files': {key: str(p.relative_to(ROOT)) for key, p in SOURCES.items()},
                'checks': ['14 W1 quarters', '10 W2 quarters', 'all 14 ratios reconcile to source KPIs',
                           '4 proxy cohorts including tail sum to 100%', '268110 source reservations', 'input hashes unchanged'],
                'outputs': {p.name: digest(p) for p in sorted(out.iterdir())}}
    assert len(rows.loc[rows.quarter >= '2024Q1']) == 10
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(stats.round(6).to_string(index=False))
    print(f'Written: {out}')


if __name__ == '__main__':
    main()
