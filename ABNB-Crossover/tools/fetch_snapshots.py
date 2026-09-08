"""Fetch archived kay.com / zales.com homepage snapshots from the Wayback Machine.

Resumable: every successful fetch is written to disk as <banner>_<timestamp>.html and
skipped on re-run. Failures are logged to fetch_log.csv so coverage can be reported honestly.
"""
import json, os, random, time, csv, sys
import requests

CACHE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(CACHE, "fetch_log.csv")

# months that get a denser sample: Nov/Dec (holiday), Jan (post-holiday clearance),
# Feb (Valentine's), May (Mother's Day)
DENSE = {1, 2, 5, 11, 12}
N_BASE, N_DENSE = 3, 5

SESS = requests.Session()
SESS.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
})


def build_sample(banner):
    rows = json.load(open(os.path.join(CACHE, f"cdx_{banner}.json")))[1:]
    by_month = {}
    for r in rows:
        by_month.setdefault(r[1][:6], []).append(r[1])
    out = []
    for month in sorted(by_month):
        ts = sorted(by_month[month])
        n = N_DENSE if int(month[4:6]) in DENSE else N_BASE
        if len(ts) <= n:
            pick = ts
        else:
            # even spread across the month
            idx = [round(i * (len(ts) - 1) / (n - 1)) for i in range(n)]
            pick = [ts[i] for i in sorted(set(idx))]
        out.extend(pick)
    return out


def fetch(banner, ts, tries=4):
    path = os.path.join(CACHE, f"{banner}_{ts}.html")
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return "cached", os.path.getsize(path)
    url = f"https://web.archive.org/web/{ts}id_/https://www.{banner}.com/"
    last = "unknown"
    for a in range(tries):
        try:
            r = SESS.get(url, timeout=120)
            if r.status_code == 200 and len(r.text) > 3000:
                # guard against the IA "Temporarily Offline" interstitial
                if "Internet Archive services are temporarily offline" in r.text:
                    last = "ia_offline"
                else:
                    open(path, "w", encoding="utf-8").write(r.text)
                    return "ok", len(r.text)
            else:
                last = f"http_{r.status_code}_len{len(r.text)}"
        except Exception as e:
            last = f"err_{type(e).__name__}"
        time.sleep(min(60, 4 * (2 ** a)) + random.uniform(0, 2))
    return last, 0


def wait_for_service(max_wait=7200):
    """Block until the Wayback replay service stops returning the outage interstitial."""
    probe = "https://web.archive.org/web/20250105113728id_/https://www.kay.com/"
    t0 = time.time()
    while time.time() - t0 < max_wait:
        try:
            r = SESS.get(probe, timeout=60)
            if r.status_code == 200 and "temporarily offline" not in r.text.lower():
                print(f"replay service up after {int(time.time()-t0)}s", flush=True)
                return True
        except Exception:
            pass
        print(f"  waiting for replay service ({int(time.time()-t0)}s elapsed)", flush=True)
        time.sleep(60)
    return False


def main():
    banners = sys.argv[1:] or ["kay", "zales"]
    wait_for_service()
    new_log = not os.path.exists(LOG)
    lf = open(LOG, "a", newline="", encoding="utf-8")
    w = csv.writer(lf)
    if new_log:
        w.writerow(["banner", "timestamp", "status", "bytes"])
    consecutive_fail = 0
    for banner in banners:
        sample = build_sample(banner)
        print(f"{banner}: sampling {len(sample)} snapshots", flush=True)
        for i, ts in enumerate(sample):
            status, n = fetch(banner, ts)
            w.writerow([banner, ts, status, n])
            lf.flush()
            if status in ("ok", "cached"):
                consecutive_fail = 0
            else:
                consecutive_fail += 1
            if i % 10 == 0:
                print(f"  {banner} {i}/{len(sample)} {ts} -> {status}", flush=True)
            if status != "cached":
                time.sleep(1.5 + random.uniform(0, 1.0))
            # if the archive is hard down, back off long rather than burn the sample
            if consecutive_fail >= 8:
                print("  8 consecutive failures - long backoff 180s", flush=True)
                time.sleep(180)
                consecutive_fail = 0
    lf.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
