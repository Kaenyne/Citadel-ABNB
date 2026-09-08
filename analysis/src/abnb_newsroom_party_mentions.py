"""Crawl news.airbnb.com (WordPress sitemaps) for posts about group / family / solo travel and pull every sentence that
carries a number, to extend the dated party-size disclosure ledger (data/processed/abnb_party_size_disclosures.csv).
Polite: 1 request/sec, ~600 posts max. Raw HTML cached gitignored in data/raw/abnb_newsroom/.
Output: data/processed/abnb_newsroom_party_mentions.csv (post_date, url, title, sentence)
"""
import os, re, time, html, urllib.request, csv, gzip
RAW = 'data/raw/abnb_newsroom'; OUT = 'data/processed'; os.makedirs(RAW, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (research; ksurapaneni@ufl.edu)'}
KEY_URL = re.compile(r'group|famil|solo|guests|trend|report|summer|holiday|thanksgiving|travel-data|insights|stats|survey|multigen|kids|friends', re.I)
KEY_SENT = re.compile(r'(group|famil|solo|guests? per|per booking|per trip|party|multigenerational|travel(l)?ing (alone|with)|bedroom|friends|kids|children)', re.I)


def get(url):
    key = re.sub(r'[^A-Za-z0-9]+', '_', url)[-150:] + '.html.gz'; p = f'{RAW}/{key}'
    if os.path.exists(p): return gzip.open(p, 'rt', encoding='utf-8', errors='ignore').read()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: t = r.read().decode('utf-8', 'ignore')
    except Exception as e:
        print('ERR', url, e, flush=True); return ''
    gzip.open(p, 'wt', encoding='utf-8').write(t); time.sleep(1.0); return t


def sitemap_urls():
    idx = get('https://news.airbnb.com/sitemap.xml') or get('https://news.airbnb.com/sitemap_index.xml') or get('https://news.airbnb.com/wp-sitemap.xml')
    maps = re.findall(r'<loc>([^<]+)</loc>', idx)
    posts = []
    for m in maps:
        if not re.search(r'post|sitemap-\d|wp-sitemap-posts', m): continue
        posts += re.findall(r'<loc>([^<]+)</loc>', get(m))
    if not posts: posts = maps
    return sorted(set(u for u in posts if 'news.airbnb.com' in u))


if __name__ == '__main__':
    urls = [u for u in sitemap_urls() if KEY_URL.search(u.split('news.airbnb.com/')[-1])]
    print(len(urls), 'candidate posts', flush=True)
    rows = []
    for i, u in enumerate(urls[:1100]):
        h = get(u)
        if not h: continue
        title = html.unescape(re.sub(r'<[^>]+>', '', (re.search(r'<title>(.*?)</title>', h, re.S) or [None, ''])[1])).strip()
        date = (re.search(r'"datePublished":"(\d{4}-\d{2}-\d{2})', h) or re.search(r'article:published_time" content="(\d{4}-\d{2}-\d{2})', h) or [None, ''])[1]
        body = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>|<style.*?</style>', ' ', h, flags=re.S))); body = re.sub(r'\s+', ' ', body)
        for s in re.split(r'(?<=[.!?])\s+', body):
            if 40 < len(s) < 400 and KEY_SENT.search(s) and re.search(r'\d', s):
                rows.append((date, u, title[:120], s.strip()))
        if i % 50 == 0: print(i, len(rows), flush=True)
    seen = set(); out = []
    for r in rows:
        if r[3] in seen: continue
        seen.add(r[3]); out.append(r)
    with open(f'{OUT}/abnb_newsroom_party_mentions.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['post_date', 'url', 'title', 'sentence']); w.writerows(sorted(out))
    print('sentences', len(out))
