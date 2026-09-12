"""
K2 step 4 -- the recognition kernel: phi_k, the M matrix, survival, and scenarios.

phi_k = share of a stay quarter's REVENUE that was booked k quarters earlier.
Revenue is recognised at check-in, so a stay quarter's revenue is exactly the realised
stays of that quarter; grouping them by the quarter in which they were booked gives phi.

Built by integrating a per-stay-month lead-time CDF over the days of the quarter, rather
than by counting booking-quarter labels, so that every quarter is treated identically
despite the vendor's capture window W(d) differing by stay month (see K2_02/K2_03).

Per stay month m the CDF is empirical up to A(m)=min(W(m),180) and, above that, carries the
conditional tail P(T>x | T>A) of the reference panel (stays Dec-16..Feb-17, W>=300).  We
report the no-tail variant alongside as the lower bound, because the reference months are
Melbourne's peak summer and so probably have a FATTER tail than the off-peak months.

SEASON.  The panel is Melbourne: southern hemisphere.  Peak leisure demand is Dec-Jan, the
role northern Jul-Aug plays for Airbnb.  We therefore also report a season-role remap that
shifts the calendar six months (Melbourne month m -> northern ((m+5) mod 12)+1), which maps
whole quarters onto whole quarters and preserves position-within-quarter.
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = os.environ.get("CITADEL_ABNB_PARENT", str(Path(__file__).resolve().parents[5]))  # parent of the repo folder (holds "Theo Data"); portable
OUT = os.path.join(ROOT, "Citadel-ABNB/data/processed/forecast_methods/kernel_leadtime_v2")
MAXL = 460
MLEN = {1: 31, 2: 28.25, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
QPREV = 91.0

df = pd.read_parquet(os.path.join(OUT, "K2_reservations_weighted.parquet"))
ref = df[df.W >= 300]
print(f"window n={len(df):,}; reference panel (W>=300) n={len(ref):,}")

def wcdf(lead, wt):
    h = np.bincount(np.clip(np.asarray(lead), 0, MAXL), weights=np.asarray(wt), minlength=MAXL + 1)
    c = np.cumsum(h)
    return c / c[-1]

def month_cdf(m, wcol, splice=True):
    """Full lead-time CDF for stay month m.

    The month's own data are truncated at A, its largest observed lead, so what we see
    empirically is F_obs(x) = F(x)/F(A).  We undo
    that by rescaling to the reference panel's F(A), then take the tail above A from the
    reference panel outright:
        F(x) = F_obs(x) * R(A)   for x <= A
        F(x) = R(x)              for x >  A
    which is continuous at A.  splice=False leaves the truncated CDF alone and is reported
    as the lower bound on the far-lead buckets.
    """
    sub = df[df.check_in.dt.month == m]
    A = int(sub.lead_days.max())
    F = np.maximum.accumulate(np.clip(wcdf(sub.lead_days.values, sub[wcol].values), 0, 1))
    if not splice:
        return F / F[-1]
    R = np.maximum.accumulate(np.clip(wcdf(ref.lead_days.values, ref[wcol].values), 0, 1))
    R = R / R[-1]
    G = F * R[A]
    G[A:] = R[A:]
    G = np.maximum.accumulate(np.clip(G, 0, 1))
    return G / G[-1]

def quarter_phi(months, wcol, splice=True, stretch=1.0):
    """integrate the monthly CDFs over the days of the quarter; stretch scales lead times"""
    num, den = np.zeros(4), 0.0
    for mi, m in enumerate(months):
        sub = df[df.check_in.dt.month == m]
        F = month_cdf(m, wcol, splice)
        if stretch != 1.0:                            # lengthen every lead by `stretch`
            x = np.arange(MAXL + 1)
            F = np.interp(x, x * stretch, F, left=0.0, right=1.0)
        off = sum(MLEN[mm] for mm in months[:mi])
        for day, wt in sub.groupby(sub.check_in.dt.day)[wcol].sum().items():
            a = int(round(off + day - 1))
            b1, b2 = a + int(QPREV), a + 2 * int(QPREV)
            f0 = F[min(a, MAXL)]
            num += wt * np.array([f0, F[min(b1, MAXL)] - f0,
                                  F[min(b2, MAXL)] - F[min(b1, MAXL)], 1.0 - F[min(b2, MAXL)]])
            den += wt
    return num / den

MELB_Q = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
NORTH = {3: [1, 2, 3], 4: [4, 5, 6], 1: [7, 8, 9], 2: [10, 11, 12]}   # season-role remap

rows = []
for basis, mp in [("melbourne_calendar", MELB_Q), ("northern_season_role", NORTH)]:
    for q, months in mp.items():
        n = int(sum(len(df[df.check_in.dt.month == m]) for m in months))
        rec = {"basis": basis, "stay_quarter": f"Q{q}",
               "melbourne_months": "-".join(map(str, months)), "n_reservations": n}
        for wname, wcol in [("count", "w_count"), ("nights", "w_nights"), ("value", "w_value")]:
            p = quarter_phi(months, wcol)
            for k in range(4):
                rec[f"phi{k}_{wname}"] = p[k]
            rec[f"booked_before_quarter_{wname}"] = p[1:].sum()
        pl = quarter_phi(months, "w_value", splice=False)
        rec["phi0_value_notail_lo"] = pl[0]
        rec["phi2plus_value_notail_lo"] = pl[2:].sum()
        rows.append(rec)
phi = pd.DataFrame(rows)
phi.to_csv(os.path.join(OUT, "K2_phi_kernel_analytic.csv"), index=False)
pd.set_option("display.width", 260)
print("\n=== phi_k : share of a stay quarter's revenue booked k quarters earlier ===")
print(phi[["basis", "stay_quarter", "melbourne_months", "n_reservations",
           "phi0_count", "phi1_count", "phi2_count", "phi3_count",
           "phi0_value", "phi1_value", "phi2_value", "phi3_value",
           "booked_before_quarter_value", "phi0_value_notail_lo"]].round(4).to_string(index=False))

q4 = df[df.check_in.dt.quarter == 4]
emp = [q4.loc[q4.k_cap == k, "w_value"].sum() / q4.w_value.sum() for k in range(4)]
ana = phi[(phi.basis == "melbourne_calendar") & (phi.stay_quarter == "Q4")][
    [f"phi{k}_value" for k in range(4)]].values[0]
print(f"\ncross-check Q4-2016 (labels exact there): labels={[f'{v:.4f}' for v in emp]}  "
      f"analytic={[f'{v:.4f}' for v in ana]}  maxdiff={np.abs(np.array(emp)-ana).max():.4f}")

# ------------------------------------------------------------------ (C) SURVIVAL
# STR records only stays that actually happened, so the phi above is ALREADY net of
# cancellation -- it is the survival-adjusted revenue weight. The GROSS booking share that
# GBV records is obtained by grossing UP by 1/s(lead). Three calibrations of s, all pinned
# to Airbnb's ~16% platform cancellation rate (Mertz, 4Q25 call).
def survival(L, mode):
    L = np.asarray(L, float)
    if mode == "flat":                      # no lead dependence
        return np.full_like(L, 0.84)
    if mode == "moderate":                  # immediate 4% + 3.6%/30d exposure hazard
        return (1 - 0.04) * np.exp(-L / 30.0 * 0.0366)
    if mode == "strong":                    # Krish's artifact-stripped reopen hazard ~6%/30d
        return (1 - 0.03) * np.exp(-L / 30.0 * 0.0619)
    raise ValueError(mode)

srows = []
for mode in ["flat", "moderate", "strong"]:
    s = survival(df.lead_days.values, mode)
    implied = 1 - np.average(s, weights=df.w_value)          # value-weighted cancel rate
    gross_w = df.w_value.values / s                          # gross-up to booking time
    for basis, mp in [("northern_season_role", NORTH)]:
        for q, months in mp.items():
            sel = df.check_in.dt.month.isin(months).values
            g = gross_w[sel]
            d2 = df[sel]
            tot = g.sum()
            rec = {"survival_model": mode, "implied_cancel_rate": implied,
                   "stay_quarter_northern": f"Q{q}"}
            for k in range(4):
                rec[f"g{k}_booking_share"] = g[(d2.k_cap == k).values].sum() / tot
            p = phi[(phi.basis == basis) & (phi.stay_quarter == f"Q{q}")]
            for k in range(4):
                rec[f"phi{k}_revenue_weight"] = p[f"phi{k}_value"].values[0]
            srows.append(rec)
surv = pd.DataFrame(srows)
surv.to_csv(os.path.join(OUT, "K2_survival_adjustment.csv"), index=False)
print("\n=== (C) gross BOOKING share of GBV vs survival-adjusted REVENUE weight ===")
print("    (STR sees realised stays only, so phi is already net of cancellation;")
print("     g_k is what the same cohort looked like at the moment of booking)")
print(surv.round(4).to_string(index=False))

# ------------------------------------------------------- (D) M matrix, booking -> recognition
mrows = []
for q, months in NORTH.items():
    p = quarter_phi(months, "w_value")
    mrows.append({"northern_stay_quarter": f"Q{q}", **{f"from_GBV_q-{k}": p[k] for k in range(4)}})
M = pd.DataFrame(mrows)
M.to_csv(os.path.join(OUT, "K2_M_matrix.csv"), index=False)
print("\n=== (D) revenue_q = sum_k phi_k * GBV_(q-k), northern season role ===")
print(M.round(4).to_string(index=False))

# ------------------------------------------------------------- (E) +10% lead lengthening
erows = []
for stretch, lab in [(1.0, "base"), (1.10, "+10% lead times"), (0.90, "-10% lead times")]:
    for q, months in NORTH.items():
        p = quarter_phi(months, "w_value", stretch=stretch)
        erows.append({"scenario": lab, "stay_quarter_northern": f"Q{q}",
                      **{f"phi{k}": p[k] for k in range(4)},
                      "booked_before_quarter": p[1:].sum()})
sc = pd.DataFrame(erows)
sc.to_csv(os.path.join(OUT, "K2_scenarios_leadtime_shift.csv"), index=False)
print("\n=== (E) sensitivity to a 10% lengthening / shortening of lead times ===")
print(sc.round(4).to_string(index=False))
piv = sc.pivot(index="stay_quarter_northern", columns="scenario", values="phi0")
print("\nphi0 (in-quarter share) response:")
print(piv.round(4).to_string())
print("\n  d(phi0) per +10% lead time:")
print((piv["+10% lead times"] - piv["base"]).round(4).to_string())
