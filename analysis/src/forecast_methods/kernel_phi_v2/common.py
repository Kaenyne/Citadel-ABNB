"""kernel_phi_v2 — shared panel construction.

COPY-NEVER-OVERWRITE: this package is a new copy seeded from
`analysis/src/forecast_methods/kernel_lambda/kernel.py` (panel + simplex machinery)
and `analysis/src/forecast_methods/tracker_backlog/{common,rebuild}.py` (backlog
rebuild).  Nothing under those packages is imported or modified.

Everything here reads only PRINTED quantities:
  data/processed/overnight/02_kpi_panel_quarterly.csv
  data/processed/abnb_backlog_indicators.csv
  data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv

The circular `unearned_fees_restated = reported/(1-d_q)` series is NEVER built,
read or used here (struck by tracker-backlog T1).
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
KPI = os.path.join(REPO, "data", "processed", "overnight", "02_kpi_panel_quarterly.csv")
BACKLOG = os.path.join(REPO, "data", "processed", "abnb_backlog_indicators.csv")
D1 = os.path.join(REPO, "data", "processed", "overnight2", "D",
                  "D1_rnpl_cohort_scenarios.csv")
OUT = os.path.join(REPO, "data", "processed", "forecast_methods", "kernel_phi_v2")

SEASON_NAME = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}

# printed / disclosed live inputs, all from the 2Q26 letter (6 Aug 2026)
GBV_2Q26 = 27_200.0
GBV_1Q26 = 29_200.0
GBV_4Q25 = 20_400.0
GBV_3Q25 = 22_900.0
GUIDE_3Q26_MID = 4_730.0


def canon(q: str) -> str:
    """'3Q26' -> '2026Q3'; passes '2026Q3' through."""
    s = str(q).strip().upper()
    if len(s) == 6 and s[4] == "Q":
        return s
    return f"20{s[2:4]}Q{s[0]}"


def label(q: str) -> str:
    """'2026Q3' -> '3Q26'."""
    return f"{q[-1]}Q{q[2:4]}"


def qidx(q: str) -> int:
    return int(q[:4]) * 4 + int(q[-1]) - 1


def build_panel(kmax: int = 4) -> pd.DataFrame:
    """Revenue / GBV / nights / balance-sheet panel with GBV lags 0..kmax."""
    d = pd.read_csv(KPI)
    keep = ["quarter", "revenue_musd", "gbv_musd", "nights_m",
            "unearned_fees_musd", "funds_held_for_clients_musd",
            "nights_yoy_pct", "gbv_yoy_pct", "revenue_yoy_pct",
            "unearned_fees_yoy_pct", "funds_held_yoy_pct", "take_rate_pct"]
    d = d[keep].copy()
    d["q"] = d["quarter"].map(canon)
    d = d.sort_values("q").reset_index(drop=True)
    idx = [qidx(x) for x in d["q"]]
    assert np.all(np.diff(idx) == 1), "panel is not a contiguous quarterly index"
    for k in range(0, kmax + 1):
        d[f"gbv_l{k}"] = d["gbv_musd"].shift(k)
    d["season"] = d["q"].str[-1].astype(int)
    d["season_name"] = d["season"].map(SEASON_NAME)
    d["label"] = d["q"].map(label)
    # PAID backlog, as defined in 03_insider_mechanics.md 1.3 from the 10-Q lines:
    #   unearned fees  = Airbnb's own service fee already collected in cash on
    #                    bookings that have not yet checked in (fee-denominated,
    #                    refundable, NOT an ASC-606 contract balance)
    #   funds payable  = the host's share of guest cash held on behalf of customers
    #                    (booking-amount-denominated, net of service fees)
    d["paid_backlog_musd"] = d["unearned_fees_musd"] + d["funds_held_for_clients_musd"]
    d["next_revenue_musd"] = d["revenue_musd"].shift(-1)
    d["cov_total"] = d["paid_backlog_musd"] / d["next_revenue_musd"]
    d["cov_uf"] = d["unearned_fees_musd"] / d["next_revenue_musd"]
    d["cov_fp"] = d["funds_held_for_clients_musd"] / d["next_revenue_musd"]
    d["paid_backlog_yoy_pct"] = 100.0 * (d["paid_backlog_musd"] /
                                         d["paid_backlog_musd"].shift(4) - 1.0)
    return d


def with_lags(kmax: int = 4) -> pd.DataFrame:
    return build_panel(kmax=kmax)


def usable(frame: pd.DataFrame, kmax: int = 4) -> pd.DataFrame:
    cols = ["revenue_musd"] + [f"gbv_l{k}" for k in range(0, kmax + 1)]
    return frame.dropna(subset=cols).reset_index(drop=True)


def ex_covid_mask(frame: pd.DataFrame, thresh: float = 25.0) -> pd.Series:
    """Drop quarters whose nights y/y is outside +/-25% (or is missing)."""
    y = frame["nights_yoy_pct"]
    return y.notna() & (y.abs() <= thresh)
