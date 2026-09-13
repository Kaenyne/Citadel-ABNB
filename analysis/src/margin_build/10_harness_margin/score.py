#!/usr/bin/env python
"""Score the margin registry (run after registering a method).

  python analysis/src/margin_build/10_harness_margin/score.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_margin.score import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
