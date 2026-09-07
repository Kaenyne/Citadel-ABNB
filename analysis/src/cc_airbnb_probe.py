"""Common Crawl probe for archived airbnb.com/rooms/<id> pages (prototype, 2026-09-05).

What it does:
  1. Counts captures of airbnb.com/rooms/* in one crawl via the CDX index (status, size, unique listing ids,
     share of URLs carrying check_in dates).
  2. Range-fetches one full WARC record from data.commoncrawl.org and reports which fields the archived HTML
     actually contains.

Findings from the first run (see research/notes/2026-09-05_crossover-checklist.md and docs plan):
  - CC-MAIN-2026-30: 9,946 index rows, 7,884 status-200, 7,534 unique listing ids, every full render 140-170 KB
    compressed (about 1 MB HTML). Crawls back to 2021 hold 4-10 index blocks each (roughly 8k-20k rows).
  - No price in any era (2022, 2024, 2026 samples): structuredDisplayPrice is null and no priceString/amount
    fields exist, with or without check_in dates in the URL. Prices load client-side via GraphQL.
  - Present in every era: listingId, isSuperhost, roomType, personCapacity, localizedLocation, latitude/longitude,
    review count (visibleReviewCount in 2022/2024, ratingCount + ratingValue in the 2026 LD+JSON block),
    cancellationPolicies, amenities. GUEST_FAVORITE appears from 2024/2025.
  So the usable panel is listing survival, review velocity, Superhost / Guest Favorite share and geography mix,
  not nightly price. For price use Inside Airbnb listings.csv (CC-BY 4.0) instead.

Usage:
  python analysis/src/cc_airbnb_probe.py --crawl CC-MAIN-2026-30 --fetch 1
Polite use: one index page and one or two WARC range fetches per run. Common Crawl is a public archive; this
does not touch airbnb.com.
"""
import argparse, collections, gzip, io, json, re, sys
import requests

UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}
INDEX = "https://index.commoncrawl.org/{crawl}-index"
DATA = "https://data.commoncrawl.org/"
FIELDS = {
    "listingId": r'"listingId":"?(\d+)',
    "isSuperhost": r'"isSuperhost":(true|false)',
    "roomType": r'"roomType":"([^"]+)"',
    "personCapacity": r'"personCapacity":(\d+)',
    "localizedLocation": r'"localizedLocation":"([^"]{0,80})"',
    "latitude": r'"latitude":(-?\d+\.\d+)',
    "visibleReviewCount": r'"visibleReviewCount":(\d+)',
    "ratingCount": r'"ratingCount":"?(\d+)',
    "ratingValue": r'"ratingValue":(\d+(?:\.\d+)?)',
    "guestFavorite": r'(GUEST_FAVORITE)',
    "structuredDisplayPrice": r'"structuredDisplayPrice":(\{|null)',
    "priceString": r'"priceString":"([^"]{0,40})"',
}


def index_rows(crawl, pattern="airbnb.com/rooms/*", page=0):
    r = requests.get(INDEX.format(crawl=crawl), params={"url": pattern, "output": "json", "page": page}, headers=UA, timeout=180)
    r.raise_for_status()
    return [json.loads(l) for l in r.text.splitlines() if l.strip()]


def fetch_html(rec):
    off, ln = int(rec["offset"]), int(rec["length"])
    r = requests.get(DATA + rec["filename"], headers={**UA, "Range": f"bytes={off}-{off + ln - 1}"}, timeout=180)
    r.raise_for_status()
    raw = gzip.GzipFile(fileobj=io.BytesIO(r.content)).read()
    return raw.split(b"\r\n\r\n", 2)[-1].decode("utf-8", "ignore")


def summarize(rows):
    ok = [r for r in rows if r.get("status") == "200"]
    ids = {m.group(1) for r in ok for m in [re.search(r"/rooms/(\d+)", r["url"])] if m}
    lens = sorted(int(r["length"]) for r in ok)
    return dict(rows=len(rows), status=dict(collections.Counter(r.get("status") for r in rows)), unique_ids=len(ids),
                median_len=lens[len(lens) // 2] if lens else None,
                with_check_in=sum("check_in" in r["url"] for r in ok),
                dates=(min(r["timestamp"] for r in ok)[:8], max(r["timestamp"] for r in ok)[:8]) if ok else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crawl", default="CC-MAIN-2026-30")
    ap.add_argument("--fetch", type=int, default=1, help="number of full records to fetch and inspect")
    a = ap.parse_args()
    rows = index_rows(a.crawl)
    print(json.dumps(summarize(rows), indent=1))
    full = [r for r in rows if r.get("status") == "200" and int(r["length"]) > 60000]
    for rec in full[: a.fetch]:
        html = fetch_html(rec)
        print("\n", rec["url"][:120], "| capture", rec["timestamp"][:8], "| html bytes", len(html))
        for name, pat in FIELDS.items():
            ms = re.findall(pat, html)
            print(f"  {name:24s} hits={len(ms):3d} {ms[0] if ms else ''}")


if __name__ == "__main__":
    sys.exit(main())
