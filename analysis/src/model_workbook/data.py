"""Assembles the frames the core tabs share (history, scenario forecasts, revenue path, consensus, guide items).
Everything is read from data/processed; nothing is typed in here except labels and the scenario map."""
from __future__ import annotations
from functools import lru_cache
import pandas as pd
import numpy as np
from style import read

HIST_Q = ["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
          "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
FC_Q = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
ALL_Q = HIST_Q + FC_Q

# display name -> (csv scenario key, source)
SCENARIOS = {
    "Base (team model)": "base",
    "Short case: costs at budget (PITCH)": "short_costs_at_budget",
    "Short case: with 4Q26 marketing cut": "short_with_q4_marketing_cut",
    "Evidence-only costs (upside)": "evidence_only",
    "Revenue bear": "rev_bear",
    "Revenue bull": "rev_bull",
    "Cost bear": "cost_bear",
    "Cost bull": "cost_bull",
    "Both bear": "both_bear",
    "Both bull": "both_bull",
}
SCEN_KEYS = list(SCENARIOS.values())

# IS line items carried in the Scenarios block, in order (csv column -> label)
LINES = [
    ("nights_m", "Nights & seats booked (m)"),
    ("gbv_busd", "Gross booking value ($bn)"),
    ("bookings_m", "Bookings (m)"),
    ("revenue", "Revenue"),
    ("cor_cash", "Cost of revenue (cash)"),
    ("ops_cash", "Operations & support (cash)"),
    ("pd_cash", "Product development (cash)"),
    ("sm_cash", "Sales & marketing (cash)"),
    ("ga_cash", "General & administrative (cash)"),
    ("total_cash_costs", "Total cash costs"),
    ("da", "Depreciation & amortisation"),
    ("adj_ebitda", "Adjusted EBITDA"),
    ("sbc", "Stock-based compensation"),
    ("op_income", "Operating income (GAAP)"),
    ("interest_income", "Interest income"),
    ("interest_expense", "Interest expense"),
    ("other_income", "Other income / (expense), net"),
    ("pretax", "Pre-tax income"),
    ("tax", "Income tax provision"),
    ("net_income", "Net income"),
    ("diluted_shares_m", "Diluted shares (m)"),
    ("eps", "Diluted EPS ($)"),
    # cost detail
    ("cor_fees", "  Merchant / payment fees"),
    ("cor_chargebacks", "  Chargebacks"),
    ("cor_hosting", "  Hosting"),
    ("cor_other", "  Other cost of revenue"),
    ("ops_variable", "  Ops: variable (AI-addressable)"),
    ("ops_fixed", "  Ops: fixed / payroll"),
    ("sm_marketing", "  S&M: brand + performance marketing"),
    ("sm_field", "  S&M: field operations & policy"),
    ("ops_per_booking", "  Ops & support per booking ($)"),
    ("merchant_fee_rate_q_pct", "  Merchant fee rate (% of GBV)"),
    ("etr_pct", "  Effective tax rate (%)"),
]


@lru_cache(maxsize=None)
def scenario_quarterly() -> pd.DataFrame:
    """Long frame: scenario, quarter, <line columns> for all 10 scenarios x 6 quarters."""
    L = read("margin_build/40_line_build/40_lines_quarterly.csv")
    S = read("margin_build/40_line_build/40_short_case_quarterly.csv")
    summ = read("margin_build/40_line_build/40_short_case_summary.csv")
    cut = float(summ.loc[summ.case == "short_with_q4_marketing_cut", "q4_marketing_cut_musd"].iloc[0])
    S2 = S.copy()
    S2["scenario"] = "short_with_q4_marketing_cut"
    m = S2.quarter == "4Q26"
    etr = S2.loc[m, "etr_pct"] / 100.0
    for c in ["sm_marketing", "sm_cash", "total_cash_costs"]:
        S2.loc[m, c] = S2.loc[m, c] - cut
    for c in ["adj_ebitda", "op_income", "pretax"]:
        S2.loc[m, c] = S2.loc[m, c] + cut
    S2.loc[m, "tax"] = S2.loc[m, "pretax"] * etr
    S2.loc[m, "net_income"] = S2.loc[m, "pretax"] - S2.loc[m, "tax"]
    S2.loc[m, "eps"] = S2.loc[m, "net_income"] / S2.loc[m, "diluted_shares_m"]
    S2.loc[m, "adj_ebitda_margin_pct"] = S2.loc[m, "adj_ebitda"] / S2.loc[m, "revenue"] * 100
    S2.loc[m, "sm_cash_pct_rev"] = S2.loc[m, "sm_cash"] / S2.loc[m, "revenue"] * 100
    S2.loc[m, "total_cash_costs_pct_rev"] = S2.loc[m, "total_cash_costs"] / S2.loc[m, "revenue"] * 100
    out = pd.concat([L, S, S2], ignore_index=True)
    return out


@lru_cache(maxsize=None)
def history_quarterly() -> pd.DataFrame:
    """Quarterly actuals 1Q23-2Q26 with the same column names as the scenario frame where possible."""
    p = read("margin_build/02_financial_panel/02_panel_quarterly.csv")
    h = read("abnb_driver_history_quarterly.csv")
    p = p[p.quarter.isin(HIST_Q)].set_index("quarter")
    h = h[h.quarter.isin(HIST_Q)].set_index("quarter")
    df = pd.DataFrame(index=HIST_Q)
    df["nights_m"] = h["nights_m"]
    df["gbv_busd"] = h["gbv_b"]
    df["adr_usd"] = h["adr"]
    df["revenue"] = p["revenue"]
    for c in ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "total_cash_costs", "da",
              "interest_income", "interest_expense", "pretax_income", "tax_provision", "net_income",
              "eps_diluted", "shares_diluted_m", "sbc_total_is", "op_income", "other_income_expense",
              "cor_gaap", "ops_gaap", "pd_gaap", "sm_gaap", "ga_gaap", "lodging_tax_reserves"]:
        df[c] = p[c]
    df["adj_ebitda"] = h["adj_ebitda_musd"]
    df["fcf"] = h["fcf_musd"]
    df["buybacks"] = h["buybacks_musd"]
    df["take_rate_pct"] = h["take_rate_calc_pct"]
    # G&A on the ex-lodging-reserve basis (management adds the reserves back), and the total re-summed on that basis
    df["ga_cash_incl_lodging"] = df["ga_cash"]
    df["ga_cash"] = p["ga_cash_ex_lodging"]
    df["total_cash_costs"] = df[["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]].sum(axis=1)
    df = df.rename(columns={"pretax_income": "pretax", "tax_provision": "tax", "eps_diluted": "eps",
                            "shares_diluted_m": "diluted_shares_m", "sbc_total_is": "sbc",
                            "other_income_expense": "other_income"})
    # stack identity: adj EBITDA = revenue - cash costs + D&A (cash lines include D&A); the residual is other add-backs
    df["stack_ebitda"] = df["revenue"] - df["total_cash_costs"] + df["da"]
    df["other_addbacks"] = df["adj_ebitda"] - df["stack_ebitda"]
    df["gaap_other"] = df["op_income"] - (df["adj_ebitda"] - df["da"] - df["sbc"])
    return df


@lru_cache(maxsize=None)
def history_annual() -> pd.DataFrame:
    a = read("margin_build/02_financial_panel/02_panel_annual.csv")
    a = a[a.year.isin([2022, 2023, 2024, 2025])].set_index("year")
    h = read("abnb_driver_history_quarterly.csv")
    h["year"] = h.quarter.str[-2:].astype(int) + 2000
    fcf = h.groupby("year")["fcf_musd"].sum()
    bb = h.groupby("year")["buybacks_musd"].sum()
    df = pd.DataFrame(index=a.index)
    df["nights_m"] = a["nights_m"]; df["gbv_busd"] = a["gbv_busd"]; df["revenue"] = a["revenue"]
    for c in ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "total_cash_costs", "da", "op_income",
              "interest_income", "interest_expense", "other_income_expense", "pretax_income", "tax_provision",
              "net_income", "sbc_total_is", "cfo", "capex", "fcf_reported"]:
        df[c] = a[c]
    df["adj_ebitda"] = a["adj_ebitda_reported"]
    df["ga_cash"] = a["ga_cash_ex_lodging"]
    df["total_cash_costs"] = df[["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]].sum(axis=1)
    df = df.rename(columns={"pretax_income": "pretax", "tax_provision": "tax", "sbc_total_is": "sbc",
                            "other_income_expense": "other_income"})
    df["buybacks"] = bb.reindex(df.index)
    df["stack_ebitda"] = df["revenue"] - df["total_cash_costs"] + df["da"]
    df["other_addbacks"] = df["adj_ebitda"] - df["stack_ebitda"]
    df["gaap_other"] = df["op_income"] - (df["adj_ebitda"] - df["da"] - df["sbc"])
    df.index = [f"FY{y-2000}" for y in df.index]
    return df


@lru_cache(maxsize=None)
def revenue_path() -> pd.DataFrame:
    """Wide: index line, columns quarter, for scenario in base/bear/bull (06 v2b path = bridge v3 for 2H26)."""
    p = read("margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv")
    return p


def revenue_path_wide(scenario: str) -> pd.DataFrame:
    p = revenue_path()
    w = p[p.scenario == scenario].pivot(index="line", columns="quarter", values="value")
    return w


@lru_cache(maxsize=None)
def fx_schedule() -> pd.DataFrame:
    return read("overnight/05_fx_schedule.csv")


@lru_cache(maxsize=None)
def consensus() -> dict:
    cur = read("margin_build/03_consensus_pit/03_current_consensus.csv")
    lseg = cur[cur.vendor == "LSEG"].set_index("period")
    vs = read("margin_build/23_final_model/23_vs_consensus.csv").set_index("period")
    bbg = read("reverse_dcf/E/E_street_distribution_vs_team.csv")
    return {"lseg": lseg, "vs": vs, "bbg": bbg}


@lru_cache(maxsize=None)
def bridge() -> dict:
    return {
        "proj": read("h2_bridge_v3/h2_bridge_2026_projection.csv").set_index("metric"),
        "rev": read("h2_bridge_v3/h2_bridge_revenue_dollars.csv").set_index("quarter"),
        "lines": read("h2_bridge_v3/h2_bridge_v3_rebased_lines.csv"),
        "fx": read("h2_bridge_v3/h2_bridge_v3_fx_line.csv"),
        "nights": read("h2_bridge_v3/h2_bridge_nights_scenarios.csv"),
        "guide_hist": read("abnb_revenue_guidance_vs_actual.csv"),
    }


@lru_cache(maxsize=None)
def margin_build() -> dict:
    return {
        "card": read("margin_build/23_final_model/23_card_5nov.csv"),
        "annual": read("margin_build/40_line_build/40_annual.csv"),
        "params": read("margin_build/40_line_build/40_params.csv"),
        "sens": read("margin_build/40_line_build/40_sensitivities.csv"),
        "sentence": read("margin_build/40_line_build/40_sentence_implied.csv"),
        "backcast": read("margin_build/40_line_build/40_backcast.csv"),
        "short_summary": read("margin_build/40_line_build/40_short_case_summary.csv"),
        "short_stress": read("margin_build/40_line_build/40_short_case_stress.csv"),
        "short_path": read("margin_build/40_line_build/40_short_case_revenue_path.csv"),
        "identity": read("margin_build/23_final_model/23_card_budget_identity.csv"),
        "floor": read("margin_build/23_final_model/23_fy26_floor_breakeven.csv"),
        "m3_q4": read("margin_build/M3_guide_policy_margin/M3_q4_implied_live_5nov.csv"),
        "cushion": read("margin_build/M3_guide_policy_margin/M3_cushion_history.csv"),
        "run_vs_line": read("margin_build/40_line_build/40_vs_run_and_street.csv"),
        "fc_annual_run": read("margin_build/23_final_model/23_forecast_annual.csv"),
        "seasonality": read("margin_build/23_final_model/23_seasonality.csv"),
        "macro": read("margin_build/23_final_model/23_macro_sensitivity.csv"),
    }


def short_case_annual() -> pd.DataFrame:
    """FY26/FY27 for the two short cases: 1H26 actual + forecast quarters."""
    sq = scenario_quarterly()
    hist = history_quarterly()
    rows = {}
    for key in ["short_costs_at_budget", "short_with_q4_marketing_cut"]:
        s = sq[sq.scenario == key].set_index("quarter")
        cols = ["revenue", "adj_ebitda", "net_income", "sbc", "total_cash_costs", "sm_cash", "cor_cash",
                "ops_cash", "pd_cash", "ga_cash", "nights_m", "gbv_busd"]
        fy26 = {c: hist.loc[["1Q26", "2Q26"], c].sum() + s.loc[["3Q26", "4Q26"], c].sum() for c in cols}
        fy27 = {c: s.loc[["1Q27", "2Q27", "3Q27", "4Q27"], c].sum() for c in cols}
        for per, d in [("FY26", fy26), ("FY27", fy27)]:
            d["adj_ebitda_margin_pct"] = d["adj_ebitda"] / d["revenue"] * 100
            rows[(key, per)] = d
    return pd.DataFrame(rows).T
