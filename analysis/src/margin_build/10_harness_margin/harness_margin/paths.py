"""Path resolution for the margin harness. Everything is relative to THIS file."""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent            # .../10_harness_margin/harness_margin
PKG_DIR = HERE.parent                              # .../10_harness_margin
REPO_ROOT = PKG_DIR.parents[3]                     # margin_build -> src -> analysis -> repo

FROZEN_SRC = REPO_ROOT / "analysis" / "src" / "forecast_methods"   # frozen revenue harness lives here

DATA = REPO_ROOT / "data"
PROCESSED = DATA / "processed"
MB = PROCESSED / "margin_build"

OUT_DIR = MB / "10_harness_margin"
REGISTRY_DIR = MB / "registry"

# ---- stage-1 inputs (preferred) ------------------------------------------------
SRC_WS02_PANEL = MB / "02_financial_panel" / "02_panel_quarterly.csv"
SRC_WS03_CONS = MB / "03_consensus_pit" / "03_consensus_at_dates.csv"
SRC_WS03_SURPRISE = MB / "03_consensus_pit" / "03_surprise_history.csv"
SRC_WS05_LANG = MB / "05_mgmt_statements_v2" / "05_guide_language_pattern.csv"   # optional

# ---- fallback repo panels (used when WS02 is absent or fails validation) --------
SRC_FB_COST_STACK = PROCESSED / "abnb_quarterly_cost_stack_exsbc.csv"      # 1Q21-2Q26 cash lines
SRC_FB_COSTLINES = PROCESSED / "abnb_quarterly_costlines.csv"              # 1Q20-2Q26 GAAP lines
SRC_FB_FCF_BRIDGE = PROCESSED / "abnb_fcf_bridge.csv"                      # 1Q21+ below-EBITDA
SRC_FB_CAPRET = PROCESSED / "abnb_capital_return_quarterly.csv"            # shares, fcf
SRC_KPI_PANEL = PROCESSED / "overnight" / "02_kpi_panel_quarterly.csv"     # nights, gbv, 2020 NI
SRC_GUIDANCE_LEDGER = PROCESSED / "overnight" / "02_guidance_ledger.csv"

# ---- outputs -------------------------------------------------------------------
OUT_TARGETS = OUT_DIR / "targets.csv"
OUT_TARGETS_UNITS = OUT_DIR / "targets_units.csv"
OUT_TARGETS_SOURCE = OUT_DIR / "targets_source.json"
OUT_GUIDES = OUT_DIR / "guides_margin.csv"
OUT_STREET = OUT_DIR / "street_margin_pit.csv"
OUT_SEASONAL_SHARES = OUT_DIR / "seasonal_shares.csv"
OUT_SCOREBOARD = OUT_DIR / "scoreboard_margin.csv"
OUT_SCOREBOARD_MD = OUT_DIR / "scoreboard_margin.md"
OUT_BY_QUARTER = OUT_DIR / "scoreboard_by_quarter.csv"
OUT_BASELINE_TABLE = OUT_DIR / "baseline_scoreboard_summary.md"

BASELINE_METHOD = "baselines-margin"


def ensure_dirs() -> None:
    for d in (OUT_DIR, REGISTRY_DIR):
        d.mkdir(parents=True, exist_ok=True)
