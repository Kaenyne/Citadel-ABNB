"""Workstream 27: which end of the regional nights bucket, and the FY27 nights band.

Part A. For 4Q24-2Q26 Airbnb gave regional nights growth only as buckets ("mid-single digits").
Regional revenue (XBRL geography) and regional reported ADR are hard numbers, so
implied nights y/y = (1+rev)/(1+ADR)/(1+take-rate y/y)/(1+FX timing wedge) - 1 is an independent read.
Each region is then placed inside its bucket, as close as possible to the revenue-implied value,
subject to the share-weighted sum reproducing reported total nights growth.

Part B. Every 2Q26 bucket is +/-1pp wide. The forward regional growth rates are set relative to those
buckets, so the same +/-1pp is carried through 3Q26, 4Q26 and FY27 as a band around the base case,
using the driver model's regional mechanics (prior-year nights by region x growth less regulatory drag).

Run:  py -3.13 analysis/src/overnight/27_regional_bucket_check.py
Writes: data/processed/overnight/27_regional_bucket_check.csv, 27_nights_band.csv
"""
import csv
import os
import numpy as np
from scipy.optimize import minimize

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OD = lambda f: os.path.join(ROOT, "data", "processed", "overnight", f)
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8")))
f = lambda x: float(x) if x not in ("", None) else np.nan

REG = ["na", "emea", "latam", "apac"]
Q = ["4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
QS = lambda q: (int(q[0]), 2000 + int(q[2:]))
prev = lambda q: f"{q[0]}Q{int(q[2:]) - 1:02d}"

panel = {r["quarter"]: r for r in rd(OD("10_regional_panel_quarterly.csv"))}
kpi = {r["quarter"]: r for r in rd(OD("02_kpi_panel_quarterly.csv"))}

# ---------- Part A: cross-check and pick ----------
rows = []
for q in Q:
    p, k, kp = panel[q], kpi[q], kpi[prev(q)]
    take_yoy = f(k["take_rate_pct"]) / f(kp["take_rate_pct"]) - 1
    wedge = (1 + f(k["fx_pts_revenue"]) / 100) / (1 + f(k["fx_pts_adr"]) / 100) - 1
    total = f(p["total_nights_yoy_pct"])
    lo = np.array([f(p[f"{r}_nights_yoy_lo"]) for r in REG])
    hi = np.array([f(p[f"{r}_nights_yoy_hi"]) for r in REG])
    mid = (lo + hi) / 2
    # shares of the prior-year quarter weight the growth contributions
    sh = np.array([f(panel[prev(q)][f"{r}_nights_share_est_pct"]) for r in REG]) / 100
    rev = np.array([f(p[f"{r}_revenue_yoy_pct"]) for r in REG]) / 100
    adr = np.array([f(p[f"{r}_adr_yoy_reported_pct"]) for r in REG]) / 100
    implied = ((1 + rev) / (1 + adr) / (1 + take_yoy) / (1 + wedge) - 1) * 100
    # weight: revenue-implied values are noisy (regional revenue mix, hotels, timing); ~2pp sd
    target = np.where(np.isnan(implied), mid, implied)
    res = minimize(lambda x: np.sum((x - target) ** 2), mid, bounds=list(zip(lo, hi)),
                   constraints=[{"type": "eq", "fun": lambda x: sh @ x - total}], method="SLSQP")
    pick = res.x if res.success else mid
    for i, r in enumerate(REG):
        pos = "low" if pick[i] - lo[i] < 0.25 else "high" if hi[i] - pick[i] < 0.25 else "inside"
        rows.append(dict(quarter=q, region=r, bucket_lo=lo[i], bucket_hi=hi[i], bucket_mid=mid[i],
                         prior_share_pct=round(sh[i] * 100, 1), revenue_yoy_pct=round(rev[i] * 100, 2),
                         adr_yoy_reported_pct=round(adr[i] * 100, 1), take_rate_yoy_pct=round(take_yoy * 100, 2),
                         fx_wedge_pp=round(wedge * 100, 2), revenue_implied_nights_yoy_pct=round(implied[i], 2),
                         picked_nights_yoy_pct=round(pick[i], 2), position_in_bucket=pos,
                         midpoint_sum_residual_pp=round(sh @ mid - total, 2),
                         picked_sum_residual_pp=round(sh @ pick - total, 2), total_nights_yoy_pct=total))
with open(OD("27_regional_bucket_check.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ---------- Part B: carry the bucket half-width through the forecast ----------
G = {"3Q26": (7.0, 8.0, 18.0, 17.0), "4Q26": (7.0, 7.0, 18.0, 17.0)}  # WS10 base (13_driver_model REGIONAL_G)
G27 = (6.0, 7.0, 16.0, 15.0)
DRAG = {2026: (0.03, 0.36, 0, 0), 2027: (0.05, 0.71, 0, 0)}
HALF = np.array([(f(panel["2Q26"][f"{r}_nights_yoy_hi"]) - f(panel["2Q26"][f"{r}_nights_yoy_lo"])) / 2 for r in REG])

def nights(q):  # actual regional nights, M
    return f(kpi[q]["nights_m"]) * np.array([f(panel[q][f"{r}_nights_share_est_pct"]) for r in REG]) / 100

def path(shift):  # shift in pp applied to every region's forward growth
    out = {}
    for q in ["3Q26", "4Q26"]:
        g = (np.array(G[q]) + shift - np.array(DRAG[2026])) / 100
        out[q] = nights(prev(q)) * (1 + g)
    base26 = {"1Q26": nights("1Q26"), "2Q26": nights("2Q26"), "3Q26": out["3Q26"], "4Q26": out["4Q26"]}
    g27 = (np.array(G27) + shift - np.array(DRAG[2027])) / 100
    for q in ["1Q27", "2Q27", "3Q27", "4Q27"]:
        out[q] = base26[q[0] + "Q26"] * (1 + g27)
    fy26 = sum(base26.values()); fy27 = sum(out[q] for q in ["1Q27", "2Q27", "3Q27", "4Q27"])
    fy25 = f(kpi["1Q25"]["nights_m"]) + f(kpi["2Q25"]["nights_m"]) + f(kpi["3Q25"]["nights_m"]) + f(kpi["4Q25"]["nights_m"])
    return {"3Q26": out["3Q26"].sum(), "4Q26": out["4Q26"].sum(), "FY26": fy26.sum(), "FY27": fy27.sum(),
            "3Q26_yoy": out["3Q26"].sum() / f(kpi["3Q25"]["nights_m"]) * 100 - 100,
            "4Q26_yoy": out["4Q26"].sum() / f(kpi["4Q25"]["nights_m"]) * 100 - 100,
            "FY26_yoy": fy26.sum() / fy25 * 100 - 100, "FY27_yoy": fy27.sum() / fy26.sum() * 100 - 100}

band = []
for label, shift in [("bucket_low", -HALF), ("base", 0 * HALF), ("bucket_high", +HALF)]:
    p = path(shift)
    band.append(dict(case=label, shift_pp_na=shift[0], shift_pp_emea=shift[1], shift_pp_latam=shift[2], shift_pp_apac=shift[3],
                     **{k: round(v, 2) for k, v in p.items()}))
with open(OD("27_nights_band.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(band[0])); w.writeheader(); w.writerows(band)

for r in rows:
    print(f"{r['quarter']} {r['region']:5s} bucket {r['bucket_lo']:5.1f}-{r['bucket_hi']:5.1f} implied {r['revenue_implied_nights_yoy_pct']:6.2f} pick {r['picked_nights_yoy_pct']:6.2f} {r['position_in_bucket']:6s} resid mid {r['midpoint_sum_residual_pp']:5.2f} pick {r['picked_sum_residual_pp']:5.2f}")
for b in band:
    print(b["case"], {k: b[k] for k in ["3Q26_yoy", "4Q26_yoy", "FY26_yoy", "FY27_yoy", "FY27"]})
