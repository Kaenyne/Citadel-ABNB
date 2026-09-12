"""fx_lag / run.py -- entry point. Rebuilds every output. Exit code 0 on success.

    cd "<repo>"
    python analysis/src/forecast_methods/fx_lag/run.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

import baskets, panel, fits, stages, registry_out
from common import OUT, L0, write, TODAY


def main() -> int:
    written = []
    print("[1/9] baskets")
    baskets.build()
    print("[2/9] analysis panel")
    d = panel.build()

    print("[3/9] stage (b): ADR contemporaneous fits / 05_fx_fits reproduction")
    sb = fits.stage_b(d)

    print("[4/9] Object A: joint interval-likelihood lag regression + confidence set")
    resG, varG, packG = fits.object_a(d, "gross_fx_ex_hedge_pp", "gross_ex_hedge")
    resS, varS, packS = fits.object_a(d, "stated_revenue_fx_pp", "stated")
    write(pd.DataFrame([resG, resS]), "06_object_a_summary.csv")
    write(pd.concat([varG.assign(target="gross_ex_hedge"),
                     varS.assign(target="stated")], ignore_index=True),
          "06b_object_a_hypothesis_tests.csv")
    bs = pd.concat([stages.block_bootstrap_a(d, "gross_fx_ex_hedge_pp"),
                    stages.block_bootstrap_a(d, "stated_revenue_fx_pp")], ignore_index=True)
    write(bs, "06c_object_a_block_bootstrap.csv")

    print("[5/9] Object B: revenue-FX minus ADR-FX wedge")
    ob = fits.object_b(d)
    print("[6/9] Object C: architect falsification reproduction + extension")
    oc, _ = fits.object_c(d)

    print("[7/9] hypothesis horse-race (full sample LOO) and PIT expanding window")
    hr = pd.concat([stages.full_sample_horse_race(d, "fx_pts_revenue", "stated"),
                    stages.full_sample_horse_race(d, "gross_fx_ex_hedge_pp", "gross_ex_hedge")],
                   ignore_index=True)
    write(hr, "09_hypothesis_horse_race_loo.csv")
    pf = stages.pit_forecasts(d)
    write(pf, "09b_pit_expanding_window_forecasts.csv")
    sc = stages.score_pit(pf)
    write(sc, "09c_pit_window_scores.csv")

    # full-sample-prior replay: same PIT drivers, full-sample weights.
    # FIX r2: the point forecast is now recomputed from the full-sample coefficients
    # (previously only sigma was overwritten, so the two replays were the same forecast).
    full_coef = stages.full_sample_coefficients(d)
    pf_full = stages.pit_forecasts(d, coef_override=full_coef)
    write(pf_full, "09d_pit_forecasts_full_sample_prior.csv")
    sc_full = stages.score_pit(pf_full)
    write(sc_full, "09e_pit_window_scores_full_sample_prior.csv")
    rd = stages.replay_delta(pf, pf_full, sc, sc_full)
    write(rd, "09f_replay_delta_pit_vs_full.csv")
    # REGRESSION GUARD for the round-1 bug: the two replays must be distinct
    # forecasts, not one forecast with a relabelled band.
    assert len(pf_full) == len(pf), "replay row counts must match"
    assert float(rd["max_abs_point_delta"].max()) > 1e-6, \
        "full-sample-prior replay is identical to the PIT replay -- the round-1 bug is back"
    print(f"   replay check: max |point delta| = {rd['max_abs_point_delta'].max():.4f}pp, "
          f"{int(rd['n_rows_point_identical'].sum())} of {len(pf)} rows identical")

    # PIT caveats, machine-readable (verifier item 2)
    l0 = pd.read_csv(L0 / "L0_exact_regional_revenue.csv")
    cav = pd.DataFrame([
        {"item": "training_feature_basket_lags_not_vintage_stamped",
         "columns": "b_lag1,b_lag2,b_lag3,eur_lag1,eur_lag2,adrfx_lag1,adrfx_lag2",
         "detail": "baskets.regional_revenue_weights() uses the current-vintage L0 "
                   "regional revenue split with no knowable_from filter; the target "
                   "quarter's own lag-0 basket (pit_fx.regional_shares_asof) IS filtered",
         "l0_basis_values": ",".join(sorted(map(str, l0["basis"].unique()))),
         "l0_restated_rows": int((l0["basis"].astype(str)
                                  .str.contains("restat|derived", case=False)).sum()),
         "severity": "low: FRED spot never revises and L0 carries no restated rows",
         "resolution": "documented, not fixed"},
        {"item": "gross_ex_hedge_target_is_non_PIT_structural",
         "columns": "gross_fx_ex_hedge_pp",
         "detail": "built from 10-Q hedge reclassification filed AFTER the guide date; "
                   "used for the structural Object-A fit only, never registered",
         "l0_basis_values": "", "l0_restated_rows": 0,
         "severity": "labelled, not a leak",
         "resolution": "every registered object uses the PIT-clean stated letter series"},
        {"item": "daily_FRED_FX_ends_2026-08-28",
         "columns": "b_lag0 (live), forward schedule",
         "detail": "nothing in this package is genuinely as of 2026-09-11",
         "l0_basis_values": "", "l0_restated_rows": 0,
         "severity": "medium for the LIVE objects", "resolution": "stated everywhere"},
    ])
    write(cav, "00_pit_caveats.csv")

    print("[8/9] determined share, forward schedule, reconciliation, hedges")
    a_hat = np.array([resG["a0_hat"], resG["a1_hat"], resG["a2_hat"]])
    ds = stages.determined_share(resG["cs_w0_lo"], resG["cs_w0_hi"], resG["w0_hat"])
    fwd = stages.forward_schedule(a_hat, resG["sigma_hat"])
    kc = stages.kernel_carried_fx(d, a_hat)
    acc = stages.exfx_acceleration(d, kc)
    rec = stages.four_way_reconciliation(kc[kc["reading"].str.startswith("C_")].iloc[0])
    hx = stages.hedge_exhibit()

    print("[9/9] registry")
    objs = registry_out.emit(pf, pf_full, a_hat, resG["sigma_hat"],
                             fwd, int(resG["n"]), written)

    summary = {
        "run_date": TODAY.isoformat(),
        "object_a_gross": resG, "object_a_stated": resS,
        "registry_objects": objs,
        "free_parameter_counts": {"object_A_free_weights": 4, "H2_phi": 2,
                                  "H0_contemporaneous": 2, "H1_repo_eur": 3,
                                  "object_B_wedge": 5, "object_C_falsification": 3},
    }
    (OUT / "00_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print("wrote 00_summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
