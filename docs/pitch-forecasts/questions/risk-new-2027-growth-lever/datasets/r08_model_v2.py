"""R08 risk-new-2027-growth-lever, revision 2 (audit A11 response). Tree arithmetic plus the corrected
impact rows. Changes from r08_model.py (kept untouched): the per-print conditionals are relabelled a judgmental
elicitation (A11-22) and re-set to Nov 0.035 / Feb 0.10 after convention 2 was narrowed to booking-generating
revenue (A11-07; the seller-services / sponsored-listings route no longer counts); the impact rows are computed
from the line build's FY27 base (A11-06, A11-21). Standard library only."""
import csv, pathlib
here = pathlib.Path(__file__).parent


def tree(p_named=0.92, p_num_nov=0.035, p_num_feb=0.10, p_loose=0.25, p_oom_phrase=0.45, strict=True):
    p_explicit = p_named * (1 - (1 - p_num_nov) * (1 - p_num_feb))
    p_loose_route = 0.0 if strict else p_named * p_oom_phrase * p_loose
    return p_explicit + (1 - p_explicit) * p_loose_route


base = tree()
rows = [("base (rev 2: explicit figure, booking-generating revenue only)", base),
        ("loose resolver counts order-of-magnitude phrases", tree(strict=False)),
        ("p_num_feb 0.20 (Feb letter decomposes the FY27 guide by driver)", tree(p_num_feb=0.20)),
        ("p_num_feb 0.06 (2Q26 no-one-thing framing persists)", tree(p_num_feb=0.06)),
        ("p_num_nov 0.05 (revision-1 November)", tree(p_num_nov=0.05)),
        ("p_named 0.75 (no product named before Feb)", tree(p_named=0.75)),
        ("convention 2 as in revision 1 (take-rate revenue converts): Feb 0.12", tree(p_num_feb=0.12)),
        ("auditor tree (named 1.0, Nov 0.03, Feb 0.10)", tree(p_named=1.0, p_num_nov=0.03, p_num_feb=0.10)),
        ("revision-1 tree (Nov 0.05, Feb 0.12)", tree(p_num_nov=0.05, p_num_feb=0.12)),
        ("joint bull (named 0.95, nov 0.08, feb 0.22, loose)", tree(p_named=0.95, p_num_nov=0.08, p_num_feb=0.22, strict=False)),
        ("joint bear (named 0.8, nov 0.02, feb 0.05)", tree(p_named=0.8, p_num_nov=0.02, p_num_feb=0.05))]
with open(here / "r08_v2_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric", "value"]); w.writerow(["p_yes_base", round(base, 4)])
    w.writerow(["p_yes_lenient", round(tree(strict=False), 4)])
with open(here / "r08_v2_sensitivity.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "p_yes"])
    for n, p in rows:
        w.writerow([n, round(p, 3)])
for n, p in rows:
    print(f"{n:75s} {p:.3f}")

# base-rate classes (Laplace)
print("all prints 0/23 -> per print %.4f, two prints %.4f" % (1 / 25, 1 - (1 - 1 / 25) ** 2))
print("prints since the new-business strategy (4Q24-2Q26) 0/7 -> per print %.4f, two prints %.4f" % (1 / 9, 1 - (1 - 1 / 9) ** 2))
print("Feb letters 0/6 (4Q20-4Q25) -> %.4f; 3Q prints 0/5 -> %.4f; union Feb-class x all-print Nov = %.4f"
      % (1 / 8, 1 / 7, 1 - (1 - 1 / 25) * (1 - 1 / 8)))

# impact (line build FY27: revenue 15,829, adj. EBITDA 5,483; brief: 1pt of FY27 growth = $158M; flex 0.42)
FY26_REV, FY27_REV, FY27_EBITDA = 14268.0, 15829.0, 5483.0
up = 0.42 * 158
base_m = 100 * FY27_EBITDA / FY27_REV
with open(here / "r08_v2_impact.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["launch_opex_musd", "fy27_margin_pct", "delta_pp", "eps_delta_usd", "ebitda_delta_musd"])
    for cost in (0, 60, 100, 112, 125):
        m = 100 * (FY27_EBITDA + up - cost) / (FY27_REV + 158)
        w.writerow([cost, round(m, 3), round(m - base_m, 3), round((up - cost) * 0.0014, 3), round(up - cost, 1)])
        print("launch opex $%3dM -> margin %.3f%% (%+.3fpp), EBITDA %+.0fM, EPS %+.3f" % (cost, m, m - base_m, up - cost, (up - cost) * 0.0014))
mult = 99e3 / 5483.0     # market cap / FY27 EBITDA ~ 18x
cost = 112
ebitda_hit = cost - up
debit = ebitda_hit * mult / 590
print("margin debit at $%dM: EBITDA -%.0fM x %.1fx / 590m sh = -$%.2f/share; net stock = +4.90 - %.2f = %+.2f; EV at 0.13 = %+.2f"
      % (cost, ebitda_hit, mult, debit, debit, 4.90 - debit, 0.13 * (4.90 - debit)))
print("fixed-multiple channel: +1.50 - %.2f = %+.2f; EV %+.2f" % (debit, 1.50 - debit, 0.13 * (1.50 - debit)))
print("1pt of FY27 growth on the FY26 base = %.1fM (the brief's $158M is 1%% of FY27 revenue)" % (0.01 * FY26_REV))
