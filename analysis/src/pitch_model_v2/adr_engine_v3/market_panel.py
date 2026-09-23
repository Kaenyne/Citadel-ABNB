"""adr_engine / market_panel.py — mitigation B: a market-level panel test of the core like-for-like price term.

    cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.market_panel

Governing pre-registration: docs/pitch-model-v2/lines/adr_v2_mitigation_B_market_panel.md (§1-§3, written and saved
before any y, any x or any regression was computed; only the *inventory of dump dates* was inspected first, because
the pair window cannot be registered without knowing whether pairs exist -- and at 300-430 days they do not).

The object. `adr_v2_thesis.md` calls the core (3.85pp, carried) the ADR line's weakest term, and
`adr_v1b_utilisation_prereg.md` failed the quarterly utilisation test on n 13. This module turns that one time
series into a cross-section: for every market with two Inside Airbnb dumps ~9-12 months apart, it measures the
growth of the market's listed nightly price against the growth of its stays per active listing, and asks whether
utilisation prices.

Writes, into data/processed/pitch_model_v2/adr_engine/:

  market_panel_dump_aggregates.csv   cache: one row per market-dump (the raw-store pass; minutes)
  market_panel_lfl_pairs.csv         cache: same-listing (id-matched) price change per candidate pair
  market_panel_pairs.csv             the panel: one row per market x dump-pair, with y_* and x_*
  market_panel_scores.csv            the registered specifications: n, b, se, p, r2, elasticity CI
  market_panel_by_region.csv         region-by-region M1
  market_panel_robustness.csv        the robustness list of the registration, §3
  market_panel_implied_core.csv      the elasticity applied to the 1H26 regional utilisation readings

Nothing here is fitted to reach a number and nothing is chosen after a result: the primary is `y_med` on `x_util`
under M2 and no other basis, window, lag or region can be promoted into its place.
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from . import config as C
from .refresh_prices import COUNTRY_CCY, MIN_USD_LEVEL, ROOM_TYPE_EH, _clean_price, fx_year_average

# --------------------------------------------------------------------------------------------------------------- #
# raw stores (read-only).  The capture store holds the 2026 wave; the two E-package expansion stores hold the 2025
# wave and a handful of 2026 re-pulls.  Nothing is ever written back to any of them.
# --------------------------------------------------------------------------------------------------------------- #
EXPANSION = Path.home() / "abnb_scratch/raw_expansion/v3_2026-09-06"
STORES = {
    "capture": Path.home() / "abnb_ia_capture",
    "yoy2025": EXPANSION / "inside_airbnb_yoy_2025",
    "backfill": EXPANSION / "inside_airbnb_listings_backfill",
}
SKIP_DIRS = {"logs"}

# --------------------------------------------------------------------------------------------------------------- #
# registered constants (§1-§3 of the note; frozen before the first estimate)
# --------------------------------------------------------------------------------------------------------------- #
GAP_MIN, GAP_MAX = 240, 430          # A1: amended from 300-430, which holds exactly one pair
GAP_TASK = (300, 430)                # the window as originally specified -- reported, never scored
MODAL_GAP = (260, 290)               # robustness (v): the September-2025 -> June-2026 wave, one common season
MIN_LISTINGS_ROBUST = 300            # robustness (i)
WINSOR = 0.01                        # robustness (ii)
FX_YEAR = 2026                       # the $5 floor screen only; every regression variable is local-currency growth
READ_COLS = ["id", "room_type", "price", "number_of_reviews_ltm", "number_of_reviews_ly"]
REGION_ORDER = ["NAM", "EMEA", "APAC", "LatAm"]
CORE_CARRIED = 3.85                  # adr_v2_thesis.md: the 2Q26 core, carried flat


# =============================================================================================================== #
# 1. inventory
# =============================================================================================================== #
def dump_inventory() -> pd.DataFrame:
    """One row per listings.csv.gz in any store: market_key, country, dump date, path."""
    rows = []
    for store, root in STORES.items():
        if not root.exists():
            continue
        for f in sorted(root.rglob("listings.csv.gz")):
            rel = f.relative_to(root).parts
            if len(rel) != 5 or rel[0] in SKIP_DIRS:
                continue
            country, state, market, dump, _ = rel
            rows.append({"market_key": f"{country}_{state}_{market}", "country": country, "state": state,
                         "market": market, "store": store, "dump_date": dump, "path": str(f)})
    inv = pd.DataFrame(rows)
    inv["dump_dt"] = pd.to_datetime(inv.dump_date)
    # a market-dump captured in two stores is one observation: keep one path per (market, dump date)
    inv = inv.sort_values(["market_key", "dump_dt", "store"]).drop_duplicates(["market_key", "dump_date"])
    return inv.reset_index(drop=True)


def candidate_pairs(inv: pd.DataFrame) -> pd.DataFrame:
    """Every within-market ordered pair of distinct dump dates, with its span in days."""
    rows = []
    for mk, sub in inv.groupby("market_key"):
        sub = sub.sort_values("dump_dt")
        for (_, a), (_, b) in itertools.combinations(sub.iterrows(), 2):
            rows.append({"market_key": mk, "country": a.country, "market": a.market,
                         "dump_a": a.dump_date, "dump_b": b.dump_date,
                         "path_a": a.path, "path_b": b.path,
                         "gap_days": int((b.dump_dt - a.dump_dt).days)})
    return pd.DataFrame(rows).sort_values(["market_key", "dump_a", "dump_b"]).reset_index(drop=True)


# =============================================================================================================== #
# 2. the raw-store pass (cached)
# =============================================================================================================== #
def read_dump(path: str | Path) -> pd.DataFrame:
    """The registered listing selection: entire home, number_of_reviews_ltm > 0, price parsed from the string."""
    head = pd.read_csv(path, nrows=0)
    cols = [c for c in READ_COLS if c in head.columns]
    d = pd.read_csv(path, usecols=cols, dtype={"id": "str"})
    for c in READ_COLS:
        if c not in d.columns:
            d[c] = np.nan
    d["number_of_reviews_ltm"] = pd.to_numeric(d.number_of_reviews_ltm, errors="coerce")
    d["number_of_reviews_ly"] = pd.to_numeric(d.number_of_reviews_ly, errors="coerce")
    eh = d[(d.room_type == ROOM_TYPE_EH) & (d.number_of_reviews_ltm > 0)].copy()
    eh["listed"] = _clean_price(eh.price)
    return eh.dropna(subset=["listed"])[["id", "listed", "number_of_reviews_ltm", "number_of_reviews_ly"]]


def aggregate(eh: pd.DataFrame) -> dict:
    """Scalar aggregates of one market-dump under the registered selection."""
    if len(eh) == 0:
        return {"active": 0, "median_price": np.nan, "rw_mean": np.nan, "reviews_ltm": np.nan,
                "reviews_ly": np.nan, "reviews_ltm_on_ly_panel": np.nan, "n_ly": 0}
    w = eh.number_of_reviews_ltm
    ly = eh.dropna(subset=["number_of_reviews_ly"])
    return {"active": int(len(eh)),
            "median_price": float(eh.listed.median()),
            "rw_mean": float(np.average(eh.listed, weights=w)),
            "reviews_ltm": float(w.sum()),
            "reviews_ly": float(ly.number_of_reviews_ly.sum()) if len(ly) else np.nan,
            "reviews_ltm_on_ly_panel": float(ly.number_of_reviews_ltm.sum()) if len(ly) else np.nan,
            "n_ly": int(len(ly))}


def lfl_change(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    """Same-listing price change: median (and review-weighted mean) of the per-listing price ratio, id-matched."""
    m = a[["id", "listed"]].merge(b[["id", "listed", "number_of_reviews_ltm"]], on="id", suffixes=("_a", "_b"))
    m = m[(m.listed_a > 0) & (m.listed_b > 0)]
    if len(m) < 25:
        return {"n_lfl": int(len(m)), "lfl_log_med": np.nan, "lfl_log_rw": np.nan}
    r = np.log(m.listed_b / m.listed_a)
    return {"n_lfl": int(len(m)), "lfl_log_med": float(r.median()),
            "lfl_log_rw": float(np.average(r, weights=m.number_of_reviews_ltm.clip(lower=1)))}


def build_cache(rebuild: bool = False, verbose: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One pass over the raw stores, market by market: per-dump aggregates and per-pair id-matched price change."""
    agg_path, lfl_path = C.OUT / "market_panel_dump_aggregates.csv", C.OUT / "market_panel_lfl_pairs.csv"
    if agg_path.exists() and lfl_path.exists() and not rebuild:
        if verbose:
            print(f"[cache] reusing {agg_path.name} and {lfl_path.name} (pass --rebuild to re-read the raw store)")
        return pd.read_csv(agg_path), pd.read_csv(lfl_path)

    inv, pairs = dump_inventory(), None
    pairs = candidate_pairs(inv)
    agg_rows, lfl_rows = [], []
    markets = sorted(inv.market_key.unique())
    for i, mk in enumerate(markets, 1):
        sub = inv[inv.market_key == mk].sort_values("dump_dt")
        frames = {}
        for _, r in sub.iterrows():
            eh = read_dump(r.path)
            frames[r.dump_date] = eh
            agg_rows.append({"market_key": mk, "country": r.country, "market": r.market, "store": r.store,
                             "dump_date": r.dump_date, **aggregate(eh)})
        for _, p in pairs[pairs.market_key == mk].iterrows():
            lfl_rows.append({"market_key": mk, "dump_a": p.dump_a, "dump_b": p.dump_b,
                             **lfl_change(frames[p.dump_a], frames[p.dump_b])})
        if verbose and (i % 10 == 0 or i == len(markets)):
            print(f"[raw] {i}/{len(markets)} markets", flush=True)
    agg = pd.DataFrame(agg_rows)
    lfl = pd.DataFrame(lfl_rows)
    C.OUT.mkdir(parents=True, exist_ok=True)
    agg.to_csv(agg_path, index=False)
    lfl.to_csv(lfl_path, index=False)
    return agg, lfl


# =============================================================================================================== #
# 3. the panel
# =============================================================================================================== #
def ann(log_ratio: pd.Series | float, days: pd.Series | float) -> pd.Series | float:
    """Annualised log growth in percent (§1): 100 * ln(v_b/v_a) * 365 / days."""
    return 100.0 * log_ratio * 365.0 / days


def usd_levels(agg: pd.DataFrame) -> pd.Series:
    """Median local price converted at the FX_YEAR average -- used only for the $5 broken-price floor."""
    fx = fx_year_average(FX_YEAR)
    ccy = agg.country.map(COUNTRY_CCY)
    return agg.median_price * ccy.map(fx)


def build_pairs(agg: pd.DataFrame, lfl: pd.DataFrame) -> pd.DataFrame:
    """One row per market x dump-pair, with the registered y_* and x_*."""
    cmap = pd.read_csv(C.OUT / "market_currency_map.csv")[["market_key", "region"]]
    ctry_region = (pd.read_csv(C.OUT / "market_currency_map.csv")[["country", "region"]]
                   .drop_duplicates().set_index("country").region)

    agg = agg.copy()
    agg["usd_level"] = usd_levels(agg)
    agg["price_ok"] = agg.usd_level >= MIN_USD_LEVEL
    ak = agg.set_index(["market_key", "dump_date"])

    inv = dump_inventory()
    p = candidate_pairs(inv).drop(columns=["path_a", "path_b"])
    for side, dcol in (("a", "dump_a"), ("b", "dump_b")):
        j = ak.reindex(pd.MultiIndex.from_arrays([p.market_key, p[dcol]]))
        for c in ["active", "median_price", "rw_mean", "reviews_ltm", "reviews_ly", "reviews_ltm_on_ly_panel",
                  "usd_level", "price_ok"]:
            p[f"{c}_{side}"] = j[c].to_numpy()
    p["n_listings_a"], p["n_listings_b"] = p.active_a, p.active_b
    p = p.merge(lfl, on=["market_key", "dump_a", "dump_b"], how="left")

    p["region"] = p.market_key.map(cmap.set_index("market_key").region)
    p["region"] = p.region.fillna(p.country.map(ctry_region))

    d = p.gap_days
    p["y_med"] = ann(np.log(p.median_price_b / p.median_price_a), d)
    p["y_rw"] = ann(np.log(p.rw_mean_b / p.rw_mean_a), d)
    p["y_lfl"] = ann(p.lfl_log_med, d)
    p["y_lfl_rw"] = ann(p.lfl_log_rw, d)
    p["y_quote"] = np.nan          # A3: price_quote_price_per_night exists only in the 2026 dumps
    p["x_supply"] = ann(np.log(p.active_b / p.active_a), d)
    p["x_rev"] = ann(np.log(p.reviews_ltm_b / p.reviews_ltm_a), d)
    p["x_util"] = p.x_rev - p.x_supply
    # x_util_lfl: within-dump-B, constant listing panel, already a 12-month comparison -> not annualised
    p["x_util_lfl"] = 100.0 * np.log(p.reviews_ltm_on_ly_panel_b / p.reviews_ly_b)

    p["gap_bucket"] = (p.gap_days // 30 * 30).astype("Int64").astype(str) + "-" + \
                      (p.gap_days // 30 * 30 + 29).astype("Int64").astype(str)
    p["in_task_window"] = p.gap_days.between(*GAP_TASK)
    p["in_primary"] = (p.gap_days.between(GAP_MIN, GAP_MAX) & p.price_ok_a.astype(bool)
                       & p.price_ok_b.astype(bool) & p.y_med.notna() & p.x_util.notna())
    cols = ["market_key", "market", "country", "region", "dump_a", "dump_b", "gap_days", "gap_bucket",
            "n_listings_a", "n_listings_b", "active_a", "active_b", "median_price_a", "median_price_b",
            "rw_mean_a", "rw_mean_b", "reviews_ltm_a", "reviews_ltm_b", "reviews_ly_b", "usd_level_a", "usd_level_b",
            "price_ok_a", "price_ok_b", "n_lfl", "y_med", "y_rw", "y_lfl", "y_lfl_rw", "y_quote",
            "x_util", "x_supply", "x_rev", "x_util_lfl", "in_task_window", "in_primary"]
    return p[cols].sort_values(["region", "market_key"]).reset_index(drop=True)


# =============================================================================================================== #
# 4. scoring
# =============================================================================================================== #
def ols(df: pd.DataFrame, y: str, xs: list[str], fe: list[str] | None = None, spec: str = "",
        note: str = "") -> dict | None:
    """OLS with market-clustered standard errors; `fe` are absorbed as dummies (drop-first)."""
    fe = fe or []
    use = df.dropna(subset=[y] + xs + fe).copy()
    if len(use) < 10:
        return None
    X = use[xs].astype(float)
    for f in fe:
        dummies = pd.get_dummies(use[f], prefix=f, drop_first=True, dtype=float)
        dummies = dummies.loc[:, dummies.sum() > 0]
        X = pd.concat([X, dummies], axis=1)
    X = sm.add_constant(X, has_constant="add")
    m = sm.OLS(use[y].astype(float), X).fit(cov_type="cluster", cov_kwds={"groups": use.market_key})
    b0 = xs[0]
    ci = m.conf_int().loc[b0]
    row = {"spec": spec, "y": y, "x": b0, "fe": "+".join(fe) if fe else "none", "n": int(m.nobs),
           "n_markets": int(use.market_key.nunique()), "b": float(m.params[b0]), "se": float(m.bse[b0]),
           "t": float(m.tvalues[b0]), "p": float(m.pvalues[b0]), "ci_lo": float(ci[0]), "ci_hi": float(ci[1]),
           "r2": float(m.rsquared), "note": note}
    for extra in xs[1:]:
        row[f"b_{extra}"] = float(m.params[extra])
        row[f"p_{extra}"] = float(m.pvalues[extra])
    return row


def winsorise(df: pd.DataFrame, cols: list[str], q: float = WINSOR) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        lo, hi = out[c].quantile(q), out[c].quantile(1 - q)
        out[c] = out[c].clip(lo, hi)
    return out


def score(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base = panel[panel.in_primary].copy()
    exus = base[base.country != "united-states"]
    FE = ["region", "gap_bucket"]
    rows = []
    rows.append(ols(base, "y_med", ["x_util"], None, "M1  y_med ~ x_util", "no fixed effects"))
    rows.append(ols(base, "y_med", ["x_util"], FE, "M2  y_med ~ x_util + FE", "PRIMARY (registered pass line)"))
    rows.append(ols(base, "y_med", ["x_rev", "x_supply"], FE, "M3  y_med ~ x_rev + x_supply + FE",
                    "supply/demand split; b is on x_rev"))
    rows.append(ols(exus, "y_med", ["x_util"], FE, "M2-exUS", "PRIMARY, ex-US half of the pass line"))
    rows.append(ols(exus, "y_med", ["x_rev", "x_supply"], FE, "M3-exUS", "supply/demand split, ex-US"))
    rows.append(ols(base, "y_rw", ["x_util"], FE, "M2 on y_rw", "review-weighted mean price basis"))
    rows.append(ols(base, "y_lfl", ["x_util"], FE, "M2 on y_lfl", "same-listing (id-matched) price basis"))
    rows.append(ols(base, "y_med", ["x_util_lfl"], FE, "M2 with x_util_lfl", "within-dump-B constant-panel demand"))
    rows.append(ols(base, "y_lfl", ["x_util_lfl"], FE, "y_lfl ~ x_util_lfl", "both like-for-like"))
    scores = pd.DataFrame([r for r in rows if r])

    reg_rows = []
    for g in REGION_ORDER:
        sub = base[base.region == g]
        r = ols(sub, "y_med", ["x_util"], ["gap_bucket"], f"M1-{g}", f"region {g}")
        reg_rows.append(r or {"spec": f"M1-{g}", "y": "y_med", "x": "x_util", "fe": "gap_bucket", "n": len(sub),
                              "n_markets": int(sub.market_key.nunique()), "b": np.nan, "se": np.nan, "t": np.nan,
                              "p": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "r2": np.nan,
                              "note": f"region {g}: fewer than 10 pairs, not estimable"})
    by_region = pd.DataFrame(reg_rows)

    rb = []
    big = base[(base.active_a >= MIN_LISTINGS_ROBUST) & (base.active_b >= MIN_LISTINGS_ROBUST)]
    rb.append(ols(big, "y_med", ["x_util"], FE, "R-i  >=300 listings both dumps", "robustness (i)"))
    rb.append(ols(winsorise(base, ["y_med", "x_util"]), "y_med", ["x_util"], FE, "R-ii winsorised 1/99",
                  "robustness (ii)"))
    rb.append(ols(base, "y_rw", ["x_util"], FE, "R-iii y_rw basis", "robustness (iii)"))
    rb.append(ols(base, "y_lfl", ["x_util"], FE, "R-iv y_lfl basis", "robustness (iv)"))
    modal = base[base.gap_days.between(*MODAL_GAP)]
    rb.append(ols(modal, "y_med", ["x_util"], ["region"], "R-v  modal span 260-290d",
                  "robustness (v): one common seasonal window, so no gap FE"))
    rb.append(ols(base[base.country != "switzerland"], "y_med", ["x_util"], FE, "R-vi ex-Switzerland",
                  "robustness (vi)"))
    rb.append({"spec": "R-vii y_quote basis", "y": "y_quote", "x": "x_util", "fe": "-", "n": 0, "n_markets": 0,
               "b": np.nan, "se": np.nan, "t": np.nan, "p": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
               "r2": np.nan, "note": "NOT EXECUTABLE (A3): price_quote_price_per_night exists only in 2026 dumps"})
    short = panel[panel.in_primary.eq(False) & panel.gap_days.between(150, 239)
                  & panel.y_med.notna() & panel.x_util.notna()]
    rb.append(ols(short, "y_med", ["x_util"], ["region"], "R-span 150-239d (excluded arm)",
                  "span sensitivity, not part of the pass line"))
    rb.append({"spec": "R-task window 300-430d", "y": "y_med", "x": "x_util", "fe": "-",
               "n": int(panel.in_task_window.sum()), "n_markets": int(panel[panel.in_task_window].market_key.nunique()),
               "b": np.nan, "se": np.nan, "t": np.nan, "p": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "r2": np.nan,
               "note": "NOT EXECUTABLE (A1): the store holds one pair at this span"})
    robust = pd.DataFrame([r for r in rb if r])
    return scores, by_region, robust


# =============================================================================================================== #
# 5. what it means for the line
# =============================================================================================================== #
def implied_core(scores: pd.DataFrame) -> pd.DataFrame:
    """Carry the 1H26 regional utilisation readings through the estimated elasticity, against the carried 3.85pp.

    LatAm's utilisation series is the vintage artefact `adr_v1b_utilisation_prereg.md` §4(3) reports and does not
    use (+45-65% y/y every quarter, from the listing counts, not from utilisation); it is carried here with a flag
    and kept out of the primary blend, exactly as that note leaves it. The v1b North American quarterly beta (0.32)
    is carried through the same readings as a comparator, so the two estimates can be read side by side."""
    prim = scores[scores.spec.str.startswith("M2  ")].iloc[0]
    b, lo, hi = prim.b, prim.ci_lo, prim.ci_hi
    u = pd.read_csv(C.OUT / "utilisation_vmatch_quarterly.csv")
    u = u[u.q.isin(["2026Q1", "2026Q2"]) & u.region.isin(REGION_ORDER)]
    u = u.groupby("region", as_index=False).util_yoy_pct.mean()
    w = pd.read_csv(C.OUT / "regional_growth_forward.csv")
    w = w[w.quarter == "4Q26"].iloc[0]
    shares = {"NAM": w.share_na, "EMEA": w.share_emea, "LatAm": w.share_latam, "APAC": w.share_apac}
    u["nights_share_4q26"] = u.region.map(shares)
    u["artefact_flag"] = np.where(u.region == "LatAm", "vintage artefact (v1b §4.3) - excluded from blend", "")
    u["implied_pp"] = b * u.util_yoy_pct
    u["implied_lo"] = np.minimum(lo * u.util_yoy_pct, hi * u.util_yoy_pct)
    u["implied_hi"] = np.maximum(lo * u.util_yoy_pct, hi * u.util_yoy_pct)
    u["implied_pp_v1b_na_beta"] = 0.32 * u.util_yoy_pct
    u["carried_core_pp"] = CORE_CARRIED
    u["vs_carried_pp"] = u.implied_pp - CORE_CARRIED

    def blend(rows: pd.DataFrame, label: str) -> dict:
        s = rows.nights_share_4q26
        agg = {c: float((rows[c] * s).sum() / s.sum())
               for c in ["implied_pp", "implied_lo", "implied_hi", "implied_pp_v1b_na_beta"]}
        return {"region": label, "util_yoy_pct": float((rows.util_yoy_pct * s).sum() / s.sum()),
                "nights_share_4q26": float(s.sum()), "artefact_flag": "", **agg,
                "carried_core_pp": CORE_CARRIED, "vs_carried_pp": agg["implied_pp"] - CORE_CARRIED}

    ex = u[u.region != "LatAm"]
    u = pd.concat([u, pd.DataFrame([blend(ex, "BLEND ex-LatAm (4Q26 nights shares) - PRIMARY"),
                                    blend(u, "BLEND incl. LatAm artefact - not used")])], ignore_index=True)
    u["elasticity_b"] = b
    u["elasticity_ci"] = f"[{lo:.3f}, {hi:.3f}]"
    return u


def exclusions(panel: pd.DataFrame, agg: pd.DataFrame) -> pd.DataFrame:
    """Every pair inside the amended window that does not reach the primary, with the reason, plus the dead dumps."""
    w = panel[panel.gap_days.between(GAP_MIN, GAP_MAX) & ~panel.in_primary].copy()
    w["reason"] = np.where(w.median_price_a.isna() | w.median_price_b.isna(),
                           "price column empty in one dump (Inside Airbnb publication gap)",
                           "median price below the $5 floor (broken price field)")
    dead = agg[agg.active.eq(0)][["market_key", "dump_date"]].assign(
        reason="dump carries no parseable price for any established entire-home listing")
    out = pd.concat([w[["market_key", "region", "dump_a", "dump_b", "gap_days", "median_price_a",
                        "median_price_b", "usd_level_a", "usd_level_b", "reason"]],
                     dead], ignore_index=True)
    return out


def descriptives(panel: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    """The facts the verdict rests on: how big the seasonal wedge in y is, and what the panel can and cannot rule out."""
    base = panel[panel.in_primary]
    prim = scores[scores.spec.str.startswith("M2  ")].iloc[0]
    fe_only = ols(base.assign(_z=0.0), "y_med", ["_z"], ["region", "gap_bucket"], "FE only")
    rows = [{"item": "pairs in primary window", "value": float(len(base))},
            {"item": "markets in primary window", "value": float(base.market_key.nunique())},
            {"item": "median span (days)", "value": float(base.gap_days.median())},
            {"item": "mean y_med (annualised %)", "value": float(base.y_med.mean())},
            {"item": "median y_med (annualised %)", "value": float(base.y_med.median())},
            {"item": "median y_lfl same-listing (annualised %)", "value": float(base.y_lfl.median())},
            {"item": "sd of y_med across markets", "value": float(base.y_med.std())},
            {"item": "mean x_util (annualised %)", "value": float(base.x_util.mean())},
            {"item": "sd of x_util across markets", "value": float(base.x_util.std())},
            {"item": "raw corr(y_med, x_util)", "value": float(base.y_med.corr(base.x_util))},
            {"item": "R2 of the fixed effects alone", "value": float(fe_only["r2"]) if fe_only else np.nan},
            {"item": "R2 of M2 (FE + x_util)", "value": float(prim.r2)},
            {"item": "R2 added by x_util", "value": float(prim.r2) - (float(fe_only["r2"]) if fe_only else np.nan)},
            {"item": "M2 elasticity b", "value": float(prim.b)},
            {"item": "M2 95% CI upper bound on b", "value": float(prim.ci_hi)},
            {"item": "v1b NA quarterly beta (comparator)", "value": 0.32},
            {"item": "is v1b beta inside the panel CI?", "value": float(prim.ci_lo <= 0.32 <= prim.ci_hi)},
            {"item": "carried core 2Q26 (pp)", "value": CORE_CARRIED}]
    h = pd.read_csv(C.OUT / "exfx_history.csv")
    rows.append({"item": "core 2023-25 mean (pp)",
                 "value": float(h[h.quarter.str[-2:].isin(["23", "24", "25"])].core.mean())})
    return pd.DataFrame(rows)


# =============================================================================================================== #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild", action="store_true", help="re-read the raw stores instead of the cached aggregates")
    a = ap.parse_args()

    inv = dump_inventory()
    cand = candidate_pairs(inv)
    print(f"[inventory] {len(inv)} market-dumps, {inv.market_key.nunique()} markets, "
          f"{len(cand)} candidate pairs; {int(cand.gap_days.between(*GAP_TASK).sum())} in the task's 300-430d window")

    agg, lfl = build_cache(rebuild=a.rebuild)
    panel = build_pairs(agg, lfl)
    panel.to_csv(C.OUT / "market_panel_pairs.csv", index=False)
    base = panel[panel.in_primary]
    print(f"[panel] {len(panel)} pairs written; {len(base)} in the primary window "
          f"({base.market_key.nunique()} markets, span {base.gap_days.min()}-{base.gap_days.max()}d)")

    exc = exclusions(panel, agg)
    exc.to_csv(C.OUT / "market_panel_exclusions.csv", index=False)
    print(f"[exclusions] {len(exc)} rows written ({int(panel.gap_days.between(GAP_MIN, GAP_MAX).sum())} pairs in "
          f"window, {len(base)} reach the primary)")

    scores, by_region, robust = score(panel)
    scores.to_csv(C.OUT / "market_panel_scores.csv", index=False)
    by_region.to_csv(C.OUT / "market_panel_by_region.csv", index=False)
    robust.to_csv(C.OUT / "market_panel_robustness.csv", index=False)
    cols = ["spec", "n", "n_markets", "b", "se", "p", "ci_lo", "ci_hi", "r2"]
    print("\n[scores]\n", scores[cols].to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print("\n[by region]\n", by_region[cols].to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print("\n[robustness]\n", robust[cols].to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    desc = descriptives(panel, scores)
    desc.to_csv(C.OUT / "market_panel_descriptives.csv", index=False)
    print("\n[descriptives]\n", desc.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    imp = implied_core(scores)
    imp.to_csv(C.OUT / "market_panel_implied_core.csv", index=False)
    print("\n[implied core]\n", imp.drop(columns=["elasticity_b"]).to_string(
        index=False, float_format=lambda v: f"{v:.3f}"))

    prim = scores[scores.spec.str.startswith("M2  ")].iloc[0]
    ex = scores[scores.spec == "M2-exUS"].iloc[0]
    passed = bool(prim.b > 0 and prim.p <= 0.05 and ex.b > 0 and ex.p <= 0.05)
    print(f"\n[VERDICT] registered pass line (M2 full b>0 & p<=0.05 AND M2-exUS b>0 & p<=0.05): "
          f"{'PASS' if passed else 'FAIL'}"
          f"  [full b {prim.b:+.3f} p {prim.p:.3f} | ex-US b {ex.b:+.3f} p {ex.p:.3f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
