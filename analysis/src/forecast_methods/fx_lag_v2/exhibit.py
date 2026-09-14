"""fx_lag_v2 / exhibit.py -- the B4 FX exhibit.

NEW module (not a copy).  Everything B4 asks for that fx_lag did not produce:

  20  observed / already-determined share of each quarter's revenue-FX term, as a
      TRIPLE (free fit | Phi kernel | contemporaneous) at four decision dates,
      with the volume-determined share alongside
  21  the live 3Q26 three-number table (ours, Phi at scale 0.851, management)
  22  the hedge line, gross vs after-hedge, shown ONCE
  23  the 4Q26 forecast under the lag-loaded spec: point, confidence-set interval,
      predictive band, spot-held and +/-1sd USD paths
  24  the four-way (five-row) reconciliation for 4Q26
  25  the same for FY27
  26  ex-FX acceleration at the frozen card GBV and at $26,550M
  27  booking-date FX carried through Phi, recomputed on the refresh

Every FX pp is an OUTPUT of the lagged-GBV arithmetic.  Nothing here is added to a
revenue forecast, and 28_fx_hedge_forward.csv is never added on top of a
letter-stated (already after-hedge) FX point.
"""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pandas as pd

import pit_fx
from common import OVN, OUT, FX_LAST_OBS, TODAY, to_period, short, write
from fits import ols

PHI = np.array([0.0, 2.0 / 3.0, 1.0 / 3.0])      # the architect's kernel weights
NON_USD = 0.56                                    # disclosed non-USD revenue share
RT_SCALE = 0.851                                  # RED_TEAM / fx-lag fitted stated scale
REV_4Q25 = 2778.0                                 # $m, the 4Q26 y/y denominator
H10_LAG_DAYS = 7                                  # FRED H.10 publication lag

# decision dates -> (target quarter, what)
DATES = [
    ("2026-08-06", "3Q26", "3Q26 guide date (2Q26 letter)"),
    ("2026-09-11", "3Q26", "today (this build)"),
    ("2026-10-02", "4Q26", "memo / pitch date"),
    ("2026-11-05", "4Q26", "4Q26 guide date (3Q26 print)"),
    ("2027-02-11", "1Q27", "1Q27 + FY27 guide date (4Q26 print)"),
]
# GBV print dates, for the volume-determined share
GBV_PRINTS = {"1Q26": _dt.date(2026, 5, 7), "2Q26": _dt.date(2026, 8, 6),
              "3Q26": _dt.date(2026, 11, 5), "4Q26": _dt.date(2027, 2, 11),
              "1Q27": _dt.date(2027, 5, 6)}


# --------------------------------------------------------------- basket helper
def baskets_asof(asof: _dt.date, shift_pct: float = 0.0,
                 quarters=("1Q26", "2Q26", "3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27")
                 ) -> dict:
    """Global revenue-weighted basket y/y for each quarter, actuals through `asof`
    and spot held constant after it.  `shift_pct` shifts only the held spot, so
    quarters that are already complete are unaffected by the scenario.

    A COMPLETED quarter takes its value from 02_basket_quarterly.csv -- the same
    series the Object-A weights were fitted on -- rather than from the business-day
    reconstruction, so the weights are applied to exactly the inputs they were
    estimated against.  The two differ by under 0.04pp; using one everywhere removes
    an avoidable inconsistency rather than a material error."""
    hist = pd.read_csv(OUT / "02_basket_quarterly.csv").set_index("quarter")
    out = {}
    for q in quarters:
        p = to_period(q)
        complete = p.end_time.date() <= asof
        sh = 0.0 if complete else shift_pct
        r = pit_fx.basket_yoy_asof(p, asof, hold_shift_pct=sh)
        g = r["global_pct"]
        src = "pit_reconstruction"
        if complete and q in hist.index and pd.notna(hist.loc[q, "basket_global_rev_wtd_yoy_pct"]):
            g = float(hist.loc[q, "basket_global_rev_wtd_yoy_pct"])
            src = "02_basket_quarterly (completed quarter, as fitted)"
        out[q] = {"global_pct": g, "obs_frac": r["elapsed_frac"], "source": src,
                  **{k: r[k] for k in ("na", "emea", "latam", "apac")}}
    return out


def _obs_frac(q: str, through: _dt.date) -> float:
    """Share of the quarter's business days for which a FRED print exists (or, for a
    date in the future, will exist) once data through `through` is published.

    For `through` <= the refresh we count REAL prints, so US bank holidays are
    excluded correctly.  Beyond it we count business days, which overstates the
    numerator by the two or three holidays in a quarter -- stated, not hidden."""
    p = to_period(q)
    if through <= FX_LAST_OBS:
        return pit_fx.basket_yoy_asof(p, through)["elapsed_frac"]
    days = pd.bdate_range(p.start_time.date(), p.end_time.date())
    n = sum(1 for d in days if d.date() <= through)
    return n / len(days)


# ------------------------------------------------- 20: the determined-share triple
def observed_share(a_free_stated, a_free_gross, cs_stated, cs_gross) -> pd.DataFrame:
    """FX-determined share = w1 + w2 + w0 * f, f = share of the target quarter that
    is already in the average.  Reported for THREE specifications, never one:

      (a) free fit        w = a/sum(a) from Object A   (both targets; CS band)
      (b) Phi kernel      w = (0, 2/3, 1/3)            -> 1.00 at every date
      (c) contemporaneous w = (1, 0, 0)                -> f

    Two readings of f: calendar days elapsed (the convention the programme already
    uses, and the one that reproduces M6's 0.54) and FRED business days actually
    printed (what a forecaster can really see, given the H.10 publication lag).
    The volume-determined share of the kernel GBV base sits alongside.
    """
    w_free_s = a_free_stated / a_free_stated.sum()
    w_free_g = a_free_gross / a_free_gross.sum()
    w0_lo = float(min((cs_gross.sum(axis=1) > 0).astype(float).min(), 1))  # placeholder
    sg = cs_gross[cs_gross.sum(axis=1) > 1e-9]
    w0_g = sg[:, 0] / sg.sum(axis=1)
    ss = cs_stated[cs_stated.sum(axis=1) > 1e-9]
    w0_s = ss[:, 0] / ss.sum(axis=1)
    del w0_lo

    rows = []
    for ds, tq, what in DATES:
        dte = _dt.date.fromisoformat(ds)
        p = to_period(tq)
        qs, qe = p.start_time.date(), p.end_time.date()
        ndays = (qe - qs).days + 1
        elapsed = min(max((dte - qs).days, 0), ndays)
        f_cal = elapsed / ndays
        # data-observed: FRED prints through dte - H10 lag, capped at the refresh
        # what FRED will have published by `dte`: H.10 runs about a week behind, and
        # for dates at or before today it cannot reach past the refresh itself
        data_through = (dte - _dt.timedelta(days=H10_LAG_DAYS) if dte > TODAY
                        else min(dte - _dt.timedelta(days=1), FX_LAST_OBS))
        f_obs = _obs_frac(tq, data_through) if data_through >= qs else 0.0
        # volume-determined: kernel base = 2/3 GBV(q-1) + 1/3 GBV(q-2)
        k1 = GBV_PRINTS.get(short(p - 1), _dt.date(2100, 1, 1)) <= dte
        k2 = GBV_PRINTS.get(short(p - 2), _dt.date(2100, 1, 1)) <= dte
        vol = (2.0 / 3.0) * k1 + (1.0 / 3.0) * k2

        def det(w0, f):
            return (1.0 - w0) + w0 * f

        specs = [
            ("a_free_fit_stated", float(w_free_s[0]),
             float(det(np.min(w0_s), f_cal)), float(det(np.max(w0_s), f_cal))),
            ("a_free_fit_gross", float(w_free_g[0]),
             float(det(np.min(w0_g), f_cal)), float(det(np.max(w0_g), f_cal))),
            ("b_phi_kernel_0_23_13", 0.0, 1.0, 1.0),
            ("c_contemporaneous", 1.0, f_cal, f_cal),
        ]
        for name, w0, lo, hi in specs:
            rows.append({
                "as_of": ds, "what": what, "target_quarter": tq, "spec": name,
                "w0": round(w0, 4),
                "days_elapsed": elapsed, "days_in_quarter": ndays,
                "elapsed_frac_calendar": round(f_cal, 4),
                "observed_frac_fred_prints": round(f_obs, 4),
                "fred_data_through": data_through.isoformat(),
                "fx_determined_share_calendar": round(det(w0, f_cal), 4),
                "fx_determined_share_fred_observed": round(det(w0, f_obs), 4),
                "fx_determined_share_cs_lo": round(min(lo, hi), 4),
                "fx_determined_share_cs_hi": round(max(lo, hi), 4),
                "volume_determined_share": round(vol, 4),
            })
    out = pd.DataFrame(rows)
    write(out, "20_observed_share_triple.csv")
    return out


# ------------------------------------------------------ 21: the live 3Q26 exhibit
def live_3q26(b: dict, a_gross, a_stated, s_phi_stated, s_phi_gross,
              sigma_stated, sigma_gross) -> pd.DataFrame:
    """One table, three live numbers for 3Q26 revenue FX, plus the constructions
    that bracket them.  Management's ~+3pp is AFTER hedging; ours are gross unless
    the row says otherwise, and the hedge is applied ONCE, in 22_."""
    lags = np.array([b["3Q26"]["global_pct"], b["2Q26"]["global_pct"],
                     b["1Q26"]["global_pct"]])
    phi_drv = float(PHI @ lags)          # 2/3 * b(2Q26) + 1/3 * b(1Q26)
    rows = [
        {"construction": "ours: Object-A free fit, STATED series (PIT-clean)",
         "weights": f"({a_stated[0]:.2f}, {a_stated[1]:.2f}, {a_stated[2]:.2f})",
         "basis": "after-hedge (stated) target",
         "fx_3Q26_pp": round(float(a_stated @ lags), 2),
         "band_80_lo": round(float(a_stated @ lags) - 1.2816 * sigma_stated, 2),
         "band_80_hi": round(float(a_stated @ lags) + 1.2816 * sigma_stated, 2)},
        {"construction": "ours as registered by fx-lag: free fit, GROSS weights",
         "weights": f"({a_gross[0]:.2f}, {a_gross[1]:.2f}, {a_gross[2]:.2f})",
         "basis": "gross of hedge",
         "fx_3Q26_pp": round(float(a_gross @ lags), 2),
         "band_80_lo": round(float(a_gross @ lags) - 1.2816 * sigma_gross, 2),
         "band_80_hi": round(float(a_gross @ lags) + 1.2816 * sigma_gross, 2)},
        {"construction": "Phi kernel (0, 2/3, 1/3) x 0.851 (free-fit stated scale)",
         "weights": "(0, 0.567, 0.284)", "basis": "after-hedge (stated) target",
         "fx_3Q26_pp": round(RT_SCALE * phi_drv, 2),
         "band_80_lo": round(RT_SCALE * phi_drv - 1.2816 * sigma_stated, 2),
         "band_80_hi": round(RT_SCALE * phi_drv + 1.2816 * sigma_stated, 2)},
        {"construction": f"Phi kernel x {s_phi_stated:.3f} (scale fitted TO the Phi shape, stated)",
         "weights": f"(0, {2*s_phi_stated/3:.3f}, {s_phi_stated/3:.3f})",
         "basis": "after-hedge (stated) target",
         "fx_3Q26_pp": round(s_phi_stated * phi_drv, 2),
         "band_80_lo": np.nan, "band_80_hi": np.nan},
        {"construction": f"Phi kernel x {s_phi_gross:.3f} (scale fitted TO the Phi shape, gross)",
         "weights": f"(0, {2*s_phi_gross/3:.3f}, {s_phi_gross/3:.3f})",
         "basis": "gross of hedge",
         "fx_3Q26_pp": round(s_phi_gross * phi_drv, 2),
         "band_80_lo": np.nan, "band_80_hi": np.nan},
        {"construction": "Phi kernel x 0.56 (architect's literal H0, disclosed non-USD share)",
         "weights": "(0, 0.373, 0.187)", "basis": "gross of hedge",
         "fx_3Q26_pp": round(NON_USD * phi_drv, 2),
         "band_80_lo": np.nan, "band_80_hi": np.nan},
        {"construction": "contemporaneous x 0.56",
         "weights": "(0.56, 0, 0)", "basis": "gross of hedge",
         "fx_3Q26_pp": round(NON_USD * lags[0], 2),
         "band_80_lo": np.nan, "band_80_hi": np.nan},
        {"construction": "MANAGEMENT, 6 Aug 2026 letter: 'approximately three "
                         "percentage points of FX tailwind after factoring in our "
                         "hedging program'",
         "weights": "n/a", "basis": "AFTER hedging, as stated",
         "fx_3Q26_pp": 3.0, "band_80_lo": np.nan, "band_80_hi": np.nan},
        {"construction": "MANAGEMENT implied GROSS (stated + 0.21pp hedge drag, "
                         "28_fx_hedge_forward 3Q26)",
         "weights": "n/a", "basis": "gross of hedge (derived, hedge applied ONCE)",
         "fx_3Q26_pp": 3.21, "band_80_lo": np.nan, "band_80_hi": np.nan},
    ]
    out = pd.DataFrame(rows)
    out["basket_3Q26_pct"] = round(float(lags[0]), 3)
    out["basket_2Q26_pct"] = round(float(lags[1]), 3)
    out["basket_1Q26_pct"] = round(float(lags[2]), 3)
    out["phi_driver_pct"] = round(phi_drv, 3)
    out["fx_data_through"] = FX_LAST_OBS.isoformat()
    out["hedge_rule"] = ("hedges enter ONCE: the letter-stated pp is already after "
                         "hedging; 28_fx_hedge_forward.csv is applied only to a GROSS "
                         "number, never on top of a stated one")
    write(out, "21_live_3q26_three_numbers.csv")
    return out


# ------------------------------------------------------------- 22: the hedge line
def hedge_line() -> pd.DataFrame:
    h = pd.read_csv(OVN / "28_fx_hedge_disclosures.csv")
    keep = ["quarter", "designated_notional_musd", "reclassified_to_revenue_musd",
            "hedge_effect_on_revenue_growth_pp", "stated_revenue_fx_pp",
            "gross_fx_ex_hedge_pp", "expected_reclass_next_12m_musd",
            "non_usd_revenue_share", "designated_notional_pct_of_ltm_non_usd_revenue"]
    out = h[keep].copy()
    out["identity_gross_plus_hedge_equals_stated"] = (
        (out["gross_fx_ex_hedge_pp"] + out["hedge_effect_on_revenue_growth_pp"]
         - out["stated_revenue_fx_pp"]).abs() < 1e-6)
    fwd = pd.read_csv(OVN / "28_fx_hedge_forward.csv")
    fwd = fwd.rename(columns={"hedge_effect_on_revenue_growth_pp": "forward_hedge_pp"})
    out = pd.concat([out, fwd[["quarter", "forward_hedge_pp"]].assign(
        stated_revenue_fx_pp=np.nan, gross_fx_ex_hedge_pp=np.nan)], ignore_index=True)
    out["hedge_once_rule"] = ("the letter-stated revenue-FX pp is ALREADY AFTER "
                              "hedges; the forward hedge schedule is applied ONCE and "
                              "only to a gross projection")
    write(out, "22_hedge_gross_vs_after.csv")
    return out


# ------------------------------------------------------- 23: the 4Q26 forecast
def forecast_4q26(a_stated, sigma_stated, s_phi_stated, cs_stated,
                  adr_slope, adr_intercept) -> pd.DataFrame:
    """The forecast rule for the GUIDE.  Management sets the 5 Nov Q4 guide from an
    information set in which 4Q26's own quarter has barely started, so the spec that
    forecasts what they will SAY is the lag-loaded one (H2 / Phi), not the free fit.

    Point = Phi kernel on the rebuilt basket at the fitted scale.
    Interval = every weight vector in the Object-A 95% confidence set pushed through
               the same forward baskets (parameter uncertainty), reported alongside
               the predictive 80% band from the fitted sigma.
    Paths  = spot held constant from the last FRED print, and +/-5% parallel shifts
             (about one standard deviation of a two-quarter dollar move).
    """
    rows = []
    css = cs_stated[cs_stated.sum(axis=1) > 1e-9]
    for path, shift in [("spot_held", 0.0), ("usd_weak_+1sd", +5.0),
                        ("usd_strong_-1sd", -5.0)]:
        b = baskets_asof(FX_LAST_OBS, shift_pct=shift)
        for q in ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]:
            p = to_period(q)
            lags = np.array([b[q]["global_pct"], b[short(p - 1)]["global_pct"],
                             b[short(p - 2)]["global_pct"]])
            phi_drv = float(PHI @ lags)
            # H2 on ADR-FX: the disclosed ADR-FX point is contemporaneous at booking,
            # so it is extended forward with the contemporaneous ADR fit on the basket
            adr_l1 = adr_intercept + adr_slope * lags[1]
            adr_l2 = adr_intercept + adr_slope * lags[2]
            phi_adr = (2.0 / 3.0) * adr_l1 + (1.0 / 3.0) * adr_l2
            cs_vals = css @ lags
            rows.append({
                "path": path, "quarter": q,
                "basket_lag0_pct": round(lags[0], 3),
                "basket_lag1_pct": round(lags[1], 3),
                "basket_lag2_pct": round(lags[2], 3),
                "phi_driver_pct": round(phi_drv, 3),
                "point_phi_basket_fitted_scale_pp": round(s_phi_stated * phi_drv, 2),
                "point_phi_basket_scale_0.851_pp": round(RT_SCALE * phi_drv, 2),
                "point_phi_adrfx_pp": round(phi_adr, 2),
                "point_free_fit_stated_pp": round(float(a_stated @ lags), 2),
                "cs_interval_lo_pp": round(float(np.min(cs_vals)), 2),
                "cs_interval_hi_pp": round(float(np.max(cs_vals)), 2),
                "cs_interval_p05_pp": round(float(np.percentile(cs_vals, 5)), 2),
                "cs_interval_p95_pp": round(float(np.percentile(cs_vals, 95)), 2),
                "band80_lo_pp": round(s_phi_stated * phi_drv - 1.2816 * sigma_stated, 2),
                "band80_hi_pp": round(s_phi_stated * phi_drv + 1.2816 * sigma_stated, 2),
            })
    out = pd.DataFrame(rows)
    out["fx_data_through"] = FX_LAST_OBS.isoformat()
    out["note"] = ("point = Phi kernel (0, 2/3, 1/3) at the scale fitted to the Phi "
                   "shape on the stated series; interval = the Object-A 95% "
                   "confidence set pushed through the same baskets")
    write(out, "23_forecast_4q26_v2.csv")

    # FY27 annualisation: the revenue-weighted AVERAGE of four quarters, never the sum
    kp = pd.read_csv(OVN / "02_kpi_panel_quarterly.csv").set_index("quarter")["revenue_musd"]
    w = np.array([float(kp[f"{i}Q25"]) for i in range(1, 5)]); w = w / w.sum()
    arows = []
    for path in out["path"].unique():
        sub = out[out["path"] == path].set_index("quarter")
        for col, lab in [("point_phi_basket_fitted_scale_pp", "phi_fitted_scale"),
                         ("point_phi_basket_scale_0.851_pp", "phi_scale_0.851"),
                         ("point_free_fit_stated_pp", "free_fit_stated"),
                         ("cs_interval_lo_pp", "cs_lo"), ("cs_interval_hi_pp", "cs_hi")]:
            v = np.array([float(sub.loc[q, col]) for q in ["1Q27", "2Q27", "3Q27", "4Q27"]])
            arows.append({"path": path, "spec": lab,
                          "q1_pp": v[0], "q2_pp": v[1], "q3_pp": v[2], "q4_pp": v[3],
                          "sum_of_four_quarters_pp_DO_NOT_QUOTE": round(float(v.sum()), 2),
                          "simple_average_pp": round(float(v.mean()), 2),
                          "revenue_weighted_average_pp": round(float(w @ v), 2)})
    ann = pd.DataFrame(arows)
    ann["rule"] = "an FY y/y FX contribution is the revenue-weighted AVERAGE of its four quarters"
    write(ann, "23b_fy27_annualisation_v2.csv")
    return out, ann


# ------------------------------------------------ 24 / 25: four-way reconciliation
def four_way(fc: pd.DataFrame, ann: pd.DataFrame) -> tuple:
    sched = pd.read_csv(OVN / "05_fx_schedule.csv")
    cons = sched[sched["path"] == "consensus"].set_index("quarter")
    repo_4q = float(cons.loc["2026Q4", "revenue_fx_fit_pp"])
    kp = pd.read_csv(OVN / "02_kpi_panel_quarterly.csv").set_index("quarter")["revenue_musd"]
    w = np.array([float(kp[f"{i}Q25"]) for i in range(1, 5)]); w = w / w.sum()
    repo_fy27 = float(w @ np.array([float(cons.loc[f"2027Q{i}", "revenue_fx_fit_pp"])
                                    for i in range(1, 5)]))

    sh = fc[(fc["path"] == "spot_held")].set_index("quarter")
    # ADOPTED = the Phi shape at scale 0.851 (the free fit's own total scale, the
    # construction RED_TEAM F4 validated on the three live quarters).  The scale
    # fitted to the Phi shape ALONE is 0.653 and gives 0.22pp less; both are carried
    # in 23_forecast_4q26_v2.csv and the difference is inside every band quoted.
    adopted_4q = float(sh.loc["4Q26", "point_phi_basket_scale_0.851_pp"])
    adopted_4q_alt = float(sh.loc["4Q26", "point_phi_basket_fitted_scale_pp"])
    adopted_lo = float(sh.loc["4Q26", "cs_interval_lo_pp"])
    adopted_hi = float(sh.loc["4Q26", "cs_interval_hi_pp"])
    adopted_fy27 = float(ann[(ann["path"] == "spot_held")
                             & (ann["spec"] == "phi_scale_0.851")]["revenue_weighted_average_pp"].iloc[0])
    adopted_fy27_alt = float(ann[(ann["path"] == "spot_held")
                                 & (ann["spec"] == "phi_fitted_scale")]["revenue_weighted_average_pp"].iloc[0])

    # M6's own rule (two-index, lambda = 0.75) reconstructed on the refreshed basket,
    # labelled as OUR reconstruction -- the M6 forward table stops at 2Q27.
    def m6(q):
        p = to_period(q)
        l0 = float(sh.loc[q, "basket_lag0_pct"]); l1 = float(sh.loc[q, "basket_lag1_pct"])
        l2 = float(sh.loc[q, "basket_lag2_pct"])
        return NON_USD * (0.75 * l0 + 0.25 * ((2 / 3) * l1 + (1 / 3) * l2))
    m6_fy27 = float(w @ np.array([m6(f"{i}Q27") for i in range(1, 5)]))

    def block(label, level, step, status, cause, base_rev, adopted):
        return {"construction": label, "fx_level_pp": round(level, 2)
                if level is not None else np.nan,
                "step_applied_in_a_walk_pp": round(step, 2) if step is not None else np.nan,
                "status": status, "named_cause": cause,
                "delta_vs_adopted_pp": round(level - adopted, 2) if level is not None else np.nan,
                "dollar_impact_vs_adopted_musd":
                    round((level - adopted) * base_rev / 100.0, 0) if level is not None else np.nan}

    q4 = pd.DataFrame([
        block("repo 29_q4_fy27_bridge FX step", repo_4q, -3.4, "REJECTED as an input",
              "the level it carries is the 05_fx_schedule fit (-0.4pp); the -3.4pp is that "
              "level SUBTRACTED from a guide-anchored walk whose 3Q26 start already contains "
              "management's +3.0pp of FX, and from a GBV base that already carries booking-date "
              "FX -- the double subtraction the architect ruled out", REV_4Q25, adopted_4q),
        block("repo 05_fx_schedule revenue_fx_fit_pp (consensus path)", repo_4q, None,
              "REJECTED as an input",
              "a reduced-form level fit of stated revenue FX on a lagged EURUSD / broad-USD "
              "blend; EURUSD is not the basket (EUR y/y rolled from +11.1 in 1Q26 to -1.5 in "
              "3Q26 while LatAm held the basket up), and it re-applies a lag already inside "
              "the lagged GBV base", REV_4Q25, adopted_4q),
        block("M6 memo forward schedule (after hedge; +0.62 gross)", 0.41, None,
              "REJECTED as an input",
              "a contemporaneous two-index construction (lambda = 0.75) that misses a nearly "
              "observed 3Q26 by about 2pp; M6's own note carries +1.04pp in its schedule "
              "against +0.73pp in its 3Q26 build", REV_4Q25, adopted_4q),
        block("guide-anchored (hold management's stated 3Q26 +3.0pp flat)", 2.6, None,
              "REJECTED as an input",
              "holds the 3Q26 tailwind into 4Q26; the basket itself rolls over (1Q26 +5.7 -> "
              "2Q26 +2.3 -> 3Q26 ~+0.4), so flat imports a tailwind the spot path has already "
              "removed", REV_4Q25, adopted_4q),
        block("kernel-implied: Phi kernel x 0.851 on the refreshed basket, spot held "
              "(THIS package; Phi x the 0.653 shape-scale gives +0.75pp)", adopted_4q, 0.0,
              "ADOPTED, as an OUTPUT",
              "booking-date FX is already inside the lagged USD GBV base; the pp shown is what "
              "the kernel arithmetic produces and it is never added to, or subtracted from, a "
              "revenue forecast", REV_4Q25, adopted_4q),
    ])
    q4["adopted_alt_scale_0.653_pp"] = round(adopted_4q_alt, 2)
    q4["adopted_cs_interval_lo_pp"] = round(adopted_lo, 2)
    q4["adopted_cs_interval_hi_pp"] = round(adopted_hi, 2)
    lo, hi = q4["fx_level_pp"].min(), q4["fx_level_pp"].max()
    q4["level_spread_pp"] = round(float(hi - lo), 2)
    q4["level_spread_musd"] = round(float((hi - lo) * REV_4Q25 / 100.0), 0)
    q4["spread_including_the_bridge_step_pp"] = round(float(q4[["fx_level_pp",
                                                                "step_applied_in_a_walk_pp"]]
                                                           .max().max() - -3.4), 2)
    q4["spread_including_the_bridge_step_musd"] = round(
        float(q4["spread_including_the_bridge_step_pp"].iloc[0] * REV_4Q25 / 100.0), 0)
    q4["dollar_per_pp_musd"] = round(REV_4Q25 / 100.0, 2)
    write(q4, "24_four_way_4q26.csv")

    # ---- FY27.  1pp of FY27 growth = 1% of FY26 revenue.
    fy26 = 2678.0 + 3608.0 + 4816.0 + 3191.0     # 1H26 actual + 3Q26 (guide x cushion) + 4Q26 kernel
    fy = pd.DataFrame([
        block("repo 29 bridge FY27 (level -0.6pp on the consensus euro path; the walk "
              "subtracts -3.4pp)", -0.6, -3.4, "REJECTED as an input",
              "same double subtraction one year out: the -3.4pp step is taken off an FY26 base "
              "that already carries FY26's +2.7pp of stated FX, on top of a GBV base already in "
              "booking-date USD", fy26, adopted_fy27),
        block("repo 05_fx_schedule, revenue-weighted average of 1Q27-4Q27", repo_fy27, None,
              "REJECTED as an input",
              "the same EURUSD-only reduced form, annualised; it has FX turning materially "
              "negative through FY27 where the revenue-weighted basket only fades", fy26,
              adopted_fy27),
        block("M6 rule (lambda = 0.75 two-index) reconstructed on the refreshed basket "
              "-- OUR reconstruction, not an M6 number; the M6 table stops at 2Q27",
              m6_fy27, None, "REJECTED as an input",
              "contemporaneous-dominant weighting of a basket nobody can observe a year out; "
              "it is a spot forecast wearing a lag's clothes", fy26, adopted_fy27),
        block("guide-anchored (hold +3.0pp flat through FY27)", 3.0, None,
              "REJECTED as an input",
              "imports a 2026 dollar path into 2027; under spot held the basket y/y is near "
              "zero by 2Q27 by arithmetic, because the base quarters are themselves recent",
              fy26, adopted_fy27),
        block("kernel-implied: Phi kernel x 0.851, revenue-weighted average of four "
              "quarters (THIS package; the 0.653 shape-scale gives +0.40pp)", adopted_fy27,
              0.0, "ADOPTED, as an OUTPUT",
              "the FY27 y/y FX contribution is the revenue-weighted AVERAGE of four quarterly "
              "contributions, each an output of the lagged-GBV arithmetic; the SUM is meaningless",
              fy26, adopted_fy27),
    ])
    lo, hi = fy["fx_level_pp"].min(), fy["fx_level_pp"].max()
    fy["adopted_alt_scale_0.653_pp"] = round(adopted_fy27_alt, 2)
    fy["level_spread_pp"] = round(float(hi - lo), 2)
    fy["fy26_revenue_base_musd"] = round(fy26, 0)
    fy["dollar_per_pp_musd"] = round(fy26 / 100.0, 2)
    fy["level_spread_musd"] = round(float((hi - lo) * fy26 / 100.0), 0)
    write(fy, "25_four_way_fy27.csv")
    return q4, fy


# ----------------------------------------- 26 / 27: kernel-carried FX and ex-FX
def kernel_carried(d: pd.DataFrame, b: dict, a_stated, s_phi_stated,
                   adr_slope, adr_intercept) -> pd.DataFrame:
    bq = {r["quarter"]: r for _, r in d.iterrows()}
    basket = {q: b[q]["global_pct"] for q in ["1Q26", "2Q26", "3Q26", "4Q26"]}
    adr = {q: float(bq[q]["fx_pts_adr"]) for q in ["1Q26", "2Q26"]}
    adr["3Q26"] = adr_intercept + adr_slope * basket["3Q26"]
    rows = []
    for name, ser, note in [
        ("A_disclosed_ADR_FX_through_Phi", adr,
         "the architect's construction, recomputed from data; 3Q26 ADR-FX fitted from the basket"),
        ("B_basket_x_0.56_through_Phi", {k: NON_USD * v for k, v in basket.items()},
         "disclosed non-USD revenue share on the rebuilt basket"),
        ("C_Phi_x_0.851_free_fit_total_scale",
         {k: RT_SCALE * v for k, v in basket.items()},
         "Phi shape at 0.851, the free fit's own total scale -- the ADOPTED reading "
         "(RED_TEAM F4 validated this construction on 1Q26/2Q26/3Q26)"),
        (f"C2_Phi_x_fitted_shape_scale_{s_phi_stated:.3f}",
         {k: s_phi_stated * v for k, v in basket.items()},
         "Phi shape at the scale fitted to the Phi shape alone -- the low alternative"),
        ("D_objectA_free_weights_on_basket", None,
         "the free fit; loads on lag 0, so it is the wrong reading for a guide-date question"),
    ]:
        if ser is None:
            v3 = float(a_stated @ np.array([basket["3Q26"], basket["2Q26"], basket["1Q26"]]))
            v4 = float(a_stated @ np.array([basket["4Q26"], basket["3Q26"], basket["2Q26"]]))
        else:
            v3 = (2.0 / 3.0) * ser["2Q26"] + (1.0 / 3.0) * ser["1Q26"]
            v4 = (2.0 / 3.0) * ser["3Q26"] + (1.0 / 3.0) * ser["2Q26"]
        rows.append({"reading": name, "fx_3Q26_pp": round(v3, 1),
                     "fx_4Q26_pp": round(v4, 1),
                     "step_4Q26_minus_3Q26_pp": round(v4 - v3, 1),
                     "step_unrounded_pp": v4 - v3, "note": note})
    out = pd.DataFrame(rows)
    out["adr_fx_3Q26_fitted_pp"] = round(adr["3Q26"], 2)
    out["basket_3Q26_pct"] = round(basket["3Q26"], 3)
    out["basket_4Q26_spot_held_pct"] = round(basket["4Q26"], 3)
    write(out, "27_kernel_carried_fx_v2.csv")
    return out


def exfx(d: pd.DataFrame, kc: pd.DataFrame) -> pd.DataFrame:
    g = {r["quarter"]: r["gbv_musd"] for _, r in d.iterrows() if not pd.isna(r["gbv_musd"])}
    rows = []
    for gbv3q26, lab in [(26185.0, "frozen card 20_frozen_q3_2026"),
                         (26300.0, "architect central"),
                         (26550.0, "B4 request"),
                         (25900.0, "low"), (27000.0, "high")]:
        g2 = dict(g); g2["3Q26"] = gbv3q26

        def base(q):
            p = to_period(q)
            return (2.0 / 3.0) * g2[short(p - 1)] + (1.0 / 3.0) * g2[short(p - 2)]
        gr3 = 100.0 * (base("3Q26") / base("3Q25") - 1.0)
        gr4 = 100.0 * (base("4Q26") / base("4Q25") - 1.0)
        for _, k in kc.iterrows():
            step = float(k["step_4Q26_minus_3Q26_pp"])
            step_raw = float(k["step_unrounded_pp"])
            # the 3Q26 GBV at which ex-FX growth is exactly flat into 4Q26:
            #   gr4(G) = gr3 + step, gr4 linear in G through the 2/3 weight
            b4p = (2.0 / 3.0) * g["3Q25"] + (1.0 / 3.0) * g["2Q25"]
            target_b4 = b4p * (1.0 + (gr3 + step_raw) / 100.0)
            gbv_breakeven = (target_b4 - (1.0 / 3.0) * g["2Q26"]) * 1.5
            rows.append({"gbv_3Q26_musd": gbv3q26, "gbv_basis": lab,
                         "gbv_3Q26_breakeven_musd": round(gbv_breakeven, 0),
                         "kernel_base_3Q26_musd": round(base("3Q26"), 0),
                         "kernel_base_4Q26_musd": round(base("4Q26"), 0),
                         "kernel_base_yoy_3Q26_pct": round(gr3, 2),
                         "kernel_base_yoy_4Q26_pct": round(gr4, 2),
                         "gbv_base_growth_step_pp": round(gr4 - gr3, 2),
                         "fx_reading": k["reading"], "fx_step_pp": step,
                         "exfx_acceleration_pp": round((gr4 - gr3) - step, 2),
                         "exfx_acceleration_unrounded_pp": round((gr4 - gr3) - step_raw, 2),
                         "sign": "accelerates" if (gr4 - gr3) - step_raw > 0 else "decelerates"})
    out = pd.DataFrame(rows)
    write(out, "26_exfx_acceleration_v2.csv")
    return out
