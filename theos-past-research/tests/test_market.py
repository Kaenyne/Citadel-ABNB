from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from abnb_guidance.market import compute_total_return, reaction_session


NY = ZoneInfo("America/New_York")
SESSIONS = [date(2024, 5, 7), date(2024, 5, 8), date(2024, 5, 9), date(2024, 5, 10)]


def test_after_close_release_reacts_next_session():
    published = datetime(2024, 5, 8, 16, 5, tzinfo=NY)

    assert reaction_session(published, SESSIONS) == date(2024, 5, 9)


def test_before_open_release_reacts_same_session():
    published = datetime(2024, 5, 8, 8, 0, tzinfo=NY)

    assert reaction_session(published, SESSIONS) == date(2024, 5, 8)


def test_non_session_release_reacts_next_session():
    published = datetime(2024, 5, 11, 12, 0, tzinfo=NY)
    sessions = SESSIONS + [date(2024, 5, 13)]

    assert reaction_session(published, sessions) == date(2024, 5, 13)


def test_one_session_return_uses_prior_close_to_reaction_close():
    prices = pd.Series(
        [100.0, 90.0, 99.0],
        index=pd.to_datetime(["2024-05-07", "2024-05-08", "2024-05-09"]),
    )

    assert compute_total_return(prices, date(2024, 5, 8), sessions=1) == pytest.approx(-0.10)


def test_return_window_rejects_insufficient_price_history():
    prices = pd.Series([100.0], index=pd.to_datetime(["2024-05-08"]))

    with pytest.raises(ValueError, match="prior close"):
        compute_total_return(prices, date(2024, 5, 8), sessions=1)
