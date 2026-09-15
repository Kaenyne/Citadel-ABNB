"""Analytical and point-in-time failure-mode tests; no frozen writes."""
import importlib.util
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import pytest

_spec=importlib.util.spec_from_file_location("_conversion_validation_v1_runner_test",Path(__file__).with_name("run.py"))
r=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r)
m=r._model


def synthetic(w=.37):
    i=np.arange(16);season=i%4+1
    a=10000+700*i+np.sin(i)*900;b=9000+500*i+np.cos(i)*1100
    lam=np.array([.12,.14,.18,.11])
    return pd.DataFrame(dict(season=season,gbv_l1=a,gbv_l2=b,revenue_musd=lam[season-1]*(w*a+(1-w)*b)))


@pytest.mark.parametrize("w",[0.,.37,1.])
def test_recovers_exact_shared_weight_and_four_coefficients(w):
    d=synthetic(w);f=m.fit(d)
    assert f["w"]==pytest.approx(w,abs=2e-7)
    assert f["lambdas"]==pytest.approx([.12,.14,.18,.11],abs=2e-8)
    assert np.max(np.abs(m.fitted_values(d,f)-d.revenue_musd))<1e-4


@pytest.mark.parametrize("bad",[-.1,1.1,np.nan,np.inf,[.2,.3],True])
def test_scalar_weight_bounds(bad):
    with pytest.raises(ValueError):m.fit(synthetic(),bad)


def test_relative_loss_has_correct_analytical_coefficients():
    d=synthetic();f=m.fit(d,.37,"relative")
    assert f["lambdas"]==pytest.approx([.12,.14,.18,.11],abs=1e-12)


def test_fixed_fit_matches_manual_through_origin_regression():
    d=synthetic();f=m.fit(d,m.FIXED_W)
    for s in range(1,5):
        z=d[d.season==s];x=m.FIXED_W*z.gbv_l1+(1-m.FIXED_W)*z.gbv_l2
        assert f["lambdas"][s-1]==pytest.approx((x*z.revenue_musd).sum()/(x*x).sum())
    assert f["n_parameters"]==4


def test_season_coverage_and_nonfinite_values_rejected():
    d=synthetic()
    with pytest.raises(ValueError):m.fit(d[d.season!=4])
    with pytest.raises(ValueError):m.fit(d.iloc[:7])
    d.loc[0,"gbv_l1"]=np.nan
    with pytest.raises(ValueError):m.fit(d)


def test_explicit_currency_unit_conversions():
    assert m.to_musd([27.2],"USD_billions")==pytest.approx([27200.])
    assert m.to_musd([27_200_000_000],"USD")==pytest.approx([27200.])
    with pytest.raises(ValueError):m.to_musd([27.2],"unknown")
    with pytest.raises(ValueError):m.to_musd([-1],"USD_millions")


def test_exact_22_lag_complete_source_reconstruction():
    panel,targets=r.load();d=m.lag_rows(panel)
    assert d.quarter.tolist()==list(pd.period_range("2021Q1","2026Q2",freq="Q").astype(str))
    lookup=panel.set_index("quarter")
    for x in d.itertuples():
        assert x.gbv_l1==lookup.loc[m.shift(x.quarter,-1),"gbv_musd"]
        assert x.gbv_l2==lookup.loc[m.shift(x.quarter,-2),"gbv_musd"]
    assert len(d)==22


def test_same_day_letter_is_admissible_but_future_actual_and_gbv_are_not():
    panel,_=r.load();date="2023-02-14";known=panel[panel.print_date<=pd.Timestamp(date)]
    f=m.predict(known,"2023Q1",date)
    assert f["n"]==8 and f["lag1_print_date"]==date
    assert "2023Q1" not in f["training_quarters"]
    future=panel[panel.quarter=="2023Q1"].copy();future["revenue_musd"]=1e8;future["gbv_musd"]=1e9
    with pytest.raises(ValueError,match="future"):
        m.predict(pd.concat([known,future]),"2023Q1",date)
    altered=panel.copy();altered.loc[altered.print_date>pd.Timestamp(date),["revenue_musd","gbv_musd"]]*=1000
    second=m.predict(altered[altered.print_date<=pd.Timestamp(date)],"2023Q1",date)
    assert f["point"]==second["point"] and f["w"]==second["w"]


def test_missing_lag_and_duplicate_or_undated_panel_rejected():
    panel,_=r.load();date="2023-02-14";known=panel[panel.print_date<=pd.Timestamp(date)]
    with pytest.raises(ValueError,match="lagged"):
        m.predict(known[known.quarter!="2022Q4"],"2023Q1",date)
    with pytest.raises(ValueError,match="duplicate"):
        m.predict(pd.concat([known,known.iloc[[0]]]),"2023Q1",date)
    bad=known.copy();bad.loc[bad.index[0],"print_date"]=pd.NaT
    with pytest.raises(ValueError,match="publication"):
        m.predict(bad,"2023Q1",date)


def test_known_target_outcome_is_forbidden_even_if_timestamp_manipulated():
    panel,_=r.load();known=panel[panel.quarter<="2023Q1"].copy();known.loc[known.quarter=="2023Q1","print_date"]=pd.Timestamp("2023-02-14")
    with pytest.raises(ValueError,match="target outcome"):
        m.predict(known,"2023Q1","2023-02-14")


def test_conservative_sequential_band_uses_only_supplied_past_errors():
    lo,hi,n=m.sequential_band(100,[.1]*5);assert np.isnan(lo) and n==5
    lo,hi,n=m.sequential_band(100,[.01,.02,.03,.04,.05,.06])
    assert (lo,hi,n)==pytest.approx((94,106,6))
    with pytest.raises(ValueError):m.sequential_band(100,[np.nan]*6)


def test_interval_denominator_matches_multiplicative_bound_algebra():
    e=m.calibration_error(100,120)
    assert e==pytest.approx(-1/6)
    lo,hi,n=m.sequential_band(120,[e]*6)
    assert (lo,hi,n)==pytest.approx((100,140,6))
    with pytest.raises(ValueError):m.calibration_error(100,0)


def test_fit_is_deterministic():
    a=m.fit(synthetic());b=m.fit(synthetic())
    assert a["w"]==b["w"] and np.array_equal(a["lambdas"],b["lambdas"])


def test_immutable_output_guard_before_any_write():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"preserve";p.write_text("unchanged")
        with pytest.raises(FileExistsError):r.run(td)
        assert p.read_text()=="unchanged" and len(list(Path(td).iterdir()))==1
