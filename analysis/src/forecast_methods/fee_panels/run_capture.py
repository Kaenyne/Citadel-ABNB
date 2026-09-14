"""A3 (2/2): capture listed vs total price for the frozen fee-deadline sample.

One run = one pass over data/processed/forecast_methods/fee_panels/sample_ids.csv,
quoting the SAME listings for the SAME fixed stay dates every time, so any movement in
the series is price, not question. Output: one CSV per run under
data/processed/forecast_methods/fee_panels/runs/capture_<YYYY-MM-DD>_<HHMM>.csv

Two capture modes (see docs/revenue-forecast-strategy/05_backtests/A3_fee_panels.md)
  --mode pdp     the frozen sample_ids.csv listings, one public listing page per quote.
                 VERIFIED BROKEN 2026-09-11: the page returns HTTP 200 but the booking
                 panel is rendered client-side (structuredDisplayPrice is null) and the
                 check_in/checkout URL parameters are ignored for an anonymous session --
                 confirmed in a real logged-out Chrome session, which showed "Add your
                 travel dates for exact pricing". Kept because it is the only route that
                 can price a PRE-SPECIFIED listing, so it must be re-tested each run.
  --mode search  the public search results page for a fixed city x fixed dates x fixed
                 cursor pages. This DOES server-render prices: per-card listing id,
                 "N nights x $X" line, discounted vs original total, and host-added fees
                 such as a resort fee. It carries no cleaning-fee, no Airbnb-service-fee
                 and no tax line, so it yields the LISTED price, not the all-in total.
                 Listings are whatever search ranks that day, so the panel is the
                 intersection across runs, not a pre-frozen list.

Scheduling
  Runs at 09:00 local on 14, 16, 18 Sep and 12, 14, 16 Oct 2026 (two before / one after
  each deadline). launchd cannot express six specific calendar dates without six
  StartCalendarInterval entries that would also fire in every later year, so the plist
  fires DAILY at 09:00 and this script exits 0 immediately unless today is one of the
  six -- the date guard lives here, in version control, not in the plist.
  Override with --force (manual re-run) or --date YYYY-MM-DD (backfill a missed slot).

Politeness
  One worker, one request at a time, --delay seconds between requests (default 2.0),
  exponential backoff on 429/5xx, descriptive User-Agent with a contact address. Only
  public listing pages are requested -- no login, no internal API, no key reuse.

Run
  python analysis/src/forecast_methods/fee_panels/run_capture.py                  # scheduled
  python analysis/src/forecast_methods/fee_panels/run_capture.py --force --city new-orleans \
      --limit 30 --out data/processed/forecast_methods/fee_panels/dryrun_new-orleans_2026-09-11.csv
"""
import argparse
import csv
import datetime as dt
import gzip
import html as H
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
BASE = os.path.join(ROOT, "data", "processed", "forecast_methods", "fee_panels")
SAMPLE = os.path.join(BASE, "sample_ids.csv")
RUNS = os.path.join(BASE, "runs")

# The six capture dates. Two observations before each deadline and one after, so the
# pre-trend and the jump are both estimable within each cohort's own window.
CAPTURE_DATES = {"2026-09-14", "2026-09-16", "2026-09-18",   # around 15 Sep, non-EEA
                 "2026-10-12", "2026-10-14", "2026-10-16"}   # around 13 Oct, EEA + CH

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/128.0.0.0 Safari/537.36 (academic research; UF student pitch project; "
      "contact theobmachado@gmail.com)")

FIELDS = ["listing_id", "city", "country", "eea_flag", "checkin", "checkout", "nights",
          "nightly_price", "cleaning_fee", "service_fee", "taxes", "total", "currency",
          "captured_at", "parse_status", "http_status", "bytes", "stay_window",
          "room_type", "bedroom_bucket", "host_class", "notes"]

# Keys Airbnb's PDP payload uses for the price block. Kept as a list because the front
# end renames them; an empty hit on ALL of them is the signal that the parser, not the
# market, has changed -- which is exactly the failure mode that silently corrupted the
# earlier discount series (research note: a scrape change confounded it).
PRICE_KEYS = ["structuredDisplayPrice", "priceBreakdown", "explanationData", "priceItems",
              "displayPrice", "secondaryLine", "primaryLine", "discountedPrice",
              "totalPrice", "pricingQuote", "bookItSidebar"]
FEE_LABELS = {
    "cleaning_fee": ("cleaning fee", "cleaning"),
    "service_fee": ("airbnb service fee", "service fee"),
    "taxes": ("taxes", "tax", "occupancy tax"),
}
CUR = {"$": "USD", "£": "GBP", "€": "EUR", "A$": "AUD", "MX$": "MXN"}


def log(m):
    print(f"{dt.datetime.now():%H:%M:%S} {m}", flush=True)


def fetch(listing_id, checkin, checkout, adults, timeout=45, tries=3):
    """GET the public listing page for a specific stay. Returns (status, html, err)."""
    qs = urllib.parse.urlencode({"check_in": checkin, "check_out": checkout,
                                 "adults": adults, "guests": adults})
    url = f"https://www.airbnb.com/rooms/{listing_id}?{qs}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip",
    })
    for a in range(tries):
        try:
            r = urllib.request.urlopen(req, timeout=timeout)
            b = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                b = gzip.decompress(b)
            return r.status, b.decode("utf-8", "replace"), None
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and a < tries - 1:
                time.sleep(8 * (a + 1) + random.random() * 4)
                continue
            return e.code, "", f"HTTPError {e.code}"
        except Exception as e:                                   # noqa: BLE001
            if a < tries - 1:
                time.sleep(4 * (a + 1))
                continue
            return None, "", f"{type(e).__name__}: {e}"
    return None, "", "exhausted"


def deferred_blobs(html):
    out = []
    for m in re.finditer(r'<script[^>]*id="data-deferred-state[^"]*"[^>]*>(.*?)</script>',
                         html, re.S):
        try:
            out.append(json.loads(H.unescape(m.group(1))))
        except Exception:                                        # noqa: BLE001
            pass
    return out


def walk(node, want, hits, depth=0):
    """Collect every value stored under any key in `want`."""
    if depth > 40:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            if k in want and v is not None:
                hits.setdefault(k, []).append(v)
            walk(v, want, hits, depth + 1)
    elif isinstance(node, list):
        for v in node:
            walk(v, want, hits, depth + 1)


def money(s):
    """'$1,234.56' -> (1234.56, 'USD')."""
    if not isinstance(s, str):
        return None, None
    m = re.search(r"(A\$|MX\$|[$£€])\s?([\d,]+(?:\.\d{1,2})?)", s)
    if not m:
        m2 = re.search(r"([\d,]+(?:\.\d{1,2})?)", s)
        return (float(m2.group(1).replace(",", "")), None) if m2 else (None, None)
    return float(m.group(2).replace(",", "")), CUR.get(m.group(1))


def parse(html, nights):
    """Pull the price block out of the page. Returns dict of fields + parse_status."""
    r = {k: None for k in ("nightly_price", "cleaning_fee", "service_fee", "taxes",
                           "total", "currency")}
    if not html:
        return r, "empty_body", ""

    blobs = deferred_blobs(html)
    if not blobs:
        return r, "no_deferred_state", "page returned but no data-deferred-state script"

    hits = {}
    for b in blobs:
        walk(b, set(PRICE_KEYS), hits)

    # The booking sidebar is loaded client-side; when it has not been rendered the
    # section is present but empty. Distinguish that from a real parse failure.
    sdp = hits.get("structuredDisplayPrice") or []
    rendered = any(v not in (None, {}, []) for v in sdp)
    not_complete = '"sectionId":"BOOK_IT_SIDEBAR"' in html and not rendered

    # price strings, wherever they live
    texts = []
    for k in ("explanationData", "priceItems", "secondaryLine", "primaryLine",
              "structuredDisplayPrice", "priceBreakdown"):
        for v in hits.get(k, []):
            texts.append(json.dumps(v) if not isinstance(v, str) else v)
    joined = " ".join(texts)

    if joined:
        for field, labels in FEE_LABELS.items():
            for lab in labels:
                m = re.search(re.escape(lab) + r'"[^}]{0,120}?"(?:price_string|priceString|'
                              r'localizedTitle|value)"\s*:\s*"([^"]+)"', joined, re.I)
                if m:
                    r[field], cur = money(m.group(1))
                    r["currency"] = r["currency"] or cur
                    break
        mt = re.search(r'"(?:total|Total)[^"]{0,20}"[^}]{0,200}?"([^"]*[\d][^"]*)"', joined)
        if mt:
            r["total"], cur = money(mt.group(1))
            r["currency"] = r["currency"] or cur

    if r["total"] is None and r["nightly_price"] is None and not_complete:
        return r, "price_not_server_rendered", (
            "BOOK_IT_SIDEBAR present, structuredDisplayPrice null -- price is fetched "
            "client-side after page load; server HTML carries no quote")
    if r["total"] is None and r["nightly_price"] is None:
        if re.search(r"unavailable|not available|Dates unavailable", html, re.I):
            return r, "dates_unavailable", ""
        return r, "no_price_found", "deferred state parsed but no price keys matched"

    if r["nightly_price"] is None and r["total"] is not None and nights:
        base = r["total"] - sum(v for v in (r["cleaning_fee"], r["service_fee"], r["taxes"])
                                if v is not None)
        r["nightly_price"] = round(base / nights, 2)
    status = "ok" if (r["total"] is not None and r["nightly_price"] is not None) else "partial"
    return r, status, ""


def load_sample(path, city=None, limit=None, window=None):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if city:
        rows = [r for r in rows if r["city"] == city]
    if window:
        rows = [r for r in rows if r["stay_window"] == window]
    if limit:
        # keep both stay windows for the same listings when limiting
        ids, keep = [], []
        for r in rows:
            if r["listing_id"] not in ids:
                if len(ids) >= limit:
                    continue
                ids.append(r["listing_id"])
            keep.append(r)
        rows = keep
    return rows



# ---------------------------------------------------------------- search mode
# Place slugs for the 13 markets, as Airbnb's own /s/<place>/homes URLs spell them.
PLACES = {
    "austin": "Austin--Texas--United-States",
    "chicago": "Chicago--Illinois--United-States",
    "los-angeles": "Los-Angeles--California--United-States",
    "nashville": "Nashville--Tennessee--United-States",
    "new-orleans": "New-Orleans--Louisiana--United-States",
    "new-york-city": "New-York--NY--United-States",
    "san-diego": "San-Diego--California--United-States",
    "london": "London--United-Kingdom",
    "sydney": "Sydney--New-South-Wales--Australia",
    "mexico-city": "Mexico-City--CDMX--Mexico",
    "barcelona": "Barcelona--Catalonia--Spain",
    "paris": "Paris--France",
    "rome": "Rome--Lazio--Italy",
}
PAGE_SIZE = 18   # items per search page, as Airbnb's own pageCursors step

# country + EEA deadline group per market, mirroring MARKETS in build_sample.py
MARKET_GEO = {
    "austin": ("United States", 0), "chicago": ("United States", 0),
    "los-angeles": ("United States", 0), "nashville": ("United States", 0),
    "new-orleans": ("United States", 0), "new-york-city": ("United States", 0),
    "san-diego": ("United States", 0), "london": ("United Kingdom", 0),
    "sydney": ("Australia", 0), "mexico-city": ("Mexico", 0),
    "barcelona": ("Spain", 1), "paris": ("France", 1), "rome": ("Italy", 1),
}


def page_cursor(offset):
    """Airbnb's search cursor is plain base64 of a tiny JSON object; the page publishes
    the whole list of them in paginationInfo.pageCursors. Rebuilding it is arithmetic,
    not reverse engineering."""
    import base64 as _b64
    payload = json.dumps({"section_offset": 0, "items_offset": int(offset), "version": 1},
                         separators=(",", ":"))
    return _b64.b64encode(payload.encode()).decode()


def fetch_search(city, checkin, checkout, adults, offset, timeout=60, tries=3):
    place = PLACES.get(city)
    if not place:
        return None, "", f"no place slug for {city}"
    params = {"checkin": checkin, "checkout": checkout, "adults": adults}
    if offset:
        params["cursor"] = page_cursor(offset)
    url = f"https://www.airbnb.com/s/{place}/homes?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip"})
    for a in range(tries):
        try:
            r = urllib.request.urlopen(req, timeout=timeout)
            b = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                b = gzip.decompress(b)
            return r.status, b.decode("utf-8", "replace"), None
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and a < tries - 1:
                time.sleep(10 * (a + 1) + random.random() * 5)
                continue
            return e.code, "", f"HTTPError {e.code}"
        except Exception as e:                                   # noqa: BLE001
            if a < tries - 1:
                time.sleep(5 * (a + 1))
                continue
            return None, "", f"{type(e).__name__}: {e}"
    return None, "", "exhausted"


def _cards(blob, out, depth=0):
    if depth > 60:
        return
    if isinstance(blob, dict):
        if blob.get("structuredDisplayPrice"):
            out.append(blob)
        for v in blob.values():
            _cards(v, out, depth + 1)
    elif isinstance(blob, list):
        for v in blob:
            _cards(v, out, depth + 1)


def parse_search(html, nights):
    """One dict per listing card. The fee fields stay None on purpose: search publishes
    the listed price and host-added fees, never the Airbnb service fee or taxes."""
    import base64 as _b64
    rows, seen = [], set()
    cards = []
    for b in deferred_blobs(html):
        _cards(b, cards)
    for c in cards:
        enc = (c.get("demandStayListing") or {}).get("id")
        lid = None
        if enc:
            try:
                lid = _b64.b64decode(enc).decode().split(":")[-1]
            except Exception:                                    # noqa: BLE001
                pass
        if not lid or lid in seen:
            continue
        seen.add(lid)
        sdp = c["structuredDisplayPrice"]
        prim = sdp.get("primaryLine") or {}
        total, cur = money(prim.get("discountedPrice") or prim.get("price"))
        orig, _ = money(prim.get("originalPrice"))
        nightly = cleaning = taxes = None
        stay_subtotal = after_discount = None
        host_fees, items = 0.0, []
        for g in ((sdp.get("explanationData") or {}).get("priceDetails") or []):
            for it in (g.get("items") or []):
                d = (it.get("description") or "")
                amt, c2 = money(it.get("priceString"))
                cur = cur or c2
                items.append(f"{d}={it.get('priceString')}")
                dl = d.lower()
                m = re.match(r"(\d+)\s+nights?\s*x\s*(.+)", d, re.I)
                if m:
                    nightly, c3 = money(m.group(2))
                    cur = cur or c3
                    stay_subtotal = amt
                elif "cleaning" in dl:
                    cleaning = amt
                elif "tax" in dl:
                    taxes = amt
                elif "price after discount" in dl:
                    after_discount = amt
                elif "discount" in dl or "special offer" in dl:
                    pass
                elif amt:
                    host_fees += amt
        # primaryLine.discountedPrice is absent on some cards (no rounded headline price).
        # Fall back to the breakdown itself: the post-discount line, else nights x rate.
        if total is None:
            total = after_discount if after_discount is not None else stay_subtotal
        if nightly is None and total and nights:
            nightly = round(total / nights, 2)
        rows.append({
            "listing_id": lid, "nightly_price": nightly, "cleaning_fee": cleaning,
            "service_fee": None, "taxes": taxes, "total": total, "currency": cur,
            "original_total": orig, "host_added_fees": round(host_fees, 2) or None,
            # the card title reads "<listing type> in <neighbourhood>"; the prefix is the
            # only room-type signal search gives. The authoritative room_type comes from
            # joining listing_id to the Inside Airbnb dump (93% hit rate in the dry run).
            "room_type": (c.get("title") or "").split(" in ")[0] or None,
            "title": c.get("title"), "line_items": " | ".join(items)[:400],
            "parse_status": "ok" if (total is not None and nightly is not None) else "partial",
        })
    return rows


def run_search(a, today, out):
    """Harvest fixed cursor pages of the public search results for each city x stay."""
    stays = [("W1", "2026-11-13", "2026-11-16"), ("W2", "2026-12-11", "2026-12-14")]
    if a.window:
        stays = [s for s in stays if s[0] == a.window]
    cities = [a.city] if a.city else list(PLACES)
    target = a.limit or 10 ** 9
    fields = FIELDS + ["original_total", "host_added_fees", "search_offset", "title",
                       "line_items"]
    counts, n = {}, 0
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for city in cities:
            for win, ci, co in stays:
                got = set()
                for off in range(0, a.pages * PAGE_SIZE, PAGE_SIZE):
                    if len(got) >= target:
                        break
                    st, html, err = fetch_search(city, ci, co, a.adults, off)
                    if st != 200:
                        counts[f"http_{st}"] = counts.get(f"http_{st}", 0) + 1
                        log(f"  {city} {win} offset {off}: {err}")
                        time.sleep(a.delay * 2)
                        continue
                    rows = parse_search(html, 3)
                    if not rows:
                        counts["no_cards"] = counts.get("no_cards", 0) + 1
                    for r in rows:
                        if r["listing_id"] in got or len(got) >= target:
                            continue
                        got.add(r["listing_id"])
                        counts[r["parse_status"]] = counts.get(r["parse_status"], 0) + 1
                        n += 1
                        geo = MARKET_GEO.get(city, ("", ""))
                        w.writerow({
                            "city": city, "country": geo[0], "eea_flag": geo[1],
                            "checkin": ci, "checkout": co, "nights": 3,
                            "captured_at": dt.datetime.now(dt.timezone.utc)
                                             .isoformat(timespec="seconds"),
                            "http_status": st, "bytes": len(html), "stay_window": win,
                            "search_offset": off, "bedroom_bucket": "", "host_class": "",
                            "notes": "", **r})
                    fh.flush()
                    time.sleep(a.delay + random.random() * 0.5)
                log(f"  {city} {win}: {len(got)} listings")
    ok = counts.get("ok", 0)
    log(f"done {n} rows | priced {ok} ({100.0*ok/max(n,1):.1f}%) | {counts}")
    log(f"wrote {out}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=SAMPLE)
    ap.add_argument("--out", default=None)
    ap.add_argument("--city", default=None)
    ap.add_argument("--window", default=None, help="W1 or W2")
    ap.add_argument("--limit", type=int, default=None, help="max listings (both windows kept)")
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--force", action="store_true", help="skip the capture-date guard")
    ap.add_argument("--date", default=None, help="treat this as today (backfill)")
    ap.add_argument("--mode", default="search", choices=["search", "pdp"],
                    help="search = public search results (works); pdp = frozen sample_ids "
                         "via listing pages (verified broken 2026-09-11, re-test each run)")
    ap.add_argument("--pages", type=int, default=15, help="search pages per city x stay")
    ap.add_argument("--adults", type=int, default=2)
    a = ap.parse_args()

    today = a.date or dt.date.today().isoformat()
    if not a.force and today not in CAPTURE_DATES:
        log(f"{today} is not a capture date ({sorted(CAPTURE_DATES)}) -- exiting 0")
        return 0

    if a.mode == "search":
        out = a.out or os.path.join(RUNS, f"capture_search_{today}_{dt.datetime.now():%H%M}.csv")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        log(f"search capture -> {out}")
        return run_search(a, today, out)

    if not os.path.exists(a.sample):
        log(f"missing sample {a.sample}")
        return 2
    rows = load_sample(a.sample, a.city, a.limit, a.window)
    if not rows:
        log("no rows selected")
        return 2

    out = a.out or os.path.join(RUNS, f"capture_{today}_{dt.datetime.now():%H%M}.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    log(f"capturing {len(rows)} quotes ({len({r['listing_id'] for r in rows})} listings) "
        f"-> {out}")

    counts, t0 = {}, time.time()
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            st, html, err = fetch(r["listing_id"], r["checkin"], r["checkout"],
                                  r.get("adults", 2))
            nights = int(float(r.get("nights") or 3))
            if st == 200:
                vals, status, note = parse(html, nights)
            else:
                vals = {k: None for k in ("nightly_price", "cleaning_fee", "service_fee",
                                          "taxes", "total", "currency")}
                status, note = (f"http_{st}" if st else "fetch_error"), (err or "")
            counts[status] = counts.get(status, 0) + 1
            w.writerow({
                "listing_id": r["listing_id"], "city": r["city"], "country": r["country"],
                "eea_flag": r["eea_flag"], "checkin": r["checkin"], "checkout": r["checkout"],
                "nights": nights, **vals,
                "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "parse_status": status, "http_status": st, "bytes": len(html),
                "stay_window": r.get("stay_window"), "room_type": r.get("room_type"),
                "bedroom_bucket": r.get("bedroom_bucket"), "host_class": r.get("host_class"),
                "notes": note,
            })
            fh.flush()
            if i % 10 == 0 or i == len(rows):
                log(f"  {i}/{len(rows)}  {counts}")
            time.sleep(a.delay + random.random() * 0.5)

    ok = counts.get("ok", 0) + counts.get("partial", 0)
    log(f"done {len(rows)} rows in {time.time()-t0:.0f}s | priced {ok} "
        f"({100.0*ok/len(rows):.1f}%) | {counts}")
    log(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
