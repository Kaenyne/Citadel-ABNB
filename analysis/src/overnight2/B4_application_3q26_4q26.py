"""B4: apply the relative-strength indices to 3Q26 and 4Q26.

Produces, under FX observed to the latest FRED publication and flat spot thereafter:
  (i)   direction of the cross-border share of gross nights
  (ii)  the FX-mix component of each region's nights growth differential
  (iii) the implied contribution to total nights growth and to reported ADR via mix
  (iv)  a refreshed FX translation schedule for 3Q26 / 4Q26 revenue and ADR using the
        existing WS05 elasticities and the WS28 hedge line

Comparison column only: the reconciled team nights baseline 9.9% (3Q26) / 8.9% (4Q26).

Run: py -3.13 analysis/src/overnight2/B4_application_3q26_4q26.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\krish\citadel-abnb-overnight2")
MAIN = Path(r"C:\Users\krish\citadel-abnb")
OUT = ROOT / "data" / "processed" / "overnight2" / "B"
REGIONS = ["na", "emea", "latam", "apac"]

IDX = pd.read_csv(OUT / "B_relative_strength_quarterly.csv", index_col=0)
FWD = pd.read_csv(OUT / "B_forward_flat_spot_indices.csv", index_col=0)
DAILY = pd.read_csv(OUT / "B_fx_daily_usd_per_unit.csv", index_col=0, parse_dates=True)
META = json.loads((OUT / "B_fx_meta.json").read_text())
FITS = pd.read_csv(OUT / "B_mix_fits.csv")
LAST = pd.Timestamp(META["latest_fred_fx_observation"])

# ---------------------------------------------------------------- inputs block
# Corrected regional nights shares and regional ADR levels. Sources:
#   research/notes/2026-09-07_adr-decomposition.md section 5 correction 1 and
#   data/processed/adr/01_regional_annual.csv (FY2025 10-K geographic mix table),
#   data/processed/adr/04_regional_quarterly.csv (2Q26 rebuilt shares).
# WS10's 10_regional_forecast.csv shares (NA 28.8 / EMEA 39.7 / LatAm 15.1 /
# APAC 16.3) inherit the swapped LatAm/APAC ADR index and are NOT used here.
SHARE_2Q26 = {"na": 0.28255, "emea": 0.41550, "latam": 0.17862, "apac": 0.12333}
ADR_2025 = {"na": 255.03, "emea": 158.89, "latam": 94.91, "apac": 118.20}
ADR_GLOBAL_2025 = 171.24
# 2Q26 disclosed regional nights growth, WS27 bucket placement (27_regional_bucket_check)
NIGHTS_YOY_2Q26 = {"na": 7.0, "emea": 7.4, "latam": 19.0, "apac": 17.0}
TOTAL_NIGHTS_YOY_2Q26 = 10.34
TEAM_BASELINE = {"3Q26": 9.9, "4Q26": 8.9}

# Elasticity of the regional nights growth differential to the cross-border
# purchasing-power index, from B_mix_fits.csv (pooled, both sides demeaned by region).
ELAST = {
    "base": 0.1134,   # from_4Q24_disclosed_era, n 28, r 0.398, perm p 0.038
    "low": 0.0854,    # ex_reopening / from_1Q24, n 40, r 0.234, perm p 0.156 (not significant)
    "high": 0.2106,   # post22, n 64, r 0.229, perm p 0.068
}

# WS05 fitted FX translation elasticities (data/processed/overnight/05_fx_fits.csv,
# window ex21, n 17) and the WS28 hedge line (28_fx_hedge_forward.csv).
ADR_FX_EUR = (-0.5687, 0.4512)        # intercept, slope on EUR/USD y/y %
ADR_FX_USDBROAD = (0.5246, -0.7154)   # intercept, slope on broad USD y/y %
REV_FX_EUR_AVG12 = (-0.6371, 0.4133)  # on mean of EUR/USD y/y in the two prior quarters
HEDGE_PP = {"3Q26": -0.21, "4Q26": -0.21}

# --------------------------------------------------- arithmetic FX y/y, actual+flat
ccy_cols = [c for c in DAILY.columns if c != "USD"]


def qavg(start, end, flat_from=None):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    sub = DAILY.loc[start:min(end, LAST), ccy_cols]
    days = pd.date_range(max(LAST + pd.Timedelta(days=1), start), end, freq="B")
    if flat_from is not None and len(days):
        spot = DAILY.loc[LAST, ccy_cols]
        sub = pd.concat([sub, pd.DataFrame([spot] * len(days), index=days)])
    return sub.mean()


QS = {
    "2025Q3": qavg("2025-07-01", "2025-09-30"),
    "2025Q4": qavg("2025-10-01", "2025-12-31"),
    "2026Q1": qavg("2026-01-01", "2026-03-31"),
    "2026Q2": qavg("2026-04-01", "2026-06-30"),
    "2026Q3": qavg("2026-07-01", "2026-09-30", flat_from=True),
    "2026Q4": qavg("2026-10-01", "2026-12-31", flat_from=True),
}
PREV = {"2026Q1": "2025Q1", "2026Q2": "2025Q2", "2026Q3": "2025Q3", "2026Q4": "2025Q4"}
QS["2025Q1"] = qavg("2025-01-01", "2025-03-31")
QS["2025Q2"] = qavg("2025-04-01", "2025-06-30")

fx_rows = []
for q, prv in PREV.items():
    eur = 100 * (QS[q]["EUR"] / QS[prv]["EUR"] - 1)
    brd = 100 * (QS[q]["USD_BROAD"] / QS[prv]["USD_BROAD"] - 1)
    fx_rows.append({"quarter": q, "eurusd_level": round(QS[q]["EUR"], 4),
                    "eurusd_yoy_pct": round(eur, 3),
                    "usd_broad_yoy_pct": round(brd, 3)})
FX = pd.DataFrame(fx_rows).set_index("quarter")
FX["adr_fx_pp_from_eur"] = (ADR_FX_EUR[0] + ADR_FX_EUR[1] * FX.eurusd_yoy_pct).round(2)
FX["adr_fx_pp_from_usd_broad"] = (ADR_FX_USDBROAD[0]
                                  + ADR_FX_USDBROAD[1] * FX.usd_broad_yoy_pct).round(2)
eur_yoy = FX["eurusd_yoy_pct"]
avg12 = pd.Series({q: (eur_yoy.get(p1, np.nan) + eur_yoy.get(p2, np.nan)) / 2
                   for q, p1, p2 in [("2026Q3", "2026Q2", "2026Q1"),
                                     ("2026Q4", "2026Q3", "2026Q2")]})
FX["eurusd_yoy_avg_prior_2q"] = avg12.round(3)
FX["revenue_fx_pp_gross"] = (REV_FX_EUR_AVG12[0]
                             + REV_FX_EUR_AVG12[1] * FX.eurusd_yoy_avg_prior_2q).round(2)
FX["hedge_pp"] = [HEDGE_PP.get({"2026Q3": "3Q26", "2026Q4": "4Q26"}.get(q), np.nan)
                  for q in FX.index]
FX["revenue_fx_pp_after_hedge"] = (FX.revenue_fx_pp_gross + FX.hedge_pp.fillna(0)).round(2)

# Third ADR-FX estimate, built bottom-up from the four destination baskets rather
# than from a single cross. GBV shares are FY2025 (data/processed/adr/
# 01_regional_annual.csv); pass-throughs are the WS10 fits re-tested in the ADR
# decomposition note (EMEA 1.04 vs 1.07 re-fit, LatAm 0.62 vs 0.63, APAC 0.86 vs
# 0.82, NA not identified and carried at 1.0).
DEST_BASKET = {
    "na": {"USD": 0.90, "CAD": 0.08, "MXN": 0.02},
    "emea": {"EUR": 0.70, "GBP": 0.25, "USD": 0.05},
    "latam": {"BRL": 0.55, "MXN": 0.38, "USD": 0.07},
    "apac": {"AUD": 0.55, "JPY": 0.20, "KRW": 0.10, "INR": 0.07, "USD": 0.08},
}
GBV_SHARE_2025 = {"na": 0.4415, "emea": 0.3743, "latam": 0.0936, "apac": 0.0907}
PASSTHROUGH = {"na": 1.00, "emea": 1.04, "latam": 0.62, "apac": 0.86}


def basket_yoy(q, prv, weights):
    num = sum(w * np.log(QS[q][c] if c != "USD" else 1.0) for c, w in weights.items())
    den = sum(w * np.log(QS[prv][c] if c != "USD" else 1.0) for c, w in weights.items())
    return 100.0 * (np.exp(num - den) - 1.0)


for q, prv in PREV.items():
    tot = 0.0
    for r in DEST_BASKET:
        b = basket_yoy(q, prv, DEST_BASKET[r])
        FX.loc[q, f"basket_yoy_pct_{r}"] = round(b, 3)
        tot += GBV_SHARE_2025[r] / sum(GBV_SHARE_2025.values()) * PASSTHROUGH[r] * b
    FX.loc[q, "adr_fx_pp_from_regional_baskets"] = round(tot, 2)
FX.to_csv(OUT / "B_fx_translation_schedule_refresh.csv")

# ----------------------------------------- backtest of the three ADR-FX estimators
# against the disclosed reported-minus-ex-FX ADR gap in the letters.
MACRO = pd.read_csv(MAIN / "data" / "processed" / "overnight"
                    / "05_macro_quarterly_panel.csv").set_index("quarter")
bt = []
allq = [f"{y}Q{k}" for y in range(2022, 2027) for k in (1, 2, 3, 4)]
for q in allq:
    prv = f"{int(q[:4]) - 1}Q{q[-1]}"
    if q not in MACRO.index or pd.isna(MACRO.loc[q, "adr_fx_effect"]):
        continue
    s = pd.Timestamp(f"{q[:4]}-{ {'1':'01','2':'04','3':'07','4':'10'}[q[-1]] }-01")
    e = s + pd.offsets.QuarterEnd(0)
    ps = s - pd.DateOffset(years=1)
    pe = ps + pd.offsets.QuarterEnd(0)
    if e > LAST:
        continue
    QS[q], QS[prv] = qavg(s, e), qavg(ps, pe)
    eur = 100 * (QS[q]["EUR"] / QS[prv]["EUR"] - 1)
    brd = 100 * (QS[q]["USD_BROAD"] / QS[prv]["USD_BROAD"] - 1)
    bask = sum(GBV_SHARE_2025[r] / sum(GBV_SHARE_2025.values()) * PASSTHROUGH[r]
               * basket_yoy(q, prv, DEST_BASKET[r]) for r in DEST_BASKET)
    bt.append({"quarter": q, "adr_fx_disclosed_pp": float(MACRO.loc[q, "adr_fx_effect"]),
               "est_from_eur": round(ADR_FX_EUR[0] + ADR_FX_EUR[1] * eur, 3),
               "est_from_usd_broad": round(ADR_FX_USDBROAD[0] + ADR_FX_USDBROAD[1] * brd, 3),
               "est_from_regional_baskets": round(bask, 3)})
BT = pd.DataFrame(bt)
for c in ["est_from_eur", "est_from_usd_broad", "est_from_regional_baskets"]:
    BT[f"err_{c}"] = (BT[c] - BT.adr_fx_disclosed_pp).round(3)
BT.to_csv(OUT / "B_adr_fx_estimator_backtest.csv", index=False)
RMSE = {c: round(float(np.sqrt(np.mean(BT[f"err_{c}"] ** 2))), 3)
        for c in ["est_from_eur", "est_from_usd_broad", "est_from_regional_baskets"]}

# --------------------------------------------------------- mix application
mean_ipp = {}
for label, src in [("2Q26", IDX.loc["2Q26"]), ("3Q26", FWD.loc["3Q26_flat_spot"]),
                   ("4Q26", FWD.loc["4Q26_flat_spot"])]:
    mean_ipp[label] = sum(SHARE_2Q26[r] * src[f"ipp_xb_{r}"] for r in REGIONS)

mix_rows = []
for label, src in [("2Q26", IDX.loc["2Q26"]), ("3Q26", FWD.loc["3Q26_flat_spot"]),
                   ("4Q26", FWD.loc["4Q26_flat_spot"])]:
    for r in REGIONS:
        ipp = float(src[f"ipp_xb_{r}"])
        rel = ipp - mean_ipp[label]   # demeaned so the mix term reallocates, not creates
        row = {"period": label, "region": r, "ipp_xb": round(ipp, 3),
               "ipp_xb_relative_to_share_weighted_mean": round(rel, 3),
               "nights_share_pct": round(100 * SHARE_2Q26[r], 2)}
        for k, e in ELAST.items():
            row[f"fx_mix_differential_pp_{k}"] = round(e * rel, 3)
        mix_rows.append(row)
MIX = pd.DataFrame(mix_rows)
# swing versus 2Q26: the incremental FX-mix effect the print will carry
base2q = MIX[MIX.period == "2Q26"].set_index("region")
for k in ELAST:
    MIX[f"fx_mix_swing_vs_2q26_pp_{k}"] = [
        round(r[f"fx_mix_differential_pp_{k}"]
              - base2q.loc[r["region"], f"fx_mix_differential_pp_{k}"], 3)
        for _, r in MIX.iterrows()]
MIX.to_csv(OUT / "B_mix_application_regional.csv", index=False)

# ------------------------------- total nights and reported ADR mix arithmetic
tot_rows = []
for label in ("3Q26", "4Q26"):
    sub = MIX[MIX.period == label].set_index("region")
    for k in ELAST:
        contrib = sum(SHARE_2Q26[r] * sub.loc[r, f"fx_mix_swing_vs_2q26_pp_{k}"]
                      for r in REGIONS)
        # reported-ADR mix term: regional nights shares move with the differential,
        # valued at 2025 regional ADR levels. Nights growth = 2Q26 disclosed rate
        # plus the FX-mix swing; the mix term is the change in the nights-weighted
        # ADR blend that those growth rates imply, holding regional ADR fixed.
        g = {r: NIGHTS_YOY_2Q26[r] + sub.loc[r, f"fx_mix_swing_vs_2q26_pp_{k}"]
             for r in REGIONS}
        g0 = dict(NIGHTS_YOY_2Q26)
        def blend(growth):
            w = {r: SHARE_2Q26[r] * (1 + growth[r] / 100) for r in REGIONS}
            s = sum(w.values())
            return sum(w[r] / s * ADR_2025[r] for r in REGIONS)
        blend_with = blend(g)
        blend_without = blend(g0)
        base_blend = sum(SHARE_2Q26[r] * ADR_2025[r] for r in REGIONS)
        tot_rows.append({
            "period": label, "elasticity_case": k,
            "elasticity_pp_per_pp": ELAST[k],
            "share_weighted_fx_mix_swing_pp_on_total_nights": round(contrib, 3),
            "reported_adr_mix_term_total_pp": round(100 * (blend_without / base_blend - 1), 3),
            "reported_adr_mix_term_fx_increment_pp": round(
                100 * (blend_with / blend_without - 1), 3),
            "team_baseline_nights_yoy_pct": TEAM_BASELINE[label],
            "nights_yoy_with_fx_mix_overlay_pct": round(
                TEAM_BASELINE[label] + contrib, 2),
        })
TOT = pd.DataFrame(tot_rows)
TOT.to_csv(OUT / "B_mix_application_total.csv", index=False)

# --------------------------------------------------- cross-border direction card
cb_rows = []
for label, src in [("3Q26", FWD.loc["3Q26_flat_spot"]), ("4Q26", FWD.loc["4Q26_flat_spot"])]:
    disp = float(src["ipp_dispersion_sd"])
    prev = float(IDX.loc["2Q26", "ipp_dispersion_sd"])
    cb_rows.append({
        "period": label,
        "ipp_dispersion_sd": round(disp, 3),
        "ipp_dispersion_sd_2q26": round(prev, 3),
        "ipp_xb_global_equal_weight": round(
            float(np.mean([src[f"ipp_xb_{r}"] for r in REGIONS])), 3),
        "ipp_xb_global_equal_weight_2q26": round(
            float(np.mean([IDX.loc["2Q26", f"ipp_xb_{r}"] for r in REGIONS])), 3),
        "direction_call": ("flat to marginally lower cross-border share: the "
                           "share-weighted cross-border purchasing-power index is "
                           "still negative and the dispersion across destinations "
                           "narrows versus 2Q26, so FX gives no push either way"),
        "identified": "no: best fit r 0.51, perm p 0.07, n 13 on a series that stops at 1Q24",
    })
CB = pd.DataFrame(cb_rows)
CB.to_csv(OUT / "B_cross_border_direction_card.csv", index=False)

print("=== ADR-FX estimator backtest (disclosed letter FX effect on ADR) ===")
print(BT.to_string(index=False))
print("RMSE pp:", RMSE)
print("\n=== refreshed FX translation schedule ===")
print(FX.to_string())
print("\n=== regional FX-mix overlay ===")
print(MIX.to_string(index=False))
print("\n=== total nights and ADR mix ===")
print(TOT.to_string(index=False))
print("\n=== cross-border direction ===")
print(CB.to_string(index=False))
print("\nlatest FRED FX observation used:", META["latest_fred_fx_observation"])
