import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/"analysis/src/forecast_methods"))
from cohort_fx_v2.engine import apply_timing,from_reported_contributions,RateBook,yoy_bridge
from cohort_fx_v2.run import rate_table,FX_PATH

DATE="2026-09-13"
META=dict(information_date=DATE,source_ref="hand calculated fixture",evidence_status="synthetic",reference_basis="one")


def fixture(u=.2):
    c=pd.DataFrame([dict(quarter="2026Q3",booking_quarter=b,currency="EUR",
        reported_contribution_usd=v,rnpl_share=u,**META) for b,v in [("2026Q2",200.),("2026Q1",50.)]])
    rates=pd.DataFrame([dict(period=p,currency="EUR",usd_per_unit=v,reference_usd_per_unit=1.,
        rate_status="synthetic",quote_cutoff="2026-09-04",**META) for p,v in
        [("2026Q1",1.),("2026Q2",.8),("2026-07",1.2)]])
    a=pd.DataFrame([dict(quarter=r.quarter,booking_quarter=r.booking_quarter,currency=r.currency,
        fx_period="2026-07",p=1.,timing_hypothesis="recognition_month",**META) for r in c.itertuples()])
    return c,a,rates


def calc(u=.2):
    c,a,r=fixture(u)
    return apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)


def test_hand_arithmetic_and_conservation():
    out=calc();d=out["detail"];s=out["summary"].iloc[0]
    assert s.reference_revenue_usd==pytest.approx(300)
    assert s.booking_revenue_usd==pytest.approx(250)
    assert s.retimed_revenue_usd==pytest.approx(272)
    assert s.incremental_replacement_usd==pytest.approx(22)
    assert d.w_reference.sum()==pytest.approx(1)
    assert (d.ordinary_exposure_weight+d.rnpl_exposure_weight).sum()==pytest.approx(1)
    assert out["allocations"].rnpl_reference_exposure_weight.sum()==pytest.approx(.2)
    assert s.reported_revenue_including_hedges_usd!=s.reported_revenue_including_hedges_usd


def test_reference_weights_are_not_kernel_coefficients_or_reported_shares():
    d=calc()["detail"]
    assert d.iloc[0].w_reference==pytest.approx(250/300)
    assert d.iloc[0].w_reference!=pytest.approx(2/3)
    assert d.iloc[0].w_reference!=pytest.approx(200/250)


@pytest.mark.parametrize("u,expected",[(0,250),(1,360),(.1,261),(.3,283)])
def test_rnpl_boundary_and_linearity(u,expected):
    assert calc(u)["summary"].iloc[0].retimed_revenue_usd==pytest.approx(expected)


def test_equal_booking_and_recognition_rates():
    c,a,r=fixture();r.usd_per_unit=1.2
    s=apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)["summary"].iloc[0]
    assert s.incremental_replacement_usd==pytest.approx(0)
    assert s.booking_level_multiplier==pytest.approx(1.2)


@pytest.mark.parametrize("currency",["EUR","USD"])
def test_all_equal_rates_and_all_usd(currency):
    c,a,r=fixture(1);c.currency=currency;a.currency=currency;r.currency=currency;r.usd_per_unit=1.
    s=apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)["summary"].iloc[0]
    assert s.replacement_multiplier==pytest.approx(1)
    assert s.retimed_level_multiplier==pytest.approx(1)


def test_quote_direction_and_inverse_units_counterexample():
    c,a,r=fixture(1)
    r.usd_per_unit=1.
    r.loc[r.period.eq("2026-07"),"usd_per_unit"]=1.1
    s=apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)["summary"].iloc[0]
    assert s.incremental_replacement_usd==pytest.approx(25)
    r.loc[r.period.eq("2026-07"),"usd_per_unit"]=1/1.1
    t=apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)["summary"].iloc[0]
    assert t.incremental_replacement_usd<0
    assert t.incremental_replacement_usd!=pytest.approx(-25)


def test_full_factor_on_reported_kernel_double_counts():
    s=calc()["summary"].iloc[0]
    correct=s.booking_revenue_usd*s.replacement_multiplier
    wrong=s.booking_revenue_usd*s.retimed_level_multiplier
    assert correct==pytest.approx(272)
    assert wrong!=pytest.approx(correct)


def test_missing_positive_exposure_rate_fails():
    c,a,r=fixture();r=r[~r.period.eq("2026-07")]
    with pytest.raises(ValueError,match="Missing FX rate"):
        apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)


def test_zero_rnpl_does_not_need_future_rate():
    c,a,r=fixture(0);r=r[~r.period.eq("2026-07")]
    assert apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)["summary"].iloc[0].incremental_replacement_usd==pytest.approx(0)


def test_zero_weight_currency_does_not_need_rate():
    c,a,r=fixture();z=c.iloc[[0]].copy();z.currency="ZZZ";z.reported_contribution_usd=0
    za=a.iloc[[0]].copy();za.currency="ZZZ"
    out=apply_timing(from_reported_contributions(pd.concat([c,z]),r,DATE),pd.concat([a,za]),r,DATE)
    assert out["summary"].iloc[0].retimed_revenue_usd==pytest.approx(272)


@pytest.mark.parametrize("column,value",[("rnpl_share",-.1),("rnpl_share",1.1),("rnpl_share",np.nan),("reported_contribution_usd",-1.),("reported_contribution_usd",np.inf)])
def test_invalid_cohort_inputs(column,value):
    c,a,r=fixture();c.loc[0,column]=value
    with pytest.raises(ValueError):
        apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)


@pytest.mark.parametrize("p",[.5,1.1,-.1,np.nan])
def test_invalid_allocations(p):
    c,a,r=fixture();a.loc[0,"p"]=p
    with pytest.raises(ValueError):
        apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)


@pytest.mark.parametrize("which",["cohorts","allocations","rates"])
def test_future_information_dates_rejected(which):
    c,a,r=fixture();f={"cohorts":c,"allocations":a,"rates":r}[which]
    f.loc[0,"information_date"]="2026-09-14"
    with pytest.raises(ValueError,match="Information-date leakage"):
        apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)


def test_future_actual_rate_and_quote_rejected():
    _,_,r=fixture();r.loc[0,"quote_cutoff"]="2026-09-14"
    with pytest.raises(ValueError,match="quote cutoff"):
        RateBook(r,DATE)
    r.loc[0,"quote_cutoff"]="2026-09-04";r.loc[0,"period"]="2026-09";r.loc[0,"rate_status"]="observed"
    with pytest.raises(ValueError,match="fully observed"):
        RateBook(r,DATE)


def test_duplicate_rate_or_allocation_keys_rejected():
    c,a,r=fixture()
    with pytest.raises(ValueError,match="duplicate"):
        RateBook(pd.concat([r,r.iloc[[0]]]),DATE)
    with pytest.raises(ValueError,match="duplicate"):
        apply_timing(from_reported_contributions(c,r,DATE),pd.concat([a,a.iloc[[0]]]),r,DATE)


def test_missing_cohort_allocation_rejected():
    c,a,r=fixture()
    with pytest.raises(ValueError,match="keys mismatch"):
        apply_timing(from_reported_contributions(c,r,DATE),a.iloc[[0]],r,DATE)


def test_incompatible_reference_and_currency_index_rejected():
    c,a,r=fixture();c.reference_basis="wrong"
    with pytest.raises(ValueError,match="Reference basis"):
        from_reported_contributions(c,r,DATE)
    r.loc[0,"currency"]="USD_BROAD"
    with pytest.raises(ValueError,match="Not a currency"):
        RateBook(r,DATE)


def test_recognition_outside_target_refused_payment_label_explicit():
    c,a,r=fixture();a.fx_period="2026-06"
    extra=r.iloc[[-1]].copy();extra.period="2026-06";r=pd.concat([r,extra])
    with pytest.raises(ValueError,match="outside target"):
        apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)
    a.timing_hypothesis="payment_fixing_proxy"
    assert len(apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)["summary"])==1


def test_reference_rate_cannot_change_with_timing_period():
    c,a,r=fixture();r.loc[0,"reference_usd_per_unit"]=1.1
    with pytest.raises(ValueError,match="Fixed reference"):
        RateBook(r,DATE)


def test_level_and_yoy_are_distinct_and_pp_bridge_has_denominator():
    current=calc()["summary"].iloc[0].to_dict()
    prior={**current,"quarter":"2025Q3","reference_revenue_usd":250.,"booking_revenue_usd":225.,
        "retimed_revenue_usd":225.,"rnpl_weight":0}
    y=yoy_bridge(current,prior)
    assert y["reference_yoy_pct"]==pytest.approx(20)
    assert y["retimed_yoy_pct"]==pytest.approx(100*(272/225-1))
    assert y["timing_growth_gap_pp"]==pytest.approx(100*22/225)
    assert y["current_level_fx_pct"]!=pytest.approx(y["fx_growth_gap_pp"])
    prior["reference_basis"]="wrong"
    with pytest.raises(ValueError,match="reference basis"):
        yoy_bridge(current,prior)


def test_future_daily_mutation_excluded_and_stale_cache_rejected():
    daily=pd.read_csv(FX_PATH)
    out=rate_table(daily,{"2026Q2","2026-09"},1)
    extra=daily[daily.unit.eq("usd_per_foreign_unit")].groupby("ccy").tail(1).copy()
    extra.date="2026-09-14";extra.usd_per_unit=1e9
    pd.testing.assert_frame_equal(out,rate_table(pd.concat([daily,extra]),{"2026Q2","2026-09"},1))
    with pytest.raises(ValueError,match="Stale"):
        rate_table(daily,{"2026-09"},1,as_of="2026-10-13")
    with pytest.raises(ValueError,match="unavailable"):
        rate_table(daily,{"2026Q2"},1,as_of="2026-08-01")


def test_no_hedge_addition_argument_or_cancellation_multiplier():
    c,a,r=fixture();norm=from_reported_contributions(c,r,DATE)
    with pytest.raises(TypeError):
        apply_timing(norm,a,r,DATE,hedge_usd=100)
    with pytest.raises(TypeError):
        apply_timing(norm,a,r,DATE,cancellation_loss=.1)


def test_review_quote_after_information_date_rejected():
    r=rate_table(pd.read_csv(FX_PATH),{"2026Q1"},1)
    ix=r.currency.eq("EUR")
    r.loc[ix,"information_date"]="2026-02-01"
    r.loc[ix,"quote_cutoff"]="2026-03-31"
    with pytest.raises(ValueError,match="after source information"):
        RateBook(r,DATE)


def test_review_observed_quote_outside_period_rejected():
    r=rate_table(pd.read_csv(FX_PATH),{"2026Q1"},1)
    r.loc[r.currency.eq("EUR"),"quote_cutoff"]="2025-01-01"
    with pytest.raises(ValueError,match="outside its period"):
        RateBook(r,DATE)


@pytest.mark.parametrize("drop_case",["single_observation","missing_first_month","missing_last_month","internal_month_gap"])
def test_review_reference_coverage_incomplete_rejected(drop_case):
    d=pd.read_csv(FX_PATH)
    year=d.date.str.startswith("2025")
    if drop_case=="single_observation":
        d=pd.concat([d[~year],d[year].groupby("ccy").head(1)])
    elif drop_case=="missing_first_month":
        d=d[~d.date.str.startswith("2025-01")]
    elif drop_case=="missing_last_month":
        d=d[~d.date.str.startswith("2025-12")]
    else:
        d=d[~d.date.str.startswith("2025-06")]
    with pytest.raises(ValueError,match="Incomplete 2025 reference"):
        rate_table(d,{"2026Q2","2026-09"},1)


def test_date_vintage_accepts_same_day_information_but_not_next_day():
    c,a,r=fixture();r.loc[0,"information_date"]="2026-09-13T23:00:00Z"
    RateBook(r,DATE)
    r.loc[0,"information_date"]="2026-09-14T00:00:00Z"
    with pytest.raises(ValueError,match="Information-date leakage"):
        RateBook(r,DATE)


def test_reference_rescaling_preserves_reported_baseline_and_replacement():
    c,a,r=fixture();base=apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)["summary"].iloc[0]
    r.reference_usd_per_unit*=2.75
    new=apply_timing(from_reported_contributions(c,r,DATE),a,r,DATE)["summary"].iloc[0]
    for field in ["booking_revenue_usd","retimed_revenue_usd","incremental_replacement_usd","replacement_multiplier"]:
        assert new[field]==pytest.approx(base[field])


@pytest.mark.parametrize("drop_case",["single_last_quote","missing_first_month","internal_month_gap"])
def test_review_sparse_observed_period_rejected(drop_case):
    d=pd.read_csv(FX_PATH)
    q=d.date.between("2026-04-01","2026-06-30")
    if drop_case=="single_last_quote":
        d=pd.concat([d[~q],d[q].groupby("ccy").tail(1)])
    elif drop_case=="missing_first_month":
        d=d[~d.date.str.startswith("2026-04")]
    else:
        d=d[~d.date.str.startswith("2026-05")]
    with pytest.raises(ValueError,match="Incomplete observed period"):
        rate_table(d,{"2026Q2"},1)
