#!/usr/bin/env python
"""Rebuild returns_v1 end to end (exit 0). `--refresh` re-fetches OHLC from Yahoo first (needs internet).

  python analysis/src/forecast_methods/returns_v1/run.py [--refresh]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from returns_v1 import paths as P                       # noqa: E402
from returns_v1 import build_open_returns as B          # noqa: E402


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--refresh" in argv:
        from returns_v1 import fetch_ohlc as F
        F.main()
    if not P.OHLC.exists():
        print(f"missing {P.OHLC}; run with --refresh (needs internet)", file=sys.stderr)
        return 2
    return B.main()


if __name__ == "__main__":
    raise SystemExit(main())
