"""
Workstream 02, Part A: definitive quarterly KPI panel for Airbnb, 3Q20..2Q26.

Reads
  data/raw/letters/*.htm                       23 shareholder letters (8-K Ex. 99.1), 4Q20..2Q26
  data/raw/xbrl/ABNB_companyfacts.json         SEC company-facts (balance sheet, net income, tax, CFO, capex)
  data/processed/abnb_driver_history_quarterly.csv   nights, GBV, ADR, revenue, EBITDA, cost lines, SBC, FCF, buybacks, diluted shares
  data/processed/abnb_quarterly_costlines.csv        GAAP cost lines incl. 1Q20..4Q20, restructuring, operating income
  data/processed/abnb_quarterly_cost_stack_exsbc.csv ex-SBC cost lines (if present)
  data/processed/abnb_capital_return_quarterly.csv   CFO, capex, basic shares, RSU tax withholding
  theos-past-research/research/guidance/data/normalized/quarterly_actuals.csv  revenue cross-check
  data/processed/abnb_quarterly_kpis_from_study.csv  nights/GBV/ADR cross-check

Writes
  data/processed/overnight/02_kpi_panel_quarterly.csv   one row per quarter, wide
  data/processed/overnight/02_kpi_panel_long.csv        one row per (quarter, metric), with source quote and file
  data/processed/overnight/02_disclosure_changes.csv    metrics that started, stopped or changed definition, and when
  data/processed/overnight/02_crosscheck.csv            differences between sources for the same cell

Method
  Numeric statement items come from the existing processed CSVs (themselves built from the letters and XBRL) and
  from XBRL directly; narrative KPIs (regional growth, cross-border, urban, long-term stays, listings, app share,
  first-time bookers, guest arrivals, buyback authorisations, marketing commentary) are hand-coded from the letter
  text with a verbatim quote, and every quote is re-checked against the letter HTML at run time
  (source_verified column). Growth buckets ("mid-single digit") are mapped to a midpoint and flagged as buckets.

Run:  py -3.13 analysis/src/overnight/02_kpi_panel.py
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LETTERS = ROOT / "data/raw/letters"
OUT = ROOT / "data/processed/overnight"
OUT.mkdir(parents=True, exist_ok=True)

ORDER = ["3Q20", "4Q20", "1Q21", "2Q21", "3Q21", "4Q21", "1Q22", "2Q22", "3Q22", "4Q22", "1Q23", "2Q23", "3Q23",
         "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
LETTER_QS = ORDER[1:]


def qend(q: str) -> pd.Timestamp:
    n, y = int(q[0]), 2000 + int(q[2:])
    return pd.Timestamp(year=y, month=3 * n, day=1) + pd.offsets.MonthEnd(0)


# ----------------------------------------------------------------------------------------------
# 1. Letter text
# ----------------------------------------------------------------------------------------------
def letter_text(path: Path) -> str:
    s = path.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<style.*?</style>", "", s, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t).replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


LETTER_FILES = {p.name[:4]: p for p in LETTERS.glob("*.htm")}
TEXT = {q: letter_text(p) for q, p in LETTER_FILES.items()}


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[‘’“”—–�'\"\-]", " ", s)
    return re.sub(r"[^a-z0-9%$.]+", " ", s).strip()


NTEXT = {q: norm(t) for q, t in TEXT.items()}


def verify(q: str, quote: str) -> bool:
    if q not in NTEXT:
        return False
    return norm(quote) in NTEXT[q]


# ----------------------------------------------------------------------------------------------
# 2. Numeric statement items from processed CSVs + XBRL
# ----------------------------------------------------------------------------------------------
drv = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv").set_index("quarter")
cost = pd.read_csv(ROOT / "data/processed/abnb_quarterly_costlines.csv").set_index("quarter")
cap = pd.read_csv(ROOT / "data/processed/abnb_capital_return_quarterly.csv").set_index("quarter")
study = pd.read_csv(ROOT / "data/processed/abnb_quarterly_kpis_from_study.csv").set_index("quarter")
theo = pd.read_csv(ROOT / "theos-past-research/research/guidance/data/normalized/quarterly_actuals.csv")
theo["quarter"] = theo["fiscal_period"].str[5:6] + "Q" + theo["fiscal_period"].str[2:4]
theo = theo.set_index("quarter")
exsbc_path = ROOT / "data/processed/abnb_quarterly_cost_stack_exsbc.csv"
exsbc = pd.read_csv(exsbc_path).set_index("quarter") if exsbc_path.exists() else None

facts = json.load(open(ROOT / "data/raw/xbrl/ABNB_companyfacts.json"))["facts"]["us-gaap"]


def xbrl_frame(concept: str) -> pd.DataFrame:
    rows = []
    for unit, vals in facts.get(concept, {}).get("units", {}).items():
        for v in vals:
            rows.append(dict(start=v.get("start"), end=v["end"], val=v["val"], filed=v["filed"], form=v["form"]))
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["end"] = pd.to_datetime(df["end"])
    df["start"] = pd.to_datetime(df["start"])
    return df


def xbrl_instant(concept: str) -> pd.Series:
    df = xbrl_frame(concept)
    if df.empty:
        return pd.Series(dtype=float)
    df = df[df.start.isna()].sort_values("filed").groupby("end").last()
    return df["val"]


def xbrl_quarterly(concept: str) -> pd.Series:
    """Quarterly durations; Q4 derived as FY minus 9M where no quarterly fact exists."""
    df = xbrl_frame(concept)
    if df.empty:
        return pd.Series(dtype=float)
    df = df[df.start.notna()].copy()
    df["days"] = (df.end - df.start).dt.days
    df = df.sort_values("filed").groupby(["start", "end"]).last().reset_index()
    q = df[(df.days > 80) & (df.days < 100)].set_index("end")["val"]
    fy = df[(df.days > 350) & (df.days < 380)].set_index("end")["val"]
    nine = df[(df.days > 260) & (df.days < 285)].set_index("end")["val"]
    out = q.to_dict()
    for e, v in fy.items():
        prev = e - pd.offsets.QuarterEnd()
        if e not in out and prev in nine.index:
            out[e] = v - nine[prev]
    return pd.Series(out).sort_index()


XQ = {
    "net_income_musd": xbrl_quarterly("NetIncomeLoss") / 1e6,
    "income_tax_musd": xbrl_quarterly("IncomeTaxExpenseBenefit") / 1e6,
    "cfo_musd_xbrl": xbrl_quarterly("NetCashProvidedByUsedInOperatingActivities") / 1e6,
    "capex_musd_xbrl": xbrl_quarterly("PaymentsToAcquirePropertyPlantAndEquipment") / 1e6,
    "revenue_musd_xbrl": xbrl_quarterly("RevenueFromContractWithCustomerExcludingAssessedTax") / 1e6,
    "diluted_wa_shares_m_xbrl": xbrl_quarterly("WeightedAverageNumberOfDilutedSharesOutstanding") / 1e6,
}
XI = {
    "cash_and_equivalents_musd": xbrl_instant("CashAndCashEquivalentsAtCarryingValue") / 1e6,
    "short_term_investments_musd": xbrl_instant("ShortTermInvestments") / 1e6,
    "restricted_cash_musd": xbrl_instant("RestrictedCashAndCashEquivalents") / 1e6,
    "funds_held_for_clients_musd": xbrl_instant("FundsHeldForClients") / 1e6,
    "unearned_fees_musd": xbrl_instant("DeferredRevenueCurrent") / 1e6,
    "long_term_debt_musd": xbrl_instant("LongTermDebtNoncurrent") / 1e6,
}

# ----------------------------------------------------------------------------------------------
# 3. Regex-extracted headline items from the letters (reported vs ex-FX growth, ADR ex-FX)
# ----------------------------------------------------------------------------------------------
def pct(s: str) -> float:
    s = s.strip()
    neg = s.startswith("(")
    v = float(re.sub(r"[()%]", "", s))
    return -v if neg else v


def headline_exfx(q: str) -> dict:
    """Pull 'X% Y/Y' and 'Y% Y/Y (ex-FX)' for revenue and GBV from the letter body sentences."""
    t = TEXT.get(q, "")
    out = {}
    m = re.search(r"[Rr]evenue[^.]{0,80}?(?:grew|increase of|increased|up|representing a year-over-year increase of|representing a year-over-year change of)\s*(?:by\s*)?(\(?\d+\)?%)[^.]{0,40}?\(?(?:or\s*)?(\(?\d+\)?%)\s*(?:ex-FX|on a constant currency basis|increase on a constant currency)", t)
    if m:
        out["revenue_yoy_reported_pct"], out["revenue_yoy_exfx_pct"] = pct(m.group(1)), pct(m.group(2))
        out["_rev_quote"] = m.group(0)[:120]
    m = re.search(r"(?:GBV|Gross Booking Value)[^;:]{0,140}?(?:increase of|up|grew)\s*(\(?\d+\)?%)[^;:]{0,30}?\(?(?:or\s*)?(\(?\d+\)?%)\s*ex-FX", t)
    if not m:
        m = re.search(r"Gross Booking Value (\(?\d+\)?%) Y/Y (\(?\d+\)?%) Y/Y (?:\(?\d+\)?% Y/\dY )?(\(?\d+\)?%) Y/Y \(ex-FX\)", t)
        if m:
            out["gbv_yoy_reported_pct"], out["gbv_yoy_exfx_pct"] = pct(m.group(2)), pct(m.group(3))
            out["_gbv_quote"] = m.group(0)[:120]
    else:
        out["gbv_yoy_reported_pct"], out["gbv_yoy_exfx_pct"] = pct(m.group(1)), pct(m.group(2))
        out["_gbv_quote"] = m.group(0)[:120]
    if "revenue_yoy_exfx_pct" not in out:
        m = re.search(r"Revenue Net Income Adjusted EBITDA (\(?\d+\)?%) Y/Y .{0,60}?(\(?\d+\)?%) Y/Y \(ex-FX\)", t)
        if m:
            out["revenue_yoy_reported_pct"], out["revenue_yoy_exfx_pct"] = pct(m.group(1)), pct(m.group(2))
            out["_rev_quote"] = m.group(0)[:120]
    m = re.search(r"Excluding the impact of FX, ADR in Q\d 20\d\d (increased|decreased|declined) (less than 1|\d+)%", t)
    if m:
        v = 0.5 if m.group(2) == "less than 1" else float(m.group(2))
        out["adr_yoy_exfx_pct"] = v if m.group(1) == "increased" else -v
        out["_adr_quote"] = m.group(0)[:120]
    else:
        m = re.search(r"On an ex-FX basis, ADR in Q\d 20\d\d increased (\d+)%", t)
        if m:
            out["adr_yoy_exfx_pct"] = float(m.group(1)); out["_adr_quote"] = m.group(0)[:120]
        else:
            m = re.search(r"a (\d+)% increase from Q\d 20\d\d \(or (\d+)% ex-FX\)", t)
            if m:
                out["adr_yoy_exfx_pct"] = float(m.group(2)); out["_adr_quote"] = m.group(0)[:120]
            else:
                m = re.search(r"Excluding the impact of FX, ADR in Q\d 20\d\d increased across all regions, representing a year-over-year increase of (\d+)%", t)
                if m:
                    out["adr_yoy_exfx_pct"] = float(m.group(1)); out["_adr_quote"] = m.group(0)[:120]
    return out


# ----------------------------------------------------------------------------------------------
# 4. Hand-coded narrative KPIs (quarter, metric, value, unit, quote). Quotes are verified at run time.
#    Bucket map for "mid-single digit" style disclosures.
# ----------------------------------------------------------------------------------------------
BUCKET = {"low-single": 2, "low single": 2, "mid-single": 5, "mid single": 5, "high-single": 8, "high single": 8,
          "low-double": 11, "low double": 11, "low-teens": 12, "low teens": 12, "mid-teens": 15, "mid teens": 15,
          "high-teens": 18, "high teens": 18, "low-20s": 22, "approximately 20": 20, "~20": 20}

N = []  # narrative rows


def add(q, metric, value, unit, quote, note=""):
    N.append(dict(quarter=q, metric=metric, value=value, unit=unit, source_quote=quote[:120], note=note))


# --- Regional nights growth as stated (exact % where given, else bucket) ---
REG = {
    # quarter: (NA, EMEA, LatAm, APAC) each a (value, unit, quote)
    "3Q22": [("na", 20, "pct", "North America remained strong with Nights and Experiences Booked in Q3 increasing 20% above the level achieved in the same quarter of 2021"),
             ("emea", 20, "pct", "In EMEA, Nights and Experiences Booked grew 20% compared to Q3 2021"),
             ("latam", 33, "pct", "In Latin America, Nights and Experiences Booked were 33% higher than Q3 2021"),
             ("apac", 65, "pct", "APAC increased the most with 65% more Nights and Experiences Booked")],
    "4Q22": [("emea", 25, "pct", "In EMEA, Nights and Experiences Booked grew 25% compared to Q4 2021"),
             ("apac", 40, "pct", "Asia Pacific once again increased the most with 40% more Nights and Experiences Booked")],
    "1Q23": [("apac", 48, "pct", "48% growth in Nights and Experiences Booked in Q1 2023 compared to a year ago")],
    "2Q23": [("latam", 22, "pct", "In Latin America, Nights and Experiences Booked were 22% higher than Q2 2022"),
             ("apac", 24, "pct", "In Asia Pacific, Nights and Experiences Booked saw 24% year-over-year growth")],
    "3Q23": [("latam", 24, "pct", "In Latin America, Nights and Experiences Booked were 24% higher than Q3 2022"),
             ("apac", 27, "pct", "In Asia Pacific, Nights and Experiences Booked saw a sequential acceleration in year-over-year growth of 27%")],
    "4Q23": [("latam", 22, "pct", "In Latin America, Nights and Experiences Booked were 22% higher than Q4 2022"),
             ("apac", 22, "pct", "In Asia Pacific, Nights and Experiences Booked increased 22% on a year-over-year basis")],
    "1Q24": [("latam", 19, "pct", "In Latin America, Nights and Experiences Booked grew 19% in Q1 2024 compared to Q1 2023"),
             ("apac", 21, "pct", "In Asia Pacific, Nights and Experiences Booked increased 21% on a year-over-year basis")],
    "2Q24": [("latam", 17, "pct", "In Latin America, Nights and Experiences Booked grew 17% in Q2 2024 compared to Q2 2023"),
             ("apac", 19, "pct", "In Asia Pacific, Nights and Experiences Booked increased 19% on a year-over-year basis")],
    "3Q24": [("latam", 15, "pct", "In Latin America, Nights and Experiences Booked grew 15% in Q3 2024 compared to Q3 2023"),
             ("apac", 19, "pct", "In Asia Pacific, Nights and Experiences Booked increased 19% on a year-over-year basis")],
    "4Q24": [("na", "mid-single", "bucket", "In North America, we saw mid-single digits Nights and Experiences Booked growth in Q4 2024"),
             ("emea", "low-double", "bucket", "In EMEA, we saw low-double digits Nights and Experiences Booked growth in Q4 2024"),
             ("latam", "low-20s", "bucket", "In Latin America, we saw low-20s Nights and Experiences Booked growth in Q4 2024"),
             ("apac", "low-20s", "bucket", "In Asia Pacific, we saw low-20s Nights and Experiences Booked growth in Q4 2024")],
    "1Q25": [("na", "low-single", "bucket", "In North America, we saw low-single digits Nights and Experiences Booked growth in Q1 2025"),
             ("emea", "mid-single", "bucket", "In EMEA, we saw mid-single digits Nights and Experiences Booked growth in Q1 2025"),
             ("latam", "low-20s", "bucket", "In Latin America, we saw low-20s Nights and Experiences Booked growth in Q1 2025"),
             ("apac", "mid-teens", "bucket", "In Asia Pacific, we saw mid-teens Nights and Experiences Booked growth in Q1 2025")],
    "2Q25": [("na", "low-single", "bucket", "In North America, we saw low-single digit growth in Nights and Seats Booked during Q2 2025"),
             ("emea", "mid-single", "bucket", "In EMEA, we saw mid-single digit growth in Nights and Seats Booked during Q2 2025"),
             ("latam", "high-teens", "bucket", "In Latin America, we saw high-teens growth in Nights and Seats Booked during Q2 2025"),
             ("apac", "mid-teens", "bucket", "In Asia Pacific, we saw mid-teens growth in Nights and Seats Booked during Q2 2025")],
    "3Q25": [("na", "mid-single", "bucket", "In North America, we saw mid-single digit growth of Nights and Seats Booked during Q3 2025"),
             ("emea", "mid-single", "bucket", "In EMEA, we saw mid-single digit growth in Nights and Seats Booked during Q3 2025"),
             ("latam", "low-20s", "bucket", "In Latin America, we saw low-20s growth in Nights and Seats Booked during Q3 2025"),
             ("apac", "mid-teens", "bucket", "In Asia Pacific, we saw mid-teens growth in Nights and Seats Booked during Q3 2025")],
    "4Q25": [("na", "mid-single", "bucket", "In North America, we saw mid-single digit growth of Nights and Seats Booked during Q4 2025"),
             ("emea", "high-single", "bucket", "In EMEA, we saw high-single digit growth in Nights and Seats Booked during Q4 2025"),
             ("latam", "high-teens", "bucket", "In Latin America, we saw high-teens growth in Nights and Seats Booked during Q4 2025"),
             ("apac", "mid-teens", "bucket", "In Asia Pacific, we saw mid-teens growth in Nights and Seats Booked during Q4 2025")],
    "1Q26": [("na", "high-single", "bucket", "In North America, we saw high-single digit growth of Nights and Seats Booked during Q1 2026"),
             ("emea", "mid-single", "bucket", "In EMEA, we saw mid-single digit growth in Nights and Seats Booked during Q1 2026"),
             ("latam", "high-teens", "bucket", "In Latin America, we saw high-teens growth in Nights and Seats Booked during Q1 2026"),
             ("apac", "high-teens", "bucket", "In Asia Pacific, we saw high-teens growth in Nights and Seats Booked during Q1 2026")],
    "2Q26": [("na", "high-single", "bucket", "In North America, we saw high-single digit growth of Nights and Seats Booked during Q2 2026"),
             ("emea", "high-single", "bucket", "In EMEA, we saw high-single digit growth in Nights and Seats Booked during Q2 2026"),
             ("latam", "approximately 20", "bucket", "In Latin America, we saw approximately 20% growth in Nights and Seats Booked during Q2 2026"),
             ("apac", "high-teens", "bucket", "In Asia Pacific, we saw high-teens growth in Nights and Seats Booked during Q2 2026")],
}
for q, items in REG.items():
    for reg, v, unit, quote in items:
        if unit == "bucket":
            add(q, f"nights_yoy_{reg}_pct", BUCKET[v], "pct (bucket midpoint)", quote, note=f"bucket: {v}")
        else:
            add(q, f"nights_yoy_{reg}_pct", v, "pct", quote)

# Qualitative regional statements (direction only) for quarters with no number
QUAL = [
    ("4Q22", "nights_yoy_na_pct", "North America remained strong with continued growth in Nights and Experiences Booked"),
    ("1Q23", "nights_yoy_na_pct", "In Q1 2023, we saw stable growth in North American Nights and Experiences Booked compared to the prior quarter"),
    ("2Q23", "nights_yoy_na_pct", "we saw an acceleration in year-over-year growth in North American Nights and Experiences Booked compared to the prior quarter"),
    ("2Q23", "nights_yoy_emea_pct", "EMEA faced a hard year-over-year comparison resulting in a deceleration in Nights and Experiences Booked relative to Q1 2023"),
    ("3Q23", "nights_yoy_na_pct", "we saw a modest acceleration in year-over-year growth in North American Nights and Experiences Booked compared to the prior quarter"),
    ("3Q23", "nights_yoy_emea_pct", "we also saw a sequential improvement in the year-over-year growth rate of Nights and Experiences Booked in EMEA compared to the prior quarter"),
    ("4Q23", "nights_yoy_na_pct", "Continued solid growth of Nights and Experiences Booked in North America"),
    ("4Q23", "nights_yoy_emea_pct", "Stable growth of Nights and Experiences Booked compared to the prior quarter in EMEA"),
    ("1Q24", "nights_yoy_na_pct", "In North America, domestic travel was stable, while non-urban and larger group travel remained strong"),
    ("2Q24", "nights_yoy_na_pct", "In North America, we saw a slight acceleration of year-over-year growth in Q2 2024 Nights and Experiences Booked relative to Q1 2024"),
    ("2Q24", "nights_yoy_emea_pct", "we saw relatively stable year-over-year growth of Nights and Experiences Booked in EMEA compared to the prior quarter"),
    ("3Q24", "nights_yoy_na_pct", "After a slower start to the quarter, we saw year-over-year growth of Nights and Experiences Booked improve during Q3"),
]
for q, m, quote in QUAL:
    add(q, m + "_qual", quote[:60], "text", quote, note="direction only, no number")

# --- Cross-border share of gross nights and growth ---
CB = [("1Q21", 20, "up from 20% in Q1"), ("2Q21", 27, "up from 27% in Q2"), ("3Q21", 33, "Cross-border travel jumped to 33% of gross nights booked in Q3"),
      ("4Q21", 35, "recovering to nearly 35% of global gross nights booked in Q4 2021"), ("1Q22", 39, "up from 39% in Q1 2022"),
      ("2Q22", 43, "up from 43% in Q2 2022"), ("3Q22", 43, "cross-border was 43% (versus 48% in Q3 2019)"),
      ("4Q22", 44, "cross-border was 44% (versus 47% in Q4 2019)"), ("1Q23", 45, "cross-border represented 45% of total gross nights booked, up from 39% in Q1 2022"),
      ("2Q23", 45, "cross-border represented 45% of total gross nights booked, up from 43% in Q2 2022"),
      ("3Q23", 45, "cross-border represented 45% of total gross nights booked, up from 43% in Q3 2022"),
      ("4Q23", 44, "cross-border nights booked grew by 13% year-over-year and represented 44% of total gross nights booked"),
      ("1Q24", 46, "cross-border nights booked grew by 10% year-over-year and represented 46% of total gross nights booked")]
SRCQ = {"1Q21": "4Q21", "2Q21": "3Q21", "1Q22": "1Q23", "2Q22": "2Q23"}  # quarters whose value is quoted in a later letter
for q, v, quote in CB:
    add(q, "cross_border_share_pct", v, "pct of gross nights", quote, note=f"quoted in {SRCQ.get(q, q)} letter" if q in SRCQ else "")
CBG = [("3Q22", 58, "Cross border gross nights booked increased 58%"), ("4Q22", 49, "Cross-border gross nights booked increased 49%"),
       ("1Q23", 36, "Cross-border nights booked grew by 36% in Q1 2023"), ("2Q23", 16, "Cross-border nights booked grew by 16% in Q2 2023"),
       ("3Q23", 17, "Cross-border nights booked grew by 17% in Q3 2023"), ("4Q23", 13, "cross-border nights booked grew by 13% year-over-year"),
       ("1Q24", 10, "cross-border nights booked grew by 10% year-over-year")]
for q, v, quote in CBG:
    add(q, "cross_border_nights_yoy_pct", v, "pct", quote)

# --- High-density urban share of gross nights and growth ---
URB = [("1Q21", 41, "up from 41% in Q1 2021"), ("2Q21", 40, "High-density urban areas represented over 40% of our gross nights booked in Q2 2021"),
       ("3Q21", 46, "High-density urban areas represented 46% of our gross nights booked in Q3 2021"),
       ("4Q21", 49, "representing 49% of our gross nights booked in Q4 2021 compared to 46% in Q3 2021"),
       ("1Q22", 46, "representing 46% of our gross nights booked in Q1 2022, up from 41% in Q1 2021, but still down from 58% in Q1 2019"),
       ("2Q22", 47, "Gross nights booked to high-density urban areas represented 47% of our gross nights booked in Q2 2022"),
       ("3Q22", 48, "high-density urban nights booked was 48% of total gross nights booked (versus 58% in Q3 2019)"),
       ("4Q22", 51, "high-density urban nights booked was 51% of total gross nights booked (versus 59% in Q4 2019)"),
       ("1Q23", 48, "Gross nights booked in high-density urban areas represented 48% of our gross nights booked in Q1 2023"),
       ("2Q23", 48, "Gross nights booked in high-density urban areas represented 48% of our gross nights booked in Q2 2023"),
       ("3Q23", 49, "Gross nights booked in high-density urban areas represented 49% of our gross nights booked in Q3 2023"),
       ("4Q23", 51, "represented 51% of our gross nights booked in Q4 2023, consistent with Q4 2022, but still below 59% in Q4 2019")]
for q, v, quote in URB:
    add(q, "urban_share_pct", v, "pct of gross nights", quote, note="quoted in 1Q22 letter" if q == "1Q21" else "")
URBG = [("1Q22", 80, "Gross nights booked to high-density urban areas increased 80% in Q1 2022 compared to the same prior year quarter"),
        ("3Q22", 27, "high-density urban nights booked grew 27% compared to Q3 2021"), ("4Q22", 22, "high-density urban nights booked grew 22% compared to Q4 2021"),
        ("1Q23", 20, "High-density urban nights booked increased by 20% in Q1 2023"), ("2Q23", 13, "high-density urban nights booked increasing by 13% in Q2 2023"),
        ("3Q23", 15, "high-density urban nights booked increasing by 15% in Q3 2023"), ("4Q23", 11, "gross nights booked in high-density urban areas grew by 11% year-over-year")]
for q, v, quote in URBG:
    add(q, "urban_nights_yoy_pct", v, "pct", quote)
add("1Q24", "non_urban_nights_yoy_pct", 10, "pct", "In Q1 2024, gross nights booked in non-urban areas grew 10% year-over-year")

# --- Long-term stays (28+ nights) share of gross nights ---
LTS = [("1Q21", 24, "In Q1 2021, long-term stays represented 24% of nights booked"), ("3Q21", 20, "Long-term stays accounted for 20% of gross nights booked in Q3 2021, up from 14% in Q3 2019"),
       ("4Q21", 22, "Long-term stays accounted for 22% of gross nights booked in Q4 2021, up from 16% in Q4 2019"),
       ("1Q22", 21, "Long-term stays accounted for 21% of gross nights booked in Q1 2022, up from 13% in Q1 2019 and down from 24% in Q1 2021"),
       ("2Q22", 19, "Long-term stays accounted for 19% of gross nights booked in Q2 2022, up from 13% in Q2 2019 and flat with Q2 2021"),
       ("3Q22", 20, "long-term stays of 28 days or more accounted for 20% of gross nights booked in Q3 2022, stable with Q3 2021"),
       ("4Q22", 21, "long-term stays of 28 days or more accounted for 21% of gross nights booked in Q4 2022, stable with Q4 2021"),
       ("1Q23", 18, "long-term stays of 28 days or more accounted for 18% of gross nights booked, a decrease from 21% in Q4 2022"),
       ("2Q23", 18, "long-term stays of 28 days or more accounted for 18% of gross nights booked, relatively consistent with Q1 2023 and Q2 2022"),
       ("3Q23", 18, "long-term stays of 28 days or more remained steadfast, accounting for 18% of gross nights booked"),
       ("4Q23", 19, "long-term stays of 28 days accounted for 19% of gross nights booked, up slightly from the 18% level seen in Q3 2023"),
       ("1Q24", 17, "long-term stays of 28 days or more accounted for 17% of gross nights booked, compared to 18% in Q1 2023")]
for q, v, quote in LTS:
    add(q, "long_term_stays_share_pct", v, "pct of gross nights", quote)

# --- Active listings level and growth ---
AL = [("4Q21", 6.0, "6 million active listings at the end of 2021"), ("1Q22", 6.0, "We ended Q1 2022 with over 6 million active listings"),
      ("4Q22", 6.6, "We ended 2022 with 6.6 million active listings"), ("2Q23", 7.0, "exceed 7 million total active listings"),
      ("3Q23", 7.0, "With over 7 million active listings"), ("4Q23", 7.7, "over 7.7 million active listings around the world"),
      ("2Q24", 8.0, "we surpassed 8 million active listings"), ("3Q24", 8.0, "Today, we have over 8 million active listings"),
      ("4Q24", 8.0, "over 8 million active listings around the world"), ("4Q25", 9.0, "We ended 2025 with over 9 million active listings around the world")]
for q, v, quote in AL:
    add(q, "active_listings_m", v, "millions (rounded as stated)", quote)
ALG = [("3Q22", 15, "Active listings grew approximately 15% in Q3 2022 compared to a year ago"), ("4Q22", 16, "Active listings grew approximately 16% in Q4 2022 compared to a year ago"),
       ("1Q23", 18, "Active listings grew 18% in Q1 2023 compared to a year ago"), ("2Q23", 19, "Active listings grew 19% in Q2 2023 compared to a year ago"),
       ("3Q23", 19, "active listings grew 19% in Q3 2023 compared to a year ago"), ("4Q23", 18, "Active listings grew 18% in Q4 2023 compared to a year ago"),
       ("1Q24", 15, "Active listings grew 15% in Q1 2024 compared to a year ago")]
for q, v, quote in ALG:
    add(q, "active_listings_yoy_pct", v, "pct", quote)
add("1Q24", "active_listings_yoy_ex_removals_pct", 17, "pct", "active listings excluding experiences increased 17% in Q1 2024 compared to Q1 2023", note="ex quality-driven removals")
for q, quote in [("1Q25", "with supply growing approximately in-line with Nights and Experienced Booked"), ("2Q25", "with supply growing slightly above Nights and Seats Booked"),
                 ("3Q25", "with active listings growing approximately in-line with Nights and Seats Booked"), ("4Q25", "active listings grew relatively in-line with the year-over-year increase of Nights and Seats Booked"),
                 ("1Q26", "active listings grew relatively in-line with the year-over-year increase of Nights and Seats Booked")]:
    add(q, "active_listings_yoy_qual", quote[:60], "text", quote, note="relative to nights growth only; no number")

# --- App share of nights booked and app nights growth ---
APP = [("3Q22", 48, "compared to 48% in Q3 2022", "3Q23"), ("4Q22", 50, "compared to 50% in Q4 2022", "4Q23"), ("1Q23", 49, "up from 49% in Q1 2023", "1Q24"),
       ("2Q23", 50, "up from 50% in the prior-year period", "2Q24"), ("3Q23", 53, "53% of our gross nights booked in the Airbnb app compared to 48% in Q3 2022", "3Q23"),
       ("4Q23", 55, "55% of our gross nights booked in the Airbnb app during Q4 2023", "4Q23"), ("1Q24", 54, "representing 54% of total nights booked during the quarter", "1Q24"),
       ("2Q24", 55, "now comprises 55% of total nights booked, up from 50% in the prior-year period", "2Q24"), ("3Q24", 58, "App bookings now account for 58% of total nights booked", "3Q24"),
       ("4Q24", 60, "App bookings in Q4 accounted for 60% of total nights booked", "4Q24"), ("1Q25", 58, "App bookings in Q1 accounted for 58% of total nights booked", "1Q25"),
       ("2Q25", 59, "App bookings in Q2 accounted for 59% of total nights booked", "2Q25"), ("3Q25", 62, "App bookings in Q3 accounted for 62% of total nights booked", "3Q25"),
       ("4Q25", 64, "App bookings in Q4 accounted for 64% of total nights booked", "4Q25"), ("1Q26", 63, "accounting for 63% of total nights booked", "1Q26"),
       ("2Q26", 64, "accounting for 64% of total nights booked", "2Q26")]
for q, v, quote, src in APP:
    add(q, "app_share_of_nights_pct", v, "pct", quote, note=f"quoted in {src} letter" if src != q else "")
APPG = [("1Q24", 21, "Global nights booked through our mobile app increased 21% year-over-year"), ("2Q24", 19, "nights booked on our app during Q2 2024 increased 19% year-over-year"),
        ("3Q24", 18, "nights booked on our app increasing 18% year-over-year in Q3"), ("4Q24", 22, "nights booked on our app in Q4 increasing 22% year-over-year"),
        ("1Q25", 17, "nights booked on our app in Q1 2025 increasing 17% year-over-year"), ("2Q25", 17, "nights booked on our app in Q2 2025 increasing 17% year-over-year"),
        ("3Q25", 17, "nights booked on our app in Q3 2025 increasing 17% year-over-year"), ("4Q25", 20, "nights booked on our app in Q4 2025 increasing 20% year-over-year"),
        ("1Q26", 22, "nights booked on our app in Q1 2026 increasing 22% year-over-year"), ("2Q26", 23, "nights booked on our app in Q2 2026 increasing 23% year-over-year")]
for q, v, quote in APPG:
    add(q, "app_nights_yoy_pct", v, "pct", quote)

# --- First-time bookers (global) ---
for q, v, quote in [("4Q25", 8, "we saw year-over-year growth of first-time bookers accelerate to 8% in Q4 2025"),
                    ("1Q26", 10, "we saw year-over-year growth of first-time bookers accelerate to 10% in Q1 2026"),
                    ("2Q26", 11, "we saw year-over-year growth of first-time bookers accelerate to 11% in Q2 2026")]:
    add(q, "first_time_bookers_yoy_pct", v, "pct", quote)

# --- Cumulative guest arrivals (from 'About Airbnb' boilerplate and body) ---
for q, v, quote in [("4Q20", 0.8, "welcomed over 800 million guest arrivals"), ("2Q21", 0.9, "more than 900 million guest arrivals"),
                    ("3Q21", 1.0, "we reached a major milestone of 1 billion cumulative guest arrivals"), ("4Q22", 1.4, "we’ve now had 1.4 billion cumulative guest arrivals"),
                    ("2Q23", 1.5, "we’ve had more than 1.5 billion guest arrivals"), ("3Q24", 2.0, "welcomed over 2 billion guest arrivals"),
                    ("1Q26", 2.5, "welcomed over 2.5 billion guest arrivals")]:
    add(q, "guest_arrivals_cumulative_b", v, "billions", quote)
add("3Q22", "guest_arrivals_in_quarter_m", 90, "millions", "Globally, guest arrivals during the quarter exceeded 90 million")

# --- Fully diluted share count as stated in letters (end of quarter) ---
for q, v, quote, src in [("4Q21", 703, "from 703 million at the end of 2021 to 694 million at the end of 2022", "4Q22"), ("4Q22", 694, "694 million at the end of 2022", "4Q22"),
                    ("1Q22", 706, "from 706 million in Q1 2022 to 697 million at the end of Q1 2023", "1Q23"), ("1Q23", 697, "697 million at the end of Q1 2023", "1Q23"),
                    ("2Q22", 705, "from 705 million in Q2 2022 to 686 million at the end of Q2 2023", "2Q23"), ("2Q23", 686, "686 million at the end of Q2 2023", "2Q23"),
                    ("3Q22", 698, "from 698 million in Q3 2022 to 681 million at the end of Q3 2023", "3Q23"), ("3Q23", 681, "681 million at the end of Q3 2023", "3Q23")]:
    add(q, "fully_diluted_shares_letter_m", v, "millions", quote, note=f"quoted in {src} letter" if src != q else "")

# --- Buyback authorisations announced ---
for q, v, quote in [("2Q22", 2.0, "share repurchase program with authorization to purchase up to $2 billion of our Class A common stock"),
                    ("1Q23", 2.5, "new share repurchase authorization of up to $2.5 billion of our Class A common stock"),
                    ("4Q23", 6.0, "share repurchase program with authorization to purchase up to $6 billion of our Class A common stock"),
                    ("2Q25", 6.0, "new share repurchase program with authorization to purchase up to an additional $6 billion of our Class A common stock")]:
    add(q, "buyback_authorization_announced_busd", v, "USD billions", quote)

# --- Regional ADR y/y as stated ---
RADR = {"2Q23": [("na", -1, "ADR in North America decreased 1% compared to Q2 2022"), ("emea", 8, "ADR in EMEA grew 8% year-over-year")],
        "3Q23": [("na", -1, "ADR in North America decreased 1% compared to Q3 2022"), ("emea_exfx", 6, "our ADR in EMEA increased 6% compared to Q3 2022")],
        "4Q23": [("na", 0, "ADR in North America was flat in Q4 2023 compared to Q4 2022"), ("emea_exfx", 6, "our ADR in EMEA increased 6% compared to Q4 2022")],
        "1Q24": [("na", 3, "ADR in North America increased 3% in Q1 2024 compared to Q1 2023"), ("emea", 7, "ADR in EMEA increased 7% in Q1 2024")],
        "2Q24": [("na", 4, "ADR in North America increased 4% in Q2 2024 compared to Q2 2023"), ("emea", 4, "ADR in EMEA increased 4% in Q2 2024")],
        "3Q24": [("na", 3, "ADR in North America increased 3% in Q3 2024 compared to Q3 2023"), ("emea", 6, "ADR in EMEA increased 6% year-over-year in Q3 2024")],
        "4Q24": [("na", 3, "ADR in North America increased 3% in 9 Q4 2024 compared to Q4 2023"), ("emea", 6, "ADR increased 6% on a reported and FX-neutral basis in Q4 2024")],
        "1Q25": [("na", 2, "ADR in North America increased 2% in Q1 2025"), ("emea", 2, "ADR in EMEA increased 2% in Q1 2025"), ("latam", -7, "ADR in Latin America declined 7% in Q1 2025"), ("apac", -1, "ADR in Asia Pacific declined 1% in Q1 2025")],
        "2Q25": [("na", 3, "ADR in North America increased 3% in Q2 2025"), ("emea", 9, "ADR in EMEA increased 9% in Q2 2025"), ("latam", -3, "ADR in Latin America declined 3% in Q2 2025"), ("apac", 2, "ADR in Asia Pacific increased 2% in Q2 2025")],
        "3Q25": [("na", 5, "ADR in North America increased 8 5% in Q3 2025"), ("emea", 10, "ADR in EMEA increased 10% in Q3 2025"), ("latam", 4, "ADR in Latin America increased 4% in Q3 2025"), ("apac", 2, "ADR in Asia Pacific increased 2% in Q3 2025")],
        "4Q25": [("na", 5, "ADR in North America increased 5% in Q4 2025"), ("emea", 12, "ADR in EMEA increased 12% in Q4 2025"), ("latam", 9, "ADR in Latin America increased 9% in Q4 2025"), ("apac", 2, "ADR in Asia Pacific increased 2% in Q4 2025")],
        "1Q26": [("na", 7, "ADR in North America increased 7% in Q1 2026"), ("emea", 15, "ADR in EMEA increased 15% in Q1 2026"), ("latam", 10, "ADR in Latin America increased 10% in Q1 2026"), ("apac", 6, "ADR in Asia Pacific increased 6% in Q1 2026")],
        "2Q26": [("na", 7, "ADR in North America increased 7% in Q2 2026"), ("emea", 7, "ADR in EMEA increased 7% in Q2 2026"), ("latam", 9, "ADR in Latin America increased 9% in Q2 2026"), ("apac", 1, "ADR in Asia Pacific increased 1% in Q2 2026")]}
for q, items in RADR.items():
    for reg, v, quote in items:
        add(q, f"adr_yoy_{reg}_pct", v, "pct", quote, note="page-number artefact in quote" if " 8 5%" in quote or " 9 Q4" in quote else "")

# --- Marketing / S&M commentary (text) ---
MKT = [("4Q20", "we launched our first large-scale marketing campaign in five years"),
       ("1Q21", "Our strategy is to increase brand marketing and use the strength of our brand to attract more guests via direct or unpaid channels"),
       ("4Q21", "sales and marketing expense as a percent of revenue is expected to remain relatively flat"),
       ("1Q23", "we have pulled forward the timing of marketing spend to be more heavily weighted in the first half of the year"),
       ("4Q23", "In 2024, marketing spend will continue to be weighted more towards the first half of the year than the second half of the year"),
       ("1Q24", "with heavier spend expected in Q2 than in Q1"),
       ("3Q24", "in Q3, sales and marketing expense grew faster than revenue on a year-over-year basis, partially due to investments in global markets"),
       ("4Q24", "Adjusted EBITDA Margin during Q4 2024 was 31%, down compared to 33% in Q4 2023, due to investments in sales and marketing and product development"),
       ("1Q25", "Marketing expense is expected to grow faster than revenue on a year-over-year basis in Q2 2025"),
       ("4Q25", "as we reinvest top-line efficiencies to support growth across the business, primarily in marketing, product, and technology"),
       ("1Q26", "in Q1 alone we launched 16 local, digital-first marketing and communications programs"),
       ("2Q26", "In Q2, we leaned into local marketing campaigns in key growth markets")]
for q, quote in MKT:
    add(q, "marketing_commentary", quote[:80], "text", quote)

# --- Other one-offs worth carrying ---
add("4Q22", "active_listings_ex_china_yoy_pct", 26, "pct", "total active listings (excluding China) were up 26%", note="China domestic listings removed Jul-2022")
add("4Q22", "nights_ex_china_yoy_pct", 24, "pct", "nights booked (excluding China domestic) were up 24%")
add("1Q25", "na_share_of_nights_pct", 30, "pct", "North America contributes approximately 30% of our Nights and Experiences Booked")
add("1Q25", "nights_yoy_ex_na_pct", 11, "pct", "Excluding North America, Nights and Experiences Booked grew 11% year-over-year in Q1 2025")
add("4Q25", "travel_insurance_revenue_yoy_pct", 40, "pct", "revenue from guest travel insurance, which is available in 12 of our largest countries, increased approximately 40% year-over-year", note="full-year 2025")
add("1Q26", "travel_insurance_revenue_yoy_pct", 45, "pct", "revenue from guest travel insurance, which is available in 12 of our largest countries, increased 45% year-over-year")
add("3Q25", "removed_listings_cum_k", 550, "thousands", "we’ve removed over 9 550,000 listings", note="cumulative since 2023 quality system; page-number artefact")
add("1Q25", "removed_listings_cum_k", 450, "thousands", "we’ve removed over 450,000 listings")
add("3Q24", "removed_listings_cum_k", 300, "thousands", "we’ve removed over 300,000 listings")
add("4Q25", "cash_investments_restricted_letter_busd", 11.0, "USD billions", "we had $11.0 billion of cash and cash equivalents, short-term investments, and restricted cash")
add("4Q25", "funds_held_letter_busd", 7.0, "USD billions", "$7.0 billion of funds held on behalf of guests")
add("2Q26", "bedroom_nights_yoy_pct", 12, "pct", "Bedroom Nights Booked—nights booked multiplied by bedroom count— grew over 12%", note="new metric introduced 2Q26")
add("2Q26", "experiences_supply_yoy_pct", 80, "pct", "increasing Airbnb Experiences supply by nearly 80% year-over-year in Q2 2026")
add("4Q25", "single_fee_pct", 15.5, "pct", "to a 15.5% single service fee", note="fee simplification began Oct-2025")
add("1Q25", "cross_currency_share_of_gbv_pct", 20, "pct", "cross-currency transactions comprise approximately 20% of our GBV")

# ----------------------------------------------------------------------------------------------
# 5. Assemble the long file
# ----------------------------------------------------------------------------------------------
long_rows = []


def row(q, metric, value, unit, quote, src_file, verified, note=""):
    long_rows.append(dict(quarter=q, metric=metric, value=value, unit=unit, source_quote=str(quote)[:120],
                          source_file=src_file, source_verified=verified, note=note))


# 5a. statement items from processed CSVs (source = the CSV, which itself cites the letters / XBRL)
CSV_ITEMS = {
    "nights_m": ("drv", "nights_m", "millions"), "gbv_busd": ("drv", "gbv_b", "USD billions"), "adr_usd": ("drv", "adr", "USD"),
    "revenue_musd": ("drv", "revenue_musd", "USD millions"), "adj_ebitda_musd": ("drv", "adj_ebitda_musd", "USD millions"),
    "sbc_musd": ("drv", "stock_based_comp_total_musd", "USD millions"), "fcf_musd": ("drv", "fcf_musd", "USD millions"),
    "buybacks_musd": ("drv", "buybacks_musd", "USD millions"), "diluted_wa_shares_m": ("drv", "diluted_wa_shares_m", "millions"),
    "rsu_tax_withholding_musd": ("drv", "rsu_tax_withholding_musd", "USD millions"),
    "cost_of_revenue_musd": ("cost", "cost_of_revenue_musd", "USD millions"), "ops_support_musd": ("cost", "operations_and_support_musd", "USD millions"),
    "product_dev_musd": ("cost", "product_development_musd", "USD millions"), "sales_marketing_musd": ("cost", "sales_and_marketing_musd", "USD millions"),
    "g_and_a_musd": ("cost", "general_and_administrative_musd", "USD millions"), "restructuring_musd": ("cost", "restructuring_musd", "USD millions"),
    "operating_income_musd": ("cost", "operating_income_musd", "USD millions"),
    "cfo_musd": ("cap", "cfo_musd", "USD millions"), "capex_musd": ("cap", "capex_musd", "USD millions"), "basic_wa_shares_m": ("cap", "basic_wa_shares_m", "millions"),
}
SRC = {"drv": ("data/processed/abnb_driver_history_quarterly.csv", drv), "cost": ("data/processed/abnb_quarterly_costlines.csv", cost),
       "cap": ("data/processed/abnb_capital_return_quarterly.csv", cap)}
wide = pd.DataFrame(index=ORDER)
for metric, (src, col, unit) in CSV_ITEMS.items():
    fname, df = SRC[src]
    for q in ORDER:
        if q in df.index and col in df.columns and pd.notna(df.loc[q, col]):
            v = float(df.loc[q, col])
            wide.loc[q, metric] = v
            row(q, metric, v, unit, f"{fname}:{col}", fname, True)

# 3Q20 and 4Q20 KPIs from letter tables (not in driver CSV)
EARLY = {"3Q20": dict(nights_m=(61.8, "Nights and Experiences Booked 61.8 79.7"), gbv_busd=(8.0293, "Gross Booking Value $8,029.3 $11,891.6"), revenue_musd=(1342.3, "Revenue $ 839,004 $ 1,213,678 $ 1,645,761 $ 1,106,796 $ 841,830 $ 334,774 $ 1,342,331")),
         "4Q20": dict(nights_m=(46.3, "Nights and Experiences Booked* 75.8 46.3"), gbv_busd=(5.9057, "Gross Booking Value* $8,538.4 $5,905.7"))}
for q, items in EARLY.items():
    src_q = "3Q21" if q == "3Q20" else "4Q20"
    for metric, (v, quote) in items.items():
        wide.loc[q, metric] = v
        row(q, metric, v, CSV_ITEMS[metric][2], quote, f"letters/{LETTER_FILES[src_q].name}", verify(src_q, quote))
for q in ["3Q20", "4Q20"]:
    for metric, col, unit in [("revenue_musd", "revenue_musd", "USD millions"), ("adj_ebitda_musd", "adjusted_ebitda_musd", "USD millions")]:
        if pd.isna(wide.loc[q].get(metric, np.nan)) and q in cost.index:
            wide.loc[q, metric] = float(cost.loc[q, col])
            row(q, metric, float(cost.loc[q, col]), unit, f"data/processed/abnb_quarterly_costlines.csv:{col}", "data/processed/abnb_quarterly_costlines.csv", True)
wide.loc["3Q20", "adr_usd"] = round(8029.3 / 61.8, 2)
wide.loc["4Q20", "adr_usd"] = round(5905.7 / 46.3, 2)
for q in ["3Q20", "4Q20"]:
    row(q, "adr_usd", wide.loc[q, "adr_usd"], "USD", "GBV / nights (derived)", "derived", True)
# revenue 4Q20, adj EBITDA 3Q20/4Q20, cost lines from costlines CSV already loaded (1Q20..4Q20 rows exist)

# 5b. XBRL items
for metric, s in XQ.items():
    for q in ORDER:
        e = qend(q)
        if e in s.index and pd.notna(s[e]):
            wide.loc[q, metric] = round(float(s[e]), 1)
            row(q, metric, round(float(s[e]), 1), "USD millions" if "musd" in metric else "millions", "XBRL companyfacts (quarterly; Q4 = FY less 9M)", "data/raw/xbrl/ABNB_companyfacts.json", True)
for metric, s in XI.items():
    for q in ORDER:
        e = qend(q)
        if e in s.index and pd.notna(s[e]):
            wide.loc[q, metric] = round(float(s[e]), 1)
            row(q, metric, round(float(s[e]), 1), "USD millions", "XBRL companyfacts (instant)", "data/raw/xbrl/ABNB_companyfacts.json", True)
wide["cash_plus_st_investments_musd"] = wide[["cash_and_equivalents_musd", "short_term_investments_musd"]].sum(axis=1, min_count=2)

# 5c. regex headline items
for q in LETTER_QS:
    h = headline_exfx(q)
    for k, v in h.items():
        if k.startswith("_"):
            continue
        wide.loc[q, k] = v
        quote = h.get("_rev_quote" if k.startswith("revenue") else "_gbv_quote" if k.startswith("gbv") else "_adr_quote", "")
        row(q, k, v, "pct", quote, f"letters/{LETTER_FILES[q].name}", True)
# fill revenue reported/ex-FX from the driver CSV where the regex misses (it stores decimals)
for q in ORDER:
    if q in drv.index:
        if pd.isna(wide.loc[q].get("revenue_yoy_exfx_pct", np.nan)) and pd.notna(drv.loc[q, "yoy_growth_constant_currency"]):
            v = round(100 * float(drv.loc[q, "yoy_growth_constant_currency"]), 1)
            wide.loc[q, "revenue_yoy_exfx_pct"] = v
            row(q, "revenue_yoy_exfx_pct", v, "pct", "abnb_driver_history_quarterly.csv:yoy_growth_constant_currency", "data/processed/abnb_driver_history_quarterly.csv", True)
        if pd.isna(wide.loc[q].get("revenue_yoy_reported_pct", np.nan)) and pd.notna(drv.loc[q, "yoy_growth_reported"]):
            v = round(100 * float(drv.loc[q, "yoy_growth_reported"]), 1)
            wide.loc[q, "revenue_yoy_reported_pct"] = v
            row(q, "revenue_yoy_reported_pct", v, "pct", "abnb_driver_history_quarterly.csv:yoy_growth_reported", "data/processed/abnb_driver_history_quarterly.csv", True)

# 5d. narrative items
for r in N:
    q = r["quarter"]
    src_q = q
    m = re.search(r"quoted in (\w+) letter", r.get("note", "") or "")
    if m:
        src_q = m.group(1)
    if src_q not in LETTER_FILES:
        src_q = q
    ok = verify(src_q, r["source_quote"])
    row(q, r["metric"], r["value"], r["unit"], r["source_quote"], f"letters/{LETTER_FILES[src_q].name}" if src_q in LETTER_FILES else "letter", ok, r.get("note", ""))
    if isinstance(r["value"], (int, float)):
        wide.loc[q, r["metric"]] = r["value"]
    else:
        wide.loc[q, r["metric"]] = r["value"]

# ----------------------------------------------------------------------------------------------
# 6. Derived columns
# ----------------------------------------------------------------------------------------------
w = wide.copy()
num = lambda c: pd.to_numeric(w[c], errors="coerce") if c in w.columns else pd.Series(np.nan, index=w.index)
w["gbv_musd"] = num("gbv_busd") * 1000
w["take_rate_pct"] = (num("revenue_musd") / w["gbv_musd"] * 100).round(2)
w["adj_ebitda_margin_pct"] = (num("adj_ebitda_musd") / num("revenue_musd") * 100).round(1)
w["fcf_margin_pct"] = (num("fcf_musd") / num("revenue_musd") * 100).round(1)
w["net_income_margin_pct"] = (num("net_income_musd") / num("revenue_musd") * 100).round(1)
w["sbc_pct_revenue"] = (num("sbc_musd") / num("revenue_musd") * 100).round(1)
for c in ["cost_of_revenue_musd", "ops_support_musd", "product_dev_musd", "sales_marketing_musd", "g_and_a_musd"]:
    w[c.replace("_musd", "_pct_rev")] = (num(c) / num("revenue_musd") * 100).round(1)
# ex-SBC cost lines (from margin-drivers workstream if available)
if exsbc is not None:
    for c in exsbc.columns:
        if "exsbc" in c or "ex_sbc" in c or "cash" in c:
            for q in ORDER:
                if q in exsbc.index and pd.notna(exsbc.loc[q, c]):
                    w.loc[q, f"exsbc__{c}"] = exsbc.loc[q, c]
# y/y growth
YOY = {"nights_m": "nights", "gbv_musd": "gbv", "adr_usd": "adr", "revenue_musd": "revenue", "adj_ebitda_musd": "adj_ebitda", "fcf_musd": "fcf", "sbc_musd": "sbc",
       "sales_marketing_musd": "sales_marketing", "unearned_fees_musd": "unearned_fees", "funds_held_for_clients_musd": "funds_held"}
for c, nm in YOY.items():
    s = num(c)
    w[nm + "_yoy_pct"] = (s / s.shift(4) - 1) * 100
w["nights_yoy_accel_pts"] = w["nights_yoy_pct"].diff()
w["fx_pts_revenue"] = num("revenue_yoy_reported_pct") - num("revenue_yoy_exfx_pct")
w["adr_yoy_reported_pct"] = w["adr_yoy_pct"].round(1)
w["fx_pts_adr"] = w["adr_yoy_reported_pct"] - num("adr_yoy_exfx_pct")
w.index.name = "quarter"
w = w.round(2)
w.to_csv(OUT / "02_kpi_panel_quarterly.csv")

long = pd.DataFrame(long_rows)
long["quarter"] = pd.Categorical(long["quarter"], ORDER, ordered=True)
long = long.sort_values(["quarter", "metric"]).reset_index(drop=True)
long.to_csv(OUT / "02_kpi_panel_long.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 7. Disclosure starts / stops / redefinitions
# ----------------------------------------------------------------------------------------------
present = long[long["unit"] != "text"].groupby("metric")["quarter"].agg(["min", "max", "count"]).reset_index()
present["min"] = present["min"].astype(str); present["max"] = present["max"].astype(str)
present["stopped_before_2Q26"] = present["max"] != "2Q26"
present.to_csv(OUT / "02_metric_coverage.csv", index=False)

changes = [
    ("Nights and Experiences Booked -> Nights and Seats Booked", "2Q25", "rename with Services/Experiences relaunch (May 2025); series continuous, no restatement", "2Q25 letter headline"),
    ("Nights/GBV definition", "4Q20", "net of cancellations and alterations; management warned y/y comps 'volatile and unreliable' through 2021", "4Q20/1Q21 Outlook"),
    ("Growth comparisons indexed to 2019", "4Q21-2Q22", "management asked to index 2022 growth to 2019; y/y comps 'regain relevance' from 3Q22", "4Q21, 1Q22, 2Q22 Outlook"),
    ("China domestic listings removed", "3Q22", "all mainland China listings taken down Jul-2022; supply growth quoted ex-China from 4Q22", "4Q22 letter"),
    ("Presentation thousands -> millions", "2Q23", "financial tables re-rounded; 'certain immaterial amounts in prior periods reclassified'", "2Q23 letter"),
    ("Active listings growth %", "1Q24 last", "exact y/y growth disclosed 3Q22-1Q24 (15-19%); from 2Q24 only 'over 8 million'; from 1Q25 only 'in line with nights'", "letters"),
    ("Cross-border share and growth", "1Q24 last", "share (20%->46%) and growth disclosed 1Q21-1Q24; dropped from 2Q24 (only APAC cross-border growth 4Q24)", "letters"),
    ("High-density urban share", "4Q23 last", "share disclosed 1Q21-4Q23; 1Q24 gives non-urban growth only; dropped from 2Q24", "letters"),
    ("Long-term stays share", "1Q24 last", "28+ night share disclosed 1Q21-1Q24 (24%->17%); from 2Q24 only 'short-term outpaced long-term'", "letters"),
    ("Regional nights growth exact %", "3Q24 last", "exact % for LatAm/APAC 3Q22-3Q24 (NA/EMEA only 3Q22-4Q22); from 4Q24 buckets ('mid-single digit')", "letters"),
    ("Regional ADR y/y", "2Q23 start", "NA/EMEA from 2Q23; all four regions with ex-FX from 1Q25", "letters"),
    ("App share of nights", "3Q23 start", "new metric; rises 48% (3Q22 comp) -> 64% (2Q26)", "letters"),
    ("App nights growth", "1Q24 start", "17-23% y/y every quarter since", "letters"),
    ("First-time booker growth (global %)", "4Q25 start", "8%, 10%, 11%; earlier letters gave country-level only", "letters"),
    ("Expansion vs core market growth ratio", "1Q24 start", "'more than double' every quarter; never a level", "letters"),
    ("Bedroom Nights Booked", "2Q26 start", "new metric (nights x bedrooms) +12% vs nights +10%", "2Q26 letter"),
    ("Guest travel insurance revenue growth", "4Q25 start", "+40% FY25, +45% 1Q26; not repeated 2Q26", "letters"),
    ("Removed low-quality listings cumulative", "3Q24-4Q25", "300k -> 450k -> 550k; not in 1Q26/2Q26", "letters"),
    ("Y/2Y and Y/3Y and Y/4Y comparisons", "4Q23 last", "vs-2019 comparisons carried through 4Q23 headline tables then dropped", "letters"),
    ("Take-rate guide", "4Q22 start", "'implied take rate' guided each quarter from 4Q22 letter", "letters"),
    ("FY adj. EBITDA margin floor", "4Q23 start", "'at least 35%' FY24; 'at least 34.5%' FY25; 'stable' then 'at least 35%' then 'at least 35.5%' FY26", "letters"),
    ("FY revenue growth guide", "4Q25 start", "first FY revenue guide: 'at least low double digits' FY26, raised twice", "letters"),
    ("Hedging language in revenue guide", "2Q25 start", "'after factoring in our hedging program' appears from 2Q25", "letters"),
]
pd.DataFrame(changes, columns=["item", "when", "what_changed", "source"]).to_csv(OUT / "02_disclosure_changes.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 8. Cross-checks between sources
# ----------------------------------------------------------------------------------------------
cc = []
for q in ORDER:
    if q in drv.index and q in study.index:
        for a, b in [("nights_m", "nights_m"), ("gbv_b", "gbv_b"), ("adr", "adr"), ("revenue_musd", "revenue_musd"), ("adj_ebitda_musd", "adj_ebitda_musd")]:
            d = float(drv.loc[q, a]) - float(study.loc[q, b])
            if abs(d) > 0.05:
                cc.append(dict(quarter=q, metric=a, source_a="driver_history", value_a=drv.loc[q, a], source_b="kpis_from_study", value_b=study.loc[q, b], diff=d))
    if q in drv.index and q in theo.index:
        d = float(drv.loc[q, "revenue_musd"]) - float(theo.loc[q, "value"])
        if abs(d) > 0.5:
            cc.append(dict(quarter=q, metric="revenue_musd", source_a="driver_history", value_a=drv.loc[q, "revenue_musd"], source_b="theo_quarterly_actuals", value_b=theo.loc[q, "value"], diff=d))
    e = qend(q)
    if q in drv.index and e in XQ["revenue_musd_xbrl"].index:
        d = float(drv.loc[q, "revenue_musd"]) - float(XQ["revenue_musd_xbrl"][e])
        if abs(d) > 0.6:
            cc.append(dict(quarter=q, metric="revenue_musd", source_a="driver_history", value_a=drv.loc[q, "revenue_musd"], source_b="xbrl", value_b=round(float(XQ["revenue_musd_xbrl"][e]), 1), diff=d))
    if q in cap.index and e in XQ["cfo_musd_xbrl"].index and pd.notna(XQ["cfo_musd_xbrl"][e]):
        d = float(cap.loc[q, "cfo_musd"]) - float(XQ["cfo_musd_xbrl"][e])
        if abs(d) > 1:
            cc.append(dict(quarter=q, metric="cfo_musd", source_a="capital_return", value_a=cap.loc[q, "cfo_musd"], source_b="xbrl", value_b=round(float(XQ["cfo_musd_xbrl"][e]), 1), diff=d))
    if q in drv.index and e in XQ["diluted_wa_shares_m_xbrl"].index:
        xv = float(XQ["diluted_wa_shares_m_xbrl"][e])
        if xv > 100:
            d = float(drv.loc[q, "diluted_wa_shares_m"]) - xv
            if abs(d) > 1:
                cc.append(dict(quarter=q, metric="diluted_wa_shares_m", source_a="driver_history", value_a=drv.loc[q, "diluted_wa_shares_m"], source_b="xbrl", value_b=round(xv, 1), diff=d))
pd.DataFrame(cc).to_csv(OUT / "02_crosscheck.csv", index=False)

print("wide", w.shape, "long", long.shape, "unverified quotes:", int((~long.source_verified).sum()))
print(long[~long.source_verified][["quarter", "metric", "source_quote"]].to_string())
print("crosscheck rows:", len(cc))
print(pd.DataFrame(cc).to_string() if cc else "")
