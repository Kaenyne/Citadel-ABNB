"""
Workstream 02, Part B: full Airbnb guidance ledger, 4Q20 print .. 2Q26 print.

Reads
  data/raw/letters/*.htm                                   23 shareholder letters (8-K Ex. 99.1) - the Outlook sections
  data/raw/regulatory/transcripts/*.json|*.txt             IR call transcripts (2023Q1..2026Q2) - guides given only on the call
  data/processed/overnight/02_kpi_panel_quarterly.csv      actuals (Part A of this workstream)
  theos-past-research/research/guidance/data/normalized/guidance_items.csv   cross-check of the 100 rows Theo already has

Writes
  data/processed/overnight/02_guidance_ledger.csv          one row per guidance statement per print
  data/processed/overnight/02_guidance_coverage.csv        which guide types exist in which print, and the count per print
  data/processed/overnight/02_fy_guide_revisions.csv       the path of each full-year guide through its year

Method
  Every guide is hand-transcribed from the letter Outlook (or the named transcript) with a verbatim quote of <=150 chars,
  and the quote is re-checked against the source text at run time (column `verified`). Buckets ("mid-single digit",
  "low teens") are mapped to explicit ranges; the map is printed in the note. Actuals come from the Part A panel;
  full-year actuals are the sum/ratio of the four quarters in that panel. Outcome logic:
    range  -> above_range / within_range / below_range, plus distance from midpoint
    floor  -> met / not_met, cushion = actual - floor
    ceiling-> met / not_met, cushion = ceiling - actual
    point  -> distance from the point (beat if above for "more is better" metrics)
    directional -> met / not_met against the stated comparator
  Anything whose target period has not reported yet is `pending`.

Run:  py -3.13 analysis/src/overnight/02_guidance_ledger.py
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
TRANS = ROOT / "data/raw/regulatory/transcripts"
OUT = ROOT / "data/processed/overnight"
OUT.mkdir(parents=True, exist_ok=True)

ORDER = ["4Q20", "1Q21", "2Q21", "3Q21", "4Q21", "1Q22", "2Q22", "3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23",
         "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
REPORTED = set(ORDER)  # quarters with a printed result in the Part A panel

# Print (letter release) dates - the point in time at which each guide became knowable.
PRINT_DATE = {
    "4Q20": "2021-02-25", "1Q21": "2021-05-13", "2Q21": "2021-08-12", "3Q21": "2021-11-04", "4Q21": "2022-02-15",
    "1Q22": "2022-05-03", "2Q22": "2022-08-02", "3Q22": "2022-11-01", "4Q22": "2023-02-14", "1Q23": "2023-05-09",
    "2Q23": "2023-08-03", "3Q23": "2023-11-01", "4Q23": "2024-02-13", "1Q24": "2024-05-08", "2Q24": "2024-08-06",
    "3Q24": "2024-11-07", "4Q24": "2025-02-13", "1Q25": "2025-05-01", "2Q25": "2025-08-06", "3Q25": "2025-11-06",
    "4Q25": "2026-02-12", "1Q26": "2026-05-07", "2Q26": "2026-08-06",
}

# ----------------------------------------------------------------------------------------------
# Source text, for quote verification
# ----------------------------------------------------------------------------------------------
def letter_text(path: Path) -> str:
    s = path.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<style.*?</style>", "", s, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t).replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


LETTER_FILES = {p.name[:4]: p for p in LETTERS.glob("*.htm")}
TEXT = {q: letter_text(p) for q, p in LETTER_FILES.items()}


def transcript_text(q: str) -> str:
    """q like '2Q26' -> transcript 2026-Q2."""
    y, n = "20" + q[2:], q[0]
    for suffix in (".json", ".txt", ".html"):
        p = TRANS / f"{y}-Q{n}{suffix}"
        if not p.exists():
            continue
        if suffix == ".json":
            d = json.load(open(p, encoding="utf-8"))
            t = " ".join(x.get("text", "") for x in d) if isinstance(d, list) else str(d)
        else:
            t = p.read_text(encoding="utf-8", errors="ignore")
            if suffix == ".html":
                t = re.sub(r"<[^>]+>", " ", t)
        return re.sub(r"\s+", " ", html.unescape(t))
    return ""


TRANS_TEXT = {q: transcript_text(q) for q in ORDER}


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[‘’“”—–�'\"\-]", " ", s)
    return re.sub(r"[^a-z0-9%$.]+", " ", s).strip()


NLET = {q: norm(t) for q, t in TEXT.items()}
NTRA = {q: norm(t) for q, t in TRANS_TEXT.items()}


def verify(q: str, quote: str, src: str) -> bool:
    n = norm(quote)
    if src == "transcript":
        return n in NTRA.get(q, "")
    return n in NLET.get(q, "")


# ----------------------------------------------------------------------------------------------
# Actuals
# ----------------------------------------------------------------------------------------------
P = pd.read_csv(OUT / "02_kpi_panel_quarterly.csv", index_col=0)
P = P.loc[[q for q in ORDER if q in P.index]]
num = lambda c: pd.to_numeric(P[c], errors="coerce")

P["take_rate_yoy_pts"] = num("take_rate_pct") - num("take_rate_pct").shift(4)
P["adj_ebitda_margin_yoy_pts"] = num("adj_ebitda_margin_pct") - num("adj_ebitda_margin_pct").shift(4)
P["sm_pct_rev_yoy_bps"] = (num("sales_marketing_pct_rev") - num("sales_marketing_pct_rev").shift(4)) * 100
P["sm_growth_minus_rev_growth_pts"] = num("sales_marketing_yoy_pct") - num("revenue_yoy_pct")
P["fcf_margin_minus_ebitda_margin_pts"] = num("fcf_margin_pct") - num("adj_ebitda_margin_pct")

QCOL = {  # ledger metric -> panel column, for quarterly targets
    "revenue_usd_m": "revenue_musd",
    "revenue_yoy_pct": "revenue_yoy_reported_pct",
    "revenue_yoy_exfx_pct": "revenue_yoy_exfx_pct",
    "nights_yoy_pct": "nights_yoy_pct",
    "gbv_yoy_pct": "gbv_yoy_pct",
    "adr_yoy_pct": "adr_yoy_pct",
    "take_rate_yoy_pts": "take_rate_yoy_pts",
    "take_rate_pct_seq": "take_rate_pct",
    "adr_usd_seq": "adr_usd",
    "adj_ebitda_usd_m": "adj_ebitda_musd",
    "adj_ebitda_margin_pct": "adj_ebitda_margin_pct",
    "adj_ebitda_margin_yoy_pts": "adj_ebitda_margin_yoy_pts",
    "sm_pct_rev_yoy_bps": "sm_pct_rev_yoy_bps",
    "sm_growth_minus_rev_growth_pts": "sm_growth_minus_rev_growth_pts",
    "fcf_margin_pct": "fcf_margin_pct",
    "fcf_margin_minus_ebitda_margin_pts": "fcf_margin_minus_ebitda_margin_pts",
    "nights_m": "nights_m",
    "gbv_usd_b": "gbv_busd",
}

# full-year aggregates
P["_yr"] = [2000 + int(q[2:]) for q in P.index]
FY = {}
gy = P.groupby("_yr")
sums = gy[["revenue_musd", "adj_ebitda_musd", "fcf_musd", "sbc_musd", "nights_m", "gbv_busd",
           "net_income_musd", "income_tax_musd", "sales_marketing_musd"]].sum(min_count=4)
nq = gy.size()
full = sums[nq == 4]
for y, r in full.iterrows():
    FY[("revenue_usd_m", y)] = r.revenue_musd
    FY[("adj_ebitda_usd_m", y)] = r.adj_ebitda_musd
    FY[("adj_ebitda_margin_pct", y)] = 100 * r.adj_ebitda_musd / r.revenue_musd
    FY[("fcf_margin_pct", y)] = 100 * r.fcf_musd / r.revenue_musd
    FY[("fcf_margin_minus_ebitda_margin_pts", y)] = 100 * (r.fcf_musd - r.adj_ebitda_musd) / r.revenue_musd
    FY[("sbc_usd_m", y)] = r.sbc_musd
    FY[("nights_m", y)] = r.nights_m
    FY[("gbv_usd_b", y)] = r.gbv_busd
    FY[("tax_rate_pct", y)] = 100 * r.income_tax_musd / (r.net_income_musd + r.income_tax_musd)
    FY[("sm_pct_rev", y)] = 100 * r.sales_marketing_musd / r.revenue_musd
for y in sorted({y for _, y in FY}):
    if ("revenue_usd_m", y - 1) in FY:
        FY[("revenue_yoy_pct", y)] = 100 * (FY[("revenue_usd_m", y)] / FY[("revenue_usd_m", y - 1)] - 1)
        FY[("adj_ebitda_margin_yoy_pts", y)] = FY[("adj_ebitda_margin_pct", y)] - FY[("adj_ebitda_margin_pct", y - 1)]
        FY[("sbc_yoy_pct", y)] = 100 * (FY[("sbc_usd_m", y)] / FY[("sbc_usd_m", y - 1)] - 1)
        FY[("sm_pct_rev_yoy_bps", y)] = 100 * (FY[("sm_pct_rev", y)] - FY[("sm_pct_rev", y - 1)])


def actual(metric: str, target: str):
    """target is a quarter ('3Q26') or a fiscal year ('FY2026')."""
    if target.startswith("FY"):
        return FY.get((metric, int(target[2:])), np.nan)
    if target.startswith("1H") or target.startswith("2H"):
        return np.nan
    col = QCOL.get(metric)
    if col is None or target not in P.index or col not in P.columns:
        return np.nan
    v = pd.to_numeric(pd.Series([P.loc[target, col]]), errors="coerce").iloc[0]
    return float(v) if pd.notna(v) else np.nan


# ----------------------------------------------------------------------------------------------
# Bucket vocabulary -> explicit range (percent)
# ----------------------------------------------------------------------------------------------
BUCKET = {
    "low-single": (1, 3), "mid-single": (4, 6), "high-single": (7, 9),
    "low-double": (10, 12), "low-teens": (12, 14), "low-to-mid-teens": (12, 16),
    "mid-teens": (14, 16), "high-teens": (17, 19), "low-20s": (20, 23),
}

# ----------------------------------------------------------------------------------------------
# THE LEDGER. One tuple per guidance statement.
#   (print_q, target, metric, gtype, low, high, mid, unit, quote, cmp_value, direction, src, note)
# gtype: range | floor | ceiling | point | bucket | directional | qualitative
# direction (for directional/bucket rows): up | down | flat | above | below | at_or_below | accelerate |
#            decelerate | stable | outperform | record
# cmp_value: the number the guide is measured against (prior-period level, 0 for "y/y up", etc.)
# ----------------------------------------------------------------------------------------------
G = []


def g(print_q, target, metric, gtype, low=None, high=None, mid=None, unit="", quote="", cmp_value=None,
      direction="", src="letter", note="", tol=0.0):
    G.append(dict(print_q=print_q, target_period=target, metric=metric, guide_type=gtype, value_low=low,
                  value_high=high, value_mid=mid, unit=unit, quote=quote[:150], cmp_value=cmp_value,
                  direction=direction, source=src, note=note, tol=tol))


def gb(print_q, target, metric, bucket, quote, src="letter", note=""):
    lo, hi = BUCKET[bucket]
    g(print_q, target, metric, "bucket", lo, hi, (lo + hi) / 2, "pct", quote, src=src,
      note=(note + f" bucket '{bucket}' -> {lo}-{hi}%").strip())


# ---- 4Q20 print (25 Feb 2021), targets 1Q21 / FY21 -------------------------------------------
g("4Q20", "1Q21", "nights_m", "directional", unit="level",
  quote="we anticipate that levels in Q1 2021 will be higher than those of Q1 2020, but lower than Q1 2019",
  cmp_value=None, direction="between_2020_and_2019", note="nights and GBV both; no number")
g("4Q20", "1Q21", "gbv_usd_b", "directional", unit="level",
  quote="For both of these metrics, we anticipate that levels in Q1 2021 will be higher than those of Q1 2020, but lower than Q1 2019",
  direction="between_2020_and_2019")
g("4Q20", "1Q21", "revenue_yoy_pct", "directional", unit="pct",
  quote="For revenue, the year-over-year decline in Q1 2021 is expected to be less than that of Q4 2020",
  cmp_value=-22.0, direction="above", note="4Q20 revenue y/y was -22%; guide = a smaller decline")
g("4Q20", "1Q21", "adj_ebitda_margin_pct", "qualitative", unit="narrative",
  quote="We anticipate our Adjusted EBITDA margin to also be at its lowest during Q1", direction="seasonal_low")
g("4Q20", "FY2021", "adj_ebitda_margin_pct", "qualitative", unit="narrative",
  quote="we expect our Adjusted EBITDA margins to be lower in the first half of 2021 than the second half",
  direction="2H_above_1H")
g("4Q20", "FY2021", "sm_pct_rev_yoy_bps", "qualitative", unit="narrative",
  quote="We expect that sales and marketing expenses as a percentage of revenue in the first half of 2021 will be higher than that of the second half",
  direction="1H_above_2H")
g("4Q20", "FY2021", "capex_usd_m", "directional", unit="level",
  quote="we anticipate capital expenditures in 2021 will be higher than that of 2020, but significantly lower than 2019",
  direction="up_vs_2020")

# ---- 1Q21 print, targets 2Q21 / FY21 ---------------------------------------------------------
g("1Q21", "2Q21", "nights_m", "directional", unit="level",
  quote="we expect Q2 2021 will be significantly higher than the highly depressed levels of Q2 2020, but below that of Q2 2019",
  direction="between_2020_and_2019")
g("1Q21", "2Q21", "gbv_usd_b", "directional", unit="level",
  quote="We expect GBV in Q2 2021 to be higher than that of Q2 2019", cmp_value=8.1, direction="above",
  note="2Q19 GBV $8.1bn (S-1); actual 2Q21 GBV $13.4bn")
g("1Q21", "2Q21", "revenue_usd_m", "directional", unit="level",
  quote="We expect revenue in Q2 2021 to be significantly higher than that of Q2 2020, given the impact of COVID-19 on the prior year period, and to be at a similar level to that of Q2 2019",
  cmp_value=1214.0, direction="approx", tol=150.0, note="2Q19 revenue $1,214m; actual 2Q21 $1,335m")
g("1Q21", "FY2021", "adj_ebitda_margin_pct", "qualitative", unit="narrative",
  quote="we expect our Adjusted EBITDA margins to be lower in the first half of 2021 than the second half",
  direction="2H_above_1H")
g("1Q21", "FY2021", "capex_usd_m", "directional", unit="level",
  quote="we continue to expect capital expenditures in 2021 will be higher than that of 2020, but significantly lower than 2019",
  direction="up_vs_2020")
g("1Q21", "FY2021", "adr_yoy_pct", "qualitative", unit="narrative",
  quote="If our business mix changes as travel recovers, we may see a decline in our ADR in the future", direction="down_risk")

# ---- 2Q21 print, targets 3Q21 / 2H21 ---------------------------------------------------------
g("2Q21", "3Q21", "revenue_usd_m", "directional", unit="level",
  quote="we expect Q3 2021 revenue to be our strongest quarterly revenue on record", cmp_value=1535.0,
  direction="above", note="prior record 3Q19 $1,646m / 2Q21 $1,335m; actual 3Q21 $2,237m")
g("2Q21", "3Q21", "adj_ebitda_margin_pct", "directional", unit="pct",
  quote="to deliver the highest Adjusted EBITDA dollars and margin ever", cmp_value=37.3, direction="above",
  note="prior record margin 3Q20 37.3%; actual 3Q21 49.2%")
g("2Q21", "3Q21", "nights_m", "directional", unit="level",
  quote="we expect Nights and Experiences Booked to come down from Q2 and remain below Q3 2019 levels",
  cmp_value=83.1, direction="below", note="2Q21 nights 83.1m; actual 3Q21 79.7m -> met")
g("2Q21", "3Q21", "gbv_usd_b", "directional", unit="level",
  quote="we expect GBV in Q3 2021 to be well above 2019 levels, but below what we saw in Q2", cmp_value=13.4,
  direction="below", note="2Q21 GBV $13.4bn; actual 3Q21 $11.9bn -> met")
g("2Q21", "2H2021", "adr_yoy_pct", "qualitative", unit="narrative",
  quote="In the second half of 2021, we expect ADR to gradually moderate based on the anticipated shift in regional composition",
  direction="down")
g("2Q21", "2H2021", "adj_ebitda_margin_pct", "qualitative", unit="narrative",
  quote="We expect our Adjusted EBITDA margins to be higher in the second half of 2021 than in the first half",
  direction="2H_above_1H")
g("2Q21", "2H2021", "sm_pct_rev_yoy_bps", "qualitative", unit="narrative",
  quote="we expect that sales and marketing expense as a percentage of revenue in the second half of 2021 will be lower than that of the first half",
  direction="2H_below_1H")
g("2Q21", "3Q21", "take_rate_pct_seq", "directional", unit="pts",
  quote="Our Q3 revenue as a percentage of GBV will increase substantially from Q2", cmp_value=9.96,
  direction="above", note="sequential, not y/y; 2Q21 take rate 9.96%, actual 3Q21 18.8%")

# ---- 3Q21 print, targets 4Q21 ----------------------------------------------------------------
g("3Q21", "4Q21", "revenue_usd_m", "range", 1390, 1480, 1435, "USD m",
  "We expect to deliver Q4 revenue of between $1.39 billion and $1.48 billion")
g("3Q21", "4Q21", "nights_m", "directional", unit="level",
  quote="We expect Nights and Experiences Booked in Q4 2021 to significantly outperform Q4 2020 levels and approximate Q4 2019 levels",
  cmp_value=76.0, direction="approx", tol=10.0, note="4Q19 nights ~76m (S-1); actual 4Q21 73.4m")
g("3Q21", "4Q21", "adr_usd_seq", "directional", unit="USD",
  quote="we expect our ADR will be relatively stable in Q4 2021 relative to Q3 2021", cmp_value=149.15,
  direction="approx_seq", tol=8.0, note="sequential vs 3Q21 ADR $149.15; actual 4Q21 $153.61 (+3.0%)")
g("3Q21", "4Q21", "gbv_usd_b", "directional", unit="level",
  quote="we expect Q4 2021 GBV to be substantially above both Q4 2020 and Q4 2019 levels", cmp_value=5.91,
  direction="above", note="actual 4Q21 GBV $11.3bn")
g("3Q21", "4Q21", "adj_ebitda_margin_yoy_pts", "directional", unit="pts",
  quote="we expect to deliver greater year-over-year and year-over-two year margin expansion in Q4 2021 than we delivered in Q3 2021",
  cmp_value=11.9, direction="above", note="3Q21 margin expansion +11.9pts y/y; 4Q21 delivered +24.1pts")
g("3Q21", "4Q21", "take_rate_pct_seq", "directional", unit="pts",
  quote="Q4 revenue—in both absolute dollars and as a percentage of GBV—will decrease from Q3",
  cmp_value=18.8, direction="below_seq", note="sequential take rate; actual 4Q21 13.56%")

# ---- 4Q21 print, targets 1Q22 / FY22 ---------------------------------------------------------
g("4Q21", "1Q22", "revenue_usd_m", "range", 1410, 1480, 1445, "USD m",
  "We expect to deliver Q1 2022 revenue of between $1.41 billion and $1.48 billion")
g("4Q21", "1Q22", "adr_yoy_pct", "point", mid=4.0, unit="pct",
  quote="We currently anticipate Q1 2022 ADR to be up approximately 4% from Q1 2021")
g("4Q21", "1Q22", "nights_m", "directional", unit="level",
  quote="we expect Q1 2022 Nights and Experiences Booked to significantly exceed Q1 2019 levels, which we believe will result in our strongest quarterly Nights and Experiences Booked on record",
  cmp_value=83.1, direction="above", note="prior record 2Q21 83.1m; actual 1Q22 102.1m = record -> met")
g("4Q21", "1Q22", "gbv_usd_b", "directional", unit="level",
  quote="we anticipate that GBV in Q1 2022 will be another record for Airbnb", cmp_value=13.4, direction="above",
  note="prior record 2Q21 $13.4bn; actual 1Q22 $17.2bn = record")
g("4Q21", "1Q22", "adj_ebitda_usd_m", "directional", unit="USD m",
  quote="we expect to achieve our first positive Q1 Adjusted EBITDA in Airbnb history", cmp_value=0.0,
  direction="above", note="actual 1Q22 adj EBITDA +$229m")
g("4Q21", "1Q22", "take_rate_pct_seq", "directional", unit="pts",
  quote="revenue as a share of GBV in Q1 2022 to decrease relative to Q4 2021", cmp_value=13.56,
  direction="below_seq", note="sequential; actual 1Q22 8.77%")
g("4Q21", "FY2022", "adj_ebitda_margin_yoy_pts", "point", mid=0.0, unit="pts",
  quote="we would expect Adjusted EBITDA margin to be directionally in-line with 2021", note="FY21 margin 26.6%")
g("4Q21", "FY2022", "sm_pct_rev_yoy_bps", "point", mid=0.0, unit="bps",
  quote="sales and marketing expense as a percent of revenue is expected to remain relatively flat")

# ---- 1Q22 print, targets 2Q22 / FY22 ---------------------------------------------------------
g("1Q22", "2Q22", "revenue_usd_m", "range", 2030, 2130, 2080, "USD m",
  "we expect to deliver Q2 2022 revenue between $2.03 billion and $2.13 billion")
g("1Q22", "2Q22", "adr_yoy_pct", "point", mid=0.0, unit="pct",
  quote="We expect ADR to be flat in Q2 2022 on a year-over-year basis", note="actual 2Q22 ADR +1.4% y/y")
g("1Q22", "2Q22", "nights_m", "directional", unit="pct vs 2019",
  quote="we anticipate that the Nights and Experiences Booked growth rate in Q2 2022 (compared to Q2 2019) will approximate the growth rate in Q1 2022 (compared to Q1 2019)",
  direction="approx_vs2019", note="vs-2019 basis; company had asked the street to index to 2019")
g("1Q22", "2Q22", "take_rate_pct_seq", "directional", unit="pts",
  quote="we expect our revenue as a share of GBV to increase in Q2 2022 relative to Q1 2022", cmp_value=8.77,
  direction="above_seq", note="sequential; actual 2Q22 12.38%")
g("1Q22", "2Q22", "adj_ebitda_margin_yoy_pts", "floor", low=10.0, unit="pts",
  quote="driving a low double-digit EBITDA margin percentage improvement on a year-over-year basis",
  note="'low double-digit' improvement read as >=10 points y/y; 2Q21 margin 16.3%")
g("1Q22", "FY2022", "adj_ebitda_margin_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We currently anticipate delivering modest Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021")
g("1Q22", "FY2022", "sm_pct_rev_yoy_bps", "point", mid=0.0, unit="bps",
  quote="we currently expect sales and marketing expense as a percent of revenue to remain relatively flat compared to 2021")

# ---- 2Q22 print, targets 3Q22 / FY22 ---------------------------------------------------------
g("2Q22", "3Q22", "revenue_usd_m", "range", 2780, 2880, 2830, "USD m",
  "We expect to deliver Q3 2022 revenue between $2.78 billion and $2.88 billion")
g("2Q22", "3Q22", "revenue_yoy_pct", "range", 24, 29, 26.5, "pct",
  "representing year-over-year growth of between 24% and 29%")
g("2Q22", "3Q22", "nights_yoy_pct", "directional", unit="pct",
  quote="In Q3 2022, we expect Nights and Experienced Booked year-over-year growth to be stable with the year-over-year growth in Q2 2022",
  cmp_value=24.6, direction="stable", tol=3.0, note="2Q22 nights y/y +24.6%; actual 3Q22 +25.1%")
g("2Q22", "3Q22", "adr_yoy_pct", "directional", unit="pct",
  quote="we anticipate slightly higher ADRs than we had in Q3 2021", cmp_value=0.0, direction="above",
  note="actual 3Q22 ADR +4.9% y/y")
g("2Q22", "3Q22", "gbv_yoy_pct", "directional", unit="pct",
  quote="resulting in a modest acceleration in GBV growth", cmp_value=26.9, direction="above",
  note="2Q22 GBV y/y +26.9%; actual 3Q22 +31.1%")
g("2Q22", "3Q22", "adj_ebitda_margin_pct", "ceiling", high=49.0, unit="pct",
  quote="We expect Q3 2022 Adjusted EBITDA margin to be at or slightly below last year's all-time high margin of 49%",
  note="ceiling from the stated 3Q21 margin; actual 3Q22 50.5%")
g("2Q22", "FY2022", "adj_ebitda_margin_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We continue to forecast delivering Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021")

# ---- 3Q22 print, targets 4Q22 ----------------------------------------------------------------
g("3Q22", "4Q22", "revenue_usd_m", "range", 1800, 1880, 1840, "USD m",
  "We expect another strong quarter of revenue growth, delivering between $1.80 billion and $1.88 billion in Q4 2022")
g("3Q22", "4Q22", "revenue_yoy_pct", "range", 17, 23, 20.0, "pct",
  "This represents year-over-year growth of between 17% and 23%")
g("3Q22", "4Q22", "revenue_yoy_exfx_pct", "range", 23, 29, 26.0, "pct",
  "On an FX-neutral basis, we anticipate year-over-year revenue growth between 23% and 29%")
g("3Q22", "4Q22", "take_rate_pct_seq", "directional", unit="pts",
  quote="We expect our revenue as a share of GBV to decrease in Q4 2022 relative to Q3 2022", cmp_value=18.49,
  direction="below_seq", note="sequential; actual 4Q22 14.09%")
g("3Q22", "4Q22", "nights_yoy_pct", "directional", unit="pct",
  quote="we expect Nights and Experiences Booked growth will moderate slightly relative to Q3 2022", cmp_value=25.1,
  direction="below", note="3Q22 nights y/y +25.1%; actual 4Q22 +20.2%")
g("3Q22", "4Q22", "adr_yoy_pct", "directional", unit="pct",
  quote="ADR will face some pressure from FX headwinds and business mix", cmp_value=4.9, direction="below",
  note="vs 3Q22 ADR growth +4.9%; actual 4Q22 -0.5% y/y")
g("3Q22", "4Q22", "adj_ebitda_margin_pct", "floor", low=22.0, unit="pct",
  quote="expect quarterly Adjusted EBITDA margin to be in-line to modestly higher than last year's margin of 22%")

# ---- 4Q22 print, targets 1Q23 / FY23 ---------------------------------------------------------
g("4Q22", "1Q23", "revenue_usd_m", "range", 1750, 1820, 1785, "USD m",
  "We expect revenue of $1.75 billion to $1.82 billion in Q1 2023")
g("4Q22", "1Q23", "revenue_yoy_pct", "range", 16, 21, 18.5, "pct",
  "This represents year-over-year growth of between 16% and 21%")
g("4Q22", "1Q23", "revenue_yoy_exfx_pct", "range", 18, 23, 20.5, "pct",
  "on an ex-FX basis between 18% and 23%")
g("4Q22", "1Q23", "take_rate_yoy_pts", "point", mid=0.0, unit="pts",
  quote="We expect our implied take rate (defined as revenue divided by GBV) in Q1 2023 to be similar to Q1 2022")
g("4Q22", "1Q23", "nights_yoy_pct", "directional", unit="pct",
  quote="In Q1 2023, we expect Nights and Experiences Booked year-over-year growth to be nearly as strong as Q4 2022",
  cmp_value=20.2, direction="approx", tol=3.0, note="4Q22 nights y/y +20.2%; actual 1Q23 +18.6%")
g("4Q22", "1Q23", "adr_yoy_pct", "directional", unit="pct",
  quote="In Q1 2023, we anticipate slightly lower ADR than we had in Q1 2022", cmp_value=0.0, direction="below",
  note="actual 1Q23 ADR +0.2% y/y -> essentially flat, guide called down")
g("4Q22", "1Q23", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="In Q1 2023, we expect Adjusted EBITDA margin to be slightly down on a year-over-year basis")
g("4Q22", "1Q23", "sm_pct_rev_yoy_bps", "point", mid=150.0, unit="bps",
  quote="we expect sales and marketing in Q1 2023 will be approximately 150 basis points higher as a percent of revenue")
g("4Q22", "FY2023", "adj_ebitda_margin_yoy_pts", "point", mid=0.0, unit="pts",
  quote="For the full year 2023, we expect to maintain the strong Adjusted EBITDA margin we delivered in 2022")
g("4Q22", "FY2023", "sm_pct_rev_yoy_bps", "point", mid=0.0, unit="bps",
  quote="but flat as a percent of revenue for the full year")
g("4Q22", "FY2023", "adr_yoy_pct", "qualitative", unit="narrative",
  quote="For the remainder of the year, we expect ADR will face increasing downward pressure from mix shift, as well as new and improved pricing and discounting tools",
  direction="down")

# ---- 1Q23 print, targets 2Q23 / FY23 ---------------------------------------------------------
g("1Q23", "2Q23", "revenue_usd_m", "range", 2350, 2450, 2400, "USD m",
  "We expect to deliver revenue of $2.35 billion to $2.45 billion in Q2 2023")
g("1Q23", "2Q23", "revenue_yoy_pct", "range", 12, 16, 14.0, "pct",
  "This represents year-over-year growth of between 12% and 16%")
g("1Q23", "2Q23", "take_rate_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We anticipate that our implied take rate (defined as revenue divided by GBV) in Q2 2023 will be above Q2 2022")
g("1Q23", "2Q23", "nights_yoy_pct", "directional", unit="pct",
  quote="We expect year-over-year growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth during the quarter",
  cmp_value=None, direction="below_revenue_growth", note="actual 2Q23 nights +11.0% vs revenue +18.1% -> met")
g("1Q23", "2Q23", "adr_yoy_pct", "directional", unit="pct",
  quote="we anticipate a slightly lower ADR in Q2 2023 than Q2 2022", cmp_value=0.0, direction="below",
  note="actual 2Q23 ADR +1.4% y/y -> guide wrong in sign")
g("1Q23", "2Q23", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="we expect Adjusted EBITDA to be similar to Adjusted EBITDA in Q2 2022 on a nominal basis, but lower on a margin basis")
g("1Q23", "2Q23", "sm_pct_rev_yoy_bps", "point", mid=400.0, unit="bps",
  quote="we expect that Sales and Marketing expense in Q2 2023 will be approximately 400 basis points higher as a percent of revenue")
g("1Q23", "FY2023", "adj_ebitda_margin_yoy_pts", "point", mid=0.0, unit="pts",
  quote="We continue to anticipate a full year Adjusted EBITDA margin that is broadly in-line with full-year 2022")

# ---- 2Q23 print, targets 3Q23 / FY23 ---------------------------------------------------------
g("2Q23", "3Q23", "revenue_usd_m", "range", 3300, 3400, 3350, "USD m",
  "For Q3 2023, we expect to deliver revenue of $3.3 billion to $3.4 billion")
g("2Q23", "3Q23", "revenue_yoy_pct", "range", 14, 18, 16.0, "pct",
  "which represents year-over-year growth of between 14% and 18%")
g("2Q23", "3Q23", "revenue_yoy_exfx_pct", "directional", unit="pct",
  quote="and a few points lower excluding the impact of FX", cmp_value=16.0, direction="below",
  note="ex-FX below the reported guide midpoint; actual ex-FX +14%")
g("2Q23", "3Q23", "take_rate_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We anticipate that our implied take rate (defined as revenue divided by GBV) in Q3 2023 will be higher than Q3 2022")
g("2Q23", "3Q23", "nights_yoy_pct", "directional", unit="pct",
  quote="We expect a modest sequential increase in the year-over-year growth rate of Nights and Experiences Booked from Q2 2023 to Q3 2023",
  cmp_value=11.0, direction="above", note="2Q23 nights y/y +11.0%; actual 3Q23 +13.5% -> met")
g("2Q23", "3Q23", "adr_yoy_pct", "floor", low=0.0, unit="pct",
  quote="we expect upward pressure on ADR from FX rates and listing type mix shift to outweigh their impact and drive a year-over-year increase in ADR in Q3 2023")
g("2Q23", "3Q23", "adj_ebitda_margin_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We expect a record-high Adjusted EBITDA in Q3 2023 on a nominal basis and an Adjusted EBITDA margin that exceeds Q3 2022")
g("2Q23", "FY2023", "adj_ebitda_margin_yoy_pts", "floor", low=0.0, unit="pts",
  quote="For the full-year 2023, we expect an Adjusted EBITDA margin that is modestly higher than the full-year 2022")

# ---- 3Q23 print, targets 4Q23 / FY23 ---------------------------------------------------------
g("3Q23", "4Q23", "revenue_usd_m", "range", 2130, 2170, 2150, "USD m",
  "For Q4 2023, we expect to deliver revenue of $2.13 billion to $2.17 billion")
g("3Q23", "4Q23", "revenue_yoy_pct", "range", 12, 14, 13.0, "pct",
  "This represents year-over-year growth of between 12% and 14%")
g("3Q23", "4Q23", "take_rate_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We anticipate that our implied take rate (defined as revenue divided by GBV) in Q4 2023 will be slightly higher than Q4 2022")
g("3Q23", "4Q23", "nights_yoy_pct", "directional", unit="pct",
  quote="We currently expect our nights booked growth in Q4 2023 to moderate relative to Q3 2023", cmp_value=13.5,
  direction="below", note="3Q23 nights y/y +13.5%; actual 4Q23 +12.0% -> met")
g("3Q23", "4Q23", "adr_yoy_pct", "floor", low=-0.5, unit="pct",
  quote="we expect ADR in Q4 2023 to be stable to slightly up compared to the same period last year")
g("3Q23", "4Q23", "adj_ebitda_margin_yoy_pts", "floor", low=0.0, unit="pts",
  quote="we expect a record-high fourth quarter Adjusted EBITDA in 2023 on a nominal basis and an Adjusted EBITDA margin that exceeds Q4 2022")
g("3Q23", "FY2023", "adj_ebitda_margin_yoy_pts", "point", mid=1.5, unit="pts",
  quote="we expect an Adjusted EBITDA margin for full-year 2023 that is approximately 150 bps higher than full-year 2022")
g("3Q23", "FY2023", "sbc_yoy_pct", "point", mid=20.0, unit="pct",
  quote="For full-year 2023, we expect our stock-based compensation (“SBC”) expense to be approximately 20% higher than in full-year 2022")

# ---- 4Q23 print, targets 1Q24 / FY24 ---------------------------------------------------------
g("4Q23", "1Q24", "revenue_usd_m", "range", 2030, 2070, 2050, "USD m",
  "For Q1 2024, we expect to deliver revenue of $2.03 billion to $2.07 billion")
g("4Q23", "1Q24", "revenue_yoy_pct", "range", 12, 14, 13.0, "pct",
  "which represents year-over-year growth of between 12% and 14%")
g("4Q23", "1Q24", "take_rate_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We anticipate that our implied take rate (defined as revenue divided by GBV) in Q1 2024 will be notably higher than Q1 2023")
g("4Q23", "1Q24", "nights_yoy_pct", "directional", unit="pct",
  quote="we expect the growth rate of nights booked in Q1 2024 to moderate relative to Q4 2023", cmp_value=12.0,
  direction="below", note="4Q23 nights y/y +12.0%; actual 1Q24 +9.5% -> met")
g("4Q23", "1Q24", "adr_yoy_pct", "floor", low=-0.5, unit="pct",
  quote="We expect ADR for the quarter to be flat to slightly up compared to Q1 2023")
g("4Q23", "1Q24", "adj_ebitda_margin_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We expect Adjusted EBITDA Margin in Q1 2024 to expand relative to Q1 2023")
g("4Q23", "FY2024", "adj_ebitda_margin_pct", "floor", low=35.0, unit="pct",
  quote="For the full-year 2024, we expect to maintain an Adjusted EBITDA Margin of at least 35%")
g("4Q23", "FY2024", "tax_rate_pct", "range", 15, 19, 17.0, "pct",
  "we expect our effective tax rate to approximate the mid-to-high teens in the near-term",
  note="'mid-to-high teens' -> 15-19%")

# ---- 1Q24 print, targets 2Q24 / 3Q24 / FY24 --------------------------------------------------
g("1Q24", "2Q24", "revenue_usd_m", "range", 2680, 2740, 2710, "USD m",
  "For Q2 2024, we expect to deliver revenue of $2.68 billion to $2.74 billion")
g("1Q24", "2Q24", "revenue_yoy_pct", "range", 8, 10, 9.0, "pct",
  "which represents year-over-year growth of between 8% and 10%")
g("1Q24", "3Q24", "revenue_yoy_pct", "directional", unit="pct",
  quote="we expect year-over-year revenue growth to accelerate in Q3 2024 compared to Q2 2024", cmp_value=None,
  direction="accelerate_vs_prior_q", note="two-quarter-ahead guide; 2Q24 +10.6%, 3Q24 +9.9% -> NOT met")
g("1Q24", "2Q24", "nights_yoy_pct", "directional", unit="pct",
  quote="We expect the year-over-year growth rate of nights booked in Q2 2024 to be relatively stable to that of Q1 2024",
  cmp_value=9.5, direction="stable", tol=2.0, note="1Q24 nights y/y +9.5%; actual 2Q24 +8.7% -> met")
g("1Q24", "2Q24", "adr_yoy_pct", "floor", low=0.0, unit="pct",
  quote="estimate that ADR for the quarter will be modestly up compared to Q2 2023")
g("1Q24", "2Q24", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="we expect Adjusted EBITDA to be flat to up on a nominal basis, but down on an Adjusted EBITDA Margin basis, relative to Q2 2023")
g("1Q24", "FY2024", "adj_ebitda_margin_pct", "floor", low=35.0, unit="pct",
  quote="For the full-year 2024, consistent with our prior guidance, we expect to grow Adjusted EBITDA on a nominal basis and to deliver an Adjusted EBITDA Margin of at least 35%")
g("1Q24", "FY2024", "sbc_yoy_pct", "point", mid=20.0, unit="pct",
  quote="For full-year 2024, we expect our stock-based compensation (“SBC”) expense to be approximately 20% higher than in full-year 2023")

# ---- 2Q24 print, targets 3Q24 / FY24 ---------------------------------------------------------
g("2Q24", "3Q24", "revenue_usd_m", "range", 3670, 3730, 3700, "USD m",
  "In Q3 2024, we expect to deliver revenue of $3.67 billion to $3.73 billion")
g("2Q24", "3Q24", "revenue_yoy_pct", "range", 8, 10, 9.0, "pct",
  "representing year-over-year growth of 8% to 10%, inclusive of a modest foreign exchange headwind")
g("2Q24", "3Q24", "take_rate_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We anticipate that our implied take rate in Q3 2024 will be higher on a year-over-year basis")
g("2Q24", "3Q24", "nights_yoy_pct", "directional", unit="pct",
  quote="we expect a sequential moderation in the year-over-year growth of Nights and Experiences Booked relative to Q2 2024",
  cmp_value=8.7, direction="below", note="2Q24 nights y/y +8.7%; actual 3Q24 +8.5% -> met, barely")
g("2Q24", "3Q24", "adr_yoy_pct", "floor", low=0.0, unit="pct",
  quote="we expect ADR to increase modestly on a year-over- year basis in Q3 2024")
g("2Q24", "3Q24", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="we expect Adjusted EBITDA to approximate Q3 2023 on a nominal basis, but for Adjusted EBITDA Margin to decline relative to Q3 2023")
g("2Q24", "3Q24", "sm_growth_minus_rev_growth_pts", "floor", low=0.0, unit="pts",
  quote="Marketing expense is expected to grow faster than revenue on a year-over-year basis in Q3 2024")
g("2Q24", "FY2024", "adj_ebitda_margin_pct", "floor", low=35.0, unit="pct",
  quote="For the full-year 2024, consistent with our prior guidance, we expect to grow Adjusted EBITDA on a nominal basis and to deliver an Adjusted EBITDA Margin of at least 35%")
g("2Q24", "FY2024", "fcf_margin_minus_ebitda_margin_pts", "floor", low=2.0, unit="pts",
  quote="We also expect to continue to deliver a full-year 2024 Free Cash Flow margin several points above our EBITDA margin",
  note="'several points' read as >=2 points")

# ---- 3Q24 print, targets 4Q24 / 1Q25 / FY24 --------------------------------------------------
g("3Q24", "4Q24", "revenue_usd_m", "range", 2390, 2440, 2415, "USD m",
  "For Q4 2024, we expect to deliver revenue of $2.39 billion to $2.44 billion")
g("3Q24", "4Q24", "revenue_yoy_pct", "range", 8, 10, 9.0, "pct",
  "representing year-over-year growth of 8% to 10%, inclusive of a modest foreign exchange tailwind")
g("3Q24", "4Q24", "take_rate_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="We anticipate that our implied take rate in Q4 2024 will be slightly lower on a year-over-year basis")
g("3Q24", "4Q24", "nights_yoy_pct", "directional", unit="pct",
  quote="we expect year-over-year growth of Nights and Experienced Booked in Q4 2024 to be higher than Q3 2024",
  cmp_value=8.5, direction="above", note="3Q24 nights y/y +8.5%; actual 4Q24 +10.0% -> met")
g("3Q24", "4Q24", "adr_yoy_pct", "floor", low=0.0, unit="pct",
  quote="In Q4 2024, we expect ADR to increase modestly on a year-over-year basis")
g("3Q24", "4Q24", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="Q4 2024 Adjusted EBITDA Margin is expected to decline relative to the same time period last year")
g("3Q24", "1Q25", "revenue_yoy_pct", "directional", unit="pct",
  quote="In Q1 2025, the year-over-year growth rate of revenue will be negatively impacted by the comparison to Q1 2024",
  cmp_value=11.6, direction="below", note="two-quarter-ahead; 4Q24 revenue y/y +11.6%, actual 1Q25 +6.1% -> met")
g("3Q24", "FY2024", "adj_ebitda_margin_pct", "point", mid=35.5, unit="pct",
  quote="For the full-year 2024, we now expect to deliver an Adjusted EBITDA Margin of approximately 35.5%",
  note="raised from the 'at least 35%' floor carried since 4Q23")
g("3Q24", "FY2024", "fcf_margin_minus_ebitda_margin_pts", "floor", low=2.0, unit="pts",
  quote="we expect to deliver a full-year 2024 Free Cash Flow Margin several points above our Adjusted EBITDA Margin")
g("3Q24", "FY2024", "sbc_yoy_pct", "point", mid=25.0, unit="pct",
  quote="For full-year 2024, we expect our stock-based compensation (“SBC”) expense to be approximately 25% higher than in full-year 2023",
  note="raised from ~20% in the 1Q24 letter")
g("3Q24", "FY2024", "tax_rate_pct", "point", mid=20.0, unit="pct",
  quote="For the full-year 2024, we anticipate our effective tax rate to be approximately 20%")

# ---- 4Q24 print, targets 1Q25 / FY25 ---------------------------------------------------------
g("4Q24", "1Q25", "revenue_usd_m", "range", 2230, 2270, 2250, "USD m",
  "For Q1 2025, we expect to deliver revenue of $2.23 billion to $2.27 billion")
g("4Q24", "1Q25", "revenue_yoy_pct", "range", 4, 6, 5.0, "pct",
  "representing year-over-year growth of 4% to 6%")
g("4Q24", "1Q25", "revenue_yoy_exfx_pct", "range", 7, 9, 8.0, "pct",
  "or 7% to 9% excluding the impact of FX")
g("4Q24", "1Q25", "nights_yoy_pct", "directional", unit="pct",
  quote="We expect year-over-year growth of Nights and Experiences Booked in Q1 2025 to be relatively stable compared to Q1 2024 after excluding Leap Day",
  cmp_value=8.5, direction="stable", tol=2.0, note="1Q24 nights y/y +9.5% less ~1pt Leap Day = 8.5%; actual 1Q25 +7.9% -> met")
g("4Q24", "1Q25", "adr_yoy_pct", "ceiling", high=0.0, unit="pct",
  quote="In Q1 2025, we expect ADR to decline slightly on a year-over-year basis, largely driven by FX headwinds")
g("4Q24", "1Q25", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="In Q1 2025, we expect Adjusted EBITDA and Adjusted EBITDA Margin to decline compared to Q1 2024")
g("4Q24", "FY2025", "adj_ebitda_margin_pct", "floor", low=34.5, unit="pct",
  quote="we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%")
g("4Q24", "FY2025", "new_business_investment_usd_m", "range", 200, 250, 225, "USD m",
  "we plan to invest $200 million to $250 million towards launching and scaling new businesses to be introduced later this year")
g("4Q24", "FY2025", "tax_rate_pct", "ceiling", high=20.0, unit="pct",
  quote="For the full-year 2025, we anticipate our effective tax rate to slightly below our long-term effective tax rate of approximately 20%")

# ---- 1Q25 print, targets 2Q25 / FY25 ---------------------------------------------------------
g("1Q25", "2Q25", "revenue_usd_m", "range", 2990, 3050, 3020, "USD m",
  "In Q2 2025, we expect to generate revenue of $2.99 billion to $3.05 billion")
g("1Q25", "2Q25", "revenue_yoy_pct", "range", 9, 11, 10.0, "pct",
  "representing year-over-year growth of 9% to 11%")
g("1Q25", "2Q25", "take_rate_yoy_pts", "floor", low=0.0, unit="pts",
  quote="we anticipate our implied take rate in Q2 2025 to be higher than in Q2 2024")
g("1Q25", "2Q25", "nights_yoy_pct", "directional", unit="pct",
  quote="In Q2 2025, we expect year-over-year growth of Nights and Experiences Booked to moderate relative to Q1 2025",
  cmp_value=7.9, direction="below", note="1Q25 nights y/y +7.9%; actual 2Q25 +7.4% -> met")
g("1Q25", "2Q25", "adr_yoy_pct", "point", mid=0.0, unit="pct",
  quote="In Q2 2025, we expect ADR to be approximately flat year-over-year")
g("1Q25", "2Q25", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="we expect Adjusted EBITDA to increase on a year-over- year basis, but for Adjusted EBITDA Margin to be flat to down slightly compared to Q2 2024",
  tol=0.3)
g("1Q25", "2Q25", "sm_growth_minus_rev_growth_pts", "floor", low=0.0, unit="pts",
  quote="Marketing expense is expected to grow faster than revenue on a year-over-year basis in Q2 2025")
g("1Q25", "FY2025", "adj_ebitda_margin_pct", "floor", low=34.5, unit="pct",
  quote="For full-year 2025, consistent with our prior guidance, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%")
g("1Q25", "FY2025", "new_business_investment_usd_m", "range", 200, 250, 225, "USD m",
  "we plan to invest $200 million to $250 million towards launching and scaling new businesses in 2025")

# ---- 2Q25 print, targets 3Q25 / 4Q25 / FY25 --------------------------------------------------
g("2Q25", "3Q25", "revenue_usd_m", "range", 4020, 4100, 4060, "USD m",
  "In Q3 2025, we expect to generate revenue of $4.02 billion to $4.10 billion")
g("2Q25", "3Q25", "revenue_yoy_pct", "range", 8, 10, 9.0, "pct",
  "representing year-over-year growth of 8% to 10%, inclusive of minimal foreign exchange impact after factoring in our hedging program")
g("2Q25", "3Q25", "take_rate_yoy_pts", "point", mid=0.0, unit="pts",
  quote="We anticipate our implied take rate in Q3 2025 to be flat year-over year")
g("2Q25", "3Q25", "nights_yoy_pct", "directional", unit="pct",
  quote="In Q3 2025, we expect year-over-year growth of Nights and Seats Booked to be relatively stable compared to Q2 2025",
  cmp_value=7.4, direction="stable", tol=2.0, note="2Q25 nights y/y +7.4%; actual 3Q25 +8.8% -> met")
g("2Q25", "3Q25", "adr_yoy_pct", "floor", low=0.0, unit="pct",
  quote="In Q3 2025, we expect ADR to increase modestly on a year-over-year basis, primarily driven by FX")
g("2Q25", "3Q25", "adj_ebitda_usd_m", "floor", low=2000.0, unit="USD m",
  quote="In Q3 2025, we expect Adjusted EBITDA to increase to over $2.0 billion")
g("2Q25", "3Q25", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="we anticipate that Adjusted EBITDA Margin during Q3 2025 will be lower than in Q3 2024")
g("2Q25", "4Q25", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="We expect a similar year-over-year decline in Q4 2025 Adjusted EBITDA Margin due to growth investments and a tougher year-over-year top-line comparison",
  note="two-quarter-ahead margin guide")
g("2Q25", "FY2025", "adj_ebitda_margin_pct", "floor", low=34.5, unit="pct",
  quote="For 2025, consistent with our prior guidance, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%")
g("2Q25", "FY2025", "new_business_investment_usd_m", "point", mid=200.0, unit="USD m",
  quote="This includes investing approximately $200 million towards services and experiences in 2025",
  note="trimmed from the $200-250m range guided in 4Q24 and 1Q25")

# ---- 3Q25 print, targets 4Q25 / FY25 ---------------------------------------------------------
g("3Q25", "4Q25", "revenue_usd_m", "range", 2660, 2720, 2690, "USD m",
  "In Q4 2025, we expect to generate revenue of $2.66 billion to $2.72 billion")
g("3Q25", "4Q25", "revenue_yoy_pct", "range", 7, 10, 8.5, "pct",
  "representing year-over-year growth of 7% to 10%, inclusive of a small foreign exchange tailwind after factoring in our hedging program")
g("3Q25", "4Q25", "take_rate_yoy_pts", "point", mid=0.0, unit="pts",
  quote="We anticipate our implied take rate in Q4 2025 to be relatively flat year-over year")
gb("3Q25", "4Q25", "gbv_yoy_pct", "low-double",
   "In Q4 2025, we expect our GBV to grow low-double- digits year-over-year")
gb("3Q25", "4Q25", "nights_yoy_pct", "mid-single",
   "In Q4 2025, we expect year-over-year growth of Nights and Seats Booked in the mid-single-digit range due to the challenging Q4 2024 comparison")
g("3Q25", "4Q25", "adr_yoy_pct", "floor", low=0.0, unit="pct",
  quote="We anticipate our GBV to benefit from a modest increase in ADR, primarily due to price appreciation and FX")
g("3Q25", "4Q25", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="We expect Adjusted EBITDA in Q4 2025 to be flat- to-down slightly on a year-over-year basis and for Adjusted EBITDA Margin to decline over the same time period")
g("3Q25", "FY2025", "adj_ebitda_margin_pct", "point", mid=35.0, unit="pct",
  quote="For the full-year 2025, we now expect to deliver an Adjusted EBITDA Margin of approximately 35%",
  note="raised from the 'at least 34.5%' floor carried all year")
g("3Q25", "FY2025", "new_business_investment_usd_m", "point", mid=200.0, unit="USD m",
  quote="Consistent with our prior update, this includes investing approximately $200 million towards services and experiences in 2025")

# ---- 4Q25 print, targets 1Q26 / FY26 ---------------------------------------------------------
g("4Q25", "1Q26", "revenue_usd_m", "range", 2590, 2630, 2610, "USD m",
  "We expect to generate revenue of $2.59 billion to $2.63 billion")
g("4Q25", "1Q26", "revenue_yoy_pct", "range", 14, 16, 15.0, "pct",
  "representing year-over-year growth of 14% to 16%, inclusive of an approximate three point foreign exchange tailwind after factoring in our hedging program")
g("4Q25", "1Q26", "take_rate_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We expect our implied take rate in Q1 2026 to be up slightly year-over-year")
gb("4Q25", "1Q26", "gbv_yoy_pct", "low-teens",
   "We expect GBV to increase in the low teens year-over-year")
gb("4Q25", "1Q26", "nights_yoy_pct", "high-single",
   "driven by high-single-digit growth in Nights and Seats Booked and a moderate increase in ADR due to price appreciation and FX")
g("4Q25", "1Q26", "adj_ebitda_margin_yoy_pts", "point", mid=0.0, unit="pts",
  quote="We expect Adjusted EBITDA Margin to be approximately flat year-over-year")
gb("4Q25", "FY2026", "revenue_yoy_pct", "low-double",
   "For 2026, we expect year-over-year revenue growth to accelerate to at least low double digits",
   note="floor language ('at least'); recorded as a bucket floor, see guide_type_note")
g("4Q25", "FY2026", "adj_ebitda_margin_yoy_pts", "point", mid=0.0, unit="pts",
  quote="For 2026, we expect our Adjusted EBITDA Margin to be stable year-over-year")

# ---- 1Q26 print, targets 2Q26 / FY26 ---------------------------------------------------------
g("1Q26", "2Q26", "revenue_usd_m", "range", 3540, 3600, 3570, "USD m",
  "We expect to generate revenue of $3.54 billion to $3.60 billion")
g("1Q26", "2Q26", "revenue_yoy_pct", "range", 14, 16, 15.0, "pct",
  "representing year-over-year growth of 14% to 16%, inclusive of an approximate 3% FX tailwind after factoring in our hedging program")
g("1Q26", "2Q26", "take_rate_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We expect our implied take rate in Q2 2026 to be up slightly year-over-year")
gb("1Q26", "2Q26", "gbv_yoy_pct", "low-double",
   "In Q2 2026, we expect GBV to increase in the low double digits year-over-year")
g("1Q26", "2Q26", "nights_yoy_pct", "directional", unit="pct",
  quote="In Q2 2026, we expect Nights and Seats booked growth to slightly decelerate, relative to Q1 2026, assuming an estimated roughly 100bps headwind related to the conflict in the Middle East",
  cmp_value=9.1, direction="below", note="1Q26 nights y/y +9.1%; actual 2Q26 +10.3% -> NOT met (accelerated)")
g("1Q26", "2Q26", "adr_yoy_pct", "directional", unit="pct",
  quote="We expect the FX tailwind to ADR to be significantly lower in Q2 2026 than in Q1", cmp_value=8.0,
  direction="below", note="1Q26 ADR +9.0% y/y; actual 2Q26 +5.3% -> met")
g("1Q26", "2Q26", "adj_ebitda_margin_yoy_pts", "floor", low=0.0, unit="pts",
  quote="We expect Adjusted EBITDA and Adjusted EBITDA Margin to be up year-over-year in Q2 2026")
gb("1Q26", "FY2026", "revenue_yoy_pct", "low-to-mid-teens",
   "For 2026, we are raising our guidance and now expect year-over-year revenue growth to accelerate to low to mid teens")
g("1Q26", "FY2026", "adj_ebitda_margin_pct", "floor", low=35.0, unit="pct",
  quote="For 2026, we now expect our Adjusted EBITDA Margin to be at least 35%")
g("1Q26", "FY2026", "tax_rate_pct", "range", 17, 19, 18.0, "pct",
  "For the full-year 2026, we expect our effective tax rate to be in the high teens",
  note="'high teens' -> 17-19%")

# ---- 2Q26 print, targets 3Q26 / FY26 (open) --------------------------------------------------
g("2Q26", "3Q26", "revenue_usd_m", "range", 4690, 4770, 4730, "USD m",
  "We expect to generate revenue of $4.69 billion to $4.77 billion")
g("2Q26", "3Q26", "revenue_yoy_pct", "range", 15, 17, 16.0, "pct",
  "representing year-over-year growth of 15% to 17%, inclusive of an approximate three percentage point FX tailwind after factoring in our hedging program")
g("2Q26", "3Q26", "take_rate_yoy_pts", "point", mid=0.0, unit="pts",
  quote="We expect our implied take rate to remain relatively in-line year-over-year")
gb("2Q26", "3Q26", "gbv_yoy_pct", "mid-teens",
   "We expect year-over-year GBV growth to be in the mid teens")
gb("2Q26", "3Q26", "nights_yoy_pct", "low-double",
   "driven by low double-digit growth in Nights and Seats Booked and a moderate increase in ADR due to mix shift and price appreciation")
g("2Q26", "3Q26", "adr_yoy_pct", "floor", low=0.0, unit="pct",
  quote="a moderate increase in ADR due to mix shift and price appreciation")
g("2Q26", "3Q26", "adj_ebitda_margin_yoy_pts", "ceiling", high=0.0, unit="pts",
  quote="We expect Adjusted EBITDA to increase year-over-year and Adjusted EBITDA Margin to be down slightly compared to Q3 2025, due to timing of investments")
gb("2Q26", "FY2026", "revenue_yoy_pct", "mid-teens",
   "we now expect year-over-year revenue growth to improve to at least mid teens",
   note="floor language ('at least')")
g("2Q26", "FY2026", "adj_ebitda_margin_pct", "floor", low=35.5, unit="pct",
  quote="For 2026, we now expect to deliver a full-year Adjusted EBITDA Margin of at least 35.5%")
g("2Q26", "FY2026", "tax_rate_pct", "range", 17, 19, 18.0, "pct",
  "For the full-year 2026, we expect our ee ff ctive tax rate to be in the high teens",
  note="'high teens' -> 17-19%; OCR artefact 'ee ff ctive' is in the filed HTML")

# ---- guides given on the call, not in the letter ----------------------------------------------
g("3Q25", "FY2026", "tax_rate_pct", "qualitative", unit="narrative",
  quote="we anticipate that the One Big Beautiful Bill will materially reduce our effective tax rate",
  direction="down", src="transcript", note="2025-Q3 call, CFO; first flag of the FY26 tax step-down")
g("4Q25", "FY2026", "tax_rate_pct", "range", 15, 19, 17.0, "pct",
  "we expect the One Big Beautiful Bill Act to materially reduce our effective tax rate to the mid to high-teens",
  src="transcript", note="2025-Q4 call; the letter itself gave no FY26 tax guide")

# ----------------------------------------------------------------------------------------------
# Outcome logic
# ----------------------------------------------------------------------------------------------
MORE_IS_BETTER = {  # for signing "beat" on point / range guides
    "revenue_usd_m": 1, "revenue_yoy_pct": 1, "revenue_yoy_exfx_pct": 1, "nights_yoy_pct": 1, "gbv_yoy_pct": 1,
    "adr_yoy_pct": 1, "adj_ebitda_usd_m": 1, "adj_ebitda_margin_pct": 1, "adj_ebitda_margin_yoy_pts": 1,
    "take_rate_yoy_pts": 1, "take_rate_pct_seq": 1, "adr_usd_seq": 1, "fcf_margin_pct": 1, "fcf_margin_minus_ebitda_margin_pts": 1, "nights_m": 1,
    "gbv_usd_b": 1, "sbc_yoy_pct": -1, "tax_rate_pct": -1, "sm_pct_rev_yoy_bps": -1,
    "sm_growth_minus_rev_growth_pts": 0, "new_business_investment_usd_m": 0, "capex_usd_m": 0,
}

rows = []
for i, d in enumerate(G):
    pq, tp, metric = d["print_q"], d["target_period"], d["metric"]
    a = actual(metric, tp)
    src_ok = verify(pq, d["quote"], "transcript" if d["source"] == "transcript" else "letter")

    # horizon in quarters from the print quarter to the end of the target period
    def qidx(q):
        return (2000 + int(q[2:])) * 4 + int(q[0])
    if tp.startswith("FY"):
        tq = f"4Q{int(tp[2:]) % 100:02d}"
    elif tp.startswith(("1H", "2H")):
        tq = f"{'2' if tp[0] == '1' else '4'}Q{int(tp[2:]) % 100:02d}"
    else:
        tq = tp
    horizon = qidx(tq) - qidx(pq)

    outcome, dist, cushion = "", np.nan, np.nan
    gt = d["guide_type"]
    lo, hi, mid = d["value_low"], d["value_high"], d["value_mid"]
    if pd.isna(a) if isinstance(a, float) else a is None:
        if metric in ("new_business_investment_usd_m", "capex_usd_m") or d["guide_type"] == "qualitative":
            outcome = "not_scoreable"
        else:
            outcome = "pending" if (tq not in REPORTED or (tp.startswith("FY") and int(tp[2:]) > 2025)) else "no_actual"
    else:
        if gt in ("range", "bucket"):
            if a > hi:
                outcome = "above_range"
            elif a < lo:
                outcome = "below_range"
            else:
                outcome = "within_range"
            dist = a - mid
            cushion = a - hi if a > hi else (a - lo if a < lo else 0.0)
        elif gt == "floor":
            outcome = "met" if a >= lo - 1e-9 else "not_met"
            cushion = a - lo
            dist = cushion
        elif gt == "ceiling":
            outcome = "met" if a <= hi + 1e-9 else "not_met"
            cushion = hi - a
            dist = a - hi
        elif gt == "point":
            dist = a - mid
            s = MORE_IS_BETTER.get(metric, 1)
            outcome = "at_point" if abs(dist) <= max(d["tol"], 0.5) else ("above_point" if dist > 0 else "below_point")
            if s != 0 and abs(dist) > max(d["tol"], 0.5):
                outcome = "beat" if dist * s > 0 else "miss"
        elif gt == "directional":
            c, dr, tol = d["cmp_value"], d["direction"], d["tol"]
            if dr in ("above", "accelerate"):
                outcome = "met" if c is not None and a > c else ("not_met" if c is not None else "n/a")
            elif dr in ("below", "below_seq", "decelerate"):
                outcome = "met" if c is not None and a < c else ("not_met" if c is not None else "n/a")
            elif dr == "above_seq":
                outcome = "met" if c is not None and a > c else "not_met"
            elif dr in ("stable", "approx", "approx_seq"):
                outcome = "met" if c is not None and abs(a - c) <= max(tol, 2.0) else "not_met"
            elif dr == "below_revenue_growth":
                rg = actual("revenue_yoy_pct", tp)
                outcome = "met" if pd.notna(rg) and a < rg else "not_met"
            elif dr == "accelerate_vs_prior_q":
                prev = ORDER[ORDER.index(tq) - 1] if tq in ORDER else None
                pv = actual(metric, prev) if prev else np.nan
                outcome = "met" if pd.notna(pv) and a > pv else "not_met"
            elif dr == "between_2020_and_2019":
                outcome = "n/a (2019 base not in panel)"
            else:
                outcome = "n/a"
            dist = a - c if c is not None else np.nan
        else:
            outcome = "qualitative"

    rows.append(dict(
        guide_id=f"ABNB-{pq}-{metric}-{tp}-{i:03d}",
        print_quarter=pq, print_date=PRINT_DATE[pq], target_period=tp, horizon_quarters=horizon,
        metric=metric, guide_type=gt,
        value_low=lo, value_high=hi, value_mid=mid, unit=d["unit"],
        direction=d["direction"], comparator_value=d["cmp_value"],
        actual=round(a, 2) if isinstance(a, float) and pd.notna(a) else np.nan,
        outcome=outcome,
        distance_from_mid=round(dist, 2) if pd.notna(dist) else np.nan,
        cushion=round(cushion, 2) if pd.notna(cushion) else np.nan,
        pct_distance_from_mid=(round(100 * dist / abs(mid), 2) if (gt in ("range", "bucket", "point") and mid not in (None, 0)
                                                                   and pd.notna(dist)) else np.nan),
        source=d["source"], source_file=(str(LETTER_FILES[pq].relative_to(ROOT)).replace("\\", "/")
                                         if d["source"] == "letter" and pq in LETTER_FILES
                                         else f"data/raw/regulatory/transcripts/20{pq[2:]}-Q{pq[0]}"),
        verified=src_ok, quote=d["quote"], note=d["note"],
    ))

L = pd.DataFrame(rows)

# later revision: a later print that guides the same metric and the same target period
L["revised_later_by"] = ""
L["revision_delta"] = np.nan
for (tp, metric), grp in L.groupby(["target_period", "metric"]):
    grp = grp.sort_values("print_quarter", key=lambda s: s.map(lambda q: ORDER.index(q)))
    ids = grp.index.tolist()
    for a_, b_ in zip(ids, ids[1:]):
        L.loc[a_, "revised_later_by"] = L.loc[b_, "print_quarter"]
        va = L.loc[a_, "value_mid"] if pd.notna(L.loc[a_, "value_mid"]) else L.loc[a_, "value_low"]
        vb = L.loc[b_, "value_mid"] if pd.notna(L.loc[b_, "value_mid"]) else L.loc[b_, "value_low"]
        if pd.notna(va) and pd.notna(vb):
            L.loc[b_, "revision_delta"] = float(vb) - float(va)

L = L.sort_values(["print_quarter", "target_period", "metric"],
                  key=lambda s: s.map(lambda x: ORDER.index(x)) if s.name == "print_quarter" else s)
L.to_csv(OUT / "02_guidance_ledger.csv", index=False)

# coverage matrix
cov = L.pivot_table(index="print_quarter", columns="metric", values="guide_id", aggfunc="count").reindex(ORDER)
cov["n_guides"] = L.groupby("print_quarter").size().reindex(ORDER)
cov["max_horizon_q"] = L.groupby("print_quarter")["horizon_quarters"].max().reindex(ORDER)
cov.to_csv(OUT / "02_guidance_coverage.csv")

# full-year guide paths
fyr = L[L.target_period.str.startswith("FY")].sort_values(
    ["target_period", "metric", "print_quarter"],
    key=lambda s: s.map(lambda x: ORDER.index(x)) if s.name == "print_quarter" else s)
fyr[["target_period", "metric", "print_quarter", "print_date", "guide_type", "value_low", "value_high",
     "value_mid", "unit", "actual", "outcome", "cushion", "quote"]].to_csv(OUT / "02_fy_guide_revisions.csv", index=False)

print("ledger rows:", len(L), " unverified quotes:", int((~L.verified).sum()))
if (~L.verified).any():
    print(L[~L.verified][["print_quarter", "metric", "quote"]].to_string())
print(L.outcome.value_counts().to_string())
print("\nby horizon:\n", L.horizon_quarters.value_counts().sort_index().to_string())
