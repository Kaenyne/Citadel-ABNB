"""08_trends_pull.py -- Google Trends weekly interest, US and worldwide, 2019 to date.

Reads:  nothing local (Google Trends via pytrends; unofficial endpoint, rate-limited).
Writes: data/processed/overnight/08_trends_weekly.csv (long: week, geo, payload, term, value_raw,
        window, value_stitched) and a JSON log of every request/failure in the scratch dir.

Design
- Google returns weekly resolution only for windows shorter than ~5 years, so 2019-01-01..today is
  pulled as two overlapping windows (A: 2019-01-06..2023-06-25, B: 2022-01-02..today) and window B
  is rescaled onto A's scale using the median ratio over the overlap, per term.
- Two comparative payloads (max 5 terms each), both anchored on "airbnb", plus three single-term pulls:
    P1: airbnb, vrbo, booking.com, hotels.com, expedia
    P2: airbnb, airbnb near me, hotels near me, vacation rental, hotel
- Requests are paced (>= 12 s apart) and retried with exponential backoff on 429 / ResponseError.
- If nothing can be fetched the script exits non-zero and writes the log; the note documents it.
"""
import json, sys, time, random
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/overnight/08_trends_weekly.csv"
SCR = Path(r"C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb\fe93ae72-a37b-4547-991f-690c32a0f6a0\scratchpad\08")
SCR.mkdir(parents=True, exist_ok=True)
LOG = SCR / "trends_pull_log.json"

PAYLOADS = {
    "P1_peers": ["airbnb", "vrbo", "booking.com", "hotels.com", "expedia"],
    "P2_category": ["airbnb", "airbnb near me", "hotels near me", "vacation rental", "hotel"],
    # small terms are rounded to 0-1 inside a comparative payload with "hotel" (Google's integer 0-100 scale),
    # so they are also pulled alone (own scale; y/y is valid, share-of-search is not)
    "S_airbnb_near_me": ["airbnb near me"],
    "S_hotels_near_me": ["hotels near me"],
    "S_vacation_rental": ["vacation rental"],
}
WINDOWS = {"A": "2019-01-06 2023-06-25", "B": "2022-01-02 2026-09-06"}
GEOS = {"US": "US", "WW": ""}
log = []

def fetch(pt, kws, tf, geo, tries=6):
    delay = 20
    for i in range(tries):
        try:
            pt.build_payload(kws, timeframe=tf, geo=geo)
            df = pt.interest_over_time()
            log.append({"kws": kws, "tf": tf, "geo": geo, "try": i, "ok": True, "rows": len(df)})
            return df
        except Exception as e:  # noqa
            msg = f"{type(e).__name__}: {e}"[:300]
            log.append({"kws": kws, "tf": tf, "geo": geo, "try": i, "ok": False, "err": msg})
            print("  fail", i, msg, flush=True)
            time.sleep(delay + random.uniform(0, 5))
            delay = min(delay * 2, 300)
    return None

def main():
    from pytrends.request import TrendReq
    frames = []
    for gname, geo in GEOS.items():
        # fresh client per geo: pytrends keeps the previous geo when geo == "" (self.geo = geo or self.geo)
        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 30), retries=0)
        for pname, kws in PAYLOADS.items():
            for wname, tf in WINDOWS.items():
                print(f"pull {gname} {pname} {wname}", flush=True)
                df = fetch(pt, kws, tf, geo)
                time.sleep(12 + random.uniform(0, 6))
                if df is None or df.empty:
                    continue
                df = df.drop(columns=[c for c in df.columns if c == "isPartial"])
                long = df.reset_index().melt(id_vars="date", var_name="term", value_name="value_raw")
                long["geo"] = gname; long["payload"] = pname; long["window"] = wname
                frames.append(long)
    LOG.write_text(json.dumps(log, indent=1))
    if not frames:
        print("NO DATA FETCHED", flush=True); sys.exit(2)
    w = pd.concat(frames, ignore_index=True)
    w["date"] = pd.to_datetime(w["date"])
    # stitch: rescale window B to A per (geo, payload, term) on the overlap
    out = []
    for (g, p, t), d in w.groupby(["geo", "payload", "term"]):
        a = d[d.window == "A"].set_index("date")["value_raw"]
        b = d[d.window == "B"].set_index("date")["value_raw"]
        if len(a) and len(b):
            ov = a.index.intersection(b.index)
            ratio = (a.loc[ov] / b.loc[ov].replace(0, pd.NA)).dropna().median() if len(ov) else 1.0
            ratio = float(ratio) if pd.notna(ratio) and ratio > 0 else 1.0
            s = pd.concat([a[a.index < b.index.min()], b * ratio]).sort_index()
        else:
            s = (a if len(a) else b).sort_index(); ratio = None
        dd = s.rename("value_stitched").reset_index().rename(columns={"index": "date"})
        dd["geo"] = g; dd["payload"] = p; dd["term"] = t; dd["stitch_ratio_B_to_A"] = ratio
        out.append(dd)
    st = pd.concat(out, ignore_index=True)
    res = w.merge(st, on=["date", "geo", "payload", "term"], how="right")
    res = res.sort_values(["geo", "payload", "term", "date", "window"])
    res.to_csv(OUT, index=False)
    print("wrote", OUT, len(res), flush=True)

if __name__ == "__main__":
    main()
