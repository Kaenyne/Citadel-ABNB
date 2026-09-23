"""los_nowcast / run.py — measure the change in the LOS mix term from 2Q26 to 3Q26 bookings (prereg section 2), the
World Cup's LOS effect (section 3) and the seats/hotel receipt (section 4).

Run from the repo root:
    PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.los_nowcast.run [--workers 3] [--pairs-only]
Reads the raw calendars and listings in the main tree (read-only); caches runs under OUT/cache (gitignored)."""
from __future__ import annotations
import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd
from . import config as C
from . import build as B
from . import runs as R
from . import worldcup as WC
from . import seats_check as SC


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def _task(kind, args):
    t0 = time.time()
    df = R.stock_runs(*args) if kind == "stock" else R.flow_runs(*args)
    return kind, args, len(df), time.time() - t0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); ap.add_argument("--pairs-only", action="store_true")
    a = ap.parse_args(argv)
    C.OUT.mkdir(parents=True, exist_ok=True)
    sp, fp = B.s_pairs(), B.f_pairs()
    sp.to_csv(C.OUT / "pairs_S.csv", index=False); fp.to_csv(C.OUT / "pairs_F.csv", index=False)
    log(f"S pairs {len(sp)}, F pairs {len(fp)}")
    if a.pairs_only:
        pd.set_option("display.width", 220); print(sp.to_string(index=False)); print(fp.to_string(index=False)); return 0

    # ---- runs (parallel, cached)
    jobs = sorted({("stock", (p.market, v)) for p in sp.itertuples() for v in (p.late, p.old)} |
                  {("flow", (p.market, v1, v2)) for p in fp.itertuples() for v1, v2 in ((p.late_v1, p.late_v2), (p.old_v1, p.old_v2))})
    todo = [j for j in jobs if not (C.CACHE / (f"stock_{j[1][0]}_{j[1][1]}.parquet" if j[0] == "stock" else f"flow_{j[1][0]}_{j[1][1]}_{j[1][2]}.parquet")).exists()]
    log(f"run jobs {len(jobs)}, to compute {len(todo)}")
    if todo:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            futs = [ex.submit(_task, k, args) for k, args in todo]
            for i, f in enumerate(as_completed(futs), 1):
                k, args, n, dt = f.result(); log(f"[{i}/{len(todo)}] {k} {' '.join(args)}: {n} runs, {dt:.0f}s")

    # ---- per-market stats
    msS = pd.DataFrame([r for p in sp.itertuples() for r in B.s_market_stats(p, R.stock_runs)])
    msF = pd.DataFrame([r for p in fp.itertuples() for r in B.f_market_stats(p, R.flow_runs)])
    for ms in (msS, msF):
        for b in C.BUCKETS:
            ms[f"share_{b}"] = ms[f"nights_{b}"] / ms[[f"nights_{x}" for x in C.BUCKETS]].sum(axis=1)
            ms[f"w_share_{b}"] = ms[f"w_nights_{b}"] / ms[[f"w_nights_{x}" for x in C.BUCKETS]].sum(axis=1)
    pd.concat([msS, msF]).to_csv(C.OUT / "market_stats.csv", index=False)

    # ---- reproduction gate: S on all markets vs I2's global lead-matched rows
    i2 = pd.read_csv(C.I2_TERM)
    i2 = i2[(i2.year == 2026) & (i2.window == "lead_matched") & (i2.region == "global_10k_weighted")].set_index(["kind", "weighting"]).los_mix_pp
    rep = []
    for q, kind in (("2Q26", "jun"), ("3Q26", "aug")):
        for pre, wt in (("w_", "occupancy_weighted"), ("", "unweighted")):
            mine = B.los_term(msS[msS.quarter.eq(q)], pre, require_all=True)["global"]
            rep.append(dict(quarter=q, weighting=wt, los_pp_here=mine, los_pp_I2=float(i2.loc[(kind, wt)]), diff=mine - float(i2.loc[(kind, wt)])))
    rep = pd.DataFrame(rep); rep.to_csv(C.OUT / "reproduction_I2.csv", index=False)
    gate = bool((rep["diff"].abs() <= 0.02).all())
    log("reproduction vs I2:\n" + rep.round(4).to_string(index=False) + f"\nGATE {'PASS' if gate else 'FAIL'}")
    if not gate:
        json.dump({"gate": "FAIL", "reproduction": rep.to_dict("records")}, open(C.OUT / "summary.json", "w"), indent=1)
        return 2

    # ---- the change, same-market panels
    pS, pF = B.panel(msS), B.panel(msF)
    use_f = len(pF) >= C.F_MIN_MARKETS
    rows = []
    for cons, ms, pan in (("S", msS, pS), ("F", msF, pF)):
        for pre, wt in (("w_", "W1"), ("", "W0")):
            l2, l3, d = B.delta(ms, pre, pan)
            t2 = B.los_term(ms[ms.quarter.eq("2Q26")], pre, pan); t3 = B.los_term(ms[ms.quarter.eq("3Q26")], pre, pan)
            row = dict(construction=cons, weighting=wt, n_markets=len(pan), los_2Q26_pp=l2, los_3Q26_pp=l3, delta_pp=d)
            for r in C.TENK_W:
                row[f"{r}_2Q26"] = t2["regions"].get(r, {}).get("los_pp", np.nan); row[f"{r}_3Q26"] = t3["regions"].get(r, {}).get("los_pp", np.nan)
                row[f"{r}_n"] = t3["regions"].get(r, {}).get("n", 0)
            rows.append(row)
    dt = pd.DataFrame(rows); dt.to_csv(C.OUT / "delta_by_construction.csv", index=False)
    get = lambda c, w: float(dt[(dt.construction == c) & (dt.weighting == w)].delta_pp.iloc[0])
    point = (get("F", "W1") + get("S", "W1")) / 2 if use_f else get("S", "W1")
    boot = B.bootstrap(msF, msS, pF, pS, use_f)
    p10, p90 = float(np.percentile(boot, 10)), float(np.percentile(boot, 90))
    cons_vals = dt.delta_pp.tolist() if use_f else dt[dt.construction == "S"].delta_pp.tolist()
    lo, hi = min(min(cons_vals), p10), max(max(cons_vals), p90)
    log("delta by construction:\n" + dt[["construction", "weighting", "n_markets", "los_2Q26_pp", "los_3Q26_pp", "delta_pp"]].round(3).to_string(index=False))
    log(f"point {point:+.3f}pp, bootstrap p10/p90 {p10:+.3f}/{p90:+.3f}, band [{lo:+.3f}, {hi:+.3f}], F used: {use_f}")

    # ---- World Cup (section 3)
    wcres, wctr, wcmw = WC.run(sp, R.stock_runs)
    wcres.to_csv(C.OUT / "worldcup_los_ddd.csv", index=False); wctr.to_csv(C.OUT / "worldcup_los_translation.csv", index=False)
    wcmw.to_csv(C.OUT / "worldcup_los_market_windows.csv", index=False)
    central = float(wctr[(wctr.nights == "covered") & (wctr.f_2Q26 == 1.0)].global_2Q26_los_pp.iloc[0])
    wc_added = abs(central) >= C.WC_MATERIAL_PP
    log("World Cup LOS DDD:\n" + wcres.round(3).to_string(index=False) + "\n" + wctr.round(4).to_string(index=False)
        + f"\ncentral global effect {central:+.4f}pp -> {'ADDED to delta' if wc_added else 'immaterial, not added'}")
    # a 2Q26 World Cup LOS boost that is gone in 3Q26 lowers the 3Q26 term relative to 2Q26
    point_final = point - central if wc_added else point

    # ---- seats receipt (section 4)
    sc = SC.run(); sc.to_csv(C.OUT / "seats_check.csv", index=False)

    res = pd.DataFrame([dict(quarter=q, los_in_core_2Q26=C.IN_CORE_LOS, delta_pp=point_final, los_forward_pp=C.IN_CORE_LOS + point_final,
                             band_lo_pp=C.IN_CORE_LOS + lo, band_hi_pp=C.IN_CORE_LOS + hi, basis=("measured change 2Q26->3Q26 (mean of F-W1 and S-W1)" if use_f else "measured change 2Q26->3Q26 (S-W1)")
                             + ("" if q == "3Q26" else "; 4Q26 carries the 3Q26 read (no 4Q26 bookings observable)"))
                        for q in ("3Q26", "4Q26")])
    res.to_csv(C.OUT / "los_nowcast_result.csv", index=False)
    summ = dict(gate="PASS", reproduction=rep.to_dict("records"), panel_S=pS, panel_F=pF, f_used=use_f, point_delta_pp=point,
                bootstrap_p10=p10, bootstrap_p90=p90, band=[lo, hi], worldcup_central_pp=central, worldcup_added=wc_added,
                final_delta_pp=point_final, los_forward_pp=C.IN_CORE_LOS + point_final)
    json.dump(summ, open(C.OUT / "summary.json", "w"), indent=1)
    log(f"DONE: forward LOS 3Q26/4Q26 = {C.IN_CORE_LOS + point_final:.3f}pp (in-core fill {C.IN_CORE_LOS}); band [{C.IN_CORE_LOS + lo:.3f}, {C.IN_CORE_LOS + hi:.3f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
