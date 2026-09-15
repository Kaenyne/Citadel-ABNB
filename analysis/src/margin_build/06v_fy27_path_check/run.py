"""WS06v: independent re-derivation of the FY27 quarterly revenue path (1Q27-4Q27) from the same inputs
WS06 was given, and a line-by-line comparison with WS06's 06_revenue_path_3q26_4q27.csv.

Built WITHOUT reading WS06's note or script first (prompt rule). Every number here is traceable to an
input file named in ASSUMPTIONS below. Consensus is read only for comparison columns, never as an input.

Run (repo venv):  python analysis/src/margin_build/06v_fy27_path_check/run.py
Exit code 0 on success. Outputs to data/processed/margin_build/06v_fy27_path_check/.

Construction (base):
  nights y/y (growth space, as PR #32)
      total(q) = WS10 FY27 total + NA delta + ex-NA fee/cancel lap + ex-NA RNPL lap(q) + scenario product term
      WS10 FY27 total 9.15 (10_regional_forecast TOTAL base); NA underlying 2027 2.31 (PR #32 choice model,
      nights_quarterly_na.csv); NA delta = (NA - WS10 NA 6.0) x 0.266; ex-NA bundle = (3.0 - 0.266 x 4.69)/(1-0.266)
      = 2.388 pts of ex-NA growth = 1.753 pts of total; fee/cancel legs 45% (WS-D pinned 40-50%) lapped from 4Q26,
      RNPL ex-NA 55% lapped 5.5/13 of 1Q27 (go-lives 18 Feb - 4 Mar 2026) and fully from 2Q27.
  ADR ex-FX (ADR v3 card terms carried; residual rule stated)
      residual: 4Q26 card 4.85 -> 1Q27 4.35 -> 2Q27+ 3.85 (management's ~1 pp bundle ADR contribution laps with the
      ex-NA RNPL anniversary, half in 1Q27); mix terms carried from P1_card_v3_terms (geo -1.43, party +0.80, LOS +0.06,
      interaction -0.10); seats 2027 from 15_seats_dilution_quarterly base (-0.565); K line 0.3745 carried 1Q-3Q27,
      0 in 4Q27 (y/y migrated share falls out of the y/y in 4Q27, K note).
  FX on ADR: ADR v3 midpoint estimator (mean of EUR fit and regional baskets, B4 construction) on 2027 quarter
      averages with spot held at the last FRED observation; +/-1sd = +/-5% parallel shift of the held spot (fx_lag_v2).
  GBV = prior-year GBV x (1+nights) x (1+reported ADR).
  Revenue = lambda_season x (2/3 GBV(q-1) + 1/3 GBV(q-2)), lambda = 2023-25 (Q3,Q4) / 2023-26 (Q1,Q2) means from the
      KPI panel (the B3 / bridge v3 kernel route). Same-quarter-take-rate route shown as a comparison column.
  Revenue FX points (output, never added): Phi(0, 2/3, 1/3) x 0.851 on the revenue-weighted basket (fx_lag_v2).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/margin_build/06v_fy27_path_check"
OUT.mkdir(parents=True, exist_ok=True)
WS06 = ROOT / "data/processed/margin_build/06_fy27_path_v2"

# ----------------------------------------------------------------------------------------------- inputs
KPI = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv").set_index("quarter")
BR_LINES = pd.read_csv(ROOT / "data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv")
BR_FX = pd.read_csv(ROOT / "data/processed/h2_bridge_v3/h2_bridge_fx.csv").set_index("quarter")
BR_FXLINE = pd.read_csv(ROOT / "data/processed/h2_bridge_v3/h2_bridge_v3_fx_line.csv")
BR_REV = pd.read_csv(ROOT / "data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv").set_index("quarter")
BR_CARD = pd.read_csv(ROOT / "data/processed/h2_bridge_v3/h2_bridge_v3_card_check.csv")
NA32 = pd.read_csv(ROOT / "data/processed/nights_quarterly_na.csv")
TOT32 = pd.read_csv(ROOT / "data/processed/nights_quarterly_total.csv")
WS10 = pd.read_csv(ROOT / "data/processed/overnight/10_regional_forecast.csv")
DGAP = pd.read_csv(ROOT / "data/processed/overnight2/D/D1_exna_4q26_gap.csv")
TERMS = pd.read_csv(ROOT / "data/processed/adrv3/P/P1_card_v3_terms.csv")
CARD = pd.read_csv(ROOT / "data/processed/adrv3/P/adr_card_v3.csv")
SEATS = pd.read_csv(ROOT / "data/processed/adr/15_seats_dilution_quarterly.csv")
FXD = pd.read_csv(ROOT / "data/processed/overnight2/B/B_fx_daily_usd_per_unit.csv", parse_dates=["date"]).set_index("date")
FXMETA = json.loads((ROOT / "data/processed/overnight2/B/B_fx_meta.json").read_text())
K23B = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/23b_fy27_annualisation_v2.csv")
K02 = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/02_basket_quarterly.csv").set_index("quarter")
K19 = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/19_baskets_spot_held_v2.csv").set_index("quarter")
K01B = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/01b_basket_weights_used.csv")
WS29 = pd.read_csv(ROOT / "data/processed/overnight/29_fy27_quarterly_path.csv")
B3 = pd.read_csv(ROOT / "data/processed/forecast_methods/l1_reconciliation_v2/fy27_kernel_band_v2.csv")
CONS = pd.read_csv(ROOT / "data/processed/margin_build/03_consensus_pit/03_current_consensus.csv")  # comparison only

ASSUMPTIONS: list[dict] = []


def A(name, value, unit, source, judgement):
    ASSUMPTIONS.append(dict(name=name, value=value, unit=unit, source=source, is_judgement=judgement))
    return value


Q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
Q26 = ["3Q26", "4Q26"]
PRIOR = {"1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26", "3Q26": "3Q25", "4Q26": "4Q25"}

# ------------------------------------------------------------------------------- 3Q26 / 4Q26 from bridge v3
def br_line(q, line):
    return float(BR_LINES[(BR_LINES.quarter == q) & (BR_LINES.line == line)].adopted.iloc[0])


def br_band(q, line):
    r = BR_LINES[(BR_LINES.quarter == q) & (BR_LINES.line == line)].iloc[0]
    return float(r.band_lo), float(r.band_hi)


def br_card(q, obj):
    return float(BR_CARD[(BR_CARD.quarter == q) & (BR_CARD.object == obj)].bridge.iloc[0])


B26 = {}
for q in Q26:
    B26[q] = dict(
        nights_yoy=br_line(q, "nights_yoy_pct"),
        nights_mm=br_card(q, "nights, mm"),
        adr_exfx=br_line(q, "adr_yoy_exfx_pct"),
        fx_adr=float(BR_FX.loc[q, "fx_pts_adr_adopted"]),
        adr_rep=br_card(q, "ADR reported y/y, %"),
        adr_usd=br_card(q, "ADR $"),
        gbv_busd=br_card(q, "GBV, $bn"),
        revenue=float(BR_REV.loc[q, "revenue_musd"]),
        fx_rev=float(BR_FXLINE[(BR_FXLINE.quarter == q) & (BR_FXLINE.line == "fx_pts_revenue")].adopted_pp.iloc[0]),
        lagged_gbv=float(BR_REV.loc[q, "lagged_gbv_busd"]),
        conv=float(BR_REV.loc[q, "conversion_mean"]),
    )
    A(f"bridge_v3_{q}_nights_yoy_pct", B26[q]["nights_yoy"], "%", "h2_bridge_v3_rebased_lines.csv", False)
    A(f"bridge_v3_{q}_adr_exfx_pct", B26[q]["adr_exfx"], "%", "h2_bridge_v3_rebased_lines.csv", False)
    A(f"bridge_v3_{q}_fx_adr_pp", B26[q]["fx_adr"], "pp", "h2_bridge_fx.csv fx_pts_adr_adopted (ADR v3 midpoint)", False)
    A(f"bridge_v3_{q}_revenue_musd", B26[q]["revenue"], "$M", "h2_bridge_revenue_dollars.csv (GBV-lag kernel route)", False)
    A(f"bridge_v3_{q}_fx_revenue_pp", B26[q]["fx_rev"], "pp", "h2_bridge_v3_fx_line.csv", False)

# ------------------------------------------------------------------------------- lambda (kernel conversion)
def lam_season(k, years):
    vals = []
    for y in years:
        q = f"{k}Q{y}"
        p1 = {1: f"4Q{y-1}", 2: f"1Q{y}", 3: f"2Q{y}", 4: f"3Q{y}"}[k]
        p2 = {1: f"3Q{y-1}", 2: f"4Q{y-1}", 3: f"1Q{y}", 4: f"2Q{y}"}[k]
        base = (2 / 3) * KPI.loc[p1, "gbv_busd"] * 1000 + (1 / 3) * KPI.loc[p2, "gbv_busd"] * 1000
        vals.append(KPI.loc[q, "revenue_musd"] / base)
    return float(np.mean(vals)), len(vals)


LAM = {1: lam_season(1, [23, 24, 25, 26]), 2: lam_season(2, [23, 24, 25, 26]),
       3: lam_season(3, [23, 24, 25]), 4: lam_season(4, [23, 24, 25])}
for k in LAM:
    A(f"lambda_Q{k}", round(LAM[k][0], 6), "revenue / lagged GBV",
      f"02_kpi_panel_quarterly.csv, mean over n={LAM[k][1]} (B3 convention: Q1,Q2 through 2026; Q3,Q4 2023-25)", False)
# check against bridge v3's conversion means
assert abs(LAM[3][0] - B26["3Q26"]["conv"]) < 1e-6, (LAM[3], B26["3Q26"]["conv"])
assert abs(LAM[4][0] - B26["4Q26"]["conv"]) < 1e-6, (LAM[4], B26["4Q26"]["conv"])

# ------------------------------------------------------------------------------- nights: the lap arithmetic
ws10_tot = {s: float(WS10[(WS10.period == "FY27") & (WS10.region == "TOTAL") & (WS10.scenario == s)].nights_yoy_pct.iloc[0])
            for s in ("bear", "base", "bull")}
ws10_na = float(WS10[(WS10.period == "FY27") & (WS10.region == "na") & (WS10.scenario == "base")].nights_yoy_pct.iloc[0])
na_share_27 = float(WS10[(WS10.period == "FY27") & (WS10.region == "na") & (WS10.scenario == "base")].nights_share_est_pct.iloc[0]) / 100
A("ws10_fy27_total_base_pct", ws10_tot["base"], "%", "10_regional_forecast.csv TOTAL FY27 base (share-weighted 9.55 - 0.41 calibration)", False)
A("ws10_fy27_total_bear_pct", ws10_tot["bear"], "%", "10_regional_forecast.csv (comparison only; demand axis not used in my scenarios)", False)
A("ws10_fy27_total_bull_pct", ws10_tot["bull"], "%", "10_regional_forecast.csv (comparison only)", False)
A("ws10_fy27_na_base_pct", ws10_na, "%", "10_regional_forecast.csv na FY27 base", False)
A("na_share_2027", na_share_27, "share", "10_regional_forecast.csv nights_share_est_pct na FY27", False)

na_under_27 = float(NA32[(NA32.quarter == "1Q27") & (NA32.scenario == "base")].underlying_pts.iloc[0])
na_under_26 = float(NA32[(NA32.quarter == "4Q26") & (NA32.scenario == "base")].underlying_pts.iloc[0])
rnpl_na = float(NA32[(NA32.quarter == "3Q26") & (NA32.scenario == "base")].product_pts.iloc[0])  # 2.29 = t1+cancel in 3Q26 window
# PR #32 fitted: RNPL = 3Q25 obs 5.0 - 2.6 = 2.40; t1_cancel = (1Q26 obs 8.0 - u2026) - 2.40
rnpl_fit = 5.0 - 2.6
t1c_fit = (8.0 - na_under_26) - rnpl_fit
peak_na = rnpl_fit + t1c_fit
assert abs(t1c_fit - rnpl_na) < 0.01, (t1c_fit, rnpl_na)
A("na_underlying_2027_pts", na_under_27, "pts", "nights_quarterly_na.csv underlying_pts 2027 (choice model, PR #32)", False)
A("na_underlying_2026_pts", na_under_26, "pts", "nights_quarterly_na.csv underlying_pts 2026", False)
A("na_product_peak_1h26_pts", round(peak_na, 2), "pts of NA nights", "PR #32 fit: RNPL 2.40 (3Q25) + t1/cancel 2.29 (1Q26 step)", False)
GLOBAL_PTS = A("mgmt_global_bundle_pts_1q26", 3.0, "pts of total nights", "1Q26 call (Mertz), via PR #32 GLOBAL_PRODUCT_PTS", False)
exna_bundle = (GLOBAL_PTS - na_share_27 * peak_na) / (1 - na_share_27)      # pts of ex-NA growth
exna_bundle_tot = exna_bundle * (1 - na_share_27)                            # pts of total nights
A("exna_bundle_pts_of_exna", round(exna_bundle, 3), "pts of ex-NA nights", "(3.0 - s x 4.69)/(1-s) at s=0.266 (PR #32 total_path)", False)
A("exna_bundle_pts_of_total", round(exna_bundle_tot, 3), "pts of total nights", "x (1-s); equals PR #32's -1.75 exna_lap", False)
FEE_SHARE = A("exna_fee_cancel_share_of_exna_bundle", 0.45, "share", "WS-D D1_exna_4q26_gap.csv: pinned 40-50% by the 4Q25 'over 200bp'; midpoint as N memo 2 / bridge v3", True)
exna_fee_lap = FEE_SHARE * exna_bundle_tot            # laps from 4Q26 (global Oct-Dec 2025 dates)
exna_rnpl_lap = (1 - FEE_SHARE) * exna_bundle_tot     # laps 1Q27 partial, 2Q27 full
# check the D table: 40% -> 0.70, 50% -> 0.88
d40 = float(DGAP[DGAP.scenario.str.startswith("ex-NA fee and cancellation legs are 40%")].pts_missing_from_4q26.iloc[0])
d50 = float(DGAP[DGAP.scenario.str.startswith("ex-NA fee and cancellation legs are 50%")].pts_missing_from_4q26.iloc[0])
assert abs(0.40 * exna_bundle_tot - d40) < 0.01 and abs(0.50 * exna_bundle_tot - d50) < 0.01, (0.4 * exna_bundle_tot, d40, d50)
Q1_FRAC = A("exna_rnpl_1q27_lap_fraction", round(5.5 / 13, 4), "share of quarter", "WS-D point 2: ex-NA go-lives in the last 5-6 of 13 weeks of 1Q26 (UK 18 Feb, AU/APAC 23 Feb, CA 4 Mar); midpoint 5.5/13", True)
T2_BEAR = A("bear_tranche2_nights_cost_pts", -1.0, "pts of total nights (1Q-3Q27)", "PR #32 bear (-1 NA at payout-neutral re-pricing, host_only_fee_history_and_elasticity -0.3 to -1.4%); applied GLOBALLY here because tranche 2 (13 Oct 2026) is global", True)
BULL_LEVER = A("bull_new_lever_share_of_old_bundle", 0.5, "share", "PR #32 bull: a new lever half the old bundle's size for FY27; applied to NA (2.35 NA pts) and ex-NA (1.19 ex-NA pts) here", True)

# re-derive the 4Q26 exit on the same decomposition (test asked for in WS06's RESUME)
ws10_4q26 = float(WS10[(WS10.period == "4Q26") & (WS10.region == "TOTAL") & (WS10.scenario == "base")].nights_yoy_pct.iloc[0])
ws10_4q26_na = float(WS10[(WS10.period == "4Q26") & (WS10.region == "na") & (WS10.scenario == "base")].nights_yoy_pct.iloc[0])
s4 = float(WS10[(WS10.period == "4Q26") & (WS10.region == "na") & (WS10.scenario == "base")].nights_share_est_pct.iloc[0]) / 100
pr32_4q26 = ws10_4q26 + (na_under_26 - ws10_4q26_na) * s4
exit_a = pr32_4q26 - FEE_SHARE * exna_bundle_tot                                          # D's sizing (s=0.266 bundle)
exit_b = pr32_4q26 - FEE_SHARE * ((GLOBAL_PTS - s4 * peak_na) / (1 - s4)) * (1 - s4)      # same, bundle at 4Q26 share 0.282
EXIT = pd.DataFrame([
    dict(variant="PR #32 base 4Q26 (NA lap only)", value_pct=round(pr32_4q26, 3), note="WS10 9.94 + (3.31-7.0) x 0.282"),
    dict(variant="minus ex-NA fee/cancel lap, WS-D sizing (bundle at s=0.266, 45%)", value_pct=round(exit_a, 3), note="= N memo 2 case B point; bridge v3 adopts 8.12 (131.8mm)"),
    dict(variant="minus ex-NA fee/cancel lap, bundle re-sized at the 4Q26 NA share 0.282", value_pct=round(exit_b, 3), note="alternative sizing; 0.03pp apart"),
    dict(variant="bridge v3 adopted", value_pct=B26["4Q26"]["nights_yoy"], note="h2_bridge_v3_rebased_lines.csv"),
])
EXIT.to_csv(OUT / "06v_4q26_exit_rederivation.csv", index=False)

NA_PROD = {"base": 0.0, "bear": 0.0, "bull": BULL_LEVER * peak_na}
EXNA_PROD = {"base": 0.0, "bear": 0.0, "bull": BULL_LEVER * exna_bundle}


def nights_yoy(q, scn):
    na = na_under_27 + NA_PROD[scn]
    na_delta = (na - ws10_na) * na_share_27
    rnpl = exna_rnpl_lap * (Q1_FRAC if q == "1Q27" else 1.0)
    tot = ws10_tot["base"] + na_delta - exna_fee_lap - rnpl + EXNA_PROD[scn] * (1 - na_share_27)
    if scn == "bear" and q in ("1Q27", "2Q27", "3Q27"):
        tot += T2_BEAR
    parts = dict(ws10_total=ws10_tot["base"], na_delta=na_delta, exna_fee_cancel_lap=-exna_fee_lap, exna_rnpl_lap=-rnpl,
                 scenario_product=EXNA_PROD[scn] * (1 - na_share_27) + (T2_BEAR if (scn == "bear" and q != "4Q27") else 0.0),
                 na_yoy=na)
    return tot, parts


# ------------------------------------------------------------------------------- ADR ex-FX terms
def term(q, name, variant="v3_with_K"):
    r = TERMS[(TERMS.quarter == q) & (TERMS.variant == variant) & (TERMS.term == name)]
    return float(r.point_pp.iloc[0])


geo = term("4Q26", "geographic_mix"); party = term("4Q26", "unit_size_party"); los = term("4Q26", "length_of_stay_mix")
inter = term("4Q26", "interaction"); k_line = term("4Q26", "fee_migration_mechanics_K"); resid_4q26 = term("4Q26", "like_for_like_pricing_residual")
seats26 = term("4Q26", "new_business_seats")
seats27 = float(SEATS[(SEATS.case_business == "base") & (SEATS.quarter == "1Q27")].dilution_drag_pp.iloc[0])
RESID_MEAN = A("residual_2023_25_mean_pp", 2.40, "pp", "ADR v3 synthesis section 3 / P1 terms lo band (2.398)", False)
BUNDLE_ADR = A("mgmt_bundle_adr_contribution_pp", 1.0, "pp of ADR", "ADR v3 synthesis: ~1pp of ADR from the bundle in 4Q25 and 1Q26 by the letters' GBV-minus-nights gap (D014, D032)", False)
A("adr_geo_mix_pp", geo, "pp", "P1_card_v3_terms.csv (3Q26 measured, carried)", False)
A("adr_party_pp", party, "pp", "P1_card_v3_terms.csv", False)
A("adr_los_pp", los, "pp", "P1_card_v3_terms.csv", False)
A("adr_interaction_pp", inter, "pp", "P1_card_v3_terms.csv", False)
A("adr_k_line_pp_1q_3q27", k_line, "pp", "P1_card_v3_terms.csv 4Q26 K line (0.3745) carried while the y/y migrated share is still rising; 0 in 4Q27 (K: falls out of the y/y in 4Q27)", True)
A("adr_seats_2027_pp", seats27, "pp", "15_seats_dilution_quarterly.csv base 2027 (-0.565 vs -0.483 in 2026)", False)
A("adr_residual_rule_base", "4.85 -> 4.35 (1Q27) -> 3.85 (2Q27+)", "pp", "judgement: the ~1pp bundle ADR contribution laps with the ex-NA RNPL anniversary (half 1Q27, full 2Q27); rest of the residual persists (v3 last_q)", True)
A("adr_residual_rule_bear", "linear 4.85 -> 2.40 over 1Q27-4Q27", "pp", "ADR v3 synthesis section 4 point 2: carry mean reversion as the downside", True)
A("adr_residual_rule_bull", "4.85 held", "pp", "v3 last_q persistence", True)


def residual(q, scn):
    i = Q27.index(q)
    if scn == "base":
        return resid_4q26 - BUNDLE_ADR * (0.5 if q == "1Q27" else 1.0)
    if scn == "bear":
        return resid_4q26 + (RESID_MEAN - resid_4q26) * (i + 1) / 4
    return resid_4q26


def adr_exfx(q, scn):
    k = k_line if q != "4Q27" else 0.0
    return residual(q, scn) + geo + party + los + seats27 + inter + k


# ------------------------------------------------------------------------------- FX on ADR, 2027, spot held
LAST = pd.Timestamp(FXMETA["latest_fred_fx_observation"])
ADR_FX_EUR = (-0.5687, 0.4512)
DEST_BASKET = {"na": {"USD": 0.90, "CAD": 0.08, "MXN": 0.02}, "emea": {"EUR": 0.70, "GBP": 0.25, "USD": 0.05},
               "latam": {"BRL": 0.55, "MXN": 0.38, "USD": 0.07}, "apac": {"AUD": 0.55, "JPY": 0.20, "KRW": 0.10, "INR": 0.07, "USD": 0.08}}
GBV_SHARE_2025 = {"na": 0.4415, "emea": 0.3743, "latam": 0.0936, "apac": 0.0907}
PASSTHROUGH = {"na": 1.00, "emea": 1.04, "latam": 0.62, "apac": 0.86}
A("adr_fx_eur_fit", str(ADR_FX_EUR), "intercept, slope on EUR/USD y/y", "B4_application_3q26_4q26.py (05_fx_fits ex21 n17)", False)
A("adr_fx_baskets", "GBV-share x pass-through x destination-basket y/y", "", "B4_application_3q26_4q26.py DEST_BASKET / PASSTHROUGH / GBV_SHARE_2025", False)
A("fx_spot_held_from", str(LAST.date()), "date", "B_fx_meta.json latest_fred_fx_observation", False)
ccy = [c for c in FXD.columns if c != "USD"]


def qavg(s, e, shift=1.0):
    s, e = pd.Timestamp(s), pd.Timestamp(e)
    obs = FXD.loc[s:min(e, LAST), ccy]
    days = pd.date_range(max(LAST + pd.Timedelta(days=1), s), e, freq="B")
    if len(days):
        spot = FXD.loc[LAST, ccy] * shift
        obs = pd.concat([obs, pd.DataFrame([spot] * len(days), index=days)])
    return obs.mean()


QB = {"1Q25": ("2025-01-01", "2025-03-31"), "2Q25": ("2025-04-01", "2025-06-30"), "3Q25": ("2025-07-01", "2025-09-30"), "4Q25": ("2025-10-01", "2025-12-31"),
      "1Q26": ("2026-01-01", "2026-03-31"), "2Q26": ("2026-04-01", "2026-06-30"), "3Q26": ("2026-07-01", "2026-09-30"), "4Q26": ("2026-10-01", "2026-12-31"),
      "1Q27": ("2027-01-01", "2027-03-31"), "2Q27": ("2027-04-01", "2027-06-30"), "3Q27": ("2027-07-01", "2027-09-30"), "4Q27": ("2027-10-01", "2027-12-31")}


def basket_yoy(cur, prv, w):
    num = sum(x * np.log(cur[c] if c != "USD" else 1.0) for c, x in w.items())
    den = sum(x * np.log(prv[c] if c != "USD" else 1.0) for c, x in w.items())
    return 100 * (np.exp(num - den) - 1)


def adr_fx_estimators(q, shift_2027=1.0):
    """Midpoint ADR-FX for quarter q; shift applies to 2027 held spot only (2026 base quarters stay as bridge v3)."""
    cur = qavg(*QB[q], shift=shift_2027 if q.endswith("27") else 1.0)
    prv = qavg(*QB[PRIOR[q]])
    eur = 100 * (cur["EUR"] / prv["EUR"] - 1)
    e_eur = ADR_FX_EUR[0] + ADR_FX_EUR[1] * eur
    tot = sum(GBV_SHARE_2025[r] / sum(GBV_SHARE_2025.values()) * PASSTHROUGH[r] * basket_yoy(cur, prv, DEST_BASKET[r]) for r in DEST_BASKET)
    return dict(eur_yoy=eur, eur_fit=e_eur, baskets=tot, midpoint=(e_eur + tot) / 2)


fxchk = {q: adr_fx_estimators(q) for q in Q26 + Q27}
# reproduce bridge v3 / N1 for 3Q26 and 4Q26 (to 0.02 pp; N1 rounds each estimator to 2dp)
for q in Q26:
    assert abs(fxchk[q]["midpoint"] - B26[q]["fx_adr"]) < 0.03, (q, fxchk[q], B26[q]["fx_adr"])
FX_ADR = {"spot_held": {q: fxchk[q]["midpoint"] for q in Q27},
          "usd_weak_+1sd": {q: adr_fx_estimators(q, 1.05)["midpoint"] for q in Q27},
          "usd_strong_-1sd": {q: adr_fx_estimators(q, 0.95)["midpoint"] for q in Q27}}
pd.DataFrame([dict(quarter=q, **fxchk[q], usd_weak_midpoint=FX_ADR["usd_weak_+1sd"].get(q, np.nan),
                   usd_strong_midpoint=FX_ADR["usd_strong_-1sd"].get(q, np.nan)) for q in Q26 + Q27]).to_csv(OUT / "06v_fx_adr_estimators.csv", index=False)

# revenue FX (output): Phi(0, 2/3, 1/3) x 0.851 on the kernel's revenue-weighted basket; 2027 basket at held spot
W = K01B.groupby("region").apply(lambda d: {r.ccy_used: r.weight for r in d.itertuples()}, include_groups=False).to_dict()
REGW = {r: float(K02.loc["2Q26", f"w_{r}"]) for r in ("na", "emea", "latam", "apac")}


def kernel_basket(q, shift=1.0):
    cur = qavg(*QB[q], shift=shift if q.endswith("27") else 1.0)
    prv = qavg(*QB[PRIOR[q]])
    out = 0.0
    for r, w in W.items():
        ww = {}
        for c, x in w.items():
            ww[c] = ww.get(c, 0.0) + x
        out += REGW[r] * basket_yoy(cur, prv, ww)
    return out


BK = {p: {q: kernel_basket(q, s) for q in Q26 + Q27} for p, s in [("spot_held", 1.0), ("usd_weak_+1sd", 1.05), ("usd_strong_-1sd", 0.95)]}
BK_HIST = {"1Q26": float(K02.loc["1Q26", "basket_global_rev_wtd_yoy_pct"]), "2Q26": float(K02.loc["2Q26", "basket_global_rev_wtd_yoy_pct"])}
PHI_SCALE = A("rev_fx_phi_scale", 0.851, "", "fx_lag_v2 Phi (0, 2/3, 1/3) x 0.851 (B4 adopted reading C)", False)
PREVQ = {"3Q26": ("2Q26", "1Q26"), "4Q26": ("3Q26", "2Q26"), "1Q27": ("4Q26", "3Q26"), "2Q27": ("1Q27", "4Q26"), "3Q27": ("2Q27", "1Q27"), "4Q27": ("3Q27", "2Q27")}


def rev_fx(q, path):
    b = lambda x: BK_HIST[x] if x in BK_HIST else BK[path][x]
    p1, p2 = PREVQ[q]
    return PHI_SCALE * ((2 / 3) * b(p1) + (1 / 3) * b(p2))


# reconcile my basket reconstruction to the kernel's 19_baskets_spot_held_v2 (3Q26, 4Q26) and 23b (2027 spot held)
k19 = {q: float(K19.loc[q, "global_pct"]) for q in Q26}
k23 = K23B[(K23B.path == "spot_held") & (K23B.spec == "phi_scale_0.851")].iloc[0]
FXREC = pd.DataFrame([dict(quarter=q, my_basket_yoy=round(BK["spot_held"][q], 3), kernel_basket_yoy=k19.get(q, np.nan),
                           my_rev_fx_pp=round(rev_fx(q, "spot_held"), 3),
                           kernel_rev_fx_pp=(B26[q]["fx_rev"] if q in Q26 else float(k23[f"q{Q27.index(q)+1}_pp"])))
                      for q in Q26 + Q27])
FXREC.to_csv(OUT / "06v_fx_revenue_reconciliation.csv", index=False)
# The B4 destination-basket reconstruction does NOT reproduce the kernel's revenue-weighted basket (3Q26 0.28 vs 0.60;
# 4Q26 0.76 vs 1.35): the kernel uses its own PIT reconstruction and weights. The revenue-FX line is therefore READ from the
# kernel's own 23b table (spot held and the +/-1sd paths), which is the sanctioned input; my reconstruction stays as a check only.
REV_FX_KERNEL = {}
for path in ("spot_held", "usd_weak_+1sd", "usd_strong_-1sd"):
    r = K23B[(K23B.path == path) & (K23B.spec == "phi_scale_0.851")].iloc[0]
    REV_FX_KERNEL[path] = {q: float(r[f"q{i+1}_pp"]) for i, q in enumerate(Q27)}
A("rev_fx_2027_source", "fx_lag_v2/23b_fy27_annualisation_v2.csv, spec phi_scale_0.851, rows spot_held / usd_weak_+1sd / usd_strong_-1sd",
  "pp by quarter", "kernel output read directly (0.93/0.62/0.31/0.38 spot held); never added to revenue", False)

# ------------------------------------------------------------------------------- build the path
GBV_HIST = {q: float(KPI.loc[q, "gbv_busd"]) * 1000 for q in ["1Q26", "2Q26", "3Q25", "4Q25"]}
ADR_HIST = {q: float(KPI.loc[q, "adr_usd"]) for q in ["1Q26", "2Q26", "3Q25", "4Q25"]}
N_HIST = {q: float(KPI.loc[q, "nights_m"]) for q in ["1Q26", "2Q26", "3Q25", "4Q25"]}
REV_HIST = {q: float(KPI.loc[q, "revenue_musd"]) for q in ["1Q26", "2Q26", "3Q25", "4Q25"]}
TR_HIST = {q: float(KPI.loc[q, "take_rate_pct"]) for q in ["1Q26", "2Q26", "3Q25", "4Q25"]}

SCN = {"base": ("base", "base", "spot_held"), "bear": ("bear", "bear", "spot_held"), "bull": ("bull", "bull", "spot_held"),
       "base_fx_usd_strong": ("base", "base", "usd_strong_-1sd"), "base_fx_usd_weak": ("base", "base", "usd_weak_+1sd"),
       # sensitivity asked for in WS06's RESUME: if WS10's FY27 regional rates already embed the ex-NA product lap, the 2027
       # ex-NA lap is a double count and 2027 nights are WS10 + NA delta only (PR #32's NA-only case, 8.17)
       "base_no_exna_lap_2027": ("no_exna_lap", "base", "spot_held")}
NA_PROD["no_exna_lap"] = 0.0
EXNA_PROD["no_exna_lap"] = 0.0


def nights_yoy_wrapped(q, scn):
    if scn == "no_exna_lap":
        tot, parts = nights_yoy(q, "base")
        tot = tot - parts["exna_fee_cancel_lap"] - parts["exna_rnpl_lap"]
        parts = dict(parts, exna_fee_cancel_lap=0.0, exna_rnpl_lap=0.0)
        return tot, parts
    return nights_yoy(q, scn)

rows, wide = [], []
for scn, (ns, adrs, fxp) in SCN.items():
    lvl = {}   # quarter -> dict of levels
    # 3Q26 / 4Q26 carried from bridge v3 (base); bear/bull use the bridge bands for nights and the card's central band for ADR ex-FX
    for q in Q26:
        b = B26[q]
        if scn.startswith("base"):
            n_yoy, x_yoy = b["nights_yoy"], b["adr_exfx"]
        else:
            n_yoy = br_band(q, "nights_yoy_pct")[0 if scn == "bear" else 1]
            x_yoy = br_band(q, "adr_yoy_exfx_pct")[0 if scn == "bear" else 1]
        fx_a = b["fx_adr"]
        adr_rep = x_yoy + fx_a
        n_mm = N_HIST[PRIOR[q]] * (1 + n_yoy / 100)
        adr_usd = ADR_HIST[PRIOR[q]] * (1 + adr_rep / 100)
        gbv = GBV_HIST[PRIOR[q]] * (1 + n_yoy / 100) * (1 + adr_rep / 100)
        if scn.startswith("base"):
            rev = b["revenue"]; lag = b["lagged_gbv"] * 1000
            # exactness check against bridge v3
            assert abs(gbv / 1000 - b["gbv_busd"]) < 0.02 and abs(n_mm - b["nights_mm"]) < 0.02 and abs(adr_usd - b["adr_usd"]) < 0.02
        else:
            p1, p2 = PREVQ[q]
            g = lambda x: lvl[x]["gbv"] if x in lvl else GBV_HIST[x]
            lag = (2 / 3) * g(p1) + (1 / 3) * g(p2)
            rev = LAM[int(q[0])][0] * lag
        lvl[q] = dict(nights_yoy=n_yoy, nights_mm=n_mm, adr_exfx=x_yoy, fx_adr=fx_a, adr_rep=adr_rep, adr_usd=adr_usd, gbv=gbv,
                      rev=rev, lag=lag, fx_rev=b["fx_rev"], tr=100 * rev / gbv, rev_same_q_tr=gbv * TR_HIST[PRIOR[q]] / 100,
                      rev_yoy=100 * (rev / REV_HIST[PRIOR[q]] - 1), parts={})
    for q in Q27:
        n_yoy, parts = nights_yoy_wrapped(q, ns)
        x_yoy = adr_exfx(q, adrs)
        fx_a = FX_ADR[fxp][q]
        adr_rep = x_yoy + fx_a
        pq = PRIOR[q]
        n_mm = lvl[pq]["nights_mm"] * (1 + n_yoy / 100) if pq in lvl else N_HIST[pq] * (1 + n_yoy / 100)
        adr_usd = (lvl[pq]["adr_usd"] if pq in lvl else ADR_HIST[pq]) * (1 + adr_rep / 100)
        gbv_prev = lvl[pq]["gbv"] if pq in lvl else GBV_HIST[pq]
        gbv = gbv_prev * (1 + n_yoy / 100) * (1 + adr_rep / 100)
        p1, p2 = PREVQ[q]
        lag = (2 / 3) * lvl[p1]["gbv"] + (1 / 3) * lvl[p2]["gbv"]
        rev = LAM[int(q[0])][0] * lag
        rev_prev = lvl[pq]["rev"] if pq in lvl else REV_HIST[pq]
        tr_prev = lvl[pq]["tr"] if pq in lvl else TR_HIST[pq]
        lvl[q] = dict(nights_yoy=n_yoy, nights_mm=n_mm, adr_exfx=x_yoy, fx_adr=fx_a, adr_rep=adr_rep, adr_usd=adr_usd, gbv=gbv,
                      rev=rev, lag=lag, fx_rev=REV_FX_KERNEL[fxp][q], tr=100 * rev / gbv, rev_same_q_tr=gbv * tr_prev / 100,
                      rev_yoy=100 * (rev / rev_prev - 1), parts=parts)
    for q in Q26 + Q27:
        L = lvl[q]
        pq = PRIOR[q]
        gbv_prev = lvl[pq]["gbv"] if pq in lvl else GBV_HIST[pq]
        lines = [("nights_yoy_pct", L["nights_yoy"], "%"), ("nights_mm", L["nights_mm"], "mm"),
                 ("adr_yoy_exfx_pct", L["adr_exfx"], "%"), ("fx_pts_adr", L["fx_adr"], "pp"),
                 ("adr_yoy_reported_pct", L["adr_rep"], "%"), ("adr_usd", L["adr_usd"], "$"),
                 ("gbv_musd", L["gbv"], "$M"), ("gbv_yoy_pct", 100 * (L["gbv"] / gbv_prev - 1), "%"),
                 ("lagged_gbv_musd", L["lag"], "$M"), ("revenue_musd", L["rev"], "$M"),
                 ("revenue_yoy_pct", L["rev_yoy"], "%"), ("take_rate_pct", L["tr"], "%"),
                 ("fx_pts_revenue", L["fx_rev"], "pp"), ("revenue_same_q_take_rate_route_musd", L["rev_same_q_tr"], "$M")]
        for ln, v, u in lines:
            rows.append(dict(quarter=q, scenario=scn, line=ln, value=float(v), unit=u,
                             source="bridge v3 carried" if (q in Q26 and scn.startswith("base")) else "06v build"))
        wide.append(dict(quarter=q, scenario=scn, **{k: v for k, v in L.items() if k != "parts"},
                         **{f"nights_part_{k}": v for k, v in L["parts"].items()}))
    # annuals
    fy26 = REV_HIST["1Q26"] + REV_HIST["2Q26"] + lvl["3Q26"]["rev"] + lvl["4Q26"]["rev"]
    fy27 = sum(lvl[q]["rev"] for q in Q27)
    n26 = N_HIST["1Q26"] + N_HIST["2Q26"] + lvl["3Q26"]["nights_mm"] + lvl["4Q26"]["nights_mm"]
    n27 = sum(lvl[q]["nights_mm"] for q in Q27)
    g26 = GBV_HIST["1Q26"] + GBV_HIST["2Q26"] + lvl["3Q26"]["gbv"] + lvl["4Q26"]["gbv"]
    g27 = sum(lvl[q]["gbv"] for q in Q27)
    fy25_rev = float(KPI.loc[[f"{k}Q25" for k in (1, 2, 3, 4)], "revenue_musd"].sum())
    fy25_n = float(KPI.loc[[f"{k}Q25" for k in (1, 2, 3, 4)], "nights_m"].sum())
    fy25_g = float(KPI.loc[[f"{k}Q25" for k in (1, 2, 3, 4)], "gbv_busd"].sum()) * 1000
    fyfx27 = sum(lvl[q]["fx_rev"] * lvl[q]["rev"] for q in Q27) / fy27
    for lab, r, n, g, r0, n0, g0 in [("FY26", fy26, n26, g26, fy25_rev, fy25_n, fy25_g), ("FY27", fy27, n27, g27, fy26, n26, g26)]:
        for ln, v, u in [("revenue_musd", r, "$M"), ("revenue_yoy_pct", 100 * (r / r0 - 1), "%"), ("nights_mm", n, "mm"),
                         ("nights_yoy_pct", 100 * (n / n0 - 1), "%"), ("gbv_musd", g, "$M"), ("gbv_yoy_pct", 100 * (g / g0 - 1), "%"),
                         ("take_rate_pct", 100 * r / g, "%"),
                         ("adr_usd", g / n, "$"), ("adr_yoy_reported_pct", 100 * ((g / n) / (g0 / n0) - 1), "%")]:
            rows.append(dict(quarter=lab, scenario=scn, line=ln, value=float(v), unit=u, source="sum of quarters"))
        if lab == "FY27":
            rows.append(dict(quarter=lab, scenario=scn, line="fx_pts_revenue", value=float(fyfx27), unit="pp", source="revenue-weighted average of quarters (23b rule)"))
    # FY28 continuation, base only
    if scn == "base":
        n28 = A("fy28_nights_yoy_pct", 7.0, "%", "judgement: clean comp, LatAm/APAC decay continues (WS10 direction), no new lever; reverse DCF market-implied 8-9 for FY27", True)
        a28 = A("fy28_adr_reported_yoy_pct", 2.0, "%", "judgement: residual at its 2023-25 mean 2.40 + carried mix -1.2 + seats -0.62 (15_seats 2028) + K 0 + FX 0 (spot held) ~ 0.6; rounded up to 2.0 for the 4Q27 exit 2.6", True)
        tr28 = A("fy28_take_rate_change_pts", 0.0, "pts", "judgement: take rate flat (management 'in line' language 2025-26)", True)
        g28 = g27 * (1 + n28 / 100) * (1 + a28 / 100)
        r28 = g28 * (fy27 / g27 + tr28 / 100)
        for ln, v, u in [("revenue_musd", r28, "$M"), ("revenue_yoy_pct", 100 * (r28 / fy27 - 1), "%"), ("nights_mm", n27 * (1 + n28 / 100), "mm"),
                         ("nights_yoy_pct", n28, "%"), ("gbv_musd", g28, "$M"), ("gbv_yoy_pct", 100 * (g28 / g27 - 1), "%"),
                         ("take_rate_pct", 100 * r28 / g28, "%"), ("adr_yoy_reported_pct", a28, "%")]:
            rows.append(dict(quarter="FY28", scenario=scn, line=ln, value=float(v), unit=u, source="annual continuation, growth-rate assumptions flagged is_judgement"))

PATH = pd.DataFrame(rows)
PATH.to_csv(OUT / "06v_independent_path.csv", index=False)
WIDE = pd.DataFrame(wide)
WIDE.to_csv(OUT / "06v_independent_path_wide.csv", index=False)

# ------------------------------------------------------------------------------- checks
CHK = []
def chk(name, ok, detail):
    CHK.append(dict(check=name, passed=bool(ok), detail=detail))

# sums equal annuals
for scn in SCN:
    p = PATH[PATH.scenario == scn]
    q27 = p[(p.quarter.isin(Q27)) & (p.line == "revenue_musd")].value.sum()
    fy = float(p[(p.quarter == "FY27") & (p.line == "revenue_musd")].value.iloc[0])
    chk(f"sum_of_quarters_equals_FY27_{scn}", abs(q27 - fy) < 0.01, f"{q27:.2f} vs {fy:.2f}")
# seasonal shares 2023-25 vs 2027 base
sh = {}
for y in (23, 24, 25):
    s = np.array([KPI.loc[f"{k}Q{y}", "nights_m"] for k in (1, 2, 3, 4)]); sh[y] = s / s.sum()
w = WIDE[WIDE.scenario == "base"].set_index("quarter")
n27 = np.array([w.loc[q, "nights_mm"] for q in Q27]); sh27 = n27 / n27.sum()
n26 = np.array([N_HIST["1Q26"], N_HIST["2Q26"], w.loc["3Q26", "nights_mm"], w.loc["4Q26", "nights_mm"]]); sh26 = n26 / n26.sum()
lo = np.min([sh[y] for y in sh], axis=0); hi = np.max([sh[y] for y in sh], axis=0)
SEAS = pd.DataFrame({"quarter": ["Q1", "Q2", "Q3", "Q4"], "share_2023": sh[23], "share_2024": sh[24], "share_2025": sh[25],
                     "share_2026_path": sh26, "share_2027_base": sh27, "inside_2023_25_range_pm_0.5pp": (sh27 >= lo - 0.005) & (sh27 <= hi + 0.005)})
SEAS.to_csv(OUT / "06v_seasonal_check.csv", index=False)
chk("seasonal_shares_2027_within_2023_25_range_pm_0.5pp", SEAS["inside_2023_25_range_pm_0.5pp"].all(), SEAS.round(4).to_string(index=False))
# 1Q27 vs 4Q26 exit
step = w.loc["1Q27", "nights_yoy"] - w.loc["4Q26", "nights_yoy"]
chk("1Q27_nights_within_2pts_of_4Q26_exit", abs(step) <= 2.0, f"step {step:+.2f} pts: WS10 FY27-vs-4Q26 base step {ws10_tot['base']-ws10_4q26:+.2f}, NA delta change {(na_under_27-ws10_na)*na_share_27-(na_under_26-ws10_4q26_na)*s4:+.2f}, ex-NA RNPL partial lap {-exna_rnpl_lap*Q1_FRAC:+.2f}")
fy27g = float(PATH[(PATH.scenario == "base") & (PATH.quarter == "FY27") & (PATH.line == "revenue_yoy_pct")].value.iloc[0])
chk("FY27_base_revenue_growth_inside_B3_band_9.2_11.5", 9.18 <= fy27g <= 11.52, f"{fy27g:.2f}%")
chk("4Q26_base_rows_equal_bridge_v3", True, "asserted in the build (nights, ADR $, GBV to 0.02; revenue and FX carried verbatim)")
pd.DataFrame(CHK).to_csv(OUT / "06v_pass_line.csv", index=False)

# ------------------------------------------------------------------------------- comparison columns
cmp_rows = []
for q in Q27:
    ws29 = WS29[(WS29.scenario == "base") & (WS29.quarter == f"2027Q{Q27.index(q)+1}")].iloc[0]
    pr32 = TOT32[(TOT32.scenario == "base") & (TOT32.quarter == q)]
    cmp_rows.append(dict(quarter=q, mine_nights=w.loc[q, "nights_yoy"], pr32_na_lap_only=float(pr32[~pr32.exna_lap].model_total_nights_yoy_pct.iloc[0]),
                         pr32_exna_lap=float(pr32[pr32.exna_lap].model_total_nights_yoy_pct.iloc[0]), ws29_nights=float(ws29.nights_yoy_pct),
                         mine_adr_exfx=w.loc[q, "adr_exfx"], ws29_adr_exfx=float(ws29.adr_exfx_pct), b3_adr_exfx=3.0,
                         mine_fx_rev=w.loc[q, "fx_rev"], ws29_fx_rev=float(ws29.fx_pp), kernel_23b_fx_rev=float(k23[f"q{Q27.index(q)+1}_pp"]),
                         mine_revenue=w.loc[q, "rev"], ws29_revenue=float(ws29.revenue_musd),
                         mine_rev_yoy=w.loc[q, "rev_yoy"], ws29_rev_yoy=float(ws29.reported_growth_pct)))
pd.DataFrame(cmp_rows).to_csv(OUT / "06v_comparison_quarterly.csv", index=False)
fy = PATH[(PATH.scenario == "base") & (PATH.quarter == "FY27")].set_index("line").value
cons27 = CONS[(CONS.period == "FY27") & (CONS.vendor == "LSEG")].iloc[0]
cons26 = CONS[(CONS.period == "FY26") & (CONS.vendor == "LSEG")].iloc[0]
ann = pd.DataFrame([
    dict(source="06v independent base", fy27_revenue_musd=fy["revenue_musd"], fy27_growth_pct=fy["revenue_yoy_pct"], fy27_nights_yoy=fy["nights_yoy_pct"], note="kernel route"),
    dict(source="WS29 base", fy27_revenue_musd=float(WS29[WS29.scenario == "base"].revenue_musd.sum()), fy27_growth_pct=11.55, fy27_nights_yoy=9.2, note="29_fy27_bridge.csv"),
    dict(source="B3 w=2/3 computed", fy27_revenue_musd=float(B3[B3.kernel_w > 0.6].fy27_revenue_musd.iloc[0]), fy27_growth_pct=float(B3[B3.kernel_w > 0.6].fy27_growth_pct.iloc[0]), fy27_nights_yoy=9.46, note="band 9.18-11.52 across w"),
    dict(source="B3 w=0.33 computed", fy27_revenue_musd=float(B3[B3.kernel_w < 0.4].fy27_revenue_musd.iloc[0]), fy27_growth_pct=float(B3[B3.kernel_w < 0.4].fy27_growth_pct.iloc[0]), fy27_nights_yoy=9.46, note=""),
    dict(source="LSEG consensus 2026-09-11 (comparison only)", fy27_revenue_musd=float(cons27.revenue_mean), fy27_growth_pct=100 * (float(cons27.revenue_mean) / float(cons26.revenue_mean) - 1), fy27_nights_yoy=np.nan, note=f"n {int(cons27.revenue_n)}, obs {cons27.revenue_obs_date}; vendor's own FY26 {float(cons26.revenue_mean):.0f}"),
    dict(source="PR #32 base, ex-NA lap", fy27_revenue_musd=np.nan, fy27_growth_pct=np.nan, fy27_nights_yoy=6.42, note="nights_quarterly_total.csv"),
    dict(source="PR #32 base, NA lap only", fy27_revenue_musd=np.nan, fy27_growth_pct=np.nan, fy27_nights_yoy=8.17, note=""),
])
ann.to_csv(OUT / "06v_comparison_annual.csv", index=False)
pd.DataFrame(ASSUMPTIONS).to_csv(OUT / "06v_assumptions.csv", index=False)

# ------------------------------------------------------------------------------- diff vs WS06 (line by line, explained)
# my line -> (WS06 line, scale factor applied to WS06 value to reach my unit, tolerance for a finding)
LINE_MAP = {
    "nights_yoy_pct": ("nights_yoy_pct", 1.0, 0.3), "nights_mm": ("nights_mm", 1.0, 0.5),
    "adr_yoy_exfx_pct": ("adr_exfx_yoy_pct", 1.0, 0.3), "fx_pts_adr": ("fx_pts_adr", 1.0, 0.3),
    "adr_yoy_reported_pct": ("adr_reported_yoy_pct", 1.0, 0.3), "adr_usd": ("adr_usd", 1.0, 0.5),
    "gbv_musd": ("gbv_busd", 1000.0, 100.0), "gbv_yoy_pct": ("gbv_yoy_pct", 1.0, 0.3), "lagged_gbv_musd": ("lagged_gbv_busd", 1000.0, 100.0),
    "revenue_musd": ("revenue_musd", 1.0, 15.0), "revenue_yoy_pct": ("revenue_yoy_pct", 1.0, 0.3),
    "take_rate_pct": ("take_rate_printed_pct", 1.0, 0.3), "fx_pts_revenue": ("fx_pts_revenue_memo", 1.0, 0.3),
}
EXPLAIN = {
    ("nights_yoy_pct", "1Q27"): "WS06 adds a Middle East base effect +1.0 (judgement, sourced qualitatively to the 1Q26 call) and phases WS10's ex-NA rate from its 4Q26 value (+0.1); bundle sized 1.65 (s=0.288) vs 1.75 (s=0.266) and prior-year share weights (+0.1); 1Q27 RNPL fraction 0.40 vs 0.42",
    ("nights_yoy_pct", "2Q27"): "WS06 adds a World Cup booking lap -0.5 (judgement, unsized by Airbnb); ex-NA phasing +0.05",
    ("nights_yoy_pct", "3Q27"): "WS06 ex-NA linear phasing (10.13 vs WS10 FY27 10.29 uniform); bundle sizing +0.1",
    ("nights_yoy_pct", "4Q27"): "WS06 ex-NA linear phasing (9.81 vs 10.29 uniform), i.e. the exit rate into FY28 is a phasing choice",
    ("adr_yoy_exfx_pct", None): "residual rule: WS06 AR(1) from K4 (rho 0.747, const 0.75, n 14) vs my bundle-lap step (4.85 -> 4.35 -> 3.85); K line: WS06 follows K4's migrated-share path (fades to -0.15 in 4Q27) vs carried 0.37 then 0 in 4Q27",
    ("fx_pts_adr", None): "WS06 uses a baskets proxy (0.699 x kernel global basket) for the regional-baskets leg; mine runs the B4 regional-baskets estimator forward on held spot. <0.05pp apart",
    ("revenue_musd", "1Q27"): "lambda_Q1 convention: WS06 2023-25 mean (0.127209) vs B3's 2023-26 (0.126938); 1Q27 revenue depends only on 2H26 GBV, which is identical",
    ("revenue_musd", None): "propagation of the nights differences above through GBV(q-1), GBV(q-2) x lambda; lambda_Q2 convention (0.137061 vs 0.137136)",
    ("take_rate_pct", None): "propagation (revenue / GBV) of the above",
    ("fx_pts_revenue", None): "both read fx_lag_v2 23b phi x 0.851 spot held; identical by construction",
    ("gbv_musd", None): "propagation of the nights and ADR differences", ("gbv_yoy_pct", None): "propagation of the nights and ADR differences",
    ("nights_mm", None): "propagation of nights_yoy_pct", ("adr_usd", None): "propagation of the ADR ex-FX and FX differences",
    ("adr_yoy_reported_pct", None): "propagation of the ADR ex-FX and FX differences", ("lagged_gbv_musd", None): "propagation",
    ("revenue_yoy_pct", None): "propagation",
}
SCN_EXPLAIN = {
    "bear": "SCENARIO DEFINITIONS DIFFER: WS06 bear = bridge band lows in 2H26 + PR #32 tranche-2 -1.0 on NA only + World Cup -0.75 + Middle East 0 + AR(1) mean-reversion residual 2.40 + usd_strong -1sd FX; mine = bridge band lows + tranche-2 -1.0 global + linear residual reversion + FX at spot held (FX variants separate)",
    "bull": "SCENARIO DEFINITIONS DIFFER: WS06 bull = bridge band highs + PR #32 new lever +2.35 on NA only + Middle East +1.0 + residual 4.85 held + usd_weak +1sd FX; mine = band highs + new lever on NA and ex-NA (+1.5 total) + residual held + FX at spot held",
}
ws06_file = WS06 / "06_revenue_path_3q26_4q27.csv"
ws06_ann = WS06 / "06_annual_fy26_fy28.csv"
V2B_DIR = OUT   # the _v2b files are written here (WS06v's folder); copies are placed next to WS06's originals as NEW files
if ws06_file.exists():
    W6 = pd.read_csv(ws06_file)
    A6 = pd.read_csv(ws06_ann) if ws06_ann.exists() else None
    diffs = []
    for scn in ("base", "bear", "bull"):
        for q in Q26 + Q27:
            for ln, (l6, scale, tol) in LINE_MAP.items():
                mine = PATH[(PATH.scenario == scn) & (PATH.quarter == q) & (PATH.line == ln)]
                w6 = W6[(W6.scenario == scn) & (W6.quarter == q) & (W6.line == l6)]
                if mine.empty or w6.empty:
                    continue
                v6 = float(w6.value.iloc[0]) * scale; vm = float(mine.value.iloc[0]); d = vm - v6
                flag = abs(d) > tol
                if q in Q26 and scn == "base":
                    why = "both carry bridge v3 unchanged"
                elif scn in SCN_EXPLAIN:
                    why = SCN_EXPLAIN[scn] if flag else "inside tolerance"
                else:
                    why = EXPLAIN.get((ln, q), EXPLAIN.get((ln, None), "")) if flag else "inside tolerance"
                diffs.append(dict(quarter=q, scenario=scn, line=ln, ws06=round(v6, 4), mine=round(vm, 4), diff=round(d, 4), tolerance=tol,
                                  is_finding=flag, explanation=why))
        if A6 is not None:
            for lab in ("FY26", "FY27"):
                a6 = A6[(A6.period == lab) & (A6.scenario == scn)]
                if a6.empty:
                    continue
                for ln, col, scale, tol in [("revenue_musd", "revenue_musd", 1.0, 15.0), ("revenue_yoy_pct", "revenue_musd_yoy_pct", 1.0, 0.3),
                                            ("nights_mm", "nights_mm", 1.0, 0.5), ("nights_yoy_pct", "nights_mm_yoy_pct", 1.0, 0.3),
                                            ("gbv_musd", "gbv_busd", 1000.0, 100.0), ("take_rate_pct", "take_rate_pct", 1.0, 0.3)]:
                    mine = PATH[(PATH.scenario == scn) & (PATH.quarter == lab) & (PATH.line == ln)]
                    if mine.empty:
                        continue
                    v6 = float(a6[col].iloc[0]) * scale; vm = float(mine.value.iloc[0]); d = vm - v6; flag = abs(d) > tol
                    why = ("sum of the quarterly differences" if scn == "base" else SCN_EXPLAIN[scn]) if flag else "inside tolerance"
                    diffs.append(dict(quarter=lab, scenario=scn, line=ln, ws06=round(v6, 4), mine=round(vm, 4), diff=round(d, 4), tolerance=tol,
                                      is_finding=flag, explanation=why))
    DIFF = pd.DataFrame(diffs)
    DIFF.to_csv(OUT / "06v_diff.csv", index=False)
    print(f"diff rows {len(DIFF)}, findings {int(DIFF.is_finding.sum())} (base: {int(DIFF[DIFF.scenario=='base'].is_finding.sum())})")

    # --------------------------------------------------------------------------- v2b: the one correction that changes what the model reads
    # WS06's kernel route makes 3Q26 revenue identical across scenarios ($4,804.0M, above the guide top $4,770M) because it reads only
    # printed 1Q26/2Q26 GBV. A bear margin case cannot run on base revenue. The pre-registration card's own 80% band for 3Q26 revenue
    # (INT-01: $4,755M to $4,878M around $4,816M, B1 registered block) is the sourced band; bear = low, bull = high, base unchanged.
    INT01 = {"bear": 4755.0, "bull": 4878.0}
    A("v2b_3q26_revenue_bear_musd", INT01["bear"], "$M", "PREREG_ABNB-INT-v1.md INT-01 80% band low (B1 registered block)", False)
    A("v2b_3q26_revenue_bull_musd", INT01["bull"], "$M", "PREREG_ABNB-INT-v1.md INT-01 80% band high", False)
    V2B = W6.copy()
    changes = []
    for scn, newrev in INT01.items():
        m = (V2B.scenario == scn) & (V2B.quarter == "3Q26")
        gbv = float(V2B[m & (V2B.line == "gbv_busd")].value.iloc[0]) * 1000
        rev_py = REV_HIST["3Q25"]
        upd = {"revenue_musd": newrev, "revenue_yoy_pct": 100 * (newrev / rev_py - 1), "take_rate_printed_pct": 100 * newrev / gbv,
               "take_rate_change_pts": 100 * newrev / gbv - TR_HIST["3Q25"], "revenue_conversion_lo_musd": np.nan, "revenue_conversion_hi_musd": np.nan}
        for ln, v in upd.items():
            mm = m & (V2B.line == ln)
            if mm.any():
                o = float(V2B.loc[mm, "value"].iloc[0])
                V2B.loc[mm, "value"] = v
                V2B.loc[mm, "source"] = f"v2b: INT-01 80% band {scn} (WS06v); was {o:.4f}"
                changes.append(dict(quarter="3Q26", scenario=scn, line=ln, old=round(o, 4), new=(round(v, 4) if pd.notna(v) else np.nan),
                                    reason="3Q26 revenue was identical across scenarios (kernel reads printed GBV only); replaced with the pre-registration card's INT-01 80% band so a bear/bull margin case does not run on base revenue"))
    V2B.to_csv(V2B_DIR / "06_revenue_path_3q26_4q27_v2b.csv", index=False)
    if A6 is not None:
        A6B = A6.copy()
        for scn, newrev in INT01.items():
            m6 = (A6B.period == "FY26") & (A6B.scenario == scn)
            old_q3 = float(W6[(W6.scenario == scn) & (W6.quarter == "3Q26") & (W6.line == "revenue_musd")].value.iloc[0])
            for col in ("revenue_musd", "quarters_sum_check_musd"):
                o = float(A6B.loc[m6, col].iloc[0]); A6B.loc[m6, col] = o + (newrev - old_q3)
            fy25 = float(A6B[(A6B.period == "FY25") & (A6B.scenario == scn)].revenue_musd.iloc[0])
            A6B.loc[m6, "revenue_musd_yoy_pct"] = 100 * (float(A6B.loc[m6, "revenue_musd"].iloc[0]) / fy25 - 1)
            A6B.loc[m6, "take_rate_pct"] = 100 * float(A6B.loc[m6, "revenue_musd"].iloc[0]) / (float(A6B.loc[m6, "gbv_busd"].iloc[0]) * 1000)
            m7 = (A6B.period == "FY27") & (A6B.scenario == scn)
            A6B.loc[m7, "revenue_musd_yoy_pct"] = 100 * (float(A6B.loc[m7, "revenue_musd"].iloc[0]) / float(A6B.loc[m6, "revenue_musd"].iloc[0]) - 1)
            changes.append(dict(quarter="FY26", scenario=scn, line="revenue_musd", old=round(float(A6.loc[m6, "revenue_musd"].iloc[0]), 4),
                                new=round(float(A6B.loc[m6, "revenue_musd"].iloc[0]), 4), reason="FY26 sum follows the 3Q26 change; FY27 growth re-based on it"))
        A6B.to_csv(V2B_DIR / "06_annual_fy26_fy28_v2b.csv", index=False)
    pd.DataFrame(changes).to_csv(V2B_DIR / "06_v2b_changes.csv", index=False)
    pd.DataFrame(ASSUMPTIONS).to_csv(OUT / "06v_assumptions.csv", index=False)

# ------------------------------------------------------------------------------- print
pd.set_option("display.width", 220)
print("\n=== 4Q26 exit re-derivation ===\n" + EXIT.to_string(index=False))
print("\n=== base path (wide) ===")
cols = ["nights_yoy", "nights_mm", "adr_exfx", "fx_adr", "adr_rep", "adr_usd", "gbv", "rev", "rev_yoy", "tr", "fx_rev", "rev_same_q_tr"]
print(w[cols].round(3).to_string())
for scn in ("bear", "bull", "base_fx_usd_strong", "base_fx_usd_weak"):
    ww = WIDE[WIDE.scenario == scn].set_index("quarter")
    print(f"\n=== {scn} ===")
    print(ww[cols].round(3).to_string())
print("\n=== annuals ===")
print(PATH[PATH.quarter.isin(["FY26", "FY27", "FY28"])].pivot_table(index=["quarter", "line"], columns="scenario", values="value").round(2).to_string())
print("\n=== checks ===\n" + pd.DataFrame(CHK)[["check", "passed"]].to_string(index=False))
print("\n=== FX reconciliation ===\n" + FXREC.to_string(index=False))
print(f"\nwrote {OUT}")
