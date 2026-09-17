"""R09 risk-new-businesses-quantified-material: route arithmetic. Outputs r09_summary.csv, r09_sensitivity.csv. Standard library only."""
import csv, pathlib
here = pathlib.Path(__file__).parent


def tree(p_hotel_nov=0.12, p_hotel_feb=0.18, p_true_ge3=0.65, p_seats_ge3=0.02, p_gbv=0.02, p_rev500=0.03, p_combined=0.03):
    p_hotel_disc = 1 - (1 - p_hotel_nov) * (1 - p_hotel_feb)        # a numeric or mid/high-single-digit hotel share of total nights
    p_hotel_yes = p_hotel_disc * p_true_ge3                             # ... and the figure is >= 3
    p_other = 1 - (1 - p_seats_ge3) * (1 - p_gbv) * (1 - p_rev500) * (1 - p_combined)
    return 1 - (1 - p_hotel_yes) * (1 - p_other), p_hotel_disc, p_hotel_yes, p_other


base = tree()
rows = [("base", base),
        ("hotel disclosure hazards halved (0.06 / 0.09)", tree(p_hotel_nov=0.06, p_hotel_feb=0.09)),
        ("hotel disclosure hazards doubled (0.24 / 0.36)", tree(p_hotel_nov=0.24, p_hotel_feb=0.36)),
        ("true hotel share >= 3 with P 0.40 (hotels ~2-3% of nights)", tree(p_true_ge3=0.40)),
        ("true hotel share >= 3 with P 0.85 (hotels ~4-6%)", tree(p_true_ge3=0.85)),
        ("Feb letter gives a combined new-business share (p_combined 0.10)", tree(p_combined=0.10)),
        ("joint bull (0.20/0.35, true 0.85, combined 0.10, rev 0.06)", tree(p_hotel_nov=0.20, p_hotel_feb=0.35, p_true_ge3=0.85, p_combined=0.10, p_rev500=0.06)),
        ("joint bear (0.06/0.09, true 0.40, others 0.01)", tree(p_hotel_nov=0.06, p_hotel_feb=0.09, p_true_ge3=0.40, p_seats_ge3=0.01, p_gbv=0.01, p_rev500=0.01, p_combined=0.01))]
with open(here / "r09_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric", "value"])
    for k, v in zip(["p_yes", "p_hotel_share_disclosed", "p_hotel_route_yes", "p_other_routes"], base):
        w.writerow([k, round(v, 4)])
with open(here / "r09_sensitivity.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "p_yes", "p_hotel_share_disclosed", "p_hotel_route_yes", "p_other_routes"])
    for n, r in rows:
        w.writerow([n] + [round(x, 3) for x in r])
for n, r in rows:
    print(f"{n:62s} P={r[0]:.3f} disc={r[1]:.3f} hotelYes={r[2]:.3f} other={r[3]:.3f}")
