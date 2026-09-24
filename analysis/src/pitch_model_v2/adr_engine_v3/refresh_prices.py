"""adr_engine / refresh_prices.py — rebuild the three inputs of the sub-regional geo-mix term end to end, from the
raw stores, deterministically (adr_v2_geomix_prereg.md §1; upgrade 6).

    PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.refresh_prices

Writes, into data/processed/pitch_model_v2/adr_engine/:

  market_currency_map.csv              123 panel markets -> country, region, currency, fx_available
  stays_yoy_by_country_vmatch.csv      (a) vintage-matched stays y/y by country-quarter, from q3nowcast/E
  market_price_levels_capture_2026.csv (b) median entire-home price by market, local and USD, from the capture store
  country_price_levels_usd.csv         (c) one USD price level per country, n_listed-weighted over its markets

Nothing here is fitted and nothing is chosen after a result. The three construction choices that are judgements are
frozen at the top of this file: COUNTRY_CCY (the destination currency of each panel country), FX_YEAR (the averaging
window for the local->USD conversion) and MIN_USD_LEVEL (the data-quality floor that drops the Swiss dumps, whose
`price` column carries 0.16-0.18 CHF a night).
"""
from __future__ import annotations
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C

# ---- raw stores ---------------------------------------------------------------------------------------------------
CAPTURE_ROOT = Path.home() / "abnb_ia_capture"            # Inside Airbnb dumps: <country>/<state>/<market>/<dump>/listings.csv.gz
E_MARKET_MONTHLY = C.ROOT / "data/processed/q3nowcast/E/market_monthly_yoy.csv"
SKIP_DIRS = {"logs"}

# ---- FX: FRED H.10 bilaterals, plus the ECB reference series and the Belize peg (prereg §4 amendment ii) -----------
FRED_FX_FILES = [C.FX_DAILY, C.OUT / "fx_daily_extra_2026-09-22.csv"]          # H.10 only -> sets `fx_available`
PEG_FX_FILES = [C.OUT / "fx_daily_ecb_peg_2026-09-22.csv"]                     # CZK, HUF, TRY (ECB), BZD (2:1 peg)
FX_YEAR = 2026            # local -> USD at the calendar-year-average rate of the capture year (dumps are all 2026)

# ---- frozen country -> destination currency (the panel's 37 countries; region comes from the E package) ------------
# `china` is the Inside Airbnb country folder of the single market china_hk_hong-kong, so its currency is HKD.
COUNTRY_CCY = {
    "argentina": "ARS", "australia": "AUD", "austria": "EUR", "belgium": "EUR", "belize": "BZD", "brazil": "BRL",
    "canada": "CAD", "chile": "CLP", "china": "HKD", "colombia": "COP", "czech-republic": "CZK", "denmark": "DKK",
    "france": "EUR", "germany": "EUR", "greece": "EUR", "hungary": "HUF", "ireland": "EUR", "italy": "EUR",
    "japan": "JPY", "kenya": "KES", "latvia": "EUR", "malta": "EUR", "mexico": "MXN", "new-zealand": "NZD",
    "norway": "NOK", "portugal": "EUR", "singapore": "SGD", "south-africa": "ZAR", "spain": "EUR", "sweden": "SEK",
    "switzerland": "CHF", "taiwan": "TWD", "thailand": "THB", "the-netherlands": "EUR", "turkey": "TRY",
    "united-kingdom": "GBP", "united-states": "USD",
}
HONG_KONG_MARKET = "china_hk_hong-kong"

# ---- listing filters (prereg §1: "established listings", entire home, reviewed in the last twelve months) ----------
ROOM_TYPE_EH = "Entire home/apt"
MIN_REVIEWS_LTM = 0                    # strictly greater than this
MIN_USD_LEVEL = 5.0                    # a median below $5 a night is a broken price field, not a cheap market
PRICE_COLS = ["price", "price_quote_price_per_night", "room_type", "number_of_reviews_ltm", "accommodates"]


# ---------------------------------------------------------------------------------------------------------------- #
# (0) the market -> currency map
# ---------------------------------------------------------------------------------------------------------------- #
def fred_currencies() -> set[str]:
    """Currencies carried by the FRED H.10 files in this engine's folder (plus USD itself)."""
    ccys = {"USD"}
    for f in FRED_FX_FILES:
        if Path(f).exists():
            ccys |= set(pd.read_csv(f, usecols=["ccy"]).ccy.unique())
    return ccys


def currency_map(path: Path | str = E_MARKET_MONTHLY) -> pd.DataFrame:
    """One row per panel market: market_key, country, region, destination currency, and whether FRED H.10 carries it.
    `fx_available` is a provenance flag only — CZK/HUF/TRY/BZD are False yet are converted, from the ECB/peg file."""
    e = pd.read_csv(path, usecols=["market_key", "country", "region"]).drop_duplicates()
    e = e.sort_values("market_key").reset_index(drop=True)
    missing = sorted(set(e.country) - set(COUNTRY_CCY))
    if missing:
        raise KeyError(f"COUNTRY_CCY has no entry for: {missing}")
    e["currency"] = e.country.map(COUNTRY_CCY)
    fred = fred_currencies()
    e["fx_available"] = e.currency.isin(fred)
    return e


# ---------------------------------------------------------------------------------------------------------------- #
# (a) vintage-matched stays y/y by country-quarter
# ---------------------------------------------------------------------------------------------------------------- #
def country_stays(path: Path | str = E_MARKET_MONTHLY) -> pd.DataFrame:
    """Sum the E package's vintage-matched monthly counts (n_vm_cur, n_vm_prior) over market-months to country-quarter.
    A market enters a quarter only when all three of its months are present in the vintage-matched panel (so a market
    that started or stopped mid-quarter cannot tilt the quarter); the counts are summed over every vintage pair the
    E file carries for that market, which cancels in the ratio and in the shares."""
    e = pd.read_csv(path)
    e = e.dropna(subset=["n_vm_cur", "n_vm_prior"]).copy()
    e["p"] = pd.PeriodIndex(pd.to_datetime(e.ym), freq="Q")
    mk = e.groupby(["market_key", "country", "region", "p"], as_index=False).agg(
        n_cur=("n_vm_cur", "sum"), n_prior=("n_vm_prior", "sum"), n_months=("ym", "nunique"))
    mk = mk[mk.n_months == 3]
    c = mk.groupby(["country", "region", "p"], as_index=False).agg(
        n_cur=("n_cur", "sum"), n_prior=("n_prior", "sum"), n_mkts=("market_key", "nunique"))
    c["stays_yoy_pct"] = (c.n_cur / c.n_prior - 1.0) * 100.0
    c["quarter"] = c.p.map(C.period_to_qlabel)
    c["q"] = c.p.astype(str)
    c = c.drop(columns="p").sort_values(["country", "q"]).reset_index(drop=True)
    return c[["country", "region", "q", "n_cur", "n_prior", "n_mkts", "stays_yoy_pct", "quarter"]]


# ---------------------------------------------------------------------------------------------------------------- #
# (b) market price levels from the capture store
# ---------------------------------------------------------------------------------------------------------------- #
def fx_year_average(year: int = FX_YEAR) -> pd.Series:
    """Calendar-year average USD-per-unit for every currency in the FRED + ECB/peg files (mean over printed days)."""
    frames = [pd.read_csv(f, parse_dates=["date"]) for f in (FRED_FX_FILES + PEG_FX_FILES) if Path(f).exists()]
    d = pd.concat(frames, ignore_index=True)
    d = d[d.date.dt.year == year]
    s = d.groupby("ccy").usd_per_unit.mean()
    s.loc["USD"] = 1.0
    return s.sort_index()


def _clean_price(s: pd.Series) -> pd.Series:
    """'$1,068.99' -> 1068.99; anything with no digits, or a zero price, -> NaN (a zero is a missing quote)."""
    v = pd.to_numeric(s.astype(str).str.replace(r"[^0-9.]", "", regex=True).replace("", np.nan), errors="coerce")
    return v.where(v > 0)


def latest_dumps(root: Path = CAPTURE_ROOT) -> list[tuple[str, str, Path]]:
    """(market_key, country, dump directory) for the latest dump of every market in the capture store, by market_key."""
    out = []
    if not root.exists():
        return out
    for country in sorted(p for p in root.iterdir() if p.is_dir() and p.name not in SKIP_DIRS):
        for state in sorted(p for p in country.iterdir() if p.is_dir()):
            for market in sorted(p for p in state.iterdir() if p.is_dir()):
                dumps = sorted(p for p in market.iterdir() if p.is_dir() and (p / "listings.csv.gz").exists())
                if dumps:
                    out.append((f"{country.name}_{state.name}_{market.name}", country.name, dumps[-1]))
    return sorted(out)


def market_row(market_key: str, dump: Path) -> dict:
    """Median and review-weighted mean nightly price of the market's established entire-home listings, in local units."""
    d = pd.read_csv(dump / "listings.csv.gz", usecols=PRICE_COLS, low_memory=False)
    eh = d[(d.room_type == ROOM_TYPE_EH) & (d.number_of_reviews_ltm > MIN_REVIEWS_LTM)].copy()
    eh["listed"] = _clean_price(eh.price)
    q = pd.to_numeric(eh.price_quote_price_per_night, errors="coerce")
    eh["quote"] = q.where(q > 0)
    a = eh.dropna(subset=["listed"]); b = eh.dropna(subset=["quote"])
    row = {"market_key": market_key, "dump_date": dump.name, "n_listed": len(a), "n_quote": len(b),
           "median_listed_local": float(a.listed.median()) if len(a) else np.nan,
           "median_quote_local": float(b.quote.median()) if len(b) else np.nan,
           "rw_mean_listed_local": float(np.average(a.listed, weights=a.number_of_reviews_ltm)) if len(a) else np.nan,
           "rw_mean_quote_local": float(np.average(b.quote, weights=b.number_of_reviews_ltm)) if len(b) else np.nan,
           "mean_accommodates_eh": float(eh.accommodates.mean()) if len(eh) else np.nan}
    return row


def market_prices(cmap: pd.DataFrame, fx: pd.Series, root: Path = CAPTURE_ROOT, verbose: bool = True) -> pd.DataFrame:
    """(b) one row per captured market: local medians, the country's currency, and the USD conversion."""
    ctry = cmap.drop_duplicates("country").set_index("country")[["region", "currency", "fx_available"]]
    rows = []
    for mk, country, dump in latest_dumps(root):
        if country not in ctry.index:
            if verbose:
                print(f"  ! capture country not in the panel map, skipped: {country}")
            continue
        rows.append(market_row(mk, dump) | {"country": country})
    m = pd.DataFrame(rows)
    if m.empty:
        raise RuntimeError(f"no listings.csv.gz found under {root}")
    m = m.join(ctry, on="country")
    m["usd_per_unit"] = m.currency.map(fx)
    for col in ("median_listed", "median_quote", "rw_mean_listed", "rw_mean_quote"):
        m[col + "_usd"] = m[col + "_local"] * m.usd_per_unit
    return m.sort_values("market_key").reset_index(drop=True)


# ---------------------------------------------------------------------------------------------------------------- #
# (c) country price levels
# ---------------------------------------------------------------------------------------------------------------- #
def country_prices(mp: pd.DataFrame, min_usd: float = MIN_USD_LEVEL) -> pd.DataFrame:
    """One USD price level per country: n_listed-weighted mean of its priced markets' median entire-home price."""
    x = mp.dropna(subset=["median_listed_usd"])
    x = x[x.median_listed_usd >= min_usd]
    rows = []
    for (country, region), g in x.groupby(["country", "region"]):
        rows.append({"country": country, "region": region,
                     "usd_level": float(np.average(g.median_listed_usd, weights=g.n_listed)),
                     "n_markets_priced": float(len(g))})
    return pd.DataFrame(rows).sort_values("country").reset_index(drop=True)


# ---------------------------------------------------------------------------------------------------------------- #
# coverage + reproduction check
# ---------------------------------------------------------------------------------------------------------------- #
def coverage(cmap: pd.DataFrame, mp: pd.DataFrame, cp: pd.DataFrame, stays: pd.DataFrame) -> str:
    panel_countries = sorted(set(stays.country))            # countries with at least one full quarter in the panel
    priced = set(cp.country)
    no_fx = sorted(mp.loc[mp.median_listed_usd.isna(), "market_key"])
    low = sorted(mp.loc[mp.median_listed_usd.notna() & (mp.median_listed_usd < MIN_USD_LEVEL), "market_key"])
    kept = int(mp.median_listed_usd.notna().sum()) - len(low)
    L = ["  coverage",
         f"    panel markets (E)            {len(cmap):4d}   countries {len(set(cmap.country)):3d}",
         f"    capture markets found        {len(mp):4d}   countries {len(set(mp.country)):3d}",
         f"    capture markets priced       {kept:4d}"
         f"   (dropped: no FX rate {len(no_fx)}, below ${MIN_USD_LEVEL:.0f}/night {len(low)})",
         f"    countries priced             {len(priced):4d}",
         f"    markets with no FX rate      {', '.join(no_fx) or '-'}",
         f"    markets below the floor      {', '.join(low) or '-'}",
         f"    panel countries unpriced     {', '.join(sorted(set(panel_countries) - priced)) or '-'}"
         f"   (imputed at the region median in geomix.build_term)",
         f"    countries with no capture    {', '.join(sorted(set(cmap.country) - set(mp.country))) or '-'}",
         f"    priced but outside the panel {', '.join(sorted(priced - set(panel_countries))) or '-'}"]
    return "\n".join(L)


def reproduction_check(cp: pd.DataFrame, ref_path: Path, decimals: int = 3) -> float | None:
    """Max |new - saved| on usd_level against the file on disk, before it is overwritten. None if there is no file."""
    if not Path(ref_path).exists():
        print("  reproduction check: no saved country_price_levels_usd.csv to compare against (first build)")
        return None
    ref = pd.read_csv(ref_path)
    m = ref.merge(cp, on=["country", "region"], how="outer", suffixes=("_saved", "_new"), indicator=True)
    only = m[m._merge != "both"]
    d = (m.usd_level_saved - m.usd_level_new).abs()
    mx = float(d.max()) if d.notna().any() else float("nan")
    tol = 0.5 * 10 ** (-decimals)
    ok = bool(only.empty) and (mx == mx) and mx < tol
    print(f"  reproduction check: country_price_levels_usd.csv max |diff| = {mx:.3e} USD on {len(m)} countries"
          f"  -> {'OK to 3 decimals' if ok else 'CHANGED'}")
    if not only.empty:
        print("    country set changed:", ", ".join(f"{r.country}({r._merge})" for r in only.itertuples()))
    return mx


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description="rebuild the geo-mix term's three inputs from the raw stores")
    ap.add_argument("--capture-root", default=str(CAPTURE_ROOT))
    ap.add_argument("--quiet", action="store_true", help="suppress the per-market skip warnings (the coverage table still prints)")
    a = ap.parse_args(argv)
    C.OUT.mkdir(parents=True, exist_ok=True)
    print("refresh_prices: rebuilding the sub-regional geo-mix inputs")

    cmap = currency_map()
    assert cmap.loc[cmap.market_key == HONG_KONG_MARKET, "currency"].eq("HKD").all(), "Hong Kong must price in HKD"
    cmap.to_csv(C.OUT / "market_currency_map.csv", index=False)

    stays = country_stays()
    stays.to_csv(C.OUT / "stays_yoy_by_country_vmatch.csv", index=False)

    fx = fx_year_average()
    mp = market_prices(cmap, fx, root=Path(a.capture_root), verbose=not a.quiet)
    mp.to_csv(C.OUT / "market_price_levels_capture_2026.csv", index=False)

    cp = country_prices(mp)
    mx = reproduction_check(cp, C.OUT / "country_price_levels_usd.csv")
    cp.to_csv(C.OUT / "country_price_levels_usd.csv", index=False)

    print(coverage(cmap, mp, cp, stays))
    print(f"  fx: {FX_YEAR} calendar-year averages for {len(fx)} currencies; stays panel"
          f" {stays.quarter.nunique()} quarters x {stays.country.nunique()} countries")
    return {"markets_found": int(len(mp)), "markets_priced": int(mp.median_listed_usd.notna().sum()),
            "countries_priced": int(len(cp)), "country_price_max_abs_diff": mx}


if __name__ == "__main__":
    main()
