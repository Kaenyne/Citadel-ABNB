"""N3 — joint fit of the nights v3 identity (pre-registered in docs/pitch-model-v2/lines/nights_v3_prereg.md, DEC-0033).

g_N(t) = a + gamma * v(t) + beta * b(t)
  g_N : reported nights y/y (unrounded levels, abnb_driver_history_quarterly.csv)
  v   : vintage-matched stays y/y, GLOBAL, N1 series_quarterly.csv (review-count stays proxy)
  b   : backlog identity term in growth points, N2 identity_term.csv (central, low, high)

H1: beta positive, in [0.5, 1.5], HAC(3) p <= 0.10 on W1; positive on W2. Wald test beta = 1.
Walk-forward: expanding window, min train = k+3 (N1 convention), one-step-ahead, MAE/RMSE ratio to naive,
against spec a (v alone) on the identical scored set.
Convergence: 3Q26 reads under (i) joint fit, (ii) identity-restricted beta=1 with gamma from spec a, (iii) spec a alone,
with the partial-3Q26 stays band (N1) and the 3Q26 backlog band (N2). Reads and writes only under
data/processed/pitch_model_v2/nights_v3/N3/. Nothing is chosen by its 3Q26 output.
"""
import json, pathlib, numpy as np, pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[5]
OUT = ROOT / "data/processed/pitch_model_v2/nights_v3/N3"; OUT.mkdir(parents=True, exist_ok=True)
N1 = ROOT / "data/processed/pitch_model_v2/nights_v3/N1"; N2 = ROOT / "data/processed/pitch_model_v2/nights_v3/N2"

def qi(q):  # '3Q25' -> 2025*4+2
    return int("20" + q[2:]) * 4 + int(q[0]) - 1

d = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
d["qi"] = d.quarter.map(qi); d = d.sort_values("qi").set_index("qi")
d["g"] = (d.nights_m / d.nights_m.shift(4) - 1) * 100
s = pd.read_csv(N1 / "series_quarterly.csv"); s = s[s.region == "GLOBAL"].copy(); s["qi"] = s.quarter.map(qi); s = s.set_index("qi")
# extend v back before 1Q23 from the E package itself (yoy_vmatch, GLOBAL, w_reviews) so W1 training can start at 1Q22 as in E5
iq = pd.read_csv(ROOT / "data/processed/q3nowcast/E/index_quarterly.csv")
iv = iq[(iq.region == "GLOBAL") & (iq.measure == "yoy_vmatch")].copy(); iv["qi"] = iv.quarter.map(qi); iv = iv.set_index("qi").w_reviews * 100
ov = iv.reindex(s.index); assert np.allclose(ov.values, s.v_pct.values, atol=1e-6), "N1 v_pct must equal E4 yoy_vmatch"
t = pd.read_csv(N2 / "identity_term.csv"); t["qi"] = t.quarter.map(qi); t = t.set_index("qi")
P = pd.DataFrame({"quarter": d.quarter, "g": d.g, "v": iv, "c": s.c_pct, "nl": s.nl_pct,
                  "b": t.b_central_pp, "b_lo": t.b_low_fee133_pp, "b_hi": t.b_high_fee133_pp}).dropna(subset=["g", "v", "b"])
P = P[P.index >= qi("1Q22")]  # training start as in E5
W = {"W1": (qi("1Q23"), qi("2Q26")), "W2": (qi("1Q24"), qi("2Q26"))}

def hac_ols(y, X, L=3):
    X = np.column_stack([np.ones(len(y)), X]); n, k = X.shape
    beta = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    S = sum(np.outer(X[i] * e[i], X[i] * e[i]) for i in range(n))
    for l in range(1, L + 1):
        w = 1 - l / (L + 1)
        for i in range(l, n):
            G = np.outer(X[i] * e[i], X[i - l] * e[i - l]); S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv; se = np.sqrt(np.diag(V))
    r2 = 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, V, r2, n - k

rows = []
for wn, (lo, hi) in W.items():
    for bcol in ["b", "b_lo", "b_hi"]:
        D = P[(P.index >= lo) & (P.index <= hi)]
        y = D.g.values; X = D[["v", bcol]].values
        beta, se, V, r2, dof = hac_ols(y, X)
        tb = beta[2] / se[2]; pb = 2 * stats.t.sf(abs(tb), dof)
        wald = (beta[2] - 1) / se[2]; pw = 2 * stats.t.sf(abs(wald), dof)
        loo = [np.linalg.lstsq(np.column_stack([np.ones(len(y) - 1), np.delete(X, i, 0)]), np.delete(y, i), rcond=None)[0][2] for i in range(len(y))]
        rows.append(dict(window=wn, b_variant=bcol, n=len(y), a=beta[0], gamma=beta[1], gamma_t=beta[1] / se[1],
                         beta=beta[2], beta_se=se[2], beta_t=tb, beta_p=pb, wald_beta_eq_1_t=wald, wald_p=pw, r2=r2,
                         loo_beta_min=min(loo), loo_beta_max=max(loo),
                         H1_pass=bool((wn == "W1" and 0.5 <= beta[2] <= 1.5 and pb <= 0.10) or (wn == "W2" and beta[2] > 0))))
    # spec a for reference
    D = P[(P.index >= lo) & (P.index <= hi)]; beta, se, V, r2, dof = hac_ols(D.g.values, D[["v"]].values)
    rows.append(dict(window=wn, b_variant="none (spec a)", n=len(D), a=beta[0], gamma=beta[1], gamma_t=beta[1] / se[1], r2=r2))
R = pd.DataFrame(rows); R.to_csv(OUT / "joint_regressions.csv", index=False)

# walk-forward, expanding window, min train k+3, one step ahead, scored set identical across specs
wf = []
for wn, (lo, hi) in W.items():
    Dw = P[(P.index >= lo) & (P.index <= hi)]
    full = P[P.index <= hi]  # training may start before the window (E5 convention: 1Q22 for W1)
    for spec, cols in {"a: v": ["v"], "joint: v+b": ["v", "b"]}.items():
        k = len(cols); errs = []; errs_naive = []
        for q in Dw.index:
            tr = full[full.index < q]
            if len(tr) < 5: continue   # k+3 with k=2 for both specs → identical scored set
            X = np.column_stack([np.ones(len(tr)), tr[cols].values]); bhat = np.linalg.lstsq(X, tr.g.values, rcond=None)[0]
            pred = bhat[0] + bhat[1:] @ full.loc[q, cols].values
            errs.append(full.loc[q, "g"] - pred); errs_naive.append(full.loc[q, "g"] - tr.g.iloc[-1])
        e = np.array(errs); en = np.array(errs_naive)
        wf.append(dict(window=wn, spec=spec, scored=len(e), mae=np.mean(abs(e)), mae_naive=np.mean(abs(en)), mae_ratio=np.mean(abs(e)) / np.mean(abs(en)),
                       rmse_ratio=np.sqrt(np.mean(e ** 2)) / np.sqrt(np.mean(en ** 2)), mean_err=e.mean()))
WF = pd.DataFrame(wf); WF.to_csv(OUT / "joint_walkforward.csv", index=False)

# convergence, 3Q26. stays band from N1 partial (GLOBAL v, jul_only corrected ± sd; E6 basis point), backlog band from N2
pt = pd.read_csv(N1 / "partial_3q26.csv"); pv = pt[(pt.region == "GLOBAL") & (pt.measure == "v")]
v_jul = float(pv[pv.basis == "jul_only_monthly"].corrected_pct.iloc[0]); v_sd = float(pv[pv.basis == "jul_only_monthly"].gap_sd_pp.iloc[0])
e6 = pv[pv.basis != "jul_only_monthly"]; v_e6 = float(e6.corrected_pct.iloc[0]) if len(e6) else np.nan
fb = pd.read_csv(N2 / "forward_band.csv"); f3 = fb[fb.period == "3Q26"]
bcol = [c for c in fb.columns if c.startswith("b_") and "pp" in c][0] if any(c.startswith("b_") and "pp" in c for c in fb.columns) else None
b3_central, b3_lo, b3_hi = -4.70, -13.63, -2.44   # N2 dossier 2a (fee share 0.133 band); forward_band.csv columns are wide, values copied from the dossier
base = float(d.loc[qi("3Q25"), "nights_m"])
conv = []
def add(label, g, glo, ghi, note):
    conv.append(dict(read=label, g_pct=g, g_lo=glo, g_hi=ghi, nights_m=base * (1 + g / 100), nights_lo=base * (1 + glo / 100), nights_hi=base * (1 + ghi / 100), note=note))
for wn in W:
    ra = R[(R.window == wn) & (R.b_variant == "none (spec a)")].iloc[0]; rj = R[(R.window == wn) & (R.b_variant == "b")].iloc[0]
    for vb, vlab in [(v_jul, "jul-only corrected"), (v_e6, "E6 Jul+Aug day-matched")]:
        if np.isnan(vb): continue
        add(f"spec a stays only, {wn}, {vlab}", ra.a + ra.gamma * vb, ra.a + ra.gamma * (vb - v_sd), ra.a + ra.gamma * (vb + v_sd), "band = ±1 sd of the July→Q3 gap")
        add(f"joint fit, {wn}, {vlab}", rj.a + rj.gamma * vb + rj.beta * b3_central, rj.a + rj.gamma * (vb - v_sd) + rj.beta * min(b3_lo, b3_hi) if rj.beta > 0 else rj.a + rj.gamma * (vb - v_sd) + rj.beta * b3_hi,
            rj.a + rj.gamma * (vb + v_sd) + rj.beta * max(b3_lo, b3_hi) if rj.beta > 0 else rj.a + rj.gamma * (vb + v_sd) + rj.beta * b3_lo, "fitted beta; stays ±1 sd; backlog band fee 0.133")
        add(f"identity-restricted beta=1, {wn}, {vlab}", ra.a + ra.gamma * vb + b3_central, ra.a + ra.gamma * (vb - v_sd) + b3_lo, ra.a + ra.gamma * (vb + v_sd) + b3_hi, "gamma from spec a; backlog term enters at its identity value 1")
add("mechanism v2 (final_nights.md)", 9.89, 9.89, 9.89, "146.8m; DEC-0028 base"); add("reviews index W2-corrected", 9.52, 9.52, 9.52, "146.3m"); add("Street card", 11.5, 11.5, 11.5, "149.0m")
C = pd.DataFrame(conv); C.to_csv(OUT / "convergence_3q26.csv", index=False)
P.to_csv(OUT / "joint_panel.csv", index=False)
json.dump(dict(v_jul=v_jul, v_sd=v_sd, v_e6=v_e6, b3=[b3_central, b3_lo, b3_hi], base_3q25=base), open(OUT / "inputs.json", "w"), indent=1)
pd.set_option("display.width", 250)
print(R.round(3).to_string(index=False)); print(); print(WF.round(3).to_string(index=False)); print(); print(C.round(2).to_string(index=False))
