"""B12 revision 2 (audit A17 response). Revision 1 is b12_model.py (untouched, with b12_sensitivity.csv).
B12 is a re-cut of F03's February FY27 margin sentence under B12's own resolution text, so revision 2 stops
carrying its own copy of the regime machinery and re-implements F03 REVISION 2's joint engine
(../fy27-margin-guide/datasets/f03_f04_joint_v2.py) parameter-for-parameter:
  * FY26 print A ~ N(35.72, 0.58) from C04 revision 2, with C04's 50% floor-defence rule (A17-11)
  * latent reinvestment intensity z ~ N(0,1) tilting the regime log-odds (T1 +0.5, T5 +0.8, T3 -0.2, T4 -0.7)
  * pre-tilt weights T1 .185 / T2 .215 / T3 .345 / T4 .065 / T5 .095 / T6 .075, realised
    T1 .19 / T2 .20 / T3 .34 / T4 .08 / T5 .12 / T6 .07
  * T1 floor = A - clip(1.25 + 0.4z + U(-0.75, 0.75), 0.25, 3.0) rounded down to the 0.5 grid; T2 floor =
    A - U(0, 0.25) rounded down to the 0.5 grid
Readings (unchanged from revision 1, section 0b): LITERAL Yes if T5 or a numeric floor strictly below the
one-decimal FY26 print; MATERIAL Yes if T5 or the floor is at least 50bp below it.
What revision 2 adds beyond re-citing revision 2 of F03:
  * the gap distribution GIVEN A MATERIAL Yes, which revision 1 never computed but priced at -$7 (A17-22)
  * the realised-FY27-margin arithmetic that the section-9 impact table uses, on ONE base at a time
    (realised = floor + U(0.6, 1.4) on the 60-140bp beat record, n 3; T5 = print - |N(1.0, 0.5)|), so the
    row against the team's line build and the row against the Street are computed, not asserted (A17-12)
  * the two structural variants A17 asked for: T5 as a language overlay on the numeric floor (A17-09) and
    T2 halved / zeroed (A17-10) - reported as sensitivities, NOT adopted, because the regime weights are
    F03 revision 2's adopted object and re-weighting them here would put two F03s in one deck
numpy only, seed 20260917, 400,000 draws (~5 s). Writes b12_v2_summary.csv and b12_v2_sensitivity.csv here.
Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/bonus-fy27-investment-year/datasets/b12_model_v2.py
"""
import numpy as np, csv, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SEED = 20260917; N = 400_000
BASE_W = dict(T1=0.185, T2=0.215, T3=0.345, T4=0.065, T5=0.095, T6=0.075)
TILT = dict(T1=0.5, T2=0.0, T3=-0.2, T4=-0.7, T5=0.8, T6=0.0)
STREET_MARGIN = 36.45; TEAM_LINE_BUILD = 35.7          # 23_vs_consensus.csv ; notes/40_line_build.md
STREET_REV = 15829.; STREET_EBITDA = 5766.; SPOT = 167.51; EPS_PER_MUSD = 0.0014


def run(seed=SEED, n=N, A_mu=35.72, A_sd=0.58, p_cut=0.50, w=None, tilt=None, h1=(0.5, 2.0), h2=(0.0, 0.25),
        material=0.5, t5_overlay=0.0, beat=(0.6, 1.4)):
    """t5_overlay: the share of T5 draws that are a down/investment-year GLOSS ON A T1 NUMERIC FLOOR
    (the Feb 2024 form: Mertz's 'the modest guide down' described the FY24 floor) rather than a standalone
    sentence. Overlay draws resolve through the T1 floor, so under both readings they are Yes anyway - which
    is the point A17-09 misses: the overlay reframing on its own is worth about +0.004, not -0.07."""
    w = dict(BASE_W if w is None else w); tilt = dict(TILT if tilt is None else tilt)
    rng = np.random.default_rng(seed)
    zA = rng.standard_normal(n); A = A_mu + A_sd * zA
    cut = (A < 35.5) & (rng.random(n) < p_cut)
    A = np.where(cut, 35.5 + 0.1 + np.abs(rng.normal(0, 0.1, n)), A)
    A_r = np.round(A, 1)
    z = rng.standard_normal(n)
    keys = list(w.keys())
    lw = np.log(np.maximum(np.array([w[k] for k in keys]), 1e-12))[None, :] + z[:, None] * np.array([tilt[k] for k in keys])[None, :]
    P = np.exp(lw - lw.max(axis=1, keepdims=True)); P /= P.sum(axis=1, keepdims=True)
    T = (rng.random(n)[:, None] > np.cumsum(P, axis=1)).sum(axis=1)
    if t5_overlay > 0:                      # move that share of T5 into T1 (a floor described as an investment year)
        T = np.where((T == 4) & (rng.random(n) < t5_overlay), 0, T)
    hc = np.clip(0.5 * (h1[0] + h1[1]) + 0.4 * z + rng.uniform(-0.5 * (h1[1] - h1[0]), 0.5 * (h1[1] - h1[0]), n), 0.25, 3.0)
    f1 = np.floor((A - hc) / 0.5) * 0.5
    f2 = np.floor((A - rng.uniform(h2[0], h2[1], n)) / 0.5) * 0.5
    lvl = np.where(T == 0, f1, np.where(T == 1, f2, np.nan))
    floor_ = np.where(T <= 1, lvl, np.nan)
    lit = (T == 4) | ((T <= 1) & (floor_ < A_r))
    mat = (T == 4) | ((T <= 1) & (floor_ <= A_r - material))
    gap = np.where(T <= 1, A_r - floor_, np.nan)
    realised = np.where(T <= 1, floor_ + rng.uniform(beat[0], beat[1], n), A_r - np.abs(rng.normal(1.0, 0.5, n)))

    def block(mask, label):
        g = gap[mask & (T <= 1)]; r = realised[mask]
        d_street = float(r.mean()) - STREET_MARGIN; d_team = float(r.mean()) - TEAM_LINE_BUILD
        d_eb = d_street / 100 * STREET_REV
        return dict(label=label, p=float(mask.mean()),
                    share_numeric=float((mask & (T <= 1)).sum() / mask.sum()),
                    share_t5=float((mask & (T == 4)).sum() / mask.sum()),
                    gap_mean=float(g.mean()), gap_p10=float(np.percentile(g, 10)), gap_p50=float(np.percentile(g, 50)),
                    gap_p90=float(np.percentile(g, 90)), gap_lt_50bp=float((g < 0.5).mean()), gap_gt_150bp=float((g > 1.5).mean()),
                    e_floor=float(np.nanmean(floor_[mask])), e_realised=float(r.mean()),
                    d_vs_street_pp=d_street, d_vs_team_pp=d_team, d_ebitda_musd=d_eb,
                    d_eps_usd=d_eb * EPS_PER_MUSD, stock_usd=d_eb / STREET_EBITDA * SPOT)
    return dict(literal=float(lit.mean()), material=float(mat.mean()),
                reg_w={k: float((T == i).mean()) for i, k in enumerate(keys)},
                fy26_mean=float(A.mean()), fy26_p_lt_355=float((A < 35.5).mean()),
                lit_block=block(lit, "literal"), mat_block=block(mat, "material"))


if __name__ == "__main__":
    r = run()
    print("F03 revision-2 engine, B12 readings: literal %.4f  material %.4f" % (r["literal"], r["material"]))
    print("  (F03 revision 2 publishes B12 literal 0.51 / material 0.38 from the same draws)")
    print("  FY26 print mean %.4f  P(A < 35.5) %.4f ; realised regime weights %s"
          % (r["fy26_mean"], r["fy26_p_lt_355"], {k: round(v, 3) for k, v in r["reg_w"].items()}))
    for b in (r["lit_block"], r["mat_block"]):
        print("  %-9s P %.4f | numeric %.3f / T5 %.3f | gap mean %.2f p50 %.2f p90 %.2f  <50bp %.3f  >150bp %.3f"
              % (b["label"], b["p"], b["share_numeric"], b["share_t5"], b["gap_mean"], b["gap_p50"], b["gap_p90"],
                 b["gap_lt_50bp"], b["gap_gt_150bp"]))
        print("  %-9s E[floor|Yes] %.2f  E[realised FY27 margin|Yes] %.2f  vs team line build %+.2fpp  vs Street %+.2fpp"
              % ("", b["e_floor"], b["e_realised"], b["d_vs_team_pp"], b["d_vs_street_pp"]))
        print("  %-9s dEBITDA %+.0f M  dEPS %+.3f  stock at a constant multiple %+.2f  EV at P %+.2f"
              % ("", b["d_ebitda_musd"], b["d_eps_usd"], b["stock_usd"], b["p"] * b["stock_usd"]))
    sens = [("base: F03 revision 2 regime weights and C04 revision-2 FY26 print", {}),
            ("A17-09 as written: T5 a LANGUAGE OVERLAY on the T1 floor (70% of T5)", dict(t5_overlay=0.70)),
            ("A17-09 as computed by the audit: T5 mass moved to T3/T6 (T5 -> 0.03)",
             dict(w=dict(T1=0.185, T2=0.215, T3=0.405, T4=0.065, T5=0.030, T6=0.100))),
            ("A17-10: T2 halved (no February letter has used the form)",
             dict(w=dict(T1=0.185, T2=0.108, T3=0.452, T4=0.065, T5=0.095, T6=0.075))),
            ("A17-10: T2 = 0 (the two readings coincide)",
             dict(w=dict(T1=0.185, T2=0.0, T3=0.560, T4=0.065, T5=0.095, T6=0.075))),
            ("both A17 structural corrections together",
             dict(w=dict(T1=0.185, T2=0.108, T3=0.512, T4=0.065, T5=0.030, T6=0.100))),
            ("numeric dominant (T1 .30 T2 .25 T3 .20)", dict(w=dict(T1=0.30, T2=0.25, T3=0.20, T4=0.05, T5=0.12, T6=0.08))),
            ("qualitative dominant (T3 .45)", dict(w=dict(T1=0.12, T2=0.12, T3=0.45, T4=0.10, T5=0.10, T6=0.11))),
            ("explicit investment-year 0.25 (T5)", dict(w=dict(T1=0.20, T2=0.16, T3=0.25, T4=0.05, T5=0.25, T6=0.09))),
            ("expand 0.20 (T4, bull)", dict(w=dict(T1=0.15, T2=0.20, T3=0.25, T4=0.20, T5=0.10, T6=0.10))),
            ("FY26 print 36.1 (C04 'approximately 36%' branch)", dict(A_mu=36.1)),
            ("FY26 print 35.6", dict(A_mu=35.6)),
            ("FY26 print revision 1 N(35.85, 0.55), 85% defence", dict(A_mu=35.85, A_sd=0.55, p_cut=0.85)),
            ("no floor defence (p_cut 0)", dict(p_cut=0.0)),
            ("T1 haircut band 1.0-2.0 (revision 1)", dict(h1=(1.0, 2.0))),
            ("T2 haircut band 0-50bp", dict(h2=(0.0, 0.50))),
            ("material threshold 100bp", dict(material=1.0))]
    with open(HERE / "b12_v2_sensitivity.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["case", "literal", "material", "T1", "T2", "T3", "T4", "T5", "T6",
                                         "lit_stock_usd", "mat_stock_usd"])
        for name, kw in sens:
            rr = run(**kw)
            wr.writerow([name, round(rr["literal"], 4), round(rr["material"], 4)]
                        + [round(rr["reg_w"][k], 3) for k in BASE_W]
                        + [round(rr["lit_block"]["stock_usd"], 2), round(rr["mat_block"]["stock_usd"], 2)])
            print("%-64s literal %.4f  material %.4f" % (name, rr["literal"], rr["material"]))
    with open(HERE / "b12_v2_summary.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["item", "value"])
        wr.writerow(["literal", round(r["literal"], 4)]); wr.writerow(["material", round(r["material"], 4)])
        for k, v in r["reg_w"].items(): wr.writerow(["regime_weight_" + k, round(v, 4)])
        for b in (r["lit_block"], r["mat_block"]):
            for k, v in b.items():
                if k != "label":
                    wr.writerow(["%s_%s" % (b["label"], k), round(float(v), 4)])
