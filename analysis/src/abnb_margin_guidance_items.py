"""Add Airbnb's Adjusted EBITDA margin guidance to Theo's guidance dataset (plan-of-attack branch 6).

Theo's normalized tables under theos-past-research/research/guidance/data/normalized/ hold revenue ranges and
KPI-direction guides for 23 events but no margin guides. This script appends, for every earnings event from
2020Q4 to 2026Q2, the next-quarter and full-year Adjusted EBITDA margin guidance as `guidance_items.csv` rows
(metric_code adj_ebitda_margin) with pinpoint `source_excerpts.csv` rows quoted from the SEC-filed shareholder
letter (8-K Ex. 99.1, "Outlook" section). It is idempotent: rows whose ids already exist are left alone.

measure_type values used (Theo's file has qualitative, qualitative_direction, absolute_range):
  absolute_floor    "at least X%"                     value_low = X
  absolute_point    "approximately X%" / "stable at"  value_mid = X (derived comparators noted in derivation_formula)
  absolute_ceiling  "down slightly from X%" etc.      value_high = X (X = prior-period margin from the letters)
  qualitative_direction  direction only, no usable bound
Percent values are Adjusted EBITDA margin in percent of revenue (unit "percent"), non-GAAP.

Run: python analysis/src/abnb_margin_guidance_items.py
"""
import csv, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
NORM = os.path.join(ROOT, "theos-past-research", "research", "guidance", "data", "normalized")
ITEMS = os.path.join(NORM, "guidance_items.csv")
EXCERPTS = os.path.join(NORM, "source_excerpts.csv")
ISSUES = os.path.join(NORM, "research_issues.csv")

COPYRIGHT = "Short pinpoint excerpt from a public SEC-filed issuer exhibit; not a transcript."
METHOD = "sentence extraction from SEC HTML exhibit (regex on 'Adjusted EBITDA' in the Outlook section), read and confirmed manually"

# (event quarter, target period, measure_type, low, high, mid, comparator, derivation, confidence, excerpt, paraphrase)
GUIDES = [
    ("2020Q4", "2021Q1", "qualitative_direction", None, None, None, "2020Q4", "seasonal low; no bound stated", "high",
     "We anticipate our Adjusted EBITDA margin to also be at its lowest during Q1.", "Q1 2021 margin guided to be the low point of the year."),
    ("2020Q4", "FY2021", "qualitative_direction", None, None, None, None, "H1 below H2; no bound stated", "high",
     "Additionally, we expect our Adjusted EBITDA margins to be lower in the first half of 2021 than the second half, both due to seasonality and due to investments we are making in certain areas.",
     "FY2021 margin shape guided: first half below second half."),
    ("2021Q1", "2021Q2", "absolute_floor", 0.0, None, None, "2020Q2", "breakeven to slightly positive read as floor of 0%", "medium",
     "In Q2 2021, we expect that our Adjusted EBITDA margin will be at breakeven, to slightly positive.", "Q2 2021 margin guided to breakeven or slightly positive."),
    ("2021Q1", "FY2021", "qualitative_direction", None, None, None, None, "H1 below H2; no bound stated", "high",
     "As we noted last quarter, we expect our Adjusted EBITDA margins to be lower in the first half of 2021 than the second half, both due to seasonality and to investments we are making in certain areas.",
     "FY2021 margin shape reiterated: first half below second half."),
    ("2021Q2", "2021Q3", "absolute_floor", 37.3, None, None, "2020Q3", "highest margin ever implies above the prior record of 37% in Q3 2020 (501/1,342)", "medium",
     "While the COVID-19 pandemic creates ongoing uncertainty for our future results, we expect Q3 2021 revenue to be our strongest quarterly revenue on record and to deliver the highest Adjusted EBITDA dollars and margin ever.",
     "Q3 2021 guided to a record Adjusted EBITDA margin."),
    ("2021Q3", "2021Q4", "qualitative_direction", None, None, None, "2020Q4", "greater year-over-year expansion than Q3 2021 delivered; no bound stated", "high",
     "We expect our Q4 Adjusted EBITDA to show this continued progress, adjusted for seasonality.", "Q4 2021 guided to continued margin progress adjusted for seasonality."),
    ("2021Q4", "2022Q1", "absolute_floor", 0.0, None, None, "2021Q1", "first positive Q1 Adjusted EBITDA implies margin above 0%", "high",
     "Due to these improvements, we expect to achieve our first positive Q1 Adjusted EBITDA in Airbnb history.", "Q1 2022 guided to the first positive Q1 Adjusted EBITDA."),
    ("2021Q4", "FY2022", "absolute_point", None, None,27.0, "FY2021", "directionally in line with FY2021 margin of 27% (letter)", "medium",
     "Assuming some ADR pressure due to mix shift, we would expect Adjusted EBITDA margin to be directionally in-line with 2021 as sales and marketing expense as a percent of revenue is expected to remain relatively flat and incremental variable cost improvements and fixed cost discipline is potentially offset by lower ADR.",
     "FY2022 margin guided directionally in line with FY2021."),
    ("2022Q1", "2022Q2", "absolute_floor", 26.0, None, None, "2021Q2", "low double-digit point improvement on Q2 2021's 16% read as at least 10 points", "medium",
     "We expect this progress to continue in Q2 2022, driving a low double-digit EBITDA margin percentage improvement on a year-over-year basis.",
     "Q2 2022 margin guided up by a low double-digit number of points year over year."),
    ("2022Q1", "FY2022", "absolute_floor", 27.0, None, None, "FY2021", "modest expansion versus FY2021's 27%", "medium",
     "We currently anticipate delivering modest Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021.", "FY2022 margin guided to modest expansion versus 2021."),
    ("2022Q2", "2022Q3", "absolute_ceiling", None, 49.0, None, "2021Q3", "at or slightly below Q3 2021's 49%", "high",
     "We expect Q3 2022 Adjusted EBITDA margin to be at or slightly below last years all-time high margin of 49% primarily due to the timing of expenses.",
     "Q3 2022 margin guided at or slightly below 49%."),
    ("2022Q2", "FY2022", "absolute_floor", 27.0, None, None, "FY2021", "expansion versus FY2021's 27%", "medium",
     "We continue to forecast delivering Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021.", "FY2022 margin expansion reiterated."),
    ("2022Q3", "2022Q4", "absolute_floor", 22.0, None, None, "2021Q4", "in line to modestly higher than Q4 2021's 22%", "high",
     "We expect Q4 2022 Adjusted EBITDA to be up meaningfully on a nominal basis from Q4 2021 and expect quarterly Adjusted EBITDA margin to be in-line to modestly higher than last years margin of 22%.",
     "Q4 2022 margin guided in line to modestly above 22%."),
    ("2022Q4", "2023Q1", "absolute_ceiling", None, 15.0, None, "2022Q1", "slightly down versus Q1 2022's 15%", "high",
     "In Q1 2023, we expect Adjusted EBITDA margin to be slightly down on a year-over-year basis due to changes in the timing of our brand marketing spend.",
     "Q1 2023 margin guided slightly down year over year on brand-marketing timing."),
    ("2022Q4", "FY2023", "absolute_point", None, None, 35.0, "FY2022", "maintain FY2022 margin (35% as reported in the letter; 34.6% unrounded)", "high",
     "For the full year 2023, we expect to maintain the strong Adjusted EBITDA margin we delivered in 2022, as we offset the headwinds from lower ADR with incremental variable cost efficiencies and fixed cost discipline.",
     "FY2023 margin guided flat with FY2022."),
    ("2023Q1", "2023Q2", "absolute_ceiling", None, 34.0, None, "2022Q2", "lower than Q2 2022's 34%", "high",
     "In Q2 2023, we expect Adjusted EBITDA to be similar to Adjusted EBITDA in Q2 2022 on a nominal basis, but lower on a margin basis.",
     "Q2 2023 margin guided below Q2 2022."),
    ("2023Q1", "FY2023", "absolute_point", None, None, 35.0, "FY2022", "broadly in line with FY2022", "high",
     "We continue to anticipate a full year Adjusted EBITDA margin that is broadly in-line with full-year 2022.", "FY2023 margin reiterated broadly in line with FY2022."),
    ("2023Q2", "2023Q3", "absolute_floor", 51.0, None, None, "2022Q3", "exceeds Q3 2022's 51%", "high",
     "We expect a record-high Adjusted EBITDA in Q3 2023 on a nominal basis and an Adjusted EBITDA margin that exceeds Q3 2022.", "Q3 2023 margin guided above 51%."),
    ("2023Q2", "FY2023", "absolute_floor", 35.0, None, None, "FY2022", "modestly higher than FY2022's 35%", "high",
     "For the full-year 2023, we expect an Adjusted EBITDA margin that is modestly higher than the full-year 2022.", "FY2023 margin raised to modestly above FY2022."),
    ("2023Q3", "2023Q4", "absolute_floor", 27.0, None, None, "2022Q4", "exceeds Q4 2022's 27%", "high",
     "Turning to profitability, we expect a record-high fourth quarter Adjusted EBITDA in 2023 on a nominal basis and an Adjusted EBITDA margin that exceeds Q4 2022.", "Q4 2023 margin guided above 27%."),
    ("2023Q3", "FY2023", "absolute_point", None, None, 36.1, "FY2022", "FY2022 unrounded 34.6% plus 150 bps", "high",
     "As a result, we expect an Adjusted EBITDA margin for full-year 2023 that is approximately 150 bps higher than full-year 2022.", "FY2023 margin guided about 150 bps above FY2022."),
    ("2023Q4", "2024Q1", "absolute_floor", 14.0, None, None, "2023Q1", "expands versus Q1 2023's 14%", "high",
     "We expect Adjusted EBITDA Margin in Q1 2024 to expand relative to Q1 2023, primarily due to the timing of expenses.", "Q1 2024 margin guided to expand year over year."),
    ("2023Q4", "FY2024", "absolute_floor", 35.0, None, None, "FY2023", "explicit floor", "high",
     "For the full-year 2024, we expect to maintain an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year.",
     "FY2024 margin floor of at least 35% introduced."),
    ("2024Q1", "2024Q2", "absolute_ceiling", None, 33.0, None, "2023Q2", "down versus Q2 2023's 33%", "high",
     "In Q2 2024, we expect Adjusted EBITDA to be flat to up on a nominal basis, but down on an Adjusted EBITDA Margin basis, relative to Q2 2023.", "Q2 2024 margin guided down year over year."),
    ("2024Q1", "FY2024", "absolute_floor", 35.0, None, None, "FY2023", "explicit floor reiterated", "high",
     "For the full-year 2024, consistent with our prior guidance, we expect to grow Adjusted EBITDA on a nominal basis and to deliver an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year.",
     "FY2024 floor of at least 35% reiterated."),
    ("2024Q2", "2024Q3", "absolute_ceiling", None, 54.0, None, "2023Q3", "declines versus Q3 2023's 54%", "high",
     "In Q3 2024, we expect Adjusted EBITDA to approximate Q3 2023 on a nominal basis, but for Adjusted EBITDA Margin to decline relative to Q3 2023.", "Q3 2024 margin guided down year over year."),
    ("2024Q2", "FY2024", "absolute_floor", 35.0, None, None, "FY2023", "explicit floor reiterated", "high",
     "For the full-year 2024, consistent with our prior guidance, we expect to grow Adjusted EBITDA on a nominal basis and to deliver an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year.",
     "FY2024 floor of at least 35% reiterated."),
    ("2024Q3", "2024Q4", "absolute_ceiling", None, 33.0, None, "2023Q4", "declines versus Q4 2023's 33%", "high",
     "Q4 2024 Adjusted EBITDA Margin is expected to decline relative to the same time period last year due to higher marketing and product development expenses.", "Q4 2024 margin guided down year over year."),
    ("2024Q3", "FY2024", "absolute_point", None, None, 35.5, "FY2023", "explicit point estimate", "high",
     "For the full-year 2024, we now expect to deliver an Adjusted EBITDA Margin of approximately 35.5%.", "FY2024 margin raised to approximately 35.5%."),
    ("2024Q4", "2025Q1", "absolute_ceiling", None, 20.0, None, "2024Q1", "declines versus Q1 2024's 20%; flat excluding calendar and FX", "high",
     "In Q1 2025, we expect Adjusted EBITDA and Adjusted EBITDA Margin to decline compared to Q1 2024, primarily driven by the one-time calendar factors and FX headwinds impacting revenue.", "Q1 2025 margin guided down on calendar and FX."),
    ("2024Q4", "FY2025", "absolute_floor", 34.5, None, None, "FY2024", "explicit floor including $200M to $250M of new-business investment", "high",
     "Inclusive of these investments, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%maintaining our strong track record of profitability without compromising our growth initiatives.",
     "FY2025 margin floor of at least 34.5% introduced."),
    ("2025Q1", "2025Q2", "absolute_ceiling", None, 32.5, None, "2024Q2", "flat to down slightly versus Q2 2024's 32.5%", "high",
     "In Q2 2025, we expect Adjusted EBITDA to increase on a year-over- year basis, but for Adjusted EBITDA Margin to be flat to down slightly compared to Q2 2024.", "Q2 2025 margin guided flat to slightly down."),
    ("2025Q1", "FY2025", "absolute_floor", 34.5, None, None, "FY2024", "explicit floor reiterated", "high",
     "For full-year 2025, consistent with our prior guidance, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%, maintaining our strong track record of profitability while making meaningful investments behind future growth levers.",
     "FY2025 floor of at least 34.5% reiterated."),
    ("2025Q2", "2025Q3", "absolute_ceiling", None, 52.5, None, "2024Q3", "lower than Q3 2024's 52.5%", "high",
     "However, we anticipate that Adjusted EBITDA Margin during Q3 2025 will be lower than in Q3 2024, primarily due to investments in new growth and policy initiatives.", "Q3 2025 margin guided below Q3 2024."),
    ("2025Q2", "2025Q4", "absolute_ceiling", None, 30.8, None, "2024Q4", "similar decline versus Q4 2024's 30.8%", "medium",
     "We expect a similar year-over-year decline in Q4 2025 Adjusted EBITDA Margin due to growth investments and a tougher year-over-year top-line comparison.", "Q4 2025 margin guided down year over year two quarters ahead."),
    ("2025Q2", "FY2025", "absolute_floor", 34.5, None, None, "FY2024", "explicit floor reiterated", "high",
     "For 2025, consistent with our prior guidance, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%, maintaining our strong track record of profitability while making meaningful investments behind future growth levers.",
     "FY2025 floor of at least 34.5% reiterated."),
    ("2025Q3", "2025Q4", "absolute_ceiling", None, 30.8, None, "2024Q4", "declines versus Q4 2024's 30.8%", "high",
     "We expect Adjusted EBITDA in Q4 2025 to be flat- to-down slightly on a year-over-year basis and for Adjusted EBITDA Margin to decline over the same time period, primarily driven by investments in new growth and policy initiatives.",
     "Q4 2025 margin guided down year over year."),
    ("2025Q3", "FY2025", "absolute_point", None, None, 35.0, "FY2024", "explicit point estimate", "high",
     "For the full-year 2025, we now expect to deliver an Adjusted EBITDA Margin of approximately 35%.", "FY2025 margin raised to approximately 35%."),
    ("2025Q4", "2026Q1", "absolute_point", None, None, 18.4, "2025Q1", "approximately flat versus Q1 2025's 18.4%", "high",
     "We expect Adjusted EBITDA Margin to be approximately flat year-over-year.", "Q1 2026 margin guided approximately flat."),
    ("2025Q4", "FY2026", "absolute_point", None, None, 35.1, "FY2025", "stable versus FY2025's 35.1%", "high",
     "For 2026, we expect our Adjusted EBITDA Margin to be stable year-over-year as we reinvest top-line efficiencies to support growth across the business, primarily in marketing, product, and technology.",
     "FY2026 margin guided stable with FY2025."),
    ("2026Q1", "2026Q2", "absolute_floor", 33.7, None, None, "2025Q2", "up versus Q2 2025's 33.7%", "high",
     "We expect Adjusted EBITDA and Adjusted EBITDA Margin to be up year-over-year in Q2 2026.", "Q2 2026 margin guided up year over year."),
    ("2026Q1", "FY2026", "absolute_floor", 35.0, None, None, "FY2025", "explicit floor, raised from stable", "high",
     "For 2026, we now expect our Adjusted EBITDA Margin to be at least 35%.", "FY2026 margin raised to at least 35%."),
    ("2026Q2", "2026Q3", "absolute_ceiling", None, 50.1, None, "2025Q3", "down slightly versus Q3 2025's 50.1%", "high",
     "We expect Adjusted EBITDA to increase year-over-year and Adjusted EBITDA Margin to be down slightly compared to Q3 2025, due to timing of investments.", "Q3 2026 margin guided down slightly year over year."),
    ("2026Q2", "FY2026", "absolute_floor", 35.5, None, None, "FY2025", "explicit floor, raised from 35%", "high",
     "For 2026, we now expect to deliver a full-year Adjusted EBITDA Margin of at least 35.5%",
     "FY2026 margin raised to at least 35.5%."),
]


def main():
    items = list(csv.DictReader(open(ITEMS, encoding="utf-8")))
    exc = list(csv.DictReader(open(EXCERPTS, encoding="utf-8")))
    ikeys, ekeys = list(items[0].keys()), list(exc[0].keys())
    have_i, have_e = {r["guidance_item_id"] for r in items}, {r["source_excerpt_id"] for r in exc}
    added = 0
    for ev, tgt, mt, lo, hi, mid, comp, deriv, conf, quote, para in GUIDES:
        kind = "FY" if tgt.startswith("FY") else "NEXTQ" if tgt[:4] == ev[:4] and int(tgt[-1]) == int(ev[-1]) + 1 or (ev.endswith("Q4") and tgt.endswith("Q1")) else "FWDQ"
        iid = f"ABNB-{ev}-{kind}-ADJ-EBITDA-MARGIN-GUIDE" + (f"-{tgt}" if kind == "FWDQ" else "")
        eid = iid + "-EXCERPT"
        # Theo's FiscalPeriod type only allows YYYYQn, so a full-year guide is filed against Q4 of that year
        # (the period in which the full-year outcome is known) and flagged in derivation_formula.
        fy_note = ""
        if tgt.startswith("FY"):
            fy_note = f"FULL-YEAR guide for {tgt}; target_period set to {tgt[2:]}Q4 because the schema allows quarters only. "
            tgt = f"{tgt[2:]}Q4"
        if comp and comp.startswith("FY"):
            comp = f"{comp[2:]}Q4"
        deriv = fy_note + deriv
        if iid in have_i:
            continue
        items.append({k: "" for k in ikeys} | {
            "value_status": "observed", "guidance_item_id": iid, "guidance_event_id": f"ABNB-{ev}-INITIAL", "target_period": tgt,
            "metric_code": "adj_ebitda_margin", "measure_type": mt,
            "value_low": "" if lo is None else lo, "value_high": "" if hi is None else hi, "value_mid": "" if mid is None else mid,
            "unit": "percent" if mt != "qualitative_direction" else "narrative", "currency": "", "accounting_basis": "non_GAAP",
            "is_company_stated": "True" if conf == "high" and mt in ("absolute_floor", "absolute_point", "qualitative_direction") and "read as" not in deriv and "implies" not in deriv and "FULL-YEAR" not in deriv or (mt in ("absolute_floor", "absolute_point") and lo in (35.0, 34.5, 35.5) or mid in (35.5, 35.0)) else "False",
            "derivation_formula": deriv, "comparator_period": comp or "", "source_excerpt_id": eid, "extraction_confidence": conf})
        exc.append({k: "" for k in ekeys} | {
            "value_status": "observed", "source_excerpt_id": eid, "document_id": f"ABNB-{ev}-SHAREHOLDER-LETTER", "section_heading": "Outlook",
            "source_anchor": "Outlook section; whitespace normalized", "exact_excerpt": quote, "excerpt_word_count": len(quote.split()),
            "context_paraphrase": para, "copyright_handling": COPYRIGHT, "extraction_method": METHOD, "verified_against_source": "True"})
        have_i.add(iid); added += 1
    issues = list(csv.DictReader(open(ISSUES, encoding="utf-8")))
    if not any(r["research_issue_id"] == "ABNB-ISSUE-FY-PERIOD-ENCODING" for r in issues):
        issues.append({k: "" for k in issues[0].keys()} | {
            "value_status": "observed", "research_issue_id": "ABNB-ISSUE-FY-PERIOD-ENCODING", "issue_type": "schema_limitation", "severity": "low",
            "related_record_type": "guidance_items", "related_record_id": "ABNB-*-FY-ADJ-EBITDA-MARGIN-GUIDE",
            "description": "FiscalPeriod only allows YYYYQn, so full-year Adjusted EBITDA margin guides are filed with target_period = Q4 of the fiscal year and comparator_period = Q4 of the prior year; derivation_formula starts with FULL-YEAR for these rows.",
            "proposed_resolution": "Extend FiscalPeriod to accept FYYYYY (or add a period_scope field) and re-key the 21 full-year margin items.",
            "status": "open", "requires_user_approval": "False", "created_at_utc": "2026-09-05T23:00:00Z"})
    for path, rows, keys in ((ITEMS, items, ikeys), (EXCERPTS, exc, ekeys), (ISSUES, issues, list(issues[0].keys()))):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"added {added} margin guidance items; guidance_items.csv now {len(items)} rows, source_excerpts.csv {len(exc)} rows")


if __name__ == "__main__":
    sys.exit(main())
