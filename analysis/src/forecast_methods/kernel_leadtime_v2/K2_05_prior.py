"""
K2 step 5 -- the recommended seasonal prior, with honest bands.

WHAT IS AND IS NOT IDENTIFIED.  For a stay day at offset a in its quarter,
    phi0        = F(a)              a  <=  91
    phi0+phi1   = F(a+91)           a+91 <= 182
    phi2+phi3   = 1 - F(a+91)
Every stay month in the window observes leads out to at least 174-180 days, so phi0, phi1
and the COMBINED phi2+phi3 are identified for all four quarters up to one rescaling constant
F(A) -- the probability a booking's lead is under that month's maximum observed lead.
Splitting phi2 from phi3 needs F out to ~273 days, which only Melbourne Oct-Feb stays see.

So we bracket:
  UPPER tail bound: F(A) taken from the reference panel (Melb Dec-Feb, the peak-summer months,
                    which have the FATTEST tail in the sample) -> most weight on phi2/phi3.
  LOWER tail bound: no tail at all beyond A (F(A)=1)          -> least weight on phi2/phi3.
  CENTRAL: midpoint. On Melbourne Q4-2016, the one quarter whose own window identifies every
  bucket exactly, the central estimate is compared with the exact label count below.
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = os.environ.get("CITADEL_ABNB_PARENT", str(Path(__file__).resolve().parents[5]))  # parent of the repo folder (holds "Theo Data"); portable
OUT = os.path.join(ROOT, "Citadel-ABNB/data/processed/forecast_methods/kernel_leadtime_v2")
MAXL = 460
MLEN = {1: 31, 2: 28.25, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

df = pd.read_parquet(os.path.join(OUT, "K2_reservations_weighted.parquet"))
ref = df[df.W >= 300].copy()

def wcdf(lead, wt):
    h = np.bincount(np.clip(np.asarray(lead), 0, MAXL), weights=np.asarray(wt), minlength=MAXL + 1)
    return np.cumsum(h) / np.cumsum(h)[-1]

R = {}
for wcol in ["w_count", "w_nights", "w_value"]:
    r = np.maximum.accumulate(np.clip(wcdf(ref.lead_days.values, ref[wcol].values), 0, 1))
    R[wcol] = r / r[-1]

def month_cdf(m, wcol, bound):
    sub = df[df.check_in.dt.month == m]
    A = int(sub.lead_days.max())
    F = np.maximum.accumulate(np.clip(wcdf(sub.lead_days.values, sub[wcol].values), 0, 1))
    F = F / F[-1]
    if bound == "lower":
        return F
    if wcol not in R:                       # build the reference CDF for this weighting lazily
        r = np.maximum.accumulate(np.clip(wcdf(ref[wcol].index.map(lambda i: df.lead_days.loc[i]).values
                                               if False else ref.lead_days.values,
                                               ref[wcol].values), 0, 1))
        R[wcol] = r / r[-1]
    G = F * R[wcol][A]
    G[A:] = R[wcol][A:]
    G = np.maximum.accumulate(np.clip(G, 0, 1))
    return G / G[-1]

def quarter_phi(months, wcol, bound, stretch=1.0):
    num, den = np.zeros(4), 0.0
    for mi, m in enumerate(months):
        sub = df[df.check_in.dt.month == m]
        F = month_cdf(m, wcol, bound)
        if stretch != 1.0:
            x = np.arange(MAXL + 1)
            F = np.interp(x, x * stretch, F, left=0.0, right=1.0)
        off = sum(MLEN[mm] for mm in months[:mi])
        for day, wt in sub.groupby(sub.check_in.dt.day)[wcol].sum().items():
            a = int(round(off + day - 1)); b1, b2 = a + 91, a + 182
            f0 = F[min(a, MAXL)]
            num += wt * np.array([f0, F[min(b1, MAXL)] - f0,
                                  F[min(b2, MAXL)] - F[min(b1, MAXL)], 1 - F[min(b2, MAXL)]])
            den += wt
    return num / den

NORTH = {3: [1, 2, 3], 4: [4, 5, 6], 1: [7, 8, 9], 2: [10, 11, 12]}
ROLE = {3: "peak summer", 4: "autumn shoulder + holidays", 1: "winter trough", 2: "spring shoulder"}

# measure the anchor error first (Melbourne Q4-2016 = northern Q2, exactly identified)
_q4 = df[df.check_in.dt.quarter == 4]
_exact = np.array([_q4.loc[_q4.k_cap == k, "w_value"].sum() / _q4.w_value.sum() for k in range(4)])
_cen = 0.5*(quarter_phi([10, 11, 12], "w_value", "lower") + quarter_phi([10, 11, 12], "w_value", "upper"))
ANCHOR_ERR = float(np.abs(_exact - _cen).max())
print(f"anchor error on the one exactly-identified quarter: {ANCHOR_ERR:.4f} "
      f"(bands are widened by this)\n")

rows = []
for q, months in NORTH.items():
    for wname, wcol in [("count", "w_count"), ("nights", "w_nights"), ("value", "w_value")]:
        lo, hi = quarter_phi(months, wcol, "lower"), quarter_phi(months, wcol, "upper")
        mid = 0.5 * (lo + hi)
        rec = {"northern_stay_quarter": f"Q{q}", "seasonal_role": ROLE[q],
               "melbourne_months": "-".join(map(str, months)), "weighting": wname,
               "n_reservations": int(sum(len(df[df.check_in.dt.month == m]) for m in months))}
        # ANCHOR_ERR: the largest error the central method makes on Melbourne Q4-2016, the one
        # quarter whose own observation window identifies every bucket exactly (see below).
        # The tail-import bracket alone is too tight to contain it, so we widen by it.
        for k in range(4):
            rec[f"phi{k}"] = mid[k]
            rec[f"phi{k}_lo"] = max(0.0, min(lo[k], hi[k]) - ANCHOR_ERR)
            rec[f"phi{k}_hi"] = min(1.0, max(lo[k], hi[k]) + ANCHOR_ERR)
        rec["booked_before_quarter"] = mid[1:].sum()
        rec["booked_before_quarter_lo"] = min(lo[1:].sum(), hi[1:].sum()) - ANCHOR_ERR
        rec["booked_before_quarter_hi"] = max(lo[1:].sum(), hi[1:].sum()) + ANCHOR_ERR
        rows.append(rec)
prior = pd.DataFrame(rows)
prior.to_csv(os.path.join(OUT, "K2_recommended_prior.csv"), index=False)
pd.set_option("display.width", 260)

print("=== RECOMMENDED SEASONAL PRIOR (central, with tail band) -- VALUE-WEIGHTED ===")
v = prior[prior.weighting == "value"]
for _, r in v.iterrows():
    print(f"  {r.northern_stay_quarter} ({r.seasonal_role:<26}) "
          f"phi0={r.phi0:.3f} [{r.phi0_lo:.3f}-{r.phi0_hi:.3f}]  phi1={r.phi1:.3f}  "
          f"phi2={r.phi2:.3f} [{r.phi2_lo:.3f}-{r.phi2_hi:.3f}]  phi3={r.phi3:.3f}  "
          f"| before-quarter {r.booked_before_quarter:.3f} [{r.booked_before_quarter_lo:.3f}-{r.booked_before_quarter_hi:.3f}]")

print("\n=== all three weightings, central ===")
print(prior[["northern_stay_quarter", "seasonal_role", "weighting", "n_reservations",
             "phi0", "phi1", "phi2", "phi3", "booked_before_quarter"]].round(4).to_string(index=False))

# anchor: Melbourne Q4-2016 = northern Q2, exactly identified by labels
q4 = df[df.check_in.dt.quarter == 4]
exact = np.array([q4.loc[q4.k_cap == k, "w_value"].sum() / q4.w_value.sum() for k in range(4)])
c = v[v.northern_stay_quarter == "Q2"][[f"phi{k}" for k in range(4)]].values[0]
lo = v[v.northern_stay_quarter == "Q2"][[f"phi{k}_lo" for k in range(4)]].values[0]
hi = v[v.northern_stay_quarter == "Q2"][[f"phi{k}_hi" for k in range(4)]].values[0]
print("\n=== ANCHOR: Melbourne Q4-2016 (northern Q2) -- its own window identifies every bucket ===")
print(f"  exact label count : {[f'{x:.4f}' for x in exact]}")
print(f"  central estimate  : {[f'{x:.4f}' for x in c]}   max abs err {np.abs(exact-c).max():.4f}")
print(f"  band              : {[f'[{a:.3f},{b:.3f}]' for a, b in zip(lo, hi)]}")
print(f"  exact inside band : {all(lo[k]-1e-9 <= exact[k] <= hi[k]+1e-9 for k in range(4))}")

# lead-time sensitivity on the central prior
sc = []
for st, lab in [(1.0, "base"), (1.10, "+10%"), (0.90, "-10%")]:
    for q, months in NORTH.items():
        p = 0.5*(quarter_phi(months, "w_value", "lower", st) + quarter_phi(months, "w_value", "upper", st))
        sc.append({"scenario": lab, "northern_stay_quarter": f"Q{q}",
                   **{f"phi{k}": p[k] for k in range(4)}, "booked_before_quarter": p[1:].sum()})
sc = pd.DataFrame(sc)
sc.to_csv(os.path.join(OUT, "K2_scenarios_leadtime_shift.csv"), index=False)
piv = sc.pivot(index="northern_stay_quarter", columns="scenario", values="phi0")
print("\n=== (E) phi0 under a 10% lengthening / shortening of lead times ===")
print(piv[["-10%", "base", "+10%"]].round(4).to_string())
print("\n  d(phi0) per +10% lead time (pp):")
print((100*(piv["+10%"] - piv["base"])).round(2).to_string())

summ = prior[prior.weighting == "value"][["northern_stay_quarter", "seasonal_role",
    "phi0", "phi1", "phi2", "phi3", "booked_before_quarter"]].copy()
summ["mean_lead_days_value_wtd"] = [
    np.average(df[df.check_in.dt.month.isin(NORTH[q])].lead_days,
               weights=df[df.check_in.dt.month.isin(NORTH[q])].w_value) for q in [3, 4, 1, 2]]
summ.to_csv(os.path.join(OUT, "K2_prior_summary_value_weighted.csv"), index=False)
print("\n=== headline table saved ===")
print(summ.round(4).to_string(index=False))

# ---------------------------------------------------------------- (C) SURVIVAL
# STR records only stays that HAPPENED, so phi above is already net of cancellation: it is
# the revenue weight. The gross BOOKING distribution that GBV records is recovered by
# grossing each reservation up by 1/s(lead) and re-running the SAME analytic integration,
# so the two columns are produced by one method and are directly comparable.
def survival(L, mode):
    L = np.asarray(L, float)
    if mode == "flat":     return np.full_like(L, 0.84)          # no lead dependence
    if mode == "moderate": return (1 - 0.04) * np.exp(-L / 30.0 * 0.0366)   # 4% + 3.7%/30d
    if mode == "strong":   return (1 - 0.03) * np.exp(-L / 30.0 * 0.0619)   # Krish clean reopen
    raise ValueError(mode)

srows = []
for mode in ["flat", "moderate", "strong"]:
    sv = survival(df.lead_days.values, mode)
    df["w_gross"] = df.w_value.values / sv
    ref["w_gross"] = ref.w_value.values / survival(ref.lead_days.values, mode)
    R.pop("w_gross", None)                  # refresh the reference tail for this survival model
    implied = 1 - np.average(sv, weights=df.w_value)
    for q, months in NORTH.items():
        g = 0.5*(quarter_phi(months, "w_gross", "lower") + quarter_phi(months, "w_gross", "upper"))
        r = 0.5*(quarter_phi(months, "w_value", "lower") + quarter_phi(months, "w_value", "upper"))
        rec = {"survival_model": mode, "implied_cancel_rate_value_wtd": implied,
               "northern_stay_quarter": f"Q{q}"}
        for k in range(4):
            rec[f"g{k}_gbv_booking_share"] = g[k]
            rec[f"phi{k}_revenue_weight"] = r[k]
            rec[f"gap_k{k}_pp"] = 100*(r[k] - g[k])
        rec["g2plus_booking"] = g[2:].sum(); rec["phi2plus_revenue"] = r[2:].sum()
        srows.append(rec)
surv = pd.DataFrame(srows)
surv.to_csv(os.path.join(OUT, "K2_survival_adjustment.csv"), index=False)
print("\n=== (C) GBV booking share g_k  vs  survival-adjusted revenue weight phi_k (value) ===")
print("    phi < g at high k means: the revenue actually recognised from GBV booked two")
print("    quarters earlier is LESS than that GBV's share of the cohort, because long-lead")
print("    bookings are likelier to cancel before check-in.")
print(surv[["survival_model", "implied_cancel_rate_value_wtd", "northern_stay_quarter",
            "g0_gbv_booking_share", "phi0_revenue_weight", "g2plus_booking",
            "phi2plus_revenue"]].round(4).to_string(index=False))

# ---------------------------------------------- (D) M matrix, booking -> recognition quarter
M = []
for q, months in NORTH.items():
    r = 0.5*(quarter_phi(months, "w_value", "lower") + quarter_phi(months, "w_value", "upper"))
    M.append({"northern_stay_quarter": f"Q{q}", **{f"weight_on_GBV_q-{k}": r[k] for k in range(4)}})
pd.DataFrame(M).to_csv(os.path.join(OUT, "K2_M_matrix.csv"), index=False)
print("\n=== (D) revenue_q = sum_k phi_k * GBV_(q-k) ===")
print(pd.DataFrame(M).round(4).to_string(index=False))
