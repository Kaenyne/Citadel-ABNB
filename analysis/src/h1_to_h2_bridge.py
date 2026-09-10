"""H1 -> H2 bridge for ABNB: what Q1/Q2 typically imply for Q3/Q4, where the pattern broke, and why.

INTERPRETATION NOTICE: Original exploratory scenario code preserved for context.
See docs/RNPL_HANDOFF.md. The Q1 ~3-point lift was a three-product bundle, not
RNPL alone; the RNPL lap overlays below are assumptions, not fitted effects.
Outputs are not a validated cancellation forecast or live model revision.

Method
------
For each KPI (y/y growth or level), the H1->H2 *transition* in year Y is
    T3(Y) = KPI(Q3,Y) - mean(KPI(Q1,Y), KPI(Q2,Y))
    T4(Y) = KPI(Q4,Y) - mean(KPI(Q1,Y), KPI(Q2,Y))
Base rate = mean transition over the clean regime (2023-2025). 2022 is shown but excluded from the
base rate (H1 2022 y/y still carries Omicron/reopening base effects). 2021 is reopening and dropped.
The 2026 "pattern" projection is 2026 H1 mean + base-rate transition. Known 2026 step changes
(FX, RNPL lap, World Cup, seats dilution) are then overlaid as explicit adjustments.

Deviation = actual transition in year Y minus the mean transition of the other clean years
(leave-one-out), so each year is judged against the pattern the others set. Deviations above the
threshold are joined to a hand-coded event catalogue built from the shareholder letters.

Inputs: data/processed/overnight/02_kpi_panel_quarterly.csv, data/processed/adr/*.csv,
data/processed/abnb_revenue_guidance_vs_actual.csv, data/processed/overnight/04_current_consensus.csv,
FRED DTWEXBGS and DEXUSEU (fredgraph.csv exports; pass the directory as argv[1]).
Outputs: data/processed/h2_bridge/*.csv
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'data', 'processed', 'h2_bridge')
os.makedirs(OUT, exist_ok=True)
FX_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'data', 'raw', 'fred')

panel = pd.read_csv(os.path.join(ROOT, 'data/processed/overnight/02_kpi_panel_quarterly.csv'))
panel['year'] = panel.quarter.str[-2:].astype(int) + 2000
panel['q'] = panel.quarter.str[0].astype(int)

# party-size / listing-size term (global, pp of ADR y/y)
ps = pd.read_csv(os.path.join(ROOT, 'data/processed/adr/13_party_size_adr_quarterly.csv'))
ps = ps[ps.region == 'global'][['quarter', 'size_term_pp']]
panel = panel.merge(ps, on='quarter', how='left')

# unearned fees as % of next-quarter revenue (backlog cover)
panel['unearned_cover_next_q_pct'] = np.nan
for i in range(len(panel) - 1):
    panel.loc[i, 'unearned_cover_next_q_pct'] = 100 * panel.loc[i, 'unearned_fees_musd'] / panel.loc[i + 1, 'revenue_musd']

METRICS = {
    'nights_yoy_pct': 'Nights & seats y/y (%)',
    'adr_yoy_exfx_pct': 'ADR y/y ex-FX (%)',
    'fx_pts_adr': 'FX contribution to ADR y/y (pts)',
    'adr_yoy_reported_pct': 'ADR y/y reported (%)',
    'gbv_yoy_exfx_pct': 'GBV y/y ex-FX (%)',
    'gbv_yoy_reported_pct': 'GBV y/y reported (%)',
    'revenue_yoy_exfx_pct': 'Revenue y/y ex-FX (%)',
    'fx_pts_revenue': 'FX contribution to revenue y/y (pts)',
    'revenue_yoy_reported_pct': 'Revenue y/y reported (%)',
    'take_rate_pct': 'Implied take rate (level, %)',
    'nights_yoy_na_pct': 'NA nights y/y (%)',
    'nights_yoy_emea_pct': 'EMEA nights y/y (%)',
    'nights_yoy_latam_pct': 'LatAm nights y/y (%)',
    'nights_yoy_apac_pct': 'APAC nights y/y (%)',
    'adr_yoy_na_pct': 'NA ADR y/y (%)',
    'size_term_pp': 'Party-size / listing-size term in ADR (pts)',
    'unearned_fees_yoy_pct': 'Unearned fees y/y (%)',
    'unearned_cover_next_q_pct': 'Unearned fees / next-quarter revenue (%)',
    'adj_ebitda_margin_pct': 'Adj. EBITDA margin (level, %)',
}
CLEAN = [2023, 2024, 2025]
SHOW = [2022, 2023, 2024, 2025]

wide = panel.pivot(index='year', columns='q', values=list(METRICS))


def cell(y, m, q):
    try:
        return wide.loc[y, (m, q)]
    except KeyError:
        return np.nan


rows = []
for m in METRICS:
    for y in SHOW + [2026]:
        q1, q2, q3, q4 = (cell(y, m, q) for q in (1, 2, 3, 4))
        if pd.isna(q1) and pd.isna(q2):
            continue
        h1 = np.nanmean([q1, q2])
        rows.append(dict(metric=m, label=METRICS[m], year=y, q1=q1, q2=q2, h1_mean=h1, q3=q3, q4=q4,
                         t3=q3 - h1, t4=q4 - h1, q4_minus_q3=q4 - q3))
tr = pd.DataFrame(rows)
tr.to_csv(os.path.join(OUT, 'h2_bridge_transitions.csv'), index=False)

# base rates and leave-one-out deviations
base, devs = [], []
for m in METRICS:
    sub = tr[(tr.metric == m) & (tr.year.isin(CLEAN))].dropna(subset=['t3'])
    if sub.empty:
        continue
    r22 = tr[(tr.metric == m) & (tr.year == 2022)]
    base.append(dict(metric=m, label=METRICS[m], n_years=len(sub),
                     t3_mean=sub.t3.mean(), t3_min=sub.t3.min(), t3_max=sub.t3.max(), t3_sd=sub.t3.std(ddof=0),
                     t4_mean=sub.t4.mean(), t4_min=sub.t4.min(), t4_max=sub.t4.max(), t4_sd=sub.t4.std(ddof=0),
                     t3_2022=r22.t3.squeeze() if len(r22) else np.nan, t4_2022=r22.t4.squeeze() if len(r22) else np.nan))
    for y in SHOW:
        r = tr[(tr.metric == m) & (tr.year == y)]
        if r.empty or pd.isna(r.t3.squeeze()):
            continue
        others = tr[(tr.metric == m) & (tr.year.isin(CLEAN)) & (tr.year != y)]
        for k, col, qcol in (('3', 't3', 'q3'), ('4', 't4', 'q4')):
            exp, act = others[col].mean(), r[col].squeeze()
            if pd.isna(act) or pd.isna(exp):
                continue
            devs.append(dict(metric=m, label=METRICS[m], year=y, quarter=f'{k}Q{str(y)[-2:]}', h1_mean=r.h1_mean.squeeze(),
                             expected_transition=exp, actual_transition=act, deviation_pts=act - exp,
                             implied_by_pattern=r.h1_mean.squeeze() + exp, actual=r[qcol].squeeze()))
base = pd.DataFrame(base)
base.to_csv(os.path.join(OUT, 'h2_bridge_base_rates.csv'), index=False)
devs = pd.DataFrame(devs)


def thr(m):
    if m in ('take_rate_pct', 'fx_pts_adr', 'size_term_pp', 'adr_yoy_exfx_pct', 'adr_yoy_reported_pct', 'adr_yoy_na_pct'):
        return 1.0
    if m in ('adj_ebitda_margin_pct', 'fx_pts_revenue'):
        return 1.5
    if m == 'unearned_cover_next_q_pct':
        return 5.0
    return 2.0


devs['threshold_pts'] = devs.metric.map(thr)
devs['flag'] = devs.deviation_pts.abs() >= devs.threshold_pts

# ---- event catalogue (hand-coded from the shareholder letters, call study and catalyst calendar)
EV_COLS = ['quarter_hit', 'event', 'event_date', 'first_public_signal', 'metric', 'direction', 'size',
           'foreseeable', 'mgmt_flagged_before_quarter_end', 'source']
events = [
 ('3Q21', 'COVID Delta variant wave', '2021-07', '2021-06', 'nights', 'down', 'nights fell q/q 83.1M -> 79.7M', 'partly (variant known by June; flagged in 12 Aug letter)', 'yes', '2Q21 letter outlook'),
 ('4Q21', 'Omicron (December)', '2021-12', '2021-11-26', 'nights, cancellations', 'down', '"lower than Delta"; Dec gross nights still +40% y/y', 'no (emerged after the 4 Nov call)', 'no', '4Q21 letter'),
 ('1Q22', 'Russia invades Ukraine; Omicron in January', '2022-02-24', '2022-02-24', 'nights (EMEA), cancellations', 'down', '~600k solidarity nights booked in Ukraine ($20M GBV); January an easier comp', 'no (invasion after the 15 Feb letter)', 'no', '1Q22, 4Q22 letters'),
 ('3Q22', 'USD surge (DXY peak Sep 2022)', '2022-07..10', 'spot, continuous', 'FX pts revenue/ADR', 'down', '-7 pts revenue, -7.1 pts ADR', 'yes (spot FX; "significant headwind" in 2Q22 letter)', 'yes', '2Q22/3Q22 letters; panel'),
 ('4Q22', 'USD strength persists; Q4 nights guide cut to ~20% from 25%', '2022-11-01', '2022-11-01', 'nights guide, FX', 'down', '-7 pts FX on revenue; stock -13.4% on 2 Nov 2022', 'yes for FX; the nights-guide cut was not public before the call', 'n/a', 'major-moves note'),
 ('2Q23', 'Lapping Omicron pent-up demand of 1H22', '2023-04..06', '2023-05-09', 'nights y/y', 'down', 'nights y/y 18.6% -> 11.0% (accel -7.6)', 'yes (pre-flagged in 1Q23 letter); stock still -10.9% on 10 May 2023', 'yes', '1Q23 letter outlook'),
 ('3Q23', 'NYC Local Law 18 in force (5 Sep 2023)', '2023-09-05', '2023-01 (law dated)', 'supply, NA nights', 'down', 'NYC ~1% of revenue; no visible KPI break', 'yes (dated law, months of notice)', 'yes', '3Q23/4Q23 letters'),
 ('3Q23', 'Israel-Gaza war (7 Oct, after quarter end)', '2023-10-07', '2023-10-07', 'cancellations, Q4 nights', 'down', '"greater volatility... geopolitical" on 1 Nov call; 4Q23 nights +12% anyway', 'no', 'n/a', 'Theo driver_observations 2023Q3'),
 ('1Q24', 'Easter in Q1 (31 Mar) plus Leap Day', '2024-03-31', 'calendar', 'revenue y/y, take rate', 'up', '+1 to +2 pts revenue (Easter) plus Leap Day; reversed in 2Q24', 'yes (calendar; pre-announced in 4Q23 letter)', 'yes', '4Q23/1Q24 letters'),
 ('2Q24', 'Shorter lead times and softer US demand (7 Aug 2024 call)', '2024-07..08', '2024-08-07', 'nights guide (Q3 "moderate")', 'down', 'stock -13.4%; nights y/y 8.7% -> 8.5% in Q3 (barely moved)', 'no (lead time is internal data)', 'n/a', '2Q24 letter; major-moves'),
 ('3Q24', 'Paris Summer Olympics (26 Jul-11 Aug)', '2024-07-26', '2023-11 (backlog 2x flagged)', 'EMEA nights, Paris supply', 'up', '~700k guests over the Games; EMEA "slight acceleration"; Paris supply +35%', 'yes (dated; backlog flagged in 4Q23 letter)', 'yes', '3Q24 letter'),
 ('3Q24', 'Hurricanes Helene (26 Sep) and Milton (9 Oct)', '2024-09-26', '2024-09-24', 'NA cancellations', 'down', 'not quantified; Airbnb.org disaster housing', 'partly (days of notice; season is dated)', 'no', '3Q24 letter'),
 ('4Q24', 'US election week (5 Nov) softness, then nights accelerate to +12%', '2024-11-05', 'calendar', 'NA nights', 'mixed', '4Q24 nights +12.3% vs pattern-implied ~8%: largest positive H2 deviation in the sample', 'partly (election dated; the strength was not foreseeable)', 'n/a', '3Q24 letter outlook; panel'),
 ('1Q25', 'Easter/Leap-Day lap (-3 pts revenue), FX -2, LA fires (Jan), tariff shock (2 Apr, after quarter end)', '2025-01..04', 'calendar / 2025-04-02', 'revenue y/y, NA nights', 'down', 'revenue +6% reported, +11% ex-calendar/FX; NA nights +2%', 'yes for calendar and FX; no for tariffs', 'yes (calendar)', '4Q24/1Q25 letters'),
 ('2Q25', 'Israel-Iran strikes (13-24 Jun); "H2 nights to moderate" guide', '2025-06-13', '2025-06-13', 'nights guide', 'down', 'stock -8.0% on 7 Aug 2025; nights 7.4% -> 8.8% in Q3 (accelerated instead)', 'no', 'n/a', 'major-moves; panel'),
 ('3Q25', 'Paris Olympics lap in EMEA; RNPL launch lengthens NA lead times', '2025-07..09', '2025-05 (RNPL launch)', 'EMEA nights, lead times, unearned fees', 'mixed', 'EMEA "slightly unfavorable comp"; NA nights mid-single digit, accelerating', 'yes (lap dated; RNPL launch public)', 'yes', '3Q25 letter'),
 ('4Q25', 'US federal shutdown (1 Oct-12 Nov 2025) and FAA flight cuts; new cancellation policies (Oct)', '2025-10-01', '2025-09-30', 'NA nights, cancellations', 'mixed', '4Q25 nights +9.8% (accel +1.0): no visible hit', 'yes (deadline dated) but no KPI effect', 'no', '4Q25 letter; panel'),
 ('1Q26', 'Middle East conflict: cancellations in EMEA and APAC', '2026-01..03', '2026-02 (press)', 'nights y/y', 'down', '-1 pt (mgmt: ~10% ex-conflict vs 9% reported)', 'partly (conflict public; cancellation size not)', 'yes (in letter)', '1Q26 letter'),
 ('1Q26', 'Milan-Cortina Winter Olympics (6-22 Feb)', '2026-02-06', 'dated', 'EMEA nights, Milan supply', 'up', '~200k guests; Milan supply +30%', 'yes (dated)', 'yes', '1Q26 letter'),
 ('1Q26', 'USD weakness: FX +5 pts on ADR, +3 on revenue', '2026-01..03', 'spot, continuous', 'FX pts', 'up', '+5.0 ADR, +3 revenue', 'yes (spot FX)', 'yes', '1Q26 letter'),
 ('2Q26', 'FIFA World Cup (11 Jun-19 Jul), 16 host cities, 150k new listings', '2026-06-11', '2025-10 (host outreach)', 'nights, supply, first-time bookers', 'up', 'not quantified; "helped" the Q3 nights guide; 3Q27 becomes an unfavorable comp', 'yes (dated)', 'yes', '2Q26 letter; call study'),
 ('3Q26', 'RNPL US anniversary: ~3 pts of 1Q26 nights growth was RNPL; US laps from Q3, global from 1Q27', '2026-07', '2026-05 (1Q26 letter)', 'nights y/y', 'down', 'up to -3 pts if the whole RNPL lift laps; -1 to -2 if adoption is still rising', 'yes (mgmt dated it)', 'yes', '1Q26 letter outlook; call study'),
 ('3Q26', 'FX tailwind fades: ADR FX fitted from FRED (see h2_bridge_fx.csv); revenue FX lags one to two quarters (~3 pts Q3, ~1 pt Q4)', '2026-07..12', 'spot, continuous', 'FX pts ADR/revenue', 'down (less tailwind)', 'see h2_bridge_fx.csv', 'yes (spot FX; hedging program)', 'yes (Q3 revenue ~3 pts)', 'this script'),
 ('3Q26', 'EU Affordable Housing Act draft (9 Sep 2026): city STR caps', '2026-09-09', '2026-09-04', 'headline/supply', 'down', 'no regulatory event has produced a >=7% move (0 of 41)', 'yes (dated)', 'no', 'catalyst calendar'),
 ('3Q26', 'Host-fee 6-10% pilot for host-sourced bookings (Aug 2026)', '2026-08-31', '2026-08-29', 'take rate', 'down', 'first explicit take-rate cut; size undisclosed', 'yes (public pilot)', 'no', 'pitch landscape'),
 ('4Q26', 'Atlantic hurricane season peak (Sep-Oct); 2024 analogue Helene/Milton', '2026-09..10', 'seasonal', 'NA cancellations', 'down', '2024: no visible KPI break', 'partly (season dated, storms not)', 'n/a', '3Q24 letter'),
 ('4Q26', 'US midterm elections (3 Nov, two days before the print); FY27 appropriations deadline 30 Sep (shutdown risk; 2025 precedent 43 days)', '2026-11-03', 'calendar', 'NA nights (election week), air travel', 'down (small)', '2024 election week softness; 2025 shutdown left no KPI mark', 'yes (dated)', 'n/a', '4Q24 and 4Q25 letters; 2026 shutdown status unverified'),
 ('4Q26', 'Middle East / Strait of Hormuz: air capacity and oil; BKNG and EXPE flagged cross-border pressure in Q2', '2026 ongoing', 'continuous', 'cross-border nights, cancellations', 'down', '1Q26: -1 pt; later quarters not quantified', 'partly', 'yes (1Q26)', '1Q26 letter; catalyst calendar'),
]
ev = pd.DataFrame(events, columns=EV_COLS)
ev.to_csv(os.path.join(OUT, 'h2_event_catalogue.csv'), index=False)
ev_by_q = ev.groupby('quarter_hit').event.apply(lambda s: ' | '.join(s)).to_dict()
devs['events_in_quarter'] = devs.quarter.map(ev_by_q).fillna('')
devs.sort_values(['metric', 'year']).to_csv(os.path.join(OUT, 'h2_bridge_deviations.csv'), index=False)


# ---- FX: quarter-average broad USD y/y -> FX pts on ADR (fitted 0.5 - 0.72 x USD y/y, predictive note 03)
def load_fred(name):
    d = pd.read_csv(os.path.join(FX_DIR, name + '.csv'), na_values='.')
    d.columns = ['date', 'v']
    d['date'] = pd.to_datetime(d.date)
    return d.dropna().set_index('date').v


usd, eur = load_fred('DTWEXBGS'), load_fred('DEXUSEU')
last = usd.index.max()
QTRS = {'1Q26': ('2026-01-01', '2026-03-31'), '2Q26': ('2026-04-01', '2026-06-30'),
        '3Q26': ('2026-07-01', '2026-09-30'), '4Q26': ('2026-10-01', '2026-12-31')}


def qavg(series, s, e):
    obs = series[s:min(e, last)]
    n_fill = len(pd.bdate_range(last + pd.Timedelta(days=1), e)) if e > last else 0
    vals = list(obs.values) + [series.iloc[-1]] * n_fill  # flat-spot fill for the unobserved remainder
    return float(np.mean(vals)), len(obs), n_fill


pq = panel.set_index('quarter')
fxrows = []
for lab, (s, e) in QTRS.items():
    s, e = pd.Timestamp(s), pd.Timestamp(e)
    u, n_obs, n_fill = qavg(usd, s, e)
    u_ly = usd[s - pd.DateOffset(years=1):e - pd.DateOffset(years=1)].mean()
    eu, _, _ = qavg(eur, s, e)
    eu_ly = eur[s - pd.DateOffset(years=1):e - pd.DateOffset(years=1)].mean()
    usd_yoy, eur_yoy = 100 * (u / u_ly - 1), 100 * (eu / eu_ly - 1)
    fxrows.append(dict(quarter=lab, usd_broad_avg=u, usd_broad_yoy_pct=usd_yoy, eurusd_avg=eu, eurusd_yoy_pct=eur_yoy,
                       obs_days=n_obs, filled_days_flat=n_fill, fx_pts_adr_fitted=0.5 - 0.72 * usd_yoy,
                       fx_pts_adr_disclosed=pq.fx_pts_adr.get(lab, np.nan)))
fx = pd.DataFrame(fxrows)
fx.to_csv(os.path.join(OUT, 'h2_bridge_fx.csv'), index=False)
fxq = fx.set_index('quarter')

# ---- 2026 projection: pattern + overlays
h26 = tr[tr.year == 2026].set_index('metric')
b = base.set_index('metric')
PROJ_METRICS = ['nights_yoy_pct', 'adr_yoy_exfx_pct', 'fx_pts_adr', 'adr_yoy_reported_pct', 'gbv_yoy_reported_pct',
                'revenue_yoy_exfx_pct', 'fx_pts_revenue', 'revenue_yoy_reported_pct', 'take_rate_pct',
                'nights_yoy_na_pct', 'nights_yoy_emea_pct', 'nights_yoy_latam_pct', 'nights_yoy_apac_pct', 'adj_ebitda_margin_pct']
proj = []
for m in PROJ_METRICS:
    if m not in h26.index or m not in b.index:
        continue
    h1 = h26.loc[m, 'h1_mean']
    proj.append(dict(metric=m, label=METRICS[m], h1_2026=h1, q1_2026=h26.loc[m, 'q1'], q2_2026=h26.loc[m, 'q2'],
                     q3_pattern=h1 + b.loc[m, 't3_mean'], q3_low=h1 + b.loc[m, 't3_min'], q3_high=h1 + b.loc[m, 't3_max'],
                     q4_pattern=h1 + b.loc[m, 't4_mean'], q4_low=h1 + b.loc[m, 't4_min'], q4_high=h1 + b.loc[m, 't4_max']))
proj = pd.DataFrame(proj).set_index('metric')
# take rate: the fee structure changed in 2025 (single fee, cross-currency fee, RNPL timing), so use the 2025 transition only
t25 = tr[(tr.metric == 'take_rate_pct') & (tr.year == 2025)].iloc[0]
proj.loc['take_rate_pct', ['q3_pattern', 'q3_low', 'q3_high']] = proj.loc['take_rate_pct', 'h1_2026'] + t25.t3
proj.loc['take_rate_pct', ['q4_pattern', 'q4_low', 'q4_high']] = proj.loc['take_rate_pct', 'h1_2026'] + t25.t4

seats = pd.read_csv(os.path.join(ROOT, 'data/processed/adr/15_seats_dilution_quarterly.csv'))
seats_mid = seats.groupby('quarter').dilution_drag_pp.mean()  # mean across the 3x3 business/ADR cases
fx3, fx4 = fxq.loc['3Q26', 'fx_pts_adr_fitted'], fxq.loc['4Q26', 'fx_pts_adr_fitted']
rev_fx4 = (2 / 3) * fx3 + (1 / 3) * pq.loc['2Q26', 'fx_pts_adr']  # revenue recognises at check-in: lag ADR FX

overlays = [
    ('nights_yoy_pct', '3Q26', 'RNPL US lap (mgmt: ~3 pts of 1Q26 growth); half assumed to lap in Q3', -1.5),
    ('nights_yoy_pct', '4Q26', 'RNPL US lap, fuller', -2.5),
    ('nights_yoy_pct', '3Q26', 'World Cup residual (July stays booked in-quarter); Paris 2024 analogue', 0.5),
    ('nights_yoy_pct', '3Q26', 'Middle East cancellation drag (was -1 in 1Q26, not cited in 2Q26): assumed faded', 0.0),
    ('fx_pts_adr', '3Q26', f'replace pattern with FRED-fitted quarter average (flat spot after {last.date()})', fx3 - proj.loc['fx_pts_adr', 'q3_pattern']),
    ('fx_pts_adr', '4Q26', f'replace pattern with FRED-fitted quarter average (flat spot after {last.date()})', fx4 - proj.loc['fx_pts_adr', 'q4_pattern']),
    ('adr_yoy_exfx_pct', '3Q26', 'seats/hotel dilution (15_seats_dilution, mean of cases)', float(seats_mid.get('3Q26', -0.5))),
    ('adr_yoy_exfx_pct', '4Q26', 'seats/hotel dilution (15_seats_dilution, mean of cases)', float(seats_mid.get('4Q26', -0.5))),
    ('fx_pts_revenue', '3Q26', 'management: ~3 pts FX in the Q3 revenue guide (hedged); revenue FX lags ADR FX by 1-2 quarters', 3.0 - proj.loc['fx_pts_revenue', 'q3_pattern']),
    ('fx_pts_revenue', '4Q26', 'assumed 2.0 (range 1-3): revenue FX is hedged and lags ADR FX irregularly (rev FX 3Q25 0, 4Q25 1, 1Q26 3, 2Q26 4 vs ADR FX 2.7, 2.9, 5.0, 1.3); flat spot implies fade from ~3', 2.0 - proj.loc['fx_pts_revenue', 'q4_pattern']),
]
ov = pd.DataFrame(overlays, columns=['metric', 'quarter', 'adjustment', 'pts'])
ov.to_csv(os.path.join(OUT, 'h2_bridge_overlays.csv'), index=False)

proj['q3_adjusted'] = proj.q3_pattern + ov[ov.quarter == '3Q26'].groupby('metric').pts.sum().reindex(proj.index).fillna(0)
proj['q4_adjusted'] = proj.q4_pattern + ov[ov.quarter == '4Q26'].groupby('metric').pts.sum().reindex(proj.index).fillna(0)
for q in ('q3', 'q4'):
    a = f'{q}_adjusted'
    proj.loc['adr_yoy_reported_pct', a] = proj.loc['adr_yoy_exfx_pct', a] + proj.loc['fx_pts_adr', a]
    proj.loc['gbv_yoy_reported_pct', a] = (1 + proj.loc['nights_yoy_pct', a] / 100) * (1 + proj.loc['adr_yoy_reported_pct', a] / 100) * 100 - 100
    proj.loc['revenue_yoy_reported_pct', a] = proj.loc['revenue_yoy_exfx_pct', a] + proj.loc['fx_pts_revenue', a]

guide = {'nights_yoy_pct': ('low double digits', 10.0, 12.0), 'gbv_yoy_reported_pct': ('mid teens', 14.0, 16.0),
         'revenue_yoy_reported_pct': ('15-17% incl ~3 pts FX', 15.0, 17.0), 'fx_pts_revenue': ('~3', 3.0, 3.0),
         'take_rate_pct': ('in line y/y (3Q25 17.9)', 17.9, 17.9), 'adj_ebitda_margin_pct': ('down slightly vs 50.1', 48.5, 49.9)}
proj['q3_guide_text'] = [guide.get(m, ('', np.nan, np.nan))[0] for m in proj.index]
proj['q3_guide_low'] = [guide.get(m, ('', np.nan, np.nan))[1] for m in proj.index]
proj['q3_guide_high'] = [guide.get(m, ('', np.nan, np.nan))[2] for m in proj.index]
proj.reset_index().to_csv(os.path.join(OUT, 'h2_bridge_2026_projection.csv'), index=False)

# ---- nights scenarios: the RNPL lap is the one overlay with a wide range, so show it explicitly
n_h1 = proj.loc['nights_yoy_pct', 'h1_2026']
adr3 = proj.loc['adr_yoy_reported_pct', 'q3_adjusted']
adr4 = proj.loc['adr_yoy_reported_pct', 'q4_adjusted']
scen = []
for name, lap3, lap4 in (('no lap (international RNPL adoption offsets the US anniversary)', 0.0, 0.0),
                         ('half lap', -1.5, -2.5), ('full lap (all ~3 pts of 1Q26 RNPL lift laps)', -3.0, -3.0)):
    n3 = n_h1 + b.loc['nights_yoy_pct', 't3_mean'] + lap3 + 0.5
    n4 = n_h1 + b.loc['nights_yoy_pct', 't4_mean'] + lap4
    scen.append(dict(scenario=name, rnpl_lap_q3_pts=lap3, rnpl_lap_q4_pts=lap4, nights_q3=n3, nights_q4=n4,
                     gbv_q3=(1 + n3 / 100) * (1 + adr3 / 100) * 100 - 100, gbv_q4=(1 + n4 / 100) * (1 + adr4 / 100) * 100 - 100,
                     q3_vs_guide='inside 10-12' if 10 <= n3 <= 12 else ('below' if n3 < 10 else 'above'),
                     q3_accel_vs_2q26=n3 - pq.loc['2Q26', 'nights_yoy_pct'], q4_accel_vs_q3=n4 - n3))
scen = pd.DataFrame(scen)
scen.to_csv(os.path.join(OUT, 'h2_bridge_nights_scenarios.csv'), index=False)

# ---- revenue dollars via GBV lag (call study: ~2/3 prior-quarter GBV + 1/3 two-quarters-back), quarter-specific conversion
order = list(pq.index)


def lagged_gbv(q):
    i = order.index(q)
    return (2 / 3) * pq.gbv_busd.iloc[i - 1] + (1 / 3) * pq.gbv_busd.iloc[i - 2]


conv = {q: pq.revenue_musd[q] / (1000 * lagged_gbv(q)) for q in ['3Q23', '3Q24', '3Q25', '4Q23', '4Q24', '4Q25']}
c3s = [conv['3Q23'], conv['3Q24'], conv['3Q25']]
c4s = [conv['4Q23'], conv['4Q24'], conv['4Q25']]
lag3 = (2 / 3) * pq.gbv_busd['2Q26'] + (1 / 3) * pq.gbv_busd['1Q26']
gbv3 = pq.gbv_busd['3Q25'] * (1 + proj.loc['gbv_yoy_reported_pct', 'q3_adjusted'] / 100)
lag4 = (2 / 3) * gbv3 + (1 / 3) * pq.gbv_busd['2Q26']
gva = pd.read_csv(os.path.join(ROOT, 'data/processed/abnb_revenue_guidance_vs_actual.csv')).dropna(subset=['actual_vs_mid_pct'])
gva['q'] = gva.guided_quarter.str[-1]
cush_q3, cush_q4 = gva[gva.q == '3'].actual_vs_mid_pct.mean(), gva[gva.q == '4'].actual_vs_mid_pct.mean()
cons = pd.read_csv(os.path.join(ROOT, 'data/processed/overnight/04_current_consensus.csv'))
cons_q3 = cons[(cons.period == '2026Q3') & (cons.metric == 'revenue')].value.iloc[0]
cons_q4 = cons[(cons.period == '2026Q4') & (cons.metric == 'revenue')].value.iloc[0]
revtab = pd.DataFrame([
    dict(quarter='3Q26', lagged_gbv_busd=lag3, conversion_mean=np.mean(c3s), conversion_min=min(c3s), conversion_max=max(c3s),
         revenue_musd=1000 * lag3 * np.mean(c3s), revenue_low=1000 * lag3 * min(c3s), revenue_high=1000 * lag3 * max(c3s),
         yoy_pct=100 * (lag3 * np.mean(c3s) * 1000 / pq.revenue_musd['3Q25'] - 1), guide_low=4690, guide_high=4770, consensus=cons_q3,
         hist_actual_vs_guide_mid_pct=cush_q3, implied_guide_mid_if_cushion_holds=np.nan, gbv_3q26_assumed_busd=np.nan),
    dict(quarter='4Q26', lagged_gbv_busd=lag4, conversion_mean=np.mean(c4s), conversion_min=min(c4s), conversion_max=max(c4s),
         revenue_musd=1000 * lag4 * np.mean(c4s), revenue_low=1000 * lag4 * min(c4s), revenue_high=1000 * lag4 * max(c4s),
         yoy_pct=100 * (lag4 * np.mean(c4s) * 1000 / pq.revenue_musd['4Q25'] - 1), guide_low=np.nan, guide_high=np.nan, consensus=cons_q4,
         hist_actual_vs_guide_mid_pct=cush_q4, implied_guide_mid_if_cushion_holds=1000 * lag4 * np.mean(c4s) / (1 + cush_q4 / 100), gbv_3q26_assumed_busd=gbv3),
])
revtab.to_csv(os.path.join(OUT, 'h2_bridge_revenue_dollars.csv'), index=False)
pd.DataFrame([dict(quarter=k, conversion=v) for k, v in conv.items()]).to_csv(os.path.join(OUT, 'h2_bridge_gbv_lag_conversion.csv'), index=False)

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
KEY = ['nights_yoy_pct', 'adr_yoy_exfx_pct', 'fx_pts_adr', 'revenue_yoy_exfx_pct', 'fx_pts_revenue', 'take_rate_pct',
       'adj_ebitda_margin_pct', 'nights_yoy_na_pct', 'nights_yoy_emea_pct', 'unearned_cover_next_q_pct']
print('=== TRANSITIONS')
print(tr[tr.metric.isin(KEY)].to_string(index=False))
print('\n=== BASE RATES')
print(base.to_string(index=False))
print('\n=== FLAGGED DEVIATIONS')
print(devs[devs.flag].sort_values(['year', 'metric'])[['quarter', 'label', 'h1_mean', 'implied_by_pattern', 'actual', 'deviation_pts', 'events_in_quarter']].to_string(index=False))
print('\n=== FX')
print(fx.to_string(index=False))
print('\n=== OVERLAYS')
print(ov.to_string(index=False))
print('\n=== 2026 PROJECTION')
print(proj.reset_index()[['label', 'q1_2026', 'q2_2026', 'q3_pattern', 'q3_low', 'q3_high', 'q3_adjusted', 'q3_guide_text', 'q4_pattern', 'q4_low', 'q4_high', 'q4_adjusted']].to_string(index=False))
print('\n=== REVENUE DOLLARS')
print(revtab.to_string(index=False))
print({k: round(v, 4) for k, v in conv.items()})
