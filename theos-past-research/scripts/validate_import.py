"""Audit tracked and untracked package files against the import boundary."""

import subprocess
import sys
from pathlib import Path


TEAM_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from abnb_alt_data.import_policy import collect_violations  # noqa: E402


def candidate_paths() -> list[Path]:
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            "theos-past-research",
        ],
        cwd=TEAM_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [TEAM_ROOT / line for line in result.stdout.splitlines()]


def main() -> int:
    violations = collect_violations(TEAM_ROOT, candidate_paths())
    if violations:
        print("\n".join(violations))
        return 1
    print("Theo past research import policy passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
