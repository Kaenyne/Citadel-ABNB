"""E_attrition: an attrition ladder for the reviews stays index from the 2015-2019 Inside Airbnb archives.

Build B of the GitHub alt-data catalogue (docs/github-altdata/integration_plan_raw.json, lane
'Gap 1: pre-2023 Inside Airbnb archives'). Pre-registration and results:
docs/revenue-forecast-strategy/05_backtests/WPK_reviews-attrition-ladder-2015-2019.md

What it does
  1. Counts reviews by listing x month (listing_id, date only) for every archive vintage:
       montera34/airbnb.barcelona      33 Barcelona vintages 2015-04-30 .. 2019-03-08 (folder 180619 is DataHippo, excluded) (reviews_summary)
       ChicagoBoothML/DATA___InsideAirBnB  30 cities, one vintage each Jun-Nov 2015 (reviews.csv.gz)
       JoeyDeJager/inside-airbnb-data  NYC 2015-01-01 (visualizations/nyc_reviews_*.csv)
  2. Maps archive city names to the E note's market_key via market_geo.csv (unmatched are reported).
  3. Held side = data/processed/q3nowcast/E/market_vintage_monthly.csv, latest dump_date per market
     (E3 count, same listing x month grain). Attrition ratio = n_held / n_archive for the same market
     and review month; age_months = months between the archive dump and the held dump.
  4. Intra-archive pairs inside montera34 (every early < late vintage pair) fill the 1-47 month rungs.
  5. Pooled table by age bucket (0-12, 13-24, ... months) with n and review-weighted ratio.
  6. Evaluates the pre-registered lines L1, L2, L3; writes the Barcelona supply exhibit and the raw manifest.

Raw stores (outside git): C:/Users/krish/abnb_ia_capture/{montera34_barcelona, chicagobooth_2015, joeydejager_nyc_2015}
Outputs: data/processed/q3nowcast/../q3nowcast_v2/E_attrition/  (see README.md)

Run from the worktree root:  python analysis/src/q3nowcast_v2/E_attrition/run.py
Exit code 0 on success. Nothing under analysis/src/q3nowcast/ or data/processed/q3nowcast/ is touched.
Data: Inside Airbnb, CC BY 4.0 (https://insideairbnb.com), redistributed on GitHub by the three repos above.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # worktree root
HELD_DIR = ROOT / "data" / "processed" / "q3nowcast" / "E"
OUT = ROOT / "data" / "processed" / "q3nowcast_v2" / "E_attrition"
CACHE = OUT / "cache"
RAW = Path("C:/Users/krish/abnb_ia_capture")
RAW_M34 = RAW / "montera34_barcelona"
RAW_CB = RAW / "chicagobooth_2015"
RAW_JDJ = RAW / "joeydejager_nyc_2015"

M34_URL = "https://raw.githubusercontent.com/montera34/airbnb.barcelona/master/data/original/airbnb"
CB_URL = "https://raw.githubusercontent.com/ChicagoBoothML/DATA___InsideAirBnB/master"
JDJ_URL = "https://raw.githubusercontent.com/JoeyDeJager/inside-airbnb-data/master/new-york-city/2015-01-01/visualizations"

# ChicagoBooth scrape dates from the repo's commit messages (commits?per_page=100, all dated 2015-12-03).
# Washington, D.C. has no date in its message: fall back to the max review date in the file.
CB_SCRAPE_DATES = {
    "Amsterdam": "2015-09-03", "Antwerp": "2015-10-03", "Athens": "2015-07-17", "Austin": "2015-11-07",
    "Barcelona": "2015-10-02", "Berlin": "2015-10-03", "Boston": "2015-10-03", "Brussels": "2015-10-03",
    "Chicago": "2015-10-03", "London": "2015-09-02", "Los Angeles": "2015-09-02", "Madrid": "2015-10-02",
    "Melbourne": "2015-10-02", "Montreal": "2015-10-02", "Nashville": "2015-10-03", "New Orleans": "2015-09-02",
    "New York City": "2015-09-01", "Oakland": "2015-06-22", "Paris": "2015-09-02", "Portland": "2015-09-02",
    "San Diego": "2015-06-22", "San Francisco": "2015-11-01", "Santa Cruz County": "2015-10-15",
    "Seattle": "2015-06-22", "Sydney": "2015-10-02", "Toronto": "2015-09-03", "Trentino": "2015-10-12",
    "Venice": "2015-07-18", "Vienna": "2015-07-18", "Washington, D.C.": None,
}
CB_CITIES = list(CB_SCRAPE_DATES)
# Directory-name aliases where the slug of the city name is not the last segment of a market_key.
CITY_ALIASES = {"washington-d-c": "washington-dc"}

# Pre-registered lines (copied from the note, section 0; do not edit after the run)
L1_LO, L1_HI = 0.10, 0.20          # annual attrition on 2017-2019 Barcelona pairs
L2_CENTRE, L2_TOL = (1 - 0.15) ** 10, 0.10   # 0.197 +/- 0.10
L3_TOL = 0.10

AGE_BUCKET = 12


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return CITY_ALIASES.get(s, s)


def ym_index(s: pd.Series) -> pd.Series:
    """'YYYY-MM' or datetime -> integer month index (year*12 + month-1)."""
    d = pd.to_datetime(s, errors="coerce")
    return (d.dt.year * 12 + d.dt.month - 1).astype("Int64")


def ym_label(ymi: pd.Series | np.ndarray) -> pd.Series:
    ymi = pd.Series(ymi).astype(int)
    return (ymi // 12).astype(str) + "-" + ((ymi % 12) + 1).astype(str).str.zfill(2)


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------------------------
# 1. counting
# ----------------------------------------------------------------------------------------------
def count_listing_month(path: Path, cache_key: str) -> pd.DataFrame:
    """One row per listing x month with n_reviews, from a reviews file that has listing_id and date."""
    cp = CACHE / f"{cache_key}.csv.gz"
    if cp.exists():
        return pd.read_csv(cp)
    r = pd.read_csv(path, usecols=["listing_id", "date"], dtype={"listing_id": "int64", "date": "string"})
    r["ymi"] = ym_index(r["date"])
    r = r.dropna(subset=["ymi"])
    g = r.groupby(["listing_id", "ymi"], as_index=False).size().rename(columns={"size": "n_reviews"})
    g["ymi"] = g["ymi"].astype(int)
    g.to_csv(cp, index=False)
    return g


def archive_vintages() -> list[dict]:
    """Every archive vintage on disk with its market_key, dump date and file path."""
    out = []
    for d in sorted(RAW_M34.iterdir()) if RAW_M34.exists() else []:
        if not re.fullmatch(r"\d{6}", d.name):
            continue
        f = d / "reviews_summary_barcelona_insideairbnb.csv"
        if f.exists() and not f.read_bytes()[:64].startswith(b"listing_id"):
            log(f"  montera34 {d.name}: reviews file is not a CSV (body starts {f.read_bytes()[:20]!r}); skipped")
            continue
        if f.exists() and f.stat().st_size > 0:
            out.append(dict(source="montera34", city="Barcelona", market_key="spain_catalonia_barcelona",
                            dump_date=f"20{d.name[:2]}-{d.name[2:4]}-{d.name[4:]}", path=f,
                            listings=d / "listings_summary_barcelona_insideairbnb.csv"))
    for city in CB_CITIES:
        f = RAW_CB / f"{slugify(city) if city != 'Washington, D.C.' else 'washington-d-c'}_reviews.csv.gz"
        if f.exists() and f.stat().st_size > 0:
            out.append(dict(source="chicagobooth", city=city, market_key=None, dump_date=CB_SCRAPE_DATES[city],
                            path=f, listings=None))
    f = RAW_JDJ / "nyc_reviews_20150101184336.csv"
    if f.exists():
        out.append(dict(source="joeydejager", city="New York City", market_key=None, dump_date="2015-01-01",
                        path=f, listings=RAW_JDJ / "nyc_listings_20150101184336.csv"))
    return out


def map_markets(vintages: list[dict], geo: pd.DataFrame) -> tuple[list[dict], pd.DataFrame]:
    last_seg = geo["market_key"].str.rsplit("_", n=1).str[-1]
    seg_to_key = dict(zip(last_seg, geo["market_key"]))
    rows = []
    for v in vintages:
        if v["market_key"] is None:
            v["market_key"] = seg_to_key.get(slugify(v["city"]))
        rows.append(dict(source=v["source"], city_dir=v["city"], slug=slugify(v["city"]),
                         market_key=v["market_key"], matched=v["market_key"] is not None))
    return vintages, pd.DataFrame(rows).drop_duplicates()


# ----------------------------------------------------------------------------------------------
# 2. ladders
# ----------------------------------------------------------------------------------------------
def held_latest(held: pd.DataFrame) -> pd.DataFrame:
    """Latest held dump per market from the E3 summary: market_key, held_vintage, held_ymi, ymi, n_held.
    The E3 summary starts at 2015-01, so months before that are absent here (see held_recount)."""
    latest = held.groupby("market_key")["dump_date"].max().rename("held_vintage").reset_index()
    h = held.merge(latest, on="market_key")
    h = h[h["dump_date"] == h["held_vintage"]].copy()
    h["held_ymi"] = ym_index(h["held_vintage"]).astype(int)
    return h[["market_key", "held_vintage", "held_ymi", "ymi", "n_reviews"]].rename(columns={"n_reviews": "n_held"})


def held_recount(market_keys: list[str], hl: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Recount the held latest raw reviews file (main-tree store, per E inventory.csv) for the mapped markets so that
    review months before 2015-01 exist on the held side. Returns (held counts for those markets, all months) and a
    consistency table against the E3 summary for months >= 2015-01."""
    inv = pd.read_csv(HELD_DIR / "inventory.csv", encoding="utf-8")
    inv = inv[(inv["kind"] == "reviews") & inv["market_key"].isin(market_keys)]
    rows, checks = [], []
    for mk in market_keys:
        hv = hl.loc[hl["market_key"] == mk, "held_vintage"]
        if hv.empty:
            continue
        hv = hv.iloc[0]
        f = inv[(inv["market_key"] == mk) & (inv["dump_date"] == hv)]
        if f.empty:
            log(f"  held raw file for {mk} {hv} not in inventory; pre-2015 months stay absent")
            continue
        p = Path(f["abs_path"].iloc[0])
        if not p.exists():
            log(f"  held raw file missing on disk: {p}; pre-2015 months stay absent")
            continue
        c = count_listing_month(p, f"held_{mk}_{hv}")
        t = c.groupby("ymi", as_index=False)["n_reviews"].sum().rename(columns={"n_reviews": "n_held"})
        t["market_key"] = mk
        t["held_vintage"] = hv
        t["held_ymi"] = int(ym_index(pd.Series([hv]))[0])
        rows.append(t)
        e3 = hl[(hl["market_key"] == mk)][["ymi", "n_held"]].rename(columns={"n_held": "n_e3"})
        chk = t[t["ymi"] >= 2015 * 12].merge(e3, on="ymi", how="outer").fillna(0)
        checks.append(dict(market_key=mk, held_vintage=hv, n_months=len(chk), recount_total=int(chk["n_held"].sum()),
                           e3_total=int(chk["n_e3"].sum()), max_abs_month_diff=int((chk["n_held"] - chk["n_e3"]).abs().max()),
                           n_reviews_pre2015=int(t.loc[t["ymi"] < 2015 * 12, "n_held"].sum())))
        log(f"  held recount {mk} {hv}: {int(t['n_held'].sum()):,} reviews, pre-2015 {checks[-1]['n_reviews_pre2015']:,}, "
            f"max month diff vs E3 {checks[-1]['max_abs_month_diff']}")
    if not rows:
        return hl.iloc[0:0], pd.DataFrame(checks)
    return pd.concat(rows, ignore_index=True)[["market_key", "held_vintage", "held_ymi", "ymi", "n_held"]], pd.DataFrame(checks)


def ladder_vs_held(vintages: list[dict], counts: dict[str, pd.DataFrame], hl: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for v in vintages:
        if v["market_key"] is None:
            continue
        c = counts[v["key"]].groupby("ymi", as_index=False)["n_reviews"].sum().rename(columns={"n_reviews": "n_archive"})
        a_ymi = int(ym_index(pd.Series([v["dump_date"]]))[0])
        c = c[c["ymi"] < a_ymi]  # the archive's own dump month is truncated: drop it
        h = hl[hl["market_key"] == v["market_key"]]
        if h.empty:
            continue
        held_vintage, held_ymi = h["held_vintage"].iloc[0], int(h["held_ymi"].iloc[0])
        m = c.merge(h[["ymi", "n_held"]], on="ymi", how="left")
        m["n_held"] = m["n_held"].fillna(0).astype(int)
        m["held_vintage"] = held_vintage
        m["held_ymi"] = held_ymi
        m["market_key"] = v["market_key"]
        m["source"] = v["source"]
        m["archive_vintage"] = v["dump_date"]
        m["age_months"] = held_ymi - a_ymi
        m["months_before_archive_dump"] = a_ymi - m["ymi"]
        m["ratio"] = m["n_held"] / m["n_archive"]
        m["review_month"] = ym_label(m["ymi"])
        rows.append(m)
    lad = pd.concat(rows, ignore_index=True)
    return lad[["source", "market_key", "archive_vintage", "held_vintage", "review_month", "ymi", "n_archive",
                "n_held", "ratio", "age_months", "months_before_archive_dump"]]


def ladder_intra_montera34(vintages: list[dict], counts: dict[str, pd.DataFrame]) -> pd.DataFrame:
    m34 = [v for v in vintages if v["source"] == "montera34"]
    tot = {v["dump_date"]: counts[v["key"]].groupby("ymi")["n_reviews"].sum() for v in m34}
    rows = []
    for e in m34:
        e_ymi = int(ym_index(pd.Series([e["dump_date"]]))[0])
        for l in m34:
            if l["dump_date"] <= e["dump_date"]:
                continue
            l_ymi = int(ym_index(pd.Series([l["dump_date"]]))[0])
            a = tot[e["dump_date"]]
            a = a[a.index < e_ymi]
            b = tot[l["dump_date"]].reindex(a.index).fillna(0).astype(int)
            df = pd.DataFrame({"ymi": a.index, "n_archive": a.values, "n_held": b.values})
            df["source"] = "montera34"
            df["market_key"] = "spain_catalonia_barcelona"
            df["archive_vintage"] = e["dump_date"]
            df["held_vintage"] = l["dump_date"]
            df["age_months"] = l_ymi - e_ymi
            df["months_before_archive_dump"] = e_ymi - df["ymi"]
            df["ratio"] = df["n_held"] / df["n_archive"]
            df["review_month"] = ym_label(df["ymi"])
            rows.append(df)
    lad = pd.concat(rows, ignore_index=True)
    return lad[["source", "market_key", "archive_vintage", "held_vintage", "review_month", "ymi", "n_archive",
                "n_held", "ratio", "age_months", "months_before_archive_dump"]]


def pooled_by_age(lad: pd.DataFrame, label: str, max_before: int | None = None) -> pd.DataFrame:
    d = lad[lad["months_before_archive_dump"] >= 1].copy()
    if max_before is not None:
        d = d[d["months_before_archive_dump"] <= max_before]
    d["age_bucket_lo"] = ((d["age_months"] - 1) // AGE_BUCKET) * AGE_BUCKET + 1
    d.loc[d["age_months"] <= 0, "age_bucket_lo"] = 0
    g = d.groupby("age_bucket_lo").agg(n_pairs=("archive_vintage", lambda s: s.size),
                                       n_markets=("market_key", "nunique"),
                                       n_vintage_pairs=("held_vintage", lambda s: 0),
                                       n_reviews_archive=("n_archive", "sum"),
                                       n_reviews_held=("n_held", "sum"),
                                       median_row_ratio=("ratio", "median"),
                                       mean_age_months=("age_months", "mean")).reset_index()
    vp = d.groupby("age_bucket_lo").apply(lambda x: x[["market_key", "archive_vintage", "held_vintage"]].drop_duplicates().shape[0],
                                         include_groups=False)
    g["n_vintage_pairs"] = g["age_bucket_lo"].map(vp)
    g = g.rename(columns={"n_pairs": "n_rows"})
    g["age_bucket"] = g["age_bucket_lo"].astype(str) + "-" + (g["age_bucket_lo"] + AGE_BUCKET - 1).astype(str)
    g.loc[g["age_bucket_lo"] == 0, "age_bucket"] = "0"
    g["ratio_weighted"] = g["n_reviews_held"] / g["n_reviews_archive"]
    g["annual_survival"] = g["ratio_weighted"] ** (12.0 / g["mean_age_months"].clip(lower=1))
    g["annual_attrition_pct"] = 100 * (1 - g["annual_survival"])
    g["sample"] = label
    return g[["sample", "age_bucket", "age_bucket_lo", "n_rows", "n_vintage_pairs", "n_markets", "n_reviews_archive",
              "n_reviews_held", "ratio_weighted", "median_row_ratio", "mean_age_months", "annual_survival",
              "annual_attrition_pct"]]


# ----------------------------------------------------------------------------------------------
# 3. pre-registered lines
# ----------------------------------------------------------------------------------------------
def listing_decomposition(vintages: list[dict], counts: dict[str, pd.DataFrame], pairs: pd.DataFrame) -> pd.DataFrame:
    """For each montera34 12-month pair: how much of the lost review history is listings leaving the dump versus
    reviews disappearing from listings that are still in it (review months 1-36 before the early dump)."""
    by_date = {v["dump_date"]: v["key"] for v in vintages if v["source"] == "montera34"}
    out = []
    for _, p in pairs.iterrows():
        e_ymi = int(ym_index(pd.Series([p["archive_vintage"]]))[0])
        a = counts[by_date[p["archive_vintage"]]]
        a = a[(a["ymi"] >= e_ymi - 36) & (a["ymi"] <= e_ymi - 1)]
        b = counts[by_date[p["held_vintage"]]]
        b = b[(b["ymi"] >= e_ymi - 36) & (b["ymi"] <= e_ymi - 1)]
        surv = set(b["listing_id"]) & set(a["listing_id"])
        a_surv = a[a["listing_id"].isin(surv)]["n_reviews"].sum()
        b_surv = b[b["listing_id"].isin(surv)]["n_reviews"].sum()
        out.append(dict(archive_vintage=p["archive_vintage"], held_vintage=p["held_vintage"],
                        n_listings_early=int(a["listing_id"].nunique()), n_listings_surviving=len(surv),
                        listing_exit_share=1 - len(surv) / a["listing_id"].nunique(),
                        reviews_early=int(a["n_reviews"].sum()), reviews_lost_to_listing_exit=int(a["n_reviews"].sum() - a_surv),
                        reviews_of_survivors_early=int(a_surv), reviews_of_survivors_late=int(b_surv),
                        within_survivor_ratio=b_surv / a_surv if a_surv else float("nan"),
                        total_ratio=b["n_reviews"].sum() / a["n_reviews"].sum()))
    return pd.DataFrame(out)


def eval_L1(intra: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """12-month pairs (gap 11-13 months) inside montera34, months 1-36 before the early dump."""
    d = intra[(intra["age_months"].between(11, 13)) & (intra["months_before_archive_dump"].between(1, 36))].copy()
    d["early_year"] = d["archive_vintage"].str[:4].astype(int)
    per_pair = d.groupby(["archive_vintage", "held_vintage", "age_months"]).agg(
        n_reviews_archive=("n_archive", "sum"), n_reviews_held=("n_held", "sum"), n_months=("ymi", "size")).reset_index()
    per_pair["ratio"] = per_pair["n_reviews_held"] / per_pair["n_reviews_archive"]
    per_pair["annual_attrition_pct"] = 100 * (1 - per_pair["ratio"] ** (12.0 / per_pair["age_months"]))
    per_pair["early_year"] = per_pair["archive_vintage"].str[:4].astype(int)
    per_pair["in_L1_window"] = per_pair["early_year"] >= 2017

    def pool(x: pd.DataFrame) -> pd.Series:
        r = x["n_reviews_held"].sum() / x["n_reviews_archive"].sum()
        gap = np.average(x["age_months"], weights=x["n_reviews_archive"])
        return pd.Series(dict(n_pairs=len(x), n_reviews_archive=int(x["n_reviews_archive"].sum()),
                              ratio=r, mean_gap_months=gap, annual_attrition_pct=100 * (1 - r ** (12.0 / gap))))

    by_year = per_pair.groupby("early_year").apply(pool, include_groups=False).reset_index()
    w = per_pair[per_pair["in_L1_window"]]
    pooled = pool(w)
    res = dict(line="L1", n_pairs=int(pooled["n_pairs"]), n_reviews_archive=int(pooled["n_reviews_archive"]),
               value=float(pooled["annual_attrition_pct"]), lo=100 * L1_LO, hi=100 * L1_HI,
               passed=bool(100 * L1_LO <= pooled["annual_attrition_pct"] <= 100 * L1_HI),
               detail="review-weighted annual attrition, pct, montera34 pairs with early dump 2017-2019, gap 11-13 months, review months 1-36 before the early dump")
    return per_pair, by_year, res


def eval_L2_L3(lad: pd.DataFrame) -> tuple[pd.DataFrame, dict, dict]:
    d = lad[(lad["ymi"] // 12 == 2014)]
    cb = d[d["source"] == "chicagobooth"]
    per_city = cb.groupby(["market_key", "archive_vintage", "held_vintage", "age_months"]).agg(
        n_reviews_2014_archive=("n_archive", "sum"), n_reviews_2014_held=("n_held", "sum"), n_months=("ymi", "size")).reset_index()
    per_city["ratio"] = per_city["n_reviews_2014_held"] / per_city["n_reviews_2014_archive"]
    per_city["annual_survival"] = per_city["ratio"] ** (12.0 / per_city["age_months"])
    per_city = per_city.sort_values("ratio")
    pooled = per_city["n_reviews_2014_held"].sum() / per_city["n_reviews_2014_archive"].sum()
    eq = per_city["ratio"].mean()
    med = per_city["ratio"].median()
    res2 = dict(line="L2", n_pairs=int(len(per_city)), n_reviews_archive=int(per_city["n_reviews_2014_archive"].sum()),
                value=float(pooled), lo=L2_CENTRE - L2_TOL, hi=L2_CENTRE + L2_TOL,
                passed=bool(L2_CENTRE - L2_TOL <= pooled <= L2_CENTRE + L2_TOL),
                detail=f"review-weighted 2014-month survival, 2015 ChicagoBooth vintage -> held latest vintage; equal-weighted mean {eq:.3f}, median {med:.3f}")
    j = d[d["source"] == "joeydejager"]
    jr = j["n_held"].sum() / j["n_archive"].sum() if len(j) else float("nan")
    res3 = dict(line="L3", n_pairs=int(j[["archive_vintage"]].drop_duplicates().shape[0]), n_reviews_archive=int(j["n_archive"].sum()),
                value=float(jr), lo=pooled - L3_TOL, hi=pooled + L3_TOL,
                passed=bool(abs(jr - pooled) <= L3_TOL) if len(j) else False,
                detail="NYC 2014-month survival, JoeyDeJager 2015-01-01 vintage -> held NYC latest vintage, vs the L2 pooled value")
    return per_city, res2, res3


# ----------------------------------------------------------------------------------------------
# 4. Barcelona supply exhibit and manifest
# ----------------------------------------------------------------------------------------------
def barcelona_exhibit(vintages: list[dict]) -> pd.DataFrame:
    rows = []
    for v in vintages:
        if v["source"] != "montera34" or v["listings"] is None or not v["listings"].exists():
            continue
        L = pd.read_csv(v["listings"], usecols=["id", "room_type", "price", "calculated_host_listings_count",
                                                "minimum_nights", "number_of_reviews"])
        price = pd.to_numeric(L["price"].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
        rows.append(dict(dump_date=v["dump_date"], n_listings=int(len(L)),
                         entire_home_share=float((L["room_type"] == "Entire home/apt").mean()),
                         private_room_share=float((L["room_type"] == "Private room").mean()),
                         multi_listing_share=float((L["calculated_host_listings_count"] > 1).mean()),
                         median_price_eur=float(price.median()),
                         mean_price_eur=float(price.mean()),
                         min_nights_30plus_share=float((L["minimum_nights"] >= 30).mean()),
                         listings_with_reviews_share=float((L["number_of_reviews"] > 0).mean()),
                         n_reviews_cumulative=int(pd.read_csv(CACHE / f"{v['key']}.csv.gz")["n_reviews"].sum())))
    return pd.DataFrame(rows).sort_values("dump_date")


def write_manifest() -> pd.DataFrame:
    rows = []
    for d in sorted(RAW_M34.iterdir()) if RAW_M34.exists() else []:
        if re.fullmatch(r"\d{6}", d.name):
            for f in sorted(d.iterdir()):
                rows.append((f"{M34_URL}/{d.name}/{f.name}", f, "montera34"))
    for f in sorted(RAW_CB.glob("*.gz")) if RAW_CB.exists() else []:
        slug, kind = f.name.rsplit("_", 1)
        city = next((c for c in CB_CITIES if (slugify(c) if c != "Washington, D.C." else "washington-d-c") == slug), None)
        from urllib.parse import quote
        rows.append((f"{CB_URL}/{quote(city)}/{kind}" if city else "", f, "chicagobooth"))
    for f in sorted(RAW_JDJ.glob("*.csv")) if RAW_JDJ.exists() else []:
        rows.append((f"{JDJ_URL}/{f.name}", f, "joeydejager"))
    man = pd.DataFrame([dict(url=u, local_path=str(p), source=s, bytes=p.stat().st_size, sha256=sha256_of(p),
                             pulled_at=datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
                        for u, p, s in rows])
    man["licence"] = "Inside Airbnb, CC BY 4.0 (redistributed on GitHub; see note)"
    return man


# ----------------------------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(exist_ok=True)
    geo = pd.read_csv(HELD_DIR / "market_geo.csv", encoding="utf-8")
    held = pd.read_csv(HELD_DIR / "market_vintage_monthly.csv", encoding="utf-8",
                       usecols=["market_key", "dump_date", "ymi", "n_reviews"])
    hl = held_latest(held)
    log(f"held: {hl['market_key'].nunique()} markets, latest vintages {hl['held_vintage'].min()}..{hl['held_vintage'].max()}")

    vintages = archive_vintages()
    vintages, mapping = map_markets(vintages, geo)
    mapping.to_csv(OUT / "city_market_mapping.csv", index=False)
    unmatched = mapping[~mapping["matched"]]
    log(f"archive vintages on disk: {len(vintages)} (montera34 {sum(v['source']=='montera34' for v in vintages)}, "
        f"chicagobooth {sum(v['source']=='chicagobooth' for v in vintages)}, joeydejager {sum(v['source']=='joeydejager' for v in vintages)}); "
        f"unmatched cities: {unmatched['city_dir'].tolist()}")

    counts: dict[str, pd.DataFrame] = {}
    inv = []
    for v in vintages:
        v["key"] = f"{v['source']}_{slugify(v['city'])}_{v['dump_date'] or 'nodate'}"
        c = count_listing_month(v["path"], v["key"])
        if v["dump_date"] is None:  # Washington, D.C.: no date in the commit message
            mx = pd.read_csv(v["path"], usecols=["date"], dtype={"date": "string"})["date"].max()
            v["dump_date"] = str(pd.Timestamp(mx) + pd.Timedelta(days=1))[:10]
            log(f"  {v['city']}: dump date not in commit message; using max review date + 1 = {v['dump_date']}")
        counts[v["key"]] = c
        first_m = int(c["ymi"].min())
        inv.append(dict(source=v["source"], city=v["city"], market_key=v["market_key"], dump_date=v["dump_date"],
                        file=str(v["path"]), n_reviews=int(c["n_reviews"].sum()), n_listings=int(c["listing_id"].nunique()),
                        first_review_month=ym_label(pd.Series([first_m]))[0], last_review_month=ym_label(pd.Series([int(c['ymi'].max())]))[0]))
        log(f"  counted {v['key']}: {inv[-1]['n_reviews']:,} reviews, {inv[-1]['n_listings']:,} listings")
    inv = pd.DataFrame(inv)
    inv.to_csv(OUT / "archive_vintage_inventory.csv", index=False)

    # held side: recount the latest raw dump for the mapped markets so that pre-2015 months exist
    mapped = sorted({v["market_key"] for v in vintages if v["market_key"]})
    hl_re, checks = held_recount(mapped, hl)
    checks.to_csv(OUT / "held_recount_vs_E3_check.csv", index=False)
    hl = pd.concat([hl[~hl["market_key"].isin(hl_re["market_key"].unique())], hl_re], ignore_index=True)
    log(f"held recount: {hl_re['market_key'].nunique()} markets recounted from raw; "
        f"max month diff vs E3 across markets {checks['max_abs_month_diff'].max() if len(checks) else 'n/a'}")

    lad = ladder_vs_held(vintages, counts, hl)
    intra = ladder_intra_montera34(vintages, counts)
    lad.to_csv(OUT / "survivorship_ladder.csv", index=False)
    intra.to_csv(OUT / "survivorship_ladder_intra_montera34.csv", index=False)
    log(f"ladder vs held: {len(lad):,} rows, {lad['market_key'].nunique()} markets; intra montera34: {len(intra):,} rows, "
        f"{intra[['archive_vintage','held_vintage']].drop_duplicates().shape[0]} vintage pairs")

    pooled = pd.concat([
        pooled_by_age(pd.concat([intra, lad]), "all archives, all review months >= 1 month before the early dump"),
        pooled_by_age(pd.concat([intra, lad]), "all archives, review months 1-36 before the early dump", 36),
        pooled_by_age(intra, "montera34 intra-archive only, months 1-36 before", 36),
        pooled_by_age(lad, "archive vs held 2025/2026 only, all review months"),
    ], ignore_index=True)
    pooled.to_csv(OUT / "survivorship_pooled_by_age.csv", index=False)

    # per-market decade attrition (all review months of 2012-2014 for stability) and the E note's own 12-month wedge
    wedge = pd.read_csv(HELD_DIR / "survivorship_wedge.csv", encoding="utf-8")
    w12 = wedge[wedge["months_before_early_dump"].between(1, 36)].groupby("market_key").agg(
        n_early=("n_reviews_early", "sum"), n_late=("n_reviews_late", "sum"))
    w12["e_note_12m_ratio"] = w12["n_late"] / w12["n_early"]
    pm = lad[(lad["ymi"] // 12).between(2012, 2014)].groupby(["source", "market_key", "archive_vintage", "held_vintage", "age_months"]).agg(
        n_archive=("n_archive", "sum"), n_held=("n_held", "sum")).reset_index()
    pm["ratio_2012_2014"] = pm["n_held"] / pm["n_archive"]
    pm["annual_survival"] = pm["ratio_2012_2014"] ** (12.0 / pm["age_months"])
    pm["implied_annual_attrition_pct"] = 100 * (1 - pm["annual_survival"])
    pm = pm.merge(w12[["e_note_12m_ratio"]], left_on="market_key", right_index=True, how="left")
    pm["e_note_12m_attrition_pct"] = 100 * (1 - pm["e_note_12m_ratio"])
    pm = pm.merge(geo, on="market_key", how="left").sort_values("ratio_2012_2014")
    pm.to_csv(OUT / "per_market_decade_attrition.csv", index=False)
    cbm = pm[pm["source"] == "chicagobooth"].dropna(subset=["e_note_12m_ratio"])
    rho = cbm[["implied_annual_attrition_pct", "e_note_12m_attrition_pct"]].corr(method="spearman").iloc[0, 1] if len(cbm) > 2 else float("nan")

    per_pair, by_year, r1 = eval_L1(intra)
    per_pair.to_csv(OUT / "L1_montera34_12m_pairs.csv", index=False)
    decomp = listing_decomposition(vintages, counts, per_pair)
    decomp.to_csv(OUT / "L1_listing_exit_decomposition.csv", index=False)
    by_year.to_csv(OUT / "L1_by_early_year.csv", index=False)
    per_city, r2, r3 = eval_L2_L3(lad)
    per_city.to_csv(OUT / "L2_chicagobooth_2014_by_city.csv", index=False)
    results = pd.DataFrame([r1, r2, r3])
    results["verdict"] = np.where(results["passed"], "PASS", "FAIL")
    results.to_csv(OUT / "prereg_results.csv", index=False)

    # extra rungs: archive-to-archive pairs across sources (NYC Jan 2015 -> Sep 2015; Barcelona montera34 151002 vs
    # ChicagoBooth 2015-10-02, which should be the same Inside Airbnb file)
    keyed = {(v["source"], v["market_key"], v["dump_date"]): v["key"] for v in vintages}
    xr = []
    for (s1, mk, d1), (s2, _, d2), label in [
        (("joeydejager", "united-states_ny_new-york-city", "2015-01-01"), ("chicagobooth", "united-states_ny_new-york-city", "2015-09-01"), "NYC Jan 2015 -> Sep 2015 (8 months)"),
        (("montera34", "spain_catalonia_barcelona", "2015-10-02"), ("chicagobooth", "spain_catalonia_barcelona", "2015-10-02"), "Barcelona montera34 151002 vs ChicagoBooth (same dump)"),
        (("montera34", "spain_catalonia_barcelona", "2015-04-30"), ("montera34", "spain_catalonia_barcelona", "2016-01-03"), "Barcelona Apr 2015 -> Jan 2016 (8 months)"),
    ]:
        if (s1, mk, d1) not in keyed or (s2, mk, d2) not in keyed:
            continue
        e_ymi = int(ym_index(pd.Series([d1]))[0]); l_ymi = int(ym_index(pd.Series([d2]))[0])
        a = counts[keyed[(s1, mk, d1)]]; b = counts[keyed[(s2, mk, d2)]]
        for lo, hi, win in [(1, 36, "months 1-36 before early dump"), (None, None, "calendar 2014")]:
            if lo is not None:
                aa = a[(a["ymi"] >= e_ymi - hi) & (a["ymi"] <= e_ymi - lo)]; bb = b[(b["ymi"] >= e_ymi - hi) & (b["ymi"] <= e_ymi - lo)]
            else:
                aa = a[a["ymi"] // 12 == 2014]; bb = b[b["ymi"] // 12 == 2014]
            na, nb = int(aa["n_reviews"].sum()), int(bb["n_reviews"].sum())
            surv = set(aa["listing_id"]) & set(bb["listing_id"])
            gap = max(l_ymi - e_ymi, 1)
            xr.append(dict(pair=label, window=win, early=d1, late=d2, gap_months=l_ymi - e_ymi, n_early=na, n_late=nb,
                           ratio=nb / na if na else float("nan"), annual_attrition_pct=100 * (1 - (nb / na) ** (12.0 / gap)) if na and l_ymi > e_ymi else float("nan"),
                           n_listings_early=int(aa["listing_id"].nunique()), listing_exit_share=1 - len(surv) / max(aa["listing_id"].nunique(), 1)))
    xpairs = pd.DataFrame(xr)
    xpairs.to_csv(OUT / "cross_source_pairs.csv", index=False)
    print("\n== cross-source pairs ==\n", xpairs.to_string(index=False))

    bx = barcelona_exhibit(vintages)
    bx.to_csv(OUT / "barcelona_supply_2015_2019.csv", index=False)

    man = write_manifest()
    man.to_csv(OUT / "raw_manifest.csv", index=False)

    summary = dict(run_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), wall_s=round(time.time() - t0, 1),
                   n_archive_vintages=len(vintages), unmatched_cities=unmatched["city_dir"].tolist(),
                   n_ladder_rows=int(len(lad)), n_intra_rows=int(len(intra)), n_raw_files=int(len(man)),
                   raw_bytes=int(man["bytes"].sum()), spearman_decade_vs_12m_attrition_30cities=None if np.isnan(rho) else round(float(rho), 3),
                   n_cities_spearman=int(len(cbm)), results=results.to_dict("records"))
    (OUT / "run_summary.json").write_text(json.dumps(summary, indent=1, default=str))

    pd.set_option("display.width", 200)
    print("\n== pooled by age bucket (all archives, months 1-36 before early dump) ==")
    print(pooled[pooled["sample"].str.startswith("all archives, review months 1-36")].to_string(index=False))
    print("\n== L1 by early year ==\n", by_year.to_string(index=False))
    print("\n== L1 listing-exit decomposition (pooled over 12m pairs) ==")
    dd = decomp.copy()
    dd["early_year"] = dd["archive_vintage"].str[:4]
    print(dd.groupby("early_year").agg(n_pairs=("archive_vintage", "size"), listing_exit_share=("listing_exit_share", "mean"),
                                       within_survivor_ratio=("within_survivor_ratio", "mean"), total_ratio=("total_ratio", "mean")).to_string())
    print("\n== held recount vs E3 ==\n", checks.to_string(index=False))
    print("\n== L2 per city ==\n", per_city[["market_key", "archive_vintage", "held_vintage", "age_months", "n_reviews_2014_archive", "n_reviews_2014_held", "ratio"]].to_string(index=False))
    print("\n== pre-registered lines ==\n", results.to_string(index=False))
    print(f"\nSpearman(decade-implied annual attrition, E-note 12m attrition) over {len(cbm)} ChicagoBooth cities: {rho:.3f}")
    print("\n== Barcelona supply ==\n", bx.to_string(index=False))
    log(f"done in {time.time() - t0:.1f}s; outputs in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
