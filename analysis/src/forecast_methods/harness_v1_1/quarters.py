"""Quarter-label canonicalisation.

Three spellings live in this repo:
  '3Q26'   -- overnight KPI panel, guidance ledger
  '2026Q3' -- earnings reactions, guidance-vs-actual
  '2026-09-30' -- occasionally a period-end date
Canonical form inside the harness is 'YYYYQn' because it sorts lexicographically.
"""
from __future__ import annotations

import datetime as _dt
import re

_SHORT = re.compile(r"^([1-4])Q(\d{2})$")
_LONG = re.compile(r"^(\d{4})Q([1-4])$")


def canon(q) -> str:
    """Return 'YYYYQn' for any of the repo's quarter spellings."""
    if q is None:
        raise ValueError("quarter is None")
    s = str(q).strip().upper().replace(" ", "")
    m = _LONG.match(s)
    if m:
        return f"{m.group(1)}Q{m.group(2)}"
    m = _SHORT.match(s)
    if m:
        yy = int(m.group(2))
        year = 2000 + yy if yy < 80 else 1900 + yy
        return f"{year}Q{m.group(1)}"
    if s.startswith("FY"):
        return s  # FY2026 etc: passed through, never a quarterly target
    raise ValueError(f"unparseable quarter label: {q!r}")


def short(q) -> str:
    """Return '3Q26' form (the overnight-panel spelling)."""
    c = canon(q)
    return f"{c[5]}Q{c[2:4]}"


def to_index(q) -> int:
    c = canon(q)
    return int(c[:4]) * 4 + int(c[5]) - 1


def from_index(i: int) -> str:
    return f"{i // 4}Q{i % 4 + 1}"


def shift(q, k: int) -> str:
    return from_index(to_index(q) + k)


def quarter_end(q) -> _dt.date:
    c = canon(q)
    y, n = int(c[:4]), int(c[5])
    return {1: _dt.date(y, 3, 31), 2: _dt.date(y, 6, 30),
            3: _dt.date(y, 9, 30), 4: _dt.date(y, 12, 31)}[n]


def quarter_of_date(d: _dt.date) -> str:
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"
