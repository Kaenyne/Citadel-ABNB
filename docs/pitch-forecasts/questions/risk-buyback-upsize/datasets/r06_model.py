"""R06 risk-buyback-upsize: Monte Carlo over the buyback pace, the authorization trigger rule and the size rule.
Inputs are in this file; outputs r06_summary.csv and r06_sensitivity.csv. numpy only. Seed 20260917.
"""
import numpy as np, csv, pathlib
rng = np.random.default_rng(20260917)
N = 200_000
here = pathlib.Path(__file__).parent

def run(pace_mu=1.06, pace_sd=0.13, remaining=3.4, k=2.0, r50=1.45, p_size_ge5=0.78,
        legB_base=0.06, legB_with_auth=0.14, pace_floor=0.6):
    # quarterly buyback pace 3Q26 and 4Q26 (USD bn); persistent component + quarter noise
    common = rng.normal(pace_mu, pace_sd * 0.8, N)
    q3 = np.clip(common + rng.normal(0, pace_sd * 0.6, N), pace_floor, None)
    q4 = np.clip(common + rng.normal(0, pace_sd * 0.6, N), pace_floor, None)
    rem_sep = np.clip(remaining - q3, 0, None)
    rem_dec = np.clip(rem_sep - q4, 0, None)
    pace = (q3 + q4) / 2
    r_sep = rem_sep / pace          # quarters of pace left at the 5 Nov print
    r_dec = rem_dec / pace          # quarters of pace left at the Feb print
    f = lambda r: 1 / (1 + np.exp(k * (r - r50)))   # P(announce | quarters of pace remaining)
    p_nov = f(r_sep)
    p_feb = f(r_dec)
    u1 = rng.random(N); u2 = rng.random(N)
    ann_nov = u1 < p_nov
    ann_feb = (~ann_nov) & (u2 < p_feb)
    ann = ann_nov | ann_feb
    size_ok = rng.random(N) < p_size_ge5
    legA = ann & size_ok
    # leg B: 4Q26 repurchases >= 1.5bn. Base hazard; higher if a new authorization came at the Nov print.
    pB = np.where(ann_nov, legB_with_auth, legB_base)
    # also mechanical: the simulated q4 itself >= 1.5 (rare under the pace distribution)
    legB = (rng.random(N) < pB) | (q4 >= 1.5)
    yes = legA | legB
    return dict(p_ann_nov=ann_nov.mean(), p_ann_feb_given_not_nov=(ann_feb.sum() / (~ann_nov).sum()),
                p_ann_by_feb=ann.mean(), p_legA=legA.mean(), p_legB=legB.mean(), p_yes=yes.mean(),
                mean_rem_sep=rem_sep.mean(), mean_rem_dec=rem_dec.mean(), mean_r_dec=r_dec.mean(),
                p_q4_ge_1p5_mechanical=(q4 >= 1.5).mean())

base = run()
rows = [("base", base)]
sens = [
    ("pace 0.90/q (RNPL cash drag, slower buyback)", dict(pace_mu=0.90)),
    ("pace 1.20/q (step-up)", dict(pace_mu=1.20)),
    ("trigger rule steeper, centred 1.2q (wait until nearly exhausted)", dict(k=3.0, r50=1.2)),
    ("trigger rule centred 1.8q (announce earlier, 2Q25 style)", dict(r50=1.8)),
    ("early-regime rule: announce only when exhausted (r50=0.5)", dict(r50=0.5, k=3.0)),
    ("size >= $5bn | announce = 0.60", dict(p_size_ge5=0.60)),
    ("size >= $5bn | announce = 0.90", dict(p_size_ge5=0.90)),
    ("leg B hazards doubled (0.12 / 0.28)", dict(legB_base=0.12, legB_with_auth=0.28)),
    ("leg B hazards zero (mechanical only)", dict(legB_base=0.0, legB_with_auth=0.0)),
    ("joint bear (pace 0.9, r50 0.5, size 0.6, legB 0)", dict(pace_mu=0.9, r50=0.5, k=3.0, p_size_ge5=0.6, legB_base=0, legB_with_auth=0)),
    ("joint bull (pace 1.2, r50 1.8, size 0.9, legB x2)", dict(pace_mu=1.2, r50=1.8, p_size_ge5=0.9, legB_base=0.12, legB_with_auth=0.28)),
]
for name, kw in sens:
    rows.append((name, run(**kw)))
with open(here / "r06_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric", "value"])
    for k_, v in base.items(): w.writerow([k_, round(float(v), 4)])
with open(here / "r06_sensitivity.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "p_yes", "p_ann_by_feb", "p_legA", "p_legB", "mean_rem_dec_usd_bn", "mean_r_dec_q"])
    for name, r in rows:
        w.writerow([name, round(r["p_yes"], 3), round(r["p_ann_by_feb"], 3), round(r["p_legA"], 3), round(r["p_legB"], 3), round(r["mean_rem_dec"], 2), round(r["mean_r_dec"], 2)])
for name, r in rows:
    print(f"{name:70s} P(yes)={r['p_yes']:.3f} ann={r['p_ann_by_feb']:.3f} A={r['p_legA']:.3f} B={r['p_legB']:.3f} remDec={r['mean_rem_dec']:.2f} rDec={r['mean_r_dec']:.2f}")
print("trigger rule f(r):", {r: round(1/(1+np.exp(2.0*(r-1.45))),3) for r in (0.0,0.7,1.0,1.2,1.5,1.6,2.1,2.7,3.3)})
