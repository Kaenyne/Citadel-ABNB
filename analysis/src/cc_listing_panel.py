"""Common Crawl matched-listing panel for airbnb.com/rooms/<id> pages, 2021 to 2026 (plan-of-attack branch 2).

Builds on analysis/src/cc_airbnb_probe.py (2026-09-05 prototype) and the crossover's cc_matched_sku.py. Common
Crawl is a public web archive; nothing here touches airbnb.com. Volumes: one CDX index query per crawl per domain
(about 50 crawls x 9 domains), then HTTP range fetches of individual WARC records for matched listings only.
The index is read straight from each crawl's cdx shards on data.commoncrawl.org (binary search of cluster.idx,
then the 4-10 compressed blocks covering the airbnb rooms key range), because the index.commoncrawl.org API
rate-limits and blocked this IP after a few dozen queries on 5 Sep 2026. `cdx()` is kept for single lookups.

Steps:
  py -3.13 analysis/src/cc_listing_panel.py harvest    CDX index rows for every crawl since CC-MAIN-2021-04
                                                       -> data/raw/commoncrawl/index/<crawl>__<domain>.jsonl.gz
                                                       -> data/processed/cc_index_summary.csv
  py -3.13 analysis/src/cc_listing_panel.py survival   index-only exhibit: of listings captured 200 in an earlier
                                                       crawl and re-fetched in a later crawl, share still 200 vs
                                                       gone (404/410/redirect) -> data/processed/cc_listing_survival.csv
  py -3.13 analysis/src/cc_listing_panel.py fetch      pick listing ids captured (status 200, full render) in two
                                                       crawls >= 270 days apart, sample --n, range-fetch both records
                                                       -> data/raw/commoncrawl/records/<crawl>/<id>.warc.gz
  py -3.13 analysis/src/cc_listing_panel.py panel      parse every fetched record (era-tolerant regexes)
                                                       -> data/processed/cc_listing_panel.csv (one row per capture)
                                                       -> data/processed/cc_matched_listings.csv (one row per pair)
                                                       -> data/processed/cc_panel_summary.csv (by capture year / pair)
  py -3.13 analysis/src/cc_listing_panel.py figures    -> analysis/figures/cc_*.png

What the archive carries (probe, 5 Sep 2026): listing id, Superhost flag, room type, capacity, localized location,
lat/lng, review count (visibleReviewCount 2021-2023, ratingCount / reviewCount 2024+), rating, Guest Favorite
flag `isGuestFavorite` (2024+), home tier, host review total and years hosting (2025+). NO nightly price in any era (loaded
client-side via GraphQL). Caveats for the slide: Common Crawl's sample is whatever the crawler reached (skewed to
listings linked from elsewhere, e.g. utm_source=chatgpt.com in 2026); review counts lag stays by weeks; template
changes between eras (2023, 2025) moved fields between JSON blocks, so a missing field can be a parser gap.
"""
import argparse, collections, concurrent.futures, gzip, io, json, random, re, sys, time
from pathlib import Path
import numpy as np, pandas as pd, requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/commoncrawl"
IDX = RAW / "index"
REC = RAW / "records"
PROC = ROOT / "data/processed"
FIG = ROOT / "analysis/figures"
UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}
INDEX = "https://index.commoncrawl.org/{crawl}-index"
DATA = "https://data.commoncrawl.org/"
DOMAINS = ["airbnb.com", "airbnb.co.uk", "airbnb.ca", "airbnb.com.au", "airbnb.de", "airbnb.fr", "airbnb.es", "airbnb.it", "airbnb.com.br"]
CLUSTER = DATA + "cc-index/collections/{crawl}/indexes/cluster.idx"
SHARD = DATA + "cc-index/collections/{crawl}/indexes/{file}"
FIRST_CRAWL = "CC-MAIN-2021-04"
MIN_FULL_RENDER = 60000  # compressed WARC bytes; smaller records are bot-wall / redirect stubs
SESS = requests.Session(); SESS.headers.update(UA)


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def listing_id(url):
    m = re.search(r"/rooms/(?:plus/|luxury/)?(\d{5,})", url)
    return m.group(1) if m else None


def crawl_date(crawl):
    """Approximate calendar date of a crawl from its ISO week label, e.g. CC-MAIN-2024-22 -> 2024-05-27."""
    y, w = crawl.split("-")[2:4]
    return pd.Timestamp.fromisocalendar(int(y), int(w), 1)


# ----------------------------------------------------------------------------------------------------- harvest
# collinfo.json as of 2026-09-05 (the index API host also serves this file and may be unreachable; see above)
CRAWLS = ["CC-MAIN-2021-04", "CC-MAIN-2021-10", "CC-MAIN-2021-17", "CC-MAIN-2021-21", "CC-MAIN-2021-25", "CC-MAIN-2021-31", "CC-MAIN-2021-39",
          "CC-MAIN-2021-43", "CC-MAIN-2021-49", "CC-MAIN-2022-05", "CC-MAIN-2022-21", "CC-MAIN-2022-27", "CC-MAIN-2022-33", "CC-MAIN-2022-40",
          "CC-MAIN-2022-49", "CC-MAIN-2023-06", "CC-MAIN-2023-14", "CC-MAIN-2023-23", "CC-MAIN-2023-40", "CC-MAIN-2023-50", "CC-MAIN-2024-10",
          "CC-MAIN-2024-18", "CC-MAIN-2024-22", "CC-MAIN-2024-26", "CC-MAIN-2024-30", "CC-MAIN-2024-33", "CC-MAIN-2024-38", "CC-MAIN-2024-42",
          "CC-MAIN-2024-46", "CC-MAIN-2024-51", "CC-MAIN-2025-05", "CC-MAIN-2025-08", "CC-MAIN-2025-13", "CC-MAIN-2025-18", "CC-MAIN-2025-21",
          "CC-MAIN-2025-26", "CC-MAIN-2025-30", "CC-MAIN-2025-33", "CC-MAIN-2025-38", "CC-MAIN-2025-43", "CC-MAIN-2025-47", "CC-MAIN-2025-51",
          "CC-MAIN-2026-04", "CC-MAIN-2026-08", "CC-MAIN-2026-12", "CC-MAIN-2026-17", "CC-MAIN-2026-21", "CC-MAIN-2026-25", "CC-MAIN-2026-30",
          "CC-MAIN-2026-34"]


def crawl_ids():
    """CRAWLS plus anything newer in collinfo.json when the index host answers."""
    ids = set(CRAWLS)
    try:
        cols = SESS.get("https://index.commoncrawl.org/collinfo.json", timeout=20).json()
        ids |= {c["id"] for c in cols if c["id"].startswith("CC-MAIN-20") and c["id"] >= FIRST_CRAWL}
    except Exception:
        pass
    return sorted(ids)


def cdx(crawl, pattern, page=None, tries=5):
    params = {"url": pattern, "output": "json"}
    if page is None:
        params["showNumPages"] = "true"
    else:
        params["page"] = page
    for attempt in range(tries):
        try:
            r = SESS.get(INDEX.format(crawl=crawl), params=params, timeout=240)
            if r.status_code == 200:
                if page is None:
                    return json.loads(r.text.strip() or "{}")
                lines = [l for l in r.text.splitlines() if l.strip()]
                rows = [json.loads(l) for l in lines[:-1]]
                try:  # the last line of a page is sometimes truncated mid-record; keep it only if it parses
                    rows.append(json.loads(lines[-1]))
                except (json.JSONDecodeError, IndexError):
                    if len(r.content) < 1000:  # a short, broken body is a failed page: retry
                        raise ValueError("short broken page")
                return rows
            if r.status_code == 404:  # nothing in this crawl for the pattern
                return {} if page is None else []
        except (requests.RequestException, ValueError, json.JSONDecodeError):
            pass
        time.sleep(8 * (attempt + 1))
    return None


def surt_prefix(dom):
    """airbnb.co.uk -> uk,co,airbnb)/rooms/ (Common Crawl SURT form; www. is dropped by canonicalisation)."""
    return ",".join(reversed(dom.split("."))) + ")/rooms/"


def get_range(url, start, length, tries=4):
    for attempt in range(tries):
        try:
            r = SESS.get(url, headers={"Range": f"bytes={start}-{start + length - 1}"}, timeout=120)
            if r.status_code in (200, 206):
                return r.content
            if r.status_code == 416:
                return b""
            if r.status_code == 403 and b"Request blocked" in r.content:
                raise RuntimeError("blocked by CloudFront (rate limit); wait and re-run")
        except requests.RequestException:
            pass
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"range fetch failed {url} {start}")


_cluster_size = {}
args_delay = [0.5]  # seconds between range requests; data.commoncrawl.org (CloudFront) blocks bursts


def cluster_size(crawl):
    if crawl not in _cluster_size:
        r = SESS.head(CLUSTER.format(crawl=crawl), timeout=60)
        r.raise_for_status()
        _cluster_size[crawl] = int(r.headers["Content-Length"])
    return _cluster_size[crawl]


def cluster_lines_at(crawl, pos, chunk=1 << 16):
    """Complete cluster.idx lines starting at or after byte pos (first partial line dropped unless pos == 0)."""
    size = cluster_size(crawl)
    if pos >= size:
        return [], pos
    raw = get_range(CLUSTER.format(crawl=crawl), pos, min(chunk, size - pos))
    time.sleep(args_delay[0])
    txt = raw.decode("utf-8", "ignore")
    lines = txt.split("\n")
    if pos > 0:
        lines = lines[1:]
    if pos + chunk < size:
        lines = lines[:-1]  # last line may be cut
    return [l for l in lines if l], pos


def cdx_via_cluster(crawl, prefix):
    """All CDX index rows whose SURT key starts with prefix, read straight from the crawl's cdx shards on
    data.commoncrawl.org: binary-search cluster.idx (one line per ~3,000-record compressed block, sorted by SURT)
    for the blocks that can contain the prefix, then range-fetch and filter those blocks. No index API involved."""
    size = cluster_size(crawl)
    lo, hi = 0, size
    while hi - lo > 1 << 16:  # narrow to the 64 KB window that contains the first key >= prefix
        mid = (lo + hi) // 2
        lines, _ = cluster_lines_at(crawl, mid)
        if not lines:
            hi = mid
            continue
        key = lines[0].split(" ", 1)[0]
        if key < prefix:
            lo = mid
        else:
            hi = mid
    lines, _ = cluster_lines_at(crawl, lo, chunk=1 << 18)  # 256 KB from lo covers the window and its neighbours
    entries = []
    for l in lines:
        parts = l.split("\t")
        if len(parts) < 4:
            continue
        key = parts[0].split(" ", 1)[0]
        entries.append((key, parts[1], int(parts[2]), int(parts[3])))
    if not entries:
        return []
    end_key = prefix[:-1] + chr(ord(prefix[-1]) + 1)  # "com,airbnb)/rooms0" sorts after every /rooms/ key
    # blocks to read: the last block starting before prefix, plus every block starting inside [prefix, end_key)
    idx_first = max([i for i, e in enumerate(entries) if e[0] < prefix] or [0])
    wanted = [e for i, e in enumerate(entries) if i >= idx_first and e[0] < end_key]
    if entries[-1][0] < end_key:
        # the prefix range may run past the 256 KB window (unlikely: 4-10 blocks); extend once
        more, _ = cluster_lines_at(crawl, lo + (1 << 18), chunk=1 << 18)
        for l in more:
            parts = l.split("\t")
            if len(parts) >= 4:
                k = parts[0].split(" ", 1)[0]
                if k < end_key:
                    wanted.append((k, parts[1], int(parts[2]), int(parts[3])))
                else:
                    break
    rows = []
    for key, file, off, ln in wanted:
        blob = get_range(SHARD.format(crawl=crawl, file=file), off, ln)
        for l in gzip.decompress(blob).decode("utf-8", "ignore").split("\n"):
            if l.startswith(prefix):
                surt, ts, js = l.split(" ", 2)
                try:
                    r = json.loads(js)
                except json.JSONDecodeError:
                    continue
                r.setdefault("timestamp", ts); r.setdefault("urlkey", surt)
                rows.append(r)
        time.sleep(args_delay[0])
    return rows


def harvest_one(crawl, dom, refresh=False):
    out = IDX / f"{crawl}__{dom}.jsonl.gz"
    if out.exists() and not refresh:
        return crawl, dom, "cached", sum(1 for _ in gzip.open(out, "rt", encoding="utf-8"))
    try:
        rows = cdx_via_cluster(crawl, surt_prefix(dom))
    except Exception as e:
        return crawl, dom, f"error_{type(e).__name__}", 0
    with gzip.open(out, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return crawl, dom, "ok", len(rows)


def load_index(crawls=None):
    files = sorted(IDX.glob("*.jsonl.gz"))
    frames = []
    for fp in files:
        crawl, dom = fp.name[:-9].split("__")
        if crawls and crawl not in crawls:
            continue
        rows = [json.loads(l) for l in gzip.open(fp, "rt", encoding="utf-8")]
        if not rows:
            continue
        d = pd.DataFrame(rows)
        d["crawl"], d["domain"] = crawl, dom
        frames.append(d)
    x = pd.concat(frames, ignore_index=True)
    x["listing_id"] = x.url.map(listing_id)
    x["length"] = pd.to_numeric(x.length, errors="coerce")
    x["offset"] = pd.to_numeric(x.offset, errors="coerce")
    x["status"] = x.status.astype(str)
    if "timestamp" not in x:
        x["timestamp"] = None
    x["ts"] = pd.to_datetime(x.timestamp, format="%Y%m%d%H%M%S", errors="coerce")
    x["ts_from_crawl"] = x.ts.isna()
    x["ts"] = x.ts.fillna(x.crawl.map(crawl_date))  # shard rows harvested before 2026-09-05 16:30 lack the capture time
    x["full"] = (x.status == "200") & (x.length >= MIN_FULL_RENDER)
    return x[x.listing_id.notna()].copy()


def harvest(args):
    IDX.mkdir(parents=True, exist_ok=True)
    crawls = crawl_ids()
    jobs = [(c, d) for c in crawls for d in DOMAINS]
    log(f"{len(crawls)} crawls x {len(DOMAINS)} domains = {len(jobs)} index queries, {args.workers} workers")
    args_delay[0] = args.delay
    blocked = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for crawl, dom, st, n in ex.map(lambda j: harvest_one(*j, refresh=args.refresh), jobs):
            if st != "cached":
                log(f"  {crawl} {dom}: {st} {n} rows")
            if st.startswith("error"):
                blocked += 1
                if blocked >= 6:
                    log("too many errors in a row: data.commoncrawl.org is probably rate-limiting; stopping, re-run later")
                    ex.shutdown(cancel_futures=True)
                    break
            else:
                blocked = 0
    x = load_index()
    s = x.groupby("crawl").agg(rows=("url", "size"), status_200=("status", lambda v: (v == "200").sum()), full_renders=("full", "sum"),
                               unique_ids=("listing_id", "nunique"), unique_ids_full=("listing_id", lambda v: v[x.loc[v.index, "full"]].nunique()),
                               domains=("domain", "nunique"), first_capture=("ts", "min"), last_capture=("ts", "max"),
                               with_check_in=("url", lambda v: v.str.contains("check_in").sum())).reset_index()
    s["crawl_date"] = s.crawl.map(crawl_date)
    PROC.mkdir(parents=True, exist_ok=True)
    s.to_csv(PROC / "cc_index_summary.csv", index=False)
    print(s.to_string(index=False))
    log(f"index: {len(x):,} rows, {x.listing_id.nunique():,} unique listing ids, {x[x.full].listing_id.nunique():,} with a full 200 render")


# ----------------------------------------------------------------------------------------------------- survival
def survival(args):
    """Index-only: for each later crawl B, listings whose URL was a status-200 capture in some earlier crawl A and
    which the crawler re-fetched in B. Share of those re-fetches returning 200 = survival; 404/410/3xx = gone.
    Only re-fetched listings count (absence from B is not evidence of removal)."""
    x = load_index()
    first_ok = x[x.status == "200"].groupby("listing_id").ts.min().rename("first_ok")
    x = x.join(first_ok, on="listing_id")
    re_ = x[(x.ts > x.first_ok + pd.Timedelta(days=60))]  # re-fetches at least 60 days after first 200 capture
    re_ = re_.sort_values("ts").drop_duplicates(["listing_id", "crawl"], keep="last")
    re_["outcome"] = np.select([re_.status == "200", re_.status.isin(["404", "410"]), re_.status.str.startswith("3")], ["live", "removed", "redirect"], "other")
    re_["age_days"] = (re_.ts - re_.first_ok).dt.days
    re_["age_bucket"] = pd.cut(re_.age_days, [59, 365, 730, 1095, 10000], labels=["2-12m", "1-2y", "2-3y", "3y+"])
    s = re_.groupby(["crawl"]).agg(refetched=("listing_id", "size"), live=("outcome", lambda v: (v == "live").sum()), removed=("outcome", lambda v: (v == "removed").sum()),
                                   redirect=("outcome", lambda v: (v == "redirect").sum()), other=("outcome", lambda v: (v == "other").sum()), median_age_days=("age_days", "median")).reset_index()
    s["survival_share"] = s.live / s.refetched
    s["crawl_date"] = s.crawl.map(crawl_date)
    s["year"] = s.crawl_date.dt.year
    # crawls where Airbnb answered 200 for everything (2021, Oct 2025 to Jan 2026) carry no removal signal
    s["status_informative"] = (s.removed / s.refetched) >= 0.02
    inf = set(s.loc[s.status_informative, "crawl"])
    re_ = re_[re_.crawl.isin(inf)]
    by_age = re_.groupby(["age_bucket"], observed=True).agg(refetched=("listing_id", "size"), live=("outcome", lambda v: (v == "live").sum())).reset_index()
    by_age["survival_share"] = by_age.live / by_age.refetched
    s.to_csv(PROC / "cc_listing_survival.csv", index=False)
    by_age.to_csv(PROC / "cc_listing_survival_by_age.csv", index=False)
    print(s[["crawl", "refetched", "live", "removed", "redirect", "survival_share", "median_age_days", "status_informative"]].to_string(index=False))
    print(by_age.to_string(index=False))


# ----------------------------------------------------------------------------------------------------- fetch
def fetch_record(rec, path, tries=3):
    if path.exists() and path.stat().st_size > 1000:
        return "cached"
    off, ln = int(rec["offset"]), int(rec["length"])
    for attempt in range(tries):
        try:
            r = SESS.get(DATA + rec["filename"], headers={"Range": f"bytes={off}-{off + ln - 1}"}, timeout=240)
            if r.status_code in (200, 206) and len(r.content) > 500:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(r.content)
                time.sleep(args_delay[0])
                return "ok"
            if r.status_code == 403 and b"Request blocked" in r.content:
                return "blocked"
            last = f"http_{r.status_code}"
        except requests.RequestException as e:
            last = f"err_{type(e).__name__}"
        time.sleep(5 * (attempt + 1))
    return last


def choose_pairs(x, n, seed=7, min_days=270):
    """For every listing with full renders in >= 2 crawls at least min_days apart: earliest and latest full render.
    Returns up to n pairs sampled deterministically, plus all single captures of the chosen listings are not needed."""
    f = x[x.full].sort_values("ts")
    g = f.groupby("listing_id")
    first, last = g.first(), g.last()
    span = (last.ts - first.ts).dt.days
    ok = span[span >= min_days].index
    rng = random.Random(seed)
    # stratify by year of the later capture so every window gets pairs (a plain sample is dominated by 2021 ids)
    by_year = {}
    for lid in sorted(ok):
        by_year.setdefault(last.loc[lid, "ts"].year, []).append(lid)
    quota = max(1, n // len(by_year))
    chosen = []
    for y, ids in sorted(by_year.items()):
        rng.shuffle(ids)
        chosen += ids[:quota]
    chosen = chosen[:n]
    pairs = []
    for lid in chosen:
        a, b = first.loc[lid], last.loc[lid]
        pairs.append(dict(listing_id=lid, crawl_a=a.crawl, ts_a=a.ts.strftime("%Y%m%d%H%M%S"), crawl_b=b.crawl, ts_b=b.ts.strftime("%Y%m%d%H%M%S"), days_apart=int((b.ts - a.ts).days),
                          rec_a=dict(filename=a.filename, offset=int(a.offset), length=int(a.length), url=a.url),
                          rec_b=dict(filename=b.filename, offset=int(b.offset), length=int(b.length), url=b.url)))
    return pairs, len(ok)


def fetch(args):
    x = load_index()
    pairs, eligible = choose_pairs(x, args.n, min_days=args.min_days)
    log(f"{eligible:,} listings have full renders >= {args.min_days} days apart; fetching {len(pairs)} pairs with {args.workers} workers")
    log("pairs by window: " + ", ".join(f"{k}: {v}" for k, v in collections.Counter(f"{p['ts_a'][:4]}->{p['ts_b'][:4]}" for p in pairs).most_common()))
    spans = pd.Series([p["days_apart"] for p in pairs])
    log(f"days apart: median {spans.median():.0f}, min {spans.min()}, max {spans.max()}")
    (RAW / "matched_pairs.json").write_text(json.dumps(pairs, indent=0))
    jobs = []
    for p in pairs:
        jobs.append((p["rec_a"], REC / p["crawl_a"] / f"{p['listing_id']}.warc.gz"))
        jobs.append((p["rec_b"], REC / p["crawl_b"] / f"{p['listing_id']}.warc.gz"))
    args_delay[0] = args.delay
    cnt = collections.Counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, st in enumerate(ex.map(lambda j: fetch_record(*j), jobs)):
            cnt[st] += 1
            if (i + 1) % 200 == 0:
                log(f"  {i + 1}/{len(jobs)} {dict(cnt)}")
    log(f"fetch done: {dict(cnt)}")


# ----------------------------------------------------------------------------------------------------- parse
FIELDS = {
    "is_superhost": r'"isSuperhost":(true|false)',
    "room_type": r'"roomType":"([^"]+)"',
    "person_capacity": r'"personCapacity":"?(\d+)',
    "localized_location": r'"localizedLocation":"([^"]{0,80})"',
    "lat": r'"(?:listingLat|latitude|lat)":(-?\d+\.\d+)',
    "lng": r'"(?:listingLng|longitude|lng)":(-?\d+\.\d+)',
    "visible_review_count": r'"visibleReviewCount":"?(\d+)',  # quoted in 2021 pages
    "rating_count": r'"ratingCount":"?(\d+)',
    "review_count": r'"reviewCount":"?(\d+)',
    "reviews_count": r'"reviewsCount":"?(\d+)',
    "rating_value": r'"ratingValue":"?(\d(?:\.\d+)?)',
    "star_rating": r'"starRating":"?(\d(?:\.\d+)?)',
    "home_tier": r'"homeTier":(\d)',
    "picture_count": r'"pictureCount":(\d+)',
    "host_reviews": r'"label":"Reviews","value":"([\d,]+)"',
    "host_years": r'"label":"Years? hosting","value":"(\d+)"',
    "host_months": r'"label":"Months? hosting","value":"(\d+)"',
    "instant_book": r'"instantBook(?:able)?":(true|false)',
    "property_type": r'"propertyType":"([^"]{0,60})"',
    "guest_favorite": r'"isGuestFavorite":(true|false)',  # 2024+; the GUEST_FAVORITE_BANNER slot exists on every page
    "og_title": r'property="og:title" content="([^"]{0,200})"',
    "canonical": r'"canonicalUrl":"([^"]{0,120})"',
    "price_present": r'"structuredDisplayPrice":(\{)',
}


def parse_html(html):
    out = {}
    for k, pat in FIELDS.items():
        m = re.search(pat, html)
        out[k] = m.group(1) if m else None
    out["price_present"] = bool(out["price_present"])
    for k in ("is_superhost", "instant_book", "guest_favorite"):
        out[k] = {"true": True, "false": False}.get(out[k])
    for k in ("person_capacity", "visible_review_count", "rating_count", "review_count", "reviews_count", "home_tier", "picture_count", "host_years", "host_months"):
        out[k] = int(out[k]) if out[k] is not None else None
    out["host_reviews"] = int(out["host_reviews"].replace(",", "")) if out["host_reviews"] else None
    for k in ("lat", "lng", "rating_value", "star_rating"):
        out[k] = float(out[k]) if out[k] is not None else None
    # review count: prefer the listing-level fields; ratingCount (LD+JSON) is the listing's, reviewsCount can be the host's
    rc = [v for v in (out["visible_review_count"], out["rating_count"], out["review_count"]) if v is not None]
    out["reviews"] = rc[0] if rc else None
    out["rating"] = out["rating_value"] if out["rating_value"] is not None else out["star_rating"]
    if out["og_title"]:
        m = re.search(r"(\d+) bedroom", out["og_title"]); out["bedrooms"] = int(m.group(1)) if m else (0 if "Studio" in out["og_title"] else None)
        if out["rating"] is None:
            m = re.search(r"★\s*([\d.]+)", out["og_title"]); out["rating"] = float(m.group(1)) if m else None
    else:
        out["bedrooms"] = None
    out["html_bytes"] = len(html)
    return out


def region_of(lat, lng):
    if lat is None or lng is None:
        return None
    if -170 <= lng <= -50 and 15 <= lat <= 72: return "NA"
    if -120 <= lng <= -30 and -56 <= lat < 15: return "LatAm"
    if -30 <= lng <= 60 and 34 <= lat <= 72: return "Europe"
    if -20 <= lng <= 60 and -35 <= lat < 34: return "MEA"
    if 60 < lng <= 180 or lng < -170: return "APAC"
    return "other"


def read_warc(path):
    raw = gzip.GzipFile(fileobj=io.BytesIO(path.read_bytes())).read()
    parts = raw.split(b"\r\n\r\n", 2)
    return parts[-1].decode("utf-8", "ignore")


def panel(args):
    pairs = json.loads((RAW / "matched_pairs.json").read_text())
    rows = []
    for p in pairs:
        for side in ("a", "b"):
            path = REC / p[f"crawl_{side}"] / f"{p['listing_id']}.warc.gz"
            if not path.exists():
                continue
            try:
                d = parse_html(read_warc(path))
            except Exception as e:
                d = dict(parse_error=type(e).__name__)
            rows.append(dict(listing_id=p["listing_id"], side=side, crawl=p[f"crawl_{side}"], timestamp=p[f"ts_{side}"], url=p[f"rec_{side}"]["url"], **d))
    x = pd.DataFrame(rows)
    x["ts"] = pd.to_datetime(x.timestamp, format="%Y%m%d%H%M%S", errors="coerce")
    x["year"] = x.ts.dt.year
    x["region"] = [region_of(a, b) for a, b in zip(x.lat, x.lng)]
    x["parsed_ok"] = x.reviews.notna() | x.room_type.notna()
    # isGuestFavorite is only serialised for qualifying listings in the 2023-2024 template (every parsed value is
    # true), so the share is only meaningful from 2025 when false values appear too
    x.loc[x.year < 2025, "guest_favorite"] = None
    x.to_csv(PROC / "cc_listing_panel.csv", index=False)
    log(f"panel: {len(x)} captures, parsed_ok {x.parsed_ok.mean():.0%}, reviews present {x.reviews.notna().mean():.0%}, superhost present {x.is_superhost.notna().mean():.0%}, latlng present {x.lat.notna().mean():.0%}")
    # matched pairs
    a = x[x.side == "a"].set_index("listing_id"); b = x[x.side == "b"].set_index("listing_id")
    common = a.index.intersection(b.index)
    m = pd.DataFrame(dict(listing_id=common, crawl_a=a.loc[common, "crawl"].values, crawl_b=b.loc[common, "crawl"].values,
                          ts_a=a.loc[common, "ts"].values, ts_b=b.loc[common, "ts"].values,
                          reviews_a=a.loc[common, "reviews"].values, reviews_b=b.loc[common, "reviews"].values,
                          superhost_a=a.loc[common, "is_superhost"].values, superhost_b=b.loc[common, "is_superhost"].values,
                          guest_fav_a=a.loc[common, "guest_favorite"].values, guest_fav_b=b.loc[common, "guest_favorite"].values,
                          rating_a=a.loc[common, "rating"].values, rating_b=b.loc[common, "rating"].values,
                          room_type=b.loc[common, "room_type"].fillna(a.loc[common, "room_type"]).values,
                          region=b.loc[common, "region"].fillna(a.loc[common, "region"]).values,
                          location=b.loc[common, "localized_location"].fillna(a.loc[common, "localized_location"]).values))
    m["days_apart"] = (pd.to_datetime(m.ts_b) - pd.to_datetime(m.ts_a)).dt.days
    m["review_delta"] = m.reviews_b - m.reviews_a
    m["reviews_per_year"] = m.review_delta / m.days_apart * 365
    m["year_a"], m["year_b"] = pd.to_datetime(m.ts_a).dt.year, pd.to_datetime(m.ts_b).dt.year
    m["window"] = m.year_a.astype(str) + "->" + m.year_b.astype(str)
    m.to_csv(PROC / "cc_matched_listings.csv", index=False)
    # summaries
    ok = m[m.review_delta.notna() & (m.review_delta >= 0)]
    by_window = ok.groupby("window").agg(pairs=("listing_id", "size"), median_days=("days_apart", "median"),
                                          median_reviews_a=("reviews_a", "median"), mean_reviews_per_year=("reviews_per_year", "mean"), median_reviews_per_year=("reviews_per_year", "median"),
                                          share_no_new_reviews=("review_delta", lambda v: (v == 0).mean()),
                                          superhost_a=("superhost_a", "mean"), superhost_b=("superhost_b", "mean"),
                                          guest_fav_b=("guest_fav_b", "mean")).reset_index()
    by_year = x[x.parsed_ok].groupby("year").agg(captures=("listing_id", "size"), superhost_share=("is_superhost", "mean"), guest_favorite_share=("guest_favorite", "mean"),
                                                  entire_home_share=("room_type", lambda v: v.eq("Entire home/apt").mean()), median_reviews=("reviews", "median"), median_rating=("rating", "median"),
                                                  price_present=("price_present", "mean"), NA=("region", lambda v: (v == "NA").mean()), Europe=("region", lambda v: (v == "Europe").mean()),
                                                  LatAm=("region", lambda v: (v == "LatAm").mean()), APAC=("region", lambda v: (v == "APAC").mean())).reset_index()
    by_window.loc[by_window.window.str[-4:].astype(int) < 2025, "guest_fav_b"] = None
    by_window.to_csv(PROC / "cc_panel_summary.csv", index=False)
    by_year.to_csv(PROC / "cc_panel_by_year.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(by_window.round(3).to_string(index=False)); print(by_year.round(3).to_string(index=False))
    neg = m[m.review_delta < 0]
    log(f"pairs {len(m)}, with review counts both sides {m.review_delta.notna().sum()}, negative deltas (parser/era mismatch) {len(neg)}")


# ----------------------------------------------------------------------------------------------------- figures
def figures(args):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    foot = "Source: Common Crawl CDX index and WARC records for airbnb.com/rooms pages (public archive); Citadel-ABNB analysis"
    s = pd.read_csv(PROC / "cc_listing_survival.csv", parse_dates=["crawl_date"])
    s = s[s.refetched >= 50]
    inf, uninf = s[s.status_informative], s[~s.status_informative]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(inf.crawl_date, inf.survival_share * 100, width=22, color="#4C72B0", label="crawls with a removal signal")
    ax.bar(uninf.crawl_date, uninf.survival_share * 100, width=22, color="none", edgecolor="#999999", hatch="///", label="Airbnb answered 200 for dead listings (excluded)")
    ax.set_ylim(70, 101); ax.set_ylabel("% of re-fetched listings still live")
    ax.set_title("Listing survival: share of re-fetched airbnb.com/rooms pages still live in each crawl", loc="left", fontweight="bold", fontsize=11)
    ax.text(0.01, 0.97, f"{int(inf.refetched.median()):,} re-fetched listings per crawl (median); a re-fetch is a page first captured live at least 60 days earlier", transform=ax.transAxes, fontsize=8, va="top", color="#444444")
    ax.legend(frameon=False, fontsize=8, loc="lower left"); ax.grid(alpha=0.3, axis="y")
    fig.text(0.01, 0.005, foot, fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "cc_listing_survival.png", dpi=150); plt.close(fig)
    m = pd.read_csv(PROC / "cc_matched_listings.csv")
    ok = m[m.review_delta.notna() & (m.review_delta >= 0)]
    if len(ok):
        w = ok.groupby("window").agg(n=("listing_id", "size"), mean=("reviews_per_year", "mean"), med=("reviews_per_year", "median")).reset_index()
        w = w[w.n >= 30]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(w.window, w["mean"], color="#4C72B0", label="mean"); ax.plot(w.window, w.med, "o", color="#DD8452", label="median")
        for i, (n, v) in enumerate(zip(w.n, w["mean"])):
            ax.text(i, v + 0.2, f"n={n}", ha="center", fontsize=7)
        ax.set_title("Same-listing review velocity by capture window (reviews added per year on matched listings)", loc="left", fontweight="bold", fontsize=11)
        ax.set_ylabel("reviews per year"); ax.legend(frameon=False); ax.grid(alpha=0.3, axis="y"); plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.text(0.01, 0.005, foot, fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "cc_review_velocity.png", dpi=150); plt.close(fig)
    y = pd.read_csv(PROC / "cc_panel_by_year.csv")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(y.year, y.superhost_share * 100, marker="o", label="Superhost share"); ax.plot(y.year, y.guest_favorite_share * 100, marker="o", label="Guest Favorite share (parsed reliably from 2025)")
    ax.plot(y.year, y.entire_home_share * 100, marker="o", label="Entire-home share")
    ax.set_title("Professionalisation markers in captured listing pages, by capture year", loc="left", fontweight="bold", fontsize=11)
    ax.set_ylabel("% of parsed captures"); ax.legend(frameon=False); ax.grid(alpha=0.3)
    fig.text(0.01, 0.005, foot, fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "cc_professionalisation.png", dpi=150); plt.close(fig)
    log(f"figures written to {FIG}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["harvest", "survival", "fetch", "panel", "figures"])
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--n", type=int, default=1500, help="matched listing pairs to fetch")
    ap.add_argument("--min-days", type=int, default=270)
    ap.add_argument("--delay", type=float, default=0.5, help="seconds between range requests to data.commoncrawl.org")
    ap.add_argument("--refresh", action="store_true", help="re-harvest index files that already exist")
    a = ap.parse_args()
    {"harvest": harvest, "survival": survival, "fetch": fetch, "panel": panel, "figures": figures}[a.step](a)


if __name__ == "__main__":
    sys.exit(main())
