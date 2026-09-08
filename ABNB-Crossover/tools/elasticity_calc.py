"""Elasticity + GP$/ring bridge calculations for SIG pitch (GAP G1).
All inputs cited to files in SIG/research/data/ or research reports."""
import math

def log_elast(q1, q0, p1, p0):
    return math.log(q1/q0) / math.log(p1/p0)

def arc_elast(q1, q0, p1, p0):
    return ((q1-q0)/((q1+q0)/2)) / ((p1-p0)/((p1+p0)/2))

print("=" * 70)
print("A. GJEPC INDIA LGD WHOLESALE (official customs, P and Q both observed)")
print("=" * 70)
# gjepc_india_lgd_natural_exports.csv
# FY2024-25: 14.433 Mct @ $87.76 -> FY2025-26: 18.838 Mct @ $60.14
e_log = log_elast(18.838, 14.433, 60.14, 87.76)
e_arc = arc_elast(18.838, 14.433, 60.14, 87.76)
print(f"FY24-25->FY25-26: vol +{18.838/14.433-1:.1%}, price {60.14/87.76-1:.1%}, "
      f"value {1133.0/1266.68-1:.1%}")
print(f"  elasticity: log {e_log:.2f}, arc(midpoint) {e_arc:.2f}")
# YTD Apr-Jul: 5.982 Mct @ 68.31 vs 5.082 Mct @ 74.79
e_log2 = log_elast(59.82, 50.82, 68.31, 74.79)
print(f"Apr-Jul 26 vs 25: vol +{59.82/50.82-1:.1%}, price {68.31/74.79-1:.1%}, "
      f"value {408.5/380.09-1:.1%}; log elast {e_log2:.2f}")
# H2 FY25-26 implied price
h2_val = 1133.0 - 380.09; h2_vol = 188.38 - 50.82  # lakh ct
h2_price = h2_val/ h2_vol * 100  # USD/ct ($M / lakh-ct: 1 lakh=0.1M -> *10... check)
# 1 lakh carat = 100,000 ct. value $M / (lakh ct) = 1e6/1e5 $/ct = 10 $/ct per unit
h2_price = h2_val / h2_vol * 10
print(f"Implied H2 FY25-26 realized price: ${h2_price:.2f}/ct; "
      f"Apr-Jul-26 $68.31 = {68.31/h2_price-1:+.1%} off H2 trough (SEQUENTIAL)")
print(f"CHECK full-yr FY25-26: {1133.0/188.38*10:.2f} $/ct (should be ~60.14)")

print()
print("=" * 70)
print("B. BRITECO CONSUMER 'CARAT DEMAND' ELASTICITY (LGD rings, 2019->2026)")
print("=" * 70)
# briteco: LGD ring $5,533 (2019, 1.01ct avg center) -> $4,578 (2026H1, 2.01ct)
p0, p1 = 5533/1.01, 4578/2.01   # $ per center-carat proxy
q0, q1 = 1.01, 2.01
print(f"$/carat proxy: ${p0:,.0f} -> ${p1:,.0f} ({p1/p0-1:.1%}); carats {q0}->{q1} (+{q1/q0-1:.0%})")
print(f"  carat-demand elasticity: log {log_elast(q1,q0,p1,p0):.2f}, arc {arc_elast(q1,q0,p1,p0):.2f}")
print(f"  ring spend retained: {4578/5533:.1%} (gave back {1-4578/5533:.1%} of budget "
      f"against {1-p1/p0:.0%} price/ct decline)")
# Natural comparison
print(f"Natural ring: $6,101 (2019) -> $13,660 (2026H1) = +{13660/6101-1:.0%}")

print()
print("=" * 70)
print("C. TENORIS LGD FINISHED: UNITS vs PRICE by year (retail, y/y averages)")
print("=" * 70)
# monthly y/y from tenoris_series.csv (lgd_fin_units_yoy_pct, lgd_fin_avg_price_yoy_pct)
years = {
 2023: dict(units=[59,57.6,41,67.8,51.9,45.7,64.4,45.6,51.2], price=[-12.2,-12.8,-33,-22.9,-27.7,-24.2,-23.5,-9.6]),
 2024: dict(units=[44,42.7,41.4,53,43,59,10,33,50], price=[-5.9,-11.7,-8,-8.5,-7,-8.5,-10.6]),
 2025: dict(units=[51.5,38,40,48,45,30,3], price=[-8.8,-8,-7.5,-6,-4]),
 2026: dict(units=[24], price=[0]),  # Q2-26 via JCK: +24% units-driven, spend/unit stable
}
for y, d in years.items():
    u = sum(d['units'])/len(d['units']); p = sum(d['price'])/len(d['price'])
    ratio = u/p if p != 0 else float('nan')
    print(f"{y}: avg units y/y {u:+.0f}%, avg price y/y {p:+.0f}%, naive ratio {ratio:.1f}"
          + ("  <- price flat, units STILL +24% => demand-curve SHIFT (adoption), not price response" if p==0 else ""))

print()
print("=" * 70)
print("D. GP$ PER RING AT SIGNET (VIC's own 2025 base, published margins)")
print("=" * 70)
lgd_aur, nd_aur = 3245.0, 4040.0   # VIC Exhibit 1, FY2025
print(f"AURs (VIC Exhibit 1): LGD ${lgd_aur:,.0f}, natural ${nd_aur:,.0f}")
print(f"\nGP$/ring grid (rows: LGD merch margin; cols: natural merch margin):")
print(f"{'':>10}" + "".join(f"nat {nm:.0%}".rjust(12) for nm in [0.35,0.40,0.45]))
for lm in [0.50,0.60,0.70]:
    row = f"LGD {lm:.0%}".rjust(10)
    for nm in [0.35,0.40,0.45]:
        row += f"{lgd_aur*lm/(nd_aur*nm):>11.2f}x"
    print(row)
print("(cell = LGD GP$/ring divided by natural GP$/ring; >1 = mix shift ACCRETIVE/ring)")
for nm in [0.35,0.40,0.45]:
    be = nd_aur*nm/lgd_aur
    print(f"  breakeven LGD margin vs natural at {nm:.0%}: {be:.1%}")
print(f"\nTilson '4 LGD = 1 natural' check: requires LGD GP$/ring = 25% of natural's")
print(f"  at natural 40% margin, that means LGD margin {nd_aur*0.40/4/lgd_aur:.1%} -- "
      f"vs published panels 60-82%")

print()
print("=" * 70)
print("E. SIG BRIDAL GP$ SCENARIOS (annual, VIC 2025 base: LGD $933.5M / ND $1,772.3M)")
print("=" * 70)
lgd_rev0, nd_rev0 = 933.5, 1772.3
lm, nm = 0.60, 0.35   # base margin assumptions
gp0 = lgd_rev0*lm + nd_rev0*nm
print(f"Base bridal merch GP$ (LGD 60% / nat 35%): ${gp0:,.0f}M "
      f"(LGD ${lgd_rev0*lm:,.0f}M + ND ${nd_rev0*nm:,.0f}M)")
scenarios = {
  "A. Budget-holding (Tenoris world): LGD AUR 0%/units +10%; ND AUR +5%/units -8%":
     ((1.00*1.10), (1.05*0.92)),
  "B. VIC bear yr-1 (their 2027E): LGD AUR -8.4%/units +26.6%; ND AUR -6.6%/units -26.2%":
     ((0.916*1.266), (0.934*0.738)),
  "C. Asymptote binds, budget breaks: LGD AUR -8%/units +5%; ND AUR 0%/units -15%":
     ((0.92*1.05), (1.00*0.85)),
  "D. Signet FY26 ACTUAL shape: bridal AUR +6%, units ~flat (comps +LSD)":
     (1.06, 1.06),  # applied to both (blended AUR-led)
}
for name, (lgd_f, nd_f) in scenarios.items():
    gp1 = lgd_rev0*lgd_f*lm + nd_rev0*nd_f*nm
    print(f"\n{name}")
    print(f"  bridal GP$ ${gp1:,.0f}M ({gp1/gp0-1:+.1%}); "
          f"vs -6%/yr share count -> per-share bridal GP {gp1/gp0/0.94-1:+.1%}")

print()
print("=" * 70)
print("F. GOLAN 2ct GP$ DATAPOINT + the cost-share endgame")
print("=" * 70)
print(f"Golan 2ct stone: GP$ $1,902 (Sep-24) -> $1,766 (Sep-25) = {1766/1902-1:.1%}")
print(f"  margin RATE rose (67%->75%) while GP DOLLARS fell -- the bear's point, real")
print(f"1ct LGD wholesale $80/ct on retail ~$800-900/ct: cost is {80/850:.0%} of retail.")
print(f"  From here GP$/unit ~= retail price. Rate expansion is arithmetically OVER;")
print(f"  retail spend behavior (Tenoris: flat) IS the GP$ outlook.")

print()
print("=" * 70)
print("G. CATEGORY REVENUE: did volume outpace ASP? (the user's question, answered)")
print("=" * 70)
print("LGD wholesale (GJEPC): vol +30.5% vs price -31.5% -> value -10.6%. NO (elast ~ -0.7 to -1.0)")
print("LGD retail (Tenoris 2026): units +24% at FLAT price -> revenue +24%, but Jan-26 rev -5%,")
print("  Jul-26 rev flat -> full-period LGD retail revenue ~flat. Volume growth is offsetting")
print("  the LAGGED retail repricing, not outpacing it.")
print("Total US jewelry (Tenoris 2025): sales +7.5% ON units -5.6% / avg spend +14%")
print("  -> the category grows on PRICE (natural premiumization + gold), not volume.")
