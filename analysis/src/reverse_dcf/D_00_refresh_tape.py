"""WS-D step 0: refresh the ABNB sell-side tape from yfinance (Yahoo Finance / Benzinga feed).

Run:  py -3.13 analysis/src/reverse_dcf/D_00_refresh_tape.py
Writes data/processed/reverse_dcf/D/
  D_analyst_actions_2026-09-12.csv      full upgrades_downgrades feed as pulled 12 Sep 2026
  D_yf_analyst_price_targets.csv        Ticker.analyst_price_targets (current/low/high/mean/median)
  D_yf_recommendations.csv              Ticker.recommendations (monthly strongBuy/buy/hold/sell/strongSell counts)
  D_tape_changes_since_0906.csv         actions in the new pull that are not in the 6 Sep pull
  D_prices_daily_to_0911.csv            yfinance daily close to 11 Sep 2026 (for the target-vs-price panel)
"""
import os, sys, datetime as dt
import pandas as pd
import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "reverse_dcf", "D")
os.makedirs(OUT, exist_ok=True)
PULL = dt.date.today().isoformat()
SRC = f"yfinance Ticker('ABNB').upgrades_downgrades (Yahoo Finance / Benzinga feed), pulled {PULL}"

t = yf.Ticker("ABNB")
ud = t.upgrades_downgrades.copy()
ud = ud.reset_index().rename(columns={"GradeDate": "grade_datetime"})
ud["grade_datetime"] = pd.to_datetime(ud["grade_datetime"]).dt.tz_localize(None)
ud["date"] = ud["grade_datetime"].dt.date.astype(str)
ud["source"] = SRC
for c in ["currentPriceTarget", "priorPriceTarget"]:
    if c not in ud.columns:
        ud[c] = 0.0
ud = ud.sort_values("grade_datetime")
ud.to_csv(os.path.join(OUT, f"D_analyst_actions_{PULL}.csv"), index=False)
print("upgrades_downgrades rows:", len(ud), "last:", ud.grade_datetime.max())

apt = t.analyst_price_targets
pd.DataFrame([dict(pulled=PULL, **apt)]).to_csv(os.path.join(OUT, "D_yf_analyst_price_targets.csv"), index=False)
print("analyst_price_targets:", apt)

rec = t.recommendations.copy()
rec["pulled"] = PULL
rec.to_csv(os.path.join(OUT, "D_yf_recommendations.csv"), index=False)
print(rec)

try:
    rs = t.recommendations_summary
    print("recommendations_summary:\n", rs)
except Exception as e:
    print("recommendations_summary failed:", e)

# diff vs the 6 Sep pull
old = pd.read_csv(os.path.join(ROOT, "data", "processed", "overnight", "09_analyst_actions.csv"))
old["grade_datetime"] = pd.to_datetime(old["grade_datetime"])
key = ["grade_datetime", "Firm"]
merged = ud.merge(old[key].assign(_old=1), on=key, how="left")
new = merged[merged._old.isna()].drop(columns="_old")
new.to_csv(os.path.join(OUT, "D_tape_changes_since_0906.csv"), index=False)
print("new actions since 6 Sep pull:", len(new))
print(new[["grade_datetime", "Firm", "ToGrade", "FromGrade", "Action", "priceTargetAction", "currentPriceTarget", "priorPriceTarget"]].to_string())
gone = old.merge(ud[key].assign(_new=1), on=key, how="left")
gone = gone[gone._new.isna()]
print("actions in old pull missing from new pull:", len(gone))
if len(gone):
    print(gone[["grade_datetime", "Firm", "ToGrade", "currentPriceTarget"]].tail(10).to_string())

px = yf.download("ABNB", start="2020-12-01", auto_adjust=False, progress=False)
if isinstance(px.columns, pd.MultiIndex):
    px.columns = px.columns.get_level_values(0)
px = px[["Close"]].reset_index().rename(columns={"Date": "date", "Close": "close"})
px["date"] = px["date"].dt.date.astype(str)
px.to_csv(os.path.join(OUT, "D_prices_daily_to_0911.csv"), index=False)
print(px.tail(8).to_string())
