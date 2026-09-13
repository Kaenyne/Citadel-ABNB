"""Fetch one Wayback capture per quarter (nearest to quarter-end, on or before) for archived third-party pages.
Run: python analysis/src/margin_build/04_alt_signals/pull_wayback.py --pull [page_key ...]"""
import sys, json, pathlib, hashlib, datetime as dt, time, urllib.request, csv
ROOT = pathlib.Path(__file__).resolve().parents[4]
RAW = ROOT / "data/raw/margin_build/04_alt_signals/wayback"
PAGES = {  # key: (cdx json filename, url pattern)
 "careers_home": "cdx_careers_airbnb_com_.json",
 "careers_positions": "cdx_careers_airbnb_com_positions_.json",
 "linkedin": "cdx_www_linkedin_com_company_airbnb.json",
 "glassdoor": "cdx_www_glassdoor_com_Overview_Working-at-Airbnb-EI_IE391850_11_17_htm.json",
 "appstore": "cdx_apps_apple_com_us_app_airbnb_id401626263.json",
 "trustpilot": "cdx_trustpilot.json",
 "playstore": "cdx_playstore.json",
 "bbb": "cdx_bbb.json",
 "sitejabber": "cdx_sitejabber.json",
 "downdetector": "cdx_downdetector.json",
 "layoffs": "cdx_layoffs.json",
}
UA = "citadel-abnb research ksurapaneni@ufl.edu"
def quarter_ends(start=2019, end=2026):
    out = []
    for y in range(start, end + 1):
        for m, d in ((3, 31), (6, 30), (9, 30), (12, 31)):
            q = dt.datetime(y, m, d, 23, 59, 59)
            if q <= dt.datetime.now(): out.append(q)
    return out
def pick(caps, qe):
    # nearest capture within +-45 days, prefer on/before quarter end
    best = None
    for ts in caps:
        t = dt.datetime.strptime(ts, "%Y%m%d%H%M%S")
        delta = (qe - t).total_seconds() / 86400
        if -45 <= delta <= 45:
            score = abs(delta) + (0 if delta >= 0 else 10)
            if best is None or score < best[0]: best = (score, ts)
    return best[1] if best else None
def main(pull, keys):
    rows = []
    for key in keys:
        cdxf = RAW / PAGES[key]
        if not cdxf.exists(): print(key, "no cdx"); continue
        try: d = json.load(open(cdxf))
        except Exception as e: print(key, "cdx parse fail", e); continue
        caps = [r[0] for r in d[1:]]
        urls = {r[0]: r[1] for r in d[1:]}
        outdir = RAW / key; outdir.mkdir(exist_ok=True)
        for qe in quarter_ends():
            ts = pick(caps, qe)
            q = f"{qe.year}Q{(qe.month-1)//3+1}"
            if ts is None: rows.append(dict(page=key, quarter=q, capture_ts="", status="no_capture", file="", sha256="")); continue
            f = outdir / f"{q}_{ts}.html"
            url = f"http://web.archive.org/web/{ts}id_/{urls[ts]}"
            status = "cached"
            if pull and not f.exists():
                for attempt in range(3):
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": UA})
                        data = urllib.request.urlopen(req, timeout=90).read()
                        f.write_bytes(data); status = "pulled"; break
                    except Exception as e:
                        status = f"error:{type(e).__name__}"; time.sleep(3)
                time.sleep(1.0)
            sha = hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else ""
            rows.append(dict(page=key, quarter=q, capture_ts=ts, status=status, file=str(f.relative_to(ROOT)), sha256=sha, url=url,
                             knowable_from=dt.datetime.strptime(ts, "%Y%m%d%H%M%S").date().isoformat()))
            print(key, q, ts, status)
    with open(RAW / "_wayback_manifest.csv", "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["page","quarter","capture_ts","status","file","sha256","url","knowable_from"]); 
        if fh.tell() == 0: w.writeheader()
        w.writerows(rows)
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main("--pull" in sys.argv, args or list(PAGES))
