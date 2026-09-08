"""02b. Extend the ADR history back to 1Q19 and the ex-FX reconstruction back to 1Q20.

The repo's KPI panel (02_kpi_panel_quarterly.csv) starts at 3Q20, so reported ADR y/y
starts 3Q21 and the ex-FX gap looked like three quarters. It is not: the Q1 2021
shareholder letter's "Quarterly Summary" table prints nights, GBV and GBV per Night
(ADR) for every quarter from 1Q19, and the Q3 2022 letter carries 1Q21-3Q22 on the same
basis. That extends:

  ADR level      3Q20 -> 1Q19   (+6 quarters)
  ADR y/y        3Q21 -> 1Q20   (+6 quarters)
  ADR ex-FX      2Q22 -> 1Q20   (+9 quarters reconstructed, up from 3)

Source: data/raw/letters/1Q21_d476842dex991.htm, "Quarterly Summary" table.
Values are as printed (nights in millions, GBV in $bn, ADR in dollars).

The FX method is the one validated in 02_fx_backcast.py (GBV-weighted regional currency
basket x WS10 pass-throughs; r 0.988, raw RMSE 0.68pp, calibration slope 1.10 on the 17
disclosed quarters). The currency panel runs from 1Q18, so 1Q19 onward is covered
without any new data.

HEALTH WARNING, stated once and loudly: 2Q20 nights fell 67% and 2Q21 rose 197%. An
"ex-FX ADR" for those quarters is arithmetically constructible and economically close to
meaningless -- the ADR move is a collapse and rebound in geographic, urban/rural and
length-of-stay mix, not pricing. The series is provided because the history is worth
having; the 2020-21 quarters should not be used to calibrate anything.

Outputs
  data/processed/adr/02b_adr_history_extended.csv
"""

import os
import numpy as np
import pandas as pd

OUT = "data/processed/adr"

# --- Quarterly Summary, Q1 2021 shareholder letter ----------------------------
# quarter, nights_m, gbv_busd, adr_usd  (all as printed in the letter)
LETTER_1Q21 = [
    ("1Q19", 81.3, 10.0, 122.36), ("2Q19", 83.9, 9.8, 117.14),
    ("3Q19", 85.9, 9.7, 112.39), ("4Q19", 75.8, 8.5, 112.63),
    ("1Q20", 57.1, 6.8, 118.45), ("2Q20", 28.0, 3.2, 114.18),
    ("3Q20", 61.8, 8.0, 129.95), ("4Q20", 46.3, 5.9, 127.56),
    ("1Q21", 64.4, 10.3, 159.82),
]


def qkey(q):
    return (int(q[2:]) + 2000, int(q[0]))


def build():
    hist = pd.DataFrame(LETTER_1Q21, columns=["quarter", "nights_m", "gbv_busd", "adr_usd"])
    hist["source"] = "1Q21 letter, Quarterly Summary"

    # The repo panel from 3Q20 onward; letter values win where they overlap (same basis).
    kpi = pd.read_csv("data/processed/overnight/02_kpi_panel_quarterly.csv")
    kpi = kpi[["quarter", "nights_m", "gbv_busd", "adr_usd"]].copy()
    kpi["source"] = "02_kpi_panel_quarterly.csv (letters)"

    overlap = hist.merge(kpi, on="quarter", suffixes=("_letter", "_panel")).dropna(
        subset=["adr_usd_letter", "adr_usd_panel"])
    overlap["adr_diff"] = overlap.adr_usd_letter - overlap.adr_usd_panel

    df = pd.concat([hist, kpi[~kpi.quarter.isin(hist.quarter)]], ignore_index=True)
    df = df.sort_values("quarter", key=lambda s: s.map(qkey)).reset_index(drop=True)
    df["adr_yoy_reported_pct"] = df.adr_usd.pct_change(4) * 100

    # --- FX effect, same construction as 02 ------------------------------------
    b = pd.read_csv(f"{OUT}/02_fx_basket_quarterly.csv")
    piv = b.pivot(index="quarter", columns="region", values="basket_yoy_pct").reset_index()
    piv.columns.name = None
    passthrough = {"emea": 1.04, "latam": 0.62, "apac": 0.86, "na": 1.00}

    ann = pd.read_csv(f"{OUT}/01_regional_annual.csv")
    ann = ann[ann.region != "total"]
    shares = ann.pivot(index="year", columns="region", values="gbv_share_pct") / 100.0

    piv["y"] = [qkey(q)[0] + (qkey(q)[1] - 0.5) / 4 for q in piv.quarter]
    fx_pred = np.zeros(len(piv))
    for r in ["na", "emea", "latam", "apac"]:
        w = np.interp(piv.y, shares.index + 0.5, shares[r].values,
                      left=shares[r].iloc[0], right=shares[r].iloc[-1])
        fx_pred = fx_pred + w * passthrough[r] * piv[r].values
    piv["fx_pred_pp"] = fx_pred

    df = df.merge(piv[["quarter", "fx_pred_pp"]], on="quarter", how="left")

    # Calibration transferred from 02 (fitted on the 17 disclosed quarters only).
    bc = pd.read_csv(f"{OUT}/02_fx_backcast.csv")
    fit = bc.dropna(subset=["fx_pts_adr", "fx_pred_pp"])
    slope, intercept = np.polyfit(fit.fx_pred_pp, fit.fx_pts_adr, 1)
    df["fx_pts_adr_backcast"] = intercept + slope * df.fx_pred_pp

    disclosed = bc[["quarter", "fx_pts_adr", "adr_yoy_exfx_pct"]]
    df = df.merge(disclosed, on="quarter", how="left")
    df["fx_pts_adr_final"] = df.fx_pts_adr.fillna(df.fx_pts_adr_backcast)
    df["adr_yoy_exfx_final"] = df.adr_yoy_exfx_pct.fillna(
        df.adr_yoy_reported_pct - df.fx_pts_adr_final)
    df["basis"] = np.where(df.adr_yoy_exfx_pct.notna(), "disclosed (letter)",
                           np.where(df.adr_yoy_exfx_final.notna(),
                                    "reconstructed (basket, calibrated)", "n/a"))
    # 2020-21 quarters are flagged so nobody calibrates on them by accident.
    df["usable_for_calibration"] = ~df.quarter.isin(
        ["1Q20", "2Q20", "3Q20", "4Q20", "1Q21", "2Q21"])

    os.makedirs(OUT, exist_ok=True)
    df.to_csv(f"{OUT}/02b_adr_history_extended.csv", index=False)
    return df, overlap, (slope, intercept)


if __name__ == "__main__":
    df, overlap, calib = build()
    pd.set_option("display.width", 200)
    print("=== Letter vs repo panel on overlapping quarters (basis check) ===")
    print(overlap[["quarter", "adr_usd_letter", "adr_usd_panel", "adr_diff"]]
          .round(2).to_string(index=False))
    print(f"\ncalibration carried from 02: slope {calib[0]:.3f}, intercept {calib[1]:.3f}")
    print("\n=== Extended ADR history ===")
    show = df[df.adr_yoy_reported_pct.notna()][
        ["quarter", "adr_usd", "adr_yoy_reported_pct", "fx_pts_adr_final",
         "adr_yoy_exfx_final", "basis", "usable_for_calibration"]]
    print(show.round(2).to_string(index=False))
