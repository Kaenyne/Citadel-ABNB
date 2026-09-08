"""Second pass over the Inside Airbnb review corpus: the same party-composition flags as abnb_party_size_reviews.py,
aggregated (a) by market x quarter x listing-capacity bucket x room type (mix-vs-within decomposition),
(b) by market x month (seasonality), (c) by review language (mention-rate bias check).

Usage: py -3.13 analysis/src/abnb_party_size_reviews_v2.py [--shard i n] [market substrings...]
Outputs (data/processed/):
  abnb_party_size_reviews_v2_bucket_quarter[_shardi].csv
  abnb_party_size_reviews_v2_market_month[_shardi].csv
  abnb_party_size_reviews_v2_language_year[_shardi].csv
"""
import re, glob, os, sys
import pandas as pd, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from abnb_party_size_reviews import RAW, OUT, RX, headcount

LANG = {  # crude stopword signatures; first match wins, English default
    'es': re.compile(r'\b(muy|el|la|los|las|estuvo|fue|para|con|nos|una|pero)\b', re.I),
    'fr': re.compile(r'\b(très|nous|était|est|avec|pour|dans|une|les|bien|appartement)\b', re.I),
    'it': re.compile(r'\b(molto|era|con|per|una|nella|della|siamo|casa|appartamento)\b', re.I),
    'de': re.compile(r'\b(sehr|und|wir|war|ist|nicht|mit|die|das|wohnung|gerne)\b', re.I),
    'pt': re.compile(r'\b(muito|não|uma|com|para|foi|ótimo|tudo|apartamento|nós)\b', re.I),
    'zh_ja_ko': re.compile(r'[぀-ヿ一-鿿가-힯]'),
}
EN = re.compile(r'\b(the|and|was|very|great|stay|place|we|our|host)\b', re.I)


def lang_of(t):
    if EN.search(t):
        en = len(EN.findall(t))
        for k, rx in LANG.items():
            if k != 'zh_ja_ko' and len(rx.findall(t)) > en: return k
        return 'en'
    for k, rx in LANG.items():
        if rx.search(t): return k
    return 'other'


def bucket(a):
    return pd.cut(a, [0, 2, 4, 6, 99], labels=['1-2', '3-4', '5-6', '7+'])


def process(rev_path, lst_path, market):
    acc = None
    if lst_path and os.path.exists(lst_path):
        L = pd.read_csv(lst_path, usecols=lambda c: c in ('id', 'accommodates', 'room_type', 'bedrooms'), low_memory=False)
        acc = L.drop_duplicates('id').set_index('id')
    parts = []
    for chunk in pd.read_csv(rev_path, usecols=['listing_id', 'date', 'comments'], chunksize=200_000, dtype={'comments': str}):
        c = chunk.comments.fillna('').astype(str)
        dt = pd.to_datetime(chunk.date, errors='coerce')
        d = pd.DataFrame({'listing_id': chunk.listing_id.values, 'q': dt.dt.to_period('Q').astype(str).values, 'm': dt.dt.to_period('M').astype(str).values})
        for k, rx in RX.items(): d[k] = c.str.contains(rx).values
        d['headcount'] = c.map(headcount).values
        d['lang'] = c.map(lang_of).values
        if acc is not None:
            j = acc.reindex(d.listing_id)
            d['bucket'] = bucket(pd.Series(j.accommodates.values)).astype(str).values
            d['room'] = np.where(j.room_type.values == 'Entire home/apt', 'entire', np.where(pd.isna(j.room_type.values), 'unknown', 'room'))
        else:
            d['bucket'] = 'nan'; d['room'] = 'unknown'
        parts.append(d)
    d = pd.concat(parts, ignore_index=True); d['any'] = d[list(RX)].any(axis=1)

    def agg(g):
        o = {'reviews': g.size(), 'mention_any': g['any'].mean(), 'headcount_n': g.headcount.count(), 'headcount_mean': g.headcount.mean()}
        for k in RX: o[f'share_{k}'] = g[k].mean()
        return pd.DataFrame(o)

    def cond(g):  # composition among reviews that state it
        return pd.DataFrame({f'cond_{k}': g[k].mean() for k in RX})

    b = agg(d.groupby(['q', 'bucket', 'room'])).join(cond(d[d['any']].groupby(['q', 'bucket', 'room']))).reset_index()
    m = agg(d.groupby('m')).join(cond(d[d['any']].groupby('m'))).reset_index()
    d['year'] = d.q.str[:4]
    l = agg(d.groupby(['year', 'lang'])).join(cond(d[d['any']].groupby(['year', 'lang']))).reset_index()
    for x in (b, m, l): x.insert(0, 'market', market)
    return b, m, l


if __name__ == '__main__':
    import warnings; warnings.filterwarnings('ignore', message='This pattern is interpreted')
    args = sys.argv[1:]; shard = None
    if args[:1] == ['--shard']: shard = (int(args[1]), int(args[2])); args = args[3:]
    only = args; tag = ('_' + '_'.join(only) if only else '') + (f'_shard{shard[0]}' if shard else '')
    B, M, Lg = [], [], []
    for idx, rp in enumerate(sorted(glob.glob(f'{RAW}/*_reviews.csv.gz'))):
        market = os.path.basename(rp).replace('_reviews.csv.gz', '')
        if only and not any(o in market for o in only): continue
        if shard and idx % shard[1] != shard[0]: continue
        print(market, flush=True)
        try:
            b, m, l = process(rp, rp.replace('_reviews.csv.gz', '_listings.csv.gz'), market); B.append(b); M.append(m); Lg.append(l)
        except Exception as e: print('  ERR', e, flush=True)
    pd.concat(B, ignore_index=True).to_csv(f'{OUT}/abnb_party_size_reviews_v2_bucket_quarter{tag}.csv', index=False)
    pd.concat(M, ignore_index=True).to_csv(f'{OUT}/abnb_party_size_reviews_v2_market_month{tag}.csv', index=False)
    pd.concat(Lg, ignore_index=True).to_csv(f'{OUT}/abnb_party_size_reviews_v2_language_year{tag}.csv', index=False)
    print('done', tag)
