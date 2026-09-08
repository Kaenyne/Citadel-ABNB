"""Figure for research/notes/party_size_global_series.md"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
C = {'b': '#2a78d6', 'o': '#eb6834', 'a': '#1baf7a', 'text': '#0b0b0b', 'muted': '#52514e', 'grid': '#e6e5e1', 'surface': '#fcfcfb'}
q = pd.read_csv('data/processed/abnb_party_size_reviews_quarterly.csv')
g = q[q.region.eq('global') & q.weighting.eq('fixed_2019')].copy(); g['t'] = pd.PeriodIndex(g.q, freq='Q').to_timestamp()
g = g[(g.t >= '2012-01-01') & (g.q != '2026Q3')]
reg = q[q.weighting.eq('fixed_2019') & q.region.ne('global')].copy(); reg['t'] = pd.PeriodIndex(reg.q, freq='Q').to_timestamp(); reg = reg[(reg.t >= '2013-01-01') & (reg.q != '2026Q3')]
by = pd.read_csv('data/processed/abnb_party_size_reviews_v2_by_bucket_year.csv'); by = by[by.room.eq('entire') & by.year.between(2013, 2025)]
bench = pd.read_csv('data/processed/party_size_benchmarks.csv')
bk = pd.read_csv('data/processed/booking_515k_guest_type_monthly.csv'); bk = bk[bk.country.eq('ALL')]

fig, ax = plt.subplots(2, 2, figsize=(15, 9), facecolor=C['surface'])
for a in ax.flat:
    a.set_facecolor(C['surface']); a.grid(axis='y', color=C['grid'], lw=0.8); a.set_axisbelow(True)
    for s in ['top', 'right']: a.spines[s].set_visible(False)
    for s in ['left', 'bottom']: a.spines[s].set_color(C['grid'])
    a.tick_params(colors=C['muted'], labelsize=9)
# 1 global composition
a = ax[0, 0]
for c, col, lab in [('cond_couple', C['b'], 'couple'), ('cond_family', C['o'], 'family with kids'), ('cond_group', C['a'], 'friends / group'), ('cond_solo', C['muted'], 'solo')]:
    a.plot(g.t, g[c] * 100, color=col, lw=2, label=lab); a.text(g.t.iloc[-1] + pd.Timedelta(days=40), g[c].iloc[-1] * 100, lab, color=C['text'], fontsize=8.5, va='center')
a.set_title('Airbnb reviews stating who travelled: composition, global, fixed 2019 market weights (%)', fontsize=10, loc='left', color=C['text'])
a.set_xlim(pd.Timestamp('2012-01-01'), pd.Timestamp('2028-06-01'))
# 2 implied party size vs comparators
a = ax[0, 1]
a.plot(g.t, g.implied_party_size_conditional, color=C['o'], lw=2); a.text(g.t.iloc[-1] + pd.Timedelta(days=40), g.implied_party_size_conditional.iloc[-1], f'Airbnb reviews (implied) {g.implied_party_size_conditional.iloc[-1]:.2f}', color=C['text'], fontsize=8.5, va='center')
h = bench[bench.source.str.startswith('Hawaii DBEDT Annual') & bench.segment.eq('Rental house only (STR)')]; ht = pd.to_datetime(h.period.astype(str) + '-07-01')
a.plot(ht, h.party_size, color=C['a'], lw=2); a.text(ht.iloc[-1] + pd.Timedelta(days=40), h.party_size.iloc[-1], f'Hawaii rental house (DBEDT) {h.party_size.iloc[-1]:.2f}', color=C['text'], fontsize=8.5, va='center')
h2 = bench[bench.source.str.startswith('Hawaii DBEDT Annual') & bench.segment.eq('Hotel only')]; h2 = h2[h2.period.astype(int) >= 2012]; ht2 = pd.to_datetime(h2.period.astype(str) + '-07-01')
a.plot(ht2, h2.party_size, color=C['b'], lw=2); a.text(ht2.iloc[-1] + pd.Timedelta(days=40), h2.party_size.iloc[-1], f'Hawaii hotel (DBEDT) {h2.party_size.iloc[-1]:.2f}', color=C['text'], fontsize=8.5, va='center')
bt = pd.to_datetime(bk.month + '-15'); a.plot(bt, bk.implied_party_size, color=C['b'], lw=1.2, ls='--'); a.text(bt.iloc[-1] + pd.Timedelta(days=40), bk.implied_party_size.iloc[-1], 'Booking.com hotels EU (implied)', color=C['text'], fontsize=8.5, va='center')
a.set_title('People per party: Airbnb review proxy vs observed comparators', fontsize=10, loc='left', color=C['text']); a.set_xlim(pd.Timestamp('2012-01-01'), pd.Timestamp('2029-06-01'))
# 3 capacity mix + family share within bucket
a = ax[1, 0]
piv = by.pivot(index='year', columns='bucket', values='review_share'); piv = piv[['1-2', '3-4', '5-6', '7+']]
bottom = np.zeros(len(piv)); cols = ['#9ec5f4', '#5598e7', '#256abf', '#0d366b']
for i, b in enumerate(piv.columns):
    a.bar(piv.index, piv[b] * 100, bottom=bottom, color=cols[i], width=0.72, label=f'sleeps {b}'); bottom += piv[b].values * 100
a.legend(fontsize=8, frameon=False, loc='upper left', ncol=4); a.set_ylim(0, 100)
a.set_title('Share of all Airbnb reviews by capacity of the entire home reviewed, % (remainder = private/shared rooms)', fontsize=10, loc='left', color=C['text'])
# 4 regional implied party size
a = ax[1, 1]
for r, col in [('north_america', C['b']), ('emea', C['o']), ('apac', C['a']), ('latam', C['muted'])]:
    s = reg[reg.region.eq(r)]; s = s.set_index('t').implied_party_size_conditional.rolling(4).mean()
    a.plot(s.index, s.values, color=col, lw=2); a.text(s.index[-1] + pd.Timedelta(days=40), s.values[-1] + {'apac': 0.012, 'north_america': -0.004, 'emea': -0.018, 'latam': 0}[r], r.replace('_', ' '), color=C['text'], fontsize=8.5, va='center')
a.set_title('Implied party size by region, 4-quarter rolling', fontsize=10, loc='left', color=C['text']); a.set_xlim(pd.Timestamp('2013-01-01'), pd.Timestamp('2028-06-01'))
fig.text(0.005, 0.01, 'Sources: Inside Airbnb review text, 123 markets, 74m reviews (composition among the ~6-13% that state it; implied size = solo 1, couple 2, family 3.9, group 4.7); Hawaii DBEDT; Booking.com 515K Europe hotel reviews (tags). Built 8 Sep 2026.', fontsize=7.5, color=C['muted'])
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig('docs/figures/party_size_global_series.png', dpi=150, facecolor=C['surface']); print('saved')
