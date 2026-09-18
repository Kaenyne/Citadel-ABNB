"""B13 revision 2 (audit A17 response). Revision 1 is b13_model.py (untouched, with its CSVs).
B13 no longer carries a model of its own: the run has ONE adopted 4Q26 Nights and Seats Booked object,
  ../risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json
built by r16_model_v2.py (A12 revision 2) and whose must_adopt list names this question by id
("B13 bonus-q4-nights-print-weak (batch A17): P(<=131.0m) = 0.309, not 0.26").  This script re-implements
that object's draw() parameter-for-parameter, verifies it reproduces the published tails, and writes B13's
own tables (the lower tail, its conditionals and its sensitivities) into THIS folder.  It writes nothing
outside docs/pitch-forecasts/questions/bonus-q4-nights-print-weak/datasets/ and it does not execute
r16_model_v2.py (which writes into R16's folder).
Withdrawn revision-1 parameters (A17-01): Q3 N(9.67,1.70), V1 residual sd 1.4, C02 revision-1 vector
(.21/.19/.39/.17/.04), V2 cushion N(1.2,1.3) hand-cut to 0.18, blend 0.2622 -> published 0.26.
numpy only, seed 20260917, 1,000,000 draws (~10 s). Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/bonus-q4-nights-print-weak/datasets/b13_model_v2.py
"""
import numpy as np, csv, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ADOPTED = HERE.parent.parent / "risk-q4-nights-print-meets-street" / "datasets" / "adopted_q4_states_v2.json"
SEED = 20260917; N = 1_000_000
BASE = 121.9; THR_HI = 134.0; THR_LO = 131.0
thr_hi_g = (THR_HI / BASE - 1) * 100; thr_lo_g = (THR_LO / BASE - 1) * 100   # 9.9262, 7.4651
C02_V2 = (0.18, 0.17, 0.30, 0.31, 0.04); MIDS = (10.75, 9.75, 8.0, 6.0, None)
W = (0.5, 0.3, 0.2)


def draw(q3_mu=9.5, q3_sd=1.70, q3_ref=9.5, q4_mu=8.1, beta=0.5, res_sd=2.0, tail_w=0.12, tail_mu=5.5, tail_sd=1.5,
         vec=C02_V2, cushion_mu=1.0, cushion_sd=1.3, street_mu=thr_hi_g, street_sd=1.23, w=W, seed=SEED, n=N):
    rng = np.random.default_rng(seed)
    q3 = rng.normal(q3_mu, q3_sd, n); tail = rng.random(n) < tail_w
    q4_v1 = np.where(tail, tail_mu + beta * (q3 - q3_ref) + rng.normal(0, tail_sd, n),
                     q4_mu + beta * (q3 - q3_ref) + rng.normal(0, res_sd, n))
    b = rng.choice(5, size=n, p=np.array(vec) / sum(vec))
    mids = np.array([m if m is not None else np.nan for m in MIDS])
    q4_v2 = mids[b] + rng.normal(cushion_mu, cushion_sd, n); q4_v2 = np.where(np.isnan(q4_v2), q4_v1, q4_v2)
    q4_v3 = rng.normal(street_mu, street_sd, n)
    comp = rng.choice(3, size=n, p=np.array(w) / sum(w))
    q4 = np.select([comp == 0, comp == 1, comp == 2], [q4_v1, q4_v2, q4_v3])
    return q3, q4, comp, b, q4_v1, q4_v2, q4_v3


def stats(q4, q3=None):
    nights = np.round(BASE * (1 + q4 / 100), 1); hi = nights >= THR_HI; lo = nights <= THR_LO
    d = dict(p_le_131=float(lo.mean()), p_ge_134=float(hi.mean()), p_mid=float(1 - hi.mean() - lo.mean()),
             mean=float(q4.mean()), sd=float(q4.std()), median=float(np.median(q4)),
             e_given_le_131=float(q4[lo].mean()), e_given_not_le_131=float(q4[~lo].mean()))
    if q3 is not None:
        d["q3_given_le_131"] = float(q3[lo].mean()); d["e_q3"] = float(q3.mean())
    return d


if __name__ == "__main__":
    q3, q4, comp, b, v1, v2, v3 = draw()
    S = stats(q4, q3); S1 = stats(v1); S2 = stats(v2); S3 = stats(v3)
    adopted = json.load(open(ADOPTED))
    pub = adopted["events"]["B13_printed_le_131_0m"]["p"]
    print("threshold: <=131.0m = %.4f%% y/y ; >=134.0m = %.4f%%" % (thr_lo_g, thr_hi_g))
    print("B13 P(<=131.0m) rebuild %.4f  vs adopted_q4_states_v2.json %.4f  (delta %.4f)" % (S["p_le_131"], pub, S["p_le_131"] - pub))
    print("mixture mean %.4f sd %.4f ; P(>=134.0m) %.4f ; middle %.4f" % (S["mean"], S["sd"], S["p_ge_134"], S["p_mid"]))
    print("E[4Q26 | Yes] %.3f ; E[3Q26 | Yes] %.3f ; E[3Q26] %.3f" % (S["e_given_le_131"], S["q3_given_le_131"], S["e_q3"]))
    print("views: V1 %.4f  V2 %.4f  V3 %.4f" % (S1["p_le_131"], S2["p_le_131"], S3["p_le_131"]))

    nights = np.round(BASE * (1 + q4 / 100), 1); lo = nights <= THR_LO; hi = nights >= THR_HI
    with open(HERE / "b13_v2_summary.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["item", "value"])
        for k, v in S.items(): w.writerow([k, round(v, 4)])
        w.writerow(["adopted_file_p_le_131", pub])
    with open(HERE / "b13_v2_views.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["view", "p_le_131", "p_ge_134", "mean", "sd"])
        for nm, s in [("V1_decomposition", S1), ("V2_guide_route", S2), ("V3_street_bar", S3), ("mixture 0.5/0.3/0.2", S)]:
            w.writerow([nm, round(s["p_le_131"], 4), round(s["p_ge_134"], 4), round(s["mean"], 3), round(s["sd"], 3)])
    with open(HERE / "b13_v2_conditional.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["condition", "p_le_131", "p_ge_134", "q4_mean", "n"])
        for lo_, hi_ in [(-99, 9.0), (9.0, 10.0), (10.0, 10.6), (10.6, 99)]:
            m = (q3 >= lo_) & (q3 < hi_)
            w.writerow(["3Q26 print in [%s,%s)" % (lo_, hi_), round(float(lo[m].mean()), 4), round(float(hi[m].mean()), 4),
                        round(float(q4[m].mean()), 3), int(m.sum())])
            print("  3Q26 in [%s,%s): P(<=131.0m) %.4f" % (lo_, hi_, lo[m].mean()))
        for k, lbl in enumerate(["low double digits", "around 10", "high single digits", "mid single / moderate", "no descriptor"]):
            m = (comp == 1) & (b == k)
            w.writerow(["5 Nov bucket = %s (V2 component)" % lbl, round(float(lo[m].mean()), 4), round(float(hi[m].mean()), 4),
                        round(float(q4[m].mean()), 3), int(m.sum())])
            print("  bucket %-22s P(<=131.0m) %.4f" % (lbl, lo[m].mean()))
    sens = [("adopted object (base)", {}),
            ("V2 cushion 1.5 (auditor A17: 4 of 4 Q4 guides met)", dict(cushion_mu=1.5)),
            ("V2 cushion 2.0 (4Q25 style, +4.8)", dict(cushion_mu=2.0)),
            ("V2 cushion 0.6 (no low-ball)", dict(cushion_mu=0.6)),
            ("V1 centre 7.61 (RNPL unified module base)", dict(q4_mu=7.61)),
            ("V1 centre 8.9 (case A, NA-only lap)", dict(q4_mu=8.9)),
            ("V1 residual sd 1.4 (revision 1)", dict(res_sd=1.4)),
            ("V1 residual sd 2.5", dict(res_sd=2.5)),
            ("no short tail", dict(tail_w=0.0)), ("short tail 25%", dict(tail_w=0.25)),
            ("Q3 centre 9.2 (external stack)", dict(q3_mu=9.2)), ("Q3 centre 9.9 (team)", dict(q3_mu=9.9)),
            ("Q3 sd 2.159 (naive)", dict(q3_sd=2.159)),
            ("pass-through 0.3", dict(beta=0.3)), ("pass-through 0.8", dict(beta=0.8)),
            ("V3 sd 2.0m (0.164 in growth pts)", dict(street_sd=1.64)),
            ("V3 re-centred on the measured at-print beat +0.9% (A17-25)", dict(street_mu=thr_hi_g + 0.9 * 134.0 / 121.9, street_sd=1.64)),
            ("blend 0.6/0.3/0.1", dict(w=(0.6, 0.3, 0.1))), ("blend 0.4/0.4/0.2", dict(w=(0.4, 0.4, 0.2))),
            ("blend 0.7/0.2/0.1", dict(w=(0.7, 0.2, 0.1))), ("equal thirds", dict(w=(1 / 3, 1 / 3, 1 / 3))),
            ("V1 only", dict(w=(1, 0, 0))),
            ("joint weak (V1 7.61, tail 25%, Q3 9.2, cushion 0.6)", dict(q4_mu=7.61, tail_w=0.25, q3_mu=9.2, cushion_mu=0.6)),
            ("joint strong (V1 8.9, beta 0.8, no tail, Q3 9.9, cushion 2.0)", dict(q4_mu=8.9, beta=0.8, tail_w=0.0, q3_mu=9.9, cushion_mu=2.0))]
    with open(HERE / "b13_v2_sensitivity.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["case", "p_le_131", "p_ge_134", "mean", "sd", "e_q4_given_yes"])
        for name, kw in sens:
            s = stats(draw(**kw)[1])
            w.writerow([name, round(s["p_le_131"], 4), round(s["p_ge_134"], 4), round(s["mean"], 3), round(s["sd"], 3),
                        round(s["e_given_le_131"], 3)])
            print("%-58s P(<=131.0m) %.4f  P(>=134.0m) %.4f  mean %.3f" % (name, s["p_le_131"], s["p_ge_134"], s["mean"]))
