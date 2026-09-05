"""Guidance target arithmetic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DerivedTarget:
    guide_low: float
    guide_high: float
    guide_mid: float
    range_width_pct: float
    guidance_surprise_pct: float | None
    ex_ante_conservatism_pct: float | None
    realized_cushion_pct: float | None
    actual_range_position: str | None


def derive_one_target(
    guide_low: float,
    guide_high: float,
    consensus: float | None,
    actual: float | None,
) -> DerivedTarget:
    if guide_low > guide_high:
        raise ValueError("guide_low cannot exceed guide_high")
    midpoint = (guide_low + guide_high) / 2.0
    if midpoint == 0:
        raise ValueError("guidance midpoint cannot be zero")
    if consensus == 0:
        raise ValueError("consensus cannot be zero")

    surprise = None if consensus is None else (midpoint - consensus) / consensus
    conservatism = None if consensus is None else (consensus - midpoint) / consensus
    cushion = None if actual is None else (actual - midpoint) / midpoint
    if actual is None:
        range_position = None
    elif actual < guide_low:
        range_position = "below"
    elif actual > guide_high:
        range_position = "above"
    else:
        range_position = "within"

    return DerivedTarget(
        guide_low=guide_low,
        guide_high=guide_high,
        guide_mid=midpoint,
        range_width_pct=(guide_high - guide_low) / midpoint,
        guidance_surprise_pct=surprise,
        ex_ante_conservatism_pct=conservatism,
        realized_cushion_pct=cushion,
        actual_range_position=range_position,
    )
