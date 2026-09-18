"""R07 + B02 revision 2 - ONE distribution for 3Q26 reported ADR y/y, both tails read from it (audit A10-03, A10-12, A10-13).
reported = card mix (-1.16, sd 0.35) + K fee-mechanics line (+0.17) + residual mixture + FX mixture + bias adjustment (+0.15 = half the
midpoint walk-forward bias -0.308, n 10). Residual mixture = B02's four branches (persistence 4.85 / momentum 5.35 / AR(1) 4.37 sd 0.94 /
lap-and-proxy reversion 3.6). numpy/pandas only; seed 20260917; n 400,000. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/risk-adr-residual-persists/datasets/adr_joint_model_v2.py
Writes adr_joint_results_v2.csv into both the R07 and B02 datasets folders. r07_model.py / b02_model.py and their outputs are left as the audit trail."""
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
# walk-forward errors (P1 paths, with K line)
p = pd.read_csv(ROOT/"data/processed/adrv3/P/P1_card_v3_backtest_paths.csv"); p2 = p[p.target=="t2_reported_usd_yoy"]
err = {}
for fx in ["midpoint","eur","baskets"]:
    q = p2[p2.fx_estimator==fx]; e = (q.v3_point_last_q_plus_K_line_measured_mix - q.actual).values
    err[fx] = (float(np.sqrt((e**2).mean())), float(e.mean()))
rows.append(("walk-forward midpoint RMSE, bias (model - actual), n", f"{err['midpoint'][0]:.3f}, {err['midpoint'][1]:+.3f}, {len(e)}"))
BIAS_ADJ = round(-err["midpoint"][1]/2, 2)   # +0.15
rows.append(("bias adjustment applied to the centre (half the walk-forward bias)", BIAS_ADJ))
# AR(1) on the residual (B02 claim 3)
h = pd.read_csv(ROOT/"data/processed/q3nowcast/H/adr_history_components.csv")
r = h.residual_pricing_pp.values; x, y = r[:-1], r[1:]
A = np.vstack([np.ones_like(x), x]).T; beta, *_ = np.linalg.lstsq(A, y, rcond=None)
innov_sd = float((y - A@beta).std(ddof=2)); ar1 = float(beta[0] + beta[1]*r[-1])
rows.append(("AR(1) const, rho, innovation sd, 3Q26 point", f"{beta[0]:.3f}, {beta[1]:.3f}, {innov_sd:.3f}, {ar1:.3f}"))
MIX_MU, MIX_SD, K = -1.16, 0.35, 0.17
W_RES = (0.45, 0.15, 0.25, 0.15); RES = ((4.85,0.55),(5.35,0.55),(ar1,innov_sd),(3.6,0.7))
W_FX = (0.50, 0.25, 0.25); FX = ((-0.43,0.33),(0.26,0.42),(-1.12,0.46))
def mc(mix_mu=MIX_MU, mix_sd=MIX_SD, k=K, bias=BIAS_ADJ, w_res=W_RES, res=RES, w_fx=W_FX, fx=FX, seed=20260917):
    g = np.random.default_rng(seed)
    mix = g.normal(mix_mu, mix_sd, N)
    u = g.random(N); c = np.cumsum(w_res)
    resid = np.where(u<c[0], g.normal(*res[0],N), np.where(u<c[1], g.normal(*res[1],N), np.where(u<c[2], g.normal(*res[2],N), g.normal(*res[3],N))))
    v = g.random(N); d = np.cumsum(w_fx)
    f = np.where(v<d[0], g.normal(*fx[0],N), np.where(v<d[1], g.normal(*fx[1],N), g.normal(*fx[2],N)))
    return mix + k + resid + f + bias, f, resid, mix + k + resid + bias   # reported, fx, residual, ex-FX
rep, f, res, exfx = mc()
def summ(lab, rep):
    return (f"{lab}: P(>=4.4) [R07], P(<=2.0) [B02], median, mean, sd",
            f"{(rep>=HI).mean():.4f}, {(rep<=LO).mean():.4f}, {np.median(rep):.3f}, {rep.mean():.3f}, {rep.std():.3f}")
rows.append(summ("JOINT MODEL revision 2", rep))
rows.append(("joint: P(>=4.0), P(>=3.4 Street mean), P(<=2.5), P(<=1.0), P(<=0)", f"{(rep>=4.0).mean():.4f}, {(rep>=3.4).mean():.4f}, {(rep<=2.5).mean():.4f}, {(rep<=1.0).mean():.4f}, {(rep<=0).mean():.4f}"))
rows.append(("joint: E[reported | >=4.4], E[reported | <=2.0]", f"{rep[rep>=HI].mean():.3f}, {rep[rep<=LO].mean():.3f}"))
rows.append(("joint: p5/p10/p25/p50/p75/p90/p95", ", ".join(f"{np.percentile(rep,q):.2f}" for q in [5,10,25,50,75,90,95])))
# conditionals on the disclosed FX effect
for lab, m in [("fx >= +0.2 (baskets right)", f>=0.2), ("fx in (-0.6,-0.2) (midpoint)", (f>-0.6)&(f<-0.2)), ("fx in (-1.0,-0.2)", (f>-1.0)&(f<-0.2)), ("fx <= -1.0 (euro right)", f<=-1.0), ("fx >= -0.2", f>=-0.2)]:
    rows.append((f"joint | {lab}: mass, P(>=4.4), P(<=2.0)", f"{m.mean():.3f}, {(rep[m]>=HI).mean():.3f}, {(rep[m]<=LO).mean():.3f}"))
# conditionals on the ex-FX letter integer (model ex-FX = mix + K + residual + bias)
for lab, m in [("ex-FX 5pct (>=4.5)", exfx>=4.5), ("ex-FX 4pct (3.5-4.5)", (exfx>=3.5)&(exfx<4.5)), ("ex-FX 3pct (2.5-3.5)", (exfx>=2.5)&(exfx<3.5)), ("ex-FX 2pct or lower (<2.5)", exfx<2.5)]:
    rows.append((f"joint | {lab}: mass, P(>=4.4), P(<=2.0)", f"{m.mean():.3f}, {(rep[m]>=HI).mean():.3f}, {(rep[m]<=LO).mean():.3f}"))
for lab, m in [("residual <= 3.6", res<=3.6), ("residual 3.6-4.5", (res>3.6)&(res<=4.5)), ("residual > 4.5", res>4.5)]:
    rows.append((f"joint | {lab}: mass, P(>=4.4), P(<=2.0)", f"{m.mean():.3f}, {(rep[m]>=HI).mean():.3f}, {(rep[m]<=LO).mean():.3f}"))
# sensitivities (each a full re-draw; both tails)
sens = [("no bias adjustment (raw model, K restored)", dict(bias=0.0)), ("full bias adjustment (+0.31)", dict(bias=0.31)),
        ("rev-1 R07 form: mix -1.15, no K, no bias, weights 0.55/0.20/0/0.25", dict(mix_mu=-1.15, k=0.0, bias=0.0, w_res=(0.55,0.20,0.0,0.25))),
        ("rev-1 B02 form: mix -1.15, no K, no bias", dict(mix_mu=-1.15, k=0.0, bias=0.0)),
        ("R07 residual weights 0.55/0.20/0/0.25", dict(w_res=(0.55,0.20,0.0,0.25))), ("reversion-heavy 0.30/0.10/0.35/0.25", dict(w_res=(0.30,0.10,0.35,0.25))),
        ("residual all persistence", dict(w_res=(1,0,0,0))), ("residual all momentum", dict(w_res=(0,1,0,0))), ("residual all AR(1)", dict(w_res=(0,0,1,0))), ("residual all mean-rev 3.6", dict(w_res=(0,0,0,1))),
        ("FX all midpoint", dict(w_fx=(1,0,0))), ("FX all baskets", dict(w_fx=(0,1,0))), ("FX all euro", dict(w_fx=(0,0,1))),
        ("mix -1.45 (geo drag at band low)", dict(mix_mu=-1.45)), ("mix -1.75 (LatAm mapped low)", dict(mix_mu=-1.75)), ("mix -0.94 (geo drag at band high)", dict(mix_mu=-0.94)), ("mix sd 0.6", dict(mix_sd=0.6)),
        ("K line 0 (fee mechanics not in ADR)", dict(k=0.0)), ("K line +0.93 (band top)", dict(k=0.93))]
for lab, kw in sens:
    rows.append(summ(f"sens {lab}", mc(**kw)[0]))
# Gaussian comparators
for lab, m_, s_ in [("N(3.43,0.93) with-K card raw", 3.43, 0.927), ("N(3.58,0.93) with-K card + half bias", 3.58, 0.927), ("N(3.74,0.93) bias-corrected", 3.74, 0.927), ("auditor N(3.50,1.05)", 3.50, 1.05)]:
    rows.append((f"gaussian {lab}: P(>=4.4), P(<=2.0)", f"{1-Phi((HI-m_)/s_):.4f}, {Phi((LO-m_)/s_):.4f}"))
# implied normal carrying both revision-2 tails
p_hi, p_lo = float((rep>=HI).mean()), float((rep<=LO).mean())
z1, z2 = NormalDist().inv_cdf(1-p_hi), NormalDist().inv_cdf(p_lo); sg = (HI-LO)/(z1-z2); mu_j = HI - z1*sg
rows.append(("normal carrying both revision-2 tails: mu, sd", f"{mu_j:.2f}, {sg:.2f}"))
# history counts (A10-22)
rows.append(("history 1Q23-2Q26: n, reported>=4.4, FX<=0 quarters, reported>=4.4 & FX<=0, reported<=2.0, reported<=2.0 & FX>=-0.5",
             f"{len(h)}, {int((h.adr_yoy_reported_pp>=4.4).sum())}, {int((h.fx_effect_pp<=0).sum())}, {int(((h.adr_yoy_reported_pp>=4.4)&(h.fx_effect_pp<=0)).sum())}, {int((h.adr_yoy_reported_pp<=2.0).sum())}, {int(((h.adr_yoy_reported_pp<=2.0)&(h.fx_effect_pp>=-0.5)).sum())}"))
e = pd.read_csv(ROOT/"data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv"); a = e[(e.quarter=="3Q26")&(e.metric=="adr_usd")].iloc[0]
sd_modl = (a.street_high_growth-a.street_low_growth)/4
rows.append(("MODL: n, low/mean/high growth, range/4 sd, P(>=4.4), P(<=2.0), 178.83 pct of range, 174.72 pct of range",
             f"{a.n_estimates}, {a.street_low_growth:.3f}/{a.street_mean_growth:.3f}/{a.street_high_growth:.3f}, {sd_modl:.3f}, {1-Phi((4.4-a.street_mean_growth)/sd_modl):.4f}, {Phi((2.0-a.street_mean_growth)/sd_modl):.4f}, {100*(178.83-a.street_low)/(a.street_high-a.street_low):.1f}, {100*(174.72-a.street_low)/(a.street_high-a.street_low):.1f}"))
rows.append(("MODL at the card RMSE 0.93: P(>=4.4), P(<=2.0)", f"{1-Phi((4.4-a.street_mean_growth)/0.927):.4f}, {Phi((2.0-a.street_mean_growth)/0.927):.4f}"))
out = pd.DataFrame(rows, columns=["item","value"])
out.to_csv(HERE/"adr_joint_results_v2.csv", index=False); out.to_csv(B02/"adr_joint_results_v2.csv", index=False)
pd.set_option("display.max_colwidth", 200); print(out.to_string())
