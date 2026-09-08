"""
Fee-split demand elasticity model — Airbnb split fee (3% host / 14% guest)
vs. host-only fee (15.5% host / 0% guest).

Question it answers: for a given guest price elasticity (eps), host pass-through
(theta) and fee-salience discount (sigma), what happens to guest price, nights,
GBV, Airbnb revenue, take rate and host payout when Airbnb moves every host to
the single 15.5% fee?

Mechanics (per $100 of host-set subtotal under the old model):
  OLD  guest pays  100*(1+fg) = 114      host nets 100*(1-fh_old) = 97   Airbnb 17
  NEW  host resets price to p' = 100*(1 + theta*g)  where g = required gross-up
       to keep payout flat = (1-fh_old)/(1-fh_new) - 1 = 0.97/0.845 - 1 = 14.8%
       guest pays p'          host nets p'*(1-fh_new)      Airbnb p'*fh_new
  Demand: nights_new / nights_old = (P_perc_new / P_perc_old) ** eps
       where P_perc_old = 100*(1 + fg*(1-sigma))  (guests under-weight a
       drip-priced fee by sigma; sigma=0 once total-price display is default)
       and P_perc_new = p'.
  Reported take rate = Airbnb revenue / GBV, with GBV = guest total paid
  (Airbnb's GBV also includes taxes and cleaning fees, so absolute levels here
  run ~150bp above the reported 13.2%; the *deltas* are what matter).

Parameter sources (see research/notes/host_only_fee_history_and_elasticity.md):
  fees   — Airbnb Help Center art. 1857 (split: host 3%, guest 14.1–16.5%;
           single: 15.5%)
  eps    — Farronato & Fradkin (AER 2022) listing-level own-price elasticity
           −4.27 avg (upper bound for platform level); Airbnb's 2020 claim of
           +17% bookings for hosts who switched implies eps ≈ −1.2 at the
           listing level vs. non-switched neighbours; platform-level range used
           here: −0.5 to −2.0.
  theta  — Reddit/PriceLabs guidance: +14.8% (payout-neutral) or +18.34%
           (ignores old 3%); many hosts "do nothing" for weeks.
  sigma  — Blake/Moshary/Sweeney/Tadelis (StubHub RCT): hidden fees +14%
           purchase rate, +21% spend → guests behave as if ~half the fee is
           invisible. Airbnb has shown total price by default globally since
           Apr 2025, so base case sigma = 0.
"""
from __future__ import annotations
import itertools
import pathlib
import pandas as pd

FH_OLD, FG_OLD = 0.03, 0.14          # split fee
FH_NEW, FG_NEW = 0.155, 0.0          # single fee
BASE_SUBTOTAL = 100.0
GROSSUP_NEUTRAL = (1 - FH_OLD) / (1 - FH_NEW) - 1   # 14.79%

ELASTICITIES = [-0.5, -1.0, -1.5, -2.0, -4.27]
PASS_THROUGH = [0.0, 0.5, 1.0, 18.34 / (GROSSUP_NEUTRAL * 100)]  # 0, half, neutral, "reddit 18.34%"
SALIENCE = [0.0, 0.25, 0.5]


def scenario(eps: float, theta: float, sigma: float, nights0: float = 1.0) -> dict:
    p_old = BASE_SUBTOTAL
    guest_old = p_old * (1 + FG_OLD)
    host_old = p_old * (1 - FH_OLD)
    abnb_old = guest_old - host_old
    perc_old = p_old * (1 + FG_OLD * (1 - sigma))

    p_new = p_old * (1 + theta * GROSSUP_NEUTRAL)
    guest_new = p_new * (1 + FG_NEW)
    host_new = p_new * (1 - FH_NEW)
    abnb_new = guest_new - host_new
    perc_new = p_new

    nights1 = nights0 * (perc_new / perc_old) ** eps

    return dict(
        eps=eps, theta=round(theta, 3), sigma=sigma,
        host_price_chg=p_new / p_old - 1,
        guest_price_chg=guest_new / guest_old - 1,
        perceived_price_chg=perc_new / perc_old - 1,
        nights_chg=nights1 / nights0 - 1,
        gbv_chg=(guest_new * nights1) / (guest_old * nights0) - 1,
        abnb_rev_chg=(abnb_new * nights1) / (abnb_old * nights0) - 1,
        host_payout_chg=(host_new * nights1) / (host_old * nights0) - 1,
        take_rate_old=abnb_old / guest_old,
        take_rate_new=abnb_new / guest_new,
        take_rate_chg_bp=(abnb_new / guest_new - abnb_old / guest_old) * 1e4,
    )


def main() -> None:
    root = pathlib.Path(__file__).resolve().parents[2]
    rows = [scenario(e, t, s) for e, t, s in itertools.product(ELASTICITIES, PASS_THROUGH, SALIENCE)]
    df = pd.DataFrame(rows)
    out = root / "data" / "processed" / "fee_split_elasticity_scenarios.csv"
    df.to_csv(out, index=False, float_format="%.4f")

    # Headline grid: sigma = 0 (total price shown), revenue change by eps x theta
    grid = (df[df.sigma == 0]
            .pivot(index="eps", columns="theta", values="abnb_rev_chg")
            .rename(columns=lambda t: f"theta={t}"))
    print("Airbnb revenue change vs. split fee (sigma=0):")
    print((grid * 100).round(1).to_string())
    print("\nNights change (sigma=0):")
    print((df[df.sigma == 0].pivot(index="eps", columns="theta", values="nights_chg") * 100).round(1).to_string())
    print("\nHost payout change (sigma=0):")
    print((df[df.sigma == 0].pivot(index="eps", columns="theta", values="host_payout_chg") * 100).round(1).to_string())
    print(f"\nPayout-neutral gross-up: {GROSSUP_NEUTRAL*100:.2f}%")

    # Chart: revenue change vs pass-through, one line per elasticity, sigma=0
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]  # validated categorical order
    thetas = sorted(df.theta.unique())
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=False)
    fig.patch.set_facecolor("#fcfcfb")
    panels = [("abnb_rev_chg", "Airbnb revenue"), ("nights_chg", "Nights booked"), ("host_payout_chg", "Host payout")]
    for ax, (col, title) in zip(axes, panels):
        ax.set_facecolor("#fcfcfb")
        for c, e in zip(colors, [e for e in ELASTICITIES if e > -4]):  # -4.27 is listing-level; kept in CSV only
            sub = df[(df.sigma == 0) & (df.eps == e)].sort_values("theta")
            ax.plot(sub.theta * GROSSUP_NEUTRAL * 100, sub[col] * 100, color=c, lw=2, marker="o", ms=5, label=f"ε = {e}")
        ax.axhline(0, color="#c3c2b7", lw=1)
        ax.set_title(f"{title}: % change vs. split fee", fontsize=11, color="#0b0b0b", loc="left")
        ax.set_xlabel("Host price increase after switch (%)", color="#52514e")
        ax.tick_params(colors="#898781")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color("#c3c2b7")
        ax.grid(axis="y", color="#e1e0d9", lw=0.8)
    axes[0].set_ylabel("% change", color="#52514e")
    axes[0].legend(frameon=False, fontsize=9, title="Guest price elasticity", title_fontsize=9)
    fig.suptitle("Split fee (3% host + 14% guest) → single 15.5% host fee, total price shown to guest (σ = 0)",
                 fontsize=11, color="#52514e", x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(root / "docs" / "fee_split_elasticity_sensitivity.png", dpi=160, facecolor=fig.get_facecolor())
    print("\nwrote", out, "and docs/fee_split_elasticity_sensitivity.png")


if __name__ == "__main__":
    main()
