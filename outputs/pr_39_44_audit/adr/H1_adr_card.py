"""
WS-H: the team's 3Q26 and 4Q26 ADR card.

Builds, from pieces that already exist on main and in the overnight-2 worktree:
  1. the disclosed ADR history 1Q23-2Q26 decomposed into FX, geographic mix,
     unit-size (party-size), length-of-stay mix, new-business (seats/hotels)
     dilution, interaction, and a visible residual like-for-like pricing term;
  2. two independent routes to 3Q26 / 4Q26 ex-FX ADR (component build; H1-to-H2
     seasonal transition), plus the FX effect under both WS-B estimators;
  3. sensitivities to a 1 pp move in each component, on reported ADR, on GBV and
     on revenue at the team nights baseline;
  4. a comparison against management's 6 Aug 2026 Q3 commentary and against an
     ADR implied by the published revenue consensus (no ADR consensus exists).

No new raw data. Nothing is written outside this worktree.

Run: py -3.13 analysis/src/q3nowcast/H1_adr_card.py
"""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

MAIN = r"C:\Users\krish\citadel-abnb"
ON2 = r"C:\Users\krish\citadel-abnb-overnight2"
HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(HERE, "data", "processed", "q3nowcast", "H")
os.makedirs(OUT, exist_ok=True)

REGIONS = ["na", "emea", "latam", "apac"]
QORDER = [f"{q}Q{y}" for y in range(19, 28) for q in range(1, 5)]
QORDER = [f"{q}Q{str(y)[-2:]}" for y in range(2019, 2028) for q in range(1, 5)]


def qkey(q: str) -> int:
    return QORDER.index(q)


def lag4(q: str) -> str:
    return QORDER[qkey(q) - 4]


# ----------------------------------------------------------------------------
# 1. disclosed history and the component decomposition, by quarter
# ----------------------------------------------------------------------------

hist = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "02b_adr_history_extended.csv"))
hist = hist[["quarter", "nights_m", "gbv_busd", "adr_usd", "adr_yoy_reported_pct",
             "fx_pts_adr_final", "adr_yoy_exfx_final", "basis"]].copy()
hist.columns = ["quarter", "nights_m", "gbv_busd", "adr_usd", "adr_yoy_reported_pp",
                "fx_effect_pp", "adr_exfx_yoy_pp", "fx_basis"]

# --- geographic mix, computed quarterly from the regional panel ---------------
reg = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "04_regional_quarterly_wide.csv"))
reg = reg.set_index("quarter")

geo_rows = []
for q in reg.index:
    if qkey(q) - 4 < 0 or lag4(q) not in reg.index:
        continue
    p = lag4(q)
    a0, g, s1, s0 = {}, {}, {}, {}
    ok = True
    for r in REGIONS:
        a0[r] = reg.at[p, f"adr_{r}_usd_anchored"]
        g[r] = reg.at[q, f"adr_yoy_exfx_{r}_pct"]
        s1[r] = reg.at[q, f"nights_share_{r}_pct"]
        s0[r] = reg.at[p, f"nights_share_{r}_pct"]
        if any(pd.isna(x) for x in (a0[r], g[r], s1[r], s0[r])):
            ok = False
    if not ok:
        continue
    # constant-currency: year-ago regional ADR levels grown by the disclosed
    # regional ex-FX rate, aggregated on year-ago vs current nights shares.
    base = sum(s0[r] * a0[r] for r in REGIONS)
    within = sum(s0[r] * a0[r] * (1 + g[r] / 100) for r in REGIONS) / base - 1
    total = sum(s1[r] * a0[r] * (1 + g[r] / 100) for r in REGIONS) / sum(s1[r] * a0[r] for r in REGIONS) * \
        (sum(s1[r] * a0[r] for r in REGIONS) / sum(s0[r] * a0[r] for r in REGIONS)) - 1
    # the line above equals sum(s1 A0 (1+g)) / sum(s0 A0) - 1
    geo_rows.append({
        "quarter": q,
        "within_region_exfx_pp": 100 * within,
        "blended_exfx_reconstructed_pp": 100 * total,
        "geo_mix_pp": 100 * (total - within),
        "basis_na": reg.at[q, "basis_adr_na"],
    })
geo = pd.DataFrame(geo_rows)

# --- unit-size (party-size) term, quarterly ----------------------------------
ps = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "13_party_size_adr_quarterly.csv"))
ps = ps[ps.region == "global"][["quarter", "cap_yoy_pct", "size_term_pp"]].rename(
    columns={"size_term_pp": "unit_size_pp", "cap_yoy_pct": "booked_capacity_yoy_pct"})

# --- length-of-stay mix term, quarterly --------------------------------------
los = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "14b_los_adr_term.csv"))
los = los[los.scope == "global_quarterly_yoy"][["period", "los_mix_pp", "tier"]].rename(
    columns={"period": "quarter", "tier": "los_tier"})

# --- new-business (seats + hotels) dilution ----------------------------------
# annual, base case; spread uniformly across quarters of the year.
sd = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "15_seats_dilution_annual.csv"))
sd_base = sd[sd.case_business == "base"].set_index("year")["dilution_drag_pp"].to_dict()

# --- interaction term, annual from the full decomposition --------------------
full = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "07_full_decomposition.csv"))
inter = full.set_index("year")["interaction_pp"].to_dict()

h = hist.merge(geo, on="quarter", how="left").merge(ps, on="quarter", how="left").merge(los, on="quarter", how="left")
h["year"] = h["quarter"].str[-2:].astype(int) + 2000
h["new_business_pp"] = h["year"].map(sd_base)
h["interaction_pp"] = h["year"].map(inter)
h = h[h["quarter"].map(lambda q: qkey(q) >= qkey("1Q23"))].copy()

# 14b stops at 4Q25 (no 2026 stay-length disclosure and no 2026 ALOS) and 07 is
# annual to 2025. Fill 1Q26/2Q26 with the workbook's base LOS term (+0.30pp) and
# the 2025 interaction (-0.10pp) so the 2026 residual is comparable with history.
# ASSUMED, flagged in the output.
h["term_fill_2026"] = ""
m26 = h["quarter"].isin(["1Q26", "2Q26"])
h.loc[m26 & h["los_mix_pp"].isna(), "term_fill_2026"] = "los=+0.30 assumed; interaction=-0.10 assumed"
h.loc[m26, "los_mix_pp"] = h.loc[m26, "los_mix_pp"].fillna(0.30)
h.loc[m26, "interaction_pp"] = h.loc[m26, "interaction_pp"].fillna(-0.10)

comp_cols = ["geo_mix_pp", "unit_size_pp", "los_mix_pp", "new_business_pp", "interaction_pp"]
h["components_sum_pp"] = h[comp_cols].sum(axis=1, min_count=1)
h["residual_pricing_pp"] = h["adr_exfx_yoy_pp"] - h["components_sum_pp"]
h["identity_check_pp"] = h["adr_yoy_reported_pp"] - (h["fx_effect_pp"] + h["adr_exfx_yoy_pp"])
h["geo_recon_gap_pp"] = h["blended_exfx_reconstructed_pp"] - h["adr_exfx_yoy_pp"]

hist_out = h[["quarter", "adr_usd", "nights_m", "gbv_busd", "adr_yoy_reported_pp", "fx_effect_pp",
              "adr_exfx_yoy_pp", "identity_check_pp", "geo_mix_pp", "unit_size_pp", "los_mix_pp",
              "new_business_pp", "interaction_pp", "components_sum_pp", "residual_pricing_pp",
              "within_region_exfx_pp", "blended_exfx_reconstructed_pp", "geo_recon_gap_pp",
              "booked_capacity_yoy_pct", "los_tier", "fx_basis", "term_fill_2026"]].copy()
hist_out.to_csv(os.path.join(OUT, "adr_history_components.csv"), index=False)

# ----------------------------------------------------------------------------
# 2. FX: verify WS-B's schedule against a fresh FRED pull, then carry it
# ----------------------------------------------------------------------------
fxs = pd.read_csv(os.path.join(ON2, "data", "processed", "overnight2", "B",
                               "B_fx_translation_schedule_refresh.csv")).set_index("quarter")
fxb = pd.read_csv(os.path.join(ON2, "data", "processed", "overnight2", "B",
                               "B_adr_fx_estimator_backtest.csv"))
rmse = {c.replace("err_", ""): float(np.sqrt((fxb[c] ** 2).mean()))
        for c in fxb.columns if c.startswith("err_")}

FX = {}
for q, qq in (("3Q26", "2026Q3"), ("4Q26", "2026Q4")):
    FX[q] = {
        "eur_fit": float(fxs.at[qq, "adr_fx_pp_from_eur"]),
        "baskets": float(fxs.at[qq, "adr_fx_pp_from_regional_baskets"]),
        "usd_broad": float(fxs.at[qq, "adr_fx_pp_from_usd_broad"]),
    }
    lo, hi = sorted([FX[q]["eur_fit"], FX[q]["baskets"]])
    FX[q]["lo"], FX[q]["hi"] = lo, hi
    FX[q]["point"] = 0.5 * (lo + hi)

# ----------------------------------------------------------------------------
# 3. route (a): component build for 3Q26 and 4Q26 ex-FX ADR
# ----------------------------------------------------------------------------
C = pd.read_csv(os.path.join(ON2, "data", "processed", "overnight2", "C", "C5_total_and_adr_mix.csv"))
geo_fc = {}
for q in ("3Q26", "4Q26"):
    v = C[(C.period == q) & (C.weights == "10K_FY2025_shares")]["adr_geographic_mix_pp"]
    geo_fc[q] = (float(v.min()), float(v.mean()), float(v.max()))

ps_fc = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "13_party_size_adr_forecast.csv"))
ps_fc = ps_fc[ps_fc.region == "global_nights_weighted"].set_index("case")["size_term_pp"].to_dict()

sd_q = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "15_seats_dilution_quarterly.csv"))
sd_q = sd_q.set_index(["case_business", "quarter"])["dilution_drag_pp"]

# like-for-like pricing residual: anchored entirely on the reconstruction above.
# lo = trailing 8-quarter mean, base = trailing 4-quarter mean, hi = 1H26 mean.
# No padding is added: the three anchors are the honest spread of the run rate.
res_1h26 = float(h[h.quarter.isin(["1Q26", "2Q26"])]["residual_pricing_pp"].mean())
res_2025 = float(h[h.quarter.str.endswith("25")]["residual_pricing_pp"].mean())
res_8q = float(h[h.quarter.map(lambda q: qkey(q) >= qkey("3Q24"))]["residual_pricing_pp"].mean())
res_4q = float(h[h.quarter.map(lambda q: qkey(q) >= qkey("3Q25"))]["residual_pricing_pp"].mean())

# fee migration: the 1H26 residual already embeds repricing on the migrated
# cohort at roughly a third of listings (a quarter at 1Q26, about half at 2Q26).
# Only the INCREMENTAL penetration is added, so the term is not double counted.
FEE_PEN = {"1H26": 0.375, "3Q26": 0.60, "4Q26": 0.75}   # assumed path to "most" by end-2026
FEE_PER_LISTING = {"base": 0.7, "hi": 3.8}   # % of ADR on the migrated cohort (note 12)
fee_fc = {}
for q in ("3Q26", "4Q26"):
    d_pen = FEE_PEN[q] - FEE_PEN["1H26"]
    fee_fc[q] = {
        "base": d_pen * FEE_PER_LISTING["base"],
        "lo": -0.5 * d_pen / (FEE_PEN["4Q26"] - FEE_PEN["1H26"]),   # scales note 12's -0.5 on 4Q26
        "hi": d_pen * FEE_PER_LISTING["hi"],
    }

LOS_FC = {"bear": 0.0, "base": 0.30, "bull": 0.45}
PRICE_FC = {"lo": res_8q, "base": res_4q, "hi": res_1h26}

rows = []
for q in ("3Q26", "4Q26"):
    terms = {
        "like_for_like_pricing": (PRICE_FC["lo"], PRICE_FC["base"], PRICE_FC["hi"]),
        "geographic_mix": (geo_fc[q][0] - 0.4, geo_fc[q][1], geo_fc[q][2] + 0.1),
        "unit_size_party": (ps_fc["bear"], ps_fc["base"], ps_fc["bull"]),
        "length_of_stay_mix": (LOS_FC["bear"], LOS_FC["base"], LOS_FC["bull"]),
        "new_business_seats": (float(sd_q.loc[("bull", q)]), float(sd_q.loc[("base", q)]),
                               float(sd_q.loc[("bear", q)])),
        "fee_migration_increment": (fee_fc[q]["lo"], fee_fc[q]["base"], fee_fc[q]["hi"]),
        "interaction": (-0.15, -0.10, -0.05),
    }
    for k, (lo, base, hi) in terms.items():
        rows.append({"quarter": q, "term": k, "lo_pp": lo, "point_pp": base, "hi_pp": hi})
comp = pd.DataFrame(rows)

build = {}
for q in ("3Q26", "4Q26"):
    s = comp[comp.quarter == q]
    build[q] = {
        "point": float(s.point_pp.sum()),
        # band: root-sum-square of the half-ranges, not the arithmetic sum of
        # extremes, because the terms are independently sourced.
        "half": float(np.sqrt((((s.hi_pp - s.lo_pp) / 2) ** 2).sum())),
        "arith_lo": float(s.lo_pp.sum()),
        "arith_hi": float(s.hi_pp.sum()),
    }

# ----------------------------------------------------------------------------
# 3b. walk-forward backtest of the component build (BRIEF rule, note 08 protocol)
# Every term uses only information dated before the target quarter: the pricing
# residual, geo mix, unit-size and LOS terms are trailing 4-quarter means, the
# new-business and interaction terms are the prior calendar year's annual value.
# Benchmarks: naive last quarter, same quarter prior year, AR(1) on ex-FX.
# ----------------------------------------------------------------------------
hh = h.set_index("quarter")
bt = []
for q in hh.index:
    i = qkey(q)
    prior = [x for x in hh.index if qkey(x) < i]
    if len(prior) < 5:
        continue
    p4 = prior[-4:]
    yprev = int(q[-2:]) + 2000 - 1
    pred = (hh.loc[p4, "residual_pricing_pp"].mean()
            + hh.loc[p4, "geo_mix_pp"].mean()
            + hh.loc[p4, "unit_size_pp"].mean()
            + hh.loc[p4, "los_mix_pp"].mean()
            + (0.0 if pd.isna(sd_base.get(yprev, np.nan)) else sd_base[yprev])
            + (0.0 if pd.isna(inter.get(yprev, np.nan)) else inter[yprev]))
    act = hh.at[q, "adr_exfx_yoy_pp"]
    naive = hh.at[prior[-1], "adr_exfx_yoy_pp"]
    py = hh.at[prior[-4], "adr_exfx_yoy_pp"] if len(prior) >= 4 else np.nan
    bt.append({"quarter": q, "actual_exfx_pp": act, "component_build_pp": pred,
               "naive_last_q_pp": naive, "prior_year_q_pp": py})
bt = pd.DataFrame(bt)
# AR(1) fitted on the quarters strictly before the backtest window
ar_src = hh["adr_exfx_yoy_pp"].astype(float)
x = ar_src.values[:-1]
y = ar_src.values[1:]
b1, b0 = np.polyfit(x, y, 1)
bt["ar1_pp"] = [b0 + b1 * hh.at[QORDER[qkey(q) - 1], "adr_exfx_yoy_pp"] for q in bt.quarter]
for c in ("component_build", "naive_last_q", "prior_year_q", "ar1"):
    bt[f"err_{c}"] = bt[f"{c}_pp"] - bt["actual_exfx_pp"]
bt_rmse = {c: float(np.sqrt((bt[f"err_{c}"] ** 2).mean()))
           for c in ("component_build", "naive_last_q", "prior_year_q", "ar1")}
bt_ratio = {c: bt_rmse[c] / bt_rmse["naive_last_q"] for c in bt_rmse}
bt["n_obs"] = len(bt)
bt.to_csv(os.path.join(OUT, "adr_exfx_backtest.csv"), index=False)

# ----------------------------------------------------------------------------
# 4. route (b): H1-to-H2 seasonal transition
# ----------------------------------------------------------------------------
H1_EXFX = 4.0   # disclosed 1Q26 and 2Q26 ADR ex-FX, both +4%
TRANS = {"3Q26": (-0.5, -2.0, 1.0), "4Q26": (-0.2, -2.0, 2.0)}  # mean, min, max, 2023-25, n=3
bridge = {q: {"point": H1_EXFX + m, "lo": H1_EXFX + lo, "hi": H1_EXFX + hi}
          for q, (m, lo, hi) in TRANS.items()}

# ----------------------------------------------------------------------------
# 5. the card
# ----------------------------------------------------------------------------
BASE_ADR = {"3Q26": 171.29, "4Q26": 167.51}   # 3Q25 and 4Q25 disclosed
BASE_Q = {"3Q26": "3Q25", "4Q26": "4Q25"}
NIGHTS = {"3Q26": 146.8, "4Q26": 132.7}       # team baseline (comparison input for dollars only)
NIGHTS_YOY = {"3Q26": 9.9, "4Q26": 8.9}

# route (c): the naive benchmark the backtest says is hardest to beat on this
# series - last disclosed ex-FX ADR y/y (2Q26 = +4%), band = its backtest RMSE.
NAIVE = 4.0
naive_half = bt_rmse["naive_last_q"]

card = []
for q in ("3Q26", "4Q26"):
    r_list = [
        ("a_component_build", build[q]["point"], build[q]["point"] - build[q]["half"],
         build[q]["point"] + build[q]["half"]),
        ("b_h1_h2_transition", bridge[q]["point"], bridge[q]["lo"], bridge[q]["hi"]),
        ("c_naive_last_disclosed", NAIVE, NAIVE - naive_half, NAIVE + naive_half),
    ]
    exfx_pt = float(np.mean([r[1] for r in r_list]))
    routes = {r[0]: (r[1], r[2], r[3]) for r in r_list}
    routes["headline_mean_of_routes"] = (exfx_pt, min(r[2] for r in r_list),
                                         max(r[3] for r in r_list))
    for label, (e_pt, e_lo, e_hi) in routes.items():
        # central band: component half-range (root-sum-square) with FX at the
        # midpoint of the two estimators. wide band: route union plus the full
        # FX estimator spread.
        for fxname in ("eur_fit", "baskets", "midpoint"):
            fx = FX[q]["point"] if fxname == "midpoint" else FX[q][fxname]
            rep = e_pt + fx
            c_lo = e_lo + fx
            c_hi = e_hi + fx
            w_lo = e_lo + FX[q]["lo"]
            w_hi = e_hi + FX[q]["hi"]
            card.append({
                "quarter": q, "base_quarter": BASE_Q[q], "base_adr_usd": BASE_ADR[q],
                "route": label, "fx_estimator": fxname, "fx_effect_pp": round(fx, 2),
                "adr_exfx_yoy_pp": round(e_pt, 2), "adr_exfx_lo_pp": round(e_lo, 2),
                "adr_exfx_hi_pp": round(e_hi, 2),
                "adr_reported_yoy_pp": round(rep, 2),
                "adr_reported_central_lo_pp": round(c_lo, 2),
                "adr_reported_central_hi_pp": round(c_hi, 2),
                "adr_reported_wide_lo_pp": round(w_lo, 2),
                "adr_reported_wide_hi_pp": round(w_hi, 2),
                "adr_usd_point": round(BASE_ADR[q] * (1 + rep / 100), 2),
                "adr_usd_central_lo": round(BASE_ADR[q] * (1 + c_lo / 100), 2),
                "adr_usd_central_hi": round(BASE_ADR[q] * (1 + c_hi / 100), 2),
                "nights_baseline_m": NIGHTS[q], "nights_baseline_yoy_pp": NIGHTS_YOY[q],
                "gbv_busd_point": round(BASE_ADR[q] * (1 + rep / 100) * NIGHTS[q] / 1000, 2),
                "gbv_yoy_pp_point": round(100 * ((1 + rep / 100) * (1 + NIGHTS_YOY[q] / 100) - 1), 2),
            })
card = pd.DataFrame(card)
card.to_csv(os.path.join(OUT, "adr_forecast_card.csv"), index=False)

# ----------------------------------------------------------------------------
# 6. sensitivities
# ----------------------------------------------------------------------------
TAKE = {"3Q26": 0.1788, "4Q26": 0.1362}   # 3Q25 4095/22900, 4Q25 2778/20400
REV_BASE = {"3Q26": 4095.0, "4Q26": 2778.0}   # year-ago revenue, $m
hq = card[(card.route == "headline_mean_of_routes") &
          (card.fx_estimator == "midpoint")].set_index("quarter")


def srow(q, term, rng, gbv_m, rev_m):
    return {
        "quarter": q, "term": term,
        "range_pp": round(rng, 2), "half_range_pp": round(rng / 2, 2),
        "adr_reported_pp_per_1pp": 1.0,
        "adr_usd_per_1pp": round(BASE_ADR[q] / 100, 2),
        "gbv_musd_per_1pp": round(gbv_m / 100, 0),
        "rev_musd_per_1pp_same_qtr_take": round(rev_m / 100, 0),
        "rev_growth_pp_per_1pp_same_qtr_take": round((rev_m / 100) / REV_BASE[q] * 100, 2),
        "contribution_to_variance_pct": np.nan,
    }


sens = []
for q in ("3Q26", "4Q26"):
    adr = float(hq.at[q, "adr_usd_point"])
    gbv_m = adr * NIGHTS[q]                       # $m
    rev_m = gbv_m * TAKE[q]
    for t in comp[comp.quarter == q].itertuples():
        sens.append(srow(q, t.term, t.hi_pp - t.lo_pp, gbv_m, rev_m))
    sens.append(srow(q, "fx_estimator_choice", FX[q]["hi"] - FX[q]["lo"], gbv_m, rev_m))
    sens.append(srow(q, "h1h2_vs_component_route_gap",
                     abs(build[q]["point"] - bridge[q]["point"]), gbv_m, rev_m))
sens = pd.DataFrame(sens)
for q in ("3Q26", "4Q26"):
    m = (sens.quarter == q) & (sens.term != "h1h2_vs_component_route_gap")
    v = sens.loc[m, "half_range_pp"] ** 2
    sens.loc[m, "contribution_to_variance_pct"] = (100 * v / v.sum()).round(1)
sens = sens.sort_values(["quarter", "range_pp"], ascending=[True, False])
sens.to_csv(os.path.join(OUT, "adr_sensitivities.csv"), index=False)

# ----------------------------------------------------------------------------
# 7. comparison column: ADR implied by published revenue consensus
# ----------------------------------------------------------------------------
cons = pd.read_csv(os.path.join(MAIN, "data", "processed", "overnight", "04_current_consensus.csv"))
cr = cons[(cons.metric == "revenue") & (cons.period.isin(["2026Q3", "2026Q4"]))]
implied = []
for _, r in cr.iterrows():
    q = {"2026Q3": "3Q26", "2026Q4": "4Q26"}[r.period]
    for nlabel, nights in (("team_baseline", NIGHTS[q]),
                           ("guide_low_double_digit_11pct",
                            {"3Q26": 133.6 * 1.11, "4Q26": 121.9 * 1.11}[q])):
        gbv = r.value / TAKE[q]
        adr = gbv / nights
        implied.append({"quarter": q, "vendor": r.vendor, "consensus_revenue_musd": r.value,
                        "take_rate_assumed": TAKE[q], "nights_assumption": nlabel,
                        "nights_m": round(nights, 1), "implied_gbv_musd": round(gbv, 0),
                        "implied_adr_usd": round(adr, 2),
                        "implied_adr_yoy_pp": round(100 * (adr / BASE_ADR[q] - 1), 2)})
implied = pd.DataFrame(implied)
implied.to_csv(os.path.join(OUT, "adr_consensus_implied.csv"), index=False)

# ----------------------------------------------------------------------------
# console report
# ----------------------------------------------------------------------------
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 50)
print("=== history, components (pp of ADR y/y) ===")
print(hist_out[["quarter", "adr_usd", "adr_yoy_reported_pp", "fx_effect_pp", "adr_exfx_yoy_pp",
                "geo_mix_pp", "unit_size_pp", "los_mix_pp", "new_business_pp", "interaction_pp",
                "residual_pricing_pp", "geo_recon_gap_pp"]].round(2).to_string(index=False))
print("\nresidual pricing: 2025 mean %.2f, last 8q mean %.2f, last 4q mean %.2f, 1H26 mean %.2f"
      % (res_2025, res_8q, res_4q, res_1h26))
print("geo reconstruction gap vs disclosed ex-FX: mean %.2f, mean abs %.2f, max abs %.2f pp"
      % (h.geo_recon_gap_pp.mean(), h.geo_recon_gap_pp.abs().mean(), h.geo_recon_gap_pp.abs().max()))
print("\n=== walk-forward backtest of the component build, ex-FX ADR y/y ===")
print(bt.round(2).to_string(index=False))
print("RMSE pp:", {k: round(v, 3) for k, v in bt_rmse.items()})
print("RMSE ratio vs naive:", {k: round(v, 3) for k, v in bt_ratio.items()})
print("\n=== FX estimator RMSE on 17 disclosed quarters ===")
print({k: round(v, 3) for k, v in rmse.items()})
print("FX forecast:", json.dumps({k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in FX.items()}))
print("\n=== component build ===")
print(comp.round(2).to_string(index=False))
print({k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in build.items()})
print("\n=== bridge route ===", {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in bridge.items()})
print("\n=== card (combined route) ===")
print(card[card.route == "headline_mean_of_routes"].to_string(index=False))
print("\n=== card (all) ===")
print(card.to_string(index=False))
print("\n=== sensitivities ===")
print(sens.to_string(index=False))
print("\n=== consensus-implied ADR ===")
print(implied.to_string(index=False))
print("\nwrote:", os.listdir(OUT))

