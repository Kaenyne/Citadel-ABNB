"""
SIMPLE nights model. Three drivers, all disclosed or management-quantified. No hotels.

Replaces choice_nights_driver.py for forecasting. That model had ~15 inputs, most of them about
HOTELS - a contestable pool, rooms per party, leisure party mixes, a price switch rate - and the
audit showed the hotel machinery was near-inert anyway: at the team's near-parity ADR path, moving
the switch rate from 5.0 to 10.3 changed 2030 nights by 2.1%, and the na_nights_reconciliation work
found that NEITHER the switch rate nor the contestable share could close the gap to the team's path
at ANY value. The hotel comparison is a good THESIS point (Airbnb takes 6% of solo lodging but 31%
of 5+ parties, confirmed in four datasets). It is not what moves the nights line.

WHAT ACTUALLY MOVES IT, from Airbnb's own disclosures:

    Nights(t) = Base(t) x (1 + L(t)) x (1 - C(t)) / (1 - C(0))

  Base   underlying demand, growing at the pre-feature run rate.
         Disclosed nights growth was +7.92% (1Q25) and +7.43% (2Q25), i.e. BEFORE Reserve Now Pay
         Later launched in the US. That is the underlying rate, ~7.5%, and it is observed, not fitted.

  L(t)   cumulative LEVEL uplift from the 2025-26 product bundle: Reserve Now Pay Later, the
         cancellation-policy redesign, and the single-fee migration. Management sized the bundle at
         ~2pts of nights (4Q25 call) and ~3pts (1Q26 call). It is a LEVEL effect, so it lifts the
         growth RATE only while L is still rising and contributes exactly zero once it plateaus.
         That plateau is the lap, and the dates are disclosed: US launch laps 3Q26, up-funnel
         merchandising 4Q26, global 1Q27. This is the single most important feature of the model.

  C(t)   platform cancellation rate. Nights and Seats Booked is reported NET of cancellations, so a
         rising cancellation rate is a direct, mechanical drag on reported nights. RNPL took the
         aggregate rate from ~16% to ~17%. Two things compound here:
             C(t) = (1 - s(t)) x c_base + s(t) x c_rnpl(t)
         s(t)      RNPL share of bookings - rising as adoption spreads
         c_rnpl(t) cancellation rate WITHIN the RNPL cohort - also rising, because zero-due-at-
                   booking selects progressively more marginal, less committed bookers as it scales
         c_base is pinned at the pre-RNPL 16%. c_rnpl is then DERIVED from the observed aggregate
         rather than assumed: at s=50% an aggregate of 17% implies c_rnpl = 18%.

ADR IS DOWNSTREAM, NOT AN INPUT. The old model fed an ADR path in to drive share. That causality is
backwards: ADR = GBV / nights, both dated at booking, so ADR is an OUTPUT of what kind of nights get
booked. RNPL's own disclosed channels are mix channels - guests "choose a slightly nicer listing",
mix shifts to 4+ bedroom homes - so the feature that lifts nights also lifts ADR. ADR is reported
here as a function of the nights mix, never as a driver of it.

WHAT THIS MODEL DOES NOT CONTAIN, deliberately: hotels, party-size segments, a contestable share, a
price switch rate, rooms per party, leisure party mixes, market-growth assumptions. Every one was an
assumption; none of them moved the answer.

Run:  python analysis/src/nights_simple.py
Out:  data/processed/nights_simple.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

NIGHTS_2025 = 533.0          # FY2025 10-K
UNDERLYING = 0.075           # pre-RNPL disclosed run rate (1Q25 +7.92%, 2Q25 +7.43%)
C_BASE = 0.16                # pre-RNPL platform cancellation rate

# Cumulative LEVEL uplift from the product bundle. 2025 carries the part already in the base year;
# it plateaus once all three features have lapped (global lap 1Q27), so 2027+ adds nothing.
FEATURE_LEVEL = {2025: 0.020, 2026: 0.030, 2027: 0.030, 2028: 0.030, 2029: 0.030, 2030: 0.030}

# RNPL share of bookings and the cancellation rate within that cohort. The 2026 pair is pinned by
# the observed aggregate (~17%); the paths after are the model's two real assumptions.
RNPL_SHARE = {2025: 0.25, 2026: 0.50, 2027: 0.65, 2028: 0.75, 2029: 0.80, 2030: 0.85}
RNPL_CANCEL = {2025: 0.180, 2026: 0.180, 2027: 0.187, 2028: 0.193, 2029: 0.198, 2030: 0.202}

YEARS = [2025, 2026, 2027, 2028, 2029, 2030]


def cancel_rate(y):
    s = RNPL_SHARE[y]
    return (1 - s) * C_BASE + s * RNPL_CANCEL[y]


def main():
    c0 = cancel_rate(2025)
    rows, base = [], NIGHTS_2025 / (1 + FEATURE_LEVEL[2025])
    prev = None
    for y in YEARS:
        if y > YEARS[0]:
            base *= (1 + UNDERLYING)
        n = base * (1 + FEATURE_LEVEL[y]) * (1 - cancel_rate(y)) / (1 - c0)
        g = (n / prev - 1) if prev else None
        rows.append({"year": y, "underlying_base_mm": round(base, 1),
                     "feature_level": FEATURE_LEVEL[y], "rnpl_share": RNPL_SHARE[y],
                     "rnpl_cancel": RNPL_CANCEL[y], "cancel_rate": round(cancel_rate(y), 4),
                     "nights_mm": round(n, 1), "growth": round(g, 4) if g else None})
        prev = n
    d = pd.DataFrame(rows)

    print("SIMPLE NIGHTS MODEL - three drivers, no hotels\n")
    print(d.to_string(index=False))

    print("\nGROWTH DECOMPOSITION (pp of prior-year nights)")
    print(f"  {'year':6s} {'underlying':>11s} {'feature':>9s} {'cancel':>8s} {'total':>8s}")
    for i in range(1, len(d)):
        p, c = d.iloc[i - 1], d.iloc[i]
        feat = (1 + c.feature_level) / (1 + p.feature_level) - 1
        canc = (1 - c.cancel_rate) / (1 - p.cancel_rate) - 1
        print(f"  {int(c.year):6d} {UNDERLYING * 100:10.2f}% {feat * 100:8.2f}% "
              f"{canc * 100:7.2f}% {c.growth * 100:7.2f}%")

    print("""
READ:
  2026 is the last year the product bundle contributes anything. It laps across 3Q26 (US launch),
  4Q26 (merchandising) and 1Q27 (global), after which FEATURE_LEVEL is flat and adds exactly zero
  to the growth rate - while the cancellation drag it created persists and keeps growing as RNPL
  share rises. That asymmetry is the whole model: a one-off level gain against a permanent,
  compounding drag.
""")
    g26 = d.loc[d.year == 2026, "growth"].iloc[0]
    print(f"  2026 {g26 * 100:+.1f}%  vs Airbnb's 3Q26 guide of 10-12% (mid 11%) and Krish's FY26 +9.9%")
    print(f"  2027 {d.loc[d.year == 2027, 'growth'].iloc[0] * 100:+.1f}%  <- the lap year, and the "
          f"call the model exists to make")
    print(f"  cancellation rate {c0:.1%} (2025) -> {cancel_rate(2030):.1%} (2030), "
          f"costing {(1 - cancel_rate(2030)) / (1 - c0) - 1:+.1%} of nights cumulatively")

    # ---- ADR AS AN OUTPUT, not an input
    print("\nADR IS DOWNSTREAM (reported here, never fed in)")
    print("  ADR = GBV / nights, both dated at booking, so it follows the MIX of nights booked.")
    print("  RNPL's own disclosed channels are mix channels: guests pick 'a slightly nicer listing'")
    print("  and mix shifts to 4+ bedroom homes. So the feature that lifts nights also lifts ADR -")
    print("  which is why the old model's ADR-drives-share causality was backwards.")
    print("  Management sized the same bundle at ~3pts of NIGHTS and ~4pts of GBV (1Q26 call);")
    print("  the 1pt wedge IS the ADR mix effect, and it laps with the nights effect.")
    adr25 = 91273.0 / NIGHTS_2025
    print(f"    FY2025 ADR = GBV $91,273mm / {NIGHTS_2025}mm nights = ${adr25:.2f}")
    print(f"    bundle wedge: ~4pts GBV - ~3pts nights = ~1pt of ADR, lapping on the same schedule")

    print("\nSENSITIVITY - the two real assumptions, and only these two")
    for lbl, share, canc in [("RNPL stalls at 50%, cohort rate flat", 0.50, 0.180),
                             ("base case", RNPL_SHARE[2030], RNPL_CANCEL[2030]),
                             ("RNPL to 95%, cohort rate to 22%", 0.95, 0.220)]:
        c30 = (1 - share) * C_BASE + share * canc
        drag = (1 - c30) / (1 - c0) - 1
        n30 = (NIGHTS_2025 / (1 + FEATURE_LEVEL[2025])) * (1 + UNDERLYING) ** 5 * \
              (1 + FEATURE_LEVEL[2030]) * (1 - c30) / (1 - c0)
        print(f"  {lbl:38s} 2030 cancel {c30:5.1%}  nights {n30:6.1f}mm  "
              f"cum drag {drag:+.1%}")

    d.to_csv(OUT / "nights_simple.csv", index=False)
    print("\nwrote", OUT / "nights_simple.csv")


if __name__ == "__main__":
    main()
