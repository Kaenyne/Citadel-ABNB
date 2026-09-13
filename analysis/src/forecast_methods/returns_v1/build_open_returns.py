#!/usr/bin/env python
"""Build earnings_reactions_open_v1.csv: executable next-open entry returns around every ABNB letter.

Convention (the only one the briefs may use for "executable" returns):
  * event_date  = the letter / print date from the frozen harness calendar (ABNB reports after the close).
  * entry_date  = the first trading day strictly after event_date; entry price = that day's OPEN.
  * open_{h}d   = Close(entry_date + h - 1 trading days) / Open(entry_date) - 1, h in {1, 5, 20, 60}, in percent.
  * excess_open_{h}d = ABNB open_{h}d - QQQ open_{h}d (same dates, same convention).
  * gap_pct     = Open(entry_date) / Close(last trading day <= event_date) - 1: the overnight move a trader
                  cannot capture. Reported for reconciliation only; never an executable return.
  * cc_1d_pct   = Close(entry_date) / Close(last trading day <= event_date) - 1 (the legacy close-to-close
                  definition), so the old abnb_earnings_reactions.csv can be reconciled.
Horizons that run past the last available bar are left empty, never truncated.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from returns_v1 import paths as P  # noqa: E402


def load_ohlc(path: Path = P.OHLC) -> dict:
    o = pd.read_csv(path, parse_dates=["date"])
    out = {}
    for t, g in o.groupby("ticker"):
        g = g.sort_values("date").set_index("date")
        out[t] = g[["open", "close"]].astype(float)
    return out


def events(calendar: Path = P.CALENDAR) -> pd.DataFrame:
    c = pd.read_csv(calendar, parse_dates=["print_date"])
    c = c[(c["print_date_basis"] == "ledger") & (~c["is_forecast_row"].astype(bool))].copy()
    return c[["print_quarter", "print_date", "next_quarter_guided", "guide_mid"]].rename(
        columns={"print_date": "event_date", "next_quarter_guided": "guided_quarter"}).reset_index(drop=True)


def _leg(px: pd.DataFrame, event_date: pd.Timestamp) -> dict:
    dates = px.index
    idx = int(dates.searchsorted(event_date, side="right"))       # first trading day > event
    if idx >= len(dates) or idx == 0:
        return {"entry_date": pd.NaT}
    entry = dates[idx]
    prev_close = float(px["close"].iloc[idx - 1])                  # last close on/before the event
    o = float(px["open"].iloc[idx])
    row = {"entry_date": entry.date(), "entry_open": o,
           "gap_pct": 100.0 * (o / prev_close - 1.0),
           "cc_1d_pct": 100.0 * (float(px["close"].iloc[idx]) / prev_close - 1.0)}
    for h in P.HORIZONS:
        j = idx + h - 1
        row[f"open_{h}d_pct"] = 100.0 * (float(px["close"].iloc[j]) / o - 1.0) if j < len(dates) else np.nan
    row["bars_after_entry"] = int(len(dates) - idx)
    return row


def build(ohlc: dict | None = None, ev: pd.DataFrame | None = None) -> pd.DataFrame:
    ohlc = load_ohlc() if ohlc is None else ohlc
    ev = events() if ev is None else ev
    rows = []
    for r in ev.itertuples(index=False):
        a = _leg(ohlc["ABNB"], r.event_date)
        q = _leg(ohlc["QQQ"], r.event_date)
        if pd.isna(a["entry_date"]):
            continue
        out = {"event_date": r.event_date.date(), "print_quarter": r.print_quarter,
               "guided_quarter": r.guided_quarter, "guide_mid_musd": r.guide_mid,
               "entry_date": a["entry_date"], "abnb_entry_open": a["entry_open"],
               "gap_pct": a["gap_pct"], "qqq_gap_pct": q["gap_pct"],
               "cc_1d_pct": a["cc_1d_pct"], "qqq_cc_1d_pct": q["cc_1d_pct"]}
        for h in P.HORIZONS:
            out[f"open_{h}d_pct"] = a[f"open_{h}d_pct"]
            out[f"qqq_open_{h}d_pct"] = q[f"open_{h}d_pct"]
            out[f"excess_open_{h}d_pct"] = a[f"open_{h}d_pct"] - q[f"open_{h}d_pct"]
        out["excess_cc_1d_pct"] = a["cc_1d_pct"] - q["cc_1d_pct"]
        out["bars_after_entry"] = a["bars_after_entry"]
        rows.append(out)
    return pd.DataFrame(rows)


def main() -> int:
    df = build()
    P.OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(P.OPEN_RETURNS, index=False)
    print(f"wrote {P.OPEN_RETURNS.name}: {len(df)} events, {df['event_date'].min()}..{df['event_date'].max()}")
    show = ["print_quarter", "event_date", "entry_date", "gap_pct", "open_1d_pct", "excess_open_1d_pct",
            "excess_open_5d_pct", "excess_open_20d_pct"]
    print(df[show].round(2).tail(6).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
