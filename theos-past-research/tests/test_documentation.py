from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/alt-data/agent-contract.md"
RUN_GUIDE = ROOT / "docs/alt-data/prompting-and-running.md"


def prompt_sections(markdown: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## (.+?)\n", markdown, flags=re.MULTILINE))
    return {
        match.group(1): markdown[
            match.end() : matches[index + 1].start() if index + 1 < len(matches) else None
        ]
        for index, match in enumerate(matches)
    }


def test_agent_contract_and_run_guide_exist() -> None:
    assert CONTRACT.is_file()
    assert RUN_GUIDE.is_file()


def test_run_guide_has_every_research_stage() -> None:
    sections = prompt_sections(RUN_GUIDE.read_text(encoding="utf-8"))

    assert {
        "1. Source discovery",
        "2. Transcript and guidance preparation",
        "3. Hypothesis preregistration",
        "4. Collection and provenance audit",
        "5. Single-signal guidance test",
        "6. Bloomberg ticket only",
        "7. Negative-result review",
        "8. Top-three-signal memo",
    }.issubset(sections)
    assert all("```text" in sections[name] for name in sections if name[:1].isdigit())


def test_guidance_test_prompt_preserves_point_in_time_controls() -> None:
    sections = prompt_sections(RUN_GUIDE.read_text(encoding="utf-8"))
    prompt = sections["5. Single-signal guidance test"].casefold()

    for phrase in (
        "abnb_alt_data",
        "strictly before",
        "available_at",
        "walk-forward",
        "baseline",
        "negative or inconclusive",
    ):
        assert phrase in prompt


def test_source_prompt_forbids_collection_before_approval() -> None:
    sections = prompt_sections(RUN_GUIDE.read_text(encoding="utf-8"))
    prompt = sections["1. Source discovery"].casefold()

    assert "do not collect" in prompt
    assert "wait for my approval" in prompt


def test_readiness_prompt_preserves_hierarchy_sync_gate_and_quant_handoff() -> None:
    sections = prompt_sections(RUN_GUIDE.read_text(encoding="utf-8"))
    prompt = sections["1C. Complete agent-readiness assessment"].casefold()

    for phrase in (
        "abnb research orchestrator",
        "exactly two transcript-context subagents",
        "guidance_2020q4_2023q2",
        "guidance_2023q3_2026q2",
        "pre-model historical replay",
        "stop and wait for me to sync",
        "compare the two cohort results only",
        "targets.csv",
        "features_long.csv",
        "model_matrix.csv",
        "folds.csv",
        "cutoff_audit.csv",
        "source_provenance.csv",
        "data_dictionary.csv",
        "pre_model_replay.csv",
        "model_spec.md",
        "handoff_summary.md",
        "manifest.json",
        "checksums.sha256",
    ):
        assert phrase in prompt
