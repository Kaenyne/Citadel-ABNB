"""Auditable regional accounting and FX sensitivity; no network or file mutations."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import log_ndtr
from scipy.stats import chi2

REGIONS = ('na', 'emea', 'latam', 'apac')
CCYS = ('USD', 'CAD', 'EUR', 'GBP', 'BRL', 'MXN', 'AUD', 'JPY', 'KRW', 'INR')
AS_OF = '2026-09-12'


def canonical(q):
    q = str(q)
    if len(q) == 4 and q[1] == 'Q':
        q = f'20{q[2:]}Q{q[0]}'
    p = pd.Period(q, freq='Q')
    return str(p)


def require_before(frame, as_of, date_col='print_date'):
    out = frame.copy()
    if date_col not in out:
        raise ValueError('publication date required')
    dates = pd.to_datetime(out[date_col], errors='coerce').dt.normalize()
    cutoff = pd.Timestamp(as_of).normalize()
    if dates.isna().any() or (dates >= cutoff).any():
        raise ValueError('all data must be published strictly before as_of')
    return out


def annual_ratios(frame):
    d = frame.loc[frame.region.isin(REGIONS)].copy()
    if d.duplicated(['year', 'region']).any() or (d.gbv_musd <= 0).any():
        raise ValueError('unique positive annual GBV required')
    d['lambda_pct'] = 100 * d.revenue_musd / d.gbv_musd
    precision = np.where(d.year <= 2021, 0.05, 0.5)
    d['lambda_rounding_lo'] = 100 * (d.revenue_musd - precision) / (d.gbv_musd + precision)
    d['lambda_rounding_hi'] = 100 * (d.revenue_musd + precision) / (d.gbv_musd - precision)
    d['basis'] = 'measured annual ratio; not a quarterly recognition coefficient'
    d['publication_date'] = ''
    d['publication_limitation'] = 'source_10k identifies filing year but not publication timestamp'
    return d


def validate_exposure(frame):
    needed = {'quarter', 'geography', 'currency', 'gbv_share', 'revenue_share'}
    if not needed.issubset(frame):
        raise ValueError('missing exposure columns')
    if frame.duplicated(['quarter', 'geography', 'currency']).any():
        raise ValueError('duplicate geography currency')
    values = frame[['gbv_share', 'revenue_share']].to_numpy(float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError('exposure shares must be finite and nonnegative')
    sums = frame.groupby(['quarter', 'geography'])[['gbv_share', 'revenue_share']].sum()
    if not np.allclose(sums, 1, atol=1e-10, rtol=0):
        raise ValueError('separate GBV and revenue shares must sum to one')
    return True


def origin_matrix(destination_nights, public_origins, cross_border=.46):
    """Country cross-border share is NOT region off-diagonal share."""
    if not 0 <= cross_border <= 1:
        raise ValueError('cross-border share outside [0,1]')
    n = destination_nights.reindex(REGIONS).astype(float)
    if n.isna().any() or (n <= 0).any():
        raise ValueError('positive nights in every destination required')
    global_mix = n / n.sum()
    matrix = pd.DataFrame(0., index=REGIONS, columns=REGIONS)
    for destination in REGIONS:
        foreign = public_origins.get(destination, global_mix).reindex(REGIONS).fillna(0.)
        if (foreign < 0).any() or not np.isclose(foreign.sum(), 1):
            raise ValueError('foreign origin proxy must sum to one')
        mix = cross_border * foreign
        mix.loc[destination] += 1 - cross_border
        matrix[destination] = n[destination] * mix
    if not np.allclose(matrix.sum(axis=0), n):
        raise AssertionError('O-D destination margins failed')
    return matrix


def exposure_mix(destination, origins, guest_fee_share):
    if not 0 <= guest_fee_share <= 1:
        raise ValueError('guest fee fraction outside [0,1]')
    d = np.asarray(destination, float)
    o = np.asarray(origins, float)
    if (d < 0).any() or (o < 0).any() or not np.isclose(d.sum(), 1) or not np.isclose(o.sum(), 1):
        raise ValueError('currency weights must sum to one')
    return d, (1 - guest_fee_share) * d + guest_fee_share * o


def admissible_pass_scales(frame):
    """A finite slope explicitly labelled unidentified is not a usable fitted parameter."""
    d=frame.set_index('region')
    scales=pd.Series(1.,index=REGIONS)
    for region in REGIONS:
        if region not in d.index:
            continue
        row=d.loc[region]
        if 'not identified' in str(row.get('note','')).lower():
            continue
        slope=float(row.slope_pp_per_pp)
        if np.isfinite(slope) and slope>=0:
            scales[region]=slope
    return scales


def translation(gbv_lag1, gbv_lag2, lambda_pct, fx_lag1, fx_lag2, prior_revenue):
    """Fixed 2/3--1/3 kernel; FX is removed from USD GBV, never added twice."""
    arrays = [np.asarray(x, float) for x in [gbv_lag1, gbv_lag2, lambda_pct, fx_lag1, fx_lag2]]
    g1, g2, lam, x1, x2 = arrays
    if not all(np.isfinite(a).all() for a in arrays) or prior_revenue <= 0:
        raise ValueError('finite inputs and positive prior revenue required')
    if (g1 < 0).any() or (g2 < 0).any() or (lam < 0).any() or (x1 <= -100).any() or (x2 <= -100).any():
        raise ValueError('invalid GBV, lambda or FX')
    dollars = lam / 100 * (2 / 3 * g1 + 1 / 3 * g2)
    constant_fx = lam / 100 * (2 / 3 * g1 / (1 + x1 / 100) + 1 / 3 * g2 / (1 + x2 / 100))
    return dollars, 100 * (dollars - constant_fx) / prior_revenue


def engine_order(nights, adr_reference_usd, take_rate, gbv_fx_pct, lagged_revenue_fx_pct,
                 adr_scale, revenue_scale, hedge_musd=0):
    """Python equivalent of the supplied R-engine calculation order."""
    g0 = np.asarray(nights) * np.asarray(adr_reference_usd)
    gbv = g0 * (1 + adr_scale * np.asarray(gbv_fx_pct) / 100)
    revenue_prehedge = gbv * take_rate * (1 + revenue_scale * np.asarray(lagged_revenue_fx_pct) / 100)
    return dict(g0=g0, gbv=gbv, revenue_prehedge=revenue_prehedge,
                revenue_afterhedge=revenue_prehedge + hedge_musd)


def _log_interval_probability(zlo, zhi):
    # Reflect positive-tail intervals before subtraction to avoid catastrophic cancellation.
    reflect = zlo > 0
    a = np.where(reflect, -zhi, zlo)
    b = np.where(reflect, -zlo, zhi)
    log_a, log_b = log_ndtr(a), log_ndtr(b)
    return log_b + np.log(-np.expm1(np.minimum(log_a - log_b, -1e-15)))


def interval_fit(X, y, halfwidth=.5):
    """Nonnegative lag coefficients; rounded targets scored as intervals, not exact points."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    if X.ndim != 2 or X.shape[0] != len(y) or len(y) <= X.shape[1] + 1:
        raise ValueError('too few observations or incompatible fit shapes')
    if not np.isfinite(X).all() or not np.isfinite(y).all() or halfwidth <= 0:
        raise ValueError('finite data and positive rounding interval required')
    k = X.shape[1]
    def nll(theta):
        mu, sd = X @ theta[:k], np.exp(theta[-1])
        return -float(_log_interval_probability((y-halfwidth-mu)/sd, (y+halfwidth-mu)/sd).sum())
    starts = [np.r_[np.full(k, .56/k), np.log(.8)]]
    for j in range(k):
        b = np.zeros(k); b[j] = .56
        starts.append(np.r_[b, np.log(.8)])
    fits = [minimize(nll, s, method='L-BFGS-B', bounds=[(0, 5)]*k+[(-5, 3)]) for s in starts]
    fit = min(fits, key=lambda x:x.fun)
    if not fit.success:
        raise RuntimeError('interval likelihood did not converge: '+str(fit.message))
    beta, sd = fit.x[:k], float(np.exp(fit.x[-1]))
    scale = float(beta.sum())
    grid = np.sort(np.unique(np.r_[np.linspace(0, max(2.5, scale*2), 101), scale, .56]))
    rows=[]
    # Profile the sum of coefficients, leaving lag shares and dispersion free.
    for s in grid:
        if s == 0:
            result = minimize(lambda z:nll(np.r_[np.zeros(k), z[0]]), [np.log(sd)], bounds=[(-5,3)])
        else:
            initial = np.r_[beta/scale*s if scale else np.full(k,s/k), np.log(sd)]
            result = minimize(nll, initial, method='SLSQP', bounds=[(0,s)]*k+[(-5,3)],
                              constraints=[{'type':'eq','fun':lambda z,s=s:z[:k].sum()-s}],
                              options={'maxiter':300,'ftol':1e-9})
        rows.append({'scale':s,'nll':result.fun,'success':bool(result.success),
                     'in_95_profile_set':bool(result.success and 2*(result.fun-fit.fun)<=chi2.ppf(.95,1))})
    profile = pd.DataFrame(rows)
    accepted=profile.loc[profile.in_95_profile_set,'scale']
    return {'scale':scale,'scale_ci_lo':float(accepted.min()),'scale_ci_hi':float(accepted.max()),
            'sd_pp':sd,'n':len(y),'n_params':k+1,'beta':beta.tolist(),'nll':fit.fun,
            'ci_basis':'95% profile likelihood grid; retrospective; not exposure-measurement uncertainty',
            'ci_hits_upper_grid':bool(accepted.max()==grid.max())}, profile
