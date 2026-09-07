"""20_executable_returns.py -- executable-entry event returns for every ABNB print.

Audit finding A02, defect 2: the existing excess_1d/5d/20d returns start from the close of the
PRINT DATE, i.e. before the release. ABNB reports after the US close, so that starting price
cannot be transacted with knowledge of the released numbers. This script rebuilds the event
returns from the OPEN of the first session after the release (the "reaction session"), which is
the earliest price a systematic trader acting on the released surprise can actually get.

READS
  data/processed/overnight/16_reaction_panel.csv   print_date / reaction_date per print
                                                   (falls back to 04_reaction_panel.csv)
  yfinance ABNB + QQQ daily OHLC (unadjusted Close and Open; ABNB pays no dividend and has had
  no split, so unadjusted open-to-close arithmetic is exact)

WRITES
  data/processed/overnight/20_prices_ohlc.csv       cached daily Open/Close for ABNB and QQQ
  data/processed/overnight/20_executable_returns.csv one row per print with, for each convention,
      the entry timestamp, entry price, exit date, exit price and QQQ-excess return.

CONVENTIONS PRODUCED (all excess = ABNB return minus QQQ return over the identical dates)
  legacy_1d/5d/20d   close(print_date) -> close(reaction session + h-1). NOT executable; kept
                     only so the restatement can be compared like for like.
  postclose_*        close(reaction session) -> close(reaction session + h-1). Entry at the first
                     post-release CLOSE: executable but forgoes the whole gap.
  open_*             OPEN(reaction session) -> close(reaction session + h-1). PRIMARY. Entry is
                     the first printed price after the release.
  h counts trading sessions with the reaction session as session 1, so open_5d exits at the close
  of the 5th session and open_20d at the close of the 20th.
  gap_pct            open(reaction session) / close(print_date) - 1, the part of the day-1 move
                     that the executable convention gives up.
Run: py -3.13 analysis/src/overnight/20_executable_returns.py
"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data/processed"; OUT = PROC / "overnight"
OUT.mkdir(parents=True, exist_ok=True)
CACHE = OUT / "20_prices_ohlc.csv"
HORIZONS = [1, 5, 20]


def load_prices(force=False):
    if CACHE.exists() and not force:
        return pd.read_csv(CACHE, parse_dates=["date"]).set_index("date")
    import yfinance as yf
    d = yf.download(["ABNB", "QQQ"], start="2020-12-01", end="2026-09-06",
                    auto_adjust=False, progress=False)
    px = pd.DataFrame({
        "abnb_open": d[("Open", "ABNB")], "abnb_close": d[("Close", "ABNB")],
        "qqq_open": d[("Open", "QQQ")], "qqq_close": d[("Close", "QQQ")]})
    px.index.name = "date"
    px = px.dropna(how="all")
    px.to_csv(CACHE)
    return px


def main():
    src = OUT / "16_reaction_panel.csv"
    if not src.exists():
        src = OUT / "04_reaction_panel.csv"
    p = pd.read_csv(src, parse_dates=["print_date", "reaction_date"])
    px = load_prices()
    idx = px.index

    rows = []
    for _, r in p.iterrows():
        pd_date, rx_date = r["print_date"], r["reaction_date"]
        # session index of the print date (last session <= print_date) and of the reaction session
        i_print = idx.searchsorted(pd_date, side="right") - 1
        i_rx = idx.searchsorted(rx_date, side="left")
        if i_print < 0 or i_rx >= len(idx):
            continue
        row = dict(print_quarter=r["print_quarter"],
                   print_date=pd_date.date(), reaction_date=idx[i_rx].date(),
                   release_time_convention="after US close on print_date",
                   pre_close_date=idx[i_print].date(),
                   pre_close=px["abnb_close"].iloc[i_print],
                   entry_open_time=f"{idx[i_rx].date()} 09:30 ET",
                   entry_open_px=px["abnb_open"].iloc[i_rx],
                   entry_postclose_time=f"{idx[i_rx].date()} 16:00 ET",
                   entry_postclose_px=px["abnb_close"].iloc[i_rx])
        row["gap_pct"] = (row["entry_open_px"] / row["pre_close"] - 1) * 100
        row["gap_excess_pct"] = row["gap_pct"] - (px["qqq_open"].iloc[i_rx] / px["qqq_close"].iloc[i_print] - 1) * 100
        for h in HORIZONS:
            j = i_rx + h - 1
            if j >= len(idx):
                for k in ("legacy", "postclose", "open"):
                    row[f"{k}_{h}d_pct"] = np.nan
                row[f"exit_date_{h}d"] = ""
                continue
            row[f"exit_date_{h}d"] = idx[j].date()
            a_x, q_x = px["abnb_close"].iloc[j], px["qqq_close"].iloc[j]
            # legacy: pre-release close entry
            row[f"legacy_{h}d_pct"] = ((a_x / px["abnb_close"].iloc[i_print] - 1)
                                       - (q_x / px["qqq_close"].iloc[i_print] - 1)) * 100
            # post-print close entry (h=1 is definitionally 0)
            row[f"postclose_{h}d_pct"] = ((a_x / px["abnb_close"].iloc[i_rx] - 1)
                                          - (q_x / px["qqq_close"].iloc[i_rx] - 1)) * 100
            # executable open entry
            row[f"open_{h}d_pct"] = ((a_x / px["abnb_open"].iloc[i_rx] - 1)
                                     - (q_x / px["qqq_open"].iloc[i_rx] - 1)) * 100
            row[f"exit_px_{h}d"] = a_x
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(OUT / "20_executable_returns.csv", index=False)
    print(out[["print_quarter", "gap_excess_pct", "legacy_1d_pct", "open_1d_pct",
               "legacy_20d_pct", "open_20d_pct", "postclose_20d_pct"]].round(2).to_string(index=False))
    print("\nrows:", len(out), "-> data/processed/overnight/20_executable_returns.csv")


if __name__ == "__main__":
    main()
