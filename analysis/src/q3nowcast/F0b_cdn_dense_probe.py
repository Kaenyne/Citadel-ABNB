"""WS-F step 0b: dense day-by-day CDN probe, then download every new calendar vintage.

F0 showed that data.insideairbnb.com retention is NOT a uniform 12 months: austin,
nashville, paris and rome still serve calendar.csv.gz for 2024-06, 2024-09, 2024-12 and
2025-03, while new-york-city, london, barcelona, sydney and mexico-city serve nothing
before 2025-09. Retention is per object, so the only way to know what is left is to probe
every plausible dump date. A 403 from this CDN means the key is not served.

Why it matters: a 2024-09 and 2024-12 pair for the same market is the year-ago analogue of
the 2025-09 -> 2025-12 pair we hold, which turns a descriptive pace read into one
backtestable year-over-year observation against disclosed 4Q24 / 4Q25 nights growth. A
2025-03 vintage pairs against the 2026-03 vintage already on disk for the 2Q/3Q window.

Downloads go to the MAIN tree data/raw/inside_airbnb_calendar with the same
<market>_<date>_calendar.csv.gz naming, and every file is recorded with url, bytes and
sha256 in data/processed/q3nowcast/F/F0b_new_vintages_manifest.csv.

Run: py -3.13 analysis/src/q3nowcast/F0b_cdn_dense_probe.py --probe
     py -3.13 analysis/src/q3nowcast/F0b_cdn_dense_probe.py --download
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import time
from pathlib import Path

import pandas as pd
import requests

from F0_cdn_probe import cdn_paths, head, MANIFEST, OUT, UA, ROOT

MAIN_RAW = Path(r"C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_calendar")
MIN_BYTES = 1_000_000   # a real calendar.csv.gz is megabytes
CORE13 = ["new-york-city", "los-angeles", "chicago", "austin", "nashville", "new-orleans",
          "san-diego", "paris", "london", "barcelona", "rome", "sydney", "mexico-city"]
# Months to sweep day by day. The 13 cities get the 2024 shoulder (a year-ago pair) plus
# all of 2025 up to the vintages we already hold; every other market gets 2025 only.
CORE_MONTHS = ["2024-03", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10",
               "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05",
               "2025-06", "2025-07", "2025-08"]
OTHER_MONTHS = ["2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08"]


def month_days(ym):
    y, m = map(int, ym.split("-"))
    n = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.date(y, m, 1)).days
    return [f"{ym}-{d:02d}" for d in range(1, n + 1)]


def on_disk():
    return {p.name.rsplit("_", 2)[0] + "|" + p.name.rsplit("_", 2)[1]
            for p in MAIN_RAW.glob("*_calendar.csv.gz")}


def probe(args):
    paths = cdn_paths(MANIFEST)
    have = on_disk()
    cands = []
    for market, prefix in sorted(paths.items()):
        months = CORE_MONTHS if market in CORE13 else OTHER_MONTHS
        for ym in months:
            for d in month_days(ym):
                if f"{market}|{d}" not in have:
                    cands.append((market, prefix, d))
    print(f"HEAD-checking {len(cands)} candidate calendar urls across {len(paths)} markets",
          flush=True)
    sess = requests.Session()
    sess.headers.update(UA)

    def work(c):
        market, prefix, date = c
        url = f"https://data.insideairbnb.com/{prefix}/{date}/data/calendar.csv.gz"
        st, n, lm = head(sess, url)
        return dict(market=market, dump_date=date, url=url, http_status=st, bytes=n,
                    last_modified=lm)

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(work, cands)):
            rows.append(r)
            if r["http_status"] == 200:
                print(f"  FOUND {r['market']} {r['dump_date']} {r['bytes']:,}", flush=True)
            if (i + 1) % 500 == 0:
                print(f"  {i + 1}/{len(cands)} probed", flush=True)
    frame = pd.DataFrame(rows).sort_values(["market", "dump_date"])
    frame.to_csv(OUT / "F0b_cdn_dense_probe.csv", index=False)
    hits = frame[frame.http_status == 200]
    print(f"\n{len(hits)} served of {len(frame)} probed", flush=True)
    if len(hits):
        print(hits[["market", "dump_date", "bytes"]].to_string(index=False), flush=True)
    print(f"wrote {OUT / 'F0b_cdn_dense_probe.csv'}", flush=True)


def download(args):
    frames = []
    for name in ("F0_cdn_probe.csv", "F0b_cdn_dense_probe.csv"):
        p = OUT / name
        if p.exists():
            frames.append(pd.read_csv(p))
    hits = pd.concat(frames, ignore_index=True)
    hits = hits[hits.http_status == 200].drop_duplicates(["market", "dump_date"])
    # 24 of the 188 served keys are a few hundred bytes: the CDN serves a stub, not a dump.
    tiny = hits[hits.bytes < MIN_BYTES]
    if len(tiny):
        print(f"skipping {len(tiny)} stub objects under {MIN_BYTES:,} bytes", flush=True)
    hits = hits[hits.bytes >= MIN_BYTES]
    have = on_disk()
    todo = [r for _, r in hits.iterrows() if f"{r.market}|{r.dump_date}" not in have]
    print(f"{len(hits)} served vintages, {len(todo)} not yet on disk", flush=True)
    MAIN_RAW.mkdir(parents=True, exist_ok=True)
    sess = requests.Session()
    sess.headers.update(UA)
    rows = []
    for i, r in enumerate(todo, 1):
        dest = MAIN_RAW / f"{r.market}_{r.dump_date}_calendar.csv.gz"
        t0 = time.time()
        with sess.get(r.url, timeout=600, stream=True) as resp:
            resp.raise_for_status()
            tmp = dest.with_suffix(".part")
            sha = hashlib.sha256()
            with tmp.open("wb") as fh:
                for block in resp.iter_content(1 << 20):
                    fh.write(block)
                    sha.update(block)
            tmp.replace(dest)
        size = dest.stat().st_size
        rows.append(dict(market=r.market, dump_date=r.dump_date, url=r.url, bytes=size,
                         sha256=sha.hexdigest(), local_path=str(dest),
                         content_length_head=r.bytes, size_matches_head=bool(size == r.bytes),
                         downloaded_utc=dt.datetime.utcnow().isoformat(timespec="seconds")))
        print(f"  [{i}/{len(todo)}] {dest.name} {size:,} bytes [{time.time() - t0:.0f}s]",
              flush=True)
    if rows:
        out = OUT / "F0b_new_vintages_manifest.csv"
        frame = pd.DataFrame(rows)
        if out.exists():
            frame = pd.concat([pd.read_csv(out), frame], ignore_index=True)
            frame = frame.drop_duplicates(["market", "dump_date"], keep="last")
        frame.to_csv(out, index=False)
        print(f"wrote {out} ({len(frame)} files)", flush=True)
    else:
        print("nothing to download", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    if args.probe:
        probe(args)
    if args.download:
        download(args)


if __name__ == "__main__":
    main()
