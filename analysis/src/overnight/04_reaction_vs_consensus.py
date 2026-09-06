# 04_reaction_vs_consensus.py
#
# Re-runs the ABNB print-day reaction function against surprise-vs-CONSENSUS instead of
# beat-vs-GUIDE, and benchmarks it against the existing beat-vs-guide spec.
#
# READS
#   data/processed/overnight/04_consensus_at_print.csv   (built by 04_consensus_at_print.py)
#   data/processed/abnb_revenue_guidance_vs_actual.csv   (beat-vs-guide benchmark)
#   data/processed/predictive/04_print_features.csv      (nights_accel, pre_runup_20d_pct)
#   data/processed/abnb_daily_close.csv                  (price, to scale the EPS surprise)
#
# WRITES
#   data/processed/overnight/04_reaction_tests.csv
#   data/processed/overnight/04_q3_2026_breakeven.csv
#
# METHOD NOTES
# - EPS surprise in percent is unusable pre-2023 (denominators near zero produce +167%, +100%).
#   The primary EPS regressor is therefore the surprise in DOLLARS PER SHARE divided by the
#   pre-print closing price, i.e. the surprise as a percent of market cap. Percent surprise is
#   kept as a secondary regressor on the post-2022 subsample only.
# - All t-stats are HC1 (heteroskedasticity-robust). n is 18-23; nothing here survives a
#   multiple-testing correction on its own, so LOO R2 against a mean baseline is the decision rule.

import os
import itertools
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = r"C:\Users\krish\citadel-abnb-overnight"
DP = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(DP, "overnight")

RNG = np.random.default_rng(20260906)
NPERM = 5000


def loo_r2(X, y):
    """Leave-one-out R2 of an OLS fit vs the LOO mean baseline."""
    n = len(y)
    if n <= X.shape[1] + 2:
        return np.nan, np.nan, np.nan
    pred = np.empty(n)
    base = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        try:
            b = np.linalg.lstsq(X[m], y[m], rcond=None)[0]
        except np.linalg.LinAlgError:
            return np.nan, np.nan, np.nan
        pred[i] = X[i] @ b
        base[i] = y[m].mean()
    sse = float(((y - pred) ** 2).sum())
    ssb = float(((y - base) ** 2).sum())
    return 1.0 - sse / ssb, float(np.sqrt(sse / n)), float(np.sqrt(ssb / n))


def fit(df, target, feats, label, block, notes=""):
    d = df[[target] + feats].dropna()
    if len(d) < 6:
        return None
    y = d[target].to_numpy(float)
    X = sm.add_constant(d[feats].to_numpy(float), has_constant="add")
    res = sm.OLS(y, X).fit(cov_type="HC1")
    lr2, rmse, brmse = loo_r2(X, y)
    # permutation p on the full-sample R2
    r2 = res.rsquared
    cnt = 0
    for _ in range(NPERM):
        yp = RNG.permutation(y)
        cnt += (sm.OLS(yp, X).fit().rsquared >= r2)
    row = dict(block=block, spec=label, target=target, n=len(d),
               r2=round(r2, 4), adj_r2=round(res.rsquared_adj, 4),
               loo_r2=round(lr2, 4) if lr2 == lr2 else np.nan,
               loo_rmse=round(rmse, 3) if rmse == rmse else np.nan,
               naive_rmse=round(brmse, 3) if brmse == brmse else np.nan,
               perm_p_r2=round((cnt + 1) / (NPERM + 1), 4),
               const=round(res.params[0], 3), notes=notes)
    for i, f in enumerate(feats):
        row["b_" + f] = round(res.params[i + 1], 4)
        row["t_" + f] = round(res.tvalues[i + 1], 3)
        row["p_" + f] = round(res.pvalues[i + 1], 4)
    return row


def main():
    c = pd.read_csv(os.path.join(OUT, "04_consensus_at_print.csv"))

    # --- pre-print close, to scale the EPS surprise ------------------------------
    px = pd.read_csv(os.path.join(DP, "abnb_daily_close.csv"))
    pxcol = [x for x in px.columns if x.lower() in ("close", "adj_close", "abnb_close")][0]
    dcol = [x for x in px.columns if "date" in x.lower()][0]
    px[dcol] = pd.to_datetime(px[dcol])
    px = px.sort_values(dcol)

    def prev_close(dstr):
        d = pd.Timestamp(dstr)
        s = px[px[dcol] <= d]
        return float(s[pxcol].iloc[-1]) if len(s) else np.nan

    c["pre_close"] = c["print_date"].map(prev_close)
    c["eps_surprise_bps_of_px"] = np.where(
        c["eps_comparable"] == 1,
        (c["actual_eps_usd"] - c["cons_eps_usd"]) / c["pre_close"] * 10000.0, np.nan)

    # --- beat-vs-guide benchmark -------------------------------------------------
    g = pd.read_csv(os.path.join(DP, "abnb_revenue_guidance_vs_actual.csv"))
    g["print_quarter"] = g["guided_quarter"]
    c = c.merge(g[["print_quarter", "actual_vs_mid_pct"]].rename(
        columns={"actual_vs_mid_pct": "beat_vs_guide_mid_pct"}), on="print_quarter", how="left")

    # --- nights acceleration + run-up from the predictive study -------------------
    pf = pd.read_csv(os.path.join(DP, "predictive", "04_print_features.csv"))
    c = c.merge(pf[["print_quarter", "nights_accel", "pre_runup_20d_pct", "rev_yoy"]],
                on="print_quarter", how="left")
    c["nights_accel_sign"] = np.sign(c["nights_accel"])

    c["guide_below_street"] = (c["guide_vs_street_pct"] < 0).astype(float)
    c.loc[c["guide_vs_street_pct"].isna(), "guide_below_street"] = np.nan
    # 2021Q3: direction known from the Reuters headline, magnitude unknown
    c.loc[c["print_quarter"] == "2021Q3", "guide_below_street"] = 1.0

    c["post2022"] = (c["print_quarter"] >= "2023Q1")

    c.to_csv(os.path.join(OUT, "04_reaction_panel.csv"), index=False)

    rows = []
    targets = ["excess_1d_pct", "excess_5d_pct", "excess_20d_pct"]

    UNI = ["revenue_surprise_pct", "eps_surprise_bps_of_px", "eps_surprise_pct",
           "ebitda_surprise_pct", "nights_surprise_pct", "gbv_surprise_pct",
           "guide_vs_street_pct", "beat_vs_guide_mid_pct", "nights_accel",
           "pre_runup_20d_pct"]

    for t in targets:
        for f in UNI:
            r = fit(c, t, [f], "uni_" + f, "univariate")
            if r:
                rows.append(r)

    COMBOS = [
        (["revenue_surprise_pct", "guide_vs_street_pct"], "rev+guide_vs_street"),
        (["revenue_surprise_pct", "eps_surprise_bps_of_px"], "rev+eps"),
        (["revenue_surprise_pct", "nights_surprise_pct"], "rev+nights"),
        (["guide_vs_street_pct", "nights_surprise_pct"], "guide_vs_street+nights"),
        (["revenue_surprise_pct", "eps_surprise_bps_of_px", "guide_vs_street_pct"], "rev+eps+guide_vs_street"),
        (["guide_vs_street_pct", "nights_accel"], "guide_vs_street+nights_accel"),
        (["beat_vs_guide_mid_pct", "guide_vs_street_pct"], "beat_vs_guide+guide_vs_street"),
        (["revenue_surprise_pct", "guide_vs_street_pct", "pre_runup_20d_pct"], "rev+guide_vs_street+runup"),
    ]
    for t in targets:
        for feats, lab in COMBOS:
            r = fit(c, t, feats, lab, "multivariate")
            if r:
                rows.append(r)

    # post-2022 subsample (14 prints, the regime the pitch actually cares about)
    cp = c[c["post2022"]].copy()
    for t in targets:
        for f in ["revenue_surprise_pct", "eps_surprise_pct", "eps_surprise_bps_of_px",
                  "nights_surprise_pct", "guide_vs_street_pct", "beat_vs_guide_mid_pct"]:
            r = fit(cp, t, [f], "uni_" + f, "post2022")
            if r:
                rows.append(r)
        r = fit(cp, t, ["revenue_surprise_pct", "guide_vs_street_pct"], "rev+guide_vs_street", "post2022")
        if r:
            rows.append(r)

    res = pd.DataFrame(rows)

    # ---------------- sign / count tests -----------------------------------------
    sign_rows = []

    def signtest(mask, label, target="excess_1d_pct", expect_neg=True):
        d = c.loc[mask, [target]].dropna()
        if not len(d):
            return
        neg = int((d[target] < 0).sum())
        n = len(d)
        p = stats.binomtest(neg if expect_neg else n - neg, n, 0.5,
                            alternative="greater").pvalue
        # ABNB's unconditional 20-day excess return is negative 73% of the time, so a
        # binomial against 0.5 badly overstates any "all negative" run. Test against the
        # in-sample base rate as well.
        allq = c[target].dropna()
        base = float((allq < 0).mean()) if expect_neg else float((allq > 0).mean())
        pb = stats.binomtest(neg if expect_neg else n - neg, n, base,
                             alternative="greater").pvalue
        sign_rows.append(dict(test=label, target=target, n=n, n_negative=neg,
                              share_negative=round(neg / n, 3),
                              mean=round(d[target].mean(), 2),
                              median=round(d[target].median(), 2),
                              binom_p=round(p, 4),
                              base_rate=round(base, 3), binom_p_vs_base_rate=round(pb, 4)))

    for t in targets:
        signtest(c["guide_below_street"] == 1, "guide midpoint BELOW Street", t, True)
        signtest(c["guide_below_street"] == 0, "guide midpoint ABOVE Street", t, False)
        signtest(c["eps_surprise_bps_of_px"] < 0, "EPS MISS vs consensus", t, True)
        signtest(c["revenue_surprise_pct"] > 0, "revenue BEAT vs consensus", t, False)
        signtest(c["nights_surprise_pct"] < 0, "nights MISS vs consensus", t, True)
        signtest(np.sign(c["nights_accel"]) > 0, "nights acceleration positive", t, False)

    sg = pd.DataFrame(sign_rows)

    # Mann-Whitney: guide below vs above Street, day-1
    d1 = c.loc[c["guide_below_street"] == 1, "excess_1d_pct"].dropna()
    d0 = c.loc[c["guide_below_street"] == 0, "excess_1d_pct"].dropna()
    mw = stats.mannwhitneyu(d0, d1, alternative="greater")
    sg = pd.concat([sg, pd.DataFrame([dict(
        test="MannWhitney guide ABOVE vs BELOW Street", target="excess_1d_pct",
        n=len(d0) + len(d1), n_negative=np.nan, share_negative=np.nan,
        mean=round(d0.mean() - d1.mean(), 2), median=np.nan,
        binom_p=round(mw.pvalue, 4))])], ignore_index=True)

    sg["block"] = "signtest"

    # ---------------- jackknife the one spec that survives LOO -------------------
    jk = []
    for tgt, feat in [("excess_20d_pct", "nights_surprise_pct"),
                      ("excess_20d_pct", "gbv_surprise_pct"),
                      ("excess_1d_pct", "guide_vs_street_pct")]:
        d = c[[ "print_quarter", feat, tgt]].dropna()
        full = d[feat].corr(d[tgt])
        rs = []
        for i in range(len(d)):
            dd = d.drop(d.index[i])
            rs.append(dd[feat].corr(dd[tgt]))
        jk.append(dict(block="jackknife", spec="jk_" + feat, target=tgt, n=len(d),
                       r2=round(full ** 2, 4),
                       notes="pearson r=%.3f; leave-one-out r range %.3f..%.3f; "
                             "most influential drop = %s" % (
                                 full, min(rs), max(rs),
                                 d["print_quarter"].iloc[int(np.argmax(np.abs(np.array(rs) - full)))])))
    res = pd.concat([res, sg, pd.DataFrame(jk)], ignore_index=True)
    res["n_tests_in_file"] = len(res)
    res.to_csv(os.path.join(OUT, "04_reaction_tests.csv"), index=False)

    # ---------------- Q3 2026 break-even -----------------------------------------
    q3_cons_rev = 4740.0     # Zacks, 4-Sep-2026
    q3_cons_eps = 2.87
    guide_lo, guide_hi, guide_mid = 4690.0, 4770.0, 4730.0
    hist = c.dropna(subset=["revenue_surprise_pct"])
    beat_rates = {
        "all_23": (hist["revenue_surprise_pct"] > 0).mean(),
        "post2022_14": (hist[hist["post2022"]]["revenue_surprise_pct"] > 0).mean(),
    }
    med_beat_all = hist["revenue_surprise_pct"].median()
    med_beat_post = hist[hist["post2022"]]["revenue_surprise_pct"].median()
    med_vs_guide = c["beat_vs_guide_mid_pct"].dropna().median()
    med_vs_guide_post = c[c["post2022"]]["beat_vs_guide_mid_pct"].dropna().median()

    be = [
        dict(item="Street Q3-2026 revenue consensus (Zacks, 4-Sep-26)", value=q3_cons_rev, unit="musd",
             note="7 estimates, high 4,770 low 4,720; equals +15.79% y/y"),
        dict(item="Company Q3-2026 revenue guide midpoint", value=guide_mid, unit="musd",
             note="range 4,690-4,770 given 6-Aug-26"),
        dict(item="Guide midpoint minus consensus", value=round(guide_mid - q3_cons_rev, 1), unit="musd",
             note="= %.2f%%; the Street sits essentially ON the guide midpoint, unlike 6-Aug when the guide was 2.6%% above" % ((guide_mid - q3_cons_rev) / q3_cons_rev * 100)),
        dict(item="Revenue needed to beat consensus", value=q3_cons_rev, unit="musd",
             note="any print > $4,740m is a consensus beat; that is +0.21%% over the guide midpoint and 0.63%% below the guide high"),
        dict(item="Median historical revenue beat vs consensus (all 23)", value=round(med_beat_all, 2), unit="pct",
             note="implies a Q3-26 print of $%.0fm" % (q3_cons_rev * (1 + med_beat_all / 100))),
        dict(item="Median historical revenue beat vs consensus (14 post-2022)", value=round(med_beat_post, 2), unit="pct",
             note="implies a Q3-26 print of $%.0fm" % (q3_cons_rev * (1 + med_beat_post / 100))),
        dict(item="Median historical revenue beat vs guide midpoint (all)", value=round(med_vs_guide, 2), unit="pct",
             note="implies a Q3-26 print of $%.0fm" % (guide_mid * (1 + med_vs_guide / 100))),
        dict(item="Median historical revenue beat vs guide midpoint (post-2022)", value=round(med_vs_guide_post, 2), unit="pct",
             note="implies a Q3-26 print of $%.0fm" % (guide_mid * (1 + med_vs_guide_post / 100))),
        dict(item="Share of prints beating revenue consensus (all 23)", value=round(beat_rates["all_23"], 3), unit="frac",
             note="only 2022Q2 missed (-0.28%)"),
        dict(item="Share of prints beating revenue consensus (post-2022)", value=round(beat_rates["post2022_14"], 3), unit="frac", note=""),
        dict(item="Street Q3-2026 adjusted EPS consensus (Zacks)", value=q3_cons_eps, unit="usd",
             note="11 estimates, high 3.28 low 2.52, Most Accurate 2.88, Earnings ESP +0.45%"),
        dict(item="Street Q3-2026 adj EBITDA consensus", value=np.nan, unit="musd",
             note="NOT PUBLISHED anywhere retrievable. Company FY26 guide is >=35.5% adj EBITDA margin; applying 35.5% to the $4,740m revenue consensus gives ~$1,683m, and applying last year's Q3 margin (50.1%) gives ~$2,375m. Q3-2025 actual was $2,051m on 50.1% margin. A margin-neutral Q3-26 would be ~$2,374m; use $2.3-2.4bn as the working Street bar and flag it as derived, not sourced."),
        dict(item="Street Q3-2026 nights consensus", value=np.nan, unit="m",
             note="NOT PUBLISHED. StreetAccount nights consensus has run 0.3-3.7% below the actual at each of the last 8 prints; the median gap is +1.2%. Q3-2025 actual 133.6m; +9-10% y/y implies ~146-147m, so the implied Street bar is ~144-146m."),
        dict(item="Q4-2026 revenue consensus (Zacks)", value=3200.0, unit="musd",
             note="10 estimates, high 3,700 low 3,050 - a 21% high-low spread, by far the widest in the table, i.e. the Street has not converged on the post-hotel-mix Q4 seasonal"),
        dict(item="FY2026 revenue consensus", value=14100.0, unit="musd", note="Zacks (8 est). S&P Global via stockanalysis: 14,160 (43 analysts)"),
        dict(item="FY2027 revenue consensus", value=15730.0, unit="musd", note="Zacks (13 est). S&P Global: 15,760"),
        dict(item="FY2026 adj EPS consensus", value=5.23, unit="usd", note="Zacks (13 est). S&P Global: 5.28"),
        dict(item="FY2027 adj EPS consensus", value=6.02, unit="usd", note="Zacks (13 est). S&P Global: 6.14"),
    ]
    pd.DataFrame(be).to_csv(os.path.join(OUT, "04_q3_2026_breakeven.csv"), index=False)

    # ---------------- console summary --------------------------------------------
    pd.set_option("display.width", 250)
    key = res[(res.target == "excess_1d_pct") & (res.block.isin(["univariate", "multivariate"]))]
    print(key[["spec", "n", "r2", "adj_r2", "loo_r2", "perm_p_r2"]].to_string(index=False))
    print()
    print(res[(res.block == "post2022") & (res.target == "excess_1d_pct")][
        ["spec", "n", "r2", "loo_r2", "perm_p_r2"]].to_string(index=False))
    print()
    print(sg[sg.target == "excess_1d_pct"].to_string(index=False))
    print()
    print("tests written:", len(res))


if __name__ == "__main__":
    main()
