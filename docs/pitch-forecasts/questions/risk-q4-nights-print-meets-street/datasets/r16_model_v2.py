"""R16 revision 2 (A12 audit response, 2026-09-17): ONE adopted 4Q26 Nights and Seats Booked distribution.
numpy only, seed 20260917, 1,000,000 draws (~10 s). Writes adopted_q4_states_v2.json, r16_v2_summary.csv, r16_v2_views.csv,
r16_v2_conditional.csv, r16_v2_sensitivity.csv. Revision-1 r16_model.py and its CSVs are left untouched.
Changes vs revision 1 (finding ids in research-log.md section 10):
  A12-01  one mixture, both tails published unrounded, one cushion N(1.0, 1.3) for R16, B13, F01/F02
  A12-07  V2 uses the C02 revision-2 vector (0.18, 0.17, 0.30, 0.31, 0.04)
  A12-12  V1 residual sd 1.4 -> 2.0 (Q3->Q4 sequential-change sd 3.74 on n 4; the lap is a mechanism estimate)
  R01 rev 2 3Q26 print N(9.5, 1.70); the pass-through reference is re-based to 9.5 so E[Q4 | no tail] stays the team's 8.1
  A12-16  E[4Q26 | Yes], E[4Q26 | No] and the section-9 deltas come from the mixture, not from V1
"""
import numpy as np, csv, json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260917; N = 1_000_000
BASE = 121.9; THR_HI = 134.0; THR_LO = 131.0
thr_hi_g = (THR_HI / BASE - 1) * 100; thr_lo_g = (THR_LO / BASE - 1) * 100   # 9.926, 7.465
C02_V2 = (0.18, 0.17, 0.30, 0.31, 0.04); MIDS = (10.75, 9.75, 8.0, 6.0, None)
W = (0.5, 0.3, 0.2)


def draw(q3_mu=9.5, q3_sd=1.70, q3_ref=9.5, q4_mu=8.1, beta=0.5, res_sd=2.0, tail_w=0.12, tail_mu=5.5, tail_sd=1.5,
         vec=C02_V2, cushion_mu=1.0, cushion_sd=1.3, street_mu=thr_hi_g, street_sd=1.23, w=W, seed=SEED, n=N):
    rng = np.random.default_rng(seed)
    # V1 decomposition (joint with Q3)
    q3 = rng.normal(q3_mu, q3_sd, n); tail = rng.random(n) < tail_w
    q4_v1 = np.where(tail, tail_mu + beta * (q3 - q3_ref) + rng.normal(0, tail_sd, n),
                     q4_mu + beta * (q3 - q3_ref) + rng.normal(0, res_sd, n))
    # V2 guide route: bucket drawn from the C02 vector, print = midpoint + cushion; no descriptor -> V1 draw
    b = rng.choice(5, size=n, p=np.array(vec) / sum(vec))
    mids = np.array([m if m is not None else np.nan for m in MIDS])
    q4_v2 = mids[b] + rng.normal(cushion_mu, cushion_sd, n); q4_v2 = np.where(np.isnan(q4_v2), q4_v1, q4_v2)
    # V3 Street bar N(134.0m +/- 1.5m)
    q4_v3 = rng.normal(street_mu, street_sd, n)
    comp = rng.choice(3, size=n, p=np.array(w) / sum(w))
    q4 = np.select([comp == 0, comp == 1, comp == 2], [q4_v1, q4_v2, q4_v3])
    return q3, q4, comp, b, q4_v1, q4_v2, q4_v3


def stats(q4):
    nights = np.round(BASE * (1 + q4 / 100), 1); hi = nights >= THR_HI; lo = nights <= THR_LO
    return dict(p_ge_134=hi.mean(), p_le_131=lo.mean(), p_mid=1 - hi.mean() - lo.mean(), mean=q4.mean(), sd=q4.std(),
                median=float(np.median(q4)), e_given_ge_134=q4[hi].mean(), e_given_le_131=q4[lo].mean(),
                e_given_not_ge_134=q4[~hi].mean(), e_given_mid=q4[~hi & ~lo].mean(),
                pct={k: float(np.percentile(q4, k)) for k in (5, 10, 25, 50, 75, 90, 95)})


q3, q4, comp, b, v1, v2, v3 = draw(); S = stats(q4); S1 = stats(v1); S2 = stats(v2); S3 = stats(v3)
nights = np.round(BASE * (1 + q4 / 100), 1); hi = nights >= THR_HI; lo = nights <= THR_LO
out = {
 "object": "Adopted 4Q26 Nights and Seats Booked print distribution (A12 revision 2, 2026-09-17). R16, B13, F01, F02 and X01 read this file; the revision-1 R16/B13 parameters (Q3 N(9.67,1.70), residual 1.4, C02 rev 1, hand-cut V2) are withdrawn.",
 "provenance": "questions/risk-q4-nights-print-meets-street/datasets/r16_model_v2.py (seed 20260917, 1,000,000 draws); audit A12 findings 01/07/12/16; response audits/A12-audit-response.md",
 "parametric": {
   "form": "three-component mixture on latent 4Q26 nights y/y growth (%) over the fixed 121.9m base; printed millions = round(latent, 1); 134.0m resolves R16 Yes (latent >= 9.926 - 0.041), 131.0m resolves B13 Yes (latent <= 7.465 + 0.041)",
   "V1_decomposition": {"weight": 0.5, "q3_print": "N(9.5, 1.70) = R01 revision 2 adopted_print_states_v2.json",
                        "q4": "8.1 + 0.5*(Q3 - 9.5) + N(0, 2.0); 12% short tail 5.5 +/- 1.5",
                        "q4_centre_source": "team case B global lap 8.1 (h2_bridge_v3 rebased lines; N memo 2)",
                        "residual_sd_source": "A12-12: Q3->Q4 sequential-change sd 3.74 (n 4) roughly halved for the known-comp structure; a mechanism estimate, not a fitted effect"},
   "V2_guide_route": {"weight": 0.3, "bucket_vector": "C02 revision 2 (a 0.18, b 0.17, c 0.30, d 0.31, e 0.04)",
                      "print": "bucket midpoint (10.75 / 9.75 / 8.0 / 6.0) + cushion N(1.0, 1.3); no descriptor -> V1 draw",
                      "cushion_source": "judgement between the directional-era record (mean -0.2, sd 1.3 on five stable guides) and the two bucket-era beats (+4.8, +1.15); rev-1 code used 1.2 and the log hand-cut to the equivalent of 0.78; F01 rev 2 used 0.9; one value now"},
   "V3_street_bar": {"weight": 0.2, "print": "N(9.926, 1.23) = Bloomberg MODL 134.0m +/- 1.5m (n 28, 2026-09-12)"},
   "mean": round(S["mean"], 4), "sd": round(S["sd"], 4), "median": round(S["median"], 4),
   "percentiles": {str(k): round(v, 3) for k, v in S["pct"].items()}},
 "events": {"R16_printed_ge_134_0m": {"threshold_pct": thr_hi_g, "p": round(S["p_ge_134"], 4)},
            "B13_printed_le_131_0m": {"threshold_pct": thr_lo_g, "p": round(S["p_le_131"], 4)},
            "middle_131_1_to_133_9m": {"p": round(S["p_mid"], 4)}},
 "conditional_means_pct": {"given_ge_134_0m": round(S["e_given_ge_134"], 3), "given_le_131_0m": round(S["e_given_le_131"], 3),
                           "given_not_ge_134_0m": round(S["e_given_not_ge_134"], 3), "given_middle": round(S["e_given_mid"], 3),
                           "q3_given_ge_134_0m": round(float(q3[hi].mean()), 3), "q3_given_le_131_0m": round(float(q3[lo].mean()), 3),
                           "corr_q3_q4": round(float(np.corrcoef(q3, q4)[0, 1]), 3)},
 "views": {"V1": {k: round(float(v), 4) for k, v in S1.items() if k != "pct"}, "V2": {k: round(float(v), 4) for k, v in S2.items() if k != "pct"},
           "V3": {k: round(float(v), 4) for k, v in S3.items() if k != "pct"}, "blend_weights": list(W)},
 "must_adopt": ["R16 (this log, revision 2)",
                "B13 bonus-q4-nights-print-weak (batch A17): P(<=131.0m) = %.3f, not 0.26" % S["p_le_131"],
                "F01 q1-27-nights-guide-above-82 and F02: replace the F01 rev-2 object (mean 8.70, sd 2.05, 0.29/0.27) with this one",
                "X01 scenario MC"],
 "superseded": {"R16_rev1": 0.27, "B13_rev1": 0.26, "F01_rev2_object": {"p_ge_134": 0.2897, "p_le_131": 0.272, "mean": 8.7046, "sd": 2.0512},
                "rev1_model_blend_rows": {"r16_views": 0.3032, "b13_views": 0.2622}}}
json.dump(out, open("adopted_q4_states_v2.json", "w"), indent=1)

with open("r16_v2_conditional.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["condition", "p_ge_134", "p_le_131", "q4_mean", "n"])
    for lo_, hi_ in [(-99, 9.0), (9.0, 10.0), (10.0, 10.6), (10.6, 99)]:
        m = (q3 >= lo_) & (q3 < hi_)
        w.writerow([f"3Q26 print in [{lo_},{hi_})", round(hi[m].mean(), 4), round(lo[m].mean(), 4), round(q4[m].mean(), 3), int(m.sum())])
    for k, lbl in enumerate(["low double digits", "around 10", "high single digits", "mid single / moderate", "no descriptor"]):
        m = (comp == 1) & (b == k)
        w.writerow([f"5 Nov bucket = {lbl} (V2 component)", round(hi[m].mean(), 4), round(lo[m].mean(), 4), round(q4[m].mean(), 3), int(m.sum())])
with open("r16_v2_views.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["view", "p_ge_134", "p_le_131", "mean", "sd"])
    for nm, s in [("V1_decomposition", S1), ("V2_guide_route", S2), ("V3_street_bar", S3), ("mixture 0.5/0.3/0.2", S)]:
        w.writerow([nm, round(s["p_ge_134"], 4), round(s["p_le_131"], 4), round(s["mean"], 3), round(s["sd"], 3)])
    for wts in [(0.6, 0.3, 0.1), (0.4, 0.4, 0.2), (0.7, 0.2, 0.1), (0.5, 0.5, 0.0), (1 / 3, 1 / 3, 1 / 3), (1, 0, 0)]:
        s = stats(draw(w=wts)[1])
        w.writerow([f"blend {tuple(round(x, 2) for x in wts)}", round(s["p_ge_134"], 4), round(s["p_le_131"], 4), round(s["mean"], 3), round(s["sd"], 3)])
sens = [("q4 centre = RNPL module 7.61", dict(q4_mu=7.61)), ("q4 centre = case A NA-only lap 8.9", dict(q4_mu=8.9)),
        ("q4 centre = Street 9.93, no tail", dict(q4_mu=thr_hi_g, tail_w=0.0)), ("q4 centre = bridge no-lap 10.6, no tail", dict(q4_mu=10.6, tail_w=0.0)),
        ("no short tail", dict(tail_w=0.0)), ("short tail 25%", dict(tail_w=0.25)), ("beta 0.3", dict(beta=0.3)), ("beta 0.8", dict(beta=0.8)),
        ("residual sd 1.4 (rev 1)", dict(res_sd=1.4)), ("residual sd 2.6", dict(res_sd=2.6)), ("residual sd 3.74 (raw sequential sd)", dict(res_sd=3.74)),
        ("Q3 centre 9.2", dict(q3_mu=9.2)), ("Q3 centre 9.9", dict(q3_mu=9.9)), ("Q3 sd 2.16", dict(q3_sd=2.16)),
        ("cushion N(0.6,1.3)", dict(cushion_mu=0.6)), ("cushion N(1.2,1.3)", dict(cushion_mu=1.2)), ("cushion N(2.0,1.5)", dict(cushion_mu=2.0, cushion_sd=1.5)),
        ("cushion N(0,1.3)", dict(cushion_mu=0.0)), ("C02 rev 1 vector", dict(vec=(0.21, 0.19, 0.39, 0.17, 0.04))),
        ("C02 shifted up (a .30 b .22 c .28 d .16 e .04)", dict(vec=(0.30, 0.22, 0.28, 0.16, 0.04))),
        ("C02 shifted down (a .12 b .14 c .30 d .40 e .04)", dict(vec=(0.12, 0.14, 0.30, 0.40, 0.04))),
        ("Street sd 2.5m", dict(street_sd=2.05)),
        ("joint bull: 8.9, beta .8, no tail, Q3 9.9, cushion 2.0", dict(q4_mu=8.9, beta=0.8, tail_w=0.0, q3_mu=9.9, cushion_mu=2.0, cushion_sd=1.5)),
        ("joint bear: 7.61, tail 25%, Q3 9.2, cushion 0.6", dict(q4_mu=7.61, tail_w=0.25, q3_mu=9.2, cushion_mu=0.6)),
        ("audit replay: Q3 ref 9.67 kept", dict(q3_ref=9.67))]
with open("r16_v2_sensitivity.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["case", "p_ge_134", "p_le_131", "mean", "sd", "e_q4_given_ge_134"])
    w.writerow(["base (adopted)", round(S["p_ge_134"], 4), round(S["p_le_131"], 4), round(S["mean"], 3), round(S["sd"], 3), round(S["e_given_ge_134"], 3)])
    for nm, kw in sens:
        s = stats(draw(**kw)[1])
        w.writerow([nm, round(s["p_ge_134"], 4), round(s["p_le_131"], 4), round(s["mean"], 3), round(s["sd"], 3), round(s["e_given_ge_134"], 3)])
with open("r16_v2_summary.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["item", "value"])
    for k in ["p_ge_134", "p_le_131", "p_mid", "mean", "sd", "median", "e_given_ge_134", "e_given_le_131", "e_given_not_ge_134", "e_given_mid"]:
        w.writerow([k, round(float(S[k]), 4)])
    for k, v in S["pct"].items(): w.writerow([f"p{k}", round(v, 3)])
    w.writerow(["e_q3_given_ge_134", round(float(q3[hi].mean()), 3)]); w.writerow(["e_q3_given_le_131", round(float(q3[lo].mean()), 3)])
for fn in ["r16_v2_summary.csv", "r16_v2_views.csv", "r16_v2_conditional.csv", "r16_v2_sensitivity.csv"]:
    print(open(fn).read())
