"""B11 revision 2 (audit A17 response). Revision 1 is b11_model.py (untouched, with its CSV/JSON outputs).
Same construction - pre-print + post-print negative-binomial downgrade counts over the 5 Nov print branches - rebuilt
on the run's CURRENT inputs and with the two calibration errors A17 found repaired:
  - S02 revision 2 price path (../close-15dec-2026/datasets/abnb_path_mixture_v2.py PARAMS): branch weights
    0.32 / 0.10 / 0.13 / 0.45, day-1 means +4.0 / -1.0 / -2.5 / -6.0 with the within-branch sd solved from the
    variance identity so the unconditional day-1 sd is S01's 9.5% (8.451), post-print drifts -1.5 / -0.5 / -0.5 / -1.0
    over 26 sessions, 36 pre-print sessions, 30% background vol, 6.97% total drift   (A17-05)
  - post-print branch means 0.085 / 0.525 / 0.625 / 0.965: the midpoint of the revision-1 judgement (0.15/0.5/0.7/1.1)
    and the feed's own print-window post-print means by day-1 sign (0.02 up>=5 / 0.55 small / 0.55 / 0.83 down<=-5),
    exactly the treatment R12 revision 2 gave its own post means   (A17-04)
  - pre-print mean 0.26 = the MEASURED 2023+ off-print rate over the 49-day pre-print block
    (3.5068/yr x 0.55 off-print share x 49/365 = 0.2589), not the revision-1 unlabelled 0.35   (A17-17)
  - RECENTRING (A17-04, the level error): the exponential price and day-1 modulations have E[exp(.)] > 1, so setting
    pre_mu / post_mu at unconditional rates and then modulating produced an unconditional mean ABOVE every base rate
    the log compared itself with (1.17 per 89 days = 4.8/yr against a measured print-shaped-window 0.74 = 3.0/yr).
    recentre=True divides each mean by the simulated E[modulation] (per branch for the post block), so the model's
    unconditional expected counts equal the named base rates by construction and the modulations only redistribute.
  - feed capture 0.85 kept: the run's shared convention with R12 revision 2 on the same feed (A17-03 accepted in part;
    the rates ARE feed-measured, so this is a stated ~2-3 point conservatism, not a second measurement).
Seed 20260917, n 400,000. Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/bonus-sellside-downgrades/datasets/b11_model_v2.py
"""
import numpy as np, json, csv, math, pathlib, copy
HERE = pathlib.Path(__file__).resolve().parent
SEED = 20260917; N = 400_000
S01_UNCOND_DAY1_SD = 9.5

S02 = dict(   # S02 revision 2 (abnb_path_mixture_v2.py PARAMS), copied not imported
    spot=167.51, sessions_pre=36, sessions_post_to_dec15=26, bg_vol_ann=0.30, total_drift_ann=0.0697, sessions_p1=21,
    scen={"accel": dict(p=0.32, d1=4.0, post=-1.5), "flat": dict(p=0.10, d1=-1.0, post=-0.5),
          "decel_ok": dict(p=0.13, d1=-2.5, post=-0.5), "decel_below": dict(p=0.45, d1=-6.0, post=-1.0)},
    day1_sd_within=None)
S02_REV1 = dict(  # revision-1 parameter set, for the bridge row only
    spot=167.51, sessions_pre=35, sessions_post_to_dec15=27, bg_vol_ann=0.29, total_drift_ann=0.03, sessions_p1=21,
    scen={"accel": dict(p=0.24, d1=4.0, post=-2.0), "flat": dict(p=0.14, d1=-1.0, post=-1.0),
          "decel_ok": dict(p=0.10, d1=-2.5, post=-1.0), "decel_below": dict(p=0.52, d1=-6.0, post=-2.5)},
    day1_sd_within=7.5)

POST_MU_V2 = (0.085, 0.525, 0.625, 0.965)      # midpoint judgement / feed print-window means by day-1 sign
POST_MU_EMPIRICAL = (0.02, 0.55, 0.55, 0.83)   # the feed's own print-window post means by day-1 sign
PRE_MU_V2 = 0.26                               # measured 2023+ off-print 49-day rate


def within_sd(p):
    if p.get("day1_sd_within") is not None:
        return p["day1_sd_within"]
    names = list(p["scen"]); pr = np.array([p["scen"][s]["p"] for s in names]); pr = pr / pr.sum()
    m = np.array([p["scen"][s]["d1"] for s in names]); vb = float(np.sum(pr * (m - np.sum(pr * m)) ** 2))
    return math.sqrt(max(S01_UNCOND_DAY1_SD ** 2 - vb, 1.0))


def with_probs(params, a, fl, d, b):
    q = copy.deepcopy(params)
    for s, v in zip(q["scen"], (a, fl, d, b)):
        q["scen"][s]["p"] = v
    return q


def run(seed=SEED, n=N, params=S02, pre_mu=PRE_MU_V2, k_pre=3.0, post_mu=POST_MU_V2, beta_d1=0.06, k_post=3.0,
        overdisp=1.6, capture=0.85, pool_scale=1.0, recentre=True, k_post_includes_day1=False, verbose=False):
    rng = np.random.default_rng(seed)
    p = copy.deepcopy(params); dt = 1 / 252; v = p["bg_vol_ann"]; mu = p["total_drift_ann"]

    def diff(k):
        return (mu - 0.5 * v * v) * k * dt + v * math.sqrt(k * dt) * rng.standard_normal(n)
    names = list(p["scen"]); probs = np.array([p["scen"][s]["p"] for s in names]); probs = probs / probs.sum()
    z = rng.choice(len(names), size=n, p=probs)
    g = lambda key: np.array([p["scen"][s][key] for s in names])[z] / 100
    d1_mu, post_drift = g("d1"), g("post")
    sd_w = within_sd(p) / 100
    r_pre = diff(p["sessions_pre"])
    day1 = d1_mu + sd_w * rng.standard_normal(n); r_day1 = np.log1p(day1)
    r_post = np.log1p(post_drift) + diff(p["sessions_post_to_dec15"])
    P_dec = p["spot"] * np.exp(r_pre + r_day1 + r_post)
    f = p["sessions_p1"] / p["sessions_pre"]
    p1 = f * r_pre + math.sqrt(f * (1 - f)) * v * math.sqrt(p["sessions_pre"] * dt) * rng.standard_normal(n)

    mod_pre = np.exp(-k_pre * np.minimum(p1, 0.0))
    # A17-18: k_post was calibrated on a post-print move that INCLUDES the reaction day; k_post_includes_day1=True
    # applies it to r_day1 + r_post, which is the window the coefficient was measured on.
    r_price_post = (r_day1 + r_post) if k_post_includes_day1 else r_post
    mod_post = np.exp(-beta_d1 * (day1 * 100 - d1_mu * 100)) * np.exp(-k_post * np.minimum(r_price_post, 0.0))
    s_pre = float(mod_pre.mean()) if recentre else 1.0
    s_post = np.ones(len(names))
    if recentre:
        for i in range(len(names)):
            s_post[i] = float(mod_post[z == i].mean())
    m_pre = (pre_mu / s_pre) * pool_scale * mod_pre
    m_post = (np.array(post_mu) / s_post)[z] * pool_scale * mod_post

    def nb(m):
        if overdisp <= 1.0:
            return rng.poisson(m)
        r = m / (overdisp - 1.0); q = r / (r + m); return rng.negative_binomial(r, q)
    pre, post = nb(m_pre), nb(m_post)
    if capture < 1.0:
        pre = rng.binomial(pre, capture); post = rng.binomial(post, capture)
    nd = pre + post; yes = nd >= 3
    out = dict(p=float(yes.mean()), mean_downgrades=float(nd.mean()), mean_pre=float(pre.mean()), mean_post=float(post.mean()),
               rate_per_year=float(nd.mean()) * 365 / 89,
               recentre_scale_pre=s_pre, recentre_scale_post=[float(x) for x in s_post],
               P_count={str(k): float((nd == k).mean()) for k in range(0, 6)},
               P_ge={str(k): float((nd >= k).mean()) for k in range(1, 6)},
               by_branch={k: float(yes[z == i].mean()) for i, k in enumerate(names)},
               mean_by_branch={k: float(nd[z == i].mean()) for i, k in enumerate(names)},
               P_branch_given_yes={k: float(((z == i) & yes).sum() / yes.sum()) for i, k in enumerate(names)},
               P_yes_given_day1_le_m5=float(yes[day1 <= -0.05].mean()), P_yes_given_day1_le_m8=float(yes[day1 <= -0.08].mean()),
               P_yes_given_day1_ge5=float(yes[day1 >= 0.05].mean()), P_yes_given_day1_mid=float(yes[(day1 > -0.05) & (day1 < 0.05)].mean()),
               P_yes_given_dec_le_150=float(yes[P_dec <= 150].mean()), P_yes_given_dec_ge_180=float(yes[P_dec >= 180].mean()),
               E_price_dec15_given_yes=float(P_dec[yes].mean()), E_price_dec15_uncond=float(P_dec.mean()),
               median_price_dec15_given_yes=float(np.median(P_dec[yes])), median_price_dec15_uncond=float(np.median(P_dec)),
               E_day1_given_yes=float(day1[yes].mean() * 100), E_day1_uncond=float(day1.mean() * 100))
    if verbose:
        print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    base = run(verbose=True)
    sens = [("base (rev 2: S02 v2, recentred, pre 0.26, post .085/.525/.625/.965, capture 0.85)", {}),
            ("bridge: revision-1 parameter set exactly (b11_model.py)",
             dict(params=S02_REV1, pre_mu=0.35, post_mu=(0.15, 0.5, 0.7, 1.1), recentre=False)),
            ("S02 v2 only, otherwise revision 1 (no recentring)", dict(pre_mu=0.35, post_mu=(0.15, 0.5, 0.7, 1.1), recentre=False)),
            ("no recentring (revision-1 level error left in)", dict(recentre=False)),
            ("feed capture 1.0 (the rates are already feed counts: the calibration-coherent reading)", dict(capture=1.0)),
            ("feed capture 0.70", dict(capture=0.70)),
            ("entry-state lift x1.2 on the pre block (spot -8% over 21 sessions), capture 0.85", dict(pre_mu=0.312)),
            ("entry-state lift x1.2 on the pre block, capture 1.0", dict(pre_mu=0.312, capture=1.0)),
            ("entry-state lift x1.35 (the measured <= -10% lift), capture 1.0", dict(pre_mu=0.351, capture=1.0)),
            ("post means = the feed's print-window means exactly (.02/.55/.55/.83)", dict(post_mu=POST_MU_EMPIRICAL)),
            ("post means = revision-1 judgement (.15/.5/.7/1.1)", dict(post_mu=(0.15, 0.5, 0.7, 1.1))),
            ("post means halved", dict(post_mu=tuple(x / 2 for x in POST_MU_V2))),
            ("post means x1.5", dict(post_mu=tuple(x * 1.5 for x in POST_MU_V2))),
            ("pre-print mean 0.20 (trailing-12m drought)", dict(pre_mu=0.20)),
            ("pre-print mean 0.35 (revision-1 judgement)", dict(pre_mu=0.35)),
            ("pre-print mean 0.47 (2023+ ALL-window 49-day rate)", dict(pre_mu=0.47)),
            ("no day-1 modulation", dict(beta_d1=0.0)), ("day-1 modulation 0.12", dict(beta_d1=0.12)),
            ("no price-path modulation (k_pre = k_post = 0)", dict(k_pre=0.0, k_post=0.0)),
            ("k_post applied to r_day1 + r_post, the window it was measured on (A17-18)", dict(k_post_includes_day1=True)),
            ("price-path modulation doubled", dict(k_pre=6.0, k_post=6.0)),
            ("Poisson counts", dict(overdisp=1.0)), ("overdispersion 2.5 (Nov-2023-style clustering)", dict(overdisp=2.5)),
            ("pool scale 1.25 (22 Buys, Buy share at a series high)", dict(pool_scale=1.25)),
            ("A09 rev-2 print states (accel .26 / flat .10 / ok .15 / below .48)", dict(params=with_probs(S02, 0.26, 0.10, 0.15, 0.48))),
            ("P(accel) 0.40 (Street-like)", dict(params=with_probs(S02, 0.40, 0.12, 0.10, 0.38))),
            ("P(accel) 0.13", dict(params=with_probs(S02, 0.13, 0.14, 0.12, 0.61))),
            ("joint bear-for-stock: accel 0.13, post x1.5, pool 1.25, capture 1.0, overdisp 2.5",
             dict(post_mu=tuple(x * 1.5 for x in POST_MU_V2), pool_scale=1.25, capture=1.0, overdisp=2.5,
                  params=with_probs(S02, 0.13, 0.14, 0.12, 0.61))),
            ("joint bull-for-stock: accel 0.40, post halved, pre 0.20, capture 0.70",
             dict(pre_mu=0.20, post_mu=tuple(x / 2 for x in POST_MU_V2), capture=0.70,
                  params=with_probs(S02, 0.40, 0.12, 0.10, 0.38)))]
    with open(HERE / "b11_v2_sensitivity.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["case", "p_yes", "mean_downgrades", "rate_per_year", "p_ge2", "p_yes_decel_below", "p_yes_accel"])
        for name, kw in sens:
            r = run(**kw)
            wr.writerow([name, round(r["p"], 4), round(r["mean_downgrades"], 3), round(r["rate_per_year"], 2),
                         round(r["P_ge"]["2"], 3), round(r["by_branch"]["decel_below"], 3), round(r["by_branch"]["accel"], 3)])
            print("%-78s P %.4f  mean %.3f (%.2f/yr)  P>=2 %.3f  below %.3f  accel %.3f"
                  % (name, r["p"], r["mean_downgrades"], r["rate_per_year"], r["P_ge"]["2"], r["by_branch"]["decel_below"], r["by_branch"]["accel"]))
    json.dump(base, open(HERE / "b11_v2_summary.json", "w"), indent=1)
