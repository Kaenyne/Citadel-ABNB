"""Pull ABNB price history, option chains (Dec 2026 / Jan / Feb / Mar 2027), analyst targets and
upgrades/downgrades with yfinance; save raw captures to sources/ with a UTC timestamp.
Run: py -3.13 docs/pitch-forecasts/questions/close-15dec-2026/datasets/pull_yfinance.py (from repo root)."""
import datetime as dt, json, pathlib, sys
import pandas as pd, yfinance as yf
here = pathlib.Path(__file__).resolve().parent.parent
src = here / "sources"; src.mkdir(exist_ok=True)
ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
t = yf.Ticker("ABNB")
h = t.history(period="2y", auto_adjust=False)
h.to_csv(src / f"yfinance_abnb_history_2y_{ts}.csv")
print("last closes:\n", h[["Close"]].tail(5))
q = yf.Ticker("QQQ").history(period="2y", auto_adjust=False)
q.to_csv(src / f"yfinance_qqq_history_2y_{ts}.csv")
irx = yf.Ticker("^IRX").history(period="1mo")
irx.to_csv(src / f"yfinance_irx_{ts}.csv"); print("IRX", irx["Close"].tail(1))
exps = t.options; print("expiries", exps)
json.dump(list(exps), open(src / f"yfinance_option_expiries_{ts}.json", "w"))
want = [e for e in exps if e[:7] in ("2026-10", "2026-11", "2026-12", "2027-01", "2027-02", "2027-03", "2027-06")]
frames = []
for e in want:
    ch = t.option_chain(e)
    for side, df in (("call", ch.calls), ("put", ch.puts)):
        d = df.copy(); d["expiry"] = e; d["type"] = side; frames.append(d)
allc = pd.concat(frames, ignore_index=True)
allc.to_csv(src / f"yfinance_option_chain_{ts}.csv", index=False)
print("chain rows", len(allc), "expiries", want)
try:
    apt = t.analyst_price_targets; print("targets", apt)
    json.dump(apt, open(src / f"yfinance_analyst_price_targets_{ts}.json", "w"), default=str)
except Exception as ex: print("apt fail", ex)
try:
    ud = t.upgrades_downgrades; ud.to_csv(src / f"yfinance_upgrades_downgrades_{ts}.csv"); print("ud rows", len(ud)); print(ud.head(15))
except Exception as ex: print("ud fail", ex)
try:
    cal = t.calendar; json.dump(cal, open(src / f"yfinance_calendar_{ts}.json", "w"), default=str); print(cal)
except Exception as ex: print("cal fail", ex)
try:
    rec = t.recommendations; rec.to_csv(src / f"yfinance_recommendations_{ts}.csv"); print(rec)
except Exception as ex: print("rec fail", ex)
info = t.info
json.dump({k: info.get(k) for k in ("targetMeanPrice","targetMedianPrice","targetHighPrice","targetLowPrice","numberOfAnalystOpinions","recommendationMean","recommendationKey","sharesOutstanding","shortPercentOfFloat","shortRatio","sharesShort","sharesShortPriorMonth","dateShortInterest","beta","regularMarketPrice","previousClose","fiftyTwoWeekHigh","fiftyTwoWeekLow")}, open(src / f"yfinance_info_subset_{ts}.json", "w"), indent=1, default=str)
print({k: info.get(k) for k in ("targetMeanPrice","targetMedianPrice","numberOfAnalystOpinions","shortPercentOfFloat","regularMarketPrice","previousClose")})
print("TS", ts)
