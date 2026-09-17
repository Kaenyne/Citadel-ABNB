"""R14: P(day-1 close-to-close return after the 4Q26 print >= +5%).
Mixture over (i) the 4Q26 printed nights acceleration sign vs 3Q26 (team objects: 3Q26 ~ N(9.55,1.48), 4Q26 ~ N(8.1,1.6)
with a 12% short tail N(5.5,1.5), corr 0.5; dead band 0.25pt), (ii) the 1Q27 revenue guide vs the then-Street
(F02 median +9.4% vs the gap-adjusted Street +11.0%; P(guide >= Street) 0.30), (iii) a Q4-print (February) seasonal
uplift carried at partial strength, (iv) a t5 residual with the options-implied Feb event sd. Also reports the S03
number and the options-only anchor. Seed 20260917. Run: py -3.13 docs/pitch-forecasts/questions/risk-feb-print-up-day/datasets/r14_model.py"""
import numpy as np, json, csv, pathlib
HERE = pathlib.Path(__file__).resolve().parent; N = 400_000

def run(seed=20260917, n3=(9.55,1.48), n4=(8.1,1.6), tail_w=0.12, tail=(5.5,1.5), corr=0.5, band=0.25,
        p_guide_ge=0.30, mu_cell=None, shrink=0.65, q4_uplift=3.0, resid_sd=7.5, df=5, qqq_sd=1.3, thr=5.0):
    """mu_cell: raw panel cell means (accel&above, accel&below, flat, decel&above, decel&below) from S01 s01_cells.csv:
    +7.4 (n3), -0.8 (n3), -8.7 (n1), +0.8 (n5), -7.6 (n4); shrunk toward the unconditional (-1.0) by (1-shrink).
    q4_uplift: the February/Q4-print seasonal (Q4 prints raw mean +7.9 vs all-print +1.2; guide-decel Q4 prints +7.1 vs
    non-Q4 -5.8, n 4/7) carried at 3.0 points (~40% of the n-4 spread)."""
    rng = np.random.default_rng(seed)
    if mu_cell is None: mu_cell = dict(aa=7.4, ab=-0.8, fl=-8.7, da=0.8, db=-7.6)
    z1 = rng.standard_normal(N); z2 = corr*z1 + np.sqrt(1-corr**2)*rng.standard_normal(N)
    x3 = n3[0] + n3[1]*z1
    x4 = n4[0] + n4[1]*z2
    t = rng.random(N) < tail_w
    x4 = np.where(t, tail[0] + tail[1]*rng.standard_normal(N), x4)
    d = x4 - x3
    state = np.where(d >= band, 0, np.where(d > -band, 1, 2))   # 0 accel, 1 flat, 2 decel
    g = rng.random(N) < p_guide_ge
    unc = -1.0
    def sh(m): return unc + shrink*(m-unc)
    mu = np.where(state==0, np.where(g, sh(mu_cell["aa"]), sh(mu_cell["ab"])),
         np.where(state==1, sh(mu_cell["fl"]), np.where(g, sh(mu_cell["da"]), sh(mu_cell["db"]))))
    mu = mu + q4_uplift
    r = mu + resid_sd*rng.standard_t(df, N)/np.sqrt(df/(df-2)) + qqq_sd*rng.standard_normal(N)
    out = dict(p_ge5=float((r>=thr).mean()), p_lt0=float((r<0).mean()), p_ge10=float((r>=10).mean()), p_le_m5=float((r<=-5).mean()),
               mean=float(r.mean()), sd=float(r.std()), p_accel=float((state==0).mean()), p_flat=float((state==1).mean()), p_decel=float((state==2).mean()),
               p_ge5_by_state={k: float((r[state==i]>=thr).mean()) for i,k in enumerate(["accel","flat","decel"])},
               p_ge5_given_guide_ge=float((r[g]>=thr).mean()), p_ge5_given_guide_below=float((r[~g]>=thr).mean()),
               E_r_given_ge5=float(r[r>=thr].mean()),
               pct={str(q): float(np.percentile(r,q)) for q in (5,10,25,50,75,90,95)})
    return out

if __name__ == "__main__":
    base = run(); print(json.dumps(base, indent=1))
    sens = [("base", {}),
            ("no Q4 seasonal uplift", dict(q4_uplift=0.0)), ("Q4 uplift at full n-4 spread (+7)", dict(q4_uplift=7.0)),
            ("cell means unshrunk", dict(shrink=1.0)), ("cell means market-neutral (shrink 0)", dict(shrink=0.0)),
            ("4Q26 nights centred on the Street 9.9, no tail", dict(n4=(9.9,1.2), tail_w=0.0)), ("4Q26 nights RNPL module 7.6", dict(n4=(7.6,1.6))),
            ("P(1Q27 guide >= Street) 0.50", dict(p_guide_ge=0.50)), ("P(1Q27 guide >= Street) 0.15", dict(p_guide_ge=0.15)),
            ("residual sd 8.5 (options Feb sd)", dict(resid_sd=8.5)), ("residual sd 6.5", dict(resid_sd=6.5)),
            ("normal residual", dict(df=200)),
            ("joint bull: Street nights, guide>=Street 0.5, uplift 5", dict(n4=(9.9,1.2), tail_w=0.0, p_guide_ge=0.5, q4_uplift=5.0)),
            ("joint bear: module nights, guide>=Street 0.15, no uplift", dict(n4=(7.6,1.6), p_guide_ge=0.15, q4_uplift=0.0))]
    with open(HERE/"r14_sensitivity.csv","w",newline="") as f:
        wr = csv.writer(f); wr.writerow(["case","p_ge5","p_lt0","mean","p_accel"])
        for name, kw in sens:
            r = run(**kw); wr.writerow([name, round(r["p_ge5"],3), round(r["p_lt0"],3), round(r["mean"],2), round(r["p_accel"],3)]); print("%-62s p>=5 %.3f  p<0 %.3f  mean %+.2f  P(accel) %.3f" % (name, r["p_ge5"], r["p_lt0"], r["mean"], r["p_accel"]))
    json.dump(base, open(HERE/"r14_summary.json","w"), indent=1)
    # base rates
    import pandas as pd
    rx = pd.read_csv(HERE.parents[3]/"data/processed/abnb_earnings_reactions.csv")
    q4 = rx[rx.quarter.str.endswith("Q4")]
    br = {"q4_prints": q4[["quarter","abnb_1d_pct","excess_1d_pct"]].values.tolist(), "q4_n": int(len(q4)), "q4_ge5": int((q4.abnb_1d_pct>=5).sum()), "q4_pos": int((q4.abnb_1d_pct>0).sum()),
          "all_n": int(len(rx)), "all_ge5": int((rx.abnb_1d_pct>=5).sum()), "post2022_n": int((rx.quarter>="2023Q1").sum()), "post2022_ge5": int(((rx.quarter>="2023Q1")&(rx.abnb_1d_pct>=5)).sum()),
          "ex_reopening_n": int((rx.quarter>="2022Q3").sum()), "ex_reopening_ge5": int(((rx.quarter>="2022Q3")&(rx.abnb_1d_pct>=5)).sum()),
          "q4_after_down_q3": "3Q22 -13.4 -> 4Q22 +13.4; 3Q23 -3.3 -> 4Q23 -1.7; 3Q24 -8.7 -> 4Q24 +14.4; 3Q25 +0.3 -> 4Q25 +4.6; 3Q21 +13.0 -> 4Q21 +3.6"}
    json.dump(br, open(HERE/"r14_base_rates.json","w"), indent=1); print(json.dumps(br, indent=1))
