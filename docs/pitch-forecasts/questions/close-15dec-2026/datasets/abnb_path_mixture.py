"""Seeded Monte Carlo for the ABNB price path: S02 (close 15 Dec 2026), S03 (close 12 Feb 2027, the
session after the 4Q26 print) and S04 (mean sell-side target on 15 Dec <= $176.8).
Structure (log space, raw close-to-close, USD):
  ln P(15 Dec) = ln 167.51 + r_pre (16 Sep -> 5 Nov close, 35 sessions, diffusion)
               + r_day1 (5 Nov print, mixture over four print scenarios)
               + r_post (6 Nov -> 15 Dec, 27 sessions, scenario drift + diffusion)
  ln P(12 Feb) = ln P(15 Dec) + r_mid (16 Dec -> 11 Feb, 39 sessions, scenario drift + Jan/Feb seasonal + diffusion)
               + r_feb (12 Feb reaction to the 4Q26 print, scenario-conditional mean)
  d ln T(15 Dec) = tape-lag regression on the price blocks + 0.40 x day-1 (print chase) + stale-refresh + noise
All inputs are named in PARAMS; every number is cited in the research logs.
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/close-15dec-2026/datasets/abnb_path_mixture.py
"""
import copy, json, math, pathlib
import numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent
SEED = 20260917
N = 400_000
PARAMS = dict(
    spot=167.51, spot_date="2026-09-16",
    sessions_pre=35, sessions_post_to_dec15=27, sessions_dec15_to_feb11=39,
    bg_vol_ann=0.29,           # background (non-event) annualised vol; Oct ATM IV 32.3%, 2023+ realised 63d windows imply ~28%
    equity_drift_ann=0.03,     # real-world drift (beta 0.91 x ~3-4% equity premium, no alpha)
    # 5 Nov print scenarios: P, day-1 mean %, day-1 sd %, drift to 15 Dec %, drift 16 Dec -> 11 Feb %, Feb day-1 mean %, Feb day-1 sd %
    scen={
        "accel (3Q26 nights >= 10.6%)":          dict(p=0.24, d1=4.0, sd=7.5, post=-2.0, mid=1.0, feb=4.0, feb_sd=8.0),
        "flat (10.1-10.6%)":                       dict(p=0.14, d1=-1.0, sd=7.5, post=-1.0, mid=-1.0, feb=2.5, feb_sd=8.0),
        "decel, 4Q26 guide at/above Street":       dict(p=0.10, d1=-2.5, sd=7.5, post=-1.0, mid=-1.0, feb=2.5, feb_sd=8.0),
        "decel, 4Q26 guide below Street":          dict(p=0.52, d1=-6.0, sd=7.5, post=-2.5, mid=-3.0, feb=2.0, feb_sd=8.5),
    },
    janfeb_seasonal_drift=2.0,   # % over 16 Dec -> 11 Feb (Jan +6.9 / Feb +7.7 excess, n 6, shrunk ~75%)
    # S04 tape-lag model (D_chase_regression: b0 0.075, b1 0.13, b2 0.10 per 21-session block; print chase 0.40 at +20 sessions)
    tape=dict(b0=0.075, b1=0.13, b2=0.10, chase=0.40, known_lag_terms=(0.13 + 0.10) * (-0.068) + 0.10 * 0.206 + 3 * 0.0005,
              stale_refresh=0.005, resid_sd=0.035, base_mean_target=183.22, base_mean_target_feed_asis=181.81, threshold=176.8),
)
QS = [5, 10, 25, 50, 75, 90, 95]


def run(params=PARAMS, seed=SEED, n=N, verbose=True):
    rng = np.random.default_rng(seed)
    p = params
    dt = 1 / 252
    v = p["bg_vol_ann"]
    mu = p["equity_drift_ann"]

    def diff(k):  # k sessions of diffusion, log return
        return (mu - 0.5 * v * v) * k * dt + v * math.sqrt(k * dt) * rng.standard_normal(n)

    names = list(p["scen"])
    probs = np.array([p["scen"][s]["p"] for s in names])
    probs = probs / probs.sum()
    z = rng.choice(len(names), size=n, p=probs)
    g = lambda key: np.array([p["scen"][s][key] for s in names])[z] / 100
    d1_mu, d1_sd, post_mu, mid_mu, feb_mu, feb_sd = g("d1"), g("sd"), g("post"), g("mid"), g("feb"), g("feb_sd")
    r_pre = diff(p["sessions_pre"])
    r_day1 = np.log1p(d1_mu + d1_sd * rng.standard_normal(n))          # day-1 simple return -> log
    r_post = np.log1p(post_mu) + diff(p["sessions_post_to_dec15"])
    lnP_dec = math.log(p["spot"]) + r_pre + r_day1 + r_post
    r_mid = np.log1p(mid_mu) + math.log1p(p["janfeb_seasonal_drift"] / 100) + diff(p["sessions_dec15_to_feb11"])
    r_feb = np.log1p(feb_mu + feb_sd * rng.standard_normal(n))
    lnP_feb = lnP_dec + r_mid + r_feb
    P_dec, P_feb = np.exp(lnP_dec), np.exp(lnP_feb)
    # S04: blocks p1 = 16 Sep -> 14 Oct (21 s), p2pre = 14 Oct -> 5 Nov (14 s), p3 = 6 Nov -> 15 Dec post-print (27 s)
    f = 21 / 35
    p1 = f * r_pre + math.sqrt(f * (1 - f)) * v * math.sqrt(p["sessions_pre"] * dt) * rng.standard_normal(n)
    p2pre = r_pre - p1
    t = p["tape"]
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
    out = {"params": params, "seed": seed, "n": n,
           "day1": {"mean_pct": float(sr1.mean() * 100), "sd_pct": float(sr1.std() * 100),
                    "P(<=-8%)": float((sr1 <= -0.08).mean()), "P(<=-5%)": float((sr1 <= -0.05).mean()),
                    "P(>=+5%)": float((sr1 >= 0.05).mean()), "P(>=+10%)": float((sr1 >= 0.10).mean()),
                    "percentiles_pct": {str(q): float(np.percentile(sr1, q) * 100) for q in QS}},
           "S02_close_15dec": summ(P_dec), "S03_close_12feb": summ(P_feb),
           "S03_feb_day1": {"mean_pct": float(srf.mean() * 100), "P(>=+5%)": float((srf >= 0.05).mean()), "P(<0)": float((srf < 0).mean())},
           "S04_target": {"P(T<=176.8)_base_183.22": float((T_dec <= t["threshold"]).mean()),
                          "P(T<=176.8)_base_181.81": float((T_dec_asis <= t["threshold"]).mean()),
                          "mean_dlnT_pct": float(dlnT.mean() * 100), "sd_dlnT_pct": float(dlnT.std() * 100),
                          "T_percentiles": {str(q): float(np.percentile(T_dec, q)) for q in QS},
                          "P(T>=190)": float((T_dec >= 190).mean())},
           "by_scenario": {}}
    for i, s in enumerate(names):
        m = z == i
        out["by_scenario"][s] = {"p": float(probs[i]), "dec_median": float(np.median(P_dec[m])), "dec_P(<=150)": float((P_dec[m] <= 150).mean()),
                                 "dec_P(>=180)": float((P_dec[m] >= 180).mean()),
                                 "feb_median": float(np.median(P_feb[m])), "T_dec_median": float(np.median(T_dec[m])),
                                 "P(T<=176.8)": float((T_dec[m] <= t["threshold"]).mean())}
    if verbose:
        print(json.dumps({k: out[k] for k in out if k != "params"}, indent=1))
    return out, dict(P_dec=P_dec, P_feb=P_feb, T_dec=T_dec, z=z, names=names, r_day1=r_day1)


def set_probs(q, a, fl, d, b):
    for s, v_ in zip(q["scen"], (a, fl, d, b)):
        q["scen"][s]["p"] = v_


def set_all(q, key, val):
    for s in q["scen"]:
        q["scen"][s][key] = val


SENS = [
    ("base", lambda q: None),
    ("P(accel)=0.40 (Street/Kalshi-leaning band)", lambda q: set_probs(q, 0.40, 0.14, 0.08, 0.38)),
    ("P(accel)=0.13 (nowcast centre 9.75, sd 0.75)", lambda q: set_probs(q, 0.13, 0.19, 0.11, 0.57)),
    ("day-1 conditional means shrunk to zero (market-neutral print)", lambda q: set_all(q, "d1", 0.0)),
    ("day-1 conditional means unshrunk (accel +6, flat -1, decel-ok -4, decel-below -8)",
     lambda q: [q["scen"][s].__setitem__("d1", v_) for s, v_ in zip(q["scen"], (6.0, -1.0, -4.0, -8.0))]),
    ("no post-print drift in any branch", lambda q: [set_all(q, "post", 0.0), set_all(q, "mid", 0.0)]),
    ("post-print drift doubled", lambda q: [q["scen"][s].update(post=2 * q["scen"][s]["post"], mid=2 * q["scen"][s]["mid"]) for s in q["scen"]]),
    ("background vol 33% (Oct ATM IV)", lambda q: q.__setitem__("bg_vol_ann", 0.33)),
    ("background vol 25%", lambda q: q.__setitem__("bg_vol_ann", 0.25)),
    ("event sd 9.0% in every branch", lambda q: set_all(q, "sd", 9.0)),
    ("equity drift 0", lambda q: q.__setitem__("equity_drift_ann", 0.0)),
    ("Feb day-1 mean at the raw n-6 base rate (+7.9%) in every branch", lambda q: set_all(q, "feb", 7.9)),
    ("Feb day-1 mean 0 in every branch", lambda q: set_all(q, "feb", 0.0)),
    ("no Jan/Feb seasonal drift", lambda q: q.__setitem__("janfeb_seasonal_drift", 0.0)),
    ("S04: print chase 0.60", lambda q: q["tape"].__setitem__("chase", 0.60)),
    ("S04: print chase 0.20", lambda q: q["tape"].__setitem__("chase", 0.20)),
    ("S04: no stale-refresh term", lambda q: q["tape"].__setitem__("stale_refresh", 0.0)),
    ("S04: residual sd 5%", lambda q: q["tape"].__setitem__("resid_sd", 0.05)),
    ("S04: known lag terms zero (ignore Aug/Sep history)", lambda q: q["tape"].__setitem__("known_lag_terms", 0.0)),
    ("S04: base = feed as-is 181.81 (MS action not captured)", lambda q: q["tape"].__setitem__("base_mean_target", 181.81)),
]

if __name__ == "__main__":
    out, sims = run()
    json.dump(out, open(HERE / "mixture_base_run.json", "w"), indent=1)
    for key, arr in (("S02", sims["P_dec"]), ("S03", sims["P_feb"])):
        h, e = np.histogram(arr, bins=np.arange(60, 320, 5))
        pd.DataFrame({"bin_lo": e[:-1], "count": h, "share": h / len(arr)}).to_csv(HERE / f"{key}_hist.csv", index=False)
    rows = []
    for label, mut in SENS:
        pp = copy.deepcopy(PARAMS)
        mut(pp)
        o, _ = run(pp, verbose=False)
        a, b, c = o["S02_close_15dec"], o["S03_close_12feb"], o["S04_target"]
        rows.append(dict(sensitivity=label, day1_mean=o["day1"]["mean_pct"],
                         S02_p50=a["percentiles"]["50"], S02_le150=a["P(<=150)"], S02_le143=a["P(<=143)"], S02_ge180=a["P(>=180)"],
                         S03_p50=b["percentiles"]["50"], S03_le150=b["P(<=150)"], S03_le143=b["P(<=143)"], S03_ge180=b["P(>=180)"],
                         S04_p=c["P(T<=176.8)_base_183.22"]))
    df = pd.DataFrame(rows).round(3)
    df.to_csv(HERE / "sensitivity.csv", index=False)
    print(df.to_string())
