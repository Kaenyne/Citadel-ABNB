from abnb_forecasting.eligibility import audit_features


CUTOFF = "2026-09-03T12:00:00Z"
APPROVED = {
    "M-1": {
        "manifest_id": "M-1",
        "review_status": "approved_for_forecasting",
    }
}


def feature(
    feature_id: str, available_at: str, **changes: object
) -> dict[str, object]:
    row: dict[str, object] = {
        "feature_id": feature_id,
        "manifest_id": "M-1",
        "availability_status": "verified",
        "review_status": "approved",
        "first_available_at_utc": available_at,
        "source_id": "S-1",
        "evidence_id": f"E-{feature_id}",
        "metric": "synthetic_macro_index",
        "value": 100.0,
    }
    row.update(changes)
    return row


def test_cutoff_is_strict_and_rejections_remain_auditable() -> None:
    audit = audit_features(
        [
            feature("before", "2026-09-03T11:59:59Z"),
            feature("equal", CUTOFF),
            feature("after", "2026-09-03T12:00:01Z"),
        ],
        APPROVED,
        CUTOFF,
    )

    assert [row["feature_id"] for row in audit.eligible] == ["before"]
    assert {row["feature_id"] for row in audit.rejected} == {"equal", "after"}
    assert {row["rejection_reason"] for row in audit.rejected} == {
        "not_available_strictly_before_cutoff"
    }


def test_unverified_and_unreviewed_features_are_rejected() -> None:
    audit = audit_features(
        [
            feature(
                "unverified",
                "2026-09-03T11:00:00Z",
                availability_status="unverified",
            ),
            feature(
                "unknown-manifest",
                "2026-09-03T11:00:00Z",
                manifest_id="M-X",
            ),
        ],
        APPROVED,
        CUTOFF,
    )

    assert [row["rejection_reason"] for row in audit.rejected] == [
        "availability_not_verified",
        "manifest_not_approved_for_forecasting",
    ]


def test_feature_level_review_is_required() -> None:
    audit = audit_features(
        [feature("draft", "2026-09-03T11:00:00Z", review_status="draft")],
        APPROVED,
        CUTOFF,
    )

    assert audit.eligible == ()
    assert audit.rejected[0]["rejection_reason"] == "feature_not_approved"
