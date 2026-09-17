"""Pull ABNB option chain (Oct/Nov/Dec 2026 expiries) via yfinance; save raw to sources/ with UTC stamp.
Run: py -3.13 docs/pitch-forecasts/questions/day1-move-5nov/datasets/pull_options.py
"""
import datetime as dt, json, pathlib, sys
import pandas as pd
import yfinance as yf

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "sources"
SRC.mkdir(exist_ok=True)
now = dt.datetime.now(dt.timezone.utc)
stamp = now.strftime("%Y%m%dT%H%M%SZ")
t = yf.Ticker("ABNB")
hist = t.history(period="15d")
hist.to_csv(SRC / f"yfinance_abnb_history_{stamp}.csv")
spot = float(hist["Close"].iloc[-1])
spot_date = str(hist.index[-1].date())
exps = list(t.options)
rows = []
for e in exps:
    if e < "2026-09-25" or e > "2027-01-31":
        continue
    ch = t.option_chain(e)
    for kind, df in (("call", ch.calls), ("put", ch.puts)):
        d = df.copy()
        d["type"] = kind
        d["expiry"] = e
        rows.append(d)
chain = pd.concat(rows, ignore_index=True)
chain.to_csv(SRC / f"yfinance_abnb_chain_{stamp}.csv", index=False)
meta = {"pull_utc": now.isoformat(), "spot": spot, "spot_date": spot_date, "expiries_all": exps,
        "expiries_saved": sorted(chain["expiry"].unique().tolist()), "n_contracts": int(len(chain))}
(SRC / f"yfinance_abnb_chain_meta_{stamp}.json").write_text(json.dumps(meta, indent=2))
print(json.dumps(meta, indent=2))
