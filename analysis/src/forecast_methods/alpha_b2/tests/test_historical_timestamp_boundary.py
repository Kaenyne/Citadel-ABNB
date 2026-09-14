"""Regression for the independently identified historical post-close leak."""
from pathlib import Path
import importlib.util
import sys

import pandas as pd
import pytest

MODULE = Path(__file__).resolve().parents[1] / "run.py"
spec = importlib.util.spec_from_file_location("alpha_b2_boundary", MODULE)
B = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = B
spec.loader.exec_module(B)


def row(stamp, role="pre_guide", register_id="candidate", value=4610.):
    return dict(register_id=register_id, vendor="LSEG", period="2026Q3", metric="revenue",
                value=value, role=role, pit_usable=True, vendor_attributed=True,
                as_of_timestamp=stamp)


@pytest.mark.parametrize("role", ["pre_guide", "at_print"])
@pytest.mark.parametrize("letter_day,stamp", [
    ("2026-08-06", "2026-08-06T17:00:00-04:00"),
    ("2026-08-06", "2026-08-06T16:00:00-04:00"),
    ("2026-08-06", "2026-08-06T20:00:00Z"),
    ("2026-08-06", "2026-08-06T20:00:00.000001Z"),
    ("2026-08-06", "2026-08-06T10:00:00"),
    ("2026-08-06", "2026-08-06T00:00:00"),
    ("2026-02-12", "2026-02-12T21:00:00Z"),
])
def test_historical_explicit_boundary_rejects_postclose_exactclose_and_naive(role, letter_day, stamp):
    candidates = pd.DataFrame([row(stamp, role)])
    assert B.admissible_consensus(candidates, "2026Q3", letter_day, role, exact_day=True) is None


@pytest.mark.parametrize("letter_day,stamp", [
    ("2026-08-06", "2026-08-06"),
    ("2026-08-06", "2026-08-06T15:59:59.999999-04:00"),
    ("2026-08-06", "2026-08-06T19:59:59.999999Z"),
    ("2026-02-12", "2026-02-12T20:59:59Z"),
])
def test_historical_authorized_date_only_and_strict_preclose_are_kept(letter_day, stamp):
    candidates = pd.DataFrame([row(stamp)])
    assert B.admissible_consensus(candidates, "2026Q3", letter_day, "pre_guide", exact_day=True) is not None


def test_historical_orders_explicit_offsets_by_actual_utc():
    candidates = pd.DataFrame([
        row("2026-08-06T15:00:00+01:00", register_id="earlier", value=4600.),
        row("2026-08-06T13:00:00-04:00", register_id="later", value=4610.)])
    assert B.admissible_consensus(candidates, "2026Q3", "2026-08-06", "pre_guide", exact_day=True)["register_id"] == "later"


def test_exact_day_uses_new_york_calendar_day_for_explicit_timestamp():
    candidates = pd.DataFrame([row("2026-08-06T00:30:00Z")])  # August 5 in New York.
    assert B.admissible_consensus(candidates, "2026Q3", "2026-08-06", "pre_guide", exact_day=True) is None
    assert B.admissible_consensus(candidates, "2026Q3", "2026-08-06", "pre_guide", exact_day=False) is not None


def test_transitive_kernel_inputs_are_in_manifest_inputs():
    assert B.INPUTS["kernel_kpi_panel"] == B.K.ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"
    assert B.INPUTS["kernel_cushions"] == B.K.ROOT / "data/processed/overnight/02_guidance_cushion_series.csv"
    assert B.INPUTS["kernel_kpi_panel"].is_file()
    assert B.INPUTS["kernel_cushions"].is_file()
