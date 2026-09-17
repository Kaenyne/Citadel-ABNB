"""B11 decomposition: P(>=3 rating downgrades to Hold/Sell-equivalent in the tracked feed, 17 Sep - 15 Dec 2026).
Mirror of R12's r12_model.py (upgrades leg) with the downgrade rates from datasets/downgrade_base_rates.json.
Structure: S02 print branches (accel 0.24 / flat 0.14 / decel_ok 0.10 / decel_below 0.52) with the S02 day-1 draw and price
blocks (p1 = 16 Sep -> 14 Oct, p2pre -> 5 Nov, r_post 6 Nov -> 15 Dec); pre-print count NB(mean pre_mu x exp(-k_pre x p1))
(downgrades follow price falls: prior-21-session fall <= -10% raises the 90-day mean x1.35, base rates §2); post-print count
NB(mean post_mu[branch] x exp(-beta_d1 x (day1 - branch mean)) x exp(-k_post x r_post)); counts thinned by the feed's capture
rate (the feed drops about a third of intermediate actions; Phillip Securities' Aug 2026 Hold -> Reduce is not in it).
Seed 20260917, n 400,000. Run: py -3.13 docs/pitch-forecasts/questions/bonus-sellside-downgrades/datasets/b11_model.py
"""
import numpy as np, json, csv, math, pathlib, copy
HERE = pathlib.Path(__file__).resolve().parent
SEED = 20260917; N = 400_000
S02 = dict(spot=167.51, sessions_pre=35, sessions_post_to_dec15=27, bg_vol_ann=0.29, equity_drift_ann=0.03,
           scen={"accel": dict(p=0.24, d1=4.0, sd=7.5, post=-2.0), "flat": dict(p=0.14, d1=-1.0, sd=7.5, post=-1.0),
                 "decel_ok": dict(p=0.10, d1=-2.5, sd=7.5, post=-1.0), "decel_below": dict(p=0.52, d1=-6.0, sd=7.5, post=-2.5)})

def run(seed=SEED, n=N, params=S02, pre_mu=0.35, k_pre=3.0, post_mu=(0.15, 0.5, 0.7, 1.1), beta_d1=0.06, k_post=3.0,
        overdisp=1.6, capture=0.85, pool_scale=1.0, verbose=False):
    rng = np.random.default_rng(seed)
    p = copy.deepcopy(params); dt = 1/252; v = p["bg_vol_ann"]; mu = p["equity_drift_ann"]
    def diff(k): return (mu - 0.5*v*v)*k*dt + v*math.sqrt(k*dt)*rng.standard_normal(n)
    names = list(p["scen"]); probs = np.array([p["scen"][s]["p"] for s in names]); probs = probs/probs.sum()
    z = rng.choice(len(names), size=n, p=probs)
    g = lambda key: np.array([p["scen"][s][key] for s in names])[z]/100
    d1_mu, d1_sd, post_drift = g("d1"), g("sd"), g("post")
    r_pre = diff(p["sessions_pre"])
    day1 = d1_mu + d1_sd*rng.standard_normal(n); r_day1 = np.log1p(day1)
    r_post = np.log1p(post_drift) + diff(p["sessions_post_to_dec15"])
    P_dec = p["spot"]*np.exp(r_pre + r_day1 + r_post)
    f = 21/35; p1 = f*r_pre + math.sqrt(f*(1-f))*v*math.sqrt(p["sessions_pre"]*dt)*rng.standard_normal(n)
    def nb(m):
        if overdisp <= 1.0: return rng.poisson(m)
        r = m/(overdisp-1.0); q = r/(r+m); return rng.negative_binomial(r, q)
    m_pre = pre_mu*pool_scale*np.exp(-k_pre*np.minimum(p1, 0.0))                        # falls raise the rate; rises do not lower it below base
    m_post = np.array(post_mu)[z]*pool_scale*np.exp(-beta_d1*(day1*100 - d1_mu*100))*np.exp(-k_post*np.minimum(r_post, 0.0))
    pre, post = nb(m_pre), nb(m_post)
    if capture < 1.0:
        pre = rng.binomial(pre, capture); post = rng.binomial(post, capture)
    nd = pre + post; yes = nd >= 3
    out = dict(p=float(yes.mean()), mean_downgrades=float(nd.mean()), mean_pre=float(pre.mean()), mean_post=float(post.mean()),
               P_count={str(k): float((nd==k).mean()) for k in range(0,6)}, P_ge={str(k): float((nd>=k).mean()) for k in range(1,6)},
               by_branch={k: float(yes[z==i].mean()) for i,k in enumerate(names)},
               mean_by_branch={k: float(nd[z==i].mean()) for i,k in enumerate(names)},
               P_branch_given_yes={k: float(((z==i)&yes).sum()/yes.sum()) for i,k in enumerate(names)},
               P_yes_given_day1_le_m5=float(yes[day1<=-0.05].mean()), P_yes_given_day1_le_m8=float(yes[day1<=-0.08].mean()),
               P_yes_given_day1_ge5=float(yes[day1>=0.05].mean()), P_yes_given_day1_mid=float(yes[(day1>-0.05)&(day1<0.05)].mean()),
               P_yes_given_dec_le_150=float(yes[P_dec<=150].mean()), P_yes_given_dec_ge_180=float(yes[P_dec>=180].mean()),
               E_price_dec15_given_yes=float(P_dec[yes].mean()), E_price_dec15_uncond=float(P_dec.mean()),
               median_price_dec15_given_yes=float(np.median(P_dec[yes])), median_price_dec15_uncond=float(np.median(P_dec)),
               E_day1_given_yes=float(day1[yes].mean()*100), E_day1_uncond=float(day1.mean()*100))
    if verbose: print(json.dumps(out, indent=1))
    return out

def scen(a, fl, d, b):
    q = copy.deepcopy(S02)
    for s, v_ in zip(q["scen"], (a, fl, d, b)): q["scen"][s]["p"] = v_
    return q

if __name__ == "__main__":
    base = run(verbose=True)
    sens = [("base", {}),
            ("pre-print mean 0.20 (trailing-12m: zero downgrades)", dict(pre_mu=0.20)), ("pre-print mean 0.55 (2021+ all-window rate)", dict(pre_mu=0.55)),
            ("post-print means halved", dict(post_mu=(0.075, 0.25, 0.35, 0.55))), ("post-print means x1.5", dict(post_mu=(0.225, 0.75, 1.05, 1.65))),
            ("post-print means flat 0.74 (all-print mean, no branch)", dict(post_mu=(0.74,)*4)),
            ("no day-1 modulation", dict(beta_d1=0.0)), ("day-1 modulation 0.12", dict(beta_d1=0.12)),
            ("no price-path modulation (k_pre = k_post = 0)", dict(k_pre=0.0, k_post=0.0)), ("price-path modulation doubled", dict(k_pre=6.0, k_post=6.0)),
            ("Poisson counts", dict(overdisp=1.0)), ("overdispersion 2.5 (Nov-2023-style clustering)", dict(overdisp=2.5)),
            ("feed capture 1.0", dict(capture=1.0)), ("feed capture 0.70", dict(capture=0.70)),
            ("pool scale 1.25 (22 Buys, Buy share at a series high)", dict(pool_scale=1.25)),
            ("P(accel) 0.40 (Street-like)", dict(params=scen(0.40, 0.12, 0.10, 0.38))), ("P(accel) 0.13 (nowcast centre 9.75)", dict(params=scen(0.13, 0.14, 0.12, 0.61))),
            ("day-1 means unshrunk (accel +6, decel-below -8)", dict(params={**S02, "scen": {"accel": dict(p=0.24, d1=6.0, sd=7.5, post=-2.0), "flat": dict(p=0.14, d1=-1.0, sd=7.5, post=-1.0), "decel_ok": dict(p=0.10, d1=-4.0, sd=7.5, post=-1.0), "decel_below": dict(p=0.52, d1=-8.0, sd=7.5, post=-2.5)}})),
            ("day-1 means market-neutral (all 0)", dict(params={**S02, "scen": {"accel": dict(p=0.24, d1=0.0, sd=7.5, post=-2.0), "flat": dict(p=0.14, d1=0.0, sd=7.5, post=-1.0), "decel_ok": dict(p=0.10, d1=0.0, sd=7.5, post=-1.0), "decel_below": dict(p=0.52, d1=0.0, sd=7.5, post=-2.5)}})),
            ("joint bear-for-stock: accel 0.13, post x1.5, pool 1.25, capture 1.0, overdisp 2.5", dict(post_mu=(0.225, 0.75, 1.05, 1.65), pool_scale=1.25, capture=1.0, overdisp=2.5, params=scen(0.13, 0.14, 0.12, 0.61))),
            ("joint bull-for-stock: accel 0.40, post halved, pre 0.20, capture 0.7", dict(pre_mu=0.20, post_mu=(0.075, 0.25, 0.35, 0.55), capture=0.70, params=scen(0.40, 0.12, 0.10, 0.38)))]
    with open(HERE/"b11_sensitivity.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["case", "p_yes", "mean_downgrades", "p_ge2", "p_yes_decel_below", "p_yes_accel"])
        for name, kw in sens:
            r = run(**kw); wr.writerow([name, round(r["p"],3), round(r["mean_downgrades"],3), round(r["P_ge"]["2"],3), round(r["by_branch"]["decel_below"],3), round(r["by_branch"]["accel"],3)])
            print("%-80s %.3f  mean %.2f  P>=2 %.3f  decel_below %.3f  accel %.3f" % (name, r["p"], r["mean_downgrades"], r["P_ge"]["2"], r["by_branch"]["decel_below"], r["by_branch"]["accel"]))
    json.dump(base, open(HERE/"b11_summary.json", "w"), indent=1)
