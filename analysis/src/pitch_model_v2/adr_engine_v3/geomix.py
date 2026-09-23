"""adr_engine / geomix.py — the sub-regional (country-level) geographic-mix term (adr_v2_geomix_prereg.md).

within-region mix_r(t) = [Σ_c s_c(t−4)(1+g_c(t)) P_c] / [(1+g_r(t)) Σ_c s_c(t−4) P_c] − 1
sub-regional geo term(t) = Σ_r w_r · mix_r(t),  w_r = 10-K regional GBV share

Inputs: stays_yoy_by_country_vmatch.csv (E package vintage-matched counts, all three months), market/country USD price
levels (market_price_levels_usd.csv, extended by a fuller panel when available), regional GBV shares (10-K)."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C, fx_data as F

REGION_KEY = {"NAM": "na", "EMEA": "emea", "LatAm": "latam", "APAC": "apac"}


def country_prices(level_file: str = "market_price_levels_usd.csv", basis_priority=("quote_per_night", "listed_nightly")) -> pd.DataFrame:
    """One USD price level per country: stays-weighted (n_old) mean over its priced markets, preferring the quote basis
    but bridging listed-basis-only markets by the region's quote/listed ratio."""
    lvl = pd.read_csv(C.OUT / level_file).dropna(subset=["usd_level"])
    # region-level bridge listed -> quote basis (markets with both)
    both = lvl.pivot_table(index=["market", "region"], columns="price_basis", values="usd_level").dropna()
    bridge = (both["quote_per_night"] / both["listed_nightly"]).groupby(level="region").median()
    rows = []
    for (mkt, reg, ctry), g in lvl.groupby(["market", "region", "country"]):
        g = g.set_index("price_basis")
        if "quote_per_night" in g.index:
            p = float(g.loc["quote_per_night", "usd_level"]); n = float(g.loc["quote_per_night", "n_old"]); basis = "quote"
        else:
            p = float(g.loc["listed_nightly", "usd_level"]) * float(bridge.get(reg, bridge.median())); n = float(g.loc["listed_nightly", "n_old"]); basis = "listed×bridge"
        rows.append({"market": mkt, "region": reg, "country": ctry, "usd_level": p, "n": n, "basis": basis})
    m = pd.DataFrame(rows)
    cp = m.groupby(["country", "region"]).apply(lambda x: pd.Series({"usd_level": float(np.average(x.usd_level, weights=x.n)), "n_markets_priced": len(x)}), include_groups=False).reset_index()
    return cp, bridge


def build_term(country_growth: pd.DataFrame, cp: pd.DataFrame, impute_region_median=True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (per-region mix by quarter, per-country contributions). Countries without a price level take the region
    median (stated imputation) — they then contribute zero within-region mix by construction."""
    g = country_growth.copy()
    g["q"] = g.quarter.map(C.qlabel_to_period)
    price = cp.set_index("country").usd_level
    reg_med = cp.groupby("region").usd_level.median()
    g["P"] = g.country.map(price)
    g["imputed"] = g.P.isna()
    if impute_region_median:
        g.loc[g.imputed, "P"] = g.loc[g.imputed, "region"].map(reg_med)
    # base-quarter shares from the vintage-matched prior counts (n_prior = stays a year earlier, same age)
    out = []; contrib = []
    for (reg, q), x in g.groupby(["region", "q"]):
        x = x.dropna(subset=["P", "n_prior", "stays_yoy_pct"])
        if len(x) < 2: continue
        s0 = x.n_prior / x.n_prior.sum(); gr = x.stays_yoy_pct / 100.0
        g_reg = float((s0 * gr).sum())
        num = float((s0 * (1 + gr) * x.P).sum()); den = float((1 + g_reg) * (s0 * x.P).sum())
        mix = (num / den - 1) * 100
        out.append({"region": reg, "quarter": f"{q.quarter}Q{str(q.year)[2:]}", "q": q, "mix_pp": mix, "region_growth_pct": g_reg * 100, "n_countries": len(x), "n_imputed": int(x.imputed.sum()), "share_imputed": float(s0[x.imputed].sum())})
        s1 = s0 * (1 + gr) / (1 + g_reg); rel = x.P / float((s0 * x.P).sum())
        for c, a, b, r_, gg in zip(x.country, s0, s1, rel, gr):
            contrib.append({"region": reg, "quarter": f"{q.quarter}Q{str(q.year)[2:]}", "country": c, "share_base": a, "share_new": b, "rel_price": r_, "growth_pct": gg * 100, "contrib_pp": (b - a) * r_ * 100})
    return pd.DataFrame(out), pd.DataFrame(contrib)


def subregional_term(mix: pd.DataFrame, shares_by_q: pd.DataFrame | None = None) -> pd.DataFrame:
    """Σ_r w_r · mix_r with 10-K GBV shares knowable at the quarter's print (history) or FY2025 forward."""
    shares = F.gbv_shares(); pdts = F.print_dates(); rows = []
    for q, x in mix.groupby("quarter"):
        info = pdts[q] if q in pdts.index else None
        gsh, fy = F.shares_at(shares, info)
        x = x.set_index("region"); tot = 0.0; parts = {}
        for reg, key in REGION_KEY.items():
            if reg in x.index:
                parts[reg] = float(gsh[key]) * float(x.loc[reg, "mix_pp"]); tot += parts[reg]
        rows.append({"quarter": q, "subgeo_pp": tot, **{f"part_{r}": v for r, v in parts.items()}, "shares_fy": fy})
    d = pd.DataFrame(rows); d["q"] = d.quarter.map(C.qlabel_to_period)
    return d.sort_values("q").drop(columns="q").reset_index(drop=True)
