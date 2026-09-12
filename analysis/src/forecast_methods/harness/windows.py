"""W1 / W2 / LIVE guide-date lists, HARD-CODED from the guidance-ledger revenue rows.

Hard-coded on purpose: these 15 dates are the spine of every backtest in the programme
and must not silently move if a source file is regenerated. `assert_matches_ledger()`
re-derives them from 02_guidance_ledger.csv and raises if the file disagrees, so the
hard-coding is checked rather than merely asserted.

W1: targets 2023Q1..2026Q2, 14 guide dates.
W2: targets 2024Q1..2026Q2, 10 guide dates (a strict subset of W1).
LIVE: the 2026-08-06 guide, target 2026Q3. It has no realised actual. It enters NO
metric and NO gate.
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd

from . import paths as P
from . import quarters as Q

_D = _dt.date

# (guide_date, target_quarter) -- the call that issued the revenue range for that target
GUIDE_EVENTS_ALL = [
    (_D(2021, 11, 4), "2021Q4"),
    (_D(2022, 2, 15), "2022Q1"),
    (_D(2022, 5, 3), "2022Q2"),
    (_D(2022, 8, 2), "2022Q3"),
    (_D(2022, 11, 1), "2022Q4"),
    (_D(2023, 2, 14), "2023Q1"),
    (_D(2023, 5, 9), "2023Q2"),
    (_D(2023, 8, 3), "2023Q3"),
    (_D(2023, 11, 1), "2023Q4"),
    (_D(2024, 2, 13), "2024Q1"),
    (_D(2024, 5, 8), "2024Q2"),
    (_D(2024, 8, 6), "2024Q3"),
    (_D(2024, 11, 7), "2024Q4"),
    (_D(2025, 2, 13), "2025Q1"),
    (_D(2025, 5, 1), "2025Q2"),
    (_D(2025, 8, 6), "2025Q3"),
    (_D(2025, 11, 6), "2025Q4"),
    (_D(2026, 2, 12), "2026Q1"),
    (_D(2026, 5, 7), "2026Q2"),
    (_D(2026, 8, 6), "2026Q3"),   # LIVE
]

W1_TARGETS = [q for _, q in GUIDE_EVENTS_ALL if "2023Q1" <= q <= "2026Q2"]
W2_TARGETS = [q for _, q in GUIDE_EVENTS_ALL if "2024Q1" <= q <= "2026Q2"]
LIVE_TARGETS = [q for _, q in GUIDE_EVENTS_ALL if q >= "2026Q3"]

GUIDE_DATES_W1 = [d for d, q in GUIDE_EVENTS_ALL if q in W1_TARGETS]
GUIDE_DATES_W2 = [d for d, q in GUIDE_EVENTS_ALL if q in W2_TARGETS]
GUIDE_DATE_LIVE = _D(2026, 8, 6)
GUIDE_DATES_ALL = [d for d, _ in GUIDE_EVENTS_ALL]

TARGET_TO_GUIDE_DATE = {q: d for d, q in GUIDE_EVENTS_ALL}
GUIDE_DATE_TO_TARGET = {d: q for d, q in GUIDE_EVENTS_ALL}

assert len(GUIDE_DATES_W1) == 14, f"W1 must have 14 guide dates, got {len(GUIDE_DATES_W1)}"
assert len(GUIDE_DATES_W2) == 10, f"W2 must have 10 guide dates, got {len(GUIDE_DATES_W2)}"
assert set(GUIDE_DATES_W2) <= set(GUIDE_DATES_W1)
assert GUIDE_DATE_LIVE not in GUIDE_DATES_W1

WINDOWS = ("W1", "W2", "LIVE")
WINDOW_MEMBERSHIP = {"W1": W1_TARGETS, "W2": W2_TARGETS, "LIVE": LIVE_TARGETS}


def window_of_target(q: str):
    """Windows a target quarter belongs to (a 2024Q1+ target is in BOTH W1 and W2)."""
    q = Q.canon(q)
    return [w for w, qs in WINDOW_MEMBERSHIP.items() if q in qs]


def assert_matches_ledger() -> None:
    g = pd.read_csv(P.SRC_GUIDANCE_LEDGER)
    g = g[(g["metric"] == "revenue_usd_m") & (g["guide_type"] == "range")]
    got = sorted({(pd.to_datetime(r.print_date).date(), Q.canon(r.target_period))
                  for r in g.itertuples()})
    want = sorted(GUIDE_EVENTS_ALL)
    if got != want:
        missing = [x for x in want if x not in got]
        extra = [x for x in got if x not in want]
        raise AssertionError(
            f"guidance ledger disagrees with hard-coded windows. missing={missing} extra={extra}")


def windows_frame() -> pd.DataFrame:
    rows = []
    for d, q in GUIDE_EVENTS_ALL:
        wins = window_of_target(q)
        rows.append({"guide_date": d, "target_quarter": q,
                     "in_W1": "W1" in wins, "in_W2": "W2" in wins,
                     "is_live": "LIVE" in wins,
                     "scored": "LIVE" not in wins})
    return pd.DataFrame(rows)
