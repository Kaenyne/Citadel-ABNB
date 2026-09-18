"""X01 revision 2 (batch A19 audit response): the revision-1 joint, unchanged, RE-CLASSIFIED.

Revision 1's `x01_joint.py` is left exactly as it was (audit trail). Nothing in the joint moves:
the same seed, the same draws, the same marginals. What changes is the classification laid over it:

  A19-01  base is gated on a DECELERATING print (latent < 10.09, S01 revision 2's dead-band line),
          not on "print < 10.6%", which is the thesis-breaker threshold.
  A19-07  precedence (breaker-first) is published beside short-first, as a convention with no textual basis.
  A19-10  the "material" reading's explicit-bucket share of C02 (d) is branch-varying
          (0.492 / 0.348 / 0.208 for x < 9 / 9-10 / >= 10), derived from C02's own conditioning block,
          not a constant 0.387.
  A19-04  the PRINT-PARTITION table (<=8.5% / 8.5-10.6% / >=10.6%) is computed and published as a
          separate object from X01's disclosure-gate vector; it is what the memo's 25/45/30 row is.
  A19-08  the probability-weighted 15 Dec close is published on the MEAN convention as well as
          the (non-mixable) median-of-branches convention.
  A19-09  the memo's conjunctive short-case mass is recomputed (0.0462, not 0.050).

Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/scenario-probabilities/datasets/x01_reclassify_v2.py
Writes x01_v2_summary.json next to this file. About one minute (one 1,000,000-draw simulate() call
plus one for the C04 (d) = 0.20 material variant).
"""
import json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import x01_joint as M                                    # noqa: E402  (the revision-1 joint, untouched)

R01, R02, SHORT = M.THR_R01, M.THR_R02, M.SHORT_NIGHTS_THR
DECEL = M.S01_DECEL_THR                                  # 10.09, S01 revision 2's dead band on 2Q26's 10.34
OPTS = M.OPTS

# branch-varying explicit-bucket share of C02 (d), from C02's own conditioning block
# (directional mass per branch = P(directional) x P(moderate | directional), C02 revision 2)
DIRECTIONAL = {"lt9": 0.35 * 0.75, "9to10": 0.28 * 0.60, "ge10": 0.25 * 0.55}
EXPL = {k: float(1 - DIRECTIONAL[k] / M.c02_branch[k]["cond"][3]) for k in DIRECTIONAL}


def classify(J, base_thr=DECEL, reading="literal", precedence="breaker_first", use_c04=True,
             short_thr=SHORT, u_material=None):
    x, c02, c04, below = J["x"], J["c02"], J["c04"], J["below"]
    breaker = (x >= R02) & (c02 == "a")
    if reading == "literal":
        d_gate = c02 == "d"
    elif reading == "material_const":
        d_gate = J["explicit_d"]
    else:                                                # material, branch-varying share
        sh = np.where(x < 9.0, EXPL["lt9"], np.where(x < 10.0, EXPL["9to10"], EXPL["ge10"]))
        d_gate = (c02 == "d") & (u_material < sh)
    c04d = (c04 == "d") if use_c04 else np.zeros(len(x), bool)
    short = (x < short_thr) | d_gate | c04d
    base = (x < base_thr) & (np.isin(c02, ["b", "c"]) | below) & ~short
    opt = np.full(len(x), 3)
    if precedence == "breaker_first":
        opt[short] = 2; opt[base] = 1; opt[breaker] = 0
    else:
        opt[base] = 1; opt[breaker] = 0; opt[short] = 2
    return opt


def vec(opt):
    return {o: round(float((opt == i).mean()), 4) for i, o in enumerate(OPTS)}


def cell(J, m):
    r, c = J["r"][m], J["close"][m]
    return dict(p=round(float(m.mean()), 4), day1_median=round(float(np.median(r)), 2),
                day1_mean=round(float(r.mean()), 2), day1_p_le_m8=round(float((r <= -8).mean()), 3),
                day1_p_ge_5=round(float((r >= 5).mean()), 3), day1_p_lt_0=round(float((r < 0).mean()), 3),
                dec15_median=round(float(np.median(c)), 1), dec15_mean=round(float(c.mean()), 1),
                dec15_p25=round(float(np.percentile(c, 25)), 1), dec15_p75=round(float(np.percentile(c, 75)), 1),
                dec15_p_le_150=round(float((c <= 150).mean()), 3), dec15_p_ge_180=round(float((c >= 180).mean()), 3),
                nights_mean=round(float(J["x"][m].mean()), 2), p_c01_below=round(float(J["below"][m].mean()), 3))


if __name__ == "__main__":
    J = M.simulate(M.P)
    x, c02, c04 = J["x"], J["c02"], J["c04"]
    um = np.random.default_rng(M.SEED + 7).random(len(x))        # independent uniform for the material split
    out = {"explicit_bucket_share_of_c02_d_by_branch": {k: round(v, 3) for k, v in EXPL.items()}}

    out["vectors"] = {
        "revision_2_headline (literal, decelerating base gate, breaker-first)": vec(classify(J)),
        "revision_1_published (base gate 10.6)": vec(classify(J, base_thr=R02)),
        "strict decel (<10.34, 2Q26's rate)": vec(classify(J, base_thr=10.34)),
        "lenient (decel OR flat-with-guide-below-Street)": None,
        "short-first precedence": vec(classify(J, precedence="short_first")),
        "material reading (branch-varying share)": vec(classify(J, reading="material_branch", u_material=um)),
        "material reading (constant 0.387 share, revision 1)": vec(classify(J, reading="material_const")),
        "no C04 leg": vec(classify(J, use_c04=False)),
        "short nights gate 8.0 / 9.0": None,
    }
    short = (x < SHORT) | (c02 == "d") | (c04 == "d")
    breaker = (x >= R02) & (c02 == "a")
    base_len = ((x < DECEL) | ((x < R02) & J["below"])) & (np.isin(c02, ["b", "c"]) | J["below"]) & ~short
    o = np.full(len(x), 3); o[short] = 2; o[base_len] = 1; o[breaker] = 0
    out["vectors"]["lenient (decel OR flat-with-guide-below-Street)"] = vec(o)
    out["vectors"]["short nights gate 8.0 / 9.0"] = [vec(classify(J, short_thr=t)) for t in (8.05, 9.05)]

    opt = classify(J)
    tab = {o2: cell(J, opt == i) for i, o2 in enumerate(OPTS)}
    out["scenario_table_revision_2"] = tab
    out["pw_dec15"] = dict(
        mean_convention=round(sum(tab[o2]["p"] * tab[o2]["dec15_mean"] for o2 in OPTS), 2),
        median_of_branches=round(sum(tab[o2]["p"] * tab[o2]["dec15_median"] for o2 in OPTS), 2),
        unconditional_median=round(float(np.median(J["close"])), 2),
        unconditional_mean=round(float(J["close"].mean()), 2))

    part = {"short (<=8.5%)": x < SHORT, "base (8.5-10.6%)": (x >= SHORT) & (x < R02), "breaker (>=10.6%)": x >= R02}
    out["print_partition_table"] = {k: cell(J, m) for k, m in part.items()}
    out["memo_conjunctions"] = dict(
        short_le8_5_and_c02d_and_c04d=round(float(((x < SHORT) & (c02 == "d") & (c04 == "d")).mean()), 4),
        short_le8_5_and_c02d_or_c04d=round(float(((x < SHORT) & ((c02 == "d") | (c04 == "d"))).mean()), 4),
        breaker_ge10_6_and_c02a_and_c04b=round(float(((x >= R02) & (c02 == "a") & (c04 == "b")).mean()), 4))

    sm, nm = opt == 2, opt == 3
    out["compositions"] = dict(
        short_directional_share=round(float(((c02 == "d") & ~J["explicit_d"] & sm).mean() / sm.mean()), 3),
        short_accel_state_share=round(float((J["state"][sm] == "accel").mean()), 3),
        short_print_ge_10_0_share=round(float((x[sm] >= R01).mean()), 3),
        short_print_ge_10_0_mass=round(float((sm & (x >= R01)).mean()), 4),
        none_dead_band_share=round(float(((x >= DECEL) & (x < R02))[nm].mean()), 3),
        none_accel_share=round(float((x >= R02)[nm].mean()), 3),
        none_p_c01_below=round(float(J["below"][nm].mean()), 3),
        base_to_none_reclassified_by_the_gate_fix=round(
            float(((classify(J, base_thr=R02) == 1) & (opt == 3)).mean()), 4))
    out["day1_dec15_dependence"] = dict(
        corr_overall=round(float(np.corrcoef(J["r"], np.log(J["close"]))[0, 1]), 4),
        corr_within_state={s: round(float(np.corrcoef(J["r"][J["state"] == s],
                                                      np.log(J["close"][J["state"] == s]))[0, 1]), 4)
                           for s in ("decel", "flat", "accel")})
    out["unconditional"] = dict(day1_median=round(float(np.median(J["r"])), 2),
                                day1_mean=round(float(J["r"].mean()), 2),
                                day1_p_le_m8=round(float((J["r"] <= -8).mean()), 3),
                                day1_p_ge_5=round(float((J["r"] >= 5).mean()), 3))

    json.dump(out, open(HERE / "x01_v2_summary.json", "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1))
    print("written:", HERE / "x01_v2_summary.json")
