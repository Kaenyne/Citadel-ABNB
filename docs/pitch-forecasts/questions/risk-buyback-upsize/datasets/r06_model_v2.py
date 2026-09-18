"""R06 risk-buyback-upsize, revision 2 (audit A11 response). Monte Carlo over the buyback pace, the
authorization trigger and the size judgement. Changes from r06_model.py (kept untouched as the audit trail):
  * November hazard is a fixed judgement (0.12) rather than a logistic extrapolation into the unobserved
    1.6 < r < 2.7 region (A11-05; the auditor's 0.08 and the dollar-threshold 0.13 / pace-threshold 0.30
    readings are sensitivities).
  * February trigger = 50/50 blend of the maximum-likelihood logistic on the 16-print panel
    (k 1.423, r50 1.075; A11-03) and the revision-1 hand-set rule (k 2.0, r50 1.45), each evaluated at the
    simulated quarters-of-pace reading; the two bracket the three-episode Laplace (0.60 at r ~ 1.25).
  * P(size >= $5bn | announce) 0.75, labelled a regime judgement (historical frequency 2 of 4 = 0.50; A11-02).
  * leg B threshold 1.45 (letters round $1bn+ quarters to $0.1bn; A11-14).
Outputs r06_v2_summary.csv and r06_v2_sensitivity.csv. numpy only. Seed 20260917.
"""
import numpy as np, csv, pathlib, math
rng = np.random.default_rng(20260917)
N = 200_000
here = pathlib.Path(__file__).parent

MLE_K, MLE_R50 = 1.4234, 1.5308 / 1.4234     # grid-search MLE on print_state_panel.csv (A11-reproduce.py)
R1_K, R1_R50 = 2.0, 1.45                     # revision-1 hand-set rule


def run(pace_mu=1.06, pace_sd=0.13, remaining=3.4, p_nov=0.12, feb_rule="blend", p_size_ge5=0.75,
        legB_base=0.06, legB_with_auth=0.14, legB_thresh=1.45, pace_floor=0.6):
    common = rng.normal(pace_mu, pace_sd * 0.8, N)
    q3 = np.clip(common + rng.normal(0, pace_sd * 0.6, N), pace_floor, None)
    q4 = np.clip(common + rng.normal(0, pace_sd * 0.6, N), pace_floor, None)
    rem_sep = np.clip(remaining - q3, 0, None)
    rem_dec = np.clip(rem_sep - q4, 0, None)
    pace = (q3 + q4) / 2
    r_dec = rem_dec / pace
    f_mle = 1 / (1 + np.exp(MLE_K * (r_dec - MLE_R50)))
    f_r1 = 1 / (1 + np.exp(R1_K * (r_dec - R1_R50)))
    if feb_rule == "blend":
        p_feb = 0.5 * f_mle + 0.5 * f_r1
    elif feb_rule == "mle":
        p_feb = f_mle
    elif feb_rule == "rev1":
        p_feb = f_r1
    elif feb_rule == "exhaustion":          # 2022-23 regime: announce only when (nearly) exhausted
        p_feb = 1 / (1 + np.exp(3.0 * (r_dec - 0.5)))
    else:
        raise ValueError(feb_rule)
    ann_nov = rng.random(N) < p_nov
    ann_feb = (~ann_nov) & (rng.random(N) < p_feb)
    ann = ann_nov | ann_feb
    legA = ann & (rng.random(N) < p_size_ge5)
    pB = np.where(ann_nov, legB_with_auth, legB_base)
    legB = (rng.random(N) < pB) | (q4 >= legB_thresh)
    yes = legA | legB
    return dict(p_ann_nov=ann_nov.mean(), p_ann_feb_given_not_nov=ann_feb.sum() / (~ann_nov).sum(),
                p_ann_by_feb=ann.mean(), p_legA=legA.mean(), p_legB=legB.mean(), p_yes=yes.mean(),
                p_legB_given_yes=(legB & yes).sum() / yes.sum(), p_legB_only=(legB & ~legA).mean(),
                mean_rem_sep=rem_sep.mean(), mean_rem_dec=rem_dec.mean(), mean_r_dec=r_dec.mean(),
                p_q4_ge_thresh_mechanical=(q4 >= legB_thresh).mean())


base = run()
rows = [("base (rev 2)", base)]
sens = [
    ("Nov hazard 0.08 (auditor's cap)", dict(p_nov=0.08)),
    ("Nov hazard 0.20 (logistic interpolation, upper)", dict(p_nov=0.20)),
    ("Nov hazard 0.30 (pace-threshold model)", dict(p_nov=0.30)),
    ("Feb rule = MLE logistic only", dict(feb_rule="mle")),
    ("Feb rule = revision-1 hand-set rule only", dict(feb_rule="rev1")),
    ("Feb rule = 2022-23 exhaustion regime", dict(feb_rule="exhaustion")),
    ("pace 0.90/q (RNPL cash drag, M&A reserve)", dict(pace_mu=0.90)),
    ("pace 1.20/q (step-up)", dict(pace_mu=1.20)),
    ("size >= $5bn | announce = 0.50 (historical frequency)", dict(p_size_ge5=0.50)),
    ("size >= $5bn | announce = 0.90", dict(p_size_ge5=0.90)),
    ("leg B hazards doubled (0.12 / 0.28)", dict(legB_base=0.12, legB_with_auth=0.28)),
    ("leg B hazards zero (mechanical only)", dict(legB_base=0.0, legB_with_auth=0.0)),
    ("leg B threshold 1.50 (no rounding convention)", dict(legB_thresh=1.5)),
    ("auditor's construction (Nov 0.08, MLE Feb, size 0.78)", dict(p_nov=0.08, feb_rule="mle", p_size_ge5=0.78)),
    ("revision-1 construction (Nov 0.19, rev-1 rule, size 0.78, thresh 1.5)", dict(p_nov=0.19, feb_rule="rev1", p_size_ge5=0.78, legB_thresh=1.5)),
    ("joint bear (pace 0.9, exhaustion rule, Nov 0.05, size 0.5, legB 0)", dict(pace_mu=0.9, feb_rule="exhaustion", p_nov=0.05, p_size_ge5=0.5, legB_base=0, legB_with_auth=0)),
    ("joint bull (pace 1.2, rev-1 rule, Nov 0.25, size 0.9, legB x2)", dict(pace_mu=1.2, feb_rule="rev1", p_nov=0.25, p_size_ge5=0.9, legB_base=0.12, legB_with_auth=0.28)),
]
for name, kw in sens:
    rows.append((name, run(**kw)))
with open(here / "r06_v2_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["metric", "value"])
    for k_, v in base.items(): w.writerow([k_, round(float(v), 4)])
with open(here / "r06_v2_sensitivity.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "p_yes", "p_ann_by_feb", "p_legA", "p_legB", "mean_rem_dec_usd_bn", "mean_r_dec_q"])
    for name, r in rows:
        w.writerow([name, round(r["p_yes"], 3), round(r["p_ann_by_feb"], 3), round(r["p_legA"], 3), round(r["p_legB"], 3), round(r["mean_rem_dec"], 2), round(r["mean_r_dec"], 2)])
for name, r in rows:
    print(f"{name:75s} P(yes)={r['p_yes']:.3f} ann={r['p_ann_by_feb']:.3f} nov={r['p_ann_nov']:.3f} feb|notnov={r['p_ann_feb_given_not_nov']:.3f} A={r['p_legA']:.3f} B={r['p_legB']:.3f} B|yes={r['p_legB_given_yes']:.3f} rDec={r['mean_r_dec']:.2f}")
print("Feb rules at r:", {r: (round(1/(1+math.exp(MLE_K*(r-MLE_R50))),3), round(1/(1+math.exp(R1_K*(r-R1_R50))),3)) for r in (1.0, 1.1, 1.25, 1.4, 1.6)})
# pure-frequency base rate (no size judgement): 3 episodes, 2 renewed before exhaustion at <= 1.6 quarters -> Laplace 0.60
p_feb_lap = (2 + 1) / (3 + 2); p_size_freq = 2 / 4; legB = 0.07
print("base-rate estimate:", round(p_feb_lap * p_size_freq + (1 - p_feb_lap * p_size_freq) * legB, 3))
print("impact: P(legB|yes)=%.3f -> stock = %.2f; EPS legB = %.4f" % (base["p_legB_given_yes"],
      (1 - base["p_legB_given_yes"]) * 1.0 + base["p_legB_given_yes"] * 2.5, 5.73 * 0.45e3 / 165 / 586))
