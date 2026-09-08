"""Reaction-size statistics for ABNB's >=7% close-to-close moves, by driver.

Input : data/processed/abnb_big_moves_7pct.csv
Output: data/processed/abnb_big_move_stats_by_driver.csv (+ printed summary)

Source of the underlying rows: "ABNB Move Explorer" (shared Claude artifact,
https://claude.ai/code/artifact/57e193ea-b799-47b2-a52a-bf42010fb318), which
attributes Yahoo Finance daily closes through 4 Sep 2026. Rows were transcribed
by hand on 6 Sep 2026 -- re-verify any number before it goes in the memo.

Run from repo root:  python analysis/src/big_move_reaction_stats.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "abnb_big_moves_7pct.csv"
OUT = ROOT / "data" / "processed" / "abnb_big_move_stats_by_driver.csv"


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["abs_move"] = df["abnb_move_pct"].abs()
    df["excess_vs_qqq"] = df["abnb_move_pct"] - df["qqq_pct"]
    df["excess_vs_bkng"] = df["abnb_move_pct"] - df["bkng_pct"]
    df["excess_vs_expe"] = df["abnb_move_pct"] - df["expe_pct"]
    df["year"] = pd.to_datetime(df["date"]).dt.year

    g = df.groupby("driver")
    out = pd.DataFrame(
        {
            "n": g.size(),
            "n_up": g["abnb_move_pct"].apply(lambda s: int((s > 0).sum())),
            "n_down": g["abnb_move_pct"].apply(lambda s: int((s < 0).sum())),
            "mean_abs_move": g["abs_move"].mean().round(1),
            "median_abs_move": g["abs_move"].median().round(1),
            "max_up": g["abnb_move_pct"].max(),
            "max_down": g["abnb_move_pct"].min(),
            "mean_abs_qqq_same_day": g["qqq_pct"].apply(lambda s: s.abs().mean()).round(1),
            "mean_abs_excess_vs_qqq": g["excess_vs_qqq"].apply(lambda s: s.abs().mean()).round(1),
            "mean_abs_excess_vs_bkng": g["excess_vs_bkng"].apply(lambda s: s.abs().mean()).round(1),
            "mean_abs_excess_vs_expe": g["excess_vs_expe"].apply(lambda s: s.abs().mean()).round(1),
            "n_since_2023": g["year"].apply(lambda s: int((s >= 2023).sum())),
        }
    )
    total = summarise_total(df)
    return pd.concat([out, total])


def summarise_total(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "n": [len(df)],
            "n_up": [int((df["abnb_move_pct"] > 0).sum())],
            "n_down": [int((df["abnb_move_pct"] < 0).sum())],
            "mean_abs_move": [round(df["abs_move"].mean(), 1)],
            "median_abs_move": [round(df["abs_move"].median(), 1)],
            "max_up": [df["abnb_move_pct"].max()],
            "max_down": [df["abnb_move_pct"].min()],
            "mean_abs_qqq_same_day": [round(df["qqq_pct"].abs().mean(), 1)],
            "mean_abs_excess_vs_qqq": [round(df["excess_vs_qqq"].abs().mean(), 1)],
            "mean_abs_excess_vs_bkng": [round(df["excess_vs_bkng"].abs().mean(), 1)],
            "mean_abs_excess_vs_expe": [round(df["excess_vs_expe"].abs().mean(), 1)],
            "n_since_2023": [int((df["year"] >= 2023).sum())],
        },
        index=["ALL"],
    )


def main() -> None:
    df = pd.read_csv(SRC)
    stats = summarise(df)
    stats.to_csv(OUT)
    pd.set_option("display.width", 200)
    print(stats)

    # Earnings-day detail: was it a beat, and which way did it go?
    e = df[df["driver"] == "Earnings"][["date", "abnb_move_pct", "trigger", "qqq_pct"]]
    print("\nEarnings days:\n", e.to_string(index=False))

    # Regime check: driver mix by period
    df["period"] = pd.to_datetime(df["date"]).dt.year.map(lambda y: "2020-22" if y <= 2022 else "2023+")
    print("\nDriver mix by period:\n", pd.crosstab(df["driver"], df["period"]))


if __name__ == "__main__":
    main()
