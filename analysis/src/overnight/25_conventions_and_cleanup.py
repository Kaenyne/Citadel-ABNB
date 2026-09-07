"""
Workstream 25: model conventions and documentation cleanup (audit findings A12 and section 17).

Reads
  data/processed/overnight/13_valuation_summary.csv    per-lens prices, three scenarios (WS13)
  data/processed/overnight/13_model_annual.csv         FY26-FY28 metrics, net cash, period-end shares
  data/processed/abnb_quarterly_costlines.csv          GAAP quarterly cost lines from XBRL (Q4 = FY less 9M)
  data/processed/abnb_quarterly_cost_stack_exsbc.csv   ex-SBC cash cost stack with its identity check
  data/raw/letters/4Q23_d646462dex991.htm              4Q23 shareholder letter (Adj. EBITDA recon + SBC footnote)

Writes
  data/processed/overnight/25_valuation_conventions.csv  one row per valuation lens: metric year, the date the
                                                         value is actually as of, the adopted target date, and
                                                         whether interim cash flows are counted
  data/processed/overnight/25_source_id_remap.csv        research/sources/README.md S-number collisions and the
                                                         S40+ renumbering applied on 7 Sep 2026
  data/processed/overnight/25_history_reconciliation.csv the 4Q23 ex-SBC identity gap decomposed, and the
                                                         20-vs-22-quarter history mismatch resolved

Nothing here changes a model number. Run: py -3.13 analysis/src/overnight/25_conventions_and_cleanup.py
"""
import csv
import html
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
OUT = P("data", "processed", "overnight")

SPOT = 181.94          # 4 Sep 2026 close, the price every upside_pct in 13_valuation_summary.csv uses
SPOT_DATE = "2026-09-04"
TARGET_DATE = "2027-09-30"   # adopted 12-month target date (A12 decision 1)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("wrote %s (%d rows)" % (path, len(rows)))


# =====================================================================================================
# 1. Valuation conventions (A12 decision 1)
# =====================================================================================================
# metric_year / net_cash_year / shares_year are read off valuation() in 13_driver_model.py.
# "interim cash flows" means cash generated between the 4 Sep 2026 spot date and the value date.
LENSES = [
    dict(lens="EV / adj. EBITDA, FY27E", metric="Adjusted EBITDA", metric_year=2027, exit_basis="16.5x EV/EBITDA (bear 13.5x, bull 18.5x), WS12",
         net_cash_year=2027, shares_year=2027, value_date="2027-12-31",
         interim_cash_flows="Partly - only through the FY2027E net-cash balance and the buyback-reduced FY2027E share count. No flow is added or discounted separately.",
         in_football_field="yes"),
    dict(lens="EV / FCF, FY27E", metric="Free cash flow", metric_year=2027, exit_basis="14.3x EV/FCF (11.3x / 17.3x), WS12 haircut of the 5 Sep set",
         net_cash_year=2027, shares_year=2027, value_date="2027-12-31",
         interim_cash_flows="Partly - same as the EBITDA lens: FY2027E net cash and FY2027E shares only.",
         in_football_field="yes"),
    dict(lens="P / SBC-adjusted FCF, FY27E", metric="FCF less SBC", metric_year=2027, exit_basis="19.5x price multiple (15x / 24x)",
         net_cash_year="n/a", shares_year=2027, value_date="2027-12-31",
         interim_cash_flows="No - an equity multiple with no net-cash bridge. Interim cash appears only through the FY2027E share count.",
         in_football_field="yes"),
    dict(lens="P / earnings proxy, FY27E", metric="Modelled EPS (net income / modelled period-end shares)", metric_year=2027,
         exit_basis="19.5x the earnings proxy (15x / 24x)",
         net_cash_year="n/a", shares_year=2027, value_date="2027-12-31",
         interim_cash_flows="No - price = multiple x EPS. Interim cash appears only through the share count inside EPS.",
         in_football_field="yes"),
    dict(lens="EV / adj. EBITDA, FY28E", metric="Adjusted EBITDA", metric_year=2028, exit_basis="same 16.5x applied one year later",
         net_cash_year=2028, shares_year=2028, value_date="2028-12-31",
         interim_cash_flows="Partly - through the FY2028E net-cash balance and share count. THIS LENS IS A YEAR LATER THAN THE OTHER FIVE and is not discounted back.",
         in_football_field="yes"),
    dict(lens="DCF on FCF", metric="FY2027E FCF grown at the DCF start growth, fading to 3% over 10 years, then a Gordon terminal",
         metric_year=2027, exit_basis="Cost of equity 10.5%, terminal growth 3.0%",
         net_cash_year=2027, shares_year=2027, value_date="2027-12-31",
         interim_cash_flows="No - the strip's first discounted flow is FY2028E, discounted one period back to end-FY2027. FY2026-27 cash enters only via the FY2027E net-cash balance.",
         in_football_field="yes"),
    dict(lens="DCF on SBC-adjusted FCF", metric="FY2027E FCF less SBC on the same strip", metric_year=2027,
         exit_basis="Cost of equity 10.5%, terminal growth 3.0%",
         net_cash_year=2027, shares_year=2027, value_date="2027-12-31",
         interim_cash_flows="No - same strip as the DCF on FCF.",
         in_football_field="no - shown but excluded"),
    dict(lens="EV / adj. EBITDA, FY27E (5 Sep multiples 18/22/25.5x)", metric="Adjusted EBITDA", metric_year=2027,
         exit_basis="The superseded 5 Sep multiple set, kept as a documented alternative",
         net_cash_year=2027, shares_year=2027, value_date="2027-12-31",
         interim_cash_flows="Partly - as the EBITDA lens.",
         in_football_field="no - memo only"),
]


def valuation_conventions():
    px = {(r["scenario"], r["lens"]): float(r["price"])
          for r in read(P("data", "processed", "overnight", "13_valuation_summary.csv")) if r["price"] not in ("", None)}
    rows = []
    for L in LENSES:
        r = dict(L)
        for s in ("Bear", "Base", "Bull"):
            r["price_%s" % s.lower()] = round(px.get((s, L["lens"]), float("nan")), 2)
        r["spot_date"] = SPOT_DATE
        r["spot"] = SPOT
        r["target_date_adopted"] = TARGET_DATE
        r["upside_is"] = ("12-month expected price return from the %s spot of $%.2f to the adopted %s target. "
                          "It is NOT a discount to a present fair value." % (SPOT_DATE, SPOT, TARGET_DATE))
        rows.append(r)

    # Memo rows: what the football field averages, and the cost of the mixed dates.
    ann = {(a["scenario"], int(a["year"])): a for a in read(P("data", "processed", "overnight", "13_model_annual.csv"))}
    core = [L["lens"] for L in LENSES if L["in_football_field"] == "yes"]
    for s in ("Bear", "Base", "Bull"):
        vals = [px[(s, l)] for l in core]
        ex28 = [px[(s, l)] for l in core if "FY28E" not in l]
        rows.append(dict(
            lens="MEMO: football-field mean, %s" % s, metric="Mean of the six core lenses", metric_year="2027 (five lenses) and 2028 (one)",
            exit_basis="see the six rows above", net_cash_year="mixed", shares_year="mixed",
            value_date="mixed: five lenses at 2027-12-31, one at 2028-12-31",
            interim_cash_flows="mixed - see the component rows",
            in_football_field="the mean itself",
            price_bear=round(sum(vals) / len(vals), 2) if s == "Bear" else "",
            price_base=round(sum(vals) / len(vals), 2) if s == "Base" else "",
            price_bull=round(sum(vals) / len(vals), 2) if s == "Bull" else "",
            spot_date=SPOT_DATE, spot=SPOT, target_date_adopted=TARGET_DATE,
            upside_is=("Mean $%.2f. Dropping the FY2028E lens (the only one dated a year later, and the highest of the six) "
                       "gives $%.2f, i.e. the mixed date is worth $%.2f of the mean. Documented, not changed."
                       % (sum(vals) / len(vals), sum(ex28) / len(ex28), sum(vals) / len(vals) - sum(ex28) / len(ex28)))))

    # How much the adopted Sep-2027 target date differs from the end-2027 arithmetic, on the base EBITDA lens.
    a26, a27 = ann[("Base", 2026)], ann[("Base", 2027)]
    sh = float(a26["shares_end"]) + 0.75 * (float(a27["shares_end"]) - float(a26["shares_end"]))
    nc = float(a26["net_cash"]) + 0.75 * (float(a27["net_cash"]) - float(a26["net_cash"]))
    sep27 = (16.5 * float(a27["adj_ebitda"]) + nc) / sh
    rows.append(dict(
        lens="MEMO: end-FY2027 arithmetic vs a Sep-2027 target date, base EV/EBITDA lens",
        metric="16.5x FY2027E adj. EBITDA", metric_year=2027, exit_basis="16.5x",
        net_cash_year="interpolated 75% of the way from FY2026E to FY2027E", shares_year="same interpolation",
        value_date="2027-09-30", interim_cash_flows="as the EBITDA lens", in_football_field="no - memo",
        price_bear="", price_base=round(sep27, 2), price_bull="",
        spot_date=SPOT_DATE, spot=SPOT, target_date_adopted=TARGET_DATE,
        upside_is=("The model's own end-FY2027 answer is $%.2f. Straight-lining net cash and the share count to "
                   "30 Sep 2027 gives $%.2f, $%.2f lower (%.1f%%). The adopted Sep-2027 label is therefore very "
                   "slightly generous; no number was changed for it."
                   % (px[("Base", "EV / adj. EBITDA, FY27E")], sep27, px[("Base", "EV / adj. EBITDA, FY27E")] - sep27,
                      100 * (px[("Base", "EV / adj. EBITDA, FY27E")] / sep27 - 1)))))

    cols = ["lens", "metric", "metric_year", "exit_basis", "net_cash_year", "shares_year", "value_date",
            "target_date_adopted", "interim_cash_flows", "in_football_field",
            "price_bear", "price_base", "price_bull", "spot_date", "spot", "upside_is"]
    write(os.path.join(OUT, "25_valuation_conventions.csv"), rows, cols)


# =====================================================================================================
# 2. Source-ID remap (section 17 cleanup a)
# =====================================================================================================
REMAP = [
    ("S30", "S30", "FRED / BLS CPI: lodging away from home, airline fares, all items",
     "merged", "The union merge left two S30 rows for the same three FRED series. The second row's 'Used for' "
     "was a subset of the first's. The duplicate row was deleted; no source was lost."),
    ("S32", "S40", "Inside Airbnb listings.csv.gz dumps, 13 cities, 168 dumps Dec 2022 to Aug 2026",
     "renumbered", "Collided with S32 = Airbnb 10-K FY2025 geographic note and the 1Q21/2Q21 10-Q SBC footnotes, which keeps S32."),
    ("S33", "S41", "Common Crawl archive of airbnb.com/rooms listing pages",
     "renumbered", "Collided with S33 = SEC XBRL company facts for ABNB and six peers (capital-return panel), which keeps S33."),
    ("S34", "S42", "Driver model note (5 Sep) and model/assumptions.md; 30 Jun 2026 balance sheet",
     "renumbered", "Collided with S34 = capital-return panel note, which keeps S34."),
    ("S35", "S43", "Eurostat tour_ce_omr platform nights, EU27 and 31 countries",
     "renumbered", "Collided with S35 = Airbnb earnings-call transcripts / Q&A roster, which keeps S35."),
    ("S36", "S44", "SEC XBRL: unearned fees and funds held for clients (backlog indicators)",
     "renumbered", "Collided with S36 = transcript analytics note, which keeps S36."),
    ("S37", "S45", "Peer earnings releases: BKNG, EXPE, MAR, HLT 8-K Ex. 99.1, 93 filings",
     "renumbered", "Collided with S37 = regulatory forecast profile and its research log, which keeps S37."),
]


def source_remap():
    rows = [dict(old_id=o, new_id=n, source=s, action=a, reason=r,
                 file="research/sources/README.md", applied="2026-09-07", applied_by="WS25")
            for o, n, s, a, r in REMAP]
    rows.append(dict(old_id="(none)", new_id="(none)", source="All other IDs S1-S31, S38, S39",
                     action="unchanged", reason="No collision. S1-S45 are now unique and the table is sorted by ID.",
                     file="research/sources/README.md", applied="2026-09-07", applied_by="WS25"))
    write(os.path.join(OUT, "25_source_id_remap.csv"), rows,
          ["old_id", "new_id", "source", "action", "reason", "file", "applied", "applied_by"])


# =====================================================================================================
# 3. History reconciliation (section 17 cleanup c)
# =====================================================================================================
def letter_text(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t))


def history_reconciliation():
    stack = {r["quarter"]: r for r in read(P("data", "processed", "abnb_quarterly_cost_stack_exsbc.csv"))}
    cl = {r["quarter"]: r for r in read(P("data", "processed", "abnb_quarterly_costlines.csv"))}
    q = "4Q23"
    s, c = stack[q], cl[q]
    f = lambda d, k: float(d[k]) if d[k] not in ("", None) else 0.0

    gaap_lines = sum(f(c, k) for k in ("cost_of_revenue_musd", "operations_and_support_musd", "product_development_musd",
                                       "sales_and_marketing_musd", "general_and_administrative_musd", "restructuring_musd"))
    sbc_by_function_used = f(s, "sbc_total_letter")     # what the cash lines actually subtract
    sbc_xbrl = f(s, "sbc_total")                        # XBRL Q4 = FY less 9M
    adj = f(s, "adj_ebitda")
    implied = f(s, "adj_ebitda_implied")
    gap = f(s, "identity_gap")

    # The 4Q23 letter's own Adjusted EBITDA reconciliation and SBC-by-function footnote.
    t = letter_text(P("data", "raw", "letters", "4Q23_d646462dex991.htm"))
    m = re.search(r"Operations and support \$16 \$(\d+) .*?Stock-based compensation expense \$254 \$([\d,]+)", t)
    sbc_letter_4q23 = float(m.group(2).replace(",", "")) if m else 290.0
    recon_sbc = 290.0 if "Stock-based compensation expense $254 $290" in t or m else None

    rows = [
        dict(topic="4Q23 ex-SBC identity gap", item="Reported identity gap", value=gap, unit="$M",
             source="data/processed/abnb_quarterly_cost_stack_exsbc.csv, column identity_gap",
             finding="Adj. EBITDA implied by the cash stack ($%.0fM) less the letter's reported Adj. EBITDA ($%.0fM)." % (implied, adj)),
        dict(topic="4Q23 ex-SBC identity gap", item="GAAP cost and expense lines, 4Q23", value=gaap_lines, unit="$M",
             source="data/processed/abnb_quarterly_costlines.csv (XBRL, Q4 = FY less 9M)",
             finding="Revenue $%.0fM less these lines = GAAP operating income $%.0fM, which ties to the letter." % (f(c, "revenue_musd"), f(c, "operating_income_musd"))),
        dict(topic="4Q23 ex-SBC identity gap", item="SBC by function subtracted from the cash lines", value=sbc_by_function_used, unit="$M",
             source="abnb_exsbc_stack.py, letter SBC-by-function footnote parse (column pick)",
             finding="WRONG COLUMN. $254M is the three months ended 31 Dec 2022 column of the 4Q23 letter's footnote; "
                     "the 31 Dec 2023 column is $290M (ops 17, product development 179, sales and marketing 33, G&A 61)."),
        dict(topic="4Q23 ex-SBC identity gap", item="SBC in the letter's Adjusted EBITDA reconciliation, 4Q23", value=sbc_letter_4q23, unit="$M",
             source="data/raw/letters/4Q23_d646462dex991.htm, Adjusted EBITDA Reconciliation and SBC footnote",
             finding="Both the recon line and the footnote total for the quarter are $290M."),
        dict(topic="4Q23 ex-SBC identity gap", item="SBC used as the parser's target (XBRL, FY less 9M)", value=sbc_xbrl, unit="$M",
             source="data/processed/abnb_quarterly_costlines.csv, stock_based_comp_total_musd",
             finding="$270M, itself $20M below the letter's $290M because the Q4 XBRL value is derived as FY less 9M. "
                     "Because $254M is nearer $270M than $290M is, the nearest-column rule picked the prior-year column."),
        dict(topic="4Q23 ex-SBC identity gap", item="Gap fully explained", value=round(sbc_by_function_used - sbc_letter_4q23, 1), unit="$M",
             source="derived",
             finding="254 - 290 = -36, exactly the identity gap. Re-running the stack with the 31 Dec 2023 footnote column "
                     "closes it to zero: revenue 2,218 - (2,714 - 290) + D&A 16 + add-backs 928 = 738 = reported Adj. EBITDA. "
                     "No economics are involved; it is a column-selection defect."),
        dict(topic="4Q23 ex-SBC identity gap", item="Effect on the 4Q23 cash cost lines", value="", unit="$M",
             source="derived", finding="product development cash overstated by $29M, G&A by $9M, operations and support by $1M; "
                                       "sales and marketing understated by $3M. 4Q23 only. Every other quarter's gap is within +/-$1.7M "
                                       "and 1Q23-2Q26 are exactly zero, so no other quarter is affected."),
        dict(topic="4Q23 ex-SBC identity gap", item="Fix owner", value="", unit="",
             source="analysis/src/abnb_exsbc_stack.py, the nearest-column pick around line 176",
             finding="NOT FIXED BY WS25 (documentation-only workstream). The pick should prefer the column whose header year "
                     "matches the quarter, and fall back to nearest only when the header cannot be read."),
        dict(topic="20-vs-22-quarter history", item="Quarters in this tree's ex-SBC stack", value=len(stack), unit="quarters",
             source="data/processed/abnb_quarterly_cost_stack_exsbc.csv",
             finding="22 quarters, 1Q21-2Q26."),
        dict(topic="20-vs-22-quarter history", item="Quarters in the main tree's ex-SBC stack", value=20, unit="quarters",
             source="C:/Users/krish/citadel-abnb/data/processed/abnb_quarterly_cost_stack_exsbc.csv (read-only check, 7 Sep 2026)",
             finding="20 quarters, 3Q21-2Q26. It is a pre-merge build that predates the SBC_FALLBACK table in "
                     "abnb_exsbc_stack.py, which supplies 1Q21 and 2Q21 SBC by function from 10-Q accessions "
                     "0001628280-21-010389 and 0001628280-21-016979."),
        dict(topic="20-vs-22-quarter history", item="Quarters in the margin and capital-return panels", value=22, unit="quarters",
             source="abnb_capital_return_quarterly.csv, abnb_quarterly_kpis_from_study.csv, abnb_driver_history_quarterly.csv",
             finding="All 22, 1Q21-2Q26, and all agree with this tree's ex-SBC stack."),
        dict(topic="20-vs-22-quarter history", item="Resolution", value="", unit="",
             source="derived",
             finding="There is no live mismatch in this tree. The mismatch the audit saw is between the main tree's stale "
                     "20-quarter artifact and the merged 22-quarter history. Consolidate on this tree's file; do not "
                     "re-derive 1Q21/2Q21 from the letters, which do not carry an SBC-by-function footnote for them."),
    ]
    write(os.path.join(OUT, "25_history_reconciliation.csv"), rows, ["topic", "item", "value", "unit", "source", "finding"])


if __name__ == "__main__":
    valuation_conventions()
    source_remap()
    history_reconciliation()
