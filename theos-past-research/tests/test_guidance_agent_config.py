from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
ROLE = ROOT / ".codex/agents/abnb_guidance_intelligence.toml"
PLAYBOOK = ROOT / "research/guidance/AGENT_PLAYBOOK.md"


def test_agent_role_is_valid_minimal_toml():
    config = tomllib.loads(ROLE.read_text(encoding="utf-8"))

    assert set(config) == {"description", "developer_instructions"}
    assert isinstance(config["description"], str) and config["description"].strip()
    assert isinstance(config["developer_instructions"], str)
    assert len(config["developer_instructions"].strip()) >= 500


def test_agent_role_points_to_existing_playbook_and_design():
    config = tomllib.loads(ROLE.read_text(encoding="utf-8"))
    instructions = config["developer_instructions"]

    assert PLAYBOOK.exists()
    assert "research/guidance/AGENT_PLAYBOOK.md" in instructions
    assert "docs/superpowers/specs/2026-09-02-abnb-guidance-intelligence-design.md" in instructions


def test_playbook_defines_user_visible_operating_modes():
    playbook = PLAYBOOK.read_text(encoding="utf-8")

    for mode in (
        "Historical build",
        "Quarter update",
        "Guidance analysis",
        "Evidence audit",
        "Model refresh",
        "Research review",
    ):
        assert mode in playbook


def test_guidance_role_uses_imported_research_path() -> None:
    instructions = tomllib.loads(ROLE.read_text(encoding="utf-8"))["developer_instructions"]

    assert "research/guidance/AGENT_PLAYBOOK.md" in instructions
    assert "research/abnb_guidance/" not in instructions
