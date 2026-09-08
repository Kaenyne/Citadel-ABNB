"""08. Unit-size mix in Latin America and Asia Pacific: a real sample behind 05's regional cut.

Why this exists
  05_size_mix.py measured the booking-weighted unit-size mix from Inside Airbnb dumps and
  found a 2Q26 size wedge of +1.41pp worth +0.89pp of ADR, corroborating Airbnb's disclosed
  "bedroom nights +12% vs nights +10%". Its regional cut, however, rested on
      NA   +1.97pp  (7 cities)
      EMEA +1.56pp  (3 cities)
      APAC +0.29pp  (Sydney alone)
      LatAm -0.06pp (Mexico City alone)
  The claim that "size mix is absent in the regions where Airbnb's nights growth is
  concentrated" therefore rested on ONE CITY per region, and the whole panel was
  dense-urban. Both are the obvious lines of attack. This step enlarges LatAm and APAC and
  deliberately adds NON-URBAN markets, which is where Airbnb's larger family stock is
  thought to sit.

Method
  Unchanged from 05. Every size measure, booking weight, coverage gate and hedonic
  conversion is IMPORTED from 05_size_mix.py rather than re-implemented, so the two builds
  cannot silently diverge:
    - booking weight = estimated_occupancy_l365d, which is ESTIMATED NIGHTS BOOKED over the
      trailing 365 days (a count capped at 0.7*365), not an occupancy percentage;
    - `bedrooms` coverage discipline: private/shared/hotel rooms pinned at one bedroom,
      missing whole-home counts imputed from the within-dump median at the same capacity,
      dumps below 80% whole-home coverage dropped, pairs with >10pp coverage drift dropped;
    - the repo pair_eligible / pair_eligible_pit scope convention, with the scope ratio
      recomputed here for the new markets on the supply panel's own rule (a dump under 80%
      of the largest dump of the same market within +/-200 days is partial; fewer than two
      dumps in that window means coverage is unverifiable, which is recorded, not assumed
      clean);
    - hedonic conversion through data/processed/overnight/06_wtp_hedonic_coefs.csv
      (quote basis: bedrooms 0.1402, log-capacity 0.3991).

Acquisition
  Inside Airbnb publishes only the current dump per market; older files stay on the CDN for
  a while. Historical dump dates were recovered from Wayback captures of the get-the-data
  page (the same technique as analysis/src/inside_airbnb_supply_panel.py) and every
  candidate is probed with a ranged GET (HEAD returns 403 on this CDN; 206 means present,
  403 means gone). Every URL attempted, its status, byte count and sha256 is written to
  data/processed/adr/08_acquisition_log.csv.
  Where the Theo OneDrive pull already holds a dump at a date we need, that local copy is
  used instead of re-downloading; it is copied into data/raw/inside_airbnb/ under the repo
  naming convention <market>_<YYYY-MM-DD>_listings.csv.gz so the rest of the repo can read
  it, and the log records source=onedrive_local with the sha256 of the copied bytes.

Run
  py -3.13 analysis/src/adr/08_size_mix_latam_apac.py probe      discover live dump dates
  py -3.13 analysis/src/adr/08_size_mix_latam_apac.py download   fetch them
  py -3.13 analysis/src/adr/08_size_mix_latam_apac.py build      panel + summary

Outputs
  data/processed/adr/08_size_mix_extended_panel.csv    one row per dump (new markets plus the
                                                       05 repo dumps), size aggregates,
                                                       bedrooms coverage, scope flags
  data/processed/adr/08_size_mix_extended_summary.csv  wedges and ADR contributions by
                                                       market, region, settlement type
  data/processed/adr/08_acquisition_log.csv            every URL attempted
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import importlib.util
import os
import shutil
import sys
import time
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/inside_airbnb"
OD = ROOT / "data/raw/theo_onedrive/AIRBNB DATA/raw/inside_airbnb"
OUT = ROOT / "data/processed/adr"
LOG = OUT / "08_acquisition_log.csv"
UA = {"User-Agent": "Krishang Surapaneni ksurapaneni@ufl.edu"}
CDN = "https://data.insideairbnb.com/{path}/{date}/data/listings.csv.gz"

# ---- import workstream 05 so the methodology is literally the same code ------------------
_spec = importlib.util.spec_from_file_location("ws05", Path(__file__).with_name("05_size_mix.py"))
ws05 = importlib.util.module_from_spec(_spec)
_prev = os.getcwd()
os.chdir(ROOT)                      # 05 uses repo-relative paths
_spec.loader.exec_module(ws05)
os.chdir(_prev)

USE = ws05.USE
EH_COV_MIN = ws05.EH_COV_MIN
EH_COV_DRIFT = ws05.EH_COV_DRIFT
YOY_LO, YOY_HI = ws05.YOY_LO, ws05.YOY_HI
SCOPE_MIN_RATIO = 0.80              # matches inside_airbnb_supply_panel.add_scope_flags
SCOPE_WINDOW_DAYS = 200

# ---- the markets -------------------------------------------------------------------------
# market -> (CDN path, ABNB region, settlement type, dump dates harvested from Wayback
# captures of insideairbnb.com/get-the-data/ (2025-04-24, 2025-07-08, 2025-09-08, 2025-11-15,
# 2025-12-30, 2026-04-20, 2026-07-05) plus the live page on 2026-09-07).
# settlement: "urban" = a dense city scrape; "non_urban" = a regional / coastal / state-wide
# scrape, which is the stock the headline 05 panel has none of.
MARKETS = {
    # ---------------- LatAm
    "buenos-aires": ("argentina/ciudad-autónoma-de-buenos-aires/buenos-aires", "latam", "urban",
                     ["2025-01-29", "2026-01-25", "2026-06-29", "2026-07-24"]),
    "rio-de-janeiro": ("brazil/rj/rio-de-janeiro", "latam", "urban",
                       ["2024-12-27", "2025-03-19", "2025-06-24", "2025-09-26", "2026-06-24"]),
    "sao-paulo": ("brazil/sp/são-paulo", "latam", "urban", ["2026-06-14"]),
    "santiago": ("chile/rm/santiago", "latam", "urban", ["2024-12-27", "2026-06-29"]),
    "bogota": ("colombia/dc/bogotá", "latam", "urban", ["2026-06-21"]),
    "belize": ("belize/bz/belize", "latam", "non_urban",
               ["2024-12-29", "2025-03-23", "2025-06-25", "2025-09-28", "2026-06-29"]),
    # ---------------- APAC, urban
    "tokyo": ("japan/kantō/tokyo", "apac", "urban",
              ["2024-12-30", "2025-03-23", "2025-06-27", "2025-09-29", "2026-06-30"]),
    "singapore": ("singapore/sg/singapore", "apac", "urban",
                  ["2024-12-28", "2025-06-25", "2025-09-28", "2026-06-29"]),
    "bangkok": ("thailand/central-thailand/bangkok", "apac", "urban",
                ["2024-12-25", "2025-03-19", "2025-06-24", "2025-09-26", "2026-06-29"]),
    "taipei": ("taiwan/northern-taiwan/taipei", "apac", "urban",
               ["2024-12-31", "2025-03-28", "2025-06-29", "2025-09-30", "2026-06-30"]),
    "hong-kong": ("china/hk/hong-kong", "apac", "urban",
                  ["2025-03-16", "2025-06-21", "2025-09-23", "2026-06-27"]),
    "melbourne": ("australia/vic/melbourne", "apac", "urban",
                  ["2025-03-03", "2025-06-10", "2025-09-12", "2026-06-16"]),
    "brisbane": ("australia/qld/brisbane", "apac", "urban",
                 ["2025-03-02", "2025-06-09", "2025-08-04", "2025-10-07", "2025-11-11",
                  "2026-01-16", "2026-06-15", "2026-07-14"]),
    # ---------------- APAC, non-urban (the point of the exercise)
    "tasmania": ("australia/tas/tasmania", "apac", "non_urban",
                 ["2025-03-02", "2025-06-09", "2025-09-11", "2026-06-15"]),
    "western-australia": ("australia/wa/western-australia", "apac", "non_urban",
                          ["2024-12-25", "2025-03-18", "2025-06-23", "2026-06-28"]),
    "barossa-valley": ("australia/sa/barossa-valley", "apac", "non_urban",
                       ["2024-12-27", "2025-06-25", "2025-09-27", "2026-06-29"]),
    "sunshine-coast": ("australia/qld/sunshine-coast", "apac", "non_urban",
                       ["2025-02-23", "2025-05-31", "2025-08-31", "2025-09-30", "2026-06-30",
                        "2026-07-26"]),
    "mornington-peninsula": ("australia/vic/mornington-peninsula", "apac", "non_urban",
                             ["2025-03-07", "2025-06-15", "2025-09-18", "2026-06-22"]),
    "northern-rivers": ("australia/nsw/northern-rivers", "apac", "non_urban",
                        ["2025-03-11", "2025-06-17", "2025-09-22", "2026-06-24"]),
    "mid-north-coast": ("australia/nsw/mid-north-coast", "apac", "non_urban",
                        ["2025-03-04", "2025-06-10", "2025-08-08", "2025-10-17", "2025-11-12",
                         "2026-06-19", "2026-07-16"]),
    "barwon-south-west-vic": ("australia/vic/barwon-south-west-vic", "apac", "non_urban",
                              ["2024-12-28", "2025-06-25", "2025-09-28", "2026-06-29"]),
}
# 05 markets, carried into the regional aggregates so the enlarged sample is the union of the
# old panel and the new markets, not a replacement for it
REGION_05 = ws05.REGION
SETTLE_05 = {c: "urban" for c in REGION_05}      # the 05 panel is entirely dense-urban

# Date windows probed day by day. Two reasons a window is needed:
#   (a) the market's 2025 leg was never captured by Wayback (santiago, buenos-aires) or the
#       market may simply not have existed in 2025 (sao-paulo, bogota) -- probing settles it;
#   (b) the get-the-data page lags the CDN. Austin's page entry on 2026-09-07 reads
#       2026-06-22 while 2026-07-18 and 2026-08-25 are both on the CDN and in this repo, so
#       "the page's current date" is a floor, not the latest dump. Probing Jul-Sep 2026
#       recovers later b-legs (Melbourne's 2025 dumps are gone from the CDN, so a later
#       2026 dump is its only chance of a pair) and gives the 2026 leg a scope peer.
JUL_SEP_26 = [("2026-07-01", "2026-09-06")]
EXTRA_PROBE = {
    "santiago": [("2025-03-01", "2025-10-31")] + JUL_SEP_26,
    "buenos-aires": [("2025-05-01", "2025-11-30")] + JUL_SEP_26,
    "melbourne": [("2025-04-01", "2025-08-31")] + JUL_SEP_26,
    "tokyo": JUL_SEP_26,
    "singapore": JUL_SEP_26,
    "bangkok": JUL_SEP_26,
    "taipei": JUL_SEP_26,
    "hong-kong": JUL_SEP_26,
    "rio-de-janeiro": JUL_SEP_26,
    "tasmania": JUL_SEP_26,
    "brisbane": JUL_SEP_26,
    "belize": JUL_SEP_26,
    "sao-paulo": [("2025-04-01", "2025-10-31")] + JUL_SEP_26,
    "bogota": [("2025-04-01", "2025-10-31")] + JUL_SEP_26,
    "western-australia": JUL_SEP_26,
    "barossa-valley": JUL_SEP_26,
    "barwon-south-west-vic": JUL_SEP_26,
    "mornington-peninsula": JUL_SEP_26,
    "northern-rivers": JUL_SEP_26,
    "sunshine-coast": JUL_SEP_26,
    "mid-north-coast": JUL_SEP_26,
}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def url_for(path, date):
    return CDN.format(path=urllib.parse.quote(path, safe="/"), date=date)


def local_path(market, date):
    return RAW / f"{market}_{date}_listings.csv.gz"


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def onedrive_index():
    """market -> {date: path} for the single-date dumps already pulled from OneDrive."""
    idx = {}
    if not OD.exists():
        return idx
    for f in OD.glob("*/*/*/*/listings.csv.gz"):
        market, date = f.parts[-3], f.parts[-2]
        idx.setdefault(market, {})[date] = f
    return idx


# ------------------------------------------------------------------------------- probe
def probe_one(sess, market, path, date):
    """A ranged GET, because this CDN answers HEAD with 403 regardless of the object."""
    url = url_for(path, date)
    for attempt in range(3):
        try:
            r = sess.get(url, headers={"Range": "bytes=0-100"}, timeout=45, stream=True)
            status = r.status_code
            cr = r.headers.get("Content-Range", "")
            r.close()
            size = 0
            if "/" in cr:
                try:
                    size = int(cr.rsplit("/", 1)[1])
                except ValueError:
                    size = 0
            return dict(market=market, dump_date=date, url=url, http_status=status,
                        bytes=size, action="probe", source="insideairbnb_cdn", sha256="",
                        note="", ts=dt.datetime.now().isoformat(timespec="seconds"))
        except requests.RequestException as e:
            if attempt == 2:
                return dict(market=market, dump_date=date, url=url, http_status=-1, bytes=0,
                            action="probe", source="insideairbnb_cdn", sha256="",
                            note=type(e).__name__,
                            ts=dt.datetime.now().isoformat(timespec="seconds"))
            time.sleep(2 * (attempt + 1))


def probe(argv):
    cands = []
    for market, (path, _r, _s, dates) in MARKETS.items():
        for d in dates:
            cands.append((market, path, d))
        for lo, hi in EXTRA_PROBE.get(market, []):
            d = dt.date.fromisoformat(lo)
            end = dt.date.fromisoformat(hi)
            while d <= end:
                if d.isoformat() not in dates:
                    cands.append((market, path, d.isoformat()))
                d += dt.timedelta(days=1)
    log(f"probing {len(cands)} candidate dumps across {len(MARKETS)} markets")

    sess = requests.Session()
    sess.headers.update(UA)
    rows, done = [], 0
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(_paced_probe, sess, *c) for c in cands]
        for f in cf.as_completed(futs):
            rows.append(f.result())
            done += 1
            if done % 100 == 0:
                log(f"  probed {done}/{len(cands)}")
    d = pd.DataFrame(rows).sort_values(["market", "dump_date"])
    write_log(d)
    live = d[d.http_status.eq(206)]
    log(f"live dumps: {len(live)} of {len(d)} probed")
    for m, g in live.groupby("market"):
        log(f"  {m}: {' '.join(sorted(g.dump_date))}")
    return d


_LAST = [0.0]


def _paced_probe(sess, market, path, date):
    """~3 requests/second across all workers. The CDN is a static object store, but the
    repo's fetch convention is to pace, so pace."""
    wait = 0.0
    now = time.time()
    if now - _LAST[0] < 0.30:
        wait = 0.30 - (now - _LAST[0])
    _LAST[0] = now + wait
    if wait > 0:
        time.sleep(wait)
    return probe_one(sess, market, path, date)


def write_log(new):
    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["ts", "market", "dump_date", "action", "source", "url", "http_status", "bytes",
            "sha256", "note"]
    if LOG.exists():
        new = pd.concat([pd.read_csv(LOG), new], ignore_index=True)
    for c in cols:
        if c not in new:
            new[c] = ""
    new = new[cols].drop_duplicates(subset=["market", "dump_date", "action", "url"], keep="last")
    new.sort_values(["market", "dump_date", "action"]).to_csv(LOG, index=False)


# ------------------------------------------------------------------------------- download
def download(argv):
    if not LOG.exists():
        log("no acquisition log; run probe first")
        return
    l = pd.read_csv(LOG)
    live = l[l.action.eq("probe") & l.http_status.eq(206)]
    # Every live dump of a target market is worth having: extra vintages are what make the
    # +/-200 day scope reference window computable at all, and 05's pair builder picks the
    # closest-to-365-day partner itself.
    todo = sorted({(m, d) for m, d in zip(live.market, live.dump_date)})
    od = onedrive_index()
    sess = requests.Session()
    sess.headers.update(UA)
    rows = []
    RAW.mkdir(parents=True, exist_ok=True)
    for i, (market, date) in enumerate(todo, 1):
        dest = local_path(market, date)
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        src = od.get(market, {}).get(date)
        if src is not None:
            shutil.copyfile(src, dest)
            rows.append(dict(ts=dt.datetime.now().isoformat(timespec="seconds"), market=market,
                             dump_date=date, action="acquire", source="onedrive_local",
                             url=str(src).replace("\\", "/"), http_status=0,
                             bytes=dest.stat().st_size, sha256=sha256_of(dest),
                             note="copied from the Theo OneDrive pull, not re-downloaded"))
            log(f"[{i}/{len(todo)}] {market} {date}: OneDrive copy "
                f"({dest.stat().st_size / 1e6:.1f} MB)")
            continue
        url = url_for(MARKETS[market][0], date)
        ok, status, nb, note = False, -1, 0, ""
        for attempt in range(3):
            try:
                r = sess.get(url, timeout=300, stream=True)
                status = r.status_code
                if status == 200:
                    tmp = dest.with_suffix(".part")
                    with open(tmp, "wb") as f:
                        for chunk in r.iter_content(1 << 20):
                            f.write(chunk)
                    nb = tmp.stat().st_size
                    os.replace(tmp, dest)
                    ok = True
                r.close()
                break
            except requests.RequestException as e:
                note = type(e).__name__
                time.sleep(3 * (attempt + 1))
        rows.append(dict(ts=dt.datetime.now().isoformat(timespec="seconds"), market=market,
                         dump_date=date, action="acquire", source="insideairbnb_cdn", url=url,
                         http_status=status, bytes=nb,
                         sha256=sha256_of(dest) if ok else "", note=note))
        log(f"[{i}/{len(todo)}] {market} {date}: HTTP {status} {nb / 1e6:.1f} MB")
        time.sleep(2.0)
    if rows:
        write_log(pd.DataFrame(rows))
    log(f"acquired {len(rows)} dumps this run")


# ------------------------------------------------------------------------------- build
def read_dump(path):
    head = pd.read_csv(path, nrows=0).columns
    df = pd.read_csv(path, usecols=[c for c in USE if c in head], low_memory=False)
    for c in USE:
        if c not in df:
            df[c] = np.nan
    return df


def new_market_dumps():
    out = []
    for market in MARKETS:
        for f in sorted(RAW.glob(f"{market}_*_listings.csv.gz")):
            date = f.name[len(market) + 1:len(market) + 11]
            out.append((f, market, date))
    return out


def build_panel(use_cache=True):
    """One row per dump: the new markets read from csv.gz, the 05 repo cities read from the
    parquet cache 05 already built, both through 05's own size_row()."""
    cache = OUT / ".08_size_cache.csv"
    rows = []
    if use_cache and cache.exists():
        p = pd.read_csv(cache)
        p["dump_date"] = pd.to_datetime(p.dump_date)
        log(f"panel from cache: {len(p)} dumps")
        return p
    for f, market, date in new_market_dumps():
        path, region, settle, _ = MARKETS[market]
        try:
            df = read_dump(f)
        except Exception as e:
            log(f"  SKIP {market} {date}: {type(e).__name__}: {e}"[:160])
            continue
        rows.append(ws05.size_row(df, dict(source="ws08_new_market", market=market,
                                           dump_date=date, abnb_region=region,
                                           settlement=settle, cdn_path=path)))
    log(f"new-market dumps: {len(rows)}")
    n0 = len(rows)
    prev = os.getcwd()
    os.chdir(ROOT)
    try:
        for f, city, d in ws05.repo_dumps():
            df = pd.read_parquet(f, columns=USE)
            rows.append(ws05.size_row(df, dict(source="ws05_repo", market=city, dump_date=d,
                                               abnb_region=REGION_05.get(city, "?"),
                                               settlement=SETTLE_05.get(city, "urban"),
                                               cdn_path="")))
    finally:
        os.chdir(prev)
    log(f"05 repo dumps: {len(rows) - n0}")
    p = pd.DataFrame(rows)
    p["dump_date"] = pd.to_datetime(p.dump_date)
    p = p.sort_values(["market", "dump_date"]).reset_index(drop=True)
    p.to_csv(cache, index=False)
    return p


def add_scope(p):
    """The supply panel's coverage rule, recomputed here so the new markets are classified on
    the same basis as the 05 cities rather than inheriting a blank.

    partial_scope        listings below 80% of the largest dump of the same market within
                         +/-200 days (retrospective).
    partial_scope_pit    same rule, trailing-only reference window, so it is never revised.
    scope_unverified     fewer than two dumps in the window: coverage cannot be judged. This
                         is recorded, and a pair built on such a dump is flagged, never
                         silently treated as clean.
    """
    p = p.copy()
    w = pd.Timedelta(days=SCOPE_WINDOW_DAYS)
    retro, retro_n, pit, pit_n = [], [], [], []
    for r in p.itertuples():
        same = p[p.market == r.market]
        near = same[(same.dump_date - r.dump_date).abs() <= w]
        trail = same[(same.dump_date <= r.dump_date) & (r.dump_date - same.dump_date <= w)]
        retro.append(near.listings.max())
        retro_n.append(len(near))
        pit.append(trail.listings.max())
        pit_n.append(len(trail))
    p["scope_ref_listings"] = retro
    p["scope_ref_n_dumps"] = retro_n
    p["scope_vs_peer"] = p.listings / pd.Series(retro, index=p.index)
    p["partial_scope"] = p.scope_vs_peer < SCOPE_MIN_RATIO
    p["scope_unverified"] = p.scope_ref_n_dumps < 2
    p["scope_vs_peer_pit"] = p.listings / pd.Series(pit, index=p.index)
    p["partial_scope_pit"] = p.scope_vs_peer_pit < SCOPE_MIN_RATIO
    p["scope_unverified_pit"] = pd.Series(pit_n, index=p.index) < 2
    return p


def scope_agreement(p):
    """The new markets have no row in the WS21 snapshot file, so `partial_scope` had to be
    recomputed here. Before trusting it, check the recomputation against WS21's own flags on
    the 05 repo dumps, which are in both. Disagreement would mean the new markets are being
    judged on a different rule from the old ones."""
    f = ROOT / "data/processed/inside_airbnb_city_snapshots.csv"
    if not f.exists():
        return None
    s = pd.read_csv(f, usecols=["city", "dump_date", "partial_scope"])
    s["dump_date"] = pd.to_datetime(s.dump_date)
    m = p[p.source.eq("ws05_repo")].merge(s.rename(columns={"city": "market"}),
                                          on=["market", "dump_date"], how="inner",
                                          suffixes=("", "_ws21"))
    if not len(m):
        return None
    agree = (m.partial_scope.astype(bool) == m.partial_scope_ws21.astype(bool))
    return dict(n=len(m), agree=int(agree.sum()), share=float(agree.mean()),
                disagreements=m[~agree][["market", "dump_date", "scope_vs_peer",
                                         "partial_scope", "partial_scope_ws21"]])


def pairs(p):
    """Year-ago pairs, gates in the same order as 05: the bedrooms metadata gate first
    (it moves the size measure directly), then scope."""
    out = []
    for mkt, g in p.groupby("market"):
        g = g.sort_values("dump_date").reset_index(drop=True)
        for j in range(len(g)):
            b = g.iloc[j]
            gap = (b.dump_date - g.dump_date).dt.days
            cand = g[(gap >= YOY_LO) & (gap <= YOY_HI)]
            if cand.empty:
                continue
            a = cand.iloc[int((b.dump_date - cand.dump_date).dt.days.sub(365).abs().values.argmin())]
            ca, cb = a.bedrooms_eh_nonnull_share, b.bedrooms_eh_nonnull_share
            reason = ("bedrooms_field_absent_a" if not (ca >= EH_COV_MIN)
                      else "bedrooms_field_absent_b" if not (cb >= EH_COV_MIN)
                      else "bedrooms_coverage_shift" if abs(cb - ca) > EH_COV_DRIFT
                      else "partial_scope_a" if bool(a.partial_scope)
                      else "partial_scope_b" if bool(b.partial_scope) else "")
            out.append(dict(
                market=mkt, abnb_region=b.abnb_region, settlement=b.settlement,
                source=b.source, date_a=a.dump_date, date_b=b.dump_date,
                days=(b.dump_date - a.dump_date).days,
                listings_a=a.listings, listings_b=b.listings,
                weight_source_a=a.weight_source, weight_source_b=b.weight_source,
                est_nights_a=a.est_nights_ltm, est_nights_b=b.est_nights_ltm,
                bedroom_nights_a=a.bedroom_nights_ltm, bedroom_nights_b=b.bedroom_nights_ltm,
                bed_per_night_a=a.bedrooms_per_booked_night, bed_per_night_b=b.bedrooms_per_booked_night,
                bed_cc_per_night_a=a.bedrooms_cc_per_booked_night, bed_cc_per_night_b=b.bedrooms_cc_per_booked_night,
                bed_f_per_night_a=a.bedrooms_f_per_booked_night, bed_f_per_night_b=b.bedrooms_f_per_booked_night,
                eh_cov_a=ca, eh_cov_b=cb, eh_cov_drift=cb - ca,
                priv_cov_a=a.bedrooms_priv_nonnull_share, priv_cov_b=b.bedrooms_priv_nonnull_share,
                cap_per_night_a=a.capacity_per_booked_night, cap_per_night_b=b.capacity_per_booked_night,
                mlogcap_a=a.mean_log_capacity_booked, mlogcap_b=b.mean_log_capacity_booked,
                share_entire_a=a.share_entire_booked, share_entire_b=b.share_entire_booked,
                share_cap_ge6_a=a.share_cap_ge6_booked, share_cap_ge6_b=b.share_cap_ge6_booked,
                share_cap_le2_a=a.share_cap_le2_booked, share_cap_le2_b=b.share_cap_le2_booked,
                bed_per_listing_a=a.bedrooms_per_listing, bed_per_listing_b=b.bedrooms_per_listing,
                cap_per_listing_a=a.capacity_per_listing, cap_per_listing_b=b.capacity_per_listing,
                partial_a=bool(a.partial_scope), partial_b=bool(b.partial_scope),
                scope_vs_peer_a=a.scope_vs_peer, scope_vs_peer_b=b.scope_vs_peer,
                scope_unverified_a=bool(a.scope_unverified), scope_unverified_b=bool(b.scope_unverified),
                # Capacity (`accommodates`) is 100% populated in every dump and is imputed
                # nowhere, so it is the one size measure the bedrooms coverage regime cannot
                # touch. A pair that fails ONLY the bedrooms gate is still usable for a
                # capacity-only reading, which is how Hong Kong and Buenos Aires -- both
                # excluded on bedrooms coverage alone -- are kept in evidence rather than
                # silently dropped.
                pair_eligible_capacity_only=(not bool(a.partial_scope)
                                             and not bool(b.partial_scope)),
                pair_eligible=(reason == ""), exclusion_reason=reason,
                pair_eligible_pit=(reason == "" and not bool(a.partial_scope_pit)
                                   and not bool(b.partial_scope_pit)),
                scope_unverified_pair=bool(a.scope_unverified) or bool(b.scope_unverified)))
    q = pd.DataFrame(out)
    q["nights_yoy_pct"] = (q.est_nights_b / q.est_nights_a - 1) * 100
    q["bedroom_nights_yoy_pct"] = (q.bedroom_nights_b / q.bedroom_nights_a - 1) * 100
    q["size_wedge_pp"] = q.bedroom_nights_yoy_pct - q.nights_yoy_pct
    q["cap_per_night_yoy_pct"] = (q.cap_per_night_b / q.cap_per_night_a - 1) * 100
    q["bed_cc_per_night_yoy_pct"] = (q.bed_cc_per_night_b / q.bed_cc_per_night_a - 1) * 100
    q["d_bedrooms"] = q.bed_per_night_b - q.bed_per_night_a
    q["d_bedrooms_f"] = q.bed_f_per_night_b - q.bed_f_per_night_a
    q["d_mean_log_cap"] = q.mlogcap_b - q.mlogcap_a
    q["abnb_quarter"] = q.date_b.dt.quarter.astype(str) + "Q" + q.date_b.dt.strftime("%y")
    q["year_b"] = q.date_b.dt.year
    return q


def agg(q, keys, label, hc):
    """05's own nights-weighted aggregation, with the extra columns this build needs."""
    if not len(q):
        return pd.DataFrame()
    a = ws05.agg(q, keys, label, hc)
    extra = []
    for k, g in q.groupby(keys, dropna=False):
        k = k if isinstance(k, tuple) else (k,)
        extra.append(dict(zip(list(keys), k)) | dict(
            n_new_markets=int(g[g.source.eq("ws08_new_market")].market.nunique()),
            n_unverified_scope_pairs=int(g.scope_unverified_pair.sum()),
            median_days=float(g.days.median()),
            listings_a=float(g.listings_a.sum()), listings_b=float(g.listings_b.sum()),
            eh_cov_min=float(min(g.eh_cov_a.min(), g.eh_cov_b.min())),
            eh_cov_drift_max_abs=float(g.eh_cov_drift.abs().max()),
            wedge_pp_market_median=float(g.size_wedge_pp.median())))
    return a.merge(pd.DataFrame(extra), on=list(keys), how="left")


def _confidence(r):
    """A flag with its reason on every summary row. The things that actually degrade a size
    reading here, in order: too few markets (the 05 problem this build exists to fix), too
    few booked nights behind the ratio, and `bedrooms` coverage that moved between the two
    endpoints even while staying inside the gate."""
    why = []
    nm = r.get("n_markets", np.nan)
    if pd.notna(nm) and nm < 2:
        why.append("single market")
    elif pd.notna(nm) and nm < 4:
        why.append(f"only {int(nm)} markets")
    nb = r.get("est_nights_b", np.nan)
    if pd.notna(nb) and nb < 2e5:
        why.append(f"thin: {nb / 1e3:.0f}k booked nights in the later leg")
    dr = r.get("eh_cov_drift_max_abs", np.nan)
    if pd.notna(dr) and dr > 0.05:
        why.append(f"whole-home bedrooms coverage moves up to {dr:.1%} within a pair")
    if str(r.get("scope", "")).endswith("capacity_only_relaxed_bed_gate"):
        why.append("bedrooms gate relaxed: read the capacity columns only, "
                   "the bedrooms columns on this row are contaminated by construction")
    if not why:
        return "high", "multi-market, scope-verified, bedrooms coverage stable within pairs"
    return ("low" if len(why) > 1 or "single market" in why[0] else "medium"), "; ".join(why)


def build(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    hc = ws05.hedonic()
    p = build_panel(use_cache="--rebuild" not in argv)
    p = add_scope(p)
    p.assign(dump_date=p.dump_date.dt.strftime("%Y-%m-%d")).to_csv(
        OUT / "08_size_mix_extended_panel.csv", index=False)
    log(f"panel: {len(p)} dumps, {p.market.nunique()} markets "
        f"({p[p.source.eq('ws08_new_market')].market.nunique()} new)")

    sa = scope_agreement(p)
    if sa:
        log(f"scope rule check: recomputed partial_scope agrees with the WS21 snapshot flags "
            f"on {sa['agree']}/{sa['n']} repo dumps ({sa['share']:.1%})")
        if len(sa["disagreements"]):
            print(sa["disagreements"].assign(
                dump_date=sa["disagreements"].dump_date.dt.strftime("%Y-%m-%d")).to_string(index=False))

    q = pairs(p)
    ok = q[q.pair_eligible]
    log(f"pairs: {len(q)}, eligible {len(ok)}; "
        f"exclusions {q[~q.pair_eligible].exclusion_reason.value_counts().to_dict()}")

    # The 2Q26 disclosure window, the same definition 05 uses.
    w26 = ok[(ok.date_b >= "2026-04-01") & (ok.date_b <= "2026-08-31")]
    new26 = w26[w26.source.eq("ws08_new_market")]

    parts = [
        agg(w26, ["market"], "2Q26_market", hc),
        agg(w26, ["abnb_region"], "2Q26_region_extended", hc),
        agg(w26, ["abnb_region", "settlement"], "2Q26_region_settlement", hc),
        agg(w26, ["settlement"], "2Q26_settlement", hc),
        agg(w26.assign(all_="all"), ["all_"], "2Q26_panel_extended", hc),
        agg(w26[w26.source.eq("ws05_repo")], ["abnb_region"], "2Q26_region_ws05_only", hc),
        agg(new26, ["abnb_region"], "2Q26_region_new_markets_only", hc),
        agg(ok, ["market"], "all_periods_market", hc),
        agg(ok, ["abnb_region"], "all_periods_region", hc),
    ]
    # LatAm and APAC on the enlarged sample, unweighted across markets, so the answer is not
    # one large city carrying the region.
    for reg in ("latam", "apac"):
        m = agg(w26[w26.abnb_region.eq(reg)], ["market"], "m", hc)
        if len(m):
            parts.append(pd.DataFrame([dict(
                scope="2Q26_region_market_unweighted", abnb_region=reg, n_markets=len(m),
                n_pairs=int(m.n_pairs.sum()), markets="|".join(sorted(m.market)),
                nights_yoy_pct=m.nights_yoy_pct.mean(),
                bedroom_nights_yoy_pct=m.bedroom_nights_yoy_pct.mean(),
                size_wedge_pp=m.size_wedge_pp.mean(),
                wedge_pp_market_median=m.size_wedge_pp.median(),
                wedge_pp_market_min=m.size_wedge_pp.min(),
                wedge_pp_market_max=m.size_wedge_pp.max(),
                d_bedrooms=m.d_bedrooms.mean(), d_mean_log_capacity=m.d_mean_log_capacity.mean(),
                size_mix_pp_quote_basis=ws05.size_pp(m.d_bedrooms.mean(),
                                                     m.d_mean_log_capacity.mean(),
                                                     hc["quote_per_night"]),
                size_mix_pp_listed_basis=ws05.size_pp(m.d_bedrooms.mean(),
                                                      m.d_mean_log_capacity.mean(),
                                                      hc["listed_nightly"]))]))
    # Sensitivity: keep the pairs the scope rule rejects. The wedge is a ratio of growth
    # rates, so it should be far less scope-sensitive than any level series; 05 makes the
    # same check.
    a26 = q[(q.date_b >= "2026-04-01") & (q.date_b <= "2026-08-31")]
    parts.append(agg(a26, ["abnb_region"], "sensitivity_2Q26_region_ignore_scope", hc))
    # Sensitivity: drop pairs whose scope could not be verified at all.
    parts.append(agg(w26[~w26.scope_unverified_pair], ["abnb_region"],
                     "sensitivity_2Q26_region_scope_verified_only", hc))
    # Capacity-only reading, which needs no `bedrooms` field and so can carry the markets the
    # bedrooms coverage gate throws out (Hong Kong, Buenos Aires). Read
    # size_mix_pp_capacity_only_quote and cap_per_booked_night_yoy_pct on these rows; the
    # bedrooms columns on them are contaminated by definition and must not be quoted.
    cap26 = q[q.pair_eligible_capacity_only & q.date_b.ge("2026-04-01") & q.date_b.le("2026-08-31")]
    parts.append(agg(cap26, ["abnb_region"], "2Q26_region_capacity_only_relaxed_bed_gate", hc))
    parts.append(agg(cap26, ["market"], "2Q26_market_capacity_only_relaxed_bed_gate", hc))
    parts.append(agg(cap26, ["settlement"], "2Q26_settlement_capacity_only_relaxed_bed_gate", hc))

    s = pd.concat([x for x in parts if len(x)], ignore_index=True)
    s["confidence"], s["confidence_reason"] = zip(*[_confidence(r) for _, r in s.iterrows()])
    s.insert(1, "hedonic_bed_coef_quote", hc["quote_per_night"]["b_bed"])
    s.insert(2, "hedonic_lacc_coef_quote", hc["quote_per_night"]["b_lacc"])
    s["ws05_baseline_note"] = ("05_size_mix.csv, 2Q26 window: na +1.97pp (7 cities), "
                               "emea +1.56pp (3), apac +0.29pp (Sydney only), "
                               "latam -0.06pp (Mexico City only)")
    s.to_csv(OUT / "08_size_mix_extended_summary.csv", index=False)

    q.assign(date_a=q.date_a.dt.strftime("%Y-%m-%d"),
             date_b=q.date_b.dt.strftime("%Y-%m-%d")).to_csv(OUT / "08_size_mix_pairs.csv",
                                                             index=False)

    # ------------------------------------------------------------------ console
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 60)
    cols = [c for c in ["scope", "abnb_region", "settlement", "market", "n_pairs", "n_markets",
                        "n_new_markets", "n_unverified_scope_pairs", "nights_yoy_pct",
                        "bedroom_nights_yoy_pct", "size_wedge_pp", "wedge_pp_market_min",
                        "wedge_pp_market_max", "bed_per_booked_night_a", "bed_per_booked_night_b",
                        "cap_per_booked_night_b", "cap_per_booked_night_yoy_pct",
                        "d_bedrooms", "d_mean_log_capacity",
                        "size_mix_pp_quote_basis", "size_mix_pp_capacity_only_quote",
                        "size_mix_pp_quote_rejected_bedrooms_f",
                        "size_mix_pp_listed_basis",
                        "eh_cov_min", "eh_cov_drift_max_abs", "markets"] if c in s.columns]
    for lab in ("2Q26_panel_extended", "2Q26_region_extended", "2Q26_region_ws05_only",
                "2Q26_region_new_markets_only", "2Q26_region_market_unweighted",
                "2Q26_settlement", "2Q26_region_settlement",
                "sensitivity_2Q26_region_ignore_scope",
                "sensitivity_2Q26_region_scope_verified_only",
                "2Q26_region_capacity_only_relaxed_bed_gate",
                "2Q26_settlement_capacity_only_relaxed_bed_gate",
                "2Q26_market_capacity_only_relaxed_bed_gate", "2Q26_market"):
        sub = s[s.scope.eq(lab)]
        if len(sub):
            print(f"\n-- {lab}")
            print(sub[[c for c in cols if c != "markets" or lab.endswith("unweighted")]]
                  .to_string(index=False))

    print("\n-- per-dump bedrooms coverage, new markets")
    n = p[p.source.eq("ws08_new_market")]
    print(n[["market", "dump_date", "listings", "weight_source", "occ_field_nonnull_share",
             "bedrooms_eh_nonnull_share", "bedrooms_priv_nonnull_share", "scope_vs_peer",
             "partial_scope", "scope_unverified"]]
          .assign(dump_date=n.dump_date.dt.strftime("%Y-%m-%d")).to_string(index=False))

    print("\n-- pairs excluded")
    bad = q[~q.pair_eligible]
    if len(bad):
        print(bad[["market", "date_a", "date_b", "days", "eh_cov_a", "eh_cov_b",
                   "scope_vs_peer_a", "scope_vs_peer_b", "exclusion_reason"]].to_string(index=False))
    print("\n-- target markets with no year-ago pair")
    paired = set(q[q.pair_eligible].market)
    for m in MARKETS:
        if m not in paired:
            have = sorted(f.name[len(m) + 1:len(m) + 11] for f in RAW.glob(f"{m}_*_listings.csv.gz"))
            print(f"  {m}: dumps held {have or 'none'}")
    log("done")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "probe":
        probe(sys.argv)
    elif cmd == "download":
        download(sys.argv)
    elif cmd == "build":
        build(sys.argv)
    elif cmd == "all":
        probe(sys.argv)
        download(sys.argv)
        build(sys.argv)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
