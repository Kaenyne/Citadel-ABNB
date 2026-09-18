"""Pull the latest ABNB short-interest data: Nasdaq API (settlement series) and yfinance info (sharesShort etc.). Saves JSON to sources/."""
import json, pathlib, datetime as dt, sys
HERE = pathlib.Path(__file__).resolve().parent; SRC = HERE.parent/"sources"; SRC.mkdir(exist_ok=True)
ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
try:
    import requests
    r = requests.get("https://api.nasdaq.com/api/quote/ABNB/short-interest?assetclass=stocks", headers={"User-Agent":"Mozilla/5.0","Accept":"application/json","Origin":"https://www.nasdaq.com","Referer":"https://www.nasdaq.com/"}, timeout=30)
    print("nasdaq status", r.status_code)
    (SRC/f"nasdaq_short_interest_{ts}.json").write_text(r.text, encoding="utf-8")
    j = r.json(); rows = j.get("data",{}).get("shortInterestTable",{}).get("rows",[])
    for row in rows[:6]: print(row)
except Exception as e:
    print("nasdaq failed", e)
try:
    import yfinance as yf
    t = yf.Ticker("ABNB"); info = t.info
    keys = ["sharesOutstanding","impliedSharesOutstanding","floatShares","sharesShort","sharesShortPriorMonth","sharesShortPreviousMonthDate","dateShortInterest","shortRatio","shortPercentOfFloat","sharesPercentSharesOut","currentPrice","regularMarketPreviousClose","averageDailyVolume10Day","averageVolume"]
    sub = {k: info.get(k) for k in keys}
    for k in ["dateShortInterest","sharesShortPreviousMonthDate"]:
        if sub.get(k): sub[k+"_iso"] = dt.datetime.utcfromtimestamp(sub[k]).date().isoformat()
    sub["pulled_utc"] = ts
    json.dump(sub, open(SRC/f"yfinance_info_short_{ts}.json","w"), indent=1)
    print(json.dumps(sub, indent=1))
except Exception as e:
    print("yfinance failed", e)
