"""Workstream B, step 0: pull every listed ABNB option expiry from yfinance and save raw.

Writes data/processed/reverse_dcf/B/raw_chain_<UTC timestamp>.csv (one row per contract, both
sides), B_pull_meta.json (spot, timestamp, expiries), and refreshes daily prices to
B_prices_daily.csv.  Run: py -3.13 analysis/src/reverse_dcf/B_pull_chains.py
"""
from __future__ import annotations
import datetime as dt, json, time
from pathlib import Path
import pandas as pd, yfinance as yf

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "reverse_dcf" / "B"
OUT.mkdir(parents=True, exist_ok=True)

t = yf.Ticker("ABNB")
now_utc = dt.datetime.now(dt.timezone.utc)
stamp = now_utc.strftime("%Y%m%dT%H%M%SZ")
hist = t.history(period="max", auto_adjust=False)
hist.index = hist.index.tz_localize(None)
hist = hist[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
hist.to_csv(OUT / "B_prices_daily.csv", index_label="date")
spot = float(hist["Close"].iloc[-1]); spot_date = str(hist.index[-1].date())
fi = t.fast_info
try:
    last = float(fi["last_price"])
except Exception:
    last = float("nan")

rows = []
exps = list(t.options)
for e in exps:
    for attempt in range(3):
        try:
            ch = t.option_chain(e); break
        except Exception as ex:
            print("retry", e, ex); time.sleep(2)
    else:
        continue
    for side, df in (("call", ch.calls), ("put", ch.puts)):
        d = df.copy(); d["side"] = side; d["expiry"] = e; rows.append(d)
    time.sleep(0.4)
raw = pd.concat(rows, ignore_index=True)
raw["pull_utc"] = now_utc.isoformat()
raw.to_csv(OUT / f"raw_chain_{stamp}.csv", index=False)
meta = {"pull_utc": now_utc.isoformat(), "spot_last_close": spot, "spot_close_date": spot_date,
        "fast_info_last_price": last, "expiries": exps, "n_contracts": int(len(raw)),
        "raw_file": f"raw_chain_{stamp}.csv"}
json.dump(meta, open(OUT / "B_pull_meta.json", "w"), indent=2)
print(json.dumps(meta, indent=2))
print(hist.tail(8)[["Open", "Close"]])
