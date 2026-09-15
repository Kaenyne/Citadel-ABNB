"""Executor that would place the mirrored trades -- DRY RUN by default.

Safety posture (same as the other repos in this project):
  * Nothing here submits an order unless you pass live=True AND set the
    env var COPIER_ALLOW_ORDERS=yes. Both are required, on purpose.
  * Even then it only ever talks to the Alpaca PAPER endpoint via the
    same GatedOrderRouter every other repo uses, so every order still
    passes the RiskGate (position caps, notional caps, rate limit,
    daily-loss kill switch) before it can reach the broker.
  * The default path builds the full order list, runs each order through
    the risk gate's check, and PRINTS what it would do. It never sends.

Reference prices: latest Alpaca daily close when creds are available,
otherwise the 13F-implied price (disclosed value / disclosed shares),
which is real filing data and needs no market connection.
"""
import json
import os
from dataclasses import dataclass

from config import DATA_DIR, load_alpaca_creds
from parse_13f import Holding
import cusip_map
from sizing import compute_targets, build_orders, MirrorOrder
from risk_gates import RiskGate, RiskLimits


@dataclass
class ExecutionPlan:
    as_of_report_date: str
    as_of_filing_date: str
    mirror_capital: float
    orders: list[MirrorOrder]
    gate_results: dict          # cusip -> "ALLOWED" | reason string
    skipped: list[MirrorOrder]


def _latest_snapshot():
    idx = json.loads((DATA_DIR / "snapshots_index.json").read_text())
    latest = max(idx, key=lambda r: r["report_date"])
    snap = json.loads((DATA_DIR / f"holdings_{latest['report_date']}.json").read_text())
    snap["holdings"] = [Holding(**h) for h in snap["holdings"]]
    return snap


def _reference_prices(holdings, tickers):
    """CUSIP -> reference price. Alpaca latest close if possible; else the
    13F-implied price (value/shares)."""
    implied = {h.cusip: (h.value_usd / h.shares if h.shares else None) for h in holdings}
    key, secret = load_alpaca_creds()
    if not key:
        return implied
    try:
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockLatestBarRequest
        from alpaca.data.enums import DataFeed
        client = StockHistoricalDataClient(key, secret)
        syms = sorted({t for t in tickers.values() if t})
        bars = client.get_stock_latest_bar(
            StockLatestBarRequest(symbol_or_symbols=syms, feed=DataFeed.IEX))
        out = {}
        for h in holdings:
            t = tickers.get(h.cusip)
            if t and t in bars and bars[t] is not None:
                out[h.cusip] = float(bars[t].close)
            else:
                out[h.cusip] = implied.get(h.cusip)
        return out
    except Exception as e:
        print(f"  (latest-price fetch failed: {e}; using 13F-implied prices)")
        return implied


def build_plan(mirror_capital: float = 100_000.0, max_weight: float = 0.25,
               current_notional: dict | None = None,
               risk_gate: RiskGate | None = None) -> ExecutionPlan:
    snap = _latest_snapshot()
    holdings = snap["holdings"]
    tickers = cusip_map.resolve([h.cusip for h in holdings])
    prices = _reference_prices(holdings, tickers)

    targets = compute_targets(holdings, mirror_capital, max_weight=max_weight)
    orders = build_orders(targets, current_notional or {}, prices, tickers)

    gate = risk_gate or RiskGate(RiskLimits(
        max_position_per_symbol=mirror_capital * max_weight * 1.5,
        max_total_notional=mirror_capital * 1.2,
        max_daily_loss=mirror_capital * 0.05,
    ))
    gate_results = {}
    tradeable, skipped = [], []
    import time as _t
    now = _t.time()
    for o in orders:
        if o.skip_reason or o.qty is None or o.ticker is None:
            skipped.append(o)
            continue
        try:
            gate.check_order(o.ticker, o.side, o.qty, o.ref_price, now)
            gate_results[o.cusip] = "ALLOWED"
            tradeable.append(o)
        except Exception as e:
            gate_results[o.cusip] = f"BLOCKED: {e}"
            skipped.append(o)

    return ExecutionPlan(
        as_of_report_date=snap["report_date"],
        as_of_filing_date=snap["filing_date"],
        mirror_capital=mirror_capital,
        orders=tradeable,
        gate_results=gate_results,
        skipped=skipped,
    )


def execute(plan: ExecutionPlan, live: bool = False):
    """Submit the plan's orders. Refuses unless BOTH live=True and
    COPIER_ALLOW_ORDERS=yes. Paper endpoint only."""
    if not live:
        raise RuntimeError("execute() called without live=True -- refusing (dry-run only)")
    if os.environ.get("COPIER_ALLOW_ORDERS") != "yes":
        raise RuntimeError("COPIER_ALLOW_ORDERS != 'yes' -- refusing to submit any order")

    from alpaca_adapter import GatedOrderRouter
    key, secret = load_alpaca_creds()
    gate = RiskGate(RiskLimits(
        max_position_per_symbol=plan.mirror_capital * 0.30,
        max_total_notional=plan.mirror_capital * 1.2,
        max_daily_loss=plan.mirror_capital * 0.05,
    ))
    router = GatedOrderRouter(gate, key, secret, paper=True)  # paper, always
    sent = []
    for o in plan.orders:
        # Limit at the reference price; router runs the gate again.
        res = router.submit_limit_order(o.ticker, o.side, round(o.qty, 4), o.ref_price)
        sent.append((o.ticker, o.side, o.qty, res.id if hasattr(res, "id") else None))
    return sent
