"""Point-in-time timestamp parsing and evidence eligibility."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone


def parse_utc(value: str, field_name: str) -> datetime:
    """Parse an offset-aware ISO 8601 timestamp and normalize it to UTC."""
    if not value.strip():
        raise ValueError(f"{field_name} timestamp is missing")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field_name} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class EligibilityAudit:
    """Eligible and rejected features for one immutable cutoff."""

    eligible: tuple[dict[str, object], ...]
    rejected: tuple[dict[str, object], ...]


def _rejection_reason(
    row: Mapping[str, object],
    manifests: Mapping[str, Mapping[str, object]],
    cutoff: datetime,
) -> str | None:
    if str(row.get("availability_status", "")).casefold() != "verified":
        return "availability_not_verified"

    manifest = manifests.get(str(row.get("manifest_id", "")))
    if manifest is None or str(manifest.get("review_status", "")).casefold() != (
        "approved_for_forecasting"
    ):
        return "manifest_not_approved_for_forecasting"

    if str(row.get("review_status", "")).casefold() != "approved":
        return "feature_not_approved"

    try:
        available_at = parse_utc(
            str(row.get("first_available_at_utc", "")),
            "first_available_at_utc",
        )
    except ValueError:
        return "availability_timestamp_invalid"
    if available_at >= cutoff:
        return "not_available_strictly_before_cutoff"
    return None


def audit_features(
    rows: Iterable[Mapping[str, object]],
    manifests: Mapping[str, Mapping[str, object]],
    as_of_utc: str,
) -> EligibilityAudit:
    """Partition features without dropping evidence rejected at the cutoff."""
    cutoff = parse_utc(as_of_utc, "as_of_utc")
    eligible: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    for source in rows:
        row = dict(source)
        reason = _rejection_reason(row, manifests, cutoff)
        if reason is None:
            eligible.append(row)
        else:
            row["rejection_reason"] = reason
            rejected.append(row)
    return EligibilityAudit(tuple(eligible), tuple(rejected))
