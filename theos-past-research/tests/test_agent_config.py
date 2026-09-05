from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
AGENT_PATH = ROOT / ".codex/agents/abnb_alt_data.toml"


def load_agent() -> dict[str, object]:
    with AGENT_PATH.open("rb") as handle:
        return tomllib.load(handle)


def test_agent_uses_approved_runtime_settings() -> None:
    config = load_agent()

    assert config["name"] == "abnb_alt_data"
    assert config["model"] == "gpt-5.6-sol"
    assert config["model_reasoning_effort"] == "high"
    assert config["sandbox_mode"] == "workspace-write"
    assert str(config["description"]).strip()


def test_agent_contract_contains_research_controls() -> None:
    instructions = str(load_agent()["developer_instructions"]).casefold()

    required_phrases = (
        "point-in-time",
        "source_registry.csv",
        "hypothesis_ledger.csv",
        "strictly before",
        "paid data",
        "bloomberg",
        "negative and inconclusive",
        "earning-transcripts",
        "no more than three full transcripts",
        "never invent",
        "do not spawn",
    )
    for phrase in required_phrases:
        assert phrase in instructions


def test_agent_contract_enforces_collection_approval_gates() -> None:
    instructions = str(load_agent()["developer_instructions"]).casefold()

    assert "airbnb-controlled" in instructions
    assert "terms prohibit automated collection" in instructions
    assert "revised" in instructions and "vintage" in instructions
    assert "ask the user before" in instructions


def test_agent_contract_enables_only_audited_autonomous_scraping() -> None:
    instructions = str(load_agent()["developer_instructions"]).casefold()

    for phrase in (
        "scrapling",
        "assess_scrape_candidate",
        "scraping_audit.csv",
        "free_api_registry.csv",
        ".env.example",
        "10 requests per minute",
        "personal data",
        "explicit automation permission",
    ):
        assert phrase in instructions


def test_agent_contract_defines_transcript_cohorts_and_quant_handoff() -> None:
    instructions = str(load_agent()["developer_instructions"]).casefold()

    for phrase in (
        "abnb research orchestrator",
        "exactly two transcript-context subagents",
        "guidance_2020q4_2023q2",
        "guidance_2023q3_2026q2",
        "pre-model historical replay",
        "compare cohort results only when",
        "targets.csv",
        "features_long.csv",
        "model_matrix.csv",
        "folds.csv",
        "cutoff_audit.csv",
        "data_dictionary.csv",
        "model_spec.md",
        "handoff_summary.md",
    ):
        assert phrase in instructions
