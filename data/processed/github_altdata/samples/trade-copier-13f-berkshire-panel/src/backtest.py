"""Lag-aware backtest: would mirroring this filer's DISCLOSED 13F moves
have beaten SPY?

Honesty is the whole point here, so the simulation is built to NOT cheat
on the one thing that makes 13F mirroring hard -- the disclosure lag:

  * A quarter's holdings are treated as KNOWN only on the filing_date
    (the day SEC received the 13F), NOT the report_date (quarter-end).
    Berkshire's Q1 book (Mar 31) isn't public until ~May 15. We rebalance
    into it on the filing date, ~45 days late, exactly as a real mirror
    would have to.
  * Between filings we hold fixed share counts (weights drift with price),
    then re-weight to the new disclosed book at the next filing.

Weights come from the filer's disclosed 13F values, restricted to the
positions we can actually map to a US-listed ticker AND price, then
renormalized to sum to 1 over that subset. Unmapped names (see
cusip_map) are dropped and reported -- never faked.

Prices are Alpaca IEX daily bars, dividend+split adjusted (total return),
so the SPY benchmark is a fair total-return comparison.
"""
import json
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np
import pandas as pd

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import Adjustment, DataFeed

from config import DATA_DIR, RESULTS_DIR, load_alpaca_creds
from parse_13f import Holding, portfolio_weights
import cusip_map

TRADING_DAYS = 252


@dataclass
class Metrics:
    total_return_pct: float
    cagr_pct: float
    ann_vol_pct: float
    sharpe: float
    max_drawdown_pct: float


def _load_snapshots():
    idx = json.loads((DATA_DIR / "snapshots_index.json").read_text())
    snaps = []
    for row in sorted(idx, key=lambda r: r["report_date"]):
        s = json.loads((DATA_DIR / f"holdings_{row['report_date']}.json").read_text())
        s["holdings"] = [Holding(**h) for h in s["holdings"]]
        snaps.append(s)
    return snaps


def _fetch_prices(tickers, start, end):
    key, secret = load_alpaca_creds()
    if not key:
        raise RuntimeError("no Alpaca credentials; cannot run price backtest")
    client = StockHistoricalDataClient(key, secret)
    frames = {}
    tickers = sorted(set(tickers))

    def pull(symbols):
        req = StockBarsRequest(
            symbol_or_symbols=symbols, timeframe=TimeFrame.Day,
            start=start, end=end, adjustment=Adjustment.ALL, feed=DataFeed.IEX)
        df = client.get_stock_bars(req).df
        if df.empty:
            return
        close = df["close"].reset_index().pivot(
            index="timestamp", columns="symbol", values="close")
        for c in close.columns:
            frames[c] = close[c]

    # Chunk to keep requests modest; if a chunk contains a symbol Alpaca
    # rejects (e.g. delisted), fall back to per-symbol so one bad ticker
    # doesn't kill the whole batch.
    for i in range(0, len(tickers), 20):
        chunk = tickers[i:i + 20]
        try:
            pull(chunk)
        except Exception:
            for sym in chunk:
                try:
                    pull([sym])
                except Exception as e:
                    print(f"  price fetch skipped {sym}: {e}")
    panel = pd.DataFrame(frames)
    panel.index = pd.to_datetime(panel.index).tz_localize(None).normalize()
    panel = panel[~panel.index.duplicated(keep="last")].sort_index()
    # Business-day grid, forward-filled (carry last known price over holidays).
    grid = pd.date_range(panel.index.min(), panel.index.max(), freq="B")
    return panel.reindex(grid).ffill()


def _metrics(equity: pd.Series) -> Metrics:
    equity = equity.dropna()
    rets = equity.pct_change().dropna()
    total = equity.iloc[-1] / equity.iloc[0] - 1.0
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1 if years > 0 else 0.0
    vol = rets.std() * np.sqrt(TRADING_DAYS)
    sharpe = (rets.mean() * TRADING_DAYS) / vol if vol > 0 else 0.0
    dd = (equity / equity.cummax() - 1.0).min()
    return Metrics(total * 100, cagr * 100, vol * 100, sharpe, dd * 100)


def run_backtest(mirror_capital: float = 100_000.0, max_weight: float = 1.0):
    snaps = _load_snapshots()

    # CUSIP -> ticker for everything we hold across the window.
    all_cusips = {h.cusip for s in snaps for h in s["holdings"]}
    tmap = cusip_map.resolve(sorted(all_cusips))

    # Rebalance schedule keyed by filing date (the lag-honest signal date).
    rebalances = []  # (filing_date, {ticker: weight})
    dropped_weight_report = []
    for s in snaps:
        weights = portfolio_weights(s["holdings"])
        tw = {}
        dropped = 0.0
        for h in s["holdings"]:
            t = tmap.get(h.cusip)
            w = weights.get(h.cusip, 0.0)
            if t is None:
                dropped += w
                continue
            capped = min(w, max_weight)
            tw[t] = tw.get(t, 0.0) + capped
        total = sum(tw.values())
        tw = {t: w / total for t, w in tw.items()} if total > 0 else {}
        rebalances.append((pd.Timestamp(s["filing_date"]), tw))
        dropped_weight_report.append((s["report_date"], s["filing_date"], dropped))

    start = rebalances[0][0]
    end = pd.Timestamp(datetime.utcnow().date())
    universe = {t for _, tw in rebalances for t in tw} | {"SPY"}
    prices = _fetch_prices(universe, start.to_pydatetime(), end.to_pydatetime())

    # Simulate mirrored portfolio: hold fixed shares between filings.
    grid = prices.index[(prices.index >= start) & (prices.index <= end)]
    equity = pd.Series(index=grid, dtype=float)
    shares = {}
    reb_i = 0
    reb_dates = [d for d, _ in rebalances]

    def price_on(ticker, day):
        if ticker not in prices.columns:
            return np.nan
        s_ = prices[ticker].loc[:day].dropna()
        return s_.iloc[-1] if len(s_) else np.nan

    cash_value = mirror_capital
    for day in grid:
        # Apply any rebalances whose filing date has arrived.
        while reb_i < len(reb_dates) and day >= reb_dates[reb_i]:
            _, tw = rebalances[reb_i]
            cur_val = sum(shares.get(t, 0.0) * (price_on(t, day) or 0)
                          for t in shares) or cash_value
            cur_val = cur_val if np.isfinite(cur_val) and cur_val > 0 else cash_value
            new_shares = {}
            for t, w in tw.items():
                p = price_on(t, day)
                if np.isfinite(p) and p > 0:
                    new_shares[t] = (cur_val * w) / p
            shares = new_shares
            reb_i += 1
        val = sum(sh * price_on(t, day) for t, sh in shares.items())
        equity.loc[day] = val if np.isfinite(val) and val > 0 else np.nan

    equity = equity.ffill().dropna()

    # SPY total-return benchmark over the identical window.
    spy = prices["SPY"].reindex(equity.index).ffill().dropna()
    common = equity.index.intersection(spy.index)
    equity, spy = equity.loc[common], spy.loc[common]
    spy_equity = spy / spy.iloc[0] * mirror_capital

    m_mirror = _metrics(equity)
    m_spy = _metrics(spy_equity)

    result = {
        "filer": "Berkshire Hathaway Inc (CIK 0001067983)",
        "window": {"start": str(equity.index[0].date()),
                   "end": str(equity.index[-1].date())},
        "mirror_capital": mirror_capital,
        "max_weight_cap": max_weight,
        "num_rebalances": len(rebalances),
        "final_value_mirror": float(equity.iloc[-1]),
        "final_value_spy": float(spy_equity.iloc[-1]),
        "mirror": asdict(m_mirror),
        "spy": asdict(m_spy),
        "outperformance_total_pct": m_mirror.total_return_pct - m_spy.total_return_pct,
        "dropped_weight_per_quarter": [
            {"report_date": r, "filing_date": f, "unmapped_weight_pct": round(d * 100, 2)}
            for r, f, d in dropped_weight_report],
    }
    equity_df = pd.DataFrame({"mirror": equity, "spy": spy_equity})
    equity_df.to_csv(RESULTS_DIR / "backtest_equity_curve.csv")
    (RESULTS_DIR / "backtest_result.json").write_text(json.dumps(result, indent=2))
    return result
