"""Dependency-free guidance baselines for small quarterly samples."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
import re
from statistics import median


_FISCAL_PERIOD = re.compile(r"^(?P<year>[0-9]{4})Q(?P<quarter>[1-4])$")


def _decimal(value: str | int | float | Decimal, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{field_name} must be numeric") from error


def _period(value: object) -> tuple[int, int]:
    match = _FISCAL_PERIOD.fullmatch(str(value))
    if match is None:
        raise ValueError(f"invalid fiscal period {value!r}; expected YYYYQ1-YYYYQ4")
    return int(match["year"]), int(match["quarter"])


def seasonal_naive(
    history: Sequence[Mapping[str, object]], target_period: str
) -> Decimal:
    """Return the latest earlier guidance midpoint for the same fiscal quarter."""
    target = _period(target_period)
    candidates: list[tuple[tuple[int, int], Decimal]] = []
    for row in history:
        period = _period(row.get("guided_period"))
        if period < target and period[1] == target[1]:
            candidates.append(
                (
                    period,
                    _decimal(row.get("guidance_midpoint", ""), "guidance_midpoint"),
                )
            )
    if not candidates:
        raise ValueError(f"no earlier same-quarter guidance for {target_period}")
    return max(candidates, key=lambda candidate: candidate[0])[1]


def policy_adjusted_baseline(
    operating_p50: str | int | float | Decimal,
    policy_offsets: Sequence[str | int | float | Decimal],
) -> Decimal:
    """Apply the median prior signed management offset to an operating anchor."""
    if not policy_offsets:
        raise ValueError("at least one historical policy offset is required")
    offsets = [_decimal(value, "policy offset") for value in policy_offsets]
    return _decimal(operating_p50, "operating_p50") + median(offsets)


def median_range_width(
    widths: Sequence[str | int | float | Decimal],
) -> Decimal:
    """Return the median non-negative historical guidance range width."""
    if not widths:
        raise ValueError("at least one historical range width is required")
    parsed = [_decimal(value, "range width") for value in widths]
    if any(value < 0 for value in parsed):
        raise ValueError("guidance range width cannot be negative")
    return median(parsed)


def _quantile(values: Sequence[Decimal], probability: Decimal) -> Decimal:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("at least one residual is required")
    position = Decimal(len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - Decimal(lower)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def residual_interval(
    p50: str | int | float | Decimal,
    residuals: Sequence[str | int | float | Decimal],
) -> tuple[Decimal, Decimal]:
    """Center empirical 10th/90th residual quantiles on a forecast median."""
    center = _decimal(p50, "p50")
    parsed = [_decimal(value, "residual") for value in residuals]
    return center + _quantile(parsed, Decimal("0.1")), center + _quantile(
        parsed, Decimal("0.9")
    )
