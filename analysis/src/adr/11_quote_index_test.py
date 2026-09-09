"""11. Can a quote-based price index track Airbnb's disclosed regional ADR?

The question
  A proposal on the table is to collect Airbnb quotes at scale (agents browsing listings)
  to build a sub-regional ADR series. Before spending on collection, the cheap test: Inside
  Airbnb already holds listing-level quotes for 34 markets. Build the best quote index the
  data allows and test it against the ADR y/y Airbnb actually discloses by region. If quotes
  cannot track disclosed regional ADR here, collecting more of them cannot either, because
  the collected quantity is the same.

What is built
  Two panels of year-over-year quote pairs, priced in local currency (so the comparator is
  constant-currency ADR, not reported):
  A. SAME BASIS. Pairs where both dumps carry the pre-Oct-2025 listed nightly rate and both
     are full-scope scrapes (the repo's `price_pair_eligible`). 13 pairs, four cities.
  B. CROSS BASIS. A 2025 listed-rate dump against the 2026 quote dump ~12 months later, for
     every market that has both. The 2026 quote is a stay-specific nightly rate (the raw
     quote carries no service fee, cleaning fee or tax lines in these dumps -- checked --
     so the wedge against the 2025 listed rate is date and stay-length selection, not fees).
     Reported with that caveat; it is the only route to a four-region cross-section.
  Five index constructions per pair, from the crude to the ADR-like:
     med_matched      median log price change on listings present in both dumps (the repo's
                      existing like-for-like series, survivors only, unweighted)
     wmean_matched    the same, weighted by year-ago estimated nights booked
     wmean_all_arith  nights-weighted arithmetic mean price, all priced listings, each dump
                      on its own -- the closest analogue to ADR = GBV / nights, composition
                      change included
     wmean_all_log    nights-weighted mean log price, all listings
     umean_all        unweighted mean price, all listings (what a random-click sample gives)
  Each is tested against the disclosed regional ADR ex-FX y/y for the quarter of the later
  dump (and, as a robustness check, the following quarter), and against global ADR ex-FX.

Outputs
  data/processed/adr/11_quote_index_pairs.csv   one row per pair x segment, all indices
  data/processed/adr/11_quote_index_test.csv    correlations, n, MAE per index x comparator
Run
  py -3.13 analysis/src/adr/11_quote_index_test.py <dump_inventory.csv>
"""
import glob
import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats

RAW = "data/raw/inside_airbnb"
OUT = "data/processed/adr"
LFL = "data/processed/inside_airbnb_like_for_like.csv"
REGQ = "data/processed/adr/04_regional_quarterly.csv"
HIST = "data/processed/adr/02b_adr_history_extended.csv"
SNAP = "data/processed/inside_airbnb_city_snapshots.csv"
CAP = 0.7 * 365
YOY_LO, YOY_HI = 300, 430

REGION = {"new-york-city": "na", "los-angeles": "na", "chicago": "na", "austin": "na",
          "nashville": "na", "new-orleans": "na", "san-diego": "na", "paris": "emea",
          "london": "emea", "barcelona": "emea", "rome": "emea", "sydney": "apac",
          "mexico-city": "latam", "bangkok": "apac", "tokyo": "apac", "taipei": "apac",
          "singapore": "apac", "hong-kong": "apac", "brisbane": "apac", "melbourne": "apac",
          "barossa-valley": "apac", "barwon-south-west-vic": "apac", "mid-north-coast": "apac",
          "mornington-peninsula": "apac", "northern-rivers": "apac", "sunshine-coast": "apac",
          "tasmania": "apac", "western-australia": "apac", "belize": "latam",
          "rio-de-janeiro": "latam", "santiago": "latam", "buenos-aires": "latam",
          "bogota": "latam", "sao-paulo": "latam"}
IDX = ["med_matched", "wmean_matched", "wmean_all_arith", "wmean_all_log", "umean_all"]


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def parse_price(s):
    if s.dtype.kind in "fi":
        return s.astype(float)
    return pd.to_numeric(s.astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")


def booking_weight(df):
    """Estimated nights booked, trailing 365 days (05's convention)."""
    d = pd.to_numeric(df["estimated_occupancy_l365d"], errors="coerce")
    if d.notna().mean() >= 0.5:
        return d.fillna(0).clip(0, CAP)
    per_stay = np.maximum(3, pd.to_numeric(df["minimum_nights"], errors="coerce").fillna(1).clip(upper=30))
    return np.minimum(pd.to_numeric(df["number_of_reviews_ltm"], errors="coerce").fillna(0) / 0.5 * per_stay, CAP)


def quote_base(s):
    """Undiscounted nightly subtotal from the raw quote, or NaN (monthly quotes carry none)."""
    try:
        q = (json.loads(s) or {}).get("quote") or {}
        for it in q.get("raw_price_line_items") or []:
            if it.get("item_type") == "nightly_subtotal":
                return float(it["amount"])
    except Exception:
        return np.nan
    return np.nan


def load(market, date, basis):
    """One dump -> id, room_type, price (local ccy), price_base, nights, weight."""
    f = f"{RAW}/{market}_{date}_listings"
    cols = ["id", "room_type", "price", "estimated_occupancy_l365d", "minimum_nights",
            "number_of_reviews_ltm", "accommodates"]
    if basis == "listed":
        if os.path.exists(f + ".parquet"):
            df = pd.read_parquet(f + ".parquet", columns=cols)
        else:
            df = pd.read_csv(f + ".csv.gz", usecols=cols, low_memory=False)
        df["price"] = parse_price(df["price"])
        df["price_base"] = df["price"]
        df["nights"] = np.nan
    else:
        df = pd.read_csv(f + ".csv.gz", usecols=cols + ["price_quote_checkin_date",
                         "price_quote_checkout_date", "price_quote_price_per_night",
                         "price_quote_raw"], low_memory=False)
        df["price"] = pd.to_numeric(df["price_quote_price_per_night"], errors="coerce")
        df["nights"] = (pd.to_datetime(df["price_quote_checkout_date"], errors="coerce")
                        - pd.to_datetime(df["price_quote_checkin_date"], errors="coerce")).dt.days
        sub = df["price_quote_raw"].map(quote_base, na_action="ignore")
        df["price_base"] = sub / df["nights"].where(df["nights"] > 0)
        df = df.drop(columns=["price_quote_checkin_date", "price_quote_checkout_date",
                              "price_quote_price_per_night", "price_quote_raw"])
    df["w"] = booking_weight(df)
    df["entire"] = df["room_type"].eq("Entire home/apt")
    return df


def clean(p):
    p = p.where((p >= 10) & (p <= 10000))
    lo, hi = p.quantile([0.01, 0.99])
    return p.clip(lo, hi)


def indices(a, b, seg, pcol):
    """All five constructions for one segment (entire homes or all listings)."""
    if seg == "entire":
        a, b = a[a.entire], b[b.entire]
    a = a.assign(p=clean(a[pcol])).dropna(subset=["p"])
    b = b.assign(p=clean(b[pcol])).dropna(subset=["p"])
    if len(a) < 300 or len(b) < 300:
        return None
    r = {}
    wa, wb = a.w.sum(), b.w.sum()
    r["wmean_all_arith"] = ((b.w * b.p).sum() / wb) / ((a.w * a.p).sum() / wa) - 1
    r["wmean_all_log"] = np.exp((b.w * np.log(b.p)).sum() / wb - (a.w * np.log(a.p)).sum() / wa) - 1
    r["umean_all"] = b.p.mean() / a.p.mean() - 1
    m = a[["id", "p", "w"]].merge(b[["id", "p"]], on="id", suffixes=("_a", "_b"))
    lr = np.log(m.p_b / m.p_a)
    r["med_matched"] = np.exp(lr.median()) - 1
    r["wmean_matched"] = np.exp((m.w * lr).sum() / m.w.sum()) - 1 if m.w.sum() > 0 else np.nan
    r.update(n_a=len(a), n_b=len(b), n_matched=len(m), share_matched_a=len(m) / len(a),
             nights_a=float(wa), nights_b=float(wb), level_a=(a.w * a.p).sum() / wa,
             level_b=(b.w * b.p).sum() / wb)
    return r


def quarter(d):
    d = pd.Timestamp(d)
    return f"{(d.month - 1) // 3 + 1}Q{d.year % 100:02d}"


def next_quarter(q):
    n, y = int(q[0]), int(q[2:])
    return f"{n + 1}Q{y:02d}" if n < 4 else f"1Q{y + 1:02d}"


def build_pairs(inv_path):
    lfl = pd.read_csv(LFL)
    same = lfl[lfl.pair_type.eq("year_ago") & lfl.price_pair_eligible.eq(True)
               & lfl.price_basis_a.eq("listed_nightly") & lfl.price_basis_b.eq("listed_nightly")]
    pairs = [dict(market=r.city, date_a=r.date_a, date_b=r.date_b, panel="A_same_basis",
                  basis_a="listed", basis_b="listed", scope_ok=True) for r in same.itertuples()]
    log(f"panel A pairs: {len(pairs)}")

    # panel B: every market's 2025 listed dumps vs the 2026 quote dump nearest 365 days on
    snap = pd.read_csv(SNAP)
    scope = {(r.city, r.dump_date): bool(r.partial_scope) for r in snap.itertuples()}
    inv = pd.read_csv(inv_path)
    inv["basis"] = np.where((inv.price_nn > 0.3) & (inv.quote_nn <= 0), "listed",
                            np.where(inv.quote_nn > 0.3, "quote", "none"))
    inv["date"] = pd.to_datetime(inv["date"])
    for mk, g in inv.groupby("market"):
        listed = g[g.basis.eq("listed") & (g.date >= "2025-05-01")]
        quotes = g[g.basis.eq("quote")]
        for a in listed.itertuples():
            cand = quotes.assign(gap=(quotes.date - a.date).dt.days)
            cand = cand[(cand.gap >= YOY_LO) & (cand.gap <= YOY_HI)]
            if cand.empty:
                continue
            b = cand.iloc[(cand.gap - 365).abs().argsort().iloc[0]]
            da, db = a.date.strftime("%Y-%m-%d"), b.date.strftime("%Y-%m-%d")
            ps, pb = scope.get((mk, da)), scope.get((mk, db))
            if ps is not None and pb is not None:
                ok = (not ps) and (not pb)
            else:
                ok = 0.75 <= b.n / a.n <= 1.35
            pairs.append(dict(market=mk, date_a=da, date_b=db, panel="B_cross_basis",
                              basis_a="listed", basis_b="quote", scope_ok=bool(ok),
                              n_listings_a=int(a.n), n_listings_b=int(b.n)))
    log(f"panel A+B pairs: {len(pairs)}")
    return pairs


def main():
    pairs = build_pairs(sys.argv[1])
    cache = {}

    def get(mk, d, basis):
        k = (mk, d)
        if k not in cache:
            cache[k] = load(mk, d, basis)
        return cache[k]

    rows = []
    for p in pairs:
        a = get(p["market"], p["date_a"], p["basis_a"])
        b = get(p["market"], p["date_b"], p["basis_b"])
        for seg in ("entire", "all"):
            for pcol, tag in (("price", "quote_pn"), ("price_base", "base_rate_le7n")):
                if p["panel"] == "A_same_basis" and tag != "quote_pn":
                    continue
                bb = b[b.nights.le(7)] if tag == "base_rate_le7n" else b
                r = indices(a, bb, seg, pcol)
                if r is None:
                    continue
                r.update(p, segment=seg, price_measure=tag, region=REGION.get(p["market"], "?"),
                         quarter=quarter(p["date_b"]))
                rows.append(r)
        log(f"{p['market']} {p['date_a']} -> {p['date_b']} done")
        cache.pop((p["market"], p["date_a"]), None)
    pr = pd.DataFrame(rows)
    for c in IDX:
        pr[c] = pr[c] * 100

    rq = pd.read_csv(REGQ)
    rq = rq[rq.metric.eq("adr_yoy_exfx_pct") & rq.basis.str.contains("disclosed")]
    reg = rq.pivot_table(index="quarter", columns="region", values="value")
    hist = pd.read_csv(HIST).set_index("quarter")["adr_yoy_exfx_final"]

    def look(r, q):
        return reg[r].get(q, np.nan) if r in reg.columns else np.nan
    pr["disclosed_regional_exfx"] = [look(r, q) for r, q in zip(pr.region, pr.quarter)]
    pr["disclosed_regional_exfx_next_q"] = [look(r, next_quarter(q)) for r, q in zip(pr.region, pr.quarter)]
    pr["global_exfx"] = pr.quarter.map(hist)
    pr.to_csv(f"{OUT}/11_quote_index_pairs.csv", index=False)

    tests = []
    for panel in ("A_same_basis", "B_cross_basis", "A+B"):
        sub = pr if panel == "A+B" else pr[pr.panel.eq(panel)]
        sub = sub[sub.scope_ok]
        for seg in ("entire", "all"):
            for pm in sub.price_measure.unique():
                s = sub[sub.segment.eq(seg) & sub.price_measure.eq(pm)]
                for comp in ("disclosed_regional_exfx", "disclosed_regional_exfx_next_q", "global_exfx"):
                    for c in IDX:
                        d = s[[c, comp]].dropna()
                        if len(d) < 4:
                            continue
                        pr_, pp = stats.pearsonr(d[c], d[comp])
                        sr, sp = stats.spearmanr(d[c], d[comp])
                        tests.append(dict(panel=panel, segment=seg, price_measure=pm, comparator=comp,
                                          index=c, n=len(d), pearson_r=pr_, pearson_p=pp,
                                          spearman_r=sr, spearman_p=sp,
                                          mae_pp=(d[c] - d[comp]).abs().mean(),
                                          bias_pp=(d[c] - d[comp]).mean(),
                                          sign_agree=((d[c] > 0) == (d[comp] > 0)).mean()))
    te = pd.DataFrame(tests)
    te.to_csv(f"{OUT}/11_quote_index_test.csv", index=False)

    pd.set_option("display.width", 250)
    show = ["panel", "market", "region", "quarter", "segment", "price_measure", "scope_ok",
            "n_matched"] + IDX + ["disclosed_regional_exfx", "global_exfx"]
    print(pr[show].round(1).to_string())
    print(te[te.comparator.eq("disclosed_regional_exfx")].round(3).to_string())
    print(te[te.comparator.ne("disclosed_regional_exfx")].round(3).to_string())


if __name__ == "__main__":
    main()
