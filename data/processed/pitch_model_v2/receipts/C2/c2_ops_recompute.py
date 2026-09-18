"""C2 independent recompute: reproduce 40_line_build's operations & support formula
    ops_variable = ops[q-4 or actual] * v * (1 + d_var/100) * bookings_q / bookings[prev]
    ops_fixed    = ops[prev] * (1 - v) * (1 + ops_fixed_growth/100)
    ops_cash     = (ops_variable + ops_fixed) * (1 + rnpl_ops_uplift_pct/100)
for every committed (quarter, scenario) cell in 40_lines_quarterly.csv (base, cost_bull) and
40_short_case_quarterly.csv (short_costs_at_budget), using only 40_params.csv values, the
committed bookings_m / revenue already in those files, and the prior-year actual ops_cash /
bookings from 02_panel_quarterly.csv for the four quarters whose "previous year" is actual
(3Q25, 4Q25, 1Q26, 2Q26). For 3Q27/4Q27 the "previous year" (3Q26/4Q26) is itself a forecast
row of the SAME scenario, so hist ops/bookings are taken from that scenario's own committed
3Q26/4Q26 row -- this checks the ops formula and its recursion, not the revenue path.

Also builds the FY26/FY27 ops_musd + ops_pct_rev aggregates for the short case (not written
by 40_line_build's 40_annual.csv, which only carries the SCN scenarios), using the same
H1-actual-plus-2H26-build convention as 40_line_build.py section 4 (FY26 = 1H26 actual +
2H26 build; FY27 = four quarters).

Read-only against the repo; writes only inside this receipt folder.
"""
from pathlib import Path
import pandas as pd

ROOT = Path("/Users/theomachado/Citadel-ABNB")
LB = ROOT / "data/processed/margin_build/40_line_build"
PAN = ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
OUT = ROOT / "data/processed/pitch_model_v2/receipts/C2"

params = pd.read_csv(LB / "40_params.csv").set_index("name")
def pv(name, scen):
    return float(params.loc[name, scen])

pan = pd.read_csv(PAN).set_index("quarter")
NPB_ACT = {"3Q25": 3.7, "4Q25": 3.7, "1Q26": 3.65, "2Q26": 3.65}
Q_ORDER = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
PREV = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26"}
ACTUAL_PREV = {"3Q25", "4Q25", "1Q26", "2Q26"}

def hist_ops_bookings(pq, scen_rows):
    """scen_rows: dict quarter -> (ops_cash, bookings_m) for the FORECAST rows already
    computed within this scenario (needed for 3Q27's prev=3Q26, 4Q27's prev=4Q26)."""
    if pq in ACTUAL_PREV:
        return float(pan.loc[pq, "ops_cash"]), float(pan.loc[pq, "nights_m"]) / NPB_ACT[pq]
    return scen_rows[pq]

def recompute_scenario(committed: pd.DataFrame, cost_scen: str, rnpl_uplift_override=None) -> pd.DataFrame:
    committed = committed.set_index("quarter")
    v = pv("ops_variable_share", cost_scen)
    fixed_growth = pv("ops_fixed_growth", cost_scen)
    rnpl_uplift = pv("rnpl_ops_uplift_pct", cost_scen) if rnpl_uplift_override is None else rnpl_uplift_override
    scen_rows = {}
    out = []
    for q in Q_ORDER:
        is27 = q.endswith("27")
        pq = PREV[q]
        d_var = pv("ops_variable_decline_fy27", cost_scen) if is27 else pv("ops_variable_decline_2h26", cost_scen)
        ops_prev, bookings_prev = hist_ops_bookings(pq, scen_rows)
        bookings_q = float(committed.loc[q, "bookings_m"])
        ops_var_hat = ops_prev * v * (1 + d_var / 100) * bookings_q / bookings_prev
        ops_fix_hat = ops_prev * (1 - v) * (1 + fixed_growth / 100)
        ops_hat = (ops_var_hat + ops_fix_hat) * (1 + rnpl_uplift / 100)
        scen_rows[q] = (ops_hat, bookings_q)
        out.append(dict(quarter=q,
                         ops_variable_committed=float(committed.loc[q, "ops_variable"]), ops_variable_hat=ops_var_hat,
                         ops_fixed_committed=float(committed.loc[q, "ops_fixed"]), ops_fixed_hat=ops_fix_hat,
                         ops_cash_committed=float(committed.loc[q, "ops_cash"]), ops_cash_hat=ops_hat,
                         d_ops_cash=float(committed.loc[q, "ops_cash"]) - ops_hat,
                         revenue=float(committed.loc[q, "revenue"]),
                         ops_pct_rev_committed=float(committed.loc[q, "ops_cash_pct_rev"]) if "ops_cash_pct_rev" in committed.columns else float(committed.loc[q, "ops_cash"]) / float(committed.loc[q, "revenue"]) * 100))
    return pd.DataFrame(out)

lq = pd.read_csv(LB / "40_lines_quarterly.csv")
rows_out = []

# base and cost_bull ("breaker") scenarios, straight from 40_lines_quarterly.csv
for scen, cost_scen in [("base", "base"), ("cost_bull", "bull")]:
    sub = lq[lq.scenario == scen]
    chk = recompute_scenario(sub, cost_scen)
    chk.insert(0, "scenario", scen)
    rows_out.append(chk)

# short case: scenario "short_costs_at_budget" in 40_short_case_quarterly.csv;
# overlay rnpl_ops_uplift_pct is set to 4.0 in run.py's SHORT["overlays"] (short case applies it),
# cost parameters otherwise at "base" (short case uses base cost params + overlays, see run.py L346-348)
sc = pd.read_csv(LB / "40_short_case_quarterly.csv")
chk_short = recompute_scenario(sc, "base", rnpl_uplift_override=4.0)
chk_short.insert(0, "scenario", "short_costs_at_budget")
rows_out.append(chk_short)

check = pd.concat(rows_out, ignore_index=True)
check.to_csv(OUT / "c2_ops_recompute_check.csv", index=False)
maxdiff = check["d_ops_cash"].abs().max()
print(check.to_string())
print("max abs diff (ops_cash, USD m):", maxdiff)
assert maxdiff < 1e-6, "ops recompute mismatch"
print("PASS: ops & support (variable + fixed, RNPL overlay) reproduces exactly from 40_params.csv for base, cost_bull (breaker) and short.")

# ---------------------------------------------------------------------------------------------
# FY26 / FY27 aggregates for the short case (not in 40_annual.csv, which only carries SCN scenarios)
# ---------------------------------------------------------------------------------------------
h1_ops = float(pan.loc[["1Q26", "2Q26"], "ops_cash"].sum())
h1_rev = float(pan.loc[["1Q26", "2Q26"], "revenue"].sum())
sc_i = sc.set_index("quarter")
fy26_ops = h1_ops + float(sc_i.loc[["3Q26", "4Q26"], "ops_cash"].sum())
fy26_rev = h1_rev + float(sc_i.loc[["3Q26", "4Q26"], "revenue"].sum())
fy27_ops = float(sc_i.loc[Q_ORDER[2:], "ops_cash"].sum())
fy27_rev = float(sc_i.loc[Q_ORDER[2:], "revenue"].sum())
annual_short = pd.DataFrame([
    dict(period="FY26", scenario="short_costs_at_budget", ops_musd=fy26_ops, revenue_musd=fy26_rev, ops_pct_rev=fy26_ops / fy26_rev * 100),
    dict(period="FY27", scenario="short_costs_at_budget", ops_musd=fy27_ops, revenue_musd=fy27_rev, ops_pct_rev=fy27_ops / fy27_rev * 100),
])
annual_short.to_csv(OUT / "c2_ops_short_annual.csv", index=False)
print("\n=== short case FY aggregates (built here; not in 40_annual.csv) ===")
print(annual_short.to_string(index=False))

# base and cost_bull FY26/FY27 straight from 40_annual.csv, for the dossier's §2a table
an = pd.read_csv(LB / "40_annual.csv")
an_ops = an[(an.scenario.isin(["base", "cost_bull"])) & (an.period.isin(["FY26", "FY27"]))][["period", "scenario", "ops_cash", "revenue", "ops_cash_pct_rev"]]
an_ops.to_csv(OUT / "c2_ops_annual_base_breaker.csv", index=False)
print("\n=== base / cost_bull (breaker) FY aggregates, from 40_annual.csv ===")
print(an_ops.to_string(index=False))
