from abnb_guidance.tone import ToneCodingInput, adjudicate_tone, code_tone


def coding(score: int, rationale: str):
    return code_tone(
        ToneCodingInput(
            excerpt_ids=["EX1"],
            proposed_score=score,
            demand_direction=score,
            uncertainty_emphasis=1 if score < 0 else 0,
            commitment_strength=1 if score > 0 else 0,
            rationale=rationale,
        )
    )


def test_outcome_fields_are_not_accepted_by_tone_input():
    assert "eventual_revenue" not in ToneCodingInput.model_fields
    assert "stock_return" not in ToneCodingInput.model_fields


def test_agreeing_passes_are_adjudicated_automatically():
    result = adjudicate_tone(coding(1, "constructive demand"), coding(1, "firm outlook"))

    assert result.requires_review is False
    assert result.final_score == 1


def test_disagreement_requires_human_or_agent_adjudication_reason():
    result = adjudicate_tone(coding(-1, "uncertainty"), coding(1, "demand"))

    assert result.requires_review is True
    assert result.final_score is None


def test_score_outside_rubric_is_rejected():
    try:
        coding(3, "outside scale")
    except ValueError as exc:
        assert "less than or equal to 2" in str(exc)
    else:
        raise AssertionError("score outside -2..2 was accepted")
