"""Airbnb party-size proxies from Inside Airbnb review text, all markets, quarterly.

Inputs (gitignored): data/raw/inside_airbnb_reviews/<market>_<snapshot>_reviews.csv.gz and _listings.csv.gz
(one current snapshot per market carries every review since 2009). Manifest: reviews_manifest.csv.

Per review: (1) party composition flagged from the text in en/es/fr/it/de/pt (solo, couple, family-with-kids,
friends/group); (2) an explicit head-count where the text states one ("group of 6", "the four of us",
"eramos 5"); (3) the reviewed listing's `accommodates` (booked-capacity proxy).
Output: market x quarter aggregates -> data/processed/abnb_party_size_reviews_market_quarter.csv
"""
import re, glob, os, sys
import pandas as pd, numpy as np

RAW = 'data/raw/inside_airbnb_reviews'; OUT = 'data/processed'
NUM = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,
       'dos':2,'tres':3,'cuatro':4,'cinco':5,'seis':6,'siete':7,'ocho':8,'nueve':9,'diez':10,
       'deux':2,'trois':3,'quatre':4,'cinq':5,'sept':7,'huit':8,'neuf':9,'dix':10,
       'due':2,'tre':3,'quattro':4,'cinque':5,'sei':6,'sette':7,'otto':8,'nove':9,'dieci':10,
       'zwei':2,'drei':3,'vier':4,'fünf':5,'sechs':6,'sieben':7,'acht':8,'neun':9,'zehn':10,
       'zweit':2,'dritt':3,'viert':4,'fünft':5,'sechst':6,'siebt':7,
       'duas':2,'três':3,'quatro':4,'sete':7,'oito':8,'dez':10}
W = (r'(\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez'
     r'|deux|trois|quatre|cinq|sept|huit|neuf|dix|due|tre|quattro|cinque|sei|sette|otto|nove|dieci'
     r'|zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|duas|três|sete|oito|dez)')
PAT = {
 'solo': (r"\b(solo trip|solo travel\w*|travel(l)?ing (alone|solo)|by myself|on my own|just me|as a solo"
          r"|viaj(é|e|aba) sol[oa]|en solo|da sol[oa]|alleine|allein gereist|sozinh[oa])\b"),
 'couple': (r"\b(my (wife|husband|partner|boyfriend|girlfriend|fianc[eé]e?|spouse)|(wife|husband|partner|boyfriend|girlfriend|spouse) and (i|me)"
            r"|as a couple|the two of us|both of us|for (a )?couple|mi (esposa|esposo|marido|mujer|novia|novio|pareja)|en pareja"
            r"|ma (femme|copine|compagne)|mon (mari|copain|compagnon)|en couple|mia moglie|mio marito|la mia ragazza|il mio ragazzo|in coppia"
            r"|meine (frau|freundin)|mein (mann|freund)|als paar|zu zweit|minha (esposa|namorada)|meu (marido|namorado)|em casal)\b"),
 'family': (r"\b(my family|our family|family of \w+|family trip|our (kids|children|toddler|baby|son|daughter|teen\w*|little ones)"
            r"|with (the|our|my) (kids|children|toddler|baby)|my (mom|dad|mother|father|parents|sister|brother|in-laws)|multigenerational"
            r"|mi familia|nuestra familia|en familia|con (los |mis |nuestros )?(niños|hijos|hijas)"
            r"|ma famille|notre famille|en famille|avec (nos|mes|les) enfants|la mia famiglia|in famiglia|con i (nostri |miei )?(bambini|figli)"
            r"|meine familie|unsere familie|mit (unseren |meinen |den )?kindern|als familie|minha família|nossa família|em família|com (as |os )?crianças)\b"),
 'group': (r"\b(group of \w+|\w+ of us|our group|my friends and i|with (my |our |some )?friends|(friends|colleagues|mates|buddies) and (i|me)"
           r"|bachelor(ette)? party|hen (do|party)|stag (do|party)|our crew|the (whole|entire) gang"
           r"|grupo de \w+|con (mis |unos )?amig[oa]s|entre amig[oa]s|éramos \w+|groupe de \w+|entre amis|avec (des |mes |nos )?amis|nous étions \w+"
           r"|gruppo di \w+|con (i miei |gli )?amici|tra amici|eravamo in \w+|gruppe von \w+|mit (meinen |unseren )?freunden|unter freunden|wir waren zu \w+"
           r"|com (os |meus |uns )?amigos)\b"),
}
CNT = [r"\b(?:group|family|party) of " + W + r"\b", r"\b" + W + r" of us\b", r"\b(?:grupo|familia|família) de " + W + r"\b",
       r"\béramos " + W + r"\b", r"\b(?:groupe|famille) de " + W + r"\b", r"\bnous étions " + W + r"\b",
       r"\b(?:gruppo|famiglia) di " + W + r"\b", r"\beravamo in " + W + r"\b", r"\bgruppe von " + W + r"\b",
       r"\bwir waren zu " + W + r"\b", r"\bzu (zweit|dritt|viert|fünft|sechst|siebt)\b"]
RX = {k: re.compile(p, re.I) for k, p in PAT.items()}; RXC = [re.compile(p, re.I) for p in CNT]


def headcount(t):
    for rx in RXC:
        m = rx.search(t)
        if m:
            g = m.group(1).lower(); n = NUM.get(g) or (int(g) if g.isdigit() else None)
            if n and 1 < n <= 30: return n
    return np.nan


def process(rev_path, lst_path, market):
    acc = None
    if lst_path and os.path.exists(lst_path):
        L = pd.read_csv(lst_path, usecols=lambda c: c in ('id', 'accommodates', 'room_type', 'bedrooms'), low_memory=False)
        acc = L.drop_duplicates('id').set_index('id')
    parts = []
    for chunk in pd.read_csv(rev_path, usecols=['listing_id', 'date', 'comments'], chunksize=200_000, dtype={'comments': str}):
        c = chunk.comments.fillna('').astype(str)
        d = pd.DataFrame({'listing_id': chunk.listing_id.values,
                          'q': pd.to_datetime(chunk.date, errors='coerce').dt.to_period('Q').astype(str)})
        for k, rx in RX.items(): d[k] = c.str.contains(rx).values
        d['headcount'] = c.map(headcount).values
        d['len'] = c.str.len().values
        if acc is not None:
            j = acc.reindex(d.listing_id)
            d['accommodates'] = j.accommodates.values; d['entire'] = (j.room_type.values == 'Entire home/apt')
        parts.append(d)
    d = pd.concat(parts, ignore_index=True); d['any'] = d[list(RX)].any(axis=1)
    g = d.groupby('q'); ga = d[d['any']].groupby('q')
    out = pd.DataFrame({'reviews': g.size(), 'mention_any': g['any'].mean()})
    for k in RX:
        out[f'share_{k}'] = g[k].mean(); out[f'cond_{k}'] = ga[k].mean()
    out['headcount_n'] = g.headcount.count(); out['headcount_mean'] = g.headcount.mean()
    out['headcount_ge4'] = g.headcount.apply(lambda s: (s.dropna() >= 4).mean() if s.notna().any() else np.nan)
    out['review_len_mean'] = g['len'].mean()
    if acc is not None:
        out['accommodates_mean'] = g.accommodates.mean()
        out['accommodates_ge5'] = g.accommodates.apply(lambda s: (s.dropna() >= 5).mean() if s.notna().any() else np.nan)
        out['entire_share'] = g.entire.mean()
    out.insert(0, 'market', market); return out.reset_index()


if __name__ == '__main__':
    import warnings; warnings.filterwarnings('ignore', message='This pattern is interpreted')
    args = sys.argv[1:]; shard = None
    if args[:1] == ['--shard']: shard = (int(args[1]), int(args[2])); args = args[3:]   # --shard i n
    only = args
    res = []
    files = sorted(glob.glob(f'{RAW}/*_reviews.csv.gz'))
    for idx, rp in enumerate(files):
        market = os.path.basename(rp).replace('_reviews.csv.gz', '')
        if only and not any(o in market for o in only): continue
        if shard and idx % shard[1] != shard[0]: continue
        lp = rp.replace('_reviews.csv.gz', '_listings.csv.gz')
        print(market, flush=True)
        try: res.append(process(rp, lp if os.path.exists(lp) else None, market))
        except Exception as e: print('  ERR', e)
    df = pd.concat(res, ignore_index=True)
    tag = ('_' + '_'.join(only) if only else '') + (f'_shard{shard[0]}' if shard else '')
    df.to_csv(f'{OUT}/abnb_party_size_reviews_market_quarter{tag}.csv', index=False)
    print(df.groupby('q').reviews.sum().tail(8))
