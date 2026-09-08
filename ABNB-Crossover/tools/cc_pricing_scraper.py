"""Common Crawl product-page pricing scraper for Kay / Zales / Jared (built 2026-09-02).

Replicates the UBS Evidence Lab "discount factor" (share of goods on sale x average discount) and
"central price" (median listed price) from Signet product pages archived in Common Crawl.

For every monthly crawl since 2023-06 and each banner:
  1. harvest the CDX index for the domain (paged), keep product pages (/p/V-<code>), status 200,
     large enough to be a full render (WARC length > MIN_LEN), one capture per product code;
  2. draw a seeded random sample of N_PER products;
  3. range-fetch each WARC record from data.commoncrawl.org and parse the SAP-Hybris state JSON:
     firstVariant.priceData {value, msrp, percentageDiscount, useMsrp, priceType}, the FROM-price
     startDate (promo start), productType, productCategory, signetBreadcrumb, prevOwned, stock status;
  4. append one row per product to cc_pricing_products.csv; progress is checkpointed per
     (crawl, domain) in cc_pricing_progress.json so the run is resumable.

Run:  python cc_pricing_scraper.py            (all crawls, 100 products per banner per crawl)
      python cc_pricing_scraper.py --n 40 --crawls CC-MAIN-2026-34,CC-MAIN-2025-38   (subset)
Be polite: 4 workers, retries with backoff. ~10k range fetches for the full run.
"""
import argparse, gzip, io, json, os, random, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(HERE, "cc_pricing_products.csv")
PROGRESS = os.path.join(HERE, "cc_pricing_progress.json")
LOG = os.path.join(HERE, "cc_pricing_run.log")
DOMAINS = ["kay.com", "zales.com", "jared.com"]
MIN_LEN = 60000          # WARC record length (gz bytes); shells are ~15KB, full PDPs 150-300KB
MAX_INDEX_PAGES = 12
UA = "Mozilla/5.0 (academic research; UF student pitch project; contact ksurapaneni@ufl.edu)"
S = requests.Session(); S.headers["User-Agent"] = UA

def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def get(url, timeout=120, tries=4, ok=(200,), headers=None):
    for a in range(tries):
        try:
            r = S.get(url, timeout=timeout, headers=headers)
            if r.status_code in ok: return r
            if r.status_code == 404: return r
            if r.status_code in (429, 502, 503, 504): time.sleep(10 * (a + 1)); continue
        except requests.RequestException:
            time.sleep(4 * (a + 1))
    return None

def crawl_list(since="CC-MAIN-2023-06"):
    r = get("https://index.commoncrawl.org/collinfo.json", timeout=60)
    ids = [c["id"] for c in r.json() if c["id"] >= since]
    return sorted(ids, reverse=True)   # newest first so partial runs are useful

def harvest_index(crawl, domain):
    base = f"https://index.commoncrawl.org/{crawl}-index?url={domain}/*&output=json&fl=url,timestamp,status,filename,offset,length"
    r = get(base + "&showNumPages=true", timeout=90)
    if r is None or r.status_code != 200: return None      # index error -> retry later, do not mark done
    try: npages = int(json.loads(r.text.strip().split("\n")[0]).get("pages", 1))
    except Exception: npages = 1
    recs = []
    for page in range(min(npages, MAX_INDEX_PAGES)):
        rr = get(base + f"&page={page}", timeout=120)
        if rr is None or rr.status_code != 200: return None   # index error -> retry later
        for line in rr.text.strip().split("\n"):
            if not line.startswith("{"): continue
            try: j = json.loads(line)
            except Exception: continue
            u = j.get("url", "")
            if "/p/V-" not in u or j.get("status") != "200": continue
            try:
                if int(j.get("length", 0)) < MIN_LEN: continue
            except Exception: continue
            recs.append(j)
        time.sleep(2.0)
    # one capture per product code
    seen, uniq = set(), []
    for j in recs:
        m = re.search(r"/p/(V-[A-Za-z0-9]+)", j["url"]); code = m.group(1) if m else j["url"]
        if code in seen: continue
        seen.add(code); uniq.append(j)
    return uniq

PD_RE = re.compile(r'"firstVariant":\{.*?"priceData":\{(.*?)\}', re.S)
FROM_RE = re.compile(r'"price":\{[^{}]*"priceType":"FROM"[^{}]*\}')

def field(blob, key, cast=str):
    m = re.search(r'"' + key + r'":("?)([^,"}]*)\1', blob)
    if not m: return None
    try: return cast(m.group(2))
    except Exception: return None

OLD_ORIG = re.compile(r'origPriceProductDataLayer="([\d.]+)"')
OLD_SALE = re.compile(r'salePriceProductDataLayer="([\d.]+)"')

def parse_old(html, url):
    """Pre-Oct-2024 platform: prices in dataLayer vars, category in dataLayer.category."""
    mo, ms_ = OLD_ORIG.search(html), OLD_SALE.search(html)
    if not (mo and ms_): return None
    try: orig, sale = float(mo.group(1)), float(ms_.group(1))
    except Exception: return None
    if sale <= 0: return None
    cat = re.search(r'"dl_orderItem\.productCategory":\s*"([^"]*)"', html)
    f1 = re.search(r'"dl_orderItem\.filter1":\s*"([^"]*)"', html)
    t = re.search(r"<title>([^<]{0,200})", html)
    return dict(url=url, code=(re.search(r"/p/(V-[A-Za-z0-9]+)", url) or [None, None])[1],
                price=sale, msrp=orig if orig > 0 else sale,
                pct_discount=round((1 - sale / orig) * 100, 1) if orig > sale > 0 else 0.0,
                use_msrp=str(orig <= sale), price_type="OLD_PLATFORM", promo_start=None, promo_end=None,
                product_type=(cat.group(1).lower().rstrip("s") if cat else None),
                product_category=(cat.group(1) if cat else None), breadcrumb1=(f1.group(1) if f1 else None),
                prev_owned=None, stock_status=None, title=(t.group(1).strip() if t else None))

def parse(html, url):
    if '"priceData"' not in html: return parse_old(html, url)
    m = PD_RE.search(html)
    if not m: return parse_old(html, url)
    pd = m.group(1)
    row = dict(url=url, code=(re.search(r"/p/(V-[A-Za-z0-9]+)", url) or [None, None])[1],
               price=field(pd, "value", float), msrp=field(pd, "msrp", float),
               pct_discount=field(pd, "percentageDiscount", float), use_msrp=field(pd, "useMsrp"),
               price_type=field(pd, "priceType"))
    fm = FROM_RE.search(html)
    row["promo_start"] = field(fm.group(0), "startDate") if fm else None
    row["promo_end"] = field(fm.group(0), "endDate") if fm else None
    row["product_type"] = field(html, "productType")
    row["product_category"] = field(html, "productCategory")
    bc = re.search(r'"signetBreadcrumb":\[\{[^\]]*?"name":"([^"]*)"', html)
    row["breadcrumb1"] = bc.group(1) if bc else None
    row["prev_owned"] = field(html, "prevOwned")
    row["stock_status"] = field(html, "stockLevelStatus")
    t = re.search(r"<title>([^<]{0,200})", html); row["title"] = t.group(1).strip() if t else None
    return row

def fetch_record(rec):
    off = int(rec["offset"]); ln = int(rec["length"])
    r = get("https://data.commoncrawl.org/" + rec["filename"], timeout=120, ok=(200, 206),
            headers={"Range": f"bytes={off}-{off + ln - 1}"})
    if r is None: return None
    try:
        html = gzip.GzipFile(fileobj=io.BytesIO(r.content)).read().decode("utf-8", "ignore")
    except Exception:
        return None
    return parse(html, rec["url"])

def load_progress():
    if os.path.exists(PROGRESS): return json.load(open(PROGRESS))
    return {}

def save_progress(p): json.dump(p, open(PROGRESS, "w"), indent=1)

COLS = ["crawl", "domain", "capture_ts", "url", "code", "price", "msrp", "pct_discount", "use_msrp", "price_type",
        "promo_start", "promo_end", "product_type", "product_category", "breadcrumb1", "prev_owned", "stock_status", "title"]

def append_rows(rows):
    import csv
    new = not os.path.exists(OUT_CSV)
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new: w.writeheader()
        for r in rows: w.writerow({k: r.get(k) for k in COLS})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--crawls", type=str, default="")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    crawls = a.crawls.split(",") if a.crawls else crawl_list()
    prog = load_progress()
    log(f"start: {len(crawls)} crawls x {len(DOMAINS)} domains, n={a.n}")
    for _pass in range(6):
      pending = [(c, d) for c in crawls for d in DOMAINS if not prog.get(f"{c}|{d}", {}).get("done")]
      if not pending: break
      log(f"pass {_pass+1}: {len(pending)} pairs pending")
      for crawl, dom in pending:
        if True:
            key = f"{crawl}|{dom}"
            if prog.get(key, {}).get("done"): continue
            recs = harvest_index(crawl, dom)
            if recs is None:
                log(f"{key}: index unavailable (502/timeout) - left for retry"); time.sleep(20); continue
            if not recs:
                log(f"{key}: no product records in index"); prog[key] = {"done": True, "n_index": 0, "n_rows": 0}; save_progress(prog); continue
            rng = random.Random(f"{crawl}-{dom}")
            sample = rng.sample(recs, min(a.n, len(recs)))
            rows, fails = [], 0
            with ThreadPoolExecutor(max_workers=a.workers) as ex:
                futs = {ex.submit(fetch_record, rec): rec for rec in sample}
                for fu in as_completed(futs):
                    rec = futs[fu]
                    try: row = fu.result()
                    except Exception: row = None
                    if row and row.get("price") is not None:
                        row.update(crawl=crawl, domain=dom, capture_ts=rec["timestamp"]); rows.append(row)
                    else: fails += 1
            append_rows(rows)
            prog[key] = {"done": True, "n_index": len(recs), "n_sampled": len(sample), "n_rows": len(rows), "n_fail": fails}
            save_progress(prog)
            log(f"{key}: index {len(recs)} products, sampled {len(sample)}, parsed {len(rows)}, failed {fails}")
            time.sleep(2)
    log("finished")

if __name__ == "__main__":
    main()
