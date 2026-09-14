"""L0 constraint spine — entry point. Rebuilds all three files and runs the test suite.

    python analysis/src/forecast_methods/L0/run.py

Writes progressively: file 1 is on disk and asserted before file 2 starts, so a crash in a
later stage still leaves the earlier stages' outputs and their diagnostics.
Exit code 0 means every assertion and every test passed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _paths import OUT, rel  # noqa: E402

DIAG = OUT / "L0_build_diagnostics.json"


def _save(diag: dict) -> None:
    DIAG.write_text(json.dumps(diag, indent=2, default=str))


def main() -> int:
    diag: dict = {"package": "L0-spine", "built_at_local_date": "2026-09-11"}

    import build_exact_regional_revenue as b1
    _, d1 = b1.build()
    diag["file1_exact_regional_revenue"] = d1
    _save(diag)

    import build_interval_observations as b2
    _, d2 = b2.build()
    diag["file2_interval_observations"] = d2
    _save(diag)

    import build_vintage_register as b3
    _, d3 = b3.build()
    diag["file3_vintage_register"] = d3
    _save(diag)

    # loader smoke test
    import l0
    diag["loader_smoke"] = {
        "exact_rows": len(l0.load_exact_regional_revenue()),
        "interval_rows_default": len(l0.load_interval_observations()),
        "interval_rows_with_derived": len(l0.load_interval_observations(include_derived=True)),
        "vintage_rows": len(l0.load_vintage_register()),
        "pre_guide_3Q26": l0.pre_guide_street("2026Q3"),
        "pit_consensus_revenue_2026Q4_as_of_2026_09_12":
            l0.pit_consensus("revenue", "2026Q4", "2026-09-12"),
    }
    _save(diag)
    print(f"[L0] loader smoke: {diag['loader_smoke']['exact_rows']} exact cells, "
          f"{diag['loader_smoke']['interval_rows_default']} interval rows (default view), "
          f"{diag['loader_smoke']['vintage_rows']} consensus values")

    test_file = Path(__file__).resolve().parent / "test_l0.py"
    try:
        import pytest  # noqa: F401
        rc = subprocess.call([sys.executable, "-m", "pytest", str(test_file), "-q"])
    except ModuleNotFoundError:
        # pytest is not in this interpreter: run the same test functions directly so the
        # package still self-verifies and still returns a meaningful exit code.
        print("[L0] pytest not installed; running test functions directly")
        import importlib
        mod = importlib.import_module("test_l0")
        names = [n for n in dir(mod) if n.startswith("test_")]
        failed = []
        for n in names:
            try:
                getattr(mod, n)()
            except Exception as exc:  # noqa: BLE001
                failed.append((n, repr(exc)))
        for n, e in failed:
            print(f"[L0] FAIL {n}: {e}")
        print(f"[L0] {len(names) - len(failed)}/{len(names)} tests passed (no-pytest fallback)")
        rc = 1 if failed else 0
    diag["pytest_exit_code"] = rc
    _save(diag)
    print(f"[L0] diagnostics -> {rel(DIAG)}")
    if rc != 0:
        print("[L0] FAILED: pytest returned non-zero")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
