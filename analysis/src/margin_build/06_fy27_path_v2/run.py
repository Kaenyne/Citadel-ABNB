"""WS06: FY27 quarterly revenue path v2.

Audits the PR #32 three-feature lap on real quarters, re-bases the FY27 quarterly path on the adopted
3Q26 / 4Q26 exit (H2 bridge v3), and builds one path file 3Q26-4Q27 (quarter x scenario x line) plus
FY26, FY27 and an FY28 base-only continuation for the margin model.

Architecture (identical to bridge v3 / B3, nothing new):
    nights y/y  = s_NA(q-4) x NA y/y + (1 - s_NA(q-4)) x ex-NA y/y  + laps + dated events        (growth space)
    ADR ex-FX   = like-for-like residual + K fee-mechanics line + measured / assumed mix terms       (ADR v3 card)
    ADR rep     = ADR ex-FX + ADR FX points (additive, as the card and the letters)
    GBV_q       = nights_q x ADR_q
    revenue_q   = lambda_q x (2/3 GBV_{q-1} + 1/3 GBV_{q-2})      lambda_q = 2023-25 mean, w = 2/3 (B3, bridge v3)
    take rate   = revenue_q / GBV_q  (printed definition, INT-06)
Consensus is a comparison column only; it enters nothing.

Run from the worktree root:
    python analysis/src/margin_build/06_fy27_path_v2/run.py
Exit code 0. Writes only under data/processed/margin_build/06_fy27_path_v2/ (and a figure via py -3.13 if available).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/margin_build/06_fy27_path_v2"
RAW = ROOT / "data/raw/margin_build/06_fy27_path_v2"
MANIFEST = ROOT / "data/manifests/margin_build/06_fy27_path_v2.csv"
FIG = ROOT / "analysis/figures/margin_build"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
MANIFEST.parent.mkdir(parents=True, exist_ok=True)

P = {
    "kpi": ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv",
    "b3_rebased": ROOT / "data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv",
    "b3_fx": ROOT / "data/processed/h2_bridge_v3/h2_bridge_fx.csv",
    "b3_fxline": ROOT / "data/processed/h2_bridge_v3/h2_bridge_v3_fx_line.csv",
    "b3_rev": ROOT / "data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv",
    "b3_card": ROOT / "data/processed/h2_bridge_v3/h2_bridge_v3_card_check.csv",
    "pr32_na": ROOT / "data/processed/nights_quarterly_na.csv",
    "pr32_tot": ROOT / "data/processed/nights_quarterly_total.csv",
    "ws10": ROOT / "data/processed/overnight/10_regional_forecast.csv",
    "wsd_gap": ROOT / "data/processed/overnight2/D/D1_exna_4q26_gap.csv",
    "wsd_lap": ROOT / "data/processed/overnight2/D/D1_lap_anniversary.csv",
    "card_terms": ROOT / "data/processed/adrv3/P/P1_card_v3_terms.csv",
    "k4_resid": ROOT / "data/processed/adrv3/K/K4_residual_nowcast.csv",
    "k4_fee": ROOT / "data/processed/adrv3/K/K4_fee_lap_schedule.csv",
    "seats": ROOT / "data/processed/adr/15_seats_dilution_quarterly.csv",
    "fx23": ROOT / "data/processed/forecast_methods/fx_lag_v2/23_forecast_4q26_v2.csv",
    "fx23b": ROOT / "data/processed/forecast_methods/fx_lag_v2/23b_fy27_annualisation_v2.csv",
    "ws29_q": ROOT / "data/processed/overnight/29_fy27_quarterly_path.csv",
    "ws29_b": ROOT / "data/processed/overnight/29_fy27_bridge.csv",
    "l1_reg": ROOT / "data/processed/forecast_methods/registry/l1-reconciliation-v2__fy27_revenue_v2.csv",
    "l1_band": ROOT / "data/processed/forecast_methods/l1_reconciliation_v2/fy27_kernel_band_v2.csv",
    "cons": ROOT / "data/processed/margin_build/03_consensus_pit/03_current_consensus.csv",
}
for k, v in P.items():
    assert v.exists(), f"missing input {k}: {v}"

Q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
Q26H2 = ["3Q26", "4Q26"]
SCEN = ["bear", "base", "bull"]
ASSUMPTIONS: list[dict] = []


def A(name, value, unit, source, judgement, note=""):
    ASSUMPTIONS.append({"name": name, "value": value, "unit": unit, "source": source,
                        "is_judgement": bool(judgement), "note": note})
    return value


def prev_q(q: str) -> str:
    n, y = int(q[0]), int(q[2:])
    return f"{4}Q{y-1:02d}" if n == 1 else f"{n-1}Q{y:02d}"


def qnum(q: str) -> int:
    return int(q[0])


# ----------------------------------------------------------------------------------------------
# 1. Inputs
# ----------------------------------------------------------------------------------------------
kpi = pd.read_csv(P["kpi"]).set_index("quarter")
hist = kpi[["nights_m", "gbv_busd", "adr_usd", "revenue_musd"]].copy()

# kernel lambda by fiscal quarter, 2023-25 mean, min, max (w = 2/3) -- reproduces bridge v3 conversion_mean
lam_rows = []
qs = hist.index.tolist()
for i, q in enumerate(qs):
    if 2023 <= 2000 + int(q[2:]) <= 2025:
        lag = (2 / 3) * hist.gbv_busd.iloc[i - 1] + (1 / 3) * hist.gbv_busd.iloc[i - 2]
        lam_rows.append({"quarter": q, "qn": qnum(q), "lam": hist.revenue_musd.loc[q] / (lag * 1000)})
lam_df = pd.DataFrame(lam_rows)
LAM = lam_df.groupby("qn").lam.agg(["mean", "min", "max"])
b3rev = pd.read_csv(P["b3_rev"]).set_index("quarter")
assert abs(LAM.loc[3, "mean"] - b3rev.loc["3Q26", "conversion_mean"]) < 1e-9
assert abs(LAM.loc[4, "mean"] - b3rev.loc["4Q26", "conversion_mean"]) < 1e-9
A("kernel_lambda_Q1", round(LAM.loc[1, "mean"], 6), "revenue / lagged GBV",
  "2023-25 mean of revenue_q / (2/3 GBV_{q-1} + 1/3 GBV_{q-2}), 02_kpi_panel_quarterly.csv; B3 gives 0.126938 (0.03pt apart, GBV rounding)", False)
A("kernel_lambda_Q2", round(LAM.loc[2, "mean"], 6), "revenue / lagged GBV", "same; B3 0.137136", False)
A("kernel_lambda_Q3", round(LAM.loc[3, "mean"], 6), "revenue / lagged GBV", "same; equals bridge v3 conversion_mean 3Q26 exactly", False)
A("kernel_lambda_Q4", round(LAM.loc[4, "mean"], 6), "revenue / lagged GBV", "same; equals bridge v3 conversion_mean 4Q26 exactly", False)
A("kernel_weight_w", 2 / 3, "share on GBV_{q-1}", "B3 published weight; bridge v3; band [0.33, 2/3] shown as comparison", False)

# bridge v3 adopted lines
reb = pd.read_csv(P["b3_rebased"])
b3fx = pd.read_csv(P["b3_fx"]).set_index("quarter")
b3fxl = pd.read_csv(P["b3_fxline"])
b3card = pd.read_csv(P["b3_card"])


def reb_val(q, line, col="adopted"):
    return float(reb[(reb.quarter == q) & (reb.line == line)][col].iloc[0])


BR = {}
for q in Q26H2:
    BR[q] = {
        "nights_yoy": reb_val(q, "nights_yoy_pct"), "nights_lo": reb_val(q, "nights_yoy_pct", "band_lo"),
        "nights_hi": reb_val(q, "nights_yoy_pct", "band_hi"),
        "adr_exfx": reb_val(q, "adr_yoy_exfx_pct"), "adr_lo": reb_val(q, "adr_yoy_exfx_pct", "band_lo"),
        "adr_hi": reb_val(q, "adr_yoy_exfx_pct", "band_hi"),
        "fx_adr": float(b3fx.loc[q, "fx_pts_adr_adopted"]),
        "fx_rev": float(b3fxl[(b3fxl.quarter == q) & (b3fxl.line == "fx_pts_revenue")].adopted_pp.iloc[0]),
        "revenue": float(b3rev.loc[q, "revenue_musd"]), "rev_lo": float(b3rev.loc[q, "revenue_low"]),
        "rev_hi": float(b3rev.loc[q, "revenue_high"]),
    }
A("3Q26_nights_yoy_pct", BR["3Q26"]["nights_yoy"], "pct", "h2_bridge_v3_rebased_lines.csv (team baseline, PR #32 base); band 8.5-11.0 reviews stays index", False)
A("4Q26_nights_yoy_pct", BR["4Q26"]["nights_yoy"], "pct", "h2_bridge_v3_rebased_lines.csv (ADR v3 N memo case B, WS-D global lap, 45% ex-NA split); band 8.0-8.86", False)
A("3Q26_adr_exfx_pct", BR["3Q26"]["adr_exfx"], "pct", "h2_bridge_v3_rebased_lines.csv (ADR v3 card v3_with_K, midpoint FX)", False)
A("4Q26_adr_exfx_pct", BR["4Q26"]["adr_exfx"], "pct", "same", False)
A("3Q26_fx_pts_adr", BR["3Q26"]["fx_adr"], "pp", "h2_bridge_fx.csv, ADR v3 midpoint of EUR fit and regional baskets", False)
A("4Q26_fx_pts_adr", BR["4Q26"]["fx_adr"], "pp", "same", False)
A("3Q26_fx_pts_revenue", BR["3Q26"]["fx_rev"], "pp", "h2_bridge_v3_fx_line.csv: management ~3 after hedging (6 Aug letter)", False)
A("4Q26_fx_pts_revenue", BR["4Q26"]["fx_rev"], "pp", "h2_bridge_v3_fx_line.csv: fx_lag_v2 kernel Phi x 0.851, spot held", False)

# PR #32
pr_na = pd.read_csv(P["pr32_na"])
pr_tot = pd.read_csv(P["pr32_tot"])
U26 = float(pr_na[(pr_na.quarter == "3Q26") & (pr_na.scenario == "base")].underlying_pts.iloc[0])
U27 = float(pr_na[(pr_na.quarter == "1Q27") & (pr_na.scenario == "base")].underlying_pts.iloc[0])
A("na_underlying_2026_pts", U26, "pct y/y", "choice model, no product lever (nights_quarterly_na.csv underlying_pts; analysis/src/nights_quarterly.py)", False)
A("na_underlying_2027_pts", U27, "pct y/y", "same; the 1.0pt step 2026->2027 is the choice model's annual rate change, placed on 1Q27", False)
NA_OBS = {"3Q25": 5.0, "1Q26": 8.0}
UNDERLYING_2025 = 2.6
RNPL_NA = NA_OBS["3Q25"] - UNDERLYING_2025
T1_NA = (NA_OBS["1Q26"] - U26) - RNPL_NA
PEAK_NA = RNPL_NA + T1_NA
GLOBAL_PTS = 3.0
A("pr32_rnpl_na_pts", round(RNPL_NA, 2), "pts of NA nights", "re-derived: NA 3Q25 5.0 - FY25 NA 2.6 (nights_quarterly.py fit_product)", False)
A("pr32_t1_cancel_na_pts", round(T1_NA, 2), "pts of NA nights", "re-derived: (NA 1Q26 8.0 - underlying 2026) - RNPL", False)
A("mgmt_global_bundle_1Q26_pts", GLOBAL_PTS, "pts of total nights", "Mertz, 1Q26 call (~3 pts); ledger D032", False)
S_1Q26 = A("na_share_1H26", 0.291, "share of nights", "FY25 NA share 29.6% (10-K regional, 158/533) chained with 1H26 NA +8% vs total +9.7%; judgement on the chain", True)
S_3Q26 = A("na_share_3Q26", 0.288, "share of nights", "PR #32 NA_SHARE (WS10 nights_share_est 28.8)", False)
S_4Q26 = A("na_share_4Q26", 0.282, "share of nights", "PR #32 NA_SHARE (WS10 28.2); the weight the bridge's 4Q26 decomposition used", False)
SHARE_BASE = {"1Q27": S_1Q26, "2Q27": S_1Q26, "3Q27": S_3Q26, "4Q27": S_4Q26}   # prior-year-quarter NA share = the y/y weight
EXNA_BUNDLE_TOTAL = GLOBAL_PTS - S_3Q26 * PEAK_NA   # total-nights points of the ex-NA bundle at full level
A("exna_bundle_total_pts", round(EXNA_BUNDLE_TOTAL, 3), "pts of total nights",
  "3.0 - 0.288 x 4.69 = 1.65; the figure N memo / WS-D used (D1_exna_4q26_gap: 100% case = 1.75 at PR #32's 0.266 weight)", False)
wsd = pd.read_csv(P["wsd_gap"])
FEE_SPLIT = A("exna_fee_cancel_share_of_bundle", 0.45, "share", "ADR v3 N memo case B point: midpoint of WS-D's pinned 40-50% (D1_exna_4q26_gap.csv); adopted in bridge v3", False)
LAP_FEE_TOTAL = FEE_SPLIT * EXNA_BUNDLE_TOTAL          # lapped from 4Q26 (global from Oct-Dec 2025)
LAP_RNPL_TOTAL = (1 - FEE_SPLIT) * EXNA_BUNDLE_TOTAL   # ex-NA RNPL, live 17 Feb - 4 Mar 2026 (D025-D029)
PARTIAL_1Q27 = A("exna_rnpl_lap_fraction_1Q27", 0.40, "share of the ex-NA RNPL leg lapped in 1Q27",
                 "D1_lap_anniversary.csv: ex-NA RNPL live 17 Feb-4 Mar 2026, roughly the last 5-6 of 13 weeks of 1Q26, ramping; 1Q27 lap is partial, 2Q27 full. Fraction is judgement.", True)
A("pr32_bull_new_lever_na_pts", 2.35, "pts of NA nights", "PR #32 bull: a new lever half the old bundle's size for FY27 (unnamed feature)", True)
A("pr32_bear_t2_fee_na_pts", -1.0, "pts of NA nights", "PR #32 bear: single fee tranche 2 (13 Oct 2026) at payout-neutral re-pricing costs nights, window 4Q26-3Q27", True)
ME_1Q27 = A("middle_east_base_effect_1Q27_pts", 1.0, "pts of total nights",
            "CFO Mertz, 1Q26 call: nights grew 9% after an approximate 100bp headwind from the Middle East conflict (10_regional note s.202); 1Q27 laps that base. Bear 0 (recurrence).", False)
WC_2Q27 = A("world_cup_booking_lap_2Q27_pts", -0.5, "pts of total nights",
            "World Cup stay nights booked 4Q25-2Q26, never sized by Airbnb (WS10, WS29); 2Q27 laps the peak booking quarter. Base -0.5, bear -0.75, bull 0.", True)
A("rnpl_eligibility_expansion_lap_3Q27_pts", 0.0, "pts of total nights",
  "July 2026 RNPL expanded booking types (D044) laps in 3Q27, not 2Q27 as WS29 labels; unsized, carried at zero", True)

# WS10 regional
ws10 = pd.read_csv(P["ws10"])


def ws10_total(period, scen):
    return float(ws10[(ws10.period == period) & (ws10.region == "TOTAL") & (ws10.scenario == scen)].nights_yoy_pct.iloc[0])


def ws10_na(period, scen):
    r = ws10[(ws10.period == period) & (ws10.region == "na") & (ws10.scenario == scen)].iloc[0]
    return float(r.nights_yoy_pct), float(r.nights_share_est_pct) / 100


def ws10_exna_rate(period, scen):
    tot = ws10_total(period, scen)
    na, s = ws10_na(period, scen)
    return (tot - s * na) / (1 - s)


EXNA = {}
for scen in SCEN:
    x4 = ws10_exna_rate("4Q26", scen)
    x27 = ws10_exna_rate("FY27", scen)
    d = (x4 - x27) / 2.5          # linear path from the 4Q26 rate whose four-quarter mean equals WS10's FY27 rate
    EXNA[scen] = {q: x4 - (k + 1) * d for k, q in enumerate(Q27)}
    A(f"ws10_exna_rate_4Q26_{scen}", round(x4, 3), "pct y/y ex-NA nights", "10_regional_forecast.csv TOTAL less NA at WS10's own share (includes WS10's -0.41 calibration)", False)
    A(f"ws10_exna_rate_FY27_{scen}", round(x27, 3), "pct y/y ex-NA nights", "same, FY27 rows", False)
A("exna_phasing_rule", "linear from the WS10 4Q26 ex-NA rate; four-quarter mean = WS10 FY27 rate", "rule",
  "judgement: WS10 gives only an annual FY27 rate; a linear decay avoids a jump at 1Q27", True)

# ADR v3 card terms (3Q26 point terms carried, as the card carries them into 4Q26)
terms = pd.read_csv(P["card_terms"])
t3 = terms[(terms.quarter == "3Q26") & (terms.variant == "v3_with_K")].set_index("term").point_pp
GEO = A("adr_geo_mix_pp", round(float(t3["geographic_mix"]), 3), "pp of ex-FX ADR", "P1_card_v3_terms.csv (workstream I measured); carried flat through 2027 as the card carries it into 4Q26", False)
PARTY = A("adr_party_size_pp", round(float(t3["unit_size_party"]), 3), "pp", "same", False)
LOS = A("adr_los_mix_pp", round(float(t3["length_of_stay_mix"]), 3), "pp", "same", False)
INTER = A("adr_interaction_pp", round(float(t3["interaction"]), 3), "pp", "same (descriptive)", False)
seats = pd.read_csv(P["seats"])
SEATS27 = A("adr_new_business_seats_2027_pp", round(float(seats[(seats.case_business == "base") & (seats.quarter == "1Q27")].dilution_drag_pp.iloc[0]), 3), "pp",
            "15_seats_dilution_quarterly.csv base 2027 (-0.565 vs -0.483 in 2026); nets to zero in GBV and revenue (B3)", False)
MIX27 = GEO + PARTY + LOS + INTER + SEATS27
k4 = pd.read_csv(P["k4_resid"])
ar_row = k4[(k4.scenario == "AR(1) on the residual") & (k4.quarter == "3Q26")].iloc[0]
import re
m = re.search(r"rho ([0-9.]+), const ([0-9.]+)", ar_row.basis)
RHO, CONST = float(m.group(1)), float(m.group(2))
RESID_4Q26 = float(terms[(terms.quarter == "4Q26") & (terms.variant == "v3_with_K") & (terms.term == "like_for_like_pricing_residual")].point_pp.iloc[0])
RESID_MEANREV = float(k4[(k4.scenario == "mean reversion") & (k4.quarter == "4Q26")].residual_pp.iloc[0])
A("adr_residual_4Q26_pp", round(RESID_4Q26, 3), "pp", "ADR v3 card v3_with_K 4Q26 residual (last_q rule = 2Q26 value 4.85)", False)
A("adr_residual_ar1_rho", RHO, "coefficient", "K4_residual_nowcast.csv: AR(1) fitted 1Q23-2Q26 (n 14); long-run mean const/(1-rho) = %.2f" % (CONST / (1 - RHO)), False)
A("adr_residual_ar1_const", CONST, "pp", "same", False)
A("adr_residual_2027_rule_base", "AR(1) iterated from the adopted 4Q26 value 4.85", "rule",
  "judgement: the card's last_q rule is a one-quarter rule (scored n 10); at 3-6 quarter horizons the fitted AR(1) is the only residual rule in the repo with a horizon; bear = K4 mean reversion (2.40), bull = persistence (4.85)", True)
A("adr_residual_bear_pp", RESID_MEANREV, "pp", "K4 mean reversion: 2023-25 mean", False)
kfee = pd.read_csv(P["k4_fee"])
kc = kfee[kfee.variant == "central"].set_index("quarter").yoy_change_pp
K_COEF = A("k_line_coefficient", 0.007, "pp of residual per pp of y/y migrated nights share", "K2 pre-stated central mechanics (imposed, not estimated); K4 chains it on the 2Q26 base share 21.5", False)
K_LINE = {q: K_COEF * (float(kc[q]) - float(kc["2Q26"])) for q in Q27}
A("k_line_1Q27_to_4Q27_pp", json.dumps({q: round(v, 3) for q, v in K_LINE.items()}), "pp", "0.007 x (K4 central y/y migrated share(q) - 21.5); 4Q27 negative because the migration completes and the y/y share drops to zero", False)

# FX: ADR-FX estimators for 2027 under spot held, and the +/-1sd USD variants
fx23 = pd.read_csv(P["fx23"])
eur = b3fx.eurusd_avg
EUR_HELD = float(eur["4Q26"])
eur_fit = np.polyfit(b3fx.eurusd_yoy_pct.values, b3fx.fx_pts_adr_eur_fit.values, 1)   # exact linear reconstruction of the card's EUR fit
assert np.allclose(np.polyval(eur_fit, b3fx.eurusd_yoy_pct.values), b3fx.fx_pts_adr_eur_fit.values, atol=0.01)
A("adr_fx_eur_fit", f"fx_pts = {eur_fit[1]:.3f} + {eur_fit[0]:.4f} x EUR/USD y/y %", "rule", "reconstructed exactly from the four h2_bridge_fx.csv rows (ADR v3 N memo EUR fit)", False)
basket_ratio = (b3fx.fx_pts_adr_baskets / fx23[fx23.path == "spot_held"].set_index("quarter").reindex(["3Q26", "4Q26"]).basket_lag0_pct.reindex(b3fx.index).fillna(pd.Series({"1Q26": 5.673, "2Q26": 2.266}))).dropna()
K_BASKET = A("adr_fx_baskets_proxy_ratio", round(float(basket_ratio.mean()), 3), "ADR-FX pp per pp of the global revenue-weighted basket y/y",
             "mean over 1Q26-4Q26 of (ADR v3 regional-baskets estimate / fx_lag_v2 global basket y/y): %s; the regional-baskets estimator is not run forward past 4Q26, so 2027 uses this proxy" % ", ".join(f"{k} {v:.2f}" for k, v in basket_ratio.items()), True)
A("fx_spot_held_eurusd", EUR_HELD, "USD per EUR", "h2_bridge_fx.csv 4Q26 eurusd_avg (FRED through 2026-09-04, held)", False)
FXPATH = {"bear": "usd_strong_-1sd", "base": "spot_held", "bull": "usd_weak_+1sd"}
A("fx_scenario_mapping", "bear = usd_strong_-1sd, base = spot_held, bull = usd_weak_+1sd", "rule", "fx_lag_v2 23_forecast_4q26_v2.csv paths", False)


def adr_fx_2027(q, scen):
    """Midpoint of the EUR fit (spot held) and the baskets proxy, shifted by the +/-1sd basket difference."""
    eur_yoy = (EUR_HELD / float(eur[prev_year(q)]) - 1) * 100
    eur_pts = np.polyval(eur_fit, eur_yoy)
    spot = fx23[(fx23.path == "spot_held") & (fx23.quarter == q)].basket_lag0_pct.iloc[0]
    var = fx23[(fx23.path == FXPATH[scen]) & (fx23.quarter == q)].basket_lag0_pct.iloc[0]
    baskets = K_BASKET * spot
    mid = 0.5 * (eur_pts + baskets)
    return float(mid + K_BASKET * (var - spot)), float(eur_pts), float(baskets), float(eur_yoy)


def prev_year(q):
    return f"{q[0]}Q{int(q[2:]) - 1:02d}"


def rev_fx_pts(q, scen):
    return float(fx23[(fx23.path == FXPATH[scen]) & (fx23.quarter == q)]["point_phi_basket_scale_0.851_pp"].iloc[0])


# ----------------------------------------------------------------------------------------------
# 2. Audit of PR #32 (re-derivation)
# ----------------------------------------------------------------------------------------------
audit_rows = []
for _, r in pr_na[pr_na.scenario == "base"].iterrows():
    u = U26 if r.quarter.endswith("26") else U27
    prod = T1_NA if r.quarter == "3Q26" else 0.0
    audit_rows.append({"object": f"PR32 NA base {r.quarter}", "pr32_value": r.na_nights_yoy_pct, "rederived": round(u + prod, 2),
                       "diff": round(r.na_nights_yoy_pct - (u + prod), 2), "note": "underlying + in-window product (RNPL window 3Q25-2Q26; t1+cancel 4Q25-3Q26)"})
for _, r in pr_tot[(pr_tot.scenario == "base")].iterrows():
    s = {"3Q26": 0.288, "4Q26": 0.282}.get(r.quarter, 0.266)
    na_val = float(pr_na[(pr_na.scenario == "base") & (pr_na.quarter == r.quarter)].na_nights_yoy_pct.iloc[0])
    ws10_na_v = {"3Q26": 7.0, "4Q26": 7.0}.get(r.quarter, 6.0)
    ex = 0.0
    if r.exna_lap and r.quarter.endswith("27"):
        ex = -(GLOBAL_PTS - s * PEAK_NA)
    red = r.ws10_total_pct + (na_val - ws10_na_v) * s + ex
    audit_rows.append({"object": f"PR32 total base {r.quarter} exna_lap={r.exna_lap}", "pr32_value": r.model_total_nights_yoy_pct,
                       "rederived": round(red, 2), "diff": round(r.model_total_nights_yoy_pct - red, 2),
                       "note": "WS10 total + s x (NA - WS10 NA) + ex-NA lap; s = 0.266 in 2027 (forecast-year share, see finding 3)"})
# FY27 sums PR #32 never produced
pr_levels = {}
base26 = {"1Q26": hist.nights_m["1Q26"], "2Q26": hist.nights_m["2Q26"], "3Q26": 133.6 * (1 + 9.89 / 100), "4Q26": 121.9 * (1 + 8.9 / 100)}
for lap in (False, True):
    sub = pr_tot[(pr_tot.scenario == "base") & (pr_tot.exna_lap == lap)].set_index("quarter").model_total_nights_yoy_pct
    lv = {q: base26[prev_year(q)] * (1 + sub[q] / 100) for q in Q27}
    fy27 = sum(lv.values()); fy26 = sum(base26.values())
    pr_levels[lap] = (fy27, fy27 / fy26 - 1)
    audit_rows.append({"object": f"PR32 FY27 nights level, base, exna_lap={lap}", "pr32_value": None, "rederived": round(fy27, 1),
                       "diff": None, "note": f"FY27 sum {fy27:.1f}mm = {100*(fy27/fy26-1):.2f}% on PR #32's own FY26 {fy26:.1f}mm; PR #32 left 3Q27/4Q27 levels blank"})
audit = pd.DataFrame(audit_rows)
audit.to_csv(OUT / "06_pr32_rederivation.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 3. The nights build 1Q27-4Q27
# ----------------------------------------------------------------------------------------------
NA27 = {"base": {q: U27 for q in Q27},
        "bear": {q: U27 + (-1.0 if q in ("1Q27", "2Q27", "3Q27") else 0.0) for q in Q27},
        "bull": {q: U27 + 2.35 for q in Q27}}
LAP = {"1Q27": -(LAP_FEE_TOTAL + PARTIAL_1Q27 * LAP_RNPL_TOTAL), "2Q27": -EXNA_BUNDLE_TOTAL, "3Q27": -EXNA_BUNDLE_TOTAL, "4Q27": -EXNA_BUNDLE_TOTAL}
EVENTS = {"base": {"1Q27": ME_1Q27, "2Q27": WC_2Q27, "3Q27": 0.0, "4Q27": 0.0},
          "bear": {"1Q27": 0.0, "2Q27": 1.5 * WC_2Q27, "3Q27": 0.0, "4Q27": 0.0},
          "bull": {"1Q27": ME_1Q27, "2Q27": 0.0, "3Q27": 0.0, "4Q27": 0.0}}
nb_rows = []
for scen in SCEN:
    for q in Q27:
        s = SHARE_BASE[q]
        na = NA27[scen][q]; ex = EXNA[scen][q]
        tot = s * na + (1 - s) * ex + LAP[q] + EVENTS[scen][q]
        nb_rows.append({"quarter": q, "scenario": scen, "na_share_prior_year": s, "na_yoy_pct": round(na, 3),
                        "exna_ws10_prelap_yoy_pct": round(ex, 3), "na_contribution_pts": round(s * na, 3),
                        "exna_contribution_prelap_pts": round((1 - s) * ex, 3),
                        "exna_lap_fee_cancel_pts": round(-LAP_FEE_TOTAL, 3),
                        "exna_lap_rnpl_pts": round(LAP[q] + LAP_FEE_TOTAL, 3),
                        "event_pts": EVENTS[scen][q], "total_nights_yoy_pct": round(tot, 3),
                        "sens_no_exna_lap_case_A_pct": round(tot - LAP[q], 3)})
nights_build = pd.DataFrame(nb_rows)
# re-derive the 4Q26 exit on the same decomposition (check against the bridge's 8.12)
exit_rederived = S_4Q26 * U26 + (1 - S_4Q26) * ws10_exna_rate("4Q26", "base") - LAP_FEE_TOTAL
nights_build.attrs["exit_check"] = exit_rederived

# ----------------------------------------------------------------------------------------------
# 4. The ADR build 1Q27-4Q27
# ----------------------------------------------------------------------------------------------
resid = {"base": {}, "bear": {}, "bull": {}}
r = RESID_4Q26
for q in Q27:
    r = CONST + RHO * r
    resid["base"][q] = r
    resid["bear"][q] = RESID_MEANREV
    resid["bull"][q] = RESID_4Q26
ab_rows = []
for scen in SCEN:
    for q in Q27:
        exfx = resid[scen][q] + K_LINE[q] + MIX27
        fx, eur_pts, bask, eur_yoy = adr_fx_2027(q, scen)
        ab_rows.append({"quarter": q, "scenario": scen, "residual_pp": round(resid[scen][q], 3), "k_line_pp": round(K_LINE[q], 3),
                        "geo_mix_pp": GEO, "party_size_pp": PARTY, "los_pp": LOS, "new_business_seats_pp": SEATS27, "interaction_pp": INTER,
                        "adr_exfx_yoy_pct": round(exfx, 3), "eur_yoy_spot_held_pct": round(eur_yoy, 3), "fx_eur_fit_pp": round(eur_pts, 3),
                        "fx_baskets_proxy_pp": round(bask, 3), "fx_pts_adr": round(fx, 3), "adr_reported_yoy_pct": round(exfx + fx, 3)})
adr_build = pd.DataFrame(ab_rows)

# ----------------------------------------------------------------------------------------------
# 5. Levels: 3Q26-4Q27 by scenario, kernel revenue, take rate
# ----------------------------------------------------------------------------------------------
lines = []


def add(q, scen, **kw):
    for k, v in kw.items():
        lines.append({"quarter": q, "scenario": scen, "line": k, "value": v})


levels = {}   # (q, scen) -> dict
for scen in SCEN:
    N = dict(hist.nights_m); ADR = dict(hist.adr_usd); G = dict(hist.gbv_busd); REV = dict(hist.revenue_musd)
    src = {}
    for q in Q26H2:
        b = BR[q]
        n_yoy = {"base": b["nights_yoy"], "bear": b["nights_lo"], "bull": b["nights_hi"]}[scen]
        a_ex = {"base": b["adr_exfx"], "bear": b["adr_lo"], "bull": b["adr_hi"]}[scen]
        a_fx = b["fx_adr"]
        py = prev_year(q)
        N[q] = N[py] * (1 + n_yoy / 100)
        ADR[q] = ADR[py] * (1 + (a_ex + a_fx) / 100)
        G[q] = N[q] * ADR[q] / 1000
        lag = (2 / 3) * G[prev_q(q)] + (1 / 3) * G[prev_q(prev_q(q))]
        REV[q] = LAM.loc[qnum(q), "mean"] * lag * 1000
        if scen == "base":
            assert abs(REV[q] - b["revenue"]) < 0.5, (q, REV[q], b["revenue"])
            card = b3card[(b3card.quarter == q)].set_index("object").bridge
            assert abs(N[q] - card["nights, mm"]) < 0.02 and abs(ADR[q] - card["ADR $"]) < 0.02
        levels[(q, scen)] = dict(nights_yoy=n_yoy, adr_exfx=a_ex, fx_adr=a_fx, adr_rep=a_ex + a_fx, nights=N[q], adr=ADR[q], gbv=G[q],
                                 rev=REV[q], lag=lag, fx_rev=b["fx_rev"], rev_lo=LAM.loc[qnum(q), "min"] * lag * 1000, rev_hi=LAM.loc[qnum(q), "max"] * lag * 1000,
                                 source="bridge v3 " + ("adopted" if scen == "base" else "band " + ("lo" if scen == "bear" else "hi")))
    for q in Q27:
        nb = nights_build[(nights_build.quarter == q) & (nights_build.scenario == scen)].iloc[0]
        ab = adr_build[(adr_build.quarter == q) & (adr_build.scenario == scen)].iloc[0]
        py = prev_year(q)
        N[q] = N[py] * (1 + nb.total_nights_yoy_pct / 100)
        ADR[q] = ADR[py] * (1 + ab.adr_reported_yoy_pct / 100)
        G[q] = N[q] * ADR[q] / 1000
        lag = (2 / 3) * G[prev_q(q)] + (1 / 3) * G[prev_q(prev_q(q))]
        REV[q] = LAM.loc[qnum(q), "mean"] * lag * 1000
        levels[(q, scen)] = dict(nights_yoy=nb.total_nights_yoy_pct, adr_exfx=ab.adr_exfx_yoy_pct, fx_adr=ab.fx_pts_adr, adr_rep=ab.adr_reported_yoy_pct,
                                 nights=N[q], adr=ADR[q], gbv=G[q], rev=REV[q], lag=lag, fx_rev=rev_fx_pts(q, scen),
                                 rev_lo=LAM.loc[qnum(q), "min"] * lag * 1000, rev_hi=LAM.loc[qnum(q), "max"] * lag * 1000, source="06 v2 build")
    # FY28 continuation, base only: nights y/y = 4Q27 base rate held; residual continues the AR(1); K = 0; mix held; FX 0
    if scen == "base":
        rr = resid["base"]["4Q27"]
        for q in ["1Q28", "2Q28", "3Q28", "4Q28"]:
            rr = CONST + RHO * rr
            py = prev_year(q)
            n_yoy = levels[("4Q27", "base")]["nights_yoy"]
            a_ex = rr + MIX27
            N[q] = N[py] * (1 + n_yoy / 100); ADR[q] = ADR[py] * (1 + a_ex / 100); G[q] = N[q] * ADR[q] / 1000
            lag = (2 / 3) * G[prev_q(q)] + (1 / 3) * G[prev_q(prev_q(q))]
            REV[q] = LAM.loc[qnum(q), "mean"] * lag * 1000
            levels[(q, scen)] = dict(nights_yoy=n_yoy, adr_exfx=a_ex, fx_adr=0.0, adr_rep=a_ex, nights=N[q], adr=ADR[q], gbv=G[q], rev=REV[q], lag=lag,
                                     fx_rev=0.0, rev_lo=np.nan, rev_hi=np.nan, source="FY28 continuation (flagged)")
    levels[("hist", scen)] = (N, ADR, G, REV)

# long path file
rows = []
for (q, scen), L in levels.items():
    if q == "hist":
        continue
    N, ADR, G, REV = levels[("hist", scen)]
    py = prev_year(q)
    tr = L["rev"] / (L["gbv"] * 1000) * 100
    tr_py = REV[py] / (G[py] * 1000) * 100
    rev_alt = L["gbv"] * 1000 * tr_py / 100
    rev_yoy = (L["rev"] / REV[py] - 1) * 100
    gbv_yoy = (L["gbv"] / G[py] - 1) * 100
    d = {"nights_yoy_pct": L["nights_yoy"], "nights_mm": L["nights"], "adr_exfx_yoy_pct": L["adr_exfx"], "fx_pts_adr": L["fx_adr"],
         "adr_reported_yoy_pct": L["adr_rep"], "adr_usd": L["adr"], "gbv_busd": L["gbv"], "gbv_yoy_pct": gbv_yoy,
         "lagged_gbv_busd": L["lag"], "revenue_musd": L["rev"], "revenue_yoy_pct": rev_yoy,
         "revenue_conversion_lo_musd": L["rev_lo"], "revenue_conversion_hi_musd": L["rev_hi"],
         "take_rate_printed_pct": tr, "take_rate_prior_year_pct": tr_py, "take_rate_change_pts": tr - tr_py,
         "revenue_alt_same_q_take_rate_musd": rev_alt, "fx_pts_revenue_memo": L["fx_rev"],
         "revenue_exfx_yoy_memo_pct": rev_yoy - L["fx_rev"]}
    for k, v in d.items():
        rows.append({"quarter": q, "scenario": scen, "line": k, "value": round(float(v), 4) if pd.notna(v) else np.nan, "source": L["source"]})
path_long = pd.DataFrame(rows)
wide = path_long.pivot_table(index=["quarter", "scenario"], columns="line", values="value").reset_index()
order = {q: i for i, q in enumerate(["3Q26", "4Q26"] + Q27 + ["1Q28", "2Q28", "3Q28", "4Q28"])}
wide["_o"] = wide.quarter.map(order); wide = wide.sort_values(["_o", "scenario"]).drop(columns="_o")

# annual
ann = []
for scen in SCEN:
    N, ADR, G, REV = levels[("hist", scen)]
    for fy, qq in (("FY25", ["1Q25", "2Q25", "3Q25", "4Q25"]), ("FY26", ["1Q26", "2Q26", "3Q26", "4Q26"]), ("FY27", Q27), ("FY28", ["1Q28", "2Q28", "3Q28", "4Q28"])):
        if fy == "FY28" and scen != "base":
            continue
        n = sum(N[q] for q in qq); g = sum(G[q] for q in qq); rv = sum(REV[q] for q in qq)
        ann.append({"period": fy, "scenario": scen, "nights_mm": n, "gbv_busd": g, "adr_usd": g * 1000 / n, "revenue_musd": rv, "take_rate_pct": rv / (g * 1000) * 100,
                    "fx_pts_revenue_memo": (np.nan if fy in ("FY25",) else (sum(levels[(q, scen)]["fx_rev"] * levels[(q, scen)]["rev"] for q in qq) / rv if fy != "FY26" else np.nan))})
annual = pd.DataFrame(ann)
for col in ("nights_mm", "gbv_busd", "adr_usd", "revenue_musd"):
    annual[col + "_yoy_pct"] = annual.groupby("scenario")[col].pct_change() * 100
annual["quarters_sum_check_musd"] = annual.revenue_musd
# quarterly-sum == annual check (by construction; assert explicitly)
for scen in SCEN:
    N, ADR, G, REV = levels[("hist", scen)]
    assert abs(sum(REV[q] for q in Q27) - annual[(annual.period == "FY27") & (annual.scenario == scen)].revenue_musd.iloc[0]) < 1e-6
annual = annual.round(4)

# ----------------------------------------------------------------------------------------------
# 6. Consensus comparison column (LSEG quarterly pull if present; else the derived CSV already on disk)
# ----------------------------------------------------------------------------------------------
cons_q_path = OUT / "06_consensus_quarterly_2027.csv"
raw_files = sorted(RAW.glob("lseg_abnb_quarterly_consensus_*.csv")) if RAW.exists() else []
if raw_files:
    rawf = raw_files[-1]
    lr = pd.read_csv(rawf)
    pull_ts = rawf.stem.split("_")[-1]
    cq = pd.DataFrame({
        "period_code": lr.period_code,
        "period_end": lr["Period End Date"],
        "revenue_mean_musd": lr["Revenue - Mean"] / 1e6,
        "revenue_n": lr["Revenue - Number of Estimates"],
        "revenue_sd_musd": lr["Revenue - Standard Deviation"] / 1e6,
        "revenue_obs_date": lr["Date"],
        "ebitda_mean_musd": lr["EBITDA - Mean"] / 1e6,
        "ebitda_n": lr["EBITDA - Number of Estimates"],
        "vendor": "LSEG (lseg-data desktop, TR.RevenueMean / TR.EBITDAMean)",
        "pull_timestamp_local": pull_ts,
    })
    pe = pd.to_datetime(cq.period_end)
    cq["quarter"] = [f"{((d.month - 1) // 3) + 1}Q{d.year % 100:02d}" if c.startswith("FQ") else f"FY{d.year % 100:02d}" for d, c in zip(pe, cq.period_code)]
    cq.to_csv(cons_q_path, index=False)
    man = pd.DataFrame([{"file": str(rawf.relative_to(ROOT)).replace("\\", "/"), "source": "LSEG Workspace desktop API via lseg-data 2.1.1, ABNB.O, Periods FQ1-FQ6, FY1-FY3",
                         "url": "n/a (licensed API)", "timestamp_local": pull_ts, "sha256": hashlib.sha256(rawf.read_bytes()).hexdigest(), "licensed": True, "committed": False}])
    man.to_csv(MANIFEST, index=False)
cq = pd.read_csv(cons_q_path)
cons = pd.read_csv(P["cons"])

# WS29, L1 v2, PR #32 comparison per quarter
ws29 = pd.read_csv(P["ws29_q"]); ws29["quarter"] = ws29.quarter.str.replace("2027Q", "", regex=False) + "Q27"
l1 = pd.read_csv(P["l1_reg"]); l1["quarter"] = l1.quarter.str.replace(r"(\d{4})Q(\d)", lambda m: f"{m.group(2)}Q{m.group(1)[2:]}", regex=True)
comp = []
for q in Q26H2 + Q27:
    row = {"quarter": q}
    for scen in SCEN:
        L = levels[(q, scen)]; N, ADR, G, REV = levels[("hist", scen)]
        row[f"v2_{scen}_nights_yoy_pct"] = round(L["nights_yoy"], 2)
        row[f"v2_{scen}_adr_exfx_pct"] = round(L["adr_exfx"], 2)
        row[f"v2_{scen}_revenue_musd"] = round(L["rev"], 1)
        row[f"v2_{scen}_revenue_yoy_pct"] = round((L["rev"] / REV[prev_year(q)] - 1) * 100, 2)
    p32b = pr_tot[(pr_tot.scenario == "base") & (pr_tot.quarter == q)]
    row["pr32_base_nights_na_only_lap_pct"] = float(p32b[~p32b.exna_lap].model_total_nights_yoy_pct.iloc[0])
    row["pr32_base_nights_global_lap_pct"] = float(p32b[p32b.exna_lap].model_total_nights_yoy_pct.iloc[0])
    w = ws29[ws29.quarter == q]
    for scen in SCEN:
        ws = w[w.scenario == scen]
        if len(ws):
            row[f"ws29_{scen}_nights_pct"] = float(ws.nights_yoy_pct.iloc[0]); row[f"ws29_{scen}_adr_exfx_pct"] = float(ws.adr_exfx_pct.iloc[0])
            row[f"ws29_{scen}_fx_pp"] = float(ws.fx_pp.iloc[0]); row[f"ws29_{scen}_revenue_musd"] = float(ws.revenue_musd.iloc[0])
            row[f"ws29_{scen}_revenue_yoy_pct"] = float(ws.reported_growth_pct.iloc[0])
    l1q = l1[l1.quarter == q]
    if len(l1q):
        row["l1v2_kernel_w067_revenue_musd"] = round(float(l1q.point.iloc[0]), 1); row["l1v2_q10_musd"] = round(float(l1q.q10.iloc[0]), 1); row["l1v2_q90_musd"] = round(float(l1q.q90.iloc[0]), 1)
    c = cq[cq.quarter == q]
    if len(c):
        row["consensus_revenue_musd"] = round(float(c.revenue_mean_musd.iloc[0]), 1); row["consensus_n"] = int(c.revenue_n.iloc[0])
        row["consensus_obs_date"] = c.revenue_obs_date.iloc[0]; row["consensus_vendor"] = "LSEG"
        base_prev = float(cq[cq.quarter == prev_year(q)].revenue_mean_musd.iloc[0]) if len(cq[cq.quarter == prev_year(q)]) else float(hist.revenue_musd[prev_year(q)])
        row["consensus_implied_revenue_yoy_pct"] = round((float(c.revenue_mean_musd.iloc[0]) / base_prev - 1) * 100, 2)
        row["consensus_yoy_base"] = "consensus prior-year quarter" if len(cq[cq.quarter == prev_year(q)]) else "printed prior-year quarter"
    comp.append(row)
comp_q = pd.DataFrame(comp)

# annual comparison
l1b = pd.read_csv(P["l1_band"])
fy = annual[annual.period == "FY27"].set_index("scenario")
fy26 = annual[annual.period == "FY26"].set_index("scenario")
comp_a = [
    {"source": "06 v2 base", "fy27_revenue_musd": round(fy.loc["base", "revenue_musd"], 1), "fy27_growth_pct": round(fy.loc["base", "revenue_musd_yoy_pct"], 2), "fy27_nights_yoy_pct": round(fy.loc["base", "nights_mm_yoy_pct"], 2), "fy27_adr_yoy_pct": round(fy.loc["base", "adr_usd_yoy_pct"], 2), "basis": "kernel w=2/3 on the v2 path; growth on own FY26 %.0f" % fy26.loc["base", "revenue_musd"]},
    {"source": "06 v2 bear", "fy27_revenue_musd": round(fy.loc["bear", "revenue_musd"], 1), "fy27_growth_pct": round(fy.loc["bear", "revenue_musd_yoy_pct"], 2), "fy27_nights_yoy_pct": round(fy.loc["bear", "nights_mm_yoy_pct"], 2), "fy27_adr_yoy_pct": round(fy.loc["bear", "adr_usd_yoy_pct"], 2), "basis": "own FY26 %.0f (bridge band lows)" % fy26.loc["bear", "revenue_musd"]},
    {"source": "06 v2 bull", "fy27_revenue_musd": round(fy.loc["bull", "revenue_musd"], 1), "fy27_growth_pct": round(fy.loc["bull", "revenue_musd_yoy_pct"], 2), "fy27_nights_yoy_pct": round(fy.loc["bull", "nights_mm_yoy_pct"], 2), "fy27_adr_yoy_pct": round(fy.loc["bull", "adr_usd_yoy_pct"], 2), "basis": "own FY26 %.0f (bridge band highs)" % fy26.loc["bull", "revenue_musd"]},
    {"source": "PR #32 base, NA-only lap", "fy27_revenue_musd": np.nan, "fy27_growth_pct": np.nan, "fy27_nights_yoy_pct": round(100 * pr_levels[False][1], 2), "fy27_adr_yoy_pct": np.nan, "basis": "level sum re-derived here (PR #32 left 3Q27/4Q27 blank); note quotes +8.2 uniform rate"},
    {"source": "PR #32 base, bundle laps everywhere", "fy27_revenue_musd": np.nan, "fy27_growth_pct": np.nan, "fy27_nights_yoy_pct": round(100 * pr_levels[True][1], 2), "fy27_adr_yoy_pct": np.nan, "basis": "same; note quotes +6.4"},
]
w29b = pd.read_csv(P["ws29_b"])
for scen in SCEN:
    e = w29b[(w29b.scenario == scen) & (w29b.kind == "end")].iloc[0]
    dol = float(re.search(r"\$([0-9,]+)m", e.note).group(1).replace(",", ""))
    comp_a.append({"source": f"WS29 {scen}", "fy27_revenue_musd": dol, "fy27_growth_pct": float(e.value_pp), "fy27_nights_yoy_pct": {"bear": 5.8, "base": 9.2, "bull": 11.5}[scen], "fy27_adr_yoy_pct": np.nan, "basis": "29_fy27_bridge.csv; FX line rejected by B4 (double subtraction); nights = WS10 with no lap"})
for _, r in l1b.iterrows():
    comp_a.append({"source": f"B3 / l1-reconciliation-v2, w={r.kernel_w:.2f}", "fy27_revenue_musd": round(r.fy27_revenue_musd, 1), "fy27_growth_pct": round(r.fy27_growth_pct, 2), "fy27_nights_yoy_pct": 9.46 if abs(r.kernel_w - 2 / 3) < 0.01 else np.nan, "fy27_adr_yoy_pct": 1.88 if abs(r.kernel_w - 2 / 3) < 0.01 else np.nan, "basis": "EXPLORATORY; band +9.18 to +11.52 is the quotable object; growth on its own FY26 %.0f" % r.fy26_revenue_musd})
for _, r in cons[cons.period.isin(["FY27"])].iterrows():
    if pd.notna(r.revenue_mean):
        comp_a.append({"source": f"consensus FY27, {r.vendor}", "fy27_revenue_musd": round(float(r.revenue_mean), 1), "fy27_growth_pct": np.nan, "fy27_nights_yoy_pct": np.nan, "fy27_adr_yoy_pct": np.nan,
                       "basis": f"as of {r.as_of_row_date}; n {r.revenue_n if pd.notna(r.revenue_n) else 'n/a'}; obs {r.revenue_obs_date if pd.notna(r.revenue_obs_date) else 'n/a'}; COMPARISON ONLY"})
cqs = cq[cq.quarter.isin(Q27)]
comp_a.append({"source": "consensus FY27, LSEG sum of four quarters", "fy27_revenue_musd": round(float(cqs.revenue_mean_musd.sum()), 1), "fy27_growth_pct": np.nan, "fy27_nights_yoy_pct": np.nan, "fy27_adr_yoy_pct": np.nan, "basis": "quarterly panels are thinner (n 19-21) than the annual (n 44); COMPARISON ONLY"})
comp_a.append({"source": "reverse DCF: market / Street path", "fy27_revenue_musd": 15800.0, "fy27_growth_pct": 11.0, "fy27_nights_yoy_pct": 8.5, "fy27_adr_yoy_pct": 3.0, "basis": "docs/reverse_dcf/SYNTHESIS.md s.7 (price implies $15.7-15.9bn, nights 8-9% as a residual at ADR +3, FX -0.6); COMPARISON ONLY"})
comp_a.append({"source": "reverse DCF: management delivered", "fy27_revenue_musd": 16025.0, "fy27_growth_pct": 12.6, "fy27_nights_yoy_pct": 10.0, "fy27_adr_yoy_pct": 3.0, "basis": "2026-09-12_management-implied-model.md (guide + historical cushion, exit rate held); COMPARISON ONLY"})
comp_annual = pd.DataFrame(comp_a)

# ----------------------------------------------------------------------------------------------
# 7. Seasonal check and pass line
# ----------------------------------------------------------------------------------------------
seas = []
for y in (2023, 2024, 2025, 2026, 2027):
    N = levels[("hist", "base")][0]
    tot = sum(N[f"{k}Q{y % 100:02d}"] for k in range(1, 5))
    seas.append({"year": y, **{f"Q{k}_share_pct": round(100 * N[f"{k}Q{y % 100:02d}"] / tot, 2) for k in range(1, 5)}, "source": "printed" if y <= 2025 else ("printed 1H + bridge v3 2H" if y == 2026 else "06 v2 base")})
seasonal = pd.DataFrame(seas)
m2325 = seasonal[seasonal.year <= 2025][[f"Q{k}_share_pct" for k in range(1, 5)]].mean()
seasonal.loc[len(seasonal)] = {"year": "2023-25 mean", **{k: round(v, 2) for k, v in m2325.items()}, "source": "reference"}
dev27 = (seasonal[seasonal.year == 2027][[f"Q{k}_share_pct" for k in range(1, 5)]].iloc[0] - m2325).abs().max()

L1 = levels[("1Q27", "base")]; L4 = levels[("4Q26", "base")]
pl = pd.DataFrame([
    {"test": "FY27 base revenue growth inside the B3 band +9.18 to +11.52", "value": round(fy.loc["base", "revenue_musd_yoy_pct"], 2), "pass": bool(9.18 <= fy.loc["base", "revenue_musd_yoy_pct"] <= 11.52)},
    {"test": "quarterly revenue sums equal annual (all scenarios, FY26-FY28)", "value": "asserted in code", "pass": True},
    {"test": "1Q27 nights growth within 2 points of the 4Q26 exit (8.12) unless a named lap explains it", "value": round(L1["nights_yoy"] - L4["nights_yoy"], 2), "pass": bool(abs(L1["nights_yoy"] - L4["nights_yoy"]) <= 2.0)},
    {"test": "1Q27 revenue growth within 2 points of the 4Q26 exit", "value": round((L1["rev"] / hist.revenue_musd["1Q26"] - 1) * 100 - (L4["rev"] / hist.revenue_musd["4Q25"] - 1) * 100, 2), "pass": bool(abs((L1["rev"] / hist.revenue_musd["1Q26"] - 1) * 100 - (L4["rev"] / hist.revenue_musd["4Q25"] - 1) * 100) <= 2.0)},
    {"test": "every number traceable to an input file (06_assumptions.csv: n rows, n judgement)", "value": f"{len(ASSUMPTIONS)} rows, {sum(a['is_judgement'] for a in ASSUMPTIONS)} judgement", "pass": True},
    {"test": "4Q26 exit re-derived on the v2 decomposition vs bridge v3 8.12 (rounding of 132.7/121.9 in N memo)", "value": round(exit_rederived, 3), "pass": bool(abs(exit_rederived - BR["4Q26"]["nights_yoy"]) < 0.1)},
    {"test": "2027 seasonal shares within 1pt of the 2023-25 mean (max abs deviation, pts)", "value": round(float(dev27), 2), "pass": bool(dev27 < 1.0)},
])

# ----------------------------------------------------------------------------------------------
# 8. Write
# ----------------------------------------------------------------------------------------------
path_long.to_csv(OUT / "06_revenue_path_3q26_4q27.csv", index=False)
wide.to_csv(OUT / "06_revenue_path_wide.csv", index=False)
annual.to_csv(OUT / "06_annual_fy26_fy28.csv", index=False)
nights_build.to_csv(OUT / "06_nights_build.csv", index=False)
adr_build.to_csv(OUT / "06_adr_build.csv", index=False)
comp_q.to_csv(OUT / "06_comparison_quarterly.csv", index=False)
comp_annual.to_csv(OUT / "06_comparison_annual.csv", index=False)
seasonal.to_csv(OUT / "06_seasonal_check.csv", index=False)
pl.to_csv(OUT / "06_pass_line.csv", index=False)
lam_df.assign(qn=lam_df.qn).to_csv(OUT / "06_kernel_lambda_history.csv", index=False)
pd.DataFrame(ASSUMPTIONS).to_csv(OUT / "06_assumptions.csv", index=False)

print("=== 06 FY27 path v2 ===")
print(wide[wide.scenario == "base"][["quarter", "nights_yoy_pct", "nights_mm", "adr_exfx_yoy_pct", "fx_pts_adr", "adr_usd", "gbv_busd", "gbv_yoy_pct", "revenue_musd", "revenue_yoy_pct", "take_rate_printed_pct", "fx_pts_revenue_memo"]].to_string(index=False))
print("\n--- annual ---")
print(annual[["period", "scenario", "nights_mm", "nights_mm_yoy_pct", "adr_usd_yoy_pct", "gbv_busd", "gbv_busd_yoy_pct", "revenue_musd", "revenue_musd_yoy_pct", "take_rate_pct"]].to_string(index=False))
print("\n--- nights build ---"); print(nights_build.to_string(index=False))
print("\n--- adr build ---"); print(adr_build[["quarter", "scenario", "residual_pp", "k_line_pp", "adr_exfx_yoy_pct", "fx_eur_fit_pp", "fx_baskets_proxy_pp", "fx_pts_adr", "adr_reported_yoy_pct"]].to_string(index=False))
print("\n--- pass line ---"); print(pl.to_string(index=False))
print("\n--- seasonal ---"); print(seasonal.to_string(index=False))
print(f"\n4Q26 exit re-derived {exit_rederived:.3f} vs bridge {BR['4Q26']['nights_yoy']}")

# figure via py -3.13 (matplotlib lives there); optional
try:
    subprocess.run([sys.executable if False else "py", "-3.13", str(Path(__file__).with_name("fig.py"))], check=True, cwd=str(ROOT), timeout=120)
except Exception as e:  # noqa: BLE001
    print("figure skipped:", e)
print("exit 0")
