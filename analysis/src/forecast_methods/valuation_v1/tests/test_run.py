from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location('valuation_run', Path(__file__).parents[1] / 'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


@pytest.mark.parametrize('stamp', ['2026-09-12', '2026-09-12T01:00:00', '2026-09-13'])
def test_refuses_same_day_or_later_training(stamp):
    with pytest.raises(ValueError, match='strictly before'):
        m.before(pd.DataFrame({'month_end': [stamp]}), '2026-09-12')


def test_equity_bridge_and_invalid_denominator():
    assert m.equity_price(10, 20, -5, 5) == 39
    with pytest.raises(ValueError):
        m.equity_price(10, 20, 5, 0)


def test_expanding_fit_recovers_known_level_relation():
    rng = np.random.default_rng(31)
    frame = pd.DataFrame(rng.normal(size=(36, 3)), columns=m.XCOLS)
    frame['month_end'] = pd.date_range('2020-01-31', periods=36, freq='ME').strftime('%Y-%m-%d')
    frame['last_reported_quarter'] = '4Q19'
    frame['ev_ltm_ebitda_x'] = 7 + frame[m.XCOLS] @ np.array([.4, -.2, 1.1])
    result = m.fit(frame, '2023-01-01', changes=False, window='ALL')
    assert result['slope_turns_per_growth_pp'] == pytest.approx(.4)
    assert result['last_observation'] < '2023-01-01'


def test_small_change_sample_abstains():
    frame = pd.DataFrame({col: np.arange(15) for col in m.XCOLS + ['ev_ltm_ebitda_x']})
    frame['month_end'] = pd.date_range('2020-01-31', periods=15, freq='ME').strftime('%Y-%m-%d')
    frame['last_reported_quarter'] = '4Q19'
    result = m.fit(frame, '2023-01-01', changes=True, window='ALL')
    assert result['status'] == 'underpowered'
    assert result['n'] == 3
