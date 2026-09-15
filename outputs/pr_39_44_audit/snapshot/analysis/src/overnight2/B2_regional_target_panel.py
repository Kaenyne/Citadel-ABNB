"""B2: the regional / corridor target panel for the FX geographic-mix study.

Long format, one row per (quarter, region, metric). Everything is either a
disclosure, a disclosure mapped from a qualitative bucket, an XBRL fact, or a
third-party statistic, and the basis column says which.

Sources, all read read-only from the MAIN tree C:\\Users\\krish\\citadel-abnb:
  data/processed/overnight/10_regional_panel_quarterly.csv  (WS10 letter extraction)
  data/processed/overnight/10_regional_quotes.csv           (letter sentences)
  data/processed/overnight/10_xbrl_revenue_geography.csv    (10-K/10-Q geography)
  data/processed/overnight/05_crossborder_share.csv         (2019 + 2021-1Q24)
  data/processed/overnight/05_regional_growth.csv           (bucket wording + source)
  data/processed/overnight/05_macro_quarterly_panel.csv     (BEA inbound/outbound)
  data/processed/eurostat_platform_nights_monthly.csv       (EU27 domestic/foreign)

Run: py -3.13 analysis/src/overnight2/B2_regional_target_panel.py
Writes data/processed/overnight2/B/regional_target_panel.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\krish\citadel-abnb-overnight2")
MAIN = Path(r"C:\Users\krish\citadel-abnb")
MP = MAIN / "data" / "processed" / "overnight"
OUT = ROOT / "data" / "processed" / "overnight2" / "B"
OUT.mkdir(parents=True, exist_ok=True)

REGIONS = ["na", "emea", "latam", "apac"]
LETTER = "Airbnb shareholder letter"
rows: list[dict] = []


def add(quarter, region, metric, value, basis, source, quote=""):
    rows.append({"quarter": quarter, "region": region, "metric": metric,
                 "value": value, "basis": basis, "source": source,
                 "quote": " ".join(str(quote).split())[:600]})


# --------------------------------------------------------------- WS10 panel
panel = pd.read_csv(MP / "10_regional_panel_quarterly.csv")
quotes = pd.read_csv(MP / "10_regional_quotes.csv")
regional_src = pd.read_csv(MP / "05_regional_growth.csv").set_index("quarter")

QMAP = {"1Q": "Q1", "2Q": "Q2", "3Q": "Q3", "4Q": "Q4"}


def src_for(q):
    """Letter/call attribution string as recorded by WS05 where available."""
    key = f"20{q[2:]}{QMAP[q[:2]]}"
    if key in regional_src.index:
        return f"{LETTER} / call ({regional_src.loc[key, 'source']})"
    return f"{LETTER} {q}"


def first_quote(q, cats, kw=None):
    sub = quotes[quotes.quarter == q]
    if cats:
        sub = sub[sub.categories.str.contains(cats, na=False)]
    if kw:
        sub = sub[sub.sentence.str.contains(kw, case=False, regex=True, na=False)]
    return sub.sentence.iloc[0] if len(sub) else ""


CAT = {"na": "north_america", "emea": "emea", "latam": "latin_america",
       "apac": "asia_pacific"}

for _, r in panel.iterrows():
    q = r["quarter"]
    tot = r["total_nights_yoy_pct"]
    if pd.notna(tot):
        add(q, "total", "nights_yoy_pct", round(float(tot), 2), "disclosed numeric",
            f"{LETTER} {q} (KPI table)")
    for reg in REGIONS:
        mid, basis, phrase = r[f"{reg}_nights_yoy_mid"], r[f"{reg}_basis"], r[f"{reg}_phrase"]
        if pd.notna(mid):
            add(q, reg, "nights_yoy_pct", round(float(mid), 2), str(basis),
                src_for(q), phrase if pd.notna(phrase) else first_quote(q, CAT[reg]))
            if pd.notna(tot):
                add(q, reg, "nights_yoy_differential_pp", round(float(mid) - float(tot), 2),
                    f"derived: region minus total ({basis})", "derived from the two rows above")
        for lab, col in [("nights_yoy_lo_pct", f"{reg}_nights_yoy_lo"),
                         ("nights_yoy_hi_pct", f"{reg}_nights_yoy_hi")]:
            if pd.notna(r[col]):
                add(q, reg, lab, round(float(r[col]), 2), str(basis), src_for(q))
        for lab, col in [("adr_yoy_reported_pct", f"{reg}_adr_yoy_reported_pct"),
                         ("adr_yoy_exfx_pct", f"{reg}_adr_yoy_exfx_pct")]:
            if pd.notna(r[col]):
                add(q, reg, lab, float(r[col]), "disclosed numeric (rounded to 1pp in the letter)",
                    src_for(q))
        for lab, col in [("revenue_musd", f"{reg}_revenue_musd"),
                         ("revenue_yoy_pct", f"{reg}_revenue_yoy_pct"),
                         ("revenue_share_pct", f"{reg}_revenue_share_pct"),
                         ("nights_share_est_pct", f"{reg}_nights_share_est_pct")]:
            if pd.notna(r[col]):
                b = ("XBRL srt:StatementGeographicalAxis" if "revenue" in lab
                     else "WS10 estimate (revenue / regional ADR index)")
                add(q, reg, lab, round(float(r[col]), 2), b,
                    "10-Q/10-K XBRL via EDGAR" if "revenue" in lab
                    else "data/processed/overnight/10_regional_panel_quarterly.csv")
    # totals and corridor series
    for lab, col, basis in [
        ("cross_border_share_of_gross_nights_pct", "cross_border_share_pct", "disclosed numeric"),
        ("cross_border_nights_growth_pct", "cross_border_growth_pct", "disclosed numeric"),
        ("domestic_share_of_gross_nights_pct", "domestic_share_pct", "disclosed numeric"),
        ("urban_share_of_gross_nights_pct", "urban_share_pct", "disclosed numeric"),
        ("long_term_stay_share_pct", "long_term_stay_share_pct", "disclosed numeric"),
        ("na_share_of_nights_pct", "na_share_of_nights_pct_disclosed", "disclosed numeric"),
    ]:
        if pd.notna(r[col]):
            add(q, "total", lab, float(r[col]), basis, src_for(q),
                first_quote(q, "cross_border|domestic|urban", None))
    for reg, col in [("na", "cross_border_to_na_growth_pct"),
                     ("emea", "cross_border_to_emea_growth_pct"),
                     ("apac", "cross_border_to_apac_growth_pct")]:
        if pd.notna(r[col]):
            add(q, reg, "cross_border_nights_growth_to_region_pct", float(r[col]),
                "disclosed numeric", src_for(q),
                first_quote(q, "cross_border", "cross-border|cross border"))
    for lab, col, reg in [("origin_nights_growth_brazil_pct", "brazil_origin_growth_pct", "latam"),
                          ("origin_nights_growth_india_pct", "india_origin_growth_pct", "apac"),
                          ("domestic_nights_growth_japan_pct", "japan_domestic_growth_pct", "apac"),
                          ("origin_nights_growth_china_outbound_pct", "china_outbound_growth_pct", "apac"),
                          ("domestic_nights_growth_latam_pct", "latam_domestic_growth_pct", "latam")]:
        if pd.notna(r[col]):
            add(q, reg, lab, float(r[col]), "disclosed numeric", src_for(q),
                first_quote(q, None, {"origin_nights_growth_brazil_pct": "Brazil",
                                      "origin_nights_growth_india_pct": "India",
                                      "domestic_nights_growth_japan_pct": "Japan",
                                      "origin_nights_growth_china_outbound_pct": "China",
                                      "domestic_nights_growth_latam_pct": "Latin America"}[lab]))
    if isinstance(r["events_and_shocks"], str) and r["events_and_shocks"].strip():
        add(q, "total", "events_and_shocks", np.nan, "qualitative",
            src_for(q), r["events_and_shocks"])

# ------------------------------------------------- 2019 cross-border share
cb = pd.read_csv(MP / "05_crossborder_share.csv")
for _, r in cb.iterrows():
    y, qn = r["quarter"][:4], r["quarter"][-1]
    q = f"{qn}Q{y[2:]}"
    if not ((panel.quarter == q).any()
            and (panel.loc[panel.quarter == q, "cross_border_share_pct"].notna().any())):
        add(q, "total", "cross_border_share_of_gross_nights_pct", float(r.iloc[1]),
            "disclosed numeric (2019 values quoted as comparators in 2022-23 letters)",
            r["source"])

# --------------------------------------------- annual revenue by geography
geo = pd.read_csv(MP / "10_xbrl_revenue_geography.csv")
geo["start"], geo["end"] = pd.to_datetime(geo["start"]), pd.to_datetime(geo["end"])
ann = geo[(geo.form == "10-K") & ((geo.end - geo.start).dt.days > 300)].copy()
ann["fy"] = ann["end"].dt.year
GEOMAP = {"srt:NorthAmericaMember": "na", "us-gaap:EMEAMember": "emea",
          "srt:LatinAmericaMember": "latam", "srt:AsiaPacificMember": "apac",
          "country:US": "us_only", "us-gaap:NonUsMember": "non_us",
          "country:FR": "france_only"}
piv = ann.pivot_table(index="fy", columns="geo", values="value_usd", aggfunc="max") / 1e6
for fy in piv.index:
    tot = piv.loc[fy, [c for c in ["srt:NorthAmericaMember", "us-gaap:EMEAMember",
                                   "srt:LatinAmericaMember", "srt:AsiaPacificMember"]
                       if c in piv.columns]].sum()
    for gcol, reg in GEOMAP.items():
        if gcol not in piv.columns or pd.isna(piv.loc[fy, gcol]):
            continue
        v = piv.loc[fy, gcol]
        add(f"FY{fy}", reg, "annual_revenue_musd", round(float(v), 1),
            "XBRL 10-K srt:StatementGeographicalAxis (revenue attributed by listing location)",
            "Airbnb 10-K via EDGAR company facts")
        prev = piv.loc[fy - 1, gcol] if (fy - 1) in piv.index else np.nan
        if pd.notna(prev):
            add(f"FY{fy}", reg, "annual_revenue_yoy_pct", round(100 * (v / prev - 1), 2),
                "derived from the XBRL annual facts", "Airbnb 10-K via EDGAR")
        if reg in REGIONS and tot > 0:
            add(f"FY{fy}", reg, "annual_revenue_share_pct", round(100 * v / tot, 2),
                "derived from the XBRL annual facts", "Airbnb 10-K via EDGAR")

# --------------------------------------------------- BEA inbound / outbound
mac = pd.read_csv(MP / "05_macro_quarterly_panel.csv")
for _, r in mac.iterrows():
    y, qn = r["quarter"][:4], r["quarter"][-1]
    q = f"{qn}Q{y[2:]}"
    for lab, col in [("bea_inbound_foreign_travel_in_us_yoy_pct", "bea_inbound_foreign_travel"),
                     ("bea_outbound_us_travel_abroad_yoy_pct", "bea_outbound_us_travel")]:
        if pd.notna(r[col]):
            add(q, "na", lab, round(float(r[col]), 2),
                "third-party statistic (BEA PCE by function, real, y/y)",
                "BEA via FRED, pulled by WS05 2026-09-06")

# ------------------------------------------------ Eurostat EU27 residence mix
eu = pd.read_csv(MAIN / "data" / "processed" / "eurostat_platform_nights_monthly.csv")
eu["month"] = pd.to_datetime(eu["month"])
eu["q"] = eu["month"].dt.to_period("Q")
g = eu.groupby("q")[["eu27_nights", "eu27_domestic", "eu27_foreign"]].sum(min_count=3)
g = g[g["eu27_nights"] > 0]
g["foreign_share_pct"] = 100 * g["eu27_foreign"] / g["eu27_nights"]
for col in ["eu27_nights", "eu27_domestic", "eu27_foreign"]:
    g[f"{col}_yoy"] = 100 * (g[col] / g[col].shift(4) - 1)
g["foreign_share_chg_pp"] = g["foreign_share_pct"] - g["foreign_share_pct"].shift(4)
for p, r in g.iterrows():
    q = f"{p.quarter}Q{str(p.year)[2:]}"
    for lab, col in [("eurostat_eu27_platform_foreign_share_pct", "foreign_share_pct"),
                     ("eurostat_eu27_platform_foreign_share_chg_pp", "foreign_share_chg_pp"),
                     ("eurostat_eu27_platform_nights_yoy_pct", "eu27_nights_yoy"),
                     ("eurostat_eu27_platform_domestic_yoy_pct", "eu27_domestic_yoy"),
                     ("eurostat_eu27_platform_foreign_yoy_pct", "eu27_foreign_yoy")]:
        if pd.notna(r[col]):
            add(q, "emea", lab, round(float(r[col]), 3),
                "third-party statistic (Eurostat tour_ce_omr experimental, residence of guest)",
                "Eurostat, extracted 2026-07-02 vintage; complete quarters only")

# ------------------------------------------- hand-curated corridor sentences
CORRIDOR_FACTS = [
    ("1Q25", "na", "management_statement_us_inbound_share",
     "The vast majority of nights booked in the U.S. are by domestic travelers - only a "
     "single-digit percentage of global nights booked are international inbound to the U.S.",
     f"{LETTER} 1Q25"),
    ("1Q25", "na", "corridor_commentary_canada_to_us",
     "Looking at specific corridors, while we saw softness in travel from Canada to the U.S. "
     "during the end of Q1 2025, Canadian guests continued to travel on Airbnb.",
     f"{LETTER} 1Q25"),
    ("1Q25", "latam", "corridor_commentary_canada_to_mexico",
     "Nights booked by Canadian guests to destinations in Mexico increased 27% year-over-year "
     "in March.", f"{LETTER} 1Q25"),
    ("2Q25", "na", "corridor_commentary_canada_to_us",
     "While travel from Canada to the U.S. remained soft in Q2 2025, total nights booked by "
     "Canadians - both within Canada and to destinations outside of North America - "
     "accelerated from Q1 2025.", f"{LETTER} 2Q25"),
    ("1Q26", "na", "corridor_commentary_substitution",
     "When tariff uncertainty resulted in fewer people traveling to the U.S. last year, they "
     "still came to Airbnb and found somewhere else to go.", f"{LETTER} 1Q26"),
    ("4Q24", "apac", "corridor_commentary_apac_crossborder",
     "While we saw strong growth domestically, cross-border continues to drive the majority of "
     "nights booked in APAC.", f"{LETTER} 4Q24"),
    ("4Q22", "na", "corridor_commentary_na_domestic",
     "While the majority of travel in North America, both pre-pandemic and now, is domestic, we "
     "saw cross-border Nights and Experiences Booked to North America increase approximately "
     "35% in Q4 2022.", f"{LETTER} 4Q22"),
    ("3Q22", "total", "corridor_commentary_fx_neutrality",
     "Even with foreign currency fluctuations, we saw cross-border travel to all regions "
     "increase in Q3 2022 from last year.", f"{LETTER} 3Q22"),
    ("4Q22", "total", "corridor_commentary_fx_neutrality",
     "Globally, we saw cross-border travel to all regions increase in Q4 2022 from last year "
     "despite continued foreign currency volatility.", f"{LETTER} 4Q22"),
    ("4Q23", "total", "corridor_commentary_cross_currency",
     "We do not anticipate this change to affect the majority of our guests as cross-currency "
     "transactions only make up a portion of cross border bookings.", f"{LETTER} 4Q23"),
    ("2Q26", "total", "guide_fx_assumption_q3_2026",
     "[Q3 2026 revenue of $4.69 to $4.77 billion, growth of 15% to 17%,] inclusive of an "
     "approximate three percentage point FX tailwind after factoring in our hedging program.",
     f"{LETTER} 2Q26 and Q2 2026 earnings call, 6 August 2026"),
    ("2Q26", "total", "adr_driver_statement",
     "On an ex-FX basis, ADR in Q2 2026 increased 4% year-over-year and was up across all "
     "regions - particularly North America and EMEA - due to price appreciation and mix.",
     f"{LETTER} 2Q26"),
    ("2Q26", "latam", "adr_fx_statement",
     "ADR in Latin America increased 9% in Q2 2026 compared to Q2 2025, primarily driven by FX. "
     "On an ex-FX basis, ADR increased 2% compared to Q2 2025.", f"{LETTER} 2Q26"),
    ("2Q26", "total", "origin_country_acceleration",
     "Net origin nights booked in the U.S., France, the UK, and Australia all accelerated in Q2.",
     f"{LETTER} 2Q26"),
    ("FY2025", "total", "ntto_us_inbound_origin_mix",
     "NTTO: year-to-date market share for North America (Mexico and Canada) was 48.6% of US "
     "inbound arrivals and overseas 51.4% as of December 2025.",
     "National Travel and Tourism Office via the International Inbound Travel Association, "
     "December 2025 release, retrieved 2026-09-11"),
]
for q, reg, metric, quote, source in CORRIDOR_FACTS:
    add(q, reg, metric, np.nan, "qualitative / management statement", source, quote)

# ----------------------------------------------------------------- write out
df = pd.DataFrame(rows, columns=["quarter", "region", "metric", "value", "basis",
                                 "source", "quote"])


def sortkey(q):
    if q.startswith("FY"):
        return (int(q[2:]), 9)
    return (2000 + int(q[3:]), int(q[0]))


df["_k"] = df["quarter"].map(sortkey)
df = df.sort_values(["_k", "region", "metric"]).drop(columns="_k")
df.to_csv(OUT / "regional_target_panel.csv", index=False)

print(f"rows: {len(df)}")
print(df.groupby("metric").size().sort_values(ascending=False).to_string())
print("\nquarters:", df.quarter.nunique(), "regions:", sorted(df.region.unique()))
print("\nbasis counts:")
print(df.basis.value_counts().to_string())

