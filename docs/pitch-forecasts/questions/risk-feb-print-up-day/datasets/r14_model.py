"""R14: P(day-1 close-to-close return after the 4Q26 print >= +5%).
Part A (measured): Q4-print base rates from data/processed/abnb_earnings_reactions.csv (the memo's '6 of 6' is checked), the
Q4-print residual against the pre-stated sign rule S1 (C note s.7: c -0.67, b +3.35 on the QQQ-excess return, 3Q22-2Q26), the
Feb-print event sd implied by the 15 Jan / 19 Mar 2027 expiries (S02 term structure, 16 Sep close).
Part B (mixture): (i) the 4Q26 printed nights acceleration sign vs 3Q26 (team objects: 3Q26 ~ N(9.55, 1.48), 4Q26 ~ N(8.1, 1.6)
with a 12% short tail N(5.5, 1.5), corr 0.5, 0.25pt dead band); (ii) the 1Q27 revenue guide vs the then-Street (F02 median +9.4%
vs gap-adjusted Street +11.0%: P(guide >= Street) 0.33); (iii) the panel cell means (S01 s01_cells.csv) shrunk toward the
unconditional; (iv) a Q4-print uplift carried at a fraction of the measured residual; (v) a t5 residual at the Feb event sd, plus
a QQQ term. Seed 20260917, n 400,000. Run: py -3.13 docs/pitch-forecasts/questions/risk-feb-print-up-day/datasets/r14_model.py"""
import numpy as np, json, csv, pathlib, math
import pandas as pd
from scipy.stats import norm
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[4]; N = 400_000
# ---------- Part A ----------
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
q4 = rx[rx.quarter.str.endswith("Q4")]
accel = {"3Q22", "3Q23", "4Q24", "3Q25", "4Q25", "2Q26"}; decel = {"4Q22", "1Q23", "2Q23", "4Q23", "1Q24", "2Q24", "1Q25", "2Q25", "1Q26"}; flat = {"3Q24"}
def lab(q): return q[5] + "Q" + q[2:4]   # 2022Q4 -> 4Q22
rx["lbl"] = rx.quarter.map(lab)
rx["sign"] = rx.lbl.map(lambda s: 1 if s in accel else (-1 if s in decel else (0 if s in flat else np.nan)))
rx["s1_pred_excess"] = -0.67 + 3.35 * rx.sign
rx["s1_resid"] = rx.excess_1d_pct - rx.s1_pred_excess
r16 = rx[rx.sign.notna()]
q4r = r16[r16.lbl.str.startswith("4Q")]; nq4 = r16[~r16.lbl.str.startswith("4Q")]
A = {"q4_prints_raw": q4[["quarter", "abnb_1d_pct", "excess_1d_pct"]].values.tolist(), "q4_n": int(len(q4)),
     "q4_positive_raw": int((q4.abnb_1d_pct > 0).sum()), "q4_positive_excess": int((q4.excess_1d_pct > 0).sum()),
     "q4_ge5_raw": int((q4.abnb_1d_pct >= 5).sum()), "q4_ge3.5_raw": int((q4.abnb_1d_pct >= 3.5).sum()), "q4_ge5_excess": int((q4.excess_1d_pct >= 5).sum()),
     "q4_mean_raw": float(q4.abnb_1d_pct.mean()), "q4_median_raw": float(q4.abnb_1d_pct.median()),
     "all_n": int(len(rx)), "all_ge5_raw": int((rx.abnb_1d_pct >= 5).sum()), "post2022_n": int((rx.quarter >= "2023Q1").sum()), "post2022_ge5_raw": int(((rx.quarter >= "2023Q1") & (rx.abnb_1d_pct >= 5)).sum()),
     "ex_reopening_n": int((rx.quarter >= "2022Q3").sum()), "ex_reopening_ge5_raw": int(((rx.quarter >= "2022Q3") & (rx.abnb_1d_pct >= 5)).sum()),
     "q4_post2022": q4[q4.quarter >= "2022Q4"][["quarter", "abnb_1d_pct"]].values.tolist(),
     "s1_resid_q4_3Q22plus": q4r[["lbl", "sign", "excess_1d_pct", "s1_resid"]].round(2).values.tolist(),
     "s1_resid_q4_mean": float(q4r.s1_resid.mean()), "s1_resid_q4_sd": float(q4r.s1_resid.std(ddof=1)), "s1_resid_nonq4_mean": float(nq4.s1_resid.mean()),
     "q4_effect_pts": float(q4r.s1_resid.mean() - nq4.s1_resid.mean()), "q4_effect_t": float((q4r.s1_resid.mean() - nq4.s1_resid.mean()) / math.sqrt(q4r.s1_resid.var(ddof=1) / len(q4r) + nq4.s1_resid.var(ddof=1) / len(nq4)))}
# Feb event sd from the Jan/Mar expiries
ts = pd.read_csv(ROOT / "docs/pitch-forecasts/questions/close-15dec-2026/datasets/implied_term_structure_20260917T031221Z.csv")
jan = ts[ts.expiry == "2027-01-15"].iloc[0]; mar = ts[ts.expiry == "2027-03-19"].iloc[0]
vj, vm = (jan.atm_iv / 100) ** 2 * jan["T"], (mar.atm_iv / 100) ** 2 * mar["T"]
A["feb_event_sd_by_bg_vol"] = {str(bg): float(math.sqrt(max(vm - vj - (bg / 100) ** 2 * (mar["T"] - jan["T"]), 0)) * 100) for bg in (29.0, 32.3, 33.85, 36.0)}
A["jan_mar_rows"] = {"jan": {"T": float(jan["T"]), "atm_iv": float(jan.atm_iv)}, "mar": {"T": float(mar["T"]), "atm_iv": float(mar.atm_iv)}}
json.dump(A, open(HERE / "r14_base_rates.json", "w"), indent=1); print(json.dumps(A, indent=1))
# ---------- Part B ----------
def run(seed=20260917, n3=(9.55, 1.48), n4=(8.1, 1.6), tail_w=0.12, tail=(5.5, 1.5), corr=0.5, band=0.25, p_guide_ge=0.33,
        mu_cell=None, shrink=0.65, q4_uplift=3.0, resid_sd=8.5, df=5, qqq_sd=1.3, thr=5.0, unc=-1.0):
    rng = np.random.default_rng(seed)
    if mu_cell is None: mu_cell = dict(aa=7.4, ab=-0.8, fl=-8.7, da=0.8, db=-7.6)   # S01 s01_cells.csv raw means
    z1 = rng.standard_normal(N); z2 = corr * z1 + math.sqrt(1 - corr ** 2) * rng.standard_normal(N)
    x3 = n3[0] + n3[1] * z1; x4 = n4[0] + n4[1] * z2
    t = rng.random(N) < tail_w; x4 = np.where(t, tail[0] + tail[1] * rng.standard_normal(N), x4)
    d = x4 - x3; state = np.where(d >= band, 0, np.where(d > -band, 1, 2))
    g = rng.random(N) < p_guide_ge
    sh = lambda m: unc + shrink * (m - unc)
    mu = np.where(state == 0, np.where(g, sh(mu_cell["aa"]), sh(mu_cell["ab"])), np.where(state == 1, sh(mu_cell["fl"]), np.where(g, sh(mu_cell["da"]), sh(mu_cell["db"]))))
    mu = mu + q4_uplift
    r = mu + resid_sd * rng.standard_t(df, N) / math.sqrt(df / (df - 2)) + qqq_sd * rng.standard_normal(N)
    return dict(p_ge5=float((r >= thr).mean()), p_lt0=float((r < 0).mean()), p_ge10=float((r >= 10).mean()), p_le_m5=float((r <= -5).mean()), p_le_m8=float((r <= -8).mean()),
                mean=float(r.mean()), sd=float(r.std()), p_accel=float((state == 0).mean()), p_flat=float((state == 1).mean()), p_decel=float((state == 2).mean()),
                p_ge5_by_state={k: float((r[state == i] >= thr).mean()) for i, k in enumerate(["accel", "flat", "decel"])},
                p_ge5_given_guide_ge=float((r[g] >= thr).mean()), p_ge5_given_guide_below=float((r[~g] >= thr).mean()),
                E_r_given_ge5=float(r[r >= thr].mean()), E_x4_given_ge5=float(x4[r >= thr].mean()), E_x4=float(x4.mean()), P_x4_ge_9_9_given_ge5=float((x4[r >= thr] >= 9.9).mean()),
                P_guide_ge_given_ge5=float(g[r >= thr].mean()),
                pct={str(q): float(np.percentile(r, q)) for q in (5, 10, 25, 50, 75, 90, 95)})
if __name__ == "__main__":
    base = run(); print(json.dumps(base, indent=1))
    sens = [("base", {}),
            ("no Q4 uplift", dict(q4_uplift=0.0)), ("Q4 uplift 5", dict(q4_uplift=5.0)), ("Q4 uplift at the full measured residual gap (+10)", dict(q4_uplift=10.0)),
            ("cell means unshrunk", dict(shrink=1.0)), ("cell means market-neutral (shrink 0)", dict(shrink=0.0)),
            ("4Q26 nights centred on the Street 9.9, no tail", dict(n4=(9.9, 1.2), tail_w=0.0)), ("4Q26 nights RNPL module 7.6", dict(n4=(7.6, 1.6))),
            ("3Q26 nights at the Street 11.1 (sd 0.85), 4Q26 9.9", dict(n3=(11.1, 0.85), n4=(9.9, 1.2), tail_w=0.0)),
            ("P(1Q27 guide >= Street) 0.50", dict(p_guide_ge=0.50)), ("P(1Q27 guide >= Street) 0.15", dict(p_guide_ge=0.15)),
            ("residual sd 7.5", dict(resid_sd=7.5)), ("residual sd 9.5", dict(resid_sd=9.5)), ("normal residual", dict(df=200)),
            ("unconditional centre -2.6 (post-2022 excess mean) instead of -1.0", dict(unc=-2.6)), ("unconditional centre +1.2 (all-print raw mean)", dict(unc=1.2)),
            ("joint bull: Street nights, guide>=Street 0.5, uplift 5", dict(n4=(9.9, 1.2), tail_w=0.0, p_guide_ge=0.5, q4_uplift=5.0)),
            ("joint bear: module nights, guide>=Street 0.15, no uplift", dict(n4=(7.6, 1.6), p_guide_ge=0.15, q4_uplift=0.0))]
    with open(HERE / "r14_sensitivity.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["case", "p_ge5", "p_lt0", "mean", "p_accel"])
        for name, kw in sens:
            r = run(**kw); wr.writerow([name, round(r["p_ge5"], 3), round(r["p_lt0"], 3), round(r["mean"], 2), round(r["p_accel"], 3)])
            print("%-62s p>=5 %.3f  p<0 %.3f  mean %+.2f  P(accel) %.3f" % (name, r["p_ge5"], r["p_lt0"], r["mean"], r["p_accel"]))
    # anchor: risk-neutral symmetric at the Feb event sd
    for sd in (8.0, 8.5, 9.0, 9.5):
        print("anchor sd %.1f: P(>=5) %.3f (mode -0.4)" % (sd, 1 - norm.cdf((5 + 0.4) / sd)))
    json.dump(base, open(HERE / "r14_summary.json", "w"), indent=1)
