"""
01_fetch.py - inputs for the peer-event stock study.

(a) Daily adjusted closes for ABNB, the travel complex and benchmarks (Yahoo Finance via yfinance)
    -> data/raw/prices/peer_event_closes.csv
(b) Earnings-release dates and acceptance timestamps for every US filer in the set, from SEC EDGAR
    (8-K carrying Item 2.02, "Results of Operations"). EDGAR acceptanceDateTime is Eastern.
    -> data/raw/peers/earnings_8k_dates.csv

Run: py -3.13 analysis/src/peer_readthrough/01_fetch.py
"""
import json, os, time, urllib.request
from pathlib import Path
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[3]
PRICES = ROOT / "data" / "raw" / "prices"
PEERS = ROOT / "data" / "raw" / "peers"
PRICES.mkdir(parents=True, exist_ok=True); PEERS.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": os.environ.get("SEC_USER_AGENT", "Citadel-ABNB student research ksurapaneni@ufl.edu")}
START, END = "2020-11-01", "2026-09-05"

# ticker -> (CIK or None if not a US 8-K filer, group)
UNIVERSE = {
    "ABNB": ("0001559720", "subject"),
    # online travel agencies / marketplaces
    "BKNG": ("0001075531", "ota"),
    "EXPE": ("0001324424", "ota"),
    "TRIP": ("0001526520", "ota"),
    "SABR": ("0001597033", "distribution"),
    "TCOM": (None, "ota_intl"),          # foreign private issuer, 6-K
    "DESP": (None, "ota_intl"),
    "MMYT": (None, "ota_intl"),
    # hotels / lodging C-corps
    "MAR":  ("0001048286", "hotel"),
    "HLT":  ("0001585689", "hotel"),
    "H":    ("0001468174", "hotel"),
    "WH":   ("0001722684", "hotel"),
    "CHH":  ("0001046311", "hotel"),
    "IHG":  (None, "hotel_intl"),
    # timeshare / vacation rental adjacent
    "HGV":  ("0001674168", "timeshare"),
    "TNL":  ("0001361658", "timeshare"),
    "VAC":  ("0001524358", "timeshare"),
    "VCSA": ("0001874944", "str"),       # Vacasa
    "SOND": ("0001819395", "str"),       # Sonder
    # travel demand read-throughs
    "DAL":  ("0000027904", "airline"),
    "UAL":  ("0000100517", "airline"),
    "LUV":  ("0000092380", "airline"),
    "RCL":  ("0000884887", "cruise"),
    "CCL":  ("0000815097", "cruise"),
    # benchmarks
    "QQQ": (None, "bench"), "SPY": (None, "bench"), "XLY": (None, "bench"), "JETS": (None, "bench"),
}


def fetch_prices():
    out = PRICES / "peer_event_closes.csv"
    tick = list(UNIVERSE)
    px = yf.download(tick, start=START, end=END, auto_adjust=True, progress=False)["Close"]
    px = px.dropna(how="all")
    px.index.name = "date"
    px.to_csv(out, float_format="%.4f")
    print(f"prices -> {out}  {px.shape[0]} rows x {px.shape[1]} tickers")
    print("coverage (first/last non-null):")
    for t in px.columns:
        s = px[t].dropna()
        print(f"  {t:5s} {s.index.min().date()} .. {s.index.max().date()}  n={len(s)}")
    return px


def get(url):
    time.sleep(0.35)
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8", "replace")


def earnings_8ks(cik):
    sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik}.json"))
    pages = [sub["filings"]["recent"]]
    for f in sub["filings"]["files"]:
        pages.append(json.loads(get(f"https://data.sec.gov/submissions/{f['name']}")))
    rows = []
    for p in pages:
        for form, items, fdate, acc, accept in zip(p["form"], p["items"], p["filingDate"], p["accessionNumber"], p["acceptanceDateTime"]):
            if form == "8-K" and fdate >= "2020-11-01" and "2.02" in (items or ""):
                rows.append(dict(filing_date=fdate, acceptance_et=accept, accession=acc, items=items))
    return rows


def fetch_dates():
    out = PEERS / "earnings_8k_dates.csv"
    rows = []
    for tk, (cik, grp) in UNIVERSE.items():
        if cik is None:
            continue
        try:
            r = earnings_8ks(cik)
        except Exception as e:
            print(f"  {tk}: FAILED {e}")
            continue
        for x in r:
            rows.append(dict(ticker=tk, group=grp, cik=cik, **x))
        print(f"  {tk:5s} {len(r)} earnings 8-Ks")
    df = pd.DataFrame(rows).sort_values(["ticker", "filing_date"])
    df.to_csv(out, index=False)
    print(f"earnings dates -> {out}  {len(df)} rows")
    return df


if __name__ == "__main__":
    fetch_prices()
    print("\nEDGAR 8-K Item 2.02:")
    fetch_dates()
