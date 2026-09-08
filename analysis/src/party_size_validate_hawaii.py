"""Validate the review-text party-composition proxy against observed party size: Inside Airbnb's Hawaii market vs
DBEDT rental-house-only party size (annual, 2013-2024) and DBEDT all-visitor party size (monthly, 2013-2026).
Output: data/processed/party_size_validation_hawaii.csv + printed correlations.
"""
import glob
import pandas as pd, numpy as np
OUT = 'data/processed'
fs = [f for f in glob.glob(f'{OUT}/abnb_party_size_reviews_market_quarter*.csv')]
r = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True).drop_duplicates(['market', 'q'])
h = r[r.market.str.contains('united-states_hi_hawaii')].copy(); h['year'] = h.q.str[:4].astype(int)
if h.empty: raise SystemExit('no Hawaii market rows yet')
w = lambda g, c, n: (g[c] * g[n]).sum() / g[n].sum()
a = h.groupby('year').apply(lambda g: pd.Series({'reviews': g.reviews.sum(), 'mention_any': w(g, 'mention_any', 'reviews'),
    'cond_solo': w(g.assign(n=g.reviews * g.mention_any), 'cond_solo', 'n'), 'cond_couple': w(g.assign(n=g.reviews * g.mention_any), 'cond_couple', 'n'),
    'cond_family': w(g.assign(n=g.reviews * g.mention_any), 'cond_family', 'n'), 'cond_group': w(g.assign(n=g.reviews * g.mention_any), 'cond_group', 'n'),
    'headcount_mean': w(g, 'headcount_mean', 'headcount_n'), 'accommodates_mean': w(g, 'accommodates_mean', 'reviews')})).reset_index()
a['implied_party_size'] = a.cond_solo * 1 + a.cond_couple * 2 + a.cond_family * 3.9 + a.cond_group * 4.7
d = pd.read_csv(f'{OUT}/hawaii_party_size_annual.csv'); d = d[d.segment.eq('rental_house')][['year', 'avg_party_size', 'share_parties_3plus']].rename(columns={'avg_party_size': 'dbedt_rental_party_size', 'share_parties_3plus': 'dbedt_rental_3plus'})
v = a.merge(d, on='year', how='left')
v.to_csv(f'{OUT}/party_size_validation_hawaii.csv', index=False)
pd.set_option('display.width', 250); print(v.round(3).to_string())
s = v[v.dbedt_rental_party_size.notna() & ~v.year.isin([2020, 2021])]
for c in ['implied_party_size', 'cond_solo', 'cond_family', 'cond_group', 'headcount_mean', 'accommodates_mean']:
    print(f'corr({c}, DBEDT rental party size) = {s[[c, "dbedt_rental_party_size"]].corr().iloc[0, 1]:.2f}  (n={len(s)}, ex-2020/21)')
