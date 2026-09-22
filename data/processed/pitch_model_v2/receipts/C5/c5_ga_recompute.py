"""C5 -- independent recompute of the G&A ex lodging-reserve line from 40_params.csv,
plus the three pitch scenarios (base / short / breaker) for 3Q26, 4Q26, 1Q27, 2Q27,
3Q27, 4Q27, FY26, FY27.

Read-only. Writes only into this receipt folder. Does not touch
analysis/src/margin_build/40_line_build or data/processed/margin_build/40_line_build.

  python3 data/processed/pitch_model_v2/receipts/C5/c5_ga_recompute.py

Method. The G&A line in analysis/src/margin_build/40_line_build/run.py is a two-parameter
closed-form chain (ga_growth_2h26, ga_growth_fy27) applied to the prior-year actual half/year
ga_cash_ex_lodging, spread on the 2023-25 quarterly G&A shares (SHARE["ga"]), plus a
lodging_reserves_fwd add-back that is 0 in every published scenario. Unlike cost of revenue,
S&M or product development, G&A never receives a share of the 3Q26 reconciliation-to-sentence
gap (recon_share_to_marketing sends 70% to marketing and 30% to hosting; G&A's ga3 term in the
evidence-only calc is unconditional), so this script also checks the (unstated but mechanically
implied) claim that base, evidence_only and the short case all carry identical G&A dollars, and
that this line's forecast is a pure function of the two growth parameters -- it never sees the
short case's nights/ADR overrides or the reconciliation step, unlike C1 (cost of revenue) and C4
(S&M).
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
LB = ROOT / "data/processed/margin_build/40_line_build"
PAN = ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
OUT = Path(__file__).resolve().parent

# constants copied from 40_line_build/run.py (2023-25 mean quarterly shares, WS02 02_seasonality)
SHARE_GA = {1: .2386, 2: .2600, 3: .2456, 4: .2558}
H2_GA = SHARE_GA[3] + SHARE_GA[4]
Q_ORDER = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
QN = {q: int(q[0]) for q in Q_ORDER}

params = pd.read_csv(LB / "40_params.csv").set_index("name")
PV = {c: params[c].to_dict() for c in ("base", "bear", "bull")}
pan = pd.read_csv(PAN).set_index("quarter")
lines = pd.read_csv(LB / "40_lines_quarterly.csv")
annual = pd.read_csv(LB / "40_annual.csv")
short_q = pd.read_csv(LB / "40_short_case_quarterly.csv").set_index("quarter")

GA_1H26 = float(pan.loc["1Q26", "ga_cash_ex_lodging"] + pan.loc["2Q26", "ga_cash_ex_lodging"])   # 226 + 227
GA_2H25 = float(pan.loc["3Q25", "ga_cash_ex_lodging"] + pan.loc["4Q25", "ga_cash_ex_lodging"])   # 257 + 259
REV_1H26 = float(pan.loc["1Q26", "revenue"] + pan.loc["2Q26", "revenue"])                          # 2678 + 3608
GA_CASH_1H26_ACTUAL = float(pan.loc["1Q26", "ga_cash"] + pan.loc["2Q26", "ga_cash"])                # includes the tiny 1H26 reserve/(release)


def ga_line(p: dict) -> dict:
    """The G&A chain of 40_line_build/run.py build(), for the six forecast quarters.
    Returns {quarter: ga_cash_ex_lodging}; lodging_reserves_fwd (always 0 across base/bear/bull
    in 40_params.csv) is added separately so a future non-zero reserve assumption is visible."""
    ga_2h26 = GA_2H25 * (1 + p["ga_growth_2h26"] / 100)
    ga_fy27 = (GA_1H26 + ga_2h26) * (1 + p["ga_growth_fy27"] / 100)
    out = {}
    for q in Q_ORDER:
        qn, is27 = QN[q], q.endswith("27")
        if is27:
            ga_ex = ga_fy27 * SHARE_GA[qn]
        else:
            ga_ex = ga_2h26 * SHARE_GA[qn] / H2_GA
        out[q] = ga_ex
    return out, ga_2h26, ga_fy27


rows = []
recompute = {}
for scn in ("base", "bear", "bull"):
    ga_ex, ga_2h26, ga_fy27 = ga_line(PV[scn])
    recompute[scn] = ga_ex
    for q in Q_ORDER:
        rows.append(dict(scenario=scn, quarter=q, ga_2h26_or_fy27=(ga_fy27 if q.endswith("27") else ga_2h26),
                         recompute_ga_ex_musd=ga_ex[q], lodging_reserves_fwd=PV[scn]["lodging_reserves_fwd"]))
recompute_df = pd.DataFrame(rows)

# ----------------------------------------------------------------------------------------------
# Check against committed 40_lines_quarterly.csv (base -> base scenario, bull -> cost_bull,
# bear -> cost_bear) and against 40_short_case_quarterly.csv (should equal base exactly, since
# the short build never overrides a ga_* parameter or routes any of the reconciliation gap here).
# ----------------------------------------------------------------------------------------------
SCEN_MAP = {"base": "base", "bull": "cost_bull", "bear": "cost_bear"}
check_rows = []
for scn, committed_scn in SCEN_MAP.items():
    committed = lines[lines.scenario == committed_scn].set_index("quarter")
    for q in Q_ORDER:
        mine = recompute[scn][q]
        theirs = float(committed.loc[q, "ga_cash_ex_lodging"])
        check_rows.append(dict(check="vs_40_lines_quarterly", scenario=scn, committed_scenario=committed_scn, quarter=q,
                               recompute_musd=mine, committed_musd=theirs, abs_diff=abs(mine - theirs)))
# short case identity check (base cost params, so must equal base recompute exactly)
for q in Q_ORDER:
    mine = recompute["base"][q]
    theirs = float(short_q.loc[q, "ga_cash_ex_lodging"])
    check_rows.append(dict(check="short_equals_base", scenario="short", committed_scenario="short_costs_at_budget", quarter=q,
                           recompute_musd=mine, committed_musd=theirs, abs_diff=abs(mine - theirs)))
check_df = pd.DataFrame(check_rows)
max_abs_diff = float(check_df.abs_diff.max())

# ----------------------------------------------------------------------------------------------
# Annual roll-ups: FY26 = 1H26 actual (panel ga_cash, GAAP-basis, carries any tiny actual
# lodging reserve/release) + 3Q26 + 4Q26 forecast (ex-lodging, since lodging_reserves_fwd = 0);
# FY27 = sum of the four FY27 forecast quarters. Mirrors 40_line_build/run.py section 4 exactly
# for scenario in {base, cost_bull, cost_bear}; short FY26/FY27 use the short revenue path with
# the (identical-to-base) short G&A dollars, since 40_annual.csv has no "short" row.
# ----------------------------------------------------------------------------------------------
ann_rows = []
for scn in ("base", "bear", "bull"):
    ga_ex = recompute[scn]
    fy26 = GA_CASH_1H26_ACTUAL + ga_ex["3Q26"] + ga_ex["4Q26"]
    fy27 = sum(ga_ex[q] for q in Q_ORDER[2:])
    ann_rows.append(dict(scenario=scn, period="FY26", recompute_ga_musd=fy26))
    ann_rows.append(dict(scenario=scn, period="FY27", recompute_ga_musd=fy27))
ann_recompute = pd.DataFrame(ann_rows)
for scn, committed_scn in SCEN_MAP.items():
    for fy in ("FY26", "FY27"):
        mine = float(ann_recompute[(ann_recompute.scenario == scn) & (ann_recompute.period == fy)].recompute_ga_musd.iloc[0])
        theirs = float(annual[(annual.scenario == committed_scn) & (annual.period == fy)].ga_cash.iloc[0])
        check_rows.append(dict(check="vs_40_annual", scenario=scn, committed_scenario=committed_scn, quarter=fy,
                               recompute_musd=mine, committed_musd=theirs, abs_diff=abs(mine - theirs)))
check_df = pd.DataFrame(check_rows)
max_abs_diff = float(check_df.abs_diff.max())
check_df.to_csv(OUT / "c5_ga_line_recompute_check.csv", index=False)

# short annual (base dollars, short's own revenue path)
short_rev = {"3Q26": 4680.899996629618, "4Q26": 2965.8676775559734}   # from 40_short_case_quarterly.csv, scenario short_costs_at_budget
short_rev_fy27 = float(short_q.loc[Q_ORDER[2:], "revenue"].sum())
ga_base = recompute["base"]
short_fy26_rev = REV_1H26 + short_rev["3Q26"] + short_rev["4Q26"]
short_fy27_rev = short_rev_fy27
short_fy26_ga = GA_CASH_1H26_ACTUAL + ga_base["3Q26"] + ga_base["4Q26"]
short_fy27_ga = sum(ga_base[q] for q in Q_ORDER[2:])

# ----------------------------------------------------------------------------------------------
# Scenario table for the dossier's 2a block: base, short, breaker(=cost_bull), all periods.
# ----------------------------------------------------------------------------------------------
scen_rows = []
rev_lookup = lines.set_index(["scenario", "quarter"])["revenue"]
for label, scn, ga_map, rev_map in (
    ("base", "base", recompute["base"], {q: float(rev_lookup[("base", q)]) for q in Q_ORDER}),
    ("short", "short_costs_at_budget", recompute["base"], {q: float(short_q.loc[q, "revenue"]) for q in Q_ORDER}),
    ("breaker", "cost_bull", recompute["bull"], {q: float(rev_lookup[("cost_bull", q)]) for q in Q_ORDER}),
):
    for q in Q_ORDER:
        g, r = ga_map[q], rev_map[q]
        scen_rows.append(dict(scenario=label, period=q, ga_musd=g, revenue_musd=r, ga_pct_rev=g / r * 100))
    if label == "base":
        fy26_ga, fy27_ga = ann_recompute[(ann_recompute.scenario == "base") & (ann_recompute.period == "FY26")].recompute_ga_musd.iloc[0], \
                           ann_recompute[(ann_recompute.scenario == "base") & (ann_recompute.period == "FY27")].recompute_ga_musd.iloc[0]
        fy26_rev = float(annual[(annual.scenario == "base") & (annual.period == "FY26")].revenue.iloc[0])
        fy27_rev = float(annual[(annual.scenario == "base") & (annual.period == "FY27")].revenue.iloc[0])
    elif label == "short":
        fy26_ga, fy27_ga, fy26_rev, fy27_rev = short_fy26_ga, short_fy27_ga, short_fy26_rev, short_fy27_rev
    else:
        fy26_ga = ann_recompute[(ann_recompute.scenario == "bull") & (ann_recompute.period == "FY26")].recompute_ga_musd.iloc[0]
        fy27_ga = ann_recompute[(ann_recompute.scenario == "bull") & (ann_recompute.period == "FY27")].recompute_ga_musd.iloc[0]
        fy26_rev = float(annual[(annual.scenario == "cost_bull") & (annual.period == "FY26")].revenue.iloc[0])
        fy27_rev = float(annual[(annual.scenario == "cost_bull") & (annual.period == "FY27")].revenue.iloc[0])
    scen_rows.append(dict(scenario=label, period="FY26", ga_musd=fy26_ga, revenue_musd=fy26_rev, ga_pct_rev=fy26_ga / fy26_rev * 100))
    scen_rows.append(dict(scenario=label, period="FY27", ga_musd=fy27_ga, revenue_musd=fy27_rev, ga_pct_rev=fy27_ga / fy27_rev * 100))
scen_df = pd.DataFrame(scen_rows)
scen_df.to_csv(OUT / "c5_ga_scenarios.csv", index=False)

# ----------------------------------------------------------------------------------------------
# History basis check: 4Q23 ga_cash_ex_lodging vs ga_gaap (DEC-0003 reconciling line)
# ----------------------------------------------------------------------------------------------
hist = pan.loc["4Q23", ["ga_gaap", "sbc_ga", "ga_cash", "ga_cash_ex_lodging", "lodging_tax_reserves", "revenue"]]
hist_df = pd.DataFrame([dict(item="ga_cash_ex_lodging_musd", scenario="actual", period="4Q23", point=float(hist["ga_cash_ex_lodging"])),
                       dict(item="ga_gaap_musd", scenario="actual", period="4Q23", point=float(hist["ga_gaap"])),
                       dict(item="ga_cash_musd (gaap less sbc, incl. reserve)", scenario="actual", period="4Q23", point=float(hist["ga_cash"])),
                       dict(item="sbc_ga_musd", scenario="actual", period="4Q23", point=float(hist["sbc_ga"])),
                       dict(item="lodging_tax_reserves_musd", scenario="actual", period="4Q23", point=float(hist["lodging_tax_reserves"]))])
hist_df.to_csv(OUT / "c5_ga_history_basis_check.csv", index=False)

print("=== max abs diff across all recompute-vs-committed checks (USD m) ===")
print(max_abs_diff)
print(check_df.to_string(index=False))
print("\n=== scenario table ===")
print(scen_df.round(3).to_string(index=False))
print("\n=== 4Q23 history basis check ===")
print(hist_df.to_string(index=False))
assert max_abs_diff < 1e-6, f"recompute does not match committed values: max abs diff {max_abs_diff}"
print("\nOK: independent recompute matches all committed 40_line_build G&A cells to < 1e-6 USD m.")
