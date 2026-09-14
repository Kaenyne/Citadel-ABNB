"""Loaders for the built spine; rebuild on demand if missing."""
from __future__ import annotations

import datetime as _dt
import functools

import pandas as pd

from . import paths as P
from . import quarters as Q


def _dates(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce").dt.date
    return df


@functools.lru_cache(maxsize=1)
def load_calendar() -> pd.DataFrame:
    if not P.OUT_CALENDAR.exists():
        from .spine import build_calendar
        P.ensure_dirs()
        build_calendar().to_csv(P.OUT_CALENDAR, index=False)
    c = pd.read_csv(P.OUT_CALENDAR)
    return _dates(c, ["quarter_end", "print_date", "guide_date", "letter_date",
                      "reaction_date", "filing_date"])


@functools.lru_cache(maxsize=1)
def load_targets() -> pd.DataFrame:
    if not P.OUT_TARGETS.exists():
        from .spine import build_calendar, build_targets
        P.ensure_dirs()
        cal = build_calendar()
        cal.to_csv(P.OUT_CALENDAR, index=False)
        build_targets(cal).to_csv(P.OUT_TARGETS, index=False)
    t = pd.read_csv(P.OUT_TARGETS)
    t["quarter"] = t["quarter"].map(Q.canon)
    return _dates(t, ["print_date", "guide_date", "street_pre_guide_as_of"])


def clear_cache():
    load_calendar.cache_clear()
    load_targets.cache_clear()


def history_as_of(vintage_date, metric: str = None, targets: pd.DataFrame = None,
                  include_same_day: bool = True):
    """The point-in-time information set at a guide date.

    Rows whose PRINT DATE is <= `vintage_date` (default) or strictly < it.

    WHY THE DEFAULT IS `<=` -- READ THIS. The binding point-in-time rule is written as
    "letters and 10-Qs filed strictly before d". Taken literally that excludes the very
    letter that CARRIES the guide: ABNB's 2026Q2 results and the 3Q26 revenue range are
    in one 8-K Ex.99.1 dated 2026-08-06, so a forecaster standing at that guide date
    plainly knows 2Q26 revenue. The harness therefore includes the same-day letter and
    excludes everything after it. This is also what reproduces the chief of staff's
    trailing-8 cushion (mean +1.856%, median +1.790%, sd 1.006pp at 2026-08-06); under
    a strict `<` rule the window slides back one quarter and those numbers do not
    reproduce. Pass `include_same_day=False` for the literal reading; it is a one-word
    change and both replays are cheap.

    FRED FX is a separate matter: the rule "FX through d-1" is about a daily series and
    is unaffected by this convention. Packages consuming FX must still cut at d-1.
    """
    t = load_targets() if targets is None else targets.copy()
    vd = vintage_date.date() if isinstance(vintage_date, _dt.datetime) else vintage_date
    if isinstance(vd, str):
        vd = pd.to_datetime(vd).date()

    def _before(d):
        if d is None or pd.isna(d):
            return False
        return (d <= vd) if include_same_day else (d < vd)

    h = t[t["print_date"].map(_before)].copy()
    h = h.sort_values("quarter").reset_index(drop=True)
    if metric is None:
        return h
    return h[["quarter", "print_date", metric]].dropna(subset=[metric]).reset_index(drop=True)
