"""C4: apply the pre-registered pass line (govdata vocabulary) to the C3 scoreboard and write the
verdict row plus the live 3Q26 reading table. Copy of analysis/src/govdata/V3_rank.py narrowed to
one source; the verdict is by the *_full features only (pre-registered), lag1 and qtd75 rows are
reported and cannot upgrade it.

Build C of the GitHub alt-data integration plan, 14 Sep 2026 (compiled with Claude Code).
Outputs: data/processed/govdata_v2/C_candidates.csv, C_ranked_table.md, C_live_reading.csv.
Run: python analysis/src/govdata_v2/C4_rank.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "govdata_v2")
QTD_DAYS = 75


def main():
    bt = pd.read_csv(os.path.join(OUT, "C_backtests.csv"))
    t0 = pd.read_csv(os.path.join(OUT, "C_t0_duplicate_check.csv"))
    rows = []
    for feat in ["eu40_flt_da_full", "eu_core_flt_da_full"]:
        sub = bt[(bt.feature == feat) & (bt.target == "emea_nights_yoy_mid")].set_index("window")
        w1, w2 = sub.loc["2022Q1+"], sub.loc["2023Q1+"]
        ok_n = (w1.wf_n >= 6) and (w2.wf_n >= 6)
        beats_w1 = w1.wf_ratio_vs_naive < 1.0
        beats_w2 = w2.wf_ratio_vs_naive < 1.0
        slope_pos = (w1.ols_slope_window > 0) and (w2.ols_slope_window > 0)
        if ok_n and beats_w1 and beats_w2 and slope_pos:
            verdict, crit = "survivor", "5 test: beats naive on both windows, positive slope on both"
        elif beats_w2 and w2.wf_n >= 6 and w2.ols_slope_window > 0:
            verdict, crit = "short-window survivor", "5 test: beats naive on 2023Q1+ only" if not beats_w1 else "5 test: beats naive on both windows but the slope condition or wf_n fails on 2022Q1+"
        else:
            verdict, crit = "corroboration", "5 test: does not beat naive on 2023Q1+" if not beats_w2 else "5 test: slope or wf_n condition fails"
        dup = t0[(t0.feature == feat) & (t0.held_series == "avia_eu27_full") & (t0.overlap == "1Q23 to 4Q25")]
        dup_r = dup.r.iloc[0] if len(dup) else np.nan
        dup_label = "duplicate of avia_paoc on history, new for the live quarter" if pd.notna(dup_r) and dup_r > 0.97 else ("above the red team's 0.90 line, below the pre-registered 0.97" if pd.notna(dup_r) and dup_r > 0.90 else "not a duplicate")
        robust = bool((w2.jk_ratio_max < 1) and (w2.perm_p < 0.05) and verdict in ("survivor", "short-window survivor"))
        rows.append(dict(feature=feat, target="emea_nights_yoy_mid", verdict=verdict, first_failing_criterion=crit,
                         ratio_2022Q1=w1.wf_ratio_vs_naive, ratio_2023Q1=w2.wf_ratio_vs_naive, wf_n_2022=w1.wf_n, wf_n_2023=w2.wf_n,
                         slope_2022=w1.ols_slope_window, slope_2023=w2.ols_slope_window, perm_p_2022=w1.perm_p, perm_p_2023=w2.perm_p, r_2022=w1.r, r_2023=w2.r,
                         jk_ratio_max_2022=w1.jk_ratio_max, jk_n_below_1_2022=w1.jk_n_below_1, jk_ratio_max_2023=w2.jk_ratio_max, jk_n_below_1_2023=w2.jk_n_below_1,
                         ratio_vs_ar1_2022=w1.wf_ratio_vs_ar1, ratio_vs_ar1_2023=w2.wf_ratio_vs_ar1, robust=robust,
                         t0_r_vs_avia_eu27=dup_r, t0_label=dup_label, knowable_before_print=w2.knowable_before_print))
    cand = pd.DataFrame(rows)
    cand.to_csv(os.path.join(OUT, "C_candidates.csv"), index=False)
    print(cand.round(3).T.to_string())

    # markdown table: every feature x target x window
    cols = ["feature", "target", "window", "n", "wf_n", "wf_first_scored_q", "r", "perm_p", "ols_slope_window", "wf_ratio_vs_naive", "wf_ratio_vs_prior", "wf_ratio_vs_ar1", "sign_acc", "jk_ratio_max", "jk_n_below_1"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in bt[cols].iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append("" if pd.isna(v) else (f"{v:.3f}" if isinstance(v, float) and c not in ("n", "wf_n", "jk_n_below_1") else (f"{int(v)}" if c in ("n", "wf_n", "jk_n_below_1") and pd.notna(v) else str(v))))
        lines.append("| " + " | ".join(cells) + " |")
    with open(os.path.join(OUT, "C_ranked_table.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # live reading
    agg = pd.read_csv(os.path.join(OUT, "daio_daily_aggregates.csv"), parse_dates=["entry_date"]).set_index("entry_date").sort_index()
    panel = pd.read_csv(os.path.join(OUT, "C_feature_panel.csv")).set_index("quarter")
    live = []
    q0 = pd.Timestamp("2026-07-01")
    for tag, col in [("eu40", "eu40_flt_da"), ("eu_core", "eu_core_flt_da")]:
        s = agg[col]
        cur = s.reindex(pd.date_range(q0, periods=QTD_DAYS))
        prev = s.reindex(pd.date_range(q0 - pd.DateOffset(years=1), periods=QTD_DAYS))
        prev_dow = s.reindex(pd.date_range(q0 - pd.Timedelta(days=364), periods=QTD_DAYS))
        cur68 = cur.iloc[:-7]
        prev68 = prev.iloc[:-7]
        live.append(dict(aggregate=tag, window="3Q26 qtd75 (1 Jul to 13 Sep 2026 vs same calendar days 2025)", days=int(cur.notna().sum()),
                         flights_2026=cur.sum(), flights_2025=prev.sum(), yoy_pct=(cur.sum() / prev.sum() - 1) * 100,
                         yoy_pct_dow_aligned_364d=(cur.sum() / prev_dow.sum() - 1) * 100, yoy_pct_qtd68_drop_last_week=(cur68.sum() / prev68.sum() - 1) * 100,
                         q_1q26_full=panel.at["1Q26", f"{col}_full"], q_2q26_full=panel.at["2Q26", f"{col}_full"],
                         q_2q26_qtd75_current_vintage=panel.at["2Q26", f"{col}_qtd75"], q_2q26_qtd75_pit=panel.at["2Q26", f"{col}_qtd75pit"] if f"{col}_qtd75pit" in panel.columns else np.nan,
                         emea_nights_yoy_mid_1q26=panel.at["1Q26", "emea_nights_yoy_mid"], emea_nights_yoy_mid_2q26=panel.at["2Q26", "emea_nights_yoy_mid"],
                         total_nights_yoy_2q26=panel.at["2Q26", "total_nights_yoy"]))
        # monthly y/y inside the quarter
        for mth in [7, 8, 9]:
            c = s[(s.index.year == 2026) & (s.index.month == mth)]
            p = s[(s.index.year == 2025) & (s.index.month == mth) & (s.index.day <= c.index.day.max())] if len(c) else s.iloc[0:0]
            if len(c):
                live.append(dict(aggregate=tag, window=f"2026-{mth:02d} (days 1 to {c.index.day.max()}) vs same days 2025", days=len(c), flights_2026=c.sum(), flights_2025=p.sum(), yoy_pct=(c.sum() / p.sum() - 1) * 100))
    lv = pd.DataFrame(live)
    lv.to_csv(os.path.join(OUT, "C_live_reading.csv"), index=False)
    print("\nlive reading:\n" + lv.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
