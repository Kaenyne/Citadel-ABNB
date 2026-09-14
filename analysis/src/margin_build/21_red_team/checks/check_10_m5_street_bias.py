"""WS21 check 10: M5 (`street-bias`) -- is the Street beat distinguishable, and what drives the LIVE call?

M5 is the one method allowed to use consensus as an input, so its baseline is the raw `street` object,
not seasonal naive. For every street-bias cell at h=0 and h=1 on both targets, this check reports the
paired loss differential against the raw Street baseline on matched quarters, with a Newey-West(1) t,
a sign test and the quarters-better count; and it counts the cells tested (the multiple-comparison
denominator M5 itself reports as 144).

It also checks the two things the LIVE 3Q26 call rests on:
  - the dispersion regression that motivates `dispersion_conditioned`, on the full sample and on the
    method's own pre-registered pool (2022Q1+), so the reader can see which sample carries the p-value;
  - whether the dispersion multiplier at the LIVE vintage is inside the fitted range or clipped.

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_10_m5_street_bias.py [processed_dir]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PROC = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data/processed/margin_build"
M5 = PROC / "M5_street_bias"


def nw_se(d, lag=1):
    n = len(d); x = d - d.mean()
    v = float(x @ x) / n
    for l in range(1, lag + 1):
        if l < n:
            v += 2 * (1 - l / (lag + 1)) * float(x[l:] @ x[:-l]) / n
    return float(np.sqrt(max(v, 1e-12) / n))


def main() -> int:
    bq = pd.read_csv(PROC / "10_harness_margin" / "scoreboard_by_quarter.csv")
    sb = pd.read_csv(PROC / "10_harness_margin" / "scoreboard_margin.csv")
    m5 = sb[(sb["method"] == "street-bias") & (sb["prior_basis"] == "PIT")]
    print(f"street-bias scoreboard cells (PIT): "
          f"{m5.groupby(['object','target','spec_id','horizon_q','window']).ngroups}")
    st = bq[(bq["method"] == "baselines-margin") & (bq["object"] == "street") & (bq["prior_basis"] == "PIT")]
    stmap = {(r.target, r.window, int(r.horizon_q), r.quarter): float(r.abs_err) for r in st.itertuples()}
    b = bq[(bq["method"] == "street-bias") & (bq["prior_basis"] == "PIT")]
    rows = []
    for (obj, tgt, spec, h, win), g in b.groupby(["object", "target", "spec_id", "horizon_q", "window"]):
        g = g.sort_values("quarter")
        se = np.array([stmap.get((tgt, win, int(h), q), np.nan) for q in g["quarter"]], dtype=float)
        own = g["abs_err"].to_numpy(dtype=float)
        m = np.isfinite(se) & np.isfinite(own)
        if m.sum() < 5:
            continue
        d = own[m] - se[m]
        s = nw_se(d)
        t = d.mean() / s if s > 0 else np.nan
        rows.append(dict(object=obj, target=tgt, spec=spec, h=int(h), window=win, n=int(m.sum()),
                         mae_own=own[m].mean(), mae_street=se[m].mean(),
                         ratio=own[m].mean() / se[m].mean(), mean_d=d.mean(), t=t,
                         p=2 * (1 - stats.norm.cdf(abs(t))) if np.isfinite(t) else np.nan,
                         better=f"{int((d < 0).sum())}/{len(d)}",
                         p_sign=float(stats.binomtest(int((d < 0).sum()), len(d), 0.5, alternative="greater").pvalue)))
    o = pd.DataFrame(rows).sort_values(["target", "h", "window", "ratio"])
    key = o[(o["h"] == 0) & (o["spec"].str.contains("rw_hl4"))]
    with pd.option_context("display.width", 250, "display.max_rows", 200):
        print("\nh=0 cells, rw_hl4 family, vs the RAW STREET baseline:")
        print(key.round(4).to_string(index=False))
    sig = o[(o["p"] < 0.05) & (o["ratio"] < 1)]
    print(f"\ncells beating Street with p<0.05 (NW1, two-sided): {len(sig)} of {len(o)}")
    print(sig[["object", "target", "spec", "h", "window", "n", "ratio", "t", "p", "better"]].round(4).to_string(index=False))

    print("\n--- what the LIVE 3Q26 call rests on ---")
    sec = M5 / "M5_secondary_tests.json"
    if sec.exists():
        j = json.loads(sec.read_text(encoding="utf-8"))
        txt = json.dumps(j)
        print("dispersion-regression entries in M5_secondary_tests.json:")
        for k, v in (j.items() if isinstance(j, dict) else []):
            if "disp" in str(k).lower():
                print(f"   {k}: {v}")
    par = M5 / "M5_parameters_by_vintage.csv"
    if par.exists():
        p = pd.read_csv(par)
        c = [x for x in p.columns if "disp" in x.lower()]
        if c:
            live = p[p["vintage_date"].astype(str) == "2026-09-11"]
            print(f"\ndispersion columns {c}; LIVE rows:")
            print(live[["vintage_date", "horizon_q"] + c].drop_duplicates().round(4).to_string(index=False))
            hist = p[(p["vintage_date"].astype(str) < "2026-08-01")]
            for cc in c:
                v = pd.to_numeric(hist[cc], errors="coerce").dropna()
                if len(v):
                    print(f"   {cc}: backtest range {v.min():.4f} - {v.max():.4f} (n {len(v)}); "
                          f"LIVE {pd.to_numeric(live[cc], errors='coerce').dropna().tolist()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
