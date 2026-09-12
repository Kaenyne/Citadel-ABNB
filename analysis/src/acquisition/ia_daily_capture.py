#!/usr/bin/env python3
"""Daily Inside Airbnb capture: listings + calendar + reviews for the 120-market list.

Task A2 of the Citadel-ABNB runbook. A missed daily dump is unrecoverable -- Inside
Airbnb only publishes the CURRENT dump per market on the "get the data" page and
rotates old dumps off the CDN, so this script must run every day and never silently
skip a market.

Reuses the existing acquisition layer instead of reinventing it:
  - analysis/src/acquisition/fetch.py                 HTTP GET/HEAD, retry/backoff, pacing
  - analysis/src/acquisition/integrity.py              SHA-256 + structural validation (rejects stubs)
  - analysis/src/acquisition/sources/inside_airbnb.py  regex parser for the get-the-data page

Discovery (step 2 of the runbook): Inside Airbnb's public "get the data" page
(https://insideairbnb.com/get-the-data/) embeds direct CDN links -- country/region/
city/date/data/{listings,calendar,reviews}.csv.gz -- for the CURRENT dump of every
market it tracks. sources.inside_airbnb.parse_index() (already used by
run_inside_airbnb.py) extracts these with a regex, which both discovers the latest
dump date per market AND gives us the exact download URL in one HTTP call. The page
is fetched once per run and cached to data/manifests/ia_get_the_data_cache.html
(reused for up to 6h so re-running the script for testing doesn't hammer the site).

The 120-market list is loaded from Theo's existing acquisition manifest
(../raw_expansion/v2_2026-09-05/inside_airbnb_current_manifest.csv, or the "Theo
Data" mirror), and used to FILTER what the live page discovers, so a change to
Inside Airbnb's own city roster can't silently expand or shrink the run.

Priority order (space-capped by --max-gb):
  0. listings + reviews for all 120 markets
  1. calendar for the 13 "quote cities" (data/processed/overnight/06_quote_line_items.csv
     and 08_ia_dump_metrics.csv)
  2. calendar for the remaining markets, as space allows

Output:
  <capture_root>/<country>/<region>/<city>/<date>/<listings|calendar|reviews>.csv.gz
  data/manifests/ia_daily_capture_manifest.csv   append-only, one row per file
  data/manifests/ia_capture.log                  run log

Idempotent: a (geo_id, dump_date, file) already recorded with status "ok" in the
manifest, whose local file still exists at the expected path with the recorded byte
size, is skipped without a network call.

Usage:
  python analysis/src/acquisition/ia_daily_capture.py --dry-run
  python analysis/src/acquisition/ia_daily_capture.py --max-gb 15
"""
import argparse
import csv
import datetime as dt
import os
import shutil
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
SRC = HERE.parents[1]           # analysis/src
REPO = HERE.parents[3]          # repo root (Citadel-ABNB)
SHARED = REPO.parent            # OneDrive shared folder that also holds raw_expansion/, Theo Data/

sys.path.insert(0, str(SRC))
from acquisition import fetch, integrity          # noqa: E402
from acquisition.sources import inside_airbnb as ia  # noqa: E402

GET_THE_DATA_URL = "https://insideairbnb.com/get-the-data/"
CACHE_HTML = REPO / "data/manifests/ia_get_the_data_cache.html"
CACHE_MAX_AGE_S = 6 * 3600

MANIFEST_CSV = REPO / "data/manifests/ia_daily_capture_manifest.csv"
LOG_PATH = REPO / "data/manifests/ia_capture.log"
MANIFEST_COLS = ["market", "geo_id", "dump_date", "file", "url", "bytes", "sha256", "captured_at", "status"]

MARKET_LIST_CANDIDATES = [
    SHARED / "raw_expansion/v2_2026-09-05/inside_airbnb_current_manifest.csv",
    SHARED / "Theo Data/metadata/inside_airbnb_current_manifest.csv",
]
QUOTE_CITY_FILES = [
    REPO / "data/processed/overnight/06_quote_line_items.csv",
    REPO / "data/processed/overnight/08_ia_dump_metrics.csv",
]

DEFAULT_HOME_CAPTURE_ROOT = Path.home() / "abnb_ia_capture"
EXTERNAL_CAPTURE_SUBDIR = "ia_daily_capture"
MIN_FREE_GB_RESERVE = 3.0
HEAD_POLL_ATTEMPTS = 3
HEAD_POLL_WAIT_S = 2.0
GET_PACE_S = 1.2  # polite delay: >= 1s between requests


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def log(fh, msg: str):
    line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    if fh:
        fh.write(line + "\n")
        fh.flush()


# --------------------------------------------------------------------------------- storage
def find_external_store(max_depth: int = 4):
    """Look for a mounted external volume that already holds Theo's Inside Airbnb store."""
    vol_root = Path("/Volumes")
    if not vol_root.exists():
        return None
    for v in sorted(vol_root.iterdir()):
        if not v.is_dir() or v.name in ("Macintosh HD",):
            continue
        base_depth = len(v.parts)
        try:
            for root, dirs, _files in os.walk(v):
                depth = len(Path(root).parts) - base_depth
                if depth >= max_depth:
                    dirs[:] = []
                    continue
                if "inside_airbnb" in root.lower() or any("inside_airbnb" in d.lower() for d in dirs):
                    return v
        except (PermissionError, OSError):
            continue
    return None


def determine_capture_root():
    ext = find_external_store()
    if ext is not None:
        return ext / EXTERNAL_CAPTURE_SUBDIR, f"external volume with existing Inside Airbnb store detected: {ext}"
    return DEFAULT_HOME_CAPTURE_ROOT, "no external Inside Airbnb volume mounted; using home directory (outside OneDrive)"


# --------------------------------------------------------------------------------- market list / quote cities
def load_market_list():
    for p in MARKET_LIST_CANDIDATES:
        if p.exists():
            markets = set()
            with open(p, encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    parts = row["relative_path"].split("/")
                    if len(parts) < 3:
                        continue
                    markets.add((nfc(parts[0]), nfc(parts[1]), nfc(parts[2])))
            return markets, p
    return None, None


def load_quote_cities():
    cities = set()
    for p in QUOTE_CITY_FILES:
        if not p.exists():
            continue
        with open(p, encoding="utf-8") as f:
            r = csv.DictReader(f)
            if r.fieldnames and "city" in r.fieldnames:
                for row in r:
                    if row.get("city"):
                        cities.add(row["city"])
    return cities


# --------------------------------------------------------------------------------- discovery
def fetch_get_the_data_html(fh):
    if CACHE_HTML.exists() and (time.time() - CACHE_HTML.stat().st_mtime) < CACHE_MAX_AGE_S:
        log(fh, f"using cached get-the-data page ({CACHE_HTML}, age < {CACHE_MAX_AGE_S/3600:.0f}h)")
        return CACHE_HTML.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(GET_THE_DATA_URL, headers={"User-Agent": fetch.UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", errors="replace")
    CACHE_HTML.parent.mkdir(parents=True, exist_ok=True)
    CACHE_HTML.write_text(html, encoding="utf-8")
    log(fh, f"fetched get-the-data page live -> cached to {CACHE_HTML} ({len(html):,} bytes)")
    return html


def discover_snapshots(fh):
    html = fetch_get_the_data_html(fh)
    snaps = ia.parse_index(html)
    markets = {(s.country, s.region, s.city) for s in snaps}
    log(fh, f"discovered {len(snaps)} candidate files across {len(markets)} markets on the get-the-data page")
    return snaps


def restrict_to_market_list(snaps, markets):
    if not markets:
        return list(snaps)
    out = [s for s in snaps if (nfc(s.country), nfc(s.region), nfc(s.city)) in markets]
    return out


def build_tasks(snaps, quote_cities):
    def prio(s):
        if s.kind in ("listings", "reviews"):
            return 0
        if s.kind == "calendar" and s.city in quote_cities:
            return 1
        return 2
    return sorted(snaps, key=lambda s: (prio(s), s.country, s.city, s.kind))


# --------------------------------------------------------------------------------- manifest
def load_existing_manifest():
    done_ok = {}
    if MANIFEST_CSV.exists():
        with open(MANIFEST_CSV, encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                if row.get("status") == "ok":
                    key = (row["geo_id"], row["dump_date"], row["file"])
                    done_ok[key] = row
    return done_ok


def dest_path(capture_root, s):
    return capture_root / s.country / s.region / s.city / s.date / f"{s.kind}.csv.gz"


def poll_head(url, attempts=HEAD_POLL_ATTEMPTS, wait=HEAD_POLL_WAIT_S):
    r = None
    for i in range(attempts):
        r = fetch.head(url)
        if r.status == 200:
            return r
        if i < attempts - 1:
            time.sleep(wait)
    return r


# --------------------------------------------------------------------------------- main run
def run(args):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fh = open(LOG_PATH, "a", encoding="utf-8")
    log(fh, "=" * 88)
    log(fh, f"ia_daily_capture starting: dry_run={args.dry_run} max_gb={args.max_gb}")

    capture_root, root_reason = determine_capture_root()
    if not args.dry_run:
        capture_root.mkdir(parents=True, exist_ok=True)
    log(fh, f"capture root: {capture_root} ({root_reason})")

    markets, market_list_path = load_market_list()
    if markets:
        log(fh, f"loaded {len(markets)} markets from {market_list_path}")
    else:
        log(fh, "WARNING: could not locate the 120-market list csv; using every market the live page discovers")

    quote_cities = load_quote_cities()
    log(fh, f"quote cities ({len(quote_cities)}): {sorted(quote_cities)}")

    try:
        snaps = discover_snapshots(fh)
    except Exception as e:
        log(fh, f"FATAL: could not fetch/parse the get-the-data page: {e!r}")
        fh.close()
        return 0

    snaps = restrict_to_market_list(snaps, markets)
    n_markets = len({(s.country, s.region, s.city) for s in snaps})
    log(fh, f"restricted to {len(snaps)} files across {n_markets} markets after market-list filter")

    tasks = build_tasks(snaps, quote_cities)
    done_ok = load_existing_manifest()

    max_bytes = args.max_gb * 1e9
    budget_used = 0
    stats = defaultdict(int)
    size_by_kind = defaultdict(int)

    writer = None
    mf = None
    if not args.dry_run:
        is_new = not MANIFEST_CSV.exists()
        MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
        mf = open(MANIFEST_CSV, "a", newline="", encoding="utf-8")
        writer = csv.DictWriter(mf, fieldnames=MANIFEST_COLS)
        if is_new:
            writer.writeheader()

    n = len(tasks)
    for i, s in enumerate(tasks, 1):
        geo_id = f"{s.country}/{s.region}/{s.city}"
        key = (geo_id, s.date, s.kind)
        dest = dest_path(capture_root, s)

        if key in done_ok:
            row = done_ok[key]
            try:
                recorded_bytes = int(row.get("bytes") or 0)
            except ValueError:
                recorded_bytes = 0
            if recorded_bytes > 0 and dest.exists() and dest.stat().st_size == recorded_bytes:
                stats["skipped_cached"] += 1
                continue

        if not args.dry_run:
            free_gb = shutil.disk_usage(capture_root).free / 1e9
            if free_gb < MIN_FREE_GB_RESERVE:
                remaining = n - i + 1
                log(fh, f"ABORT: free space on capture volume {free_gb:.1f} GB < reserve "
                        f"{MIN_FREE_GB_RESERVE} GB; stopping with {remaining} files unattempted")
                stats["skipped_low_disk"] += remaining
                break

        hr = poll_head(s.url)
        if hr is None or hr.status != 200:
            stats["head_failed"] += 1
            status = f"head-failed-{hr.status if hr else 'ERR'}"
            log(fh, f"[{i}/{n}] HEAD failed for {s.city}/{s.kind} ({s.date}) status={status}; skipping")
            if writer:
                writer.writerow(dict(market=s.city, geo_id=geo_id, dump_date=s.date, file=s.kind, url=s.url,
                                      bytes=0, sha256="",
                                      captured_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                      status=status))
                mf.flush()
            continue

        est_bytes = hr.content_length or 0
        if budget_used + est_bytes > max_bytes:
            remaining = n - i + 1
            stats["skipped_budget"] += remaining
            log(fh, f"[{i}/{n}] --max-gb {args.max_gb} reached ({budget_used/1e9:.2f} GB used so far); "
                    f"stopping with {remaining} lower-priority files not attempted")
            break

        if args.dry_run:
            log(fh, f"[DRY-RUN {i}/{n}] would fetch {s.city}/{s.kind} {s.date} "
                    f"(~{est_bytes/1e6:.1f} MB) -> {dest}")
            stats["dry_run_would_fetch"] += 1
            budget_used += est_bytes
            continue

        r = fetch.get(s.url, dest, pace=GET_PACE_S)
        captured_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        sha, nbytes = "", 0
        if r.classification == "ok":
            v = integrity.validate(dest)
            if not v.ok:
                dest.unlink(missing_ok=True)
                status = "rejected-" + v.detail[:40]
                stats["rejected"] += 1
            else:
                sha = integrity.sha256_file(dest)
                nbytes = r.bytes
                status = "ok"
                stats["ok"] += 1
                size_by_kind[s.kind] += nbytes
                budget_used += nbytes
        elif r.classification == "source-restriction":
            status = f"source-restriction-{r.status}"
            stats["restricted"] += 1
        else:
            status = f"local-fault-{r.status}"
            stats["failed"] += 1

        writer.writerow(dict(market=s.city, geo_id=geo_id, dump_date=s.date, file=s.kind, url=s.url,
                              bytes=nbytes, sha256=sha, captured_at=captured_at, status=status))
        mf.flush()

        if i % 10 == 0 or status != "ok":
            free_gb = shutil.disk_usage(capture_root).free / 1e9
            log(fh, f"[{i}/{n}] {s.city}/{s.kind} ({s.date}) -> {status} {nbytes/1e6:.1f}MB | "
                    f"ok={stats['ok']} restr={stats['restricted']} fail={stats['failed']} rej={stats['rejected']} "
                    f"budget_used={budget_used/1e9:.2f}GB free={free_gb:.1f}GB")

    if mf:
        mf.close()

    log(fh, f"DONE ok={stats['ok']} skipped_cached={stats['skipped_cached']} "
            f"skipped_budget={stats['skipped_budget']} skipped_low_disk={stats['skipped_low_disk']} "
            f"rejected={stats['rejected']} restricted={stats['restricted']} failed={stats['failed']} "
            f"head_failed={stats['head_failed']} dry_run_would_fetch={stats['dry_run_would_fetch']} "
            f"budget_used={budget_used/1e9:.2f}GB of max {args.max_gb}GB")
    for k, v in size_by_kind.items():
        log(fh, f"  downloaded this run: {k} = {v/1e9:.2f} GB")
    fh.close()
    return 0


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="Plan only: no downloads, no manifest writes.")
    ap.add_argument("--max-gb", type=float, default=15.0, help="Cap on bytes downloaded this run, in GB (default 15).")
    return ap.parse_args()


def main():
    args = parse_args()
    try:
        return run(args)
    except Exception as e:  # noqa: BLE001 - must exit 0 for launchd; failure is visible in the log
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            log(fh, f"FATAL: unhandled exception in ia_daily_capture: {e!r}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
