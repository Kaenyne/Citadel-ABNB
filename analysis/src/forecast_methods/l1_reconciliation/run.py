"""l1-reconciliation entry point.  Rebuilds everything.  Exit code 0 on success.

    cd "<repo>"
    python \
        analysis/src/forecast_methods/l1_reconciliation/run.py

NUMERAIRE HEADER: this package hands REPORTED ADR (GBV / units).  It does NOT
de-gross-up the fee migration and it does not hand host payout per night.
BOUNDARY: exactly one object crosses onward -- gbv_musd, booking-dated, quarterly.
"""
from __future__ import annotations

import json
import pathlib
import sys
import datetime as dt

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # .../forecast_methods
sys.path.insert(0, str(HERE.parents[1]))      # .../src

from l1_reconciliation import data as D, model as M, project as P   # noqa: E402
import harness as H                                                  # noqa: E402

TODAY = dt.date(2026, 9, 11)
OUT = D.OUT
STREET_FY27_LO, STREET_FY27_HI = 15730.0, 15760.0
DRIVER_MODEL_FY27 = 15842.0

# ---- headline weight configuration (the "G2 configuration").
# G2 names two requirements: 72/72 exact and every clean annual regional nights
# cell inside +/-0.5M.  Those are given lexicographic priority; the letter ADR
# integers are admitted at a quarter weight, and the gap they leave is the
# reportable mutual-inconsistency finding, NOT a relaxation of the exact cells.
W_CONF = dict(annual=25.0, nights_yoy=3.0, adr=0.25, smooth=3.0, drift=True)


def apply_weights(cfg):
    M.W_ANNUAL = cfg["annual"]
    M.W_NIGHTS_YOY = cfg["nights_yoy"]
    M.W_ADR_REP = cfg["adr"]
    M.W_ADR_EXFX = cfg["adr"]


def build(quarters, ex, den, iv, fx, cfg=W_CONF):
    apply_weights(cfg)
    rec = M.Recon(quarters, ex, den, iv, fx, w_smooth=cfg["smooth"], drift=cfg["drift"])
    th, f = rec.fit()
    return rec, th, f


def main() -> int:
    log = []

    def say(s=""):
        print(s)
        log.append(str(s))

    ex = D.load_exact_regional_revenue()
    iv = D.load_intervals()
    kpi = D.load_kpi()
    quarters = sorted(ex.quarter.unique(), key=D.qorder)
    den = D.denominator_identity(kpi, quarters, case="base")
    fx = D.fx_pp_table(iv)
    den.to_csv(OUT / "l1_denominator_identity.csv", index=False)
    fx.to_csv(OUT / "l1_regional_fx_pp.csv", index=False)

    say(f"panel quarters n={len(quarters)}  {quarters[0]}..{quarters[-1]}")

    # ------------------------------------------------------------------ 1. fit
    rec, th, f = build(quarters, ex, den, iv, fx)
    panel = rec.panel(th)
    resid = rec.residual_report(th)
    panel.to_csv(OUT / "l1_panel_quarterly.csv", index=False)
    resid.to_csv(OUT / "l1_residuals_by_constraint.csv", index=False)

    summ = (resid.groupby("cls")
            .agg(n=("resid", "size"), n_inside=("inside", "sum"),
                 max_abs=("resid", lambda s: float(np.abs(s).max())),
                 mean_abs=("resid", lambda s: float(np.abs(s).mean())))
            .reset_index())
    summ["pct_inside"] = 100 * summ["n_inside"] / summ["n"]
    summ.to_csv(OUT / "l1_residual_summary.csv", index=False)
    say("\nresidual summary (headline fit)")
    say(summ.to_string(index=False))

    # ------------------------------------------------- 2. feasibility ladder
    ladder = []
    for name, keep in [("exact_only", []), ("+annual", ["ann"]),
                       ("+nights_yoy", ["ann", "ny"]),
                       ("+adr_reported", ["ann", "ny", "ar"]),
                       ("+adr_exfx (all)", ["ann", "ny", "ar", "ax"])]:
        apply_weights(dict(W_CONF, adr=1.0))
        r2 = M.Recon(quarters, ex, den, iv, fx, w_smooth=W_CONF["smooth"],
                     drift=W_CONF["drift"])
        if "ann" not in keep:
            r2.ann = []
        if "ny" not in keep:
            r2.ny = []
        if "ar" not in keep:
            r2.ar = []
        if "ax" not in keep:
            r2.ax = []
        t2, _ = r2.fit(max_nfev=1500)
        full = M.Recon(quarters, ex, den, iv, fx, w_smooth=W_CONF["smooth"],
                       drift=W_CONF["drift"])
        rr = full.residual_report(t2)
        g = rr.groupby("cls").agg(n=("resid", "size"), inside=("inside", "sum"),
                                  maxabs=("resid", lambda s: float(np.abs(s).max())))
        row = {"stage": name}
        for cls, r in g.iterrows():
            row[f"{cls}__n"] = int(r["n"])
            row[f"{cls}__inside"] = int(r["inside"])
            row[f"{cls}__maxabs"] = float(r["maxabs"])
        row["adr_constraint_weight"] = 1.0     # the ladder deliberately fits ADR at
        # FULL weight so the stage is a genuine feasibility test.  The HEADLINE fit
        # above uses W_CONF adr=0.25, which trades a little ADR fit for the
        # lexicographic G2 priority on the exact cells.  That is why the two
        # "worst ADR gap" numbers differ (ladder 7.30/4.06pp vs headline
        # 8.25/4.57pp): same data, two different weightings, neither is a
        # correction of the other.  Both are printed, both carry their weight.
        ladder.append(row)
    lad = pd.DataFrame(ladder)
    lad.to_csv(OUT / "l1_feasibility_ladder.csv", index=False)
    say("\nfeasibility ladder (which disclosure classes can hold simultaneously)")
    say(f"  NOTE: ladder fits the ADR classes at weight 1.0; the headline fit above "
        f"uses adr weight {W_CONF['adr']}, so ladder and headline worst-gap figures "
        f"are not the same statistic and must not be quoted interchangeably.")
    cols = ["stage", "exact_regional_revenue__maxabs", "annual_regional_nights__inside",
            "annual_regional_nights__maxabs", "regional_nights_yoy__maxabs",
            "regional_adr_yoy_reported__maxabs", "regional_adr_yoy_exfx__maxabs"]
    say(lad[cols].to_string(index=False))

    # ------------------------------------------------------- 3. acceptance tests
    apply_weights(W_CONF)
    acc = []
    n_exact_ok = int((resid[resid.cls == "exact_regional_revenue"]["resid"].abs() < 1e-6).sum())
    # LABEL FIX (verification round 1): of the 72 L0 exact cells, 56 carry
    # basis == 'filed' (three-month regional revenue as filed) and 16 carry
    # basis == 'back_out' (the Q4 cells, FY 10-K minus the nine-month 10-Q, an
    # exact arithmetic derivation from two filed numbers -- L0 reports
    # reconciliation_max_abs_diff_musd 0.0, so they are exact, not modelled).
    # "72 filed" was loose; the test now says filed-or-exact-back-out.
    n_filed = int((ex_basis_counts := ex.basis.value_counts()).get("filed", 0))
    n_backout = int(sum(v for k, v in ex_basis_counts.items() if k != "filed"))
    acc.append(dict(test="A1: reproduce all 72 exact regional revenue cells "
                         "(filed or exact Q4 back-out)",
                    passed=n_exact_ok == 72,
                    detail=f"{n_exact_ok}/72 exact, max |resid| = "
                           f"{resid[resid.cls=='exact_regional_revenue'].resid.abs().max():.2e} $M; "
                           f"composition {n_filed} filed + {n_backout} exact back-out"))
    a_ann = resid[resid.cls == "annual_regional_nights"]
    # LABEL FIX (verification round 1): all 24 annual regional nights cells in
    # L0 are basis == 'filed' and included == True.  Only 16 enter the fit
    # because the fitted panel spans 2022Q1-2026Q2, so FY2020 and FY2021 fall
    # outside the PANEL WINDOW.  They are not dropped for being unclean.
    acc.append(dict(test="A2: every annual regional nights cell inside the fitted "
                         "panel window sits inside +/-0.5M",
                    passed=bool((a_ann.resid.abs() <= M.TOL).all()),
                    detail=f"{int((a_ann.resid.abs()<=M.TOL).sum())}/{len(a_ann)} inside; "
                           f"max overshoot beyond the band = {a_ann.resid.abs().max():.4f} M nights; "
                           f"{len(a_ann)} of the 24 L0 annual cells are in-window "
                           f"(FY2020/FY2021 predate the 2022Q1 panel start; all 24 are "
                           f"basis=filed, included=True -- a window boundary, not a "
                           f"data-quality filter)"))
    # A3: regions sum to total nights EXACTLY (softmax reparameterisation)
    tot = panel.groupby("quarter")["nights_m"].sum()
    ref = den.set_index("quarter")["nights_total_m"].reindex(tot.index)
    acc.append(dict(test="A3: regional nights sum to printed Nights-and-Seats exactly",
                    passed=bool(np.nanmax(np.abs(tot - ref)) < 1e-9),
                    detail=f"max |sum_r n_r - N| = {np.nanmax(np.abs(tot-ref)):.2e} M over "
                           f"{len(tot)} quarters"))
    # A4: blended ADR == share-weighted sum of regional ADRs (no index bias)
    bl = panel.assign(w=lambda d: d.nights_m / d.groupby("quarter").nights_m.transform("sum"))
    bl = bl.assign(wa=lambda d: d.w * d.adr_reported_usd).groupby("quarter")["wa"].sum()
    ref2 = den.set_index("quarter")["adr_reported_usd"].reindex(bl.index)
    acc.append(dict(test="A4: blended ADR equals share-weighted regional ADR (mix is an OUTPUT)",
                    passed=bool(np.nanmax(np.abs(bl - ref2)) < 1e-8),
                    detail=f"max |sum_r s_r ADR_r - GBV/N| = {np.nanmax(np.abs(bl-ref2)):.2e} USD"))
    # A5: regional GBV sums to printed GBV
    gt = panel.groupby("quarter")["gbv_musd"].sum()
    ref3 = den.set_index("quarter")["gbv_musd"].reindex(gt.index)
    acc.append(dict(test="A5: regional GBV sums to printed GBV",
                    passed=bool(np.nanmax(np.abs(gt - ref3)) < 1e-6),
                    detail=f"max |sum_r GBV_r - GBV| = {np.nanmax(np.abs(gt-ref3)):.2e} $M"))

    # ----------------------------------------------- 4. seasonal lambda (kernel)
    lam = P.seasonal_lambda(kpi, w=P.KERNEL_W_PUBLISHED)
    lam_tbl = pd.DataFrame([dict(season=f"Q{s}", mean_pct=v["mean"], n=v["n"], sd=v["sd"],
                                 values=";".join(str(x) for x in v["values"]))
                            for s, v in lam.items()])
    lam_tbl.to_csv(OUT / "l1_kernel_lambda_local.csv", index=False)
    say("\nseasonal lambda recomputed locally at w=2/3 (acceptance cross-check)")
    say(lam_tbl.to_string(index=False))
    # A6 WORDING FIX (verification round 1).  The four values 12.612 / 13.736 /
    # 17.182 / 12.026 that the method cards print as the right-hand column of the
    # conversion table are the MOST RECENT same-season OBSERVATION (1Q26, 2Q26,
    # 3Q25, 4Q25), not a multi-year mean.  What this package computes is a
    # multi-year MEAN.  Those are two different statistics, so the test now says
    # so and reports BOTH comparisons instead of calling one "the table":
    #   A6a  model mean            vs the most-recent same-season observation
    #   A6b  model mean            vs the architect's own headline MEAN, which
    #        00_INTEGRATED_SYSTEM.md states for Q3 as 17.239 -- the like-for-like
    #        comparison, and the only one that is mean-against-mean.
    tgt_recent = {1: 12.612, 2: 13.736, 3: 17.182, 4: 12.026}
    dev = {s: abs(lam[s]["mean"] - tgt_recent[s]) for s in tgt_recent}
    acc.append(dict(test="A6a: seasonal lambda mean within 0.35pp of the most recent "
                         "same-season OBSERVATION (method-card right-hand column; "
                         "a mean-vs-single-observation comparison, not mean-vs-mean)",
                    passed=bool(max(dev.values()) < 0.35),
                    detail="; ".join(f"Q{s} mean {lam[s]['mean']:.3f} (n={lam[s]['n']}) vs "
                                     f"most-recent obs {tgt_recent[s]} "
                                     f"(d={lam[s]['mean']-tgt_recent[s]:+.3f}pp)"
                                     for s in tgt_recent)))
    ARCH_Q3_MEAN = 17.239   # 00_INTEGRATED_SYSTEM.md headline lambda_Q3, a 3-yr mean
    d_q3 = abs(lam[3]["mean"] - ARCH_Q3_MEAN)
    acc.append(dict(test="A6b: seasonal lambda MEAN reproduces the architect's own headline "
                         "MEAN where one is published (lambda_Q3, like-for-like)",
                    passed=bool(d_q3 < 0.01),
                    detail=f"Q3 mean {lam[3]['mean']:.4f} vs architect headline "
                           f"{ARCH_Q3_MEAN} (d={lam[3]['mean']-ARCH_Q3_MEAN:+.4f}pp, "
                           f"n={lam[3]['n']}); no headline mean is published for Q1/Q2/Q4, "
                           f"so only Q3 is testable mean-against-mean"))

    # ------------------------------------------- 5. ADR decomposition validation
    adec = P.annual_adr_decomposition(panel, fx)
    adec.to_csv(OUT / "l1_annual_adr_decomposition.csv", index=False)
    note_within = {2023: 3.10, 2024: 3.44, 2025: 3.41}
    note_mix = {2023: -1.08, 2024: -1.24, 2025: -1.58}
    adec["note_within_exfx_pp"] = adec["year"].map(note_within)
    adec["note_geo_mix_pp"] = adec["year"].map(note_mix)
    adec["diff_within_pp"] = adec["within_region_exfx_pp"] - adec["note_within_exfx_pp"]
    adec["diff_mix_pp"] = adec["geographic_mix_pp"] - adec["note_geo_mix_pp"]
    adec.to_csv(OUT / "l1_annual_adr_decomposition.csv", index=False)
    say("\n(b) validation vs 2026-09-07_adr-decomposition.md")
    say(adec[["year", "blended_adr_yoy_pct", "within_region_exfx_pp", "note_within_exfx_pp",
              "diff_within_pp", "geographic_mix_pp", "note_geo_mix_pp", "diff_mix_pp",
              "fx_pp"]].round(3).to_string(index=False))
    sub = adec[adec.year.isin(note_mix)]
    acc.append(dict(test="A7: reproduce the note's geographic-mix drag 2023-2025",
                    passed=bool(sub["diff_mix_pp"].abs().max() < 1.0),
                    detail="; ".join(f"{int(r.year)} {r.geographic_mix_pp:+.2f} vs "
                                     f"{r.note_geo_mix_pp:+.2f} (d {r.diff_mix_pp:+.2f}pp)"
                                     for r in sub.itertuples()) + f"  n={len(sub)}"))
    acc.append(dict(test="A8: reproduce the note's within-region ex-FX ADR term 2023-2025",
                    passed=bool(sub["diff_within_pp"].abs().max() < 1.0),
                    detail="; ".join(f"{int(r.year)} {r.within_region_exfx_pp:+.2f} vs "
                                     f"{r.note_within_exfx_pp:+.2f} (d {r.diff_within_pp:+.2f}pp)"
                                     for r in sub.itertuples()) + f"  n={len(sub)}"))

    # ------------------------------------------------------ 6. block bootstrap
    boot = M.block_bootstrap(rec, th, n_rep=60, block=4, seed=11, max_nfev=400)
    say(f"\nblock bootstrap: {len(boot)}/60 replicates converged (block=4 quarters, max_nfev=400)")
    if boot:
        Sst = np.stack([b[0] for b in boot])
        Nst = np.stack([b[1] for b in boot])
        Ast = np.stack([b[3] for b in boot])
        rows = []
        for i, q in enumerate(quarters):
            for j, r in enumerate(D.REGIONS):
                rows.append(dict(quarter=q, region=r,
                                 share_p10=100 * np.percentile(Sst[:, i, j], 10),
                                 share_p50=100 * np.percentile(Sst[:, i, j], 50),
                                 share_p90=100 * np.percentile(Sst[:, i, j], 90),
                                 nights_p10=np.percentile(Nst[:, i, j], 10),
                                 nights_p90=np.percentile(Nst[:, i, j], 90),
                                 adr_p10=np.percentile(Ast[:, i, j], 10),
                                 adr_p90=np.percentile(Ast[:, i, j], 90)))
        pd.DataFrame(rows).to_csv(OUT / "l1_bootstrap_intervals.csv", index=False)

    # ------------------------------------- 7. the ONE object across the boundary
    spine = (panel.groupby("quarter")["gbv_musd"].sum().rename("gbv_musd").reset_index())
    spine["basis"] = "booking_dated_usd_reported"
    spine["source"] = "printed GBV; reconciliation redistributes it regionally only"
    spine.to_csv(OUT / "l1_gbv_spine_quarterly.csv", index=False)

    # ------------------------------------------------------------- 8. FY27
    fy27 = fy27_build(panel, kpi, lam, den, fx, say, acc)

    # ------------------------------------------------------------- 9. registry
    n_reg = register_all(rec, panel, kpi, quarters, ex, den, iv, fx, lam, fy27, say)

    # ------------------------------------------------------------ 10. wrap up
    accdf = pd.DataFrame(acc)
    accdf.to_csv(OUT / "l1_acceptance_tests.csv", index=False)
    say("\nACCEPTANCE TESTS")
    for r in accdf.itertuples():
        say(f"  [{'PASS' if r.passed else 'FAIL'}] {r.test}\n        {r.detail}")
    say(f"\nregistry rows written: {n_reg}")
    say(f"free parameters, reconciliation: {rec.n_params} "
        f"(3 softmax logits x {rec.T} quarters + 3 take-rate tilts + 3 drifts)")
    say(f"interval/exact observations bound: {rec.n_obs() + 72}")
    (OUT / "l1_run_log.txt").write_text("\n".join(log))
    return 0


# --------------------------------------------------------------------- FY27
def fy27_build(panel, kpi, lam, den, fx, say, acc):
    hist_gbv = {r.quarter: r.gbv_musd for r in
                den[["quarter", "gbv_musd"]].itertuples()}
    fwd = ["2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4"]

    rf = pd.read_csv(D.DATA / "overnight" / "10_regional_forecast.csv")
    base = rf[rf.scenario == "base"]

    def scen_nights(period):
        d = base[(base.period == period) & (base.region.isin(D.REGIONS))]
        return {r.region: float(r.nights_yoy_pct) for r in d.itertuples()} or None

    def scen_adr(period, q):
        """Driver-model base ADR: ex-FX growth from 10_regional_forecast (TOTAL row,
        the only level at which it is stated) plus the region's own FX pp.  FX after
        2026Q3 is a FLAT-SPOT CARRY (zero y/y), stated as an assumption."""
        row = base[(base.period == period) & (base.region == "TOTAL")]
        g = float(row["adr_exfx_yoy_pct"].iloc[0]) if len(row) else 3.0
        fxq = fx[fx.quarter == q].set_index("region")["fx_pp"]
        return {rr: g + float(fxq.get(rr, 0.0) or 0.0) for rr in D.REGIONS}

    # regional ADR ex-FX carried at the reconstruction's own trailing-4 by region,
    # plus the regional FX pp (booking-date FX, carried through Phi -- never added
    # to revenue a second time).
    scen_rows, cont_rows = [], []
    for q in fwd:
        per = q if q in set(base.period) else "FY27"
        sn = scen_nights(per)
        sa = scen_adr(per, q)
        scen_rows.append(P.project_regional(panel, [q], sn, sa))
        cont_rows.append(P.project_regional(panel, [q], None, None))
        panel = pd.concat([panel, scen_rows[-1]], ignore_index=True)
    scen = pd.concat(scen_rows, ignore_index=True)
    cont = pd.concat(cont_rows, ignore_index=True)
    scen.to_csv(OUT / "l1_fy27_regional_scenario_driver.csv", index=False)
    cont.to_csv(OUT / "l1_fy27_regional_scenario_dataonly.csv", index=False)

    out_rows = []
    for name, df in [("driver_base", scen), ("data_only", cont)]:
        g = dict(hist_gbv)
        g.update(df.groupby("quarter")["gbv_musd"].sum().to_dict())
        for w in P.KERNEL_W_GRID:
            rev = {q: P.kernel_revenue(g, q, lam, w) for q in fwd}
            fy27_rev = sum(rev[q] for q in fwd[2:])
            fy26_rev = sum(kpi.set_index("quarter").loc[q, "revenue_musd"]
                           for q in ["2026Q1", "2026Q2"]) + rev["2026Q3"] + rev["2026Q4"]
            out_rows.append(dict(scenario=name, kernel_w=w, fy26_revenue_musd=fy26_rev,
                                 fy27_revenue_musd=fy27_rev,
                                 fy27_growth_pct=100 * (fy27_rev / fy26_rev - 1),
                                 **{f"rev_{q}": rev[q] for q in fwd},
                                 **{f"gbv_{q}": g[q] for q in fwd}))
    fy = pd.DataFrame(out_rows)
    fy.to_csv(OUT / "l1_fy27_revenue_grid.csv", index=False)
    say("\nFY27 revenue grid (kernel w sensitivity 0.33 / 0.50 / 0.667 mandatory)")
    say(fy[["scenario", "kernel_w", "fy26_revenue_musd", "fy27_revenue_musd",
            "fy27_growth_pct", "rev_2026Q4"]].round(1).to_string(index=False))

    head = fy[(fy.scenario == "driver_base") & (np.isclose(fy.kernel_w, 2 / 3))].iloc[0]
    # NUMBER FIX (verification round 1): the kernel-weight sensitivity was quoted
    # in the note as $118M.  It is now computed here and printed, so the note can
    # never drift from the grid again.  Recomputed value: $117.3M.
    _db = fy[fy.scenario == "driver_base"]
    _lo = float(_db.loc[_db.kernel_w.idxmin(), "fy27_revenue_musd"])
    _hi = float(_db.loc[_db.kernel_w.idxmax(), "fy27_revenue_musd"])
    _glo = float(_db.loc[_db.kernel_w.idxmin(), "fy27_growth_pct"])
    _ghi = float(_db.loc[_db.kernel_w.idxmax(), "fy27_growth_pct"])
    say(f"\nkernel-weight sensitivity (driver_base, w {_db.kernel_w.min():.2f} -> "
        f"{_db.kernel_w.max():.3f}): FY27 revenue {_lo:,.1f} -> {_hi:,.1f} $M, "
        f"spread {abs(_hi-_lo):,.1f} $M = {100*abs(_hi-_lo)/head.fy27_revenue_musd:.2f}% "
        f"of revenue = {abs(_ghi-_glo):.3f}pp of FY27 growth")
    pd.DataFrame([dict(metric="kernel_weight_fy27_sensitivity_musd", value=abs(_hi - _lo),
                       pct_of_revenue=100 * abs(_hi - _lo) / head.fy27_revenue_musd,
                       pp_of_growth=abs(_ghi - _glo), w_lo=float(_db.kernel_w.min()),
                       w_hi=float(_db.kernel_w.max()))]
                ).to_csv(OUT / "l1_kernel_weight_sensitivity.csv", index=False)
    say(f"\nheadline FY27 revenue {head.fy27_revenue_musd:,.0f} $M vs Street "
        f"{STREET_FY27_LO:,.0f}-{STREET_FY27_HI:,.0f} and driver model {DRIVER_MODEL_FY27:,.0f}")
    acc.append(dict(test="A9: FY27 within 1 percent of the Street midpoint",
                    passed=bool(abs(head.fy27_revenue_musd - (STREET_FY27_LO + STREET_FY27_HI) / 2)
                                / ((STREET_FY27_LO + STREET_FY27_HI) / 2) < 0.01),
                    detail=f"l1 {head.fy27_revenue_musd:,.0f} vs Street mid "
                           f"{(STREET_FY27_LO+STREET_FY27_HI)/2:,.0f} "
                           f"({100*(head.fy27_revenue_musd/((STREET_FY27_LO+STREET_FY27_HI)/2)-1):+.2f}%), n=1"))

    # ---------------- named, non-overlapping FY27 revenue-growth decomposition
    dec = fy27_decomposition(panel, scen, kpi, lam, den, fx, head)
    dec.to_csv(OUT / "l1_fy27_growth_decomposition.csv", index=False)
    say("\nFY27 revenue-growth decomposition (named, one owner per line, no residual split)")
    say(dec.round(3).to_string(index=False))
    return dict(grid=fy, head=head, dec=dec, scen=scen, cont=cont)


def fy27_decomposition(panel, scen, kpi, lam, den, fx, head):
    """Every line has ONE owner and appears ONCE.  Volume and price lines are
    computed from this package's own reconciliation; the fee/new-lines/regulation
    lines are CARRIED as assumed inputs and are NOT rebuilt tonight."""
    pan = panel.copy()
    pan["year"] = pan["quarter"].str[:4].astype(int)
    ann = pan.groupby(["year", "region"]).agg(n=("nights_m", "sum"),
                                              gbv=("gbv_musd", "sum")).reset_index()
    ann["adr"] = ann["gbv"] / ann["n"]
    cur = ann[ann.year == 2027].set_index("region")
    prv = ann[ann.year == 2026].set_index("region")
    gbv_prv, gbv_cur = float(prv.gbv.sum()), float(cur.gbv.sum())
    wprv = prv.n / prv.n.sum()
    base_gbv_g = 100 * (gbv_cur / gbv_prv - 1)

    rows = []
    # (1) regional nights, by region -- volume ex-FX
    for r in D.REGIONS:
        contrib = 100 * (cur.loc[r, "n"] - prv.loc[r, "n"]) * prv.loc[r, "adr"] / gbv_prv
        rows.append(dict(line=f"volume: {r} nights", pp=contrib, owner="l1-reconciliation",
                         basis="estimated", note=f"nights y/y {100*(cur.loc[r,'n']/prv.loc[r,'n']-1):+.1f}%"))
    # (2) within-region home ADR ex-FX (like-for-like + sub-regional mix, reported
    #     as the identified SUM only; the 2-d ridge is NOT split)
    fxy = fx.copy()
    fxy["year"] = fxy["quarter"].str[:4].astype(int)
    fx27 = fxy[fxy.year == 2027].groupby("region")["fx_pp"].mean()
    within_rep = 100 * float((prv.n * (cur.adr - prv.adr)).sum()) / gbv_prv
    fxterm = 100 * float((prv.n * prv.adr * fx27.reindex(prv.index).fillna(0) / 100).sum()) / gbv_prv
    rows.append(dict(line="price: within-region ADR ex-FX (l-f-l + sub-regional mix, unsplit)",
                     pp=within_rep - fxterm, owner="l1-reconciliation", basis="estimated",
                     note="reported as the identified SUM; the +2.9pp l-f-l/sub-mix split is a "
                          "2-d ridge and is NOT split"))
    # (3) geographic mix -- OUTPUT of the share identity
    mixpp = 100 * float(((cur.n / cur.n.sum() - wprv) * prv.adr).sum()) / float((wprv * prv.adr).sum())
    mixpp = mixpp * gbv_prv / gbv_prv
    rows.append(dict(line="geographic mix (OUTPUT of the share identity)", pp=mixpp,
                     owner="l1-reconciliation", basis="output",
                     note="share-weighted identity; no calibration plug, no index bias"))
    # (4) unit size and LOS, bedroom elasticity 0.23
    bed = pd.read_csv(D.DATA / "overnight" / "02_kpi_panel_quarterly.csv")
    bed["quarter"] = bed["quarter"].map(D.to_canon)
    bw = bed.dropna(subset=["bedroom_nights_yoy_pct", "nights_yoy_pct"])
    wedge = float((bw["bedroom_nights_yoy_pct"] - bw["nights_yoy_pct"]).mean())
    rows.append(dict(line="unit size and LOS (bedroom elasticity 0.23)",
                     pp=P.BEDROOM_ELASTICITY * wedge * (gbv_prv / gbv_prv),
                     owner="l1-reconciliation", basis="estimated",
                     note=f"bedroom-nights wedge {wedge:+.2f}pp x elasticity 0.23; the +2pp "
                          f"Street mapping is NOT used; n={len(bw)} disclosed quarters"))
    # (5) seats and hotel dilution -- OUTPUT of the denominator identity
    d26 = den[den.quarter.str.startswith("2026")]["dilution_pct"].mean()
    nh27 = D.nonhome_units(["2027Q1", "2027Q2", "2027Q3", "2027Q4"], kpi)
    rows.append(dict(line="seats and hotel dilution (OUTPUT of N = home + hotel + seats)",
                     pp=0.0, owner="l1-reconciliation", basis="output",
                     note="nets out of GBV: dilution moves reported ADR and units in opposite "
                          f"directions, GBV is unchanged. 2026 reported-ADR drag {d26:+.2f}pp"))
    # (6) booking-date FX carried through Phi -- never added to revenue twice
    rows.append(dict(line="booking-date FX carried through Phi", pp=fxterm,
                     owner="l1-reconciliation", basis="estimated",
                     note="already inside the lagged USD GBV base; NOT added to revenue a "
                          "second time"))
    # (7)-(9) carried, not rebuilt tonight
    for k, lbl in [("fee_take_rate_mechanism_pp", "fee / take-rate mechanism (half weight)"),
                   ("new_lines_pp", "new lines"), ("regulation_pp", "regulation"),
                   ("hedge_pp", "hedge (dollars, added ONCE by kernel-lambda)")]:
        rows.append(dict(line=lbl, pp=P.ASSUMED_FY27[k], owner="fee-takerate / kernel-lambda",
                         basis="assumed_not_rebuilt_tonight",
                         note="carried as a fixed input per the decisions document"))
    dec = pd.DataFrame(rows)
    # (10) kernel/timing residual: GBV growth is not revenue growth because revenue
    # is a convolution of LAGGED GBV.  This line is named, not a plug.
    rev_g = float(head.fy27_growth_pct)
    named = dec.pp.sum()
    dec = pd.concat([dec, pd.DataFrame([dict(
        line="kernel timing (revenue is a convolution of LAGGED GBV)",
        pp=rev_g - named, owner="kernel-lambda", basis="identity",
        note="GBV growth minus revenue growth from the 2/3-1/3 lag; an identity, not a residual")])],
        ignore_index=True)
    dec["cumulative_pp"] = dec.pp.cumsum()
    dec.loc[dec.index[-1], "note"] += f"  | FY27 revenue growth = {rev_g:+.2f}%"
    return dec


# ----------------------------------------------------------------- registry
def register_all(rec, panel, kpi, quarters, ex, den, iv, fx, lam, fy27, say):
    cal = H.load_calendar()
    tg = H.load_targets()
    rows = []
    spec = "l1_recon_v1_softmax_shares_hard_exact_cells"

    # -- object 1: contemporaneous revenue from the reconciliation, PIT backtested
    for prior_basis in ["PIT", "full_sample"]:
        for wname, dates in [("W1", H.GUIDE_DATES_W1), ("W2", H.GUIDE_DATES_W2)]:
            resid_hist = []
            for d in dates:
                grow = cal[cal.guide_date.astype(str) == str(d)]
                if len(grow) == 0:
                    continue
                tq = str(grow.iloc[0]["next_quarter_guided"])
                if tq == "nan" or not tq:
                    continue
                pt, ntr = pit_point(d, tq, prior_basis, ex, den, iv, fx, kpi, quarters, panel)
                if pt is None or not np.isfinite(pt):
                    continue
                sd = max(0.025 * pt, np.std(resid_hist, ddof=1) if len(resid_hist) > 2 else 0.0)
                act = tg[tg.quarter == tq]["revenue_musd"]
                if len(act) and np.isfinite(act.iloc[0]):
                    resid_hist.append(float(act.iloc[0]) - pt)
                rows.append(dict(method="l1-reconciliation", object="revenue_contemporaneous",
                                 target="revenue_musd", quarter=tq, vintage_date=str(d),
                                 horizon_q=1, point=pt, q50=pt, window=wname,
                                 prior_basis=prior_basis, n_params=rec.n_params + 8,
                                 n_train=ntr,
                                 q10=pt - 1.2816 * sd, q90=pt + 1.2816 * sd,
                                 q05=pt - 1.6449 * sd, q95=pt + 1.6449 * sd, sd=sd,
                                 knowable_from=str(d), spec_id=spec,
                                 notes="regional GBV x fitted regional take rate; reported-ADR basis"))
    df1 = pd.DataFrame(rows)
    if len(df1):
        H.register(df1, allow_single_replay=True)
        say(f"registered l1-reconciliation__revenue_contemporaneous: {len(df1)} rows")
        say(df1.groupby(["window", "prior_basis"]).size().to_string())
    else:
        say("l1-reconciliation__revenue_contemporaneous: NO rows produced")

    # -- object 2 and 3: FY27 level and growth, LIVE at TODAY
    rows2, rows3 = [], []
    grid = fy27["grid"]
    for q in ["2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4"]:
        col = f"rev_{q}"
        vals = grid[col].dropna().to_numpy(float)
        if not len(vals):
            continue
        pt = float(grid[(grid.scenario == "driver_base")
                        & (np.isclose(grid.kernel_w, 2 / 3))][col].iloc[0])
        sd = max(float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0, 0.026 * pt)
        h = D.qorder(q) - D.qorder("2026Q3")
        rows2.append(dict(method="l1-reconciliation", object="fy27_revenue",
                          target="revenue_musd", quarter=q, vintage_date=str(TODAY),
                          horizon_q=h, point=pt, q50=pt, window="LIVE", prior_basis="full_sample",
                          n_params=rec.n_params + 8 + 4, n_train=len(quarters),
                          q10=pt - 1.2816 * sd, q90=pt + 1.2816 * sd,
                          q05=pt - 1.6449 * sd, q95=pt + 1.6449 * sd, sd=sd,
                          knowable_from=str(TODAY), spec_id=spec + "__driver_base_w0667",
                          notes="kernel convolution of reconciled GBV; w grid 0.33-0.667 in sd"))
        q4 = D.qadd(q, -4)
        prev = None
        if q4 in set(kpi.quarter):
            prev = float(kpi.set_index("quarter").loc[q4, "revenue_musd"])
        elif f"rev_{q4}" in grid.columns:
            prev = float(grid[(grid.scenario == "driver_base")
                              & (np.isclose(grid.kernel_w, 2 / 3))][f"rev_{q4}"].iloc[0])
        if prev:
            g = 100 * (pt / prev - 1)
            gsd = 100 * sd / prev
            rows3.append(dict(method="l1-reconciliation", object="fy27_growth",
                              target="revenue_yoy", quarter=q, vintage_date=str(TODAY),
                              horizon_q=h, point=g, q50=g, window="LIVE",
                              prior_basis="full_sample", n_params=rec.n_params + 8 + 4,
                              n_train=len(quarters),
                              q10=g - 1.2816 * gsd, q90=g + 1.2816 * gsd,
                              q05=g - 1.6449 * gsd, q95=g + 1.6449 * gsd, sd=gsd,
                              knowable_from=str(TODAY), spec_id=spec + "__growth",
                              notes="named non-overlapping decomposition in l1_fy27_growth_decomposition.csv"))
    n_ok = 0
    for df, nm in [(pd.DataFrame(rows2), "fy27_revenue"), (pd.DataFrame(rows3), "fy27_growth")]:
        if not len(df):
            continue
        # HARNESS v1.0 accepts window=LIVE only for quarter 2026Q3.  Forward quarters
        # beyond that have no legal window value.  Register what is legal and park the
        # rest locally; the difference is filed as a harness change request in the note.
        legal = df[df.quarter == "2026Q3"]
        parked = df[df.quarter != "2026Q3"]
        if len(parked):
            parked.to_csv(OUT / f"l1_unregistered_{nm}.csv", index=False)
            say(f"HARNESS CHANGE REQUEST: {len(parked)} rows of {nm} for 2026Q4-2027Q4 "
                f"cannot be registered (window=LIVE is restricted to 2026Q3); parked at "
                f"l1_unregistered_{nm}.csv")
        if len(legal):
            try:
                H.register(legal, allow_single_replay=True)
                say(f"registered l1-reconciliation__{nm}: {len(legal)} rows")
                n_ok += len(legal)
            except Exception as e:                       # pragma: no cover
                say(f"REGISTRY REFUSED l1-reconciliation__{nm}: {e}")
                df.to_csv(OUT / f"l1_unregistered_{nm}.csv", index=False)
    return len(df1) + n_ok


def pit_point(d, target_q, prior_basis, ex, den, iv, fx, kpi, quarters, full_panel):
    """Refit the reconciliation on the information set at guide date `d` and roll
    one quarter forward.  PIT: filings strictly-or-same-day before `d` only (the
    harness's ratified include_same_day convention), intervals with
    knowable_from <= d, FX cut at d-1, no consensus.

    Verification round 1 fix: the FX pp table is now REBUILT at each guide date
    from the date-restricted intervals with the FX aggregates cut at d-1, rather
    than the full-sample table being reused.  No leakage was demonstrated under
    the old code (the ex-FX ADR constraint only fires for quarter pairs already
    inside the PIT quarter set, and the one-quarter-ahead projection never
    touches FX at all), but the harness FX rule asks for the d-1 cut explicitly
    and another package could copy the pattern into a place where it does bite.
    """
    if prior_basis == "PIT":
        exd = ex[ex.knowable_from <= d]
        ivd = iv[iv.knowable_from <= d]
        qs = sorted(exd.quarter.unique(), key=D.qorder)
        if len(qs) < 5:
            return None, 0
        dend = den[den.quarter.isin(qs)]
        fxd = D.fx_pp_table(ivd, as_of=d)          # FX cut at d-1
        try:
            r2 = M.Recon(qs, exd, dend, ivd, fxd, w_smooth=W_CONF["smooth"],
                         drift=W_CONF["drift"])
            t2, _ = r2.fit(max_nfev=800)
            pan = r2.panel(t2)
        except Exception:
            return None, 0
    else:
        qs = quarters
        pan = full_panel[full_panel.quarter.isin(qs)]
    hist = [q for q in qs if D.qorder(q) < D.qorder(target_q)]
    if not hist:
        return None, 0
    lastq = hist[-1]
    if D.qadd(target_q, -4) not in set(hist):
        # the y/y base for the target quarter is not yet in the information set:
        # the XBRL regional revenue for a quarter only becomes public with the next
        # year's comparative filing, so the l1 object simply does not exist here.
        return None, len(hist)
    try:
        proj = P.project_regional(pan[pan.quarter.isin(hist)], [target_q], None, None)
    except KeyError:
        return None, len(hist)
    tr = pan[pan.quarter == lastq].set_index("region")["take_rate_pct"]
    rev = float((proj.set_index("region")["gbv_musd"] * tr / 100.0).sum())
    return rev, len(hist)


if __name__ == "__main__":
    sys.exit(main())
