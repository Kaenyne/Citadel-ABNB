#!/usr/bin/env python
"""Fetch daily OHLC for ABNB and QQQ from Yahoo Finance (public) and write ohlc_daily.csv + manifest.json.

  python analysis/src/forecast_methods/returns_v1/fetch_ohlc.py

Raw (unadjusted) Open/Close are stored on purpose: an executable entry is the printed open, not an
adjusted one. ABNB has no dividends or splits; QQQ's dividends make its raw 20-day return understate
total return by a few basis points, which is noted in the README and immaterial at this horizon.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from returns_v1 import paths as P  # noqa: E402

WANTED = {"Open": "open", "High": "high", "Low": "low", "Close": "close",
          "Adj Close": "adj_close", "Volume": "volume"}


def fetch(tickers=P.TICKERS, start: str = P.START) -> pd.DataFrame:
    import yfinance as yf
    frames = []
    for t in tickers:
        h = yf.Ticker(t).history(start=start, auto_adjust=False, actions=False)
        if h is None or len(h) == 0:
            raise RuntimeError(f"yfinance returned no rows for {t}")
        h = h.rename(columns=WANTED)
        h = h[[c for c in WANTED.values() if c in h.columns]].copy()
        idx = pd.to_datetime(h.index)
        if getattr(idx, "tz", None) is not None:
            idx = idx.tz_localize(None)
        h.insert(0, "ticker", t)
        h.insert(0, "date", idx.date)
        frames.append(h.reset_index(drop=True))
    out = pd.concat(frames, ignore_index=True).sort_values(["ticker", "date"]).reset_index(drop=True)
    out = out[out["open"].notna() & out["close"].notna()]
    return out


def main() -> int:
    import yfinance as yf
    P.OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = fetch()
    df.to_csv(P.OHLC, index=False)
    sha = hashlib.sha256(P.OHLC.read_bytes()).hexdigest()
    man = {
        "source": "Yahoo Finance daily bars via yfinance (public, no login)",
        "yfinance_version": getattr(yf, "__version__", "unknown"),
        "retrieved_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "tickers": list(P.TICKERS), "start": P.START, "auto_adjust": False,
        "rows": {t: int((df["ticker"] == t).sum()) for t in P.TICKERS},
        "first_date": str(df["date"].min()), "last_date": str(df["date"].max()),
        "file": P.OHLC.name, "sha256": sha,
    }
    P.MANIFEST.write_text(json.dumps(man, indent=2))
    print(f"wrote {P.OHLC.name}: {len(df)} rows, {man['first_date']}..{man['last_date']}; sha256 {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
