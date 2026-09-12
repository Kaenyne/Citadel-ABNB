"""fx_lag_v2 / run.py -- entry point for the B4 FX exhibit.  Exit code 0 on success.

    cd "<repo>"
    python \
        analysis/src/forecast_methods/fx_lag_v2/fetch_fx_v2.py       # refresh first
    python \
        analysis/src/forecast_methods/fx_lag_v2/run.py

Writes ONLY to data/processed/forecast_methods/fx_lag_v2/ and to the two NEW
registry files fx-lag-v2__*.csv.  Nothing under analysis/src/{overnight,fx_lag},
data/processed/overnight, data/processed/forecast_methods/fx_lag or docs/ is
modified, and harness/score.py is not run.
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

import baskets, panel, fits, stages, exhibit, registry_out
from common import OUT, FX_DAILY, FX_LAST_OBS, TODAY, write, to_period


def main() -> int:
    written = []
    assert FX_DAILY.exists(), f"run fetch_fx_v2.py first: {FX_DAILY} missing"

    print("[1/8] baskets, rebuilt on the 2026-09-11 FX refresh")
    baskets.build()
    print("[2/8] analysis panel")
    d = panel.build()

    print("[3/8] Object A: joint interval-likelihood lag regression + confidence set")
    resG, varG, packG = fits.object_a(d, "gross_fx_ex_hedge_pp", "gross_ex_hedge")
    resS, varS, packS = fits.object_a(d, "stated_revenue_fx_pp", "stated")
    write(pd.DataFrame([resG, resS]), "06_object_a_summary.csv")
    write(pd.concat([varG.assign(target="gross_ex_hedge"),
                     varS.assign(target="stated")], ignore_index=True),
          "06b_object_a_hypothesis_tests.csv")
    a_gross = np.array([resG["a0_hat"], resG["a1_hat"], resG["a2_hat"]])
    a_stated = np.array([resS["a0_hat"], resS["a1_hat"], resS["a2_hat"]])
    CS_gross, CS_stated = packG[7], packS[7]
    s_phi_g = float(varG[varG["hypothesis"] == "H0e_phi_free_scale"]["scale"].iloc[0])
    s_phi_s = float(varS[varS["hypothesis"] == "H0e_phi_free_scale"]["scale"].iloc[0])
    print(f"   free fit  stated a={a_stated}  scale={a_stated.sum():.3f}  "
          f"eff.lag={resS['eff_lag_hat_q']:.2f}q  sigma={resS['sigma_hat']:.3f}")
    print(f"   free fit  gross  a={a_gross}  scale={a_gross.sum():.3f}  "
          f"eff.lag={resG['eff_lag_hat_q']:.2f}q  sigma={resG['sigma_hat']:.3f}")
    print(f"   Phi-shape free scale: stated {s_phi_s:.3f}, gross {s_phi_g:.3f}")

    print("[4/8] PIT expanding window (H2 rows for the registry) + full-sample replay")
    pf = stages.pit_forecasts(d)
    write(pf, "09b_pit_expanding_window_forecasts.csv")
    sc = stages.score_pit(pf)
    write(sc, "09c_pit_window_scores.csv")
    full_coef = stages.full_sample_coefficients(d)
    pf_full = stages.pit_forecasts(d, coef_override=full_coef)
    write(pf_full, "09d_pit_forecasts_full_sample_prior.csv")
    sc_full = stages.score_pit(pf_full)
    write(sc_full, "09e_pit_window_scores_full_sample_prior.csv")
    rd = stages.replay_delta(pf, pf_full, sc, sc_full)
    write(rd, "09f_replay_delta_pit_vs_full.csv")
    assert float(rd["max_abs_point_delta"].max()) > 1e-6, \
        "full-sample replay is identical to the PIT replay"

    print("[5/8] B4 exhibits")
    # contemporaneous ADR-FX fit, used to extend the disclosed ADR-FX series forward
    sub = d[(d["p"] >= to_period("1Q23")) & (d["p"] <= to_period("2Q26"))] \
        .dropna(subset=["fx_pts_adr", "b_lag0"])
    o = fits.ols(sub["b_lag0"], sub["fx_pts_adr"])
    adr_slope, adr_int = float(o["slope"]), float(o["intercept"])
    print(f"   ADR-FX on the contemporaneous basket: slope {adr_slope:.3f}, "
          f"intercept {adr_int:.3f}, r {o['r']:.3f}")

    b_now = exhibit.baskets_asof(FX_LAST_OBS)
    write(pd.DataFrame([{"quarter": q,
                         **{k: (round(v, 4) if isinstance(v, (int, float)) else v)
                            for k, v in vv.items()}}
                        for q, vv in b_now.items()]), "19_baskets_spot_held_v2.csv")
    obs = exhibit.observed_share(a_stated, a_gross, CS_stated, CS_gross)
    live = exhibit.live_3q26(b_now, a_gross, a_stated, s_phi_s, s_phi_g,
                             resS["sigma_hat"], resG["sigma_hat"])
    hedge = exhibit.hedge_line()
    fc, ann = exhibit.forecast_4q26(a_stated, resS["sigma_hat"], s_phi_s,
                                    CS_stated, adr_slope, adr_int)
    q4, fy = exhibit.four_way(fc, ann)
    kc = exhibit.kernel_carried(d, b_now, a_stated, s_phi_s, adr_slope, adr_int)
    ex = exhibit.exfx(d, kc)

    print("[6/8] PIT caveats")
    cav = pd.DataFrame([
        {"item": "fred_h10_publication_lag",
         "detail": f"the 2026-09-11 refresh reaches {FX_LAST_OBS}; FRED H.10 publishes "
                   "weekly, so 'as of today' means FX through 2026-09-04",
         "severity": "low (5 business days)", "resolution": "stated on every table"},
        {"item": "gross_ex_hedge_target_is_non_PIT_structural",
         "detail": "built from the 10-Q hedge reclassification, filed after the guide; "
                   "used for the structural fit only, never registered",
         "severity": "labelled, not a leak",
         "resolution": "the registered objects use the stated letter series"},
        {"item": "training_feature_basket_lags_not_vintage_stamped",
         "detail": "inherited from fx_lag: baskets.regional_revenue_weights() uses the "
                   "current-vintage L0 split for historical quarters; the target "
                   "quarter's own lag-0 basket IS vintage-filtered",
         "severity": "low: FRED spot never revises, L0 carries no restated rows",
         "resolution": "documented, not fixed"},
        {"item": "holiday_fill_fixed_in_v2",
         "detail": "fx_lag/pit_fx filled every business day with no FRED print -- bank "
                   "holidays inside completed quarters included -- with the CURRENT "
                   "spot; v2 uses the last rate observed on or before the day, and "
                   "holds spot only after the last observation",
         "severity": "fixed", "resolution": "see pit_fx._q_avg_spot_held"},
    ])
    write(cav, "00_pit_caveats.csv")

    print("[7/8] registry (NEW files only, method fx-lag-v2)")
    sh = fc[fc["path"] == "spot_held"].set_index("quarter")
    live_point = float(sh.loc["4Q26", "point_phi_basket_scale_0.851_pp"])
    live_alt = float(sh.loc["4Q26", "point_phi_basket_fitted_scale_pp"])
    cs_lo = float(sh.loc["4Q26", "cs_interval_lo_pp"])
    cs_hi = float(sh.loc["4Q26", "cs_interval_hi_pp"])
    objs = registry_out.emit(
        pf, pf_full, live_point, float(resS["sigma_hat"]), cs_lo, cs_hi,
        int(resS["n"]),
        "H2_phi_kernel_on_basket_scale_0.851_spot_held_2026-09-04", written)
    print(f"   live 4Q26: adopted {live_point:+.2f}pp (Phi x 0.851); "
          f"Phi x fitted shape-scale {s_phi_s:.3f} gives {live_alt:+.2f}pp; "
          f"CS interval {cs_lo:+.2f} to {cs_hi:+.2f}pp")

    print("[8/8] summary")
    summary = {
        "run_date": TODAY.isoformat(), "fx_data_through": FX_LAST_OBS.isoformat(),
        "object_a_gross": resG, "object_a_stated": resS,
        "phi_shape_free_scale": {"stated": s_phi_s, "gross": s_phi_g},
        "adr_fx_contemporaneous_fit": {"slope": adr_slope, "intercept": adr_int,
                                       "r": float(o["r"])},
        "live_3q26_pp": {
            "free_fit_stated": round(float(a_stated @ np.array(
                [b_now["3Q26"]["global_pct"], b_now["2Q26"]["global_pct"],
                 b_now["1Q26"]["global_pct"]])), 2),
            "free_fit_gross": round(float(a_gross @ np.array(
                [b_now["3Q26"]["global_pct"], b_now["2Q26"]["global_pct"],
                 b_now["1Q26"]["global_pct"]])), 2),
            "phi_x_0.851": round(float(0.851 * ((2 / 3) * b_now["2Q26"]["global_pct"]
                                                + (1 / 3) * b_now["1Q26"]["global_pct"])), 2),
            "management_stated_after_hedging": 3.0},
        "live_4q26_pp": {"point_phi_0.851": live_point,
                         "point_phi_fitted_shape_scale": live_alt,
                         "cs_lo": cs_lo, "cs_hi": cs_hi},
        "registry_objects": objs, "files_written": written,
    }
    (OUT / "00_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print("wrote 00_summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
