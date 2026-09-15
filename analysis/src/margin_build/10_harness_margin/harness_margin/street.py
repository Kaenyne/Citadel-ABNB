"""Vintage-stamped Street (LSEG, from WS03) for the margin targets.

WS03 `03_consensus_at_dates.csv` stamps the LSEG mean at each print/guide date. The roles we use:
  guided_q_pre_guide   value on the trading day BEFORE the guide date for the quarter being guided
                       (h = 0 at that guide date). as_of = calcdate_used (D-1).
  next_q_pre_guide     same, for the quarter after (h = 1).
  current_q / current_next_q  the 11 Sep 2026 row (as_of 2026-09-11) for 3Q26 / 4Q26 -> LIVE.
Writes street_margin_pit.csv, long: vintage_date, quarter, horizon_q, target, value, vendor, as_of, n.
Mapping of LSEG fields to margin targets:
  ebitda_mean -> adj_ebitda_musd (LSEG "EBITDA" for ABNB is the adjusted basis; actuals equal the letter)
  implied_margin_pct (= ebitda_mean / revenue_mean) -> adj_ebitda_margin_pct
  revenue_mean -> revenue_musd; eps_mean -> eps_diluted (Street EPS basis; matches GAAP diluted to the
  cent in W2 per WS03, 3Q23/4Q23 excepted); ebit_mean -> op_income_musd; netprofit_mean ->
  net_income_musd; fcf_mean -> fcf_musd. cogs_mean is GAAP COGS (includes SBC/D&A) and is not mapped.
"""
from __future__ import annotations

import pandas as pd

from . import paths as P
from .frozen import Q, TODAY

FIELD_MAP = {
    "ebitda_mean": "adj_ebitda_musd",
    "implied_margin_pct": "adj_ebitda_margin_pct",
    "revenue_mean": "revenue_musd",
    "eps_mean": "eps_diluted",
    "ebit_mean": "op_income_musd",
    "netprofit_mean": "net_income_musd",
    "fcf_mean": "fcf_musd",
}
N_MAP = {"ebitda_mean": "ebitda_n", "implied_margin_pct": "ebitda_n", "revenue_mean": "revenue_n",
         "eps_mean": "eps_n", "ebit_mean": "ebit_n"}
OBS_MAP = {"ebitda_mean": "ebitda_obs_date", "implied_margin_pct": "ebitda_obs_date",
           "revenue_mean": "revenue_obs_date", "eps_mean": "eps_obs_date", "ebit_mean": "ebit_obs_date",
           "netprofit_mean": "netprofit_obs_date", "fcf_mean": "fcf_obs_date"}


def build_street(write: bool = True) -> pd.DataFrame:
    if not P.SRC_WS03_CONS.exists():
        out = pd.DataFrame(columns=["vintage_date", "quarter", "horizon_q", "target", "value",
                                    "vendor", "as_of", "n_est", "obs_date", "role"])
        if write:
            out.to_csv(P.OUT_STREET, index=False)
        return out
    d = pd.read_csv(P.SRC_WS03_CONS)
    d = d[d["found"].astype(str).str.lower() == "true"].copy()
    rows = []
    for r in d.itertuples():
        role = r.target_role
        if role in ("guided_q_pre_guide", "next_q_pre_guide"):
            vintage = pd.to_datetime(r.date).date()
            h = 0 if role == "guided_q_pre_guide" else 1
        elif role in ("current_q", "current_next_q"):
            vintage = TODAY
            h = 0 if role == "current_q" else 1
        else:
            continue
        try:
            q = Q.canon(r.target_period)
        except ValueError:
            continue
        as_of = pd.to_datetime(r.calcdate_used).date() if pd.notna(r.calcdate_used) else None
        if as_of is None or as_of > vintage:
            continue                       # never a later-vintage number
        rd = r._asdict()
        for fld, tgt in FIELD_MAP.items():
            v = rd.get(fld)
            if v is None or pd.isna(v):
                continue
            rows.append({"vintage_date": vintage, "quarter": q, "horizon_q": h, "target": tgt,
                         "value": float(v), "vendor": "LSEG", "as_of": as_of,
                         "n_est": rd.get(N_MAP.get(fld, ""), None),
                         "obs_date": rd.get(OBS_MAP.get(fld, ""), None), "role": role,
                         "lseg_field": fld})
    out = pd.DataFrame(rows).sort_values(["target", "vintage_date", "quarter"]).reset_index(drop=True)
    if write:
        P.ensure_dirs()
        out.to_csv(P.OUT_STREET, index=False)
    return out


_CACHE = {}


def load_street() -> pd.DataFrame:
    if "s" in _CACHE:
        return _CACHE["s"]
    if not P.OUT_STREET.exists():
        build_street()
    s = pd.read_csv(P.OUT_STREET)
    if len(s):
        s["vintage_date"] = pd.to_datetime(s["vintage_date"]).dt.date
        s["as_of"] = pd.to_datetime(s["as_of"]).dt.date
        s["quarter"] = s["quarter"].map(Q.canon)
    _CACHE["s"] = s
    return s
