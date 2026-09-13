#!/usr/bin/env python
"""Rebuild M2 (`margin-ts`) end to end: grid at every vintage, quantiles, registry (7 objects),
LIVE and annual tables, scoreboard rescore, figures, scoreboard extract for the note.

  cd "<worktree root>"
  py -3.13 analysis/src/margin_build/M2_margin_ts/run.py            # ~2-4 min, exit 0
  py -3.13 analysis/src/margin_build/M2_margin_ts/run.py --no-sarima   # skip object 5 (faster)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m2_margin_ts as M  # noqa: E402


def main() -> int:
    t0 = time.time()
    include_sarima = "--no-sarima" not in sys.argv
    M.OUT.mkdir(parents=True, exist_ok=True)
    targets = M.load_targets()
    n_act = int(targets["has_actual"].sum())
    print(f"== M2 margin-ts == targets: {n_act} actual quarters; vintages {len(M.VINTAGES_ALL)} "
          f"({M.VINTAGES_ALL[0]} .. {M.TODAY}); sarima={'on' if include_sarima else 'off'}")
    p = M.load_adopted_path()
    print(f"adopted revenue path: {p['source'].iloc[0]}; base 3Q26 {M.adopted('2026Q3', 'base', 'rev'):.0f}, "
          f"4Q26 {M.adopted('2026Q4', 'base', 'rev'):.0f}, 1Q27 {M.adopted('2027Q1', 'base', 'rev'):.0f}")

    print("\n[1/5] grid (all objects, specs, replays, vintages)")
    g, live = M.build_grid(targets, include_sarima=include_sarima, verbose=False)
    g = M.attach_quantiles(g)
    g.to_csv(M.OUT / f"{M.SLUG}_grid_all_vintages.csv", index=False)
    print(f"  grid rows {len(g)}; objects {sorted(g['object'].unique())}")

    print("\n[2/5] registry")
    frames = M.registry_frames(g)
    for obj, df in frames.items():
        w = sorted(df["window"].unique())
        print(f"  {obj:22s} {len(df):6d} rows, {df['target'].nunique():2d} targets, {df['spec_id'].nunique()} specs, windows {w}")
        M.register(df, quiet=True)

    print("\n[3/5] LIVE + annual tables")
    lv, ann = M.live_table(g, live, targets)
    lv.to_csv(M.OUT / f"{M.SLUG}_live_forecasts.csv", index=False)
    ann.to_csv(M.OUT / f"{M.SLUG}_annual_forecasts.csv", index=False)
    x = lv[(lv["target"] == "adj_ebitda_margin_pct") & (lv["scenario"] == "base")
           & (lv["quarter"].isin(["2026Q3", "2026Q4"]))]
    x = x[[r.spec_id == M.MAIN_SPEC.get(r.object) for r in x.itertuples()]]
    with pd.option_context("display.width", 200):
        print(x.pivot_table(index=["object", "spec_id"], columns="quarter", values="point").round(2).to_string())

    print("\n[4/5] rescore the margin registry")
    from harness_margin.score import main as score_main
    score_main(verbose=False)
    sb = pd.read_csv(M.REPO / "data/processed/margin_build/10_harness_margin/scoreboard_margin.csv")
    by_q = pd.read_csv(M.REPO / "data/processed/margin_build/10_harness_margin/scoreboard_by_quarter.csv")
    mine = sb[sb["method"] == M.METHOD].copy()
    mine.to_csv(M.OUT / f"{M.SLUG}_scoreboard_extract.csv", index=False)
    cols = ["object", "spec_id", "window", "horizon_q", "prior_basis", "n", "mae", "rw_mae", "bias",
            "mae_ratio_seasonal_naive", "rw_mae_ratio_seasonal_naive", "mae_ratio_street", "cov80",
            "survives_both_windows", "rw_survives_both_windows", "n_params"]
    m0 = mine[(mine["target"] == "adj_ebitda_margin_pct") & (mine["horizon_q"] == 0) & (mine["prior_basis"] == "PIT")]
    with pd.option_context("display.width", 250, "display.max_rows", 200):
        print(m0[cols].sort_values(["window", "mae"]).round(3).to_string(index=False))

    print("\n[5/5] figures")
    try:
        M.make_figures(sb, by_q, lv)
    except Exception as e:
        print(f"  figures skipped: {e}")
    (M.OUT / f"{M.SLUG}_run_log.txt").write_text("\n".join(M.LOG) + f"\nelapsed {time.time() - t0:.0f}s\n", encoding="utf-8")
    print(f"\nDONE in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
