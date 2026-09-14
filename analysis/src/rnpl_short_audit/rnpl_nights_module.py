"""Unified RNPL nights module: one engine, four mechanisms, nothing counted twice.

Author: Opus audit agent for Theo. Date: 2026-09-11.
Note:   docs/rnpl-short-audit/01_rnpl-nights-mechanics-audit.md

WHAT THIS IS
------------
The team currently carries four separate treatments of the same product bundle:

  PR #32 (origin/krish/nights-quarterly)  a fitted product LEVEL that laps on dates.
  Krish D1 (overnight2/D)                 a monthly cohort engine for the cancellation TAIL.
  Theo's balance-sheet bridge             a four-mechanism narrative plus a pull-forward term.
  Jessie (origin/jessie/backlog-conversion) an annual (1+L)(1-C)/(1-C0) plateau-plus-drag model.

Jessie's C(t) and Krish's tail are THE SAME OBJECT (the reported-nights drag from a higher
RNPL cancellation propensity, modelled in both years). Jessie's L(t) and PR #32's fitted
+2.40 / +2.29 are THE SAME OBJECT (the product level and its lap). Using any two of these
models together double counts. This module is the single place the four mechanisms are
separated so they can be added.

THE FOUR MECHANISMS (Theo's note, section 1.5), made orthogonal
--------------------------------------------------------------
  M1  CONVERSION UPLIFT, permanent level.
      A dated level gain contributes to y/y only while its window is open, then zero.
      Reference already laps the North American legs (PR #32 base), so M1 here is only
      the corrections PR #32 omits: the ex-NA lap schedule, the July-2026 eligibility
      expansion, and the partial-quarter correction on the US lap.

  M2  PULL-FORWARD, one-time, reverses in the comp.
      RNPL lengthens lead times. While the RNPL share is RISING, the booking calendar
      shifts forward and the quarter receives bookings that would otherwise have been
      made later. The addition to a quarter's gross is d(share) x L x u / 3 of a
      quarter's nights. It is a FLOW addition proportional to the CHANGE in share, so it
      goes to zero once the share plateaus, and the y/y effect in the lapping quarter is
      PF(q) - PF(q-4).

  M3  CANCELLATION DEFERRAL, transition timing only.
      RNPL moves the moment of failure from "days after booking" to "days before
      check-in" (payment falls due shortly before the free-cancellation window closes).
      During the ramp this FLATTERS reported nights; afterwards it deposits the tail.
      Defined here as (timed recognition) minus (recognition in the booking quarter), so
      it contains no propensity level at all and nets to ~zero over a full cycle.

  M4  HIGHER PROPENSITY, permanent drag.
      The steady-state cost of a higher RNPL cancellation rate: what the drag would be if
      every excess cancellation were recognised in its own booking quarter. Scales with
      the y/y CHANGE in RNPL nights share, not its level.

  M3 + M4 reproduces Krish's D1 tail exactly (verified in the self-checks below). The
  split is a re-partition of one number, not an addition to it.

REFERENCE (the "no-RNPL-tail" counterfactual)
---------------------------------------------
3Q26 +9.89% (146.8mm) and 4Q26 +8.90% (132.7mm), the reconciled team baseline
(research/notes/2026-09-10_nights-baseline-reconciliation.md section 1.4). 1Q27 to 4Q27 use
PR #32's base with the NA lap only and NO ex-NA lap (+8.17% each), because the ex-NA lap is
supplied here by M1 on its own dated schedule. Using PR #32's exna_lap=True row instead
would double count M1.

WHAT THIS MODULE CANNOT DO
--------------------------
It cannot measure the RNPL cancellation propensity, the live unpaid backlog, the RNPL
nights share, or the rebooking offset. Every one is a scenario input. It cannot establish
causality; the October-2025 cancellation redesign, two fee tranches, the 2Q26 Strict-to-
Firm migration, the Middle East conflict and the World Cup all overlap the window.

Run:  python analysis/src/rnpl_short_audit/rnpl_nights_module.py
Out:  data/processed/rnpl_short_audit/rnpl_nights_module.csv          quarterly, per mechanism
      data/processed/rnpl_short_audit/rnpl_nights_module_params.csv   every parameter, labelled
      data/processed/rnpl_short_audit/rnpl_nights_module_state.csv    state variables by quarter
No network. Reads nothing. Writes only under data/processed/rnpl_short_audit/.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
OUT = ROOT / "data/processed/rnpl_short_audit"

# ======================================================================================
# 1. SOURCED inputs
# ======================================================================================

# Disclosed reported Nights and Seats Booked, millions.
# SOURCED: data/processed/overnight/02_kpi_panel_quarterly.csv, reconciling to the Airbnb
# quarterly summaries. Booking-date basis, net of cancellations recorded in the quarter
# whatever their vintage (FY2025 10-K, ledger D054).
DISCLOSED = {
    "1Q24": 132.6, "2Q24": 125.1, "3Q24": 122.8, "4Q24": 111.0,
    "1Q25": 143.1, "2Q25": 134.4, "3Q25": 133.6, "4Q25": 121.9,
    "1Q26": 156.2, "2Q26": 148.3,
}

# Reference growth path, percent y/y. 3Q26/4Q26 SOURCED from the team reconciled baseline;
# 1Q27-4Q27 SOURCED from PR #32's base, NA lap only (nights_quarterly_total.csv,
# scenario=base, exna_lap=False). The ex-NA lap is NOT in the reference: M1 supplies it.
REFERENCE_GROWTH = {
    "3Q26": 9.89, "4Q26": 8.90,
    "1Q27": 8.17, "2Q27": 8.17, "3Q27": 8.17, "4Q27": 8.17,
}

# Baseline lifetime cancellation rate on non-RNPL bookings.
# SOURCED with an unstated unit of account: "an average of maybe 16% cancellation rate
# historically" (4Q25 call, ledger D018). No base period, no denominator given.
BASE_CANCEL_RATE = 0.16

# North America share of total nights. SOURCED: KPI panel na_share_of_nights_pct.
NA_SHARE = 0.288

# PR #32 fitted product terms, points of NA nights. SOURCED from a team model, not from
# disclosure: two free parameters fitted on four WS10 NA estimates.
PR32_RNPL_NA_PTS = 2.40
PR32_FEE_CANCEL_NA_PTS = 2.29

# ======================================================================================
# 2. Calendar
# ======================================================================================

QUARTERS = [
    "1Q24", "2Q24", "3Q24", "4Q24",
    "1Q25", "2Q25", "3Q25", "4Q25",
    "1Q26", "2Q26", "3Q26", "4Q26",
    "1Q27", "2Q27", "3Q27", "4Q27",
    "1Q28", "2Q28",  # absorb cohorts only; never reported on
]
REPORT = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
PRIOR = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26",
         "3Q27": "3Q26", "4Q27": "4Q26"}

MONTHS: list[str] = []
for _q in QUARTERS:
    _qq, _yy = int(_q[0]), 2000 + int(_q[2:])
    for _o in range(3):
        MONTHS.append(f"{_yy}-{(_qq - 1) * 3 + 1 + _o:02d}")
MONTH_INDEX = {m: i for i, m in enumerate(MONTHS)}
MONTH_QUARTER = {m: q for q in QUARTERS
                 for m in [f"{2000 + int(q[2:])}-{(int(q[0]) - 1) * 3 + 1 + o:02d}"
                           for o in range(3)]}


def reference_nights() -> dict[str, float]:
    """Reported nights on the no-RNPL-tail reference path, chained through 2027."""
    out = dict(DISCLOSED)
    for q in REPORT:
        out[q] = out[PRIOR[q]] * (1 + REFERENCE_GROWTH[q] / 100.0)
    # 1Q28/2Q28 exist only so late cohorts have somewhere to land.
    out["1Q28"] = out["1Q27"] * 1.08
    out["2Q28"] = out["2Q27"] * 1.08
    return out


# ======================================================================================
# 3. Scenario parameters
# ======================================================================================

SCENARIOS = {
    # ---------------------------------------------------------------- bear (short case)
    "bear": dict(
        # RNPL share of GBV, percent. 1Q26 ~20% and 2Q26 >20% SOURCED (ledger D031 official,
        # D043 call mirror). 2025 and 2H26 onward ASSUMED. A SLOWER 2025 ramp lowers the
        # prior-year base and widens the y/y drag, so it is the bear 2025 path.
        gbv_share={"3Q25": 2.5, "4Q25": 7.0, "1Q26": 20.0, "2Q26": 21.0, "3Q26": 25.0,
                   "4Q26": 27.0, "1Q27": 27.0, "2Q27": 27.0, "3Q27": 27.0, "4Q27": 27.0,
                   "1Q28": 27.0, "2Q28": 27.0},
        adr_ratio=1.33,          # DERIVED: 1Q26 ~4pts GBV on ~3pts nights => 4/3 marginal ADR
        delta_pp=6.0,            # ASSUMED via management-implied: the whole 16->17 rise is RNPL
        lead_months=1.8,         # DERIVED range floor (Little's Law on the unearned-fee pool)
        lead_uplift=0.15,        # direction SOURCED, magnitude ASSUMED
        rebook=0.00,             # mechanism SOURCED (D002, D046), magnitude ASSUMED
        exna_fee_cancel_pts=0.88,   # DERIVED: 50% of the ex-NA bundle, pinned by the 4Q25 print
        exna_rnpl_pts=1.05,         # DERIVED residual of management's ~3.0 global points
        july_expansion_pts=0.10,    # ASSUMED; July 2026 booking-type expansion, size undisclosed
        us_partial_lap_pts=0.00,    # "beginning of Q3" (3Q25 call) taken literally: full lap
    ),
    # ---------------------------------------------------------------- base
    "base": dict(
        gbv_share={"3Q25": 4.0, "4Q25": 9.0, "1Q26": 20.0, "2Q26": 21.0, "3Q26": 22.0,
                   "4Q26": 23.0, "1Q27": 23.0, "2Q27": 23.0, "3Q27": 23.0, "4Q27": 23.0,
                   "1Q28": 23.0, "2Q28": 23.0},
        adr_ratio=1.33,
        delta_pp=4.0,
        lead_months=2.2,
        lead_uplift=0.07,
        rebook=0.25,
        exna_fee_cancel_pts=0.79,
        exna_rnpl_pts=0.96,
        july_expansion_pts=0.20,
        us_partial_lap_pts=0.17,    # midpoint of 0 (call) and +0.34 (14 Aug newsroom date)
    ),
    # ---------------------------------------------------------------- bull (against the short)
    "bull": dict(
        gbv_share={"3Q25": 6.0, "4Q25": 12.0, "1Q26": 20.0, "2Q26": 21.0, "3Q26": 21.0,
                   "4Q26": 21.0, "1Q27": 21.0, "2Q27": 21.0, "3Q27": 21.0, "4Q27": 21.0,
                   "1Q28": 21.0, "2Q28": 21.0},
        adr_ratio=1.33,
        delta_pp=2.0,
        lead_months=3.0,
        lead_uplift=0.00,
        rebook=0.50,
        exna_fee_cancel_pts=0.70,
        exna_rnpl_pts=0.87,
        july_expansion_pts=0.30,
        us_partial_lap_pts=0.34,    # US RNPL live ~6.5 of 13 weeks in 3Q25 (14 Aug newsroom)
    ),
}

# Share of a cohort's EXCESS cancellations recognised in the stay month rather than the
# month before. Window SOURCED (D002, D012); split ASSUMED. Audited: worth 0.001 pts.
EXCESS_IN_STAY_MONTH = 0.85
# Share of BASELINE cancellations recognised in the booking month (24h grace, ledger D012).
# Mechanism SOURCED, magnitude ASSUMED. Audited: worth 0.000 pts.
BASE_CANCEL_IN_BOOKING_MONTH = 0.25
# Share of the July-2026 expansion level already inside each quarter. ASSUMED.
JULY_PROFILE = {"3Q26": 0.67, "4Q26": 1.0, "1Q27": 1.0, "2Q27": 1.0, "3Q27": 0.33, "4Q27": 0.0}
# Fraction of 1Q26 that ex-NA RNPL was live: 17 Feb to 4 March go-lives, so roughly the last
# 5 to 6 weeks of a 13-week quarter. SOURCED dates (ledger D025-D029), 5.5/13 rounded.
EXNA_1Q27_PARTIAL = 5.5 / 13.0


# ======================================================================================
# 4. State variables and the cohort engine
# ======================================================================================

def lead_time_weights(mean_months: float, horizon: int = 14) -> list[float]:
    """Cohort lead-time distribution: shifted geometric in whole months, k=0 = stay in the
    booking month. Mean DERIVED from Little's Law on the unearned-fee pool (2.0 to 2.6
    months); SHAPE ASSUMED, because Airbnb has never published a lead-time distribution."""
    p = 1.0 / (1.0 + mean_months)
    w = [p * (1 - p) ** k for k in range(horizon + 1)]
    t = sum(w)
    return [x / t for x in w]


def nights_share(gbv_share_pct: float, adr_ratio: float) -> float:
    """RNPL share of NIGHTS from its share of GBV.  p = s / (r(1-s) + s).
    DERIVED identity, research/notes/2026-09-10_rnpl-conversion-framework.md section 3."""
    s = gbv_share_pct / 100.0
    return s / (adr_ratio * (1 - s) + s)


def allocate(gross: float, idx: int, p_rnpl: float, delta_pp: float,
             w_base: list[float], w_rnpl: list[float]
             ) -> tuple[dict[int, float], dict[int, float], float]:
    """One booking cohort's cancellations.

    Returns (baseline_by_month, excess_timed_by_month, excess_total).
    Baseline: BASE_CANCEL_RATE of all booked nights, a fixed share in the booking month
    and the rest spread uniformly from the booking month to the stay month.
    Excess: delta_pp of the RNPL nights only, recognised at the PAYMENT DEADLINE, which
    sits 1 to 14 days before check-in (D002, D012) -- so in the stay month, or the month
    before. excess_total is the same quantity recognised instantly, for the M3/M4 split.
    """
    baseline: dict[int, float] = {}
    excess: dict[int, float] = {}

    base_total = gross * BASE_CANCEL_RATE
    booking_leg = base_total * BASE_CANCEL_IN_BOOKING_MONTH
    baseline[idx] = baseline.get(idx, 0.0) + booking_leg
    spread = base_total - booking_leg
    for lag, wt in enumerate(w_base):
        if wt <= 0:
            continue
        per = spread * wt / (lag + 1)
        for step in range(lag + 1):
            baseline[idx + step] = baseline.get(idx + step, 0.0) + per

    excess_total = 0.0
    if delta_pp > 0 and p_rnpl > 0:
        excess_total = gross * p_rnpl * (delta_pp / 100.0)
        for lag, wt in enumerate(w_rnpl):
            if wt <= 0:
                continue
            amt = excess_total * wt
            stay = idx + lag
            prior = max(idx, stay - 1)
            excess[stay] = excess.get(stay, 0.0) + amt * EXCESS_IN_STAY_MONTH
            excess[prior] = excess.get(prior, 0.0) + amt * (1 - EXCESS_IN_STAY_MONTH)
    return baseline, excess, excess_total


def solve_gross(w_base: list[float], targets: dict[str, float]) -> list[float]:
    """Solve monthly gross booked nights so reported nights hit every quarterly reference.

    Forward sweep: a cohort's cancellations land in its own month or later, never earlier.
    Run with the excess leg OFF, so the solve is independent of the share path and the
    propensity -- the reference is the no-RNPL-tail counterfactual by construction.

    AUDIT NOTE. Because the 2025 quarters are DISCLOSED actuals that already contain
    whatever RNPL excess cancellations really occurred, this solve nets that excess into
    'gross' and the scenario run then subtracts it a second time from the prior year. The
    resulting understatement of the y/y drag was measured at 0.001 to 0.002 growth points
    (3Q25 excess is 0.12% of 3Q25 nights), so the construction is sound. What DOES move
    the answer is the ASSUMED 2025 share path, worth up to 0.08 pts in 3Q26 and 0.28 pts
    in 4Q26. See the audit note, finding A.
    """
    n = len(MONTHS)
    gross = [0.0] * n
    inflow = [0.0] * n
    self_share = BASE_CANCEL_RATE * BASE_CANCEL_IN_BOOKING_MONTH
    self_share += BASE_CANCEL_RATE * (1 - BASE_CANCEL_IN_BOOKING_MONTH) * sum(
        w / (lag + 1) for lag, w in enumerate(w_base))
    for idx, m in enumerate(MONTHS):
        gross[idx] = (targets[MONTH_QUARTER[m]] / 3.0 + inflow[idx]) / (1.0 - self_share)
        base, _, _ = allocate(gross[idx], idx, 0.0, 0.0, w_base, w_base)
        for j, a in base.items():
            if j != idx and j < n:
                inflow[j] += a
    return gross


def cancellation_legs(gross: list[float], p_by_q: dict[str, float], delta_pp: float,
                      w_base: list[float], w_rnpl: list[float]
                      ) -> tuple[dict[str, float], dict[str, float]]:
    """Excess RNPL cancellations by quarter, on two recognition rules.

    timed   -- at the payment deadline (the real rule). This is M3 + M4.
    instant -- in the booking quarter. This is M4 alone: the steady-state propensity cost
               with all deferral removed.
    """
    n = len(MONTHS)
    timed = {q: 0.0 for q in QUARTERS}
    instant = {q: 0.0 for q in QUARTERS}
    for idx, m in enumerate(MONTHS):
        bq = MONTH_QUARTER[m]
        _, ex, tot = allocate(gross[idx], idx, p_by_q.get(bq, 0.0), delta_pp, w_base, w_rnpl)
        instant[bq] += tot
        for j, a in ex.items():
            if j < n:
                timed[MONTH_QUARTER[MONTHS[j]]] += a
    return timed, instant


def cohort_matrix(gross: list[float], p_by_q: dict[str, float], delta_pp: float,
                  w_base: list[float], w_rnpl: list[float]) -> list[dict]:
    """Booking quarter x cancellation-recognition quarter, millions of nights."""
    n = len(MONTHS)
    cell: dict[tuple[str, str], float] = {}
    for idx, m in enumerate(MONTHS):
        bq = MONTH_QUARTER[m]
        _, ex, _ = allocate(gross[idx], idx, p_by_q.get(bq, 0.0), delta_pp, w_base, w_rnpl)
        for j, a in ex.items():
            if j < n:
                cell[(bq, MONTH_QUARTER[MONTHS[j]])] = cell.get((bq, MONTH_QUARTER[MONTHS[j]]), 0.0) + a
    cols = ["3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
    rows = []
    for bq in cols:
        r = {"booking_quarter": bq, "units": "mm nights"}
        tot = 0.0
        for cq in cols:
            v = cell.get((bq, cq), 0.0)
            r[cq] = round(v, 3)
            tot += v
        r["cohort_total"] = round(tot, 3)
        rows.append(r)
    rec = {"booking_quarter": "RECOGNISED IN QUARTER", "units": "mm nights"}
    frm = {"booking_quarter": "of which from earlier cohorts, %", "units": "%"}
    for cq in cols:
        tot = sum(cell.get((bq, cq), 0.0) for bq in cols)
        own = cell.get((cq, cq), 0.0)
        rec[cq] = round(tot, 3)
        frm[cq] = round(100 * (1 - own / tot), 1) if tot > 0 else 0.0
    rows += [rec, frm]
    return rows


# ======================================================================================
# 5. The four mechanisms
# ======================================================================================

def m1_level_points(par: dict) -> dict[str, float]:
    """M1, conversion uplift and its dated lap, as a CORRECTION to the reference.

    The reference already laps the North American legs (PR #32 base: RNPL from 3Q26, fee
    and cancellation redesign from 4Q26) and carries NO ex-NA lap. So M1 here is exactly
    the three pieces PR #32 omits or mis-dates:

      (i)   ex-NA cancellation redesign + single fee tranche 1. Global from October to
            December 2025 (4Q25 letter, ledger D060/D024), so the y/y window closes
            EVERYWHERE from 4Q26. PR #32 laps it in NA only. Negative from 4Q26 on.
      (ii)  ex-NA RNPL. Live 17 Feb to 4 March 2026 (ledger D025-D029), i.e. the last 5 to
            6 weeks of 1Q26. So the 1Q27 lap is PARTIAL (5.5/13) and 2Q27 onward is full.
            PR #32 applies the whole 1.75 pts flat from 1Q27, which is too harsh in 1Q27.
      (iii) July-2026 expansion of eligible booking types (ledger D044), a POSITIVE level
            arriving inside 3Q26 whose own lap falls in 3Q27. Size undisclosed: ASSUMED.
      (iv)  a partial-quarter correction on the US lap. The 3Q25 call says "beginning of
            Q3"; the newsroom announcement is 14 August 2025. If US RNPL was live for less
            than the full quarter in 3Q25, the 3Q26 lap should not remove all of the fitted
            0.69 pts. Range 0 to +0.34 pts; this cuts AGAINST the short.
    """
    fee, rnpl, july, us = (par["exna_fee_cancel_pts"], par["exna_rnpl_pts"],
                           par["july_expansion_pts"], par["us_partial_lap_pts"])
    out = {}
    for q in REPORT:
        v = july * JULY_PROFILE[q]
        if q == "3Q26":
            v += us
        if q in ("4Q26", "1Q27", "2Q27", "3Q27", "4Q27"):
            v -= fee
        if q == "1Q27":
            v -= rnpl * EXNA_1Q27_PARTIAL
        if q in ("2Q27", "3Q27", "4Q27"):
            v -= rnpl
        out[q] = v
    return out


def m2_pullforward_points(par: dict, ref_n: dict[str, float]) -> dict[str, float]:
    """M2, one-time pull-forward from lengthening lead times.

    The RNPL cohort books L*u months earlier than it otherwise would. While the RNPL share
    is RISING, the quarter receives an extra d(p) * L * u / 3 of a quarter's nights. That
    addition is a flow, proportional to the CHANGE in share, and goes to zero at plateau.
    The y/y effect in the lapping quarter is therefore PF(q) - PF(q-4), in points of
    prior-year nights.

    NOT modelled anywhere else. PR #32 treats the whole fitted +2.40 as permanent level, so
    it implicitly sets M2 = 0. Theo's bridge carries -0.10/-0.20/-0.30 in 3Q26 only, which
    on PR #32's parameters implies 29% to 58% of the fitted RNPL level was pull-forward --
    a large implicit claim. This construction derives it from the share path instead, and
    finds the biggest reversal is in 1Q27, not 3Q26.
    """
    L, u = par["lead_months"], par["lead_uplift"]
    p = {q: nights_share(s, par["adr_ratio"]) for q, s in par["gbv_share"].items()}
    order = ["3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
    pf = {}
    prev = 0.0
    for q in order:
        pf[q] = max(0.0, p.get(q, 0.0) - prev) * L * u / 3.0
        prev = p.get(q, prev)
    return {q: (pf.get(q, 0.0) - pf.get(PRIOR[q], 0.0)) * 100.0 for q in REPORT}


def run_scenario(name: str, par: dict) -> tuple[list[dict], list[dict], list[dict]]:
    ref_n = reference_nights()
    w_base = lead_time_weights(par["lead_months"])
    w_rnpl = lead_time_weights(par["lead_months"] * (1 + par["lead_uplift"]))
    gross = solve_gross(w_base, ref_n)

    p_by_q = {q: nights_share(s, par["adr_ratio"]) for q, s in par["gbv_share"].items()}
    timed, instant = cancellation_legs(gross, p_by_q, par["delta_pp"], w_base, w_rnpl)
    keep = 1.0 - par["rebook"]

    m1 = m1_level_points(par)
    m2 = m2_pullforward_points(par, ref_n)

    rows, state = [], []
    nights = dict(DISCLOSED)
    for q in REPORT:
        pq = PRIOR[q]
        n_prior = nights[pq] if pq in nights else ref_n[pq]
        n_prior_ref = ref_n[pq]
        # The y/y effect of removing E nights this year and E_prior last year, in points.
        # This is the first-order-exact form of Krish's (growth_B - growth_A): it holds the
        # PRIOR year at the reference, which is the economically correct statement -- the
        # drag against a baseline that assumed the excess-cancellation burden RATIO was
        # unchanged y/y. It is linear in E, so M3 and M4 add exactly to the D1 tail.
        scale = ref_n[q] / n_prior_ref

        def pts(e_now: float, e_ago: float) -> float:
            return -keep * (e_now - e_ago * scale) / n_prior_ref * 100.0

        # M4: steady-state propensity, everything recognised in its booking quarter.
        m4 = pts(instant[q], instant[pq])
        # M3: deferral only. (timed - instant) now versus (timed - instant) a year ago.
        m3 = pts(timed[q] - instant[q], timed[pq] - instant[pq])
        total = m1[q] + m2[q] + m3 + m4
        growth = REFERENCE_GROWTH[q] + total
        nights[q] = n_prior * (1 + growth / 100.0)
        rows.append(dict(
            scenario=name, quarter=q, prior_quarter=pq,
            reference_growth_pct=round(REFERENCE_GROWTH[q], 2),
            m1_level_lap_pts=round(m1[q], 3),
            m2_pull_forward_pts=round(m2[q], 3),
            m3_cancellation_deferral_pts=round(m3, 3),
            m4_propensity_drag_pts=round(m4, 3),
            m3_plus_m4_tail_pts=round(m3 + m4, 3),
            total_rnpl_pts=round(total, 3),
            nights_yoy_pct=round(growth, 2),
            nights_mm=round(nights[q], 1),
            reference_nights_mm=round(ref_n[q], 1),
            prior_year_nights_mm=round(n_prior, 1),
        ))
        state.append(dict(
            scenario=name, quarter=q,
            rnpl_gbv_share_pct=par["gbv_share"].get(q),
            rnpl_nights_share_pct=round(100 * p_by_q.get(q, 0.0), 2),
            excess_cancellations_timed_mm=round(timed[q], 3),
            excess_cancellations_instant_mm=round(instant[q], 3),
            live_unpaid_backlog_nights_mm=round(live_backlog(gross, p_by_q, w_rnpl, q), 2),
            lead_time_months=par["lead_months"],
            rnpl_lead_time_months=round(par["lead_months"] * (1 + par["lead_uplift"]), 2),
            delta_pp=par["delta_pp"], rebook_offset=par["rebook"],
        ))
    # 2Q26 backlog is carried as the row the balance-sheet solve can be scored against.
    state.insert(0, dict(
        scenario=name, quarter="2Q26 (cross-check)",
        rnpl_gbv_share_pct=par["gbv_share"].get("2Q26"),
        rnpl_nights_share_pct=round(100 * p_by_q.get("2Q26", 0.0), 2),
        excess_cancellations_timed_mm=round(timed["2Q26"], 3),
        excess_cancellations_instant_mm=round(instant["2Q26"], 3),
        live_unpaid_backlog_nights_mm=round(live_backlog(gross, p_by_q, w_rnpl, "2Q26"), 2),
        lead_time_months=par["lead_months"],
        rnpl_lead_time_months=round(par["lead_months"] * (1 + par["lead_uplift"]), 2),
        delta_pp=par["delta_pp"], rebook_offset=par["rebook"]))
    matrix = cohort_matrix(gross, p_by_q, par["delta_pp"], w_base, w_rnpl)
    for r in matrix:
        r["scenario"] = name
    return rows, state, matrix


def live_backlog(gross: list[float], p_by_q: dict[str, float], w_rnpl: list[float],
                 quarter: str) -> float:
    """State variable: RNPL nights booked but not yet stayed at the END of `quarter`.

    This is the unpaid-at-risk stock (payment falls due days before check-in, so a live
    RNPL booking is unpaid for almost its whole life). CROSS-CHECK, not an input: the
    balance-sheet joint solve in research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md
    put the 30 June 2026 unpaid book at 7 to 19 million nights, against the 40 million
    illustrative exposure in outputs/rnpl-audit-20260910/materiality.md. A module value far
    outside 7 to 19 at 2Q26 means the share path or the lead time is wrong.
    """
    end = max(i for i, m in enumerate(MONTHS) if MONTH_QUARTER[m] == quarter)
    stock = 0.0
    for idx, m in enumerate(MONTHS):
        if idx > end:
            break
        rn = gross[idx] * p_by_q.get(MONTH_QUARTER[m], 0.0)
        # share of this cohort whose stay month is still ahead of `end`
        unstayed = sum(w for lag, w in enumerate(w_rnpl) if idx + lag > end)
        stock += rn * unstayed
    return stock


# ======================================================================================
# 6. Parameter register
# ======================================================================================

def parameters() -> list[dict]:
    P = lambda n, v, lab, src: dict(parameter=n, value=v, evidence_status=lab, source=src)
    return [
        P("reported nights 1Q24-2Q26", "disclosed quarterly series", "measured",
          "data/processed/overnight/02_kpi_panel_quarterly.csv; Airbnb quarterly summaries"),
        P("reference growth 3Q26 / 4Q26", "+9.89% / +8.90%", "derived (team baseline)",
          "research/notes/2026-09-10_nights-baseline-reconciliation.md s1.4; = PR #32 base"),
        P("reference growth 1Q27-4Q27", "+8.17% each", "derived (team model)",
          "origin/krish/nights-quarterly data/processed/nights_quarterly_total.csv, base, exna_lap=False"),
        P("RNPL GBV share 1Q26", "roughly 20%", "measured",
          "1Q26 shareholder letter, ledger D031 (official)"),
        P("RNPL GBV share 2Q26", "over 20%, used at 21%", "measured (lower bound)",
          "2Q26 call, ledger D043 -- stockanalysis.com mirror, not the official IR PDF"),
        P("RNPL GBV share 3Q25 / 4Q25", "2.5-6% / 7-12%", "assumed",
          "no 2025 quarterly share has ever been disclosed. The 4Q25 'over 70% adoption by "
          "eligible bookings' figure is eligible-GBV based and cannot be used here (D022)"),
        P("RNPL GBV share 3Q26 onward", "21-27%", "assumed",
          "direction supported by the July 2026 eligibility expansion (D044)"),
        P("RNPL / non-RNPL ADR ratio", "1.33x", "derived",
          "1Q26 ~4pts GBV on ~3pts nights = 4/3 marginal ADR (D032); 4Q25 gives 3/2. "
          "Relabelled from ASSUMED by research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md s1.7"),
        P("GBV share -> nights share", "p = s/(r(1-s)+s)", "derived",
          "research/notes/2026-09-10_rnpl-conversion-framework.md s3"),
        P("baseline cancellation rate", "16% of booked nights", "measured, unit of account unstated",
          "4Q25 call, ledger D018: 'an average of maybe 16% cancellation rate historically'. "
          "No base period, no denominator, not stated per night / per booking / per dollar"),
        P("incremental RNPL propensity delta", "+2 / +4 / +6 pp", "assumed",
          "+6.0 is management-IMPLIED: the whole 1.0pt rise in the platform rate (D017/D018) "
          "attributed to RNPL at the 1Q26 nights share. The 2Q26 Strict-to-Firm migration "
          "(D048) alone makes that unsafe. NEVER measured"),
        P("mean booking-to-check-in lead time", "2.2 months (1.8-3.0)", "derived",
          "Little's Law on the unearned-fee pool: opening unearned fees / quarterly revenue "
          "0.66-0.88x for pre-RNPL 2025, from origin/jessie/backlog-conversion"),
        P("lead-time distribution shape", "shifted geometric, whole months", "assumed",
          "Airbnb has never published a lead-time distribution; only the mean is anchored"),
        P("RNPL lead-time uplift u", "0 / 7 / 15%", "direction measured, magnitude assumed",
          "lengthening disclosed every print from 3Q25 (D010, D016, D039, D045). The only "
          "quantified lead-time move on record is -7% in April 2025, PRE-RNPL (D011)"),
        P("excess recognised in the stay month", "85%", "window measured, split assumed",
          "payment due 'shortly before the end of the free cancellation period' (D002); that "
          "window is 24h/5d/14d (D012, D060). AUDITED: worth 0.001 growth pts -- inert"),
        P("baseline cancels in the booking month", "25%", "mechanism measured, magnitude assumed",
          "24-hour grace period for bookings 7+ days ahead (D012). AUDITED: worth 0.000 pts -- inert"),
        P("same-quarter rebooking offset", "0 / 25 / 50%", "mechanism measured, magnitude assumed",
          "D002, D046. The calendar pilot's 32-44% reclosure is a descriptive lead, NOT a "
          "measured rebooking rate. AUDITED: the single widest assumption, +/-0.31 pts on 3Q26"),
        P("NA share of total nights", "28.8%", "measured",
          "data/processed/overnight/02_kpi_panel_quarterly.csv na_share_of_nights_pct"),
        P("PR #32 fitted product terms", "RNPL +2.40 / fee+cancel +2.29 pts of NA nights",
          "derived (team model, not disclosure)",
          "origin/krish/nights-quarterly. Two free parameters fitted on four WS10 NA "
          "estimates; identification by launch timing, cannot be error-bounded"),
        P("ex-NA fee + cancellation lap", "0.70-0.88 pts of total nights", "derived",
          "October-December 2025 global dates (D024, D060) plus the 40-50% ex-NA bundle split "
          "pinned out of sample by the 4Q25 'over 200bp' disclosure (D014)"),
        P("ex-NA RNPL lap", "0.87-1.05 pts of total nights", "derived",
          "residual of management's ~3.0 global points (D032) after the NA and ex-NA fee legs"),
        P("ex-NA 1Q27 partial-lap fraction", "5.5/13 of the quarter", "measured (dates)",
          "17 Feb worldwide; UK 18 Feb, AU/APAC 23 Feb, Canada 4 Mar (D025-D029)"),
        P("July 2026 expansion", "+0.10 to +0.30 pts", "assumed",
          "expansion of eligible booking types is disclosed (D044); the types are unnamed and "
          "the size has never been quantified. The largest unquantified OFFSET to the 3Q26 lap"),
        P("US partial-lap correction", "0 to +0.34 pts", "assumed (dates conflict)",
          "3Q25 call says 'beginning of Q3'; the newsroom announcement is 14 August 2025. "
          "Cuts AGAINST the short thesis and is kept on the record for that reason"),
        P("-3.4pp FX step / '82% determined' / +4.05% fee uplift / the 9/9 drift rule / "
          "'half of ADR is unit size' / the '+10.2% consensus'", "not used", "WITHDRAWN",
          "Do not quote as live. The '+10.2% consensus' is the team's own frozen 5 Nov card "
          "(WS13/WS14), per research/notes/2026-09-10_nights-baseline-reconciliation.md s1.2"),
    ]


# ======================================================================================
# 6b. Audit sensitivities: every number in the note, regenerated
# ======================================================================================

def _tail_only(par_over: dict) -> dict[str, float]:
    """M3+M4 for 3Q26/4Q26 under a parameter override, with M1 and M2 switched off."""
    par = dict(SCENARIOS["base"])
    par.update(dict(exna_fee_cancel_pts=0.0, exna_rnpl_pts=0.0, july_expansion_pts=0.0,
                    us_partial_lap_pts=0.0))
    par.update(par_over)
    rows, _, _ = run_scenario("_t", par)
    return {r["quarter"]: r["m3_plus_m4_tail_pts"] for r in rows}


def audit_sensitivities() -> list[dict]:
    global BASE_CANCEL_IN_BOOKING_MONTH, EXCESS_IN_STAY_MONTH
    ref = _tail_only({})
    out: list[dict] = []

    def add(test, value, t, note):
        out.append(dict(
            test=test, value=str(value),
            tail_3q26_pts=round(t["3Q26"], 3), tail_4q26_pts=round(t["4Q26"], 3),
            move_3q26_pts=round(t["3Q26"] - ref["3Q26"], 3),
            move_4q26_pts=round(t["4Q26"] - ref["4Q26"], 3),
            moves_3q26_by_more_than_0p2="YES" if abs(t["3Q26"] - ref["3Q26"]) > 0.2 else "no",
            note=note))

    add("reference (base scenario, M1/M2 off)", "delta=4pp, r=1.33, L=2.2, u=7%, rebook 25%",
        ref, "the cell every other row is measured against")

    # (c) the three assumptions the task names, plus the ones that actually matter
    o = BASE_CANCEL_IN_BOOKING_MONTH
    for v in (0.0, 0.25, 0.50):
        BASE_CANCEL_IN_BOOKING_MONTH = v
        add("c1 baseline cancellations recognised in the booking month", f"{v:.0%}", _tail_only({}),
            "24h grace period (D012). INERT: it applies in both years and cancels")
    BASE_CANCEL_IN_BOOKING_MONTH = o
    o = EXCESS_IN_STAY_MONTH
    for v in (0.70, 0.85, 1.00):
        EXCESS_IN_STAY_MONTH = v
        add("c2 excess cancellations recognised in the stay month", f"{v:.0%}", _tail_only({}),
            "only matters at quarter boundaries, i.e. one month in three. INERT")
    EXCESS_IN_STAY_MONTH = o
    for v in (0.0, 0.25, 0.50):
        add("c3 same-quarter rebooking offset", f"{v:.0%}", _tail_only({"rebook": v}),
            "THE widest assumption. Scales the whole tail linearly. Never measured")
    for v in (1.8, 2.2, 3.0):
        add("c4 mean lead time, months", v, _tail_only({"lead_months": v}),
            "derived range from Little's Law on the unearned-fee pool")
    for v in (1.00, 1.15, 1.25, 1.33):
        add("c5 RNPL / non-RNPL ADR ratio", v, _tail_only({"adr_ratio": v}),
            "matters only at a FIXED delta. Under the management-implied rule delta = 1/p, "
            "so delta x p is identically 1 and the ratio cancels exactly")
    for v in (2.0, 4.0, 6.0):
        add("c6 incremental RNPL propensity, pp", v, _tail_only({"delta_pp": v}),
            "scenario input in every cell; never measured")

    # (a) the base-year share path -- the real lever behind the forward solve question
    slow = dict(SCENARIOS["base"]["gbv_share"]); slow.update({"3Q25": 2.5, "4Q25": 7.0})
    fast = dict(SCENARIOS["base"]["gbv_share"]); fast.update({"3Q25": 6.0, "4Q25": 12.0})
    zero = dict(SCENARIOS["base"]["gbv_share"]); zero.update({"3Q25": 0.0, "4Q25": 0.0})
    add("a1 2025 base-year RNPL GBV share", "slow 2.5 / 7.0", _tail_only({"gbv_share": slow}),
        "a slower 2025 ramp lowers the prior-year base and WIDENS the y/y drag")
    add("a1 2025 base-year RNPL GBV share", "fast 6.0 / 12.0", _tail_only({"gbv_share": fast}),
        "a faster 2025 ramp raises the base and SHRINKS the drag")
    add("a2 2025 base-year RNPL share forced to ZERO", "0 / 0", _tail_only({"gbv_share": zero}),
        "the limiting 'pre-RNPL 2025 base' case the audit asks about. This is the ONLY route "
        "by which the forward solve's base-year treatment moves the answer materially, and it "
        "moves 4Q26 more than 3Q26")

    # (b) pull-forward against PR #32's permanent-level treatment
    for x in (0.10, 0.25, 0.50, 1.00):
        out.append(dict(
            test="b1 x% of PR #32's fitted +2.40 NA RNPL points is pull-forward, not level",
            value=f"x={x:.0%}",
            tail_3q26_pts="", tail_4q26_pts="",
            move_3q26_pts=round(-x * PR32_RNPL_NA_PTS * NA_SHARE, 3), move_4q26_pts="",
            moves_3q26_by_more_than_0p2="YES" if x * PR32_RNPL_NA_PTS * NA_SHARE > 0.2 else "no",
            note="PR #32 sets x=0. Theo's bridge uses -0.10 to -0.30 pts in 3Q26, which implies "
                 f"x = {0.10 / (PR32_RNPL_NA_PTS * NA_SHARE):.0%} to "
                 f"{0.30 / (PR32_RNPL_NA_PTS * NA_SHARE):.0%}"))
    for name in SCENARIOS:
        m2 = m2_pullforward_points(SCENARIOS[name], reference_nights())
        out.append(dict(
            test="b2 pull-forward from the share path, M2", value=name,
            tail_3q26_pts="", tail_4q26_pts="",
            move_3q26_pts=round(m2["3Q26"], 3), move_4q26_pts=round(m2["4Q26"], 3),
            moves_3q26_by_more_than_0p2="YES" if abs(m2["3Q26"]) > 0.2 else "no",
            note=f"1Q27 {m2['1Q27']:+.2f} pts, 2Q27 {m2['2Q27']:+.2f} pts. The biggest "
                 "reversal is 1Q27, which NO team model carries"))

    # (d) the ex-NA lap, three treatments
    for lab, lo, hi in (
        ("d 4Q26 ex-NA fee + cancellation lap", 0.70, 0.88),
        ("d 1Q27 dated total (fee lap carried + 5.5/13 of the ex-NA RNPL lap)",
         0.70 + EXNA_1Q27_PARTIAL * 0.87, 0.88 + EXNA_1Q27_PARTIAL * 1.05),
        ("d 2Q27+ dated total", 0.70 + 0.87, 0.88 + 1.05),
    ):
        pr32 = 0.0 if "4Q26" in lab else 1.75
        out.append(dict(test=lab, value=f"-{hi:.2f} to -{lo:.2f} pts",
                        tail_3q26_pts="", tail_4q26_pts="",
                        move_3q26_pts="", move_4q26_pts="",
                        moves_3q26_by_more_than_0p2="",
                        note=f"PR #32 carries -{pr32:.2f}. Difference vs PR #32: "
                             f"{pr32 - hi:+.2f} to {pr32 - lo:+.2f} pts"))
    for wk in (13.0, 9.0, 6.5):
        out.append(dict(
            test="d US RNPL partial-lap symmetry: weeks live of 13 in 3Q25", value=wk,
            tail_3q26_pts="", tail_4q26_pts="",
            move_3q26_pts=round(PR32_RNPL_NA_PTS * NA_SHARE * (1 - wk / 13.0), 3),
            move_4q26_pts="", moves_3q26_by_more_than_0p2="",
            note="D applies the partial-lap logic to ex-NA in 1Q27 but nobody applies it to "
                 "US RNPL in 3Q26. 'Beginning of Q3' (3Q25 call) vs 14 Aug (newsroom). "
                 "Cuts AGAINST the short"))
    return out


# ======================================================================================
# 7. Write
# ======================================================================================

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def fy27(rows: list[dict], scenario: str) -> tuple[float, float]:
    r = {x["quarter"]: x for x in rows if x["scenario"] == scenario}
    num = sum(r[q]["nights_mm"] for q in ("1Q27", "2Q27", "3Q27", "4Q27"))
    den = (DISCLOSED["1Q26"] + DISCLOSED["2Q26"]
           + r["3Q26"]["nights_mm"] + r["4Q26"]["nights_mm"])
    return num, (num / den - 1) * 100


def main() -> int:
    # ---- self-checks -----------------------------------------------------------------
    w = lead_time_weights(2.2)
    assert math.isclose(sum(w), 1.0, abs_tol=1e-9)
    assert 1.9 < sum(k * x for k, x in enumerate(w)) < 2.3
    ref_n = reference_nights()
    g = solve_gross(w, ref_n)
    chk = {q: sum(g[MONTH_INDEX[m]] for m in MONTHS if MONTH_QUARTER[m] == q) for q in QUARTERS}
    rep = {}
    for q in QUARTERS:
        rep[q] = 0.0
    land = [0.0] * len(MONTHS)
    for idx, m in enumerate(MONTHS):
        b, _, _ = allocate(g[idx], idx, 0.0, 0.0, w, w)
        for j, a in b.items():
            if j < len(MONTHS):
                land[j] += a
    for idx, m in enumerate(MONTHS):
        rep[MONTH_QUARTER[m]] += g[idx] - land[idx]
    for q in ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26"]:
        assert math.isclose(rep[q], ref_n[q], rel_tol=2e-3), f"{q}: {rep[q]:.2f} vs {ref_n[q]:.2f}"

    # M3 + M4 must reproduce the D1 central cell (share_central, r=1.25, 2.2m, +7%, 25%
    # rebook, management-implied 6.0pp): 3Q26 -0.93, 4Q26 -0.86.
    d1 = dict(gbv_share={"3Q25": 4.0, "4Q25": 9.0, "1Q26": 20.0, "2Q26": 21.0, "3Q26": 22.0,
                         "4Q26": 23.0, "1Q27": 23.0, "2Q27": 23.0, "3Q27": 23.0,
                         "4Q27": 23.0, "1Q28": 23.0, "2Q28": 23.0},
              adr_ratio=1.25, delta_pp=6.0, lead_months=2.2, lead_uplift=0.07, rebook=0.25,
              exna_fee_cancel_pts=0.0, exna_rnpl_pts=0.0, july_expansion_pts=0.0,
              us_partial_lap_pts=0.0)
    d1_rows, _, _ = run_scenario("_d1check", d1)
    t3 = [r for r in d1_rows if r["quarter"] == "3Q26"][0]["m3_plus_m4_tail_pts"]
    t4 = [r for r in d1_rows if r["quarter"] == "4Q26"][0]["m3_plus_m4_tail_pts"]
    assert abs(t3 - (-0.93)) < 0.02, f"M3+M4 3Q26 {t3} != D1 -0.93"
    assert abs(t4 - (-0.86)) < 0.02, f"M3+M4 4Q26 {t4} != D1 -0.86"
    print(f"self-check: M3+M4 reproduces D1 central cell  3Q26 {t3:+.2f} (D1 -0.93), "
          f"4Q26 {t4:+.2f} (D1 -0.86)")

    # ---- run -------------------------------------------------------------------------
    rows: list[dict] = []
    state: list[dict] = []
    matrices: list[dict] = []
    for name, par in SCENARIOS.items():
        r, s, mx = run_scenario(name, par)
        rows += r
        state += s
        matrices += mx

    for name in SCENARIOS:
        num, gr = fy27(rows, name)
        rows.append(dict(scenario=name, quarter="FY27", prior_quarter="FY26",
                         reference_growth_pct="", m1_level_lap_pts="", m2_pull_forward_pts="",
                         m3_cancellation_deferral_pts="", m4_propensity_drag_pts="",
                         m3_plus_m4_tail_pts="", total_rnpl_pts="",
                         nights_yoy_pct=round(gr, 2), nights_mm=round(num, 1),
                         reference_nights_mm="", prior_year_nights_mm=""))

    write_csv(OUT / "rnpl_nights_module.csv", rows)
    write_csv(OUT / "rnpl_nights_module_state.csv", state)
    write_csv(OUT / "rnpl_nights_module_params.csv", parameters())
    write_csv(OUT / "rnpl_nights_module_cohort_matrix.csv", matrices)
    write_csv(OUT / "rnpl_nights_module_audit_sensitivities.csv", audit_sensitivities())

    # ---- print -----------------------------------------------------------------------
    print("\nUNIFIED RNPL NIGHTS MODULE -- quarterly y/y, contribution by mechanism (growth points)")
    print("Reference = team baseline 3Q26/4Q26, PR #32 base NA-lap-only 1Q27-4Q27 (no ex-NA lap)\n")
    hdr = (f"{'scen':>5} {'qtr':>5} {'ref%':>7} {'M1 lvl':>7} {'M2 pf':>7} {'M3 def':>7} "
           f"{'M4 prop':>8} {'total':>7} {'y/y %':>7} {'nights':>8}")
    for name in SCENARIOS:
        print(hdr if name == "bear" else "")
        for r in [x for x in rows if x["scenario"] == name and x["quarter"] in REPORT]:
            print(f"{name:>5} {r['quarter']:>5} {r['reference_growth_pct']:>7.2f} "
                  f"{r['m1_level_lap_pts']:>7.2f} {r['m2_pull_forward_pts']:>7.2f} "
                  f"{r['m3_cancellation_deferral_pts']:>7.2f} {r['m4_propensity_drag_pts']:>8.2f} "
                  f"{r['total_rnpl_pts']:>7.2f} {r['nights_yoy_pct']:>7.2f} {r['nights_mm']:>8.1f}")
        num, gr = fy27(rows, name)
        print(f"{name:>5} {'FY27':>5} {'':>7} {'':>7} {'':>7} {'':>7} {'':>8} {'':>7} "
              f"{gr:>7.2f} {num:>8.1f}")

    print("\nState variables (base): live unpaid RNPL backlog, nights share")
    for s in [x for x in state if x["scenario"] == "base"]:
        print(f"  {s['quarter']}: RNPL nights share {s['rnpl_nights_share_pct']:.1f}%, "
              f"live unpaid backlog {s['live_unpaid_backlog_nights_mm']:.1f}mm, "
              f"excess cancellations recognised {s['excess_cancellations_timed_mm']:.2f}mm")
    print("  cross-check: the balance-sheet solve put the 30 Jun 2026 unpaid book at 7-19mm nights")

    print(f"\nwrote {OUT / 'rnpl_nights_module.csv'}")
    print(f"wrote {OUT / 'rnpl_nights_module_state.csv'}")
    print(f"wrote {OUT / 'rnpl_nights_module_params.csv'}")
    print("\nAudit sensitivities: what moves the 3Q26 tail by more than 0.2 growth points")
    for r in audit_sensitivities():
        if r["moves_3q26_by_more_than_0p2"] == "YES":
            print(f"  {r['test']} = {r['value']}: {r['move_3q26_pts']:+.2f} pts")

    print(f"\nwrote {OUT / 'rnpl_nights_module_cohort_matrix.csv'}")
    print(f"wrote {OUT / 'rnpl_nights_module_audit_sensitivities.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
