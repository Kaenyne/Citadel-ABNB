"""B1: relative currency strength indices for ABNB's geographic travel mix.

Builds, from FRED daily spot rates:
  1. a USD-per-unit daily panel for 23 currencies plus the broad dollar index
  2. quarterly averages and y/y log changes, 1Q18 to 3Q26 quarter-to-date
  3. destination-region currency baskets (reused from WS10 10_fx_basket.csv so the
     existing pass-through slopes stay comparable) and origin-region baskets (new)
  4. an inbound guest purchasing-power index (IPP) per destination region:
        IPP_d = sum_o w[o,d] * ( dlog(USD per origin basket o) - dlog(USD per dest basket d) )
     positive = origin guests' money goes further in destination d than a year ago
  5. the reverse, outbound affordability per origin region:
        OA_o = sum_d v[o,d] * ( dlog(USD per origin basket o) - dlog(USD per dest basket d) )
     with v derived from w and regional nights shares so the two are consistent
  6. the intra-quarter path of every index for 3Q26 to the latest FRED observation.

Run: py -3.13 analysis/src/overnight2/B1_fx_relative_strength.py
Writes data/processed/overnight2/B/fred/*.csv and data/processed/overnight2/B/*.csv
"""
from __future__ import annotations

import io
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\krish\citadel-abnb-overnight2")
MAIN = Path(r"C:\Users\krish\citadel-abnb")
OUT = ROOT / "data" / "processed" / "overnight2" / "B"
FREDDIR = OUT / "fred"
OUT.mkdir(parents=True, exist_ok=True)
FREDDIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- FRED pull
# key: FRED id, value: (currency code, orientation)
#   "usd_per" -> series is already USD per unit of foreign currency
#   "per_usd" -> series is foreign currency units per USD, so invert
SERIES = {
    "DEXUSEU": ("EUR", "usd_per"),
    "DEXUSUK": ("GBP", "usd_per"),
    "DEXUSAL": ("AUD", "usd_per"),
    "DEXUSNZ": ("NZD", "usd_per"),
    "DEXCAUS": ("CAD", "per_usd"),
    "DEXMXUS": ("MXN", "per_usd"),
    "DEXBZUS": ("BRL", "per_usd"),
    "DEXJPUS": ("JPY", "per_usd"),
    "DEXKOUS": ("KRW", "per_usd"),
    "DEXINUS": ("INR", "per_usd"),
    "DEXCHUS": ("CNY", "per_usd"),
    "DEXSZUS": ("CHF", "per_usd"),
    "DEXSDUS": ("SEK", "per_usd"),
    "DEXNOUS": ("NOK", "per_usd"),
    "DEXDNUS": ("DKK", "per_usd"),
    "DEXTHUS": ("THB", "per_usd"),
    "DEXSIUS": ("SGD", "per_usd"),
    "DEXTAUS": ("TWD", "per_usd"),
    "DEXHKUS": ("HKD", "per_usd"),
    "DEXMAUS": ("MYR", "per_usd"),
    "DEXSFUS": ("ZAR", "per_usd"),
    "DTWEXBGS": ("USD_BROAD", "index"),
}


def fetch(fred_id: str) -> pd.DataFrame:
    """Fetch one FRED series as CSV, cache it, return date/value frame."""
    cache = FREDDIR / f"{fred_id}.csv"
    if cache.exists():
        raw = cache.read_text(encoding="utf-8")
    else:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}"
        with urllib.request.urlopen(url, timeout=60) as fh:
            raw = fh.read().decode("utf-8")
        cache.write_text(raw, encoding="utf-8")
    df = pd.read_csv(io.StringIO(raw))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna()


daily = {}
for fid, (ccy, orient) in SERIES.items():
    df = fetch(fid)
    s = df.set_index("date")["value"]
    if orient == "per_usd":
        s = 1.0 / s
    daily[ccy] = s
    print(f"{fid:10s} {ccy:10s} n={len(s):6d} last={s.index[-1].date()} {s.iloc[-1]:.6f}")

DAILY = pd.DataFrame(daily).sort_index()
DAILY["USD"] = 1.0
DAILY = DAILY[DAILY.index >= "2017-01-01"]
LAST_OBS = DAILY.dropna(subset=["EUR"]).index[-1]
print(f"\nlatest FRED FX observation: {LAST_OBS.date()}")
DAILY.to_csv(OUT / "B_fx_daily_usd_per_unit.csv")

# ---------------------------------------------------------------- quarterly
q = DAILY.copy()
q["quarter"] = q.index.to_period("Q")
QAVG = q.groupby("quarter").mean(numeric_only=True)
QAVG.index = [f"{p.quarter}Q{str(p.year)[2:]}" for p in QAVG.index]
QAVG.index.name = "quarter"

# y/y log change in percent (positive = currency stronger vs USD than a year ago)
QYOY = 100.0 * np.log(QAVG / QAVG.shift(4))
QYOY = QYOY.round(4)
QAVG.round(8).to_csv(OUT / "B_fx_quarterly_avg.csv")
QYOY.to_csv(OUT / "B_fx_quarterly_yoy_logpct.csv")

# ---------------------------------------------------------------- baskets
# Destination baskets: identical in structure to WS10's 10_fx_basket.csv judgement
# weights (NA/EMEA/LatAm/APAC), so the WS10 ADR pass-through slopes remain usable.
DEST_BASKET = {
    "na": {"USD": 0.90, "CAD": 0.08, "MXN": 0.02},
    "emea": {"EUR": 0.70, "GBP": 0.25, "USD": 0.05},
    "latam": {"BRL": 0.55, "MXN": 0.38, "USD": 0.07},
    "apac": {"AUD": 0.55, "JPY": 0.20, "KRW": 0.10, "INR": 0.07, "USD": 0.08},
}
# Origin baskets: the currency a guest from that region earns in. New to this
# workstream; wider than the destination baskets because origin demand in EMEA
# and APAC is spread over more currencies than listing supply is.
ORIGIN_BASKET = {
    "na": {"USD": 0.88, "CAD": 0.10, "MXN": 0.02},
    "emea": {"EUR": 0.56, "GBP": 0.22, "CHF": 0.04, "SEK": 0.03, "NOK": 0.02,
             "DKK": 0.01, "ZAR": 0.02, "USD": 0.10},
    "latam": {"BRL": 0.48, "MXN": 0.37, "USD": 0.15},
    "apac": {"AUD": 0.30, "JPY": 0.22, "INR": 0.14, "KRW": 0.09, "CNY": 0.08,
             "SGD": 0.05, "NZD": 0.04, "THB": 0.03, "TWD": 0.03, "HKD": 0.02},
}

# Origin mix of each destination region's nights, w[origin][destination].
# Anchors, all stated in the note:
#  - cross-border was 46% of gross nights in 1Q24 and 51% in 1Q19 (letters)
#  - "only a single-digit percentage of global nights booked are international
#    inbound to the U.S." (1Q25 letter); management said 2-3% on the 1Q25 call
#  - "the majority of travel in North America ... is domestic" (4Q22 letter)
#  - "cross-border continues to drive the majority of nights booked in APAC"
#    (4Q24 letter); cross-border nights to APAC grew 22-29% y/y in 2023-24
#  - Eurostat: foreign-residence nights are 57-67% of EU27 platform nights, and
#    the large majority of those are intra-European
#  - NTTO: Canada and Mexico were 48.6% of 2025 US inbound arrivals, overseas 51.4%
W = {  # W[dest][origin]
    "na":    {"na": 0.88, "emea": 0.055, "latam": 0.030, "apac": 0.035},
    "emea":  {"emea": 0.84, "na": 0.100, "latam": 0.025, "apac": 0.035},
    "latam": {"latam": 0.80, "na": 0.130, "emea": 0.050, "apac": 0.020},
    "apac":  {"apac": 0.80, "emea": 0.090, "na": 0.080, "latam": 0.030},
}
# Nights shares by destination region, 2Q26. These use the CORRECTED shares from
# research/notes/2026-09-07_adr-decomposition.md, which found WS10's regional ADR
# index had LatAm and APAC swapped (LatAm 0.68 / APAC 0.59 used; the 10-K gives
# LatAm 0.554 / APAC 0.690 for 2025) and therefore understated LatAm's nights share
# by about a fifth. WS10 had 2Q26 at NA 28.8 / EMEA 39.7 / LatAm 15.1 / APAC 16.3;
# data/processed/adr/04_regional_quarterly.csv rebuilds 2Q26 as below.
NIGHTS_SHARE = {"na": 0.283, "emea": 0.416, "latam": 0.179, "apac": 0.123}
REGIONS = ["na", "emea", "latam", "apac"]


def basket_level(frame: pd.DataFrame, weights: dict) -> pd.Series:
    """Geometric weighted USD value of a currency basket."""
    tot = sum(weights.values())
    acc = None
    for ccy, wt in weights.items():
        col = np.log(frame[ccy]) * (wt / tot)
        acc = col if acc is None else acc + col
    return np.exp(acc)


def build_indices(frame: pd.DataFrame, lag: int) -> pd.DataFrame:
    """frame: periods x currencies of USD-per-unit. lag: periods for y/y."""
    dest = pd.DataFrame({r: basket_level(frame, DEST_BASKET[r]) for r in REGIONS})
    orig = pd.DataFrame({r: basket_level(frame, ORIGIN_BASKET[r]) for r in REGIONS})
    d_dest = 100.0 * np.log(dest / dest.shift(lag))
    d_orig = 100.0 * np.log(orig / orig.shift(lag))

    out = pd.DataFrame(index=frame.index)
    for r in REGIONS:
        out[f"dest_basket_{r}_yoy"] = d_dest[r]
        out[f"origin_basket_{r}_yoy"] = d_orig[r]

    # inbound purchasing power per destination
    for d in REGIONS:
        ipp = 0.0
        xb = 0.0  # cross-border-only version (drops the intra-regional leg)
        for o, wt in W[d].items():
            term = d_orig[o] - d_dest[d]
            ipp = ipp + wt * term
            if o != d:
                xb = xb + wt * term
        out[f"ipp_{d}"] = ipp
        out[f"ipp_xb_{d}"] = xb / sum(v for k, v in W[d].items() if k != d)

    # destination mix of each origin's nights, consistent with W and nights shares
    V = {}
    for o in REGIONS:
        raw = {d: W[d].get(o, 0.0) * NIGHTS_SHARE[d] for d in REGIONS}
        tot = sum(raw.values())
        V[o] = {d: raw[d] / tot for d in REGIONS}
    for o in REGIONS:
        oa = 0.0
        xb = 0.0
        for d, wt in V[o].items():
            term = d_orig[o] - d_dest[d]
            oa = oa + wt * term
            if d != o:
                xb = xb + wt * term
        out[f"oa_{o}"] = oa
        out[f"oa_xb_{o}"] = xb / sum(v for k, v in V[o].items() if k != o)

    # global cross-border attractiveness dispersion: how unequal the four IPPs are
    ipps = out[[f"ipp_{r}" for r in REGIONS]]
    out["ipp_dispersion_sd"] = ipps.std(axis=1)
    out["ipp_global_weighted"] = sum(NIGHTS_SHARE[r] * out[f"ipp_{r}"] for r in REGIONS)
    # USD-vs-rest gap: the single number that summarises the 2025-26 story
    out["usd_vs_rest_yoy"] = -sum(
        NIGHTS_SHARE[r] * out[f"origin_basket_{r}_yoy"] for r in REGIONS)
    return out.round(4), V


QIDX, V = build_indices(QAVG, 4)
QIDX.to_csv(OUT / "B_relative_strength_quarterly.csv")

# weights audit trail
rows = []
for d in REGIONS:
    for o, wt in W[d].items():
        rows.append({"kind": "origin_mix_of_destination", "destination": d,
                     "origin": o, "weight": wt})
for o in REGIONS:
    for d, wt in V[o].items():
        rows.append({"kind": "destination_mix_of_origin", "destination": d,
                     "origin": o, "weight": round(wt, 4)})
for r in REGIONS:
    for ccy, wt in DEST_BASKET[r].items():
        rows.append({"kind": "destination_currency_basket", "destination": r,
                     "origin": "", "currency": ccy, "weight": wt})
    for ccy, wt in ORIGIN_BASKET[r].items():
        rows.append({"kind": "origin_currency_basket", "destination": "",
                     "origin": r, "currency": ccy, "weight": wt})
pd.DataFrame(rows).to_csv(OUT / "B_index_weights.csv", index=False)

# ---------------------------------------------------------------- intra-quarter
# 3Q26 to date: rebuild the indices on a cumulative quarter-to-date average so the
# path shows how the index has drifted inside the quarter, against the same
# quarter-average base a year earlier.
cur = DAILY[(DAILY.index >= "2026-07-01") & (DAILY.index <= LAST_OBS)]
base = DAILY[(DAILY.index >= "2025-07-01") & (DAILY.index <= "2025-09-30")]
ccy_cols = [c for c in DAILY.columns if c != "USD_BROAD"]
base_avg = base[ccy_cols].mean()

path = []
for i, dt in enumerate(cur.index):
    qtd = cur[ccy_cols].iloc[: i + 1].mean()
    frame = pd.DataFrame([base_avg, qtd], index=["base", "qtd"])
    idx, _ = build_indices(frame, 1)
    row = idx.loc["qtd"].to_dict()
    row["date"] = dt.date().isoformat()
    row["n_days_in_qtd"] = i + 1
    path.append(row)
PATH = pd.DataFrame(path).set_index("date")
PATH.to_csv(OUT / "B_intraquarter_3q26_path.csv")

# flat-spot 3Q26 and 4Q26: hold the latest daily spot for the remainder
spot = DAILY[ccy_cols].loc[LAST_OBS]
rem_3q = pd.date_range(LAST_OBS + pd.Timedelta(days=1), "2026-09-30", freq="B")
q3_full = pd.concat([cur[ccy_cols],
                     pd.DataFrame([spot] * len(rem_3q), index=rem_3q)]).mean()
q4_days = pd.date_range("2026-10-01", "2026-12-31", freq="B")
q4_full = pd.DataFrame([spot] * len(q4_days), index=q4_days).mean()
base_4q = DAILY[(DAILY.index >= "2025-10-01") & (DAILY.index <= "2025-12-31")][ccy_cols].mean()

scen = {}
for label, cursor, basis in [("3Q26_flat_spot", q3_full, base_avg),
                             ("4Q26_flat_spot", q4_full, base_4q)]:
    frame = pd.DataFrame([basis, cursor], index=["base", "fwd"])
    idx, _ = build_indices(frame, 1)
    scen[label] = idx.loc["fwd"]
SCEN = pd.DataFrame(scen).T
SCEN.index.name = "scenario"
SCEN.round(4).to_csv(OUT / "B_forward_flat_spot_indices.csv")

# ------------------------------------------------- named bilateral corridors
# The corridors management actually talks about, as origin-currency-per-destination
# -currency y/y log change. Positive = the origin guest's money goes further in the
# destination than a year ago, i.e. the corridor got cheaper.
CORRIDORS = {
    "us_to_eurozone": ("USD", "EUR"),
    "us_to_uk": ("USD", "GBP"),
    "us_to_japan": ("USD", "JPY"),
    "us_to_mexico": ("USD", "MXN"),
    "us_to_brazil": ("USD", "BRL"),
    "canada_to_us": ("CAD", "USD"),
    "canada_to_mexico": ("CAD", "MXN"),
    "eurozone_to_us": ("EUR", "USD"),
    "uk_to_us": ("GBP", "USD"),
    "japan_to_us": ("JPY", "USD"),
    "japan_to_domestic": ("JPY", "JPY"),
    "brazil_to_us": ("BRL", "USD"),
    "brazil_to_eurozone": ("BRL", "EUR"),
    "mexico_to_us": ("MXN", "USD"),
    "india_to_eurozone": ("INR", "EUR"),
    "india_to_apac_aud": ("INR", "AUD"),
    "china_to_apac_jpy": ("CNY", "JPY"),
    "korea_to_japan": ("KRW", "JPY"),
    "australia_to_us": ("AUD", "USD"),
    "australia_to_japan": ("AUD", "JPY"),
}
corr_q = pd.DataFrame(index=QAVG.index)
for name, (o, d) in CORRIDORS.items():
    lvl = QAVG[o] / QAVG[d]
    corr_q[name] = (100.0 * np.log(lvl / lvl.shift(4))).round(3)
corr_q.to_csv(OUT / "B_corridor_relative_strength_quarterly.csv")

corr_fwd = {}
for label, cursor, basis in [("3Q26_flat_spot", q3_full, base_avg),
                             ("4Q26_flat_spot", q4_full, base_4q)]:
    corr_fwd[label] = {n: round(100.0 * np.log((cursor[o] / cursor[d])
                                               / (basis[o] / basis[d])), 3)
                       for n, (o, d) in CORRIDORS.items()}
pd.DataFrame(corr_fwd).T.to_csv(OUT / "B_corridor_forward_flat_spot.csv")

meta = {
    "latest_fred_fx_observation": LAST_OBS.date().isoformat(),
    "n_days_3q26_observed": int(len(cur)),
    "n_business_days_3q26_assumed_flat": int(len(rem_3q)),
    "note": ("3Q26 quarter-to-date uses observed daily rates to the latest FRED "
             "observation; the flat-spot scenario holds that day's spot for the "
             "remaining business days of 3Q26 and for all of 4Q26."),
}
(OUT / "B_fx_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

print("\n--- quarterly indices, last 10 quarters ---")
cols = [f"ipp_{r}" for r in REGIONS] + [f"oa_{r}" for r in REGIONS] + ["usd_vs_rest_yoy"]
print(QIDX[cols].tail(10).to_string())
print("\n--- forward flat spot ---")
print(SCEN[cols].to_string())
print("\n--- 3Q26 intra-quarter path, selected dates ---")
print(PATH[cols].iloc[::10].to_string())
print(json.dumps(meta, indent=2))
