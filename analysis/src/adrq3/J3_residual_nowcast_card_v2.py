"""
WS-J steps 3 and 4: the 3Q26 / 4Q26 pricing residual, card v2, and the pre-registered test.

Residual rules (each uses only residual history strictly before the target quarter):
  last_q          residual[t-1]
  persistence     mean of residual[t-2], residual[t-1]        <- PRE-REGISTERED v2 point rule
  trailing_4q     mean of last four (H's route-a rule)
  trailing_8q     mean of last eight
  ar1_residual    AR(1) fitted on residual history before t (>= 6 points)
  blend           0.5 * persistence + 0.5 * trailing_8q (shrinkage to the long run)
The v2 point uses `persistence` because the H card's diagnosis was that a trailing
four-quarter residual lags accelerations by about 1.5 pp; this is written down before the
walk-forward is run and is not changed afterwards. The band runs from the mean-reversion
case (2023-25 mean of the residual, 2.0 to 3.5 pp) to the persistence case (1H26 level).
No proxy survived J2 against the residual, so no proxy enters the point (J2 proxy_tests.csv).

Card v2: ex-FX = geo mix + unit size + LOS mix (workstream I's measured 3Q26 terms if
`data/processed/adrq3/I/I_mix_terms_3q26.csv` exists, else the H card inputs, flagged) +
new-business dilution (H, 15_seats_dilution_quarterly) + interaction (H) + residual.
Reported = ex-FX + FX (H card's EUR-fit and four-basket estimators, midpoint for the point).
Dollar ADR on 3Q25 $171.29 and 4Q25 $167.51; GBV and revenue at the team nights baseline
with H's same-quarter implied-take-rate convention (comparison column, not an input).
The H card's incremental fee-migration term is carried as a memo line, not in the point:
the residual already embeds the reprice on the migrated cohort and the increment is an
assumption on an assumption (H section 4).

Pre-registered walk-forward (1Q24-2Q26, and 2Q24-2Q26 to match H): for each quarter t,
ex-FX_v2(t) = mix(t) + new_business(prior year) + interaction(prior year) + residual_rule(t).
Two mix variants: `measured` = the realised quarter-t geo, size and LOS terms (what a perfect
in-quarter measurement by workstream I would deliver; an upper bound on I), and `trailing_4q`
(H's rule). Benchmarks refit the same way: naive last disclosed ex-FX, prior year, AR(1)
(expanding fit on ex-FX strictly before t), and H's route a from adr_exfx_backtest.csv.
Pass = RMSE ratio vs naive < 1 for the pre-registered rule with measured mix.

Run: py -3.13 analysis/src/adrq3/J3_residual_nowcast_card_v2.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MAIN = r"C:\Users\krish\citadel-abnb"
OUT = os.path.join(HERE, "data", "processed", "adrq3", "J")
os.makedirs(OUT, exist_ok=True)
HDIR = os.path.join(HERE, "data", "processed", "q3nowcast", "H")
IFILE = os.path.join(HERE, "data", "processed", "adrq3", "I", "I_mix_terms_3q26.csv")
QORDER = [f"{q}Q{str(y)[-2:]}" for y in range(2017, 2028) for q in range(1, 5)]
qi = {q: i for i, q in enumerate(QORDER)}

H = pd.read_csv(os.path.join(HDIR, "adr_history_components.csv")).set_index("quarter")
Hcard = pd.read_csv(os.path.join(HDIR, "adr_forecast_card.csv"))
Hbt = pd.read_csv(os.path.join(HDIR, "adr_exfx_backtest.csv")).set_index("quarter")
res = H["residual_pricing_pp"].astype(float)

# ----------------------------------------------------------------------------------
# 1. residual rules
# ----------------------------------------------------------------------------------
def rule_values(hist: pd.Series, t: str) -> dict:
    prior = hist[[q for q in hist.index if qi[q] < qi[t]]].dropna()
    v = prior.values
    out = {"last_q": v[-1] if len(v) >= 1 else np.nan,
           "persistence": v[-2:].mean() if len(v) >= 2 else np.nan,
           "trailing_4q": v[-4:].mean() if len(v) >= 4 else np.nan,
           "trailing_8q": v[-8:].mean() if len(v) >= 8 else v.mean() if len(v) >= 4 else np.nan}
    if len(v) >= 6:
        b1, b0 = np.polyfit(v[:-1], v[1:], 1)
        out["ar1_residual"] = b0 + b1 * v[-1]
    else:
        out["ar1_residual"] = np.nan
    out["blend"] = 0.5 * out["persistence"] + 0.5 * out["trailing_8q"]
    return out


RULES = ["last_q", "persistence", "trailing_4q", "trailing_8q", "ar1_residual", "blend"]
PRE_REGISTERED = "persistence"

# 3Q26 and 4Q26 nowcast rows. 4Q26 has no 3Q26 residual, so every rule is applied on the
# same history (through 2Q26); the 4Q26 row is therefore the same number with a wider band.
r_2325 = res[[q for q in res.index if q.endswith(("23", "24", "25"))]]
r_1h26 = res[["1Q26", "2Q26"]]
dq = res.diff().dropna()
now = []
for tq, extra_sd in (("3Q26", 1.0), ("4Q26", np.sqrt(2.0))):
    rv = rule_values(res, "3Q26")   # history through 2Q26 for both target quarters
    for rule in RULES:
        now.append({"quarter": tq, "case": rule, "residual_pp": rv[rule],
                    "lo_pp": rv[rule] - extra_sd * dq.std(), "hi_pp": rv[rule] + extra_sd * dq.std(),
                    "band_basis": f"+/- {extra_sd:.2f} x sd of quarterly residual changes ({dq.std():.2f} pp)",
                    "pre_registered_point": rule == PRE_REGISTERED, "source": "residual history 1Q23-2Q26 (H reconstruction)"})
    now.append({"quarter": tq, "case": "persistence_case_1H26", "residual_pp": float(r_1h26.mean()),
                "lo_pp": float(r_1h26.min()), "hi_pp": float(r_1h26.max()),
                "band_basis": "1Q26 and 2Q26 values", "pre_registered_point": False, "source": "H reconstruction"})
    now.append({"quarter": tq, "case": "mean_reversion_case_2023_25", "residual_pp": float(r_2325.mean()),
                "lo_pp": float(r_2325.quantile(0.25)), "hi_pp": float(r_2325.quantile(0.75)),
                "band_basis": "2023-25 interquartile range (full range %.2f to %.2f)" % (r_2325.min(), r_2325.max()),
                "pre_registered_point": False, "source": "H reconstruction"})
    now.append({"quarter": tq, "case": "historical_distribution", "residual_pp": float(res.mean()),
                "lo_pp": float(res.quantile(0.10)), "hi_pp": float(res.quantile(0.90)),
                "band_basis": "1Q23-2Q26 10th to 90th percentile", "pre_registered_point": False, "source": "H reconstruction"})
    now.append({"quarter": tq, "case": "proxy_based", "residual_pp": np.nan, "lo_pp": np.nan, "hi_pp": np.nan,
                "band_basis": "no proxy survived the note-08 protocol against the residual (J2 proxy_tests.csv)",
                "pre_registered_point": False, "source": "J2"})
now = pd.DataFrame(now)
now.to_csv(os.path.join(OUT, "residual_nowcast.csv"), index=False)

# ----------------------------------------------------------------------------------
# 2. mix terms for the card: workstream I if present, else H
# ----------------------------------------------------------------------------------
sd_q = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "15_seats_dilution_quarterly.csv")).set_index(["case_business", "quarter"])["dilution_drag_pp"]
H_TERMS = {   # H card table 2.3, lo / point / hi
    "3Q26": {"geographic_mix": (-1.64, -1.19, -1.04), "unit_size_party": (0.00, 0.74, 0.98), "length_of_stay_mix": (0.00, 0.30, 0.45)},
    "4Q26": {"geographic_mix": (-1.65, -1.19, -1.02), "unit_size_party": (0.00, 0.74, 0.98), "length_of_stay_mix": (0.00, 0.30, 0.45)},
}
mix_source = "H card inputs (I_mix_terms_3q26.csv not present when J3 ran)"
mix = {q: dict(H_TERMS[q]) for q in H_TERMS}
if os.path.exists(IFILE):
    I = pd.read_csv(IFILE)
    print("I file columns:", list(I.columns))
    cols = {c.lower(): c for c in I.columns}
    tcol = next((cols[c] for c in cols if c in ("term", "component", "name")), None)
    qcol = next((cols[c] for c in cols if c in ("quarter", "period", "target_quarter")), None)
    pcol = next((cols[c] for c in cols if c in ("adr_contribution_pp", "point_pp", "point", "pp", "value_pp", "term_pp", "central_pp")), None)
    lcol = next((cols[c] for c in cols if c in ("lo_pp", "low_pp", "lo", "low")), None)
    hcol = next((cols[c] for c in cols if c in ("hi_pp", "high_pp", "hi", "high")), None)
    ALIAS = {"unit_size_party_size": "unit_size_party", "geo": "geographic_mix", "geographic_mix": "geographic_mix", "geo_mix": "geographic_mix", "geo_mix_pp": "geographic_mix",
             "unit_size": "unit_size_party", "unit_size_party": "unit_size_party", "party_size": "unit_size_party", "size": "unit_size_party",
             "unit_size_pp": "unit_size_party", "los": "length_of_stay_mix", "los_mix": "length_of_stay_mix", "length_of_stay_mix": "length_of_stay_mix",
             "los_mix_pp": "length_of_stay_mix"}
    if tcol and pcol:
        used = 0
        for _, r in I.iterrows():
            key = ALIAS.get(str(r[tcol]).strip().lower())
            q = str(r[qcol]).strip() if qcol else "3Q26"
            # I's file carries comparison rows (2Q26, 3Q25, H card, WS-C ...); only the
            # measured 3Q26-to-date rows are inputs.
            if qcol and q not in ("3Q26_to_date", "3Q26", "2026Q3", "4Q26", "2026Q4"):
                continue
            q = {"2026Q3": "3Q26", "2026Q4": "4Q26", "3Q26_to_date": "3Q26"}.get(q, q)
            if key and q in mix:
                lo = float(r[lcol]) if lcol and pd.notna(r[lcol]) else float(r[pcol])
                hi = float(r[hcol]) if hcol and pd.notna(r[hcol]) else float(r[pcol])
                mix[q][key] = (min(lo, hi), float(r[pcol]), max(lo, hi))
                used += 1
        if used:
            mix_source = f"workstream I I_mix_terms_3q26.csv ({used} term rows read)"
            if not any(qcol and str(r[qcol]).strip() in ("4Q26", "2026Q4") for _, r in I.iterrows()):
                mix["4Q26"] = dict(mix["3Q26"])
                mix_source += "; 4Q26 carries I's 3Q26 terms"
    print("mix source:", mix_source)

# ----------------------------------------------------------------------------------
# 3. card v2
# ----------------------------------------------------------------------------------
BASE_ADR = {"3Q26": 171.29, "4Q26": 167.51}
BASE_Q = {"3Q26": "3Q25", "4Q26": "4Q25"}
NIGHTS = {"3Q26": 146.8, "4Q26": 132.7}
NIGHTS_YOY = {"3Q26": 9.9, "4Q26": 8.9}
TAKE = {"3Q26": 0.1788, "4Q26": 0.1362}
REV_BASE = {"3Q26": 4095.0, "4Q26": 2778.0}
FX = {}
for q in ("3Q26", "4Q26"):
    h = Hcard[(Hcard.quarter == q) & (Hcard.route == "headline_mean_of_routes")].set_index("fx_estimator")["fx_effect_pp"]
    FX[q] = {"eur_fit": float(h["eur_fit"]), "baskets": float(h["baskets"]), "midpoint": float(h["midpoint"])}

card_rows, term_rows = [], []
for q in ("3Q26", "4Q26"):
    rv = now[(now.quarter == q)].set_index("case")
    r_pt = float(rv.at[PRE_REGISTERED, "residual_pp"])
    r_lo = float(rv.at["mean_reversion_case_2023_25", "residual_pp"])   # 2023-25 mean, the mean-reversion case
    r_hi = float(rv.at["persistence_case_1H26", "hi_pp"])               # 2Q26 value
    terms = {
        "like_for_like_pricing_residual": (r_lo, r_pt, r_hi, f"J3 rule {PRE_REGISTERED}; band mean-reversion (2023-25 mean) to 2Q26 value", "assumed, anchored on measured residuals"),
        "geographic_mix": (*mix[q]["geographic_mix"], mix_source, "measured (I) or sourced (H)"),
        "unit_size_party": (*mix[q]["unit_size_party"], mix_source, "measured (I) or descriptive (H)"),
        "length_of_stay_mix": (*mix[q]["length_of_stay_mix"], mix_source, "measured (I) or descriptive (H)"),
        "new_business_seats": (float(sd_q.loc[("bull", q)]), float(sd_q.loc[("base", q)]), float(sd_q.loc[("bear", q)]), "H, 15_seats_dilution_quarterly", "assumed"),
        "interaction": (-0.15, -0.10, -0.05, "H, 07 interaction", "descriptive"),
    }
    memo_fee = {"3Q26": (-0.30, 0.16, 0.85), "4Q26": (-0.50, 0.26, 1.42)}[q]
    for k, (lo, pt, hi, src, lab) in terms.items():
        term_rows.append({"quarter": q, "term": k, "lo_pp": lo, "point_pp": pt, "hi_pp": hi, "in_point": True, "source": src, "label": lab})
    term_rows.append({"quarter": q, "term": "memo_fee_migration_increment_H", "lo_pp": memo_fee[0], "point_pp": memo_fee[1], "hi_pp": memo_fee[2],
                      "in_point": False, "source": "H card table 2.3; not added, residual embeds migrated-cohort reprice", "label": "assumed"})
    pt = sum(v[1] for v in terms.values())
    half = float(np.sqrt(sum(((v[2] - v[0]) / 2) ** 2 for v in terms.values())))
    arith_lo = sum(v[0] for v in terms.values())
    arith_hi = sum(v[2] for v in terms.values())
    for fxname, fx in FX[q].items():
        rep = pt + fx
        c_lo, c_hi = pt - half + fx, pt + half + fx
        w_lo = arith_lo + min(FX[q]["eur_fit"], FX[q]["baskets"])
        w_hi = arith_hi + max(FX[q]["eur_fit"], FX[q]["baskets"])
        adr = BASE_ADR[q] * (1 + rep / 100)
        gbv = adr * NIGHTS[q]
        card_rows.append({
            "quarter": q, "base_quarter": BASE_Q[q], "base_adr_usd": BASE_ADR[q], "fx_estimator": fxname, "fx_effect_pp": round(fx, 2),
            "residual_rule": PRE_REGISTERED, "residual_pp": round(r_pt, 2), "mix_source": mix_source,
            "adr_exfx_yoy_pp": round(pt, 2), "adr_exfx_central_lo_pp": round(pt - half, 2), "adr_exfx_central_hi_pp": round(pt + half, 2),
            "adr_exfx_arith_lo_pp": round(arith_lo, 2), "adr_exfx_arith_hi_pp": round(arith_hi, 2),
            "adr_reported_yoy_pp": round(rep, 2), "adr_reported_central_lo_pp": round(c_lo, 2), "adr_reported_central_hi_pp": round(c_hi, 2),
            "adr_reported_wide_lo_pp": round(w_lo, 2), "adr_reported_wide_hi_pp": round(w_hi, 2),
            "adr_usd_point": round(adr, 2), "adr_usd_central_lo": round(BASE_ADR[q] * (1 + c_lo / 100), 2),
            "adr_usd_central_hi": round(BASE_ADR[q] * (1 + c_hi / 100), 2),
            "nights_baseline_m": NIGHTS[q], "gbv_busd_point": round(gbv / 1000, 2),
            "gbv_yoy_pp_point": round(100 * ((1 + rep / 100) * (1 + NIGHTS_YOY[q] / 100) - 1), 2),
            "revenue_musd_same_q_take": round(gbv * TAKE[q], 0),
            "revenue_yoy_pp_same_q_take": round(100 * (gbv * TAKE[q] / REV_BASE[q] - 1), 2),
            "h_card_reported_yoy_pp": float(Hcard[(Hcard.quarter == q) & (Hcard.route == "headline_mean_of_routes") & (Hcard.fx_estimator == fxname)]["adr_reported_yoy_pp"].iloc[0]),
            "h_route_a_exfx_pp": float(Hcard[(Hcard.quarter == q) & (Hcard.route == "a_component_build") & (Hcard.fx_estimator == fxname)]["adr_exfx_yoy_pp"].iloc[0]),
        })
card = pd.DataFrame(card_rows)
card.to_csv(os.path.join(OUT, "adr_card_v2.csv"), index=False)
pd.DataFrame(term_rows).to_csv(os.path.join(OUT, "J3_card_v2_terms.csv"), index=False)

# ----------------------------------------------------------------------------------
# 4. pre-registered walk-forward
# ----------------------------------------------------------------------------------
sd_annual = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "15_seats_dilution_annual.csv"))
sd_base = sd_annual[sd_annual.case_business == "base"].set_index("year")["dilution_drag_pp"].to_dict()
inter = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "07_full_decomposition.csv")).set_index("year")["interaction_pp"].to_dict()
exfx = H["adr_exfx_yoy_pp"].astype(float)
MIXC = ["geo_mix_pp", "unit_size_pp", "los_mix_pp"]

bt = []
for t in H.index:
    if qi[t] < qi["1Q24"]:
        continue
    prior = [q for q in H.index if qi[q] < qi[t]]
    yprev = 2000 + int(t[-2:]) - 1
    nb = 0.0 if pd.isna(sd_base.get(yprev, np.nan)) else sd_base[yprev]
    it = 0.0 if pd.isna(inter.get(yprev, np.nan)) else inter[yprev]
    mix_meas = float(H.loc[t, MIXC].sum())
    mix_tr4 = float(H.loc[prior[-4:], MIXC].sum(axis=1).mean())
    rv = rule_values(res, t)
    yy = exfx[prior].values
    a1, a0 = np.polyfit(yy[:-1], yy[1:], 1)
    row = {"quarter": t, "actual_exfx_pp": exfx[t], "actual_residual_pp": res[t],
           "mix_measured_pp": mix_meas, "mix_trailing4q_pp": mix_tr4, "new_business_prior_year_pp": nb, "interaction_prior_year_pp": it,
           "naive_last_q_pp": exfx[prior[-1]], "prior_year_q_pp": exfx.get(QORDER[qi[t] - 4], np.nan),
           "ar1_expanding_pp": a0 + a1 * exfx[prior[-1]],
           "h_route_a_pp": Hbt["component_build_pp"].get(t, np.nan)}
    for rule in RULES:
        row[f"residual_{rule}_pp"] = rv[rule]
        row[f"v2_measured_{rule}_pp"] = mix_meas + nb + it + rv[rule]
        row[f"v2_trailing4q_{rule}_pp"] = mix_tr4 + nb + it + rv[rule]
    bt.append(row)
bt = pd.DataFrame(bt).set_index("quarter")

models = ["naive_last_q", "prior_year_q", "ar1_expanding", "h_route_a"] + \
         [f"v2_measured_{r}" for r in RULES] + [f"v2_trailing4q_{r}" for r in RULES]
score = []
for window, start in (("1Q24-2Q26", "1Q24"), ("2Q24-2Q26", "2Q24")):
    w = bt[bt.index.map(qi) >= qi[start]]
    err = {m: (w[f"{m}_pp"] - w.actual_exfx_pp) for m in models}
    rmse = {m: float(np.sqrt((e.dropna() ** 2).mean())) for m, e in err.items()}
    for m in models:
        e = err[m].dropna()
        d_act = (w.actual_exfx_pp - w.naive_last_q_pp)
        d_pred = (w[f"{m}_pp"] - w.naive_last_q_pp)
        nz = d_act != 0
        score.append({"window": window, "model": m, "n": int(len(e)), "rmse_pp": rmse[m], "bias_pp": float(e.mean()),
                      "mae_pp": float(e.abs().mean()),
                      "ratio_vs_naive": rmse[m] / rmse["naive_last_q"], "ratio_vs_prior_year": rmse[m] / rmse["prior_year_q"],
                      "ratio_vs_ar1": rmse[m] / rmse["ar1_expanding"],
                      "sign_accuracy_vs_naive": float((np.sign(d_pred[nz]) == np.sign(d_act[nz])).mean()) if nz.any() else np.nan,
                      "pre_registered": m == f"v2_measured_{PRE_REGISTERED}",
                      "residual_rule": m.split("_", 2)[2] if m.startswith("v2_") else "",
                      "mix_variant": "measured (realised quarter-t terms, upper bound on I)" if m.startswith("v2_measured") else
                                     "trailing 4q (H rule)" if m.startswith("v2_trailing4q") else "",
                      "knowable_before_print": "no: the residual is only knowable after the print; the rule uses prior residuals only" if m.startswith("v2_") else "yes"})
score = pd.DataFrame(score)
# jackknife: range of the ratio vs naive when any one walk-forward quarter is dropped
jk = []
for window, start in (("1Q24-2Q26", "1Q24"), ("2Q24-2Q26", "2Q24")):
    w = bt[bt.index.map(qi) >= qi[start]]
    for m in models:
        ratios = []
        for drop in w.index:
            ww = w.drop(index=drop)
            e_m = (ww[f"{m}_pp"] - ww.actual_exfx_pp).dropna()
            e_n = (ww["naive_last_q_pp"] - ww.actual_exfx_pp).dropna()
            ratios.append(float(np.sqrt((e_m ** 2).mean()) / np.sqrt((e_n ** 2).mean())))
        jk.append({"window": window, "model": m, "jackknife_ratio_min": min(ratios), "jackknife_ratio_max": max(ratios),
                   "jackknife_quarters_ratio_below_1": int(sum(r < 1 for r in ratios)), "jackknife_n": len(ratios)})
score = score.merge(pd.DataFrame(jk), on=["window", "model"], how="left")
# error attribution for the pre-registered model: with measured mix the error is exactly the residual-rule error
w = bt[bt.index.map(qi) >= qi["1Q24"]]
attr = pd.DataFrame({
    "quarter": w.index,
    "err_v2_pre_registered_pp": (w[f"v2_measured_{PRE_REGISTERED}_pp"] - w.actual_exfx_pp).values,
    "err_from_residual_rule_pp": (w[f"residual_{PRE_REGISTERED}_pp"] - w.actual_residual_pp).values,
    "err_from_new_business_and_interaction_pp": ((w.new_business_prior_year_pp + w.interaction_prior_year_pp)
                                                 - (H.loc[w.index, "new_business_pp"].fillna(0) + H.loc[w.index, "interaction_pp"].fillna(0))).values,
    "err_naive_pp": (w.naive_last_q_pp - w.actual_exfx_pp).values,
    "err_mix_if_trailing4q_pp": (w.mix_trailing4q_pp - w.mix_measured_pp).values,
})
bt.to_csv(os.path.join(OUT, "J3_card_v2_walk_forward_paths.csv"))
score.to_csv(os.path.join(OUT, "card_v2_backtest.csv"), index=False)
attr.to_csv(os.path.join(OUT, "J3_card_v2_error_attribution.csv"), index=False)

pd.set_option("display.width", 250)
print("\nresidual nowcast\n", now.round(2).to_string())
print("\ncard v2\n", card[["quarter", "fx_estimator", "fx_effect_pp", "residual_pp", "adr_exfx_yoy_pp", "adr_exfx_central_lo_pp", "adr_exfx_central_hi_pp",
                          "adr_reported_yoy_pp", "adr_reported_central_lo_pp", "adr_reported_central_hi_pp", "adr_usd_point", "adr_usd_central_lo",
                          "adr_usd_central_hi", "gbv_busd_point", "revenue_musd_same_q_take", "h_card_reported_yoy_pp"]].to_string())
print("\nterms\n", pd.DataFrame(term_rows).round(2).to_string())
print("\nbacktest\n", score.round(3).to_string())
print("\nattribution\n", attr.round(2).to_string())
pr = score[(score.window == "1Q24-2Q26") & score.pre_registered].iloc[0]
print(f"\nPRE-REGISTERED TEST: v2 ({PRE_REGISTERED}, measured mix) RMSE {pr.rmse_pp:.3f} vs naive {score[(score.window=='1Q24-2Q26')&(score.model=='naive_last_q')].rmse_pp.iloc[0]:.3f}: ratio {pr.ratio_vs_naive:.3f} -> {'PASS' if pr.ratio_vs_naive < 1 else 'FAIL'}")
