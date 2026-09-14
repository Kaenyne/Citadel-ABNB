"""C3: fixed, vintage-gated univariate screens; no promotions without the named baseline."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'data/processed/forecast_methods/gbv_features_v1'
NOTE = ROOT / 'docs/revenue-forecast-strategy/05_backtests/ALPHA_C3_GBV_FEATURES.md'
MIN_TRAIN = 4
FEATURES = ('rnpl_corrected_unearned', 'funds_growth', 'gbv_momentum',
            'ntto_arrivals', 'reviews_stays', 'hotel_revpar', 'calendar_pickup')
DIAGNOSTIC = 'raw_unearned_diagnostic'
REASONS = {
    'rnpl_corrected_unearned': 'no historical publication vintage for RNPL correction; no baseline exists',
    'ntto_arrivals': 'supplied NTTO observations lack publication dates and revision vintages',
    'reviews_stays': 'supplied quarterly index is reconstructed from later dumps; no historical index-weight vintage',
    'calendar_pickup': 'supplied retrospective pairs lack a complete historical estimation/selection vintage',
}
INPUTS = (
    'data/processed/overnight/02_kpi_panel_quarterly.csv',
    'data/processed/forecast_methods/harness/calendar.csv',
    'data/processed/predictive/02_peer_prints.csv',
    'data/processed/forecast_methods/kernel_phi_v2/D0_carried_and_residual_panel.csv',
    'data/processed/ntto_us_inbound_monthly.csv',
    'data/processed/q3nowcast/E/index_quarterly.csv',
    'data/processed/q3nowcast/E/inventory.csv',
    'data/processed/q3nowcast/F/F2_backtest.csv',
    'analysis/src/forecast_methods/kernel_phi_v2/stage_d.py',
    'data/processed/overnight/08_feature_tests_all.csv',
)


def quarter(x):
    x = str(x)
    return pd.Period(x if len(x) == 6 else f'20{x[-2:]}Q{x[0]}', freq='Q')


def day(x):
    return pd.Timestamp(x).normalize()


def load():
    k = pd.read_csv(ROOT / INPUTS[0], usecols=['quarter', 'gbv_musd',
        'funds_held_for_clients_musd', 'unearned_fees_musd', 'gbv_yoy_reported_pct']).copy()
    k['q'] = k.quarter.map(quarter)
    k = k.set_index('q').sort_index()
    c = pd.read_csv(ROOT / INPUTS[1])
    c['q'] = c.print_quarter.map(quarter)
    c = c.set_index('q').sort_index()
    for col in ('print_date', 'filing_date', 'guide_date'):
        c[col] = pd.to_datetime(c[col]).dt.normalize()
    k['print_date'] = c.print_date.reindex(k.index)
    k['filing_date'] = c.filing_date.reindex(k.index)
    # Exact quarter-key joins, not shift-after-filter, avoid missing-quarter leakage.
    previous = k.gbv_musd.reindex(k.index - 4).to_numpy()
    k['gbv_yoy'] = 100 * (k.gbv_musd.to_numpy() / previous - 1)
    residual = pd.read_csv(ROOT / INPUTS[3])
    residual['q'] = residual.q.map(quarter)
    k['R_musd'] = residual.set_index('q').R_musd.reindex(k.index)
    peers = pd.read_csv(ROOT / INPUTS[2])
    peers['q'] = peers.quarter.map(quarter)
    for peer in ('mar', 'hlt'):
        peers[f'{peer}_report_date'] = pd.to_datetime(peers[f'{peer}_report_date']).dt.normalize()
    origins = []
    for _, row in c.dropna(subset=['guide_date', 'next_quarter_guided']).iterrows():
        target = quarter(row.next_quarter_guided)
        if target in k.index and target <= quarter('2026Q2'):
            origins.append((target, row.guide_date))
    return k, c, peers, sorted(set(origins))


def feature_at(feature, as_of, k, peers):
    """Return a scalar and its latest public-input date; never consume same-day data."""
    cutoff = day(as_of)
    if feature in REASONS:
        return None, REASONS[feature]
    if feature == 'hotel_revpar':
        candidates = []
        for _, row in peers.iterrows():
            values, dates = [], []
            for peer in ('mar', 'hlt'):
                d, v = row[f'{peer}_report_date'], row[f'{peer}_revpar_yoy']
                if pd.notna(d) and d < cutoff and pd.notna(v) and np.isfinite(v):
                    values.append(float(v)); dates.append(d)
            if values:
                candidates.append((row.q, np.mean(values), max(dates), len(values)))
        if not candidates:
            return None, 'no dated peer release before origin'
        q, value, known, n = max(candidates, key=lambda v: v[0])
        return dict(value=float(value), source_quarter=str(q), knowable_from=known,
                    n_components=n), ''
    if feature not in ('funds_growth', 'gbv_momentum', DIAGNOSTIC):
        raise ValueError(f'Unknown feature: {feature}')
    value_col = {'funds_growth': 'funds_held_for_clients_musd',
                 'gbv_momentum': 'gbv_musd', DIAGNOSTIC: 'unearned_fees_musd'}[feature]
    date_col = 'print_date' if feature == 'gbv_momentum' else 'filing_date'
    for q in reversed(k.index):
        prev = q - 4
        if prev not in k.index:
            continue
        a, b = k.loc[q], k.loc[prev]
        dates = [a[date_col], b[date_col]]
        vals = [a[value_col], b[value_col]]
        if any(pd.isna(d) or d >= cutoff for d in dates):
            continue
        if not all(pd.notna(v) and np.isfinite(v) and v > 0 for v in vals):
            continue
        return dict(value=100 * (vals[0] / vals[1] - 1), source_quarter=str(q),
                    knowable_from=max(dates), n_components=1), ''
    return None, 'no annual pair with both source publication dates strictly before origin'


def interval_error(prediction, reported):
    """Signed distance to a reported integer's rounding interval, never force equality."""
    if pd.isna(reported) or not np.isfinite(reported) or float(reported) != round(float(reported)):
        return np.nan
    return prediction - np.clip(prediction, float(reported) - .5, float(reported) + .5)


def fit_at(samples, origin, current):
    train = [s for s in samples if s['target_print'] < origin and s['feature_date'] < s['origin']]
    if len(train) < MIN_TRAIN:
        return None, f'insufficient published training targets ({len(train)} < {MIN_TRAIN})'
    x = np.array([s['feature_value'] for s in train], dtype=float)
    y = np.array([s['actual'] for s in train], dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    if np.linalg.matrix_rank(design) < 2:
        return None, 'singular feature history'
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    return dict(point=float(beta[0] + beta[1] * current['value']),
                slope=float(beta[1]), intercept=float(beta[0]), n_train=len(train),
                last_training_print=max(s['target_print'] for s in train)), ''


def run_screen(k, peers, origins):
    paths, audits = [], []
    for feature in (*FEATURES, DIAGNOSTIC):
        for target in ('gbv_yoy', 'R_musd'):
            samples = []
            for q, origin in origins:
                actual = k.at[q, target]
                if pd.isna(actual):
                    continue
                snapshot, reason = feature_at(feature, origin, k, peers)
                base = dict(feature=feature, target=target, quarter=str(q), vintage_date=origin.date().isoformat())
                if snapshot is None:
                    audits.append(dict(**base, status='unavailable', reason=reason))
                    continue
                fit, reason = fit_at(samples, origin, snapshot)
                if fit is None:
                    audits.append(dict(**base, status='unavailable', reason=reason))
                else:
                    assert snapshot['knowable_from'] < origin
                    assert fit['last_training_print'] < origin
                    reported = k.at[q, 'gbv_yoy_reported_pct'] if target == 'gbv_yoy' else np.nan
                    paths.append(dict(**base, **fit, actual=float(actual), error=fit['point']-actual,
                        feature_value=snapshot['value'], feature_quarter=snapshot['source_quarter'],
                        knowable_from=snapshot['knowable_from'].date().isoformat(),
                        last_training_date=fit['last_training_print'].date().isoformat(), n_params=2,
                        interval_error=interval_error(fit['point'], reported),
                        target_basis='PIT' if target == 'gbv_yoy' else 'full_sample_target_diagnostic'))
                    audits.append(dict(**base, status='scored', reason=''))
                samples.append(dict(actual=float(actual), target_print=k.at[q, 'print_date'],
                    feature_value=snapshot['value'], feature_date=snapshot['knowable_from'], origin=origin))
    return pd.DataFrame(paths).drop(columns=['last_training_print']), pd.DataFrame(audits)


def summarize(paths, audits):
    rows = []
    for feature in FEATURES:
        for target in ('gbv_yoy', 'R_musd'):
            for window, start in [('W1', '2023Q1'), ('W2', '2024Q1')]:
                expected = {str(q) for q in pd.period_range(start, '2026Q2', freq='Q')}
                p = paths[(paths.feature == feature) & (paths.target == target) & paths.quarter.isin(expected)]
                raw = paths[(paths.feature == DIAGNOSTIC) & (paths.target == target) & paths.quarter.isin(expected)]
                common = p.merge(raw[['quarter', 'error']], on='quarter', suffixes=('', '_raw'))
                denominator = np.sqrt(np.mean(common.error_raw**2)) if len(common) else np.nan
                ratio = np.sqrt(np.mean(common.error**2)) / denominator if denominator > 0 else np.nan
                signs = np.sign(p.slope).unique()
                stable = bool(len(p) and len(signs) == 1 and signs[0] != 0)
                interval = p.interval_error.dropna()
                rows.append(dict(feature=feature, target=target, window=window, n=len(p), n_expected=len(expected),
                    rmse=float(np.sqrt(np.mean(p.error**2))) if len(p) else np.nan,
                    interval_n=len(interval), interval_rmse=float(np.sqrt(np.mean(interval**2))) if len(interval) else np.nan,
                    n_required_baseline_common=0, required_ledger_ratio=np.nan, required_ledger_status='no baseline exists',
                    raw_ledger_diagnostic_n=len(common), raw_ledger_diagnostic_ratio=ratio,
                    stable_sign=stable, slope_min=float(p.slope.min()) if len(p) else np.nan,
                    slope_max=float(p.slope.max()) if len(p) else np.nan,
                    excluded_quarters=';'.join(sorted(expected-set(p.quarter))),
                    common_raw_quarters=';'.join(sorted(common.quarter)),
                    verdict='underpowered', promoted=False))
    result = pd.DataFrame(rows)
    result['same_cells_warning'] = ''
    for (feature, target), indexes in result.groupby(['feature', 'target']).groups.items():
        pair = result.loc[indexes]
        cells = pair.common_raw_quarters.tolist()
        if cells[0] and len(set(cells)) == 1:
            result.loc[indexes, 'same_cells_warning'] = 'vacuous across windows: identical common cells'
    return result


def main():
    started = time.perf_counter()
    if not NOTE.exists() or 'Pass line, unchanged:' not in NOTE.read_text(encoding='utf8'):
        raise RuntimeError('Pre-registration note must exist before execution')
    OUT.mkdir(parents=True, exist_ok=True)
    prereg = OUT / 'preregistration.json'
    if not prereg.exists():
        prereg.write_text(json.dumps(dict(features=FEATURES, min_train=MIN_TRAIN,
            pass_line='A feature earns a place only if it beats the ledger baseline (RNPL-corrected unearned fees) on GBV on BOTH windows with a stable coefficient sign. Report everything that did not, with ratios.',
            note_sha256_before_results=hashlib.sha256(NOTE.read_bytes()).hexdigest()), indent=2)+'\n', encoding='utf8')
    frozen_prereg = OUT / 'preregistered_note.md'
    if not frozen_prereg.exists():
        expected = json.loads(prereg.read_text(encoding='utf8'))['note_sha256_before_results']
        if hashlib.sha256(NOTE.read_bytes()).hexdigest() != expected:
            raise RuntimeError('Original pre-registration note changed before its snapshot was saved')
        frozen_prereg.write_bytes(NOTE.read_bytes())
    k, calendar, peers, origins = load()
    paths, audit = run_screen(k, peers, origins)
    summary = summarize(paths, audit)
    paths.to_csv(OUT / 'forecast_path.csv', index=False)
    audit.to_csv(OUT / 'availability_and_exclusions.csv', index=False)
    summary.to_csv(OUT / 'full_failure_table.csv', index=False)
    pd.DataFrame([dict(path=p, sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),
        usage='read-only supplied summary/source; no new raw data') for p in INPUTS]).to_csv(OUT/'input_manifest.csv', index=False)
    summary[summary.promoted].to_csv(OUT/'survivors.csv', index=False)
    pd.DataFrame([dict(feature=f, status='unavailable', reason=r) for f,r in REASONS.items()]).to_csv(OUT/'unavailable_features.csv', index=False)
    cols = ['feature', 'target', 'window', 'n', 'rmse', 'raw_ledger_diagnostic_n', 'raw_ledger_diagnostic_ratio', 'stable_sign']
    display = summary[cols].round(4).to_string(index=False)
    report = ('No features promoted. Required RNPL-adjusted ledger baseline: no baseline exists on W1 or W2.\n\n'
              'Every ratio below is a separate raw-unearned-fees diagnostic; it cannot satisfy the pass line.\n\n'+display+'\n')
    (OUT/'results.txt').write_text(report, encoding='utf8')
    elapsed = time.perf_counter()-started
    result = dict(verdict='underpowered', promoted_features=0, strict_RNPL_baseline_cells_W1=0,
        strict_RNPL_baseline_cells_W2=0, forecasts=len(paths), registered_rows=0,
        runtime_seconds=round(elapsed, 3), tuned_parameters=0, regression_parameters=2,
        consensus_used=False, network_requests=0, tokens='unavailable')
    (OUT/'run_summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(report)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
