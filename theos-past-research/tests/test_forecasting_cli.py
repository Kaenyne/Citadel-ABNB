from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_forecast_rehearsal.py"
FIXTURE = ROOT / "tests/fixtures/forecast_rehearsal.json"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_forecast_then_audit_round_trip(tmp_path: Path) -> None:
    packet_dir = tmp_path / "packet"

    forecast = run(
        "forecast", "--input", str(FIXTURE), "--output", str(packet_dir)
    )

    assert forecast.returncode == 0, forecast.stderr
    assert "ABNB-MVP-REHEARSAL-v1" in forecast.stdout
    assert "workflow_rehearsal_not_backtest" in forecast.stdout
    assert "ADR-MVP-001" in (packet_dir / "review_memo.md").read_text(
        encoding="utf-8"
    )

    audit = run("audit", "--packet-dir", str(packet_dir))
    assert audit.returncode == 0, audit.stderr
    assert "audit passed" in audit.stdout.casefold()


def test_forecast_refuses_to_overwrite_existing_packet(tmp_path: Path) -> None:
    packet_dir = tmp_path / "packet"

    assert (
        run("forecast", "--input", str(FIXTURE), "--output", str(packet_dir)).returncode
        == 0
    )
    second = run(
        "forecast", "--input", str(FIXTURE), "--output", str(packet_dir)
    )

    assert second.returncode == 1
    assert "already exists" in second.stderr
