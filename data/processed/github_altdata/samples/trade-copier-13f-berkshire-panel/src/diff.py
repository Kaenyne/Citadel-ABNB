"""Quarter-over-quarter diff of a filer's 13F holdings.

Given the holdings of two consecutive filings (previous, current),
classify each position into one of:

  NEW       -- held now, not held before.
  EXIT      -- held before, not held now.
  INCREASE  -- share count went up.
  DECREASE  -- share count went down (but not to zero).
  UNCHANGED -- same share count.

Matching is by CUSIP (stable across quarters; issuer names and even
tickers are not). Share-count deltas -- not value deltas -- drive the
classification, because value can move purely on price with no trade.
We surface value/weight too, for sizing and reporting.
"""
from dataclasses import dataclass
from enum import Enum

from parse_13f import Holding, portfolio_weights


class ChangeType(str, Enum):
    NEW = "NEW"
    EXIT = "EXIT"
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    UNCHANGED = "UNCHANGED"


@dataclass
class PositionChange:
    cusip: str
    issuer: str
    change: ChangeType
    prev_shares: float
    curr_shares: float
    share_delta: float
    prev_weight: float        # fraction of prev portfolio (0..1)
    curr_weight: float        # fraction of curr portfolio (0..1)
    curr_value_usd: float

    @property
    def share_pct_change(self) -> float | None:
        """Signed % change in share count, or None for NEW/EXIT."""
        if self.prev_shares == 0 or self.curr_shares == 0:
            return None
        return (self.curr_shares - self.prev_shares) / self.prev_shares * 100.0


def diff_holdings(prev: list[Holding], curr: list[Holding]) -> list[PositionChange]:
    prev_by = {h.cusip: h for h in prev}
    curr_by = {h.cusip: h for h in curr}
    prev_w = portfolio_weights(prev)
    curr_w = portfolio_weights(curr)

    changes: list[PositionChange] = []
    for cusip in prev_by.keys() | curr_by.keys():
        p = prev_by.get(cusip)
        c = curr_by.get(cusip)
        ps = p.shares if p else 0.0
        cs = c.shares if c else 0.0
        issuer = (c or p).issuer

        if p is None:
            change = ChangeType.NEW
        elif c is None:
            change = ChangeType.EXIT
        elif cs > ps:
            change = ChangeType.INCREASE
        elif cs < ps:
            change = ChangeType.DECREASE
        else:
            change = ChangeType.UNCHANGED

        changes.append(PositionChange(
            cusip=cusip,
            issuer=issuer,
            change=change,
            prev_shares=ps,
            curr_shares=cs,
            share_delta=cs - ps,
            prev_weight=prev_w.get(cusip, 0.0),
            curr_weight=curr_w.get(cusip, 0.0),
            curr_value_usd=(c.value_usd if c else 0.0),
        ))

    # Report order: biggest current position first, exits last.
    changes.sort(key=lambda x: (x.change == ChangeType.EXIT, -x.curr_weight))
    return changes


def summarize(changes: list[PositionChange]) -> dict[str, int]:
    out = {ct.value: 0 for ct in ChangeType}
    for ch in changes:
        out[ch.change.value] += 1
    return out
