"""
WS-N, memo 1: which ADR-FX estimator to name.

Reconciles two apparently conflicting rankings of the ADR-FX estimators (euro
fit vs regional-basket build vs their midpoint):
  - WS-B (research/notes/overnight2/B_fx-relative-strength-geographic-mix.md):
    on the 17 disclosed quarters 2Q22-2Q26, euro fit RMSE 0.458 pp beats
    baskets 0.535 pp.
  - WS-S (data/processed/adrv3/S/error_attribution_v3.csv): on the scored
    walk-forward window 1Q24-2Q26 (n10), baskets 0.416 pp and midpoint 0.332 pp
    both beat euro 0.455 pp.

This script recomputes both rankings from the same source file
(B_adr_fx_estimator_backtest.csv), splits the 17-quarter record into
sub-windows, and shows where each estimator wins. It does not re-collect any
data: every number here is a transform of the B backtest CSV (errors already
computed by WS-B) plus the S error-attribution CSV (read for the cross-check).
No fitting is done in this script; the two estimators and their midpoint are
exactly WS-B's.

Outputs:
  data/processed/adrv3/N/N1_fx_estimator_by_quarter.csv
  data/processed/adrv3/N/N1_fx_choice_card.csv

py -3.13, offline.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # worktree root
OVERNIGHT2_B = os.path.join(ROOT, "data", "processed", "overnight2", "B")
ADRV3_S = os.path.join(ROOT, "data", "processed", "adrv3", "S")
ADRQ3_J = os.path.join(ROOT, "data", "processed", "adrq3", "J")
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "N")
os.makedirs(OUT, exist_ok=True)


def rmse(x):
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(x ** 2)))


def main():
    b = pd.read_csv(os.path.join(OVERNIGHT2_B, "B_adr_fx_estimator_backtest.csv"))
    # quarter labels like "2022Q2" -> sortable and to H-style "2Q22"
    b["year"] = b["quarter"].str[:4].astype(int)
    b["q"] = b["quarter"].str[4:].str.replace("Q", "").astype(int)
    b["h_label"] = b["q"].astype(str) + "Q" + (b["year"] % 100).astype(str).str.zfill(2)
    b = b.sort_values(["year", "q"]).reset_index(drop=True)

    # midpoint estimator: (eur + baskets) / 2, error against disclosed
    b["est_from_midpoint"] = (b["est_from_eur"] + b["est_from_regional_baskets"]) / 2.0
    b["err_est_from_midpoint"] = b["est_from_midpoint"] - b["adr_fx_disclosed_pp"]

    # sub-window labels
    def subwin(row):
        if row["year"] == 2022:
            return "2022 dollar surge (2Q22-4Q22)"
        if row["year"] == 2023:
            return "2023 (unwind, mixed)"
        if row["year"] == 2024 and row["q"] == 1:
            return "scored window (1Q24-2Q26)"
        if (row["year"], row["q"]) >= (2024, 1):
            return "scored window (1Q24-2Q26)"
        return "other"

    b["subwindow"] = b.apply(subwin, axis=1)

    b["abs_err_eur"] = b["err_est_from_eur"].abs()
    b["abs_err_baskets"] = b["err_est_from_regional_baskets"].abs()
    b["abs_err_midpoint"] = b["err_est_from_midpoint"].abs()

    def winner(row):
        errs = {
            "eur": row["abs_err_eur"],
            "baskets": row["abs_err_baskets"],
            "midpoint": row["abs_err_midpoint"],
        }
        return min(errs, key=errs.get)

    b["winner_by_quarter"] = b.apply(winner, axis=1)

    per_q = b[[
        "h_label", "year", "q", "subwindow", "adr_fx_disclosed_pp",
        "est_from_eur", "err_est_from_eur", "abs_err_eur",
        "est_from_regional_baskets", "err_est_from_regional_baskets", "abs_err_baskets",
        "est_from_midpoint", "err_est_from_midpoint", "abs_err_midpoint",
        "winner_by_quarter",
    ]].rename(columns={"h_label": "quarter_h"})
    per_q.to_csv(os.path.join(OUT, "N1_fx_estimator_by_quarter.csv"), index=False)

    # windows to summarise
    windows = {
        "full_2Q22_2Q26_n17": b,
        "2022_dollar_surge_n3": b[b["subwindow"] == "2022 dollar surge (2Q22-4Q22)"],
        "2023_n4": b[b["subwindow"] == "2023 (unwind, mixed)"],
        "scored_1Q24_2Q26_n10": b[b["subwindow"] == "scored window (1Q24-2Q26)"],
        "scored_2Q24_2Q26_n9": b[(b["year"] > 2024) | ((b["year"] == 2024) & (b["q"] >= 2))],
    }

    rows = []
    for wname, sub in windows.items():
        if len(sub) == 0:
            continue
        n = len(sub)
        n_eur_wins = int((sub["winner_by_quarter"] == "eur").sum())
        n_baskets_wins = int((sub["winner_by_quarter"] == "baskets").sum())
        n_mid_wins = int((sub["winner_by_quarter"] == "midpoint").sum())
        rows.append({
            "window": wname,
            "n": n,
            "rmse_eur_pp": round(rmse(sub["err_est_from_eur"]), 3),
            "rmse_baskets_pp": round(rmse(sub["err_est_from_regional_baskets"]), 3),
            "rmse_midpoint_pp": round(rmse(sub["err_est_from_midpoint"]), 3),
            "bias_eur_pp": round(float(sub["err_est_from_eur"].mean()), 3),
            "bias_baskets_pp": round(float(sub["err_est_from_regional_baskets"].mean()), 3),
            "bias_midpoint_pp": round(float(sub["err_est_from_midpoint"].mean()), 3),
            "quarters_eur_wins": n_eur_wins,
            "quarters_baskets_wins": n_baskets_wins,
            "quarters_midpoint_wins": n_mid_wins,
            "best_rmse": min(
                [("eur", rmse(sub["err_est_from_eur"])),
                 ("baskets", rmse(sub["err_est_from_regional_baskets"])),
                 ("midpoint", rmse(sub["err_est_from_midpoint"]))],
                key=lambda t: t[1],
            )[0],
        })
    windows_summary = pd.DataFrame(rows)

    # cross-check against S's reported scored-window numbers (descriptive; not refit)
    s_check = pd.DataFrame([
        {"source": "S error_attribution_v3.csv, 1Q24-2Q26", "eur_rmse": 0.455, "baskets_rmse": 0.416, "midpoint_rmse": 0.332},
        {"source": "N1 recompute, scored_1Q24_2Q26_n10 (this script)",
         "eur_rmse": windows_summary.loc[windows_summary.window == "scored_1Q24_2Q26_n10", "rmse_eur_pp"].values[0],
         "baskets_rmse": windows_summary.loc[windows_summary.window == "scored_1Q24_2Q26_n10", "rmse_baskets_pp"].values[0],
         "midpoint_rmse": windows_summary.loc[windows_summary.window == "scored_1Q24_2Q26_n10", "rmse_midpoint_pp"].values[0]},
        {"source": "B note, 2Q22-2Q26 (17 quarters, B's own words)", "eur_rmse": 0.458, "baskets_rmse": 0.535, "midpoint_rmse": None},
        {"source": "N1 recompute, full_2Q22_2Q26_n17 (this script)",
         "eur_rmse": windows_summary.loc[windows_summary.window == "full_2Q22_2Q26_n17", "rmse_eur_pp"].values[0],
         "baskets_rmse": windows_summary.loc[windows_summary.window == "full_2Q22_2Q26_n17", "rmse_baskets_pp"].values[0],
         "midpoint_rmse": windows_summary.loc[windows_summary.window == "full_2Q22_2Q26_n17", "rmse_midpoint_pp"].values[0]},
    ])

    # 3Q26 / 4Q26 point card from card v2 (data/processed/adrq3/J/adr_card_v2.csv),
    # base ex-FX +3.46 pp (sourced, card v2, both quarters), FX effect per
    # estimator from B_fx_translation_schedule_refresh.csv via the same file.
    j = pd.read_csv(os.path.join(ADRQ3_J, "adr_card_v2.csv"))
    card_rows = []
    for q in ("3Q26", "4Q26"):
        qd = j[j.quarter == q].set_index("fx_estimator")
        for est in ("eur_fit", "baskets", "midpoint"):
            r = qd.loc[est]
            card_rows.append({
                "quarter": q,
                "fx_estimator": est,
                "fx_effect_pp": r["fx_effect_pp"],
                "adr_exfx_yoy_pp": r["adr_exfx_yoy_pp"],
                "adr_reported_yoy_pp": r["adr_reported_yoy_pp"],
                "adr_usd_point": r["adr_usd_point"],
                "base_adr_usd": r["base_adr_usd"],
            })
    card = pd.DataFrame(card_rows)

    # attach the scored-window and full-window RMSE for each estimator as the
    # decision inputs, plus a recommendation flag
    rmse_lookup_scored = {
        "eur_fit": windows_summary.loc[windows_summary.window == "scored_1Q24_2Q26_n10", "rmse_eur_pp"].values[0],
        "baskets": windows_summary.loc[windows_summary.window == "scored_1Q24_2Q26_n10", "rmse_baskets_pp"].values[0],
        "midpoint": windows_summary.loc[windows_summary.window == "scored_1Q24_2Q26_n10", "rmse_midpoint_pp"].values[0],
    }
    rmse_lookup_full = {
        "eur_fit": windows_summary.loc[windows_summary.window == "full_2Q22_2Q26_n17", "rmse_eur_pp"].values[0],
        "baskets": windows_summary.loc[windows_summary.window == "full_2Q22_2Q26_n17", "rmse_baskets_pp"].values[0],
        "midpoint": windows_summary.loc[windows_summary.window == "full_2Q22_2Q26_n17", "rmse_midpoint_pp"].values[0],
    }
    card["rmse_scored_window_1Q24_2Q26_pp"] = card["fx_estimator"].map(rmse_lookup_scored).round(3)
    card["rmse_full_window_2Q22_2Q26_pp"] = card["fx_estimator"].map(rmse_lookup_full).round(3)
    card["recommended"] = card["fx_estimator"] == "midpoint"

    card.to_csv(os.path.join(OUT, "N1_fx_choice_card.csv"), index=False)

    print("=== window summary (RMSE and bias, pp; wins are per-quarter min abs error) ===")
    print(windows_summary.to_string(index=False))
    print("\n=== reconciliation with B and S published numbers ===")
    print(s_check.to_string(index=False))
    print("\n=== 3Q26 / 4Q26 card ===")
    print(card.to_string(index=False))

    windows_summary.to_csv(os.path.join(OUT, "N1_fx_estimator_window_summary.csv"), index=False)
    s_check.to_csv(os.path.join(OUT, "N1_fx_estimator_reconciliation_check.csv"), index=False)


if __name__ == "__main__":
    main()
