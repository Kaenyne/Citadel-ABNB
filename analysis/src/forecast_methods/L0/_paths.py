"""Path resolution for the L0 constraint spine.

Every path is resolved relative to THIS file, so the package runs from anywhere.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent                      # .../analysis/src/forecast_methods/L0
REPO = HERE.parents[3]                                       # .../Citadel-ABNB
DATA = REPO / "data" / "processed"
OVERNIGHT = DATA / "overnight"
ADR = DATA / "adr"
OUT = DATA / "forecast_methods" / "L0"
DOCS = REPO / "docs" / "revenue-forecast-strategy"

OUT.mkdir(parents=True, exist_ok=True)


def rel(p: Path) -> str:
    """Repo-relative string for the source_path column."""
    try:
        return str(Path(p).resolve().relative_to(REPO))
    except ValueError:
        return str(p)
