"""Materialise the `file=` code blocks of the implementation plan into the repo. Idempotent."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
PLAN = ROOT / "docs/superpowers/plans/2026-09-18-reviews-index-v2.md"
blocks = re.findall(r"