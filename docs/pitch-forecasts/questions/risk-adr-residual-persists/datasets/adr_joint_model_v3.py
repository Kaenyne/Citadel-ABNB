"""R07 + B02 revision 3 - ONE distribution for 3Q26 reported ADR y/y, both tails read from it (audit A14-04/05/06/07/11/12/15/16/22).
Final distribution = 0.60 x structural mixture + 0.40 x Gaussian-on-the-card route, one joint draw.
Structural (v2 form with three repairs): reported = card mix N(-1.16, 0.50) [sd 0.35 -> 0.50, A14-12] + K +0.17 + residual mixture
[persistence N(4.85,0.55) 0.45 / momentum N(5.35,0.55) 0.15 / AR(1) N(4.59, 0.94) 0.25 (centre = midpoint of the OLS 4.37 and the
Kendall-corrected 4.81, A14-05) / lap-and-proxy N(3.6,0.7) 0.15] + FX mixture [midpoint N(-0.43,0.33) 0.63 / baskets N(0.26,0.42) 0.185 /
euro N(-1.12,0.46) 0.185, A14-11] + bias +0.15 (half the pooled walk-forward bias; the direction-split justification is withdrawn, A14-04).
Gaussian route: the with-K card + half bias, N(3.58, 1.00) on the walk-forward RMSE 0.927 widened for the out-of-range FX spread, built as
ex-FX N(4.01, 0.944) + midpoint FX N(-0.43, 0.33) so the FX conditionals are defined on every draw.
numpy/pandas only; seed 20260917; n 400,000. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/risk-adr-residual-persists/datasets/adr_joint_model_v3.py
Writes adr_joint_results_v3.csv into both the R07 and B02 datasets folders and b02_modest_increase_record_v2.csv into B02's.
adr_joint_model_v2.py and its outputs are left as the audit trail."""
from pathlib import Path
import numpy as np, pandas as pd
from math import erf, sqrt
from statistics import NormalDist
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[4]
B02 = HERE.parent.parent / "bonus-adr-residual-reverts/datasets"
N = 400_000
Phi = lambda z: 0.5*(1+erf(z/sqrt(2)))
HI, LO = 4.4, 2.0
rows = []
# ---- walk-forward errors (P1 paths, with K line), pooled and split both ways (A14-04)
p = pd.read_csv(ROOT/"data/processed/adrv3/P/P1_card_v3_backtest_paths.csv"); p2 = p[p.target=="t2_reported_usd_yoy"]
err = {}
for fx in ["midpoint","eur","baskets"]:
    q = p2[p2.fx_estimator==fx]; e = (q.v3_point_last_q_plus_K_line_measured_mix - q.actual).values
    err[fx] = (float(np.sqrt((e**2).mean())), float(e.mean()))
rows.append(("walk-forward midpoint RMSE, bias (model - actual), n", f"{err['midpoint'][0]:.3f}, {err['midpoint'][1]:+.3f}, {len(e)}"))
BIAS_ADJ = round(-err["midpoint"][1]/2, 2)   # +0.15
h = pd.read_csv(ROOT/"data/processed/q3nowcast/H/adr_history_components.csv")
hist = h.set_index("quarter").adr_yoy_reported_pp
q = p2[p2.fx_estimator=="midpoint"].copy()
q["prior"] = [hist.get(pq) for pq in ["4Q23","1Q24","2Q24","3Q24","4Q24","1Q25","2Q25","3Q25","4Q25","1Q26"]]
q["err"] = q.v3_point_last_q_plus_K_line_measured_mix - q.actual
for lab, m in [("ex-post decel (actual < prior)", q.actual < q.prior), ("ex-post accel", q.actual >= q.prior),
               ("ex-ante decel (model point < prior)", q.v3_point_last_q_plus_K_line_measured_mix < q.prior), ("ex-ante accel", q.v3_point_last_q_plus_K_line_measured_mix >= q.prior)]:
    e_ = q.err[m].values
    rows.append((f"bias split {lab}: n, mean, SE, quarters", f"{len(e_)}, {e_.mean():+.3f}, {e_.std(ddof=1)/np.sqrt(len(e_)):.3f}, {list(q.quarter[m])}"))
rows.append(("bias adjustment applied to the centre: half the POOLED bias (shrinkage on n 10, SE 0.29); neither direction split is distinguishable from pooled", BIAS_ADJ))
# ---- AR(1) on the residual, OLS and Kendall-corrected (A14-05)
r = h.residual_pricing_pp.values; x, y = r[:-1], r[1:]
A = np.vstack([np.ones_like(x), x]).T; beta, *_ = np.linalg.lstsq(A, y, rcond=None)
innov_sd = float((y - A@beta).std(ddof=2)); ar1_ols = float(beta[0] + beta[1]*r[-1])
rho_k = min(0.999, float(beta[1]) + (1 + 3*float(beta[1]))/len(r)); mu_lr = float(beta[0]/(1-beta[1]))
ar1_k = (1-rho_k)*mu_lr + rho_k*float(r[-1]); AR1_C = round((ar1_ols + ar1_k)/2, 2)
rows.append(("AR(1) OLS const, rho, innovation sd, 3Q26 point", f"{beta[0]:.3f}, {beta[1]:.3f}, {innov_sd:.3f}, {ar1_ols:.3f}"))
rows.append(("AR(1) Kendall-corrected rho (T=14), 3Q26 point; branch centre used (midpoint)", f"{rho_k:.3f}, {ar1_k:.3f}; {AR1_C:.2f}"))
# ---- FX branch calibration against the 17-quarter disclosed record (A14-11)
fxq = pd.read_csv(ROOT/"data/processed/adrv3/N/N1_fx_estimator_by_quarter.csv")
spread = (fxq.est_from_eur - fxq.est_from_regional_baskets).abs(); e_mid = fxq.err_est_from_midpoint
rows.append(("FX record n, |err| mean, corr(|err|, spread), err >= +0.57 (disclosed <= -1.0 from midpoint -0.43) count, Laplace",
             f"{len(fxq)}, {e_mid.abs().mean():.3f}, {e_mid.abs().corr(spread):+.3f}, {int((e_mid>=0.57).sum())}, {2/(len(fxq)+2):.3f}"))
rows.append(("FX record: quarters with spread >= 0.7 and their midpoint errors", "; ".join(f"{a} {b:+.2f}" for a, b in zip(fxq.quarter_h[spread>=0.7], e_mid[spread>=0.7]))))
# ---- model
MIX_MU, MIX_SD, K = -1.16, 0.50, 0.17
W_RES = (0.45, 0.15, 0.25, 0.15); RES = ((4.85,0.55),(5.35,0.55),(AR1_C,innov_sd),(3.6,0.7))
W_FX = (0.63, 0.185, 0.185); FX = ((-0.43,0.33),(0.26,0.42),(-1.12,0.46))
G_MU, G_SD, W_STRUCT = 3.43 + BIAS_ADJ, 1.00, 0.60
def mc(mix_mu=MIX_MU, mix_sd=MIX_SD, k=K, bias=BIAS_ADJ, w_res=W_RES, res=RES, w_fx=W_FX, fx=FX, g_mu=G_MU, g_sd=G_SD, w_struct=W_STRUCT, seed=20260917):
    g = np.random.default_rng(seed)
    mix = g.normal(mix_mu, mix_sd, N)
    u = g.random(N); c = np.cumsum(w_res)
    resid = np.where(u<c[0], g.normal(*res[0],N), np.where(u<c[1], g.normal(*res[1],N), np.where(u<c[2], g.normal(*res[2],N), g.normal(*res[3],N))))
    v = g.random(N); d = np.cumsum(w_fx)
    f_s = np.where(v<d[0], g.normal(*fx[0],N), np.where(v<d[1], g.normal(*fx[1],N), g.normal(*fx[2],N)))
    exfx_s = mix + k + resid + bias; rep_s = exfx_s + f_s
    f_g = g.normal(fx[0][0], fx[0][1], N); exfx_g = g.normal(g_mu - fx[0][0], sqrt(max(g_sd**2 - fx[0][1]**2, 0.01)), N); rep_g = exfx_g + f_g
    z = g.random(N) < w_struct
    rep = np.where(z, rep_s, rep_g); f = np.where(z, f_s, f_g); exfx = np.where(z, exfx_s, exfx_g)
    return rep, f, resid, exfx, z, rep_s, rep_g
rep, f, res, exfx, z, rep_s, rep_g = mc()
def summ(lab, rep):
    return (f"{lab}: P(>=4.4) [R07], P(<=2.0) [B02], median, mean, sd",
            f"{(rep>=HI).mean():.4f}, {(rep<=LO).mean():.4f}, {np.median(rep):.3f}, {rep.mean():.3f}, {rep.std():.3f}")
rows.append(summ("JOINT MODEL revision 3 (0.60 structural + 0.40 Gaussian)", rep))
rows.append(summ("  structural component alone (A14-05, -11, -12 repaired)", rep_s))
rows.append(summ("  Gaussian route alone N(3.58, 1.00)", rep_g))
rows.append(summ("  revision-2 model (mix sd 0.35, AR(1) 4.37, FX .50/.25/.25, structural only)", mc(mix_sd=0.35, res=((4.85,0.55),(5.35,0.55),(ar1_ols,innov_sd),(3.6,0.7)), w_fx=(0.50,0.25,0.25), w_struct=1.0)[0]))
rows.append(("joint: P(>=4.0), P(>=3.4 Street mean), P(<=2.5), P(<=1.0), P(<=0)", f"{(rep>=4.0).mean():.4f}, {(rep>=3.4).mean():.4f}, {(rep<=2.5).mean():.4f}, {(rep<=1.0).mean():.4f}, {(rep<=0).mean():.4f}"))
rows.append(("joint: E[reported | >=4.4], E[reported | <=2.0]", f"{rep[rep>=HI].mean():.3f}, {rep[rep<=LO].mean():.3f}"))
rows.append(("joint: p5/p10/p25/p50/p75/p90/p95", ", ".join(f"{np.percentile(rep,q):.2f}" for q in [5,10,25,50,75,90,95])))
for lab, m in [("fx >= +0.2 (baskets right)", f>=0.2), ("fx in (-0.6,-0.2) (midpoint)", (f>-0.6)&(f<-0.2)), ("fx in (-1.0,-0.2)", (f>-1.0)&(f<-0.2)), ("fx <= -1.0 (euro right)", f<=-1.0), ("fx >= -0.2", f>=-0.2)]:
    rows.append((f"joint | {lab}: mass, P(>=4.4), P(<=2.0)", f"{m.mean():.3f}, {(rep[m]>=HI).mean():.3f}, {(rep[m]<=LO).mean():.3f}"))
for lab, m in [("ex-FX 5pct (>=4.5)", exfx>=4.5), ("ex-FX 4pct (3.5-4.5)", (exfx>=3.5)&(exfx<4.5)), ("ex-FX 3pct (2.5-3.5)", (exfx>=2.5)&(exfx<3.5)), ("ex-FX 2pct or lower (<2.5)", exfx<2.5)]:
    rows.append((f"joint | {lab}: mass, P(>=4.4), P(<=2.0)", f"{m.mean():.3f}, {(rep[m]>=HI).mean():.3f}, {(rep[m]<=LO).mean():.3f}"))
for lab, m in [("residual <= 3.6", res<=3.6), ("residual 3.6-4.5", (res>3.6)&(res<=4.5)), ("residual > 4.5", res>4.5)]:
    mm = m & z
    rows.append((f"structural component | {lab}: mass (of structural), P(>=4.4), P(<=2.0)", f"{mm.sum()/z.sum():.3f}, {(rep[mm]>=HI).mean():.3f}, {(rep[mm]<=LO).mean():.3f}"))
sens = [("no bias adjustment", dict(bias=0.0, g_mu=3.43)), ("full bias adjustment +0.31", dict(bias=0.31, g_mu=3.74)),
        ("bias -0.07 (ex-post decel split)", dict(bias=-0.07, g_mu=3.36)), ("bias +0.58 (ex-ante decel split)", dict(bias=0.58, g_mu=4.01)),
        ("structural weight 1.0 (no Gaussian route)", dict(w_struct=1.0)), ("structural weight 0.40", dict(w_struct=0.40)), ("Gaussian route only", dict(w_struct=0.0)),
        ("Gaussian sd 0.927 (raw RMSE)", dict(g_sd=0.927)), ("Gaussian sd 1.10", dict(g_sd=1.10)),
        ("AR(1) at OLS 4.37 (rev 2)", dict(res=((4.85,0.55),(5.35,0.55),(ar1_ols,innov_sd),(3.6,0.7)))), ("AR(1) at Kendall 4.81", dict(res=((4.85,0.55),(5.35,0.55),(ar1_k,innov_sd),(3.6,0.7)))),
        ("AR(1) weight halved (0.45/0.15/0.125/0.15 renormalised)", dict(w_res=(0.45/0.875,0.15/0.875,0.125/0.875,0.15/0.875))),
        ("residual weights reversion-heavy 0.30/0.10/0.35/0.25", dict(w_res=(0.30,0.10,0.35,0.25))), ("residual all persistence", dict(w_res=(1,0,0,0))), ("residual all momentum", dict(w_res=(0,1,0,0))), ("residual all AR(1)", dict(w_res=(0,0,1,0))), ("residual all mean-rev 3.6", dict(w_res=(0,0,0,1))),
        ("FX .50/.25/.25 (rev 2)", dict(w_fx=(0.50,0.25,0.25))), ("FX .76/.12/.12 (empirical rate)", dict(w_fx=(0.76,0.12,0.12))), ("FX all midpoint", dict(w_fx=(1,0,0))), ("FX all baskets", dict(w_fx=(0,1,0))), ("FX all euro", dict(w_fx=(0,0,1))),
        ("mix sd 0.35 (rev 2)", dict(mix_sd=0.35)), ("mix sd 0.60", dict(mix_sd=0.60)), ("mix -1.45 (geo drag at band low)", dict(mix_mu=-1.45)), ("mix -1.75 (LatAm mapped low)", dict(mix_mu=-1.75)), ("mix -0.94 (band high)", dict(mix_mu=-0.94)),
        ("K line 0", dict(k=0.0, g_mu=3.26+BIAS_ADJ)), ("K line +0.93", dict(k=0.93, g_mu=3.43+0.76+BIAS_ADJ))]
for lab, kw in sens:
    rows.append(summ(f"sens {lab}", mc(**kw)[0]))
for lab, m_, s_ in [("N(3.43,0.93) with-K card raw", 3.43, 0.927), ("N(3.58,0.93) with-K card + half bias", 3.58, 0.927), ("N(3.58,1.00) route used", 3.58, 1.00), ("N(3.74,0.93) bias-corrected", 3.74, 0.927), ("auditor A10 N(3.50,1.05)", 3.50, 1.05), ("auditor A14 N(3.50,1.00)", 3.50, 1.00)]:
    rows.append((f"gaussian {lab}: P(>=4.4), P(<=2.0)", f"{1-Phi((HI-m_)/s_):.4f}, {Phi((LO-m_)/s_):.4f}"))
p_hi, p_lo = float((rep>=HI).mean()), float((rep<=LO).mean())
z1, z2 = NormalDist().inv_cdf(1-p_hi), NormalDist().inv_cdf(p_lo); sg = (HI-LO)/(z1-z2); mu_j = HI - z1*sg
rows.append(("normal carrying both revision-3 tails: mu, sd", f"{mu_j:.2f}, {sg:.2f}"))
# ---- reference classes, corrected (A14-15, A14-16)
rows.append(("history 1Q23-2Q26: n, reported<=2.0, FX>=-0.5 quarters, of those <=2.0, residual>=3.5 quarters, of those <=2.0, residual>=3.45 quarters, of those <=2.0",
             f"{len(h)}, {int((h.adr_yoy_reported_pp<=2.0).sum())}, {int((h.fx_effect_pp>=-0.5).sum())}, {int(((h.fx_effect_pp>=-0.5)&(h.adr_yoy_reported_pp<=2.0)).sum())}, {int((h.residual_pricing_pp>=3.5).sum())}, {int(((h.residual_pricing_pp>=3.5)&(h.adr_yoy_reported_pp<=2.0)).sum())}, {int((h.residual_pricing_pp>=3.45).sum())}, {int(((h.residual_pricing_pp>=3.45)&(h.adr_yoy_reported_pp<=2.0)).sum())}"))
rows.append(("history: reported>=4.4, FX<=0 quarters, reported>=4.4 & FX<=0", f"{int((h.adr_yoy_reported_pp>=4.4).sum())}, {int((h.fx_effect_pp<=0).sum())}, {int(((h.adr_yoy_reported_pp>=4.4)&(h.fx_effect_pp<=0)).sum())}"))
# ---- the seven 'modest/moderate increase' guides (A14-06)
rec = pd.DataFrame([
    ("1Q24","2Q24","modestly up","estimate that ADR for the quarter will be modestly up compared to Q2 2023", 2.12),
    ("2Q24","3Q24","increase modestly","we expect ADR to increase modestly on a year-over-year basis in Q3 2024", 1.40),
    ("3Q24","4Q24","increase modestly","In Q4 2024, we expect ADR to increase modestly on a year-over-year basis", 0.89),
    ("2Q25","3Q25","increase modestly","In Q3 2025, we expect ADR to increase modestly on a year-over-year basis, primarily driven by FX", 4.67),
    ("3Q25","4Q25","modest increase in ADR","We anticipate our GBV to benefit from a modest increase in ADR, primarily due to price appreciation and FX", 5.93),
    ("4Q25","1Q26","moderate increase in ADR","a moderate increase in ADR due to price appreciation and FX", 9.03),
    ("1Q26","2Q26","moderate increase in ADR","a moderate increase in ADR", 5.30)],
    columns=["print_quarter","target_period","wording","quote","actual_reported_yoy_pct"])
rec["le_2_0"] = (rec.actual_reported_yoy_pct <= 2.0).astype(int)
rec.to_csv(B02/"b02_modest_increase_record_v2.csv", index=False)
rows.append(("modest/moderate-increase guides: n, printed <= 2.0; 'increase modestly / modestly up' n, <= 2.0; 'modest/moderate increase in ADR' n, <= 2.0",
             f"{len(rec)}, {int(rec.le_2_0.sum())}; {int(rec.wording.str.contains('modestly').sum())}, {int(rec[rec.wording.str.contains('modestly')].le_2_0.sum())}; {int((~rec.wording.str.contains('modestly')).sum())}, {int(rec[~rec.wording.str.contains('modestly')].le_2_0.sum())}"))
# ---- MODL anchor
e = pd.read_csv(ROOT/"data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv"); a = e[(e.quarter=="3Q26")&(e.metric=="adr_usd")].iloc[0]
sd_modl = (a.street_high_growth-a.street_low_growth)/4
rows.append(("MODL: n, low/mean/high growth, range/4 sd, P(>=4.4), P(<=2.0), 178.83 pct of range, 174.72 pct of range",
             f"{a.n_estimates}, {a.street_low_growth:.3f}/{a.street_mean_growth:.3f}/{a.street_high_growth:.3f}, {sd_modl:.3f}, {1-Phi((4.4-a.street_mean_growth)/sd_modl):.4f}, {Phi((2.0-a.street_mean_growth)/sd_modl):.4f}, {100*(178.83-a.street_low)/(a.street_high-a.street_low):.1f}, {100*(174.72-a.street_low)/(a.street_high-a.street_low):.1f}"))
rows.append(("MODL at the card RMSE 0.93: P(>=4.4), P(<=2.0)", f"{1-Phi((4.4-a.street_mean_growth)/0.927):.4f}, {Phi((2.0-a.street_mean_growth)/0.927):.4f}"))
# ---- impact arithmetic: a level shift is not a growth shift (A14-07)
v = pd.read_csv(ROOT/"data/processed/margin_build/23_final_model/23_vs_consensus.csv").set_index("period")
fy26, fy27 = float(v.loc["FY26","model_revenue_musd"]), float(v.loc["FY27","model_revenue_musd"]); g0 = 100*(fy27/fy26-1)
e_lo, e_hi = float(rep[rep<=LO].mean()), float(rep[rep>=HI].mean())
for lab, d_adr, pr in [("B02 Yes", e_lo-3.3, p_lo), ("R07 Yes", e_hi-3.3, p_hi)]:
    r3, r4, r27 = d_adr*46, d_adr*30, d_adr*158; g1 = 100*((fy27+r27)/(fy26+r3+r4)-1)
    mult = abs(g1-g0)*0.44*9.5; lev = abs(r27)*16/591.7; stock = (mult+lev)*0.70*np.sign(d_adr)
    m26 = (r3+r4)/(fy26/2)*100*0.59*0.5; m27 = r27/fy27*100*0.66; eps = r27*0.66*0.0014 if False else r27*0.0014
    rows.append((f"impact {lab}: dADR pt, 3Q26 rev $M, 4Q26 rev $M, FY27 rev $M, FY27 growth {g0:.2f}% -> new, delta pt, FY26 margin pp, FY27 margin pp, FY27 EPS $ (held), multiple $, level $, stock $ (x0.70), EV $ at P {pr:.3f}",
                 f"{d_adr:+.2f}, {r3:+.0f}, {r4:+.0f}, {r27:+.0f}, {g1:.2f}, {g1-g0:+.2f}, {m26:+.2f}, {m27:+.2f}, {eps:+.2f}, {mult:.2f}, {lev:.2f}, {stock:+.1f}, {pr*stock:+.2f}"))
out = pd.DataFrame(rows, columns=["item","value"])
out.to_csv(HERE/"adr_joint_results_v3.csv", index=False); out.to_csv(B02/"adr_joint_results_v3.csv", index=False)
pd.set_option("display.max_colwidth", 260); pd.set_option("display.width", 400); print(out.to_string())
