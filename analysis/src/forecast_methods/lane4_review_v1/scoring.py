"""Deterministic interval rules for an UNSIGNED review card; no trade actions.

All inputs are intervals in declared units. Publication uncertainty is distinct
from model uncertainty. None values remain absent; no management-word mapping is
implied by an arbitrary percentage estimate.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Interval:
    low: float
    high: float

    def __post_init__(self):
        if not all(math.isfinite(x) for x in (self.low, self.high)):
            raise ValueError("Intervals require finite values")
        if self.low > self.high:
            raise ValueError("Reversed interval")

    @classmethod
    def reported(cls, value, precision):
        if precision < 0 or not math.isfinite(precision):
            raise ValueError("precision must be finite and nonnegative")
        return cls(value - precision / 2, value + precision / 2)


def ratio(numerator, denominator, scale=1.0):
    if numerator is None or denominator is None:
        return None
    if numerator.low < 0 or denominator.low <= 0:
        raise ValueError("Ratio requires nonnegative numerator and positive denominator")
    return Interval(scale * numerator.low / denominator.high,
                    scale * numerator.high / denominator.low)


def growth(current, prior):
    r = ratio(current, prior, 100)
    return None if r is None else Interval(r.low - 100, r.high - 100)


def difference(left, right):
    if left is None or right is None:
        return None
    return Interval(left.low - right.high, left.high - right.low)


def versus(value, target):
    """Only wholly separated intervals receive a direction."""
    d = difference(value, target)
    if d is None:
        return "ABSENT"
    if d.low > 0:
        return "ABOVE"
    if d.high < 0:
        return "BELOW"
    if d.low == d.high == 0:
        return "EQUAL"
    return "OVERLAPS"


def band_membership(value, low, high):
    if value is None:
        return "ABSENT"
    if low > high:
        raise ValueError("Reversed band")
    if value.low >= low and value.high <= high:
        return "INSIDE"
    if value.high < low:
        return "BELOW"
    if value.low > high:
        return "ABOVE"
    return "AMBIGUOUS"


def lambda_alarm(revenue, base_musd, warning_pct, escalation_pct):
    if revenue is None:
        return "ABSENT"
    if not 0 < escalation_pct < warning_pct or base_musd <= 0:
        raise ValueError("Invalid lambda rule")
    lam = ratio(revenue, Interval(base_musd, base_musd), 100)
    if lam.low >= warning_pct:
        return "NO ALARM"
    if lam.high < escalation_pct:
        return "ESCALATE"
    if lam.low >= escalation_pct and lam.high < warning_pct:
        return "WARN"
    return "AMBIGUOUS"


def conditional_refutation(lambda_pct, uf_minus_gbv_growth_pp,
                           explicit_nights_phrase_status, warning_pct=17.09):
    """F's proposed conjunction; absence/inconclusive never become support.

    Phrase status is a human-reviewed exact quotation classification: at_least_low
    means explicit 'low double digit' or unambiguously stronger wording. Values
    are not mapped from a model forecast. No automatic investment conclusion.
    """
    allowed = {None, "at_least_low", "below_low", "ambiguous"}
    if explicit_nights_phrase_status not in allowed:
        raise ValueError("Exact phrase must be reviewed; unsupported word mapping")
    if lambda_pct is None or uf_minus_gbv_growth_pp is None or explicit_nights_phrase_status is None:
        return "ABSENT"
    if (lambda_pct.low >= warning_pct and uf_minus_gbv_growth_pp.low > -8
            and explicit_nights_phrase_status == "at_least_low"):
        return "PROPOSED REFUTATION CONDITION MET"
    return "INCONCLUSIVE"
