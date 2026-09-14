"""returns_v1 -- the executable-return convention is what the file says it is (offline, committed data).

  python -m pytest analysis/src/forecast_methods/returns_v1/tests -q
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from returns_v1 import paths as P
from returns_v1 import build_open_returns as B


@pytest.fixture(scope="module")
def table():
    return pd.read_csv(P.OPEN_RETURNS, parse_dates=["event_date", "entry_date"])


@pytest.fixture(scope="module")
def ohlc():
    return B.load_ohlc()


def test_committed_files_and_manifest_exist():
    assert P.OHLC.exists() and P.OPEN_RETURNS.exists() and P.MANIFEST.exists()
    man = json.loads(P.MANIFEST.read_text())
    for k in ("source", "retrieved_at_utc", "sha256", "rows", "auto_adjust"):
        assert k in man
    assert man["auto_adjust"] is False


def test_one_row_per_ledger_event(table):
    ev = B.events()
    assert len(table) == len(ev) == 23
    assert table["print_quarter"].is_unique


def test_entry_is_strictly_after_the_letter_and_is_a_trading_day(table, ohlc):
    assert (table["entry_date"] > table["event_date"]).all()
    days = set(ohlc["ABNB"].index)
    assert all(d in days for d in table["entry_date"])
    # the letter itself is on a trading day (after the close) for every event
    assert all(d in days for d in table["event_date"])


def test_excess_is_abnb_minus_qqq(table):
    for h in P.HORIZONS:
        m = table[f"open_{h}d_pct"].notna()
        np.testing.assert_allclose(table.loc[m, f"excess_open_{h}d_pct"],
                                   table.loc[m, f"open_{h}d_pct"] - table.loc[m, f"qqq_open_{h}d_pct"], atol=1e-9)


def test_gap_and_open_1d_compound_to_close_to_close(table):
    lhs = (1 + table["gap_pct"] / 100) * (1 + table["open_1d_pct"] / 100) - 1
    np.testing.assert_allclose(100 * lhs, table["cc_1d_pct"], atol=1e-9)


def test_hand_recompute_of_one_event(table, ohlc):
    # 6 Aug 2025 letter -> entry 7 Aug 2025 open; 20-day exit = 20th bar counting the entry day
    px = ohlc["ABNB"]
    r = table[table["event_date"] == "2025-08-06"].iloc[0]
    assert str(r["entry_date"].date()) == "2025-08-07"
    i = px.index.get_loc(pd.Timestamp("2025-08-07"))
    o = px["open"].iloc[i]
    assert r["open_1d_pct"] == pytest.approx(100 * (px["close"].iloc[i] / o - 1), abs=1e-9)
    assert r["open_20d_pct"] == pytest.approx(100 * (px["close"].iloc[i + 19] / o - 1), abs=1e-9)


def test_unfinished_horizons_are_empty_not_truncated(table):
    for h in P.HORIZONS:
        short = table[table["bars_after_entry"] < h]
        assert short[f"open_{h}d_pct"].isna().all()
        long = table[table["bars_after_entry"] >= h]
        assert long[f"open_{h}d_pct"].notna().all()


def test_reconciles_with_the_legacy_close_based_file():
    legacy = pd.read_csv(P.LEGACY_REACTIONS)
    new = pd.read_csv(P.OPEN_RETURNS)
    m = legacy.merge(new, left_on="quarter", right_on="print_quarter")
    assert len(m) >= 20
    diff = (m["abnb_1d_pct"] - m["cc_1d_pct"]).abs()
    # same event, same definition, different vendor rounding: agree to within 1pp on >= 90% of events
    assert (diff < 1.0).mean() >= 0.9, diff.describe()
    assert np.sign(m["abnb_1d_pct"]).eq(np.sign(m["cc_1d_pct"].round(1))).mean() >= 0.9
