"""l0 — the ONLY reader for Layer 0, the constraint spine.

No model reads a disclosure except through this module. Import it, do not re-parse
10_xbrl_revenue_geography.csv, 10_regional_panel_quarterly.csv, 02_guidance_ledger.csv,
04_current_consensus.csv or 04/16_consensus_at_print*.csv yourself.

    import sys; sys.path.insert(0, "<repo>/analysis/src/forecast_methods/L0")
    import l0
    rev  = l0.load_exact_regional_revenue()          # 72 cells
    obs  = l0.load_interval_observations()           # 172 rows, derived rows dropped
    reg  = l0.load_vintage_register()                # 127 consensus values
    st   = l0.pit_consensus("revenue", "2026Q3", "2026-08-06")   # -> None (strictly before)
    st   = l0.pit_consensus("revenue", "2026Q3", "2026-08-07")   # -> LSEG 4610.0

Defaults that are not negotiable:
  * load_interval_observations() drops basis == 'derived' unless include_derived=True.
  * pit_consensus() uses a STRICT inequality on the vintage and ignores pit_usable == False.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from _paths import OUT  # noqa: E402

F_REVENUE = OUT / "L0_exact_regional_revenue.csv"
F_INTERVALS = OUT / "L0_interval_observations.csv"
F_VINTAGE = OUT / "L0_vintage_register.csv"

REGIONS = ("na", "emea", "latam", "apac")


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} is missing. Build Layer 0 first:\n"
            f"  python "
            f"analysis/src/forecast_methods/L0/run.py")
    return pd.read_csv(path, comment="#")


# --------------------------------------------------------------------------- #
# File 1
# --------------------------------------------------------------------------- #
def load_exact_regional_revenue(basis: Optional[str] = None) -> pd.DataFrame:
    """72 exact regional revenue cells: 56 filed three-month + 16 Q4 back-outs.

    basis: None (all 72), 'filed' (56) or 'back_out' (16).
    """
    df = _read(F_REVENUE)
    if basis is not None:
        df = df[df["basis"] == basis].reset_index(drop=True)
    return df


def regional_revenue_wide() -> pd.DataFrame:
    """The same spine pivoted to quarter x region, with a `total` column."""
    df = load_exact_regional_revenue()
    w = df.pivot(index="quarter", columns="region", values="revenue_musd")
    w = w[[r for r in REGIONS if r in w.columns]]
    w["total"] = w.sum(axis=1)
    order = sorted(w.index, key=lambda q: (int(q[2:]), int(q[0])))
    return w.loc[order]


# --------------------------------------------------------------------------- #
# File 2
# --------------------------------------------------------------------------- #
def load_interval_observations(include_derived: bool = False,
                               include_live: bool = True,
                               metric: Optional[str] = None) -> pd.DataFrame:
    """Interval observations. `derived` rows are dropped by default and must stay dropped
    in every likelihood; include_derived=True is for audit only.

    include_live=False additionally drops rows with scoreable == False (the LIVE 3Q26 and
    FY2026 guides), which enter no metric and no gate.
    """
    df = _read(F_INTERVALS)
    for c in ("included", "scoreable"):
        df[c] = df[c].astype(str).str.lower().isin(("true", "1"))
    if not include_derived:
        df = df[df["included"]]
    if not include_live:
        df = df[df["scoreable"]]
    if metric is not None:
        df = df[df["metric"] == metric]
    return df.reset_index(drop=True)


def interval_likelihood_rows(as_of: Optional[str] = None) -> pd.DataFrame:
    """Exactly the rows a likelihood may use: derived dropped, LIVE dropped, and
    (optionally) restricted to rows knowable strictly before `as_of`."""
    df = load_interval_observations(include_derived=False, include_live=False)
    if as_of is not None:
        df = df[df["knowable_from"].astype(str) < str(as_of)]
    return df.reset_index(drop=True)


# --------------------------------------------------------------------------- #
# File 3
# --------------------------------------------------------------------------- #
def load_vintage_register(role: Optional[str] = None,
                          pit_usable_only: bool = False) -> pd.DataFrame:
    """Consensus values with vendor, period, metric, value, n_estimates, as_of, url."""
    df = _read(F_VINTAGE)
    df["pit_usable"] = df["pit_usable"].astype(str).str.lower().isin(("true", "1"))
    if role is not None:
        df = df[df["role"] == role]
    if pit_usable_only:
        df = df[df["pit_usable"]]
    return df.reset_index(drop=True)


def pit_consensus(metric: str, period: str, as_of: str,
                  vendor: Optional[str] = None,
                  role: Optional[str] = None) -> Optional[dict]:
    """The latest consensus value for (metric, period) whose vintage is STRICTLY before
    `as_of`. Returns a dict (vendor, value, n_estimates, as_of_timestamp, url, role,
    source_path) or None if nothing qualifies.

    Rows with pit_usable == False (vintage_unknown or value missing) are never returned.
    Ties on as_of are broken toward the row with the larger n_estimates, then by vendor
    name, so the function is deterministic.
    """
    df = load_vintage_register(pit_usable_only=True)
    m = (df["metric"] == metric) & (df["period"] == period)
    if vendor is not None:
        m &= df["vendor"].str.contains(vendor, case=False, na=False)
    if role is not None:
        m &= df["role"] == role
    df = df[m & (df["as_of_timestamp"].astype(str) < str(as_of))]
    if df.empty:
        return None
    df = df.assign(_n=pd.to_numeric(df["n_estimates"], errors="coerce").fillna(-1))
    df = df.sort_values(["as_of_timestamp", "_n", "vendor"], ascending=[True, True, True])
    r = df.iloc[-1]
    return {
        "vendor": r["vendor"], "period": r["period"], "metric": r["metric"],
        "value": float(r["value"]), "unit": r["unit"],
        "n_estimates": None if pd.isna(r["n_estimates"]) else r["n_estimates"],
        "as_of_timestamp": r["as_of_timestamp"], "url": r["url"],
        "role": r["role"], "source_path": r["source_path"],
    }


def pre_guide_street(period: str) -> Optional[dict]:
    """The vintage-stamped PRE-guide Street revenue consensus for a target quarter --
    the only Street baseline a gate may use. For 2026Q3 this is LSEG $4,610M @ 2026-08-06.
    """
    df = load_vintage_register(role="pre_guide", pit_usable_only=True)
    df = df[(df["period"] == period) & (df["metric"] == "revenue")]
    if df.empty:
        return None
    r = df.iloc[0]
    return {"vendor": r["vendor"], "period": r["period"], "value": float(r["value"]),
            "as_of_timestamp": r["as_of_timestamp"], "source_path": r["source_path"]}


__all__ = [
    "load_exact_regional_revenue", "regional_revenue_wide",
    "load_interval_observations", "interval_likelihood_rows",
    "load_vintage_register", "pit_consensus", "pre_guide_street",
]
