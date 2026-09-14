"""FORMAT 1.1 -- the one rule that differs from frozen 1.0, and proof nothing else moved.

  python -m pytest analysis/src/forecast_methods/harness_v1_1/tests -q
"""
from __future__ import annotations

import datetime as dt

import pandas as pd
import pytest

from harness_v1_1 import paths as P
from harness_v1_1 import windows as W
from harness_v1_1.registry import RegistryError, validate_registry_frame, load_registry
from harness_v1_1.score import score_registry


def _row(**kw):
    base = dict(method="toy", object="obj", target="revenue_musd", quarter="2025Q2",
                vintage_date=dt.date(2025, 5, 1), horizon_q=1, point=3000.0, q50=3000.0,
                window="W1", prior_basis="PIT", n_params=2, n_train=12)
    base.update(kw)
    return base


def test_format_version_and_run_date():
    assert P.FORMAT_VERSION == "1.1"
    assert P.LIVE_VINTAGE_MIN == dt.date(2026, 8, 7)
    assert P.FROZEN_TODAY == dt.date(2026, 9, 11)
    assert P.RUN_DATE >= P.LIVE_VINTAGE_MIN
    assert P.TODAY == P.RUN_DATE


def test_run_date_env_override(monkeypatch):
    monkeypatch.setenv("CITADEL_ABNB_RUN_DATE", "2026-09-14")
    assert P._run_date() == dt.date(2026, 9, 14)
    monkeypatch.setenv("CITADEL_ABNB_RUN_DATE", "2026-08-01")
    with pytest.raises(ValueError, match="precedes the LIVE window"):
        P._run_date()


def test_outputs_go_to_v1_1_dir_and_spine_is_read_from_frozen():
    assert P.OUT_SCOREBOARD.parent.name == "harness_v1_1"
    assert P.OUT_SCOREBOARD.name == "scoreboard_v1_1.csv"
    assert P.OUT_CONFORMAL_GRID.parent.name == "harness_v1_1"
    assert P.OUT_CALENDAR.parent.name == "harness"
    assert P.OUT_TARGETS.parent.name == "harness"
    assert P.REGISTRY_DIR.name == "registry"          # shared with 1.0 on purpose


def test_live_row_accepts_the_real_run_date():
    d = pd.DataFrame([_row(quarter="2026Q4", window="LIVE", vintage_date=P.RUN_DATE, horizon_q=1)])
    out = validate_registry_frame(d)
    assert out["format_version"].iloc[0] == "1.1"
    assert out["vintage_date"].iloc[0] == P.RUN_DATE


def test_live_row_accepts_dates_between_last_guide_and_run_date():
    for v in (dt.date(2026, 8, 7), dt.date(2026, 9, 11), dt.date(2026, 9, 12)):
        if v <= P.RUN_DATE:
            validate_registry_frame(pd.DataFrame([_row(quarter="2026Q3", window="LIVE", vintage_date=v)]))


def test_live_row_rejects_dates_outside_the_window():
    with pytest.raises(RegistryError, match="vintage_date must be a guide date"):
        validate_registry_frame(pd.DataFrame([_row(quarter="2026Q3", window="LIVE",
                                                   vintage_date=dt.date(2026, 8, 1))]))
    with pytest.raises(RegistryError, match="vintage_date must be a guide date"):
        validate_registry_frame(pd.DataFrame([_row(quarter="2026Q4", window="LIVE",
                                                   vintage_date=P.RUN_DATE + dt.timedelta(days=1))]))


def test_historical_rows_still_require_a_guide_date():
    with pytest.raises(RegistryError, match="vintage_date must be a guide date"):
        validate_registry_frame(pd.DataFrame([_row(vintage_date=P.RUN_DATE)]))
    with pytest.raises(RegistryError, match="vintage_date must be a guide date"):
        validate_registry_frame(pd.DataFrame([_row(vintage_date=dt.date(2025, 5, 2))]))


def test_future_quarters_are_live_and_historical_windows_unchanged():
    assert W.window_of_target("2026Q3") == ["LIVE"]
    assert W.window_of_target("2026Q4") == ["LIVE"]
    assert W.window_of_target("2027Q1") == ["LIVE"]
    assert W.window_of_target("2026Q2") == ["W1", "W2"]
    assert W.window_of_target("2023Q1") == ["W1"]
    assert W.window_of_target("2022Q4") == []
    assert len(W.GUIDE_DATES_W1) == 14 and len(W.GUIDE_DATES_W2) == 10


def test_every_existing_registry_file_validates_under_1_1():
    files = sorted(P.REGISTRY_DIR.glob("*__*.csv"))
    assert len(files) >= 60, "expected the shared registry to be populated"
    bad = []
    for f in files:
        d = pd.read_csv(f).drop(columns=["format_version"], errors="ignore")
        try:
            validate_registry_frame(d)
        except Exception as e:      # noqa: BLE001
            bad.append((f.name, str(e)[:120]))
    assert not bad, bad


def test_historical_scores_are_identical_to_the_frozen_scoreboard():
    frozen = pd.read_csv(P.HARNESS_FROZEN_OUT / "scoreboard.csv")
    sb = score_registry(load_registry())
    key = ["method", "object", "target", "window", "prior_basis"]
    m = frozen.merge(sb, on=key, suffixes=("_10", "_11"), how="left")
    assert m["rmse_11"].notna().all(), "every frozen row must still be scored"
    assert (m["n_10"] == m["n_11"]).all()
    assert ((m["rmse_10"] - m["rmse_11"]).abs() < 1e-9).all()
    assert ((m["mae_10"] - m["mae_11"]).abs() < 1e-9).all()
