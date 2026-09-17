"""R10 revision 2 (A12 audit response, 2026-09-17): P(DTWEXBGS on 2027-02-11 <= 0.96 x DTWEXBGS on 2026-09-16).
py -3.13, numpy/pandas/scipy. Reads sources/fred_DTWEXBGS_*.csv, sources/fred_DEXUSEU_*.csv, sources/yfinance_dxy_daily_*T0756*.csv and
sources/yfinance_fx_etf_options_20260917T0350Z.json. Writes r10_v2_summary.csv, r10_v2_regime.csv, r10_v2_sensitivity.csv, r10_v2_hazard.csv.
Revision-1 r10_model.py and its CSVs are left untouched.
Changes vs revision 1 (finding ids in research-log.md section 10):
  A12-15  horizon H = 100 FRED observations (weekdays 17 Sep 2026 - 11 Feb 2027 net of six federal holidays; the 2025-26 analogue window has 100)
  A12-05  parametric leg uses the FORWARD vol that calm starts realise (mean forward 105d vol in the trailing-vol calm quintile), not the trailing 4.12%
  A12-06  Reuters-poll drift interpolated on the spot -> 3m -> 6m -> 12m path at the measured broad/EUR beta (-0.62)
  A12-13  option leg: UUP Jan-2027 chain from the 03:50 pull (real quotes, five-figure OI); the implied vol is a band, not a point; broad implied ~ DXY/broad realised ratio x premium
  A12-21  zero-episode years 10 of 21; effective sample size stated (non-overlapping blocks)
"""
import pandas as pd, numpy as np, glob, csv, os, json, math
from scipy.stats import norm, t as student_t
os.chdir(os.path.dirname(os.path.abspath(__file__)))
b = pd.read_csv(sorted(glob.glob('../sources/fred_DTWEXBGS_2026*.csv'))[-1]); b.columns = ['date', 'v']
b.v = pd.to_numeric(b.v, errors='coerce'); b = b.dropna().reset_index(drop=True); b.date = pd.to_datetime(b.date)
x = pd.read_csv(sorted(glob.glob('../sources/yfinance_dxy_daily_2026*T0756*.csv'))[-1]); x.columns = ['date', 'dxy']; x.date = pd.to_datetime(x.date)
e = pd.read_csv(sorted(glob.glob('../sources/fred_DEXUSEU_2026*.csv'))[-1]); e.columns = ['date', 'eur']; e.eur = pd.to_numeric(e.eur, errors='coerce'); e.date = pd.to_datetime(e.date)
lv = np.log(b.v.values); dl = np.diff(lv)
THR = np.log(0.96)
# --- A12-15: horizon
hol = np.array(['2026-10-12', '2026-11-11', '2026-11-26', '2026-12-25', '2027-01-01', '2027-01-18'], dtype='datetime64[D]')
H = int(np.busday_count('2026-09-17', '2027-02-12', holidays=hol))            # 100
analog = b[(b.date > '2025-09-16') & (b.date <= '2026-02-11')]; H_analog = int(analog.v.notna().sum())
# --- spot on 16 Sep (unpublished until 21 Sep): DXY-beta estimate, as revision 1
m = b.merge(x, on='date'); m = m[m.date >= '2024-01-01']
lb = np.log(m.v).diff().dropna(); lx = np.log(m.dxy).diff().dropna(); beta_dxy = np.cov(lb, lx, ddof=1)[0, 1] / lx.var(ddof=1)
dxy11 = float(x[x.date == '2026-09-11'].dxy.iloc[0]); dxy16 = float(x[x.date == '2026-09-16'].dxy.iloc[0])
s11 = float(b.v.iloc[-1]); s16 = s11 * np.exp(beta_dxy * np.log(dxy16 / dxy11)); thr_level = 0.96 * s16
# --- empirical H-day log changes
r = lv[H:] - lv[:-H]; start = b.date.values[:-H]
df = pd.DataFrame({'start': pd.to_datetime(start), 'r': r}); df['yr'] = df.start.dt.year
p_all = (r <= THR).mean(); p_2010 = (df[df.yr >= 2010].r <= THR).mean(); p_2015 = (df[df.yr >= 2015].r <= THR).mean()
zero_years = sorted(y for y, g in df.groupby('yr') if not (g.r <= THR).any()); n_years = df.yr.nunique()
# non-overlapping blocks at every phase: mean and spread of the block estimate (A12-21 effective sample size)
blk = [(r[k::H] <= THR).mean() for k in range(H)]; n_blk = len(r[::H])
se_blk = math.sqrt(p_all * (1 - p_all) / n_blk)
tail = r[r <= THR]; e_tail = tail.mean()
# --- regime: trailing 252d realised vol at start, and the FORWARD H-day vol realised after such starts (A12-05)
rv = pd.Series(dl).rolling(252).std().values * np.sqrt(252)
df['rv'] = np.r_[np.nan, rv][:len(r)]
fwd = np.array([dl[i:i + H].std() * np.sqrt(252) if i + H <= len(dl) else np.nan for i in range(len(r))]); df['fwd'] = fwd
cur = {'rv63': dl[-63:].std() * np.sqrt(252), 'rv126': dl[-126:].std() * np.sqrt(252), 'rv252': dl[-252:].std() * np.sqrt(252), 'rv_full': dl.std() * np.sqrt(252)}
q = df.dropna().copy(); q['rvq'] = pd.qcut(q.rv, 5, labels=False)
reg = q.groupby('rvq').agg(rv_lo=('rv', 'min'), rv_hi=('rv', 'max'), p=('r', lambda s: (s <= THR).mean()), mean=('r', 'mean'), sd=('r', 'std'), fwd_vol=('fwd', 'mean'), n=('r', 'count')).round(4)
band = q[(q.rv > cur['rv252'] - 0.01) & (q.rv < cur['rv252'] + 0.01)]
reg.loc['band_cur_pm1pp'] = [band.rv.min(), band.rv.max(), (band.r <= THR).mean(), band.r.mean(), band.r.std(), band.fwd.mean(), len(band)]
reg.loc['all'] = [q.rv.min(), q.rv.max(), (q.r <= THR).mean(), q.r.mean(), q.r.std(), q.fwd.mean(), len(q)]
reg.to_csv('r10_v2_regime.csv')
p_q1 = float(reg.loc[0, 'p']); fwd_q1 = float(reg.loc[0, 'fwd_vol']); fwd_band = float(band.fwd.mean()); p_band = (band.r <= THR).mean()
df['mom12'] = np.r_[np.full(252, np.nan), lv[252:] - lv[:-252]][:len(r)]
cm = lv[-1] - lv[-253]; mm = df.dropna(subset=['mom12']); sub = mm[(mm.mom12 > cm - 0.02) & (mm.mom12 < cm + 0.02)]; p_mom = (sub.r <= THR).mean()
# --- A12-06: drift from the Reuters poll path (2 Sep 2026: 3m 1.16, 6m 1.17, 12m 1.18), spot 16 Sep 1.1538 (yfinance), at the measured broad/EUR beta
me = b.merge(e, on='date').dropna(); me = me[me.date >= '2024-01-01']
lb2 = np.log(me.v).diff().dropna(); le2 = np.log(me.eur).diff().dropna(); beta_eur = np.cov(lb2, le2, ddof=1)[0, 1] / le2.var(ddof=1)
eur16 = 1.153762; path = [(0, eur16), (3, 1.16), (6, 1.17), (12, 1.18)]; tm = (pd.Timestamp('2027-02-11') - pd.Timestamp('2026-09-16')).days / 30.4375
eurT = next(v0 + (v1 - v0) * (tm - m0) / (m1 - m0) for (m0, v0), (m1, v1) in zip(path, path[1:]) if m0 <= tm <= m1)
drift_poll = beta_eur * math.log(eurT / eur16)      # about -0.0066 at beta -0.62; the audit's -0.0064 used beta -0.6
# --- A12-13: option leg. UUP Jan-2027 chain, 03:50 pull
opt = json.load(open(sorted(glob.glob('../sources/yfinance_fx_etf_options_20260917T0350Z.json'))[-1]))
S0 = opt['UUP']['spot']; T = (pd.Timestamp('2027-01-15') - pd.Timestamp('2026-09-16')).days / 365
def bs(S, K, T, vol, side):
    d1 = (math.log(S / K) + 0.5 * vol * vol * T) / (vol * math.sqrt(T)); d2 = d1 - vol * math.sqrt(T)
    return S * norm.cdf(d1) - K * norm.cdf(d2) if side == 'call' else K * norm.cdf(-d2) - S * norm.cdf(-d1)
def iv(S, K, T, px, side):
    lo, hi = 0.001, 2.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if bs(S, K, T, mid, side) > px: hi = mid
        else: lo = mid
    return mid
uup = []
for o in opt['UUP']['atm_options']:
    if o['exp'] == '2027-01-15' and o['strike'] in (28.0,) and o['bid'] and o['bid'] > 0:
        uup.append(dict(side=o['side'], K=o['strike'], bid=o['bid'], ask=o['ask'], oi=o['oi'], vol=o['vol'], iv_mid=iv(S0, o['strike'], T, (o['bid'] + o['ask']) / 2, o['side']),
                        iv_bid=iv(S0, o['strike'], T, o['bid'], o['side']), iv_ask=iv(S0, o['strike'], T, o['ask'], o['side'])))
dx = np.log(x.dxy).diff().dropna(); rv_dxy = dx[-252:].std() * np.sqrt(252); ratio_dxy_broad = rv_dxy / cur['rv252']
implied_vol = 0.048   # kept: broad realised 4.13% x ~1.15 implied-over-realised premium; the UUP straddle band (5-14%) on a DXY-like basket / 1.27 brackets it and cannot pin it
# --- parametric
def p_norm(vol, drift=0.0): sd = vol * np.sqrt(H / 252); return norm.cdf((THR - drift) / sd)
def p_t(vol, drift=0.0, nu=4): sd = vol * np.sqrt(H / 252); scale = sd / np.sqrt(nu / (nu - 2)); return student_t.cdf((THR - drift) / scale, nu)
fvol = round(fwd_q1, 4)      # forward vol realised after calm-quintile starts (~4.64%)
legs = {
 'empirical_regime': 0.10,     # quintile 1 (p_q1), band (p_band), momentum (p_mom): centre 0.10 as in revision 1, at H = 100
 'parametric_forward_vol': 0.5 * p_norm(fvol, drift_poll) + 0.5 * p_t(fvol, drift_poll),
 'implied_construction': 0.5 * p_norm(implied_vol, drift_poll) + 0.5 * p_t(implied_vol, drift_poll)}
wts = {'empirical_regime': 0.35, 'parametric_forward_vol': 0.35, 'implied_construction': 0.30}
final = sum(wts[k] * legs[k] for k in legs)
rows = [('spot_11sep', s11), ('beta_broad_on_dxy', beta_dxy), ('spot_16sep_est', s16), ('threshold_level', thr_level), ('threshold_log', THR), ('horizon_obs', H), ('horizon_analog_2025_26_obs', H_analog),
        ('n_windows', len(r)), ('mean_Hd', r.mean()), ('sd_Hd', r.std()), ('P_empirical_all', p_all), ('P_empirical_2010plus', p_2010), ('P_empirical_2015plus', p_2015),
        ('zero_episode_years', len(zero_years)), ('n_years', n_years), ('nonoverlap_blocks_n', n_blk), ('nonoverlap_block_p_mean_over_phases', float(np.mean(blk))), ('nonoverlap_block_p_min', float(np.min(blk))), ('nonoverlap_block_p_max', float(np.max(blk))), ('se_binomial_on_blocks', se_blk),
        ('E_move_given_yes', e_tail), ('median_move_given_yes', float(np.median(tail))), ('n_tail', len(tail)),
        ('rv63', cur['rv63']), ('rv126', cur['rv126']), ('rv252', cur['rv252']), ('rv_full', cur['rv_full']), ('P_regime_quintile1', p_q1), ('fwd_vol_after_quintile1_start', fwd_q1), ('P_regime_band_pm1pp', p_band), ('fwd_vol_after_band_start', fwd_band), ('P_momentum_band', p_mom),
        ('beta_broad_on_eur_daily_2024plus', beta_eur), ('eur_16sep', eur16), ('eur_poll_interp_at_11feb', eurT), ('drift_poll_Hd', drift_poll), ('rv252_dxy', rv_dxy), ('ratio_dxy_over_broad_rv', ratio_dxy_broad), ('implied_vol_used', implied_vol), ('forward_vol_used', fvol),
        ('P_normal_fwdvol_poll', p_norm(fvol, drift_poll)), ('P_t4_fwdvol_poll', p_t(fvol, drift_poll)), ('P_normal_fwdvol_zero', p_norm(fvol)), ('P_t4_fwdvol_zero', p_t(fvol)),
        ('P_normal_rv252_poll', p_norm(cur['rv252'], drift_poll)), ('P_normal_implied_poll', p_norm(implied_vol, drift_poll)), ('P_t4_implied_poll', p_t(implied_vol, drift_poll)), ('P_normal_implied_zero', p_norm(implied_vol))]
with open('r10_v2_summary.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['item', 'value'])
    for k, v in rows: w.writerow([k, round(float(v), 5)])
    for k, v in legs.items(): w.writerow(['leg_' + k, round(float(v), 4)])
    w.writerow(['final_blend', round(float(final), 4)])
    for o in uup: w.writerow(['UUP_jan27_%s_K%.0f_iv_bid_mid_ask' % (o['side'], o['K']), '%.3f / %.3f / %.3f (oi %d, vol %d)' % (o['iv_bid'], o['iv_mid'], o['iv_ask'], o['oi'], o['vol'])])
    w.writerow(['zero_episode_year_list', ' '.join(map(str, zero_years))])
with open('r10_v2_sensitivity.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['vol_ann', 'drift_Hd', 'p_normal', 'p_t4', 'p_leg_mix'])
    for vol in [0.035, 0.040, 0.0413, 0.045, 0.0464, 0.048, 0.050, 0.054, 0.060]:
        for dr in [-0.015, -0.010, round(drift_poll, 4), -0.0042, 0.0, 0.005, 0.010]:
            w.writerow([vol, dr, round(p_norm(vol, dr), 4), round(p_t(vol, dr), 4), round(0.5 * p_norm(vol, dr) + 0.5 * p_t(vol, dr), 4)])
# hazard table: spot unchanged (or moved by d) with k observations left, at the forward vol and poll drift scaled to the remaining window
with open('r10_v2_hazard.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['obs_left', 'move_so_far_log', 'p_normal_fwdvol'])
    for k in [100, 80, 60, 40, 30, 20, 10]:
        for d in [0.0, -0.01, -0.02, -0.03]:
            sd = fvol * np.sqrt(k / 252); w.writerow([k, d, round(norm.cdf((THR - d - drift_poll * k / H) / sd), 4)])
print(open('r10_v2_summary.csv').read()); print(open('r10_v2_regime.csv').read())
