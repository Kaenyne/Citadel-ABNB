"""Reconstruct A2's exact headline using the mandated K0 engine and independent joins."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'analysis/src/forecast_methods'))
from kernel_engine_v2 import engine as K

OUT = ROOT / 'data/processed/forecast_methods/refute_a2_vintage'
PATHS = {
    'calendar': 'data/processed/forecast_methods/harness/calendar.csv',
    'targets': 'data/processed/forecast_methods/harness/targets.csv',
    'kpi': 'data/processed/overnight/02_kpi_panel_quarterly.csv',
    'cushion': 'data/processed/overnight/02_guidance_cushion_series.csv',
    'consensus': 'data/processed/forecast_methods/L0/L0_vintage_register.csv',
    'returns': 'data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv',
    'cells': 'data/processed/forecast_methods/alpha_a2/cells.csv',
    'registry': 'data/processed/forecast_methods/registry/alpha-a2__guide_mid_next_q.csv',
}


def truth(value):
    return str(value).lower() == 'true'


def quarter(value):
    value = str(value)
    return f'20{value[2:]}Q{value[0]}' if len(value) == 4 else value


def flagged_consensus(row, origin):
    stamp = pd.to_datetime(row.as_of_timestamp, utc=True, errors='coerce')
    unknown_vendor = pd.isna(row.vendor) or str(row.vendor).strip() in ('', 'vendor_not_recorded')
    reasons = []
    if row.role not in ('pre_guide', 'at_print'):
        reasons.append('invalid_historical_role')
    if not truth(row.pit_usable):
        reasons.append('pit_usable_false')
    if not truth(row.vendor_attributed):
        reasons.append('vendor_unattributed')
    if pd.isna(stamp):
        reasons.append('missing_timestamp')
    elif stamp.date() > origin.date():
        reasons.append('future_date')
    if not np.isfinite(row.value) or row.value <= 0:
        reasons.append('invalid_value')
    return reasons, unknown_vendor


def summarize(frame, signal_col):
    output = []
    for window, low in [('W1', '2023Q1'), ('W2', '2024Q1')]:
        w = frame[frame.quarter.between(low, '2026Q2')]
        valid = w.dropna(subset=[signal_col, 'actual_gap'])
        hi = valid[(valid[signal_col].abs() > 1) & (valid.actual_sign.abs() == 1)]
        signed = np.sign(hi[signal_col]) * hi.excess_open_20d_pct
        output.append(dict(variant=signal_col, window=window, candidates=len(w), evaluable=len(valid),
                           high_n=len(hi), hits=int((np.sign(hi[signal_col]) == hi.actual_sign).sum()),
                           signed_return20_n=int(signed.notna().sum()), signed_return20_mean=float(signed.mean())))
    return output


def main():
    start = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    frames = {name: pd.read_csv(ROOT / path, comment='#') for name, path in PATHS.items()}
    calendar = frames['calendar'].set_index('print_quarter').print_date.map(pd.Timestamp).to_dict()
    panel = frames['kpi'].copy()
    panel['quarter'] = panel.quarter.map(quarter)
    panel['print_date'] = panel.quarter.map(calendar)
    cushions = frames['cushion'].copy()
    cushions['quarter'] = cushions.target_period.map(quarter)
    cushions['print_date'] = cushions.quarter.map(calendar)
    cushions['ratio'] = cushions.actual / cushions.value_mid
    source = frames['consensus']
    returns = frames['returns'].set_index('event_date')
    gbv = panel.set_index('quarter').gbv_musd.to_dict()
    cells = []
    sources = []
    for target in frames['targets'][frames['targets'].quarter.between('2021Q4', '2026Q2')].itertuples():
        q, d = target.quarter, pd.Timestamp(target.guide_date)
        before = d + pd.Timedelta(days=1)
        pq = str(pd.Period(q, freq='Q') - 1)
        older = str(pd.Period(q, freq='Q') - 2)
        found = source[(source.period == q) & (source.metric == 'revenue') & (source.role == 'pre_guide')]
        assert len(found) == 1, (q, len(found))
        c = found.iloc[0]
        reasons, unknown = flagged_consensus(c, d)
        cons = float(c.value) if not reasons and not unknown else np.nan
        for role, period, metric in [('pre_guide', q, 'revenue'), ('at_print', pq, 'gbv'), ('at_print', pq, 'revenue')]:
            obs = source[(source.period == period) & (source.metric == metric) & (source.role == role)]
            for _, observed in obs.iterrows():
                flags, unknown_vendor = flagged_consensus(observed, d)
                sources.append(dict(quarter=q, origin=str(d.date()), role=role, metric=metric,
                    register_id=observed.register_id, vendor=observed.vendor, as_of_timestamp=observed.as_of_timestamp,
                    pit_usable=observed.pit_usable, vendor_attributed=observed.vendor_attributed,
                    source_value=observed.value, unit=observed.unit, source_note=observed.note,
                    source_path=observed.source_path, url=observed.url, exclusion='|'.join(flags),
                    vendor_name_missing=unknown_vendor,
                    explicit_intraday_stamp=('T' in str(observed.as_of_timestamp) or ':' in str(observed.as_of_timestamp))))
        p = panel[panel.print_date <= d].copy()
        ch = cushions[cushions.print_date <= d].copy()
        row = dict(quarter=q, guide_date=str(d.date()), consensus=cons, consensus_id=c.register_id,
            vendor=c.vendor, consensus_stamp=c.as_of_timestamp, consensus_exclusion='|'.join(reasons),
            actual_guide=target.guide_mid, actual_gap=100*(target.guide_mid/cons-1),
            actual_sign=1 if target.guide_mid-.5 > cons else -1 if target.guide_mid+.5 < cons else 0,
            panel_max_date=str(p.print_date.max().date()),
            gbv_lag1_date=str(calendar[pq].date()), gbv_lag2_date=str(calendar[older].date()),
            kernel_point=np.nan, signal=np.nan, future_lambda_signal=np.nan,
            future_gbv_signal=np.nan, both_future_signal=np.nan)
        try:
            # All data passed to K0 are manually clipped before calling its authoritative estimator.
            f = K.kernel_guide(q, before, panel=p, cushion_frame=ch)
            direct = K.kernel_guide(q, before)
            assert abs(f['point']-direct['point']) < 1e-9
            assert pd.Timestamp(f['knowable_from']) <= d
            training_dates = [calendar[t] for t in f['training_quarters']]
            assert max(training_dates) <= d
            tail = ch.sort_values('quarter').tail(8)
            divisor = float(np.median(tail.ratio))
            assert abs((divisor-1)-f['cushion']) < 1e-12
            assert q not in set(tail.quarter)
            row.update(kernel_point=f['point'], signal=100*(f['point']/cons-1),
                kernel_status='available', lambda_pct=f['lambda_pct'], variant=f['variant'],
                training_quarters=json.dumps(f['training_quarters']), n_train=f['n_train'],
                lambda_max_date=str(max(training_dates).date()), cushion=divisor-1, cushion_n=len(tail),
                cushion_quarters=json.dumps(tail.quarter.tolist()),
                cushion_max_date=str(tail.print_date.max().date()), knowable_from=f['knowable_from'])
            future_base = (2*gbv[q]+gbv[pq])/3
            row['future_gbv_signal'] = 100*((f['lambda_pct']/100*future_base/divisor)/cons-1)
        except K.DataUnavailable as exc:
            row['kernel_status'] = str(exc)
            divisor = float(ch.sort_values('quarter').tail(8).ratio.median())
            future_base = (2*gbv[q]+gbv[pq])/3
        # Deliberate look-ahead: update the same target-season lambda at the next letter.
        # Keep the original cushion to isolate lambda/GBV leakage.
        try:
            future = K.pit_lambda(int(q[-1]), calendar[q]+pd.Timedelta(days=1))
            base = (2*gbv[pq]+gbv[older])/3
            row.update(future_lambda_pct=future['lambda_pct'],
                       future_lambda_date=str(calendar[q].date()),
                       future_lambda_signal=100*((future['lambda_pct']/100*base/divisor)/cons-1),
                       both_future_signal=100*((future['lambda_pct']/100*future_base/divisor)/cons-1))
        except K.DataUnavailable:
            pass
        event = returns.loc[target.guide_date]
        assert pd.Timestamp(event.entry_date) > d
        assert event.guided_quarter == q
        assert abs(event.excess_open_20d_pct - (event.open_20d_pct-event.qqq_open_20d_pct)) < 1e-10
        row.update(entry_date=event.entry_date, excess_open_20d_pct=event.excess_open_20d_pct)
        cells.append(row)
    independently = pd.DataFrame(cells)
    original = frames['cells'].set_index('quarter')
    independently['a2_point_delta'] = independently.apply(lambda r:r.kernel_point-original.loc[r.quarter,'default_kernel_guide_musd'],axis=1)
    independently['a2_signal_delta'] = independently.apply(lambda r:r.signal-original.loc[r.quarter,'signal_pct'],axis=1)
    assert independently.a2_point_delta.abs().max() < 1e-9
    assert independently.a2_signal_delta.abs().max() < 1e-10
    stats = pd.DataFrame(sum([summarize(independently, c) for c in ['signal','future_lambda_signal','future_gbv_signal','both_future_signal']], []))
    base = stats[stats.variant == 'signal'].set_index('window')
    assert (int(base.loc['W1','hits']),int(base.loc['W1','high_n'])) == (7,8)
    assert (int(base.loc['W2','hits']),int(base.loc['W2','high_n'])) == (6,7)
    registry = frames['registry'].copy()
    historical = registry[registry.window.isin(['W1','W2'])]
    pit = historical[historical.prior_basis == 'PIT']
    for r in pit.itertuples():
        own = independently[independently.quarter == r.quarter].iloc[0]
        assert r.vintage_date == own.guide_date
        assert pd.Timestamp(r.knowable_from) <= pd.Timestamp(r.vintage_date)
        assert abs(r.point-own.kernel_point) < 1e-9
    # Synthetic attack on the selector implementation, explicitly excluded from empirical counts.
    spec = importlib.util.spec_from_file_location('a2_selector_under_audit', ROOT/'analysis/src/forecast_methods/alpha_a2/run.py')
    a2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a2)
    synthetic = source[source.register_id == 'PG-2025Q1-revenue'].copy()
    assert len(synthetic) == 1
    synthetic['as_of_timestamp'] = '2025-02-13T23:59:00'
    _, synthetic_status = a2.valid_consensus(synthetic,'2025Q1','2025-02-13')
    original_snapshot = json.loads((ROOT/'data/processed/forecast_methods/alpha_a2/audit.json').read_text())
    actual_hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PATHS.values()}
    shared_hash_matches = {p:actual_hashes[p] == old for p,old in original_snapshot['inputs_sha256'].items() if p in actual_hashes}
    assert all(shared_hash_matches.values())
    result = dict(runtime_seconds=time.perf_counter()-start, exact_claim_verdict='SURVIVED',
        max_point_difference_musd=float(independently.a2_point_delta.abs().max()),
        max_signal_difference_pp=float(independently.a2_signal_delta.abs().max()),
        historical_registry_rows=len(historical), pit_registry_rows=len(pit), live_registry_rows=int((registry.window=='LIVE').sum()),
        synthetic_postclose_status=synthetic_status,
        synthetic_caveat='Date normalization accepts a deliberately late same-day timestamp; no actual historical denominator has an intraday stamp.',
        shared_input_hashes_match_a2=shared_hash_matches, input_sha256=actual_hashes,
        n_params_added=0, scorers_run=False, forecasts_registered=False)
    independently.to_csv(OUT/'independent_cells.csv',index=False)
    pd.DataFrame(sources).to_csv(OUT/'consensus_row_audit.csv',index=False)
    stats.to_csv(OUT/'summary_and_lookahead.csv',index=False)
    (OUT/'audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(stats.to_string(index=False))
    print(json.dumps(result,indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
