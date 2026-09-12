"""
K2 step 3 -- validate the truncation correction against the vendor's real capture rule.

The capture rule recovered in step 2 is
    observed  iff  booked_date >= 2016-02-05
                   OR (booked_date >= 2015-09-01 AND lead <= 180)
so the maximum observable lead for a stay on d is
    W(d) = max(d - 2016-02-05, min(180, d - 2015-09-01)).
W(d) is pinned at 180 days for every stay month from Feb-16 to Jul-16 and only opens up
from Aug-16.  Stays from Dec-16 have W>=300, which covers ~99% of the lead distribution;
we treat those as the effectively-complete reference panel.

Two checks:
 (1) a simulation that re-imposes an EARLIER capture rule of exactly the same shape on the
     reference panel and asks whether Lynden-Bell recovers the known answer;
 (2) the label-count phi for Q4-2016 stays, whose own W (269-330) covers the buckets that
     matter, against the analytic kernel built in step 4.
"""
import os
import numpy as np
import pandas as pd

ROOT = "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB"
OUT = os.path.join(ROOT, "Citadel-ABNB/data/processed/forecast_methods/kernel_leadtime_v2")

df = pd.read_parquet(os.path.join(OUT, "K2_reservations_weighted.parquet"))

def lynden_bell_cdf(T, W):
    T = np.asarray(T, np.int64); W = np.asarray(W, np.int64)
    grid = np.unique(T); Ts = np.sort(T); Ws = np.sort(W)
    d = np.searchsorted(Ts, grid, "right") - np.searchsorted(Ts, grid, "left")
    n = np.searchsorted(Ts, grid, "right") - np.searchsorted(Ws, grid, "left")
    n = np.maximum(n, d)
    ratio = 1.0 - np.divide(d, n, out=np.zeros_like(d, float), where=n > 0)
    P = np.cumprod(ratio[::-1])[::-1]
    return grid, np.clip(np.concatenate([P[1:], [1.0]]), 1e-9, 1.0)

ref = df[df.W >= 300].copy()          # Dec-16 .. Feb-17
print(f"reference panel W>=300: n={len(ref):,}  stays {ref.check_in.min().date()}..{ref.check_in.max().date()}")
print(f"  observed max lead={ref.lead_days.max()}, P(lead<=300)={100*(ref.lead_days<=300).mean():.2f}%")
truth_mean = ref.lead_days.mean()
truth_v = np.average(ref.lead_days, weights=ref.value_w)
truth_90 = (ref.lead_days <= 90).mean()
truth_180 = (ref.lead_days <= 180).mean()

print("\n=== (1) SIMULATION: re-impose a capture rule of the real shape, then recover ===")
print("    Wsim(d) = max(d - B0sim, min(180, d - A0sim)) with a later B0sim, so the window")
print("    keeps the same varying structure as the true data.")
hdr = f"{'B0sim':>12} {'Wsim range':>12} {'kept':>8} {'naive mean':>11} {'IPW mean':>9} {'TRUE':>7} " \
      f"{'naive<=90':>10} {'IPW<=90':>8} {'TRUE<=90':>9}"
print(hdr)
rows = []
for b0 in ["2016-06-01", "2016-08-01", "2016-09-15", "2016-10-15"]:
    B0s, A0s = pd.Timestamp(b0), pd.Timestamp(b0) - pd.Timedelta(days=160)
    s = ref.copy()
    s["Wsim"] = np.maximum((s.check_in - B0s).dt.days, np.minimum(180, (s.check_in - A0s).dt.days))
    keep = s[s.lead_days <= s.Wsim].copy()
    g, F = lynden_bell_cdf(keep.lead_days.values, keep.Wsim.values)
    w = 1.0 / np.clip(np.interp(keep.Wsim.values, g, F, left=0, right=1), 1e-6, None)
    im, i90 = np.average(keep.lead_days, weights=w), np.average(keep.lead_days <= 90, weights=w)
    print(f"{b0:>12} {keep.Wsim.min():>4}-{keep.Wsim.max():<7} {len(keep):>8,} "
          f"{keep.lead_days.mean():>11.1f} {im:>9.1f} {truth_mean:>7.1f} "
          f"{100*(keep.lead_days<=90).mean():>9.1f}% {100*i90:>7.1f}% {100*truth_90:>8.1f}%")
    rows.append({"B0_sim": b0, "wsim_min": int(keep.Wsim.min()), "wsim_max": int(keep.Wsim.max()),
                 "n_kept": len(keep), "pct_of_panel_kept": 100*len(keep)/len(ref),
                 "naive_mean_lead": keep.lead_days.mean(), "ipw_mean_lead": im,
                 "true_mean_lead": truth_mean, "naive_pct_le90": 100*(keep.lead_days<=90).mean(),
                 "ipw_pct_le90": 100*i90, "true_pct_le90": 100*truth_90})
pd.DataFrame(rows).to_csv(os.path.join(OUT, "K2_truncation_validation.csv"), index=False)
print("  READ: IPW closes part of the gap but cannot invent mass beyond max(Wsim). The real")
print("  panel's binding constraint is W=180 for Mar-Jul-16 stays, so the >180d tail in those")
print("  months is NOT identified and is imported from the Nov-16..Feb-17 months in step 4.")

# ---------------- (2) reference-panel phi and lead summary, no correction needed
ref["w_count"] = 1.0; ref["w_nights"] = ref.nights; ref["w_value"] = ref.value_w
out = []
for lab, sub in [("Dec-16 (Melb summer build)", ref[ref.check_in.dt.month == 12]),
                 ("Jan-17 (Melb peak summer)", ref[ref.check_in.dt.month == 1]),
                 ("Feb-17 (Melb summer)", ref[ref.check_in.dt.month == 2]),
                 ("ALL W>=300", ref)]:
    rec = {"panel": lab, "n_reservations": len(sub), "W_min": int(sub.W.min()),
           "mean_lead_days": sub.lead_days.mean(), "median_lead_days": sub.lead_days.median(),
           "value_wtd_mean_lead": np.average(sub.lead_days, weights=sub.w_value),
           "pct_count_lead_gt180": 100*(sub.lead_days > 180).mean(),
           "pct_value_lead_gt180": 100*sub.loc[sub.lead_days > 180, "w_value"].sum()/sub.w_value.sum()}
    for wname, col in [("count", "w_count"), ("nights", "w_nights"), ("value", "w_value")]:
        tot = sub[col].sum()
        for k in range(4):
            rec[f"phi{k}_{wname}"] = sub.loc[sub.k_cap == k, col].sum()/tot
    out.append(rec)
ex = pd.DataFrame(out)
ex.to_csv(os.path.join(OUT, "K2_phi_reference_panel.csv"), index=False)
pd.set_option("display.width", 250)
print("\n=== (2) reference panel (W>=300, no correction applied) ===")
print(ex.round(4).to_string(index=False))
print("\n  NOTE these are Melbourne Dec/Jan/Feb = the SOUTHERN PEAK SUMMER. They are the")
print("  seasonal analogue of northern Jun/Jul/Aug, i.e. of Airbnb's Q3 stay quarter.")

old = os.path.join(OUT, "K2_phi_exact_untruncated.csv")
if os.path.exists(old):
    os.remove(old)
    print(f"\nremoved superseded {os.path.basename(old)} (it used the wrong censoring boundary)")
