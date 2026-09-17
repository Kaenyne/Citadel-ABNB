"""B02 - P(3Q26 reported ADR y/y <= +2.0%, i.e. ADR <= $174.72). Extends the R07 structural model for the lower tail.
numpy/pandas only. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/bonus-adr-residual-reverts/datasets/b02_model.py"""
from pathlib import Path
import numpy as np, pandas as pd
from math import erf, sqrt
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[4]
N = 400_000
Phi = lambda z: 0.5*(1+erf(z/sqrt(2)))
THR = 2.0; rows = []
# 1. history
h = pd.read_csv(ROOT/"data/processed/q3nowcast/H/adr_history_components.csv")
hist = h[["quarter","adr_usd","adr_yoy_reported_pp","fx_effect_pp","adr_exfx_yoy_pp","residual_pricing_pp"]].copy()
hist["reported_le_2.0"] = hist.adr_yoy_reported_pp <= THR
hist["mix_terms_pp"] = hist.adr_exfx_yoy_pp - hist.residual_pricing_pp
hist["resid_change_pp"] = hist.residual_pricing_pp.diff()
hist["needed_resid_for_le2_at_fx_-0.43"] = THR + 0.43 - hist.mix_terms_pp
hist.to_csv(HERE/"b02_history.csv", index=False)
rows.append(("quarters 1Q23-2Q26 n", len(hist)))
rows.append(("reported <= 2.0", int(hist["reported_le_2.0"].sum())))
rows.append(("reported <= 2.0 with FX >= -0.5", int((hist["reported_le_2.0"] & (hist.fx_effect_pp>=-0.5)).sum())))
rows.append(("reported <= 2.0 with residual >= 3.5", int((hist["reported_le_2.0"] & (hist.residual_pricing_pp>=3.5)).sum())))
rows.append(("min one-quarter residual change", float(hist.resid_change_pp.min())))
rows.append(("sd of one-quarter residual change (n13)", float(hist.resid_change_pp.std())))
# AR(1) on the residual: innovation sd
r = hist.residual_pricing_pp.values; x, y = r[:-1], r[1:]
A = np.vstack([np.ones_like(x), x]).T; beta, *_ = np.linalg.lstsq(A, y, rcond=None)
innov = y - A@beta; innov_sd = float(innov.std(ddof=2))
rows.append(("AR(1) const, rho", f"{beta[0]:.3f}, {beta[1]:.3f}")); rows.append(("AR(1) innovation sd", innov_sd))
ar1_3q26 = float(beta[0] + beta[1]*r[-1]); rows.append(("AR(1) 3Q26 residual point", ar1_3q26))
# 2. v3 card walk-forward errors (reported dollar y/y, with K line), split by accel/decel quarters
p = pd.read_csv(ROOT/"data/processed/adrv3/P/P1_card_v3_backtest_paths.csv"); p2 = p[p.target=="t2_reported_usd_yoy"]
err = {}
for fx in ["midpoint","eur","baskets"]:
    q = p2[p2.fx_estimator==fx]; e = (q.v3_point_last_q_plus_K_line_measured_mix - q.actual).values
    err[fx] = (float(np.sqrt((e**2).mean())), float(e.mean()))
    rows.append((f"v3+K walk-forward {fx}: RMSE, bias (model-actual)", f"{err[fx][0]:.3f}, {err[fx][1]:+.3f}"))
q = p2[p2.fx_estimator=="midpoint"].copy(); q["err"] = q.v3_point_last_q_plus_K_line_measured_mix - q.actual
q["prior_actual"] = q.actual.shift(1); q.loc[q.index[0],"prior_actual"] = 2.565277  # 4Q23 reported y/y
q["decel"] = q.actual < q.prior_actual
q[["quarter","actual","prior_actual","decel","err"]].to_csv(HERE/"b02_v3_errors_by_direction.csv", index=False)
rows.append(("decel quarters (actual < prior): n, mean err, rmse", f"{int(q.decel.sum())}, {q[q.decel].err.mean():+.2f}, {np.sqrt((q[q.decel].err**2).mean()):.2f}"))
rows.append(("accel quarters: n, mean err, rmse", f"{int((~q.decel).sum())}, {q[~q.decel].err.mean():+.2f}, {np.sqrt((q[~q.decel].err**2).mean()):.2f}"))
# 3. gaussian on the card
card = {"midpoint":3.43,"eur":2.74,"baskets":4.12}
for fx,pt in card.items():
    sd, b = err[fx]
    rows.append((f"P(<=2.0) N(card {fx} {pt}, sd {sd:.2f})", Phi((THR-pt)/sd)))
    rows.append((f"P(<=2.0) N(card {fx} bias-corrected {pt-b:.2f}, sd {sd:.2f})", Phi((THR-(pt-b))/sd)))
    rows.append((f"P(<=2.0) N(card {fx} {pt}, decel-quarter rmse 1.25)", Phi((THR-pt)/1.25)))
# 4. structural MC, R07 form (reproduction)
def mc(mix_mu=-1.15, mix_sd=0.35, w_res=(0.55,0.20,0.25), res=((4.85,0.55),(5.35,0.55),(3.6,0.7)), w_fx=(0.5,0.25,0.25), fx=((-0.43,0.33),(0.26,0.42),(-1.12,0.46)), seed=20260917):
    g = np.random.default_rng(seed)
    mix = g.normal(mix_mu, mix_sd, N)
    u = g.random(N); c = np.cumsum(w_res)
    resid = np.where(u<c[0], g.normal(*res[0],N), np.where(u<c[1], g.normal(*res[1],N), g.normal(*res[2],N)))
    v = g.random(N); d = np.cumsum(w_fx)
    f = np.where(v<d[0], g.normal(*fx[0],N), np.where(v<d[1], g.normal(*fx[1],N), g.normal(*fx[2],N)))
    return mix + resid + f, f, resid
rep, f, resid = mc()
rows.append(("R07 structural MC P(<=2.0) [reproduction]", float((rep<=THR).mean())))
rows.append(("R07 MC median", float(np.median(rep)))); rows.append(("R07 MC E[reported | <=2.0]", float(rep[rep<=THR].mean())))
# 5. B02 model: residual mixture re-weighted for the lower tail with an AR(1)-innovation reversion branch
#    persistence N(4.85,0.55) 0.45 / momentum N(5.35,0.55) 0.15 / AR(1) reversion N(ar1, innov sd) 0.25 / lap-and-proxy reversion N(3.6,0.7) 0.15
def mc2(w=(0.45,0.15,0.25,0.15), mix_mu=-1.15, mix_sd=0.35, w_fx=(0.5,0.25,0.25), fx=((-0.43,0.33),(0.26,0.42),(-1.12,0.46)), seed=20260917, ar_mu=None):
    g = np.random.default_rng(seed); ar_mu = ar1_3q26 if ar_mu is None else ar_mu
    mix = g.normal(mix_mu, mix_sd, N); u = g.random(N); c = np.cumsum(w)
    resid = np.where(u<c[0], g.normal(4.85,0.55,N), np.where(u<c[1], g.normal(5.35,0.55,N), np.where(u<c[2], g.normal(ar_mu, innov_sd, N), g.normal(3.6,0.7,N))))
    v = g.random(N); d = np.cumsum(w_fx)
    f = np.where(v<d[0], g.normal(*fx[0],N), np.where(v<d[1], g.normal(*fx[1],N), g.normal(*fx[2],N)))
    return mix + resid + f, f, resid
rep2, f2, res2 = mc2()
rows.append(("B02 MC P(<=2.0)", float((rep2<=THR).mean()))); rows.append(("B02 MC median", float(np.median(rep2))))
rows.append(("B02 MC P(>=4.4) [R07 check]", float((rep2>=4.4).mean())))
rows.append(("B02 MC E[reported | <=2.0]", float(rep2[rep2<=THR].mean()))); rows.append(("B02 MC E[reported | >2.0]", float(rep2[rep2>THR].mean())))
rows.append(("B02 MC P(<=2.5)", float((rep2<=2.5).mean()))); rows.append(("B02 MC P(<=1.0)", float((rep2<=1.0).mean()))); rows.append(("B02 MC P(<=0)", float((rep2<=0).mean())))
for lab, m in [("fx<=-1.0", f2<=-1.0), ("fx in (-1.0,-0.2)", (f2>-1.0)&(f2<-0.2)), ("fx>=-0.2", f2>=-0.2)]:
    rows.append((f"B02 MC P(<=2.0 | {lab}), mass", f"{(rep2[m]<=THR).mean():.3f}, {m.mean():.2f}"))
for lab, m in [("resid<=3.6", res2<=3.6), ("resid 3.6-4.5", (res2>3.6)&(res2<=4.5)), ("resid>4.5", res2>4.5)]:
    rows.append((f"B02 MC P(<=2.0 | {lab}), mass", f"{(rep2[m]<=THR).mean():.3f}, {m.mean():.2f}"))
for lab, kw in [("residual all persistence", dict(w=(1,0,0,0))), ("residual all momentum", dict(w=(0,1,0,0))), ("residual all AR(1)", dict(w=(0,0,1,0))), ("residual all mean-rev 3.6", dict(w=(0,0,0,1))),
                ("R07 weights (0.55/0.20/0/0.25)", dict(w=(0.55,0.20,0,0.25))), ("reversion-heavy (0.30/0.10/0.35/0.25)", dict(w=(0.30,0.10,0.35,0.25))),
                ("FX all midpoint", dict(w_fx=(1,0,0))), ("FX all baskets", dict(w_fx=(0,1,0))), ("FX all euro", dict(w_fx=(0,0,1))),
                ("mix centre -0.98 (H fills)", dict(mix_mu=-0.98)), ("mix centre -1.45 (geo drag band low)", dict(mix_mu=-1.45)), ("mix centre -1.75 (LatAm +27.5% mapped at the low end)", dict(mix_mu=-1.75)),
                ("mix sd 0.6", dict(mix_sd=0.6))]:
    rr, _, _ = mc2(**kw); rows.append((f"B02 MC {lab}", float((rr<=THR).mean())))
# 6. management "modest/moderate increase" record
led = pd.read_csv(ROOT/"data/processed/overnight/02_guidance_ledger.csv")
a = led[(led.metric=="adr_yoy_pct") & led.quote.str.contains("modest|moderate", case=False, na=False) & led.actual.notna()][["print_quarter","target_period","actual","quote"]]
a.to_csv(HERE/"b02_modest_increase_record.csv", index=False)
rows.append(("modest/moderate-increase ADR guides resolved: n, printed <=2.0", f"{len(a)}, {int((a.actual<=2.0).sum())}"))
# 7. sequential route: reported_3Q = reported_2Q + dFX + d(ex-FX y/y); Q2->Q3 ex-FX steps 2023/24/25 = -1.5, -1.0, +1.0
dex = np.array([-1.5,-1.0,1.0]); dfx_mid = -0.43-1.3
seq = 5.30 + dfx_mid + dex; rows.append(("sequential route 3Q26 reported under 2023/24/25 Q2->Q3 ex-FX steps", ", ".join(f"{s:.2f}" for s in seq)))
rows.append(("sequential route P(<=2.0), N(5.30+dFX+mean dex, sd 1.3)", Phi((THR-(5.30+dfx_mid+dex.mean()))/1.3)))
out = pd.DataFrame(rows, columns=["item","value"]); out.to_csv(HERE/"b02_results.csv", index=False); print(out.to_string())
