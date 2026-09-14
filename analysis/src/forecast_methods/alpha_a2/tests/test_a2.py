from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run as a


def register_row(**overrides):
    row = dict(period="2024Q1", role="pre_guide", metric="revenue", value=2000.,
               as_of_timestamp="2024-02-13", pit_usable=True, vendor_attributed=True,
               vendor="LSEG", note="", register_id="PG-2024Q1-revenue")
    return pd.DataFrame([{**row, **overrides}])


def test_same_day_morning_is_admissible():
    _, reason = a.valid_consensus(register_row(), "2024Q1", "2024-02-13")
    assert reason == "available"


def test_future_timestamp_is_rejected():
    _, reason = a.valid_consensus(register_row(as_of_timestamp="2024-02-14"), "2024Q1", "2024-02-13")
    assert reason == "timestamp_after_origin"


def test_quarantine_cannot_be_overridden():
    _, reason = a.valid_consensus(register_row(pit_usable=False), "2024Q1", "2024-02-13")
    assert reason.startswith("pit_usable_false")


def test_current_is_never_historical():
    row, reason = a.valid_consensus(register_row(role="current"), "2024Q1", "2024-02-13")
    assert row is None and reason == "no_registered_row"


def test_unattributed_is_excluded():
    _, reason = a.valid_consensus(register_row(vendor_attributed=False), "2024Q1", "2024-02-13")
    assert reason == "vendor_unattributed"


def test_ambiguous_guide_interval_has_no_direction():
    assert a.sign_interval(-.01, .01) == 0
    assert a.sign_interval(.01, .02) == 1
    assert a.sign_interval(-.02, -.01) == -1
    with pytest.raises(ValueError):
        a.sign_interval(1, -1)


def test_wilson_known_boundary_and_no_cells():
    lo, hi = a.wilson(6, 6)
    assert lo == pytest.approx(.609665712, abs=1e-8)
    assert hi == pytest.approx(1.)
    assert np.isnan(a.wilson(0, 0)[0])


def test_bootstrap_deterministic_and_preserves_no_data():
    first = a.boot_mean([1, 2, 3, np.nan])
    assert first == a.boot_mean([1, 2, 3, np.nan])
    assert first[0] == 3 and first[1] == 2
    assert np.isnan(a.boot_mean([np.nan])[1])
    idx = a.block_indices(5, np.random.default_rng(1), draws=10)
    assert idx.shape == (10, 5)
    assert np.all((idx[:, 1]-idx[:, 0]) % 5 == 1)


def test_permutation_respects_imbalanced_sign_labels():
    assert a.permutation_p(np.ones(7), np.ones(7)) == 1
    assert np.isnan(a.permutation_p([], []))


def test_partial_corr_on_exact_shared_sample():
    rng = np.random.default_rng(99)
    z = rng.normal(size=100)
    x = z + rng.normal(size=100)
    y = 4*z-x+rng.normal(scale=.1,size=100)
    frame = pd.DataFrame(dict(signal_pct=x, excess_open_20d_pct=y, z=z))
    frame.loc[0, "z"] = np.nan
    n, raw, partial, status = a.partial_corr(frame, ["z"])
    assert n == 99 and status == "available" and raw > 0 and partial < -.98


def test_ridge_slope_prior_and_minimum_pairs():
    intercept, slope = a.ridge_fit(np.arange(6), 2+np.arange(6))
    assert intercept == pytest.approx(2) and slope == pytest.approx(1)
    with pytest.raises(ValueError):
        a.ridge_fit(np.arange(5), np.arange(5))


def test_kernel_adapter_uses_next_day_but_checks_last_input(monkeypatch):
    calls = []
    def fake(quarter, as_of, variant=None):
        calls.append(as_of)
        return dict(point=1, knowable_from="2024-02-13", **{q:1. for q in a.QCOLS})
    monkeypatch.setattr(a.K, "kernel_guide", fake)
    _, status = a.forecast("2024Q1", "2024-02-13", None)
    assert calls[0] == pd.Timestamp("2024-02-14") and status == "available"


def test_return_columns_are_executable_only():
    source = Path(a.__file__).read_text(encoding="utf-8")
    assert 'f"excess_open_{h}d_pct"' in source
    assert 'events.loc[d, "gap_pct"]' not in source


def test_cushion_conditional_quantiles_are_ordered_and_auditable():
    q = a.cushion_only_quantiles(100, [1.01, 1.02, 1.03])
    assert q["q50"] == pytest.approx(100)
    assert np.all(np.diff([q[name] for name in a.QCOLS]) >= 0)
    assert q["q05"] > 100*1.02/1.03 and q["q95"] < 100*1.02/1.01
    with pytest.raises(ValueError):
        a.cushion_only_quantiles(100, [0])


def live_row(register_id, stamp, vendor="Yahoo Finance (LSEG family)", **overrides):
    return dict(period="2026Q4", role="current", metric="revenue", value=3161.,
                as_of_timestamp=stamp, pit_usable=True, vendor_attributed=True,
                vendor=vendor, register_id=register_id, **overrides)


def test_live_mixed_date_and_utc_captures_use_actual_time():
    rows = pd.DataFrame([
        live_row("alpha_old", "2026-09-11", "Alpha Vantage (aggregated sell-side panel)"),
        live_row("same_day", "2026-09-13T15:20Z"),
        live_row("future_same_day", "2026-09-13T18:00:00Z"),
        live_row("future_date", "2026-09-14"),
        live_row("zacks_date", "2026-09-13", "Zacks"),
        live_row("sp_full_utc", "2026-09-13T15:10:22Z", "S&P Global Market Intelligence"),
    ])
    chosen = a.select_live_consensus(rows, "2026-09-13T17:15:00Z")
    assert set(chosen.register_id) == {"same_day", "zacks_date", "sp_full_utc"}
    before_capture = a.select_live_consensus(rows, "2026-09-13T15:00:00Z")
    assert set(before_capture.register_id) == {"alpha_old", "zacks_date"}


def test_live_offset_ordering_and_cutoff_boundary():
    rows = pd.DataFrame([
        live_row("same_instant_z", "2026-09-13T16:00:00Z"),
        live_row("newer_offset", "2026-09-13T12:30:00-04:00"),
        live_row("future_one_second", "2026-09-13T16:30:01Z"),
        live_row("invalid_stamp", "not-a-date"),
    ])
    chosen = a.select_live_consensus(rows, "2026-09-13T16:30:00Z")
    assert chosen.register_id.tolist() == ["newer_offset"]
    assert chosen.stamp_utc.iloc[0] == pd.Timestamp("2026-09-13T16:30:00Z")


@pytest.mark.parametrize("stamp,date,expected", [
    ("2025-02-13T23:59:00", "2025-02-13", "ambiguous_intraday_timezone"),
    ("2025-02-13T09:00:00", "2025-02-13", "ambiguous_intraday_timezone"),
    ("2025-02-13T15:59:59-05:00", "2025-02-13", "available"),
    ("2025-02-13T16:00:00-05:00", "2025-02-13", "timestamp_at_or_after_market_close"),
    ("2025-02-13T23:59:00-05:00", "2025-02-13", "timestamp_at_or_after_market_close"),
    ("2025-02-13T20:59:59Z", "2025-02-13", "available"),
    ("2025-02-13T21:00:00Z", "2025-02-13", "timestamp_at_or_after_market_close"),
    ("2025-05-01T19:59:59Z", "2025-05-01", "available"),
    ("2025-05-01T20:00:00Z", "2025-05-01", "timestamp_at_or_after_market_close"),
    ("2025-02-14T05:59:59+09:00", "2025-02-13", "available"),
    ("2025-02-13", "2025-02-13", "available"),
    ("2025-02-14", "2025-02-13", "timestamp_after_origin"),
])
def test_historical_intraday_boundary_requires_zone_and_preclose(stamp, date, expected):
    _, reason = a.valid_consensus(register_row(as_of_timestamp=stamp), "2024Q1", date)
    assert reason == expected
