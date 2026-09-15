# trade-copier-13f

A **13F position mirror** — a "trade copier" in spirit, not in real time.
It pulls a chosen institutional investor's quarterly **Form 13F** holdings
from the SEC's free, official EDGAR API, diffs consecutive quarters to
infer new positions / exits / size changes, scales the institution's
portfolio weights into proportional order sizes, and (dry-run only)
mirrors them onto an Alpaca **paper** account through the same risk-gated
router used by the other repos in this project.

The filer mirrored here is **Berkshire Hathaway Inc.** (CIK `0001067983`).

---

## ⚠️ THIS IS NOT REAL-TIME. There is a structural ~45-day (up to 45-day) lag.

**Read this before anything else.** 13F is a *quarterly, backward-looking*
disclosure. Under SEC rules an institutional manager has **up to 45 days
after the end of each calendar quarter** to file its 13F. So:

- A manager's **March 31** holdings do not become public until **~May 15**.
- By the time you can see and mirror a trade, it is **at minimum several
  weeks — often ~45 days — stale**, and the manager may have already
  reversed it entirely inside the *current* (undisclosed) quarter.
- 13F reports **long U.S. equity positions only**. It does **not** show
  short positions, most options exposure (only long puts/calls, at
  notional), cash, non-U.S.-listed holdings, or intra-quarter round trips.
- Managers can also request **confidential treatment** to delay disclosing
  a position while they build it, so even the lagged snapshot can be
  incomplete.

**This project makes no attempt to be, and cannot be, a real-time copier.**
Anyone who tells you a 13F strategy is "following the smart money in real
time" is wrong about how the disclosure works. The backtest below is
deliberately built to respect this lag (it only acts on the filing date,
never the quarter-end date) — see [Backtest](#backtest).

---

## Why Berkshire Hathaway?

Every 13F is public per filer; the choice matters for whether mirroring is
even *coherent* given the 45-day lag:

- **Low turnover.** Berkshire is a long-horizon holder — positions are
  held for years, not days. The 45-day lag is **least damaging** for a
  slow, buy-and-hold manager: a stale snapshot of Berkshire is still
  broadly representative of what it holds today. Mirroring a high-turnover
  quant fund with the same lag would be close to noise.
- **Real, plain common stock.** The book is almost entirely long U.S.
  common equity that maps cleanly to Alpaca-tradeable tickers — not
  options, swaps, or exotic structures a 13F can't fully show.
- **Concentrated and well-documented.** A handful of names (Apple, Amex,
  Coca-Cola, Bank of America, Chevron) drive most of the weight, so the
  mirror is interpretable and its moves are easy to sanity-check against
  public reporting.
- **Long, clean filing history** on EDGAR for backtesting.

The honest flip side (see [Results](#results-honest)): because 13F shows
*only* the equity book, mirroring it captures **none** of what actually
drives Berkshire's total return — its wholly-owned operating businesses,
insurance float, and large cash/T-bill position. So "mirror Berkshire's
13F" is **not** "get Berkshire's returns."

---

## Data sources (all free, official, no scraping)

| Source | Used for | Notes |
| --- | --- | --- |
| [SEC EDGAR submissions API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) (`data.sec.gov`) | Filing history + 13F information tables | Official JSON/XML API. Requires a declared `User-Agent` (SEC returns 403 otherwise). |
| [OpenFIGI mapping API](https://www.openfigi.com/api) | CUSIP → ticker (13F gives only CUSIP) | Free, keyless at low volume. Results cached to `data/`. |
| [Alpaca Market Data](https://alpaca.markets/) (IEX feed) | Daily total-return bars for the backtest & live reference prices | Uses the existing paper credentials; IEX daily bars, split+dividend adjusted. |

Everything fetched is **real** SEC/market data and cached under `data/`.
Nothing in this repo is fabricated or hand-typed except the small,
clearly-labelled CUSIP override table in `src/cusip_map.py` (public
CUSIP→ticker facts for a handful of foreign-domiciled names OpenFIGI's
keyless tier can't resolve, e.g. Chubb→`CB`).

---

## Results (honest)

Backtest window **2022-11-14 → 2026-09-02** (16 quarterly, filing-date-lagged
rebalances), $100,000, Apple-style single-name concentration left uncapped
so it is a faithful mirror. Prices are Alpaca IEX daily bars, dividend+split
adjusted (total return), so SPY is a fair total-return benchmark.

| | Total return | CAGR | Ann. vol | Sharpe | Max drawdown | Final value |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Mirror Berkshire 13F** (45-day lagged) | **+77.4%** | +16.3% | 15.3% | 1.03 | −20.1% | $177,422 |
| **SPY** (buy & hold, total return) | **+103.6%** | +20.6% | 14.5% | 1.32 | −18.7% | $203,562 |

![equity curve](results/backtest_equity_curve.png)

**The copier underperformed a plain S&P 500 index fund by ~26 percentage
points over this window**, with slightly higher volatility and a slightly
worse drawdown. Lower return *and* lower risk-adjusted return (Sharpe 1.03
vs 1.32). This is the real result, reported per this project's honesty
norm — mirroring Berkshire's disclosed equity book was **not** an edge over
2022–2026.

Why this is unsurprising, not a bug:
1. **13F ≠ Berkshire.** It excludes the operating companies, insurance
   float, and the very large cash/T-bill position that shaped Berkshire's
   actual results in this period.
2. **The lag.** We buy each quarter's book ~45 days late.
3. **The window.** 2023–2025 was a mega-cap-tech-led melt-up; Berkshire was
   trimming Apple and holding cash/value names, which trailed the index.

A different filer, or a different regime, could invert this. The point of
the repo is the **honest, reproducible machinery**, not a claim of alpha.

Reproduce: `python scripts/run_backtest.py` (writes
`results/backtest_result.json` and the equity CSV/PNG).

---

## How it works

```
EDGAR submissions API ──> edgar_client ──> parse_13f ──> per-quarter holdings (data/)
                                                │
                          diff (Q vs Q-1) ──────┤
                                                │
   OpenFIGI CUSIP→ticker ──> cusip_map ─────────┤
                                                │
                         sizing (weights → $) ──┼──> executor (DRY RUN) ──> [gated] Alpaca paper
                                                │
   Alpaca daily bars ──> backtest (lag-aware) ──┘──> results/
```

- **`src/edgar_client.py`** — pulls the filer's full 13F history and each
  filing's information-table XML from EDGAR; caches to `data/`.
- **`src/parse_13f.py`** — parses the XML, aggregates by CUSIP, and
  normalizes value units (pre-2023 filings report value in *thousands*,
  later ones in *whole dollars*).
- **`src/diff.py`** — quarter-over-quarter classification: NEW / EXIT /
  INCREASE / DECREASE / UNCHANGED, matched by CUSIP, driven by **share**
  deltas (not value, which moves with price alone).
- **`src/sizing.py`** — `target_notional = filer_weight × mirror_capital`,
  with a per-name weight cap; diffs target vs current book into orders.
- **`src/cusip_map.py`** — CUSIP → ticker via OpenFIGI (cached), plus a
  documented manual override table for foreign-CINS names.
- **`src/backtest.py`** — lag-aware backtest vs SPY (details below).
- **`src/executor.py`** — builds the order list and runs each through the
  **risk gate**; **dry-run only** unless explicitly unlocked (see Safety).
- **`src/alpaca_adapter.py`, `src/risk_gates.py`** — copied unchanged from
  the project's `alpaca-paper-trader` so every order passes the same
  position / notional / rate-limit / daily-loss kill-switch gates.

### Backtest

The simulation refuses to cheat on the disclosure lag — the one thing that
makes 13F mirroring hard:

- Each quarter's holdings are treated as known **only on the filing date**
  (the day SEC received the 13F), never the quarter-end. Berkshire's Q1
  book isn't acted on until ~May 15.
- Between filings we hold **fixed share counts** (weights drift with
  price), then re-weight to the newly disclosed book at the next filing.
- Weights are the disclosed 13F values, restricted to names we can map to a
  US ticker and price, then renormalized. Unmapped names (a small % — see
  `dropped_weight_per_quarter` in the result JSON) are **dropped and
  reported, never faked.**

---

## Safety (executor is dry-run only)

Same posture as the other repos in this project:

- The executor **submits nothing** unless you pass `live=True` in code
  **and** set env `COPIER_ALLOW_ORDERS=yes`. Both are required.
- Even then it only ever uses the Alpaca **paper** endpoint, through
  `GatedOrderRouter`, so every order still passes the `RiskGate`
  (per-symbol position cap, total-notional cap, orders-per-minute limit,
  and a daily-loss **kill switch** that latches and needs a manual reset).
- `scripts/dry_run_executor.py` prints exactly what it *would* do and
  submits nothing.

This repo was **run** end-to-end (real EDGAR pulls, real backtest) but is
**not scheduled or deployed** anywhere.

---

## Usage

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Pull real 13F filings from EDGAR (caches to data/)
python scripts/pull_filings.py 16

# 2. See the quarter-over-quarter diff
python scripts/run_diff.py                     # two most recent quarters
python scripts/run_diff.py 2025-03-31 2025-06-30

# 3. Lag-aware backtest vs SPY (needs Alpaca creds for prices)
python scripts/run_backtest.py

# 4. Dry-run the mirror orders for the latest 13F (submits nothing)
python scripts/dry_run_executor.py 100000 0.25   # capital, per-name weight cap

# tests (pure logic, no network)
python -m pytest tests/ -q
```

Credentials: the code reads Alpaca paper keys from
`~/Documents/GitHub/NewsTrader/.env` by default (see `src/config.py`); no
new account setup. The EDGAR pull, diff, and sizing all work with **no**
credentials. See `.env.example` for the optional overrides.

---

## Limitations

- **The 45-day lag is fundamental** and cannot be engineered away — see the
  warning at the top.
- 13F shows long U.S. equities only: no shorts, no cash, limited options,
  no foreign-listed lines.
- CUSIP→ticker mapping is best-effort; a few small foreign/tracking-stock
  positions (e.g. some Liberty Media lines, delisted Activision) are left
  unmapped and excluded from sizing and the backtest.
- Backtest ignores transaction costs and slippage (Alpaca paper is
  commission-free and Berkshire's quarterly turnover is low, so the effect
  is small — but it is not zero).
- One filer, one ~4-year window. This is machinery and an honest result,
  not a generalizable claim about 13F mirroring.
