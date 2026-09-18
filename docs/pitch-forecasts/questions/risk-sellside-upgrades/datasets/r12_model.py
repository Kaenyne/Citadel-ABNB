"""R12 decomposition: P(>=3 rating upgrades to Buy-equivalent in the tracked feed, 17 Sep - 15 Dec 2026, OR the feed-convention
mean target reaches >= $190 at any feed pull in the window).

Two legs, jointly simulated over the 5 Nov print branches:
  (A) upgrade counts: negative-binomial pre-print (17 Sep - 4 Nov) and post-print (5 Nov - 15 Dec) counts, the post-print mean
      by print branch (upgrades cluster on print days and follow the day-1 sign: D note s.5, datasets/upgrade_base_rates.json);
  (B) mean target: the S04 tape-lag block replicated verbatim from ../close-15dec-2026/datasets/abnb_path_mixture.py (same
      PARAMS, same seed convention) with the mean target evaluated at three checkpoints (4 Nov, ~25 Nov, 15 Dec) so that the
      any-day reading is the max of the three (the tape is stepwise: same-day print revisions, then a 1-2 month lag).
The two legs share the print branch and, within a branch, the day-1 move (the target chase is 0.40 x day-1; the post-print
upgrade count scales with the same draw). Seed 20260917, n 400,000.
Run: py -3.13 docs/pitch-forecasts/questions/risk-sellside-upgrades/datasets/r12_model.py
"""
import numpy as np, json, csv, math, pathlib, copy
HERE = pathlib.Path(__file__).resolve().parent
SEED = 20260917; N = 400_000
QS = [5, 10, 25, 50, 75, 90, 95]

# S02/S04 master parameters (copied, not imported, so this script is dependency-free; see the S02 log claim 19 and S04 claim 33)
S02 = dict(
    spot=167.51, sessions_pre=35, sessions_post_to_dec15=27, bg_vol_ann=0.29, equity_drift_ann=0.03,
    scen={"accel": dict(p=0.24, d1=4.0, sd=7.5, post=-2.0),
          "flat": dict(p=0.14, d1=-1.0, sd=7.5, post=-1.0),
          "decel_ok": dict(p=0.10, d1=-2.5, sd=7.5, post=-1.0),
          "decel_below": dict(p=0.52, d1=-6.0, sd=7.5, post=-2.5)},
    tape=dict(b0=0.075, b1=0.13, b2=0.10, chase=0.40, known_lag_terms=(0.13 + 0.10) * (-0.068) + 0.10 * 0.206 + 3 * 0.0005,
              stale_refresh=0.005, resid_sd=0.035, base_mean_target=183.22, base_feed_asis=181.81),
)

def run(seed=SEED, n=N, params=S02, pre_mu=0.7, post_mu=(2.0, 1.0, 0.7, 0.35), post_day1_beta=0.06, overdisp=1.6,
        thr_T=190.0, any_day=True, any_day_ratio=1.15, verbose=False):
    """pre_mu: mean upgrades-to-Buy 17 Sep - 4 Nov (7 weeks, no print). post_mu: by branch (accel / flat / decel_ok /
    decel_below), 5 Nov - 15 Dec (6 weeks, print inside). post_day1_beta: log-mean sensitivity of the post-print count to the
    realised day-1 move in points (a +10% day raises the mean by exp(0.6) = 1.8x within the branch). overdisp: NB var/mean."""
    rng = np.random.default_rng(seed)
    p = copy.deepcopy(params); dt = 1 / 252; v = p["bg_vol_ann"]; mu = p["equity_drift_ann"]
    def diff(k): return (mu - 0.5 * v * v) * k * dt + v * math.sqrt(k * dt) * rng.standard_normal(n)
    names = list(p["scen"]); probs = np.array([p["scen"][s]["p"] for s in names]); probs = probs / probs.sum()
    z = rng.choice(len(names), size=n, p=probs)
    g = lambda key: np.array([p["scen"][s][key] for s in names])[z] / 100
    d1_mu, d1_sd, post_drift = g("d1"), g("sd"), g("post")
    r_pre = diff(p["sessions_pre"])
    day1_simple = d1_mu + d1_sd * rng.standard_normal(n)
    r_day1 = np.log1p(day1_simple)
    # post-print block split 13 + 14 sessions
    r_post_a = np.log1p(post_drift) * (13 / 27) + diff(13)
    r_post_b = np.log1p(post_drift) * (14 / 27) + diff(14)
    r_post = r_post_a + r_post_b
    P_dec = p["spot"] * np.exp(r_pre + r_day1 + r_post)
    # S04 tape blocks
    f = 21 / 35
    p1 = f * r_pre + math.sqrt(f * (1 - f)) * v * math.sqrt(p["sessions_pre"] * dt) * rng.standard_normal(n)
    p2pre = r_pre - p1
    t = p["tape"]; rs = t["resid_sd"]
    # residual as a random walk over the window: 36 of 63 sessions by 4 Nov, 49 by ~25 Nov, 63 by 15 Dec
    e1 = rs * math.sqrt(36 / 63) * rng.standard_normal(n)
    e2 = e1 + rs * math.sqrt(13 / 63) * rng.standard_normal(n)
    e3 = e2 + rs * math.sqrt(14 / 63) * rng.standard_normal(n)
    kl = t["known_lag_terms"]
    lnT_nov4 = kl * (36 / 63) + (t["b0"] + t["b1"] + t["b2"]) * p1 + (t["b0"] + t["b1"]) * p2pre + t["stale_refresh"] * 0.3 + e1
    lnT_nov25 = kl * (49 / 63) + (t["b0"] + t["b1"] + t["b2"]) * p1 + (t["b0"] + t["b1"] + 0.5 * t["b2"]) * p2pre + t["chase"] * r_day1 \
        + (t["b0"] + 0.5 * t["b1"]) * r_post_a + t["stale_refresh"] * 0.8 + e2
    lnT_dec = kl + (t["b0"] + t["b1"] + t["b2"]) * p1 + (t["b0"] + t["b1"]) * p2pre + t["chase"] * r_day1 \
        + (t["b0"] + 0.5 * t["b1"]) * r_post + t["stale_refresh"] + e3
    base = t["base_mean_target"]
    T_nov4, T_nov25, T_dec = base * np.exp(lnT_nov4), base * np.exp(lnT_nov25), base * np.exp(lnT_dec)
    T_max = np.maximum(np.maximum(T_nov4, T_nov25), T_dec)   # three-checkpoint construction, reported only (overstates: see log s.4)
    # any-day reading: the D panel shows P(running max >= +3.7%) / P(end >= +3.7%) = 1.22 (all 63-session windows) and 1.12 (2023+);
    # implemented monotonically: the paths that finished closest below the threshold are the ones that touched it
    p_end = (T_dec >= thr_T).mean()
    thr_lower = np.quantile(T_dec, 1 - min(any_day_ratio * p_end, 0.999)) if any_day else thr_T
    T_leg = (T_dec >= thr_lower)
    # upgrade counts
    def nb(m):
        if overdisp <= 1.0: return rng.poisson(m)
        r = m / (overdisp - 1.0); q = r / (r + m); return rng.negative_binomial(r, q)
    pre = nb(np.full(n, pre_mu))
    mus = np.array(post_mu)[z] * np.exp(post_day1_beta * (day1_simple * 100 - d1_mu * 100))   # within-branch day-1 modulation
    post = nb(mus)
    n_up = pre + post
    up_leg = n_up >= 3
    yes = up_leg | T_leg
    out = dict(p=float(yes.mean()), p_up=float(up_leg.mean()), p_T=float(T_leg.mean()), p_T_dec15_only=float((T_dec >= thr_T).mean()),
               p_both=float((up_leg & T_leg).mean()), p_T_three_checkpoint=float((T_max >= thr_T).mean()), thr_lower=float(thr_lower),
               by_branch={k: float(yes[z == i].mean()) for i, k in enumerate(names)},
               by_branch_up={k: float(up_leg[z == i].mean()) for i, k in enumerate(names)},
               by_branch_T={k: float(T_leg[z == i].mean()) for i, k in enumerate(names)},
               by_branch_T_dec15={k: float((T_dec[z == i] >= thr_T).mean()) for i, k in enumerate(names)},
               mean_upgrades=float(n_up.mean()), P_upgrades={str(k): float((n_up == k).mean()) for k in range(0, 6)},
               P_upgrades_ge={str(k): float((n_up >= k).mean()) for k in range(1, 6)},
               T_dec_pct={str(q): float(np.percentile(T_dec, q)) for q in QS},
               T_max_pct={str(q): float(np.percentile(T_max, q)) for q in QS},
               S04_check_P_T_le_176_8=float((T_dec <= 176.8).mean()),
               E_price_dec15_given_yes=float(P_dec[yes].mean()), E_price_dec15_uncond=float(P_dec.mean()),
               median_price_dec15_given_yes=float(np.median(P_dec[yes])), median_price_dec15_uncond=float(np.median(P_dec)),
               P_branch_given_yes={k: float(((z == i) & yes).sum() / yes.sum()) for i, k in enumerate(names)},
               P_yes_given_day1_ge5=float(yes[day1_simple >= 0.05].mean()), P_yes_given_day1_le_m5=float(yes[day1_simple <= -0.05].mean()))
    if verbose: print(json.dumps(out, indent=1))
    return out

if __name__ == "__main__":
    base = run(verbose=True)
    sens = [("base", {}),
            ("pre-print mean 0.35 (2023-25 off-print rate)", dict(pre_mu=0.35)), ("pre-print mean 1.2 (trailing-12m rate, no pool limit)", dict(pre_mu=1.2)),
            ("post-print means halved", dict(post_mu=(1.0, 0.5, 0.35, 0.175))), ("post-print means x1.5", dict(post_mu=(3.0, 1.5, 1.05, 0.525))),
            ("post-print means flat 0.93 (2023+ print-window mean, no branch)", dict(post_mu=(0.93, 0.93, 0.93, 0.93))),
            ("no within-branch day-1 modulation", dict(post_day1_beta=0.0)), ("day-1 modulation 0.12", dict(post_day1_beta=0.12)),
            ("Poisson counts", dict(overdisp=1.0)), ("overdispersion 2.5", dict(overdisp=2.5)),
            ("target leg on 15 Dec only (no any-day reading)", dict(any_day=False)),
            ("any-day ratio 1.22 (all-history)", dict(any_day_ratio=1.22)), ("any-day ratio 1.12 (2023+)", dict(any_day_ratio=1.12)),
            ("target threshold 192 (feed as-is base: 181.81 needs +4.5%)", dict(thr_T=190.0 * 183.22 / 181.81)),
            ("P(accel) 0.40 (Street-like)", dict(params={**S02, "scen": {"accel": dict(p=0.40, d1=4.0, sd=7.5, post=-2.0), "flat": dict(p=0.12, d1=-1.0, sd=7.5, post=-1.0), "decel_ok": dict(p=0.10, d1=-2.5, sd=7.5, post=-1.0), "decel_below": dict(p=0.38, d1=-6.0, sd=7.5, post=-2.5)}})),
            ("P(accel) 0.13 (nowcast centre 9.75)", dict(params={**S02, "scen": {"accel": dict(p=0.13, d1=4.0, sd=7.5, post=-2.0), "flat": dict(p=0.14, d1=-1.0, sd=7.5, post=-1.0), "decel_ok": dict(p=0.12, d1=-2.5, sd=7.5, post=-1.0), "decel_below": dict(p=0.61, d1=-6.0, sd=7.5, post=-2.5)}})),
            ("print chase 0.60", dict(params={**S02, "tape": {**S02["tape"], "chase": 0.60}})), ("print chase 0.20", dict(params={**S02, "tape": {**S02["tape"], "chase": 0.20}})),
            ("tape residual sd 5%", dict(params={**S02, "tape": {**S02["tape"], "resid_sd": 0.05}})),
            ("day-1 means unshrunk (accel +6, decel-below -8)", dict(params={**S02, "scen": {"accel": dict(p=0.24, d1=6.0, sd=7.5, post=-2.0), "flat": dict(p=0.14, d1=-1.0, sd=7.5, post=-1.0), "decel_ok": dict(p=0.10, d1=-4.0, sd=7.5, post=-1.0), "decel_below": dict(p=0.52, d1=-8.0, sd=7.5, post=-2.5)}})),
            ("day-1 means market-neutral (all 0)", dict(params={**S02, "scen": {"accel": dict(p=0.24, d1=0.0, sd=7.5, post=-2.0), "flat": dict(p=0.14, d1=0.0, sd=7.5, post=-1.0), "decel_ok": dict(p=0.10, d1=0.0, sd=7.5, post=-1.0), "decel_below": dict(p=0.52, d1=0.0, sd=7.5, post=-2.5)}})),
            ("joint bull: accel 0.40, post x1.5, pre 1.2, chase 0.6", dict(pre_mu=1.2, post_mu=(3.0, 1.5, 1.05, 0.525), params={**S02, "tape": {**S02["tape"], "chase": 0.60}, "scen": {"accel": dict(p=0.40, d1=4.0, sd=7.5, post=-2.0), "flat": dict(p=0.12, d1=-1.0, sd=7.5, post=-1.0), "decel_ok": dict(p=0.10, d1=-2.5, sd=7.5, post=-1.0), "decel_below": dict(p=0.38, d1=-6.0, sd=7.5, post=-2.5)}})),
            ("joint bear: accel 0.13, post halved, pre 0.35, chase 0.2, 15 Dec only", dict(pre_mu=0.35, post_mu=(1.0, 0.5, 0.35, 0.175), any_day=False, params={**S02, "tape": {**S02["tape"], "chase": 0.20}, "scen": {"accel": dict(p=0.13, d1=4.0, sd=7.5, post=-2.0), "flat": dict(p=0.14, d1=-1.0, sd=7.5, post=-1.0), "decel_ok": dict(p=0.12, d1=-2.5, sd=7.5, post=-1.0), "decel_below": dict(p=0.61, d1=-6.0, sd=7.5, post=-2.5)}}))]
    rows = []
    with open(HERE / "r12_sensitivity.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["case", "p_yes", "p_upgrades_leg", "p_target_leg", "p_target_leg_dec15_only"])
        for name, kw in sens:
            r = run(**kw); wr.writerow([name, round(r["p"], 3), round(r["p_up"], 3), round(r["p_T"], 3), round(r["p_T_dec15_only"], 3)])
            print("%-72s %.3f  up %.3f  T %.3f (15 Dec only %.3f)" % (name, r["p"], r["p_up"], r["p_T"], r["p_T_dec15_only"]))
    json.dump(base, open(HERE / "r12_summary.json", "w"), indent=1)
