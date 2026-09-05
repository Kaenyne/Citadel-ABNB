"""Outcome-blind tone coding and adjudication."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ToneCodingInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    excerpt_ids: list[str] = Field(min_length=1)
    proposed_score: int = Field(ge=-2, le=2)
    demand_direction: int = Field(ge=-2, le=2)
    uncertainty_emphasis: int = Field(ge=0, le=2)
    commitment_strength: int = Field(ge=-1, le=1)
    rationale: str = Field(min_length=3)


class ToneCoding(BaseModel):
    model_config = ConfigDict(frozen=True)

    excerpt_ids: tuple[str, ...]
    score: int = Field(ge=-2, le=2)
    demand_direction: int = Field(ge=-2, le=2)
    uncertainty_emphasis: int = Field(ge=0, le=2)
    commitment_strength: int = Field(ge=-1, le=1)
    rationale: str


class ToneAdjudication(BaseModel):
    model_config = ConfigDict(frozen=True)

    first_score: int
    second_score: int
    requires_review: bool
    final_score: int | None
    adjudication_reason: str | None = None


def code_tone(coding_input: ToneCodingInput) -> ToneCoding:
    return ToneCoding(
        excerpt_ids=tuple(coding_input.excerpt_ids),
        score=coding_input.proposed_score,
        demand_direction=coding_input.demand_direction,
        uncertainty_emphasis=coding_input.uncertainty_emphasis,
        commitment_strength=coding_input.commitment_strength,
        rationale=coding_input.rationale,
    )


def adjudicate_tone(first: ToneCoding, second: ToneCoding) -> ToneAdjudication:
    agrees = first.score == second.score
    return ToneAdjudication(
        first_score=first.score,
        second_score=second.score,
        requires_review=not agrees,
        final_score=first.score if agrees else None,
        adjudication_reason="independent coding passes agree" if agrees else None,
    )
