"""R14 revision 2 (audit A13 response). Revision 1 is r14_model.py (untouched, with r14_base_rates.json / r14_summary.json /
r14_sensitivity.csv). Part A of revision 1 (record, S1 residual, Feb event sd) is unchanged and not re-run here; the log's
'3 of 14' was a transcription error against that file's post2022_ge5_raw = 2 (A13-05).
Mixture changes, each tied to a finding:
  - A13-03: the S01 panel cells are used EX the four post-2022 Q4 prints (aa +8.85 n2, ab -8.35 n2, fl -8.7 n1, da -2.60 n3,
    db -7.55 n4) and the Q4 premium is the leave-one-out deviation of those four prints from the ex-Q4 cells (+8.85, not the
    S1-residual gap +10.29), still carried at 30% (= +2.66)
  - A13-04: P(1Q27 revenue guide >= gap-adjusted Street +11.0%) = 0.45 from F02 revision 2's percentile table
  - A13-17: the adopted 3Q26 object N(9.5, 1.70) (risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json) and the
    F01/F02 revision-2 V1 conditional 4Q26 = 8.1 + 0.5 (Q3 - 9.5) + N(0, 1.4), 12% tail N(5.5, 1.5)
  - A13-16: the model's total day-1 sd is reported and compared with the 9.0% Feb event sd; the t5 residual stays 8.5
Seed 20260917, n 400,000. Run from the repo root:
  py -3.13 docs/pitch-forecasts/questions/risk-feb-print-up-day/datasets/r14_model_v2.py
"""
import numpy as np, json, csv, pathlib, math
from scipy.stats import norm
HERE = pathlib.Path(__file__).resolve().parent; N = 400_000
CELLS_FULL = dict(aa=7.43, ab=-0.77, fl=-8.7, da=0.78, db=-7.55)      # s01_cells.csv raw means (revision 1)
CELLS_EXQ4 = dict(aa=8.85, ab=-8.35, fl=-8.7, da=-2.60, db=-7.55)     # ex 4Q22 / 4Q23 / 4Q24 / 4Q25 (A13-03)
LOO_PREMIUM = 8.85                                                      # mean deviation of the four Q4 prints from the ex-Q4 cells
def run(seed=20260917, n3=(9.5, 1.70), q4_slope=0.5, q4_base=8.1, q4_sd=1.4, tail_w=0.12, tail=(5.5, 1.5), band=0.25, p_guide_ge=0.45,
        mu_cell=None, shrink=0.65, q4_uplift=0.30 * LOO_PREMIUM, resid_sd=8.5, df=5, qqq_sd=1.3, thr=5.0, unc=-1.0, n4_override=None, corr=0.5):
    rng = np.random.default_rng(seed)
    if mu_cell is None: mu_cell = CELLS_EXQ4
    z1 = rng.standard_normal(N); z2 = corr * z1 + math.sqrt(1 - corr ** 2) * rng.standard_normal(N)
    x3 = n3[0] + n3[1] * z1
    if n4_override is None: x4 = q4_base + q4_slope * (x3 - n3[0]) + q4_sd * rng.standard_normal(N)
    else: x4 = n4_override[0] + n4_override[1] * z2   # revision-1 construction: independent draw with corr (0.5 in revision 1)
    t = rng.random(N) < tail_w; x4 = np.where(t, tail[0] + tail[1] * rng.standard_normal(N), x4)
    d = x4 - x3; state = np.where(d >= band, 0, np.where(d > -band, 1, 2))
    g = rng.random(N) < p_guide_ge
    sh = lambda m: unc + shrink * (m - unc)
    mu = np.where(state == 0, np.where(g, sh(mu_cell["aa"]), sh(mu_cell["ab"])), np.where(state == 1, sh(mu_cell["fl"]), np.where(g, sh(mu_cell["da"]), sh(mu_cell["db"]))))
    mu = mu + q4_uplift
    r = mu + resid_sd * rng.standard_t(df, N) / math.sqrt(df / (df - 2)) + qqq_sd * rng.standard_normal(N)
    up = r >= thr; dn = r <= -5
    return dict(p_ge5=float(up.mean()), p_lt0=float((r < 0).mean()), p_ge10=float((r >= 10).mean()), p_le_m5=float(dn.mean()), p_le_m8=float((r <= -8).mean()),
                p_3_to_5=float(((r >= 3) & (r < 5)).mean()),
                mean=float(r.mean()), sd=float(r.std()), mu_sd=float(mu.std()), p_accel=float((state == 0).mean()), p_flat=float((state == 1).mean()), p_decel=float((state == 2).mean()),
                p_ge5_by_state={k: float((r[state == i] >= thr).mean()) for i, k in enumerate(["accel", "flat", "decel"])},
                p_ge5_given_guide_ge=float((r[g] >= thr).mean()), p_ge5_given_guide_below=float((r[~g] >= thr).mean()),
                E_r_given_ge5=float(r[up].mean()), E_r_given_le_m5=float(r[dn].mean()), up_tail_pts=float(up.mean() * r[up].mean()), down_tail_pts=float(dn.mean() * r[dn].mean()),
                E_x4_given_ge5=float(x4[up].mean()), E_x4=float(x4.mean()), P_x4_ge_9_9_given_ge5=float((x4[up] >= 9.9).mean()), P_x4_ge_9_9=float((x4 >= 9.9).mean()),
                P_guide_ge_given_ge5=float(g[up].mean()), P_guide_ge_given_le_m5=float(g[dn].mean()),
                pct={str(q): float(np.percentile(r, q)) for q in (5, 10, 25, 50, 75, 90, 95)})
if __name__ == "__main__":
    base = run(); print(json.dumps(base, indent=1))
    sens = [("base (revision 2)", {}),
            ("bridge: revision 1 (full cells, uplift 3.0, p_guide 0.33, N(9.55,1.48) x N(8.1,1.6) corr 0.5)", dict(mu_cell=CELLS_FULL, q4_uplift=3.0, p_guide_ge=0.33, n3=(9.55, 1.48), n4_override=(8.1, 1.6))),
            ("bridge: rev-1 cells/uplift, p_guide 0.45 only", dict(mu_cell=CELLS_FULL, q4_uplift=3.0)),
            ("bridge: ex-Q4 cells + LOO uplift 2.66, p_guide 0.33", dict(p_guide_ge=0.33)),
            ("bridge: full cells + uplift 1.7 (auditor's equivalent), p_guide 0.45", dict(mu_cell=CELLS_FULL, q4_uplift=1.7)),
            ("no Q4 uplift", dict(q4_uplift=0.0)), ("Q4 uplift at 50% of LOO (+4.4)", dict(q4_uplift=0.5 * LOO_PREMIUM)), ("Q4 uplift at the full LOO premium (+8.85)", dict(q4_uplift=LOO_PREMIUM)),
            ("Q4 uplift 30% of the S1 gap (+3.1) on ex-Q4 cells", dict(q4_uplift=0.3 * 10.29)),
            ("cell means unshrunk", dict(shrink=1.0)), ("cell means market-neutral (shrink 0)", dict(shrink=0.0)),
            ("4Q26 nights centred on the Street 9.9 sd 1.2, no tail, corr 0.5 with 3Q26", dict(n4_override=(9.9, 1.2), tail_w=0.0)),
            ("4Q26 at the RNPL module 7.6 (base 7.6, same slope)", dict(q4_base=7.6)),
            ("3Q26 at the Street 11.1 (sd 0.85), 4Q26 9.9 sd 1.2, no tail", dict(n3=(11.1, 0.85), n4_override=(9.9, 1.2), tail_w=0.0)),
            ("3Q26 N(9.67,1.70) (R01 rev 2 centre)", dict(n3=(9.67, 1.70))),
            ("P(1Q27 guide >= Street) 0.60", dict(p_guide_ge=0.60)), ("P(1Q27 guide >= Street) 0.30", dict(p_guide_ge=0.30)),
            ("residual sd 8.0 (t5)", dict(resid_sd=8.0)), ("residual sd 9.5 (t5)", dict(resid_sd=9.5)), ("normal residual", dict(df=200)),
            ("unconditional centre -2.6 (post-2022 excess mean)", dict(unc=-2.6)), ("unconditional centre +1.2 (all-print raw mean)", dict(unc=1.2)),
            ("joint bull: Street nights, guide>=Street 0.6, uplift 4.4", dict(n4_override=(9.9, 1.2), tail_w=0.0, p_guide_ge=0.6, q4_uplift=0.5 * LOO_PREMIUM)),
            ("joint bear: module nights, guide>=Street 0.30, no uplift", dict(q4_base=7.6, p_guide_ge=0.30, q4_uplift=0.0))]
    with open(HERE / "r14_v2_sensitivity.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["case", "p_ge5", "p_lt0", "p_le_m5", "mean", "sd", "p_accel"])
        for name, kw in sens:
            r = run(**kw); wr.writerow([name, round(r["p_ge5"], 4), round(r["p_lt0"], 4), round(r["p_le_m5"], 4), round(r["mean"], 2), round(r["sd"], 2), round(r["p_accel"], 3)])
            print("%-92s p>=5 %.4f  p<0 %.3f  p<=-5 %.3f  mean %+.2f  sd %.2f  P(accel) %.3f" % (name, r["p_ge5"], r["p_lt0"], r["p_le_m5"], r["mean"], r["sd"], r["p_accel"]))
    for sd in (8.0, 8.5, 9.0, 9.5):
        print("anchor sd %.1f: P(>=5) %.4f (mode -0.4)  %.4f (mean 0)" % (sd, 1 - norm.cdf((5 + 0.4) / sd), 1 - norm.cdf(5 / sd)))
    # base-rate route (A13-05): Q4 class Laplace at half weight; other half = mean of all-print raw (6/23) and post-2022 Laplace (3/16)
    q4_lap = (3 + 1) / (6 + 2); allp = 6 / 23; post22_lap = (2 + 1) / (14 + 2)
    print("base rate: Q4 Laplace %.3f; all-print %.3f; post-2022 Laplace %.3f; blend 0.5*Q4 + 0.5*mean(all, post-2022) = %.3f; auditor 0.5*Q4 + 0.5*0.19 = %.3f"
          % (q4_lap, allp, post22_lap, 0.5 * q4_lap + 0.5 * (allp + post22_lap) / 2, 0.5 * q4_lap + 0.5 * 0.19))
    json.dump(base, open(HERE / "r14_v2_summary.json", "w"), indent=1)
