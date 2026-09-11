"""
Workstream C, step 2. Monthly consumer strength panel by country, 2017 to Aug 2026.

Sources, all OECD SDMX (public, no key):
  DSD_KEI@DF_KEI       monthly: composite consumer confidence (CCICP), unemployment rate (UNEMP),
                       retail trade volume y/y (TOVM), share prices y/y (SHARE), CPI y/y (CP),
                       hourly earnings y/y (H_EARN)
  DSD_HHDASH@DF_HHDASH_INDIC  quarterly: household saving rate (B8GS1M_B6GA), real household
                       disposable income per capita (B6GS1M_R_POP), real household consumption
                       per capita (P3S1M_R_POP), plus CCICP for countries missing it in KEI

Raw pulls are cached under data/processed/overnight2/C/raw/ and reused if present, so the script
is reproducible offline. Delete the cache to re-pull.

Writes:
  data/processed/overnight2/C/consumer_panel_monthly.csv   long: country, date, indicator, value
  data/processed/overnight2/C/C2_coverage.csv              country x indicator coverage and gaps
  data/processed/overnight2/C/C2_source_gaps.csv           sources that blocked or had no data
"""
from __future__ import annotations

import gzip
import urllib.request
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parents[3] / "data/processed/overnight2/C"
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)

# Countries, grouped by the region Airbnb reports them in. Airbnb puts Mexico in Latin America
# (its letters discuss Mexico under the Latin America heading) and NA is the US and Canada.
REGION_OF = {
    "USA": "na", "CAN": "na",
    "MEX": "latam", "BRA": "latam", "ARG": "latam", "CHL": "latam", "COL": "latam", "CRI": "latam",
    "GBR": "emea", "DEU": "emea", "FRA": "emea", "ITA": "emea", "ESP": "emea", "NLD": "emea",
    "PRT": "emea", "IRL": "emea", "POL": "emea", "SWE": "emea", "CHE": "emea", "TUR": "emea",
    "ISR": "emea", "ZAF": "emea",
    "AUS": "apac", "JPN": "apac", "KOR": "apac", "IND": "apac", "CHN": "apac", "IDN": "apac",
    "NZL": "apac",
}
COUNTRIES = list(REGION_OF)

KEI_URL = (
    "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_KEI@DF_KEI,4.0/"
    + "+".join(COUNTRIES)
    + ".M.CCICP+UNEMP+TOVM+SHARE+CP+H_EARN.....?startPeriod=2016-01&format=csvfilewithlabels"
)
HH_URL = (
    "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_HHDASH@DF_HHDASH_INDIC,/all"
    "?startPeriod=2016-Q1&format=csvfilewithlabels"
)


def fetch(url: str, cache: Path) -> pd.DataFrame:
    """Pull once, cache gzipped so the raw SDMX response stays committable, then reuse."""
    if not cache.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "research/1.0"})
        with urllib.request.urlopen(req, timeout=300) as r:
            raw = r.read()
        with gzip.open(cache, "wb") as fh:
            fh.write(raw)
    return pd.read_csv(cache, low_memory=False, compression="gzip")


def month_index(s: pd.Series) -> pd.Series:
    return pd.PeriodIndex(s, freq="M").to_timestamp("M")


def build() -> tuple[pd.DataFrame, list[dict]]:
    gaps: list[dict] = []
    kei = fetch(KEI_URL, RAW / "oecd_kei_monthly.csv.gz")
    kei = kei[kei["FREQ"] == "M"].copy()

    frames = []

    def take(df, measure, unit=None, transf=None, activity=None, adjustment=None, name=None):
        m = df[df["MEASURE"] == measure]
        if unit is not None:
            m = m[m["UNIT_MEASURE"] == unit]
        if transf is not None:
            m = m[m["TRANSFORMATION"] == transf]
        if activity is not None:
            m = m[m["ACTIVITY"] == activity]
        if adjustment is not None:
            m = m[m["ADJUSTMENT"] == adjustment]
        m = m[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].dropna()
        m = m.rename(columns={"REF_AREA": "country", "OBS_VALUE": "value"})
        m["indicator"] = name
        m["date"] = month_index(m["TIME_PERIOD"])
        return m[["country", "date", "indicator", "value"]]

    frames.append(take(kei, "CCICP", unit="PB", adjustment="Y", name="cci"))
    frames.append(take(kei, "UNEMP", unit="PT_LF", name="unemp_rate"))
    frames.append(take(kei, "TOVM", unit="GR", transf="GY", activity="G47", name="retail_vol_yoy"))
    frames.append(take(kei, "SHARE", unit="GR", transf="GY", name="equity_yoy"))
    frames.append(take(kei, "CP", unit="GR", transf="GY", name="cpi_yoy"))
    frames.append(take(kei, "H_EARN", unit="GR", transf="GY", activity="C", name="hearn_yoy"))

    mon = pd.concat(frames, ignore_index=True)
    mon = mon[mon["country"].isin(COUNTRIES)]
    mon = mon.groupby(["country", "date", "indicator"], as_index=False)["value"].mean()

    # real wage = nominal hourly earnings y/y less CPI y/y
    w = mon.pivot_table(index=["country", "date"], columns="indicator", values="value")
    if "hearn_yoy" in w and "cpi_yoy" in w:
        rw = (w["hearn_yoy"] - w["cpi_yoy"]).dropna().rename("value").reset_index()
        rw["indicator"] = "real_wage_yoy"
        mon = pd.concat([mon, rw[["country", "date", "indicator", "value"]]], ignore_index=True)

    # ---- quarterly household dashboard
    try:
        hh = fetch(HH_URL, RAW / "oecd_hhdash_quarterly.csv.gz")
        hh = hh[hh["FREQ"] == "Q"].copy()
        hh = hh[hh["REF_AREA"].isin(COUNTRIES)]
        qmap = {"B8GS1M_B6GA": "saving_rate", "B6GS1M_R_POP": "real_hh_income_pc_ix",
                "P3S1M_R_POP": "real_hh_cons_pc_ix", "CCICP": "cci_hh"}
        h = hh[hh["MEASURE"].isin(qmap)][["REF_AREA", "MEASURE", "TIME_PERIOD", "OBS_VALUE"]].dropna()
        h = h.rename(columns={"REF_AREA": "country", "OBS_VALUE": "value"})
        h["indicator"] = h["MEASURE"].map(qmap)
        h = h.groupby(["country", "indicator", "TIME_PERIOD"], as_index=False)["value"].mean()
        # expand each quarter to its three months so the monthly panel stays rectangular
        rows = []
        for _, r in h.iterrows():
            p = pd.Period(r["TIME_PERIOD"].replace("-Q", "Q"), freq="Q")
            for m in pd.period_range(p.start_time, p.end_time, freq="M"):
                rows.append({"country": r["country"], "date": m.to_timestamp("M"),
                             "indicator": r["indicator"], "value": r["value"]})
        q = pd.DataFrame(rows)
        # y/y on the two index series
        for ind, new in [("real_hh_income_pc_ix", "real_hh_income_pc_yoy"),
                         ("real_hh_cons_pc_ix", "real_hh_cons_pc_yoy")]:
            sub = q[q["indicator"] == ind].pivot_table(index="date", columns="country", values="value")
            yoy = (sub / sub.shift(12) - 1.0) * 100.0
            yoy = yoy.reset_index().melt(id_vars="date", var_name="country", value_name="value").dropna()
            yoy["indicator"] = new
            q = pd.concat([q, yoy], ignore_index=True)
        mon = pd.concat([mon, q], ignore_index=True)
    except Exception as exc:  # pragma: no cover
        gaps.append({"source": "OECD DSD_HHDASH@DF_HHDASH_INDIC", "status": "failed", "detail": str(exc)[:200]})

    # fill the CCI gap (OECD KEI has no CCICP for CAN, CHE, IND, NZL, ZAF, ARG, CRI)
    piv = mon.pivot_table(index=["country", "date"], columns="indicator", values="value").reset_index()
    if "cci_hh" in piv:
        have = piv.groupby("country")["cci"].apply(lambda s: s.notna().sum()) if "cci" in piv else None
        missing = [c for c in COUNTRIES if have is None or have.get(c, 0) == 0]
        for c in missing:
            sel = (piv["country"] == c) & piv["cci_hh"].notna()
            piv.loc[sel, "cci"] = piv.loc[sel, "cci_hh"]
            if sel.sum():
                gaps.append({"source": f"CCI for {c}", "status": "filled from HHDASH CCICP",
                             "detail": f"{int(sel.sum())} monthly observations"})
            else:
                gaps.append({"source": f"CCI for {c}", "status": "no data", "detail": "absent from both OECD dataflows"})

    piv = piv.drop(columns=[c for c in ["cci_hh", "real_hh_income_pc_ix", "real_hh_cons_pc_ix"] if c in piv])
    out = piv.melt(id_vars=["country", "date"], var_name="indicator", value_name="value").dropna()
    out["region"] = out["country"].map(REGION_OF)
    out = out[out["date"] <= pd.Timestamp("2026-08-31")]
    out = out[out["date"] >= pd.Timestamp("2016-01-01")].sort_values(["country", "indicator", "date"])
    return out, gaps


if __name__ == "__main__":
    panel, gaps = build()
    panel.to_csv(OUT / "consumer_panel_monthly.csv", index=False)

    cov = (panel[panel["date"] >= "2018-01-01"]
           .groupby(["country", "indicator"])
           .agg(n=("value", "size"), first=("date", "min"), last=("date", "max"))
           .reset_index())
    cov["region"] = cov["country"].map(REGION_OF)
    cov.to_csv(OUT / "C2_coverage.csv", index=False)

    gaps.append({"source": "OECD DSD_PRICES@DF_PRICES_ALL (CPI by COICOP, travel price term)",
                 "status": "404 on the key tried", "detail": "not pursued further inside the time budget; US CPI lodging and airfare already sit in data/processed/overnight/05_macro_quarterly_panel.csv"})
    gaps.append({"source": "World Bank ST.INT.XPND.CD (international tourism expenditure, origin weights)",
                 "status": "returns null for 2021-2024", "detail": "too stale to weight 2026 origin nights; weights built in C3 instead"})
    pd.DataFrame(gaps).to_csv(OUT / "C2_source_gaps.csv", index=False)

    print("panel rows", len(panel))
    print(panel.groupby("indicator").size().to_string())
    print()
    print(cov.pivot_table(index="country", columns="indicator", values="n", fill_value=0).to_string())
    print()
    for g in gaps:
        print("GAP", g["source"], "|", g["status"])
