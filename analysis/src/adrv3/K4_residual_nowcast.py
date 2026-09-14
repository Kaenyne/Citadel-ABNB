"""WS-K, step 5: the 3Q26 and 4Q26 pricing residual under each scenario.

Scenarios (column `scenario`):
  cohort model, fitted        : 2023-25 mean + b_hat * d4share_t, b_hat from K3 (levels, no constant) per K1 variant.
                                This is the extrapolation of the hypothesis that the 1H26 step IS the reprice. It is a reductio.
  cohort mechanics, central   : last_q + 0.007 * (d4share_t - d4share_{t-1}), the K3 primary rule, chained for 4Q26.
  cohort mechanics, high      : same at 0.038.
  lap only, residual steps    : treat each residual change since 2Q25 as a permanent dated level step (3Q25 US RNPL, 4Q25 cancellation
                                redesign + fee tranche 1, 1Q26 ex-NA RNPL + testing, 2Q26); the y/y loses each step at its anniversary.
                                3Q26 = 2Q26 residual - 3Q25 step; 4Q26 = that - 4Q25 step.
  lap only, disclosed bundle  : 4Q26 = 2Q26 residual - the bundle's disclosed GBV-minus-nights contribution in 4Q25 (~1.0 pp, D014);
                                3Q26 unchanged (the 3Q25 contribution was not disclosed).
  lap + tranche 2, central    : lap only (residual steps) + 0.007 * (d4share_t - d4share_2Q26): the cohort beyond what 2Q26 already carries.
  lap + tranche 2, high       : same at 0.038.
  persistence                 : mean of 1Q26 and 2Q26 (J3's v2 rule).
  last_q                      : 2Q26 value (the v3 rule).
  mean reversion              : 2023-25 mean.
  AR(1) on the residual       : fitted 1Q23-2Q26, iterated.
Band: +/- 1 sd of quarterly residual changes (3Q26) and 1.41 sd (4Q26), as J 2.5, on the rule scenarios; the lap scenarios carry the
range across K1 variants and the 40-50% split instead.

Output: data/processed/adrv3/K/K4_residual_nowcast.csv

py -3.13 analysis/src/adrv3/K4_residual_nowcast.py
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "K")

H = pd.read_csv(os.path.join(ROOT, "data", "processed", "q3nowcast", "H", "adr_history_components.csv")).set_index("quarter")
res = H["residual_pricing_pp"].astype(float)
share = pd.read_csv(os.path.join(OUT, "K1_migrated_cohort_share.csv"))
fits = pd.read_csv(os.path.join(OUT, "K3_residual_fit.csv"))
MEAN_2325 = float(res[[q for q in res.index if int(q[2:]) <= 25]].mean())
sd_chg = float(res.diff().dropna().std(ddof=1))
CARD_V2_RESIDUAL = 4.61  # J3 card v2 point (comparison column, not an input)


def d4(variant, basis="nights"):
    s = share[(share.region == "blended") & (share.basis == basis) & (share.variant == variant)].set_index("quarter")
    return (s["migrated_share_yoy_change"] * 100).astype(float)


rows = []
def add(scenario, q, value, lo, hi, basis, label, knowable):
    rows.append({"scenario": scenario, "quarter": q, "residual_pp": round(value, 3), "band_low_pp": round(lo, 3) if lo is not None else np.nan,
                 "band_high_pp": round(hi, 3) if hi is not None else np.nan, "delta_vs_card_v2_residual_pp": round(value - CARD_V2_RESIDUAL, 3),
                 "basis": basis, "label": label, "knowable_before_print": knowable})

last = float(res["2Q26"]); pers = float(res[["1Q26", "2Q26"]].mean())
b3, b4 = sd_chg, sd_chg * np.sqrt(2)

# cohort model, fitted (reductio)
for v in ("central", "low_migrant", "high_migrant"):
    b = float(fits[(fits.variant == v) & (fits.basis == "nights") & (fits.spec.str.startswith("levels, no"))].coef_pp_per_pp_share.iloc[0])
    x = d4(v)
    for q in ("3Q26", "4Q26"):
        add(f"cohort model, fitted ({v}, b {b:.3f})", q, MEAN_2325 + b * x[q], None, None,
            f"2023-25 mean {MEAN_2325:.2f} + b * y/y migrated nights share {x[q]:.1f} pp", "assumed: extrapolates the fitted 1H26 relation; b is 3 to 7x the fee mechanics, so this is the reductio, not a forecast", "share yes; b fitted on 4Q25-2Q26")
# cohort mechanics (K3 primary and high), chained
for coef, nm in ((0.007, "central"), (0.038, "high")):
    x = d4("central")
    v3 = last + coef * (x["3Q26"] - x["2Q26"])
    v4 = v3 + coef * (x["4Q26"] - x["3Q26"])
    add(f"cohort mechanics, {nm} (last_q + {coef} * change in y/y share)", "3Q26", v3, v3 - b3, v3 + b3, f"last_q {last:.2f} + {coef} * {x['3Q26'] - x['2Q26']:.1f} pp", "rule on the pre-stated mechanics coefficient; the K3 primary rule" if nm == "central" else "rule at the top of the mechanics range", "yes (share dated from disclosures before the print; base is the 2Q26 residual)")
    add(f"cohort mechanics, {nm} (last_q + {coef} * change in y/y share)", "4Q26", v4, v4 - b4, v4 + b4, f"3Q26 value + {coef} * {x['4Q26'] - x['3Q26']:.1f} pp", "chained on the 3Q26 rule value", "yes")
# lap only, residual steps
a_step = float(res["3Q25"] - res["2Q25"]); b_step = float(res["4Q25"] - res["3Q25"]); c_step = float(res["1Q26"] - res["4Q25"]); d_step = float(res["2Q26"] - res["1Q26"])
l3 = last - a_step; l4 = l3 - b_step
add("lap only, residual steps", "3Q26", l3, l3 - b3, l3 + b3, f"2Q26 residual {last:.2f} minus the 3Q25 step {a_step:.2f} (US RNPL live from 3Q25)", "assumed: every residual change since 2Q25 is a permanent dated product step; scenario, not a forecast", "yes")
add("lap only, residual steps", "4Q26", l4, l4 - b4, l4 + b4, f"3Q26 lap value minus the 4Q25 step {b_step:.2f} (cancellation redesign, fee tranche 1, global from Oct 2025)", "assumed: as above; the 1Q26 and 2Q26 steps ({c_step:.2f}, {d_step:.2f}) stay in the y/y until 1H27", "yes")
# lap only, disclosed bundle
add("lap only, disclosed bundle ADR contribution", "3Q26", last, last - b3, last + b3, "2Q26 residual; the 3Q25 bundle contribution was not disclosed", "sourced dates, no 3Q25 figure", "yes")
add("lap only, disclosed bundle ADR contribution", "4Q26", last - 1.0, last - 1.0 - b4, last - 1.0 + b4, "2Q26 residual minus ~1.0 pp (4Q25 call: >200 bp nights, ~300 bp GBV, D014; the difference is an ADR contribution)", "sourced (D014), the subtraction assumes the whole 4Q25 bundle ADR contribution laps in 4Q26 and nothing replaces it", "yes")
# lap + tranche 2
for coef, nm in ((0.007, "central"), (0.038, "high")):
    x = d4("central")
    t3 = l3 + coef * (x["3Q26"] - x["2Q26"]); t4 = l4 + coef * (x["4Q26"] - x["2Q26"])
    add(f"lap + tranche 2, {nm}", "3Q26", t3, t3 - b3, t3 + b3, f"lap only + {coef} * (y/y share 3Q26 {x['3Q26']:.1f} - 2Q26 {x['2Q26']:.1f})", "assumed: lap arithmetic plus the fee reprice on the cohort migrating after 2Q26 (15 Sep and 13 Oct deadlines)", "yes")
    add(f"lap + tranche 2, {nm}", "4Q26", t4, t4 - b4, t4 + b4, f"lap only + {coef} * (y/y share 4Q26 {x['4Q26']:.1f} - 2Q26 {x['2Q26']:.1f})", "as above", "yes")
# reference rules
add("persistence (v2 rule)", "3Q26", pers, pers - b3, pers + b3, "mean of 1Q26 and 2Q26", "rule", "yes")
add("persistence (v2 rule)", "4Q26", pers, pers - b4, pers + b4, "same", "rule", "yes")
add("last_q (v3 rule)", "3Q26", last, last - b3, last + b3, "2Q26 residual", "rule", "yes")
add("last_q (v3 rule)", "4Q26", last, last - b4, last + b4, "same", "rule", "yes")
add("mean reversion", "3Q26", MEAN_2325, float(res[[q for q in res.index if int(q[2:]) <= 25]].quantile(0.25)), float(res[[q for q in res.index if int(q[2:]) <= 25]].quantile(0.75)), "2023-25 mean, interquartile band", "rule", "yes")
add("mean reversion", "4Q26", MEAN_2325, float(res[[q for q in res.index if int(q[2:]) <= 25]].quantile(0.25)), float(res[[q for q in res.index if int(q[2:]) <= 25]].quantile(0.75)), "same", "rule", "yes")
# AR(1)
yl = res.shift(1).dropna(); yy = res[yl.index]
b1, b0 = np.polyfit(yl.values, yy.values, 1)
ar3 = b0 + b1 * last; ar4 = b0 + b1 * ar3
add("AR(1) on the residual", "3Q26", ar3, ar3 - b3, ar3 + b3, f"rho {b1:.3f}, const {b0:.3f}, fitted 1Q23-2Q26", "rule", "yes")
add("AR(1) on the residual", "4Q26", ar4, ar4 - b4, ar4 + b4, "iterated", "rule", "yes")

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "K4_residual_nowcast.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(f"2023-25 mean {MEAN_2325:.3f}; sd of quarterly changes {sd_chg:.3f}; steps 3Q25 {a_step:+.3f}, 4Q25 {b_step:+.3f}, 1Q26 {c_step:+.3f}, 2Q26 {d_step:+.3f}")
print(df[["scenario", "quarter", "residual_pp", "band_low_pp", "band_high_pp", "delta_vs_card_v2_residual_pp"]].to_string())

# ------------------------------------------------------------------------------------------
# when does the reprice lap: y/y migrated share through 4Q27 (2027 level held at the 4Q26 level, assumed) and its
# contribution to the residual at the mechanics coefficients
# ------------------------------------------------------------------------------------------
lap = []
for v in ("central", "low_migrant", "high_migrant"):
    s = share[(share.region == "blended") & (share.basis == "nights") & (share.variant == v)].set_index("quarter")["migrated_split_to_single_share"] * 100
    lvl = s.to_dict()
    for q in ("1Q27", "2Q27", "3Q27", "4Q27"):
        lvl[q] = lvl["4Q26"]
    order = list(s.index) + ["1Q27", "2Q27", "3Q27", "4Q27"]
    for i, q in enumerate(order):
        if i < 4:
            continue
        d = lvl[q] - lvl[order[i - 4]]
        lap.append({"variant": v, "quarter": q, "migrated_nights_share_pct": round(lvl[q], 1), "yoy_change_pp": round(d, 1),
                    "fee_contribution_central_pp": round(0.007 * d, 2), "fee_contribution_high_pp": round(0.038 * d, 2),
                    "label": "assumed path on sourced dates" if q <= "4Q26" or q.endswith("26") else "assumed: 2027 level held at the 4Q26 level (migration complete)"})
lap = pd.DataFrame(lap)
lap.to_csv(os.path.join(OUT, "K4_fee_lap_schedule.csv"), index=False)
print("\nFEE LAP SCHEDULE (central):")
print(lap[(lap.variant == "central") & (lap.quarter.isin(["3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]))].to_string())
