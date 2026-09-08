"""06. Like-for-like PRICE, measured independently from external benchmarks.

WHY THIS FILE EXISTS
--------------------
In an ADR decomposition of the form

    ADR ex-FX growth = geographic mix + length-of-stay mix + unit-size mix + like-for-like price

the price term is normally the residual plug. That is the term the pitch quotes, and
making it the plug means every measurement error in the other three lands inside it.
This step refuses the plug: price is measured from outside sources, and whatever the
identity does not close is carried as a visible UNEXPLAINED line.

WHAT "LIKE-FOR-LIKE PRICE" MEANS HERE
-------------------------------------
The constant-currency change in the nightly price of a FIXED accommodation bundle:
same country, same length of stay, same unit size and capacity, same quality tier --
i.e. what the same listing charges for the same night this year versus last year.
It deliberately excludes everything that moves ADR through WHAT IS SOLD rather than
what it costs: country mix, urban/non-urban mix, stay-length mix, bedrooms and
capacity mix, quality-tier mix. Airbnb's own ADR is a value-weighted average of a
changing basket, so it is NOT a like-for-like price and cannot be used to measure one.

Because no external source publishes an Airbnb-specific matched-listing price index
(see REJECTED below), like-for-like price is measured as the price change of the
lodging category in which Airbnb's inventory sits, weighted to Airbnb's own footprint.

THE WEIGHT IS GBV SHARE, NOT NIGHTS SHARE
-----------------------------------------
North America is ~30% of Airbnb nights, which is the figure usually quoted. But the
contribution of a region's price change to GROUP ADR growth is

    d ADR / ADR = sum_r  (GBV share_r) * (d ADR_r / ADR_r)

not nights share, because NA ADR ($255 in 2025) is far above EMEA ($159) or LatAm
($95). NA GBV share is ~44%, not ~30%. Weighting the US benchmark at 30% would
understate it by ~14pp of weight. Both weights are carried in the output; GBV share
is used, nights share is reported for reference.

BENCHMARKS AND THEIR STATUS
---------------------------
USED, US leg -- "US matched-item lodging price":
  B1 CPI lodging away from home (BLS, CUSR0000SEHB). A matched-item, quality-adjusted
     price index: BLS reprices the same room in the same property. This is the only
     input that is like-for-like BY CONSTRUCTION. Availability lag ~13 days after
     month end. US only. Predominantly hotels/motels -- it is a hotel-side price.
  B2 BEA PCE hotels-and-motels price index. Lag ~30 days after month end. US only.
     Largely built from the same BLS source data, so it is NOT an independent second
     vote; the script measures corr(B1,B2) and averages them as one US vote rather
     than counting them twice.

USED, rest-of-world leg -- "global same-store constant-currency lodging":
  B3 Marriott worldwide comparable systemwide constant-dollar RevPAR y/y and Hilton
     system-wide comparable RevPAR y/y (currency neutral), averaged. Lag ~36 days
     after quarter end (median 1.5 days before ABNB's own print for MAR, 7.5 for HLT).
     This is the ONLY benchmark that matches Airbnb ADR ex-FX on both geography
     (worldwide) and currency (constant). Its defect is that RevPAR = ADR x occupancy,
     so it is not a pure price measure. Handled explicitly, not silently:
       - 2021, 2022 AND 2023 are marked NOT ESTIMABLE on this leg. Worldwide comparable
         RevPAR y/y ran +98% to +263% in 2021, +29% to +97% in 2022, and +6.5% to +32.2%
         in 2023. That is occupancy recovery, not rate. The 2023 exclusion is not fitted
         to the numbers: China lifted travel restrictions in January 2023, so every 2023
         quarter compares a reopened period against a still-closed APAC base. The first
         quarter in which both the current and the year-ago period are fully reopened
         worldwide is 1Q24, and that is where the ROW leg starts.
       - From 1Q24 the central case takes RevPAR at face value (occupancy adjustment
         = 0) and carries a band from the only measurable occupancy contributions in
         the data: FY2025 CoStar US (occ -1.2pp), Mar-2026 (+2.1pp), Jul-2026 (+2.5pp).
         So the band is [-1.2pp, +2.5pp] on the ROW leg, applied to (1 - w_gbv_na).
       - An alternative series using the US occupancy proxy where measurable is also
         written, so the reader can see the sign of the bias.

CORROBORATING ONLY (too sparse to build a series on, used to set confidence):
  B4 CoStar/STR US hotel ADR y/y. Same-store hotel ADR, no quality adjustment.
     Lag ~3 weeks. Present for FY2025, Mar-2026, Jul-2026 only.
  B5 AirDNA US short-term-rental ADR y/y. The only SAME-ASSET-CLASS benchmark --
     whole-home US STRs. Lag ~3-4 weeks. Present for Dec-2024, Dec-2025, Jun-2026 and
     Jul-2026 only, and it is an aggregate ADR so it carries STR mix, not like-for-like.

REJECTED, recorded not discarded:
  R1 Inside Airbnb like-for-like city prices. DEAD as a price signal. The overnight
     workstream-06 test put the correlation with ABNB ADR y/y at r = +0.03 on n = 8;
     this script independently re-tests the price-per-bedroom y/y and gets r = +0.32 on
     n = 5. Neither is anywhere near significant and the two disagree about the sign of
     a weak effect, which is itself the point: the panel rests on 1-7 cities per quarter
     and 4Q25 rests on ONE city, the price basis breaks in 2026 (listed_nightly ->
     quote_per_night), and Inside Airbnb stopped publishing listed prices after ~Sep
     2025. The correlation is recomputed here so the rejection is reproducible.
  R2 Airbnb's own 1-bedroom-vs-hotel comparison. Published in the 3Q23 and 4Q23 letters
     and one 2024 press citation, then discontinued. Three points, two sources, no
     methodology. Anecdote. Not used.
  R3 Quote-panel discount penetration (Mar-Aug 2026, 10.9% -> 31.4% of quotes
     discounted). There is NO year-ago comparison -- the quote block only exists from
     March 2026 -- and part of the rise is a schema change (share of quotes carrying a
     separate taxes line went 0.2% -> 6.5%). It cannot support any y/y claim. Level
     indicator only. Not used in the price series.

TRAPS HANDLED EXPLICITLY
------------------------
  T1 CPI lodging has NO October 2025 observation (the shutdown gap). The upstream
     quarterly file averages the monthly INDEX, so 4Q25 is a 2-month mean compared
     against a 3-month 2024 mean: it prints -1.59% where the month-matched y/y average
     is about -2.5%. This script rebuilds quarterly CPI as the mean of MONTHLY y/y over
     available months and carries cpi_n_months so the gap is visible. 4Q25 is demoted
     to medium confidence for it.
  T2 US benchmarks are US-only; Airbnb is global. Never applied at full weight -- see
     the GBV-weight section. The ROW leg is measured separately or declared not
     estimable.
  T3 RevPAR is not price. See B3.

OUTPUTS
-------
  data/processed/adr/06_measured_price_quarterly.csv          measured price + confidence
  data/processed/adr/06_price_benchmarks.csv                  every benchmark, source, lag, status
  data/processed/adr/06_price_residual_annual.csv             the unexplained line, by year
  data/processed/adr/06_price_benchmark_informativeness.csv   which benchmark tracks ABNB pricing

Run: py -3.13 analysis/src/adr/06_measured_price.py
"""

import os

import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")


def P(*a):
    return os.path.join(ROOT, *a)


OUT = P("data", "processed", "adr")

# Availability lag, per benchmark, measured from the end of the period it covers.
LAGS = {
    "cpi_lodging": "~13 days after month end (BLS CPI release)",
    "bea_hotels_price": "~30 days after month end (BEA Personal Income release); annual revision each September",
    "mar_hlt_revpar": "~36 days after quarter end (MAR median 1.5 days before ABNB's print, HLT 7.5 days before)",
    "str_us_hotel_adr": "~3 weeks after month end (CoStar via trade press)",
    "airdna_us_str_adr": "~3-4 weeks after month end (AirDNA U.S. Review)",
    "inside_airbnb": "1-2 months after the dump date, irregular; listed prices discontinued after ~Sep 2025",
    "abnb_1br_vs_hotel": "with the shareholder letter, ~5 weeks after quarter end; discontinued after 4Q23",
}

# Occupancy contribution to RevPAR: the only points in the data where a hotel ADR y/y
# and a RevPAR y/y are published for the same period, so the wedge is measurable.
OCC_WEDGE_POINTS = {
    "FY2025 CoStar US (ADR +0.9%, RevPAR -0.3%)": -1.2,
    "Mar-2026 CoStar US (ADR +3.8%, RevPAR +5.9%)": 2.1,
    "Jul-2026 CoStar US (ADR +5.7%, RevPAR +8.2%)": 2.5,
}
OCC_LO = min(OCC_WEDGE_POINTS.values())
OCC_HI = max(OCC_WEDGE_POINTS.values())

# First year in which worldwide comparable RevPAR is a usable price proxy. China lifted
# travel restrictions in Jan 2023, so every 2023 quarter still compares a reopened period
# against a closed APAC base. 1Q24 is the first quarter with both periods fully reopened.
ROW_FIRST_YEAR = 2024

CONF_ORDER = ["high", "medium", "low"]


def first_valid(s):
    return s.dropna().iloc[0] if s.notna().any() else np.nan


def load_monthly():
    """Monthly benchmark block, de-duplicated (STR and AirDNA rows are appended separately)."""
    m = pd.read_csv(P("data/processed/overnight/06_price_gap_monthly.csv"))
    text = {"month", "str_confidence", "str_source", "airdna_source", "source"}
    num = [c for c in m.columns if c not in text]
    for c in num:
        m[c] = pd.to_numeric(m[c], errors="coerce")
    m = (m.sort_values("month")
           .groupby("month", as_index=False)
           .agg({c: first_valid for c in num}))
    m["yq"] = pd.PeriodIndex(pd.to_datetime(m.month + "-01"), freq="Q").astype(str)
    return m


def quarterly_us_leg(m):
    """T1: month-matched y/y, averaged over AVAILABLE months, with the month count kept."""
    g = m.groupby("yq")
    out = pd.DataFrame({
        "cpi_lodging_yoy_pct": g.cpi_lodging_yoy_pct.mean(),
        "cpi_n_months": g.cpi_lodging_yoy_pct.count(),
        "bea_hotels_price_yoy_pct": g.bea_hotels_price_yoy_pct.mean(),
        "bea_n_months": g.bea_hotels_price_yoy_pct.count(),
        "str_us_hotel_adr_yoy_pct": g.str_us_hotel_adr_yoy_reported_pct.mean(),
        "str_us_hotel_revpar_yoy_pct": g.str_us_hotel_revpar_yoy_reported_pct.mean(),
        "airdna_us_str_adr_yoy_pct": g.airdna_us_str_adr_yoy_pct.mean(),
    }).reset_index()
    # The US matched-item vote. B1 and B2 share source data -- averaged as ONE vote.
    out["us_matched_item_price_yoy_pct"] = out[["cpi_lodging_yoy_pct",
                                                "bea_hotels_price_yoy_pct"]].mean(axis=1)
    out["us_leg_spread_pp"] = (out.cpi_lodging_yoy_pct - out.bea_hotels_price_yoy_pct).abs()
    # US occupancy wedge where both STR ADR and STR RevPAR exist in the quarter.
    out["occ_wedge_us_pp"] = out.str_us_hotel_revpar_yoy_pct - out.str_us_hotel_adr_yoy_pct
    return out


def gbv_and_nights_weights():
    """NA share of GBV (the correct weight) and of nights (the usually-quoted one)."""
    a = pd.read_csv(P("data/processed/adr/01_regional_annual.csv"))
    na = a[a.region == "na"][["year", "gbv_share_pct", "nights_share_pct"]].copy()
    na = na.rename(columns={"gbv_share_pct": "w_gbv_na_pct",
                            "nights_share_pct": "w_nights_na_pct"})
    # 2026 has no 10-K yet: carry 2025 forward and FLAG it, do not interpolate silently.
    last = na[na.year == na.year.max()].iloc[0]
    fwd = {"year": int(last.year) + 1, "w_gbv_na_pct": last.w_gbv_na_pct,
           "w_nights_na_pct": last.w_nights_na_pct}
    na = pd.concat([na, pd.DataFrame([fwd])], ignore_index=True)
    na["w_basis"] = np.where(na.year <= last.year, "10-K regional disclosure",
                             f"carried forward from {int(last.year)} (no 10-K yet)")
    return na


def informativeness(q):
    """Which benchmark actually tracks Airbnb's own pricing? Correlate, do not assert."""
    rows = []
    targets = {"adr_exfx_yoy_pct": "ABNB ADR ex-FX y/y", "adr_yoy_pct": "ABNB ADR reported y/y"}
    cands = [
        ("cpi_lodging_yoy_pct", "CPI lodging away from home (US)"),
        ("bea_hotels_price_yoy_pct", "BEA hotels-and-motels price (US)"),
        ("us_matched_item_price_yoy_pct", "US matched-item vote (CPI+BEA avg)"),
        ("global_revpar_yoy_pct", "MAR+HLT worldwide ccy-neutral RevPAR"),
        ("mar_revpar_yoy", "MAR worldwide comparable RevPAR"),
        ("hlt_revpar_yoy", "HLT system-wide comparable RevPAR"),
        ("price_for_residual_pp", "This study's measured price (GBV-weighted composite)"),
        ("ia_perbed_yoy_pct", "Inside Airbnb US price per bedroom y/y"),
    ]
    for tgt, tlab in targets.items():
        for col, lab in cands:
            if col not in q.columns:
                continue
            lagged = q[[tgt]].join(q[[col]].shift(1)).dropna()
            windows = [
                # The full sample is dominated by the 2021-22 reopening, where every lodging
                # series moves together for reasons that have nothing to do with pricing.
                ("full sample", q[[tgt, col]].dropna()),
                ("2023Q1+ (post-reopening)", q.loc[q.yq >= "2023Q1", [tgt, col]].dropna()),
                (f"{ROW_FIRST_YEAR}Q1+ (both legs measured)",
                 q.loc[q.yq >= f"{ROW_FIRST_YEAR}Q1", [tgt, col]].dropna()),
                # Does the benchmark LEAD Airbnb by a quarter? MAR and HLT print before ABNB,
                # so a lead would be tradeable, not just descriptive.
                ("2023Q1+, benchmark lagged 1Q", lagged[lagged.index.isin(
                    q.index[q.yq >= "2023Q1"])]),
            ]
            for lbl, dd in windows:
                if len(dd) < 4 or dd[col].nunique() < 3:
                    rows.append({"target": tlab, "benchmark": lab, "window": lbl, "n": len(dd),
                                 "pearson_r": np.nan, "p": np.nan, "spearman_r": np.nan})
                    continue
                r, p = stats.pearsonr(dd[tgt], dd[col])
                sr, _ = stats.spearmanr(dd[tgt], dd[col])
                rows.append({"target": tlab, "benchmark": lab, "window": lbl, "n": len(dd),
                             "pearson_r": round(float(r), 3), "p": round(float(p), 4),
                             "spearman_r": round(float(sr), 3)})
    out = pd.DataFrame(rows)
    # This is a battery of tests on ~14-20 overlapping quarters. At alpha 0.10 roughly one
    # test in ten clears on noise alone, so a raw p-value is not a finding here. Every
    # verdict is stated against the Bonferroni-adjusted p over the tests run per target.
    k = out.groupby("target").benchmark.transform("size")
    out["n_tests_for_target"] = k
    out["p_bonferroni"] = (out.p * k).clip(upper=1.0).round(3)
    out["verdict"] = np.where(
        out.p.isna(), "too few overlapping quarters",
        np.where(out.p_bonferroni < 0.10, "INFORMATIVE (survives multiple testing)",
                 np.where(out.p < 0.10,
                          "NOT informative -- raw p<0.10 but dies under multiple testing",
                          "NOT informative")))
    return out


def confidence(row):
    """Per-quarter flag with its reason. Rules are stated, not eyeballed."""
    year = int(row.yq[:4])
    if pd.isna(row.adr_exfx_yoy_pct):
        return "not estimable", ("no ABNB ADR ex-FX for this quarter (pre-3Q21; the letters do not "
                                 "disclose an ex-FX ADR before 3Q21)")
    if year <= 2021:
        return ("not estimable",
                "2021 reopening: MAR/HLT RevPAR y/y runs +98% to +263%, which is occupancy recovery "
                "not price, and CPI lodging y/y swings -11.7% to +23.1% off a collapsed 2020 base. "
                "Neither leg is a like-for-like price signal in this year.")
    if year == 2022:
        return ("low",
                "US leg usable but still carrying reopening base effects (CPI lodging +23.4% y/y in "
                "1Q22). ROW leg NOT estimable: MAR worldwide RevPAR +96.5% falling to +28.8% across "
                "the year is occupancy, not rate. Only the US leg is measured; the ROW share of ADR "
                "growth stays in the unexplained line.")
    if year < ROW_FIRST_YEAR:
        return ("low",
                "US leg measured and clean. ROW leg NOT estimable: China lifted travel restrictions "
                "in Jan 2023, so every 2023 quarter compares a reopened period against a closed APAC "
                "base -- MAR worldwide comparable RevPAR +34.3% in 1Q23 falling to +7.2% in 4Q23 is "
                "occupancy recovery, not rate. The ROW share of ADR growth stays in the unexplained "
                "line.")
    reasons = []
    if row.cpi_n_months < 3:
        reasons.append(f"CPI lodging has only {int(row.cpi_n_months)} of 3 months (Oct-2025 shutdown "
                       "gap), so the US leg is a 2-month month-matched y/y average")
    if pd.isna(row.mar_revpar_yoy) or pd.isna(row.hlt_revpar_yoy):
        reasons.append("only one of MAR/HLT reported a comparable RevPAR for this quarter")
    if row.us_leg_spread_pp > 1.5:
        reasons.append(f"CPI and BEA disagree by {row.us_leg_spread_pp:.1f}pp on the US leg")
    corrob = []
    if not pd.isna(row.str_us_hotel_adr_yoy_pct):
        corrob.append("CoStar US hotel ADR")
    if not pd.isna(row.airdna_us_str_adr_yoy_pct):
        corrob.append("AirDNA US STR ADR")
    if reasons:
        return "medium", "; ".join(reasons)
    if corrob:
        return "high", ("both legs complete and corroborated in-quarter by a same-store or "
                        "same-asset-class ADR benchmark (" + ", ".join(corrob) + ")")
    return ("medium", "both legs complete, but no same-store or same-asset-class ADR benchmark was "
                      "published in this quarter to corroborate the index-based US leg")


def build():
    m = load_monthly()
    us = quarterly_us_leg(m)

    g = pd.read_csv(P("data/processed/overnight/06_price_gap_series.csv"))
    keep = ["quarter", "yq", "gbv_musd", "nights_m", "adr", "adr_yoy_pct", "mar_revpar_yoy",
            "hlt_revpar_yoy", "ia_us_median_price_per_bedroom", "ia_us_cities", "ia_us_price_basis"]
    q = g[keep].copy()

    ex = pd.read_csv(P("data/processed/adr/02_adr_exfx_reconstructed.csv"))
    q = q.merge(ex[["quarter", "adr_yoy_exfx_final", "adr_exfx_basis"]], on="quarter", how="left")
    q = q.rename(columns={"adr_yoy_exfx_final": "adr_exfx_yoy_pct"})

    q = q.merge(us, on="yq", how="left")
    q["year"] = q.yq.str[:4].astype(int)
    q = q.merge(gbv_and_nights_weights(), on="year", how="left")
    q["w_gbv_na"] = q.w_gbv_na_pct / 100.0

    # --- ROW leg: global same-store, constant currency ------------------------------------
    q["global_revpar_yoy_pct"] = q[["mar_revpar_yoy", "hlt_revpar_yoy"]].mean(axis=1)
    q["row_leg_yoy_pct"] = np.where(q.year >= ROW_FIRST_YEAR, q.global_revpar_yoy_pct, np.nan)
    q["occ_adj_central_pp"] = 0.0                  # RevPAR at face value; band carried below
    q["occ_adj_us_proxy_pp"] = q.occ_wedge_us_pp   # only where CoStar publishes ADR and RevPAR

    # Inside Airbnb y/y, built only so the rejection is reproducible.
    q["ia_perbed_yoy_pct"] = q.ia_us_median_price_per_bedroom.pct_change(4) * 100

    # --- the measured price series ---------------------------------------------------------
    q["price_us_leg_contrib_pp"] = q.w_gbv_na * q.us_matched_item_price_yoy_pct
    q["price_row_leg_contrib_pp"] = (1 - q.w_gbv_na) * q.row_leg_yoy_pct
    q["price_measured_us_only_pp"] = q.price_us_leg_contrib_pp
    both = q.price_row_leg_contrib_pp.notna()
    # Central estimate: both legs where the ROW leg is estimable, US leg alone otherwise.
    # The basis is stated per quarter so a US-only number is never read as a global one.
    q["price_measured_pp"] = np.where(both,
                                      q.price_us_leg_contrib_pp + q.price_row_leg_contrib_pp,
                                      q.price_us_leg_contrib_pp)
    q["price_basis"] = np.where(
        both,
        "US matched-item leg (GBV-weighted) + worldwide same-store ccy-neutral ROW leg",
        "US matched-item leg ONLY -- ROW leg not estimable, ROW price left in the residual")

    row_w = 1 - q.w_gbv_na
    us_half = q.w_gbv_na * q.us_leg_spread_pp / 2
    # Band = CPI-vs-BEA disagreement on the US leg, plus the RevPAR occupancy wedge on the
    # ROW leg where that leg is used. The MISSING ROW price in US-only quarters is NOT folded
    # into the band: it is a one-sided unknown, not an error bar, and it stays in the residual.
    q["price_measured_lo_pp"] = np.where(both, q.price_measured_pp - row_w * OCC_HI - us_half,
                                         q.price_measured_pp - us_half)
    q["price_measured_hi_pp"] = np.where(both, q.price_measured_pp - row_w * OCC_LO + us_half,
                                         q.price_measured_pp + us_half)
    q["price_measured_occadj_pp"] = np.where(both, q.price_measured_pp - row_w * q.occ_adj_us_proxy_pp,
                                             np.nan)

    fl = q.apply(confidence, axis=1, result_type="expand")
    q["confidence"], q["confidence_reason"] = fl[0], fl[1]
    # Where the flag says not estimable, publish NO number rather than a fragile one.
    ne = q.confidence == "not estimable"
    q.loc[ne, ["price_measured_pp", "price_measured_us_only_pp", "price_measured_lo_pp",
               "price_measured_hi_pp", "price_measured_occadj_pp"]] = np.nan
    q.loc[ne, "price_basis"] = "NOT ESTIMABLE"

    # Quarterly residual. The quarterly geo/LOS/size terms do not exist (step 03 is annual),
    # so this line is labelled honestly: it holds ALL non-price ADR effects plus true error.
    q["price_for_residual_pp"] = q.price_measured_pp
    q["residual_vs_adr_exfx_pp"] = q.adr_exfx_yoy_pct - q.price_for_residual_pp
    q["residual_content"] = np.where(
        q.confidence == "low",
        "geo mix + LOS mix + size mix + ROW like-for-like price (UNMEASURED) + unexplained",
        "geo mix + LOS mix + size mix + unexplained")
    q.loc[ne, "residual_vs_adr_exfx_pp"] = np.nan
    q.loc[ne, "residual_content"] = ""

    inf = informativeness(q)

    # --- annual residual against the step-03 decomposition ----------------------------------
    d = pd.read_csv(P("data/processed/adr/03_annual_decomposition.csv"))
    w = q.dropna(subset=["price_for_residual_pp"]).copy()

    def gbv_wavg(frame, col):
        v = frame[col].fillna(frame.price_measured_us_only_pp)
        return float((v * frame.gbv_musd).sum() / frame.gbv_musd.sum())

    ann = []
    for year, grp in w.groupby("year"):
        ann.append({
            "year": year,
            "n_quarters_measured": len(grp),
            "quarters": ", ".join(grp.quarter),
            "price_measured_pp": gbv_wavg(grp, "price_for_residual_pp"),
            "price_measured_lo_pp": gbv_wavg(grp, "price_measured_lo_pp"),
            "price_measured_hi_pp": gbv_wavg(grp, "price_measured_hi_pp"),
            "worst_confidence": min(grp.confidence, key=CONF_ORDER.index),
        })
    # Left-join onto the decomposition so years with NO measurable price still appear,
    # flagged, instead of silently vanishing from the annual table.
    ann = d[["year", "adr_yoy_pct", "geo_mix_pp", "interaction_pp", "of_which_fx_pp",
             "of_which_los_pp", "of_which_size_and_price_pp"]].merge(
        pd.DataFrame(ann), on="year", how="left")
    ann["worst_confidence"] = ann.worst_confidence.fillna("not estimable")
    ann["n_quarters_measured"] = ann.n_quarters_measured.fillna(0).astype(int)
    ann["quarters"] = ann.quarters.fillna("")

    ann["residual_after_price_pp"] = ann.of_which_size_and_price_pp - ann.price_measured_pp
    ann["residual_lo_pp"] = ann.of_which_size_and_price_pp - ann.price_measured_hi_pp
    ann["residual_hi_pp"] = ann.of_which_size_and_price_pp - ann.price_measured_lo_pp
    ann["residual_content"] = np.where(
        ann.worst_confidence == "not estimable",
        "NOT ESTIMABLE -- no like-for-like price benchmark is usable in this year",
        np.where(ann.year < ROW_FIRST_YEAR,
                 f"unit-size mix + ROW like-for-like price (NOT MEASURABLE before {ROW_FIRST_YEAR}) "
                 "+ unexplained",
                 "unit-size mix + unexplained"))
    ann["share_of_adr_growth_unexplained_pct"] = 100 * ann.residual_after_price_pp / ann.adr_yoy_pct
    ann["share_of_size_and_price_explained_by_price_pct"] = (
        100 * ann.price_measured_pp / ann.of_which_size_and_price_pp)

    # How much of the residual could unit-size mix plausibly claim? This is NOT part of the
    # decomposition -- step 04 measures size mix properly. It exists only so the residual is
    # readable: the ONE quarter with a direct company size disclosure is 2Q26 (bedroom nights
    # +12% vs nights and seats +10%, i.e. bedrooms per night +1.8% y/y, off 1.786 bedrooms
    # per night). Priced through the 06_wtp_hedonic_coefs quote-basis coefficients
    # (bedrooms +0.1402 per bedroom holding capacity fixed; capacity elasticity +0.399),
    # and assuming capacity grows with bedrooms, that is worth roughly +1.2pp of ADR.
    # Applying a single 2026 quarter to earlier years is an EXTRAPOLATION, so this is a
    # ceiling for reading the residual, not a measurement.
    bed_growth = 0.018
    beds_per_night = 1.786
    size_bound = (0.1402 * beds_per_night * bed_growth + 0.399 * np.log1p(bed_growth)) * 100
    ann["size_mix_indicative_ceiling_pp"] = round(float(size_bound), 2)
    ann["size_mix_ceiling_basis"] = (
        "EXTRAPOLATION, not a measurement. 2Q26 is the only quarter with a direct company size "
        "disclosure (bedroom nights +12% vs nights +10% -> bedrooms per night +1.8% off 1.786). "
        "Priced with the 06_wtp_hedonic_coefs quote-basis coefficients (bedrooms +0.1402/bedroom "
        "at fixed capacity, capacity elasticity +0.399) assuming capacity grows with bedrooms. "
        "Step 04 measures unit-size mix properly; this column exists only to make the residual "
        "readable and must not be netted off it.")
    ann["residual_net_of_size_ceiling_pp"] = ann.residual_after_price_pp - size_bound

    # The identity must close: geo + interaction + FX + LOS + measured price + residual = ADR y/y.
    ann["check_identity_pp"] = (ann.geo_mix_pp + ann.interaction_pp + ann.of_which_fx_pp
                                + ann.of_which_los_pp + ann.price_measured_pp
                                + ann.residual_after_price_pp - ann.adr_yoy_pct)
    bad = ann.check_identity_pp.abs() > 1e-9
    if bad.any():
        raise AssertionError(f"decomposition identity does not close: "
                             f"{ann.loc[bad, ['year', 'check_identity_pp']].to_dict('records')}")

    # --- benchmark register -----------------------------------------------------------------
    reg = []

    def add(bm, col, geo, ccy, lfl, src, lag, status, note):
        d2 = q[["quarter", "yq", col]].rename(columns={col: "value_yoy_pct"}).copy()
        d2["benchmark"], d2["geography"], d2["currency_basis"] = bm, geo, ccy
        d2["like_for_like_basis"], d2["source"] = lfl, src
        d2["availability_lag"], d2["status"], d2["note"] = lag, status, note
        reg.append(d2)

    add("CPI lodging away from home", "cpi_lodging_yoy_pct", "US urban", "USD (domestic)",
        "matched item: BLS reprices the same room in the same property, quality adjusted",
        "BLS CUSR0000SEHB via FRED", LAGS["cpi_lodging"], "USED (US leg, averaged with BEA)",
        "no October 2025 observation (shutdown); the quarterly value here is the mean of AVAILABLE "
        "monthly y/y, not a mean of the index -- see cpi_n_months in the quarterly output")
    add("BEA PCE hotels-and-motels price index", "bea_hotels_price_yoy_pct", "US", "USD (domestic)",
        "chain price index for the accommodation category",
        "BEA PCE monthly detail (data/raw/bea/bea_pce_travel_monthly_2015_2026.csv)",
        LAGS["bea_hotels_price"], "USED (US leg, averaged with CPI)",
        "built largely from the same BLS source data as CPI lodging -- NOT an independent second "
        "vote; averaged with CPI into one US vote rather than counted twice")
    add("MAR+HLT worldwide comparable RevPAR (ccy neutral)", "global_revpar_yoy_pct", "worldwide",
        "constant currency", "same-store (comparable system-wide) but RevPAR = ADR x occupancy",
        "Marriott and Hilton quarterly releases via data/processed/predictive/02_peer_prints.csv",
        LAGS["mar_hlt_revpar"], f"USED (rest-of-world leg, {ROW_FIRST_YEAR} onward)",
        f"NOT ESTIMABLE before {ROW_FIRST_YEAR}: occupancy recovery dominates (worldwide comparable "
        "RevPAR y/y +98% to +263% in 2021, +29% to +97% in 2022, +6.5% to +32.2% in 2023 as APAC "
        f"reopened). From 1Q{ROW_FIRST_YEAR} taken at face value with an occupancy band of "
        f"[{OCC_LO:+.1f}pp, {OCC_HI:+.1f}pp] from the only measurable ADR-vs-RevPAR wedges in the data")
    add("CoStar/STR US hotel ADR", "str_us_hotel_adr_yoy_pct", "US", "USD (domestic)",
        "same-store hotel ADR, NOT quality adjusted", "CoStar via Business Travel News",
        LAGS["str_us_hotel_adr"], "CORROBORATING ONLY",
        "published for only 2 months inside the quarterly window plus FY2025; far too sparse to "
        "carry a quarterly leg, used only to set the confidence flag")
    add("AirDNA US short-term-rental ADR", "airdna_us_str_adr_yoy_pct", "US", "USD (domestic)",
        "aggregate STR ADR -- SAME ASSET CLASS as Airbnb but carries STR mix, not like-for-like",
        "AirDNA U.S. Review monthly", LAGS["airdna_us_str_adr"], "CORROBORATING ONLY",
        "3 monthly observations in the window (Dec-2025, Jun-2026, Jul-2026); conceptually the most "
        "relevant benchmark available and the one worth backfilling before the next step")
    add("Inside Airbnb US median price per bedroom", "ia_perbed_yoy_pct",
        "1-7 US/EU cities per quarter", "USD, unadjusted",
        "claimed like-for-like, in fact a shifting city panel",
        "Inside Airbnb quarterly dumps", LAGS["inside_airbnb"], "TESTED AND REJECTED",
        "see the REJECTION EVIDENCE row for this benchmark")

    reg = pd.concat(reg, ignore_index=True)
    reg = reg[reg.value_yoy_pct.notna()].copy()
    # Whether each individual observation actually enters the price series, so no reader
    # assumes a benchmark that is merely present in the file was also used.
    conf = q.set_index("quarter").confidence
    reg["reg_year"] = reg.yq.str[:4].astype(int)
    reg["used_in_price_series"] = np.where(
        reg.status.str.startswith("USED (US leg"),
        np.where(reg.quarter.map(conf) == "not estimable", "no -- quarter not estimable", "yes"),
        np.where(reg.status.str.startswith("USED (rest-of-world"),
                 np.where(reg.reg_year >= ROW_FIRST_YEAR, "yes",
                          f"no -- ROW leg not estimable before {ROW_FIRST_YEAR}"),
                 np.where(reg.status == "CORROBORATING ONLY",
                          "no -- sets the confidence flag only", "no -- rejected")))
    reg = reg.drop(columns=["reg_year"])

    # Rejection evidence rows, so the negative results travel with the file.
    ia = q[["adr_yoy_pct", "ia_perbed_yoy_pct"]].dropna()
    if len(ia) >= 4:
        ia_r, ia_p = stats.pearsonr(ia.adr_yoy_pct, ia.ia_perbed_yoy_pct)
    else:
        ia_r, ia_p = np.nan, np.nan
    cities = q.ia_us_cities.dropna()
    rej = pd.DataFrame([
        {"benchmark": "Inside Airbnb US median price per bedroom", "quarter": "REJECTION EVIDENCE",
         "yq": "", "value_yoy_pct": round(float(ia_r), 3) if len(ia) >= 4 else np.nan,
         "geography": "1-7 cities per quarter", "currency_basis": "USD, unadjusted",
         "like_for_like_basis": "FAILS", "source": "this script, reproducing the step-06 overnight test",
         "availability_lag": LAGS["inside_airbnb"], "status": "TESTED AND REJECTED",
         "note": f"Pearson r of Inside Airbnb price-per-bedroom y/y vs ABNB ADR y/y = {ia_r:+.3f} "
                 f"(p={ia_p:.2f}) on n={len(ia)}; the overnight workstream-06 test of the level "
                 "series got r=+0.03 on n=8. Neither is significant and they disagree on the sign "
                 "of a weak effect. City count per quarter ranges "
                 f"{int(cities.min())}-{int(cities.max())} (4Q25 rests on ONE city). The price basis "
                 "breaks in 2026 (listed_nightly -> quote_per_night) and Inside Airbnb stopped "
                 "publishing listed prices after ~Sep 2025. Not used in the price series."},
        {"benchmark": "Airbnb 1-bedroom vs hotel ADR (company published)",
         "quarter": "REJECTION EVIDENCE", "yq": "", "value_yoy_pct": np.nan, "geography": "US",
         "currency_basis": "USD, fee-inclusive ex tax", "like_for_like_basis": "1-bedroom listings only",
         "source": "ABNB 3Q23 and 4Q23 shareholder letters; Skift 22-May-2024 citing Airbnb and CoStar",
         "availability_lag": LAGS["abnb_1br_vs_hotel"], "status": "TESTED AND REJECTED",
         "note": "Three published points (Sep-2023 +1%, Dec-2023 -2%, Mar-2024 -2%), then "
                 "discontinued, with no methodology disclosed. Anecdote, not a series. Directionally "
                 "it says Airbnb 1BR prices were FLAT TO DOWN while hotel ADR rose 7-10% -- "
                 "consistent with this study's finding, but not evidence for it."},
        {"benchmark": "Quote-panel discount penetration", "quarter": "REJECTION EVIDENCE", "yq": "",
         "value_yoy_pct": np.nan, "geography": "13 cities", "currency_basis": "USD quote",
         "like_for_like_basis": "n/a -- level only",
         "source": "data/processed/overnight/06_quote_discount_panel.csv",
         "availability_lag": "same month as the dump", "status": "TESTED AND REJECTED (level indicator only)",
         "note": "Discounted share of quotes rises 10.9% (Mar-2026) to 31.4% (Aug-2026) in all 13 "
                 "cities. NO year-ago comparison exists -- the quote block starts Mar-2026 -- and part "
                 "of the rise is a schema change: the share of quotes carrying a separate taxes line "
                 "went 0.2% to 6.5% over the same months. It cannot support a y/y price claim."},
    ])
    rej["used_in_price_series"] = "no -- rejected"
    reg = pd.concat([reg, rej], ignore_index=True)
    reg = reg[["benchmark", "quarter", "yq", "value_yoy_pct", "geography", "currency_basis",
               "like_for_like_basis", "source", "availability_lag", "status",
               "used_in_price_series", "note"]]

    qcols = ["quarter", "yq", "adr", "adr_yoy_pct", "adr_exfx_yoy_pct", "adr_exfx_basis",
             "w_gbv_na_pct", "w_nights_na_pct", "w_basis",
             "cpi_lodging_yoy_pct", "cpi_n_months", "bea_hotels_price_yoy_pct", "us_leg_spread_pp",
             "us_matched_item_price_yoy_pct", "mar_revpar_yoy", "hlt_revpar_yoy",
             "global_revpar_yoy_pct", "row_leg_yoy_pct", "occ_adj_central_pp", "occ_adj_us_proxy_pp",
             "str_us_hotel_adr_yoy_pct", "airdna_us_str_adr_yoy_pct",
             "price_us_leg_contrib_pp", "price_row_leg_contrib_pp",
             "price_measured_pp", "price_measured_lo_pp", "price_measured_hi_pp",
             "price_measured_us_only_pp", "price_measured_occadj_pp", "price_basis",
             "confidence", "confidence_reason",
             "residual_vs_adr_exfx_pp", "residual_content"]
    qout = q[qcols].round(3)

    os.makedirs(OUT, exist_ok=True)
    qout.to_csv(os.path.join(OUT, "06_measured_price_quarterly.csv"), index=False)
    reg.round(3).to_csv(os.path.join(OUT, "06_price_benchmarks.csv"), index=False)
    ann.round(3).to_csv(os.path.join(OUT, "06_price_residual_annual.csv"), index=False)
    inf.to_csv(os.path.join(OUT, "06_price_benchmark_informativeness.csv"), index=False)
    return qout, reg, ann, inf, q


def report(qout, reg, ann, inf, q):
    pd.set_option("display.width", 260)
    line = "=" * 118
    print(line)
    print("MEASURED LIKE-FOR-LIKE PRICE, QUARTERLY (pp contribution to ADR growth, GBV-weighted)")
    print(line)
    print(qout[["quarter", "adr_exfx_yoy_pct", "w_gbv_na_pct", "us_matched_item_price_yoy_pct",
                "row_leg_yoy_pct", "price_measured_pp", "price_measured_lo_pp",
                "price_measured_hi_pp", "confidence", "residual_vs_adr_exfx_pp"]].to_string(index=False))
    print()
    print("Confidence counts:", qout.confidence.value_counts().to_dict())
    print()

    d = q[["cpi_lodging_yoy_pct", "bea_hotels_price_yoy_pct"]].dropna()
    r, p = stats.pearsonr(d.cpi_lodging_yoy_pct, d.bea_hotels_price_yoy_pct)
    print(f"CPI vs BEA independence check: r = {r:+.3f} (p={p:.1e}, n={len(d)}) "
          "-> NOT two votes, collapsed into one US vote.")
    print()
    print(line)
    print("ANNUAL: what measured price explains, and what it does NOT")
    print(line)
    print(ann[["year", "adr_yoy_pct", "geo_mix_pp", "of_which_fx_pp", "of_which_los_pp",
               "of_which_size_and_price_pp", "price_measured_pp", "price_measured_lo_pp",
               "price_measured_hi_pp", "residual_after_price_pp", "residual_lo_pp",
               "residual_hi_pp", "worst_confidence"]].round(2).to_string(index=False))
    print()
    print(ann[["year", "share_of_size_and_price_explained_by_price_pct",
               "share_of_adr_growth_unexplained_pct", "size_mix_indicative_ceiling_pp",
               "residual_net_of_size_ceiling_pp",
               "residual_content"]].round(1).to_string(index=False))
    print()
    print("size_mix_indicative_ceiling_pp is an EXTRAPOLATION from the single 2Q26 bedroom-nights")
    print("disclosure, not a measurement. Step 04 measures unit-size mix. It is shown only so the")
    print("residual is readable, and must NOT be netted off the decomposition.")
    print()
    print(line)
    print("WHICH BENCHMARK IS INFORMATIVE ABOUT ABNB'S OWN PRICING (target = ADR ex-FX y/y)")
    print(line)
    sub = inf[inf.target == "ABNB ADR ex-FX y/y"]
    print(sub[["benchmark", "window", "n", "pearson_r", "p", "p_bonferroni", "spearman_r",
               "verdict"]].to_string(index=False))
    print()
    print(f"{sub.n_tests_for_target.iloc[0]} tests were run against this target; verdicts are "
          "stated on the Bonferroni-adjusted p.")
    print()
    print("Benchmark register rows:", len(reg))
    for s, n in reg.status.value_counts().items():
        print(f"   {n:>3}  {s}")


if __name__ == "__main__":
    report(*build())
