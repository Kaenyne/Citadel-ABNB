"""
Workstream C, step 5. 3Q26 and 4Q26 regional split, implied total nights, implied ADR mix.

Three forecasts are produced and kept side by side on purpose:

  index_model   the fitted within-region model from C4, diff_pp_hat[i] = mean_diff[i]
                + b * (relative_z[i,t] - mean_z[i]) with b from the bucket era. The fitted b is
                NEGATIVE, which contradicts the demand-pull hypothesis, so this column is a risk
                overlay, not a base case. Differentials are renormalised to be weight-zero-sum.
  persistence   each region carries its 2Q26 disclosed growth forward. This is the naive model
                the index has to beat, and on leave-one-out it barely does.
  comparison    the team nights baseline (3Q26 +9.9, 4Q26 +8.9) and WS10's regional cells, as
                comparison columns, never as inputs.

Weights: the 10-K FY2025 nights shares (NA 29.6, EMEA 40.3, LatAm 16.9, APAC 13.1). WS10 used
LatAm 13.6 and APAC 15.8, which the ADR decomposition audit (research/notes/2026-09-07_adr-
decomposition.md section 5) identifies as an error against the 10-K: it understates the weight of
the fastest-growing region by about a fifth. Both weightings are run.

Reads   data/processed/overnight2/C/regional_strength_quarterly.csv
        data/processed/overnight2/C/C4_regression_panel.csv
        data/processed/overnight2/C/C4_fits.csv
        data/processed/overnight2/C/regional_target_panel.csv
        C:/Users/krish/citadel-abnb/data/processed/overnight/10_regional_forecast.csv
Writes  data/processed/overnight2/C/C5_regional_split_forecast.csv
        data/processed/overnight2/C/C5_total_and_adr_mix.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

MAIN = Path(r"C:/Users/krish/citadel-abnb")
OUT = Path(__file__).resolve().parents[3] / "data/processed/overnight2/C"

REGIONS = ["na", "emea", "latam", "apac"]

# 10-K FY2025 Geographic Mix: nights share and ADR (GBV / nights), data/processed/adr/01_regional_annual.csv
SHARES_10K = {"na": 0.29644, "emea": 0.40338, "latam": 0.16886, "apac": 0.13133}
SHARES_WS10_3Q26 = {"na": 0.288, "emea": 0.397, "latam": 0.151, "apac": 0.163}
SHARES_WS10_4Q26 = {"na": 0.282, "emea": 0.399, "latam": 0.155, "apac": 0.164}
ADR_10K_2025 = {"na": 255.03, "emea": 158.89, "latam": 94.91, "apac": 118.20}

TEAM_BASELINE = {"3Q26": 9.9, "4Q26": 8.9}
TEAM_BAND = {"3Q26": (8.5, 10.3), "4Q26": (8.1, 9.9)}

DISCLOSED_2Q26 = {"na": 8.0, "emea": 8.0, "latam": 20.0, "apac": 18.0}
TOTAL_2Q26 = 10.34


def load_fit() -> tuple[float, pd.Series, pd.Series]:
    fits = pd.read_csv(OUT / "C4_fits.csv")
    row = fits[(fits["sample"] == "bucket_era_4Q24_2Q26") & (fits["predictor"] == "relative_z")].iloc[0]
    b = float(row["slope_pp_per_z"])
    p = pd.read_csv(OUT / "C4_regression_panel.csv")
    QORDER = [f"{q}Q{y}" for y in range(19, 27) for q in (1, 2, 3, 4)]
    QIX = {q: i for i, q in enumerate(QORDER)}
    p["ix"] = p["quarter"].map(QIX)
    bucket = p[p["ix"] >= QIX["4Q24"]]
    return b, bucket.groupby("region")["diff_pp"].mean(), bucket.groupby("region")["relative_z"].mean()


def zero_sum(diffs: dict[str, float], w: dict[str, float]) -> dict[str, float]:
    m = sum(w[r] * diffs[r] for r in REGIONS) / sum(w[r] for r in REGIONS)
    return {r: diffs[r] - m for r in REGIONS}


def adr_mix_pp(growth: dict[str, float], shares: dict[str, float], adr: dict[str, float]) -> float:
    """Geographic mix contribution to reported ADR y/y, in percentage points."""
    base = sum(shares[r] * adr[r] for r in REGIONS) / sum(shares.values())
    new_w = {r: shares[r] * (1.0 + growth[r] / 100.0) for r in REGIONS}
    new = sum(new_w[r] * adr[r] for r in REGIONS) / sum(new_w.values())
    return (new / base - 1.0) * 100.0


def main() -> None:
    b, mean_diff, mean_z = load_fit()
    z = pd.read_csv(OUT / "regional_strength_quarterly.csv")

    # 3Q26 reading: July and August 2026, the data actually in hand on 11 Sep 2026.
    # 4Q26 reading: carried at the 3Q26 level, since no 4Q26 macro data exists yet. The band
    # widens for 4Q26 to reflect that.
    z3 = z[z["quarter"] == "3Q26"].set_index("region")["relative_z"]
    z3_chg = z[z["quarter"] == "3Q26"].set_index("region")["relative_z_chg2q"]

    ws10 = pd.read_csv(MAIN / "data/processed/overnight/10_regional_forecast.csv")
    ws10_base = (ws10[(ws10["scenario"] == "base") & (ws10["region"].isin(REGIONS))]
                 .set_index(["period", "region"])["nights_yoy_pct"])

    rows = []
    fc: dict[str, dict[str, dict[str, float]]] = {}
    for period, zread, halfband in [("3Q26", z3, 1.5), ("4Q26", z3, 2.5)]:
        raw = {r: float(mean_diff[r] + b * (zread[r] - mean_z[r])) for r in REGIONS}
        idx_diff = zero_sum(raw, SHARES_10K)
        pers_diff = zero_sum({r: DISCLOSED_2Q26[r] - TOTAL_2Q26 for r in REGIONS}, SHARES_10K)
        total = TEAM_BASELINE[period]
        fc[period] = {
            "index_model": {r: total + idx_diff[r] for r in REGIONS},
            "persistence": {r: total + pers_diff[r] for r in REGIONS},
        }
        for r in REGIONS:
            rows.append({
                "period": period, "region": r,
                "relative_z_reading": round(float(zread[r]), 3),
                "relative_z_chg2q": round(float(z3_chg[r]), 3),
                "z_vs_own_bucket_mean": round(float(zread[r] - mean_z[r]), 3),
                "bucket_era_mean_diff_pp": round(float(mean_diff[r]), 2),
                "index_diff_pp": round(idx_diff[r], 2),
                "index_growth_pct": round(fc[period]["index_model"][r], 1),
                "index_growth_low": round(fc[period]["index_model"][r] - halfband, 1),
                "index_growth_high": round(fc[period]["index_model"][r] + halfband, 1),
                "persistence_growth_pct": round(fc[period]["persistence"][r], 1),
                "comparison_ws10_base_pct": float(ws10_base.get((period, r), np.nan)),
                "comparison_team_total_pct": total,
                "anchor_note": "total is the team baseline; only the SPLIT is this workstream's output",
            })
    split = pd.DataFrame(rows)
    split.to_csv(OUT / "C5_regional_split_forecast.csv", index=False)

    # ---- implied total from regional levels, and the ADR mix term
    trows = []
    for period in ("3Q26", "4Q26"):
        shares_ws10 = SHARES_WS10_3Q26 if period == "3Q26" else SHARES_WS10_4Q26
        ws10_cells = {r: float(ws10_base.get((period, r), np.nan)) for r in REGIONS}
        for label, g in [("index_model", fc[period]["index_model"]),
                         ("persistence", fc[period]["persistence"]),
                         ("ws10_base_cells", ws10_cells)]:
            for wlabel, w in [("10K_FY2025_shares", SHARES_10K), ("WS10_shares", shares_ws10)]:
                implied = sum(w[r] * g[r] for r in REGIONS) / sum(w.values())
                trows.append({
                    "period": period, "split": label, "weights": wlabel,
                    "implied_total_nights_yoy_pct": round(implied, 2),
                    "team_baseline_pct": TEAM_BASELINE[period],
                    "team_band": f"{TEAM_BAND[period][0]} to {TEAM_BAND[period][1]}",
                    "adr_geographic_mix_pp": round(adr_mix_pp(g, w, ADR_10K_2025), 2),
                    "adr_mix_pp_2025_actual_for_reference": -1.58,
                })
    tot = pd.DataFrame(trows)
    tot.to_csv(OUT / "C5_total_and_adr_mix.csv", index=False)

    print("=== 3Q26 / 4Q26 regional split ===")
    print(split[["period", "region", "relative_z_reading", "z_vs_own_bucket_mean", "index_diff_pp",
                 "index_growth_pct", "index_growth_low", "index_growth_high",
                 "persistence_growth_pct", "comparison_ws10_base_pct"]].to_string(index=False))
    print()
    print("=== implied total and ADR geographic mix ===")
    print(tot.to_string(index=False))
    print()
    print("b used (pp of differential per z unit, bucket era, fixed effects):", b)
    print("bucket-era mean differential by region:")
    print(mean_diff.round(2).to_string())
    print("bucket-era mean relative z by region:")
    print(mean_z.round(3).to_string())


def chart() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    m = pd.read_csv(OUT / "regional_strength_monthly.csv", parse_dates=["date"])
    m = m[m["date"] >= "2018-01-01"]
    panel = pd.read_csv(OUT / "C4_regression_panel.csv")
    fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
    labels = {"na": "North America", "emea": "EMEA", "latam": "Latin America", "apac": "Asia Pacific"}
    for r, lab in labels.items():
        s_ = m[m["region"] == r].set_index("date")["relative_z"].rolling(3).mean()
        ax[0].plot(s_.index, s_.values, label=lab, lw=1.4)
    ax[0].axhline(0, color="k", lw=0.7)
    ax[0].axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color="0.9", zorder=0)
    ax[0].set_title("Consumer relative strength by origin region, z units, 3-month mean "
                    "(region composite less global origin-weighted composite)")
    ax[0].legend(fontsize=8, ncol=4)
    ax[0].set_ylabel("z")

    QORDER = [f"{q}Q{y}" for y in range(22, 27) for q in (1, 2, 3, 4)]
    for r, lab in labels.items():
        sub = panel[panel["region"] == r].set_index("quarter")["diff_pp"].reindex(QORDER)
        ax[1].plot(range(len(QORDER)), sub.values, marker="o", ms=3, label=lab, lw=1.2)
    ax[1].axhline(0, color="k", lw=0.7)
    ax[1].set_xticks(range(len(QORDER)))
    ax[1].set_xticklabels(QORDER, rotation=90, fontsize=7)
    ax[1].set_title("Disclosed regional nights growth less total nights growth, percentage points")
    ax[1].set_ylabel("pp")
    ax[1].legend(fontsize=8, ncol=4)
    fig.tight_layout()
    fig.savefig(OUT / "C5_relative_strength_and_differential.png", dpi=130)
    print("wrote", OUT / "C5_relative_strength_and_differential.png")


if __name__ == "__main__":
    main()
    chart()
