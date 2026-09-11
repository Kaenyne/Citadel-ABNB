"""WS D, deliverable 2: RNPL cohort survival and timing arithmetic for 3Q26 and 4Q26.

Answers the RNPL handoff's next-steps item 4 and the part of item 5 that asks for both
years to be modelled. Builds a monthly booking-cohort engine with an explicit
booking-month by stay-month matrix and a booking-month by cancellation-month matrix,
then reports the incremental reported-nights effect against the team baseline of
3Q26 +9.9% (146.8mm) and 4Q26 +8.9% (132.7mm).

Design, and why it is built this way
-----------------------------------
The disclosed KPI is a transaction-period metric: bookings created in a quarter less
cancellations and alterations recorded in that quarter, including cancellations of older
bookings (10-K FY2025, ledger D054). So a cancellation-propensity assumption cannot be
turned into a growth effect without a lead-time distribution and a cancellation-timing
rule, and it must be applied to BOTH years or the prior-year denominator is wrong.

Two runs:
  Run A, reference. Incremental RNPL cancellation propensity = 0. Gross monthly bookings
    are solved so that reported nights reproduce the disclosed 2024, 2025 and 1H26
    quarters exactly and the team baseline in 3Q26 and 4Q26.
  Run B, scenario. The SAME gross booking path, with an incremental RNPL cancellation
    propensity and an RNPL share path. Reported nights change in both years.

The reported effect is growth_B minus growth_A in points, so the 2025 denominator carries
its own RNPL cancellations. That is what makes the answer far smaller than applying a
lifetime cancellation rate to a net-nights forecast, which the handoff forbids.

Nothing here is applied to the live model. Every parameter is labelled sourced, derived
or assumed in D1_rnpl_parameters.csv.

Run:  py -3.13 analysis/src/overnight2/D1_rnpl_cohort_scenarios.py
"""

from __future__ import annotations

import csv
import itertools
import math
from pathlib import Path

HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[3]
OUT = WORKTREE / "data/processed/overnight2/D"

# ======================================================================================
# Inputs
# ======================================================================================

# Disclosed reported Nights and Seats Booked, millions. SOURCED:
# data/processed/overnight/02_kpi_panel_quarterly.csv in the main tree, which reconciles
# to the Airbnb quarterly summaries.
DISCLOSED = {
    "1Q24": 132.6, "2Q24": 125.1, "3Q24": 122.8, "4Q24": 111.0,
    "1Q25": 143.1, "2Q25": 134.4, "3Q25": 133.6, "4Q25": 121.9,
    "1Q26": 156.2, "2Q26": 148.3,
}
# Team reconciled baseline. SOURCED: research/notes/2026-09-10_nights-baseline-reconciliation.md
BASELINE = {"3Q26": 146.8, "4Q26": 132.7}
BASELINE_GROWTH = {"3Q26": 9.89, "4Q26": 8.90}

QUARTERS = [
    "1Q24", "2Q24", "3Q24", "4Q24",
    "1Q25", "2Q25", "3Q25", "4Q25",
    "1Q26", "2Q26", "3Q26", "4Q26",
    "1Q27", "2Q27",
]
# 1Q27 and 2Q27 exist only to absorb cohorts; their targets are a flat extension and are
# never reported on.
TARGETS = {**DISCLOSED, **BASELINE, "1Q27": 169.0, "2Q27": 160.4}

MONTHS: list[str] = []
for quarter in QUARTERS:
    q = int(quarter[0])
    yy = 2000 + int(quarter[2:])
    for offset in range(3):
        MONTHS.append(f"{yy}-{(q - 1) * 3 + 1 + offset:02d}")
MONTH_INDEX = {m: i for i, m in enumerate(MONTHS)}
MONTH_QUARTER = {}
for quarter in QUARTERS:
    q = int(quarter[0])
    yy = 2000 + int(quarter[2:])
    for offset in range(3):
        MONTH_QUARTER[f"{yy}-{(q - 1) * 3 + 1 + offset:02d}"] = quarter

# --------------------------------------------------------------------------------------
# RNPL share of GBV by quarter, percent.
# SOURCED: 1Q26 roughly 20% (ledger D031, official 1Q26 letter); 2Q26 over 20%
# (ledger D043, call mirror only, taken here at 21 as a stated lower bound).
# ASSUMED: 3Q25 and 4Q25 ramp, and the 3Q26 / 4Q26 path. Airbnb has never disclosed a
# 2025 quarterly GBV share. The 4Q25 "over 70% adoption by eligible bookings" figure
# (ledger D022) is a share of ELIGIBLE bookings on a GBV basis, not of total GBV, so it
# cannot be used for this path.
# --------------------------------------------------------------------------------------
GBV_SHARE_PATHS = {
    # name: {quarter: percent of GBV}
    "share_central": {"3Q25": 4.0, "4Q25": 9.0, "1Q26": 20.0, "2Q26": 21.0,
                      "3Q26": 22.0, "4Q26": 23.0, "1Q27": 23.0, "2Q27": 23.0},
    "share_flat_2h26": {"3Q25": 4.0, "4Q25": 9.0, "1Q26": 20.0, "2Q26": 21.0,
                        "3Q26": 21.0, "4Q26": 21.0, "1Q27": 21.0, "2Q27": 21.0},
    "share_high_2h26": {"3Q25": 4.0, "4Q25": 9.0, "1Q26": 20.0, "2Q26": 21.0,
                        "3Q26": 25.0, "4Q26": 27.0, "1Q27": 27.0, "2Q27": 27.0},
    # A faster 2025 US ramp raises the prior-year base and therefore SHRINKS the y/y drag.
    "share_fast_2025": {"3Q25": 6.0, "4Q25": 12.0, "1Q26": 20.0, "2Q26": 21.0,
                        "3Q26": 22.0, "4Q26": 23.0, "1Q27": 23.0, "2Q27": 23.0},
    # A slower 2025 ramp lowers the base and widens the drag. This is the bear share path.
    "share_slow_2025": {"3Q25": 2.5, "4Q25": 7.0, "1Q26": 20.0, "2Q26": 21.0,
                        "3Q26": 22.0, "4Q26": 23.0, "1Q27": 23.0, "2Q27": 23.0},
}

# RNPL ADR divided by non-RNPL ADR. Direction SOURCED (mix shift to larger entire homes,
# especially four or more bedrooms, and a contribution to the ADR increase: ledger D016,
# D033, D045). Magnitude ASSUMED; Airbnb has never published the ratio.
ADR_RATIOS = {"adr_equal": 1.00, "adr_plus15": 1.15, "adr_plus25": 1.25}

# Baseline lifetime cancellation rate on non-RNPL bookings, share of booked nights.
# SOURCED as a platform average with no stated unit of account: "an average of maybe 16%
# cancellation rate historically" (ledger D018).
BASE_CANCEL_RATE = 0.16

# Incremental lifetime cancellation propensity on RNPL bookings, percentage points of
# booked nights, versus an otherwise comparable non-RNPL booking.
# The four fixed values are the scenario grid the task specifies. "mgmt_implied" is
# computed per scenario from the 16 to 17 platform remark: excess = 1.0 / nights_share.
DELTA_SCENARIOS = [0.0, 1.0, 2.0, 4.0, "mgmt_implied"]

# Mean booking-to-check-in lead time, months.
# DERIVED from disclosure, not assumed: Little's Law on the unearned-fee pool. Jessie's
# backlog table (origin/jessie/backlog-conversion, research/notes/2026-09-05_eu-platform-
# and-backlog.md section 3b) gives opening unearned fees divided by the quarter's revenue
# as 0.71x in Q1, 0.88x in Q2, 0.70x in Q3 and 0.66x in Q4 for 2025. Mean residence time
# of a booked-but-unstayed fee is stock over outflow, so 0.66 to 0.88 quarters, that is
# 2.0 to 2.6 months. Revenue is recognised at check-in, so this is booking to check-in.
# Caveats: the pool holds fees only, so Pay Less Upfront understates it; long-term stays
# are billed monthly; and from 3Q25 RNPL itself corrupts the ratio, which is why only the
# pre-RNPL 2022 to 2025 seasonal constants are used.
LEAD_TIME_MONTHS = {"lead_1.8": 1.8, "lead_2.2": 2.2, "lead_3.0": 3.0}

# RNPL lengthens lead times. Direction SOURCED in every print from 3Q25 (ledger D010,
# D016, D039, D045). The only quantified y/y lead-time move Airbnb has ever given is
# minus 7 percent in April 2025, pre-RNPL (ledger D011), so 7 percent is used as the
# scale at which management calls a lead-time shift notable. Magnitude ASSUMED.
LEAD_TIME_UPLIFT = {"uplift_0": 0.00, "uplift_7": 0.07, "uplift_15": 0.15}

# Share of a cohort's EXCESS RNPL cancellations recognised in the stay month rather than
# the month before. The 1-to-14-day window is SOURCED: RNPL payment falls due "shortly
# before the end of the listing's free cancellation period" (ledger D002), and the free
# window is 24 hours before check-in for flexible, 5 days for moderate, and 14 days under
# the new Limited policy (ledger D012). The 0.85 split is ASSUMED.
EXCESS_IN_STAY_MONTH = 0.85

# Share of BASELINE cancellations recognised in the booking month itself. Mechanism
# SOURCED: from October 2025 guests booking more than 7 days ahead get a 24-hour full
# refund grace period (ledger D012). Magnitude ASSUMED. This term is close to y/y neutral
# because it applies in both years, and it is held constant across runs.
BASE_CANCEL_IN_BOOKING_MONTH = 0.25

# Same-quarter net rebooking offset on excess cancelled nights. Mechanism SOURCED:
# "because the payment from guests is always due before the free cancellation period ends,
# hosts have time to secure another booking even if a guest cancels" (ledger D002), and
# "enabling hosts to lock in earlier calendar share" (D046). Magnitudes are the three the
# task specifies; the calendar pilot's 32 to 44 percent reclosure of reopened short-run
# dates is a descriptive lead, not a measured rebooking rate.
REBOOK_OFFSETS = [0.0, 0.25, 0.50]


# ======================================================================================
# Lead-time distribution: the booking-month by stay-month matrix
# ======================================================================================

def lead_time_weights(mean_months: float, horizon: int = 14) -> list[float]:
    """Discrete booking-to-stay lag distribution over whole months, 0..horizon.

    A shifted geometric in whole months. k = 0 means the stay falls in the booking month.
    Chosen for transparency and because Airbnb discloses no lead-time distribution: only
    the mean is anchored, by the unearned-fee residence-time derivation above.
    """
    if mean_months <= 0:
        raise ValueError("mean lead time must be positive")
    # Geometric with mean m has success probability 1/(1+m) on support 0,1,2,...
    p = 1.0 / (1.0 + mean_months)
    weights = [p * (1 - p) ** k for k in range(horizon + 1)]
    total = sum(weights)
    return [w / total for w in weights]


def stay_month_index(booking_idx: int, lag: int) -> int:
    return booking_idx + lag


# ======================================================================================
# Cohort engine
# ======================================================================================

def allocate_cancellations(
    gross: float,
    booking_idx: int,
    rnpl_nights_share: float,
    delta_pp: float,
    lead_weights: list[float],
    lead_weights_rnpl: list[float],
) -> tuple[dict[int, float], dict[int, float]]:
    """Allocate one booking cohort's cancellations to recognition months.

    Returns (baseline_by_month, excess_by_month). Both are nights in millions.

    Baseline leg: BASE_CANCEL_RATE of all booked nights. A fixed share lands in the
    booking month (the 24-hour grace period), the rest is spread uniformly over the
    months from the booking month to the stay month inclusive, weighted by the lead-time
    distribution. This is the same in both runs and both years.

    Excess leg: delta_pp of the RNPL nights only, recognised at the payment deadline,
    which sits days before check-in. EXCESS_IN_STAY_MONTH of it lands in the stay month
    and the remainder in the month before.
    """
    baseline: dict[int, float] = {}
    excess: dict[int, float] = {}

    base_total = gross * BASE_CANCEL_RATE
    in_booking_month = base_total * BASE_CANCEL_IN_BOOKING_MONTH
    baseline[booking_idx] = baseline.get(booking_idx, 0.0) + in_booking_month
    spread_total = base_total - in_booking_month
    for lag, weight in enumerate(lead_weights):
        if weight <= 0:
            continue
        amount = spread_total * weight
        span = lag + 1  # booking month through stay month inclusive
        per_month = amount / span
        for step in range(span):
            idx = booking_idx + step
            baseline[idx] = baseline.get(idx, 0.0) + per_month

    if delta_pp > 0 and rnpl_nights_share > 0:
        excess_total = gross * rnpl_nights_share * (delta_pp / 100.0)
        for lag, weight in enumerate(lead_weights_rnpl):
            if weight <= 0:
                continue
            amount = excess_total * weight
            stay_idx = stay_month_index(booking_idx, lag)
            excess[stay_idx] = excess.get(stay_idx, 0.0) + amount * EXCESS_IN_STAY_MONTH
            prior_idx = max(booking_idx, stay_idx - 1)
            excess[prior_idx] = excess.get(prior_idx, 0.0) + amount * (1 - EXCESS_IN_STAY_MONTH)

    return baseline, excess


def solve_reference_gross(lead_weights: list[float]) -> list[float]:
    """Solve monthly gross booked nights so reported nights hit every quarterly target.

    Run A only: no RNPL excess, so the solve is independent of the share path. Monthly
    targets are the quarterly target split in thirds (ASSUMED within-quarter shape; only
    quarterly aggregates are reported on). Forward solve: a cohort's cancellations land in
    its own month and later months, never earlier, so month m's gross depends only on
    itself and on inflow already determined.
    """
    n = len(MONTHS)
    gross = [0.0] * n
    inflow = [0.0] * n  # baseline cancellations landing in each month from earlier cohorts

    # Self share: the fraction of a cohort's baseline cancellations recognised in its own
    # booking month.
    self_share = BASE_CANCEL_RATE * BASE_CANCEL_IN_BOOKING_MONTH
    self_share += BASE_CANCEL_RATE * (1 - BASE_CANCEL_IN_BOOKING_MONTH) * sum(
        w / (lag + 1) for lag, w in enumerate(lead_weights)
    )

    for idx, month in enumerate(MONTHS):
        target = TARGETS[MONTH_QUARTER[month]] / 3.0
        gross[idx] = (target + inflow[idx]) / (1.0 - self_share)
        baseline, _ = allocate_cancellations(
            gross[idx], idx, 0.0, 0.0, lead_weights, lead_weights
        )
        for j, amount in baseline.items():
            if j == idx or j >= n:
                continue
            inflow[j] += amount
    return gross


def run_scenario(
    gross: list[float],
    nights_share_by_quarter: dict[str, float],
    delta_pp: float,
    lead_weights: list[float],
    lead_weights_rnpl: list[float],
    rebook: float,
) -> dict[str, float]:
    """Reported nights by quarter for a given cancellation-propensity scenario."""
    n = len(MONTHS)
    reported_month = [0.0] * n
    base_land = [0.0] * n
    excess_land = [0.0] * n

    for idx, month in enumerate(MONTHS):
        share = nights_share_by_quarter.get(MONTH_QUARTER[month], 0.0)
        baseline, excess = allocate_cancellations(
            gross[idx], idx, share, delta_pp, lead_weights, lead_weights_rnpl
        )
        for j, amount in baseline.items():
            if j < n:
                base_land[j] += amount
        for j, amount in excess.items():
            if j < n:
                excess_land[j] += amount

    for idx in range(n):
        # Rebooking returns a share of excess cancelled nights as a new booking in the
        # same month, so it offsets the excess only.
        reported_month[idx] = (
            gross[idx] - base_land[idx] - excess_land[idx] * (1.0 - rebook)
        )

    out: dict[str, float] = {}
    for quarter in QUARTERS:
        out[quarter] = sum(
            reported_month[MONTH_INDEX[m]] for m in MONTHS if MONTH_QUARTER[m] == quarter
        )
    return out


def nights_share_path(gbv_path: dict[str, float], adr_ratio: float) -> dict[str, float]:
    """Convert an RNPL GBV share path into an RNPL nights share path.

    p_nights = s / (r * (1 - s) + s), with s the GBV share and r the RNPL to non-RNPL ADR
    ratio. Identity from research/notes/2026-09-10_rnpl-conversion-framework.md section 3.
    """
    out = {}
    for quarter, pct in gbv_path.items():
        s = pct / 100.0
        out[quarter] = s / (adr_ratio * (1 - s) + s)
    return out


# ======================================================================================
# Build the scenario grid
# ======================================================================================

def build_grid() -> list[dict]:
    rows: list[dict] = []
    reference_cache: dict[str, list[float]] = {}
    reference_reported: dict[str, dict[str, float]] = {}

    for lead_name, lead_mean in LEAD_TIME_MONTHS.items():
        weights = lead_time_weights(lead_mean)
        gross = solve_reference_gross(weights)
        reference_cache[lead_name] = gross
        reference_reported[lead_name] = run_scenario(
            gross, {}, 0.0, weights, weights, 0.0
        )

    combos = itertools.product(
        GBV_SHARE_PATHS.items(), ADR_RATIOS.items(), DELTA_SCENARIOS,
        LEAD_TIME_MONTHS.items(), LEAD_TIME_UPLIFT.items(), REBOOK_OFFSETS,
    )
    for (share_name, gbv_path), (adr_name, adr_ratio), delta, \
            (lead_name, lead_mean), (uplift_name, uplift), rebook in combos:
        shares = nights_share_path(gbv_path, adr_ratio)
        if delta == "mgmt_implied":
            # The 16 to 17 platform remark implies a 1.0-point rise in the platform-wide
            # cancellation rate. If RNPL alone explains it, its excess propensity is
            # 1.0 / p. Evaluated at the 1Q26 nights share, the quarter whose GBV share is
            # officially disclosed.
            anchor = shares.get("1Q26", 0.0)
            if anchor <= 0:
                continue
            delta_pp = 1.0 / anchor
            delta_label = "mgmt_implied"
        else:
            delta_pp = float(delta)
            delta_label = f"delta_{delta:.0f}pp"

        base_weights = lead_time_weights(lead_mean)
        rnpl_weights = lead_time_weights(lead_mean * (1.0 + uplift))
        gross = reference_cache[lead_name]
        ref = reference_reported[lead_name]
        scen = run_scenario(gross, shares, delta_pp, base_weights, rnpl_weights, rebook)

        row = {
            "share_path": share_name, "adr_ratio": adr_name, "delta_scenario": delta_label,
            "delta_pp_applied": round(delta_pp, 3),
            "lead_time": lead_name, "lead_uplift": uplift_name, "rebook_offset": rebook,
            "rnpl_nights_share_1q26_pct": round(shares.get("1Q26", 0) * 100, 2),
            "rnpl_nights_share_3q26_pct": round(shares.get("3Q26", 0) * 100, 2),
            "rnpl_nights_share_4q26_pct": round(shares.get("4Q26", 0) * 100, 2),
        }
        for quarter, prior in [("3Q26", "3Q25"), ("4Q26", "4Q25")]:
            growth_ref = (ref[quarter] / ref[prior] - 1) * 100
            growth_scen = (scen[quarter] / scen[prior] - 1) * 100
            row[f"{quarter}_nights_delta_mm"] = round(scen[quarter] - ref[quarter], 3)
            row[f"{quarter}_prior_year_delta_mm"] = round(scen[prior] - ref[prior], 3)
            row[f"{quarter}_growth_delta_pts"] = round(growth_scen - growth_ref, 3)
            row[f"{quarter}_nights_mm"] = round(
                BASELINE[quarter] * (1 + (growth_scen - growth_ref) / 100
                                     * DISCLOSED[prior] / BASELINE[quarter]), 2)
            row[f"{quarter}_growth_pct"] = round(
                BASELINE_GROWTH[quarter] + growth_scen - growth_ref, 2)
        rows.append(row)
    return rows


# ======================================================================================
# Level and anniversary arithmetic, separate from the cancellation engine
# ======================================================================================

def cohort_matrices(
    gross: list[float],
    shares: dict[str, float],
    delta_pp: float,
    lead_weights: list[float],
    lead_weights_rnpl: list[float],
) -> tuple[list[dict], list[dict]]:
    """The two matrices the handoff's next-steps item 4 asks for, at quarter resolution.

    Matrix 1, booking quarter by cancellation quarter: where each booking cohort's EXCESS
    RNPL cancellations are recognised. This is the cancellation tail.
    Matrix 2, booking quarter by stay quarter: where each booking cohort's nights are
    consumed. This is the timing bridge between the booked KPI and revenue.
    """
    n = len(MONTHS)
    cancel: dict[tuple[str, str], float] = {}
    stay: dict[tuple[str, str], float] = {}
    for idx, month in enumerate(MONTHS):
        bq = MONTH_QUARTER[month]
        share = shares.get(bq, 0.0)
        _, excess = allocate_cancellations(
            gross[idx], idx, share, delta_pp, lead_weights, lead_weights_rnpl
        )
        for j, amount in excess.items():
            if j < n:
                cancel[(bq, MONTH_QUARTER[MONTHS[j]])] = (
                    cancel.get((bq, MONTH_QUARTER[MONTHS[j]]), 0.0) + amount)
        for lag, weight in enumerate(lead_weights):
            j = idx + lag
            if j >= n:
                continue
            sq = MONTH_QUARTER[MONTHS[j]]
            stay[(bq, sq)] = stay.get((bq, sq), 0.0) + gross[idx] * weight

    report_quarters = ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26"]

    def to_rows(matrix: dict[tuple[str, str], float], label: str) -> list[dict]:
        rows = []
        for bq in report_quarters:
            row = {"booking_quarter": bq, "units": "millions of nights", "matrix": label}
            total = 0.0
            for tq in report_quarters:
                value = matrix.get((bq, tq), 0.0)
                row[tq] = round(value, 3)
                total += value
            row["total_in_window"] = round(total, 3)
            rows.append(row)
        return rows

    return (to_rows(cancel, "excess_rnpl_cancellations_by_recognition_quarter"),
            to_rows(stay, "booked_nights_by_stay_quarter"))


def lap_table() -> list[dict]:
    """The product-level anniversary, built only from disclosed bundle contributions.

    A one-off level gain stops contributing to y/y growth once fully lapped, with no
    deterioration in conversion. That is distinct from a cancellation drag and must not be
    counted twice. Dates come from the ledger.
    """
    na_share = 0.288  # SOURCED: main tree data/processed/overnight/02_kpi_panel_quarterly.csv
    rows = [
        dict(
            feature="RNPL, US only",
            live_from="3Q25 (call: beginning of Q3; letter: August)",
            geography="US guests, US domestic stays, flexible or moderate policy",
            yoy_window="3Q25 to 2Q26",
            laps_from="3Q26",
            ledger_ids="D001 D004 D008",
            disclosed_contribution="not disclosed separately in any quarter",
            pr32_fitted_pts_on_na=2.40,
            pts_on_total_nights=round(2.40 * na_share, 2),
            evidence="PR #32 fits it on 3Q25, the only quarter where RNPL is live alone in NA. Four observations, WS10 NA estimates, not disclosure.",
        ),
        dict(
            feature="Updated cancellation policies",
            live_from="October 2025",
            geography="global",
            yoy_window="4Q25 to 3Q26",
            laps_from="4Q26",
            ledger_ids="D012 D060",
            disclosed_contribution="inside the bundle only",
            pr32_fitted_pts_on_na="",
            pts_on_total_nights="",
            evidence="The 4Q25 letter dates the announcement to October 2025, which closes PR #32's caveat 2 that the cancellation-redesign date is unknown. Global, not NA.",
        ),
        dict(
            feature="Single service fee, tranche 1",
            live_from="October 2025 PMS hosts, December 2025 most remaining single-fee hosts",
            geography="global",
            yoy_window="4Q25 to 3Q26",
            laps_from="4Q26",
            ledger_ids="D013 D024",
            disclosed_contribution="inside the bundle only",
            pr32_fitted_pts_on_na="",
            pts_on_total_nights="",
            evidence="Two dated tranches inside 4Q25, not one. Global, not NA.",
        ),
        dict(
            feature="Cancellation redesign plus single fee, combined",
            live_from="October to December 2025",
            geography="global",
            yoy_window="4Q25 to 3Q26",
            laps_from="4Q26",
            ledger_ids="D012 D013 D024 D060",
            disclosed_contribution="inside the bundle only",
            pr32_fitted_pts_on_na=2.29,
            pts_on_total_nights=round(2.29 * na_share, 2),
            evidence="PR #32 fits these two jointly off the 1Q26 step up and applies them to NA only, although both are global in the letters.",
        ),
        dict(
            feature="RNPL, rest of world",
            live_from="17 February 2026 worldwide, UK 18 Feb, AU 23 Feb, Canada 4 March",
            geography="global excluding BRL, INR and TRY payers",
            yoy_window="1Q26 to 4Q26, partial in 1Q26",
            laps_from="1Q27, partially; 2Q27 fully",
            ledger_ids="D025 D026 D027 D028 D029 D034",
            disclosed_contribution="inside the bundle only",
            pr32_fitted_pts_on_na="n/a, ex-NA",
            pts_on_total_nights=1.75,
            evidence="PR #32's ex-NA lap switch is worth 1.75 points of total nights and it turns on flat from 1Q27. The ledger dates the ex-NA go-live to 17 Feb to 4 March 2026, so roughly the last five to six weeks of a thirteen-week quarter. The 1Q27 lap is therefore a partial-quarter lap and is smaller than 1.75; 2Q27 onward is the full one.",
        ),
        dict(
            feature="Single service fee, tranche 2",
            live_from="announced July 2026, migration to complete during 2026",
            geography="global",
            yoy_window="from the migration date",
            laps_from="not before 3Q27",
            ledger_ids="D047",
            disclosed_contribution="not disclosed",
            pr32_fitted_pts_on_na=0.0,
            pts_on_total_nights=0.0,
            evidence="Roughly half of active listings were on the single fee at 2Q26 against over a quarter at 1Q26, guided to the whole base by year-end. PR #32 models the nights effect at zero on its own fee-elasticity work. The ramp offsets part of the tranche-1 lap inside 4Q26.",
        ),
        dict(
            feature="RNPL, expanded booking types",
            live_from="July 2026",
            geography="not specified",
            yoy_window="3Q26 onward",
            laps_from="3Q27",
            ledger_ids="D044",
            disclosed_contribution="not disclosed",
            pr32_fitted_pts_on_na="not modelled",
            pts_on_total_nights="unknown",
            evidence="Fresh treatment landing inside 3Q26, in the same quarter as the US anniversary. Call mirror only, booking types unnamed, size undisclosed. This is the single largest unquantified offset to the 3Q26 lap.",
        ),
    ]
    return rows


def bundle_crosscheck() -> list[dict]:
    """Out-of-sample test of PR #32's fitted parameters against the 4Q25 disclosure.

    PR #32 fits two NA parameters and then infers the ex-NA bundle from management's
    global ~3 points in 1Q26. The 4Q25 disclosure of over 200bp nights and roughly 300bp
    GBV (ledger D014) is a second global observation that PR #32 does not use, so it is a
    genuine check.
    """
    na_share = 0.288
    rnpl_na = 2.40
    rest_na = 2.29
    exna_bundle_total_pts = 1.75  # PR #32's ex-NA lap switch, points of total nights
    exna_on_exna = exna_bundle_total_pts / (1 - na_share)

    rows = []
    # 1Q26, the fitted quarter. Everything live.
    na_1q26 = (rnpl_na + rest_na) * na_share
    rows.append(dict(
        quarter="1Q26",
        disclosed_bundle_nights_pts="~3.0",
        ledger_id="D032",
        pr32_na_pts=round(na_1q26, 2),
        pr32_exna_pts=round(exna_bundle_total_pts, 2),
        pr32_total_pts=round(na_1q26 + exna_bundle_total_pts, 2),
        status="fitted, so agreement is by construction",
        note="PR #32 allocates 1.35 of management's ~3.0 global points to NA (28.8% of nights) and backs out 1.65 to 1.75 for ex-NA. Internally consistent.",
    ))
    # 4Q25. RNPL is US only, the cancellation redesign and fee tranche 1 are global but
    # only partly into their windows, and ex-NA RNPL is zero.
    na_4q25 = (rnpl_na + rest_na) * na_share
    for exna_fee_cancel_share in (0.4, 0.5, 0.7, 1.0):
        exna_4q25 = exna_bundle_total_pts * exna_fee_cancel_share
        rows.append(dict(
            quarter="4Q25",
            disclosed_bundle_nights_pts=">2.0",
            ledger_id="D014",
            pr32_na_pts=round(na_4q25, 2),
            pr32_exna_pts=round(exna_4q25, 2),
            pr32_total_pts=round(na_4q25 + exna_4q25, 2),
            status="out of sample",
            note=f"Assumes the fee and cancellation legs are {exna_fee_cancel_share:.0%} of the ex-NA bundle, with ex-NA RNPL at zero in 4Q25 because it went live 17 Feb 2026. A total at or above 2.0 is consistent with management's 'over 200 basis points'.",
        ))
    return rows


def exna_4q26_gap() -> list[dict]:
    """The 4Q26 gap the ledger opens in PR #32, sized and labelled.

    The cancellation redesign and fee tranche 1 are global in the letters (October to
    December 2025), so their y/y window closes everywhere from 4Q26. PR #32 laps them in
    NA only and leaves ex-NA at WS10, which carries no lap at all. The missing piece is
    the ex-NA fee and cancellation legs lapping in 4Q26.
    """
    na_share = 0.288
    exna_bundle_total_pts = 1.75
    rows = []
    for exna_fee_cancel_share in (0.4, 0.5, 0.7, 1.0):
        missing = exna_bundle_total_pts * exna_fee_cancel_share
        rows.append(dict(
            scenario=f"ex-NA fee and cancellation legs are {exna_fee_cancel_share:.0%} of the ex-NA bundle",
            basis="sourced dates, split pinned by the 4Q25 disclosure",
            pts_missing_from_4q26=round(missing, 2),
            team_baseline_4q26_pct=BASELINE_GROWTH["4Q26"],
            adjusted_4q26_pct=round(BASELINE_GROWTH["4Q26"] - missing, 2),
            adjusted_4q26_nights_mm=round(
                DISCLOSED["4Q25"] * (1 + (BASELINE_GROWTH["4Q26"] - missing) / 100), 1),
            consistent_with_4q25_disclosure=(
                "yes" if exna_fee_cancel_share <= 0.5 else
                "no, implies a 4Q25 bundle of 2.6 to 3.1 points against management's 'over 200 basis points'"),
            note="Not a model change. It is the arithmetic consequence of dating the cancellation redesign and fee tranche 1 to October to December 2025 globally, as the 3Q25 and 4Q25 letters do, rather than to North America only. The split is not free: in 4Q25 ex-NA RNPL was zero, so the 4Q25 ex-NA bundle is the fee and cancellation legs alone, and management's 'over 200 basis points' caps the split at roughly 40 to 50 percent. The same parameter therefore sizes both the cross-check and this gap.",
        ))
    return rows


def prereg_thresholds() -> list[dict]:
    """Pre-registered 5 November scoring rules for the RNPL cancellation-drag hypothesis."""
    return [
        dict(
            metric="3Q26 reported Nights and Seats Booked growth, y/y",
            baseline="team 9.9% (146.8mm); guide low double digits; 3Q25 denominator 133.6mm",
            supports_hypothesis="at or below 8.5% (at or below 144.9mm), which is 1.4 points or more below baseline and needs about 1.9mm net lost nights",
            weakens_hypothesis="at or above 10.3% (at or above 147.3mm), matching or beating 2Q26's 10.34% with the US RNPL anniversary inside the quarter",
            inconclusive="8.6% to 10.2%",
            why="One growth point is 1.336mm nights on the fixed 3Q25 denominator. A reading inside the baseline band is consistent with either a small drag offset by the July eligibility expansion, or no drag at all, and cannot separate them.",
            identifies="magnitude only, not the mechanism",
        ),
        dict(
            metric="3Q26 GBV growth minus nights growth, points",
            baseline="2Q26 gap 5.4 pts (GBV +15.74%, nights +10.34%); 1Q26 gap 10.0 pts; 3Q25 gap 5.1 pts",
            supports_hypothesis="gap widens to above 7 points while nights growth is at or below 9%, that is ADR and mix carrying the GBV line while nights stall",
            weakens_hypothesis="gap narrows to below 4.5 points with nights growth at or above 10%",
            inconclusive="4.5 to 7 points",
            why="RNPL raises ADR through the mix shift to larger homes (D016, D033, D045). If RNPL cancellations are removing nights, the nights line should deteriorate faster than the GBV line, because the cancelled nights were higher-ADR than average and their removal pulls GBV down too but proportionally less once FX is stripped out. The guide already says mid-teens GBV on low double-digit nights, a gap of about 4 to 5 points, so the gap is the cleaner signal than either line alone.",
            identifies="a mix and cancellation composite, confounded by FX, which was a 3-point revenue tailwind in the 3Q26 guide",
        ),
        dict(
            metric="3Q26 quarter-end unearned fees, y/y",
            baseline="3Q25 $1,820mm. Recent path: 3Q25 +9.8%, 4Q25 +7.9%, 1Q26 +0.4%, 2Q26 -0.9%",
            supports_hypothesis="at or below -3% y/y (below about $1,765mm). Management said RNPL produces HIGHER unearned fees in Q3 (D038), so a further deterioration means either RNPL bookings are not converting to payments, or the live unpaid base is smaller than the GBV share implies",
            weakens_hypothesis="at or above +6% y/y (about $1,930mm or more), which would show the deferred 1H26 fees arriving on schedule as payment deadlines hit, exactly as management predicted",
            inconclusive="-3% to +6%",
            why="This is the only dated, official, directional forward prediction in the whole ledger, and it is specifically about 3Q26. The FY2025 10-K baseline seasonality says unearned fees normally FALL sequentially in Q3 as check-ins peak (D055), so the test must be y/y, not sequential. An RNPL booking creates no unearned fee at all until the guest pays (D058), so the line is a direct read on how much of the booked base is still unpaid and therefore still at risk of a payment-deadline cancellation.",
            identifies="payment timing, not cancellation. A weak print is consistent with deferral, with cancellation, or with a smaller live RNPL base, and cannot separate them without the unbilled-bookings balance that the 10-K says Airbnb hedges but never discloses (D056)",
        ),
        dict(
            metric="Jessie's backlog conversion, revenue over revenue plus closing unearned fees, 3Q26",
            baseline="3Q 2022 to 2025 constant at 69.2% to 70.3%; 2026 ran 4.0 points high in both 1Q and 2Q",
            supports_hypothesis="3Q26 at or above 74%, that is the 2026 wedge persisting or widening in the quarter management said it would reverse",
            weakens_hypothesis="3Q26 at 70% to 71%, back on the pre-RNPL seasonal constant",
            inconclusive="71% to 74%",
            why="Independent construction of the same payment-timing question from the level side rather than the growth side. Source: origin/jessie/backlog-conversion.",
            identifies="payment timing only",
        ),
        dict(
            metric="4Q26 nights guide issued 5 November",
            baseline="team 8.9% (132.7mm). PR #32 sits about 1 point below the WS10 build",
            supports_hypothesis="guide implies 7.5% or below. That is consistent with both the global fee and cancellation lap that PR #32 omits ex-NA, worth 0.9 to 1.8 points, and with a cancellation tail from 1H26 cohorts",
            weakens_hypothesis="guide implies 9.5% or above, which needs the tranche-2 fee ramp and the July RNPL expansion to more than cover the whole 2025 bundle lap",
            inconclusive="7.6% to 9.4%",
            why="4Q26 is the quarter where every 2025 feature has lapped, so it is the cleanest read on underlying demand on the calendar. It is also the quarter the ledger says PR #32 is most likely to be too generous, because the cancellation redesign and fee tranche 1 were global from October 2025 and PR #32 laps them in North America only.",
            identifies="the combined lap, not RNPL cancellations specifically. A guide cut cannot be attributed to cancellations without management saying so",
        ),
        dict(
            metric="An RNPL GBV share disclosed for 3Q26",
            baseline="1Q26 roughly 20% (official), 2Q26 over 20% (call mirror only)",
            supports_hypothesis="share flat or down versus 2Q26 while the nights line decelerates, that is adoption plateauing while the installed cancellation base keeps growing",
            weakens_hypothesis="share at or above 25% with nights growth at or above 10%",
            inconclusive="21% to 24%",
            why="The asymmetry at the centre of the hypothesis is that the gross booking uplift scales with the FLOW of new RNPL bookings in the quarter while cancellations scale with the STOCK of live RNPL bookings reaching their payment deadline. A flattening share with a still-growing stock is the configuration in which the net turns negative.",
            identifies="nothing on its own. It is the variable that reconciles the funds-held read with the guide, per the EU and backlog note",
        ),
        dict(
            metric="Whether management repeats a quantified bundle contribution",
            baseline="4Q25 over 200bp nights and roughly 300bp GBV; 1Q26 approximately 3 points nights and 4 points GBV; 2Q26 none given",
            supports_hypothesis="no figure given, or a figure at or below 1.5 points, which would be the anniversary arriving",
            weakens_hypothesis="a figure at or above 2.5 points for 3Q26, meaning the bundle is still adding despite the US lap",
            inconclusive="a qualitative update only, which is what 2Q26 gave",
            why="Management quantified the bundle twice and then stopped. Whether the figure returns, and at what level, is the most direct available read on whether the lap is biting.",
            identifies="management's own attribution, which is not an independent measurement",
        ),
    ]


def parameter_register() -> list[dict]:
    return [
        dict(parameter="reported nights, 1Q24 to 2Q26", value="disclosed quarterly series",
             label="sourced", source="main tree data/processed/overnight/02_kpi_panel_quarterly.csv, reconciling to the Airbnb quarterly summaries"),
        dict(parameter="3Q26 and 4Q26 baseline reported nights", value="146.8mm and 132.7mm, +9.89% and +8.90%",
             label="sourced", source="research/notes/2026-09-10_nights-baseline-reconciliation.md, team reconciled baseline"),
        dict(parameter="RNPL GBV share, 1Q26", value="roughly 20%",
             label="sourced", source="ledger D031, official 1Q26 shareholder letter"),
        dict(parameter="RNPL GBV share, 2Q26", value="over 20%, used at 21%",
             label="sourced lower bound", source="ledger D043, 2Q26 call via stockanalysis.com mirror; the official letter carries no share"),
        dict(parameter="RNPL GBV share, 3Q25 and 4Q25", value="4% and 9% central, 2.5 to 6 and 7 to 12 range",
             label="assumed", source="no quarterly 2025 share has ever been disclosed. The 4Q25 'over 70% adoption by eligible bookings' figure is a share of eligible bookings on a GBV basis and cannot be used here"),
        dict(parameter="RNPL GBV share, 3Q26 and 4Q26", value="22% and 23% central, 21/21 flat to 25/27 high",
             label="assumed", source="direction supported by the July 2026 eligibility expansion, ledger D044, and continued expansion language in the 2Q26 letter"),
        dict(parameter="RNPL to non-RNPL ADR ratio", value="1.00, 1.15, 1.25",
             label="direction sourced, magnitude assumed", source="ledger D016, D033, D045: mix shift to larger entire homes, especially four or more bedrooms, and a contribution to the ADR increase. The ratio itself is undisclosed"),
        dict(parameter="GBV share to nights share conversion", value="p = s / (r(1-s) + s)",
             label="derived", source="research/notes/2026-09-10_rnpl-conversion-framework.md section 3"),
        dict(parameter="baseline lifetime cancellation rate", value="16% of booked nights",
             label="sourced with an unstated unit of account", source="ledger D018: 'an average of maybe 16% cancellation rate historically'. Not stated to be per night, per booking or per dollar, and no base period given"),
        dict(parameter="incremental RNPL cancellation propensity", value="0, +1, +2, +4 points, plus management-implied",
             label="scenario grid", source="the four fixed values are the task's grid. Management-implied is 1.0 divided by the RNPL nights share, from the 16 to 17 platform remark, ledger D017 and D018"),
        dict(parameter="mean booking-to-check-in lead time", value="2.2 months central, 1.8 to 3.0 range",
             label="derived from disclosure", source="Little's Law on the unearned-fee pool. Opening unearned fees over quarterly revenue is 0.66x to 0.88x for 2025, so mean residence of a booked-but-unstayed fee is 2.0 to 2.6 months. Table from origin/jessie/backlog-conversion via research/notes/2026-09-05_eu-platform-and-backlog.md section 3b"),
        dict(parameter="lead-time distribution shape", value="shifted geometric in whole months",
             label="assumed", source="Airbnb has never published a lead-time distribution. Only the mean is anchored"),
        dict(parameter="RNPL lead-time uplift", value="0%, 7%, 15%",
             label="direction sourced, magnitude assumed", source="lengthening disclosed in every print from 3Q25, ledger D010, D016, D039, D045. The only quantified y/y lead-time move on record is minus 7% in April 2025, pre-RNPL, ledger D011"),
        dict(parameter="excess cancellations recognised in the stay month", value="85%, remainder in the prior month",
             label="window sourced, split assumed", source="RNPL payment falls due shortly before the end of the free cancellation period, ledger D002, and that window is 24 hours to 14 days before check-in, ledger D012"),
        dict(parameter="baseline cancellations recognised in the booking month", value="25%",
             label="mechanism sourced, magnitude assumed", source="the 24-hour full-refund grace period for bookings made more than 7 days ahead, ledger D012. Held constant across runs and years, so close to y/y neutral"),
        dict(parameter="same-quarter net rebooking offset", value="0%, 25%, 50%",
             label="mechanism sourced, magnitude assumed", source="ledger D002 and D046. The calendar pilot's 32 to 44% reclosure of reopened short-run dates is a descriptive lead, not a measured rebooking rate"),
        dict(parameter="within-quarter monthly split of bookings", value="equal thirds",
             label="assumed", source="only quarterly aggregates are reported on, so the split affects only cross-quarter spill at the margin"),
        dict(parameter="North America share of total nights", value="28.8%",
             label="sourced", source="main tree data/processed/overnight/02_kpi_panel_quarterly.csv, na_share_of_nights_pct"),
        dict(parameter="PR #32 fitted product terms", value="RNPL +2.40 pts NA, fee and cancellation redesign +2.29 pts NA, ex-NA lap switch 1.75 pts of total nights",
             label="sourced from a team model, not from disclosure", source="origin/krish/nights-quarterly, research/notes/nights_quarterly.md and data/processed/nights_quarterly_na.csv and nights_quarterly_total.csv. Two free parameters fitted on four WS10 NA estimates"),
    ]


# ======================================================================================
# Write
# ======================================================================================

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    # Self-checks on the engine before anything is written.
    weights = lead_time_weights(2.2)
    assert math.isclose(sum(weights), 1.0, abs_tol=1e-9)
    mean = sum(k * w for k, w in enumerate(weights))
    assert 1.9 < mean < 2.3, f"truncated geometric mean drifted to {mean:.3f}"
    gross = solve_reference_gross(weights)
    ref = run_scenario(gross, {}, 0.0, weights, weights, 0.0)
    for quarter in ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26"]:
        assert math.isclose(ref[quarter], TARGETS[quarter], rel_tol=2e-3), (
            f"reference run failed to reproduce {quarter}: {ref[quarter]:.2f} "
            f"against {TARGETS[quarter]:.2f}")
    # A zero-delta scenario must be identical to the reference.
    zero = run_scenario(gross, nights_share_path(GBV_SHARE_PATHS["share_central"], 1.25),
                        0.0, weights, weights, 0.0)
    assert all(math.isclose(zero[q], ref[q], rel_tol=1e-12) for q in QUARTERS)

    grid = build_grid()
    write_csv(OUT / "D1_rnpl_cohort_scenarios.csv", grid)

    # The two cohort matrices, at the central cell.
    central_shares = nights_share_path(GBV_SHARE_PATHS["share_central"], 1.25)
    central_delta = 1.0 / central_shares["1Q26"]
    cancel_rows, stay_rows = cohort_matrices(
        gross, central_shares, central_delta,
        lead_time_weights(2.2), lead_time_weights(2.2 * 1.07),
    )
    write_csv(OUT / "D1_cohort_matrix_cancellation.csv", cancel_rows)
    write_csv(OUT / "D1_cohort_matrix_stay.csv", stay_rows)
    write_csv(OUT / "D1_rnpl_parameters.csv", parameter_register())
    write_csv(OUT / "D1_lap_anniversary.csv", lap_table())
    write_csv(OUT / "D1_bundle_crosscheck.csv", bundle_crosscheck())
    write_csv(OUT / "D1_exna_4q26_gap.csv", exna_4q26_gap())
    write_csv(OUT / "D1_prereg_thresholds.csv", prereg_thresholds())

    # Console summary: the central cell and the range.
    central = [r for r in grid if r["share_path"] == "share_central"
               and r["adr_ratio"] == "adr_plus25" and r["lead_time"] == "lead_2.2"
               and r["lead_uplift"] == "uplift_7" and r["rebook_offset"] == 0.25]
    print(f"Wrote {len(grid)} scenario cells to {OUT.relative_to(WORKTREE)}")
    print(f"Reference run reproduces every disclosed quarter within 0.2%.")
    print("\nCentral cell (central share path, ADR +25%, 2.2-month lead, +7% uplift, 25% rebooking):")
    print(f"{'delta':>14} {'3Q26 pts':>9} {'3Q26 mm':>9} {'4Q26 pts':>9} {'4Q26 mm':>9}")
    for row in central:
        print(f"{row['delta_scenario']:>14} "
              f"{row['3Q26_growth_delta_pts']:>9.2f} {row['3Q26_nights_delta_mm']:>9.2f} "
              f"{row['4Q26_growth_delta_pts']:>9.2f} {row['4Q26_nights_delta_mm']:>9.2f}")
    for quarter in ("3Q26", "4Q26"):
        values = [r[f"{quarter}_growth_delta_pts"] for r in grid]
        print(f"\n{quarter} growth delta across all {len(grid)} cells: "
              f"{min(values):+.2f} to {max(values):+.2f} points")
        nonzero = [r[f"{quarter}_growth_delta_pts"] for r in grid
                   if r["delta_scenario"] != "delta_0pp"]
        print(f"{quarter} excluding the zero-delta cells: "
              f"{min(nonzero):+.2f} to {max(nonzero):+.2f} points")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
