"""R09 risk-new-businesses-quantified-material, revision 2 (audit A11 response). Route arithmetic. Changes from
r09_model.py (kept untouched): the hotel hazard is 'descriptor upgraded' (any move from "single-digit" to a
number or a finer bucket; A11-12), the Feb hazard includes the same-day FY26 10-K as a venue (A11-10),
P(upgraded figure >= 3) is 0.55 from the supply arithmetic lifted for selective disclosure (A11-11), and an
aggregation route (hotels disclosed below 3 plus a seats figure, summing >= 3) is added (A11-01).
Standard library only."""
import csv, pathlib
here = pathlib.Path(__file__).parent


def tree(p_up_nov=0.12, p_up_feb=0.20, p_true_ge3=0.55, p_seats_ge3=0.02, p_gbv=0.02, p_rev500=0.03,
         p_combined=0.03, p_agg=0.02):
    p_hotel_up = 1 - (1 - p_up_nov) * (1 - p_up_feb)      # hotel descriptor upgraded at either print (or the 10-K)
    p_hotel_yes = p_hotel_up * p_true_ge3                  # ... and the upgraded figure / bucket is >= 3
    p_other = 1 - (1 - p_seats_ge3) * (1 - p_gbv) * (1 - p_rev500) * (1 - p_combined) * (1 - p_agg)
    return 1 - (1 - p_hotel_yes) * (1 - p_other), p_hotel_up, p_hotel_yes, p_other


base = tree()
rows = [("base (rev 2)", base),
        ("upgrade hazards halved (0.06 / 0.10)", tree(p_up_nov=0.06, p_up_feb=0.10)),
        ("upgrade hazards doubled (0.24 / 0.40)", tree(p_up_nov=0.24, p_up_feb=0.40)),
        ("Laplace hazard on 5 opportunities at both prints (0.143 / 0.143)", tree(p_up_nov=1 / 7, p_up_feb=1 / 7)),
        ("P(figure >= 3) 0.40 (unconditional supply arithmetic)", tree(p_true_ge3=0.40)),
        ("P(figure >= 3) 0.65 (revision 1)", tree(p_true_ge3=0.65)),
        ("P(figure >= 3) 0.85 (hotels 4-6%)", tree(p_true_ge3=0.85)),
        ("combined new-business sentence 0.10", tree(p_combined=0.10)),
        ("aggregation route 0 (resolver may not sum two figures)", tree(p_agg=0.0)),
        ("aggregation route 0.05", tree(p_agg=0.05)),
        ("strict denominator (a share of nights must be >= 3.1): P(>=3) 0.50", tree(p_true_ge3=0.50)),
        ("only an explicit number counts (no bucket): hazards x 0.75", tree(p_up_nov=0.09, p_up_feb=0.15)),
        ("auditor construction (0.10 / 0.18, true 0.55, agg 0.025)", tree(p_up_nov=0.10, p_up_feb=0.18, p_agg=0.025)),
        ("revision-1 construction (0.12 / 0.18, true 0.65, no agg)", tree(p_up_nov=0.12, p_up_feb=0.18, p_true_ge3=0.65, p_agg=0.0)),
        ("joint bull (0.20/0.35, true 0.85, combined 0.10, rev 0.06, agg 0.05)", tree(p_up_nov=0.20, p_up_feb=0.35, p_true_ge3=0.85, p_combined=0.10, p_rev500=0.06, p_agg=0.05)),
        ("joint bear (0.06/0.10, true 0.40, others 0.01)", tree(p_up_nov=0.06, p_up_feb=0.10, p_true_ge3=0.40, p_seats_ge3=0.01, p_gbv=0.01, p_rev500=0.01, p_combined=0.01, p_agg=0.01))]
with open(here / "r09_v2_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric", "value"])
    for k, v in zip(["p_yes", "p_hotel_descriptor_upgraded", "p_hotel_route_yes", "p_other_routes"], base):
        w.writerow([k, round(v, 4)])
with open(here / "r09_v2_sensitivity.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "p_yes", "p_hotel_descriptor_upgraded", "p_hotel_route_yes", "p_other_routes"])
    for n, r in rows:
        w.writerow([n] + [round(x, 3) for x in r])
for n, r in rows:
    print(f"{n:78s} P={r[0]:.3f} up={r[1]:.3f} hotelYes={r[2]:.3f} other={r[3]:.3f}")
# base rate on the corrected denominator
lap = 1 / (5 + 2); two = 1 - (1 - lap) ** 2
other = 1 - 0.98 * 0.98 * 0.97 * 0.97 * 0.98
print("Laplace 5 opportunities: %.4f/print, two prints %.4f, x0.55 = %.4f; other routes %.4f; union %.4f"
      % (lap, two, two * 0.55, other, 1 - (1 - two * 0.55) * (1 - other)))
# supply arithmetic (data/processed/hotel_funnel_audit/hotel_supply_requirements.csv)
nights_fy26 = 575e6
for share, per_1m in ((0.05, 3913.9), (0.10, 1956.9), (0.20, 978.5)):
    print("3%% of FY26 nights = %.1fm nights -> %.0f signed properties at a %d%% channel share"
          % (0.03 * nights_fy26 / 1e6, 0.03 * nights_fy26 / 1e6 * per_1m, share * 100))
nyc = 20000 * 365 * 0.8
print("NYC anchor: 20,000 rooms x 365 x 0.80 occ = %.2fm room-nights; x 20 destinations = %.0fm; 3%% target needs a %.0f%% channel share on that base"
      % (nyc / 1e6, 20 * nyc / 1e6, 100 * 0.03 * nights_fy26 / (20 * nyc)))
print("denominator: 3.0%% of nights = %.2f%% of nights+seats at a 2%% seats share" % (3.0 * 0.98))
