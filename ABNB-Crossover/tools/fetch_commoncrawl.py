"""Fetch kay.com / zales.com homepage captures from Common Crawl.

Independent second archive, used because the Internet Archive replay tier went down mid-build.
Arguably the better source: Common Crawl runs a *systematic* monthly crawl, so capture timing is
not correlated with promotional news events the way trigger-based Wayback captures are.

Path: index.commoncrawl.org/<collection>-index?url=<host>/  ->  {filename, offset, length}
      -> HTTP Range request against data.commoncrawl.org/<filename> -> gzip WARC record -> HTML body

Resumable: successful captures are written to ./cc/<banner>_<timestamp>.html and skipped on re-run.
"""
import gzip, io, json, os, random, sys, time, csv
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.path.join(HERE, "cc")
LOG = os.path.join(HERE, "cc_fetch_log.csv")
os.makedirs(CC, exist_ok=True)

SESS = requests.Session()
SESS.headers.update({"User-Agent": "SIG-equity-research/1.0 (academic coursework; ksurapaneni@ufl.edu)"})


def collections():
    cols = SESS.get("https://index.commoncrawl.org/collinfo.json", timeout=90).json()
    return [c["id"] for c in cols
            if c["id"].startswith("CC-MAIN-") and c["id"][8:12] in ("2023", "2024", "2025", "2026")]


def query(coll, host, tries=4):
    url = f"https://index.commoncrawl.org/{coll}-index?url={host}%2F&output=json"
    for a in range(tries):
        try:
            r = SESS.get(url, timeout=180)
            if r.status_code == 200 and r.text.strip():
                out = []
                for line in r.text.strip().split("\n"):
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        pass
                return out
            if r.status_code == 404:
                return []          # host absent from this crawl
        except Exception:
            pass
        time.sleep(6 * (a + 1))
    return []


def fetch_record(rec, banner, tries=3):
    ts = rec["timestamp"]
    path = os.path.join(CC, f"{banner}_{ts}.html")
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return "cached", os.path.getsize(path)
    off, ln = int(rec["offset"]), int(rec["length"])
    url = "https://data.commoncrawl.org/" + rec["filename"]
    for a in range(tries):
        try:
            r = SESS.get(url, headers={"Range": f"bytes={off}-{off+ln-1}"}, timeout=180)
            if r.status_code in (200, 206):
                raw = gzip.GzipFile(fileobj=io.BytesIO(r.content)).read().decode("utf-8", "ignore")
                # WARC record: warc headers \r\n\r\n http headers \r\n\r\n body
                parts = raw.split("\r\n\r\n", 2)
                body = parts[-1] if len(parts) == 3 else raw
                if len(body) < 3000:
                    return f"short_body_{len(body)}", 0
                open(path, "w", encoding="utf-8").write(body)
                return "ok", len(body)
            last = f"http_{r.status_code}"
        except Exception as e:
            last = f"err_{type(e).__name__}"
        time.sleep(5 * (a + 1))
    return last, 0


def main():
    banners = sys.argv[1:] or ["kay", "zales"]
    cols = collections()
    print(f"{len(cols)} collections", flush=True)
    new = not os.path.exists(LOG)
    lf = open(LOG, "a", newline="", encoding="utf-8")
    w = csv.writer(lf)
    if new:
        w.writerow(["banner", "collection", "timestamp", "status", "bytes"])
    for banner in banners:
        host = f"{banner}.com"
        for coll in cols:
            recs = query(coll, host)
            ok = [r for r in recs
                  if r.get("status") == "200"
                  and r.get("mime", "text/html").startswith("text/html")
                  and r.get("url", "").rstrip("/").endswith(f"{banner}.com")]
            # de-dup by timestamp; cap per collection so one crawl cannot dominate
            seen, keep = set(), []
            for r in sorted(ok, key=lambda x: x["timestamp"]):
                if r["timestamp"] in seen:
                    continue
                seen.add(r["timestamp"])
                keep.append(r)
            keep = keep[:6]
            print(f"  {banner} {coll}: {len(recs)} recs, {len(ok)} html-200, fetching {len(keep)}",
                  flush=True)
            for rec in keep:
                st, n = fetch_record(rec, banner)
                w.writerow([banner, coll, rec["timestamp"], st, n])
                lf.flush()
                if st != "cached":
                    time.sleep(1.5 + random.uniform(0, 1.0))
            time.sleep(2.0)
    lf.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
