"""
Q3 2026 nowcast, workstream E, August-batch refresh, step 2: download every live file in
data/processed/q3nowcast/E_aug/download_plan_aug2026.csv into the MAIN tree raw stores (gitignored),
with the existing naming conventions:
  reviews   C:\\Users\\krish\\citadel-abnb\\data\\raw\\inside_airbnb_reviews\\<market_key>_<date>_reviews.csv.gz
  calendar  C:\\Users\\krish\\citadel-abnb\\data\\raw\\inside_airbnb_calendar\\<short>_<date>_calendar.csv.gz
  listings  C:\\Users\\krish\\citadel-abnb\\data\\raw\\inside_airbnb\\<short>_<date>_listings.csv.gz
(<market_key> is the store key, e.g. japan_kanto_tokyo, even where the CDN path carries a diacritic;
the manifest records the true url.)

Outputs: data/processed/q3nowcast/E_aug/download_manifest_aug2026.csv (file, url, bytes, sha256, status)
         data/processed/q3nowcast/E_aug/download_gaps_aug2026.csv   (failures)

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC-BY 4.0.
Run: py -3.13 analysis/src/q3nowcast/E_aug2_download.py [--workers 4] [--kinds reviews,calendar,listings]
"""
import argparse, concurrent.futures, datetime as dt, hashlib, time
from pathlib import Path
import pandas as pd, requests

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
DEST = {"reviews": MAIN / "data/raw/inside_airbnb_reviews",
        "calendar": MAIN / "data/raw/inside_airbnb_calendar",
        "listings": MAIN / "data/raw/inside_airbnb"}
OUT = WT / "data/processed/q3nowcast/E_aug"
UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def target(row):
    k = row["kind"]
    if k == "reviews":
        return DEST[k] / f"{row['market_key']}_{row['dump_date']}_reviews.csv.gz"
    return DEST[k] / f"{row['short']}_{row['dump_date']}_{k}.csv.gz"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def fetch(row, retries=3):
    url, p = row["url"], target(row)
    exp = int(row["bytes"])
    base = dict(kind=row["kind"], market_key=row["market_key"], dump_date=row["dump_date"], url=url)
    if p.exists() and (not exp or p.stat().st_size == exp):
        return dict(base, file=p.name, bytes=p.stat().st_size, sha256=sha(p), status="already_present")
    for a in range(retries):
        try:
            with requests.get(url, headers=UA, stream=True, timeout=180) as r:
                r.raise_for_status()
                tmp = p.with_suffix(".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
                tmp.replace(p)
            if exp and p.stat().st_size != exp:
                raise IOError(f"size {p.stat().st_size} != expected {exp}")
            return dict(base, file=p.name, bytes=p.stat().st_size, sha256=sha(p), status="downloaded")
        except Exception as e:
            log(f"  retry {a + 1} {p.name}: {e}")
            time.sleep(5 * (a + 1))
    return dict(base, file=p.name, bytes=0, sha256="", status="FAILED")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--kinds", default="reviews,calendar,listings")
    ap.add_argument("--dates", default="", help="comma list of dump dates to restrict to (default all)")
    a = ap.parse_args()
    plan = pd.read_csv(OUT / "download_plan_aug2026.csv", encoding="utf-8")
    plan = plan[plan.kind.isin(a.kinds.split(","))]
    if a.dates:
        plan = plan[plan.dump_date.isin(a.dates.split(","))]
    log(f"{len(plan)} files, {plan.bytes.sum() / 1e9:.2f} GB; by kind {plan.kind.value_counts().to_dict()}")
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(fetch, r) for _, r in plan.iterrows()]
        for i, f in enumerate(concurrent.futures.as_completed(futs), 1):
            r = f.result()
            r["mode"] = "aug_refresh"
            r["downloaded_utc"] = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
            rows.append(r)
            log(f"[{i}/{len(plan)}] {r['status']} {r['file']} {r['bytes'] / 1e6:.0f} MB")
    man = pd.DataFrame(rows)
    mp = OUT / "download_manifest_aug2026.csv"
    if mp.exists():
        man = pd.concat([pd.read_csv(mp, encoding="utf-8"), man], ignore_index=True).drop_duplicates("file", keep="last")
    man.to_csv(mp, index=False, encoding="utf-8")
    bad = man[man.status == "FAILED"]
    bad.to_csv(OUT / "download_gaps_aug2026.csv", index=False, encoding="utf-8")
    log(f"manifest {len(man)} rows, {len(bad)} failures; "
        f"{man[man.status != 'FAILED'].bytes.sum() / 1e9:.2f} GB held")
