from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

METHODS=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(METHODS))
from regional_kernel_v1.engine import (REGIONS, annual_ratios, require_before, origin_matrix,
    exposure_mix, validate_exposure, translation, engine_order, interval_fit, admissible_pass_scales)


def test_annual_rounding_bounds_preserve_published_precision():
    a=pd.DataFrame([dict(year=2025,region='na',gbv_musd=40295,revenue_musd=5196,source_10k='FY2025')])
    r=annual_ratios(a).iloc[0]
    assert r.lambda_rounding_lo<100*5196/40295<r.lambda_rounding_hi
    assert r.publication_date==''


@pytest.mark.parametrize('value',['2026-09-12','2026-09-13','2026-09-12 00:00:01',None,'not a date'])
def test_same_day_future_or_unknown_publication_refused(value):
    with pytest.raises(ValueError,match='strictly before'):
        require_before(pd.DataFrame({'print_date':[value]}),'2026-09-12 23:59:59')


def test_past_publication_accepted_and_missing_column_refused():
    assert len(require_before(pd.DataFrame({'print_date':['2026-09-11']}),'2026-09-12'))==1
    with pytest.raises(ValueError,match='publication date'):
        require_before(pd.DataFrame({'date':['2026-09-11']}),'2026-09-12')


def test_country_crossborder_is_not_region_offdiagonal():
    n=pd.Series([40.,30.,20.,10.],index=REGIONS)
    matrix=origin_matrix(n,{},.46)
    assert np.allclose(matrix.sum(axis=0),n)
    assert matrix.to_numpy().sum()==pytest.approx(n.sum())
    assert (matrix.to_numpy().sum()-np.trace(matrix)) / n.sum()<.46
    assert np.allclose(origin_matrix(n,{},0).to_numpy(),np.diag(n))


def test_guest_fee_migration_moves_revenue_currency_not_gbv():
    gbv,rev0=exposure_mix([.9,.1],[.2,.8],0)
    gbv1,rev1=exposure_mix([.9,.1],[.2,.8],1)
    assert np.allclose(gbv,gbv1)
    assert np.allclose(rev0,[.9,.1])
    assert np.allclose(rev1,[.2,.8])
    with pytest.raises(ValueError):exposure_mix([.9,.1],[.2,.8],1.1)


@pytest.mark.parametrize('failure',['duplicate','negative','wrong_sum','nan'])
def test_bad_exposure_refused(failure):
    d=pd.DataFrame({'quarter':['2026Q3']*2,'geography':['na']*2,'currency':['USD','CAD'],
                    'gbv_share':[.8,.2],'revenue_share':[.6,.4]})
    assert validate_exposure(d)
    if failure=='duplicate':d=pd.concat([d,d.iloc[:1]],ignore_index=True)
    elif failure=='negative':d.loc[0,'gbv_share']=-.1
    elif failure=='wrong_sum':d.loc[0,'revenue_share']=.3
    else:d.loc[0,'gbv_share']=np.nan
    with pytest.raises(ValueError):validate_exposure(d)


def test_fx_removal_identity_and_usd_zero():
    dollars,pp=translation([110.],[110.],[10.],[10.],[10.],10.)
    assert dollars[0]==pytest.approx(11.)
    assert pp[0]==pytest.approx(10.)
    assert translation([110.],[110.],[10.],[0.],[0.],10.)[1][0]==0


def test_hedge_once_and_independent_exposure_order():
    x=engine_order(10.,100.,.1,10.,20.,1.,.5,-2.)
    assert x['g0']==pytest.approx(1000.)
    assert x['gbv']==pytest.approx(1100.)
    assert x['revenue_prehedge']==pytest.approx(121.)
    assert x['revenue_afterhedge']==pytest.approx(119.)


def test_invalid_translation_refused():
    with pytest.raises(ValueError):translation([100],[100],[10],[-100],[0],100)
    with pytest.raises(ValueError):translation([100],[100],[10],[0],[0],0)


def test_finite_but_unidentified_slope_is_not_adopted():
    d=pd.DataFrame([dict(region='na',slope_pp_per_pp=3.205,note='not identified: slope is noise'),
                    dict(region='apac',slope_pp_per_pp=.86,note='fitted')])
    scales=admissible_pass_scales(d)
    assert scales['na']==1.
    assert scales['apac']==.86
    assert scales['emea']==1.


def test_public_extract_control_totals():
    p=pd.read_csv(METHODS/'regional_kernel_v1/public_inputs.csv')
    assert p[p.provider=='NTTO'].visitors_or_nights.sum()==68288000
    assert p[p.provider=='JNTO'].visitors_or_nights.sum()==3442100
    assert p[p.provider=='EUROSTAT'].visitors_or_nights.sum()==951611862
    assert (pd.to_datetime(p.publication_date)<pd.Timestamp('2026-09-12')).all()


def test_interval_fit_handles_rounding_and_identified_scale():
    # One lag keeps this diagnostic fast and independently identifies the known scale.
    x=np.array([-8,-6,-4,-2,0,2,4,6,8,10.])[:,None]
    y=np.round(.6*x[:,0]+np.array([.1,-.3,.2,-.1,.3,-.3,.1,.2,-.2,.1]))
    r,profile=interval_fit(x,y)
    assert r['scale_ci_lo']-1e-12<=.6<=r['scale_ci_hi']+1e-12
    assert r['scale']==pytest.approx(.6,abs=.12)
    assert r['n']==10 and r['n_params']==2
    assert not profile.empty
