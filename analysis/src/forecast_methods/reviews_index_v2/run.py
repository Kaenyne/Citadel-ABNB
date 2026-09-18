"""Orchestrator. python3 run.py --stage freeze|A|B|C|D|E|F|figures|all. Stages write into config.OUT only.
freeze: writes prereg.json, appends its sha256 and timestamp as the first line of the note's §2. Refuses to run
A/B/C/D before a freeze line exists."""
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C, data as D, index as I


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def freeze():
    C.OUT.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(C.PREREG, indent=2, sort_keys=True); (C.OUT / "prereg.json").write_text(txt)
    h = hashlib.sha256(txt.encode()).hexdigest(); stamp = time.strftime("%Y-%m-%d %H:%M %Z")
    note = C.NOTE.read_text()
    if "FROZEN" in note:
        log("already frozen; not re-freezing"); return
    line = f"**FROZEN {stamp}** — `prereg.json` sha256 `{h}`. Stages run in order below; no pass line changes after this line.\n"
    note = note.replace("*(empty until frozen and run)*", line); C.NOTE.write_text(note); log(f"frozen {h[:12]}")


def require_frozen():
    if "FROZEN" not in C.NOTE.read_text():
        sys.exit("refusing to run: pre-registration not frozen (python3 run.py --stage freeze)")


def load_all():
    mv = D.load_counted(); latest, prior = D.select_vintages(mv); my = I.market_monthly(latest, prior)
    log(f"market-months {len(my)}, markets {my.market_key.nunique()}, vintage-matched markets {my.dropna(subset=['n_vm_prior']).market_key.nunique()}")
    return my


def stage_a(my):
    import panel as P
    res, p, pc = P.run_stage_a(my)
    p.to_csv(C.OUT / "panel_country_month.csv", index=False); pc.to_csv(C.OUT / "panel_per_country_walkforward.csv", index=False)
    resA = [res]
    for sens in ["yoy_all", "yoy_mature"]:
        r, _, _ = P.run_stage_a(my, sens); resA.append(r)
    out = pd.concat(resA, ignore_index=True); out.to_csv(C.OUT / "stage_a_tests.csv", index=False)
    prim = out[out.measure == "yoy_vmatch"].set_index("test")
    passed = bool(prim.loc["A1_elasticity", "passed"] and prim.loc["A2_first_differences", "passed"] and prim.loc["A5_out_of_sample_by_country", "passed"])
    log(f"Stage A {'PASS' if passed else 'FAIL'}\n{out[['measure','test','value','p','passed','extra']].to_string(index=False)}")
    return passed


def stage_b(my):
    import stages as T
    idx = T.build_index(my); idx.to_csv(C.OUT / "index_quarterly_v2.csv", index=False)
    kpi = D.load_kpi(); res, paths = T.run_stage_b(idx, kpi)
    res.to_csv(C.OUT / "stage_b_walkforward.csv", index=False); paths.to_csv(C.OUT / "stage_b_paths.csv", index=False)
    loco = T.loco_slopes(idx.set_index("qi").yoy_vmatch, kpi.set_index("qi").nights_m_yoy_pct); loco.to_csv(C.OUT / "stage_b_loco_slopes.csv", index=False)
    log(f"Stage B B1 {'PASS' if res.attrs['B1_passed'] else 'FAIL'}\n" + res[["measure","window","subset","target","wf_n","wf_ratio_vs_naive","ratio_lo90","ratio_hi90","dm_p","mean_err","passed"]].to_string(index=False))
    return res.attrs["B1_passed"]


def stage_c(my):
    import stages as T
    idx = pd.read_csv(C.OUT / "index_quarterly_v2.csv"); kpi = D.load_kpi(); M = D.load_kernel()
    res, gaps = T.run_stage_c(idx, kpi, my, M)
    r0 = res.iloc[0]; c3 = T.stage_c3_3q26(r0.frozen_a, r0.frozen_b, r0.band_pp)
    res.to_csv(C.OUT / "stage_c_tests.csv", index=False); gaps.to_csv(C.OUT / "stage_c_gap.csv", index=False)
    (C.OUT / "stage_c3_3q26.json").write_text(json.dumps(c3, indent=2))
    log(f"Stage C C1 {'PASS' if bool(r0.passed) else 'FAIL'} — {r0.reading}\n{gaps.to_string(index=False)}\n{res.to_string(index=False)}\n3Q26: {c3}")
    return bool(r0.passed)


def stage_e():
    import view as V
    v, r = V.run_stage_e()
    log("Stage E (the view)\n" + v[["quarter", "base_m", "base_yoy", "street_m", "street_yoy", "p_print_at_or_above_street"]].to_string(index=False))


def stage_f():
    import final_model as FM
    df, meta = FM.build(); log("Stage F (final model)\n" + df[["quarter", "phase", "stays_yoy", "print_yoy", "I_pp", "street_yoy"]].round(2).to_string(index=False))


def stage_d(my):
    import did_power as DP
    rows, gap, es = DP.run_stage_d(my)
    rows.to_csv(C.OUT / "stage_d_power.csv", index=False); gap.to_csv(C.OUT / "stage_d_pretrend.csv", index=False); es.to_csv(C.OUT / "stage_d_event_study_EXPLORATORY.csv", index=False)
    log(f"Stage D\n{rows.to_string(index=False)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", default="all"); a = ap.parse_args()
    C.OUT.mkdir(parents=True, exist_ok=True); C.FIG.mkdir(parents=True, exist_ok=True)
    if a.stage == "freeze":
        freeze(); sys.exit()
    require_frozen(); my = load_all(); verdict = {}
    if a.stage in ("A", "all"): verdict["A"] = stage_a(my)
    if a.stage in ("B", "all"): verdict["B"] = stage_b(my)
    if a.stage in ("C", "all"): verdict["C"] = stage_c(my)
    if a.stage in ("D", "all"): stage_d(my)
    if a.stage in ("E", "all"): stage_e()
    if a.stage in ("F", "all"): stage_f()
    if a.stage in ("figures", "all"):
        import figures as F; F.render_all()
    (C.OUT / "RESULTS.json").write_text(json.dumps({**verdict, "ran": time.strftime("%Y-%m-%d %H:%M")}, indent=2)); log(f"verdicts {verdict}")
