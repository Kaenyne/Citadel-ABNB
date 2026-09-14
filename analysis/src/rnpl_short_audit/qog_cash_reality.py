"""Quality-of-growth object 2: the cash-reality panel.

Builds the quarterly (1Q21-2Q26) and annual (FY21-FY25) cash panel that separates
what Airbnb *collects* from what it *reports*, isolates the RNPL transition effect,
sizes the permanent 2027 effects, and states the 5 November test.

Run from the repo root:
    python analysis/src/rnpl_short_audit/qog_cash_reality.py

Reads (read-only):
    data/processed/overnight/02_kpi_panel_quarterly.csv   - revenue, adj EBITDA, SBC, CFO, capex,
                                                            FCF, balance-sheet stocks, nights, GBV
    data/processed/abnb_fcf_bridge.csv                    - quarterly interest income (verified
                                                            against the 10-K/10-Q below)
Writes (new files only):
    data/processed/rnpl_short_audit/qog_cash_reality_quarterly.csv
    data/processed/rnpl_short_audit/qog_cash_reality_annual.csv
    data/processed/rnpl_short_audit/qog_cash_reality_seasonality.csv
    data/processed/rnpl_short_audit/qog_cash_reality_transition.csv
    data/processed/rnpl_short_audit/qog_cash_reality_bridge_2027.csv
    data/processed/rnpl_short_audit/qog_cash_reality_exhibit.csv
    data/processed/rnpl_short_audit/qog_cash_reality_3q26_test.csv
    data/processed/rnpl_short_audit/qog_cash_reality_filing_facts.csv

No network. Nothing existing is modified.

Evidence labels on every number: measured / derived / assumed.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------------------
# 0. Paths
# --------------------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[3]
PANEL = REPO / "data" / "processed" / "overnight" / "02_kpi_panel_quarterly.csv"
BRIDGE = REPO / "data" / "processed" / "abnb_fcf_bridge.csv"
OUT = REPO / "data" / "processed" / "rnpl_short_audit"
OUT.mkdir(parents=True, exist_ok=True)

TENK = "data/raw/regulatory/quantification/abnb_2025_10k.json"
TENQ = "data/raw/regulatory/quantification/abnb_2026q2_10q.html"

# --------------------------------------------------------------------------------------
# 1. Filing facts, transcribed with their location. Verbatim quotes kept whole.
# --------------------------------------------------------------------------------------

FILING_FACTS = [
    dict(
        fact="FCF definition / float exclusion",
        value="CFO less purchases of property and equipment",
        label="measured",
        source=f"{TENK} p.43, Item 7, 'Free Cash Flow Reconciliation'",
        quote=(
            "Our FCF is impacted by the timing of GBV because we collect our service fees at the "
            "time of booking, which is generally before a stay, experience, or service occurs. "
            "Funds held on behalf of our customers and amounts payable to our customers do not "
            "impact FCF, except interest earned on these funds."
        ),
    ),
    dict(
        fact="FCF definition, RNPL amendment",
        value="same definition; RNPL named as a timing shift",
        label="measured",
        source=f"{TENQ} Part I Item 2, 'Free Cash Flow Reconciliation'",
        quote=(
            "Our FCF is impacted by the timing of GBV, as we generally collect our service fees at "
            "booking, which typically occurs before a stay, experience, or service. For bookings "
            "under RNPL, we collect payment closer to the date of stay. The continued expansion of "
            "RNPL results in a shift in timing of when cash for unearned fees is received, which "
            "impacts our FCF. Funds held on behalf of customers and amounts payable to customers "
            "do not impact FCF, except for interest earned on those funds."
        ),
    ),
    dict(
        fact="Seasonality of FCF",
        value="Q1 highest, Q4 lowest",
        label="measured",
        source=f"{TENQ} Part I Item 2, 'Seasonality'",
        quote=(
            "Seasonality in GBV also affects FCF. Unearned fees typically rise when GBV rises since "
            "guests pay at the time of booking. As such, FCF is typically highest in the first "
            "quarter and lowest in the fourth quarter. However, increasing adoption of RNPL, which "
            "shifts payment and unearned fees closer to the date of stay, is changing the typical "
            "seasonal dynamics between GBV and FCF."
        ),
    ),
    dict(
        fact="RNPL cash mechanics",
        value="no unearned fees, no operating cash flow until payment",
        label="measured",
        source=f"{TENQ} Part I Item 2, 'Liquidity and Capital Resources'",
        quote=(
            "This reflected unearned fees growing at a rate less than the GBV growth rate during "
            "the six months ended June 30, 2026, compared to the same period in the prior year, "
            "which was primarily due to the increased guest adoption of our flexible payment "
            "options, which allow guests to pay closer to check-in dates rather than at time of "
            "booking, shifting the timing of cash collection and its recognition in operating "
            "activities. For example, under our RNPL option, payment is collected closer to "
            "check-in rather than at booking. Accordingly, unearned fees are not recorded, and "
            "operating cash flows are not generated until payment is received."
        ),
    ),
    dict(
        fact="Interest income, composition",
        value="FY2023 $721m / FY2024 $818m / FY2025 $705m",
        label="measured",
        source=f"{TENK} p.46-47, Item 7, 'Interest Income'; income statement p.55",
        quote=(
            "Interest income consists primarily of interest earned on our cash, cash equivalents, "
            "marketable securities, and amounts held on behalf of customers."
        ),
    ),
    dict(
        fact="Interest income, 2Q26",
        value="2Q26 $183m vs 2Q25 $190m; 1H26 $338m vs 1H25 $363m",
        label="measured",
        source=f"{TENQ} Part I Item 2, 'Interest Income'",
        quote=(
            "Interest income decreased by $7 million, or 4%, and $25 million, or 7%, respectively, "
            "primarily due to lower interest earned on our investment portfolio, driven by lower "
            "interest rates, partially offset by a slight increase in interest income on operating "
            "cash."
        ),
    ),
    dict(
        fact="Payment-processing cost share",
        value="merchant fees and chargebacks FY2023 $1,369m / FY2024 $1,508m / FY2025 $1,666m",
        label="measured",
        source=f"{TENK} p.85, Note 16 segment table, 'Merchant fees and chargebacks'",
        quote=(
            "Cost of revenue includes payment processing costs, including merchant fees and "
            "chargebacks, costs associated with third-party data centers used to host our "
            "platform, and amortization of internally developed software and acquired technology. "
            "As the merchant of record, we bear all payment processing costs for our bookings, "
            "including those from chargebacks due to both fraud and non-fraud activities."
        ),
    ),
    dict(
        fact="Merchant fee driver",
        value="FY2025 cost of revenue +$208m, of which +$188m merchant fees",
        label="measured",
        source=f"{TENK} p.45, Item 7, 'Cost of Revenue'",
        quote=(
            "Cost of revenue increased $208 million, or 11%, primarily due to a $188 million "
            "increase in merchant fees, due to higher pay-in volumes, a $28 million increase in "
            "amortization costs related to capitalized internal-use software projects, and a $27 "
            "million increase in data hosting services. These increases were partially offset by a "
            "reduction in chargebacks of $29 million and a reduction in other service costs of $12 "
            "million, which includes authentication, translation, and SMS services."
        ),
    ),
    dict(
        fact="Refunds, size",
        value="variable-consideration estimate immaterial at 31 Dec 2024 and 2025",
        label="measured",
        source=f"{TENK} p.63, Note 2, 'Refunds'",
        quote=(
            "The Company accounts for refunds, net of any recoveries, as variable consideration, "
            "which results in a reduction to revenue. ... The estimate for variable consideration "
            "was immaterial as of December 31, 2024 and 2025."
        ),
    ),
    dict(
        fact="Single-fee migration, cash treatment",
        value="host fee is collected at booking under BOTH structures; no incremental float",
        label="measured",
        source=f"{TENK} pp.62-63, Note 2, 'Revenue Recognition' and 'Funds Receivable and Funds Payable'",
        quote=(
            "For all bookings, the guest pays the booking amount to the Company, which disburses "
            "the booking amount to the host after check-in, net of the host's service fees. ... "
            "The Company records guest payments, net of service fees, as funds receivable and "
            "amounts held on behalf of customers with a corresponding amount in funds payable and "
            "amounts payable to customers when cash is received in advance of check-in. Host and "
            "guest fees are recorded as cash with a corresponding amount in unearned fees."
        ),
    ),
    dict(
        fact="Customer-funds yield",
        value="NOT DISCLOSED - no separate yield on amounts held on behalf of customers",
        label="assumed",
        source=f"{TENK} p.46-47 (interest income is presented as one line only)",
        quote=(
            "Interest income consists primarily of interest earned on our cash, cash equivalents, "
            "marketable securities, and amounts held on behalf of customers."
        ),
    ),
    dict(
        fact="RNPL cancellation rate",
        value="RNPL bookings have experienced higher cancellation rates",
        label="measured",
        source=f"{TENQ} Part I Item 2, 'Gross Booking Value'",
        quote=(
            "To date, RNPL bookings, which require no payment at the time of booking, have "
            "experienced higher cancellation rates than historic bookings in which some or all of "
            "the cash was received at the time of booking. As adoption of RNPL and our other "
            "flexible payment options continues to grow, the timing among GBV, revenue, and cash "
            "receipts may become less correlated."
        ),
    ),
]

# Cash-flow-statement "Unearned fees" line, where published, against the balance difference.
# Source: 10-Q condensed consolidated statements of cash flows; 10-K consolidated statements
# of cash flows. Used only as a reconciliation check on the balance-difference series.
UF_CASHFLOW_CHECK = [
    dict(period="FY2023", cf_line=242.0, source=f"{TENK} consolidated statements of cash flows"),
    dict(period="FY2024", cf_line=200.0, source=f"{TENK} consolidated statements of cash flows"),
    dict(period="FY2025", cf_line=122.0, source=f"{TENK} consolidated statements of cash flows"),
    dict(period="1H2025", cf_line=1236.0, source=f"{TENQ} condensed consolidated statements of cash flows"),
    dict(period="1H2026", cf_line=1085.0, source=f"{TENQ} condensed consolidated statements of cash flows"),
]

# Disclosed / repo-sourced scenario inputs for tasks 3 and 5.
GUIDE_3Q26_REV_LOW, GUIDE_3Q26_REV_HIGH = 4690.0, 4770.0   # measured: 2Q26 letter, guidance ledger
GUIDE_3Q26_REV_MID = 4730.0
REV_4Q26_BASE = 3111.0      # derived: data/processed/overnight/29_fy27_bridge.csv, base scenario
REV_FY27_BASE = 15842.0     # derived: data/processed/overnight/13_model_annual.csv, Base 2027
GBV_FY27_BASE = 118081.0    # derived: same file
GBV_TTM_2Q26 = 99700.0      # derived: KPI panel, 3Q25+4Q25+1Q26+2Q26
REV_1Q27_BASE = 2973.0      # derived: 1Q26 $2,678m grown at the FY27 base rate of +11.0%
REV_1Q28_BASE = 3300.0      # derived: 1Q27 grown at +11.0%

# RNPL share of GBV path. Measured history: ~20% 1Q26 (1Q26 letter, ledger D031),
# >20% 2Q26 (2Q26 call, ledger D043). Forward path is the study's assumed scenario grid.
RNPL_SHARE = {
    "2Q26_measured": 0.21,
    "central": {"3Q26": 0.22, "4Q26": 0.23, "FY27": 0.25},
    "bear": {"3Q26": 0.24, "4Q26": 0.27, "FY27": 0.30},
    "bull": {"3Q26": 0.21, "4Q26": 0.21, "FY27": 0.20},
}

PLATFORM_CANCEL_RATE = 0.17  # measured (hedged): 4Q25 call, ledger D017/D018, "16% to 17%"

# Pre-RNPL seasonal norm for the unearned-fees stock over NEXT-quarter revenue.
# Rebuilt below from the panel over pre-RNPL quarters and asserted against these pins.
NORM_PINS = {"1Q": 0.880, "2Q": 0.697, "3Q": 0.665, "4Q": 0.689}


# --------------------------------------------------------------------------------------
# 2. Panel
# --------------------------------------------------------------------------------------

def qkey(q: str) -> tuple[int, int]:
    return (int(q[2:]), int(q[0]))


def load_panel() -> pd.DataFrame:
    p = pd.read_csv(PANEL)
    b = pd.read_csv(BRIDGE)[["period", "interest_income", "fcf"]].rename(
        columns={"period": "quarter", "interest_income": "interest_income_musd",
                 "fcf": "fcf_bridge_musd"}
    )
    d = p.merge(b, on="quarter", how="left")
    d["_k"] = d["quarter"].map(qkey)
    d = d.sort_values("_k").drop(columns="_k").reset_index(drop=True)
    return d


def build_quarterly(d: pd.DataFrame) -> pd.DataFrame:
    o = pd.DataFrame()
    o["quarter"] = d["quarter"]
    o["qnum"] = d["quarter"].str[:2]
    for src, dst in [
        ("revenue_musd", "revenue_musd"),
        ("adj_ebitda_musd", "adj_ebitda_musd"),
        ("sbc_musd", "sbc_musd"),
        ("cfo_musd", "cfo_musd"),
        ("capex_musd", "capex_musd"),
        ("fcf_musd", "fcf_reported_musd"),
        ("unearned_fees_musd", "unearned_fees_musd"),
        ("funds_held_for_clients_musd", "funds_payable_musd"),
        ("cash_and_equivalents_musd", "cash_musd"),
        ("short_term_investments_musd", "st_investments_musd"),
        ("restricted_cash_musd", "restricted_cash_musd"),
        ("nights_m", "nights_m"),
        ("gbv_musd", "gbv_musd"),
        ("interest_income_musd", "interest_income_musd"),
        ("fcf_bridge_musd", "fcf_crosscheck_bridge_musd"),
    ]:
        o[dst] = d[src]

    # Cross-check the KPI panel's FCF against data/processed/abnb_fcf_bridge.csv, which ties to
    # the 10-K reconciliation. They agree exactly from 1Q23 on; 2021 diverges (see note, limits).
    o["fcf_crosscheck_delta_musd"] = o["fcf_reported_musd"] - o["fcf_crosscheck_bridge_musd"]

    # Change in unearned fees: balance difference. The cash-flow-statement line is the same
    # information (residual $3-8m over six quarters, see docs/rnpl-short-audit/04).
    o["d_unearned_fees_musd"] = o["unearned_fees_musd"].diff()

    # The two cash measures.
    o["fcf_exfloat_musd"] = o["cfo_musd"] - o["d_unearned_fees_musd"] - o["capex_musd"]
    o["fcf_less_sbc_musd"] = o["fcf_reported_musd"] - o["sbc_musd"]
    o["fcf_exfloat_less_sbc_musd"] = o["fcf_exfloat_musd"] - o["sbc_musd"]

    # Customer float and the interest it earns.
    o["customer_float_musd"] = o["funds_payable_musd"] + o["unearned_fees_musd"]
    o["interest_earning_balances_musd"] = (
        o["cash_musd"] + o["st_investments_musd"] + o["restricted_cash_musd"] + o["funds_payable_musd"]
    )
    avg_bal = (o["interest_earning_balances_musd"] + o["interest_earning_balances_musd"].shift(1)) / 2
    avg_float = (o["customer_float_musd"] + o["customer_float_musd"].shift(1)) / 2
    o["avg_interest_earning_balances_musd"] = avg_bal
    o["avg_customer_float_musd"] = avg_float
    o["implied_yield_annualised_pct"] = 100.0 * 4.0 * o["interest_income_musd"] / avg_bal
    o["customer_funds_share_of_balances_pct"] = 100.0 * avg_float / avg_bal
    o["interest_income_on_customer_funds_musd"] = o["interest_income_musd"] * (avg_float / avg_bal)

    # Conversion ratios.
    o["fcf_margin_pct"] = 100.0 * o["fcf_reported_musd"] / o["revenue_musd"]
    o["fcf_exfloat_margin_pct"] = 100.0 * o["fcf_exfloat_musd"] / o["revenue_musd"]
    o["fcf_to_adj_ebitda_pct"] = 100.0 * o["fcf_reported_musd"] / o["adj_ebitda_musd"]
    o["fcf_exfloat_to_adj_ebitda_pct"] = 100.0 * o["fcf_exfloat_musd"] / o["adj_ebitda_musd"]
    o["fcf_less_sbc_to_adj_ebitda_pct"] = 100.0 * o["fcf_less_sbc_musd"] / o["adj_ebitda_musd"]

    # Same-quarter y/y (the only comparison the seasonality permits).
    for c in [
        "nights_m", "gbv_musd", "revenue_musd", "adj_ebitda_musd",
        "fcf_reported_musd", "fcf_exfloat_musd", "unearned_fees_musd", "sbc_musd",
    ]:
        o[c.replace("_musd", "").replace("_m", "") + "_yoy_pct"] = 100.0 * (o[c] / o[c].shift(4) - 1.0)

    # Trailing four quarters.
    for c in ["revenue_musd", "adj_ebitda_musd", "fcf_reported_musd", "fcf_exfloat_musd"]:
        o["ttm_" + c] = o[c].rolling(4).sum()
    for c in ["revenue_musd", "adj_ebitda_musd", "fcf_reported_musd", "fcf_exfloat_musd"]:
        o["ttm_" + c.replace("_musd", "") + "_yoy_pct"] = 100.0 * (
            o["ttm_" + c] / o["ttm_" + c].shift(4) - 1.0
        )

    return o[o["quarter"].map(lambda q: qkey(q) >= (21, 1))].reset_index(drop=True)


def build_annual(q: pd.DataFrame, d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    uf = dict(zip(d["quarter"], d["unearned_fees_musd"]))
    for y in range(2021, 2026):
        sub = q[q["quarter"].str.endswith(str(y)[2:])]
        if len(sub) != 4:
            continue
        d_uf = uf[f"4Q{str(y)[2:]}"] - uf[f"4Q{str(y - 1)[2:]}"]
        cfo, capex = sub["cfo_musd"].sum(), sub["capex_musd"].sum()
        rows.append(
            dict(
                period=f"FY{y}",
                revenue_musd=sub["revenue_musd"].sum(),
                adj_ebitda_musd=sub["adj_ebitda_musd"].sum(),
                sbc_musd=sub["sbc_musd"].sum(),
                cfo_musd=cfo,
                capex_musd=capex,
                fcf_reported_musd=sub["fcf_reported_musd"].sum(),
                d_unearned_fees_musd=d_uf,
                fcf_exfloat_musd=cfo - d_uf - capex,
                interest_income_musd=sub["interest_income_musd"].sum(),
                interest_income_on_customer_funds_musd=sub["interest_income_on_customer_funds_musd"].sum(),
                avg_customer_float_musd=sub["avg_customer_float_musd"].mean(),
                implied_yield_annualised_pct=sub["implied_yield_annualised_pct"].mean(),
            )
        )
    # 1H26 memo row: the only RNPL-era period with a published cash-flow statement.
    h1 = q[q["quarter"].isin(["1Q26", "2Q26"])]
    h0 = q[q["quarter"].isin(["1Q25", "2Q25"])]
    for tag, sub in [("1H2025", h0), ("1H2026", h1)]:
        cfo, capex = sub["cfo_musd"].sum(), sub["capex_musd"].sum()
        d_uf = sub["d_unearned_fees_musd"].sum()
        rows.append(
            dict(
                period=tag,
                revenue_musd=sub["revenue_musd"].sum(),
                adj_ebitda_musd=sub["adj_ebitda_musd"].sum(),
                sbc_musd=sub["sbc_musd"].sum(),
                cfo_musd=cfo,
                capex_musd=capex,
                fcf_reported_musd=sub["fcf_reported_musd"].sum(),
                d_unearned_fees_musd=d_uf,
                fcf_exfloat_musd=cfo - d_uf - capex,
                interest_income_musd=sub["interest_income_musd"].sum(),
                interest_income_on_customer_funds_musd=sub["interest_income_on_customer_funds_musd"].sum(),
                avg_customer_float_musd=sub["avg_customer_float_musd"].mean(),
                implied_yield_annualised_pct=sub["implied_yield_annualised_pct"].mean(),
            )
        )
    a = pd.DataFrame(rows)
    a["fcf_less_sbc_musd"] = a["fcf_reported_musd"] - a["sbc_musd"]
    a["fcf_exfloat_less_sbc_musd"] = a["fcf_exfloat_musd"] - a["sbc_musd"]
    a["fcf_margin_pct"] = 100.0 * a["fcf_reported_musd"] / a["revenue_musd"]
    a["fcf_exfloat_margin_pct"] = 100.0 * a["fcf_exfloat_musd"] / a["revenue_musd"]
    a["fcf_to_adj_ebitda_pct"] = 100.0 * a["fcf_reported_musd"] / a["adj_ebitda_musd"]
    a["fcf_exfloat_to_adj_ebitda_pct"] = 100.0 * a["fcf_exfloat_musd"] / a["adj_ebitda_musd"]
    a["fcf_less_sbc_to_adj_ebitda_pct"] = 100.0 * a["fcf_less_sbc_musd"] / a["adj_ebitda_musd"]
    return a


# --------------------------------------------------------------------------------------
# 3. Seasonal norm and the RNPL transition
# --------------------------------------------------------------------------------------

def build_norms(d: pd.DataFrame) -> dict[str, float]:
    """Rebuild the pre-RNPL norm (unearned fees stock over next-quarter revenue) and check
    it against the pins carried in the study design. Pre-RNPL = through 2Q25 (US RNPL
    launched in 3Q25), window from 2023 to exclude the covid-distorted 2021-22 stocks."""
    w = d.copy()
    w["next_rev"] = w["revenue_musd"].shift(-1)
    w["ratio"] = w["unearned_fees_musd"] / w["next_rev"]
    w["_k"] = w["quarter"].map(qkey)
    pre = w[(w["_k"] >= (23, 1)) & (w["_k"] <= (25, 2))]
    norms = {}
    for qn in ["1Q", "2Q", "3Q", "4Q"]:
        sub = pre[pre["quarter"].str.startswith(qn)]["ratio"].dropna()
        norms[qn] = float(sub.mean())
        assert abs(norms[qn] - NORM_PINS[qn]) < 0.002, (
            f"norm {qn} rebuilt at {norms[qn]:.4f} vs pin {NORM_PINS[qn]}"
        )
    return norms


def build_transition(q: pd.DataFrame, norms: dict[str, float]) -> pd.DataFrame:
    """Unearned-fees shortfall against the pre-RNPL seasonal norm, and the FCF drag it
    implies. The drag in a quarter is the QUARTER-ON-QUARTER GROWTH in the shortfall:
    the stock shortfall is a level, the cash-flow effect is its change."""
    w = q.copy().reset_index(drop=True)
    w["next_rev_musd"] = w["revenue_musd"].shift(-1)
    # 2Q26's next quarter is not yet reported: use the guided 3Q26 midpoint.
    w.loc[w["quarter"] == "2Q26", "next_rev_musd"] = GUIDE_3Q26_REV_MID
    w["norm_ratio"] = w["qnum"].map(norms)
    w["unearned_fees_norm_musd"] = w["norm_ratio"] * w["next_rev_musd"]
    w["uf_shortfall_musd"] = w["unearned_fees_norm_musd"] - w["unearned_fees_musd"]
    w["uf_shortfall_pct_of_norm"] = 100.0 * w["uf_shortfall_musd"] / w["unearned_fees_norm_musd"]
    w["fcf_drag_in_quarter_musd"] = -w["uf_shortfall_musd"].diff()
    w["fcf_exrnpl_musd"] = w["fcf_reported_musd"] - w["fcf_drag_in_quarter_musd"]
    w["fcf_growth_less_revenue_growth_pts"] = w["fcf_reported_yoy_pct"] - w["revenue_yoy_pct"]
    w["ttm_fcf_growth_less_revenue_growth_pts"] = (
        w["ttm_fcf_reported_yoy_pct"] - w["ttm_revenue_yoy_pct"]
    )
    cols = [
        "quarter", "qnum", "revenue_musd", "next_rev_musd", "norm_ratio",
        "unearned_fees_musd", "unearned_fees_norm_musd", "uf_shortfall_musd",
        "uf_shortfall_pct_of_norm", "fcf_drag_in_quarter_musd", "fcf_reported_musd",
        "fcf_exrnpl_musd", "fcf_reported_yoy_pct", "revenue_yoy_pct",
        "fcf_growth_less_revenue_growth_pts", "ttm_fcf_reported_yoy_pct",
        "ttm_revenue_yoy_pct", "ttm_fcf_growth_less_revenue_growth_pts",
    ]
    return w[cols]


# --------------------------------------------------------------------------------------
# 4. 2027 permanent effects
# --------------------------------------------------------------------------------------

def build_bridge_2027(q: pd.DataFrame, tr: pd.DataFrame, norms: dict[str, float]) -> pd.DataFrame:
    last = q[q["quarter"] == "2Q26"].iloc[0]
    t2q26 = tr[tr["quarter"] == "2Q26"].iloc[0]

    # Pass-through from RNPL GBV share to the unearned-fees shortfall rate, pinned on 2Q26.
    u_2q26 = float(t2q26["uf_shortfall_pct_of_norm"]) / 100.0
    passthrough = u_2q26 / RNPL_SHARE["2Q26_measured"]

    # Yield on interest-earning balances: not disclosed separately for customer funds, so the
    # blended implied yield is used. 2026 run rate (1H26) central, FY25 as the high case.
    yld_1h26 = float(q[q["quarter"].isin(["1Q26", "2Q26"])]["implied_yield_annualised_pct"].mean()) / 100.0
    yld_fy25 = float(q[q["quarter"].str.endswith("25")]["implied_yield_annualised_pct"].mean()) / 100.0

    # Average customer float, trailing four quarters, grown to FY27 on GBV.
    ttm_float = float(q[q["quarter"].isin(["3Q25", "4Q25", "1Q26", "2Q26"])]["customer_float_musd"].mean())
    gbv_growth_to_fy27 = GBV_FY27_BASE / GBV_TTM_2Q26
    float_fy27_observed = ttm_float * gbv_growth_to_fy27

    # Ex-float conversion, the RNPL-neutral anchor. FY25 realised.
    fy25 = q[q["quarter"].str.endswith("25")]
    exfloat_margin_fy25 = float(fy25["fcf_exfloat_musd"].sum() / fy25["revenue_musd"].sum())

    # Counterfactual annual change in unearned fees at the pre-RNPL norm.
    d_uf_norm_fy27 = norms["4Q"] * (REV_1Q28_BASE - REV_1Q27_BASE)

    rows = []
    for scen in ["bear", "central", "bull"]:
        share_fy27 = RNPL_SHARE[scen]["FY27"]
        share_4q26 = RNPL_SHARE[scen]["4Q26"]
        u_fy27 = passthrough * share_fy27
        u_4q26 = passthrough * share_4q26

        # A. FCF if RNPL did not exist.
        fcf_no_rnpl = exfloat_margin_fy25 * REV_FY27_BASE + d_uf_norm_fy27

        # B. Transition: the shortfall still growing through 2027 as the share steps up.
        sf_4q26 = u_4q26 * norms["4Q"] * REV_1Q27_BASE
        sf_4q27 = u_fy27 * norms["4Q"] * REV_1Q28_BASE
        transition = -(sf_4q27 - sf_4q26)

        # C. Permanent float loss and the interest income it would have earned.
        #    Low  = the measured unearned-fees shortfall only (FX-clean, fee slice only).
        #    High = u applied to the whole customer backlog (the unpaid-GBV reading of doc 04).
        #    Central = measured unearned-fees shortfall plus the measured ex-FX funds-payable
        #              gap, scaled to the FY27 share and volume.
        avg_uf_shortfall = float(
            tr[tr["quarter"].isin(["3Q25", "4Q25", "1Q26", "2Q26"])]["uf_shortfall_musd"].mean()
        )
        float_loss_low = avg_uf_shortfall * gbv_growth_to_fy27 * (share_fy27 / RNPL_SHARE["2Q26_measured"])
        float_loss_high = u_fy27 * float_fy27_observed / (1.0 - u_fy27)
        # measured ex-FX funds-payable lag vs GBV at 2Q26: 15.7% - 11.9% = 3.8pts on the 2Q25 base
        fp_gap_2q26 = 0.038 * float(q[q["quarter"] == "2Q25"].iloc[0]["funds_payable_musd"])
        peak_to_avg = ttm_float / float(last["customer_float_musd"])
        float_loss_mid = (
            (float(t2q26["uf_shortfall_musd"]) + fp_gap_2q26)
            * peak_to_avg
            * gbv_growth_to_fy27
            * (share_fy27 / RNPL_SHARE["2Q26_measured"])
        )
        interest_lost_mid = -float_loss_mid * yld_1h26
        interest_lost_low = -float_loss_low * yld_1h26
        interest_lost_high = -float_loss_high * yld_fy25

        # D. One extra point of platform cancellation rate: processing cost only.
        gross_bookings_fy27 = GBV_FY27_BASE / (1.0 - PLATFORM_CANCEL_RATE)
        merchant_fee_rate = 1666.0 / (91300.0 / (1.0 - PLATFORM_CANCEL_RATE))  # FY25 pay-in proxy
        extra_cancelled_gbv = 0.01 * gross_bookings_fy27
        cancel_cost_high = -extra_cancelled_gbv * merchant_fee_rate   # all cancellations post-payment
        cancel_cost_low = 0.0                                          # all pre-payment (RNPL mechanics)
        cancel_cost_mid = 0.5 * cancel_cost_high

        # E. Single-fee migration working capital. The 10-K puts the host fee in unearned fees
        #    at receipt under BOTH structures, so there is no recurring float term; the only
        #    effect is the one-time stock build on the 0.6pt higher total take, which lands in
        #    2026 as the migration completes.
        single_fee_wc = 0.0

        fcf_with_rnpl = (
            fcf_no_rnpl + transition + interest_lost_mid + cancel_cost_mid + single_fee_wc
        )

        for term, val, lo, hi, kind, label, note in [
            ("A. FCF 2027 if RNPL did not exist", fcf_no_rnpl, None, None, "start", "derived",
             f"FY25 ex-float conversion {100*exfloat_margin_fy25:.1f}% on base FY27 revenue "
             f"${REV_FY27_BASE:,.0f}m, plus the pre-RNPL seasonal change in unearned fees "
             f"${d_uf_norm_fy27:,.0f}m"),
            ("B. Transition: RNPL share still stepping up", transition, None, None, "step", "derived",
             f"unearned-fees shortfall grows from ${sf_4q26:,.0f}m (4Q26 at {100*share_4q26:.0f}% of GBV) "
             f"to ${sf_4q27:,.0f}m (4Q27 at {100*share_fy27:.0f}%); the FCF effect is the increment, not the level"),
            ("C. Permanent: interest income on float never collected", interest_lost_mid,
             interest_lost_low, interest_lost_high, "step", "derived",
             f"float loss ${float_loss_mid:,.0f}m (range ${float_loss_low:,.0f}-{float_loss_high:,.0f}m) "
             f"at an ASSUMED blended yield of {100*yld_1h26:.2f}% (1H26 implied; {100*yld_fy25:.2f}% FY25). "
             f"No customer-funds yield is disclosed."),
            ("D. Permanent: +1pt platform cancellation rate, processing cost", cancel_cost_mid,
             cancel_cost_low, cancel_cost_high, "step", "derived",
             f"{extra_cancelled_gbv:,.0f}m extra cancelled GBV at a {100*merchant_fee_rate:.2f}% merchant-fee "
             f"rate; zero if the cancellation lands before the RNPL payment date, full if after"),
            ("E. Single-fee migration working capital", single_fee_wc, 0.0, 0.0, "step", "measured",
             "10-K Note 2: host and guest fees are recorded as cash with a corresponding amount "
             "in unearned fees under BOTH structures, so the migration adds no float"),
            ("F. FCF 2027 with RNPL", fcf_with_rnpl, None, None, "end", "derived",
             f"margin {100*fcf_with_rnpl/REV_FY27_BASE:.1f}% on base FY27 revenue"),
            ("MEMO: same deltas on the repo base-case FY27 FCF", 5420.0 + (fcf_with_rnpl - fcf_no_rnpl),
             None, None, "memo", "derived",
             "data/processed/overnight/13_model_annual.csv Base 2027 FCF $5,420m carries its own "
             "P&L assumptions; only the RNPL deltas belong to this object"),
            ("MEMO: pass-through, RNPL GBV share to unearned-fees shortfall rate",
             passthrough, None, None, "memo", "derived",
             f"pinned on 2Q26: shortfall {100*u_2q26:.1f}% of norm at a measured ~21% RNPL GBV share"),
            ("MEMO: blended implied yield on interest-earning balances, 1H26 (pct)",
             100 * yld_1h26, None, 100 * yld_fy25, "memo", "assumed",
             "no customer-funds yield is disclosed; interest income over average "
             "(cash + short-term investments + restricted cash + funds held on behalf of customers)"),
            ("MEMO: merchant-fee rate on pay-in volume (pct)",
             100 * merchant_fee_rate, None, None, "memo", "derived",
             "FY25 merchant fees and chargebacks $1,666m over FY25 GBV grossed up for a 17% "
             "cancellation rate"),
            ("MEMO: revenue at risk from +1pt cancellation rate (not in the bridge)",
             -extra_cancelled_gbv * 0.1325, None, None, "memo", "derived",
             "belongs to the KPI-inflation object, not here; carried to avoid double counting"),
        ]:
            rows.append(
                dict(scenario=scen, rnpl_share_fy27_pct=100 * share_fy27, term=term,
                     value_musd=val, low_musd=lo, high_musd=hi, kind=kind, label=label, note=note)
            )
    return pd.DataFrame(rows)


def build_forward_drag(q: pd.DataFrame, tr: pd.DataFrame, norms: dict[str, float]) -> pd.DataFrame:
    """Carry the shortfall forward 3Q26-2Q27 under each share path and report the FCF drag in
    each quarter and, decisively, the YEAR-ON-YEAR change in that drag, which is what moves
    reported FCF growth."""
    t2q26 = tr[tr["quarter"] == "2Q26"].iloc[0]
    u_2q26 = float(t2q26["uf_shortfall_pct_of_norm"]) / 100.0
    passthrough = u_2q26 / RNPL_SHARE["2Q26_measured"]

    # Forward next-quarter revenue, base path (derived from the repo FY26/FY27 model).
    next_rev = {
        "3Q26": REV_4Q26_BASE, "4Q26": REV_1Q27_BASE,
        "1Q27": 4005.0,          # 2Q26 $3,608m at the FY27 base rate of +11.0%
        "2Q27": 5156.0,          # 3Q26 guide mid $4,730m at +9.0%
    }
    shares = {
        "central": {"3Q26": 0.22, "4Q26": 0.23, "1Q27": 0.25, "2Q27": 0.25},
        "bear": {"3Q26": 0.24, "4Q26": 0.27, "1Q27": 0.30, "2Q27": 0.30},
        "bull": {"3Q26": 0.21, "4Q26": 0.21, "1Q27": 0.20, "2Q27": 0.20},
    }
    prior_drag = dict(zip(tr["quarter"], tr["fcf_drag_in_quarter_musd"]))
    rows = []
    for scen, path in shares.items():
        prev_shortfall = float(t2q26["uf_shortfall_musd"])
        for qtr in ["3Q26", "4Q26", "1Q27", "2Q27"]:
            u = passthrough * path[qtr]
            norm = norms[qtr[:2]] * next_rev[qtr]
            uf = norm * (1.0 - u)
            sf = norm - uf
            drag = -(sf - prev_shortfall)
            ly = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26"}[qtr]
            rows.append(dict(
                scenario=scen, quarter=qtr, rnpl_share_of_gbv_pct=100 * path[qtr],
                unearned_fees_norm_musd=norm, unearned_fees_musd=uf,
                uf_shortfall_musd=sf, fcf_drag_in_quarter_musd=drag,
                prior_year_quarter=ly, prior_year_drag_musd=float(prior_drag[ly]),
                yoy_change_in_drag_musd=drag - float(prior_drag[ly]), label="derived",
            ))
            prev_shortfall = sf
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------
# 5. 5 November test
# --------------------------------------------------------------------------------------

def build_3q26_test(q: pd.DataFrame, tr: pd.DataFrame, norms: dict[str, float]) -> pd.DataFrame:
    t2q26 = tr[tr["quarter"] == "2Q26"].iloc[0]
    u_2q26 = float(t2q26["uf_shortfall_pct_of_norm"]) / 100.0
    passthrough = u_2q26 / RNPL_SHARE["2Q26_measured"]
    uf_2q26 = float(q[q["quarter"] == "2Q26"].iloc[0]["unearned_fees_musd"])

    # Q3 ex-float conversion: the RNPL-neutral run rate for the quarter.
    q3s = q[q["quarter"].isin(["3Q22", "3Q23", "3Q24", "3Q25"])]
    exfloat_q3 = float(q3s["fcf_exfloat_musd"].sum() / q3s["revenue_musd"].sum())
    exfloat_q3_recent = float(
        q[q["quarter"].isin(["3Q24", "3Q25"])]["fcf_exfloat_musd"].sum()
        / q[q["quarter"].isin(["3Q24", "3Q25"])]["revenue_musd"].sum()
    )

    uf_norm_3q26 = norms["3Q"] * REV_4Q26_BASE
    rows = []
    for scen, rev in [("guide low", GUIDE_3Q26_REV_LOW), ("guide mid", GUIDE_3Q26_REV_MID),
                      ("guide high", GUIDE_3Q26_REV_HIGH)]:
        for path in ["bull", "central", "bear"]:
            share = RNPL_SHARE[path]["3Q26"]
            u = passthrough * share
            uf_3q26 = uf_norm_3q26 * (1.0 - u)
            d_uf = uf_3q26 - uf_2q26
            for mname, m in [("4-year Q3", exfloat_q3), ("2-year Q3", exfloat_q3_recent)]:
                fcf = m * rev + d_uf
                rows.append(
                    dict(
                        rev_scenario=scen, revenue_3q26_musd=rev, rnpl_path=path,
                        rnpl_share_of_gbv_pct=100 * share, exfloat_basis=mname,
                        unearned_fees_3q26_musd=uf_3q26,
                        unearned_fees_3q26_yoy_pct=100 * (uf_3q26 / 1820.0 - 1.0),
                        unearned_fees_norm_3q26_musd=uf_norm_3q26,
                        d_unearned_fees_musd=d_uf,
                        fcf_exfloat_musd=m * rev,
                        fcf_3q26_musd=fcf,
                        fcf_margin_3q26_pct=100 * fcf / rev,
                        vs_3q25_fcf_musd=fcf - 1349.0,
                        vs_3q25_margin_pts=100 * fcf / rev - 32.9,
                        label="derived",
                    )
                )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------
# 6. Run
# --------------------------------------------------------------------------------------

def main() -> None:
    d = load_panel()
    q = build_quarterly(d)
    a = build_annual(q, d)
    norms = build_norms(d)
    tr = build_transition(q, norms)
    fw = build_forward_drag(q, tr, norms)
    br = build_bridge_2027(q, tr, norms)
    tst = build_3q26_test(q, tr, norms)

    # Noise band on the drag estimate: the same construction over eight pre-RNPL quarters,
    # where the true RNPL drag is zero by construction.
    pre = tr[tr["quarter"].map(lambda x: (25, 3) > qkey(x) >= (23, 3))]["fcf_drag_in_quarter_musd"]
    noise = dict(pre_rnpl_drag_mean_musd=float(pre.mean()),
                 pre_rnpl_drag_sd_musd=float(pre.std()),
                 pre_rnpl_drag_abs_max_musd=float(pre.abs().max()),
                 n=int(pre.count()))

    exhibit_cols = [
        "quarter", "nights_yoy_pct", "gbv_yoy_pct", "revenue_yoy_pct", "adj_ebitda_yoy_pct",
        "fcf_reported_yoy_pct", "fcf_exfloat_yoy_pct", "fcf_margin_pct",
        "fcf_exfloat_margin_pct", "fcf_to_adj_ebitda_pct", "fcf_exfloat_to_adj_ebitda_pct",
    ]
    ex = q[q["quarter"].map(lambda x: qkey(x) >= (24, 1))][exhibit_cols].copy()

    seas = (
        q[q["quarter"].map(lambda x: (24, 1) > qkey(x) >= (22, 1))]
        .groupby("qnum")[["fcf_margin_pct", "fcf_exfloat_margin_pct", "d_unearned_fees_musd"]]
        .mean()
        .reset_index()
        .rename(columns={
            "fcf_margin_pct": "mean_fcf_margin_pct_2022_2023",
            "fcf_exfloat_margin_pct": "mean_fcf_exfloat_margin_pct_2022_2023",
            "d_unearned_fees_musd": "mean_d_unearned_fees_musd_2022_2023",
        })
    )
    seas2 = (
        q[q["quarter"].map(lambda x: qkey(x) >= (24, 1))]
        .groupby("qnum")[["fcf_margin_pct", "fcf_exfloat_margin_pct", "d_unearned_fees_musd"]]
        .mean()
        .reset_index()
        .rename(columns={
            "fcf_margin_pct": "mean_fcf_margin_pct_2024_2026",
            "fcf_exfloat_margin_pct": "mean_fcf_exfloat_margin_pct_2024_2026",
            "d_unearned_fees_musd": "mean_d_unearned_fees_musd_2024_2026",
        })
    )
    seas = seas.merge(seas2, on="qnum")

    ff = pd.DataFrame(FILING_FACTS)
    ufc = pd.DataFrame(UF_CASHFLOW_CHECK)
    bal = {}
    uf = dict(zip(d["quarter"], d["unearned_fees_musd"]))
    bal["FY2023"] = uf["4Q23"] - uf["4Q22"]
    bal["FY2024"] = uf["4Q24"] - uf["4Q23"]
    bal["FY2025"] = uf["4Q25"] - uf["4Q24"]
    bal["1H2025"] = uf["2Q25"] - uf["4Q24"]
    bal["1H2026"] = uf["2Q26"] - uf["4Q25"]
    ufc["balance_difference"] = ufc["period"].map(bal)
    ufc["residual"] = ufc["balance_difference"] - ufc["cf_line"]

    writes = {
        "qog_cash_reality_quarterly.csv": q,
        "qog_cash_reality_annual.csv": a,
        "qog_cash_reality_seasonality.csv": seas,
        "qog_cash_reality_transition.csv": tr,
        "qog_cash_reality_forward_drag.csv": fw,
        "qog_cash_reality_bridge_2027.csv": br,
        "qog_cash_reality_exhibit.csv": ex,
        "qog_cash_reality_3q26_test.csv": tst,
        "qog_cash_reality_filing_facts.csv": ff,
        "qog_cash_reality_uf_reconciliation.csv": ufc,
    }
    for name, frame in writes.items():
        frame.to_csv(OUT / name, index=False)

    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 60)
    print("=== unearned fees: balance difference vs cash-flow statement ===")
    print(ufc.drop(columns="source").to_string(index=False))
    print("\n=== pre-RNPL seasonal norms (UF stock / next-quarter revenue) ===")
    print(norms)
    print("\n=== seasonality ===")
    print(seas.round(1).to_string(index=False))
    print("\n=== exhibit 1Q24-2Q26 ===")
    print(ex.round(1).to_string(index=False))
    print("\n=== transition, 1Q25-2Q26 ===")
    print(tr[tr["quarter"].map(lambda x: qkey(x) >= (25, 1))].round(1).to_string(index=False))
    print("\n=== annual ===")
    print(a.round(1).to_string(index=False))
    print("\n=== drag noise band, pre-RNPL quarters (true drag = 0) ===")
    print(noise)
    print("\n=== FCF cross-check, KPI panel vs abnb_fcf_bridge.csv (max |delta| by year) ===")
    print(q.assign(yr=q["quarter"].str[2:]).groupby("yr")["fcf_crosscheck_delta_musd"]
          .apply(lambda s: s.abs().max()).round(1).to_string())
    print("\n=== forward drag path ===")
    print(fw.round(1).to_string(index=False))
    print("\n=== 2027 bridge ===")
    print(br[["scenario", "term", "value_musd", "low_musd", "high_musd", "label"]].round(0).to_string(index=False))
    print("\n=== 3Q26 test (guide mid) ===")
    print(tst[tst["rev_scenario"] == "guide mid"].round(1).to_string(index=False))
    print("\nwrote:")
    for name in writes:
        print("  " + os.path.join("data/processed/rnpl_short_audit", name))


if __name__ == "__main__":
    main()
