"""
Q3 2026 nowcast, workstream E, August-batch refresh, step 1: HEAD-probe the Inside Airbnb CDN for
every market in the reviews inventory, every date 1 Aug to 11 Sep 2026, for reviews.csv.gz; then
listings.csv.gz and calendar.csv.gz on every date where reviews is live (Inside Airbnb publishes the
three files together). Also probes the year-ago window (Jun to Oct 2025) for the four markets that
had no 2025 vintage after the E1 run: Tokyo (E1 used the path japan/kanto/tokyo, the CDN path is
japan/kant\u014d/tokyo with a macron, so every Tokyo probe returned 403), Sao Paulo, Bogota and
Nairobi (E1 probed Jul to Oct 2025 only).

Outputs (data/processed/q3nowcast/E_aug/)
  cdn_probe_aug2026.csv        every url probed: market, kind, date, status, bytes, already_held
  download_plan_aug2026.csv    live files not yet held in the main-tree raw stores

Back-off: any status other than 200/403/404 (429, 5xx, timeouts) counts as an error; after 5 errors
inside a minute the pool pauses 30 s, after 20 the run stops and writes what it has.

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC-BY 4.0.
Run: py -3.13 analysis/src/q3nowcast/E_aug1_probe.py [--workers 16]
"""
import argparse, concurrent.futures, datetime as dt, threading, time, urllib.parse
from pathlib import Path
import pandas as pd, requests

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
REV = MAIN / "data/raw/inside_airbnb_reviews"
CAL = MAIN / "data/raw/inside_airbnb_calendar"
LST = MAIN / "data/raw/inside_airbnb"
E = WT / "data/processed/q3nowcast/E"
OUT = WT / "data/processed/q3nowcast/E_aug"
UA = {"User-Agent": "Citadel-ABNB student research ksurapaneni@ufl.edu"}
CDN = "https://data.insideairbnb.com/{path}/{date}/data/{kind}.csv.gz"
TODAY = dt.date(2026, 9, 11)
PATH_FIX = {"japan_kanto_tokyo": "japan/kant\u014d/tokyo"}
YEARAGO_EXT = {"japan_kanto_tokyo": ("2025-06-01", "2025-10-31"),
               "brazil_sp_s\u00e3o-paulo": ("2025-06-01", "2025-06-30"),
               "colombia_dc_bogot\u00e1": ("2025-06-01", "2025-06-30"),
               "kenya_nairobi_nairobi": ("2025-06-01", "2025-06-30")}
# short names of the 34 calendar-panel markets (analysis/src/adr/14c_los_runs_panel.py MARKETS)
SHORT = {
    "united-states/ny/new-york-city": "new-york-city", "united-states/ca/los-angeles": "los-angeles",
    "united-states/il/chicago": "chicago", "united-states/tx/austin": "austin",
    "united-states/tn/nashville": "nashville", "united-states/la/new-orleans": "new-orleans",
    "united-states/ca/san-diego": "san-diego", "france/ile-de-france/paris": "paris",
    "united-kingdom/england/london": "london", "spain/catalonia/barcelona": "barcelona",
    "italy/lazio/rome": "rome", "australia/nsw/sydney": "sydney", "mexico/df/mexico-city": "mexico-city",
    "argentina/ciudad-aut\u00f3noma-de-buenos-aires/buenos-aires": "buenos-aires",
    "brazil/rj/rio-de-janeiro": "rio-de-janeiro", "brazil/sp/s\u00e3o-paulo": "sao-paulo",
    "chile/rm/santiago": "santiago", "colombia/dc/bogot\u00e1": "bogota", "belize/bz/belize": "belize",
    "japan/kant\u014d/tokyo": "tokyo", "singapore/sg/singapore": "singapore",
    "thailand/central-thailand/bangkok": "bangkok", "taiwan/northern-taiwan/taipei": "taipei",
    "china/hk/hong-kong": "hong-kong", "australia/vic/melbourne": "melbourne",
    "australia/qld/brisbane": "brisbane", "australia/tas/tasmania": "tasmania",
    "australia/wa/western-australia": "western-australia", "australia/sa/barossa-valley": "barossa-valley",
    "australia/qld/sunshine-coast": "sunshine-coast", "australia/vic/mornington-peninsula": "mornington-peninsula",
    "australia/nsw/northern-rivers": "northern-rivers", "australia/nsw/mid-north-coast": "mid-north-coast",
    "australia/vic/barwon-south-west-vic": "barwon-south-west-vic",
}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def url(path, date, kind):
    return CDN.format(path=urllib.parse.quote(path, safe="/"), date=date, kind=kind)


def held(market_key, path, date, kind):
    if kind == "reviews":
        return (REV / f"{market_key}_{date}_reviews.csv.gz").exists()
    s = SHORT.get(path)
    if s is None:
        return False
    if kind == "calendar":
        return (CAL / f"{s}_{date}_calendar.csv.gz").exists()
    return (LST / f"{s}_{date}_listings.csv.gz").exists()


class Prober:
    def __init__(self, workers):
        self.sess = requests.Session()
        self.sess.headers.update(UA)
        self.workers = workers
        self.lock = threading.Lock()
        self.errs = []          # timestamps of recent errors
        self.stop = False

    def head(self, u):
        st = None
        for a in range(3):
            if self.stop:
                return None, 0, ""
            try:
                r = self.sess.head(u, timeout=45, allow_redirects=True)
                if r.status_code in (200, 403, 404):
                    return r.status_code, int(r.headers.get("Content-Length") or 0), r.headers.get("Last-Modified", "")
                st = r.status_code
            except requests.RequestException:
                st = -1
            self.error(st)
            time.sleep(2.0 * (a + 1))
        return st, 0, ""

    def error(self, st):
        with self.lock:
            now = time.time()
            self.errs = [t for t in self.errs if now - t < 60] + [now]
            n = len(self.errs)
        if n >= 20:
            log(f"  {n} errors in a minute (last status {st}): stopping the probe")
            self.stop = True
        elif n >= 5:
            log(f"  {n} errors in a minute (last status {st}): pausing 30 s")
            time.sleep(30)

    def run(self, cands):
        rows = []

        def work(c):
            st, n, lm = self.head(c["url"])
            return dict(c, http_status=st, bytes=n, last_modified=lm)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as ex:
            for i, r in enumerate(ex.map(work, cands), 1):
                rows.append(r)
                if r["http_status"] == 200:
                    log(f"  hit {r['kind']:9s} {r['market_key']} {r['dump_date']} {r['bytes'] / 1e6:.1f} MB")
                if i % 1000 == 0:
                    log(f"  probed {i}/{len(cands)}, live so far {sum(x['http_status'] == 200 for x in rows)}")
        return rows


def markets():
    inv = pd.read_csv(E / "inventory.csv", encoding="utf-8")
    r = inv[inv.kind == "reviews"][["market_key", "cdn_path"]].drop_duplicates("market_key")
    r["cdn_path"] = [PATH_FIX.get(k, p) for k, p in zip(r.market_key, r.cdn_path)]
    return r.sort_values("market_key").reset_index(drop=True)


def dates(a, b):
    d, out = dt.date.fromisoformat(a), []
    while d <= dt.date.fromisoformat(b):
        out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    mk = markets()
    log(f"{len(mk)} markets")
    cands = []
    for _, r in mk.iterrows():
        for d in dates("2026-08-01", TODAY.isoformat()):
            cands.append(dict(market_key=r.market_key, cdn_path=r.cdn_path, kind="reviews", dump_date=d,
                              why="aug_batch" if d < "2026-09-01" else "sep_batch",
                              url=url(r.cdn_path, d, "reviews")))
        if r.market_key in YEARAGO_EXT:
            for d in dates(*YEARAGO_EXT[r.market_key]):
                cands.append(dict(market_key=r.market_key, cdn_path=r.cdn_path, kind="reviews", dump_date=d,
                                  why="yearago_ext", url=url(r.cdn_path, d, "reviews")))
    log(f"pass 1: {len(cands)} reviews urls, {a.workers} workers")
    P = Prober(a.workers)
    rows = P.run(cands)
    live = [r for r in rows if r["http_status"] == 200]
    log(f"pass 1 done: {len(live)} live reviews files, {sum(r['bytes'] for r in live) / 1e9:.2f} GB")
    if not P.stop:
        c2 = []
        for r in live:
            if r["why"] == "yearago_ext":
                continue
            for k in ("listings", "calendar"):
                c = dict(r, kind=k, url=url(r["cdn_path"], r["dump_date"], k), bytes=0, last_modified="")
                c.pop("http_status", None)
                c2.append(c)
        log(f"pass 2: {len(c2)} listings/calendar urls on live dates")
        rows += P.run(c2)
    pr = pd.DataFrame(rows)
    pr["already_held"] = [held(m, p, d, k) for m, p, d, k in zip(pr.market_key, pr.cdn_path, pr.dump_date, pr.kind)]
    pr["probed_utc"] = dt.datetime.utcnow().isoformat(timespec="seconds")
    pr.to_csv(OUT / "cdn_probe_aug2026.csv", index=False, encoding="utf-8")
    lv = pr[pr.http_status == 200]
    log(f"cdn_probe_aug2026.csv: {len(pr)} probed, {len(lv)} live; status counts {pr.http_status.value_counts().to_dict()}")
    print(lv.groupby(["kind", "why"]).agg(markets=("market_key", "nunique"), files=("url", "size"),
                                          held=("already_held", "sum")).to_string())
    plan = lv[~lv.already_held].copy()
    # calendar and listings are only stored for the 34-market panel
    plan = plan[(plan.kind == "reviews") | plan.cdn_path.isin(SHORT)]
    plan["short"] = plan.cdn_path.map(SHORT)
    plan.sort_values(["kind", "market_key", "dump_date"]).to_csv(OUT / "download_plan_aug2026.csv",
                                                                 index=False, encoding="utf-8")
    log(f"download_plan_aug2026.csv: {len(plan)} files, {plan.bytes.sum() / 1e9:.2f} GB")
    print(plan.groupby("kind").agg(markets=("market_key", "nunique"), files=("url", "size"),
                                   gb=("bytes", lambda s: round(s.sum() / 1e9, 2))).to_string())
    if P.stop:
        log("probe stopped early on CDN errors; rerun later")
