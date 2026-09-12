"""
Workstream C (reverse DCF run, 12-13 Sep 2026): one clean print panel, 23 prints 4Q20-2Q26.

Inputs (all data/processed/overnight unless stated):
  abnb_earnings_reactions.csv (data/processed)   raw and QQQ-excess close-to-close 1/5/20-session returns
  20_executable_returns.csv                        gap, executable next-open entry returns (QQQ-excess)
  12_abnb_print_decomposition.csv                  EV/NTM-revenue multiple change and estimate change per print (19 prints)
  02_kpi_panel_quarterly.csv                       nights y/y and nights_yoy_accel_pts
  16_consensus_at_print_merged.csv                 consensus at print (revenue, EPS, nights, EBITDA, next-Q revenue)
  02_guidance_ledger.csv                           revenue guide ranges (beat vs top), nights guide quotes
  04_reaction_panel.csv                            pre-print 20-day run-up, beat vs guide midpoint
  abnb_guidance_reaction_panel.csv (data/processed) FY guide action coding

Output: data/processed/reverse_dcf/C/C_print_panel.csv, C_guide_direction_coding.csv
Run: py -3.13 analysis/src/reverse_dcf/C_01_print_panel.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OV = ROOT / "data/processed/overnight"
PR = ROOT / "data/processed"
OUT = ROOT / "data/processed/reverse_dcf/C"
OUT.mkdir(parents=True, exist_ok=True)


def q_to_label(q):
    """'2020Q4' -> '4Q20'"""
    y, n = q.split("Q")
    return f"{n}Q{y[2:]}"


# ---------------------------------------------------------------------------
# Guide-direction coding: next-quarter nights guide vs the just-printed nights y/y rate.
# Coded by hand from the letters' Outlook sections (quotes verbatim, from the letter text or the
# verified ledger quote). guide_dir_code: +1 accelerating, 0 stable, -1 decelerating.
# guide_dir_pts: the guide-implied next-quarter nights growth minus the printed rate, in points.
#   directional language: "higher"/"modest sequential increase" = +2; "stable"/"approximate" = 0;
#   "moderate"/"lower"/"come down" = -2; "moderate slightly"/"nearly as strong"/"slightly decelerate" = -1.
#   bucket guides: bucket midpoint minus the printed rate (MEASURED).
#   1Q23: "lower than our revenue growth" -> revenue guide midpoint y/y (14%) minus printed 18.6 = -4.6.
# basis: 'yoy' where the letter speaks about the y/y growth rate; '2019' where the 2021-22 letters spoke
#   about levels vs 2019 (coded on a vs-2019 trajectory and flagged; these are excluded from the
#   ex-reopening sample anyway).
# ---------------------------------------------------------------------------
GUIDE_CODING = [
    # print, next_q, code, pts, basis, quote
    ("4Q20", "1Q21", np.nan, np.nan, "2019_level", "we anticipate that levels in Q1 2021 will be higher than those of Q1 2020, but lower than Q1 2019"),
    ("1Q21", "2Q21", 0, 0.0, "2019_level", "For Nights and Experiences Booked, we expect Q2 2021 will be significantly higher than the highly depressed levels of Q2 2020, but below that of Q2 2019."),
    ("2Q21", "3Q21", -1, -2.0, "2019_level", "we expect Nights and Experiences Booked to come down from Q2 and remain below Q3 2019 levels."),
    ("3Q21", "4Q21", 1, 2.0, "2019_level", "We expect Nights and Experiences Booked in Q4 2021 to significantly outperform Q4 2020 levels and approximate Q4 2019 levels."),
    ("4Q21", "1Q22", 1, 2.0, "2019_level", "we expect Q1 2022 Nights and Experiences Booked to significantly exceed Q1 2019 levels, which we believe will result in our strongest quarterly Nights and Experiences Booked on record."),
    ("1Q22", "2Q22", 0, 0.0, "2019_growth", "we anticipate that the Nights and Experiences Booked growth rate in Q2 2022 (compared to Q2 2019) will approximate the growth rate in Q1 2022 (compared to Q1 2019)."),
    ("2Q22", "3Q22", 0, 0.0, "yoy", "In Q3 2022, we expect Nights and Experienced Booked year-over-year growth to be stable with the year-over-year growth in Q2 2022."),
    ("3Q22", "4Q22", -1, -1.0, "yoy", "On a year-over-year basis, we expect Nights and Experiences Booked growth will moderate slightly relative to Q3 2022"),
    ("4Q22", "1Q23", -1, -1.0, "yoy", "In Q1 2023, we expect Nights and Experiences Booked year-over-year growth to be nearly as strong as Q4 2022."),
    ("1Q23", "2Q23", -1, -4.6, "yoy_vs_revenue_guide", "We expect year-over-year growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth during the quarter."),
    ("2Q23", "3Q23", 1, 2.0, "yoy", "We expect a modest sequential increase in the year-over-year growth rate of Nights and Experiences Booked from Q2 2023 to Q3 2023."),
    ("3Q23", "4Q23", -1, -2.0, "yoy", "We currently expect our nights booked growth in Q4 2023 to moderate relative to Q3 2023."),
    ("4Q23", "1Q24", -1, -2.0, "yoy", "we expect the growth rate of nights booked in Q1 2024 to moderate relative to Q4 2023."),
    ("1Q24", "2Q24", 0, 0.0, "yoy", "We expect the year-over-year growth rate of nights booked in Q2 2024 to be relatively stable to that of Q1 2024"),
    ("2Q24", "3Q24", -1, -2.0, "yoy", "During Q3 2024, we expect a sequential moderation in the year-over-year growth of Nights and Experiences Booked relative to Q2 2024."),
    ("3Q24", "4Q24", 1, 2.0, "yoy", "we expect year-over-year growth of Nights and Experienced Booked in Q4 2024 to be higher than Q3 2024."),
    ("4Q24", "1Q25", -1, -3.9, "yoy_vs_prior_year_quarter", "We expect year-over-year growth of Nights and Experiences Booked in Q1 2025 to be relatively stable compared to Q1 2024 after excluding Leap Day, which contributed to approximately one percentage point"),
    ("1Q25", "2Q25", -1, -2.0, "yoy", "In Q2 2025, we expect year-over-year growth of Nights and Experiences Booked to moderate relative to Q1 2025."),
    ("2Q25", "3Q25", 0, 0.0, "yoy", "In Q3 2025, we expect year-over-year growth of Nights and Seats Booked to be relatively stable compared to Q2 2025."),
    ("3Q25", "4Q25", -1, -3.8, "bucket", "In Q4 2025, we expect year-over-year growth of Nights and Seats Booked in the mid-single-digit range due to the challenging Q4 2024 comparison."),
    ("4Q25", "1Q26", -1, -1.8, "bucket", "We expect GBV to increase in the low teens year-over-year, driven by high-single-digit growth in Nights and Seats Booked and a moderate increase in ADR due to price appreciation and FX."),
    ("1Q26", "2Q26", -1, -1.0, "yoy", "In Q2 2026, we expect Nights and Seats booked growth to slightly decelerate, relative to Q1 2026, assuming an estimated roughly 100bps headwind related to the conflict in the Middle East."),
    ("2Q26", "3Q26", 1, 0.7, "bucket", "We expect year-over-year GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked and a moderate increase in ADR due to mix shift and price appreciation."),
]
CODING_NOTES = {
    "4Q24": "Letter compares 1Q25 growth with 1Q24 growth (9.5% incl. ~1pt leap day, so ~8.5%), not with the 4Q24 printed rate of 12.3%. Relative to the printed rate this is a ~4pt deceleration; a prior team coding (abnb_guidance_reaction_panel nq_nights_dir=0) read it as stable. The stock rose 14% on the day, so this print is the clearest case where the printed acceleration (+3.9pts, nights beat +2.1%) and the guide direction disagree.",
    "1Q23": "Revenue guide for 2Q23 was $2.35-2.45bn = +12 to +16% y/y, midpoint 14%; printed 1Q23 nights growth 18.6%. Guide-implied deceleration ~4.6pts.",
    "3Q25": "Bucket mid-single digits read as 4-6%, midpoint 5.0% vs printed 8.8% = -3.8pts. Outcome: 4Q25 printed 9.8% (above the bucket).",
    "4Q25": "Bucket high-single digits read as 7-9%, midpoint 8.0% vs printed 9.8% = -1.8pts. Outcome: 1Q26 printed 9.2% (above the bucket).",
    "2Q26": "Bucket low double digits read as 10-12%, midpoint 11.0% vs printed 10.3% = +0.7pts. The only accelerating guide since 3Q24 and the first bucket guide above the printed rate.",
    "1Q22": "Basis is growth vs 2019, not y/y; coded stable. Excluded from the ex-reopening sample.",
    "4Q20": "Level guide between 2020 and 2019; not codable as a direction. Excluded.",
    "1Q21": "Level guide; 1Q21 was also below 1Q19, so coded stable on the 2019 basis. Excluded from the ex-reopening sample.",
}


def main():
    # --- returns ---------------------------------------------------------------------------
    rx = pd.read_csv(PR / "abnb_earnings_reactions.csv")
    rx["print_quarter"] = rx["quarter"]
    ex = pd.read_csv(OV / "20_executable_returns.csv")
    panel = rx[["print_quarter", "reaction_date", "abnb_1d_pct", "excess_1d_pct", "abnb_5d_pct", "excess_5d_pct",
                "abnb_20d_pct", "excess_20d_pct"]].rename(columns={
        "abnb_1d_pct": "ret_1d_cc_raw_pct", "excess_1d_pct": "ret_1d_cc_excess_pct",
        "abnb_5d_pct": "ret_5d_cc_raw_pct", "excess_5d_pct": "ret_5d_cc_excess_pct",
        "abnb_20d_pct": "ret_20d_cc_raw_pct", "excess_20d_pct": "ret_20d_cc_excess_pct"})
    panel = panel.merge(ex[["print_quarter", "print_date", "pre_close", "entry_open_px", "gap_pct", "gap_excess_pct",
                            "open_1d_pct", "open_5d_pct", "open_20d_pct", "legacy_1d_pct", "legacy_5d_pct", "legacy_20d_pct"]].rename(columns={
        "open_1d_pct": "ret_1d_open_excess_pct", "open_5d_pct": "ret_5d_open_excess_pct",
        "open_20d_pct": "ret_20d_open_excess_pct"}), on="print_quarter", how="left")
    # Audit fix 10: the QQQ-excess close-to-close returns in abnb_earnings_reactions.csv are rounded to one decimal;
    # 20_executable_returns.csv legacy_*_pct is the same quantity at full precision (2Q23 is -0.036, not -0.0). Use it.
    panel["ret_1d_cc_excess_1dp_pct"] = panel["ret_1d_cc_excess_pct"]
    for h in ["1d", "5d", "20d"]:
        panel[f"ret_{h}_cc_excess_pct"] = panel[f"legacy_{h}_pct"].where(panel[f"legacy_{h}_pct"].notna(), panel[f"ret_{h}_cc_excess_pct"])
    panel = panel.drop(columns=["legacy_1d_pct", "legacy_5d_pct", "legacy_20d_pct"])
    # intraday (open to close) excess return = close-to-close excess minus the gap; descriptive
    panel["intraday_excess_pct"] = panel["ret_1d_cc_excess_pct"] - panel["gap_excess_pct"]
    panel["label"] = panel["print_quarter"].map(q_to_label)

    # --- multiple change on the print (WS12) -----------------------------------------------
    dec = pd.read_csv(OV / "12_abnb_print_decomposition.csv")
    dec = dec.rename(columns={"quarter": "label", "multiple_change_pct": "ev_ntm_rev_multiple_change_pct",
                              "estimate_change_pct": "ntm_rev_estimate_change_pct"})
    panel = panel.merge(dec[["label", "ev_ntm_rev_multiple_change_pct", "ntm_rev_estimate_change_pct", "ev_change_pct"]],
                        on="label", how="left")

    # --- KPIs: nights growth and acceleration -------------------------------------------------
    k = pd.read_csv(OV / "02_kpi_panel_quarterly.csv").rename(columns={"quarter": "label"})
    panel = panel.merge(k[["label", "nights_m", "nights_yoy_pct", "nights_yoy_accel_pts", "revenue_musd",
                           "revenue_yoy_reported_pct", "adj_ebitda_musd"]], on="label", how="left")
    # sign with a 0.25pt dead band (1Q22 is +0.01pt and is coded flat)
    panel["nights_accel_sign"] = np.where(panel["nights_yoy_accel_pts"] > 0.25, 1,
                                          np.where(panel["nights_yoy_accel_pts"] < -0.25, -1, 0)).astype(float)
    panel.loc[panel["nights_yoy_accel_pts"].isna(), "nights_accel_sign"] = np.nan

    # --- consensus at print (WS04/WS16 merged) -----------------------------------------------
    c = pd.read_csv(OV / "16_consensus_at_print_merged.csv")
    c["eps_surprise_pct_comparable"] = np.where(c["eps_comparable"] == 1, c["eps_surprise_pct"], np.nan)
    # EPS surprise in cents of pre-print price is more stable than % when the base is near zero
    panel = panel.merge(c[["print_quarter", "cons_revenue_musd", "cons_revenue_vendor", "revenue_surprise_pct",
                           "cons_eps_usd", "actual_eps_usd", "eps_surprise_pct_comparable", "cons_nights_m",
                           "nights_surprise_pct", "cons_adj_ebitda_musd", "ebitda_surprise_pct",
                           "next_q_cons_revenue_musd", "next_q_guide_mid_musd", "guide_vs_street_pct"]],
                        on="print_quarter", how="left")
    panel["eps_surprise_usd"] = panel["actual_eps_usd"] - panel["cons_eps_usd"]
    panel.loc[panel["eps_surprise_pct_comparable"].isna(), "eps_surprise_usd"] = np.nan
    panel["eps_surprise_bps_px"] = 1e4 * panel["eps_surprise_usd"] / panel["pre_close"]
    # Audit fix 9: 4Q21's +16.5% is an unattributed CNBC number flagged low-confidence in the source; it is 2.7x the next
    # largest value. The clipped column (+/-8) is used for the 'all' sample regressions; the primary sample is unaffected.
    panel["guide_vs_street_pct_clipped"] = panel["guide_vs_street_pct"].clip(-8, 8)
    panel["guide_below_street"] = np.where(panel["guide_vs_street_pct"].isna(), np.nan,
                                           (panel["guide_vs_street_pct"] < 0).astype(float))
    # 3Q21 guide vs Street is direction-only (Reuters: below) per WS04/WS20
    panel.loc[panel["print_quarter"] == "2021Q3", "guide_below_street"] = 1.0

    # --- revenue vs own guide (midpoint and top) ----------------------------------------------
    g = pd.read_csv(OV / "02_guidance_ledger.csv")
    rv = g[(g["metric"] == "revenue_usd_m") & (g["horizon_quarters"] == 1) & (g["guide_type"] == "range")]
    rv = rv[["target_period", "value_low", "value_high", "value_mid"]].rename(
        columns={"target_period": "label", "value_low": "guide_low_musd", "value_high": "guide_high_musd",
                 "value_mid": "guide_mid_musd"})
    panel = panel.merge(rv, on="label", how="left")
    panel["rev_beat_vs_guide_mid_pct"] = 100 * (panel["revenue_musd"] / panel["guide_mid_musd"] - 1)
    panel["rev_beat_vs_guide_top_pct"] = 100 * (panel["revenue_musd"] / panel["guide_high_musd"] - 1)

    # --- next-quarter nights guide direction (hand coded above) -----------------------------
    gd = pd.DataFrame(GUIDE_CODING, columns=["label", "next_quarter", "guide_dir_code", "guide_dir_pts", "guide_basis",
                                             "guide_quote"])
    gd["coding_note"] = gd["label"].map(CODING_NOTES).fillna("")
    gd["guide_dir"] = gd["guide_dir_code"].map({1: "accelerating", 0: "stable", -1: "decelerating"})
    panel = panel.merge(gd.drop(columns=["coding_note"]), on="label", how="left")

    # --- FY guide raised (existing team coding, checked against 02_fy_guide_revisions) ---------
    gp = pd.read_csv(PR / "abnb_guidance_reaction_panel.csv")
    gp["fy_raised"] = ((gp["fy_margin_action"] == "raised") | (gp["fy_rev_raised"] == 1)).astype(int)
    panel = panel.merge(gp[["print_quarter", "fy_raised", "fy_margin_action"]], on="print_quarter", how="left")

    # --- pre-print run-up ---------------------------------------------------------------------
    rp = pd.read_csv(OV / "04_reaction_panel.csv")
    panel = panel.merge(rp[["print_quarter", "pre_runup_20d_pct"]], on="print_quarter", how="left")

    # --- samples ------------------------------------------------------------------------------
    order = list(panel["print_quarter"])
    panel["idx"] = range(len(panel))
    panel["sample_all"] = True
    panel["sample_ex_reopening"] = panel["print_quarter"] >= "2022Q3"   # 16 prints, 3Q22-2Q26
    panel["sample_post2022"] = panel["print_quarter"] >= "2023Q1"       # 14 prints, 1Q23-2Q26

    # joint "momentum" score: printed acceleration sign plus guide direction (-2..+2)
    panel["momentum_score"] = panel["nights_accel_sign"] + panel["guide_dir_code"]

    cols = ["print_quarter", "label", "print_date", "reaction_date", "pre_close", "entry_open_px",
            "ret_1d_cc_raw_pct", "ret_1d_cc_excess_pct", "ret_1d_cc_excess_1dp_pct", "gap_pct", "gap_excess_pct", "intraday_excess_pct", "ret_1d_open_excess_pct",
            "ret_5d_cc_raw_pct", "ret_5d_cc_excess_pct", "ret_5d_open_excess_pct",
            "ret_20d_cc_raw_pct", "ret_20d_cc_excess_pct", "ret_20d_open_excess_pct",
            "ev_ntm_rev_multiple_change_pct", "ntm_rev_estimate_change_pct", "ev_change_pct",
            "nights_m", "nights_yoy_pct", "nights_yoy_accel_pts", "nights_accel_sign",
            "cons_nights_m", "nights_surprise_pct",
            "revenue_musd", "revenue_yoy_reported_pct", "cons_revenue_musd", "cons_revenue_vendor", "revenue_surprise_pct",
            "guide_low_musd", "guide_mid_musd", "guide_high_musd", "rev_beat_vs_guide_mid_pct", "rev_beat_vs_guide_top_pct",
            "cons_eps_usd", "actual_eps_usd", "eps_surprise_pct_comparable", "eps_surprise_usd", "eps_surprise_bps_px",
            "cons_adj_ebitda_musd", "adj_ebitda_musd", "ebitda_surprise_pct",
            "next_quarter", "guide_dir", "guide_dir_code", "guide_dir_pts", "guide_basis", "guide_quote",
            "next_q_guide_mid_musd", "next_q_cons_revenue_musd", "guide_vs_street_pct", "guide_vs_street_pct_clipped", "guide_below_street",
            "fy_raised", "fy_margin_action", "pre_runup_20d_pct", "momentum_score",
            "sample_all", "sample_ex_reopening", "sample_post2022"]
    panel = panel[cols]
    panel.to_csv(OUT / "C_print_panel.csv", index=False)

    # coding table with the realised outcome of the next quarter
    gd = gd.merge(panel[["label", "nights_yoy_pct", "ret_1d_cc_excess_pct", "ret_1d_cc_raw_pct"]], on="label", how="left")
    nxt = panel[["label", "nights_yoy_pct"]].rename(columns={"label": "next_quarter", "nights_yoy_pct": "next_q_nights_yoy_pct"})
    gd = gd.merge(nxt, on="next_quarter", how="left")
    gd["printed_rate_pct"] = gd["nights_yoy_pct"]
    gd["realised_change_pts"] = gd["next_q_nights_yoy_pct"] - gd["printed_rate_pct"]
    gd["realised_direction"] = np.where(gd["realised_change_pts"].isna(), "pending",
                               np.where(gd["realised_change_pts"] > 0.25, "accelerated",
                               np.where(gd["realised_change_pts"] < -0.25, "decelerated", "flat")))
    gd = gd[["label", "next_quarter", "guide_dir", "guide_dir_code", "guide_dir_pts", "guide_basis", "printed_rate_pct",
             "next_q_nights_yoy_pct", "realised_change_pts", "realised_direction", "ret_1d_cc_raw_pct",
             "ret_1d_cc_excess_pct", "guide_quote", "coding_note"]]
    gd.to_csv(OUT / "C_guide_direction_coding.csv", index=False)

    pd.set_option("display.width", 250)
    print(panel[["label", "ret_1d_cc_excess_pct", "ret_1d_open_excess_pct", "ev_ntm_rev_multiple_change_pct",
                 "nights_yoy_pct", "nights_yoy_accel_pts", "nights_accel_sign", "nights_surprise_pct",
                 "revenue_surprise_pct", "rev_beat_vs_guide_top_pct", "eps_surprise_pct_comparable", "guide_dir",
                 "guide_dir_pts", "guide_vs_street_pct", "fy_raised", "pre_runup_20d_pct"]].round(2).to_string())
    print(gd[["label", "guide_dir", "guide_dir_pts", "printed_rate_pct", "next_q_nights_yoy_pct", "realised_direction",
              "ret_1d_cc_excess_pct"]].to_string())
    print("coverage:", panel.notna().sum()[["nights_yoy_accel_pts", "guide_dir_code", "nights_surprise_pct",
                                            "revenue_surprise_pct", "eps_surprise_pct_comparable",
                                            "ev_ntm_rev_multiple_change_pct", "guide_vs_street_pct"]].to_dict())


if __name__ == "__main__":
    main()
