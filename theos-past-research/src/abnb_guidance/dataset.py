"""End-to-end assembly of the normalized research dataset."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .management_evidence import (
    build_management_evidence,
    build_other_guidance_items,
    build_transcript_evidence,
)
from .official_history import build_official_history
from .records import ConsensusSnapshot, ResearchIssue, TABLE_MODELS
from .storage import write_table
from .transcripts import TRANSCRIPT_FILENAMES, build_transcript_manifest


def _frame(records: list, table_name: str) -> pd.DataFrame:
    columns = list(TABLE_MODELS[table_name].model_fields)
    return pd.DataFrame(
        [record.model_dump(mode="json") for record in records], columns=columns
    )


def _missing_consensus(events: list, guidance: list) -> list[ConsensusSnapshot]:
    target_by_event = {
        item.guidance_event_id: item.target_period
        for item in guidance
        if item.metric_code == "revenue"
    }
    return [
        ConsensusSnapshot(
            consensus_snapshot_id=f"{event.guidance_event_id}-REVENUE-CONSENSUS-MISSING",
            guidance_event_id=event.guidance_event_id,
            target_period=target_by_event[event.guidance_event_id],
            metric_code="revenue",
            statistic_type="mean",
            value=None,
            unit="USD_millions",
            currency="USD",
            analyst_count=None,
            snapshot_at_utc=None,
            snapshot_precision="unknown",
            snapshot_age_hours=None,
            is_strictly_pre_event=False,
            point_in_time_verified=False,
            source_name="Bloomberg BEst point-in-time request pending",
            license_or_access_basis="Not collected; user approval required before Bloomberg extraction",
            source_document_id=None,
            quality_grade="D",
            value_status="missing",
            missing_reason="No verified lawful public pre-guidance consensus snapshot was available in the repository.",
        )
        for event in events
    ]


def _research_issues(created_at: datetime) -> list[ResearchIssue]:
    return [
        ResearchIssue(
            research_issue_id="ABNB-ISSUE-CONSENSUS-BLOOMBERG",
            issue_type="paid_data_required",
            severity="high",
            description="Strictly point-in-time pre-guidance revenue consensus is not available from the official issuer materials.",
            proposed_resolution="After explicit user approval, populate the provided Bloomberg XLSX request using BEst snapshots timestamped before each event.",
            status="open",
            requires_user_approval=True,
            created_at_utc=created_at,
        ),
        ResearchIssue(
            research_issue_id="ABNB-ISSUE-SEC-ACCEPTANCE-TIMES",
            issue_type="timestamp_precision",
            severity="medium",
            description="Event time currently uses the disclosed webcast start as a conservative certainly-public-by proxy.",
            proposed_resolution="Capture exact SEC 8-K acceptance timestamps and retain both release and call-start clocks.",
            status="open",
            requires_user_approval=False,
            created_at_utc=created_at,
        ),
        ResearchIssue(
            research_issue_id="ABNB-ISSUE-TRANSCRIPT-RIGHTS",
            issue_type="source_rights",
            severity="low",
            description="User-supplied FactSet transcript PDFs are local research copies and cannot be redistributed.",
            proposed_resolution="Retain metadata, hashes, and short excerpts only; reacquire through an authorized terminal when needed.",
            status="accepted_limitation",
            requires_user_approval=False,
            created_at_utc=created_at,
        ),
        ResearchIssue(
            research_issue_id="ABNB-ISSUE-Q3-2026-ACTUAL",
            issue_type="future_outcome",
            severity="low",
            guidance_event_id="ABNB-2026Q2-INITIAL",
            description="The Q3 2026 actual was not public by the research cutoff and is intentionally absent.",
            proposed_resolution="Populate only after the Q3 2026 earnings release, preserving the new public-availability timestamp.",
            status="open",
            requires_user_approval=False,
            created_at_utc=created_at,
        ),
        ResearchIssue(
            research_issue_id="ABNB-ISSUE-TONE-SECOND-CODER",
            issue_type="coding_reliability",
            severity="medium",
            description="Outcome-blind tone coding is automated and provisional until independently adjudicated.",
            proposed_resolution="Run a second blinded coding pass and adjudicate disagreements before investment use.",
            status="open",
            requires_user_approval=False,
            created_at_utc=created_at,
        ),
    ]


def build_research_dataset(
    research_root: Path,
    *,
    retrieved_at: datetime,
    transcript_directory: Path | None = None,
    transcript_filenames: dict[str, str] | None = None,
) -> dict[str, int]:
    """Build canonical CSV and Parquet tables from curated lawful sources."""
    root = Path(research_root)
    official = build_official_history(retrieved_at=retrieved_at)
    evidence = build_management_evidence(
        events=official["guidance_events"],
        official_documents=official["source_documents"],
    )
    other_guidance = build_other_guidance_items(
        events=official["guidance_events"],
        revenue_guidance=official["guidance_items"],
        driver_observations=evidence["driver_observations"],
    )

    transcript_documents = []
    transcript_evidence = {"source_excerpts": [], "evidence_claims": []}
    if transcript_directory is not None:
        transcript_documents = build_transcript_manifest(
            transcript_directory,
            transcript_filenames or TRANSCRIPT_FILENAMES,
            retrieved_at=retrieved_at,
        )
        transcript_evidence = build_transcript_evidence(
            events=official["guidance_events"],
            transcript_documents=transcript_documents,
        )

    guidance = official["guidance_items"] + other_guidance
    tables = {
        "source_documents": official["source_documents"] + transcript_documents,
        "guidance_events": official["guidance_events"],
        "source_excerpts": (
            official["source_excerpts"]
            + evidence["source_excerpts"]
            + transcript_evidence["source_excerpts"]
        ),
        "quarterly_actuals": official["quarterly_actuals"],
        "guidance_items": guidance,
        "driver_observations": evidence["driver_observations"],
        "evidence_claims": evidence["evidence_claims"] + transcript_evidence["evidence_claims"],
        "consensus_snapshots": _missing_consensus(
            official["guidance_events"], official["guidance_items"]
        ),
        "market_returns": [],
        "model_results": [],
        "research_issues": _research_issues(retrieved_at),
    }
    for table_name in TABLE_MODELS:
        write_table(table_name, _frame(tables[table_name], table_name), root)

    return {
        "event_count": len(official["guidance_events"]),
        "numeric_revenue_guidance_count": sum(
            item.metric_code == "revenue" and item.measure_type == "absolute_range"
            for item in guidance
        ),
        "transcript_count": len(transcript_documents),
        "evidence_claim_count": len(tables["evidence_claims"]),
    }
