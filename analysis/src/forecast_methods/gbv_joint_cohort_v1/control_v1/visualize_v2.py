"""Plot reviewed model uncertainty and early-guide forecast errors from saved CSVs."""
from pathlib import Path
import argparse
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLORS = {'W1': '#177f94', 'W2': '#aa5e35'}
GROUPS = ['same_quarter', 'one_earlier', 'two_earlier', 'older_finite_tail']
LABELS = ['Booked in target quarter', 'Booked 1 quarter earlier', 'Booked 2 quarters earlier', 'Booked 3–4 quarters earlier*']


def clean(ax):
    ax.set_facecolor('white')
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    for side in ['bottom', 'left']:
        ax.spines[side].set_color('#cbd4dd')
    ax.set_axisbelow(True)
    ax.tick_params(colors='#42536a', labelsize=10)


def save(fig, out, name):
    for ext in ['png', 'svg']:
        fig.savefig(out / f'{name}.{ext}', dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--quarter', default='2025Q4')
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError('Use a new output directory')
    inputs = {name: a.results / f'{name}.csv' for name in ['nearfit_bounds', 'pit_predictions', 'pit_scores']}
    bounds = pd.read_csv(inputs['nearfit_bounds'])
    pred = pd.read_csv(inputs['pit_predictions'])
    scores = pd.read_csv(inputs['pit_scores'])
    chosen = bounds[bounds.quarter == a.quarter]
    if len(chosen) != 8:
        raise ValueError('Expected four cohort ranges in both windows')
    pred = pred[pred.spec == 'tail34'].sort_values('quarter')
    s = scores[(scores.spec == 'tail34') & (scores.target == 'guide') & (scores.model != 'oracle')]
    a.out.mkdir(parents=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': '#19304d'})
    fig, axes = plt.subplots(1, 2, figsize=(13.7, 6.5))
    fig.set_facecolor('#f5f7fa')
    fig.subplots_adjust(left=.20, right=.97, top=.72, bottom=.24, wspace=.50)
    fig.text(.045, .925, 'One dollar matrix, two questions — both uncertain', size=22, weight='bold')
    fig.text(.045, .85, f'{a.quarter}: ranges across similarly fitting models, not observed corporate booking cohorts', size=12)
    fig.text(.045, .80, 'W1 = 2023Q1–2026Q2 (14 quarters)     W2 = 2024Q1–2026Q2 (10 quarters)', size=10, color='#52637b')
    for window, offset in [('W1', -.12), ('W2', .12)]:
        rows = chosen[chosen.window == window].set_index('group').loc[GROUPS]
        for axis, low, high, count in [(axes[0], 'share_low_pct', 'share_high_pct', 4),
                                        (axes[1], 'effective_low_pct', 'effective_high_pct', 3)]:
            for i in range(count):
                r = rows.iloc[i]
                axis.plot([r[low], r[high]], [i+offset, i+offset], color=COLORS[window], lw=5,
                          solid_capstyle='round', label=window if i == 0 else None)
    for axis in axes:
        clean(axis)
        axis.invert_yaxis()
        axis.grid(axis='x', color='#e5e9ef')
    axes[0].set_yticks(range(4), LABELS)
    axes[0].set_xlim(-1, 101)
    axes[0].set_xlabel('Share of allocated target-quarter revenue (%)')
    axes[0].set_title('Where did the revenue come from?', size=12, loc='left', pad=16)
    axes[0].legend(frameon=False, ncol=2, loc='lower right')
    axes[1].set_yticks(range(3), ['Same quarter', '1 earlier', '2 earlier'])
    axes[1].set_xlim(left=0)
    axes[1].set_xlabel('Fee dollars attributed per $100 reported GBV')
    axes[1].set_title('How much did each booking dollar generate?', size=12, loc='left', pad=16)
    fig.text(.045, .145, 'Ranges retain shapes within 0.25 percentage points of the best historical relative RMSE; they are not confidence intervals.', size=10)
    fig.text(.045, .10, '*The primary model assumes lags 3–4 for the older tail. Separate lag-tail tests are in the audit.', size=10)
    fig.text(.045, .055, 'Reported GBV is net of period cancellations. Effective fee conversion is not a reservation survival or cancellation rate.', size=10, color='#52637b')
    save(fig, a.out, '01_joint_uncertainty')

    fig, axes = plt.subplots(1, 2, figsize=(13.7, 6.5), gridspec_kw={'width_ratios': [1.65, 1]})
    fig.set_facecolor('#f5f7fa')
    fig.subplots_adjust(left=.075, right=.97, top=.72, bottom=.34, wspace=.27)
    fig.text(.045, .925, 'Does the joint model improve the guide forecast?', size=22, weight='bold')
    fig.text(.045, .85, 'Forecasts made at the release before the one issuing the target guide; unprinted GBV is forecast.', size=12)
    fig.text(.045, .80, 'The fixed-lag benchmark uses the same origins and guidance cushion. Forecasts are reconstructed historical replays.', size=10, color='#52637b')
    ax = axes[0]
    clean(ax)
    x = np.arange(len(pred))
    for col, color, lab in [('guide_actual_musd', '#263b53', 'Issued guide midpoint'),
                            ('baseline_guide_musd', '#177f94', 'Fixed-lag benchmark'),
                            ('candidate_guide_musd', '#c17243', 'Joint-cohort candidate')]:
        ax.plot(x, pred[col]/1000, marker='o', markersize=4, linewidth=1.6, color=color, label=lab)
    ax.set_xticks(x, pred.quarter, rotation=45, ha='right')
    ax.set_ylabel('Quarterly guide midpoint (USD billions)')
    ax.grid(axis='y', color='#e5e9ef')
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    ax = axes[1]
    clean(ax)
    for i, window in enumerate(['W1', 'W2']):
        group = s[s.window == window].set_index('model')
        for model, offset, color in [('baseline', -.18, '#177f94'), ('candidate', .18, '#c17243')]:
            r = group.loc[model]
            ax.bar(i+offset, r.rmse_musd, width=.34, color=color)
            ax.text(i+offset, r.rmse_musd+3, f'${r.rmse_musd:.0f}m', ha='center', va='bottom', size=10)
    counts = s[s.model == 'candidate'].set_index('window').n
    ax.set_xticks([0, 1], [f'W1\nn={int(counts["W1"])}', f'W2\nn={int(counts["W2"])}'])
    ax.set_ylabel('Guide forecast RMSE (USD millions)')
    ax.set_ylim(0, s.rmse_musd.max()*1.23)
    ax.set_title('Lower error is better', size=12, loc='left', pad=16)
    ax.grid(axis='y', color='#e5e9ef')
    fig.text(.045, .195, 'Validation: the improvement reverses when 2024 is excluded. The candidate is not promoted.', size=11, weight='bold', color='#9b482e')
    fig.text(.045, .145, 'Promotion rule: candidate RMSE at most 90% of benchmark in both windows, n≥8 in each, and no deletion reversals.', size=10)
    fig.text(.045, .10, 'Warm-up abstentions are retained separately. Overlapping windows and few years limit statistical precision.', size=10)
    fig.text(.045, .055, 'No fitted booking split is presented as an observed fact; no earnings-return or price-target claim follows from this test.', size=10, color='#52637b')
    save(fig, a.out, '02_guide_forecast_test')
    manifest = {name: {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for name, path in inputs.items()}
    (a.out / 'sources.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Figures saved in {a.out}')


if __name__ == '__main__':
    main()
