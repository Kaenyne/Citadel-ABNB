"""
Workstream C: the 5 Nov 2026 breakeven print. Expected day-1 reaction as a function of
  (i)  printed 3Q26 nights growth (grid 8.5-12.5%), which sets the acceleration sign vs 2Q26's 10.34%;
  (ii) the 4Q26 guide, in nights-growth points vs the printed rate (guide direction) and in revenue-guide-midpoint
       vs Street terms (the axis the reaction function actually responds to);
  (iii) 3Q26 revenue at the management delivered case ($4,815m) and at the guide midpoint ($4,730m).

Specifications (from C_02):
  S1  pre-stated univariate, THE HEADLINE:  E[r] = c + b * sign(accel)     [ex_reopening n16, post2022 n14]
  S2  post-hoc M6, ILLUSTRATIVE:            E[r] = c + b1 * sign(accel) + b2 * guide_vs_street_pct
  S2 sensitivities: + b3 * revenue_surprise_pct (M8), + b4 * guide_dir_code (M7)

Audit (audit_C.md, 12 Sep) fixes applied here: S1 is the headline and S2 illustrative (6); Zacks $3,200m comparator column
beside Bloomberg $3,154m (6); the nights-to-revenue mapping is carried at two elasticities, the H-note 1.0% of revenue per
point (anchored on the management delivered case) and the team's own 0.38%/pt implied by its base case (8.9% at $3,111m vs
10.5% at $3,130m), and team-derived scenarios use the team elasticity (6, 12); unconditional rows with P(accelerate) as an
explicit input from the nowcast band (5); bootstrap columns relabelled as the sampling range of the fitted mean, with the
realised-move range (E +/- 1.28 x residual sd) beside them (5).

Anchors (BRIEF.md): 2Q26 printed nights +10.34%; Street 3Q26 nights +11.1% / revenue $4,744m (Bloomberg FA 4 Sep);
Street 4Q26 revenue $3,154m (Bloomberg FA) and $3,200m (Zacks 4 Sep); management delivered 3Q26 rev $4,815m,
4Q26 rev $3,130m at nights +10.5%; team base 3Q26 +9.9% / $4,771m, 4Q26 +8.9% / $3,111m; 3Q26 guide mid $4,730m.
Nowcast band (docs/q3nowcast/SYNTHESIS.md): 3Q26 nights +9.5 to +10.0, band 8.5 to 11.0.

Outputs (data/processed/reverse_dcf/C/): C_breakeven_grid_nights_x_guidepts.csv, C_breakeven_grid_nights_x_gvs.csv,
  C_breakeven_zero_contour.csv, C_scenarios.csv, C_unconditional.csv, C_base_rates.csv, C_prior_breakeven_critique.csv,
  C_coefficients_used.csv
Run: py -3.13 analysis/src/reverse_dcf/C_03_breakeven.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/reverse_dcf/C"
rng = np.random.default_rng(7)

# ---- anchors -------------------------------------------------------------------------------
PRINTED_2Q26 = 10.34
DEADBAND = 0.25
STREET_3Q26_NIGHTS = 11.1
STREET_3Q26_REV = 4744.0
STREET_4Q26_REV_BBG = 3154.0
STREET_4Q26_REV_ZACKS = 3200.0
STREET_4Q26_NIGHTS = 10.1
MGMT_3Q26_REV = 4815.0
MGMT_3Q26_NIGHTS = 11.5
MGMT_4Q26_REV = 3130.0
MGMT_4Q26_NIGHTS = 10.5
TEAM_3Q26_NIGHTS = 9.9
TEAM_3Q26_REV = 4771.0
TEAM_4Q26_NIGHTS = 8.9
TEAM_4Q26_REV = 3111.0
TEAM_4Q26_NIGHTS_EXNA = 8.1
GUIDE_MID_3Q26 = 4730.0
# nights-guide -> revenue-guide mappings (JUDGEMENT): revenue % per point of 4Q26 nights growth, and the anchor point
TEAM_ELASTICITY = (MGMT_4Q26_REV / TEAM_4Q26_REV - 1) / (MGMT_4Q26_NIGHTS - TEAM_4Q26_NIGHTS)   # 0.0038 per pt, implied by the team's own cases
MAPPINGS = {
    "hnote_1.0pct_per_pt": {"slope": 0.01, "anchor_n": MGMT_4Q26_NIGHTS, "anchor_rev": MGMT_4Q26_REV,
                            "note": "H-note elasticity: 1pt of nights = ~1% of revenue; anchored on management delivered 10.5% <-> $3,130m"},
    "team_0.38pct_per_pt": {"slope": TEAM_ELASTICITY, "anchor_n": TEAM_4Q26_NIGHTS, "anchor_rev": TEAM_4Q26_REV,
                            "note": "team's own elasticity implied by base (8.9% <-> $3,111m) vs delivered (10.5% <-> $3,130m); anchored on team base"},
}
# nowcast band as an explicit probability input for the unconditional rows (JUDGEMENT on the shape; the nowcast note gives no distribution)
NOWCAST_SHAPES = [("nowcast centre 9.9, sd 0.85 (band 8.5-11.0 read as ~1.3 sd)", 9.9, 0.85),
                  ("nowcast centre 9.75, sd 0.75", 9.75, 0.75),
                  ("Street centre 11.1, sd 0.85", 11.1, 0.85)]


def accel_sign(g3):
    d = g3 - PRINTED_2Q26
    return 1.0 if d > DEADBAND else (-1.0 if d < -DEADBAND else 0.0)


def rev4_from_nights(n4, mapping="hnote_1.0pct_per_pt"):
    m = MAPPINGS[mapping]
    return m["anchor_rev"] * (1 + m["slope"] * (n4 - m["anchor_n"]))


def nights_from_rev4(r4, mapping):
    m = MAPPINGS[mapping]
    return m["anchor_n"] + (r4 / m["anchor_rev"] - 1) / m["slope"]


def gvs(rev4, street=STREET_4Q26_REV_BBG):
    return 100 * (rev4 / street - 1)


def state_probs(centre, sd):
    p_acc = 1 - stats.norm.cdf(PRINTED_2Q26 + DEADBAND, centre, sd)
    p_dec = stats.norm.cdf(PRINTED_2Q26 - DEADBAND, centre, sd)
    return p_acc, 1 - p_acc - p_dec, p_dec


def main():
    panel = pd.read_csv(OUT / "C_print_panel.csv")
    uni = pd.read_csv(OUT / "C_univariate_tests.csv")
    multi = pd.read_csv(OUT / "C_multivariate_tests.csv")
    T = "ret_1d_cc_excess_pct"

    coefs = {}
    for s in ["ex_reopening", "post2022"]:
        u = uni[(uni.target == T) & (uni["sample"] == s) & (uni.features == "nights_accel_sign")].iloc[0]
        coefs[f"S1_{s}"] = {"c": u["const"], "b_sign": u["b"], "b_gvs": 0.0, "b_rev": 0.0, "b_gdir": 0.0, "n": u["n"],
                            "r2": u["r2"], "loo_r2": u["loo_r2"], "perm_p": u["perm_p_r2"], "resid_sd": u["resid_sd"],
                            "status": "pre-stated; HEADLINE", "spec": "S1: sign(printed nights acceleration)"}
        m6 = multi[(multi.target == T) & (multi["sample"] == s) & (multi.spec.str.startswith("M6"))].iloc[0]
        m7 = multi[(multi.target == T) & (multi["sample"] == s) & (multi.spec.str.startswith("M7"))].iloc[0]
        m8 = multi[(multi.target == T) & (multi["sample"] == s) & (multi.spec.str.startswith("M8"))].iloc[0]
        coefs[f"S2_{s}"] = {"c": m6["const"], "b_sign": m6["b_nights_accel_sign"], "b_gvs": m6["b_guide_vs_street_pct"],
                            "b_rev": 0.0, "b_gdir": 0.0, "n": m6["n"], "r2": m6["r2"], "loo_r2": m6["loo_r2"],
                            "perm_p": m6["perm_p_r2"], "resid_sd": m6["resid_sd"], "status": "post-hoc; ILLUSTRATIVE",
                            "spec": "S2 (M6): sign(accel) + next-Q revenue guide midpoint vs Street (%)"}
        coefs[f"S2s_{s}"] = {"c": m8["const"], "b_sign": m8["b_nights_accel_sign"], "b_gvs": m8["b_guide_vs_street_pct"],
                             "b_rev": m8["b_revenue_surprise_pct"], "b_gdir": m7["b_guide_dir_code"], "n": m8["n"],
                             "r2": m8["r2"], "loo_r2": m8["loo_r2"], "perm_p": m8["perm_p_r2"], "resid_sd": m8["resid_sd"],
                             "status": "post-hoc; sensitivity only",
                             "spec": "S2 sensitivity: M8 (adds revenue surprise) with M7's guide-direction coefficient bolted on"}
    cdf = pd.DataFrame(coefs).T.reset_index().rename(columns={"index": "spec_id"})
    cdf.to_csv(OUT / "C_coefficients_used.csv", index=False)

    def expect(spec_id, sign, g, rev_surprise=0.0, gdir=0.0):
        k = coefs[spec_id]
        return k["c"] + k["b_sign"] * sign + k["b_gvs"] * g + k["b_rev"] * rev_surprise + k["b_gdir"] * gdir

    # ---- bootstrap: sampling distribution of the FITTED MEAN (not of the realised move) ----------
    def boot_predict(sample_col, sign, g, n_boot=3000):
        d = panel[panel[sample_col]][["nights_accel_sign", "guide_vs_street_pct", T]].dropna()
        X = np.column_stack([np.ones(len(d)), d["nights_accel_sign"].values, d["guide_vs_street_pct"].values])
        y = d[T].values
        preds = []
        for _ in range(n_boot):
            idx = rng.integers(0, len(d), len(d))
            Xb, yb = X[idx], y[idx]
            if np.linalg.matrix_rank(Xb) < 3:
                continue
            b = np.linalg.pinv(Xb.T @ Xb) @ Xb.T @ yb
            preds.append(b[0] + b[1] * sign + b[2] * g)
        preds = np.array(preds)
        return np.percentile(preds, [10, 50, 90]), (preds > 0).mean()

    def boot_predict_s1(sample_col, sign, n_boot=3000):
        d = panel[panel[sample_col]][["nights_accel_sign", T]].dropna()
        v = d[d["nights_accel_sign"] == sign][T].values if sign != 0 else d[T].values
        preds = np.array([rng.choice(v, len(v)).mean() for _ in range(n_boot)])
        return np.percentile(preds, [10, 50, 90]), (preds > 0).mean()

    # ---- named scenarios ---------------------------------------------------------------------
    scen = [
        ("Team base (WS29/30)", TEAM_3Q26_NIGHTS, TEAM_3Q26_REV, TEAM_4Q26_NIGHTS, TEAM_4Q26_REV, "ANCHOR (team files)"),
        ("Team base, ex-NA lap adopted (4Q26 8.1%)", TEAM_3Q26_NIGHTS, TEAM_3Q26_REV, TEAM_4Q26_NIGHTS_EXNA, rev4_from_nights(TEAM_4Q26_NIGHTS_EXNA, "team_0.38pct_per_pt"), "ANCHOR nights; 4Q26 revenue mapped at the team elasticity"),
        ("Street (Bloomberg FA 4 Sep)", STREET_3Q26_NIGHTS, STREET_3Q26_REV, STREET_4Q26_NIGHTS, STREET_4Q26_REV_BBG, "ANCHOR"),
        ("Management delivered", MGMT_3Q26_NIGHTS, MGMT_3Q26_REV, MGMT_4Q26_NIGHTS, MGMT_4Q26_REV, "ANCHOR"),
        ("Q3 nowcast central (reviews index 9.75) with stable 4Q guide", 9.75, MGMT_3Q26_REV, 9.75, rev4_from_nights(9.75, "team_0.38pct_per_pt"), "MEASURED nights (docs/q3nowcast); revenue mapped at the team elasticity"),
        ("Flat print: 3Q26 = 2Q26 rate, 4Q26 guided stable, revenue at Street", PRINTED_2Q26, STREET_3Q26_REV, PRINTED_2Q26, STREET_4Q26_REV_BBG, "construct"),
        ("Accelerating print, 4Q26 guide at Street revenue", 11.0, MGMT_3Q26_REV, 10.1, STREET_4Q26_REV_BBG, "construct"),
        ("Accelerating print, 4Q26 guide 2% below Street", 11.0, MGMT_3Q26_REV, nights_from_rev4(STREET_4Q26_REV_BBG * 0.98, "hnote_1.0pct_per_pt"), STREET_4Q26_REV_BBG * 0.98, "construct (nights at H-note mapping)"),
        ("Decelerating print, 4Q26 guide 3% above Street", 9.9, MGMT_3Q26_REV, nights_from_rev4(STREET_4Q26_REV_BBG * 1.03, "hnote_1.0pct_per_pt"), STREET_4Q26_REV_BBG * 1.03, "construct (nights at H-note mapping)"),
        ("2Q26 replay: accel print, guide +2.6% vs Street", 11.0, MGMT_3Q26_REV, nights_from_rev4(STREET_4Q26_REV_BBG * 1.026, "hnote_1.0pct_per_pt"), STREET_4Q26_REV_BBG * 1.026, "construct (nights at H-note mapping)"),
    ]
    rows = []
    for name, g3, r3, n4, r4, src in scen:
        s = accel_sign(g3)
        gdir_pts = n4 - g3
        gdir = 1.0 if gdir_pts > DEADBAND else (-1.0 if gdir_pts < -DEADBAND else 0.0)
        g_b = gvs(r4, STREET_4Q26_REV_BBG)
        g_z = gvs(r4, STREET_4Q26_REV_ZACKS)
        rs = 100 * (r3 / STREET_3Q26_REV - 1)
        row = {"scenario": name, "source": src, "conditional_on": {1.0: "accelerating print", 0.0: "flat print", -1.0: "decelerating print"}[s],
               "nights_3q26_pct": round(g3, 2), "accel_pts_vs_2q26": round(g3 - PRINTED_2Q26, 2),
               "accel_sign": s, "revenue_3q26_musd": round(r3), "revenue_surprise_vs_street_pct": round(rs, 2),
               "nights_guide_4q26_pct": round(n4, 2), "guide_dir_pts_vs_printed": round(gdir_pts, 2), "guide_dir_code": gdir,
               "rev_guide_4q26_musd": round(r4), "guide_vs_street_bbg_pct": round(g_b, 2), "guide_vs_street_zacks_pct": round(g_z, 2),
               "guide_below_street_bbg_flag": int(g_b < 0), "guide_below_street_zacks_flag": int(g_z < 0)}
        # HEADLINE: S1
        for sid in ["S1_ex_reopening", "S1_post2022"]:
            row[f"E_{sid}_pct"] = round(expect(sid, s, 0.0), 2)
        # ILLUSTRATIVE: S2 with both comparators
        for sid in ["S2_ex_reopening", "S2_post2022"]:
            row[f"E_{sid}_bbg_pct"] = round(expect(sid, s, g_b), 2)
            row[f"E_{sid}_zacks_pct"] = round(expect(sid, s, g_z), 2)
        row["E_S2s_ex_reopening_bbg_pct"] = round(expect("S2s_ex_reopening", s, g_b, rs, gdir), 2)
        row["E_S2s_post2022_bbg_pct"] = round(expect("S2s_post2022", s, g_b, rs, gdir), 2)
        for sid, col in [("S1_ex_reopening", "sample_ex_reopening"), ("S1_post2022", "sample_post2022")]:
            pct, ppos = boot_predict_s1(col, s)
            row[f"fitted_mean_p10_{sid}_pct"], row[f"fitted_mean_p90_{sid}_pct"] = round(pct[0], 2), round(pct[2], 2)
            row[f"share_of_refits_E_positive_{sid}"] = round(ppos, 2)
            k = coefs[sid]
            row[f"realised_move_p10_{sid}_pct"] = round(expect(sid, s, 0.0) - 1.2816 * k["resid_sd"], 2)
            row[f"realised_move_p90_{sid}_pct"] = round(expect(sid, s, 0.0) + 1.2816 * k["resid_sd"], 2)
        for sid, col in [("S2_ex_reopening", "sample_ex_reopening"), ("S2_post2022", "sample_post2022")]:
            pct, ppos = boot_predict(col, s, g_b)
            row[f"fitted_mean_p10_{sid}_bbg_pct"], row[f"fitted_mean_p90_{sid}_bbg_pct"] = round(pct[0], 2), round(pct[2], 2)
            row[f"share_of_refits_E_positive_{sid}_bbg"] = round(ppos, 2)
            k = coefs[sid]
            row[f"realised_move_p10_{sid}_bbg_pct"] = round(expect(sid, s, g_b) - 1.2816 * k["resid_sd"], 2)
            row[f"realised_move_p90_{sid}_bbg_pct"] = round(expect(sid, s, g_b) + 1.2816 * k["resid_sd"], 2)
        row["resid_sd_S1_ex_reopening_pct"] = coefs["S1_ex_reopening"]["resid_sd"]
        row["resid_sd_S2_ex_reopening_pct"] = coefs["S2_ex_reopening"]["resid_sd"]
        rows.append(row)
    scen_df = pd.DataFrame(rows)

    # ---- unconditional rows: P(accelerate) as an explicit input ---------------------------------
    unc = []
    for label, centre, sd in NOWCAST_SHAPES:
        p_a, p_f, p_d = state_probs(centre, sd)
        for gname, g_b in [("team guide $3,111m vs Bbg $3,154m", gvs(TEAM_4Q26_REV)), ("team guide vs Zacks $3,200m", gvs(TEAM_4Q26_REV, STREET_4Q26_REV_ZACKS)),
                           ("guide at Street", 0.0)]:
            r = {"nowcast_shape": label, "centre": centre, "sd": sd, "p_accelerating_gt_10.59": round(p_a, 3), "p_flat": round(p_f, 3),
                 "p_decelerating_lt_10.09": round(p_d, 3), "guide_case": gname, "guide_vs_street_pct": round(g_b, 2)}
            for sid in ["S1_ex_reopening", "S1_post2022", "S2_ex_reopening", "S2_post2022"]:
                e = p_a * expect(sid, 1.0, g_b) + p_f * expect(sid, 0.0, g_b) + p_d * expect(sid, -1.0, g_b)
                r[f"E_uncond_{sid}_pct"] = round(e, 2)
            unc.append(r)
    unc_df = pd.DataFrame(unc)
    unc_df.to_csv(OUT / "C_unconditional.csv", index=False)
    # append the two nowcast-band unconditional rows to the scenarios table for the team base
    for label, centre, sd in NOWCAST_SHAPES[:2]:
        p_a, p_f, p_d = state_probs(centre, sd)
        g_b, g_z = gvs(TEAM_4Q26_REV), gvs(TEAM_4Q26_REV, STREET_4Q26_REV_ZACKS)
        row = {"scenario": f"Team base, UNCONDITIONAL over the nowcast band ({label}): P(accel) {p_a:.2f}, P(flat) {p_f:.2f}, P(decel) {p_d:.2f}",
               "source": "JUDGEMENT on the band shape; team 4Q26 guide in every state", "conditional_on": "none (mixture)",
               "nights_3q26_pct": centre, "accel_pts_vs_2q26": np.nan, "accel_sign": np.nan, "revenue_3q26_musd": round(TEAM_3Q26_REV),
               "revenue_surprise_vs_street_pct": round(100 * (TEAM_3Q26_REV / STREET_3Q26_REV - 1), 2),
               "nights_guide_4q26_pct": TEAM_4Q26_NIGHTS, "guide_dir_pts_vs_printed": np.nan, "guide_dir_code": np.nan,
               "rev_guide_4q26_musd": TEAM_4Q26_REV, "guide_vs_street_bbg_pct": round(g_b, 2), "guide_vs_street_zacks_pct": round(g_z, 2),
               "guide_below_street_bbg_flag": 1, "guide_below_street_zacks_flag": 1}
        for sid in ["S1_ex_reopening", "S1_post2022"]:
            row[f"E_{sid}_pct"] = round(p_a * expect(sid, 1.0, 0) + p_f * expect(sid, 0.0, 0) + p_d * expect(sid, -1.0, 0), 2)
        for sid in ["S2_ex_reopening", "S2_post2022"]:
            row[f"E_{sid}_bbg_pct"] = round(p_a * expect(sid, 1.0, g_b) + p_f * expect(sid, 0.0, g_b) + p_d * expect(sid, -1.0, g_b), 2)
            row[f"E_{sid}_zacks_pct"] = round(p_a * expect(sid, 1.0, g_z) + p_f * expect(sid, 0.0, g_z) + p_d * expect(sid, -1.0, g_z), 2)
        scen_df = pd.concat([scen_df, pd.DataFrame([row])], ignore_index=True)
    scen_df.to_csv(OUT / "C_scenarios.csv", index=False)

    # ---- grid 1: printed nights x guide direction in nights points -> via mapping to gvs, both elasticities ---
    grid = []
    for mapping in MAPPINGS:
        for g3 in np.arange(8.5, 12.51, 0.25):
            s = accel_sign(g3)
            for gp in [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0]:
                n4 = g3 + gp
                r4 = rev4_from_nights(n4, mapping)
                g_b = gvs(r4)
                gdir = 1.0 if gp > DEADBAND else (-1.0 if gp < -DEADBAND else 0.0)
                for rev_case, r3 in [("delivered_4815", MGMT_3Q26_REV), ("guide_mid_4730", GUIDE_MID_3Q26)]:
                    rs = 100 * (r3 / STREET_3Q26_REV - 1)
                    grid.append({"mapping": mapping, "nights_3q26_pct": round(g3, 2), "accel_sign": s, "guide_dir_pts": gp, "nights_guide_4q26_pct": round(n4, 2),
                                 "rev_guide_4q26_musd_mapped": round(r4), "guide_vs_street_bbg_pct": round(g_b, 2),
                                 "revenue_case": rev_case, "revenue_surprise_pct": round(rs, 2),
                                 "E_S1_ex_reopening_pct": round(expect("S1_ex_reopening", s, g_b), 2),
                                 "E_S1_post2022_pct": round(expect("S1_post2022", s, g_b), 2),
                                 "E_S2_ex_reopening_pct": round(expect("S2_ex_reopening", s, g_b), 2),
                                 "E_S2_post2022_pct": round(expect("S2_post2022", s, g_b), 2),
                                 "E_S2s_ex_reopening_pct": round(expect("S2s_ex_reopening", s, g_b, rs, gdir), 2),
                                 "E_S2s_post2022_pct": round(expect("S2s_post2022", s, g_b, rs, gdir), 2)})
    pd.DataFrame(grid).to_csv(OUT / "C_breakeven_grid_nights_x_guidepts.csv", index=False)

    # ---- grid 2: printed nights x guide vs Street (the axis the function responds to) --------
    grid2 = []
    for g3 in np.arange(8.5, 12.51, 0.5):
        s = accel_sign(g3)
        for g_b in np.arange(-4.0, 4.01, 1.0):
            r4 = STREET_4Q26_REV_BBG * (1 + g_b / 100)
            grid2.append({"nights_3q26_pct": round(g3, 2), "accel_sign": s, "guide_vs_street_bbg_pct": g_b,
                          "rev_guide_4q26_musd": round(r4),
                          "implied_nights_guide_hnote_pct": round(nights_from_rev4(r4, "hnote_1.0pct_per_pt"), 1),
                          "implied_nights_guide_team_pct": round(nights_from_rev4(r4, "team_0.38pct_per_pt"), 1),
                          "E_S1_ex_reopening_pct": round(expect("S1_ex_reopening", s, 0), 2),
                          "E_S1_post2022_pct": round(expect("S1_post2022", s, 0), 2),
                          "E_S2_ex_reopening_pct": round(expect("S2_ex_reopening", s, g_b), 2),
                          "E_S2_post2022_pct": round(expect("S2_post2022", s, g_b), 2)})
    pd.DataFrame(grid2).to_csv(OUT / "C_breakeven_grid_nights_x_gvs.csv", index=False)

    # ---- zero contour ------------------------------------------------------------------------
    zc = []
    for sid in ["S1_ex_reopening", "S1_post2022"]:
        k = coefs[sid]
        for s, lab in [(1.0, "accelerating (3Q26 > 10.6%)"), (0.0, "flat (10.1-10.6%)"), (-1.0, "decelerating (3Q26 < 10.1%)")]:
            zc.append({"spec": sid, "status": k["status"], "printed_3q26": lab, "accel_sign": s, "E_pct": round(k["c"] + k["b_sign"] * s, 2),
                       "breakeven_guide_vs_street_bbg_pct": np.nan, "breakeven_rev_guide_4q26_musd_vs_bbg3154": np.nan,
                       "breakeven_rev_guide_4q26_musd_vs_zacks3200": np.nan, "implied_4q26_nights_guide_hnote_1pct_per_pt": np.nan,
                       "implied_4q26_nights_guide_team_0.38pct_per_pt": np.nan,
                       "note": "S1 has no guide term: the expected reaction is the bucket mean and no guide brings it to zero"})
    for sid in ["S2_ex_reopening", "S2_post2022"]:
        k = coefs[sid]
        for s, lab in [(1.0, "accelerating (3Q26 > 10.6%)"), (0.0, "flat (10.1-10.6%)"), (-1.0, "decelerating (3Q26 < 10.1%)")]:
            g_star = -(k["c"] + k["b_sign"] * s) / k["b_gvs"]
            r4 = STREET_4Q26_REV_BBG * (1 + g_star / 100)
            zc.append({"spec": sid, "status": k["status"], "printed_3q26": lab, "accel_sign": s, "E_pct": round(k["c"] + k["b_sign"] * s, 2),
                       "breakeven_guide_vs_street_bbg_pct": round(g_star, 2),
                       "breakeven_rev_guide_4q26_musd_vs_bbg3154": round(r4),
                       "breakeven_rev_guide_4q26_musd_vs_zacks3200": round(STREET_4Q26_REV_ZACKS * (1 + g_star / 100)),
                       "implied_4q26_nights_guide_hnote_1pct_per_pt": round(nights_from_rev4(r4, "hnote_1.0pct_per_pt"), 1),
                       "implied_4q26_nights_guide_team_0.38pct_per_pt": round(nights_from_rev4(r4, "team_0.38pct_per_pt"), 1),
                       "note": "E_pct is the expectation with the guide at Street; g* is the guide-vs-Street that zeroes it"})
    pd.DataFrame(zc).to_csv(OUT / "C_breakeven_zero_contour.csv", index=False)

    # ---- base rates --------------------------------------------------------------------------
    br = []
    for s, col in [("all", "sample_all"), ("ex_reopening", "sample_ex_reopening"), ("post2022", "sample_post2022")]:
        d = panel[panel[col]]
        for t in [T, "ret_1d_cc_raw_pct", "gap_excess_pct", "intraday_excess_pct", "ret_1d_open_excess_pct", "ev_ntm_rev_multiple_change_pct", "ret_20d_cc_excess_pct"]:
            v = d[t].dropna()
            br.append({"sample": s, "target": t, "n": len(v), "mean": round(v.mean(), 2), "median": round(v.median(), 2),
                       "sd": round(v.std(), 2), "mean_abs": round(v.abs().mean(), 2), "share_positive": round((v > 0).mean(), 2),
                       "share_abs_ge_7": round((v.abs() >= 7).mean(), 2)})
    pd.DataFrame(br).to_csv(OUT / "C_base_rates.csv", index=False)

    # ---- critique of the prior breakeven file ---------------------------------------------------
    crit = []
    post = panel[panel["sample_post2022"]]
    crit.append({"item": "Median revenue beat vs consensus, post-2022", "prior_value": 1.70, "reproduced": round(post["revenue_surprise_pct"].median(), 2),
                 "implied_print_musd": round(STREET_3Q26_REV * (1 + post["revenue_surprise_pct"].median() / 100)),
                 "comment": "Reproduces (on the same 14 prints). Uses Zacks $4,740m; Bloomberg FA is $4,744m."})
    crit.append({"item": "Median revenue beat vs guide midpoint, post-2022", "prior_value": 2.15, "reproduced": round(post["rev_beat_vs_guide_mid_pct"].median(), 2),
                 "implied_print_musd": round(GUIDE_MID_3Q26 * (1 + post["rev_beat_vs_guide_mid_pct"].median() / 100)),
                 "comment": "Reproduces to rounding."})
    crit.append({"item": "Street 3Q26 nights bar", "prior_value": np.nan, "reproduced": np.nan, "implied_print_musd": np.nan,
                 "comment": "Prior file: 'NOT PUBLISHED', derived ~144-146m (+8 to +9%). Superseded: Bloomberg FA (4 Sep) has 148.9m = +11.1%. The Street bar is 2.5-3pts above the derived one, sits at the top of the team's 8.5-11.0 band and above the 2Q26 rate, so the Street already expects an accelerating 3Q26 print."})
    crit.append({"item": "Reaction content of the prior file", "prior_value": np.nan, "reproduced": np.nan, "implied_print_musd": np.nan,
                 "comment": "It is a table of consensus bars, not a reaction breakeven: it says what beats consensus, not what moves the stock. Its one reaction claim (nights beat vs StreetAccount > 1.8% -> positive 20-day drift) was later shown by WS20 not to survive an executable next-open entry (LOO R2 -0.016). The day-1 reaction to the revenue beat is zero in every sample here (b 0.4-0.7 per 1%, LOO negative), so the revenue bar carries no reaction information at all."})
    crit.append({"item": "Q4-26 revenue consensus", "prior_value": 3200.0, "reproduced": np.nan, "implied_print_musd": np.nan,
                 "comment": "Zacks $3,200m (10 est., 3,050-3,700) vs Bloomberg FA $3,154m. The 4Q26 guide vs this number is the one pre-stated feature with a day-1 coefficient on the primary sample (+1.9% per 1% above Street, n16; post-hoc M6 +2.1%). The vendor choice is a 1.5% swing in guide-vs-Street, about 3 points of S2 expected reaction, and flips the sign of the Street and management-delivered scenarios under S2. The number that matters is the one on the tape on 5 Nov, not today's."})
    pd.DataFrame(crit).to_csv(OUT / "C_prior_breakeven_critique.csv", index=False)

    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 80); pd.set_option("display.max_colwidth", 90)
    print(cdf.to_string())
    print(scen_df[["scenario", "nights_3q26_pct", "accel_sign", "nights_guide_4q26_pct", "rev_guide_4q26_musd", "guide_vs_street_bbg_pct", "guide_vs_street_zacks_pct",
                   "E_S1_ex_reopening_pct", "E_S1_post2022_pct", "E_S2_ex_reopening_bbg_pct", "E_S2_ex_reopening_zacks_pct", "E_S2_post2022_bbg_pct", "E_S2_post2022_zacks_pct",
                   "fitted_mean_p10_S1_ex_reopening_pct", "fitted_mean_p90_S1_ex_reopening_pct", "realised_move_p10_S1_ex_reopening_pct", "realised_move_p90_S1_ex_reopening_pct",
                   "fitted_mean_p10_S2_ex_reopening_bbg_pct", "fitted_mean_p90_S2_ex_reopening_bbg_pct"]].to_string())
    print(unc_df.to_string())
    print(pd.DataFrame(zc).to_string())
    print(pd.DataFrame(br).to_string())
    print("team elasticity %.4f per pt" % TEAM_ELASTICITY)


if __name__ == "__main__":
    main()
