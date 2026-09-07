"""Rewrite the WS09 live-options artefacts from the corrected estimator (audit finding A08).

Reads : data/processed/abnb_options_ledger.csv          (schema v2 rows, this run)
        data/processed/overnight/23_options_event_estimates.csv
        data/processed/overnight/09_implied_vs_realised.csv   (per-print realised moves; kept)
Writes: data/processed/overnight/09_implied_move_live.json    (replaced, corrected method)
        data/processed/overnight/09_implied_vs_realised.csv   (live_* block replaced)

The per-print realised-move columns produced by 09_stock_behaviour.py are untouched. Only the
repeated live_* snapshot block, which carried the superseded estimator's numbers, is replaced.

Run: py -3.13 analysis/src/overnight/23_update_ws09_options.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data" / "processed"
OUT = PROC / "overnight"
CORRECTION_DATE = "2026-09-06"

led = pd.read_csv(PROC / "abnb_options_ledger.csv")
ev = pd.read_csv(OUT / "23_options_event_estimates.csv")

a = led[(led.ticker == "ABNB") & (led.schema_version == 2)].sort_values("T_years")
ae = ev[ev.ticker == "ABNB"]
run_dt = str(a["run_datetime_utc"].iloc[0])
spot = float(a["spot"].iloc[0])


def f(x):
    try:
        v = float(x)
        return None if not np.isfinite(v) else v
    except Exception:
        return None


expiries = []
for _, r in a.iterrows():
    expiries.append(dict(
        expiry=r["expiry"], event_class=r["expiry_event_class"], dte_cal=int(r["dte_cal"]),
        T_years=f(r["T_years"]),
        raw_atm_iv_pct=f(r.get("raw_atm_iv_pct")),
        raw_straddle_mid_pct_spot=f(r.get("raw_straddle_mid_pct_spot")),
        raw_straddle_bid_pct_spot=f(r.get("raw_straddle_bid_pct_spot")),
        raw_straddle_ask_pct_spot=f(r.get("raw_straddle_ask_pct_spot")),
        straddle_strike=f(r.get("straddle_strike")),
        straddle_verified=bool(r.get("straddle_verified")),
        quote_quality=r.get("quote_quality"), qq_flags=r.get("qq_flags") if isinstance(r.get("qq_flags"), str) else ""))

estimates = []
for _, r in ae.iterrows():
    estimates.append(dict(
        spec_name=r["spec_name"], status=r["status"], detail=r["detail"],
        maturities_used=r.get("maturities_used"),
        background_vol_pct=f(r.get("background_vol_pct")),
        event_var=f(r.get("event_var")),
        event_sd_pct=f(r.get("event_sd_pct")),
        event_exp_abs_move_pct=f(r.get("event_exp_abs_move_pct")),
        event_var_sign=r.get("event_var_sign") if isinstance(r.get("event_var_sign"), str) else ""))

head = next((e for e in estimates if e["spec_name"] == "pre_plus_first_post"), None)
allspec = next((e for e in estimates if e["spec_name"] == "all_eligible"), None)
twopost = next((e for e in estimates if e["spec_name"] == "first_two_post"), None)

# ---- how identified is E, really?  Two diagnostics.
# (1) dispersion of the pre-event ATM IV curve: with no event between adjacent weeklies, any
#     dispersion here is measurement noise in the background baseline b.
pre_ivs = [e["raw_atm_iv_pct"] for e in expiries
           if e["event_class"] == "pre_event" and e["raw_atm_iv_pct"]]
pre_iv_dispersion_pts = (max(pre_ivs) - min(pre_ivs)) if pre_ivs else None
# (2) sensitivity of E to the assumed pre-event baseline, holding the 20 Nov quote fixed:
#     E(iv_base) = T_post * (iv_post^2 - iv_base^2)
post0 = next((e for e in expiries if e["event_class"] == "post_event"), None)
sens = []
if post0 and pre_ivs:
    import math as _m
    ivp, Tp = post0["raw_atm_iv_pct"] / 100.0, post0["T_years"]
    for base_pct in sorted(set([round(x, 2) for x in pre_ivs])):
        Ev = Tp * (ivp ** 2 - (base_pct / 100.0) ** 2)
        sens.append(dict(assumed_background_vol_pct=base_pct,
                         event_var=round(Ev, 8),
                         event_sd_pct=(round(_m.sqrt(Ev) * 100, 3) if Ev > 0 else None),
                         note=("non-positive" if Ev <= 0 else "")))
sd_vals = [e["event_sd_pct"] for e in estimates
           if e["status"] == "ok" and e.get("event_sd_pct")]

post_weeklies = [e["expiry"] for e in expiries if e["event_class"] == "post_event"]
weekly_6nov_listed = "2026-11-06" in list(a["expiry"])

spec_row = ae.iloc[0]
live = {
    # Schema/method marker. 1 = the legacy inline block in 09_stock_behaviour.py (flat-vol jump plus
    # an "upper bound" on total incremental variance, plus the defective ledger cross-check);
    # 2 = the WS23 / audit-A08 total-variance fit below. 09_stock_behaviour.py refuses to overwrite
    # this file when it reads a method_version >= 2. Do not lower it.
    "method_version": 2,
    "correction": f"{CORRECTION_DATE}: replaced by WS23. The previous content used "
                  "(a) a flat-vol jump estimate and (b) an 'upper bound' that attributed all "
                  "incremental total variance to the event, and cross-checked against "
                  "`abnb_options_ledger.csv`'s `event_implied_move_pct`, which was computed as "
                  "sigma_near^2*T_near - sigma_far^2*T_near and equals E*(1 - T_near/T_far), not E "
                  "(audit finding A08). Straddles were also summed from independently chosen "
                  "nearest-strike calls and puts, and expiry choice was by proximity to a target "
                  "date rather than by strict post-event eligibility.",
    "method": "Total-variance model: sigma_i^2 * T_i = b * T_i + E * d_i, where d_i = 1 if expiry i "
              "settles strictly after the latest plausible release timestamp. Fitted by least "
              "squares over eligible ATM-IV maturities. b = annualised background variance, "
              "E = event variance (variance of the earnings log-return).",
    "identification_requirement": "at least two post-event maturities, or at least one pre-event "
                                  "and one post-event maturity",
    "assumptions": str(spec_row.get("assumptions", "")),
    "estimator_source": "analysis/src/abnb_options_ledger.py (schema v2)",
    "acceptance_test": "analysis/src/overnight/23_options_estimator_test.py --dry-run (25/25 pass)",
    "observation_datetime_utc": run_dt,
    "spot": spot,
    "spot_source": "yfinance fast_info.last_price",
    "event": {
        "ticker": "ABNB", "label": str(spec_row.get("event_label")),
        "date_early": str(spec_row.get("event_date_early")),
        "date_late": str(spec_row.get("event_date_late")),
        "release_time_et": "after_close",
        "confidence": str(spec_row.get("event_confidence")),
        "company_confirmed": False,
        "sources": str(spec_row.get("event_sources")),
    },
    "post_event_weekly_6nov_listed": bool(weekly_6nov_listed),
    "listed_post_event_expiries": post_weeklies,
    "raw_measures_are_total_not_event": True,
    "expiries": expiries,
    "event_estimates": estimates,
    "headline": {
        "preferred_spec": None,
        "verdict": "IDENTIFIED IN PRINCIPLE, NOT USABLE TODAY. The three specifications disagree "
                   "from non-positive to " + (f"{max(sd_vals):.2f}%" if sd_vals else "n/a") +
                   " event standard deviation, and the fitted E is smaller than the noise in the "
                   "pre-event ATM IV curve. Quote the raw term structure today; quote an event "
                   "number only after the 6 Nov weekly lists.",
        "event_sd_range_pct": [min(sd_vals), max(sd_vals)] if sd_vals else None,
        "spec_pre_plus_first_post": {
            "background_vol_pct": (head or {}).get("background_vol_pct"),
            "event_sd_pct": (head or {}).get("event_sd_pct"),
            "event_exp_abs_move_pct": (head or {}).get("event_exp_abs_move_pct"),
            "status": (head or {}).get("status"),
        },
        "spec_all_eligible": {
            "background_vol_pct": (allspec or {}).get("background_vol_pct"),
            "event_sd_pct": (allspec or {}).get("event_sd_pct"),
            "event_exp_abs_move_pct": (allspec or {}).get("event_exp_abs_move_pct"),
            "status": (allspec or {}).get("status"),
        },
        "spec_first_two_post": {
            "background_vol_pct": (twopost or {}).get("background_vol_pct"),
            "event_var": (twopost or {}).get("event_var"),
            "event_sd_pct": (twopost or {}).get("event_sd_pct"),
            "event_var_sign": (twopost or {}).get("event_var_sign"),
            "note": "both maturities contain the print; this is the pair the SUPERSEDED estimator "
                    "used. Its fitted E is non-positive, which is a statement about the background "
                    "term structure, not about the earnings premium.",
        },
    },
    "identification_diagnostics": {
        "pre_event_atm_iv_curve_pct": pre_ivs,
        "pre_event_atm_iv_dispersion_pts": pre_iv_dispersion_pts,
        "pre_event_dispersion_meaning": "no scheduled event separates these weekly expiries, so "
                                        "this dispersion is measurement noise in the background "
                                        "baseline b",
        "E_sensitivity_to_assumed_background": sens,
        "conclusion": "E moves from non-positive to mid-single-digit percent across the range of "
                      "background vols the pre-event weeklies themselves span. The event variance "
                      "is inside the noise at this maturity.",
    },
    "historical_base_rate_abs_day1_move_pct": 7.07,
    "historical_base_rate_median_pct": 6.87,
    "caveats": [
        "The 6 Nov 2026 weekly is not listed yet; the nearest post-event expiry is 20 Nov, 15 days "
        "after the estimated print, so E also absorbs any other catalyst in that window and is "
        "estimated off a wide, thin strike grid.",
        "Yahoo implied volatilities, single snapshot, no skew/variance-swap correction: ATM IV is "
        "a proxy for total expiry variance, not the variance swap rate.",
        "The event date is a third-party estimate, not company-confirmed. Eligibility is robust "
        "to that uncertainty (the whole plausible window sits between the 23 Oct and 20 Nov "
        "expiries), but the identity of the event inside the 20 Nov expiry is not.",
        "A non-positive fitted E means the term structure shows no event kink at these quotes. It "
        "is NOT evidence that the market prices no earnings premium.",
    ],
    "rerun": "Re-run analysis/src/abnb_options_ledger.py in the week of 26-30 Oct 2026, once the "
             "6 Nov 2026 weekly is listed. That gives a post-event expiry 1 day after the print "
             "and turns E into a usable number.",
}
(OUT / "09_implied_move_live.json").write_text(json.dumps(live, indent=2, default=str))
print("wrote", OUT / "09_implied_move_live.json")

# ---- 09_implied_vs_realised.csv : replace the repeated live_* snapshot block
ivr = pd.read_csv(OUT / "09_implied_vs_realised.csv")
ivr = ivr[[c for c in ivr.columns if not c.startswith("live_")]]
ivr["live_snapshot_utc"] = run_dt
ivr["live_spot"] = spot
ivr["live_method"] = "sigma^2*T = b*T + E*d (WS23 correction, A08)"
ivr["live_event_confidence"] = str(spec_row.get("event_confidence"))
ivr["live_event_window"] = f"{spec_row.get('event_date_early')}..{spec_row.get('event_date_late')}"
for key, col in (("pre_plus_first_post", "live_event_sd_pct_pre_post"),
                 ("first_two_post", "live_event_sd_pct_two_post"),
                 ("all_eligible", "live_event_sd_pct_all")):
    e = next((x for x in estimates if x["spec_name"] == key), None)
    ivr[col] = (e or {}).get("event_sd_pct")
    if e is None:
        st = "spec_not_available"
    elif e["status"] == "ok" and e.get("event_var_sign") == "non_positive":
        st = "ok_but_non_positive_event_variance"
    else:
        st = e["status"]
    ivr[col + "_status"] = st
    ivr[col.replace("_sd_pct", "_var")] = (e or {}).get("event_var")
ivr["live_background_vol_pct"] = (head or {}).get("background_vol_pct")
for e in expiries:
    if e["event_class"] == "pre_event" and e is max(
            [x for x in expiries if x["event_class"] == "pre_event"], key=lambda z: z["T_years"]):
        ivr["live_last_pre_event_expiry"] = e["expiry"]
        ivr["live_last_pre_event_raw_atm_iv_pct"] = e["raw_atm_iv_pct"]
        ivr["live_last_pre_event_raw_straddle_pct_spot"] = e["raw_straddle_mid_pct_spot"]
post_sorted = [x for x in expiries if x["event_class"] == "post_event"]
if post_sorted:
    p0 = post_sorted[0]
    ivr["live_first_post_event_expiry"] = p0["expiry"]
    ivr["live_first_post_event_raw_atm_iv_pct"] = p0["raw_atm_iv_pct"]
    ivr["live_first_post_event_raw_straddle_pct_spot"] = p0["raw_straddle_mid_pct_spot"]
ivr["live_note"] = ("RAW straddle/IV columns are TOTAL implied move to expiry, not event moves. "
                    "Event columns come from the fitted variance model; see "
                    "09_implied_move_live.json and research/notes/overnight/"
                    "23_options-estimator-fix.md. Corrected " + CORRECTION_DATE + " (A08).")
ivr.to_csv(OUT / "09_implied_vs_realised.csv", index=False)
print("wrote", OUT / "09_implied_vs_realised.csv", ivr.shape)
print(json.dumps(live["headline"], indent=2))
