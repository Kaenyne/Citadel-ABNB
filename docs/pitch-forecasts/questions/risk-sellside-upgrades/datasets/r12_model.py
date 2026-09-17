"""R12 decomposition: P(>=3 rating upgrades to Buy-equivalent in the feed, 17 Sep - 15 Dec 2026, OR the feed-convention
mean target reaches >= $190 by 15 Dec). Monte Carlo over the 5 Nov print branches (S01/S02 weights), Poisson upgrade
counts pre- and post-print with branch-dependent means, and the S04 target model's by-branch P(T >= 190) with a
path-max premium. Seed 20260917. Run: py -3.13 docs/pitch-forecasts/questions/risk-sellside-upgrades/datasets/r12_model.py"""
import numpy as np, json, csv, pathlib
HERE = pathlib.Path(__file__).resolve().parent; N = 400_000

def run(seed=20260917, w=(0.24, 0.12, 0.12, 0.52), pre_mu=0.7, post_mu=(2.0, 1.0, 0.7, 0.3),
        pT=(0.55, 0.30, 0.16, 0.10), path_prem=0.02, overdisp=1.6, rho=0.5):
    """w: branch weights accel / flat / decel-guide-ok / decel-guide-below (S02 day1_mixture, flat and decel-ok merged
    from 0.14+0.10 to 0.12+0.12 to match S01's 0.24/0.12/0.64 with C01's 0.78 guide-below given decel).
    pre_mu: Poisson mean of upgrades-to-Buy 17 Sep - 4 Nov (7 weeks). post_mu: by branch, 5 Nov - 15 Dec.
    pT: P(mean target >= 190 on 15 Dec | branch) from S04 (weighted 0.235); path_prem adds the any-day premium.
    overdisp: negative-binomial variance/mean (upgrades cluster on print days). rho: within-branch correlation
    between the upgrade count and the target leg (both driven by the day-1 move)."""
    rng = np.random.default_rng(seed)
    b = rng.choice(4, size=N, p=np.array(w)/sum(w))
    def nb(mu):
        if overdisp <= 1.0: return rng.poisson(mu)
        r = mu/(overdisp-1.0); p = r/(r+mu); return rng.negative_binomial(r, p)
    pre = nb(np.full(N, pre_mu))
    mus = np.array(post_mu)[b]
    # shared shock z drives both the post-print count and the target leg within a branch
    z = rng.standard_normal(N)
    post = nb(mus*np.exp(0.5*z - 0.125))            # lognormal-modulated mean, E preserved
    n_up = pre + post
    pt = np.array(pT)[b] + path_prem
    # target leg: latent normal correlated with z
    u = rho*z + np.sqrt(1-rho**2)*rng.standard_normal(N)
    from scipy.stats import norm
    T_yes = u > norm.ppf(1-pt)
    up_yes = n_up >= 3
    yes = up_yes | T_yes
    out = dict(p=float(yes.mean()), p_up=float(up_yes.mean()), p_T=float(T_yes.mean()), p_both=float((up_yes&T_yes).mean()),
               by_branch={k: float(yes[b==i].mean()) for i,k in enumerate(["accel","flat","decel_ok","decel_below"])},
               by_branch_up={k: float(up_yes[b==i].mean()) for i,k in enumerate(["accel","flat","decel_ok","decel_below"])},
               mean_upgrades=float(n_up.mean()), P_upgrades={str(k): float((n_up==k).mean()) for k in range(0,5)})
    return out

if __name__ == "__main__":
    base = run(); print(json.dumps(base, indent=1))
    sens = [("base", {}),
            ("pre-print mean 0.3 (2023-25 rate)", dict(pre_mu=0.3)), ("pre-print mean 1.2 (2026 rate)", dict(pre_mu=1.2)),
            ("post-print means halved", dict(post_mu=(1.0,0.5,0.35,0.15))), ("post-print means x1.5", dict(post_mu=(3.0,1.5,1.05,0.45))),
            ("P(accel) 0.40 (Street-like)", dict(w=(0.40,0.12,0.10,0.38))), ("P(accel) 0.13", dict(w=(0.13,0.12,0.14,0.61))),
            ("target leg by branch -30%", dict(pT=(0.385,0.21,0.11,0.07))), ("target leg by branch +30%", dict(pT=(0.715,0.39,0.21,0.13))),
            ("no path premium", dict(path_prem=0.0)), ("path premium 0.05", dict(path_prem=0.05)),
            ("Poisson (no overdispersion)", dict(overdisp=1.0)), ("overdispersion 2.5", dict(overdisp=2.5)),
            ("legs independent (rho 0)", dict(rho=0.0)), ("legs tightly linked (rho 0.9)", dict(rho=0.9)),
            ("joint bull: accel 0.40, post x1.5, pre 1.2, pT +30%", dict(w=(0.40,0.12,0.10,0.38), post_mu=(3.0,1.5,1.05,0.45), pre_mu=1.2, pT=(0.715,0.39,0.21,0.13))),
            ("joint bear: accel 0.13, post halved, pre 0.3, pT -30%", dict(w=(0.13,0.12,0.14,0.61), post_mu=(1.0,0.5,0.35,0.15), pre_mu=0.3, pT=(0.385,0.21,0.11,0.07)))]
    with open(HERE/"r12_sensitivity.csv","w",newline="") as f:
        wr = csv.writer(f); wr.writerow(["case","p_yes","p_upgrades_leg","p_target_leg"])
        for name, kw in sens:
            r = run(**kw); wr.writerow([name, round(r["p"],3), round(r["p_up"],3), round(r["p_T"],3)]); print("%-60s %.3f  up %.3f  T %.3f" % (name, r["p"], r["p_up"], r["p_T"]))
    json.dump(base, open(HERE/"r12_summary.json","w"), indent=1)
