"""Matched-SKU panel from Common Crawl: like-for-like price and markdown changes (built 2026-09-03).

For a pair of windows (default: Signet Q2 FY26 = May-Jul 2025 crawls vs Q2 FY27 = May-Jul 2026 crawls), and
each banner: harvest the product-page index for every crawl in both windows, intersect product codes
(V-xxxxx), sample up to N matched codes, fetch the capture from each window (preferring the same calendar
month), parse with cc_pricing_scraper.parse, and write one row per matched product with both sides.
Then summarise like-for-like: median list-price change, median sale-price change, markdown breadth and
depth on the same products, share with a list-price increase, by banner and by bucket.

Run:  python cc_matched_sku.py                      (Q2 windows, N=300 per banner)
      python cc_matched_sku.py --window holiday     (Nov-Dec 2024 vs Nov-Dec 2025 crawls)
Outputs: cc_matched_sku_<window>.csv (rows), cc_matched_sku_<window>_summary.csv, log in cc_matched_sku.log
"""
import argparse, os, re, json, random, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cc_pricing_scraper as cc

HERE = os.path.dirname(os.path.abspath(__file__))
WINDOWS = {
    "q2":      {"a": ["CC-MAIN-2025-21", "CC-MAIN-2025-26", "CC-MAIN-2025-30"], "b": ["CC-MAIN-2026-21", "CC-MAIN-2026-25", "CC-MAIN-2026-30"],
                "label_a": "Q2 FY26 (May-Jul 2025)", "label_b": "Q2 FY27 (May-Jul 2026)"},
    "holiday": {"a": ["CC-MAIN-2024-46", "CC-MAIN-2024-51"], "b": ["CC-MAIN-2025-47", "CC-MAIN-2025-51"],
                "label_a": "holiday FY25 (Nov-Dec 2024)", "label_b": "holiday FY26 (Nov-Dec 2025)"},
}
LOG = os.path.join(HERE, "cc_matched_sku.log")
def log(m):
    line = f"{time.strftime('%H:%M:%S')} {m}"; print(line, flush=True)
    open(LOG, "a", encoding="utf-8").write(line + "\n")

def code_of(u):
    m = re.search(r"/p/(V-[A-Za-z0-9]+)", u); return m.group(1) if m else None

def harvest_window(crawls, dom):
    """code -> list of index records across the window's crawls (with retry on index errors)."""
    out = {}
    for c in crawls:
        recs = None
        for attempt in range(4):
            recs = cc.harvest_index(c, dom)
            if recs is not None: break
            log(f"  index error {c}|{dom}, retry {attempt+1}"); time.sleep(30)
        recs = recs or []
        for r in recs:
            k = code_of(r["url"])
            if k: out.setdefault(k, []).append(r)
        log(f"  {c}|{dom}: {len(recs)} product records")
        time.sleep(3)
    return out

def pick(recs_a, recs_b):
    """Prefer captures in the same calendar month (May/May, Jun/Jun, ...); else latest of each."""
    ma = {r["timestamp"][4:6]: r for r in sorted(recs_a, key=lambda r: r["timestamp"])}
    mb = {r["timestamp"][4:6]: r for r in sorted(recs_b, key=lambda r: r["timestamp"])}
    common = set(ma) & set(mb)
    if common:
        m = sorted(common)[0]; return ma[m], mb[m], True
    return sorted(recs_a, key=lambda r: r["timestamp"])[-1], sorted(recs_b, key=lambda r: r["timestamp"])[-1], False

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--window", default="q2"); ap.add_argument("--n", type=int, default=300); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(); W = WINDOWS[a.window]
    out_rows = os.path.join(HERE, f"cc_matched_sku_{a.window}.csv")
    rows = []
    for dom in cc.DOMAINS:
        log(f"{dom}: harvesting window A {W['a']}"); A = harvest_window(W["a"], dom)
        log(f"{dom}: harvesting window B {W['b']}"); B = harvest_window(W["b"], dom)
        matched = sorted(set(A) & set(B))
        log(f"{dom}: {len(A)} codes in A, {len(B)} in B, {len(matched)} matched")
        rng = random.Random(f"{a.window}-{dom}"); sample = rng.sample(matched, min(a.n, len(matched)))
        pairs = [(k,) + pick(A[k], B[k]) for k in sample]
        def work(item):
            k, ra, rb, same_month = item
            pa = cc.fetch_record(ra); pb = cc.fetch_record(rb)
            if not pa or not pb or pa.get("price") is None or pb.get("price") is None: return None
            return dict(domain=dom, code=k, same_month=same_month, ts_a=ra["timestamp"], ts_b=rb["timestamp"],
                        price_a=pa["price"], msrp_a=pa["msrp"], price_b=pb["price"], msrp_b=pb["msrp"],
                        product_type=pb.get("product_type") or pa.get("product_type"), breadcrumb1=pb.get("breadcrumb1") or pa.get("breadcrumb1"),
                        product_category=pb.get("product_category") or pa.get("product_category"), title=pb.get("title") or pa.get("title"), url=rb["url"])
        got, fail = 0, 0
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            for fu in as_completed([ex.submit(work, it) for it in pairs]):
                try: r = fu.result()
                except Exception: r = None
                if r: rows.append(r); got += 1
                else: fail += 1
        log(f"{dom}: fetched {got} matched pairs ({fail} failed)")
        pd.DataFrame(rows).to_csv(out_rows, index=False)
    d = pd.DataFrame(rows)
    if d.empty: log("no rows"); return
    for s_ in ("a", "b"):
        d[f"msrp_{s_}"] = d[f"msrp_{s_}"].fillna(d[f"price_{s_}"])
        d[f"disc_{s_}"] = np.clip(1 - d[f"price_{s_}"] / d[f"msrp_{s_}"], 0, 0.95)
        d[f"on_sale_{s_}"] = d[f"disc_{s_}"] > 0.005
    d["msrp_chg"] = d["msrp_b"] / d["msrp_a"] - 1
    d["price_chg"] = d["price_b"] / d["price_a"] - 1
    txt = (d["title"].fillna("") + " " + d["breadcrumb1"].fillna("") + " " + d["product_category"].fillna("") + " " + d["url"].fillna("")).str.lower()
    d["bucket"] = np.where(d["product_type"].fillna("").str.contains("watch"), "watch", np.where(txt.str.contains(r"engagement|bridal|wedding|anniversary band"), "bridal", "fashion"))
    d["lab_grown"] = txt.str.contains(r"lab[- ]?(?:grown|created)")
    d.to_csv(out_rows, index=False)
    def summ(g):
        return pd.Series(dict(n=len(g), same_month_share=g["same_month"].mean(),
            median_list_chg_pct=g["msrp_chg"].median() * 100, mean_list_chg_pct=g["msrp_chg"].mean() * 100,
            share_list_up=(g["msrp_chg"] > 0.005).mean(), share_list_down=(g["msrp_chg"] < -0.005).mean(),
            median_sale_chg_pct=g["price_chg"].median() * 100, mean_sale_chg_pct=g["price_chg"].mean() * 100,
            breadth_a=g["on_sale_a"].mean(), breadth_b=g["on_sale_b"].mean(),
            depth_a=g.loc[g["on_sale_a"], "disc_a"].mean() if g["on_sale_a"].any() else 0, depth_b=g.loc[g["on_sale_b"], "disc_b"].mean() if g["on_sale_b"].any() else 0,
            discount_factor_a=g["on_sale_a"].mean() * (g.loc[g["on_sale_a"], "disc_a"].mean() if g["on_sale_a"].any() else 0),
            discount_factor_b=g["on_sale_b"].mean() * (g.loc[g["on_sale_b"], "disc_b"].mean() if g["on_sale_b"].any() else 0),
            mean_disc_a=g["disc_a"].mean(), mean_disc_b=g["disc_b"].mean(),
            median_msrp_a=g["msrp_a"].median(), median_msrp_b=g["msrp_b"].median(), median_price_a=g["price_a"].median(), median_price_b=g["price_b"].median()))
    parts = [d.groupby("domain").apply(summ).reset_index().assign(bucket="all"),
             d.groupby(["domain", "bucket"]).apply(summ).reset_index()]
    s = pd.concat(parts, ignore_index=True)
    s["window"] = a.window; s["label_a"] = W["label_a"]; s["label_b"] = W["label_b"]
    s.to_csv(os.path.join(HERE, f"cc_matched_sku_{a.window}_summary.csv"), index=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
    print(s.round(3).to_string(index=False))
    log("finished")

if __name__ == "__main__":
    main()
