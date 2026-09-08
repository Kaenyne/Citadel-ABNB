"""Aggregate the market x quarter review-text party-size proxies into global and regional quarterly series.

Input: data/processed/abnb_party_size_reviews_market_quarter*.csv (shards from abnb_party_size_reviews.py)
Output: data/processed/abnb_party_size_reviews_quarterly.csv  (region x quarter, region in {global, north_america, emea, latam, apac})

Two weightings per series:
  * raw    - pooled over all reviews in the quarter (market mix moves with Inside Airbnb coverage and each city's growth)
  * fixed  - each market's contribution held at its 2019 share of reviews (mix-neutral index of within-market change)
"""
import glob, re
import pandas as pd, numpy as np

OUT = 'data/processed'
REGION = {'united-states': 'north_america', 'canada': 'north_america',
          'argentina': 'latam', 'brazil': 'latam', 'chile': 'latam', 'colombia': 'latam', 'mexico': 'latam', 'belize': 'latam',
          'australia': 'apac', 'new-zealand': 'apac', 'china': 'apac', 'japan': 'apac', 'singapore': 'apac', 'taiwan': 'apac', 'thailand': 'apac'}
SHARE_COLS = ['mention_any', 'share_solo', 'share_couple', 'share_family', 'share_group',
              'cond_solo', 'cond_couple', 'cond_family', 'cond_group', 'headcount_ge4', 'accommodates_ge5', 'entire_share']
MEAN_COLS = ['headcount_mean', 'accommodates_mean', 'review_len_mean']


def load():
    fs = [f for f in glob.glob(f'{OUT}/abnb_party_size_reviews_market_quarter*.csv') if 'shard' in f or f.endswith('market_quarter.csv')]
    df = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True).drop_duplicates(['market', 'q'])
    df['country'] = df.market.str.split('_').str[0]
    df['region'] = df.country.map(REGION).fillna('emea')
    df = df[df.q.str[:4].astype(int) >= 2011]
    return df


def weighted(df, w):
    """w = weights aligned with df rows. Shares weighted by w*reviews-in-denominator; means by w*n."""
    out = {}
    for c in SHARE_COLS:
        n = df.reviews if not c.startswith('cond_') else df.reviews * df.mention_any
        if c == 'headcount_ge4': n = df.headcount_n
        if c in ('accommodates_ge5',): n = df.reviews * df.accommodates_mean.notna()
        ww = (w * n).where(df[c].notna(), 0); out[c] = (ww * df[c].fillna(0)).sum() / ww.sum() if ww.sum() else np.nan
    for c in MEAN_COLS:
        n = df.headcount_n if c == 'headcount_mean' else df.reviews
        ww = (w * n).where(df[c].notna(), 0); out[c] = (ww * df[c].fillna(0)).sum() / ww.sum() if ww.sum() else np.nan
    out['reviews'] = df.reviews.sum(); out['headcount_n'] = df.headcount_n.sum(); out['markets'] = df.market.nunique()
    return pd.Series(out)


def build(df):
    ref = df[df.q.str.startswith('2019')].groupby('market').reviews.sum()
    df = df.assign(ref_share=df.market.map(ref / ref.sum()).fillna(0), q_share=df.reviews / df.groupby('q').reviews.transform('sum'))
    rows = []
    for region, sub in [('global', df)] + list(df.groupby('region')):
        for q, g in sub.groupby('q'):
            raw = weighted(g, pd.Series(1.0, index=g.index)); raw['weighting'] = 'raw'
            # fixed weights: market's 2019 share / its share of this quarter's reviews -> holds the market mix at 2019
            fw = (g.ref_share / g.q_share.replace(0, np.nan)).fillna(0)
            fx = weighted(g, fw); fx['weighting'] = 'fixed_2019'
            for r in (raw, fx): r['region'] = region; r['q'] = q; rows.append(r)
    res = pd.DataFrame(rows)
    # derived: implied mean party size among reviews that state composition (solo=1, couple=2, family=3.9, group=4.7 from headcount priors)
    res['implied_party_size_conditional'] = (res.cond_solo * 1 + res.cond_couple * 2 + res.cond_family * 3.9 + res.cond_group * 4.7) / res[['cond_solo', 'cond_couple', 'cond_family', 'cond_group']].sum(axis=1)
    cols = ['region', 'q', 'weighting', 'reviews', 'markets', 'mention_any', 'cond_solo', 'cond_couple', 'cond_family', 'cond_group',
            'implied_party_size_conditional', 'headcount_n', 'headcount_mean', 'headcount_ge4', 'accommodates_mean', 'accommodates_ge5', 'entire_share', 'review_len_mean',
            'share_solo', 'share_couple', 'share_family', 'share_group']
    return res[cols].sort_values(['region', 'weighting', 'q']).reset_index(drop=True)


if __name__ == '__main__':
    df = load(); res = build(df)
    res.to_csv(f'{OUT}/abnb_party_size_reviews_quarterly.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200)
    g = res[res.region.eq('global') & res.weighting.eq('fixed_2019')].copy(); g['year'] = g.q.str[:4]
    print(g.groupby('year')[['reviews', 'mention_any', 'cond_solo', 'cond_couple', 'cond_family', 'cond_group', 'implied_party_size_conditional', 'headcount_mean', 'headcount_ge4', 'accommodates_mean', 'accommodates_ge5', 'entire_share']]
          .agg({'reviews': 'sum', **{c: 'mean' for c in ['mention_any', 'cond_solo', 'cond_couple', 'cond_family', 'cond_group', 'implied_party_size_conditional', 'headcount_mean', 'headcount_ge4', 'accommodates_mean', 'accommodates_ge5', 'entire_share']}}).round(3).to_string())
