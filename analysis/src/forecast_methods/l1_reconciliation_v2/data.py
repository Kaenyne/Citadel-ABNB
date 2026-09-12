"""l1-reconciliation-v2: data loaders and exogenous assumption blocks.

COPY of `l1_reconciliation/data.py` (task B3).  The ONLY change is the output
directory: v2 writes to `data/processed/forecast_methods/l1_reconciliation_v2/`
and reads the v1 artefacts from `SRC_V1` READ-ONLY.  Nothing under
`l1_reconciliation/` is ever written by this package.

NUMERAIRE HEADER (binding, required by the addendum)
----------------------------------------------------
This package hands **reported ADR** (GBV in reported USD divided by units), NOT
host payout per night, and NOT usd_constant.  It does **not** de-gross-up the
fee migration.  The single de-gross-up equation lives in `fee-takerate` and only
there.  Every ADR number produced here is reported-basis; every ex-FX ADR number
here is reported ADR with the disclosed (or basket-implied) FX pp removed, which
is the letters' own definition.

BOUNDARY RULE (written also into model/assumptions.md)
------------------------------------------------------
Exactly ONE object crosses the l1 boundary onward: **GBV in USD, booking-dated,
one number per quarter**.  Nights, ADR, regional mix, unit size, LOS, seats and
regulation do NOT cross the boundary.  Downstream packages consume `gbv_musd`
only.
"""
from __future__ import annotations

import pathlib
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
DATA = REPO / "data" / "processed"
L0 = DATA / "forecast_methods" / "L0"
OUT = DATA / "forecast_methods" / "l1_reconciliation_v2"      # v2 writes HERE, only here
SRC_V1 = DATA / "forecast_methods" / "l1_reconciliation"       # v1 artefacts: READ-ONLY
REGISTRY = DATA / "forecast_methods" / "registry"
OUT.mkdir(parents=True, exist_ok=True)

REGIONS = ["na", "emea", "latam", "apac"]
REF_REGION = "apac"  # softmax reference; its logit is pinned at 0

# ---------------------------------------------------------------- quarter keys
def to_canon(q: str) -> str:
    """'1Q22' -> '2022Q1'.  Passes '2022Q1' through."""
    q = str(q).strip()
    if "Q" in q and q[0].isdigit() and len(q) == 4:
        n, yy = q[0], q[2:]
        return f"20{yy}Q{n}"
    return q


def to_short(q: str) -> str:
    """'2022Q1' -> '1Q22'."""
    q = str(q).strip()
    if len(q) == 6 and q[4] == "Q":
        return f"{q[5]}Q{q[2:4]}"
    return q


def qorder(q: str) -> int:
    c = to_canon(q)
    return int(c[:4]) * 4 + int(c[5]) - 1


def qadd(q: str, k: int) -> str:
    o = qorder(q) + k
    return f"{o // 4}Q{o % 4 + 1}"


def qend_date(q: str):
    """Calendar end date of a quarter key.  Used for the harness FX rule: a
    quarterly FX aggregate is only knowable once its last day is behind us."""
    c = to_canon(q)
    y, n = int(c[:4]), int(c[5])
    m, d = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}[n]
    return __import__("datetime").date(y, m, d)


# ---------------------------------------------------------------- L0 spine
def load_exact_regional_revenue() -> pd.DataFrame:
    d = pd.read_csv(L0 / "L0_exact_regional_revenue.csv")
    d["quarter"] = d["quarter"].map(to_canon)
    d["knowable_from"] = pd.to_datetime(d["knowable_from"]).dt.date
    return d[["quarter", "region", "revenue_musd", "basis", "knowable_from"]].copy()


def load_intervals() -> pd.DataFrame:
    d = pd.read_csv(L0 / "L0_interval_observations.csv", comment="#")
    d = d[d["included"].astype(str).str.lower().isin(["true", "1"])].copy()
    d["knowable_from"] = pd.to_datetime(d["knowable_from"]).dt.date
    d["is_annual"] = d["quarter_or_year"].astype(str).str.startswith("FY")
    d["quarter"] = np.where(d["is_annual"], d["quarter_or_year"],
                            d["quarter_or_year"].map(to_canon))
    return d


# ---------------------------------------------------------------- KPI panel
def load_kpi() -> pd.DataFrame:
    k = pd.read_csv(DATA / "overnight" / "02_kpi_panel_quarterly.csv")
    k["quarter"] = k["quarter"].map(to_canon)
    k = k[["quarter", "nights_m", "gbv_musd", "revenue_musd", "adr_usd",
           "take_rate_pct"]].copy()
    k = k.sort_values("quarter", key=lambda s: s.map(qorder)).reset_index(drop=True)
    return k


# ---------------------------------------------------------------- seats / hotels
# Exogenous, dated, NEVER fitted.  Source: research/notes/2026-09-09_seats-dilution.md
# and data/processed/adr/15_seats_dilution_annual.csv (base case).  Pre-2024 annual
# non-home units are BACK-EXTRAPOLATED here and are labelled `assumed_backcast`.
NONHOME_ANNUAL = {
    # year: (hotel_nights_m, experiences_seats_m, services_seats_m, basis)
    2021: (5.04, 3.00, 0.0, "assumed_backcast"),
    2022: (6.55, 3.50, 0.0, "assumed_backcast"),
    2023: (10.66, 4.50, 0.0, "assumed_backcast"),
    2024: (14.3846, 5.3333, 0.0, "seats_file_base"),
    2025: (18.70, 6.00, 0.6667, "seats_file_base"),
    2026: (25.245, 9.00, 2.3333, "seats_file_base"),
    2027: (32.8185, 13.0667, 5.1111, "seats_file_base"),
}
RHO = {"hotel": 0.8062059473031431, "exp": 0.43189604319811237, "svc": 0.6910336691169798}

NONHOME_CASES = {  # sensitivity: multiplier on all non-home unit counts
    "low": 0.60, "base": 1.00, "high": 1.45,
}


def nonhome_units(quarters: list[str], kpi: pd.DataFrame, case: str = "base") -> pd.DataFrame:
    """Split annual non-home units across quarters in proportion to printed
    Nights-and-Seats.  Returns per-quarter unit counts and the rho-weighted
    GBV-equivalent unit count."""
    mult = NONHOME_CASES[case]
    kk = kpi.set_index("quarter")["nights_m"]
    rows = []
    for q in quarters:
        yr = int(q[:4])
        if yr not in NONHOME_ANNUAL:
            yr = max(NONHOME_ANNUAL)
        h, e, s, basis = NONHOME_ANNUAL[yr]
        yq = [f"{yr}Q{i}" for i in range(1, 5)]
        tot = sum(float(kk[x]) for x in yq if x in kk.index)
        if tot <= 0 or q not in kk.index:
            w = 0.25
        else:
            w = float(kk[q]) / tot
        rows.append(dict(quarter=q, hotel_m=h * w * mult, exp_m=e * w * mult,
                         svc_m=s * w * mult, basis=basis, share_of_year=w))
    d = pd.DataFrame(rows)
    d["nonhome_units_m"] = d[["hotel_m", "exp_m", "svc_m"]].sum(axis=1)
    d["nonhome_gbv_equiv_m"] = (d["hotel_m"] * RHO["hotel"] + d["exp_m"] * RHO["exp"]
                                + d["svc_m"] * RHO["svc"])
    return d


def denominator_identity(kpi: pd.DataFrame, quarters: list[str], case="base") -> pd.DataFrame:
    """N = n_home + n_hotel + s_exp + s_svc, and the closed-form home price.

    GBV_q = p_home * (n_home + sum_k units_k * rho_k)  =>  p_home solved exactly,
    so seats/hotel dilution of reported ADR is an OUTPUT, not an input.
    """
    nh = nonhome_units(quarters, kpi, case)
    k = kpi.set_index("quarter")
    d = nh.copy()
    d["nights_total_m"] = d["quarter"].map(k["nights_m"])
    d["gbv_musd"] = d["quarter"].map(k["gbv_musd"])
    d["revenue_musd"] = d["quarter"].map(k["revenue_musd"])
    d["n_home_m"] = d["nights_total_m"] - d["nonhome_units_m"]
    d["p_home_usd"] = d["gbv_musd"] / (d["n_home_m"] + d["nonhome_gbv_equiv_m"])
    d["home_gbv_musd"] = d["p_home_usd"] * d["n_home_m"]
    d["adr_reported_usd"] = d["gbv_musd"] / d["nights_total_m"]
    d["dilution_pct"] = 100.0 * (d["adr_reported_usd"] / d["p_home_usd"] - 1.0)
    return d


# ---------------------------------------------------------------- regional FX
FX_WEIGHTS = {  # GBV-weighted regional baskets; USD weight = 1 - sum (zero y/y)
    "na":    {"CAD": 0.15},
    "emea":  {"EUR": 0.60, "GBP": 0.28},
    "latam": {"BRL": 0.45, "MXN": 0.45},
    "apac":  {"AUD": 0.30, "JPY": 0.25, "KRW": 0.15, "INR": 0.15},
}


def load_fx_basket_yoy() -> pd.DataFrame:
    raw = pd.read_csv(DATA / "overnight" / "10_fx_quarterly.csv", header=[0, 1], index_col=0)
    yoy = raw["yoy_pct"]
    yoy.index = [to_canon(i) for i in yoy.index]
    pt = pd.read_csv(DATA / "overnight" / "10_regional_fx_passthrough.csv").set_index("region")
    rows = []
    for q in yoy.index:
        for r, w in FX_WEIGHTS.items():
            b = 0.0
            ok = True
            for ccy, wt in w.items():
                v = yoy.loc[q, ccy] if ccy in yoy.columns else np.nan
                if pd.isna(v):
                    ok = False
                else:
                    b += wt * float(v)
            slope = float(pt.loc[r, "slope_pp_per_pp"]) if r in pt.index else 1.0
            rows.append(dict(quarter=q, region=r, basket_yoy_pct=b if ok else np.nan,
                             fx_pp_basket=slope * b if ok else np.nan, slope=slope))
    return pd.DataFrame(rows)


def fx_pp_table(intervals: pd.DataFrame, as_of=None) -> pd.DataFrame:
    """Regional FX pp on ADR y/y.  Preferred source: the letters themselves, where
    BOTH the reported and the ex-FX integer are disclosed for the same cell, so
    fx_pp = mid(reported) - mid(exfx).  Fallback: the weighted basket x the
    regional pass-through slope.

    POINT-IN-TIME (harness FX rule, verification round 1 fix): when `as_of` is a
    date the table is rebuilt on the information set at that date -- FX cut at
    as_of - 1 day, i.e. only quarters whose LAST DAY is strictly before `as_of`
    contribute a basket value, and only letter integers with
    knowable_from <= as_of contribute a disclosed pair.  Callers inside a PIT
    refit MUST pass as_of and MUST pass an already knowable_from-filtered
    `intervals`.  With as_of=None the full sample is used (full-sample replay
    and the LIVE/TODAY objects only)."""
    bas = load_fx_basket_yoy()
    if as_of is not None:
        cut = as_of - __import__("datetime").timedelta(days=1)
        bas = bas[[qend_date(q) <= cut for q in bas["quarter"]]].copy()
        intervals = intervals[intervals["knowable_from"] <= as_of]
    iv = intervals[~intervals["is_annual"]]
    rep = iv[iv.metric == "adr_yoy_reported_pct"].set_index(["quarter", "region"])
    exf = iv[iv.metric == "adr_yoy_exfx_pct"].set_index(["quarter", "region"])
    out = []
    for _, row in bas.iterrows():
        key = (row.quarter, row.region)
        src, val = "basket", row.fx_pp_basket
        if key in rep.index and key in exf.index:
            a = (float(rep.loc[key, "lo"]) + float(rep.loc[key, "hi"])) / 2
            b = (float(exf.loc[key, "lo"]) + float(exf.loc[key, "hi"])) / 2
            val, src = a - b, "disclosed_pair"
        out.append(dict(quarter=row.quarter, region=row.region, fx_pp=val,
                        fx_pp_basket=row.fx_pp_basket, source=src))
    return pd.DataFrame(out)
