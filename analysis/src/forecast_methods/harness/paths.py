"""Path resolution for the forecast-methods harness.

Every path is resolved relative to THIS file, so any script can be run from anywhere.
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
FORECAST_METHODS_SRC = HARNESS_DIR.parent
REPO_ROOT = HARNESS_DIR.parents[3]

DATA = REPO_ROOT / "data"
PROCESSED = DATA / "processed"
OVERNIGHT = PROCESSED / "overnight"

FM_DATA = PROCESSED / "forecast_methods"
HARNESS_OUT = FM_DATA / "harness"
REGISTRY_DIR = FM_DATA / "registry"
L0_DIR = FM_DATA / "L0"

DOCS_BACKTESTS = REPO_ROOT / "docs" / "revenue-forecast-strategy" / "05_backtests"

# ---- source files -----------------------------------------------------------
SRC_KPI_QUARTERLY = OVERNIGHT / "02_kpi_panel_quarterly.csv"
SRC_GUIDANCE_LEDGER = OVERNIGHT / "02_guidance_ledger.csv"
SRC_CUSHION_SERIES = OVERNIGHT / "02_guidance_cushion_series.csv"
SRC_CONSENSUS_MERGED = OVERNIGHT / "16_consensus_at_print_merged.csv"
SRC_CURRENT_CONSENSUS = OVERNIGHT / "04_current_consensus.csv"
SRC_GUIDE_VS_ACTUAL = PROCESSED / "abnb_revenue_guidance_vs_actual.csv"
SRC_EARNINGS_REACTIONS = PROCESSED / "abnb_earnings_reactions.csv"
SRC_EDGAR_LOG = DATA / "manifests" / "edgar_filings_log.csv"
SRC_L0_VINTAGE_REGISTER = L0_DIR / "L0_vintage_register.csv"

# ---- harness outputs --------------------------------------------------------
OUT_CALENDAR = HARNESS_OUT / "calendar.csv"
OUT_TARGETS = HARNESS_OUT / "targets.csv"
OUT_WINDOWS = HARNESS_OUT / "windows.csv"
OUT_CONFORMAL_GRID = HARNESS_OUT / "conformal_attainable_grid.csv"
OUT_SCOREBOARD = HARNESS_OUT / "scoreboard.csv"
OUT_SCOREBOARD_MD = HARNESS_OUT / "scoreboard.md"

TODAY = _dt.date(2026, 9, 11)

FORMAT_VERSION = "1.0"


def ensure_dirs() -> None:
    for d in (FM_DATA, HARNESS_OUT, REGISTRY_DIR):
        d.mkdir(parents=True, exist_ok=True)
