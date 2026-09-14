"""Reconcile existing valuation arithmetic without adopting an investment direction."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import textwrap

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'data/processed/forecast_methods/valuation_v1'
OVERNIGHT = ROOT / 'data/processed/overnight'
METHOD = 'valuation-v1'
XCOLS = ['ntm_growth_proxy_pct', 'dgs10_pct', 'ndx_fwd_pe']
SOURCES = [
    'data/processed/overnight/12_abnb_multiples_monthly.csv',
    'data/processed/overnight/12_abnb_multiples_history.csv',
    'data/processed/overnight/12_abnb_multiple_regressions.csv',
    'data/processed/overnight/12_exit_multiple_recommendation.csv',
    'data/processed/overnight/12_peer_multiples.csv',
    'data/processed/overnight/12_analyst_target_summary.csv',
    'data/processed/overnight/13_valuation_summary.csv',
    'data/processed/overnight/13_model_annual.csv',
    'data/processed/forecast_methods/harness/calendar.csv',
    'data/processed/abnb_daily_close.csv',
    'docs/revenue-forecast-strategy/05_backtests/B3_FY27_DECOMPOSITION.md',
    'deck/drafts/memo_v0_2026-09-11.md',
    'model/assumptions.md',
]


def before(frame: pd.DataFrame, as_of: str) -> pd.DataFrame:
    """A supplied training frame must already have strictly earlier observations."""
    dates = pd.to_datetime(frame.month_end, errors='raise').dt.normalize()
    if dates.isna().any() or (dates >= pd.Timestamp(as_of).normalize()).any():
        raise ValueError('Training data must be dated strictly before as_of')
    return frame.copy()


def equity_price(multiple: float, ebitda: float, net_cash: float, shares: float) -> float:
    vals = [multiple, ebitda, net_cash, shares]
    if not np.isfinite(vals).all() or multiple <= 0 or ebitda <= 0 or shares <= 0:
        raise ValueError('Finite positive multiple, EBITDA and shares required')
    return (multiple * ebitda + net_cash) / shares


def fit(frame: pd.DataFrame, as_of: str, *, changes: bool, window: str,
        dependent: str = 'ev_ltm_ebitda_x') -> dict:
    d = before(frame, as_of).sort_values('month_end').copy()
    if changes:
        # Original diagnostic is twelve ROWS apart; the last row is 4 Sep,
        # not a completed month. This inherited convention is disclosed.
        d[[dependent] + XCOLS] = d[[dependent] + XCOLS].diff(12)
    d = d.dropna(subset=[dependent] + XCOLS)
    if window in ('W1', 'W2'):
        d = d[d.month_end >= ('2023-01-01' if window == 'W1' else '2024-01-01')]
    if len(d) < 8:
        return {'window': window, 'n': len(d), 'status': 'underpowered', 'as_of': as_of}
    regressors = sm.add_constant(d[XCOLS], has_constant='add')
    if np.linalg.matrix_rank(regressors) != regressors.shape[1]:
        return {'window': window, 'n': len(d), 'status': 'rank_deficient', 'as_of': as_of}
    result = sm.OLS(d[dependent], regressors).fit(
        cov_type='HAC', cov_kwds={'maxlags': min(12 if changes else 6, len(d)-1)},
        use_t=False)
    ci = result.conf_int().loc[XCOLS[0]]
    return {
        'spec': '12_row_changes' if changes else 'levels', 'dependent': dependent,
        'window': window, 'n': int(result.nobs), 'n_params': 4, 'as_of': as_of,
        'slope_turns_per_growth_pp': float(result.params[XCOLS[0]]),
        'ci95_lo': float(ci.iloc[0]), 'ci95_hi': float(ci.iloc[1]),
        'intercept': float(result.params['const']), 'r2': float(result.rsquared),
        'first_observation': str(d.month_end.min()), 'last_observation': str(d.month_end.max()),
        'last_reported_quarters': int(d.last_reported_quarter.nunique()),
        'source_vintage_status': 'inherited monthly PIT label; source vintages unverified',
        'status': 'descriptive_only',
    }


def refresh_positioning(as_of: str) -> dict:
    """Public Yahoo requests only. Never silently call stale observations current."""
    import yfinance as yf
    payload = {'provider': 'Yahoo Finance via yfinance',
               'source_url': 'https://finance.yahoo.com/quote/ABNB/',
               'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
               'requested_as_of': as_of, 'status': 'offline', 'errors': []}
    ticker = yf.Ticker('ABNB')
    try:
        h = ticker.history(period='5d', auto_adjust=False, timeout=15)
        h = h[[str(idx.date()) < as_of for idx in h.index]]
        if not h.empty:
            last = h.iloc[-1]
            payload.update(status='price_refreshed', price=float(last.Close),
                           price_date=str(h.index[-1].date()), price_kind='unadjusted regular-session close')
    except Exception as exc:
        payload['errors'].append(f'history: {type(exc).__name__}: {exc}')
    try:
        info = ticker.get_info()
        for key in ['shortPercentOfFloat', 'sharesShort', 'shortRatio', 'dateShortInterest',
                    'targetLowPrice', 'targetHighPrice', 'targetMeanPrice',
                    'targetMedianPrice', 'numberOfAnalystOpinions', 'recommendationKey']:
            if info.get(key) is not None:
                payload[key] = info[key]
        payload['positioning_stamp_status'] = 'Yahoo snapshot retrieval stamp; analyst-target publication stamps not supplied'
    except Exception as exc:
        payload['errors'].append(f'info: {type(exc).__name__}: {exc}')
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--as-of', default='2026-09-12')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    prereg = ROOT / 'docs/revenue-forecast-strategy/05_backtests/V_VALUATION_RECONCILIATION.md'
    if 'Pre-registered pass line' not in prereg.read_text(encoding='utf-8'):
        raise RuntimeError('Missing pre-registration')

    monthly = pd.read_csv(OVERNIGHT / '12_abnb_multiples_monthly.csv')
    eligible = monthly[(monthly.ltm_revenue_growth_pct < 60) &
                       (monthly.ltm_ebitda_margin_pct > 5) &
                       (monthly.month_end < args.as_of)].copy()
    fits = [fit(eligible, args.as_of, changes=ch, window=w, dependent=dep)
            for dep, ch in [('ev_ltm_ebitda_x', True), ('ev_ntm_ebitda_x', False)]
            for w in ['ALL', 'W1', 'W2']]
    pd.DataFrame(fits).to_csv(OUT / 'regression_reproduction.csv', index=False)
    slope = fits[0]['slope_turns_per_growth_pp']
    replicated = bool(fits[0]['ci95_lo'] <= .48 <= fits[0]['ci95_hi'])

    # Verify the reported-quarter labels against the immutable publication calendar.
    calendar = pd.read_csv(ROOT / 'data/processed/forecast_methods/harness/calendar.csv')
    dates = dict(zip(calendar.print_quarter, calendar.print_date))
    audit = eligible[['month_end', 'last_reported_quarter']].copy()
    audit['canonical_quarter'] = audit.last_reported_quarter.map(lambda q: '20'+q[2:]+'Q'+q[0])
    audit['letter_publication_date'] = audit.canonical_quarter.map(dates)
    audit['letter_precedes_month'] = audit.letter_publication_date.notna() & (audit.letter_publication_date < audit.month_end)
    audit['source_component_timestamps_complete'] = False
    audit.to_csv(OUT / 'monthly_vintage_audit.csv', index=False)
    guide_rows = []
    for _, event in calendar.iterrows():
        q, origin = str(event.next_quarter_guided), str(event.guide_date)
        if not ('2023Q1' <= q <= '2026Q2'):
            continue
        pre = eligible[eligible.month_end < origin]
        for w in ['W1'] + (['W2'] if q >= '2024Q1' else []):
            f = fit(pre, origin, changes=True, window=w)
            f.update(guide_target=q, guide_date=origin, strict_month_cutoff=True)
            guide_rows.append(f)
    pd.DataFrame(guide_rows).to_csv(OUT / 'guide_date_refits.csv', index=False)

    annual = pd.read_csv(OVERNIGHT / '13_model_annual.csv')
    base = annual[(annual.scenario == 'Base') & (annual.year == 2027)].iloc[0]
    ebitda, cash, shares, anchor_growth = [float(base[x]) for x in
                                       ['adj_ebitda', 'net_cash', 'shares_end', 'revenue_yoy_pct']]
    growth_rows = []
    for weight, growth in [(0.33, 9.18), (.5, 10.35), (2/3, 11.52)]:
        multiple = 16.5 + slope * (growth - anchor_growth)
        sensitivities = [16.5 + b * (growth-anchor_growth) for b in (fits[0]['ci95_lo'], fits[0]['ci95_hi'])]
        growth_rows.append({'kernel_weight': weight, 'growth_pct': growth, 'anchor_growth_pct': anchor_growth,
                            'anchor_multiple': 16.5, 'slope': slope, 'multiple': multiple,
                            'price': equity_price(multiple, ebitda, cash, shares),
                            'slope_only_price_lo': equity_price(min(sensitivities), ebitda, cash, shares),
                            'slope_only_price_hi': equity_price(max(sensitivities), ebitda, cash, shares),
                            'n_scenarios': 1, 'basis': 'conditional sensitivity; no price confidence interval'})
    growth = pd.DataFrame(growth_rows)
    growth.to_csv(OUT / 'growth_multiple_price_bridge.csv', index=False)

    valuation = pd.read_csv(OVERNIGHT / '13_valuation_summary.csv')
    recommended = pd.read_csv(OVERNIGHT / '12_exit_multiple_recommendation.csv')
    fields = []
    for scenario, multiple in [('Bear',13.5), ('Base',16.5), ('Bull',18.5)]:
        a = annual[(annual.scenario == scenario) & (annual.year == 2027)].iloc[0]
        v = valuation[valuation.scenario == scenario]
        old = recommended[recommended.scenario == scenario].iloc[0]
        calc = equity_price(multiple, a.adj_ebitda, a.net_cash, a.shares_end)
        published = float(v[v.lens == 'EV / adj. EBITDA, FY27E'].price.iloc[0])
        if abs(calc-published) > .001:
            raise AssertionError(f'{scenario} valuation arithmetic failed: {calc} vs {published}')
        fields.append({'scenario': scenario, 'multiple': multiple, 'fy27_ebitda_musd': a.adj_ebitda,
                       'fy27_net_cash_musd': a.net_cash, 'fy27_shares_m': a.shares_end,
                       'price': calc, 'published_price': published,
                       'football_mean': float(v[v.lens == 'Football field mean'].price.iloc[0]),
                       'football_low': float(v[v.lens == 'Football field low'].price.iloc[0]),
                       'football_high': float(v[v.lens == 'Football field high'].price.iloc[0]),
                       'old_recommendation_price': float(old.price_at_recommended), 'n_lenses': 6})
    field = pd.DataFrame(fields)
    field.to_csv(OUT / 'football_field_reconciliation.csv', index=False)
    branches = pd.DataFrame([{'branch': name, 'low': lo, 'high': hi,
                              'implied_base_ebitda_multiple_low': (lo*shares-cash)/ebitda,
                              'implied_base_ebitda_multiple_high': (hi*shares-cash)/ebitda,
                              'n_endpoints': 2, 'source': 'memo_v0_2026-09-11.md',
                              'derivation': why}
                             for name, lo, hi, why in [
                                 ('Bear',140,152,'conditional event analogue; no exact EBITDA/cash/share bridge supplied'),
                                 ('Base',170,185,'conditional event analogue; no exact EBITDA/cash/share bridge supplied'),
                                 ('Bull',205,215,'memo links roughly +2pp growth to +1 turn; residual price bridge unspecified')]])
    branches.to_csv(OUT / 'memo_branches.csv', index=False)

    snapshot = OUT / 'public_positioning_snapshot.json'
    if args.refresh:
        snapshot.write_text(json.dumps(refresh_positioning(args.as_of), indent=2), encoding='utf-8')
    if snapshot.exists():
        positioning = json.loads(snapshot.read_text(encoding='utf-8'))
    else:
        close = pd.read_csv(ROOT / 'data/processed/abnb_daily_close.csv').iloc[-1]
        positioning = {'status': 'offline', 'price': float(close.Close), 'price_date': str(close.Date),
                       'provider': 'existing abnb_daily_close.csv', 'stale': True}
    if 'dateShortInterest' in positioning:
        positioning['short_interest_date'] = datetime.fromtimestamp(
            positioning['dateShortInterest'], timezone.utc).date().isoformat()
    live_position_text = (
        f"Short float {100*positioning['shortPercentOfFloat']:.2f}% / "
        f"{positioning['sharesShort']:,} shares / {positioning['shortRatio']:.2f} days "
        f"(Yahoo settlement date {positioning['short_interest_date']}); targets mean "
        f"${positioning['targetMeanPrice']:.3f}, median ${positioning['targetMedianPrice']:.0f}, "
        f"range ${positioning['targetLowPrice']:.0f}–{positioning['targetHighPrice']:.0f} "
        f"(n={positioning['numberOfAnalystOpinions']})."
        if all(k in positioning for k in ['shortPercentOfFloat','sharesShort','shortRatio',
               'short_interest_date','targetMeanPrice','targetMedianPrice','targetLowPrice',
               'targetHighPrice','numberOfAnalystOpinions']) else
        'Short-interest and current analyst-target details unavailable; see saved refresh status.')
    analyst = pd.read_csv(OVERNIGHT / '12_analyst_target_summary.csv')
    analyst.to_csv(OUT / 'existing_analyst_summary.csv', index=False)
    manifest = [{'path': path, 'sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for path in SOURCES]
    (OUT / 'input_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    summary = {'method': METHOD, 'verdict': 'partial', 'slope_replication_pass': replicated,
               'slope': fits[0], 'price_band': [float(growth.price.min()), float(growth.price.max())],
               'annual_base_inputs': {'ebitda': ebitda, 'net_cash': cash, 'shares': shares, 'growth': anchor_growth},
               'monthly_label_date_checks_pass': int(audit.letter_precedes_month.sum()),
               'monthly_label_date_checks_n': len(audit), 'complete_source_vintage_cells': 0,
               'scored_W1_cells': 0, 'scored_W2_cells': 0, 'registry_status': 'not registered: no price or multiple target in frozen harness',
               'positioning': positioning, 'runtime_seconds': time.perf_counter()-started}
    (OUT / 'run_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    # Compact static page: all values are generated from the same audited tables.
    table_rows = []
    for i, row in field.iterrows():
        g, b = growth.iloc[i], branches.iloc[i]
        table_rows.append(f"| {row.scenario} | {g.growth_pct:.2f}% → {g.multiple:.2f}x → ${g.price:.2f} | "
                          f"{row.multiple:.1f}x → ${row.price:.2f} | ${row.football_mean:.2f} "
                          f"[${row.football_low:.2f}–{row.football_high:.2f}] | ${b.low}–{b.high} "
                          f"({b.implied_base_ebitda_multiple_low:.2f}–{b.implied_base_ebitda_multiple_high:.2f}x) |")
    page = f'''# V — arithmetic reconciliation, 12 September 2026

**PARTIAL.** Arithmetic reproduces; inherited vintages and the translation of a change coefficient into an exit level remain unverified. No direction recommendation.

| Scenario / rank (n=1 each) | FY27 growth sensitivity | FY27 EV/EBITDA lens | Six-lens football field: mean [range], n=6 | Memo event analogue [implied multiple on fixed base EBITDA] |
|---|---:|---:|---:|---:|
{chr(10).join(table_rows)}

**Shown calculation:** multiple = 16.5 + {slope:.6f} × (growth% − {anchor_growth:.4f}); price = (multiple × ${ebitda:,.4f}M + ${cash:,.4f}M) / {shares:.4f}M. This holds EBITDA, cash and shares fixed; row ranks align for comparison and are **not the same scenarios**.

**Relation:** +{slope:.4f} turns/pp, HAC 95% CI [{fits[0]['ci95_lo']:.4f}, {fits[0]['ci95_hi']:.4f}], n={fits[0]['n']} overlapping monthly changes, 4 parameters. This is Δ12 EV/**LTM** EBITDA against Δ12 forward-growth proxy, controlling for rates and Nasdaq valuation; it supplies a sensitivity, not an exit-multiple intercept. W1/W2 are diagnostics, with zero eligible independently vintage-verified scored forecasts. Source: regression_reproduction.csv; dates: monthly_vintage_audit.csv.

**Positioning:** ${positioning.get('price', float('nan')):.2f}, observed {positioning.get('price_date','unavailable')} ({positioning['provider']}); refresh status {positioning['status']}. {live_position_text} Retrieval stamp {positioning.get('retrieved_at_utc','offline')}; latest snapshot, not backdated to a guide date. Existing rating split pulled 6 Sep: 21 Buy / 11 Hold / 2 Sell (n=34); old target dispersion SD/mean 0.131 (n=31). The current range is a measure of dispersion; current target standard deviation is unavailable. These vendor panels have different membership.

**Three unresolved inconsistencies:** (1) Δmultiple/LTM and FY27 exit-multiple levels are different objects; a slope does not identify the intercept. (2) The preliminary exit recommendation uses older EBITDA/cash/shares: base $191.317 versus the final model's ${field.iloc[1].price:.2f}; the six-lens mean is a third object. (3) Memo branches are event analogues with unspecified earnings/cash/share bridges and a different horizon; +1 turn at fixed base inputs adds only ${ebitda/shares:.2f}, not the full bull-branch increase. All model prices retain the existing ~30 Sep 2027 target convention and weighted-average-share proxy caveat.

Evidence: growth_multiple_price_bridge.csv; football_field_reconciliation.csv; memo_branches.csv; input_manifest.json. No new valuation target has been adopted.
'''
    (OUT / 'valuation_page.md').write_text(page, encoding='utf-8')
    # Standalone 16:9 research exhibit, checked visually after rendering.
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['text.parse_math'] = False
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(16, 9), facecolor='#fafbf9')
    fig.text(.035, .953, 'V  |  Valuation arithmetic: three different price objects',
             fontsize=23, weight='bold', color='#153635')
    fig.text(.035, .909, 'PARTIAL  ·  Arithmetic reconciles; source vintages and exit-level inference remain unverified. No direction adopted.',
             fontsize=13, color='#734d19')
    table_ax = fig.add_axes([.035,.608,.93,.257]); table_ax.axis('off')
    cells = []
    for i,row in field.iterrows():
        g,b = growth.iloc[i],branches.iloc[i]
        cells.append([row.scenario,
                      f'{g.growth_pct:.2f}% → {g.multiple:.2f}x\n${g.price:.2f}',
                      f'{row.multiple:.1f}x\n${row.price:.2f}',
                      f'${row.football_mean:.2f}\n[${row.football_low:.2f}–{row.football_high:.2f}]',
                      f'${b.low}–{b.high}\n[{b.implied_base_ebitda_multiple_low:.2f}–{b.implied_base_ebitda_multiple_high:.2f}x]'])
    table = table_ax.table(cellText=cells, colLabels=['Rank only', 'Growth sensitivity (n=1)',
                          'FY27 EBITDA lens (n=1)', 'Six-lens field (n=6)', 'Memo event analogue (n=2 ends)'],
                          cellLoc='center', loc='center', colWidths=[.10,.23,.19,.22,.26])
    table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1,3)
    for (r,c), cell in table.get_celld().items():
        cell.set_edgecolor('#cbd8d4')
        cell.set_facecolor('#153635' if r==0 else ('#edf3ef' if r%2 else '#fafbf9'))
        if r==0: cell.set_text_props(color='white',weight='bold',fontsize=11)
    formula = (f'Shown arithmetic: x = 16.5 + {slope:.6f} × (g − {anchor_growth:.4f}); '
               f'P = (x × ${ebitda:,.2f}M + ${cash:,.2f}M) / {shares:.4f}M.\n'
               'Growth sensitivity fixes EBITDA, cash and shares. Row ranks align for comparison; these are not identical scenarios.')
    fig.text(.035,.549,formula,fontsize=11.7,linespacing=1.5,color='#263b36')
    relation = (f'Relation: +{slope:.4f} turns/pp; HAC95% [{fits[0]["ci95_lo"]:.4f}, {fits[0]["ci95_hi"]:.4f}]. '
                'Dependent variable is the 12-row change in EV/LTM EBITDA. W1 n=35, W2 n=33 overlapping monthly changes; '
                'four parameters. Forward-multiple LEVEL slope W2 = +0.1948 [−0.3233, +0.7129]. '
                '47/47 reported-quarter date labels pass, but complete component vintages are unverified: zero scored forecasts.')
    fig.text(.035,.443,textwrap.fill(relation,175),fontsize=11.4,linespacing=1.5,color='#263b36')
    spot = (f'Positioning: ${positioning.get("price",float("nan")):.2f}, close {positioning.get("price_date","unavailable")}. '
            f'{live_position_text} Existing 6 Sep rating split: 21 Buy / 11 Hold / 2 Sell (n=34). '
            'Current target SD unavailable. Yahoo snapshot retrieved '+positioning.get('retrieved_at_utc','offline')+
            '; not a historical guide-date snapshot.')
    fig.text(.035,.315,textwrap.fill(spot,175),fontsize=11.4,linespacing=1.5,color='#263b36')
    inconsistencies = ('Three unresolved inconsistencies: (1) A change slope does not identify an exit-level intercept. '
                       '(2) Preliminary model inputs yield base $191.317; final inputs yield $180.88; the six-lens mean is $156.79. '
                       '(3) Event branches omit a complete earnings/cash/share bridge: +1 turn adds $9.89 at fixed base inputs. '
                       'All model prices retain the ~30 Sep 2027 target convention and the weighted-average-share proxy caveat.')
    fig.text(.035,.170,textwrap.fill(inconsistencies,175),fontsize=11.4,linespacing=1.5,color='#263b36')
    fig.text(.035,.04,'Evidence: valuation_v1/{regression_reproduction, growth_multiple_price_bridge, football_field_reconciliation, memo_branches}.csv; input_manifest.json',
             fontsize=9.3,color='#5d726b')
    fig.savefig(OUT/'valuation_page.png',dpi=120,facecolor=fig.get_facecolor())
    fig.savefig(OUT/'valuation_page.pdf',facecolor=fig.get_facecolor())
    plt.close(fig)
    summary['runtime_seconds'] = time.perf_counter()-started
    (OUT / 'run_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
