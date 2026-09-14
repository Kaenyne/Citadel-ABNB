"""Gate 1 tests: accounting identities, temporal refusals and regional aggregation."""
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from kernel_engine_v2 import engine as E

AS_OF="2026-09-12"


@pytest.fixture
def panel():
    return E._panel(AS_OF)


CALLS = [
    lambda **kw:E.lambda_table(AS_OF,**kw),
    lambda **kw:E.pit_lambda(3,AS_OF,**kw),
    lambda **kw:E.kernel_forecast("2026Q3",AS_OF,**kw),
    lambda **kw:E.kernel_guide("2026Q3",AS_OF,**kw),
    lambda **kw:E.term_structure(AS_OF,**kw),
    lambda **kw:E.control_chart(AS_OF,**kw),
]


@pytest.mark.parametrize("call",CALLS)
@pytest.mark.parametrize("bad_date",["2026-09-12","2026-09-13",None])
def test_every_public_function_refuses_same_day_future_and_undated_input(call,bad_date,panel):
    panel.loc[panel.index[-1],"print_date"]=pd.NaT if bad_date is None else pd.Timestamp(bad_date)
    with pytest.raises(E.PointInTimeError):
        call(panel=panel)


def test_acceptance_twelve_exact_accounting_cells():
    expected={"2024Q1":13.034,"2025Q1":12.325,"2026Q1":12.612,
              "2024Q2":13.449,"2025Q2":13.946,"2026Q2":13.736,
              "2023Q3":17.391,"2024Q3":17.145,"2025Q3":17.182,
              "2023Q4":11.946,"2024Q4":12.117,"2025Q4":12.026}
    got=E.lambda_table(AS_OF).set_index("quarter").lambda_pct
    for quarter,value in expected.items():
        # Independently compare the interval implied by three-decimal publication.
        assert value-.000500000001 <= float(got[quarter]) <= value+.000500000001
        if quarter[-1] in "34":
            assert round(float(got[quarter]),2)==float(Decimal(str(value)).quantize(Decimal(".01"),rounding=ROUND_HALF_UP))


def test_same_day_letter_gbv_is_not_available_but_next_day_is():
    with pytest.raises(E.DataUnavailable):
        E.kernel_forecast("2026Q3","2026-08-06",variant="last3")
    assert E.kernel_forecast("2026Q3","2026-08-07",variant="last3")["point"]>0


def test_future_gbv_requires_explicit_scenario():
    with pytest.raises(E.DataUnavailable):
        E.kernel_forecast("2026Q4",AS_OF)


def test_exact_quarter_joins_do_not_bridge_gaps(panel):
    panel=panel[panel.quarter!="2026Q1"]
    with pytest.raises(E.DataUnavailable):
        E.kernel_forecast("2026Q3",AS_OF,panel=panel)


@pytest.mark.parametrize("bad_value",[0.,-1.,np.nan,np.inf])
def test_invalid_gbv_refused(panel,bad_value):
    panel.loc[panel.index[-1],"gbv_musd"]=bad_value
    with pytest.raises(ValueError):
        E.kernel_forecast("2026Q3",AS_OF,panel=panel)


def test_duplicate_quarters_refused(panel):
    with pytest.raises(ValueError):
        E.pit_lambda(3,AS_OF,panel=pd.concat([panel,panel.tail(1)],ignore_index=True))


def test_no_hidden_full_sample_default_and_no_input_mutation(panel):
    before=panel.copy(deep=True)
    early=E._panel("2024-01-01")
    result=E.pit_lambda(3,"2024-01-01",panel=early)
    assert max(result["training_quarters"])<="2023Q3"
    E.kernel_forecast("2026Q3",AS_OF,panel=panel)
    pd.testing.assert_frame_equal(panel,before)


def test_ex_covid_drops_only_eligible_known_growth_cells(panel):
    result=E.pit_lambda(3,AS_OF,variant="ex_covid",panel=panel)
    chosen=panel[panel.quarter.isin(result["training_quarters"])]
    assert chosen.nights_yoy_pct.notna().all()
    assert (chosen.nights_yoy_pct.abs()<=25).all()


def test_guide_cushion_arithmetic_and_ordered_uncertainty():
    forecast=E.kernel_forecast("2026Q3",AS_OF)
    guide=E.kernel_guide("2026Q3",AS_OF)
    assert guide["point"]==pytest.approx(forecast["point"]/(1+guide["cushion"]))
    assert guide["cushion_n"]==8
    ladder=[guide[k] for k in ["q05","q10","q25","q50","q75","q90","q95"]]
    assert np.isfinite(ladder).all() and np.all(np.diff(ladder)>=0)
    assert guide["conformal_n_cal"]<=6


def test_same_day_cushion_refused():
    frame=pd.DataFrame([dict(quarter="2026Q2",print_date=AS_OF,ratio=1.01)])
    with pytest.raises(E.PointInTimeError):
        E.kernel_guide("2026Q3",AS_OF,cushion_frame=frame)


@pytest.fixture
def regional(panel):
    rows=[]
    for row in panel.tail(2).itertuples():
        for region,weight in (("A",.4),("B",.6)):
            rows.append(dict(quarter=row.quarter,region=region,gbv_usd_booking_dated=row.gbv_musd*1e6*weight))
    g=pd.DataFrame(rows)
    l=pd.DataFrame([dict(region="A",season=3,lambda_pct=15.,lambda_sd_pct=.1,print_date="2026-09-01"),
                    dict(region="B",season=3,lambda_pct=20.,lambda_sd_pct=.2,print_date="2026-09-01")])
    return g,l


def test_regional_revenue_and_guide_are_sums_in_correct_currency_units(regional):
    g,l=regional
    result=E.kernel_forecast("2026Q3",AS_OF,regional_gbv=g,regional_lambdas=l)
    expected=((2*27200+29200)/3)*(.4*.15+.6*.20)
    assert result["point"]==pytest.approx(expected)
    assert result["point"]==pytest.approx(sum(r["point"] for r in result["regions"]))
    guide=E.kernel_guide("2026Q3",AS_OF,regional_gbv=g,regional_lambdas=l)
    assert guide["point"]==pytest.approx(sum(r["point"] for r in guide["regions"]))
    assert E.pit_lambda(3,AS_OF,regional_gbv=g,regional_lambdas=l)["lambda_pct"] is None


@pytest.mark.parametrize("call",CALLS)
def test_all_functions_reject_future_regional_coefficients(call,regional):
    g,l=regional
    l.loc[0,"print_date"]=AS_OF
    with pytest.raises(E.PointInTimeError):
        call(regional_gbv=g,regional_lambdas=l)


@pytest.mark.parametrize("call",CALLS)
def test_all_functions_reject_future_regional_gbv(call,regional):
    g,l=regional
    g["print_date"]=AS_OF
    with pytest.raises(E.PointInTimeError):
        call(regional_gbv=g,regional_lambdas=l)


def test_missing_regional_coefficient_and_unknown_publication_date_refused(regional):
    g,l=regional
    with pytest.raises(ValueError):
        E.kernel_forecast("2026Q3",AS_OF,regional_gbv=g,regional_lambdas=l.iloc[:1])
    g.loc[0,"quarter"]="2030Q1"
    with pytest.raises(E.PointInTimeError):
        E.kernel_forecast("2026Q3",AS_OF,regional_gbv=g,regional_lambdas=l)


def test_term_structure_labels_unprinted_inputs_and_historical_scenario_abstention():
    terms=E.term_structure(AS_OF).set_index("quarter")
    assert terms.loc["2026Q4","status"]=="conditional_scenario"
    assert terms.loc["2027Q1","status"]=="conditional_scenario"
    assert terms.loc["2026Q4","gbv_forecast_n"]==1
    assert terms.loc["2027Q1","gbv_forecast_n"]==2
    assert terms.loc["2027Q1","q10"]<terms.loc["2027Q1","q90"]
    historical=E.term_structure("2026-08-07")
    assert (historical.iloc[1:].status=="unavailable").all()


def test_control_rule_never_backdates_live_card():
    assert E.control_chart("2024-01-01")["rule"] is None
    current=E.control_chart(AS_OF)
    assert current["rule"]["base_musd"]==pytest.approx(27866.666666666668)
    assert current["rule"]["warn_below_lambda_pct"]==17.09
    assert current["rule"]["escalate_below_lambda_pct"]==16.93
    assert (current["alarms"].n_train>=2).all()


@pytest.mark.parametrize("offset,expected",[(0,True),(.000499999,True),(-.0005,True),(.00050001,False),(-.00050001,False),(np.nan,False),(np.inf,False)])
def test_published_reference_precision_boundary(offset,expected):
    from kernel_engine_v2.acceptance import within_reference_precision
    assert within_reference_precision(12.325+offset,12.325) is expected


@pytest.mark.parametrize("season",[0,5,3.9,np.nan,np.inf])
def test_fractional_or_invalid_season_refused(season,regional):
    with pytest.raises(ValueError):
        E.pit_lambda(season,AS_OF)
    g,l=regional
    l["season"]=l.season.astype(float)
    l.loc[0,"season"]=season
    with pytest.raises(ValueError):
        E.kernel_forecast("2026Q3",AS_OF,regional_gbv=g,regional_lambdas=l)


def test_regional_provenance_and_no_fake_conformal_calibration(regional):
    g,l=regional
    for fn in (E.kernel_forecast,E.kernel_guide):
        r=fn("2026Q3",AS_OF,regional_gbv=g,regional_lambdas=l)
        assert r["knowable_from"]=="2026-09-01"
    assert E.kernel_guide("2026Q3",AS_OF,regional_gbv=g,regional_lambdas=l)["conformal_n_cal"]==0


def test_forecast_cannot_train_on_already_printed_target():
    for fn in (E.kernel_forecast,E.kernel_guide):
        with pytest.raises(E.PointInTimeError):
            fn("2026Q2",AS_OF)


def test_calibration_uses_full_historical_cushions_and_requested_stat(panel):
    history=E._cushions(AS_OF,trailing=False)
    assert len(history)>8
    for statistic in ("mean","median"):
        result=E.kernel_guide("2026Q3",AS_OF,cushion=statistic)
        assert result["conformal_n_cal"]==6
        for row in result["conformal_calibration_cells"]:
            admissible=history[history.print_date<pd.Timestamp(row["origin"])].tail(8)
            denominator=getattr(admissible.ratio,statistic)()
            predicted=E.kernel_forecast(row["quarter"],row["origin"])["point"]/denominator
            assert row["pred"]==pytest.approx(predicted)
            assert row["known_from"]<AS_OF
            assert row["cushion_stat"]==statistic


def test_term_structure_guide_intervals_are_ordered():
    terms=E.term_structure(AS_OF)
    assert (terms.guide_q10 < terms.guide_q90).all()
