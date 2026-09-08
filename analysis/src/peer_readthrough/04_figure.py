"""
04_figure.py - the two panels that carry the peer-readthrough result.

  Left  every BKNG and EXPE earnings-reaction day: the peer's abnormal return against ABNB's, with the
        fitted line for each. EXPE's slope is real (r 0.81, jackknife 0.75-0.84); BKNG's is a cloud (r 0.01).
  Right how much bigger ABNB's own idiosyncratic move is on each peer's print day than on an ordinary day
        (z_ratio from 02_peer_summary.csv, volatility-standardised). 1.0 = an ordinary day.

Inputs   data/processed/peer_readthrough/02_event_days.csv, 02_peer_summary.csv
Output   analysis/figures/peer_readthrough_abnb.png

Run: py -3.13 analysis/src/peer_readthrough/04_figure.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data" / "processed" / "peer_readthrough"
FIG = ROOT / "analysis" / "figures" / "peer_readthrough_abnb.png"

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#b8b7b2"
BLUE, ORANGE = "#2a78d6", "#eb6834"   # categorical slots 1 and 2


def main():
    ed = pd.read_csv(PROC / "02_event_days.csv", parse_dates=["reaction_date"])
    s = pd.read_csv(PROC / "02_peer_summary.csv")
    ed = ed[~ed.abnb_print_same_day]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.5, 5.6), facecolor=SURFACE,
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    for ax in (axL, axR):
        ax.set_facecolor(SURFACE)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(MUTED)
        ax.tick_params(colors=INK2, labelsize=9, length=3, color=MUTED)

    # ---- left: the scatter ----
    axL.axhline(0, color=MUTED, lw=1, zorder=1)
    axL.axvline(0, color=MUTED, lw=1, zorder=1)
    for tk, col in [("EXPE", BLUE), ("BKNG", ORANGE)]:
        d = ed[ed.ticker == tk]
        x, y = d.ar_peer.to_numpy(float), d.ar_abnb.to_numpy(float)
        r = np.corrcoef(x, y)[0, 1]
        axL.scatter(x, y, s=62, color=col, edgecolor=SURFACE, linewidth=2, zorder=3,
                    label=f"{tk}  (n={len(d)}, r = {r:.2f})")
        b, a = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 20)
        axL.plot(xs, a + b * xs, color=col, lw=2, zorder=2)
    axL.set_xlabel("Peer's own abnormal return on its earnings-reaction day (%)", color=INK2, fontsize=9.5)
    axL.set_ylabel("ABNB abnormal return, same day (%)", color=INK2, fontsize=9.5)
    axL.set_title("Expedia's print reads through to Airbnb. Booking's does not.",
                  color=INK, fontsize=12, fontweight="bold", loc="left", pad=10)
    leg = axL.legend(frameon=False, fontsize=9.5, loc="upper left")
    for t in leg.get_texts():
        t.set_color(INK2)
    axL.text(4.0, -4.6, "slope 0.18: ABNB picks up about 18c\nof every $1 Expedia moves on its print",
             fontsize=9, color=INK2, ha="left")

    # ---- right: the volatility ratio ----
    t = s[s.scope == "ticker"].sort_values("z_ratio")
    y = np.arange(len(t))
    axR.barh(y, t.z_ratio, height=0.68, color=BLUE, zorder=3)
    axR.axvline(1.0, color=INK2, lw=1.4, zorder=4)
    axR.set_yticks(y)
    axR.set_yticklabels(t.name, fontsize=9.5, color=INK)
    axR.set_xlim(0, 1.72)
    axR.set_xlabel("ABNB's mean |abnormal return| on that peer's print day,\nrelative to an ordinary day (volatility-standardised)",
                   color=INK2, fontsize=9.5)
    axR.set_title("Only the two OTAs and one timeshare register at all",
                  color=INK, fontsize=12, fontweight="bold", loc="left", pad=10)
    for yi, (v, p) in enumerate(zip(t.z_ratio, t.p_absz_perm_eramatched)):
        star = "  *" if p <= 0.05 else ""
        axR.text(v + 0.025, yi, f"{v:.2f}{star}", va="center", fontsize=9, color=INK2)
    axR.set_ylim(-1.3, len(t) - 0.35)
    axR.text(1.015, -0.85, "ordinary day", fontsize=8.5, color=INK2, va="center")
    axR.text(0.02, -0.85, "*  p <= 0.05, era-matched permutation test", fontsize=8.5, color=INK2, va="center")

    fig.text(0.008, 0.038,
             "Abnormal return = residual of a market model vs QQQ, betas fitted on the 250 sessions ending 6 days before the day shown.",
             fontsize=7.6, color=INK2)
    fig.text(0.008, 0.014,
             "Peer earnings dates from SEC 8-K Item 2.02 filings; reaction day is the filing date if accepted before 16:00 ET, else the "
             "next session. Days ABNB itself reported are excluded. Dec 2020 - Sep 2026.",
             fontsize=7.6, color=INK2)
    fig.tight_layout(rect=[0, 0.075, 1, 1])
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, dpi=170, facecolor=SURFACE)
    print(f"wrote {FIG}")


if __name__ == "__main__":
    main()
