"""Paths for returns_v1, resolved from this file so the package runs from anywhere."""
from __future__ import annotations

from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
REPO_ROOT = PKG_DIR.parents[3]
OUT_DIR = REPO_ROOT / "data" / "processed" / "forecast_methods" / "returns_v1"
CALENDAR = REPO_ROOT / "data" / "processed" / "forecast_methods" / "harness" / "calendar.csv"
LEGACY_REACTIONS = REPO_ROOT / "data" / "processed" / "abnb_earnings_reactions.csv"

OHLC = OUT_DIR / "ohlc_daily.csv"
MANIFEST = OUT_DIR / "manifest.json"
OPEN_RETURNS = OUT_DIR / "earnings_reactions_open_v1.csv"

TICKERS = ("ABNB", "QQQ")
START = "2020-12-01"          # ABNB listed 2020-12-10
HORIZONS = (1, 5, 20, 60)     # trading days, inclusive of the entry day
