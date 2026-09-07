"""Workstream 06: what Airbnb's own fee-inclusive price quotes say about fees and discounting.

Reads : data/raw/inside_airbnb/*_2026-*_listings.csv.gz  (Mar 2026 onward carry `price_quote_raw`,
        the JSON Airbnb returns for a real stay quote: total price, per-night price, and any
        line items -- nightly_subtotal, discount_amount, taxes, cleaning_fee, service_fee)
Writes: data/processed/overnight/06_quote_discount_panel.csv   one row per city-dump
        data/processed/overnight/06_quote_line_items.csv       line-item type frequency by month

Why: the quote block is the only place in any dataset we hold where Airbnb's *displayed total*
is visible. It tests (a) whether cleaning/service fees still appear as separate lines after the
2025 total-price default, and (b) how much of the market is discounting.
Run: py -3.13 analysis/src/overnight/06_quote_panel.py
"""
import collections, glob, json, os, sys
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
OUT = os.path.join(ROOT, "data", "processed", "overnight")
COLS = ["id", "price_quote_raw", "price_quote_checkin_date", "price_quote_checkout_date",
        "price_quote_total_price", "price_quote_price_per_night", "accommodates", "bedrooms",
        "room_type", "host_is_superhost", "instant_bookable", "last_scraped"]


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "data/raw/inside_airbnb/*_2026-*_listings.csv.gz")))
    rows, items = [], []
    for f in files:
        base = os.path.basename(f)
        city, date = base.split("_")[0], base.split("_")[1]
        try:
            d = pd.read_csv(f, usecols=lambda c: c in COLS, low_memory=False)
        except Exception as e:
            print("skip", base, e); continue
        if "price_quote_raw" not in d.columns:
            continue
        c = collections.Counter()
        rec = []
        for _, r in d.iterrows():
            v = r.get("price_quote_raw")
            if not isinstance(v, str):
                continue
            try:
                q = json.loads(v)["quote"]
            except Exception:
                continue
            if not q.get("is_available"):
                continue
            c["quotes"] += 1
            sub = _f(q.get("nightly_subtotal"))
            disc = _f(q.get("discount_amount"))
            tot = _f(q.get("total_price"))
            ppn = _f(q.get("price_per_night"))
            for k in ("service_fee", "cleaning_fee", "taxes", "discount_amount"):
                if q.get(k) not in (None, ""):
                    c["field_" + k] += 1
            for li in (q.get("raw_price_line_items") or []):
                c["li_" + str(li.get("item_type"))] += 1
            ci, co = q.get("requested_checkin_date"), q.get("requested_checkout_date")
            nights = None
            if ci and co:
                nights = (pd.Timestamp(co) - pd.Timestamp(ci)).days
            lead = None
            if ci and isinstance(r.get("last_scraped"), str):
                lead = (pd.Timestamp(ci) - pd.Timestamp(r["last_scraped"])).days
            acc = r.get("accommodates")
            rec.append({"ppn": ppn, "total": tot, "sub": sub, "disc": disc, "nights": nights,
                        "lead": lead, "accommodates": acc, "room_type": r.get("room_type"),
                        "disc_pct": (100.0 * disc / sub) if (disc and sub) else None,
                        "ppppn": (ppn / acc) if (ppn and acc and acc > 0) else None})
        if not rec:
            continue
        t = pd.DataFrame(rec)
        n = len(t)
        eh = t[t["room_type"] == "Entire home/apt"]
        rows.append({
            "city": city, "dump_date": date, "quotes": n,
            "share_with_discount_pct": round(100.0 * t["disc"].notna().sum() / n, 2),
            "median_discount_pct_of_subtotal": _r(t["disc_pct"].median()),
            "mean_discount_pct_of_subtotal": _r(t["disc_pct"].mean()),
            "discount_drag_on_ppn_pct": _r(100.0 * (t["disc"].fillna(0).sum() / t["sub"].sum())) if t["sub"].sum() else None,
            "share_line_cleaning_fee_pct": round(100.0 * c.get("li_cleaning_fee", 0) / n, 3),
            "share_line_service_fee_pct": round(100.0 * c.get("li_service_fee", 0) / n, 3),
            "share_line_taxes_pct": round(100.0 * c.get("li_taxes", 0) / n, 2),
            "median_quote_nights": _r(t["nights"].median()),
            "median_quote_lead_days": _r(t["lead"].median()),
            "median_ppn": _r(t["ppn"].median()),
            "median_ppn_entire": _r(eh["ppn"].median()) if len(eh) else None,
            "median_accommodates": _r(t["accommodates"].median()),
            "median_price_per_person_night": _r(t["ppppn"].median()),
            "median_price_per_person_night_entire": _r(eh["ppppn"].median()) if len(eh) else None,
        })
        items.append({"city": city, "dump_date": date, **{k: v for k, v in c.items()}})
        print(base, n, rows[-1]["share_with_discount_pct"], rows[-1]["median_ppn"])
    os.makedirs(OUT, exist_ok=True)
    pd.DataFrame(rows).sort_values(["city", "dump_date"]).to_csv(os.path.join(OUT, "06_quote_discount_panel.csv"), index=False)
    pd.DataFrame(items).fillna(0).sort_values(["city", "dump_date"]).to_csv(os.path.join(OUT, "06_quote_line_items.csv"), index=False)
    print("wrote", len(rows), "city-dumps")


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _r(x, n=2):
    return None if x is None or pd.isna(x) else round(float(x), n)


if __name__ == "__main__":
    main()
