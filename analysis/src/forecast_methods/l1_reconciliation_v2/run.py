"""l1-reconciliation-v2 entry point -- task B3, the FY27 decomposition rebuild.

    cd "<repo>"
    python \
        analysis/src/forecast_methods/l1_reconciliation_v2/run.py

EXPLORATORY.  Nothing here is a scored object: the harness has no annual slot and
`l1-reconciliation` registers nothing at annual horizon.  Read the note at
docs/revenue-forecast-strategy/05_backtests/B3_FY27_DECOMPOSITION.md.

WHAT THIS IS.  RED_TEAM F1 refuted the published FY27 decomposition: 14 additive
lines in which geographic mix (-1.09pp) and unit-size/LOS (+0.38pp) were listed as
separate contributors although (1+volume 8.2632%)(1+ADR 3.00%) = 11.5111% already
IS the model's GBV growth; the volume x price cross term (+0.2479pp) was omitted;
and "kernel timing +0.1674pp" was a residual mislabelled as an identity (the true
computed value is +0.0117pp).  This package rebuilds the object multiplicatively,
separates COMPUTED from ASSUMED, and publishes the kernel-weight band.

COPY-NEVER-OVERWRITE.  This package READS v1 artefacts from
`data/processed/forecast_methods/l1_reconciliation/` and WRITES only to
`data/processed/forecast_methods/l1_reconciliation_v2/` and to registry files
under the NEW method name `l1-reconciliation-v2`.  It does not run the
reconciliation fit, does not touch v1 outputs, and does not run harness/score.py.

NUMERAIRE HEADER: unchanged from v1 -- REPORTED ADR (GBV / units), no de-gross-up.
BOUNDARY: unchanged -- exactly one object crosses onward, gbv_musd, quarterly.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # .../forecast_methods
sys.path.insert(0, str(HERE.parents[1]))      # .../src

from l1_reconciliation_v2 import data as D, project as P   # noqa: E402
import harness as H                                        # noqa: E402

TODAY = dt.date(2026, 9, 11)
OUT = D.OUT
V1 = D.SRC_V1
OUT.mkdir(parents=True, exist_ok=True)

FY26_Q = ["2026Q1", "2026Q2", "2026Q3", "2026Q4"]
FY27_Q = ["2027Q1", "2027Q2", "2027Q3", "2027Q4"]
FWD = ["2026Q3", "2026Q4"] + FY27_Q

# --- Street anchors.  VENDOR-STAMPED.  Source: 05_backtests/A1_consensus_vintages.md
#     (captured 11 Sep 2026 15:44-15:55 ET) and 00_IMPLEMENTATION_DECISIONS.md line 494
#     (Zacks 3-4 Sep 2026).  Street-implied growth = vendor FY27 / vendor FY26 - 1.
STREET = [
    dict(vendor="Zacks", as_of="2026-09-04", fy26_musd=14130.0, fy27_musd=15745.0,
         n_fy27=None, note="ranges FY26 $14.10-14.16bn, FY27 $15.73-15.76bn; midpoints used "
                           "(00_IMPLEMENTATION_DECISIONS.md line 494)"),
    dict(vendor="Zacks", as_of="2026-09-11", fy26_musd=14100.0, fy27_musd=15740.0,
         n_fy27=13, note="A1 table 1; FY26 n=8, FY27 n=13"),
    dict(vendor="Alpha Vantage (LSEG family)", as_of="2026-09-11", fy26_musd=14155.1,
         fy27_musd=15757.8, n_fy27=44, note="A1 table 1; FY26 n=43, FY27 n=44"),
    dict(vendor="Yahoo Finance (LSEG family)", as_of="2026-09-11", fy26_musd=14160.0,
         fy27_musd=15790.0, n_fy27=43, note="A1 table 1; not independent of Alpha Vantage"),
    dict(vendor="S&P Global MI", as_of="2026-09-10", fy26_musd=14160.0, fy27_musd=15770.0,
         n_fy27=None, note="A1 table 1; FY27 n paywalled"),
]
TURNS_PER_PP = 0.48          # EV/EBITDA turns per point of forward revenue growth,
                             # APPLIED ONCE (OPTIMAL_MIX.md §4.5 / INTEGRATED_SYSTEM §3(e))

# Kernel walk-forward error, used ONLY to widen the predictive interval.
KERNEL_PIT_MAPE_PCT = 2.313  # strict-PIT replay (RED_TEAM §6 / 07_MORNING_REPORT line 379).
                             # The quoted 1.74% is the full-sample-prior replay; the strict
                             # PIT number is the honest one and it is the one used here.
MAE_TO_SD = np.sqrt(np.pi / 2)   # Gaussian MAE -> sd


def main() -> int:
    log = []

    def say(s=""):
        print(s)
        log.append(str(s))

    say("=" * 78)
    say("l1-reconciliation-v2 -- B3 FY27 decomposition rebuild.  EXPLORATORY.")
    say(f"run {TODAY}.  reads v1 artefacts read-only from {V1.name}/, writes to {OUT.name}/")
    say("=" * 78)

    # ------------------------------------------------------------------ inputs
    kpi = D.load_kpi()
    panel_v1 = pd.read_csv(V1 / "l1_panel_quarterly.csv")
    scen = pd.read_csv(V1 / "l1_fy27_regional_scenario_driver.csv")
    grid_v1 = pd.read_csv(V1 / "l1_fy27_revenue_grid.csv")
    boot = pd.read_csv(V1 / "l1_bootstrap_intervals.csv")

    cols = ["quarter", "region", "nights_m", "adr_reported_usd", "gbv_musd"]
    panel = pd.concat([panel_v1[panel_v1.quarter.isin(["2026Q1", "2026Q2"])][cols],
                       scen[cols]], ignore_index=True)

    lam = P.seasonal_lambda(kpi, w=P.KERNEL_W_PUBLISHED)
    say("\nseasonal lambda (recomputed from the KPI panel at w=2/3, as v1 does; NOTE that "
        "\nlambda is ESTIMATED at w=2/3 and then held FIXED across the w grid -- that is v1's"
        "\nconvention, reproduced here so the grids are comparable, and it is a caveat):")
    for s in sorted(lam):
        say(f"  lambda_Q{s} = {lam[s]['mean']:.6f}%  (n={lam[s]['n']}, sd={lam[s]['sd']:.4f})")

    gbv = dict(kpi.set_index("quarter")["gbv_musd"])
    gbv.update(scen.groupby("quarter")["gbv_musd"].sum().to_dict())
    actual_rev = {q: float(kpi.set_index("quarter").loc[q, "revenue_musd"])
                  for q in ["2026Q1", "2026Q2"]}

    # ------------------------------------------- 1. reproduce the v1 grid exactly
    say("\n--- CHECK 0: does v2 reproduce the v1 driver_base grid?  (it must, to the cent)")
    repro = []
    for w in P.KERNEL_W_GRID:
        kk = P.kernel_kappa(gbv, lam, w, actual_rev, FY26_Q, FY27_Q)
        ref = grid_v1[(grid_v1.scenario == "driver_base")
                      & (np.isclose(grid_v1.kernel_w, w))].iloc[0]
        repro.append(dict(kernel_w=w,
                          fy26_v2=kk["fy_y0_revenue_musd"], fy26_v1=float(ref.fy26_revenue_musd),
                          fy27_v2=kk["fy_y1_revenue_musd"], fy27_v1=float(ref.fy27_revenue_musd),
                          growth_v2=100 * kk["g_revenue"], growth_v1=float(ref.fy27_growth_pct)))
    rep = pd.DataFrame(repro)
    rep["abs_err_fy27_musd"] = (rep.fy27_v2 - rep.fy27_v1).abs()
    rep["abs_err_growth_pp"] = (rep.growth_v2 - rep.growth_v1).abs()
    say(rep.round(6).to_string(index=False))
    assert rep.abs_err_fy27_musd.max() < 1e-6 and rep.abs_err_growth_pp.max() < 1e-9, \
        "v2 does not reproduce the v1 grid"
    say("  PASS: max |dFY27| = %.2e $M, max |dgrowth| = %.2e pp" %
        (rep.abs_err_fy27_musd.max(), rep.abs_err_growth_pp.max()))

    # --------------------------------------------------- 2. the GBV factorisation
    ann = P.annual_regional(panel)
    fac = P.gbv_factorisation(ann)
    say("\n--- THE ALGEBRA (FY2027 vs FY2026, driver_base GBV path; GBV is w-INVARIANT)")
    say(f"  GBV_FY26 = {fac['gbv_y0']:,.1f} $M      GBV_FY27 = {fac['gbv_y1']:,.1f} $M")
    say(f"  N_FY26   = {fac['nights_y0']:,.2f} M     N_FY27   = {fac['nights_y1']:,.2f} M")
    say(f"  ADR_FY26 = {fac['adr_y0']:,.4f} $        ADR_FY27 = {fac['adr_y1']:,.4f} $")
    say("")
    say("  BASIS B (published).  GBV == N x ADR_blend, exactly, so")
    say(f"    (1 + g_N {100*fac['g_nights']:+.6f}%) x (1 + g_ADR {100*fac['g_adr']:+.6f}%) - 1 "
        f"= {100*((1+fac['g_nights'])*(1+fac['g_adr'])-1):+.6f}%  ==  g_GBV {100*fac['g_gbv']:+.6f}%")
    say(f"    additive expansion: {100*fac['g_nights']:+.4f} + {100*fac['g_adr']:+.4f} "
        f"+ cross {100*fac['cross_nights_adr']:+.4f} = {100*fac['g_gbv']:+.4f} pp")
    say("")
    say("  BASIS A (the red team's index basis).  Fixed-price quantity index Q x "
        "fixed-quantity price index P:")
    say(f"    (1 + Q {100*fac['lasp_quantity_Q']:+.6f}%) x (1 + P {100*fac['lasp_price_P']:+.6f}%) - 1 "
        f"= {100*((1+fac['lasp_quantity_Q'])*(1+fac['lasp_price_P'])-1):+.6f}%  ==  g_GBV")
    say(f"    additive expansion: {100*fac['lasp_quantity_Q']:+.4f} + {100*fac['lasp_price_P']:+.4f} "
        f"+ cross {100*fac['cross_QP']:+.4f} = {100*fac['g_gbv']:+.4f} pp")
    say("")
    say("  *** THE v1 DOUBLE COUNT, NAMED.  v1 took its VOLUME line from basis A (Q = "
        f"{100*fac['lasp_quantity_Q']:+.4f}pp,")
    say("      a FIXED-PRICE index which ALREADY CONTAINS geographic mix) and its PRICE line "
        "from basis A")
    say(f"      (P = {100*fac['lasp_price_P']:+.4f}pp), then ADDED the basis-B geographic-mix "
        f"line ({100*fac['adr_geo_mix']:+.4f}pp)")
    say("      and the unit-size/LOS line (+0.3818pp) on top.  Mixing the two bases is the "
        "double count.")
    say(f"      It also dropped the basis-A cross term ({100*fac['cross_QP']:+.4f}pp), which is "
        "why the plug came out")
    say("      at +0.1674pp instead of the true kernel effect.  v2 never mixes bases.")

    say("\n  regional detail (driver_base scenario assumptions):")
    say(fac["regional"].round(4).to_string())

    # ------------------------------------------------------ 3. the kernel effect
    say("\n--- THE KERNEL RECOGNITION / TIMING EFFECT kappa_w, COMPUTED (not a residual)")
    say("  Revenue_q = lambda_s(q) x [ w*GBV_{q-1} + (1-w)*GBV_{q-2} ].  FY26 revenue uses the")
    say("  PRINTED 1Q26 ($2,678M) and 2Q26 ($3,608M); 3Q26/4Q26 and all of FY27 are kernel.")
    kap = {w: P.kernel_kappa(gbv, lam, w, actual_rev, FY26_Q, FY27_Q) for w in P.KERNEL_W_GRID}
    for w in P.KERNEL_W_GRID:
        k = kap[w]
        say(f"  w={w:.4f}:  FY26 rev {k['fy_y0_revenue_musd']:,.1f}  FY27 rev "
            f"{k['fy_y1_revenue_musd']:,.1f}  g_rev {100*k['g_revenue']:+.5f}%  "
            f"kappa {100*k['kappa']:+.5f}%  (lag channel {100*k['kappa_lag_channel']:+.5f}, "
            f"print channel {100*k['kappa_print_channel']:+.5f})")
    say(f"  The v1 line 'kernel timing +0.1674pp, an identity' is REFUTED: at w=2/3 the "
        f"computed effect is {100*kap[2/3]['kappa']:+.5f}%, i.e. "
        f"{100*(1+fac['g_gbv'])*kap[2/3]['kappa']:+.4f}pp of growth.")

    # ------------------------------------------- 4. the decomposition table itself
    dec = build_decomposition(fac, kap)
    dec.to_csv(OUT / "fy27_decomposition_v2.csv", index=False)
    say("\n--- fy27_decomposition_v2.csv  (block / line / pp; only block=COMPUTED_TOTAL rows "
        "carry weight)")
    say(dec[["block", "line", "pp_w0333", "pp_w050", "pp_w0667", "weight_in_total",
             "attributed_pp_of_adr_line", "basis"]].round(4).to_string(index=False))

    # ----------------------------------------------- 5. identity reproduction test
    chk = identity_check(fac, kap, dec)
    chk.to_csv(OUT / "fy27_identity_check_v2.csv", index=False)
    say("\n--- IDENTITY CHECK: do the pieces reproduce total FY27 growth at every w?")
    say(chk.round(8).to_string(index=False))
    assert chk.abs_err_pp.max() < 0.01, "identity does not reproduce to 0.01pp"
    say(f"  PASS: max |error| = {chk.abs_err_pp.max():.2e} pp (tolerance 0.01pp)")

    # --------------------------------------------------- 6. the ADR attribution
    attr = build_attribution(fac)
    attr.to_csv(OUT / "fy27_adr_attribution_v2.csv", index=False)
    say("\n--- ADR ATTRIBUTION (ZERO WEIGHT IN THE TOTAL).  Sums to the ADR line, by "
        "construction.")
    say(attr[["level", "line", "pp", "basis", "weight_in_total"]].round(4).to_string(index=False))

    # ------------------------------------------------------- 7. bootstrap widening
    sd_boot = bootstrap_growth_sd(boot, ann, panel, gbv, lam, actual_rev, say)

    # ------------------------------------------------------- 8. kernel-weight band
    band = kernel_band(kap, fac, sd_boot)
    band.to_csv(OUT / "fy27_kernel_band_v2.csv", index=False)
    say("\n--- KERNEL-WEIGHT BAND (w = 0.33 / 0.50 / 2/3)")
    say(band[["kernel_w", "fy26_revenue_musd", "fy27_revenue_musd", "fy27_growth_pct",
              "fy27_revenue_incl_assumed_theta1_musd",
              "fy27_revenue_incl_assumed_theta083_musd"]].round(2).to_string(index=False))

    edges = street_edges(band)
    edges.to_csv(OUT / "fy27_street_edges_v2.csv", index=False)
    say("\n--- GROWTH EDGE vs EACH VENDOR-STAMPED STREET ANCHOR, and the multiple implication")
    say("    (+0.48 EV/EBITDA turns per point of forward growth, APPLIED ONCE)")
    say(edges[["vendor", "as_of", "street_fy27_musd", "street_implied_growth_pct", "kernel_w",
               "our_fy27_musd", "level_edge_pct", "growth_edge_pp", "ev_ebitda_turns"]]
        .round(4).to_string(index=False))

    # ------------------------------------------------------------- 9. registration
    n = register_v2(band, edges, kpi, say)

    (OUT / "run_log.txt").write_text("\n".join(log))
    print(f"\nwrote {len(list(OUT.glob('*.csv')))} csv files to {OUT}; registered {n} rows")
    return 0


# --------------------------------------------------------------- decomposition
def build_decomposition(fac, kap) -> pd.DataFrame:
    """The ONLY table that carries weight.  Three multiplicative factors, plus the
    additive cross term that makes the pp column add up, plus two zero-weight
    blocks (ATTRIBUTION, ASSUMED) that are fenced off from the total."""
    ws = P.KERNEL_W_GRID
    gN, gA, gG = fac["g_nights"], fac["g_adr"], fac["g_gbv"]
    rows = []
    rows.append(dict(block="COMPUTED_GBV", line="volume: total Nights-and-Seats (N)",
                     factor=f"1 + {100*gN:+.6f}%",
                     pp_w0333=100 * gN, pp_w050=100 * gN, pp_w0667=100 * gN,
                     weight_in_total="YES", owner="l1-reconciliation-v2", basis="computed",
                     source="N_FY27 / N_FY26 - 1 from the driver_base regional scenario "
                            "(l1_fy27_regional_scenario_driver.csv) + printed 1H26 regional panel",
                     note="regional nights y/y NA +6.0 / EMEA +7.0 / LatAm +16.0 / APAC +15.0, "
                          "from 10_regional_forecast.csv base scenario"))
    rows.append(dict(block="COMPUTED_GBV", line="price: blended REPORTED ADR (ADR_blend)",
                     factor=f"1 + {100*gA:+.6f}%",
                     pp_w0333=100 * gA, pp_w050=100 * gA, pp_w0667=100 * gA,
                     weight_in_total="YES", owner="l1-reconciliation-v2", basis="computed",
                     source="ADR_blend == sum_r share_r x ADR_r, the L1 share identity",
                     note="geographic mix, unit-size mix, LOS, seats dilution and booking-date FX "
                          "are ALL INSIDE this line -- see the ATTRIBUTION block, which has "
                          "ZERO weight"))
    rows.append(dict(block="COMPUTED_GBV", line="cross term: volume x price",
                     factor="(expansion term, not a factor)",
                     pp_w0333=100 * gN * gA, pp_w050=100 * gN * gA, pp_w0667=100 * gN * gA,
                     weight_in_total="YES", owner="l1-reconciliation-v2", basis="computed",
                     source="g_N x g_ADR; it exists only because the pp column is additive",
                     note="v1 OMITTED this term; that omission is half of why the v1 plug was "
                          "+0.1674pp"))
    rows.append(dict(block="COMPUTED_TOTAL", line="= GBV growth (w-INVARIANT)",
                     factor=f"1 + {100*gG:+.6f}%",
                     pp_w0333=100 * gG, pp_w050=100 * gG, pp_w0667=100 * gG,
                     weight_in_total="SUBTOTAL", owner="l1-reconciliation-v2", basis="computed",
                     source="(1+g_N)(1+g_ADR) - 1, exact",
                     note="the kernel weight w does NOT move GBV; it moves only the recognition "
                          "of GBV into revenue"))
    kvals = [100 * (1 + gG) * kap[w]["kappa"] for w in ws]
    rows.append(dict(block="COMPUTED_REVENUE",
                     line="kernel recognition / timing (lagged-GBV conversion)",
                     factor="1 + kappa_w  (%s)" % " / ".join(
                         f"w={w:.3f}: {100*kap[w]['kappa']:+.5f}%" for w in ws),
                     pp_w0333=kvals[0], pp_w050=kvals[1], pp_w0667=kvals[2],
                     weight_in_total="YES", owner="kernel-lambda / l1-reconciliation-v2",
                     basis="computed",
                     source="kappa_w = (1+g_revenue)/(1+g_GBV) - 1 with BOTH sides built from "
                            "lambda_s and the GBV path; nothing solved for",
                     note="REPLACES the v1 line 'kernel timing +0.1674pp, an identity', which "
                          "RED_TEAM F1 refuted as a residual.  Two channels inside it: the "
                          "lambda-weighted lagged-GBV base grows at a different rate than the "
                          "calendar year, and FY26 1H is the PRINTED number rather than the "
                          "kernel's own"))
    rvals = [100 * kap[w]["g_revenue"] for w in ws]
    rows.append(dict(block="COMPUTED_TOTAL",
                     line="= FY27 REVENUE GROWTH, COMPUTED (excludes the ASSUMED block)",
                     factor="(1+g_GBV)(1+kappa_w)",
                     pp_w0333=rvals[0], pp_w050=rvals[1], pp_w0667=rvals[2],
                     weight_in_total="TOTAL", owner="l1-reconciliation-v2", basis="computed",
                     source="the kernel convolution of the reconciled GBV path",
                     note="this is the growth implied by the $15,720.3 / $15,779.5 / $15,837.6M "
                          "revenue grid; the four ASSUMED lines below are NOT in those dollars"))

    for key, d in P.ASSUMED_FY27_V2.items():
        nm = {"fee_take_rate_mechanism_pp": "fee / take-rate migration (half weight)",
              "new_lines_pp": "new lines outside GBV (ads, Services excess)",
              "regulation_pp": "regulation (dated DiD on EMEA nights)",
              "hedge_pp": "hedge (DOLLARS, added ONCE by kernel-lambda)"}[key]
        rows.append(dict(block="ASSUMED_NOT_IN_THE_COMPUTED_DOLLAR", line=nm,
                         factor=f"+{d['pp']:.2f}pp as carried; "
                                f"restated {d['lo']:+.2f} to {d['hi']:+.2f}pp",
                         pp_w0333=d["pp"], pp_w050=d["pp"], pp_w0667=d["pp"],
                         weight_in_total="NO -- OUTSIDE the computed $15,837.6M",
                         owner="fee-takerate / kernel-lambda", basis="assumed",
                         source=d["source"], note=d["note"]))
    tot_as = sum(d["pp"] for d in P.ASSUMED_FY27_V2.values())
    tot_as_c = sum(d["central"] for d in P.ASSUMED_FY27_V2.values())
    rows.append(dict(block="ASSUMED_NOT_IN_THE_COMPUTED_DOLLAR",
                     line="= assumed block, total",
                     factor=f"as carried {tot_as:+.2f}pp; at theta=0.833 {tot_as_c:+.2f}pp",
                     pp_w0333=tot_as, pp_w050=tot_as, pp_w0667=tot_as,
                     weight_in_total="NO -- shown separately, never added silently",
                     owner="fee-takerate / kernel-lambda", basis="assumed",
                     source="sum of the four lines above",
                     note="FY27 revenue INCLUDING this block is published alongside, never "
                          "instead of, the computed number"))

    # the ATTRIBUTION block appears here too, at zero, so the file is self-contained
    for r in build_attribution(fac).itertuples():
        rows.append(dict(block="ATTRIBUTION_ZERO_WEIGHT", line=f"[{r.level}] {r.line}",
                         factor="attribution only", pp_w0333=0.0, pp_w050=0.0, pp_w0667=0.0,
                         weight_in_total="NO -- ZERO WEIGHT (already inside the ADR line)",
                         attributed_pp_of_adr_line=r.pp,
                         owner=r.owner, basis=r.basis, source=r.source, note=r.note))
    d = pd.DataFrame(rows)
    if "attributed_pp_of_adr_line" not in d.columns:
        d["attributed_pp_of_adr_line"] = np.nan
    return d[["block", "line", "factor", "pp_w0333", "pp_w050", "pp_w0667",
              "weight_in_total", "attributed_pp_of_adr_line", "owner", "basis",
              "source", "note"]]


def build_attribution(fac) -> pd.DataFrame:
    """Attribution of the blended-ADR line.  ZERO weight.  Sums to the ADR line.

    Level 1 splits blended ADR into the share identity's own outputs:
        g_ADR == geographic mix + within-region price + (mix x price) cross.
    Level 2 splits the within-region price line into the named measurements and
    leaves like-for-like price + sub-regional mix as the IDENTIFIED REMAINDER --
    the 2-d ridge the decisions document forbids splitting.
    """
    gA, mix, within, cx = (fac["g_adr"], fac["adr_geo_mix"],
                           fac["adr_within_region"], fac["adr_cross"])
    S = P.ADR_ATTRIBUTION_SOURCES
    rows = [
        dict(level="L1", line="geographic mix (OUTPUT of ADR_blend = sum_r share_r ADR_r)",
             pp=100 * mix, owner="l1-reconciliation-v2", basis="computed_output",
             source="this build's own share identity; cross-validated in l1-reconciliation §4 "
                    "against the 10-K Geographic Mix table and the ADR note to <=0.14pp",
             note="the plan carries -1.5pp and the ADR note -1.6pp (2025); the OBSERVED 2026 H1 "
                  "drag is only -0.34pp, so -1.09 may itself be too negative"),
        dict(level="L1", line="within-region price (reported basis, before the L2 split)",
             pp=100 * within, owner="l1-reconciliation-v2", basis="computed_output",
             source="sum_r share_r,FY26 x (ADR_r,FY27 - ADR_r,FY26) / ADR_blend,FY26",
             note="the driver_base scenario sets every region's ADR y/y to +3.00% ex-FX with FX "
                  "on a flat-spot carry, so this line equals +3.00pp by assumption"),
        dict(level="L1", line="mix x price cross term",
             pp=100 * cx, owner="l1-reconciliation-v2", basis="computed_output",
             source="g_ADR - geographic mix - within-region price", note="small by construction"),
        dict(level="L1", line="= ADR LINE (blended reported ADR growth)", pp=100 * gA,
             owner="l1-reconciliation-v2", basis="computed",
             source="ADR_FY27 / ADR_FY26 - 1", note="SUBTOTAL: the three L1 rows sum to this"),
        dict(level="L2", line="unit-size mix (bedroom elasticity 0.23)", pp=S["unit_size_mix_pp"]["pp"],
             owner="adr-decomposition (Krish, 7 Sep 2026)", basis=S["unit_size_mix_pp"]["basis"],
             source=S["unit_size_mix_pp"]["source"], note=S["unit_size_mix_pp"]["note"]),
        dict(level="L2", line="LOS mix", pp=S["los_mix_pp"]["pp"],
             owner="adr-decomposition (Krish, 7 Sep 2026)", basis=S["los_mix_pp"]["basis"],
             source=S["los_mix_pp"]["source"], note=S["los_mix_pp"]["note"]),
        dict(level="L2", line="seats / hotel dilution (OUTPUT of N = home + hotel + seats)",
             pp=S["seats_hotel_dilution_pp"]["pp"], owner="l1-reconciliation / seats note",
             basis=S["seats_hotel_dilution_pp"]["basis"],
             source=S["seats_hotel_dilution_pp"]["source"],
             note=S["seats_hotel_dilution_pp"]["note"]),
        dict(level="L2", line="booking-date FX carried through Phi",
             pp=S["booking_fx_phi_pp"]["pp"], owner="fx-lag / l1-reconciliation-v2",
             basis=S["booking_fx_phi_pp"]["basis"], source=S["booking_fx_phi_pp"]["source"],
             note=S["booking_fx_phi_pp"]["note"]),
    ]
    named = sum(S[k]["pp"] for k in S)
    rem = 100 * within - named
    rows.append(dict(level="L2",
                     line="like-for-like price + sub-regional mix (IDENTIFIED REMAINDER)",
                     pp=rem, owner="l1-reconciliation-v2", basis="unidentified_2d_ridge",
                     source="within-region price line MINUS the four named L2 measurements",
                     note="NOT SPLIT: separate price and sub-regional-mix states are exactly "
                          "collinear (00_IMPLEMENTATION_DECISIONS.md §8.2).  It lands at "
                          f"{rem:+.2f}pp against the plan's +2.9pp, which is corroboration, "
                          "not a second estimate"))
    rows.append(dict(level="L2", line="= within-region price line (L2 rows sum to this)",
                     pp=100 * within, owner="l1-reconciliation-v2", basis="computed",
                     source="identity", note="SUBTOTAL"))
    d = pd.DataFrame(rows)
    d["weight_in_total"] = "NO -- ZERO WEIGHT"
    return d[["level", "line", "pp", "weight_in_total", "owner", "basis", "source", "note"]]


def identity_check(fac, kap, dec) -> pd.DataFrame:
    """Do the published pieces reproduce total FY27 growth at each w, to 0.01pp?"""
    rows = []
    for w, col in zip(P.KERNEL_W_GRID, ["pp_w0333", "pp_w050", "pp_w0667"]):
        k = kap[w]
        gN, gA = fac["g_nights"], fac["g_adr"]
        mult = 100 * ((1 + gN) * (1 + gA) * (1 + k["kappa"]) - 1)
        add = float(dec[(dec.block.isin(["COMPUTED_GBV", "COMPUTED_REVENUE"]))][col].sum())
        actual = 100 * k["g_revenue"]
        rows.append(dict(kernel_w=w,
                         multiplicative_pct=mult, additive_pp_sum=add, model_growth_pct=actual,
                         abs_err_pp=max(abs(mult - actual), abs(add - actual)),
                         attribution_block_weight=float(
                             dec[dec.block == "ATTRIBUTION_ZERO_WEIGHT"][col].sum()),
                         assumed_block_excluded_pp=float(
                             dec[(dec.block == "ASSUMED_NOT_IN_THE_COMPUTED_DOLLAR")
                                 & (dec.line == "= assumed block, total")][col].iloc[0])))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------- bootstrap
def bootstrap_growth_sd(boot, ann, panel, gbv, lam, actual_rev, say) -> float:
    """Propagate the PUBLISHED block-bootstrap regional-share intervals into an sd
    on FY27 GBV growth.  A Monte Carlo is used only to PROPAGATE an interval that
    already exists -- it is not the method (00_IMPLEMENTATION_DECISIONS.md §9.11).

    Channel: total GBV per quarter is pinned by the letters, so the bootstrap's
    live uncertainty is COMPOSITION.  Perturb the regional nights-share vector,
    hold regional ADR, recompute the GBV weights and hence the fixed-price
    quantity index; regional growth rates and the +3.00% price line are held.
    """
    b = boot.set_index(["quarter", "region"])
    # 2026Q3/Q4 are projections: use the sd of the base quarter each rolls forward from.
    sd_src = {"2026Q1": "2026Q1", "2026Q2": "2026Q2", "2026Q3": "2025Q3", "2026Q4": "2025Q4"}
    pan = panel.copy()
    pan["year"] = pan.quarter.str[:4].astype(int)
    rng = np.random.default_rng(20260911)
    draws = 4000
    g = []
    q26 = ["2026Q1", "2026Q2", "2026Q3", "2026Q4"]
    base = {q: pan[pan.quarter == q].set_index("region") for q in q26}
    g27 = {}
    for r in D.REGIONS:
        n26 = sum(float(base[q].loc[r, "nights_m"]) for q in q26)
        n27 = float(pan[(pan.year == 2027) & (pan.region == r)]["nights_m"].sum())
        g27[r] = n27 / n26 - 1
    sd = {}
    for q in q26:
        s = sd_src[q]
        sd[q] = {r: max((float(b.loc[(s, r), "share_p90"]) - float(b.loc[(s, r), "share_p10"]))
                        / (2 * 1.2816), 1e-9) for r in D.REGIONS}
    for _ in range(draws):
        num, den = 0.0, 0.0
        for q in q26:
            tot_n = float(base[q]["nights_m"].sum())
            sh = np.array([100 * float(base[q].loc[r, "nights_m"]) / tot_n for r in D.REGIONS])
            sh = sh + np.array([rng.normal(0, sd[q][r]) for r in D.REGIONS])
            sh = np.clip(sh, 0.5, None)
            sh = 100 * sh / sh.sum()
            for i, r in enumerate(D.REGIONS):
                n = sh[i] / 100 * tot_n
                gb = n * float(base[q].loc[r, "adr_reported_usd"])
                den += gb
                num += gb * (1 + g27[r])
        g.append(1.03 * num / den - 1)          # +3.00% uniform price line
    g = np.array(g)
    s = float(np.std(g, ddof=1))
    say("\n--- BOOTSTRAP PROPAGATION (published block-bootstrap share intervals, "
        f"{draws} draws, seed 20260911)")
    say(f"  FY27 GBV growth p10 {100*np.percentile(g,10):+.4f}%  p50 "
        f"{100*np.percentile(g,50):+.4f}%  p90 {100*np.percentile(g,90):+.4f}%  "
        f"sd {100*s:.4f}pp")
    say("  Channel is COMPOSITION only: quarterly total GBV is pinned by the letters, so a "
        "share\n  perturbation moves the GBV weights and hence the quantity index, not the "
        "level.")
    return 100 * s


# ---------------------------------------------------------------- band & Street
def kernel_band(kap, fac, sd_boot_pp) -> pd.DataFrame:
    ws = P.KERNEL_W_GRID
    rev = {w: kap[w]["fy_y1_revenue_musd"] for w in ws}
    fy26 = {w: kap[w]["fy_y0_revenue_musd"] for w in ws}
    gr = {w: 100 * kap[w]["g_revenue"] for w in ws}
    pub = P.KERNEL_W_PUBLISHED
    sd_w_rev = abs(rev[pub] - min(rev.values())) / 1.2816
    sd_w_g = abs(gr[pub] - min(gr.values())) / 1.2816
    sd_kernel_rev = KERNEL_PIT_MAPE_PCT / 100 * MAE_TO_SD * rev[pub]
    rows = []
    as_carried = sum(d["pp"] for d in P.ASSUMED_FY27_V2.values())
    central = sum(d["central"] for d in P.ASSUMED_FY27_V2.values())
    for w in ws:
        sd_boot_rev = sd_boot_pp / 100 * fy26[w]
        sd_rev = float(np.sqrt(sd_w_rev ** 2 + sd_boot_rev ** 2 + sd_kernel_rev ** 2))
        sd_g = float(np.sqrt(sd_w_g ** 2 + sd_boot_pp ** 2
                             + (100 * sd_kernel_rev / fy26[w]) ** 2))
        rows.append(dict(
            kernel_w=w, fy26_revenue_musd=fy26[w], fy27_revenue_musd=rev[w],
            fy27_growth_pct=gr[w], gbv_growth_pct=100 * fac["g_gbv"],
            kappa_pct=100 * kap[w]["kappa"],
            assumed_block_pp_as_carried=as_carried, assumed_block_pp_theta083=central,
            fy27_revenue_incl_assumed_theta1_musd=rev[w] + fy26[w] * as_carried / 100,
            fy27_revenue_incl_assumed_theta083_musd=rev[w] + fy26[w] * central / 100,
            fy27_growth_incl_assumed_theta1_pct=gr[w] + as_carried,
            fy27_growth_incl_assumed_theta083_pct=gr[w] + central,
            sd_revenue_musd=sd_rev, sd_growth_pp=sd_g,
            sd_component_w_revenue_musd=sd_w_rev, sd_component_w_growth_pp=sd_w_g,
            sd_component_bootstrap_pp=sd_boot_pp,
            sd_component_kernel_pit_revenue_musd=sd_kernel_rev))
    return pd.DataFrame(rows)


def street_edges(band) -> pd.DataFrame:
    rows = []
    for s in STREET:
        imp = 100 * (s["fy27_musd"] / s["fy26_musd"] - 1)
        for r in band.itertuples():
            rows.append(dict(
                vendor=s["vendor"], as_of=s["as_of"], n_fy27=s["n_fy27"],
                street_fy26_musd=s["fy26_musd"], street_fy27_musd=s["fy27_musd"],
                street_implied_growth_pct=imp, kernel_w=r.kernel_w,
                our_fy27_musd=r.fy27_revenue_musd, our_growth_pct=r.fy27_growth_pct,
                level_edge_pct=100 * (r.fy27_revenue_musd / s["fy27_musd"] - 1),
                growth_edge_pp=r.fy27_growth_pct - imp,
                ev_ebitda_turns=TURNS_PER_PP * (r.fy27_growth_pct - imp),
                our_fy27_incl_assumed_theta083_musd=r.fy27_revenue_incl_assumed_theta083_musd,
                growth_edge_incl_assumed_theta083_pp=(r.fy27_growth_incl_assumed_theta083_pct
                                                      - imp),
                vendor_note=s["note"]))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- registration
def register_v2(band, edges, kpi, say) -> int:
    """Register fy27_revenue_v2 and fy27_growth_v2 under method l1-reconciliation-v2.

    HARNESS CHANGE REQUEST (this is RED_TEAM harness request 5).  Format v1.0 has
    no ANNUAL slot and `LIVE` is legal only for 2026Q3, the single guided forward
    quarter.  The FY27 object is annual.  Rather than park an annual number under a
    quarter label that contradicts it -- which is exactly what RED_TEAM flagged in
    `l1-reconciliation__fy27_revenue.csv` (one 2026Q3 row of 4,804.0 under an object
    called fy27_revenue) -- v2 registers the full forward QUARTERLY path 2026Q3 ...
    2027Q4 with `strict_windows=False`, so every row's `quarter` means what it says,
    and states the annual total in `notes` and in fy27_kernel_band_v2.csv.
    """
    pub = P.KERNEL_W_PUBLISHED
    row = band[np.isclose(band.kernel_w, pub)].iloc[0]
    lam = P.seasonal_lambda(kpi, w=pub)
    scen = pd.read_csv(V1 / "l1_fy27_regional_scenario_driver.csv")
    gbv = dict(kpi.set_index("quarter")["gbv_musd"])
    gbv.update(scen.groupby("quarter")["gbv_musd"].sum().to_dict())
    q_rev = {w: P.kernel_year(gbv, lam, w, FWD) for w in P.KERNEL_W_GRID}
    k = kpi.set_index("quarter")

    rel_sd_rev = float(row.sd_revenue_musd / row.fy27_revenue_musd)
    z = dict(q05=-1.6449, q10=-1.2816, q25=-0.6745, q75=0.6745, q90=1.2816, q95=1.6449)
    n_par, n_tr = 84, len(k)
    note = (f"EXPLORATORY B3 rebuild. Forward quarterly path; the FY27 annual object is the SUM "
            f"of the four 2027 rows = {row.fy27_revenue_musd:,.1f} musd at w=2/3 (w band "
            f"{band.fy27_revenue_musd.min():,.1f}-{band.fy27_revenue_musd.max():,.1f}); the 2026Q3 "
            f"and 2026Q4 rows are the FY26 base and are NOT part of FY27. The ASSUMED block "
            f"(+{row.assumed_block_pp_as_carried:.1f}pp as carried) is NOT in these dollars.")
    rows_r, rows_g = [], []
    for q in FWD:
        pt = q_rev[pub][q]["used_musd"]
        band_q = [q_rev[w][q]["used_musd"] for w in P.KERNEL_W_GRID]
        sd = float(np.sqrt((abs(pt - min(band_q)) / 1.2816) ** 2 + (rel_sd_rev * pt) ** 2))
        h = int((int(q[:4]) * 4 + int(q[5])) - (2026 * 4 + 3))
        r = dict(method="l1-reconciliation-v2", object="fy27_revenue_v2",
                 target="revenue_musd", quarter=q, vintage_date=str(TODAY), horizon_q=h,
                 point=pt, q50=pt, window="LIVE", prior_basis="full_sample",
                 n_params=n_par, n_train=n_tr, sd=sd,
                 knowable_from=str(TODAY),
                 spec_id="l1_recon_v2_multiplicative_fy27__driver_base_w0667",
                 notes=note)
        r.update({c: pt + zz * sd for c, zz in z.items()})
        rows_r.append(r)
        q4 = f"{int(q[:4])-1}Q{q[5]}"
        prev = float(k.loc[q4, "revenue_musd"]) if q4 in k.index else q_rev[pub][q4]["used_musd"]
        gg, gsd = 100 * (pt / prev - 1), 100 * sd / prev
        rg = dict(method="l1-reconciliation-v2", object="fy27_growth_v2",
                  target="revenue_yoy", quarter=q, vintage_date=str(TODAY), horizon_q=h,
                  point=gg, q50=gg, window="LIVE", prior_basis="full_sample",
                  n_params=n_par, n_train=n_tr, sd=gsd, knowable_from=str(TODAY),
                  spec_id="l1_recon_v2_multiplicative_fy27__growth",
                  notes=(f"EXPLORATORY B3. Quarterly y/y path; the FY27 ANNUAL growth object is "
                         f"{row.fy27_growth_pct:+.2f}% at w=2/3, w band "
                         f"{band.fy27_growth_pct.min():+.2f} to {band.fy27_growth_pct.max():+.2f}pp. "
                         f"Multiplicative decomposition in fy27_decomposition_v2.csv; ASSUMED "
                         f"block excluded."))
        rg.update({c: gg + zz * gsd for c, zz in z.items()})
        rows_g.append(rg)

    n = 0
    for df, nm in [(pd.DataFrame(rows_r), "fy27_revenue_v2"),
                   (pd.DataFrame(rows_g), "fy27_growth_v2")]:
        H.register(df, allow_single_replay=True, strict_windows=False)
        say(f"registered l1-reconciliation-v2__{nm}: {len(df)} rows "
            f"(strict_windows=False -- harness change request, see docstring)")
        n += len(df)
    # the annual object the harness cannot hold, parked locally in the v2 folder
    ann_rows = []
    for r in band.itertuples():
        ann_rows.append(dict(object="fy27_revenue_v2_annual", kernel_w=r.kernel_w,
                             fy26_musd=r.fy26_revenue_musd, fy27_musd=r.fy27_revenue_musd,
                             fy27_growth_pct=r.fy27_growth_pct, sd_musd=r.sd_revenue_musd,
                             sd_growth_pp=r.sd_growth_pp, vintage_date=str(TODAY),
                             window="LIVE_ANNUAL_NOT_SUPPORTED_BY_HARNESS_v1_0"))
    pd.DataFrame(ann_rows).to_csv(OUT / "fy27_annual_object_v2.csv", index=False)
    say("parked the ANNUAL FY27 object at fy27_annual_object_v2.csv (harness v1.0 has no "
        "annual slot)")
    return n


if __name__ == "__main__":
    sys.exit(main())
