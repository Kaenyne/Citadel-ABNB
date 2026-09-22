"""origin_language.py — Task D: a QUARTERLY guest-origin proxy from the RAW Inside Airbnb review corpus.

The repo's only Airbnb-side origin object was reviewer language at ANNUAL frequency
(`abnb_party_size_reviews_v2_language_year_shard*.csv`, aggregated into
`origin_proxy_review_language_by_region_year.csv`).  The raw review text IS on this machine
(~/abnb_ia_capture/<country>/<state>/<market>/<dump_date>/reviews.csv.gz, 120 markets, 7.4 GB gz),
so this module rebuilds that object at QUARTER frequency, adds day-matched LTM windows that are
immune to the truncated final quarter, and — because reviews carry `listing_id` — attaches the
reviewed listing's nightly price, which is the first (descriptive) price link for an origin bucket.

Language classifier: imported verbatim from `abnb_party_size_reviews_v2.lang_of`, so the buckets
(de/en/es/fr/it/other/pt/zh_ja_ko) and every judgement call are identical to the annual build.

VINTAGE CAVEAT (load-bearing): Inside Airbnb ships one review file per dump and it contains the
reviews of the listings that were live AT THAT DUMP.  Only ONE dump per market carries reviews here
(119 of 120 in June 2026, Vaud 2026-08-10), so every quarter in this panel is read off a single
vintage.  Shares WITHIN a quarter are clean; LEVELS and growth rates across quarters carry delisting
attrition, which biases early quarters down.  The LTM-window rotation numbers are the same three
day-matched windows off the same vintage, so the attrition bias is common to all three and largely
differences out of a ratio of shares, but not out of a ratio of levels.

Usage
  cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.origin_language
  ... [--workers N] [--rebuild] [--limit N]

Outputs (data/processed/pitch_model_v2/adr_engine/):
  origin_lang_cache_counts.csv      per market x period x lang review counts     (raw-pass cache)
  origin_lang_cache_price.csv       per market x LTM window x lang price stats   (raw-pass cache)
  origin_lang_coverage.csv          one row per market: dump, n reviews, 2Q26 day coverage
  origin_lang_market_quarter.csv    market x quarter x lang: reviews, share, y/y
  origin_lang_region_quarter.csv    region x quarter x lang: reviews, share, y/y (incl. GLOBAL)
  origin_lang_global_quarter.csv    the global composite alone
  origin_lang_rotation_ltm.csv      (a) the origin rotation, day-matched LTM windows, by region
  origin_lang_filings_crosscheck.csv (b) filed origin statements vs the language panel
  origin_lang_price_by_lang.csv     (c) within-market nightly price of the listing reviewed, by lang

Nothing here is fitted and nothing here enters the ADR term; it is a descriptive exhibit.
"""
from __future__ import annotations

import os
import sys
import glob
import unicodedata
import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))          # analysis/src
from abnb_party_size_reviews_v2 import lang_of                         # noqa: E402  exact annual-build classifier

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/pitch_model_v2/adr_engine"
IA = Path.home() / "abnb_ia_capture"
MARKET_MAP = OUT / "market_currency_map.csv"
CAPTURE = OUT / "market_price_levels_capture_2026.csv"                 # carries usd_per_unit per market

LANGS = ["de", "en", "es", "fr", "it", "other", "pt", "zh_ja_ko"]
NON_EN = [l for l in LANGS if l != "en"]
Q_FIRST, Q_LAST = pd.Period("2021Q1", "Q"), pd.Period("2026Q2", "Q")
CLASSIFY_FROM = pd.Timestamp("2021-01-01")                             # y/y for 1Q22 needs 1Q21
CHUNK = 200_000

# Destination-country groups used by the filed-statement cross-checks (countries present in the panel)
SPANISH_DEST = {"spain", "mexico", "argentina", "chile", "colombia"}
PORTUGUESE_DEST = {"brazil", "portugal"}
GERMAN_DEST = {"germany", "austria", "switzerland"}
FRENCH_DEST = {"france", "belgium", "switzerland"}
ITALIAN_DEST = {"italy", "switzerland"}


# ----------------------------------------------------------------------------- raw pass
def market_files():
    """(market_key, dump_date, reviews path, listings path) for every raw review dump on disk."""
    rows = []
    for rp in sorted(glob.glob(str(IA / "*/*/*/*/reviews.csv.gz"))):
        p = Path(rp)
        dump = p.parent.name
        country, state, market = p.parent.parent.parent.parent.name, p.parent.parent.parent.name, p.parent.parent.name
        lp = p.parent / "listings.csv.gz"
        rows.append((f"{country}_{state}_{market}", dump, str(p), str(lp) if lp.exists() else ""))
    return rows


def _listing_price(lst_path):
    """listing_id -> (nightly price in LOCAL currency, accommodates, entire-home flag)."""
    if not lst_path or not os.path.exists(lst_path):
        return None
    use = ("id", "price", "accommodates", "room_type")
    L = pd.read_csv(lst_path, usecols=lambda c: c in use, low_memory=False)
    if "price" not in L.columns:
        return None
    L = L.drop_duplicates("id")
    px = L.price.astype(str).str.replace(r"[^0-9.]", "", regex=True)
    L["price_local"] = pd.to_numeric(px, errors="coerce")
    L.loc[L.price_local <= 0, "price_local"] = np.nan
    L["acc"] = pd.to_numeric(L.get("accommodates"), errors="coerce")
    L["entire"] = (L.get("room_type") == "Entire home/apt").astype(float) if "room_type" in L.columns else np.nan
    return L.set_index("id")[["price_local", "acc", "entire"]]


def process_market(job):
    """One market: stream the review file, classify language, aggregate to quarters and LTM windows."""
    key, dump, rev_path, lst_path = job
    d0 = pd.Timestamp(dump)
    prices = _listing_price(lst_path)
    n_total = 0
    parts = []
    for ch in pd.read_csv(rev_path, usecols=["listing_id", "date", "comments"],
                          chunksize=CHUNK, dtype={"comments": str}, on_bad_lines="skip"):
        n_total += len(ch)
        dt = pd.to_datetime(ch.date, errors="coerce")
        keep = dt.notna() & (dt >= CLASSIFY_FROM) & (dt <= d0)
        if not keep.any():
            continue
        sub = ch.loc[keep]
        c = sub.comments.fillna("").astype(str)
        parts.append(pd.DataFrame({"listing_id": sub.listing_id.to_numpy(),
                                   "dt": dt.loc[keep].to_numpy(),
                                   "lang": c.map(lang_of).to_numpy()}))
    if not parts:
        return key, dump, n_total, pd.DataFrame(), pd.DataFrame()
    d = pd.concat(parts, ignore_index=True)
    d["dt"] = pd.to_datetime(d.dt)

    # --- quarterly counts
    d["q"] = d.dt.dt.to_period("Q")
    q = d[(d.q >= Q_FIRST) & (d.q <= Q_LAST)].groupby([d.q.astype(str), "lang"]).size().rename("reviews").reset_index()
    q.columns = ["period", "lang", "reviews"]
    q.insert(0, "basis", "quarter")

    # --- day-matched LTM windows ending at the dump date (immune to the truncated final quarter)
    age = (d0 - d.dt).dt.days
    d["ltm"] = np.where(age.between(0, 364), "ltm0",
                        np.where(age.between(365, 729), "ltm1",
                                 np.where(age.between(730, 1094), "ltm2",
                                          np.where(age.between(1095, 1459), "ltm3", ""))))
    dl = d[d.ltm != ""]
    l = dl.groupby(["ltm", "lang"]).size().rename("reviews").reset_index()
    l.columns = ["period", "lang", "reviews"]
    l.insert(0, "basis", "ltm")
    counts = pd.concat([q, l], ignore_index=True)
    counts.insert(0, "dump_date", dump)
    counts.insert(0, "market_key", key)

    # --- (c) price of the listing reviewed, by language bucket, LTM windows
    price = pd.DataFrame()
    if prices is not None and len(dl):
        j = prices.reindex(dl.listing_id.to_numpy())
        pj = pd.DataFrame({"period": dl.ltm.to_numpy(), "lang": dl.lang.to_numpy(),
                           "price_local": j.price_local.to_numpy(), "acc": j.acc.to_numpy(),
                           "entire": j.entire.to_numpy(), "listing_id": dl.listing_id.to_numpy()})
        pj["pp_local"] = pj.price_local / pj.acc.replace(0, np.nan)
        g = pj.groupby(["period", "lang"])
        price = pd.DataFrame({
            "n_reviews": g.size(),
            "n_priced": g.price_local.count(),
            "n_listings": g.listing_id.nunique(),
            "price_mean_local": g.price_local.mean(),
            "price_median_local": g.price_local.median(),
            "pp_mean_local": g.pp_local.mean(),
            "pp_median_local": g.pp_local.median(),
            "entire_share": g.entire.mean(),
        }).reset_index()
        price.insert(0, "dump_date", dump)
        price.insert(0, "market_key", key)
    return key, dump, n_total, counts, price


def raw_pass(workers, rebuild, limit):
    cc, cp = OUT / "origin_lang_cache_counts.csv", OUT / "origin_lang_cache_price.csv"
    jobs = market_files()
    if limit:
        jobs = jobs[:limit]
    done = set()
    if cc.exists() and not rebuild:
        done = set(pd.read_csv(cc, usecols=["market_key"]).market_key.unique())
    todo = [j for j in jobs if j[0] not in done]
    print(f"raw pass: {len(jobs)} review dumps on disk, {len(done)} cached, {len(todo)} to read", flush=True)
    if todo:
        import multiprocessing as mp
        C, P, cov = [], [], []
        ctx = mp.get_context("fork")
        with ctx.Pool(workers) as pool:
            for i, (key, dump, n_total, counts, price) in enumerate(pool.imap_unordered(process_market, todo), 1):
                print(f"  [{i}/{len(todo)}] {key} {dump} n_raw={n_total:,}", flush=True)
                if len(counts):
                    C.append(counts)
                if len(price):
                    P.append(price)
                cov.append({"market_key": key, "dump_date": dump, "reviews_all_time": n_total})
        if C:
            new = pd.concat(C, ignore_index=True)
            if cc.exists() and not rebuild:
                new = pd.concat([pd.read_csv(cc), new], ignore_index=True)
            new.to_csv(cc, index=False)
        if P:
            newp = pd.concat(P, ignore_index=True)
            if cp.exists() and not rebuild:
                newp = pd.concat([pd.read_csv(cp), newp], ignore_index=True)
            newp.to_csv(cp, index=False)
    counts = pd.read_csv(cc)
    price = pd.read_csv(cp) if cp.exists() else pd.DataFrame()
    return counts, price


# ----------------------------------------------------------------------------- aggregation
def _nk(s: str) -> str:
    """Normalised market key: the capture store spells Tokyo `japan_kantō_tokyo`, the engine's
    market_currency_map.csv spells it `japan_kanto_tokyo`. Strip accents so the two meet."""
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


def region_map():
    m = pd.read_csv(MARKET_MAP)
    m["_k"] = m.market_key.map(_nk)
    return m.drop_duplicates("_k").set_index("_k")[["country", "region", "currency"]]


def attach_region(df, rm):
    """Left-join country/region on the accent-stripped market key; UNMAPPED if absent."""
    d = df.copy()
    d["_k"] = d.market_key.map(_nk)
    d = d.merge(rm, left_on="_k", right_index=True, how="left").drop(columns="_k")
    d["region"] = d.region.fillna("UNMAPPED")
    d["country"] = d.country.fillna("unmapped")
    return d


def _share_yoy(df, keys):
    """shares within (keys + period) and y/y growth of levels and of shares, quarter basis."""
    tot = df.groupby(keys + ["period"], as_index=False).reviews.sum().rename(columns={"reviews": "tot"})
    d = df.merge(tot, on=keys + ["period"])
    d["share_pct"] = 100 * d.reviews / d.tot
    d["_p"] = pd.PeriodIndex(d.period, freq="Q")
    prev = d[keys + ["lang", "_p", "reviews", "share_pct"]].copy()
    prev["_p"] = prev._p + 4
    prev = prev.rename(columns={"reviews": "reviews_lag4", "share_pct": "share_pct_lag4"})
    d = d.merge(prev, on=keys + ["lang", "_p"], how="left")
    d["yoy_pct"] = 100 * (d.reviews / d.reviews_lag4 - 1)
    d["share_chg_pp"] = d.share_pct - d.share_pct_lag4
    return d.drop(columns="_p")


def build_quarterly(counts, rm):
    q = attach_region(counts[counts.basis == "quarter"], rm)
    mkt = _share_yoy(q.groupby(["market_key", "country", "region", "dump_date", "period", "lang"],
                               as_index=False).reviews.sum(),
                     ["market_key", "country", "region", "dump_date"])
    reg = _share_yoy(q.groupby(["region", "period", "lang"], as_index=False).reviews.sum(), ["region"])
    g = q.groupby(["period", "lang"], as_index=False).reviews.sum()
    g.insert(0, "region", "GLOBAL")
    glob_ = _share_yoy(g, ["region"])
    return mkt, pd.concat([reg, glob_], ignore_index=True), glob_


def build_rotation(counts, rm):
    """(a) the origin rotation on day-matched LTM windows: ltm2 = year to mid-2024, ltm0 = year to mid-2026."""
    l = attach_region(counts[counts.basis == "ltm"], rm)
    rows = []
    for reg, sub in list(l.groupby("region")) + [("GLOBAL", l)]:
        w = sub.pivot_table(index="lang", columns="period", values="reviews", aggfunc="sum").fillna(0)
        for c in ("ltm0", "ltm1", "ltm2"):
            if c not in w.columns:
                w[c] = 0.0
        tot = w.sum()
        for lang in w.index:
            r = w.loc[lang]
            rows.append({
                "region": reg, "lang": lang,
                "reviews_ltm_2024": r.ltm2, "reviews_ltm_2025": r.ltm1, "reviews_ltm_2026": r.ltm0,
                "share_pct_2024": 100 * r.ltm2 / tot.ltm2 if tot.ltm2 else np.nan,
                "share_pct_2025": 100 * r.ltm1 / tot.ltm1 if tot.ltm1 else np.nan,
                "share_pct_2026": 100 * r.ltm0 / tot.ltm0 if tot.ltm0 else np.nan,
                "growth_pct_24_26": 100 * (r.ltm0 / r.ltm2 - 1) if r.ltm2 else np.nan,
                "growth_pct_25_26": 100 * (r.ltm0 / r.ltm1 - 1) if r.ltm1 else np.nan,
            })
        # English vs everything else
        en = w.loc["en"] if "en" in w.index else pd.Series(0.0, index=w.columns)
        ne = tot - en
        rows.append({"region": reg, "lang": "ALL_NON_EN",
                     "reviews_ltm_2024": ne.ltm2, "reviews_ltm_2025": ne.ltm1, "reviews_ltm_2026": ne.ltm0,
                     "share_pct_2024": 100 * ne.ltm2 / tot.ltm2 if tot.ltm2 else np.nan,
                     "share_pct_2025": 100 * ne.ltm1 / tot.ltm1 if tot.ltm1 else np.nan,
                     "share_pct_2026": 100 * ne.ltm0 / tot.ltm0 if tot.ltm0 else np.nan,
                     "growth_pct_24_26": 100 * (ne.ltm0 / ne.ltm2 - 1) if ne.ltm2 else np.nan,
                     "growth_pct_25_26": 100 * (ne.ltm0 / ne.ltm1 - 1) if ne.ltm1 else np.nan})
        rows.append({"region": reg, "lang": "TOTAL",
                     "reviews_ltm_2024": tot.ltm2, "reviews_ltm_2025": tot.ltm1, "reviews_ltm_2026": tot.ltm0,
                     "share_pct_2024": 100.0, "share_pct_2025": 100.0, "share_pct_2026": 100.0,
                     "growth_pct_24_26": 100 * (tot.ltm0 / tot.ltm2 - 1) if tot.ltm2 else np.nan,
                     "growth_pct_25_26": 100 * (tot.ltm0 / tot.ltm1 - 1) if tot.ltm1 else np.nan})
    return pd.DataFrame(rows)


def build_crosscheck(counts, rm):
    """(b) the filed origin statements against the language panel, cross-border only."""
    l = attach_region(counts[counts.basis == "ltm"], rm)

    def block(label, lang, mask, filed, filed_ltm=np.nan):
        sub = l[(l.lang == lang) & mask]
        tot = l[mask]
        w = sub.groupby("period").reviews.sum()
        t = tot.groupby("period").reviews.sum()
        g = lambda a, b: 100 * (w.get(a, 0) / w.get(b, np.nan) - 1) if w.get(b, 0) else np.nan
        gt = lambda a, b: 100 * (t.get(a, 0) / t.get(b, np.nan) - 1) if t.get(b, 0) else np.nan
        # levels off a single vintage are inflated by delisting attrition; the attrition is common to the
        # scope, so the interpretable statistic is the language's growth MINUS the scope's own growth.
        return {"check": label, "lang": lang, "filed_statement": filed, "filed_ltm_yoy_pct": filed_ltm,
                "scope_growth_pct_25_26": gt("ltm0", "ltm1"), "scope_growth_pct_24_26": gt("ltm0", "ltm2"),
                "excess_pp_25_26": g("ltm0", "ltm1") - gt("ltm0", "ltm1"),
                "excess_pp_24_26": g("ltm0", "ltm2") - gt("ltm0", "ltm2"),
                "n_markets": sub.market_key.nunique(),
                "reviews_ltm_2024": w.get("ltm2", 0), "reviews_ltm_2025": w.get("ltm1", 0),
                "reviews_ltm_2026": w.get("ltm0", 0),
                "share_of_scope_pct_2024": 100 * w.get("ltm2", 0) / t.get("ltm2", np.nan) if t.get("ltm2", 0) else np.nan,
                "share_of_scope_pct_2026": 100 * w.get("ltm0", 0) / t.get("ltm0", np.nan) if t.get("ltm0", 0) else np.nan,
                "growth_pct_25_26": g("ltm0", "ltm1"), "growth_pct_24_26": g("ltm0", "ltm2")}

    rows = [
        block("Brazil origin: pt reviews OUTSIDE Brazil/Portugal", "pt",
              ~l.country.isin(PORTUGUESE_DEST), "Brazil origin nights 4Q25 +21 / 1Q26 +21 / 2Q26 +31 (letters)", 23.5),
        block("Brazil origin: pt reviews INSIDE Brazil/Portugal (domestic control)", "pt",
              l.country.isin(PORTUGUESE_DEST), "control: domestic/near-domestic Portuguese"),
        block("LatAm origin: es reviews OUTSIDE Spanish-speaking destinations", "es",
              ~l.country.isin(SPANISH_DEST), "LatAm domestic nights +24/+21/+30 (2Q24-4Q24); LatAm ~20% of nights", np.nan),
        block("LatAm origin: es reviews INSIDE Spanish-speaking destinations (control)", "es",
              l.country.isin(SPANISH_DEST), "control: domestic/intra-Hispanophone Spanish"),
        block("East-Asian outbound: zh_ja_ko reviews OUTSIDE APAC", "zh_ja_ko",
              l.region != "APAC", "China outbound +80 (1Q24) then +25 (4Q24); Japan origin high-teens 2Q26", np.nan),
        block("East-Asian outbound: zh_ja_ko reviews INSIDE APAC (control)", "zh_ja_ko",
              l.region == "APAC", "control: intra-APAC East-Asian"),
        block("India origin: NOT IDENTIFIABLE (Indian guests write English)", "en",
              l.region != "UNMAPPED", "India origin 4Q25 +50 / 1Q26 +50 / 2Q26 +60 — INVISIBLE in this object", 53.3),
    ]
    return pd.DataFrame(rows)


def build_price(price, counts, rm, min_reviews=20):
    """(c) within-market nightly price of the listing reviewed, by language bucket, LTM to the dump."""
    if not len(price):
        return pd.DataFrame()
    p = attach_region(price[price.period == "ltm0"], rm)
    cap = pd.read_csv(CAPTURE, usecols=["market_key", "usd_per_unit"])
    cap["_k"] = cap.market_key.map(_nk)
    cap = cap.drop_duplicates("_k").set_index("_k").usd_per_unit
    p["usd_per_unit"] = p.market_key.map(_nk).map(cap)
    base = p[p.lang == "en"].set_index("market_key")[["price_median_local", "pp_median_local", "n_reviews"]]
    p["en_price_median_local"] = p.market_key.map(base.price_median_local)
    p["en_pp_median_local"] = p.market_key.map(base.pp_median_local)
    p["en_n_reviews"] = p.market_key.map(base.n_reviews)
    p["rel_price_vs_en"] = p.price_median_local / p.en_price_median_local
    p["rel_pp_vs_en"] = p.pp_median_local / p.en_pp_median_local
    p["price_median_usd"] = p.price_median_local * p.usd_per_unit
    tot = p.groupby("market_key").n_reviews.sum().rename("market_reviews_ltm")
    p = p.merge(tot, on="market_key")
    p["lang_share_pct"] = 100 * p.n_reviews / p.market_reviews_ltm
    p = p[p.n_reviews >= min_reviews]
    return p.sort_values(["market_reviews_ltm", "lang"], ascending=[False, True])


def build_mix_effect(price, counts, rm, min_n=20):
    """The rotation priced, descriptively: hold each language's median nightly price at its LTM-2026 level
    inside each market and move only the language SHARES from the LTM-2024 window to the LTM-2026 window.
    The result is the change in the review-weighted price of the listing reviewed that the origin rotation
    alone explains, within market, with no cross-market or cross-currency comparison anywhere in it."""
    if not len(price):
        return pd.DataFrame(), pd.DataFrame()
    px = price[(price.period == "ltm0") & (price.n_reviews >= min_n) & price.price_median_local.notna()]
    px = px[["market_key", "lang", "price_median_local", "pp_median_local"]]
    sh = counts[counts.basis == "ltm"].pivot_table(index=["market_key", "lang"], columns="period",
                                                   values="reviews", aggfunc="sum").reset_index()
    for c in ("ltm0", "ltm1", "ltm2"):
        if c not in sh.columns:
            sh[c] = 0.0
    d = px.merge(sh, on=["market_key", "lang"], how="left").fillna({"ltm0": 0, "ltm1": 0, "ltm2": 0})
    rows = []
    for mk, g in d.groupby("market_key"):
        if len(g) < 2 or g.ltm2.sum() == 0 or g.ltm0.sum() == 0:
            continue
        w0, w1, w2 = g.ltm0 / g.ltm0.sum(), g.ltm1 / g.ltm1.sum(), g.ltm2 / g.ltm2.sum()
        P = lambda w, col: float((w * g[col]).sum())
        rows.append({"market_key": mk, "n_langs": len(g), "reviews_ltm_2026": float(g.ltm0.sum()),
                     "price_idx_2024": P(w2, "price_median_local"), "price_idx_2025": P(w1, "price_median_local"),
                     "price_idx_2026": P(w0, "price_median_local"),
                     "mix_pct_24_26": 100 * (P(w0, "price_median_local") / P(w2, "price_median_local") - 1),
                     "mix_pct_25_26": 100 * (P(w0, "price_median_local") / P(w1, "price_median_local") - 1),
                     "mix_pp_pct_24_26": 100 * (P(w0, "pp_median_local") / P(w2, "pp_median_local") - 1),
                     "mix_pp_pct_25_26": 100 * (P(w0, "pp_median_local") / P(w1, "pp_median_local") - 1)})
    m = attach_region(pd.DataFrame(rows), rm)
    agg = []
    for reg, sub in list(m.groupby("region")) + [("GLOBAL", m)]:
        w = sub.reviews_ltm_2026
        agg.append({"region": reg, "n_markets": len(sub),
                    "mix_pct_24_26_wtd": float((sub.mix_pct_24_26 * w).sum() / w.sum()),
                    "mix_pct_25_26_wtd": float((sub.mix_pct_25_26 * w).sum() / w.sum()),
                    "mix_pp_pct_24_26_wtd": float((sub.mix_pp_pct_24_26 * w).sum() / w.sum()),
                    "mix_pct_24_26_median": float(sub.mix_pct_24_26.median()),
                    "n_markets_negative": int((sub.mix_pct_24_26 < 0).sum())})
    return m, pd.DataFrame(agg)


def price_summary(pl):
    """Pooled: within a market, how does the listing reviewed in language L price against the English one?"""
    if not len(pl):
        return pd.DataFrame()
    d = pl[pl.lang != "en"].dropna(subset=["rel_price_vs_en"])
    d = d[(d.n_reviews >= 100) & (d.en_n_reviews >= 100)]
    g = d.groupby("lang")
    return pd.DataFrame({
        "n_markets": g.size(),
        "rel_price_vs_en_median": g.rel_price_vs_en.median(),
        "rel_price_vs_en_wtd": g.apply(lambda x: float((x.rel_price_vs_en * x.n_reviews).sum() / x.n_reviews.sum()),
                                       include_groups=False),
        "rel_pp_vs_en_median": g.rel_pp_vs_en.median(),
        "markets_cheaper_than_en": g.apply(lambda x: int((x.rel_price_vs_en < 1).sum()), include_groups=False),
        "total_reviews_ltm_2026": g.n_reviews.sum(),
    }).reset_index()


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=max(1, min(8, (os.cpu_count() or 4) - 2)))
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    OUT.mkdir(parents=True, exist_ok=True)

    counts, price = raw_pass(a.workers, a.rebuild, a.limit)
    rm = region_map()

    # coverage
    cov = counts[counts.basis == "quarter"].groupby(["market_key", "dump_date"], as_index=False).reviews.sum()
    cov = attach_region(cov, rm)
    d0 = pd.to_datetime(cov.dump_date)
    qs = d0.dt.to_period("Q").dt.start_time
    cov["final_quarter"] = d0.dt.to_period("Q").astype(str)
    cov["final_quarter_day_coverage"] = ((d0 - qs).dt.days + 1) / (d0.dt.to_period("Q").dt.end_time - qs).dt.days.add(1)
    cov["reviews_2021q1_2026q2"] = cov.reviews
    cov.drop(columns="reviews").to_csv(OUT / "origin_lang_coverage.csv", index=False)

    mkt, reg, glob_ = build_quarterly(counts, rm)
    mkt.to_csv(OUT / "origin_lang_market_quarter.csv", index=False)
    reg.to_csv(OUT / "origin_lang_region_quarter.csv", index=False)
    glob_.to_csv(OUT / "origin_lang_global_quarter.csv", index=False)
    rot = build_rotation(counts, rm)
    rot.to_csv(OUT / "origin_lang_rotation_ltm.csv", index=False)
    xc = build_crosscheck(counts, rm)
    xc.to_csv(OUT / "origin_lang_filings_crosscheck.csv", index=False)
    pl = build_price(price, counts, rm)
    ps = mix_m = mix_r = pd.DataFrame()
    if len(pl):
        pl.to_csv(OUT / "origin_lang_price_by_lang.csv", index=False)
        ps = price_summary(pl)
        ps.to_csv(OUT / "origin_lang_price_summary.csv", index=False)
        mix_m, mix_r = build_mix_effect(price, counts, rm)
        if len(mix_m):
            mix_m.to_csv(OUT / "origin_lang_price_mix_market.csv", index=False)
            mix_r.to_csv(OUT / "origin_lang_price_mix_effect.csv", index=False)

    print("\n=== coverage ===")
    print(f"markets {cov.market_key.nunique()}  reviews 2021Q1-2026Q2 {int(cov.reviews_2021q1_2026q2.sum()):,}")
    print(cov.groupby("region").agg(markets=("market_key", "nunique"),
                                    reviews=("reviews_2021q1_2026q2", "sum")).to_string())
    print("\n=== GLOBAL share_pct by quarter (last 8q) ===")
    piv = glob_.pivot_table(index="period", columns="lang", values="share_pct").tail(8).round(2)
    print(piv.to_string())
    print("\n=== rotation, LTM to the dump (GLOBAL + regions) ===")
    print(rot[rot.lang.isin(["en", "ALL_NON_EN", "es", "pt", "zh_ja_ko", "other", "TOTAL"])]
          .round(2).to_string(index=False))
    print("\n=== filings cross-check ===")
    print(xc.round(2).to_string(index=False))
    if len(ps):
        print("\n=== price of the listing reviewed, relative to the same market's English reviews ===")
        print(ps.round(3).to_string(index=False))
    if len(mix_r):
        print("\n=== rotation priced: language-mix effect on the within-market price of the listing reviewed ===")
        print(mix_r.round(3).to_string(index=False))
    if len(pl):
        print("\n=== price by language, 10 largest markets ===")
        top = pl.market_key.drop_duplicates().head(10)
        print(pl[pl.market_key.isin(top)][["market_key", "region", "lang", "n_reviews", "lang_share_pct",
                                           "price_median_local", "rel_price_vs_en", "rel_pp_vs_en"]]
              .round(3).to_string(index=False))
    print("\ndone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
