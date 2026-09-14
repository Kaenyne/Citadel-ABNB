"""
Q3 2026 nowcast, workstream E, step 2: download reviews.csv.gz dumps selected from
data/processed/q3nowcast/E/download_plan.csv into the MAIN tree raw store
C:\\Users\\krish\\citadel-abnb\\data\\raw\\inside_airbnb_reviews (gitignored), and write a manifest
with url, bytes and sha256.

Selection modes
  --mode latest     the newest available dump per market that we do not already hold (the Jul/Aug 2026 refresh)
  --mode vintages   older vintages of the 13-city panel nearest to the dates in --targets, for survivorship

Outputs: data/processed/q3nowcast/E/download_manifest.csv (appended, deduped on file)
         data/processed/q3nowcast/E/download_gaps.csv   (markets with no reachable newer dump)

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC-BY 4.0.
Run: py -3.13 analysis/src/q3nowcast/E2_download_reviews.py --mode latest --workers 4
"""
import argparse, concurrent.futures, datetime as dt, hashlib, time
from pathlib import Path
import pandas as pd, requests

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
DEST = MAIN / "data/raw/inside_airbnb_reviews"
OUT = WT / "data/processed/q3nowcast/E"
UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def fname(cdn_path, date):
    return f"{cdn_path.replace('/', '_')}_{date}_reviews.csv.gz"


def select(mode, targets):
    plan = pd.read_csv(OUT / "download_plan.csv")
    if mode == "latest":
        n = plan[plan.why == "newer_than_held"]
        return n.sort_values("dump_date").groupby("market_key", as_index=False).last()
    o = plan[plan.why.isin(["older_vintage_13city", "yearago_vintage"])].copy()
    o["d"] = pd.to_datetime(o.dump_date)
    keep = []
    for t in targets:
        td = pd.Timestamp(t)
        for mkt, g in o.groupby("market_key"):
            i = (g.d - td).abs().idxmin()
            keep.append(i)
    return o.loc[sorted(set(keep))].drop_duplicates(["cdn_path", "dump_date"])


def fetch(row, retries=3):
    url, p = row["url"], DEST / fname(row["cdn_path"], row["dump_date"])
    exp = int(row["bytes"])
    if p.exists() and p.stat().st_size == exp:
        h = sha(p)
        return dict(file=p.name, url=url, bytes=p.stat().st_size, sha256=h, status="already_present")
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
            return dict(file=p.name, url=url, bytes=p.stat().st_size, sha256=sha(p), status="downloaded")
        except Exception as e:
            log(f"  retry {a + 1} {p.name}: {e}")
            time.sleep(3 * (a + 1))
    return dict(file=p.name, url=url, bytes=0, sha256="", status="FAILED")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["latest", "vintages"], default="latest")
    ap.add_argument("--targets", default="2025-08-15")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    sel = select(a.mode, [t for t in a.targets.split(",") if t])
    log(f"mode {a.mode}: {len(sel)} files, {sel.bytes.sum() / 1e9:.2f} GB -> {DEST}")
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(fetch, r): r for _, r in sel.iterrows()}
        done = 0
        for f in concurrent.futures.as_completed(futs):
            r = f.result()
            r["mode"] = a.mode
            r["downloaded_utc"] = dt.datetime.utcnow().isoformat(timespec="seconds")
            rows.append(r)
            done += 1
            log(f"[{done}/{len(sel)}] {r['status']} {r['file']} {r['bytes'] / 1e6:.0f} MB")
    man = pd.DataFrame(rows)
    mp = OUT / "download_manifest.csv"
    if mp.exists():
        man = pd.concat([pd.read_csv(mp), man], ignore_index=True).drop_duplicates("file", keep="last")
    man.to_csv(mp, index=False, encoding="utf-8")
    bad = man[man.status == "FAILED"]
    bad.to_csv(OUT / "download_gaps.csv", index=False, encoding="utf-8")
    log(f"manifest {len(man)} rows, {len(bad)} failures; {man[man.status != 'FAILED'].bytes.sum() / 1e9:.2f} GB held")
