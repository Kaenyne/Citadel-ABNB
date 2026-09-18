"""R12 revision 2 (audit A13 response). Revision 1 is r12_model.py (untouched, with its CSV/JSON outputs).
Same two-leg construction (upgrade counts + S04 tape block over the 5 Nov print branches), rebuilt on the run's CURRENT inputs:
  - S02 revision 2 price path (../close-15dec-2026/datasets/abnb_path_mixture_v2.py PARAMS): print-state weights
    0.32 / 0.10 / 0.13 / 0.45, day-1 means +4.0 / -1.0 / -2.5 / -6.0 with the within-branch sd solved from the variance
    identity so the unconditional day-1 sd is 9.5% (8.451), post-print drifts -1.5 / -0.5 / -0.5 / -1.0 over 26 sessions,
    36 pre-print sessions, 30% background vol, 6.97% total drift (A13-01)
  - S04 revision 2 tape residual sd 5.0% (A13-01); p1 = 21 of the 36 pre sessions
  - feed capture 0.85 on every modelled count, the convention B11 uses on the same feed (A13-06)
  - post-print branch means 1.8 / 0.9 / 0.6 / 0.3: the midpoint of the revision-1 regime-lifted means (2.0/1.0/0.7/0.35)
    and the empirical 2023+ print-window post counts by day-1 sign (1.67 up / 0.9 / 0.5 / 0.2; A13-07)
  - any-day leg kept at the measured running-max ratio 1.15, applied rank-preservingly (A13-10; stated, not changed)
Sensitivities include the revision-1 parameter set (bridge), the auditor's construction (capture 0.85 + empirical means),
and the A09 revision-2 adopted print states (accel 0.26 / flat 0.10 / decel-ok 0.15 / decel-below 0.48).
Seed 20260917, n 400,000. Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/risk-sellside-upgrades/datasets/r12_model_v2.py
"""
import numpy as np, json, csv, math, pathlib, copy
HERE = pathlib.Path(__file__).resolve().parent
SEED = 20260917; N = 400_000
QS = [5, 10, 25, 50, 75, 90, 95]
S01_UNCOND_DAY1_SD = 9.5

S02 = dict(   # S02/S04 revision 2 (abnb_path_mixture_v2.py PARAMS), copied not imported
    spot=167.51, sessions_pre=36, sessions_post_to_dec15=26, bg_vol_ann=0.30, total_drift_ann=0.0697, sessions_p1=21,
    scen={"accel": dict(p=0.32, d1=4.0, post=-1.5),
          "flat": dict(p=0.10, d1=-1.0, post=-0.5),
          "decel_ok": dict(p=0.13, d1=-2.5, post=-0.5),
          "decel_below": dict(p=0.45, d1=-6.0, post=-1.0)},
    day1_sd_within=None,
    tape=dict(b0=0.075, b1=0.13, b2=0.10, chase=0.40, known_lag_terms=(0.13 + 0.10) * (-0.068) + 0.10 * 0.206 + 3 * 0.0005,
              stale_refresh=0.005, resid_sd=0.05, base_mean_target=183.22, base_feed_asis=181.81),
)
S02_REV1 = dict(  # revision-1 parameter set, for the bridge only
    spot=167.51, sessions_pre=35, sessions_post_to_dec15=27, bg_vol_ann=0.29, total_drift_ann=0.03, sessions_p1=21,
    scen={"accel": dict(p=0.24, d1=4.0, post=-2.0), "flat": dict(p=0.14, d1=-1.0, post=-1.0),
          "decel_ok": dict(p=0.10, d1=-2.5, post=-1.0), "decel_below": dict(p=0.52, d1=-6.0, post=-2.5)},
    day1_sd_within=7.5,
    tape=dict(S02["tape"], resid_sd=0.035),
)

def within_sd(p):
    if p.get("day1_sd_within") is not None: return p["day1_sd_within"]
    names = list(p["scen"]); pr = np.array([p["scen"][s]["p"] for s in names]); pr = pr / pr.sum()
    m = np.array([p["scen"][s]["d1"] for s in names]); vb = float(np.sum(pr * (m - np.sum(pr * m)) ** 2))
    return math.sqrt(max(S01_UNCOND_DAY1_SD ** 2 - vb, 1.0))

def with_probs(params, a, fl, d, b):
    q = copy.deepcopy(params)
    for s, v in zip(q["scen"], (a, fl, d, b)): q["scen"][s]["p"] = v
    return q

def run(seed=SEED, n=N, params=S02, pre_mu=0.7, post_mu=(1.8, 0.9, 0.6, 0.3), post_day1_beta=0.06, overdisp=1.6,
        capture=0.85, thr_T=190.0, any_day=True, any_day_ratio=1.15, verbose=False):
    rng = np.random.default_rng(seed)
    p = copy.deepcopy(params); dt = 1 / 252; v = p["bg_vol_ann"]; mu = p["total_drift_ann"]
    def diff(k): return (mu - 0.5 * v * v) * k * dt + v * math.sqrt(k * dt) * rng.standard_normal(n)
    names = list(p["scen"]); probs = np.array([p["scen"][s]["p"] for s in names]); probs = probs / probs.sum()
    z = rng.choice(len(names), size=n, p=probs)
    g = lambda key: np.array([p["scen"][s][key] for s in names])[z] / 100
    d1_mu, post_drift = g("d1"), g("post")
    sd_w = within_sd(p) / 100
    r_pre = diff(p["sessions_pre"])
    day1_simple = d1_mu + sd_w * rng.standard_normal(n)
    r_day1 = np.log1p(day1_simple)
    r_post = np.log1p(post_drift) + diff(p["sessions_post_to_dec15"])
    P_dec = p["spot"] * np.exp(r_pre + r_day1 + r_post)
    # S04 tape block (revision 2): p1 = first 21 sessions, p2pre = the rest of the pre-print block
    f = p["sessions_p1"] / p["sessions_pre"]
    p1 = f * r_pre + math.sqrt(f * (1 - f)) * v * math.sqrt(p["sessions_pre"] * dt) * rng.standard_normal(n)
    p2pre = r_pre - p1
    t = p["tape"]
    lnT_dec = (t["known_lag_terms"] + (t["b0"] + t["b1"] + t["b2"]) * p1 + (t["b0"] + t["b1"]) * p2pre + t["chase"] * r_day1
               + (t["b0"] + 0.5 * t["b1"]) * r_post + t["stale_refresh"] + t["resid_sd"] * rng.standard_normal(n))
    T_dec = t["base_mean_target"] * np.exp(lnT_dec)
    # any-day reading: P(running max >= thr) = ratio x P(end >= thr), applied rank-preservingly (the paths that finish
    # closest below the threshold are taken as the ones that touched it) - an assumption, stated in the log (A13-10)
    p_end = float((T_dec >= thr_T).mean())
    thr_lower = float(np.quantile(T_dec, 1 - min(any_day_ratio * p_end, 0.999))) if any_day else thr_T
    T_leg = T_dec >= thr_lower
    def nb(m):
        if overdisp <= 1.0: return rng.poisson(m)
        r = m / (overdisp - 1.0); q = r / (r + m); return rng.negative_binomial(r, q)
    pre = nb(np.full(n, pre_mu * capture))
    mus = np.array(post_mu)[z] * np.exp(post_day1_beta * (day1_simple * 100 - d1_mu * 100)) * capture
    post = nb(mus)
    n_up = pre + post
    up_leg = n_up >= 3
    yes = up_leg | T_leg
    out = dict(p=float(yes.mean()), p_up=float(up_leg.mean()), p_T=float(T_leg.mean()), p_T_dec15_only=p_end,
               p_both=float((up_leg & T_leg).mean()), thr_lower=thr_lower, day1_sd_within_pct=within_sd(p),
               by_branch={k: float(yes[z == i].mean()) for i, k in enumerate(names)},
               by_branch_up={k: float(up_leg[z == i].mean()) for i, k in enumerate(names)},
               by_branch_T={k: float(T_leg[z == i].mean()) for i, k in enumerate(names)},
               by_branch_T_dec15={k: float((T_dec[z == i] >= thr_T).mean()) for i, k in enumerate(names)},
               mean_upgrades=float(n_up.mean()), P_upgrades={str(k): float((n_up == k).mean()) for k in range(0, 6)},
               P_upgrades_ge={str(k): float((n_up >= k).mean()) for k in range(1, 6)},
               T_dec_pct={str(q): float(np.percentile(T_dec, q)) for q in QS},
               S04_check_P_T_le_176_8=float((T_dec <= 176.8).mean()),
               E_price_dec15_given_yes=float(P_dec[yes].mean()), E_price_dec15_uncond=float(P_dec.mean()),
               median_price_dec15_given_yes=float(np.median(P_dec[yes])), median_price_dec15_uncond=float(np.median(P_dec)),
               P_branch_given_yes={k: float(((z == i) & yes).sum() / yes.sum()) for i, k in enumerate(names)},
               P_yes_given_day1_ge5=float(yes[day1_simple >= 0.05].mean()), P_yes_given_day1_le_m5=float(yes[day1_simple <= -0.05].mean()),
               P_yes_given_day1_mid=float(yes[(day1_simple > -0.05) & (day1_simple < 0.05)].mean()))
    if verbose: print(json.dumps(out, indent=1))
    return out

if __name__ == "__main__":
    base = run(verbose=True)
    A09 = with_probs(S02, 0.261, 0.104, 0.152, 0.484)   # adopted_print_states_v2.json S01 states x S01 rev-2 P(below | decel) 0.761
    sens = [("base (revision 2)", {}),
            ("bridge: revision-1 parameters, capture 1.0, rev-1 post means", dict(params=S02_REV1, capture=1.0, post_mu=(2.0, 1.0, 0.7, 0.35))),
            ("bridge: rev-2 S02/S04 parameters only (capture 1.0, rev-1 post means)", dict(capture=1.0, post_mu=(2.0, 1.0, 0.7, 0.35))),
            ("bridge: rev-2 parameters + capture 0.85 (rev-1 post means)", dict(post_mu=(2.0, 1.0, 0.7, 0.35))),
            ("auditor: rev-2 parameters + capture 0.85 + empirical post means 1.67/0.9/0.5/0.2", dict(post_mu=(1.67, 0.9, 0.5, 0.2))),
            ("capture 1.0", dict(capture=1.0)), ("capture 0.70", dict(capture=0.70)),
            ("pre-print mean 0.35 (2023-25 off-print rate)", dict(pre_mu=0.35)), ("pre-print mean 1.2 (trailing-12m rate, no pool limit)", dict(pre_mu=1.2)),
            ("post-print means halved", dict(post_mu=(0.9, 0.45, 0.3, 0.15))), ("post-print means x1.5", dict(post_mu=(2.7, 1.35, 0.9, 0.45))),
            ("post-print means flat 0.93 (2023+ print-window mean, no branch)", dict(post_mu=(0.93, 0.93, 0.93, 0.93))),
            ("no within-branch day-1 modulation", dict(post_day1_beta=0.0)), ("day-1 modulation 0.12", dict(post_day1_beta=0.12)),
            ("Poisson counts", dict(overdisp=1.0)), ("overdispersion 2.5", dict(overdisp=2.5)),
            ("target leg on 15 Dec only (no any-day reading)", dict(any_day=False)),
            ("any-day ratio 1.185 (all-history, corrected)", dict(any_day_ratio=1.185)), ("any-day ratio 1.11 (2023+)", dict(any_day_ratio=1.11)),
            ("target threshold 192 (feed as-is base: 181.81 needs +4.5%)", dict(thr_T=190.0 * 183.22 / 181.81)),
            ("A09 rev-2 adopted print states 0.26/0.10/0.15/0.48", dict(params=A09)),
            ("P(accel) 0.40 (Street-like)", dict(params=with_probs(S02, 0.40, 0.10, 0.11, 0.39))),
            ("P(accel) 0.22 (R02 alt-data leg only)", dict(params=with_probs(S02, 0.22, 0.10, 0.15, 0.53))),
            ("print chase 0.60", dict(params={**S02, "tape": {**S02["tape"], "chase": 0.60}})), ("print chase 0.20", dict(params={**S02, "tape": {**S02["tape"], "chase": 0.20}})),
            ("tape residual sd 3.5% (revision 1)", dict(params={**S02, "tape": {**S02["tape"], "resid_sd": 0.035}})),
            ("tape residual sd 6.68% (Astra two-regressor)", dict(params={**S02, "tape": {**S02["tape"], "resid_sd": 0.0668}})),
            ("day-1 means unshrunk (accel +6, decel-ok -4, decel-below -8)", dict(params={**S02, "scen": {"accel": dict(p=0.32, d1=6.0, post=-1.5), "flat": dict(p=0.10, d1=-1.0, post=-0.5), "decel_ok": dict(p=0.13, d1=-4.0, post=-0.5), "decel_below": dict(p=0.45, d1=-8.0, post=-1.0)}})),
            ("day-1 means market-neutral (all 0)", dict(params={**S02, "scen": {"accel": dict(p=0.32, d1=0.0, post=-1.5), "flat": dict(p=0.10, d1=0.0, post=-0.5), "decel_ok": dict(p=0.13, d1=0.0, post=-0.5), "decel_below": dict(p=0.45, d1=0.0, post=-1.0)}})),
            ("within-branch day-1 sd 7.5 (revision 1)", dict(params={**S02, "day1_sd_within": 7.5})),
            ("joint bull: accel 0.40, post x1.5, pre 1.2, chase 0.6, capture 1.0", dict(pre_mu=1.2, post_mu=(2.7, 1.35, 0.9, 0.45), capture=1.0, params={**with_probs(S02, 0.40, 0.10, 0.11, 0.39), "tape": {**S02["tape"], "chase": 0.60}})),
            ("joint bear: accel 0.22, post halved, pre 0.35, chase 0.2, capture 0.7, 15 Dec only", dict(pre_mu=0.35, post_mu=(0.9, 0.45, 0.3, 0.15), capture=0.70, any_day=False, params={**with_probs(S02, 0.22, 0.10, 0.15, 0.53), "tape": {**S02["tape"], "chase": 0.20}}))]
    with open(HERE / "r12_v2_sensitivity.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["case", "p_yes", "p_upgrades_leg", "p_target_leg", "p_target_leg_dec15_only", "mean_upgrades"])
        for name, kw in sens:
            r = run(**kw); wr.writerow([name, round(r["p"], 4), round(r["p_up"], 4), round(r["p_T"], 4), round(r["p_T_dec15_only"], 4), round(r["mean_upgrades"], 3)])
            print("%-84s %.4f  up %.4f  T %.4f (15 Dec only %.4f)  mean n %.2f" % (name, r["p"], r["p_up"], r["p_T"], r["p_T_dec15_only"], r["mean_upgrades"]))
    json.dump(base, open(HERE / "r12_v2_summary.json", "w"), indent=1)
