"""14c. Length-of-stay bucket shares from Inside Airbnb calendars, 34 markets, five snapshots.

The question
  The ADR build needs a current length-of-stay mix -- what share of booked nights sits in
  short (<7 night), medium (7-27) and long (28+) stays -- by region, not just for the US.
  Airbnb discloses only regional ALOS (2025: NA 4.1, EMEA 3.8, LatAm 3.6, APAC 3.3) and a
  single global "long-term stays ~17-18% of nights" line. Inside Airbnb calendars are the
  only public panel that can be cut into buckets by market and by quarter.

Method (the run extraction is the repo's existing one, from
  analysis/src/kitchen_wholehome_stay_length.py / research/notes/kitchen_wholehome_stay_length.md)
  A "booked run" is a contiguous block of nights marked unavailable (available == 'f') in
  calendar.csv.gz for one listing. Listings are restricted to those active in the last 12
  months (number_of_reviews_ltm > 0) using the SAME-DATE listings dump already on disk.
  Two caps are reported:
    - CAP 30, the original convention: runs longer than 30 nights are dropped as host blocks.
      Under this cap the 28+ bucket is unobservable, which is why it is only the comparison.
    - CAP 90, this build's convention: runs up to 90 nights are kept so the 28+ bucket exists.
      Runs longer than 90 nights are dropped and counted; their share is the host-block
      contamination signal (a genuinely booked 90+ night run is rare, an off-market host
      block is not).
  Buckets: <7 nights, 7-27 nights, 28+ nights (28-90 under the 90 cap). Reported as a share
  of RUNS (bookings) and of NIGHTS, unweighted and weighted so that each listing contributes
  its estimated_occupancy_l365d (estimated nights booked, trailing 365d) rather than its
  forward calendar nights.

Known caveats, carried from the existing note
  - The forward calendar mixes booked and host-blocked nights, so the LEVEL of mean run
    length is biased UP versus the 10-K ALOS (that build got pooled 4.9 vs NA 4.1). Read the
    differences across regions and across snapshots, not the level.
  - New York City (Local Law 18: a 30-night minimum for un-hosted rentals) and Los Angeles
    (registration + 120-day cap) carry regulatory minimums that mechanically move listings
    into the 28+ bucket. Both are kept in the market table, flagged, and EXCLUDED from the
    regional and global aggregates.
  - A run that touches either end of the 365-day calendar window is truncated by the window.

Snapshots
  One dump per market per quarter, nearest 2025-09-15, 2025-12-15, 2026-03-15, 2026-06-15,
  2026-08-20. Candidates are the dump dates already on disk under data/raw/inside_airbnb;
  where a quarter has none, the CDN is probed day by day around the target (HEAD is 403 on
  this CDN, so a ranged GET is used, as in 08_size_mix_latam_apac.py) and the listings dump
  is fetched alongside the calendar when the calendar turns out to exist.

Run
  py -3.13 analysis/src/adr/14c_los_runs_panel.py discover     probe which calendars exist
  py -3.13 analysis/src/adr/14c_los_runs_panel.py download     fetch them (resumable)
  py -3.13 analysis/src/adr/14c_los_runs_panel.py aggregate    per-listing runs + the panel
Outputs
  data/processed/adr/14c_calendar_manifest.csv      market, date, url, exists, size, flags
  data/processed/adr/14c_los_runs_by_listing/*.parquet   per listing per dump: runs, nights,
                                                    runs and nights by bucket, capped runs,
                                                    min_nights, room_type, accommodates, weight
  data/processed/adr/14c_los_runs_panel.csv         market x dump x segment, plus regional
                                                    and global aggregate blocks
"""
import concurrent.futures as cf
import datetime as dt
import glob
import os
import sys
import time
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/inside_airbnb"
CAL = ROOT / "data/raw/inside_airbnb_calendar"
OUT = ROOT / "data/processed/adr"
BYL = OUT / "14c_los_runs_by_listing"
MANIFEST = OUT / "14c_calendar_manifest.csv"
PANEL = OUT / "14c_los_runs_panel.csv"

UA = {"User-Agent": "Krishang Surapaneni ksurapaneni@ufl.edu"}
CDN = "https://data.insideairbnb.com/{path}/{date}/data/{kind}.csv.gz"
CAP30, CAP90 = 30, 90
CHUNK = 4_000_000
MIN_FREE_GB = 20

# 10-K 2025 nights shares, used only for the global roll-up row
TENK_W = {"na": 0.296, "emea": 0.403, "latam": 0.169, "apac": 0.131}
TENK_ALOS = {"na": 4.1, "emea": 3.8, "latam": 3.6, "apac": 3.3}
REG_MIN_MARKETS = {"new-york-city", "los-angeles"}   # regulatory night minimums; excluded from aggregates

TARGETS = ["2025-09-15", "2025-12-15", "2026-03-15", "2026-06-15", "2026-08-20"]
NEAR_DAYS = 45          # a local dump this close to a target is used as that quarter's snapshot
PROBE_DAYS = 24         # otherwise probe +/- this many days around the target, nearest first

# market -> (CDN path, ABNB region). Paths from analysis/src/inside_airbnb_supply_panel.py
# (the 13 original markets) and analysis/src/adr/08_size_mix_latam_apac.py (the 21 added
# LatAm / APAC markets). Regions follow 11_quote_index_test.py.
MARKETS = {
    "new-york-city": ("united-states/ny/new-york-city", "na"),
    "los-angeles": ("united-states/ca/los-angeles", "na"),
    "chicago": ("united-states/il/chicago", "na"),
    "austin": ("united-states/tx/austin", "na"),
    "nashville": ("united-states/tn/nashville", "na"),
    "new-orleans": ("united-states/la/new-orleans", "na"),
    "san-diego": ("united-states/ca/san-diego", "na"),
    "paris": ("france/ile-de-france/paris", "emea"),
    "london": ("united-kingdom/england/london", "emea"),
    "barcelona": ("spain/catalonia/barcelona", "emea"),
    "rome": ("italy/lazio/rome", "emea"),
    "sydney": ("australia/nsw/sydney", "apac"),
    "mexico-city": ("mexico/df/mexico-city", "latam"),
    "buenos-aires": ("argentina/ciudad-autónoma-de-buenos-aires/buenos-aires", "latam"),
    "rio-de-janeiro": ("brazil/rj/rio-de-janeiro", "latam"),
    "sao-paulo": ("brazil/sp/são-paulo", "latam"),
    "santiago": ("chile/rm/santiago", "latam"),
    "bogota": ("colombia/dc/bogotá", "latam"),
    "belize": ("belize/bz/belize", "latam"),
    "tokyo": ("japan/kantō/tokyo", "apac"),
    "singapore": ("singapore/sg/singapore", "apac"),
    "bangkok": ("thailand/central-thailand/bangkok", "apac"),
    "taipei": ("taiwan/northern-taiwan/taipei", "apac"),
    "hong-kong": ("china/hk/hong-kong", "apac"),
    "melbourne": ("australia/vic/melbourne", "apac"),
    "brisbane": ("australia/qld/brisbane", "apac"),
    "tasmania": ("australia/tas/tasmania", "apac"),
    "western-australia": ("australia/wa/western-australia", "apac"),
    "barossa-valley": ("australia/sa/barossa-valley", "apac"),
    "sunshine-coast": ("australia/qld/sunshine-coast", "apac"),
    "mornington-peninsula": ("australia/vic/mornington-peninsula", "apac"),
    "northern-rivers": ("australia/nsw/northern-rivers", "apac"),
    "mid-north-coast": ("australia/nsw/mid-north-coast", "apac"),
    "barwon-south-west-vic": ("australia/vic/barwon-south-west-vic", "apac"),
}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def url_for(market, date, kind="calendar"):
    return CDN.format(path=urllib.parse.quote(MARKETS[market][0], safe="/"), date=date, kind=kind)


def cal_path(market, date):
    return CAL / f"{market}_{date}_calendar.csv.gz"


def lst_path(market, date):
    return RAW / f"{market}_{date}_listings.csv.gz"


def free_gb():
    import shutil
    return shutil.disk_usage(str(ROOT)).free / 1e9


def local_dates(market):
    pat = str(RAW / f"{market}_*_listings.csv.gz")
    out = []
    for f in glob.glob(pat):
        d = Path(f).name[len(market) + 1:][:10]
        if len(d) == 10 and d[4] == "-":
            out.append(d)
    return sorted(set(out))


def quarter(d):
    d = pd.Timestamp(d)
    return f"{(d.month - 1) // 3 + 1}Q{d.year % 100:02d}"


# --------------------------------------------------------------------------- discover
def probe(url, session=None):
    """(status, size). Ranged GET: this CDN answers HEAD with 403, 206 means present."""
    s = session or requests
    try:
        r = s.get(url, headers={**UA, "Range": "bytes=0-0"}, timeout=45)
    except Exception as e:
        return -1, 0, str(e)[:80]
    n = 0
    cr = r.headers.get("Content-Range")
    if cr and "/" in cr:
        try:
            n = int(cr.split("/")[-1])
        except ValueError:
            n = 0
    return r.status_code, n, ""


def discover_one(market, target):
    """The snapshot for one market x target quarter: nearest local dump, else probe the CDN."""
    t = pd.Timestamp(target)
    loc = local_dates(market)
    near = sorted(loc, key=lambda d: abs((pd.Timestamp(d) - t).days))
    rows = []
    if near and abs((pd.Timestamp(near[0]) - t).days) <= NEAR_DAYS:
        d = near[0]
        st, sz, err = probe(url_for(market, d))
        rows.append(dict(market=market, target=target, date=d, source="local_listings",
                         url=url_for(market, d), status=st, exists=st == 206, size=sz,
                         listings_local=True, note=err))
        return rows
    # no local dump near this target -> probe the CDN day by day, nearest the target first
    days = sorted(range(-PROBE_DAYS, PROBE_DAYS + 1), key=abs)
    sess = requests.Session()
    for k in days:
        d = (t + pd.Timedelta(days=k)).strftime("%Y-%m-%d")
        if d in loc:
            continue
        st, sz, err = probe(url_for(market, d), sess)
        if st == 206:
            rows.append(dict(market=market, target=target, date=d, source="cdn_probe",
                             url=url_for(market, d), status=st, exists=True, size=sz,
                             listings_local=False, note=""))
            return rows
    rows.append(dict(market=market, target=target, date="", source="cdn_probe",
                     url="", status=403, exists=False, size=0, listings_local=False,
                     note=f"no dump within +/-{PROBE_DAYS}d"))
    return rows


def discover():
    tasks = [(m, t) for m in MARKETS for t in TARGETS]
    rows = []
    with cf.ThreadPoolExecutor(10) as ex:
        futs = {ex.submit(discover_one, m, t): (m, t) for m, t in tasks}
        for i, f in enumerate(cf.as_completed(futs), 1):
            rows += f.result()
            if i % 20 == 0:
                log(f"probed {i}/{len(tasks)} market-quarters")
    man = pd.DataFrame(rows).sort_values(["market", "target"]).reset_index(drop=True)
    man["region"] = man.market.map(lambda m: MARKETS[m][1])
    man["quarter"] = [quarter(d) if d else "" for d in man.date]
    man["downloaded"] = [bool(d) and cal_path(m, d).exists() for m, d in zip(man.market, man.date)]
    man["processed"] = [bool(d) and (BYL / f"{m}_{d}.parquet").exists() for m, d in zip(man.market, man.date)]
    OUT.mkdir(parents=True, exist_ok=True)
    man.to_csv(MANIFEST, index=False)
    log(f"manifest: {man.exists.sum()}/{len(man)} calendars found, "
        f"{man.loc[man.exists, 'size'].sum() / 1e9:.2f} GB")
    print(man.groupby(["region", "target"]).exists.sum().unstack(fill_value=0).to_string())
    return man


# --------------------------------------------------------------------------- download
def fetch(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, headers=UA, stream=True, timeout=600) as r:
        if r.status_code != 200:
            return 0, r.status_code
        with open(tmp, "wb") as f:
            for c in r.iter_content(1 << 20):
                f.write(c)
    tmp.replace(dest)
    return dest.stat().st_size, 200


def download_one(row):
    m, d = row.market, row.date
    got = []
    if not cal_path(m, d).exists():
        n, st = fetch(url_for(m, d, "calendar"), cal_path(m, d))
        got.append(f"cal {st} {n / 1e6:.0f}MB")
    if not lst_path(m, d).exists():
        n, st = fetch(url_for(m, d, "listings"), lst_path(m, d))
        got.append(f"lst {st} {n / 1e6:.0f}MB")
    return f"{m} {d} " + (" ".join(got) if got else "already present")


def download():
    man = pd.read_csv(MANIFEST, dtype={"date": str})
    todo = man[man.exists.astype(bool)].copy()
    todo = todo[[not cal_path(m, d).exists() for m, d in zip(todo.market, todo.date)]]
    log(f"{len(todo)} calendars to fetch, {todo['size'].sum() / 1e9:.2f} GB, free {free_gb():.0f} GB")
    todo = todo.sort_values("size")           # small files first so aggregation can start early
    with cf.ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(download_one, r) for r in todo.itertuples()]
        for i, f in enumerate(cf.as_completed(futs), 1):
            log(f"[{i}/{len(todo)}] {f.result()}")
            if free_gb() < MIN_FREE_GB:
                log("STOP: free space below threshold")
                break
    refresh_manifest()


def refresh_manifest():
    man = pd.read_csv(MANIFEST, dtype={"date": str}).fillna({"date": ""})
    man["downloaded"] = [bool(d) and cal_path(m, d).exists() for m, d in zip(man.market, man.date)]
    man["processed"] = [bool(d) and (BYL / f"{m}_{d}.parquet").exists() for m, d in zip(man.market, man.date)]
    man.to_csv(MANIFEST, index=False)
    return man


# --------------------------------------------------------------------------- runs
def _runs_of_block(b):
    """(listing_id, run_length) for every contiguous unavailable block in a sorted block."""
    b = b.sort_values(["listing_id", "date"], kind="stable")
    lid = b["listing_id"].to_numpy()
    unav = (b["available"].to_numpy().astype(str) == "f")
    if len(lid) == 0:
        return pd.DataFrame({"lid": [], "len": []})
    bd = np.empty(len(lid), bool)
    bd[0] = True
    bd[1:] = (lid[1:] != lid[:-1]) | (unav[1:] != unav[:-1])
    rid = np.cumsum(bd)
    sel = unav
    if not sel.any():
        return pd.DataFrame({"lid": [], "len": []})
    df = pd.DataFrame({"lid": lid[sel], "rid": rid[sel]})
    g = df.groupby(["lid", "rid"], sort=False).size().reset_index(name="len")
    return g[["lid", "len"]]


def runs_from_calendar(path):
    """All booked runs in one calendar.csv.gz, read in chunks with a carry-over listing."""
    parts, carry = [], None
    for ch in pd.read_csv(path, usecols=["listing_id", "date", "available"],
                          dtype={"listing_id": "int64", "available": "str"},
                          chunksize=CHUNK, low_memory=False):
        if carry is not None and len(carry):
            ch = pd.concat([carry, ch], ignore_index=True)
        last = ch["listing_id"].iloc[-1]
        m = (ch["listing_id"] == last).to_numpy()
        carry = ch[m]
        parts.append(_runs_of_block(ch[~m]))
    if carry is not None and len(carry):
        parts.append(_runs_of_block(carry))
    r = pd.concat(parts, ignore_index=True)
    return r


def per_listing(runs):
    """One row per listing: runs / nights overall, by cap and by bucket."""
    r = runs.copy()
    r["b"] = np.select([r["len"] < 7, r["len"] < 28, r["len"] <= CAP90], [0, 1, 2], 3)
    g = r.groupby(["lid", "b"])["len"].agg(["size", "sum"]).unstack(fill_value=0)
    out = pd.DataFrame(index=g.index)
    for b, name in [(0, "lt7"), (1, "n7_27"), (2, "ge28"), (3, "over90")]:
        out[f"runs_{name}"] = g[("size", b)] if ("size", b) in g.columns else 0
        out[f"nights_{name}"] = g[("sum", b)] if ("sum", b) in g.columns else 0
    r30 = r[r["len"] <= CAP30].groupby("lid")["len"].agg(runs_le30="size", nights_le30="sum")
    out = out.join(r30).fillna(0)
    out["runs_le90"] = out.runs_lt7 + out.runs_n7_27 + out.runs_ge28
    out["nights_le90"] = out.nights_lt7 + out.nights_n7_27 + out.nights_ge28
    out["runs_all"] = out.runs_le90 + out.runs_over90
    out["nights_all"] = out.nights_le90 + out.nights_over90
    out["max_run"] = r.groupby("lid")["len"].max()
    return out.reset_index().rename(columns={"lid": "listing_id"})


LCOLS = ["id", "room_type", "accommodates", "minimum_nights", "number_of_reviews_ltm",
         "estimated_occupancy_l365d"]


def process_one(market, date):
    """calendar + same-date listings -> data/processed/adr/14c_los_runs_by_listing/<m>_<d>.parquet"""
    dest = BYL / f"{market}_{date}.parquet"
    if dest.exists():
        return f"{market} {date} already processed"
    cp, lp = cal_path(market, date), lst_path(market, date)
    if not cp.exists():
        return f"{market} {date} MISSING calendar"
    t0 = time.time()
    runs = runs_from_calendar(cp)
    pl = per_listing(runs)
    if lp.exists():
        lst = pd.read_csv(lp, usecols=lambda c: c in LCOLS, low_memory=False)
        for c in LCOLS:
            if c not in lst.columns:
                lst[c] = np.nan
        lst = lst[LCOLS].rename(columns={"id": "listing_id"})
        pl = pl.merge(lst, on="listing_id", how="left")
    else:
        for c in LCOLS[1:]:
            pl[c] = np.nan
    pl["active"] = pd.to_numeric(pl.number_of_reviews_ltm, errors="coerce").fillna(0) > 0
    pl["w"] = pd.to_numeric(pl.estimated_occupancy_l365d, errors="coerce").clip(0, 0.7 * 365)
    pl["market"] = market
    pl["dump_date"] = date
    pl["region"] = MARKETS[market][1]
    BYL.mkdir(parents=True, exist_ok=True)
    pl.to_parquet(dest, index=False)
    return (f"{market} {date}: {len(pl)} listings, {int(pl.runs_all.sum())} runs, "
            f"{time.time() - t0:.0f}s")


# --------------------------------------------------------------------------- panel
BUCKETS = ["lt7", "n7_27", "ge28"]


def _block(df, keys, label):
    """Aggregate a set of per-listing rows into panel rows."""
    out = []
    for k, g in df.groupby(keys, dropna=False):
        k = k if isinstance(k, tuple) else (k,)
        row = dict(zip(keys, k))
        row["level"] = label
        row["n_listings"] = len(g)
        row["n_listings_min28"] = int((pd.to_numeric(g.minimum_nights, errors="coerce") >= 28).sum())
        row["share_listings_min28"] = row["n_listings_min28"] / max(row["n_listings"], 1)
        row["runs_le90"] = float(g.runs_le90.sum())
        row["nights_le90"] = float(g.nights_le90.sum())
        row["runs_le30"] = float(g.runs_le30.sum())
        row["nights_le30"] = float(g.nights_le30.sum())
        row["runs_over90"] = float(g.runs_over90.sum())
        row["runs_over30"] = float(g.runs_all.sum() - g.runs_le30.sum())
        row["mean_run_cap30"] = row["nights_le30"] / row["runs_le30"] if row["runs_le30"] else np.nan
        row["mean_run_cap90"] = row["nights_le90"] / row["runs_le90"] if row["runs_le90"] else np.nan
        row["share_runs_at_cap90"] = row["runs_over90"] / max(row["runs_le90"] + row["runs_over90"], 1)
        row["share_runs_over30"] = row["runs_over30"] / max(g.runs_all.sum(), 1)
        for b in BUCKETS:
            row[f"share_runs_{b}"] = g[f"runs_{b}"].sum() / row["runs_le90"] if row["runs_le90"] else np.nan
            row[f"share_nights_{b}"] = g[f"nights_{b}"].sum() / row["nights_le90"] if row["nights_le90"] else np.nan
        # occupancy-weighted: each listing contributes its estimated nights booked, split
        # across buckets in the proportion its calendar runs imply
        ok = g[(g.nights_le90 > 0) & g.w.notna() & (g.w > 0)]
        sc = ok.w / ok.nights_le90
        wn = {b: float((ok[f"nights_{b}"] * sc).sum()) for b in BUCKETS}
        wr = {b: float((ok[f"runs_{b}"] * sc).sum()) for b in BUCKETS}
        tw, twr = sum(wn.values()), sum(wr.values())
        row["w_nights"] = tw
        row["w_runs"] = twr
        row["w_mean_run_cap90"] = tw / twr if twr else np.nan
        for b in BUCKETS:
            row[f"w_share_nights_{b}"] = wn[b] / tw if tw else np.nan
            row[f"w_share_runs_{b}"] = wr[b] / twr if twr else np.nan
        out.append(row)
    return pd.DataFrame(out)


def segment_of(rt):
    if rt == "Entire home/apt":
        return "entire"
    if isinstance(rt, str):
        return "private"
    return "unknown"


def build_panel():
    files = sorted(BYL.glob("*.parquet"))
    if not files:
        log("nothing processed yet")
        return None
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    # Scope flags, computed on the whole dump before the active filter.
    # A handful of 2026 monthly scrapes are SHORT-STAY-ONLY: every listing in them has
    # minimum_nights <= 7, because the scrape queried a short stay and only kept listings
    # bookable for it. Such a dump structurally cannot contain a 28+ night booking, so it is
    # excluded from every aggregate rather than read as a collapse in long stays. A dump under
    # 80% of the market's largest snapshot is flagged partial (the supply panel's rule) and
    # reported, but kept.
    sc = df.groupby(["market", "dump_date"]).agg(
        n_listings_dump=("listing_id", "size"),
        mn_max=("minimum_nights", lambda x: pd.to_numeric(x, errors="coerce").max())).reset_index()
    sc["scope_ratio"] = sc.n_listings_dump / sc.groupby("market").n_listings_dump.transform("max")
    sc["short_stay_only"] = sc.mn_max <= 7
    sc["scope_ok"] = (~sc.short_stay_only) & (sc.scope_ratio >= 0.80)
    df = df.merge(sc, on=["market", "dump_date"], how="left")

    df = df[df.active]                                   # active listings only
    df["segment"] = df.room_type.map(segment_of)
    df["quarter"] = df.dump_date.map(quarter)
    df["reg_min"] = df.market.isin(REG_MIN_MARKETS)
    # snapshot label = the target quarter the dump was chosen for. Aggregates are grouped on
    # it, not on the calendar quarter of the dump date: a market's Dec-2025 snapshot can be a
    # mid-January scrape, and grouping on the calendar quarter would double-count it.
    man = pd.read_csv(MANIFEST, dtype={"date": str}).fillna({"date": ""})
    tgt = dict(zip(zip(man.market, man.date), man.target))
    df["snapshot"] = [tgt.get((m, d), "") for m, d in zip(df.market, df.dump_date)]

    keys = ["market", "dump_date", "snapshot", "quarter", "region", "segment",
            "n_listings_dump", "scope_ratio", "short_stay_only", "scope_ok"]
    parts = []
    m_all = df.assign(segment="all")
    for d in (df, m_all):
        parts.append(_block(d, keys, "market"))
    mk = pd.concat(parts, ignore_index=True)
    mk["reg_min_market"] = mk.market.isin(REG_MIN_MARKETS)

    # regional: drop the two regulatory-minimum markets and the short-stay-only scrapes
    ex = df[(~df.reg_min) & (~df.short_stay_only)]
    ex_all = ex.assign(segment="all")
    reg = _block(pd.concat([ex, ex_all]), ["region", "snapshot", "segment"], "region")
    reg["market"] = "(regional ex NYC/LA)"
    # the same, restricted to full-scope dumps only, as the robustness cut
    fs = df[(~df.reg_min) & df.scope_ok]
    fsr = _block(pd.concat([fs, fs.assign(segment="all")]), ["region", "snapshot", "segment"], "region_fullscope")
    fsr["market"] = "(regional ex NYC/LA, full-scope dumps)"
    reg = pd.concat([reg, fsr], ignore_index=True)
    reg["reg_min_market"] = False

    # global: the four regions blended on the 10-K 2025 nights shares
    gl = []
    for (lvl, q, seg), g in reg.groupby(["level", "snapshot", "segment"]):
        g = g[g.region.isin(TENK_W)]
        if g.empty:
            continue
        w = g.region.map(TENK_W).to_numpy()
        w = w / w.sum()
        row = dict(market="(global 10-K weighted)",
                   level="global" if lvl == "region" else "global_fullscope", snapshot=q, segment=seg,
                   region="global", dump_date="", n_regions=len(g), regions=",".join(sorted(g.region)),
                   n_listings=int(g.n_listings.sum()), runs_le90=float(g.runs_le90.sum()),
                   nights_le90=float(g.nights_le90.sum()), reg_min_market=False)
        for c in ["mean_run_cap30", "mean_run_cap90", "w_mean_run_cap90", "share_runs_at_cap90",
                  "share_listings_min28"] + [f"share_{k}_{b}" for k in ("runs", "nights") for b in BUCKETS] \
                 + [f"w_share_{k}_{b}" for k in ("runs", "nights") for b in BUCKETS]:
            row[c] = float(np.nansum(w * g[c].to_numpy(dtype=float)))
        gl.append(row)
    panel = pd.concat([mk, reg, pd.DataFrame(gl)], ignore_index=True)
    panel = panel.sort_values(["level", "region", "market", "snapshot", "segment"])
    panel.to_csv(PANEL, index=False)
    log(f"wrote {PANEL} ({len(panel)} rows)")
    return panel


def aggregate(workers=4):
    man = refresh_manifest()
    todo = [(r.market, r.date) for r in man.itertuples()
            if r.exists and r.downloaded and not r.processed]
    log(f"{len(todo)} calendars to process")
    if todo:
        # biggest last so a partial run still covers most markets
        todo.sort(key=lambda md: cal_path(*md).stat().st_size)
        if workers > 1:
            with cf.ProcessPoolExecutor(workers) as ex:
                futs = [ex.submit(process_one, m, d) for m, d in todo]
                for i, f in enumerate(cf.as_completed(futs), 1):
                    try:
                        log(f"[{i}/{len(todo)}] {f.result()}")
                    except Exception as e:
                        log(f"[{i}/{len(todo)}] FAILED: {e}")
        else:
            for i, (m, d) in enumerate(todo, 1):
                try:
                    log(f"[{i}/{len(todo)}] {process_one(m, d)}")
                except Exception as e:
                    log(f"[{i}/{len(todo)}] {m} {d} FAILED: {e}")
    refresh_manifest()
    p = build_panel()
    if p is not None:
        show = ["region", "snapshot", "segment", "n_listings", "mean_run_cap30", "mean_run_cap90",
                "share_runs_lt7", "share_runs_n7_27", "share_runs_ge28",
                "share_nights_lt7", "share_nights_n7_27", "share_nights_ge28",
                "share_runs_at_cap90"]
        pd.set_option("display.width", 250)
        r = p[p.level.eq("region") & p.segment.eq("all")]
        print(r[show].round(3).to_string(index=False))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "aggregate"
    if cmd == "discover":
        discover()
    elif cmd == "download":
        download()
    elif cmd == "aggregate":
        w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        aggregate(w)
    elif cmd == "panel":
        build_panel()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
