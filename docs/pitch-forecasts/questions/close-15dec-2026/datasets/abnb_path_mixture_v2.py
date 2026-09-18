"""Revision-2 seeded Monte Carlo for the ABNB price path (S02 close 15 Dec 2026, S03 close of the session after
the 4Q26 print, S04 mean sell-side target on 15 Dec <= $176.8). Revision 1 is abnb_path_mixture.py (untouched).
Changes from revision 1, each tied to an audit finding (A07) or a later input:
  - print-state weights from R01/R02 (accel 0.32, P(>=10.0) 0.42 -> flat 0.10, decel 0.58 split by S01's
    P(guide below | decel) 0.78 -> 0.13 / 0.45) instead of the S02-built 0.24/0.14/0.10/0.52
  - sessions 36 pre / 26 post / 39 mid (A07-15); background vol 30% (trailing-1y realised ex-print 30.0%, Oct ATM 32.3%)
  - one drift convention: TOTAL expected return 6.97% a year (3.97% cash + 3% premium) in the diffusion and in the
    anchor shift (A07-17); within-branch event sd from the variance identity so the unconditional day-1 sd is S01's 9.5%
  - post-print drifts rebased at the reaction close (A07-05/06: proper +20 all -3.1%, W1 -0.9, W2 -1.9; +27 W1 +1.0,
    W2 -1.3; accelerating paired -2.1 / -0.6): accel -1.5, flat -0.5, decel-ok -0.5, decel-below -1.0 (26 sessions)
  - 16 Dec -> 11 Feb: the Jan/Feb calendar seasonal is replaced by the measured 15 Dec -> pre-release window
    (+6.5% excess ex-IPO year, n 5, sd 12; ../close-12feb-2027/datasets/dec_to_prerelease_window.py) carried at 25%
    = +1.5% (A07-12); branch drifts accel -0.5, flat -0.5, decel-ok -0.5, decel-below -2.0 (memo's estimate-cut leg,
    judgment, half strength)
  - February event from R14 (P(>= +5%) 0.30, mean +0.8%, sd 9.1): branch means +2.5 / +1.0 / +0.5 / -0.5, sd 9.0
  - S04 tape block: p1 = 21 of the 36 pre sessions, p2pre = 15, post 26; residual sd 5.0% from the exact hybrid
    equation on 21 historical print windows (sd 5.2 all, 4.3 W1, 4.7 W2; A07-08); everything else as revision 1
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/close-15dec-2026/datasets/abnb_path_mixture_v2.py
"""
import copy, json, math, pathlib
import numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent
SEED = 20260917
N = 400_000
S01_UNCOND_DAY1_SD = 9.5      # S01 revision 1 unconditional day-1 sd (%); options 9.1-9.5
PARAMS = dict(
    spot=167.51, spot_date="2026-09-16",
    sessions_pre=36, sessions_post_to_dec15=26, sessions_dec15_to_feb11=39,
    bg_vol_ann=0.30,
    total_drift_ann=0.0697,     # 3.97% cash + 3.0% equity premium (beta ~0.9 x 3-4%); no alpha
    # 5 Nov print scenarios: P, day-1 mean %, drift to 15 Dec %, drift 16 Dec -> 11 Feb %, Feb day-1 mean %, Feb day-1 sd %
    scen={
        "accel (3Q26 nights >= 10.6%)":          dict(p=0.32, d1=4.0, post=-1.5, mid=-0.5, feb=2.5, feb_sd=9.0),
        "flat (10.0-10.6%)":                       dict(p=0.10, d1=-1.0, post=-0.5, mid=-0.5, feb=1.0, feb_sd=9.0),
        "decel, 4Q26 guide at/above Street":       dict(p=0.13, d1=-2.5, post=-0.5, mid=-0.5, feb=0.5, feb_sd=9.0),
        "decel, 4Q26 guide below Street":          dict(p=0.45, d1=-6.0, post=-1.0, mid=-2.0, feb=-0.5, feb_sd=9.0),
    },
    day1_sd_within=None,          # None -> solved from the variance identity to hit S01_UNCOND_DAY1_SD
    prerelease_seasonal_drift=1.5,  # % over 16 Dec -> 11 Feb: 25% of the measured +6.5% excess (n 5)
    tape=dict(b0=0.075, b1=0.13, b2=0.10, chase=0.40, known_lag_terms=(0.13 + 0.10) * (-0.068) + 0.10 * 0.206 + 3 * 0.0005,
              stale_refresh=0.005, resid_sd=0.05, base_mean_target=183.22, base_mean_target_feed_asis=181.81, threshold=176.8,
              sessions_p1=21),
)
QS = [5, 10, 25, 50, 75, 90, 95]


def within_sd(p):
    if p.get("day1_sd_within") is not None:
        return p["day1_sd_within"]
    names = list(p["scen"]); pr = np.array([p["scen"][s]["p"] for s in names]); pr = pr / pr.sum()
    m = np.array([p["scen"][s]["d1"] for s in names]); var_between = float(np.sum(pr * (m - np.sum(pr * m)) ** 2))
    return math.sqrt(max(S01_UNCOND_DAY1_SD ** 2 - var_between, 1.0))


def run(params=PARAMS, seed=SEED, n=N, verbose=True):
    rng = np.random.default_rng(seed)
    p = params
    dt = 1 / 252
    v = p["bg_vol_ann"]
    mu = p["total_drift_ann"]

    def diff(k):  # k sessions of diffusion, log return
        return (mu - 0.5 * v * v) * k * dt + v * math.sqrt(k * dt) * rng.standard_normal(n)

    names = list(p["scen"])
    probs = np.array([p["scen"][s]["p"] for s in names])
    probs = probs / probs.sum()
    z = rng.choice(len(names), size=n, p=probs)
    g = lambda key: np.array([p["scen"][s][key] for s in names])[z] / 100
    d1_mu, post_mu, mid_mu, feb_mu, feb_sd = g("d1"), g("post"), g("mid"), g("feb"), g("feb_sd")
    sd_w = within_sd(p) / 100
    r_pre = diff(p["sessions_pre"])
    r_day1 = np.log1p(d1_mu + sd_w * rng.standard_normal(n))          # day-1 simple return -> log
    r_post = np.log1p(post_mu) + diff(p["sessions_post_to_dec15"])
    lnP_dec = math.log(p["spot"]) + r_pre + r_day1 + r_post
    r_mid = np.log1p(mid_mu) + math.log1p(p["prerelease_seasonal_drift"] / 100) + diff(p["sessions_dec15_to_feb11"])
    r_feb = np.log1p(feb_mu + feb_sd * rng.standard_normal(n))
    lnP_feb = lnP_dec + r_mid + r_feb
    P_dec, P_feb = np.exp(lnP_dec), np.exp(lnP_feb)
    # S04 blocks: p1 = first 21 sessions (16 Sep -> 14 Oct), p2pre = remaining pre-print sessions, post = 6 Nov -> 15 Dec
    t = p["tape"]
    f = t["sessions_p1"] / p["sessions_pre"]
    p1 = f * r_pre + math.sqrt(f * (1 - f)) * v * math.sqrt(p["sessions_pre"] * dt) * rng.standard_normal(n)
    p2pre = r_pre - p1
    dlnT = (t["known_lag_terms"] + (t["b0"] + t["b1"] + t["b2"]) * p1 + (t["b0"] + t["b1"]) * p2pre + t["chase"] * r_day1
            + (t["b0"] + 0.5 * t["b1"]) * r_post + t["stale_refresh"] + t["resid_sd"] * rng.standard_normal(n))
    T_dec = t["base_mean_target"] * np.exp(dlnT)
    T_dec_asis = t["base_mean_target_feed_asis"] * np.exp(dlnT)

    def thr(x):
        return {"P(<=143)": (x <= 143).mean(), "P(<=150)": (x <= 150).mean(), "P(>=180)": (x >= 180).mean(),
                "P(<=125)": (x <= 125).mean(), "P(>=200)": (x >= 200).mean(), "P(<100)": (x < 100).mean(), "P(>260)": (x > 260).mean()}

    def summ(x):
        d = {"percentiles": {str(q): float(np.percentile(x, q)) for q in QS}, "mean": float(x.mean()),
             "sd_log_pct": float(np.std(np.log(x / p["spot"])) * 100), "median_return_pct": float((np.median(x) / p["spot"] - 1) * 100)}
        d.update({k: float(v_) for k, v_ in thr(x).items()})
        return d

    sr1 = np.expm1(r_day1)
    srf = np.expm1(r_feb)
    out = {"params": params, "day1_sd_within_pct": within_sd(p), "seed": seed, "n": n,
           "day1": {"mean_pct": float(sr1.mean() * 100), "sd_pct": float(sr1.std() * 100),
                    "P(<=-8%)": float((sr1 <= -0.08).mean()), "P(<=-5%)": float((sr1 <= -0.05).mean()),
                    "P(>=+5%)": float((sr1 >= 0.05).mean()), "P(>=+10%)": float((sr1 >= 0.10).mean()),
                    "percentiles_pct": {str(q): float(np.percentile(sr1, q) * 100) for q in QS}},
           "S02_close_15dec": summ(P_dec), "S03_close_12feb": summ(P_feb),
           "S03_feb_day1": {"mean_pct": float(srf.mean() * 100), "sd_pct": float(srf.std() * 100),
                            "P(>=+5%)": float((srf >= 0.05).mean()), "P(<0)": float((srf < 0).mean())},
           "S04_target": {"P(T<=176.8)_base_183.22": float((T_dec <= t["threshold"]).mean()),
                          "P(T<=176.8)_base_181.81": float((T_dec_asis <= t["threshold"]).mean()),
                          "mean_dlnT_pct": float(dlnT.mean() * 100), "sd_dlnT_pct": float(dlnT.std() * 100),
                          "T_percentiles": {str(q): float(np.percentile(T_dec, q)) for q in QS},
                          "P(T>=190)": float((T_dec >= 190).mean()),
                          "P(T<=176.8)_given_day1": {"<=-8%": float((T_dec[sr1 <= -0.08] <= t["threshold"]).mean()),
                                                     "<=-5%": float((T_dec[sr1 <= -0.05] <= t["threshold"]).mean()),
                                                     "(-5,+5)": float((T_dec[(sr1 > -0.05) & (sr1 < 0.05)] <= t["threshold"]).mean()),
                                                     ">=+5%": float((T_dec[sr1 >= 0.05] <= t["threshold"]).mean())}},
           "by_scenario": {}}
    for i, s in enumerate(names):
        m = z == i
        out["by_scenario"][s] = {"p": float(probs[i]), "dec_median": float(np.median(P_dec[m])), "dec_P(<=150)": float((P_dec[m] <= 150).mean()),
                                 "dec_P(>=180)": float((P_dec[m] >= 180).mean()),
                                 "feb_median": float(np.median(P_feb[m])), "feb_P(<=150)": float((P_feb[m] <= 150).mean()),
                                 "T_dec_median": float(np.median(T_dec[m])), "P(T<=176.8)": float((T_dec[m] <= t["threshold"]).mean())}
    if verbose:
        print(json.dumps({k: out[k] for k in out if k != "params"}, indent=1))
    return out, dict(P_dec=P_dec, P_feb=P_feb, T_dec=T_dec, z=z, names=names, r_day1=r_day1)


def set_probs(q, a, fl, d, b):
    for s, v_ in zip(q["scen"], (a, fl, d, b)):
        q["scen"][s]["p"] = v_


def set_all(q, key, val):
    for s in q["scen"]:
        q["scen"][s][key] = val


def set_each(q, key, vals):
    for s, v_ in zip(q["scen"], vals):
        q["scen"][s][key] = v_


SENS = [
    ("base", lambda q: None),
    ("revision-1 print weights 0.24/0.14/0.10/0.52 (S02-built)", lambda q: set_probs(q, 0.24, 0.14, 0.10, 0.52)),
    ("P(accel)=0.40 (Street/Kalshi-leaning band)", lambda q: set_probs(q, 0.40, 0.10, 0.11, 0.39)),
    ("P(accel)=0.22 (R02 alt-data leg only)", lambda q: set_probs(q, 0.22, 0.10, 0.15, 0.53)),
    ("day-1 conditional means shrunk to zero (market-neutral print)", lambda q: set_all(q, "d1", 0.0)),
    ("day-1 conditional means unshrunk (accel +6, flat -1, decel-ok -4, decel-below -8)", lambda q: set_each(q, "d1", (6.0, -1.0, -4.0, -8.0))),
    ("no post-print drift in any branch (Astra's construction)", lambda q: [set_all(q, "post", 0.0), set_all(q, "mid", 0.0)]),
    ("revision-1 post-print drifts (-2.0/-1.0/-1.0/-2.5; mid +1/-1/-1/-3)", lambda q: [set_each(q, "post", (-2.0, -1.0, -1.0, -2.5)), set_each(q, "mid", (1.0, -1.0, -1.0, -3.0))]),
    ("post-print drift doubled", lambda q: [q["scen"][s].update(post=2 * q["scen"][s]["post"], mid=2 * q["scen"][s]["mid"]) for s in q["scen"]]),
    ("background vol 33% (Oct ATM IV / 2023+ realised ex-print)", lambda q: q.__setitem__("bg_vol_ann", 0.33)),
    ("background vol 26%", lambda q: q.__setitem__("bg_vol_ann", 0.26)),
    ("within-branch event sd 7.5% (revision 1; unconditional ~8.7%)", lambda q: q.__setitem__("day1_sd_within", 7.5)),
    ("total drift 3% (revision-1 convention)", lambda q: q.__setitem__("total_drift_ann", 0.03)),
    ("total drift 0", lambda q: q.__setitem__("total_drift_ann", 0.0)),
    ("Feb day-1 means at revision 1 (+4.0/+2.5/+2.5/+2.0; S03 rev 1)", lambda q: set_each(q, "feb", (4.0, 2.5, 2.5, 2.0))),
    ("Feb day-1 mean at the raw n-6 base rate (+7.9%) in every branch", lambda q: set_all(q, "feb", 7.9)),
    ("Feb day-1 mean 0 in every branch", lambda q: set_all(q, "feb", 0.0)),
    ("no pre-release seasonal drift", lambda q: q.__setitem__("prerelease_seasonal_drift", 0.0)),
    ("pre-release seasonal at half the measured excess (+3.25%)", lambda q: q.__setitem__("prerelease_seasonal_drift", 3.25)),
    ("S04: print chase 0.60", lambda q: q["tape"].__setitem__("chase", 0.60)),
    ("S04: print chase 0.20", lambda q: q["tape"].__setitem__("chase", 0.20)),
    ("S04: no stale-refresh term", lambda q: q["tape"].__setitem__("stale_refresh", 0.0)),
    ("S04: residual sd 3.5% (revision 1)", lambda q: q["tape"].__setitem__("resid_sd", 0.035)),
    ("S04: residual sd 6.68% (Astra's two-regressor residual)", lambda q: q["tape"].__setitem__("resid_sd", 0.0668)),
    ("S04: known lag terms zero (ignore Aug/Sep history)", lambda q: q["tape"].__setitem__("known_lag_terms", 0.0)),
    ("S04: base = feed as-is 181.81 (MS action not captured)", lambda q: q["tape"].__setitem__("base_mean_target", 181.81)),
    ("S04: 2023+ tape betas 0.14/0.19/0.10", lambda q: q["tape"].update(b0=0.14, b1=0.19, b2=0.10)),
]

if __name__ == "__main__":
    out, sims = run()
    json.dump(out, open(HERE / "mixture_base_run_v2.json", "w"), indent=1)
    for key, arr in (("S02", sims["P_dec"]), ("S03", sims["P_feb"])):
        h, e = np.histogram(arr, bins=np.arange(60, 320, 5))
        pd.DataFrame({"bin_lo": e[:-1], "count": h, "share": h / len(arr)}).to_csv(HERE / f"{key}_hist_v2.csv", index=False)
    rows = []
    for label, mut in SENS:
        pp = copy.deepcopy(PARAMS)
        mut(pp)
        o, _ = run(pp, verbose=False)
        a, b, c = o["S02_close_15dec"], o["S03_close_12feb"], o["S04_target"]
        rows.append(dict(sensitivity=label, day1_mean=o["day1"]["mean_pct"], day1_sd=o["day1"]["sd_pct"],
                         S02_p50=a["percentiles"]["50"], S02_le150=a["P(<=150)"], S02_le143=a["P(<=143)"], S02_ge180=a["P(>=180)"],
                         S03_p50=b["percentiles"]["50"], S03_le150=b["P(<=150)"], S03_le143=b["P(<=143)"], S03_ge180=b["P(>=180)"],
                         S04_p=c["P(T<=176.8)_base_183.22"]))
    df = pd.DataFrame(rows).round(3)
    df.to_csv(HERE / "sensitivity_v2.csv", index=False)
    print(df.to_string())
