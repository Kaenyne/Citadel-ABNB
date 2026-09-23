"""ADR audit, extra checks. Read-only against the engine; writes only to receipts/ADR_AUDIT.
    PYTHONPATH=analysis/src py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/audit_extra.py
(1) how much of V2's forecast is its intercept, and a through-origin V2 on the same PIT protocol;
(2) V2's own error against the LatAm component (the mirror of the identity's);
(3) FY27 ADR if the 2027 quarters (h = 3..6) use the expanding-mean core, the rule that beats the carry at h = 3 and
    h = 4 on both windows of the core's own PIT record (C1_core_pit_scores.csv), 3Q26/4Q26 left on the carry;
(4) the combined table of P(print >= Street) under the audit's alternatives."""
from __future__ import annotations
import pathlib
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from pitch_model_v2.adr_engine import config as C, fx_data as F, walkforward as W, exfx as M, assemble as A

R = pathlib.Path(__file__).resolve().parent
daily = F.load_daily(); shares = F.gbv_shares(); tg = F.disclosed_targets(); pdts = F.print_dates()
full = W.build_full_design(daily, shares, tg)

# (1) V2 intercept share and a through-origin V2
a2, b2 = np.polyfit(full.eur_yoy.values, full.y.values, 1)[::-1]
for q in ["3Q26", "4Q26"]:
    x = F.design_row(daily, shares, q, None)
    print(f"V2 {q}: intercept {a2:+.3f} + slope {b2:.3f} x EUR {x['eur_yoy']:+.3f} = {a2 + b2 * x['eur_yoy']:+.3f}  "
          f"(intercept share {a2 / (a2 + b2 * x['eur_yoy']):.0%}); identity at zero currency moves is 0 by construction")
recs = []
for q in C.WINDOWS["W1"]:
    for o, d in F.origin_dates(q, pdts).items():
        if d is None or o == "O1":
            continue
        tr = full[full.print_date <= d]
        if len(tr) < 3:
            continue
        xt = F.design_row(daily, shares, q, d)
        b0 = float(np.linalg.lstsq(tr[["eur_yoy"]].values, tr.y.values, rcond=None)[0][0])
        a, b = np.polyfit(tr.eur_yoy.values, tr.y.values, 1)[::-1]
        recs.append({"quarter": q, "origin": o, "y": float(full.loc[q, "y"]), "V2_origin": b0 * xt["eur_yoy"], "V2": a + b * xt["eur_yoy"],
                     "naive": float(tr.y.iloc[-1])})
v = pd.DataFrame(recs)
for w, qs in C.WINDOWS.items():
    for o in ["O2", "O3"]:
        s = v[(v.origin == o) & v.quarter.isin(qs)]
        rm = lambda c: float(np.sqrt(((s[c] - s.y) ** 2).mean()))
        print(f"  {w} {o}: V2 {rm('V2')/rm('naive'):.3f} (bias {(s.V2-s.y).mean():+.2f}) | V2 through origin {rm('V2_origin')/rm('naive'):.3f} (bias {(s.V2_origin-s.y).mean():+.2f})")
b0_all = float(np.linalg.lstsq(full[["eur_yoy"]].values, full.y.values, rcond=None)[0][0])
for q in ["3Q26", "4Q26"]:
    x = F.design_row(daily, shares, q, None)
    print(f"  V2 through origin, all 17, {q}: {b0_all * x['eur_yoy']:+.3f}")

# (2) V2's O3 error against X_latam
wf = pd.read_csv(C.OUT / "fx_pit_walkforward.csv")
e = wf[(wf.variant == "V2_eur_ols") & (wf.origin == "O3") & wf.quarter.isin(C.WINDOWS["W1"])].set_index("quarter").err_pp
m = sm.OLS(e.values, sm.add_constant(full.loc[e.index, "latam"].values)).fit()
fq = pd.read_csv(R / "C3_forecast_quarters_by_variant.csv", index_col=0)
print(f"\nV2 O3 error (W1, n {len(e)}) = {m.params[0]:+.2f} + {m.params[1]:+.2f} x X_latam (p {m.pvalues[1]:.3f});"
      + " ".join(f" implied V2 at {q}: {fq.loc[q,'V2_eur_ols_all17'] - (m.params[0] + m.params[1]*fq.loc[q,'X_latam']):+.2f}" for q in ["3Q26", "4Q26"]))

# (3) FY27 under the expanding-mean core for h >= 3
h = M.history(); core_mean_all = float(h.core.mean())
base = M.forward(); fc = pd.read_csv(C.OUT / "fx_forecast_asof.csv"); fc = fc[fc["asof"] == "2026-09-21"].set_index("quarter")
path = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
lvl = dict(A.ADR_HIST); rows = []
for i, q in enumerate(C.FORWARD_QUARTERS, start=1):
    core = float(base.loc[q, "core"]) if i <= 2 else core_mean_all
    ex = float(base.loc[q, "exfx_yoy"]) - float(base.loc[q, "core"]) + core
    rep = ex + float(fc.loc[q, "fx_pp_point_spot_held"]); bq = C.prior_quarter(q, 4)
    lvl[q] = lvl[bq] * (1 + rep / 100); rows.append({"quarter": q, "core": core, "exfx": ex, "adr": lvl[q], "adr_filed": float(path.loc[q, "adr_usd"]),
                                                    "nights_m": C.NIGHTS_BASE_M[q]})
d = pd.DataFrame(rows).set_index("quarter")
q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
fy = float((d.loc[q27, "adr"] * d.loc[q27, "nights_m"]).sum() / d.loc[q27, "nights_m"].sum())
fyf = float(path.loc["FY27", "adr_usd"])
gbv = float((d.loc[q27, "adr"] * d.loc[q27, "nights_m"]).sum() / 1000); gbvf = float(path.loc["FY27", "gbv_busd"])
print(f"\nexpanding-mean core (1Q23-2Q26 mean {core_mean_all:.3f}) for 1Q27-4Q27, carry for 3Q26/4Q26:")
print(d.round(3).to_string())
print(f"  FY27 ADR {fy:.2f} vs filed {fyf:.2f} ({(fy/fyf-1)*100:+.2f}%); FY27 GBV ${gbv:.2f}bn vs ${gbvf:.2f}bn ({gbv-gbvf:+.2f}bn)")
d.to_csv(R / "C1_fy27_expanding_mean_core.csv")

# (4) P(print >= Street) under the audit's alternatives (the filed sd = the filed half-band, as assemble.py does)
la = pd.read_csv(R / "C2_ladder_corrections.csv").set_index("construction")
fxv = pd.read_csv(R / "C3_adr_under_fx_variants.csv")
rows = []
for q in ["3Q26", "4Q26"]:
    by = float(path.loc[q, "adr_usd_base_year"]); sd_usd = by * float(path.loc[q, "band_half_pp"]) / 100; st = C.STREET_ADR[q][0]
    v1 = float(fxv[(fxv.quarter == q) & (fxv.variant == "V1_MAP_all17")].fx_pp.iloc[0]); v0 = float(path.loc[q, "fx_pp"])
    cons = float(la.loc["both bases + netted sub-regional", f"adr_{q.lower()}"])
    for name, val in (("filed base", float(path.loc[q, "adr_usd"])),
                      ("composition consistently measured (both bases + netted sub-regional)", cons),
                      ("same + V1 FX weights (pre-registered variant, all 17 quarters)", cons + by * (v1 - v0) / 100)):
        rows.append({"quarter": q, "construction": name, "adr_usd": val, "street": st, "vs_street": val - st,
                     "p_print_ge_street": float(1 - stats.norm.cdf((st - val) / sd_usd))})
p = pd.DataFrame(rows); pd.set_option("display.width", 250); print("\n" + p.round(3).to_string(index=False)); p.to_csv(R / "C2_p_ge_street_alternatives.csv", index=False)
