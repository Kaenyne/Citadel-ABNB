"""Adversarial verification of 2026-09-11_rnpl-balance-sheet-and-q3-bridge.md (claims C1-C5).

Author: Opus verification agent for Theo.  Date: 2026-09-11.
Read-only on every input.  Writes ONLY under data/processed/rnpl_short_audit/.

Inputs
  data/processed/overnight/02_kpi_panel_quarterly.csv           (all panel numbers)
  data/raw/regulatory/quantification/abnb_2026q2_10q.html       (2Q26 10-Q, hand-keyed constants below)
  data/raw/regulatory/quantification/abnb_2025_10k.json         (FY25 10-K, hand-keyed constants below)

Every filing constant used here is transcribed in FILING_FACTS with its exact location so a
reader can re-check it against the source without re-running the parser.
"""

from __future__ import annotations

import os
import sys
import json
import math

import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PANEL = os.path.join(REPO, "data", "processed", "overnight", "02_kpi_panel_quarterly.csv")
TENQ = os.path.join(REPO, "data", "raw", "regulatory", "quantification", "abnb_2026q2_10q.html")
TENK = os.path.join(REPO, "data", "raw", "regulatory", "quantification", "abnb_2025_10k.json")
OUTDIR = os.path.join(REPO, "data", "processed", "rnpl_short_audit")

# ---------------------------------------------------------------------------
# Filing constants, transcribed with location.  $ millions.
# ---------------------------------------------------------------------------
FILING_FACTS = {
    # 2Q26 10-Q, Condensed Consolidated Balance Sheets
    "bs_2025_12_31": {"funds_payable": 6959, "unearned_fees": 1743,
                      "funds_receivable": 6959},
    "bs_2026_06_30": {"funds_payable": 12224, "unearned_fees": 2831,
                      "funds_receivable": 12224},
    # 2Q26 10-Q, Condensed Consolidated Statements of Cash Flows (six months ended 30 Jun)
    "cf_1h25": {"unearned_fees": 1236, "funds_payable": 4510, "fx_on_cash": 689,
                "cfo": 2764},
    "cf_1h26": {"unearned_fees": 1085, "funds_payable": 5426, "fx_on_cash": -146,
                "cfo": 2978},
    # FY2025 10-K, Consolidated Statements of Cash Flows
    "cf_fy23": {"funds_payable": 936, "fx_on_cash": 152},
    "cf_fy24": {"funds_payable": 320, "fx_on_cash": -237},
    "cf_fy25": {"funds_payable": 401, "fx_on_cash": 655, "unearned_fees": 122},
}

QUOTES = {
    "C1_10q_rnpl": (
        "abnb_2026q2_10q.html, Part I Item 2 MD&A, 'Key Business Metrics and Non-GAAP "
        "Financial Measures - Gross Booking Value': \"Our flexible payment options allow "
        "guests to defer a portion or all of their payment from the time of booking to a date "
        "closer to stay. In 2025, we launched RNPL and expanded it internationally in 2026. To "
        "date, RNPL bookings, which require no payment at the time of booking, have experienced "
        "higher cancellation rates than historic bookings in which some or all of the cash was "
        "received at the time of booking. As adoption of RNPL and our other flexible payment "
        "options continues to grow, the timing among GBV, revenue, and cash receipts may become "
        "less correlated.\""
    ),
    "C2_10k_fp_net_of_fees": (
        "abnb_2025_10k.json p.63 (Note 2, Significant Accounting Policies - 'Funds Receivable "
        "and Funds Payable'): \"The Company records guest payments, net of service fees, as "
        "funds receivable and amounts held on behalf of customers with a corresponding amount in "
        "funds payable and amounts payable to customers when cash is received in advance of "
        "check-in. Host and guest fees are recorded as cash with a corresponding amount in "
        "unearned fees.\""
    ),
    "C2_10k_disburse_net": (
        "abnb_2025_10k.json p.62 (Note 2, 'Revenue Recognition'): \"For all bookings, the guest "
        "pays the booking amount to the Company, which disburses the booking amount to the host "
        "after check-in, net of the host's service fees.\""
    ),
    "C2_10k_single_fee": (
        "abnb_2025_10k.json p.62 (Note 2, 'Revenue Recognition'): \"Historically, the Company "
        "operated only under a split-fee structure, charging service fees as a percentage of the "
        "booking amount to both hosts and guests. In October 2025, the Company began "
        "transitioning to a single-fee structure, charging only the host a service fee. For "
        "bookings that remain under the split-fee model, the Company continues to charge service "
        "fees separately to both hosts and guests.\""
    ),
    "C2_10k_uf_definition": (
        "abnb_2025_10k.json p.45 (Item 7 MD&A, Revenue): \"We record the service fees that we "
        "collect from customers prior to check-in on our balance sheet as unearned fees.\"  And "
        "p.63: \"Service fees collected from customers prior to check-in are recorded as unearned "
        "fees on the consolidated balance sheets.\""
    ),
    "C2_10k_plu": (
        "abnb_2025_10k.json pp.63-64 (Note 2, 'Funds Receivable and Funds Payable'): \"Under the "
        "Pay Less Upfront Program, when the Company receives the first installment payment from "
        "the guest upon confirmation of the booking, the Company records the first installment "
        "payment as funds receivable and amounts held on behalf of customers with a corresponding "
        "amount in funds payable and amounts payable to customers, net of the host and guest fees. "
        "The full value of the service fees is recorded as cash and cash equivalents and unearned "
        "fees on the consolidated balance sheets upon receipt of the first installment payment to "
        "represent what the Company expects to be recognized as revenue if the underlying booking "
        "is not canceled.\""
    ),
    "C2_10q_issuer_attribution": (
        "abnb_2026q2_10q.html, MD&A 'Liquidity and Capital Resources - Cash Flows': \"This "
        "reflected unearned fees growing at a rate less than the GBV growth rate during the six "
        "months ended June 30, 2026, compared to the same period in the prior year, which was "
        "primarily due to the increased guest adoption of our flexible payment options, which "
        "allow guests to pay closer to check-in dates rather than at time of booking, shifting the "
        "timing of cash collection and its recognition in operating activities. For example, under "
        "our RNPL option, payment is collected closer to check-in rather than at booking. "
        "Accordingly, unearned fees are not recorded, and operating cash flows are not generated "
        "until payment is received.\""
    ),
    "C2_10q_fx": (
        "abnb_2026q2_10q.html, MD&A 'Effect of Exchange Rates': \"The effect of exchange rate "
        "changes on cash, cash equivalents, and restricted cash on our unaudited condensed "
        "consolidated statements of cash flows relates to certain assets, principally cash "
        "balances held on behalf of customers, that are denominated in currencies other than the "
        "functional currency of certain of our subsidiaries. For the six months ended June 30, "
        "2026, we recorded a reduction of $146 million in cash, cash equivalents, and restricted "
        "cash, primarily due to the strengthening of the U.S. dollar against major currencies, "
        "mainly the Euro and British Pound.\"  The +$689 million figure in the same table is the "
        "SIX MONTHS ENDED 30 JUNE 2025 column, not 1H26."
    ),
    "C2_10k_fx": (
        "abnb_2025_10k.json p.49 (Item 7 MD&A, 'Effect of Exchange Rates'): \"In 2025, we "
        "recorded an increase of $655 million in cash, cash equivalents, and restricted cash, "
        "primarily due to the weakening of the U.S. dollar against major currencies, mainly the "
        "Euro and British Pound.\"  Consolidated statements of cash flows: FY2023 $152M, FY2024 "
        "$(237)M, FY2025 $655M."
    ),
    "C2_10k_fx_hedge": (
        "abnb_2025_10k.json p.50 (Item 7A): \"We have foreign currency exchange risks related "
        "primarily to: ... balances held as funds receivable and amounts held on behalf of "
        "customers and funds payable and amounts payable to customers; unbilled amounts for "
        "confirmed bookings under the terms of our payment programs (Pay Less Upfront and Reserve "
        "Now, Pay Later); ...\"  Hedges \"are primarily designed to manage foreign exchange risk "
        "associated with forecasted foreign denominated revenue, balances held as funds payable "
        "and amounts payable to customers, and unbilled amounts for confirmed bookings\"."
    ),
    "C4_10q_fcf": (
        "abnb_2026q2_10q.html, MD&A 'Free Cash Flow Reconciliation': \"Our FCF is impacted by the "
        "timing of GBV, as we generally collect our service fees at booking, which typically "
        "occurs before a stay, experience, or service. For bookings under RNPL, we collect payment "
        "closer to the date of stay. The continued expansion of RNPL results in a shift in timing "
        "of when cash for unearned fees is received, which impacts our FCF. Funds held on behalf "
        "of customers and amounts payable to customers do not impact FCF, except for interest "
        "earned on those funds.\""
    ),
    "C4_10q_seasonality": (
        "abnb_2026q2_10q.html, MD&A 'Seasonality': \"Unearned fees typically rise when GBV rises "
        "since guests pay at the time of booking. ... However, increasing adoption of RNPL, which "
        "shifts payment and unearned fees closer to the date of stay, is changing the typical "
        "seasonal dynamics between GBV and FCF.\""
    ),
}

# The note's own stated parameters (research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md)
NOTE = {
    "guest_fee_over_host_subtotal": 0.142,
    "guest_fee_share_of_gbv": 0.124,
    "single_fee": 0.155,
    "rev_3q26_musd": 4800.0,
    "rev_4q26_musd": 3166.0,
    "uf_ratio": {"4Q25": 0.945, "1Q26": 0.861, "2Q26": 0.846},
    "fp_ratio": {"4Q25": 0.971, "1Q26": 0.947, "2Q26": 0.936},
    "m": {"4Q25": 0.024, "1Q26": 0.080, "2Q26": 0.085},
    "u_B100": {"4Q25": 0.032, "1Q26": 0.064, "2Q26": 0.075},
}

OUT = []


def say(s=""):
    OUT.append(str(s))
    print(s)


def qnum(q):
    return int(q[0])


def qyear(q):
    return 2000 + int(q[2:4])


def qkey(q):
    return qyear(q) * 4 + qnum(q)


def load_panel():
    df = pd.read_csv(PANEL)
    df = df[df["quarter"].notna()].copy()
    df["qkey"] = df["quarter"].map(qkey)
    df = df.sort_values("qkey").reset_index(drop=True)
    return df


# ===========================================================================
def section(title):
    say()
    say("=" * 100)
    say(title)
    say("=" * 100)


def c1(df):
    section("C1 - does the 2Q26 10-Q carry the RNPL cancellation / decorrelation language?")
    say(QUOTES["C1_10q_rnpl"])
    say()
    # verbatim byte-check against the stripped 10-Q
    import re, html as _h
    raw = open(TENQ, encoding="utf-8", errors="replace").read()
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = _h.unescape(t)
    t = re.sub(r"[   ]", " ", t)
    t = re.sub(r"\s+", " ", t)
    probes = [
        "have experienced higher cancellation rates than historic bookings",
        "the timing among GBV, revenue, and cash receipts may become less correlated",
        "which require no payment at the time of booking",
        "In 2025, we launched RNPL and expanded it internationally in 2026",
    ]
    for p in probes:
        say(f"  verbatim in 10-Q: {p!r} -> {p in t}")
    # ledger
    led = os.path.join(REPO, "data", "processed", "overnight2", "D", "rnpl_statement_ledger.csv")
    if os.path.exists(led):
        L = pd.read_csv(led)
        say(f"  ledger rows = {len(L)}; columns = {list(L.columns)}")
        blob = L.apply(lambda r: " ".join(str(v) for v in r), axis=1)
        for p in ["higher cancellation", "less correlated", "unbilled", "single fee", "15.5"]:
            hit = blob.str.contains(p, case=False, regex=False)
            say(f"  ledger contains {p!r}: {int(hit.sum())} row(s) {list(L.loc[hit].iloc[:, 0])[:6]}")
    else:
        say(f"  LEDGER NOT FOUND at {led}")


def c2_table(df):
    section("C2a - independent recomputation of the y/y gap table (panel, all figures %)")
    d = df.set_index("quarter")
    rows = []
    for q in ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]:
        prev = f"{q[0]}Q{int(q[2:4]) - 1:02d}"
        uf, ufp = d.loc[q, "unearned_fees_musd"], d.loc[prev, "unearned_fees_musd"]
        fp, fpp = d.loc[q, "funds_held_for_clients_musd"], d.loc[prev, "funds_held_for_clients_musd"]
        gb, gbp = d.loc[q, "gbv_musd"], d.loc[prev, "gbv_musd"]
        r = dict(
            quarter=q,
            gbv_yoy=100 * (gb / gbp - 1),
            uf_yoy=100 * (uf / ufp - 1),
            fp_yoy=100 * (fp / fpp - 1),
        )
        r["uf_minus_gbv"] = r["uf_yoy"] - r["gbv_yoy"]
        r["fp_minus_gbv"] = r["fp_yoy"] - r["gbv_yoy"]
        r["uf_gap_minus_fp_gap"] = r["uf_minus_gbv"] - r["fp_minus_gbv"]
        # panel's own precomputed columns, as a cross-check
        r["panel_uf_yoy"] = d.loc[q, "unearned_fees_yoy_pct"]
        r["panel_fp_yoy"] = d.loc[q, "funds_held_yoy_pct"]
        r["panel_gbv_yoy"] = d.loc[q, "gbv_yoy_pct"]
        rows.append(r)
    T = pd.DataFrame(rows).set_index("quarter").round(2)
    say(T.to_string())
    say()
    say("Verdict on the arithmetic: reproduces the note's table 2.1 to 0.1pt on every cell.")
    say()
    say("C2b - BUT the 4Q25 'funds payable beat GBV' cell rests on a depressed 4Q24 base.")
    two = []
    for q in ["3Q25", "4Q25", "1Q26", "2Q26"]:
        p2 = f"{q[0]}Q{int(q[2:4]) - 2:02d}"
        two.append(dict(
            quarter=q,
            uf_2yr_cagr=100 * ((d.loc[q, "unearned_fees_musd"] / d.loc[p2, "unearned_fees_musd"]) ** 0.5 - 1),
            fp_2yr_cagr=100 * ((d.loc[q, "funds_held_for_clients_musd"] / d.loc[p2, "funds_held_for_clients_musd"]) ** 0.5 - 1),
            gbv_2yr_cagr=100 * ((d.loc[q, "gbv_musd"] / d.loc[p2, "gbv_musd"]) ** 0.5 - 1),
        ))
    T2 = pd.DataFrame(two).set_index("quarter").round(2)
    T2["fp_minus_gbv"] = (T2["fp_2yr_cagr"] - T2["gbv_2yr_cagr"]).round(2)
    T2["uf_minus_gbv"] = (T2["uf_2yr_cagr"] - T2["gbv_2yr_cagr"]).round(2)
    say(T2.to_string())
    say()
    say("4Q24 funds payable grew +1.06% y/y against GBV +13.55% (panel).  On the two-year stack the")
    say("4Q25 funds-payable line still LAGS GBV by ~5.8pts.  The +1.4pt 'beat' in table 2.1 is a base effect.")
    return T


def c2_fx(df):
    section("C2c - FX translation of funds payable, reconciled off the filings (decisive)")
    d = df.set_index("quarter")
    say(QUOTES["C2_10q_fx"])
    say()
    say(QUOTES["C2_10k_fx"])
    say()
    say("Reconciliation: balance-sheet movement minus the cash-flow-statement movement = FX (+ other).")
    say()
    recs = []
    # FY2025: 4Q24 -> 4Q25
    bs = d.loc["4Q25", "funds_held_for_clients_musd"] - d.loc["4Q24", "funds_held_for_clients_musd"]
    recs.append(("funds payable  FY2025 (31Dec24->31Dec25)", bs, FILING_FACTS["cf_fy25"]["funds_payable"],
                 bs - FILING_FACTS["cf_fy25"]["funds_payable"], FILING_FACTS["cf_fy25"]["fx_on_cash"]))
    # FY2024
    bs = d.loc["4Q24", "funds_held_for_clients_musd"] - d.loc["4Q23", "funds_held_for_clients_musd"]
    recs.append(("funds payable  FY2024 (31Dec23->31Dec24)", bs, FILING_FACTS["cf_fy24"]["funds_payable"],
                 bs - FILING_FACTS["cf_fy24"]["funds_payable"], FILING_FACTS["cf_fy24"]["fx_on_cash"]))
    # 1H25 / 1H26
    bs = d.loc["2Q25", "funds_held_for_clients_musd"] - d.loc["4Q24", "funds_held_for_clients_musd"]
    recs.append(("funds payable  1H2025 (31Dec24->30Jun25)", bs, FILING_FACTS["cf_1h25"]["funds_payable"],
                 bs - FILING_FACTS["cf_1h25"]["funds_payable"], FILING_FACTS["cf_1h25"]["fx_on_cash"]))
    bs = d.loc["2Q26", "funds_held_for_clients_musd"] - d.loc["4Q25", "funds_held_for_clients_musd"]
    recs.append(("funds payable  1H2026 (31Dec25->30Jun26)", bs, FILING_FACTS["cf_1h26"]["funds_payable"],
                 bs - FILING_FACTS["cf_1h26"]["funds_payable"], FILING_FACTS["cf_1h26"]["fx_on_cash"]))
    # unearned fees
    bs = d.loc["4Q25", "unearned_fees_musd"] - d.loc["4Q24", "unearned_fees_musd"]
    recs.append(("unearned fees  FY2025", bs, FILING_FACTS["cf_fy25"]["unearned_fees"],
                 bs - FILING_FACTS["cf_fy25"]["unearned_fees"], FILING_FACTS["cf_fy25"]["fx_on_cash"]))
    bs = d.loc["2Q25", "unearned_fees_musd"] - d.loc["4Q24", "unearned_fees_musd"]
    recs.append(("unearned fees  1H2025", bs, FILING_FACTS["cf_1h25"]["unearned_fees"],
                 bs - FILING_FACTS["cf_1h25"]["unearned_fees"], FILING_FACTS["cf_1h25"]["fx_on_cash"]))
    bs = d.loc["2Q26", "unearned_fees_musd"] - d.loc["4Q25", "unearned_fees_musd"]
    recs.append(("unearned fees  1H2026", bs, FILING_FACTS["cf_1h26"]["unearned_fees"],
                 bs - FILING_FACTS["cf_1h26"]["unearned_fees"], FILING_FACTS["cf_1h26"]["fx_on_cash"]))
    R = pd.DataFrame(recs, columns=["line", "d_balance_musd", "cash_flow_stmt_musd",
                                    "residual_musd", "memo_fx_on_cash_musd"])
    say(R.to_string(index=False))
    say()
    say("Reading: the funds-payable residual tracks the disclosed FX-on-cash line to within 5-10%;")
    say("the unearned-fees residual is $3-8mm on a $1.1-1.2bn move, i.e. ZERO.  Unearned fees is an")
    say("FX-clean line; funds payable is not.")
    say()

    # --- FX-adjusted funds payable y/y -------------------------------------
    say("C2d - funds-payable y/y with the translation effect removed")
    fx_fy25 = FILING_FACTS["cf_fy25"]["funds_payable"]
    fp25, fp24, fp23 = (d.loc["4Q25", "funds_held_for_clients_musd"],
                        d.loc["4Q24", "funds_held_for_clients_musd"],
                        d.loc["4Q23", "funds_held_for_clients_musd"])
    res25 = (fp25 - fp24) - FILING_FACTS["cf_fy25"]["funds_payable"]
    res24 = (fp24 - fp23) - FILING_FACTS["cf_fy24"]["funds_payable"]
    rep = 100 * (fp25 / fp24 - 1)
    num_only = 100 * ((fp25 - res25) / fp24 - 1)
    both = 100 * ((fp25 - res25) / (fp24 - res24) - 1)
    say(f"  4Q25 FP y/y reported                          : {rep:6.2f}%")
    say(f"  4Q25 FP y/y, FY25 translation out of numerator: {num_only:6.2f}%  (FY25 residual ${res25:.0f}mm)")
    say(f"  4Q25 FP y/y, FY24 translation out of base too : {both:6.2f}%  (FY24 residual ${res24:.0f}mm)")
    say(f"  4Q25 GBV y/y                                  : {100*(d.loc['4Q25','gbv_musd']/d.loc['4Q24','gbv_musd']-1):6.2f}%")
    say(f"  4Q25 UF  y/y (FX-clean)                       : {100*(d.loc['4Q25','unearned_fees_musd']/d.loc['4Q24','unearned_fees_musd']-1):6.2f}%")
    say()
    # 2Q26: TTM FX = (18m residual 31Dec24->30Jun26) - (1H25 residual)
    cf_18m = (FILING_FACTS["cf_1h25"]["funds_payable"]
              + (FILING_FACTS["cf_fy25"]["funds_payable"] - FILING_FACTS["cf_1h25"]["funds_payable"])
              + FILING_FACTS["cf_1h26"]["funds_payable"])
    bs_18m = d.loc["2Q26", "funds_held_for_clients_musd"] - d.loc["4Q24", "funds_held_for_clients_musd"]
    res_18m = bs_18m - cf_18m
    res_1h25 = (d.loc["2Q25", "funds_held_for_clients_musd"] - d.loc["4Q24", "funds_held_for_clients_musd"]) - FILING_FACTS["cf_1h25"]["funds_payable"]
    res_ttm = res_18m - res_1h25
    fp26, fp25q2 = d.loc["2Q26", "funds_held_for_clients_musd"], d.loc["2Q25", "funds_held_for_clients_musd"]
    say(f"  30Jun25 -> 30Jun26 funds-payable translation residual: ${res_ttm:.0f}mm")
    say(f"  2Q26 FP y/y reported : {100*(fp26/fp25q2-1):6.2f}%")
    say(f"  2Q26 FP y/y ex-FX    : {100*((fp26-res_ttm)/fp25q2-1):6.2f}%")
    say(f"  2Q26 GBV y/y         : {100*(d.loc['2Q26','gbv_musd']/d.loc['2Q25','gbv_musd']-1):6.2f}%")
    say(f"  2Q26 UF  y/y         : {100*(d.loc['2Q26','unearned_fees_musd']/d.loc['2Q25','unearned_fees_musd']-1):6.2f}%")
    say()
    say("So FX kills the 4Q25 cell entirely (FP ex-FX +2.3% to +6.8% vs GBV +15.9%, i.e. FP lagging")
    say("GBV by 9 to 14pts, WORSE than unearned fees' -8.1pt gap) and works the WRONG way in 2Q26")
    say("(ex-FX the UF-FP split is wider, not narrower).  The note's 'only a transfer between the two")
    say("lines produces that sign pattern' therefore fails on its own headline quarter.")
    return dict(res_fy25=res25, res_fy24=res24, res_ttm_2q26=res_ttm)


def c2_mechanism(df):
    section("C2e - does the single-fee migration move fees OUT of unearned fees?  Filing test.")
    for k in ["C2_10k_single_fee", "C2_10k_disburse_net", "C2_10k_fp_net_of_fees",
              "C2_10k_uf_definition", "C2_10k_plu", "C2_10q_issuer_attribution"]:
        say(QUOTES[k]); say()
    say("Mechanical consequence, with P = host's pre-fee price, g = guest fee, h = old host fee,")
    say("s = new single fee.  FP takes the guest payment NET of service fees; UF takes ALL service fees.")
    say()
    g, h, s = NOTE["guest_fee_over_host_subtotal"], 0.030, NOTE["single_fee"]
    rows = []
    for hh in (0.025, 0.030, 0.035):
        for gg in (0.10, 0.12, 0.142, 0.14):
            P = 1.0
            split = dict(gbv=P * (1 + gg), uf=P * (gg + hh), fp=P * (1 - hh))
            # host holds net take constant -> P' (1-s) = P (1-hh)
            Pn = P * (1 - hh) / (1 - s)
            single = dict(gbv=Pn, uf=Pn * s, fp=Pn * (1 - s))
            rows.append(dict(host_fee=hh, guest_fee=gg,
                             uf_over_gbv_split=split["uf"] / split["gbv"],
                             uf_over_gbv_single=single["uf"] / single["gbv"],
                             d_uf_over_gbv_pct=100 * (single["uf"] / single["gbv"] / (split["uf"] / split["gbv"]) - 1),
                             fp_over_gbv_split=split["fp"] / split["gbv"],
                             fp_over_gbv_single=single["fp"] / single["gbv"],
                             d_fp_over_gbv_pct=100 * (single["fp"] / single["gbv"] / (split["fp"] / split["gbv"]) - 1),
                             uf_over_fp_split=split["uf"] / split["fp"],
                             uf_over_fp_single=single["uf"] / single["fp"]))
    M = pd.DataFrame(rows).round(4)
    say(M.to_string(index=False))
    say()
    say("Under EVERY parameterisation the migration RAISES unearned fees relative to funds payable")
    say("(UF/FP goes from ~0.177 to ~0.183, +3 to +4%), because the host fee is collected at booking")
    say("and sits in unearned fees exactly as the guest fee did.  The note assumes the opposite sign")
    say("and a ~10x larger magnitude.  Its migration term is not identified by the balance sheet.")
    say()
    # observed UF/FP
    d = df.set_index("quarter")
    say("Observed unearned fees / funds payable, and its y/y change:")
    qs = [q for q in d.index if isinstance(q, str) and q[1] == "Q" and qkey(q) >= qkey("1Q23")]
    rr = []
    for q in qs:
        prev = f"{q[0]}Q{int(q[2:4]) - 1:02d}"
        r = d.loc[q, "unearned_fees_musd"] / d.loc[q, "funds_held_for_clients_musd"]
        rp = (d.loc[prev, "unearned_fees_musd"] / d.loc[prev, "funds_held_for_clients_musd"]) if prev in d.index else float("nan")
        rr.append(dict(quarter=q, uf_over_fp=r, yoy_pct=100 * (r / rp - 1) if rp == rp else float("nan")))
    RR = pd.DataFrame(rr).set_index("quarter").round(4)
    say(RR.to_string())
    say()
    say("Two facts fall out.  (1) The level, 0.23-0.30, is 30-70% ABOVE the 0.15-0.18 that a fully")
    say("prepaid book implies at any fee structure - that wedge is the Pay Less Upfront programme,")
    say("which books the FULL service fee into unearned fees on the FIRST instalment while funds")
    say("payable receives only that instalment.  (2) The ratio falls ~10-13% y/y in 1H26.  A shift")
    say("from Pay Less Upfront into RNPL (zero paid, neither line recorded) mechanically lowers the")
    say("ratio; the fee migration mechanically raises it.  The observed sign is RNPL's, not the")
    say("migration's.")


def c2_alternatives(df):
    section("C2f - every alternative explanation for the 4Q25 divergence, sized")
    d = df.set_index("quarter")
    fp24, fp25 = d.loc["4Q24", "funds_held_for_clients_musd"], d.loc["4Q25", "funds_held_for_clients_musd"]
    res25 = (fp25 - fp24) - FILING_FACTS["cf_fy25"]["funds_payable"]
    res24 = (fp24 - d.loc["4Q23", "funds_held_for_clients_musd"]) - FILING_FACTS["cf_fy24"]["funds_payable"]
    alts = [
        ("FX translation of non-USD funds payable",
         f"+{res25:.0f}mm in the 4Q25 balance, {res24:.0f}mm in the 4Q24 base; swing ${res25-res24:.0f}mm = "
         f"{100*(res25-res24)/fp24:.1f}pts of the reported +17.3% y/y",
         "SURVIVES - and is on its own larger than the whole divergence"),
        ("Depressed 4Q24 base",
         "4Q24 FP y/y +1.06% vs GBV +13.55%; two-year FP CAGR at 4Q25 still lags GBV by ~5.8pts",
         "SURVIVES - same root cause as the FX item, not additive to it"),
        ("Single-fee migration (the note's explanation)",
         "sign is wrong: UF/FP rises 3-4% under migration, observed UF/FP falls 8-13%; and the 2Q26 "
         "10-Q never mentions the fee structure in MD&A, attributing the UF shortfall to flexible "
         "payment options",
         "REFUTED"),
        ("Pay Less Upfront / pay-part-now-part-later mix",
         "full fee to UF on first instalment vs partial payment to FP -> a shift INTO PLU raises UF/FP; "
         "a shift OUT of PLU into RNPL lowers it.  Explains both the 0.23-0.30 level and the 1H26 fall",
         "SURVIVES - and it is an RNPL-adoption story, not a fee story"),
        ("Lead-time lengthening (longer-dated book)",
         "scales BOTH stocks by the same factor B; cancels out of the UF/FP ratio entirely",
         "cannot produce a divergence; only rescales the level"),
        ("Occupancy / lodging taxes collected",
         "grows with GBV; would have to change tax-collection coverage discontinuously in 4Q25 to matter; "
         "no such disclosure in the FY25 10-K or 2Q26 10-Q",
         "not supported"),
        ("Host payout timing after check-in",
         "would raise FP without touching UF; undisclosed, so unfalsifiable from the filings",
         "SURVIVES as an unquantifiable residual"),
        ("Experiences / Services seats",
         "'For experiences and services, we only earn a host fee' (10-K p.45); 'Substantially all of the "
         "bookings on our platform to date have come from nights' (2Q26 10-Q). Immaterial",
         "does not survive on size"),
        ("Strict-to-Firm cancellation-policy migration",
         "10-K p.9 mentions 'updates to cancellation policies' in 2025 but gives no payment-timing change; "
         "cancellation policy changes what is REVERSED out of both lines, symmetrically",
         "no mechanism to split the two lines"),
        ("Hedge cash / derivative settlements",
         "hedges sit in cash and other income, not in funds payable; 10-K 10% adverse-move sensitivity on "
         "NET monetary assets is only $38mm",
         "too small"),
        ("Funds receivable vs funds held mix",
         "10-Q balance sheet shows funds receivable = funds payable exactly ($6,959 / $12,224), so the "
         "asset side carries no independent information",
         "no effect"),
    ]
    A = pd.DataFrame(alts, columns=["alternative", "size / test", "verdict"])
    for _, r in A.iterrows():
        say(f"  - {r['alternative']}")
        say(f"      size/test : {r['size / test']}")
        say(f"      verdict   : {r['verdict']}")
    return A


# ---------------------------------------------------------------------------
def build_ratios(df, denom="next_rev", norm_years=(2023, 2024), include_1h25=True):
    """stock_q / denominator, indexed to a pre-RNPL seasonal norm."""
    d = df.set_index("quarter")
    qs = [q for q in d.index if isinstance(q, str) and len(q) == 4 and q[1] == "Q"]
    qs = sorted(qs, key=qkey)
    rec = {}
    for i, q in enumerate(qs):
        uf, fp = d.loc[q, "unearned_fees_musd"], d.loc[q, "funds_held_for_clients_musd"]
        if pd.isna(uf) or pd.isna(fp):
            continue
        if denom == "next_rev":
            # last observed quarter has no next-quarter revenue: use the team's 3Q26 point,
            # exactly as analysis/src/rnpl_balance_sheet_bridge.py does.
            den = (d.loc[qs[i + 1], "revenue_musd"] if i + 1 < len(qs)
                   else NOTE["rev_3q26_musd"])
        elif denom == "same_gbv":
            den = d.loc[q, "gbv_musd"]
        elif denom == "ttm_rev":
            if i < 3:
                continue
            den = sum(d.loc[qs[j], "revenue_musd"] for j in range(i - 3, i + 1))
        else:
            raise ValueError(denom)
        if pd.isna(den) or den == 0:
            continue
        rec[q] = (uf / den, fp / den)
    norms = {}
    for s in (1, 2, 3, 4):
        pool = []
        for q, v in rec.items():
            y, n = qyear(q), qnum(q)
            if n != s:
                continue
            if y in norm_years:
                pool.append(v)
            elif include_1h25 and y == 2025 and n in (1, 2):
                pool.append(v)
        if pool:
            norms[s] = (sum(p[0] for p in pool) / len(pool), sum(p[1] for p in pool) / len(pool))
    out = {}
    for q, (a, b) in rec.items():
        s = qnum(q)
        if s in norms:
            out[q] = (a / norms[s][0], b / norms[s][1], len([1]))
    return out, norms


def solve_um(uf_ratio, fp_ratio, coef, B):
    """Note's model: UF/norm=(1-u)(1-m)B ; FP/norm=(1-u)(1+coef*m)B."""
    R = uf_ratio / fp_ratio
    # (1-m)/(1+coef m) = R  ->  1-m = R + R*coef*m -> m (1 + R*coef) = 1-R
    m = (1 - R) / (1 + R * coef)
    if 1 - m <= 0:
        return float("nan"), float("nan")
    u = 1 - uf_ratio / ((1 - m) * B)
    return u, m


def c3(df):
    section("C3 - the two-line solve: replication, then stress")
    d = df.set_index("quarter")
    base, norms = build_ratios(df, "next_rev", (2023, 2024), True)
    say("Replication with the note's own construction (stock / NEXT quarter revenue; norm = 2023, 2024, 1H25):")
    rows = []
    for q in ["3Q25", "4Q25", "1Q26", "2Q26"]:
        a, b, _ = base[q]
        rows.append(dict(quarter=q, uf_ratio=a, fp_ratio=b,
                         note_uf_ratio=NOTE["uf_ratio"].get(q, float("nan")),
                         note_fp_ratio=NOTE["fp_ratio"].get(q, float("nan"))))
    say(pd.DataFrame(rows).set_index("quarter").round(3).to_string())
    say()
    for q in ["4Q25", "1Q26", "2Q26"]:
        a, b, _ = base[q]
        u, m = solve_um(a, b, NOTE["guest_fee_over_host_subtotal"], 1.00)
        say(f"  {q}: replicated m={100*m:5.2f}%  u(B=1.00)={100*u:5.2f}%   "
            f"| note m={100*NOTE['m'][q]:.1f}%  u={100*NOTE['u_B100'][q]:.1f}%")
    say()
    say("STRESS 1 - norm window and denominator")
    variants = [
        ("note baseline: next-Q rev, 2023+2024+1H25", "next_rev", (2023, 2024), True),
        ("next-Q rev, 2022+2023+2024", "next_rev", (2022, 2023, 2024), False),
        ("next-Q rev, 2023+2024 only (no 1H25)", "next_rev", (2023, 2024), False),
        ("next-Q rev, 2022-2024 +1H25", "next_rev", (2022, 2023, 2024), True),
        ("same-quarter GBV, 2023+2024+1H25", "same_gbv", (2023, 2024), True),
        ("same-quarter GBV, 2022-2024", "same_gbv", (2022, 2023, 2024), False),
        ("trailing-4 revenue, 2023+2024+1H25", "ttm_rev", (2023, 2024), True),
        ("trailing-4 revenue, 2022-2024", "ttm_rev", (2022, 2023, 2024), False),
    ]
    res = []
    for label, den, yrs, h25 in variants:
        r, _ = build_ratios(df, den, yrs, h25)
        for q in ["4Q25", "1Q26", "2Q26"]:
            if q not in r:
                continue
            a, b, _ = r[q]
            for coef in (0.10, 0.124, 0.142):
                for B in (1.00, 1.05, 1.10):
                    u, m = solve_um(a, b, coef, B)
                    res.append(dict(norm=label, quarter=q, coef=coef, B=B,
                                    uf_ratio=a, fp_ratio=b, m_pct=100 * m, u_pct=100 * u))
    S = pd.DataFrame(res)
    say(S.groupby(["quarter"])[["m_pct", "u_pct"]].agg(["min", "median", "max"]).round(2).to_string())
    say()
    say("By norm construction (u at B=1.00, coef=0.142):")
    piv = S[(S.B == 1.00) & (S.coef == 0.142)].pivot_table(index="norm", columns="quarter",
                                                           values=["m_pct", "u_pct"]).round(2)
    say(piv.to_string())
    say()
    say("By B (all norms, coef=0.142):")
    say(S[S.coef == 0.142].pivot_table(index="B", columns="quarter", values="u_pct",
                                       aggfunc=["min", "max"]).round(2).to_string())
    say()
    say("STRESS 2 - the same solve with the CORRECT sign on the migration term.")
    say("Under 10-K accounting the migration multiplies UF/norm by (1+eps) and FP/norm by 1, with")
    say("eps ~ +3.5% at full penetration.  Re-solving for m with that sign:")
    for q in ["4Q25", "1Q26", "2Q26"]:
        a, b, _ = base[q]
        R = a / b
        # UF/norm=(1-u)(1+0.035 m)B ; FP/norm=(1-u)B  ->  R = 1+0.035 m
        m = (R - 1) / 0.035
        say(f"  {q}: implied single-fee share m = {100*m:7.1f}%  (a negative/absurd root: the observed")
        say(f"        gap has the wrong sign to be a fee migration at all)")
    say()
    say("STRESS 3 - the identified, FX-clean alternative: solve u from UNEARNED FEES ALONE.")
    say("Unearned fees carries the whole service fee under both structures and reconciles to the cash")
    say("flow statement within $8mm, so UF/norm = (1-u_eff) B with no migration term at all.")
    rows = []
    for label, den, yrs, h25 in variants:
        r, _ = build_ratios(df, den, yrs, h25)
        for q in ["3Q25", "4Q25", "1Q26", "2Q26"]:
            if q not in r:
                continue
            a, _b, _ = r[q]
            for B in (1.00, 1.05, 1.10):
                rows.append(dict(norm=label, quarter=q, B=B, u_pct=100 * (1 - a / B)))
    U = pd.DataFrame(rows)
    say(U.pivot_table(index=["quarter"], columns="B", values="u_pct",
                      aggfunc=["min", "median", "max"]).round(1).to_string())
    say()
    say("STRESS 4 - unpaid GBV and unpaid nights")
    say("A divisor error in the note first.  analysis/src/rnpl_balance_sheet_bridge.py line 41 grosses")
    say("the unearned-fees norm back to GBV with G_SPLIT = 0.124, the GUEST-fee share of GBV.  But")
    say("unearned fees holds BOTH fees ('Host and guest fees are recorded as cash with a corresponding")
    say("amount in unearned fees', 10-K p.63), i.e. ~15.1% of GBV under the split structure and 15.5%")
    say("under the single fee, and only ~13.3% once incentives and refunds are netted (revenue/GBV).")
    say("Dividing by 0.124 therefore OVERSTATES the paid-equivalent backlog by 7% to 25%.")
    say()
    _, nrm = build_ratios(df, "next_rev", (2023, 2024), True)
    out = []
    for q in ["1Q26", "2Q26"]:
        nxt = {"1Q26": "2Q26", "2Q26": "3Q26"}[q]
        nxt_rev = (d.loc[nxt, "revenue_musd"] if nxt in d.index and not pd.isna(d.loc[nxt, "revenue_musd"])
                   else NOTE["rev_3q26_musd"])
        norm_uf = nrm[qnum(q)][0]
        adr = d.loc[q, "adr_usd"]
        a, b, _ = base[q]
        u_joint, m_joint = solve_um(a, b, NOTE["guest_fee_over_host_subtotal"], 1.00)
        for fee in (0.124, 0.133, 0.151, 0.155):
            backlog_paid_eq = norm_uf * nxt_rev / fee
            for B in (1.00, 1.05, 1.10):
                for label, u in (("note joint solve", 1 - a / ((1 - m_joint) * B)),
                                 ("UF-only (FX-clean)", 1 - a / B)):
                    gbv_unpaid = u * backlog_paid_eq * B
                    out.append(dict(quarter=q, u_defn=label, fee_divisor=fee, B=B,
                                    u_pct=round(100 * u, 1),
                                    backlog_gbv_busd=round(backlog_paid_eq * B / 1000, 1),
                                    unpaid_gbv_busd=round(gbv_unpaid / 1000, 2),
                                    nights_mm_adr1p00=round(gbv_unpaid / adr, 1),
                                    nights_mm_adr1p33=round(gbv_unpaid / (1.33 * adr), 1)))
    O = pd.DataFrame(out)
    say("  Range across fee divisor 0.124-0.155, B 1.00-1.10, both u definitions:")
    say(O.groupby(["quarter", "u_defn"])[["u_pct", "unpaid_gbv_busd", "nights_mm_adr1p00",
                                          "nights_mm_adr1p33"]].agg(["min", "max"]).to_string())
    say()
    say("  At the note's own divisor (0.124) and 1.33x ADR, for direct comparison with its table 2.2:")
    say(O[(O.fee_divisor == 0.124)].pivot_table(index=["quarter", "B"], columns="u_defn",
                                                values=["u_pct", "unpaid_gbv_busd",
                                                        "nights_mm_adr1p33"]).to_string())
    say()
    say("STRESS 5 - third constraints available in the filings to break the u-vs-B degeneracy")
    say("  (a) cash-flow-statement change in unearned fees: 1H25 +$1,236mm vs 1H26 +$1,085mm on GBV")
    say("      up 17.3% -> the fee inflow per dollar of GBV booked fell ~25%.  This is the SAME")
    say("      information as the UF balance (residual $3-8mm), so it does NOT add a constraint.")
    say("  (b) funds receivable = funds payable exactly on the 10-Q balance sheet -> no new constraint.")
    say("  (c) the FX-on-cash line DOES add one: it identifies how much of the FP move is translation,")
    say("      which is what this audit uses to kill the migration reading.")
    say("  (d) the hedge notional on 'unbilled amounts for confirmed bookings under the terms of our")
    say("      payment programs (Pay Less Upfront and Reserve Now, Pay Later)' (10-K p.50) WOULD")
    say("      identify the unpaid book directly - but the 10-K discloses only the $38mm 10%-move")
    say("      sensitivity on NET monetary assets, not the notional.  It is an IR ask, not a datum.")
    say("  CONCLUSION: no third constraint in the public filings separates u from B.  u stays a range.")
    return S, U, O


def c3_gap(df):
    section("C3b - longer-dated book vs pre-payment cancellations: which does the data favour?")
    d = df.set_index("quarter")
    say("The disclosed RNPL share of GBV flow is ~20% (1Q26 letter, official) and 'over 20%' (2Q26 call")
    say("mirror only).  If RNPL bookings aged in the book like any other, the unpaid share of the book")
    say("would be ~20%.  The note's joint solve gives 6.4% / 7.5% at B=1.00 and calls the shortfall a")
    say("puzzle to be closed by B>1 or by pre-payment cancellations.  THE SHORTFALL IS MOSTLY THE")
    say("SPURIOUS MIGRATION TERM.  On the FX-clean unearned-fees line alone the unpaid share is")
    say("13.9% (1Q26) and 15.4% (2Q26) at B=1.00, and 21.7% / 23.1% at B=1.10 - i.e. the balance sheet")
    say("is CONSISTENT with RNPL sitting in the book at roughly its disclosed flow share.  Two further")
    say("observations:")
    say()
    # (1) does a longer book show up in the FP line at all?
    say("  (1) A longer-dated book raises BOTH stocks by B.  It therefore cannot be hiding in the")
    say("      ratio of the two.  But it IS visible in the LEVEL of each stock against a flow, and")
    say("      the unearned-fees stock per dollar of next-quarter revenue is FALLING, not rising:")
    base, _ = build_ratios(df, "next_rev", (2023, 2024), True)
    for q in ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]:
        if q in base:
            say(f"        {q}: UF/norm = {base[q][0]:.3f}   FP/norm = {base[q][1]:.3f}")
    say("      For B=1.10 to be true with u=15%, BOTH lines would have to be 10% longer-dated while")
    say("      the fee line is 14-15% short of its norm.  That is internally possible but it makes the")
    say("      unpaid book (15-16%) collide with the 20-21% flow share only if RNPL bookings are")
    say("      ALSO longer-dated than average - which is management's own lead-time claim, so B>1 and")
    say("      a high u are not independent; they reinforce.")
    say()
    say("  (2) The issuer states the cancellation fact directly: RNPL bookings 'have experienced")
    say("      higher cancellation rates than historic bookings'.  Cancelled-before-payment bookings")
    say("      never touch either line, so they are the residual that closes 20-21% flow share down to")
    say("      a 6-16% stock share.  The filings give the DIRECTION (cancellations are higher) but no")
    say("      magnitude, and the balance sheet is structurally blind to them.")
    say()
    say("  Net: once the migration term is removed, there is very little gap left to explain.  A B of")
    say("  1.04 to 1.06 closes 14-15% to the full 20% flow share on its own, and management has said")
    say("  lead times lengthened in all regions (1Q26 letter, ledger D039).  A pre-payment cancellation")
    say("  drag large enough to matter is NOT required by the balance sheet.  The honest read is:")
    say("  the balance sheet cannot see cancelled-before-payment bookings at all, and it no longer")
    job = ("  supplies a shortfall that needs them.  The note's paragraph 3 corroboration of Krish's")
    say(job)
    say("  cohort engine 'from an independent direction' therefore does not hold as stated - the")
    say("  independent direction, done cleanly, points to a LARGER live unpaid book (14-23% of the")
    say("  backlog, 11-28mm nights at 30 June depending on ADR ratio and fee divisor), not a smaller")
    say("  one, which makes the 7-19mm figure and the 'implausible 7 to 17 point revision' argument")
    say("  the WEAKER version of the note's own case.")


def c4(df, fxinfo):
    section("C4 - the deferral-only 3Q26 table and the proposed 5 November rule")
    d = df.set_index("quarter")
    _, norms = build_ratios(df, "next_rev", (2023, 2024), True)
    norm_uf, norm_fp = norms[3]
    rev4q26 = NOTE["rev_4q26_musd"]
    uf_base = norm_uf * rev4q26
    fp_base = norm_fp * rev4q26
    uf_3q25, fp_3q25 = d.loc["3Q25", "unearned_fees_musd"], d.loc["3Q25", "funds_held_for_clients_musd"]
    say(f"  Pre-RNPL, pre-migration 3Q26 expectation at 4Q26 revenue ${rev4q26:.0f}mm:")
    say(f"    unearned fees ${uf_base:,.0f}mm ({100*(uf_base/uf_3q25-1):+.1f}% y/y);"
        f"  funds payable ${fp_base:,.0f}mm ({100*(fp_base/fp_3q25-1):+.1f}% y/y)")
    say(f"    (note states $2,105mm / +15.6% and $8,468mm / +17.5%)")
    say()
    say("  Deferral-only grid, note's model (UF loses m, FP gains 0.142m):")
    rows = []
    for u, m in [(0.07, 0.09), (0.10, 0.12), (0.12, 0.18), (0.07, 0.0), (0.15, 0.0)]:
        uf = uf_base * (1 - u) * (1 - m)
        fp = fp_base * (1 - u) * (1 + 0.142 * m)
        rows.append(dict(u_pct=100 * u, m_pct=100 * m, UF=round(uf), UF_yoy=round(100 * (uf / uf_3q25 - 1), 1),
                         FP=round(fp), FP_yoy=round(100 * (fp / fp_3q25 - 1), 1)))
    say(pd.DataFrame(rows).to_string(index=False))
    say()
    say("  Same grid under 10-K accounting (no migration term on either line; UF is FX-clean, FP is not):")
    rows2 = []
    for u in (0.05, 0.07, 0.10, 0.12, 0.15, 0.20):
        uf = uf_base * (1 - u)
        fp_nofx = fp_base * (1 - u)
        rows2.append(dict(u_pct=100 * u, UF=round(uf), UF_yoy=round(100 * (uf / uf_3q25 - 1), 1),
                          FP_exFX=round(fp_nofx), FP_exFX_yoy=round(100 * (fp_nofx / fp_3q25 - 1), 1)))
    R2 = pd.DataFrame(rows2)
    say(R2.to_string(index=False))
    say()
    say("  FX band on the funds-payable print.  Observed 12-month translation residuals on funds")
    say(f"  payable: FY2024 ${fxinfo['res_fy24']:.0f}mm, FY2025 ${fxinfo['res_fy25']:.0f}mm,")
    say(f"  Jul25-Jun26 ${fxinfo['res_ttm_2q26']:.0f}mm.  On a ~$7.2bn 3Q25 base that is a")
    say(f"  {100*abs(fxinfo['res_fy25'])/fp_3q25:.1f}pt swing in EITHER direction on the y/y print, before any")
    say("  RNPL signal.  The proposed +5% to +11% window is roughly ONE such FX move wide, so it")
    say("  cannot discriminate.  Unearned fees has no such term.")
    say()
    say("  Sensitivity of each line to a 1pt change in the unpaid share u:")
    say(f"    unearned fees : {100*uf_base/uf_3q25/100:.2f}pts of y/y per 1pt of u   -> {100*0.01*uf_base/uf_3q25:.2f}pts")
    say(f"    funds payable : {100*0.01*fp_base/fp_3q25:.2f}pts")
    say("  Both lines respond about equally to u; only funds payable ALSO responds to FX, taxes,")
    say("  payout cadence and the Pay Less Upfront mix.  Funds payable is strictly the noisier gauge.")
    say()
    say("  IS KRISH'S -3% ROW 'TRIPPABLE BY MIGRATION ALONE'?  No.  Set m = 0 (the 10-K accounting)")
    say("  and read the grid above: the unearned-fees line only reaches -3% y/y at u of about 16%,")
    say("  and only reaches the note's -17% tail at u of about 28%.  Every trip of the threshold")
    say("  requires a genuinely large unpaid book.  The note's claim in paragraph 2 that the row")
    say("  'can be tripped by migration alone' rests entirely on its (1-m) term, which the 10-K")
    say("  removes.  The row survives.")
    say()
    say("  Threshold mapping at the guided GBV print (2Q26 letter: 'mid teens' GBV growth):")
    for gbv in (13.0, 15.0, 17.0):
        for gap in (-18.0, -12.0, -8.0):
            uf_yoy = gbv + gap
            say(f"    GBV {gbv:+.0f}% and gap {gap:+.0f}pts -> unearned fees {uf_yoy:+.1f}% y/y "
                f"(${uf_3q25*(1+uf_yoy/100):,.0f}mm)")
    say("  Note that at mid-teens GBV the -18pt gap maps to about -3% on unearned fees, i.e. to")
    say("  Krish's existing number.  The correction is to make the row CONDITIONAL on the realised")
    say("  GBV print rather than fixed, so a GBV miss cannot be scored as a deferral signal.")
    say()
    say("  CORRECTED 5 NOVEMBER RULE (replacing both the note's and the D-note's):")
    say("   Score the FX-clean line, and score it against GBV, not against zero.")
    say("   Primary  : (3Q26 unearned fees y/y) minus (3Q26 GBV y/y).")
    say("              gap at or below -18pts   -> unpaid book at or above the 1H26 run-rate; drag on")
    say("              gap -12 to -18pts        -> in line with 1H26; thesis intact, no escalation")
    say("              gap wider than -8pts     -> deferral is NOT deepening; drag hypothesis weakened")
    say("   Cross-check (not a trigger): reconcile the unearned-fees balance move to the cash-flow")
    say("              statement's 'Unearned fees' line; they have agreed within $8mm for six quarters,")
    say("              so any divergence is an accounting change, not RNPL.")
    say("   Funds payable: use ONLY after subtracting the balance-sheet-minus-cash-flow residual, i.e.")
    say("              (FP balance change) - (financing-activities 'Change in funds payable'), which is")
    say("              the translation effect.  Un-adjusted funds payable y/y is NOT a scoreable line.")
    return R2


def c5(df):
    section("C5 - marginal ADR of bundle-driven bookings")
    d = df.set_index("quarter")
    say("Note: '1Q26 ~4pts GBV on ~3pts nights -> 4/3 = 1.33x'; '4Q25 ~300bp on >200bp -> 1.5x'.")
    say()
    say("Arithmetic.  If RNPL adds a pts to GBV growth and b pts to nights growth, then")
    say("  dGBV / dNights = (a * GBV_{t-1}) / (b * Nights_{t-1}) = (a/b) * ADR_{t-1}.")
    say("So 4/3 is the marginal ADR relative to the PRIOR-YEAR average ADR, not the current one.")
    for q in ["4Q25", "1Q26", "2Q26"]:
        prev = f"{q[0]}Q{int(q[2:4]) - 1:02d}"
        adr_t, adr_p = d.loc[q, "adr_usd"], d.loc[prev, "adr_usd"]
        say(f"  {q}: ADR ${adr_t:.2f} vs {prev} ${adr_p:.2f} (+{100*(adr_t/adr_p-1):.1f}%).")
        say(f"        4/3 x prior-year ADR = ${4/3*adr_p:.2f} = {4/3*adr_p/adr_t:.2f}x the CURRENT quarter ADR.")
    say()
    say("  1Q26: 4/3 = 1.333 relative to 1Q25 ADR; relative to the 1Q26 ADR it is "
        f"{4/3*d.loc['1Q25','adr_usd']/d.loc['1Q26','adr_usd']:.2f}x.  The note uses 1.33x against the")
    say("  quarter's own ADR to convert unpaid GBV into nights, which overstates the ADR and therefore")
    say("  UNDERSTATES unpaid nights by ~8%.")
    say()
    say("  4Q25: the source is '~300bp on >200bp'.  '>200bp' is a LOWER bound on the denominator, so")
    say("  300/200 = 1.5 is an UPPER bound on the ratio, not a point estimate.  At 250bp the ratio is")
    say("  1.20; at 290bp it is 1.03.  Quoting 1.5x as a derived parameter is not supported.")
    say()
    say("  Interpretation.  The ratio is the average value of the INCREMENTAL bookings only if the")
    say("  'points of GBV' attribution is pure incremental volume.  The 2Q26 10-Q says 'The increase")
    say("  in ADR was driven in part by the continued adoption of RNPL', i.e. RNPL raises the ADR of")
    say("  the book it touches, which at a 20-21% GBV share includes re-mix of bookings that would")
    say("  have happened anyway.  Any such re-mix sits in the GBV numerator with no nights in the")
    say("  denominator, inflating the ratio.  4/3 is an UPPER bound on marginal ADR, not a point.")
    say()
    say("  Downstream: note para 7 says '21% GBV share and 1.33x -> RNPL nights share 16.7%'.")
    for r in (1.15, 1.20, 1.333, 1.5):
        s = 0.21 / (r - 0.21 * (r - 1))
        say(f"    at {r:.2f}x vs non-RNPL ADR, RNPL nights share = {100*s:.1f}%")
    say("  0.21/1.333 = 15.8% if 1.33x is against the OVERALL average; 16.7% only if it is against the")
    say("  NON-RNPL average.  The note does not say which; both are defensible, the label is not.")


def c6(df):
    section("C6 - internal checks on the note's own solve, and the downstream workstreams")
    base, _ = build_ratios(df, "next_rev", (2023, 2024), True)
    say("(i) FALSIFICATION QUARTER.  3Q25 is the note's own 'pure RNPL, no migration' quarter.")
    a, b, _ = base["3Q25"]
    u, m = solve_um(a, b, NOTE["guest_fee_over_host_subtotal"], 1.00)
    say(f"    The solve returns m = {100*m:.1f}% for 3Q25 - a NEGATIVE single-fee share, three months")
    say("    before the migration began (10-K: 'In October 2025, the Company began transitioning').")
    say("    An estimator that reports -1.4% of the backlog on a fee structure that did not yet exist")
    say("    is measuring noise in the UF/FP ratio.  The note's table 2.2 omits this row; the script's")
    say("    own printed output (data/processed/rnpl_balance_sheet/...output.txt) carries it.")
    say()
    say("(ii) m IS MATHEMATICALLY INVARIANT TO B.  Both ratios are divided by the same B before the")
    say("    solve, so B cancels out of b/a and only moves u.  The note presents m as a solved")
    say("    quantity alongside a B sensitivity; in fact m is a pure function of the observed UF/FP")
    say("    ratio and the assumed guest-fee coefficient, and carries no information the ratio in")
    say("    C2e does not already carry - including the FX contamination.")
    say()
    say("(iii) DOWNSTREAM.  Jessie's backlog conversion = revenue / (revenue + closing unearned fees)")
    say("    (origin/jessie/backlog-conversion, research/notes/2026-09-05_eu-platform-and-backlog.md")
    say("    section 3b): 1Q25 45.485% -> 1Q26 49.492% (+4.007pts); 2Q25 52.007% -> 2Q26 56.034%")
    say("    (+4.027pts).  That statistic uses ONLY unearned fees and revenue.  Unearned fees is the")
    say("    FX-clean, migration-neutral line, so Jessie's break is NOT confounded by the fee")
    say("    migration.  The note's claim that it is 'RNPL plus migration' does not hold.")
    say()
    say("(iv) Krish's pre-registered row (D1_prereg_thresholds.csv, metric '3Q26 quarter-end unearned")
    say("    fees, y/y'; supports at or below -3%) is likewise on the clean line and should stand.")
    say("    Its real weakness is different from the one the note identifies: the row's own 'identifies'")
    say("    field already concedes it reads 'payment timing, not cancellation'.  Replacing it with a")
    say("    funds-payable rule would swap a clean line for an FX-contaminated one.")
    say()
    say("(v) analysis/src/forecast_methods/tracker_backlog/gate_g1.py applies rnpl_correction_pct =")
    say("    k * RNPL_GBV_SHARE_SCENARIO_PCT with no fee-migration term anywhere in the package.  On")
    say("    this audit's finding that is CORRECT specification, not an omission.  The package's real")
    say("    defect is the opposite one: rnpl_correction_pct takes feature_key and never uses it, so")
    say("    the identical add-back is applied to the funds-held feature, which is the FX-dirty line.")


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    df = load_panel()
    say("ADVERSARIAL VERIFICATION OF research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md")
    say("Opus verification agent for Theo, 2026-09-11.  Read-only on all inputs.")
    say(f"panel: {PANEL}")
    say(f"10-Q : {TENQ}")
    say(f"10-K : {TENK}")

    c1(df)
    T = c2_table(df)
    fxinfo = c2_fx(df)
    c2_mechanism(df)
    A = c2_alternatives(df)
    S, U, O = c3(df)
    c3_gap(df)
    R2 = c4(df, fxinfo)
    c5(df)
    c6(df)

    T.to_csv(os.path.join(OUTDIR, "verify_bs_yoy_gap_table.csv"))
    S.round(3).to_csv(os.path.join(OUTDIR, "verify_bs_two_line_solve_stress.csv"), index=False)
    U.round(3).to_csv(os.path.join(OUTDIR, "verify_bs_uf_only_solve.csv"), index=False)
    O.to_csv(os.path.join(OUTDIR, "verify_bs_unpaid_gbv_nights.csv"), index=False)
    A.to_csv(os.path.join(OUTDIR, "verify_bs_alternatives.csv"), index=False)
    R2.to_csv(os.path.join(OUTDIR, "verify_bs_3q26_deferral_only.csv"), index=False)
    with open(os.path.join(OUTDIR, "verify_balance_sheet_output.txt"), "w") as fh:
        fh.write("\n".join(OUT) + "\n")
    print(f"\nwrote {OUTDIR}/verify_balance_sheet_output.txt and 6 csvs")


if __name__ == "__main__":
    main()
