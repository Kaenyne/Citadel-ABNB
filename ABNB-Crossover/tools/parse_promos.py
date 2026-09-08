"""Parse archived kay.com / zales.com homepage captures into a promo-intensity panel.

Reads <banner>_<timestamp>.html from this directory (Wayback) and ./cc/ (Common Crawl),
emits ../promo_intensity.csv plus coverage.csv.

TEMPLATE PROBLEM AND HOW IT IS HANDLED
--------------------------------------
Kay/Zales re-skinned the homepage repeatedly over the window, so no single DOM hook survives:

  era A (through ~Mar 2025)  no "Skip to Offers" skip-link; promo copy sits in the
                             "SALE & CLEARANCE > Featured Deals" nav block
  era B (~Apr 2025-Apr 2026) "Skip to Offers" skip-link introduced; hero promo strip at
                             the very top of the linearized text
  era C (~May-Jul 2026)      skip-link removed in the Q3 FY27 redesign; promo copy
                             immediately follows <title>
  era D (~Aug 2026)          skip-link restored

Anchoring on any one of these silently returns 0% for the other eras - which would
manufacture a fake "promotional discipline" trend exactly where the thesis wants one.
So the parser extracts TWO regions that exist in every era and reports both:

  1. FEATURED-DEALS BLOCK - the promoted-offer list in the Sale & Clearance nav.
     Present in every era; the backbone of the y/y comparison.
  2. HERO STRIP - the top promo carousel (skip-link anchored where available,
     otherwise the text immediately after <title>).

METRICS
-------
`promo_depth`  deepest % anywhere in either region, permanent store furniture included.
               Retained for transparency; it saturates near 50 and barely moves.
`event_depth`  PRIMARY. Deepest TIME-LIMITED promotional offer, with evergreen furniture
               stripped (see EVERGREEN FURNITURE below). This is the series that moves.
`sitewide_pct` the rate attached to "Everything" (Kay) / "Storewide" (Zales) - depth and
               breadth in one number, and the sharpest test of a "broader promotions" pivot.

Captures lacking the promoted-offer nav block are flagged non-comparable and excluded rather
than zero-filled: a spurious zero would manufacture exactly the promotional-discipline
signal the thesis wants to find.
"""
import csv, glob, html, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "promo_intensity.csv")
COVER = os.path.join(HERE, "coverage.csv")

MIN_TEXT = 2000          # below this the capture is a fragment, not a rendered homepage
JS_SHELL = 400           # below this it is a JS shell / failed capture

# INCLUSION RULE for the y/y panel: the capture must contain the promoted-offer nav block
# ("Featured Deals" on Kay, "Top Deals" on Zales). That block is the one region present in
# every template era and on both banners, so requiring it makes observations comparable.
# Hero-only partial captures are recorded in coverage.csv but excluded from the panel: they
# see a strictly smaller slice of the page, so mixing them in would bias depth downward.

TAG_STRIP = re.compile(r"<(script|style|noscript|svg|template)\b[^>]*>.*?</\1>", re.I | re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)
TAG = re.compile(r"<[^>]+>")

# ---- promo regexes -------------------------------------------------------
RE_PCT = re.compile(r"(\d{1,2})\s*%\s*(?:\*\s*)?off", re.I)
RE_UPTO = re.compile(r"up\s+to\s+(?:an\s+)?(\d{1,2})\s*%", re.I)
RE_SAVE = re.compile(r"sav(?:e|ings?)\s+(?:up\s+to\s+)?(\d{1,2})\s*%", re.I)
RE_EXTRA = re.compile(r"extra\s+(?:up\s+to\s+)?(\d{1,2})\s*%", re.I)
# Kay's markup sometimes drops the '%' glyph outright (observed verbatim 2026-01-24:
# '<span ...>30 Off* Select Diamond Jewelry</span>'). Applied only inside the promo
# regions, and never after a currency symbol, so '$30 off' cannot become a percentage.
RE_BARE_OFF = re.compile(r"(?<![$\d.])\b(\d{1,2})\s+off\b", re.I)

# The rate attached to the whole store == depth x breadth in one number.
# Kay says "Everything"; Zales says "Storewide".
RE_SITEWIDE_PCT = re.compile(
    r"(\d{1,2})\s*%\s*off\W{0,6}(?:almost\s+|select\s+)?"
    r"(?:everything|storewide|store\s*wide|site\s*wide)", re.I)

# ---- EVERGREEN FURNITURE -------------------------------------------------
# The promoted-offer nav block mixes genuine time-limited PROMOTIONAL EVENTS with permanent
# store furniture. The furniture never changes, so leaving it in pins the series at a
# constant (~50) and destroys every y/y comparison. Three kinds are excluded:
#
#   1. "50% Off & Up"        - a clearance FLOOR ("50% off and higher"), not an offer
#   2. Military / Pre-Owned / Outlet - standing programmes, always present
#   3. "Up to 50% Off Clearance"     - the permanent clearance department...
#      ...but NOT "Extra 20% Off Select Clearance", which is a genuine incremental
#      markdown event. The presence of "extra" is what separates the two.
RE_AND_UP = re.compile(r"^\W{0,3}(?:&|and)\s*up\b", re.I)
RE_EVERGREEN_CTX = re.compile(r"military\s+discount|pre-?owned|\boutlet\b", re.I)
RE_ANY_PCT = re.compile(r"\d{1,2}\s*%")

RE_CODE = re.compile(r"(?:promo(?:tion)?\s*code|use\s+code|code[:\s]{1,3})\s*[\"']?([A-Z0-9]{3,12})\b")
RE_BOGO = re.compile(r"buy\s+one\s*,?\s*get\s+one|\bbogo\b|second\s+item|2nd\s+item", re.I)
RE_GIFT = re.compile(r"free\s+gift|gift\s+with\s+purchase|\bgwp\b|bonus\s+gift", re.I)
RE_FIN = re.compile(r"(\d{1,2})\s*months?\s+(?:special\s+)?financing|0%\s*apr|no\s+interest\s+if", re.I)
RE_CLEAR = re.compile(r"clearance", re.I)
RE_SALE = re.compile(r"\bsale\b", re.I)
RE_DOORB = re.compile(r"door\s*buster|doorbuster|black\s+friday|cyber\s+(?:week|monday)", re.I)
RE_SITEWIDE = re.compile(r"site\s*wide|store\s*wide|entire\s+(?:site|store)|\beverything\b", re.I)
NOISE_CTX = re.compile(r"(off\s+the\s+shoulder|100\s*%\s*off)", re.I)

# region anchors
OFFERS_START = re.compile(r"Skip to Offers", re.I)
OFFERS_END = re.compile(r"Select Your Store|What can we help you find|\bCancel\s+Sign In\b|"
                        r"This Action will open drawer|Skip to Navigation", re.I)
NAV_BOILER = re.compile(r"Skip to (Content|Navigation|Offers)\s*", re.I)
# Kay labels the promoted-offer nav block "Featured Deals"; Zales labels it "Top Deals".
RE_FEATURED = re.compile(r"(Featured Deals|Top Deals)(?:\s+\1)?", re.I)
# Structural boundaries only. "Military Discount", "New Markdowns" and "Deeper Discounts"
# were previously in this list but they are DEAL ITEMS, not boundaries - when one led the
# block it truncated the region to the empty string and silently dropped the capture
# (this removed all of Oct-2025 Kay, a month inside the Q3 FY26 test window).
FEATURED_END = re.compile(r"Shop All Sale|Shop All Clearance|Kay Outlet|Zales Outlet|"
                          r"Gift Card|View All Offers|View All Clearance", re.I)
HERO_HINTS = [
    re.compile(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']{10,400})', re.I),
    re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']{10,400})', re.I),
]


def visible_text(raw):
    s = COMMENT.sub(" ", raw)
    s = TAG_STRIP.sub(" ", s)
    s = TAG.sub(" ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def all_pcts(text, bare_ok=False, drop_evergreen=False):
    """Percentages in `text`. With drop_evergreen, permanent store furniture is excluded
    so that what remains is time-limited promotional-event depth."""
    vals = []
    rxs = (RE_PCT, RE_UPTO, RE_SAVE, RE_EXTRA) + ((RE_BARE_OFF,) if bare_ok else ())
    for rx in rxs:
        for m in rx.finditer(text):
            v = int(m.group(1))
            if not (5 <= v <= 80):      # the band real jewelry offers occupy
                continue
            before, after = text[max(0, m.start() - 45):m.start()], text[m.end():m.end() + 45]
            if NOISE_CTX.search(before + text[m.start():m.end()] + after):
                continue
            if RE_AND_UP.match(after):                      # clearance floor
                continue
            if drop_evergreen:
                # Scope the test to THIS offer's phrase: forward to the next percentage
                # (where the next offer begins) and back to the previous one. Several of the
                # regexes match the same offer at different spans ("Up to 50%" vs "50% Off"),
                # so testing a raw character window filtered one span but not the other.
                nxt = RE_ANY_PCT.search(after)
                scope_fwd = after[:nxt.start()] if nxt else after
                prv = list(RE_ANY_PCT.finditer(before))
                scope_back = before[prv[-1].end():] if prv else before
                if RE_EVERGREEN_CTX.search(scope_fwd + " " + scope_back):
                    continue
                # the standing clearance department, unless this is an "extra N% off" event
                if re.search(r"\bclearance\b", scope_fwd, re.I) and not \
                        re.search(r"\bextra\b", scope_back, re.I):
                    continue
            vals.append(v)
    return vals


def hero_block(txt, title=""):
    """Top promo carousel: skip-link anchored where present, else the post-<title> text."""
    m = OFFERS_START.search(txt)
    seg = txt[m.end():] if m else txt[:1200]
    e = OFFERS_END.search(seg)
    if e:
        seg = seg[:e.start()]
    seg = NAV_BOILER.sub("", seg).strip()
    if title and seg.startswith(title):
        seg = seg[len(title):].strip(" |-")
    return seg[:1200]


def featured_block(txt):
    """The 'Featured Deals' promoted-offer list - the one region present in every era."""
    m = RE_FEATURED.search(txt)
    if not m:
        return ""
    seg = txt[m.end():m.end() + 500]
    e = FEATURED_END.search(seg)
    if e:
        seg = seg[:e.start()]
    return seg.strip()


def era(txt, ts, has_fd):
    """Which site template this capture came from.

    '0_legacy' is the pre-Aug-2024 skin: no Featured-Deals block and no skip-link, with an
    editorial hero ('Perfect Presents for Every Love - SHOP NOW') and percentages scattered
    through unrelated page furniture. Neither canonical promo region exists, so these
    captures are marked comparable=0 and excluded from the y/y analysis rather than
    zero-filled - a zero here would be a measurement artifact, not promotional restraint.
    """
    if OFFERS_START.search(txt):
        return "D_anchor" if ts >= "20260701" else "B_anchor"
    if not has_fd:
        return "0_legacy"
    return "C_redesign" if ts >= "20260401" else "A_featured"


def promo_type(txt, depth, region):
    t = []
    if RE_DOORB.search(region):
        t.append("holiday_event")
    if depth >= 50:
        t.append("deep_pct")
    elif depth > 0:
        t.append("pct_off")
    if RE_SITEWIDE.search(region) and depth:
        t.append("sitewide")
    if RE_CLEAR.search(region):
        t.append("clearance")
    if RE_BOGO.search(txt):
        t.append("bogo")
    if RE_GIFT.search(txt):
        t.append("free_gift")
    if RE_FIN.search(txt):
        t.append("financing")
    if not t:
        t.append("sale_generic" if RE_SALE.search(region) else "no_offer")
    return "|".join(dict.fromkeys(t))


def parse_file(path, source=None):
    banner, ts = os.path.basename(path)[:-5].split("_")
    if source is None:
        source = "commoncrawl" if os.sep + "cc" + os.sep in path else "wayback"
    raw = open(path, encoding="utf-8", errors="ignore").read()
    txt = visible_text(raw)
    base = dict(banner=banner, timestamp=ts, source=source, text_len=len(txt), bytes=len(raw))
    if len(txt) < JS_SHELL:
        return None, dict(base, status="js_shell")
    if len(txt) < MIN_TEXT:
        return None, dict(base, status="partial_capture")

    tm = re.search(r"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
    title = re.sub(r"\s+", " ", html.unescape(TAG.sub("", tm.group(1)))).strip() if tm else ""
    hb = hero_block(txt, title)
    fb = featured_block(txt)
    fd_found = bool(RE_FEATURED.search(txt))   # block located, even if it extracted empty
    region = (hb + " || " + fb).strip()

    hero_p = all_pcts(hb, bare_ok=True)
    deal_p = all_pcts(fb, bare_ok=True)
    # event_* strips permanent store furniture; this is the metric that actually moves
    hero_e = all_pcts(hb, bare_ok=True, drop_evergreen=True)
    deal_e = all_pcts(fb, bare_ok=True, drop_evergreen=True)
    event_p = hero_e + deal_e
    depth = max(hero_p + deal_p) if (hero_p or deal_p) else 0
    event_depth = max(event_p) if event_p else 0
    sw = [int(x) for x in RE_SITEWIDE_PCT.findall(region)]
    code = RE_CODE.search(txt)
    fin = RE_FIN.search(txt)

    row = dict(
        date=f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}",
        banner=banner,
        max_pct_off=depth,
        headline_promo_text=re.sub(r"[\r\n,]+", " ", (hb or fb))[:180],
        promo_type=promo_type(txt, depth, region),
        promo_depth=depth,
        event_depth=event_depth,
        n_event_offers=len(set(event_p)),
        event_offers=";".join(str(v) for v in sorted(set(event_p), reverse=True)[:8]),
        hero_max_pct_off=max(hero_p) if hero_p else 0,
        deals_max_pct_off=max(deal_p) if deal_p else 0,
        sitewide_pct=max(sw) if sw else 0,
        n_pct_offers=len(set(hero_p + deal_p)),
        pct_offers=";".join(str(v) for v in sorted(set(hero_p + deal_p), reverse=True)[:8]),
        deals_text=re.sub(r"[\r\n,]+", " ", fb)[:180],
        promo_code=code.group(1) if code else "",
        free_gift=int(bool(RE_GIFT.search(txt))),
        bogo=int(bool(RE_BOGO.search(txt))),
        financing_months=int(fin.group(1)) if (fin and fin.group(1)) else "",
        clearance_mentions=len(RE_CLEAR.findall(txt)),
        sitewide=int(bool(RE_SITEWIDE.search(region))),
        era=era(txt, ts, fd_found),
        # comparable == the promoted-offer nav block was located (see INCLUSION RULE above)
        comparable=int(fd_found),
        timestamp=ts,
        source=source,
        snapshot_url=(f"https://web.archive.org/web/{ts}/https://www.{banner}.com/"
                      if source == "wayback" else f"commoncrawl:{banner}.com@{ts}"),
        text_len=len(txt),
    )
    return row, dict(base, status="parsed")


def main():
    rows, cov = [], []
    paths = (sorted(glob.glob(os.path.join(HERE, "*_2*.html")))
             + sorted(glob.glob(os.path.join(HERE, "cc", "*_2*.html"))))
    for p in paths:
        try:
            r, c = parse_file(p)
        except Exception as e:
            b, ts = os.path.basename(p)[:-5].split("_")
            r, c = None, dict(banner=b, timestamp=ts,
                              source="commoncrawl" if os.sep + "cc" + os.sep in p else "wayback",
                              status=f"parse_err_{type(e).__name__}", text_len=0, bytes=0)
        cov.append(c)
        if r:
            rows.append(r)

    # one observation per banner-day; prefer the richer capture
    best = {}
    for r in rows:
        k = (r["banner"], r["date"])
        if k not in best or r["text_len"] > best[k]["text_len"]:
            best[k] = r
    rows = sorted(best.values(), key=lambda r: (r["banner"], r["timestamp"]))

    if rows:
        with open(OUT, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    with open(COVER, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["banner", "timestamp", "source", "status",
                                          "text_len", "bytes"])
        w.writeheader()
        w.writerows(sorted(cov, key=lambda c: (c["banner"], c["timestamp"])))
    print("panel rows:", len(rows), "from", len(cov), "files")
    print("file status:", dict(Counter(c["status"] for c in cov)))
    print("by banner:  ", dict(Counter(r["banner"] for r in rows)))
    print("by source:  ", dict(Counter(r["source"] for r in rows)))
    print("by era:     ", dict(Counter(r["era"] for r in rows)))
    comp = [r for r in rows if r["comparable"]]
    print(f"comparable: {len(comp)} of {len(rows)} "
          f"({dict(Counter(r['banner'] for r in comp))})")


if __name__ == "__main__":
    main()
