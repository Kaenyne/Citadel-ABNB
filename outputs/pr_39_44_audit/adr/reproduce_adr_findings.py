"""Read-only reproductions from PR44 head 573b377 and inherited PR41 H outputs.
Run with any Python containing pandas and numpy; writes only audit_evidence.json.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
SRC = OUT / 'source'
results = {}
H = pd.read_csv(SRC / 'data/processed/q3nowcast/H/adr_history_components.csv').set_index('quarter')
bt = pd.read_csv(OUT / 'adr_exfx_backtest.csv').set_index('quarter')
y = H.adr_exfx_yoy_pp
predictions = []
for q in bt.index:
    history = y.iloc[:list(y.index).index(q)].to_numpy()
    slope, intercept = np.polyfit(history[:-1], history[1:], 1)
    predictions.append(intercept + slope*history[-1])
old_rmse = float(np.sqrt(np.mean((bt.ar1_pp-bt.actual_exfx_pp)**2)))
new_rmse = float(np.sqrt(np.mean((np.array(predictions)-bt.actual_exfx_pp)**2)))
results['H_AR1_future_fit'] = {'n':len(bt), 'full_history_rmse_pp':old_rmse, 'expanding_rmse_pp':new_rmse,
    'full_history_predictions':bt.ar1_pp.to_dict(), 'expanding_predictions':dict(zip(bt.index,predictions))}
terms = pd.read_csv(SRC / 'data/processed/adrq3/J/J3_card_v2_terms.csv')
cards = pd.read_csv(SRC / 'data/processed/adrq3/J/adr_card_v2.csv')
results['J3_asymmetric_band'] = {}
for q in ['3Q26','4Q26']:
    t = terms[(terms.quarter==q)&terms.in_point]
    c = cards[(cards.quarter==q)&(cards.fx_estimator=='midpoint')].iloc[0]
    residual = t[t.term=='like_for_like_pricing_residual'].iloc[0]
    mean_reversion_only_pp = float(c.adr_reported_yoy_pp+residual.lo_pp-residual.point_pp)
    half_reported = float(np.sqrt(np.sum(((t.hi_pp-t.lo_pp)/2)**2)))
    rss_down = float(np.sqrt(np.sum((t.point_pp-t.lo_pp)**2)))
    rss_up = float(np.sqrt(np.sum((t.hi_pp-t.point_pp)**2)))
    results['J3_asymmetric_band'][q] = {'reported_point_pp':float(c.adr_reported_yoy_pp),
       'advertised_central_lo_pp':float(c.adr_reported_central_lo_pp),'advertised_central_hi_pp':float(c.adr_reported_central_hi_pp),
       'reported_half_range':half_reported,'rss_distance_down':rss_down,'rss_distance_up':rss_up,
       'mean_reversion_only_pp':mean_reversion_only_pp,
       'mean_reversion_only_adr_usd':float(c.base_adr_usd*(1+mean_reversion_only_pp/100)),
       'mean_reversion_only_gbv_change_musd':float(c.base_adr_usd*c.nights_baseline_m*(residual.lo_pp-residual.point_pp)/100)}
cal = pd.read_csv(SRC / 'data/processed/adrq3/J/calendar_price_yoy.csv')
results['calendar_matched_prices_move'] = cal[(cal.snapshot1_quarter=='2Q25')&(cal.group_type=='lead')&(cal.group=='0-90')&(cal.regime=='all')&(cal.region.isin(['na','emea']))][['region','median_yoy_pct','trimmed_mean_yoy_pct','mean_ratio_yoy_pct']].to_dict('records')
rev = pd.read_csv(SRC / 'data/processed/adrq3/J/J1_lead_revision.csv')
rev = rev[rev.regime=='all'].copy()
rev['share_changed'] = rev.share_cut+rev.share_raised
results['calendar_lead_revision'] = {'weighted_share_changed':float(np.average(rev.share_changed,weights=rev.n)),
    'min_share_changed':float(rev.share_changed.min()),'max_share_changed':float(rev.share_changed.max())}
pairs = pd.read_csv(SRC / 'data/processed/adrq3/I/I2_los_pairs.csv')
results['LOS_calendar_windows_not_lead_matched'] = {'pairs':len(pairs),'exact_364_day_gap_pairs':int((pairs.gap_days==364).sum()),
    'max_lead_difference_days':int((pairs.gap_days-364).abs().max()),'gap_days_distribution':pairs.gap_days.value_counts().sort_index().to_dict()}
(OUT/'audit_evidence.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
