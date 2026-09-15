"""Hard risk gates for Phase 4 (live paper trading via IBKR).

These are deliberately NOT strategy parameters you'd tune for
performance -- they're safety limits checked before every single order,
independent of what the strategy thinks is a good trade. The design
intent (see project history): a bug that fires orders in a loop is the
most common way an algo trading project loses real money fast, and
that's a bug class to guard against structurally, not a market risk to
manage with discipline in the moment.

No network/broker dependency in this module -- it's pure logic, fully
unit-testable without a live or paper IBKR connection.
"""
from dataclasses import dataclass, field


@dataclass
class RiskLimits:
    max_position_per_symbol: float
    max_total_notional: float
    max_daily_loss: float          # positive number; breach is realized_pnl <= -max_daily_loss
    max_orders_per_minute: int = 30


class KillSwitchTripped(Exception):
    """Raised once the daily loss limit is breached. Once tripped, the
    gate refuses ALL new orders for the rest of the session -- it does
    not reset automatically, on purpose. A human has to decide to
    restart, not the same code that just blew through the limit.
    """


@dataclass
class RiskGate:
    limits: RiskLimits
    positions: dict = field(default_factory=dict)     # symbol -> signed qty
    realized_pnl: float = 0.0
    _order_timestamps: list = field(default_factory=list)
    _tripped: bool = False

    def check_order(self, symbol: str, side: str, qty: float, price: float, now: float) -> None:
        """Raises if the order should be blocked. Returns normally (no
        return value) if it's allowed -- callers must call this before
        every single order submission, no exceptions.
        """
        if self._tripped:
            raise KillSwitchTripped("kill switch is tripped; no new orders until manually reset")

        if self.realized_pnl <= -self.limits.max_daily_loss:
            self._tripped = True
            raise KillSwitchTripped(
                f"daily loss limit breached: realized_pnl={self.realized_pnl:.2f} "
                f"<= -{self.limits.max_daily_loss:.2f}"
            )

        signed_qty = qty if side == "BUY" else -qty
        prospective_position = self.positions.get(symbol, 0.0) + signed_qty
        if abs(prospective_position) > self.limits.max_position_per_symbol:
            raise ValueError(
                f"order rejected: {symbol} position would be {prospective_position}, "
                f"exceeds max_position_per_symbol={self.limits.max_position_per_symbol}"
            )

        notional = abs(qty * price)
        total_notional = sum(abs(p) for p in self.positions.values()) * price + notional
        if total_notional > self.limits.max_total_notional:
            raise ValueError(
                f"order rejected: total notional {total_notional:.2f} would exceed "
                f"max_total_notional={self.limits.max_total_notional}"
            )

        recent = [t for t in self._order_timestamps if now - t < 60]
        if len(recent) >= self.limits.max_orders_per_minute:
            raise ValueError(
                f"order rejected: {len(recent)} orders in the last 60s, "
                f"exceeds max_orders_per_minute={self.limits.max_orders_per_minute} "
                f"-- likely a runaway loop, not legitimate strategy activity"
            )

    def record_order_sent(self, now: float) -> None:
        self._order_timestamps.append(now)

    def record_fill(self, symbol: str, side: str, qty: float, price: float, entry_price: float | None = None) -> None:
        signed_qty = qty if side == "BUY" else -qty
        self.positions[symbol] = self.positions.get(symbol, 0.0) + signed_qty
        if entry_price is not None:
            self.realized_pnl += (price - entry_price) * (qty if side == "SELL" else -qty)

    def is_tripped(self) -> bool:
        return self._tripped

    def manual_reset(self) -> None:
        """Explicit, separate call -- never invoked automatically."""
        self._tripped = False
