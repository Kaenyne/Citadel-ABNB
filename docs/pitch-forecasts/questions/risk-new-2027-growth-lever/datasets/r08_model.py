"""R08 risk-new-2027-growth-lever: tree arithmetic. Outputs r08_summary.csv, r08_sensitivity.csv. Standard library only."""
import csv, pathlib
here = pathlib.Path(__file__).parent


def tree(p_named=0.92, p_num_nov=0.05, p_num_feb=0.12, p_loose=0.25, p_oom_phrase=0.45, strict=True):
    # P(explicit >=1pt / >=$1bn-GBV-equivalent 2027 figure for a named lever in the Nov letter/call or the Feb letter/call)
    p_explicit = p_named * (1 - (1 - p_num_nov) * (1 - p_num_feb))
    # loose-resolver route: an order-of-magnitude phrase ("hundreds of millions", "as much as Hawaii") is counted
    p_loose_route = 0.0 if strict else p_named * p_oom_phrase * p_loose
    return p_explicit + (1 - p_explicit) * p_loose_route


base = tree()
rows = [("base (convention: explicit figure required)", base),
        ("loose resolver counts order-of-magnitude phrases", tree(strict=False)),
        ("p_num_feb 0.20 (Feb letter decomposes the FY27 guide)", tree(p_num_feb=0.20)),
        ("p_num_feb 0.06 (2Q26 no-one-thing framing persists)", tree(p_num_feb=0.06)),
        ("p_named 0.75 (no product named before Feb)", tree(p_named=0.75)),
        ("joint bull (named 0.95, nov 0.10, feb 0.25, loose)", tree(p_named=0.95, p_num_nov=0.10, p_num_feb=0.25, strict=False)),
        ("joint bear (named 0.8, nov 0.03, feb 0.06)", tree(p_named=0.8, p_num_nov=0.03, p_num_feb=0.06))]
with open(here / "r08_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric", "value"]); w.writerow(["p_yes_base", round(base, 4)])
with open(here / "r08_sensitivity.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "p_yes"])
    for n, p in rows:
        w.writerow([n, round(p, 3)])
for n, p in rows:
    print(f"{n:60s} {p:.3f}")
