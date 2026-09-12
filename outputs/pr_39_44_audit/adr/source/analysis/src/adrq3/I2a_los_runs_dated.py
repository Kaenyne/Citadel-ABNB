"""I2a. Blocked-run lengths WITH START DATES from Inside Airbnb calendars, so run-length
distributions can be compared for the same stay dates (or the same lead time) across vintages.

14c (`analysis/src/adr/14c_los_runs_panel.py`) kept only per-listing totals, which cannot
be restricted to July-September stays. This script re-reads the raw calendars in the main
tree (read-only) with 14c's run definition (a run = contiguous block of `available == 'f'`
nights for one listing; here a gap in the date sequence also ends a run) and writes one
row per run: listing_id, start, len.

Vintages processed: every calendar dated 2024-05-01..2024-07-31, 2025-05-01..2025-09-30 and
2026-06-01..2026-09-05 (the pairs used by I2b), 34 markets.

Output: data/processed/adrq3/I/los_runs/<market>_<date>_runs.parquet   (checkpoint per file)
Run:    py -3.13 analysis/src/adrq3/I2a_los_runs_dated.py [--workers 4]
"""
import sys, re, glob, time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
CAL = MAIN / "data/raw/inside_airbnb_calendar"
OUT = WT / "data/processed/adrq3/I/los_runs"
CHUNK = 4_000_000
WINDOWS = [("2024-05-01", "2024-07-31"), ("2025-05-01", "2025-09-30"), ("2026-06-01", "2026-09-05")]


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def runs_of_block(b):
    b = b.sort_values(["listing_id", "date"], kind="stable")
    lid = b["listing_id"].to_numpy()
    dn = b["date"].to_numpy().astype("datetime64[D]").astype(np.int64)
    unav = (b["available"].to_numpy().astype(str) == "f")
    if len(lid) == 0:
        return pd.DataFrame({"listing_id": [], "start": [], "len": []})
    bd = np.empty(len(lid), bool)
    bd[0] = True
    bd[1:] = (lid[1:] != lid[:-1]) | (unav[1:] != unav[:-1]) | (dn[1:] != dn[:-1] + 1)
    rid = np.cumsum(bd)
    df = pd.DataFrame({"listing_id": lid[unav], "rid": rid[unav], "dn": dn[unav]})
    if df.empty:
        return pd.DataFrame({"listing_id": [], "start": [], "len": []})
    g = df.groupby(["listing_id", "rid"], sort=False).dn.agg(["min", "size"]).reset_index()
    return pd.DataFrame({"listing_id": g.listing_id.values,
                         "start": g["min"].values.astype("datetime64[D]"),
                         "len": g["size"].values.astype(np.int32)})


def process_one(path):
    path = Path(path)
    m = re.match(r"(.+)_(\d{4}-\d{2}-\d{2})_calendar\.csv\.gz", path.name)
    market, date = m.group(1), m.group(2)
    dest = OUT / f"{market}_{date}_runs.parquet"
    if dest.exists():
        return f"{market} {date} cached"
    t0 = time.time()
    parts, carry = [], None
    for ch in pd.read_csv(path, usecols=["listing_id", "date", "available"],
                          dtype={"listing_id": "int64", "available": "str"}, chunksize=CHUNK, low_memory=False):
        ch["date"] = pd.to_datetime(ch["date"], errors="coerce")
        ch = ch.dropna(subset=["date"])
        if carry is not None and len(carry):
            ch = pd.concat([carry, ch], ignore_index=True)
        last = ch["listing_id"].iloc[-1]
        msk = (ch["listing_id"] == last).to_numpy()
        carry = ch[msk]
        parts.append(runs_of_block(ch[~msk]))
    if carry is not None and len(carry):
        parts.append(runs_of_block(carry))
    r = pd.concat(parts, ignore_index=True)
    r["market"] = market
    r["dump_date"] = date
    OUT.mkdir(parents=True, exist_ok=True)
    r.to_parquet(dest, index=False)
    return f"{market} {date}: {len(r)} runs, {time.time() - t0:.0f}s"


def targets():
    fs = sorted(glob.glob(str(CAL / "*_calendar.csv.gz")))
    keep = []
    for f in fs:
        d = re.search(r"_(\d{4}-\d{2}-\d{2})_calendar", f).group(1)
        if any(a <= d <= b for a, b in WINDOWS):
            keep.append(f)
    return keep


if __name__ == "__main__":
    workers = int(sys.argv[2]) if sys.argv[1:2] == ["--workers"] else 4
    fs = targets()
    fs.sort(key=lambda f: Path(f).stat().st_size)
    log(f"{len(fs)} calendars, {sum(Path(f).stat().st_size for f in fs) / 1e9:.2f} GB, {workers} workers")
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(process_one, f): f for f in fs}
        for fu in as_completed(futs):
            try:
                log(fu.result())
            except Exception as e:
                log(f"{Path(futs[fu]).name}: ERR {e!r}")
    log("done")

