"""Point-in-time eligibility and transcript-derived guidance validation."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Iterable, Mapping


def parse_utc(value: str | None, field_name: str) -> datetime:
    """Parse an offset-aware ISO timestamp and normalize it to UTC."""
    if value is None or not value.strip():
        raise ValueError(f"{field_name} timestamp is missing")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field_name} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def assert_feature_available_before_cutoff(
    feature_available_at: str | None,
    guidance_available_at: str | None,
) -> None:
    """Require strict pre-cutoff availability for a historical feature."""
    feature_time = parse_utc(feature_available_at, "feature available_at")
    cutoff = parse_utc(guidance_available_at, "guidance available_at")
    if feature_time >= cutoff:
        raise ValueError(
            "feature availability must be strictly before the guidance cutoff: "
            f"feature={feature_available_at}, cutoff={guidance_available_at}"
        )


def eligible_features(
    rows: Iterable[Mapping[str, str]], cutoff: str
) -> list[Mapping[str, str]]:
    """Return verified feature rows released strictly before *cutoff*."""
    cutoff_time = parse_utc(cutoff, "cutoff")
    eligible: list[Mapping[str, str]] = []
    for row in rows:
        if row.get("availability_status", "").casefold() != "verified":
            identifier = row.get("id", row.get("source_id", "unknown"))
            raise ValueError(f"feature {identifier} has an unverified release time")
        available_at = parse_utc(row.get("available_at"), "feature available_at")
        if available_at < cutoff_time:
            eligible.append(row)
    return eligible


def _decimal(value: str, field_name: str) -> Decimal:
    if not value.strip():
        raise ValueError(f"{field_name} is missing")
    try:
        return Decimal(value.strip())
    except InvalidOperation as error:
        raise ValueError(f"{field_name} is not a valid decimal") from error


def guidance_midpoint(value_low: str, value_high: str) -> Decimal:
    """Compute an exact midpoint from an explicitly stated numeric range."""
    low = _decimal(value_low, "value_low")
    high = _decimal(value_high, "value_high")
    if low > high:
        raise ValueError("value_low cannot exceed value_high")
    return (low + high) / Decimal("2")


def _is_true(value: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no", ""}:
        return False
    raise ValueError(f"invalid boolean value {value!r}")


def validate_guidance_row(
    row: Mapping[str, str],
    transcript_index_by_markdown: Mapping[str, Mapping[str, str]],
    valid_turn_ids_by_markdown: Mapping[str, set[str]],
) -> None:
    """Validate one guidance target against verified transcript provenance."""
    source_markdown = row.get("source_markdown", "")
    transcript = transcript_index_by_markdown.get(source_markdown)
    if transcript is None:
        raise ValueError(f"guidance source Markdown is not indexed: {source_markdown}")
    if transcript.get("availability_status", "").casefold() != "verified":
        raise ValueError(f"transcript availability is unverified: {source_markdown}")

    source_turn_id = row.get("source_turn_id", "")
    if source_turn_id not in valid_turn_ids_by_markdown.get(source_markdown, set()):
        raise ValueError(f"guidance source turn is not present: {source_turn_id}")

    call_event = parse_utc(row.get("call_event_at"), "call_event_at")
    available_at = parse_utc(row.get("available_at"), "available_at")
    indexed_event = parse_utc(transcript.get("event_at"), "transcript event_at")
    if call_event != indexed_event:
        raise ValueError("guidance call_event_at does not match the transcript index")
    if available_at < call_event:
        raise ValueError("guidance available_at cannot precede call_event_at")

    guidance_type = row.get("guidance_type", "").strip().casefold()
    numeric_fields = ("value_low", "value_high", "value_midpoint")
    numeric_values = [row.get(field, "").strip() for field in numeric_fields]
    qualitative = row.get("qualitative_direction", "").strip()

    if guidance_type == "range":
        expected = guidance_midpoint(row.get("value_low", ""), row.get("value_high", ""))
        actual = _decimal(row.get("value_midpoint", ""), "value_midpoint")
        if actual != expected:
            raise ValueError(
                f"guidance midpoint {actual} does not equal range midpoint {expected}"
            )
        if qualitative:
            raise ValueError("numeric range cannot also contain qualitative direction")
    elif guidance_type == "point":
        if numeric_values[0] or numeric_values[1]:
            raise ValueError("point guidance cannot contain low or high values")
        _decimal(row.get("value_midpoint", ""), "value_midpoint")
        if qualitative:
            raise ValueError("point guidance cannot also contain qualitative direction")
    elif guidance_type == "qualitative":
        if any(numeric_values):
            raise ValueError("qualitative guidance cannot contain numeric values")
        if not qualitative:
            raise ValueError("qualitative guidance requires a direction")
    elif guidance_type == "non_comparable":
        if any(numeric_values):
            raise ValueError("non-comparable guidance cannot contain numeric values")
    else:
        raise ValueError(f"unsupported guidance_type {guidance_type!r}")

    if _is_true(row.get("indiscernible_affects_record", "")) and row.get(
        "confidence", ""
    ).casefold() == "high":
        raise ValueError("indiscernible guidance cannot have high confidence")
