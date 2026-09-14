import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location('c3_screen', Path(__file__).parents[1] / 'run.py')
screen = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(screen)


def test_reported_integer_interval_edges():
    assert screen.interval_error(10.5, 10) == 0
    assert screen.interval_error(9.5, 10) == 0
    assert screen.interval_error(11, 10) == .5
    assert screen.interval_error(9, 10) == -.5
    assert np.isnan(screen.interval_error(10, 10.2))


def test_unavailable_rnpl_cannot_silently_become_raw_ledger():
    value, reason = screen.feature_at('rnpl_corrected_unearned', '2025-05-01', None, None)
    assert value is None
    assert 'no baseline exists' in reason


def test_same_day_peer_is_refused_even_with_intraday_origin():
    peers = pd.DataFrame([dict(q=screen.quarter('2024Q1'), mar_report_date=pd.Timestamp('2024-05-08'),
        mar_revpar_yoy=9., hlt_report_date=pd.NaT, hlt_revpar_yoy=np.nan)])
    value, _ = screen.feature_at('hotel_revpar', '2024-05-08 23:59', None, peers)
    assert value is None
    value, _ = screen.feature_at('hotel_revpar', '2024-05-09', None, peers)
    assert value['value'] == 9.


def test_future_peer_mutation_does_not_change_snapshot():
    k, _, peers, _ = screen.load()
    before, _ = screen.feature_at('hotel_revpar', '2024-05-08', k, peers)
    for peer in ('mar', 'hlt'):
        peers.loc[peers[f'{peer}_report_date'] >= pd.Timestamp('2024-05-08'), f'{peer}_revpar_yoy'] = 1e9
    after, _ = screen.feature_at('hotel_revpar', '2024-05-08', k, peers)
    assert before == after


def test_missing_annual_pair_date_refused():
    k, _, peers, _ = screen.load()
    k['filing_date'] = pd.NaT
    value, _ = screen.feature_at('funds_growth', '2026-08-06', k, peers)
    assert value is None


def test_same_day_target_cannot_train():
    origin = pd.Timestamp('2024-05-08')
    samples = [dict(target_print=origin, feature_date=origin-pd.Timedelta(days=2),
        origin=origin-pd.Timedelta(days=1), feature_value=float(i), actual=float(i)) for i in range(10)]
    fitted, reason = screen.fit_at(samples, origin, {'value': 1.})
    assert fitted is None
    assert '(0 < 4)' in reason


def test_all_computed_forecasts_use_strict_prior_dates():
    k, _, peers, origins = screen.load()
    paths, _ = screen.run_screen(k, peers, origins)
    assert len(paths) > 0
    assert (pd.to_datetime(paths.knowable_from) < pd.to_datetime(paths.vintage_date)).all()
    assert (pd.to_datetime(paths.last_training_date) < pd.to_datetime(paths.vintage_date)).all()
    assert (paths.n_train >= screen.MIN_TRAIN).all()
