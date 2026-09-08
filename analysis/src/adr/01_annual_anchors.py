"""01. Annual regional anchors for the ADR decomposition.

Every figure here is transcribed from the "Geographic Mix" section of an Airbnb 10-K
(MD&A), downloaded to data/raw/filings/ and converted to text in data/raw/filings/txt/.
Nothing is derived from another repo file, which is the point: WS10's quarterly regional
nights shares were themselves built using a regional ADR index, so using them to measure
geographic mix would be circular. These 10-K tables are the independent anchor.

Sources, one 10-K per pair of years:
  FY2020 10-K (filed 2021-02-26)  2020 (narrative only, no table)
  FY2021 10-K (filed 2022-02-25)  2020, 2021
  FY2022 10-K (filed 2023-02-17)  2021, 2022
  FY2023 10-K (filed 2024-02-16)  2022, 2023
  FY2024 10-K (filed 2025-02-13)  2023, 2024
  FY2025 10-K (filed 2026-02-12)  2024, 2025

Outputs
  data/processed/adr/01_regional_annual.csv     nights, GBV, revenue, ADR, ALOS by region-year
  data/processed/adr/01_adr_disclosure_check.csv  computed vs company-stated ADR
"""

import os
import pandas as pd

OUT = "data/processed/adr"

# --- Regional nights / GBV / revenue, 10-K "Geographic Mix" tables -------------
# nights in millions, GBV and revenue in $m. Precision is as printed: 2020 and 2021
# are given to 0.1m nights, 2022 onward are rounded to whole millions, which is the
# dominant source of error in computed ADR for 2022+ (see 01_adr_disclosure_check).
ANNUAL = [
    # year, region, nights_m, gbv_musd, revenue_musd, nights_precision, source_10k
    (2020, "na",    75.5, 13169.9, 1772.7, 0.1, "FY2021"),
    (2020, "emea",  67.7,  6660.1, 1023.8, 0.1, "FY2021"),
    (2020, "latam", 22.4,  1700.8,  242.0, 0.1, "FY2021"),
    (2020, "apac",  27.6,  2366.1,  339.7, 0.1, "FY2021"),
    (2021, "na",   114.0, 25305.5, 3201.1, 0.1, "FY2021"),
    (2021, "emea", 118.1, 14606.9, 1930.8, 0.1, "FY2021"),
    (2021, "latam", 38.8,  3706.0,  431.2, 0.1, "FY2021"),
    (2021, "apac",  29.7,  3258.6,  428.7, 0.1, "FY2021"),
    (2022, "na",   133.0, 32246.0, 4210.0, 1.0, "FY2022"),
    (2022, "emea", 168.0, 21486.0, 2924.0, 1.0, "FY2022"),
    (2022, "latam", 53.0,  4838.0,  643.0, 1.0, "FY2022"),
    (2022, "apac",  40.0,  4642.0,  622.0, 1.0, "FY2022"),
    (2023, "na",   146.0, 34941.0, 4638.0, 1.0, "FY2023"),
    (2023, "emea", 187.0, 26241.0, 3615.0, 1.0, "FY2023"),
    (2023, "latam", 64.0,  6054.0,  824.0, 1.0, "FY2023"),
    (2023, "apac",  51.0,  6016.0,  840.0, 1.0, "FY2023"),
    (2024, "na",   154.0, 37816.0, 5006.0, 1.0, "FY2024"),
    (2024, "emea", 201.0, 29750.0, 4135.0, 1.0, "FY2024"),
    (2024, "latam", 76.0,  7092.0,  969.0, 1.0, "FY2024"),
    (2024, "apac",  61.0,  7126.0,  992.0, 1.0, "FY2024"),
    (2025, "na",   158.0, 40295.0, 5196.0, 1.0, "FY2025"),
    (2025, "emea", 215.0, 34162.0, 4729.0, 1.0, "FY2025"),
    (2025, "latam", 90.0,  8542.0, 1160.0, 1.0, "FY2025"),
    (2025, "apac",  70.0,  8274.0, 1156.0, 1.0, "FY2025"),
]

# --- Company-stated ADR ("GBV per Night and Experience Booked"), where given ----
# The company stops naming every region from FY2023; blanks below are genuinely absent
# from the filing, not omitted here.
STATED_ADR = {
    (2020, "na"): 174.43, (2020, "emea"): 98.41, (2020, "apac"): 85.83,
    (2020, "latam"): 75.74, (2020, "total"): 123.69,
    (2021, "na"): 221.92, (2021, "emea"): 123.71, (2021, "apac"): 109.75,
    (2021, "latam"): 95.42, (2021, "total"): 155.93,
    (2022, "na"): 240.29, (2022, "emea"): 127.99, (2022, "apac"): 117.41,
    (2022, "latam"): 92.89, (2022, "total"): 160.56,
    (2023, "emea"): 140.40,
}

# --- Average nights per booking, 10-K MD&A ("excluding experiences") -----------
# This is the LOS series. Global 2019 is not disclosed in the S-1 or any 10-K.
ALOS = [
    (2020, "na", 4.4), (2020, "emea", 4.4), (2020, "latam", 4.4), (2020, "apac", 2.8), (2020, "total", 4.1),
    (2021, "na", 4.3), (2021, "emea", 4.4), (2021, "latam", 4.3), (2021, "apac", 2.7), (2021, "total", 4.1),
    (2022, "na", 4.2), (2022, "emea", 4.2), (2022, "latam", 4.2), (2022, "apac", 3.2), (2022, "total", 4.1),
    (2023, "na", 4.1), (2023, "emea", 3.9), (2023, "latam", 3.9), (2023, "apac", 3.3), (2023, "total", 3.9),
    (2024, "na", 4.1), (2024, "emea", 3.8), (2024, "latam", 3.7), (2024, "apac", 3.3), (2024, "total", 3.8),
    (2025, "na", 4.1), (2025, "emea", 3.8), (2025, "latam", 3.6), (2025, "apac", 3.3), (2025, "total", 3.7),
]


def build():
    df = pd.DataFrame(
        ANNUAL,
        columns=["year", "region", "nights_m", "gbv_musd", "revenue_musd",
                 "nights_precision_m", "source_10k"],
    )

    # Totals as the sum of the four regions. The 10-K prints a total too; for 2022+
    # the printed total (e.g. 394) can differ from the sum of rounded regions, so we
    # carry both and let the check file show the gap.
    tot = df.groupby("year", as_index=False)[["nights_m", "gbv_musd", "revenue_musd"]].sum()
    tot["region"] = "total"
    tot["nights_precision_m"] = df.groupby("year")["nights_precision_m"].max().values
    tot["source_10k"] = "sum of regions"
    df = pd.concat([df, tot], ignore_index=True)

    df["adr_computed"] = df["gbv_musd"] / df["nights_m"]
    df["take_rate_pct"] = 100 * df["revenue_musd"] / df["gbv_musd"]
    df["adr_stated"] = [STATED_ADR.get((r.year, r.region)) for r in df.itertuples()]

    alos = pd.DataFrame(ALOS, columns=["year", "region", "alos_nights"])
    df = df.merge(alos, on=["year", "region"], how="left")

    # Implied bookings and GBV per booking: ADR x ALOS is the average booking value,
    # which is the object a length-of-stay discount actually applies to.
    df["gbv_per_booking"] = df["adr_computed"] * df["alos_nights"]
    df["bookings_m"] = df["nights_m"] / df["alos_nights"]

    df = df.sort_values(["year", "region"]).reset_index(drop=True)

    # Shares and growth, computed within region across years.
    df["nights_share_pct"] = 100 * df["nights_m"] / df.groupby("year")["nights_m"].transform(
        lambda s: s.iloc[-1] if False else df.loc[s.index[0], "nights_m"])
    # (recompute cleanly below; the line above is replaced)
    totals = df[df.region == "total"].set_index("year")
    df["nights_share_pct"] = df.apply(
        lambda r: 100 * r.nights_m / totals.loc[r.year, "nights_m"], axis=1)
    df["gbv_share_pct"] = df.apply(
        lambda r: 100 * r.gbv_musd / totals.loc[r.year, "gbv_musd"], axis=1)
    df["revenue_share_pct"] = df.apply(
        lambda r: 100 * r.revenue_musd / totals.loc[r.year, "revenue_musd"], axis=1)

    for c in ["nights_m", "gbv_musd", "adr_computed", "alos_nights"]:
        df[c + "_yoy_pct"] = df.groupby("region")[c].pct_change() * 100

    # Rounding error band on computed ADR: how much ADR moves if nights are at the
    # edge of their rounding interval. For 2022+ (whole millions) this is material.
    half = df["nights_precision_m"] / 2
    df["adr_round_err_pct"] = 100 * (
        df["gbv_musd"] / (df["nights_m"] - half) - df["gbv_musd"] / (df["nights_m"] + half)
    ) / df["adr_computed"] / 2

    os.makedirs(OUT, exist_ok=True)
    df.to_csv(f"{OUT}/01_regional_annual.csv", index=False)

    chk = df[df.adr_stated.notna()].copy()
    chk["diff_pct"] = 100 * (chk.adr_computed - chk.adr_stated) / chk.adr_stated
    chk = chk[["year", "region", "adr_computed", "adr_stated", "diff_pct",
               "adr_round_err_pct", "nights_precision_m", "source_10k"]]
    chk.to_csv(f"{OUT}/01_adr_disclosure_check.csv", index=False)

    return df, chk


if __name__ == "__main__":
    df, chk = build()
    pd.set_option("display.width", 200)
    print("=== Regional ADR, computed GBV/nights ===")
    piv = df.pivot(index="year", columns="region", values="adr_computed")
    print(piv[["na", "emea", "latam", "apac", "total"]].round(2).to_string())
    print("\n=== ADR y/y % ===")
    piv2 = df.pivot(index="year", columns="region", values="adr_computed_yoy_pct")
    print(piv2[["na", "emea", "latam", "apac", "total"]].round(1).to_string())
    print("\n=== Nights share of total, % ===")
    piv3 = df.pivot(index="year", columns="region", values="nights_share_pct")
    print(piv3[["na", "emea", "latam", "apac"]].round(1).to_string())
    print("\n=== Average nights per booking (LOS) ===")
    piv4 = df.pivot(index="year", columns="region", values="alos_nights")
    print(piv4[["na", "emea", "latam", "apac", "total"]].to_string())
    print("\n=== Computed vs company-stated ADR ===")
    print(chk.round(2).to_string(index=False))
