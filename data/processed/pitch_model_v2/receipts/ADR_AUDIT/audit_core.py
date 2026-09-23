"""ADR audit (C1/C2): the core. Read-only against the engine; writes only to receipts/ADR_AUDIT.
    PYTHONPATH=analysis/src py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/audit_core.py
Everything here is descriptive or a mechanical consequence of a stated rule; no input is chosen to reach a price."""
from __future__ import annotations
import pathlib
import numpy as np
import pandas as pd
from scipy import stats
from pitch_model_v2.adr_engine import config as C, exfx as M

R = pathlib.Path(__file__).resolve().parent
h = M.history()
core = h.core
print("core 1Q23-2Q26:", " ".join(f"{q} {v:.2f}" for q, v in core.items()))
c = core.values
m2325 = core.loc[["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25"]].mean()
r2325 = h.residual.loc[core.index[:12]].mean()
print(f"core mean 2023-25 {m2325:.3f} | residual mean 2023-25 {r2325:.3f} | exfx.CORE_MEAN_2023_25 {M.CORE_MEAN_2023_25}")

# ---- 1. h-step carry error: the filed sd of the h-change vs the RMSE of the carry (which keeps the drift) ------------
rows = []
for k in range(1, 7):
    d = c[k:] - c[:-k]
    rows.append({"h": k, "n_pairs": len(d), "sd_filed_ddof1": d.std(ddof=1), "rmse_carry": np.sqrt(np.mean(d ** 2)), "mean_change": d.mean(),
                 "rmse_carry_from_above_mean": np.sqrt(np.mean(d[(c[:-k] - m2325) > 0.5] ** 2)) if ((c[:-k] - m2325) > 0.5).any() else np.nan,
                 "mean_change_from_above_mean": d[(c[:-k] - m2325) > 0.5].mean() if ((c[:-k] - m2325) > 0.5).any() else np.nan,
                 "n_from_above_mean": int(((c[:-k] - m2325) > 0.5).sum())})
hs = pd.DataFrame(rows); print("\nh-step carry error on the 14-quarter core:"); print(hs.round(3).to_string(index=False))
hs.to_csv(R / "C1_core_hstep_errors.csv", index=False)

# ---- 2. PIT walk-forward on the core: carry vs expanding mean vs AR(1) refit on the core's own history -----------------
def ar1_fit(x):
    y, xl = x[1:], x[:-1]
    b, a = np.polyfit(xl, y, 1)
    return a, b
qs = list(core.index); recs = []
for i in range(4, len(qs)):                               # origin = qs[i-1] .. need >= 4 points to fit
    hist = c[:i]
    for k in (1, 2, 3, 4):
        j = i - 1 + k
        if j >= len(qs):
            continue
        a, b = ar1_fit(hist); f = hist[-1]
        for _ in range(k):
            f = a + b * f
        recs.append({"origin": qs[i - 1], "target": qs[j], "h": k, "actual": c[j], "carry": hist[-1], "mean": hist.mean(), "ar1": f,
                     "rho": b, "mu": a / (1 - b) if b < 1 else np.nan})
wf = pd.DataFrame(recs); wf.to_csv(R / "C1_core_pit_walkforward.csv", index=False)
out = []
for k, g in wf.groupby("h"):
    for w, start in (("targets 1Q24+", "1Q24"), ("targets 1Q25+", "1Q25")):
        g2 = g[g.target.map(C.qlabel_to_period) >= C.qlabel_to_period(start)]
        e = {m: np.sqrt(np.mean((g2[m] - g2.actual) ** 2)) for m in ("carry", "mean", "ar1")}
        out.append({"h": k, "window": w, "n": len(g2), **{f"rmse_{m}": v for m, v in e.items()},
                    "ar1_vs_carry": e["ar1"] / e["carry"], "mean_vs_carry": e["mean"] / e["carry"]})
pw = pd.DataFrame(out); print("\nPIT walk-forward on the core (descriptive; the bundle split is only knowable after 4Q25):")
print(pw.round(3).to_string(index=False)); pw.to_csv(R / "C1_core_pit_scores.csv", index=False)

# ---- 3. like-for-like AR(1) on the core itself, vs the filed AR(1) row (K4's residual constant 0.750, rho .747) ---------
a, b = ar1_fit(c)
mu = a / (1 - b)
path_ll, f = {}, c[-1]
for q in C.FORWARD_QUARTERS:
    f = a + b * f; path_ll[q] = f
f2, path_filed = c[-1], {}
for q in C.FORWARD_QUARTERS:
    f2 = 0.750 + 0.747 * f2; path_filed[q] = f2
print(f"\nAR(1) fitted on the core 1Q23-2Q26: const {a:.3f} rho {b:.3f} -> implied mean {mu:.3f}; filed row uses const 0.750 rho 0.747 -> implied mean {0.750/(1-0.747):.3f}")
f3, path_k4mu = c[-1], {}
for q in C.FORWARD_QUARTERS:
    f3 = m2325 + 0.747 * (f3 - m2325); path_k4mu[q] = f3
print("core path 3Q26..4Q27 | filed AR(1):", {q: round(v, 3) for q, v in path_filed.items()})
print("                     | K4 rho, core's own mean:", {q: round(v, 3) for q, v in path_k4mu.items()})
print("                     | AR(1) fitted on core:", {q: round(v, 3) for q, v in path_ll.items()})

# ---- 4. rounding: ex-FX is disclosed to whole points, so every core value carries +/-0.5 of rounding ------------------
sd_d1 = np.diff(c).std(ddof=1)
print(f"\nrounding: sd(delta core) {sd_d1:.3f}; rounding contributes sd sqrt(2)*{1/np.sqrt(12):.3f} = {np.sqrt(2/12):.3f} to it;"
      f" implied sd of the true quarterly change {np.sqrt(max(sd_d1**2 - 2/12, 0)):.3f}. The carried 2Q26 level has rounding sd {1/np.sqrt(12):.3f} (+/-0.5 uniform).")
print(f"   1Q26 and 2Q26 both print ex-FX '4'. core 1Q26 {c[-2]:.3f} -> 2Q26 {c[-1]:.3f}: the +{c[-1]-c[-2]:.3f} step is entirely the measured terms moving:")
for t in ["geo_mix", "unit_size", "los_mix", "seats", "interaction"]:
    print(f"      {t:12s} 1Q26 {h.loc['1Q26', t]:+.3f} -> 2Q26 {h.loc['2Q26', t]:+.3f}  (contributes {-(h.loc['2Q26', t]-h.loc['1Q26', t]):+.3f} to the residual step)")
print(f"   4Q25 -> 1Q26 residual step {h.loc['1Q26','residual']-h.loc['4Q25','residual']:+.3f}, of which the ASSUMED seats step contributes "
      f"{-(h.loc['1Q26','seats']-h.loc['4Q25','seats']):+.3f}")

# ---- 5. basis consistency: the core is computed on H's geo and unit terms, the forward uses the bucket geo and I's unit --
gm = pd.read_csv(C.OUT / "geo_mix_method_check.csv", index_col=0)
geo_off_2q26 = float(gm.loc["2Q26", "diff_pp"]); geo_off_last7 = float(gm.loc[["4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"], "diff_pp"].mean())
i = pd.read_csv(C.I_MIX_3Q26)
u_I_2q26 = float(i[(i.term == "unit_size") & (i.quarter == "2Q26")].point_pp.iloc[0]); u_H_2q26 = float(h.loc["2Q26", "unit_size"])
u_I_3q26 = float(i[(i.term == "unit_size") & (i.quarter == "3Q26")].point_pp.iloc[0])
print(f"\nbasis: geo bucket-minus-H 2Q26 {geo_off_2q26:+.3f} (mean 4Q24-2Q26 {geo_off_last7:+.3f}, all 7 positive: "
      f"{bool((gm.loc[['4Q24','1Q25','2Q25','3Q25','4Q25','1Q26','2Q26'],'diff_pp']>0).all())});"
      f" unit I-minus-H 2Q26 {u_I_2q26 - u_H_2q26:+.3f} (I 2Q26 {u_I_2q26:.3f}, H 2Q26 {u_H_2q26:.3f}; forward I 3Q26 {u_I_3q26:.3f})")
core_consistent = c[-1] - geo_off_2q26 - (u_I_2q26 - u_H_2q26)
print(f"   core on the forward terms' own basis: {c[-1]:.3f} - {geo_off_2q26:.3f} - {u_I_2q26 - u_H_2q26:.3f} = {core_consistent:.3f}")

# ---- 6. the ladder, re-run with each correction, as 4Q26 (and 3Q26) ADR ------------------------------------------------
path = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
fx = {q: float(path.loc[q, "fx_pp"]) for q in ("3Q26", "4Q26")}; by = {q: float(path.loc[q, "adr_usd_base_year"]) for q in ("3Q26", "4Q26")}
base_ex = {q: float(path.loc[q, "adr_yoy_exfx_pct"]) for q in ("3Q26", "4Q26")}
sub = pd.read_csv(C.OUT / "geomix_subregional_term.csv").set_index("quarter").subgeo_pp
subf = pd.read_csv(C.OUT / "geomix_subregional_term_forward.csv").set_index("quarter").subgeo_pp
sub_2q26 = float(sub.loc["2Q26"])
def adr(q, dex, dfx=0.0):
    return by[q] * (1 + (base_ex[q] + dex + fx[q] + dfx) / 100)
lad = []
def add(name, d3, d4, note, dfx3=0.0, dfx4=0.0):
    lad.append({"construction": name, "d_exfx_3q26": d3, "d_exfx_4q26": d4, "adr_3q26": adr("3Q26", d3, dfx3), "adr_4q26": adr("4Q26", d4, dfx4), "note": note})
add("filed base", 0, 0, "")
add("filed 'base + sub-regional' (adds the full forward term)", float(subf["3Q26"]), float(subf["4Q26"]), "double counts 2Q26's term, already inside the carried core")
add("sub-regional, netted against the 2Q26 term inside the core", float(subf["3Q26"]) - sub_2q26, float(subf["4Q26"]) - sub_2q26, f"2Q26 subgeo {sub_2q26:+.3f}")
add("geo basis: core recomputed on the bucket method", -geo_off_2q26, -geo_off_2q26, "same arithmetic as the forward geo")
add("unit basis: core recomputed on I's construction", -(u_I_2q26 - u_H_2q26), -(u_I_2q26 - u_H_2q26), "same construction as the forward unit term")
add("both bases consistent", -geo_off_2q26 - (u_I_2q26 - u_H_2q26), -geo_off_2q26 - (u_I_2q26 - u_H_2q26), "")
d_all = -geo_off_2q26 - (u_I_2q26 - u_H_2q26)
add("both bases + netted sub-regional", d_all + float(subf["3Q26"]) - sub_2q26, d_all + float(subf["4Q26"]) - sub_2q26, "composition, consistently measured")
add("mean reversion to the core's own mean (brief's flag)", m2325 - c[-1] + (base_ex["3Q26"] - base_ex["3Q26"]), m2325 - c[-1], "filed uses 2.398")
add("AR(1): K4 rho, core's own 2023-25 mean", path_k4mu["3Q26"] - c[-1], path_k4mu["4Q26"] - c[-1], "filed row's constant implies a mean of 2.96")
add("AR(1) fitted on the core itself", path_ll["3Q26"] - c[-1], path_ll["4Q26"] - c[-1], f"rho {b:.3f}, mean {mu:.3f}")
add("carry the 1H26 core average, not the single rounded 2Q26 value", (c[-1] + c[-2]) / 2 - c[-1], (c[-1] + c[-2]) / 2 - c[-1], "rounding-robust level")
la = pd.DataFrame(lad); la["vs_street_4q26"] = la.adr_4q26 - C.STREET_ADR["4Q26"][0]; la["vs_street_3q26"] = la.adr_3q26 - C.STREET_ADR["3Q26"][0]
pd.set_option("display.width", 250); print("\nladder with the audit's corrections:"); print(la.round(3).to_string(index=False))
la.to_csv(R / "C2_ladder_corrections.csv", index=False)

# break-even for an event (World Cup) composition premium carried inside the 2Q26 core
need = float(path.loc["4Q26", "adr_usd"]) - C.STREET_ADR["4Q26"][0]
for label, d0 in (("from the filed base", 0.0), ("after both basis fixes + netted sub-regional", d_all + float(subf["4Q26"]) - sub_2q26)):
    gap_pp = (adr("4Q26", d0) - C.STREET_ADR["4Q26"][0]) / by["4Q26"] * 100
    print(f"World Cup break-even {label}: the 2Q26 core must hold {gap_pp:.3f}pp of non-recurring event premium; "
          f"at s = 0.48% of 2Q26 nights (nights line's 0.5pt pull-forward) that is k = {1 + gap_pp / 0.48:.2f}x the average ADR")
