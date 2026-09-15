"""
Workstream C, step 1. Regional target panel.

Every disclosed regional nights growth figure by quarter from the 23 shareholder letters
(North America / EMEA / Latin America / Asia Pacific), the annual 10-K regional nights,
and the origin-country nights commentary that is the only true origin-basis disclosure.

Every quote is verified to exist in the raw letter text before it is written out. A row whose
quote does not verify is dropped and listed in C1_quote_failures.csv.

Reads (main tree, read only):
  data/raw/letters/*.htm
  data/processed/adr/01_regional_annual.csv        (10-K geographic mix, rebuilt by the ADR study)

Writes:
  data/processed/overnight2/C/regional_target_panel.csv
  data/processed/overnight2/C/origin_country_panel.csv
  data/processed/overnight2/C/C1_quote_failures.csv
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import pandas as pd

MAIN = Path(r"C:/Users/krish/citadel-abnb")
OUT = Path(__file__).resolve().parents[3] / "data/processed/overnight2/C"
OUT.mkdir(parents=True, exist_ok=True)


def letter_text(path: Path) -> str:
    s = path.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<style.*?</style>", "", s, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t).replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[\u2018\u2019\u201c\u201d\u2014\u2013\ufffd\u0027\"\-]", " ", s)
    return re.sub(r"[^a-z0-9%$.]+", " ", s).strip()


LETTERS = {p.name[:4]: p for p in (MAIN / "data/raw/letters").glob("*.htm")}
NTEXT = {q: norm(letter_text(p)) for q, p in LETTERS.items()}

# Stated mapping from Airbnb qualitative bucket language to a numeric midpoint.
# Researcher reading, not a company statement. Half-width is used for the band in step 5.
BUCKETS = {
    "low-single digit": (2.0, 1.0),
    "mid-single digit": (5.0, 1.0),
    "high-single digit": (8.0, 1.0),
    "low-double digit": (11.0, 1.0),
    "low-teens": (13.0, 1.0),
    "mid-teens": (15.0, 1.0),
    "high-teens": (18.0, 1.0),
    "low-20s": (21.0, 1.0),
}

# quarter, region, bucket or "numeric", value, quote fragment that must appear in that letter.
# basis note: Airbnb reports these regions by the LISTING location, not the guest origin.
ROWS = [
    ("3Q22", "na", "numeric", 20.0, "north america remained strong with nights and experiences booked in q3 increasing 20% above the level achieved in the same quarter of 2021"),
    ("3Q22", "emea", "numeric", 20.0, "in emea nights and experiences booked grew 20% compared to q3 2021"),
    ("3Q22", "latam", "numeric", 33.0, "in latin america nights and experiences booked were 33% higher than q3 2021"),
    ("3Q22", "apac", "numeric", 65.0, "apac increased the most with 65% more nights and experiences booked"),
    ("4Q22", "emea", "numeric", 25.0, "in emea nights and experiences booked grew 25% compared to q4 2021"),
    ("4Q22", "latam", "numeric", 23.0, "in latin america nights and experiences booked were 23% higher than q4 2021"),
    ("4Q22", "apac", "numeric", 40.0, "asia pacific once again increased the most with 40% more nights and experiences booked"),
    ("1Q23", "emea", "numeric", 21.0, "in emea nights and experiences booked grew 21% compared to q1 2022"),
    ("1Q23", "latam", "numeric", 22.0, "in latin america nights and experiences booked were 22% higher than q1 2022"),
    ("1Q23", "apac", "numeric", 48.0, "48% growth in nights and experiences booked in q1 2023 compared to a year ago"),
    ("2Q23", "latam", "numeric", 22.0, "in latin america nights and experiences booked were 22% higher than q2 2022"),
    ("2Q23", "apac", "numeric", 24.0, "in asia pacific nights and experiences booked saw 24% year over year growth"),
    ("3Q23", "latam", "numeric", 24.0, "in latin america nights and experiences booked were 24% higher than q3 2022"),
    ("3Q23", "apac", "numeric", 27.0, "in asia pacific nights and experiences booked saw a sequential acceleration in year over year growth of 27%"),
    ("4Q23", "latam", "numeric", 22.0, "in latin america nights and experiences booked were 22% higher than q4 2022"),
    ("4Q23", "apac", "numeric", 22.0, "in asia pacific nights and experiences booked increased 22% on a year over year basis"),
    ("1Q24", "latam", "numeric", 19.0, "in latin america nights and experiences booked grew 19% in q1 2024 compared to q1 2023"),
    ("1Q24", "apac", "numeric", 21.0, "in asia pacific nights and experiences booked increased 21% on a year over year basis"),
    ("2Q24", "latam", "numeric", 17.0, "in latin america nights and experiences booked grew 17% in q2 2024 compared to q2 2023"),
    ("2Q24", "apac", "numeric", 19.0, "in asia pacific nights and experiences booked increased 19% on a year over year basis"),
    ("3Q24", "latam", "numeric", 15.0, "in latin america nights and experiences booked grew 15% in q3 2024 compared to q3 2023"),
    ("3Q24", "apac", "numeric", 19.0, "in asia pacific nights and experiences booked increased 19% on a year over year basis stable with the prior quarter"),
    ("4Q24", "na", "mid-single digit", None, "in north america we saw mid single digits nights and experiences booked growth in q4 2024 compared to q4 2023"),
    ("4Q24", "emea", "low-double digit", None, "in emea we saw low double digits nights and experiences booked growth in q4 2024 compared to q4 2023"),
    ("4Q24", "latam", "low-20s", None, "in latin america we saw low 20s nights and experiences booked growth in q4 2024 compared to q4 2023"),
    ("4Q24", "apac", "low-20s", None, "in asia pacific we saw low 20s nights and experiences booked growth in q4 2024 compared to q4 2023"),
    ("1Q25", "na", "low-single digit", None, "in north america we saw low single digits nights and experiences booked growth in q1 2025 compared to q1 2024"),
    ("1Q25", "emea", "mid-single digit", None, "in emea we saw mid single digits nights and experiences booked growth in q1 2025 compared to q1 2024"),
    ("1Q25", "latam", "low-20s", None, "in latin america we saw low 20s nights and experiences booked growth in q1 2025 compared to q1 2024"),
    ("1Q25", "apac", "mid-teens", None, "in asia pacific we saw mid teens nights and experiences booked growth in q1 2025 compared to q1 2024"),
    ("2Q25", "na", "low-single digit", None, "in north america we saw low single digit growth in nights and seats booked during q2 2025 compared to q2 2024"),
    ("2Q25", "emea", "mid-single digit", None, "in emea we saw mid single digit growth in nights and seats booked during q2 2025 compared to q2 2024"),
    ("2Q25", "latam", "high-teens", None, "in latin america we saw high teens growth in nights and seats booked during q2 2025 compared to q2 2024"),
    ("2Q25", "apac", "mid-teens", None, "in asia pacific we saw mid teens growth in nights and seats booked during q2 2025 compared to q2 2024"),
    ("3Q25", "na", "mid-single digit", None, "in north america we saw mid single digit growth of nights and seats booked during q3 2025 compared to q3 2024 representing a sequential acceleration"),
    ("3Q25", "emea", "mid-single digit", None, "in emea we saw mid single digit growth in nights and seats booked during q3 2025 compared to q3 2024"),
    ("3Q25", "latam", "low-20s", None, "in latin america we saw low 20s growth in nights and seats booked during q3 2025 compared to q3 2024"),
    ("3Q25", "apac", "mid-teens", None, "in asia pacific we saw mid teens growth in nights and seats booked during q3 2025 compared to q3 2024"),
    ("4Q25", "na", "mid-single digit", None, "in north america we saw mid single digit growth of nights and seats booked during q4 2025 compared to q4 2024"),
    ("4Q25", "emea", "high-single digit", None, "in emea we saw high single digit growth in nights and seats booked during q4 2025 compared to q4 2024 representing an acceleration compared to q3 2025"),
    ("4Q25", "latam", "high-teens", None, "in latin america we saw high teens growth in nights and seats booked during q4 2025 compared to q4 2024"),
    ("4Q25", "apac", "mid-teens", None, "in asia pacific we saw mid teens growth in nights and seats booked during q4 2025 compared to q4 2024"),
    ("1Q26", "na", "high-single digit", None, "in north america we saw high single digit growth of nights and seats booked during q1 2026 compared to q1 2025"),
    ("1Q26", "emea", "mid-single digit", None, "in emea we saw mid single digit growth in nights and seats booked during q1 2026 compared to q1 2025"),
    ("1Q26", "latam", "high-teens", None, "in latin america we saw high teens growth in nights and seats booked during q1 2026 compared to q1 2025"),
    ("1Q26", "apac", "high-teens", None, "in asia pacific we saw high teens growth in nights and seats booked during q1 2026 compared to q1 2025"),
    ("2Q26", "na", "high-single digit", None, "in north america we saw high single digit growth of nights and seats booked during q2 2026 compared to q2 2025"),
    ("2Q26", "emea", "high-single digit", None, "in emea we saw high single digit growth in nights and seats booked during q2 2026 compared to q2 2025 accelerating from q1 2026"),
    ("2Q26", "latam", "numeric", 20.0, "in latin america we saw approximately 20% growth in nights and seats booked during q2 2026 compared to q2 2025"),
    ("2Q26", "apac", "high-teens", None, "in asia pacific we saw high teens growth in nights and seats booked during q2 2026 compared to q2 2025"),
]

CROSSCHECK = [
    ("1Q25", "ex_na", 11.0, "excluding north america nights and experiences booked grew 11% year over year in q1 2025", "nights_yoy_ex_na"),
    ("2Q25", "ex_na", 10.0, "nights and seats booked grew double digits year over year in q2 2025 when excluding north america which contributes approximately 30% of total nights and seats booked", "nights_yoy_ex_na_floor"),
    ("3Q25", "ex_na", 10.0, "nights and seats booked grew double digits year over year in q3 2025 when excluding north america which contributed approximately 30% of total nights and seats booked", "nights_yoy_ex_na_floor"),
]

ORIGIN = [
    ("4Q23", "CHN", 90.0, "nearly", "in q4 2023 nights booked in china on an origin basis increased nearly 90% on a year over year basis"),
    ("1Q24", "CHN", 80.0, "nearly", "in q1 2024 nights booked on an origin basis in china increased nearly 80% on a year over year basis"),
    ("4Q24", "BRA", 21.0, "over20", "origin nights booked in brazil grew over 20% for both q4 and full year 2024"),
    ("4Q24", "CHN", 25.0, "numeric", "we are encouraged by the recovery of the china outbound business with nights booked growing 25% year over year in q4 2024"),
    ("1Q25", "BRA", 27.0, "numeric", "in brazil origin nights booked grew 27% in q1 2025"),
    ("2Q25", "BRA", 18.0, "high-teens", "brazil continued to drive meaningful growth across the region with origin nights booked increasing at a high teens rate"),
    ("2Q25", "DEU", 11.0, "low-double digit", "we saw strong results in germany one of our expansion markets with double digit year over year growth of nights booked in q2 2025 representing an acceleration compared to q1 2025"),
    ("3Q25", "BRA", 21.0, "over20", "brazil continued to drive meaningful growth across the region with origin nights booked increasing over 20% and the number of first time bookers increasing 17% in q3 2025 compared to q3 2024"),
    ("3Q25", "JPN", 27.0, "domestic", "in japan nights booked for domestic travel in q3 2025 increased 27% year over year representing the third consecutive quarter of acceleration"),
    ("4Q25", "BRA", 21.0, "over20", "brazil continued to drive meaningful growth across the region with origin nights booked increasing over 20% and the number of first time bookers increasing 17% in q4 2025 compared to q4 2024"),
    ("4Q25", "MEX", 18.0, "high-teens", "we saw a strong sequential acceleration of growth in origin nights booked in mexico up high teens on a year over year basis in q4 2025"),
    ("4Q25", "IND", 50.0, "numeric", "q4 2025 nights booked on an origin basis in india grew 50% year over year"),
    ("1Q26", "BRA", 21.0, "over20", "brazil continued to drive meaningful growth with origin nights booked increasing over 20% for the third consecutive quarter"),
    ("1Q26", "IND", 50.0, "approximately", "in india origin nights booked grew approximately 50% year over year"),
    ("1Q26", "MEX", 11.0, "low-double digit", "we saw continued double digit nights growth in mexico"),
    ("2Q26", "BRA", 31.0, "over30", "brazil continued to see meaningful demand with origin net nights booked accelerating to over 30% year over year growth"),
    ("2Q26", "JPN", 18.0, "high-teens", "japan where in q2 2026 origin net nights booked grew in the high teens year over year driven by continued momentum for domestic travel"),
    ("2Q26", "IND", 60.0, "numeric", "we saw origin net nights booked in india accelerate to 60% year over year"),
]

KIND_BASIS = {
    "numeric": "disclosed numeric",
    "nearly": "stated as nearly X%, read at face value",
    "approximately": "stated as approximately X%, read at face value",
    "over20": "stated as over 20%, read as 21",
    "over30": "stated as over 30%, read as 31",
    "high-teens": "bucket, mapped to 18",
    "low-double digit": "stated as double digit, read as 11",
    "domestic": "DOMESTIC nights in that country, not total origin nights",
}


def verify(q: str, quote: str) -> bool:
    return q in NTEXT and norm(quote) in NTEXT[q]


def build_regional():
    rows, fails = [], []
    for q, region, bucket, val, quote in ROWS:
        if not verify(q, quote):
            fails.append({"table": "regional", "quarter": q, "region": region, "quote": quote})
            continue
        if bucket == "numeric":
            value, halfwidth, basis = val, 0.5, "disclosed numeric y/y"
        else:
            value, halfwidth = BUCKETS[bucket]
            basis = f"qualitative bucket {bucket} mapped to midpoint {value}, researcher mapping, half-width {halfwidth}pp"
        rows.append({
            "quarter": q, "region": region, "metric": "nights_yoy_pct_destination",
            "value": value, "halfwidth_pp": halfwidth, "basis": basis,
            "source": f"{q} shareholder letter ({LETTERS[q].name})", "quote": quote,
        })
    for q, region, val, quote, metric in CROSSCHECK:
        if not verify(q, quote):
            fails.append({"table": "crosscheck", "quarter": q, "region": region, "quote": quote})
            continue
        rows.append({
            "quarter": q, "region": region, "metric": metric, "value": val,
            "halfwidth_pp": 0.5 if metric == "nights_yoy_ex_na" else 2.0,
            "basis": "disclosed numeric" if metric == "nights_yoy_ex_na" else "floor only: double digits, read as at least 10",
            "source": f"{q} shareholder letter", "quote": quote,
        })
    return pd.DataFrame(rows), fails


def build_origin():
    rows, fails = [], []
    for q, iso, val, kind, quote in ORIGIN:
        if not verify(q, quote):
            fails.append({"table": "origin", "quarter": q, "region": iso, "quote": quote})
            continue
        rows.append({
            "quarter": q, "country_iso3": iso, "metric": "origin_nights_yoy_pct",
            "value": val, "value_kind": kind, "basis": KIND_BASIS[kind],
            "source": f"{q} shareholder letter", "quote": quote,
        })
    return pd.DataFrame(rows), fails


def build_annual() -> pd.DataFrame:
    a = pd.read_csv(MAIN / "data/processed/adr/01_regional_annual.csv")
    a = a[a.region != "total"].copy()
    rows = []
    for _, r in a.iterrows():
        tag = f"10-K {r['source_10k']} Geographic Mix via data/processed/adr/01_regional_annual.csv"
        if pd.notna(r["nights_m_yoy_pct"]):
            rows.append({
                "quarter": f"FY{int(r['year'])}", "region": r["region"],
                "metric": "nights_yoy_pct_annual_10k", "value": round(float(r["nights_m_yoy_pct"]), 2),
                "halfwidth_pp": 1.0,
                "basis": "10-K nights rounded to whole millions from FY2022, so roughly +/-1pp at these levels",
                "source": tag, "quote": f"nights {r['nights_m']}m in {int(r['year'])}",
            })
        rows.append({
            "quarter": f"FY{int(r['year'])}", "region": r["region"],
            "metric": "nights_share_pct_annual_10k", "value": round(float(r["nights_share_pct"]), 2),
            "halfwidth_pp": 0.5, "basis": "10-K nights share by listing location",
            "source": tag, "quote": f"nights {r['nights_m']}m in {int(r['year'])}",
        })
        rows.append({
            "quarter": f"FY{int(r['year'])}", "region": r["region"],
            "metric": "adr_usd_annual_10k", "value": round(float(r["adr_computed"]), 2),
            "halfwidth_pp": 0.0, "basis": "GBV divided by nights from the 10-K Geographic Mix table",
            "source": tag, "quote": f"gbv {r['gbv_musd']}musd over nights {r['nights_m']}m",
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    reg, f1 = build_regional()
    org, f2 = build_origin()
    ann = build_annual()

    panel = pd.concat([reg, ann], ignore_index=True)
    panel.to_csv(OUT / "regional_target_panel.csv", index=False)
    org.to_csv(OUT / "origin_country_panel.csv", index=False)
    pd.DataFrame(f1 + f2).to_csv(OUT / "C1_quote_failures.csv", index=False)

    print("regional_target_panel rows", len(panel))
    print(panel.groupby("metric").size().to_string())
    print("origin rows", len(org))
    print("quote failures", len(f1 + f2))
    for f in f1 + f2:
        print("  FAIL", f["quarter"], f["region"], f["quote"][:80])

