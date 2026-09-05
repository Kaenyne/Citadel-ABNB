from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def load_agent() -> dict[str, object]:
    with (ROOT / ".codex/agents/abnb_forecasting.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_forecasting_agent_loads_with_approved_runtime() -> None:
    config = load_agent()

    assert config["name"] == "abnb_forecasting"
    assert config["model"] == "gpt-5.6-sol"
    assert config["model_reasoning_effort"] == "xhigh"
    assert config["sandbox_mode"] == "workspace-write"
    assert str(config["description"]).strip()
    assert str(config["developer_instructions"]).strip()


def test_forecasting_skill_and_operator_docs_are_installed() -> None:
    assert (ROOT / ".codex/skills/abnb-forecasting/SKILL.md").is_file()
    assert (ROOT / "docs/forecasting/agent-contract.md").is_file()
    assert (ROOT / "docs/forecasting/prompting-and-running.md").is_file()
