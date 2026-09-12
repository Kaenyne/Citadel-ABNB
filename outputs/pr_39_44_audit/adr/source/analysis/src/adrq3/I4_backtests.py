"""I4. Backtests of the three mix terms with the note-08 protocol.

For each term: (1) the measured historical series against the corresponding column of
H's adr_history_components.csv (geo_mix_pp, unit_size_pp, los_mix_pp); (2) the series
against ex-FX ADR y/y itself (02b disclosed + reconstructed, usable quarters) with the
expanding walk-forward from 1Q24 (n small: every ratio is reported with its n and no
tuning is done on it).

Party size: H's unit_size_pp IS 13's global series (identity check), so the informative
tests are (a) the refreshed-dump within-vintage series (I1b, Aug 2026 dumps) against 13's
series (Jun/Jul 2026 dumps) on the overlapping quarters, and (b) 13's series against ex-FX
ADR at leads 0 and 1 quarter. Length of stay: H's los_mix_pp (14b, disclosure-based, to
4Q25) against ex-FX ADR; the calendar-run series (14c snapshots, I2b windows) has too few
points to backtest and is reported as measured but unvalidated. Geographic mix: I3's rows.

Outputs data/processed/adrq3/I/I4_backtest_scoreboard.csv, I4_party_size_series_check.csv
Run: py -3.13 analysis/src/adrq3/I4_backtests.py
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
OUT = WT / "data/processed/adrq3/I"
sys.path.insert(0, str(WT / "analysis/src/adrq3"))
from I0_protocol import score, qkey, q_from_period, QORDER  # noqa: E402


def main():
    H = pd.read_csv(WT / "data/processed/q3nowcast/H/adr_history_components.csv").set_index("quarter")
    hist = pd.read_csv(MAIN / "data/processed/adr/02b_adr_history_extended.csv")
    hist = hist[hist.usable_for_calibration & hist.adr_yoy_exfx_final.notna()].set_index("quarter")
    p13 = pd.read_csv(MAIN / "data/processed/adr/13_party_size_adr_quarterly.csv")
    p13 = p13[p13.region.eq("global")].set_index("quarter")
    rows, checks = [], []

    # ---------------- party size --------------------------------------------------------
    hq = [q for q in H.index if q in p13.index]
    d = (H.loc[hq, "unit_size_pp"] - p13.loc[hq, "size_term_pp"]).abs().max()
    checks.append(dict(check="H unit_size_pp equals 13 global size_term_pp (identity)", n=len(hq), max_abs_diff_pp=float(d)))
    qi = OUT / "I1_party_size_quarterly.csv"
    if qi.exists():
        mine = pd.read_csv(qi)
        mine = mine[mine.region.eq("global")].copy()
        mine["quarter"] = mine.q.map(q_from_period)
        mine = mine.set_index("quarter")
        ov = [q for q in mine.index if q in p13.index and np.isfinite(mine.at[q, "size_term_pp"]) and np.isfinite(p13.at[q, "size_term_pp"])]
        if len(ov) >= 4:
            a, b = mine.loc[ov, "size_term_pp"].values, p13.loc[ov, "size_term_pp"].values
            checks.append(dict(check="refreshed Aug-2026 dumps (I1b within-vintage, fixed-2019) vs 13 series (Jun/Jul-2026 dumps): size term pp",
                               n=len(ov), quarters=f"{ov[0]}..{ov[-1]}", mean_diff_pp=float(np.mean(a - b)),
                               rmse_pp=float(np.sqrt(np.mean((a - b) ** 2))), r=float(np.corrcoef(a, b)[0, 1]),
                               refreshed_mean_pp=float(a.mean()), series13_mean_pp=float(b.mean())))
            a2, b2 = mine.loc[ov, "accommodates_mean_yoy_pct"].values, p13.loc[ov, "cap_yoy_pct"].values
            checks.append(dict(check="refreshed vs 13: booked-capacity y/y pct", n=len(ov), quarters=f"{ov[0]}..{ov[-1]}",
                               mean_diff_pp=float(np.mean(a2 - b2)), rmse_pp=float(np.sqrt(np.mean((a2 - b2) ** 2))), r=float(np.corrcoef(a2, b2)[0, 1])))
    # size term vs ex-FX ADR, leads 0 and 1 (term at t+lead against ADR at t), usable quarters from 1Q21
    tq = [q for q in QORDER if q in hist.index and qkey(q) >= qkey("1Q21") and q in p13.index]
    y = [float(hist.at[q, "adr_yoy_exfx_final"]) for q in tq]
    for lead in (0, 1):
        x = []
        for q in tq:
            ql = QORDER[qkey(q) + lead]
            x.append(float(p13.at[ql, "size_term_pp"]) if ql in p13.index else np.nan)
        r = score(f"unit size term (13, global) lead {lead} vs ex-FX ADR y/y", x, y, tq, "1Q24",
                  "yes (reviews for the quarter are ~complete 14 days after quarter end)" if lead == 0 else "no")
        r["target"] = "adr_exfx_yoy_pp"; r["term"] = "unit_size"
        rows.append(r)
    # vs H residual pricing (does size explain what the decomposition leaves?)
    hq2 = [q for q in H.index if q in p13.index]
    r = score("unit size term vs H residual pricing", [float(p13.at[q, "size_term_pp"]) for q in hq2],
              [float(H.at[q, "residual_pricing_pp"]) for q in hq2], hq2, "1Q25", "yes")
    r["target"] = "residual_pricing_pp"; r["term"] = "unit_size"
    rows.append(r)

    # ---------------- length of stay ----------------------------------------------------
    los = H["los_mix_pp"].copy()
    los.loc[["1Q26", "2Q26"]] = np.nan  # assumed cells excluded
    lq = [q for q in H.index if np.isfinite(los.get(q, np.nan))]
    r = score("LOS mix term (H/14b, disclosure-based) vs ex-FX ADR y/y", [float(los[q]) for q in lq],
              [float(H.at[q, "adr_exfx_yoy_pp"]) for q in lq], lq, "1Q24",
              "no (14b's quarterly cells rest on the year's ALOS, disclosed at the print)")
    r["target"] = "adr_exfx_yoy_pp"; r["term"] = "los_mix"
    rows.append(r)
    # 14c calendar snapshots: 28+ occupancy-weighted share, global, five snapshots (descriptive only)
    c14 = pd.read_csv(MAIN / "data/processed/adr/14c_los_runs_panel.csv")
    g = c14[c14.level.eq("global") & c14.segment.eq("all")].sort_values("snapshot")
    if len(g):
        checks.append(dict(check="14c global occupancy-weighted 28+ nights share by snapshot (descriptive, n=5, not backtestable)",
                           n=len(g), values=" ".join(f"{s}:{v:.3f}" for s, v in zip(g.snapshot, g.w_share_nights_ge28))))
    lt = OUT / "I2_los_term.csv"
    if lt.exists():
        t = pd.read_csv(lt)
        gg = t[t.region.eq("global_10k_weighted")]
        checks.append(dict(check="I2b LOS mix term by year/window/weighting (global, pp)", n=len(gg),
                           values=" | ".join(f"{r.year}-{r.kind}-{r.window}-{r.weighting[:3]}:{r.los_mix_pp:+.2f}" for r in gg.itertuples())))

    # ---------------- geographic mix ------------------------------------------------------
    gb = OUT / "I3_geo_mix_backtest.csv"
    if gb.exists():
        g3 = pd.read_csv(gb)
        g3["term"] = "geo_mix"
        rows.extend(g3.to_dict("records"))

    # ---------------- the three measured terms together -----------------------------------
    hq3 = [q for q in H.index if qkey(q) >= qkey("1Q23")]
    comb = [float(H.at[q, "geo_mix_pp"] + H.at[q, "unit_size_pp"] + H.at[q, "los_mix_pp"]) for q in hq3]
    r = score("geo + size + LOS (H columns) vs ex-FX ADR y/y", comb, [float(H.at[q, "adr_exfx_yoy_pp"]) for q in hq3], hq3, "1Q25", "partial")
    r["target"] = "adr_exfx_yoy_pp"; r["term"] = "three_terms"
    rows.append(r)

    sb = pd.DataFrame(rows)
    cols = ["term", "feature", "target", "n", "r", "perm_p", "knowable_before_print", "wf_start", "wf_n", "wf_rmse", "wf_rmse_naive",
            "wf_rmse_prior", "wf_rmse_ar1", "wf_ratio_vs_naive", "wf_ratio_vs_prior", "wf_ratio_vs_ar1", "sign_acc", "rmse_vs_H_pp", "mean_diff_pp"]
    sb = sb[[c for c in cols if c in sb.columns]]
    sb.to_csv(OUT / "I4_backtest_scoreboard.csv", index=False)
    ck = pd.DataFrame(checks)
    ck.to_csv(OUT / "I4_party_size_series_check.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200)
    print(sb.round(3).to_string(index=False))
    print(ck.to_string(index=False))


if __name__ == "__main__":
    main()

