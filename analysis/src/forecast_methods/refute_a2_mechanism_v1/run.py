"""Independent A2 mechanism diagnostics; no imports from A2, no registrations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'data/processed/forecast_methods/refute_a2_mechanism_v1'
INPUTS = {
    'cells': 'data/processed/forecast_methods/alpha_a2/cells.csv',
    'register': 'data/processed/forecast_methods/L0/L0_vintage_register.csv',
    'kpi': 'data/processed/overnight/02_kpi_panel_quarterly.csv',
    'guides': 'data/processed/overnight/02_guidance_ledger.csv',
    'returns': 'data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv',
    'ohlc': 'data/processed/forecast_methods/returns_v1/ohlc_daily.csv',
    'registry': 'data/processed/forecast_methods/registry/alpha-a2__guide_mid_next_q.csv',
}


def quarter_old(q):
    return f'{q[-1]}Q{q[2:4]}'


def corr(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return float('nan')
    return float(np.corrcoef(x, y)[0, 1])


def partial(df, x, y, controls):
    z = df[[x, y] + controls].dropna()
    design = np.column_stack([np.ones(len(z)), z[controls].to_numpy(float)])
    rank = np.linalg.matrix_rank(design)
    if len(z) <= rank + 1:
        return {'n': len(z), 'raw': corr(z[x], z[y]), 'partial': float('nan'), 'control_rank': int(rank)}
    rx = z[x].to_numpy() - design @ np.linalg.lstsq(design, z[x], rcond=None)[0]
    ry = z[y].to_numpy() - design @ np.linalg.lstsq(design, z[y], rcond=None)[0]
    return {'n': len(z), 'raw': corr(z[x], z[y]), 'partial': corr(rx, ry), 'control_rank': int(rank)}


def bootstrap_mean(values, seed=20260913):
    """Length-2 circular blocks, fixed 2000 draws, descriptive 90% interval."""
    v = np.asarray(values, float)
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, len(v), size=(2000, (len(v) + 1) // 2))
    indices = (starts[:, :, None] + np.arange(2)[None, None, :]) % len(v)
    means = v[indices.reshape(2000, -1)[:, :len(v)]].mean(axis=1)
    return [float(x) for x in np.quantile(means, [.05, .95])]


def main():
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    frames = {k: pd.read_csv(ROOT / p, comment='#') for k, p in INPUTS.items()}
    cells, register, kpi, guides, returns, ohlc, registry = [frames[k] for k in INPUTS]
    eligible = cells.loc[cells['evaluable'] & cells['quarter'].between('2023Q1', '2026Q2')].copy()
    # Independently reconstruct consensus, guide gap and GBV surprise. Kernel point
    # is the registered engine output; this mechanism audit does not re-fit lambda.
    source_rows = []
    for _, c in eligible.iterrows():
        pg = register.loc[register.register_id.eq(c.consensus_register_id)]
        assert len(pg) == 1
        pg = pg.iloc[0]
        assert pg.role == 'pre_guide' and bool(pg.pit_usable) and bool(pg.vendor_attributed)
        assert pd.to_datetime(pg.as_of_timestamp, utc=True) <= pd.to_datetime(c.guide_date, utc=True)
        guide = guides.loc[guides.target_period.eq(quarter_old(c.quarter)) & guides.print_date.eq(c.guide_date) & guides.metric.eq('revenue_usd_m')]
        assert len(guide) == 1
        guide_mid = float(guide.iloc[0].value_mid)
        rp = registry.loc[registry.quarter.eq(c.quarter) & registry.window.eq('W1') & registry.prior_basis.eq('PIT')]
        assert len(rp) == 1
        kernel = float(rp.iloc[0].point)
        consensus = float(pg.value)
        signal = 100 * (kernel / consensus - 1)
        gap = 100 * (guide_mid / consensus - 1)
        assert np.isclose(signal, c.signal_pct, atol=1e-10)
        assert np.isclose(gap, c.actual_gap_pct, atol=1e-10)
        printed = kpi.loc[kpi.quarter.eq(quarter_old(c.print_quarter))]
        assert len(printed) == 1
        # The A2 printed GBV field is the letter's busd precision.
        gbv_actual = float(printed.iloc[0].gbv_busd) * 1000
        assert np.isclose(gbv_actual, c.gbv_actual_musd)
        ap = register.loc[register.register_id.eq('AP-' + c.print_quarter + '-gbv')]
        gbv_surprise, ap_vendor, ap_stamp, ap_id, ap_value, ap_unit = np.nan, '', '', '', np.nan, ''
        if len(ap):
            assert len(ap) == 1
            a = ap.iloc[0]
            if bool(a.pit_usable) and bool(a.vendor_attributed) and pd.notna(a.value):
                assert a.role == 'at_print'
                assert pd.to_datetime(a.as_of_timestamp, utc=True) <= pd.to_datetime(c.guide_date, utc=True)
                assert a.unit in ['busd', 'musd']
                gbv_consensus = float(a.value) * (1000 if a.unit == 'busd' else 1)
                gbv_surprise = 100 * (gbv_actual / gbv_consensus - 1)
                ap_vendor, ap_stamp, ap_id, ap_value, ap_unit = a.vendor, a.as_of_timestamp, a.register_id, float(a.value), a.unit
        assert np.isclose(gbv_surprise, c.gbv_surprise_pct, equal_nan=True, atol=1e-10)
        source_rows.append({'quarter': c.quarter, 'guide_date': c.guide_date,
                            'signal': signal, 'gap': gap, 'kernel_musd': kernel,
                            'guide_musd': guide_mid, 'consensus_musd': consensus,
                            'consensus_vendor': pg.vendor, 'consensus_stamp': pg.as_of_timestamp,
                            'consensus_id': pg.register_id, 'gbv_actual_musd': gbv_actual,
                            'gbv_surprise': gbv_surprise, 'gbv_vendor': ap_vendor,
                            'gbv_stamp': ap_stamp, 'gbv_id': ap_id, 'gbv_source_value': ap_value,
                            'gbv_source_unit': ap_unit})
    data = pd.DataFrame(source_rows).merge(returns, left_on='guide_date', right_on='event_date', validate='one_to_one')
    assert len(data) == 11
    data['season'] = data.quarter.str[-1].astype(int)
    data['high_signal'] = data.signal.abs().gt(1)
    data['sign_hit'] = np.sign(data.signal).eq(np.sign(data.gap))
    prices = ohlc.pivot(index='date', columns='ticker', values='close').sort_index()
    daily = prices.pct_change(fill_method=None).dropna(subset=['ABNB', 'QQQ'])
    beta_values, beta_ns = [], []
    for _, r in data.iterrows():
        hist = daily.loc[daily.index < r.guide_date, ['ABNB', 'QQQ']].tail(252)
        assert len(hist) >= 126
        beta = np.linalg.lstsq(np.column_stack([np.ones(len(hist)), hist.QQQ]), hist.ABNB, rcond=None)[0][1]
        beta_values.append(beta)
        beta_ns.append(len(hist))
        # Independent open-to-close 20-bar return reconstruction from raw OHLC.
        for ticker, column in [('ABNB', 'open_20d_pct'), ('QQQ', 'qqq_open_20d_pct')]:
            p = ohlc.loc[ohlc.ticker.eq(ticker) & ohlc.date.ge(r.entry_date)].sort_values('date')
            assert len(p) >= 20 and p.iloc[0].date == r.entry_date
            actual = 100 * (float(p.iloc[19].close) / float(p.iloc[0].open) - 1)
            assert np.isclose(actual, r[column], atol=1e-9)
    data['beta_pre_event'] = beta_values
    data['beta_n'] = beta_ns
    data['beta_excess_20d'] = data.open_20d_pct - data.beta_pre_event * data.qqq_open_20d_pct
    data['kernel_signed_20d'] = np.sign(data.signal) * data.excess_open_20d_pct
    data['gap_signed_20d'] = np.sign(data.gap) * data.excess_open_20d_pct
    data['guide_minus_kernel_return'] = data.gap_signed_20d - data.kernel_signed_20d
    for season in [2, 3, 4]:
        data[f'season_{season}'] = data.season.eq(season).astype(float)
    summaries, controls, seasonal, deletions, hedge, baselines = [], [], [], [], [], []
    for window, start in [('W1', '2023Q1'), ('W2', '2024Q1')]:
        d = data.loc[data.quarter.ge(start)].copy()
        high = d.loc[d.high_signal].copy()
        summaries.append({'window': window, 'evaluable_n': len(d), 'n': len(high), 'hits': int(high.sign_hit.sum()),
                          'kernel_signed_20d': high.kernel_signed_20d.mean(), 'guide_signed_20d': high.gap_signed_20d.mean(),
                          'guide_minus_kernel_20d': high.guide_minus_kernel_return.mean(),
                          'gap_corr': corr(d.signal, d.gap), 'raw_return_corr': corr(d.signal, d.excess_open_20d_pct),
                          'positive_gap_n': int(high.gap.gt(0).sum()), 'negative_gap_n': int(high.gap.lt(0).sum()),
                          'named_gbv_vendor_n': int((d.gbv_surprise.notna() & d.gbv_vendor.ne('vendor_not_recorded')).sum())})
        for label, cov in [('GBV', ['gbv_surprise']), ('guide_gap', ['gap']), ('GBV_and_gap', ['gbv_surprise', 'gap']), ('season', ['season_2', 'season_3', 'season_4'])]:
            for target in ['excess_open_20d_pct', 'gap']:
                if target in cov:
                    continue
                controls.append({'window': window, 'target': target, 'controls': label, **partial(d, 'signal', target, cov)})
        for season, group in high.groupby('season'):
            seasonal.append({'window': window, 'season': int(season), 'n': len(group), 'hits': int(group.sign_hit.sum()),
                             'kernel_signed_20d': group.kernel_signed_20d.mean(), 'guide_signed_20d': group.gap_signed_20d.mean()})
        for season in range(1, 5):
            group = high.loc[high.season.ne(season)]
            deletions.append({'window': window, 'omitted_season': season, 'n': len(group), 'hits': int(group.sign_hit.sum()),
                              'kernel_signed_20d': group.kernel_signed_20d.mean()})
        for label, col in [('unit_QQQ', 'excess_open_20d_pct'), ('unhedged', 'open_20d_pct'), ('PIT_beta_QQQ', 'beta_excess_20d')]:
            signed = np.sign(high.signal) * high[col]
            lo, hi = bootstrap_mean(signed)
            hedge.append({'window': window, 'hedge': label, 'n': len(high), 'signed_mean': signed.mean(), 'q05_block': lo, 'q95_block': hi})
        for label, sign in [('always_positive', np.ones(len(high))), ('always_negative', -np.ones(len(high))), ('actual_guide_gap', np.sign(high.gap).to_numpy())]:
            baselines.append({'window': window, 'baseline': label, 'n': len(high), 'guide_sign_hits': int((sign == np.sign(high.gap)).sum()),
                              'signed_mean': (sign * high.excess_open_20d_pct.to_numpy()).mean()})
    # A pure season sign baseline is chosen only on prior admissible letters;
    # this remains a small-sample diagnostic, with abstentions at empty seasons.
    season_baseline = []
    for _, row in data.iterrows():
        prior = data.loc[data.guide_date.lt(row.guide_date) & data.season.eq(row.season)]
        prediction = np.sign(prior.gap.mean()) if len(prior) else np.nan
        season_baseline.append({'quarter': row.quarter, 'season': row.season, 'high_signal': row.high_signal,
                                'prior_n': len(prior), 'sign': prediction,
                                'hit': float(prediction == np.sign(row.gap)) if len(prior) else np.nan,
                                'signed_return': prediction * row.excess_open_20d_pct})
    for name, frame in [('cells', data), ('summary', pd.DataFrame(summaries)), ('controls', pd.DataFrame(controls)),
                        ('seasonal', pd.DataFrame(seasonal)), ('leave_season_out', pd.DataFrame(deletions)),
                        ('hedge', pd.DataFrame(hedge)), ('baselines', pd.DataFrame(baselines)), ('prior_season_baseline', pd.DataFrame(season_baseline))]:
        frame.to_csv(OUT / (name + '.csv'), index=False)
    audit = {'run_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.perf_counter() - started,
             'input_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in INPUTS.values()},
             'assertions': '11 source-reconstructed signals/gaps/GBV controls agree; 22 raw 20-bar OHLC returns agree; each beta has 252 strictly pre-event days',
             'registered_rows': 0, 'scorers_run': False,
             'note': 'Exploratory mechanism diagnostics only. K0 points are read from registered PIT W1 output. No re-fit of lambda.'}
    (OUT / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    print(pd.DataFrame(summaries).to_string(index=False))
    print(pd.DataFrame(controls).to_string(index=False))
    print(pd.DataFrame(hedge).to_string(index=False))
    print('Independent source and return reconstruction assertions PASS; runtime %.3fs' % audit['elapsed_seconds'])


if __name__ == '__main__':
    main()
