"""Aggregate the v2 shard outputs: (1) composition by listing-capacity bucket over time and a mix-vs-within decomposition
of the rise in the family share / implied party size; (2) global monthly series and a seasonal index; (3) mention rate
and composition by review language. Outputs data/processed/abnb_party_size_reviews_v2_*.csv (global files)."""
import glob, pandas as pd, numpy as np
OUT = 'data/processed'; W = {'solo': 1, 'couple': 2, 'family': 3.9, 'group': 4.7}
def load(kind): return pd.concat([pd.read_csv(f) for f in glob.glob(f'{OUT}/abnb_party_size_reviews_v2_{kind}_shard*.csv')], ignore_index=True)
def wmean(g, cols, n):
    return pd.Series({c: (g[c] * g[n]).sum() / g[n].where(g[c].notna(), 0).sum() if g[n].where(g[c].notna(), 0).sum() else np.nan for c in cols})
def comp(g):
    n = g.reviews * g.mention_any; r = wmean(g.assign(n=n), ['cond_solo', 'cond_couple', 'cond_family', 'cond_group'], 'n')
    r['implied_party_size'] = sum(r[f'cond_{k}'] * v for k, v in W.items()); r['reviews'] = g.reviews.sum(); r['mentions'] = n.sum()
    r['headcount_mean'] = wmean(g, ['headcount_mean'], 'headcount_n').iloc[0]; return r

b = load('bucket_quarter'); b = b[b.q.str[:4].astype(int) >= 2011]; b['year'] = b.q.str[:4].astype(int)
b = b[b.bucket.isin(['1-2', '3-4', '5-6', '7+']) & b.room.isin(['entire', 'room'])]
# 1a composition by bucket x year (entire homes) and share of reviews by bucket
by = b.groupby(['year', 'room', 'bucket']).apply(comp, include_groups=False).reset_index()
tot = b.groupby('year').reviews.sum(); by['review_share'] = by.reviews / by.year.map(tot)
by.to_csv(f'{OUT}/abnb_party_size_reviews_v2_by_bucket_year.csv', index=False)
# 1b decomposition: implied party size = sum_b share_b * ips_b ; compare 2014-16 vs 2023-25
def stage(y0, y1):
    s = b[b.year.between(y0, y1)].groupby(['room', 'bucket']).apply(comp, include_groups=False).reset_index()
    s['w'] = s.mentions / s.mentions.sum(); return s.set_index(['room', 'bucket'])
s0, s1 = stage(2014, 2016), stage(2023, 2025); idx = s0.index.union(s1.index); s0, s1 = s0.reindex(idx), s1.reindex(idx)
ips0 = (s0.w * s0.implied_party_size).sum(); ips1 = (s1.w * s1.implied_party_size).sum()
mix = ((s1.w - s0.w) * s0.implied_party_size).sum(); within = (s1.w * (s1.implied_party_size - s0.implied_party_size)).sum()
dec = pd.DataFrame([dict(period0='2014-16', period1='2023-25', ips0=ips0, ips1=ips1, change=ips1 - ips0, mix_effect=mix, within_effect=within,
                         fam0=(s0.w * s0.cond_family).sum(), fam1=(s1.w * s1.cond_family).sum(),
                         fam_mix=((s1.w - s0.w) * s0.cond_family).sum(), fam_within=(s1.w * (s1.cond_family - s0.cond_family)).sum())])
dec.to_csv(f'{OUT}/abnb_party_size_reviews_v2_decomposition.csv', index=False)
print('=== decomposition (entire+room, weights = stated-composition reviews)'); print(dec.round(3).T.to_string())
print('=== mention-weight by bucket'); print(pd.DataFrame({'2014-16': s0.w, '2023-25': s1.w, 'ips_2014-16': s0.implied_party_size, 'ips_2023-25': s1.implied_party_size, 'fam_2014-16': s0.cond_family, 'fam_2023-25': s1.cond_family}).round(3).to_string())
# 2 monthly global + seasonal index
m = load('market_month'); m = m[m.m.str[:4].astype(int) >= 2013]
gm = m.groupby('m').apply(comp, include_groups=False).reset_index(); gm['year'] = gm.m.str[:4].astype(int); gm['month'] = gm.m.str[5:].astype(int)
gm.to_csv(f'{OUT}/abnb_party_size_reviews_v2_global_month.csv', index=False)
nrm = gm[~gm.year.isin([2020, 2021]) & gm.year.between(2014, 2025)]
si = (nrm.set_index('m')[['implied_party_size', 'cond_family', 'cond_group', 'cond_couple', 'cond_solo']].div(nrm.groupby('year')[['implied_party_size', 'cond_family', 'cond_group', 'cond_couple', 'cond_solo']].transform('mean').values)).assign(month=nrm.month.values).groupby('month').mean()
si.to_csv(f'{OUT}/abnb_party_size_reviews_v2_seasonal_index.csv'); print('=== seasonal index (month / annual mean)'); print(si.round(3).to_string())
# 3 language
l = load('language_year'); gl = l.groupby(['year', 'lang']).apply(comp, include_groups=False).reset_index()
gl['mention_rate'] = gl.mentions / gl.reviews; gl.to_csv(f'{OUT}/abnb_party_size_reviews_v2_by_language_year.csv', index=False)
print('=== 2024 by language'); print(gl[gl.year.eq(2024)].round(3).to_string())
print('=== english-only implied party size by year'); print(gl[gl.lang.eq('en')].set_index('year')[['implied_party_size', 'cond_family', 'cond_couple', 'mention_rate']].round(3).T.to_string())
