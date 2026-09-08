"""Figure for research/notes/hawaii_party_size_series.md from the DBEDT party-size outputs."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt

C = {'hotel': '#2a78d6', 'rental_house': '#eb6834', 'condo': '#1baf7a', 'text': '#0b0b0b', 'muted': '#52514e', 'grid': '#e6e5e1', 'surface': '#fcfcfb'}
an = pd.read_csv('data/processed/hawaii_party_size_annual.csv')
ms = pd.read_csv('data/processed/hawaii_party_size_monthly.csv'); ms = ms[ms.flight.eq('total')].copy()
ms['date'] = pd.to_datetime(ms.ym); ms['year'] = ms.date.dt.year; ms['month'] = ms.date.dt.month

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6), facecolor=C['surface'])
for a in ax:
    a.set_facecolor(C['surface']); a.grid(axis='y', color=C['grid'], lw=0.8); a.set_axisbelow(True)
    for s in ['top', 'right']: a.spines[s].set_visible(False)
    for s in ['left', 'bottom']: a.spines[s].set_color(C['grid'])
    a.tick_params(colors=C['muted'], labelsize=9)

# 1 annual party size by accommodation
w = an.pivot(index='year', columns='segment', values='avg_party_size')
for seg, lab in [('hotel', 'Hotel only'), ('condo', 'Condo only'), ('rental_house', 'Rental house only')]:
    s = w[seg].dropna(); ax[0].plot(s.index, s.values, color=C[seg], lw=2, label=lab)
    ax[0].text(s.index[-1] + 0.4, s.values[-1], f'{lab} {s.values[-1]:.2f}', color=C['text'], fontsize=8.5, va='center')
ax[0].set_xlim(1999, 2031); ax[0].set_title('Hawaii air visitors: people per travel party, by accommodation', fontsize=10, color=C['text'], loc='left')
ax[0].set_ylabel('avg party size', color=C['muted'], fontsize=9)

# 2 monthly total party size
full = ms.set_index('date').party_size.reindex(pd.date_range(ms.date.min(), ms.date.max(), freq='MS'))  # leave gaps for missing months
ax[1].plot(full.index, full.values, color=C['hotel'], lw=1.6)
yr = ms[~ms.year.isin([2020, 2021])].groupby('year').party_size.mean()
ax[1].set_title('All air visitors, monthly (DBEDT Visitor Highlights)', fontsize=10, color=C['text'], loc='left')
ax[1].set_ylabel('avg party size', color=C['muted'], fontsize=9)
ax[1].annotate('COVID', xy=(pd.Timestamp('2020-05-01'), 1.25), color=C['muted'], fontsize=8.5)

# 3 seasonal index
norm = ms[~ms.year.isin([2020, 2021]) & (ms.year <= 2025)]
idx = (norm.party_size / norm.groupby('year').party_size.transform('mean')).groupby(norm.month).mean()
bars = ax[2].bar(idx.index, (idx - 1) * 100, color=C['hotel'], width=0.7)
ax[2].axhline(0, color=C['grid'], lw=1)
ax[2].set_xticks(range(1, 13)); ax[2].set_xticklabels(list('JFMAMJJASOND'))
ax[2].set_title('Seasonal index, % vs annual mean (2013-19, 2022-25)', fontsize=10, color=C['text'], loc='left')
for m, v in idx.items():
    ax[2].text(m, (v - 1) * 100 + (0.6 if v >= 1 else -0.6), f'{(v-1)*100:+.0f}', ha='center', va='bottom' if v >= 1 else 'top', fontsize=8, color=C['text'])
ax[2].set_ylim(-9, 14)
fig.text(0.005, 0.01, 'Source: Hawaii DBEDT Annual Visitor Research Reports (tables by accommodation, 2000-2024) and monthly Visitor Highlights (2013-2026, Wayback for 2013-2024). Party = self-reported immediate travel party of air visitors.', fontsize=7.5, color=C['muted'])
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig('docs/figures/hawaii_party_size_series.png', dpi=160, facecolor=C['surface'])
print('saved')
