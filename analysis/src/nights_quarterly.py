"""Quarterly nights path from the choice model, with the three-feature lap placed on real quarters.

WHY A GROWTH-SPACE BUILD RATHER THAN SEASONAL FACTORS
----------------------------------------------------
Airbnb reports Nights and Seats BOOKED (booking date, net of cancellations), while the choice model
is built on stays - hotel room-nights sold, lodging demand. The two have different seasonal shapes
(Q1 is the largest booking quarter and the smallest stay quarter), and this repo has no booking-to-
stay lag distribution good enough to convert one into the other: `booking_curve_daily.csv` is a
handful of forward-calendar snapshots, not a lag distribution.

So this does not allocate an annual number across quarters with seasonal factors. It forecasts each
quarter's Y/Y GROWTH, which cancels seasonality on both sides, and applies it to the disclosed
prior-year quarter. Consensus never enters as an input; it appears only as a comparison column
(model/assumptions.md house rule).

WHAT IS ACTUALLY QUARTER-SPECIFIC
---------------------------------
The choice model's four driver blocks - market, mix drift, category adoption, relative price - are
annual rates, and an annual rate is exactly what a Y/Y growth contribution should be: 4% category
adoption means every quarter grows 4% Y/Y from category adoption. Nothing is gained by pretending
they have a quarterly shape we cannot observe.

The one block that IS quarter-specific is the product lever, and it is the whole trade. Three
features drove the NA acceleration and each laps on a known date:

  Reserve Now Pay Later      US rollout 3Q25   Y/Y window 3Q25-2Q26, laps from 3Q26. Management:
                                               "tougher comps in the back half of this year against
                                               the rollout of Reserve Now, Pay Later" (1Q26 call).
  Single fee, tranche 1      Oct 2025 (4Q25)   software-connected hosts. Window 4Q25-3Q26.
  Cancellation redesign      date not disclosed; live by the 1Q26 attribution. Modelled with
                                               tranche 1's window. THE WEAKEST DATE HERE.
  Single fee, tranche 2      13 Oct 2026       all remaining hosts. Window 4Q26-3Q27, but its own
                                               nights effect is -0.3% to -1.4% at payout-neutral
                                               re-pricing (host_only_fee_history_and_elasticity.md),
                                               so it is modelled at zero, -1pt in the bear case.

The product contribution is FITTED, not asserted: observed NA Y/Y less the choice model's underlying,
quarter by quarter. It then decays as each feature leaves its Y/Y window.

Run:  py -3.13 analysis/src/nights_quarterly.py
Out:  data/processed/nights_quarterly_na.csv      NA build, fitted product term and the lap
      data/processed/nights_quarterly_total.csv   total nights vs WS10, the guide and consensus
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

import choice_nights_driver as cnd

ROOT = Path(__file__).resolve().parents[2]
OUT_NA = ROOT / "data/processed/nights_quarterly_na.csv"
OUT_TOT = ROOT / "data/processed/nights_quarterly_total.csv"

# Disclosed NA nights Y/Y (WS10 estimates with lo/hi bands - Airbnb does not disclose quarterly
# regional nights, only annual regional totals in the 10-K).
NA_OBSERVED = {"1Q25": 2.0, "2Q25": 2.0, "3Q25": 5.0, "4Q25": 5.0, "1Q26": 8.0, "2Q26": 8.0}
# FY25 NA disclosed +2.6% (158/154mm, 10-K regional tables) - the pre-product run rate.
UNDERLYING_2025 = 2.6

FORECAST_Q = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
YEAR_OF = {"3Q26": 2026, "4Q26": 2026, "1Q27": 2027, "2Q27": 2027, "3Q27": 2027, "4Q27": 2027}

# Which features are still inside their Y/Y window in each forecast quarter.
IN_WINDOW = {
    "3Q26": {"rnpl": False, "t1_cancel": True,  "t2": False},
    "4Q26": {"rnpl": False, "t1_cancel": False, "t2": True},
    "1Q27": {"rnpl": False, "t1_cancel": False, "t2": True},
    "2Q27": {"rnpl": False, "t1_cancel": False, "t2": True},
    "3Q27": {"rnpl": False, "t1_cancel": False, "t2": True},
    "4Q27": {"rnpl": False, "t1_cancel": False, "t2": False},
}

# WS10 base, for comparison only (10_regional_forecast.csv)
WS10_NA = {"3Q26": 7.0, "4Q26": 7.0, "1Q27": 6.0, "2Q27": 6.0, "3Q27": 6.0, "4Q27": 6.0}
WS10_TOTAL = {"3Q26": 10.29, "4Q26": 9.94, "1Q27": 9.15, "2Q27": 9.15, "3Q27": 9.15, "4Q27": 9.15}
GUIDE_3Q26 = (10.0, 12.0)      # "low double digit" nights, Q2'26 release
CONSENSUS_3Q26 = 10.2          # 147.2mm, WS14 master synthesis

PRIOR_NIGHTS = {"3Q26": 133.6, "4Q26": 121.9, "1Q27": 156.2, "2Q27": 148.3}   # 02_kpi_panel_quarterly
NA_SHARE = {"3Q26": 0.288, "4Q26": 0.282, "1Q27": 0.266, "2Q27": 0.266, "3Q27": 0.266, "4Q27": 0.266}

GLOBAL_PRODUCT_PTS = 3.0       # Mertz, 1Q26 call: ~3 pts of nights growth from the three features


def underlying() -> dict[int, float]:
    """Choice-model US nights growth with no product lever, in points."""
    df, _ = cnd.project(cnd.calibrate())
    g = df.set_index("year").us_nights_growth
    return {y: float(g.loc[y]) * 100 for y in (2026, 2027)}


def fit_product(u: dict[int, float]) -> dict[str, float]:
    """Split the fitted NA product contribution between RNPL and the tranche-1 bundle.

    3Q25 is the only quarter where RNPL is live alone, so it identifies RNPL. The step up in 1Q26,
    once tranche 1 and the cancellation redesign have ramped, identifies the rest.
    """
    rnpl = NA_OBSERVED["3Q25"] - UNDERLYING_2025
    t1_cancel = (NA_OBSERVED["1Q26"] - u[2026]) - rnpl
    return {"rnpl": rnpl, "t1_cancel": t1_cancel}


def na_path(u, fitted, scenario="base"):
    rows = []
    for q in FORECAST_Q:
        w = IN_WINDOW[q]
        prod = 0.0
        if w["rnpl"]:
            prod += fitted["rnpl"]
        if w["t1_cancel"]:
            prod += fitted["t1_cancel"]
        if scenario == "bull":
            # the RNPL comp is not clean: 3Q25 was a ramping quarter, so part of the lift recurs
            if q == "3Q26":
                prod += 0.5 * fitted["rnpl"]
            # and a new lever of half the old bundle's size arrives for FY27
            if YEAR_OF[q] == 2027:
                prod += 0.5 * (fitted["rnpl"] + fitted["t1_cancel"])
        if scenario == "bear" and w["t2"]:
            prod -= 1.0   # single fee tranche 2 at payout-neutral re-pricing costs nights
        rows.append({"quarter": q, "scenario": scenario, "underlying_pts": round(u[YEAR_OF[q]], 2),
                     "product_pts": round(prod, 2),
                     "na_nights_yoy_pct": round(u[YEAR_OF[q]] + prod, 2),
                     "ws10_na_base_pct": WS10_NA[q],
                     "delta_vs_ws10_pts": round(u[YEAR_OF[q]] + prod - WS10_NA[q], 2)})
    return pd.DataFrame(rows)


def total_path(na: pd.DataFrame, exna_laps: bool, peak_na: float) -> pd.DataFrame:
    """Total nights = WS10's total, adjusted for our NA delta, optionally plus an ex-NA lap.

    Management's ~3 pts was a GLOBAL figure. With NA fitted at its own (larger) number, the implied
    ex-NA contribution is (3.0 - na_share x na_product) / (1 - na_share). RNPL rolled out in the US
    first, so ex-NA laps later; `exna_laps` toggles whether that lap lands inside the horizon.
    """
    rows = []
    for _, r in na.iterrows():
        q = r.quarter
        s = NA_SHARE[q]
        na_delta = (r.na_nights_yoy_pct - WS10_NA[q]) * s
        exna_delta = 0.0
        if exna_laps:
            peak = (GLOBAL_PRODUCT_PTS - s * peak_na) / (1 - s)
            exna_delta = -peak * (1 - s) if q in ("1Q27", "2Q27", "3Q27", "4Q27") else 0.0
        tot = WS10_TOTAL[q] + na_delta + exna_delta
        rows.append({"quarter": q, "scenario": r.scenario, "exna_lap": exna_laps,
                     "ws10_total_pct": WS10_TOTAL[q],
                     "na_contribution_delta_pts": round(na_delta, 2),
                     "exna_contribution_delta_pts": round(exna_delta, 2),
                     "model_total_nights_yoy_pct": round(tot, 2),
                     "nights_mm": round(PRIOR_NIGHTS[q] * (1 + tot / 100), 1) if q in PRIOR_NIGHTS else None})
    return pd.DataFrame(rows)


def main():
    u = underlying()
    fitted = fit_product(u)
    peak_na = fitted["rnpl"] + fitted["t1_cancel"]

    print("Choice-model underlying US nights growth, no product lever")
    print(f"  2026 {u[2026]:+.2f}%   2027 {u[2027]:+.2f}%   (2025 actual NA {UNDERLYING_2025:+.1f}%)")
    print("\nFitted NA product contribution (observed NA Y/Y less underlying, points)")
    print(f"  RNPL (identified on 3Q25, the only quarter it is live alone): {fitted['rnpl']:+.2f}")
    print(f"  tranche-1 single fee + cancellation redesign (the 1Q26 step): {fitted['t1_cancel']:+.2f}")
    print(f"  peak bundle, 1H26: {peak_na:+.2f} pts")
    exna = (GLOBAL_PRODUCT_PTS - 0.293 * peak_na) / (1 - 0.293)
    print(f"  implied ex-NA bundle from the global ~3.0 pts: {exna:+.2f} pts")

    nas = pd.concat([na_path(u, fitted, s) for s in ("bear", "base", "bull")], ignore_index=True)
    nas.to_csv(OUT_NA, index=False)
    print("\n=== North America nights Y/Y by quarter ===")
    piv = nas.pivot(index="quarter", columns="scenario", values="na_nights_yoy_pct").reindex(FORECAST_Q)
    piv["WS10 base"] = [WS10_NA[q] for q in piv.index]
    print(piv[["bear", "base", "bull", "WS10 base"]].to_string())

    tots = pd.concat([total_path(nas[nas.scenario == s], lap, peak_na)
                      for s in ("bear", "base", "bull") for lap in (False, True)], ignore_index=True)
    tots.to_csv(OUT_TOT, index=False)
    print("\n=== Total nights Y/Y: NA lap only (ex-NA unchanged from WS10) ===")
    p1 = tots[~tots.exna_lap].pivot(index="quarter", columns="scenario",
                                    values="model_total_nights_yoy_pct").reindex(FORECAST_Q)
    p1["WS10 base"] = [WS10_TOTAL[q] for q in p1.index]
    print(p1[["bear", "base", "bull", "WS10 base"]].to_string())
    print("\n=== Total nights Y/Y: the bundle laps everywhere from 1Q27 ===")
    p2 = tots[tots.exna_lap].pivot(index="quarter", columns="scenario",
                                   values="model_total_nights_yoy_pct").reindex(FORECAST_Q)
    p2["WS10 base"] = [WS10_TOTAL[q] for q in p2.index]
    print(p2[["bear", "base", "bull", "WS10 base"]].to_string())

    b = tots[(tots.scenario == "base") & (~tots.exna_lap)].set_index("quarter")
    print("\n=== The 5 Nov card ===")
    print(f"  3Q26 model {b.loc['3Q26'].model_total_nights_yoy_pct:+.2f}% "
          f"({b.loc['3Q26'].nights_mm:.1f}mm)   guide {GUIDE_3Q26[0]:.0f}-{GUIDE_3Q26[1]:.0f}%   "
          f"consensus {CONSENSUS_3Q26:+.1f}% (147.2mm)")
    print(f"  4Q26 model {b.loc['4Q26'].model_total_nights_yoy_pct:+.2f}% "
          f"({b.loc['4Q26'].nights_mm:.1f}mm)   WS10 {WS10_TOTAL['4Q26']:+.2f}%   "
          "<- the guide given on 5 Nov, and the trade")
    print(f"\nwrote {OUT_NA}\nwrote {OUT_TOT}")


if __name__ == "__main__":
    main()
