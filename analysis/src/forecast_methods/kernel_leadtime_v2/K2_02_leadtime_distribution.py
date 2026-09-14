"""
K2 step 2 -- lead-time distribution, corrected for the vendor's booked-date capture rule.

THE CENSORING RULE (recovered from the data, not assumed).  Booked Date is not missing at
random.  Comparing the modelled and the observed maximum lead month by month shows the
vendor captured a reservation's booking date if and only if

    booked_date >= 2016-02-05           (full ~365-day forward calendar from this date)
 OR (booked_date >= 2015-09-01 AND lead <= 180)   (earlier regime: only ~180 days forward)

so the largest lead observable for a stay on date d is
    W(d) = max( d - 2016-02-05 , min(180, d - 2015-09-01) ).
Modelled W(d) reproduces the observed maximum lead in every stay month to within a day or
two (208/238/269/299/330/359 for Aug-16..Jan-17), and only 0.25% of reservations violate it.

Consequence: lead time is RIGHT-TRUNCATED at W(d), and W(d) sits at 180 days for every stay
month from Feb-16 to Jul-16.  Those months therefore cannot see the long tail at all.  Only
stays from Nov-16 (W>=299) observe the distribution out past three quarters.  We correct with
the Lynden-Bell / Efron-Petrosian NPMLE and inverse-probability weights w = 1/F(W).
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = os.environ.get("CITADEL_ABNB_PARENT", str(Path(__file__).resolve().parents[5]))  # parent of the repo folder (holds "Theo Data"); portable
OUT = os.path.join(ROOT, "Citadel-ABNB/data/processed/forecast_methods/kernel_leadtime_v2")
A0, B0 = pd.Timestamp("2015-09-01"), pd.Timestamp("2016-02-05")
WIN_LO, WIN_HI = pd.Timestamp("2016-03-01"), pd.Timestamp("2017-02-28")   # exactly 12 months

df = pd.read_parquet(os.path.join(OUT, "K2_reservations.parquet"))
for c in ["check_in", "booked_date", "last_night"]:
    df[c] = pd.to_datetime(df[c])
df["lead_days"] = df["lead_days"].astype(int)
df["W"] = np.maximum((df.check_in - B0).dt.days, np.minimum(180, (df.check_in - A0).dt.days))

viol = (df.lead_days > df.W).sum()
print(f"loaded {len(df):,}; censoring-rule violations dropped: {viol:,} ({100*viol/len(df):.3f}%)")
df = df[df.lead_days <= df.W].copy()

df = df[(df.check_in >= WIN_LO) & (df.check_in <= WIN_HI)].copy()
print(f"12-month analysis window {WIN_LO.date()}..{WIN_HI.date()}: n={len(df):,}, W {df.W.min()}-{df.W.max()}")

def lynden_bell_cdf(T, W):
    """NPMLE of F(t)=P(T<=t) under right truncation T<=W (Lynden-Bell / Efron-Petrosian)."""
    T = np.asarray(T, np.int64); W = np.asarray(W, np.int64)
    grid = np.unique(T); Ts = np.sort(T); Ws = np.sort(W)
    d = np.searchsorted(Ts, grid, "right") - np.searchsorted(Ts, grid, "left")
    n = np.searchsorted(Ts, grid, "right") - np.searchsorted(Ws, grid, "left")
    n = np.maximum(n, d)
    ratio = 1.0 - np.divide(d, n, out=np.zeros_like(d, float), where=n > 0)
    P = np.cumprod(ratio[::-1])[::-1]                  # P[j] = prod_{i>=j} ratio[i]
    F = np.concatenate([P[1:], [1.0]])                 # F(grid[j]) = prod_{i>j} ratio[i]
    return grid, np.clip(F, 1e-9, 1.0)

grid, F = lynden_bell_cdf(df.lead_days.values, df.W.values)
df["p_incl"] = np.interp(df.W.values, grid, F, left=0, right=1)
df["w"] = 1.0 / df.p_incl
print(f"inclusion prob {df.p_incl.min():.3f}-{df.p_incl.max():.3f}; weights {df.w.min():.3f}-{df.w.max():.3f}")

adr_hi = df.adr.quantile(0.995)
df["adr_w"] = df.adr.clip(upper=adr_hi)
df["value_w"] = df.adr_w * df.nights
df["w_count"] = df.w
df["w_nights"] = df.w * df.nights
df["w_value"] = df.w * df.value_w
qidx = lambda d: d.dt.year * 4 + (d.dt.quarter - 1)
df["k"] = qidx(df.check_in) - qidx(df.booked_date)
df["k_cap"] = df.k.clip(upper=3)
df.to_parquet(os.path.join(OUT, "K2_reservations_weighted.parquet"), index=False)

print(f"\nADR winsorised at p99.5={adr_hi:,.0f}; mean booking value {df.value_w.mean():,.0f} (AUD, unverified)")
print("\n=== effect of the truncation correction (pooled, 12-month window) ===")
for nm, wt in [("naive (uncorrected)", None), ("IPW-corrected", df.w.values)]:
    ld = df.lead_days.values
    mu = ld.mean() if wt is None else np.average(ld, weights=wt)
    p90 = (ld <= 90).mean() if wt is None else np.average(ld <= 90, weights=wt)
    p180 = (ld <= 180).mean() if wt is None else np.average(ld <= 180, weights=wt)
    print(f"  {nm:<22} mean lead={mu:6.2f}  P(<=90)={100*p90:5.2f}%  P(<=180)={100*p180:5.2f}%")
clean = df[df.W >= 299]
print(f"  {'stays with W>=299':<22} mean lead={clean.lead_days.mean():6.2f}  "
      f"P(<=90)={100*(clean.lead_days<=90).mean():5.2f}%  P(<=180)={100*(clean.lead_days<=180).mean():5.2f}%  "
      f"(n={len(clean):,}, Nov16-Feb17 only)")

# CDF table, IPW-corrected, by Melbourne stay quarter
HZ = [0, 1, 3, 7, 14, 21, 30, 45, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 365]
rows = []
for lab, sub in [("ALL", df)] + [(f"Q{q}", df[df.check_in.dt.quarter == q]) for q in [1, 2, 3, 4]]:
    g, Fq = lynden_bell_cdf(sub.lead_days.values, sub.W.values)
    for h in HZ:
        rows.append({"stay_quarter_melbourne": lab, "horizon_days": h,
                     "cdf_share_booked_within": float(np.interp(h, g, Fq, left=0, right=1)),
                     "n_reservations": len(sub), "max_W_in_group": int(sub.W.max())})
cdf_tab = pd.DataFrame(rows)
cdf_tab.to_csv(os.path.join(OUT, "K2_leadtime_cdf_by_season.csv"), index=False)
print("\n=== lead-time CDF (share of bookings made within H days of check-in), IPW-corrected ===")
print(cdf_tab.pivot(index="horizon_days", columns="stay_quarter_melbourne",
                    values="cdf_share_booked_within").round(3).to_string())

# stay length
ln = []
for lab, lo, hi in [("1-2 nights", 1, 2), ("3-6", 3, 6), ("7-13", 7, 13), ("14-27", 14, 27),
                    ("28+ (long-term)", 28, 10**6)]:
    s = df[(df.nights >= lo) & (df.nights <= hi)]
    ln.append({"stay_length": lab, "n": len(s),
               "share_of_reservations": s.w_count.sum()/df.w_count.sum(),
               "share_of_nights": s.w_nights.sum()/df.w_nights.sum(),
               "share_of_value": s.w_value.sum()/df.w_value.sum(),
               "mean_lead_days": np.average(s.lead_days, weights=s.w),
               "median_lead_days": s.lead_days.median(),
               "value_wtd_mean_lead": np.average(s.lead_days, weights=s.w_value),
               "mean_nights": np.average(s.nights, weights=s.w),
               "pct_value_lead_gt_180": 100*s.loc[s.lead_days > 180, "w_value"].sum()/s.w_value.sum()})
ln = pd.DataFrame(ln)
ln.to_csv(os.path.join(OUT, "K2_leadtime_by_stay_length.csv"), index=False)
print("\n=== lead time by stay length ===")
print(ln.round(3).to_string(index=False))

mo = []
for m in range(1, 13):
    s = df[df.check_in.dt.month == m]
    mo.append({"melbourne_stay_month": m, "n": len(s), "W_for_month": int(s.W.max()),
               "mean_lead_days": np.average(s.lead_days, weights=s.w),
               "median_lead_days": s.lead_days.median(),
               "value_wtd_mean_lead": np.average(s.lead_days, weights=s.w_value),
               "share_value_lead_gt_180": s.loc[s.lead_days > 180, "w_value"].sum()/s.w_value.sum()})
mo = pd.DataFrame(mo)
mo.to_csv(os.path.join(OUT, "K2_leadtime_by_stay_month.csv"), index=False)
print("\n=== by stay month (Melbourne calendar; note W varies -- tail only visible Nov-Feb) ===")
print(mo.round(3).to_string(index=False))
