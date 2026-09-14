"""Path resolution for harness FORMAT 1.1 (a copy of the frozen 1.0 harness).

Every path is resolved relative to THIS file, so any script can be run from anywhere.

What differs from the frozen `harness/` (nothing else does):
  * RUN_DATE replaces the hard-coded TODAY = 2026-09-11. It is read from the environment
    variable CITADEL_ABNB_RUN_DATE (ISO date) and defaults to the real calendar date, so a
    LIVE forecast made today carries today's date instead of a stale constant.
  * The spine (calendar / targets / windows) is READ from the frozen harness directory and
    never rewritten here. Only this version's own scoreboard and grid land in
    data/processed/forecast_methods/harness_v1_1/.
  * The registry directory is shared with 1.0 on purpose: one registry, both scorers.
"""
from __future__ import annotations

import datetime as _dt
import os as _os
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
FORECAST_METHODS_SRC = HARNESS_DIR.parent
REPO_ROOT = HARNESS_DIR.parents[3]

DATA = REPO_ROOT / "data"
PROCESSED = DATA / "processed"
OVERNIGHT = PROCESSED / "overnight"

FM_DATA = PROCESSED / "forecast_methods"
HARNESS_FROZEN_OUT = FM_DATA / "harness"        # 1.0 spine: calendar, targets, windows (read-only here)
HARNESS_OUT = FM_DATA / "harness_v1_1"          # this version's own outputs
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
OUT_CALENDAR = HARNESS_FROZEN_OUT / "calendar.csv"      # frozen spine, never rewritten by 1.1
OUT_TARGETS = HARNESS_FROZEN_OUT / "targets.csv"
OUT_WINDOWS = HARNESS_FROZEN_OUT / "windows.csv"
OUT_CONFORMAL_GRID = HARNESS_OUT / "conformal_attainable_grid.csv"
OUT_SCOREBOARD = HARNESS_OUT / "scoreboard_v1_1.csv"
OUT_SCOREBOARD_MD = HARNESS_OUT / "scoreboard_v1_1.md"

FROZEN_TODAY = _dt.date(2026, 9, 11)          # the 1.0 constant, kept for reference
LIVE_VINTAGE_MIN = _dt.date(2026, 8, 7)       # first day after the 2026-08-06 LIVE guide


def _run_date() -> _dt.date:
    raw = _os.environ.get("CITADEL_ABNB_RUN_DATE", "").strip()
    if raw:
        d = _dt.date.fromisoformat(raw)
    else:
        d = _dt.date.today()
    if d < LIVE_VINTAGE_MIN:
        raise ValueError(f"CITADEL_ABNB_RUN_DATE={d} precedes the LIVE window start {LIVE_VINTAGE_MIN}")
    return d


RUN_DATE = _run_date()
TODAY = RUN_DATE                              # alias kept so copied modules keep working

FORMAT_VERSION = "1.1"


def ensure_dirs() -> None:
    for d in (FM_DATA, HARNESS_OUT, REGISTRY_DIR):
        d.mkdir(parents=True, exist_ok=True)
