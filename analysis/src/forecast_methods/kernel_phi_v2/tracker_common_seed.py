"""Shared paths and loaders for the tracker-backlog package.

Every path resolves relative to THIS file (pathlib), so scripts run from anywhere.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PKG_DIR = Path(__file__).resolve().parent
REPO_ROOT = PKG_DIR.parents[3]

DATA = REPO_ROOT / "data"
PROCESSED = DATA / "processed"
OVERNIGHT = PROCESSED / "overnight"
OUT_DIR = PROCESSED / "forecast_methods" / "tracker_backlog"
NOTE_PATH = REPO_ROOT / "docs" / "revenue-forecast-strategy" / "05_backtests" / "tracker-backlog.md"

SRC_BACKLOG_IND = PROCESSED / "abnb_backlog_indicators.csv"
SRC_KPI_QUARTERLY = OVERNIGHT / "02_kpi_panel_quarterly.csv"
SRC_BOOKING_CURVES_MKT = PROCESSED / "booking_curves_by_market.csv"
SRC_BOOKING_CURVE_DAILY = PROCESSED / "booking_curve_daily.csv"
SRC_INSIDER_MECHANICS = REPO_ROOT / "docs" / "revenue-forecast-strategy" / "01_ground-truth" / "03_insider_mechanics.md"
SRC_C_M6 = REPO_ROOT / "docs" / "revenue-forecast-strategy" / "03_critiques" / "C_M6_fx_takerate_timing_mechanics.md"
SRC_08_BACKLOG_TESTS = OVERNIGHT / "08_backlog_tests.csv"

sys.path.insert(0, str(PKG_DIR.parents[0]))  # .../analysis/src/forecast_methods
from harness import (  # noqa: E402
    GUIDE_EVENTS_ALL, GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE,
    W1_TARGETS, W2_TARGETS, window_of_target, TARGET_TO_GUIDE_DATE,
    load_targets, load_calendar, history_as_of, register, validate_registry_frame,
    baseline_naive, baseline_ar1, quarters as Q,
)


def ensure_out_dir() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_kpi_quarterly() -> pd.DataFrame:
    k = pd.read_csv(SRC_KPI_QUARTERLY)
    return k


def load_backlog_indicators() -> pd.DataFrame:
    b = pd.read_csv(SRC_BACKLOG_IND)
    return b


# Coverage norms (2023-25 seasonal means of unearned_fees / next-quarter revenue),
# as reported in 03_insider_mechanics.md sec 1.4/1.5, reproduced from
# abnb_backlog_indicators.csv. Season is keyed off the quarter-END (the balance-sheet
# date), i.e. the "Q1-end" row is 1Q23/1Q24/1Q25 unearned fees vs 2Q actual revenue.
COVERAGE_NORM_FULL_SAMPLE = {1: 0.880, 2: 0.697, 3: 0.661, 4: 0.676}

# d_q dated distortion series, quarter-end -> pct, from 03_insider_mechanics.md L182-185
DATED_DQ_PCT = {"3Q25": 0.9, "4Q25": 3.8, "1Q26": 16.2, "2Q26": 16.5}

# RNPL GBV share. Only the FLOOR is management-disclosed: "~20%" for 1Q26, ">20%" for
# 2Q26 (03_insider_mechanics.md). The specific point values used below -- 20.0 for
# 1Q26 and 22.0 for 2Q26 -- are the researcher's OWN point picks within that disclosed
# floor, not disclosures themselves; do not describe either as "management-disclosed"
# without this qualification (verification round 1 flagged the 2Q26=22.0 case).
# 3Q25/4Q25 are researcher scenario ramps (launch quarter, partial rollout) with NO
# disclosure of any kind behind them -- labelled as such everywhere they are used.
RNPL_GBV_SHARE_SCENARIO_PCT = {
    "3Q25": 5.0, "4Q25": 12.0, "1Q26": 20.0, "2Q26": 22.0,
}
