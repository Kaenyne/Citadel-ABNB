"""
C7 scratch recompute (read-only): independently re-derive the below-EBITDA schedule
(SBC, D&A, interest income, interest expense, other income, tax, diluted shares, EPS)
from the M7 parameter sheet and the committed 40_line_build / 40_short_case outputs,
and check the result against the committed net_income / eps cells.

HARD CONSTRAINT (C7 brief): does NOT run analysis/src/margin_build/M7_below_ebitda/run.py,
analysis/src/margin_build/40_line_build/run.py, or any other M1-M7 / 23_final_model / 40_line_build
script. It only reads already-committed CSVs (M7_parameter_sheet.csv; 40_lines_quarterly.csv,
40_annual.csv, 40_short_case_quarterly.csv, 40_short_case_summary.csv; 02_panel_quarterly.csv)
and re-implements the identity documented in analysis/src/margin_build/40_line_build/run.py
lines 180-188 (read, not executed) purely in this new script.

Identity used (matches 40_line_build/run.py exactly):
  op_income   = adj_ebitda - D&A - SBC                              (lodging_reserves_fwd = 0 forward, cancels)
  interest_income = beta * (tbill_3m/100) * (cash_plus_sti + avg(funds_held_this_q, funds_held_prev_q)) / 4
                    funds_held_this_q = funds_held[q-4] * (gbv_now / gbv[q-4]) * (1 - rnpl_share_shift_pts/100)
  pretax      = op_income + interest_income - interest_expense + other_income
  net_income  = pretax * (1 - ETR)
  eps         = net_income / diluted_shares_m                       (diluted_shares_m walks +delta_per_q from 597.0m at 2Q26)

Also computes FY26 short-case EPS, which 40_short_case_summary.csv does not publish (it only
publishes q3_eps and fy27_eps for the short case), using the same H1-actual + build-quarters
annual formula as 40_line_build/run.py lines 219-235 (read, not executed).

Outputs (this folder): c7_recompute_quarterly.csv, c7_recompute_annual.csv, c7_recompute_check.csv
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
M7 = pd.read_csv(ROOT / "data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv").set_index("name")["value"]
PAN = pd.read_csv(ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv").set_index("quarter")
LINES_Q = pd.read_csv(ROOT / "data/processed/margin_build/40_line_build/40_lines_quarterly.csv")
ANNUAL = pd.read_csv(ROOT / "data/processed/margin_build/40_line_build/40_annual.csv")
SHORT_Q = pd.read_csv(ROOT / "data/processed/margin_build/40_line_build/40_short_case_quarterly.csv")
SHORT_SUM = pd.read_csv(ROOT / "data/processed/margin_build/40_line_build/40_short_case_summary.csv")

def f(x):
    return float(M7[x])

BETA = f("interest_income_beta")
TBILL = 3.76  # 40_line_build/run.py prm("below","tbill_3m",3.76,...) rounds M7's tbill_3m_3q26_hat (3.762380952380953) to 3.76 -- read, matched to 40_params.csv row, not the unrounded M7 cell
CASH_STI = f("cash_plus_sti_2q26")
INT_EXP_Q = f("interest_expense_musd_q")  # 37.0, matches 40_params.csv "interest_expense_per_q" exactly
OTHER_INC_Q = 3.7  # 40_line_build/run.py prm("below","other_income_per_q",3.7,...) rounds M7's other_income_musd_q (3.707412112603224) to 3.7 -- read, matched to 40_params.csv row
ETR_FY26 = 18.0  # 40_params.csv below|etr_2h26 (M7's own etr_fy26 row, 18.0, matches)
ETR_FY27 = 17.5  # 40_params.csv below|etr_fy27
SHARES_2Q26 = f("diluted_shares_2q26")
DELTA_PER_Q = f("diluted_shares_delta_m_q")

PREV = {"3Q26": "3Q25", "4Q26": "4Q25"}
QUARTERS = ["3Q26", "4Q26"]

# diluted share count walk (scenario-independent in the committed build: verified below)
shares = {}
s = SHARES_2Q26
for q in QUARTERS:
    s = s + DELTA_PER_Q
    shares[q] = s

def interest_income_path(gbv_now: dict, rnpl_share_shift_pts: float):
    """Reproduce run.py's interest-income recursion (lines 182-185) for 3Q26/4Q26 only."""
    fh_last = float(PAN.loc["2Q26", "funds_held_on_behalf"]) * (1 - rnpl_share_shift_pts / 100)
    out = {}
    for q in QUARTERS:
        pq = PREV[q]
        fh_unshifted = float(PAN.loc[pq, "funds_held_on_behalf"]) * (gbv_now[q] / float(PAN.loc[pq, "gbv_busd"]))
        fh = fh_unshifted * (1 - rnpl_share_shift_pts / 100)
        out[q] = BETA * TBILL / 100 * (CASH_STI + (fh + fh_last) / 2) / 4
        fh_last = fh
    return out

rows = []
checks = []

def recompute_scenario(label, ebitda: dict, da: dict, sbc: dict, gbv: dict, rnpl_shift: float,
                        committed_ni: dict, committed_eps: dict, committed_int_inc: dict):
    int_inc = interest_income_path(gbv, rnpl_shift)
    for q in QUARTERS:
        op_inc = ebitda[q] - da[q] - sbc[q]
        pretax = op_inc + int_inc[q] - INT_EXP_Q + OTHER_INC_Q
        etr = ETR_FY26
        ni = pretax * (1 - etr / 100)
        eps = ni / shares[q]
        rows.append(dict(scenario=label, quarter=q, adj_ebitda=ebitda[q], da=da[q], sbc=sbc[q],
                          interest_income_recomputed=int_inc[q], interest_income_committed=committed_int_inc[q],
                          op_income=op_inc, pretax=pretax, etr_pct=etr, net_income_recomputed=ni,
                          net_income_committed=committed_ni[q], diluted_shares_m=shares[q],
                          eps_recomputed=eps, eps_committed=committed_eps[q]))
        checks.append(dict(scenario=label, quarter=q, cell="interest_income",
                            diff=int_inc[q] - committed_int_inc[q]))
        checks.append(dict(scenario=label, quarter=q, cell="net_income", diff=ni - committed_ni[q]))
        checks.append(dict(scenario=label, quarter=q, cell="eps", diff=eps - committed_eps[q]))

# --- base ---
b = LINES_Q[(LINES_Q.scenario == "base") & (LINES_Q.quarter.isin(QUARTERS))].set_index("quarter")
recompute_scenario("base",
                    ebitda=b["adj_ebitda"].to_dict(), da=b["da"].to_dict(), sbc=b["sbc"].to_dict(),
                    gbv=b["gbv_busd"].to_dict(), rnpl_shift=0.0,
                    committed_ni=b["net_income"].to_dict(), committed_eps=b["eps"].to_dict(),
                    committed_int_inc=b["interest_income"].to_dict())

# --- breaker (cost_bull, base revenue path) ---
k = LINES_Q[(LINES_Q.scenario == "cost_bull") & (LINES_Q.quarter.isin(QUARTERS))].set_index("quarter")
recompute_scenario("breaker_cost_bull",
                    ebitda=k["adj_ebitda"].to_dict(), da=k["da"].to_dict(), sbc=k["sbc"].to_dict(),
                    gbv=k["gbv_busd"].to_dict(), rnpl_shift=0.0,
                    committed_ni=k["net_income"].to_dict(), committed_eps=k["eps"].to_dict(),
                    committed_int_inc=k["interest_income"].to_dict())

# --- short (short_costs_at_budget; rnpl_share_shift_pts overlay = 10.0) ---
sc = SHORT_Q[SHORT_Q.quarter.isin(QUARTERS)].set_index("quarter")
recompute_scenario("short_costs_at_budget",
                    ebitda=sc["adj_ebitda"].to_dict(), da=sc["da"].to_dict(), sbc=sc["sbc"].to_dict(),
                    gbv=sc["gbv_busd"].to_dict(), rnpl_shift=10.0,
                    committed_ni=sc["net_income"].to_dict(), committed_eps=sc["eps"].to_dict(),
                    committed_int_inc=sc["interest_income"].to_dict())

pd.DataFrame(rows).to_csv(Path(__file__).parent / "c7_recompute_quarterly.csv", index=False)
check_df = pd.DataFrame(checks)
check_df.to_csv(Path(__file__).parent / "c7_recompute_check.csv", index=False)
print(check_df.assign(abs_diff=check_df["diff"].abs()).groupby(["scenario", "cell"])["abs_diff"].max().to_string())
max_abs = check_df["diff"].abs().max()
print(f"\nMax abs diff across all scenario/quarter/cell recomputations: {max_abs:.6e}")

# ------------------------------------------------------------------------------------------------
# FY26 / FY27 annual EPS, incl. the short-case FY26 EPS that 40_short_case_summary.csv does not publish
# ------------------------------------------------------------------------------------------------
h1 = PAN.loc[["1Q26", "2Q26"]]
h1_ni = float(h1["net_income"].sum())
h1_sh = float(h1["shares_diluted_m"].mean())

ann_rows = []

def annual_row(label, ni_36_46, sh_36_46):
    fy26_ni = h1_ni + ni_36_46["3Q26"] + ni_36_46["4Q26"]
    fy26_sh = (h1_sh + (sh_36_46["3Q26"] + sh_36_46["4Q26"]) / 2) / 2
    fy26_eps = fy26_ni / fy26_sh
    ann_rows.append(dict(scenario=label, period="FY26", net_income=fy26_ni, diluted_shares_m=fy26_sh, eps_recomputed=fy26_eps))

annual_row("base", b["net_income"].to_dict(), b["diluted_shares_m"].to_dict())
annual_row("breaker_cost_bull", k["net_income"].to_dict(), k["diluted_shares_m"].to_dict())
annual_row("short_costs_at_budget", sc["net_income"].to_dict(), sc["diluted_shares_m"].to_dict())

ann_check = ANNUAL[(ANNUAL.period == "FY26") & (ANNUAL.scenario.isin(["base", "cost_bull"]))].set_index("scenario")
for label, committed_key in (("base", "base"), ("breaker_cost_bull", "cost_bull")):
    row = next(r for r in ann_rows if r["scenario"] == label)
    row["eps_committed"] = float(ann_check.loc[committed_key, "eps"])
    row["net_income_committed"] = float(ann_check.loc[committed_key, "net_income"])

# short-case FY26: not published anywhere in the repo; this is new
short_fy26 = next(r for r in ann_rows if r["scenario"] == "short_costs_at_budget")
short_fy26["eps_committed"] = None
short_fy26["net_income_committed"] = None

pd.DataFrame(ann_rows).to_csv(Path(__file__).parent / "c7_recompute_annual.csv", index=False)
print("\n=== Annual (FY26) ===")
print(pd.DataFrame(ann_rows).to_string(index=False))

TOL = 0.01  # USD m / USD per share; the identity should reproduce the committed cells to float precision
assert max_abs < TOL, f"recompute exceeds tolerance: {max_abs}"
print(f"\nPASS: all recomputed cells match committed 40_line_build / 40_short_case cells within {TOL}")

