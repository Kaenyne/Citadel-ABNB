"""Event timing and trading-session return calculations."""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pandas as pd


NEW_YORK = ZoneInfo("America/New_York")
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)


def reaction_session(published_at: datetime, exchange_calendar: list[date]) -> date:
    if published_at.tzinfo is None or published_at.utcoffset() is None:
        raise ValueError("published_at must be timezone-aware")
    sessions = sorted(set(exchange_calendar))
    local = published_at.astimezone(NEW_YORK)
    local_date = local.date()
    if local_date in sessions and local.timetz().replace(tzinfo=None) <= MARKET_CLOSE:
        return local_date
    future = [session for session in sessions if session > local_date]
    if not future:
        raise ValueError("exchange calendar has no reaction session after publication")
    return future[0]


def compute_total_return(prices: pd.Series, start: date, sessions: int) -> float:
    if sessions <= 0:
        raise ValueError("sessions must be positive")
    clean = prices.dropna().sort_index().copy()
    clean.index = pd.to_datetime(clean.index).date
    index = list(clean.index)
    if start not in index:
        raise ValueError("reaction session missing from price series")
    start_position = index.index(start)
    if start_position == 0:
        raise ValueError("prior close is required")
    end_position = start_position + sessions - 1
    if end_position >= len(clean):
        raise ValueError("insufficient prices for requested return window")
    prior_close = float(clean.iloc[start_position - 1])
    end_close = float(clean.iloc[end_position])
    if prior_close == 0:
        raise ValueError("prior close cannot be zero")
    return end_close / prior_close - 1.0
