"""guidance-policy-v2 (task B2): shared paths and loaders.

COPY of analysis/src/forecast_methods/tracker_backlog/common.py with the output
directory, the note path and the package-specific constants retargeted.  The
original file is untouched.


Every path resolves relative to THIS file (pathlib), so scripts run from anywhere.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PKG_DIR = Path(__file__).resolve().parent
REPO_ROOT = PKG_DIR.parents[3]   # .../Citadel-ABNB

DATA = REPO_ROOT / "data"
PROCESSED = DATA / "processed"
OVERNIGHT = PROCESSED / "overnight"
OUT_DIR = PROCESSED / "forecast_methods" / "guidance_policy_v2"
NOTE_PATH = (REPO_ROOT / "docs" / "revenue-forecast-strategy" / "05_backtests"
             / "B2_Q4_GUIDE_EXHIBIT.md")

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


# ---- v2: the combined 3Q26 GBV object published by optimal-mix -----------------
SRC_COMBINED_LIVE = PROCESSED / "forecast_methods" / "optimal_mix" / "combined_live_objects.json"
SRC_FEE_STEP_PATH = PROCESSED / "forecast_methods" / "fee_takerate" / "03_migrated_share_path.csv"
SRC_GP_SCORES = PROCESSED / "forecast_methods" / "guidance_policy" / "07_backtest_scores.csv"
SRC_L0_VINTAGE = PROCESSED / "forecast_methods" / "L0" / "L0_vintage_register.csv"


def load_combined_live() -> dict:
    import json
    with open(SRC_COMBINED_LIVE) as fh:
        return json.load(fh)
