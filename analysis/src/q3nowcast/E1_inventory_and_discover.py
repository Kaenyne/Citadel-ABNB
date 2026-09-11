"""
Q3 2026 nowcast, workstream E, step 1+2: inventory every reviews dump we hold, inventory
Theo's review-count and stays artifacts, and HEAD-probe the Inside Airbnb CDN for newer reviews
dumps (and for older vintages of the 13-city panel, used to measure survivorship bias).

Outputs (data/processed/q3nowcast/E/):
  inventory.csv              one row per local reviews/listings file + Theo artifact
  cdn_probe_reviews.csv      every candidate url probed, status, bytes
  download_plan.csv          the reviews dumps worth fetching (newer than held, or an older vintage)

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC-BY 4.0.
Run: py -3.13 analysis/src/q3nowcast/E1_inventory_and_discover.py [--probe-workers 16]
"""
import argparse, concurrent.futures, datetime as dt, time
from pathlib import Path
import pandas as pd, requests

HERE = Path(__file__).resolve()
WT = HERE.parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
REV = MAIN / "data/raw/inside_airbnb_reviews"
IA13 = MAIN / "data/raw/inside_airbnb"
THEO = MAIN / "data/raw/theo_onedrive/AIRBNB DATA"
OUT = WT / "data/processed/q3nowcast/E"
UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}
CDN = "https://data.insideairbnb.com/{path}/{date}/data/reviews.csv.gz"
TODAY = dt.date(2026, 9, 11)

CITY13 = {
    "new-york-city": "united-states/ny/new-york-city", "los-angeles": "united-states/ca/los-angeles",
    "chicago": "united-states/il/chicago", "austin": "united-states/tx/austin",
    "nashville": "united-states/tn/nashville", "new-orleans": "united-states/la/new-orleans",
    "san-diego": "united-states/ca/san-diego", "paris": "france/ile-de-france/paris",
    "london": "united-kingdom/england/london", "barcelona": "spain/catalonia/barcelona",
    "rome": "italy/lazio/rome", "sydney": "australia/nsw/sydney", "mexico-city": "mexico/df/mexico-city",
}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def parse_name(fn):
    for suf in ("_reviews.csv.gz", "_listings.csv.gz", "_calendar.csv.gz"):
        if fn.endswith(suf):
            stem = fn[: -len(suf)]
            kind = suf[1:].split(".")[0]
            break
    else:
        return None
    parts = stem.split("_")
    date, segs = parts[-1], parts[:-1]
    return "/".join(segs), "_".join(segs), date, kind


def local_inventory():
    rows = []
    for p in sorted(REV.glob("*.csv.gz")):
        pr = parse_name(p.name)
        if not pr:
            continue
        path, mkt, date, kind = pr
        rows.append(dict(store="inside_airbnb_reviews", kind=kind, market_key=mkt, cdn_path=path,
                         dump_date=date, file=p.name, bytes=p.stat().st_size, abs_path=str(p)))
    for p in sorted(IA13.glob("*_listings.csv.gz")):
        stem = p.name[: -len("_listings.csv.gz")]
        city, date = stem.rsplit("_", 1)
        rows.append(dict(store="inside_airbnb_13city", kind="listings", market_key=city,
                         cdn_path=CITY13.get(city, ""), dump_date=date, file=p.name,
                         bytes=p.stat().st_size, abs_path=str(p)))
    theo_checks = [
        ("theo_v1", "processed/airbnb_quant_panel_v1/review_events.csv.gz", "review event fact table, 685072 rows per manifest"),
        ("theo_v1", "processed/airbnb_quant_panel_v1/market_snapshot_panel.csv", "market aggregate panel, 133 rows"),
        ("theo_v1", "processed/airbnb_quant_panel_v1/calendar_daily.csv.gz", "calendar fact table"),
        ("theo_v3", "processed/airbnb_quant_panel_v3/review_events.parquet", "v3 review event fact table, 909 MB, manifest location=scratch"),
        ("theo_v3", "processed/airbnb_quant_panel_v3/market_snapshot_panel.csv", "v3 market aggregate panel"),
        ("theo_v3", "processed/airbnb_quant_panel_v3/market_lodging_demand.csv", "v3 market lodging demand"),
        ("theo_v3", "processed/airbnb_quant_panel_v3/listing_snapshots.csv", "v3 listing fact table, 1.4 GB, scratch"),
        ("theo_v3", "processed/airbnb_quant_panel_v3.duckdb", "v3 duckdb, 3.4 GB"),
        ("theo_mongo", "raw/mongodb", "mongodb mirror dir"),
        ("theo_meta", "metadata/inside_airbnb_current_manifest.csv", "current cohort manifest, 120 markets"),
        ("theo_doc", "CODEX_HANDOFF_V3.md", "v3 handoff"),
        ("theo_doc", "docs/V3_DELIVERABLES.md", "v3 deliverables"),
    ]
    for store, rel, note in theo_checks:
        p = THEO / rel
        rows.append(dict(store=store, kind="theo_artifact", market_key="", cdn_path="", dump_date="",
                         file=rel, bytes=(p.stat().st_size if p.is_file() else -1), abs_path=str(p),
                         note=note, present=("file" if p.is_file() else ("dir" if p.is_dir() else "MISSING"))))
    inv = pd.DataFrame(rows)
    inv.to_csv(OUT / "inventory.csv", index=False, encoding="utf-8")
    log(f"inventory.csv: {len(inv)} rows; reviews files {(inv.kind == 'reviews').sum()}, "
        f"13-city listings {(inv.store == 'inside_airbnb_13city').sum()}")
    return inv


def head(sess, url):
    for a in range(3):
        try:
            r = sess.head(url, timeout=45, allow_redirects=True)
            if r.status_code in (200, 403, 404):
                return r.status_code, int(r.headers.get("Content-Length") or 0), r.headers.get("Last-Modified", "")
        except requests.RequestException:
            pass
        time.sleep(1.5 * (a + 1))
    return None, 0, ""


def probe(inv, workers):
    held = (inv[inv.kind == "reviews"][["market_key", "cdn_path", "dump_date"]]
            .sort_values("dump_date").groupby(["market_key", "cdn_path"], as_index=False).last())
    cands = []
    for _, r in held.iterrows():
        d = dt.date.fromisoformat(r.dump_date) + dt.timedelta(days=1)
        while d <= TODAY:
            cands.append((r.market_key, r.cdn_path, d.isoformat(), "newer_than_held"))
            d += dt.timedelta(days=1)
    for city, path in CITY13.items():
        d = dt.date(2025, 1, 1)
        while d <= TODAY:
            cands.append((city, path, d.isoformat(), "older_vintage_13city"))
            d += dt.timedelta(days=1)
    # C: a year-ago vintage for every market, so a vintage-matched y/y (month m in the 2026 dump
    #    against month m-12 in the 2025 dump) can be built without the survivorship wedge
    for _, r in held.iterrows():
        d = dt.date(2025, 7, 1)
        while d <= dt.date(2025, 10, 31):
            cands.append((r.market_key, r.cdn_path, d.isoformat(), "yearago_vintage"))
            d += dt.timedelta(days=1)
    seen, uniq = set(), []
    for c in cands:
        k = (c[1], c[2])
        if k not in seen:
            seen.add(k)
            uniq.append(c)
    log(f"HEAD-probing {len(uniq)} candidate reviews urls, {workers} workers")
    sess = requests.Session()
    sess.headers.update(UA)

    def work(c):
        mkt, path, date, why = c
        st, n, lm = head(sess, CDN.format(path=path, date=date))
        return dict(market_key=mkt, cdn_path=path, dump_date=date, why=why,
                    url=CDN.format(path=path, date=date), http_status=st, bytes=n, last_modified=lm)

    rows, hits = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(work, uniq)):
            rows.append(r)
            if r["http_status"] == 200:
                hits += 1
                log(f"  hit {r['market_key']} {r['dump_date']} {r['bytes'] / 1e6:.0f} MB ({r['why']})")
            if (i + 1) % 2000 == 0:
                log(f"  probed {i + 1}/{len(uniq)}, {hits} live")
    pr = pd.DataFrame(rows)
    pr.to_csv(OUT / "cdn_probe_reviews.csv", index=False, encoding="utf-8")
    live = pr[pr.http_status == 200].copy()
    log(f"cdn_probe_reviews.csv: {len(pr)} probed, {len(live)} live, {live.bytes.sum() / 1e9:.2f} GB")
    have = set(zip(inv[inv.kind == "reviews"].cdn_path, inv[inv.kind == "reviews"].dump_date))
    live["already_held"] = [(p, d) in have for p, d in zip(live.cdn_path, live.dump_date)]
    plan = live[~live.already_held].sort_values(["market_key", "dump_date"])
    plan.to_csv(OUT / "download_plan.csv", index=False, encoding="utf-8")
    log(f"download_plan.csv: {len(plan)} files, {plan.bytes.sum() / 1e9:.2f} GB")
    print(plan.groupby("why").agg(n=("url", "size"), gb=("bytes", lambda s: round(s.sum() / 1e9, 2))).to_string())
    return plan


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-workers", type=int, default=16)
    ap.add_argument("--skip-probe", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    inv = local_inventory()
    if not a.skip_probe:
        probe(inv, a.probe_workers)
