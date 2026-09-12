"""
fee_schedule.py  --  THE fee function, THE migrated share, THE single ADR de-gross-up.

OWNERSHIP (binding, per the chief-of-staff decisions):
  This file is the ONLY place in the repository where reported ADR is de-grossed-up
  to a host-payout numeraire.  `l1-reconciliation` must NOT de-gross-up.  The ADR
  workbook "reprice" row and the driver model's `take_bps` lever are the SAME event
  as the migration modelled here; both are deleted and replaced by this schedule.

  theta is an EXPLICIT ARGUMENT of every function that can move a price.  There is no
  default theta anywhere in this file.  theta is UNIDENTIFIED for the mandatory cohort
  (see the note at docs/revenue-forecast-strategy/05_backtests/fee-takerate.md).

  The migrated share is EXOGENOUS AND DATED.  It is never fitted against GBV.

PRIMITIVES
  Split regime  (pre-migration, guest + host fee)
      listed nightly price L
      host payout        H = L * (1 - HOST_FEE_SPLIT)          = 0.970 L
      guest total / GBV  G = L * (1 + GUEST_FEE_SPLIT)         = 1.141 L
      Airbnb revenue     R = L * (HOST_FEE_SPLIT+GUEST_FEE_SPLIT) = 0.171 L
      take rate          R/G = 0.171 / 1.141 = 14.987 %

  Single regime (host-only 15.5 %)
      listed nightly price L'
      host payout        H' = L' * (1 - HOST_FEE_SINGLE)       = 0.845 L'
      guest total / GBV  G' = L'                               (no guest fee)
      Airbnb revenue     R' = L' * HOST_FEE_SINGLE             = 0.155 L'
      take rate          R'/G' = 15.500 %

  Payout-neutral reprice.  Holding H constant, L'/L = 0.97/0.845 = 1.147929,
  i.e. REPRICE_NEUTRAL = +14.79 pp of listed price.  theta is the fraction of that
  reprice the host actually applies:   L' = L * (1 + theta * REPRICE_NEUTRAL).
  theta = 1  <=>  host payout unchanged.  theta < 1  <=>  host payout FALLS.

DENOMINATOR WARNING (verified in code, not assumed)
  analysis/src/adr/12_fee_migration_reprice.py line 108 computes
      theta = mean_jump / 0.138
  i.e. it normalises the observed listed-price jump by 13.8 pp, not by the
  payout-neutral 14.79 pp.  The repo theta is therefore biased UP by the factor
  14.79/13.8 = 1.0717.  Both conventions are exposed here:
      theta_repo  (jump / 13.8)   -- what 12_reprice_summary.csv contains
      theta_payout_neutral        = theta_repo * 13.8 / 14.79
  The chief-of-staff addendum instructs the uplift table to be evaluated at
  theta_repo * REPRICE_NEUTRAL (that is what reproduces -1.56 % GBV / +1.81 %
  revenue at 0.833), so `uplift()` takes theta in REPO UNITS by default and
  `theta_units` makes the choice explicit.
"""
from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------- fee constants
GUEST_FEE_SPLIT = 0.141      # guest service fee, split regime (~14.1 %)
HOST_FEE_SPLIT = 0.03        # host service fee, split regime (3 %)
HOST_FEE_SINGLE = 0.155      # single host-only fee (15.5 %)

REPRICE_NEUTRAL = (1.0 - HOST_FEE_SPLIT) / (1.0 - HOST_FEE_SINGLE) - 1.0   # 0.1479290
REPO_THETA_DENOM = 0.138     # the denominator actually used in 12_fee_migration_reprice.py

TAKE_SPLIT = (HOST_FEE_SPLIT + GUEST_FEE_SPLIT) / (1.0 + GUEST_FEE_SPLIT)  # 0.149869
TAKE_SINGLE = HOST_FEE_SINGLE                                              # 0.155


@dataclass(frozen=True)
class FeeOutcome:
    """GBV and revenue returned JOINTLY, once, from one payout and one regime."""
    regime: str
    theta: float | None
    listed: float
    host_payout: float
    gbv: float
    revenue: float

    @property
    def take_rate(self) -> float:
        return self.revenue / self.gbv


def fee(H: float, regime: str, theta: float | None = None) -> FeeOutcome:
    """Map a host payout H to (GBV, revenue) jointly.

    regime == 'split'  : GBV = H/0.97 * 1.141, revenue = H/0.97 * 0.171, take 14.99 %
    regime == 'single' : GBV = H/0.845,        revenue = H/0.845 * 0.155, take 15.50 %

    theta is accepted (and recorded) but does NOT enter this mapping: given a payout,
    the regime fixes the split of guest-total between host and platform.  theta only
    determines how much payout survives a migration -- see `migrate_cohort`.
    """
    if regime == "split":
        listed = H / (1.0 - HOST_FEE_SPLIT)
        gbv = listed * (1.0 + GUEST_FEE_SPLIT)
        rev = listed * (HOST_FEE_SPLIT + GUEST_FEE_SPLIT)
    elif regime == "single":
        listed = H / (1.0 - HOST_FEE_SINGLE)
        gbv = listed
        rev = listed * HOST_FEE_SINGLE
    else:
        raise ValueError(f"regime must be 'split' or 'single', got {regime!r}")
    return FeeOutcome(regime=regime, theta=theta, listed=listed,
                      host_payout=H, gbv=gbv, revenue=rev)


def theta_to_payout_neutral_units(theta_repo: float) -> float:
    """Convert a 12_reprice_summary.csv theta (jump/13.8) to payout-neutral units."""
    return theta_repo * REPO_THETA_DENOM / REPRICE_NEUTRAL


def migrate_cohort(listed_pre: float, theta: float, theta_units: str = "repo") -> dict:
    """One migrated cohort: pre-migration listed price -> post-migration economics.

    theta_units == 'repo'            : L' = L * (1 + theta * REPRICE_NEUTRAL)
                                       (the addendum's convention; reproduces the
                                        -1.56 % / +1.81 % table at theta = 0.833)
    theta_units == 'payout_neutral'  : identical arithmetic, different labelling of
                                       what theta = 1 means; supplied for symmetry.
    theta_units == 'jump_pp'         : theta is the raw observed listed-price jump in
                                       pp, so L' = L * (1 + theta/100).
    """
    if theta_units == "jump_pp":
        mult = 1.0 + theta / 100.0
    elif theta_units in ("repo", "payout_neutral"):
        mult = 1.0 + theta * REPRICE_NEUTRAL
    else:
        raise ValueError(f"unknown theta_units {theta_units!r}")

    listed_post = listed_pre * mult
    pre = FeeOutcome("split", theta,
                     listed_pre,
                     listed_pre * (1 - HOST_FEE_SPLIT),
                     listed_pre * (1 + GUEST_FEE_SPLIT),
                     listed_pre * (HOST_FEE_SPLIT + GUEST_FEE_SPLIT))
    post = FeeOutcome("single", theta,
                      listed_post,
                      listed_post * (1 - HOST_FEE_SINGLE),
                      listed_post,
                      listed_post * HOST_FEE_SINGLE)
    return {
        "theta": theta, "theta_units": theta_units,
        "listed_mult": mult,
        "gbv_chg_pct": 100.0 * (post.gbv / pre.gbv - 1.0),
        "revenue_chg_pct": 100.0 * (post.revenue / pre.revenue - 1.0),
        "host_payout_chg_pct": 100.0 * (post.host_payout / pre.host_payout - 1.0),
        "take_before_pct": 100.0 * pre.take_rate,
        "take_after_pct": 100.0 * post.take_rate,
        "pre": pre, "post": post,
    }


def uplift(theta: float, theta_units: str = "repo") -> dict:
    """Migrated-cohort uplift as a pure function of theta.  No demand response."""
    d = migrate_cohort(1.0, theta, theta_units)
    d.pop("pre"); d.pop("post")
    return d


# ------------------------------------------------------- THE single de-gross-up
def host_payout_from_reported_adr(adr_reported: float,
                                  migrated_share: float,
                                  theta: float,
                                  basis: str = "gbv_consistent") -> float:
    """THE de-gross-up.  One equation, one file, theta explicit.

    basis == 'fiat'  (the literal chief-of-staff equation):
        H = ADR_reported / (1 + s * theta * 0.1479)
      This is correct if and only if reported ADR is on the LISTED-PRICE basis.

    basis == 'gbv_consistent' (DEFAULT, and what is used downstream):
        Airbnb's reported ADR is GBV / nights, i.e. the GUEST TOTAL per night.
        Migration moves guest-total per night by the cohort GBV factor
            f(theta) = (1 + theta*0.1479) / 1.141,
        not by (1 + theta*0.1479).  So, against a no-migration counterfactual,
            ADR_reported = ADR_counterfactual * [1 - s * (1 - f(theta))]
        and the host payout per night is
            H = ADR_counterfactual / 1.141 * 0.97.

    The two differ by roughly 6 % of ADR at s = 0.5, theta = 0.833.  The discrepancy
    is reported in the note as an escalation; the fiat form is retained verbatim so
    the decision can be re-ratified rather than silently overwritten.
    """
    if basis == "fiat":
        return adr_reported / (1.0 + migrated_share * theta * REPRICE_NEUTRAL)
    if basis == "gbv_consistent":
        f = (1.0 + theta * REPRICE_NEUTRAL) / (1.0 + GUEST_FEE_SPLIT)
        adr_cf = adr_reported / (1.0 - migrated_share * (1.0 - f))
        return adr_cf / (1.0 + GUEST_FEE_SPLIT) * (1.0 - HOST_FEE_SPLIT)
    raise ValueError(f"unknown basis {basis!r}")


def blended_take_rate(migrated_share: float, theta: float) -> float:
    """GBV-weighted blended fee take rate at a given migrated GBV share.

    Note the weighting subtlety: `migrated_share` is the share of *post-migration*
    GBV on the single fee, so the blend is a straight GBV weighting of 15.50 % and
    14.987 %.  theta does not change either leg's take rate; it changes how much GBV
    the migrated cohort carries, which is why the share must be a GBV share and not a
    listing share.
    """
    return migrated_share * TAKE_SINGLE + (1.0 - migrated_share) * TAKE_SPLIT


# -------------------------------------------------- exogenous dated migrated share
# Listing-weighted share of ACTIVE LISTINGS on the single fee, quarterly average
# (bookings happen through the quarter, so the average, not the end-point, is the
# booking-weighted exposure).  Sources, all in data/processed/overnight/06_fee_timeline.csv
# unless flagged:
#   2025-10  PMS-host migration begins                       (4Q25 and 1Q26 letters)
#   2026-03  "over a quarter of active listings"              (1Q26 letter)  -> 27 % end-1Q26
#   2026-06  "about half of active listings"                  (2Q26 letter)  -> 50 % end-2Q26
#   2026-07  "most remaining hosts ... complete during 2026"  (2Q26 letter)
#   15-Sep-2026 ex-EEA deadline, 13-Oct-2026 EEA+CH deadline  -- NOT IN THE TIMELINE FILE;
#            sourced from host-facing communications and carried here as an explicit
#            dated assumption.  See README.
# lo / central / hi are judgemental interpolation bands, not fitted.
LISTING_SHARE_PATH = {
    #  quarter : (lo, central, hi)   quarterly-average listing-weighted share
    "2025Q2": (0.00, 0.00, 0.00),
    "2025Q3": (0.00, 0.00, 0.00),
    "2025Q4": (0.02, 0.05, 0.09),
    "2026Q1": (0.14, 0.18, 0.22),
    "2026Q2": (0.33, 0.38, 0.43),
    "2026Q3": (0.55, 0.62, 0.70),
    "2026Q4": (0.88, 0.94, 0.98),
    "2027Q1": (0.95, 0.98, 1.00),
    "2027Q2": (0.95, 0.99, 1.00),
    "2027Q3": (0.95, 0.99, 1.00),
    "2027Q4": (0.95, 0.99, 1.00),
}

# Host-concentration multiplier m turning a listing share into a GBV share.
# PMS-connected / professional hosts migrated FIRST and carry more GBV per listing.
# Applied as an odds transform so the GBV share can never exceed 1:
#        s_gbv = m*s / (1 + (m-1)*s)
# m = 1.00 would mean no concentration.  Range is judgemental; AirDNA-style splits put
# professionally managed supply at roughly 1.3-1.8x GBV per listing versus the average.
CONCENTRATION_M = {"lo": 1.20, "central": 1.45, "hi": 1.80}


def listing_share_to_gbv_share(s_list: float, m: float) -> float:
    if s_list <= 0.0:
        return 0.0
    return m * s_list / (1.0 + (m - 1.0) * s_list)


# Recognition kernel used to carry a BOOKING-quarter share into the REVENUE quarter.
# Revenue_q = 2/3 GBV_{q-1} + 1/3 GBV_{q-2} (architect's published weight; the 0.33
# sensitivity is propagated by the caller, not hard-coded here).
KERNEL_W1 = 2.0 / 3.0
KERNEL_W2 = 1.0 / 3.0


def kernel_weighted_share(share_by_quarter: dict, quarter: str,
                          prev1: str, prev2: str,
                          w1: float = KERNEL_W1, w2: float = KERNEL_W2) -> float:
    """Migrated share applicable to REVENUE recognised in `quarter`."""
    s1 = share_by_quarter.get(prev1, 0.0)
    s2 = share_by_quarter.get(prev2, 0.0)
    return w1 * s1 + w2 * s2


# ---------------------------------------------------------------- self-test hook
def _selftest() -> None:
    assert abs(REPRICE_NEUTRAL - 0.1479290) < 1e-6, REPRICE_NEUTRAL
    assert abs(TAKE_SPLIT - 0.1498685) < 1e-6, TAKE_SPLIT
    a = fee(97.0, "split")
    assert abs(a.gbv - 114.1) < 1e-9 and abs(a.revenue - 17.1) < 1e-9
    b = fee(84.5, "single")
    assert abs(b.gbv - 100.0) < 1e-9 and abs(b.revenue - 15.5) < 1e-9
    u1 = uplift(1.0)
    assert abs(u1["revenue_chg_pct"] - 4.05) < 0.02, u1
    assert abs(u1["gbv_chg_pct"] - 0.605) < 0.01, u1
    assert abs(u1["host_payout_chg_pct"]) < 1e-9, u1
    u2 = uplift(0.8333333333)
    assert abs(u2["revenue_chg_pct"] - 1.81) < 0.02, u2
    assert abs(u2["gbv_chg_pct"] + 1.56) < 0.02, u2
    u3 = uplift(11.5, theta_units="jump_pp")
    assert abs(u3["revenue_chg_pct"] - 1.07) < 0.02, u3
    assert abs(u3["gbv_chg_pct"] + 2.28) < 0.02, u3


if __name__ == "__main__":
    _selftest()
    print("fee_schedule self-test OK")
