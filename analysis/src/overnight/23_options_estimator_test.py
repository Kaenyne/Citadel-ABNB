"""Acceptance tests for the rewritten options event-variance estimator (audit finding A08).

Reads : analysis/src/abnb_options_ledger.py (imported by path; no network in --dry-run)
Writes: nothing (prints a PASS/FAIL table; exit status 1 on any failure)
Run   : py -3.13 analysis/src/overnight/23_options_estimator_test.py --dry-run

--dry-run (the default) uses only synthetic chains with a KNOWN background variance b and a KNOWN
event variance E, so the estimator can be checked against the truth.  Tests cover the four things
the audit asked to be demonstrated:

  T1  exact recovery of E and b from one pre-event and one post-event maturity;
  T2  exact recovery of E and b from two post-event maturities;
  T3  exact recovery over a full synthetic term structure (4 maturities, least squares);
  T4  expiries that PRECEDE the event fail eligibility -- a chain that lists only pre-event
      expiries returns 'unavailable_no_post_event_expiry', never a number;
  T5  a single post-event maturity with no pre-event maturity is not identified;
  T6  an ambiguous expiry (settlement inside the event-date uncertainty window) is excluded;
  T7  the old (broken) estimator is shown to return E*(1 - T_near/T_far), not E, on the same data;
  T8  E <= 0 is returned as 'non_positive_event_variance', not floored to zero and not described
      as 'no earnings premium';
  T9  same-strike verification: independently chosen nearest-strike call and put are rejected as a
      straddle when the strikes differ;
  T10 confidence gating: an event spec with confidence 'unknown'/'pattern_estimate' yields
      'unavailable_no_event_timestamp'.

Also runs a --live smoke test (not part of the acceptance set) if asked.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parents[1] / "abnb_options_ledger.py"
spec = importlib.util.spec_from_file_location("abnb_options_ledger", SRC)
OL = importlib.util.module_from_spec(spec)
sys.modules["abnb_options_ledger"] = OL   # dataclasses needs the module registered
spec.loader.exec_module(OL)

TOL = 1e-9
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, msg: str = ""):
    RESULTS.append((name, bool(ok), msg))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {msg}" if msg else ""))


def synth(T_days: int, event_class: str, b_var: float, E: float, expiry="synthetic"):
    """Build one synthetic observation consistent with sigma^2*T = b*T + E*d."""
    T = T_days / OL.DAYS_PER_YEAR
    d = 1.0 if event_class == "post_event" else 0.0
    total = b_var * T + E * d
    iv = math.sqrt(total / T)
    return dict(expiry=f"{expiry}_{T_days}d", T=T, iv=iv, event_class=event_class)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args(argv)

    B_TRUE = 0.30 ** 2          # 30% annualised background vol
    E_TRUE = 0.07 ** 2          # 7% one-day event standard deviation
    print(f"synthetic truth: background vol {math.sqrt(B_TRUE)*100:.2f}%, "
          f"event sd {math.sqrt(E_TRUE)*100:.2f}%\n")

    # ---------------------------------------------------------------- T1 one pre + one post
    obs = [synth(47, "pre_event", B_TRUE, E_TRUE), synth(76, "post_event", B_TRUE, E_TRUE)]
    f = OL.fit_variance_model(obs)
    check("T1 one pre + one post recovers E",
          f.status == "ok" and abs(f.event_var - E_TRUE) < TOL and abs(f.b_var - B_TRUE) < TOL,
          f"status={f.status} E={f.event_var:.10f} (true {E_TRUE:.10f}) b={f.b_var:.10f}")
    check("T1b reported event sd matches truth",
          abs(f.event_sd_pct - math.sqrt(E_TRUE) * 100) < 1e-7,
          f"{f.event_sd_pct:.6f}% vs {math.sqrt(E_TRUE)*100:.6f}%")
    check("T1c expected |move| = sd * sqrt(2/pi)",
          abs(f.event_exp_abs_move_pct - math.sqrt(E_TRUE) * math.sqrt(2 / math.pi) * 100) < 1e-7)

    # ---------------------------------------------------------------- T2 two post-event
    obs = [synth(76, "post_event", B_TRUE, E_TRUE), synth(104, "post_event", B_TRUE, E_TRUE)]
    f = OL.fit_variance_model(obs)
    check("T2 two post-event maturities recover E",
          f.status == "ok" and abs(f.event_var - E_TRUE) < TOL and abs(f.b_var - B_TRUE) < TOL,
          f"E={f.event_var:.10f} b={f.b_var:.10f}")

    # ---------------------------------------------------------------- T3 full term structure
    obs = [synth(47, "pre_event", B_TRUE, E_TRUE), synth(76, "post_event", B_TRUE, E_TRUE),
           synth(104, "post_event", B_TRUE, E_TRUE), synth(131, "post_event", B_TRUE, E_TRUE)]
    f = OL.fit_variance_model(obs)
    check("T3 four maturities, least squares, recovers E",
          f.status == "ok" and abs(f.event_var - E_TRUE) < 1e-8 and abs(f.b_var - B_TRUE) < 1e-8,
          f"E={f.event_var:.10f} b={f.b_var:.10f} rmse={f.resid_rmse_var:.2e}")
    check("T3b leave-one-out spread is degenerate on clean data",
          np.isfinite(f.loo_event_sd_min_pct) and
          abs(f.loo_event_sd_max_pct - f.loo_event_sd_min_pct) < 1e-6,
          f"[{f.loo_event_sd_min_pct:.6f}, {f.loo_event_sd_max_pct:.6f}]")

    # ---------------------------------------------------------------- T4 pre-event expiries only
    obs = [synth(20, "pre_event", B_TRUE, E_TRUE), synth(47, "pre_event", B_TRUE, E_TRUE)]
    f = OL.fit_variance_model(obs)
    check("T4 expiries before the event fail eligibility",
          f.status == "unavailable_no_post_event_expiry" and not np.isfinite(f.event_var),
          f"status={f.status}")

    # eligibility at the classifier level, with the real ABNB spec and real listed expiries
    abnb = OL.EVENTS["ABNB"]
    listed = ["2026-09-11", "2026-10-16", "2026-10-23", "2026-11-20", "2026-12-18", "2027-01-15"]
    cls = {e: OL.classify_expiry(e, abnb) for e in listed}
    check("T4b every expiry settling before the earliest plausible release is pre_event",
          all(cls[e] == "pre_event" for e in ["2026-09-11", "2026-10-16", "2026-10-23"]), str(cls))
    check("T4c every expiry settling after the latest plausible release is post_event",
          all(cls[e] == "post_event" for e in ["2026-11-20", "2026-12-18", "2027-01-15"]), str(cls))
    check("T4d an expiry on the event date itself is NOT post_event",
          OL.classify_expiry("2026-11-05", abnb) != "post_event",
          OL.classify_expiry("2026-11-05", abnb))
    check("T4e strictness: an expiry settling the same afternoon as an after-close release is "
          "not post_event",
          OL.classify_expiry("2026-11-04", abnb) != "post_event")

    # ---------------------------------------------------------------- T5 single post, no pre
    obs = [synth(76, "post_event", B_TRUE, E_TRUE)]
    f = OL.fit_variance_model(obs)
    check("T5 one post-event maturity alone is not identified",
          f.status.startswith("unavailable") and not np.isfinite(f.event_var), f.status)

    # ---------------------------------------------------------------- T6 ambiguous excluded
    obs = [synth(47, "pre_event", B_TRUE, E_TRUE),
           dict(synth(60, "post_event", B_TRUE, E_TRUE), event_class="ambiguous"),
           synth(76, "post_event", B_TRUE, E_TRUE)]
    f = OL.fit_variance_model(obs)
    check("T6 ambiguous expiries are dropped from identification",
          f.n_maturities == 2 and abs(f.event_var - E_TRUE) < TOL, f"n={f.n_maturities}")

    # ---------------------------------------------------------------- T7 old estimator is biased
    o_near = synth(76, "post_event", B_TRUE, E_TRUE)
    o_far = synth(104, "post_event", B_TRUE, E_TRUE)
    old_var = o_near["iv"] ** 2 * o_near["T"] - o_far["iv"] ** 2 * o_near["T"]
    expected_bias = E_TRUE * (1 - o_near["T"] / o_far["T"])
    check("T7 old estimator returns E*(1 - T_near/T_far), not E",
          abs(old_var - expected_bias) < 1e-12 and abs(old_var - E_TRUE) > 1e-4,
          f"old={old_var:.8f} predicted_bias={expected_bias:.8f} true_E={E_TRUE:.8f} "
          f"(old recovers {old_var/E_TRUE*100:.1f}% of E; old sd {math.sqrt(max(old_var,0))*100:.2f}% "
          f"vs true {math.sqrt(E_TRUE)*100:.2f}%)")
    f_new = OL.fit_variance_model([o_near, o_far])
    check("T7b new estimator recovers E on the same two quotes",
          abs(f_new.event_var - E_TRUE) < TOL)

    # ---------------------------------------------------------------- T8 non-positive E labelling
    # background is HIGHER in the far expiry, so the fitted event variance goes negative
    T2, T3 = 76 / OL.DAYS_PER_YEAR, 104 / OL.DAYS_PER_YEAR
    obs = [dict(expiry="p1", T=T2, iv=0.379, event_class="post_event"),
           dict(expiry="p2", T=T3, iv=0.385, event_class="post_event")]
    f = OL.fit_variance_model(obs)
    check("T8 negative fitted E is returned, not floored to zero",
          f.status == "ok" and f.event_var < 0 and not np.isfinite(f.event_sd_pct),
          f"E={f.event_var:.8f}")
    check("T8b negative E is labelled non_positive_event_variance and not 'no premium'",
          "non_positive_event_variance" in f.detail and "NOT evidence" in f.detail, f.detail[:80])

    # ---------------------------------------------------------------- T9 same-strike verification
    calls = pd.DataFrame(dict(strike=[175.0, 180.0, 185.0], bid=[12.0, 9.0, 6.5],
                              ask=[12.4, 9.3, 6.8], impliedVolatility=[.38, .38, .38],
                              openInterest=[100, 100, 100], volume=[5, 5, 5],
                              lastTradeDate=pd.Timestamp("2026-09-04", tz="UTC")))
    puts_ok = pd.DataFrame(dict(strike=[175.0, 180.0, 185.0], bid=[6.0, 8.0, 10.5],
                                ask=[6.3, 8.3, 10.9], impliedVolatility=[.39, .39, .39],
                                openInterest=[100, 100, 100], volume=[5, 5, 5],
                                lastTradeDate=pd.Timestamp("2026-09-04", tz="UTC")))
    puts_disjoint = puts_ok.assign(strike=[172.5, 177.5, 182.5])

    class FakeChain:
        def __init__(self, c, p):
            self.calls, self.puts = c, p

    class FakeTicker:
        def __init__(self, c, p):
            self._ch = FakeChain(c, p)

        def option_chain(self, _exp):
            return self._ch

    asof = pd.Timestamp("2026-09-06 20:00", tz="UTC")
    r_ok = OL.snapshot_expiry(FakeTicker(calls, puts_ok), "TEST", "2026-11-20", 181.94, asof, abnb)
    check("T9 straddle accepted only on a shared strike",
          r_ok["straddle_verified"] and r_ok["straddle_strike"] == 180.0 and
          abs(r_ok["straddle_mid"] - ((9.0 + 9.3) / 2 + (8.0 + 8.3) / 2)) < 1e-9,
          f"K={r_ok['straddle_strike']} mid={r_ok['straddle_mid']}")
    check("T9b bid/ask/mid/strike/observation time are all stored",
          all(np.isfinite(r_ok[k]) for k in ("call_bid", "call_ask", "call_mid", "put_bid",
                                             "put_ask", "put_mid", "straddle_bid", "straddle_ask",
                                             "straddle_mid", "straddle_strike"))
          and r_ok["run_datetime_utc"] and r_ok["call_last_trade_utc"])
    check("T9c raw measures are labelled raw/total, and no event column is on the ledger row",
          "raw_straddle_mid_pct_spot" in r_ok and "raw_atm_iv_pct" in r_ok
          and not any("event_implied_move" in k for k in r_ok))
    r_bad = OL.snapshot_expiry(FakeTicker(calls, puts_disjoint), "TEST", "2026-11-20", 181.94,
                               asof, abnb)
    check("T9d disjoint call/put strikes are NOT called a straddle",
          r_bad["straddle_verified"] is False and r_bad["quote_quality"] == "unusable",
          r_bad.get("straddle_reject_reason", ""))
    check("T9e a rejected straddle is excluded from identification",
          OL.eligible_obs([r_bad]) == [])

    # ---------------------------------------------------------------- T10 confidence gating
    unknown = OL.EventSpec("XYZ", None, None, "after_close", "unknown", "none", "Q3")
    recs = OL.event_estimates_for("XYZ", [r_ok], unknown, asof)
    check("T10 no usable event timestamp -> unavailable_no_event_timestamp",
          len(recs) == 1 and recs[0]["status"] == "unavailable_no_event_timestamp",
          recs[0]["status"])
    pattern = OL.EventSpec("XYZ", "2026-11-04", "2026-11-12", "after_close", "pattern_estimate",
                           "pattern only", "Q3")
    check("T10b pattern_estimate confidence is not sufficient for an event estimate",
          OL.event_estimates_for("XYZ", [r_ok], pattern, asof)[0]["status"]
          == "unavailable_no_event_timestamp")
    check("T10c every real event spec carries a confidence label and sources",
          all(s.confidence and s.sources for s in OL.EVENTS.values()))

    # ---------------------------------------------------------------- summary
    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - n_fail}/{len(RESULTS)} checks passed")

    if a.live:
        print("\n--- live smoke test (network) ---")
        led, evd = OL.run(["ABNB"], write=False)
        print(evd[["spec_name", "status", "background_vol_pct", "event_sd_pct"]].to_string(index=False))

    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
