"""K2 step 6 -- lead-time CDF by season with the quarter cut lines."""
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.environ.get("CITADEL_ABNB_PARENT", str(Path(__file__).resolve().parents[5]))  # parent of the repo folder (holds "Theo Data"); portable
OUT = os.path.join(ROOT, "Citadel-ABNB/data/processed/forecast_methods/kernel_leadtime_v2")
MAXL = 460
df = pd.read_parquet(os.path.join(OUT, "K2_reservations_weighted.parquet"))
ref = df[df.W >= 300]

def wcdf(lead, wt):
    h = np.bincount(np.clip(np.asarray(lead), 0, MAXL), weights=np.asarray(wt), minlength=MAXL + 1)
    return np.cumsum(h) / np.cumsum(h)[-1]

Rv = np.maximum.accumulate(np.clip(wcdf(ref.lead_days.values, ref.w_value.values), 0, 1)); Rv /= Rv[-1]
Rc = np.maximum.accumulate(np.clip(wcdf(ref.lead_days.values, ref.w_count.values), 0, 1)); Rc /= Rc[-1]

def season_cdf(months, wcol, Rref):
    sub = df[df.check_in.dt.month.isin(months)]
    A = int(sub.lead_days.max())
    F = np.maximum.accumulate(np.clip(wcdf(sub.lead_days.values, sub[wcol].values), 0, 1)); F /= F[-1]
    G = F * Rref[A]; G[A:] = Rref[A:]
    G = np.maximum.accumulate(np.clip(G, 0, 1))
    return G / G[-1], len(sub)

NORTH = {"Q3  peak summer": [1, 2, 3], "Q4  autumn + holidays": [4, 5, 6],
         "Q1  winter trough": [7, 8, 9], "Q2  spring shoulder": [10, 11, 12]}
COL = {"Q3  peak summer": "#C0392B", "Q4  autumn + holidays": "#E67E22",
       "Q1  winter trough": "#2E86C1", "Q2  spring shoulder": "#27AE60"}

fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.9), sharey=True)
x = np.arange(MAXL + 1)
for ax, (wcol, Rref, ttl) in zip(axes, [("w_count", Rc, "Count-weighted (per booking)"),
                                        ("w_value", Rv, "Value-weighted (per booking dollar)")]):
    for lab, months in NORTH.items():
        G, n = season_cdf(months, wcol, Rref)
        A = int(df[df.check_in.dt.month.isin(months)].lead_days.max())
        ax.plot(x[:A + 1], G[:A + 1], color=COL[lab], lw=2.1, label=f"{lab}  (n={n:,})")
        ax.plot(x[A:381], G[A:381], color=COL[lab], lw=1.6, ls=":", alpha=0.85)
        ax.plot([A], [G[A]], "o", color=COL[lab], ms=4.5, mec="white", mew=0.8, zorder=5)
    for cut, txt in [(91, "1 quarter"), (182, "2 quarters"), (273, "3 quarters")]:
        ax.axvline(cut, color="0.45", ls="--", lw=1.0, zorder=0)
        ax.text(cut + 4, 0.045, txt, rotation=90, fontsize=8, color="0.35", va="bottom")
    ax.set_xlim(0, 380); ax.set_ylim(0, 1.005)
    ax.set_xlabel("lead time: days from booking to check-in")
    ax.set_title(ttl, fontsize=11)
    ax.grid(alpha=0.25, lw=0.6)
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.94, title=
              "solid = own data;  dotted = imported tail", title_fontsize=8)
axes[0].set_ylabel("cumulative share of bookings made within X days of check-in")
fig.suptitle("Airbnb booking lead time by stay season — Melbourne STR reservation panel, "
             "Mar-2016 to Feb-2017 (n=268,110 reservations)\n"
             "Southern-hemisphere months mapped to their northern seasonal role "
             "(6-month shift). Dashed verticals are the calendar-quarter cuts; the dot marks "
             "where each season's own\nobservation window ends and the tail is imported from the "
             "Melb Dec-Feb reference panel",
             fontsize=10.5, y=0.995)
fig.tight_layout(rect=[0, 0.005, 1, 0.90])
p = os.path.join(OUT, "K2_leadtime_cdf_by_season.png")
fig.savefig(p, dpi=170)
print("wrote", p)
for lab, months in NORTH.items():
    G, n = season_cdf(months, "w_value", Rv)
    print(f"  {lab:<24} value-wtd: 30d {G[30]:.3f}  91d {G[91]:.3f}  182d {G[182]:.3f}  273d {G[273]:.3f}")
