"""Shared path setup for the calibration-rail package. Import this first."""
from __future__ import annotations

import sys
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
FM_SRC = PKG_DIR.parent                       # analysis/src/forecast_methods
REPO_ROOT = FM_SRC.parents[2]                  # .../Citadel-ABNB

sys.path.insert(0, str(FM_SRC))

DATA_OUT = REPO_ROOT / "data" / "processed" / "forecast_methods" / "calibration_rail"
DOCS_OUT = REPO_ROOT / "docs" / "revenue-forecast-strategy" / "05_backtests"
DATA_OUT.mkdir(parents=True, exist_ok=True)

import harness  # noqa: E402  (import after sys.path insert)

__all__ = ["PKG_DIR", "FM_SRC", "REPO_ROOT", "DATA_OUT", "DOCS_OUT", "harness"]
