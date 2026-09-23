"""ADR audit (C3, part 2): (a) does the identity's error depend on its own LatAm component? (b) what probability does
the pre-registered 3Q26 falsifier ("printed ADR-FX pp inside the 21 Sep 80% band [0.36, 0.48]") have of withdrawing
a PERFECT identity, given the letter rounds ex-FX to whole points? (c) the FX leg's model error missing from the band.
    PYTHONPATH=analysis/src py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/audit_fx2.py"""
from __future__ import annotations
import pathlib
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from pitch_model_v2.adr_engine import config as C

R = pathlib.Path(__file__).resolve().parent
wf = pd.read_csv(C.OUT / "fx_pit_walkforward.csv")
fd = pd.read_csv(R / "C3_full_design_with_errors.csv", index_col=0)

print("(a) identity error vs its own regional components")
for o in ["O2", "O3"]:
    for w, qs in C.WINDOWS.items():
        e = wf[(wf.variant == "V0_translation") & (wf.origin == o) & wf.quarter.isin(qs)].set_index("quarter").err_pp
        X = fd.loc[e.index, ["latam"]]
        m = sm.OLS(e.values, sm.add_constant(X.values)).fit()
        m2 = sm.OLS(e.values, sm.add_constant(fd.loc[e.index, ["emea", "latam", "apac"]].values)).fit()
        print(f"  {w} {o} n={len(e)}: err = {m.params[0]:+.2f} + {m.params[1]:+.2f}*X_latam  (p {m.pvalues[1]:.3f}, r {np.corrcoef(X.latam, e)[0,1]:+.2f});"
              f"  3-comp slopes emea {m2.params[1]:+.2f} (p {m2.pvalues[1]:.2f}) latam {m2.params[2]:+.2f} (p {m2.pvalues[2]:.2f}) apac {m2.params[3]:+.2f} (p {m2.pvalues[3]:.2f})")
        if w == "W1" and o == "O3":
            x3 = pd.read_csv(R / "C3_forecast_quarters_by_variant.csv", index_col=0)
            for q in ["3Q26", "4Q26"]:
                pred_err = m.params[0] + m.params[1] * x3.loc[q, "X_latam"]
                print(f"     implied identity error at {q} (X_latam {x3.loc[q,'X_latam']:+.3f}): {pred_err:+.2f} -> FX {x3.loc[q,'V0_identity']-pred_err:+.2f}")
full = fd
m = sm.OLS(full.v0_err.values, sm.add_constant(full[["latam"]].values)).fit()
print(f"  all 17 quarters (print-date information): err = {m.params[0]:+.2f} + {m.params[1]:+.2f}*X_latam, p {m.pvalues[1]:.4f}")
lat_strong = full[full.latam > 0.5]
print("  quarters with X_latam > 0.5pp:", ", ".join(f"{q} {r.v0_err:+.2f}" for q, r in lat_strong.iterrows()),
      f"| mean {lat_strong.v0_err.mean():+.2f}, positive {int((lat_strong.v0_err > 0).sum())}/{len(lat_strong)}")
w3 = wf[(wf.origin == "O3") & (wf.variant == "V2_eur_ols")].set_index("quarter").err_pp
ls = [q for q in lat_strong.index if q in w3.index]
print("  V2 O3 errors in the same quarters:", ", ".join(f"{q} {w3[q]:+.2f}" for q in ls), f"| mean {w3[ls].mean():+.2f}")

print("\n(b) the 3Q26 falsifier: P(printed FX pp in [P10, P90]) when the identity is exactly right")
path = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
p10, p90, fx = float(path.loc["3Q26", "fx_p10"]), float(path.loc["3Q26", "fx_p90"]), float(path.loc["3Q26", "fx_pp"])
rng = np.random.default_rng(7)
n = 200_000
true_fx = fx + rng.normal(0, (p90 - p10) / 2.563, n)             # rate uncertainty only (the band's own content)
true_ex = rng.uniform(2.0, 5.0, n)                                 # any true ex-FX; only its fractional part matters
reported = true_ex + true_fx                                      # reported y/y from unrounded disclosed ADR levels
printed_fx = reported - np.round(true_ex)                          # letter rounds ex-FX to a whole point
inside = (printed_fx >= p10) & (printed_fx <= p90)
overlap = (printed_fx + 0.5 >= p10) & (printed_fx - 0.5 <= p90)   # rounding-aware (interval) reading
print(f"  band [{p10:.3f}, {p90:.3f}] (width {p90-p10:.3f}pp). P(printed point inside) = {inside.mean():.3f};"
      f" P(printed +/-0.5 interval overlaps band) = {overlap.mean():.3f}")

print("\n(c) the FX leg's model error is absent from the reported band")
env = pd.read_csv(C.OUT / "exfx_envelope.csv", index_col=0)
sc = pd.read_csv(C.OUT / "fx_scores.csv")
v0 = sc[sc.variant == "V0_translation"].set_index(["window", "origin"])
rows = []
for q, org in (("3Q26", "O3"), ("4Q26", "O1")):
    ex_half = float(env.loc[q, "exfx_half_band_pp"]); fxsd = float(env.loc[q, "fx_sd_pp"])
    model = float(v0.loc[("W1", "O3"), "interval_rmse_pp"])       # rounding-fair model error at full information
    rep_old = float(np.sqrt(ex_half ** 2 + fxsd ** 2)); rep_new = float(np.sqrt(ex_half ** 2 + fxsd ** 2 + model ** 2))
    base_rep = float(path.loc[q, "adr_yoy_reported_pct"]); st_yoy = float(path.loc[q, "street_yoy_pct"])
    p_old = 1 - stats.norm.cdf((st_yoy - base_rep) / rep_old); p_new = 1 - stats.norm.cdf((st_yoy - base_rep) / rep_new)
    rows.append({"quarter": q, "exfx_half": ex_half, "fx_rate_sd": fxsd, "fx_model_err_added": model, "half_band_filed": rep_old,
                 "half_band_with_model_err": rep_new, "p_ge_street_filed": p_old, "p_ge_street_with_model_err": p_new})
d = pd.DataFrame(rows); print(d.round(3).to_string()); d.to_csv(R / "C3_band_with_fx_model_error.csv", index=False)
