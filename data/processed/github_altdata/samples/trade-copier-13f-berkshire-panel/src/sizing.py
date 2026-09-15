"""Position sizing: translate the filer's portfolio weights into
proportional Alpaca paper-account order sizes.

The scheme is deliberately simple and transparent:

  target_notional(symbol) = filer_weight(symbol) * MIRROR_CAPITAL

where filer_weight is the position's share of the filer's disclosed 13F
value, and MIRROR_CAPITAL is the dollar amount of OUR paper account we
choose to allocate to mirroring. We never mirror the filer's absolute
dollar amounts (they run tens to hundreds of billions) -- only their
relative allocation.

For each quarter we compute the *target* notional per symbol from the
new filing, compare to what we'd currently hold, and emit the trade
needed to close the gap. That means a fresh mirror on quarter 1 buys the
whole target book; later quarters only trade the deltas -- which is
exactly the "trade copier" behavior.

Only long common-stock positions are mirrored. Options, principal
(bond) holdings, and anything without a resolvable ticker are skipped
and reported, never silently sized.
"""
from dataclasses import dataclass

from parse_13f import Holding, portfolio_weights


@dataclass
class TargetPosition:
    cusip: str
    issuer: str
    weight: float             # filer's fraction of portfolio (0..1)
    target_notional: float    # dollars of OUR capital to allocate


@dataclass
class MirrorOrder:
    cusip: str
    issuer: str
    ticker: str | None
    side: str                 # "BUY" or "SELL"
    target_notional: float
    current_notional: float
    delta_notional: float     # signed; + = buy more, - = sell
    ref_price: float | None
    qty: float | None         # whole shares to trade (delta / ref_price)
    skip_reason: str | None = None


def compute_targets(holdings: list[Holding], mirror_capital: float,
                    max_weight: float = 1.0) -> list[TargetPosition]:
    """Target notional per CUSIP from filer weights.

    `max_weight` caps any single position's weight before scaling, so a
    filer with a huge single holding (Berkshire's Apple has been ~40-50%)
    doesn't dump nearly half our capital into one name. Capping then
    NOT re-normalizing is intentional: the capped weight stays capped and
    the freed capital simply isn't deployed, rather than being forced
    into the other names.
    """
    weights = portfolio_weights(holdings)
    issuer_by = {h.cusip: h.issuer for h in holdings}
    out = []
    for cusip, w in weights.items():
        capped = min(w, max_weight)
        out.append(TargetPosition(
            cusip=cusip,
            issuer=issuer_by.get(cusip, ""),
            weight=w,
            target_notional=capped * mirror_capital,
        ))
    out.sort(key=lambda t: t.target_notional, reverse=True)
    return out


def build_orders(targets: list[TargetPosition],
                 current_notional: dict[str, float],
                 ref_prices: dict[str, float],
                 tickers: dict[str, str | None],
                 min_order_notional: float = 1.0) -> list[MirrorOrder]:
    """Diff target vs current book -> concrete mirror orders.

    `current_notional`, `ref_prices`, `tickers` are keyed by CUSIP.
    A ticker of None (unresolvable CUSIP -- e.g. an option or an untraded
    name) produces a skipped order, surfaced with a reason.
    """
    orders = []
    seen = set()
    for t in targets:
        seen.add(t.cusip)
        cur = current_notional.get(t.cusip, 0.0)
        delta = t.target_notional - cur
        ticker = tickers.get(t.cusip)
        price = ref_prices.get(t.cusip)
        side = "BUY" if delta >= 0 else "SELL"

        skip = None
        qty = None
        if ticker is None:
            skip = "no ticker for CUSIP (option/untraded/unmapped)"
        elif price is None or price <= 0:
            skip = "no reference price"
        elif abs(delta) < min_order_notional:
            skip = "delta below min order notional"
        else:
            qty = abs(delta) / price

        orders.append(MirrorOrder(
            cusip=t.cusip, issuer=t.issuer, ticker=ticker, side=side,
            target_notional=t.target_notional, current_notional=cur,
            delta_notional=delta, ref_price=price, qty=qty, skip_reason=skip,
        ))

    # Names we currently hold but the filer no longer targets -> sell to 0.
    for cusip, cur in current_notional.items():
        if cusip in seen or cur <= 0:
            continue
        ticker = tickers.get(cusip)
        price = ref_prices.get(cusip)
        qty = (cur / price) if (ticker and price and price > 0) else None
        orders.append(MirrorOrder(
            cusip=cusip, issuer="", ticker=ticker, side="SELL",
            target_notional=0.0, current_notional=cur, delta_notional=-cur,
            ref_price=price, qty=qty,
            skip_reason=None if qty else "cannot price exit",
        ))
    return orders
