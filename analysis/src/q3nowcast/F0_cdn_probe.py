"""WS-F step 0: probe data.insideairbnb.com for calendar vintages we do not hold.

Two questions the brief asks:
  (a) does a Sep 2026 calendar dump exist yet for any of the 34 markets on disk?
  (b) are Aug/Sep 2024 calendar files still served for the 13 core cities (they would
      give one year-ago pace comparison, i.e. a 2025-vs-2024 pair to backtest)?

CDN paths come from the acquisition manifest (main tree) so no path table is guessed.
Known 2024/2025 dump dates for the 13 cities come from inside_airbnb_supply_panel.py's
KNOWN_DATES, which was itself built from Wayback captures of the get-the-data page.

HEAD only. Nothing is downloaded here; F0b does any download, into the MAIN tree.

Run: py -3.13 analysis/src/q3nowcast/F0_cdn_probe.py [--workers 12]
"""
import argparse
import concurrent.futures
import csv
import datetime as dt
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[3]
MAIN_TREE = Path(r"C:\Users\krish\citadel-abnb")
MANIFEST = MAIN_TREE / "data/processed/adr/14c_calendar_manifest.csv"
OUT = ROOT / "data/processed/q3nowcast/F"
UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}

# Dump dates seen on the get-the-data page (Wayback) for the 13 cities that carry a
# long listings history. Copied from analysis/src/inside_airbnb_supply_panel.py.
CITY_DATES_2024_25 = {
    "new-york-city": ["2024-07-05", "2024-09-04", "2024-11-04", "2025-01-03", "2025-03-01"],
    "los-angeles": ["2024-06-07", "2024-09-04", "2024-12-06", "2025-03-01"],
    "chicago": ["2024-06-21", "2024-09-17", "2024-12-18", "2025-03-11"],
    "austin": ["2024-06-17", "2024-09-13", "2024-12-14", "2025-03-06"],
    "nashville": ["2024-06-22", "2024-09-18", "2024-12-21", "2025-03-15"],
    "new-orleans": ["2024-06-10", "2024-09-05", "2024-12-08", "2025-03-02"],
    "san-diego": ["2024-06-24", "2024-09-21", "2024-12-23", "2025-03-16"],
    "paris": ["2024-06-10", "2024-09-06", "2024-12-06", "2025-03-03"],
    "london": ["2024-06-14", "2024-09-06", "2024-12-11", "2025-03-04"],
    "barcelona": ["2024-06-15", "2024-09-06", "2024-12-12", "2025-03-05"],
    "rome": ["2024-06-15", "2024-09-11", "2024-12-12", "2025-03-05"],
    "sydney": ["2024-06-10", "2024-09-05", "2024-12-08", "2025-03-03"],
    "mexico-city": ["2024-09-25", "2024-12-27", "2025-03-19"],
}
# Retention is about 12 months, so 2025-06 should be live and 2024-09 probably gone.
# Probing 2025-06 as well tells us whether a null on 2024 is retention or a bad date.


def cdn_paths(manifest_path):
    """market -> CDN prefix, e.g. united-states/tx/austin, taken from the manifest urls."""
    paths = {}
    with Path(manifest_path).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            url = row.get("url") or ""
            if "data.insideairbnb.com/" not in url:
                continue
            tail = url.split("data.insideairbnb.com/", 1)[1]
            prefix = "/".join(tail.split("/")[:3])
            paths.setdefault(row["market"], prefix)
    return paths


def head(sess, url):
    for attempt in range(3):
        try:
            r = sess.head(url, timeout=60, allow_redirects=True)
            if r.status_code in (200, 403, 404):
                return r.status_code, int(r.headers.get("Content-Length") or 0), r.headers.get("Last-Modified")
        except requests.RequestException:
            pass
        time.sleep(2 * (attempt + 1))
    return None, 0, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--today", default="2026-09-11")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    paths = cdn_paths(MANIFEST)
    print(f"{len(paths)} markets with a CDN path in the manifest", flush=True)

    cands = []
    # (a) Sep 2026 dumps for every market on disk: day-by-day probe of 1 Sep to today.
    today = dt.date.fromisoformat(args.today)
    for market, prefix in sorted(paths.items()):
        day = dt.date(2026, 9, 1)
        while day <= today:
            cands.append((market, prefix, day.isoformat(), "sep2026_probe"))
            day += dt.timedelta(days=1)
    # (b) 2024 and early-2025 dumps for the 13 cities with known dump dates.
    for city, dates in CITY_DATES_2024_25.items():
        prefix = paths.get(city)
        if not prefix:
            print(f"no CDN path for {city}; skipped", flush=True)
            continue
        for d in dates:
            cands.append((city, prefix, d, "known_date_2024_25"))
        # Inside Airbnb sometimes shifted a dump by a few days; widen the Sep 2024 window.
        sep24 = [d for d in dates if d.startswith("2024-09")]
        if sep24:
            anchor = dt.date.fromisoformat(sep24[0])
            for delta in range(-14, 15):
                d = (anchor + dt.timedelta(days=delta)).isoformat()
                if d not in dates and d.startswith(("2024-08", "2024-09", "2024-10")):
                    cands.append((city, prefix, d, "sep2024_window"))

    seen, unique = set(), []
    for c in cands:
        key = (c[0], c[2])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    print(f"HEAD-checking {len(unique)} candidate calendar urls", flush=True)

    sess = requests.Session()
    sess.headers.update(UA)

    def work(c):
        market, prefix, date, how = c
        url = f"https://data.insideairbnb.com/{prefix}/{date}/data/calendar.csv.gz"
        st, n, lm = head(sess, url)
        return dict(market=market, dump_date=date, probe=how, url=url,
                    http_status=st, bytes=n, last_modified=lm)

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(work, unique)):
            rows.append(r)
            if r["http_status"] == 200:
                print(f"  FOUND {r['market']} {r['dump_date']} {r['bytes']:,} bytes", flush=True)
            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{len(unique)} probed", flush=True)
    frame = pd.DataFrame(rows).sort_values(["market", "dump_date"])
    frame.to_csv(OUT / "F0_cdn_probe.csv", index=False)
    hits = frame[frame.http_status == 200]
    print(f"\n{len(hits)} of {len(frame)} candidates served (HTTP 200)", flush=True)
    for how, g in frame.groupby("probe"):
        print(f"  {how}: {int((g.http_status == 200).sum())} of {len(g)}", flush=True)
    if len(hits):
        print(hits[["market", "dump_date", "probe", "bytes"]].to_string(index=False), flush=True)
    print(f"wrote {OUT / 'F0_cdn_probe.csv'}", flush=True)


if __name__ == "__main__":
    main()
