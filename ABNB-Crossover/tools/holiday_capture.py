"""Weekly live pricing capture for Signet banners via the Unbxd search API (built 2026-09-03).

The banner sites (kay.com, zales.com, jared.com) return 403 to scripts, but their category pages are
rendered from Unbxd's public search API using site keys embedded in the pages. This script queries that
API the way the site's own front end does, at low volume (~24 requests per banner per run), and computes
the same measures as the Common Crawl series so the weekly points splice onto the fiscal-quarter history:
  breadth  = share of products whose current price is below list (MSRP)
  depth    = average markdown among those
  discount_factor = breadth x depth        (UBS Evidence Lab definition)
  median_msrp / median_price               ("central price")
plus lab-grown share and a bridal / fashion / watch split from the category path and title.

Run:  python holiday_capture.py                (kay, zales, jared)
      python holiday_capture.py --banners kay,zales,jared,banter,peoples
Outputs: holiday_capture_products/<YYYY-MM-DD>_<banner>.csv (one row per product),
         holiday_capture_weekly.csv (one summary row per banner per run, appended).
Scheduled weekly (Mondays 08:00) via Windows Task Scheduler as "SIG holiday pricing capture".
"""
import argparse, os, re, time, datetime as dt, json
import requests, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "holiday_capture_products"); os.makedirs(OUT_DIR, exist_ok=True)
WEEKLY = os.path.join(HERE, "holiday_capture_weekly.csv")
LOG = os.path.join(HERE, "holiday_capture.log")
# site keys as embedded in the banners' own pages (Kay PDP config, Aug 2026)
SITES = {
    "kay":     ("18d57de5077c063f9223fc48dfd31820", "ss-unbxd-gus-prod-kay27631718722879", "https://www.kay.com/"),
    "zales":   ("6aca609af777259abba5b601704bd6a4", "ss-unbxd-gus-prod-zales27631718722962", "https://www.zales.com/"),
    "jared":   ("8ecc0caa425dc75f58fc86a734eec3d3", "ss-unbxd-gus-prod-jared27631718470417", "https://www.jared.com/"),
    "banter":  ("a6b646cd772cb4d8c5bbc225de10b324", "ss-unbxd-gus-prod-banter27631718723236", "https://www.banter.com/"),
    "peoples": ("4dcbe1713d7e3bda1f31ae3833139af3", "ss-unbxd-gus-prod-peoplesjewellers27631718723053", "https://www.peoplesjewellers.com/"),
}
TERMS = ["ring", "engagement ring", "necklace", "earrings", "bracelet", "chain", "lab-grown diamond", "gold"]
ROWS, PAGES = 100, 3
FIELDS = "title,uniqueId,price,MSRP,min_price,max_price,productUrl,categoryPath1,categoryPath"

def log(m):
    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {m}"; print(line, flush=True)
    open(LOG, "a", encoding="utf-8").write(line + "\n")

def fetch_banner(name):
    key, site, ref = SITES[name]
    H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
         "Accept": "application/json", "Referer": ref, "Origin": ref.rstrip("/")}
    prods = {}
    for term in TERMS:
        for page in range(PAGES):
            u = (f"https://search.unbxd.io/{key}/{site}/search?q={requests.utils.quote(term)}&version=V2"
                 f"&start={page * ROWS}&rows={ROWS}&fields={FIELDS}")
            try:
                r = requests.get(u, headers=H, timeout=40)
                if r.status_code != 200: log(f"{name} {term} p{page}: HTTP {r.status_code}"); break
                ps = r.json().get("response", {}).get("products", [])
            except Exception as e:
                log(f"{name} {term} p{page}: ERR {str(e)[:80]}"); break
            for p in ps:
                uid = str(p.get("uniqueId"))
                if uid in prods: continue
                cp = p.get("categoryPath") or []
                prods[uid] = dict(uniqueId=uid, title=p.get("title"), price=p.get("price"), msrp=p.get("MSRP"),
                                  min_price=p.get("min_price"), max_price=p.get("max_price"), url=p.get("productUrl"),
                                  category1=(p.get("categoryPath1") or [None])[0] if isinstance(p.get("categoryPath1"), list) else p.get("categoryPath1"),
                                  category_path="|".join(cp[:12]) if isinstance(cp, list) else str(cp), term=term)
            if len(ps) < ROWS: break
            time.sleep(1.0)
        time.sleep(1.0)
    return pd.DataFrame(prods.values())

def summarise(d, name, run_date):
    d = d.dropna(subset=["price"]).copy()
    d["price"] = pd.to_numeric(d["price"], errors="coerce"); d["msrp"] = pd.to_numeric(d["msrp"], errors="coerce").fillna(d["price"])
    d = d[(d["price"] > 0) & (d["msrp"] > 0)]
    d["disc"] = np.clip(1 - d["price"] / d["msrp"], 0, 0.95); d["on_sale"] = d["disc"] > 0.005
    txt = (d["title"].fillna("") + " " + d["category_path"].fillna("") + " " + d["url"].fillna("")).str.lower()
    d["bucket"] = np.where(txt.str.contains(r"\bwatch"), "watch", np.where(txt.str.contains(r"engagement|bridal|wedding band|anniversary band|bridal set"), "bridal", "fashion"))
    d["lab_grown"] = txt.str.contains(r"lab[- ]?(?:grown|created)")
    on = d[d["on_sale"]]
    row = dict(run_date=run_date, banner=name, n=len(d), breadth=d["on_sale"].mean(), depth=on["disc"].mean() if len(on) else 0.0,
               discount_factor=d["on_sale"].mean() * (on["disc"].mean() if len(on) else 0.0), mean_discount_all=d["disc"].mean(),
               median_msrp=d["msrp"].median(), median_price=d["price"].median(), share_lab_grown=d["lab_grown"].mean(),
               share_bridal=(d["bucket"] == "bridal").mean(), share_watch=(d["bucket"] == "watch").mean())
    for b in ("bridal", "fashion"):
        g = d[d["bucket"] == b]; og = g[g["on_sale"]]
        row[f"discount_factor_{b}"] = (g["on_sale"].mean() * (og["disc"].mean() if len(og) else 0.0)) if len(g) else np.nan
        row[f"median_msrp_{b}"] = g["msrp"].median() if len(g) else np.nan
        row[f"median_price_{b}"] = g["price"].median() if len(g) else np.nan
    return d, row

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--banners", default="kay,zales,jared"); a = ap.parse_args()
    run_date = dt.date.today().isoformat(); rows = []
    for name in a.banners.split(","):
        d = fetch_banner(name)
        if d.empty: log(f"{name}: no products"); continue
        d, row = summarise(d, name, run_date)
        d.to_csv(os.path.join(OUT_DIR, f"{run_date}_{name}.csv"), index=False); rows.append(row)
        log(f"{name}: n={row['n']} breadth={row['breadth']:.2f} depth={row['depth']:.2f} discount_factor={row['discount_factor']:.3f} median_msrp={row['median_msrp']:.0f} median_price={row['median_price']:.0f} lab={row['share_lab_grown']:.2f}")
    if rows:
        w = pd.DataFrame(rows)
        if os.path.exists(WEEKLY): w = pd.concat([pd.read_csv(WEEKLY), w], ignore_index=True)
        w.to_csv(WEEKLY, index=False); log(f"weekly file now {len(w)} rows")

if __name__ == "__main__":
    main()
